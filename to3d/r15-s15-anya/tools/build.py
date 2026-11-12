"""Аня, нуар (С15) in 3D: builds the character pack the viewer (web/anya.js) and the engine take.
  python3 build.py [outdir]
Р1's build (to3d/r1-s3-anya) with С15's shapes. Bases: Anny's body (engine/data/bodies/moood-woman: legs, feet and the
SOMA skeleton with its weights), Blender's Human Base Meshes stylised head (CC0; hbm_export.py), fitted to the drawing
(head.py); the clothes and the hair are built here from the drawing's silhouettes (drawing.py). Everything is skinned
to SOMA's 77 joints, so Kimodo's motions play on it through the engine. For the look the pack carries, per vertex,
its place in the head's own frame (hp, head units) and its kind — the viewer's shader draws the designed black shapes
from them."""
import os, sys, json
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M, headfit as Hd, drawing as D

K = D.K
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/cache/to3d-r15-s15-anya/out'
HBM = '/home/user/cache/to3d-r15-s15-anya/hbm_head.npz'
os.makedirs(OUT, exist_ok=True)

y3 = lambda yd: (D.FLOOR - np.asarray(yd, float)) * K
ydr = lambda y: D.FLOOR - np.asarray(y, float) / K
u = lambda v: np.asarray(v, float) * K                     # drawing units → metres
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))


def rgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


C = {k: rgb(v) for k, v in dict(skin='#e6c6a4', hair='#b84a2a', card='#c9982f', dress='#4b6788', shoe='#7d3528', black='#07070b', rim='#3b4566').items()}
X0, X1, Y0, Y1 = -120.0, 120.0, -130.0, 130.0      # the face layer's box, units (web/face.js)

# ---------------------------------------------------------------- skeleton and Anny's body
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body('moood-woman')
P0 = a['positions'].reshape(-1, 3).astype(float); J0 = a['joints'].reshape(-1, 3).astype(float)
FR = a['frames'].reshape(-1, 4).astype(np.float32)
TRI0 = t['triangles'].reshape(-1, 3).astype(np.int64)
SJ0 = t['skinJoints'].reshape(-1, 4).astype(np.int64); SW0 = t['skinWeights'].reshape(-1, 4).astype(float)
dz = -J0[I['Hips'], 2]
P0[:, 2] += dz; J0[:, 2] += dz


def under(j):
    out, st = [], [j]
    while st:
        k = st.pop(); out.append(k); st += list(np.where(PARENT == k)[0])
    return out


# the new joints: the drawing's heights for the spine, the neck and the head; shoulders lower and narrower (the
# drawing's long thin neck and sloped shoulders); arms 8 % shorter; legs a little closer
J1 = J0.copy()
spine_y = lambda y: np.interp(y, [0.897, 1.008, 1.076, 1.314], [0.897, 1.0, 1.06, 1.215])
for n in ['Spine1', 'Spine2', 'Chest']: J1[I[n], 1] = spine_y(J0[I[n], 1])
J1[I['Neck1']] = [0, y3(238), 0.0]
J1[I['Neck2']] = [0, y3(165), 0.0]
J1[I['Head']] = [0, y3(106), -0.004]
J1[I['HeadEnd']] = [0, y3(D.SKULL), -0.01]
J1[I['Jaw']] = [0, y3(40), -0.03]          # where the jaw turns, under the ear
for s, sg in (('Left', 1), ('Right', -1)):
    J1[I[s + 'Eye']] = [sg * u(37), y3(0), 0.07]
    J1[I[s + 'Shoulder']] = [sg * 0.015, 1.19, 0.035]
    J1[I[s + 'Arm']] = [sg * 0.128, y3(D.Y_SH + 30), 0.0]
    for n, k in (('ForeArm', 0.92), ('Hand', 0.92)):
        j = I[s + n]; J1[j] = J1[PARENT[j]] + k * (J0[j] - J0[PARENT[j]])
    for j in under(I[s + 'Hand'])[1:]:
        J1[j] = J1[PARENT[j]] + 0.84 * (J0[j] - J0[PARENT[j]])
    for n, x in (('Leg', 0.072), ('Shin', 0.064), ('Foot', 0.068)):
        J1[I[s + n], 0] = sg * x
    for n in ('ToeBase', 'ToeEnd'):        # a shorter foot: a small shoe as drawn
        j = I[s + n]; J1[j] = J1[PARENT[j]] + 0.82 * (J0[j] - J0[PARENT[j]])


def joint_affine(j):
    """Joint j's move of the rest: x ↦ J1_j + A (x − J0_j): radial slimming of shins and forearms, smaller feet/hands."""
    n = NAMES[j]
    A = np.eye(3)
    if n.endswith('Shin') or n.endswith('ForeArm') or n.endswith('Leg'):
        c = [k for k in range(NJ) if PARENT[k] == j][0]
        d = J0[c] - J0[j]; d /= np.linalg.norm(d)
        r = 0.74 if n.endswith('Shin') else 0.72 if n.endswith('Leg') else 0.85
        A = r * np.eye(3) + (1 - r) * np.outer(d, d)
    elif 'Foot' in n or 'Toe' in n: A = np.diag([0.9, 0.9, 0.8])
    elif 'Hand' in n: A = 0.84 * np.eye(3)
    return A


AFF = [joint_affine(j) for j in range(NJ)]


def deform(P, SJ, SW):
    out = np.zeros_like(P)
    for k in range(4):
        for j in np.unique(SJ[:, k]):
            m = (SJ[:, k] == j) & (SW[:, k] > 0)
            out[m] += SW[m, k, None] * (J1[j] + (P[m] - J0[j]) @ AFF[j].T)
    return out


PF = deform(P0, SJ0, SW0)          # the whole body, fitted (for the weights the clothes take from it)
dom = SJ0[np.arange(len(SJ0)), SW0.argmax(1)]
dn = np.array([NAMES[j] for j in dom])
hand = np.array(['Hand' in n for n in dn])
fore = np.array([n.endswith('ForeArm') for n in dn])
legs = np.array([('Shin' in n or 'Foot' in n or 'Toe' in n or n.endswith('Leg')) for n in dn])
near_wrist = np.zeros(len(P0), bool)
for s in ('Left', 'Right'): near_wrist |= np.linalg.norm(P0 - J0[I[s + 'Hand']], axis=1) < 0.06
keep = (fore & near_wrist) | (legs & (P0[:, 1] < 0.70) & (P0[:, 1] > 0.062))      # bare legs from under the skirt      # Anny's hands are replaced by drawn mittens
tk = keep[TRI0].all(1)
bi = np.where(keep)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
B = dict(V=PF[bi], T=remap[TRI0[tk]], SJ=SJ0[bi], SW=SW0[bi])
nb = len(bi)
B['col'] = np.tile(C['skin'], (nb, 1)); B['shd'] = np.tile(C['black'], (nb, 1)); B['lin'] = np.tile(C['rim'], (nb, 1))

# shoes: the drawing's small pointed flats (figures.py shoe: a wedge — a straight heel, the top sloping to a low
# point), modelled in place of Anny's feet: a loft from the heel to the toe, flat under, on the foot and toe joints
SHOES = []
for s_, sg in (('Left', 1), ('Right', -1)):
    A_, T_ = J1[I[s_ + 'Foot']], J1[I[s_ + 'ToeEnd']]
    fw = (T_ - A_) * [1, 0, 1]; Lf = np.linalg.norm(fw); fw /= Lf; sd = np.array([fw[2], 0, -fw[0]])
    heel = A_ * [1, 0, 1] - fw * 0.052; Ls = Lf + 0.052 + 0.012
    rows_, cols_ = 30, 24; V_ = []
    for uu in np.linspace(0, 1, rows_):
        w_ = 0.040 * np.interp(uu, [0, 0.06, 0.3, 0.62, 0.88, 1], [0.35, 0.78, 0.92, 1.0, 0.55, 0.03])
        h_ = np.interp(uu, [0, 0.05, 0.36, 0.5, 1], [0.05, 0.068, 0.068, 0.05, 0.008])
        for th in np.linspace(0, 2 * np.pi, cols_, endpoint=False):
            cx_, cy_ = np.sin(th), np.cos(th)
            V_.append(heel + fw * uu * Ls + sd * w_ * np.sign(cx_) * abs(cx_) ** 0.8 + [0, h_ * (0.5 + 0.5 * np.sign(cy_) * abs(cy_) ** (0.9 if cy_ > 0 else 0.35)), 0])
    V_ = np.array(V_); Tt = []
    for r_ in range(rows_ - 1):
        for c_ in range(cols_):
            a0, a1 = r_ * cols_ + c_, r_ * cols_ + (c_ + 1) % cols_; Tt += [[a0, a0 + cols_, a1], [a1, a0 + cols_, a1 + cols_]]
    k0 = len(V_); V_ = np.vstack([V_, V_[:cols_].mean(0), V_[-cols_:].mean(0)])
    for c_ in range(cols_): Tt += [[k0, c_, (c_ + 1) % cols_], [k0 + 1, (rows_ - 1) * cols_ + (c_ + 1) % cols_, (rows_ - 1) * cols_ + c_]]
    Tt = np.array(Tt)
    if (M.vertex_normals(V_, Tt) * (V_ - V_.mean(0))).sum(1).mean() < 0: Tt = Tt[:, ::-1]
    W = np.zeros((len(V_), NJ)); tb = J1[I[s_ + 'ToeBase']]
    wt = smooth((((V_ - tb) * fw).sum(1) + 0.015) / 0.03)
    W[:, I[s_ + 'Foot']] = 1 - wt; W[:, I[s_ + 'ToeBase']] = wt
    SHOES.append(dict(V=V_, T=Tt, W=W, col=np.tile(C['shoe'], (len(V_), 1)), shd=np.tile(C['black'], (len(V_), 1)), lin=np.tile(C['rim'], (len(V_), 1)), side=s_))

# ---------------------------------------------------------------- the head
V0, hP, earm, fw = Hd.build(HBM)       # no eyeballs: the eye is a drawn shape
nh = len(V0)
HT = M.triangulate(hP)
REG = [(37, -2, 34, 30), (-37, -2, 34, 30), (0, 72, 40, 22)]      # where the face layer paints (no outline there)
# proxy normals for the face's shade: the head smoothed into one plain form (the eyes take the head's nearest)
Ah = M.adjacency(nh, hP)
hs = M.smooth(V0[:nh], Ah, np.ones(nh, bool), iters=60, lam=0.5)
pn_h = M.vertex_normals(hs, M.triangulate(hP))
pn = pn_h
Hh = dict(V=V0, T=HT)
nH = len(V0)
xd, yd = V0[:, 0] / K, ydr(V0[:, 1])
# weights: the head, then down the neck to the chest
yde = yd - 18 * smooth((V0[:, 2] - 0.0) / 0.03)      # the chin and the jaw stay with the head
SW = np.zeros((nH, NJ))
sA = smooth((yde - 100) / 50); sB = smooth((yde - 160) / 50); sC = smooth((yde - 215) / 40)
SW[:, I['Head']] = 1 - sA
SW[:, I['Neck2']] = sA * (1 - sB)
SW[:, I['Neck1']] = sA * sB * (1 - sC)
SW[:, I['Chest']] = sA * sB * sC
# the lower face on the jaw (it opens a little with the drawn mouth)
wj = smooth((yd - 74) / 14) * smooth(V0[:, 2] / 0.03) * (1 - smooth((yd - 112) / 14))
wj[nh:] = 0
SW *= (1 - wj)[:, None]; SW[:, I['Jaw']] += wj
Hh['W'] = SW
Hh['col'] = np.tile(C['skin'], (nH, 1)); Hh['shd'] = np.tile(C['black'], (nH, 1)); Hh['lin'] = np.tile(C['rim'], (nH, 1))
Hh['uv'] = np.c_[(xd - X0) / (X1 - X0), 1 - (yd - Y0) / (Y1 - Y0)]
Hh['kind'] = np.full(nH, 1)
Hh['tex'] = ((V0[:, 2] > 0.0) & (yd < 128)).astype(np.uint8)
ow = np.ones(nH)
for cx, cy, rx, ry in REG:
    e = np.sqrt(((xd - cx) / rx) ** 2 + ((yd - cy) / ry) ** 2)
    ow = np.minimum(ow, smooth((e - 1.3) / 0.3))
ow[nh:] = 0
Hh['ow'] = ow
Hh['pn'] = pn; Hh['pw'] = np.ones(nH)      # the face plain; the neck shaded by its own form


# ---------------------------------------------------------------- lofted shells (clothes, hair)
def ring(a, zc, df, db, th, p=2.3):
    s, c = np.sin(th), np.cos(th)
    x = a * np.sign(s) * np.abs(s) ** (2 / p)
    z = zc + np.where(c > 0, df, db) * np.sign(c) * np.abs(c) ** (2 / p)
    return x, z


def grid(rows, cols, closed):
    T = []
    cn = cols if closed else cols - 1
    for r in range(rows - 1):
        for c in range(cn):
            a0, a1 = r * cols + c, r * cols + (c + 1) % cols
            b0, b1 = a0 + cols, a1 + cols
            T += [[a0, b0, a1], [a1, b0, b1]]
    return np.array(T)


def loft(rows, cols=72, closed=True, gap=None):
    """rows: list of (y, a, zc, df, db) in metres; gap: per row the half-angle left open at the front."""
    V = []
    for i, (yy, aa, zc, df, db) in enumerate(rows):
        g = 0 if gap is None else gap[i]
        th = np.linspace(0, 2 * np.pi, cols, endpoint=False) if closed else np.linspace(g, 2 * np.pi - g, cols)
        x, z = ring(aa, zc, df, db, th)
        V += list(np.c_[x, np.full(cols, yy), z])
    return np.array(V), grid(len(rows), cols, closed)


def side_span(name, yy):
    s = D.profile(D.SIDE[name], [yy])[0]; return s


def front_half(name, yy):
    return D.profile(D.FRONT[name], [yy])[0][1]


# the blue top and the skirt, one shell: under the jacket from the neck to the waist, then the skirt swung out to the
# hem. (y, half width in front, front, back) in units: heights from the figure, the shoulders from the turn sheet's
# bust; the figure is drawn in three-quarter, so its widths lie between the front's and the profile's
TORSO = np.array([(204, 60, 44, -46), (232, 100, 50, -52), (262, 120, 56, -56), (D.Y_ARMPIT, 116, 62, -56), (400, 88, 52, -48),
                  (D.Y_WAIST, 62, 43, -43), (D.Y_JHEM, 72, 50, -52), (600, 94, 64, -66), (700, 112, 78, -78), (800, 126, 90, -88), (D.Y_HEM, 142, 104, -100)])
drows = []
for yy in np.unique(np.r_[np.linspace(190, 204, 4), np.arange(210, D.Y_HEM, 8.0), D.Y_HEM, D.Y_TOP - 0.8, D.Y_TOP + 0.8]):
    if yy < 204:   # yoke: from the neck to the top ring
        t_ = (204 - yy) / 14
        a_ = 60 * (1 - t_) + 38 * t_; f_ = 44 * (1 - t_) + 43 * t_; b_ = -46 * (1 - t_) - 46 * t_
        yv = 204 - 14 * (1 - (1 - t_) ** 2)
    else:
        a_, f_, b_ = [np.interp(yy, TORSO[:, 0], TORSO[:, k]) for k in (1, 2, 3)]; yv = yy
    drows.append((y3(yv), u(a_), u((f_ + b_) / 2), u((f_ - b_) / 2), u((f_ - b_) / 2)))
DV, DT = loft(drows, 72, True)
nd = len(DV)
dyd = ydr(DV[:, 1])
Dd = dict(V=DV, T=DT)
Dd['col'] = np.tile(C['dress'], (nd, 1)); Dd['shd'] = np.tile(C['black'], (nd, 1)); Dd['lin'] = np.tile(C['rim'], (nd, 1))
Dd['col'][dyd < D.Y_TOP] = C['skin']        # above the top's neckline: the chest's skin in the jacket's V


def dims_at(rows, yv):
    r = np.array(rows); o = np.argsort(r[:, 0])
    return [np.interp(yv, r[o, 0], r[o, k]) for k in range(1, 5)]


# the jacket: a shell over the top, its yoke round the neck, open as a V from the neck down to where it closes, closed
# to its hem under the waist; sleeves along the arms
krows, kgap = [], []
gapf = lambda yy: np.interp(yy, [186, D.Y_V, D.Y_V + 6], [46, 2.5, 1.2])
JACK = np.array([(240, 140, 62, -70), (D.Y_ARMPIT, 128, 68, -64), (400, 98, 58, -55), (D.Y_WAIST, 70, 50, -50), (D.Y_JHEM, 80, 58, -60)])
for tt in np.linspace(1, 0, 12)[:-1]:         # yoke: neck ring → shoulder ring, a sloping shoulder
    yv = 188 + 52 * (1 - tt) ** 2.0
    a_ = 140 * (1 - tt) ** 0.8 + 42 * (1 - (1 - tt) ** 0.8)
    zf = 62 * (1 - tt) + 46 * tt; zb = -70 * (1 - tt) - 50 * tt
    krows.append((y3(yv), u(a_), u((zf + zb) / 2), u((zf - zb) / 2), u((zf - zb) / 2)))
    kgap.append(np.arcsin(min(gapf(yv) / a_, np.sin(np.radians(78)))))
for yy in np.r_[np.arange(246, D.Y_JHEM, 6.0), D.Y_JHEM]:
    da, dzc, ddf, ddb = dims_at(drows, y3(yy))
    a_, zf_, zb_ = [np.interp(yy, JACK[:, 0], JACK[:, k]) for k in (1, 2, 3)]
    a_ = max(u(a_), da + 0.009)
    zf = max(u(zf_), dzc + ddf + 0.009); zb = min(u(zb_), dzc - ddb - 0.009)
    krows.append((y3(yy), a_, (zf + zb) / 2, (zf - zb) / 2, (zf - zb) / 2))
    kgap.append(np.arcsin(min(gapf(yy) / (a_ / K), 0.97)))
KV, KT = loft(krows, 64, False, kgap)
nk = len(KV)
Kc = dict(V=KV, T=KT, col=np.tile(C['card'], (nk, 1)), shd=np.tile(C['black'], (nk, 1)), lin=np.tile(C['rim'], (nk, 1)))


def tube(path, radii, cols=24):
    """A tube along a polyline (rest), rings across its direction."""
    path = np.asarray(path); V = []
    ref = np.array([0, 0, 1.0])
    for i, p in enumerate(path):
        tg = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]; tg /= np.linalg.norm(tg)
        n1 = ref - tg * (ref @ tg); n1 /= np.linalg.norm(n1); n2 = np.cross(tg, n1)
        for th in np.linspace(0, 2 * np.pi, cols, endpoint=False):
            V.append(p + radii[i] * (np.cos(th) * n1 + np.sin(th) * n2))
    return np.array(V), grid(len(path), cols, True)[:, ::-1]


def catmull(pts, n):
    pts = np.asarray(pts, float); P = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]]); out = []
    for i in range(1, len(P) - 2):
        for s in np.linspace(0, 1, n, endpoint=False):
            p0, p1, p2, p3 = P[i - 1:i + 3]
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-2]); return np.array(out)


# hands: mittens as drawn (fingers together, a small thumb), rigid on the hand, instead of Anny's spread fingers
HANDS = []
for s, sg in (('Left', 1), ('Right', -1)):
    W_ = J1[I[s + 'Hand']]; tip = J1[I[s + 'HandMiddleEnd']]
    d = tip - W_; d /= np.linalg.norm(d)
    acr = J1[I[s + 'HandIndex1']] - J1[I[s + 'HandPinky1']]; acr -= d * (acr @ d); acr /= np.linalg.norm(acr)
    nrm_ = np.cross(d, acr) * sg
    Lh, rows_, cols_ = 0.115, 26, 22
    V_ = []
    for uu in np.linspace(-0.12, 1.0, rows_):
        tip_r = np.sqrt(max(0.0, 1 - max(0.0, (uu - 0.55) / 0.45) ** 2))
        a_ = 0.025 * tip_r * (0.85 + 0.15 * smooth((uu + 0.1) / 0.3)); b_ = 0.0125 * tip_r * (0.9 + 0.1 * smooth(uu / 0.4))
        thumb = 0.010 * np.exp(-((uu - 0.33) / 0.14) ** 2)
        for th in np.linspace(0, 2 * np.pi, cols_, endpoint=False):
            x_ = a_ * np.cos(th) + thumb * max(np.cos(th), 0) ** 2; z_ = b_ * np.sin(th)
            V_.append(W_ + d * uu * Lh + acr * x_ + nrm_ * z_)
    V_ = np.array(V_); T_ = grid(rows_, cols_, True)
    if (M.vertex_normals(V_, T_) * (V_ - V_.mean(0))).sum(1).mean() < 0: T_ = T_[:, ::-1]
    W = np.zeros((len(V_), NJ)); W[:, I[s + 'Hand']] = 1
    HANDS.append(dict(V=V_, T=T_, W=W, col=np.tile(C['skin'], (len(V_), 1)), shd=np.tile(C['black'], (len(V_), 1)),
                      lin=np.tile(C['rim'], (len(V_), 1)), side=s))

SL = []
for s in ('Left', 'Right'):
    A_, E_, W_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']], J1[I[s + 'Hand']]
    d1 = (E_ - A_) / np.linalg.norm(E_ - A_); d2 = (W_ - E_) / np.linalg.norm(W_ - E_)
    path = catmull([A_ - d1 * 0.02, (A_ + E_) / 2, E_, W_ + d2 * 0.01], 10)
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]; L /= L[-1]
    radii = np.interp(L, [0, 0.12, 0.5, 0.9, 1.0], [0.028, 0.034, 0.030, 0.026, 0.027])      # a narrow sleeve, as drawn
    V_, T_ = tube(path, radii)
    SL.append(dict(V=V_, T=T_, col=np.tile(C['card'], (len(V_), 1)), shd=np.tile(C['black'], (len(V_), 1)),
                   lin=np.tile(C['rim'], (len(V_), 1)), side=s))


# ---------------------------------------------------------------- weights for what is built here
FT = cKDTree(PF)


def transfer(V, k=6):
    dd, ii = FT.query(V, k)
    w = 1 / (dd + 1e-3) ** 2; w /= w.sum(1, keepdims=True)
    W = np.zeros((len(V), NJ))
    for c in range(k):
        for q in range(4): np.add.at(W, (np.arange(len(V)), SJ0[ii[:, c], q]), w[:, c] * SW0[ii[:, c], q])
    return W


def skirt_rule(V):
    yd_ = ydr(V[:, 1]); W = np.zeros((len(V), NJ))
    L = 0.55 * smooth((yd_ - 560) / 380)
    side = 1 / (1 + np.exp(-V[:, 0] / 0.035))
    W[:, I['LeftLeg']] = L * side; W[:, I['RightLeg']] = L * (1 - side); W[:, I['Hips']] = 1 - L
    return W


def smooth_w(W, T, n, iters=12):
    polys = [list(t_) for t_ in T]; A = M.adjacency(n, polys)
    return M.smooth(W, A, np.ones(n, bool), iters, 0.5)


def cloth_weights(V, T):
    W = transfer(V)
    uu = smooth((ydr(V[:, 1]) - 500) / 110)[:, None]
    W = (1 - uu) * W + uu * skirt_rule(V)
    return smooth_w(W, T, len(V))


Dd['W'] = cloth_weights(DV, DT)
Kc['W'] = cloth_weights(KV, KT)
for S_ in SL:
    W = transfer(S_['V'])
    # a sleeve belongs to its own arm only (the nearest skin under the armpit may be the chest's)
    side = S_['side']; arm = set(under(I[side + 'Shoulder']))
    tr = np.array([j in arm for j in range(NJ)])
    top = smooth((np.linalg.norm(S_['V'] - J1[I[side + 'Arm']], axis=1) - 0.0) / 0.06)
    Wa = W * tr; Wa /= Wa.sum(1, keepdims=True) + 1e-9
    S_['W'] = smooth_w(Wa * top[:, None] + W * (1 - top[:, None]), S_['T'], len(S_['V']))
BW = np.zeros((nb, NJ))
for q in range(4): np.add.at(BW, (np.arange(nb), B['SJ'][:, q]), B['SW'][:, q])
B['W'] = BW

# ---------------------------------------------------------------- the hair (hair.py)
import hair as HR  # noqa: E402
hP_ne = [p for p in hP if not earm[p].any()]
Hr = HR.build(dict(head=(V0[:nh], M.triangulate(hP_ne)), card=krows, C=C, J1=J1, I=I, NJ=NJ))
Hr['kind'] = np.full(len(Hr['V']), 2)

# ---------------------------------------------------------------- one pack
pieces = [('body', B), ('head', Hh), ('dress', Dd), ('cardigan', Kc)] + \
         [('hand' + h_['side'], h_) for h_ in HANDS] + [('shoe' + h_['side'], h_) for h_ in SHOES] + \
         [('sleeve' + S_['side'], S_) for S_ in SL] + [('hair', Hr)]
Vs, Ts, Ws, cols, shds, lins, ows, uvs, texs, pns, pws, two, bands, kinds = [], [], [], [], [], [], [], [], [], [], [], [], [], []
base = 0; ranges = {}; tbase = 0; tranges = {}
for name, p in pieces:
    n = len(p['V'])
    Vs.append(p['V']); Ts.append(p['T'] + base); Ws.append(p['W'])
    cols.append(p['col']); shds.append(p['shd']); lins.append(p['lin'])
    ows.append(p.get('ow', np.ones(n))); bands.append(p.get('band', -np.ones(n))); uvs.append(p.get('uv', np.zeros((n, 2))))
    texs.append(p.get('tex', np.zeros(n))); pns.append(p.get('pn', np.zeros((n, 3)))); pws.append(p.get('pw', np.zeros(n)))
    kinds.append(p.get('kind', np.zeros(n)))
    two.append(np.full(n, 1 if name in ('cardigan', 'hair', 'dress') or name.startswith('sleeve') else 0))
    ranges[name] = [base, base + n]; tranges[name] = [tbase, tbase + len(p['T'])]; base += n; tbase += len(p['T'])
V = np.vstack(Vs); W = np.vstack(Ws); N = len(V)
# every vertex's place in the head's own frame, head units (x to the character's left, y down from the eye line + 12,
# z forward from the neck's axis): the shader draws the head's and the hair's designed black shapes there
hp = np.c_[V[:, 0] / K / D.HS, ydr(V[:, 1]) / D.HS + D.EYE, V[:, 2] / K / D.HS]
W = np.maximum(W, 0)
order = np.argsort(-W, 1)[:, :4]
SJ = order.astype(np.uint8); SWt = np.take_along_axis(W, order, 1); SWt /= SWt.sum(1, keepdims=True)
pj = SJ[:, 0].astype(np.float32)
pack.save(os.path.join(OUT, 'anya.json'),
          dict(format='r1/character', version=1, id='anya-s15', label={'ru': 'Аня, нуар'}, faces='.', skinning='cor',
               source='Anny moood-woman (engine) + Human Base Meshes stylised head (CC0) + shells from the drawing',
               pieces=ranges, trianglePieces=tranges),
          dict(positions=V.astype(np.float32).ravel(), triangles=np.vstack(Ts).astype(np.uint32).ravel(),
               skinJoints=SJ, skinWeights=SWt.astype(np.float32), joints=J1.astype(np.float32).ravel(), frames=FR.ravel(),
               col=np.vstack(cols).astype(np.uint8), shd=np.vstack(shds).astype(np.uint8), lin=np.vstack(lins).astype(np.uint8),
               ow=(np.clip(np.concatenate(ows), 0, 1) * 255).astype(np.uint8), uv=np.vstack(uvs).astype(np.float32),
               tex=np.concatenate(texs).astype(np.uint8), pn=np.vstack(pns).astype(np.float32),
               pw=(np.clip(np.concatenate(pws), 0, 1) * 255).astype(np.uint8), pj=pj, two=np.concatenate(two).astype(np.uint8), band=np.concatenate(bands).astype(np.float32),
               hp=hp.astype(np.float32), kind=np.concatenate(kinds).astype(np.uint8)))
print('vertices', N, 'triangles', sum(len(t_) for t_ in Ts), {k: v[1] - v[0] for k, v in ranges.items()})
