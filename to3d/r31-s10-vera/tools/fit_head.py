"""Fit Blender's Human Base Meshes head (realistic, for animation; CC0) to the head of the drawing (who.py).

The drawing's head is a 3D surface already (styles/s10-ligne-claire/tools/head.py: slices, nose, lips, chin, ears,
neck); drawing.py dumped it as points. Here the base head is laid onto it:
  1. a first placement by landmarks (eyes, crown, chin, back of the head), stretched per axis and above/below the
     eyes separately (the drawing's face below the eyes is shorter);
  2. non-rigid ICP: each vertex pulled to the nearest point of the drawing's surface whose normal agrees, while a
     Laplacian term keeps the base mesh's own form (its loops, lids, lips, ears, nostrils) — the stiffness lowered
     step by step;
  3. the eyes and lids are not pulled to the surface (the drawing has none there): the eye region is carried as a
     whole — scaled about the eye's centre and set where the drawing has its eye; the ears likewise are carried
     to the drawing's ear as a whole; the inside of the mouth follows the Laplacian only.
Units: the drawing's (crown to chin ~200, y down, z toward the viewer), in the figure's frame (head drop 20).
usage: python3 fit_head.py CACHE  → CACHE/head_fit.npz (verts, faces, eye balls), CACHE/head_fit.png
"""
import sys, os, json
import numpy as np
from scipy.spatial import cKDTree
import scipy.sparse as sp
from scipy.sparse.linalg import factorized

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import who           # noqa: E402
import dots          # noqa: E402

C = sys.argv[1]
d = np.load(os.path.join(C, 'hbm_head.npz'))
dr = np.load(os.path.join(C, 'drawing.npz'))
info = json.load(open(os.path.join(C, 'drawing.json')))
DROP = who.DROP
h, _ = who.head()

V0 = d['head_v'].copy()
Fpoly = d['head_f']
cx = (V0[:, 0].min() + V0[:, 0].max()) / 2
EYE_H = np.array([d['scleraL_v'].mean(0), d['scleraR_v'].mean(0)])   # Blender: L is +x (the person's left)
RS = 0.0117                                                           # sclera radius
ez, ey = EYE_H[0, 2], EYE_H[0, 1]

# ------------------------------------------------------------------ 1. first placement
EX = who.EYE[0]                                # the drawing's eye on the face
EYD = who.EYE[1] + DROP
CROWN_D, CHIN_D = h.ymin + DROP, h.ymax - 1 + DROP
cxs = EX / abs(EYE_H[0, 0] - cx)
up = (EYD - CROWN_D) / (0.88 - ez)
down = (CHIN_D - EYD) / (ez - 0.648)
zs = 0.5 * (up + down) * 1.08                   # depth scale (the drawing's head is deep: a long skull behind)
EYE_ZD = float(h.face_z(EX, who.EYE[1]))
c_e = 0.84 * cxs                                # the eye region's own scale (the drawing's eyes are a bit smaller)
eye_depth = (RS + 0.0012) * c_e
EYE_D = np.array([[EX, EYD, EYE_ZD - eye_depth], [-EX, EYD, EYE_ZD - eye_depth]])


def place(P):
    x = (P[:, 0] - cx) * cxs
    dz = P[:, 2] - ez
    t = 1 / (1 + np.exp(-dz / 0.01))            # smooth step between the scales above and below the eyes
    y = EYD - dz * (t * up + (1 - t) * down)
    z = EYE_D[0, 2] - (P[:, 1] - ey) * zs
    return np.stack([x, y, z], 1)


def eye_carry(P, k):
    """Points of eye k (0: the person's left, +x) carried by the eye region's own scale."""
    q = P - EYE_H[k]
    return EYE_D[k] + np.stack([q[:, 0], -q[:, 2], -q[:, 1]], 1) * c_e


V = place(V0)
# the drawing's face can be much narrower below the eyes than the base's (a pointed chin): the base is first brought
# to the drawing's width at every height, so the fit starts near and the skin doesn't fold over itself
_notear = np.abs(V0[:, 0] - cx) < 0.066
_ys = np.arange(CROWN_D + 10, CHIN_D + 1, 6.0)
_wb = np.array([np.abs(V[_notear & (np.abs(V[:, 1] - y) < 5), 0]).max() for y in _ys])
_wd = np.array([float(h.sl(y - DROP)[0]) for y in _ys])
_ok = _ys < CHIN_D - 14                              # at the very chin both go to nothing: hold the last ratio
_ratio = np.interp(V[:, 1], _ys[_ok], np.clip(_wd / _wb, 0.6, 1.4)[_ok])
V[:, 0] *= np.where(V[:, 1] < 150, _ratio, 1.0)
print('width ratio by height', np.round(np.clip(_wd / _wb, 0.6, 1.4)[_ok][::4], 2))

# the nose: the drawing's is the caricature — big, round, drooping. The base's nose is enlarged about its root
# before the fit (so the Laplacian keeps a nose's form, at the drawing's size), with a smooth falloff to the cheeks.
NOSE_H = np.array([cx, -0.169, 0.729])
ROOT_H = np.array([cx, -0.128, 0.770])
_m = np.abs(V0[:, 0] - cx) < 2e-3
_ys = np.linspace(-10, 60, 300)
_zt = np.array([float(h.face_z(0.0, y)) for y in _ys])
TIP_D = np.array([0.0, _ys[_zt.argmax()] + DROP, _zt.max()])
ROOT_D = np.array([0.0, -2 + DROP, float(h.face_z(0.0, -2))])
r_h, t_h = place(ROOT_H[None])[0], place(NOSE_H[None])[0]
sc_n = np.array([getattr(who, 'NOSE_W', 1.0), (TIP_D[1] - ROOT_D[1]) / (t_h[1] - r_h[1]), (TIP_D[2] - ROOT_D[2]) / (t_h[2] - r_h[2])])
dn = np.linalg.norm((V0 - NOSE_H) * [1, 1, 0.8], axis=1)
wn = np.clip((0.05 - dn) / 0.022, 0, 1) ** 1.5
wn[V0[:, 1] > -0.115] = 0
V = V + wn[:, None] * (ROOT_D + (V - r_h) * sc_n - V)
print('nose scale', sc_n.round(2), 'tip', TIP_D.round(1))

# the mouth: the drawing's is narrower than the base's — the base's mouth is drawn in toward the middle before the
# fit (the lips keep their form), fading out to the cheeks
MOUTH_H = np.array([cx, -0.150, 0.691])
_dm = np.linalg.norm((V0 - MOUTH_H) * [1, 0.6, 1.3], axis=1)
_wm = np.exp(-(_dm / 0.024) ** 2)
V[:, 0] *= 1 - (1 - getattr(who, 'MOUTH_SX', 1.0)) * _wm
# and set at the drawing's height (the drawing's upper lip is short, the chin long)
_my0 = place(MOUTH_H[None])[0, 1]
V[:, 1] += (who.MOUTH_Y - _my0) * np.exp(-(_dm / 0.034) ** 2)
print('mouth moved by', round(float(who.MOUTH_Y - _my0), 1))

# mesh: triangles from the polygons (fan), edges, Laplacian
tris, edges = [], set()
for f in Fpoly:
    f = [x for x in f if x >= 0]
    for i in range(1, len(f) - 1):
        tris.append((f[0], f[i], f[i + 1]))
    for i in range(len(f)):
        a, b = f[i], f[(i + 1) % len(f)]
        edges.add((min(a, b), max(a, b)))
tris = np.array(tris)
E = np.array(sorted(edges))
N = len(V)
A = sp.coo_matrix((np.ones(len(E) * 2), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(N, N)).tocsr()
deg = np.asarray(A.sum(1)).ravel()
L = sp.diags(np.ones(N)) - sp.diags(1 / deg) @ A


def vnormals(P):
    n = np.zeros_like(P)
    fn = np.cross(P[tris[:, 1]] - P[tris[:, 0]], P[tris[:, 2]] - P[tris[:, 0]])
    for k in range(3):
        np.add.at(n, tris[:, k], fn)
    return SGN * n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


SGN = 1.0


_nv = vnormals(V)
SGN = 1.0 if np.mean(np.einsum('ij,ij->i', _nv, V - V.mean(0))) > 0 else -1.0
# ------------------------------------------------------------------ regions of the base head
# distance to an eye, counting little what lies behind it (the socket's pocket goes deep behind the ball)
_q = V0[:, None, :] - EYE_H[None]
_de = np.sqrt(_q[..., 0] ** 2 + _q[..., 2] ** 2 + np.minimum(_q[..., 1], 0) ** 2 + (np.maximum(_q[..., 1], 0) * 0.3) ** 2)
dist_eye = _de.min(1)
eye_k = _de.argmin(1)
eye_w = np.clip((0.026 - dist_eye) / 0.008, 0, 1)            # 1 inside 18 mm of an eye, 0 beyond 26 mm
ear = (np.abs(V0[:, 0] - cx) > 0.066) & (V0[:, 2] > 0.68) & (V0[:, 2] < 0.80) & (V0[:, 1] > -0.066) & (V0[:, 1] < -0.018)
# the inside of the mouth and the throat: vertices whose normal at rest points inward (toward the head's axis)
n0 = vnormals(V0) * SGN   # V0 is in Blender's handedness: flip back
axis_pt = np.stack([np.full(N, cx), np.full(N, -0.03), V0[:, 2]], 1)
inward = np.einsum('ij,ij->i', n0, V0 - axis_pt) < 0
# the mouth's bag: those of them that lie behind the face's front surface (the concave skin beside the nose and
# under it is turned inward too, but nothing is in front of it)
_cand = inward & (V0[:, 2] < 0.75) & (V0[:, 2] > 0.6) & (np.abs(V0[:, 0] - cx) < 0.06)
import igl                                                  # noqa: E402
_T64 = np.ascontiguousarray(tris, np.int64)
_V64 = np.ascontiguousarray(V0, np.float64)
mouth_in = np.zeros(N, bool)
for _i in np.nonzero(_cand)[0]:
    _hit = igl.ray_mesh_intersect(V0[_i] + np.array([0, -4e-4, 0]), np.array([0.0, -1.0, 0.0]), _V64, _T64, True)
    mouth_in[_i] = bool(_hit)
_nc = 1
print('mouth bag', mouth_in.sum(), 'of', _cand.sum(), 'in', _nc, 'patches')
# below the collar: no target (the shirt hides it); it follows the Laplacian
low = V0[:, 2] < 0.56
# the neck between the jaw and the collar: pulled onto the drawing's neck (an elliptic tube), not to the jaw above
NK = info['neck']
neck = (V0[:, 2] < 0.635) & (V0[:, 1] > -0.085) & ~low

# the drawing's ear: a sheet at (±(w-3+out*0.6), y, z)
e = info['ear']
w_e = float(h.sl(e['y'])[0])
EAR_D = np.array([[w_e - 3 + e['out'] * 0.55, e['y'] + DROP, e['z']], [-(w_e - 3 + e['out'] * 0.55), e['y'] + DROP, e['z']]])
ear_side = np.where(V0[:, 0] > cx, 0, 1)
EAR_H = np.array([V0[ear & (ear_side == k)].mean(0) for k in (0, 1)])
ear_c = 1.0 * cxs


EAR_K = np.array([e['out'] / 14, e['ry'] / 22, e['rz'] / 12])     # the drawing's ear against Савелий Петрович's (Р2)


def ear_carry(P, k):
    q = P - EAR_H[k]
    return EAR_D[k] + np.stack([q[:, 0] * 0.8, -q[:, 2] * 1.1, -q[:, 1] * 0.9], 1) * ear_c * EAR_K


# ------------------------------------------------------------------ target: the drawing's skin (no ears)
T = dr['head_pts']
lab = dr['head_lab']
T = T[~np.isin(lab, ['earR', 'earL'])]
rng = np.random.default_rng(0)
T = T[rng.choice(len(T), min(len(T), 160000), replace=False)]
tree = cKDTree(T)
_, nn = tree.query(T, 12)
Q = T[nn] - T[nn].mean(1, keepdims=True)
_, _, vt = np.linalg.svd(Q, full_matrices=False)
TN = vt[:, 2, :]
cen = np.stack([np.zeros(len(T)), T[:, 1], np.full(len(T), -14.0)], 1)
TN *= np.sign(np.einsum('ij,ij->i', TN, T - cen))[:, None]

# fixed targets: the eye regions and the ears, carried whole
fixed_t = np.zeros_like(V)
fixed_w = np.zeros(N)
for k in (0, 1):
    m = (eye_k == k) & (eye_w > 0)
    fixed_t[m] = eye_carry(V0[m], k)
    fixed_w[m] = np.where(eye_w[m] >= 1, 1e4, eye_w[m] * 20)     # the eye and lids held exactly
    m2 = ear & (ear_side == k)
    fixed_t[m2] = ear_carry(V0[m2], k)
    fixed_w[m2] = 1e4
free = (fixed_w == 0) & ~mouth_in & ~low & ~neck

# the reference form for the Laplacian: the placed base, with the eyes and ears already where they are carried
wb = np.where(fixed_w >= 1e4, 1.0, np.clip(fixed_w / 20, 0, 1))[:, None]
V = V * (1 - wb) + fixed_t * wb
Vref = V.copy()
for it, alpha in enumerate([30, 20, 12, 8, 5, 3, 2, 2]):
    n = vnormals(V)
    dist, j = tree.query(V, 1)
    ok = free & (np.einsum('ij,ij->i', n, TN[j]) > 0.3) & (dist < 30)
    # neck: radial projection onto the drawing's neck tube at the vertex's height
    a = np.arctan2((V[:, 2] - NK['z']) / NK['rz'], V[:, 0] / NK['rx'])
    nt = np.stack([NK['rx'] * np.cos(a), V[:, 1], NK['z'] + NK['rz'] * np.sin(a)], 1)
    wv = ok.astype(float) + fixed_w + neck * 0.5
    tv = np.where(ok[:, None], T[j], 0) + fixed_t * fixed_w[:, None] + nt * (neck * 0.5)[:, None]
    tv = np.where(wv[:, None] > 0, tv / np.maximum(wv, 1e-9)[:, None], 0)
    M = sp.diags(wv) + alpha * (L.T @ L)
    solve = factorized(M.tocsc())
    rhs = wv[:, None] * tv + alpha * (L.T @ (L @ Vref))
    V = np.stack([solve(rhs[:, k]) for k in range(3)], 1)
    print(it, alpha, ok.sum(), float(np.mean(dist[ok])))

# the mouth's bag is as wide and as high as the base's own jaw; the drawing's face is narrower and its upper lip
# shorter: the bag is kept inside (narrower and a little deeper), the lips' own edge left as it is
_hop = np.full(N, 99)
_hop[~mouth_in] = 0
for _i in range(1, 5):
    _near = (A @ (_hop < 99).astype(float)) > 0
    _hop[(_hop == 99) & _near] = _i
_wb = np.clip((_hop - 1) / 3.0, 0, 1) * mouth_in
_lim = 0.4 * np.asarray(h.sl(V[:, 1] - DROP)[0], float)
_x = _lim * np.tanh(V[:, 0] / np.maximum(_lim, 1e-6))
V = V + _wb[:, None] * (np.stack([_x, V[:, 1], V[:, 2] - 6.0], 1) - V)

_edge = (_hop == 1) & (np.abs(V[:, 0]) < 4) & (V[:, 2] > 55)
print('the fitted lips meet at y', round(float(V[_edge, 1].mean()), 1), '— the drawing\'s mouth is at', round(who.MOUTH_Y, 1))

# eye balls (sclera, iris) carried with their regions
balls = {}
for k, s in ((0, 'L'), (1, 'R')):
    for part in ('sclera', 'iris'):
        P = d[part + s + '_v']
        if part == 'iris':        # the base's iris lies under a clear cornea; ours is opaque: set it on the ball
            P = P + np.array([0, -0.0024, 0])
        balls[part + s] = eye_carry(P, k)

np.savez(os.path.join(C, 'head_fit.npz'), v=V, f=Fpoly, tris=tris, v_init=Vref, low=low, ear=ear, eye_w=eye_w, mouth_in=mouth_in,
         hop=_hop, mouth_line=float(V[_edge, 1].mean()), mouth_dark=mouth_in & (V0[:, 2] < 0.703),   # the bag reaches up behind the nostrils: only the mouth's part is dark
         **{b + '_v': balls[b] for b in balls}, **{b + '_f': d[b + '_f'] for b in balls})

# a look: profile and front, the fitted head over the drawing's points
Tp = dr['head_pts'][::8]
pr = [[(Tp[:, [2, 1]] * [-1, -1], '#f0c0a0', 0.6), (V[:, [2, 1]] * [-1, -1], '#333', 0.8),
       (np.vstack([balls['scleraL']])[:, [2, 1]] * [-1, -1], 'blue', 0.6)],
      [(Tp[:, [0, 1]] * [1, -1], '#f0c0a0', 0.6), (V[:, [0, 1]] * [1, -1], '#333', 0.8),
       (np.vstack([balls['scleraL'], balls['scleraR']])[:, [0, 1]] * [1, -1], 'blue', 0.6)]]
dots.plot(pr, os.path.join(C, 'head_fit.png'), 700)
