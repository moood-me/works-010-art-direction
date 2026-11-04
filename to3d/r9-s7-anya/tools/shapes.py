"""Building blocks for the shells: a grid surface turned into a thin solid (outer side, inner side, a rim along its
open edges — so a garment's edge has a real edge, which the outline then draws), tubes along polylines, and lines
lying on a surface (the drawing's folds and strands as thin dark strips)."""
import numpy as np
import mesh as M


def grid_tris(R, C, closed):
    T = []
    cn = C if closed else C - 1
    for r in range(R - 1):
        for c in range(cn):
            a0, a1 = r * C + c, r * C + (c + 1) % C
            b0, b1 = a0 + C, a1 + C
            T += [[a0, b0, a1], [a1, b0, b1]]
    return np.array(T, np.int64)


def grid_normals(G, closed):
    V = G.reshape(-1, 3); R, C = G.shape[:2]
    return M.vertex_normals(V, grid_tris(R, C, closed)).reshape(R, C, 3)


def solid(G, closed, th, out_ref):
    """G (rows, cols, 3) — the outer surface; a thin solid of thickness th inward. out_ref(V) → a point inside, per
    vertex, to orient the outer side away from it. Returns V, T, and a mask of the outer side's vertices."""
    R, C = G.shape[:2]
    T0 = grid_tris(R, C, closed)
    V0 = G.reshape(-1, 3)
    n = M.vertex_normals(V0, T0)
    if ((V0 - out_ref(V0)) * n).sum(1).mean() < 0:
        T0 = T0[:, ::-1]; n = -n
    Vi = V0 - n * th
    N = len(V0)
    T = [T0, T0[:, ::-1] + N]
    # rims along the open edges: first and last rows; first and last columns when open
    def rim(idx):
        idx = list(idx); q = []
        for a, b in zip(idx[:-1], idx[1:]):
            q += [[a, b, b + N], [a, b + N, a + N]]
        return np.array(q, np.int64)
    edges = []
    rows0 = list(range(C)) + ([0] if closed else [])
    edges.append([0 * C + c for c in rows0][::-1])
    edges.append([(R - 1) * C + c for c in rows0])
    if not closed:
        edges.append([r * C + 0 for r in range(R)])
        edges.append([r * C + C - 1 for r in range(R)][::-1])
    for e in edges:
        q = rim(e)
        # orient each rim outward (away from the strip's middle)
        Vt = np.vstack([V0, Vi])
        nn = np.cross(Vt[q[:, 1]] - Vt[q[:, 0]], Vt[q[:, 2]] - Vt[q[:, 0]])
        mid = Vt[q].mean(1)
        cen = (V0.mean(0))
        T.append(q)
    T = np.vstack(T)
    V = np.vstack([V0, Vi])
    outer = np.r_[np.ones(N, bool), np.zeros(N, bool)]
    return V, T, outer


def fix_rims(V, T, outer):
    """orient every triangle consistently with its neighbours (flood over shared edges from the outer side)."""
    from collections import defaultdict, deque
    ef = defaultdict(list)
    for i, t in enumerate(T):
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            ef[(min(a, b), max(a, b))].append(i)
    done = np.zeros(len(T), bool); T = T.copy()
    seeds = [i for i, t in enumerate(T) if outer[t].all()]
    dq = deque(seeds); done[seeds] = True
    while dq:
        i = dq.popleft(); t = T[i]
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            for j in ef[(min(a, b), max(a, b))]:
                if done[j]: continue
                u = list(T[j])
                # consistent neighbours traverse the shared edge in opposite directions
                k = [(u[0], u[1]), (u[1], u[2]), (u[2], u[0])]
                if (a, b) in k: T[j] = T[j][::-1]
                done[j] = True; dq.append(j)
    return T


def shell(G, closed, th, out_ref):
    V, T, outer = solid(G, closed, th, out_ref)
    return V, fix_rims(V, T, outer), outer


def tube(path, radii, cols=24, caps=True):
    """A tube along a 3D polyline with a radius per point; rounded ends (caps)."""
    path = np.asarray(path, float); R = len(path)
    G = np.zeros((R, cols, 3))
    ref = np.array([0, 0, 1.0])
    for i, p in enumerate(path):
        tg = path[min(i + 1, R - 1)] - path[max(i - 1, 0)]; tg /= np.linalg.norm(tg)
        r0 = ref if abs(tg @ ref) < 0.9 else np.array([1.0, 0, 0])
        n1 = r0 - tg * (r0 @ tg); n1 /= np.linalg.norm(n1); n2 = np.cross(tg, n1)
        for k, th in enumerate(np.linspace(0, 2 * np.pi, cols, endpoint=False)):
            G[i, k] = p + radii[i] * (np.cos(th) * n1 + np.sin(th) * n2)
    V = G.reshape(-1, 3); T = list(grid_tris(R, cols, True))
    if caps:
        for end, row in ((0, 0), (1, R - 1)):
            c = len(V); V = np.vstack([V, path[row]])
            for k in range(cols):
                a, b = row * cols + k, row * cols + (k + 1) % cols
                T.append([a, b, c] if end == 0 else [b, a, c])
    T = np.array(T, np.int64)
    nrm = M.vertex_normals(V, T)
    ax = np.array([path[np.clip(np.argmin(np.linalg.norm(path - v, axis=1)), 0, R - 1)] for v in V])
    if ((V - ax) * nrm).sum(1).mean() < 0: T = T[:, ::-1]
    return V, T


def strip(P, N, width, lift=0.0015):
    """A thin strip along points P lying on a surface with normals N (a drawn line): width per point (m)."""
    P = np.asarray(P, float); N = np.asarray(N, float); w = np.broadcast_to(width, (len(P),))
    tg = np.gradient(P, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-12
    side = np.cross(tg, N); side /= np.linalg.norm(side, axis=1, keepdims=True) + 1e-12
    Q = P + N * lift
    V = np.vstack([Q - side * w[:, None] / 2, Q + side * w[:, None] / 2])
    n = len(P); T = []
    for i in range(n - 1):
        T += [[i, i + 1, n + i], [i + 1, n + i + 1, n + i]]
    T = np.array(T, np.int64)
    tn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    if (tn * np.vstack([N, N])[T[:, 0]]).sum(1).mean() < 0: T = T[:, ::-1]
    return V, T


def taper(n, ends=0.25):
    s = np.linspace(0, 1, n)
    return np.clip(np.minimum(s, 1 - s) / ends, 0.25, 1.0)
