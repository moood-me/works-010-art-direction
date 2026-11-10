"""Савелий Петрович (Arcane) in 3D: builds the character pack that the viewer (web/figure.js) and the engine take.
  python3 build.py CACHE            → CACHE/out/savely.json|bin, CACHE/out/face.json
Bases: Anny's body (engine/data/bodies/moood-man: mesh, SOMA skeleton and weights) made lean, for the body, arms,
hands and legs; Blender's Human Base Meshes head «for animation» (CC0) fitted to the drawing (fit_head.py) with its
eyeballs; the white hair (a shell cut by the drawing's hair mask and the drawing's own tufts as separate locks), the
bushy brows and the moustache (thin shells on the face), the round glasses, the shirt, waistcoat, trousers and shoes
made here from the drawing's numbers (styles/s4-arcane/tools/cast.py, savely()). Everything is skinned to SOMA's joints.
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
    'skin':    (rgb('#efcab4'), rgb('#b97c74'), rgb('#d8644a'), rgb('#9fd0d8')),
    'hair':    (rgb('#d6cfc4'), rgb('#8f8690'), rgb('#c9a08c'), rgb('#dff4f8')),
    'suit':    (rgb('#d6d2c6'), rgb('#8f8a9c'), rgb('#cfae9c'), rgb('#dff4f8')),      # the shirt; waistcoat and trousers are painted by place
    'shoe':    (rgb('#2a1e18'), rgb('#120c0a'), rgb('#4a3026'), rgb('#9fd0d8')),
    'sclera':  (rgb('#e3d6cc'), rgb('#a8949a'), rgb('#e3d6cc'), rgb('#e3d6cc')),
    'iris':    (rgb('#5a7284'), rgb('#26303a'), rgb('#5a7284'), rgb('#a9bcc6')),
    'frame':   (rgb('#8f6c34'), rgb('#4e391e'), rgb('#b88a44'), rgb('#fff0c0')),
    'mouth':   (rgb('#4a2222'), rgb('#2e1414'), rgb('#5a2424'), rgb('#4a2222')),
    'lens':    (rgb('#dfe8f0'), rgb('#dfe8f0'), rgb('#dfe8f0'), rgb('#ffffff')),
    'teeth':   (rgb('#e6dccf'), rgb('#a08c88'), rgb('#e6dccf'), rgb('#e6dccf')),
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

# Anny's man 1.77 m → Савелий's 1.57 m. The drawn head is bigger for the body than Anny's, and Anny's shoulders rise
# high beside the neck: a scale by the whole height leaves no neck. The scale puts Anny's shoulder tops (10 cm off
# the middle) where the drawing's shoulders are, 158 units below the eye line.
_m = np.abs(np.abs(P0[:, 0]) - 0.11) < 0.008
S = (FEET - 158.0) * K / float(P0[_m, 1].max())


def under(j):
    out, st = [], [j]
    while st:
        k = st.pop(); out.append(k); st += list(np.where(PARENT == k)[0])
    return out


LEG = 1.03                                          # Arcane: legs a little long (the drawing's are much longer — stilts)
J1 = J0 * S
lift = J0[I['Hips'], 1] * S * (LEG - 1)
for s, sg in (('Left', 1), ('Right', -1)):
    for j in under(I[s + 'Leg']):
        J1[j, 1] = J0[I[s + 'Leg'], 1] * S + lift + (J0[j, 1] - J0[I[s + 'Leg'], 1]) * S * LEG
for j in range(NJ):
    if j not in under(I['LeftLeg']) and j not in under(I['RightLeg']):
        J1[j, 1] += lift * (1 - sm((J0[j, 1] * S - 0.95) / 0.4))     # the trunk keeps the shoulders' height
for s, sg in (('Left', 1), ('Right', -1)):          # an old man's narrow, sloping shoulders
    for j in under(I[s + 'Shoulder']): J1[j] += [-sg * 0.004, -0.008, 0]
    for j in under(I[s + 'Arm']): J1[j] += [-sg * 0.02, -0.012, 0]


def joint_affine(j):
    n = NAMES[j]
    if n in ('Hips',): return np.diag([0.9, 1, 0.9])
    if n in ('Spine1', 'Spine2'): return np.diag([0.86, 1, 0.92])
    if n in ('Chest',): return np.diag([0.84, 1, 0.86])
    if n.endswith('Shoulder'): return np.diag([0.86, 0.9, 0.86])
    r = {'LeftArm': 0.8, 'RightArm': 0.8, 'LeftForeArm': 0.82, 'RightForeArm': 0.82,
         'LeftLeg': 0.86, 'RightLeg': 0.86, 'LeftShin': 0.86, 'RightShin': 0.86}.get(n)
    if r:
        c = [k for k in range(NJ) if PARENT[k] == j][0]
        d = J0[c] - J0[j]; d /= np.linalg.norm(d)
        ax = r * np.eye(3) + (1 - r) * np.outer(d, d)
        if 'Leg' in n or 'Shin' in n: ax = ax + (LEG - 1) * np.outer(d, d)
        return ax
    return np.eye(3)


AFF = [joint_affine(j) for j in range(NJ)]
# the legs closer together (he stands with his feet near, as drawn): each leg turned in about its hip
LEG_IN = np.radians(7.0)
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
HT = HT[~(hv[HT, 1] > NECK_CUT).all(1)]            # the neck's end, inside the shirt's collar, is cut away
HV = W(hv)
yd_h = hv[:, 1]
# proxy normals for the face's shade: the head smoothed into big planes (Arcane's shadow is one shape)
Ah = M.adjacency(len(HV), HT)
hs_ = M.smooth(HV, Ah, np.ones(len(HV)), iters=45, lam=0.5)
pn = M.vertex_normals(hs_, HT)
pw = 0.88 * (1 - sm((yd_h - 120) / 30)) * (1 - 0.5 * hf['ear'])
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

# ---------------------------------------------------------------- the hair: white, round the sides and the back; tufts
HC = np.array([0.0, -20.0, -8.0])
skull = PT.Skull(hv, outer & ~ear & ~mi_ & (hv[:, 1] < 95), HC)


def hair_mask(U, V):                                # the drawing's (cast.savely): a band from the temples round the back
    au = np.abs(U)
    rag = 3.0 * np.sin(U * 9 + 0.01 * V * 7) + 2.0 * np.sin(U * 23 + 1 + 0.2 * V)       # a ragged edge
    side = (au - 1.2) * 60 + 0.4 * rag + 0.25 * (V + 10) * (V > -10)                      # the front edge slants back to the ear
    low = 26 + 40 * sm((au - 1.5) / 0.7)                                                 # sideburns end by the ear; the nape lower
    return np.minimum(np.minimum(side, V + 56 + rag), low - V + rag)


cap_v, cap_t, cap_m, cap_U, cap_V = PT.hair_cap(skull, HEAD, hair_mask, lambda U, V: 3.5 + 2.5 * sm((np.abs(U) - 1.6) / 0.8), edge=5.0)
hair_v = [cap_v]; hair_t = [cap_t]; hair_m = [cap_m]; hair_s = [cap_U * 4.0 + 0.01 * cap_V]; hair_a = [(cap_V + 60) / 130]
nlock = 0
# the drawing's tufts, and as many again by the same recipe (soft locks lifting off at their tips), so the mass reads
# as locks from every side
import random, math
rnd = random.Random(5)
more = []
for k in range(90):
    sd = rnd.choice((1, -1)); u0 = sd * rnd.uniform(1.28, math.pi); v0 = rnd.uniform(-54, 46)
    if (1.4 < abs(u0) < 1.95 and v0 > -12) or v0 > 14 + 40 * sm((abs(u0) - 1.5) / 0.7): continue
    u1 = u0 + sd * rnd.uniform(0.04, 0.22); v1 = v0 + rnd.uniform(14, 26)
    more.append(dict(pts=[('s', u0, v0, 3), ('s', (u0 + u1) / 2, (v0 + v1) / 2, 6.5), ('s', u1, v1, 8 + rnd.uniform(0, 8))], w=[7, 10, 0.5]))
own = [L for L in P.hair_locks(HEAD) if hair_mask(np.array([L['pts'][0][1]]), np.array([L['pts'][0][2]]))[0] > 0]      # not the ones rooted off the mask (on the cheek)
for k, spec in enumerate(own + more):
    v, tt, ac, al = PT.lock_mesh(HEAD, skull, spec, k=k, least=1.5, wscale=1.6, flat=0.42)
    hair_t.append(tt + sum(len(q) for q in hair_v)); hair_v.append(v); hair_m.append(np.ones(len(v))); hair_s.append(ac); hair_a.append(al); nlock += 1
hair_v = np.vstack(hair_v); hair_t = np.vstack(hair_t); hair_m = np.concatenate(hair_m); hair_s = np.concatenate(hair_s); hair_a = np.concatenate(hair_a)
HRV = W(hair_v)
HRT = PT.orient(HRV, hair_t, W(HC))
print('hair', len(hair_v), 'vertices,', nlock, 'locks')

# brows and moustache: thin shells of white hair on the face (they move with the skin: web/face.js)
okf = outer & (hv[:, 2] > 30)
shells = []
brow = [(x, y) for x, y in P.brow]
bx0, bx1 = P.brow_inner_x, P.brow_outer_x
# the drawn brow, a little heavier (bushy) and drooping over the eye at the outer end
brow_poly = [(x + (2.5 if i in (4, 5) else 0), y - (3.5 if i in (1, 2, 3, 4) else 0) + (2.5 if i in (6, 7, 8) else 0)) for i, (x, y) in enumerate(brow)]
for sd in (1, -1):
    v, tt, m_, hs, ids = PT.face_shell(hv, HT, okf, [(sd * x, y) for x, y in brow_poly], lambda x, y: 3.4 + 1.2 * sm((np.abs(x) - 10) / 20), edge=1.6, flow=(1.0, 0.25), fine=0.06)
    shells.append(('brow' + ('L' if sd > 0 else 'R'), v, tt, m_, hs))
# the moustache: the drawing's shape put between the fitted nose's base and the fitted mouth's slit
my0, my1 = min(y for x, y in P.moustache), max(y for x, y in P.moustache)
ty0, ty1 = SUB_Y + 0.5, mouth['y'] + 2.5
mous = [(x * 1.08, ty0 + (y - my0) / (my1 - my0) * (ty1 - ty0)) for x, y in P.moustache]
mpoly = mous + [(-x, y) for x, y in mous[::-1]]
v, tt, m_, hs, ids = PT.face_shell(hv, HT, outer & (hv[:, 2] > 30) & ~mi_, mpoly, lambda x, y: 3.4 - 1.2 * sm((np.abs(x) - 12) / 14), edge=1.5, flow=(1.0, 0.75), fine=0.08)
shells.append(('moustache', v, tt, m_, hs))

# ---------------------------------------------------------------- glasses: round gold wire, low on the nose
zf = float(hf['scleraL_v'][:, 2].max())
gv, gt, lv, lt = PT.glasses(P, hv, ear, zf, wire=0.75)
GV, GT, LV, LT = W(gv), gt, W(lv), lt

# upper teeth: a band behind the lips (seen when the jaw opens)
tx = np.linspace(-1, 1, 21); ty = np.linspace(0, 1, 5)
TX, TY = np.meshgrid(tx, ty, indexing='ij')
tw_ = mouth['w'] * 0.82
teeth_v = np.stack([TX * tw_, mouth['y'] - 6.5 + TY * 7.2, mouth['z'] - 5.5 - 9.0 * TX ** 2 + 0 * TY], -1).reshape(-1, 3)
teeth_t = []
for i in range(20):
    for j in range(4):
        a0, a1, b0, b1 = i * 5 + j, (i + 1) * 5 + j, i * 5 + j + 1, (i + 1) * 5 + j + 1
        teeth_t += [[a0, a1, b0], [a1, b1, b0]]
teeth_t = np.array(teeth_t)

# ---------------------------------------------------------------- Anny's body: shirt, waistcoat, trousers
COLLAR_TOP = 136.0                                  # the shirt collar's top edge (drawing units)
gone = (Winv(PB)[:, 1] < COLLAR_TOP) & (np.abs(PB[:, 0]) < 0.1)        # Anny's head and upper neck go; her lower neck is the shirt's collar
tk = ~gone[TRI0].any(1)
bi = np.where(~gone)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
bv = PB[bi].copy(); bT = remap[TRI0[tk]]; bSJ = SJ0[bi]; bSW = SW0[bi]
bp = PARTS[bi]
bpart = lambda *ns: sum(bp[:, PN.index(n)] for n in ns)
hands = bpart('Lhand', 'Rhand') > 0.5
feet = bpart('Lfoot', 'Rfoot') > 0.5
arms = bpart('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand')
legw = bpart('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot')
mat = np.full(len(bv), mi('suit'))
du = Winv(bv)                                       # rest places in drawing units
VEST_HEM = 622.0                                    # the waistcoat's lower edge = the trousers' top
# the sleeves end at the wrist with a cuff; hands are skin
wrist = np.zeros(len(bv))
for s in ('Left', 'Right'):
    jw = J1[I[s + 'Hand']]; jf = J1[I[s + 'ForeArm']]
    d = (jw - jf) / np.linalg.norm(jw - jf)
    along = (bv - jw) @ d
    side = (bpart('Lhand', 'LforeArm') if s == 'Left' else bpart('Rhand', 'RforeArm')) > 0.3
    wrist = np.maximum(wrist, side * sm((along + 0.012) / 0.01))
mat[(wrist > 0.5)] = mi('skin')
cloth = mat == mi('suit')
nb = M.vertex_normals(bv, bT)
# the waistcoat: over the trunk (not the arms: the armhole follows Anny's own arm parts), a cloth's thickness off the shirt
vest_w = sm((0.62 - arms) / 0.3) * sm((VEST_HEM + 4 - du[:, 1]) / 8) * (1 - (bpart('neck') > 0.3))
trou_w = sm((du[:, 1] - VEST_HEM + 4) / 8) * (1 - sm((arms - 0.3) / 0.3))
off = np.where(cloth, 0.004, 0) + cloth * vest_w * 0.008 + cloth * trou_w * 0.006
off += np.where(cloth & (wrist > 0), 0.005 * (1 - wrist), 0)        # the cuff
bv = bv + nb * off[:, None]
# the shirt's collar (Anny's lower neck in the shirt's cloth): round the fitted head's neck with a little room — pushed
# in or out to the fitted neck, by how much a point belongs to the neck and how high it is —, its top edge level
hn = hv[(hv[:, 1] > COLLAR_TOP - 5) & (hv[:, 1] < COLLAR_TOP + 7)]
ncz = float((hn[:, 2].max() + hn[:, 2].min()) / 2)
hang = np.arctan2(hn[:, 0], hn[:, 2] - ncz); hrad = np.hypot(hn[:, 0], hn[:, 2] - ncz)
nbins = 48; hb = ((hang + np.pi) / (2 * np.pi) * nbins).astype(int) % nbins
rmax = np.array([hrad[hb == k].max() if (hb == k).any() else hrad.max() for k in range(nbins)])
nw = bpart('neck') * sm((188 - du[:, 1]) / 30) * cloth
du2 = Winv(bv)
ang = np.arctan2(du2[:, 0], du2[:, 2] - ncz); rad = np.hypot(du2[:, 0], du2[:, 2] - ncz)
want = rmax[((ang + np.pi) / (2 * np.pi) * nbins).astype(int) % nbins] + 3.0
kc = sm(nw / 0.5) * sm((176 - du[:, 1]) / 36)       # at its top the collar hugs the neck; lower it widens into the shoulders
rad2 = np.maximum(rad + (want - rad) * kc, np.where(nw > 0.3, want, 0))
bv[:, 0] = np.sin(ang) * rad2 * K; bv[:, 2] = (ncz + np.cos(ang) * rad2) * K + ZOFF
for lp in M.boundary_loops(bT):
    lp = np.array(lp)
    if np.mean(du[lp, 1]) < COLLAR_TOP + 30:           # the cut's jagged edge: put on the collar's top ring
        bv[lp, 1] = W([0, COLLAR_TOP, 0])[1]
        bv[lp, 0] = np.sin(ang[lp]) * want[lp] * K; bv[lp, 2] = (ncz + np.cos(ang[lp]) * want[lp]) * K + ZOFF
Ab = M.adjacency(len(bv), bT)
chest = cloth & (du[:, 1] > 170) & (du[:, 1] < VEST_HEM) & (bv[:, 2] > -0.02) & (arms < 0.3)
bv = M.smooth(bv, Ab, chest * sm((bv[:, 2] + 0.02) / 0.06), iters=30, lam=0.5)

# the trousers: each leg a straight-cut tube from the hip to the shoe (the knee and the calf don't show through)
HEM_Y = 0.06
for s in ('Left', 'Right'):
    lw = bpart(s[0] + 'thigh', s[0] + 'shin')
    A_, B_, C_ = J1[I[s + 'Leg']], J1[I[s + 'Shin']], J1[I[s + 'Foot']]
    m = np.where((lw > 0.5) & cloth)[0]
    p = bv[m]
    # the leg's axis: a straight line from the hip to the ankle (trousers hang straight)
    ab = C_ - A_; tpar = np.clip(((p - A_) @ ab) / (ab @ ab), -0.2, 1.1)
    cpt = A_ + tpar[:, None] * ab
    d = p - cpt; r = np.linalg.norm(d, axis=1) + 1e-9
    rt = np.interp(tpar, [0.0, 0.25, 0.55, 1.0], [0.0, 0.076, 0.064, 0.058])     # the tube's radius down the leg
    wgt = sm((tpar - 0.12) / 0.25)
    rn = np.maximum(r, rt)
    bv[m] = cpt + d / r[:, None] * (r + (rn - r) * wgt)[:, None]
trou = cloth & (legw > 0.5)
bv = M.smooth(bv, Ab, trou * sm((0.8 - bv[:, 1]) / 0.2), iters=6, lam=0.5)
seat = cloth & (du[:, 1] > VEST_HEM) & (du[:, 1] < VEST_HEM + 200) & (arms < 0.3)
bv = M.smooth(bv, Ab, seat * 1.0, iters=14, lam=0.5)
# feet go; shoes instead; the trousers' hem level over the shoe
footcut = feet | ((legw > 0.5) & (bv[:, 1] < HEM_Y - 0.02))
bT = bT[~footcut[bT].any(1)]
for lp in M.boundary_loops(bT):
    lp = np.array(lp)
    if np.mean(bv[lp, 1]) < 0.2:
        bv[lp, 1] = HEM_Y
two = (trou | (wrist > 0)).astype(np.uint8)
SHOE_V, SHOE_T, SHOE_W = PT.shoes(J1, I, NJ, length=0.19, width=0.045, height=0.085, back=0.055)

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


add('body', bv, bT, mat, bSJ, bSW, hg=sm((0.62 - arms) / 0.3) * sm((0.5 - bpart('neck')) / 0.3), two=two)
# the mouth's inside: what is hardly seen from outside (export_hbm.py's rays), in the mouth's box
vis = np.load(os.path.join(C, 'hbm_head.npz'))['head_vis']
inside = (vis < 26) & (np.abs(hv[:, 0]) < mouth['w'] + 2) & (np.abs(hv[:, 1] - mouth['y']) < 16) & (hv[:, 2] > 40)
tw = tw * ~(inside | hf['mouth_in'])               # no painted layer inside the mouth
head_mat = np.where(inside | (hf['mouth_in'] & (hv[:, 2] > 50)), mi('mouth'), mi('skin'))
add('head', HV, HT, head_mat, Wt=headW, uv=uv, tw=tw, pn=pn, pw=pw, dr=hv)
for prt, k, v, tri in balls:
    add(prt + 'LR'[k], W(v), tri, mi(prt), Wt=rigid(len(v)), dr=v)
add('hair', HRV, HRT, mi('hair'), Wt=chain_w(hair_v[:, 1], len(HRV)), hs=hair_s, hm=hair_m, ha=hair_a, dr=hair_v, two=1)
for name, v, tt, m_, hs in shells:
    add(name, W(v), tt, mi('hair'), Wt=rigid(len(v)), hs=hs, hm=m_, ha=0.3 + 0.01 * v[:, 0], dr=v, two=2)       # two = 2: drawn from both sides, casts no shadow
add('teeth', W(teeth_v), teeth_t, mi('teeth'), Wt=rigid(len(teeth_v)), two=1, dr=teeth_v)
add('shoes', SHOE_V, SHOE_T, mi('shoe'), Wt=SHOE_W, two=1)
add('glasses', GV, GT, mi('frame'), Wt=rigid(len(GV)), two=1)
add('lens', LV, LT, mi('lens'), Wt=rigid(len(LV)), two=1, dr=lv)

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
header = dict(format='engine/body', version=1, id='savely-arcane', label={'ru': 'Савелий Петрович (Arcane)'}, topology='savely-arcane',
              skeleton='soma', source='to3d/r19-s4-savely/tools/build.py', floor=floor, materials=MATS, ranges=ranges,
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
