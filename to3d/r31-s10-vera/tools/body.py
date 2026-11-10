"""Вера's body and clothes, on Anny (engine/data/bodies/moood-woman: Anny baked by moood, SOMA skeleton).

1. Anny's woman is fitted to the drawing's proportions (styles/s10-ligne-claire/tools/figures.py: vera_figure):
   each bone of the skeleton is scaled (the whole figure taller, legs close together and straight, arms shorter),
   and every vertex follows its own joints by Anny's skin weights (v' = Σ w·(J' + A·(v − J))) — the frames stay, so
   Kimodo's motions carry as they do on any engine body.  The trunk is kept inside the drawing's own shells.
   The fingers are laid side by side (each finger's joints set along the middle finger's direction) and a little
   thicker, so the hand reads as the style's hand: one shape with short lines between the fingers.
2. Clothes are made to the drawing: the jacket (with its V opening) and the blouse are the drawing's
   own torso shells, the skirt is its skirt shell; the sleeves are shells laid over Anny's arms, widened to the
   drawing's sleeve; the legs in tights are Anny's own; shoes, the blouse's collar, the lapels, buttons and the
   seams from the drawing's shapes.  The folder is a box held in the left hand.
3. Every piece gets four SOMA joints and weights: Anny's own where it is Anny's, else from the nearby Anny
   vertices; the skirt's from both legs, blended across its width, so it spans between them like cloth pulled tight.
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
U = 1.17                                         # the drawing's Вера against Anny's woman, overall
FINGERS = ('Index', 'Middle', 'Ring', 'Pinky')


def scale_of(name):
    """The scale of the bone from this joint's parent to it, per axis (x, y, z) in the drawing's frame."""
    if name in ('LeftLeg', 'RightLeg'):
        return (0.46 * U, U, U)              # the drawing's legs stand close together under the narrow skirt
    if 'Shin' in name or ('Foot' in name and 'Toe' not in name):
        return (0.0, U, 0.45 * U)            # and straight down, not splayed as Anny's rest; the ankle under the knee
    if 'Toe' in name:
        return (0.7 * U, 0.7 * U, 0.58 * U)  # small shoes
    if name in ('LeftForeArm', 'RightForeArm', 'LeftHand', 'RightHand'):
        return (0.86 * U,) * 3               # the drawing's arms are shorter (the wrist at the hip)
    if 'Hand' in name:
        return (0.98 * U,) * 3
    return (U, U, U)


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
    hand = J1[IDX[side + 'Hand']]
    for f in FINGERS:
        base = J1[IDX[f'{side}Hand{f}1']].copy()
        if f != 'Middle':                        # the knuckles a little closer to the middle one
            base = m1 + (base - m1) * 0.94
        prev_old, prev_new = J1[IDX[f'{side}Hand{f}1']].copy(), base
        J1[IDX[f'{side}Hand{f}1']] = base
        for seg in ('2', '3', '4', 'End'):
            j = IDX[f'{side}Hand{f}{seg}']
            old = J1[j].copy()
            L = np.linalg.norm(old - prev_old)
            d = (old - prev_old) / max(L, 1e-9)
            d = 0.25 * d + 0.75 * dm
            new = prev_new + d / np.linalg.norm(d) * L
            J1[j] = new
            prev_old, prev_new = old, new
# the root: the body centred where the drawing stands
J1 += np.array([0, 0, -J1[IDX['Hips'], 2] - 14])
# the neck and head joints: where the drawing's head turns on its neck (figures.NECK + the head drop)
HEAD_JOINTS = ('Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye')
for n, p in (('Neck1', (0, 178, -14)), ('Neck2', (0, 152, -12)), ('Head', (0, 126, -10)), ('HeadEnd', (0, -84, -10)),
             ('Jaw', (0, 110, 20)), ('LeftEye', (who.EYE[0], who.EYE[1] + who.DROP, 58)),
             ('RightEye', (-who.EYE[0], who.EYE[1] + who.DROP, 58))):
    J1[IDX[n]] = p

# vertices follow their joints: v' = Σ w (J'_k + A_k (v − J_k)); A_k: the joint's own girth
A = S.copy()
for n in NAMES:
    if 'Shin' in n:
        A[IDX[n]] = (1.0, U, 1.0)                # slim legs, as drawn (the calf's radius 38)
    if 'Leg' in n:
        A[IDX[n]] = (0.66, U, 0.66)              # the thighs thin: they are under the skirt and must stay under it
    if 'Foot' in n or 'Toe' in n:
        A[IDX[n]] = (0.8, 0.85, 0.66)
    if 'Arm' in n:
        A[IDX[n]] = (1.0, 1.0, 1.0)
    if 'Hand' in n:
        A[IDX[n]] = (1.12, 1.12, 1.12)
    if any(f in n for f in FINGERS):
        A[IDX[n]] = (1.22, 1.22, 1.22)           # fingers thick enough to lie against each other
X1 = np.zeros_like(X0)
for k in range(4):
    j = SJ[:, k]
    X1 += SW[:, k:k + 1] * (J1[j] + A[j] * (X0 - J0[j]))
used = np.zeros(len(X0), bool)
used[TRI.ravel()] = True
feet = (part('Lfoot', 'Rfoot') > 0.5) & used
_shift = FLOOR - 6 - X1[feet, 1].max()            # the sole of the shoe is 6 under the foot
X1[:, 1] += _shift
for n in NAMES:
    if n not in HEAD_JOINTS:
        J1[IDX[n], 1] += _shift
print('floor shift', round(_shift, 1))


# ------------------------------------------------------------------ the drawing's shells (figures.vera_figure)
TORSO = [(126, 41, -12, 28, -50, 2.0), (148, 90, -10, 40, -58, 2.2), (172, 124, -12, 52, -64, 2.4),
         (210, 128, -10, 64, -68, 2.6), (265, 118, -6, 74, -66, 2.6), (335, 98, -4, 58, -60, 2.6),
         (405, 94, -2, 56, -60, 2.6), (460, 118, 0, 64, -70, 2.5), (505, 128, 0, 68, -76, 2.4)]
SKIRT = [(400, 88, -2, 52, -56, 2.4), (470, 116, 0, 62, -68, 2.4), (600, 114, 0, 62, -68, 2.3),
         (860, 98, 0, 56, -62, 2.2)]


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
X1 = keep_inside(X1, inset(TORSO, 7), 0.92, trunk & (X1[:, 1] < 430) & (X1[:, 1] > 126))
X1 = keep_inside(X1, SKIRT, 0.9, (trunk | legs_all) & (X1[:, 1] >= 430) & (X1[:, 1] < 850))


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


# hands (skin)
hands = (part('Lhand', 'Rhand') > 0.5) & used
wrist = (part('LforeArm', 'RforeArm') > 0.2) & used
anny_region(hands | (wrist & (part('Lhand', 'Rhand') > 0.15)), 0.0, 'hands', SKIN)

# legs in tights: Anny's own legs and feet (the skirt hides them above the knee)
tights = (part('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot') > 0.5) & used
anny_region(tights | ((part('pelvis') > 0.4) & used & (X1[:, 1] > 560)), 0.6, 'tights', COL['tights'])

# sleeves: over the arms, from inside the jacket down to the wrist, widened to the drawing's sleeve (33 → 26)
arm = (part('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm') > 0.5) & used        # the shoulder is the jacket's
arm &= (part('Lhand', 'Rhand') < 0.15)


def widen(V):
    out = V.copy()
    for s, side, L in ((1, 'Left', 'L'), (-1, 'Right', 'R')):
        acc = np.zeros_like(V); wsum = np.zeros(len(V))
        for (ja, jb), pn, (r0, r1) in (((side + 'Arm', side + 'ForeArm'), L + 'upperArm', (34, 31)),
                                        ((side + 'ForeArm', side + 'Hand'), L + 'foreArm', (31, 27))):
            a, b = J1[IDX[ja]], J1[IDX[jb]]
            d = b - a
            t = np.clip(((V - a) @ d) / (d @ d), 0, 1)
            c = a + t[:, None] * d
            r_now = np.linalg.norm(V - c, axis=1)
            r = np.maximum(r0 + (r1 - r0) * t, r_now + 2)
            cand = c + (V - c) / np.maximum(r_now, 1e-6)[:, None] * r[:, None]
            w = part(pn)
            acc += cand * w[:, None]; wsum += w
        rest = np.clip(1 - wsum, 0, 1)                 # the shoulder's own vertices stay
        m = (wsum > 0) & arm
        out[m] = (acc[m] + V[m] * rest[m, None]) / (wsum[m] + rest[m])[:, None]
    return out


# ------------------------------------------------------------------ the drawing's own garments
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


def jacket_margin(X, Y, Z, U, V):
    d = np.abs(wrapdeg(U))
    t = np.clip((330 - Y) / (330 - 140), 0, 1)         # figures.vneck(330, 140, 30)
    return d - 30 * t


Vj, Fj = shell_mesh(TORSO, 126, 505, jacket_margin, nu=128, nv=64)


# the sleeves go into the jacket's shoulder as they are (an arm hole there opens at the back when the arm is down)
anny_region(arm, 2.5, 'sleeves', COL['jacket'], extra=widen)
add('jacket', Vj, Fj, COL['jacket'], *weights_nearest(Vj, trunk))
jacket = H.Shell(TORSO)

# blouse: the torso shell 7 in, from the collar down to the waist
BLOUSE = inset(TORSO, 7, y1=405)
# (only its front, which the jacket's opening shows: at the shoulders it would come through the jacket in motion)
Vs, Fs = shell_mesh(BLOUSE, 126, 405, lambda X, Y, Z, U, V: 62 - np.abs(wrapdeg(U)) - np.clip((165 - Y) * 2.0, 0, 60),
                    nu=96, nv=40)
add('blouse', Vs, Fs, COL['blouse'], *weights_nearest(Vs, trunk))
blouse = H.Shell(BLOUSE)

# skirt: the drawing's shell; each point takes the weights of both legs' sides, blended across the width
# (its top a little narrower than drawn: it is under the jacket there and must not come through it in motion)
SKIRT_TOP = [(400, 80, -2, 46, -50, 2.4), (470, 108, 0, 56, -62, 2.4)] + SKIRT[2:]
Vk, Fk = shell_mesh(SKIRT_TOP, 420, 860, None, nu=96, nv=40)
side_l = (trunk | legs_all) & (X1[:, 0] > -2)
side_r = (trunk | legs_all) & (X1[:, 0] < 2)
wl = weights_nearest(Vk, side_l, k=32, sigma=30, top4=False)
wr = weights_nearest(Vk, side_r, k=32, sigma=30, top4=False)
a = np.clip((Vk[:, 0] + 40) / 80, 0, 1)
a = (a * a * (3 - 2 * a))[:, None]
add('skirt', Vk, Fk, COL['skirt'], *top_four(wl * a + wr * (1 - a)))
skirt = H.Shell(SKIRT)

# shoes: low pumps — an oval over each foot's toes and heel, the sole flat on the floor
for s, side in ((1, 'Left'), (-1, 'Right')):
    fm = (part(('L' if s > 0 else 'R') + 'foot') > 0.5) & used & (X1[:, 1] > FLOOR - 34)
    lo, hi = X1[fm].min(0), X1[fm].max(0)
    c = np.array([(lo[0] + hi[0]) / 2, FLOOR - 19, (lo[2] + hi[2]) / 2])
    Ve, Fe = M.ellipsoid(c, ((hi[0] - lo[0]) / 2 + 5, 20, (hi[2] - lo[2]) / 2 + 7), nu=36, nv=18)
    Ve[:, 1] = np.minimum(Ve[:, 1], FLOOR)
    footm = (part(('L' if s > 0 else 'R') + 'foot') > 0.5) & used
    add('shoe' + side, Ve, Fe, COL['shoe'], *weights_nearest(Ve, footm))
    print('shoe', side, (hi - lo).round(0))


def ribbon(shell, path, widths, lift, res=0.35):
    p = H.lock_part(shell, path, widths, lift=lift, res=res)
    P = np.stack([p.X, p.Y, p.Z], 1)
    m = int(max(8, max(widths) * 2 * res * 1.5))
    n = len(P) // m
    q = np.array([(i * m + j, (i + 1) * m + j, (i + 1) * m + j + 1, i * m + j + 1) for i in range(n - 1) for j in range(m - 1)])
    return P, q


# the blouse's high collar and the jacket's lapels (figures.vera_figure)
for s in (1, -1):
    P, q = ribbon(blouse, [(s * -2, 128), (s * -16, 132), (s * -30, 136)], [9, 11, 0], 3)
    add(f'bcol{s}', P, q, COL['blouse'], *weights_joint(P, 'Chest'), solidify=1.0)
    P, q = ribbon(jacket, [(s * -12, 142), (s * -24, 190), (s * -30, 250), (s * -26, 320)], [10, 20, 14, 0], 3)
    add(f'lapel{s}', P, q, COL['jacket'], *weights_nearest(P, trunk), solidify=1.0)

# buttons
jc = jacket.curve
for y in (360, 420):
    p = jc([(0, y)])[0] + [0, 0, 1.5]
    Ve, Fe = M.ellipsoid(p, (4.5, 4.5, 2.0), nu=16, nv=8)
    add(f'button{y}', Ve, Fe, '#1e2534', *weights_nearest(Ve, trunk), line=False)

# the folder: held in the left hand, flat against the thigh when the arm hangs (the drawing holds it at the hip)
_stand = os.path.join(C, 'stand.json')
if os.environ.get('FOLDER', '1') == '1' and os.path.exists(_stand) and 'hand' in json.load(open(_stand)):
    # where it is when she stands with the arms down (stand.mjs gives the hand's turn and shift in that pose):
    # upright, flat against the side of the skirt, the palm on it — and from there back to the rest pose
    Mh = np.array(json.load(open(_stand))['hand']).reshape(3, 4)       # engine axes, metres: rest → stand
    Rm, tm = Mh[:, :3], Mh[:, 3]
    hj = J1[IDX['LeftHand']]
    he = np.array([hj[0] * K, (FLOOR - hj[1]) * K, hj[2] * K])
    hs = Rm @ he + tm                                                  # the wrist in the stand, engine axes
    c = hs + np.array([-0.014, -0.135, 0.035])                         # inside the palm, lower, a little forward
    sz = np.array([0.012, 0.30, 0.215]) / 2                            # thickness (x), height (y), width (z)
    cube = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float) * sz
    tilt = np.radians(-8)                                              # leaning forward a little at the top
    Rt = np.array([[1, 0, 0], [0, np.cos(tilt), -np.sin(tilt)], [0, np.sin(tilt), np.cos(tilt)]])
    yw = np.radians(-32)                                               # its face turned a little to the front
    Ry = np.array([[np.cos(yw), 0, np.sin(yw)], [0, 1, 0], [-np.sin(yw), 0, np.cos(yw)]])
    Ps = cube @ (Ry @ Rt).T + c + np.array([0.012, 0, 0.02])
    Pe = (Ps - tm) @ Rm                                                # back to the rest pose (Rm is a turn)
    Vf = np.stack([Pe[:, 0] / K, FLOOR - Pe[:, 1] / K, Pe[:, 2] / K], 1)
    Ff = np.array([(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)])
    add('folder', Vf, Ff, COL['folder'], *weights_joint(Vf, 'LeftHand'), smooth=False)

# the seams the drawing has, as thin ink: the jacket's pockets and darts (the skirt's slit line is left out:
# between the two legs' turns it smears in a step)
LINES = []
for s in (1, -1):
    LINES.append((jc([(s * 30, 452), (s * 58, 450)]), 0.6, trunk))
    LINES.append((jc([(s * 40, 230), (s * 44, 330), (s * 40, 410)]), 0.55, trunk))
from scipy.interpolate import CubicSpline
for i, (P, w, mask) in enumerate(LINES):
    if len(P) > 2:
        P = CubicSpline(np.linspace(0, 1, len(P)), P)(np.linspace(0, 1, 24))
    else:
        P = P[0] + (P[1] - P[0]) * np.linspace(0, 1, 12)[:, None]
    if mask is None:                                   # on the skirt: move as the skirt's nearest points do
        _, j = cKDTree(Vk).query(P)
        sj, sw = OBJ[[o['name'] for o in OBJ].index('skirt')]['sj'][j], OBJ[[o['name'] for o in OBJ].index('skirt')]['sw'][j]
        sh = skirt
    else:
        sj, sw = weights_nearest(P, mask)
        sh = jacket
    zm = sh.sl(P[:, 1])[1]
    nrm = P - np.stack([0 * zm, P[:, 1], zm], 1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    Vt, Ft = M.tube(P + nrm * 1.8, w * 1.5, nseg=6)
    rep = np.repeat(np.arange(len(P)), 6)
    rep = np.r_[rep, [0, len(P) - 1]]
    add(f'seam{i}', Vt, Ft, INK, sj[rep], sw[rep], line=False)

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
for n in ('LeftArm', 'LeftForeArm', 'LeftHand', 'LeftLeg', 'LeftShin', 'LeftFoot', 'Hips'):
    print(n, J1[IDX[n]].round(1))
