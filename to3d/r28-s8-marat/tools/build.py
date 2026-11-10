"""Марат assembled: Anny's fitted man (fit_body.py), the fitted base head (fit_head.py) with its glass eyes, the
replacement face pieces (face.py: the mouth with teeth and tongue, the brows, the moustache's curls), the curls and the
beard (fit_hair.py), the drawing's short thick neck, and the clothes — every piece skinned on SOMA's 77 joints — written
as an engine body on its own topology (engine/README.md: Formats), plus what the renderer and the viewer need.

Clothes, from the drawing's numbers (marat.MARAT_FIG / MARAT_BODY of styles/s8-stopmotion):
- the cook's jacket: the drawing's own torso loft (a barrel) as a clean grid, its weights from Anny's trunk carried out
  onto the same loft (trunk joints only); the sleeves = Anny's upper arms carried round their bones to the sleeve's
  radius, ending at the elbow in a roll; the forearms and hands are skin;
- the apron: the bib cut from the same loft a little out (the drawing's BIB outline), two straps to the neck, a tie
  round the waist, and below it the drawing's apron loft hanging in front of the legs (hips' and thighs' weights);
- the towel over his left shoulder, with its two woven stripes; the trousers = Anny's legs carried round the leg bones;
  the shoes lofted round the feet.
Writes CACHE/engine/data/{bodies,topology}/marat8.* and CACHE/model.json (pieces, materials) + CACHE/rest.npz."""
import json, math, os
import numpy as np, igl
import base, drawing
import fit_body as body
from drawing import P as TP
import cast
from head import interp
from head import Head
from scipy.spatial import cKDTree
from common import CACHE, HH, FEET, HEAD_Y, IX, NAMES, PARENT, vertex_normals, pack, ENGINE, FOLDER, BID

NJ = len(NAMES)
Z0 = 0.03                    # the head's centre (and the drawing's z = 0) in the engine's z
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
SKIN_UV = (0.5, 0.97)             # a plain patch of the skin's picture (the crown), for the neck and the hands

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


def sphere(c, r, n=40, squash=(1, 1, 1)):
    th = np.linspace(0, np.pi, n); ph = np.linspace(0, 2 * np.pi, 2 * n, endpoint=False)
    Pp = np.array([[np.sin(t) * np.cos(p), np.sin(t) * np.sin(p), np.cos(t)] for t in th for p in ph])
    m = 2 * n; T = []
    for i in range(n - 1):
        for j in range(m):
            a, b = i * m + j, i * m + (j + 1) % m; T += [(a, b, a + m), (b, b + m, a + m)]
    return c + Pp * r * np.array(squash), np.array(T), np.c_[Pp[:, 0] * 0.5 + 0.5, Pp[:, 1] * 0.5 + 0.5]


for s, nm in ((1, 'eyeL'), (-1, 'eyeR')):
    V, T, uv = sphere(drawing.eye_centre(s), drawing.EYE_R, n=26)
    sj, sw = one(len(V), 'Head')
    piece(nm, 'eye', W(V), T, sj, sw, uv=uv)

# the replacement pieces, at the calm face (face.mjs mixes their shapes)
F = np.load(f'{CACHE}/face.npz')
MOUTH = ['lipU', 'lipL', 'cav', 'teethU', 'teethL', 'moust']        # the pieces that go with the mouth's shapes
MOUTH = ['lipU', 'lipL', 'cav', 'tongue', 'teethU', 'teethL', 'moust']        # the pieces that go with the mouth's shapes
for part, mat in (('lipU', 'lip'), ('lipL', 'lip'), ('cav', 'mouth'), ('tongue', 'tongue'), ('teethU', 'teeth'), ('teethL', 'teeth')):
    V = F[f'{part}_calm']; sj, sw = one(len(V), 'Head')
    piece(part, mat, W(V), F[part + '_T'], sj, sw)
V = F['moust_calm']; sj, sw = one(len(V), 'Head'); piece('moust', 'curl', W(V), F['moust_T'], sj, sw, uv=F['moust_uv'])
V = F['brow_calm']; sj, sw = one(len(V), 'Head'); piece('brows', 'brow', W(V), F['brow_T'], sj, sw, uv=F['brow_uv'], subdiv=1)
V = F['lash_V']; sj, sw = one(len(V), 'Head'); piece('lashes', 'lash', W(V), F['lash_T'], sj, sw)

HR = np.load(f'{CACHE}/hair.npz')
for kind, nm, mat in ((0, 'haircap', 'hairmass'), (1, 'curls', 'curl'), (2, 'beardmass', 'hairmass'), (3, 'beard', 'curl')):
    m = HR['kind'] == kind; idx = np.where(m)[0]; re = -np.ones(len(m), int); re[idx] = np.arange(len(idx))
    T = HR['T'][m[HR['T'][:, 0]]]
    sj, sw = one(len(idx), 'Head'); piece(nm, mat, W(HR['V'][idx]), re[T], sj, sw, uv=HR['uv'][idx])
from common import hu

def resample(p, n):
    """a smooth curve through the points (Catmull-Rom), n points"""
    p = np.asarray(p, float); m = len(p) - 1; out = []
    for u in np.linspace(0, m, n):
        j = min(int(u), m - 1); t = u - j
        p0, p1, p2, p3 = p[max(0, j - 1)], p[j], p[j + 1], p[min(m, j + 2)]
        out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


# ======================================================================================== the neck
N = drawing.BODY['neck']
ys = np.linspace(0.25, 0.78, 24)
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


def neck_weights(X):
    y = X[:, 1]
    yH, y2, y1 = J[IX['Head'], 1], J[IX['Neck2'], 1], J[IX['Neck1'], 1]
    D = np.zeros((len(X), NJ))
    a = np.clip((y - y2) / (yH - y2), 0, 1); b = np.clip((y - y1) / (y2 - y1), 0, 1)
    D[:, IX['Head']] = a; D[:, IX['Neck2']] = (1 - a) * b; D[:, IX['Neck1']] = (1 - a) * (1 - b)
    return D


sj, sw = top4(neck_weights(NV))
piece('neck', 'skin', NV, np.array(NT), sj, sw, uv=np.tile(SKIN_UV, (len(NV), 1)), tint=np.full(len(NV), 0.15))

# ======================================================================================== clothes
FIG = drawing.FIG
TOR = Head({k: v for k, v in FIG['torso'].items() if k != 'x'}, 1.0, 0.0, 0.0, 0.0, 0.0)   # without its lean (a pose)          # the drawing's torso loft (head units, y down from the head)
TY0, TY1 = FIG['torso_y']
yw = lambda yd: (FEET - np.asarray(yd, float)) * HH          # head units down from the head's centre → metres up


def bar(phi, yd, out=0.0):
    """a point of the torso loft (phi round it, 0 = the middle of the front; yd down from the head's centre), pushed
    out along the loft's normal by `out` (head units) → world"""
    p = np.array([TOR.surf(a, b, c) for a, b, c in np.broadcast(phi, yd, out)])
    return Wd(p[:, 0], p[:, 1], p[:, 2])


def front(X, yd, out=0.0):
    """a point on the loft's front at the lateral offset X (head units) — the drawing's body.tx"""
    a = np.array([max(TOR.a(v), 1e-3) for v in np.atleast_1d(yd)])
    return bar(np.arcsin(np.clip(np.asarray(X) / a, -1, 1)), yd, out)


def bone_t(X, a, b):
    A, Bb = BJ[IX[a]], BJ[IX[b]]; d = Bb - A
    t = ((X - A) @ d) / (d @ d)
    return t, A + t[:, None] * d


Y = BV[:, 1]
armw = pw('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm')
handw = pw('Lhand', 'Rhand')
legw = pw('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot')


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


def leg_coord(X):
    """along the leg: 0 at the hip joint, 1 at the knee, 2 at the ankle; and the point on the bone"""
    out_t = np.zeros(len(X)); out_p = np.zeros_like(X)
    for s, pre in ((1, 'Left'), (-1, 'Right')):
        m = (X[:, 0] >= 0) if s > 0 else (X[:, 0] < 0)
        t1, p1 = bone_t(X[m], pre + 'Leg', pre + 'Shin')
        t2, p2 = bone_t(X[m], pre + 'Shin', pre + 'Foot')
        lower = t1 > 1
        out_t[m] = np.where(lower, 1 + np.clip(t2, -1, 3), t1)
        out_p[m] = np.where(lower[:, None], p2, p1)
    return out_t, out_p


at, ap = arm_coord(BV)
lt, lp = leg_coord(BV)

# --- Anny's trunk carried out onto the loft: where the waistcoat's weights come from
trunk = np.where((armw < 0.5) & (handw < 0.3) & (legw < 0.6) & (Y < yw(TY0 - 0.12)))[0]
TRUNK_J = [IX[n] for n in ('Hips', 'Spine1', 'Spine2', 'Chest', 'Neck1', 'LeftShoulder', 'RightShoulder')]
yd_t = np.clip(FEET - BV[trunk, 1] / HH, TY0, TY1)
A_ = np.array([TOR.a(v) for v in yd_t]) * HH
Bz = np.array([TOR.b(v) for v in yd_t]) * HH; Cz = np.array([TOR.c(v) for v in yd_t]) * HH + Z0
ang_t = np.arctan2(BV[trunk, 0] / np.maximum(A_, 1e-4), (BV[trunk, 2] - Cz) / np.maximum(Bz, 1e-4))
TRV = np.c_[A_ * np.sin(ang_t), BV[trunk, 1], Cz + Bz * np.cos(ang_t)]
TRD = np.zeros((len(trunk), NJ)); TRD[:, TRUNK_J] = BD[trunk][:, TRUNK_J]
# what the arms and legs held goes to the chest and the hips: the waistcoat is stiff
TRD[:, IX['Chest']] += BD[trunk][:, [IX[n] for n in NAMES if 'Arm' in n or 'Hand' in n]].sum(1)
TRD[:, IX['Hips']] += BD[trunk][:, [IX[n] for n in NAMES if any(k in n for k in ('Leg', 'Shin', 'Foot', 'Toe'))]].sum(1)
TRD[:, IX['Neck1']] += BD[trunk][:, [IX['Neck2'], IX['Head']]].sum(1)
TRD[TRD.sum(1) < 1e-6, IX['Chest']] = 1.0
TRD /= TRD.sum(1, keepdims=True)
_tree = cKDTree(TRV)


def trunk_weights(X, k=8):
    """weights for points near the loft: a smooth mean of the nearest trunk vertices' (carried onto the loft)"""
    d, i = _tree.query(X, k=k)
    w = 1 / (d + 0.004) ** 2; w /= w.sum(1, keepdims=True)
    D = (TRD[i] * w[..., None]).sum(1)
    return D / D.sum(1, keepdims=True)


def grid(nphi, yds, out=0.0, phi0=-math.pi, phi1=math.pi, closed=True):
    """the loft as a grid: rows by heights yds, columns round it"""
    ph = np.linspace(phi0, phi1, nphi, endpoint=not closed)
    PH, YD = np.meshgrid(ph, yds)
    V = bar(PH.ravel(), YD.ravel(), out)
    T = []
    for i in range(len(yds) - 1):
        for j in range(nphi if closed else nphi - 1):
            a, b = i * nphi + j, i * nphi + (j + 1) % nphi
            T += [(a, a + nphi, b), (b, a + nphi, b + nphi)]
    return V, np.array(T), PH.ravel(), YD.ravel()


def poly_sd(X, Yd, poly):
    """signed distance (head units; negative inside) from points (X, Yd) to a polygon"""
    P_ = np.c_[X, Yd]; poly = np.asarray(poly, float); n = len(poly)
    d = np.full(len(P_), 1e9); inside = np.zeros(len(P_), bool)
    for k in range(n):
        a, b = poly[k], poly[(k + 1) % n]
        e = b - a; t = np.clip(((P_ - a) @ e) / (e @ e), 0, 1)
        d = np.minimum(d, np.linalg.norm(P_ - (a + t[:, None] * e), axis=1))
        cond = (a[1] > P_[:, 1]) != (b[1] > P_[:, 1])
        xs = a[0] + (P_[:, 1] - a[1]) / (b[1] - a[1] + 1e-12) * (b[0] - a[0])
        inside ^= cond & (P_[:, 0] < xs)
    return np.where(inside, -d, d)


def wall(V, T, D, loop, depth, uv=None):
    """a wall along an open edge: the edge's vertices again, moved in along the surface's normals by depth (metres)"""
    Nn = vertex_normals(V, T)
    m = len(loop); n0 = len(V)
    V2 = np.r_[V, V[loop] - Nn[loop] * depth]
    ids = np.arange(n0, n0 + m)
    T2 = np.r_[T, np.stack([loop, np.roll(loop, -1), ids], 1), np.stack([np.roll(loop, -1), np.roll(ids, -1), ids], 1)]
    return V2, T2, np.r_[D, D[loop]], (None if uv is None else np.r_[uv, uv[loop]])


JACKET_OUT, APRON_OUT = 0.0, 0.016                 # the cloth against the loft (head units)
yds = TY0 + (TY1 - TY0) * np.linspace(0, 1, 90) ** 1.2
gv, gt, gph, gyd = grid(144, yds, JACKET_OUT)
# the loft's bottom closed (its table narrows to 0.4 head at 2.5)
c0 = len(gv); gv = np.r_[gv, gv[-144:].mean(0)[None]]
gt = np.r_[gt, [(c0, c0 - 144 + (j + 1) % 144, c0 - 144 + j) for j in range(144)]]
sj, sw = top4(trunk_weights(gv))
piece('jacket', 'jacket', gv, gt, sj, sw)

# the apron's bib on the chest and belly (marat.BIB), a little out from the jacket, with an edge
import marat as M
av, at_, aph, ayd = grid(200, TY0 + (TY1 - TY0) * np.linspace(0, 1, 110), APRON_OUT)
aX = np.array([TOR.a(v) for v in ayd]) * np.sin(aph)
sdB = np.where(np.cos(aph) > 0, poly_sd(aX, ayd, M.BIB), 1.0)
v, t, a, on = cut(av, at_, sdB)
AD = trunk_weights(v)
for L in boundary_loops(t):
    v, t, AD, a = wall(v, t, AD, L, APRON_OUT * HH * 1.1)
sj, sw = top4(AD); piece('bib', 'apron', v, t, sj, sw)
def patch(corners, out, n=8, bulge=0.004):
    """a small bilinear patch on the loft's front through four (X, yd) corners, standing `out` off it"""
    c = np.asarray(corners, float); u = np.linspace(0, 1, n)
    U, Vv = np.meshgrid(u, u)
    Pq = ((1 - U)[..., None] * (1 - Vv)[..., None] * c[0] + U[..., None] * (1 - Vv)[..., None] * c[1]
          + U[..., None] * Vv[..., None] * c[2] + (1 - U)[..., None] * Vv[..., None] * c[3]).reshape(-1, 2)
    o = out + bulge * (np.sin(np.pi * U) * np.sin(np.pi * Vv)).ravel() ** 0.5
    V = front(Pq[:, 0], Pq[:, 1], o)
    T = []
    for i in range(n - 1):
        for j in range(n - 1):
            a, b = i * n + j, i * n + j + 1; T += [(a, a + n, b), (b, a + n, b + n)]
    T = np.array(T)
    return V, orient_out(V, T)


def orient_out(V, T):
    """triangles turned to face away from the body's axis"""
    nrm = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]).sum(0)
    c = V.mean(0) - np.array([0, V[:, 1].mean(), Z0])
    return T if nrm @ c > 0 else T[:, ::-1]


# the collar's points (cast.savely_details) and the tie (cast.savely_inside)

for side in (-1, 1):
    V, T = patch([(side * 0.19, 0.56), (side * 0.27, 0.56), (side * 0.3, 1.04), (side * 0.22, 1.04)], APRON_OUT * 0.9, n=10, bulge=0.004)
    sj, sw = top4(trunk_weights(V)); piece('strap' + 'RL'[side > 0], 'apron', V, T, sj, sw)
# the bib's top hem and the tie round the waist: rolls of the apron's cloth
tt = np.linspace(-1, 1, 24)
hem = front(0.3 * tt, np.full(24, 1.03), APRON_OUT + 0.006)
V, T, _ = tube_along(hem, np.full(24, 0.014 * HH), n=8); sj, sw = top4(trunk_weights(V)); piece('bibhem', 'apron', V, T, sj, sw)
ph = np.linspace(-math.pi, math.pi, 97)
tie = bar(ph, 2.31 + 0.015 * np.cos(ph), APRON_OUT + 0.008)
V, T, _ = tube_along(tie, np.full(97, 0.017 * HH), n=8); sj, sw = top4(trunk_weights(V)); piece('aprontie', 'aprontie', V, T, sj, sw)

# the apron below the waist: the drawing's own loft hanging in front of the legs (marat.MARAT_FIG['skirts'])
SK = FIG['skirts'][0]
SKL = Head({k: v for k, v in SK['table'].items() if k != 'x'}, 1.0, 0.0, 0.0, 0.0, 0.0)
sy = np.linspace(SK['y'][0], SK['y'][1], 40); sp = np.linspace(-math.pi, math.pi, 96, endpoint=False)
SV = np.array([SKL.surf(p, y) for y in sy for p in sp]); SV = Wd(SV[:, 0], SV[:, 1], SV[:, 2])
ST = []
for i in range(len(sy) - 1):
    for j in range(96):
        a_, b_ = i * 96 + j, i * 96 + (j + 1) % 96; ST += [(a_, a_ + 96, b_), (b_, a_ + 96, b_ + 96)]
c0 = len(SV); SV = np.r_[SV, SV[-96:].mean(0)[None]]; ST += [(c0, c0 - 96 + (j + 1) % 96, c0 - 96 + j) for j in range(96)]
# it hangs from the hips; lower down each side goes a little with its thigh, so a step pushes it forward
down = np.clip((SV[:, 1] - yw(SK['y'][0])) / (yw(SK['y'][1]) - yw(SK['y'][0])), 0, 1)
sidew = np.clip(SV[:, 0] / (0.3 * HH), -1, 1)
Dk = np.zeros((len(SV), NJ)); wl = 0.55 * down ** 1.3
Dk[:, IX['LeftLeg']] = wl * (0.5 + 0.5 * sidew); Dk[:, IX['RightLeg']] = wl * (0.5 - 0.5 * sidew); Dk[:, IX['Hips']] = 1 - wl
sj, sw = top4(Dk); piece('apron', 'apron', SV, np.array(ST), sj, sw, pat=np.c_[np.tile(sp, len(sy)).tolist() + [0.0], SV[:, 1], np.zeros(len(SV))])

# the towel over his left shoulder: from the back over the top down the chest (marat_details), two woven stripes near its end
x0, x1, yend = 0.43, 0.62, 1.42
def over(X):
    return next(y for y in np.arange(0.5, 1.5, 0.004) if TOR.a(y) >= X * 1.04)
rows = []
for u in np.linspace(0, 1, 9):
    X = x0 + (x1 - x0) * u; yt = over(X)
    yb = np.linspace(1.05, yt, 10)[:-1]; yf = np.linspace(yt, yend + 0.012 * math.sin(7 * u), 26)
    back = bar(math.pi - np.arcsin(np.clip(X / np.array([TOR.a(y) for y in yb]), -1, 1)), yb, 0.022)
    frt = bar(np.arcsin(np.clip(X / np.array([TOR.a(y) for y in yf]), -1, 1)), yf, 0.02 + 0.008 * np.sin(np.linspace(0, 3, 26) + 2 * u))
    rows.append((np.r_[back, frt], np.r_[-(yt - yb) - 1, yf]))
TV = np.array([r[0] for r in rows]).transpose(1, 0, 2).reshape(-1, 3)
Tyd = np.array([r[1] for r in rows]).T.ravel()
TT = []
nrow = len(rows[0][0])
for i in range(nrow - 1):
    for j in range(8):
        a_, b_ = i * 9 + j, i * 9 + j + 1; TT += [(a_, a_ + 9, b_), (b_, a_ + 9, b_ + 9)]
TT = np.array(TT)
nrm = np.cross(TV[TT[:, 1]] - TV[TT[:, 0]], TV[TT[:, 2]] - TV[TT[:, 0]]).sum(0)
if nrm[2] < 0: TT = TT[:, ::-1]
sj, sw = top4(trunk_weights(TV)); piece('towel', 'towel', TV, TT, sj, sw, pat=np.c_[np.zeros(len(TV)), Tyd, np.zeros(len(TV))], subdiv=1)

# --- the jacket's sleeves: Anny's upper arms carried round their bones to the sleeve's radius (0.2 → 0.175 head), to
# the elbow, where the sleeve is rolled up
sleeve_end = 1.0
f_sl = np.maximum.reduce([np.where(armw + handw > 0.25, at - sleeve_end, 1.0), 0.25 - (armw + handw), 0.0 - at])
v, t, a, on = cut(BV, BT, f_sl, np.c_[BD, at])
D_sl = a[:, :NJ]; at_s = a[:, NJ]
_, bp = arm_coord(v)
d = v - bp; dl = np.linalg.norm(d, axis=1, keepdims=True)
rs = (0.2 - 0.025 * np.clip(at_s, 0, 1)) * HH
sv = bp + d / np.maximum(dl, 1e-6) * rs[:, None]
sv = smooth(sv, t, it=5, lam=0.4, fixed=np.where(on & (at_s > 0.8))[0])
sj, sw = top4(D_sl)
piece('sleeves', 'jacket', sv, t, sj, sw, subdiv=1)
SL_V, SL_T, SL_D = sv, t, D_sl
for pre in ('Left', 'Right'):
    V, T, _ = sphere(BJ[IX[pre + 'Arm']], 0.2 * HH, n=14)
    sj, sw = one(len(V), pre + 'Arm'); piece('shoulder' + pre[0], 'jacket', V, T, sj, sw)

def band(loop, V, Dl, out_dir, width, thick, name, along, mat):
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
    piece(name, mat, BVb, np.array(Tb), sjb, swb)



for L in boundary_loops(SL_T):
    c = SL_V[L].mean(0); pre = 'Left' if c[0] > 0 else 'Right'
    if np.linalg.norm(c - BJ[IX[pre + 'ForeArm']]) > 0.08: continue
    axh = BJ[IX[pre + 'ForeArm']] - BJ[IX[pre + 'Arm']]; axh /= np.linalg.norm(axh)
    def od(X, cc=c, axh=axh):
        d = X - cc; d -= (d @ axh)[:, None] * axh; return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
    band(L, SL_V, SL_D, od, 0.03, 0.007, 'roll' + pre[0], lambda X, axh=axh: np.tile(-axh, (len(X), 1)), 'jacket')

# --- the trousers: Anny's legs carried round the leg bones to the drawing's thick trouser legs (r 0.22 → 0.16 head)
TR_TOP, TR_HEM = yw(2.2), yw(3.66)
f_tr = np.maximum.reduce([Y - TR_TOP, TR_HEM - Y, 0.45 - legw])
v, t, a, on = cut(BV, BT, f_tr, np.c_[BD, lt])
D_tr = a[:, :NJ]; lt_s = a[:, NJ]
_, bp = leg_coord(v)
d = v - bp; d[:, 1] = 0; dl = np.linalg.norm(d, axis=1, keepdims=True)
rt = (0.22 - 0.03 * np.clip(lt_s / 2, 0, 1)) * HH
sv = np.c_[bp[:, 0], v[:, 1], bp[:, 2]] + d / np.maximum(dl, 1e-6) * rt[:, None]
sv = smooth(sv, t, it=6, lam=0.4, fixed=np.where(on & (v[:, 1] < TR_HEM + 0.01))[0])
sj, sw = top4(D_tr)
piece('trousers', 'trousers', sv, t, sj, sw, subdiv=1)
for L in boundary_loops(t):
    c = sv[L].mean(0)
    if c[1] < TR_HEM + 0.02:
        band(L, sv, D_tr, lambda X, cc=c: np.c_[(X - cc)[:, 0], np.zeros(len(X)), (X - cc)[:, 2]] / np.maximum(np.linalg.norm((X - cc)[:, [0, 2]], axis=1, keepdims=True), 1e-6),
             0.012, 0.003, 'trhem' + ('L' if c[0] > 0 else 'R'), lambda X: np.tile([0, 1.0, 0], (len(X), 1)), 'trousers')

# --- skin: the thick forearms from inside the rolled sleeves, and the hands
f_skin = np.where(handw + armw > 0.3, sleeve_end - 0.1 - at, 1.0)
v, t, a, on = cut(BV, BT, f_skin, np.c_[BD, handw])
sj, sw = top4(a[:, :NJ])
piece('skin', 'skin', v, t, sj, sw, uv=np.tile(SKIN_UV, (len(v), 1)), tint=np.clip(a[:, NJ], 0, 1) * 0.5, subdiv=1)


# --- shoes: a rounded shoe lofted along each foot (the drawing's: length 0.5 head, height 0.13, half width 0.15)
SHOE = dict(len=0.5, h=0.13, w=0.15)


def shoe(pre):
    F_, T_ = BJ[IX[pre + 'Foot']], BJ[IX[pre + 'ToeEnd']]
    ax = np.array([T_[0] - F_[0], 0, T_[2] - F_[2]]); L = np.linalg.norm(ax); ax /= L
    Ltot = SHOE['len'] * HH * 1.05
    heel = np.array([F_[0], 0, F_[2]]) - ax * 0.22 * Ltot
    sd = np.cross([0, 1.0, 0], ax)
    nu, nv = 30, 28; X = []
    for i in range(nu):
        t = i / (nu - 1)
        c = heel + ax * Ltot * t
        w = SHOE['w'] * HH * (0.8 + 0.25 * np.sin(np.pi * min(t / 0.8, 1) / 2))
        hgt = SHOE['h'] * HH * np.interp(t, [0, 0.25, 0.5, 0.8, 1], [1.05, 1.08, 0.86, 0.7, 0.55])
        cap = np.clip(np.sin(np.pi * t) ** 0.3, 0.04, 1)
        for j in range(nv):
            q = 2 * np.pi * j / nv
            sx, sy = np.cos(q), np.sin(q)
            r = (abs(sx) ** 2.4 + abs(sy) ** 2.4) ** (-1 / 2.4)
            px, py = sx * r * w * cap, (sy * r * 0.5 + 0.5) * hgt * (0.3 + 0.7 * cap)
            X.append(c + sd * px + np.array([0, max(py, 0.0), 0]))
    X = np.array(X); Fc = []
    for i in range(nu - 1):
        for j in range(nv):
            a_, b_ = i * nv + j, i * nv + (j + 1) % nv
            Fc += [(a_, b_, a_ + nv), (b_, b_ + nv, a_ + nv)]
    for end, rev in ((0, True), (nu - 1, False)):
        ci = len(X); X = np.r_[X, X[end * nv:(end + 1) * nv].mean(0)[None]]
        for j in range(nv):
            tri = (end * nv + j, end * nv + (j + 1) % nv, ci)
            Fc.append(tri[::-1] if rev else tri)
    tt = ((X - heel) @ ax) / Ltot
    Dd = np.zeros((len(X), NJ)); wt = np.clip((tt - 0.55) / 0.2, 0, 1)
    Dd[:, IX[pre + 'Foot']] = 1 - wt; Dd[:, IX[pre + 'ToeBase']] = wt
    return X, np.array(Fc), Dd


for pre in ('Left', 'Right'):
    X, Fc, Dd = shoe(pre)
    sole = 0.011
    for nm, g in (('shoe', X[:, 1] - sole), ('sole', sole - X[:, 1])):
        v, t, a, _ = cut(X, Fc, -g, Dd)
        sj, sw = top4(a)
        piece(nm + pre[0], nm, v, t, sj, sw)

# ======================================================================================== write
def write():
    th, _ = pack.read(os.path.join(ENGINE, 'data/topology/anny-moood.json'))
    _, bod = pack.read(os.path.join(ENGINE, f'data/bodies/{body.BASE}.json'))
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
    pack.write(out + '/topology/marat8.json',
               dict(format='engine/topology', version=1, id='marat8', about='Марат (С8): every piece in one mesh',
                    source='to3d/r28-s8-marat', skeleton='soma77', vertices=len(Vall), triangles=len(T), parts=th['parts']),
               dict(triangles=T.astype(np.uint32), skinJoints=sj.astype(np.uint8), skinWeights=sw.astype(np.float32), parts=parts))
    pack.write(out + '/bodies/marat8.json',
               dict(format='engine/body', version=1, id='marat8', label=dict(ru='Марат', en='Marat'),
                    source='to3d/r28-s8-marat: Anny (moood-man) fitted to the С8 drawing, HBM stylised head',
                    topology='marat8', skeleton='soma77'),
               dict(positions=Vall, joints=J.astype(np.float32), frames=np.asarray(bod['frames'], np.float32)))
    np.savez(f'{CACHE}/rest.npz', uv=np.vstack([p['uv'] for p in PIECES]).astype(np.float32),
             pat=np.vstack([p['pat'] for p in PIECES]).astype(np.float32),
             tint=np.concatenate([p['tint'] for p in PIECES]).astype(np.float32))
    json.dump(dict(id=BID, pieces=info, HH=HH, O=O.tolist(), tex=os.path.join(FOLDER, 'tools/web/tex')),
              open(f'{CACHE}/model.json', 'w'), indent=1)
    print('marat8', len(Vall), 'vertices', len(T), 'triangles;', ', '.join(f"{p['name']}:{p['count']}" for p in info))


write()


def write_face():
    """the face rig for face.mjs: every replacement piece's shapes (world rest positions), the lids' weights over the
    head's vertices and each eye's centre and axes, the lash and eyeballs' vertex ranges, the expressions' numbers"""
    info = {p['name']: (sum(q['V'].shape[0] for q in PIECES[:i]), len(p['V'])) for i, p in enumerate(PIECES)}
    fj = json.load(open(f'{CACHE}/face.json'))
    arrays = {}
    shapes = {}
    for part in MOUTH:
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
    hdr = dict(format='marat8/face', version=1, pieces={k: list(v) for k, v in info.items()}, shapes=shapes, lids=lids,
               eU0=eU0, eL0=eL0, mouth=MOUTH, expr=fj['expr'], faces=fj['faces'], visemes=fj['visemes'],
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
    for sub, name, to in (('engine/data/bodies', 'marat8', 'bodies'), ('engine/data/topology', 'marat8', 'topology'), ('engine', 'face', '')):
        os.makedirs(os.path.join(D, to), exist_ok=True)
        for ext in ('json', 'bin'):
            shutil.copy(os.path.join(CACHE, sub, f'{name}.{ext}'), os.path.join(D, to, f'{name}.{ext}'))
    info = [dict(name=p['name'], mat=p['mat']) for p in PIECES]
    pack.write(os.path.join(D, 'look.json'), dict(format='marat8/look', version=1, pieces=info,
               counts=[len(p['V']) for p in PIECES], tris=[len(p['T']) for p in PIECES]),
               dict(uv=np.vstack([p['uv'] for p in PIECES]).astype(np.float32),
                    pat=np.vstack([p['pat'] for p in PIECES]).astype(np.float32),
                    tint=np.concatenate([p['tint'] for p in PIECES]).astype(np.float32)))
    print('viewer data in', D)


write_viewer_data()

