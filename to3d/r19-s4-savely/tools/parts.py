"""Parts shared by the Arcane characters' builds (build.py): tubes, the hair as a shell over the fitted skull cut by the
drawing's own hair mask, separate locks from the drawing's lock lists, thin shells of hair lying on the face (brows,
a moustache), round or square glasses, lofted shoes, skin weights down the neck.
Everything here is in the drawing's units (y down, z toward the viewer) unless said otherwise."""
import numpy as np
from scipy.spatial import cKDTree
from arc import interp

sm = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))


def tube(path, radius, n=10, closed=False):
    path = np.asarray(path, float)
    V, T = [], []
    m = len(path)
    for i, p in enumerate(path):
        d = path[(i + 1) % m if closed else min(i + 1, m - 1)] - path[(i - 1) % m if closed else max(i - 1, 0)]; d /= np.linalg.norm(d)
        u = np.cross(d, [0, 0, 1.0]) if abs(d[2]) < 0.9 else np.cross(d, [1.0, 0, 0]); u /= np.linalg.norm(u)
        w = np.cross(d, u)
        r = radius[i] if np.ndim(radius) else radius
        for k in range(n):
            a_ = 2 * np.pi * k / n
            V.append(p + (u * np.cos(a_) + w * np.sin(a_)) * r)
    for i in range(m if closed else m - 1):
        for k in range(n):
            a0, a1 = i * n + k, i * n + (k + 1) % n; b0, b1 = ((i + 1) % m) * n + k, ((i + 1) % m) * n + (k + 1) % n
            T += [[a0, a1, b0], [a1, b1, b0]]
    return np.array(V), np.array(T)


def spline(pts, n):
    """Catmull-Rom through the points, n samples; returns the samples and their parameter 0…1."""
    pts = np.asarray(pts, float)
    if len(pts) == 2:
        t = np.linspace(0, 1, n)
        return pts[0] + (pts[1] - pts[0]) * t[:, None], t
    P = np.r_[[2 * pts[0] - pts[1]], pts, [2 * pts[-1] - pts[-2]]]
    out = []
    ts = np.linspace(0, len(pts) - 1, n)
    for t in ts:
        i = min(int(t), len(pts) - 2); f = t - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3))
    return np.array(out), ts / (len(pts) - 1)


class Skull:
    """The fitted head's outer skull as a radius over directions from a centre: where the hair lies."""

    def __init__(self, hv, sel, centre):
        self.c = np.asarray(centre, float)
        d = hv[sel] - self.c
        self.r0 = np.linalg.norm(d, axis=1)
        self.tree = cKDTree(d / self.r0[:, None])

    def r(self, d):
        dist, j = self.tree.query(d, 8)
        w = 1 / (dist + 1e-3)
        return (self.r0[j] * w).sum(1) / w.sum(1)

    def lift(self, p, least):
        """points pushed out so that they lie at least `least` over the skull"""
        q = p - self.c; r = np.linalg.norm(q, axis=1); d = q / r[:, None]
        return self.c + d * np.maximum(r, self.r(d) + least)[:, None]


def hair_cap(skull, head, mask, thick, nphi=220, nth=110, th_max=2.75, edge=7.0):
    """The hair mass: the skull pushed out by thick(U, V), kept where the drawing's hair mask(U, V) > 0 (U the angle
    round the head's axis, V the height — the drawing's own hair coordinates). The shell covers a little more than the
    mask and carries the mask as an attribute (the shader cuts it: a clean edge); toward the edge it thins onto the
    skin. Returns vertices, triangles, the mask attribute (0 at the edge … 1 inside) and (U, V)."""
    phis = np.linspace(-np.pi, np.pi, nphi, endpoint=False)
    ths = np.linspace(0.0, th_max, nth)
    PH, TH = np.meshgrid(phis, ths, indexing='ij')
    d = np.stack([np.sin(TH) * np.sin(PH), -np.cos(TH), np.sin(TH) * np.cos(PH)], -1).reshape(-1, 3)
    r = skull.r(d)
    base = skull.c + d * r[:, None]
    yy = np.clip(base[:, 1], head.v0, head.v1)
    z0 = np.array([interp(head.z0, y) for y in yy])
    U = np.arctan2(base[:, 0], base[:, 2] - z0); Vv = base[:, 1]
    m = mask(U, Vv)
    hm = np.clip(m / edge, -1, 1)
    t = thick(U, Vv) * sm(m / edge) + 0.35
    V = skull.c + d * (r + t)[:, None]
    T = []
    idx = np.arange(nphi * nth).reshape(nphi, nth)
    a0 = idx[:, :-1]; b0 = idx[:, 1:]; a1 = np.roll(idx, -1, 0)[:, :-1]; b1 = np.roll(idx, -1, 0)[:, 1:]
    T = np.r_[np.stack([a0, b0, a1], -1).reshape(-1, 3), np.stack([a1, b0, b1], -1).reshape(-1, 3)]
    keep = (hm[T] > -0.6).any(1)
    T = T[keep]
    used = np.unique(T); re = -np.ones(len(V), int); re[used] = np.arange(len(used))
    return V[used], re[T], hm[used], U[used], Vv[used]


def lock_mesh(head, skull, spec, k=0, nseg=10, nround=8, flat=0.34, least=1.2, wscale=1.0):
    """One lock of the drawing's list ({pts: ('s', u, v, out) on the head or raw (x, y, z); w: widths}) as a flattened,
    tapered tube: wide across the head, thin off it. Returns vertices, triangles, the across-coordinate (for the
    painted strands) and the along-coordinate 0…1."""
    pts, nrm = [], []
    for p in spec['pts']:
        if p[0] == 's':
            _, u, v, out = p
            P_, N_ = head.normals(np.array([u]), np.array([float(np.clip(v, head.v0 + 0.5, head.v1 - 0.5))]))
            pts.append(P_[0] + N_[0] * out); nrm.append(N_[0])
        else:
            x, y, z = p[:3]; l = np.hypot(x, z) + 1e-6
            pts.append(np.array([x, y, z], float)); nrm.append(np.array([x / l, 0, z / l]))
    C, t = spline(pts, nseg)
    Nn, _ = spline(nrm, nseg)
    C = skull.lift(C, least)
    w = np.interp(t, np.linspace(0, 1, len(spec['w'])), spec['w']) * wscale
    V, across, along = [], [], []
    for i in range(nseg):
        tg = C[min(i + 1, nseg - 1)] - C[max(i - 1, 0)]; tg /= np.linalg.norm(tg) + 1e-9
        n = Nn[i] - tg * (Nn[i] @ tg); n /= np.linalg.norm(n) + 1e-9
        b = np.cross(tg, n)
        hw = max(w[i] / 2, 0.25); ht = max(hw * flat, 0.5 if i < nseg - 1 else 0.2)
        for j in range(nround):
            a = 2 * np.pi * j / nround
            V.append(C[i] + b * np.cos(a) * hw + n * (np.sin(a) * ht + ht * 0.5))
            across.append(np.cos(a)); along.append(t[i])
    T = []
    for i in range(nseg - 1):
        for j in range(nround):
            a0, a1 = i * nround + j, i * nround + (j + 1) % nround; b0, b1 = a0 + nround, a1 + nround
            T += [[a0, b0, a1], [a1, b0, b1]]
    c0 = len(V); V.append(C[0]); across.append(0); along.append(0)
    c1 = len(V); V.append(C[-1]); across.append(0); along.append(1)
    for j in range(nround):
        T.append([c0, j, (j + 1) % nround]); T.append([c1, (nseg - 1) * nround + (j + 1) % nround, (nseg - 1) * nround + j])
    return np.array(V), np.array(T), np.array(across) * 0.5 + k * 7.31, np.array(along)


def face_shell(hv, HT, ok, poly, thick, edge=2.0, flow=(1.0, 0.0), fine=0.11):
    """A thin shell of hair lying on the face (a brow, a moustache): the head's own triangles inside a polygon of the
    face's flat coordinates (x, y), pushed out along the normals; the polygon's edge is carried as the mask attribute.
    flow: the hairs' direction in (x, y) for the figure's left side (mirrored on the right)."""
    from shapely.geometry import Polygon, Point
    pg = Polygon(poly).buffer(0)
    big = pg.buffer(edge * 1.5)
    x0, y0, x1, y1 = big.bounds
    cand = np.where(ok & (hv[:, 0] > x0) & (hv[:, 0] < x1) & (hv[:, 1] > y0) & (hv[:, 1] < y1))[0]
    sd = {}
    for i in cand:
        p = Point(hv[i, 0], hv[i, 1])
        if big.contains(p):
            sd[i] = (1 if pg.contains(p) else -1) * pg.exterior.distance(p)
    ids = np.array(sorted(sd)); re = -np.ones(len(hv), int); re[ids] = np.arange(len(ids))
    T = HT[(re[HT] >= 0).all(1)]
    n = np.cross(hv[HT[:, 1]] - hv[HT[:, 0]], hv[HT[:, 2]] - hv[HT[:, 0]])
    N = np.zeros_like(hv)
    for k in range(3): np.add.at(N, HT[:, k], n)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    if np.mean(N[ids, 2]) < 0: N = -N
    s = np.array([sd[i] for i in ids])
    th = thick(hv[ids, 0], hv[ids, 1]) if callable(thick) else thick
    V = hv[ids] + N[ids] * (th * sm(s / edge) + 0.25)[:, None]
    f = np.array(flow, float); f /= np.linalg.norm(f)
    hs = (np.abs(hv[ids, 0]) * -f[1] + hv[ids, 1] * f[0]) * fine
    return V, re[T], np.clip(s / edge, -1, 1), hs, ids


def glasses(P, hv, ear, eye_front, wire=0.6):
    """Frames from the drawing's numbers (P.glasses: rx, ry, dy, dz, square), curved round the face, a bridge, arms to
    the ears; and flat lenses (for the glint). Returns frame (V, T) and lens (V, T)."""
    G = P.glasses
    gl_v, gl_t, lens = [], [], []
    curve = 0.0028
    gz = eye_front + G['dz'] * 0.8 + curve * P.eye_x ** 2
    gy = P.eye_y + G['dy'] + 1
    rx, ry = G['rx'] + 1.5, G['ry'] + 0.5
    for sd in (1, -1):
        cxg = sd * (P.eye_x + 1)
        pts = []
        for a_ in np.linspace(0, 2 * np.pi, 64, endpoint=False):
            c_, s_ = np.cos(a_), np.sin(a_)
            kk = 2 + G['square'] * 6
            r = (abs(c_) ** kk + abs(s_) ** kk) ** (-1 / kk)
            x = cxg + rx * r * c_
            pts.append((x, gy + ry * r * s_, gz - curve * x * x))
        lens.append(np.array(pts))
        v, tt = tube(pts, wire, 8, closed=True); gl_t.append(tt + sum(len(q) for q in gl_v)); gl_v.append(v)
        x0 = sd * (P.eye_x + 1 + rx); z0 = gz - curve * x0 * x0
        ex = sd * (abs(hv[ear & (np.sign(hv[:, 0]) == sd), 0]).max() - 3)
        arm = [(x0, gy - 2, z0), (x0 + sd * 3, gy - 3, z0 - 10), (ex * 0.98, P.ear_y - 12, P.ear_z + 12), (ex * 0.96, P.ear_y - 13, P.ear_z - 6), (ex * 0.9, P.ear_y - 4, P.ear_z - 16)]
        v, tt = tube(arm, wire, 8); gl_t.append(tt + sum(len(q) for q in gl_v)); gl_v.append(v)
    xb = P.eye_x + 1 - rx
    xs = np.linspace(-1, 1, 9)
    bp = [(xb * x, gy - 2 - 3 * (1 - x * x), gz - curve * xb ** 2 * x * x + 1.5 * (1 - x * x)) for x in xs]
    v, tt = tube(bp, wire * 0.9, 8); gl_t.append(tt + sum(len(q) for q in gl_v)); gl_v.append(v)
    GV = np.vstack(gl_v); GT = np.vstack(gl_t)[:, [0, 2, 1]]
    lv, lt = [], []
    for L_ in lens:
        c = L_.mean(0); base = sum(len(q) for q in lv)
        lv.append(np.r_[c[None], L_]); n = len(L_)
        lt.append(np.array([[base, base + 1 + i, base + 1 + (i + 1) % n] for i in range(n)]))
    return GV, GT, np.vstack(lv), np.vstack(lt)[:, [0, 2, 1]]


def shoes(J1, I, NJ, length=0.205, width=0.043, height=0.09, back=0.052, heel=0.0, pw=2.4):
    """A lofted shoe on each foot (world units, metres): a rounded toe, a flat sole on the floor."""
    SHV, SHT, SHW = [], [], []
    for s in ('Left', 'Right'):
        jf = J1[I[s + 'Foot']]; jt = J1[I[s + 'ToeBase']]
        fwd = jt - jf; fwd[1] = 0; fwd /= np.linalg.norm(fwd)
        side = np.cross([0, 1.0, 0], fwd)
        base = np.array([jf[0], 0.0, jf[2]])
        rows, cols = 16, 48
        vs = []
        for i in range(rows):
            t_ = i / (rows - 1)
            y = 0.002 + t_ * (height - 0.002)
            front = max(length * (1 - t_) ** 1.6 + 0.05 * t_, 0.05)
            bk = back - 0.01 * t_
            w = width - 0.008 * t_
            if t_ > 0.55: front = 0.05 + 0.015 * (1 - (t_ - 0.55) / 0.45)
            a_ = np.linspace(0, 2 * np.pi, cols, endpoint=False)
            ca, sa = np.cos(a_), np.sin(a_)
            L_ = np.where(ca > 0, front, bk)
            rr = (np.abs(ca) ** pw + np.abs(sa) ** pw) ** (-1 / pw)
            for k in range(cols):
                vs.append(base + fwd * (ca[k] * L_[k] * rr[k]) + side * (sa[k] * w * rr[k]) + [0, y, 0])
        vs = np.array(vs)
        ts = []
        for i in range(rows - 1):
            for k in range(cols):
                a0, a1 = i * cols + k, i * cols + (k + 1) % cols; b0, b1 = a0 + cols, a1 + cols
                ts += [[a0, a1, b0], [a1, b1, b0]]
        c0 = len(vs); vs = np.r_[vs, [base + [0, 0.002, 0] + fwd * 0.07]]
        ts += [[c0, (k + 1) % cols, k] for k in range(cols)]
        c1 = len(vs); vs = np.r_[vs, [base + [0, height, 0] + fwd * 0.01]]
        ts += [[c1, (rows - 1) * cols + k, (rows - 1) * cols + (k + 1) % cols] for k in range(cols)]
        ts = np.array(ts)
        off_ = sum(len(q) for q in SHV)
        SHV.append(vs); SHT.append(ts + off_)
        w_ = np.zeros((len(vs), NJ)); w_[:, I[s + 'Foot']] = 1.0
        toe = np.clip(((vs - jt) @ fwd) / 0.04, 0, 1) * 0.6
        w_[:, I[s + 'Foot']] -= toe; w_[:, I[s + 'ToeBase']] += toe
        SHW.append(w_)
    return np.vstack(SHV), np.vstack(SHT), np.vstack(SHW)


def orient(V, T, c):
    """turn every triangle so its normal points away from c (a closed shell round c)"""
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    out = (n * (V[T].mean(1) - c)).sum(1) < 0
    T = T.copy(); T[out] = T[out][:, [0, 2, 1]]
    return T


def top4(Wt):
    idx = np.argsort(-Wt, 1)[:, :4]; w = np.take_along_axis(Wt, idx, 1); w /= w.sum(1, keepdims=True)
    return idx, w
