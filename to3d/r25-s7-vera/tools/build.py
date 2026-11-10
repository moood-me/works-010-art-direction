"""A character of С7 (Гибли) in 3D: builds the pack the viewer (web/char.js) and the engine take.
  python3 build.py [outdir]
Who — config.py. Bases: Anny's body from the engine (its hands, the SOMA skeleton and its weights), Blender's Human Base
Meshes stylised head (CC0; hbm_export.py) fitted to the drawing's head (headfit.py); the clothes and the hair are the
drawing's own 3D forms (its torso loft, its limb tubes, its hair shell and locks — drawing.py) made into meshes here;
the face is drawn live from the drawing's face parts (web/face.js). Everything is skinned to SOMA's 77 joints, so
Kimodo's motions play on it through the engine.
What is built follows the character's garment spec (styles/s7-ghibli/tools/<who>.py SPEC): a top (with a turtleneck
collar or a hood), a jacket open in front, trousers (wide over shoes, or narrow into boots), shoes or boots,
headphones, earrings."""
import os, sys
import numpy as np
from scipy.spatial import cKDTree
import config, pack, mesh as M, headfit as Hf, drawing as D, shapes as S, blob

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(config.CACHE, 'out')
HBM = os.path.join(config.CACHE, 'hbm_head.npz')
os.makedirs(OUT, exist_ok=True)
CM = D.CM
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))
B, SPEC, who = D.B, D.SPEC, D.who
INK = D.rgb(D.INK)
top_s, over_s, bot_s, shoe_s = SPEC['top'], SPEC.get('over'), SPEC['bottom'], SPEC['shoes']
unit = lambda v: np.asarray(v, float) / np.linalg.norm(v)


def paint(n, c, s=None, l=INK):
    """per-vertex fill, shade, line colours: c a hex; the shade is the drawing's (a warm multiply)."""
    return dict(col=np.tile(D.rgb(c), (n, 1)), shd=np.tile(s if s is not None else D.shade(c), (n, 1)), lin=np.tile(l, (n, 1)))


# ---------------------------------------------------------------- skeleton and Anny's body
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body(config.BODY)
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
# the trunk: the body's heights mapped onto the drawing's (hip joints, shoulders, the neck's foot); the drawing's
# forward lean of the upper body (a slouch) moves the trunk's joints forward as it moves the torso's rings
ty0, ty1 = B['torso'][0][0], B['torso'][-1][0]
y_sh = B['shoulder'][1] + D.POSE.get('shrug', 0.0)
ymap = lambda y: np.interp(y, [0, J0[I['Hips'], 1], J0[I['LeftArm'], 1], J0[I['Neck1'], 1]], [0, B['hip_y'] * CM, y_sh * CM, B['neck'][0] * CM])
lean_z = lambda y: D.LEAN * np.clip((y / CM - ty0) / (ty1 - ty0), 0, 1) ** 1.5 * CM
for n in ['Hips', 'Spine1', 'Spine2', 'Chest']:
    J1[I[n], 1] = ymap(J0[I[n], 1]); J1[I[n], 2] = J0[I[n], 2] + lean_z(J1[I[n], 1])
J1[I['Neck1']] = m3(D.J['neck0'])
J1[I['Neck2']] = m3(D.J['neck1'])
J1[I['Head']] = D.head_to_model([0, -0.45, -0.25])[0]
J1[I['HeadEnd']] = D.head_to_model([0, 1.0, -0.1])[0]
J1[I['Jaw']] = D.head_to_model([0, -0.3, -0.12])[0]
FACE = D.FACE
hand_k = 0.88 * B['hand'] / 15.0
foot_k = 0.86 * shoe_s['len'] / 21.0
for s, sg in (('Left', 1), ('Right', -1)):
    side = 'l' if sg > 0 else 'r'
    J1[I[s + 'Eye']] = D.head_to_model([sg * FACE['eye_x'], FACE['eye_y'], 0.5])[0]
    ys = ymap(J0[I[s + 'Shoulder'], 1])
    J1[I[s + 'Shoulder']] = [sg * 0.015, ys, J0[I[s + 'Shoulder'], 2] - 0.03 + lean_z(ys)]
    J1[I[s + 'Arm']] = m3(D.J['sh' + side])
    for n, L in (('ForeArm', B['upper']), ('Hand', B['fore'])):
        j = I[s + n]; p = PARENT[j]; d = J0[j] - J0[p]
        J1[j] = J1[p] + d / np.linalg.norm(d) * L * CM
    for j in under(I[s + 'Hand'])[1:]:
        J1[j] = J1[PARENT[j]] + hand_k * (J0[j] - J0[PARENT[j]])
    J1[I[s + 'Leg']] = m3(D.J['hp' + side])
    J1[I[s + 'Shin']] = m3(D.J['kn' + side]) + [0, 0, 0.004]
    J1[I[s + 'Foot']] = m3(D.J['an' + side])
    for n in ('ToeBase', 'ToeEnd'):
        j = I[s + n]; J1[j] = J1[PARENT[j]] + foot_k * (J0[j] - J0[PARENT[j]])


def rot_between(u, v):
    u = u / np.linalg.norm(u); v = v / np.linalg.norm(v)
    c = u @ v; ax = np.cross(u, v); s = np.linalg.norm(ax)
    if s < 1e-9: return np.eye(3)
    ax /= s; K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + s * K + (1 - c) * K @ K


CHILD = {'Arm': 'ForeArm', 'ForeArm': 'Hand', 'Leg': 'Shin', 'Shin': 'Foot', 'Foot': 'ToeBase'}
arm_k = B['arm_r'][0] / 3.5        # how thick the drawing's arm is against Аня's (whom Anny's arm fits as it is)


def joint_affine(j):
    """joint j's move of the rest: x ↦ J1_j + A (x − J0_j): the bone turned to its new direction, stretched along
    it to its new length, thinned across it; the hand to the drawing's size."""
    n = NAMES[j]
    for s in ('Left', 'Right'):
        if n.startswith(s) and n[len(s):] in CHILD:
            c = I[s + CHILD[n[len(s):]]]
            d0, d1 = J0[c] - J0[j], J1[c] - J1[j]
            L = np.linalg.norm(d1) / np.linalg.norm(d0); u = d0 / np.linalg.norm(d0)
            r = {'Shin': 0.82, 'Leg': 0.9, 'Foot': 0.9, 'Arm': arm_k, 'ForeArm': arm_k}[n[len(s):]]
            return rot_between(d0, d1) @ (r * np.eye(3) + (L - r) * np.outer(u, u))
    if 'Toe' in n: return np.diag([0.9, 0.9, foot_k])
    if 'Hand' in n: return hand_k * np.eye(3)
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
near_wrist = np.zeros(len(P0), bool)
for s in ('Left', 'Right'): near_wrist |= np.linalg.norm(PF - J1[I[s + 'Hand']], axis=1) < 0.07
# kept of Anny: the hands with the wrists (the rest is under the clothes)
keep = handv | (fore & near_wrist)
tk = keep[TRI0].all(1)
bi = np.where(keep)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
Bd = dict(V=PF[bi], T=remap[TRI0[tk]], SJ=SJ0[bi], SW=SW0[bi])
nb = len(bi)
Bd.update(paint(nb, D.COL['skin']))
Bd['two'] = np.ones(nb)
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


LEGJ = {s: np.array([j in set(under(I[s + 'Leg'])) for j in range(NJ)]) for s in ('Left', 'Right')}
ARMJ = {s: np.array([j in set(under(I[s + 'Shoulder'])) for j in range(NJ)]) for s in ('Left', 'Right')}


def trunk_weights(V, T):
    """a garment on the trunk: the skin's weights nearby, without the arms' (a jacket's side does not go up with
    the arm that hangs beside it)."""
    W = transfer(V)
    for s in ('Left', 'Right'): W[:, ARMJ[s] & ~np.array([n.endswith('Shoulder') for n in NAMES])] *= 0.15
    W /= W.sum(1, keepdims=True)
    return smooth_w(W, T, len(V))


def leg_weights(V, T):
    """trousers and boots: the skin's weights nearby, each side keeping to its own leg."""
    W = transfer(V)
    x = V[:, 0] / CM
    W[:, LEGJ['Right']] *= smooth((1.5 - x) / 3)[:, None]; W[:, LEGJ['Left']] *= smooth((1.5 + x) / 3)[:, None]
    for s in ('Left', 'Right'): W[:, ARMJ[s]] = 0
    W /= W.sum(1, keepdims=True)
    return smooth_w(W, T, len(V), 8)


def arm_weights(V, T, side):
    W = transfer(V)
    tr = ARMJ[side]
    top = smooth(np.linalg.norm(V - J1[I[side + 'Arm']], axis=1) / 0.07)
    Wa = W * tr; Wa /= Wa.sum(1, keepdims=True) + 1e-9
    return smooth_w(Wa * top[:, None] + W * (1 - top[:, None]), T, len(V))


def rigid(V, **w):
    W = np.zeros((len(V), NJ))
    for n, x in w.items(): W[:, I[n]] = x
    return W


# ---------------------------------------------------------------- the head (headfit.py)
hl, hP, earm, fw = Hf.build(HBM)
HT = M.triangulate(hP)
# the face's triangles all facing out (the closed sockets and the folds of laying the face on one surface may face in)
_c = hl[HT].mean(1); _n = np.cross(hl[HT[:, 1]] - hl[HT[:, 0]], hl[HT[:, 2]] - hl[HT[:, 0]])
_out = _c - np.c_[np.zeros(len(_c)), _c[:, 1], np.full(len(_c), -0.1)]
_flip = ((_n * _out).sum(1) < 0) & ~earm[HT].any(1) & (_c[:, 1] > -1.0)
HT[_flip] = HT[_flip][:, ::-1]
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
# — what lies outside the drawing's skull form (its rings) is neck
_y = np.clip(hy, -0.98, 0.98); _zm = D.HEAD.zm(_y); _a = np.maximum(D.HEAD.a(_y), 1e-3)
_d = np.where(hz > _zm, D.HEAD.zf(_y) - _zm, _zm - D.HEAD.zb(_y))
_rr = (np.abs(hx / _a) ** D.HEAD.n + np.abs((hz - _zm) / _d) ** D.HEAD.n) ** (1 / D.HEAD.n)
neck = ((hy < -0.98) | ((_rr > 1.12) & (hy < -0.3) & (fw < 0.3))) & ~earm
Hh['col'][neck] = D.shade(D.COL['skin'])
# the face's drawn layer: front projection in head-local units (web/face.js draws in the same box)
FX0, FX1, FY0, FY1 = -1.0, 1.0, -1.3, 1.0
Hh['uv'] = np.c_[(hx - FX0) / (FX1 - FX0), (hy - FY0) / (FY1 - FY0)]
Hh['tex'] = ((hz > D.HEAD.zm(np.clip(hy, -1, 1)) - 0.1) & (hy > -1.05) & ~earm).astype(np.uint8)
# the face's shade by a smoothed head (one clean shade on the far side, not every bump of the base)
Ah = M.adjacency(nH, hP)
hs = M.smooth(V0, Ah, np.ones(nH, bool), iters=60, lam=0.5)
pn_s = M.vertex_normals(hs, HT)


# on the face: the normal of the drawing's own plain head form (its rings, without the nose and lips), so the shade's
# edge is the drawing's clean crescent, not the base's bumps
def form_normal(L):
    e = 1e-3; y = np.clip(L[:, 1], -0.99, 0.99)

    def p(t, yy):
        a_ = D.HEAD.a(yy); zm = D.HEAD.zm(yy); df = D.HEAD.zf(yy) - zm; db = zm - D.HEAD.zb(yy); n_ = D.HEAD.n
        s_, c_ = np.sin(t), np.cos(t)
        return np.stack([a_ * np.sign(s_) * np.abs(s_) ** (2 / n_), yy, zm + np.where(c_ > 0, df, db) * np.sign(c_) * np.abs(c_) ** (2 / n_)], 1)
    zm = D.HEAD.zm(y); a_ = np.maximum(D.HEAD.a(y), 1e-3)
    t = np.arctan2(L[:, 0] / a_, (L[:, 2] - zm) / np.maximum(D.HEAD.zf(y) - zm, 1e-3))
    n_ = np.cross(p(t + e, y) - p(t - e, y), p(t, y + e) - p(t, y - e))
    n_ /= np.linalg.norm(n_, axis=1, keepdims=True) + 1e-12
    return n_ * np.sign((n_ * (L - np.c_[np.zeros(len(L)), L[:, 1], zm])).sum(1, keepdims=True) + 1e-9)


fn = D.head_dir(form_normal(hl))
wf = smooth((hy + 0.95) / 0.1) * smooth((hz - D.HEAD.zm(np.clip(hy, -1, 1)) + 0.35) / 0.3) * ~earm
pn_h = pn_s * (1 - wf[:, None]) + fn * wf[:, None]
Hh['pn'] = pn_h / (np.linalg.norm(pn_h, axis=1, keepdims=True) + 1e-9); Hh['pw'] = 1 - smooth((-0.8 - hy) / 0.2)
Hh['two'] = np.ones(nH)
Hh['ow'] = np.ones(nH)


# ---------------------------------------------------------------- the clothes: the drawing's lofts as thin solids
def piece(V, T, c, W, **kw):
    d = dict(V=V, T=T, W=W); d.update(paint(len(V), c)); d.update(kw); return d


class LegRings:
    """the two legs' tubes as one ring per height (a garment's hem that hangs over the thighs must go round them)."""
    n = 2.4

    def __init__(self, ease):
        self.L = [D.F.limb(['hp' + s, 'kn' + s, 'an' + s], B['leg_r'], n=60) for s in ('l', 'r')]
        self.ease = ease; self.y0 = B['hip_y'] - B['thigh'] * 0.6; self.y1 = B['hip_y']

    def at(self, y):
        a_ = zf = -1e9; zb = 1e9
        for pts, rr in self.L:
            i = np.argmin(abs(pts[:, 1] - y)); r = rr[i] + self.ease
            a_ = max(a_, abs(pts[i, 0]) + r); zf = max(zf, pts[i, 2] + r); zb = min(zb, pts[i, 2] - r)
        return a_, zf, zb, 0.0, 0.0


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
y_neck = ty1
legs_r = LegRings(bot_s.get('ease', 1.2))
NT = 96
TS = np.linspace(-np.pi, np.pi, NT, endpoint=False)


def axis_ref(V):
    """a point inside, for each vertex: the body's axis at its height (leaning as the torso leans)."""
    return np.c_[np.zeros(len(V)), V[:, 1], lean_z(V[:, 1]) - 0.005]


def grid_loft(lo, ys_of_col, ts, R=60):
    """grid (rows, cols): column c at azimuth ts[c] runs over the heights ys_of_col(c, v) for v in 0…1."""
    G = np.zeros((R, len(ts), 3))
    for c, tt in enumerate(ts):
        for r, v in enumerate(np.linspace(0, 1, R)):
            G[r, c] = lo.pt(tt, ys_of_col(c, v))
    return G * CM


LINES = []
lw = 0.0021      # the drawing's thin lines (0.55 of its outline) at the turnaround's scale


def line_on(P, Nn, width, src, lift=0.0012, c=INK, taper=0.2):
    """a drawn line lying on a surface: points (m) and the surface's normals there; weights from the piece it lies on."""
    V_, T_ = S.strip(P, Nn, width * S.taper(len(P), taper), lift=lift)
    i = cKDTree(src['V']).query(V_)[1]
    LINES.append(dict(V=V_, T=T_, W=src['W'][i], col=np.tile(c, (len(V_), 1)), shd=np.tile(c, (len(V_), 1)),
                      lin=np.tile(c, (len(V_), 1)), ow=np.zeros(len(V_))))


def loft_normal(lo, t_, y_):
    e = 1e-3
    n_ = np.cross(lo.pt(t_ + e, y_) - lo.pt(t_ - e, y_), lo.pt(t_, y_ + 0.5) - lo.pt(t_, y_ - 0.5))
    n_ /= np.linalg.norm(n_)
    p = lo.pt(t_, y_)
    return n_ if n_ @ (p - [0, p[1], lo.at(y_)[4]]) > 0 else -n_


def surface_line(lo, ts, ys, width, src, push=0.1):
    P = np.array([lo.pt(t_, y_, push) for t_, y_ in zip(ts, ys)]) * CM
    line_on(P, np.array([loft_normal(lo, t_, y_) for t_, y_ in zip(ts, ys)]), width, src)


# the top (a sweater, a hoodie): the torso loft eased; where its hem hangs over the thighs it goes round them
top_lo = D.Loft(rings_max((torso, top_s['ease']), (legs_r, 0.5), ys=np.r_[np.arange(top_s['hem'], y_neck, 1.0), y_neck]), 2.4)
TV, TT, _ = S.shell(grid_loft(top_lo, lambda c, v: top_s['hem'] + (y_neck - top_s['hem']) * v, TS), True, 0.0025, axis_ref)
TOP = piece(TV, TT, top_s['c'], trunk_weights(TV, TT))
# the top closed onto the neck (under a turtleneck's collar or a hood)
n0, n1 = D.J['neck0'], D.J['neck1']
nd = unit(n1 - n0)
G = np.array([[top_lo.pt(tt, y) for tt in TS] for y in np.linspace(y_neck - 6, y_neck, 8)])
cap = np.array([[n0 + nd * 1.0 + B['neck_r'] * 0.98 * np.array([np.sin(tt), 0, np.cos(tt)]) for tt in TS]])
G = np.vstack([G, G[-1:] * 0.5 + cap * 0.5 + [0, 0.3, 0], cap]) * CM
SV, ST, _ = S.shell(G, True, 0.002, axis_ref)
YOKE = piece(SV, ST, top_s['c'], None)
YOKE['W'] = smooth_w(transfer(SV), ST, len(SV))
outer_lo, outer_ease, OUTER = top_lo, top_s['ease'], TOP

OVER = None
if over_s:
    # a jacket: bigger than the top everywhere, open at the front (the drawing's opening: narrow at the hem, wide at
    # the neck), its neckline round the neck at the back
    y_top = y_neck - 0.5
    over_lo = D.Loft(rings_max((torso, over_s['ease']), (top_lo, 0.35), (legs_r, 0.5),
                               ys=np.r_[np.arange(over_s['hem'], y_top, 1.0), y_top]), 2.4)
    w0, w1 = over_s['open'][:2]
    NC = 84
    OG = np.zeros((60, NC, 3))
    for r, v in enumerate(np.linspace(0, 1, 60)):
        y = over_s['hem'] + (y_top - over_s['hem']) * v
        g = w0 + (w1 - w0) * np.clip((y - (over_s['hem'] - 3)) / (y_top + 4 - (over_s['hem'] - 3)), 0, 1)
        for c, u in enumerate(np.linspace(0, 1, NC)):
            OG[r, c] = over_lo.pt(g + u * (2 * np.pi - 2 * g), y)
    OV, OT, _ = S.shell(OG * CM, False, 0.003, axis_ref)
    OVER = piece(OV, OT, over_s['c'], trunk_weights(OV, OT))
    outer_lo, outer_ease, OUTER = over_lo, over_s['ease'], OVER
    # the buttons the drawing puts by the opening's edge
    BUTTONS = []
    for y in over_s.get('buttons', []):
        tt = w0 + 0.03
        c = top_lo.pt(tt, y, 0.05) * CM; n_ = loft_normal(top_lo, tt, y)
        V_, T_ = S.tube(np.array([c, c + n_ * 0.0025]), [0.006, 0.0055], cols=14)
        bc = D.svgdoc.mix(over_s['c'], '#000000', 0.3)
        BUTTONS.append(piece(V_, T_, bc, TOP['W'][cKDTree(TOP['V']).query(V_)[1]], ow=np.full(len(V_), 0.4), shd=np.tile(D.rgb(bc), (len(V_), 1))))

# a turtleneck: the collar is a short wide tube round the neck, its top rolled in under the chin, folded once
COLLAR = None
if top_s.get('turtle'):
    r = B['neck_r'] + 0.8
    chin = D.head_to_model([0, -1.0, float(D.HEAD.zf(-1.0))])[0] / CM
    s_top = (chin - n0) @ nd + 0.2                    # up to the chin, as drawn: its front goes under the jaw
    prof = np.array([(-2.5, r + 0.2), (0, r + 0.5), (s_top * 0.5, r + 0.3), (s_top - 0.8, r + 0.1), (s_top - 0.25, r - 0.05),
                     (s_top, r - 0.45), (s_top - 0.3, r - 0.9), (s_top - 1.2, r - 1.2)])
    from geo import spline as _spline
    pr = _spline(prof, 40)
    CG = np.array([[n0 + nd * s_ + r_ * np.array([np.sin(tt), 0, np.cos(tt)]) for tt in TS[::2]] for s_, r_ in pr]) * CM
    CV = CG.reshape(-1, 3); CT = S.grid_tris(len(pr), CG.shape[1], True)
    if ((CV - axis_ref(CV)) * M.vertex_normals(CV, CT)).sum(1).mean() < 0: CT = CT[:, ::-1]
    sc = np.repeat(pr[:, 0], CG.shape[1])
    Wc = np.zeros((len(CV), NJ)); u1 = smooth(sc / 2.5); u2 = smooth((sc - 2.0) / 3.5) * 0.6
    Wc[:, I['Chest']] = 1 - u1; Wc[:, I['Neck1']] = u1 * (1 - u2); Wc[:, I['Neck2']] = u1 * u2
    COLLAR = piece(CV, CT, top_s['c'], Wc, two=np.ones(len(CV)))
    sf = s_top * 0.45; rf = np.interp(sf, pr[:20, 0], pr[:20, 1])
    tf = np.linspace(-1.45, 1.45, 30)
    Nn = np.array([[np.sin(tt), 0, np.cos(tt)] for tt in tf])
    line_on((n0 + nd * sf + rf * Nn) * CM, Nn, lw * 1.1, COLLAR)

# marks on the top the drawing lays on its surface: a hoodie's pocket and hem band
if hasattr(who, 'POCKET'):
    (y1_, w1_), (y0_, w0_) = who.POCKET
    tsl = np.linspace(-w1_, w1_, 30)
    surface_line(top_lo, tsl, [y1_] * 30, lw * 1.35, TOP)
    for s_ in (-1, 1):
        surface_line(top_lo, np.linspace(s_ * w1_, s_ * w0_, 16), np.linspace(y1_, y0_, 16), lw * 1.35, TOP)
    tsl = np.linspace(-2.2, 2.2, 80)
    surface_line(top_lo, tsl, [top_s['hem'] + 2.5] * 80, lw, TOP)

# the sleeves: the drawing's arm tube (radii arm_r + ease) from under the shoulder to the wrist, a cuff a little wider
sl_s = over_s if over_s and over_s.get('sleeve') else top_s
SLEEVES = []
for s, side in (('Left', 'l'), ('Right', 'r')):
    A_, E_, W_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']], J1[I[s + 'Hand']]
    e = sl_s['sleeve']['ease'] * CM
    r0 = np.array(B['arm_r']) * CM
    d1 = (E_ - A_) / np.linalg.norm(E_ - A_); d2 = (W_ - E_) / np.linalg.norm(W_ - E_)
    pts = [A_ - d1 * 0.01, A_ + d1 * 0.06, (A_ + E_) / 2, E_ - d1 * 0.02, E_ + d2 * 0.03, (E_ + W_) / 2, W_ - d2 * 0.035, W_ - d2 * 0.02, W_ + d2 * 0.003]
    rad = [r0[0] * 0.75 + e, r0[0] + e, (r0[0] + r0[1]) / 2 + e, r0[1] + e, r0[1] + e, r0[2] + e, r0[3] + e + 0.002, r0[3] + e + 0.006, r0[3] + e + 0.006]
    path = np.vstack([np.linspace(p, q, 5, endpoint=False) for p, q in zip(pts[:-1], pts[1:])] + [pts[-1]])
    rr = np.interp(np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))],
                   np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.array(pts), axis=0), axis=1))], rad)
    V_, T_ = S.tube(path, rr, cols=28)
    SL = piece(V_, T_, sl_s['c'], arm_weights(V_, T_, s), side=s)
    SLEEVES.append(SL)
    # the fold at the elbow, on the sleeve's front
    zf_ = np.array([0, 0, 1.0]); zf_ = unit(zf_ - d2 * (zf_ @ d2))
    ss = np.linspace(-0.025, 0.015, 8)
    line_on(np.array([E_ + d2 * s_ + zf_ * (r0[1] + e) for s_ in ss]) + np.cross(d2, zf_) * np.linspace(-0.004, 0.004, 8)[:, None],
            np.tile(zf_, (8, 1)), lw, SL)

# ---------------------------------------------------------------- trousers: the pelvis and both legs as one piece
e_b = bot_s.get('ease', 1.2)


def pelvis_push(y):
    """the trousers' ease; under the garments that hang over them, thinner than those."""
    p = e_b
    for g in (over_s, top_s):
        if g: p += (min(p, g['ease'] - 0.5) - p) * float(smooth((y - g['hem'] + 2.0) / 1.5))
    return p


fs = [blob.loft(torso, ty0, bot_s['waist'], pelvis_push)]
knee_r = {}
for side in ('l', 'r'):
    pts, rr = D.F.limb(['hp' + side, 'kn' + side, 'an' + side], B['leg_r'], n=24)
    fs.append(blob.tube(pts, rr + np.array([pelvis_push(y) for y in pts[:, 1]])))
    kn, an = D.J['kn' + side], D.J['an' + side]
    knee_r[side] = float(np.interp(B['thigh'], np.linspace(0, B['thigh'] + B['shin'], len(B['leg_r'])), B['leg_r'])) + e_b
    if not bot_s.get('narrow'):        # wide below the knee, down over the shoe
        fs.append(blob.tube([kn, an + [0, -1.5, 0]], [B['leg_r'][len(B['leg_r']) // 2] + e_b + 0.3, B['leg_r'][-1] + e_b + 1.6]))
hem_y = D.J['anl'][1] if bot_s.get('narrow') else 1.2
PV, PT = blob.mesh(blob.above(blob.join(fs, 1.4), hem_y), 0.8)
PANTS = piece(PV, PT, bot_s['c'], leg_weights(PV, PT))
# the drawing's fold at each knee
for side in ('l', 'r'):
    kn = D.J['kn' + side]; hp, an = D.J['hp' + side], D.J['an' + side]
    ax = unit(an - hp)
    q = np.linspace(kn + [-2.5, 2, 4.5], kn + [1, 0, 5.5], 8)
    c = kn + ((q - kn) @ ax)[:, None] * ax
    Nn = (q - c) / np.linalg.norm(q - c, axis=1, keepdims=True)
    line_on((c + Nn * (knee_r[side] + (0.5 if not bot_s.get('narrow') else 0.1))) * CM, Nn, lw, PANTS, lift=0.002)

# ---------------------------------------------------------------- shoes / boots
SHOES, EXTRA = [], []
for s, side in (('Left', 'l'), ('Right', 'r')):
    sg = 1 if side == 'l' else -1
    an = D.J['an' + side]; Ls, r = shoe_s['len'], shoe_s['r']; o_ = np.radians(shoe_s.get('out', 10))
    fwd = np.array([sg * np.sin(o_), 0, np.cos(o_)]); across = np.array([np.cos(o_), 0, -sg * np.sin(o_)])
    heel = an + [0, -r * 0.6, 0] - fwd * Ls * 0.18
    mid = an + fwd * Ls * 0.25 + [0, -r * 0.3, 0]
    toe = an + [0, -r * 0.8, 0] + fwd * Ls * 0.78
    foot = blob.tube([heel, mid, toe], [0.95 * r, 1.05 * r, 0.75 * r])

    def foot_w(V_):
        W_ = np.zeros((len(V_), NJ))
        u_ = smooth((((V_ / CM) - an) @ fwd - Ls * 0.35) / (Ls * 0.25))
        up_ = smooth((V_[:, 1] / CM - an[1] - 1.0) / 6.0) * (1 - u_)
        W_[:, I[s + 'Foot']] = (1 - u_) * (1 - up_); W_[:, I[s + 'ToeBase']] = u_; W_[:, I[s + 'Shin']] = up_
        return W_
    if shoe_s.get('sole'):
        # a heavy boot: the foot and a shaft up the shin as one piece, a thick sole, laces
        up = unit(D.J['kn' + side] - an)
        f = blob.above(blob.join([foot, blob.tube([an + up * 13, an + up * 2], [r * 0.92, r * 0.98])], 0.8), 0.0)
        V_, T_ = blob.mesh(f, 0.55)
        SHOES.append(piece(V_, T_, shoe_s['c'], smooth_w(foot_w(V_), T_, len(V_), 6), side=s))
        sole_h = 0.24 * (an[1] + r * 0.6 + r * 0.85)
        V_, T_ = blob.mesh(blob.below(blob.grow(f, 0.2), sole_h), 0.5)
        EXTRA.append(('sole' + s, piece(V_, T_, shoe_s['sole'], smooth_w(foot_w(V_), T_, len(V_), 6), ow=np.full(len(V_), 0.7))))
        acid = D.rgb(who.ACID)
        for i, h_ in enumerate((2.5, 5.2, 7.9, 10.6)):
            sl_ = 0.5 if i % 2 else -0.5
            ph = np.linspace(-0.42, 0.42, 7); R_ = r * 0.96
            P_ = np.array([an + up * (h_ + sl_ * (-p_ / 0.42)) + R_ * (np.cos(p_) * fwd + np.sin(p_) * across) for p_ in ph])
            Nn = np.array([np.cos(p_) * fwd + np.sin(p_) * across for p_ in ph])
            V_, T_ = S.strip(P_ * CM, Nn, 0.0042, lift=0.0015)
            LINES.append(dict(V=V_, T=T_, W=rigid(V_, **{s + 'Shin': 0.75, s + 'Foot': 0.25}), col=np.tile(acid, (len(V_), 1)),
                              shd=np.tile(D.shade(who.ACID), (len(V_), 1)), lin=np.tile(INK, (len(V_), 1)), ow=np.zeros(len(V_))))
    else:
        V_, T_ = blob.mesh(blob.above(foot, 0.0), 0.5)
        SHOES.append(piece(V_, T_, shoe_s['c'], smooth_w(foot_w(V_), T_, len(V_), 6), side=s))

# ---------------------------------------------------------------- a hood lying round the neck, headphones on it
if hasattr(who, 'HOOD_EASE'):
    def ring(a_deg, r, y, fwd=0.0):
        a_ = np.radians(a_deg)
        return n0 + np.array([r * np.sin(a_), 0.0, r * np.cos(a_) + fwd]) + nd * y
    fs = [blob.tube([ring(a_, 8.2, 4.6 - 1.6 * abs(abs(a_) - 180) / 80, -1.5) for a_ in np.linspace(100, 260, 15)], [3.9] * 15)]
    strings = []
    for s_ in (-1, 1):
        fr = [ring(s_ * a_, 8.4 - 1.2 * (100 - a_) / 85, 3.0 - 6.4 * ((100 - a_) / 85) ** 1.2, -1.5 + 2.2 * (100 - a_) / 85)
              for a_ in np.linspace(100, 15, 10)]
        fs.append(blob.tube(fr, np.linspace(3.9, 2.3, len(fr))))
        strings.append((s_, fr[-1] + np.array([0, -1.5, 1.2])))
    V_, T_ = blob.mesh(blob.join(fs, 0.6), 0.6)
    HOOD = piece(V_, T_, top_s['c'], rigid(V_, Chest=1.0))
    EXTRA.append(('hood', HOOD))
    # the drawstrings: light cords lying on the chest

    def front_z(x, y):
        a_, zf_, zb_, x0, z0 = top_lo.at(y); zm = (zf_ + zb_) / 2
        return z0 + zm + (zf_ - zm) * (1 - min(abs(x / a_), 1) ** top_lo.n) ** (1 / top_lo.n)
    from geo import bezier as _bez
    for s_, a0 in strings:
        c = _bez(a0, a0 + [s_ * 0.6, -4.5, 0.6], a0 + [s_ * 0.2, -9.0, 0.2], n=14)
        c[:, 2] = [front_z(x, y) + 0.3 for x, y, _ in c]
        V_, T_ = S.tube(c * CM, [0.0028] * len(c), cols=8)
        EXTRA.append(('string%d' % s_, piece(V_, T_, '#e9e1d4', TOP['W'][cKDTree(TOP['V']).query(V_)[1]], ow=np.full(len(V_), 0.4))))
    # the headphones: the band behind the neck, the cups resting on the collarbones, turned outward
    band = [ring(a_, 7.6, 6.0 - 2.4 * abs(abs(a_) - 180) / 100, -1.0) for a_ in np.linspace(80, 280, 17)]
    V_, T_ = blob.mesh(blob.tube(band, [1.25] * len(band)), 0.4)
    EXTRA.append(('band', piece(V_, T_, who.COAL, rigid(V_, Chest=1.0))))
    for s_ in (-1, 1):
        c = ring(s_ * 60, 7.6, 0.6, 0.5)
        n_ = unit([s_ * 0.80, 0.25, 0.55])
        V_, T_ = blob.mesh(blob.tube([c - n_ * 1.5, c - n_ * 0.2], [3.5, 3.7]), 0.4)
        EXTRA.append(('pad%d' % s_, piece(V_, T_, who.COAL, rigid(V_, Chest=1.0))))
        V_, T_ = blob.mesh(blob.tube([c, c + n_ * 2.0], [3.4, 2.8]), 0.35)
        CUP = piece(V_, T_, who.ACID, rigid(V_, Chest=1.0))
        EXTRA.append(('cup%d' % s_, CUP))
        u_ = unit(np.cross(n_, [0, 1, 0])); v_ = np.cross(n_, u_)
        tt = np.linspace(0, 2 * np.pi, 40)
        cc = c + n_ * (2.0 + np.sqrt(2.8 ** 2 - 1.5 ** 2))
        ringp = np.array([cc + 1.5 * (np.cos(x) * u_ + np.sin(x) * v_) for x in tt])
        line_on(ringp * CM, np.array([unit(p_ - (c + n_ * 2.0)) for p_ in ringp]), lw * 1.2, CUP, taper=0.01)

# small gold earrings (the drawing's `extra`)
if config.WHO == 'vera':
    for side in (-1, 1):
        a_ = float(D.HEAD.a(-0.40))
        c = D.head_to_model([side * (a_ - 0.01), -0.47, float(D.HEAD.zm(-0.40)) + 0.06])[0]
        rr_ = 0.035 * D.HK * CM
        zz = np.linspace(-1, 1, 9)
        V_, T_ = S.tube(c + np.outer(zz * rr_ * 0.98, [1.0, 0, 0]), rr_ * np.sqrt(np.maximum(1 - zz ** 2 * 0.96, 0)), cols=12)
        EXTRA.append(('earring%d' % side, piece(V_, T_, '#d8b058', rigid(V_, Head=1.0), ow=np.full(len(V_), 0.5))))

# ---------------------------------------------------------------- the hair (hair3d.py)
import hair3d  # noqa: E402
HAIR = hair3d.build(dict(head=(V0, HT), earm=earm, J1=J1, I=I, NJ=NJ, smooth_w=smooth_w, lofts=[(outer_lo, 0.6)]))
LINES += hair3d.LINES


# ---------------------------------------------------------------- the fringe's shadow on the forehead (as the drawing
# does: the front hair's shape, shifted a little down and right, over the skin), in the face layer's head-local units
def fringe_shadow():
    from geo import View, shift, polys
    from head import Head
    from hair import Hair
    K = 150.0           # the drawing works in pixels (its small round-offs are in px): draw at 150 px a unit
    h0 = Head(D.FACE); h0.place((0, 0, 0), 2.0)
    v = View(yaw=0, pitch=0, s=K)
    Fh, _, _ = Hair(h0, D.HAIRDEF).build(v)
    sk_ = h0.skull(v)
    g = shift(Fh, 0.015 * K, 0.045 * K).intersection(sk_).difference(Fh)
    g = g.buffer(-0.012 * K).buffer(0.012 * K)      # only the shadow's body under the locks' tips, not slivers along their edges
    out = []
    for p in polys(g):
        if p.area < 1e-4 * K * K: continue
        for ring_ in [p.exterior] + list(p.interiors):
            out.append([[float(x) / K, float(-y) / K] for x, y in np.asarray(ring_.coords)])
    return out


# ---------------------------------------------------------------- the face's numbers for the live layer (web/face.js)
def face_params():
    F_ = D.FACE
    g = lambda k, d: F_.get(k, d)
    return dict(eye_x=F_['eye_x'], eye_y=F_['eye_y'], eye_w=F_['eye_w'], eye_h=F_['eye_h'], iris_w=F_['iris_w'], iris_h=F_['iris_h'],
                flick=g('flick', 1.0), lid_w=g('lid_w', 1.25), eye_tilt=g('eye_tilt', 0.0), crease=g('crease', 0), lashes=g('lashes', 0),
                brow_y=F_['brow_y'], brow_w=F_['brow_w'], brow_th=g('brow_th', 1.6), brow_arch=g('brow_arch', 0.035),
                nose_y=F_['nose_y'], nose_len=g('nose_len', 0.16), nose_w=g('nose_w', 0.075),
                mouth_y=F_['mouth_y'], mouth_w=F_['mouth_w'], mouth_curve=g('mouth_curve', 0.0), lower_lip=g('lower_lip', 0), blush=g('blush', 0),
                white=g('white', '#f6f1ea'), iris=who.IRIS, iris_light=g('iris_light', '#8a5a40'), mouth_c=g('mouth_c', '#7a2e2e'),
                hair=who.HAIR, skin=who.SKIN, ink=D.INK,
                marks=[dict(pts=[list(p) for p in m['pts']], w=m.get('w', 0.6), op=m.get('op', 1.0)) for m in F_.get('marks', [])])


def expr_js(E):
    E = D.Expr(E)
    m = E.mouth
    return dict(open=E.open, lid_in=E.lid_in, lid_out=E.lid_out, smile_eye=E.smile_eye, closed=float(E.closed), iris=E.iris,
                lx=E.look[0], ly=E.look[1], brow_up=E.brow_up, brow_in=E.brow_in, brow_arch=E.brow_arch,
                mLine=float(m == 'line'), mD=float(m == 'D'), mO=float(m == 'O'), mShout=float(m not in ('line', 'D', 'O')),
                smile=E.smile, smirk=E.smirk, mouth_w=E.mouth_w, mouth_open=E.mouth_open if m != 'line' else 0.0,
                teeth=float(bool(E.teeth)), tongue=float(bool(E.tongue)), blush=E.blush)


# the sheet's expressions (styles/s7-ghibli/tools/build.py EXPR), a character's own where its module gives them
SHEET = dict(
    joy=dict(closed=1, mouth='D', mouth_open=0.9, smile=1.0, teeth=True, blush=0.6, brow_up=0.35, mouth_w=1.25),
    surprise=dict(open=1.2, iris=0.78, brow_up=1.0, brow_arch=0.6, mouth='O', mouth_open=0.7, mouth_w=0.7),
    sad=dict(open=0.72, lid_out=0.35, brow_in=-1.0, brow_up=0.2, smile=-0.9, look=(0.0, -0.7), mouth_w=0.9),
    anger=dict(open=0.85, lid_in=0.45, brow_in=1.1, brow_up=-0.45, mouth='shout', mouth_open=0.85, teeth=True, smile=-0.5, mouth_w=1.35))
EXPRS = dict(calm=expr_js(config.CALM), plain=expr_js({}))
for k, v in SHEET.items(): EXPRS[k] = expr_js(getattr(who, 'EXPR', {}).get(k, v))

# the 'stand' pose's arm directions (the drawing paints the arms over the body; here they hang just outside it)
arm = D.POSE['arml']
STAND = dict(upper=list(arm['upper']), fore=list(arm['fore']), hand=list(arm.get('hand', arm['fore'])), palm=list(arm.get('palm', (-1, 0, 0.2))),
             out=config.ARM_OUT, cy=B['hip_y'] * CM)

# ---------------------------------------------------------------- one pack
pieces = [('body', Bd), ('head', Hh), ('yoke', YOKE), ('pants', PANTS), ('top', TOP)] + ([('collar', COLLAR)] if COLLAR else []) + \
         ([('over', OVER)] + [('button%d' % i, b_) for i, b_ in enumerate(BUTTONS)] if OVER else []) + \
         [('sleeve' + p_['side'], p_) for p_ in SLEEVES] + [('shoe' + p_['side'], p_) for p_ in SHOES] + EXTRA + [('hair', HAIR)] + [('lines', dict(
             V=np.vstack([l_['V'] for l_ in LINES]), T=np.vstack([l_['T'] + o for l_, o in zip(LINES, np.cumsum([0] + [len(l_['V']) for l_ in LINES])[:-1])]),
             W=np.vstack([l_['W'] for l_ in LINES]), col=np.vstack([l_['col'] for l_ in LINES]), shd=np.vstack([l_['shd'] for l_ in LINES]),
             lin=np.vstack([l_['lin'] for l_ in LINES]), ow=np.concatenate([l_['ow'] for l_ in LINES])))]
Vs, Ts, Ws, cols, shds, lins, ows, uvs, texs, pns, pws, two, obs = [], [], [], [], [], [], [], [], [], [], [], [], []
base = 0; ranges = {}; tbase = 0; tranges = {}
for name, p in pieces:
    n = len(p['V'])
    Vs.append(p['V']); Ts.append(p['T'] + base); Ws.append(p['W'])
    cols.append(p['col']); shds.append(p['shd']); lins.append(p['lin'])
    ows.append(p.get('ow', np.ones(n))); uvs.append(p.get('uv', np.zeros((n, 2))))
    texs.append(p.get('tex', np.zeros(n))); pns.append(p.get('pn', np.zeros((n, 3)))); pws.append(p.get('pw', np.zeros(n)))
    two.append(p.get('two', np.full(n, 1 if name in ('lines',) else 0))); obs.append(p.get('ob', np.zeros(n)))
    ranges[name] = [base, base + n]; tranges[name] = [tbase, tbase + len(p['T'])]; base += n; tbase += len(p['T'])
V = np.vstack(Vs); W = np.maximum(np.vstack(Ws), 0); N = len(V)
W /= W.sum(1, keepdims=True)
W[W < 0.05] = 0          # no dust of tiny weights left by smoothing
order = np.argsort(-W, 1)[:, :4]
SJ = order.astype(np.uint8); SWt = np.take_along_axis(W, order, 1); SWt /= SWt.sum(1, keepdims=True)
pj = SJ[:, 0].astype(np.float32)
pack.save(os.path.join(OUT, config.WHO + '.json'),
          dict(format='r1/character', version=1, id=config.WHO + '-s7', label={'ru': config.LABEL}, faces='.', skinning='dqs',
               source='Anny %s (engine) + Human Base Meshes stylised head (CC0) + the drawing\'s own 3D forms (styles/s7-ghibli)' % config.BODY,
               face=dict(x0=FX0, x1=FX1, y0=FY0, y1=FY1, shadow=fringe_shadow(), params=face_params(), expr=EXPRS),
               stand=STAND, headFwd=[float(x) for x in D.HR[:, 2]],
               pieces=ranges, trianglePieces=tranges),
          dict(positions=V.astype(np.float32).ravel(), triangles=np.vstack(Ts).astype(np.uint32).ravel(),
               skinJoints=SJ, skinWeights=SWt.astype(np.float32), joints=J1.astype(np.float32).ravel(), frames=FR.ravel(),
               col=np.vstack(cols).astype(np.uint8), shd=np.vstack(shds).astype(np.uint8), lin=np.vstack(lins).astype(np.uint8),
               ow=(np.clip(np.concatenate(ows), 0, 1) * 255).astype(np.uint8), uv=np.vstack(uvs).astype(np.float32),
               tex=np.concatenate(texs).astype(np.uint8), pn=np.vstack(pns).astype(np.float32),
               pw=(np.clip(np.concatenate(pws), 0, 1) * 255).astype(np.uint8), pj=pj, two=np.concatenate(two).astype(np.uint8),
               ob=np.concatenate(obs).astype(np.float32)))
print('vertices', N, 'triangles', sum(len(t_) for t_ in Ts), {k: v[1] - v[0] for k, v in ranges.items()})
