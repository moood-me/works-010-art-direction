"""Кира's hair: one cap over the designed head (head.py's form, about a centimetre thicker) that hangs straight down
from the head's widest places — a choppy bob. Its lower edge is the drawing's own: in front the lowest point of the
front view's hair at each x (kira.NEAR_F and FRINGE_F: the long fringe slanting over her left eye, the lock by her right
cheek), behind the profile's choppy ends (kira.HAIR_S). On the forehead the edge's last row lies on the skin. A few
flat cones are the tufts that stick out. Built in the head's own units, upright; build.py pitches it with the head."""
import numpy as np
import drawing as D, head as Hd, shapes as VW, mesh as M

K = D.K
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))
P = Hd.P
Y0, YTOP = -96.0, -139.0          # the dome over the ring at Y0 rises to YTOP
# the hair's own form below the head's widest places: it hangs, it does not follow the jaw in
W_H = np.maximum.accumulate(Hd.W_T); ZB_H = np.minimum.accumulate(Hd.ZB_T)


def dims(y, t):
    """The hair's half-width, front, back at height y, t units thicker than the head."""
    k = 1.0
    if y < Y0:
        k = np.sqrt(max(1 - ((Y0 - y) / (Y0 - YTOP)) ** 2, 0.0)); y = Y0
    w, zb = np.interp(y, Hd.BINS, W_H), np.interp(y, Hd.BINS, ZB_H); zf = Hd.shape(y)[1]
    zc = (zf + zb) / 2
    return k * (w + t), zc + k * (zf + t - zc), zc + k * (zb - t - zc)


def point(y, th, t):
    a, zf, zb = dims(y, t); zc = (zf + zb) / 2
    s, c = np.sin(th), np.cos(th)
    return np.array([a * np.sign(s) * abs(s) ** (2 / P), y, zc + ((zf - zc) if c > 0 else (zc - zb)) * np.sign(c) * abs(c) ** (2 / P)])


def build(ctx):
    C, I, NJ = ctx['C'], ctx['I'], ctx['NJ']
    fr = [p for d in VW.HAIR_FRONT for p in D.sample(d)]
    sd = D.sample(VW.HAIR_S)

    def front(x):                  # the front view's hair: its lowest point at x; the lock by the cheek a little further out
        if x < -60: x += 12
        s = D.span(fr, float(np.clip(x, -112, 108)), ax=0)
        return s[1] if s else -72.0

    def ends(z):                   # the profile's choppy ends: the hair's lowest point at z
        s = D.span(sd, float(np.clip(z, -126, -48)), ax=0)
        return s[1] if s else 90.0

    rows, cols, T_TOP, T_EDGE = 30, 280, 12.0, 9.0
    V = np.zeros((rows + 1, cols, 3))
    for c in range(cols):
        th = 2 * np.pi * c / cols
        d = abs((th + np.pi) % (2 * np.pi) - np.pi)          # 0 in front … π behind
        lim = np.radians(80 if np.sin(th) > 0 else 62)       # her left: the fringe's side; her right: the lock begins earlier
        back = ends(-48 - 70 * np.clip((d - lim) / (np.pi - lim), 0, 1))
        ub = smooth((d - lim) / np.radians(12))
        ye = -40.0
        if ub < 1:
            for _ in range(24):
                ye += 0.4 * (front(point(ye, th, T_EDGE)[0]) - ye)
        ye = ye * (1 - ub) + back * ub
        for r in range(rows):
            v = r / (rows - 1)
            y = YTOP + (ye - YTOP) * v ** 0.85
            V[r, c] = point(y, th, T_TOP + (T_EDGE - T_TOP) * v)
        V[rows, c] = point(ye + 2, th, 1.5 if ye < 40 else T_EDGE * 0.5)      # on the forehead the edge lies on the skin
    V = V.reshape(-1, 3)
    T = []
    for r in range(rows):
        for c in range(cols):
            a0, a1 = r * cols + c, r * cols + (c + 1) % cols; b0, b1 = a0 + cols, a1 + cols
            T += [[a0, a1, b0], [a1, b1, b0]]
    T = np.array(T)
    parts = [(V, T)]

    def cone(base, tip, r1, r2, ax, n=14, rings=5):
        base, tip, ax = np.array(base, float), np.array(tip, float), np.array(ax, float)
        d = tip - base; ax = ax - d * (ax @ d) / (d @ d); ax /= np.linalg.norm(ax); bx = np.cross(d / np.linalg.norm(d), ax)
        v = []
        for i in range(rings):
            s = i / (rings - 1); k = (1 - s) ** 0.9
            for j in range(n):
                a = 2 * np.pi * j / n
                v.append(base + d * s + k * (r1 * np.cos(a) * ax + r2 * np.sin(a) * bx))
        t = []
        for i in range(rings - 1):
            for j in range(n):
                a0, a1 = i * n + j, i * n + (j + 1) % n; b0, b1 = a0 + n, a1 + n
                t += [[a0, a1, b0], [a1, b1, b0]]
        parts.append((np.array(v), np.array(t)))

    # x, y, z in the head's units (z forward): base, tip, half-widths across and through, the flat side's direction
    cone((-92, -98, -40), (-106, -116, -54), 13, 7, (1, 0, 0))
    cone((-104, -26, -34), (-134, -20, -48), 14, 7, (0, 1, 0))
    cone((-102, 66, -44), (-128, 90, -56), 14, 7, (0, 1, 0))
    cone((102, 66, -44), (128, 90, -56), 14, 7, (0, 1, 0))
    cone((-10, -60, -100), (-16, -46, -126), 14, 7, (1, 0, 0))
    cone((50, 10, -92), (64, 26, -116), 13, 7, (1, 0, 0))
    n0 = 0; Vs, Ts = [], []
    for v, t in parts: Vs.append(v); Ts.append(t + n0); n0 += len(v)
    V = np.vstack(Vs); T = np.vstack(Ts)
    V3 = np.c_[V[:, 0] * K, (D.FLOOR - V[:, 1]) * K, V[:, 2] * K]
    n0 = 0
    for v, t in parts:               # every part faces outward (in metres: the drawing's y is down)
        tt = T[n0:n0 + len(t)]; c = V3[np.unique(tt)].mean(0)
        if (M.vertex_normals(V3, tt)[np.unique(tt)] * (V3[np.unique(tt)] - c)).sum(1).mean() < 0: T[n0:n0 + len(t)] = tt[:, ::-1]
        n0 += len(t)
    n = len(V3)
    W = np.zeros((n, NJ)); W[:, I['Head']] = 1
    col = np.tile(C['hair'], (n, 1)); shd = np.tile(C['hairS'], (n, 1)); lin = np.tile(C['hairL'], (n, 1))
    # the highlight: a band across the top front, as drawn
    xd, yd = V[:, 0], V[:, 1]
    curve = -124 + 0.0022 * (xd - 30) ** 2
    hi = (yd > curve) & (yd < curve + 9) & (xd > -24) & (xd < 84) & (V[:, 2] > 0) & (np.arange(n) < len(parts[0][0]))
    col[hi] = C['hairH']
    A = M.adjacency(n, [list(t) for t in T])
    pn = M.vertex_normals(M.smooth(V3, A, np.ones(n, bool), iters=30, lam=0.5), T)
    return dict(V=V3, T=T, W=W, col=col, shd=shd, lin=lin, pn=pn, pw=np.full(n, 0.7))
