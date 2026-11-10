"""Тим assembled: Anny's fitted child body (body.py), the fitted base head (fit_head.py) with its glass eyes, the
replacement face pieces (face.py), the sculpted hair (fit_hair.py), the drawing's thin neck, and the clothes — every
piece skinned on SOMA's 77 joints — written as an engine body on its own topology (engine/README.md: Formats), plus
what the renderer and the viewer need: which vertices are which piece and its material, the paint coordinates.

Clothes, from the drawing's numbers (cast.TIM_FIG / TIM_BODY of styles/s8-stopmotion):
- the sweater: Anny's trunk and arms, each vertex carried out to the drawing's barrel (the torso loft: its width,
  front and back at every height) or round its arm bone to the sleeve's radius — so it keeps Anny's weights and bends
  as she does; a ribbed band at the neckline and at the cuffs and hem;
- the shorts: Anny's hips and thighs carried round the thigh bones to the drawing's wide legs (r 0.15 head);
- the socks: the shins below the drawing's sock top, ribbed; the shoes: lofted round each foot (the drawing's
  rounded red shoe with a pale sole).
Writes CACHE/engine/data/{bodies,topology}/savely8.* and CACHE/model.json (pieces, materials) + CACHE/rest.npz."""
import json, math, os
import numpy as np, igl
import base, drawing
import fit_body as body
from drawing import P as TP
import cast
from head import interp
from common import CACHE, HH, FEET, HEAD_Y, IX, NAMES, PARENT, vertex_normals, pack, ENGINE, FOLDER

NJ = len(NAMES)
Z0 = 0.035                    # the head's centre (and the drawing's z = 0) in the engine's z
O = np.array([0.0, HEAD_Y, Z0])


def W(X):
    """the drawing's head units (engine axes, head centre 0) → metres in the engine's world"""
    return O + np.asarray(X) * HH


def Wd(x, y, z):
    """the drawing's own coordinates (x right, y down from the head's centre, z toward us) → world"""
    return W(np.stack([np.asarray(x, float), -np.asarray(y, float), np.asarray(z, float)], -1))


def dense(sj, sw):
    D = np.zeros((len(sj), NJ))
    for k in range(4): np.add.at(D, (np.arange(len(sj)), sj[:, k]), sw[:, k])
    return D


def top4(D):
    j = np.argsort(-D, 1)[:, :4]; w = np.take_along_axis(D, j, 1)
    return j, w / np.maximum(w.sum(1, keepdims=True), 1e-9)


def one(n, joint):
    return np.tile([IX[joint], 0, 0, 0], (n, 1)), np.tile([1.0, 0, 0, 0], (n, 1))


PIECES = []


def piece(name, mat, V, T, sj, sw, uv=None, pat=None, tint=None, subdiv=0):
    V = np.asarray(V, float)
    PIECES.append(dict(name=name, mat=mat, V=V, T=np.asarray(T, np.int64), sj=np.asarray(sj), sw=np.asarray(sw, float),
                       uv=np.zeros((len(V), 2)) if uv is None else np.asarray(uv, float),
                       pat=V.copy() if pat is None else np.asarray(pat, float),
                       tint=np.zeros(len(V)) if tint is None else np.asarray(tint, float), subdiv=subdiv))


def cut(V, T, f, A=None):
    """keep where f < 0; triangles crossing 0 split on the zero level (clean edges along any curve)"""
    V = list(map(tuple, V)); A = None if A is None else list(map(tuple, A)); f = list(f)
    on = [False] * len(V); mid = {}

    def edge(a, b):
        k = (min(a, b), max(a, b))
        if k not in mid:
            t = f[a] / (f[a] - f[b])
            V.append(tuple(np.array(V[a]) * (1 - t) + np.array(V[b]) * t))
            if A is not None: A.append(tuple(np.array(A[a]) * (1 - t) + np.array(A[b]) * t))
            f.append(0.0); on.append(True); mid[k] = len(V) - 1
        return mid[k]
    out = []
    for tri in T:
        s = [f[v] < 0 for v in tri]; n = sum(s)
        if n == 3: out.append(tri); continue
        if n == 0: continue
        r = 0
        while not (s[r] if n == 1 else not s[r]): r += 1
        a, b, c = tri[r], tri[(r + 1) % 3], tri[(r + 2) % 3]
        if n == 1: out.append((a, edge(a, b), edge(a, c)))
        else:
            ab, ac = edge(a, b), edge(a, c); out.append((ab, b, c)); out.append((ab, c, ac))
    V = np.array(V); T = np.array(out)
    used = np.unique(T); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
    return V[used], remap[T], (None if A is None else np.array(A)[used]), np.array(on)[used]


def smooth(V, T, it=10, lam=0.5, fixed=None):
    adj = igl.adjacency_list(T); V = V.copy()
    for _ in range(it):
        M = np.array([V[s].mean(0) if len(s) else V[i] for i, s in enumerate(adj)])
        D = M - V
        if fixed is not None: D[fixed] = 0
        V = V + lam * D
    return V


def boundary_loops(T):
    from collections import defaultdict
    cnt = defaultdict(int)
    for t in T:
        for k in range(3): a, b = t[k], t[(k + 1) % 3]; cnt[(min(a, b), max(a, b))] += 1
    nxt = {}
    for t in T:
        for k in range(3):
            a, b = t[k], t[(k + 1) % 3]
            if cnt[(min(a, b), max(a, b))] == 1: nxt[a] = b
    out, seen = [], set()
    for s in nxt:
        if s in seen: continue
        L = [s]; seen.add(s); x = nxt[s]
        while x != s and x not in seen: L.append(x); seen.add(x); x = nxt.get(x, s)
        out.append(np.array(L))
    return out


def tube_along(path, radii, n=24, closed_ends=False):
    """a ring tube along a polyline path (M×3) with radii (M), rings by a parallel transport frame"""
    path = np.asarray(path, float); M = len(path)
    tg = np.gradient(path, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True)
    ref = np.array([0, 0, 1.0]) if abs(tg[0, 2]) < 0.9 else np.array([1.0, 0, 0])
    a = np.cross(tg[0], ref); a /= np.linalg.norm(a)
    V, A = [], []
    for i in range(M):
        if i:
            a = a - (a @ tg[i]) * tg[i]; a /= np.linalg.norm(a)
        b = np.cross(tg[i], a)
        for j in range(n):
            q = 2 * math.pi * j / n
            V.append(path[i] + radii[i] * (math.cos(q) * a + math.sin(q) * b))
            A.append((q, i))
    T = []
    for i in range(M - 1):
        for j in range(n):
            p, q = i * n + j, i * n + (j + 1) % n
            T += [(p, q, p + n), (q, q + n, p + n)]
    return np.array(V), np.array(T), np.array(A, float)


# ======================================================================================== the body
BV, BJ = body.fit()
B = body.B
BT = B['triangles']; BP = B['parts'] / 255.0; PN = list(B['partnames'])
pw = lambda *names: sum(BP[:, PN.index(n)] for n in names)
BD = dense(B['sj'], B['sw'])
BN = vertex_normals(BV, BT)

J = BJ.copy()
J[IX['HeadEnd']] = W([0, 0.5, 0])
J[IX['Jaw']] = W([0, -0.3, 0.2])
for s, n in ((1, 'LeftEye'), (-1, 'RightEye')):
    J[IX[n]] = W(drawing.eye_centre(s))

# ======================================================================================== the head
HD = np.load(f'{CACHE}/head_raw.npz')
HV, HT = HD['V'], base.tris(HD['Q'])
ear = np.r_[HD['earL'] | HD['earR'], np.zeros(len(HV) - len(HD['earL']), bool)].astype(float)
sj, sw = one(len(HV), 'Head')
piece('head', 'skin', W(HV), HT, sj, sw, uv=np.c_[HV[:, 0] + 0.5, HV[:, 1] + 0.5], tint=ear * 0.6, subdiv=1)


def sphere(c, r, n=40):
    th = np.linspace(0, np.pi, n); ph = np.linspace(0, 2 * np.pi, 2 * n, endpoint=False)
    Pp = np.array([[np.sin(t) * np.cos(p), np.sin(t) * np.sin(p), np.cos(t)] for t in th for p in ph])
    m = 2 * n; T = []
    for i in range(n - 1):
        for j in range(m):
            a, b = i * m + j, i * m + (j + 1) % m; T += [(a, b, a + m), (b, b + m, a + m)]
    return c + Pp * r, np.array(T), np.c_[Pp[:, 0] * 0.5 + 0.5, Pp[:, 1] * 0.5 + 0.5]


for s, nm in ((1, 'eyeL'), (-1, 'eyeR')):
    V, T, uv = sphere(drawing.eye_centre(s), drawing.EYE_R)
    sj, sw = one(len(V), 'Head')
    piece(nm, 'eye', W(V), T, sj, sw, uv=uv)

# the replacement pieces, at the calm face (face.mjs mixes their shapes)
F = np.load(f'{CACHE}/face.npz')
for part, mat in (('lipU', 'lip'), ('lipL', 'lip'), ('cav', 'mouth'), ('teethU', 'teeth'), ('teethL', 'teeth')):
    V = F[f'{part}_calm']; sj, sw = one(len(V), 'Head')
    piece(part, mat, W(V), F[part + '_T'], sj, sw)
V = F['brow_calm']; sj, sw = one(len(V), 'Head'); piece('brows', 'brow', W(V), F['brow_T'], sj, sw)
V = F['lash_V']; sj, sw = one(len(V), 'Head'); piece('lashes', 'lash', W(V), F['lash_T'], sj, sw)

HR = np.load(f'{CACHE}/hair.npz')
sj, sw = one(len(HR['V']), 'Head')
piece('hair', 'hair', W(HR['V']), HR['T'], sj, sw, uv=HR['uv'])

# ======================================================================================== the neck
N = cast.TIM_BODY['neck']
ys = np.linspace(0.25, 0.82, 24)
ring = []
for y in ys:
    a = interp(N['a'], y); fr = interp(N['front'], y); bk = interp(N['back'], y)
    ring.append((y, a, (fr - bk) / 2, (fr + bk) / 2))
nn = 32
NV = []
for y, a, b, c in ring:
    for j in range(nn):
        q = 2 * math.pi * j / nn
        NV.append(Wd(a * math.sin(q), y, c + b * math.cos(q)))
NV = np.array(NV); NT = []
for i in range(len(ring) - 1):
    for j in range(nn):
        p, q = i * nn + j, i * nn + (j + 1) % nn
        NT += [(p, p + nn, q), (q, p + nn, q + nn)]
y = NV[:, 1]
yH, y2, y1 = J[IX['Head'], 1], J[IX['Neck2'], 1], J[IX['Neck1'], 1]
D = np.zeros((len(NV), NJ))
a = np.clip((y - y2) / (yH - y2), 0, 1); b = np.clip((y - y1) / (y2 - y1), 0, 1)
D[:, IX['Head']] = a; D[:, IX['Neck2']] = (1 - a) * b; D[:, IX['Neck1']] = (1 - a) * (1 - b)
sj, sw = top4(D)
piece('neck', 'skin', NV, np.array(NT), sj, sw, uv=np.full((len(NV), 2), 0.5), tint=np.full(len(NV), 0.15))

# ======================================================================================== clothes
FIG = cast.TIM_FIG
TOR = FIG['torso']


def torso_at(yw):
    """the drawing's barrel at world height yw: half width, front and back z (world), centre z"""
    yd = FEET - yw / HH
    yd = np.clip(yd, 0.56, 1.9)
    a = np.array([interp(TOR['a'], v) for v in np.atleast_1d(yd)]) * HH
    fr = np.array([interp(TOR['front'], v) for v in np.atleast_1d(yd)]) * HH + Z0
    bk = np.array([interp(TOR['back'], v) for v in np.atleast_1d(yd)]) * HH + Z0
    return a, fr, bk


def bone_t(X, a, b):
    A, Bb = BJ[IX[a]], BJ[IX[b]]; d = Bb - A
    t = ((X - A) @ d) / (d @ d)
    return t, A + t[:, None] * d


Y = BV[:, 1]
armw = pw('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm')
handw = pw('Lhand', 'Rhand')
legw = pw('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot')
side = np.where(BV[:, 0] >= 0, 1, -1)


def arm_coord(X):
    """along the arm: 0 at the shoulder joint, 1 at the elbow, 2 at the wrist; and the point on the bone"""
    out_t = np.zeros(len(X)); out_p = np.zeros_like(X)
    for s, pre in ((1, 'Left'), (-1, 'Right')):
        m = (X[:, 0] >= 0) if s > 0 else (X[:, 0] < 0)
        t1, p1 = bone_t(X[m], pre + 'Arm', pre + 'ForeArm')
        t2, p2 = bone_t(X[m], pre + 'ForeArm', pre + 'Hand')
        lower = t1 > 1
        out_t[m] = np.where(lower, 1 + np.clip(t2, 0, 3), t1)
        out_p[m] = np.where(lower[:, None], p2, p1)
    return out_t, out_p


HEM = (FEET - 1.75) * HH                          # the sweater's hem (world y)
NECK_F, NECK_B = (FEET - 0.63) * HH, (FEET - 0.57) * HH   # the neckline, front and back
at, ap = arm_coord(BV)


def neckline(X):
    """> 0 above the neckline (the neckline dips in front)"""
    zf = (X[:, 2] - Z0) / (0.15)
    t = np.clip((zf + 1) / 2, 0, 1)
    return X[:, 1] - (NECK_B + (NECK_F - NECK_B) * t ** 1.5)


# --- the sweater: trunk + arms down to the wrist
sleeve_end = 1.93
f_sw = np.maximum.reduce([HEM - Y, neckline(BV), np.where(armw + handw > 0.3, at - sleeve_end, -1), legw - 0.5,
                          handw - 0.6])
v, t, a, on = cut(BV, BT, f_sw, np.c_[BD, at, armw, BV])
D_sw = a[:, :NJ]; at_s = a[:, NJ]; aw_s = a[:, NJ + 1]; rest_s = a[:, NJ + 2:]
sv = v.copy()
# the drawing's shoulders are high and round (the barrel closes up to the neck at 0.56 head): the trunk's top is lifted
SH0 = 0.66
lift = (sv[:, 1] > SH0) & (aw_s < 0.5)
kx = 1 + 0.45 * np.clip((np.abs(sv[:, 0]) - 0.035) / 0.05, 0, 1)        # the shoulders, not round the neck
sv[lift, 1] = SH0 + (sv[lift, 1] - SH0) * kx[lift]
# trunk part → the barrel (radially from the trunk's axis, at every height)
A_, FR_, BK_ = torso_at(sv[:, 1])
cz = (FR_ + BK_) / 2; hz = (FR_ - BK_) / 2
ang = np.arctan2(sv[:, 0] / np.maximum(A_, 1e-4), (sv[:, 2] - cz) / np.maximum(hz, 1e-4))
tor = np.c_[A_ * np.sin(ang), sv[:, 1], cz + hz * np.cos(ang)]
# arm part → round its bone at the sleeve's radius (0.09 head at the shoulder, 0.08 at the wrist)
_, bp = arm_coord(sv)
d = sv - bp; dl = np.linalg.norm(d, axis=1, keepdims=True)
rs = (0.095 - 0.012 * np.clip(at_s / 2, 0, 1)) * HH
slv = bp + d / np.maximum(dl, 1e-6) * rs[:, None]
wa = np.clip((aw_s - 0.25) / 0.5, 0, 1)
# near the shoulder the sleeve rises out of the barrel
wa = wa * np.clip(at_s / 0.35, 0, 1) ** 0.7 + (1 - np.clip(at_s / 0.35, 0, 1) ** 0.7) * wa * 0.0
sv = tor * (1 - wa[:, None]) + slv * wa[:, None]
sv = smooth(sv, t, it=6, lam=0.4, fixed=np.where(on)[0])
# knit coordinates: across the ribs (metres round the barrel or the sleeve) and the stripes' coordinate
u_t = ang * 0.15
u_a = np.zeros(len(sv))
for s, pre in ((1, 'Left'), (-1, 'Right')):
    m = sv[:, 0] * s >= 0
    ax_ = BJ[IX[pre + 'ForeArm']] - BJ[IX[pre + 'Arm']]; ax_ /= np.linalg.norm(ax_)
    e1 = np.cross(ax_, [0, 0, 1.0]); e1 /= np.linalg.norm(e1); e2 = np.cross(ax_, e1)
    dd = rest_s[m] - BJ[IX[pre + 'Arm']]
    u_a[m] = np.arctan2(dd @ e2, dd @ e1) * 0.03
uv_sw = np.c_[np.where(wa > 0.5, u_a, u_t), np.where(wa > 0.5, at_s * 0.17, sv[:, 1])]
# the stripes' coordinate: metres down from the first cream band's top (the drawing's stripes(0.62, …, 0.09) on the
# body, (0.8, …) on the arms)
stripe = np.where(wa > 0.5, at_s * 0.18 - 0.027, (FEET - 0.62) * HH - sv[:, 1])
sj, sw = top4(D_sw)
piece('sweater', 'sweater', sv, t, sj, sw, uv=uv_sw, pat=np.c_[np.zeros(len(sv)), stripe, np.zeros(len(sv))], subdiv=1)
SW_V, SW_T, SW_D, SW_ON = sv, t, D_sw, on

# ribbed bands at the sweater's open edges: the neckline, the hem, the cuffs (each edge loop, rolled outward)
def band(loop, V, Dl, out_dir, width, thick, name, along):
    L = V[loop]; m = len(loop)
    rows = []
    nrm = out_dir(L)
    for k in range(5):
        th_ = math.pi * k / 4
        rows.append(L + nrm * thick * math.sin(th_) + along(L) * width * (0.5 - 0.5 * math.cos(th_)))
    BVb = np.concatenate(rows)
    Tb = []
    for i in range(4):
        for j in range(m):
            p, q = i * m + j, i * m + (j + 1) % m
            Tb += [(p, q, p + m), (q, q + m, p + m)]
    Db = np.tile(Dl[loop], (5, 1))
    sjb, swb = top4(Db)
    per = np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.r_[L, L[:1]], axis=0), axis=1))][:m]
    uvb = np.c_[np.tile(per, 5), np.repeat(np.arange(5) * width / 4, m)]
    piece(name, 'cuff', BVb, np.array(Tb), sjb, swb, uv=uvb)


loops = boundary_loops(SW_T)
for L in loops:
    c = SW_V[L].mean(0)
    if c[1] > NECK_B - 0.08 and abs(c[0]) < 0.05:          # the neckline
        cc = c.copy()
        band(L, SW_V, SW_D, lambda X: np.c_[(X - cc)[:, 0], np.zeros(len(X)), (X - cc)[:, 2]] / np.maximum(np.linalg.norm((X - cc)[:, [0, 2]], axis=1, keepdims=True), 1e-6),
             0.016, 0.006, 'neckband', lambda X: np.tile([0, -1.0, 0], (len(X), 1)))
    elif c[1] < HEM + 0.03 and abs(c[0]) < 0.05:          # the hem
        cc = c.copy()
        band(L, SW_V, SW_D, lambda X: np.c_[(X - cc)[:, 0], np.zeros(len(X)), (X - cc)[:, 2]] / np.maximum(np.linalg.norm((X - cc)[:, [0, 2]], axis=1, keepdims=True), 1e-6),
             0.022, 0.005, 'hem', lambda X: np.tile([0, 1.0, 0], (len(X), 1)))
    else:                                                  # a cuff
        cc = c.copy(); pre = 'Left' if c[0] > 0 else 'Right'
        axh = BJ[IX[pre + 'Hand']] - BJ[IX[pre + 'ForeArm']]; axh /= np.linalg.norm(axh)
        def od(X, cc=cc, axh=axh):
            d = X - cc; d -= (d @ axh)[:, None] * axh; return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
        band(L, SW_V, SW_D, od, 0.02, 0.004, 'cuff' + pre[0], lambda X, axh=axh: np.tile(-axh, (len(X), 1)))

# --- the shorts: hips and thighs from inside the sweater down to the drawing's hem (y 2.0 head + r)
SH_TOP, SH_HEM = HEM + 0.05, (FEET - 2.02) * HH
f_sh = np.maximum.reduce([Y - SH_TOP, SH_HEM - Y, armw + handw - 0.3])
v, t, a, on = cut(BV, BT, f_sh, np.c_[BD, legw, BV])
D_sh = a[:, :NJ]; lw_ = a[:, NJ]
sv = v.copy()
for s, pre in ((1, 'Left'), (-1, 'Right')):
    m = sv[:, 0] * s > 0
    tt, bp = bone_t(sv[m], pre + 'Leg', pre + 'Shin')
    d = sv[m] - bp; dl = np.linalg.norm(d, axis=1, keepdims=True)
    r = (0.15 - 0.01 * np.clip(tt / 0.6, 0, 1)) * HH
    leg = bp + d / np.maximum(dl, 1e-6) * r[:, None]
    # the seat: above the crotch, out round the hips (the barrel's bottom a little smaller)
    A_, FR_, BK_ = torso_at(sv[m, 1])
    cz = (FR_ + BK_) / 2; hz = (FR_ - BK_) / 2 * 0.86
    ang = np.arctan2(sv[m, 0] / (A_ * 0.9), (sv[m, 2] - cz) / hz)
    hip = np.c_[A_ * 0.9 * np.sin(ang), sv[m, 1], cz + hz * np.cos(ang)]
    wl = np.clip((lw_[m] - 0.2) / 0.6, 0, 1)
    sv[m] = hip * (1 - wl[:, None]) + leg * wl[:, None]
sv = smooth(sv, t, it=8, lam=0.4, fixed=np.where(on & (v[:, 1] < SH_HEM + 0.01))[0])
sj, sw = top4(D_sh)
piece('shorts', 'shorts', sv, t, sj, sw, subdiv=1)
for L in boundary_loops(t):
    c = sv[L].mean(0)
    if c[1] < SH_HEM + 0.02:
        cc = c.copy()
        band(L, sv, D_sh, lambda X: np.c_[(X - cc)[:, 0], np.zeros(len(X)), (X - cc)[:, 2]] / np.maximum(np.linalg.norm((X - cc)[:, [0, 2]], axis=1, keepdims=True), 1e-6),
             0.012, 0.004, 'shorthem' + ('L' if c[0] > 0 else 'R'), lambda X: np.tile([0, 1.0, 0], (len(X), 1)))
PIECES[-1]['mat'] = 'shorts'; PIECES[-2]['mat'] = 'shorts'

# --- skin: the hands; the legs between the shorts and the socks; the socks
SOCK_TOP = (FEET - 2.5) * HH
SHOE_TOP = 0.045
f_skin = np.minimum(np.where(handw > 0.3, 1.93 - at + 0.02 * 0, 1.0) * 0 + np.where(handw + armw > 0.3, sleeve_end - 0.04 - at, 1.0),
                    np.where(legw > 0.4, Y - (SH_HEM + 0.015), 1.0))
f_skin = np.where(Y < SOCK_TOP, 1.0, f_skin)
v, t, a, on = cut(BV, BT, f_skin, np.c_[BD, handw])
sj, sw = top4(a[:, :NJ])
piece('skin', 'skin', v, t, sj, sw, uv=np.full((len(v), 2), 0.5), tint=np.clip(a[:, NJ], 0, 1) * 0.5)
# socks: the shins from the sock top to the ankle, a little out from the skin
f_so = np.maximum.reduce([Y - SOCK_TOP, SHOE_TOP - 0.01 - Y, 0.4 - legw])
v, t, a, on = cut(BV, BT, f_so, np.c_[BD, BN])
nrm = a[:, NJ:NJ + 3]; nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
v = v + nrm * 0.0025
uvs = np.zeros((len(v), 2))
for s, pre in ((1, 'Left'), (-1, 'Right')):
    m = v[:, 0] * s > 0
    c = BJ[IX[pre + 'Shin']]
    uvs[m, 0] = np.arctan2(v[m, 0] - c[0], v[m, 2] - c[2]) * 0.024
uvs[:, 1] = v[:, 1]
sj, sw = top4(a[:, :NJ])
piece('socks', 'sock', v, t, sj, sw, uv=uvs)


# --- shoes: a rounded shoe lofted along each foot (the drawing's: length 0.34 head, height 0.11, a pale sole)
def shoe(pre):
    F_, T_ = BJ[IX[pre + 'Foot']], BJ[IX[pre + 'ToeEnd']]
    ax = np.array([T_[0] - F_[0], 0, T_[2] - F_[2]]); L = np.linalg.norm(ax); ax /= L
    Ltot = 0.34 * HH * 1.05
    heel = np.array([F_[0], 0, F_[2]]) - ax * 0.2 * Ltot
    sd = np.cross([0, 1.0, 0], ax)
    nu, nv = 30, 28; X = []; uvx = []
    for i in range(nu):
        t = i / (nu - 1)
        c = heel + ax * Ltot * t
        w = (0.05 * HH / 0.1 * 0.1) * (0.82 + 0.25 * np.sin(np.pi * min(t / 0.8, 1) / 2))
        w = 0.1 * HH * (0.8 + 0.25 * np.sin(np.pi * min(t / 0.8, 1) / 2))
        hgt = 0.11 * HH * np.interp(t, [0, 0.25, 0.5, 0.8, 1], [1.05, 1.08, 0.86, 0.7, 0.55])
        cap = np.clip(np.sin(np.pi * t) ** 0.3, 0.04, 1)
        for j in range(nv):
            q = 2 * np.pi * j / nv
            sx, sy = np.cos(q), np.sin(q)
            r = (abs(sx) ** 2.4 + abs(sy) ** 2.4) ** (-1 / 2.4)
            px, py = sx * r * w * cap, (sy * r * 0.5 + 0.5) * hgt * (0.3 + 0.7 * cap)
            X.append(c + sd * px + np.array([0, max(py, 0.0), 0])); uvx.append((q, t))
    X = np.array(X); Fc = []
    for i in range(nu - 1):
        for j in range(nv):
            a_, b_ = i * nv + j, i * nv + (j + 1) % nv
            Fc += [(a_, b_, a_ + nv), (b_, b_ + nv, a_ + nv)]
    for end, rev in ((0, True), (nu - 1, False)):
        ci = len(X); X = np.r_[X, X[end * nv:(end + 1) * nv].mean(0)[None]]; uvx.append((0, end / (nu - 1)))
        for j in range(nv):
            tri = (end * nv + j, end * nv + (j + 1) % nv, ci)
            Fc.append(tri[::-1] if rev else tri)
    tt = ((X - heel) @ ax) / Ltot
    Dd = np.zeros((len(X), NJ)); wt = np.clip((tt - 0.55) / 0.2, 0, 1)
    Dd[:, IX[pre + 'Foot']] = 1 - wt; Dd[:, IX[pre + 'ToeBase']] = wt
    return X, np.array(Fc), Dd


for pre in ('Left', 'Right'):
    X, Fc, Dd = shoe(pre)
    sole = 0.012
    for nm, g in (('shoe', X[:, 1] - sole), ('sole', sole - X[:, 1])):
        v, t, a, _ = cut(X, Fc, -g, Dd)
        sj, sw = top4(a)
        piece(nm + pre[0], nm, v, t, sj, sw)

# ======================================================================================== write
def write():
    th, _ = pack.read(os.path.join(ENGINE, 'data/topology/anny-moood.json'))
    _, bod = pack.read(os.path.join(ENGINE, 'data/bodies/moood-child.json'))
    Vs, Ts, SJ, SW, info = [], [], [], [], []
    n = 0
    for p in PIECES:
        Vs.append(p['V']); Ts.append(p['T'] + n); SJ.append(p['sj']); SW.append(p['sw'] / p['sw'].sum(1, keepdims=True))
        info.append(dict(name=p['name'], mat=p['mat'], start=n, count=len(p['V']), subdiv=p['subdiv']))
        n += len(p['V'])
    Vall = np.vstack(Vs).astype(np.float32); T = np.vstack(Ts)
    sj = np.vstack(SJ); sw = np.vstack(SW)
    parts = np.zeros((len(Vall), len(th['parts'])), np.uint8)
    hw = sum(np.where(np.isin(sj[:, k], [IX['Head'], IX['HeadEnd'], IX['Jaw'], IX['LeftEye'], IX['RightEye']]), sw[:, k], 0) for k in range(4))
    parts[:, th['parts'].index('head')] = np.round(hw * 255)
    out = os.path.join(CACHE, 'engine/data')
    os.makedirs(out + '/bodies', exist_ok=True); os.makedirs(out + '/topology', exist_ok=True)
    pack.write(out + '/topology/savely8.json',
               dict(format='engine/topology', version=1, id='savely8', about='Тим (С8): every piece in one mesh',
                    source='to3d/r27-s8-savely', skeleton='soma77', vertices=len(Vall), triangles=len(T), parts=th['parts']),
               dict(triangles=T.astype(np.uint32), skinJoints=sj.astype(np.uint8), skinWeights=sw.astype(np.float32), parts=parts))
    pack.write(out + '/bodies/savely8.json',
               dict(format='engine/body', version=1, id='savely8', label=dict(ru='Тим', en='Tim'),
                    source='to3d/r27-s8-savely: Anny (moood-child) fitted to the С8 drawing, HBM stylised head',
                    topology='savely8', skeleton='soma77'),
               dict(positions=Vall, joints=J.astype(np.float32), frames=np.asarray(bod['frames'], np.float32)))
    np.savez(f'{CACHE}/rest.npz', uv=np.vstack([p['uv'] for p in PIECES]).astype(np.float32),
             pat=np.vstack([p['pat'] for p in PIECES]).astype(np.float32),
             tint=np.concatenate([p['tint'] for p in PIECES]).astype(np.float32))
    json.dump(dict(pieces=info, HH=HH, O=O.tolist(), tex=os.path.join(FOLDER, 'tools/web/tex')),
              open(f'{CACHE}/model.json', 'w'), indent=1)
    print('savely8', len(Vall), 'vertices', len(T), 'triangles;', ', '.join(f"{p['name']}:{p['count']}" for p in info))


write()


def write_face():
    """the face rig for face.mjs: every replacement piece's shapes (world rest positions), the lids' weights over the
    head's vertices and each eye's centre and axes, the lash and eyeballs' vertex ranges, the expressions' numbers"""
    info = {p['name']: (sum(q['V'].shape[0] for q in PIECES[:i]), len(p['V'])) for i, p in enumerate(PIECES)}
    fj = json.load(open(f'{CACHE}/face.json'))
    arrays = {}
    shapes = {}
    for part in ('lipU', 'lipL', 'cav', 'teethU', 'teethL'):
        keys = fj['faces'] + ['v' + v for v in fj['visemes']]
        shapes[part] = keys
        for k in keys: arrays[f'{part}.{k}'] = W(F[f'{part}_{k}']).astype(np.float32)
    shapes['brows'] = fj['faces']
    for k in fj['faces']: arrays[f'brows.{k}'] = W(F['brow_' + k]).astype(np.float32)
    arrays['lash.w'] = F['lash_w'].astype(np.float32)
    lids = {}
    h0 = info['head'][0]
    for k in ('L', 'R'):
        wU, wL = F[f'lid{k}_wU'], F[f'lid{k}_wL']
        idx = np.where((wU > 1e-3) | (wL > 1e-3))[0]
        arrays[f'lid{k}.idx'] = (idx + h0).astype(np.uint32)
        arrays[f'lid{k}.wU'] = wU[idx].astype(np.float32); arrays[f'lid{k}.wL'] = wL[idx].astype(np.float32)
        c = W(F[f'lid{k}_c'])
        lids[k] = dict(c=c.tolist(), n=F[f'lid{k}_n'].tolist(), up=F[f'lid{k}_up'].tolist(), ax=F[f'lid{k}_ax'].tolist())
    from fit_head import R_EYE, LID_R
    R = TP['eye_r']; op = TP['eye_open']
    eU0 = math.asin(min(1, R * TP['lid_top'] * op / (R_EYE * LID_R)))
    eL0 = -math.asin(min(1, R * TP['lid_bot'] * op / (R_EYE * LID_R)))
    hdr = dict(format='savely8/face', version=1, pieces={k: list(v) for k, v in info.items()}, shapes=shapes, lids=lids,
               eU0=eU0, eL0=eL0, expr=fj['expr'], faces=fj['faces'], visemes=fj['visemes'],
               eyes={'L': W(drawing.eye_centre(1)).tolist(), 'R': W(drawing.eye_centre(-1)).tolist()})
    pack.write(f'{CACHE}/engine/face.json', hdr, arrays)
    print('face rig', len(arrays), 'arrays')


write_face()


def write_viewer_data():
    """the viewer's copy, in the folder (data/): the body and its topology, the face rig, the paint coordinates and
    which piece is which (look.json)"""
    import shutil
    D = os.path.join(FOLDER, 'data')
    os.makedirs(D, exist_ok=True)
    for sub, name, to in (('engine/data/bodies', 'savely8', 'bodies'), ('engine/data/topology', 'savely8', 'topology'), ('engine', 'face', '')):
        os.makedirs(os.path.join(D, to), exist_ok=True)
        for ext in ('json', 'bin'):
            shutil.copy(os.path.join(CACHE, sub, f'{name}.{ext}'), os.path.join(D, to, f'{name}.{ext}'))
    info = [dict(name=p['name'], mat=p['mat']) for p in PIECES]
    pack.write(os.path.join(D, 'look.json'), dict(format='savely8/look', version=1, pieces=info,
               counts=[len(p['V']) for p in PIECES], tris=[len(p['T']) for p in PIECES]),
               dict(uv=np.vstack([p['uv'] for p in PIECES]).astype(np.float32),
                    pat=np.vstack([p['pat'] for p in PIECES]).astype(np.float32),
                    tint=np.concatenate([p['tint'] for p in PIECES]).astype(np.float32)))
    print('viewer data in', D)


write_viewer_data()
