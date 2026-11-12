"""Марат's body and clothes, on Anny (engine/data/bodies/moood-man: Anny baked by moood, SOMA skeleton).

1. Anny's man is fitted to the drawing's proportions (styles/s10-ligne-claire/tools/marat.py: figure, arms down):
   each bone of the skeleton is scaled — the trunk a third longer, the shoulders half again as wide, the forearms
   shorter, the hands bigger — and every vertex follows its own joints by Anny's skin weights
   (v' = Σ w·(J' + A·(v − J))); the frames stay, so Kimodo's motions carry as they do on any engine body.
   The barrel of his body is the drawing's own jacket shell: Anny's trunk is only kept inside it.
   The bare forearms are Anny's, made as thick as drawn (45 → 33) about their bones; the fingers are laid side by
   side and thicker, so the hand reads as one shape.
2. Clothes are made to the drawing: the cook's jacket, its collar, the apron and the trousers' top are the drawing's
   own shells; the sleeves (rolled above the elbow) and trouser legs are shells over Anny's arms and legs, widened
   to the drawn radii; shoes, buttons, the towel over the shoulder, the jacket's flap, the apron's fold and pocket
   from the drawing's shapes.  The ladle of the drawing's pose is left out: his arms hang, as in its turnaround.
3. Every piece gets four SOMA joints and weights: Anny's own where it is Anny's, else from the nearby Anny
   vertices; the apron's lower part from both legs blended across its width (and a little from the hips), so it
   hangs between the legs.
Units: the drawing's (y down, z toward the viewer), floor at who.FLOOR; who.K metres per unit.
usage: python3 body.py CACHE → CACHE/body.npz
"""
import sys, os, json
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import who                      # noqa: E402
import pack                     # noqa: E402
import meshes as M              # noqa: E402
import head as H                # noqa: E402
from figures import inset       # noqa: E402
import body as Bd               # noqa: E402  (the drawing's body.py: its spline)
from cast import wrapdeg        # noqa: E402

C = sys.argv[1]
REPO = who.REPO
K, FLOOR = who.K, who.FLOOR
COL = who.colours()
SKIN = COL['skin']
INK = '#1b1714'

sk = json.load(open(os.path.join(REPO, 'engine/data/skeleton.json')))
NAMES = [j['name'] for j in sk['joints']]
PARENT = [j['parent'] for j in sk['joints']]
IDX = {n: i for i, n in enumerate(NAMES)}
th, top = pack.read(os.path.join(REPO, 'engine/data/topology/anny-moood.json'))
bh, bod = pack.read(os.path.join(REPO, f'engine/data/bodies/{who.BASE_BODY}.json'))
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
FINGERS = ('Index', 'Middle', 'Ring', 'Pinky')


def scale_of(name):
    """The scale of the bone from this joint's parent to it, per axis (x, y, z) in the drawing's frame."""
    if name in ('LeftLeg', 'RightLeg'):
        return (1.1, 1.0, 1.0)
    if 'Shin' in name or ('Foot' in name and 'Toe' not in name):
        return (0.25, 1.0, 0.6)              # the legs straight down, the ankle under the knee
    if 'Toe' in name:
        return (0.9, 0.9, 0.9)
    if name in ('Spine1', 'Spine2', 'Chest', 'Neck1'):
        return (1.0, 1.36, 1.0)              # a long barrel of a trunk: the shoulders at the drawing's height
    if 'Shoulder' in name:
        return (1.0, 1.36, 1.0)
    if name in ('LeftArm', 'RightArm'):
        return (1.55, 1.0, 1.0)              # heavy shoulders: the arms start at x ±176
    if name in ('LeftForeArm', 'RightForeArm'):
        return (0.97,) * 3
    if name in ('LeftHand', 'RightHand'):
        return (0.82,) * 3                   # the drawing's forearm is short and thick
    if 'Hand' in name:
        return (1.22,) * 3                   # big hands
    return (1.0, 1.0, 1.0)


S = np.array([scale_of(n) for n in NAMES])
J1 = J0.copy()
for j in range(len(NAMES)):                      # joints are listed parents first
    p = PARENT[j]
    if p < 0:
        J1[j] = J0[j]
        continue
    J1[j] = J1[p] + (J0[j] - J0[p]) * S[j]
# the fingers side by side: every finger's joints along the middle finger's direction
for side in ('Left', 'Right'):
    m1, me = J1[IDX[side + 'HandMiddle1']], J1[IDX[side + 'HandMiddleEnd']]
    dm = (me - m1) / np.linalg.norm(me - m1)
    for f in FINGERS:
        base = J1[IDX[f'{side}Hand{f}1']].copy()
        if f != 'Middle':
            base = m1 + (base - m1) * 0.94
        prev_old, prev_new = J1[IDX[f'{side}Hand{f}1']].copy(), base
        J1[IDX[f'{side}Hand{f}1']] = base
        for seg in ('2', '3', '4', 'End'):
            j = IDX[f'{side}Hand{f}{seg}']
            old = J1[j].copy()
            L = np.linalg.norm(old - prev_old)
            d = 0.25 * (old - prev_old) / max(L, 1e-9) + 0.75 * dm
            new = prev_new + d / np.linalg.norm(d) * L
            J1[j] = new
            prev_old, prev_new = old, new
J1 += np.array([0, 0, -J1[IDX['Hips'], 2] - 18])
# the neck and head joints: where the drawing's head turns on its neck (figures.NECK + the head drop)
HEAD_JOINTS = ('Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye')
D = who.DROP
for n, p in (('Neck1', (0, 158 + D, -14)), ('Neck2', (0, 132 + D, -12)), ('Head', (0, 106 + D, -10)),
             ('HeadEnd', (0, -104 + D, -10)), ('Jaw', (0, 90 + D, 20)), ('LeftEye', (who.EYE[0], who.EYE[1] + D, 58)),
             ('RightEye', (-who.EYE[0], who.EYE[1] + D, 58))):
    J1[IDX[n]] = p

# vertices follow their joints: v' = Σ w (J'_k + A_k (v − J_k)); A_k: the joint's own girth
A = S.copy()
for n in NAMES:
    if 'Leg' in n or 'Shin' in n:
        A[IDX[n]] = (1.0, 1.0, 1.0)
    if 'Foot' in n or 'Toe' in n:
        A[IDX[n]] = (1.0, 1.0, 0.9)
    if 'Arm' in n:
        A[IDX[n]] = (1.0, 1.0, 1.0)
    if 'Hand' in n:
        A[IDX[n]] = (1.3, 1.3, 1.3)
    if any(f in n for f in FINGERS):
        A[IDX[n]] = (1.42, 1.42, 1.42)           # thick fingers lying against each other
X1 = np.zeros_like(X0)
for k in range(4):
    j = SJ[:, k]
    X1 += SW[:, k:k + 1] * (J1[j] + A[j] * (X0 - J0[j]))
used = np.zeros(len(X0), bool)
used[TRI.ravel()] = True
feet = (part('Lfoot', 'Rfoot') > 0.5) & used
_shift = FLOOR - 8 - X1[feet, 1].max()            # the sole of the shoe is 8 under the foot
X1[:, 1] += _shift
for n in NAMES:
    if n not in HEAD_JOINTS:
        J1[IDX[n], 1] += _shift
print('floor shift', round(_shift, 1))


# ------------------------------------------------------------------ the drawing's shells (marat.figure)
TORSO = [(126, 64, -14, 36, -64, 2.0), (148, 132, -14, 52, -78, 2.2), (174, 182, -16, 68, -90, 2.4),
         (218, 194, -16, 92, -100, 2.6), (292, 192, -12, 114, -102, 2.6), (382, 186, -10, 126, -100, 2.6),
         (462, 178, -10, 124, -100, 2.6), (542, 172, -12, 106, -102, 2.5), (604, 168, -14, 94, -102, 2.4)]
COLLAR = [(104, 62, -14, 44, -66, 2.0), (126, 66, -14, 46, -68, 2.0), (146, 76, -14, 50, -72, 2.0)]
APRON = inset(TORSO, -5, y0=462) + [(800, 172, -10, 96, -104, 2.3), (1060, 180, -8, 102, -104, 2.2)]
HIPS = [(560, 168, -12, 100, -100, 2.5), (640, 166, -14, 92, -100, 2.4), (700, 150, -14, 84, -94, 2.3)]


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
legs_all = (part('Lthigh', 'Rthigh', 'Lshin', 'Rshin') > 0.3) & used
X1 = keep_inside(X1, TORSO, 0.9, trunk & (X1[:, 1] < 590) & (X1[:, 1] > 126))
X1 = keep_inside(X1, HIPS, 0.9, trunk & (X1[:, 1] >= 590))


def vnormals(P, T):
    n = np.zeros_like(P)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    for k in range(3):
        np.add.at(n, T[:, k], fn)
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


N1 = vnormals(X1, TRI)
_hips = (part('pelvis') > 0.5) & used
if np.mean(np.einsum('ij,ij->i', N1[_hips], X1[_hips] - X1[_hips].mean(0))) < 0:
    N1 = -N1

OBJ = []


def weights_nearest(P, mask=None, k=24, sigma=12.0, top4=True):
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
    acc /= acc.sum(1, keepdims=True)
    return top_four(acc) if top4 else acc


def top_four(acc):
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


def along(V, pieces, mask, grow=2.0):
    """Vertices of mask set at given radii about their bones: pieces = ((joint a, joint b), part name, (r0, r1))."""
    out = V.copy()
    acc = np.zeros_like(V); wsum = np.zeros(len(V))
    for (ja, jb), pn, (r0, r1) in pieces:
        a, b = J1[IDX[ja]], J1[IDX[jb]]
        d = b - a
        t = np.clip(((V - a) @ d) / (d @ d), 0, 1)
        c = a + t[:, None] * d
        r_now = np.linalg.norm(V - c, axis=1)
        r = np.maximum(r0 + (r1 - r0) * t, r_now + grow) if grow is not None else r0 + (r1 - r0) * t
        cand = c + (V - c) / np.maximum(r_now, 1e-6)[:, None] * r[:, None]
        w = part(pn)
        acc += cand * w[:, None]; wsum += w
    rest = np.clip(1 - wsum, 0, 1)
    m = (wsum > 0) & mask
    out[m] = (acc[m] + V[m] * rest[m, None]) / (wsum[m] + rest[m])[:, None]
    return out


ARMS = [((s + 'Arm', s + 'ForeArm'), L + 'upperArm', (54, 51)) for s, L in (('Left', 'L'), ('Right', 'R'))]
FORE = [((s + 'ForeArm', s + 'Hand'), L + 'foreArm', (45, 34)) for s, L in (('Left', 'L'), ('Right', 'R'))]
# (the drawn legs are 78 thick at the top; under the apron they are kept thinner, so a step doesn't bring them
# through it — what shows below the apron's hem is as drawn)
LEGS = [((s + 'Leg', s + 'Shin'), L + 'thigh', (56, 54)) for s, L in (('Left', 'L'), ('Right', 'R'))] + \
       [((s + 'Shin', s + 'Foot'), L + 'shin', (54, 50)) for s, L in (('Left', 'L'), ('Right', 'R'))]

# the bare forearms as thick as drawn, then the hands (skin)
fore = (part('LforeArm', 'RforeArm') > 0.5) & used & (part('Lhand', 'Rhand') < 0.3)
X1 = np.where(fore[:, None], along(X1, FORE, fore, grow=None) * 0.8 + X1 * 0.2, X1)
N1 = vnormals(X1, TRI)
if np.mean(np.einsum('ij,ij->i', N1[_hips], X1[_hips] - X1[_hips].mean(0))) < 0:
    N1 = -N1
skin_arm = ((part('LforeArm', 'RforeArm', 'Lhand', 'Rhand') > 0.5) | ((part('LupperArm', 'RupperArm') > 0.5)
            & (part('LforeArm', 'RforeArm') > 0.12))) & used
anny_region(skin_arm, 0.0, 'hands', SKIN)

# sleeves, rolled above the elbow: over the upper arms, at the drawn radius, a thicker roll at the end
upper = (part('LupperArm', 'RupperArm') > 0.4) & used & (part('LforeArm', 'RforeArm') < 0.45)


def sleeve(V):
    out = along(V, ARMS, upper)
    roll = np.clip((part('LforeArm', 'RforeArm') - 0.12) / 0.15, 0, 1)        # the last part before the elbow
    for s in ('Left', 'Right'):
        a, b = J1[IDX[s + 'Arm']], J1[IDX[s + 'ForeArm']]
        d = b - a
        t = np.clip(((out - a) @ d) / (d @ d), 0, 1)
        c = a + t[:, None] * d
        m = upper & (np.sign(X1[:, 0]) == (1 if s == 'Left' else -1))
        out[m] = c[m] + (out[m] - c[m]) * (1 + 0.1 * roll[m, None])
    return out


anny_region(upper, 3.0, 'sleeves', COL['jacket'], extra=sleeve)

# trouser legs: Anny's thighs and shins on straight, heavy tubes (the drawing's radii 78 → 50)
leg = (part('Lthigh', 'Rthigh', 'Lshin', 'Rshin') > 0.5) & used
leg |= (part('Lfoot', 'Rfoot') > 0.5) & used & (X1[:, 1] < FLOOR - 42)       # the ankle too: the hem is cut below it
seat = (part('pelvis') > 0.4) & used & (X1[:, 1] > 640)
def trouser(V):
    out = along(V, LEGS, leg)
    out[:, 1] = np.minimum(out[:, 1], FLOOR - 40)           # a straight hem over the shoe
    return out


anny_region(leg | seat, 3.0, 'trouserlegs', COL['trousers'], extra=trouser)

def shell_mesh(rows, y0, y1, margin=None, nu=200, nv=80):
    sh = H.Shell(rows)
    u = np.linspace(0, 2 * np.pi, nu, endpoint=False)
    v = np.linspace(y0, y1, nv)
    V, F = M.grid_cut(lambda U, V: sh.point(U, V), u, v, margin)
    return smooth_edge(V, F), F


def smooth_edge(V, F, it=4):
    """The cut edge of a grid mesh drawn smooth: each edge vertex moved toward the middle of its two edge
    neighbours (a diagonal cut across a grid leaves small steps)."""
    from collections import defaultdict
    cnt = defaultdict(int)
    for f in F:
        f = [x for x in f if x >= 0]
        for i in range(len(f)):
            a, b = f[i - 1], f[i]
            cnt[(min(a, b), max(a, b))] += 1
    nb = defaultdict(list)
    for (a, b), c in cnt.items():
        if c == 1:
            nb[a].append(b); nb[b].append(a)
    idx = [i for i, n in nb.items() if len(n) == 2]
    V = V.copy()
    for _ in range(it):
        V[idx] = 0.5 * V[idx] + 0.25 * (V[[nb[i][0] for i in idx]] + V[[nb[i][1] for i in idx]])
    return V


# the cook's jacket: the drawing's torso shell, whole; its stand-up collar open at the front
jacket = H.Shell(TORSO)
Vj, Fj = shell_mesh(TORSO, 126, 604, None, nu=128, nv=64)
add('jacket', Vj, Fj, COL['jacket'], *weights_nearest(Vj, trunk))
Vc, Fc = shell_mesh(COLLAR, 104, 146, lambda X, Y, Z, U, V: np.abs(wrapdeg(U)) - 7, nu=96, nv=10)
add('collar', Vc, Fc, COL['jacket'], *weights_joint(Vc, 'Neck1'))

# the trousers' top: the hips shell
Vh, Fh = shell_mesh(HIPS, 580, 700, None, nu=96, nv=14)
add('trousers', Vh, Fh, COL['trousers'], *weights_nearest(Vh, trunk | leg))

# the apron: the front of its shell, from the waist nearly to the ankles; below the hips its points take both legs'
# weights blended across the width (and a little of the hips'), so it hangs between the legs
apron = H.Shell(APRON)
Va, Fa = shell_mesh(APRON, 462, 1060, lambda X, Y, Z, U, V: 112 - np.abs(wrapdeg(U)), nu=120, nv=48)
side_l = (trunk | legs_all) & (X1[:, 0] > -2)
side_r = (trunk | legs_all) & (X1[:, 0] < 2)
wl = weights_nearest(Va, side_l, k=32, sigma=30, top4=False)
wr = weights_nearest(Va, side_r, k=32, sigma=30, top4=False)
a = np.clip((Va[:, 0] + 45) / 90, 0, 1)
a = (a * a * (3 - 2 * a))[:, None]
wleg = wl * a + wr * (1 - a)
whip = np.zeros_like(wleg); whip[:, IDX['Hips']] = 1
kh = (0.12 * np.clip((Va[:, 1] - 640) / 120, 0, 1))[:, None]
APRON_W = wleg * (1 - kh) + whip * kh
add('apron', Va, Fa, COL['apron'], *top_four(APRON_W))

# shoes: heavy ovals over each foot, the sole flat on the floor
for s, side in ((1, 'Left'), (-1, 'Right')):
    fm = (part(('L' if s > 0 else 'R') + 'foot') > 0.5) & used & (X1[:, 1] > FLOOR - 45)
    lo, hi = X1[fm].min(0), X1[fm].max(0)
    c = np.array([(lo[0] + hi[0]) / 2, FLOOR - 27, (lo[2] + hi[2]) / 2])
    Ve, Fe = M.ellipsoid(c, ((hi[0] - lo[0]) / 2 + 6, 28, (hi[2] - lo[2]) / 2 + 8), nu=36, nv=18)
    Ve[:, 1] = np.minimum(Ve[:, 1], FLOOR)
    footm = (part(('L' if s > 0 else 'R') + 'foot') > 0.5) & used
    add('shoe' + side, Ve, Fe, COL['shoe'], *weights_nearest(Ve, footm))
    print('shoe', side, (hi - lo).round(0))


def front_z(shell, x, y):
    w, zm, zf, zb, n = shell.sl(y)
    a = np.clip(np.abs(x) / np.maximum(w, 1e-3), 0, 1)
    return float(zm + (zf - zm) * (1 - a ** n) ** (1 / n))


# the towel over his left shoulder: a band from the chest up over the shoulder and down the back (marat.figure)
tz = lambda x, y: front_z(jacket, x, y) + 7
path = [(112, 380, tz(112, 380)), (114, 300, tz(114, 300)), (118, 226, tz(118, 226)), (120, 176, tz(120, 176) + 2),
        (120, 140, 16), (120, 136, -34), (120, 168, -84), (118, 250, -112), (116, 340, -114)]
Cc, _ = Bd._spline(path, 60)
Tt = np.gradient(Cc, axis=0)
Tt /= np.linalg.norm(Tt, axis=1, keepdims=True) + 1e-9
Nn = np.cross(Tt, [1.0, 0, 0])
Nn /= np.linalg.norm(Nn, axis=1, keepdims=True) + 1e-9
ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
Vt = (Cc[:, None, :] + np.array([1.0, 0, 0])[None, None, :] * (25 * np.cos(ang))[None, :, None]
      + Nn[:, None, :] * (3.0 * np.sin(ang))[None, :, None]).reshape(-1, 3)
Ft = [(i * 16 + j, i * 16 + (j + 1) % 16, (i + 1) * 16 + (j + 1) % 16, (i + 1) * 16 + j)
      for i in range(len(Cc) - 1) for j in range(16)]
add('towel', Vt, np.array(Ft), COL['towel'], *weights_nearest(Vt, trunk))

# buttons: two rows on the double-breasted front
jc = jacket.curve
for y in (236, 306, 376, 440):
    for d in (-19, 17):
        p = jc([(d, y)])[0] + [0, 0, 1.5]
        Ve, Fe = M.ellipsoid(p, (6.5, 6.5, 2.4), nu=16, nv=8)
        add(f'button{y}_{d}', Ve, Fe, COL['jacket'], *weights_nearest(Ve, trunk))

# lines the drawing has, as thin ink (or the apron's colour for the towel's stripes): the flap's edge, the apron's
# fold at the waist and its pocket, the towel's stripes
from scipy.interpolate import CubicSpline
def on_shell(shell, pts, n=40, corners=False):
    """A line on a shell through (degrees, y) points: sampled in the shell's own coordinates, so it lies on it."""
    Q = np.array(pts, float)
    if corners:
        Q = np.vstack([Q[k] + (Q[k + 1] - Q[k]) * np.linspace(0, 1, 8, endpoint=False)[:, None] for k in range(len(Q) - 1)]
                      + [Q[-1:]])
    else:
        Q = CubicSpline(np.linspace(0, 1, len(Q)), Q)(np.linspace(0, 1, n))
    return shell.curve([tuple(q) for q in Q])


LINES = [(on_shell(jacket, [(-10, 150), (-27, 200), (-30, 300), (-28, 400), (-26, 462)]), 0.7, jacket, INK, 'trunk'),
         (on_shell(apron, [(d, 500 + 4 * np.cos(np.radians(d))) for d in range(-108, 109, 12)]), 0.7, apron, INK, 'apron'),
         (on_shell(apron, [(-58, 640), (-56, 740), (-22, 744), (-22, 640), (-58, 640)], corners=True), 0.6, apron, INK,
          'apron')]
for y in (346, 359):
    xs = np.linspace(89, 137, 12)
    LINES.append((np.array([(x, y, front_z(jacket, x, y) + 10.5) for x in xs]), 1.6, None, COL['apron'], 'trunk'))
for i, (P, w, sh, colour, what) in enumerate(LINES):
    if what == 'apron':
        _, j = cKDTree(Va).query(P)
        sj, sw = top_four(APRON_W[j])
    else:
        sj, sw = weights_nearest(P, trunk)
    if sh is not None:
        zm = sh.sl(P[:, 1])[1]
        nrm = P - np.stack([0 * zm, P[:, 1], zm], 1)
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
        P = P + nrm * 1.8
    Vt, Ft = M.tube(P, w * 1.5, nseg=6)
    rep = np.r_[np.repeat(np.arange(len(P)), 6), [0, len(P) - 1]]
    add(f'seam{i}', Vt, Ft, colour, sj[rep], sw[rep], line=False)

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
for n in ('LeftArm', 'LeftForeArm', 'LeftHand', 'LeftLeg', 'LeftShin', 'LeftFoot', 'Hips', 'Chest'):
    print(n, J1[IDX[n]].round(1))
