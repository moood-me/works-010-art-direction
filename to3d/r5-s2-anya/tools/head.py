"""The head: Blender's Human Base Meshes stylised head (CC0), its eye sockets and mouth closed (the eyes, brows and
mouth of the Klaus style are painted from the drawing), then fitted to Аня's front view and profile by slices: each
height of the base goes to the drawing's height by landmarks (crown, brow, eyes, nose tip, mouth, chin, neck), its
width to the front view's, its front and back to the profile's."""
import numpy as np
import mesh as M
import drawing as D

HBM = '/home/user/cache/to3d-r5-s2-anya/hbm.npz'
C0 = 2.082951545715332
K = 0.00086            # metres per drawing unit (head views)
XF, XS = 250.0, 300.0  # the front view's middle; the profile's x that becomes z=0
CHIN_Y = 370.0


def conv(v): return np.c_[v[:, 0] - C0, v[:, 2], -v[:, 1]]


def load():
    d = np.load(HBM)
    v = conv(d['head_v']); P = M.polys_of(d['head_fs'], d['head_f'])
    eL, eR = conv(d['eyeL_v']), conv(d['eyeR_v'])
    return v, P, d['head_vis'], eL, eR


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


CUTS = [(0.046, 0.729, 0.036, 0.032, 0.0), (-0.046, 0.729, 0.036, 0.032, 0.0), (0.0, 0.640, 0.040, 0.022, 0.03)]


def blank(v, P):
    """Eye sockets (lids, linings) and lips cut out by ellipses in the front view, the holes filled with a smooth patch
    (bi-harmonic: it continues the face around it); returns the patch vertices too."""
    ins = np.zeros(len(v), bool)
    for cx, cy, rx, ry, zmin in CUTS:
        ins |= (((v[:, 0] - cx) / rx) ** 2 + ((v[:, 1] - cy) / ry) ** 2 < 1) & (v[:, 2] > zmin)
    P = [p for p in P if not ins[p].any()]
    P = largest_part(P)
    v, P, _ = compact(v, P)
    n0 = len(v); T = M.triangulate(P); loops = M.boundary_loops(T)
    assert len(loops) == len(CUTS), [len(l) for l in loops]
    for L in loops: v, P = fill(v, P, L[::-1], rings=6)
    patch = np.zeros(len(v), bool); patch[n0:] = True
    free = patch.copy()
    for cx, cy, rx, ry, zmin in CUTS:       # and a ring round each cut, so what is left of the lids and lips smooths out
        free |= (((v[:, 0] - cx) / rx) ** 2 + ((v[:, 1] - cy) / ry) ** 2 < 1.5 ** 2) & (v[:, 2] > 0.09)
    v = biharmonic(v, P, free)
    return v, P, patch


def weld(v, P, extra):
    """Vertices at the same place made one (the base's halves meet on the middle line)."""
    from scipy.spatial import cKDTree
    pairs = cKDTree(v).query_pairs(1e-6)
    m = np.arange(len(v))
    for a, b in sorted(pairs): m[max(a, b)] = m[min(a, b)]
    for _ in range(3): m = m[m]
    P = [[int(m[i]) for i in p] for p in P]
    P = [p for p in P if len(set(p)) == len(p)]
    v2, P, mm = compact(v, P)
    ex = np.zeros(len(v2), bool); ex[mm[np.where(extra)[0]][mm[np.where(extra)[0]] >= 0]] = True
    return v2, P, ex


def largest_part(P):
    """Only the faces connected (over vertices) to the biggest piece."""
    from scipy.sparse.csgraph import connected_components
    from scipy.sparse import coo_matrix
    T = M.triangulate(P); n = T.max() + 1
    A = coo_matrix((np.ones(len(T) * 2), (np.r_[T[:, 0], T[:, 1]], np.r_[T[:, 1], T[:, 2]])), shape=(n, n))
    _, lab = connected_components(A, directed=False)
    big = np.bincount(lab[T[:, 0]]).argmax()
    return [p for p in P if lab[p[0]] == big]


def biharmonic(v, P, free):
    """The free vertices placed so the surface bends as little as it can (min |L x|^2, uniform Laplacian)."""
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


# ---------------------------------------------------------------- targets from the drawing
BASE_Y = [0.513, 0.578, 0.600, 0.645, 0.680, 0.729, 0.760, 0.888]
DRAW_Y = [472.0, 370.0, 344.0, 326.0, 292.0, 248.0, 214.0, 96.0]


def _fill(a):
    i = np.arange(len(a)); ok = ~np.isnan(a)
    return np.interp(i, i[ok], a[ok])


def targets(yd):
    """Half-width (front), front z and back z (profile), drawing units, at drawing heights yd."""
    f = D.spans(D.FRONT['face'], yd); s = D.spans(D.SIDE['face'], yd)
    nf = D.spans(D.FRONT['neck'], yd); ns = D.spans(D.SIDE['neck'], yd)
    hw = (f[:, 1] - f[:, 0]) / 2
    # the skull above the face's top, under the hair: round to the crown at y=96
    sk = 70 * np.sqrt(np.clip(1 - ((165 - yd) / 69) ** 2, 0, 1))
    hw = np.where(yd < 200, np.fmax(sk, np.where(yd < 200, np.nan, hw)), hw)
    # the neck: the drawing's is a stick (4 cm); a real neck's width, thin for a young woman
    neck = np.interp(yd, [330, 380, 440, 470], [30, 36, 40, 42])
    face_hw = hw.copy()
    hw = np.where(yd > 340, np.fmax(hw, neck), hw)
    zf = XS - s[:, 0]
    zf = np.where(yd < 120, np.interp(yd, [96, 106, 120], [XS - 262, XS - 236, XS - 220]), zf)
    zf = np.where(yd > 368, XS - ns[:, 0] + 6, zf)
    zb = XS - np.interp(yd, [96, 106, 120, 160, 200, 240, 280, 310, 340, 380, 440],
                        [260, 290, 330, 354, 362, 360, 348, 334, 322, 318, 318])
    face_hw = np.where(np.isnan(face_hw) & (yd > 340), 0, face_hw)
    return _fill(hw), _fill(zf), _fill(zb), np.where(yd > 340, np.fmin(_fill(face_hw), _fill(hw)), _fill(hw))


def rbf(src, dst, lam=1e-6):
    """A smooth map R^3 -> R^3 taking src to dst: biharmonic kernel |r| plus an affine part."""
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
    """The surface cut at height y: segments (S×2×3)."""
    d = V[T, 1] - y
    segs = []
    for e0, e1, e2 in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        pass
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


def sample(V, T, tri_ok, y):
    """At height y: the side-most point (max |x|, triangles tri_ok only), the front and the back of the midline."""
    S = slice_segments(V, T[tri_ok], y)
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


def fit(v, T, tri_ok, iters=3):
    """Points of the base's surface (its silhouettes in front and in profile, at heights matched by the landmarks) taken
    to the drawing's, the whole head following by a smooth map; repeated so the silhouettes settle."""
    yd = np.arange(100, 471, 5.0)
    hw, zf, zb, fw = targets(yd)
    yt = (CHIN_Y - yd) * K
    V = v.copy()
    # start: heights by the landmarks (piecewise), widths and depths scaled overall
    V[:, 1] = (CHIN_Y - np.interp(v[:, 1], BASE_Y, DRAW_Y)) * K
    V[:, 0] *= 0.62; V[:, 2] = V[:, 2] * 0.75
    for it in range(iters):
        src, dst = [], []
        for k, y in enumerate(yt):
            side, fr, bk, face = sample(V, T, tri_ok, y)
            if face is not None and yd[k] > 300 and yd[k] < 372:
                q = np.array([np.sign(face[0]) * fw[k] * K, face[1], face[2]])
                src += [face, face * [-1, 1, 1]]; dst += [q, q * [-1, 1, 1]]
            if side is not None:
                q = np.array([np.sign(side[0]) * hw[k] * K, side[1], side[2]])
                src += [side, side * [-1, 1, 1]]; dst += [q, q * [-1, 1, 1]]
            if fr is not None: src.append(fr); dst.append([0, fr[1], zf[k] * K])
            if bk is not None: src.append(bk); dst.append([0, bk[1], zb[k] * K])
        src, dst = np.array(src), np.array(dst)
        f = rbf(src, dst, lam=1e-3)
        V = f(V)
        print('fit', it, 'mean miss', np.abs(dst - src).mean() / K, 'units')
    return V


def ears_of(v):
    return (abs(v[:, 0]) > 0.10) & (v[:, 2] > -0.06) & (v[:, 2] < 0.07) & (v[:, 1] > 0.64) & (v[:, 1] < 0.80)


def build():
    v, P, vis, eL, eR = load()
    r = (eL.max(0) - eL.min(0)).max() / 2
    v, P, patch = blank(v, P)
    v, P, patch = weld(v, P, patch)
    T = M.triangulate(P)
    ear = ears_of(v)
    V = fit(v, T, ~ear[T].any(1))
    # the ears smaller and close to the head (the drawing's are small and under the hair)
    for sg in (1, -1):
        m = ear & (np.sign(v[:, 0]) == sg)
        w = np.clip((abs(v[m, 0]) - 0.10) / 0.02, 0, 1)
        c = V[m].mean(0)
        V[m] = V[m] + (c - V[m]) * (0.3 * w)[:, None]
        V[m, 0] -= sg * 0.5 * w * np.clip(abs(V[m, 0]) - abs(c[0]) + 0.004, 0, None)
    return V, P, patch


if __name__ == '__main__':
    import sys
    from PIL import Image
    V, P, patch = build()
    T = M.triangulate(P)
    print(len(V), len(T), 'boundary', [len(l) for l in M.boundary_loops(T)])
    y = lambda yd: (CHIN_Y - yd) * K
    box = ((60 - XF) * K, (440 - XF) * K, y(500), y(40))
    a, _ = M.raster(V, T, 0, 500, box)
    boxs = ((XS - 440) * K, (XS - 60) * K, y(500), y(40))
    b, _ = M.raster(V, T, np.pi / 2, 500, ((-(440 - XS)) * K, (XS - 60) * K, y(500), y(40)))
    Image.fromarray(np.hstack([a, b])).save(sys.argv[1] if len(sys.argv) > 1 else '/tmp/h.png')
