"""Shells built from the drawing's sizes: lofted rings (a jumper, shorts, a jacket), tubes along the limbs (sleeves,
trouser legs), mittens, an icosphere (the hair's dome); and how they take the body's skinning weights.
The lofts, tubes and mittens are Р12's (to3d/r12-s12-anya/tools/form.py)."""
import numpy as np
from scipy.spatial import cKDTree
import mesh as M

smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))


def ring(a, zc, df, db, th, p=2.3):
    s, c = np.sin(th), np.cos(th)
    x = a * np.sign(s) * np.abs(s) ** (2 / p)
    z = zc + np.where(c > 0, df, db) * np.sign(c) * np.abs(c) ** (2 / p)
    return x, z


def grid(rows, cols, closed):
    T = []
    cn = cols if closed else cols - 1
    for r in range(rows - 1):
        for c in range(cn):
            a0, a1 = r * cols + c, r * cols + (c + 1) % cols
            b0, b1 = a0 + cols, a1 + cols
            T += [[a0, b0, a1], [a1, b0, b1]]
    return np.array(T)


def loft(rows, cols=72, closed=True, gap=None, p=2.3, xc=None):
    """rows: (y, a, zc, df, db) in metres, top to bottom; gap: per row the half-angle left open (at the front, or
    where gap_at says); xc: per row the ring's centre x."""
    V = []
    for i, (yy, aa, zc, df, db) in enumerate(rows):
        g = 0 if gap is None else gap[i]
        th = np.linspace(0, 2 * np.pi, cols, endpoint=False) if closed else np.linspace(g, 2 * np.pi - g, cols)
        x, z = ring(aa, zc, df, db, th, p)
        V += list(np.c_[x + (0 if xc is None else xc[i]), np.full(cols, yy), z])
    return np.array(V), grid(len(rows), cols, closed)


def outward(V, T):
    """Triangles turned so that normals point away from the shell's axis (its centre line by height)."""
    n = M.vertex_normals(V, T); c = V.mean(0)
    return T if (n * (V - c)).sum(1).mean() > 0 else T[:, ::-1]


def tube(path, radii, cols=24, flat=1.0):
    """A tube along a polyline (rest), rings across its direction; flat: the ring's depth to its width."""
    path = np.asarray(path, float); V = []
    ref = np.array([0, 0, 1.0])
    for i, p in enumerate(path):
        tg = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]; tg /= np.linalg.norm(tg)
        n1 = ref - tg * (ref @ tg); n1 /= np.linalg.norm(n1); n2 = np.cross(tg, n1)
        for th in np.linspace(0, 2 * np.pi, cols, endpoint=False):
            V.append(p + radii[i] * (flat * np.cos(th) * n1 + np.sin(th) * n2))
    V = np.array(V); T = grid(len(path), cols, True)
    c = np.repeat(path, cols, 0)
    if (M.vertex_normals(V, T) * (V - c)).sum(1).mean() < 0: T = T[:, ::-1]
    return V, T


def catmull(pts, n):
    pts = np.asarray(pts, float); P = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]]); out = []
    for i in range(1, len(P) - 2):
        for s in np.linspace(0, 1, n, endpoint=False):
            p0, p1, p2, p3 = P[i - 1:i + 3]
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-2]); return np.array(out)


def mitten(W_, tip, acr, sg, Lh=0.115, wide=0.025, thick=0.0125, thumb=0.010, rows=26, cols=22):
    """A mitten as drawn: fingers together, a small thumb. W_: the wrist, tip: the middle finger's end, acr: across the
    palm (index − pinky)."""
    d = tip - W_; d /= np.linalg.norm(d)
    acr = acr - d * (acr @ d); acr /= np.linalg.norm(acr)
    nrm_ = np.cross(d, acr) * sg
    V = []
    for uu in np.linspace(-0.12, 1.0, rows):
        tip_r = np.sqrt(max(0.0, 1 - max(0.0, (uu - 0.55) / 0.45) ** 2))
        a_ = wide * tip_r * (0.85 + 0.15 * smooth((uu + 0.1) / 0.3)); b_ = thick * tip_r * (0.9 + 0.1 * smooth(uu / 0.4))
        th_ = thumb * np.exp(-((uu - 0.33) / 0.14) ** 2)
        for th in np.linspace(0, 2 * np.pi, cols, endpoint=False):
            x_ = a_ * np.cos(th) + th_ * max(np.cos(th), 0) ** 2; z_ = b_ * np.sin(th)
            V.append(W_ + d * uu * Lh + acr * x_ + nrm_ * z_)
    V = np.array(V); T = grid(rows, cols, True)
    if (M.vertex_normals(V, T) * (V - V.mean(0))).sum(1).mean() < 0: T = T[:, ::-1]
    return V, T


def icosphere(level):
    t = (1 + 5 ** 0.5) / 2
    V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    V = [np.array(v) / np.linalg.norm(v) for v in V]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    for _ in range(level):
        mid = {}; F2 = []
        def m(a, b):
            k = (min(a, b), max(a, b))
            if k not in mid:
                p = V[a] + V[b]; V.append(p / np.linalg.norm(p)); mid[k] = len(V) - 1
            return mid[k]
        for a, b, c in F:
            ab, bc, ca = m(a, b), m(b, c), m(c, a)
            F2 += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        F = F2
    return np.array(V), np.array(F)


class Weights:
    """Skinning weights for built shells: from the fitted body's nearest skin, smoothed over the shell."""
    def __init__(self, PF, SJ0, SW0, NJ):
        self.tree = cKDTree(PF); self.SJ, self.SW, self.NJ = SJ0, SW0, NJ

    def transfer(self, V, k=6):
        dd, ii = self.tree.query(V, k)
        w = 1 / (dd + 1e-3) ** 2; w /= w.sum(1, keepdims=True)
        W = np.zeros((len(V), self.NJ))
        for c in range(k):
            for q in range(4): np.add.at(W, (np.arange(len(V)), self.SJ[ii[:, c], q]), w[:, c] * self.SW[ii[:, c], q])
        return W

    @staticmethod
    def smooth(W, T, iters=12):
        A = M.adjacency(len(W), [list(t_) for t_ in T])
        return M.smooth(W, A, np.ones(len(W), bool), iters, 0.5)

    def limb(self, V, T, keep, root, r=0.06):
        """A sleeve or a trouser leg belongs to its own limb only (the nearest skin near its root may be the trunk's)."""
        W = self.transfer(V)
        top = smooth(np.linalg.norm(V - root, axis=1) / r)
        Wa = W * keep; Wa /= Wa.sum(1, keepdims=True) + 1e-9
        return self.smooth(Wa * top[:, None] + W * (1 - top[:, None]), T)
