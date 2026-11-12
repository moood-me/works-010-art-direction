"""Small mesh helpers: polygons, normals, adjacency, smoothing, boundary loops, and a plain software rasteriser for
quick looks (orthographic, Lambert) while fitting."""
import numpy as np
from scipy.sparse import coo_matrix, diags


def polys_of(fs, f):
    off = np.r_[0, np.cumsum(fs)]
    return [list(f[off[i]:off[i + 1]]) for i in range(len(fs))]


def triangulate(P):
    return np.array([[p[0], p[k], p[k + 1]] for p in P for k in range(1, len(p) - 1)], np.int64)


def vertex_normals(V, T):
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    N = np.zeros_like(V)
    for k in range(3): np.add.at(N, T[:, k], n)
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)


def adjacency(n, T):
    i = np.r_[T[:, 0], T[:, 1], T[:, 2], T[:, 1], T[:, 2], T[:, 0]]
    j = np.r_[T[:, 1], T[:, 2], T[:, 0], T[:, 0], T[:, 1], T[:, 2]]
    A = coo_matrix((np.ones(len(i)), (i, j)), shape=(n, n)).tocsr()
    A.data[:] = 1
    return A


def smooth(V, A, mask, iters=10, lam=0.5):
    """Laplacian smoothing of the vertices in mask (others fixed); mask may be weights 0..1."""
    w = np.asarray(mask, float)
    D = diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1))
    V = V.copy()
    for _ in range(iters):
        V += (lam * w)[:, None] * (D @ (A @ V) - V)
    return V


def boundary_loops(T):
    from collections import defaultdict
    cnt = defaultdict(int)
    for t in T:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): cnt[(a, b)] += 1
    nxt = {}
    for (a, b) in cnt:
        if (b, a) not in cnt: nxt[a] = b
    loops, seen = [], set()
    for s in nxt:
        if s in seen: continue
        L, c = [], s
        while c not in seen:
            seen.add(c); L.append(c); c = nxt[c]
        loops.append(L)
    return loops


def raster(V, T, yaw=0.0, size=600, box=None, col=None, light=(-0.5, 0.5, 0.7)):
    """Orthographic picture: yaw turns the camera round y (0: from the front, +z). Returns an RGB array and the box
    (x0, x1, y0, y1) in view units. col: per-vertex RGB 0..1 (default grey); Lambert shading."""
    c, s = np.cos(yaw), np.sin(yaw)
    X = V[:, 0] * c - V[:, 2] * s; Z = V[:, 0] * s + V[:, 2] * c; Y = V[:, 1]
    if box is None:
        x0, x1, y0, y1 = X.min(), X.max(), Y.min(), Y.max(); m = 0.05 * max(x1 - x0, y1 - y0)
        r = max(x1 - x0, y1 - y0) / 2 + m; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; box = (cx - r, cx + r, cy - r, cy + r)
    x0, x1, y0, y1 = box
    W = size; H = int(round(size * (y1 - y0) / (x1 - x0)))
    px = (X - x0) / (x1 - x0) * W; py = (y1 - Y) / (y1 - y0) * H
    N = vertex_normals(np.c_[X, Y, Z], T)
    L = np.array(light, float); L /= np.linalg.norm(L)
    sh = np.clip(N @ L, 0, 1) * 0.75 + 0.25
    if col is None: col = np.full((len(V), 3), 0.8)
    vc = col * sh[:, None]
    img = np.full((H, W, 3), 1.0); zb = np.full((H, W), -1e9)
    for t in T:
        a, b, d = t
        xs, ys = px[t], py[t]
        mnx, mxx = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
        mny, mxy = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
        if mnx > mxx or mny > mxy: continue
        gx, gy = np.meshgrid(np.arange(mnx, mxx + 1) + 0.5, np.arange(mny, mxy + 1) + 0.5)
        den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(den) < 1e-12: continue
        l0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / den
        l1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / den
        l2 = 1 - l0 - l1
        ins = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not ins.any(): continue
        z = l0 * Z[a] + l1 * Z[b] + l2 * Z[d]
        sub = zb[mny:mxy + 1, mnx:mxx + 1]
        upd = ins & (z > sub)
        sub[upd] = z[upd]
        im = img[mny:mxy + 1, mnx:mxx + 1]
        for k in range(3): im[..., k][upd] = (l0 * vc[a, k] + l1 * vc[b, k] + l2 * vc[d, k])[upd]
    return (np.clip(img, 0, 1) * 255).astype(np.uint8), box
