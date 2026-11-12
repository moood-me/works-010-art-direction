"""Small mesh helpers: polygons → triangles, edges, boundary loops, Laplacian smoothing, subdivision of quads."""
import numpy as np
import scipy.sparse as sp


def polys_of(fs, f):
    out, o = [], 0
    for n in fs:
        out.append(list(f[o:o + n])); o += n
    return out


def triangulate(polys):
    t = []
    for p in polys:
        for k in range(1, len(p) - 1):
            t.append([p[0], p[k], p[k + 1]])
    return np.array(t, dtype=np.int64)


def edges_of(polys):
    e = {}
    for p in polys:
        for a, b in zip(p, p[1:] + p[:1]):
            k = (min(a, b), max(a, b)); e[k] = e.get(k, 0) + 1
    return e


def boundary_loops(polys):
    e = edges_of(polys)
    nxt = {}
    for p in polys:
        for a, b in zip(p, p[1:] + p[:1]):
            if e[(min(a, b), max(a, b))] == 1: nxt[a] = b
    loops, seen = [], set()
    for s in nxt:
        if s in seen: continue
        L, v = [], s
        while v not in seen:
            seen.add(v); L.append(v); v = nxt[v]
        loops.append(L)
    return loops


def adjacency(n, polys):
    r, c = [], []
    for p in polys:
        for a, b in zip(p, p[1:] + p[:1]):
            r += [a, b]; c += [b, a]
    A = sp.coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)).tocsr()
    A.data[:] = 1
    return A


def smooth(V, A, mask, iters=10, lam=0.5):
    """Laplacian smoothing of the vertices in mask (the rest fixed)."""
    V = V.copy(); deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1
    for _ in range(iters):
        M = (A @ V) / deg[:, None]
        V[mask] += lam * (M[mask] - V[mask])
    return V


def smooth_field(D, A, mask, iters=30, lam=0.5):
    """Smooth a field (displacements) over the mesh in mask."""
    return smooth(D, A, mask, iters, lam)


def tri_normals(V, T):
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    return n


def vertex_normals(V, T):
    N = np.zeros_like(V); n = tri_normals(V, T)
    for k in range(3): np.add.at(N, T[:, k], n)
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)


def catmull_clark(V, polys, levels=1):
    """Catmull–Clark subdivision (polygons of any size; boundaries kept as creases). Returns V, quads."""
    for _ in range(levels):
        V, polys = _cc(V, polys)
    return V, polys


def _cc(V, polys):
    n = len(V)
    fp = np.array([V[p].mean(0) for p in polys])
    E = {}
    ef = {}
    for fi, p in enumerate(polys):
        for a, b in zip(p, p[1:] + p[:1]):
            k = (min(a, b), max(a, b))
            ef.setdefault(k, []).append(fi)
    ekeys = list(ef.keys())
    eidx = {k: n + len(polys) + i for i, k in enumerate(ekeys)}
    ep = np.zeros((len(ekeys), 3))
    bnd = np.zeros(n, bool)
    for i, k in enumerate(ekeys):
        fs = ef[k]
        if len(fs) == 2: ep[i] = (V[k[0]] + V[k[1]] + fp[fs[0]] + fp[fs[1]]) / 4
        else: ep[i] = (V[k[0]] + V[k[1]]) / 2; bnd[list(k)] = True
    # new vertex points
    vf = [[] for _ in range(n)]; ve = [[] for _ in range(n)]
    for fi, p in enumerate(polys):
        for v in p: vf[v].append(fi)
    for i, k in enumerate(ekeys):
        ve[k[0]].append(i); ve[k[1]].append(i)
    NV = V.copy()
    for v in range(n):
        if not vf[v]: continue
        if bnd[v]:
            be = [i for i in ve[v] if len(ef[ekeys[i]]) == 1]
            mids = [(V[ekeys[i][0]] + V[ekeys[i][1]]) / 2 for i in be]
            NV[v] = (V[v] * 6 + 2 * sum(mids)) / (6 + 2 * len(mids)) if mids else V[v]
            continue
        m = len(vf[v]); F = fp[vf[v]].mean(0)
        R = np.mean([(V[ekeys[i][0]] + V[ekeys[i][1]]) / 2 for i in ve[v]], 0)
        NV[v] = (F + 2 * R + (m - 3) * V[v]) / m
    out = np.vstack([NV, fp, ep])
    q = []
    for fi, p in enumerate(polys):
        c = n + fi; L = len(p)
        for j in range(L):
            a, b, prev = p[j], p[(j + 1) % L], p[j - 1]
            q.append([a, eidx[(min(a, b), max(a, b))], c, eidx[(min(prev, a), max(prev, a))]])
    return out, q
