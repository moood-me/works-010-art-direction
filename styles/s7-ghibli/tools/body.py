"""The body: a torso lofted from horizontal rings, limbs as tapered tubes along a posed skeleton, garments as
slightly bigger lofts and tubes over them, hands and shoes as small built forms. Everything ends as flat shapes,
drawn far-to-near with one shadow tone and an outline.

Model space is centimetres, y up, +x is the character's left (the viewer's right when it faces us), +z forward."""
import math
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
from geo import (poly, hull_union, tube, tube2d, ribbon, bezier, spline, shift, smooth, polys, lines, resample)
from svgdoc import INK, mix, shade


def table(pairs):
    from head import table as t
    return t(pairs)


def unit(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


class Loft:
    """rings along y: each ring (y, a, zf, zb[, x0, z0]) — half width, front, back, centre offsets; exponent n."""

    def __init__(self, rings, n=2.4, wave=None):
        """wave=(amp, count, y_start): soft folds that grow toward the bottom (a skirt's hem)."""
        self.wave = wave
        R = sorted(rings, key=lambda r: r[0])
        self.y0, self.y1 = R[0][0], R[-1][0]
        cols = list(zip(*[(r + (0.0, 0.0))[:6] if len(r) < 6 else r for r in R]))
        self.f = [table(list(zip(cols[0], c))) for c in cols[1:]]
        self.n = n

    def at(self, y):
        return [float(f(y)) for f in self.f]       # a, zf, zb, x0, z0

    def pt(self, t, y, push=0.0):
        """surface point at azimuth t (rad, 0 front, +pi/2 the character's left) and height y."""
        a, zf, zb, x0, z0 = self.at(y)
        if self.wave:
            amp, cnt, ys = self.wave
            push += amp * math.sin(cnt * t + 0.7) * min(max((ys - y) / max(ys - self.y0, 1e-3), 0), 1) ** 1.5
        zm = (zf + zb) / 2
        s, c = math.sin(t), math.cos(t)
        x = (a + push) * math.copysign(abs(s) ** (2 / self.n), s)
        d = (zf - zm + push) if c > 0 else (zm - zb + push)
        return np.array([x0 + x, y, z0 + zm + d * math.copysign(abs(c) ** (2 / self.n), c)])

    def ring(self, y, nt=48, push=0.0):
        return np.array([self.pt(t, y, push) for t in np.linspace(0, 2 * np.pi, nt, endpoint=False)])

    def shape(self, view, y0=None, y1=None, n=40, push=0.0):
        y0 = self.y0 if y0 is None else y0
        y1 = self.y1 if y1 is None else y1
        ys = np.linspace(y0, y1, n)
        return smooth(hull_union([view.xy(self.ring(y, push=push)) for y in ys]), 0.6)

    def region(self, view, ts, ys, push=0.3):
        """a patch of the surface bounded by a curve given as azimuths and heights → flat polygon."""
        return poly(view.xy(np.array([self.pt(t, y, push) for t, y in zip(ts, ys)]))).buffer(0)

    def curve(self, view, ts, ys, push=0.3):
        return view.xy(np.array([self.pt(t, y, push) for t, y in zip(ts, ys)]))

    def facing(self, view, t, y):
        e = 0.02
        p = self.pt(t, y)
        a = self.pt(t + e, y) - self.pt(t - e, y)
        b = self.pt(t, y + 1) - self.pt(t, y - 1)
        n = unit(np.cross(a, b))
        return float(view.dir(n[None])[0, 2])


class Figure:
    """A posed character: the skeleton, the drawable parts and how to draw them."""

    def __init__(self, B, pose):
        self.B, self.pose = B, pose
        self.J = self.skeleton()

    # ---------------------------------------------------------------- skeleton
    def skeleton(self):
        B, p = self.B, self.pose
        J = {}
        lean = p.get('lean', 0.0)                       # forward lean of the upper body (cm at the shoulders)
        J['pelvis'] = np.array([p.get('hip_shift', 0.0), B['hip_y'], 0.0])
        sy = B['shoulder'][1]
        for s, nm in ((1, 'l'), (-1, 'r')):
            J['sh' + nm] = np.array([s * B['shoulder'][0], sy + p.get('shrug', 0.0), B['shoulder'][2] + lean])
            a = p['arm' + nm]
            J['el' + nm] = J['sh' + nm] + unit(np.array(a['upper']) * [s, 1, 1]) * B['upper']
            J['wr' + nm] = J['el' + nm] + unit(np.array(a['fore']) * [s, 1, 1]) * B['fore']
            J['hd' + nm] = J['wr' + nm] + unit(np.array(a.get('hand', a['fore'])) * [s, 1, 1]) * B['hand']
            l = p['leg' + nm]
            J['hp' + nm] = np.array([s * B['hip_x'] + p.get('hip_shift', 0.0), B['hip_y'], 0.0])
            J['kn' + nm] = J['hp' + nm] + unit(np.array(l['thigh']) * [s, 1, 1]) * B['thigh']
            J['an' + nm] = J['kn' + nm] + unit(np.array(l['shin']) * [s, 1, 1]) * B['shin']
        J['neck0'] = np.array([0.0, B['neck'][0], B['neck'][2] + lean * 0.9])
        J['neck1'] = np.array([0.0, B['neck'][1], B['neck'][3] + lean * 1.2 + p.get('head_fwd', 0.0)])
        hc = B['head_c']
        J['head'] = np.array([hc[0], hc[1], hc[2] + lean * 1.2 + p.get('head_fwd', 0.0)]) + np.array(p.get('head_off', (0, 0, 0)))
        return J

    def torso_loft(self, push=0.0):
        B, lean = self.B, self.pose.get('lean', 0.0)
        y0, y1 = B['torso'][0][0], B['torso'][-1][0]
        rings = []
        for r in B['torso']:
            y, a, zf, zb = r[:4]
            f = (y - y0) / (y1 - y0)
            rings.append((y, a + push, zf + push, zb - push, self.pose.get('hip_shift', 0.0) * (1 - f), lean * f ** 1.5))
        return Loft(rings, B.get('torso_n', 2.4))

    # ---------------------------------------------------------------- limbs
    def limb(self, names, radii, n=30, upto=1.0, start=0.0):
        P = np.array([self.J[k] for k in names])
        R = np.array(radii, float)
        d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
        t = np.linspace(start * d[-1], upto * d[-1], n)
        pts = np.stack([np.interp(t, d, P[:, i]) for i in range(3)], 1)
        rr = np.interp(t, d, R) if len(R) == len(P) else np.interp(t, np.linspace(0, d[-1], len(R)), R)
        return pts, rr

    def arm_shape(self, view, side, ease=0.0, upto=1.0, start=0.0):
        B = self.B
        pts, rr = self.limb(['sh' + side, 'el' + side, 'wr' + side], B['arm_r'], upto=upto, start=start)
        return tube(view, pts, rr + ease), pts

    def leg_shape(self, view, side, ease=0.0, upto=1.0, start=0.0):
        B = self.B
        pts, rr = self.limb(['hp' + side, 'kn' + side, 'an' + side], B['leg_r'], upto=upto, start=start)
        return tube(view, pts, rr + ease), pts

    # ---------------------------------------------------------------- hands and feet
    def hand(self, view, side, kind='relaxed'):
        """a simple hand: palm, fingers held together and slightly curled, a thumb apart."""
        B = self.B
        s = 1 if side == 'l' else -1
        w, h = self.J['wr' + side], self.J['hd' + side]
        ax = unit(h - w)
        L = B['hand']
        pal = self.pose['arm' + side].get('palm', (0, 0, 1))     # where the palm faces (model, before mirroring)
        pn = unit(np.array(pal) * [s, 1, 1])
        side_v = unit(np.cross(ax, pn))
        r = B['hand_r']
        if kind == 'fist':
            pts = [w, w + ax * L * 0.45]
            return unary_union([tube(view, pts, [r * 0.8, r * 1.15]), tube(view, [w + ax * L * 0.3 + side_v * r * 0.6 * s,
                                                                               w + ax * L * 0.45 + pn * r * 0.6], [r * 0.45, r * 0.4])]), []
        curl = 0.25 if kind == 'relaxed' else 0.05
        k1 = w + ax * L * 0.48
        tip = k1 + unit(ax + pn * curl * 2) * L * 0.5
        palm = tube(view, [w, k1], [r * 0.75, r])
        fingers = tube(view, [k1, k1 + unit(ax + pn * curl) * L * 0.28, tip], [r * 0.95, r * 0.8, r * 0.55])
        th0 = w + ax * L * 0.15 + side_v * r * 0.7 * s * -1
        thumb = tube(view, [th0, th0 + unit(ax * 0.8 + pn * 0.5 - side_v * 0.3 * s) * L * 0.38], [r * 0.45, r * 0.32])
        g = unary_union([palm, fingers, thumb])
        # a line between fingers: two short marks near the tip
        marks = []
        for f in (-0.3, 0.3):
            a = k1 + unit(ax + pn * curl) * L * 0.12 + side_v * r * f
            b = tip + side_v * r * f * 0.7 - ax * L * 0.06
            marks.append(view.xy(np.array([a, b])))
        return g, marks

    def shoe(self, view, side, B_shoe):
        an = self.J['an' + side]
        s = 1 if side == 'l' else -1
        L, r = B_shoe['len'], B_shoe['r']
        out = math.radians(B_shoe.get('out', 10))
        fwd = np.array([s * math.sin(out), 0, math.cos(out)])
        heel = an + np.array([0, -r * 0.6, 0]) - fwd * L * 0.18
        toe = an + np.array([0, -r * 0.8, 0]) + fwd * L * 0.78
        g = unary_union([tube(view, [heel, an + fwd * L * 0.25 + [0, -r * 0.3, 0], toe], [r * 0.95, r * 1.05, r * 0.75]),
                         tube(view, [an + [0, r * 0.6, 0], an], [r * 0.85, r * 0.95])])
        floor = view.xy(np.array([[0, 0, 0]]))[0][1]
        # flatten the sole on the floor
        from shapely.geometry import box
        g = g.intersection(box(-1e4, -1e4, 1e4, view.xy(np.array([an * [1, 0, 1]]))[0][1] + 0.3))
        return g


def draw_part(d, g, c, light=(-1, -0.6), k=6.0, extra=None, line=True, w=None):
    """a flat shape with its one shadow tone (the side away from the light, plus any cast shadows)."""
    if g is None or g.is_empty:
        return
    sh = g.difference(shift(g, light[0] * k, light[1] * k))
    if extra is not None:
        sh = sh.union(extra)
    d.fill(g, c)
    d.fill(smooth(sh, 0.4).intersection(g), shade(c))
    if line:
        d.outline(g, w)
