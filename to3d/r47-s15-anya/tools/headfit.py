"""The head (from Р1's head.py, for С15): Blender's Human Base Meshes stylised head (CC0) fitted to the noir Аня by
her front and profile outlines (drawing.py); its face is cut out and closed by a clean patch laid on the planes the
drawing designs (`surf`) — the eyes, brows, nose's plane and lips of this style are black and coloured shapes drawn
over (web/face.js)."""
import numpy as np
import mesh as M

C0 = 2.082951545715332   # the bundle's head stands at x=2.083


def conv(v):
    return np.c_[v[:, 0] - C0, v[:, 2], -v[:, 1]]


def load(path):
    d = np.load(path)
    v = conv(d['head_v']); P = M.polys_of(d['head_fs'], d['head_f']); vis = d['head_vis']
    eyes = [conv(d['L_v']).mean(0), conv(d['R_v']).mean(0)]
    r = (conv(d['L_v']).max(0) - conv(d['L_v']).min(0)).max() / 2
    return v, P, eyes, r, vis


def fill(v, P, loop, rings=4):
    """Close a hole: rings from its edge to its middle (quads), a fan in the centre."""
    v = list(v); c = np.mean([v[i] for i in loop], 0); n = len(loop)
    prev = list(loop); new = []
    for r in range(1, rings + 1):
        t = r / (rings + 1); cur = []
        for i in loop:
            v.append(v[i] * (1 - t) + c * t); cur.append(len(v) - 1)
        new += cur
        for k in range(n):
            P.append([prev[k], cur[k], cur[(k + 1) % n], prev[(k + 1) % n]][::-1])
        prev = cur
    v.append(c); ci = len(v) - 1; new.append(ci)
    for k in range(n): P.append([prev[k], ci, prev[(k + 1) % n]][::-1])
    return np.array(v), P, new


def compact(v, P):
    used = sorted(set(i for p in P for i in p)); m = -np.ones(len(v), int); m[used] = np.arange(len(used))
    return v[used], [[int(m[i]) for i in p] for p in P], m


# ---------------------------------------------------------------- fitting to the drawing
import drawing as D  # noqa: E402

# the base's own heights (its units) → the drawing's (units, y down): neck's end, chin, eye line, crown
Y_BASE = [0.513, 0.575, 0.7287, 0.888]
Y_DRAW = [262.0, D.CHIN, 0.0, D.SKULL]


def targets(yd):
    """The drawing's half-width (front) and front/back (profile) at drawing heights yd: the face, then the neck."""
    f = D.profile(D.FRONT['face'], yd); s = D.profile(D.SIDE['face'], yd)
    w = np.where(np.isnan(f[:, 1]), np.nan, f[:, 1])
    zf, zb = s[:, 1].copy(), s[:, 0].copy()
    # the neck: its width as drawn in front (head.py neck_f: ±25 head units), a little less deep than the profile
    # draws it (the two views disagree: 76 head units deep, 50 wide), then under the collar
    nk = np.interp(yd, [80, 118, 178, 230, 262], [34, 34, 36, 44, 56])
    nf = np.interp(yd, [80, 110, 178, 230, 262], [40, 42, 42, 46, 52])
    nb = np.interp(yd, [70, 118, 178, 230, 262], [-44, -44, -46, -52, -60])
    # the nape: from the skull's back (drawn) down to the neck's
    back = np.where(yd < 0, zb, np.interp(yd, [-1, 0, 16, 49, 118], [np.nan, -105, -94, -56, -44]))
    below = yd >= D.CHIN - 6
    w = np.where(below | np.isnan(w), np.maximum(nk, np.nan_to_num(w, nan=0)), w)
    zf = np.where(below | np.isnan(zf), nf, zf)
    zb = np.where(yd >= 0, np.where(below, nb, back), zb)
    zb = np.where(np.isnan(zb), nb, zb)
    return w, zf, zb


def fit(v, ears_mask, extra=()):
    """The base head into the drawing: heights piecewise by its landmarks, then each height's width (front) and
    front/back (profile) to the drawing's; the field of moves smoothed so the forms stay the base's.
    Returns 3D metres (y up, facing +z)."""
    yd = np.interp(v[:, 1], Y_BASE, Y_DRAW)      # increasing base y → decreasing drawing y (interp needs xp up)
    # slices of the base at drawing heights
    bins = np.arange(-158, 266, 4.0)
    w_c, zf_c, zb_c = [], [], []
    for b in bins:
        m = (abs(yd - b) < 9) & ~ears_mask
        if m.sum() < 3: w_c.append(np.nan); zf_c.append(np.nan); zb_c.append(np.nan); continue
        w_c.append(abs(v[m, 0]).max()); zf_c.append(v[m, 2].max()); zb_c.append(v[m, 2].min())
    w_c, zf_c, zb_c = map(lambda a: _fillnan(np.array(a)), (w_c, zf_c, zb_c))
    w_t, zf_t, zb_t = targets(bins)
    w_t, zf_t, zb_t = map(_fillnan, (w_t, zf_t, zb_t))
    sm = lambda a: np.convolve(np.pad(a, 2, mode='edge'), np.ones(5) / 5, 'valid')
    kx = sm(w_t * D.K / np.maximum(w_c, 1e-3))
    zf_t, zb_t = sm(zf_t * D.K), sm(zb_t * D.K)
    zf_c, zb_c = sm(zf_c), sm(zb_c)
    out = []
    for V in (v,) + tuple(extra):
        y = np.interp(V[:, 1], Y_BASE, Y_DRAW)
        x = V[:, 0] * np.interp(y, bins, kx)
        a, b = np.interp(y, bins, zb_c), np.interp(y, bins, zf_c)
        A, B = np.interp(y, bins, zb_t), np.interp(y, bins, zf_t)
        z = A + (V[:, 2] - a) / (b - a) * (B - A)
        out.append(np.c_[x, (D.FLOOR - y) * D.K, z])
    # the ears a little smaller (the hair goes behind them; the front drawing shows them as small wedges)
    e = ears_mask
    c = out[0][e].mean(0) * [0, 1, 1]
    for s_ in (1, -1):
        m = e & (np.sign(out[0][:, 0]) == s_)
        root = np.array([s_ * 0.088, c[1], c[2]])
        out[0][m] = root + (out[0][m] - root) * [0.6, 0.8, 0.8]
    return out


def smooth01(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def _fillnan(a):
    i = np.arange(len(a)); ok = ~np.isnan(a)
    return np.interp(i, i[ok], a[ok])


def ears(v):
    return (abs(v[:, 0]) > 0.085) & (v[:, 2] > -0.05) & (v[:, 2] < 0.075) & (v[:, 1] > 0.64) & (v[:, 1] < 0.80)


# ---------------------------------------------------------------- the noir face: planes, as the drawing designs them
# The drawing gives the face as a few planes: the front plane ends at the drawn edge of the side shadow (head.py
# `side_f`: from the temple by the cheekbone to the chin), the side plane goes back from it to the outline; down the
# middle the profile's line (nose, lips, chin). `surf` is that surface: the base head's face is laid onto it, so the
# form itself breaks where the black shape begins, and sockets, lids and lips of the base (drawn in this style) go.
EDGE = np.array([(-100, 44), (-80, 47.6), (-14, 43.6), (34, 37.6), (56, 23.6), (84, 21), (98, 12.5)])     # head units (y, x)
_so = D._so


def _zy(k):
    z, y = D.side(*_so[k][:2]); return y, z


def profile_lines(yu):
    """the profile's front line at heights yu (units): the whole (zmid), without the nose and the lips (zface), and
    the lips' relief."""
    ys = np.arange(D.SKULL, D.CHIN + 1, 1.0)
    zmid = D.profile(D.SIDE['face'], ys)[:, 1]
    ok = ~np.isnan(zmid); zmid = np.interp(ys, ys[ok], zmid[ok])
    (yb, zb_), (yn, zn), (yf, zf_) = _zy('brow'), _zy('nosebase'), _zy('chinfold')
    base = zmid.copy()
    m = (ys > yb) & (ys < yn); base[m] = np.interp(ys[m], [yb, yn], [zb_, zn])
    m = (ys >= yn) & (ys < yf); base[m] = np.interp(ys[m], [yn, yf], [zn, zf_])
    g = lambda arr: np.interp(yu, ys, arr)
    lips = np.where((yu > yn) & (yu < yf), g(zmid) - g(base), 0.0)
    nose = np.where((yu > yb) & (yu <= yn), g(zmid) - g(base), 0.0)
    return g(base), nose, lips


def surf(xu, yu):
    """the face's surface: z (units) at front coordinates (units)."""
    yh = yu / D.HS + D.EYE
    zface, nose, lips = profile_lines(yu)
    xs = np.interp(yh, EDGE[:, 0], EDGE[:, 1]) * D.HS
    f = D.profile(D.FRONT['face'], np.unique(np.round(yu)))
    a = np.interp(yu, np.unique(np.round(yu)), np.nan_to_num(f[:, 1], nan=40.0))
    a = np.maximum(a, xs + 6)
    ax = np.abs(xu)
    t = np.clip((ax - xs) / (a - xs), 0, 1)
    z_out = np.interp(yh, [-100, 0, 60, 98], [10, 0, 14, 40]) * D.HS            # the side plane's far end, at the outline
    z_edge = zface - (13 + 15 * np.exp(-((yh - 14) / 24) ** 2)) * (ax.clip(max=xs) / xs) ** 2     # rounder across the eyes: they turn with the cheeks                              # the front plane: nearly flat
    z = np.where(ax <= xs, z_edge, z_edge - (z_edge - z_out) * t ** 0.85)
    nw = np.interp(yh, [-6, 10, 30, 40, 46], [5, 6, 9, 10.5, 9]) * D.HS            # the nose: a narrow wedge
    z = z + nose * np.clip(1 - ax / nw, 0, 1) ** 1.1
    z = z + lips * (1 - smooth01((ax - 10 * D.HS) / (12 * D.HS)))
    return z


def build(path):
    """→ the fitted head (metres, y up, facing +z), polygons, ear mask, face weight (1 where the face is the
    drawing's surface).
    The base gives the skull, the jaw's underside, the neck, the ears. Its face — sockets, lids, nose, lips, the mouth's
    bag: all drawn in this style — is cut out along one loop inside the face's outline, and the opening is closed by a
    clean patch (rings from the loop to the middle) laid on the drawing's surface (`surf`)."""
    v, P, eyes, r, vis = load(path)
    earm = ears(v)
    V = fit(v, earm)[0]
    ys_ = np.arange(D.SKULL, D.CHIN + 2, 2.0)
    f = np.nan_to_num(D.profile(D.FRONT['face'], ys_)[:, 1], nan=30.0)
    def where(V):
        xu, yu = V[:, 0] / D.K, D.FLOOR - V[:, 1] / D.K
        return xu, yu, yu / D.HS + D.EYE, np.abs(xu) / np.maximum(np.interp(yu, ys_, f), 1)
    xu, yu, yh, rr = where(V)
    vn = M.vertex_normals(V, M.triangulate(P))
    under = (vn[:, 1] < -0.4) & (yh > 60) & (vn[:, 2] < 0.5)          # the jaw's underside stays the base's
    inner = (V[:, 2] > 0.0) & (rr < 0.8) & (yh > -66) & (yh < 99.0) & ~earm & ~under
    while True:       # the cut's edge is one simple loop: a point where two cut parts touch is cut out too
        Q = [p for p in P if not inner[p].any()]
        cnt = M.edges_of(Q); out = {}
        for p in Q:
            for a_, b_ in zip(p, p[1:] + p[:1]):
                if cnt[(min(a_, b_), max(a_, b_))] == 1: out[a_] = out.get(a_, 0) + 1
        bad = [k for k, n_ in out.items() if n_ > 1 and V[k, 2] > 0.0]
        if not bad: break
        inner[bad] = True
    P = Q
    # what hung on the face from inside (the mouth's bag, the sockets' linings) is now loose: only the head stays
    par = list(range(len(V)))
    def root(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for p in P:
        for q in p[1:]: par[root(q)] = root(p[0])
    comp = {}
    for i, p in enumerate(P): comp.setdefault(root(p[0]), []).append(i)
    big = max(comp.values(), key=len); P = [P[i] for i in big]
    V, P, m = compact(V, P); earm = earm[m >= 0]
    n0 = len(V); p0 = len(P)
    loops = [L for L in M.boundary_loops(P) if V[L].mean(0)[2] > 0.03 and V[L].mean(0)[1] > (D.FLOOR - D.CHIN) * D.K]
    L = max(loops, key=len)
    V, P, new = fill(V, P, L, rings=20)
    nrm = np.cross(V[P[p0][1]] - V[P[p0][0]], V[P[p0][2]] - V[P[p0][0]])
    if nrm[2] < 0: P = P[:p0] + [p[::-1] for p in P[p0:]]
    n1 = len(V)
    hc = np.array([0, (D.FLOOR - 0) * D.K, 0.0])
    for L2 in M.boundary_loops(P):         # what else the cut left open (under the chin): closed plainly
        if V[L2].mean(0)[1] < (D.FLOOR - 200) * D.K: continue          # the neck's opening stays
        p1 = len(P)
        V, P, _ = fill(V, P, L2, rings=2)
        q = P[p1]; nn = np.cross(V[q[1]] - V[q[0]], V[q[2]] - V[q[0]])
        if nn @ (V[L2].mean(0) - hc) < 0: P = P[:p1] + [p[::-1] for p in P[p1:]]
    earm = np.r_[earm, np.zeros(len(V) - n0, bool)]
    xu, yu, yh, rr = where(V)
    isnew = np.zeros(len(V), bool); isnew[new] = True
    extra = np.zeros(len(V), bool); extra[n1:] = True
    # the patch on the surface; the base round the loop comes to it over a band (so no ridge where they meet)
    wgt = np.where(isnew, 1.0, (1 - smooth01((rr - 0.8) / 0.16)) * smooth01((101.5 - yh) / 3) * smooth01((yh + 82) / 16) * (V[:, 2] > 0.0) * ~earm)
    A = M.adjacency(len(V), P)
    def lay(V):
        s_ = surf(V[:, 0] / D.K, D.FLOOR - V[:, 1] / D.K) * D.K
        V[:, 2] = V[:, 2] * (1 - wgt) + s_ * wgt
        return V
    V = lay(V)
    for _ in range(30):      # the patch's points spread evenly over the surface
        V = M.smooth(V, A, isnew, iters=1, lam=0.5)
        V = lay(V)
    seam = ((wgt > 0.01) & ~isnew & ~earm) | extra
    V = M.smooth(V, A, seam, iters=4, lam=0.5)
    return V, P, earm, wgt
