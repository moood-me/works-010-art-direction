"""Аня in 3D: builds the character pack the viewer (web/anya.js) and the engine take.
  python3 build.py outdir
Bases: Anny's body (engine/data/bodies/moood-woman: hands, shins, feet and the SOMA skeleton with its weights), Blender's
Human Base Meshes stylised head (CC0; hbm_export.py), fitted to the drawing (head.py); the clothes and the hair are
built here from the drawing's own front and profile silhouettes (drawing.py); the face is painted from the drawing's
SVG parts (faces.py). Everything is skinned to SOMA's 77 joints, so Kimodo's motions play on it through the engine."""
import os, sys, json
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M, head as Hd, drawing as D, faces as FC

K = D.K
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/cache/to3d-r1-s3-anya/out'
HBM = '/home/user/cache/to3d-r1-s3-anya/hbm_head.npz'
os.makedirs(OUT, exist_ok=True)

y3 = lambda yd: (D.FLOOR - np.asarray(yd, float)) * K
ydr = lambda y: D.FLOOR - np.asarray(y, float) / K
u = lambda v: np.asarray(v, float) * K                     # drawing units → metres
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))


def rgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


C = {k: rgb(v) for k, v in FC.C.items()}
C['belt'], C['beltL'] = rgb('#d9805f'), rgb('#8a3a28')

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
J1[I['Neck2']] = [0, y3(150), 0.0]
J1[I['Head']] = [0, y3(100), -0.004]
J1[I['HeadEnd']] = [0, y3(-126), -0.01]
J1[I['Jaw']] = [0, y3(66), 0.03]
for s, sg in (('Left', 1), ('Right', -1)):
    J1[I[s + 'Eye']] = [sg * u(36), y3(0), 0.045]
    J1[I[s + 'Shoulder']] = [sg * 0.015, 1.19, 0.035]
    J1[I[s + 'Arm']] = [sg * 0.125, y3(258), 0.0]
    for n, k in (('ForeArm', 0.92), ('Hand', 0.92)):
        j = I[s + n]; J1[j] = J1[PARENT[j]] + k * (J0[j] - J0[PARENT[j]])
    for j in under(I[s + 'Hand'])[1:]:
        J1[j] = J1[PARENT[j]] + 0.95 * (J0[j] - J0[PARENT[j]])
    for n, x in (('Leg', 0.098), ('Shin', 0.09), ('Foot', 0.105)):
        J1[I[s + n], 0] = sg * x
    for n in ('ToeBase', 'ToeEnd'):
        J1[I[s + n], 0] = J0[I[s + n], 0] + (J1[I[s + 'Foot'], 0] - J0[I[s + 'Foot'], 0])


def joint_affine(j):
    """Joint j's move of the rest: x ↦ J1_j + A (x − J0_j): radial slimming of shins and forearms, smaller feet/hands."""
    n = NAMES[j]
    A = np.eye(3)
    if n.endswith('Shin') or n.endswith('ForeArm'):
        c = [k for k in range(NJ) if PARENT[k] == j][0]
        d = J0[c] - J0[j]; d /= np.linalg.norm(d)
        r = 0.74 if n.endswith('Shin') else 0.85
        A = r * np.eye(3) + (1 - r) * np.outer(d, d)
    elif 'Foot' in n or 'Toe' in n: A = 0.92 * np.eye(3)
    elif 'Hand' in n: A = 0.95 * np.eye(3)
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
keep = hand | (fore & near_wrist) | (legs & (P0[:, 1] < 0.36))
tk = keep[TRI0].all(1)
bi = np.where(keep)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
B = dict(V=PF[bi], T=remap[TRI0[tk]], SJ=SJ0[bi], SW=SW0[bi])
nb = len(bi)
# colours of what is left of the body: skin, white socks, brown shoes (feet a little fuller, as shoes)
by = B['V'][:, 1]
isfoot = np.array([('Foot' in n or 'Toe' in n) for n in dn[bi]]) | (by < 0.06)
nrm = M.vertex_normals(B['V'], B['T'])
B['V'][isfoot] += nrm[isfoot] * 0.005
B['col'] = np.tile(C['skin'], (nb, 1)); B['shd'] = np.tile(C['shade'], (nb, 1)); B['lin'] = np.tile(C['line'], (nb, 1))
sock = (by < y3(1252)) & ~isfoot
B['col'][sock] = C['sock']; B['shd'][sock] = rgb('#e2d6c4'); B['lin'][sock] = rgb('#9c8a76')
B['col'][isfoot] = C['shoe']; B['shd'][isfoot] = rgb('#55301f'); B['lin'][isfoot] = C['shoeL']

# ---------------------------------------------------------------- the head
hv, hP, eyes, er, vis = Hd.load(HBM)
d = np.load(HBM)
eL, eR = Hd.conv(d['L_v']), Hd.conv(d['R_v'])
hv2, eL2, eR2 = Hd.fit(hv, Hd.ears(hv), (eL, eR))
REG = [(36, -2, 30, 34), (-36, -2, 30, 34), (0, 72, 28, 9)]
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
# weights: the head, then down the neck to the chest
yde = yd - 18 * smooth((V0[:, 2] - 0.0) / 0.03)      # the chin and the jaw stay with the head
SW = np.zeros((nH, NJ))
sA = smooth((yde - 100) / 50); sB = smooth((yde - 160) / 50); sC = smooth((yde - 215) / 40)
SW[:, I['Head']] = 1 - sA
SW[:, I['Neck2']] = sA * (1 - sB)
SW[:, I['Neck1']] = sA * sB * (1 - sC)
SW[:, I['Chest']] = sA * sB * sC
Hh['W'] = SW
Hh['col'] = np.tile(C['skin'], (nH, 1)); Hh['shd'] = np.tile(C['shade'], (nH, 1)); Hh['lin'] = np.tile(C['line'], (nH, 1))
Hh['uv'] = np.c_[(xd - FC.X0) / (FC.X1 - FC.X0), 1 - (yd - FC.Y0) / (FC.Y1 - FC.Y0)]
Hh['tex'] = ((V0[:, 2] > -0.03) & (yd < 125)).astype(np.uint8)
ow = np.ones(nH)
for cx, cy, rx, ry in REG:
    e = np.sqrt(((xd - cx) / rx) ** 2 + ((yd - cy) / ry) ** 2)
    ow = np.minimum(ow, smooth((e - 1.0) / 0.4))
ow[nh:] = 0
Hh['ow'] = ow
Hh['pn'] = pn; Hh['pw'] = (1 - smooth((yd - 95) / 30))      # the face plain; the neck shaded by its own form


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


# the dress: drawn front width, drawn profile; at the top a small yoke into the neck
drows = []
for yy in np.r_[np.linspace(190, 204, 4), np.arange(210, 1142, 8.0), 1142]:
    if yy < 204:   # yoke: from the neck to the dress's top ring
        t_ = (204 - yy) / 14
        a_ = 58 * (1 - t_) + 33 * t_; f_ = 41 * (1 - t_) + 33 * t_; b_ = -41 * (1 - t_) - 39 * t_
        yv = 204 - 14 * (1 - (1 - t_) ** 2)
    else:
        a_ = front_half('dress', yy); s = side_span('dress', yy); f_, b_ = s[1], s[0]; yv = yy
    drows.append((y3(yv), u(a_), u((f_ + b_) / 2), u((f_ - b_) / 2), u((f_ - b_) / 2)))
DV, DT = loft(drows, 72, True)
nd = len(DV)
dyd = ydr(DV[:, 1])
Dd = dict(V=DV, T=DT)
Dd['col'] = np.tile(C['dress'], (nd, 1)); Dd['shd'] = np.tile(C['dressS'], (nd, 1)); Dd['lin'] = np.tile(C['dressL'], (nd, 1))
belt = (dyd > 404) & (dyd < 434)
Dd['col'][belt] = C['belt']; Dd['shd'][belt] = rgb('#bf6a4c'); Dd['lin'][belt] = C['beltL']


def dims_at(rows, yv):
    r = np.array(rows); o = np.argsort(r[:, 0])
    return [np.interp(yv, r[o, 0], r[o, k]) for k in range(1, 5)]


# the collar: a white round collar lying on the dress's yoke, deepest at the front
crows, ccols = [], 60
CV = []
for i, tt in enumerate(np.linspace(0, 1, 6)):
    th = np.linspace(0, 2 * np.pi, ccols, endpoint=False)
    deep = 194 + (232 - 194) * tt * np.clip(np.cos(th), 0, 1) ** 1.5 + 8 * tt * (1 - np.clip(np.cos(th), 0, 1))
    pts = []
    for k, (thk, dk) in enumerate(zip(th, deep)):
        a_, zc_, df_, db_ = dims_at(drows, y3(min(dk, 204)))
        grow = 1 + 0.06 * tt
        x, z = ring(a_ * grow if dk >= 204 else (33 + (58 - 33) * tt) * K * grow, zc_, df_ * grow + 0.003, db_ * grow + 0.003, np.array([thk]))
        pts.append([x[0], y3(dk) + 0.002, z[0]])
    CV += pts
CV = np.array(CV); CT = grid(6, ccols, True)
nc = len(CV)
Cc = dict(V=CV, T=CT, col=np.tile(C['sock'], (nc, 1)), shd=np.tile(rgb('#e8dccb'), (nc, 1)), lin=np.tile(C['dressL'], (nc, 1)))

# the cardigan: a shell over the dress, open in front, its yoke round the neck; sleeves along the arms
krows, kgap = [], []
gapf = lambda yy: np.interp(yy, [188, 222, 360, 520, 656], [50, 22, 46, 50, 48])
for tt in np.linspace(1, 0, 9)[:-1]:          # yoke: neck ring → shoulder ring
    yv = 188 + 62 * (1 - tt) ** 2
    a_ = 112 * (1 - tt) + 36 * tt
    zf = 62 * (1 - tt) + 36 * tt; zb = -82 * (1 - tt) - 44 * tt
    krows.append((y3(yv), u(a_), u((zf + zb) / 2), u((zf - zb) / 2), u((zf - zb) / 2)))
    kgap.append(np.arcsin(min(gapf(yv) / a_, np.sin(np.radians(78)))))
for yy in np.arange(250, 657, 8.0):
    da, dzc, ddf, ddb = dims_at(drows, y3(yy))
    a_ = max(u(112), da + 0.009)
    zf = max(u(62), dzc + ddf + 0.009); zb = min(u(-82), dzc - ddb - 0.009)
    krows.append((y3(yy), a_, (zf + zb) / 2, (zf - zb) / 2, (zf - zb) / 2))
    kgap.append(np.arcsin(min(gapf(yy) / (a_ / K), 0.97)))
KV, KT = loft(krows, 64, False, kgap)
nk = len(KV)
Kc = dict(V=KV, T=KT, col=np.tile(C['knit'], (nk, 1)), shd=np.tile(C['knitS'], (nk, 1)), lin=np.tile(C['knitL'], (nk, 1)))


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


SL = []
for s in ('Left', 'Right'):
    A_, E_, W_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']], J1[I[s + 'Hand']]
    d1 = (E_ - A_) / np.linalg.norm(E_ - A_); d2 = (W_ - E_) / np.linalg.norm(W_ - E_)
    path = catmull([A_ - d1 * 0.045, (A_ + E_) / 2, E_, W_ + d2 * 0.01], 10)
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]; L /= L[-1]
    radii = np.interp(L, [0, 0.12, 0.5, 0.9, 1.0], [0.036, 0.041, 0.037, 0.034, 0.036])
    V_, T_ = tube(path, radii)
    SL.append(dict(V=V_, T=T_, col=np.tile(C['knit'], (len(V_), 1)), shd=np.tile(C['knitS'], (len(V_), 1)),
                   lin=np.tile(C['knitL'], (len(V_), 1)), side=s))


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
    L = 0.5 * smooth((yd_ - 640) / 500)
    side = 1 / (1 + np.exp(-V[:, 0] / 0.035))
    W[:, I['LeftLeg']] = L * side; W[:, I['RightLeg']] = L * (1 - side); W[:, I['Hips']] = 1 - L
    return W


def smooth_w(W, T, n, iters=12):
    polys = [list(t_) for t_ in T]; A = M.adjacency(n, polys)
    return M.smooth(W, A, np.ones(n, bool), iters, 0.5)


def cloth_weights(V, T):
    W = transfer(V)
    uu = smooth((ydr(V[:, 1]) - 560) / 140)[:, None]
    W = (1 - uu) * W + uu * skirt_rule(V)
    return smooth_w(W, T, len(V))


Dd['W'] = cloth_weights(DV, DT)
Kc['W'] = cloth_weights(KV, KT)
Cc['W'] = transfer(CV)
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
Hr = HR.build(dict(head=(V0[:nh], M.triangulate(hP)), dress=drows, card=krows, C=C, J1=J1, I=I, NJ=NJ))

# ---------------------------------------------------------------- one pack
pieces = [('body', B), ('head', Hh), ('dress', Dd), ('collar', Cc), ('cardigan', Kc)] + \
         [('sleeve' + S_['side'], S_) for S_ in SL] + [('hair', Hr)]
Vs, Ts, Ws, cols, shds, lins, ows, uvs, texs, pns, pws, two = [], [], [], [], [], [], [], [], [], [], [], []
base = 0; ranges = {}
for name, p in pieces:
    n = len(p['V'])
    Vs.append(p['V']); Ts.append(p['T'] + base); Ws.append(p['W'])
    cols.append(p['col']); shds.append(p['shd']); lins.append(p['lin'])
    ows.append(p.get('ow', np.ones(n))); uvs.append(p.get('uv', np.zeros((n, 2))))
    texs.append(p.get('tex', np.zeros(n))); pns.append(p.get('pn', np.zeros((n, 3)))); pws.append(p.get('pw', np.zeros(n)))
    two.append(np.full(n, 1 if name in ('cardigan', 'hair', 'dress', 'collar') or name.startswith('sleeve') else 0))
    ranges[name] = [base, base + n]; base += n
V = np.vstack(Vs); W = np.vstack(Ws); N = len(V)
W = np.maximum(W, 0)
order = np.argsort(-W, 1)[:, :4]
SJ = order.astype(np.uint8); SWt = np.take_along_axis(W, order, 1); SWt /= SWt.sum(1, keepdims=True)
pj = SJ[:, 0].astype(np.float32)
pack.save(os.path.join(OUT, 'anya.json'),
          dict(format='r1/character', version=1, id='anya-s3', label={'ru': 'Аня, графичный стиль'}, faces='.', skinning='cor',
               source='Anny moood-woman (engine) + Human Base Meshes stylised head (CC0) + shells from the drawing',
               pieces=ranges),
          dict(positions=V.astype(np.float32).ravel(), triangles=np.vstack(Ts).astype(np.uint32).ravel(),
               skinJoints=SJ, skinWeights=SWt.astype(np.float32), joints=J1.astype(np.float32).ravel(), frames=FR.ravel(),
               col=np.vstack(cols).astype(np.uint8), shd=np.vstack(shds).astype(np.uint8), lin=np.vstack(lins).astype(np.uint8),
               ow=(np.clip(np.concatenate(ows), 0, 1) * 255).astype(np.uint8), uv=np.vstack(uvs).astype(np.float32),
               tex=np.concatenate(texs).astype(np.uint8), pn=np.vstack(pns).astype(np.float32),
               pw=(np.clip(np.concatenate(pws), 0, 1) * 255).astype(np.uint8), pj=pj, two=np.concatenate(two).astype(np.uint8)))
print('vertices', N, 'triangles', sum(len(t_) for t_ in Ts), {k: v[1] - v[0] for k, v in ranges.items()})
