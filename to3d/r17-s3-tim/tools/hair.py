"""Тим's hair: one cap laid over the designed head (head.py's form, a centimetre and a half thicker), from the crown
down to an edge that is the drawing's own — in front the fringe's saw teeth, read off the front view's hair shape
(views.HAIR_F: its lowest point at each x), over the ears and down to the nape behind; the edge's last row lies on the
skin. The cowlick's two spikes, the tuft at the temple and two at the nape are flat cones on it."""
import numpy as np
import drawing as D, head as Hd, views as VW, mesh as M

K = D.K
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))
P = Hd.P
Y0, YTOP = -84.0, -123.0          # the dome over the ring at Y0 rises to YTOP


def dims(y, t):
    """The hair's half-width, front, back at drawing height y, t units thicker than the head."""
    k = 1.0
    if y < Y0:
        k = np.sqrt(max(1 - ((Y0 - y) / (Y0 - YTOP)) ** 2, 0.0)); y = Y0
    w, zf, zb = Hd.shape(y)
    zc = (zf + zb) / 2
    return k * (w + t), zc + k * (zf + t - zc), zc + k * (zb - t - zc)


def point(y, th, t):
    a, zf, zb = dims(y, t); zc = (zf + zb) / 2
    s, c = np.sin(th), np.cos(th)
    return np.array([a * np.sign(s) * abs(s) ** (2 / P), y, zc + ((zf - zc) if c > 0 else (zc - zb)) * np.sign(c) * abs(c) ** (2 / P)])


def build(ctx):
    C, I, NJ = ctx['C'], ctx['I'], ctx['NJ']
    fr = D.sample(VW.HAIR_F)

    sd = D.sample(VW.HAIR_S)

    def fringe(x):                 # the front view's hair shape: its lowest point at x (the side tuft left out)
        s = D.span(fr, float(np.clip(x, -104, 104)), ax=0)
        return min(s[1], 6.0) if s else 4.0

    def sidefr(z):                 # the profile's hair shape: its lowest point at z
        s = D.span(sd, float(np.clip(z, -108, 96)), ax=0)
        return s[1] if s else 4.0

    rows, cols, T_TOP, T_EDGE = 26, 260, 15.0, 9.0
    V = np.zeros((rows + 1, cols, 3))
    for c in range(cols):
        th = 2 * np.pi * c / cols
        d = abs((th + np.pi) % (2 * np.pi) - np.pi)          # 0 in front … π behind
        # in front the front view's fringe; toward the temples the higher of the two views' edges; behind the profile's
        zref = point(30.0, th, T_EDGE)[2]
        low = 24 * smooth((d - np.radians(105)) / np.radians(40))      # the nape lower than the profile's line shows
        if d > np.radians(98): ye = sidefr(zref) + low
        else:
            uf = smooth((d - np.radians(34)) / np.radians(20)); ub = smooth((d - np.radians(84)) / np.radians(14))
            ye = -40.0
            for _ in range(24):
                p = point(ye, th, T_EDGE); f = fringe(p[0]); s_ = sidefr(p[2]); m_ = f * (1 - uf) + min(f, s_) * uf
                ye += 0.4 * (m_ * (1 - ub) + sidefr(zref) * ub - ye)
        for r in range(rows):
            v = r / (rows - 1)
            y = YTOP + (ye - YTOP) * v ** 0.85
            V[r, c] = point(y, th, T_TOP + (T_EDGE - T_TOP) * v)
        V[rows, c] = point(ye + 2, th, 1.5)                  # the edge laid on the skin
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
        v, t = np.array(v), np.array(t)
        parts.append((v, t))

    # x, y, z in drawing units (z forward): base, tip, half-widths across and through, the flat side's direction
    cone((-12, -112, -8), (-30, -152, -16), 20, 11, (1, 0, 0))
    cone((22, -112, 2), (16, -158, 6), 19, 11, (1, 0, 0))
    cone((96, -30, 50), (128, -48, 62), 16, 8, (0, 1, 0))
    cone((-30, 22, -92), (-36, 62, -112), 16, 8, (1, 0, 0))
    cone((34, 26, -90), (44, 60, -106), 15, 8, (1, 0, 0))
    cone((-96, -20, -40), (-124, -8, -62), 15, 8, (0, 1, 0))
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
    curve = -108 + 0.0016 * xd ** 2 - 0.12 * xd
    hi = (yd > curve) & (yd < curve + 10) & (xd > -72) & (xd < 52) & (V[:, 2] > 0) & (np.arange(n) < len(parts[0][0]))
    col[hi] = C['hairH']
    # the shade follows a smoothed form: big clean shapes
    A = M.adjacency(n, [list(t) for t in T])
    pn = M.vertex_normals(M.smooth(V3, A, np.ones(n, bool), iters=30, lam=0.5), T)
    return dict(V=V3, T=T, W=W, col=col, shd=shd, lin=lin, pn=pn, pw=np.full(n, 0.7))
