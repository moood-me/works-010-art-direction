"""The head: Blender's Human Base Meshes stylised head (CC0), made blank where the drawing paints (eye sockets and the
mouth bag closed and smoothed — the eyes, brows and mouth of this style are signs painted from the SVG), then fitted
to Аня's drawing by its front and profile silhouettes."""
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


def face_normals(v, P):
    n = np.array([np.cross(v[p[1]] - v[p[0]], v[p[2]] - v[p[0]]) for p in P])
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


def flood(P, seed_faces, ok):
    """Faces reachable from the seeds over shared edges, through faces where ok is true."""
    ef = {}
    for i, p in enumerate(P):
        for a, b in zip(p, p[1:] + p[:1]): ef.setdefault((min(a, b), max(a, b)), []).append(i)
    seen = set(seed_faces); st = list(seed_faces)
    while st:
        i = st.pop(); p = P[i]
        for a, b in zip(p, p[1:] + p[:1]):
            for j in ef[(min(a, b), max(a, b))]:
                if j not in seen and ok[j]: seen.add(j); st.append(j)
    return seen


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


def blank(v, P, vis, eyes, r):
    """Eye sockets and mouth closed: the faces there that no ray from outside reaches (their linings, hbm_export.py)
    taken out, the holes filled."""
    fc = np.array([v[p].mean(0) for p in P])
    near = np.zeros(len(P), bool)
    for c in eyes: near |= np.linalg.norm(fc - c, axis=1) < r * 1.5
    near |= (abs(fc[:, 0]) < 0.06) & (fc[:, 1] > 0.55) & (fc[:, 1] < 0.70) & (fc[:, 2] > -0.0) & (fc[:, 2] < 0.14)
    drop = set(np.where((vis == 0) & near)[0])
    P = [p for i, p in enumerate(P) if i not in drop]
    v, P, _ = compact(v, P)
    loops = M.boundary_loops(P)
    filled = []
    for L in loops:
        c = v[L].mean(0)
        if c[1] < 0.54: continue          # the neck's opening stays open
        # loops go round the hole; orientation: we want the fill to face outward (+z mostly)
        v, P, new = fill(v, P, L)
        filled += new + list(L)
    return v, P, loops, filled


# ---------------------------------------------------------------- fitting to the drawing
import drawing as D  # noqa: E402

# the base's own heights (its units) → the drawing's (units, y down): neck's end, chin, eye line, crown
Y_BASE = [0.513, 0.575, 0.7287, 0.888]
Y_DRAW = [262.0, 112.0, 0.0, -126.0]


def targets(yd):
    """The drawing's half-width (front) and front/back (profile) at drawing heights yd: the face, then the neck."""
    f = D.profile(D.FRONT['face'], yd); s = D.profile(D.SIDE['face'], yd)
    w = np.where(np.isnan(f[:, 1]), np.nan, f[:, 1])
    zf, zb = s[:, 1].copy(), s[:, 0].copy()
    # the neck, as drawn (front ±26 → ±32 at the collar; profile front 26 → 30, back −30 → −36), then under the collar
    nk = np.interp(yd, [80, 112, 178, 230, 262], [26, 26, 30, 40, 52])
    nf = np.interp(yd, [80, 104, 178, 230, 262], [24, 26, 30, 36, 44])
    nb = np.interp(yd, [70, 112, 178, 230, 262], [-30, -29, -36, -46, -56])
    # the nape: from the skull's back (drawn) down to the neck's
    back = np.where(yd < 0, zb, np.interp(yd, [-1, 0, 40, 80, 112], [np.nan, -92, -80, -54, -30]))
    below = yd >= 106
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
    bins = np.arange(-130, 266, 4.0)
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
    # the lower face fuller and flatter in front (the drawing's face is one round plane; the base has a muzzle):
    # where it lies behind an arc through the lips' front, it comes forward toward it
    V = out[0]; y = np.interp(v[:, 1], Y_BASE, Y_DRAW)
    zf = np.interp(y, bins, zf_t)
    wy = smooth01((y - 10) / 30) * (1 - smooth01((y - 104) / 14))
    arc = zf - V[:, 0] ** 2 / (2 * 0.085) - 0.004
    push = np.clip(arc - V[:, 2], 0, None) * wy * (V[:, 2] > 0.0) * np.exp(-(V[:, 0] / 0.075) ** 4)
    V[:, 2] += 0.85 * push
    # the ears smaller and closer to the head (under the hair; the drawing shows only a bit of one in profile)
    e = ears_mask
    c = out[0][e].mean(0) * [0, 1, 1]
    for s_ in (1, -1):
        m = e & (np.sign(out[0][:, 0]) == s_)
        root = np.array([s_ * 0.075, c[1], c[2]])
        out[0][m] = root + (out[0][m] - root) * [0.4, 0.7, 0.7]
    return out


def smooth01(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def _fillnan(a):
    i = np.arange(len(a)); ok = ~np.isnan(a)
    return np.interp(i, i[ok], a[ok])


def ears(v):
    return (abs(v[:, 0]) > 0.085) & (v[:, 2] > -0.05) & (v[:, 2] < 0.075) & (v[:, 1] > 0.64) & (v[:, 1] < 0.80)


def flatten(V, regions, front_min=0.0):
    """Where the drawing paints (eyes, the mouth's line), the base's sockets and lips are laid onto one smooth
    surface: inside each ellipse (drawing units: cx, cy, rx, ry) every vertex in front of front_min goes to the surface
    fitted (a quadratic) to the face around it; between the ellipse and 1.6× it, a blend."""
    V = V.copy()
    xd, yd = V[:, 0] / D.K, D.FLOOR - V[:, 1] / D.K
    for cx, cy, rx, ry in regions:
        e = np.sqrt(((xd - cx) / rx) ** 2 + ((yd - cy) / ry) ** 2)
        front = V[:, 2] > front_min
        ring = (e > 1.15) & (e < 1.9) & front
        # only the outermost layer of the ring (the face, not anything behind it)
        A = np.c_[np.ones(ring.sum()), xd[ring], yd[ring], xd[ring] ** 2, xd[ring] * yd[ring], yd[ring] ** 2]
        c, *_ = np.linalg.lstsq(A, V[ring, 2], rcond=None)
        z = np.c_[np.ones(len(V)), xd, yd, xd ** 2, xd * yd, yd ** 2] @ c
        t = np.clip((1.6 - e) / 0.6, 0, 1)
        t = t * t * (3 - 2 * t)
        m = front & (e < 1.6)
        V[m, 2] = V[m, 2] * (1 - t[m]) + z[m] * t[m]
    return V
