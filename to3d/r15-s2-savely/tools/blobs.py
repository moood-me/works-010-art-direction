"""Big soft forms (a nose, a moustache, brows, a beard, curls, tufts) as smooth solids: balls strung on curves and
melted together (a smooth union of their distances), turned into a mesh by marching cubes. The Klaus drawing is made
of exactly such forms — each one flat shape with its own light — so in 3D each is one smooth solid.
Units are the caller's (head-view units or metres)."""
import numpy as np
from skimage import measure
import mesh as M


def chain(points, radii, n=24):
    """Balls along a polyline through points (Catmull-Rom), radii interpolated: (centres, radii)."""
    P = np.asarray(points, float); R = np.asarray(radii, float)
    if len(P) == 1: return P, R
    t = np.linspace(0, len(P) - 1, n)
    i = np.clip(np.floor(t).astype(int), 0, len(P) - 2); u = (t - i)[:, None]
    p0 = P[np.clip(i - 1, 0, len(P) - 1)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[np.clip(i + 2, 0, len(P) - 1)]
    C = 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
    return C, np.interp(t, np.arange(len(R)), R)


def solid(balls, k, cell, squash=None, pad=None, smooth=6):
    """balls: (centres N×3, radii N). k: how far neighbours melt together. squash: (sx, sy, sz) — the form is made
    in a space stretched by 1/s and brought back (a flatter form). Returns V, T (outward faces)."""
    C, R = np.asarray(balls[0], float), np.asarray(balls[1], float)
    s = np.ones(3) if squash is None else np.asarray(squash, float)
    c0 = C.mean(0)
    Cs = (C - c0) / s                       # the stretched space
    pad = pad or (R.max() / s.min() + 3 * cell + k)
    lo, hi = Cs.min(0) - pad, Cs.max(0) + pad
    ax = [np.arange(lo[i], hi[i] + cell, cell) for i in range(3)]
    G = np.stack(np.meshgrid(*ax, indexing='ij'), -1).reshape(-1, 3)
    acc = np.zeros(len(G))
    for c, r in zip(Cs, R):
        d = np.linalg.norm(G - c, axis=1) - r
        acc += np.exp(-np.clip(d / k, -50, 50))
    F = (-k * np.log(acc + 1e-300)).reshape([len(a) for a in ax])
    V, T, _, _ = measure.marching_cubes(F, 0.0, spacing=(cell,) * 3)
    V = V + lo
    T = T[:, ::-1].astype(np.int64)
    if smooth:
        V = M.smooth(V, M.adjacency(len(V), T), np.ones(len(V)), iters=smooth, lam=0.5)
    V = V * s + c0
    return V, outward(V, T)


def outward(V, T):
    """Faces turned so the closed surface's volume is positive (normals out)."""
    vol = np.einsum('ij,ij->i', V[T[:, 0]], np.cross(V[T[:, 1]], V[T[:, 2]])).sum()
    return T if vol > 0 else T[:, ::-1]


def mirror(points):
    P = np.asarray(points, float).copy(); P[:, 0] *= -1; return P


def tube(path, radius, n=10, closed=False, cap=True):
    """A tube along a path (radius a number, or per point; a pair = an ellipse (across, along the view))."""
    path = np.asarray(path, float); m = len(path)
    rad = np.broadcast_to(np.asarray(radius, float), (m,) + np.shape(radius)[1:]) if np.ndim(radius) else np.full(m, radius)
    V, T = [], []
    u_prev = None
    for i, p in enumerate(path):
        a = path[(i + 1) % m] if closed else path[min(i + 1, m - 1)]
        b = path[(i - 1) % m] if closed else path[max(i - 1, 0)]
        d = a - b; d /= np.linalg.norm(d) + 1e-12
        if u_prev is None:
            u = np.cross(d, [0, 1.0, 0]) if abs(d[1]) < 0.9 else np.cross(d, [1.0, 0, 0])
        else: u = u_prev - d * (u_prev @ d)
        u /= np.linalg.norm(u) + 1e-12; u_prev = u
        w = np.cross(d, u)
        r = rad[i]; ru, rw = (r if np.ndim(r) else (r, r))
        for k in range(n):
            an = 2 * np.pi * k / n
            V.append(p + u * np.cos(an) * ru + w * np.sin(an) * rw)
    for i in range(m if closed else m - 1):
        for k in range(n):
            a0, a1 = i * n + k, i * n + (k + 1) % n; b0, b1 = ((i + 1) % m) * n + k, ((i + 1) % m) * n + (k + 1) % n
            T += [[a0, a1, b0], [a1, b1, b0]]
    if cap and not closed:
        V.append(path[0]); V.append(path[-1]); c0, c1 = len(V) - 2, len(V) - 1
        for k in range(n):
            T.append([c0, (k + 1) % n, k]); T.append([c1, (m - 1) * n + k, (m - 1) * n + (k + 1) % n])
    V, T = np.array(V), np.array(T)
    nrm = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    ctr = np.repeat(path, n, 0)
    cc = np.r_[ctr, path[:1], path[-1:]] if (cap and not closed) else ctr
    if (nrm * (V[T].mean(1) - cc[T].mean(1))).sum() < 0: T = T[:, ::-1]
    return V, T


def join(parts):
    """[(V, T), …] → one (V, T)."""
    Vs, Ts, base = [], [], 0
    for V, T in parts:
        Vs.append(V); Ts.append(T + base); base += len(V)
    return np.concatenate(Vs), np.concatenate(Ts)
