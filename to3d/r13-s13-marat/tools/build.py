"""Марат (С13, woodblock print) in 3D: the pack the print's renderer (web/marat.js, web/print.js) takes.
  python3 build.py [outdir]        (after form.py)

To the form (form.py) it adds what a print needs instead of a material:
  grp      — which colour block a vertex is printed by (skin, black, white, terracotta, checks, towel, shoes)
  puv      — the cloth's own flat coordinates, for the patterns printed on it (waves on the apron, checks, stripes)
  bok      — bokashi: how much of the block's second colour is wiped on there (0…1)
  edges    — every mesh edge once with its triangles (silhouettes and open edges are found from them each frame)
  inner    — where a silhouette inside one colour is a line of the drawing (not on the face, except the nose and ears)
  faceTri, faceBar — the drawing's front face grid (head units) laid on the head and the beard: the face is drawn
             through it every frame
  strokes, marks — lines and signs that belong to the form: the apron's folds and waist, the jacket's front edge,
             the buttons, the small hooks of the curls"""
import os, sys
import numpy as np
import pack, drawing as D

HERE = os.path.dirname(os.path.abspath(__file__))
FORM = '/home/user/cache/to3d-r13-s13-marat/form/marat.json'
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data')
os.makedirs(OUT, exist_ok=True)
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))
K = D.K

h, a = pack.load(FORM)
P = a['positions'].reshape(-1, 3).astype(np.float64)
T = a['triangles'].reshape(-1, 3).astype(np.int64)
pieces, tpieces = h['pieces'], h['trianglePieces']
N = len(P); PN = list(pieces)
pid = np.zeros(N, np.uint8)
for i, k in enumerate(PN): pid[pieces[k][0]:pieces[k][1]] = i
sl = lambda k: slice(*pieces[k])

# ---------------------------------------------------------------- colour blocks
G = dict(skin=1, black=2, white=3, terra=4, checks=5, towel=6, shoe=7)
OF = dict(arms='skin', head='skin', beard='black', hair='black', jacket='white', collar='white', sleeveLeft='white',
          sleeveRight='white', apron='terra', strapLeft='terra', strapRight='terra', legs='checks', towel='towel',
          shoeLeft='shoe', shoeRight='shoe')
grp = np.zeros(N, np.uint8)
for k in PN: grp[sl(k)] = G[OF[k]]
puv = a['uv'].reshape(N, 2).astype(np.float32).copy()
bok = np.zeros(N)
y = P[:, 1]
bok[sl('apron')] = smooth((0.80 - y[sl('apron')]) / 0.5)                    # the apron deepens toward its hem
bok[sl('jacket')] = 0.8 * smooth((1.02 - y[sl('jacket')]) / 0.22)           # a grey wiped along the jacket's hem
bok[sl('legs')] = 0.9 * smooth((0.34 - y[sl('legs')]) / 0.26)               # the trousers darken to the shoes
for s in ('Left', 'Right'):
    v = P[sl('sleeve' + s)]; c = v.mean(0)
    bok[sl('sleeve' + s)] = 0.0

# the cheeks' blush (parts.head: a round bokashi at (±46, 36), r 28 hu, on the face's front): how far from its centre
blu = np.full(N, 9.0)
hv_ = P[sl('head')]; bx, by = hv_[:, 0] / K, (D.EYE - hv_[:, 1]) / K
blu[sl('head')] = np.where(hv_[:, 2] > 0.0, np.minimum(np.hypot(bx - 46, by - 36), np.hypot(bx + 46, by - 36)) / 28, 9.0)

# ---------------------------------------------------------------- edges
e = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
f = np.tile(np.arange(len(T)), 3)
key = np.sort(e, 1); o = np.lexsort((key[:, 1], key[:, 0])); key, f = key[o], f[o]
first = np.r_[True, (key[1:] != key[:-1]).any(1)]
idx = np.flatnonzero(first); cnt = np.diff(np.r_[idx, len(key)])
E = key[idx]
F0 = f[idx]; F1 = np.where(cnt >= 2, f[np.minimum(idx + 1, len(f) - 1)], -1)
print('edges', len(E), 'open', (F1 < 0).sum(), 'more than two', (cnt > 2).sum())
ep = pid[E[:, 0]]
drop = np.zeros(len(E), bool)
for k in ('head', 'arms'): drop |= (ep == PN.index(k)) & (F1 < 0)
drop |= (ep == PN.index('legs')) & (F1 < 0) & (P[E[:, 0], 1] > 0.5)     # the bases' own holes and cut ends
for k in ('strapLeft', 'strapRight'): drop |= ep == PN.index(k)               # a strap is a band of colour, no line
drop |= (ep == PN.index('hair')) & (F1 >= 0) & False

# the head in head units
H = sl('head'); hv = P[H]
hx, hy, hz = hv[:, 0] / K, (D.EYE - hv[:, 1]) / K, hv[:, 2]
inner = np.ones(N, np.uint8)
face_area = (hz > -0.02) & (hy > -75) & (hy < 110) & (np.abs(hx) < 74)
nose = (np.abs(hx) < 17) & (hy > 6) & (hy < 52)
inner[H] = np.where(face_area, np.where(nose, 2, 0), 1)
# the eyes' and the mouth's regions of the base: no lines there at all (the face is drawn)
hd0, hd1 = pieces['head']
inhead = (E[:, 0] >= hd0) & (E[:, 0] < hd1)
ex, ey = P[E[:, 0], 0] / K, (D.EYE - P[E[:, 0], 1]) / K
for cx, cy, rx, ry in [(33, 0, 27, 19), (-33, 0, 27, 19), (0, 66, 34, 18)]:
    drop |= inhead & ((((ex - cx) / rx) ** 2 + ((ey - cy) / ry) ** 2) < 1) & (P[E[:, 0], 2] > 0.02)

# ---------------------------------------------------------------- the face grid on the head and the beard
thi = np.r_[np.arange(*tpieces['head']), np.arange(*tpieces['beard'])]
TH = T[thi]
GX = np.arange(-96, 97, 3.0); GY = np.arange(-78, 136, 3.0)
gx, gy = np.meshgrid(GX, GY)
q = np.c_[(gx * K).ravel(), (D.EYE - gy * K).ravel()]
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
    better = z > best[m]
    m, z = m[better], z[better]
    best[m] = z; faceTri[m] = thi[ti]
    faceBar[m] = np.c_[l0[better], l1[better], l2[better]]
print('face grid', len(q), 'on the head', (faceTri >= 0).sum())

# ---------------------------------------------------------------- lines and signs that belong to the form
strokes, marks = [], []
ar, ac = h['grids']['apron']; a0 = pieces['apron'][0]
ay = P[a0:a0 + ar * ac:ac, 1]
rw = int(np.argmin(np.abs(ay - 1.115)))
strokes.append(dict(kind='waist', w=5.0, color='terraD', prof='swell', v=[int(a0 + rw * ac + c) for c in range(1, ac - 1)]))
for c, r1 in ((9, ar - 2), (20, ar - 2), (30, ar - 3)):
    strokes.append(dict(kind='fold', w=3.0, color='terraD', prof='taper', v=[int(a0 + r * ac + c + (1 if (r - rw) > 12 and c != 20 else 0)) for r in range(rw + 1, r1)]))
jr, jc = h['grids']['jacket']; j0 = pieces['jacket'][0]
jy = P[j0:j0 + jr * jc:jc, 1]
strokes.append(dict(kind='seam', w=3.0, color='ink', prof='taper', v=[int(j0 + r * jc + (1 if r % 2 else 0) * 0) for r in range(8, int(np.argmin(np.abs(jy - 1.40))) + 1)]))
J = P[sl('jacket')]
for bx in (-0.075, 0.075):
    marks.append(dict(kind='button', v=int(j0 + np.argmin(np.where(J[:, 2] > 0, (J[:, 0] - bx) ** 2 + (J[:, 1] - 1.475) ** 2, 9)))))
# the curls' small hooks: one on some of the lumps (form.py: lumps), at its top
Hv = P[sl('hair')]; hc = np.array(h['hairCentre']); hd = Hv - hc; hd /= np.linalg.norm(hd, axis=1, keepdims=True)
rng = np.random.default_rng(5)
for L in a['lumps'].reshape(-1, 3):
    i = int(np.argmax(hd @ L))
    if hd[i] @ L > 0.995 and rng.random() < 0.62: marks.append(dict(kind='curl', v=int(pieces['hair'][0] + i)))
print('strokes', len(strokes), 'marks', len(marks))

header = dict(format='r13/character', version=1, id='marat-s13', label={'ru': 'Марат, укиё-э'}, skinning='cor',
              source=h['source'], pieces=pieces, trianglePieces=tpieces, pieceNames=PN, groups=G, grids=h['grids'],
              face=dict(gx=[float(GX[0]), 3.0, len(GX)], gy=[float(GY[0]), 3.0, len(GY)], k=K, eye=D.EYE),
              strokes=strokes, marks=marks)
pack.save(os.path.join(OUT, 'marat.json'), header, dict(
    positions=P.astype(np.float32).ravel(), triangles=T.astype(np.uint32).ravel(),
    skinJoints=a['skinJoints'].reshape(N, 4).astype(np.uint8), skinWeights=a['skinWeights'].reshape(N, 4).astype(np.float32),
    joints=a['joints'].astype(np.float32), frames=a['frames'].astype(np.float32),
    grp=grp, pid=pid, puv=puv.ravel(), blu=np.clip(blu, 0, 2).astype(np.float32), bok=(np.clip(bok, 0, 1) * 255).astype(np.uint8),
    edges=E.astype(np.uint32).ravel(), edgeTris=np.where(np.c_[F0, F1] < 0, 0xFFFFFFFF, np.c_[F0, F1]).astype(np.uint32).ravel(),
    edgeDrop=drop.astype(np.uint8), inner=inner,
    faceTri=np.where(faceTri < 0, 0xFFFFFFFF, faceTri).astype(np.uint32), faceBar=faceBar.astype(np.float32).ravel()))
print('saved', OUT, N, 'vertices', len(T), 'triangles')
