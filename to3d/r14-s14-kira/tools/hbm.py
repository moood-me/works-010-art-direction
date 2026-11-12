"""The Human Base Meshes stylised head (CC0) in the engine's frame (metres, y up, facing +z, his left +x), and the
topology helpers the head is made with: boundary loops of a quad mesh, the outer skin, a hole closed by rings."""
import numpy as np
from collections import defaultdict
from scipy.sparse.csgraph import connected_components
from scipy.sparse import coo_matrix
from common import CACHE


def load():
    d = np.load(f'{CACHE}/hbm_head.npz')
    v, f, vis = d['sub_v'], d['sub_f'], d['sub_vis']
    V = np.c_[v[:, 0], v[:, 2], -v[:, 1]]
    V[:, 0] -= (V[:, 0].max() + V[:, 0].min()) / 2
    return V, f, vis


def compact(V, Q):
    used = np.unique(Q); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
    return V[used], remap[Q], used


def boundary(Q):
    """directed boundary edges a→b (a dict of lists) and their count per vertex"""
    cnt = defaultdict(int)
    for q in Q:
        for k in range(4): a, b = q[k], q[(k + 1) % 4]; cnt[(min(a, b), max(a, b))] += 1
    bd = defaultdict(list)
    for q in Q:
        for k in range(4):
            a, b = q[k], q[(k + 1) % 4]
            if cnt[(min(a, b), max(a, b))] == 1: bd[a].append(b)
    return bd


def clean(Q):
    """drop faces until every boundary vertex has one boundary edge out (no pinches) and no face hangs by an edge"""
    while True:
        bd = boundary(Q)
        bad = {a for a, l in bd.items() if len(l) > 1}
        nb = np.array([sum(1 for k in range(4) if q[(k + 1) % 4] in bd.get(q[k], [])) for q in Q])
        drop = np.array([any(v in bad for v in q) for q in Q]) | (nb >= 3)
        if not drop.any(): return Q
        Q = Q[~drop]


def loops(Q):
    bd = boundary(Q)
    out, seen = [], set()
    for s in list(bd):
        if s in seen: continue
        L = [s]; seen.add(s); x = bd[s][0]
        while x != s: L.append(x); seen.add(x); x = bd[x][0]
        out.append(L)
    return out


def largest(V, Q):
    """the biggest connected piece"""
    r = Q.ravel(); c = np.roll(Q, -1, axis=1).ravel()
    n, lab = connected_components(coo_matrix((np.ones(len(r)), (r, c)), shape=(len(V), len(V))))
    k = np.bincount(lab[Q[:, 0]]).argmax()
    return Q[lab[Q[:, 0]] == k]


def close(V, Q, L, rings=6):
    """close the hole L with rings of quads toward its middle (and a fan at the centre); returns V, Q and the new vertices"""
    n = len(L); c = V[L].mean(0)
    Vn = [V]; Qn = [Q]; prev = np.array(L); new = []
    base = len(V)
    for r in range(1, rings + 1):
        t = r / (rings + 1)
        ring = np.arange(base, base + n); base += n
        Vn.append(V[L] * (1 - t) + c * t); new += list(ring)
        Qn.append(np.stack([prev, np.roll(prev, -1), np.roll(ring, -1), ring], 1)[:, ::-1])
        prev = ring
    ci = base; Vn.append(c[None]); new.append(ci)
    Qn.append(np.stack([prev, np.roll(prev, -1), np.full(n, ci), np.full(n, ci)], 1)[:, ::-1])
    return np.concatenate(Vn), np.concatenate(Qn), np.array(new)


def tris(Q):
    T = np.r_[Q[:, [0, 1, 2]], Q[:, [0, 2, 3]]]
    return T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]
