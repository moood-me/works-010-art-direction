"""The hair (Р1's hair.py, for С15): one shell from the crown down to pointed ends. Its width is the front drawing's
outer mass, its depth the profile's; it is open where the face shows: the window's two edges are the drawn hairline
(a side parting on the picture's right, the fringe swept across the forehead to the picture's left), each laid on the
face; below the temples the edges go behind the ears and the hair hangs behind the neck and the shoulders."""
import numpy as np
from scipy.spatial import cKDTree
import drawing as D, mesh as M

K = D.K
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))
P = 2.3
TOP, RING_Y, END = D.CROWN, -128.0, 224.0


def _span(d, yy):
    return D.profile(d, np.atleast_1d(yy))


def build(ctx):
    C, J1, I, NJ = ctx['C'], ctx['J1'], ctx['I'], ctx['NJ']
    hv, ht = ctx['head']
    hn = M.vertex_normals(hv, ht)
    hyd, hxd = D.FLOOR - hv[:, 1] / K, hv[:, 0] / K
    hyd[np.setdiff1d(np.arange(len(hv)), np.unique(ht))] = 1e9
    ys = np.arange(TOP, END + 8, 2.0)
    bf, ff = _span(D.HAIR['back_f'], ys), _span(D.HAIR['front_f'], ys)
    bs, fs = _span(D.HAIR['back_s'], ys), _span(D.HAIR['front_s'], ys)
    nz = lambda a, v: np.nan_to_num(a, nan=v)
    a_t = np.maximum.reduce([nz(-bf[:, 0], 0), nz(bf[:, 1], 0), nz(-ff[:, 0], 0), nz(ff[:, 1], 0)]) + 2
    zb_t = np.minimum(nz(bs[:, 0], 0), nz(fs[:, 0], 0)) - 2
    zf_top = np.maximum(nz(fs[:, 1], -1e9), nz(bs[:, 1], -1e9))
    # the window's edges (units): the drawn hairline, then behind the ears
    wy = lambda pts: (np.array([(p[0] - D.EYE) * D.HS for p in pts]), np.array([p[1] * D.HS for p in pts]))
    yr, xr = wy(D.WIN_R); yl, xl = wy(D.WIN_L)
    apex = yr[0]
    w_r = np.where(ys < apex, xr[0], np.interp(ys, yr, xr))
    w_l = np.where(ys < apex, xl[0], np.interp(ys, yl, xl))
    ear_y = (0 - D.EYE) * D.HS
    # below the temples the edges go behind the ears, lying on the head, then down and in to the neck's sides: the
    # hair hangs behind the neck as a mass with a front of its own (the front drawing shows it either side of the neck)
    back_r, back_l = smooth((ys + 76) / 44), smooth((ys + 22) / 30)      # the right from the temple; the left after the fringe's tip
    w_low = np.interp(ys, [ear_y, 50, 92, 128, END], [84, 82, 62, 44, 50])
    w_r = np.minimum(w_r, 85) * (1 - back_r) + w_low * back_r      # on the head, not past its side
    w_l = np.maximum(w_l, -85) * (1 - back_l) - w_low * back_l
    behind = np.interp(ys, [-50, 0, 50, 92, 128, END], [-12, -62, -76, -52, -32, -36])

    def on_face(w):
        ze = np.full(len(ys), np.nan)
        for i, (y, x) in enumerate(zip(ys, w)):
            m = (abs(hyd - y) < 6) & (abs(hxd - x) < 8)
            if m.sum(): ze[i] = hv[m, 2].max() / K + 8
        return ze
    def edge_z(w, back):
        ze = on_face(w)
        ze = np.where(ys < apex, np.nan, ze)
        ze = np.where(back > 0.05, np.nan, ze)
        ze = np.where(back > 0.95, behind, ze)
        ok = ~np.isnan(ze)
        ze = np.interp(ys, ys[ok], ze[ok])
        low = ys > apex + 8          # an even edge (the head's own small forms are not the hair's)
        ze[low] = np.convolve(np.pad(ze, 6, mode='edge'), np.ones(13) / 13, 'valid')[low]
        return ze
    ze_r, ze_l = edge_z(w_r, back_r), edge_z(w_l, back_l)
    zc_t = np.interp(ys, [TOP, -100, 60, 140, END], [4, -4, -12, -66, -80])

    def shape(y):
        k = 1.0
        if y < RING_Y:      # the crown: a dome over the ring
            k = np.sqrt(max(1 - ((RING_Y - y) / (RING_Y - TOP + 0.4)) ** 2, 1e-8)); y = RING_Y
        g = lambda arr: np.interp(y, ys, arr)
        zc = g(zc_t); closed = y < apex
        zft = zc + k * (g(zf_top) - zc)
        return (k * g(a_t), zc, zc - k * (zc - g(zb_t)), k * g(w_r), k * g(w_l), zft if closed else g(ze_r), zft if closed else g(ze_l))

    # a ring: on each side a front piece from the window's edge (w, ze) round the corner to the side (±a, zs), then
    # the back piece from the side to the back's middle (0, zb). zs is the ring's middle, or the edge's depth when the
    # edge lies behind it (the hair hanging behind the neck has a flat front of its own)
    rows, NF, NB = 150, 26, 34
    cols = 2 * (NF + NB)
    S_ = lambda t: np.sin(t * np.pi / 2) ** (2 / P)
    C_ = lambda t: np.cos(t * np.pi / 2) ** (2 / P)

    def point(y, c):
        a, zc, zb, wr, wl, zr, zl = shape(y)
        a = max(a, 1e-3)
        right = c < cols // 2
        k = c if right else cols - 1 - c           # 0 at the edge … NF+NB−1 at the back's middle
        sg, w, z_e = (1, wr, zr) if right else (-1, wl, zl)
        zs = min(zc, z_e)
        if k < NF:
            t = k / NF
            return w + (sg * a - w) * S_(t), zs + (z_e - zs) * C_(t)
        t = (k - NF) / (NB - 0.5)
        return sg * a * C_(t), zs - (zs - zb) * S_(t)

    V = np.zeros((rows, cols, 3))
    for r in range(rows):
        v = r / (rows - 1)
        y0 = TOP - 0.4 + (END - TOP + 0.4) * v
        # pointed ends: the lowest rows rise between the locks (big angular points, as drawn)
        lock = np.abs(np.sin(5.0 * np.pi * (np.arange(cols) + 6) / (cols + 11)))
        y = y0 - 56 * (1 - lock) ** 0.9 * smooth((v - 0.7) / 0.3)
        for c in range(cols):
            x, z = point(y[c], c)
            V[r, c] = [x * K, (D.FLOOR - y[c]) * K, z * K]
    V = V.reshape(-1, 3)
    T = []
    for r in range(rows - 1):
        for c in range(cols - 1):
            a0 = r * cols + c; a1 = a0 + 1; b0 = a0 + cols; b1 = b0 + 1
            T += [[a0, b0, a1], [a1, b0, b1]]
    T = np.array(T)
    # out of the head
    used = np.unique(ht); hv_u, hn_u = hv[used], hn[used]
    tree = cKDTree(hv_u)
    for _ in range(3):
        dd, ii = tree.query(V)
        s = ((V - hv_u[ii]) * hn_u[ii]).sum(1)
        m = s < 0.009
        V[m] += hn_u[ii[m]] * (0.009 - s[m])[:, None]
    # out of the clothes (their rings, as ellipses), below the chin
    def push(rows_, margin):
        r_ = np.array(rows_); o = np.argsort(r_[:, 0]); r_ = r_[o]
        for i, p in enumerate(V):
            if p[1] > r_[-1, 0] + 0.02 or p[1] < r_[0, 0]: continue
            a, zc, df, db = [np.interp(p[1], r_[:, 0], r_[:, k]) for k in range(1, 5)]
            dz = p[2] - zc; d = df if dz > 0 else db
            rr = np.hypot(p[0] / a, dz / d)
            if rr < margin:
                V[i, 0] *= margin / rr; V[i, 2] = zc + dz * margin / rr
    push(ctx['card'], 1.07)
    A = M.adjacency(len(V), [list(t) for t in T])
    yd = D.FLOOR - V[:, 1] / K
    V = M.smooth(V, A, np.ones(len(V), bool), iters=2, lam=0.5)
    Vg = V.reshape(rows, cols, 3)          # above the parting's end the two edges are one line
    for r in range(rows):
        if TOP - 0.4 + (END - TOP + 0.4) * r / (rows - 1) < apex + 2: Vg[r, 0] = Vg[r, -1] = (Vg[r, 0] + Vg[r, -1]) / 2
    V = M.smooth(V, A, (yd > -80) & (yd < 20), iters=8, lam=0.5)      # where the edge leaves the face for behind the ear
    n = len(V)
    W = np.zeros((n, NJ))
    wh = 1 - 0.8 * smooth((yd - 110) / 110)
    W[:, I['Head']] = wh; W[:, I['Chest']] = (1 - wh) * 0.7; W[:, I['Neck1']] = (1 - wh) * 0.3
    col = np.tile(C['hair'], (n, 1)); shd = np.tile(C['black'], (n, 1)); lin = np.tile(C['rim'], (n, 1))
    # the shade follows a smoothed form of the hair: big clean shapes, not every ripple of the shell
    Vs = M.smooth(V, A, np.ones(n, bool), iters=40, lam=0.5)
    pn = M.vertex_normals(Vs, T)
    return dict(V=V, T=T, W=W, col=col, shd=shd, lin=lin, pn=pn, pw=np.ones(n))
