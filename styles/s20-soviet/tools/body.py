"""С20 — bodies: limbs, hands, shoes, and the trick that makes a turnaround cheap.

The style's bodies are ONE bold silhouette each (the costume is the body: a box, a bell, a column, a pear) with
thin legs and small feet; the arms are sleeves ending in drawn hands with separate fingers. A character writes its
silhouettes for the FRONT and the SIDE with the same number of points; `pick()` gives the three-quarter view as a
blend of the two, so the three views of a turnaround agree.
"""
import math
from kit import form, ink, paint, cr, ell, arc, rot_pts, move, SKIN, INK, d_of, hatch


def pick(front, side, view, t3=0.5):
    """front / side: point lists of equal length (or numbers). 'three' blends them."""
    t = {'front': 0.0, 'three': t3, 'side': 1.0}[view]
    if isinstance(front, (int, float)):
        return front + (side - front) * t
    if isinstance(front, tuple) and isinstance(front[0], (int, float)):
        return (front[0] + (side[0] - front[0]) * t, front[1] + (side[1] - front[1]) * t)
    return [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(front, side)]


def tube(path, w0, w1, n=6):
    """Outline of a limb along a centre path, width w0 → w1 (a sleeve, a trouser leg, a thin leg)."""
    P = cr(path, False, 4)
    L = [0]
    for i in range(1, len(P)):
        L.append(L[-1] + math.dist(P[i - 1], P[i]))
    tot = L[-1] or 1
    left, right = [], []
    for i, p in enumerate(P):
        a, b = P[max(0, i - 1)], P[min(len(P) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = (w0 + (w1 - w0) * L[i] / tot) / 2
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    # thin the list a little so the smooth curve stays calm
    k = max(1, len(left) // 7)
    left = left[::k] + [left[-1]]
    right = right[::k] + [right[-1]]
    return left + right[::-1]


def limb(path, w0, w1, color, lw=2.2, tex='brush', hatch_c=None):
    pts = tube(path, w0, w1)
    s = form(pts, color, lw=lw, tex=tex)
    if hatch_c:
        s = form(pts, color, lw=0, tex=tex, line=False) + hatch(pts, hatch_c, step=4.5, op=0.35) + \
            form(pts, None, lw=lw)
    return s


def leg(hip, knee, ankle, w, color=SKIN, lw=2.0):
    """A thin cartoon leg (stocking, bare or narrow trouser)."""
    return limb([hip, knee, ankle], w, w * 0.8, color, lw, tex='flat' if color == SKIN else 'brush')


# ---------------------------------------------------------------- hands
# Hand space: the wrist at (0, 0), the hand points along +x; size 1 = a hand 16 units long.
def _finger(x0, y0, ang, L, w):
    c, s = math.cos(ang), math.sin(ang)
    tip = (x0 + c * L, y0 + s * L)
    nx, ny = -s * w / 2, c * w / 2
    return [(x0 + nx, y0 + ny), (tip[0] + nx * 0.9, tip[1] + ny * 0.9), (tip[0] + c * w * 0.45, tip[1] + s * w * 0.45),
            (tip[0] - nx * 0.9, tip[1] - ny * 0.9), (x0 - nx, y0 - ny)]


def _place(pts, x, y, ang, s, flip):
    out = []
    c, sn = math.cos(ang), math.sin(ang)
    for px, py in pts:
        py = -py if flip else py
        px, py = px * s, py * s
        out.append((x + px * c - py * sn, y + px * sn + py * c))
    return out


def hand(x, y, ang=0.0, kind='open', s=1.0, flip=False, color=SKIN, lw=1.8, spread=1.0):
    """kind: open (fingers apart), rest (hanging, fingers together, a little curled), fist, hold (fist round a
    handle: the hole is left for it), point. flip mirrors across the hand's axis (left hand vs right hand)."""
    s = s * 1.25
    P = lambda pts: _place(pts, x, y, ang, s, flip)
    out = ''
    fills = []
    if kind in ('open', 'point', 'wave'):
        palm = ell(7, 0, 7.5, 6.2, 10)
        fl = [(13, -4.2, -0.42 * spread, 8.5), (14.5, -1.4, -0.12 * spread, 10), (14.2, 1.6, 0.14 * spread, 9.6),
              (12.5, 4.2, 0.42 * spread, 7.8)]
        if kind == 'point':
            fl = [(13, -4.2, -0.05, 11)] + [(11.5, -1.2 + i * 2.3, 0.9 + i * 0.25, 3.5) for i in range(3)]
        for fx, fy, fa, L in fl:
            out += form(P(_finger(fx - 3, fy, fa, L, 3.1)), color, lw=lw, tex='flat', off=False)
        thumb = _finger(5, -5, -1.05 * spread - 0.1, 8, 3.4)
        out += form(P(thumb), color, lw=lw, tex='flat', off=False)
        out += form(P(palm), color, lw=lw, tex='flat', off=False, gap=(0.9, 0.99) if False else None)
        # knuckle side open: cover the base lines of the fingers with a little paper
        out += paint(P([(9, -5.5), (13.5, -4), (14, 4.5), (9, 5.5)]), color, 'flat', off=False)
        return out
    if kind == 'rest':
        mitt = [(0, -4.6), (8, -6), (15, -5), (19.5, -2.5), (20.5, 1.5), (17.5, 4.6), (10, 5.6), (2, 4.6)]
        out += form(P(mitt), color, lw=lw, tex='flat', off=False)
        out += ink(P([(11, -1.6), (17.5, -1.2)]), lw * 0.65, taper=0.4)
        out += ink(P([(10.5, 1.4), (16.5, 2.2)]), lw * 0.65, taper=0.4)
        thumb = [(4, -4.5), (9, -8.6), (12.5, -8.4), (11, -5.2)]
        out += form(P(thumb), color, lw=lw * 0.9, tex='flat', off=False)
        return out
    # fist / hold
    box = [(0, -5), (6, -6.5), (13.5, -6.2), (16, -3), (16, 3.5), (13, 6.3), (5, 6.2), (0, 4.8)]
    out += form(P(box), color, lw=lw, tex='flat', off=False)
    for k in (-2.7, 0.6, 3.6):
        out += ink(P([(10.5, k), (15.2, k + 0.4)]), lw * 0.6, taper=0.45)
    out += ink(P([(4.5, -5.4), (9.5, -2.8), (11.5, 0.5)]), lw * 0.75, taper=0.35)
    return out


def shoe(x, y, s=1.0, d=1, color=INK, lw=1.8, kind='shoe'):
    """A small shoe; d = +1 toe to the right, -1 left, 0 toe to the viewer."""
    if d == 0:
        pts = [(-6, -6), (6, -6), (8.5, -1), (6, 1.5), (-6, 1.5), (-8.5, -1)]
    elif kind == 'boot':
        pts = [(-7, -16), (5, -16), (6, -7), (16, -4), (17.5, 1.5), (-8, 1.5), (-8.5, -6)]
    else:
        pts = [(-7, -7), (4, -7.5), (14, -3.5), (16, 0.5), (14, 1.8), (-7.5, 1.8), (-8.5, -3)]
    pts = [(x + px * s * (d if d else 1), y + py * s) for px, py in pts]
    return form(pts, color, lw=lw, tex='brush')


def ground(x, y, w, color='#3a2a1a', op=0.22):
    """A dry-brush shadow strip under the feet."""
    pts = ell(x, y + 2, w, 5, 12)
    return paint(pts, color, 'crayon', off=False, op=op)
