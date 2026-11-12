"""Марат assembled: Anny's fitted man body (a barrel on short legs), the fitted base head with a broad nose and ears,
the cap of curls as balls on the skull, the beard lofted from the drawing's front and side outlines with curls along
its edge, the white jacket with rolled sleeves, the long apron (bib, straps, a skirt hung round the belly, a pocket),
the towel over the shoulder, trousers, big shoes — every part skinned on SOMA's 77 joints — one model pack (model.py)."""
import numpy as np
from common import CACHE, IX, NAMES, vertex_normals
from body import B, fit
from model import part, write, MATS
from meshcut import cut, loops, smooth, rim, neighbours
from hbm import tris
from drawing import K, extent, EAR_X, curve

NJ = len(NAMES)


def dense(sj, sw):
    D = np.zeros((len(sj), NJ))
    for k in range(4): np.add.at(D, (np.arange(len(sj)), sj[:, k]), sw[:, k])
    return D


def top4(D):
    j = np.argsort(-D, 1)[:, :4]; w = np.take_along_axis(D, j, 1)
    return j, w / np.maximum(w.sum(1, keepdims=True), 1e-9)


def split(p, g, mat2):
    """a part cut in two along g = 0: where g < 0 it keeps its paint, elsewhere it takes mat2 — so a paint changes on
    a clean line, never across a triangle"""
    A = np.c_[dense(p['sj'], p['sw']), p['fuv'], p['pat'], p['mat'], p.get('ex', np.zeros(len(p['V'])))]
    out = []
    for sgn, m in ((1, None), (-1, mat2)):
        v, t, a, _ = cut(p['V'], p['T'], sgn * g, A)
        if len(t) == 0: continue
        sj, sw = top4(a[:, :NJ])
        mm = np.rint(a[:, -2]).astype(int) if m is None else np.full(len(v), MATS.index(m))
        out.append(dict(V=v, T=t, sj=sj, sw=sw, mat=mm, fuv=a[:, NJ:NJ + 3], pat=a[:, NJ + 3:NJ + 6], ex=a[:, -1]))     # ex: one more number carried along
    return out


def one(n, joint): return np.tile([IX[joint], 0, 0, 0], (n, 1)), np.tile([1., 0, 0, 0], (n, 1))


def grid(nu, nv, wrap=True):
    """triangles of a grid of nv rings of nu points (ring after ring); wrap: each ring closed"""
    F = []
    for i in range(nv - 1):
        for j in range(nu if wrap else nu - 1):
            a, b = i * nu + j, i * nu + (j + 1) % nu
            F += [(a, b, a + nu), (b, b + nu, a + nu)]
    return np.array(F)


from scipy.spatial import cKDTree
from drawing import FRONT

# ---------------- the body ----------------
V, J = fit()
T = B['triangles']; P = B['parts'] / 255.; PN = B['partnames']
pw = lambda *names: sum(P[:, PN.index(n)] for n in names)
D = dense(B['sj'], B['sw'])
NB = vertex_normals(V, T)

# where the head sits: the drawing's head centre O; the chin (drawing y 102) 1.49 m up, the beard on the chest
CHIN_Y = 1.475
O = np.array([0.0, CHIN_Y + 102 * K, 0.05])
toW = lambda X: X + O                         # head frame → world
J2 = J.copy()
J2[IX['Head']] = O + [0, -84 * K, 6 * K]
J2[IX['HeadEnd']] = O + [0, 135 * K, 6 * K]
J2[IX['Jaw']] = O + [0, -60 * K, 40 * K]
J2[IX['LeftEye']] = O + [30 * K, -2 * K, 70 * K]; J2[IX['RightEye']] = O + [-30 * K, -2 * K, 70 * K]
J2[IX['Neck1']] = [0, 1.42, O[2] - 0.02]
J2[IX['Neck2']] = (J2[IX['Neck1']] + J2[IX['Head']]) / 2

# ---------------- the head ----------------
hs = np.load(f'{CACHE}/head_steps.npz')
HV, HQ = hs['warped'].copy(), hs['Q']; HT = tris(HQ)
# the ears stick out: each ear (found on the base) turned out about its front edge, a little larger
FB = hs['faired']
ew = np.clip((np.abs(FB[:, 0]) - 0.104) / 0.01, 0, 1) * ((FB[:, 1] > 0.66) & (FB[:, 1] < 0.80) & (FB[:, 2] > -0.045) & (FB[:, 2] < 0.035))
for sgn in (1, -1):
    m = (ew > 0) & (np.sign(HV[:, 0]) == sgn)
    c = (HV[m] * ew[m, None]).sum(0) / ew[m].sum(); zf = HV[m & (ew > 0.5), 2].max()
    w = ew[m, None]
    X = HV[m]; X = c + (X - c) * (1 + 0.1 * w)
    X[:, 0] += sgn * w[:, 0] * (0.004 + 0.4 * np.clip(zf - X[:, 2], 0, None))
    HV[m] = X
NECK_CUT = 1.40
HV, HT, EW, _ = cut(HV, HT, -(HV[:, 1] - (NECK_CUT - O[1])), ew[:, None]); EW = EW[:, 0]
yd, zd = -HV[:, 1] / K, HV[:, 2] / K
cm = ((yd > -20) & (yd < 110) & (zd > -30) & (EW < 0.01)).astype(float)
for _ in range(30):                       # (Taubin's two steps: the lumps go, the form doesn't shrink)
    HV = smooth(HV, HT, it=1, lam=0.5, mask=cm); HV = smooth(HV, HT, it=1, lam=-0.53, mask=cm)
HW = toW(HV)
HN = vertex_normals(HV, HT)


def head_skin(W):
    """the head on Head; its neck from Head down to Neck1"""
    y = W[:, 1]; yH, y2, y1 = J2[IX['Head'], 1], J2[IX['Neck2'], 1], J2[IX['Neck1'], 1]
    Dh = np.zeros((len(W), NJ))
    a = np.clip((y - y2) / (yH - y2), 0, 1); b = np.clip((y - y1) / (y2 - y1), 0, 1)
    Dh[:, IX['Head']] = a
    Dh[:, IX['Neck2']] = (1 - a) * b
    Dh[:, IX['Neck1']] = (1 - a) * (1 - b)
    return top4(Dh)


# the face picture's coordinates: the front projection in the drawing's head units, and how much the surface faces front
def fuv_of(X, N):
    u = (X[:, 0] / K + 160) / 320; v = (-X[:, 1] / K + 160) / 320
    return np.c_[u, v, np.clip(N[:, 2], 0, 1) * (X[:, 2] > 0)]


def units(X): return X[:, 0] / K, -X[:, 1] / K, X[:, 2] / K + EAR_X      # x, y (down), s (the side view's x)

# the hairline, in the drawing's units: along the side view from the forehead back over the ear to the nape, and
# across the forehead in the front view (under the row of curls)
HLS = [(-100, 40), (-70, 34), (-30, 8), (-18, -22), (-4, -46), (20, -64), (46, -72), (68, -70), (100, -70)]      # (s, y)
FRH = [(0, -84), (32, -78), (60, -62), (76, -40), (90, -20)]                                                       # (|x|, y)
def hair_f(X):
    """< 0 where the skull carries hair"""
    x, y, s = units(X)
    hl = np.interp(s, *zip(*HLS))
    return y - np.where(s > 20, np.minimum(hl, np.interp(np.abs(x), *zip(*FRH))), hl)
# the beard's upper edge in the front view: from the ears down the cheeks, under the mouth's corners
BT = [(0, 43), (16, 46), (42, 46), (68, 24), (84, -14), (100, -24)]                                               # (|x|, y)
def beard_f(X):
    """< 0 where there is beard"""
    x, y, s = units(X)
    top = np.maximum(np.interp(np.abs(x), *zip(*BT)), np.interp(s, [-46, -32, -20], [24, -14, -40]))      # behind the ear it drops to the nape
    return np.maximum(top - y, -46 - s)

parts = []
sj, sw = head_skin(HW)
head = part(HW, HT, sj, sw, 'skin', fuv=fuv_of(HV, HN), pat=HW); head['ex'] = EW * 100      # the ears stay skin
for p in split(head, -HV[:, 1] / K - 106, 'skin_d'):
    if p['mat'][0] != MATS.index('skin'): parts.append(p); continue
    # the skull under the curls and the jaw under the beard are painted as hair, so nothing pale shows between
    for q in split(p, -(hair_f(p['V'] - O) + 5 + p['ex']), 'hair'):
        parts += split(q, -(beard_f(q['V'] - O) + 8 + q['ex']), 'hair') if q['mat'][0] == MATS.index('skin') else [q]


def ball(c, r, nu=14, nv=9):
    th = np.linspace(0, np.pi, nv); ph = np.linspace(0, 2 * np.pi, nu, endpoint=False)
    X = np.array([[np.sin(t) * np.cos(p), np.cos(t), np.sin(t) * np.sin(p)] for t in th for p in ph]) * r + c
    return X, grid(nu, nv)[:, ::-1]

def balls(C, R):
    Xs, Ts, n = [], [], 0
    for c, r in zip(C, R):
        X, F = ball(np.asarray(c), r); Xs.append(X); Ts.append(F + n); n += len(X)
    return np.concatenate(Xs), np.concatenate(Ts)

# ---------------- the cap of curls: balls on the skull (the drawing's round dabs of the brush) ----------------
hx, hy, hsx = units(HV)
C, R = [], []
front = HV[:, 2] > 0
for x, y, r in [(-76, -52, 15), (-60, -80, 19), (-32, -98, 21), (0, -104, 22), (32, -98, 21), (60, -80, 19), (76, -52, 15)]:
    i = np.where(front)[0][np.hypot(hx[front] - x * 0.9, hy[front] - (y + 4)).argmin()]          # the forehead's row, from the front view
    C.append(HV[i] + HN[i] * r * K * 0.45); R.append(r * K)
cand = np.where((hair_f(HV) < -6) & (EW < 0.01))[0]
rng = np.random.default_rng(3)
for i in cand[np.argsort(HV[cand, 1] + rng.normal(0, 0.004, len(cand)))[::-1]]:              # from the top down
    r = (17 + 5 * np.clip((-hy[i] - 20) / 90, 0, 1)) * K
    c = HV[i] + HN[i] * r * 0.75
    if all(np.linalg.norm(c - c2) > 0.95 * (r + r2) * 0.62 for c2, r2 in zip(C, R)): C.append(c); R.append(r)
CX, CT = balls(C, R)
print('curls', len(C))
hfuv = fuv_of(CX, vertex_normals(CX, CT)); hfuv[:, 2] *= (-CX[:, 1] / K < -60)                # the dry strokes on the top only
sj, sw = one(len(CX), 'Head')
parts.append(part(toW(CX), CT, sj, sw, 'hair', fuv=hfuv, pat=toW(CX)))

# ---------------- the beard: one dark form from ear to ear, lofted from the drawing's outlines ----------------
BEARD_FRONT = [(0, -30), (83, -28), (84, 0), (88, 40), (80, 88), (48, 122), (0, 134), (-48, 122), (-80, 88), (-90, 40), (-88, 0), (-84, -28)]
BF = [(-30, 76), (48, 77), (54, 78), (72, 84), (102, 81), (128, 61), (133.5, 30)]            # (y, s): the front of it in the side view
BB = [(-30, -40), (4, -40), (50, -42), (96, -34), (124, -10), (133.5, 22)]                   # the back of it
nu, YS = 64, np.r_[np.linspace(-22, 110, 30), [116, 121, 125, 128, 130.5, 132.3, 133.3]]
ring = []
for y in YS:
    a = extent(BEARD_FRONT, y, +1); f = np.interp(y, *zip(*BF)); b = np.interp(y, *zip(*BB)); cs = np.interp(y, [-30, 100, 133.5], [18, 22, 26])
    for k in range(nu):
        ph = 2 * np.pi * k / nu; c, s_ = np.cos(ph), np.sin(ph)
        rz = (f - cs) if c > 0 else (cs - b)
        r = (abs(s_ / a) ** 2.2 + abs(c / rz) ** 2.2) ** (-1 / 2.2)
        ring.append((r * s_, y, cs + r * c))
Rg = np.array(ring)
BX = np.c_[Rg[:, 0], -Rg[:, 1], Rg[:, 2] - EAR_X] * K
BXT = grid(nu, len(Rg) // nu)
bot = len(BX); BX = np.r_[BX, [[0, -134 * K, (26 - EAR_X) * K]]]
n0 = (len(YS) - 1) * nu
BXT = np.r_[BXT, [(n0 + (k + 1) % nu, bot, n0 + k) for k in range(nu)]][:, ::-1]
bv, bt, _, edge = cut(BX, BXT, beard_f(BX))
L = max(loops(bt), key=len)
bn = vertex_normals(bv, bt)
bv2, bt2, _ = rim(bv, bt, L, -bn[L] * 7 * K)
# curls along its lower edge and over the jaw (the scalloped outline)
def on_loft(y, deg):
    a = extent(BEARD_FRONT, y, +1); f = np.interp(y, *zip(*BF)); b = np.interp(y, *zip(*BB)); cs = np.interp(y, [-30, 100, 133.5], [18, 22, 26])
    ph = np.radians(deg); c, s_ = np.cos(ph), np.sin(ph); rz = (f - cs) if c > 0 else (cs - b)
    r = (abs(s_ / a) ** 2.2 + abs(c / rz) ** 2.2) ** (-1 / 2.2) - 3
    return np.array([r * s_, -y, cs + r * c - EAR_X]) * K
BC = [on_loft(y, d) for y, ds in ((18, (-97, 97)), (42, (-95, 95)), (64, (-93, 93)), (86, (-112, -84, 84, 112)), (104, (-100, -64, -30, 30, 64, 100, 150, -150)), (118, (-80, -42, 0, 42, 80, 125, -125)), (128, (-45, 0, 45, 180)))
      for d in ds]
QX, QT = balls(BC, [14.5 * K] * len(BC))
bvA = np.r_[bv2, QX]; btA = np.r_[bt2, QT + len(bv2)]
sj, sw = one(len(bvA), 'Head')
bfuv = fuv_of(bvA, vertex_normals(bvA, btA))
bx_, by_, _ = units(bvA); bfuv[:, 2] *= ~((by_ < 52) & (np.abs(bx_) > 26))            # the cheeks' blush stays on the skin
parts.append(part(toW(bvA), btA, sj, sw, 'hair', fuv=bfuv, pat=toW(bvA)))

# ---------------- the broad nose: a wedge widening down to round wings ----------------
NY = np.r_[[-11.5], np.linspace(-9, 44, 16), [46.5]]
nw = np.interp(NY, [-11.5, -8, 20, 36, 44, 46.5], [1.5, 9, 20, 25, 15, 4])
nd = np.interp(NY, [-11.5, -4, 22, 36, 44, 46.5], [70, 75, 92, 96, 88, 74])
nn = 20; NXl = []
for y, w_, d in zip(NY, nw, nd):
    for k in range(nn):
        th = -np.pi / 2 + np.pi * k / (nn - 1)
        NXl.append((w_ * np.sin(th), -y, 58 + (d - 58) * np.cos(th) ** 0.8 - EAR_X))
NX = np.array(NXl) * K; NT = grid(nn, len(NY), wrap=False)[:, ::-1]
sj, sw = one(len(NX), 'Head')
parts.append(part(toW(NX), NT, sj, sw, 'nose', fuv=fuv_of(NX, np.tile([0, 0, 1.0], (len(NX), 1))), pat=toW(NX)))
np.savez(f'{CACHE}/build_head.npz', O=O)

# ---------------- clothes ----------------
def bone_t(X, a, b):
    A, Bb = J[IX[a]], J[IX[b]]; d = Bb - A
    return ((X - A) @ d) / (d @ d)

def shell(region_f, off, mat, smooth_it=3, free=0):
    """the body's surface where region_f < 0, pushed out along its normals by off (per vertex)"""
    A = np.c_[D, NB, off]
    v, t, a, on = cut(V, T, region_f, A)
    d, n, o = a[:, :NJ], a[:, NJ:NJ + 3], a[:, -1]
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    v = v + n * o[:, None]
    v = smooth(v, t, it=smooth_it, lam=0.3, fixed=np.where(on)[0])
    if free:                                              # the edge too: its line faired along itself
        for L in loops(t):
            L = np.array(L)
            for _ in range(free): v[L] = 0.5 * v[L] + 0.25 * (v[np.roll(L, 1)] + v[np.roll(L, -1)])
        v = smooth(v, t, it=2, lam=0.3, fixed=np.unique(np.concatenate([np.array(L) for L in loops(t)])))
    sj, sw = top4(d)
    return part(v, t, sj, sw, mat)

y = V[:, 1]
WAIST, COLL, JHEM, AHEM = 1.085, 1.47, 0.60, 0.32
ua = np.where(V[:, 0] > 0, bone_t(V, 'LeftArm', 'LeftForeArm'), bone_t(V, 'RightArm', 'RightForeArm'))     # along the upper arm
fa = np.where(V[:, 0] > 0, bone_t(V, 'LeftForeArm', 'LeftHand'), bone_t(V, 'RightForeArm', 'RightHand'))   # along the forearm
arm = pw('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand')
armside = arm > 0.5
legs = pw('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot')
NZ = np.array([0, 0, J2[IX['Neck1'], 2] + 0.02])

def to_neck(p, y0, rt, pw_=1.5):
    """above y0 a shell is drawn in round the neck"""
    sv = p['V']; rr = np.hypot(sv[:, 0], sv[:, 2] - NZ[2])
    sg = np.clip((sv[:, 1] - y0) / (COLL - y0), 0, 1) ** pw_
    k = np.where(rr > rt, (rr + (rt - rr) * sg) / rr, 1.0)
    sv[:, 0] *= k; sv[:, 2] = NZ[2] + (sv[:, 2] - NZ[2]) * k
    return p

# the white jacket: the trunk down over the hips, sleeves rolled up above the elbows; a stand-up collar, cuffs
f_jac = np.maximum.reduce([np.where(legs > 0.5, 1.0, JHEM - y), y - COLL, np.where(armside, ua - 0.86, -1.0)])
jac = to_neck(shell(f_jac, np.full(len(V), 0.012) + 0.006 * np.clip(ua, 0, 1) * armside, 'white', smooth_it=12, free=3), 1.38, rt=0.095)
jv = jac['V'].copy(); jd = dense(jac['sj'], jac['sw'])
jua = np.where(jv[:, 0] > 0, bone_t(jv, 'LeftArm', 'LeftForeArm'), bone_t(jv, 'RightArm', 'RightForeArm'))
jarm = sum(jd[:, IX[n]] for n in NAMES if 'Arm' in n or 'Hand' in n) > 0.5
for p in split(jac, np.where(jarm, jua - 0.74, -1.0), 'white_d'):                 # the rolled cuffs
    if p['mat'][0] != MATS.index('white'): parts.append(p); continue
    # the apron's straps, painted on the jacket: from the bib's corners up to the collar
    px, py, pz = p['V'].T
    xs = 0.128 - 0.03 * np.clip((py - 1.35) / 0.1, 0, 1)
    for q in split(p, -np.maximum.reduce([np.abs(np.abs(px) - xs) - 0.013, 1.33 - py, -(pz - (NZ[2] - 0.02))]), 'apron'):
        if q['mat'][0] == MATS.index('apron'): q['V'] = q['V'] + vertex_normals(q['V'], q['T']) * 0.005       # a little proud of the jacket
        parts.append(q)
# the stand-up collar: a low ring round the neck, right under the beard
cn, CYs = 48, (1.395, 1.405, 1.425, 1.446, 1.452, 1.446)
CR = (0.122, 0.118, 0.112, 0.108, 0.102, 0.094)
CXc = np.array([(r * np.sin(2 * np.pi * k / cn), yy - 0.016 * max(np.cos(2 * np.pi * k / cn), 0) ** 2, NZ[2] + 0.01 + r * 0.92 * np.cos(2 * np.pi * k / cn))
                for yy, r in zip(CYs, CR) for k in range(cn)])          # it dips in front, as drawn
Dc = np.zeros((len(CXc), NJ)); Dc[:, IX['Chest']] = 0.6; Dc[:, IX['Neck1']] = 0.4
sj, sw = top4(Dc)
parts.append(part(CXc, grid(cn, len(CYs))[:, ::-1], sj, sw, 'white_d'))
# trousers and big shoes
f_tr = np.maximum(y - (JHEM + 0.03), 0.07 - y)
f_tr = np.where((legs > 0.3) | (pw('pelvis') > 0.3), f_tr, 1.0)
parts.append(shell(f_tr, np.full(len(V), 0.012), 'trous', smooth_it=10, free=2))

def shoe(side):
    F_, T_ = J[IX[side + 'Foot']], J[IX[side + 'ToeEnd']]
    ax = np.array([T_[0] - F_[0], 0, T_[2] - F_[2]]); L_ = np.linalg.norm(ax); ax /= L_
    heel = np.array([F_[0], 0, F_[2]]) - ax * 0.06; Ltot = L_ + 0.06 + 0.03
    side_v = np.cross([0, 1, 0], ax)
    nu_, nv_ = 28, 24; X = []
    for i in range(nu_):
        t = i / (nu_ - 1)
        c = heel + ax * Ltot * t
        w = 0.05 + 0.014 * np.sin(np.pi * min(t / 0.75, 1) / 2)
        hgt = np.interp(t, [0, 0.3, 0.55, 0.85, 1], [0.105, 0.11, 0.085, 0.07, 0.055])
        cap = np.clip(np.sin(np.pi * t) ** 0.3, 0.05, 1)
        for j in range(nv_):
            a = 2 * np.pi * j / nv_
            sx, sy = np.cos(a), np.sin(a)
            r = (abs(sx) ** 2.6 + abs(sy) ** 2.6) ** (-1 / 2.6)
            X.append(c + side_v * sx * r * w * cap + np.array([0, max((sy * r * 0.5 + 0.5) * hgt * (0.35 + 0.65 * cap) - 0.002, 0), 0]))
    X = np.array(X); Fc = [tuple(q) for q in grid(nv_, nu_)]
    for end, rev in ((0, True), (nu_ - 1, False)):
        ci = len(X); X = np.r_[X, X[end * nv_:(end + 1) * nv_].mean(0)[None]]
        for j in range(nv_):
            tri = (end * nv_ + j, end * nv_ + (j + 1) % nv_, ci)
            Fc.append(tri[::-1] if rev else tri)
    tt = ((X - heel) @ ax) / Ltot
    Dd = np.zeros((len(X), NJ)); wt = np.clip((tt - 0.55) / 0.2, 0, 1)
    Dd[:, IX[side + 'Foot']] = 1 - wt; Dd[:, IX[side + 'ToeBase']] = wt
    sj, sw = top4(Dd)
    return part(X, np.array(Fc), sj, sw, 'shoe')
for sd in ('Left', 'Right'): parts.append(shoe(sd))

# the apron: its cloth is measured off the jacket — how far the jacket reaches from the trunk's axis at each height and
# angle — and hangs straight from the belly's widest round; a bib up the chest, a pocket, straps over the shoulders
ZC = 0.07
trunk = ~jarm
jr = np.hypot(jv[trunk, 0], jv[trunk, 2] - ZC); jph = np.arctan2(jv[trunk, 0], jv[trunk, 2] - ZC); jy = jv[trunk, 1]
SPAN, na, BIB = np.radians(104), 97, 1.35
ys = np.r_[np.linspace(BIB, 0.66, 40), np.linspace(0.64, AHEM, 14)]; phs = np.linspace(-SPAN, SPAN, na)
Rg = np.zeros((len(ys), na))
for i, yy in enumerate(ys):
    m = np.abs(jy - max(yy, 0.68)) < 0.035
    for k, ph in enumerate(phs):
        d = np.abs((jph[m] - ph + np.pi) % (2 * np.pi) - np.pi); mm = d < 0.14
        Rg[i, k] = jr[m][mm].max() if mm.any() else np.nan
for i in range(len(ys)):                                      # fill, then smooth
    bad = np.isnan(Rg[i]); Rg[i, bad] = np.interp(phs[bad], phs[~bad], Rg[i, ~bad])
for _ in range(6): Rg[:, 1:-1] = (Rg[:, :-2] + 2 * Rg[:, 1:-1] + Rg[:, 2:]) / 4; Rg[1:-1] = (Rg[:-2] + 2 * Rg[1:-1] + Rg[2:]) / 4
iw = np.argmin(np.abs(ys - 0.80))
for i in range(len(ys)):
    if ys[i] < 0.80: Rg[i] = Rg[iw] * (1 - (0.2 + 0.16 * (np.abs(phs) / SPAN) ** 2) * ((0.80 - ys[i]) / (0.80 - AHEM)) ** 1.3)       # it falls in a little towards the knees, more at its edges
Rg += 0.014 + 0.036 * np.clip((ys - WAIST) / 0.2, 0, 1)[:, None]         # the bib stands a little off the chest
AX = np.array([(Rg[i, k] * np.sin(ph), yy, ZC + Rg[i, k] * np.cos(ph)) for i, yy in enumerate(ys) for k, ph in enumerate(phs)])
AT = grid(na, len(ys), wrap=False)[:, ::-1]
aph = np.arctan2(AX[:, 0], AX[:, 2] - ZC)
# skinned as the jacket under it; below the hips it hangs from them and each side follows its thigh a little
tree = cKDTree(jv[trunk]); _, nn_ = tree.query(AX, k=4)
Da = jd[trunk][nn_].mean(1)
tl = np.clip((0.72 - AX[:, 1]) / (0.72 - AHEM), 0, 1)
sidew = 0.5 + 0.5 * np.clip(AX[:, 0] / 0.12, -1, 1)
Dh = np.zeros_like(Da); Dh[:, IX['LeftLeg']] = 0.45 * tl * sidew; Dh[:, IX['RightLeg']] = 0.45 * tl * (1 - sidew); Dh[:, IX['Hips']] = 1 - 0.45 * tl
lw = np.clip((0.78 - AX[:, 1]) / 0.12, 0, 1)[:, None]
sj, sw = top4(Da * (1 - lw) + Dh * lw)
apron = part(AX, AT, sj, sw, 'apron')
ap = []
for p in split(apron, np.where(AX[:, 1] > WAIST + 0.006, np.abs(AX[:, 0]) - 0.15, -1.0), 'clay'):     # the bib: only the middle goes up
    if p['mat'][0] == MATS.index('apron'): ap.append(p)
for p in ap:
    ph_ = np.arctan2(p['V'][:, 0], p['V'][:, 2] - ZC); yy = p['V'][:, 1]
    for q in split(p, -np.maximum(np.abs(ph_ - np.radians(34)) - np.radians(17), np.abs(yy - 0.80) - 0.095), 'apron_d'):      # the pocket
        parts += split(q, 0.011 - np.abs(q['V'][:, 1] - (WAIST - 0.005)), 'apron_d') if q['mat'][0] == MATS.index('apron') else [q]      # the tie
# the tie goes on round the back, over the jacket: a band at the same measure
tn = 60; tph = np.linspace(SPAN - 0.06, 2 * np.pi - SPAN + 0.06, tn)
mrow = np.abs(jy - WAIST) < 0.04
tr_ = np.array([jr[mrow][np.abs((jph[mrow] - ph + np.pi) % (2 * np.pi) - np.pi) < 0.16].max() for ph in tph]) + 0.008
for _ in range(4): tr_[1:-1] = (tr_[:-2] + 2 * tr_[1:-1] + tr_[2:]) / 4
TX = np.array([(r * np.sin(ph), WAIST - 0.004 + dy, ZC + r * np.cos(ph)) for dy in (0.014, 0, -0.014) for r, ph in zip(tr_ + np.array([[0], [0.004], [0]]).repeat(tn, 1)[0] * 0, tph)])
TX[tn:2 * tn, [0, 2]] = np.c_[(tr_ + 0.004) * np.sin(tph), ZC + (tr_ + 0.004) * np.cos(tph)]
_, nn_ = tree.query(TX, k=4)
sj, sw = top4(jd[trunk][nn_].mean(1))
parts.append(part(TX, grid(tn, 3, wrap=False), sj, sw, 'apron_d'))
# the towel over his right shoulder: cream, terracotta stripes
f_tow = np.maximum.reduce([np.abs(V[:, 0] + 0.185) - 0.042, np.where(V[:, 2] > NZ[2], 1.2 - y, 1.24 - y), np.where(arm > 0.75, 1.0, -1.0)])
tow = shell(f_tow, np.full(len(V), 0.026), 'towel', smooth_it=30, free=4)
tv = tow['V']; tow['pat'] = np.c_[tv[:, 0], tv[:, 1] + 0.04 * tv[:, 0], tv[:, 2]]
parts.append(tow)

# the skin left showing: the forearms and the big hands
v, t, a, _ = cut(V, T, np.where(armside, 0.62 - ua, 1.0), D)
sj, sw = top4(a)
parts.append(part(v, t, sj, sw, 'skin'))

write('marat', parts, J2, B['frames'], extra=dict(stripes=dict(mat='towel', period=0.14, width=0.12, y0=1.225), face=320,
                                                 corrections=dict(armsOff=dict(degrees=16), armsOutOfHead=dict(margin=0.03))))
