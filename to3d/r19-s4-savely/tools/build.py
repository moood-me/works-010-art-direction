"""Вера (Arcane) in 3D: builds the character pack that the viewer (web/vera.js) and the engine take.
  python3 build.py CACHE            → CACHE/out/vera.json|bin, CACHE/out/face.json
Bases: Anny's body (engine/data/bodies/moood-woman: mesh, SOMA skeleton and weights) for the body, arms, hands and
legs; Blender's Human Base Meshes head «for animation» (CC0) fitted to the drawing (fit_head.py) with its eyeballs;
the hair, the bun, the coat, the skirt, the collar and the glasses made here from the drawing's numbers
(styles/s4-arcane/tools/cast.py, vera()). Everything is skinned to SOMA's 77 joints.
Units: metres; the drawing's units map as world = (x·K, (FEET − y)·K, z·K + ZOFF)."""
import os, sys, json
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack, mesh as M, drawing as DR  # noqa: E402
from arc import interp  # noqa: E402

C = sys.argv[1] if len(sys.argv) > 1 else '/home/user/cache/to3d-r7-s4-vera'
OUT = os.path.join(C, 'out')
os.makedirs(OUT, exist_ok=True)
K = 0.00097
FEET = float(DR.FEET)
sm = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))
P = DR.vera()
HEAD, NOSE, NECK = DR.surfaces(P)


def rgb(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)
def mix(a, b, t): return a + (b - a) * t


# ---------------------------------------------------------------- materials: the drawing's paints
# base, shadow (Arcane: skin into red-brown, cloth into a cool violet), the warm band at the shadow's edge, the rim
SKIN = rgb('#ecccb8')
MAT = {
    'skin':   (SKIN, rgb('#b07a72'), rgb('#d8644c'), rgb('#c8e0ff')),
    'lips':   (rgb('#b26862'), rgb('#7e3c3c'), rgb('#c04a40'), rgb('#c8e0ff')),
    'hair':   (rgb('#2e2629'), rgb('#141012'), rgb('#4a3236'), rgb('#9fb8d8')),
    'coat':   (rgb('#3a4757'), rgb('#232a36'), rgb('#5a4a5a'), rgb('#9fb8d8')),
    'lapel':  (rgb('#2a3442'), rgb('#1a2029'), rgb('#4a3e4e'), rgb('#9fb8d8')),
    'shirt':  (rgb('#ece6de'), rgb('#9c96a6'), rgb('#d8b8a8'), rgb('#e0f0ff')),
    'tights': (rgb('#2c2b33'), rgb('#18171d'), rgb('#4a3a44'), rgb('#9fb8d8')),
    'shoe':   (rgb('#1c1a20'), rgb('#0c0b0e'), rgb('#3a2e34'), rgb('#9fb8d8')),
    'sclera': (rgb('#e6dcd6'), rgb('#a8949a'), rgb('#e6dcd6'), rgb('#e6dcd6')),
    'iris':   (rgb('#4d6a82'), rgb('#1d2834'), rgb('#4d6a82'), rgb('#a6bac6')),
    'frame':  (rgb('#2a2226'), rgb('#141014'), rgb('#2a2226'), rgb('#8a98a8')),
    'brooch': (rgb('#8a2c36'), rgb('#4a1820'), rgb('#c0404a'), rgb('#ffd0d0')),
    'mouth':  (rgb('#5a2a2c'), rgb('#3a1a1c'), rgb('#6a2a2a'), rgb('#5a2a2c')),
    'lens':   (rgb('#dfe8f0'), rgb('#dfe8f0'), rgb('#dfe8f0'), rgb('#ffffff')),
}
MATS = list(MAT)
mi = MATS.index

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

S = (FEET + 122) * K / 1.585                       # Anny's 1.585 m → Вера's 1.725 m


def under(j):
    out, st = [], [j]
    while st:
        k = st.pop(); out.append(k); st += list(np.where(PARENT == k)[0])
    return out


LEG = 1.045                                         # Arcane: long legs (the hips go up, the trunk is shorter)
J1 = J0 * S
lift = J0[I['Hips'], 1] * S * (LEG - 1)
for s, sg in (('Left', 1), ('Right', -1)):
    for j in under(I[s + 'Leg']):
        J1[j, 1] = J0[I[s + 'Leg'], 1] * S + lift + (J0[j, 1] - J0[I[s + 'Leg'], 1]) * S * LEG
        J1[j] += [-sg * 0.008, 0, 0]
for j in range(NJ):
    if j not in under(I['LeftLeg']) and j not in under(I['RightLeg']):
        J1[j, 1] += lift * (1 - sm((J0[j, 1] * S - 1.0) / 0.45))     # the trunk keeps the shoulders' height
for s, sg in (('Left', 1), ('Right', -1)):          # shoulders a little narrower and lower (a slim woman)
    for j in under(I[s + 'Shoulder']): J1[j] += [-sg * 0.004, -0.006, 0]
    for j in under(I[s + 'Arm']): J1[j] += [-sg * 0.016, -0.01, 0]


def joint_affine(j):
    n = NAMES[j]
    if n in ('Hips',): return np.diag([0.82, 1, 0.9])
    if n in ('Spine1', 'Spine2'): return np.diag([0.8, 1, 0.88])
    if n in ('Chest',): return np.diag([0.84, 1, 0.9])
    if n.endswith('Shoulder'): return np.diag([0.88, 0.9, 0.9])
    r = {'LeftArm': 0.86, 'RightArm': 0.86, 'LeftForeArm': 0.86, 'RightForeArm': 0.86,
         'LeftLeg': 0.86, 'RightLeg': 0.86, 'LeftShin': 0.84, 'RightShin': 0.84}.get(n)
    if r:
        c = [k for k in range(NJ) if PARENT[k] == j][0]
        d = J0[c] - J0[j]; d /= np.linalg.norm(d)
        ax = r * np.eye(3) + (1 - r) * np.outer(d, d)
        if 'Leg' in n or 'Shin' in n: ax = ax + (LEG - 1) * np.outer(d, d)
        return ax
    return np.eye(3)


AFF = [joint_affine(j) for j in range(NJ)]
# the legs closer together (she stands with her feet near, as drawn; a narrow skirt): each leg turned in about its hip
LEG_IN = np.radians(4.5)
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

# ---------------------------------------------------------------- the head (drawing units → world)
hf = np.load(os.path.join(C, 'head_fit.npz'))
neck_c = PB[(abs(PB[:, 1] - (FEET - 150) * K) < 0.01) & (part("neck") > 0.3)]
ZOFF = float((neck_c[:, 2].max() + neck_c[:, 2].min()) / 2) - (-26.0 * K) + 0.004


def W(p):
    p = np.asarray(p, float)
    return np.stack([p[..., 0] * K, (FEET - p[..., 1]) * K, p[..., 2] * K + ZOFF], -1)


hv = hf['v'].copy()
# the ears a little smaller and closer to the head (they stand out of the hair)
ear = hf['ear']
for sd in (1, -1):
    m = ear & (np.sign(hv[:, 0]) == sd)
    c = hv[m].mean(0); root = c.copy(); root[0] -= sd * 6
    wgt = np.zeros(len(hv)); dd = np.linalg.norm((hv - c) / [10, 22, 16], axis=1); wgt = 1 - sm((dd - 1.0) / 0.6)
    wgt[~(np.sign(hv[:, 0]) == sd)] = 0
    hv = hv + wgt[:, None] * ((root + (hv - root) * [0.8, 0.88, 0.88]) - hv)
HT = hf['tris']
HT = HT[~(hv[HT, 1] > 152).all(1)]                # the neck's end, inside the coat's collar, is cut away
HV = W(hv)
yd_h = hv[:, 1]
# proxy normals for the face's shade: the head smoothed into big planes (Arcane's shadow is one shape)
Ah = M.adjacency(len(HV), HT)
hs = M.smooth(HV, Ah, np.ones(len(HV)), iters=45, lam=0.5)
pn = M.vertex_normals(hs, HT)
pw = 0.88 * (1 - sm((yd_h - 120) / 30)) * (1 - 0.5 * hf['ear'])
# the painted layer: front projection (faces.py frame: x −80…80, y −110…130 in drawing units)
FX0, FX1, FY0, FY1 = -80.0, 80.0, -110.0, 130.0
uv = np.c_[(hv[:, 0] - FX0) / (FX1 - FX0), 1 - (hv[:, 1] - FY0) / (FY1 - FY0)]
nh = M.vertex_normals(HV, HT)
tw = sm((nh[:, 2] - 0.0) / 0.3) * (hv[:, 2] > -10) * (np.abs(hv[:, 0]) < 79)


def chain_w(yd, n, marks):
    Wt = np.zeros((n, NJ))
    ts = [sm((yd - m) / 40) for m in marks]
    Wt[:, I['Head']] = 1 - ts[0]
    Wt[:, I['Neck2']] = ts[0] * (1 - ts[1])
    Wt[:, I['Neck1']] = ts[0] * ts[1] * (1 - ts[2])
    Wt[:, I['Chest']] = ts[0] * ts[1] * ts[2]
    return Wt


headW = chain_w(yd_h - 15 * sm(-hv[:, 2] / 40), len(HV), [115, 160, 205])

# eyes: balls (sclera, iris), rigid on the head; each vertex knows its eye (for the gaze) and its place on the iris
balls = []
for k, s in ((0, 'L'), (1, 'R')):
    for prt in ('sclera', 'iris'):
        v = hf[prt + s + '_v']; f = hf[prt + s + '_f']
        tri = np.array([[q[0], q[kk], q[kk + 1]] for q in f for kk in range(1, len([x for x in q if x >= 0]) - 1)])
        balls.append((prt, k, v, tri))
EYE_D = hf['eye_d']

# ---------------------------------------------------------------- the hair: a cap over the skull, the bun
hl = [(0, -84), (0.45, -78), (0.95, -46), (1.3, -8), (1.45, 8), (2.0, 32), (np.pi, 64)]
HC = np.array([0.0, -20.0, -8.0])                  # the hair's centre (drawing units)
outer = hf['eye_w'] == 0
sel = outer & ~hf['ear'] & ~hf['mouth_in'] & (hv[:, 1] < 90)
Hd = hv[sel] - HC
Hr = np.linalg.norm(Hd, axis=1); Hu = Hd / Hr[:, None]
dtree = cKDTree(Hu)


def head_r(d):
    dist, j = dtree.query(d, 8)
    w = 1 / (dist + 1e-3)
    return (Hr[j] * w).max(1) * 0 + (Hr[j] * w).sum(1) / w.sum(1)


def inside_hair(p):
    """p in drawing units: above the hairline? (the drawing's hairline: y over |u| round the head's axis)"""
    yy = np.clip(p[:, 1], HEAD.v0, HEAD.v1)
    z0 = np.array([interp(HEAD.z0, y) for y in yy])
    u = np.abs(np.arctan2(p[:, 0], p[:, 2] - z0))
    return p[:, 1] < np.interp(u, [q[0] for q in hl], [q[1] for q in hl])


def thick(p, t):
    """hair thickness (drawing units): fuller on the crown; at the edge (t → 1) it lies on the skin"""
    top = np.clip(-(p[:, 1] + 20) / 90, 0, 1)
    return (4.5 + 5.5 * top) * (1 - sm((t - 0.84) / 0.16)) + 0.8


NPHI, NTH = 180, 70
phis = np.linspace(-np.pi, np.pi, NPHI, endpoint=False)
rows = []
for ph in phis:
    # along this meridian from the crown down to where the hairline is crossed
    ths = np.linspace(0.0, 2.9, 300)
    d = np.stack([np.sin(ths) * np.sin(ph), -np.cos(ths), np.sin(ths) * np.cos(ph)], 1)
    pts = HC + d * head_r(d)[:, None]
    ins = inside_hair(pts)
    k = np.argmin(ins) if not ins.all() else len(ins) - 1
    rows.append(ths[max(k, 1)])
rows = np.array(rows)
rows = np.convolve(np.r_[rows[-3:], rows, rows[:3]], np.ones(7) / 7, 'valid')
HV2, HSTR = [], []
for i, ph in enumerate(phis):
    ts = np.linspace(0, 1, NTH)
    th_ = rows[i] * ts
    d = np.stack([np.sin(th_) * np.sin(ph), -np.cos(th_), np.sin(th_) * np.cos(ph)], 1)
    r = head_r(d)
    base = HC + d * r[:, None]
    HV2.append(HC + d * (r + thick(base, ts))[:, None])
HV2 = np.array(HV2)                                 # (NPHI, NTH, 3)
hair_v = HV2.reshape(-1, 3)
hair_t = []
for i in range(NPHI):
    i2 = (i + 1) % NPHI
    for j in range(NTH - 1):
        a0, a1, b0, b1 = i * NTH + j, i2 * NTH + j, i * NTH + j + 1, i2 * NTH + j + 1
        hair_t += [[a0, b0, a1], [a1, b0, b1]]
hair_t = np.array(hair_t)
# a lip under the edge: the cap's border turned in onto the skin (no gap shows from below)
# strands: they sweep from the hairline over the head back to the bun; across-coordinate = the angle round the axis
BUN = np.array([0.0, -20.0, -112.0])
ax = BUN - np.array([0.0, -40.0, 20.0]); ax /= np.linalg.norm(ax)
e1 = np.array([1.0, 0, 0]); e2 = np.cross(ax, e1); e2 /= np.linalg.norm(e2)


def strand_coord(p):
    q = p - np.array([0.0, -40.0, 20.0]); q = q - np.outer(q @ ax, ax)
    return np.arctan2(q @ e1, q @ e2)


hair_s = strand_coord(hair_v)
# the grey streak at the front: from the parting on the figure's left, sweeping back
hair_grey = np.exp(-((hair_s - 0.5) / 0.16) ** 2) * sm((hair_v[:, 2] + 40) / 40)
# the bun: a squashed ball at the back of the head, coiled
bth, bph = np.meshgrid(np.linspace(0, np.pi, 40), np.linspace(-np.pi, np.pi, 64, endpoint=False), indexing='ij')
bx = 30 * np.sin(bth) * np.cos(bph); by = 26 * np.sin(bth) * np.sin(bph); bz = 22 * np.cos(bth)
bun_v = np.stack([bx, BUN[1] + by, BUN[2] - 6 - bz], -1).reshape(-1, 3)
bun_t = []
for i in range(39):
    for j in range(64):
        j2 = (j + 1) % 64
        a0, a1, b0, b1 = i * 64 + j, i * 64 + j2, (i + 1) * 64 + j, (i + 1) * 64 + j2
        bun_t += [[a0, a1, b0], [a1, b1, b0]]
bun_t = np.array(bun_t)
bun_s = np.arctan2(bun_v[:, 1] - BUN[1], bun_v[:, 0]) * 3 + np.hypot(bun_v[:, 0], bun_v[:, 1] - BUN[1]) * 0.12
hair_all_v = np.r_[hair_v, bun_v]; hair_all_t = np.r_[hair_t, bun_t + len(hair_v)]
hair_all_s = np.r_[hair_s, bun_s]; hair_all_g = np.r_[hair_grey, np.zeros(len(bun_v))]
HRV = W(hair_all_v)
hairW = chain_w(hair_all_v[:, 1], len(HRV), [115, 160, 205])

# ---------------------------------------------------------------- glasses: rounded rectangles off the face, arms to the ears
G = P.glasses


def tube(path, radius, n=10, closed=False):
    path = np.asarray(path, float)
    V, T = [], []
    m = len(path)
    for i, p in enumerate(path):
        d = path[(i + 1) % m if closed else min(i + 1, m - 1)] - path[(i - 1) % m if closed else max(i - 1, 0)]; d /= np.linalg.norm(d)
        u = np.cross(d, [0, 0, 1.0]) if abs(d[2]) < 0.9 else np.cross(d, [1.0, 0, 0]); u /= np.linalg.norm(u)
        w = np.cross(d, u)
        r = radius[i] if np.ndim(radius) else radius
        for k in range(n):
            a_ = 2 * np.pi * k / n
            V.append(p + (u * np.cos(a_) + w * np.sin(a_)) * r)
    for i in range(m if closed else m - 1):
        for k in range(n):
            a0, a1 = i * n + k, i * n + (k + 1) % n; b0, b1 = ((i + 1) % m) * n + k, ((i + 1) % m) * n + (k + 1) % n
            T += [[a0, a1, b0], [a1, b1, b0]]
    return np.array(V), np.array(T)


def face_front(x, y):
    """the fitted head's front surface z at (x, y) (drawing units)"""
    m = (np.abs(hv[:, 0] - x) < 3) & (np.abs(hv[:, 1] - y) < 3)
    return hv[m, 2].max()


gl_v, gl_t = [], []
zf = float(hf['scleraL_v'][:, 2].max())              # the eye's front
gz = zf + G['dz'] * 0.8 + 0.0028 * P.eye_x ** 2
gy = P.eye_y + G['dy'] + 1
rx, ry = G['rx'] + 1.5, G['ry'] + 0.5
lens = []
for sd in (1, -1):
    cxg = sd * (P.eye_x + 1)
    pts = []
    for a_ in np.linspace(0, 2 * np.pi, 64, endpoint=False):
        c_, s_ = np.cos(a_), np.sin(a_)
        kk = 2 + G['square'] * 6
        r = (abs(c_) ** kk + abs(s_) ** kk) ** (-1 / kk)
        x = cxg + rx * r * c_
        pts.append((x, gy + ry * r * s_, gz - 0.004 * (x - sd * 8) ** 2 * 0.0 - 0.0028 * x * x))
    lens.append(np.array(pts))
    v, tt = tube(pts, 0.6, 8, closed=True); gl_t.append(tt + sum(len(q) for q in gl_v)); gl_v.append(v)
    # the arm: from the outer edge back over the ear
    x0 = sd * (P.eye_x + 1 + rx); z0 = gz - 0.0028 * x0 * x0
    ex = sd * (abs(hv[ear & (np.sign(hv[:, 0]) == sd), 0]).max() - 3)
    arm = [(x0, gy - 2, z0), (x0 + sd * 3, gy - 3, z0 - 10), (ex * 0.98, P.ear_y - 12, P.ear_z + 12), (ex * 0.96, P.ear_y - 13, P.ear_z - 6), (ex * 0.9, P.ear_y - 4, P.ear_z - 16)]
    v, tt = tube(arm, 0.6, 8); gl_t.append(tt + sum(len(q) for q in gl_v)); gl_v.append(v)
bridge = [(P.eye_x + 1 - rx, gy - 2, gz - 0.0028 * (P.eye_x + 1 - rx) ** 2), (0, gy - 5, gz + 1.5), (-(P.eye_x + 1 - rx), gy - 2, gz - 0.0028 * (P.eye_x + 1 - rx) ** 2)]
xs = np.linspace(-1, 1, 9)
bp = [(bridge[0][0] * (-x) if x < 0 else bridge[2][0] * x, gy - 2 - 3 * (1 - x * x), gz - 0.0028 * (P.eye_x + 1 - rx) ** 2 * x * x + 1.5 * (1 - x * x)) for x in xs]
v, tt = tube(bp, 0.55, 8); gl_t.append(tt + sum(len(q) for q in gl_v)); gl_v.append(v)
GV = W(np.vstack(gl_v)); GT = np.vstack(gl_t)[:, [0, 2, 1]]
glassW = chain_w(np.full(len(GV), 0.0), len(GV), [115, 160, 205])
# the lenses: flat glass (for the glint), a fan in each frame
lv, lt = [], []
for L_ in lens:
    c = L_.mean(0); base = sum(len(q) for q in lv)
    lv.append(np.r_[c[None], L_]); n = len(L_)
    lt.append(np.array([[base, base + 1 + i, base + 1 + (i + 1) % n] for i in range(n)]))
LV = W(np.vstack(lv)); LT = np.vstack(lt)[:, [0, 2, 1]]
lensW = chain_w(np.full(len(LV), 0.0), len(LV), [115, 160, 205])

# ---------------------------------------------------------------- Anny's body: what is kept, and the coat over it
gone = (part('head', 'neck') > 0.5) & (PB[:, 1] > W([0, 134, 0])[1])     # Anny's neck below that is the coat's stand collar
tk = ~gone[TRI0].any(1)
bi = np.where(~gone)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
bv = PB[bi].copy(); bT = remap[TRI0[tk]]; bSJ = SJ0[bi]; bSW = SW0[bi]
bp = PARTS[bi]; by = bv[:, 1]
bpart = lambda *ns: sum(bp[:, PN.index(n)] for n in ns)
hands = bpart('Lhand', 'Rhand') > 0.5
legs = bpart('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot') > 0.5
feet = bpart('Lfoot', 'Rfoot') > 0.5
WAIST = W([0, 420, 0])[1]
mat = np.full(len(bv), mi('coat'))
mat[hands] = mi('skin')
mat[legs & (by < WAIST - 0.12)] = mi('tights')
mat[feet | ((by < 0.08) & legs)] = mi('shoe')
mat[bpart('neck') > 0.5] = mi('coat')
# the coat a little off the body (cloth thickness), fuller over the chest; the sleeves end at the wrist with a cuff
nb = M.vertex_normals(bv, bT)
coat = mat == mi('coat')
wrist = np.zeros(len(bv))
for s in ('Left', 'Right'):
    jw = J1[I[s + 'Hand']]; jf = J1[I[s + 'ForeArm']]
    d = (jw - jf) / np.linalg.norm(jw - jf)
    along = (bv - jw) @ d
    side = (bpart('Lhand', 'LforeArm') if s == 'Left' else bpart('Rhand', 'RforeArm')) > 0.3
    wrist = np.maximum(wrist, side * sm((along + 0.02) / 0.012))
mat[(wrist > 0.5) & coat] = mi('skin')
coat = mat == mi('coat')
neckc = coat & (bpart('neck') > 0.3)
off = np.where(coat, 0.006, 0) + np.where(neckc, 0.006, 0) + np.where(mat == mi('shoe'), 0.004, 0) + np.where(mat == mi('tights'), 0.0012, 0)
sleeve_end = coat & (wrist > 0.0)
off = off + np.where(sleeve_end, 0.006 * (1 - wrist), 0)
bv = bv + nb * off[:, None]
# the stand collar (Anny's neck in the coat's cloth): round the fitted head's neck with a little room, its top edge level
hn = HV[(hv[:, 1] > 118) & (hv[:, 1] < 152)]
ncx = 0.0; ncz = float((hn[:, 2].max() + hn[:, 2].min()) / 2)
hang = np.arctan2(hn[:, 0] - ncx, hn[:, 2] - ncz); hrad = np.hypot(hn[:, 0] - ncx, hn[:, 2] - ncz)
nbins = 48; hb = ((hang + np.pi) / (2 * np.pi) * nbins).astype(int) % nbins
rmax = np.array([hrad[hb == k].max() if (hb == k).any() else hrad.max() for k in range(nbins)])
rmax = np.maximum(rmax, np.roll(rmax, 1)); rmax = np.maximum(rmax, np.roll(rmax, -1))
cn = neckc & (bv[:, 1] > W([0, 175, 0])[1])
ang = np.arctan2(bv[cn, 0] - ncx, bv[cn, 2] - ncz); rad = np.hypot(bv[cn, 0] - ncx, bv[cn, 2] - ncz)
want = rmax[((ang + np.pi) / (2 * np.pi) * nbins).astype(int) % nbins] + 0.006
rad2 = np.maximum(rad, want)
bv[cn, 0] = ncx + np.sin(ang) * rad2; bv[cn, 2] = ncz + np.cos(ang) * rad2
loops = M.boundary_loops(bT)
top_y = W([0, 134, 0])[1]
for lp in loops:
    lp = np.array(lp)
    if np.mean(bv[lp, 1]) > top_y - 0.03:
        bv[lp, 1] = top_y
Ab = M.adjacency(len(bv), bT)
chest = coat & (by > 1.05) & (by < 1.42) & (bv[:, 2] > -0.02) & (bpart('spine') > 0.3)
bv = M.smooth(bv, Ab, chest * sm((bv[:, 2] + 0.02) / 0.06), iters=50, lam=0.5)
toes = feet & (bv[:, 2] > 0.08)
shoe = mat == mi('shoe')
y_before = bv[:, 1].copy()
bv = M.smooth(bv, Ab, shoe * 1.0, iters=300, lam=0.5)
bv = M.smooth(bv, Ab, toes * 1.0, iters=300, lam=0.5)
nsh = M.vertex_normals(bv, bT)
bv[shoe] += nsh[shoe] * 0.004
sole = shoe & (y_before < 0.03)                      # the soles keep their height: she stands on the floor
bv[sole, 1] = np.minimum(bv[sole, 1], y_before[sole])
# the coat's body ends at the waist, its skirt is a separate A-line (below): the legs under the skirt are tights
mat[legs & (by < WAIST) & (by >= WAIST - 0.12)] = mi('tights')
# the shoes: Anny's feet below the ankle go; a lofted shoe on each foot instead (a low heel, a rounded toe)
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
        front = 0.205 * (1 - t_) ** 1.6 + 0.05 * t_ + 0.0
        front = max(front, 0.05)
        back = 0.052 - 0.01 * t_
        w = 0.043 - 0.008 * t_
        if t_ > 0.55: front = 0.05 + 0.015 * (1 - (t_ - 0.55) / 0.45)
        a_ = np.linspace(0, 2 * np.pi, cols, endpoint=False)
        ca, sa = np.cos(a_), np.sin(a_)
        L_ = np.where(ca > 0, front, back)
        p_ = 2.4
        rr = (np.abs(ca) ** p_ + np.abs(sa) ** p_) ** (-1 / p_)
        for k in range(cols):
            vs.append(base + fwd * (ca[k] * L_[k] * rr[k] - 0.0) + side * (sa[k] * w * rr[k]) + [0, y, 0])
    vs = np.array(vs)
    ts = []
    for i in range(rows - 1):
        for k in range(cols):
            a0, a1 = i * cols + k, i * cols + (k + 1) % cols; b0, b1 = a0 + cols, a1 + cols
            ts += [[a0, a1, b0], [a1, b1, b0]]
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

# the body under the skirt's top (hips, upper thighs) drawn in a little, so it never shows through the skirt
arms_ = bpart('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand', 'Lclavicle', 'Rclavicle') > 0.2
hipz = ~arms_ & (bv[:, 1] < WAIST + 0.01) & (bv[:, 1] > J1[I['LeftShin'], 1]) & (mat != mi('shoe'))
nb2 = M.vertex_normals(bv, bT)
bv[hipz] -= nb2[hipz] * 0.012 * sm((WAIST + 0.01 - bv[hipz, 1]) / 0.04)[:, None]

# ---------------------------------------------------------------- the skirt: an A-line from the waist to below the knee
def ring_body(y, pad):
    m = (abs(bv[:, 1] - y) < 0.01) & (bpart('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand') < 0.3)
    v = bv[m]
    return abs(v[:, 0]).max() + pad, v[:, 2].max() + pad, v[:, 2].min() - pad


HEM = W([0, 1210, 0])[1]
srows, scols = 30, 80
ys = np.linspace(WAIST + 0.015, HEM, srows)
SV = []
hip_y = J1[I['LeftLeg'], 1] - 0.04
for i, y in enumerate(ys):
    u = i / (srows - 1)
    axw, zfr, zbk = ring_body(min(max(y, hip_y), WAIST), 0.008)
    below = sm((hip_y - y) / 0.5)
    flare = 0.014 * below
    axw = axw + flare; zf2 = zfr + flare * 0.7; zb2 = zbk - flare * 0.8
    if y < hip_y:                                     # the legs (a little apart) stay inside
        lx, lzf, lzb = ring_body(y, 0.02)
        axw = max(axw, lx); zf2 = max(zf2, lzf); zb2 = min(zb2, lzb)
    zc = (zf2 + zb2) / 2
    th_ = np.linspace(0, 2 * np.pi, scols, endpoint=False)
    sn, cs = np.sin(th_), np.cos(th_)
    wave = 1 + 0.018 * np.sin(7 * th_ + 1.2) * u ** 1.5        # soft folds toward the hem
    p_ = 2.3
    rr = (np.abs(sn) ** p_ + np.abs(cs) ** p_) ** (-1 / p_)
    x = axw * sn * rr * wave
    z = zc + np.where(cs > 0, zf2 - zc, zc - zb2) * cs * rr * wave
    SV.append(np.c_[x, np.full(scols, y), z])
SV = np.array(SV).reshape(-1, 3)
ST = []
for r in range(srows - 1):
    for c_ in range(scols):
        a0, a1 = r * scols + c_, r * scols + (c_ + 1) % scols; b0, b1 = a0 + scols, a1 + scols
        ST += [[a0, b0, a1], [a1, b0, b1]]
ST = np.array(ST)
skW = np.zeros((len(SV), NJ))
yy = SV[:, 1]; side = sm((SV[:, 0] / 0.06 + 1) / 2)
down = sm((hip_y - yy) / 0.35) * 0.62
knee = sm((J1[I['LeftShin'], 1] + 0.12 - yy) / 0.15) * 0.28
skW[:, I['Hips']] = 1 - down
for s, f in (('Left', side), ('Right', 1 - side)):
    skW[:, I[s + 'Leg']] += (down - knee) * f
    skW[:, I[s + 'Shin']] += knee * f
top_band = sm((yy - (WAIST - 0.01)) / 0.02)
skW = skW * (1 - top_band)[:, None]; skW[:, I['Spine1']] += top_band

# ---------------------------------------------------------------- the collar: a stand-up collar round the neck, opening in front
NB = W([0, 150, 0])[1]                              # the neck's base
ncut = PB[(abs(PB[:, 1] - NB) < 0.008) & (part('neck', 'spine') > 0.3)]
nzc = (ncut[:, 2].max() + ncut[:, 2].min()) / 2
hvn = HV[(abs(HV[:, 1] - (NB + 0.03)) < 0.006)]
nrx = abs(hvn[:, 0]).max() + 0.006; nrz = (hvn[:, 2].max() - hvn[:, 2].min()) / 2 + 0.006
nzc = (hvn[:, 2].max() + hvn[:, 2].min()) / 2
crow, ccol = 14, 72
CV = []
for i in range(crow):
    t_ = i / (crow - 1)
    y = NB - 0.028 + t_ * 0.052
    grow = 1.05 + 0.22 * (1 - t_) ** 2 + 0.05 * t_
    angs = np.linspace(0.28 + 0.22 * t_, 2 * np.pi - 0.28 - 0.22 * t_, ccol)    # a stand collar, open in front in a narrow V
    x = nrx * grow * np.sin(angs); z = nzc + nrz * grow * np.cos(angs) + 0.004 * t_
    CV.append(np.c_[x, np.full(ccol, y), z])
CV = np.array(CV).reshape(-1, 3)
CT = []
for r in range(crow - 1):
    for c_ in range(ccol - 1):
        a0, a1 = r * ccol + c_, r * ccol + c_ + 1; b0, b1 = a0 + ccol, a1 + ccol
        CT += [[a0, a1, b0], [a1, b1, b0]]
CT = np.array(CT)
colW = np.zeros((len(CV), NJ)); tc = sm((CV[:, 1] - NB) / 0.04)
colW[:, I['Chest']] = 1 - 0.6 * tc; colW[:, I['Neck1']] = 0.6 * tc
# the shirt's white collar inside it: a narrower band, closed, with a small V in front
SH = []
for i in range(8):
    t_ = i / 7
    y = NB - 0.03 + t_ * 0.045
    angs = np.linspace(-0.75, 0.75, 72)                                       # the front only: a white band in the collar's opening
    rr = 1.0 + 0.45 * (1 - t_) ** 2
    x = nrx * 0.96 * rr * np.sin(angs); z = nzc + nrz * 0.96 * rr * np.cos(angs)
    z = z - 0.012 * np.exp(-(angs / 0.12) ** 2) * (1 - t_)
    SH.append(np.c_[x, np.full(72, y), z])
SHV = np.array(SH).reshape(-1, 3)
SHT = []
for r in range(7):
    for c_ in range(71):
        a0, a1 = r * 72 + c_, r * 72 + c_ + 1; b0, b1 = a0 + 72, a1 + 72
        SHT += [[a0, a1, b0], [a1, b1, b0]]
SHT = np.array(SHT)
shW = colW[:len(SHV)].copy() if len(SHV) <= len(colW) else None
shW = np.zeros((len(SHV), NJ)); ts_ = sm((SHV[:, 1] - NB) / 0.04)
shW[:, I['Chest']] = 1 - 0.6 * ts_; shW[:, I['Neck1']] = 0.6 * ts_

# ---------------------------------------------------------------- joints for the new head, and the pack
J = J1.copy()
Jw = lambda p: W(np.array(p, float))
J[I['Neck1']] = Jw([0, 150, -26])
J[I['Neck2']] = Jw([0, 118, -24])
J[I['Head']] = Jw([0, 92, -24])
J[I['HeadEnd']] = Jw([0, -122, -20])
J[I['Jaw']] = Jw([0, 50, -10])
for s, k in (('Left', 0), ('Right', 1)):
    J[I[s + 'Eye']] = Jw(EYE_D[k])


def orient(V, T, c):
    """turn every triangle so its normal points away from c (a closed shell round c)"""
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    out = (n * (V[T].mean(1) - c)).sum(1) < 0
    T = T.copy(); T[out] = T[out][:, [0, 2, 1]]
    return T


HRT = orient(HRV, hair_all_t, W(HC))
bun_c = W(BUN + [0, 0, -6]); bm = (hair_all_t >= len(hair_v)).all(1)
HRT[bm] = orient(HRV, hair_all_t[bm], bun_c)


def top4(Wt):
    idx = np.argsort(-Wt, 1)[:, :4]; w = np.take_along_axis(Wt, idx, 1); w /= w.sum(1, keepdims=True)
    return idx, w


parts_out = []


def add(name, V, T, mat, SJ=None, SW=None, Wt=None, **attr):
    if Wt is not None: SJ, SW = top4(Wt)
    parts_out.append(dict(name=name, V=V, T=T, mat=np.broadcast_to(mat, (len(V),)), SJ=SJ, SW=SW, **attr))


add('body', bv, bT, mat, bSJ, bSW, rp=bv.copy())
head_mat = np.where(hf['mouth_in'] & (hv[:, 2] > 50), mi('mouth'), mi('skin'))
add('head', HV, HT, head_mat, Wt=headW, uv=uv, tw=tw, pn=pn, pw=pw, dr=hv)
for prt, k, v, tri in balls:
    add(prt + 'LR'[k], W(v), tri, mi(prt), Wt=chain_w(np.zeros(len(v)), len(v), [115, 160, 205]), dr=v)
add('hair', HRV, HRT, mi('hair'), Wt=hairW, hs=hair_all_s, hg=hair_all_g, dr=hair_all_v)
add('shoes', SHOE_V, SHOE_T, mi('shoe'), Wt=SHOE_W, two=1)
add('skirt', SV, ST, mi('coat'), Wt=skW, two=1, rp=SV.copy())
add('glasses', GV, GT, mi('frame'), Wt=glassW, two=1)
add('lens', LV, LT, mi('lens'), Wt=lensW, two=1)

N = sum(len(p['V']) for p in parts_out)
pos = np.concatenate([p['V'] for p in parts_out]).astype(np.float32)
tri, base, ranges = [], 0, {}
for p in parts_out:
    tri.append(p['T'] + base); ranges[p['name']] = [base, base + len(p['V'])]; base += len(p['V'])
tri = np.concatenate(tri).astype(np.uint32)
SJ = np.concatenate([p['SJ'] for p in parts_out]).astype(np.uint8)
SW = np.concatenate([p['SW'] for p in parts_out]).astype(np.float32)
matv = np.concatenate([p['mat'] for p in parts_out])


def cat(k, shape, dt=np.float32):
    return np.concatenate([np.broadcast_to(p[k], (len(p['V']),) + shape) if k in p else np.zeros((len(p['V']),) + shape) for p in parts_out]).reshape((N,) + shape).astype(dt)


floor = float(pos[:, 1].min())
header = dict(format='engine/body', version=1, id='vera-arcane', label={'ru': 'Вера (Arcane)'}, topology='vera-arcane',
              skeleton='soma', source='to3d/r7-s4-vera/tools/build.py', floor=floor, materials=MATS, ranges=ranges,
              K=K, FEET=FEET, ZOFF=ZOFF, face=dict(x0=FX0, x1=FX1, y0=FY0, y1=FY1))
col = np.array([MAT[MATS[m]][0] for m in matv]); shd = np.array([MAT[MATS[m]][1] for m in matv])
glw = np.array([MAT[MATS[m]][2] for m in matv]); rim = np.array([MAT[MATS[m]][3] for m in matv])
pack.save(os.path.join(OUT, 'vera.json'), header, dict(
    positions=pos, triangles=tri, skinJoints=SJ, skinWeights=SW,
    joints=J.astype(np.float32).ravel(), frames=FR.ravel(),
    col=col.astype(np.uint8), shd=shd.astype(np.uint8), glw=glw.astype(np.uint8), rim=rim.astype(np.uint8),
    mat=matv.astype(np.uint8), uv=cat('uv', (2,)), tw=(cat('tw', ()) * 255).astype(np.uint8),
    pn=cat('pn', (3,)), pw=(cat('pw', ()) * 255).astype(np.uint8), two=cat('two', (), np.uint8),
    hs=cat('hs', ()), hg=(np.clip(cat('hg', ()), 0, 1) * 255).astype(np.uint8), rp=cat('rp', (3,)), dr=cat('dr', (3,))))
# measures for the face (faces.py, the live face): the mouth's slit = skin vertices next to the mouth's inside
mi_ = hf['mouth_in']; tri_h = hf['tris']
adj = np.zeros(len(hv), bool)
for k_ in range(3):
    m_ = mi_[tri_h].any(1)
    adj[tri_h[m_, k_]] = True
slit = adj & ~mi_ & outer & (hv[:, 2] > 72)
sp_ = hv[slit]
mouth = dict(y=float(np.median(sp_[:, 1])), w=float(np.abs(sp_[:, 0]).max()), z=float(sp_[:, 2].max()))
iv = hf['irisL_v']
iris_r = float((iv[:, 0].max() - iv[:, 0].min()) / 2)
print('mouth', {k_: round(v_, 1) for k_, v_ in mouth.items()}, 'iris r', round(iris_r, 2))
json.dump(dict(eyes=EYE_D.tolist(), rb=float(hf['rb']), iris_r=iris_r, mouth=mouth, jaw=[0.0, 28.0, -35.0], K=K, FEET=FEET, ZOFF=ZOFF, ranges=ranges), open(os.path.join(OUT, 'face.json'), 'w'))
print('pack', N, 'vertices', len(tri), 'triangles; height', round(float(pos[:, 1].max() - floor), 3), 'ZOFF', round(ZOFF, 4))
