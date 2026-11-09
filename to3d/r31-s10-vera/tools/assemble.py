"""Put Вера's 3D pieces into one scene for render.py: scene.npz + scene.json.
Pieces (drawing units, the figure's frame): the fitted base head, its eyes, the drawing's hair cap and knot,
the face marks; with --body, the fitted Anny body and the clothes (body.py → body.npz).
usage: python3 assemble.py CACHE [--body]
"""
import sys, os, json
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meshes as M
import who
from scipy.interpolate import CubicSpline

C = sys.argv[1]
WITH_BODY = '--body' in sys.argv
K, FLOOR = who.K, who.FLOOR

d = np.load(os.path.join(C, 'drawing.npz'))
info = json.load(open(os.path.join(C, 'drawing.json')))
hf = np.load(os.path.join(C, 'head_fit.npz'))
col = info['colours']
SCLERA = os.environ.get('SCLERA', col['skin'])

objs, arrays = [], {}
DARK = '#4a1a14'
RIG = {}                    # name → (skin joints N×4, weights N×4) for the engine


def add(name, V, F, colour, **kw):
    arrays['obj_' + name + '_v'] = np.asarray(V, float)
    F = np.asarray(F)
    arrays['obj_' + name + '_f'] = F
    o = dict(name=name, colour=colour)
    o.update({k: v for k, v in kw.items() if k != 'fc'})
    if 'fc' in kw:
        arrays['obj_' + name + '_fc'] = np.asarray(kw['fc'])
    objs.append(o)


def grid(nu, nv):
    q = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a = i * nv + j
            q.append((a, a + nv, a + nv + 1, a + 1))
    return np.array(q)


if WITH_BODY:
    b = np.load(os.path.join(C, 'body.npz'))
    for name in b['names']:
        meta = json.loads(str(b[name + '_meta']))
        add(name, b[name + '_v'], b[name + '_f'], meta['colour'], **{k: v for k, v in meta.items() if k != 'colour'})
        RIG[name] = (b[name + '_sj'], b[name + '_sw'])
    # the base head's shoulders are cut off: its neck ends inside the blouse's collar
    F = np.asarray(hf['f'])
    low = np.asarray(hf['low'])
    keepf = ~low[np.maximum(F, 0)].any(1)
    # the mouth is drawn, as in the drawing (a line that opens into a dark shape: see the mouth pieces below), so
    # the base's lips are sealed: its mouth bag is cut away just behind the lips' edge and the edge drawn together
    hop = np.asarray(hf['hop'])
    keepf &= ~(np.where(F >= 0, hop[np.maximum(F, 0)], 0).max(1) > 2)
    F = F[keepf]
    # what is left of the bag as loose pieces goes too: only the largest connected piece of the head stays
    import scipy.sparse as sp
    from scipy.sparse.csgraph import connected_components
    ii, jj = [], []
    for fi, f in enumerate(F):
        f = [x for x in f if x >= 0]
        ii += f[1:]; jj += [f[0]] * (len(f) - 1)
    nvh = len(hf['v'])
    _, lab = connected_components(sp.coo_matrix((np.ones(len(ii)), (ii, jj)), shape=(nvh, nvh)), directed=False)
    main = np.bincount(lab[F[:, 0]]).argmax()
    F = F[lab[F[:, 0]] == main]
    Vh = np.asarray(hf['v']).copy()
    nb = [set() for _ in range(len(Vh))]
    for f in F:
        f = [x for x in f if x >= 0]
        for i in range(len(f)):
            nb[f[i]].add(f[i - 1]); nb[f[i - 1]].add(f[i])
    seal = [i for i in np.nonzero((hop == 1) | (hop == 2))[0] if nb[i]]
    for _ in range(40):
        Vh[seal] = [Vh[list(nb[i])].mean(0) for i in seal]
    hv_sealed = Vh
    # the lips: Freestyle draws there only the outer contour (render.py: face marks)
    cen = np.array([Vh[f[f >= 0]].mean(0) for f in F])
    MY = who.MOUTH_Y
    lips = (np.abs(cen[:, 0]) < 24) & (cen[:, 1] > MY - 7) & (cen[:, 1] < MY + 18) & (cen[:, 2] > 45)
    add('head', Vh, F, col['skin'], subsurf=1)
    arrays['obj_head_fm'] = lips.astype(np.uint8)
else:
    add('head', hf['v'], hf['f'], col['skin'], subsurf=1)
for s in 'LR':
    add('sclera' + s, hf['sclera' + s + '_v'], hf['sclera' + s + '_f'], SCLERA)
    add('iris' + s, hf['iris' + s + '_v'], hf['iris' + s + '_f'], '#1b1714', line=False)


class Surface:
    """Nearest point and normal on a mesh (by its vertices: dense enough here)."""
    def __init__(self, V, F):
        V = np.asarray(V, float)
        n = np.zeros_like(V)
        for f in F:
            f = [x for x in f if x >= 0]
            for i in range(1, len(f) - 1):
                a, b, c = V[f[0]], V[f[i]], V[f[i + 1]]
                fn = np.cross(b - a, c - a)
                for x in (f[0], f[i], f[i + 1]):
                    n[x] += fn
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        # outward: away from the head's middle axis
        mid = np.stack([np.zeros(len(V)), V[:, 1], np.full(len(V), -14.0)], 1)
        if np.mean(np.einsum('ij,ij->i', n, V - mid)) < 0:
            n = -n
        self.V, self.N, self.tree = V, n, cKDTree(V)

    def lift(self, P, d):
        """P put onto the surface and lifted d along its normal."""
        _, j = self.tree.query(P)
        k = min(8, len(self.V))
        dist, j = self.tree.query(P, k)              # a smooth blend of the nearby vertices' planes, not the nearest one
        w = np.exp(-(dist / (dist[:, :1] + 2.0)) ** 2)[..., None]
        n = (self.N[j] * w).sum(1); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        h = (np.einsum('ijk,ik->ij', self.V[j] - P[:, None], n)[..., None] * w).sum(1) / w.sum(1)
        return P + n * (h + d)

    def push_out(self, P, clear):
        """Points closer than `clear` outside the surface (or inside it) moved out to `clear`."""
        _, j = self.tree.query(P)
        sd = np.einsum('ij,ij->i', P - self.V[j], self.N[j])
        return P + self.N[j] * np.maximum(clear - sd, 0)[:, None]


skin = Surface(arrays['obj_head_v'], arrays['obj_head_f'])


def radial_clear(P, V, clear, skip):
    """Points moved out along rays from the head's axis (0, y, -14) to stay `clear` outside the head's vertices
    (a radius map over angle and height, the ears left out: they stand in front of the hair, as drawn)."""
    from scipy.ndimage import maximum_filter, gaussian_filter
    def polar(Q):
        a = np.arctan2(Q[:, 0], Q[:, 2] + 14)
        return a, Q[:, 1], np.hypot(Q[:, 0], Q[:, 2] + 14)
    a, y, r = polar(V[~skip])
    na, ny = 180, 120
    ia = ((a + np.pi) / (2 * np.pi) * na).astype(int) % na
    iy = np.clip(((y + 120) / 240 * ny).astype(int), 0, ny - 1)
    R = np.zeros((na, ny))
    np.maximum.at(R, (ia, iy), r)
    R = gaussian_filter(maximum_filter(R, size=3, mode='wrap'), 1.0, mode='wrap')
    pa, py, pr = polar(P)
    ja = ((pa + np.pi) / (2 * np.pi) * na).astype(int) % na
    jy = np.clip(((py + 120) / 240 * ny).astype(int), 0, ny - 1)
    need = R[ja, jy] + clear
    k = np.maximum(need / np.maximum(pr, 1e-6), 1.0)
    out = P.copy()
    out[:, 0] *= k
    out[:, 2] = (P[:, 2] + 14) * k - 14
    return out


hv0 = np.asarray(arrays['obj_head_v'])
hair_v = radial_clear(d['hair_v'], hv0, 2.0, hf['ear'])
hair_v, hair_q = M.compact(hair_v, np.asarray(d['hair_q']))
add('hair', hair_v, hair_q, col['hair'])
hair = Surface(hair_v, hair_q)
add('knot', d['knot_v'], d['knot_q'], col['hair'])


def shape_tris(n, group):
    """Triangles of a filled mark: a brow is a strip (top edge, then the bottom edge back); others a fan."""
    if group == 'brow' and n % 2 == 0:
        h = n // 2
        t = []
        for i in range(h - 1):
            a, b, c, e = i, i + 1, n - 2 - i, n - 1 - i
            t += [(a, b, c), (a, c, e)]
        return t
    return [(n, i, (i + 1) % n) for i in range(n)]       # fan about the centre (appended as the last point)


# the drawing's marks laid onto this 3D surface (they were drawn on the drawing's own surface, a little off ours)
marks = {}
for e, ms in info['marks'].items():
    out = []
    for mk in ms:
        P = np.array(mk['pts'], float)
        if mk['kind'] == 'line' and len(P) > 2 and mk['group'] != 'glasses':
            # the drawing draws a smooth curve through a few points: sampled densely, so it lies on the surface
            t = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
            P = CubicSpline(t, P)(np.linspace(0, t[-1], max(len(P), int(t[-1] / 2.5) + 2)))
        if mk['group'] != 'glasses':
            if mk['on'] == 'hair':
                P = hair.lift(P, 0.6)
            elif mk['on'] == 'stache':
                pass
            else:
                P = skin.lift(P, 0.9 if mk['kind'] == 'line' else 1.0)
        mk = dict(mk, pts=P.round(3).tolist())
        if mk['kind'] == 'shape':
            if not (mk['group'] == 'brow' and len(P) % 2 == 0):
                c = P.mean(0)
                mk['pts'] = P.round(3).tolist() + [c.round(3).tolist()]
                mk['outline'] = len(P)
            mk['tris'] = shape_tris(len(P), mk['group'])
        out.append(mk)
    marks[e] = out


# ------------------------------------------------------------------ the rig: everything on SOMA's joints
if WITH_BODY:
    import pack_engine
    J1 = b['joints']
    sk = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../engine/data/skeleton.json')))
    IDX = {j['name']: i for i, j in enumerate(sk['joints'])}

    def head_weights(V):
        """By height: the skull on Head; the neck handed down Head → Neck2 → Neck1 → Chest."""
        y = V[:, 1]
        keys = [(110, 'Head'), (152, 'Neck2'), (178, 'Neck1'), (215, 'Chest')]
        n = len(V)
        sj = np.zeros((n, 4), int); sw = np.zeros((n, 4))
        ys = np.array([k[0] for k in keys], float)
        i = np.clip(np.searchsorted(ys, y) - 1, 0, len(keys) - 2)
        t = np.clip((y - ys[i]) / (ys[i + 1] - ys[i]), 0, 1)
        sj[:, 0] = [IDX[keys[k][1]] for k in i]; sw[:, 0] = 1 - t
        sj[:, 1] = [IDX[keys[k + 1][1]] for k in i]; sw[:, 1] = t
        return sj, sw

    def rigid(V, name='Head'):
        sj = np.zeros((len(V), 4), int); sw = np.zeros((len(V), 4))
        sj[:, 0] = IDX[name]; sw[:, 0] = 1
        return sj, sw

    for o in objs:
        if o['name'] in RIG:
            continue
        V = arrays['obj_' + o['name'] + '_v']
        RIG[o['name']] = head_weights(V) if o['name'] == 'head' else rigid(V)
    # the face's marks, baked as ink geometry for moving pictures (render.py sets each tube's width for its picture)
    lw = float(os.environ.get('BAKE_LW', '2.2'))
    k = 0
    for mk in marks['calm']:
        # the 3D lids and eyes draw themselves; the mouth has its own pieces; the nose hook is for still fronts
        if mk['group'] in ('nose', 'mouth') or (mk['group'] == 'eye' and mk['kind'] == 'shape'):
            continue
        if mk['group'] == 'eye' and mk['w'] >= 1.3:          # the heavy lid stroke: the 3D lid's contour is it
            continue
        P = np.array(mk['pts'])
        r = (mk['w'] or 0) * lw / 2
        if mk['kind'] == 'shape' and mk.get('fill') not in (None, 'none'):
            T = np.array(mk['tris'])
            add(f'bm{k}', P, np.hstack([T, -np.ones((len(T), 1), int)]), mk['fill'], line=False, baked=True)
            RIG[f'bm{k}'] = rigid(P); k += 1
        if r > 0:
            Q = P[:mk.get('outline', len(P))]
            Vt, Ft = M.tube(Q, r, nseg=6, closed=mk['kind'] == 'shape')
            add(f'bm{k}', Vt, Ft, mk.get('stroke') or '#1b1714', line=False, baked=True,
                tube=[6, len(Q) + (1 if mk['kind'] == 'shape' else 0), mk['w']])
            RIG[f'bm{k}'] = rigid(Vt); k += 1
    # the mouth, drawn as the drawing draws it: one line when shut; when it opens the lower edge goes down with the
    # jaw and the line becomes the outline of a dark shape, with the teeth at the top and the tongue below.
    # Each vertex has an opening weight (0: stays with the upper lip, 1: goes with the jaw).
    OPEN = {}
    ml = [mk for mk in marks[who.MOUTH_FROM] if mk['group'] == 'mouth' and mk['kind'] == 'line']
    top = np.array(max(ml, key=lambda m: len(m['pts']))['pts'])
    t = np.r_[0, np.cumsum(np.linalg.norm(np.diff(top, axis=0), axis=1))]
    top = CubicSpline(t, top)(np.linspace(0, t[-1], 21))
    MOUTH_W = float(np.abs(top[:, 0]).max())
    n = len(top)
    prof = np.sin(np.pi * np.linspace(0, 1, n)) ** 0.7
    fwd = np.array([0, 0, 1.0])

    def band(name, a, b, w_top, w_bot, colour, lift):
        """A strip between the top line and the lower edge over points a..b of the mouth's line."""
        P = np.vstack([top[a:b], top[a:b]]) + fwd * lift
        m = b - a
        add(name, P, np.array([(i, i + 1, m + i + 1, m + i) for i in range(m - 1)]), colour, line=False, baked=True,
            smooth=False)
        RIG[name] = rigid(P)
        OPEN[name] = np.r_[w_top * prof[a:b], w_bot * prof[a:b]].round(3).tolist()
    band('mouthfill', 0, n, 0.0, 1.0, DARK, 0.0)
    band('mouthteeth', 2, n - 2, 0.0, 0.34, '#fffdf6', 0.25)
    band('mouthtongue', 5, n - 5, 0.6, 0.97, '#c8564a', 0.25)
    loop = np.vstack([top, top[::-1][1:-1]]) + fwd * 0.3
    Vt, Ft = M.tube(loop, lw / 2, nseg=6, closed=True)
    add('mouthline', Vt, Ft, '#1b1714', line=False, baked=True, tube=[6, len(loop) + 1, 1.0])
    RIG['mouthline'] = rigid(Vt)
    OPEN['mouthline'] = np.repeat(np.r_[0 * prof, prof[::-1][1:-1], 0.0], 6).round(3).tolist()
    for mk in marks[who.MOUTH_FROM]:                       # the small strokes by the mouth (corner ticks, the lower lip)
        if mk['group'] == 'mouth' and mk['kind'] == 'line' and len(mk['pts']) < 12:
            P = np.array(mk['pts'])
            Vt, Ft = M.tube(P, mk['w'] * lw / 2, nseg=6)
            add(f'bm{k}', Vt, Ft, '#1b1714', line=False, baked=True, tube=[6, len(P), mk['w']])
            RIG[f'bm{k}'] = rigid(Vt); k += 1
    pack_engine.write(C, objs, arrays, RIG, J1, K, FLOOR)
    # what the live face (face.mjs) needs: where its pieces are in the body's vertices, and the face's measures
    offs = json.load(open(os.path.join(C, 'engine/offsets.json')))
    json.dump(dict(K=K, floor=FLOOR, eyes=[np.asarray(hf['sclera' + s + '_v']).mean(0).tolist() for s in 'LR'],
                   rb=float(np.linalg.norm(hf['scleraL_v'] - np.asarray(hf['scleraL_v']).mean(0), axis=1).mean()),
                   mouthY=who.MOUTH_Y, mouthW=MOUTH_W, mouthZ=float(top[:, 2].mean()) - 3, open=OPEN, jaw=[0.0, 30.0, -25.0],
                   pieces={n: offs[n] for n in offs if n in ('head', 'irisL', 'irisR') or n in OPEN},
                   marks=[offs[n] for n in offs if n.startswith('bm')],
                   colours={o['name']: o.get('colours', [o['colour']]) for o in objs}),
              open(os.path.join(C, 'engine/face.json'), 'w'))

json.dump(dict(objects=objs, marks=marks, k=K, floor=FLOOR, skip=['pupil'], bake_lw=float(os.environ.get('BAKE_LW', '2.2'))), open(os.path.join(C, 'scene.json'), 'w'))
np.savez(os.path.join(C, 'scene.npz'), **arrays)
print(len(objs), 'objects')
