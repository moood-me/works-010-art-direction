"""Shared face parts in the mid-century manner: tiny features, dark ink, round pink cheeks.

Every part takes a centre (x, y), a size s (1.0 = an adult face 200 units tall) and `side`:
+1 when the outer corner of the eye points to +x, -1 when to -x.
"""
from kit import brush, shape, ell, circle, blush, path, INK

LIP = '#c23a2c'      # gouache vermilion for mouths
MOUTH_IN = '#6e1f1c'


def eye(x, y, s=1.0, kind='open', side=1, squash=1.0, lash=True, color=INK, lid=0.0, gaze=1.0):
    """kind: open | dot | closed | happy | lid | wide | sad | cross."""
    o = []
    w = s * squash
    if kind == 'dot':
        o.append(ell(x, y, 4.2 * w, 5.6 * s, color))
    elif kind == 'open':
        # a small dark almond, flat-ish top lid, lash flick at the outer corner
        top = y - 4.6 * s + lid * 3.5 * s
        o.append(shape([(x - side * 7 * w, y + 0.6 * s, 'c'), (x - side * 2 * w, top), (x + side * 4 * w, top + 0.4 * s),
                        (x + side * 8 * w, y - 0.8 * s, 'c'), (x + side * 2 * w, y + 3.6 * s)], color))
        o.append(brush([(x - side * 7.5 * w, y + 0.2 * s), (x - side * 1 * w, top - 1.2 * s), (x + side * 6 * w, top - 0.2 * s),
                        (x + side * 10.5 * w, y - 3.5 * s)], 2.3 * s, color, taper=(0.2, 0.25)))
        if lash:
            o.append(brush([(x + side * 7.5 * w, y - 1.5 * s), (x + side * 11 * w, y - 5.5 * s), (x + side * 13 * w, y - 7.5 * s)],
                           1.8 * s, color, taper=(0.0, 0.7)))
    elif kind == 'look':
        # white almond, big dark iris pushed up under a heavy lid (the dreamy upward look)
        top = y - 5.5 * s + lid * 3 * s
        alm = [(x - side * 8 * w, y + 0.8 * s, 'c'), (x - side * 2 * w, top), (x + side * 5 * w, top + 0.2 * s),
               (x + side * 9 * w, y - 1.2 * s, 'c'), (x + side * 2 * w, y + 4.2 * s)]
        o.append(shape(alm, '#fbf6ea'))
        cid = 'eye%d' % (abs(hash((x, y, s, side))) % 10**8)
        o.append(f'<clipPath id="{cid}"><path d="{path(alm)}"/></clipPath>')
        o.append(f'<g clip-path="url(#{cid})">' + ell(x + side * gaze * w, y - 1.6 * s, 4.6 * w, 5.4 * s, color) + '</g>')
        o.append(brush([(x - side * 8.5 * w, y + 0.4 * s), (x - side * 1 * w, top - 1.4 * s), (x + side * 6 * w, top - 0.4 * s),
                        (x + side * 11 * w, y - 3.8 * s)], 2.8 * s, color, taper=(0.2, 0.25)))
        if lash:
            o.append(brush([(x + side * 8.5 * w, y - 2 * s), (x + side * 12 * w, y - 6 * s), (x + side * 14 * w, y - 8 * s)],
                           2.0 * s, color, taper=(0.0, 0.7)))
    elif kind == 'closed':
        # dreamy closed lid: a downward curve with short lashes under it
        o.append(brush([(x - side * 8 * w, y - 1 * s), (x, y + 3.5 * s), (x + side * 9 * w, y - 1.5 * s)], 2.6 * s, color,
                       taper=(0.3, 0.2)))
        if lash:
            for t, dx in ((0.55, 3), (0.85, 7.5)):
                bx = x + side * dx * w
                by = y + 3.5 * s * (1 - (dx / 9) ** 2) - 0.8 * s
                o.append(brush([(bx, by), (bx + side * 2.2 * s, by + 3.6 * s)], 1.5 * s, color, taper=(0, 0.8)))
            o.append(brush([(x + side * 8.5 * w, y - 1.5 * s), (x + side * 12 * w, y - 4.5 * s)], 1.6 * s, color, taper=(0, 0.8)))
    elif kind == 'happy':
        o.append(brush([(x - side * 7 * w, y + 2.5 * s), (x, y - 3.5 * s), (x + side * 8 * w, y + 2 * s)], 2.6 * s, color,
                       taper=(0.25, 0.25)))
        if lash:
            o.append(brush([(x + side * 7.5 * w, y + 1.5 * s), (x + side * 11 * w, y - 1 * s)], 1.5 * s, color, taper=(0, 0.8)))
    elif kind == 'lid':
        # tired: the heavy lid cuts the eye straight across
        o.append(shape([(x - side * 7 * w, y, 'c'), (x + side * 8 * w, y - 1 * s, 'c'), (x + side * 3 * w, y + 3.4 * s),
                        (x - side * 3 * w, y + 3.2 * s)], color))
        o.append(brush([(x - side * 8.5 * w, y - 0.4 * s), (x + side * 1 * w, y - 1.6 * s), (x + side * 11 * w, y - 1.8 * s)],
                       2.6 * s, color, taper=(0.15, 0.2)))
        if lash:
            o.append(brush([(x + side * 9 * w, y - 1.6 * s), (x + side * 12.5 * w, y - 4.2 * s)], 1.6 * s, color, taper=(0, 0.8)))
    elif kind == 'wide':
        o.append(ell(x, y - 1 * s, 6.5 * w, 7.8 * s, '#fbf6ea'))
        o.append(ell(x + side * 0.6 * w, y - 0.5 * s, 3.4 * w, 4.4 * s, color))
        o.append(brush([(x - side * 7 * w, y - 3 * s), (x, y - 9.4 * s), (x + side * 7.5 * w, y - 3.5 * s)], 1.8 * s, color,
                       taper=(0.3, 0.3)))
    elif kind == 'sad':
        o.append(ell(x, y + 0.8 * s, 3.8 * w, 4.4 * s, color))
        o.append(brush([(x - side * 7 * w, y - 4.5 * s), (x + side * 1 * w, y - 4.6 * s), (x + side * 8 * w, y - 1 * s)],
                       2.2 * s, color, taper=(0.2, 0.3)))
    elif kind == 'cross':   # squeezed shut (anger, a shout)
        o.append(brush([(x - side * 7 * w, y - 2.5 * s), (x + side * 1 * w, y + 0.5 * s), (x + side * 8 * w, y + 0.5 * s)],
                       2.6 * s, color, taper=(0.2, 0.2)))
    return ''.join(o)


def brow(x, y, s=1.0, side=1, inner=0.0, outer=0.0, w=2.6, length=1.0, color=INK, squash=1.0):
    """A thin tapered brow; inner/outer move its ends down (+) or up (-), in face units."""
    L = length * squash
    return brush([(x - side * 8 * L * s, y + inner * s), (x + side * 1 * L * s, y - 2.4 * s + (inner + outer) * 0.5 * s),
                  (x + side * 10 * L * s, y + outer * s)], w * s, color, taper=(0.15, 0.6))


def mouth(x, y, s=1.0, kind='smile', side=1, color=LIP, width=1.0):
    W = width * s
    if kind == 'smile':
        return brush([(x - side * 8 * W, y - 1.5 * s), (x, y + 3 * s), (x + side * 8 * W, y - 2.5 * s)], 2.6 * s, color, taper=(0.3, 0.3))
    if kind == 'soft':      # the quiet closed smile
        return brush([(x - side * 6 * W, y - 0.5 * s), (x, y + 2 * s), (x + side * 6 * W, y - 1.2 * s)], 2.4 * s, color, taper=(0.35, 0.35))
    if kind == 'lips':      # a small painted mouth: upper lip with a dip, fuller lower lip, a little smile at the corners
        return (shape([(x - side * 8 * W, y - 0.5 * s, 'c'), (x - side * 3 * W, y - 3.2 * s), (x - side * 0.5 * W, y - 2 * s, 'c'),
                       (x + side * 2.5 * W, y - 3.4 * s), (x + side * 7.5 * W, y - 1.5 * s, 'c'), (x + side * 2 * W, y + 3.8 * s),
                       (x - side * 4 * W, y + 3.2 * s)], color)
                + brush([(x - side * 8.5 * W, y - 0.6 * s), (x, y + 0.3 * s), (x + side * 8 * W, y - 1.8 * s)], 1.3 * s, MOUTH_IN,
                        taper=(0.3, 0.3)))
    if kind == 'smirk':
        return brush([(x - side * 7 * W, y + 0.5 * s), (x + side * 2 * W, y + 1.5 * s), (x + side * 8 * W, y - 3.5 * s)], 2.6 * s, color,
                     taper=(0.3, 0.2))
    if kind == 'flat':
        return brush([(x - side * 7 * W, y), (x + side * 7 * W, y + 0.6 * s)], 2.4 * s, color, taper=(0.3, 0.3))
    if kind == 'frown':
        return brush([(x - side * 8 * W, y + 2.5 * s), (x, y - 1.5 * s), (x + side * 8 * W, y + 3 * s)], 2.6 * s, color, taper=(0.3, 0.3))
    if kind == 'o':
        return ell(x, y + 1 * s, 4 * W, 5 * s, color) + ell(x, y + 1.6 * s, 2.3 * W, 3.2 * s, MOUTH_IN)
    if kind == 'grin':      # open laugh: a red half-moon, dark inside, tongue
        return (shape([(x - side * 10 * W, y - 2 * s, 'c'), (x + side * 10 * W, y - 3 * s, 'c'), (x + side * 5 * W, y + 7 * s),
                       (x - side * 4 * W, y + 7 * s)], MOUTH_IN)
                + shape([(x - side * 4 * W, y + 4.5 * s), (x + side * 4 * W, y + 4 * s), (x + side * 3 * W, y + 7 * s),
                         (x - side * 3 * W, y + 7 * s)], '#e2706a')
                + brush([(x - side * 10.5 * W, y - 2 * s), (x, y - 2.8 * s), (x + side * 10.5 * W, y - 3.2 * s)], 1.8 * s, color, taper=(0.1, 0.1)))
    if kind == 'sad':       # small down-turned, a little open
        return brush([(x - side * 7 * W, y + 3 * s), (x - side * 2 * W, y - 0.5 * s), (x + side * 3 * W, y - 0.5 * s),
                      (x + side * 7 * W, y + 3.4 * s)], 2.4 * s, color, taper=(0.35, 0.35))
    if kind == 'shout':     # angry open: wide, angular
        return (shape([(x - side * 10 * W, y - 3 * s, 'c'), (x - side * 2 * W, y - 1 * s), (x + side * 10 * W, y - 3.5 * s, 'c'),
                       (x + side * 7 * W, y + 6 * s, 'c'), (x - side * 7 * W, y + 6 * s, 'c')], MOUTH_IN)
                + shape([(x - side * 8 * W, y - 2 * s, 'c'), (x + side * 8 * W, y - 2.4 * s, 'c'), (x + side * 7 * W, y + 0.4 * s),
                         (x - side * 7 * W, y + 0.6 * s)], '#f6efe0'))
    raise ValueError(kind)


# the four expressions of the sheet, and calm; characters may override per face
EXPR = {
    'calm':     dict(eye='open', brow=(0, 0), mouth='soft'),
    'joy':      dict(eye='happy', brow=(-3, -1), mouth='grin', cheek=1.25),
    'surprise': dict(eye='wide', brow=(-8, -7), mouth='o'),
    'sad':      dict(eye='sad', brow=(-4, 4), mouth='sad'),
    'anger':    dict(eye='lid', brow=(5, -4), mouth='shout'),
}
