"""The eyes made the drawing's: a ball of radius R where the drawn eye is, the base's lids carried onto it.

The base's lid rings (quad loops round the eye, found by quads.py) are moved in the eye's spherical coordinates: a
vertex at polar angle α (from the eye's axis), turn θ round it and radius r about the base ball goes to the new ball:
the lid margin's α_old(θ) becomes α_new(θ) — the drawn opening (face.eye_shape) seen on the new ball —, the lids
keep their angular widths and their height over the ball; the socket's lining is spread over the rest of the ball
behind the margin. The outer rings blend back into the head as it is."""
import numpy as np
from scipy.optimize import least_squares
from quads import Quads
from drawing import C
import face

R = 12.5                                  # the new ball (head units)
OPEN_C = np.array([18.5, -5.0])           # the drawn opening's middle (y up)
ZC = 19.5                                 # the ball's centre depth: its front at ~32, the drawn face there
# the rings of the left eye (seed vertex → which ring), from the margin outward, and the lining inward
OUTER = [381, 657, 385, 687, 597, 390]
OUTER_W = [1, 1, 0, 0, 0, 0]          # the margin and the next ring placed; the rest relaxed
LINING = [1355, 1996, 1371, 1451, 1433]


def ball_fit(E):
    r = least_squares(lambda p: np.linalg.norm(E - p[:3], axis=1) - p[3], np.r_[E.mean(0), 12])
    return r.x[:3], r.x[3]


def ring(Q, V, seed):
    for u in Q.neighbours(seed):
        if abs(V[u, 1] - V[seed, 1]) < abs(V[u, 0] - V[seed, 0]):
            L, closed = Q.loop(seed, u)
            assert closed, seed
            return np.array(L)


def opening(ex=None):
    ex = ex or face.expr(smile=0.25)
    up, lo, _, _ = face.eye_shape(C, ex, 1, ex)
    P = np.array(up + lo, float)
    return np.c_[P[:, 0] - OPEN_C[0], -P[:, 1] - OPEN_C[1]]     # about the opening's middle, y up


def polar_interp(P):
    th = np.arctan2(P[:, 1], P[:, 0]); rr = np.hypot(P[:, 0], P[:, 1]); o = np.argsort(th)
    th, rr = th[o], rr[o]
    th = np.r_[th - 2 * np.pi, th, th + 2 * np.pi]; rr = np.r_[rr, rr, rr]
    return lambda t: np.interp(((t + np.pi) % (2 * np.pi)) - np.pi, th, rr)


def frame(axis):
    z = axis / np.linalg.norm(axis); x = np.cross([0, 1, 0], z); x /= np.linalg.norm(x); y = np.cross(z, x)
    return np.stack([x, y, z])


def sph(X, c, F):
    L = (X - c) @ F.T
    r = np.linalg.norm(L, axis=1); a = np.arccos(np.clip(L[:, 2] / r, -1, 1)); t = np.arctan2(L[:, 1], L[:, 0])
    return r, a, t


def from_sph(r, a, t, c, F):
    L = np.c_[r * np.sin(a) * np.cos(t), r * np.sin(a) * np.sin(t), r * np.cos(a)]
    return c + L @ F


def fit_eyes(V, P, eyes, mirror_ix):
    """V: the head (already shaped); eyes: {'L': ball vertices, 'R': …} as shaped. Returns new V and the balls."""
    Q = Quads(P)
    O = polar_interp(opening())
    V = V.copy(); balls = {}
    for side, key in ((1, 'L'), (-1, 'R')):
        c1, R1 = ball_fit(eyes[key])
        ax1 = np.array([0.0, -0.25, 1.0]); ax1[0] = side * -0.15     # the base eye looks a little down and in
        F1 = frame(ax1)
        c2 = np.array([side * OPEN_C[0], OPEN_C[1], ZC]); F2 = frame(np.array([0.0, 0, 1]))
        S = lambda I: I if side == 1 else mirror_ix[I]
        rings = [S(ring(Q, V if side == 1 else V * [-1, 1, 1], s) if side == 1 else ring(Q, V, s)) for s in OUTER]
        lin = [S(ring(Q, V, s)) for s in LINING] if side == 1 else [mirror_ix[ring(Q, V, s)] for s in LINING]
        if side == -1: rings = [mirror_ix[ring(Q, V, s)] for s in OUTER]
        margin = rings[0]
        r_m, a_m, t_m = sph(V[margin], c1, F1)
        # α_old(θ) of the margin, α_new(θ) of the drawn opening on the new ball
        o = np.argsort(t_m); tt = np.r_[t_m[o] - 2 * np.pi, t_m[o], t_m[o] + 2 * np.pi]; aa = np.r_[a_m[o], a_m[o], a_m[o]]
        a_old = lambda t: np.interp(((t + np.pi) % (2 * np.pi)) - np.pi, tt, aa)
        # the drawn opening's θ is measured in the front view with x toward his left: mirror for the right eye
        a_new = lambda t: np.arcsin(np.clip(O(t if side == 1 else np.pi - t) / R, 0, 0.999))
        for L, w in zip(rings, OUTER_W):
            r, a, t = sph(V[L], c1, F1)
            X = from_sph(R + (r - R1), a_new(t) + (a - a_old(t)) * 1.0, t, c2, F2)
            V[L] = w * X + (1 - w) * V[L]
        # the lid between the placed rings and the face: a smooth membrane over the ball (Laplacian relaxation with the
        # placed rings and everything outside ring 390 held, pushed out to clear the ball)
        free = np.unique(np.concatenate(rings[2:]))
        V = relax(V, Q, free, c2, R + 1.4, it=60)
        allin = np.unique(np.concatenate(lin))
        # the deepest socket: every vertex near the old ball that is in no ring
        inring = np.zeros(len(V), bool); inring[np.concatenate(rings + lin)] = True
        r_all, _, _ = sph(V, c1, F1)
        deep = np.where(~inring & (r_all < R1 + 2.5))[0]
        for L in [allin, deep]:
            r, a, t = sph(V[L], c1, F1)
            ao, an = a_old(t), a_new(t)
            a2 = an + (a - ao) * (np.pi - an) / np.maximum(np.pi - ao, 1e-3)
            V[L] = from_sph(R + 0.15 + np.maximum(r - R1, 0) * 0.3, a2, t, c2, F2)
        balls[key] = (c2, R)
    return V, balls


def relax(V, Q, free, c, rmin, it=60, lam=0.5):
    nb = [np.array(Q.neighbours(v)) for v in free]
    for _ in range(it):
        M = np.array([V[n].mean(0) for n in nb])
        V[free] += lam * (M - V[free])
        d = V[free] - c; r = np.linalg.norm(d, axis=1); k = r < rmin
        V[free[k]] = c + d[k] / r[k, None] * rmin
    return V
