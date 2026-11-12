"""The facet engine: convex pieces in 3D → shaded flat polygons in SVG.

Every visible form is a *piece*: the convex hull of a few hand-placed points (so the points ARE the drawing — where
they go decides where the planes go), with one base colour and a material. Small flat things that lie on a piece —
eyes, brows, lips, a stripe — are *decals*: polygons pressed onto the piece's faceted surface.

Rendering: pieces are moved by the camera (yaw, pitch, a weak perspective), each face is filled with one flat colour
from its normal (a warm key light from the upper left, cool shadow, a faint fill), and pieces are drawn back to front
by an exact test on their overlaps (a convex piece never hides itself, so only the order of pieces matters).
"""
import math
import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
from shapely.ops import unary_union

# ---------------------------------------------------------------------------------------------------------- maths

def Rx(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(d):
    a = math.radians(d); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def euler(x=0, y=0, z=0):
    """Turn about y (yaw), then x (nod), then z (tilt) — in the parent's frame."""
    return Ry(y) @ Rx(x) @ Rz(z)


def unit(v):
    v = np.asarray(v, float); n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def frame_along(d, up=(0, 0, 1)):
    """A rotation whose y axis is d (a bone direction) and whose z axis is as close to `up` as can be."""
    y = unit(d); z = np.asarray(up, float) - np.dot(up, y) * y
    if np.linalg.norm(z) < 1e-6:
        z = np.array([1.0, 0, 0]) - y[0] * y
    z = unit(z); x = np.cross(y, z)
    return np.column_stack([x, y, z])


def hexcol(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0


def tohex(c):
    c = np.clip(np.asarray(c) * 255.0 + 0.5, 0, 255).astype(int)
    return '#%02x%02x%02x' % tuple(c)


def mix(a, b, t):
    return np.asarray(a) * (1 - t) + np.asarray(b) * t


# --------------------------------------------------------------------------------------------------------- pieces

class Piece:
    """A convex piece: points (n×3), faces (lists of point indices, counter-clockwise seen from outside)."""

    def __init__(self, pts, color, mat='cloth', name='', faces=None, decals=None, bias=0.0):
        self.pts = np.asarray(pts, float)
        self.color = hexcol(color) if isinstance(color, str) else np.asarray(color, float)
        self.mat = mat
        self.name = name
        self.faces = faces if faces is not None else hull_faces(self.pts)
        self.decals = decals or []   # [(pts n×3, colour, opacity)]
        self.bias = bias             # nudges the order when two pieces really intersect

    def moved(self, R=None, t=(0, 0, 0)):
        R = np.eye(3) if R is None else R
        f = lambda P: np.asarray(P) @ R.T + np.asarray(t, float)
        p = Piece(f(self.pts), self.color, self.mat, self.name, self.faces,
                  [(f(d), c, o) for d, c, o in self.decals], self.bias)
        return p


def hull_faces(P, tol=0.9995):
    """Faces of the convex hull, coplanar triangles merged into one polygon each."""
    try:
        h = ConvexHull(P)
    except Exception:      # flat input: joggle it
        h = ConvexHull(P, qhull_options='QJ')
    groups = []   # [normal, offset, set(idx)]
    for simp, eq in zip(h.simplices, h.equations):
        n, d = eq[:3], eq[3]
        for g in groups:
            if np.dot(g[0], n) > tol and abs(g[1] - d) < 1e-3 * (1 + abs(d)):
                g[2].update(simp.tolist()); break
        else:
            groups.append([n, d, set(simp.tolist())])
    faces = []
    for n, d, idx in groups:
        idx = list(idx); Q = P[idx]; c = Q.mean(0)
        u = unit(Q[0] - c); v = np.cross(n, u)
        ang = [math.atan2(np.dot(q - c, v), np.dot(q - c, u)) for q in Q]
        faces.append([i for _, i in sorted(zip(ang, idx))])
    return faces


def hull(points, color, mat='cloth', name='', bias=0.0):
    return Piece(points, color, mat, name, bias=bias)


def mirror_x(points):
    """Points given for x ≥ 0 plus their mirror images (points on x = 0 kept once)."""
    out = []
    for p in points:
        out.append(p)
        if abs(p[0]) > 1e-9:
            out.append((-p[0], p[1], p[2]))
    return out


def ring(c, R, rx, rz, n=6, phase=0.0, front=0.0, back=0.0):
    """n points round centre c in the xz plane of rotation R; rx half-width, rz half-depth;
    front/back push the front (+z) or back point further out (a chest, a belly, a bottom)."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + math.radians(phase)
        x, z = rx * math.sin(a), rz * math.cos(a)
        if z > 0: z += front * math.cos(a) ** 2
        else: z -= back * math.cos(a) ** 2
        pts.append(np.asarray(c, float) + R @ np.array([x, 0, z]))
    return pts


def segment(a, b, ra, rb, color, mat='cloth', n=6, up=(0, 0, 1), ext=0.0, flat=1.0, name='', phase=0.0):
    """A limb: a prism between joints a and b, radius ra at a and rb at b, `flat` squashes it front to back."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = b - a; L = np.linalg.norm(d); R = frame_along(d, up); y = R[:, 1]
    ea, eb = ext if isinstance(ext, tuple) else (ext, ext)
    a2 = a - y * ea * ra; b2 = b + y * eb * rb
    caps = [a2 - y * ra * 0.45 * (ea > 0), b2 + y * rb * 0.45 * (eb > 0)]   # pointed ends: no flat cap shows at a joint
    return hull(ring(a2, R, ra, ra * flat, n, phase) + ring(b2, R, rb, rb * flat, n, phase) + caps, color, mat, name)


def chain(joints, radii, color, mat='cloth', n=6, flat=1.0, up=(0, 0, 1), cap=(0.5, 0.5), name='', phase=30.0):
    """A limb through several joints (hip, knee, ankle): a prism per bone and, at each bent joint, the hull of the two
    rings that meet there — it fills the wedge the bend opens, like the faces round a knee in a low-poly model.
    cap: how far the first and last ends are pointed (0 = flat)."""
    J = [np.asarray(j, float) for j in joints]
    frames = [frame_along(J[i + 1] - J[i], up) for i in range(len(J) - 1)]
    out = []
    for i, R in enumerate(frames):
        a, b = J[i], J[i + 1]; y = R[:, 1]
        pts = ring(a, R, radii[i], radii[i] * flat, n, phase) + ring(b, R, radii[i + 1], radii[i + 1] * flat, n, phase)
        if i == 0 and cap[0] > 0:
            pts.append(a - y * radii[0] * cap[0])
        if i == len(frames) - 1 and cap[1] > 0:
            pts.append(b + y * radii[-1] * cap[1])
        out.append(hull(pts, color, mat, name))
    for i in range(1, len(J) - 1):
        R0, R1 = frames[i - 1], frames[i]
        if np.dot(R0[:, 1], R1[:, 1]) > math.cos(math.radians(4)):
            continue
        pts = ring(J[i], R0, radii[i], radii[i] * flat, n, phase) + ring(J[i], R1, radii[i], radii[i] * flat, n, phase)
        out.append(hull(pts, color, mat, name + '-joint'))
    return out


# --------------------------------------------------------------------------------------------------------- decals

def press(piece, poly, color, opacity=1.0, centre=None, lift=0.06, dir=(0, 0, 1)):
    """Put a flat polygon onto the piece. Each point (x, y, ·) is carried along `dir` (default: straight in from the
    front) onto the faceted surface and lifted a little off it; with `centre` given, along the ray from that centre
    instead. The decal is kept on the piece and turns with it."""
    planes = face_planes(piece.pts, piece.faces)
    poly = [np.asarray(p, float) for p in poly]
    view = unit(dir) if centre is None else unit(np.mean(poly, 0) - np.asarray(centre, float))
    nrm = sum(np.cross(p, q) for p, q in zip(poly, poly[1:] + poly[:1]))
    if np.dot(nrm, view) < 0:   # keep it counter-clockwise as seen from where it is pressed
        poly = poly[::-1]
    out = []
    for p in poly:
        p = np.asarray(p, float)
        if centre is not None:
            c = np.asarray(centre, float); d = p - c
            t = min((-(np.dot(n, c) + o) / nd) for n, o in planes for nd in [np.dot(n, d)] if nd > 1e-9)
            q = c + d * t; out.append(q + unit(d) * lift)
        else:
            dv = unit(dir); far = p + dv * 200.0
            t = max((np.dot(n, far) + o) / nd for n, o in planes for nd in [np.dot(n, dv)] if nd > 1e-9)
            out.append(far - dv * t + dv * lift)
    piece.decals.append((np.array(out), hexcol(color) if isinstance(color, str) else color, opacity))
    return piece


def face_planes(P, faces):
    pl = []
    c = P.mean(0)
    for f in faces:
        Q = P[f]; n = np.zeros(3)
        for i in range(len(Q)):
            a, b = Q[i], Q[(i + 1) % len(Q)]
            n += np.array([(a[1] - b[1]) * (a[2] + b[2]), (a[2] - b[2]) * (a[0] + b[0]), (a[0] - b[0]) * (a[1] + b[1])])
        n = unit(n); o = -np.dot(n, Q.mean(0))
        if np.dot(n, c) + o > 0:   # keep normals outward
            n, o = -n, -o
        pl.append((n, o))
    return pl


# ---------------------------------------------------------------------------------------------------------- light

class Light:
    """A warm key from the upper left front, a cool shadow, a faint fill from the right; per material."""

    def __init__(self, key=(-0.72, 0.52, 0.45), fill=(0.85, -0.05, 0.5), warm='#fff1dc', cool='#5a5f8c',
                 wrap=0.15, fill_k=0.22, amb=0.0):
        self.key = unit(key); self.fill = unit(fill)
        self.warm = hexcol(warm); self.cool = hexcol(cool); self.wrap = wrap; self.fill_k = fill_k; self.amb = amb

    MATS = {   # the shadow side: base × tint × depth; how far the lit side goes toward the light's colour
        'skin': (hexcol('#d9b2bd'), 0.80, 0.10),
        'decal': (hexcol('#d9b2bd'), 0.85, 0.05),
        'cloth': (None, 0.72, 0.06),
        'hair': (None, 0.70, 0.05),
        'metal': (None, 0.65, 0.25),
        'flat': (None, 1.0, 0.0),
    }

    def shade(self, base, n, mat):
        if mat == 'flat':
            return base
        k = (np.dot(n, self.key) + self.wrap) / (1 + self.wrap)
        k = min(max(k, 0.0), 1.0)
        k = k * k * (3 - 2 * k)
        tint, depth, warm_t = self.MATS.get(mat, self.MATS['cloth'])
        tint = mix(self.cool, hexcol('#ffffff'), 0.25) if tint is None else tint
        shadow = base * tint * depth
        lit = mix(base * 1.06, self.warm, warm_t)
        c = mix(shadow, lit, k)
        f = max(np.dot(n, self.fill), 0.0) * self.fill_k * (1 - k)
        c = c + f * base
        c = c + self.amb
        return np.clip(c, 0, 1)


# ---------------------------------------------------------------------------------------------------------- camera

class Camera:
    """Turns the model by yaw (degrees; + turns its face to the viewer's right), looks down by pitch,
    weak perspective with focal distance f (in model units), then scales to pixels and moves to (ox, oy)."""

    def __init__(self, yaw=0.0, pitch=0.0, f=900.0, scale=3.0, ox=400.0, oy=800.0, target=(0, 0, 0)):
        self.R = Rx(pitch) @ Ry(yaw)
        self.f = f; self.scale = scale; self.ox = ox; self.oy = oy; self.target = np.asarray(target, float)

    def view(self, P):
        return (np.asarray(P, float) - self.target) @ self.R.T

    def project(self, V):
        """Projective map (keeps planes planes): x' = f x/(f−z), y' likewise, z' = f z/(f−z)."""
        s = self.f / (self.f - V[:, 2])
        return np.column_stack([V[:, 0] * s, V[:, 1] * s, V[:, 2] * s])

    def px(self, Q):
        return np.column_stack([self.ox + Q[:, 0] * self.scale, self.oy - Q[:, 1] * self.scale])


# --------------------------------------------------------------------------------------------------------- render

def _area(xy):
    x, y = xy[:, 0], xy[:, 1]
    return 0.5 * (np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _front_z(planes, x, y):
    """The nearest (largest z) surface point of a convex piece on the line through (x, y), or None."""
    hi, lo = 1e9, -1e9
    for n, o in planes:
        if n[2] > 1e-9:
            hi = min(hi, (-o - n[0] * x - n[1] * y) / n[2])
        elif n[2] < -1e-9:
            lo = max(lo, (-o - n[0] * x - n[1] * y) / n[2])
        elif n[0] * x + n[1] * y + o > 1e-6:
            return None
    return hi if hi >= lo - 1e-6 else None


def render(pieces, cam, light=None, stroke=0.7, edges=None, decals=True, flat=None):
    """→ list of SVG strings. Exact hidden surfaces: every face turned to the viewer is cut down to the part no
    face of another piece lies in front of (on the overlap both are planes, so "in front" is a half-plane); decals
    are cut the same way and drawn over their piece. Nothing depends on a drawing order, so pieces may wrap round
    or pass through each other (hair round a head, an arm into a body)."""
    light = light or Light()
    F = []       # visible faces: dict(poly, plane (a, b, c): z = a x + b y + c, piece, colour, z)
    D = []       # decals
    for pi, p in enumerate(pieces):
        V = cam.view(p.pts); Q = cam.project(V)
        vplanes = face_planes(V, p.faces)
        for fi, f in enumerate(p.faces):
            q = Q[f]
            if _area(q[:, :2]) <= 1e-9:
                continue
            pl = _zplane(q)
            if pl is None:
                continue
            c = flat or tohex(light.shade(p.color, vplanes[fi][0], p.mat))
            F.append(dict(xy=[tuple(v) for v in q[:, :2]], pl=pl, piece=pi, col=c, z=q[:, 2].mean()))
        for dpts, col, op in p.decals:
            DV = cam.view(dpts); DQ = cam.project(DV)
            if _area(DQ[:, :2]) <= 1e-9:
                continue
            pl = _zplane(DQ)
            if pl is None:
                continue
            n = vplanes[min(range(len(p.faces)), key=lambda i: abs(np.dot(vplanes[i][0], DV.mean(0)) + vplanes[i][1]))][0]
            if n[2] <= 0.02:      # its face is turned away
                continue
            c = tohex(light.shade(col, n, 'flat' if p.mat == 'flat' else 'decal'))
            D.append(dict(xy=[tuple(v) for v in DQ[:, :2]], pl=pl, piece=pi, col=c, op=op))
    boxes = [_bbox(f['xy']) for f in F]
    out = []
    for f in sorted(F, key=lambda f: f['z']):
        vis = _visible(f, F, boxes, convex=True)
        if vis is not None:
            out.append(_path(vis, cam, f['col'], stroke))
            if edges:   # the facet's outline (for the diagrams)
                out.append(_path(vis, cam, 'none', 0.0).replace('fill="none"', 'fill="none" stroke="%s" stroke-width="1.1" stroke-linejoin="round"' % edges))
    for d in (D if decals else []):
        vis = _visible(d, F, boxes, convex=False)
        if vis is not None:
            out.append(_path(vis, cam, d['col'], 0.0 if d['op'] < 1 else stroke * 0.4, d['op']))
    return out


def _zplane(q):
    """z = a x + b y + c through the projected polygon q (Newell normal)."""
    n = np.zeros(3)
    for i in range(len(q)):
        u, v = q[i], q[(i + 1) % len(q)]
        n += np.array([(u[1] - v[1]) * (u[2] + v[2]), (u[2] - v[2]) * (u[0] + v[0]), (u[0] - v[0]) * (u[1] + v[1])])
    if abs(n[2]) < 1e-9:
        return None
    m = q.mean(0)
    a, b = -n[0] / n[2], -n[1] / n[2]
    return a, b, m[2] - a * m[0] - b * m[1]


def _bbox(xy):
    xs = [p[0] for p in xy]; ys = [p[1] for p in xy]
    return min(xs), min(ys), max(xs), max(ys)


def _clip(poly, a, b, c):
    """Sutherland–Hodgman: the part of poly where a x + b y + c > 0."""
    out = []
    n = len(poly)
    for i in range(n):
        P, Q = poly[i], poly[(i + 1) % n]
        dp = a * P[0] + b * P[1] + c; dq = a * Q[0] + b * Q[1] + c
        if dp > 0:
            out.append(P)
        if (dp > 0) != (dq > 0):
            t = dp / (dp - dq)
            out.append((P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])))
    return out


def _cut_convex(subj, clip):
    """subj ∩ clip, clip convex and counter-clockwise."""
    out = subj
    n = len(clip)
    for i in range(n):
        (x1, y1), (x2, y2) = clip[i], clip[(i + 1) % n]
        out = _clip(out, -(y2 - y1), (x2 - x1), (y2 - y1) * x1 - (x2 - x1) * y1)
        if len(out) < 3:
            return []
    return out


EPS = 0.03
GRID = 1e-3


def _visible(f, F, boxes, convex):
    x0, y0, x1, y1 = _bbox(f['xy'])
    a, b, c = f['pl']
    occ = []
    for g, (gx0, gy0, gx1, gy1) in zip(F, boxes):
        if g['piece'] == f['piece'] or gx0 >= x1 or gx1 <= x0 or gy0 >= y1 or gy1 <= y0:
            continue
        if convex:
            Q = _cut_convex(f['xy'], g['xy'])
        else:
            try:
                Q = _areal(Polygon(f['xy']).buffer(0).intersection(Polygon(g['xy']), grid_size=GRID))
            except Exception:
                Q = None
        if not Q:
            continue
        ga, gb, gc = g['pl']
        da, db, dc = ga - a, gb - b, gc - c - EPS     # > 0 where g is nearer
        if convex:
            Q = _clip(Q, da, db, dc)
            if len(Q) >= 3:
                occ.append(Polygon(Q))
        else:
            minx, miny, maxx, maxy = Q.bounds
            box = [(minx - 1, miny - 1), (maxx + 1, miny - 1), (maxx + 1, maxy + 1), (minx - 1, maxy + 1)]
            hp = _clip(box, da, db, dc)
            if len(hp) >= 3:
                try:
                    o = _areal(Q.intersection(Polygon(hp), grid_size=GRID))
                except Exception:
                    o = None
                if o is not None:
                    occ.append(o)
    P = Polygon(f['xy']).buffer(0)
    occ = [o for o in (_areal(o) for o in occ) if o is not None]
    if occ:
        occ = [o for o in occ if not o.is_empty]
        try:
            P = P.difference(unary_union(occ, grid_size=GRID), grid_size=GRID)
        except Exception:    # a degenerate overlap: cut one by one
            for o in occ:
                try:
                    P = P.difference(o, grid_size=GRID)
                except Exception:
                    pass
    if P.is_empty or P.area < 1e-4:
        return None
    return P


def _areal(g):
    """Only the polygons of a geometry (an overlay may leave lines and points), or None."""
    if g is None or g.is_empty:
        return None
    if g.geom_type in ('Polygon', 'MultiPolygon'):
        return g
    parts = [p for p in getattr(g, 'geoms', []) if p.geom_type in ('Polygon', 'MultiPolygon') and not p.is_empty]
    return unary_union(parts) if parts else None


def _path(geom, cam, color, stroke, opacity=1.0):
    polys = [geom] if geom.geom_type == 'Polygon' else [g for g in getattr(geom, 'geoms', []) if g.geom_type == 'Polygon']
    d = []
    for pg in polys:
        if pg.area < 0.01 or pg.area < 0.04 * pg.length:   # drop slivers left at the edges of hidden faces
            continue
        for ring_ in [pg.exterior] + list(pg.interiors):
            xy = cam.px(np.array(ring_.coords)[:-1])
            d.append('M' + 'L'.join('%.1f,%.1f' % (x, y) for x, y in xy) + 'Z')
    if not d:
        return ''
    op = '' if opacity >= 1 else ' fill-opacity="%.2f"' % opacity
    st = ' stroke="%s" stroke-width="%.2f" stroke-linejoin="round"' % (color, stroke) if stroke > 0 else ''
    return '<path d="%s" fill="%s" fill-rule="evenodd"%s%s/>' % (''.join(d), color, op, st)


def _poly(xy, color, stroke, opacity=1.0):
    pts = ' '.join('%.1f,%.1f' % (x, y) for x, y in xy)
    op = '' if opacity >= 1 else ' fill-opacity="%.2f"' % opacity
    st = ' stroke="%s" stroke-width="%.2f" stroke-linejoin="round"' % (color, stroke) if stroke > 0 else ''
    return '<polygon points="%s" fill="%s"%s%s/>' % (pts, color, op, st)


# ------------------------------------------------------------------------------------------------------------ svg

class Doc:
    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h; self.parts = []; self.defs = []
        if bg:
            self.parts.append('<rect width="%d" height="%d" fill="%s"/>' % (w, h, bg))

    def add(self, items):
        if isinstance(items, str):
            self.parts.append(items)
        else:
            self.parts.extend(items)

    def text(self, x, y, s, size=22, color='#3b3a48', anchor='middle', weight=500, opacity=1.0):
        self.parts.append('<text x="%.1f" y="%.1f" font-family="\'PT Sans\', \'Helvetica Neue\', Arial, sans-serif" '
                          'font-size="%d" font-weight="%d" fill="%s" fill-opacity="%.2f" text-anchor="%s" '
                          'letter-spacing="1">%s</text>' % (x, y, size, weight, color, opacity, anchor, s))

    def svg(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s%s</svg>'
                % (self.w, self.h, self.w, self.h,
                   ('<defs>%s</defs>' % ''.join(self.defs)) if self.defs else '', ''.join(self.parts)))

    def save(self, path):
        with open(path, 'w') as f:
            f.write(self.svg())
