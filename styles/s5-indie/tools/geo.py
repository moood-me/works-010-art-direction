"""Tiny 2.5D kit for flat indie characters: volumes as stacks of elliptic rings, projected at a yaw,
drawn as smooth flat shapes with one cel shade and a warm outline. Everything returns SVG strings."""
import math

LINE = '#3a2b2e'
SW = 3.2          # outline width; set by the caller (thinner for close-ups)
_uid = [0]


def uid(p='c'):
    _uid[0] += 1
    return f'{p}{_uid[0]}'


def mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02x}' for x, y in zip(a, b))


def shade_of(c):
    # shade: darker and a little toward violet, as in flat indie palettes
    return mix(mix(c, '#2a1f3d', .28), c, .0)


def light_of(c):
    return mix(c, '#fff6e4', .35)


def f(v):
    return f'{v:.1f}'


def smooth(pts, closed=True, k=1 / 6):
    """Catmull-Rom through points -> cubic Bezier path."""
    n = len(pts)
    if n < 2:
        return ''
    d = f'M{f(pts[0][0])},{f(pts[0][1])}'
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        d += f' C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}'
    return d + (' Z' if closed else '')


class View:
    def __init__(self, yaw_deg=0):
        self.t = math.radians(yaw_deg)
        self.c, self.s = math.cos(self.t), math.sin(self.t)

    def p(self, X, Y, Z=0):
        return (X * self.c + Z * self.s, Y)

    def depth(self, X, Z):
        return -X * self.s + Z * self.c


def lerp_rings(rings, y):
    """rings: list of (y, w, d, cx, cz) sorted by y. Returns interpolated (w,d,cx,cz)."""
    if y <= rings[0][0]:
        return rings[0][1:]
    for a, b in zip(rings, rings[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0] or 1)
            return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 5))
    return rings[-1][1:]


def norm_rings(rings):
    out = []
    for r in rings:
        r = list(r) + [0] * (5 - len(r))
        out.append(tuple(r))
    return out


def vol_outline(v, rings):
    """Silhouette of a stack of elliptic rings (y, w, d, cx, cz)."""
    rings = norm_rings(rings)
    right, left = [], []
    for y, w, d, cx, cz in rings:
        x0 = cx * v.c + cz * v.s
        h = math.hypot(w * v.c, d * v.s)
        right.append((x0 + h, y))
        left.append((x0 - h, y))
    pts = right + left[::-1]
    # collapse doubled tips (w=0)
    clean = []
    for q in pts:
        if not clean or math.dist(q, clean[-1]) > .3:
            clean.append(q)
    if math.dist(clean[0], clean[-1]) < .3:
        clean.pop()
    return clean


def surf(v, rings, phi, y, out=0):
    """A point on a ring-volume surface at angle phi (0 = front, + toward +X) and height y.
    Returns (x, y, facing) where facing = cos of the angle to the viewer."""
    w, d, cx, cz = lerp_rings(norm_rings(rings), y)
    X = cx + (w + out) * math.sin(phi)
    Z = cz + (d + out) * math.cos(phi)
    x, yy = v.p(X, y, Z)
    nx, nz = math.sin(phi) / max(w, 1e-3), math.cos(phi) / max(d, 1e-3)
    nn = math.hypot(nx, nz)
    facing = (-nx * v.s + nz * v.c) / nn
    return x, yy, facing


def shape(d, fill, shade=True, line=True, off=(-.09, -.06), size=60, extra='', sw=None, shade_col=None):
    """Flat fill + one cel shade on the lower right (light from upper left) + outline."""
    sw = SW if sw is None else sw
    out = ''
    if shade:
        cid = uid('k')
        sc = shade_col or shade_of(fill)
        dx, dy = off[0] * size, off[1] * size
        out += (f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'
                f'<g clip-path="url(#{cid})"><path d="{d}" fill="{sc}"/>'
                f'<path d="{d}" fill="{fill}" transform="translate({f(dx)},{f(dy)})"/></g>')
    else:
        out += f'<path d="{d}" fill="{fill}"/>'
    if line:
        out += f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="{f(sw)}" stroke-linejoin="round" {extra}/>'
    return out


def vol(v, rings, fill, **kw):
    pts = vol_outline(v, rings)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    size = max(max(xs) - min(xs), (max(ys) - min(ys)) * .6)
    kw.setdefault('size', size)
    return shape(smooth(pts), fill, **kw)


def sphere(v, X, Y, Z, r, fill, **kw):
    x, y = v.p(X, Y, Z)
    d = (f'M{f(x - r)},{f(y)} a{f(r)},{f(r)} 0 1,0 {f(2 * r)},0 a{f(r)},{f(r)} 0 1,0 {f(-2 * r)},0 Z')
    kw.setdefault('size', 2 * r)
    return shape(d, fill, **kw)


def ellipse_d(x, y, rx, ry, rot=0):
    if rot:
        pts = []
        for i in range(16):
            a = i / 16 * 2 * math.pi
            px, py = rx * math.cos(a), ry * math.sin(a)
            ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
            pts.append((x + px * ca - py * sa, y + px * sa + py * ca))
        return smooth(pts)
    return (f'M{f(x - rx)},{f(y)} a{f(rx)},{f(ry)} 0 1,0 {f(2 * rx)},0 a{f(rx)},{f(ry)} 0 1,0 {f(-2 * rx)},0 Z')


def tube(v, pts3, width, fill, line=True, cap='round', taper=None, sw=None):
    """A limb: a stroked polyline (projected), outline drawn as a wider stroke under it."""
    sw = SW if sw is None else sw
    pts = [v.p(*p) for p in pts3]
    d = smooth(pts, closed=False, k=.2) if len(pts) > 2 else f'M{f(pts[0][0])},{f(pts[0][1])} L{f(pts[1][0])},{f(pts[1][1])}'
    return _clip_to_stroke(d, width, None, fill, shade_of(fill), sw, line, cap)


def _clip_to_stroke(d, width, _out, fill, sh, sw, line, cap):
    mid = uid('m')
    out = ''
    if line:
        out += f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="{f(width + 2 * sw)}" stroke-linecap="{cap}" stroke-linejoin="round"/>'
    out += (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="4000" height="4000">'
            f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{f(width)}" stroke-linecap="{cap}" stroke-linejoin="round"/></mask>')
    out += f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{f(width)}" stroke-linecap="{cap}" stroke-linejoin="round"/>'
    out += (f'<g mask="url(#{mid})"><path d="{d}" fill="none" stroke="{sh}" stroke-width="{f(width * .5)}" '
            f'stroke-linecap="round" transform="translate({f(width * .42)},{f(width * .12)})"/></g>')
    return out


def stroke(d, w=None, col=LINE, cap='round', extra=''):
    w = SW if w is None else w
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{f(w)}" stroke-linecap="{cap}" stroke-linejoin="round" {extra}/>'


def poly_d(pts, closed=False):
    d = 'M' + ' L'.join(f'{f(x)},{f(y)}' for x, y in pts)
    return d + (' Z' if closed else '')


def svg(body, vb, w, h, bg=None, defs=''):
    x, y, W, H = vb
    bgr = f'<rect x="{f(x)}" y="{f(y)}" width="{f(W)}" height="{f(H)}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(x)} {f(y)} {f(W)} {f(H)}" width="{w}" height="{h}">'
            f'<defs>{defs}</defs>{bgr}{body}</svg>')
