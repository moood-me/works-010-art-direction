"""The Human Base Meshes stylised head (CC0) in head units on the engine's axes (x his left, y up, z forward; head
centre 0, crown to chin = 1), with its eyes, and the topology helpers (from Р3's hbm.py)."""
import numpy as np
from collections import defaultdict
from common import CACHE

CROWN, CHIN = 0.887, 0.588          # the base's crown and chin heights (Blender z)


def to_hu(v, x0):
    V = np.c_[v[:, 0] - x0, v[:, 2], -v[:, 1]]
    V[:, 1] -= (CROWN + CHIN) / 2
    return V / (CROWN - CHIN)


def load():
    d = np.load(f'{CACHE}/hbm.npz')
    v = d['sub_v']; x0 = (v[:, 0].max() + v[:, 0].min()) / 2
    out = dict(V=to_hu(v, x0), Q=d['sub_f'], cage=to_hu(d['cage_v'], x0), cageQ=d['cage_f'])
    for s in 'LR':
        out['eye' + s] = (to_hu(d[f'eye{s}_v'], x0), d[f'eye{s}_f'])
    return out


def boundary(Q):
    cnt = defaultdict(int)
    for q in Q:
        for k in range(4):
            a, b = q[k], q[(k + 1) % 4]
            if a != b: cnt[(min(a, b), max(a, b))] += 1
    bd = defaultdict(list)
    for q in Q:
        for k in range(4):
            a, b = q[k], q[(k + 1) % 4]
            if a != b and cnt[(min(a, b), max(a, b))] == 1: bd[a].append(b)
    return bd


def loops(Q):
    bd = boundary(Q)
    out, seen = [], set()
    for s in list(bd):
        if s in seen: continue
        L = [s]; seen.add(s); x = bd[s][0]
        while x != s: L.append(x); seen.add(x); x = bd[x][0]
        out.append(L)
    return out


def tris(Q):
    T = np.r_[Q[:, [0, 1, 2]], Q[:, [0, 2, 3]]]
    return T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]


if __name__ == '__main__':
    B = load()
    V = B['V']
    print(V.min(0).round(3), V.max(0).round(3))
    for L in loops(B['Q']):
        print('loop', len(L), V[L].mean(0).round(3), V[L].min(0).round(3), V[L].max(0).round(3))
    for s in 'LR':
        e = B['eye' + s][0]; print('eye', s, e.mean(0).round(3), (e.max(0) - e.min(0)).round(3))


def largest(V, Q):
    from scipy.sparse.csgraph import connected_components
    from scipy.sparse import coo_matrix
    r = Q.ravel(); c = np.roll(Q, -1, axis=1).ravel()
    n, lab = connected_components(coo_matrix((np.ones(len(r)), (r, c)), shape=(len(V), len(V))))
    k = np.bincount(lab[Q[:, 0]]).argmax()
    return Q[lab[Q[:, 0]] == k]


def close(V, Q, L, rings=6):
    """close the hole L with rings of quads toward its middle (and a fan at the centre) — Р3's hbm.close"""
    n = len(L); c = V[L].mean(0)
    Vn = [V]; Qn = [Q]; prev = np.array(L); new = []
    b = len(V)
    for r in range(1, rings + 1):
        t = r / (rings + 1)
        ring = np.arange(b, b + n); b += n
        Vn.append(V[L] * (1 - t) + c * t); new += list(ring)
        Qn.append(np.stack([prev, np.roll(prev, -1), np.roll(ring, -1), ring], 1)[:, ::-1])
        prev = ring
    ci = b; Vn.append(c[None]); new.append(ci)
    Qn.append(np.stack([prev, np.roll(prev, -1), np.full(n, ci), np.full(n, ci)], 1)[:, ::-1])
    return np.concatenate(Vn), np.concatenate(Qn), np.array(new)
