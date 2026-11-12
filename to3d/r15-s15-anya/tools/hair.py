"""The hair: one shell from the crown down to pointed ends, its width from the drawing's front (the back mass), its
depth from the profile, open in front where the face shows (the curtains' inner edges, drawn), the window's edge laid
on the face; below the chin it lies over the shoulders (pushed out of the clothes and the head)."""
import numpy as np
from scipy.spatial import cKDTree
import drawing as D, anya, mesh as M

K = D.K
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))
P = 2.3


def _span(d, yy):
    return D.profile(d, np.atleast_1d(yy))


def build(ctx):
    C, J1, I, NJ = ctx['C'], ctx['J1'], ctx['I'], ctx['NJ']
    hv, ht = ctx['head']
    hn = M.vertex_normals(hv, ht)
    hyd, hxd = D.FLOOR - hv[:, 1] / K, hv[:, 0] / K
    hyd[np.setdiff1d(np.arange(len(hv)), np.unique(ht))] = 1e9
    ys = np.arange(-142, 262, 2.0)
    back = _span(anya.BACK_F, ys)[:, 1]
    curt = _span(anya.CURT_F, ys)
    side = _span(anya.HAIR_S, ys)
    a_t = np.fmax(np.nan_to_num(back, nan=0), np.nan_to_num(-curt[:, 0], nan=0)) + 3
    zb_t = np.nan_to_num(side[:, 0], nan=-60) - 2
    zf_top = np.nan_to_num(side[:, 1], nan=40)
    # the face's window: the curtains' inner edge (a little wider, so more face shows as in the profile)
    inner = np.where(np.isnan(curt[:, 1]), 0, -curt[:, 1])        # CURT_F is the image-left curtain: its inner edge is x<0
    w_t = np.where(ys < -112, 0, np.clip(inner, 0, None) + 5 + 7 * smooth((ys + 100) / 40))
    w_t = np.where(ys > 236, np.nan, w_t)
    w_t = np.interp(ys, ys[~np.isnan(w_t)], w_t[~np.isnan(w_t)])
    # where the window's edge lies: on the face (its front at that width), below the chin by the neck
    ze = np.zeros_like(ys)
    for i, (y, w) in enumerate(zip(ys, w_t)):
        m = (abs(hyd - y) < 6) & (abs(abs(hxd) - w) < 8)
        ze[i] = hv[m, 2].max() / K + 9 if m.sum() else np.nan
    # half way back toward where the profile's hair begins (the profile shows more cheek than the front's curtains)
    ze = np.where(ys > 100, np.interp(ys, [100, 180, 262], [30, 6, 0]), ze)
    ok = ~np.isnan(ze); ze = np.interp(ys, ys[ok], ze[ok])
    zc_t = np.interp(ys, [-142, -100, 90, 160, 262], [10, -8, -8, -40, -46])

    def shape(y):
        # the crown: a dome over the ring at −126
        k = 1.0
        if y < -126:
            k = np.sqrt(max(1 - ((-126 - y) / 16.5) ** 2, 0.0004)); y = -126
        g = lambda arr: np.interp(y, ys, arr)
        zc = g(zc_t)
        return k * g(a_t), zc, zc - k * (zc - g(zb_t)), g(w_t), g(ze), zc + k * (g(zf_top) - zc)

    rows, cols = 150, 110
    V = np.zeros((rows, cols, 3)); TH = np.zeros((rows, cols))
    for r in range(rows):
        v = r / (rows - 1)
        y0 = -142.4 + (256 + 142.4) * v
        a, zc, zb, w, z_e, zft = shape(y0)
        a = max(a, 1.0)
        thw = np.arcsin(min((w / a), 0.98) ** (P / 2)) if w > 0 else 0.0
        th = np.linspace(thw, 2 * np.pi - thw, cols)
        # pointed ends: the lowest rows rise between the locks
        lock = np.abs(np.sin(4.5 * (th - thw) * np.pi / (2 * np.pi - 2 * thw) * 2))
        y = y0 - 30 * (1 - lock) ** 1.2 * smooth((v - 0.8) / 0.2)
        for c in range(cols):
            a, zc, zb, w, z_e, zft = shape(y[c])
            a = max(a, 1.0)
            thw_c = np.arcsin(min((w / a), 0.98) ** (P / 2)) if w > 0 else 0.0
            df = (z_e - zc) / max(np.cos(thw_c), 0.05) ** (2 / P) if w > 0 else zft - zc
            db = zc - zb
            s_, c_ = np.sin(th[c]), np.cos(th[c])
            x = a * np.sign(s_) * abs(s_) ** (2 / P)
            z = zc + (df if c_ > 0 else db) * np.sign(c_) * abs(c_) ** (2 / P)
            V[r, c] = [x * K, (D.FLOOR - y[c]) * K, z * K]
            TH[r, c] = th[c]
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
    push(ctx['dress'], 1.1)
    A = M.adjacency(len(V), [list(t) for t in T])
    yd = D.FLOOR - V[:, 1] / K
    V = M.smooth(V, A, yd > 120, iters=4, lam=0.5)
    n = len(V)
    W = np.zeros((n, NJ))
    wh = 1 - 0.8 * smooth((yd - 105) / 110)
    W[:, I['Head']] = wh; W[:, I['Chest']] = (1 - wh) * 0.7; W[:, I['Neck1']] = (1 - wh) * 0.3
    col = np.tile(C['hair'], (n, 1)); shd = np.tile(C['hairS'], (n, 1)); lin = np.tile(C['hairL'], (n, 1))
    xd = V[:, 0] / K
    curve = -128 + 0.40 * abs(xd)
    hi = (yd > curve - 1) & (yd < curve + 9) & (abs(xd) > 5) & (abs(xd) < 74) & (V[:, 2] > 0)
    col[hi] = C['hairH']
    # the shade follows a smoothed form of the hair: big clean shapes, not every ripple of the shell
    Vs = M.smooth(V, A, np.ones(n, bool), iters=40, lam=0.5)
    pn = M.vertex_normals(Vs, T)
    return dict(V=V, T=T, W=W, col=col, shd=shd, lin=lin, pn=pn, pw=np.ones(n))
