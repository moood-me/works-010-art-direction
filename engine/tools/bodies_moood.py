# moood's baked Anny bodies (experiments/data: the bytes of moood's engines/1/bodies/*.bin, base64 in a JS module each)
# as the engine's body description: one shared topology (data/topology/anny-moood) and a body per person
# (data/bodies/moood-<who>). python3 tools/bodies_moood.py
import base64, json, os, re, numpy as np
from scipy.spatial.transform import Rotation as Rot
import pack
from soma import NAMES, part

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, '..', 'experiments', 'data')
PEOPLE = ['woman', 'man', 'girl', 'boy', 'child', 'oldwoman', 'oldman']
LABEL = {'woman': ('Женщина', 'Woman'), 'man': ('Мужчина', 'Man'), 'girl': ('Девочка', 'Girl'), 'boy': ('Подросток', 'Teenage boy'),
         'child': ('Ребёнок', 'Child'), 'oldwoman': ('Старушка', 'Old woman'), 'oldman': ('Старик', 'Old man')}
# the parts a deformer or a garment can ask for: each vertex's share of each, from its skin weights
PARTS = ['pelvis', 'spine', 'neck', 'head'] + [s + p for p in ['clavicle', 'upperArm', 'foreArm', 'hand', 'thigh', 'shin', 'foot'] for s in ['L', 'R']]


def module_bytes(name):
    s = open(os.path.join(DATA, name + '.js')).read()
    return base64.b64decode(re.search(r'"([^"]+)"', s).group(1))


def part_of_joint(n):
    side, kind = part(n)
    kind = {'eye': 'head', 'finger': 'hand', 'toe': 'foot'}.get(kind, kind)
    return kind if side == 'C' or kind == 'head' else side + kind


def read_base():
    b = module_bytes('base'); at = 0
    def take(dt, n):
        nonlocal at
        a = np.frombuffer(b, dt, n, at); at += a.nbytes; return a
    N, T = take('<u4', 2)
    tris = take('<u2', T * 3).reshape(T, 3)
    joint = take('u1', N * 4).reshape(N, 4)
    weight = take('u1', N * 4).reshape(N, 4)
    F, = take('<u4', 1)
    face = take('<u2', F)
    return dict(N=int(N), tris=tris, joint=joint, weight=weight, face=face)


def read_person(who, base):
    b = module_bytes(who); N, F = base['N'], len(base['face'])
    pos = np.frombuffer(b, '<i2', N * 3, 0).reshape(N, 3) / 1e4
    plain = np.frombuffer(b, '<i2', F * 3, N * 6).reshape(F, 3) / 1e4
    inv = np.frombuffer(b, '<f4', 77 * 12, N * 6 + F * 6).reshape(77, 3, 4).astype(np.float64)
    R = np.array([I[:, :3].T for I in inv]); P = np.array([-(I[:, :3].T @ I[:, 3]) for I in inv])
    return pos, plain, R, P


def topology(base):
    N = base['N']
    w = base['weight'].astype(np.float64); s = w.sum(1, keepdims=True); s[s == 0] = 1
    weights = (w / s).astype(np.float32)
    pj = np.array([PARTS.index(part_of_joint(n)) for n in NAMES])
    parts = np.zeros((N, len(PARTS)))
    for k in range(4): np.add.at(parts, (np.arange(N), pj[base['joint'][:, k]]), weights[:, k])
    used = np.zeros(N, bool); used[base['tris'].ravel()] = True
    header = {
        'format': 'engine/topology', 'version': 1, 'id': 'anny-moood',
        'about': "moood's Anny mesh (MakeHuman's, as moood bakes it): its triangles, each vertex's four SOMA joints and weights, "
                 "its share of each body part, and the face's vertices (those a face without features replaces).",
        'source': 'moood engines/1/bodies/base.bin (experiments/data/base.js); Anny (NAVER, Apache-2.0), MakeHuman (CC0), SOMA rig (NVIDIA, Apache-2.0)',
        'skeleton': 'soma77', 'vertices': N, 'triangles': int(len(base['tris'])), 'parts': PARTS,
        'unused': int((~used).sum()),
    }
    pack.write(os.path.join(ROOT, 'data/topology/anny-moood.json'), header, {
        'triangles': base['tris'].astype(pack.index_type(N)), 'skinJoints': base['joint'].astype(np.uint8), 'skinWeights': weights,
        'parts': np.round(parts * 255).astype(np.uint8), 'face': base['face'].astype(pack.index_type(N))})


def body_file(bid, label, source, pos, R, P, extra_header=None, extra=None):
    """A body: its vertices at rest and its joints at rest — place and frame (the frames are what a motion's rotations
    are carried by, see src/retarget.js)."""
    q = Rot.from_matrix(R).as_quat().astype(np.float32)
    header = {'format': 'engine/body', 'version': 1, 'id': bid, 'label': {'ru': label[0], 'en': label[1]}, 'source': source,
              'topology': 'anny-moood', 'skeleton': 'soma77'}
    header.update(extra_header or {})
    arrays = {'positions': pos.astype(np.float32), 'joints': P.astype(np.float32), 'frames': q}
    arrays.update(extra or {})
    pack.write(os.path.join(ROOT, 'data/bodies', bid + '.json'), header, arrays)


if __name__ == '__main__':
    base = read_base()
    topology(base)
    meta = json.load(open(os.path.join(DATA, 'meta.json')))
    for who in PEOPLE:
        pos, plain, R, P = read_person(who, base)
        f = meta['people'][who]
        body_file('moood-' + who, LABEL[who], f"moood engines/1/bodies/{who}.bin (experiments/data/{who}.js): Anny baked by moood",
                  pos, R, P, {'eyes': {'centers': f['eyes'], 'size': f['size'], 'about': "moood's drawn eyes: where they sit, their size"}},
                  {'facePlain': plain.astype(np.float32)})
        print('moood-' + who, 'height %.3f' % (pos[:, 1].max() - pos[:, 1].min()))
