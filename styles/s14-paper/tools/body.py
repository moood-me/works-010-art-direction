"""С14 — body parts shared by all characters: limbs as strips of paper pinned at the joints with brads (the way
cut-out puppets of Norstein and Reiniger are jointed), hands cut with scissors, shoes, folds."""
import math
from kit import *

BRASS = '#c9a24c'


def brad(x, y, r=3.4):
    """A brass paper fastener in a joint."""
    return [card(ell(x, y, r, r, n=8), BRASS, 1), flat(ell(x - r * 0.3, y - r * 0.3, r * 0.35, r * 0.35, n=6), '#f3e2a6')]


def limb(pts, w, fill, lift=1, kind='card', var=0, joints=True, r=3.0):
    """An arm or a leg: one strip per segment, overlapping at the joint, a brad through it."""
    ws = w if isinstance(w, (list, tuple)) else [w] * len(pts)
    if not joints:                                             # one bent strip, no pins (trouser legs, stockings)
        return [Piece(strip(pts, ws, round_ends=True), fill, lift, kind, var=var)]
    out = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        ux, uy = dx / d, dy / d
        a2 = (a[0] - ux * ws[i] * 0.42, a[1] - uy * ws[i] * 0.42)
        b2 = (b[0] + ux * ws[i + 1] * 0.42, b[1] + uy * ws[i + 1] * 0.42)
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        p = strip([a2, mid, b2], [ws[i], (ws[i] + ws[i + 1]) / 2, ws[i + 1]], round_ends=True)
        out.append(Piece(p, fill, lift, kind, var=var + i))
    if joints:
        for (x, y) in pts[1:-1]:
            out += brad(x, y, r)
    return out


def hand(x, y, ang, s, skin, spread=0, thumb=1, lift=1):
    """A hand cut from one piece: the palm and four fingers divided by snips; the thumb is glued under it.
    (x, y) — the wrist; ang — where the fingers point (0 — down, 90 — to the viewer's left, −90 — right);
    spread — degrees between the fingers; thumb: +1 / −1 — which side it is on, 0 — hidden."""
    ky = 13
    cx = [-7.5, -2.5, 2.5, 7.5]
    ln = [14, 18, 17, 13]
    if thumb < 0:
        ln = ln[::-1]
    hw = 2.7
    pts = [(-6.5, -3, 1), (-10.5, 7)]
    for i in range(4):
        a = math.radians((i - 1.5) * spread)
        dx, dy = math.sin(a), math.cos(a)
        nx, ny = dy, -dx
        bx = cx[i]
        tipx, tipy = bx + dx * ln[i], ky + dy * ln[i]
        notch = 0.45 if spread < 6 else 0.05
        if i > 0:
            pts.append(((cx[i - 1] + bx) / 2, ky + min(ln[i - 1], ln[i]) * notch, 1))
        pts += [(bx - nx * hw + dx * ln[i] * 0.7, ky - ny * hw + dy * ln[i] * 0.7), (tipx - nx * hw * 0.6, tipy - ny * hw * 0.6 - 0.5 * dy),
                (tipx, tipy + 0.8), (tipx + nx * hw * 0.6, tipy + ny * hw * 0.6 - 0.5 * dy), (bx + nx * hw + dx * ln[i] * 0.7, ky + ny * hw + dy * ln[i] * 0.7)]
    pts += [(10.5, 7), (6.5, -3, 1)]
    out = []
    if thumb:
        t = thumb
        th = [(t * 6, 1), (t * 13, 6), (t * 18, 15), (t * 16.5, 20), (t * 12.5, 19), (t * 8, 12)]
        out.append(card(th if t > 0 else th[::-1], mix(skin, '#c0705c', 0.10), lift))
    out.append(card(pts, skin, lift))
    out = scale(out, s)
    out = rot(out, ang)
    return move(out, x, y)


def fist(x, y, ang, s, skin, lift=1):
    """A hand closed around something: a rounded piece with the knuckle snips, the thumb over it."""
    p = [(-7, -3, 1), (-10, 6), (-10, 15), (-5, 19), (0, 17.5, 1), (5, 19), (10, 15), (10, 6), (7, -3, 1)]
    out = [card(p, skin, lift), card([(-11, 6), (-3, 5), (2, 8), (-2, 12), (-11, 11)], mix(skin, '#c0705c', 0.10), 1)]
    return move(rot(scale(out, s), ang), x, y)


def shoe(x, y, d, L, col, sole='#efe6d2', h=None):
    """A shoe seen from the side; (x, y) — the heel on the ground, d — +1 toe to the right, −1 to the left."""
    h = h or L * 0.42
    up = [(0, 0, 1), (0, -h * 0.9), (L * 0.28, -h), (L * 0.62, -h * 0.62), (L * 0.95, -h * 0.5), (L, -h * 0.12), (L, 0, 1)]
    so = [(-1.5, 0.5, 1), (-1.5, -h * 0.16, 1), (L + 1.5, -h * 0.16, 1), (L + 1.5, 0.5, 1)]
    out = [card(up, col, 1), card(so, sole, 1)]
    if d < 0:
        out = mirror(out)
    return move(out, x, y)


def boot(x, y, d, L, col, sole='#2a2428', h=None, lace=None):
    """A heavy boot: tall shaft, thick tread, laces as tiny strips."""
    h = h or L * 0.85
    up = [(-1, 0, 1), (-2, -h, 1), (L * 0.42, -h, 1), (L * 0.45, -h * 0.5), (L * 0.9, -h * 0.42), (L * 1.02, -h * 0.14), (L * 1.02, 0, 1)]
    so = [(-3, 1, 1), (-3, -h * 0.13, 1), (L * 1.05, -h * 0.13, 1), (L * 1.05, 1, 1)]
    out = [card(up, col, 1), card(so, sole, 1)]
    if lace:
        for i in range(3):
            yy = -h * (0.86 - 0.17 * i)
            out.append(flat(strip([(L * 0.14, yy), (L * 0.44, yy + 2)], 2.2), lace))
    if d < 0:
        out = mirror(out)
    return move(out, x, y)


def folds(pts, lines, strength=0.2):
    """Creases over a piece: each line ((x1, y1), (x2, y2)) is a fold — dark at the first point, fading to the second."""
    return [shade(pts, a, b, strength) for a, b in lines]


def curl(x, y, r, col, lift=2, turns=1):
    """A rolled-up end of a paper strip seen end-on: a disc, the darker inside of the roll, the lit lip."""
    out = [card(ell(x, y, r, r, n=10), col, lift)]
    out.append(flat(ell(x + r * 0.10, y + r * 0.12, r * 0.62, r * 0.62, n=8), dark(col, 0.28)))
    out.append(flat(ell(x - r * 0.02, y - r * 0.02, r * 0.36, r * 0.36, n=8), lite(col, 0.10)))
    return out


def ground_shadow(x, w, y=0):
    return [Piece(ell(x, y + 3, w, w * 0.11, n=12), '#2b1b2c', 0, 'tissue', op=0.16)]
