"""Тим (С12, pen and watercolour) in 3D: the pack the drawing renderer (web/figure.js, web/pen.js, web/char.js) takes.
  python3 build.py            → ../data/tim.json, tim.bin
Bases: Anny's child body (engine/data/bodies/moood-child: knees, shins, feet and the SOMA skeleton with its weights),
re-proportioned to the drawing (a big head on a short body, thin legs, short arms); Blender's Human Base Meshes
stylised head (CC0), fitted to head_front and head_side (head.py); the jumper, shorts, sleeves and mittens are shells
of the drawing's sizes (shells.py); the hair is a dome over the skull with spikes — the drawing's tufts as form.
What the pen-and-wash renderer needs instead of a material:
  grp      — which watercolour wash a vertex belongs to
  stripe   — the jumper's stripes: a coordinate down the body and along the sleeves
  band     — the legs' rest height (sock, its red band and the sneaker are cut by height)
  edges    — every mesh edge once, with its one or two triangles (silhouettes and open edges are found from them)
  inner    — where a silhouette of a part over itself is a line of this drawing (0 no, 1 yes, 2 thin: hair's spikes)
  faceTri, faceBar — the drawing's front face grid (head_front units) laid on the head
"""
import os, sys
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M, head as Hd, drawing as D, shells as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data')
HBM = '/home/user/cache/to3d-r35-s12-tim/hbm_head.npz'      # tools/hbm_export.py's arrays
os.makedirs(OUT, exist_ok=True)
K = D.K
y3 = lambda yd: (D.FLOOR - np.asarray(yd, float)) * K
ydr = lambda y: D.FLOOR - np.asarray(y, float) / K
u = lambda v: np.asarray(v, float) * K
smooth = S.smooth
rng = np.random.default_rng(35)

# ---------------------------------------------------------------- skeleton and Anny's child
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body('moood-child')
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


# the drawing's joints: hips low (short legs under long shorts), a short trunk, narrow shoulders, short arms, legs
# straight down and close; the neck and the head by the drawing's heights
J1 = J0.copy()
HIP = 0.535
J1[I['Hips']] = [0, HIP, 0]
for n in ['Spine1', 'Spine2', 'Chest']: J1[I[n]] = [0, HIP + 0.93 * (J0[I[n], 1] - J0[I['Hips'], 1]), 0.9 * J0[I[n], 2]]
J1[I['Neck1']] = [0, y3(132), 0.004]
J1[I['Neck2']] = [0, y3(112), 0.006]
J1[I['Head']] = [0, y3(84), 0.008]
J1[I['HeadEnd']] = [0, y3(-124), 0.0]
J1[I['Jaw']] = [0, y3(34), -0.012]
for s, sg in (('Left', 1), ('Right', -1)):
    J1[I[s + 'Eye']] = [sg * u(32), y3(0), u(70)]
    J1[I[s + 'Shoulder']] = [sg * 0.012, y3(134), 0.03]
    J1[I[s + 'Arm']] = [sg * 0.098, y3(137), 0.0]
    for n in ('ForeArm', 'Hand'):
        j = I[s + n]; J1[j] = J1[PARENT[j]] + 0.72 * (J0[j] - J0[PARENT[j]])
    for j in under(I[s + 'Hand'])[1:]:
        J1[j] = J1[PARENT[j]] + 0.62 * (J0[j] - J0[PARENT[j]])
    J1[I[s + 'Leg']] = [sg * 0.050, 0.500, 0.0]
    J1[I[s + 'Shin']] = [sg * 0.052, 0.270, 0.004]
    J1[I[s + 'Foot']] = [sg * 0.054, 0.045, -0.008]
    for n in ('ToeBase', 'ToeEnd'):
        j = I[s + n]; J1[j] = J1[PARENT[j]] + (J0[j] - J0[PARENT[j]]) * [0.0, 0.75, 0.66]


def rot_between(a_, b_):
    a_ = a_ / np.linalg.norm(a_); b_ = b_ / np.linalg.norm(b_)
    v = np.cross(a_, b_); c = a_ @ b_; s = np.linalg.norm(v)
    if s < 1e-9: return np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * ((1 - c) / s ** 2)


RADIAL = {'Leg': 0.52, 'Shin': 0.58, 'Arm': 0.62, 'ForeArm': 0.62}


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
    if 'Foot' in n or 'Toe' in n: return np.diag([0.70, 0.75, 0.66])
    if 'Hand' in n: return 0.62 * np.eye(3)
    if n in ('Hips', 'Spine1', 'Spine2', 'Chest') or 'Shoulder' in n: return np.diag([0.80, 0.93, 0.80])
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
legs = np.array([('Shin' in n or 'Foot' in n or 'Toe' in n or n.endswith('Leg')) for n in dn])
keep = legs & (PF[:, 1] < 0.44)              # of Anny's body the drawing shows the knees, shins and feet
tk = keep[TRI0].all(1)
bi = np.where(keep)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
B = dict(V=PF[bi], T=remap[TRI0[tk]])
nb = len(bi)
by = B['V'][:, 1]
isfoot = np.array([('Foot' in n or 'Toe' in n) for n in dn[bi]]) | (by < 0.05)
Ab = M.adjacency(nb, [list(t_) for t_ in B['T']])
B['V'] = M.smooth(B['V'], Ab, isfoot & (by < 0.045), iters=40, lam=0.5)       # a sneaker: the foot as one rounded form
nrm = M.vertex_normals(B['V'], B['T'])
B['V'][isfoot] += nrm[isfoot] * 0.007
B['V'][:, 1] -= B['V'][:, 1].min()
B['band'] = np.maximum(by, 0.0)
BW = np.zeros((nb, NJ))
for q in range(4): np.add.at(BW, (np.arange(nb), SJ0[bi][:, q]), SW0[bi][:, q])
B['W'] = BW

# ---------------------------------------------------------------- the head
hv, hP, eL, eR = Hd.load(HBM)
earm = Hd.ears(hv)
hv2, = Hd.fit(hv, earm, ear=(u(78), np.array([0.92, 0.82, 0.8])))
# the ears where the drawing has them: in the middle of the head's side (profile x 16…48), sticking out
ec = hv2[earm].mean(0)
hv2[earm] += [0, y3(-1) - ec[1], u(-30) - ec[2]]
for sg in (1, -1):
    m = earm & (np.sign(hv2[:, 0]) == sg)
    root = np.array([sg * u(76), y3(-1), u(-22)])
    q = hv2[m] - root; ang = sg * np.radians(-8)          # turned outward round the vertical
    hv2[m] = root + np.c_[q[:, 0] * np.cos(ang) - q[:, 2] * np.sin(ang), q[:, 1], q[:, 0] * np.sin(ang) + q[:, 2] * np.cos(ang)]
V0 = Hd.flatten(hv2, D.REG, front_min=0.02)
# the nose: the base's (nostrils, wings) laid flat, and the drawing's upturned button put on: its profile head_side's,
# its width head_front's (the nostrils' curve, ±10)
V0 = Hd.flatten(V0, [(0, 10, 19, 24)], front_min=0.02)
_xd, _yd = V0[:, 0] / K, ydr(V0[:, 1])
_m = (V0[:, 2] > 0.02) & (np.abs(_xd) < 28) & (_yd > -22) & (_yd < 30)
_pick = lambda yy: V0[np.argmin(np.where(_m, np.abs(_xd) + np.abs(_yd - yy), 1e9)), 2]
_plane = lambda y: np.interp(y, [-20, 28], [_pick(-20), _pick(28)])
_h = np.clip(np.interp(_yd, D.NOSE[:, 0], D.NOSE[:, 1], left=np.nan, right=np.nan) * K - _plane(_yd), 0, None)
_w = np.interp(_yd, [-16, -4, 8, 16, 22], [5, 8, 12.5, 12.5, 9])
_t = np.clip(np.abs(_xd) / _w, 0, 1)
_prof = (1 - _t ** 2) ** 0.9
V0[:, 2] = np.where(_m & ~np.isnan(_h), np.maximum(V0[:, 2], _plane(_yd) + np.nan_to_num(_h) * _prof), V0[:, 2])
nh = len(V0)
HT = M.triangulate(hP)
xd, yd = V0[:, 0] / K, ydr(V0[:, 1])
yde = yd - 14 * smooth(V0[:, 2] / 0.03)      # the chin and the jaw stay with the head
SW = np.zeros((nh, NJ))
sA = smooth((yde - 80) / 30); sB = smooth((yde - 106) / 24); sC = smooth((yde - 128) / 20)
SW[:, I['Head']] = 1 - sA
SW[:, I['Neck2']] = sA * (1 - sB)
SW[:, I['Neck1']] = sA * sB * (1 - sC)
SW[:, I['Chest']] = sA * sB * sC
Hh = dict(V=V0, T=HT, W=SW)

# ---------------------------------------------------------------- the jumper, sleeves, shorts, mittens
def rows_of(spec, step=6.0):
    spec = np.array(spec, float); ys = np.arange(spec[0, 0], spec[-1, 0] + 1e-6, step)
    ys = np.unique(np.r_[ys, spec[-1, 0]])
    f = lambda k: np.interp(ys, spec[:, 0], spec[:, k])
    a_, zf, zb = f(1), f(2), f(3)
    for arr in (a_, zf, zb):                     # rounded between the given heights
        arr[1:-1] = (arr[:-2] + 2 * arr[1:-1] + arr[2:]) / 4
    return [(y3(yy), u(aa), u((f_ + b_) / 2), u((f_ - b_) / 2), u((f_ - b_) / 2)) for yy, aa, f_, b_ in zip(ys, a_, zf, zb)]


# (drawing height, half-width, front, back): a round neck, narrow shoulders, a straight body to the hem
jrows = rows_of([(104, 35, 35, -31), (110, 44, 40, -36), (118, 58, 45, -43), (129, 71, 49, -48), (146, 77, 53, -50),
                 (200, 78, 58, -50), (270, 78, 60, -51), (330, 80, 60, -52), (352, 80, 58, -52)], 5.0)
JV, JT = S.loft(jrows, 64, True); JT = S.outward(JV, JT)
Jm = dict(V=JV, T=JT, W=WT.smooth(WT.transfer(JV), JT), stripe=y3(396 / 0.66 - 300 / 0.66 + 7) - JV[:, 1])
# stripes: the figure's are 32 px apart (0.66 px a unit) and 14 px wide, the first just under the shoulders
PERIOD = u(32 / 0.66); STRIPE0 = y3(144)
Jm['stripe'] = (STRIPE0 - JV[:, 1]) / PERIOD

SL, HANDS = [], []
for s, sg in (('Left', 1), ('Right', -1)):
    A_, E_, W_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']], J1[I[s + 'Hand']]
    d1 = (E_ - A_) / np.linalg.norm(E_ - A_); d2 = (W_ - E_) / np.linalg.norm(W_ - E_)
    path = S.catmull([A_ - d1 * 0.022, (A_ + E_) / 2, E_, W_ + d2 * 0.004], 9)
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    Ln = L / L[-1]
    radii = np.interp(Ln, [0, 0.14, 0.5, 0.92, 1.0], [0.027, 0.031, 0.027, 0.023, 0.024])
    V_, T_ = S.tube(path, radii, 22)
    arm = set(under(I[s + 'Shoulder'])); tr = np.array([j in arm for j in range(NJ)])
    SL.append(dict(V=V_, T=T_, W=WT.limb(V_, T_, tr, A_), side=s,
                   stripe=np.repeat((STRIPE0 - (A_[1] - L * 0.92)) / PERIOD, 22)))
    V_, T_ = S.mitten(W_, J1[I[s + 'HandMiddleEnd']], J1[I[s + 'HandIndex1']] - J1[I[s + 'HandPinky1']], sg,
                      Lh=0.078, wide=0.0185, thick=0.0105, thumb=0.008, rows=20, cols=18)
    Wm = np.zeros((len(V_), NJ)); Wm[:, I[s + 'Hand']] = 1
    HANDS.append(dict(V=V_, T=T_, W=Wm, side=s))

# shorts: wide and long, to above the knee — the hips' shell and a wide leg each
prow = rows_of([(334, 70, 54, -52), (380, 77, 57, -57), (420, 78, 55, -57), (440, 66, 44, -48), (452, 40, 26, -30), (458, 6, 4, -6)], 5.0)
PV, PT = S.loft(prow, 56, True); PT = S.outward(PV, PT)
SH = [dict(V=PV, T=PT, W=WT.smooth(WT.transfer(PV), PT))]
for s, sg in (('Left', 1), ('Right', -1)):
    A_, B_ = J1[I[s + 'Leg']], J1[I[s + 'Shin']]
    ax = lambda yy: A_ + (B_ - A_) * (A_[1] - yy) / (A_[1] - B_[1])
    ys = np.linspace(y3(380), y3(467), 12)
    path = np.array([ax(yy) + [sg * 0.006, 0, 0] for yy in ys])
    V_, T_ = S.tube(path, np.interp(ys, [ys[-1], ys[0]], [0.050, 0.044]), 30, flat=1.08)
    leg = set(under(I[s + 'Leg'])); tr = np.array([j in leg for j in range(NJ)])
    Wl = WT.transfer(V_); Wl = Wl * (tr | (np.arange(NJ) == I['Hips'])); Wl /= Wl.sum(1, keepdims=True)
    SH.append(dict(V=V_, T=T_, W=WT.smooth(Wl, T_, 6)))

# ---------------------------------------------------------------- the hair: a dome over the skull, with spikes
used = np.zeros(nh, bool); used[np.unique(HT)] = True
skull = V0[used & ~earm]
CEN = np.array([0, y3(-25), u(-6)])
sd = skull - CEN; sr = np.linalg.norm(sd, axis=1); sdir = sd / sr[:, None]
stree = cKDTree(sdir)


def skull_r(dirs):
    dd, ii = stree.query(dirs, 8)
    w = 1 / (dd + 0.03) ** 2
    return (sr[ii] * w).sum(1) / w.sum(1)


# the hairline as the drawing has it: across the forehead (y −70 in front), level along the side to behind the ear's
# top, then down behind the ear to the nape — as the elevation above the dome's centre by the azimuth from the front
HL_AZ = [0, 40, 80, 100, 118, 135, 155, 180]
HL_EL = [31, 29, 25, 22, 10, -6, -22, -30]
IV, IF = S.icosphere(5)
az = np.degrees(np.arctan2(np.abs(IV[:, 0]), IV[:, 2])); el = np.degrees(np.arcsin(IV[:, 1]))
# the edge is toothed: tufts of uneven length point down over the forehead and the nape
azs = np.degrees(np.arctan2(IV[:, 0], IV[:, 2]))
tk_ = np.sort(rng.uniform(-180, 180, 44)); tk_ = np.r_[tk_[-1] - 360, tk_, tk_[0] + 360]
th_ = rng.uniform(5, 13, len(tk_))
ti = np.clip(np.searchsorted(tk_, azs) - 1, 0, len(tk_) - 2)
tf = (azs - tk_[ti]) / (tk_[ti + 1] - tk_[ti])
tooth = th_[ti] * (1 - np.abs(2 * tf - 1) ** 1.3)                 # degrees below the hairline, a point in each interval
edge = np.interp(az, HL_AZ, HL_EL) - tooth
keepv = el > edge - 4
keepf = keepv[IF].all(1)
IF = IF[keepf]; usedv = np.unique(IF); rm = -np.ones(len(IV), int); rm[usedv] = np.arange(len(usedv))
IV = IV[usedv]; IF = rm[IF]; el = el[usedv]; edge = edge[usedv]; az = az[usedv]
# vertices below the edge go onto it
low = el < edge
eln = np.radians(np.where(low, edge, el)); azr = np.arctan2(IV[:, 0], IV[:, 2])
IV = np.c_[np.cos(eln) * np.sin(azr), np.sin(eln), np.cos(eln) * np.cos(azr)]
above = np.degrees(eln) - np.interp(az, HL_AZ, HL_EL)          # how far above the hairline (the teeth are below: < 0)
area = np.linalg.norm(np.cross(IV[IF[:, 1]] - IV[IF[:, 0]], IV[IF[:, 2]] - IV[IF[:, 0]]), axis=1)
IF = IF[area > 1e-7]
# spikes: seeds spread over the dome, each a cone of its own height leaning back (and down near the hairline)
seeds = []
cand = rng.normal(size=(6000, 3)); cand /= np.linalg.norm(cand, axis=1, keepdims=True)
caz = np.degrees(np.arctan2(np.abs(cand[:, 0]), cand[:, 2])); cel = np.degrees(np.arcsin(cand[:, 1]))
cand = cand[cel > np.interp(caz, HL_AZ, HL_EL) + 5]
for c in cand:
    if all(np.arccos(np.clip(c @ s_, -1, 1)) > 0.255 for s_ in seeds): seeds.append(c)
seeds = np.array(seeds); ns = len(seeds)
sh = rng.uniform(u(20), u(38), ns); srad = rng.uniform(0.18, 0.23, ns)
saz = np.degrees(np.arctan2(np.abs(seeds[:, 0]), seeds[:, 2])); sel = np.degrees(np.arcsin(seeds[:, 1]))
down = np.c_[-seeds[:, 0] * seeds[:, 1], 1 - seeds[:, 1] ** 2, -seeds[:, 2] * seeds[:, 1]] * -1      # the tangent that goes down
down /= np.linalg.norm(down, axis=1, keepdims=True) + 1e-9
back = np.array([0, 0.15, -1.0]) - seeds * (seeds @ np.array([0, 0.15, -1.0]))[:, None]
back /= np.linalg.norm(back, axis=1, keepdims=True) + 1e-9
near_edge = smooth(1 - (sel - np.interp(saz, HL_AZ, HL_EL)) / 22)
lean = back * (1 - near_edge)[:, None] * 0.55 + down * near_edge[:, None] * 0.75
ang = np.arccos(np.clip(IV @ seeds.T, -1, 1))                    # (vertices, seeds)
tt = np.clip(1 - ang / srad[None, :], 0, None)
bi_ = tt.argmax(1); tb = tt[np.arange(len(IV)), bi_]
base_t = u(6) + u(7) * smooth(above / 16) + u(6) * smooth((az - 95) / 50)                       # the hair's body: thin at the edge, thicker above
r0 = skull_r(IV) + base_t
rise = sh[bi_] * tb ** 1.05 * smooth((above + 2) / 10)
HV = CEN + IV * (r0 + rise)[:, None] + lean[bi_] * (rise * tb)[:, None]
# the teeth lie close over the forehead; the edge everywhere stands a little off the skin
HV += IV * (u(2) * (above < 0))[:, None]
HT_ = IF if (M.vertex_normals(HV, IF) * (HV - CEN)).sum(1).mean() > 0 else IF[:, ::-1]
Wh = np.zeros((len(HV), NJ)); Wh[:, I['Head']] = 1
Hr = dict(V=HV, T=HT_, W=Wh)
print('hair', len(HV), 'vertices', len(HT_), 'triangles', ns, 'spikes')

# ---------------------------------------------------------------- one mesh
G = dict(skin=1, hair=2, jumper=3, stripe=4, shorts=5, shoe=6, white=7, sock=8)
pieces = [('body', B, G['skin']), ('head', Hh, G['skin'])] + [('hand' + h_['side'], h_, G['skin']) for h_ in HANDS] + \
         [('jumper', Jm, G['jumper'])] + [('sleeve' + s_['side'], s_, G['jumper']) for s_ in SL] + \
         [('shorts%d' % i, s_, G['shorts']) for i, s_ in enumerate(SH)] + [('hair', Hr, G['hair'])]
Vs, Ts, Ws, grp, band, stripe, pid = [], [], [], [], [], [], []
base = tbase = 0; ranges, tranges = {}, {}
for k, (name, p, g_) in enumerate(pieces):
    n = len(p['V'])
    Vs.append(p['V']); Ts.append(p['T'] + base); Ws.append(p['W'])
    grp.append(np.full(n, g_, np.uint8)); pid.append(np.full(n, k, np.uint8))
    band.append(p.get('band', -np.ones(n))); stripe.append(p.get('stripe', -np.ones(n) * 100))
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
inhead = (E[:, 0] >= hd0) & (E[:, 0] < hd1)
drop |= inhead & (F1 < 0)                                         # the head's own holes (eyes, mouth, the neck's end)
ex, ey = P[E[:, 0], 0] / K, ydr(P[E[:, 0], 1])
for cx, cy, rx, ry in D.REG:                                      # where the face is drawn, not contoured
    drop |= inhead & ((((ex - cx) / (rx * 1.15)) ** 2 + ((ey - cy) / (ry * 1.15)) ** 2) < 1) & (P[E[:, 0], 2] > 0.02)
for k in ('body',):                                               # the cut of the legs under the shorts
    b0, b1 = ranges[k]; drop |= (E[:, 0] >= b0) & (E[:, 0] < b1) & (F1 < 0)
# the pen does not draw the sleeves' and the shorts' legs' upper ends (inside the jumper and the hips)
for k in PN:
    if k.startswith('sleeve') or k in ('shorts1', 'shorts2'):
        b0, b1 = ranges[k]; top = P[b0:b1, 1].max() if k.startswith('shorts') else None
        m = (E[:, 0] >= b0) & (E[:, 0] < b1) & (F1 < 0)
        if k.startswith('sleeve'):
            cols = 22; first_ring = (E[:, 0] - b0) < cols
            drop |= m & first_ring
        else:
            drop |= m & (P[E[:, 0], 1] > top - 0.01)

# where a part's silhouette over itself is a line: not on the face (its folds are the base mesh's, not the drawing's),
# but the nose, the ears, the chin; the hair's spikes over the hair — thin
inner = np.ones(N, np.uint8)
face_area = (V0[:, 2] > -0.01) & (yd > -70) & (yd < 64)
nose = (np.abs(xd) < 15) & (yd > -8) & (yd < 28)
inner[hd0:hd1] = np.where(face_area & ~nose & ~earm, 0, 1)
inner[slice(*ranges['hair'])] = 2

# ---------------------------------------------------------------- the face grid on the head (front projection)
thi = np.arange(*tranges['head']); TH = T[thi]
GX = np.arange(-93, 94, 3.0); GY = np.arange(-96, 100, 3.0)
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

header = dict(format='r12/character', version=2, id='tim-s12', label={'ru': 'Тим, перо и акварель'},
              skinning='cor', source='Anny moood-child (engine) + Human Base Meshes stylised head (CC0) + shells from the С12 drawing',
              pieces=ranges, trianglePieces=tranges, pieceNames=PN, groups=G,
              face=dict(gx=[float(GX[0]), 3.0, len(GX)], gy=[float(GY[0]), 3.0, len(GY)]),
              strokes=[], marks=[], units=K, floorUnits=D.FLOOR)
pack.save(os.path.join(OUT, 'tim.json'), header, dict(
    positions=P.astype(np.float32).ravel(), triangles=T.astype(np.uint32).ravel(),
    skinJoints=SJ.astype(np.uint8), skinWeights=SWt.astype(np.float32),
    joints=J1.astype(np.float32).ravel(), frames=FR.ravel(),
    band=band.astype(np.float32), stripe=stripe.astype(np.float32), grp=grp, pid=pid,
    edges=E.astype(np.uint32).ravel(), edgeTris=np.where(np.c_[F0, F1] < 0, 0xFFFFFFFF, np.c_[F0, F1]).astype(np.uint32).ravel(),
    edgeDrop=drop.astype(np.uint8), inner=inner,
    faceTri=np.where(faceTri < 0, 0xFFFFFFFF, faceTri).astype(np.uint32), faceBar=faceBar.astype(np.float32).ravel()))
print('saved', OUT, N, 'vertices', len(T), 'triangles', {k: v[1] - v[0] for k, v in ranges.items()})
