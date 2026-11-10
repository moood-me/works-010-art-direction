"""Аня (С13, the woodblock print) in 3D: the pack the print renderer (web/print.js, web/kit.js, web/char.js) takes.
  python3 build.py            → ../data/anya.json, anya.bin
Bases: Anny's woman (engine/data/bodies/moood-woman: hands, shins, feet and the SOMA skeleton with its weights),
re-proportioned to the drawing (7.8 heads, narrow sloping shoulders, thin limbs); Blender's Human Base Meshes stylised
head (CC0), fitted to parts.head_pts front and profile (head.py); the dress, the cardigan, its sleeves and the long
loose hair are shells of the drawing's sizes (shells.py).
What the print renderer needs instead of a material: grp (the colour block), band (the shoe's cut on the foot), edges,
inner (where a part's silhouette over itself is a line: 0 no, 1 yes, 2 thin), the face grid, strokes (the skirt's folds,
the hair's light lines, the hairline's separate hairs)."""
import os, sys
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M, head as Hd, drawing as D, shells as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data')
HBM = '/home/user/cache/to3d-r37-s13-anya/hbm_head.npz'      # tools/hbm_export.py's arrays
os.makedirs(OUT, exist_ok=True)
K = D.K
y3 = lambda yd: (D.FLOOR - np.asarray(yd, float)) * K
ydr = lambda y: D.FLOOR - np.asarray(y, float) / K
u = lambda v: np.asarray(v, float) * K
smooth = S.smooth
rng = np.random.default_rng(37)
P_ = 2.3

# ---------------------------------------------------------------- skeleton and Anny's woman
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body('moood-woman')
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


# the drawing's joints: long legs close together, a short trunk, a long thin neck, narrow shoulders, arms a little short
J1 = J0.copy()
HIP = 0.955; NECK1 = float(y3(205)); TR = (NECK1 - HIP) / (J0[I['Neck1'], 1] - J0[I['Hips'], 1])
J1[I['Hips']] = [0, HIP, 0]
for n in ['Spine1', 'Spine2', 'Chest']: J1[I[n]] = [0, HIP + TR * (J0[I[n], 1] - J0[I['Hips'], 1]), J0[I[n], 2] * 0.7]
J1[I['Neck1']] = [0, NECK1, -0.006]
J1[I['Neck2']] = [0, y3(150), 0.0]
J1[I['Head']] = [0, y3(98), 0.004]
J1[I['HeadEnd']] = [0, y3(-100), 0.0]
J1[I['Jaw']] = [0, y3(34), -0.02]
for s, sg in (('Left', 1), ('Right', -1)):
    J1[I[s + 'Eye']] = [sg * u(33), y3(0), u(70)]
    J1[I[s + 'Shoulder']] = [sg * 0.015, y3(212), 0.03]
    J1[I[s + 'Arm']] = [sg * 0.112, y3(240), -0.004]
    for n, k in (('ForeArm', 0.9), ('Hand', 0.9)):
        j = I[s + n]; J1[j] = J1[PARENT[j]] + k * (J0[j] - J0[PARENT[j]])
    for j in under(I[s + 'Hand'])[1:]:
        J1[j] = J1[PARENT[j]] + 0.8 * (J0[j] - J0[PARENT[j]])
    J1[I[s + 'Leg']] = [sg * 0.078, 0.875, 0.0]
    J1[I[s + 'Shin']] = [sg * 0.072, 0.470, 0.006]
    J1[I[s + 'Foot']] = [sg * 0.076, 0.075, -0.014]
    for n in ('ToeBase', 'ToeEnd'):
        j = I[s + n]; J1[j] = J1[PARENT[j]] + (J0[j] - J0[PARENT[j]]) * [0.0, 1.0, 0.86]


def rot_between(a_, b_):
    a_ = a_ / np.linalg.norm(a_); b_ = b_ / np.linalg.norm(b_)
    v = np.cross(a_, b_); c = a_ @ b_; s = np.linalg.norm(v)
    if s < 1e-9: return np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * ((1 - c) / s ** 2)


RADIAL = {'Leg': 0.86, 'Shin': 0.76, 'Arm': 0.82, 'ForeArm': 0.8}


def joint_affine(j):
    """Joint j's move of the rest: x ↦ J1_j + A (x − J0_j). A limb's bone turns and stretches to the new joints and is
    made thinner across; feet and hands are scaled."""
    n = NAMES[j]
    for key, r in RADIAL.items():
        if n.endswith(key) and n[:-len(key)] in ('Left', 'Right'):
            c = [k for k in range(NJ) if PARENT[k] == j][0]
            d0 = J0[c] - J0[j]; d1 = J1[c] - J1[j]
            ln = np.linalg.norm(d1) / np.linalg.norm(d0); d0 /= np.linalg.norm(d0)
            return rot_between(d0, d1) @ (r * np.eye(3) + (ln - r) * np.outer(d0, d0))
    if 'Foot' in n or 'Toe' in n: return np.diag([0.84, 0.9, 0.86])
    if 'Hand' in n: return 0.8 * np.eye(3)
    if n in ('Hips', 'Spine1', 'Spine2', 'Chest') or 'Shoulder' in n: return np.diag([0.8, TR, 0.8])
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
hand = np.array(['Hand' in n for n in dn])
fore = np.array([n.endswith('ForeArm') for n in dn])
legs = np.array([('Shin' in n or 'Foot' in n or 'Toe' in n or n.endswith('Leg')) for n in dn])
near_wrist = np.zeros(len(P0), bool)
for s in ('Left', 'Right'): near_wrist |= np.linalg.norm(PF - J1[I[s + 'Hand']], axis=1) < 0.07
keep = hand | (fore & near_wrist) | (legs & (PF[:, 1] < 0.56))
tk = keep[TRI0].all(1)
bi = np.where(keep)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
B = dict(V=PF[bi], T=remap[TRI0[tk]])
nb = len(bi)
by = B['V'][:, 1]
isfoot = np.array([('Foot' in n or 'Toe' in n) for n in dn[bi]]) | (by < 0.085)
ishand = hand[bi]
Ab = M.adjacency(nb, [list(t_) for t_ in B['T']])
Vsm = M.smooth(B['V'], Ab, isfoot & (by < 0.07), iters=60, lam=0.5)       # a slipper: the foot as one rounded form,
sole = smooth((by - 0.004) / 0.02)[:, None]                                # its sole kept flat on the floor
B['V'] = np.where(isfoot[:, None], Vsm * [1, 0, 1] + (B['V'] * (1 - sole) + Vsm * sole) * [0, 1, 0], B['V'])
nrm = M.vertex_normals(B['V'], B['T'])
B['V'][isfoot] += nrm[isfoot] * 0.003 * [1, 0, 1]
B['V'][:, 1] = np.where(isfoot, np.maximum(B['V'][:, 1], 0.0), B['V'][:, 1])
BW = np.zeros((nb, NJ))
for q in range(4): np.add.at(BW, (np.arange(nb), SJ0[bi][:, q]), SW0[bi][:, q])
B['W'] = BW
B['band'] = np.where(legs[bi], np.where(np.array(['Toe' in n for n in dn[bi]]), 0.0, B['V'][:, 1]), -1.0)        # the legs' rest height: the renderer cuts the slipper by it

# ---------------------------------------------------------------- the head
hv, hP, eL, eR = Hd.load(HBM)
earm = Hd.ears(hv)
hv2, = Hd.fit(hv, earm, ear=(u(78), np.array([0.5, 0.6, 0.58])))
ec = hv2[earm].mean(0)
hv2[earm] += [0, y3(8) - ec[1], u(-19) - ec[2]]          # the ears: parts.ear — front x 80…93, y −16…30; profile x 16…40
V0 = Hd.flatten(hv2, D.REG, front_min=0.02)
# the nose: the base's laid flat, and the drawing's small soft one put on: its profile head_pts('s'), narrow
V0 = Hd.flatten(V0, [(0, 16, 17, 24)], front_min=0.02)
_xd, _yd = V0[:, 0] / K, ydr(V0[:, 1])
_m = (V0[:, 2] > 0.02) & (np.abs(_xd) < 26) & (_yd > -22) & (_yd < 44)
_pick = lambda yy: V0[np.argmin(np.where(_m, np.abs(_xd) + np.abs(_yd - yy), 1e9)), 2]
_plane = lambda y: np.interp(y, [-18, 40], [_pick(-18), _pick(40)])
_h = np.clip(np.interp(_yd, D.NOSE[:, 0], D.NOSE[:, 1], left=np.nan, right=np.nan) * K - _plane(_yd), 0, None)
_w = np.interp(_yd, [-18, 0, 14, 27, 34, 37], [5, 6, 8, 11, 10, 7])
_t = np.clip(np.abs(_xd) / _w, 0, 1)
_prof = (1 - _t ** 2) ** 0.9
V0[:, 2] = np.where(_m & ~np.isnan(_h), np.maximum(V0[:, 2], _plane(_yd) + np.nan_to_num(_h) * _prof), V0[:, 2])
nh = len(V0)
HT = M.triangulate(hP)
xd, yd = V0[:, 0] / K, ydr(V0[:, 1])
yde = yd - 18 * smooth(V0[:, 2] / 0.03)      # the chin and the jaw stay with the head
SW = np.zeros((nh, NJ))
sA = smooth((yde - 96) / 40); sB = smooth((yde - 140) / 36); sC = smooth((yde - 176) / 26)
SW[:, I['Head']] = 1 - sA
SW[:, I['Neck2']] = sA * (1 - sB)
SW[:, I['Neck1']] = sA * sB * (1 - sC)
SW[:, I['Chest']] = sA * sB * sC
Hh = dict(V=V0, T=HT, W=SW)
used = np.zeros(nh, bool); used[np.unique(HT)] = True
hn = M.vertex_normals(V0, HT)
skullm = used & ~earm
htree = cKDTree(V0[skullm]); hV, hN = V0[skullm], hn[skullm]


def off_head(V, d, iters=3):
    """Points kept at least d outside the head (its ears not counted)."""
    V = V.copy()
    for _ in range(iters):
        dd, ii = htree.query(V)
        s_ = ((V - hV[ii]) * hN[ii]).sum(1)
        m = s_ < d
        V[m] += hN[ii[m]] * (d - s_[m])[:, None]
    return V


# ---------------------------------------------------------------- the dress, the chest in its scoop, the cardigan
def rows_of(spec, step=6.0):
    spec = np.array(spec, float); ys = np.arange(spec[0, 0], spec[-1, 0] + 1e-6, step)
    ys = np.unique(np.r_[ys, spec[-1, 0]])
    f = lambda k: np.interp(ys, spec[:, 0], spec[:, k])
    a_, zf, zb = f(1), f(2), f(3)
    for _ in range(3):
        for arr in (a_, zf, zb):                     # rounded between the given heights
            arr[1:-1] = (arr[:-2] + 2 * arr[1:-1] + arr[2:]) / 4
    return [(float(y3(yy)), float(u(aa)), float(u((f_ + b_) / 2)), float(u((f_ - b_) / 2)), float(u((f_ - b_) / 2))) for yy, aa, f_, b_ in zip(ys, a_, zf, zb)]


# (drawing height, half-width, front, back): the neck ring, sloping shoulders, a small bust, a narrow waist, the skirt
# flaring to below the knee
HEM = 1093.0
DSPEC = [(158, 44, 30, -46), (176, 66, 38, -56), (200, 92, 48, -62), (222, 104, 54, -64), (300, 90, 66, -60),
         (400, 76, 54, -52), (470, 68, 48, -50), (560, 88, 62, -74), (700, 114, 86, -98), (900, 148, 118, -128),
         (HEM, 178, 144, -154)]
drows = rows_of(DSPEC, 8.0)
DC = 72
DV, DT = S.loft(drows, DC, True); DT = S.outward(DV, DT)
dyd = ydr(DV[:, 1]); dth = np.tile(np.linspace(0, 2 * np.pi, DC, endpoint=False), len(drows))
# the round neckline: the top rows dip in front to the scoop's bottom (y 205)
tt_ = np.clip((dyd - 158) / 90, 0, 1)
dip = 47 * np.clip(np.cos(dth), 0, None) ** 1.3 * (1 - tt_) ** 1.6
for i in np.flatnonzero(dip > 0.01):
    r = S.row_at(drows, float(y3(dyd[i] + dip[i])))
    x_, z_ = S.ring(r[1], r[2], r[3], r[4], np.array([dth[i]]))
    DV[i] = [x_[0], r[0], z_[0]]
# the skirt: soft folds deepening to the hem, the hem's wave
fold = smooth((dyd - 520) / 400)
rad = np.c_[DV[:, 0], np.zeros(len(DV)), DV[:, 2]]; rad /= np.linalg.norm(rad, axis=1, keepdims=True) + 1e-9
DV += rad * (u(7) * np.cos(7 * dth + 0.4) * fold)[:, None]
DV[:, 1] += u(9) * np.sin(7 * dth + 0.4) * smooth((dyd - 900) / 190)
Dd = dict(V=DV, T=DT)

CSPEC = [(166, 30, 16, -40), (178, 58, 31, -50), (200, 86, 43, -58), (240, 92, 54, -58)]
crows = rows_of(CSPEC, 6.0)
CV, CT = S.loft(crows, 40, True); CT = S.outward(CV, CT)
Cc = dict(V=CV, T=CT)


def dims_at(rows, yv):
    r = np.array(rows); o = np.argsort(r[:, 0])
    return [np.interp(yv, r[o, 0], r[o, k]) for k in range(1, 5)]


# the cardigan: open in front (the dress shows in the opening), a round yoke from the neck to the shoulders
CHEM = 582.0
gapf = lambda yy: np.interp(yy, [150, 250, CHEM], [38, 45, 36])
krows, kgap = [], []
for tt in np.linspace(1, 0, 12)[:-1]:
    yv = 150 + 72 * (1 - tt) ** 1.25
    a_ = 120 * (1 - tt) ** 0.8 + 46 * (1 - (1 - tt) ** 0.8)
    zf = 62 * (1 - tt) + 36 * tt; zb = -72 * (1 - tt) - 50 * tt
    krows.append((float(y3(yv)), float(u(a_)), float(u((zf + zb) / 2)), float(u((zf - zb) / 2)), float(u((zf - zb) / 2))))
    kgap.append(np.arcsin(min(gapf(yv) / a_, np.sin(np.radians(78)))))
for yy in np.r_[np.arange(222, CHEM, 8.0), CHEM]:
    da, dzc, ddf, ddb = dims_at(drows, y3(yy))
    a_ = max(u(np.interp(yy, [222, 400, CHEM], [120, 104, 100])), da + 0.008)
    zf = max(u(62), dzc + ddf + 0.008); zb = min(u(-72), dzc - ddb - 0.008)
    krows.append((float(y3(yy)), float(a_), float((zf + zb) / 2), float((zf - zb) / 2), float((zf - zb) / 2)))
    kgap.append(np.arcsin(min(gapf(yy) / (a_ / K), 0.97)))
KC = 64
KV, KT = S.loft(krows, KC, False, kgap); KT = S.outward(KV, KT)
Kc = dict(V=KV, T=KT)

SL = []
for s in ('Left', 'Right'):
    A_, E_, W_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']], J1[I[s + 'Hand']]
    d1 = (E_ - A_) / np.linalg.norm(E_ - A_); d2 = (W_ - E_) / np.linalg.norm(W_ - E_)
    path = S.catmull([A_ - d1 * 0.02, (A_ + E_) / 2, E_, (E_ + W_) / 2, W_ - d2 * 0.012], 8)
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]; L /= L[-1]
    radii = np.interp(L, [0, 0.12, 0.5, 0.9, 1.0], [0.034, 0.040, 0.034, 0.028, 0.027])
    V_, T_ = S.tube(path, radii, 24)
    arm = set(under(I[s + 'Shoulder'])); tr = np.array([j in arm for j in range(NJ)])
    SL.append(dict(V=V_, T=T_, W=WT.limb(V_, T_, tr, A_, 0.06), side=s))


def skirt_rule(V):
    yd_ = ydr(V[:, 1]); W = np.zeros((len(V), NJ))
    L = 0.55 * smooth((yd_ - 640) / 420)
    side = 1 / (1 + np.exp(-V[:, 0] / 0.035))
    W[:, I['LeftLeg']] = L * side; W[:, I['RightLeg']] = L * (1 - side); W[:, I['Hips']] = 1 - L
    return W


def cloth_weights(V, T):
    W = WT.transfer(V)
    uu = smooth((ydr(V[:, 1]) - 540) / 120)[:, None]
    return WT.smooth((1 - uu) * W + uu * skirt_rule(V), T, 12)


Dd['W'] = cloth_weights(DV, DT)
Kc['W'] = cloth_weights(KV, KT)
Cc['W'] = WT.smooth(WT.transfer(CV), CT, 8)

# ---------------------------------------------------------------- the hair: long, loose, parted in the middle
# One shell from the crown to below the shoulder blades: its half-width from the front view (hair_back, hair_front),
# its back from the profile (hair_front 's', hair_side_fall). In front it is open: above the ears the opening's edge is
# the hairline on the forehead (hair_front 'f'); at the ear the hair goes behind it and falls behind the shoulders.
ROWS, COLS = 124, 96
HY0, HY1 = -118.0, 322.0
from scipy.interpolate import PchipInterpolator as _PI
a_of = _PI([-118, -94, -50, -6, 60, 180, 322], [30, 76, 97, 99, 108, 118, 127])
zb_of = _PI([-118, -100, -56, -6, 70, 170, 322], [-10, -74, -106, -112, -106, -112, -128])
zc_of = lambda y: np.interp(y, [-118, -90, 10, 60, 322], [8, -8, -10, -22, -30])
zt_of = lambda y: np.interp(y, [-118, -108, -78, -44], [18, 40, 71, 78])            # the front over the forehead (profile)
w_of = lambda y: np.interp(y, [-86, -84, -78, -66, -52, -38, -22, -8], [0, 16, 32, 50, 62, 70, 75, 77])       # the hairline's half-width
hy_ = ydr(V0[:, 1]); hx_ = V0[:, 0] / K


def face_z(y, w):
    m = skullm & (abs(hy_ - y) < 7) & (abs(abs(hx_) - w) < 9)
    return V0[m, 2].max() / K + 4 if m.sum() else np.nan


def hair_row(y):
    """A row's ring: (half-width, centre, back depth, the opening's half-angle, front depth)."""
    k = 1.0
    if y < -104:      # the crown: a dome
        k = np.sqrt(max(1 - ((-104 - y) / 14.2) ** 2, 0.0004)); y = -104
    a_, zc, zb = float(a_of(y)) * k, zc_of(y), zc_of(y) - k * (zc_of(y) - float(zb_of(y)))
    if y <= -86: return a_, zc, zc - zb, 0.0, k * (zt_of(y) - zc)
    yy = min(y, -26.0)
    w = w_of(yy); thw = np.arcsin(min(w / a_, 0.985) ** (P_ / 2))
    ze = face_z(yy, w)
    if np.isnan(ze): ze = zt_of(-44)
    df = (ze - zc) / max(np.cos(thw), 0.12) ** (2 / P_)
    if y > -26:       # behind the ear and down behind the shoulders
        thw = np.interp(y, [-26, -10, 30, 110, 322], [thw, np.radians(100), np.radians(106), np.radians(107), np.radians(104)])
    return a_, zc, zc - zb, thw, df


HV = np.zeros((ROWS, COLS, 3))
for r in range(ROWS):
    y = HY0 + 0.4 + (HY1 - HY0 - 0.4) * (r / (ROWS - 1)) ** 1.06
    a_, zc, db, thw, df = hair_row(y)
    th = np.linspace(thw, 2 * np.pi - thw, COLS)
    s_, c_ = np.sin(th), np.cos(th)
    x = a_ * np.sign(s_) * np.abs(s_) ** (2 / P_)
    z = zc + np.where(c_ > 0, df, db) * np.sign(c_) * np.abs(c_) ** (2 / P_)
    lock = np.abs(np.sin(5.0 * (th - thw) * np.pi / (2 * np.pi - 2 * thw)))
    yv = y - 9 * (1 - lock) ** 1.4 * smooth((r / (ROWS - 1) - 0.86) / 0.14)        # the ends: soft points
    HV[r] = np.c_[u(x), y3(yv), u(z)]
HV = HV.reshape(-1, 3)
HT_ = S.grid(ROWS, COLS, False)
HV = off_head(HV, 0.005)


def push_out(V, rows_, margin):
    """Out of a garment's rings (as ellipses)."""
    r_ = np.array(rows_); o = np.argsort(r_[:, 0]); r_ = r_[o]
    for i, p in enumerate(V):
        if p[1] > r_[-1, 0] + 0.02 or p[1] < r_[0, 0]: continue
        a_, zc, df, db = [np.interp(p[1], r_[:, 0], r_[:, k]) for k in range(1, 5)]
        dz_ = p[2] - zc; d_ = df if dz_ > 0 else db
        rr = np.hypot(p[0] / a_, dz_ / d_)
        if rr < margin: V[i, 0] *= margin / rr; V[i, 2] = zc + dz_ * margin / rr


push_out(HV, krows, 1.08)
Ah = M.adjacency(len(HV), [list(t_) for t_ in HT_])
hyd = ydr(HV[:, 1])
HV = M.smooth(HV, Ah, hyd > 60, iters=5, lam=0.5)
HV = off_head(M.smooth(HV, Ah, np.ones(len(HV), bool), iters=3, lam=0.5), 0.004)
if (M.vertex_normals(HV, HT_) * (HV - [0, float(y3(0)), u(-10)])).sum(1).mean() < 0: HT_ = HT_[:, ::-1]
Wh = np.zeros((len(HV), NJ))
wh = 1 - 0.85 * smooth((hyd - 100) / 110)
Wh[:, I['Head']] = wh; Wh[:, I['Chest']] = (1 - wh) * 0.75; Wh[:, I['Neck1']] = (1 - wh) * 0.25
Hr = dict(V=HV, T=HT_, W=Wh)
print('hair', len(HV), 'vertices')

# ---------------------------------------------------------------- one mesh
G = dict(skin=1, hair=2, card=3, dress=4, shoe=5)
pieces = [('body', B, G['skin']), ('head', Hh, G['skin']), ('chest', Cc, G['skin']), ('dress', Dd, G['dress']),
          ('cardigan', Kc, G['card'])] + [('sleeve' + s_['side'], s_, G['card']) for s_ in SL] + [('hair', Hr, G['hair'])]
Vs, Ts, Ws, grp, band, stripe, pid = [], [], [], [], [], [], []
base = tbase = 0; ranges, tranges = {}, {}
for k, (name, p, g_) in enumerate(pieces):
    n = len(p['V'])
    Vs.append(p['V']); Ts.append(p['T'] + base); Ws.append(p['W'])
    grp.append(np.full(n, g_, np.uint8)); pid.append(np.full(n, k, np.uint8))
    band.append(p.get('band', -np.ones(n))); stripe.append(-np.ones(n) * 100)
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
drop |= inp('body') & (F1 < 0)                                    # the cuts of the wrists and the legs
drop |= inp('chest') & (F1 < 0)
for k in PN:
    if k.startswith('sleeve'): drop |= inp(k) & (F1 < 0) & ((E[:, 0] - ranges[k][0]) < 24)       # its end inside the cardigan
h0 = ranges['hair'][0]
hcol = (E[:, 0] - h0) % COLS; hrow = (E[:, 0] - h0) // COLS
hl_rows = np.flatnonzero((hyd.reshape(ROWS, COLS)[:, 0] > -87) & (hyd.reshape(ROWS, COLS)[:, 0] < -18))
drop |= inp('hair') & (F1 < 0) & (hrow <= hl_rows[-1])            # the hairline is separate hairs, not a line

inner = np.ones(N, np.uint8)
# on the face a silhouette of skin over skin is a line only along the jaw (over the neck) and on the ear; the nose
# is drawn by the drawing's own stroke (char.js)
mid_face = (V0[:, 2] > 0.0) & (yd > -96) & ((yd < 80) | ((yd < 99) & (np.abs(xd) < 44)))
inner[hd0:hd1] = np.where(mid_face & ~earm, 0, 1)
b0 = ranges['body'][0]
inner[b0:b0 + nb] = np.where(isfoot, 0, 1)                         # a slipper is one form: no lines of toes
inner[slice(*ranges['hair'])] = 0
inner[slice(*ranges['chest'])] = 0

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

# ---------------------------------------------------------------- strokes that belong to the form
strokes = []
d0 = ranges['dress'][0]; nrow = len(drows)
drow_y = ydr(np.array([r[0] for r in drows]))
row_of = lambda v: int(np.argmin(np.abs(drow_y - v)))
for c, v0_ in [(4, 520), (13, 560), (66, 500), (58, 580), (23, 640), (49, 620), (31, 560), (41, 600)]:      # the skirt's folds
    strokes.append(dict(kind='fold', w=3.0, prof='taper', v=[int(d0 + r * DC + c) for r in range(row_of(v0_), nrow, 2)] + [int(d0 + (nrow - 1) * DC + c)]))
for c in [5, 12, 20, 29, 38, 47, 57, 66, 75, 83, 90]:             # the hair's light lines: the comb's trace
    r0 = int(rng.integers(8, 40)); r1 = int(rng.integers(92, ROWS - 4))
    strokes.append(dict(kind='sheen', w=0.9, prof='swell', v=[int(h0 + r * COLS + c) for r in range(r0, r1, 3)]))
for side, c in (('L', 0), ('R', COLS - 1)):                        # the hairline: separate hairs out of its edge
    strokes.append(dict(kind='fringe', side=1 if side == 'L' else -1, v=[int(h0 + r * COLS + c) for r in hl_rows]))

header = dict(format='r37/character', version=1, id='anya-s13', label={'ru': 'Аня, японская гравюра'},
              skinning='cor', source='Anny moood-woman (engine) + Human Base Meshes stylised head (CC0) + shells from the С13 drawing',
              pieces=ranges, trianglePieces=tranges, pieceNames=PN, groups=G,
              face=dict(gx=[float(GX[0]), 3.0, len(GX)], gy=[float(GY[0]), 3.0, len(GY)]),
              strokes=strokes, marks=[], units=K, floorUnits=D.FLOOR,
              skirt=dict(piece='dress', ring=DC, closed=True, top=float(y3(600)),
                         caps=[['LeftLeg', 'LeftShin', 0.06], ['LeftShin', 'LeftFoot', 0.05], ['RightLeg', 'RightShin', 0.06], ['RightShin', 'RightFoot', 0.05]]))
pack.save(os.path.join(OUT, 'anya.json'), header, dict(
    positions=P.astype(np.float32).ravel(), triangles=T.astype(np.uint32).ravel(),
    skinJoints=SJ.astype(np.uint8), skinWeights=SWt.astype(np.float32),
    joints=J1.astype(np.float32).ravel(), frames=FR.ravel(),
    band=band.astype(np.float32), stripe=stripe.astype(np.float32), grp=grp, pid=pid,
    edges=E.astype(np.uint32).ravel(), edgeTris=np.where(np.c_[F0, F1] < 0, 0xFFFFFFFF, np.c_[F0, F1]).astype(np.uint32).ravel(),
    edgeDrop=drop.astype(np.uint8), inner=inner,
    faceTri=np.where(faceTri < 0, 0xFFFFFFFF, faceTri).astype(np.uint32), faceBar=faceBar.astype(np.float32).ravel()))
print('saved', OUT, N, 'vertices', len(T), 'triangles', {k: v[1] - v[0] for k, v in ranges.items()})
