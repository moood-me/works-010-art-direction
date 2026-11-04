"""Савелий Петрович's body and clothes, on Anny (engine/data/bodies/moood-oldman: Anny baked by moood, SOMA skeleton).

1. Anny's old man is fitted to the drawing's proportions (styles/s10-ligne-claire/tools/figures.py: savely_figure):
   each bone of the skeleton is scaled (legs shorter, the trunk a little shorter and wider, arms shorter), and every
   vertex follows its own joints by Anny's skin weights (v' = Σ w·(J' + A·(v − J))) — the frames stay, so Kimodo's
   motions carry as they do on any engine body.  The trunk is then kept inside the drawing's own torso shell.
2. Clothes are made to the drawing: the vest and the shirt's body are the drawing's own torso shells (the vest with
   its V opening and arm holes), the trouser top is its hips shell; the sleeves and trouser legs are shells laid
   over Anny's arms and legs (the legs widened to the drawing's straight trouser legs); shoes, the bow tie, the
   collar points, buttons, the watch chain and the pocket watch from the drawing's own shapes.
3. Every piece gets four SOMA joints and weights: Anny's own where it is Anny's, else the nearest Anny vertex's.
Units: the drawing's (y down, z toward the viewer), floor at y = 1030; K metres per unit.
usage: python3 body.py CACHE → CACHE/body.npz
"""
import sys, os, json
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, '../../..')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, 'engine/tools'))
sys.path.insert(0, os.path.join(REPO, 'styles/s10-ligne-claire/tools'))
import pack                     # noqa: E402
import meshes as M              # noqa: E402
import head as H                # noqa: E402
from figures import inset, SAVELY_COL   # noqa: E402
from cast import wrapdeg        # noqa: E402

C = sys.argv[1]
K = 1.60 / 1114
FLOOR = 1030.0
SKIN = '#f1c6a0'
COL = dict(SAVELY_COL, skin=SKIN, gold='#d9a837', chain='#a87a1e', face='#fbf8ee')

sk = json.load(open(os.path.join(REPO, 'engine/data/skeleton.json')))
NAMES = [j['name'] for j in sk['joints']]
PARENT = [j['parent'] for j in sk['joints']]
IDX = {n: i for i, n in enumerate(NAMES)}
th, top = pack.read(os.path.join(REPO, 'engine/data/topology/anny-moood.json'))
bh, bod = pack.read(os.path.join(REPO, 'engine/data/bodies/moood-oldman.json'))
TRI = top['triangles'].astype(int)
SJ, SW = top['skinJoints'].astype(int), top['skinWeights'].astype(float)
PARTS = top['parts'].astype(float) / 255
PN = th['parts']


def part(*names):
    return sum(PARTS[:, PN.index(n)] for n in names)


def to_d(P):
    P = np.asarray(P, float)
    return np.stack([P[..., 0] / K, FLOOR - P[..., 1] / K, P[..., 2] / K], -1)


X0 = to_d(bod['positions'])
J0 = to_d(bod['joints'].reshape(-1, 3))

# ------------------------------------------------------------------ 1. the skeleton to the drawing's proportions
def scale_of(name):
    """The scale of the bone from this joint's parent to it, per axis (x, y, z) in the drawing's frame."""
    if name in ('LeftLeg', 'RightLeg'):
        return (0.72, 0.8, 1.0)              # the drawing's legs stand closer (x ±66)
    if 'Shin' in name or ('Foot' in name and 'Toe' not in name):
        return (0.35, 0.81, 1.0)             # and straight down, not splayed as Anny's rest
    if 'Toe' in name:
        return (0.75, 0.75, 0.75)
    if name in ('Spine1', 'Spine2', 'Chest'):
        return (1.0, 0.92, 1.0)
    if 'Shoulder' in name:
        return (1.12, 0.92, 1.0)
    if name in ('LeftArm', 'RightArm'):
        return (1.05, 0.92, 1.0)
    if 'ForeArm' in name or name in ('LeftHand', 'RightHand'):
        return (0.9, 0.9, 0.9)
    if 'Hand' in name:
        return (0.95, 0.95, 0.95)
    return (1.0, 1.0, 1.0)


S = np.array([scale_of(n) for n in NAMES])
J1 = J0.copy()
for j in range(len(NAMES)):                      # joints are listed parents first
    p = PARENT[j]
    if p < 0:
        J1[j] = J0[j]
        continue
    J1[j] = J1[p] + (J0[j] - J0[p]) * S[j]
# the root: legs start at the drawing's hips (y 520), the body centred where the drawing stands
legs_y = 0.5 * (J1[IDX['LeftLeg'], 1] + J1[IDX['RightLeg'], 1])
J1 += np.array([0, 515 - legs_y, -J1[IDX['Hips'], 2] - 22])
# the neck and head joints: where the drawing's head turns on its neck (figures.NECK + the head drop)
for n, p in (('Neck1', (0, 178, -14)), ('Neck2', (0, 152, -12)), ('Head', (0, 126, -10)), ('HeadEnd', (0, -84, -10)),
             ('Jaw', (0, 110, 20)), ('LeftEye', (27, 23, 58)), ('RightEye', (-27, 23, 58))):
    J1[IDX[n]] = p
# the floor: the lowest of the feet's skin stays on the floor (checked below)

# vertices follow their joints: v' = Σ w (J'_k + A_k (v − J_k)); A_k: the joint's own bone scale (girth too)
A = S.copy()
A[IDX['Spine1']] = A[IDX['Spine2']] = A[IDX['Chest']] = A[IDX['Hips']] = (1.12, 0.92, 1.25)
X1 = np.zeros_like(X0)
for k in range(4):
    j = SJ[:, k]
    X1 += SW[:, k:k + 1] * (J1[j] + A[j] * (X0 - J0[j]))
used = np.zeros(len(X0), bool)
used[TRI.ravel()] = True
feet = (part('Lfoot', 'Rfoot') > 0.5) & used
_shift = FLOOR - X1[feet, 1].max()
X1[:, 1] += _shift
for n in NAMES:
    if n not in ('Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'):
        J1[IDX[n], 1] += _shift
print('floor shift', round(_shift, 1))


# ------------------------------------------------------------------ the drawing's shells
TORSO = [(122, 52, -14, 30, -58, 2.0), (144, 104, -14, 42, -66, 2.2), (168, 140, -16, 54, -76, 2.4),
         (205, 146, -16, 70, -82, 2.6), (260, 140, -14, 84, -82, 2.6), (330, 136, -16, 94, -80, 2.6),
         (400, 138, -20, 90, -84, 2.6), (450, 142, -22, 78, -92, 2.5)]
HIPS = [(400, 134, -20, 84, -82, 2.5), (450, 140, -22, 78, -90, 2.5), (500, 140, -24, 70, -92, 2.4),
        (540, 132, -26, 64, -92, 2.2)]


def rho(rows, X, Y, Z):
    """How far a point is out of a shell (1 on it, < 1 inside): the shell's own superellipse at that height."""
    sh = H.Shell(rows)
    w, zm, zf, zb, n = sh.sl(Y)
    fz = np.where(Z >= zm, (Z - zm) / (zf - zm), (zm - Z) / (zm - zb))
    nn = np.where(Z >= zm, n, 2.0)
    return (np.abs(X / w) ** nn + np.abs(fz) ** nn) ** (1 / nn), zm


def keep_inside(P, rows, k, mask):
    """Points of mask pulled inside the shell scaled by k (toward its middle line)."""
    r, zm = rho(rows, P[:, 0], P[:, 1], P[:, 2])
    f = np.where(mask & (r > k), k / np.maximum(r, 1e-9), 1.0)
    out = P.copy()
    out[:, 0] *= f
    out[:, 2] = zm + (P[:, 2] - zm) * f
    return out


trunk = (part('pelvis', 'spine', 'Lclavicle', 'Rclavicle') > 0.3) & used
X1 = keep_inside(X1, TORSO, 0.9, trunk & (X1[:, 1] < 440) & (X1[:, 1] > 122))
X1 = keep_inside(X1, HIPS, 0.9, trunk & (X1[:, 1] >= 440))

# vertex normals of the fitted body
def vnormals(P, T):
    n = np.zeros_like(P)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    for k in range(3):
        np.add.at(n, T[:, k], fn)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    # Anny in the drawing's frame (y flipped) has its winding mirrored: normals point outward after a flip
    c = P[used].mean(0)
    return n


N1 = vnormals(X1, TRI)
_hips = (part('pelvis') > 0.5) & used
if np.mean(np.einsum('ij,ij->i', N1[_hips], X1[_hips] - X1[_hips].mean(0))) < 0:
    N1 = -N1

OBJ = []
tree_body = cKDTree(np.where(used[:, None], X1, 1e6))


def weights_nearest(P, mask=None, k=24, sigma=12.0):
    """Skin weights for a garment point: Anny's weights of the nearby body vertices blended by distance (a smooth
    field: neighbouring points of a shell move alike), the four largest kept."""
    m = used if mask is None else (mask & used)
    idx = np.nonzero(m)[0]
    t = cKDTree(X1[idx])
    dist, j = t.query(P, k)
    j = idx[j]
    g = np.exp(-((dist - dist[:, :1]) / sigma) ** 2)
    acc = np.zeros((len(P), len(NAMES)))
    for c in range(k):
        for q in range(4):
            np.add.at(acc, (np.arange(len(P)), SJ[j[:, c], q]), g[:, c] * SW[j[:, c], q])
    top = np.argsort(-acc, 1)[:, :4]
    w = np.take_along_axis(acc, top, 1)
    w /= w.sum(1, keepdims=True)
    return top, w


def weights_joint(P, name):
    n = len(P)
    jj = np.zeros((n, 4), int); ww = np.zeros((n, 4))
    jj[:, 0] = IDX[name]; ww[:, 0] = 1
    return jj, ww


def add(name, V, F, colour, sj, sw, **kw):
    F = np.asarray(F)
    if F.shape[1] == 3:
        F = np.hstack([F, -np.ones((len(F), 1), int)])
    OBJ.append(dict(name=name, v=np.asarray(V, float), f=F, colour=colour, sj=sj, sw=sw, meta=kw))


def anny_region(mask_v, offset, name, colour, extra=None, **kw):
    """A shell over Anny's surface where mask_v holds for all three corners, pushed out by offset."""
    tm = mask_v[TRI].all(1)
    T = TRI[tm]
    V = X1 + N1 * (offset if np.ndim(offset) == 0 else offset[:, None])
    if extra is not None:
        V = extra(V)
    Vc, Fc = M.compact(V, T)
    keep = np.unique(T)
    add(name, Vc, Fc, colour, SJ[keep], SW[keep], **kw)
    return keep


# hands (skin), the body itself hidden under the clothes is not drawn
hands = (part('Lhand', 'Rhand') > 0.5) & used
wrist = (part('LforeArm', 'RforeArm') > 0.2) & used
anny_region(hands | (wrist & (part('Lhand', 'Rhand') > 0.15)), 0.0, 'hands', SKIN)

# sleeves: over the arms, from inside the vest down to the wrist
arm = (part('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lclavicle', 'Rclavicle') > 0.5) & used
arm &= (part('Lhand', 'Rhand') < 0.15)

# trouser legs: Anny's thighs and shins on a straight, loose tube (the drawing's radii 60 → 42)
leg = (part('Lthigh', 'Rthigh', 'Lshin', 'Rshin') > 0.5) & used & (X1[:, 1] < FLOOR - 22)
# the seat and crotch: the pelvis below the trouser top's shell, so the trousers close between the legs
seat = (part('pelvis') > 0.4) & used & (X1[:, 1] > 500)


def loosen(V):
    out = V.copy()
    for s, side in ((1, 'Left'), (-1, 'Right')):
        a, b = J1[IDX[side + 'Leg']], J1[IDX[side + 'Foot']]
        a = a + np.array([0, 10, 0])
        m = leg & (np.sign(X1[:, 0]) == s)
        d = b - a
        t = np.clip(((V[m] - a) @ d) / (d @ d), 0, 1)
        c = a + t[:, None] * d
        r_now = np.linalg.norm(V[m] - c, axis=1)
        r_want = np.interp(t, [0, 0.35, 0.7, 1.0], [60, 52, 46, 42])
        r = np.maximum(r_want, r_now + 2)
        dirs = (V[m] - c) / np.maximum(r_now, 1e-6)[:, None]
        out[m] = c + dirs * r[:, None]
    return out


anny_region(leg | seat, 3.0, 'trouserlegs', COL['trousers'], extra=loosen)

# ------------------------------------------------------------------ the drawing's own garments
la, ra = J1[IDX['LeftArm']], J1[IDX['RightArm']]
le, re_ = J1[IDX['LeftForeArm']], J1[IDX['RightForeArm']]


def arm_hole(X, Y, Z, r):
    """Margin of a hole where an arm passes through a torso shell (distance to the upper arm's axis − r)."""
    out = np.full(X.shape, 1e9)
    for a, e in ((la, le), (ra, re_)):
        a2 = a - (e - a) * 0.6
        d = e - a2
        P = np.stack([X, Y, Z], -1)
        t = np.clip(((P - a2) @ d) / (d @ d), 0, 1)
        c = a2 + t[..., None] * d
        out = np.minimum(out, np.linalg.norm(P - c, axis=-1) - r)
    return out


def shell_mesh(rows, y0, y1, margin=None, nu=200, nv=80):
    sh = H.Shell(rows)
    u = np.linspace(0, 2 * np.pi, nu, endpoint=False)
    v = np.linspace(y0, y1, nv)
    return M.grid_cut(lambda U, V: sh.point(U, V), u, v, margin)


# vest: the torso shell 2 out, with its V and its arm holes; ends in two points at the front
VEST = inset(TORSO, -2)


def vest_margin(X, Y, Z, U, V):
    d = np.abs(wrapdeg(U))
    t = np.clip((300 - Y) / (300 - 140), 0, 1)
    vee = d - 26 * t
    hem = 452 + np.clip(30 - d, 0, 30) * 0.9 - Y       # the hem comes down to two points at the front
    return np.minimum(np.minimum(vee, arm_hole(X, Y, Z, 33)), hem)


Vv, Fv = shell_mesh(VEST, 122, 480, vest_margin, nu=128, nv=64)


def tuck(V):
    """The sleeve's top kept under the vest where the vest covers it, so it comes out of the arm hole (whose edge
    the line draws) instead of through the cloth."""
    m = np.ones(len(V), bool)
    r, zm = rho(VEST, V[:, 0], V[:, 1], V[:, 2])
    hole = arm_hole(V[:, 0], V[:, 1], V[:, 2], 33)
    sel = (hole > -6) & (r > 0.9) & (r < 1.2) & (V[:, 1] < 452)
    return keep_inside(V, VEST, 0.96, sel)


anny_region(arm, 2.5, 'sleeves', COL['shirt'], extra=tuck)
sj, sw = weights_nearest(Vv, trunk)
add('vest', Vv, Fv, COL['vest'], sj, sw)
vest_shell = H.Shell(VEST)

# shirt body: the torso shell 6 in, from the collar down into the trousers, with arm holes
Vs, Fs = shell_mesh(inset(TORSO, 6), 122, 440, lambda X, Y, Z, U, V: arm_hole(X, Y, Z, 34), nu=80, nv=44)
sj, sw = weights_nearest(Vs, trunk)
add('shirt', Vs, Fs, COL['shirt'], sj, sw)
shirt_shell = H.Shell(inset(TORSO, 6))

# trouser top: the hips shell
Vh, Fh = shell_mesh(HIPS, 420, 540, None, nu=96, nv=16)
sj, sw = weights_nearest(Vh, trunk | leg)
add('trousers', Vh, Fh, COL['trousers'], sj, sw)

# shoes: the drawing's blobs (30, 24, 60), set on each foot along it
for s, side in ((1, 'Left'), (-1, 'Right')):
    f, t = J1[IDX[side + 'Foot']], J1[IDX[side + 'ToeEnd']]
    c = np.array([(f[0] + t[0]) / 2, FLOOR - 26, (f[2] + t[2]) / 2 + 10])
    Ve, Fe = M.ellipsoid(c, (36, 28, 74), nu=36, nv=18)
    Ve[:, 1] = np.minimum(Ve[:, 1], FLOOR)                   # a flat sole on the floor
    footm = (part(('L' if s > 0 else 'R') + 'foot') > 0.5) & used
    sj, sw = weights_nearest(Ve, footm)
    add('shoe' + side, Ve, Fe, COL['shoe'], sj, sw)

# collar points and the bow tie (figures.savely_figure), on the shirt
for s in (1, -1):
    p = H.lock_part(shirt_shell, [(s * -4, 124), (s * -14, 134), (s * -22, 146)], [8, 9, 0], lift=3, res=1.0)
    P = np.stack([p.X, p.Y, p.Z], 1)
    m = int(max(8, 9 * 2 * 1.0 * 1.5))
    n = len(P) // m
    q = np.array([(i * m + j, (i + 1) * m + j, (i + 1) * m + j + 1, i * m + j + 1) for i in range(n - 1) for j in range(m - 1)])
    sj, sw = weights_joint(P, 'Chest')
    add(f'collar{s}', P, q, COL['shirt'], sj, sw, solidify=1.0)
zb = float(shirt_shell.sl(142)[2]) + 6
for s in (1, -1):
    a = np.radians(s * -10)
    R = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Ve, Fe = M.ellipsoid((s * 16, 142, zb), (16, 10, 6), R, nu=24, nv=12)
    add(f'bow{s}', Ve, Fe, COL['tie'], *weights_joint(Ve, 'Chest'))
Ve, Fe = M.ellipsoid((0, 142, zb + 3), (7, 8, 6), nu=20, nv=10)
add('knot', Ve, Fe, COL['tie'], *weights_joint(Ve, 'Chest'))

# buttons, pocket, chain and the watch in the vest pocket
vc = vest_shell.curve
btn = []
for y in (310, 352, 394):
    p = vc([(0, y)])[0] + [0, 0, 1.5]
    Ve, Fe = M.ellipsoid(p, (4.5, 4.5, 2.0), nu=16, nv=8)
    add(f'button{y}', Ve, Fe, '#c9a35a', *weights_nearest(Ve, trunk))
# the watch: a gold case peeking out of the left pocket (the person's left: x > 0... the drawing's pocket at -angle)
wp = vc([(-40, 352)])[0]
nrm = wp - np.array([0, 352, float(vest_shell.sl(352)[1])]); nrm /= np.linalg.norm(nrm)
R = np.array([[1, 0, 0], [0, 1, 0], nrm]); R[0] -= R[0] @ nrm * nrm; R[0] /= np.linalg.norm(R[0])
R[1] = np.cross(nrm, R[0])
Ve, Fe = M.ellipsoid(wp + nrm * 3 + np.array([0, -8, 0]), (12, 12, 3.5), R.T, nu=28, nv=10)
add('watch', Ve, Fe, COL['gold'], *weights_nearest(Ve, trunk))
Ve, Fe = M.ellipsoid(wp + nrm * 6.2 + np.array([0, -8, 0]), (9, 9, 0.6), R.T, nu=28, nv=6)
add('watchface', Ve, Fe, COL['face'], *weights_nearest(Ve, trunk))
chain = vc([(0, 352), (-12, 372), (-26, 370), (-38, 346)]) + nrm * 0 + np.array([0, 0, 2.5])
from scipy.interpolate import CubicSpline
cs = CubicSpline(np.linspace(0, 1, len(chain)), chain)
Ve, Fe = M.tube(cs(np.linspace(0, 1, 40)), 1.3, nseg=6)
add('chain', Ve, Fe, COL['chain'], *weights_nearest(Ve, trunk), line=False)

# lines on the clothes, as the drawing has them: pocket welts, the vest's seam at the hem, trouser creases
LINES = []
for s in (1, -1):
    LINES.append((vc([(s * 30, 360), (s * 52, 356)]), 0.6, 'vest'))
    LINES.append((vc([(s * 32, 250), (s * 52, 246)]), 0.6, 'vest'))
json.dump([dict(pts=(p + np.array([0, 0, 1.0]) * 0).tolist(), w=w) for p, w, _ in LINES],
          open(os.path.join(C, 'body_lines.json'), 'w'))

names = [o['name'] for o in OBJ]
arr = {'names': np.array(names), 'joints': J1, 'joints0': J0, 'anny_raw': X0, 'anny_fit': X1, 'anny_tri': TRI[used[TRI].all(1)]}
for o in OBJ:
    arr[o['name'] + '_v'] = o['v']
    arr[o['name'] + '_f'] = o['f']
    arr[o['name'] + '_sj'] = o['sj']
    arr[o['name'] + '_sw'] = o['sw']
    arr[o['name'] + '_meta'] = json.dumps(dict(o['meta'], colour=o['colour']))
np.savez(os.path.join(C, 'body.npz'), **arr)
print({o['name']: len(o['v']) for o in OBJ}, sum(len(o['v']) for o in OBJ))
print('joints: arm', J1[IDX['LeftArm']].round(1), 'leg', J1[IDX['LeftLeg']].round(1), 'hand', J1[IDX['LeftHand']].round(1),
      'foot', J1[IDX['LeftFoot']].round(1))
