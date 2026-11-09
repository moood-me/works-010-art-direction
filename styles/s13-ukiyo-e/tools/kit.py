"""The print's means, shared by every character: the brush line with pressure, flat printed colour, bokashi
(gradation), cloth patterns, paper and wood grain, the sheet with its ground, border, cartouche and seal.

Everything is drawn into a Doc; a character module never writes SVG itself.
Points are (x, y) or (x, y, 'c') — 'c' marks a corner; other points are joined by a smooth curve.
"""
import math
import random
from contextlib import contextmanager

INK = '#211c1c'          # sumi: warm black of the key block
PAPER = '#eee3cb'        # unprinted paper
SKIN = '#f4e7d0'         # a face is paper left almost bare
RED = '#b8402f'          # beni / seal red


def _f(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')


# ---------------------------------------------------------------- curves

def _cr_run(p, n, closed=False):
    """Catmull-Rom through p (a list of (x, y)); n samples per span."""
    m = len(p)
    if m < 3 and not closed:
        if m == 2:
            return [(p[0][0] + (p[1][0] - p[0][0]) * i / n, p[0][1] + (p[1][1] - p[0][1]) * i / n)
                    for i in range(n + 1)]
        return list(p)
    out = []
    spans = m if closed else m - 1
    for i in range(spans):
        if closed:
            p0, p1, p2, p3 = p[(i - 1) % m], p[i], p[(i + 1) % m], p[(i + 2) % m]
        else:
            p1, p2 = p[i], p[i + 1]
            p0 = p[i - 1] if i > 0 else (2 * p1[0] - p2[0], 2 * p1[1] - p2[1])
            p3 = p[i + 2] if i + 2 < m else (2 * p2[0] - p1[0], 2 * p2[1] - p1[1])
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[a] + (-p0[a] + p2[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2
                                    + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3) for a in (0, 1)))
    if not closed:
        out.append((p[-1][0], p[-1][1]))
    return out


def curve(pts, closed=False, n=8):
    """Sample a smooth curve through pts; points tagged 'c' stay corners."""
    xy = [(p[0], p[1]) for p in pts]
    corners = [i for i, p in enumerate(pts) if len(p) > 2 and p[2] == 'c']
    if not corners:
        return _cr_run(xy, n, closed)
    if closed:
        k = corners[0]
        xy = xy[k:] + xy[:k] + [xy[k]]
        corners = [c - k for c in corners] + [len(xy) - 1]
    else:
        corners = sorted(set([0] + corners + [len(xy) - 1]))
    out = []
    for a, b in zip(corners, corners[1:]):
        run = _cr_run(xy[a:b + 1], n)
        out.extend(run if not out else run[1:])
    if closed:
        out.pop()
    return out


def path_d(sm, closed=True):
    return 'M' + 'L'.join(_f(x) + ' ' + _f(y) for x, y in sm) + ('Z' if closed else '')


def lerp_pts(a, b, t):
    """A curve between two sampled curves of any lengths (for hair strands, folds between two edges)."""
    n = max(len(a), len(b))
    out = []
    for i in range(n):
        u = i / (n - 1)
        pa = a[min(len(a) - 1, int(round(u * (len(a) - 1))))]
        pb = b[min(len(b) - 1, int(round(u * (len(b) - 1))))]
        out.append((pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t))
    return out


# ---------------------------------------------------------------- the brush

def _prof(kind, t):
    if callable(kind):
        return kind(t)
    if kind == 'taper':        # a pressed start (nail head), a long tail (rat tail)
        return min(1.0, t / 0.05 + 0.25) * (0.1 + 0.9 * (1 - t) ** 0.9)
    if kind == 'tail':         # the reverse: comes in thin, ends pressed
        return min(1.0, (1 - t) / 0.05 + 0.25) * (0.1 + 0.9 * t ** 0.9)
    if kind == 'swell':        # thin – full – thin
        return 0.12 + 0.88 * math.sin(math.pi * t) ** 0.7
    if kind == 'even':         # the hair line of the key block: even, the ends just pointed
        return min(1.0, t / 0.06 + 0.3, (1 - t) / 0.06 + 0.3)
    if kind == 'press':        # pressed at both ends, lighter in the middle (a fold of cloth)
        return 0.55 + 0.45 * abs(math.cos(math.pi * t)) ** 1.5 * min(1.0, t / 0.03 + 0.4, (1 - t) / 0.03 + 0.2)
    raise ValueError(kind)


def brush_poly(sm, w, prof='swell', nib=0.3, closed=False, seed=0):
    """The outline of a stroke of varying width along the sampled curve sm."""
    rnd = random.Random(seed * 7919 + len(sm))
    n = len(sm)
    seg = [0.0]
    for i in range(1, n):
        seg.append(seg[-1] + math.hypot(sm[i][0] - sm[i - 1][0], sm[i][1] - sm[i - 1][1]))
    total = seg[-1] or 1.0
    ph1, ph2 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    left, right = [], []
    for i in range(n):
        a = sm[(i - 1) % n] if (closed or i > 0) else sm[i]
        b = sm[(i + 1) % n] if (closed or i < n - 1) else sm[i]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        t = seg[i] / total
        ang = math.atan2(dy, dx)
        # the brush is held at a slant: strokes running down-right are full, up-right are light
        k = (1 - nib) + nib * (0.5 + 0.5 * math.cos(2 * (ang - 1.0)))
        # the hand: a slow uneven pressure
        k *= 1 + 0.10 * math.sin(ph1 + seg[i] * 0.045) + 0.06 * math.sin(ph2 + seg[i] * 0.13)
        hw = 0.5 * w * k * (1.0 if closed else _prof(prof, t))
        left.append((sm[i][0] + nx * hw, sm[i][1] + ny * hw))
        right.append((sm[i][0] - nx * hw, sm[i][1] - ny * hw))
    if closed:
        return path_d(left) + path_d(right[::-1])
    return path_d(left + right[::-1])


# ---------------------------------------------------------------- the sheet

class Doc:
    def __init__(self, w, h, seed=1):
        self.w, self.h = w, h
        self.out = []
        self.defs = []
        self._ids = {}
        self.scale = [1.0]
        self.rnd = random.Random(seed)
        self.seed = seed
        self._n = 0
        self.ground_svg = ''
        self.over_svg = ''
        self.margin = 0

    # --- groups
    @contextmanager
    def g(self, x=0, y=0, s=1.0, rot=0, flip=False, clip=None):
        t = 'translate(%s %s)' % (_f(x), _f(y))
        if rot:
            t += ' rotate(%s)' % _f(rot)
        if s != 1.0 or flip:
            t += ' scale(%s %s)' % (_f(-s if flip else s), _f(s))
        self.out.append('<g transform="%s"%s>' % (t, ' clip-path="url(#%s)"' % clip if clip else ''))
        self.scale.append(self.scale[-1] * s)
        try:
            yield
        finally:
            self.scale.pop()
            self.out.append('</g>')

    @property
    def lw(self):
        """Lines keep some of their weight when a figure is drawn small."""
        return (1.0 / self.scale[-1]) ** 0.55

    def _id(self, prefix='i'):
        self._n += 1
        return '%s%d' % (prefix, self._n)

    def raw(self, s):
        self.out.append(s)

    # --- colour
    def fill(self, pts, color, closed=True, n=8, op=1.0, pattern=None, pat_op=1.0):
        """A flat printed colour. `pattern` (an id from one of the pattern methods) is printed over it,
        flat — a cloth pattern doesn't follow the folds."""
        sm = curve(pts, closed, n)
        d = path_d(sm)
        self.out.append('<path d="%s" fill="%s"%s/>' % (d, color, '' if op == 1 else ' opacity="%s"' % _f2(op)))
        if pattern:
            self.out.append('<path d="%s" fill="url(#%s)"%s/>' % (d, pattern, '' if pat_op == 1 else
                                                                 ' opacity="%s"' % _f2(pat_op)))
        return sm

    def clip(self, pts, n=8):
        cid = self._id('c')
        self.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, path_d(curve(pts, True, n))))
        return cid

    def bokashi(self, pts, color, p1, p2, op=0.6, n=8, radial=None):
        """Gradation: the colour wiped on the block by hand — full at p1, gone at p2 — inside the shape pts.
        radial=(cx, cy, r) gives a round soft patch (a cheek, the lid of an eye)."""
        gid = self._id('b')
        if radial:
            cx, cy, r = radial
            self.defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s">'
                             '<stop offset="0" stop-color="%s" stop-opacity="%s"/><stop offset="0.55" '
                             'stop-color="%s" stop-opacity="%s"/><stop offset="1" stop-color="%s" '
                             'stop-opacity="0"/></radialGradient>'
                             % (gid, _f(cx), _f(cy), _f(r), color, _f2(op), color, _f2(op * 0.55), color))
        else:
            self.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" '
                             'y2="%s"><stop offset="0" stop-color="%s" stop-opacity="%s"/><stop offset="0.5" '
                             'stop-color="%s" stop-opacity="%s"/><stop offset="1" stop-color="%s" '
                             'stop-opacity="0"/></linearGradient>'
                             % (gid, _f(p1[0]), _f(p1[1]), _f(p2[0]), _f(p2[1]), color, _f2(op), color,
                                _f2(op * 0.45), color))
        self.out.append('<path d="%s" fill="url(#%s)"/>' % (path_d(curve(pts, True, n)), gid))

    # --- line
    def line(self, pts, w=3.0, prof='swell', color=INK, nib=0.3, n=8, op=1.0):
        """One stroke of the brush."""
        sm = curve(pts, False, n)
        self._n += 1
        self.out.append('<path d="%s" fill="%s"%s/>' % (brush_poly(sm, w * self.lw, prof, nib, False, self._n),
                                                       color, '' if op == 1 else ' opacity="%s"' % _f2(op)))
        return sm

    def contour(self, pts, w=3.0, color=INK, nib=0.45, n=8):
        """The closed outline of a shape, its weight changing with direction."""
        sm = curve(pts, True, n)
        self._n += 1
        self.out.append('<path d="%s" fill="%s" fill-rule="evenodd"/>'
                        % (brush_poly(sm, w * self.lw, 'even', nib, True, self._n), color))

    def shape(self, pts, color, w=3.0, line=INK, pattern=None, pat_op=1.0, nib=0.45, n=8):
        """Colour and its outline together."""
        self.fill(pts, color, n=n, pattern=pattern, pat_op=pat_op)
        if w:
            self.contour(pts, w, line, nib, n)

    def strands(self, a, b, count, w=1.0, color=INK, prof='swell', t0=0.0, t1=1.0, jitter=0.6, op=1.0, n=8):
        """Fine parallel lines between two guide curves: hair cut line by line, the comb's trace."""
        sa, sb = curve(a, False, n), curve(b, False, n)
        for i in range(count):
            t = t0 + (t1 - t0) * (i + 0.5) / count + self.rnd.uniform(-jitter, jitter) / count
            sm = lerp_pts(sa, sb, t)
            self._n += 1
            self.out.append('<path d="%s" fill="%s"%s/>' % (brush_poly(sm, w * self.lw, prof, 0.15, False, self._n),
                                                           color, '' if op == 1 else ' opacity="%s"' % _f2(op)))

    def fringe(self, pts, length=10, w=1.0, color=INK, lean=0.0, step=3.0, side=1, vary=0.4, prof='taper', n=8):
        """Short separate hairs growing out of an edge: the hairline of a print (kewari), a beard, a brow."""
        sm = curve(pts, False, n)
        acc = 0.0
        for i in range(1, len(sm)):
            dx, dy = sm[i][0] - sm[i - 1][0], sm[i][1] - sm[i - 1][1]
            ln = math.hypot(dx, dy)
            acc += ln
            if acc < step or ln == 0:
                continue
            acc = 0.0
            nx, ny = -dy / ln * side, dx / ln * side
            tx, ty = dx / ln, dy / ln
            L = length * (1 + self.rnd.uniform(-vary, vary))
            le = lean + self.rnd.uniform(-0.15, 0.15)
            ex, ey = sm[i][0] + (nx + tx * le) * L, sm[i][1] + (ny + ty * le) * L
            mx, my = sm[i][0] + (nx + tx * le * 0.3) * L * 0.5, sm[i][1] + (ny + ty * le * 0.3) * L * 0.5
            self._n += 1
            self.out.append('<path d="%s" fill="%s"/>' % (
                brush_poly(curve([sm[i], (mx, my), (ex, ey)], False, 4), w * self.lw, prof, 0.1, False, self._n),
                color))

    def dot(self, x, y, r, color=INK):
        self.out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(x), _f(y), _f2(r), color))

    def ellipse(self, x, y, rx, ry, color, rot=0, op=1.0):
        self.out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"%s%s/>' % (
            _f(x), _f(y), _f(rx), _f(ry), color,
            ' transform="rotate(%s %s %s)"' % (_f(rot), _f(x), _f(y)) if rot else '',
            '' if op == 1 else ' opacity="%s"' % _f2(op)))

    # --- cloth patterns (printed flat)
    def _pat(self, key, w, h, body, rot=0):
        if key in self._ids:
            return self._ids[key]
        pid = self._id('p')
        self._ids[key] = pid
        self.defs.append('<pattern id="%s" width="%s" height="%s" patternUnits="userSpaceOnUse"%s>%s</pattern>'
                         % (pid, _f(w), _f(h), ' patternTransform="rotate(%s)"' % _f(rot) if rot else '', body))
        return pid

    def stripes(self, color, gap=14, band=6, rot=0):
        return self._pat(('st', color, gap, band, rot), gap, gap,
                         '<rect width="%s" height="%s" fill="%s"/>' % (_f(band), _f(gap), color), rot)

    def checks(self, color, size=12, rot=0):
        """Ichimatsu: the chequer board."""
        return self._pat(('ch', color, size, rot), 2 * size, 2 * size,
                         '<rect width="{0}" height="{0}" fill="{1}"/><rect x="{0}" y="{0}" width="{0}" height="{0}" '
                         'fill="{1}"/>'.format(_f(size), color), rot)

    def dots(self, color, gap=9, r=1.6, rot=30):
        """Kanoko / same-komon: small dots in staggered rows."""
        return self._pat(('do', color, gap, r, rot), gap, gap,
                         '<circle cx="{0}" cy="{0}" r="{2}" fill="{3}"/><circle cx="{1}" cy="{1}" r="{2}" fill="{3}"/>'
                         .format(_f(gap * 0.25), _f(gap * 0.75), _f2(r), color), rot)

    def asanoha(self, color, size=22, w=1.0, rot=0):
        """Hemp leaf: six-pointed stars of straight lines."""
        a, h = size, size * 0.8660254
        ln = []

        def seg(x1, y1, x2, y2):
            ln.append('M%s %sL%s %s' % (_f(x1), _f(y1), _f(x2), _f(y2)))
        for ox, oy in ((0, 0), (a / 2, h)):
            for dx, dy in ((-a, 0), (0, 0), (a, 0)):
                cx, cy = ox + dx, oy + dy
                for k in range(6):
                    ang = math.radians(60 * k)
                    seg(cx, cy, cx + a * math.cos(ang), cy + a * math.sin(ang))
                    ang2 = math.radians(60 * k + 30)
                    r2 = a / math.sqrt(3)
                    px, py = cx + r2 * math.cos(ang2), cy + r2 * math.sin(ang2)
                    seg(px, py, cx + a * math.cos(ang), cy + a * math.sin(ang))
                    seg(px, py, cx + a * math.cos(ang + math.radians(60)), cy + a * math.sin(ang + math.radians(60)))
        return self._pat(('as', color, size, w, rot), a, 2 * h,
                         '<path d="%s" stroke="%s" stroke-width="%s" fill="none"/>' % (''.join(ln), color, _f2(w)),
                         rot)

    def seigaiha(self, color, r=14, w=1.0, rot=0):
        """Blue sea waves: overlapping arcs in rows."""
        arcs = []
        for cx, cy in ((0, r), (2 * r, r), (r, 0), (r, 2 * r), (-r, 0), (3 * r, 0), (-r, 2 * r), (3 * r, 2 * r)):
            for k in (1.0, 0.7, 0.4):
                rr = r * k
                arcs.append('M%s %sA%s %s 0 0 1 %s %s' % (_f(cx - rr), _f(cy), _f(rr), _f(rr), _f(cx + rr), _f(cy)))
        return self._pat(('se', color, r, w, rot), 2 * r, 2 * r,
                         '<path d="%s" stroke="%s" stroke-width="%s" fill="none"/>' % (''.join(arcs), color, _f2(w)),
                         rot)

    def blossoms(self, color, gap=34, r=4.0, rot=20, heart=None):
        """Small five-petal flowers scattered (komon)."""
        body = ''
        for cx, cy, k in ((gap * 0.25, gap * 0.3, 1.0), (gap * 0.75, gap * 0.8, 0.8)):
            for i in range(5):
                a = math.radians(72 * i - 90)
                body += '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
                    _f(cx + r * k * math.cos(a)), _f(cy + r * k * math.sin(a)), _f2(r * k * 0.62), color)
            if heart:
                body += '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(cx), _f(cy), _f2(r * k * 0.45), heart)
        return self._pat(('bl', color, gap, r, rot, heart), gap, gap, body, rot)

    def kasuri(self, color, gap=16, size=5, rot=0):
        """Kasuri: small crosses of a woven splash pattern."""
        s = size
        body = ''
        for cx, cy in ((gap * 0.25, gap * 0.25), (gap * 0.75, gap * 0.75)):
            body += '<path d="M%s %sh%sM%s %sv%s" stroke="%s" stroke-width="%s"/>' % (
                _f(cx - s / 2), _f(cy), _f(s), _f(cx), _f(cy - s / 2), _f(s), color, _f2(s * 0.3))
        return self._pat(('ka', color, gap, size, rot), gap, gap, body, rot)

    # --- the sheet
    def ground(self, color='#d9cdb0', top=None, bottom=None, margin=26, mica=False):
        """The printed ground inside the border; `top` / `bottom` — a band of bokashi along that edge."""
        m = self.margin = margin
        w, h = self.w - 2 * m, self.h - 2 * m
        s = '<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (m, m, w, h, color)
        if top:
            gid = self._id('b')
            self.defs.append('<linearGradient id="%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/>'
                             '<stop offset="0.5" stop-color="%s" stop-opacity="0.35"/>'
                             '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>'
                             % (gid, top, top, top))
            s += '<rect x="%d" y="%d" width="%d" height="%s" fill="url(#%s)"/>' % (m, m, w, _f(h * 0.3), gid)
        if bottom:
            gid = self._id('b')
            self.defs.append('<linearGradient id="%s" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="%s"/>'
                             '<stop offset="0.5" stop-color="%s" stop-opacity="0.35"/>'
                             '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>'
                             % (gid, bottom, bottom, bottom))
            s += '<rect x="%d" y="%s" width="%d" height="%s" fill="url(#%s)"/>' % (m, _f(m + h * 0.78), w,
                                                                                 _f(h * 0.22), gid)
        self.ground_svg = s
        self.mica = mica

    def cartouche(self, text, x, y, size=26, seal=True, color=RED):
        """The title slip of a print — the name, written downwards — and the red seal under it."""
        n = len(text)
        w, h = size * 1.5, size * 1.12 * n + size * 0.7
        s = '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (_f(x), _f(y), _f(w), _f(h), '#f3ead6')
        s += '<rect x="%s" y="%s" width="%s" height="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (
            _f(x), _f(y), _f(w), _f(h), INK)
        for i, ch in enumerate(text):
            s += ('<text x="%s" y="%s" font-family="Georgia, \'PT Serif\', \'DejaVu Serif\', serif" font-size="%s" '
                  'text-anchor="middle" fill="%s">%s</text>') % (
                _f(x + w / 2), _f(y + size * 1.12 * (i + 1) + size * 0.05), _f(size), INK, ch)
        if seal:
            sy = y + h + size * 0.45
            ss = size * 1.05
            sx = x + (w - ss) / 2
            s += '<rect x="%s" y="%s" width="%s" height="%s" rx="2" fill="%s"/>' % (_f(sx), _f(sy), _f(ss), _f(ss),
                                                                                 color)
            # the seal's sign: a plain cut mark, not a word
            s += ('<path d="M%s %sh%sM%s %sv%sM%s %sh%s" stroke="#f3ead6" stroke-width="%s" fill="none"/>' % (
                _f(sx + ss * 0.22), _f(sy + ss * 0.3), _f(ss * 0.56), _f(sx + ss * 0.5), _f(sy + ss * 0.3),
                _f(ss * 0.48), _f(sx + ss * 0.28), _f(sy + ss * 0.78), _f(ss * 0.44), _f2(ss * 0.1)))
        self.over_svg += s

    def svg(self):
        w, h, m = self.w, self.h, self.margin
        sd = self.seed
        defs = ''.join(self.defs)
        defs += (
            # paper: fibres and tooth, printed colour sinks into it unevenly
            '<filter id="paper" x="0" y="0" width="100%%" height="100%%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="%d"/>'
            '<feColorMatrix values="0 0 0 0 0.42  0 0 0 0 0.33  0 0 0 0 0.2  0.85 0 0 0 -0.27"/></filter>'
            # wood grain of the colour block: long light streaks where the pigment didn't take
            '<filter id="grain" x="0" y="0" width="100%%" height="100%%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.0035 0.11" numOctaves="3" seed="%d"/>'
            '<feColorMatrix values="0 0 0 0 0.97  0 0 0 0 0.93  0 0 0 0 0.82  2.4 0 0 0 -1.2"/></filter>'
            # old paper: blotches of tone
            '<filter id="age" x="0" y="0" width="100%%" height="100%%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.006" numOctaves="3" seed="%d"/>'
            '<feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.36  0 0 0 0 0.16  1.3 0 0 0 -0.5"/></filter>'
            % (sd, sd + 5, sd + 9))
        s = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)
             + '<defs>' + defs + '<clipPath id="sheet"><rect x="%d" y="%d" width="%d" height="%d"/></clipPath></defs>'
             % (m, m, w - 2 * m, h - 2 * m)
             + '<rect width="%d" height="%d" fill="%s"/>' % (w, h, PAPER)
             + self.ground_svg
             + '<g clip-path="url(#sheet)">' + ''.join(self.out) + '</g>'
             + self.over_svg)
        if m:
            s += '<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2.2"/>' % (
                m, m, w - 2 * m, h - 2 * m, INK)
        s += ('<rect width="%d" height="%d" filter="url(#grain)" opacity="0.15" style="mix-blend-mode:screen"/>'
              '<rect width="%d" height="%d" filter="url(#paper)" opacity="0.42" style="mix-blend-mode:multiply"/>'
              '<rect width="%d" height="%d" filter="url(#age)" opacity="0.28" style="mix-blend-mode:multiply"/>'
              % (w, h, w, h, w, h))
        return s + '</svg>'


def _f2(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')
