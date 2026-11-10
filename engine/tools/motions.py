# Kimodo's motions as the engine keeps them (motions/<id>.json): the studio's own data exactly as made — every one of
# SOMA's 77 joints (fingers too) each frame, its rotation and its place — with the whole ask it was made by, how it goes
# on from another motion, and one thing derived from it: the lowest point of SOMA's posed skin each frame.
#
# The sources: the studio's per-joint data (`motion(key, data: "body")` → {n, fps, names, q, p}) — the first fifteen
# kept in experiments/motions-raw, the rest in data/kimodo/<key>.json — and each one's ask (`motion(key)`: prompts,
# seconds, heading, transition_frames, seed, steps, cfg, constraints, after, made, startsAt) in data/kimodo/asks.json.
#   python3 tools/motions.py   (writes motions/*.json and motions/index.json)
#
# The file:
#   {format: "engine/motion", version: 2, id, label: {ru, en}, skeleton: "soma77", fps, frames,
#    kimodo: {key, made, ask: {…the whole ask, as the studio keeps it}, startsAt: {x, z} | null},
#    after: {motion: <engine id>, frames} | null — made to go on from that one: its first `frames` frames are that one's
#           last (Kimodo was given them); startsAt: where its origin is in that one's space,
#    data: {names, q, p} — the studio's: q each joint's rotation in the world (x, y, z, w; int16 / 32767), frame by frame;
#          p its place (int16, millimetres); y up, at frame 0 the pelvis over the origin, facing +z, the person's left +x,
#    derived: {lowest: [metres, a frame each] — SOMA's whole skin posed, its lowest point}}
# src/motion.js reads it; clipOf joins a chain.
import base64, json, os, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot
import soma

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, '..', 'experiments', 'motions-raw')
KIMODO = os.path.join(ROOT, 'data', 'kimodo')
ASKS = json.load(open(os.path.join(KIMODO, 'asks.json')))

# id, its data (a path under experiments/motions-raw, or None: data/kimodo/<key>.json), studio key, label (ru, en)
MOTIONS = [
    ('walk', 'indie/walk.txt', 'f555a59113ec14d816ef7a510d607a3a432bae37e85c0d6ac7c61d43afbebc46', ('шаг', 'walk')),
    ('run', 'indie/run.txt', '533445e36c78dbf85cd24a8ec44d456711b85edfe75f3da82fd4cdc7492f89bb', ('бег', 'run')),
    ('sneak', 'indie/sneak.txt', '1ece5113cb09f2b676f74614ad57105f8676d35e60698edc69740f2b9a1e8d76', ('крадётся', 'sneak')),
    ('wave', 'indie/wave.txt', '87e6b449537b34333a719f053b90b21541bb2d311526c31c19733344c1e489b6', ('машет', 'wave')),
    ('jump', 'indie/jump.txt', '933719dbf16fec4fe78cff528c1aebcd3fc9aea077efb7d51c793d77c4e463b2', ('прыжок', 'jump')),
    ('dance', 'indie/dance.txt', 'a68bef2fc712d04c5040122e43eff4a3ac932e1857ed6d7ca9b1acbd55e98fb3', ('танец', 'dance')),
    ('bow', 'indie/bow.txt', 'cb04b420e335a2490a6b411abc43893ecfcef5ed2cfc06cee780daca17c6e452', ('поклон', 'bow')),
    ('stomp', 'indie/stomp.txt', 'cb0b726fa68337afddf42a3efee74d3c2fd8d0315eaf4fa663ede65138b10b6f', ('топает', 'stomp')),
    ('idle', 'indie/idle.txt', 'b4718c096c53ea996d04d339aba6ebe034fe5812abb17f0ce1a5c1e70b7ee96b', ('стоит', 'idle')),
    ('sit', 'indie/sit.txt', '91761c43090091a6fc2ed99b7575634df75483aedba60661f6c569b6f2902a8c', ('садится', 'sit')),
    ('lie', 'cloth/lie2.txt', 'b148f30e2429a100ae27c91f4ad13e88ae4262cb91ca10f6dcd9ac5538f3addc', ('ложится', 'lie down')),
    ('lying', 'cloth/lie.txt', 'ae9eed0ac02db47acfc1a8ff4f0d4b78063513319d80843e65021ac975506cad', ('лежит', 'lying')),
    ('roll', 'cloth/roll.txt', 'f9ede70a3b8952f970768c226b27b2720f5b616dd15c890748df229ff4edb38d', ('кувырок', 'forward roll')),
    ('roll-side', 'cloth/roll2.txt', '4de88a6dab600de0e6bae971c00f0c6bec9be0c256a2e4d3fc5b679db3f47b6a', ('катается', 'rolls sideways')),
    # made to go on from `lie` (after: its last 5 frames); the studio's own data (the earlier engine had taken it back
    # from experiments/cloth's joined file: the same within a unit of rounding)
    ('rollover', None, '7a4c19b1e67d148d50b144da72ae4a1dfbfd1934bf70e567d1194195003f43db', ('перекатывается', 'rolls over')),
    # a chain to test joins with (ordered 2026-11-03): walk → stop → look around → turn back, each after the one before
    ('stop', None, 'a54282c0b563d9f25e56a45efcca08111c30cbcc50c3f006f9ca10428169e6ea', ('останавливается', 'comes to a stop')),
    ('look-around', None, '679cda3a7ca6d1db236db3199efdb6d4113b6d55e224c0088ea145c28ef58102', ('оглядывается', 'looks around')),
    ('turn-back', None, 'b9fe1859080faed6f3690b49f010718fdb8c38c895a90738ee351ac655f69913', ('поворачивает назад', 'turns back')),
]
# chains: their motions (pinned by content hash when written) and how each join is treated (src/motion.js)
CHAINS = [
    {'id': 'lie-rollover', 'label': {'ru': 'ложится → перекатывается', 'en': 'lies down → rolls over'}, 'motions': ['lie', 'rollover'],
     'joins': [{'blend': 'dead', 'frames': 12}]},
    {'id': 'walk-stop-look-back', 'label': {'ru': 'идёт → останавливается → оглядывается → назад', 'en': 'walks → stops → looks around → turns back'},
     'motions': ['walk', 'stop', 'look-around', 'turn-back'], 'joins': [{'blend': 'cut'}, {'blend': 'cut'}, {'blend': 'cut'}]},
]

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


def write(mid, label, key, d):
    q, p = arrays(d)
    assert d['names'] == soma.NAMES
    meta = ASKS[key]; ask = meta['ask']
    after = None
    if ask.get('after'):
        prev = next(m[0] for m in MOTIONS if m[2] == ask['after']['key'])
        after = {'motion': prev, 'frames': ask['after'].get('frames', 5)}
    out = {'format': 'engine/motion', 'version': 2, 'id': mid, 'label': {'ru': label[0], 'en': label[1]}, 'skeleton': 'soma77',
           'fps': d['fps'], 'frames': int(len(q)),
           'kimodo': {'key': key, 'made': meta['made'], 'ask': ask, 'startsAt': meta['startsAt']},
           'after': after,
           'data': {'names': d['names'], 'q': d['q'], 'p': d['p']},
           'derived': {'lowest': lowest(q, p)}}
    json.dump(out, open(os.path.join(ROOT, 'motions', mid + '.json'), 'w'), ensure_ascii=False)
    print(mid, len(q), 'frames')
    return {'id': mid, 'label': out['label'], 'frames': out['frames'], 'fps': d['fps'], **({'after': after['motion']} if after else {})}


if __name__ == '__main__':
    index = {'format': 'engine/motions', 'version': 2, 'motions': [], 'chains': CHAINS}
    for mid, src, key, label in MOTIONS:
        d = json.load(open(os.path.join(RAW, src) if src else os.path.join(KIMODO, key + '.json')))
        index['motions'].append(write(mid, label, key, d))
    json.dump(index, open(os.path.join(ROOT, 'motions', 'index.json'), 'w'), indent=1, ensure_ascii=False)
    print('chains are pinned by node engine/tools/characters.mjs chains')
