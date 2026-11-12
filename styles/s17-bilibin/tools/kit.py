"""The means of the ornamental illustration (Bilibin, Mucha, 1900s), shared by every character: the even ink
contour, flat fills, ornament patterns, ornament bands along a hem, the decorated frame, the Mucha halo,
the flat landscape of a fairy-tale page, paper.

Everything is drawn into a Doc; a character module never writes SVG itself.
Points are (x, y) or (x, y, 'c') — 'c' marks a corner; other points are joined by a smooth curve.
"""
import math
import random
from contextlib import contextmanager

INK = '#1d1712'          # the drawing ink: a warm black
PAPER = '#efe4c8'        # book paper
SKIN = '#f1d9bd'         # skin: one flat light tone
SKIN_SH = '#e2bf9c'      # the only second tone of skin (used sparingly: under hair, a neck under the chin)
RED = '#a8392b'          # cinnabar of the folk ornament
GOLD = '#c99a3c'         # ochre gold (Mucha's halo, Bilibin's borders)
GREEN = '#5d6b3a'        # olive green
BLUE = '#5d7a8c'         # dusty blue
CREAM = '#f6edd5'


def _f(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')


def _f2(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


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


def curve(pts, closed=False, n=6):
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
    n = max(len(a), len(b))
    out = []
    for i in range(n):
        u = i / (n - 1)
        pa = a[min(len(a) - 1, int(round(u * (len(a) - 1))))]
        pb = b[min(len(b) - 1, int(round(u * (len(b) - 1))))]
        out.append((pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t))
    return out


def arclen(sm):
    s = [0.0]
    for i in range(1, len(sm)):
        s.append(s[-1] + math.hypot(sm[i][0] - sm[i - 1][0], sm[i][1] - sm[i - 1][1]))
    return s


def offset(sm, dist):
    """The curve moved sideways by dist (positive: to the left of the direction of travel)."""
    out = []
    n = len(sm)
    for i in range(n):
        a, b = sm[max(0, i - 1)], sm[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        d = dist(i / (n - 1)) if callable(dist) else dist
        out.append((sm[i][0] + dy / ln * d, sm[i][1] - dx / ln * d))
    return out


def taper_poly(sm, w, prof='taper'):
    """A stroke with pointed ends: a hair lock, a lash, a fold that dies away."""
    s = arclen(sm)
    tot = s[-1] or 1.0

    def width(i):
        t = s[i] / tot
        if prof == 'taper':          # full at the root, pointed at the end
            return w * (1 - t) ** 0.8 * min(1.0, t / 0.08 + 0.35)
        if prof == 'swell':
            return w * (0.15 + 0.85 * math.sin(math.pi * t) ** 0.8)
        if prof == 'even':
            return w * min(1.0, t / 0.04 + 0.5, (1 - t) / 0.04 + 0.5)
        return w
    left, right = [], []
    n = len(sm)
    for i in range(n):
        a, b = sm[max(0, i - 1)], sm[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        hw = width(i) / 2
        left.append((sm[i][0] + dy / ln * hw, sm[i][1] - dx / ln * hw))
        right.append((sm[i][0] - dy / ln * hw, sm[i][1] + dx / ln * hw))
    return path_d(left + right[::-1])


# ---------------------------------------------------------------- the sheet

class Doc:
    LINE = 3.2          # the contour: one even weight for every outline of a figure
    THIN = 1.7          # the drawing inside a shape: folds, features, ornament

    def __init__(self, w, h, seed=1, paper=PAPER):
        self.w, self.h = w, h
        self.out = []
        self.defs = []
        self.over = []
        self._ids = {}
        self.scale = [1.0]
        self.rnd = random.Random(seed)
        self.seed = seed
        self.paper = paper
        self._n = 0

    # --- groups
    @contextmanager
    def g(self, x=0, y=0, s=1.0, rot=0, flip=False, clip=None):
        t = 'translate(%s %s)' % (_f(x), _f(y))
        if rot:
            t += ' rotate(%s)' % _f(rot)
        if s != 1.0 or flip:
            t += ' scale(%s %s)' % (_f2(-s if flip else s), _f2(s))
        self.out.append('<g transform="%s"%s>' % (t, ' clip-path="url(#%s)"' % clip if clip else ''))
        self.scale.append(self.scale[-1] * s)
        try:
            yield
        finally:
            self.scale.pop()
            self.out.append('</g>')

    @property
    def lw(self):
        """The line keeps one weight on the page whatever the scale of the group (the ornamental line is even);
        a little heavier when a figure is drawn large, so a bust doesn't look scratched."""
        s = self.scale[-1]
        return (1.0 / s) * (s ** 0.25)

    def _id(self, prefix='i'):
        self._n += 1
        return '%s%d' % (prefix, self._n)

    def raw(self, s):
        self.out.append(s)

    # --- colour and line
    def fill(self, pts, color, n=6, pattern=None, op=1.0, pat_op=1.0):
        sm = curve(pts, True, n)
        d = path_d(sm)
        self.out.append('<path d="%s" fill="%s"%s/>' % (d, color, '' if op == 1 else ' opacity="%s"' % _f2(op)))
        if pattern:
            self.out.append('<path d="%s" fill="url(#%s)"%s/>' % (d, pattern, '' if pat_op == 1 else
                                                                 ' opacity="%s"' % _f2(pat_op)))
        return sm

    def ink(self, pts, w=None, closed=False, color=INK, n=6, op=1.0, cap='round'):
        """The even ink line."""
        sm = curve(pts, closed, n)
        w = (w if w is not None else self.LINE) * self.lw
        self.out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round" '
                        'stroke-linecap="%s"%s/>' % (path_d(sm, closed), color, _f2(w), cap,
                                                     '' if op == 1 else ' opacity="%s"' % _f2(op)))
        return sm

    def thin(self, pts, closed=False, color=INK, n=6, k=1.0, op=1.0):
        return self.ink(pts, self.THIN * k, closed, color, n, op)

    def shape(self, pts, color, w=None, pattern=None, pat_op=1.0, n=6, line=INK):
        """A flat colour and its contour."""
        sm = self.fill(pts, color, n, pattern, pat_op=pat_op)
        if w != 0:
            self.ink(pts, w, True, line, n)
        return sm

    def lock(self, pts, w=4.0, color=INK, prof='taper', n=6):
        """A stroke with a pointed end: a lock of hair, a lash, a fold dying away."""
        sm = curve(pts, False, n)
        self.out.append('<path d="%s" fill="%s"/>' % (taper_poly(sm, w * self.lw, prof), color))
        return sm

    def dot(self, x, y, r, color=INK):
        self.out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(x), _f(y), _f2(r), color))

    def circle(self, x, y, r, fill='none', stroke=INK, w=None, op=1.0):
        w = (w if w is not None else self.LINE) * self.lw
        self.out.append('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"%s/>' % (
            _f(x), _f(y), _f(r), fill, stroke, _f2(w), '' if op == 1 else ' opacity="%s"' % _f2(op)))

    def clip(self, pts, n=6):
        cid = self._id('c')
        self.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, path_d(curve(pts, True, n))))
        return cid

    @contextmanager
    def clipped(self, pts, n=6):
        cid = self.clip(pts, n)
        self.out.append('<g clip-path="url(#%s)">' % cid)
        try:
            yield
        finally:
            self.out.append('</g>')

    # --- ornament bands: the embroidered hem, the border of a towel, a placket
    def band(self, pts, width, color, kind='rhomb', ink=RED, ground=None, edge=True, n=6, step=None, flip=False):
        """An ornament band of `width` along the open curve pts (centre line): a flat ground, a motif repeated
        along the band, and its two edges in ink. Kinds: rhomb, cross, teeth, wave, dots, flower, stripe."""
        sm = curve(pts, False, n)
        L = arclen(sm)
        a = offset(sm, width / 2)
        b = offset(sm, -width / 2)
        poly = a + b[::-1]
        self.out.append('<path d="%s" fill="%s"/>' % (path_d(poly), ground or CREAM))
        step = step or width * 1.0
        tot = L[-1]
        k = max(1, int(tot / step))
        step = tot / k

        def at(s, side):
            # point at arclength s, side in -1..1 across the band
            i = 1
            while i < len(L) - 1 and L[i] < s:
                i += 1
            t = (s - L[i - 1]) / ((L[i] - L[i - 1]) or 1)
            x = sm[i - 1][0] + (sm[i][0] - sm[i - 1][0]) * t
            y = sm[i - 1][1] + (sm[i][1] - sm[i - 1][1]) * t
            dx, dy = sm[i][0] - sm[i - 1][0], sm[i][1] - sm[i - 1][1]
            ln = math.hypot(dx, dy) or 1
            sd = side * width / 2 * (-1 if flip else 1)
            return (x + dy / ln * sd, y - dx / ln * sd)
        parts = []
        lw = self.THIN * self.lw
        for j in range(k):
            s0, s1 = j * step, (j + 1) * step
            sc = (s0 + s1) / 2
            if kind == 'rhomb':
                q = [at(s0 + step * 0.12, 0), at(sc, 0.62), at(s1 - step * 0.12, 0), at(sc, -0.62)]
                parts.append('<path d="%s" fill="%s"/>' % (path_d(q), ink))
                c = at(sc, 0)
                parts.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(c[0]), _f(c[1]),
                                                                             _f2(width * 0.09), ground or CREAM))
            elif kind == 'cross':       # cross-stitch: a stepped cross
                u = step * 0.13
                for dd in (-1, 0, 1):
                    for ee in (-1, 0, 1):
                        if abs(dd) + abs(ee) <= 1:
                            c = at(sc + dd * u * 1.6, ee * 0.36)
                            parts.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (
                                _f(c[0] - u * 0.75), _f(c[1] - u * 0.75), _f2(u * 1.5), _f2(u * 1.5), ink))
            elif kind == 'teeth':       # wolf teeth: triangles alternating
                q = [at(s0, -0.75), at(sc, 0.75), at(s1, -0.75)]
                parts.append('<path d="%s" fill="%s"/>' % (path_d(q), ink))
            elif kind == 'wave':        # a running scroll
                q = [at(s0, 0), at(s0 + step * 0.25, 0.55), at(sc, 0), at(s0 + step * 0.75, -0.55), at(s1, 0)]
                parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s"/>'
                             % (path_d(curve(q, False, 6), False), ink, _f2(lw * 1.3)))
                c = at(s0 + step * 0.25, 0.1)
                parts.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(c[0]), _f(c[1]), _f2(width * .1), ink))
            elif kind == 'dots':
                c = at(sc, 0)
                parts.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(c[0]), _f(c[1]), _f2(width * .22), ink))
            elif kind == 'flower':      # a little five-petal flower with leaves
                c = at(sc, 0)
                for i in range(5):
                    an = math.radians(72 * i)
                    parts.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
                        _f(c[0] + math.cos(an) * width * 0.2), _f(c[1] + math.sin(an) * width * 0.2),
                        _f2(width * 0.14), ink))
                parts.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(c[0]), _f(c[1]), _f2(width * 0.1),
                                                                             GOLD))
            elif kind == 'stripe':
                q = [at(s0 + step * 0.3, -1), at(s0 + step * 0.3, 1), at(s0 + step * 0.6, 1), at(s0 + step * 0.6, -1)]
                parts.append('<path d="%s" fill="%s"/>' % (path_d(q), ink))
        self.out.append(''.join(parts))
        if edge:
            for e in (a, b):
                self.out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>'
                                % (path_d(e, False), INK, _f2(lw)))
        return poly

    # --- patterns (fills of cloth)
    def _pat(self, key, w, h, body, rot=0):
        if key in self._ids:
            return self._ids[key]
        pid = self._id('p')
        self._ids[key] = pid
        self.defs.append('<pattern id="%s" width="%s" height="%s" patternUnits="userSpaceOnUse"%s>%s</pattern>'
                         % (pid, _f(w), _f(h), ' patternTransform="rotate(%s)"' % _f(rot) if rot else '', body))
        return pid

    def p_stripes(self, color, gap=14, band=6, rot=0):
        return self._pat(('st', color, gap, band, rot), gap, gap,
                         '<rect width="%s" height="%s" fill="%s"/>' % (_f(band), _f(gap), color), rot)

    def p_dots(self, color, gap=10, r=1.6, rot=0):
        return self._pat(('do', color, gap, r, rot), gap, gap,
                         '<circle cx="{0}" cy="{0}" r="{2}" fill="{3}"/><circle cx="{1}" cy="{1}" r="{2}" fill="{3}"/>'
                         .format(_f(gap * 0.25), _f(gap * 0.75), _f2(r), color), rot)

    def p_sprig(self, color, leaf, gap=36, r=3.4, rot=0):
        """A calico of small flowers with two leaves each — the printed cotton (ситец) of a peasant dress."""
        body = ''
        for cx, cy in ((gap * 0.25, gap * 0.25), (gap * 0.75, gap * 0.75)):
            body += '<path d="M%s %sq%s %s %s %s" fill="none" stroke="%s" stroke-width="%s"/>' % (
                _f(cx), _f(cy), _f(r * 1.2), _f(r * 1.4), _f(r * 2.6), _f(r * 1.2), leaf, _f2(r * 0.35))
            body += '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" transform="rotate(-30 %s %s)"/>' % (
                _f(cx + r * 2.0), _f(cy + r * 1.7), _f(r * 0.9), _f(r * 0.45), leaf, _f(cx + r * 2.0),
                _f(cy + r * 1.7))
            for i in range(5):
                a = math.radians(72 * i - 90)
                body += '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
                    _f(cx + r * math.cos(a)), _f(cy + r * math.sin(a)), _f2(r * 0.6), color)
            body += '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(cx), _f(cy), _f2(r * 0.45), GOLD)
        return self._pat(('sp', color, leaf, gap, r, rot), gap, gap, body, rot)

    def p_rhombs(self, color, size=16, w=1.4, rot=0):
        """A lattice of rhombs with a dot in each — knitting, a woven belt."""
        s = size
        body = ('<path d="M0 {h}L{h} 0L{s} {h}L{h} {s}Z" fill="none" stroke="{c}" stroke-width="{w}"/>'
                '<circle cx="{h}" cy="{h}" r="{r}" fill="{c}"/>').format(h=_f(s / 2), s=_f(s), c=color, w=_f2(w),
                                                                        r=_f2(s * 0.09))
        return self._pat(('rh', color, size, w, rot), s, s, body, rot)

    def p_checks(self, color, size=10, rot=0):
        return self._pat(('ch', color, size, rot), 2 * size, 2 * size,
                         '<rect width="{0}" height="{0}" fill="{1}"/><rect x="{0}" y="{0}" width="{0}" height="{0}" '
                         'fill="{1}"/>'.format(_f(size), color), rot)

    def p_scales(self, color, r=9, w=1.2, rot=0):
        """Scale or petal pattern: arcs in staggered rows (Bilibin's roofs, Mucha's mosaics)."""
        body = ''
        for cx, cy in ((0, 0), (2 * r, 0), (r, r), (0, 2 * r), (2 * r, 2 * r)):
            body += '<path d="M%s %sA%s %s 0 0 0 %s %s" fill="none" stroke="%s" stroke-width="%s"/>' % (
                _f(cx - r), _f(cy), _f(r), _f(r), _f(cx + r), _f(cy), color, _f2(w))
        return self._pat(('sc', color, r, w, rot), 2 * r, 2 * r, body, rot)

    def p_herring(self, color, size=12, w=1.3, rot=0):
        """Herringbone / a knitted chevron."""
        s = size
        body = '<path d="M0 0L%s %sL%s 0" fill="none" stroke="%s" stroke-width="%s"/>' % (
            _f(s / 2), _f(s / 2), _f(s), color, _f2(w))
        return self._pat(('hb', color, size, w, rot), s, s * 0.7, body, rot)

    # --- the page
    def frame(self, x, y, w, h, kind='rhomb', ink=RED, ground=CREAM, width=26, outer=INK, inner_kind='teeth',
              inner_ink=GREEN):
        """The decorated border of a book page (Bilibin): a black rule, a wide ornament band, a black rule, a narrow
        second band, a black rule; corner squares with a rosette."""
        m = width
        m2 = max(8, width * 0.42)
        lw = self.LINE * 1.15

        def runs(o, ww):
            return [[(x + o + ww / 2, y + o + ww / 2), (x + w - o - ww / 2, y + o + ww / 2)],
                    [(x + w - o - ww / 2, y + o + ww / 2), (x + w - o - ww / 2, y + h - o - ww / 2)],
                    [(x + w - o - ww / 2, y + h - o - ww / 2), (x + o + ww / 2, y + h - o - ww / 2)],
                    [(x + o + ww / 2, y + h - o - ww / 2), (x + o + ww / 2, y + o + ww / 2)]]
        for r in runs(0, m):
            self.band(r, m, None, kind, ink, ground, edge=False, n=2, step=m * 1.15)
        for r in runs(m, m2):
            self.band(r, m2, None, inner_kind, inner_ink, '#e9dfc2', edge=False, n=2, step=m2 * 1.2)
        s = []
        for o, ww in ((0, lw), (m, lw * 0.8), (m + m2, lw * 0.9)):
            s.append('<rect x="%s" y="%s" width="%s" height="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (
                _f(x + o), _f(y + o), _f(w - 2 * o), _f(h - 2 * o), outer, _f2(ww)))
        for qx, qy in ((x, y), (x + w - m, y), (x, y + h - m), (x + w - m, y + h - m)):
            s.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (
                _f(qx), _f(qy), _f(m), _f(m), ink, outer, _f2(lw * 0.8)))
            c = (qx + m / 2, qy + m / 2)
            for i in range(4):
                a = math.radians(90 * i + 45)
                s.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (
                    _f(c[0] + math.cos(a) * m * 0.2), _f(c[1] + math.sin(a) * m * 0.2), _f2(m * 0.14), ground))
            s.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(c[0]), _f(c[1]), _f2(m * 0.1), GOLD))
        self.out.append(''.join(s))

    def svg(self, texture=True):
        w, h = self.w, self.h
        sd = self.seed
        defs = ''.join(self.defs)
        defs += (
            '<filter id="paper" x="0" y="0" width="100%%" height="100%%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="%d"/>'
            '<feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.36  0 0 0 0 0.22  0.7 0 0 0 -0.24"/></filter>'
            '<filter id="age" x="0" y="0" width="100%%" height="100%%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.005" numOctaves="3" seed="%d"/>'
            '<feColorMatrix values="0 0 0 0 0.55  0 0 0 0 0.42  0 0 0 0 0.2  1.1 0 0 0 -0.45"/></filter>'
            % (sd, sd + 7))
        s = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)
             + '<defs>' + defs + '</defs>'
             + '<rect width="%d" height="%d" fill="%s"/>' % (w, h, self.paper)
             + ''.join(self.out) + ''.join(self.over))
        if texture:
            s += ('<rect width="%d" height="%d" filter="url(#paper)" opacity="0.3" style="mix-blend-mode:multiply"/>'
                  '<rect width="%d" height="%d" filter="url(#age)" opacity="0.18" style="mix-blend-mode:multiply"/>'
                  % (w, h, w, h))
        return s + '</svg>'


# ---------------------------------------------------------------- page pieces (Mucha's halo, Bilibin's landscape)

def halo(d, cx, cy, r, ring=GOLD, field='#e9d9b0', ink=RED, kind='petals'):
    """The disc behind a head (Mucha): a field, a broad ring with ornament, thin rules."""
    lw = d.THIN * d.lw
    d.raw('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(cx), _f(cy), _f(r), field))
    # inner rays: thin lines and dots radiating, as in Mucha's zodiac discs
    n = 36
    rays = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rays.append('M%s %sL%s %s' % (_f(cx + math.cos(a) * r * 0.32), _f(cy + math.sin(a) * r * 0.32),
                                      _f(cx + math.cos(a) * r * 0.74), _f(cy + math.sin(a) * r * 0.74)))
    d.raw('<path d="%s" stroke="%s" stroke-width="%s" opacity="0.35"/>' % (''.join(rays), ink, _f2(lw * 0.8)))
    rr0, rr1 = r * 0.8, r
    d.raw('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (
        _f(cx), _f(cy), _f((rr0 + rr1) / 2), ring, _f(rr1 - rr0)))
    m = 28
    s = []
    for i in range(m):
        a = 2 * math.pi * (i + 0.5) / m
        rm = (rr0 + rr1) / 2
        x, y = cx + math.cos(a) * rm, cy + math.sin(a) * rm
        if kind == 'petals':
            s.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" transform="rotate(%s %s %s)"/>' % (
                _f(x), _f(y), _f((rr1 - rr0) * 0.36), _f((rr1 - rr0) * 0.18), ink, _f(a * 180 / math.pi), _f(x),
                _f(y)))
        else:
            s.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(x), _f(y), _f((rr1 - rr0) * 0.2), ink))
        a2 = 2 * math.pi * i / m
        s.append('<path d="M%s %sL%s %s" stroke="%s" stroke-width="%s"/>' % (
            _f(cx + math.cos(a2) * rr0), _f(cy + math.sin(a2) * rr0), _f(cx + math.cos(a2) * rr1),
            _f(cy + math.sin(a2) * rr1), INK, _f2(lw * 0.7)))
    d.raw(''.join(s))
    for rr in (rr0, rr1, r * 0.3):
        d.raw('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (
            _f(cx), _f(cy), _f(rr), INK, _f2(lw * (1.4 if rr == rr1 else 1.0))))


def cloud(d, x, y, w, color='#f6efdc'):
    """A flat ornamental cloud: a row of curls on a flat base, outlined."""
    k = w / 100
    pts = [(x, y, 'c'), (x + 8 * k, y - 12 * k), (x + 22 * k, y - 16 * k), (x + 30 * k, y - 26 * k),
           (x + 46 * k, y - 30 * k), (x + 60 * k, y - 22 * k), (x + 72 * k, y - 26 * k), (x + 88 * k, y - 16 * k),
           (x + 100 * k, y, 'c')]
    d.shape(pts, color, d.THIN * 1.1)
    for cx, cy, r in ((x + 30 * k, y - 12 * k, 7 * k), (x + 58 * k, y - 10 * k, 6 * k)):
        d.thin([(cx - r, cy + r * 0.3), (cx - r * 0.6, cy - r * 0.7), (cx + r * 0.4, cy - r * 0.6),
                (cx + r * 0.3, cy + r * 0.1), (cx - r * 0.1, cy)], k=0.8)


def tuft(d, x, y, h, color=GREEN, flower=None):
    """A tuft of grass as Bilibin draws it: a few blades as flat shapes, maybe a flower on a stalk."""
    for i, (dx, lean, hh) in enumerate(((-6, -0.5, 0.8), (-2, -0.15, 1.0), (3, 0.25, 0.9), (7, 0.6, 0.7))):
        bx = x + dx * h / 30
        tip = (bx + lean * h * 0.6, y - h * hh)
        d.raw('<path d="M%s %sQ%s %s %s %sQ%s %s %s %sZ" fill="%s" stroke="%s" stroke-width="%s"/>' % (
            _f(bx - h * 0.06), _f(y), _f(bx + lean * h * 0.1 - h * 0.05), _f(y - h * hh * 0.6), _f(tip[0]),
            _f(tip[1]), _f(bx + lean * h * 0.15 + h * 0.06), _f(y - h * hh * 0.5), _f(bx + h * 0.06), _f(y), color,
            INK, _f2(d.THIN * d.lw * 0.8)))
    if flower:
        fx, fy = x + h * 0.1, y - h * 1.25
        d.raw('<path d="M%s %sQ%s %s %s %s" fill="none" stroke="%s" stroke-width="%s"/>' % (
            _f(x), _f(y), _f(x - h * 0.1), _f(y - h * 0.6), _f(fx), _f(fy), INK, _f2(d.THIN * d.lw * 0.8)))
        for i in range(5):
            a = math.radians(72 * i - 90)
            d.raw('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (
                _f(fx + math.cos(a) * h * 0.12), _f(fy + math.sin(a) * h * 0.12), _f2(h * 0.09), flower, INK,
                _f2(d.THIN * d.lw * 0.6)))
        d.dot(fx, fy, h * 0.06, GOLD)


def fir(d, x, y, h, color='#4f5f34', dark='#36421f'):
    """A fir as Bilibin draws it: a straight trunk and tiers of drooping branches, each tier a curved fan with
    a dark underside line."""
    tiers = 6
    d.raw('<path d="M%s %sL%s %s" stroke="%s" stroke-width="%s"/>' % (_f(x), _f(y), _f(x), _f(y - h), '#4a3526',
                                                                     _f2(h * 0.035)))
    for i in range(tiers):
        t = i / (tiers - 1)
        ty = y - h * (0.12 + 0.82 * t)
        tw = h * (0.34 - 0.27 * t)
        th = h * 0.2
        pts = [(x, ty - th, 'c'), (x + tw * 0.5, ty - th * 0.3), (x + tw, ty + th * 0.15), (x + tw * 0.5, ty - th * 0.02),
               (x, ty + th * 0.1), (x - tw * 0.5, ty - th * 0.02), (x - tw, ty + th * 0.15), (x - tw * 0.5, ty - th * 0.3)]
        d.shape(pts, color, d.THIN, n=5)
        d.thin([(x - tw * 0.8, ty + th * 0.05), (x - tw * 0.4, ty - th * 0.08), (x, ty + th * 0.02),
                (x + tw * 0.4, ty - th * 0.08), (x + tw * 0.8, ty + th * 0.05)], k=0.6, color=dark)


def birch(d, x, y, h, w=22, lean=0):
    """A birch trunk: white with black dashes across, a few thin branches."""
    import random as _r
    rnd = _r.Random(int(x * 7 + h))
    top = (x + lean, y - h)
    d.shape([(x - w / 2, y, 'c'), (x + w / 2, y, 'c'), (top[0] + w * 0.3, top[1], 'c'), (top[0] - w * 0.3, top[1], 'c')],
            '#f4efe2', n=2)
    for i in range(int(h / 34)):
        t = (i + 0.5) / (h / 34)
        cx = x + lean * t
        ww = w * (1 - 0.4 * t)
        yy = y - h * t + rnd.uniform(-8, 8)
        side = rnd.choice((-1, 1))
        d.raw('<path d="M%s %sL%s %s" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (
            _f(cx + side * ww / 2), _f(yy), _f(cx + side * ww * rnd.uniform(-0.1, 0.3)), _f(yy + rnd.uniform(-2, 2)),
            INK, _f2(rnd.uniform(3, 6))))


def meadow(d, x, y, w, h, seed=1):
    """The near edge of the field as a flower frieze: tufts and flowers in a loose row."""
    import random as _r
    rnd = _r.Random(seed)
    n = int(w / 42)
    cols = ('#a8392b', '#5d7a8c', '#e8d27a', '#c99a3c', '#f4efe2')
    for i in range(n):
        xx = x + (i + 0.5) * w / n + rnd.uniform(-10, 10)
        yy = y + h - rnd.uniform(4, h * 0.7)
        tuft(d, xx, yy, rnd.uniform(32, 52), flower=cols[i % len(cols)] if rnd.random() < 0.6 else None)


def landscape(d, x, y, w, h, sky='#e4dcc0', far='#a9ae8a', near='#8d9662', ground='#b7a873', horizon=0.62, seed=3,
              clouds=True, trees=True):
    """A flat fairy-tale landscape (Bilibin): a pale sky with ornamental clouds, a band of distant forest as
    a row of fir silhouettes, rolling fields in flat bands with contour lines, tufts and flowers in front."""
    import random as _r
    rnd = _r.Random(seed)
    hy = y + h * horizon
    d.raw('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (_f(x), _f(y), _f(w), _f(h), sky))
    if clouds:
        for i in range(3 if w < h * 1.2 else 5):
            cw = min(w * rnd.uniform(0.12, 0.2), h * rnd.uniform(0.16, 0.22))
            k = 3 if w < h * 1.2 else 5
            cloud(d, x + w * (0.06 + 0.9 * i / k) + rnd.uniform(0, w * 0.06), y + h * rnd.uniform(0.1, 0.26), cw)
    # distant forest: a row of small firs
    if trees == 'firs':
        for i in range(int(w / 34) + 2):
            fh = h * rnd.uniform(0.1, 0.16)
            fir(d, x + i * 34 + rnd.uniform(-6, 6), hy + 6, fh, '#7d8a5a', '#55613a')
        trees = False
    if trees:
        fx = x - 10
        pts = [(x, hy)]
        while fx < x + w + 20:
            th = h * rnd.uniform(0.07, 0.13)
            tw = th * 0.45
            pts += [(fx, hy - th * 0.15, 'c'), (fx + tw * 0.5, hy - th, 'c'), (fx + tw, hy - th * 0.15, 'c')]
            fx += tw * rnd.uniform(0.7, 1.0)
        pts += [(x + w, hy), (x + w, hy + 10, 'c'), (x, hy + 10, 'c')]
        d.shape([(max(x, min(x + w, q[0])),) + tuple(q[1:]) for q in pts], far, d.THIN, n=2)
    # fields: two rolling bands
    b1 = [(x, hy + h * 0.02)]
    for i in range(1, 7):
        b1.append((x + w * i / 6, hy + h * (0.02 + 0.025 * math.sin(i * 1.3 + seed))))
    d.shape(b1 + [(x + w, y + h, 'c'), (x, y + h, 'c')], near, d.THIN)
    b2 = [(x, hy + h * 0.13)]
    for i in range(1, 7):
        b2.append((x + w * i / 6, hy + h * (0.12 + 0.03 * math.sin(i * 0.9 + seed * 2))))
    d.shape(b2 + [(x + w, y + h, 'c'), (x, y + h, 'c')], ground, d.THIN)
    # furrows: thin parallel lines along the near field
    for k in range(4):
        yy = hy + h * (0.2 + 0.05 * k)
        d.thin([(x, yy), (x + w * 0.3, yy - 4), (x + w * 0.6, yy + 3), (x + w, yy - 2)], k=0.6, op=0.45)
