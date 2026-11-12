"""Марат (С13, woodblock print) in 3D: the form — a skinned mesh on SOMA's 77 joints, in pieces.
  python3 form.py [outdir]      → <cache>/form/marat.json/.bin  (build.py turns it into the pack the page draws)

Bases:
  body  — Anny's stocky man from the engine (engine/data/bodies/anny-T-man-stocky-baby15: Anny's own settings — wide
          shoulders, thick limbs), × 1.05; of it are seen the forearms (made thicker), the hands (bigger) and the feet
          (smoothed into shoes); its legs, pushed out, are the trousers; its skeleton and weights carry everything;
  head  — Blender Human Base Meshes' stylised head (CC0), fitted to the drawing's front and side outlines (head.py);
  beard, hair — grown from that head: the beard is the lower face's own surface lifted and smoothed into one mass;
          the hair is a cap of round lumps (the drawing's curls: a scalloped edge);
  jacket, collar, sleeves, apron, straps, towel — shells built here from the figure's measures."""
import os, sys
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M, head as Hd, drawing as D

K, KF = D.K, D.KF
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/cache/to3d-r13-s13-marat/form'
HBM = '/home/user/cache/to3d-r1-s3-anya/hbm_head.npz'      # Р1's export of the bundle's head (to3d/r1-s3-anya/notes.md)
os.makedirs(OUT, exist_ok=True)
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))
ydr = lambda y: D.FLOOR - np.asarray(y, float) / K           # metres → head units (y down from the eye line)
SC = 1.05

# ---------------------------------------------------------------- skeleton and Anny's body
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body('anny-T-man-stocky-baby15')
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


J1 = J0 * SC
J1[I['Neck1']] = [0, 1.555, -0.03]
J1[I['Neck2']] = [0, 1.61, -0.02]
J1[I['Head']] = [0, D.EYE - 100 * K, -0.01]
J1[I['HeadEnd']] = [0, D.EYE + 100 * K, -0.01]
J1[I['Jaw']] = [0, D.EYE - 40 * K, 0.02]
for s, sg in (('Left', 1), ('Right', -1)):
    J1[I[s + 'Eye']] = [sg * 33 * K, D.EYE, 0.08]
    for j in under(I[s + 'Shoulder']): J1[j, 1] += 0.02           # heavy shoulders sit high: a short neck
    for j in under(I[s + 'Hand'])[1:]:                             # big hands
        J1[j] = J1[PARENT[j]] + 1.15 * (J1[j] - J1[PARENT[j]])
    for n, x in (('Shin', 0.165), ('Foot', 0.18)):                 # the stance a little narrower than the base's
        dx = sg * x - J1[I[s + n], 0]
        for j in under(I[s + n]): J1[j, 0] += dx


def joint_affine(j):
    n = NAMES[j]; A = SC * np.eye(3)
    if n.endswith('ForeArm'):                                      # thick forearms
        c = [k for k in range(NJ) if PARENT[k] == j][0]
        d = J0[c] - J0[j]; d /= np.linalg.norm(d)
        A = SC * (1.22 * np.eye(3) + (1 - 1.22) * np.outer(d, d))
    elif 'Hand' in n: A = SC * 1.15 * np.eye(3)
    elif 'Foot' in n or 'Toe' in n: A = SC * np.diag([1.12, 1.0, 1.08])
    return A


AFF = [joint_affine(j) for j in range(NJ)]


def deform(P, SJ, SW):
    out = np.zeros_like(P)
    for k in range(4):
        for j in np.unique(SJ[:, k]):
            m = (SJ[:, k] == j) & (SW[:, k] > 0)
            out[m] += SW[m, k, None] * (J1[j] + (P[m] - J0[j]) @ AFF[j].T)
    return out


PF = deform(P0, SJ0, SW0)
dom = SJ0[np.arange(len(SJ0)), SW0.argmax(1)]
dn = np.array([NAMES[j] for j in dom])
arm = np.array([(n.endswith('ForeArm') or 'Hand' in n) for n in dn])
near_elbow = np.zeros(len(P0), bool)
for s in ('Left', 'Right'): near_elbow |= np.linalg.norm(PF - J1[I[s + 'ForeArm']], axis=1) < 0.10
keep_arm = arm | (near_elbow & np.array([n.endswith('Arm') for n in dn]))
keep_leg = PF[:, 1] < 0.97
keep = keep_arm | (keep_leg & ~arm)


def sub(mask):
    tk = mask[TRI0].all(1); bi = np.where(mask)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
    W = np.zeros((len(bi), NJ))
    for q in range(4): np.add.at(W, (np.arange(len(bi)), SJ0[bi, q]), SW0[bi, q])
    return dict(V=PF[bi].copy(), T=remap[TRI0[tk]], W=W, src=bi)


ARMS = sub(keep_arm)
LEGS = sub(keep_leg & ~arm & (PF[:, 1] > 0.062))
# trousers: the legs pushed out and smoothed into wide tubes; shoes: the feet smoothed into one rounded form
lv = LEGS['V']; nL = len(lv)
AL = M.adjacency(nL, [list(t_) for t_ in LEGS['T']])
shoe = lv[:, 1] < 0.075
nrm = M.vertex_normals(lv, LEGS['T'])
tro = ~shoe
push = 0.046 * smooth((lv[:, 1] - 0.07) / 0.05) * (1 - 0.25 * smooth((lv[:, 1] - 0.5) / 0.4)) * (1 - 0.85 * smooth((lv[:, 1] - 0.74) / 0.1))
lv[tro] += (nrm * push[:, None])[tro] * [1, 0.15, 1]
lv = M.smooth(lv, AL, tro & (lv[:, 1] > 0.10), iters=6, lam=0.5)
# the trouser's hem: a clean ring just over the shoe
LEGS['V'] = lv
# the cloth's own coordinates for the printed checks: round the leg, down the leg
uvL = np.zeros((nL, 2))
for s, sg in (('Left', 1), ('Right', -1)):
    m = np.sign(lv[:, 0]) == sg
    A_, B_ = J1[I[s + 'Leg']], J1[I[s + 'Foot']]
    ax = (B_ - A_) / np.linalg.norm(B_ - A_)
    r = lv[m] - A_; hgt = r @ ax; rad = r - np.outer(hgt, ax)
    e1 = np.array([0, 0, 1.0]) - ax * ax[2]; e1 /= np.linalg.norm(e1); e2 = np.cross(ax, e1)
    ang = np.arctan2(rad @ e2 * sg, -(rad @ e1))        # the seam at the back
    uvL[m] = np.c_[ang / (2 * np.pi) * 16 * 0.035, hgt]
LEGS['uv'] = uvL

def grid(rows, cols, closed):
    T = []
    cn = cols if closed else cols - 1
    for r in range(rows - 1):
        for c in range(cn):
            a0, a1 = r * cols + c, r * cols + (c + 1) % cols
            b0, b1 = a0 + cols, a1 + cols
            T += [[a0, b0, a1], [a1, b0, b1]]
    return np.array(T)


# shoes: soft black slippers as drawn — one rounded form over each foot (the body's foot stays inside)
SH = []
for s, sg in (('Left', 1), ('Right', -1)):
    F_, T_e = J1[I[s + 'Foot']], J1[I[s + 'ToeEnd']]
    z0, z1 = F_[2] - 0.085, T_e[2] + 0.045; cx0, cx1 = F_[0], T_e[0]
    V_ = []; nr, ncol = 22, 24
    for i in range(nr):
        u_ = i / (nr - 1); e = np.sqrt(max(0.0, 1 - (2 * u_ - 1) ** 2)) ** 0.55
        wd = 0.068 * e * np.interp(u_, [0, 0.35, 0.75, 1], [0.92, 1.0, 1.08, 0.95])
        ht = np.interp(u_, [0, 0.25, 0.45, 0.7, 1], [0.105, 0.125, 0.11, 0.078, 0.06]) * (0.35 + 0.65 * e)
        for k in range(ncol):
            ph = 2 * np.pi * k / ncol; c_, s_ = np.cos(ph), np.sin(ph)
            V_.append([cx0 + (cx1 - cx0) * u_ + wd * np.sign(c_) * abs(c_) ** 0.7, ht / 2 + ht / 2 * np.sign(s_) * abs(s_) ** 0.6, z0 + (z1 - z0) * u_])
    V_ = np.array(V_); T_ = grid(nr, ncol, True)
    if (M.vertex_normals(V_, T_) * (V_ - V_.mean(0))).sum(1).mean() < 0: T_ = T_[:, ::-1]
    W_ = np.zeros((len(V_), NJ)); tb = smooth((V_[:, 2] - J1[I[s + 'ToeBase'], 2] + 0.02) / 0.05)
    W_[:, I[s + 'Foot']] = 1 - tb; W_[:, I[s + 'ToeBase']] = tb
    SH.append(dict(V=V_, T=T_, W=W_, side=s))

# ---------------------------------------------------------------- the head
hv, hP, eyes, er, vis = Hd.load(HBM)
dd = np.load(HBM)
(hv2,) = Hd.fit(hv, Hd.ears(hv))
hv2[:, 2] += -0.01
REG = [(33, 0, 24, 17), (-33, 0, 24, 17)]            # the eyes are drawn: the sockets laid onto one smooth surface
V0 = Hd.flatten(hv2, REG, front_min=0.02)
nh = len(V0)
earm = Hd.ears(hv)
HT = M.triangulate(hP)
# drop the eye sockets' and the mouth's inner faces? they stay inside; the outer picture hides them
xd, yd = V0[:, 0] / K, ydr(V0[:, 1]); zs = -(V0[:, 2] + 0.01) / K        # side coordinate: the front is negative
Hh = dict(V=V0, T=HT)
SW = np.zeros((nh, NJ))
sA = smooth((yd - 96) / 50)
SW[:, I['Head']] = 1 - sA; SW[:, I['Neck2']] = sA * 0.7; SW[:, I['Neck1']] = sA * 0.3
Hh['W'] = SW
nrmH = M.vertex_normals(V0, HT)
AH = M.adjacency(nh, hP)

# the beard: the lower face's own surface (subdivided once, for a smooth edge), lifted off the skin and smoothed into
# one mass (parts: marat.BEARDS)
V0s, hPs = M.catmull_clark(V0, hP, 1); V0s = np.asarray(V0s)
nrmS = M.vertex_normals(V0s, M.triangulate(hPs))
xs_, ys_, zs_ = V0s[:, 0] / K, ydr(V0s[:, 1]), -(V0s[:, 2] + 0.01) / K
ears_ = earm[cKDTree(V0).query(V0s)[1]] & (zs_ > 2)          # the ear itself (the mask also takes the cheek before it)
top = np.interp(zs_, [-90, -60, -36, -16, -6, 2], [46, 42, 42, 24, -10, -40])      # its upper edge, by the side view
wb_ = smooth((-14 - zs_) / 24); top = top * (1 - wb_) + np.minimum(top, np.interp(np.abs(xs_), [0, 30, 56, 70, 80], [46, 43, 36, 14, -8])) * wb_
top = top + 6 * (1 - smooth((np.abs(xs_) - 8) / 12)) * (zs_ < -40)              # parted under the nose: the nose's tip stays on skin
back = np.interp(ys_, [-40, -12, 30, 68, 100, 130], [2, 2, 2, 3, -16, -30])              # its back edge: before the ear, under the jaw
inb = (ys_ > top) & (zs_ < back) & (ys_ < 122) & ~ears_
fb = np.array([inb[p].all() for p in hPs])
bP = [p for p, k in zip(hPs, fb) if k]
bi = np.unique(np.concatenate(bP)); rm = -np.ones(len(V0s), int); rm[bi] = np.arange(len(bi))
bP = [[int(rm[i]) for i in p] for p in bP]
BV = V0s[bi].copy(); bn = nrmS[bi]; byd = ys_[bi]; bzs = zs_[bi]
BT = M.triangulate(bP); AB = M.adjacency(len(BV), bP)
edge = np.zeros(len(BV), bool)
for L in M.boundary_loops(bP): edge[L] = True
depth = np.ones(len(BV)); cur = edge.copy(); depth[edge] = 0        # how far from the beard's edge (in rings)
for r_ in range(1, 24):
    nb_ = (AB @ cur.astype(float)) > 0; new = nb_ & ~cur & (depth == 1) if r_ == 1 else nb_ & ~cur
    depth[nb_ & ~cur] = r_; cur |= nb_
depth[~cur] = 24; depth = depth / 2
thick = (2 + 13 * smooth(depth / 4)) * K * (0.6 + 0.4 * smooth((byd - 20) / 50))
BV += bn * thick[:, None]
low = smooth((byd - 62) / 40) * smooth((-bzs + 10) / 50)            # the chin's mass hangs lower, forward
BV[:, 1] -= low * 22 * K * (~edge); BV[:, 2] += low * 6 * K * (~edge)
BV = M.smooth(BV, AB, ~edge, iters=40, lam=0.5)
lift = ((BV - V0s[bi]) * bn).sum(1); need = np.where(edge, 0.6, 3.5 + 3.5 * smooth(depth / 3)) * K      # never under the skin
BV += bn * np.clip(need - lift, 0, None)[:, None]
BV = M.smooth(BV, AB, ~edge, iters=2, lam=0.5)
lift = ((BV - V0s[bi]) * bn).sum(1); BV += bn * np.clip(np.where(edge, 0.6, 3.0) * K - lift, 0, None)[:, None]
Bd = dict(V=BV, T=BT, W=np.tile(np.eye(NJ)[I['Head']], (len(BV), 1)))

# the hair: a cap of round lumps over the skull (marat.HAIRS: about 12 hu over the skull, a scalloped edge)
C = np.array([0, D.EYE + 22 * K, -0.012])
skull = ~earm & (yd < 60)
dirs = V0[skull] - C; rad = np.linalg.norm(dirs, axis=1); dirs /= rad[:, None]
DT = cKDTree(dirs)
nlat, nlon = 56, 120
rng = np.random.default_rng(13)
# lump centres: even over the sphere (a golden spiral), jittered
nl = 110; kk = np.arange(nl) + 0.5
phi = np.arccos(1 - 2 * kk / nl); tht = np.pi * (1 + 5 ** 0.5) * kk
LC = np.c_[np.sin(phi) * np.cos(tht), np.cos(phi), np.sin(phi) * np.sin(tht)] + rng.normal(0, 0.035, (nl, 3))
LC /= np.linalg.norm(LC, axis=1, keepdims=True)
LT = cKDTree(LC)
HV, ok = [], []
for i in range(nlat):
    la = np.pi * 0.74 * i / (nlat - 1)                 # from the crown down
    for j in range(nlon):
        lo = 2 * np.pi * j / nlon
        dv = np.array([np.sin(la) * np.sin(lo), np.cos(la), np.sin(la) * np.cos(lo)])
        d_, ii = DT.query(dv, 6); w = 1 / (d_ + 0.02) ** 2
        r0 = (rad[ii] * w).sum() / w.sum()
        p0 = C + dv * r0
        x_, y_, z_ = p0[0] / K, float(ydr(p0[1])), -(p0[2] + 0.01) / K
        # the hairline (front: marat.HAIRS f inner; side and nape: s inner and outer ends), with small scallops
        hl_f = np.interp(abs(x_), [0, 44, 70, 84], [-70, -62, -40, -14])
        hl_s = np.interp(z_, [-20, 6, 22, 40, 70, 100], [-48, -28, -8, 14, 34, 40])
        tb = smooth((z_ + 44) / 40)
        hl = hl_f * (1 - tb) + hl_s * tb + 3.5 * np.sin(lo * 15)
        inside = hl - y_                                # > 0: under hair
        dl, li = LT.query(dv, 1)
        lump = max(0.0, 1 - (dl / 0.215) ** 2) ** 0.5
        t_ = (2 + 5 * smooth(inside / 14) + 18 * lump * smooth(inside / 6)) * K
        HV.append(p0 + dv * t_); ok.append(inside > -1.5)
HV = np.array(HV); ok = np.array(ok)
gt = []
for i in range(nlat - 1):
    for j in range(nlon):
        a0, a1 = i * nlon + j, i * nlon + (j + 1) % nlon; b0, b1 = a0 + nlon, a1 + nlon
        gt += [[a0, b0, a1], [a1, b0, b1]]
gt = np.array(gt); gt = gt[ok[gt].all(1)]
used = np.unique(gt); rm = -np.ones(len(HV), int); rm[used] = np.arange(len(used))
HAIR = dict(V=HV[used], T=rm[gt], W=np.tile(np.eye(NJ)[I['Head']], (len(used), 1)), grid=(nlat, nlon), gridmap=rm, lumps=LC, centre=C)
if (M.vertex_normals(HAIR['V'], HAIR['T']) * (HAIR['V'] - C)).sum(1).mean() < 0: HAIR['T'] = HAIR['T'][:, ::-1]


# ---------------------------------------------------------------- lofted shells
def ring(a_, zc, df, db, th, p=2.5):
    s, c = np.sin(th), np.cos(th)
    x = a_ * np.sign(s) * np.abs(s) ** (2 / p)
    z = zc + np.where(c > 0, df, db) * np.sign(c) * np.abs(c) ** (2 / p)
    return x, z


# the jacket: (height m, half-width, front, back) — a barrel: the belly forward, the back straight
JK = np.array([(1.535, 0.262, 0.150, -0.150), (1.47, 0.268, 0.185, -0.158), (1.38, 0.274, 0.215, -0.160),
               (1.25, 0.282, 0.250, -0.158), (1.12, 0.288, 0.268, -0.155), (1.00, 0.286, 0.262, -0.158),
               (0.90, 0.280, 0.240, -0.165), (0.815, 0.274, 0.222, -0.168)])


def jk(y):
    o = np.argsort(JK[:, 0]); return [np.interp(y, JK[o, 0], JK[o, k]) for k in (1, 2, 3)]


jrows = []
for tt in np.linspace(1, 0, 11)[:-1]:          # the yoke: the neck's ring → the shoulders' ring, round shoulders
    yv = 1.535 + 0.085 * (1 - (1 - tt) ** 2.0)
    a_ = 0.262 * (1 - tt) ** 0.75 + 0.082 * (1 - (1 - tt) ** 0.75)
    zf = 0.150 * (1 - tt) + 0.085 * tt; zb = -0.150 * (1 - tt) - 0.105 * tt
    jrows.append((yv, a_, (zf + zb) / 2, (zf - zb) / 2, (zf - zb) / 2))
for yy in np.r_[np.arange(1.535, 0.83, -0.03)[1:], 0.815]:
    a_, zf, zb = jk(yy); jrows.append((yy, a_, (zf + zb) / 2, (zf - zb) / 2, (zf - zb) / 2))
JC = 80
JV = []
for (yy, aa, zc, df, db) in jrows:
    x, z = ring(aa, zc, df, db, np.linspace(0, 2 * np.pi, JC, endpoint=False))
    JV += list(np.c_[x, np.full(JC, yy), z])
JV = np.array(JV); JT = grid(len(jrows), JC, True)
Jk = dict(V=JV, T=JT, rows=len(jrows), cols=JC)


def jsurf(x, y, front=True):
    """The jacket's surface at height y and side x: its z in front (or behind)."""
    o = np.argsort([r[0] for r in jrows]); R = np.array(jrows)[o]
    aa, zc, df = [np.interp(y, R[:, 0], R[:, k]) for k in (1, 2, 3)]
    s = np.clip(abs(x) / aa, 0, 1) ** (2.5 / 2); c = np.sqrt(1 - s * s)
    return zc + (1 if front else -1) * df * c ** (2 / 2.5)


# the collar: a soft thick roll round the neck, lower in front
CV = []; cc, cr = 48, 14
for i in range(cc):
    th_ = 2 * np.pi * i / cc
    cf = max(0.0, np.cos(th_))
    cx, cz = 0.118 * np.sin(th_), -0.022 + (0.112 + 0.062 * cf ** 2) * np.cos(th_)
    cy = 1.622 - 0.012 * np.cos(th_) - 0.046 * cf ** 1.5
    ro = 0.033 + 0.007 * np.cos(th_)
    for k in range(cr):
        ph = 2 * np.pi * k / cr
        CV.append([cx + ro * np.cos(ph) * np.sin(th_), cy + ro * 1.1 * np.sin(ph), cz + ro * np.cos(ph) * np.cos(th_)])
CV = np.array(CV)
CT = np.array([[i * cr + k, ((i + 1) % cc) * cr + k, i * cr + (k + 1) % cr] for i in range(cc) for k in range(cr)] +
              [[((i + 1) % cc) * cr + k, ((i + 1) % cc) * cr + (k + 1) % cr, i * cr + (k + 1) % cr] for i in range(cc) for k in range(cr)])
if (M.vertex_normals(CV, CT) * (CV - CV.mean(0))).sum(1).mean() < 0: CT = CT[:, ::-1]
Cl = dict(V=CV, T=CT)


def tube(path, radii, cols=24):
    path = np.asarray(path); V = []
    ref = np.array([0, 0, 1.0])
    for i, p in enumerate(path):
        tg = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]; tg /= np.linalg.norm(tg)
        n1 = ref - tg * (ref @ tg); n1 /= np.linalg.norm(n1); n2 = np.cross(tg, n1)
        for th_ in np.linspace(0, 2 * np.pi, cols, endpoint=False):
            V.append(p + radii[i] * (np.cos(th_) * n1 + np.sin(th_) * n2))
    return np.array(V), grid(len(path), cols, True)[:, ::-1]


# sleeves, rolled up over the elbow: a wide tube with a thick roll at its end
SL = []
for s in ('Left', 'Right'):
    A_, E_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']]
    d1 = (E_ - A_) / np.linalg.norm(E_ - A_); Ln = np.linalg.norm(E_ - A_)
    us = np.r_[np.linspace(-0.22, 0.80, 14), 0.84, 0.88, 0.92, 0.96, 0.99, 1.0]
    rs = np.r_[np.interp(np.linspace(-0.22, 0.80, 14), [-0.22, -0.1, 0.05, 0.25, 0.8], [0.03, 0.066, 0.086, 0.092, 0.086]), 0.089, 0.094, 0.095, 0.092, 0.084, 0.070]
    V_, T_ = tube([A_ + d1 * u_ * Ln for u_ in us], rs, 28)
    if (M.vertex_normals(V_, T_) * (V_ - (A_ + E_) / 2)).sum(1).mean() < 0: T_ = T_[:, ::-1]
    SL.append(dict(V=V_, T=T_, side=s))

# the long apron: a bib on the chest, from the waist a wide panel round the front, down to the shins
arows = np.r_[np.arange(1.41, 0.32, -0.03), 0.31]
AC = 41
AV = []
for yy in arows:
    yj = max(yy, 0.815)
    aa, zf, zb = jk(yj)
    if yy < 0.815:                     # below the jacket's hem it hangs: a little narrower, straight
        k_ = 1 - 0.10 * smooth((0.815 - yy) / 0.5); aa, zf = aa * k_, zf * (1 - 0.22 * smooth((0.815 - yy) / 0.3))
    zc, df = (zf + zb) / 2, (zf - zb) / 2
    hw = np.interp(yy, [0.31, 1.06, 1.14, 1.20, 1.41], [0.262, 0.270, 0.270, 0.170, 0.118])     # half-width on the front
    hw = min(hw, aa * 0.985)
    g = np.arcsin(np.clip(hw / aa, 0, 1) ** (2.5 / 2))
    gw = np.radians(np.interp(yy, [0.31, 1.06, 1.125], [50, 52, 50]))                            # from the waist it wraps round the sides
    tw = smooth((1.185 - yy) / 0.06); g = g * (1 - tw) + gw * tw
    x, z = ring(aa + 0.012, zc, df + 0.012, df + 0.012, np.linspace(-g, g, AC))
    AV += list(np.c_[x, np.full(AC, yy), z])
AV = np.array(AV); AT = grid(len(arows), AC, False)
if (M.vertex_normals(AV, AT)[:, 2]).mean() < 0: AT = AT[:, ::-1]
Ap = dict(V=AV, T=AT, rows=len(arows), cols=AC)
Ap['uv'] = np.c_[np.tile(np.linspace(-1, 1, AC), len(arows)) * np.repeat([np.interp(yy, [0.31, 1.06, 1.14, 1.20, 1.41], [0.235, 0.245, 0.245, 0.170, 0.118]) for yy in arows], AC), AV[:, 1]]


def ribbon(path, across, width, cols=5):
    """A strip along a path of points, `across` its unit side direction at each."""
    V = []
    for p, c in zip(path, across):
        for u_ in np.linspace(-0.5, 0.5, cols): V.append(p + c * u_ * width)
    return np.array(V), grid(len(path), cols, False)


def over_shoulder(x, y0f, y0b, off, n=16):
    """Points of a line over the shoulder at side x: up the jacket's front from y0f, over the yoke, down the back."""
    pts = []
    ytop = None
    for yy in np.linspace(y0f, 1.62, 60):
        o = np.argsort([r[0] for r in jrows]); R = np.array(jrows)[o]
        if abs(x) >= np.interp(yy, R[:, 0], R[:, 1]) * 0.97: ytop = yy; break
        pts.append([x, yy, jsurf(x, yy, True) + off])
    zf_, zb_ = pts[-1][2], jsurf(x, pts[-1][1], False) - off
    top = pts[-1][1] + off
    for u_ in np.linspace(0, 1, 9)[1:-1]:
        pts.append([x, top + 0.012 * np.sin(np.pi * u_), zf_ + (zb_ - zf_) * u_])
    for yy in np.linspace(pts[-1][1] - off, y0b, 20):
        if abs(x) < jk(max(yy, 0.815))[0] or True:
            o = np.argsort([r[0] for r in jrows]); R = np.array(jrows)[o]
            if abs(x) >= np.interp(yy, R[:, 0], R[:, 1]) * 0.97: continue
            pts.append([x, yy, jsurf(x, yy, False) - off])
    pts = np.array(pts)
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    return np.array([[np.interp(s_, L, pts[:, k]) for k in range(3)] for s_ in np.linspace(0, L[-1], n)]), L[-1]


# the towel over his left shoulder (stripes along it); the apron's straps (thin, from the bib's corners to the neck)
tp, tl = over_shoulder(0.172, 1.27, 1.30, 0.016, 40)
TV, TT = ribbon(tp, np.tile([1.0, 0, 0], (len(tp), 1)), 0.10, 7)
if M.vertex_normals(TV, TT)[:7 * 8, 2].mean() < 0: TT = TT[:, ::-1]
Tw = dict(V=TV, T=TT, uv=np.c_[np.tile(np.linspace(-0.5, 0.5, 7) * 0.105, len(tp)), np.repeat(np.linspace(0, tl, len(tp)), 7)])
ST = []
for sg in (1, -1):
    sp, _ = over_shoulder(sg * 0.105, 1.405, 1.30, 0.007, 30)
    sp[:, 0] = sg * np.interp(np.arange(len(sp)), [0, 8, 14, 29], [0.110, 0.098, 0.095, 0.10])
    for k_ in range(len(sp)):                      # keep it on the jacket as it moves in
        if k_ < 9: sp[k_, 2] = jsurf(sp[k_, 0], sp[k_, 1], True) + 0.007
    V_, T_ = ribbon(sp, np.tile([1.0, 0, 0], (len(sp), 1)), 0.022, 3)
    if M.vertex_normals(V_, T_)[:9, 2].mean() < 0: T_ = T_[:, ::-1]
    ST.append(dict(V=V_, T=T_, side='Left' if sg > 0 else 'Right'))

# ---------------------------------------------------------------- weights for what is built here
FT = cKDTree(PF)
ARMJ = np.zeros(NJ, bool)
for s in ('Left', 'Right'): ARMJ[under(I[s + 'Arm'])] = True
LOWARM = np.zeros(NJ, bool)
for s in ('Left', 'Right'): LOWARM[under(I[s + 'ForeArm'])] = True


def transfer(V, k=6):
    dd_, ii = FT.query(V, k)
    w = 1 / (dd_ + 1e-3) ** 2; w /= w.sum(1, keepdims=True)
    W = np.zeros((len(V), NJ))
    for c in range(k):
        for q in range(4): np.add.at(W, (np.arange(len(V)), SJ0[ii[:, c], q]), w[:, c] * SW0[ii[:, c], q])
    return W


def smooth_w(W, T, n, iters=12):
    A = M.adjacency(n, [list(t_) for t_ in T])
    return M.smooth(W, A, np.ones(n, bool), iters, 0.5)


def torso_w(V, T, hang_from=0.98, hang=0.55):
    """A shell on the trunk: the body's nearest weights without the arms (but the shoulder's), below the hips a skirt:
    part on the hips, part on the leg of its side."""
    W = transfer(V)
    sh = smooth((V[:, 1] - 1.44) / 0.06) * smooth((np.abs(V[:, 0]) - 0.17) / 0.06)       # the shoulder cap goes with the arm
    W[:, LOWARM] = 0
    W[:, ARMJ] *= sh[:, None]
    W /= W.sum(1, keepdims=True) + 1e-12
    yv = V[:, 1]
    L = hang * smooth((hang_from - yv) / 0.45)
    side = 1 / (1 + np.exp(-V[:, 0] / 0.05))
    S = np.zeros_like(W); S[:, I['LeftLeg']] = L * side; S[:, I['RightLeg']] = L * (1 - side); S[:, I['Hips']] = 1 - L
    uu = smooth((1.02 - yv) / 0.12)[:, None]
    W = (1 - uu) * W + uu * S
    return smooth_w(W, T, len(V), 10)


Jk['W'] = torso_w(JV, JT, hang=0.35)
Ap['W'] = torso_w(AV, AT, hang=0.5)
Cl['W'] = np.zeros((len(CV), NJ)); Cl['W'][:, I['Chest']] = 0.5; Cl['W'][:, I['Neck1']] = 0.5
Tw['W'] = torso_w(TV, TT)
for S_ in ST: S_['W'] = torso_w(S_['V'], S_['T'])
for S_ in SL:
    side = S_['side']; W = transfer(S_['V'])
    tr = np.zeros(NJ, bool); tr[under(I[side + 'Shoulder'])] = True
    Wa = W * tr; Wa /= Wa.sum(1, keepdims=True) + 1e-9
    topw = smooth(np.linalg.norm(S_['V'] - J1[I[side + 'Arm']], axis=1) / 0.07)
    S_['W'] = smooth_w(Wa * topw[:, None] + W * (1 - topw[:, None]), S_['T'], len(S_['V']))

# ---------------------------------------------------------------- one pack
pieces = [('arms', ARMS), ('legs', LEGS), ('head', Hh), ('beard', Bd), ('hair', HAIR), ('jacket', Jk), ('collar', Cl)] + \
         [('sleeve' + S_['side'], S_) for S_ in SL] + [('apron', Ap), ('towel', Tw)] + [('strap' + S_['side'], S_) for S_ in ST] + [('shoe' + S_['side'], S_) for S_ in SH]
Vs, Ts, Ws, uvs = [], [], [], []
base = 0; ranges = {}; tbase = 0; tranges = {}
for name, p in pieces:
    n = len(p['V'])
    Vs.append(p['V']); Ts.append(p['T'] + base); Ws.append(p['W'])
    uvs.append(p.get('uv', np.zeros((n, 2))))
    ranges[name] = [base, base + n]; tranges[name] = [tbase, tbase + len(p['T'])]; base += n; tbase += len(p['T'])
V = np.vstack(Vs); W = np.maximum(np.vstack(Ws), 0); N = len(V)
order = np.argsort(-W, 1)[:, :4]
SJ = order.astype(np.uint8); SWt = np.take_along_axis(W, order, 1); SWt /= SWt.sum(1, keepdims=True)
np.save(os.path.join(OUT, 'hairgrid.npy'), HAIR['gridmap'])
pack.save(os.path.join(OUT, 'marat.json'),
          dict(format='r13/form', version=1, id='marat-s13', label={'ru': 'Марат, укиё-э'},
               source='Anny stocky man (engine) + Human Base Meshes stylised head (CC0) + shells from the drawing',
               pieces=ranges, trianglePieces=tranges, grids=dict(jacket=[Jk['rows'], JC], apron=[Ap['rows'], AC], hair=[nlat, nlon], towel=[len(tp), 7]),
               hairCentre=[float(c) for c in C]),
          dict(positions=V.astype(np.float32).ravel(), triangles=np.vstack(Ts).astype(np.uint32).ravel(),
               skinJoints=SJ, skinWeights=SWt.astype(np.float32), joints=J1.astype(np.float32).ravel(), frames=FR.ravel(),
               uv=np.vstack(uvs).astype(np.float32),
               lumps=LC.astype(np.float32).ravel()))
print('vertices', N, 'triangles', sum(len(t_) for t_ in Ts), {k: v[1] - v[0] for k, v in ranges.items()})
