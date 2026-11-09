"""Full figures: lofts for torso, skirt or coat, legs, arms, hands and feet, drawn back to front, with the head on top."""
import math
import numpy as np
from arc import *
from face import *
from person import *


def limb(y0, y1, x_tab, z_tab, a_tab, d_tab=None, p=2.0):
    """A limb hanging along y: centre x(y), z(y), half width a(y), half depth d(y)."""
    d_tab = d_tab or a_tab
    return Loft(a=a_tab, bf=d_tab, bb=d_tab, p=p, x0=x_tab, z0=z_tab, y0=y0, y1=y1)


class Part:
    def __init__(self, surf, base, kind='cloth', pieces=(), lines=(), shadow=None, bias=0.0, center=None, pal=None, rim=None):
        self.surf, self.base, self.kind = surf, base, kind
        self.pieces, self.lines = list(pieces), list(lines)
        self.shadow, self.bias, self.center, self.pal, self.rim = shadow, bias, center, pal, rim


def part_svg(doc, view, part):
    if part.kind == 'skin':
        R = regions(part.surf, view)
        s = shade_layers(doc, R, part.pal)
        if getattr(part, 'outline', None) and not R['sil'].is_empty:
            # a thin dark edge, so fingers next to each other stay apart
            s += path(poly_path(R['sil']), 'none', part.pal['line'], part.outline * view.s, 0.55)
        return s
    return draw_cloth(doc, view, part.surf, part.base, part.pieces, shadow=part.shadow or '#7f7590', rim=part.rim, lines=part.lines)


def draw_figure(doc, P, view, e=None, parts=None):
    """The whole person: back hair, neck, body parts back to front, then the head."""
    parts = parts if parts is not None else P.body()

    def depth(pt):
        c = pt.center
        _, _, z = view.proj(np.array([c[0]], float), np.array([c[1]], float), np.array([c[2]], float))
        return float(z[0]) + pt.bias

    def body(doc_, view_, head):
        return ''.join(part_any(doc_, view_, pt) for pt in sorted(parts, key=depth))
    saved = getattr(P, 'bust', None)
    P.bust = body
    try:
        return draw_head(doc, P, view, e, bust=True)
    finally:
        P.bust = saved


def shoe(x, y_top, y_sole, length, width, color, z=0.0, toe=1.0):
    """A shoe: sections along y from the ankle to the sole, long toward +z."""
    h = y_sole - y_top
    return Loft(a=[(y_top, width * 0.75), (y_top + h * 0.5, width), (y_sole, width)],
                bf=[(y_top, width * 0.8), (y_top + h * 0.45, length * 0.55 * toe), (y_sole - h * 0.15, length * toe), (y_sole, length * 0.95 * toe)],
                bb=[(y_top, width * 0.8), (y_top + h * 0.5, width * 1.0), (y_sole, width * 1.0)],
                p=2.2, x0=[(y_top, x), (y_sole, x)], z0=[(y_top, z), (y_sole, z)], y0=y_top, y1=y_sole)


def hand(x, y0, y1, z, w, d, curl=0.0):
    """A relaxed hand as a soft mitten."""
    h = y1 - y0
    return Loft(a=[(y0, w * 0.75), (y0 + h * 0.3, w), (y0 + h * 0.7, w * 0.95), (y1, w * 0.35)],
                bf=[(y0, d), (y0 + h * 0.3, d * 1.05), (y0 + h * 0.75, d * 0.9), (y1, d * 0.4)],
                bb=[(y0, d), (y0 + h * 0.5, d), (y1, d * 0.4)], p=2.3,
                x0=[(y0, x), (y1, x)], z0=[(y0, z), (y1, z + curl)], y0=y0, y1=y1)


class BoxPart:
    """A box (a book, a case): centre, half sizes, a turn about y and a tilt about x, face colours."""

    def __init__(self, c, hs, yaw=0.0, tilt=0.0, cols=None, bias=0.0, deco=None):
        self.center, self.hs, self.yaw, self.tilt = c, hs, yaw, tilt
        self.cols = cols or {}
        self.bias = bias
        self.kind = 'box'
        self.deco = deco

    def svg(self, doc, view):
        cx, cy, cz = self.center
        hx, hy, hz = self.hs
        cyw, syw = math.cos(math.radians(self.yaw)), math.sin(math.radians(self.yaw))
        ct, st = math.cos(math.radians(self.tilt)), math.sin(math.radians(self.tilt))

        def P(x, y, z):
            y2, z2 = y * ct - z * st, y * st + z * ct
            x3, z3 = x * cyw + z2 * syw, -x * syw + z2 * cyw
            return (cx + x3, cy + y2, cz + z3)
        faces = {'front': [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)], 'back': [(1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1)],
                 'left': [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)], 'right': [(1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1)],
                 'top': [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)], 'bottom': [(-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1)]}
        normals = {'front': (0, 0, 1), 'back': (0, 0, -1), 'left': (-1, 0, 0), 'right': (1, 0, 0), 'top': (0, -1, 0), 'bottom': (0, 1, 0)}
        out = []
        for k, f in faces.items():
            n = np.array(P(*normals[k])) - np.array(P(0, 0, 0))
            nx, ny, nz = view.rot(np.array([n[0]]), np.array([n[1]]), np.array([n[2]]))
            if nz[0] <= 0.02:
                continue
            pts = [view.proj(np.array([q[0]]), np.array([q[1]]), np.array([q[2]])) for q in [P(a * hx, b * hy, c * hz) for a, b, c in f]]
            d = 'M' + 'L'.join('%s,%s' % (fmt(p[0][0]), fmt(p[1][0])) for p in pts) + 'Z'
            col = self.cols.get(k, self.cols.get('side', '#888'))
            dl = float(nx[0] * view.L[0] + ny[0] * view.L[1] + nz[0] * view.L[2])
            out.append(path(d, col))
            if dl < 0.25:
                out.append(path(d, '#6e6680', op=min(0.7, 0.35 + (0.25 - dl)), extra=' style="mix-blend-mode:multiply"'))
            if self.deco and k == 'front':
                out.append(self.deco(view, P))
        return ''.join(out)


def part_any(doc, view, part):
    if getattr(part, 'kind', '') == 'box':
        return part.svg(doc, view)
    return part_svg(doc, view, part)


# ---------------------------------------------------------------- hands with fingers

def _unit(v):
    v = np.array(v, float)
    return v / (np.linalg.norm(v) + 1e-9)


class FTube(Tube):
    """A tube flattened along a given direction (a palm: thin along its normal)."""

    def __init__(self, pts, radii, flat, normal):
        Tube.__init__(self, pts, radii, flat)
        T = np.gradient(self.C, axis=0)
        T /= np.linalg.norm(T, axis=-1, keepdims=True) + 1e-9
        n = np.array(normal, float)[None, :]
        N = n - (n * T).sum(-1, keepdims=True) * T
        N /= np.linalg.norm(N, axis=-1, keepdims=True) + 1e-9
        self.N, self.B = N, np.cross(T, N)


def hand_parts(wrist, d, n, pal, L=56, wid=24, curl=0.2, spread=0.3, thumb=(0.8, 0.2), side=1, bias=0.0, outline=1.6):
    """A hand of a palm, four fingers and a thumb, as skin parts.
    wrist: the point where it starts; d: the direction the hand points; n: where the palm faces (the fingers curl
    toward it); L: length wrist to fingertip; wid: width of the palm; curl: radians per finger joint (a number or four,
    index to little finger); spread: fan of the fingers; thumb: (angle away from the fingers, angle toward the palm);
    side: +1 or -1 puts the thumb on one side or the other."""
    w = np.array(wrist, float)
    d = _unit(d)
    n = np.array(n, float)
    n = _unit(n - n.dot(d) * d)
    s = np.cross(n, d) * side
    curl = [curl] * 4 if not isinstance(curl, (list, tuple)) else list(curl)
    pl = L * 0.5
    parts = []

    def add(surf, c, b=0.0):
        pt = Part(surf, None, kind='skin', pal=pal, center=tuple(c), bias=bias + b)
        pt.outline = outline
        parts.append(pt)
    palm = FTube([w - d * wid * 0.2, w + d * pl * 0.5, w + d * pl * 1.02], [wid * 0.4, wid * 0.53, wid * 0.5], 0.42, n)
    add(palm, w + d * pl * 0.5)
    lens = [0.47, 0.52, 0.48, 0.38]
    for i in range(4):
        b = w + d * (pl - L * 0.03) + s * wid * (0.38 - 0.253 * i)
        a = spread * (0.5 - i / 3.0)
        d0 = _unit(d * math.cos(a) + s * math.sin(a))
        rf = wid * 0.128 * (1 - 0.07 * i)
        pts, p = [b], b
        for k, f in enumerate((0.45, 0.3, 0.25)):
            ang = curl[i] * (k + 1)
            dk = d0 * math.cos(ang) + n * math.sin(ang)
            p = p + dk * L * lens[i] * f
            pts.append(p)
        pts.append(p + dk * rf * 0.7)
        add(Tube([tuple(q) for q in pts], [rf * 1.08, rf, rf * 0.93, rf * 0.86, rf * 0.4]), (pts[1] + pts[2]) / 2 + n * rf, 0.5 + 0.1 * i)
    t0, t1 = thumb
    b = w + d * pl * 0.18 + s * wid * 0.36
    dt = _unit(d * math.cos(t0) + s * math.sin(t0))
    dt = _unit(dt * math.cos(t1) + n * math.sin(t1))
    rt = wid * 0.165
    p1 = b + dt * L * 0.24
    dt2 = _unit(dt + d * 0.35 + n * 0.2 * (1 if t1 > 0.5 else 0))
    p2 = p1 + dt2 * L * 0.2
    add(Tube([tuple(b), tuple(p1), tuple(p2), tuple(p2 + dt2 * rt * 0.7)], [rt * 1.15, rt, rt * 0.88, rt * 0.4]), p1 + n * rt, 0.3)
    return parts
