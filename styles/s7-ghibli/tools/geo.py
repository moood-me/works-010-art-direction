"""3D → flat shapes. A character is built from simple 3D forms (lofted rings, tubes, surface templates),
projected orthographically and turned into flat 2D polygons (shapely). The drawing then works on flat shapes only:
fill, one shadow tone, an outline — the cel look of the style.

Model space: centimetres, y up, the character faces +z at yaw 0. A View turns it by `yaw` (degrees, + turns the face to
the viewer's right), tilts the camera down by `pitch`, scales by `s` px/cm and places the origin at (ox, oy) px."""
import math
import numpy as np
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely import affinity


class View:
    def __init__(self, yaw=0.0, pitch=4.0, s=10.0, ox=0.0, oy=0.0):
        self.yaw, self.pitch, self.s, self.ox, self.oy = yaw, pitch, s, ox, oy
        a, p = math.radians(yaw), math.radians(pitch)
        self.ca, self.sa, self.cp, self.sp = math.cos(a), math.sin(a), math.cos(p), math.sin(p)

    def rot(self, P):
        """model points (N,3) → camera space (N,3): x right, y up, z toward the viewer."""
        P = np.asarray(P, float).reshape(-1, 3)
        x = P[:, 0] * self.ca + P[:, 2] * self.sa
        z = -P[:, 0] * self.sa + P[:, 2] * self.ca
        y = P[:, 1] * self.cp - z * self.sp
        z2 = z * self.cp + P[:, 1] * self.sp
        return np.stack([x, y, z2], 1)

    def dir(self, N):
        """turn direction vectors (no translation) — for normals."""
        return self.rot(N)

    def xy(self, P):
        """model points → screen px (N,2)."""
        C = self.rot(P)
        return np.stack([self.ox + self.s * C[:, 0], self.oy - self.s * C[:, 1]], 1)

    def depth(self, P):
        return self.rot(P)[:, 2]


# ---------------------------------------------------------------- shapes

def poly(pts):
    p = Polygon(pts)
    if not p.is_valid:
        p = p.buffer(0)
    return p


def hull_union(rings2d):
    """union of convex hulls of consecutive projected rings — the silhouette of a loft."""
    parts = []
    for a, b in zip(rings2d[:-1], rings2d[1:]):
        parts.append(MultiPolygonFromPts(np.vstack([a, b])).convex_hull)
    return unary_union(parts)


def MultiPolygonFromPts(pts):
    from shapely.geometry import MultiPoint
    return MultiPoint([tuple(p) for p in pts])


def tube2d(pts, radii):
    """a tapered tube through 2D points: union of hulls of consecutive circles."""
    parts = []
    circ = [Point(p).buffer(max(r, 0.05), 24) for p, r in zip(pts, radii)]
    for a, b in zip(circ[:-1], circ[1:]):
        parts.append(unary_union([a, b]).convex_hull)
    if len(circ) == 1:
        parts = circ
    return unary_union(parts)


def tube(view, P3, radii):
    """a tube along a 3D polyline with radii in cm (orthographic, so circles stay circles)."""
    P3 = np.asarray(P3, float)
    return tube2d(view.xy(P3), [r * view.s for r in radii])


def resample(P, n):
    """resample a polyline (N,k) to n points evenly along its length."""
    P = np.asarray(P, float)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    t = np.linspace(0, d[-1], n)
    return np.stack([np.interp(t, d, P[:, i]) for i in range(P.shape[1])], 1)


def bezier(*ctrl, n=24):
    """cubic (or any order) Bézier through control points, (n,k)."""
    C = np.asarray(ctrl, float)
    t = np.linspace(0, 1, n)[:, None]
    k = len(C) - 1
    out = np.zeros((n, C.shape[1]))
    for i, c in enumerate(C):
        out += math.comb(k, i) * (1 - t) ** (k - i) * t ** i * c
    return out


def spline(pts, n=40, closed=False):
    """Catmull-Rom through the points."""
    P = np.asarray(pts, float)
    if closed:
        P = np.vstack([P[-1], P, P[0], P[1]])
    else:
        P = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
    out = []
    segs = len(P) - 3
    per = max(2, n // max(segs, 1))
    for i in range(segs):
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        for t in np.linspace(0, 1, per, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed:
        out.append(P[-2])
    return np.array(out)


def ribbon(center, widths):
    """a leaf-like ribbon around a 2D centerline with a width at each point (lock of hair, a fold)."""
    C = np.asarray(center, float)
    T = np.gradient(C, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-9)
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    w = np.asarray(widths, float)[:, None] / 2
    pts = np.vstack([C + N * w, (C - N * w)[::-1]])
    return poly(pts)


def shift(g, dx, dy):
    return affinity.translate(g, dx, dy)


def polys(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if hasattr(g, 'geoms'):
        out = []
        for x in g.geoms:
            out += polys(x)
        return out
    return []


def lines(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, LineString):
        return [g]
    if hasattr(g, 'geoms'):
        out = []
        for x in g.geoms:
            out += lines(x)
        return out
    return []


def smooth(g, r=0.6):
    """round off tiny corners left by unions."""
    if g.is_empty:
        return g
    return g.buffer(r, 8).buffer(-r, 8)


# ---------------------------------------------------------------- svg paths

def _fmt(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


def path_of(g, min_area=0.5):
    """polygon(s) → svg path d (with holes, evenodd)."""
    out = []
    for p in polys(g):
        if p.area < min_area:
            continue
        p = p.simplify(0.3, preserve_topology=True)
        for ring in [p.exterior] + list(p.interiors):
            c = np.asarray(ring.coords)
            out.append('M' + ' '.join(f'{_fmt(x)},{_fmt(y)}' for x, y in c[:-1]) + 'Z')
    return ''.join(out)


def line_of(pts):
    P = np.asarray(pts, float)
    if len(P) < 2:
        return ''
    if len(P) > 3:
        P = np.asarray(LineString(P).simplify(0.25).coords)
    return 'M' + ' '.join(f'{_fmt(x)},{_fmt(y)}' for x, y in P)
