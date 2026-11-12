"""Кира (Arcane) in 3D: builds the character pack that the viewer (web/figure.js) and the engine take.
  python3 build.py CACHE            → CACHE/out/kira.json|bin, CACHE/out/face.json
Bases: Anny's body (engine/data/bodies/moood-girl: mesh, SOMA skeleton and weights) made thin and long-legged, for the
body, arms, hands and legs; Blender's Human Base Meshes head «for animation» (CC0) fitted to the drawing
(fit_head.py) with its eyeballs; the hair (a shell cut by the drawing's hairline and the drawing's own locks — the
choppy layers, the long fringe over one eye — as separate locks), the oversized hoodie with its hood, the headphones
round the neck, narrow trousers and heavy boots made here from the drawing's numbers
(styles/s4-arcane/tools/cast2.py, kira()). Everything is skinned to SOMA's joints.
Units: metres; the drawing's units map as world = (x·K, (FEET − y)·K, z·K + ZOFF)."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack, mesh as M, drawing as DR, parts as PT  # noqa: E402
from parts import sm  # noqa: E402

C = sys.argv[1]
OUT = os.path.join(C, 'out')
os.makedirs(OUT, exist_ok=True)
K = 0.00097
FEET = float(DR.FEET)
P = DR.person()
HEAD, NOSE, NECK = DR.surfaces(P)
CROWN = float(HEAD.v0)


def rgb(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


# ---------------------------------------------------------------- materials: the drawing's paints
# base, shadow (Arcane: skin into red-brown, cloth into a cool violet), the warm band at the shadow's edge, the rim
MAT = {
    'skin':    (rgb('#f1d8cc'), rgb('#b78690'), rgb('#d86a62'), rgb('#e4f7a0')),
    'hair':    (rgb('#2e2434'), rgb('#120d16'), rgb('#4a3050'), rgb('#c8dc98')),
    'suit':    (rgb('#4c3050'), rgb('#271a33'), rgb('#6a3856'), rgb('#dcf78e')),      # the hoodie; the trousers are painted by place
    'shoe':    (rgb('#1c1b20'), rgb('#0b0a0d'), rgb('#3a2c38'), rgb('#dcf78e')),
    'sclera':  (rgb('#e6dad6'), rgb('#a8949a'), rgb('#e6dad6'), rgb('#e6dad6')),
    'iris':    (rgb('#4e6660'), rgb('#1c2224'), rgb('#4e6660'), rgb('#a9c0a8')),
    'mouth':   (rgb('#4a2026'), rgb('#2e1418'), rgb('#5a2428'), rgb('#4a2026')),
    'lime':    (rgb('#c9ee2c'), rgb('#7c9a1c'), rgb('#e6f060'), rgb('#ffffff')),
    'pad':     (rgb('#34323a'), rgb('#19181d'), rgb('#4a3c4a'), rgb('#dcf78e')),
}
MATS = list(MAT)
mi = MATS.index

# ---------------------------------------------------------------- skeleton and Anny's body
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body(DR.BODY)
P0 = a['positions'].reshape(-1, 3).astype(float); J0 = a['joints'].reshape(-1, 3).astype(float)
FR = a['frames'].reshape(-1, 4).astype(np.float32)
TRI0 = t['triangles'].reshape(-1, 3).astype(np.int64)
SJ0 = t['skinJoints'].reshape(-1, 4).astype(np.int64); SW0 = t['skinWeights'].reshape(-1, 4).astype(float)
PARTS = t['parts'].reshape(len(P0), -1) / 255.0; PN = th['parts']
part = lambda *ns: sum(PARTS[:, PN.index(n)] for n in ns)

# Anny's girl 1.51 m → Кира's 1.54 m. The drawn head is bigger for the body than Anny's, and Anny's shoulders rise high
# beside the neck: the scale puts Anny's shoulder tops (9 cm off the middle) where the drawing's shoulders are,
# 160 units below the eye line; the legs are then made longer (she is all legs).
_m = np.abs(np.abs(P0[:, 0]) - 0.09) < 0.008
S = (FEET - 160.0) * K / float(P0[_m, 1].max())


def under(j):
    out, st = [], [j]
    while st:
        k = st.pop(); out.append(k); st += list(np.where(PARENT == k)[0])
    return out


LEG = 1.07                                          # long thin legs (the drawing's are longer still — stilts)
J1 = J0 * S
lift = J0[I['Hips'], 1] * S * (LEG - 1)
for s, sg in (('Left', 1), ('Right', -1)):
    for j in under(I[s + 'Leg']):
        J1[j, 1] = J0[I[s + 'Leg'], 1] * S + lift + (J0[j, 1] - J0[I[s + 'Leg'], 1]) * S * LEG
for j in range(NJ):
    if j not in under(I['LeftLeg']) and j not in under(I['RightLeg']):
        J1[j, 1] += lift * (1 - sm((J0[j, 1] * S - 0.95) / 0.4))     # the trunk keeps the shoulders' height
for s, sg in (('Left', 1), ('Right', -1)):          # narrow shoulders
    for j in under(I[s + 'Shoulder']): J1[j] += [-sg * 0.004, -0.004, 0]
    for j in under(I[s + 'Arm']): J1[j] += [-sg * 0.016, -0.006, 0]


def joint_affine(j):
    n = NAMES[j]
    if n in ('Hips',): return np.diag([0.84, 1, 0.86])
    if n in ('Spine1', 'Spine2'): return np.diag([0.84, 1, 0.86])
    if n in ('Chest',): return np.diag([0.86, 1, 0.84])
    if n.endswith('Shoulder'): return np.diag([0.88, 0.9, 0.86])
    r = {'LeftArm': 0.8, 'RightArm': 0.8, 'LeftForeArm': 0.8, 'RightForeArm': 0.8,
         'LeftLeg': 0.8, 'RightLeg': 0.8, 'LeftShin': 0.8, 'RightShin': 0.8}.get(n)
    if r:
        c = [k for k in range(NJ) if PARENT[k] == j][0]
        d = J0[c] - J0[j]; d /= np.linalg.norm(d)
        ax = r * np.eye(3) + (1 - r) * np.outer(d, d)
        if 'Leg' in n or 'Shin' in n: ax = ax + (LEG - 1) * np.outer(d, d)
        return ax
    return np.eye(3)


AFF = [joint_affine(j) for j in range(NJ)]
# the legs closer together: each leg turned in about its hip
LEG_IN = np.radians(5.0)
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
NB_Y = 150.0                                        # the neck's base (drawing units)
neck_c = PB[(abs(PB[:, 1] - (FEET - NB_Y) * K) < 0.01) & (part('neck') > 0.3)]
ZOFF = float((neck_c[:, 2].max() + neck_c[:, 2].min()) / 2) - (-26.0 * K) + 0.006


def W(p):
    p = np.asarray(p, float)
    return np.stack([p[..., 0] * K, (FEET - p[..., 1]) * K, p[..., 2] * K + ZOFF], -1)


def Winv(p):
    return np.stack([p[..., 0] / K, FEET - p[..., 1] / K, (p[..., 2] - ZOFF) / K], -1)


hv = hf['v'].copy()
ear = hf['ear']
HT = hf['tris']
NECK_CUT = 158.0
HT = HT[~(hv[HT, 1] > NECK_CUT).all(1)]            # the neck's end, inside the hoodie's neck, is cut away
HV = W(hv)
yd_h = hv[:, 1]
# proxy normals for the face's shade: the head smoothed into big planes (Arcane's shadow is one shape)
Ah = M.adjacency(len(HV), HT)
hs_ = M.smooth(HV, Ah, np.ones(len(HV)), iters=90, lam=0.5)       # a young face: bigger, calmer planes than Вера's 45
pn = M.vertex_normals(hs_, HT)
pw = 0.96 * (1 - sm((yd_h - 120) / 30)) * (1 - 0.5 * hf['ear'])       # the shade follows the big planes almost fully: few clean shadow shapes
# the painted layer: front projection (faces.py frame, drawing units)
FX0, FX1, FY0, FY1 = -80.0, 80.0, -125.0, 130.0
uv = np.c_[(hv[:, 0] - FX0) / (FX1 - FX0), 1 - (hv[:, 1] - FY0) / (FY1 - FY0)]
nh = M.vertex_normals(HV, HT)
tw = sm((nh[:, 2] - 0.0) / 0.3) * (hv[:, 2] > -10) * (np.abs(hv[:, 0]) < 79)
MARKS = [115, 160, 205]


def chain_w(yd, n, marks=MARKS):
    Wt = np.zeros((n, NJ))
    ts = [sm((yd - m) / 40) for m in marks]
    Wt[:, I['Head']] = 1 - ts[0]
    Wt[:, I['Neck2']] = ts[0] * (1 - ts[1])
    Wt[:, I['Neck1']] = ts[0] * ts[1] * (1 - ts[2])
    Wt[:, I['Chest']] = ts[0] * ts[1] * ts[2]
    return Wt


headW = chain_w(yd_h - 15 * sm(-hv[:, 2] / 40), len(HV))
rigid = lambda n: chain_w(np.zeros(n), n)

balls = []
for k, s in ((0, 'L'), (1, 'R')):
    for prt in ('sclera', 'iris'):
        v = hf[prt + s + '_v']; f = hf[prt + s + '_f']
        tri = np.array([[q[0], q[kk], q[kk + 1]] for q in f for kk in range(1, len([x for x in q if x >= 0]) - 1)])
        balls.append((prt, k, v, tri))
EYE_D = hf['eye_d']

# measures of the fitted mouth (the slit = skin vertices next to the mouth's inside)
outer = hf['eye_w'] == 0
mi_ = hf['mouth_in']; tri_h = hf['tris']
adj = np.zeros(len(hv), bool)
for k_ in range(3):
    adj[tri_h[mi_[tri_h].any(1), k_]] = True
slit = adj & ~mi_ & outer & (hv[:, 2] > 72)
sp_ = hv[slit]
mouth = dict(y=float(np.median(sp_[:, 1])), w=float(np.abs(sp_[:, 0]).max()), z=float(sp_[:, 2].max()))
SUB_Y = float(NOSE.sub)

# ---------------------------------------------------------------- the hair: short, choppy, a long fringe over one eye
HC = np.array([0.0, -20.0, -8.0])
skull = PT.Skull(hv, outer & ~ear & ~mi_ & (hv[:, 1] < 95), HC)
hl = [(0, -78), (0.5, -72), (0.95, -44), (1.3, -6), (1.45, 10), (2.0, 34), (np.pi, 60)]          # the drawing's hairline (cast2.kira)


def hair_mask(U, V):
    rag = 2.5 * np.sin(U * 11 + 0.3) + 1.5 * np.sin(U * 27 + 1)                              # a choppy lower edge
    return np.interp(np.abs(U), [q[0] for q in hl], [q[1] for q in hl]) - V + rag * sm((np.abs(U) - 1.2) / 0.4)


cap_v, cap_t, cap_m, cap_U, cap_V = PT.hair_cap(skull, HEAD, hair_mask, lambda U, V: 6 + 6 * np.clip(-V / 110, 0, 1), edge=6.0)
# the cap's strands run from the parting (on her right, U ≈ −0.35) down each side: the across-coordinate follows them
hair_v = [cap_v]; hair_t = [cap_t]; hair_m = [cap_m]; hair_s = [cap_U * 3.0 + 0.006 * cap_V]; hair_a = [(cap_V + 122) / 190]
nlock = 0
def rooted(spec):
    """a lock whose root lies below the hairline (on bare skin: in the drawing other locks cover it, in 3D it is a bar
    stuck on the forehead) is grown up into the hair first"""
    p0 = spec['pts'][0]
    if p0[0] != 's' or hair_mask(np.array([p0[1]]), np.array([p0[2]]))[0] > 6: return spec
    top = float(np.interp(abs(p0[1]), [q[0] for q in hl], [q[1] for q in hl])) - 14
    return dict(spec, pts=[('s', p0[1], top, 5), ('s', p0[1], (top + p0[2]) / 2, p0[3] + 2)] + list(spec['pts']), w=[spec['w'][0] * 0.8, spec['w'][0]] + list(spec['w']))


for k, spec in enumerate(map(rooted, P.hair_locks(HEAD))):
    v, tt, ac, al = PT.lock_mesh(HEAD, skull, spec, k=k, nseg=16, nround=10, least=1.5, wscale=1.12, flat=0.34, tip=0.5)      # pointed tips: blunt ends read as bars stuck on the forehead
    hair_t.append(tt + sum(len(q) for q in hair_v)); hair_v.append(v); hair_m.append(np.ones(len(v))); hair_s.append(ac); hair_a.append(al); nlock += 1
hair_v = np.vstack(hair_v); hair_t = np.vstack(hair_t); hair_m = np.concatenate(hair_m); hair_s = np.concatenate(hair_s); hair_a = np.concatenate(hair_a)
HRV = W(hair_v)
HRT = PT.orient(HRV, hair_t, W(HC))
print('hair', len(hair_v), 'vertices,', nlock, 'locks')
shells = []

# ---------------------------------------------------------------- Anny's body: the hoodie, the trousers
COLLAR_TOP = 132.0                                  # the hoodie's neckband's top edge (drawing units)
gone = (Winv(PB)[:, 1] < COLLAR_TOP) & (np.abs(PB[:, 0]) < 0.1)        # Anny's head and upper neck go; her lower neck is the neckband
tk = ~gone[TRI0].any(1)
bi = np.where(~gone)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
bv = PB[bi].copy(); bT = remap[TRI0[tk]]; bSJ = SJ0[bi]; bSW = SW0[bi]
bp = PARTS[bi]
bpart = lambda *ns: sum(bp[:, PN.index(n)] for n in ns)
feet = bpart('Lfoot', 'Rfoot') > 0.5
arms = bpart('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand')
legw = bpart('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot')
mat = np.full(len(bv), mi('suit'))
du = Winv(bv)                                       # rest places in drawing units
HEM = 640.0                                         # the hoodie's lower edge (drawing units)
# the sleeves are long: they end over the hand's heel; hands are skin
wrist = np.zeros(len(bv))
for s in ('Left', 'Right'):
    jw = J1[I[s + 'Hand']]; jf = J1[I[s + 'ForeArm']]
    d = (jw - jf) / np.linalg.norm(jw - jf)
    along = (bv - jw) @ d
    side = (bpart('Lhand', 'LforeArm') if s == 'Left' else bpart('Rhand', 'RforeArm')) > 0.3
    wrist = np.maximum(wrist, side * sm((along - 0.012) / 0.01))
mat[(wrist > 0.5)] = mi('skin')
cloth = mat == mi('suit')
Ab = M.adjacency(len(bv), bT)
# the oversized hoodie: the trunk and the arms pushed well off the body and smoothed (the body's own forms don't show
# through thick cloth), fuller toward the hem and the cuffs; below the hem narrow trousers close on the legs
hood_w = sm((HEM + 3 - du[:, 1]) / 6) * cloth
trunk_w = sm((0.62 - arms) / 0.3)
nb = M.vertex_normals(bv, bT)
off = cloth * 0.003 + hood_w * (0.016 + 0.008 * (1 - trunk_w) * sm((du[:, 1] - 230) / 80))
off += np.where(cloth & (wrist > 0), 0.008 * (1 - wrist), 0)
bv = bv + nb * off[:, None]
# the trunk is boxy: below the chest every section is pushed out to at least an ellipse (the waist does not show),
# wider toward the hem; the pocket's pouch stands out on the belly (the hands go into it)
tr = np.where(hood_w * trunk_w > 0.01)[0]
kb = sm((du[tr, 1] - 200) / 90) * hood_w[tr] * trunk_w[tr]
zc_ = float(np.median(bv[tr, 2]))
ea = 0.142 + 0.016 * sm((du[tr, 1] - 300) / 300); eb = 0.1 + 0.014 * sm((du[tr, 1] - 300) / 300)
pouch = 0.022 * np.exp(-((du[tr, 1] - 520) / 60) ** 2) * np.exp(-(du[tr, 0] / 70) ** 2) * (bv[tr, 2] > zc_)
f = np.sqrt((bv[tr, 0] / ea) ** 2 + ((bv[tr, 2] - zc_) / (eb + pouch)) ** 2)
g = 1 + (np.maximum(1 / np.maximum(f, 1e-3), 1) - 1) * kb
bv[tr, 0] *= g; bv[tr, 2] = zc_ + (bv[tr, 2] - zc_) * g
bv = M.smooth(bv, Ab, hood_w * trunk_w * sm((du[:, 1] - 190) / 40), iters=12, lam=0.5)
bv = M.smooth(bv, Ab, hood_w * (1 - trunk_w) * (1 - wrist), iters=8, lam=0.5)
# under the hem, between the legs: the trousers' front is flat (the body's own form there read as a lump hanging
# under the hoodie)
fr = cloth & (du[:, 1] > HEM + 5) & (du[:, 1] < HEM + 110) & (np.abs(du[:, 0]) < 75) & (arms < 0.3)
zc2 = float(np.median(bv[fr, 2]))
wf = fr * sm((HEM + 110 - du[:, 1]) / 40) * sm((75 - np.abs(du[:, 0])) / 25) * (bv[:, 2] > zc2)
bv = M.smooth(bv, Ab, wf, iters=40, lam=0.5)
# the neckband (Anny's lower neck in the hoodie's cloth): round the fitted head's neck, loose, its top edge level
hn = hv[(hv[:, 1] > COLLAR_TOP - 5) & (hv[:, 1] < COLLAR_TOP + 7)]
ncz = float((hn[:, 2].max() + hn[:, 2].min()) / 2)
hang = np.arctan2(hn[:, 0], hn[:, 2] - ncz); hrad = np.hypot(hn[:, 0], hn[:, 2] - ncz)
nbins = 48; hb = ((hang + np.pi) / (2 * np.pi) * nbins).astype(int) % nbins
rmax = np.array([hrad[hb == k].max() if (hb == k).any() else hrad.max() for k in range(nbins)])
nw = bpart('neck') * sm((188 - du[:, 1]) / 30) * cloth
du2 = Winv(bv)
ang = np.arctan2(du2[:, 0], du2[:, 2] - ncz); rad = np.hypot(du2[:, 0], du2[:, 2] - ncz)
want = rmax[((ang + np.pi) / (2 * np.pi) * nbins).astype(int) % nbins] + 7.0
kc = sm(nw / 0.5) * sm((176 - du[:, 1]) / 36)
rad2 = np.maximum(rad + (want - rad) * kc, np.where(nw > 0.3, want, 0))
bv[:, 0] = np.sin(ang) * rad2 * K; bv[:, 2] = (ncz + np.cos(ang) * rad2) * K + ZOFF
for lp in M.boundary_loops(bT):
    lp = np.array(lp)
    if np.mean(du[lp, 1]) < COLLAR_TOP + 30:
        bv[lp, 1] = W([0, COLLAR_TOP, 0])[1]
        bv[lp, 0] = np.sin(ang[lp]) * want[lp] * K; bv[lp, 2] = (ncz + np.cos(ang[lp]) * want[lp]) * K + ZOFF
# feet go: boots instead; the trousers end inside the boots
BOOT_H = 0.2
footcut = feet | ((legw > 0.5) & (bv[:, 1] < BOOT_H - 0.07))
bT = bT[~footcut[bT].any(1)]
two = ((wrist > 0) | ((du[:, 1] > HEM - 12) & (du[:, 1] < HEM + 6))).astype(np.uint8)


def boots():
    """Heavy boots, a loft by height on each foot (world units): a thick sole with a heel and an arch under it, a welt,
    a high rounded toe box, the instep rising into a shaft that narrows at the ankle and opens a little at the top."""
    #        height  front   back   half-width  roundness
    rows = [(0.000, 0.168, 0.066, 0.051, 2.6), (0.005, 0.174, 0.070, 0.054, 2.6), (0.026, 0.174, 0.070, 0.054, 2.6),
            (0.027, 0.166, 0.064, 0.049, 2.3), (0.045, 0.166, 0.064, 0.049, 2.2), (0.060, 0.158, 0.063, 0.048, 2.1),
            (0.072, 0.140, 0.062, 0.047, 2.0), (0.082, 0.112, 0.061, 0.046, 2.0), (0.092, 0.086, 0.060, 0.045, 2.0),
            (0.105, 0.068, 0.058, 0.044, 2.0), (0.125, 0.058, 0.056, 0.043, 2.0), (0.150, 0.056, 0.057, 0.044, 2.0),
            (0.180, 0.058, 0.059, 0.046, 2.0), (0.200, 0.060, 0.061, 0.048, 2.0), (0.203, 0.056, 0.057, 0.044, 2.0)]
    cols = 56
    SHV, SHT, SHW = [], [], []
    for s_ in ('Left', 'Right'):
        jf = J1[I[s_ + 'Foot']]; jt = J1[I[s_ + 'ToeBase']]
        fwd = jt - jf; fwd[1] = 0; fwd /= np.linalg.norm(fwd)
        side = np.cross([0, 1.0, 0], fwd)
        base = np.array([jf[0], 0.0, jf[2]])
        vs = []
        a_ = np.linspace(0, 2 * np.pi, cols, endpoint=False); ca, sa = np.cos(a_), np.sin(a_)
        for y, front, back, w, pw_ in rows:
            L_ = np.where(ca > 0, front, back)
            rr = (np.abs(ca) ** pw_ + np.abs(sa) ** pw_) ** (-1 / pw_)
            along = ca * L_ * rr
            yy = np.full(cols, y)
            if y < 0.01:                              # the arch: between the heel and the ball the sole's underside is lifted
                yy = yy + 0.014 * sm((along + 0.012) / 0.012) * sm((0.07 - along) / 0.02)
            vs.append(base + np.outer(along, fwd) + np.outer(sa * w * rr, side) + np.c_[np.zeros(cols), yy, np.zeros(cols)])
        vs = np.vstack(vs)
        ts = []
        for i_ in range(len(rows) - 1):
            for k in range(cols):
                a0, a1 = i_ * cols + k, i_ * cols + (k + 1) % cols; b0, b1 = a0 + cols, a1 + cols
                ts += [[a0, a1, b0], [a1, b1, b0]]
        c0 = len(vs); vs = np.r_[vs, [base + [0, 0.014, 0] + fwd * 0.03]]
        ts += [[c0, (k + 1) % cols, k] for k in range(cols)]
        c1 = len(vs); vs = np.r_[vs, [base + [0, rows[-1][0] - 0.004, 0]]]
        ts += [[c1, (len(rows) - 1) * cols + k, (len(rows) - 1) * cols + (k + 1) % cols] for k in range(cols)]
        off_ = sum(len(q) for q in SHV)
        SHV.append(vs); SHT.append(np.array(ts) + off_)
        w_ = np.zeros((len(vs), NJ)); w_[:, I[s_ + 'Foot']] = 1.0
        toe = np.clip(((vs - jt) @ fwd) / 0.04, 0, 1) * 0.6 * (vs[:, 1] < 0.09)
        w_[:, I[s_ + 'Foot']] -= toe; w_[:, I[s_ + 'ToeBase']] += toe
        k_ = sm((vs[:, 1] - 0.09) / 0.07) * 0.8                    # the shaft goes with the shin
        w_ *= (1 - k_)[:, None]; w_[:, I[s_ + 'Shin']] += k_
        SHW.append(w_)
    return np.vstack(SHV), np.vstack(SHT), np.vstack(SHW)


SHOE_V, SHOE_T, SHOE_W = boots()

# the hood, lying on the upper back: a soft lump behind the neck
th_, ph_ = np.meshgrid(np.linspace(0.05, np.pi - 0.05, 22), np.linspace(-np.pi, np.pi, 40, endpoint=False), indexing='ij')
back_z = float(du2[(np.abs(du2[:, 0]) < 20) & (np.abs(du2[:, 1] - 185) < 12), 2].min())
hc_ = np.array([0.0, 158.0, back_z + 6.0])
lump = 1 + 0.06 * np.sin(3 * ph_ + 1) * np.sin(th_)
hood_v = np.stack([74 * np.sin(th_) * np.cos(ph_) * lump, hc_[1] + 8 - 56 * np.cos(th_) + 14 * np.sin(th_) * np.sin(ph_), hc_[2] - 34 * np.sin(th_) * np.sin(ph_) * lump], -1).reshape(-1, 3)
hood_t = []
for i in range(21):
    for j in range(40):
        j2 = (j + 1) % 40
        a0, a1, b0, b1 = i * 40 + j, i * 40 + j2, (i + 1) * 40 + j, (i + 1) * 40 + j2
        hood_t += [[a0, a1, b0], [a1, b1, b0]]
hood_t = PT.orient(W(hood_v), np.array(hood_t), W(hc_))       # in the world: the drawing's y is down
hoodW = np.zeros((len(hood_v), NJ)); hoodW[:, I['Chest']] = 0.75; hoodW[:, I['Neck1']] = 0.25

# the headphones round the neck: two lime cups on the collarbones, dark pads under them, a band behind the neck
def ellipsoid(c, ax_, r, n1=14, n2=24):
    """ax_: the cup's axis (unit); r: (radius across, half depth)"""
    ax_ = np.array(ax_, float); ax_ /= np.linalg.norm(ax_)
    u = np.cross(ax_, [0, 1.0, 0]); u /= np.linalg.norm(u); w = np.cross(ax_, u)
    t1, t2 = np.meshgrid(np.linspace(0.02, np.pi - 0.02, n1), np.linspace(-np.pi, np.pi, n2, endpoint=False), indexing='ij')
    v = (np.array(c) + (np.sin(t1) * np.cos(t2))[..., None] * u * r[0] + (np.sin(t1) * np.sin(t2))[..., None] * w * r[0] + np.cos(t1)[..., None] * ax_ * r[1]).reshape(-1, 3)
    tt = []
    for i in range(n1 - 1):
        for j in range(n2):
            j2 = (j + 1) % n2
            a0, a1, b0, b1 = i * n2 + j, i * n2 + j2, (i + 1) * n2 + j, (i + 1) * n2 + j2
            tt += [[a0, a1, b0], [a1, b1, b0]]
    return v, PT.orient(W(v), np.array(tt), W(np.array(c)))


lime_v, lime_t, pad_v, pad_t = [], [], [], []
CUP_Y = 186.0
for sd in (1, -1):
    near = du2[(np.abs(du2[:, 0] - sd * 50) < 14) & (np.abs(du2[:, 1] - CUP_Y) < 14) & (du2[:, 2] > ncz)]
    zs = float(near[:, 2].max())
    axis = [sd * 0.45, -0.25, 1.0]
    c = np.array([sd * 50.0, CUP_Y, zs + 5.0])
    v, tt = ellipsoid(c, axis, (20.0, 7.0)); pad_t.append(tt + sum(len(q) for q in pad_v)); pad_v.append(v)
    a_ = np.array(axis) / np.linalg.norm(axis)
    v, tt = ellipsoid(c + a_ * 6.0, axis, (15.5, 6.5)); lime_t.append(tt + sum(len(q) for q in lime_v)); lime_v.append(v)
    cup_c = c
    if sd == 1: cupL = c
    else: cupR = c
bz = hc_[2] - 8
band = [cupL + [6, -6, -4], [70, 160, ncz + 6], [60, 138, ncz - 34], [34, 126, bz + 4], [0, 122, bz - 2], [-34, 126, bz + 4], [-60, 138, ncz - 34], [-70, 160, ncz + 6], cupR + [-6, -6, -4]]
bpts, _ = PT.spline(band, 40)
v, tt = PT.tube(bpts, 5.5, 10); pad_t.append(tt[:, [0, 2, 1]] + sum(len(q) for q in pad_v)); pad_v.append(v)
lime_v = np.vstack(lime_v); lime_t = np.vstack(lime_t); pad_v = np.vstack(pad_v); pad_t = np.vstack(pad_t)


def chestW(n):
    w = np.zeros((n, NJ)); w[:, I['Chest']] = 1.0
    return w

# ---------------------------------------------------------------- joints for the new head, and the pack
J = J1.copy()
Jw = lambda p: W(np.array(p, float))
J[I['Neck1']] = Jw([0, 150, -26])
J[I['Neck2']] = Jw([0, 118, -24])
J[I['Head']] = Jw([0, 92, -24])
J[I['HeadEnd']] = Jw([0, CROWN, -20])
J[I['Jaw']] = Jw([0, 50, -10])
for s, k in (('Left', 0), ('Right', 1)):
    J[I[s + 'Eye']] = Jw(EYE_D[k])

parts_out = []


def add(name, V, T, mat, SJ=None, SW=None, Wt=None, **attr):
    if Wt is not None: SJ, SW = PT.top4(Wt)
    parts_out.append(dict(name=name, V=V, T=T, mat=np.broadcast_to(mat, (len(V),)), SJ=SJ, SW=SW, **attr))


add('body', bv, bT, mat, bSJ, bSW, hg=trunk_w * sm((0.5 - bpart('neck')) / 0.3), two=two)
# the mouth's inside: what is hardly seen from outside (export_hbm.py's rays), in the mouth's box
vis = np.load(os.path.join(C, 'hbm_head.npz'))['head_vis']
inside = (vis < 14) & (np.abs(hv[:, 0]) < mouth['w'] + 2) & (np.abs(hv[:, 1] - mouth['y']) < 16) & (hv[:, 2] > 40) & (hv[:, 2] < mouth['z'] - 5)      # behind the lips' front
tw = tw * ~(inside | hf['mouth_in'])               # no painted layer inside the mouth
head_mat = np.where(inside | (hf['mouth_in'] & (hv[:, 2] > 50)), mi('mouth'), mi('skin'))
add('head', HV, HT, head_mat, Wt=headW, uv=uv, tw=tw, pn=pn, pw=pw, dr=hv)
for prt, k, v, tri in balls:
    add(prt + 'LR'[k], W(v), tri, mi(prt), Wt=rigid(len(v)), dr=v)
add('hair', HRV, HRT, mi('hair'), Wt=chain_w(hair_v[:, 1], len(HRV)), hs=hair_s, hm=hair_m, ha=hair_a, dr=hair_v, two=1)
for name, v, tt, m_, hs in shells:
    add(name, W(v), tt, mi('hair'), Wt=rigid(len(v)), hs=hs, hm=m_, ha=0.3 + 0.01 * v[:, 0], dr=v, two=2)       # two = 2: drawn from both sides, casts no shadow
add('shoes', SHOE_V, SHOE_T, mi('shoe'), Wt=SHOE_W, two=1)
add('hood', W(hood_v), hood_t, mi('suit'), Wt=hoodW, hg=0.0, dr=hood_v)
add('pads', W(pad_v), pad_t, mi('pad'), Wt=chestW(len(pad_v)), two=1)
add('cups', W(lime_v), lime_t, mi('lime'), Wt=chestW(len(lime_v)), dr=lime_v)

N = sum(len(p['V']) for p in parts_out)
pos = np.concatenate([p['V'] for p in parts_out]).astype(np.float32)
tri, base, ranges = [], 0, {}
for p in parts_out:
    tri.append(p['T'] + base); ranges[p['name']] = [base, base + len(p['V'])]; base += len(p['V'])
tri = np.concatenate(tri).astype(np.uint32)
SJ = np.concatenate([p['SJ'] for p in parts_out]).astype(np.uint8)
SW = np.concatenate([p['SW'] for p in parts_out]).astype(np.float32)
matv = np.concatenate([p['mat'] for p in parts_out])


def cat(k, shape, dt=np.float32, default=0.0):
    return np.concatenate([np.broadcast_to(p[k], (len(p['V']),) + shape) if k in p else np.full((len(p['V']),) + shape, default) for p in parts_out]).reshape((N,) + shape).astype(dt)


floor = float(pos[:, 1].min())
header = dict(format='engine/body', version=1, id='kira-arcane', label={'ru': 'Кира (Arcane)'}, topology='kira-arcane',
              skeleton='soma', source='to3d/r20-s4-kira/tools/build.py', floor=floor, materials=MATS, ranges=ranges,
              K=K, FEET=FEET, ZOFF=ZOFF, face=dict(x0=FX0, x1=FX1, y0=FY0, y1=FY1))
col = np.array([MAT[MATS[m]][0] for m in matv]); shd = np.array([MAT[MATS[m]][1] for m in matv])
glw = np.array([MAT[MATS[m]][2] for m in matv]); rim = np.array([MAT[MATS[m]][3] for m in matv])
rp = cat('rp', (3,)); norp = np.concatenate([np.full(len(p['V']), 'rp' not in p) for p in parts_out]); rp[norp] = pos[norp]
pack.save(os.path.join(OUT, DR.WHO + '.json'), header, dict(
    positions=pos, triangles=tri, skinJoints=SJ, skinWeights=SW,
    joints=J.astype(np.float32).ravel(), frames=FR.ravel(),
    col=col.astype(np.uint8), shd=shd.astype(np.uint8), glw=glw.astype(np.uint8), rim=rim.astype(np.uint8),
    mat=matv.astype(np.uint8), uv=cat('uv', (2,)), tw=(cat('tw', ()) * 255).astype(np.uint8),
    pn=cat('pn', (3,)), pw=(cat('pw', ()) * 255).astype(np.uint8), two=cat('two', (), np.uint8),
    hs=cat('hs', ()), hg=(np.clip(cat('hg', ()), 0, 1) * 255).astype(np.uint8), hm=cat('hm', (), default=1.0), ha=cat('ha', ()),
    rp=rp, dr=cat('dr', (3,))))
iv = hf['irisL_v']
iris_r = float((iv[:, 0].max() - iv[:, 0].min()) / 2)
print('mouth', {k_: round(v_, 1) for k_, v_ in mouth.items()}, 'iris r', round(iris_r, 2), 'sub', SUB_Y)
skin_pieces = ['head'] + [s[0] for s in shells]
json.dump(dict(eyes=EYE_D.tolist(), rb=float(hf['rb']), iris_r=iris_r, mouth=mouth, jaw=[0.0, 28.0, -35.0], K=K, FEET=FEET, ZOFF=ZOFF,
               ranges=ranges, skin=skin_pieces), open(os.path.join(OUT, 'face.json'), 'w'))
print('pack', N, 'vertices', len(tri), 'triangles; height', round(float(pos[:, 1].max() - floor), 3), 'ZOFF', round(ZOFF, 4), 'S', round(S, 3))
