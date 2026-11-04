"""Put Савелий Петрович's 3D pieces into one scene for render.py: scene.npz + scene.json.
Pieces (drawing units, the figure's frame): the fitted base head, its eyes, the drawing's hair horseshoe and moustache,
the face marks; with --body, the fitted Anny body and the clothes (body.py → body.npz).
usage: python3 assemble.py CACHE [--body]
"""
import sys, os, json
import numpy as np
from scipy.spatial import cKDTree

C = sys.argv[1]
WITH_BODY = '--body' in sys.argv
K = 1.60 / 1114            # metres per drawing unit: the drawing's figure (crown to floor 1114 units) is 1.60 m
FLOOR = 1030.0

d = np.load(os.path.join(C, 'drawing.npz'))
info = json.load(open(os.path.join(C, 'drawing.json')))
hf = np.load(os.path.join(C, 'head_fit.npz'))
col = info['colours']
SCLERA = os.environ.get('SCLERA', col['skin'])

objs, arrays = [], {}


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
else:
    keep = ~hf['low']
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
        return self.V[j] + self.N[j] * (np.einsum('ij,ij->i', P - self.V[j], self.N[j]))[:, None] * 0 + self.N[j] * d

    def push_out(self, P, clear):
        """Points closer than `clear` outside the surface (or inside it) moved out to `clear`."""
        _, j = self.tree.query(P)
        sd = np.einsum('ij,ij->i', P - self.V[j], self.N[j])
        return P + self.N[j] * np.maximum(clear - sd, 0)[:, None]


skin = Surface(hf['v'], hf['f'])


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


hv0 = np.asarray(hf['v'])
hair_v = radial_clear(d['hair_v'], hv0, 2.0, hf['ear'])
add('hair', hair_v, d['hair_q'], col['hair'])
hair = Surface(hair_v, d['hair_q'])
staches = []
for k in (0, 1):
    P = d[f'stache{k}']
    n, m = d[f'stache{k}_nm']
    P = P[:n * m]
    add(f'stache{k}', P, grid(n, m), col['stache'], solidify=1.5)
    staches.append(P)
stache = cKDTree(np.vstack(staches))


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

json.dump(dict(objects=objs, marks=marks, k=K, floor=FLOOR, skip=['pupil']), open(os.path.join(C, 'scene.json'), 'w'))
np.savez(os.path.join(C, 'scene.npz'), **arrays)
print(len(objs), 'objects')
