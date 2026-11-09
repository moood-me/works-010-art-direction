"""Anny's body (an engine body pack: mesh, SOMA joints, weights) reshaped for a drawn character: scaled, each joint's
region made wider or thinner about its bone, joints moved, a standing habit (a hunch, a belly forward) turned into the
rest shape itself, the head and upper neck taken off; then helpers to dress it — regions pushed out and smoothed
into cloth forms, shells hung in front of it, weights taken over from the body."""
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M

sm = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))


class Body:
    def __init__(self, bid):
        sk = pack.skeleton(); self.names = [j['name'] for j in sk['joints']]; self.I = {n: i for i, n in enumerate(self.names)}
        self.parent = np.array([j['parent'] for j in sk['joints']]); self.NJ = len(self.names)
        h, a, th, t = pack.body(bid)
        self.P = a['positions'].reshape(-1, 3).astype(float); self.J = a['joints'].reshape(-1, 3).astype(float)
        self.J0 = self.J.copy(); self.P0 = self.P.copy()
        self.frames = a['frames'].reshape(-1, 4).astype(np.float32)
        self.T = t['triangles'].reshape(-1, 3).astype(np.int64)
        self.SJ = t['skinJoints'].reshape(-1, 4).astype(np.int64); self.SW = t['skinWeights'].reshape(-1, 4).astype(float)
        self.parts = t['parts'].reshape(len(self.P), -1) / 255.0; self.pn = th['parts']

    def part(self, *ns): return sum(self.parts[:, self.pn.index(n)] for n in ns)

    def under(self, j):
        out, st = [], [j]
        while st:
            k = st.pop(); out.append(k); st += list(np.where(self.parent == k)[0])
        return out

    def dense(self):
        W = np.zeros((len(self.P), self.NJ))
        for k in range(4): np.add.at(W, (np.arange(len(self.P)), self.SJ[:, k]), self.SW[:, k])
        return W

    def reshape(self, scale, affine, moves=(), length=None):
        """scale: overall; affine(name, bone direction or None) → 3×3 about the joint; length {joint name: factor}:
        the bone from that joint to its children made longer or shorter (the joint's region stretched along it);
        moves: [(joint name, vector)] applied to the joint and all under it."""
        length = length or {}
        order = []
        st = [int(np.where(self.parent < 0)[0][0])]
        while st:
            k = st.pop(0); order.append(k); st += list(np.where(self.parent == k)[0])
        J1 = self.J * scale
        for j in order:
            p = self.parent[j]
            if p >= 0: J1[j] = J1[p] + scale * length.get(self.names[p], 1.0) * (self.J[j] - self.J[p])
        for n, d in moves:
            for j in self.under(self.I[n]): J1[j] += d
        A = []
        for j, n in enumerate(self.names):
            kids = np.where(self.parent == j)[0]
            d = None
            if len(kids):
                d = self.J[kids[0]] - self.J[j]; d = d / (np.linalg.norm(d) + 1e-12)
            M_ = affine(n, d)
            if n in length and d is not None:
                # stretch along the bone, but only beyond the joint (the part behind it belongs to the parent's side)
                M_ = M_ @ (np.eye(3) + (length[n] - 1) * np.outer(d, d))
            A.append(M_)
        out = np.zeros_like(self.P)
        for k in range(4):
            for j in np.unique(self.SJ[:, k]):
                m = (self.SJ[:, k] == j) & (self.SW[:, k] > 0)
                out[m] += self.SW[m, k, None] * (J1[j] + scale * (self.P[m] - self.J[j]) @ A[j].T)
        self.P, self.J = out, J1

    def prepose(self, turns):
        """A habit of standing made the rest shape: turns {joint name: (axis, angle)} applied down the skeleton
        (linear blending — the angles are small)."""
        R = [np.eye(3)] * self.NJ; Jn = self.J.copy()

        def rot(ax, an):
            ax = np.asarray(ax, float); ax /= np.linalg.norm(ax); x, y, z = ax; c, s = np.cos(an), np.sin(an); C = 1 - c
            return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s], [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                             [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])
        order = []
        st = [int(np.where(self.parent < 0)[0][0])]
        while st:
            k = st.pop(0); order.append(k); st += list(np.where(self.parent == k)[0])
        for j in order:
            p = self.parent[j]
            Rp = R[p] if p >= 0 else np.eye(3)
            if p >= 0: Jn[j] = Jn[p] + Rp @ (self.J[j] - self.J[p])
            R[j] = Rp @ rot(*turns[self.names[j]]) if self.names[j] in turns else Rp
        out = np.zeros_like(self.P)
        for k in range(4):
            for j in np.unique(self.SJ[:, k]):
                m = (self.SJ[:, k] == j) & (self.SW[:, k] > 0)
                out[m] += self.SW[m, k, None] * (Jn[j] + (self.P[m] - self.J[j]) @ R[j].T)
        self.P, self.J = out, Jn

    def cut(self, gone):
        """Vertices out (a mask); returns the map old → new."""
        keep = np.where(~gone)[0]; remap = -np.ones(len(self.P), int); remap[keep] = np.arange(len(keep))
        self.T = remap[self.T[~gone[self.T].any(1)]]
        for k in ('P', 'SJ', 'SW', 'parts', 'P0'): setattr(self, k, getattr(self, k)[keep])
        return remap

    def front(self, x, y, r=0.015, mask=None, back=False):
        """The body's front-most (or back-most) z near (x, y)."""
        m = (abs(self.P[:, 0] - x) < r) & (abs(self.P[:, 1] - y) < r)
        if mask is not None: m &= mask
        if not m.any(): return np.nan
        return self.P[m, 2].min() if back else self.P[m, 2].max()

    def weights_at(self, Q, mask=None, k=6):
        """Dense weights for points Q: the mean of the nearest body vertices' (of mask)."""
        idx = np.arange(len(self.P)) if mask is None else np.where(mask)[0]
        W = self.dense()[idx]
        d, i = cKDTree(self.P[idx]).query(Q, k=k)
        w = 1 / (d + 1e-4); w /= w.sum(1, keepdims=True)
        return np.einsum('nk,nkj->nj', w, W[i])


def top4(W):
    idx = np.argsort(-W, 1)[:, :4]; w = np.take_along_axis(W, idx, 1); w = w / w.sum(1, keepdims=True)
    return idx, w


def grid_tris(rows, cols, wrap=False):
    T = []
    for r in range(rows - 1):
        for c in range(cols if wrap else cols - 1):
            a0, a1 = r * cols + c, r * cols + (c + 1) % cols; b0, b1 = a0 + cols, a1 + cols
            T += [[a0, b0, a1], [a1, b0, b1]]
    return np.array(T)
