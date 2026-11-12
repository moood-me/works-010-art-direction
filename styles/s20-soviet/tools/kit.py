"""С20 «Советская мультипликация 60–70-х» — the shared kit: line, paint, paper.

How a thing is drawn here (the style's rules in code):
  * An INK LINE drawn by hand with a pen or a brush: one confident curve, a little wobble, heavier where the form
    turns away from the light (down-right), thin at the ends, and free to stop short — the line does not have to
    close (`gap`).
  * PAINT laid under it OFF REGISTER: the colour patch is shifted from the line by a few pixels and its edge is not
    the line's edge (`OFF`), the way the 1960s Soyuzmultfilm cels and prints look. Paint has a texture: `brush`
    (gouache streaks), `crayon` (dry crayon on rough paper: the paper shows through), `flat` (none).
  * Faces and hands are mostly the PAPER itself (unpainted), with a crayon blush on the cheeks.
  * Pencil HATCHING (`hatch`) for a shaded side or a texture of cloth, clipped to the shape.

Everything is built from control points in local units (a character's figure: feet at y = 0, up is negative y).
A drawing is a list of SVG strings. `scaled(s)` sets the scale the next drawing will be placed at, so that line
width, off-register shift and the grain of the textures look the same on a portrait and on a full figure.
"""
import math, random, contextlib

INK = '#1c1512'
PAPER = '#f6eedd'
SKIN = '#fbf4e6'          # the face is paper, a touch warmer
BLUSH = '#e0574a'

# ------------------------------------------------------------------ context: scale of the next drawing
_S = [1.0]
_SEED = [1]


@contextlib.contextmanager
def scaled(s, seed=None):
    _S.append(s)
    old = _SEED[0]
    if seed is not None:
        _SEED[0] = seed
    try:
        yield
    finally:
        _S.pop()
        _SEED[0] = old


def S():
    return _S[-1]


def LWF():
    """Line-width factor in local units: a close-up gets a somewhat heavier line on screen, not s times heavier."""
    return S() ** -0.45


def OFF():
    k = 2.6 / S() ** 0.55
    return (k, -0.7 * k)


def rng():
    _SEED[0] += 1
    return random.Random(_SEED[0] * 7919 + 13)


def SK():
    return ('%.2f' % S()).replace('.', '_')


USED = set()          # filter variants used: (kind, scale-key)


def filt(kind):
    USED.add((kind, SK(), S()))
    return 'url(#%s-%s)' % (kind, SK())


# ------------------------------------------------------------------ geometry
def cr(pts, closed=False, n=6):
    """Catmull-Rom through the control points; returns dense points."""
    P = list(pts)
    if len(P) < 2:
        return P
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        seg = max(2, int(n * max(1.0, math.dist(p1, p2) / 18)))
        for k in range(seg):
            t = k / seg
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(P[-2])
    return out


def ell(cx, cy, rx, ry, n=10, rot=0, start=0):
    c, s = math.cos(rot), math.sin(rot)
    pts = []
    for i in range(n):
        a = start + 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def arc(cx, cy, rx, ry, a0, a1, n=8):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / (n - 1)), cy + ry * math.sin(a0 + (a1 - a0) * i / (n - 1)))
            for i in range(n)]


def move(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


def scale_pts(pts, sx, sy=None, ox=0, oy=0):
    sy = sx if sy is None else sy
    return [(ox + (x - ox) * sx, oy + (y - oy) * sy) for x, y in pts]


def rot_pts(pts, a, ox=0, oy=0):
    c, s = math.cos(a), math.sin(a)
    return [(ox + (x - ox) * c - (y - oy) * s, oy + (x - ox) * s + (y - oy) * c) for x, y in pts]


def mirror_pts(pts, ox=0):
    return [(2 * ox - x, y) for x, y in pts][::-1]


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def area(pts):
    return 0.5 * sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                     for i in range(len(pts)))


def d_of(pts, closed=True):
    s = 'M%.1f %.1f' % pts[0] + ''.join('L%.1f %.1f' % p for p in pts[1:])
    return s + ('Z' if closed else '')


# ------------------------------------------------------------------ the ink line
LIGHT_N = (0.55, 0.83)    # a contour whose outward normal looks this way (down-right) gets heavier


def _wobble(n, total, amp, r):
    ph = [r.uniform(0, 6.28) for _ in range(3)]
    lam = [55, 23, 140]
    out = []
    for i in range(n):
        s = total * i / max(1, n - 1)
        out.append(amp * (0.55 * math.sin(6.283 * s / lam[0] + ph[0]) + 0.3 * math.sin(6.283 * s / lam[1] + ph[1]) +
                          0.4 * math.sin(6.283 * s / lam[2] + ph[2])))
    return out


def ink(pts, lw=2.2, closed=False, taper=0.22, weight=0.55, wob=0.45, smooth=True, gap=None, color=INK,
        op=1.0, press=None):
    """A hand-drawn line through control points, as a filled outline.
    lw: base width (before the scale factor); taper: share of the length that thins at each open end;
    weight: how much heavier the line is where it faces down-right; gap: (t0, t1) of a closed line left undrawn;
    press: optional list of multipliers along the line (interpolated)."""
    r = rng()
    P = cr(pts, closed) if smooth else list(pts)
    if closed and smooth is False:
        P = P + [P[0]]
    if len(P) < 2:
        return ''
    lw = lw * LWF()
    CX = sum(p[0] for p in P) / len(P)
    CY = sum(p[1] for p in P) / len(P)
    L = [0.0]
    for i in range(1, len(P)):
        L.append(L[-1] + math.dist(P[i - 1], P[i]))
    total = L[-1] or 1
    wob_v = _wobble(len(P), total, wob * LWF() * 1.4, r)
    left, right = [], []
    segs = []
    if closed and gap:
        t0, t1 = gap
        keep = [i for i in range(len(P)) if not (t0 <= L[i] / total <= t1)]
        # rotate so the kept run is contiguous
        if t0 > 0 and t1 < 1:
            idx = [i for i in range(len(P)) if L[i] / total > t1] + [i for i in range(len(P)) if L[i] / total < t0]
        else:
            idx = keep
        segs = [idx]
        closed_draw = False
    else:
        segs = [list(range(len(P)))]
        closed_draw = closed
    out = []
    for idx in segs:
        if len(idx) < 2:
            continue
        sub = [P[i] for i in idx]
        Ls = [0.0]
        for i in range(1, len(sub)):
            Ls.append(Ls[-1] + math.dist(sub[i - 1], sub[i]))
        tot = Ls[-1] or 1
        left, right = [], []
        for k, i in enumerate(idx):
            a = sub[max(0, k - 1)] if not closed_draw else sub[(k - 1) % len(sub)]
            b = sub[min(len(sub) - 1, k + 1)] if not closed_draw else sub[(k + 1) % len(sub)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / ln, dx / ln
            t = Ls[k] / tot
            w = lw
            if not closed_draw:
                e = min(t, 1 - t)
                if taper > 0 and e < taper:
                    w *= 0.25 + 0.75 * math.sin(0.5 * math.pi * e / taper)
            # heavier on the shadow side
            if closed:
                vx, vy = sub[k][0] - CX, sub[k][1] - CY
                on = (nx, ny) if vx * nx + vy * ny > 0 else (-nx, -ny)
                facing = max(0.0, on[0] * LIGHT_N[0] + on[1] * LIGHT_N[1])
            else:
                facing = 0.35
            w *= 1 + weight * facing
            if press:
                f = t * (len(press) - 1)
                j = min(int(f), len(press) - 2)
                w *= press[j] + (press[j + 1] - press[j]) * (f - j)
            o = wob_v[i]
            cx, cy = sub[k][0] + nx * o, sub[k][1] + ny * o
            left.append((cx + nx * w / 2, cy + ny * w / 2))
            right.append((cx - nx * w / 2, cy - ny * w / 2))
        if closed_draw:
            out.append('<path d="%s %s" fill="%s" fill-rule="evenodd"%s/>' % (
                d_of(left), d_of(right), color, '' if op == 1 else ' opacity="%.2f"' % op))
        else:
            poly = left + right[::-1]
            out.append('<path d="%s" fill="%s"%s/>' % (d_of(poly), color, '' if op == 1 else ' opacity="%.2f"' % op))
    return ''.join(out)


def dot(x, y, r, color=INK):
    r = r * LWF() ** 0.3
    return '<ellipse cx="%.1f" cy="%.1f" rx="%.2f" ry="%.2f" fill="%s"/>' % (x, y, r, r * 1.08, color)


# ------------------------------------------------------------------ paint
_CLIP = [0]


def paint(pts, color, tex='brush', off=True, smooth=True, op=1.0, closed=True):
    """A patch of paint under the line, off register, with a texture."""
    P = cr(pts, True) if smooth else list(pts)
    dx, dy = OFF() if off else (0, 0)
    f = '' if tex == 'flat' else ' filter="%s"' % filt(tex)
    return '<path d="%s" fill="%s" transform="translate(%.1f %.1f)"%s%s/>' % (
        d_of(P), color, dx, dy, f, '' if op == 1 else ' opacity="%.2f"' % op)


def form(pts, color=None, lw=2.2, tex='brush', gap=None, line=True, off=True, weight=0.55, wob=0.45, op=1.0,
         smooth=True):
    """The usual thing: paint (if a colour) + a closed ink line over it."""
    s = ''
    if color:
        s += paint(pts, color, tex, off, op=op, smooth=smooth)
    if line:
        s += ink(pts, lw, closed=True, gap=gap, weight=weight, wob=wob, smooth=smooth)
    return s


def hatch(pts, color=INK, angle=-0.9, step=5.0, lw=0.8, op=0.55, jitter=0.25, smooth=True):
    """Pencil hatching clipped to a shape."""
    r = rng()
    _CLIP[0] += 1
    cid = 'hc%d_%d' % (_CLIP[0], r.randint(0, 99999))
    P = cr(pts, True) if smooth else list(pts)
    xs = [p[0] for p in P]
    ys = [p[1] for p in P]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    R = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 4
    c, s = math.cos(angle), math.sin(angle)
    step = step * LWF() ** 0.6
    lines = []
    k = -R
    while k < R:
        a = (cx + c * -R - s * k, cy + s * -R + c * k)
        b = (cx + c * R - s * k, cy + s * R + c * k)
        j1, j2 = r.uniform(-jitter, jitter) * R * 0.3, r.uniform(-jitter, jitter) * R * 0.3
        a = (a[0] + c * j1, a[1] + s * j1)
        b = (b[0] + c * j2, b[1] + s * j2)
        lines.append('M%.1f %.1fL%.1f %.1f' % (a + b))
        k += step * r.uniform(0.8, 1.25)
    return ('<clipPath id="%s"><path d="%s"/></clipPath><path d="%s" stroke="%s" stroke-width="%.2f" fill="none" '
            'stroke-linecap="round" opacity="%.2f" clip-path="url(#%s)" filter="%s"/>') % (
        cid, d_of(P), ''.join(lines), color, lw * LWF(), op, cid, filt('pencil'))


def blush(x, y, rx, ry=None, color=BLUSH, op=0.85):
    """A crayon blush on the cheek: a rubbed patch, the paper showing through."""
    ry = ry or rx * 0.8
    return '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity="%.2f" filter="%s"/>' % (
        x, y, rx, ry, color, op, filt('rub'))


def group(items, tx=0, ty=0, s=1.0, extra=''):
    body = ''.join(i for i in items if i)
    return '<g transform="translate(%.1f %.1f) scale(%.4f)"%s>%s</g>' % (tx, ty, s, extra, body)


def flip(items, ox=0):
    """Mirror a drawing horizontally around x = ox (whole SVG group)."""
    return '<g transform="translate(%.1f 0) scale(-1 1)">%s</g>' % (2 * ox, ''.join(items))


# ------------------------------------------------------------------ filters
def _filters():
    out = []
    for kind, sk, s in sorted(USED):
        f = lambda v: v / s    # frequency in local units → same grain on screen
        g = lambda v: v * 1.0 / s
        if kind == 'brush':
            out.append('''<filter id="brush-%s" x="-5%%" y="-5%%" width="110%%" height="110%%">
<feTurbulence type="fractalNoise" baseFrequency="%.4f" numOctaves="2" seed="3" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="%.2f" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency="%.4f %.4f" numOctaves="2" seed="8" result="t"/>
<feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.6 1.45" result="tm"/>
<feComposite in="tm" in2="d" operator="in" result="streak"/>
<feComponentTransfer in="streak" result="st"><feFuncA type="linear" slope="0.20"/></feComponentTransfer>
<feTurbulence type="fractalNoise" baseFrequency="%.4f" numOctaves="1" seed="5" result="sp"/>
<feColorMatrix in="sp" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -3 1.55" result="spm"/>
<feComposite in="spm" in2="d" operator="in" result="spec"/>
<feComponentTransfer in="spec" result="sp2"><feFuncA type="linear" slope="0.07"/></feComponentTransfer>
<feMerge><feMergeNode in="d"/><feMergeNode in="st"/></feMerge></filter>''' % (
                sk, f(0.035), g(3.2), f(0.006), f(0.045), f(0.6)))
        elif kind == 'crayon':
            out.append('''<filter id="crayon-%s" x="-5%%" y="-5%%" width="110%%" height="110%%">
<feTurbulence type="fractalNoise" baseFrequency="%.4f" numOctaves="2" seed="4" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="%.2f" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency="%.4f %.4f" numOctaves="2" seed="11" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 4.5 -1.55" result="gm"/>
<feComposite in="d" in2="gm" operator="in"/></filter>''' % (sk, f(0.04), g(3.0), f(0.55), f(0.9)))
        elif kind == 'rub':
            out.append('''<filter id="rub-%s" x="-30%%" y="-30%%" width="160%%" height="160%%">
<feGaussianBlur in="SourceGraphic" stdDeviation="%.2f" result="b"/>
<feTurbulence type="fractalNoise" baseFrequency="%.4f" numOctaves="2" seed="21" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 4 -1.4" result="gm"/>
<feComposite in="b" in2="gm" operator="in"/></filter>''' % (sk, g(1.6), f(0.5)))
        elif kind == 'pencil':
            out.append('''<filter id="pencil-%s" x="-5%%" y="-5%%" width="110%%" height="110%%">
<feTurbulence type="fractalNoise" baseFrequency="%.4f" numOctaves="2" seed="31" result="g"/>
<feDisplacementMap in="SourceGraphic" in2="g" scale="%.2f" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 3 -0.9" result="gm"/>
<feComposite in="d" in2="gm" operator="in"/></filter>''' % (sk, f(0.7), g(1.4)))
        elif kind == 'drybrush':
            out.append('''<filter id="drybrush-%s" x="-10%%" y="-10%%" width="120%%" height="120%%">
<feTurbulence type="fractalNoise" baseFrequency="%.4f" numOctaves="2" seed="6" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="%.2f" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency="%.4f %.4f" numOctaves="3" seed="9" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 5 -1.9" result="gm"/>
<feComposite in="d" in2="gm" operator="in"/></filter>''' % (sk, f(0.05), g(10), f(0.02), f(0.35)))
    return ''.join(out)


PAPER_FILTER = '''<filter id="paper" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="2" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.28  0 0 0 0 0.18  0 0 0 -1.3 0.75"/>
</filter>
<filter id="fibre" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.008 0.011" numOctaves="3" seed="12" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.36  0 0 0 0 0.22  0 0 0 -1.4 0.82"/>
</filter>'''


class Doc:
    def __init__(self, w, h, bg=PAPER):
        self.w, self.h, self.bg = w, h, bg
        self.items = []

    def add(self, *items):
        self.items.extend(i for i in items if i)

    def svg(self, grain=True):
        g = ''
        if grain:
            g = ('<rect width="%d" height="%d" filter="url(#paper)" opacity="0.32" style="mix-blend-mode:multiply"/>'
                 '<rect width="%d" height="%d" filter="url(#fibre)" opacity="0.16" style="mix-blend-mode:multiply"/>'
                 ) % (self.w, self.h, self.w, self.h)
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
                '<defs>%s%s</defs><rect width="%d" height="%d" fill="%s"/>%s%s</svg>') % (
            self.w, self.h, self.w, self.h, PAPER_FILTER, _filters(), self.w, self.h, self.bg,
            ''.join(self.items), g)

    def save(self, path, grain=True):
        with open(path, 'w') as f:
            f.write(self.svg(grain))


def text(x, y, s, size=22, color=INK, anchor='middle', italic=False):
    st = 'font-style:italic;' if italic else ''
    return ('<text x="%.1f" y="%.1f" font-family="\'PT Serif\',\'DejaVu Serif\',Georgia,serif" font-size="%.1f" '
            'fill="%s" text-anchor="%s" style="%s">%s</text>') % (x, y, size, color, anchor, st, s)
