# Poses for Kimodo's constraints, from motions Kimodo made.
#
# Kimodo's hand constraints are given as a whole pose (every joint's local turn and the pelvis's place): the hand is
# where that pose puts it (FK). So a hand at a place = a pose Kimodo made itself (a frame of one of its motions, where
# the person reaches that way), turned about the vertical and moved so its hand comes to the place; when the place is
# higher or lower than that pose's hand, the arm alone (shoulder and elbow) is turned by the least angle to reach it.
# What goes to Kimodo is that pose; Kimodo then makes the motion around it (the lean, the steps, the elbow).
#
# The studio's body data: q — each joint's frame in the world (x y z w, /32767), p — its place (mm). The turn from
# SOMA's rest is G = R(q) R0ᵀ (R0: SOMA's rest frame); Kimodo's local turn is Gparentᵀ G (axis-angle).
import base64, json, os, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, '..', '..', 'engine', 'tools'))
import soma  # noqa: E402

S = soma.load()
NAMES = soma.NAMES
IX = {n: i for i, n in enumerate(NAMES)}
PARENT = S['parent']
REST = S['P']            # rest places
R0 = S['R']              # rest frames (matrices)


def raw(mid):
    """a motion's studio data: from motions/raw/<id>.json while it is being kept, else from motions/<id>.json"""
    src = os.path.join(ROOT, 'motions', 'raw', mid + '.json')
    if os.path.exists(src): d = json.load(open(src))
    else: m = json.load(open(os.path.join(ROOT, 'motions', mid + '.json'))); d = {**m['data'], 'n': m['frames']}
    n = d['n']
    q = np.frombuffer(base64.b64decode(d['q']), '<i2').reshape(n, 77, 4) / 32767.0
    p = np.frombuffer(base64.b64decode(d['p']), '<i2').reshape(n, 77, 3) / 1000.0
    return q, p


def globals_of(q):
    """each joint's turn from rest, in the world (77×3×3)"""
    return Rot.from_quat(q).as_matrix() @ R0.transpose(0, 2, 1)


def locals_of(G):
    L = np.empty_like(G)
    for j in range(77):
        L[j] = G[j] if PARENT[j] < 0 else G[PARENT[j]].T @ G[j]
    return L


def fk(L, root):
    G = np.empty_like(L); P = np.empty((77, 3))
    for j in range(77):
        pj = PARENT[j]
        if pj < 0: G[j] = L[j]; P[j] = root
        else: G[j] = G[pj] @ L[j]; P[j] = P[pj] + G[pj] @ (REST[j] - REST[pj])
    return G, P


def pose_at(mid, f):
    q, p = raw(mid)
    G = globals_of(q[f])
    return locals_of(G), p[f, 0].copy(), p[f]


def turn_move(L, root, angle, move):
    """the pose turned about the vertical (through the origin) and moved over the floor"""
    r = Rot.from_rotvec([0, angle, 0]).as_matrix()
    L = L.copy(); L[0] = r @ L[0]
    root = r @ root + np.array([move[0], 0, move[1]])
    return L, root


def reach(L, root, side, target):
    """the arm alone (shoulder ball, elbow hinge) turned by the least to bring the wrist to target (the pose's own
    elbow plane kept)"""
    L = L.copy()
    a, b, c = IX[side + 'Arm'], IX[side + 'ForeArm'], IX[side + 'Hand']
    G, P = fk(L, root)
    A, B, C = P[a], P[b], P[c]
    la, lb = np.linalg.norm(B - A), np.linalg.norm(C - B)
    t = np.asarray(target, float); d = np.linalg.norm(t - A)
    d = min(d, la + lb - 1e-4)
    # elbow angle for distance d (law of cosines), as an extra bend about the elbow's own hinge (normal of the arm's plane)
    cur = np.linalg.norm(C - A)
    def inner(x): return np.arccos(np.clip((la * la + lb * lb - x * x) / (2 * la * lb), -1, 1))
    n = np.cross(B - A, C - B); n = n / (np.linalg.norm(n) + 1e-12)
    dth = inner(cur) - inner(d)          # the elbow opens by this much
    Rb = Rot.from_rotvec(n * dth).as_matrix()    # in the world, about the hinge (a turn about u×v bends further)
    # apply at the elbow: G_b' = Rb G_b  →  L_b' = G_a^T Rb G_b
    L[b] = G[a].T @ Rb @ G[b]
    G, P = fk(L, root)
    # then swing the shoulder so the wrist points at the target
    u, v = P[c] - P[a], t - P[a]
    u, v = u / np.linalg.norm(u), v / np.linalg.norm(v)
    ax = np.cross(u, v); s = np.linalg.norm(ax)
    if s > 1e-9:
        Ra = Rot.from_rotvec(ax / s * np.arctan2(s, np.dot(u, v))).as_matrix()
        pa = PARENT[a]
        L[a] = G[pa].T @ Ra @ G[a]
    G, P = fk(L, root)
    return L, P


def native(L):
    """Kimodo's own local turns: between the joints' frames themselves (the studio's q), not between turns from rest —
    q_parentᵀ q_j = R0_parentᵀ L_j R0_j (the pelvis: L R0). Found by sending turns from rest first: the hand came 45 cm
    off, exactly where this reading puts it."""
    N = np.empty_like(L)
    for j in range(77):
        N[j] = L[j] @ R0[j] if PARENT[j] < 0 else R0[PARENT[j]].T @ L[j] @ R0[j]
    return N


def kimodo(kind, frames, poses):
    """a constraint as Kimodo takes it"""
    return {'type': kind, 'frame_indices': list(frames),
            'root_positions': [[round(float(x), 5) for x in r] for _, r in poses],
            'local_joints_rot': [[[round(float(x), 5) for x in Rot.from_matrix(m).as_rotvec()] for m in native(L)] for L, _ in poses]}


if __name__ == '__main__':
    # check: the studio's places are SOMA's FK of its turns
    mid = sys.argv[1]
    q, p = raw(mid)
    for f in [0, len(q) // 2, len(q) - 1]:
        G = globals_of(q[f]); L = locals_of(G); _, P = fk(L, p[f, 0])
        print(f, 'FK vs data, mm: max', round(float(np.abs(P - p[f]).max() * 1000), 2))
