"""Mesh tools for the clothes and the hair: cut a triangle mesh along a level of a scalar (clean edges along any
curve), boundary loops, offset shells with a rim, Laplacian smoothing."""
import numpy as np
from collections import defaultdict


def cut(V, T, f, A=None):
    """keep where f < 0; triangles crossing 0 are split on the zero level. A: per-vertex attributes (N×k) carried
    linearly. Returns V, T, A, and for each new vertex whether it lies on the cut (the new edge)."""
    V = list(map(tuple, V)); A = None if A is None else list(map(tuple, A)); f = list(f)
    on = [False] * len(V)
    mid = {}
    def edge(a, b):
        k = (min(a, b), max(a, b))
        if k not in mid:
            t = f[a] / (f[a] - f[b])
            V.append(tuple(np.array(V[a]) * (1 - t) + np.array(V[b]) * t))
            if A is not None: A.append(tuple(np.array(A[a]) * (1 - t) + np.array(A[b]) * t))
            f.append(0.0); on.append(True); mid[k] = len(V) - 1
        return mid[k]
    out = []
    for tri in T:
        s = [f[v] < 0 for v in tri]
        n = sum(s)
        if n == 3: out.append(tri); continue
        if n == 0: continue
        r = 0
        while not (s[r] if n == 1 else not s[r]): r += 1
        a, b, c = tri[r], tri[(r + 1) % 3], tri[(r + 2) % 3]
        if n == 1:          # a inside
            out.append((a, edge(a, b), edge(a, c)))
        else:               # a outside, b and c inside
            ab, ac = edge(a, b), edge(a, c)
            out.append((ab, b, c)); out.append((ab, c, ac))
    V = np.array(V); T = np.array(out)
    used = np.unique(T); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
    return V[used], remap[T], (None if A is None else np.array(A)[used]), np.array(on)[used]


def loops(T):
    cnt = defaultdict(int)
    for t in T:
        for k in range(3): a, b = t[k], t[(k + 1) % 3]; cnt[(min(a, b), max(a, b))] += 1
    nxt = {}
    for t in T:
        for k in range(3):
            a, b = t[k], t[(k + 1) % 3]
            if cnt[(min(a, b), max(a, b))] == 1: nxt[a] = b
    out, seen = [], set()
    for s in nxt:
        if s in seen: continue
        L = [s]; seen.add(s); x = nxt[s]
        while x != s and x not in seen: L.append(x); seen.add(x); x = nxt.get(x, s)
        out.append(L)
    return out


def neighbours(T, n):
    nb = [set() for _ in range(n)]
    for a, b, c in T: nb[a] |= {b, c}; nb[b] |= {a, c}; nb[c] |= {a, b}
    return [np.array(sorted(s)) for s in nb]


def smooth(V, T, it=10, lam=0.5, fixed=None, mask=None):
    nb = neighbours(T, len(V)); V = V.copy()
    for _ in range(it):
        M = np.array([V[s].mean(0) if len(s) else V[i] for i, s in enumerate(nb)])
        D = M - V
        if fixed is not None: D[fixed] = 0
        if mask is not None: D *= mask[:, None]
        V = V + lam * D
    return V


def rim(V, T, L, inward, A=None):
    """a band from the boundary loop L to its copy moved by inward (N×3 for the loop's vertices): the cloth's edge
    turned in, so it has thickness. Returns V, T (and A) with the band added."""
    n = len(V); L = np.array(L)
    V2 = np.r_[V, V[L] + inward]
    ring = np.arange(n, n + len(L))
    a, b = L, np.roll(L, -1); c, d = ring, np.roll(ring, -1)
    band = np.r_[np.stack([b, a, c], 1), np.stack([b, c, d], 1)]
    A2 = None if A is None else np.r_[A, A[L]]
    return V2, np.r_[T, band], A2
