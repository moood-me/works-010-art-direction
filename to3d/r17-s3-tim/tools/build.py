"""Тим in 3D: builds the character pack the viewer (web/char.js) and the engine take.
  python3 build.py outdir
Bases: Anny's child body (engine/data/bodies/moood-child: the SOMA skeleton and the weights of the trunk; the limbs are tubes on its bones), Blender's
Human Base Meshes stylised head (CC0; hbm_export.py) fitted to the drawing (head.py); the shirt, the shorts, the limbs, the socks,
the sneakers, the mittens and the hair are built here from the drawing's front and profile (views.py, drawing.py); the
face is drawn by web/face.js from the drawing's own parts. Everything is skinned to SOMA's 77 joints, so Kimodo's
motions play on it through the engine."""
import os, sys
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M, head as Hd, drawing as D, views as VW

K = D.K
CACHE = '/home/user/cache/to3d-r17-s3-tim'
OUT = sys.argv[1] if len(sys.argv) > 1 else CACHE + '/out'
HBM = CACHE + '/hbm_head.npz'
os.makedirs(OUT, exist_ok=True)

y3 = lambda yd: (D.FLOOR - np.asarray(yd, float)) * K
ydr = lambda y: D.FLOOR - np.asarray(y, float) / K
u = lambda v: np.asarray(v, float) * K                     # drawing units → metres
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))


def rgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


C = {k: rgb(v) for k, v in VW.C.items()}

# ---------------------------------------------------------------- skeleton and Anny's body
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body('moood-child')
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


# the joints at the drawing's places: a short barrel of a trunk, short legs wide apart, a big head on a short neck,
# the shoulders outside the barrel
J1 = J0.copy()
for n, yy in (('Hips', 396), ('Spine1', 350), ('Spine2', 292), ('Chest', 228), ('Neck1', 142), ('Neck2', 122), ('Head', 100)):
    J1[I[n]] = [0, y3(yy), 0]
J1[I['HeadEnd']] = [0, y3(-106), 0]
J1[I['Jaw']] = [0, y3(52), -0.02]
ARM, FORE, HAND = 96, 96, 54            # drawing units: shoulder to elbow, elbow to wrist, wrist to fingertips
for s, sg in (('Left', 1), ('Right', -1)):
    J1[I[s + 'Eye']] = [sg * u(40), y3(14), u(70)]
    J1[I[s + 'Shoulder']] = [sg * u(24), y3(146), 0]
    J1[I[s + 'Arm']] = [sg * u(136), y3(152), 0]
    for n, L in (('ForeArm', ARM), ('Hand', FORE)):
        j = I[s + n]; d = J0[j] - J0[PARENT[j]]; J1[j] = J1[PARENT[j]] + d / np.linalg.norm(d) * u(L)
    kh = u(HAND) / np.linalg.norm(J0[I[s + 'HandMiddleEnd']] - J0[I[s + 'Hand']])
    for j in under(I[s + 'Hand'])[1:]:
        J1[j] = J1[PARENT[j]] + kh * (J0[j] - J0[PARENT[j]])
    J1[I[s + 'Leg']] = [sg * u(VW.LEGS_X), y3(410), 0]
    J1[I[s + 'Shin']] = [sg * u(VW.LEGS_X), y3(536), 0.004]
    J1[I[s + 'Foot']] = [sg * u(VW.LEGS_X), y3(650), -0.004]
    J1[I[s + 'ToeBase']] = [sg * u(VW.LEGS_X), y3(672), u(44)]
    J1[I[s + 'ToeEnd']] = [sg * u(VW.LEGS_X), y3(672), u(74)]

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

# ---------------------------------------------------------------- the head
hv, hP, d = Hd.load(HBM)
eL, eR = Hd.conv(d['L_v']), Hd.conv(d['R_v'])
EAR = dict(root=(96, 24, -18), h=80, out=36)
(hv2, eL2, eR2), earw = Hd.fit(hv, hP, (eL, eR), ear=EAR)
REG = [(40, 14, 31, 35), (-40, 14, 31, 35), (2, 86, 46, 24)]
V0 = Hd.flatten(np.vstack([hv2, eL2, eR2]), REG, front_min=0.02)
nh = len(hv2)
HT = np.vstack([M.triangulate(hP), M.triangulate(M.polys_of(d['L_fs'], d['L_f'])) + nh,
                M.triangulate(M.polys_of(d['R_fs'], d['R_f'])) + nh + len(eL2)])
# proxy normals for the face's shade: the head smoothed into one plain form (the eyes take the head's nearest)
Ah = M.adjacency(nh, hP)
hs = M.smooth(V0[:nh], Ah, np.ones(nh, bool), iters=60, lam=0.5)
pn_h = M.vertex_normals(hs, M.triangulate(hP))
pn = np.vstack([pn_h, pn_h[cKDTree(V0[:nh]).query(V0[nh:])[1]]])
Hh = dict(V=V0, T=HT)
nH = len(V0)
xd, yd = V0[:, 0] / K, ydr(V0[:, 1])
yde = yd - 14 * smooth(V0[:, 2] / 0.04)      # the chin and the jaw stay with the head
SW = np.zeros((nH, NJ))
sA = smooth((yde - 100) / 26); sB = smooth((yde - 124) / 20); sC = smooth((yde - 138) / 14)
SW[:, I['Head']] = 1 - sA
SW[:, I['Neck2']] = sA * (1 - sB)
SW[:, I['Neck1']] = sA * sB * (1 - sC)
SW[:, I['Chest']] = sA * sB * sC
# the lower face on the jaw (it opens a little with the drawn mouth)
wj = smooth((yd - 84) / 14) * smooth(V0[:, 2] / 0.05) * (1 - smooth((yd - 116) / 12))
wj[nh:] = 0
SW *= (1 - wj)[:, None]; SW[:, I['Jaw']] += wj
Hh['W'] = SW
Hh['col'] = np.tile(C['skin'], (nH, 1)); Hh['shd'] = np.tile(C['shade'], (nH, 1)); Hh['lin'] = np.tile(C['line'], (nH, 1))
FX0, FX1, FY0, FY1 = -120.0, 120.0, -130.0, 130.0          # the face layer's box (web/face.js)
Hh['uv'] = np.c_[(xd - FX0) / (FX1 - FX0), 1 - (yd - FY0) / (FY1 - FY0)]
Hh['tex'] = ((V0[:, 2] > 0.0) & (yd < 124) & (abs(xd) < 100)).astype(np.uint8)
ow = np.ones(nH)
for cx, cy, rx, ry in REG:
    e = np.sqrt(((xd - cx) / rx) ** 2 + ((yd - cy) / ry) ** 2)
    ow = np.minimum(ow, smooth((e - 1.3) / 0.3))
ow[nh:] = 0
Hh['ow'] = ow
earw_all = np.r_[earw, np.zeros(nH - nh)]
Hh['pn'] = pn; Hh['pw'] = (1 - smooth((yd - 100) / 30)) * (1 - np.clip(earw_all * 2, 0, 1))   # the face plain; ears and neck by their own form


# ---------------------------------------------------------------- lofted shells (clothes)
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


def loft(rows, cols=72, cx=0.0):
    """rows: list of (y, a, zf, zb) in drawing units → a closed tube of rings in metres, centred at x=cx."""
    V = []
    for yy, aa, zf, zb in rows:
        thv = np.linspace(0, 2 * np.pi, cols, endpoint=False)
        x, z = ring(aa, (zf + zb) / 2, (zf - zb) / 2, (zf - zb) / 2, thv)
        V += list(np.c_[(x + cx) * K, np.full(cols, y3(yy)), z * K])
    V = np.array(V); T = grid(len(rows), cols)
    return V, outward(V, T)


def piece(V, T, col, shd, lin, **kw):
    n = len(V)
    return dict(V=V, T=T, col=np.tile(C[col], (n, 1)), shd=np.tile(C[shd], (n, 1)), lin=np.tile(C[lin], (n, 1)), **kw)


half = lambda d, yy: D.profile(d, [yy])[0][1]
sidesp = lambda d, yy: D.profile(d, [yy])[0]

# the shirt: the front view's width, the profile's depth; a collar ring at the neck
srows = [(119, 37, 33, -39), (123, 42, 37, -43)]
for yy in np.r_[np.arange(127, 150, 3.0), np.arange(150, 338, 6.0), 338]:
    s_ = sidesp(VW.SHIRT_S, yy); srows.append((yy, half(VW.SHIRT_F, yy), s_[1], s_[0]))
SV, ST = loft(srows, 80)
Sh = piece(SV, ST, 'shirt', 'shirtS', 'shirtL')
syd = ydr(SV[:, 1])
Sh['col'][syd < 126] = C['shirtS']
Sh['band'] = syd.copy()                       # the stripes are cut by the drawing's heights in the shader
Asv = M.adjacency(len(SV), [list(t_) for t_ in ST])
Sh['pn'] = M.vertex_normals(M.smooth(SV, Asv, np.ones(len(SV), bool), iters=10), ST); Sh['pw'] = np.full(len(SV), 0.6)

# the shorts: the trunk's part, then a wide leg each
prow = []
for yy in np.arange(312, 404, 6.0):
    s_ = sidesp(VW.SHORTS_S, max(yy, 317)); prow.append((yy, half(VW.SHORTS_F, max(yy, 317)) - (4 if yy < 330 else 0), s_[1] - 2, s_[0] + 2))
PV, PT = loft(prow, 72)
SHORTS = [piece(PV, PT, 'shorts', 'shortsS', 'shortsL')]
for sg in (1, -1):
    lrow = []
    for yy in np.r_[np.arange(366, 446, 8.0), 446]:
        f = (yy - 366) / 80; s_ = sidesp(VW.SHORTS_S, yy)
        o = half(VW.SHORTS_F, yy); inner = 14 * smooth((yy - 392) / 54) if yy > 392 else 0.0
        lrow.append((yy, (o - inner) / 2 + 1, s_[1] - 3 - 6 * f, s_[0] + 3 + 6 * f, sg * (o + inner) / 2))
    V_ = []
    for yy, aa, zf, zb, cx in lrow:
        thv = np.linspace(0, 2 * np.pi, 56, endpoint=False)
        x, z = ring(aa, (zf + zb) / 2, (zf - zb) / 2, (zf - zb) / 2, thv)
        V_ += list(np.c_[(x + cx) * K, np.full(56, y3(yy)), z * K])
    V_ = np.array(V_); T_ = outward(V_, grid(len(lrow), 56))
    SHORTS.append(piece(V_, T_, 'shorts', 'shortsS', 'shortsL', side='Left' if sg > 0 else 'Right'))


def tube(path, radii, cols=24, flat=1.0):
    """A tube along a polyline (rest), rings across its direction."""
    path = np.asarray(path); V = []
    ref = np.array([0, 0, 1.0])
    for i, p in enumerate(path):
        tg = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]; tg /= np.linalg.norm(tg)
        n1 = ref - tg * (ref @ tg); n1 /= np.linalg.norm(n1); n2 = np.cross(tg, n1)
        for thv in np.linspace(0, 2 * np.pi, cols, endpoint=False):
            V.append(p + radii[i] * (np.cos(thv) * n1 * flat + np.sin(thv) * n2))
    V = np.array(V)
    return V, outward(V, grid(len(path), cols))


def onjoints(n, pairs):
    W = np.zeros((n, NJ))
    for j, w in pairs: W[:, I[j]] += w
    return W


# arms and legs: plain tapering tubes along the bones, as drawn (Anny's limbs are anatomy; the drawing's are sticks);
# their weights are set by the place along the bone: one joint, a soft change at the elbow, the knee, the wrist
LIMBS = []
for s in ('Left', 'Right'):
    A_, E_, W_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']], J1[I[s + 'Hand']]
    d1, d2 = (E_ - A_) / u(ARM), (W_ - E_) / u(FORE)
    ts = np.linspace(14, ARM + FORE + 5, 30)                  # drawing units from the shoulder
    path = [A_ + d1 * u(t_) if t_ < ARM else E_ + d2 * u(t_ - ARM) for t_ in ts]
    V_, T_ = tube(path, u(np.interp(ts, [0, ARM, ARM + FORE], [19.5, 18.5, 17.5])), 20)
    tt = np.repeat(ts, 20); e = smooth((tt - ARM + 16) / 32); w = smooth((tt - ARM - FORE + 8) / 12) * 0.6
    p_ = piece(V_, T_, 'skin', 'shade', 'line', side=s, W=onjoints(len(V_), [(s + 'Arm', 1 - e), (s + 'ForeArm', e * (1 - w)), (s + 'Hand', e * w)]))
    LIMBS.append(('arm' + s, p_))
for s, sg in (('Left', 1), ('Right', -1)):
    H_, K_, F_ = J1[I[s + 'Leg']], J1[I[s + 'Shin']], J1[I[s + 'Foot']]
    ys = np.linspace(414, 662, 34)
    path = [H_ + (K_ - H_) * (yy - 410) / 126 if yy < 536 else K_ + (F_ - K_) * (yy - 536) / 114 for yy in ys]
    rr = np.interp(ys, [414, 440, 536, 640, 662], [28, 27.5, 24.5, 19.5, 19])
    V_, T_ = tube(path, u(rr), 22)
    yy = np.repeat(ys, 22); e = smooth((yy - 536 + 20) / 40); w = smooth((yy - 644) / 14)
    p_ = piece(V_, T_, 'skin', 'shade', 'line', side=s, W=onjoints(len(V_), [(s + 'Leg', 1 - e), (s + 'Shin', e * (1 - w)), (s + 'Foot', e * w)]))
    LIMBS.append(('leg' + s, p_))
    if sg < 0:        # the plaster on the knee: a patch on the leg's own surface
        gy_, ga = np.meshgrid(np.linspace(514, 532, 5), np.radians(np.linspace(-46, 46, 11)), indexing='ij')
        r_ = u(np.interp(gy_, ys, rr)) + 0.0022
        c_ = np.array([path[int(np.argmin(abs(ys - y_)))] for y_ in gy_.ravel()])
        PV_ = np.c_[c_[:, 0] + r_.ravel() * np.sin(ga.ravel()), y3(gy_.ravel()), c_[:, 2] + r_.ravel() * np.cos(ga.ravel())]
        PT_ = grid(5, 11, False)
        if M.vertex_normals(PV_, PT_)[:, 2].mean() < 0: PT_ = PT_[:, ::-1]
        PL = piece(PV_, PT_, 'plaster', 'plaster', 'plaster', W=onjoints(len(PV_), [(s + 'Leg', 1 - smooth((gy_.ravel() - 516) / 40)), (s + 'Shin', smooth((gy_.ravel() - 516) / 40))]))
        PL['lin'][:] = rgb('#b08a55'); PL['shd'][:] = rgb('#dcc28c')

# sleeves: short and wide, from the shoulder to above the elbow; their stripe by the distance along the arm
SL = []
for s in ('Left', 'Right'):
    A_, E_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']]
    d1 = (E_ - A_) / np.linalg.norm(E_ - A_)
    ts = np.r_[-27, -25, -21, -15, -8, np.linspace(0, 64, 8)]
    path = [A_ + d1 * u(t_) for t_ in ts]
    radii = u(np.interp(ts, [-27, -25, -21, -15, -8, 0, 20, 64], [2, 10, 17, 23, 27, 29, 29, 28.5]))
    V_, T_ = tube(path, radii, 28)
    p_ = piece(V_, T_, 'shirt', 'shirtS', 'shirtL', side=s)
    p_['band'] = 148 + np.repeat(ts, 28)       # the stripe at the drawn sleeve's 176…188
    SL.append(p_)

# hands: mittens as drawn (fingers together, a small thumb), rigid on the hand, instead of Anny's fingers
HANDS = []
for s, sg in (('Left', 1), ('Right', -1)):
    W_ = J1[I[s + 'Hand']]; tip = J1[I[s + 'HandMiddleEnd']]
    d_ = tip - W_; d_ /= np.linalg.norm(d_)
    acr = J1[I[s + 'HandIndex1']] - J1[I[s + 'HandPinky1']]; acr -= d_ * (acr @ d_); acr /= np.linalg.norm(acr)
    nrm_ = np.cross(d_, acr) * sg
    Lh, rows_, cols_ = u(HAND), 22, 22
    V_ = []
    for uu in np.linspace(-0.16, 1.0, rows_):
        tip_r = np.sqrt(max(0.0, 1 - max(0.0, (uu - 0.5) / 0.5) ** 2))
        a_ = u(24) * tip_r * (0.86 + 0.14 * smooth((uu + 0.1) / 0.3)); b_ = u(15) * tip_r * (0.92 + 0.08 * smooth(uu / 0.4))
        thumb = u(10) * np.exp(-((uu - 0.3) / 0.16) ** 2)
        for thv in np.linspace(0, 2 * np.pi, cols_, endpoint=False):
            x_ = a_ * np.cos(thv) + thumb * max(np.cos(thv), 0) ** 2; z_ = b_ * np.sin(thv)
            V_.append(W_ + d_ * uu * Lh + acr * x_ + nrm_ * z_)
    V_ = np.array(V_); T_ = outward(V_, grid(rows_, cols_))
    W = np.zeros((len(V_), NJ)); W[:, I[s + 'Hand']] = 1
    HANDS.append(piece(V_, T_, 'skin', 'shade', 'line', side=s, W=W))

# socks (a tube round the ankle, its red stripe cut in the shader) and sneakers (rigid on the foot; the sole by height)
SOCKS, SHOES = [], []
for s, sg in (('Left', 1), ('Right', -1)):
    cx = sg * VW.LEGS_X
    V_, T_ = loft([(yy, 21, 21, -21) for yy in np.linspace(614, 660, 8)], 28, cx)
    p_ = piece(V_, T_, 'sock', 'sock', 'sock', side=s); p_['shd'][:] = rgb('#e2d6c4'); p_['lin'][:] = rgb('#9c8a76')
    p_['band'] = 1000 + (ydr(V_[:, 1]) - 614)
    SOCKS.append(p_)
    zs = np.array([-33, -31, -24, -10, 6, 22, 40, 56, 66, 71, 73])
    aw = np.interp(zs, [-33, -31, -24, 0, 40, 60, 71, 73], [1, 13, 26, 31, 33, 28, 11, 1])
    top = np.interp(zs, [-33, -31, -24, -8, 8, 22, 40, 60, 71, 73], [22, 34, 44, 47, 46, 40, 30, 22, 14, 8])
    V_ = []
    for z_, a_, t_ in zip(zs, aw, top):
        thv = np.linspace(0, 2 * np.pi, 26, endpoint=False)
        sole = 12.0
        x, yv = ring(a_, sole, t_ - sole, sole if a_ > 2 else 2, thv, p=2.6)
        V_ += list(np.c_[(x + cx) * K, np.clip(yv, 0, None) * K, np.full(26, z_ * K)])
    V_ = np.array(V_); T_ = grid(len(zs), 26)
    V_ = np.vstack([V_, V_[:26].mean(0), V_[-26:].mean(0)]); nv = len(V_) - 2
    caps = [[nv, k, (k + 1) % 26] for k in range(26)] + [[nv + 1, nv - 26 + (k + 1) % 26, nv - 26 + k] for k in range(26)]
    T_ = np.vstack([T_, caps]); T_ = outward(V_, T_)
    W = np.zeros((len(V_), NJ)); W[:, I[s + 'Foot']] = 1
    p_ = piece(V_, T_, 'shoe', 'shoe', 'shoeL', side=s, W=W); p_['shd'][:] = rgb('#cfc7b8')
    p_['band'] = 2000 + V_[:, 1] / K
    SHOES.append(p_)

# ---------------------------------------------------------------- weights for what is built here
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


W = transfer(SV, ~is_arm & ~is_leg)
for sd in ('Left', 'Right'):             # the trunk does not go with the arms: what the skin gave them goes to the chest
    arm = under(I[sd + 'Arm']); W[:, I['Chest']] += W[:, arm].sum(1) + 0.6 * W[:, I[sd + 'Shoulder']]; W[:, arm] = 0; W[:, I[sd + 'Shoulder']] *= 0.4
Sh['W'] = smooth_w(W, ST)
SHORTS[0]['W'] = smooth_w(transfer(PV, ~is_arm), PT)
for p_ in SHORTS[1:]:
    W = transfer(p_['V'], ~is_arm)
    other = [j for j in under(I[('Right' if p_['side'] == 'Left' else 'Left') + 'Leg'])]
    W[:, I['Hips']] += W[:, other].sum(1); W[:, other] = 0
    p_['W'] = smooth_w(W, p_['T'], 6)
for p_ in SL:        # a sleeve goes with its upper arm; its cap inside the trunk partly with the collarbone
    side = p_['side']; cap = np.clip((148 - p_['band']) / 27, 0, 1)[:, None] * 0.5
    p_['W'] = onjoints(len(p_['V']), [(side + 'Arm', 1)]) * (1 - cap) + onjoints(len(p_['V']), [(side + 'Shoulder', 1)]) * cap
for p_ in SOCKS:
    w = smooth((ydr(p_['V'][:, 1]) - 644) / 14)
    p_['W'] = onjoints(len(p_['V']), [(p_['side'] + 'Shin', 1 - w), (p_['side'] + 'Foot', w)])
# ---------------------------------------------------------------- the hair (hair.py)
import hair as HR  # noqa: E402
Hr = HR.build(dict(C=C, I=I, NJ=NJ))

# ---------------------------------------------------------------- one pack
pieces = LIMBS + [('head', Hh), ('shirt', Sh), ('shorts', SHORTS[0])] + [('shorts' + p_['side'], p_) for p_ in SHORTS[1:]] + \
         [('hand' + p_['side'], p_) for p_ in HANDS] + [('sleeve' + p_['side'], p_) for p_ in SL] + \
         [('sock' + p_['side'], p_) for p_ in SOCKS] + [('shoe' + p_['side'], p_) for p_ in SHOES] + [('plaster', PL), ('hair', Hr)]
TWO = ('shirt', 'shorts', 'sleeve', 'sock', 'hair', 'plaster')
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
BANDS = [[y, y + 12, f01(C['stripe']), f01(rgb('#e3d2b4'))] for y in range(160, 340, 36)] + \
        [[1006.5, 1010, f01(rgb('#d06a55')), f01(rgb('#b85a47'))], [1999, 2011.5, f01(C['sole']), f01(rgb('#a83a2f'))]]
pack.save(os.path.join(OUT, 'tim.json'),
          dict(format='r1/character', version=2, id='tim-s3', label={'ru': 'Тим, графичный стиль'}, skinning='cor',
               source='Anny moood-child (engine) + Human Base Meshes stylised head (CC0) + shells from the drawing',
               pieces=ranges, trianglePieces=tranges, bands=BANDS),
          dict(positions=V.astype(np.float32).ravel(), triangles=np.vstack(Ts).astype(np.uint32).ravel(),
               skinJoints=SJ, skinWeights=SWt.astype(np.float32), joints=J1.astype(np.float32).ravel(), frames=FR.ravel(),
               col=np.vstack(cols).astype(np.uint8), shd=np.vstack(shds).astype(np.uint8), lin=np.vstack(lins).astype(np.uint8),
               ow=(np.clip(np.concatenate(ows), 0, 1) * 255).astype(np.uint8), uv=np.vstack(uvs).astype(np.float32),
               tex=np.concatenate(texs).astype(np.uint8), pn=np.vstack(pns).astype(np.float32),
               pw=(np.clip(np.concatenate(pws), 0, 1) * 255).astype(np.uint8), pj=pj, two=np.concatenate(two).astype(np.uint8), band=np.concatenate(bands).astype(np.float32)))
print('vertices', N, 'triangles', sum(len(t_) for t_ in Ts), {k: v[1] - v[0] for k, v in ranges.items()})
