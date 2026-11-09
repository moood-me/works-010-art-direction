"""The body: a torso lofted from horizontal rings, limbs as tapered tubes along a posed skeleton, garments as
slightly bigger lofts and tubes over them, hands and shoes as small built forms. Everything ends as flat shapes,
drawn far-to-near with one shadow tone and an outline.

Model space is centimetres, y up, +x is the character's left (the viewer's right when it faces us), +z forward."""
import math
import numpy as np
from shapely.ops import unary_union
from geo import hull_union, tube, smooth, poly


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
        """a hand: a palm, four fingers side by side and a thumb. Returns a list of flat pieces in drawing order
        (far to near) — each drawn with its own line, so the fingers part from each other as in a drawing."""
        B = self.B
        s = 1 if side == 'l' else -1
        w, h = self.J['wr' + side], self.J['hd' + side]
        ax = unit(h - w)
        L = B['hand']
        pal = self.pose['arm' + side].get('palm', (0, 0, 1))
        pn = unit(np.array(pal) * [s, 1, 1])
        pn = unit(pn - ax * np.dot(pn, ax))
        sv = unit(np.cross(ax, pn)) * s          # across the knuckles, from the little finger to the index
        r = B['hand_r']
        pieces = []
        if kind == 'pocket':      # the hand is inside a pocket: nothing to draw
            return []
        if kind == 'fist':
            k1 = w + ax * L * 0.42
            palm = tube(view, [w, k1], [r * 0.8, r * 1.05])
            knuck = tube(view, [k1 - sv * r * 0.7 + pn * r * 0.3, k1 + sv * r * 0.7 + pn * r * 0.3], [r * 0.62, r * 0.62])
            thumb = tube(view, [w + ax * L * 0.15 + sv * r * 0.8, k1 + sv * r * 0.5 + pn * r * 0.9], [r * 0.42, r * 0.36])
            return [unary_union([palm, knuck]), thumb]
        curl = {'relaxed': 0.55, 'open': 0.12, 'hold': 0.95}.get(kind, 0.5)
        k1 = w + ax * L * 0.47
        palm = tube(view, [w, k1 - ax * r * 0.3], [r * 0.78, r * 1.0])
        palm = unary_union([palm, tube(view, [k1 - sv * r * 0.65, k1 + sv * r * 0.65], [r * 0.55] * 2)])
        fingers = []
        for f, (off, ln) in enumerate(((-0.72, 0.36), (-0.24, 0.44), (0.24, 0.47), (0.72, 0.42))):
            base = k1 + sv * r * off
            d1 = unit(ax + pn * curl * 0.5 + sv * off * 0.06)
            p1 = base + d1 * L * ln * 0.45
            d2 = unit(ax + pn * curl * 1.6)
            p2 = p1 + d2 * L * ln * 0.32
            d3 = unit(ax * (1 - curl) + pn * curl * 2.2)
            p3 = p2 + d3 * L * ln * 0.23
            g = tube(view, [base, p1, p2, p3], [r * 0.30, r * 0.28, r * 0.26, r * 0.23])
            dep = float(view.depth(np.array([p2]))[0])
            fingers.append((dep, g))
        th0 = w + ax * L * 0.12 + sv * r * 0.75
        t1 = th0 + unit(ax * 0.7 + sv * 0.5 + pn * 0.4) * L * 0.26
        t2 = t1 + unit(ax * 0.8 + pn * 0.6 * (0.5 + curl)) * L * 0.2
        thumb = tube(view, [th0, t1, t2], [r * 0.42, r * 0.33, r * 0.26])
        tdep = float(view.depth(np.array([t1]))[0])
        pdep = float(view.depth(np.array([k1]))[0])
        items = [(pdep, palm), (tdep, thumb)] + fingers
        items.sort(key=lambda x: x[0])
        return [g for _, g in items]

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
