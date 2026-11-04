"""Тим's sculpted hair, from the drawing's own hair: `cast.tim_hair` builds its locks as 3D paths in head units
(H.surf_path / H.fall over the head's shell) with widths, and a cap over the skull above a hairline line(phi).
Here each lock becomes a solid: a flattened tube along its path (wide across the head, thin off it), narrow at the root,
tapering to a point, its top cut by lengthwise grooves (the drawing's `grooves`); the cap becomes a shell of the
head's loft (scaled by the drawing's k) above the hairline, with a thickness and a tucked-in edge.
Output: CACHE/hair.npz — V (head units, engine axes), T, uv (across −1…1, along 0…1; the cap: −9), lock id."""
import math
import numpy as np
import drawing
from drawing import H0, P
from common import CACHE, hu



def smooth_path(p, n=28):
    p = np.asarray(p, float)
    # resample by arc length, then a light smoothing (as the drawing's geom: resample + smooth)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    t = np.linspace(0, s[-1], n)
    q = np.array([np.interp(t, s, p[:, k]) for k in range(3)]).T
    for _ in range(2):
        q[1:-1] = (q[:-2] + 2 * q[1:-1] + q[2:]) / 4
    return q


def lock_mesh(L, centre, nu=28, nv=14, flat=0.42, grooves=2):
    """one lock: rings of nv points along the path"""
    c = smooth_path(hu(np.array(L.path3)), nu)
    tg = np.gradient(c, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True)
    V, UV = [], []
    for i in range(nu):
        t = i / (nu - 1)
        out = c[i] - centre; out -= (out @ tg[i]) * tg[i]; out /= np.linalg.norm(out)
        side = np.cross(tg[i], out)
        w = (L.w0 + (L.w1 - L.w0) * t ** L.taper) / 2
        w *= min(1.0, L.root + (1 - L.root) * t / 0.22)
        w *= (1 - t ** 6) ** 0.5 if L.w1 == 0 else 1.0           # a soft point at the tip
        w = max(w, 0.002)
        th = w * flat + 0.004
        for j in range(nv):
            a = 2 * math.pi * j / nv
            x, y = math.cos(a), math.sin(a)
            r = 1.0
            if y > 0 and grooves:                                  # grooves along the top
                r -= 0.16 * y * max(0.0, math.cos(a * (grooves + 1) * 2 / 2 * 2)) ** 3 * (1 - t ** 2)
            V.append(c[i] + side * x * w * r + out * (y * th * r + th * 0.15))
            UV.append((x, t))
    T = []
    for i in range(nu - 1):
        for j in range(nv):
            a, b = i * nv + j, i * nv + (j + 1) % nv
            T += [(a, b, a + nv), (b, b + nv, a + nv)]
    # close the root
    base = len(V); V.append(c[0] - tg[0] * 0.004); UV.append((0, 0))
    for j in range(nv):
        T.append((base, (j + 1) % nv, j))
    return np.array(V), np.array(T), np.array(UV)


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
    Vo = C + Nf * 0.022; Vi = C - Nf * 0.01
    n = len(Vo)
    last = np.arange((rows - 1) * cols, rows * cols); nxt = np.roll(last, -1)
    W = np.r_[np.stack([last, last + n, nxt], 1), np.stack([nxt, last + n, nxt + n], 1)]
    return np.r_[Vo, Vi], np.r_[T, T[:, ::-1] + n, W]


def orient(V, T, centre):
    """triangles turned so their normals point away from the centre on the whole"""
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    c = V[T].mean(1) - centre
    return T if (n * c).sum() > 0 else T[:, ::-1]


def build():
    hd = cast_hair()
    locks = hd['locks']
    line, yb, k = hd['cap']
    centre = np.array([0.0, 0.05, -0.02])
    Vs, Ts, UVs, ID = [], [], [], []
    n = 0
    CV, CT = cap_mesh(line, k)
    CT = orient(CV, CT, centre)
    Vs.append(CV); Ts.append(CT); UVs.append(np.full((len(CV), 2), -9.0)); ID.append(np.full(len(CV), -1)); n += len(CV)
    for i, L in enumerate(locks):
        v, t, uv = lock_mesh(L, centre, grooves=L.grooves + 1)
        t = orient(v, t, v.mean(0) - 0.3 * (v.mean(0) - centre))
        Vs.append(v); Ts.append(t + n); UVs.append(uv); ID.append(np.full(len(v), i)); n += len(v)
    V = np.concatenate(Vs); T = np.concatenate(Ts)
    np.savez(f'{CACHE}/hair.npz', V=V, T=T, uv=np.concatenate(UVs), lock=np.concatenate(ID))
    print('hair', len(locks), 'locks', len(V), 'vertices')
    return V, T


def cast_hair():
    class D:                        # the drawing's hair function wants a document only for defs; none are made here
        def uid(self, *_): return 'x'
        defs = []
    return P['hair'](H0, D(), P, drawing.EXPR['calm'])


if __name__ == '__main__':
    build()
