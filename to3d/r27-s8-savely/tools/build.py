"""Савелий Петрович assembled: Anny's fitted old man (fit_body.py), the fitted base head (fit_head.py) with its glass
eyes, the replacement face pieces (face.py: mouth, brows, the moustache), the tufts (fit_hair.py), the half-moon
glasses, the drawing's short wide neck, and the clothes — every piece skinned on SOMA's 77 joints — written as an engine
body on its own topology (engine/README.md: Formats), plus what the renderer and the viewer need: which vertices are
which piece and its material, the paint coordinates.

Clothes, from the drawing's numbers (cast.SAVELY_FIG / SAVELY_BODY of styles/s8-stopmotion):
- the waistcoat: the drawing's own torso loft (a pear: its width, front and back at every height) as a clean grid, cut
  open in the drawing's V; its weights taken from Anny's trunk carried out onto the same loft (trunk joints only: a
  stiff waistcoat on a round body); a wall at its edges, so it has a thickness;
- the shirt: its front inside the V (the same loft, a little in), a collar stand round the neck and two collar points,
  the sleeves = Anny's arms carried round their bones to the sleeve's radius, with cuffs; the tie on the shirt front;
- three buttons and the watch chain on the waistcoat; the trousers = Anny's legs carried round the leg bones to the
  drawing's wide trouser legs; the shoes lofted round the feet.
Writes CACHE/engine/data/{bodies,topology}/savely8.* and CACHE/model.json (pieces, materials) + CACHE/rest.npz."""
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
    V, T, uv = sphere(drawing.eye_centre(s), drawing.EYE_R)
    sj, sw = one(len(V), 'Head')
    piece(nm, 'eye', W(V), T, sj, sw, uv=uv)

# the replacement pieces, at the calm face (face.mjs mixes their shapes)
F = np.load(f'{CACHE}/face.npz')
MOUTH = ['lipU', 'lipL', 'cav', 'teethU', 'teethL', 'moust']        # the pieces that go with the mouth's shapes
for part, mat in (('lipU', 'lip'), ('lipL', 'lip'), ('cav', 'mouth'), ('teethU', 'teeth'), ('teethL', 'teeth')):
    V = F[f'{part}_calm']; sj, sw = one(len(V), 'Head')
    piece(part, mat, W(V), F[part + '_T'], sj, sw)
V = F['moust_calm']; sj, sw = one(len(V), 'Head'); piece('moust', 'whisker', W(V), F['moust_T'], sj, sw, uv=F['moust_uv'], subdiv=1)
V = F['brow_calm']; sj, sw = one(len(V), 'Head'); piece('brows', 'whisker', W(V), F['brow_T'], sj, sw, uv=F['brow_uv'], subdiv=1)
V = F['lash_V']; sj, sw = one(len(V), 'Head'); piece('lashes', 'lash', W(V), F['lash_T'], sj, sw)

HR = np.load(f'{CACHE}/hair.npz')
sj, sw = one(len(HR['V']), 'Head')
piece('hair', 'hair', W(HR['V']), HR['T'], sj, sw, uv=HR['uv'])


# --- the half-moon glasses (cast.savely_over → props.glasses 'half'): gold wire rims in front of the eyes, lower than
# the eyes (he looks over them), a bridge over the nose, temples back to the ears; thin lenses
def glasses(rw=0.075, rh=0.05, out=0.1, lw=0.008, y_off=0.075):
    H0 = drawing.H0
    ye = TP['eye_y'] + y_off
    wire = lw * 0.62
    tubes, lens = [], []
    ends = {}
    for side in (-1, 1):
        phi = side * TP['eye_phi']
        c = np.array(H0.surf(phi, ye, out))
        tg = np.array(H0.surf(phi + 0.01, ye, out)) - c; tg /= np.linalg.norm(tg)
        dn = np.array([0, 1.0, 0])
        tt = np.linspace(0, 2 * np.pi, 48, endpoint=False)
        loc = np.c_[rw * np.cos(tt), rh * np.maximum(-0.15, np.sin(tt))]
        # the flat top's corners rounded a little
        ring = c + loc[:, :1] * tg + loc[:, 1:] * dn
        ring = np.r_[ring, ring[:1]]
        tubes.append(ring)
        nrm = np.cross(tg, dn); nrm *= np.sign(nrm[2])
        lens.append((c, loc, tg, dn, nrm))
        ends[side] = (c + side * rw * tg * (1 if tg[0] > 0 else -1) - 0.15 * rh * dn * 0, c)
    # bridge
    br = np.array([H0.surf(-TP['eye_phi'] * 0.45, ye - 0.02, out * 0.8), H0.surf(0, ye - 0.035, out * 0.95),
                   H0.surf(TP['eye_phi'] * 0.45, ye - 0.02, out * 0.8)])
    tubes.append(resample(br, 14))
    for side in (-1, 1):
        phi = side * TP['eye_phi']
        c = np.array(H0.surf(phi, ye, out)); tg = np.array(H0.surf(phi + 0.01, ye, out)) - c; tg /= np.linalg.norm(tg)
        p_rim = c + side * rw * tg * np.sign(tg[0]) + np.array([0, -0.15 * rh, 0])
        p0 = np.array(H0.surf(side * (TP['eye_phi'] + 0.5), ye - 0.03, out * 0.55))
        p1 = np.array(H0.surf(side * TP['ear_phi'] * 0.97, TP['ear_y'] - 0.07, 0.022))
        p2 = np.array(H0.surf(side * (TP['ear_phi'] + 0.22), TP['ear_y'] - 0.02, 0.012))
        tubes.append(resample(np.array([p_rim, p0, p1, p2]), 22))
    Vs, Ts, n = [], [], 0
    for path in tubes:
        v, t, _ = tube_along(hu(path), np.full(len(path), wire), n=10)
        Vs.append(v); Ts.append(t + n); n += len(v)
    GV, GT = np.concatenate(Vs), np.concatenate(Ts)
    Ls, LTs, n = [], [], 0
    for c, loc, tg, dn, nrm in lens:
        rr = np.linspace(0, 1, 6)[1:]
        v = [c] + [c + (loc[:, :1] * tg + loc[:, 1:] * dn) * r for r in rr]
        v = np.vstack([np.atleast_2d(x) for x in v]); m = len(loc); t = []
        for j in range(m): t.append((0, 1 + j, 1 + (j + 1) % m))
        for k in range(len(rr) - 1):
            for j in range(m):
                a, b = 1 + k * m + j, 1 + k * m + (j + 1) % m; t += [(a, a + m, b), (b, a + m, b + m)]
        Ls.append(hu(v)); LTs.append(np.array(t) + n); n += len(v)
    return GV, GT, np.concatenate(Ls), np.concatenate(LTs)


def resample(p, n):
    """a smooth curve through the points (Catmull-Rom), n points"""
    p = np.asarray(p, float); m = len(p) - 1; out = []
    for u in np.linspace(0, m, n):
        j = min(int(u), m - 1); t = u - j
        p0, p1, p2, p3 = p[max(0, j - 1)], p[j], p[j + 1], p[min(m, j + 2)]
        out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


from common import hu
GV, GT, LV, LT = glasses()
sj, sw = one(len(GV), 'Head'); piece('glasses', 'gold', W(GV), GT, sj, sw)
sj, sw = one(len(LV), 'Head'); piece('lenses', 'lens', W(LV), LT, sj, sw)

# ======================================================================================== the neck
N = drawing.BODY['neck']
ys = np.linspace(0.25, 0.8, 24)
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
TOR = Head(FIG['torso'], 1.0, 0.0, 0.0, 0.0, 0.0)          # the drawing's torso loft (head units, y down from the head)
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


VEE = [(-0.2, 0.6), (-0.13, 0.75), (-0.03, 1.15), (0.0, 1.2), (0.03, 1.15), (0.13, 0.75), (0.2, 0.6), (0.2, 0.45), (-0.2, 0.45)]
yds = TY0 + (TY1 - TY0) * np.linspace(0, 1, 84) ** 1.25            # denser at the shoulders
VEST_OUT, SHIRT_IN = 0.012, -0.012                              # the cloth's thickness against the loft (head units)
gv, gt, gph, gyd = grid(160, yds, VEST_OUT)
gX = np.array([TOR.a(v) for v in gyd]) * np.sin(gph)
sdV = np.where(np.cos(gph) > 0, poly_sd(gX, gyd, VEE), 1.0)
v, t, a, on = cut(gv, gt, -sdV, np.c_[gph, gyd])
VD = trunk_weights(v)
for L in boundary_loops(t):
    v, t, VD, a = wall(v, t, VD, L, (VEST_OUT - SHIRT_IN) * HH * 0.9, a)
sj, sw = top4(VD)
piece('vest', 'vest', v, t, sj, sw, uv=np.c_[a[:, 0] * 0.2, yw(a[:, 1])])
# the barrel's bottom closed a little above the hem (seen from below, the waistcoat is not hollow)
cy = TY1 - 0.06
ph = np.linspace(-math.pi, math.pi, 48, endpoint=False)
rimv = bar(ph, np.full(48, cy), 0.0); cv = np.r_[rimv, rimv.mean(0)[None]]
ct = np.array([(48, (j + 1) % 48, j) for j in range(48)])
sj, sw = top4(trunk_weights(cv)); piece('vestbottom', 'dark', cv, ct, sj, sw)

# the shirt front inside the V, and the collar stand round the neck
sv, st, sph, syd = grid(160, yds[yds < 1.3], SHIRT_IN)
sX = np.array([TOR.a(v_) for v_ in syd]) * np.sin(sph)
sds = np.where(np.cos(sph) > 0, poly_sd(sX, syd, VEE), 1.0)
v, t, a, on = cut(sv, st, sds - 0.03)
sj, sw = top4(trunk_weights(v)); piece('shirtfront', 'shirt', v, t, sj, sw)
rows = []
for k, (y, grow) in enumerate(((0.44, 0.022), (0.47, 0.03), (0.52, 0.032), (0.58, 0.03), (0.63, 0.024))):
    a_ = interp(N['a'], y) + grow; fr = interp(N['front'], y) + grow; bk = interp(N['back'], y) - grow
    rows.append([Wd(a_ * math.sin(q), y, (fr + bk) / 2 + (fr - bk) / 2 * math.cos(q)) for q in np.linspace(-math.pi, math.pi, 40, endpoint=False)])
cv = np.array(rows).reshape(-1, 3); ct = []
for i in range(len(rows) - 1):
    for j in range(40):
        p, q = i * 40 + j, i * 40 + (j + 1) % 40
        ct += [(p, p + 40, q), (q, p + 40, q + 40)]
Dc = 0.5 * neck_weights(cv) + 0.5 * trunk_weights(cv)
sj, sw = top4(Dc); piece('collarstand', 'shirt', cv, np.array(ct), sj, sw)


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
    V, T = patch([(side * 0.035, 0.585), (side * 0.16, 0.6), (side * 0.095, 0.76), (side * 0.03, 0.7)], VEST_OUT + 0.003, bulge=0.012)
    sj, sw = top4(trunk_weights(V)); piece('collar' + 'RL'[side > 0], 'collar', V, T, sj, sw)
tie_y = np.array([0.62, 0.66, 0.7, 0.74, 0.85, 0.95, 1.0, 1.04, 1.08])
tie_w = np.array([0.03, 0.04, 0.038, 0.028, 0.036, 0.046, 0.05, 0.03, 0.002])
tie_o = np.array([0.02, 0.03, 0.028, 0.016, 0.014, 0.014, 0.014, 0.012, 0.008])
yy = np.linspace(0.62, 1.08, 30); nu = 9
V = []
for y in yy:
    w_, o_ = np.interp(y, tie_y, tie_w), np.interp(y, tie_y, tie_o)
    for u in np.linspace(-1, 1, nu):
        V.append(front([u * w_], [y], SHIRT_IN + o_ * (0.35 + 0.65 * math.sqrt(max(0.0, 1 - u * u))))[0])
V = np.array(V); T = []
for i in range(len(yy) - 1):
    for j in range(nu - 1):
        a_, b_ = i * nu + j, i * nu + j + 1; T += [(a_, a_ + nu, b_), (b_, a_ + nu, b_ + nu)]
T = orient_out(V, np.array(T))
sj, sw = top4(trunk_weights(V)); piece('tie', 'tie', V, T, sj, sw)

# buttons (three, down the front) and the watch chain (a sagging line of links from a button to the pocket)
for k in range(3):
    c = front([0.0], [1.22 + 0.13 * k], VEST_OUT + 0.006)[0]
    V, T, _ = sphere(c, 0.019 * HH, n=10, squash=(1, 1, 0.5))
    sj, sw = top4(trunk_weights(V)); piece(f'button{k}', 'button', V, T, sj, sw)
tt = np.linspace(0, 1, 40)
ch = front(-0.06 + 0.34 * tt, 1.3 + 0.12 * np.sin(np.pi * tt), VEST_OUT + 0.008)
V, T, A = tube_along(ch, np.full(len(ch), 0.0045 * HH * (1 + 0.0 * tt)), n=8)
sj, sw = top4(trunk_weights(V)); piece('chain', 'chain', V, T, sj, sw, uv=np.c_[A[:, 0], A[:, 1] / 39.0])

# --- the shirt's sleeves: Anny's arms carried round their bones to the sleeve's radius (0.13 → 0.11 head)
sleeve_end = 1.9
f_sl = np.maximum.reduce([np.where(armw + handw > 0.25, at - sleeve_end, 1.0), 0.25 - (armw + handw), 0.0 - at, handw - 0.6])
v, t, a, on = cut(BV, BT, f_sl, np.c_[BD, at])
D_sl = a[:, :NJ]; at_s = a[:, NJ]
_, bp = arm_coord(v)
d = v - bp; dl = np.linalg.norm(d, axis=1, keepdims=True)
rs = (0.13 - 0.01 * np.clip(at_s / 2, 0, 1)) * HH * (1 + 0.06 * np.exp(-((at_s - 1.0) / 0.25) ** 2))      # a little fuller at the elbow
sv = bp + d / np.maximum(dl, 1e-6) * rs[:, None]
sv = smooth(sv, t, it=5, lam=0.4, fixed=np.where(on & (at_s > 1.5))[0])
sj, sw = top4(D_sl)
piece('sleeves', 'shirt', sv, t, sj, sw, subdiv=1)
SL_V, SL_T, SL_D = sv, t, D_sl
# the shoulders: a ball at each shoulder joint, where the sleeve comes out of the waistcoat (a puppet's ball joint under cloth)
for pre in ('Left', 'Right'):
    V, T, _ = sphere(BJ[IX[pre + 'Arm']], 0.132 * HH, n=14)
    sj, sw = one(len(V), pre + 'Arm'); piece('shoulder' + pre[0], 'shirt', V, T, sj, sw)


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
    if np.linalg.norm(c - BJ[IX[pre + 'Hand']]) > 0.08: continue          # the shoulder's end stays open inside the waistcoat
    axh = BJ[IX[pre + 'Hand']] - BJ[IX[pre + 'ForeArm']]; axh /= np.linalg.norm(axh)
    def od(X, cc=c, axh=axh):
        d = X - cc; d -= (d @ axh)[:, None] * axh; return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
    band(L, SL_V, SL_D, od, 0.016, 0.0035, 'cuff' + pre[0], lambda X, axh=axh: np.tile(-axh, (len(X), 1)), 'collar')

# --- the trousers: Anny's legs carried round the leg bones to the drawing's wide trouser legs (r 0.17 → 0.14 head)
TR_TOP, TR_HEM = yw(1.95), yw(3.22)
f_tr = np.maximum.reduce([Y - TR_TOP, TR_HEM - Y, 0.45 - legw])
v, t, a, on = cut(BV, BT, f_tr, np.c_[BD, lt])
D_tr = a[:, :NJ]; lt_s = a[:, NJ]
_, bp = leg_coord(v)
# the trouser leg hangs straight down from the hip (the bone leans out a little): its axis is the bone's point, x kept
d = v - bp; d[:, 1] = 0; dl = np.linalg.norm(d, axis=1, keepdims=True)
rt = (0.17 - 0.015 * np.clip(lt_s / 2, 0, 1)) * HH
sv = np.c_[bp[:, 0], v[:, 1], bp[:, 2]] + d / np.maximum(dl, 1e-6) * rt[:, None]
sv = smooth(sv, t, it=6, lam=0.4, fixed=np.where(on & (v[:, 1] < TR_HEM + 0.01))[0])
sj, sw = top4(D_tr)
piece('trousers', 'trousers', sv, t, sj, sw, subdiv=1)
for L in boundary_loops(t):
    c = sv[L].mean(0)
    if c[1] < TR_HEM + 0.02:
        band(L, sv, D_tr, lambda X, cc=c: np.c_[(X - cc)[:, 0], np.zeros(len(X)), (X - cc)[:, 2]] / np.maximum(np.linalg.norm((X - cc)[:, [0, 2]], axis=1, keepdims=True), 1e-6),
             0.012, 0.003, 'trhem' + ('L' if c[0] > 0 else 'R'), lambda X: np.tile([0, 1.0, 0], (len(X), 1)), 'trousers')

# --- skin: the hands from inside the cuffs
f_skin = np.where(handw + armw > 0.3, sleeve_end - 0.06 - at, 1.0)
v, t, a, on = cut(BV, BT, f_skin, np.c_[BD, handw])
sj, sw = top4(a[:, :NJ])
piece('skin', 'skin', v, t, sj, sw, uv=np.tile(SKIN_UV, (len(v), 1)), tint=np.clip(a[:, NJ], 0, 1) * 0.5, subdiv=1)


# --- shoes: a rounded shoe lofted along each foot (the drawing's: length 0.36 head, height 0.11, half width 0.1)
SHOE = dict(len=0.36, h=0.11, w=0.1)


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
    sole = 0.009
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
    pack.write(out + '/topology/savely8.json',
               dict(format='engine/topology', version=1, id='savely8', about='Савелий Петрович (С8): every piece in one mesh',
                    source='to3d/r27-s8-savely', skeleton='soma77', vertices=len(Vall), triangles=len(T), parts=th['parts']),
               dict(triangles=T.astype(np.uint32), skinJoints=sj.astype(np.uint8), skinWeights=sw.astype(np.float32), parts=parts))
    pack.write(out + '/bodies/savely8.json',
               dict(format='engine/body', version=1, id='savely8', label=dict(ru='Савелий Петрович', en='Savely Petrovich'),
                    source='to3d/r27-s8-savely: Anny (moood-oldman) fitted to the С8 drawing, HBM stylised head',
                    topology='savely8', skeleton='soma77'),
               dict(positions=Vall, joints=J.astype(np.float32), frames=np.asarray(bod['frames'], np.float32)))
    np.savez(f'{CACHE}/rest.npz', uv=np.vstack([p['uv'] for p in PIECES]).astype(np.float32),
             pat=np.vstack([p['pat'] for p in PIECES]).astype(np.float32),
             tint=np.concatenate([p['tint'] for p in PIECES]).astype(np.float32))
    json.dump(dict(id=BID, pieces=info, HH=HH, O=O.tolist(), tex=os.path.join(FOLDER, 'tools/web/tex')),
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
    hdr = dict(format='savely8/face', version=1, pieces={k: list(v) for k, v in info.items()}, shapes=shapes, lids=lids,
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
