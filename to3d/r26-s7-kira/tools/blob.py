"""Soft joined solids: a few simple forms (tubes with a radius per point, a loft of rings) given as distance fields,
joined with a smooth minimum and turned into one mesh by marching cubes — trousers (the pelvis and both legs as one
piece, as the drawing fills them as one shape), boots (foot and shaft), a hood's roll, headphone cups.
Centimetres in, metres out."""
import numpy as np
from skimage import measure


def smin(a, b, k):
    if k <= 0: return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)


def tube(path, radii):
    """a chain of segments, the radius changing along it (round ends)."""
    path = np.asarray(path, float); radii = np.asarray(radii, float)

    def f(P):
        d = np.full(len(P), 1e9)
        for a, b, ra, rb in zip(path[:-1], path[1:], radii[:-1], radii[1:]):
            ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab + 1e-12), 0, 1)
            d = np.minimum(d, np.linalg.norm(P - (a + t[:, None] * ab), axis=1) - (ra + t * (rb - ra)))
        return d
    f.box = (path.min(0) - radii.max(), path.max(0) + radii.max())
    return f


def loft(lo, y0, y1, push=0.0):
    """a body.Loft between two heights; push: a number or a function of y (cm)."""
    pf = push if callable(push) else (lambda y: push)
    ys = np.linspace(y0, y1, 80)
    T = np.array([lo.at(y) for y in ys]); ps = np.array([pf(y) for y in ys])

    def f(P):
        y = np.clip(P[:, 1], y0, y1)
        a, zf, zb, x0, z0 = (np.interp(y, ys, T[:, i]) for i in range(5)); p = np.interp(y, ys, ps)
        a = a + p; zm = (zf + zb) / 2 + z0; d = (zf - zb) / 2 + p
        r = (np.abs((P[:, 0] - x0) / a) ** lo.n + np.abs((P[:, 2] - zm) / d) ** lo.n) ** (1 / lo.n)
        side = (r - 1) * np.minimum(a, d)
        return np.maximum(side, np.maximum(y0 - P[:, 1], P[:, 1] - y1))
    amax = T[:, 0].max() + ps.max() + abs(T[:, 3]).max()
    f.box = (np.array([-amax, y0, (T[:, 2] + T[:, 4]).min() - ps.max()]), np.array([amax, y1, (T[:, 1] + T[:, 4]).max() + ps.max()]))
    return f


def join(fs, k):
    def f(P):
        d = fs[0](P)
        for g in fs[1:]: d = smin(d, g(P), k)
        return d
    f.box = (np.min([g.box[0] for g in fs], 0), np.max([g.box[1] for g in fs], 0))
    return f


def above(f, y):
    """only what is above the height y (a flat cut)."""
    def g(P): return np.maximum(f(P), y - P[:, 1])
    g.box = f.box
    return g


def below(f, y):
    def g(P): return np.maximum(f(P), P[:, 1] - y)
    g.box = f.box
    return g


def grow(f, r):
    def g(P): return f(P) - r
    g.box = (f.box[0] - r, f.box[1] + r)
    return g


def mesh(f, h=0.7):
    """→ vertices (metres), triangles facing out."""
    lo, hi = f.box[0] - 2 * h, f.box[1] + 2 * h
    ax = [np.arange(lo[i], hi[i] + h, h) for i in range(3)]
    G = np.stack(np.meshgrid(*ax, indexing='ij'), -1).reshape(-1, 3)
    D = np.concatenate([f(G[i:i + 400000]) for i in range(0, len(G), 400000)]).reshape([len(a) for a in ax])
    V, T, _, _ = measure.marching_cubes(D, 0.0, spacing=(h, h, h))
    V = V + lo
    T = T.astype(np.int64)
    # outward: the signed volume positive
    vol = np.einsum('ij,ij->i', V[T[:, 0]], np.cross(V[T[:, 1]], V[T[:, 2]])).sum()
    if vol < 0: T = T[:, ::-1]
    return V * 0.01, T
