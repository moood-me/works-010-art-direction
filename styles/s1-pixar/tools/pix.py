"""pix — a small toolkit to draw Pixar/Disney-like characters as SVG.

A head (and body) is a simple 3D model: cross-sections stacked along y, each a superellipse whose front gets
bumps (brow, nose, lips, chin). Features (eyes, brows, mouth, nose marks) are written in front-view coordinates and
wrapped onto that surface, so the same face turns for a three-quarter or a side view. Hair is ribbons (locks) on a
shell around the cranium. Volume is painted the way a concept artist does: a shadow-coloured base, a lit copy of the
shape shifted toward the light and blurred, soft accents (sockets, blush, under-nose, rim light).

Coordinates: x right, y down, z toward the viewer. A head is 100 units tall (crown -50, chin +50).
"""
import math

# ------------------------------------------------------------------ svg helpers

def f(v):
    t = f"{v:.1f}"
    return t[:-2] if t.endswith(".0") else t


def smooth_path(pts, closed=True, t=0.5):
    """Catmull-Rom through points -> cubic Bezier path string (points closer than ~1.5px are merged)."""
    if len(pts) > 4:
        q = [pts[0]]
        for p in pts[1:]:
            if abs(p[0] - q[-1][0]) + abs(p[1] - q[-1][1]) > 1.5:
                q.append(p)
        if len(q) >= 3:
            pts = q
    n = len(pts)
    if n < 2:
        return ""
    out = [f"M{f(pts[0][0])},{f(pts[0][1])}"]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        out.append(f"C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}")
    if closed:
        out.append("Z")
    return "".join(out)


def poly_path(pts, closed=True):
    s = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
    return s + ("Z" if closed else "")


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(lerp(a[i], b[i], t)):02x}" for i in range(3))


def interp(keys, y):
    """piecewise smooth (cosine) interpolation over sorted (y, value) keys"""
    if y <= keys[0][0]:
        return keys[0][1]
    for (y0, v0), (y1, v1) in zip(keys, keys[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            # Catmull-like smoothness: use smoothstep blend of linear
            t = t * t * (3 - 2 * t)
            return v0 + (v1 - v0) * t
    return keys[-1][1]


def spline(keys, y):
    """Catmull-Rom interpolation of (y, value) keys (smoother than interp)."""
    if y <= keys[0][0]:
        return keys[0][1]
    if y >= keys[-1][0]:
        return keys[-1][1]
    for i in range(len(keys) - 1):
        y1, v1 = keys[i]
        y2, v2 = keys[i + 1]
        if y1 <= y <= y2:
            y0, v0 = keys[i - 1] if i > 0 else (y1 - (y2 - y1), v1 - (v2 - v1))
            y3, v3 = keys[i + 2] if i + 2 < len(keys) else (y2 + (y2 - y1), v2 + (v2 - v1))
            t = (y - y1) / (y2 - y1)
            m1 = (v2 - v0) / (y2 - y0) * (y2 - y1)
            m2 = (v3 - v1) / (y3 - y1) * (y2 - y1)
            t2, t3 = t * t, t * t * t
            return (2 * t3 - 3 * t2 + 1) * v1 + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * v2 + (t3 - t2) * m2
    return keys[-1][1]


class Canvas:
    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h
        self.defs = []
        self.body = []
        self.n = 0
        self.bg = bg

    def uid(self, p="i"):
        self.n += 1
        return f"{p}{self.n}"

    def add(self, s):
        self.body.append(s)

    def blur(self, sd):
        k = f"b{round(sd * 10)}"
        if not any(f'id="{k}"' in d for d in self.defs):
            self.defs.append(
                f'<filter id="{k}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{sd:.2f}"/></filter>')
        return k

    def clip(self, d):
        k = self.uid("c")
        self.defs.append(f'<clipPath id="{k}"><path d="{d}"/></clipPath>')
        return k

    def lingrad(self, stops, x1, y1, x2, y2):
        k = self.uid("g")
        st = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
        self.defs.append(
            f'<linearGradient id="{k}" gradientUnits="userSpaceOnUse" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}">{st}</linearGradient>')
        return k

    def radgrad(self, stops, cx, cy, r, fx=None, fy=None):
        k = self.uid("g")
        st = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
        fxy = f' fx="{f(fx)}" fy="{f(fy)}"' if fx is not None else ""
        self.defs.append(
            f'<radialGradient id="{k}" gradientUnits="userSpaceOnUse" cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"{fxy}>{st}</radialGradient>')
        return k

    def svg(self):
        bg = f'<rect width="{self.w}" height="{self.h}" fill="{self.bg}"/>' if self.bg else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">'
                f'<defs>{"".join(self.defs)}</defs>{bg}{"".join(self.body)}</svg>')


# ------------------------------------------------------------------ painting a volume

LIGHT = (-0.62, -0.78)   # direction the light comes FROM, in screen space (upper left)


def paint_volume(cv, d, base, shadow, size, light=None, lift=0.07, soft=0.06, rim=None, rim_side=1, extra=None,
                 tf=""):
    """A shape painted as a soft volume: shadow-coloured base, the shape again in base colour shifted toward the
    light and blurred inside the clip, an optional cool rim on the shadow side. The path is stored once."""
    lx, ly = light or LIGHT
    pid = cv.uid("p")
    cv.defs.append(f'<path id="{pid}" d="{d}"/>')
    k = cv.uid("c")
    cv.defs.append(f'<clipPath id="{k}"><use href="#{pid}"/></clipPath>')
    g = [f'<g{tf}>', f'<use href="#{pid}" fill="{shadow}"/>', f'<g clip-path="url(#{k})">']
    dx, dy = lx * size * lift, ly * size * lift
    g.append(f'<use href="#{pid}" fill="{base}" filter="url(#{cv.blur(size * soft)})" '
             f'transform="translate({f(dx)},{f(dy)})"/>')
    if rim:
        g.append(f'<use href="#{pid}" fill="none" stroke="{rim}" stroke-width="{f(size * 0.035)}" stroke-opacity="0.55" '
                 f'filter="url(#{cv.blur(size * 0.012)})" transform="translate({f(-lx * size * 0.012)},{f(-ly * size * 0.012)})"/>')
    if extra:
        g.append(extra)
    g.append('</g></g>')
    cv.add("".join(g))
    return k


# ------------------------------------------------------------------ 3D head

class Head:
    """A head as stacked superellipse sections; front-view feature coordinates wrap onto it."""

    def __init__(self, w, zf, zb, n=2.3, bumps=(), cx=0.0, cy=0.0, s=1.0, yaw=0.0, pitch=0.0, roll=0.0):
        self.w, self.zf, self.zb = w, zf, zb       # keys [(y, value)]
        self.n = n
        self.bumps = bumps                          # (x, y, sx, sy, h) gaussian bumps along +z of the front
        self.cx, self.cy, self.s = cx, cy, s
        self.yaw, self.pitch, self.roll = yaw, pitch, roll

    # shape -------------------------------------------------------
    def width(self, y):
        return max(0.0, spline(self.w, y))

    def bump(self, x, y):
        b = 0.0
        for bx, by, sx, sy, h in self.bumps:
            b += h * math.exp(-((x - bx) / sx) ** 2 - ((y - by) / sy) ** 2)
        return b

    def section(self, y, phi):
        w = self.width(y)
        sp, cp = math.sin(phi), math.cos(phi)
        e = 2.0 / self.n
        x = w * math.copysign(abs(sp) ** e, sp)
        d = spline(self.zf, y) if cp >= 0 else -spline(self.zb, y)
        z = d * math.copysign(abs(cp) ** e, cp)
        if cp > 0:
            z += self.bump(x, y) * cp ** 0.5
        return x, z

    def surf(self, x, y, lift=0.0):
        """front-view point (x, y) -> 3D point on the face surface"""
        w = max(self.width(y), 1e-3)
        u = max(-1.0, min(1.0, x / w))
        # invert x = w * sin^e(phi)
        e = 2.0 / self.n
        sphi = math.copysign(abs(u) ** (1 / e), u)
        phi = math.asin(max(-1, min(1, sphi)))
        X, Z = self.section(y, phi)
        return (X, y, Z + lift)

    # projection --------------------------------------------------
    def rot(self, p):
        x, y, z = p
        a = self.pitch                       # nod: positive looks down
        y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
        b = self.yaw
        x, z = x * math.cos(b) + z * math.sin(b), -x * math.sin(b) + z * math.cos(b)
        c = self.roll
        x, y = x * math.cos(c) - y * math.sin(c), x * math.sin(c) + y * math.cos(c)
        return x, y, z

    def proj(self, p):
        x, y, z = self.rot(p)
        return (self.cx + x * self.s, self.cy + y * self.s), z

    def P(self, x, y, lift=0.0):
        return self.proj(self.surf(x, y, lift))[0]

    def facing(self, x, y):
        """how much the surface at front point (x,y) faces the viewer (cos)"""
        p0 = self.rot(self.surf(x, y))
        p1 = self.rot(self.surf(x + 0.5, y))
        p2 = self.rot(self.surf(x, y + 0.5))
        ax, ay, az = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        bx, by, bz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
        nx, ny, nz = ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
        l = math.sqrt(nx * nx + ny * ny + nz * nz) or 1
        return -nz / l if False else abs(nz / l) * (1 if (ax * by - ay * bx) > 0 else -1)

    def silhouette(self, y0=-50, y1=50, ny=90, nphi=96):
        right, left = [], []
        for i in range(ny + 1):
            y = y0 + (y1 - y0) * i / ny
            best_r, best_l = None, None
            for j in range(nphi):
                phi = -math.pi + 2 * math.pi * j / nphi
                X, Z = self.section(y, phi)
                (sx, sy), _ = self.proj((X, y, Z))
                # silhouette across the screen direction perpendicular to the (rolled) axis
                if best_r is None or sx > best_r[0]:
                    best_r = (sx, sy)
                if best_l is None or sx < best_l[0]:
                    best_l = (sx, sy)
            right.append(best_r)
            left.append(best_l)
        return right + left[::-1]

    def outline(self, **kw):
        pts = self.silhouette(**kw)
        # thin out
        pts = [p for i, p in enumerate(pts) if i % 2 == 0]
        return smooth_path(pts)

    def curve(self, pts, lift=0.0, closed=False, smooth=True):
        q = [self.P(x, y, lift) for x, y in pts]
        return smooth_path(q, closed=closed) if smooth else poly_path(q, closed)

    def visible(self, x, y):
        p = self.rot(self.surf(x, y))
        q = self.rot(self.surf(x + 0.3 * (1 if x >= 0 else -1), y))
        return self.fore(x, y) > 0.08

    def fore(self, x, y):
        """horizontal foreshortening of the surface at (x,y): screen dx per unit front dx"""
        a = self.rot(self.surf(x - 0.5, y))
        b = self.rot(self.surf(x + 0.5, y))
        return (b[0] - a[0])


# ------------------------------------------------------------------ sphere shell for hair

class Shell:
    """hair shell: an ellipsoid around the cranium, addressed by (lat, lon) in degrees; lon 0 = front, +lon = the
    character's left (screen right in front view); lat 90 = top, 0 = equator through the forehead."""

    def __init__(self, head, c=(0, -8, -4), r=(44, 44, 48)):
        self.h = head
        self.c, self.r = c, r

    def pt(self, lat, lon, k=1.0, dy=0.0):
        la, lo = math.radians(lat), math.radians(lon)
        x = self.c[0] + self.r[0] * k * math.cos(la) * math.sin(lo)
        y = self.c[1] - self.r[1] * k * math.sin(la) + dy
        z = self.c[2] + self.r[2] * k * math.cos(la) * math.cos(lo)
        return (x, y, z)

    def normal(self, p):
        x, y, z = p
        return ((x - self.c[0]) / self.r[0], (y - self.c[1]) / self.r[1], (z - self.c[2]) / self.r[2])


def norm3(v):
    l = math.sqrt(sum(a * a for a in v)) or 1
    return tuple(a / l for a in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def lock_ribbon(head, centre, widths, normals=None, shell=None):
    """a ribbon along 3D centreline points; returns projected outline points, mean depth, and centreline 2D"""
    left, right = [], []
    n = len(centre)
    zs = []
    for i, p in enumerate(centre):
        a = centre[max(0, i - 1)]
        b = centre[min(n - 1, i + 1)]
        t = norm3((b[0] - a[0], b[1] - a[1], b[2] - a[2]))
        if normals:
            nn = normals[i]
        else:
            nn = norm3(shell.normal(p))
        sd = norm3(cross(t, nn))
        w = widths[i]
        l3 = (p[0] + sd[0] * w, p[1] + sd[1] * w, p[2] + sd[2] * w)
        r3 = (p[0] - sd[0] * w, p[1] - sd[1] * w, p[2] - sd[2] * w)
        left.append(head.proj(l3)[0])
        right.append(head.proj(r3)[0])
        zs.append(head.rot(p)[2])
    pts = left + right[::-1]
    c2 = [head.proj(p)[0] for p in centre]
    return pts, sum(zs) / len(zs), c2
