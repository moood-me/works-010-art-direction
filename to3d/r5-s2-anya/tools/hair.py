"""Аня's hair as one big shape, the Klaus way: a shell lofted through rings, one ring per height, each ring taken from
the drawing — its width from the front view (the hair's outer outline, with the parting's peak off the middle), its
front and back from the profile, open in front where the face shows (the face's own outline gives the opening's
edge). The shell has a thickness; where it would go into the head it is pushed out. Units: the head view's
(x_front, y, x_side); hair.build() returns metres in the head's frame (head.py)."""
import numpy as np
from scipy.spatial import cKDTree
import drawing as D
import head as H

P = 2.6                       # the rings' squareness (2 an ellipse)


def _fill(a):
    i = np.arange(len(a)); ok = ~np.isnan(a)
    return np.interp(i, i[ok], a[ok])


def rings(rows=70, cols=64):
    yd = np.r_[np.linspace(72, 120, 10), np.linspace(124, 452, rows - 10)]
    f = D.spans(D.FRONT['hair'], yd); s = D.spans(D.SIDE['hairall'], yd); fa = D.spans(D.FRONT['face'], yd)
    f[0] = [258, 266]; s[0] = [250, 280]
    cx = _fill((f[:, 0] + f[:, 1]) / 2 - H.XF); a = _fill((f[:, 1] - f[:, 0]) / 2)
    zf, zb = _fill(H.XS - s[:, 0]), _fill(H.XS - s[:, 1])
    inner = (fa[:, 1] - fa[:, 0]) / 2              # the face's half-width (nan above the hairline, below the chin)
    inner = np.where(np.isnan(inner) & (yd > 300), 58, inner)
    V = np.zeros((len(yd), cols, 3)); gap = np.zeros(len(yd))
    for r in range(len(yd)):
        zc = (zf[r] + zb[r]) / 2; db = zc - zb[r]
        g = 0.0
        if not np.isnan(inner[r]):
            xe = min(inner[r] + 1, a[r] * 0.97)
            g = np.arcsin(np.clip(xe / a[r], 0, 1) ** (P / 2))
        df = (zf[r] - zc) / max(np.cos(g) ** (2 / P), 0.15)
        th = np.linspace(g, 2 * np.pi - g, cols)        # the same columns on every row (closed rows meet at the front, the parting's line)
        sn, cs = np.sin(th), np.cos(th)
        x = a[r] * np.sign(sn) * abs(sn) ** (2 / P)
        z = zc + np.where(cs > 0, df, db) * np.sign(cs) * abs(cs) ** (2 / P)
        V[r] = np.c_[cx[r] + x, np.full(cols, yd[r]), z]
        gap[r] = g
    return V, yd, gap


def to_m(V):
    return np.c_[V[..., 0] * H.K, (H.CHIN_Y - V[..., 1]) * H.K, V[..., 2] * H.K]


def build(head_V, head_N, thick=0.006):
    R, yd, gap = rings()
    rows, cols, _ = R.shape
    O = to_m(R.reshape(-1, 3))
    # out of the head: every hair point at least 4 mm (more on the skull) outside the head's surface
    tree = cKDTree(head_V)
    for _ in range(4):
        d, i = tree.query(O)
        s = np.einsum('ij,ij->i', O - head_V[i], head_N[i])
        need = 0.004 + 0.008 * np.clip((240 - O[:, 1] * 0 - np.repeat(yd, cols)) / 140, 0, 1)
        push = np.clip(need - s, 0, None)
        O += head_N[i] * push[:, None]
    O = O.reshape(rows, cols, 3)
    # smooth along the rows and down (keeps the big shape, takes out kinks the pushing made)
    for _ in range(6):
        Q = O.copy()
        Q[1:-1] = (O[:-2] + 2 * O[1:-1] + O[2:]) / 4
        O = Q
    # the inner skin: toward the ring's own middle; thinner at the tips
    mid = O.mean(1, keepdims=True)
    dirv = O - mid; dirv[..., 1] = 0; dirv /= np.linalg.norm(dirv, axis=2, keepdims=True) + 1e-9
    t = thick * np.interp(yd, [72, 300, 452], [1.0, 1.0, 0.45])[:, None, None]
    I = O - dirv * t
    V = np.r_[O.reshape(-1, 3), I.reshape(-1, 3)]
    n = rows * cols
    T = []
    def quad(a, b, c, d): T.extend([[a, b, c], [a, c, d]])
    for r in range(rows - 1):
        wrap = False
        for c in range(cols if wrap else cols - 1):
            c2 = (c + 1) % cols
            a, b, cc, d = r * cols + c, r * cols + c2, (r + 1) * cols + c2, (r + 1) * cols + c
            quad(a, b, cc, d)                       # outer, facing out
            quad(n + a, n + d, n + cc, n + b)       # inner, facing in
        if not wrap:                                # the opening's two edges join outer and inner
            for c in (0, cols - 1):
                a, d = r * cols + c, (r + 1) * cols + c
                if c == 0: quad(a, d, n + d, n + a)
                else: quad(a, n + a, n + d, d)
    r = rows - 1                                    # the tips' edge
    for c in range(cols - 1):
        a, b = r * cols + c, r * cols + c + 1
        quad(a, n + a, n + b, b)
    V = np.r_[V, O[0].mean(0, keepdims=True) + [0, 0.002, 0]]
    top = len(V) - 1
    for c in range(cols): T.append([c, top, (c + 1) % cols][::-1])
    outer = np.zeros(len(V), bool); outer[:n] = True; outer[top] = True
    ydv = np.r_[np.repeat(yd, cols), np.repeat(yd, cols), yd[0]]
    return V, np.array(T)[:, ::-1], outer, ydv
