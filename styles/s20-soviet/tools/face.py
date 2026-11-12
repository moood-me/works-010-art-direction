"""С20 — the head: a caricature built from a few numbers.

A head lives in its own units: centre (0, 0), crown near y = -60, chin near y = +45. View: 'front', 'three' (three
quarters, facing the viewer's right) or 'side' (profile, facing right). The rules of the style it follows:
  * the skull is one simple, bold shape — a box, an egg, a pear — set by half-widths at a few heights (`rows`);
  * the face is the paper (unpainted), with a crayon blush;
  * the nose is the biggest feature and lies OVER the contour in three-quarters and profile;
  * eyes are small: a ring with a dot, or a dot alone, set close to the nose; the lid is a line that cuts the ring;
  * brows are short heavy strokes that do most of the acting; the mouth is a short line or an open shape with
    teeth and tongue.
"""
import math
from kit import ink, paint, form, dot, blush, cr, ell, arc, move, INK, SKIN, PAPER, rng

VIEWS = ('front', 'three', 'side')

# expression = offsets for brows, eyes, mouth; a character overrides any of these
EXPR = {
    'calm':     dict(brow=0, tilt=0, eye='ring', lid=0.0, mouth='line', curve=0.15),
    'joy':      dict(brow=-5, tilt=-0.1, eye='happy', lid=0, mouth='open', curve=1.0, open=0.8),
    'surprise': dict(brow=-12, tilt=0.15, eye='wide', lid=0, mouth='o', curve=0, open=0.9),
    'sadness':  dict(brow=-3, tilt=0.45, eye='ring', lid=0.45, look=(0, 0.6), mouth='line', curve=-0.7),
    'anger':    dict(brow=5, tilt=-0.5, eye='ring', lid=0.35, mouth='teeth', curve=-0.5, open=0.45),
}


def _skull(rows, view, round_=1.0):
    """rows: [(y, halfwidth)] from crown to chin. Returns a closed outline in head space."""
    top, bot = rows[0][0] - 3, rows[-1][0] + 2.5
    if view == 'front':
        right = [(w, y) for y, w in rows]
        left = [(-w, y) for y, w in rows[::-1]]
        return [(0, top)] + right + [(0, bot)] + left
    if view == 'three':
        right = [(w * 0.86 + 6, y) for y, w in rows]
        left = [(-w * 0.94 + 4, y) for y, w in rows[::-1]]
        return [(4, top)] + right + [(rows[-1][1] * 0.5 + 6, bot)] + left
    # side: the back of the head is rounder and deeper, the front follows the face line
    right = [(w * 0.9 + 10, y) for y, w in rows]
    left = [(-w * 1.08 + 6, y) for y, w in rows[::-1]]
    return [(2, top)] + right + [(rows[-1][1] * 0.7 + 8, bot)] + left


class Head:
    """A head. Characters give the numbers; `draw(view, expr)` returns the layers."""

    def __init__(self, rows, eye_y=-8, eye_gap=17, eye_r=5.5, nose='button', nose_s=1.0, nose_y=6,
                 mouth_y=22, mouth_w=12, brow_y=-20, brow_len=11, brow_lw=3.2, ear=(0, 10, 9),
                 skin=SKIN, blush_r=9, blush_op=0.75, lw=2.3, expr=None, eye_kind='ring', lashes=0,
                 nose_fill=None, chin_line=None, cheek_y=12, prof=None, brow_fill=None):
        self.rows, self.eye_y, self.eye_gap, self.eye_r = rows, eye_y, eye_gap, eye_r
        self.nose, self.nose_s, self.nose_y = nose, nose_s, nose_y
        self.mouth_y, self.mouth_w = mouth_y, mouth_w
        self.brow_y, self.brow_len, self.brow_lw = brow_y, brow_len, brow_lw
        self.ear, self.skin, self.blush_r, self.blush_op, self.lw = ear, skin, blush_r, blush_op, lw
        self.expr = expr or {}
        self.eye_kind, self.lashes = eye_kind, lashes
        self.nose_fill = nose_fill or skin
        self.cheek_y = cheek_y
        self.prof = prof
        self.brow_fill = brow_fill

    # where things sit, per view: x of the eyes, nose, mouth
    def layout(self, view):
        g = self.eye_gap
        if view == 'front':
            return dict(eyes=[(-g, 1.0), (g, 1.0)], nose=0, mouth=0, ear=[-1, 1], cheeks=[-g - 3, g + 3])
        if view == 'three':
            w = max(w for _, w in self.rows)
            c = w * 0.38
            return dict(eyes=[(c - g * 0.72, 0.82), (c + g * 0.95, 1.0)], nose=c + g * 0.25,
                        mouth=c + g * 0.2, ear=[-1], cheeks=[c - g * 0.95, c + g * 0.95])
        W = self.front_x()
        return dict(eyes=[(W - 13, 0.95)], nose=W - 3, mouth=W - 3, ear=[0], cheeks=[W - 22])

    def ex(self, name):
        e = dict(EXPR[name])
        e.update(self.expr.get(name, {}))
        return e

    def front_x(self):
        return max(w for _, w in self.rows) * 0.9 + 6

    def outline(self, view):
        if view != 'side':
            return _skull(self.rows, view)
        # profile: the back of the skull from the rows, the face line from the features
        W = self.front_x()
        top, chin = self.rows[0][0], self.rows[-1][0]
        back = [(-w * 1.08 + 4, y) for y, w in self.rows[::-1]]
        ey, ny, my = self.eye_y, self.nose_y, self.mouth_y
        p = self.prof or {}
        jaw = p.get('jaw', 0.55)
        face = [(W * 0.55, top - 1), (W * 0.92, top + (ey - top) * 0.45), (W + p.get('brow', 2), ey - 9),
                (W - 1.5, ey + 1), (W + p.get('nose', 0), ny + 5), (W + p.get('lip', 0), my - 3),
                (W - 1.5 + p.get('mouth', 0), my + 1), (W + p.get('lip2', 0), my + 5), (W - 4 + p.get('dent', 0), my + 10),
                (W - 1 + p.get('chin', 0), chin - 4), (W * jaw, chin + 3)]
        return back[:-1] + [(back[-1][0] * 0.6, top - 3)] + face

    def face(self, view):
        return form(self.outline(view), self.skin, lw=self.lw, tex='flat' if self.skin == SKIN else 'brush')

    def ears(self, view, which='near'):
        ex, ey, er = self.ear
        if er <= 0:
            return ''
        L = self.layout(view)
        w = dict((round(y), w) for y, w in self.rows)
        # half width at ear height
        hw = min(self.rows, key=lambda r: abs(r[0] - ey))[1]
        s = ''
        if view == 'front':
            for sgn in (-1, 1):
                x = sgn * (hw - 1)
                pts = [(x, ey - er), (x + sgn * er * 0.75, ey - er * 0.8), (x + sgn * er * 0.95, ey),
                       (x + sgn * er * 0.6, ey + er * 0.85), (x, ey + er * 0.7)]
                s += paint(pts, self.skin, 'flat', off=False) + ink(pts, self.lw * 0.9)
                s += ink([(x + sgn * er * 0.25, ey - er * 0.4), (x + sgn * er * 0.55, ey), (x + sgn * er * 0.2, ey + er * 0.35)],
                         self.lw * 0.6)
        elif view == 'three':
            x = -hw * 0.94 + 4 + hw * 0.32
            pts = ell(x, ey, er * 0.7, er, 10)
            s += form(pts, self.skin, lw=self.lw * 0.85, tex='flat')
            s += ink([(x + er * 0.15, ey - er * 0.5), (x - er * 0.35, ey), (x + er * 0.1, ey + er * 0.45)], self.lw * 0.6)
        else:
            x = -hw * 0.15
            pts = ell(x, ey, er * 0.75, er * 1.1, 10)
            s += form(pts, self.skin, lw=self.lw * 0.85, tex='flat')
            s += ink([(x - er * 0.1, ey - er * 0.55), (x + er * 0.35, ey), (x, ey + er * 0.5)], self.lw * 0.6)
        return s

    # ---------------------------------------------------------------- features
    def eye(self, x, y, k, e, view, side):
        r = self.eye_r * k
        kind = e.get('eye', 'ring')
        if kind == 'ring' and self.eye_kind != 'ring':
            kind = self.eye_kind
        look = e.get('look', (0.25 if view != 'front' else 0, 0.1))
        s = ''
        lw = self.lw * 0.8
        if kind == 'happy':
            return ink(arc(x, y + r * 0.4, r * 1.05, r * 0.9, math.pi * 1.1, math.pi * 1.9, 7), self.lw * 1.15, taper=0.3)
        if kind == 'shut':
            return ink(arc(x, y - r * 0.3, r * 1.05, r * 0.7, math.pi * 0.15, math.pi * 0.85, 7), self.lw, taper=0.3)
        if kind == 'dot':
            rr = r * 0.48
            s += dot(x + look[0] * r * 0.3, y + look[1] * r * 0.3, rr)
            if e.get('lid', 0) > 0.2:
                s += ink([(x - r * 0.9, y - r * 0.55), (x + r * 0.9, y - r * 0.45 - e.get('tilt_lid', 0))], lw)
            return s
        if kind == 'wide':
            r *= 1.25
        rx, ry = r * (0.82 if view == 'side' else 0.9), r * 1.08
        ring = ell(x, y, rx, ry, 12)
        s += paint(ring, '#fffaf0', 'flat', off=False)
        pr = r * (0.42 if kind != 'wide' else 0.3)
        s += dot(x + look[0] * (rx - pr), y + look[1] * (ry - pr) * 0.8, pr)
        lid = e.get('lid', 0)
        if lid > 0:
            # the lid: cover the top of the ring with skin, a heavy line across
            t = e.get('lidtilt', 0.0) * side
            yl = y - ry + 2 * ry * lid
            cover = [(x - rx - 2, y - ry - 3), (x + rx + 2, y - ry - 3), (x + rx + 2, yl + t * rx), (x - rx - 2, yl - t * rx)]
            s += paint(cover, self.skin, 'flat', off=False, smooth=False)
            s += ink(arc(x, y, rx, ry, math.pi * 1.0, math.pi * 2.0, 9)[1:-1], lw * 0.7, taper=0.4) if lid < 0.5 else ''
            s += ink([(x - rx * 1.15, yl - t * rx + 0.5), (x, yl - 0.6), (x + rx * 1.15, yl + t * rx + 0.5)], self.lw * 1.05)
            s += ink(arc(x, y, rx, ry, 0.0, math.pi, 9), lw * 0.85, taper=0.3)
        else:
            s += ink(ring, lw, closed=True, weight=0.6)
        if self.lashes:
            o = 1 if view != 'front' else side
            for i in range(self.lashes):
                a = -0.35 - 0.33 * i
                px, py = x + o * rx * math.cos(a), y + ry * math.sin(a) - (2 * ry * lid if lid > 0 else 0) * 0
                s += ink([(px, py), (px + o * r * 0.55 * math.cos(a - 0.2), py + r * 0.55 * math.sin(a - 0.4))],
                         self.lw * 0.75, taper=0.4)
        return s

    def brow(self, x, y, e, side, k=1.0):
        L = self.brow_len * k
        t = e.get('tilt', 0) * side   # positive: inner end up (sad)
        b = e.get('brow', 0)
        ang_in = -t * L * 0.9
        pts = [(x - side * L, y + b - ang_in * 0.0 + e.get('brow_out', 0)),
               (x, y + b - 1.5 - ang_in * 0.5),
               (x + side * L * 0.95, y + b - ang_in)]
        if side < 0:
            pts = pts[::-1]
        if self.brow_fill:
            # a bushy brow: a tuft of paint with a ragged edge, outlined
            th = self.brow_lw * 1.6
            top = [(x, y - th * (0.9 if i == 1 else 0.5)) for i, (x, y) in enumerate(pts)]
            bot = [(x, y + th * 0.45) for x, y in pts[::-1]]
            tuft = [top[0], top[1], top[2], (top[2][0] + side * 3, top[2][1] + 3), bot[0], bot[1], bot[2]]
            return form(tuft, self.brow_fill, lw=self.lw * 0.75, tex='crayon', off=False)
        return ink(pts, self.brow_lw, taper=0.35, weight=0.2)

    def nose_draw(self, view, x0):
        s, y = self.nose_s, self.nose_y
        k = self.nose
        lw = self.lw
        if view == 'front':
            if k in ('potato', 'bulb'):
                pts = ell(x0, y + 2 * s, 9 * s, 8 * s, 10)
                return (paint(pts, self.nose_fill, 'flat', off=False) +
                        ink(arc(x0, y + 2 * s, 9 * s, 8 * s, math.pi * 0.95, math.pi * 2.25, 9), lw) +
                        ink([(x0 - 4 * s, y + 7 * s), (x0 - 2 * s, y + 9.5 * s)], lw * 0.6, taper=0.4))
            if k == 'wedge':
                return ink([(x0 - 1, y - 18 * s), (x0 + 1.5 * s, y - 4 * s), (x0 + 5 * s, y + 6 * s),
                            (x0 + 1 * s, y + 8 * s), (x0 - 3 * s, y + 6.5 * s)], lw, taper=0.25)
            if k == 'long':
                return ink([(x0 - 2, y - 16 * s), (x0 + 1 * s, y + 2 * s), (x0 + 4 * s, y + 9 * s),
                            (x0 - 1 * s, y + 10 * s)], lw, taper=0.25)
            # button / small
            return ink([(x0 + 2 * s, y - 5 * s), (x0 + 4 * s, y + 2 * s), (x0 + 0.5 * s, y + 4 * s),
                        (x0 - 3 * s, y + 3 * s)], lw, taper=0.3)
        # three and side: the nose sticks out to the right, over the contour
        if k in ('potato', 'bulb'):
            pts = [(x0 - 6 * s, y - 14 * s), (x0 + 1 * s, y - 6 * s), (x0 + 8 * s, y - 1 * s), (x0 + 11 * s, y + 6 * s),
                   (x0 + 6 * s, y + 12 * s), (x0 - 2 * s, y + 11 * s), (x0 - 7 * s, y + 6 * s)]
            return form(pts, self.nose_fill, lw=lw, tex='flat', gap=(0.0, 0.08)) + \
                ink([(x0 - 4 * s, y + 6 * s), (x0 - 1 * s, y + 8 * s)], lw * 0.6, taper=0.4)
        if k == 'wedge':
            pts = [(x0 - 5 * s, y - 20 * s), (x0 + 3 * s, y - 6 * s), (x0 + 13 * s, y + 7 * s),
                   (x0 + 2 * s, y + 9 * s), (x0 - 4 * s, y + 7 * s)]
            return paint(pts, self.nose_fill, 'flat', off=False) + ink(pts, lw, taper=0.2)
        if k == 'long':
            pts = [(x0 - 4 * s, y - 18 * s), (x0 + 3 * s, y - 2 * s), (x0 + 9 * s, y + 8 * s),
                   (x0 + 1 * s, y + 10 * s), (x0 - 3 * s, y + 8 * s)]
            return paint(pts, self.nose_fill, 'flat', off=False) + ink(pts, lw, taper=0.2)
        pts = [(x0 - 3 * s, y - 8 * s), (x0 + 3 * s, y - 1 * s), (x0 + 7 * s, y + 4 * s),
               (x0 + 2 * s, y + 6.5 * s), (x0 - 3 * s, y + 5 * s)]
        return paint(pts, self.nose_fill, 'flat', off=False) + ink(pts, lw, taper=0.25)

    def mouth(self, view, x0, e):
        y, w = self.mouth_y, self.mouth_w
        kind = e.get('mouth', 'line')
        c = e.get('curve', 0)
        lw = self.lw
        if view == 'three':
            xl, xr = x0 - w * 0.75, x0 + w * 0.85
        elif view == 'side':
            xl, xr = x0 - w * 0.55, x0 + w * 0.15
        else:
            xl, xr = x0 - w, x0 + w
        sk = e.get('skew', 0)
        if kind == 'line':
            return ink([(xl, y - c * 4 - sk), ((xl + xr) / 2, y + c * 3), (xr, y - c * 4 + sk)], lw, taper=0.35)
        if kind == 'smirk':
            return ink([(xl, y + 1.5), ((xl + xr) / 2, y + 1), (xr, y - 4), (xr + 2, y - 5.5)], lw, taper=0.35)
        if kind == 'o':
            o = e.get('open', 0.8)
            pts = ell((xl + xr) / 2 + (2 if view != 'front' else 0), y + 3, w * 0.38, w * 0.45 * (0.6 + o), 10)
            return paint(pts, '#5a1e1a', 'flat', off=False) + ink(pts, lw, closed=True)
        # open shapes: 'open' (smile, laugh), 'teeth' (anger: a rectangle of teeth)
        o = e.get('open', 0.7)
        h = w * 0.9 * o
        if kind == 'teeth':
            top = [(xl, y - 2), ((xl + xr) / 2, y + 1), (xr, y - 3)]
            bot = [(xr - 1, y + h * 0.6), ((xl + xr) / 2, y + h * 0.75), (xl + 1, y + h * 0.5)]
            pts = top + bot
            s = paint(pts, '#5a1e1a', 'flat', off=False)
            s += paint([(xl + 1, y - 1), (xr - 1, y - 2), (xr - 1, y + h * 0.55), (xl + 1, y + h * 0.48)], '#fffaf0', 'flat',
                       off=False, smooth=False)
            s += ink([((xl + xr) / 2, y + 0.5), ((xl + xr) / 2 + 0.3, y + h * 0.65)], lw * 0.5)
            s += ink([(xl, y + h * 0.27), (xr, y + h * 0.22)], lw * 0.5)
            return s + ink(pts, lw, closed=True)
        # smile/laugh: flat-ish top, deep round bottom
        top = [(xl - 2, y - c * 5), ((xl + xr) / 2, y - c * 1), (xr + 2, y - c * 5.5)]
        bot = [(xr - 2, y + h * 0.55), ((xl + xr) / 2 + 1, y + h), (xl + 1, y + h * 0.5)]
        pts = top + bot
        s = paint(pts, '#5a1e1a', 'flat', off=False)
        # upper teeth: a band under the top line; tongue: a bump at the bottom
        tw = [(xl + 1, y - c * 4.5 + 0.5), ((xl + xr) / 2, y - c * 0.5 + 0.5), (xr + 0.5, y - c * 5),
              (xr - 1, y - c * 4 + h * 0.2), ((xl + xr) / 2, y + h * 0.22), (xl + 2, y - c * 3.5 + h * 0.2)]
        s += paint(tw, '#fffaf0', 'flat', off=False)
        tg = [(xl + w * 0.35, y + h * 0.85), ((xl + xr) / 2 + 1, y + h * 0.5), (xr - w * 0.35, y + h * 0.8),
              ((xl + xr) / 2 + 1, y + h * 0.98)]
        s += paint(tg, '#d8665a', 'flat', off=False)
        return s + ink(pts, lw, closed=True, weight=0.7)

    # ---------------------------------------------------------------- whole head
    def draw(self, view='three', expr='calm', hair_back='', hair_front='', over_face='', after='', beard='',
             stache=''):
        """Layers: hair behind, ears (far), face, ears (near), cheeks, eyes, brows, beard, mouth, nose,
        hair in front, `after` (glasses, a loupe…)."""
        e = self.ex(expr)
        L = self.layout(view)
        s = [hair_back]
        s.append(self.face(view))
        s.append(self.ears(view))
        s.append(over_face)
        for cx in L['cheeks']:
            if self.blush_r:
                s.append(blush(cx, self.cheek_y + (e.get('cheek', 0)), self.blush_r, op=self.blush_op))
        for i, (x, k) in enumerate(L['eyes']):
            side = -1 if (view == 'front' and i == 0) or (view == 'three' and i == 0) else 1
            s.append(self.eye(x, self.eye_y, k, e, view, side))
            bx = x + (side * 1.5 if view != 'side' else 2)
            s.append(self.brow(bx, self.brow_y, e, side if view != 'side' else 1, k))
        s.append(beard)
        s.append(self.mouth(view, L['mouth'], e))
        s.append(stache)
        s.append(self.nose_draw(view, L['nose']))
        s.append(hair_front)
        s.append(after)
        return ''.join(x for x in s if x)
