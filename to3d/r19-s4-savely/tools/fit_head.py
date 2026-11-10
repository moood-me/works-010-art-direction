"""Fit Blender's Human Base Meshes head «for animation» (realistic, CC0) to Вера's head from the Arcane drawing.
After Р2's fit_head.py (to3d/r2-s10-savely), changed for this drawing:
  1. placement by landmarks: eyes (±31, 0), crown −122, chin 112, separate vertical scales above and below the eyes;
  2. the nose enlarged about its root toward the drawing's long nose (tip and length from the drawing's nose surface),
     so the Laplacian keeps a nose's form at the drawing's size;
  3. non-rigid ICP onto the drawing's head, nose and neck surfaces (drawing.py) — the eye regions (balls and lids)
     and the ears carried as a whole; the inside of the mouth follows the Laplacian only; stiffness 30 → 2.
The drawn neck (54–64 units wide) is a stick in 3D; it is taken 1.45× wider (a slim woman's neck), as Р5 did.
usage: python3 fit_head.py CACHE  → CACHE/head_fit.npz, CACHE/head_fit.png"""
import sys, os
import numpy as np
from scipy.spatial import cKDTree
import scipy.sparse as sp
from scipy.sparse.linalg import factorized

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drawing as DR  # noqa: E402
from face import flat_uv  # noqa: E402  (the style's own)
import dots  # noqa: E402

C = sys.argv[1]
d = np.load(os.path.join(C, 'hbm_head.npz'))
dr = np.load(os.path.join(C, 'drawing.npz'))
P = DR.person()
FIT = DR.FIT
head, nose, neck = DR.surfaces(P)

V0 = d['head_v'].copy()
Fpoly = d['head_f']
cx = (V0[:, 0].min() + V0[:, 0].max()) / 2
EYE_H = np.array([d['scleraL_v'].mean(0), d['scleraR_v'].mean(0)])   # Blender: L is +x (the person's left)
RS = 0.0117
ez, ey = EYE_H[0, 2], EYE_H[0, 1]

EX, EYD = float(P.eye_x), float(P.eye_y)
CROWN_D, CHIN_D = float(head.v0), float(head.v1)


def face_z(x, y):
    u = flat_uv(head, np.array([float(x)]), np.array([float(y)]))
    return float(head.pos(u, np.array([float(y)]))[2][0])


cxs = EX / abs(EYE_H[0, 0] - cx)
up = (EYD - CROWN_D) / (0.880 - ez)
down = (CHIN_D - EYD) / (ez - 0.648)
zs = 0.5 * (up + down) * 1.0
EYE_SCALE = FIT['eye_scale']                              # the eye region against the head's scale
EYE_WIDE = FIT['eye_wide']                                # and its widening (an almond)
c_e = EYE_SCALE * cxs
EYE_ZD = face_z(EX + 2, EYD)
eye_depth = (RS + 0.0016) * c_e + FIT['eye_back']
EYE_D = np.array([[EX, EYD, EYE_ZD - eye_depth], [-EX, EYD, EYE_ZD - eye_depth]])
print('scales x %.0f up %.0f down %.0f z %.0f eye %.0f; eye z %.1f' % (cxs, up, down, zs, c_e, EYE_D[0, 2]))


# heights of the base's landmarks (Blender z, on the face's middle line) → the drawing's heights:
# crown, eye, nose tip, subnasale, mouth line, chin
ZMAP = [(0.648, CHIN_D), (0.692, float(P.mouth_y)), (0.714, float(nose.sub)), (0.731, float(nose.tip) - 2), (ez, EYD), (0.880, CROWN_D)]
from scipy.interpolate import PchipInterpolator
_zm = PchipInterpolator([a for a, b in ZMAP], [b for a, b in ZMAP], extrapolate=True)


def place(Pt):
    x = (Pt[:, 0] - cx) * cxs
    y = _zm(Pt[:, 2])
    z = EYE_D[0, 2] - (Pt[:, 1] - ey) * zs
    return np.stack([x, y, z], 1)


def eye_carry(Pt, k):
    q = Pt - EYE_H[k]
    return EYE_D[k] + np.stack([q[:, 0] * EYE_WIDE, -q[:, 2], -q[:, 1]], 1) * c_e


V = place(V0)
# the base's mouth is wide for this face: drawn in toward the middle (FIT['mouth_narrow'])
_dm0 = np.linalg.norm((V0 - np.array([cx, -0.155, 0.693])) / [0.032, 0.03, 0.02], axis=1)
V[:, 0] *= 1 - (1 - FIT.get('mouth_narrow', 1.0)) * np.clip(1.7 - _dm0, 0, 1) * np.clip((0.710 - V0[:, 2]) / 0.008, 0, 1)      # not the nose's base

# the nose: the drawing's is longer and stands further out; its protrusion is scaled (depth only, about the face
# behind it) so the Laplacian keeps a nose's form at the drawing's size
NP = dr['pts'][dr['lab'] == 1]
mid = NP[np.abs(NP[:, 0]) < 1.0]
tip = mid[mid[:, 2].argmax()]
NOSE_H = np.array([cx, -0.169, 0.731])
t_h = place(NOSE_H[None])[0]
zface = face_z(0, t_h[1]) - 6
k_n = float(np.clip((tip[2] - zface) / (t_h[2] - zface), 0.8, 1.6))
wn = np.clip((0.034 - np.linalg.norm((V0 - NOSE_H) * [1.0, 0.5, 0.9], axis=1)) / 0.014, 0, 1) ** 1.5
wn *= np.clip((V0[:, 2] - 0.709) / 0.006, 0, 1)
V[:, 2] = V[:, 2] + wn * (k_n - 1) * np.maximum(V[:, 2] - zface, 0)
print('nose: drawing tip', tip.round(1), 'base tip', t_h.round(1), 'protrusion x%.2f' % k_n)

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
SGN = 1.0


def vnormals(Pt):
    n = np.zeros_like(Pt)
    fn = np.cross(Pt[tris[:, 1]] - Pt[tris[:, 0]], Pt[tris[:, 2]] - Pt[tris[:, 0]])
    for k in range(3):
        np.add.at(n, tris[:, k], fn)
    return SGN * n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


_nv = vnormals(V)
SGN = 1.0 if np.mean(np.einsum('ij,ij->i', _nv, V - V.mean(0))) > 0 else -1.0

_q = V0[:, None, :] - EYE_H[None]
_de = np.sqrt(_q[..., 0] ** 2 + _q[..., 2] ** 2 + np.minimum(_q[..., 1], 0) ** 2 + (np.maximum(_q[..., 1], 0) * 0.3) ** 2)
dist_eye = _de.min(1)
eye_k = _de.argmin(1)
eye_w = np.clip((0.026 - dist_eye) / 0.008, 0, 1)
ear = (np.abs(V0[:, 0] - cx) > 0.066) & (V0[:, 2] > 0.68) & (V0[:, 2] < 0.80) & (V0[:, 1] > -0.066) & (V0[:, 1] < -0.018)
n0 = vnormals(V0) * SGN
axis_pt = np.stack([np.full(N, cx), np.full(N, -0.03), V0[:, 2]], 1)
inward = np.einsum('ij,ij->i', n0, V0 - axis_pt) < 0
mouth_in = inward & (V0[:, 2] < 0.72) & (V0[:, 2] > 0.6) & (np.abs(V0[:, 0] - cx) < 0.03)
low = V0[:, 2] < 0.545                     # below the collar: no target

EAR_D = np.array([[P.ear_x - 4, P.ear_y + 2, P.ear_z - 2], [-(P.ear_x - 4), P.ear_y + 2, P.ear_z - 2]])
ear_side = np.where(V0[:, 0] > cx, 0, 1)
EAR_H = np.array([V0[ear & (ear_side == k)].mean(0) for k in (0, 1)])
ear_c = FIT['ear'] * cxs


def ear_carry(Pt, k):
    q = Pt - EAR_H[k]
    return EAR_D[k] + np.stack([q[:, 0] * 0.85, -q[:, 2], -q[:, 1] * 0.9], 1) * ear_c


# target: the drawing's head, nose and (widened) neck
T = dr['pts'].copy()
lab = dr['lab']
nk = lab == 2
zc = -26.0
T[nk, 0] *= FIT['neck_x']
T[nk, 2] = zc + (T[nk, 2] - zc) * FIT['neck_z']
# neck points inside the head (under the jaw) are no target
from arc import interp
yy = np.clip(T[:, 1], head.v0, head.v1)
z0 = np.array([interp(head.z0, y) for y in yy])
uu = np.arctan2(T[:, 0], T[:, 2] - z0)
rr = head.r(uu, yy)
inside = nk & (T[:, 1] < head.v1 - 1) & (np.hypot(T[:, 0], T[:, 2] - z0) < rr + 4)
T = T[~inside]; lab = lab[~inside]; nk = lab == 2
# the face points that lie under the nose surface are inside the nose: drop them
under = (lab == 0) & (np.abs(T[:, 0]) < 13) & (T[:, 1] > nose.root + 4) & (T[:, 1] < nose.sub) & (T[:, 2] > 60)
T = T[~under]
lab = lab[~under]
tree = cKDTree(T)
_, nn = tree.query(T, 12)
Q = T[nn] - T[nn].mean(1, keepdims=True)
_, _, vt = np.linalg.svd(Q, full_matrices=False)
TN = vt[:, 2, :]
cen = np.stack([np.zeros(len(T)), np.clip(T[:, 1], -60, 140), np.full(len(T), -20.0)], 1)
TN *= np.sign(np.einsum('ij,ij->i', TN, T - cen))[:, None]

# the eye regions: carried whole (balls, lids) inside 16 mm; from there to 34 mm the carried place blends smoothly
# into the placed head, so the reference form has no step
fixed_t = np.zeros_like(V)
fixed_w = np.zeros(N)
blend = np.clip((0.034 - dist_eye) / 0.018, 0, 1)
blend = blend * blend * (3 - 2 * blend)
for k in (0, 1):
    m = (eye_k == k) & (blend > 0)
    V[m] = V[m] + blend[m, None] * (eye_carry(V0[m], k) - V[m])
    core = (eye_k == k) & (dist_eye < 0.016)
    fixed_t[core] = V[core]
    fixed_w[core] = 1e4
    m2 = ear & (ear_side == k)
    fixed_t[m2] = V[m2]
    fixed_w[m2] = 30
vis = d['head_vis']
outer = vis >= 8                            # seen from outside over a good part of its hemisphere
mouth_in = ~outer & (V0[:, 2] < 0.72) & (V0[:, 2] > 0.6) & (np.abs(V0[:, 0] - cx) < 0.035)
free = (fixed_w == 0) & outer & ~low
print('outer', outer.sum(), 'of', N)
Vref = V.copy()
# the lips and the nose keep the base's own form (the drawing's are a few bumps): their pull is weak
MOUTH_H = np.array([cx, -0.155, 0.693])
dm = np.linalg.norm((V0 - MOUTH_H) / [0.032, 0.03, 0.02], axis=1)
dn2 = np.linalg.norm((V0 - NOSE_H) / [0.024, 0.03, 0.03], axis=1)
soft_w = 1 - 0.85 * np.clip(1.6 - dm, 0, 1) - 0.8 * np.clip(1.5 - dn2, 0, 1)
soft_w = np.clip(soft_w, 0.12, 1) * (1 - 0.7 * blend)
for it, alpha in enumerate([40, 30, 20, 15, 12, 10]):
    n = vnormals(V)
    dist, j = tree.query(V, 1)
    ok = free & (np.einsum('ij,ij->i', n, TN[j]) > 0.3) & (dist < 30)
    wd = ok * soft_w
    wv = wd + fixed_w
    tv = np.where(ok[:, None], T[j], 0) * wd[:, None] + fixed_t * fixed_w[:, None]
    tv = np.where(wv[:, None] > 0, tv / np.maximum(wv, 1e-9)[:, None], 0)
    M = sp.diags(wv) + alpha * (L.T @ L)
    solve = factorized(M.tocsc())
    rhs = wv[:, None] * tv + alpha * (L.T @ (L @ Vref))
    V = np.stack([solve(rhs[:, k]) for k in range(3)], 1)
    print(it, alpha, ok.sum(), round(float(np.mean(dist[ok])), 2))

# the seam between the carried eye regions and the fitted skin: a few smoothing steps in a ring round each eye
ring = (dist_eye > 0.019) & (dist_eye < 0.034)
ring &= outer
for _ in range(30):
    V[ring] = V[ring] + 0.5 * ((A @ V)[ring] / deg[ring, None] - V[ring])

balls = {}
for k, s in ((0, 'L'), (1, 'R')):
    for part in ('sclera', 'iris'):
        Pt = d[part + s + '_v']
        if part == 'iris':
            Pt = Pt + np.array([0, -0.0024, 0])
        balls[part + s] = eye_carry(Pt, k)

np.savez(os.path.join(C, 'head_fit.npz'), v=V, f=Fpoly, tris=tris, v_init=Vref, low=low, ear=ear, eye_w=eye_w, mouth_in=mouth_in,
         eye_d=EYE_D, rb=RS * c_e, **{b + '_v': balls[b] for b in balls}, **{b + '_f': d[b + '_f'] for b in balls})

Tp = dr['pts'][::6]
pr = [[(Tp[:, [2, 1]] * [1, -1], '#f0c0a0', 0.6), (V[::2][:, [2, 1]] * [1, -1], '#333', 0.6),
       (balls['scleraL'][:, [2, 1]] * [1, -1], 'blue', 0.6)],
      [(Tp[:, [0, 1]] * [1, -1], '#f0c0a0', 0.6), (V[::2][:, [0, 1]] * [1, -1], '#333', 0.6),
       (np.vstack([balls['scleraL'], balls['scleraR']])[:, [0, 1]] * [1, -1], 'blue', 0.6)]]
dots.plot(pr, os.path.join(C, 'head_fit.png'), 700)
