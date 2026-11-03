"""A small vector 'painter' for the Arcane-like style.

Heads, necks, busts and hair shells are parametric surfaces (lofts of super-elliptic cross-sections with bumps).
For a view (yaw, pitch) each surface is cut into flat regions — silhouette, shadow, deep shadow, highlight, rim —
computed on a fine parameter grid, turned into polygons (shapely), smoothed, mapped onto the surface and projected.
That gives the big graphic light-and-shadow shapes of the style; painterly texture is added by SVG filters.
Features (eyes, brows, lips, nostrils) are drawn in the face's own 2D coordinates and wrapped onto the surface,
so they turn with the head. Everything is written out as plain SVG.
"""
import math
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, box, LineString
from shapely.ops import unary_union
from shapely import affinity

# ---------------------------------------------------------------- helpers: numbers and paths

def interp(table, y):
    ys = [t[0] for t in table]
    vs = [t[1] for t in table]
    return np.interp(y, ys, vs)


def fmt(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')


def smooth_path(pts, closed=True, k=0.5):
    """Catmull-Rom through points; a point given as (x, y, 1) is a corner."""
    n = len(pts)
    if n < 2:
        return ''
    P = [(p[0], p[1]) for p in pts]
    C = [len(p) > 2 and p[2] for p in pts]
    d = 'M%s,%s' % (fmt(P[0][0]), fmt(P[0][1]))
    segs = n if closed else n - 1
    for i in range(segs):
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[i]
        p1 = P[i]
        p2 = P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3)
        if C[i]:
            c1 = p1
        if C[(i + 1) % n]:
            c2 = p2
        d += 'C%s,%s %s,%s %s,%s' % tuple(fmt(v) for v in (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
    return d + ('Z' if closed else '')


def poly_path(geom, smooth=True):
    """shapely (Multi)Polygon -> SVG path data."""
    if geom is None or geom.is_empty:
        return ''
    polys = [geom] if isinstance(geom, Polygon) else [g for g in getattr(geom, 'geoms', []) if isinstance(g, Polygon)]
    out = []
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            c = list(ring.coords)[:-1]
            if len(c) < 3:
                continue
            out.append(smooth_path(c, True) if smooth else 'M' + 'L'.join('%s,%s' % (fmt(x), fmt(y)) for x, y in c) + 'Z')
    return ''.join(out)


def chaikin(coords, it=2):
    c = list(coords)
    for _ in range(it):
        n = len(c)
        nc = []
        for i in range(n):
            a, b = c[i], c[(i + 1) % n]
            nc.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            nc.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        c = nc
    return c


def clean(geom):
    if geom is None or geom.is_empty:
        return geom
    g = geom.buffer(0)
    if isinstance(g, MultiPolygon):
        g = MultiPolygon([p for p in g.geoms if p.area > 2])
    elif isinstance(g, Polygon) and g.area <= 2:
        return Polygon()
    return g

# ---------------------------------------------------------------- view


class View:
    """Rotation (yaw about the vertical axis, then pitch), scale and placement."""

    def __init__(self, yaw=0.0, pitch=0.0, roll=0.0, s=1.0, cx=0.0, cy=0.0, light=(-0.55, -0.5, 0.67), rim=(0.85, -0.2, -0.3), rimcol=None):
        self.rimcol = rimcol
        self.yaw, self.pitch, self.roll = math.radians(yaw), math.radians(pitch), math.radians(roll)
        self.s, self.cx, self.cy = s, cx, cy
        L = np.array(light, float)
        self.L = L / np.linalg.norm(L)
        R = np.array(rim, float)
        self.R = R / np.linalg.norm(R)

    def rot(self, X, Y, Z):
        cy_, sy_ = math.cos(self.yaw), math.sin(self.yaw)
        x1 = X * cy_ + Z * sy_
        z1 = -X * sy_ + Z * cy_
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        y2 = Y * cp - z1 * sp
        z2 = Y * sp + z1 * cp
        cr, sr = math.cos(self.roll), math.sin(self.roll)
        x3 = x1 * cr - y2 * sr
        y3 = x1 * sr + y2 * cr
        return x3, y3, z2

    def proj(self, X, Y, Z):
        x, y, z = self.rot(X, Y, Z)
        return self.cx + self.s * x, self.cy + self.s * y, z

# ---------------------------------------------------------------- surfaces


class Surf:
    """A parametric surface over (u, v) in [u0,u1] x [v0,v1]; pos(u, v) -> X, Y, Z arrays."""
    u0, u1, v0, v1 = -math.pi, math.pi, -1, 1
    nu, nv = 220, 150

    def pos(self, u, v):
        raise NotImplementedError

    def grid(self, nu=None, nv=None):
        nu = nu or self.nu
        nv = nv or self.nv
        u = np.linspace(self.u0, self.u1, nu)
        v = np.linspace(self.v0, self.v1, nv)
        U, V = np.meshgrid(u, v)
        return U, V

    def normals(self, U, V):
        e = 1e-3
        X, Y, Z = self.pos(U, V)
        Xu, Yu, Zu = self.pos(U + e, V)
        Xv, Yv, Zv = self.pos(U, V + e * (self.v1 - self.v0))
        du = np.stack([Xu - X, Yu - Y, Zu - Z], -1)
        dv = np.stack([Xv - X, Yv - Y, Zv - Z], -1)
        n = np.cross(dv, du)
        ln = np.linalg.norm(n, axis=-1, keepdims=True) + 1e-12
        n = n / ln * self.nsign
        out = self.outward(X, Y, Z)
        if out is not None:
            d = n[..., 0] * out[0] + n[..., 1] * out[1] + n[..., 2] * out[2]
            n = np.where((d < 0)[..., None], -n, n)
        return np.stack([X, Y, Z], -1), n

    def outward(self, X, Y, Z):
        return None

    nsign = 1


class Loft(Surf):
    """Cross-sections stacked along y: half width a(y), front depth bf(y), back depth bb(y), exponent p(y),
    centre offsets x0(y), z0(y), and gaussian bumps [(phi, y, sphi, sy, amp)] added to the radius.
    u = angle (0 = front, +pi/2 = the figure's left = +x), v = y."""

    def __init__(self, a, bf, bb, p=2.2, y0=None, y1=None, bumps=(), z0=None, x0=None, extra=None, pf=None):
        self.a, self.bf, self.bb, self.p = a, bf, bb, p
        self.pf = pf
        self.v0 = y0 if y0 is not None else a[0][0]
        self.v1 = y1 if y1 is not None else a[-1][0]
        self.bumps = list(bumps)
        self.z0, self.x0 = z0, x0
        self.extra = extra

    def r(self, u, v):
        a = np.maximum(interp(self.a, v), 1e-3)
        bf = np.maximum(interp(self.bf, v), 1e-3)
        bb = np.maximum(interp(self.bb, v), 1e-3)
        p = interp(self.p, v) if isinstance(self.p, list) else self.p
        s, c = np.sin(u), np.cos(u)
        if self.pf is not None:
            p = np.where(c >= 0, interp(self.pf, v), p)
        b = np.where(c >= 0, bf, bb)
        r = (np.abs(s / a) ** p + np.abs(c / b) ** p) ** (-1.0 / p)
        for (pu, pv, su, sv, amp) in self.bumps:
            du = np.angle(np.exp(1j * (u - pu)))
            r = r + amp * np.exp(-0.5 * ((du / su) ** 2 + ((v - pv) / sv) ** 2))
        if self.extra:
            r = r + self.extra(u, v)
        return r

    def outward(self, X, Y, Z):
        x0 = interp(self.x0, Y) if self.x0 else 0
        z0 = interp(self.z0, Y) if self.z0 else 0
        return (X - x0, 0 * X, Z - z0)

    def pos(self, u, v):
        r = self.r(u, v)
        X = r * np.sin(u)
        Z = r * np.cos(u)
        if self.x0:
            X = X + interp(self.x0, v)
        if self.z0:
            Z = Z + interp(self.z0, v)
        return X, v + 0 * u, Z


def Head(zf, zb, a, p=2.2, bumps=(), extra=None, pf=None):
    """A loft given the absolute front (zf) and back (zb) of each section."""
    ys = sorted(set([t[0] for t in zf] + [t[0] for t in zb]))
    F = [interp(zf, y) for y in ys]
    B = [interp(zb, y) for y in ys]
    z0 = [(y, (f + b) / 2) for y, f, b in zip(ys, F, B)]
    d = [(y, max((f - b) / 2, 0.01)) for y, f, b in zip(ys, F, B)]
    return Loft(a=a, bf=d, bb=d, p=p, z0=z0, bumps=bumps, extra=extra, pf=pf)


class Offset(Surf):
    """A surface pushed out along its normals by t(u, v) (hair shells)."""

    def __init__(self, base, t):
        self.base, self.t = base, t
        self.u0, self.u1, self.v0, self.v1 = base.u0, base.u1, base.v0, base.v1
        self.nu, self.nv = base.nu, base.nv

    def outward(self, X, Y, Z):
        return self.base.outward(X, Y, Z)

    def pos(self, u, v):
        X, Y, Z = self.base.pos(u, v)
        _, n = self.base.normals(u, v)
        t = self.t(u, v)
        return X + n[..., 0] * t, Y + n[..., 1] * t, Z + n[..., 2] * t


class Nose(Surf):
    """A nose on a face: u across (-1..1), v along (0 root .. 1 subnasale).
    The path goes down the bridge to the tip and turns back under it."""
    u0, u1, v0, v1 = -1, 1, 0, 1
    nu, nv = 90, 120

    def __init__(self, face, root, tip, sub, width, height, tipw=None, alar=None, hump=0.0, droop=0.0):
        self.face = face
        self.root, self.tip, self.sub = root, tip, sub  # y of root, tip, subnasale
        self.width, self.height = width, height        # tables over v
        self.tipw = tipw
        self.hump, self.droop = hump, droop
        self.nsign = 1

    def outward(self, X, Y, Z):
        return None

    def orient(self):
        _, n = self.normals(np.array([0.0]), np.array([0.4]))
        if n[0, 2] < 0:
            self.nsign = -self.nsign
        return self

    def pos(self, u, v):
        # y along: root -> tip for v in [0, .82], then back up to sub
        vt = 0.82
        y = np.where(v <= vt, self.root + (self.tip - self.root) * (v / vt), self.tip + (self.sub - self.tip) * ((v - vt) / (1 - vt)))
        w = interp(self.width, v)
        h = interp(self.height, v) + self.hump * np.exp(-((v - 0.4) / 0.15) ** 2)
        x = w * u
        fz = self.face.pos(np.zeros_like(u), y)[2]
        # cross-section: a rounded wedge, flatter on top
        prof = np.clip(1 - np.abs(u) ** 1.8, 0, 1) ** 0.75
        z = fz - 2 + h * prof
        y = y + self.droop * np.exp(-((v - 0.85) / 0.1) ** 2)
        return x, y, z

# ---------------------------------------------------------------- regions


def _cells_union(mask, U, V):
    """Union of grid cells where mask is True, in parameter space."""
    rows = []
    nv, nu = mask.shape
    us = U[0]
    vs = V[:, 0]
    for j in range(nv - 1):
        row = mask[j, :-1] & mask[j + 1, :-1] | mask[j, :-1] & mask[j, 1:]
        row = mask[j, :-1]
        i = 0
        while i < nu - 1:
            if row[i]:
                k = i
                while k < nu - 1 and row[k]:
                    k += 1
                rows.append(box(us[i], vs[j], us[min(k, nu - 1)], vs[j + 1]))
                i = k
            else:
                i += 1
    if not rows:
        return Polygon()
    return unary_union(rows)


def _smooth_param(g, du, dv, it=2):
    if g.is_empty:
        return g
    g = g.simplify(min(du, dv) * 0.6)
    polys = [g] if isinstance(g, Polygon) else list(g.geoms)
    out = []
    for p in polys:
        if not isinstance(p, Polygon) or p.area < du * dv * 3:
            continue
        ext = chaikin(list(p.exterior.coords)[:-1], it)
        holes = [chaikin(list(h.coords)[:-1], it) for h in p.interiors if Polygon(h).area > du * dv * 3]
        out.append(Polygon(ext, holes))
    return unary_union(out) if out else Polygon()


def _densify(g, step):
    if g.is_empty:
        return g
    return g.segmentize(step)


def _map(surf, view, g):
    """Map a parameter-space polygon onto the surface and project it."""
    if g is None or g.is_empty:
        return Polygon()
    polys = [g] if isinstance(g, Polygon) else [p for p in g.geoms if isinstance(p, Polygon)]
    out = []
    for p in polys:
        def tr(coords):
            c = np.array(coords)
            X, Y, Z = surf.pos(c[:, 0], c[:, 1])
            x, y, _ = view.proj(X, Y, Z)
            return list(zip(x, y))
        try:
            q = Polygon(tr(p.exterior.coords), [tr(h.coords) for h in p.interiors])
            out.append(q.buffer(0).simplify(0.4))
        except Exception:
            pass
    return clean(unary_union(out)) if out else Polygon()


def _contour_geom(F, U, V):
    """Region F > 0 on the parameter grid as a shapely geometry in (u, v), via marching squares."""
    from skimage import measure
    if not np.any(F > 0):
        return Polygon()
    G = np.pad(F, 1, constant_values=-1.0)
    cs = measure.find_contours(G, 0.0)
    us, vs = U[0], V[:, 0]
    nv, nu = F.shape
    geom = Polygon()
    polys = []
    for c in cs:
        if len(c) < 4:
            continue
        r = np.clip(c[:, 0] - 1, 0, nv - 1)
        q = np.clip(c[:, 1] - 1, 0, nu - 1)
        uu = np.interp(q, np.arange(nu), us)
        vv = np.interp(r, np.arange(nv), vs)
        pg = Polygon(list(zip(uu, vv))).buffer(0)
        if pg.area > 0:
            polys.append(pg)
    polys.sort(key=lambda p: -p.area)
    for pg in polys:
        geom = geom.symmetric_difference(pg)
    return geom


def regions(surf, view, mask_fn=None, shadow=0.1, deep=-0.35, hi=0.93, rim=0.8, extra=None):
    """Silhouette, shadow, deep shadow, highlight and rim regions of a surface in a view (screen space).
    mask_fn(U, V) gives a field that is > 0 where the surface is kept."""
    U, V = surf.grid()
    P, N = surf.normals(U, V)
    nx, ny, nz = view.rot(N[..., 0], N[..., 1], N[..., 2])
    base = nz.copy()
    if mask_fn is not None:
        m = mask_fn(U, V)
        if m.dtype == bool:
            m = np.where(m, 1.0, -1.0)
        base = np.minimum(base, m)
    dl = nx * view.L[0] + ny * view.L[1] + nz * view.L[2]
    dr = nx * view.R[0] + ny * view.R[1] + nz * view.R[2]
    du = (surf.u1 - surf.u0) / (U.shape[1] - 1)
    dv = (surf.v1 - surf.v0) / (U.shape[0] - 1)
    step = min(du, dv)

    def reg(F):
        g = _contour_geom(F, U, V)
        if g.is_empty:
            return Polygon()
        g = g.simplify(step * 0.3)
        return _map(surf, view, _densify(g, step * 2))

    out = {
        'sil': reg(base),
        'shadow': reg(np.minimum(base, shadow - dl)),
        'deep': reg(np.minimum(base, deep - dl)),
        'hi': reg(np.minimum(base, dl - hi)),
        'rim': reg(np.minimum(np.minimum(base, dr - rim), 0.4 - nz)),
    }
    if extra:
        for k, f in extra.items():
            out[k] = reg(np.minimum(base, f(U, V, dl, nz)))
    return out


def on_surface(surf, view, pts, lift=0.0):
    """Points (u, v) on a surface -> screen points, plus facing (n.view) per point."""
    c = np.array(pts, float)
    P, N = surf.normals(c[:, 0], c[:, 1])
    X = P[:, 0] + N[:, 0] * lift
    Y = P[:, 1] + N[:, 1] * lift
    Z = P[:, 2] + N[:, 2] * lift
    x, y, z = view.proj(X, Y, Z)
    nx, ny, nz = view.rot(N[:, 0], N[:, 1], N[:, 2])
    return list(zip(x, y)), nz


def point3(view, X, Y, Z):
    x, y, z = view.proj(np.array([X], float), np.array([Y], float), np.array([Z], float))
    return float(x[0]), float(y[0]), float(z[0])

# ---------------------------------------------------------------- svg output


class Doc:
    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h
        self.defs = []
        self.body = []
        self.ids = 0
        self.bg = bg

    def uid(self, p='i'):
        self.ids += 1
        return '%s%d' % (p, self.ids)

    def add(self, s):
        self.body.append(s)

    def svg(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (self.w, self.h, self.w, self.h)
                + '<defs>' + ''.join(self.defs) + '</defs>' + ''.join(self.body) + '</svg>')


FILTERS = '''
<filter id="paint" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="3" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="3.2" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="brush" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="2.6" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.03 0.07" numOctaves="3" seed="11" result="s"/>
  <feColorMatrix in="s" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.9 0 0 0 0.25" result="sa"/>
  <feComposite in="d" in2="sa" operator="in" result="t"/>
  <feGaussianBlur in="d" stdDeviation="0.6" result="db"/>
  <feComponentTransfer in="db" result="dbh"><feFuncA type="linear" slope="0.8"/></feComponentTransfer>
  <feMerge><feMergeNode in="dbh"/><feMergeNode in="t"/></feMerge>
</filter>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="soft2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="edge" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1.1"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="5" result="n"/>
  <feColorMatrix in="n" type="saturate" values="0" result="g"/>
  <feComponentTransfer in="g"><feFuncA type="linear" slope="0" intercept="1"/></feComponentTransfer>
</filter>
<filter id="canvas" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.006 0.03" numOctaves="4" seed="21" result="n"/>
  <feColorMatrix in="n" type="saturate" values="0"/>
</filter>
'''


def path(d, fill='none', stroke=None, sw=None, op=None, extra=''):
    if not d:
        return ''
    s = '<path d="%s" fill="%s"' % (d, fill)
    if stroke:
        s += ' stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"' % (stroke, fmt(sw or 1))
    if op is not None:
        s += ' opacity="%s"' % fmt(op) if op >= 0.1 else ' opacity="%.2f"' % op
    return s + extra + '/>'


def taper(pts, w0, w1=0.0, wmid=None, k=0.5):
    """A tapered ribbon (stroke as a filled shape) along a polyline/curve of points."""
    P = np.array(pts, float)
    # resample along a smooth curve
    n = max(12, len(P) * 6)
    t = np.linspace(0, 1, len(P))
    tt = np.linspace(0, 1, n)
    # catmull-rom via numpy interp on cumulative chord would be nicer; use quadratic smoothing
    x = np.interp(tt, t, P[:, 0])
    y = np.interp(tt, t, P[:, 1])
    for _ in range(3):
        x[1:-1] = (x[:-2] + 2 * x[1:-1] + x[2:]) / 4
        y[1:-1] = (y[:-2] + 2 * y[1:-1] + y[2:]) / 4
    dx = np.gradient(x)
    dy = np.gradient(y)
    l = np.hypot(dx, dy) + 1e-9
    nx, ny = -dy / l, dx / l
    if wmid is None:
        w = w0 + (w1 - w0) * tt
    else:
        w = np.where(tt < 0.5, w0 + (wmid - w0) * (tt / 0.5), wmid + (w1 - wmid) * ((tt - 0.5) / 0.5))
        w = np.maximum(w, 0)
    L = list(zip(x + nx * w / 2, y + ny * w / 2))
    R = list(zip(x - nx * w / 2, y - ny * w / 2))[::-1]
    return smooth_path(L + R, True)


def lin(d, stroke, sw, op=None):
    return path(d, 'none', stroke, sw, op)


class Tube(Surf):
    """A tube swept along a smooth 3D curve: points [(x, y, z)], radii [r] (or (rx, rz) for flattened sections)."""
    u0, u1, v0, v1 = -math.pi, math.pi, 0.0, 1.0
    nu, nv = 60, 90

    def __init__(self, pts, radii, flat=1.0):
        P = np.array(pts, float)
        # dense catmull-rom resample of the centre line
        t = np.linspace(0, 1, len(P))
        n = 200
        tt = np.linspace(0, 1, n)
        C = []
        for k in range(3):
            C.append(np.interp(tt, t, P[:, k]))
        C = np.stack(C, -1)
        for _ in range(6):
            C[1:-1] = (C[:-2] + 2 * C[1:-1] + C[2:]) / 4
        self.C = C
        self.tt = tt
        R = np.array(radii, float)
        self.R = np.interp(tt, np.linspace(0, 1, len(R)), R)
        self.flat = flat
        T = np.gradient(C, axis=0)
        T /= np.linalg.norm(T, axis=-1, keepdims=True) + 1e-9
        up = np.array([0.0, 0.0, 1.0])
        N = np.cross(T, up)
        bad = np.linalg.norm(N, axis=-1) < 1e-3
        N[bad] = np.cross(T[bad], np.array([1.0, 0, 0]))
        N /= np.linalg.norm(N, axis=-1, keepdims=True) + 1e-9
        B = np.cross(T, N)
        self.N, self.B = N, B

    def _at(self, v):
        i = np.clip(v, 0, 1) * (len(self.tt) - 1)
        i0 = np.floor(i).astype(int)
        i1 = np.minimum(i0 + 1, len(self.tt) - 1)
        f = (i - i0)[..., None]
        C = self.C[i0] * (1 - f) + self.C[i1] * f
        N = self.N[i0] * (1 - f) + self.N[i1] * f
        B = self.B[i0] * (1 - f) + self.B[i1] * f
        R = self.R[i0] * (1 - f[..., 0]) + self.R[i1] * f[..., 0]
        return C, N, B, R

    def pos(self, u, v):
        C, N, B, R = self._at(v)
        cu, su = np.cos(u)[..., None], np.sin(u)[..., None]
        P = C + R[..., None] * (cu * N * self.flat + su * B)
        return P[..., 0], P[..., 1], P[..., 2]

    def outward(self, X, Y, Z):
        return None

    def normals(self, U, V):
        P, n = Surf.normals(self, U, V)
        C, _, _, _ = self._at(V)
        d = (P[..., 0] - C[..., 0]) * n[..., 0] + (P[..., 1] - C[..., 1]) * n[..., 1] + (P[..., 2] - C[..., 2]) * n[..., 2]
        n = np.where((d < 0)[..., None], -n, n)
        return P, n
