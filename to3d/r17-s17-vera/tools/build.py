"""Вера (Билибин) in 3D: builds the character pack that the viewer (web/vera.js) and the engine take.
  python3 build.py [CACHE]          → CACHE/out/vera.json|bin  (copy to web/data/)
Bases: Anny's body (engine/data/bodies/moood-woman: mesh, SOMA skeleton and weights) for the body, arms, hands and
legs; the head, the ears, the hair and the knot are the drawing's own volume (styles/s17-bilibin/tools/parts.py:
cross-sections, the face surface with nose and lips, the hairline) meshed as it is — the face is drawn on it, flat,
by the style's code, so the silhouette is what the head has to give, and it gives the drawing's exactly.
The dress is Anny's body pushed out plus a long skirt; the shawl is a shell over the shoulders and upper arms with
its edges cut per pixel; the roses of its print are placed on the cloth's surface (centres and frames on the shell).
After Р7's build.py (to3d/r7-s4-vera) for the body, the skirt, the shoes.
Units: metres; the drawing's units map as world = (x·K, (FEET − y)·K, z·K + ZOFF)."""
import os, sys, json, math
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack, mesh as M, drawing as DR  # noqa: E402

C = sys.argv[1] if len(sys.argv) > 1 else '/home/user/cache/to3d-r17-s17-vera'
OUT = os.path.join(C, 'out')
os.makedirs(OUT, exist_ok=True)
K, FEET, P = DR.K, DR.FEET, DR.P
sm = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))

# pieces: what the contour separates (a line is drawn where the piece changes) and what paint each gets
PIECES = ['none', 'skin', 'dress', 'legs', 'shoe', 'head', 'earL', 'earR', 'hair', 'knot', 'shawl', 'cover', 'pages',
          'ground', 'flower']
pi_ = PIECES.index

# ---------------------------------------------------------------- skeleton and Anny's body
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body('moood-woman')
P0 = a['positions'].reshape(-1, 3).astype(float); J0 = a['joints'].reshape(-1, 3).astype(float)
FR = a['frames'].reshape(-1, 4).astype(np.float32)
TRI0 = t['triangles'].reshape(-1, 3).astype(np.int64)
SJ0 = t['skinJoints'].reshape(-1, 4).astype(np.int64); SW0 = t['skinWeights'].reshape(-1, 4).astype(float)
PARTS = t['parts'].reshape(len(P0), -1) / 255.0; PN = th['parts']
part = lambda *ns: sum(PARTS[:, PN.index(n)] for n in ns)

S = (FEET + 112) * K / 1.585 * 1.03                       # Anny's 1.585 m → Вера's 1.67 m


def under(j):
    out, st = [], [j]
    while st:
        k = st.pop(); out.append(k); st += list(np.where(PARENT == k)[0])
    return out


J1 = J0 * S
for s, sg in (('Left', 1), ('Right', -1)):          # the drawing's narrow, slightly fallen shoulders
    for j in under(I[s + 'Shoulder']): J1[j] += [-sg * 0.008, -0.006, 0]
    for j in under(I[s + 'Arm']): J1[j] += [-sg * 0.028, -0.008, 0]


def joint_affine(j):
    n = NAMES[j]
    if n in ('Hips',): return np.diag([0.86, 1, 0.9])
    if n in ('Spine1', 'Spine2'): return np.diag([0.82, 1, 0.86])
    if n in ('Chest',): return np.diag([0.79, 1, 0.84])
    if n.endswith('Shoulder'): return np.diag([0.8, 0.9, 0.88])
    r = {'LeftArm': 0.84, 'RightArm': 0.84, 'LeftForeArm': 0.86, 'RightForeArm': 0.86,
         'LeftLeg': 0.86, 'RightLeg': 0.86, 'LeftShin': 0.86, 'RightShin': 0.86}.get(n)
    if r:
        c = [k for k in range(NJ) if PARENT[k] == j][0]
        d = J0[c] - J0[j]; d /= np.linalg.norm(d)
        return r * np.eye(3) + (1 - r) * np.outer(d, d)
    return np.eye(3)


AFF = [joint_affine(j) for j in range(NJ)]
LEG_IN = np.radians(7.0)                            # the feet near each other under the narrow long skirt
for s, sg in (('Left', 1), ('Right', -1)):
    c, sn_ = np.cos(-sg * LEG_IN), np.sin(-sg * LEG_IN)
    Rz = np.array([[c, -sn_, 0], [sn_, c, 0], [0, 0, 1]])
    root = J1[I[s + 'Leg']].copy()
    for j in under(I[s + 'Leg']):
        J1[j] = root + Rz @ (J1[j] - root)
        AFF[j] = Rz @ AFF[j]


def deform(Pt, SJ, SW):
    out = np.zeros_like(Pt)
    for k in range(4):
        for j in np.unique(SJ[:, k]):
            m = (SJ[:, k] == j) & (SW[:, k] > 0)
            out[m] += SW[m, k, None] * (J1[j] + S * (Pt[m] - J0[j]) @ AFF[j].T)
    return out


PB = deform(P0, SJ0, SW0)

# ---------------------------------------------------------------- drawing units ↔ world
NECK_Z = -12.0                                      # the drawn neck's middle (parts.neck)
CUT = 126.0                                         # Anny's neck above this height (drawing units) is replaced
cut_y = (FEET - CUT) * K
neck_c = PB[(PB[:, 1] > cut_y) & (PB[:, 1] < cut_y + 0.05) & (part('neck') > 0.5)]
ZOFF = float((neck_c[:, 2].max() + neck_c[:, 2].min()) / 2) - NECK_Z * K


def W(p):
    p = np.asarray(p, float)
    return np.stack([p[..., 0] * K, (FEET - p[..., 1]) * K, p[..., 2] * K + ZOFF], -1)


def D(w):
    w = np.asarray(w, float)
    return np.stack([w[..., 0] / K, FEET - w[..., 1] / K, (w[..., 2] - ZOFF) / K], -1)


def grid_tris(nr, nc, closed=True, flip=False):
    T = []
    for r in range(nr - 1):
        for c in range(nc if closed else nc - 1):
            a0, a1 = r * nc + c, r * nc + (c + 1) % nc; b0, b1 = a0 + nc, a1 + nc
            T += [[a0, b0, a1], [a1, b0, b1]] if not flip else [[a0, a1, b0], [a1, b1, b0]]
    return np.array(T)


def orient(V, T, c):
    """turn every triangle so its normal points away from c"""
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    out = (n * (V[T].mean(1) - c)).sum(1) < 0
    T = T.copy(); T[out] = T[out][:, [0, 2, 1]]
    return T


def chain_w(yd, n, marks=(100, 132, 170)):
    """weights down the neck by height (drawing units): Head → Neck2 → Neck1 → Chest"""
    Wt = np.zeros((n, NJ))
    ts = [sm((yd - m) / 34) for m in marks]
    Wt[:, I['Head']] = 1 - ts[0]
    Wt[:, I['Neck2']] = ts[0] * (1 - ts[1])
    Wt[:, I['Neck1']] = ts[0] * ts[1] * (1 - ts[2])
    Wt[:, I['Chest']] = ts[0] * ts[1] * ts[2]
    return Wt


# ---------------------------------------------------------------- the head: the drawing's volume
ys, ths, HG = DR.head_grid()
NY, NTH = HG.shape[:2]
top = np.array([[0.0, P.crown - 0.5, 0.0]]); bot = np.array([[0.0, P.chin + 0.5, P.zm(P.chin) * 0.5]])
hd = np.r_[HG.reshape(-1, 3), top, bot]
hT = list(grid_tris(NY, NTH))
for c in range(NTH):
    c2 = (c + 1) % NTH
    hT.append([NY * NTH, c, c2]); hT.append([NY * NTH + 1, (NY - 1) * NTH + c2, (NY - 1) * NTH + c])
hT = np.array(hT)
HC = np.array([0.0, -10.0, 0.0])
hT = orient(hd, hT, HC)
# the neck: a tube set back from the face, from inside the head down into Anny's neck; the drawn neck (29–33 wide
# at a head of 60) widens at its foot into the shoulders
nrows = np.linspace(40, 168, 40); ncols = 48
nk = []
for y in nrows:
    rx = np.interp(y, [40, 112, 140, 168], [P.neck * 1.1, P.neck * 1.12, P.neck * 1.22, P.neck * 1.3])
    rz = rx * 0.92
    an = np.linspace(0, 2 * np.pi, ncols, endpoint=False)
    nk.append(np.c_[rx * np.sin(an), np.full(ncols, y), NECK_Z + rz * np.cos(an)])
nk = np.array(nk).reshape(-1, 3)
nkT = orient(nk, grid_tris(len(nrows), ncols), np.array([0, 100.0, NECK_Z]))
# the ears: a flat lobe standing out of the head's side, its back edge further out (parts.ear: 46 high, from y −6)
ears = []
for sd in (1, -1):
    u, v = np.meshgrid(np.linspace(0, np.pi, 18), np.linspace(-np.pi, np.pi, 28, endpoint=False), indexing='ij')
    ex = 3.2 * np.sin(u) * np.cos(v); ey = 23.0 * np.cos(u) * (1 + 0.0 * u); ez = 12.0 * np.sin(u) * np.sin(v)
    ey = ey - 3.0 * np.sin(u) * np.sin(v)                # the top leans back a little
    ang = np.radians(52)                                 # the lobe turned out from the skull
    lx = ex * np.cos(ang) - ez * np.sin(ang); lz = ex * np.sin(ang) + ez * np.cos(ang)
    y0, y1 = P.ear_y
    cx = P.a((y0 + y1) / 2) * 0.97 + 5.5; cz = -P.a(15) * 0.18 - 4
    ev = np.stack([sd * (cx + lx), (y0 + y1) / 2 + ey, cz + lz], -1).reshape(-1, 3)
    eT = orient(ev, grid_tris(18, 28), ev.mean(0))
    ears.append((ev, eT))

# ---------------------------------------------------------------- the hair: the head grown by 8 above the hairline; the knot
hn = M.vertex_normals(hd, hT)
grid_th = np.r_[np.tile(ths, NY), 0, 0]
hm = DR.hairline_y(grid_th) - hd[:, 1]              # how far inside the hair (units); < 0: skin
hm[-2] = 60; hm[-1] = -60
thick = 7.5 * sm(hm / 16) + 0.7
hair_v = hd + hn * thick[:, None]
keep = (hm[hT] > -8).any(1)
hair_t = hT[keep]
used = np.unique(hair_t); rm = -np.ones(len(hd), int); rm[used] = np.arange(len(used))
hair_v, hair_m, hair_t = hair_v[used], hm[used], rm[hair_t]
# strands: combed straight back from the hairline to the knot — the across-coordinate is the angle round the axis
# from the forehead to the knot
BUN = DR.KNOT
ax0 = np.array([0.0, -70.0, 40.0]); ax = BUN - ax0; ax /= np.linalg.norm(ax)
e1 = np.array([1.0, 0, 0]); e2 = np.cross(ax, e1); e2 /= np.linalg.norm(e2)


def strand_coord(p):
    q = p - ax0; q = q - np.outer(q @ ax, ax)
    return np.arctan2(q @ e1, q @ e2)


hair_s = strand_coord(hair_v)
bu, bv_ = np.meshgrid(np.linspace(0, np.pi, 30), np.linspace(-np.pi, np.pi, 48, endpoint=False), indexing='ij')
knot_v = np.stack([31 * np.sin(bu) * np.cos(bv_), BUN[1] + 30 * np.sin(bu) * np.sin(bv_), BUN[2] - 30 * np.cos(bu)], -1).reshape(-1, 3)
knot_t = orient(knot_v, grid_tris(30, 48), BUN)
knot_s = np.hypot(knot_v[:, 0], knot_v[:, 1] - BUN[1])      # rings round the knot's axis

# ---------------------------------------------------------------- Anny's body: what is kept; the dress on it
gone = (part('head', 'neck') > 0.5) & (PB[:, 1] > cut_y)
tk = ~gone[TRI0].any(1)
bi = np.where(~gone)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
bv = PB[bi].copy(); bT = remap[TRI0[tk]]; bSJ = SJ0[bi]; bSW = SW0[bi]
bp = PARTS[bi]
bpart = lambda *ns: sum(bp[:, PN.index(n)] for n in ns)
legs = bpart('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot') > 0.5
feet = bpart('Lfoot', 'Rfoot') > 0.5
arms_ = bpart('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand') > 0.3
# the neck's foot: Anny's neck stump drawn in to the drawn neck's width at the cut, so the silhouette runs on
nbd = D(bv)
nz = (bpart('neck') > 0.2) | ((nbd[:, 1] < 170) & (np.abs(nbd[:, 0]) < 60) & ~arms_)
kk = sm((170 - nbd[:, 1]) / (170 - CUT)) * nz
rad = np.hypot(nbd[:, 0], nbd[:, 2] - NECK_Z)
want = np.minimum(rad, P.neck * 1.22 + (rad - P.neck * 1.22) * 0.25)
f = 1 + kk * (want / np.maximum(rad, 1e-6) - 1)
nbd[:, 0] *= f; nbd[:, 2] = NECK_Z + (nbd[:, 2] - NECK_Z) * f
bv = W(nbd)
Ab = M.adjacency(len(bv), bT)
bv = M.smooth(bv, Ab, kk * 0.8, iters=12, lam=0.5)
by = bv[:, 1]

# where the sleeve ends (the wrist) and where the neckline is: margins in drawing units, > 0 on the dress
wrist_m = np.full(len(bv), 1e3)
for s in ('Left', 'Right'):
    jw = J1[I[s + 'Hand']]; jf = J1[I[s + 'ForeArm']]
    d = (jw - jf) / np.linalg.norm(jw - jf)
    along = (bv - jw) @ d
    side = (bpart('Lhand', 'LforeArm') if s == 'Left' else bpart('Rhand', 'RforeArm')) > 0.3
    wrist_m = np.where(side, np.minimum(wrist_m, (-0.012 - along) / K), wrist_m)
bd = D(bv)
ax_ = np.abs(bd[:, 0])
yn_front = np.where(ax_ < 36, 150 - 26 * (ax_ / 36) ** 2.0, 124 - (ax_ - 36) * 3.0)     # the round neckline
yn = np.where(bd[:, 2] > NECK_Z, yn_front, 128.0)
neck_m = np.where(arms_, 1e3, bd[:, 1] - yn)
body_em = wrist_m                                  # the neckline is cut per pixel in the viewer (a smooth curve)
dress = (body_em > 0) & ~legs
nb = M.vertex_normals(bv, bT)
off = np.where(legs, 0.001, 0.005 * sm(np.minimum(body_em, neck_m) / 12))
bv = bv + nb * off[:, None]
mat = np.where(legs, pi_('legs'), pi_('dress'))       # 'dress' with em < 0 is skin (decided per pixel)

# the feet: Anny's below the ankle go; a lofted shoe on each foot (Р7's)
footcut = feet & (bv[:, 1] < 0.085)
bT = bT[~footcut[bT].all(1)]
SHV, SHT, SHW = [], [], []
for s, sg in (('Left', 1), ('Right', -1)):
    jf = J1[I[s + 'Foot']]; jt = J1[I[s + 'ToeBase']]
    fwd = jt - jf; fwd[1] = 0; fwd /= np.linalg.norm(fwd)
    side = np.cross([0, 1.0, 0], fwd)
    base = np.array([jf[0], 0.0, jf[2]])
    rows, cols = 16, 48
    vs = []
    for i in range(rows):
        t_ = i / (rows - 1)
        y = 0.002 + t_ * 0.088
        front = max(0.172 * (1 - t_) ** 1.6 + 0.05 * t_, 0.05)
        back = 0.052 - 0.01 * t_
        w = 0.044 - 0.008 * t_
        if t_ > 0.55: front = 0.05 + 0.015 * (1 - (t_ - 0.55) / 0.45)
        a_ = np.linspace(0, 2 * np.pi, cols, endpoint=False)
        ca, sa = np.cos(a_), np.sin(a_)
        L_ = np.where(ca > 0, front, back)
        rr = (np.abs(ca) ** 2.4 + np.abs(sa) ** 2.4) ** (-1 / 2.4)
        for k in range(cols):
            vs.append(base + fwd * (ca[k] * L_[k] * rr[k]) + side * (sa[k] * w * rr[k]) + [0, y, 0])
    vs = np.array(vs)
    ts = [list(q) for q in grid_tris(rows, cols, flip=True)]
    c0 = len(vs); vs = np.r_[vs, [base + [0, 0.002, 0] + fwd * 0.07]]
    ts += [[c0, (k + 1) % cols, k] for k in range(cols)]
    ts = np.array(ts)
    off_ = sum(len(q) for q in SHV)
    SHV.append(vs); SHT.append(ts + off_)
    w_ = np.zeros((len(vs), NJ)); w_[:, I[s + 'Foot']] = 1.0
    toe = np.clip(((vs - jt) @ fwd) / 0.04, 0, 1) * 0.6
    w_[:, I[s + 'Foot']] -= toe; w_[:, I[s + 'ToeBase']] += toe
    SHW.append(w_)
SHOE_V, SHOE_T, SHOE_W = np.vstack(SHV), np.vstack(SHT), np.vstack(SHW)

# ---------------------------------------------------------------- the skirt: from the waist to the ankles
WAIST = float(J1[I['Spine1'], 1]) + 0.02
hipz = ~arms_ & (bv[:, 1] < WAIST + 0.01) & (bv[:, 1] > J1[I['LeftShin'], 1]) & ~feet
nb2 = M.vertex_normals(bv, bT)
bv[hipz] -= nb2[hipz] * 0.010 * sm((WAIST + 0.01 - bv[hipz, 1]) / 0.04)[:, None]


def ring_body(y, pad):
    m = (abs(bv[:, 1] - y) < 0.012) & ~arms_
    v = bv[m]
    return abs(v[:, 0]).max() + pad, v[:, 2].max() + pad, v[:, 2].min() - pad


HEM = (FEET - 1290) * K
srows, scols = 44, 97
sys_ = np.linspace(WAIST + 0.012, HEM, srows)
hip_y = J1[I['LeftLeg'], 1] - 0.05
hx, hzf, hzb = [float(np.mean([ring_body(hip_y + d_, 0.012)[c_] for d_ in (-0.02, -0.01, 0, 0.01, 0.02)])) for c_ in range(3)]
SV = []
# the body's widths from the waist to the hips, smoothed along the height (a ring at one height is noisy)
fy = np.linspace(hip_y, WAIST, 24)
fr = np.array([ring_body(y, 0.010) for y in fy])
for c_ in range(3):
    fr[:, c_] = np.convolve(np.r_[[fr[0, c_]] * 3, fr[:, c_], [fr[-1, c_]] * 3], np.ones(7) / 7, 'valid')
for i, y in enumerate(sys_):
    u = i / (srows - 1)
    yc_ = min(max(y, hip_y), WAIST)
    axw, zf2, zb2 = (float(np.interp(yc_, fy, fr[:, c_])) for c_ in range(3))
    if y < hip_y:                                   # below the hips: a narrow bell down to the hem (as drawn: 150–170 units)
        k = sm((hip_y - y) / (hip_y - HEM)) ** 0.8
        axw = hx + (0.176 - hx) * k; zf2 = hzf + (0.150 - hzf) * k; zb2 = hzb + (-0.125 - hzb) * k
    tuck = -0.014 * (1 - min(1.0, i / 4.0))             # the top rows go into the body: no step at the waist
    axw += tuck; zf2 += tuck; zb2 -= tuck
    zc = (zf2 + zb2) / 2
    th_ = np.linspace(-np.pi, np.pi, scols)
    sn, cs = np.sin(th_), np.cos(th_)
    wave = 1 + 0.022 * np.sin(8 * th_ + 0.4) * u ** 1.5        # soft folds toward the hem
    rr = (np.abs(sn) ** 2.3 + np.abs(cs) ** 2.3) ** (-1 / 2.3)
    SV.append(np.c_[axw * sn * rr * wave, np.full(scols, y), zc + np.where(cs > 0, zf2 - zc, zc - zb2) * cs * rr * wave])
SV = np.array(SV).reshape(-1, 3)
ST = grid_tris(srows, scols, closed=False)
skW = np.zeros((len(SV), NJ))
yy = SV[:, 1]; side = sm((SV[:, 0] / 0.06 + 1) / 2)
down = sm((hip_y - yy) / 0.35) * 0.62
knee = sm((J1[I['LeftShin'], 1] + 0.12 - yy) / 0.15) * 0.28
skW[:, I['Hips']] = 1 - down
for s, f_ in (('Left', side), ('Right', 1 - side)):
    skW[:, I[s + 'Leg']] += (down - knee) * f_
    skW[:, I[s + 'Shin']] += knee * f_
top_band = sm((yy - (WAIST - 0.01)) / 0.02)
skW = skW * (1 - top_band)[:, None]; skW[:, I['Spine1']] += top_band
sk_th = np.tile(np.linspace(-np.pi, np.pi, scols), srows)
sk_em = (SV[:, 1] - HEM) / K                         # units above the hem
sk_ea = sk_th * 150.0                                # along the hem (units)

# what the skirt hides (hips, thighs) is not needed and would only show through: cut away
hid = ~arms_ & (bv[:, 1] < WAIST - 0.03) & (bv[:, 1] > J1[I['LeftShin'], 1] - 0.05)
bT = bT[~hid[bT].all(1)]

# ---------------------------------------------------------------- the shawl: a shell over the shoulders and upper arms
nb = M.vertex_normals(bv, bT)
bd = D(bv)
w_arm = np.clip(bpart('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand'), 0, 1)
m_arm = np.full(len(bv), 1e3)
for s in ('Left', 'Right'):
    j0, j1_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']]
    L = np.linalg.norm(j1_ - j0); d = (j1_ - j0) / L
    tt = (bv - j0) @ d / L
    sidem = (bv[:, 0] > 0) if s == 'Left' else (bv[:, 0] < 0)
    m_arm = np.where(sidem, (0.97 - tt) * L / K, m_arm)
torso_c = np.array([0.0, 0.0, float(J1[I['Chest'], 2])])
phi = np.arctan2(bv[:, 0], bv[:, 2] - torso_c[2])     # round the trunk: 0 the front, ±pi the back
aphi = np.abs(phi)
# the lower edge: high in front (the ends crossed on the chest), down the sides, a point down the back
yb = np.interp(aphi, [0, 0.9, 1.6, 2.5, np.pi], [350, 385, 420, 445, 456])
m_bot = yb - bd[:, 1]
# the V at the neck: from the neck's sides (±56 at y 128) to its point (0, 262)
vx = np.interp(bd[:, 1], [110, 128, 150, 262], [40, 40, 40, 0])
m_v = np.where((bd[:, 2] > NECK_Z) & (bd[:, 1] < 262), ax_ * 0 + np.abs(bd[:, 0]) - vx, 1e3)
m_v = np.where(bd[:, 1] >= 262, np.minimum(1e3, (bd[:, 1] - 262) * 1.5 + np.abs(bd[:, 0])), m_v)
m_v = np.where(bd[:, 2] > NECK_Z, m_v, 1e3)
m_torso = np.minimum(m_bot, m_v)
sh_em = (1 - w_arm) * np.minimum(m_torso, 200) + w_arm * np.minimum(m_arm, 200)
sh_em = np.where(legs, -100, sh_em)
cand = sh_em > -14
shT = bT[cand[bT].all(1)]
used = np.unique(shT); rm = -np.ones(len(bv), int); rm[used] = np.arange(len(used))
SHL_V = (bv + nb * 0.011)[used]; SHL_T = rm[shT]; SHL_SJ, SHL_SW = bSJ[used], bSW[used]
SHL_EM = sh_em[used]
# along the edge (for the teeth of the border): the V runs by height, the lower edge round the trunk, the arm round itself
is_v = (m_v < m_bot)[used]
arm_ang = np.zeros(len(bv))
for s in ('Left', 'Right'):
    j0, j1_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']]
    d = (j1_ - j0) / np.linalg.norm(j1_ - j0)
    q = bv - j0; q = q - np.outer(q @ d, d)
    e1_ = np.cross(d, [0, 0, 1.0]); e1_ /= np.linalg.norm(e1_); e2_ = np.cross(d, e1_)
    sidem = (bv[:, 0] > 0) if s == 'Left' else (bv[:, 0] < 0)
    arm_ang = np.where(sidem, np.arctan2(q @ e1_, q @ e2_), arm_ang)
SHL_EA = np.where(w_arm[used] > 0.5, arm_ang[used] * 45.0, np.where(is_v, bd[used, 1] * 1.08, phi[used] * 110.0))
SHL_N = M.vertex_normals(SHL_V, SHL_T)
# the print: roses scattered on the cloth — big ones first, small ones in the gaps (the tile of vera.shawl_pattern
# has four roses of radius 15, 13, 9, 8 on 120 × 120)
rng = np.random.RandomState(4)
sd_ = D(SHL_V)
order = rng.permutation(len(SHL_V))
roses = []


def scatter(rmin, rmax, dist, margin, room):
    for i in order:
        if SHL_EM[i] < margin: continue
        p = sd_[i]
        if any(np.linalg.norm(p - q[0]) < dist * (0.5 + 0.5 * (q[3] > 10)) + room * (q[3] <= 10) for q in roses if abs(q[0][1] - p[1]) < 120): continue
        n = SHL_N[i] * [1, -1, 1]                    # the normal in drawing units (y down)
        t = np.cross([0, 1.0, 0], n);
        if np.linalg.norm(t) < 0.2: t = np.cross([0, 0, 1.0], n)
        t /= np.linalg.norm(t); b = np.cross(n, t)
        a_ = rng.uniform(0, 2 * np.pi)
        t, b = t * np.cos(a_) + b * np.sin(a_), b * np.cos(a_) - t * np.sin(a_)
        roses.append((p, t, b, rng.uniform(rmin, rmax)))


scatter(13, 15.5, 74, 30, 0)
nbig = len(roses)
scatter(8, 9.5, 62, 22, 16)
print('roses', nbig, len(roses) - nbig)

# ---------------------------------------------------------------- joints for the new head, and the pack
J = J1.copy()
Jw = lambda p: W(np.array(p, float))
J[I['Neck1']] = Jw([0, 150, NECK_Z])
J[I['Neck2']] = Jw([0, 118, NECK_Z])
J[I['Head']] = Jw([0, 88, NECK_Z + 2])
J[I['HeadEnd']] = Jw([0, P.crown, 0])
J[I['Jaw']] = Jw([0, 50, 10])
for s, sg in (('Left', 1), ('Right', -1)):
    J[I[s + 'Eye']] = Jw([sg * P.eye_x, 0, P.zs(P.eye_x, 0) - 10])


def top4(Wt):
    idx = np.argsort(-Wt, 1)[:, :4]; w = np.take_along_axis(Wt, idx, 1); w /= w.sum(1, keepdims=True)
    return idx, w


parts_out = []


def add(name, V, T, mat, SJ=None, SW=None, Wt=None, **attr):
    if Wt is not None: SJ, SW = top4(Wt)
    parts_out.append(dict(name=name, V=V, T=T, mat=np.broadcast_to(mat, (len(V),)), SJ=SJ, SW=SW, **attr))


def flipw(T): return T[:, [0, 2, 1]]


def outward(V, T, c=None):
    return T


add('body', bv, bT, mat, bSJ, bSW, em=body_em, dr=D(bv))
add('head', W(hd), flipw(hT), pi_('head'), Wt=chain_w(hd[:, 1], len(hd)), dr=hd, em=np.full(len(hd), 100.0))
add('neck', W(nk), flipw(nkT), pi_('skin'), Wt=chain_w(nk[:, 1], len(nk)), dr=nk, em=np.full(len(nk), -100.0))
for (ev, eT), nm in zip(ears, ('earL', 'earR')):
    add(nm, W(ev), flipw(eT), pi_(nm), Wt=chain_w(ev[:, 1], len(ev)), dr=ev)
add('hair', W(hair_v), flipw(hair_t), pi_('hair'), Wt=chain_w(hair_v[:, 1], len(hair_v)), dr=hair_v, em=hair_m, hs=hair_s)
add('knot', W(knot_v), flipw(knot_t), pi_('knot'), Wt=chain_w(knot_v[:, 1], len(knot_v)), dr=knot_v, em=np.full(len(knot_v), 100.0), hs=knot_s)
add('shoes', SHOE_V, SHOE_T, pi_('shoe'), Wt=SHOE_W, two=1, em=np.full(len(SHOE_V), 100.0))
add('skirt', SV, ST, pi_('dress'), Wt=skW, two=1, em=sk_em, ea=sk_ea, hs=sk_th + 10.0, dr=D(SV))   # hs > 5 marks the skirt
add('shawl', SHL_V, SHL_T, pi_('shawl'), SHL_SJ, SHL_SW, two=1, em=SHL_EM, ea=SHL_EA, dr=sd_)

N = sum(len(p['V']) for p in parts_out)
pos = np.concatenate([p['V'] for p in parts_out]).astype(np.float32)
tri, base, ranges = [], 0, {}
for p in parts_out:
    tri.append(p['T'] + base); ranges[p['name']] = [base, base + len(p['V'])]; base += len(p['V'])
tri = np.concatenate(tri).astype(np.uint32)
SJ = np.concatenate([p['SJ'] for p in parts_out]).astype(np.uint8)
SW = np.concatenate([p['SW'] for p in parts_out]).astype(np.float32)
matv = np.concatenate([p['mat'] for p in parts_out])


def cat(k, shape, dt=np.float32, fill=0.0):
    return np.concatenate([np.broadcast_to(np.asarray(p[k], float), (len(p['V']),) + shape) if k in p
                           else np.full((len(p['V']),) + shape, fill) for p in parts_out]).reshape((N,) + shape).astype(dt)


floor = float(pos[:, 1].min())
header = dict(format='engine/body', version=1, id='vera-bilibin', label={'ru': 'Вера (Билибин)'}, topology='vera-bilibin',
              skeleton='soma', source='to3d/r17-s17-vera/tools/build.py', floor=floor, pieces=PIECES, ranges=ranges,
              K=K, FEET=FEET, ZOFF=ZOFF, neckZ=NECK_Z, skirt=[srows, scols],
              roses=[[*map(float, q[0]), *map(float, q[1]), *map(float, q[2]), float(q[3])] for q in roses],
              knot=[float(x) for x in BUN],
              head=dict((k, getattr(P, k)) for k in vars(P) if isinstance(getattr(P, k), (int, float, str, tuple, list))))
pack.save(os.path.join(OUT, 'vera.json'), header, dict(
    positions=pos, triangles=tri, skinJoints=SJ, skinWeights=SW,
    joints=J.astype(np.float32).ravel(), frames=FR.ravel(),
    mat=matv.astype(np.uint8), em=cat('em', (), fill=100.0), ea=cat('ea', ()), hs=cat('hs', ()),
    two=cat('two', (), np.uint8), dr=cat('dr', (3,))))
print('pack', N, 'vertices', len(tri), 'triangles; height', round(float(pos[:, 1].max() - floor), 3), 'ZOFF', round(ZOFF, 4),
      'waist', round(WAIST, 3), 'hem', round(HEM, 3))
