"""С14 «Вырезанная бумага» — the shared paper kit.

Everything drawn is a PIECE of paper: a closed outline, a colour, a height above the sheet (`lift`) and a kind of
paper. No strokes anywhere. A picture is a tree (nested lists) of pieces, in the order they are glued: later = on top.

Kinds of paper
  card   — smooth coloured card, cut with scissors: crisp edge, a light rim on the lit side, a cast shadow
  paint  — tissue painted by brush before cutting (Eric Carle): the same, with brush streaks inside
  torn   — torn by hand: a wavering edge with the white core of the sheet showing
  flat   — glued down flush (iris on the eye, teeth in the mouth): no shadow of its own
  tissue — translucent tissue (cheeks, glasses): flush, see-through
  shade  — not paper: the soft dark side of a fold or a curl, laid over the piece below (a gradient, clipped by shape)

lift 1..3 — how high the piece stands above what is under it: the shadow gets longer and softer.
The light is always from the top left; mirror a figure with `mirror()` (in numbers), never with an SVG transform,
so that its shadows keep falling down-right.
"""
import math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHADOW = '#2b1b2c'


class Piece:
    __slots__ = ('pts', 'fill', 'lift', 'kind', 'holes', 'grad', 'stops', 'op', 'var')

    def __init__(self, pts, fill, lift=1, kind='card', holes=None, grad=None, stops=None, op=1, var=0):
        self.pts, self.fill, self.lift, self.kind = pts, fill, lift, kind
        self.holes, self.grad, self.stops, self.op, self.var = holes or [], grad, stops, op, var


def card(pts, fill, lift=1, **k): return Piece(pts, fill, lift, 'card', **k)
def paint(pts, fill, lift=1, var=0, **k): return Piece(pts, fill, lift, 'paint', var=var, **k)
def torn(pts, fill, lift=1, **k): return Piece(pts, fill, lift, 'torn', **k)
def flat(pts, fill, **k): return Piece(pts, fill, 0, 'flat', **k)
def tissue(pts, fill, op=0.55, **k): return Piece(pts, fill, 0, 'tissue', op=op, **k)


def shade(pts, a, b, strength=0.22, color='#1d0f22', holes=None):
    """The dark side of a fold over `pts`: darkest at point a, gone at point b."""
    return Piece(pts, None, 0, 'shade', grad=(a, b), stops=[(0, color, strength), (1, color, 0)], holes=holes)


def light(pts, a, b, strength=0.25):
    return Piece(pts, None, 0, 'shade', grad=(a, b), stops=[(0, '#fff', strength), (1, '#fff', 0)])


# ---------------------------------------------------------------- geometry

def ell(cx, cy, rx, ry=None, rot=0, n=10):
    ry = rx if ry is None else ry
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def strip(path, w, round_ends=False):
    """A strip of paper along a polyline; w — width, a number or one per point. Ends are cut square."""
    n = len(path)
    ws = w if isinstance(w, (list, tuple)) else [w] * n
    L, R = [], []
    for i, (x, y) in enumerate(path):
        x0, y0 = path[max(i - 1, 0)][:2]
        x1, y1 = path[min(i + 1, n - 1)][:2]
        dx, dy = x1 - x0, y1 - y0
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        h = ws[i] / 2
        L.append((x + nx * h, y + ny * h))
        R.append((x - nx * h, y - ny * h))
    if round_ends:
        return L + R[::-1]
    c = lambda p: (p[0], p[1], 1)
    return [c(L[0])] + L[1:-1] + [c(L[-1]), c(R[-1])] + R[1:-1][::-1] + [c(R[0])]


def arc(cx, cy, r, a0, a1, n=8, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


def crescent(x0, y0, x1, y1, bend, thick, n=9):
    """A sliver between two points: bows by `bend` (to the right of the direction), `thick` in the middle."""
    dx, dy = x1 - x0, y1 - y0
    d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d, dx / d
    a, b = [], []
    for i in range(n):
        t = i / (n - 1)
        s = math.sin(math.pi * t)
        px, py = x0 + dx * t, y0 + dy * t
        a.append((px + nx * (bend * s - thick * s / 2), py + ny * (bend * s - thick * s / 2)))
        b.append((px + nx * (bend * s + thick * s / 2), py + ny * (bend * s + thick * s / 2)))
    a[0] = (a[0][0], a[0][1], 1)
    a[-1] = (a[-1][0], a[-1][1], 1)
    return a + b[-2:0:-1]


def corner(p): return (p[0], p[1], 1)


def path_d(pts, k=1.0):
    """Closed curve through the points; a point (x, y, 1) is a corner (a snip of the scissors)."""
    n = len(pts)
    if n < 3:
        return ''
    P = [(p[0], p[1]) for p in pts]
    C = [len(p) > 2 and p[2] for p in pts]
    d = [f'M{P[0][0]:.1f} {P[0][1]:.1f}']
    for i in range(n):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        if C[i] and C[(i + 1) % n]:
            d.append(f'L{p2[0]:.1f} {p2[1]:.1f}')
            continue
        c1 = p1 if C[i] else (p1[0] + (p2[0] - p0[0]) / 6 * k, p1[1] + (p2[1] - p0[1]) / 6 * k)
        c2 = p2 if C[(i + 1) % n] else (p2[0] - (p3[0] - p1[0]) / 6 * k, p2[1] - (p3[1] - p1[1]) / 6 * k)
        d.append(f'C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}')
    return ''.join(d) + 'Z'


# ---------------------------------------------------------------- moving trees of pieces

def _map(tree, f):
    if isinstance(tree, Piece):
        mp = lambda pts: [f(p[0], p[1]) + tuple(p[2:]) for p in pts]
        q = Piece(mp(tree.pts), tree.fill, tree.lift, tree.kind, [mp(h) for h in tree.holes],
                  None, tree.stops, tree.op, tree.var)
        if tree.grad:
            q.grad = tuple(f(*g) for g in tree.grad)
        return q
    return [_map(t, f) for t in tree if t is not None]


def move(tree, dx, dy): return _map(tree, lambda x, y: (x + dx, y + dy))
def scale(tree, s, sy=None, about=(0, 0)):
    sy = s if sy is None else sy
    return _map(tree, lambda x, y: (about[0] + (x - about[0]) * s, about[1] + (y - about[1]) * sy))


def rot(tree, deg, about=(0, 0)):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    ax, ay = about
    return _map(tree, lambda x, y: (ax + (x - ax) * c - (y - ay) * s, ay + (x - ax) * s + (y - ay) * c))


def mirror(tree, about=0):
    """Flip left-right. Shadows are not flipped: they are made when the picture is written."""
    def rev(t):
        if isinstance(t, Piece):
            t.pts = t.pts[::-1]
            return t
        return [rev(u) for u in t]
    return rev(_map(tree, lambda x, y: (2 * about - x, y)))


def rpt(pt, deg, about=(0, 0)):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (about[0] + (pt[0] - about[0]) * c - (pt[1] - about[1]) * s,
            about[1] + (pt[0] - about[0]) * s + (pt[1] - about[1]) * c)


# ---------------------------------------------------------------- the sheet

LIFT = {1: (1.3, 2.2, 1.3, .40), 2: (2.8, 4.6, 2.8, .36), 3: (5.5, 9.5, 5.5, .32)}   # dx, dy, blur, opacity
PAD = {0: 2, 1: 9, 2: 17, 3: 32}


def _shadow(L, src='SourceAlpha'):
    dx, dy, b, op = LIFT[L]
    return (f'<feGaussianBlur in="{src}" stdDeviation="{b}" result="b"/><feOffset in="b" dx="{dx}" dy="{dy}" result="o"/>'
            f'<feFlood flood-color="{SHADOW}" flood-opacity="{op}"/><feComposite in2="o" operator="in" result="sh"/>'
            f'<feOffset in="{src}" dx=".7" dy="1" result="t0"/>'
            f'<feFlood flood-color="{SHADOW}" flood-opacity=".5"/><feComposite in2="t0" operator="in" result="th"/>')


_RIM = ('<feOffset in="SourceAlpha" dx=".9" dy="1.1" result="h0"/>'
        '<feComposite in="SourceAlpha" in2="h0" operator="out" result="h1"/>'
        '<feFlood flood-color="#fff" flood-opacity=".42"/><feComposite in2="h1" operator="in" result="hl"/>')

STREAKS = [('0.012 0.22', 3), ('0.2 0.014', 7), ('0.035 0.06', 11), ('0.016 0.3', 23)]   # brush direction, seed


def filters():
    f = []
    head = lambda i: f'<filter id="{i}" x="0" y="0" width="1" height="1" color-interpolation-filters="sRGB">'
    for L in (1, 2, 3):
        f.append(head(f'card{L}') + _shadow(L) + _RIM +
                 '<feMerge><feMergeNode in="sh"/><feMergeNode in="th"/><feMergeNode in="SourceGraphic"/>'
                 '<feMergeNode in="hl"/></feMerge></filter>')
        for v, (bf, seed) in enumerate(STREAKS):
            f.append(head(f'paint{L}_{v}') + _shadow(L) + _RIM +
                     f'<feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="3" seed="{seed}"/>'
                     '<feColorMatrix values="2.6 0 0 0 -0.8  2.6 0 0 0 -0.8  2.6 0 0 0 -0.8  0 0 0 0 1" result="n"/>'
                     '<feComposite in="SourceGraphic" in2="n" operator="arithmetic" k1="0.46" k2="0.80" k3="0" k4="0"/>'
                     '<feComposite in2="SourceAlpha" operator="in" result="pt"/>'
                     '<feMerge><feMergeNode in="sh"/><feMergeNode in="th"/><feMergeNode in="pt"/>'
                     '<feMergeNode in="hl"/></feMerge></filter>')
        # torn: the coloured face of the sheet tears off unevenly and bares the white core along the edge
        f.append(head(f'torn{L}') +
                 '<feTurbulence type="fractalNoise" baseFrequency="0.07" numOctaves="3" seed="5" result="n1"/>'
                 '<feTurbulence type="fractalNoise" baseFrequency="0.11" numOctaves="2" seed="17" result="n2"/>'
                 '<feDisplacementMap in="SourceGraphic" in2="n1" scale="9" xChannelSelector="R" yChannelSelector="G" result="face"/>'
                 '<feMorphology in="SourceAlpha" operator="dilate" radius="2.2" result="fat"/>'
                 '<feDisplacementMap in="fat" in2="n2" scale="8" xChannelSelector="G" yChannelSelector="R" result="core0"/>'
                 '<feFlood flood-color="#f7f2e7"/><feComposite in2="core0" operator="in" result="core1"/>'
                 '<feMerge><feMergeNode in="core1"/><feMergeNode in="face"/></feMerge>'
                 '<feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 1 0" result="whole"/>'
                 '<feColorMatrix in="whole" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="wa"/>' +
                 _shadow(L, 'wa') +
                 '<feMerge><feMergeNode in="sh"/><feMergeNode in="th"/><feMergeNode in="whole"/></feMerge></filter>')
    return ''.join(f)


class Doc:
    """A sheet. add(tree, x, y, s) glues a tree of pieces at a place and size; text() adds a label."""

    def __init__(self, w, h, bg='#e9dfcb', grain=True):
        self.w, self.h, self.bg, self.grain = w, h, bg, grain
        self.body, self.defs, self.over, self.n = [], [], [], 0

    def _piece(self, p):
        d = path_d(p.pts) + ''.join(path_d(h) for h in p.holes)
        rule = ' fill-rule="evenodd"' if p.holes else ''
        if p.kind == 'shade':
            self.n += 1
            (x1, y1), (x2, y2) = p.grad
            st = ''.join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in p.stops)
            self.defs.append(f'<linearGradient id="g{self.n}" gradientUnits="userSpaceOnUse" x1="{x1:.1f}" '
                             f'y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}">{st}</linearGradient>')
            return f'<path d="{d}" fill="url(#g{self.n})"{rule}/>'
        if p.kind in ('flat', 'tissue'):
            op = f' opacity="{p.op}"' if p.op != 1 else ''
            return f'<path d="{d}" fill="{p.fill}"{rule}{op}/>'
        xs = [q[0] for q in p.pts]
        ys = [q[1] for q in p.pts]
        pad = PAD[p.lift] + (12 if p.kind == 'torn' else 0)
        box = (f'<rect x="{min(xs) - pad:.0f}" y="{min(ys) - pad:.0f}" width="{max(xs) - min(xs) + 2 * pad:.0f}" '
               f'height="{max(ys) - min(ys) + 2 * pad:.0f}" fill="none"/>')
        fid = f'{p.kind}{p.lift}' + (f'_{p.var % len(STREAKS)}' if p.kind == 'paint' else '')
        op = f' opacity="{p.op}"' if p.op != 1 else ''
        return f'<g filter="url(#{fid})"{op}><path d="{d}" fill="{p.fill}"{rule}/>{box}</g>'

    def _tree(self, t):
        if isinstance(t, Piece):
            return self._piece(t)
        return ''.join(self._tree(u) for u in t if u is not None)

    def add(self, tree, x=0, y=0, s=1):
        tf = f' transform="translate({x},{y}) scale({s})"' if (x, y, s) != (0, 0, 1) else ''
        self.body.append(f'<g{tf}>{self._tree(tree)}</g>')

    def text(self, x, y, s, size=22, anchor='middle', fill='#5b4a3c'):
        self.over.append(f'<text x="{x}" y="{y}" font-family="Georgia, \'PT Serif\', serif" font-size="{size}" '
                         f'text-anchor="{anchor}" fill="{fill}">{s}</text>')

    def svg(self):
        w, h = self.w, self.h
        grain = (f'<filter id="grain" filterUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}" '
                 'color-interpolation-filters="sRGB">'
                 '<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="2"/>'
                 '<feColorMatrix values="1.5 0 0 0 -0.25  1.5 0 0 0 -0.25  1.5 0 0 0 -0.25  0 0 0 0 1" result="fine"/>'
                 '<feTurbulence type="fractalNoise" baseFrequency="0.9 0.05" numOctaves="2" seed="8"/>'
                 '<feColorMatrix values="1.2 0 0 0 -0.1  1.2 0 0 0 -0.1  1.2 0 0 0 -0.1  0 0 0 0 1" result="fibre"/>'
                 '<feComposite in="SourceGraphic" in2="fine" operator="arithmetic" k1="0.24" k2="0.88" k3="0" k4="0" result="a"/>'
                 '<feComposite in="a" in2="fibre" operator="arithmetic" k1="0.12" k2="0.94" k3="0" k4="0"/>'
                 '</filter>')
        g0 = '<g filter="url(#grain)">' if self.grain else '<g>'
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
                f'<defs>{filters()}{grain}{"".join(self.defs)}</defs>'
                f'{g0}<rect width="{w}" height="{h}" fill="{self.bg}"/>{"".join(self.body)}</g>{"".join(self.over)}</svg>')

    def save(self, name):
        with open(os.path.join(ROOT, 'svg', name + '.svg'), 'w') as fh:
            fh.write(self.svg())
        print('svg', name)


def rnd(seed): return random.Random(seed)


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(a[i] + (b[i] - a[i]) * t):02x}' for i in range(3))


def dark(c, t=0.2): return mix(c, '#2b1b2c', t)
def lite(c, t=0.2): return mix(c, '#fff6e6', t)
