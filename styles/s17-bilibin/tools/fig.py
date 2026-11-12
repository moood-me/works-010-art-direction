"""Pieces of a full figure, in head units (a head ~ 200 high, its eye line at y = 0; a figure stands with its feet
at y = HEIGHT - 112). A character module places the joints by hand — a pose with a line of action — and dresses
them with these pieces: arms and legs as tubes through three joints, hands, shoes, a skirt with an ornament hem."""
import math
import parts
from parts import limb, hand
from kit import INK, curve, path_d, _f, _f2


def ang(a, b):
    """The angle for parts.hand (0 = fingers down) pointing from a to b."""
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) - 90


def arm(d, sh, el, wr, color, w0=58, w1=40, pattern=None, cuff=None, skin=None, pose='rest', flip=False,
        hand_s=1.35, hand_ang=None, hand_dx=0, fore=None, roll=None):
    """A sleeved arm: a tube from the shoulder through the elbow to the wrist, a cuff band, the hand."""
    if skin:
        hx, hy = wr
        a = ang(el, wr) if hand_ang is None else hand_ang
        hand(d, hx + hand_dx, hy - 6, a, hand_s, pose, skin, flip)
    # a round shoulder cap (the deltoid) under the tubes, so the arm grows out of the body, not out of a cut
    d.raw('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (
        _f(sh[0]), _f(sh[1]), _f(w0 * 0.56), color, INK, _f2(d.LINE * d.lw)))
    if pattern:
        d.raw('<circle cx="%s" cy="%s" r="%s" fill="url(#%s)"/>' % (_f(sh[0]), _f(sh[1]), _f(w0 * 0.56 - 1.5), pattern))
    # two tubes and a round elbow: a sharp bend stays clean
    wm = (w0 + w1) / 2
    limb(d, [sh, ((sh[0] + el[0]) / 2, (sh[1] + el[1]) / 2), el], w0, wm, color, pattern)
    # cover the tube's square top inside the cap
    d.raw('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(sh[0]), _f(sh[1]), _f(w0 * 0.56 - d.LINE * d.lw / 2), color))
    if pattern:
        d.raw('<circle cx="%s" cy="%s" r="%s" fill="url(#%s)"/>' % (_f(sh[0]), _f(sh[1]),
                                                                    _f(w0 * 0.56 - d.LINE * d.lw / 2), pattern))
    limb(d, [el, ((el[0] + wr[0]) / 2, (el[1] + wr[1]) / 2), wr], wm, w1, fore or color, None if fore else pattern)
    # hide the seam: a disc of the sleeve's colour over the joint, its outer arc in ink
    d.raw('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_f(el[0]), _f(el[1]), _f(wm / 2 - 1.5), color))
    if pattern:
        d.raw('<circle cx="%s" cy="%s" r="%s" fill="url(#%s)"/>' % (_f(el[0]), _f(el[1]), _f(wm / 2 - 1.5), pattern))
    a1 = math.atan2(sh[1] - el[1], sh[0] - el[0])
    a2 = math.atan2(wr[1] - el[1], wr[0] - el[0])
    da = (a2 - a1) % (2 * math.pi)
    # the outer side of the bend is the long way round from one tube to the other
    if da < math.pi:
        a1, a2 = a2, a1
        da = 2 * math.pi - da
    r = wm / 2
    p1 = (el[0] + math.cos(a1 + math.pi / 2) * r, el[1] + math.sin(a1 + math.pi / 2) * r)
    p2 = (el[0] + math.cos(a2 - math.pi / 2) * r, el[1] + math.sin(a2 - math.pi / 2) * r)
    d.raw('<path d="M%s %sA%s %s 0 0 1 %s %s" fill="none" stroke="%s" stroke-width="%s"/>' % (
        _f(p1[0]), _f(p1[1]), _f(r), _f(r), _f(p2[0]), _f(p2[1]), INK, _f2(d.LINE * d.lw)))
    if roll:
        # a sleeve rolled up above the elbow: the turned-back cuff as an ornament band across the upper arm
        ground, ink = roll
        t = 0.72
        c = (sh[0] + (el[0] - sh[0]) * t, sh[1] + (el[1] - sh[1]) * t)
        dx, dy = el[0] - sh[0], el[1] - sh[1]
        ln = math.hypot(dx, dy) or 1
        w = w0 + (wm - w0) * t + 8
        d.band([(c[0] - dx / ln * 14, c[1] - dy / ln * 14), (c[0] + dx / ln * 14, c[1] + dy / ln * 14)], w, None,
               'stripe', ink, ground=ground, step=9, n=2)
        q = [(c[0] - dx / ln * 14 + dy / ln * w / 2, c[1] - dy / ln * 14 - dx / ln * w / 2),
             (c[0] + dx / ln * 14 + dy / ln * w / 2, c[1] + dy / ln * 14 - dx / ln * w / 2),
             (c[0] + dx / ln * 14 - dy / ln * w / 2, c[1] + dy / ln * 14 + dx / ln * w / 2),
             (c[0] - dx / ln * 14 - dy / ln * w / 2, c[1] - dy / ln * 14 + dx / ln * w / 2)]
        d.ink([(x, y, 'c') for x, y in q], closed=True, n=2)
    if cuff:
        dx, dy = wr[0] - el[0], wr[1] - el[1]
        ln = math.hypot(dx, dy) or 1
        c0 = (wr[0] - dx / ln * 16, wr[1] - dy / ln * 16)
        d.band([c0, wr], w1 + 2, None, 'stripe', cuff[1], ground=cuff[0], step=7, n=2)


def leg(d, hip, knee, ankle, color, w0=80, w1=44, pattern=None):
    limb(d, [hip, knee, ankle], w0, w1, color, pattern)


def shoe(d, ankle, toe_dir=1, color='#3a2a22', L=78, H=40, sole=None, laces=None, boot=0):
    """A shoe seen from the side or three-quarters: toe_dir +1 points right, -1 left. boot > 0 raises the shaft."""
    x, y = ankle
    s = toe_dir
    pts = [(x - s * 22, y - 6 - boot, 'c'), (x + s * 14, y - 8 - boot, 'c'), (x + s * 18, y - 2), (x + s * (L - 16), y + 14),
           (x + s * L, y + H - 8), (x + s * (L - 4), y + H, 'c'), (x - s * 26, y + H, 'c'), (x - s * 28, y + 12)]
    d.shape(pts, color)
    if sole:
        d.band([(x - s * 26, y + H - 5), (x + s * (L - 6), y + H - 5)], 9, None, 'stripe', sole, ground=sole, n=2,
               edge=False)
        d.ink(pts, closed=True)
    if laces:
        for i in range(3):
            lx, ly = x + s * (6 + i * 9), y + 4 + i * 6 - boot * (0.6 - i * 0.2)
            d.ink([(lx - 8, ly - 2), (lx + 8, ly + 3)], 3.2, color=laces)


def skirt(d, waist_l, waist_r, hem_l, hem_r, color, pattern=None, hem=None, folds=3, wave=10):
    """A skirt as a flat trapezoid with a waving hem, folds as thin lines, an ornament band along the hem."""
    n = 6
    hemline = []
    for i in range(n + 1):
        t = i / n
        x = hem_l[0] + (hem_r[0] - hem_l[0]) * t
        y = hem_l[1] + (hem_r[1] - hem_l[1]) * t + (wave if i % 2 else 0)
        hemline.append((x, y))
    pts = [waist_l, ((waist_l[0] + hem_l[0]) / 2 - 6, (waist_l[1] + hem_l[1]) / 2)] + hemline + \
          [((waist_r[0] + hem_r[0]) / 2 + 6, (waist_r[1] + hem_r[1]) / 2), waist_r]
    d.shape(pts, color, pattern=pattern)
    for i in range(folds):
        t = (i + 1) / (folds + 1)
        top = (waist_l[0] + (waist_r[0] - waist_l[0]) * t, waist_l[1] + 60)
        bot = hemline[int(round(t * n))]
        d.thin([top, ((top[0] + bot[0]) / 2 + 4, (top[1] + bot[1]) / 2), (bot[0], bot[1] - 4)], k=0.9)
    if hem:
        kind, ink, ground, w = hem
        hl = [(q[0], q[1] - w / 2 - 2) for q in hemline]
        with d.clipped(pts):
            d.band(hl, w, None, kind, ink, ground=ground, step=w * 1.1)
        d.ink(pts, closed=True)
    return pts


def flowers(d, x, y, s=1.0, colors=('#a8392b', '#e8d27a', '#5d7a8c')):
    """A small bunch of field flowers (stems, leaves, round heads) — for a hand to hold."""
    with d.g(x, y, s):
        heads = [(-30, -150, colors[0]), (-5, -175, colors[1]), (22, -150, colors[2]), (-12, -125, colors[1]),
                 (12, -120, colors[0])]
        for hx, hy, c in heads:
            d.ink([(0, 0), (hx * 0.4, hy * 0.5), (hx, hy)], 2.2, color='#4a5a2a')
        d.shape([(-4, -60), (-34, -86), (-14, -70)], '#6b7a3a', 2.0)
        d.shape([(4, -70), (34, -96), (14, -76)], '#6b7a3a', 2.0)
        for hx, hy, c in heads:
            for i in range(6):
                a = math.radians(60 * i)
                d.raw('<circle cx="%s" cy="%s" r="7" fill="%s" stroke="%s" stroke-width="%s"/>' % (
                    _f(hx + math.cos(a) * 9), _f(hy + math.sin(a) * 9), c, INK, _f2(d.THIN * d.lw)))
            d.raw('<circle cx="%s" cy="%s" r="6" fill="#c99a3c" stroke="%s" stroke-width="%s"/>' % (
                _f(hx), _f(hy), INK, _f2(d.THIN * d.lw)))
