"""Аня (С12, pen and watercolour) in 3D: the pack the drawing renderer (web/anya.js, web/pen.js) takes.
  python3 build.py [outdir]

The form is Р1's Аня (to3d/r1-s3-anya: Anny's body and SOMA skeleton, Blender's Human Base Meshes stylised head,
the dress, cardigan, sleeves, mittens and hair built from that drawing's silhouettes) — the same girl in the same
clothes; here it is reshaped to the С12 drawing (head, nose, hair longer and wavy, the dress's V neckline instead of a
collar, bare legs) and given what a pen-and-wash renderer needs instead of a material:
  grp      — which watercolour wash a vertex belongs to (skin, hair, cardigan, dress, shoes)
  edges    — every mesh edge once, with its one or two triangles (silhouettes and open edges are found from them)
  faceTri, faceBar — the drawing's front face grid (С12 head_front units) laid on the head: for each grid node the
             head triangle it lies on and where; the face is drawn on the 3D through it every frame
  strokes  — lines that belong to the form, drawn when visible: locks of hair, folds of the skirt
"""
import os, sys, json
import numpy as np
import pack, mesh as M

HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.join(HERE, '..', '..', 'r1-s3-anya', 'data', 'anya.json')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data')
os.makedirs(OUT, exist_ok=True)
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))

h, a = pack.load(R1)
P = a['positions'].reshape(-1, 3).astype(np.float64).copy()
T = a['triangles'].reshape(-1, 3).astype(np.int64)
pieces = {k: list(v) for k, v in h['pieces'].items()}
tpieces = {k: list(v) for k, v in h['trianglePieces'].items()}

# ---------------------------------------------------------------- the collar goes (С12: the dress's V neckline)
c0, c1 = pieces.pop('collar'); t0, t1 = tpieces.pop('collar')
keepv = np.r_[0:c0, c1:len(P)]; keept = np.r_[0:t0, t1:len(T)]
nc, ntc = c1 - c0, t1 - t0
P = P[keepv]; T = T[keept]; T = np.where(T >= c1, T - nc, T)
arr = {k: v.reshape(len(a['positions']) // 3, -1)[keepv] if k not in ('triangles', 'joints', 'frames', 'positions') else v
       for k, v in a.items()}
for k, (s, e) in list(pieces.items()):
    if s >= c1: pieces[k] = [s - nc, e - nc]
for k, (s, e) in list(tpieces.items()):
    if s >= t1: tpieces[k] = [s - ntc, e - ntc]
N = len(P)
band = arr['band'].reshape(-1).copy()
SJ = arr['skinJoints'].reshape(N, 4); SW = arr['skinWeights'].reshape(N, 4)
pid = np.zeros(N, np.uint8); PN = list(pieces)
for i, k in enumerate(PN): pid[pieces[k][0]:pieces[k][1]] = i
sl = lambda k: slice(*pieces[k])

sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}

# ---------------------------------------------------------------- the head: С12's face is rounder below, the nose a
# little longer and sharper (the nose is the face's main mark in the drawing and the pen draws it as a contour)
H = sl('head'); hv = P[H]
uv = arr['uv'][H]
fx = (uv[:, 0] * 240 - 120)            # Р1's face layer units (eyes at x ±36, y 0; mouth y 76)
fy = (1 - uv[:, 1]) * 260 - 130
front = hv[:, 2] > 0.0
# nose: forward and a touch down at its tip
wn = np.exp(-((fx / 13) ** 2) - ((fy - 40) / 16) ** 2) * front * smooth((hv[:, 2] - 0.05) / 0.03)
hv[:, 2] += 0.010 * wn
hv[:, 1] -= 0.002 * wn
# the cheeks and the lower face a little fuller and rounder (С12's three-quarter face is round under the cheek)
wc = np.exp(-(((np.abs(fx) - 52) / 26) ** 2) - ((fy - 62) / 34) ** 2) * (hv[:, 2] > -0.02)
nh = M.vertex_normals(hv, T[slice(*tpieces['head'])] - pieces['head'][0])
hv += nh * (0.004 * wc)[:, None]
P[H] = hv

# ---------------------------------------------------------------- hair: С12's hair is longer, in loose waves
HR = sl('hair'); hp = P[HR].reshape(150, 110, 3)
rows, cols = 150, 110
v = np.linspace(0, 1, rows)[:, None]
yy = hp[:, :, 1]
below = smooth((1.30 - yy) / 0.12)                     # from the shoulders down: longer, waves
hp[:, :, 1] -= 0.10 * below * smooth((1.24 - yy) / 0.2)
th = np.linspace(0, 1, cols)[None, :]
wave = np.sin((1.40 - yy) * 26 + th * 3.0) * 0.006 * below
rad = np.stack([hp[:, :, 0], np.zeros_like(yy), hp[:, :, 2] + 0.02], -1)
rad /= np.linalg.norm(rad, axis=-1, keepdims=True) + 1e-9
hp += rad * wave[:, :, None]
P[HR] = hp.reshape(-1, 3)

# ---------------------------------------------------------------- wash groups
G = dict(skin=1, hair=2, card=3, dress=4, shoe=5)
grp = np.full(N, G['skin'], np.uint8)
grp[sl('hair')] = G['hair']
for k in ('cardigan', 'sleeveLeft', 'sleeveRight'): grp[sl(k)] = G['card']
grp[sl('dress')] = G['dress']
band[sl('body')] = np.where(band[sl('body')] < 0.0, -1, band[sl('body')])

# ---------------------------------------------------------------- edges: each once, with its triangles
e = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
f = np.tile(np.arange(len(T)), 3)
key = np.sort(e, 1); o = np.lexsort((key[:, 1], key[:, 0])); key, f = key[o], f[o]
first = np.r_[True, (key[1:] != key[:-1]).any(1)]
idx = np.flatnonzero(first); cnt = np.diff(np.r_[idx, len(key)])
E = key[idx]
F0 = f[idx]; F1 = np.where(cnt >= 2, f[np.minimum(idx + 1, len(f) - 1)], -1)
print('edges', len(E), 'open', (F1 < 0).sum(), 'more than two', (cnt > 2).sum())
# open edges that are not drawn: the inner rims of the eyes and the mouth's fold (the face is drawn), hair's top seam
hd0, hd1 = pieces['head']
drop = np.zeros(len(E), bool)
inhead = (E[:, 0] >= hd0) & (E[:, 0] < hd1)
drop |= inhead & (F1 < 0)                                         # the head's own holes (eyes, the neck's end)
# the eyes' and the mouth's regions (Р1 flattened them onto one surface; the face is drawn there, not contoured)
mid = (E[:, 0] - hd0).clip(0, hd1 - hd0 - 1)
ex = (arr['uv'][E[:, 0], 0] * 240 - 120); ey = (1 - arr['uv'][E[:, 0], 1]) * 260 - 130
for cx, cy, rx, ry in [(36, -2, 30, 34), (-36, -2, 30, 34), (0, 72, 28, 10)]:
    drop |= inhead & ((((ex - cx) / (rx * 1.15)) ** 2 + ((ey - cy) / (ry * 1.15)) ** 2) < 1) & (P[E[:, 0], 2] > 0.02)

# ---------------------------------------------------------------- the face grid on the head (front projection)
thi = np.arange(*tpieces['head'])
thi = thi[((T[thi] < hd1) & (T[thi] >= hd0)).all(1)]
TH = T[thi]
# where the face's features are on the head (Р1's face layer: eyes ±36,0; mouth 0,76)
def at(x, y):
    m = front & (hv[:, 2] > 0.03)
    d = (fx - x) ** 2 + (fy - y) ** 2; d[~m] = 1e9
    return hv[np.argmin(d)]
eyeL, eyeR, mth = at(36, 0), at(-36, 0), at(0, 76)
# С12's head_front units: eyes (±28, −4), mouth (2, 54): an affine from those to the head's front plane
sx = (eyeL[0] - eyeR[0]) / 56.0
sy = ((eyeL[1] + eyeR[1]) / 2 - mth[1]) / 58.0
ox = 0.0; oy = (eyeL[1] + eyeR[1]) / 2 + sy * -4
GX = np.arange(-84, 85, 3.0); GY = np.arange(-96, 112, 3.0)
gx, gy = np.meshgrid(GX, GY)
qx = ox + gx * sx; qy = oy - gy * sy
q = np.c_[qx.ravel(), qy.ravel()]
faceTri = -np.ones(len(q), np.int64); faceBar = np.zeros((len(q), 3)); best = np.full(len(q), -1e9)
A3, B3, C3 = P[TH[:, 0]], P[TH[:, 1]], P[TH[:, 2]]
for ti in range(len(TH)):
    a2, b2, c2 = A3[ti, :2], B3[ti, :2], C3[ti, :2]
    lo = np.minimum(np.minimum(a2, b2), c2); hi = np.maximum(np.maximum(a2, b2), c2)
    m = np.flatnonzero((q[:, 0] >= lo[0]) & (q[:, 0] <= hi[0]) & (q[:, 1] >= lo[1]) & (q[:, 1] <= hi[1]))
    if not len(m): continue
    v0, v1 = b2 - a2, c2 - a2; den = v0[0] * v1[1] - v1[0] * v0[1]
    if abs(den) < 1e-14: continue
    w = q[m] - a2
    l1 = (w[:, 0] * v1[1] - v1[0] * w[:, 1]) / den; l2 = (v0[0] * w[:, 1] - w[:, 0] * v0[1]) / den; l0 = 1 - l1 - l2
    ok = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
    m, l0, l1, l2 = m[ok], l0[ok], l1[ok], l2[ok]
    z = l0 * A3[ti, 2] + l1 * B3[ti, 2] + l2 * C3[ti, 2]
    nz = np.cross(B3[ti] - A3[ti], C3[ti] - A3[ti])[2]
    better = (z > best[m]) & (nz > 0)
    m, z = m[better], z[better]
    best[m] = z; faceTri[m] = thi[ti]
    faceBar[m] = np.c_[l0[better], l1[better], l2[better]]
print('face grid', len(q), 'on the head', (faceTri >= 0).sum())

# ---------------------------------------------------------------- strokes that belong to the form
strokes = []
rng = np.random.default_rng(12)
# hair: a few long locks down the hair (columns of its grid), and short ones; not on the face's window edge
for c in [8, 18, 27, 40, 55, 62, 70, 83, 92, 101]:
    r0 = int(rng.integers(4, 30)); r1 = int(rng.integers(105, 149))
    strokes.append(dict(kind='hair', w=0.9, v=[int(pieces['hair'][0] + r * cols + c) for r in range(r0, r1, 2)]))
for c in [12, 34, 48, 77, 97]:
    r0 = int(rng.integers(70, 100)); r1 = min(149, r0 + int(rng.integers(20, 40)))
    strokes.append(dict(kind='hair', w=0.8, v=[int(pieces['hair'][0] + r * cols + c) for r in range(r0, r1, 2)]))
# the skirt's folds: three soft lines in front, two behind, from the knee down (the dress is rings of 72)
d0, d1 = pieces['dress']; drows = (d1 - d0) // 72
dy = P[d0:d1:72, 1]
rk = int(np.argmin(np.abs(dy - 0.62)))
for c in [5, 67, 0, 30, 42]:
    strokes.append(dict(kind='fold', w=0.9, v=[int(d0 + r * 72 + c) for r in range(rk, drows - 2, 2)]))
# the cardigan: two buttons on its left front edge
k0, k1 = pieces['cardigan']; kcols = 64
krows = (k1 - k0) // kcols
by = P[k0:k1:kcols, 1]
buttons = [int(k0 + int(np.argmin(np.abs(by - y))) * kcols + 2) for y in (1.11, 1.02)]

# ---------------------------------------------------------------- the pack
header = dict(format='r12/character', version=1, id='anya-s12', label={'ru': 'Аня, перо и акварель'},
              skinning='cor', source='Р1 Аня (Anny moood-woman + Human Base Meshes stylised head + shells) reshaped to С12',
              pieces=pieces, trianglePieces=tpieces, pieceNames=PN, groups=G,
              face=dict(gx=[float(GX[0]), 3.0, len(GX)], gy=[float(GY[0]), 3.0, len(GY)]),
              strokes=strokes, buttons=buttons)
pack.save(os.path.join(OUT, 'anya.json'), header, dict(
    positions=P.astype(np.float32).ravel(), triangles=T.astype(np.uint32).ravel(),
    skinJoints=SJ.astype(np.uint8), skinWeights=SW.astype(np.float32),
    joints=a['joints'].astype(np.float32), frames=a['frames'].astype(np.float32),
    band=band.astype(np.float32), grp=grp, pid=pid,
    edges=E.astype(np.uint32).ravel(), edgeTris=np.where(np.c_[F0, F1] < 0, 0xFFFFFFFF, np.c_[F0, F1]).astype(np.uint32).ravel(), edgeDrop=drop.astype(np.uint8),
    faceTri=np.where(faceTri < 0, 0xFFFFFFFF, faceTri).astype(np.uint32), faceBar=faceBar.astype(np.float32).ravel()))
print('saved', OUT, N, 'vertices', len(T), 'triangles')
