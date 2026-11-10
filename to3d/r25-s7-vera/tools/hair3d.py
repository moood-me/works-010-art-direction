"""The hair, from the drawing's own hair (styles/s7-ghibli/tools/hair.py, HAIRDEF): its shell over the skull
(between the hairline and the crown, the drawing's volume), tucked into the skin at the hairline; every lock and tuft
of the drawing as a 3D lock along the same Bézier curve from the same root, with the same width profile and pointed
end — flat across, wide side along the head; a knot as a ball on the shell; the drawing's strand lines (on the locks' edges and the flow lines on the
shell) as thin dark strips on them."""
import math
import numpy as np
from scipy.spatial import cKDTree
import drawing as D, mesh as M, shapes as S
from geo import bezier, spline

H, HR = D.HEAD, D.HAIR
LINES = []
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))


def shell():
    ts = np.arange(-180, 180, 3.0)
    nY = 34
    hl = np.minimum(HR.line_y(ts), 0.97)
    rows = []
    # below the hairline: two rows that tuck the edge into the skin
    for k, tuck in ((0.03, 0.0), (0.012, 0.6)):
        rows.append([HR.C + (H_pt(t, y - k) - HR.C) * (1 + float(HR.k(y)) * tuck) for t, y in zip(ts, hl)])
    for i in range(nY):
        u = (i / (nY - 1)) ** 1.3
        rows.append([HR.shell_pt(t, y0 + (0.999 - y0) * u) for t, y0 in zip(ts, hl)])
    G = np.array(rows)
    return G


def H_pt(t_deg, y):
    """a point of the head's own surface ring (no hair volume) at azimuth t, height y (head-local)."""
    t = math.radians(t_deg); y = float(np.clip(y, -0.999, 0.999))
    a = float(H.a(y)); zm = float(H.zm(y)); n = H.n
    s, c = math.sin(t), math.cos(t)
    x = a * math.copysign(abs(s) ** (2 / n), s)
    d = (float(H.zf(y)) - zm) if c > 0 else (zm - float(H.zb(y)))
    return np.array([x, y, zm + d * math.copysign(abs(c) ** (2 / n), c)])


def lock_geo(L):
    """one lock of the drawing → (centre curve, widths, side vectors, out vectors) per root (head-local)."""
    roots = [L['root']] if not L.get('mirror') else [L['root'], (-L['root'][0], L['root'][1])]
    out = []
    for k, (t, y) in enumerate(roots):
        r = HR.shell_pt(t, y)
        ctrl = [r] + [r + np.array([(-dx if k else dx), dy, dz]) for dx, dy, dz in L['to']]
        c = bezier(*ctrl, n=40)
        s = np.linspace(0, 1, len(c))
        prof = L.get('prof', 1.2)
        w = L['w'] * (1 - s ** prof) * (0.6 + 0.4 * np.sin(np.clip(s * 3, 0, 1) * np.pi / 2))
        w = np.maximum(w, 0.012)
        tg = np.gradient(c, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True)
        o = c - HR.C
        o -= tg * (o * tg).sum(1, keepdims=True); o /= np.linalg.norm(o, axis=1, keepdims=True)
        side = np.cross(tg, o)
        out.append((c, w, side, o, L))
    return out


def lock_mesh(c, w, side, o, cols=16):
    R = len(c); G = np.zeros((R, cols, 3))
    th = np.maximum(w * 0.26, 0.012)
    for i in range(R):
        for j, a in enumerate(np.linspace(0, 2 * np.pi, cols, endpoint=False)):
            # a lens: flat across, a little thicker in the middle
            G[i, j] = c[i] + side[i] * np.cos(a) * w[i] / 2 + o[i] * np.sin(a) * th[i] / 2 * (0.6 + 0.4 * abs(np.cos(a)))
    V = G.reshape(-1, 3); T = S.grid_tris(R, cols, True)
    # the root closed (inside the shell), the tip closed
    for row, flip in ((0, False), (R - 1, True)):
        ci = len(V); V = np.vstack([V, c[row]])
        add = [[row * cols + j, row * cols + (j + 1) % cols, ci] for j in range(cols)]
        T = np.vstack([T, np.array(add)[:, ::-1] if flip else add])
    n = M.vertex_normals(V, T)
    ax = np.vstack([np.repeat(c, cols, 0), c[0], c[-1]])
    if ((V - ax) * n).sum(1).mean() < 0: T = T[:, ::-1]
    return V, T


def build(ctx):
    hv, ht = ctx['head']
    hn = M.vertex_normals(hv, ht)
    I, NJ = ctx['I'], ctx['NJ']
    parts = []          # (V head-local, T, kind)
    G = shell()
    R, C = G.shape[:2]
    VS = G.reshape(-1, 3); TS = S.grid_tris(R, C, True)
    n = M.vertex_normals(VS, TS)
    if ((VS - HR.C) * n).sum(1).mean() < 0: TS = TS[:, ::-1]
    parts.append((VS, TS, 'shell'))
    strands = []
    for L in HR.locks:
        for c, w, side, o, L_ in lock_geo(L):
            V_, T_ = lock_mesh(c, w, side, o)
            parts.append((V_, T_, 'lock'))
            if L_.get('line'):
                strands.append((c, w, side, o, 1 if L_['line'] in (True, 1, 'r') else -1))
    for t, y, r, out in D.HAIRDEF.get('balls', []):
        # a knot: a ball sitting on the shell
        p = HR.shell_pt(t, y); p = HR.C + (p - HR.C) * (1 + out)
        zz = np.cos(np.linspace(0, np.pi, 14))
        V_, T_ = S.tube(p + np.outer(zz * r, [0, 1.0, 0]), r * np.sqrt(np.maximum(1 - zz ** 2, 1e-4)), cols=20)
        parts.append((V_, T_, 'lock'))
    # one mesh, head-local → model
    Vs, Ts, kind, base = [], [], [], 0
    for V_, T_, k in parts:
        Vs.append(V_); Ts.append(T_ + base); kind += [k] * len(V_); base += len(V_)
    VL = np.vstack(Vs); T = np.vstack(Ts); kind = np.array(kind)
    V = D.head_to_model(VL)
    # out of the head (and its neck): along the head's normal, to at least 4 mm off the skin
    tree = cKDTree(hv)
    for _ in range(3):
        dd, ii = tree.query(V)
        s = ((V - hv[ii]) * hn[ii]).sum(1)
        m = s < 0.004
        V[m] += hn[ii[m]] * (0.004 - s[m])[:, None]
    # out of the clothes (the cardigan's and the blouse's rings, as superellipses), with a little room
    for lo, margin in ctx['lofts']:
        yc = V[:, 1] / D.CM
        inr = (yc > lo.y0) & (yc < lo.y1)
        for i in np.where(inr)[0]:
            a_, zf_, zb_, x0, z0 = lo.at(yc[i])
            a_ += margin; zf_ += margin; zb_ -= margin
            zm = (zf_ + zb_) / 2 + z0; x = V[i, 0] / D.CM - x0; z = V[i, 2] / D.CM - zm
            d = (zf_ - zb_) / 2
            rr = (abs(x / a_) ** lo.n + abs(z / d) ** lo.n) ** (1 / lo.n)
            if rr < 1:
                V[i, 0] = (x / rr + x0) * D.CM; V[i, 2] = (z / rr + zm) * D.CM
    N = len(V)
    hy = VL[:, 1]
    # weights: the head; what hangs below the chin goes over to the neck and the chest
    W = np.zeros((N, NJ))
    wh = 1 - 0.85 * smooth((-1.05 - hy) / 0.9)
    W[:, I['Head']] = wh; W[:, I['Chest']] = (1 - wh) * 0.75; W[:, I['Neck1']] = (1 - wh) * 0.25
    col = np.tile(D.rgb(D.COL['hair']), (N, 1)); shd = np.tile(D.shade(D.COL['hair'], 1.1), (N, 1))
    lin = np.tile(D.rgb(D.INK), (N, 1))
    # the shade follows a big plain form: the shell smoothed; locks take the direction from the head's centre
    A = M.adjacency(N, [list(t_) for t_ in T])
    Vsm = M.smooth(V, A, np.ones(N, bool), iters=30, lam=0.5)
    pn = M.vertex_normals(Vsm, T)
    radial = V - D.head_to_model(HR.C)[0]; radial /= np.linalg.norm(radial, axis=1, keepdims=True)
    lockm = kind == 'lock'
    pn[lockm] = pn[lockm] * 0.5 + radial[lockm] * 0.5
    pn /= np.linalg.norm(pn, axis=1, keepdims=True)
    hair = dict(V=V, T=T, W=ctx['smooth_w'](W, T, N), col=col, shd=shd, lin=lin, pn=pn, pw=np.full(N, 0.75),
                ob=np.full(N, 0.012))
    # strand lines: along a lock's edge over its last 45 % (as the drawing does), and the flow lines on the shell
    lw = 0.0023
    for c, w, side, o, sg in strands:
        k0 = int(len(c) * 0.55)
        P = c[k0:] + side[k0:] * sg * (w[k0:, None] / 2) * 0.8
        th = np.maximum(w[k0:] * 0.26, 0.012) * 0.5
        P = D.head_to_model(P + o[k0:] * th[:, None] * 0.75)
        Nn = o[k0:]
        add_line(P, Nn, lw * S.taper(len(P), 0.3), hair, lift=0.0008)
    for path in D.HAIRDEF.get('flow', []):
        pts = np.array([HR.shell_pt(t, y) for t, y in path])
        c = spline(pts, 30)
        Nn = c - HR.C; Nn /= np.linalg.norm(Nn, axis=1, keepdims=True)
        add_line(D.head_to_model(c), Nn, lw * S.taper(len(c), 0.3), hair, lift=0.0012)
    return hair


def add_line(P, Nn, width, src, lift):
    V_, T_ = S.strip(P, Nn, width, lift=lift)
    i = cKDTree(src['V']).query(V_)[1]
    ink = D.rgb(D.INK)
    LINES.append(dict(V=V_, T=T_, W=src['W'][i], col=np.tile(ink, (len(V_), 1)), shd=np.tile(ink, (len(V_), 1)),
                      lin=np.tile(ink, (len(V_), 1)), ow=np.zeros(len(V_))))
