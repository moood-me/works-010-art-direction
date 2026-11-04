"""Pen and watercolour in SVG: a living ink line and loose washes on white paper.

Shared by every character. Nothing here knows about a particular person.

- Doc: one picture. Holds a transform stack (so a head drawn in its own units can be placed, scaled, turned or
  mirrored), and three layers: washes (multiplied, like glazes), ink (multiplied), paper.
- ink(): a pen stroke — a centre line through hand-placed points, given width that swells and tapers, a slow wobble
  and a fine tremor, sometimes skipping like a dry nib.
- hatch(): loose parallel pen strokes inside a shape (shadow, texture) — shorter than the shape, never ruled.
- wash(): a watercolour patch — a soft irregular shape, its edge pushed about by noise, pigment uneven inside,
  darker where it dried at the rim, grainy; placed a little off the line, as a painter's wash is.
"""
import math, os, random, subprocess

INK = '#211c19'
PAPER = '#fdfaf3'


# ---------- geometry ----------

def catmull(pts, closed=False, step=2.0):
    """Dense points along a Catmull-Rom spline through pts."""
    if len(pts) < 2:
        return list(pts)
    P = list(pts)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [(2 * P[0][0] - P[1][0], 2 * P[0][1] - P[1][1])] + P + [(2 * P[-1][0] - P[-2][0], 2 * P[-1][1] - P[-2][1])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(2, int(math.dist(p1, p2) / step))
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(P[-2])
    return out


class Noise1:
    """Smooth 1-D value noise."""
    def __init__(self, rnd, period):
        self.r = [rnd.uniform(-1, 1) for _ in range(512)]
        self.p = period

    def __call__(self, s):
        x = s / self.p
        i = int(math.floor(x))
        f = x - i
        f = f * f * (3 - 2 * f)
        return self.r[i % 512] * (1 - f) + self.r[(i + 1) % 512] * f


def inside(pt, poly):
    x, y = pt
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            c = not c
        j = i
    return c


def fmt(pts):
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)


# ---------- the document ----------

class Doc:
    def __init__(self, w, h, seed=1, paper=PAPER):
        self.w, self.h = w, h
        self.rnd = random.Random(seed)
        self.paper = paper
        self.washes, self.whites, self.inks = [], [], []
        self.T = [(1, 0, 0, 1, 0, 0)]      # affine stack: x' = a x + c y + e ; y' = b x + d y + f
        self.lw = 1.0                       # line width multiplier (for small figures)
        self.fade = None                    # (y0, y1): washes thin out from y0 to y1, as a vignette on a page

    # transforms
    def push(self, dx=0, dy=0, s=1.0, rot=0.0, flip=False):
        a, b, c, d, e, f = self.T[-1]
        cs, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        sx = -s if flip else s
        # local matrix M = T(dx,dy) R(rot) S(sx,s)
        m = (cs * sx, sn * sx, -sn * s, cs * s, dx, dy)
        self.T.append((a * m[0] + c * m[1], b * m[0] + d * m[1], a * m[2] + c * m[3], b * m[2] + d * m[3],
                       a * m[4] + c * m[5] + e, b * m[4] + d * m[5] + f))

    def pop(self):
        self.T.pop()

    def turn(self, cx, cy, rot):
        """Turn what follows about (cx, cy) by rot degrees (a lean of the body); undo with two pops."""
        self.push(cx, cy, 1, rot)
        self.push(-cx, -cy)

    def tp(self, pts):
        a, b, c, d, e, f = self.T[-1]
        return [(a * x + c * y + e, b * x + d * y + f) for x, y in pts]

    # output
    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">'
                f'<defs>{DEFS}</defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="{self.paper}"/>'
                f'<rect width="{self.w}" height="{self.h}" filter="url(#paper)" opacity="0.5"/>'
                f'{self._fade_defs()}'
                f'<g style="mix-blend-mode:multiply"{self._fade_attr()}>{"".join(self.washes)}</g>'
                f'<g fill="{self.paper}" filter="url(#wcS0)">{"".join(self.whites)}</g>'
                f'<g style="mix-blend-mode:multiply" fill="{INK}" filter="url(#nib)">{"".join(self.inks)}</g>'
                '</svg>')

    def _fade_defs(self):
        if not self.fade:
            return ''
        y0, y1 = self.fade
        return (f'<defs><linearGradient id="fadeg" gradientUnits="userSpaceOnUse" x1="0" y1="{y0}" x2="0" y2="{y1}">'
                f'<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
                f'<filter id="fadef"><feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" seed="4"/>'
                f'<feDisplacementMap in="SourceGraphic" scale="60" xChannelSelector="R" yChannelSelector="G"/></filter>'
                f'<mask id="fadem" maskUnits="userSpaceOnUse" x="0" y="0" width="{self.w}" height="{self.h}">'
                f'<rect x="-50" y="-50" width="{self.w + 100}" height="{self.h + 100}" fill="url(#fadeg)" filter="url(#fadef)"/></mask></defs>')

    def _fade_attr(self):
        return ' mask="url(#fadem)"' if self.fade else ''

    def save(self, path):
        with open(path, 'w') as f:
            f.write(self.svg())


# ---------- pen ----------

def ink(d, pts, w=2.0, closed=False, taper=(0.18, 0.35), jit=0.9, press=0.5, skip=0.0, seed=None,
        color=None, alpha=0.93, start=1.0, end=1.0, retrace=0.3):
    """A pen stroke through pts (local coordinates). w is the full width at its heaviest, in output pixels
    (times d.lw). taper: fraction of length over which each end thins. start/end: width factor at the ends
    (a pen put down hard starts at 1; a flick ends near 0). skip: chance per 40 px that the dry nib skips."""
    rnd = random.Random(seed) if seed is not None else d.rnd
    P = d.tp(pts)
    C = catmull(P, closed, 1.6)
    if len(C) < 3:
        return
    L = [0.0]
    for i in range(1, len(C)):
        L.append(L[-1] + math.dist(C[i - 1], C[i]))
    tot = L[-1] or 1
    nlo, nhi, nw = Noise1(rnd, 40), Noise1(rnd, 6), Noise1(rnd, 13)
    nsk = Noise1(rnd, 40)
    W = w * d.lw
    left, right, pieces = [], [], []
    for i, (x, y) in enumerate(C):
        j0, j1 = max(0, i - 1), min(len(C) - 1, i + 1)
        tx, ty = C[j1][0] - C[j0][0], C[j1][1] - C[j0][1]
        n = math.hypot(tx, ty) or 1
        nx, ny = -ty / n, tx / n
        s = L[i]; t = s / tot
        off = jit * nlo(s) + 0.35 * nhi(s)
        a0, a1 = taper
        prof = 1.0
        if not closed:
            if t < a0:
                u = t / a0; prof = start + (1 - start) * (u * u * (3 - 2 * u)) if start < 1 else 0.55 + 0.45 * u
            elif t > 1 - a1:
                u = (1 - t) / a1; prof = end + (1 - end) * (u * u * (3 - 2 * u))
        ww = max(0.3, W * prof * max(0.25, 1 + press * 1.3 * nw(s))) / 2
        cx, cy = x + nx * off, y + ny * off
        gap = skip > 0 and nsk(s) > 1 - 2 * skip
        if gap:
            if left:
                pieces.append((left, right)); left, right = [], []
            continue
        left.append((cx + nx * ww, cy + ny * ww))
        right.append((cx - nx * ww, cy - ny * ww))
    if left:
        pieces.append((left, right))
    # the pen goes back over part of the line, a hair off: the scratchy double line of a dip pen
    if retrace and len(C) > 20 and rnd.random() < retrace and w > 0.9:
        a = rnd.uniform(0.0, 0.5); b = min(1.0, a + rnd.uniform(0.25, 0.5))
        sub = C[int(a * len(C)):int(b * len(C))]
        if len(sub) > 6:
            o = rnd.choice((-1, 1)) * rnd.uniform(1.2, 2.4) * d.lw
            k = max(1, len(sub) // 5)
            pts2 = []
            for i in range(0, len(sub), k):
                j0, j1 = max(0, i - 1), min(len(sub) - 1, i + 1)
                tx, ty = sub[j1][0] - sub[j0][0], sub[j1][1] - sub[j0][1]
                n = math.hypot(tx, ty) or 1
                pts2.append((sub[i][0] - ty / n * o, sub[i][1] + tx / n * o))
            T = d.T; d.T = [(1, 0, 0, 1, 0, 0)]
            ink(d, pts2, w=w * 0.45 / d.lw, jit=jit * 0.5, press=press, start=0.2, end=0.1, retrace=0,
                seed=rnd.randint(0, 1 << 30), alpha=alpha * 0.85)
            d.T = T
    style = f' fill="{color}"' if color else ''
    for lft, rgt in pieces:
        if len(lft) < 2:
            continue
        if closed and len(pieces) == 1:
            d.inks.append(f'<path d="M{fmt(lft)}Z M{fmt(rgt[::-1])}Z" fill-rule="evenodd" opacity="{alpha}"{style}/>')
        else:
            d.inks.append(f'<polygon points="{fmt(lft + rgt[::-1])}" opacity="{alpha}"{style}/>')


def dot(d, x, y, r=2.2, seed=None):
    """An ink dot (an eye, a freckle): a tiny irregular blob."""
    rnd = random.Random(seed) if seed is not None else d.rnd
    pts = []
    for i in range(9):
        a = i / 9 * 2 * math.pi
        rr = r * (1 + rnd.uniform(-0.18, 0.18))
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a) * 0.95))
    P = catmull(d.tp(pts), True, 1.0)
    d.inks.append(f'<polygon points="{fmt(P)}" opacity="0.95"/>')


def white(d, x, y, rx, ry, rot=0):
    """Paper left white inside a wash (the white of an eye): a small ellipse in paper colour over the washes."""
    pts = [(x + rx * math.cos(a) * math.cos(math.radians(rot)) - ry * math.sin(a) * math.sin(math.radians(rot)),
            y + rx * math.cos(a) * math.sin(math.radians(rot)) + ry * math.sin(a) * math.cos(math.radians(rot)))
           for a in [i / 12 * 2 * math.pi for i in range(12)]]
    d.whites.append(f'<polygon points="{fmt(catmull(d.tp(pts), True, 1.5))}"/>')


def hatch(d, poly, angle=45, gap=6, w=1.0, fill=0.8, jit=0.4, seed=None, curve=0.0):
    """Loose parallel strokes inside poly (local coords). gap in local units. fill: how much of each span is
    drawn (the pen stops short). curve bows each stroke a little."""
    rnd = random.Random(seed) if seed is not None else d.rnd
    poly = catmull(poly, True, 3)
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    proj_v = [x * vx + y * vy for x, y in poly]
    proj_u = [x * ux + y * uy for x, y in poly]
    v = min(proj_v) + gap * rnd.uniform(0.3, 1)
    while v < max(proj_v):
        segs, cur = [], None
        u = min(proj_u)
        while u <= max(proj_u):
            p = (ux * u + vx * v, uy * u + vy * v)
            if inside(p, poly):
                if cur is None:
                    cur = [u, u]
                cur[1] = u
            elif cur:
                segs.append(cur); cur = None
            u += 1.5
        if cur:
            segs.append(cur)
        for u0, u1 in segs:
            ln = u1 - u0
            if ln < 3:
                continue
            k = fill * rnd.uniform(0.7, 1.0)
            m = u0 + ln * rnd.uniform(0, 1 - k)
            ua, ub = m, m + ln * k
            bow = curve * ln * rnd.uniform(0.5, 1)
            pts = [(ux * ua + vx * v, uy * ua + vy * v),
                   (ux * (ua + ub) / 2 + vx * (v + bow), uy * (ua + ub) / 2 + vy * (v + bow)),
                   (ux * ub + vx * v, uy * ub + vy * v)]
            ink(d, pts, w=w, jit=jit * 0.6, press=0.3, taper=(0.2, 0.5), start=0.6, end=0.15,
                seed=rnd.randint(0, 1 << 30))
        v += gap * rnd.uniform(0.75, 1.25)


# ---------- watercolour ----------

def wash(d, poly, color, opacity=0.62, dx=0, dy=0, closed=True, seed=None, rough=None, angle=None):
    """A watercolour patch. poly: rough outline (local coords), smoothed. dx, dy shift it off the line.
    rough: 'S' (small shapes) or 'L' (big ones), by default from the size on the page.
    angle: the brush direction (degrees on the page) along which the pigment streaks; random by default."""
    rnd = random.Random(seed) if seed is not None else d.rnd
    pts = [(x + dx, y + dy) for x, y in poly]
    P = catmull(d.tp(pts), closed, 3)
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    size = max(max(xs) - min(xs), max(ys) - min(ys))
    if rough is None:
        rough = 'S' if size < 90 else 'L'
    k = rnd.randrange(6)
    if angle is None:
        angle = rnd.uniform(-60, 60)
    # turn the shape by -angle and the element by +angle, so the filter's streaks run along the brush
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    ca, sa = math.cos(math.radians(-angle)), math.sin(math.radians(-angle))
    R = [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in P]
    d.washes.append(f'<polygon points="{fmt(R)}" fill="{color}" fill-opacity="{opacity}" filter="url(#wc{rough}{k})" '
                    f'transform="rotate({angle:.1f} {cx:.1f} {cy:.1f})"/>')


def blot(d, x, y, r, color, opacity=0.4, seed=None):
    """A soft round touch of colour (a cheek)."""
    rnd = random.Random(seed) if seed is not None else d.rnd
    pts = [(x + r * math.cos(a) * rnd.uniform(0.85, 1.1), y + r * math.sin(a) * rnd.uniform(0.75, 1.0))
           for a in [i / 10 * 2 * math.pi for i in range(10)]]
    P = catmull(d.tp(pts), True, 2)
    d.washes.append(f'<polygon points="{fmt(P)}" fill="{color}" fill-opacity="{opacity}" filter="url(#blush)"/>')


def _wc_filter(name, i, freq, scale, erode, blur, dfreq='0.008 0.02', dm=-4.0, db=2.6, rimk=0.8):
    return f'''<filter id="{name}{i}" x="-15%" y="-15%" width="130%" height="130%" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="4" seed="{i * 7 + 3}" result="n1"/>
<feDisplacementMap in="SourceGraphic" in2="n1" scale="{scale}" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feGaussianBlur in="d" stdDeviation="{blur}" result="ds"/>
<feTurbulence type="fractalNoise" baseFrequency="{dfreq}" numOctaves="3" seed="{i * 5 + 21}" result="n2"/>
<feColorMatrix in="n2" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 {dm} {db}" result="dens"/>
<feComposite in="ds" in2="dens" operator="in" result="dd"/>
<feMorphology in="d" operator="erode" radius="{erode}" result="er"/>
<feComposite in="d" in2="er" operator="out" result="rim"/>
<feGaussianBlur in="rim" stdDeviation="0.6" result="rimb"/>
<feComponentTransfer in="rimb" result="rimc"><feFuncA type="linear" slope="{rimk}"/></feComponentTransfer>
<feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="{i + 40}" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.1 1.25" result="ga"/>
<feComposite in="dd" in2="ga" operator="in" result="gr"/>
<feMerge><feMergeNode in="gr"/><feMergeNode in="rimc"/></feMerge>
</filter>'''


DEFS = (''.join(_wc_filter('wcL', i, 0.03, 12, 1.6, 0.2) for i in range(6))
        + ''.join(_wc_filter('wcS', i, 0.06, 6, 1.1, 0.2, '0.016 0.04') for i in range(6))
        + '''<filter id="blush" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="nib" x="-5%" y="-5%" width="110%" height="110%">
<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="1" seed="5" result="t"/>
<feDisplacementMap in="SourceGraphic" in2="t" scale="1.3" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="paper" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="11" result="t"/>
<feColorMatrix in="t" type="matrix" values="0 0 0 0 0.45 0 0 0 0 0.40 0 0 0 0 0.33 0 0 0 -0.35 0.2"/>
<feComposite operator="in" in2="SourceGraphic"/></filter>''')


# ---------- rendering ----------

def render(svg_path, png_path, w, h, scale=1):
    """Render with headless Chrome (SVG filters and blend modes as in a browser)."""
    html = svg_path + '.html'
    with open(html, 'w') as f:
        f.write(f'<html><body style="margin:0;background:{PAPER}"><img src="{os.path.basename(svg_path)}" '
                f'style="width:{w}px;height:{h}px;display:block"></body></html>')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    f'--force-device-scale-factor={scale}', f'--window-size={w},{h}',
                    f'--screenshot={os.path.abspath(png_path)}', 'file://' + os.path.abspath(html)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    os.remove(html)
