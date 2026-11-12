"""Small mesh makers: a parametric grid cut by a margin with a smooth edge, an ellipsoid, a tube along a line."""
import numpy as np


def grid_cut(point, u, v, margin=None, closed_u=True):
    """point(U, V) -> X, Y, Z on a (nu, nv) grid of parameters u (around), v (along).
    margin(X, Y, Z, U, V) > 0 where the surface is kept; quads with a corner inside are kept and their outside
    corners slide along the grid toward the inside ones to where the margin crosses zero (no staircase edge).
    Returns verts (n, 3), quads (m, 4)."""
    U, Vv = np.meshgrid(u, v, indexing='ij')
    nu, nv = U.shape
    X, Y, Z = point(U, Vv)
    if margin is None:
        f = np.ones_like(U)
    else:
        f = margin(X, Y, Z, U, Vv)
    inside = f > 0
    U2, V2 = U.copy(), Vv.copy()
    su = np.zeros_like(U); sv = np.zeros_like(U); cnt = np.zeros_like(U)
    span = (u[-1] - u[0]) * nu / max(nu - 1, 1) if closed_u else None
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        fi = np.roll(f, (-di, -dj), (0, 1))
        ui = np.roll(U, (-di, -dj), (0, 1)); vi = np.roll(Vv, (-di, -dj), (0, 1))
        bad = np.zeros_like(inside)
        if dj:
            bad[:, -1 if dj > 0 else 0] = True
        if di and not closed_u:
            bad[-1 if di > 0 else 0, :] = True
        fi = np.where(bad, -1, fi)
        if closed_u:
            ui = np.where(np.abs(ui - U) > span / 2, ui + np.sign(U - ui) * span, ui)
        m = (~inside) & (fi > 0)
        t = np.clip(f / (f - fi + 1e-12), 0, 1)
        su += np.where(m, U + (ui - U) * t, 0); sv += np.where(m, Vv + (vi - Vv) * t, 0); cnt += m
    mv = cnt > 0
    U2[mv], V2[mv] = su[mv] / cnt[mv], sv[mv] / cnt[mv]
    X, Y, Z = point(U2, V2)
    verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    q = []
    for i in range(nu if closed_u else nu - 1):
        for j in range(nv - 1):
            a = i * nv + j
            b = ((i + 1) % nu) * nv + j
            q.append((a, b, b + 1, a + 1))
    q = np.array(q)
    ins, ok = inside.ravel(), (inside | mv).ravel()
    q = q[ins[q].any(1) & ok[q].all(1)]
    return compact(verts, q)


def compact(V, F):
    used = np.unique(F[F >= 0])
    remap = -np.ones(len(V), int)
    remap[used] = np.arange(len(used))
    F2 = np.where(F >= 0, remap[np.maximum(F, 0)], -1)
    return V[used], F2


def ellipsoid(c, radii, R=np.eye(3), nu=32, nv=16):
    u = np.linspace(0, 2 * np.pi, nu, endpoint=False)
    v = np.linspace(0, np.pi, nv + 1)[1:-1]
    U, Vv = np.meshgrid(u, v, indexing='ij')
    P = np.stack([np.cos(U) * np.sin(Vv) * radii[0], np.cos(Vv) * radii[1], np.sin(U) * np.sin(Vv) * radii[2]], -1)
    P = P.reshape(-1, 3)
    P = np.vstack([P, [[0, radii[1], 0], [0, -radii[1], 0]]])
    P = P @ np.asarray(R).T + np.asarray(c, float)
    n1 = nv - 1
    F = []
    for i in range(nu):
        for j in range(n1 - 1):
            a, b = i * n1 + j, ((i + 1) % nu) * n1 + j
            F.append((a, a + 1, b + 1, b))
        top, bot = len(P) - 2, len(P) - 1
        F.append((top, i * n1, ((i + 1) % nu) * n1, -1))
        F.append((bot, ((i + 1) % nu) * n1 + n1 - 1, i * n1 + n1 - 1, -1))
    return P, np.array(F)


def tube(pts, r, nseg=8, closed=False):
    """A round tube of radius r along pts (a thin ink line, or a chain)."""
    P = np.asarray(pts, float)
    if closed:
        P = np.vstack([P, P[:1]])
    n = len(P)
    T = np.gradient(P, axis=0)
    for i in np.nonzero(np.linalg.norm(T, axis=1) < 1e-9)[0]:      # a point where the line turns back on itself
        T[i] = P[i] - P[i - 1] if i else P[1] - P[0]
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    S = np.cross(T, [0, 0, 1.0])
    bad = np.linalg.norm(S, axis=1) < 1e-4
    S[bad] = np.cross(T[bad], [1, 0, 0])
    S /= np.linalg.norm(S, axis=1, keepdims=True)
    Uu = np.cross(S, T)
    a = np.linspace(0, 2 * np.pi, nseg, endpoint=False)
    Q = P[:, None] + r * (S[:, None] * np.cos(a)[None, :, None] + Uu[:, None] * np.sin(a)[None, :, None])
    V = Q.reshape(-1, 3)
    F = []
    for i in range(n - 1):
        for j in range(nseg):
            F.append((i * nseg + j, i * nseg + (j + 1) % nseg, (i + 1) * nseg + (j + 1) % nseg, (i + 1) * nseg + j))
    if not closed:
        for end in (0, n - 1):
            c = len(V)
            V = np.vstack([V, P[end]])
            for j in range(nseg):
                F.append((end * nseg + j, end * nseg + (j + 1) % nseg, c, -1))
    return V, np.array(F)
