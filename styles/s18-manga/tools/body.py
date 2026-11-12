"""Bodies, drawn in 2D in the three-quarter view of the figure: garments as shapes with folds, limbs as two pen lines,
hands with fingers, shoes. A figure is written in head units (the character's head height = 1; y down, the ground at
y = 0) and mapped to the page by Fig, so tone keeps its pitch on the page whatever the size of the figure."""
import math, random
from pen import *
from head import Head, View, draw_head, EXPR


class Fig:
    def __init__(self, x, y, s, lw=2.0, flip=False):
        self.x, self.y, self.s, self.lw, self.flip = x, y, s, lw, flip

    def p(self, x, y):
        return (self.x + (-x if self.flip else x) * self.s, self.y + y * self.s)

    def P(self, pts):
        return [self.p(*q[:2]) for q in pts]


# ---------------------------------------------------------------- shapes

def shape(F, pts, fill=PAPER, line=1.0, k=0.6, smooth=True, closed=True, skip=None):
    """A filled shape with the contour weighted by the light."""
    P = F.P(pts)
    out = fillpath(P, fill, smooth=smooth)
    if line:
        out += outline(P, F.lw * line, k, closed=closed, smooth=smooth, skip=skip)
    return out


def shaded(F, pts, base=0.0, dark=0.35, off=(0.06, 0.03), line=1.0, smooth=True, black=False, extra=''):
    """A form with tone `base` and a shadow (`dark`) along its lower right edges: the shape moved towards the light
    covers it all but a band on the far side — the cast shadow of manga, cut in tone."""
    P = F.P(pts)
    d = smooth_d(P) if smooth else poly(P)
    dx, dy = off[0] * F.s * (-1 if F.flip else 1), off[1] * F.s
    fill_base = PAPER if base <= 0 else f'url(#{tone_id(base)})'
    fill_dark = INK if black else f'url(#{tone_id(dark)})'
    lit = f'<path d="{d}" transform="translate({-dx:.1f},{-dy:.1f})" fill="{PAPER}"/>'
    lit += f'<path d="{d}" transform="translate({-dx:.1f},{-dy:.1f})" fill="{fill_base}"/>' if base > 0 else ''
    inner = f'<path d="{d}" fill="{fill_dark}"/>' + lit + extra
    out = f'<path d="{d}" fill="{PAPER}"/>' + clip(d, inner)
    if line:
        out += outline(P, F.lw * line, 0.6, smooth=smooth)
    return out


def line(F, pts, w=0.8, taper=(0.25, 0.3), smooth=True):
    return stroke(F.P(pts), F.lw * w if not isinstance(w, (list, tuple)) else [F.lw * a for a in w], taper=taper, smooth=smooth)


def folds(F, lines, w=0.6):
    """Fold lines: each a list of points, drawn thin with a thicker middle."""
    return ''.join(stroke(F.P(L), [F.lw * w * 0.4, F.lw * w * 1.2, F.lw * w * 0.4], taper=(0.3, 0.4)) for L in lines)


def hatchf(F, pts, angle=-40, gap=0.035, w=0.45, density=None, seed=2):
    P = F.P(pts)
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    return hatch(P, (min(xs), min(ys), max(xs), max(ys)), angle=angle if not F.flip else 180 - angle,
                 gap=gap * F.s, w=F.lw * w, density=density, seed=seed)


def tonef(F, pts, level=0.2, smooth=True):
    return tone(F.P(pts), level, smooth)


# ---------------------------------------------------------------- limbs

def limb(F, chain, radii, fill=PAPER, line_w=1.0, ends=(False, False), shade=None):
    """A limb (a sleeve, a trouser leg, a bare arm): two contour lines along a chain of joints, each joint with its
    radius (a radius may be a pair: (towards the left of the direction, towards the right)). Returns the fill and
    the lines. ends: close the start / the end with a line."""
    n = len(chain)
    C = catmull(chain, False, 6)
    R = []
    m = len(C)
    for i in range(m):
        t = i / (m - 1) * (n - 1)
        j = min(int(t), n - 2); u = t - j
        ra = radii[j] if isinstance(radii[j], (tuple, list)) else (radii[j], radii[j])
        rb = radii[j + 1] if isinstance(radii[j + 1], (tuple, list)) else (radii[j + 1], radii[j + 1])
        R.append((ra[0] + (rb[0] - ra[0]) * u, ra[1] + (rb[1] - ra[1]) * u))
    N = normals(C)
    L = [(C[i][0] + N[i][0] * R[i][0], C[i][1] + N[i][1] * R[i][0]) for i in range(m)]
    Rr = [(C[i][0] - N[i][0] * R[i][1], C[i][1] - N[i][1] * R[i][1]) for i in range(m)]
    PL, PR = F.P(L), F.P(Rr)
    out = fillpath(PL + PR[::-1], fill, smooth=False)
    if shade:
        out += clip(PL + PR[::-1], shade, smooth=False)
    # heavier on the side away from the light (the right side of the figure)
    lw = F.lw * line_w
    out += stroke(PL, [lw * 0.8, lw * 1.0, lw * 0.9], taper=(0.06, 0.06), smooth=False)
    out += stroke(PR, [lw * 1.2, lw * 1.5, lw * 1.3], taper=(0.06, 0.06), smooth=False)
    if ends[0]:
        out += stroke([PL[0], PR[0]], lw * 0.9, taper=(0.1, 0.1), smooth=False)
    if ends[1]:
        out += stroke([PL[-1], PR[-1]], lw * 0.9, taper=(0.1, 0.1), smooth=False)
    return out, (L, Rr)


# ---------------------------------------------------------------- hands

# the hand in 3D, in units of its length: the wrist at 0, the fingers along +y, the thumb on +x, the palm facing +z
FINGERS = [  # x at the knuckle, y of the knuckle, length, radius
    (0.148, 0.50, 0.41, 0.054), (0.050, 0.52, 0.46, 0.056), (-0.050, 0.51, 0.43, 0.053), (-0.143, 0.48, 0.35, 0.047)]
POSES = dict(relaxed=[(18, 25, 15), (22, 28, 18), (26, 30, 20), (30, 34, 22)],
             open=[(4, 4, 2), (2, 3, 2), (3, 3, 2), (6, 6, 4)],
             fist=[(88, 100, 65)] * 4, hold=[(70, 85, 55)] * 4,
             point=[(5, 5, 3), (88, 100, 65), (88, 100, 65), (88, 100, 65)],
             loose=[(35, 40, 25), (40, 45, 30), (45, 50, 30), (50, 55, 35)])
THUMBS = dict(relaxed=(8, 10, 10), open=(-25, 0, 0), fist=(55, 35, 30), hold=(35, 25, 25), point=(55, 35, 30), loose=(15, 15, 15))


def _rx(p, a):
    c, s = math.cos(a), math.sin(a)
    return (p[0], p[1] * c - p[2] * s, p[1] * s + p[2] * c)


def _capsule(F, C3, r, proj, lw):
    P = [proj(p) for p in C3]
    C = catmull(P, False, 4)
    N = normals(C)
    Lf = [(c[0] + n[0] * r, c[1] + n[1] * r) for c, n in zip(C, N)]
    Rg = [(c[0] - n[0] * r, c[1] - n[1] * r) for c, n in zip(C, N)]
    ta = math.atan2(C[-1][1] - C[-2][1], C[-1][0] - C[-2][0])
    tip = [(C[-1][0] + math.cos(ta + t) * r, C[-1][1] + math.sin(ta + t) * r) for t in [math.pi / 2 - k * math.pi / 8 for k in range(9)]]
    ring = Lf + tip + Rg[::-1]
    PP = F.P(ring)
    return fillpath(PP, PAPER, smooth=False) + stroke(PP, lw, taper=(0.03, 0.03), smooth=False)


def hand(F, wrist, ang, size=0.62, pose='relaxed', curl=None, side=1, spread=0.0, thumb=None, twist=0, tilt=0, lw=None):
    """A hand: wrist point (head units), direction of the hand on the page (degrees; 90 points down), size (its
    length in head units). twist turns it about its own axis: 0 shows the back of the hand, 90 the thumb side,
    180 the palm; tilt leans the fingers towards (+) or away from the viewer. side: +1 a right hand, -1 a left.
    pose: relaxed, loose, open, fist, hold (round a handle), point."""
    lw = (lw or F.lw * 0.8)
    curls = curl or POSES[pose]
    th = thumb or THUMBS[pose]
    a = math.radians(ang - 90); ca, sa = math.cos(a), math.sin(a)
    tw = math.radians(twist); ct, st = math.cos(tw), math.sin(tw)
    tl = math.radians(tilt)

    def view(p):
        x, y, z = p
        x *= side
        # twist about the hand's axis (y), the back of the hand (-z) towards the viewer at twist 0
        X = x * ct + z * st
        Z = -x * st + z * ct
        Z = -Z
        # tilt: towards the viewer
        Y = y * math.cos(tl) - Z * math.sin(tl)
        Z2 = y * math.sin(tl) + Z * math.cos(tl)
        return X, Y, Z2

    def proj(p):
        X, Y, _ = view(p)
        return (wrist[0] + (X * ca - Y * sa) * size, wrist[1] + (X * sa + Y * ca) * size)
    parts = []
    # palm: a plate, drawn as the hull of its corners
    corners = []
    for z in (-0.06, 0.06):
        for x, y in [(-0.13, 0.0), (0.12, 0.0), (0.20, 0.22), (0.19, 0.50), (0.06, 0.53), (-0.05, 0.52), (-0.18, 0.47), (-0.19, 0.2)]:
            corners.append((x, y, z * (0.7 if y < 0.05 else 1)))
    P2 = [proj(p) for p in corners]
    hull = _hull(P2)
    zpalm = sum(view(p)[2] for p in corners) / len(corners)
    palm_svg = fillpath(F.P(hull), PAPER) + outline(F.P(hull), lw * 1.05, 0.4)
    # lines on the palm or the back
    if ct < -0.3:
        palm_svg += stroke(F.P([proj((-0.15, 0.33, 0.07)), proj((0.0, 0.37, 0.07)), proj((0.17, 0.30, 0.07))]), lw * 0.4, taper=(0.4, 0.4))
        palm_svg += stroke(F.P([proj((0.16, 0.12, 0.07)), proj((0.05, 0.3, 0.07)), proj((0.02, 0.48, 0.07))]), lw * 0.35, taper=(0.4, 0.4))
    elif ct > 0.3:
        for x0, y0, _, _ in FINGERS[:3]:
            palm_svg += stroke(F.P([proj((x0 * 0.4, 0.15, -0.07)), proj((x0, y0 - 0.05, -0.07))]), lw * 0.3, taper=(0.5, 0.5))
    parts.append((zpalm, palm_svg))
    for i, (x0, y0, L, r) in enumerate(FINGERS):
        x0 *= 1 + spread
        flex = curls[i]
        seg = [L * 0.45, L * 0.32, L * 0.23]
        p = (x0, y0, 0.0)
        d = (spread * (i - 1.5) * -0.12, 1.0, 0.0)
        C3 = [p]
        ang_acc = 0.0
        for sl, fx in zip(seg, flex):
            ang_acc += math.radians(fx)
            dd = _rx(d, ang_acc)
            p = (p[0] + dd[0] * sl, p[1] + dd[1] * sl, p[2] + dd[2] * sl)
            C3.append(p)
        z = sum(view(q)[2] for q in C3) / len(C3)
        parts.append((z, _capsule(F, C3, r * size, proj, lw)))
    # thumb: from the base of the palm out and forward, bending towards the palm
    b = (0.17, 0.20, 0.03)
    d = (0.16, 0.92, 0.36)
    C3 = [b]
    p = b
    acc = math.radians(th[0]) * 0.6
    for sl, fx in zip([0.15, 0.14, 0.11], th):
        acc += math.radians(fx) * 0.8
        # bend: turn the direction towards -x (across the palm) and +z
        dd = (d[0] - 0.55 * math.sin(acc), d[1] * math.cos(acc * 0.6), d[2] + 0.35 * math.sin(acc))
        n = math.sqrt(sum(c * c for c in dd)); dd = tuple(c / n for c in dd)
        p = (p[0] + dd[0] * sl, p[1] + dd[1] * sl, p[2] + dd[2] * sl)
        C3.append(p)
    z = sum(view(q)[2] for q in C3) / len(C3)
    parts.append((z + 0.02, _capsule(F, C3, 0.058 * size, proj, lw)))
    parts.sort(key=lambda t: t[0])
    return ''.join(s for _, s in parts)


def _hull(P):
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in P))
    if len(pts) < 3:
        return pts
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


# ---------------------------------------------------------------- shoes

def shoe(F, heel, toe, h=0.16, kind='shoe', fill=PAPER, sole=0.035):
    """A shoe seen from the side or three-quarter: heel point and toe point on the ground."""
    hx, hy = heel; tx, ty = toe
    d = 1 if tx > hx else -1
    L = abs(tx - hx)
    top = min(hy, ty) - h
    if kind == 'boot':
        pts = [(hx - d * 0.02, hy), (tx, ty), (tx + d * 0.01, ty - h * 0.45), (tx - d * L * 0.35, top + h * 0.3),
               (hx + d * L * 0.25, top - h * 0.8), (hx - d * 0.0, top - h * 0.75), (hx - d * 0.04, hy - h * 0.4)]
    elif kind == 'sneaker':
        pts = [(hx - d * 0.02, hy), (tx, ty), (tx + d * 0.0, ty - h * 0.55), (tx - d * L * 0.4, top + h * 0.25),
               (hx + d * L * 0.25, top - h * 0.05), (hx, top + h * 0.05), (hx - d * 0.04, hy - h * 0.4)]
    else:
        pts = [(hx - d * 0.02, hy), (tx, ty), (tx + d * 0.0, ty - h * 0.5), (tx - d * L * 0.4, top + h * 0.25),
               (hx + d * L * 0.25, top + h * 0.05), (hx, top + h * 0.15), (hx - d * 0.035, hy - h * 0.4)]
    out = shape(F, pts, fill, line=1.1)
    out += line(F, [(hx - d * 0.02, hy - sole), (tx - d * 0.01, ty - sole)], 0.6, smooth=False)
    if kind == 'sneaker':
        out += line(F, [(hx + d * L * 0.3, top + h * 0.15), (tx - d * L * 0.3, top + h * 0.45)], 0.5)
    return out


# ---------------------------------------------------------------- the head on the body

def head_on(F, mod, at, yaw=30, pitch=0, roll=0, hs=1.0, e=None, hair='all', lw=None, neck=True):
    """Draw a character's head with its neck at `at` (the pit of the neck, head units of the figure).
    hair: 'all', 'back' (only the hair behind), 'front' (the head and the hair in front)."""
    x, y = F.p(*at)
    s = F.s * hs
    # the neck pit is about 0.95 head heights below the eye line
    v = View(yaw=-yaw if F.flip else yaw, pitch=pitch, roll=-roll if F.flip else roll, s=s, x=x, y=y - 0.80 * s)
    h = Head(mod.HEAD, EXPR.get(e) if isinstance(e, str) else e)
    lw = lw or F.lw * 0.95
    if hair == 'back':
        return mod.HAIR.back(h, v, lw)

    class Front:
        def back(self, h, v, lw):
            return ''

        def front(self, h, v, lw):
            return mod.HAIR.front(h, v, lw)
    hh = Front() if hair == 'front' else mod.HAIR
    return draw_head(h, v, lw, hair=hh, extras=mod.EXTRAS, neck=neck)
