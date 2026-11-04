"""Аня's Klaus drawings (styles/s2-klaus/tools/anya.py) read as shapes: each form the drawing makes is recorded with
its colour and turned into a polygon, so the 3D can be fitted to the drawing's own outlines.
Frames: the head views are 500×600 (front: the face's middle at x=250; profile facing left; chin at y≈368);
the figure is 500×900, the floor at y=846."""
import os, re, sys
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

KLAUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'styles', 's2-klaus', 'tools')
sys.path.insert(0, KLAUS)
import anya  # noqa: E402
from kit import Light  # noqa: E402


class Rec:
    """Stands in for kit.Doc: records every form (outline + base colour) instead of drawing it."""
    def __init__(self):
        self.light = Light(-0.85, -0.5, key='#ffc47a', shade='#3a2a5a'); self.forms = []; self.flat = False

    def form(self, d, base, **k):
        self.forms.append((d, base)); return ''

    def tone(self, *a, **k): return ''
    def clip(self, *a, **k): return 'c'
    def blur(self, *a, **k): return 'b'


def path_points(d, step=2.0):
    """An SVG path (absolute M L C Q Z) as a polyline, a point every ~step units."""
    toks = re.findall(r'[MLCQZmlcqz]|-?\d*\.?\d+(?:e-?\d+)?', d)
    pts, cur, i, cmd = [], None, 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha(): cmd = t; i += 1
        if cmd in 'Zz': i += 0; cmd = None; continue
        n = {'M': 2, 'L': 2, 'C': 6, 'Q': 4}[cmd.upper()]
        a = [float(x) for x in toks[i:i + n]]; i += n
        if cmd == 'M': cur = np.array(a); pts.append(cur); cmd = 'L'; continue
        if cmd == 'L': p = np.array(a); m = max(2, int(np.linalg.norm(p - cur) / step))
        if cmd in 'L':
            for s in np.linspace(0, 1, m)[1:]: pts.append(cur + (p - cur) * s)
            cur = p; continue
        ctrl = [cur] + [np.array(a[k:k + 2]) for k in range(0, n, 2)]
        L = sum(np.linalg.norm(ctrl[k + 1] - ctrl[k]) for k in range(len(ctrl) - 1))
        for s in np.linspace(0, 1, max(3, int(L / step)))[1:]:
            if cmd == 'C':
                p0, p1, p2, p3 = ctrl
                pts.append((1 - s) ** 3 * p0 + 3 * (1 - s) ** 2 * s * p1 + 3 * (1 - s) * s * s * p2 + s ** 3 * p3)
            else:
                p0, p1, p2 = ctrl
                pts.append((1 - s) ** 2 * p0 + 2 * (1 - s) * s * p1 + s * s * p2)
        cur = ctrl[-1]
    return np.array(pts)


def forms(fn, *args):
    r = Rec(); out = []
    fn(r, out, *args)
    return [(path_points(d), c) for d, c in r.forms]


def poly(pts):
    p = Polygon(pts)
    return p if p.is_valid else p.buffer(0)


# the head views, by part
def head_view(which):
    fs = forms(getattr(anya, 'head_' + which), 'calm')
    return {'back': fs[0][0], 'neck': fs[1][0], 'face': fs[2][0], **({'nose': fs[3][0], 'left': fs[4][0], 'right': fs[5][0],
            'lock': fs[6][0]} if which == 'front' else {'ear': fs[3][0], 'hair': fs[4][0]})}


FRONT = head_view('front')
SIDE = head_view('side')
FRONT['hair'] = unary_union([poly(FRONT[k]) for k in ('back', 'left', 'right', 'lock')])
SIDE['hairall'] = unary_union([poly(SIDE[k]) for k in ('back', 'hair')])
FIG = forms(anya.figure)


def span(shape, y):
    """Left and right x of a polygon (or point list) at height y (nan where it isn't)."""
    from shapely.geometry import LineString
    if not hasattr(shape, 'intersection'): shape = poly(shape)
    g = shape.intersection(LineString([(-1e4, y), (1e4, y)]))
    if g.is_empty: return np.nan, np.nan
    b = g.bounds
    return b[0], b[2]


def spans(shape, ys):
    return np.array([span(shape, y) for y in ys])
