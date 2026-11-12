"""Марат (С13, the woodblock print) in 3D: the pack the print renderer (web/print.js, web/kit.js, web/char.js) takes.
  python3 build.py            → ../data/marat.json, marat.bin
From Р36's build (to3d/r36-s12-marat: the same man in another style), with the С13 drawing's numbers: here he is
eight heads tall, long-legged, so less far from Anny's man than there.
Bases: Anny's man (engine/data/bodies/moood-man: the forearms and hands, the feet and the SOMA skeleton with its
weights), re-proportioned to the drawing — a barrel of a trunk, heavy shoulders, thick limbs, legs apart; Blender's
Human Base Meshes stylised head (CC0), fitted to parts.head_pts front and profile (head.py); the cook's jacket, its
rolled sleeves, the trousers, the apron with its bib and straps and the towel are shells of the drawing's sizes
(shells.py); the hair is a dome over the skull with round bumps (the drawing's scalloped edge of curls as form), the
beard a smooth cup round the jaw and over the mouth, open under the nose.
What the print renderer needs instead of a material: grp (the colour block), edges, inner (where a part's silhouette
over itself is a line: 0 no, 1 yes, 2 thin), the face grid, strokes and marks (the apron's folds, the jacket's collar
and flap, buttons, curls)."""
import os, sys
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M, head as Hd, drawing as D, shells as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data')
HBM = '/home/user/cache/to3d-r38-s13-marat/hbm_head.npz'      # tools/hbm_export.py's arrays
os.makedirs(OUT, exist_ok=True)
K = D.K
y3 = lambda yd: (D.FLOOR - np.asarray(yd, float)) * K
ydr = lambda y: D.FLOOR - np.asarray(y, float) / K
u = lambda v: np.asarray(v, float) * K
smooth = S.smooth
rng = np.random.default_rng(38)

# ---------------------------------------------------------------- skeleton and Anny's man
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body('moood-man')
P0 = a['positions'].reshape(-1, 3).astype(float); J0 = a['joints'].reshape(-1, 3).astype(float)
FR = a['frames'].reshape(-1, 4).astype(np.float32)
TRI0 = t['triangles'].reshape(-1, 3).astype(np.int64)
SJ0 = t['skinJoints'].reshape(-1, 4).astype(np.int64); SW0 = t['skinWeights'].reshape(-1, 4).astype(float)
dz = -J0[I['Hips'], 2]; P0[:, 2] += dz; J0[:, 2] += dz


def under(j):
    out, st = [], [j]
    while st:
        k = st.pop(); out.append(k); st += list(np.where(PARENT == k)[0])
    return out


# the drawing's joints: long thick legs standing apart, a long barrel of a trunk, heavy shoulders, a short neck
J1 = J0.copy()
HIP = 0.90; TR = (y3(150) - HIP) / (J0[I['Neck1'], 1] - J0[I['Hips'], 1])
J1[I['Hips']] = [0, HIP, 0]
for n in ['Spine1', 'Spine2', 'Chest']: J1[I[n]] = [0, HIP + TR * (J0[I[n], 1] - J0[I['Hips'], 1]), J0[I[n], 2]]
J1[I['Neck1']] = [0, y3(150), 0.0]
J1[I['Neck2']] = [0, y3(122), 0.006]
J1[I['Head']] = [0, y3(94), 0.01]
J1[I['HeadEnd']] = [0, y3(-100), 0.0]
J1[I['Jaw']] = [0, y3(34), -0.03]          # where the jaw turns, under the ear
for s, sg in (('Left', 1), ('Right', -1)):
    J1[I[s + 'Eye']] = [sg * u(33), y3(0), u(70)]
    J1[I[s + 'Shoulder']] = [sg * 0.03, y3(176), 0.03]
    J1[I[s + 'Arm']] = [sg * 0.212, y3(238), 0.0]
    for n, k in (('ForeArm', 1.0), ('Hand', 0.95)):
        j = I[s + n]; J1[j] = J1[PARENT[j]] + k * (J0[j] - J0[PARENT[j]])
    for j in under(I[s + 'Hand'])[1:]:
        J1[j] = J1[PARENT[j]] + 1.2 * (J0[j] - J0[PARENT[j]])
    J1[I[s + 'Leg']] = [sg * 0.105, 0.84, 0.0]
    J1[I[s + 'Shin']] = [sg * 0.125, 0.44, 0.004]
    J1[I[s + 'Foot']] = [sg * 0.135, 0.09, -0.012]
    for n in ('ToeBase', 'ToeEnd'):
        j = I[s + n]; J1[j] = J1[PARENT[j]] + (J0[j] - J0[PARENT[j]]) * [0.0, 1.1, 1.05]


def rot_between(a_, b_):
    a_ = a_ / np.linalg.norm(a_); b_ = b_ / np.linalg.norm(b_)
    v = np.cross(a_, b_); c = a_ @ b_; s = np.linalg.norm(v)
    if s < 1e-9: return np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * ((1 - c) / s ** 2)


RADIAL = {'Leg': 1.3, 'Shin': 1.35, 'Arm': 1.45, 'ForeArm': 1.6}


def joint_affine(j):
    """Joint j's move of the rest: x ↦ J1_j + A (x − J0_j). A limb's bone turns and stretches to the new joints and is
    made thicker across; feet and hands are scaled; the trunk is a barrel."""
    n = NAMES[j]
    for key, r in RADIAL.items():
        if n.endswith(key) and n[:-len(key)] in ('Left', 'Right'):
            c = [k for k in range(NJ) if PARENT[k] == j][0]
            d0 = J0[c] - J0[j]; d1 = J1[c] - J1[j]
            ln = np.linalg.norm(d1) / np.linalg.norm(d0); d0 /= np.linalg.norm(d0)
            return rot_between(d0, d1) @ (r * np.eye(3) + (ln - r) * np.outer(d0, d0))
    if 'Foot' in n or 'Toe' in n: return np.diag([1.3, 1.15, 1.05])
    if 'Hand' in n: return 1.2 * np.eye(3)
    if n in ('Hips', 'Spine1', 'Spine2', 'Chest') or 'Shoulder' in n: return np.diag([1.6, TR, 2.0])
    return np.eye(3)


AFF = [joint_affine(j) for j in range(NJ)]


def deform(P, SJ, SW):
    out = np.zeros_like(P)
    for k in range(4):
        for j in np.unique(SJ[:, k]):
            m = (SJ[:, k] == j) & (SW[:, k] > 0)
            out[m] += SW[m, k, None] * (J1[j] + (P[m] - J0[j]) @ AFF[j].T)
    return out


PF = deform(P0, SJ0, SW0)          # the whole body, fitted (the shells take their weights from it)
WT = S.Weights(PF, SJ0, SW0, NJ)
dom = SJ0[np.arange(len(SJ0)), SW0.argmax(1)]
dn = np.array([NAMES[j] for j in dom])
fore = np.array([n.endswith('ForeArm') for n in dn])
feet = np.array([('Foot' in n or 'Toe' in n) for n in dn]) | (np.array([n.endswith('Shin') for n in dn]) & (PF[:, 1] < 0.14))
hand = np.array(['Hand' in n for n in dn])
keep = fore | hand | feet           # of Anny's body the drawing shows the bare forearms and hands; the feet make the clogs
tk = keep[TRI0].all(1)
bi = np.where(keep)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
B = dict(V=PF[bi], T=remap[TRI0[tk]])
nb = len(bi)
isfoot = feet[bi]
Ab = M.adjacency(nb, [list(t_) for t_ in B['T']])
B['V'] = M.smooth(B['V'], Ab, isfoot, iters=220, lam=0.5)       # a clog: the foot as one rounded form
nrm = M.vertex_normals(B['V'], B['T'])
B['V'][isfoot] += nrm[isfoot] * 0.022
lo = B['V'][isfoot, 1].min(); B['V'][isfoot, 1] = np.maximum(B['V'][isfoot, 1] - lo, 0.0) * 1.0
BW = np.zeros((nb, NJ))
for q in range(4): np.add.at(BW, (np.arange(nb), SJ0[bi][:, q]), SW0[bi][:, q])
B['W'] = BW
B['grp'] = np.where(isfoot, 6, 1)

# ---------------------------------------------------------------- the head
hv, hP, eL, eR = Hd.load(HBM)
earm = Hd.ears(hv)
hv2, = Hd.fit(hv, earm, ear=(u(82), np.array([0.5, 0.62, 0.62])))
ec = hv2[earm].mean(0)
hv2[earm] += [0, y3(8) - ec[1], u(-34) - ec[2]]          # the ears: parts.ear ×1.2 — profile x 14…42, y −22…38
V0 = Hd.flatten(hv2, D.REG, front_min=0.02)
# the nose: the base's laid flat, and the drawing's broad round one put on: its profile head_side's, its width
# head_front's (the wings ±22)
V0 = Hd.flatten(V0, [(0, 16, 24, 28)], front_min=0.02)
_xd, _yd = V0[:, 0] / K, ydr(V0[:, 1])
_m = (V0[:, 2] > 0.02) & (np.abs(_xd) < 34) & (_yd > -24) & (_yd < 46)
_pick = lambda yy: V0[np.argmin(np.where(_m, np.abs(_xd) + np.abs(_yd - yy), 1e9)), 2]
_plane = lambda y: np.interp(y, [-20, 42], [_pick(-20), _pick(42)])
_h = np.clip(np.interp(_yd, D.NOSE[:, 0], D.NOSE[:, 1], left=np.nan, right=np.nan) * K - _plane(_yd), 0, None)
_w = np.interp(_yd, [-18, 0, 14, 27, 34, 38], [7, 9, 13, 18, 18, 12])
_t = np.clip(np.abs(_xd) / _w, 0, 1)
_prof = (1 - _t ** 2) ** 0.75
V0[:, 2] = np.where(_m & ~np.isnan(_h), np.maximum(V0[:, 2], _plane(_yd) + np.nan_to_num(_h) * _prof), V0[:, 2])
nh = len(V0)
HT = M.triangulate(hP)
xd, yd = V0[:, 0] / K, ydr(V0[:, 1])
yde = yd - 16 * smooth(V0[:, 2] / 0.04)
SW = np.zeros((nh, NJ))
sA = smooth((yde - 92) / 30); sB = smooth((yde - 118) / 24); sC = smooth((yde - 140) / 22)
SW[:, I['Head']] = 1 - sA
SW[:, I['Neck2']] = sA * (1 - sB)
SW[:, I['Neck1']] = sA * sB * (1 - sC)
SW[:, I['Chest']] = sA * sB * sC
# the lower face on the jaw: it drops when he laughs
jaw_w = lambda X: smooth((ydr(X[:, 1]) - 62) / 16) * smooth((X[:, 2] - u(-20)) / u(40)) * (1 - smooth((ydr(X[:, 1]) - 116) / 16))
wj = jaw_w(V0); SW *= (1 - wj)[:, None]; SW[:, I['Jaw']] += wj
Hh = dict(V=V0, T=HT, W=SW)
used = np.zeros(nh, bool); used[np.unique(HT)] = True
hn = M.vertex_normals(V0, HT)
htree = cKDTree(V0[used]); hV, hN = V0[used], hn[used]


def off_head(V, d, iters=3):
    """Points kept at least d outside the head."""
    V = V.copy()
    for _ in range(iters):
        dd, ii = htree.query(V)
        s_ = ((V - hV[ii]) * hN[ii]).sum(1)
        m = s_ < d
        V[m] += hN[ii[m]] * (d - s_[m])[:, None]
    return V


# ---------------------------------------------------------------- the jacket, sleeves, trousers, fists
def rows_of(spec, step=6.0):
    spec = np.array(spec, float); ys = np.arange(spec[0, 0], spec[-1, 0] + 1e-6, step)
    ys = np.unique(np.r_[ys, spec[-1, 0]])
    f = lambda k: np.interp(ys, spec[:, 0], spec[:, k])
    a_, zf, zb = f(1), f(2), f(3)
    for _ in range(3):
        for arr in (a_, zf, zb):                     # rounded between the given heights
            arr[1:-1] = (arr[:-2] + 2 * arr[1:-1] + arr[2:]) / 4
    return [(y3(yy), u(aa), u((f_ + b_) / 2), u((f_ - b_) / 2), u((f_ - b_) / 2)) for yy, aa, f_, b_ in zip(ys, a_, zf, zb)]


# (drawing height, half-width, front, back): a stand-up collar round the thick neck, heavy round shoulders, the chest
# and the belly one barrel leading in front, widest below the waist, the hem under the apron
JSPEC = [(110, 70, 56, -70), (124, 100, 66, -84), (148, 150, 80, -96), (190, 186, 98, -106), (300, 200, 152, -114),
         (500, 214, 198, -122), (640, 216, 202, -126), (740, 200, 172, -122), (788, 182, 150, -116)]
jrows = rows_of(JSPEC, 8.0)
JC = 80
JV, JT = S.loft(jrows, JC, True); JT = S.outward(JV, JT)
Jk = dict(V=JV, T=JT, W=WT.smooth(WT.transfer(JV, 8), JT, 20))
jfront = lambda x, yd_: S.ring_z(S.row_at(jrows, float(y3(yd_))), x)          # the jacket's front at (x metres, height)

SL, HANDS, TRS = [], [], []
for s, sg in (('Left', 1), ('Right', -1)):
    A_, E_, W_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']], J1[I[s + 'Hand']]
    d1 = (E_ - A_) / np.linalg.norm(E_ - A_)
    # the sleeve rolled up to the elbow: a thick tube, the roll a fuller ring at its end
    path = np.array([A_ + (E_ - A_) * t_ for t_ in np.linspace(0.0, 0.93, 13)])
    radii = np.interp(np.linspace(0, 1, 13), [0, 0.15, 0.6, 0.86, 0.9, 1.0], [0.058, 0.070, 0.066, 0.062, 0.069, 0.069])
    V_, T_ = S.tube(path, radii, 26)
    arm = set(under(I[s + 'Shoulder'])); tr = np.array([j in arm for j in range(NJ)])
    SL.append(dict(V=V_, T=T_, W=WT.limb(V_, T_, tr, A_, 0.12), side=s))
    L_, S_, F_ = J1[I[s + 'Leg']], J1[I[s + 'Shin']], J1[I[s + 'Foot']]
    path = S.catmull([L_ + [0, 0.02, 0], (L_ + S_) / 2, S_, (S_ + F_) / 2, F_ + [0, -0.035, 0.004]], 6)
    Ln = np.linspace(0, 1, len(path))
    V_, T_ = S.tube(path, np.interp(Ln, [0, 0.5, 1], [0.104, 0.082, 0.066]), 26)
    leg = set(under(I[s + 'Leg'])); tr = np.array([j in leg for j in range(NJ)])
    Wl = WT.transfer(V_); Wl = Wl * tr; Wl /= Wl.sum(1, keepdims=True) + 1e-9
    bad = Wl.sum(1) < 0.5; Wl[bad] = 0; Wl[bad, I[s + 'Leg']] = 1
    TRS.append(dict(V=V_, T=T_, W=WT.smooth(Wl, T_, 6), side=s))

# ---------------------------------------------------------------- the apron: a bib, a skirt to the shins, two straps
OFF = 0.012
P_ = 2.3
def apron_row(yd_):
    r = S.row_at(jrows, float(y3(min(yd_, 770))))
    k = 1.0 if yd_ <= 770 else 1 - 0.12 * (yd_ - 770) / 440         # below the jacket's hem it hangs a little in
    return (float(y3(yd_)), (r[1] + OFF) * k, r[2], (r[3] + OFF) * k, r[4] + OFF)
BIBW = 100
BIB0, WAIST, AHEM = 316.0, 552.0, 1208.0
bib_y = np.r_[np.arange(BIB0, WAIST, 8.0), WAIST]
brow = [apron_row(v) for v in bib_y]
# (the bib widens from its top to the skirt's width at the waist, as the drawing's apron is one piece)
bgap = [np.pi - (t0_ + (np.radians(114) - t0_) * ((v - BIB0) / (WAIST - BIB0)) ** 1.6) for v, r in zip(bib_y, brow) for t0_ in [np.arcsin(min(1, (u(BIBW) / r[1]) ** (P_ / 2)))]]
BV, BT = S.loft(brow, 40, False, bgap, back=True); BT = S.outward(BV, BT) if False else BT
sk_y = np.r_[np.arange(WAIST, AHEM, 8.0), AHEM]
srow = [apron_row(v) for v in sk_y]
AC = 64
AV, AT = S.loft(srow, AC, False, [np.radians(66)] * len(srow), back=True)
for V_, T_ in ((BV, BT), (AV, AT)):
    pass
fix = lambda V_, T_: T_ if (M.vertex_normals(V_, T_) * (V_ - [0, 0, 0]) * [1, 0, 1]).sum(1).mean() > 0 else T_[:, ::-1]
BT = fix(BV, BT); AT = fix(AV, AT)
Wa = WT.transfer(AV, 8)
ayd = ydr(AV[:, 1]); Lw = 0.5 * smooth((ayd - 760) / 300)
side_ = 1 / (1 + np.exp(-AV[:, 0] / 0.06))
Wr = np.zeros_like(Wa); Wr[:, I['LeftLeg']] = Lw * side_; Wr[:, I['RightLeg']] = Lw * (1 - side_); Wr[:, I['Hips']] = 1 - Lw
uu = smooth((ayd - 700) / 120)[:, None]
Ap = dict(V=AV, T=AT, W=WT.smooth((1 - uu) * Wa + uu * Wr, AT, 12))
Bb = dict(V=BV, T=BT, W=WT.smooth(WT.transfer(BV, 8), BT, 12))
STRAPS = []
for sg in (1, -1):
    ts = np.linspace(0, 1, 14)
    xs = sg * u(np.interp(ts, [0, 1], [BIBW - 9, 66])); yds = np.interp(ts, [0, 1], [BIB0 + 2, 118])
    pts = np.array([[x_, float(y3(v)), jfront(x_, v)] for x_, v in zip(xs, yds)])
    cen = np.array([[0, p_[1], S.row_at(jrows, p_[1])[2]] for p_ in pts])
    nr = pts - cen; nr /= np.linalg.norm(nr, axis=1, keepdims=True)
    V_, T_ = S.strip(pts, nr, u(9), OFF + 0.004)
    STRAPS.append(dict(V=V_, T=T_, W=WT.transfer(V_, 8)))
# the towel over his left shoulder: down the front to the bib's height, a little down the back; two stripes at its end
tw_f = [(142, v) for v in np.linspace(350, 150, 12)]
x_t = u(142)
tp = [[x_t, float(y3(v)), jfront(x_t, v)] for _, v in tw_f]
rtop = S.row_at(jrows, float(y3(150)))
zb_ = lambda v: (lambda r: r[2] - r[4] * np.sqrt(1 - min(1, x_t / r[1]) ** P_) ** (2 / P_))(S.row_at(jrows, float(y3(v))))
tp += [[x_t, float(y3(141)), (tp[-1][2] + zb_(150)) / 2 + 0.01]] + [[x_t, float(y3(v)), zb_(v)] for v in np.linspace(152, 236, 6)]
tp = np.array(tp); cen = np.array([[0, p_[1] - 0.05, S.row_at(jrows, p_[1])[2]] for p_ in tp])
nr = tp - cen; nr[:, 0] *= 0.3; nr /= np.linalg.norm(nr, axis=1, keepdims=True)
TV, TT = S.strip(tp, nr, u(30), OFF + 0.008)
tl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(tp, axis=0), axis=1))]; tl /= tl[-1]
Tw = dict(V=TV, T=TT, W=WT.transfer(TV, 8), stripe=np.repeat(tl, 4))

# ---------------------------------------------------------------- the hair: a dome over the skull, with round curls
skull = V0[used & ~earm]
CEN = np.array([0, y3(-20), u(-8)])
sd = skull - CEN; sr = np.linalg.norm(sd, axis=1); sdir = sd / sr[:, None]
stree = cKDTree(sdir)


def skull_r(dirs):
    dd, ii = stree.query(dirs, 8)
    w = 1 / (dd + 0.03) ** 2
    return (sr[ii] * w).sum(1) / w.sum(1)


def bumps(Pts, Nrm, n, rad, hgt, keep_from=None):
    """Round curls on a surface: seeds spread over it, each a dome of its own size; returns the rise along the normal."""
    seeds = []
    order = rng.permutation(len(Pts))
    for i in order:
        if keep_from is not None and not keep_from[i]: continue
        if all(np.linalg.norm(Pts[i] - Pts[j]) > rad[0] * 1.85 for j in seeds): seeds.append(i)
        if len(seeds) >= n: break
    seeds = np.array(seeds); r_ = rng.uniform(rad[0], rad[1], len(seeds)); h_ = rng.uniform(hgt[0], hgt[1], len(seeds))
    dist = np.linalg.norm(Pts[:, None, :] - Pts[seeds][None, :, :], axis=2) / r_[None, :]
    dome = np.sqrt(np.clip(1 - dist ** 2, 0, None)) * h_[None, :]
    return dome.max(1), seeds


# the hairline: low over the forehead (y −74 in the middle), down to the temples where the beard's sideburns meet it,
# over the ear, down to the nape
HL_AZ = [0, 40, 70, 90, 104, 120, 140, 180]
HL_EL = [36, 32, 20, 6, 4, -6, -15, -21]
IV, IF = S.icosphere(5)
az = np.degrees(np.arctan2(np.abs(IV[:, 0]), IV[:, 2])); el = np.degrees(np.arcsin(IV[:, 1]))
edge = np.interp(az, HL_AZ, HL_EL)
keepf = (el > edge - 4)[IF].all(1)
IF = IF[keepf]; usedv = np.unique(IF); rm = -np.ones(len(IV), int); rm[usedv] = np.arange(len(usedv))
IV = IV[usedv]; IF = rm[IF]; el = el[usedv]; edge = edge[usedv]; az = az[usedv]
eln = np.radians(np.where(el < edge, edge, el)); azr = np.arctan2(IV[:, 0], IV[:, 2])
IV = np.c_[np.cos(eln) * np.sin(azr), np.sin(eln), np.cos(eln) * np.cos(azr)]
above = np.degrees(eln) - edge
area = np.linalg.norm(np.cross(IV[IF[:, 1]] - IV[IF[:, 0]], IV[IF[:, 2]] - IV[IF[:, 0]]), axis=1)
IF = IF[area > 1e-7]
r0 = skull_r(IV) + u(5) + u(10) * smooth(above / 14)
HV = CEN + IV * r0[:, None]
rise, hseeds = bumps(HV, IV, 400, (u(14), u(19)), (u(11), u(16)))
HV = CEN + IV * (r0 + rise * (0.45 + 0.55 * smooth(above / 8)))[:, None]
HT_ = IF if (M.vertex_normals(HV, IF) * (HV - CEN)).sum(1).mean() > 0 else IF[:, ::-1]
Wh = np.zeros((len(HV), NJ)); Wh[:, I['Head']] = 1
Hr = dict(V=HV, T=HT_, W=Wh)
print('hair', len(HV), 'vertices', len(hseeds), 'curls')

# ---------------------------------------------------------------- the beard: a cup round the jaw, wider than the face
# and deeper than the chin, open at the back; in front it leaves the cheeks and the mouth bare (its inner edge runs
# from the sideburn down the cheek to the mouth's corner and under the mouth)
by_ = np.r_[np.arange(-33, 118, 5.0), 118, 122, 124.5, 126]
b_a = np.interp(by_, [-33, -8, 30, 76, 104, 118, 126], [80, 84, 93, 85, 60, 38, 3])
b_f = np.interp(by_, [-8, 30, 44, 60, 76, 100, 116, 126], [60, 74, 86, 91, 93, 86, 56, 16])
b_zc = np.interp(by_, [-8, 100, 126], [-6, -6, 14])
b_in = np.interp(by_, [-33, -8, 12, 36, 43, 47], [79, 80, 70, 56, 30, 0])       # the bare front's half-width (BEARDS 'f', inner)
TB = np.radians(104)
n_half = 22
BV_ = []; open_mid = []
for yv, a_, f_, zc_, xin in zip(by_, b_a, b_f, b_zc, b_in):
    # the bare cheek: in front as the front view's inner edge, and back to where the profile's inner edge runs
    # (BEARDS 's': from the mouth's corner up to the ear) — the further back of the two
    th_in = np.arcsin(min(1.0, (xin / a_)) ** (P_ / 2)) if xin > 0 else 0.0
    if xin > 0:
        zin = np.interp(yv, [-33, -8, 10, 30, 44, 47], [-14, -4, 8, 24, 48, 95]); cq = (zin - zc_) / (f_ - zc_)
        th_in = max(th_in, np.arccos(np.clip(np.sign(cq) * abs(cq) ** (P_ / 2), -0.3, 1)))
    ths = th_in + (TB - th_in) * np.linspace(0, 1, n_half)
    ths = np.r_[-ths[::-1], ths]
    x_, z_ = S.ring(a_, zc_, f_ - zc_, 34, ths)
    BV_ += list(np.c_[u(x_), np.full(len(ths), float(y3(yv))), u(z_)])
    open_mid.append(xin > 0)
BV_ = np.array(BV_); nc = 2 * n_half
BT_ = []
for r in range(len(by_) - 1):
    for c in range(nc - 1):
        if c == n_half - 1 and (open_mid[r] or open_mid[r + 1]): continue          # the bare front between the two halves
        a0 = r * nc + c; a1 = a0 + 1; b0 = a0 + nc; b1 = b0 + 1
        BT_ += [[a0, b0, a1], [a1, b0, b1]]
BT_ = np.array(BT_)
BV_ = off_head(BV_, u(6))
Abd = M.adjacency(len(BV_), [list(t_) for t_ in BT_])
BV_ = M.smooth(BV_, Abd, np.ones(len(BV_), bool), iters=3, lam=0.4)
bn = M.vertex_normals(BV_, BT_)
if (bn * (BV_ - [0, float(y3(60)), 0])).sum(1).mean() < 0: BT_ = BT_[:, ::-1]; bn = -bn
Wb = np.zeros((len(BV_), NJ)); wjb = smooth((ydr(BV_[:, 1]) - 58) / 26) * smooth((BV_[:, 2] - u(-30)) / u(50))
Wb[:, I['Head']] = 1 - wjb; Wb[:, I['Jaw']] = wjb
Bd = dict(V=BV_, T=BT_, W=Wb)
print('beard', len(BV_), 'vertices')

# ---------------------------------------------------------------- one mesh
G = dict(skin=1, hair=2, jacket=3, apron=4, trousers=5, shoe=6, towel=7)
pieces = [('body', B, G['skin']), ('head', Hh, G['skin'])] + \
         [('jacket', Jk, G['jacket'])] + [('sleeve' + s_['side'], s_, G['jacket']) for s_ in SL] + \
         [('trousers' + s_['side'], s_, G['trousers']) for s_ in TRS] + \
         [('apron', Ap, G['apron']), ('bib', Bb, G['apron'])] + [('strap%d' % i, s_, G['apron']) for i, s_ in enumerate(STRAPS)] + \
         [('towel', Tw, G['towel']), ('hair', Hr, G['hair']), ('beard', Bd, G['hair'])]
Vs, Ts, Ws, grp, band, stripe, pid = [], [], [], [], [], [], []
base = tbase = 0; ranges, tranges = {}, {}
for k, (name, p, g_) in enumerate(pieces):
    n = len(p['V'])
    Vs.append(p['V']); Ts.append(p['T'] + base); Ws.append(p['W'])
    grp.append(p['grp'].astype(np.uint8) if 'grp' in p else np.full(n, g_, np.uint8)); pid.append(np.full(n, k, np.uint8))
    band.append(-np.ones(n)); stripe.append(p.get('stripe', -np.ones(n) * 100))
    ranges[name] = [base, base + n]; tranges[name] = [tbase, tbase + len(p['T'])]; base += n; tbase += len(p['T'])
P = np.vstack(Vs); T = np.vstack(Ts); W = np.maximum(np.vstack(Ws), 0); N = len(P)
order = np.argsort(-W, 1)[:, :4]
SJ = order.astype(np.uint8); SWt = np.take_along_axis(W, order, 1); SWt /= SWt.sum(1, keepdims=True)
grp, pid, band, stripe = map(np.concatenate, (grp, pid, band, stripe))
PN = [p[0] for p in pieces]

# ---------------------------------------------------------------- edges: each once, with its triangles
e = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
f = np.tile(np.arange(len(T)), 3)
key = np.sort(e, 1); o = np.lexsort((key[:, 1], key[:, 0])); key, f = key[o], f[o]
first = np.r_[True, (key[1:] != key[:-1]).any(1)]
idx = np.flatnonzero(first); cnt = np.diff(np.r_[idx, len(key)])
E = key[idx]
F0 = f[idx]; F1 = np.where(cnt >= 2, f[np.minimum(idx + 1, len(f) - 1)], -1)
print('edges', len(E), 'open', (F1 < 0).sum(), 'more than two', (cnt > 2).sum())
hd0, hd1 = ranges['head']
drop = np.zeros(len(E), bool)
inp = lambda k: (E[:, 0] >= ranges[k][0]) & (E[:, 0] < ranges[k][1])
inhead = inp('head')
drop |= inhead & (F1 < 0)                                         # the head's own holes (eyes, mouth, the neck's end)
ex, ey = P[E[:, 0], 0] / K, ydr(P[E[:, 0], 1])
for cx, cy, rx, ry in D.REG:                                      # where the face is drawn, not contoured
    drop |= inhead & ((((ex - cx) / (rx * 1.15)) ** 2 + ((ey - cy) / (ry * 1.15)) ** 2) < 1) & (P[E[:, 0], 2] > 0.02)
drop |= inp('body') & (F1 < 0)                                    # the cuts of the forearms and the ankles
for k in PN:                                                      # ends that are inside other parts
    if k.startswith('sleeve'): drop |= inp(k) & (F1 < 0) & ((E[:, 0] - ranges[k][0]) < 26)
    if k.startswith('trousers'): drop |= inp(k) & (F1 < 0) & (P[E[:, 0], 1] > 0.5)
    if k.startswith('strap'): drop |= inp(k) & (F1 < 0) & ((ey > BIB0 - 6) | (ey < 124))
drop |= inp('bib') & (F1 < 0) & (ey > WAIST - 4)                        # the bib's lower edge is the skirt's upper one
drop |= inp('beard') & (F1 < 0) & (P[E[:, 0], 2] < u(-12))      # the beard's back edge, by the ear

inner = np.ones(N, np.uint8)
# on the face a silhouette of skin over skin is a line only on the ear; the nose is drawn by the drawing's own stroke
mid_face = (V0[:, 2] > 0.0) & (yd > -96) & (yd < 110)
inner[hd0:hd1] = np.where(mid_face & ~earm, 0, 1)
inner[ranges['body'][0]:ranges['body'][1]] = np.where(isfoot, 0, 1)        # a clog is one form: no lines of toes
inner[slice(*ranges['hair'])] = 2
inner[slice(*ranges['beard'])] = 0

# ---------------------------------------------------------------- the face grid on the head (front projection)
thi = np.arange(*tranges['head']); TH = T[thi]
GX = np.arange(-99, 100, 3.0); GY = np.arange(-99, 118, 3.0)
gx, gy = np.meshgrid(GX, GY)
q = np.c_[(gx * K).ravel(), y3(gy).ravel()]
faceTri = -np.ones(len(q), np.int64); faceBar = np.zeros((len(q), 3)); best = np.full(len(q), -1e9)
A3, B3, C3 = P[TH[:, 0]], P[TH[:, 1]], P[TH[:, 2]]
earT = earm[TH - hd0].any(1)
for ti_ in range(len(TH)):
    if earT[ti_]: continue
    a2, b2, c2 = A3[ti_, :2], B3[ti_, :2], C3[ti_, :2]
    lo = np.minimum(np.minimum(a2, b2), c2); hi = np.maximum(np.maximum(a2, b2), c2)
    m = np.flatnonzero((q[:, 0] >= lo[0]) & (q[:, 0] <= hi[0]) & (q[:, 1] >= lo[1]) & (q[:, 1] <= hi[1]))
    if not len(m): continue
    v0, v1 = b2 - a2, c2 - a2; den = v0[0] * v1[1] - v1[0] * v0[1]
    if abs(den) < 1e-14: continue
    w = q[m] - a2
    l1 = (w[:, 0] * v1[1] - v1[0] * w[:, 1]) / den; l2 = (v0[0] * w[:, 1] - w[:, 0] * v0[1]) / den; l0 = 1 - l1 - l2
    ok = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
    m, l0, l1, l2 = m[ok], l0[ok], l1[ok], l2[ok]
    z = l0 * A3[ti_, 2] + l1 * B3[ti_, 2] + l2 * C3[ti_, 2]
    nz = np.cross(B3[ti_] - A3[ti_], C3[ti_] - A3[ti_])[2]
    better = (z > best[m]) & (nz > 0)
    m, z = m[better], z[better]
    best[m] = z; faceTri[m] = thi[ti_]
    faceBar[m] = np.c_[l0[better], l1[better], l2[better]]
print('face grid', len(q), 'on the head', (faceTri >= 0).sum())

# ---------------------------------------------------------------- strokes and marks that belong to the form
strokes, marks = [], []
a0 = ranges['apron'][0]; nrow = len(srow)
row_of = lambda v: int(np.argmin(np.abs(sk_y - v)))
col_of = lambda r, x: int(np.argmin(np.abs(AV[r * AC:(r + 1) * AC, 0] - x) + 10 * (AV[r * AC:(r + 1) * AC, 2] < 0)))
for x_, v0_ in [(-0.15, 566), (-0.03, 560), (0.1, 570)]:                               # the skirt's folds
    strokes.append(dict(kind='fold', w=3.0, v=[int(a0 + r * AC + col_of(r, x_ * (1 + 0.0002 * (sk_y[r] - WAIST)))) for r in range(row_of(v0_), nrow, 2)]))
j0, j1 = ranges['jacket']; jtree = cKDTree(P[j0:j1])
jv = lambda x, v: int(j0 + jtree.query([x, float(y3(v)), jfront(x, v)])[1])
strokes.append(dict(kind='flap', w=3.0, v=[jv(u(2), v) for v in range(156, 317, 10)]))
for x_, v in [(-34, 236), (30, 236)]: marks.append(dict(kind='button', v=jv(u(x_), v), r=6))
b0 = ranges['hair'][0]
for i in rng.permutation(len(hseeds))[:60]:                                            # curls: a short arc in a bump
    marks.append(dict(kind='curl', v=int(b0 + hseeds[i]), r=float(rng.uniform(5, 7)), rot=float(rng.uniform(-30, 30)), min=0.4))

header = dict(format='r37/character', version=1, id='marat-s13', label={'ru': 'Марат, японская гравюра'},
              skinning='cor', source='Anny moood-man (engine) + Human Base Meshes stylised head (CC0) + shells from the С13 drawing',
              pieces=ranges, trianglePieces=tranges, pieceNames=PN, groups=G,
              face=dict(gx=[float(GX[0]), 3.0, len(GX)], gy=[float(GY[0]), 3.0, len(GY)]),
              strokes=strokes, marks=marks, units=K, floorUnits=D.FLOOR,
              skirt=dict(piece='apron', ring=AC, closed=False, top=float(y3(760)),
                         caps=[['LeftLeg', 'LeftShin', 0.105], ['LeftShin', 'LeftFoot', 0.08], ['RightLeg', 'RightShin', 0.105], ['RightShin', 'RightFoot', 0.08]]))
pack.save(os.path.join(OUT, 'marat.json'), header, dict(
    positions=P.astype(np.float32).ravel(), triangles=T.astype(np.uint32).ravel(),
    skinJoints=SJ.astype(np.uint8), skinWeights=SWt.astype(np.float32),
    joints=J1.astype(np.float32).ravel(), frames=FR.ravel(),
    band=band.astype(np.float32), stripe=stripe.astype(np.float32), grp=grp, pid=pid,
    edges=E.astype(np.uint32).ravel(), edgeTris=np.where(np.c_[F0, F1] < 0, 0xFFFFFFFF, np.c_[F0, F1]).astype(np.uint32).ravel(),
    edgeDrop=drop.astype(np.uint8), inner=inner,
    faceTri=np.where(faceTri < 0, 0xFFFFFFFF, faceTri).astype(np.uint32), faceBar=faceBar.astype(np.float32).ravel()))
print('saved', OUT, N, 'vertices', len(T), 'triangles', {k: v[1] - v[0] for k, v in ranges.items()})
