# Kimodo's motions as the engine keeps them (motions/<id>.json): the studio's own data exactly as made — every one of
# SOMA's 77 joints (fingers too) each frame, its rotation and its place — with what was asked for it, how it goes on
# from another motion, and one thing derived from it: the lowest point of SOMA's posed skin each frame.
#
# The sources are the studio's per-joint data (`motion(key, data: "body")` → {n, fps, names, q, p}), kept in
# experiments/motions-raw. python3 tools/motions.py   (writes motions/*.json and motions/index.json)
#
# The file:
#   {format: "engine/motion", version: 1, id, label: {ru, en},
#    kimodo: {key, prompts, seconds, after?: {motion: <engine id>, key, frames}, startsAt?: {x, z}},
#    fps, frames, skeleton: "soma77",
#    data: {names, q, p} — the studio's: q each joint's rotation in the world (x, y, z, w; int16 / 32767), frame by frame;
#          p its place (int16, millimetres); y up, at frame 0 the pelvis over the origin, facing +z, the person's left +x,
#    derived: {lowest: [metres, a frame each] — SOMA's whole skin posed, its lowest point}}
# A motion made to go on from another (`after`) has that one's last `frames` frames as its first; `startsAt` is where
# its origin is in the other's frame (its heading the other's). src/chain.js joins them.
import base64, json, os, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot
import soma

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, '..', 'experiments', 'motions-raw')

# id, source, studio key, label (ru, en), prompts, seconds
MOTIONS = [
    ('walk', 'indie/walk.txt', 'f555a59113ec14d816ef7a510d607a3a432bae37e85c0d6ac7c61d43afbebc46', ('шаг', 'walk'), ['A person walks forward at a relaxed pace.'], [4]),
    ('run', 'indie/run.txt', '533445e36c78dbf85cd24a8ec44d456711b85edfe75f3da82fd4cdc7492f89bb', ('бег', 'run'), ['A person runs forward.'], [3]),
    ('sneak', 'indie/sneak.txt', '1ece5113cb09f2b676f74614ad57105f8676d35e60698edc69740f2b9a1e8d76', ('крадётся', 'sneak'), ['A person sneaks forward on tiptoes, crouching.'], [4]),
    ('wave', 'indie/wave.txt', '87e6b449537b34333a719f053b90b21541bb2d311526c31c19733344c1e489b6', ('машет', 'wave'), ['A person stands and waves hello with the right hand.'], [3]),
    ('jump', 'indie/jump.txt', '933719dbf16fec4fe78cff528c1aebcd3fc9aea077efb7d51c793d77c4e463b2', ('прыжок', 'jump'), ['A person jumps up happily with both arms raised.'], [3]),
    ('dance', 'indie/dance.txt', 'a68bef2fc712d04c5040122e43eff4a3ac932e1857ed6d7ca9b1acbd55e98fb3', ('танец', 'dance'), ['A person dances cheerfully, swinging the arms.'], [4]),
    ('bow', 'indie/bow.txt', 'cb04b420e335a2490a6b411abc43893ecfcef5ed2cfc06cee780daca17c6e452', ('поклон', 'bow'), ['A person bows politely.'], [3]),
    ('stomp', 'indie/stomp.txt', 'cb0b726fa68337afddf42a3efee74d3c2fd8d0315eaf4fa663ede65138b10b6f', ('топает', 'stomp'), ['A person stomps angrily and shakes a fist.'], [3]),
    ('idle', 'indie/idle.txt', 'b4718c096c53ea996d04d339aba6ebe034fe5812abb17f0ce1a5c1e70b7ee96b', ('стоит', 'idle'), ['A person stands idle, breathing, shifting weight and looking around.'], [5]),
    ('sit', 'indie/sit.txt', '91761c43090091a6fc2ed99b7575634df75483aedba60661f6c569b6f2902a8c', ('садится', 'sit'), ['A person sits down on the ground and hugs their knees.'], [4]),
    ('lie', 'cloth/lie2.txt', 'b148f30e2429a100ae27c91f4ad13e88ae4262cb91ca10f6dcd9ac5538f3addc', ('ложится', 'lie down'),
     ['A person stands still.', 'A person kneels down and then lies down on the floor on their back.'], [1, 5]),
    ('lying', 'cloth/lie.txt', 'ae9eed0ac02db47acfc1a8ff4f0d4b78063513319d80843e65021ac975506cad', ('лежит', 'lying'), ['A person lies down on the floor on their back.'], [5]),
    ('roll', 'cloth/roll.txt', 'f9ede70a3b8952f970768c226b27b2720f5b616dd15c890748df229ff4edb38d', ('кувырок', 'forward roll'), ['A person does a forward roll on the floor.'], [4]),
    ('roll-side', 'cloth/roll2.txt', '4de88a6dab600de0e6bae971c00f0c6bec9be0c256a2e4d3fc5b679db3f47b6a', ('катается', 'rolls sideways'), ['A person lies on the ground and rolls over sideways.'], [5]),
]
# made to go on from `lie` (after: its last 5 frames); its origin in lie's frame
ROLLOVER = ('rollover', '7a4c19b1e67d148d50b144da72ae4a1dfbfd1934bf70e567d1194195003f43db', ('перекатывается', 'rolls over'),
            ['A person lying on their back on the floor rolls over sideways onto their stomach, and keeps rolling onto their back again.'], [5],
            {'motion': 'lie', 'frames': 5}, {'x': -0.1022, 'z': -0.6537})
CHAINS = [{'id': 'lie-rollover', 'label': {'ru': 'ложится → перекатывается', 'en': 'lies down → rolls over'}, 'motions': ['lie', 'rollover']}]

S = soma.load()


def arrays(d):
    n = d['n']
    q = np.frombuffer(base64.b64decode(d['q']), '<i2').reshape(n, 77, 4).copy()
    p = np.frombuffer(base64.b64decode(d['p']), '<i2').reshape(n, 77, 3).copy()
    return q, p


def lowest(q, p):
    """SOMA's skin posed each frame (x' = R_j R0_jᵀ (x − rest_j) + place_j over its 8 joints), its lowest point"""
    out = []
    for f in range(len(q)):
        R = Rot.from_quat(q[f] / 32767.0).as_matrix() @ S['R'].transpose(0, 2, 1)
        T = p[f] / 1000.0 - np.einsum('jab,jb->ja', R, S['P'])
        y = np.zeros(S['V'])
        for k in range(8):
            j = S['joint'][:, k]
            y += S['weight'][:, k] * (np.einsum('vb,vb->v', R[j, 1, :], S['bind']) + T[j, 1])
        out.append(round(float(y.min()), 4))
    return out


def write(mid, label, key, prompts, seconds, q, p, fps, after=None, starts=None):
    names = [j for j in soma.NAMES]
    kim = {'key': key, 'prompts': prompts, 'seconds': seconds}
    if after: kim['after'] = {**after, 'key': next(m[2] for m in MOTIONS if m[0] == after['motion'])}
    if starts: kim['startsAt'] = starts
    out = {'format': 'engine/motion', 'version': 1, 'id': mid, 'label': {'ru': label[0], 'en': label[1]}, 'kimodo': kim,
           'fps': fps, 'frames': int(len(q)), 'skeleton': 'soma77',
           'data': {'names': names, 'q': base64.b64encode(q.astype('<i2').tobytes()).decode(), 'p': base64.b64encode(p.astype('<i2').tobytes()).decode()},
           'derived': {'lowest': lowest(q, p)}}
    json.dump(out, open(os.path.join(ROOT, 'motions', mid + '.json'), 'w'))
    print(mid, len(q), 'frames')
    return {'id': mid, 'label': out['label'], 'frames': out['frames'], 'fps': fps, **({'after': after['motion']} if after else {})}


def rollover():
    """The studio's rollover, as it was kept: experiments/motions-raw/cloth/rollover.txt is lie's first 145 frames and
    then rollover's frames from its 5th on, moved over the floor (experiments/cloth/chain.py, overlap 5, keep 145): its
    own frames 5… are taken back from there, its first five are lie's last five (what `after` means), all in its own
    frame (lie's, less startsAt)."""
    lie = json.load(open(os.path.join(RAW, 'cloth/lie2.txt'))); joined = json.load(open(os.path.join(RAW, 'cloth/rollover.txt')))
    qa, pa = arrays(lie); qj, pj = arrays(joined)
    keep, k = 145, 5
    assert (qj[:keep] == qa[:keep]).all() and (pj[:keep] == pa[:keep]).all()
    st = np.array([ROLLOVER[6]['x'] * 1000, 0, ROLLOVER[6]['z'] * 1000])
    head_q, head_p = qa[-k:], pa[-k:] - np.round(st).astype(int)          # its first frames, in its own frame
    d = pa[keep - k, 0].astype(float) - head_p[0, 0]; d[1] = 0               # what chain.py moved it by
    tail_p = pj[keep:] - np.round(d).astype(int)
    q = np.concatenate([head_q, qj[keep:]]); p = np.concatenate([head_p, tail_p])
    gap = np.abs(p[k, 0].astype(int) + st - pa[-1, 0]).max()
    print('rollover: frame 5 against lie\'s last, mm', gap)
    return q, p


if __name__ == '__main__':
    index = {'format': 'engine/motions', 'version': 1, 'motions': [], 'chains': CHAINS}
    for mid, src, key, label, prompts, seconds in MOTIONS:
        d = json.load(open(os.path.join(RAW, src)))
        assert d['names'] == soma.NAMES
        q, p = arrays(d)
        index['motions'].append(write(mid, label, key, prompts, seconds, q, p, d['fps']))
    q, p = rollover()
    mid, key, label, prompts, seconds, after, starts = ROLLOVER
    index['motions'].append(write(mid, label, key, prompts, seconds, q, p, 30, after, starts))
    json.dump(index, open(os.path.join(ROOT, 'motions', 'index.json'), 'w'), indent=1, ensure_ascii=False)
