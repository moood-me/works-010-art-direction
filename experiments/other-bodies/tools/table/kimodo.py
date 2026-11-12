# Kimodo's data and constraints, for contacts: reading the studio's per-joint data, a pose of a made motion moved to a
# place, and that pose written as Kimodo's own constraint (what make_motion takes as it is).
#
# What the studio's body data is (motion(key, data: "body") → {n, fps, names, q, p}): each SOMA joint's place p (int16,
# mm) and its rotation q (int16/32767, x y z w) — Kimodo's own global rotation G, as Kimodo gives it. Kimodo's forward
# kinematics measures G from its *neutral* skeleton, a T-pose (arms straight out: kimodo_neutral.json, from Kimodo's
# assets), not from the SOMA skin's A-pose rest the engine carries bodies by (engine/data/skeleton.json): p_child =
# p_parent + G_parent (n_child − n_parent). (The engine's own FK, q·frameᵀ over the A-pose rest, gives the same
# places, because the skin's bind frames are what turns one rest into the other; but Kimodo reads local rotations
# against its T-pose, so a constraint must be written in Kimodo's terms: local = G_parentᵀ G.) Checked on a made
# motion: 0.7 mm mean, the int16 rounding.
#
# Kimodo's hand constraint (kimodo/constraints.py, EndEffectorConstraintSet) is a whole pose: {type, frame_indices,
# local_joints_rot [T, 77, 3] axis-angle, root_positions [T, 3]}; Kimodo runs its FK and then holds, at those frames,
# the hand joints' places (the wrist and every finger joint), the wrist's turn — and also the pelvis's place over the
# floor, its height and the heading. So "the hands here" always comes with "the body there": the pose a hand constraint
# is cut from decides how the person stands while touching.
import base64, json, os, numpy as np
from scipy.spatial.transform import Rotation as Rot

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SK = json.load(open(os.path.join(REPO, 'engine/data/skeleton.json')))
NAMES = [j['name'] for j in SK['joints']]
PARENT = [j['parent'] for j in SK['joints']]
REST = np.array([j['rest'] for j in SK['joints']])
NEUTRAL = np.array(json.load(open(os.path.join(HERE, 'kimodo_neutral.json')))['joints'])
IDX = {n: i for i, n in enumerate(NAMES)}
SOMA_FLOOR = SK['floor']
HIP_SOMA = REST[0, 1] - SOMA_FLOOR


def read_raw(path):
    """the studio's body data, or a motion of this folder (motions/<id>.json, which keeps it as it was)"""
    d = json.load(open(path))
    if d.get('format') == 'engine/motion': d = {'n': d['frames'], 'fps': d['fps'], **d['data']}
    assert d['names'] == NAMES, 'joint order differs from SOMA77'
    n = d['n']
    q = np.frombuffer(base64.b64decode(d['q']), '<i2').reshape(n, 77, 4).astype(float) / 32767
    q /= np.linalg.norm(q, axis=-1, keepdims=True)
    p = np.frombuffer(base64.b64decode(d['p']), '<i2').reshape(n, 77, 3).astype(float) / 1000
    return dict(n=n, fps=d['fps'], q=q, p=p, raw=d)


def kimodo_globals(q):
    """[77,4] the studio's quaternions → Kimodo's global rotations (they are the same: identity at Kimodo's T-pose)"""
    return Rot.from_quat(q)


def pose(m, f):
    """a frame of a motion as {G: Rotation[77] (Kimodo's globals), p: [77,3]}"""
    return dict(G=kimodo_globals(m['q'][f]), p=m['p'][f].copy())


def moved(ps, turn=0.0, move=(0, 0, 0)):
    """the pose turned about the vertical through the origin by `turn` radians, then moved by `move` (metres)"""
    r = Rot.from_rotvec([0, turn, 0])
    return dict(G=r * ps['G'], p=r.apply(ps['p']) + np.asarray(move, float))


def fk(G, root):
    """Kimodo's FK (for checking): joint places from the globals and the pelvis's place"""
    out = np.zeros((77, 3)); out[0] = root
    for j in range(1, 77):
        a = PARENT[j]; out[j] = out[a] + G[a].apply(NEUTRAL[j] - NEUTRAL[a])
    return out


def locals_of(G):
    """Kimodo's local rotations (axis-angle, [77,3]) from its globals"""
    L = []
    for j in range(77):
        a = PARENT[j]
        L.append((G[j] if a < 0 else G[a].inv() * G[j]).as_rotvec())
    return np.array(L)


def constraint(kind, frames, poses, joint_names=None):
    """Kimodo's constraint of `kind` (left-hand, right-hand, end-effector, fullbody) at `frames`, each frame's pose"""
    c = {'type': kind, 'frame_indices': [int(f) for f in frames],
         'local_joints_rot': [np.round(locals_of(ps['G']), 3).tolist() for ps in poses],
         'root_positions': [np.round(ps['p'][0], 4).tolist() for ps in poses]}
    if joint_names: c['joint_names'] = joint_names
    # check: Kimodo's FK of what we send gives back the pose's places
    for ps in poses:
        err = np.abs(fk(ps['G'], ps['p'][0]) - ps['p']).max()
        assert err < 0.004, f'FK differs from the pose by {err:.4f} m'
    return c


def palm(p, side):
    """the middle of the palm from the joints: between the wrist and the knuckles of the index and the little finger"""
    s = 'Left' if side == 'L' else 'Right'
    return (p[IDX[s + 'Hand']] + p[IDX[s + 'HandIndex1']] + p[IDX[s + 'HandPinky1']]) / 3
