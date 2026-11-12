"""The head's base: Blender's Human Base Meshes stylised head (CC0), its eye sockets and lips closed with a smooth
patch (in the Klaus style eyes and mouth are painted), then fitted to the character by points (after Р5's head.py):
heights go by landmarks, and at many heights the base's silhouette points (side, face, the middle line's front and
back) are taken to the wanted outline; the whole head follows by a smooth map (RBF), a few passes.
Frame: x to the character's left, y up, z forward; "head units" are the drawing's units, y down."""
import numpy as np
import mesh as M

C0 = 2.082951545715332
# base landmarks (metres in the base's frame): neck bottom, chin, under the lip, mouth, nose tip, eyes, brow, crown
BASE_Y = [0.513, 0.578, 0.600, 0.645, 0.680, 0.729, 0.760, 0.888]
CUTS = [(0.046, 0.729, 0.036, 0.032, 0.0), (-0.046, 0.729, 0.036, 0.032, 0.0), (0.0, 0.640, 0.040, 0.022, 0.03)]


def conv(v): return np.c_[v[:, 0] - C0, v[:, 2], -v[:, 1]]


def load(path):
    d = np.load(path)
    return conv(d['head_v']), M.polys_of(d['head_fs'], d['head_f'])


def fill(v, P, loop, rings=5):
    v = list(v); c = np.mean([v[i] for i in loop], 0); n = len(loop); prev = list(loop)
    for r in range(1, rings + 1):
        t = r / (rings + 1); cur = []
        for i in loop: v.append(v[i] * (1 - t) + c * t); cur.append(len(v) - 1)
        for k in range(n): P.append([prev[k], prev[(k + 1) % n], cur[(k + 1) % n], cur[k]])
        prev = cur
    v.append(c); ci = len(v) - 1
    for k in range(n): P.append([prev[k], prev[(k + 1) % n], ci])
    return np.array(v), P


def compact(v, P):
    used = sorted(set(i for p in P for i in p)); m = -np.ones(len(v), int); m[used] = np.arange(len(used))
    return v[used], [[int(m[i]) for i in p] for p in P], m


def largest_part(P):
    from scipy.sparse.csgraph import connected_components
    from scipy.sparse import coo_matrix
    T = M.triangulate(P); n = T.max() + 1
    A = coo_matrix((np.ones(len(T) * 2), (np.r_[T[:, 0], T[:, 1]], np.r_[T[:, 1], T[:, 2]])), shape=(n, n))
    _, lab = connected_components(A, directed=False)
    big = np.bincount(lab[T[:, 0]]).argmax()
    return [p for p in P if lab[p[0]] == big]


def biharmonic(v, P, free):
    from scipy.sparse import diags
    from scipy.sparse.linalg import spsolve
    T = M.triangulate(P); A = M.adjacency(len(v), T)
    L = diags(np.asarray(A.sum(1)).ravel()) - A
    L2 = (L.T @ L).tocsr()
    f = np.where(free)[0]; k = np.where(~free)[0]
    Aff = L2[f][:, f]; Afk = L2[f][:, k]
    v = v.copy()
    for c in range(3): v[f, c] = spsolve(Aff.tocsc(), -Afk @ v[k, c])
    return v


def blank(v, P):
    """Eye sockets and lips cut out by ellipses in the front view; the holes filled with a bi-harmonic patch."""
    ins = np.zeros(len(v), bool)
    for cx, cy, rx, ry, zmin in CUTS:
        ins |= (((v[:, 0] - cx) / rx) ** 2 + ((v[:, 1] - cy) / ry) ** 2 < 1) & (v[:, 2] > zmin)
    P = [p for p in P if not ins[p].any()]
    P = largest_part(P)
    v, P, _ = compact(v, P)
    n0 = len(v); T = M.triangulate(P); loops = M.boundary_loops(T)
    assert len(loops) == len(CUTS), [len(l) for l in loops]
    for L in loops: v, P = fill(v, P, L[::-1], rings=6)
    free = np.zeros(len(v), bool); free[n0:] = True
    for cx, cy, rx, ry, zmin in CUTS:
        free |= (((v[:, 0] - cx) / rx) ** 2 + ((v[:, 1] - cy) / ry) ** 2 < 1.5 ** 2) & (v[:, 2] > 0.09)
    return biharmonic(v, P, free), P


def weld(v, P):
    from scipy.spatial import cKDTree
    pairs = cKDTree(v).query_pairs(1e-6)
    m = np.arange(len(v))
    for a, b in sorted(pairs): m[max(a, b)] = m[min(a, b)]
    for _ in range(3): m = m[m]
    P = [[int(m[i]) for i in p] for p in P]
    P = [p for p in P if len(set(p)) == len(p)]
    v2, P, _ = compact(v, P)
    return v2, P


def rbf(src, dst, lam=1e-6):
    n = len(src)
    Kmat = np.linalg.norm(src[:, None] - src[None], axis=2) + lam * np.eye(n)
    Pm = np.c_[np.ones(n), src]
    A = np.block([[Kmat, Pm], [Pm.T, np.zeros((4, 4))]])
    w = np.linalg.solve(A, np.r_[dst - src, np.zeros((4, 3))])
    def f(X):
        R = np.linalg.norm(X[:, None] - src[None], axis=2)
        return X + R @ w[:n] + np.c_[np.ones(len(X)), X] @ w[n:]
    return f


def slice_segments(V, T, y):
    d = V[T, 1] - y
    s = np.sign(d)
    cross = (s.min(1) < 0) & (s.max(1) > 0)
    out = []
    for t, dd in zip(T[cross], d[cross]):
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if (dd[a] < 0) != (dd[b] < 0):
                u = dd[a] / (dd[a] - dd[b]); pts.append(V[t[a]] + u * (V[t[b]] - V[t[a]]))
        if len(pts) == 2: out.append(pts)
    return np.array(out).reshape(-1, 2, 3)


def sample(V, T, y):
    """At height y: the side-most point, the side-most point of the front part, the middle line's front and back."""
    S = slice_segments(V, T, y)
    if len(S) == 0: return None, None, None, None
    P = S.reshape(-1, 3)
    side = P[np.argmax(abs(P[:, 0]))]
    zm = (P[:, 2].max() + P[:, 2].min()) / 2
    Q = P[P[:, 2] > zm + 0.25 * (P[:, 2].max() - zm)]
    face = Q[np.argmax(abs(Q[:, 0]))] if len(Q) else None
    a, b = S[:, 0], S[:, 1]
    c = (np.sign(a[:, 0]) != np.sign(b[:, 0]))
    if not c.any(): return side, None, None, face
    u = a[c, 0] / (a[c, 0] - b[c, 0])
    M0 = a[c] + u[:, None] * (b[c] - a[c])
    return side, M0[np.argmax(M0[:, 2])], M0[np.argmin(M0[:, 2])], face


def ears_of(v):
    return (abs(v[:, 0]) > 0.10) & (v[:, 2] > -0.06) & (v[:, 2] < 0.07) & (v[:, 1] > 0.64) & (v[:, 1] < 0.80)


def fit(v, T, tri_ok, spec, iters=3):
    """spec: K (metres per unit), chin (the unit height that becomes y=0), draw_y (the landmarks' unit heights),
    yd (unit heights to fit at) with hw (half width), fw (the face's half width in front of the ears; nan: none),
    zf, zb (front and back of the middle line, units), start (rough scale of x and z)."""
    K, CH = spec['K'], spec['chin']
    yd = np.asarray(spec['yd'], float)
    yt = (CH - yd) * K
    V = v.copy()
    V[:, 1] = (CH - np.interp(v[:, 1], BASE_Y, spec['draw_y'])) * K
    V[:, 0] *= spec['start'][0]; V[:, 2] *= spec['start'][1]
    for it in range(iters):
        src, dst = [], []
        for k, y in enumerate(yt):
            side, fr, bk, face = sample(V, T[tri_ok], y)
            if face is not None and not np.isnan(spec['fw'][k]):
                q = np.array([np.sign(face[0]) * spec['fw'][k] * K, face[1], face[2]])
                src += [face, face * [-1, 1, 1]]; dst += [q, q * [-1, 1, 1]]
            if side is not None and not np.isnan(spec['hw'][k]):
                q = np.array([np.sign(side[0]) * spec['hw'][k] * K, side[1], side[2]])
                src += [side, side * [-1, 1, 1]]; dst += [q, q * [-1, 1, 1]]
            if fr is not None: src.append(fr); dst.append([0, fr[1], spec['zf'][k] * K])
            if bk is not None: src.append(bk); dst.append([0, bk[1], spec['zb'][k] * K])
        src, dst = np.array(src), np.array(dst)
        V = rbf(src, dst, lam=1e-3)(V)
        print('fit', it, 'mean miss', np.abs(dst - src).mean() / K, 'units')
    return V


def base(path):
    v, P = load(path)
    v, P = blank(v, P)
    v, P = weld(v, P)
    return v, P


def surface_point(V, N, x, y, zmin=0.0):
    """The head's surface point in front (z > zmin) nearest to the line (x, y): (point, normal)."""
    m = V[:, 2] > zmin
    i = np.where(m)[0][np.argmin((V[m, 0] - x) ** 2 + (V[m, 1] - y) ** 2)]
    return V[i], N[i]
