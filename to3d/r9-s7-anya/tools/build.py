"""Аня (С7, Гибли) in 3D: builds the character pack the viewer (web/anya.js) and the engine take.
  python3 build.py outdir
Bases: Anny's body (engine/data/bodies/moood-woman: hands, shins, feet and the SOMA skeleton with its weights), Blender's
Human Base Meshes stylised head (CC0; hbm_export.py) fitted to the drawing's head (headfit.py); the clothes and the hair
are the drawing's own 3D forms (its torso and skirt lofts, its arm tubes, its hair shell and locks — drawing.py) made
into meshes here; the face is drawn live from the drawing's face parts (web/face.js). Everything is skinned to SOMA's
77 joints, so Kimodo's motions play on it through the engine."""
import os, sys
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M, headfit as Hf, drawing as D, shapes as S

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/cache/to3d-r9-s7-anya/out'
HBM = '/home/user/cache/to3d-r9-s7-anya/hbm_head.npz'
os.makedirs(OUT, exist_ok=True)
CM = D.CM
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))
B = D.anya.B
SPEC = D.anya.SPEC
INK = D.rgb(D.INK)


def paint(n, c, s=None, l=INK):
    """per-vertex fill, shade, line colours: c a hex; the shade is the drawing's (a warm multiply)."""
    return dict(col=np.tile(D.rgb(c), (n, 1)), shd=np.tile(s if s is not None else D.shade(c), (n, 1)), lin=np.tile(l, (n, 1)))


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


m3 = lambda p: np.asarray(p, float) * CM          # drawing cm → metres
J1 = J0.copy()
# the trunk: Anny's heights mapped onto the drawing's (hip joints 84 cm, shoulders 131, the neck's foot 136)
ymap = lambda y: np.interp(y, [0, 0.819, 1.265, 1.314], [0, 0.84, 1.31, 1.36])
for n in ['Hips', 'Spine1', 'Spine2', 'Chest']: J1[I[n], 1] = ymap(J0[I[n], 1])
J1[I['Neck1']] = m3(D.J['neck0'])
J1[I['Neck2']] = m3(D.J['neck1'])
J1[I['Head']] = D.head_to_model([0, -0.45, -0.25])[0]
J1[I['HeadEnd']] = D.head_to_model([0, 1.0, -0.1])[0]
J1[I['Jaw']] = D.head_to_model([0, -0.3, -0.12])[0]
FACE = D.anya.FACE
for s, sg in (('Left', 1), ('Right', -1)):
    J1[I[s + 'Eye']] = D.head_to_model([sg * FACE['eye_x'], FACE['eye_y'], 0.5])[0]
    J1[I[s + 'Shoulder']] = [sg * 0.015, ymap(J0[I[s + 'Shoulder'], 1]), J0[I[s + 'Shoulder'], 2] - 0.03]
    J1[I[s + 'Arm']] = m3(D.J['sh' + ('l' if sg > 0 else 'r')])
    for n, L in (('ForeArm', B['upper']), ('Hand', B['fore'])):
        j = I[s + n]; p = PARENT[j]; d = J0[j] - J0[p]
        J1[j] = J1[p] + d / np.linalg.norm(d) * L * CM
    for j in under(I[s + 'Hand'])[1:]:
        J1[j] = J1[PARENT[j]] + 0.88 * (J0[j] - J0[PARENT[j]])
    side = 'l' if sg > 0 else 'r'
    J1[I[s + 'Leg']] = m3(D.J['hp' + side])
    J1[I[s + 'Shin']] = m3(D.J['kn' + side]) + [0, 0, 0.004]
    J1[I[s + 'Foot']] = m3(D.J['an' + side])
    for n in ('ToeBase', 'ToeEnd'):        # a shorter foot: the drawing's small flat shoe
        j = I[s + n]; J1[j] = J1[PARENT[j]] + 0.86 * (J0[j] - J0[PARENT[j]])


def rot_between(u, v):
    u = u / np.linalg.norm(u); v = v / np.linalg.norm(v)
    c = u @ v; ax = np.cross(u, v); s = np.linalg.norm(ax)
    if s < 1e-9: return np.eye(3)
    ax /= s; K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + s * K + (1 - c) * K @ K


CHILD = {'Arm': 'ForeArm', 'ForeArm': 'Hand', 'Leg': 'Shin', 'Shin': 'Foot', 'Foot': 'ToeBase'}


def joint_affine(j):
    """joint j's move of the rest: x ↦ J1_j + A (x − J0_j): the bone turned to its new direction, stretched along
    it to its new length, slimmed across it (shins); smaller hands and feet."""
    n = NAMES[j]
    for s in ('Left', 'Right'):
        if n.startswith(s) and n[len(s):] in CHILD:
            c = I[s + CHILD[n[len(s):]]]
            d0, d1 = J0[c] - J0[j], J1[c] - J1[j]
            L = np.linalg.norm(d1) / np.linalg.norm(d0); u = d0 / np.linalg.norm(d0)
            r = {'Shin': 0.82, 'Leg': 0.9, 'Foot': 0.9}.get(n[len(s):], 1.0)
            return rot_between(d0, d1) @ (r * np.eye(3) + (L - r) * np.outer(u, u))
    if 'Toe' in n: return np.diag([0.9, 0.9, 0.86])
    if 'Hand' in n: return 0.88 * np.eye(3)
    return np.eye(3)


AFF = [joint_affine(j) for j in range(NJ)]


def deform(P, SJ, SW):
    out = np.zeros_like(P)
    for k in range(4):
        for j in np.unique(SJ[:, k]):
            m = (SJ[:, k] == j) & (SW[:, k] > 0)
            out[m] += SW[m, k, None] * (J1[j] + (P[m] - J0[j]) @ AFF[j].T)
    return out


PF = deform(P0, SJ0, SW0)          # the whole body, fitted (the clothes take their weights from it)
dom = SJ0[np.arange(len(SJ0)), SW0.argmax(1)]
dn = np.array([NAMES[j] for j in dom])
handv = np.array(['Hand' in n for n in dn])
fore = np.array([n.endswith('ForeArm') for n in dn])
legs = np.array([('Shin' in n or 'Foot' in n or 'Toe' in n or n.endswith('Leg')) for n in dn])
near_wrist = np.zeros(len(P0), bool)
for s in ('Left', 'Right'): near_wrist |= np.linalg.norm(PF - J1[I[s + 'Hand']], axis=1) < 0.07
keep = handv | (fore & near_wrist) | (legs & (PF[:, 1] < 0.43))
tk = keep[TRI0].all(1)
bi = np.where(keep)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
Bd = dict(V=PF[bi], T=remap[TRI0[tk]], SJ=SJ0[bi], SW=SW0[bi])
nb = len(bi)
by = Bd['V'][:, 1]
isfoot = np.array([('Foot' in n or 'Toe' in n) for n in dn[bi]]) | (by < 0.07)
# the shoe: the foot smoothed into one rounded form (no toes), a little fuller — the drawing's flat brown shoe
Ab = M.adjacency(nb, [list(t_) for t_ in Bd['T']])
fz = isfoot & (by < 0.075)
Bd['V'] = M.smooth(Bd['V'], Ab, fz, iters=40, lam=0.5)
nrm = M.vertex_normals(Bd['V'], Bd['T'])
Bd['V'][isfoot] += nrm[isfoot] * 0.004
Bd.update(paint(nb, D.COL['skin']))
# the shoe's top edge, per vertex: below it the shader paints the shoe (a clean edge, sloping from heel to toe)
Bd['band'] = np.where(by < 0.2, by - (0.058 - 0.2 * (Bd['V'][:, 2] + 0.0075)), -1.0)
BW = np.zeros((nb, NJ))
for q in range(4): np.add.at(BW, (np.arange(nb), Bd['SJ'][:, q]), Bd['SW'][:, q])
Bd['W'] = BW

# ---------------------------------------------------------------- weights for what is built here
FT = cKDTree(PF)


def transfer(V, k=6):
    dd, ii = FT.query(V, k)
    w = 1 / (dd + 1e-3) ** 2; w /= w.sum(1, keepdims=True)
    W = np.zeros((len(V), NJ))
    for c in range(k):
        for q in range(4): np.add.at(W, (np.arange(len(V)), SJ0[ii[:, c], q]), w[:, c] * SW0[ii[:, c], q])
    return W


def smooth_w(W, T, n, iters=12):
    A = M.adjacency(n, [list(t_) for t_ in T])
    return M.smooth(W, A, np.ones(n, bool), iters, 0.5)


def skirt_rule(V):
    """below the hips a skirt goes with the pelvis and, toward the hem, partly with the thighs."""
    W = np.zeros((len(V), NJ))
    L = 0.5 * smooth((0.80 - V[:, 1]) / 0.40)
    side = 1 / (1 + np.exp(-V[:, 0] / 0.035))
    W[:, I['LeftLeg']] = L * side; W[:, I['RightLeg']] = L * (1 - side); W[:, I['Hips']] = 1 - L
    return W


def cloth_weights(V, T):
    W = transfer(V)
    u = smooth((0.86 - V[:, 1]) / 0.10)[:, None]
    W = (1 - u) * W + u * skirt_rule(V)
    return smooth_w(W, T, len(V))


def arm_weights(V, T, side):
    W = transfer(V)
    arm = set(under(I[side + 'Shoulder'])); tr = np.array([j in arm for j in range(NJ)])
    top = smooth(np.linalg.norm(V - J1[I[side + 'Arm']], axis=1) / 0.07)
    Wa = W * tr; Wa /= Wa.sum(1, keepdims=True) + 1e-9
    return smooth_w(Wa * top[:, None] + W * (1 - top[:, None]), T, len(V))


# ---------------------------------------------------------------- the head (headfit.py)
hl, hP, earm, fw = Hf.build(HBM)
HT = M.triangulate(hP)
V0 = D.head_to_model(hl)
nH = len(V0)
hx, hy, hz = hl[:, 0], hl[:, 1], hl[:, 2]
Hh = dict(V=V0, T=HT)
# weights: the head; down the neck to the chest (the chin and the jaw stay with the head)
hye = hy + 0.45 * smooth((hz + 0.05) / 0.3)
W = np.zeros((nH, NJ))
sA = smooth((-0.55 - hye) / 0.35); sB = smooth((-0.95 - hye) / 0.3); sC = smooth((-1.25 - hye) / 0.15)
W[:, I['Head']] = 1 - sA
W[:, I['Neck2']] = sA * (1 - sB)
W[:, I['Neck1']] = sA * sB * (1 - sC)
W[:, I['Chest']] = sA * sB * sC
# the lower face on the jaw (it opens a little with the drawn mouth)
wj = smooth((-0.62 - hy) / 0.12) * smooth((hz - 0.2) / 0.15) * (1 - smooth((-0.97 - hy) / 0.08)) * (abs(hx) < 0.45)
W *= (1 - wj)[:, None]; W[:, I['Jaw']] += wj
Hh['W'] = W
Hh.update(paint(nH, D.COL['skin']))
# the neck under the jaw is in the head's shadow (the drawing: the head's outline shifted down over the neck)
neck = (hy < -0.98) | ((hy < -0.75) & (hz < 0.1) & (abs(hx) < 0.42))
Hh['col'][neck] = D.shade(D.COL['skin'])
# the face's drawn layer: front projection in head-local units (web/face.js draws in the same box)
FX0, FX1, FY0, FY1 = -1.0, 1.0, -1.3, 1.0
Hh['uv'] = np.c_[(hx - FX0) / (FX1 - FX0), (hy - FY0) / (FY1 - FY0)]
Hh['tex'] = ((hz > D.HEAD.zm(np.clip(hy, -1, 1)) - 0.1) & (hy > -1.05) & ~earm).astype(np.uint8)
# the face's shade by a smoothed head (one clean shade on the far side, not every bump of the base)
Ah = M.adjacency(nH, hP)
hs = M.smooth(V0, Ah, np.ones(nH, bool), iters=60, lam=0.5)
Hh['pn'] = M.vertex_normals(hs, HT); Hh['pw'] = 1 - smooth((-0.8 - hy) / 0.2)
Hh['ow'] = np.ones(nH)


# ---------------------------------------------------------------- the clothes: the drawing's lofts as thin solids
def loft_of(rings, n=2.4, wave=None):
    return D.Loft(rings, n, wave)


def rings_max(*lofts_push, ys):
    """rings at heights ys, each the largest of the given (loft, push) at that height (the outer garment covers the
    inner one everywhere)."""
    out = []
    for y in ys:
        best = None
        for lo, p in lofts_push:
            if y < lo.y0 - 1e-6 or y > lo.y1 + 1e-6: continue
            a_, zf_, zb_, x0, z0 = lo.at(y)
            r = [a_ + p, zf_ + z0 + p, zb_ + z0 - p]
            best = r if best is None else [max(best[0], r[0]), max(best[1], r[1]), min(best[2], r[2])]
        out.append((y,) + tuple(best))
    return out


torso = D.F.torso_loft()
skirt = loft_of(SPEC['bottom']['rings'], 2.2, SPEC['bottom'].get('wave'))
skirt_plain = loft_of(SPEC['bottom']['rings'], 2.2)
y_neck = B['torso'][-1][0]
top_s, over_s = SPEC['top'], SPEC['over']
NT = 96
TS = np.linspace(-np.pi, np.pi, NT, endpoint=False)


def axis_ref(V):
    """a point inside, for each vertex: the body's vertical axis at its height (lofts are centred near x=0)."""
    return np.c_[np.zeros(len(V)), V[:, 1], np.full(len(V), -0.005)]


def piece(V, T, c, W, **kw):
    d = dict(V=V, T=T, W=W); d.update(paint(len(V), c)); d.update(kw); return d


def grid_loft(lo, ys_of_col, ts, push=0.0):
    """grid (rows, cols): column c at azimuth ts[c] runs over the heights ys_of_col(c, v) for v in 0…1."""
    R = 60
    G = np.zeros((R, len(ts), 3))
    for c, tt in enumerate(ts):
        for r, v in enumerate(np.linspace(0, 1, R)):
            G[r, c] = lo.pt(tt, ys_of_col(c, v), push)
    return G * CM


# the skin under the neckline: the torso from the chest up, closed onto the neck
skin_lo = torso
G = np.array([[skin_lo.pt(tt, y) for tt in TS] for y in np.linspace(B['chest_y'], y_neck, 20)])
nz, nr = Hf.neck_axis((y_neck + 0.8 - D.HC[1]) / D.HK)
cap = np.array([[[np.sin(tt) * nr * D.HK * 0.98, y_neck + 0.8, D.HC[2] + nz * D.HK + np.cos(tt) * nr * D.HK * 0.98] for tt in TS]])
G = np.vstack([G, (G[-1:] * 0.5 + cap * 0.5) * [1, 0, 1] + [0, y_neck + 0.4, 0], cap]) * CM
SV, ST, _ = S.shell(G, True, 0.002, axis_ref)
SKIN = piece(SV, ST, D.COL['skin'], None)
SKIN['W'] = smooth_w(transfer(SV), ST, len(SV))

# the blouse: the torso loft eased, over the skirt's top, cut by the V neckline at the front
top_lo = loft_of(rings_max((torso, top_s['ease']), (skirt_plain, 0.6), ys=np.r_[np.arange(top_s['hem'], y_neck, 1.0), y_neck]), 2.4)
dep, wid = top_s['neck_cut']
def top_y(c, v):
    tt = abs(TS[c])
    # the V: its bottom at the front middle, up to the neckline at |t| = wid, then the neck's height
    yv = np.interp(tt, [0, wid * 0.6, wid, wid + 0.08], [y_neck - dep, y_neck - dep * 0.6, y_neck - 1, y_neck])
    return top_s['hem'] + (yv - top_s['hem']) * v
TV, TT, _ = S.shell(grid_loft(top_lo, top_y, TS), True, 0.0025, axis_ref)
TOP = piece(TV, TT, top_s['c'], cloth_weights(TV, TT))

# the cardigan: bigger than the blouse everywhere, open at the front (the drawing's opening: narrow at the hem, wide
# at the neck), its neckline round the neck at the back
over_lo = loft_of(rings_max((torso, over_s['ease']), (top_lo, over_s['ease'] - top_s['ease'] + 0.2), (skirt_plain, 1.2),
                            ys=np.r_[np.arange(over_s['hem'], y_neck - 0.5, 1.0), y_neck - 0.5]), 2.4)
w0, w1 = over_s['open'][:2]
y_top = y_neck - 0.5
NC = 84
def over_cols(v_unused=None):
    return np.linspace(0, 1, NC)
OG = np.zeros((60, NC, 3))
for r, v in enumerate(np.linspace(0, 1, 60)):
    y = over_s['hem'] + (y_top - over_s['hem']) * v
    g = w0 + (w1 - w0) * np.clip((y - (over_s['hem'] - 3)) / (y_top + 4 - (over_s['hem'] - 3)), 0, 1)
    for c, u in enumerate(np.linspace(0, 1, NC)):
        tt = g + u * (2 * np.pi - 2 * g)
        OG[r, c] = over_lo.pt(tt, y)
OV, OT, _ = S.shell(OG * CM, False, 0.003, axis_ref)
OVER = piece(OV, OT, over_s['c'], cloth_weights(OV, OT))

# the skirt: the drawing's loft with its soft folds toward the hem
KG = np.array([[skirt.pt(tt, y) for tt in TS] for y in np.linspace(skirt.y0, skirt.y1, 70)]) * CM
KV, KT, _ = S.shell(KG, True, 0.0025, axis_ref)
SKIRT = piece(KV, KT, SPEC['bottom']['c'], cloth_weights(KV, KT))

# the cardigan's sleeves: the drawing's arm tube (radii arm_r + ease) from under the shoulder to the wrist, a cuff a
# little wider; the sleeve's top starts below the shoulder's slope (the drawing cuts what rises above the torso)
SLEEVES = []
for s, side in (('Left', 'l'), ('Right', 'r')):
    A_, E_, W_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']], J1[I[s + 'Hand']]
    e = over_s['sleeve']['ease'] * CM
    r0 = np.array(B['arm_r']) * CM
    d1 = (E_ - A_) / np.linalg.norm(E_ - A_); d2 = (W_ - E_) / np.linalg.norm(W_ - E_)
    pts = [A_ - d1 * 0.01, A_ + d1 * 0.06, (A_ + E_) / 2, E_ - d1 * 0.02, E_ + d2 * 0.03, (E_ + W_) / 2, W_ - d2 * 0.035, W_ - d2 * 0.02, W_ + d2 * 0.003]
    rad = [r0[0] * 0.75 + e, r0[0] + e, (r0[0] + r0[1]) / 2 + e, r0[1] + e, r0[1] + e, r0[2] + e, r0[3] + e + 0.002, r0[3] + e + 0.006, r0[3] + e + 0.006]
    path = np.vstack([np.linspace(p, q, 5, endpoint=False) for p, q in zip(pts[:-1], pts[1:])] + [pts[-1]])
    rr = np.interp(np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))],
                   np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.array(pts), axis=0), axis=1))], rad)
    V_, T_ = S.tube(path, rr, cols=28)
    SLEEVES.append(piece(V_, T_, over_s['c'], arm_weights(V_, T_, s), side=s))

# ---------------------------------------------------------------- the hair (hair3d.py)
import hair3d  # noqa: E402
HAIR = hair3d.build(dict(head=(V0, HT), earm=earm, J1=J1, I=I, NJ=NJ, smooth_w=smooth_w,
                         lofts=[(over_lo, over_s['ease'] * 0 + 0.6), (top_lo, 0.6)]))

# ---------------------------------------------------------------- lines lying on the surfaces (the drawing's folds)
LINES = []
lw = 0.0021      # the drawing's thin lines (0.55 of its outline) at the turnaround's scale


def surface_line(lo, ts, ys, width, src, push=0.1):
    P = np.array([lo.pt(t_, y_, push) for t_, y_ in zip(ts, ys)]) * CM
    e = 1e-3
    Nn = []
    for t_, y_ in zip(ts, ys):
        a_ = lo.pt(t_ + e, y_) - lo.pt(t_ - e, y_); b_ = lo.pt(t_, y_ + 0.5) - lo.pt(t_, y_ - 0.5)
        n_ = np.cross(a_, b_); n_ /= np.linalg.norm(n_); Nn.append(n_)
    Nn = np.array(Nn)
    if (Nn * (P - axis_ref(P))).sum(1).mean() < 0: Nn = -Nn
    V_, T_ = S.strip(P, Nn, width * S.taper(len(P), 0.2), lift=0.0012)
    i = cKDTree(src['V']).query(V_)[1]
    LINES.append(dict(V=V_, T=T_, W=src['W'][i], col=np.tile(INK, (len(V_), 1)), shd=np.tile(INK, (len(V_), 1)),
                      lin=np.tile(INK, (len(V_), 1)), ow=np.zeros(len(V_))))


for tf in SPEC['bottom'].get('folds', []):
    ys = np.linspace(skirt.y0 + 1, skirt.y0 + (skirt.y1 - skirt.y0) * 0.55, 30)
    surface_line(skirt, [tf] * len(ys), ys, lw, SKIRT, push=0.35)
for L_ in hair3d.LINES:
    LINES.append(L_)

# ---------------------------------------------------------------- the fringe's shadow on the forehead (as the drawing
# does: the front hair's shape, shifted a little down and right, over the skin), in the face layer's head-local units
def fringe_shadow():
    from geo import View, shift, polys
    from head import Head
    from hair import Hair
    h0 = Head(D.anya.FACE); h0.place((0, 0, 0), 2.0)
    v = View(yaw=0, pitch=0, s=1.0)
    Fh, _, _ = Hair(h0, D.anya.HAIRDEF).build(v)
    sk = h0.skull(v)
    g = shift(Fh, 0.015, 0.045).intersection(sk).difference(Fh.buffer(-0.004))
    return [[[float(x), float(-y)] for x, y in np.asarray(p.exterior.coords)] for p in polys(g) if p.area > 1e-4]


# ---------------------------------------------------------------- one pack
pieces = [('body', Bd), ('head', Hh), ('skin', SKIN), ('skirt', SKIRT), ('top', TOP), ('cardigan', OVER)] + \
         [('sleeve' + p_['side'], p_) for p_ in SLEEVES] + [('hair', HAIR)] + [('lines', dict(
             V=np.vstack([l_['V'] for l_ in LINES]), T=np.vstack([l_['T'] + o for l_, o in zip(LINES, np.cumsum([0] + [len(l_['V']) for l_ in LINES])[:-1])]),
             W=np.vstack([l_['W'] for l_ in LINES]), col=np.vstack([l_['col'] for l_ in LINES]), shd=np.vstack([l_['shd'] for l_ in LINES]),
             lin=np.vstack([l_['lin'] for l_ in LINES]), ow=np.concatenate([l_['ow'] for l_ in LINES])))]
Vs, Ts, Ws, cols, shds, lins, ows, uvs, texs, pns, pws, two, bands, obs = [], [], [], [], [], [], [], [], [], [], [], [], [], []
base = 0; ranges = {}; tbase = 0; tranges = {}
for name, p in pieces:
    n = len(p['V'])
    Vs.append(p['V']); Ts.append(p['T'] + base); Ws.append(p['W'])
    cols.append(p['col']); shds.append(p['shd']); lins.append(p['lin'])
    ows.append(p.get('ow', np.ones(n))); bands.append(p.get('band', -np.ones(n))); uvs.append(p.get('uv', np.zeros((n, 2))))
    texs.append(p.get('tex', np.zeros(n))); pns.append(p.get('pn', np.zeros((n, 3)))); pws.append(p.get('pw', np.zeros(n)))
    two.append(np.full(n, 1 if name in ('lines',) else 0)); obs.append(p.get('ob', np.zeros(n)))
    ranges[name] = [base, base + n]; tranges[name] = [tbase, tbase + len(p['T'])]; base += n; tbase += len(p['T'])
V = np.vstack(Vs); W = np.maximum(np.vstack(Ws), 0); N = len(V)
order = np.argsort(-W, 1)[:, :4]
SJ = order.astype(np.uint8); SWt = np.take_along_axis(W, order, 1); SWt /= SWt.sum(1, keepdims=True)
pj = SJ[:, 0].astype(np.float32)
pack.save(os.path.join(OUT, 'anya.json'),
          dict(format='r1/character', version=1, id='anya-s7', label={'ru': 'Аня, Гибли'}, faces='.', skinning='cor',
               source='Anny moood-woman (engine) + Human Base Meshes stylised head (CC0) + the drawing\'s own 3D forms (styles/s7-ghibli)',
               face=dict(x0=FX0, x1=FX1, y0=FY0, y1=FY1, shadow=fringe_shadow()),
               pieces=ranges, trianglePieces=tranges),
          dict(positions=V.astype(np.float32).ravel(), triangles=np.vstack(Ts).astype(np.uint32).ravel(),
               skinJoints=SJ, skinWeights=SWt.astype(np.float32), joints=J1.astype(np.float32).ravel(), frames=FR.ravel(),
               col=np.vstack(cols).astype(np.uint8), shd=np.vstack(shds).astype(np.uint8), lin=np.vstack(lins).astype(np.uint8),
               ow=(np.clip(np.concatenate(ows), 0, 1) * 255).astype(np.uint8), uv=np.vstack(uvs).astype(np.float32),
               tex=np.concatenate(texs).astype(np.uint8), pn=np.vstack(pns).astype(np.float32),
               pw=(np.clip(np.concatenate(pws), 0, 1) * 255).astype(np.uint8), pj=pj, two=np.concatenate(two).astype(np.uint8),
               band=np.concatenate(bands).astype(np.float32), ob=np.concatenate(obs).astype(np.float32)))
print('vertices', N, 'triangles', sum(len(t_) for t_ in Ts), {k: v[1] - v[0] for k, v in ranges.items()})
