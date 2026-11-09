"""Shared drawing parts of the С11 «Резиновые 1930-е» style: smooth shapes, rubber hoses, the ball head with its
features, gloves, shoes, and the film look (paper, ink wobble, grain, vignette).

Everything is plain SVG text. Shapes are point lists turned into smooth closed curves (Catmull-Rom → cubic Bézier),
so a form is written as a few points round its outline.
"""
import math

INK = '#1b1714'          # ink: near-black, a little warm
LW = 3.2                 # outer ink line
LWI = 2.2                # inner line (folds, lids, mouth)
PAPER = '#efe2c4'        # aged paper / cel background
WHITE = '#fbf7ee'        # glove and eye white: warm, never pure
MOUTH = '#4a1712'        # inside of the mouth
TONGUE = '#d9533f'
CHEEK = '#e98a72'

_uid = [0]


def uid(p='u'):
    _uid[0] += 1
    return f'{p}{_uid[0]}'


def f(v):
    return f'{v:.1f}'


# ------------------------------------------------------------------ curves
def smooth(pts, closed=True, k=1.0):
    """Catmull-Rom spline through pts as an SVG path (cubic Bézier). k<1 makes it tighter."""
    n = len(pts)
    if n < 2:
        return ''
    d = [f'M {f(pts[0][0])} {f(pts[0][1])}']
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * k, p1[1] + (p2[1] - p0[1]) / 6 * k)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * k, p2[1] - (p3[1] - p1[1]) / 6 * k)
        d.append(f'C {f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}')
    if closed:
        d.append('Z')
    return ' '.join(d)


def sample(pts, steps=12):
    """Points along the open Catmull-Rom curve through pts."""
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                   + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


# ------------------------------------------------------------------ primitives
def P(d, fill='none', stroke=INK, w=LW, extra=''):
    s = f' stroke="{stroke}" stroke-width="{w}"' if stroke and w else ''
    return f'<path d="{d}" fill="{fill}"{s} stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def blob(pts, fill, w=LW, stroke=INK, k=1.0, extra=''):
    return P(smooth(pts, True, k), fill, stroke, w, extra)


def line(pts, w=LWI, stroke=INK, k=1.0, extra=''):
    return P(smooth(pts, False, k), 'none', stroke, w, extra)


def tline(pts, w0, w1, stroke=INK, w2=None):
    """A tapered ink stroke along pts: width w0 at the start, w1 in the middle, (w2 or w0) at the end — the brush line."""
    w2 = w0 if w2 is None else w2
    s = sample(pts, 10)
    n = len(s)
    left, right = [], []
    for i, p in enumerate(s):
        a = s[max(i - 1, 0)]
        b = s[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = i / (n - 1)
        w = (w0 + (w1 - w0) * (t / .5)) if t < .5 else (w1 + (w2 - w1) * ((t - .5) / .5))
        left.append((p[0] + nx * w / 2, p[1] + ny * w / 2))
        right.append((p[0] - nx * w / 2, p[1] - ny * w / 2))
    poly = left + right[::-1]
    d = 'M ' + ' L '.join(f'{f(x)} {f(y)}' for x, y in poly) + ' Z'
    return P(d, stroke, None, 0)


def circle(cx, cy, r, fill, w=LW, stroke=INK, extra=''):
    s = f' stroke="{stroke}" stroke-width="{w}"' if w else ''
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"{s} {extra}/>'


def ellipse(cx, cy, rx, ry, fill, w=LW, stroke=INK, rot=0, extra=''):
    s = f' stroke="{stroke}" stroke-width="{w}"' if w else ''
    t = f' transform="rotate({f(rot)} {f(cx)} {f(cy)})"' if rot else ''
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}"{s}{t} {extra}/>'


def g(body, x=0, y=0, s=1, rot=0, flip=False, extra=''):
    tr = f'translate({f(x)} {f(y)})'
    if rot:
        tr += f' rotate({f(rot)})'
    if s != 1 or flip:
        tr += f' scale({f(-s if flip else s)} {f(s)})'
    return f'<g transform="{tr}" {extra}>{body}</g>'


def clip(shape_d, body):
    i = uid('c')
    return f'<clipPath id="{i}"><path d="{shape_d}"/></clipPath><g clip-path="url(#{i})">{body}</g>'


# ------------------------------------------------------------------ hoses (the rubber limbs)
def tube(pts, w0, w1=None, w2=None):
    """Closed outline of a tube along pts, width w0 → w1 (middle) → w2 (end): a hose that may taper."""
    w1 = w0 if w1 is None else w1
    w2 = w1 if w2 is None else w2
    s = sample(pts, 10)
    n = len(s)
    left, right = [], []
    for i, p in enumerate(s):
        a = s[max(i - 1, 0)]
        b = s[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = i / (n - 1)
        w = (w0 + (w1 - w0) * (t / .5)) if t < .5 else (w1 + (w2 - w1) * ((t - .5) / .5))
        left.append((p[0] + nx * w / 2, p[1] + ny * w / 2))
        right.append((p[0] - nx * w / 2, p[1] - ny * w / 2))
    return 'M ' + ' L '.join(f'{f(x)} {f(y)}' for x, y in left + right[::-1]) + ' Z'


def hose(pts, w, fill, w1=None, w2=None, lw=LW):
    """A rubber-hose limb: one smooth arc, no elbow or knee, ends hidden in the glove or shoe."""
    return P(tube(pts, w, w1, w2), fill, INK, lw)


def union(parts, fill, lw=LW, inner=''):
    """Several shapes read as one form: an ink pass under all of them, then one fill pass — the seams vanish.
    parts: path d strings (closed)."""
    def pen(p, col, extra_w):
        if isinstance(p, tuple):
            return P(p[1], 'none', col, p[2] + extra_w)
        return P(p, col, col, extra_w or .01)
    ink = ''.join(pen(p, INK, lw * 2) for p in parts)
    col = ''.join(pen(p, fill, 0) for p in parts)
    return ink + col + inner


# ------------------------------------------------------------------ the ball head: features on a sphere
class Head:
    """A head as a ball of radius R turned by angle a (0 front, +right of the viewer, π/2 profile facing right).
    Features are placed by (x, y) on the front of the ball; project() returns where they land and how much they
    foreshorten."""

    def __init__(self, R, a=0.0, tilt=0.0):
        self.R, self.a, self.tilt = R, a, tilt

    def project(self, x, y, z=None):
        R = self.R
        if z is None:
            z = math.sqrt(max(R * R - x * x - y * y * .25, R * R * .05))
        ca, sa = math.cos(self.a), math.sin(self.a)
        X = x * ca + z * sa
        Z = -x * sa + z * ca
        fz = max(Z / math.sqrt(max(R * R - y * y * .25, 1)), 0.0)  # 1 facing us, 0 on the edge
        return X, y, Z, fz

    def muzzle(self, cy, A, B, C, cz):
        """The lower face as a second, flatter ball (semi-axes A wide, B tall, C deep) centred at (0, cy, cz): returns
        the path of its outline in the turned view. Turned to the side it bulges past the skull — cheeks and mouth."""
        X = cz * math.sin(self.a)
        rx = math.hypot(A * math.cos(self.a), C * math.sin(self.a))
        return (f'M {f(X - rx)} {f(cy)} A {f(rx)} {f(B)} 0 1 1 {f(X + rx)} {f(cy)} '
                f'A {f(rx)} {f(B)} 0 1 1 {f(X - rx)} {f(cy)} Z')

    def ball(self, grow=0):
        R = self.R + grow
        return f'M {f(-R)} 0 A {f(R)} {f(R)} 0 1 1 {f(R)} 0 A {f(R)} {f(R)} 0 1 1 {f(-R)} 0 Z'

    def jaw(self, pts, k=.5):
        """Project the lower face: like pts(), but the chin sits flatter than the ball would put it (k)."""
        R = self.R
        return [self.project(x, y, math.sqrt(max(R * R - x * x - y * y * k, R * R * .02)))[:2] for x, y in pts]

    def pts(self, pts, z=None):
        return [self.project(x, y, z)[:2] for x, y in pts]

    def loop(self, pts, push=1.6):
        """Project a loop drawn on the ball; points that turn to the back are pushed out past the edge, so a region
        bounded by the loop is cut cleanly by the silhouette."""
        out = []
        for x, y in pts:
            X, Y, Z, fz = self.project(x, y)
            if Z < 0:
                X = (1 if X >= 0 else -1) * max(abs(X), self.R * push)
            out.append((X, Y))
        return out

    def cap(self, face_loop, fill, grow=9, lw=LW):
        """Hair over the skull: the ball (grown by `grow`) minus the face. face_loop: (x, y) points on the front of
        the ball going round the bare face — over the forehead along the hairline, down the cheeks, under the chin."""
        R = self.R + grow
        fl = smooth(self.loop(face_loop), True)
        circ = f'M {-R} 0 A {R} {R} 0 1 1 {R} 0 A {R} {R} 0 1 1 {-R} 0 Z'
        big = f'M {-4 * R} {-4 * R} L {4 * R} {-4 * R} L {4 * R} {4 * R} L {-4 * R} {4 * R} Z'
        i = uid('h')
        return (f'<clipPath id="{i}"><path clip-rule="evenodd" d="{big} {fl}"/></clipPath>'
                f'<g clip-path="url(#{i})"><path d="{circ}" fill="{fill}" stroke="{INK}" stroke-width="{lw}"/></g>'
                + clip(circ, P(fl, 'none', INK, lw)))


# ------------------------------------------------------------------ eyes
def eye(cx, cy, rx, ry, look=(0, 0), fz=1.0, kind='pie', lid=None, lash=0, side=1, lower=None, pr=None,
        heavy=0.0, white=WHITE, rot=0, skin='#f4d6bd'):
    """A 1930s eye: a tall white oval, a big black pupil with a pie-cut wedge.
    kind: 'pie' (pupil with a cut wedge), 'dot' (solid black bean pupil), 'closed-happy' (∩ arc), 'closed' (− line),
    'ring' (round pupil with a highlight dot — the later, softer eye).
    lid: 0..1 how far the upper lid comes down (cuts the eye with a straight or tilted line); heavy: thick upper lid
    line (women); lash: number of lashes on the outer side (side=+1 outer is to the right).
    """
    rx = rx * (.35 + .65 * fz)
    out = []
    if kind == 'closed-happy':
        out.append(tline([(cx - rx, cy + ry * .15), (cx, cy - ry * .45), (cx + rx, cy + ry * .15)], 2, 6.5, w2=2))
        if lash:
            for i in range(lash):
                t = .6 + i * .2
                bx = cx + side * rx * (.55 + i * .22)
                by = cy - ry * (.25 - i * .18)
                out.append(tline([(bx, by), (bx + side * 9, by - 6 + i * 3)], 3, 2, w2=.6))
        return ''.join(out)
    if kind == 'closed':
        out.append(tline([(cx - rx, cy + ry * .1), (cx, cy + ry * .28), (cx + rx, cy + ry * .1)], 2, 5.5, w2=2))
        if lash:
            for i in range(lash):
                bx = cx + side * rx * (.7 + i * .2)
                by = cy + ry * (.2 - i * .02)
                out.append(tline([(bx, by), (bx + side * 9, by + 3 + i * 2)], 3, 2, w2=.6))
        return ''.join(out)
    eid = uid('e')
    ed = (f'M {f(cx)} {f(cy - ry)} C {f(cx + rx * 1.1)} {f(cy - ry)} {f(cx + rx * 1.05)} {f(cy + ry)} {f(cx)} {f(cy + ry)} '
          f'C {f(cx - rx * 1.05)} {f(cy + ry)} {f(cx - rx * 1.1)} {f(cy - ry)} {f(cx)} {f(cy - ry)} Z')
    inner = []
    pr = pr or (rx * .62, ry * .55)
    px, py = cx + look[0] * rx * .45, cy + ry * .18 + look[1] * ry * .35
    if kind == 'pie':
        inner.append(ellipse(px, py, pr[0], pr[1], INK, 0))
        # the pie-cut: a wedge of white from the pupil's centre to its upper edge
        wa = math.radians(-60 if side > 0 else -120)
        r1 = max(pr) * 1.3
        a0, a1 = wa - .32, wa + .32
        inner.append(P(f'M {f(px + pr[0] * .15 * math.cos(wa))} {f(py + pr[1] * .2 * math.sin(wa))} '
                       f'L {f(px + r1 * math.cos(a0))} {f(py + r1 * math.sin(a0))} '
                       f'L {f(px + r1 * math.cos(a1))} {f(py + r1 * math.sin(a1))} Z', white, None, 0))
    elif kind == 'dot':
        inner.append(ellipse(px, py, pr[0] * .7, pr[1] * .75, INK, 0))
    elif kind == 'ring':
        inner.append(ellipse(px, py, pr[0], pr[1], INK, 0))
        inner.append(ellipse(px - pr[0] * .3 * side, py - pr[1] * .4, pr[0] * .28, pr[1] * .22, white, 0))
    elif kind == 'spark':  # surprise: small pupils
        inner.append(ellipse(px, py, pr[0] * .45, pr[1] * .45, INK, 0))
    if lid is not None and lid > 0:
        ly = cy - ry + 2 * ry * lid
        tilt = rot  # positive: outer corner lower (sad), negative: inner lower (angry); given in units of ry
        y_in = ly + tilt * ry * -side * -1
        y_out = ly - tilt * ry * -side * -1
        xl, xr = cx - rx * 1.3, cx + rx * 1.3
        yl, yr = (y_in, y_out) if side > 0 else (y_out, y_in)
        inner.append(P(f'M {f(xl)} {f(cy - ry * 2)} L {f(xr)} {f(cy - ry * 2)} L {f(xr)} {f(yr)} L {f(xl)} {f(yl)} Z',
                       skin, None, 0))
        inner.append(P(f'M {f(xl)} {f(yl)} L {f(xr)} {f(yr)}', 'none', INK, LW))
    if lower is not None:
        ly = cy + ry - 2 * ry * lower
        inner.append(P(f'M {f(cx - rx * 1.3)} {f(cy + ry * 2)} L {f(cx + rx * 1.3)} {f(cy + ry * 2)} '
                       f'L {f(cx + rx * 1.3)} {f(ly)} Q {f(cx)} {f(ly - ry * .25)} {f(cx - rx * 1.3)} {f(ly)} Z',
                       skin, None, 0))
        inner.append(P(f'M {f(cx - rx * 1.3)} {f(ly)} Q {f(cx)} {f(ly - ry * .25)} {f(cx + rx * 1.3)} {f(ly)}', 'none', INK, LWI))
    out.append(f'<clipPath id="{eid}"><path d="{ed}"/></clipPath>')
    out.append(P(ed, white, None, 0))
    out.append(f'<g clip-path="url(#{eid})">{"".join(inner)}</g>')
    out.append(P(ed, 'none', INK, LW))
    if heavy:
        # thick upper lid: a black crescent over the top of the eye
        t = heavy
        top = cy - ry if lid is None else cy - ry + 2 * ry * lid
        if lid is None:
            out.append(P(f'M {f(cx - rx * .98)} {f(cy - ry * .25)} C {f(cx - rx * .9)} {f(cy - ry * 1.12)} {f(cx + rx * .9)} {f(cy - ry * 1.12)} {f(cx + rx * .98)} {f(cy - ry * .25)} '
                         f'C {f(cx + rx * .8)} {f(cy - ry * (1.02 - t))} {f(cx - rx * .8)} {f(cy - ry * (1.02 - t))} {f(cx - rx * .98)} {f(cy - ry * .25)} Z', INK, INK, 1))
        lash_y = cy - ry * .45 if lid is None else top
    else:
        lash_y = cy - ry * .45 if lid is None else cy - ry + 2 * ry * lid
    for i in range(lash):
        bx = cx + side * rx * (.82 + i * .1)
        by = lash_y - ry * .15 + i * ry * .2
        out.append(tline([(bx, by), (bx + side * 6, by - 7 + i * 3.5), (bx + side * 12, by - 9 + i * 5)], 3.2, 2.2, w2=.5))
    return ''.join(out)


def brow(cx, cy, w, tilt=0, arch=.25, th=4.5, side=1):
    """A thin arched brow; tilt>0 lifts the inner end (worry), tilt<0 lowers it (anger)."""
    xi, xo = cx - side * w / 2, cx + side * w / 2
    yi, yo = cy - tilt * w * .35, cy + tilt * w * .1
    return tline([(xi, yi), (cx, cy - arch * w * .5 - tilt * w * .1), (xo, yo)], th * .55, th, w2=th * .3)


# ------------------------------------------------------------------ gloves and shoes
def sausage(pts, w):
    """A stroke part for union(): a round-ended sausage of width w along pts."""
    return ('s', smooth(pts, False), w)


def glove(pose='open', fill=WHITE, cuff=True, lines=True):
    """A white four-fingered glove in local coordinates: wrist at (0,0), the hand points along +y (down), the thumb is
    on the +x side. Poses: 'open' (palm out, fingers spread), 'wave' (fanned wider), 'fist', 'point' (index out),
    'rest' (fingers together, a little curled), 'hold' (curled round a handle)."""
    parts, inner = [], ''
    if pose in ('open', 'wave'):
        sp = 1.0 if pose == 'open' else 1.5
        parts.append(smooth([(-13, 4), (0, 2), (13, 4), (16, 18), (12, 30), (0, 33), (-12, 30), (-16, 18)]))
        for x0, ang, ln in ((-9, -14, 17), (0, 0, 19), (9, 14, 17)):
            a = math.radians(ang * sp)
            parts.append(sausage([(x0, 24), (x0 + math.sin(a) * ln, 24 + math.cos(a) * ln)], 11.5))
        parts.append(sausage([(11, 14), (19, 17), (25, 13 - 4 * (sp - 1))], 11))
        if lines:
            inner = ''.join(line([(x, 8), (x * 1.05, 17)], 1.7) for x in (-5, 0, 5))
    elif pose in ('fist', 'hold', 'point'):
        parts.append(smooth([(-14, 3), (0, 1), (14, 3), (18, 16), (17, 30), (6, 36), (-8, 36), (-17, 30), (-19, 16)]))
        if pose == 'point':
            parts.append(sausage([(-8, 28), (-9, 44), (-8, 54)], 11))
        parts.append(sausage([(13, 12), (19, 21), (10, 27)], 10.5))
        k = ([(-14, 30), (-9, 34)], [(-6, 32), (0, 35)], [(2, 32), (8, 34)]) if pose != 'point' else ([(-1, 32), (5, 34)],)
        inner = ''.join(line([(p[0][0], p[0][1] - 6), p[0], p[1]], 1.8) for p in k)
        if pose == 'hold':
            inner += line([(-15, 20), (-4, 22), (8, 20)], 1.8)
    elif pose == 'rest':
        parts.append(smooth([(-13, 4), (0, 2), (13, 4), (15, 18), (12, 28), (-12, 28), (-15, 18)]))
        for x0, dx in ((-8, -1), (0, 0), (8, 1)):
            parts.append(sausage([(x0, 24), (x0 + dx, 36), (x0 + dx * 2 - 2, 44)], 11))
        parts.append(sausage([(11, 12), (18, 20), (17, 29)], 10.5))
        inner = line([(-4, 30), (-4, 40)], 1.6) + line([(4, 30), (4, 40)], 1.6)
    out = union(parts, fill, LW, inner)
    if cuff:
        out += blob([(-13, -9), (0, -10), (13, -9), (17, -2), (16, 5), (0, 7), (-16, 5), (-17, -2)], fill, LW, k=.9)
        out += line([(-13, -1), (0, 0), (13, -1)], 1.5)
    return out


def shoe(fill, sole=None, w=1.0, view='side'):
    """A big round shoe: ankle at (0,0); side view toe to +x, front view toe toward us. Sole under it."""
    sole = sole or INK
    if view == 'front':
        sl = P(smooth([(-26, 16), (0, 20), (26, 16), (27, 22), (0, 27), (-27, 22)]), sole, INK, LW * .8)
        body = blob([(-8, -6), (8, -6), (22, 0), (27, 12), (18, 21), (0, 23), (-18, 21), (-27, 12), (-22, 0)], fill, LW)
        hl = line([(-12, 4), (-4, 1)], 2.6, '#ffffff', extra='opacity=".6"')
        return g(sl + body + hl, 0, 0, w)
    sl = P(smooth([(-20, 17), (10, 20), (44, 16), (50, 12), (51, 19), (40, 26), (5, 27), (-20, 25), (-24, 20)]), sole, INK, LW * .8)
    body = blob([(-10, -6), (6, -6), (16, -4), (34, -6), (49, 2), (51, 13), (40, 20), (10, 21), (-16, 20), (-22, 10), (-18, 0)], fill, LW)
    hl = line([(28, -1), (40, 3)], 2.6, '#ffffff', extra='opacity=".6"')
    tongue = line([(-6, -5), (2, 4), (10, -4)], 1.8)
    return g(sl + body + hl + tongue, 0, 0, w)


def shadow(cx, cy, rx, ry=None):
    ry = ry or rx * .12
    return ellipse(cx, cy, rx, ry, INK, 0, extra='opacity=".22"')


# ------------------------------------------------------------------ the film look
def defs(seed=3):
    """Filters: ink wobble (hand-inked line), grain, vignette."""
    return f'''<defs>
<filter id="wob" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="{seed}"/>
<feDisplacementMap in="SourceGraphic" scale="2.4" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="{seed + 7}" result="n"/>
<feColorMatrix type="matrix" values="0 0 0 0 .1  0 0 0 0 .08  0 0 0 0 .05  0 0 0 -1.4 .95"/></filter>
<filter id="bw"><feColorMatrix type="matrix" values=".30 .55 .15 0 0  .30 .55 .15 0 0  .30 .55 .15 0 0  0 0 0 1 0"/>
<feComponentTransfer><feFuncR type="gamma" amplitude="1.12" exponent=".8" offset="-.04"/><feFuncG type="gamma" amplitude="1.12" exponent=".8" offset="-.04"/><feFuncB type="gamma" amplitude="1.1" exponent=".8" offset="-.04"/></feComponentTransfer></filter>
<radialGradient id="vig" cx="50%" cy="48%" r="72%"><stop offset="55%" stop-color="#2a1d10" stop-opacity="0"/><stop offset="100%" stop-color="#2a1d10" stop-opacity=".42"/></radialGradient>
<radialGradient id="vigbw" cx="50%" cy="48%" r="70%"><stop offset="50%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".62"/></radialGradient>
</defs>'''


def svg(w, h, body, bg=PAPER, film=True, bw=False, seed=3):
    """A finished sheet: background, the drawing with ink wobble, grain and vignette on top.
    bw=True: black-and-white film (desaturated, harder, darker corners)."""
    grain = (f'<rect width="{w}" height="{h}" filter="url(#grain)" opacity="{.4 if bw else .2}"/>'
             f'<rect width="{w}" height="{h}" fill="url(#{"vigbw" if bw else "vig"})"/>') if film else ''
    inner = f'<rect width="{w}" height="{h}" fill="{bg}"/><g filter="url(#wob)">{body}</g>{grain}'
    if bw:
        inner = f'<g filter="url(#bw)">{inner}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'{defs(seed)}{inner}</svg>')


def text(x, y, s, size=26, fill=INK, anchor='middle', weight='700', family="Georgia, 'DejaVu Serif', serif", extra=''):
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>')


# ------------------------------------------------------------------ mouths and noses
def mouth(cx, cy, w, kind='smile', fz=1.0, lip=None, skin='#f4d6bd', open_=1.0, side=0):
    """1930s mouths, centred at (cx, cy), w wide. side shifts the far corner for a turned head (-1..1).
    kinds: 'smile' (a curve with cheek ticks), 'grin' (open D with tongue), 'o' (round open — surprise),
    'frown' (∩ with ticks), 'shout' (open, square-ish, tongue), 'lips' (small cupid-bow lips, for women),
    'lips-smile', 'flat' (pressed), 'wobble' (sad wavy line), 'grumpy' (frown hidden under a moustache)."""
    w = w * (.55 + .45 * fz)
    hw = w / 2
    lx, rx = cx - hw, cx + hw
    out = []
    if kind == 'smile':
        out.append(tline([(lx, cy - 3), (cx, cy + w * .22), (rx, cy - 3)], 2.2, 4.5, w2=2.2))
        out.append(line([(lx - 3, cy - 8), (lx + 1, cy - 1)], 2))
        out.append(line([(rx + 3, cy - 8), (rx - 1, cy - 1)], 2))
    elif kind == 'flat':
        out.append(tline([(lx + 4, cy), (cx, cy + 1.5), (rx - 4, cy)], 2, 4, w2=2))
    elif kind == 'frown':
        out.append(tline([(lx, cy + 5), (cx, cy - w * .14), (rx, cy + 5)], 2.2, 4.5, w2=2.2))
    elif kind == 'wobble':
        out.append(tline([(lx, cy + 4), (lx + w * .25, cy - 1), (cx, cy + 2), (rx - w * .25, cy - 1), (rx, cy + 4)], 2, 3.8, w2=2))
    elif kind in ('grin', 'shout', 'o'):
        if kind == 'grin':
            d = smooth([(lx, cy - 4), (cx, cy - 1), (rx, cy - 4), (rx - w * .12, cy + w * .3 * open_), (cx, cy + w * .5 * open_),
                        (lx + w * .12, cy + w * .3 * open_)], True, .9)
        elif kind == 'shout':
            d = smooth([(lx, cy + 2), (cx, cy - w * .12), (rx, cy + 2), (rx - w * .05, cy + w * .45 * open_), (cx, cy + w * .55 * open_),
                        (lx + w * .05, cy + w * .45 * open_)], True, .9)
        else:
            d = smooth([(cx, cy - w * .32), (cx + w * .28, cy), (cx, cy + w * .42), (cx - w * .28, cy)])
        i = uid('m')
        tongue = ellipse(cx + (w * .08 if kind != 'o' else 0), cy + w * (.5 if kind != 'o' else .42) * open_, w * .3, w * .2, TONGUE, 0)
        teeth = ''
        if kind == 'shout':
            teeth = P(f'M {f(lx)} {f(cy - 2)} L {f(rx)} {f(cy - 2)} L {f(rx)} {f(cy + 6)} L {f(lx)} {f(cy + 6)} Z', WHITE, None, 0)
        out.append(f'<clipPath id="{i}"><path d="{d}"/></clipPath>' + P(d, MOUTH, None, 0)
                   + f'<g clip-path="url(#{i})">{tongue}{teeth}</g>' + P(d, 'none', INK, LWI + .4))
        if kind == 'grin':
            out.append(line([(lx - 4, cy - 9), (lx + 1, cy - 3)], 2))
            out.append(line([(rx + 4, cy - 9), (rx - 1, cy - 3)], 2))
    elif kind in ('lips', 'lips-smile', 'lips-o', 'lips-frown'):
        lip = lip or '#c8392f'
        if kind == 'lips-o':
            out.append(ellipse(cx, cy + 2, w * .18, w * .24, lip, LWI))
            out.append(ellipse(cx, cy + 3, w * .08, w * .13, MOUTH, 0))
        else:
            up = {'lips': 0, 'lips-smile': 1, 'lips-frown': -1}[kind]
            d = (f'M {f(lx)} {f(cy - up * 3)} C {f(cx - hw * .6)} {f(cy - 5)} {f(cx - hw * .25)} {f(cy - 7)} {f(cx)} {f(cy - 3)} '
                 f'C {f(cx + hw * .25)} {f(cy - 7)} {f(cx + hw * .6)} {f(cy - 5)} {f(rx)} {f(cy - up * 3)} '
                 f'C {f(cx + hw * .5)} {f(cy + 7 + up)} {f(cx - hw * .5)} {f(cy + 7 + up)} {f(lx)} {f(cy - up * 3)} Z')
            out.append(P(d, lip, INK, LWI))
            out.append(line([(lx + 2, cy - up * 2), (cx, cy + 1 + up), (rx - 2, cy - up * 2)], 1.6))
            if up > 0:
                out.append(line([(lx - 3, cy - 7), (lx, cy - 3)], 1.8))
                out.append(line([(rx + 3, cy - 7), (rx, cy - 3)], 1.8))
    return ''.join(out)


def nose(cx, cy, r, fill, kind='button', fz=1.0, dirx=0):
    """'button': a small ball (with a shine); 'bulb': an old man's big round nose; 'pointed': a sharper bead."""
    out = []
    if kind == 'pointed':
        out.append(blob([(cx - r * .7, cy + r * .5), (cx + dirx * r * .6, cy - r * 1.4), (cx + r * .7, cy + r * .5),
                         (cx + dirx * r * .3, cy + r * .9)], fill, LWI + .3))
    else:
        out.append(ellipse(cx, cy, r * (1.0 if kind == 'bulb' else .95), r * (.9 if kind == 'bulb' else .85), fill, LWI + .4))
    out.append(ellipse(cx - r * .35 + dirx * r * .2, cy - r * .35, r * .28, r * .18, '#ffffff', 0, extra='opacity=".7"'))
    return ''.join(out)


def cheek(cx, cy, r, col=CHEEK, op=.55):
    return ellipse(cx, cy, r, r * .8, col, 0, extra=f'opacity="{op}"')


def arm(pts, w, fill, pose='open', gs=1.0, flip=False, gfill=WHITE, sleeve=None, w1=None, w2=None):
    """A hose arm along pts ending in a glove that follows the arm's last direction.
    flip mirrors the glove (thumb to the other side). w1, w2: the hose's width in the middle and at the wrist (a thick
    forearm). sleeve: (fill, t[, extra width]) — a rolled-up sleeve over the first t (0..1) of the arm, ending in a
    cuff roll."""
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    rot = -math.degrees(math.atan2(x2 - x1, y2 - y1))
    out = hose(pts, w, fill, w1, w2)
    if sleeve:
        sfill, t = sleeve[0], sleeve[1]
        extra = sleeve[2] if len(sleeve) > 2 else 5
        s = sample(pts, 10)
        n = max(2, int(round((len(s) - 1) * t)))
        part = s[:n + 1]
        wm = w if w1 is None else w1
        we = w + (wm - w) * min(t / .5, 1)
        out += hose(part, w + extra, sfill, (w + we) / 2 + extra, we + extra)
        (ax, ay), (bx, by) = part[-2], part[-1]
        L = math.hypot(bx - ax, by - ay) or 1
        ux, uy = (bx - ax) / L, (by - ay) / L
        out += hose([(bx - ux * 5, by - uy * 5), (bx + ux * 5, by + uy * 5)], we + extra + 7, sfill)
    return out + g(glove(pose, gfill), x2, y2, gs, rot, flip)


def leg(pts, w0, w1, w2, fill, shoe_fill, sole=None, ss=1.0, toe=1, view='side', sock=None):
    """A hose leg from hip to ankle, tapering w0 → w1 → w2, standing in a big shoe (toe=+1 right, -1 left)."""
    out = hose(pts, w0, fill, w1, w2)
    x, y = pts[-1]
    return out + g(shoe(shoe_fill, sole, view=view), x, y - 2, ss, flip=(toe < 0))
