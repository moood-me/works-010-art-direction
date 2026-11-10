"""Марат's sculpted curls, from the drawing's own hair (`marat.marat_hair`): the drawing lays curls as a jittered
honeycomb of spots over the head (hair.curl_spots: a point, a radius — the same seed, the same curls) and draws each as
a small lit ball with a spiral cut. Here each spot becomes a real ball of clay (a little flattened onto the head, its
spiral in the bump of the material), over an under-mass that closes the gaps: the cap over the skull above the
drawing's hairline, and for the beard a bowl hanging from the jaw (the drawing's `beard_at`).
The moustache's curls go with the mouth's shapes and are made in face.py.
Output: CACHE/hair.npz — V (head units, engine axes), T, uv (round the curl, from its top 0 … 1; the under-mass: −9)."""
import math
import numpy as np
import drawing
from drawing import H0, P
from common import CACHE, hu





def cap_mesh(line, k, rows=40, cols=144, thick=0.03):
    """the cap: the loft scaled by k, from the crown down to the hairline — each column of the grid ends exactly on
    the line, so the edge is the drawing's hairline — with an inner wall, so the edge reads as a lip of sculpted hair"""
    ph = np.linspace(-math.pi, math.pi, cols, endpoint=False)
    Vo, Vi = [], []
    for r in range(rows):
        s_ = r / (rows - 1)
        for p in ph:
            y = -0.5 + (line(p) + 0.5) * (1 - (1 - s_) ** 1.0) if True else 0
            y = -0.497 + (line(p) + 0.497) * s_
            Vo.append(H0.surf(p, y, 0.018, k)); Vi.append(H0.surf(p, y, 0.018 - thick, k))
    Vo = hu(np.array(Vo)); Vi = hu(np.array(Vi))
    T = []
    idx = lambda r, j: r * cols + j % cols
    for r in range(rows - 1):
        for j in range(cols):
            a, b, c, d = idx(r, j), idx(r, j + 1), idx(r + 1, j), idx(r + 1, j + 1)
            T += [(a, c, b), (b, c, d)]
    # the crown: a fan to a pole a little above the skull's top (the loft narrows to a point there)
    po = len(Vo)
    Vo = np.r_[Vo, [[0.0, 0.535, Vo[:cols, 2].mean()]]]; Vi = np.r_[Vi, [[0.0, 0.505, Vi[:cols, 2].mean()]]]
    T += [(po, j, (j + 1) % cols) for j in range(cols)]
    T = np.array(T)
    # laid on the fitted head itself (it is rounder than the loft at the crown): outer 2.5 % of the head above it
    import igl
    from common import vertex_normals
    hd = np.load(f'{CACHE}/head_raw.npz'); HV = hd['V']; HT = __import__('base').tris(hd['Q'])
    HN = vertex_normals(HV, HT)
    _, I, C = igl.point_mesh_squared_distance(Vo, HV, HT)
    Nf = HN[HT[I]].mean(1); Nf /= np.linalg.norm(Nf, axis=1, keepdims=True)
    Vo = C + Nf * 0.02; Vi = C - Nf * 0.004
    n = len(Vo)
    last = np.arange((rows - 1) * cols, rows * cols); nxt = np.roll(last, -1)
    W = np.r_[np.stack([last, last + n, nxt], 1), np.stack([nxt, last + n, nxt + n], 1)]
    return np.r_[Vo, Vi], np.r_[T, T[:, ::-1] + n, W]


def orient(V, T, centre):
    """triangles turned so their normals point away from the centre on the whole"""
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    c = V[T].mean(1) - centre
    return T if (n * c).sum() > 0 else T[:, ::-1]


import marat as M
import hair as H

_BALL = None


def ball(nr=6, nc=12):
    """a unit ball, its pole along +z: rings from the pole"""
    global _BALL
    if _BALL is None:
        V = [(0, 0, 1.0)]; uv = [(0.0, 0.0)]
        for i in range(1, nr):
            th = math.pi * i / nr
            for j in range(nc):
                q = 2 * math.pi * j / nc
                V.append((math.sin(th) * math.cos(q), math.sin(th) * math.sin(q), math.cos(th))); uv.append((q, i / nr))
        V.append((0, 0, -1.0)); uv.append((0.0, 1.0))
        T = [(0, 1 + j, 1 + (j + 1) % nc) for j in range(nc)]
        for i in range(nr - 2):
            for j in range(nc):
                a, b = 1 + i * nc + j, 1 + i * nc + (j + 1) % nc
                T += [(a, a + nc, b), (b, a + nc, b + nc)]
        last = len(V) - 1; s = 1 + (nr - 2) * nc
        T += [(last, s + (j + 1) % nc, s + j) for j in range(nc)]
        _BALL = (np.array(V), np.array(T), np.array(uv))
    return _BALL


def curls(spots, centre_of, flat=0.78):
    """spots [(point (drawing axes), radius, facing, start angle, winding)] → balls, each flattened along its outward
    direction (away from centre_of(point)) and sunk a little; uv: (angle + start, 0 at the top … 1), the winding's sign in
    the angle"""
    BV, BT, BUV = ball()
    Vs, Ts, UVs = [], [], []; n = 0
    for p, r, _, a0, wind in spots:
        c = hu(np.array(p)); o = c - centre_of(c); o /= np.linalg.norm(o)
        e1 = np.cross(o, [0, 1.0, 0.3]); e1 /= np.linalg.norm(e1); e2 = np.cross(o, e1)
        R = np.stack([e1, e2, o], 1)
        v = (BV * np.array([1, 1, flat]) * r) @ R.T + c - o * r * 0.15
        Vs.append(v); Ts.append(BT + n); UVs.append(np.c_[wind * BUV[:, 0] + a0, BUV[:, 1]]); n += len(v)
    return np.concatenate(Vs), np.concatenate(Ts), np.concatenate(UVs)


def beard_at(phi, y):
    """marat.marat_hair's beard: on the face down to the jaw, then a bowl of its own hanging from it"""
    h = H0
    if y <= M.JAW:
        return h.surf(phi, y, 0.02 + 0.03 * max(0.0, (y - 0.1) / (M.JAW - 0.1)))
    base = h.surf(phi, M.JAW, 0.05)
    t = (y - M.JAW) / (M.BEARD_END - M.JAW)
    s = math.sqrt(max(0.0, 1 - t ** 2.4))
    cz = h.c(M.JAW)
    return (base[0] * s, y, cz + (base[2] - cz) * (0.3 + 0.7 * s) + 0.04 * t)


def beard_rad(y):
    r = (H0.a(M.JAW) + H0.b(M.JAW)) / 2
    return r if y <= M.JAW else r * math.sqrt(max(0.02, 1 - ((y - M.JAW) / (M.BEARD_END - M.JAW)) ** 2.4))


def beard_mass(nphi=96, ny=60):
    """the under-mass of the beard: the drawing's beard surface itself as a grid, kept below the beard's upper edge"""
    ph = np.linspace(-1.95, 1.95, nphi); ys = np.linspace(-0.1, M.BEARD_END - 0.004, ny)
    V = np.array([beard_at(p, y) for y in ys for p in ph])
    f = np.array([M._beard_top(abs(p)) - y for y in ys for p in ph])
    T = []
    for i in range(ny - 1):
        for j in range(nphi - 1):
            a, b = i * nphi + j, i * nphi + j + 1
            if max(f[a], f[b], f[a + nphi], f[b + nphi]) < 0.03: T += [(a, a + nphi, b), (b, a + nphi, b + nphi)]
    T = np.array(T); used = np.unique(T); re = -np.ones(len(V), int); re[used] = np.arange(len(used))
    return hu(V[used]), re[T]


def build():
    centre = np.array([0.0, 0.05, -0.02])
    Vs, Ts, UVs, KIND = [], [], [], []
    n = 0

    def add(v, t, uv, kind):
        nonlocal n
        Vs.append(v); Ts.append(t + n); UVs.append(uv); KIND.append(np.full(len(v), kind)); n += len(v)
    CV, CT = cap_mesh(M._hairline, 1.02)
    add(CV, orient(CV, CT, centre), np.full((len(CV), 2), -9.0), 0)
    top = H.curl_spots(H0, lambda phi, y: y <= M._hairline(phi), 0.052, -0.5, 0.25, out=0.03, k=1.0, seed=4)
    v, t, uv = curls(top, lambda c: centre)
    add(v, t, uv, 1)
    BV_, BT_ = beard_mass()
    jawc = hu(np.array([0.0, M.JAW, H0.c(M.JAW)]))
    add(BV_, orient(BV_, BT_, jawc), np.full((len(BV_), 2), -9.0), 2)
    beard = H.curl_spots(H0, lambda phi, y: M._beard_top(abs(phi)) <= y <= M.BEARD_END - 0.035, 0.044, -0.04, M.BEARD_END,
                         seed=9, place=beard_at, radius=beard_rad)
    v, t, uv = curls(beard, lambda c: np.array([0.0, min(c[1], jawc[1] + 0.1), jawc[2] - 0.05]))
    add(v, t, uv, 3)
    V = np.concatenate(Vs); T = np.concatenate(Ts)
    np.savez(f'{CACHE}/hair.npz', V=V, T=T, uv=np.concatenate(UVs), kind=np.concatenate(KIND))
    print('hair', len(top), 'curls on top,', len(beard), 'in the beard;', len(V), 'vertices')
    return V, T


if __name__ == '__main__':
    build()
