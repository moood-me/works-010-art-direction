"""Кира in 3D: builds the character pack the viewer (web/char.js) and the engine take.
  python3 build.py outdir
Bases: Anny's girl body (engine/data/bodies/moood-girl: the SOMA skeleton and the weights of the trunk), Blender's
Human Base Meshes stylised head (CC0; hbm_export.py) fitted to the drawing (head.py). The hoodie, its hood and pocket,
the sleeves, the legs, the boots, the headphones and the hair are built here from the drawing's front and profile
(shapes.py: styles/s3-graphic/tools/kira.py). The slouch is in the rest itself: the legs slant back, the trunk leans
back from the hips, the neck goes forward and the head is pitched down, as the profile is drawn — the joints stand
there, the frames are not touched, so Kimodo's motions carry the slouch along. The face is drawn by web/face.js."""
import os, sys
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M, head as Hd, drawing as D, shapes as VW

K = D.K
CACHE = '/home/user/cache/to3d-r18-s3-kira'
OUT = sys.argv[1] if len(sys.argv) > 1 else CACHE + '/out'
HBM = CACHE + '/hbm_head.npz'
os.makedirs(OUT, exist_ok=True)

y3 = lambda yd: (D.FLOOR - np.asarray(yd, float)) * K
ydr = lambda y: D.FLOOR - np.asarray(y, float) / K
u = lambda v: np.asarray(v, float) * K                     # drawing units → metres
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))
lean = VW.lean_z                                           # how far back the leaned trunk is at a height (units)


def rgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


C = {k: rgb(v) for k, v in VW.C.items()}

# the head's place in the figure: built upright in its own units (as if its eye line were the figure's y=0), then
# pitched down about its neck point and pushed forward and down
_ph = np.radians(VW.PITCH); _piv = np.array([0, y3(VW.PIVOT_Y), 0]); _sh = np.array([0, -u(VW.HEAD_DY), u(VW.HEAD_DZ)])
_R = np.array([[1, 0, 0], [0, np.cos(_ph), -np.sin(_ph)], [0, np.sin(_ph), np.cos(_ph)]])
place = lambda V: (np.asarray(V, float) - _piv) @ _R.T + _piv + _sh
turn = lambda N: np.asarray(N, float) @ _R.T
hp = lambda x, y, z: place([[u(x), y3(y), u(z)]])[0]       # a point given in the head's units

# ---------------------------------------------------------------- skeleton and Anny's body
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body('moood-girl')
P0 = a['positions'].reshape(-1, 3).astype(float); J0 = a['joints'].reshape(-1, 3).astype(float)
FR = a['frames'].reshape(-1, 4).astype(np.float32)
SJ0 = t['skinJoints'].reshape(-1, 4).astype(np.int64); SW0 = t['skinWeights'].reshape(-1, 4).astype(float)
dz = -J0[I['Hips'], 2]
P0[:, 2] += dz; J0[:, 2] += dz


def under(j):
    out, st = [], [j]
    while st:
        k = st.pop(); out.append(k); st += list(np.where(PARENT == k)[0])
    return out


# the joints at the drawing's places: the slouch
J1 = J0.copy()
for n, yy in (('Hips', 640), ('Spine1', 566), ('Spine2', 476), ('Chest', 376)):
    J1[I[n]] = [0, y3(yy), u(lean(yy))]
J1[I['Neck1']] = [0, y3(206), u(-30)]
J1[I['Neck2']] = [0, y3(164), u(6)]
J1[I['Head']] = hp(0, 100, 0)
J1[I['HeadEnd']] = hp(0, -126, 0)
J1[I['Jaw']] = hp(0, 34, -20)
ARM, FORE, HAND = 206, 206, 72            # drawing units: shoulder to elbow, elbow to wrist, wrist to fingertips
SHX, LEGX = 136, (52, 61, 65)             # the shoulders' and the legs' places across (hip, knee, ankle)
for s, sg in (('Left', 1), ('Right', -1)):
    J1[I[s + 'Eye']] = hp(sg * 38, 0, 50)
    J1[I[s + 'Shoulder']] = [sg * u(22), y3(206), u(lean(206))]
    J1[I[s + 'Arm']] = [sg * u(SHX), y3(216), u(lean(216) + 6)]
    for n, L in (('ForeArm', ARM), ('Hand', FORE)):
        j = I[s + n]; d = J0[j] - J0[PARENT[j]]; J1[j] = J1[PARENT[j]] + d / np.linalg.norm(d) * u(L)
    kh = u(HAND) / np.linalg.norm(J0[I[s + 'HandMiddleEnd']] - J0[I[s + 'Hand']])
    for j in under(I[s + 'Hand'])[1:]:
        J1[j] = J1[PARENT[j]] + kh * (J0[j] - J0[PARENT[j]])
    J1[I[s + 'Leg']] = [sg * u(LEGX[0]), y3(640), u(-2)]
    J1[I[s + 'Shin']] = [sg * u(LEGX[1]), y3(958), u(-17)]
    J1[I[s + 'Foot']] = [sg * u(LEGX[2]), y3(1284), u(-57)]
    J1[I[s + 'ToeBase']] = [sg * u(LEGX[2]), y3(1336), u(-57 + 62)]
    J1[I[s + 'ToeEnd']] = [sg * u(LEGX[2]), y3(1336), u(-57 + 104)]


def deform(P, SJ, SW):
    """The body after its joints: each vertex moves with its joints (their moves blended by Anny's weights)."""
    out = np.zeros_like(P)
    for k in range(4):
        for j in np.unique(SJ[:, k]):
            m = (SJ[:, k] == j) & (SW[:, k] > 0)
            out[m] += SW[m, k, None] * (J1[j] + (P[m] - J0[j]))
    return out


PF = deform(P0, SJ0, SW0)          # the whole body on the new joints (the trunk's clothes take their weights from it)
dom = SJ0[np.arange(len(SJ0)), SW0.argmax(1)]
dn = np.array([NAMES[j] for j in dom])
is_arm = np.array([any(k in n for k in ('Arm', 'Hand')) for n in dn])
is_leg = np.array([any(k in n for k in ('Leg', 'Shin', 'Foot', 'Toe')) for n in dn])

# ---------------------------------------------------------------- the head (upright, then placed)
hv, hP, d = Hd.load(HBM)
eL, eR = Hd.conv(d['L_v']), Hd.conv(d['R_v'])
EAR = dict(root=(84, 14, -14), h=46, out=4)
(hv2, eL2, eR2), earw = Hd.fit(hv, hP, (eL, eR), ear=EAR)
REG = [(38, 0, 30, 32), (-38, 0, 30, 32), (0, 82, 34, 16)]
V0 = Hd.flatten(np.vstack([hv2, eL2, eR2]), REG, front_min=0.02)
nh = len(hv2)
HT = np.vstack([M.triangulate(hP), M.triangulate(M.polys_of(d['L_fs'], d['L_f'])) + nh,
                M.triangulate(M.polys_of(d['R_fs'], d['R_f'])) + nh + len(eL2)])
Ah = M.adjacency(nh, hP)
hs = M.smooth(V0[:nh], Ah, np.ones(nh, bool), iters=60, lam=0.5)
pn_h = M.vertex_normals(hs, M.triangulate(hP))
pn = np.vstack([pn_h, pn_h[cKDTree(V0[:nh]).query(V0[nh:])[1]]])
nH = len(V0)
xd, yd = V0[:, 0] / K, ydr(V0[:, 1])
Hh = dict(V=place(V0), T=HT)
yde = yd - 18 * smooth(V0[:, 2] / 0.03)      # the chin and the jaw stay with the head
SW = np.zeros((nH, NJ))
sA = smooth((yde - 96) / 40); sB = smooth((yde - 128) / 34); sC = smooth((yde - 156) / 20)
SW[:, I['Head']] = 1 - sA
SW[:, I['Neck2']] = sA * (1 - sB)
SW[:, I['Neck1']] = sA * sB * (1 - sC)
SW[:, I['Chest']] = sA * sB * sC
wj = smooth((yd - 78) / 14) * smooth(V0[:, 2] / 0.03) * (1 - smooth((yd - 112) / 14))
wj[nh:] = 0
SW *= (1 - wj)[:, None]; SW[:, I['Jaw']] += wj
Hh['W'] = SW
Hh['col'] = np.tile(C['skin'], (nH, 1)); Hh['shd'] = np.tile(C['shade'], (nH, 1)); Hh['lin'] = np.tile(C['line'], (nH, 1))
FX0, FX1, FY0, FY1 = -120.0, 120.0, -130.0, 130.0          # the face layer's box (web/face.js)
Hh['uv'] = np.c_[(xd - FX0) / (FX1 - FX0), 1 - (yd - FY0) / (FY1 - FY0)]
Hh['tex'] = ((V0[:, 2] > 0.0) & (yd < 122) & (abs(xd) < 86)).astype(np.uint8)
ow = np.ones(nH)
for cx, cy, rx, ry in REG:
    e = np.sqrt(((xd - cx) / rx) ** 2 + ((yd - cy) / ry) ** 2)
    ow = np.minimum(ow, smooth((e - 1.3) / 0.3))
ow[nh:] = 0
Hh['ow'] = ow
Hh['pn'] = turn(pn); Hh['pw'] = (1 - smooth((yd - 95) / 30))      # the face plain; the neck shaded by its own form


# ---------------------------------------------------------------- lofted shells
def ring(a, zc, df, db, th, p=2.3):
    s, c = np.sin(th), np.cos(th)
    x = a * np.sign(s) * np.abs(s) ** (2 / p)
    z = zc + np.where(c > 0, df, db) * np.sign(c) * np.abs(c) ** (2 / p)
    return x, z


def grid(rows, cols, closed=True):
    T = []
    cn = cols if closed else cols - 1
    for r in range(rows - 1):
        for c in range(cn):
            a0, a1 = r * cols + c, r * cols + (c + 1) % cols
            b0, b1 = a0 + cols, a1 + cols
            T += [[a0, b0, a1], [a1, b0, b1]]
    return np.array(T)


def outward(V, T):
    return T if (M.vertex_normals(V, T) * (V - V.mean(0))).sum(1).mean() > 0 else T[:, ::-1]


def loft(rows, cols=72, cx=0.0, cap=False, p=2.3):
    """rows: list of (y, a, zf, zb) in drawing units → a tube of rings in metres, centred at x=cx; cap closes its top."""
    V = []
    for yy, aa, zf, zb in rows:
        thv = np.linspace(0, 2 * np.pi, cols, endpoint=False)
        x, z = ring(aa, (zf + zb) / 2, (zf - zb) / 2, (zf - zb) / 2, thv, p)
        V += list(np.c_[(x + cx) * K, np.full(cols, y3(yy)), z * K])
    V = np.array(V); T = grid(len(rows), cols)
    if cap:
        V = np.vstack([V, V[:cols].mean(0)]); T = np.vstack([T, [[len(V) - 1, k, (k + 1) % cols] for k in range(cols)]])
    return V, outward(V, T)


def piece(V, T, col, shd, lin, **kw):
    n = len(V)
    return dict(V=V, T=T, col=np.tile(C[col], (n, 1)), shd=np.tile(C[shd], (n, 1)), lin=np.tile(C[lin], (n, 1)), **kw)


def onjoints(n, pairs):
    W = np.zeros((n, NJ))
    for j, w in pairs: W[:, I[j]] += w
    return W


def tube(path, radii, cols=24, ref=(0, 0, 1.0)):
    """A tube along a polyline (rest), rings across its direction."""
    path = np.asarray(path); V = []
    ref = np.array(ref, float)
    for i, p in enumerate(path):
        tg = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]; tg /= np.linalg.norm(tg)
        n1 = ref - tg * (ref @ tg); n1 /= np.linalg.norm(n1); n2 = np.cross(tg, n1)
        for thv in np.linspace(0, 2 * np.pi, cols, endpoint=False):
            V.append(p + radii[i] * (np.cos(thv) * n1 + np.sin(thv) * n2))
    V = np.array(V)
    return V, outward(V, grid(len(path), cols))


half = lambda d_, yy: D.profile(d_, [yy])[0][1]


def side_leaned(d_, yy):
    """A profile shape of the upper body at figure height yy, leaned back with the trunk: (back, front)."""
    s_ = D.profile(d_, [yy])[0]
    return s_ + lean(yy)


# the hoodie: big and boxy; the front view's width, the profile's depth leaned back; a darker hem band
hrows = [(172, 62, 40 + lean(172), -52 + lean(172))]
for yy in np.r_[np.arange(180, 640, 10.0), 640]:
    s_ = side_leaned(VW.HOODIE_S, yy); hrows.append((yy, half(VW.HOODIE_F, yy), s_[1], s_[0]))
HV, HT_ = loft(hrows, 84)
Hd_ = piece(HV, HT_, 'hood', 'hoodS', 'hoodL')
hyd = ydr(HV[:, 1])
Hd_['col'][hyd > 606] = C['hoodS']; Hd_['shd'][hyd > 606] = rgb('#2f1c32')
Av = M.adjacency(len(HV), [list(t_) for t_ in HT_])
Hd_['pn'] = M.vertex_normals(M.smooth(HV, Av, np.ones(len(HV), bool), iters=10), HT_); Hd_['pw'] = np.full(len(HV), 0.6)


def hoodie_front(x, yy):
    """The hoodie's front surface (drawing units z) at x, height yy."""
    r_ = np.array(hrows); a_ = np.interp(yy, r_[:, 0], r_[:, 1]); zf = np.interp(yy, r_[:, 0], r_[:, 2]); zb = np.interp(yy, r_[:, 0], r_[:, 3])
    return (zf + zb) / 2 + (zf - zb) / 2 * np.clip(1 - np.abs(x / a_) ** 2.3, 0, 1) ** (1 / 2.3)


# the hood lying on the back and the shoulders: a closed cushion (the neck comes out in front of it)
orows = []
for yy in np.r_[94, 97, np.arange(102, 204, 8.0)]:
    f_ = half(VW.HOOD_F, max(yy, 99)); s_ = side_leaned(VW.HOOD_S, max(yy, 101))
    k_ = np.sqrt(np.clip((yy - 92) / 12, 0.02, 1))                       # rounded shut at the top
    c_ = (s_[0] + s_[1]) / 2
    orows.append((yy, f_ * k_, c_ + (s_[1] - c_) * k_, c_ + (s_[0] - c_) * k_))
OV, OT = loft(orows, 64, cap=True)
Ho = piece(OV, OT, 'hood', 'hoodS', 'hoodL')

# the pocket: a patch raised off the hoodie's front, its shape the drawn one
pk = D.sample(VW.POCKET_F)
gy_, gu = np.meshgrid(np.linspace(452, 598, 14), np.linspace(-1, 1, 25), indexing='ij')
pw_ = np.array([(lambda s_: s_[1] if s_ else 74.0)(D.span(pk, float(np.clip(y_, 454, 596)))) for y_ in gy_[:, 0]])
px = gu * pw_[:, None]
edge = np.minimum(np.minimum(1 - np.abs(gu), (gy_ - 452) / 146 * 6), (598 - gy_) / 146 * 6)
pz = hoodie_front(px, gy_) + 1.5 + 6.0 * smooth(edge / 0.16)
KV = np.c_[u(px.ravel()), y3(gy_.ravel()), u(pz.ravel())]; KT = grid(14, 25, False)
if M.vertex_normals(KV, KT)[:, 2].mean() < 0: KT = KT[:, ::-1]
Pk = piece(KV, KT, 'hood', 'hoodS', 'hoodL')

# sleeves: long and wide, down over the hand to the knuckles; a darker cuff; the cap at the shoulder round
SL, HANDS = [], []
for s, sg in (('Left', 1), ('Right', -1)):
    A_, E_, W_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']], J1[I[s + 'Hand']]
    d1, d2 = (E_ - A_) / u(ARM), (W_ - E_) / u(FORE)
    ts = np.r_[-38, -35, -29, -20, -10, np.linspace(0, ARM + FORE + 26, 34)]
    path = [A_ + d1 * u(t_) if t_ < ARM else E_ + d2 * u(t_ - ARM) for t_ in ts]
    rr = np.interp(ts, [-38, -35, -29, -20, -10, 0, 60, ARM, ARM + FORE, ARM + FORE + 26], [3, 14, 24, 33, 39, 42, 42, 40, 37.5, 37])
    V_, T_ = tube(path, u(rr), 28)
    tt = np.repeat(ts, 28); e = smooth((tt - ARM + 30) / 60); cap = np.clip(-tt / 38, 0, 1) * 0.5
    p_ = piece(V_, T_, 'hood', 'hoodS', 'hoodL', side=s,
               W=onjoints(len(V_), [(s + 'Arm', (1 - e) * (1 - cap)), (s + 'Shoulder', cap), (s + 'ForeArm', e)]))
    cuff = tt > ARM + FORE - 4
    p_['col'][cuff] = C['hoodS']; p_['shd'][cuff] = rgb('#2f1c32')
    SL.append(p_)
    # the hand: a mitten (fingers together, a small thumb), rigid on the hand; only the fingers peep out of the sleeve
    tip = J1[I[s + 'HandMiddleEnd']]
    d_ = tip - W_; d_ /= np.linalg.norm(d_)
    acr = J1[I[s + 'HandIndex1']] - J1[I[s + 'HandPinky1']]; acr -= d_ * (acr @ d_); acr /= np.linalg.norm(acr)
    nrm_ = np.cross(d_, acr) * sg
    Lh, rows_, cols_ = u(HAND), 22, 22
    V_ = []
    for uu in np.linspace(-0.16, 1.0, rows_):
        tip_r = np.sqrt(max(0.0, 1 - max(0.0, (uu - 0.5) / 0.5) ** 2))
        a_ = u(25) * tip_r * (0.86 + 0.14 * smooth((uu + 0.1) / 0.3)); b_ = u(14) * tip_r * (0.92 + 0.08 * smooth(uu / 0.4))
        thumb = u(9) * np.exp(-((uu - 0.3) / 0.16) ** 2)
        for thv in np.linspace(0, 2 * np.pi, cols_, endpoint=False):
            x_ = a_ * np.cos(thv) + thumb * max(np.cos(thv), 0) ** 2; z_ = b_ * np.sin(thv)
            V_.append(W_ + d_ * uu * Lh + acr * x_ + nrm_ * z_)
    V_ = np.array(V_); T_ = outward(V_, grid(rows_, cols_))
    HANDS.append(piece(V_, T_, 'skin', 'shade', 'line', side=s, W=onjoints(len(V_), [(s + 'Hand', 1)])))

# legs: narrow trousers — thin tapering tubes along the bones; heavy boots: a shaft round the ankle, the foot rigid,
# a thick sole (cut by height in the shader), four acid laces across the shaft's front
LEGS, BOOTS = [], []
ANK = 1284.0
for s, sg in (('Left', 1), ('Right', -1)):
    H_, K_, F_ = J1[I[s + 'Leg']], J1[I[s + 'Shin']], J1[I[s + 'Foot']]
    axis = lambda yy: H_ + (K_ - H_) * (yy - 640) / 318 if yy < 958 else K_ + (F_ - K_) * (yy - 958) / 326
    ys = np.linspace(604, 1240, 40)
    rr = np.interp(ys, [604, 640, 958, 1240], [45, 44, 31, 26])
    V_, T_ = tube([axis(yy) for yy in ys], u(rr), 22)
    yy = np.repeat(ys, 22); e = smooth((yy - 958 + 30) / 60); top = smooth((640 - yy) / 40) * 0.5
    LEGS.append(piece(V_, T_, 'trou', 'trouS', 'trouL', side=s,
                      W=onjoints(len(V_), [(s + 'Leg', (1 - e) * (1 - top)), ('Hips', (1 - e) * top), (s + 'Shin', e)])))
    ys = np.linspace(ANK - 88, ANK + 22, 12)
    rr = np.interp(ys, [ANK - 88, ANK - 84, ANK - 40, ANK + 22], [33, 36, 37, 40])
    V_, T_ = tube([axis(yy) for yy in ys], u(rr), 26)
    w = smooth((np.repeat(ys, 26) - ANK + 34) / 40)
    p_ = piece(V_, T_, 'boot', 'boot', 'bootL', side=s, W=onjoints(len(V_), [(s + 'Shin', 1 - w), (s + 'Foot', w)]))
    p_['shd'][:] = rgb('#17151a')
    BOOTS.append(('shaft' + s, p_))
    # the laces
    LV, LT = [], []
    for k_, yl in enumerate((ANK - 66, ANK - 48, ANK - 30, ANK - 12)):
        c_ = axis(yl); r_ = u(np.interp(yl, ys, rr)) + 0.0025
        g_y, g_a = np.meshgrid([yl - 3.2, yl + 3.2], np.radians(np.linspace(-34, 34, 9)), indexing='ij')
        LT += list(grid(2, 9, False) + len(LV))
        LV += list(np.c_[c_[0] + r_ * np.sin(g_a.ravel()), y3(g_y.ravel()), c_[2] + r_ * np.cos(g_a.ravel())])
    LV, LT = np.array(LV), np.array(LT)
    if M.vertex_normals(LV, LT)[:, 2].mean() < 0: LT = LT[:, ::-1]
    wl = smooth((ydr(LV[:, 1]) - ANK + 34) / 40)
    p_ = piece(LV, LT, 'lime', 'limeS', 'lime', side=s, W=onjoints(len(LV), [(s + 'Shin', 1 - wl), (s + 'Foot', wl)]))
    BOOTS.append(('laces' + s, p_))
    # the foot of the boot: a loft along the foot
    cx, z0 = sg * LEGX[2], -57.0
    zs = np.array([-45, -43, -36, -18, 4, 30, 56, 80, 98, 108, 111])
    aw = np.interp(zs, [-45, -43, -36, 0, 60, 90, 108, 111], [1, 18, 34, 41, 44, 40, 18, 1])
    top = np.interp(zs, [-45, -43, -36, -10, 30, 44, 64, 90, 108, 111], [40, 62, 84, 90, 88, 66, 54, 46, 34, 22])
    V_ = []
    for z_, a_, t_ in zip(zs, aw, top):
        thv = np.linspace(0, 2 * np.pi, 28, endpoint=False)
        sole = 20.0
        x, yv = ring(a_, sole, t_ - sole, sole if a_ > 2 else 2, thv, p=2.8)
        V_ += list(np.c_[(x + cx) * K, np.clip(yv, 0, None) * K, np.full(28, (z_ + z0) * K)])
    V_ = np.array(V_); T_ = grid(len(zs), 28)
    V_ = np.vstack([V_, V_[:28].mean(0), V_[-28:].mean(0)]); nv = len(V_) - 2
    caps = [[nv, k, (k + 1) % 28] for k in range(28)] + [[nv + 1, nv - 28 + (k + 1) % 28, nv - 28 + k] for k in range(28)]
    T_ = outward(V_, np.vstack([T_, caps]))
    p_ = piece(V_, T_, 'boot', 'boot', 'bootL', side=s, W=onjoints(len(V_), [(s + 'Foot', 1)])); p_['shd'][:] = rgb('#17151a')
    p_['band'] = 2000 + V_[:, 1] / K
    BOOTS.append(('boot' + s, p_))

# the headphones round the neck: the cups lie on the hood's front, the band goes behind the neck — the acid accent
PHONES = []
orr = np.array(orows)
for sg in (1, -1):
    yc = 176.0; a_, zf, zb = [np.interp(yc, orr[:, 0], orr[:, k]) for k in (1, 2, 3)]
    xc = sg * 76.0
    zc = (zf + zb) / 2 + (zf - zb) / 2 * (1 - abs(xc / a_) ** 2.3) ** (1 / 2.3)
    cen = np.array([u(xc), y3(yc), u(zc - 4)]); nrm = np.array([sg * 0.5, 0.18, 0.85]); nrm /= np.linalg.norm(nrm)
    e1 = np.cross([0, 1, 0], nrm); e1 /= np.linalg.norm(e1); e2 = np.cross(nrm, e1)
    V_ = []; prof = [(0, 31, 37), (9, 32, 38), (15, 29, 35), (16, 24, 30), (19, 22, 28), (21, 12, 16), (21.5, 0.5, 0.5)]   # out, rx, ry
    for o_, rx, ry in prof:
        for thv in np.linspace(0, 2 * np.pi, 28, endpoint=False):
            V_.append(cen + nrm * u(o_) + e1 * u(rx) * np.cos(thv) + e2 * u(ry) * np.sin(thv))
    V_ = np.array(V_); T_ = outward(V_, grid(len(prof), 28))
    p_ = piece(V_, T_, 'boot', 'boot', 'bootL'); p_['shd'][:] = rgb('#17151a')
    lime = np.arange(len(V_)) >= 3 * 28
    p_['col'][lime] = C['lime']; p_['shd'][lime] = C['limeS']; p_['lin'][lime] = C['limeL']
    p_['col'][np.arange(len(V_)) >= 5 * 28] = C['limeS']
    PHONES.append(('cup' + ('Left' if sg > 0 else 'Right'), p_))
    PHONES[-1][1]['cen'] = cen
cL, cR = PHONES[0][1]['cen'], PHONES[1][1]['cen']
ang = np.linspace(0, np.pi, 26)
nb_ = np.array([0, y3(150), u(lean(150) - 26)])                    # behind the neck
path = [[cL[0] * np.cos(a_), cL[1] + (nb_[1] - cL[1]) * np.sin(a_) ** 0.7, cL[2] + (nb_[2] - u(40) - cL[2]) * np.sin(a_)] for a_ in ang]
V_, T_ = tube(path, np.full(len(path), u(7.5)), 12, ref=(0, 1.0, 0))
PHONES.append(('band', piece(V_, T_, 'boot', 'boot', 'bootL')))
for n_, p_ in PHONES: p_['W'] = onjoints(len(p_['V']), [('Chest', 0.75), ('Neck1', 0.25)])

# the drawstrings: two cords down the chest
CORDS = []
for pts in (((-18, 236), (-20, 270), (-16, 300), (-22, 330)), ((18, 236), (22, 264), (18, 292), (24, 318))):
    pts = np.array(pts, float); tt = np.linspace(0, 1, 14)
    xs = np.interp(tt, np.linspace(0, 1, 4), pts[:, 0]); ys_ = np.interp(tt, np.linspace(0, 1, 4), pts[:, 1])
    path = np.c_[u(xs), y3(ys_), u(hoodie_front(xs, ys_) + 2.5)]
    V_, T_ = tube(path, np.full(14, u(2.6)), 8)
    p_ = piece(V_, T_, 'cord', 'cord', 'cord'); p_['shd'][:] = rgb('#a99fae'); p_['lin'][:] = rgb('#6d6474')
    CORDS.append(p_)


# ---------------------------------------------------------------- weights for what lies on the trunk
def transfer(V, allow, k=6):
    idx = np.where(allow)[0]; dd, ii = cKDTree(PF[idx]).query(V, k); ii = idx[ii]
    w = 1 / (dd + 1e-3) ** 2; w /= w.sum(1, keepdims=True)
    W = np.zeros((len(V), NJ))
    for c in range(k):
        for q in range(4): np.add.at(W, (np.arange(len(V)), SJ0[ii[:, c], q]), w[:, c] * SW0[ii[:, c], q])
    return W


def smooth_w(W, T, iters=12):
    A = M.adjacency(len(W), [list(t_) for t_ in T])
    return M.smooth(W, A, np.ones(len(W), bool), iters, 0.5)


def trunk_w(V):
    W = transfer(V, ~is_arm & ~is_leg)
    for sd in ('Left', 'Right'):         # the trunk does not go with the arms: what the skin gave them goes to the chest
        arm = under(I[sd + 'Arm']); W[:, I['Chest']] += W[:, arm].sum(1) + 0.6 * W[:, I[sd + 'Shoulder']]; W[:, arm] = 0; W[:, I[sd + 'Shoulder']] *= 0.4
    hd = [I['Head'], I['Neck2'], I['Jaw']]; W[:, I['Neck1']] += W[:, hd].sum(1); W[:, hd] = 0      # nor with the head
    return W


Hd_['W'] = smooth_w(trunk_w(HV), HT_)
ht = cKDTree(HV)
Ho['W'] = smooth_w(trunk_w(OV) * 0.3 + onjoints(len(OV), [('Chest', 0.7)]), OT, 4)
for p_ in [Pk] + CORDS:
    p_['W'] = Hd_['W'][ht.query(p_['V'])[1]]

# ---------------------------------------------------------------- the hair (hair.py), placed with the head
import hair as HR  # noqa: E402
Hr = HR.build(dict(C=C, I=I, NJ=NJ))
Hr['V'] = place(Hr['V']); Hr['pn'] = turn(Hr['pn'])

# ---------------------------------------------------------------- one pack
pieces = [('leg' + p_['side'], p_) for p_ in LEGS] + BOOTS + [('head', Hh), ('hoodie', Hd_), ('pocket', Pk), ('hood', Ho)] + \
         [('cord%d' % k_, p_) for k_, p_ in enumerate(CORDS)] + [('sleeve' + p_['side'], p_) for p_ in SL] + \
         [('hand' + p_['side'], p_) for p_ in HANDS] + PHONES + [('hair', Hr)]
TWO = ('hoodie', 'sleeve', 'hair', 'pocket', 'laces', 'leg', 'shaft')
Vs, Ts, Ws, cols, shds, lins, ows, uvs, texs, pns, pws, two, bands = [], [], [], [], [], [], [], [], [], [], [], [], []
base = 0; ranges = {}; tbase = 0; tranges = {}
for name, p in pieces:
    n = len(p['V'])
    Vs.append(p['V']); Ts.append(p['T'] + base); Ws.append(p['W'])
    cols.append(p['col']); shds.append(p['shd']); lins.append(p['lin'])
    ows.append(p.get('ow', np.ones(n))); bands.append(p.get('band', -np.ones(n))); uvs.append(p.get('uv', np.zeros((n, 2))))
    texs.append(p.get('tex', np.zeros(n))); pns.append(p.get('pn', np.zeros((n, 3)))); pws.append(p.get('pw', np.zeros(n)))
    two.append(np.full(n, 1 if name.startswith(TWO) else 0))
    ranges[name] = [base, base + n]; tranges[name] = [tbase, tbase + len(p['T'])]; base += n; tbase += len(p['T'])
V = np.vstack(Vs); W = np.vstack(Ws); N = len(V)
W = np.maximum(W, 0)
order = np.argsort(-W, 1)[:, :4]
SJ = order.astype(np.uint8); SWt = np.take_along_axis(W, order, 1); SWt /= SWt.sum(1, keepdims=True)
pj = SJ[:, 0].astype(np.float32)
f01 = lambda c: [round(x / 255, 4) for x in c]
BANDS = [[1999, 2021.0, f01(C['sole']), f01(rgb('#46434b'))]]
pack.save(os.path.join(OUT, 'kira.json'),
          dict(format='r1/character', version=2, id='kira-s3', label={'ru': 'Кира, графичный стиль'}, skinning='cor',
               source='Anny moood-girl (engine) + Human Base Meshes stylised head (CC0) + shells from the drawing',
               pieces=ranges, trianglePieces=tranges, bands=BANDS),
          dict(positions=V.astype(np.float32).ravel(), triangles=np.vstack(Ts).astype(np.uint32).ravel(),
               skinJoints=SJ, skinWeights=SWt.astype(np.float32), joints=J1.astype(np.float32).ravel(), frames=FR.ravel(),
               col=np.vstack(cols).astype(np.uint8), shd=np.vstack(shds).astype(np.uint8), lin=np.vstack(lins).astype(np.uint8),
               ow=(np.clip(np.concatenate(ows), 0, 1) * 255).astype(np.uint8), uv=np.vstack(uvs).astype(np.float32),
               tex=np.concatenate(texs).astype(np.uint8), pn=np.vstack(pns).astype(np.float32),
               pw=(np.clip(np.concatenate(pws), 0, 1) * 255).astype(np.uint8), pj=pj, two=np.concatenate(two).astype(np.uint8), band=np.concatenate(bands).astype(np.float32)))
print('vertices', N, 'triangles', sum(len(t_) for t_ in Ts), {k: v[1] - v[0] for k, v in ranges.items()})
