"""Face parts and small things drawn the same way for everyone: eyes, brows, mouths, hands, colours.

All take local coordinates (the head's own units, about 220 from crown to chin) and an optional size factor s.
"""
import math
from kit import ink, dot, white, wash, blot

# colours: transparent watercolours, light and clean; white paper does the rest
SKIN = '#f0bf98'
SKIN_OLD = '#e8b08c'
BLUSH = '#e57d68'
LIPS = '#d4594b'
SHADOW = '#8f86a8'      # a cool violet-grey wash for shade under hair, chin, folds

EXPR = {
    # brow lift (+ up), brow tilt (+ inner ends up = sad, - = angry), lid (0 open .. 1 shut), look (dx, dy),
    # mouth kind, eye size
    'calm':     dict(lift=0, tilt=0, lid=0.25, look=(0, 0), mouth='soft', eye=1.0),
    'dream':    dict(lift=2, tilt=1, lid=0.5, look=(-0.5, -1), mouth='soft', eye=1.0),
    'joy':      dict(lift=4, tilt=0, lid=0.0, look=(0, 0), mouth='laugh', eye=0.9, squint=True),
    'surprise': dict(lift=12, tilt=2, lid=0.0, look=(0, 0), mouth='O', eye=1.25),
    'sad':      dict(lift=2, tilt=7, lid=0.45, look=(0, 1.5), mouth='down', eye=1.0),
    'anger':    dict(lift=-5, tilt=-8, lid=0.3, look=(0, 0), mouth='shout', eye=1.0),
    'grump':    dict(lift=-3, tilt=-5, lid=0.35, look=(0, 0), mouth='flat', eye=0.95),
    'smirk':    dict(lift=2, tilt=-2, lid=0.1, look=(-1, 0), mouth='grin', eye=1.0),
    'stern':    dict(lift=-1, tilt=-3, lid=0.4, look=(0, 0), mouth='flat', eye=1.0),
}


def eye(d, x, y, s=1.0, look=(0, 0), lid=0.25, lash=False, side=-1, squint=False, white_=True, w=1.0, seed=None):
    """A Blake eye: a small round of white paper, a loose upper line, a dot of a pupil.
    side: -1 if the outer corner is to the left. squint: a happy closed arc instead of an open eye."""
    rx, ry = 7.6 * s, 8.4 * s
    if squint:
        ink(d, [(x - rx * 1.2, y + 1), (x, y - ry * 0.9), (x + rx * 1.2, y + 1)], w=2.2 * w, start=0.4, end=0.3, seed=seed)
        return
    if white_:
        white(d, x, y, rx, ry)
    px, py = x + look[0] * 2.4 * s, y + look[1] * 2.0 * s + lid * ry * 0.5
    dot(d, px, py, 3.1 * s)
    top = y - ry + lid * ry * 1.1
    ink(d, [(x - rx * 1.1, y + 0.5 * s + lid * 2), (x - rx * 0.4, top - 0.5), (x + rx * 0.5, top - 0.3),
            (x + rx * 1.1, y + 0.5 * s + lid * 2)], w=1.8 * w, start=0.5, end=0.3, seed=seed)
    ink(d, [(x - rx * 0.6, y + ry * 0.95), (x + rx * 0.5, y + ry * 0.9)], w=0.8 * w, start=0.2, end=0.2, jit=0.3,
        seed=None if seed is None else seed + 1)
    if lash:
        ox = x + side * rx * 1.05
        ink(d, [(ox, y + lid * 2), (ox + side * 5 * s, y - 4 * s + lid * 2)], w=1.6 * w, start=1, end=0.1)


def brow(d, x, y, length=22, lift=0, tilt=0, side=-1, w=1.6, arch=4, seed=None):
    """A brow over an eye at (x, y): a tapered stroke; tilt raises the inner end (sad) or drops it (angry).
    side: -1 if the outer end is to the left."""
    yi = y - lift + (-tilt)            # inner end
    yo = y - lift + tilt * 0.3          # outer end
    xi, xo = x - side * length * 0.5, x + side * length * 0.5
    ink(d, [(xi, yi), ((xi + xo) / 2, (yi + yo) / 2 - arch), (xo, yo + 2)], w=w * 1.4, start=1.0, end=0.15, seed=seed)


def mouth(d, x, y, kind='soft', s=1.0, side=-1, w=1.0, lips=True, seed=None):
    """Mouths. side: which way the face looks (-1 left); the far corner is shorter."""
    a, b = x + side * 12 * s, x - side * 9 * s       # near-the-profile corner, far corner
    if kind == 'soft':
        ink(d, [(a, y - 1), ((a + b) / 2, y + 2.5 * s), (b, y - 2.5 * s)], w=1.7 * w, start=0.4, end=0.2, seed=seed)
        if lips:
            wash(d, [(a, y - 2), (b, y - 4), (b, y + 5), ((a + b) / 2, y + 9 * s), (a, y + 4)], LIPS, 0.45)
            ink(d, [((a + b) / 2 - 4 * s, y + 8 * s), ((a + b) / 2 + 4 * s, y + 8 * s)], w=0.9 * w, jit=0.2)
    elif kind == 'flat':
        ink(d, [(a, y + 1), ((a + b) / 2, y), (b, y + 2)], w=1.8 * w, start=0.6, end=0.4, seed=seed)
        ink(d, [(b, y + 2), (b - side * 3, y + 5)], w=1.0 * w)
    elif kind == 'down':
        ink(d, [(a, y + 4), ((a + b) / 2, y - 1), (b, y + 4)], w=1.7 * w, start=0.4, end=0.3, seed=seed)
    elif kind == 'grin':
        ink(d, [(a, y - 1), ((a + b) / 2, y + 4 * s), (b, y - 4 * s), (b - side * 3, y - 7 * s)], w=1.8 * w,
            start=0.4, end=0.2, seed=seed)
    elif kind == 'laugh':
        pts = [(a, y - 3), ((a + b) / 2 - side * 2, y - 2), (b + side * 1, y - 5 * s),
               (b - side * 1, y + 4 * s), ((a + b) / 2, y + 12 * s), (a + side * 1, y + 3)]
        wash(d, pts, '#c4473f', 0.75)
        ink(d, pts + [pts[0]], w=1.7 * w, start=0.8, end=0.6, seed=seed)
        ink(d, [(a - side * 4, y - 1), (b + side * 1, y - 3 * s)], w=0.8, jit=0.2)   # teeth line
    elif kind == 'O':
        pts = [(x - side * 1, y - 5 * s), (x + 5 * s, y + 1), (x, y + 9 * s), (x - 5 * s, y + 2)]
        wash(d, pts, '#b43c38', 0.7)
        ink(d, pts + [pts[0]], w=1.6 * w, closed=False, start=0.8, end=0.6, seed=seed)
    elif kind == 'shout':
        pts = [(a, y - 2), ((a + b) / 2, y - 4 * s), (b, y - 1), (b + side * 1, y + 7 * s), ((a + b) / 2, y + 10 * s),
               (a - side * 1, y + 6 * s)]
        wash(d, pts, '#b43c38', 0.75)
        ink(d, pts + [pts[0]], w=1.9 * w, start=0.9, end=0.7, seed=seed)
        ink(d, [(a - side * 2, y + 0.5), (b + side * 2, y + 1)], w=0.8, jit=0.2)


def hand(d, x, y, s=1.0, rot=0, kind='open', flip=False, color=SKIN, seed=None):
    """A quick hand: a mitten of a palm and a few long fingers. kind: open, rest, hold, fist, point.
    Drawn pointing down in its own frame (wrist at 0,0), turned by rot."""
    d.push(x, y, s, rot, flip)
    if kind == 'open':
        palm = [(-7, 0), (-9, 14), (-6, 24), (6, 24), (9, 12), (7, 0)]
        fingers = [[(-6, 22), (-12, 34), (-15, 42)], [(-2, 24), (-4, 38), (-5, 48)], [(2, 24), (3, 39), (4, 49)],
                   [(6, 22), (10, 35), (12, 44)]]
        thumb = [(8, 8), (16, 14), (21, 22)]
    elif kind == 'rest':
        palm = [(-7, 0), (-8, 14), (-5, 24), (6, 24), (8, 12), (7, 0)]
        fingers = [[(-5, 22), (-6, 33), (-4, 39)], [(-1, 24), (-1, 36), (1, 41)], [(3, 23), (4, 34), (6, 38)]]
        thumb = [(7, 8), (12, 16), (13, 23)]
    elif kind == 'fist':
        palm = [(-8, 0), (-10, 12), (-8, 24), (8, 25), (10, 12), (8, 0)]
        fingers = [[(-8, 22), (-4, 27), (0, 24)], [(0, 25), (4, 28), (8, 23)]]
        thumb = [(8, 8), (2, 14), (-4, 16)]
    elif kind == 'point':
        palm = [(-7, 0), (-9, 12), (-6, 22), (6, 22), (8, 12), (7, 0)]
        fingers = [[(-2, 20), (-3, 36), (-3, 50)], [(3, 21), (6, 25), (4, 28)], [(-6, 20), (-7, 26), (-3, 28)]]
        thumb = [(7, 8), (13, 12), (14, 18)]
    else:   # hold: fingers curled round something
        palm = [(-7, 0), (-9, 14), (-6, 24), (6, 24), (9, 12), (7, 0)]
        fingers = [[(-6, 22), (-12, 30), (-8, 36)], [(-1, 24), (-5, 34), (0, 38)], [(4, 23), (2, 32), (7, 34)]]
        thumb = [(8, 8), (15, 16), (12, 24)]
    wash(d, palm + [(4, 40), (-4, 42)], color, 0.5, rough='S')
    ink(d, [palm[0], palm[1], palm[2]], w=1.5, end=0.3)
    ink(d, [palm[-1], palm[-2], palm[-3]], w=1.3, end=0.3)
    for f in fingers:
        ink(d, f, w=1.3, start=0.8, end=0.25)
    ink(d, thumb, w=1.4, start=0.9, end=0.3)
    d.pop()


def shade(d, poly, opacity=0.35, dx=0, dy=0):
    """A cool violet-grey wash in shadow (under a chin, a hat brim, inside a fold)."""
    wash(d, poly, SHADOW, opacity, dx, dy)


def strand(d, x0, y0, x1, y1, amp=6, waves=1.5, w=1.0, phase=0.0, seed=None, start=0.4, end=0.05):
    """A wavy lock of hair from (x0, y0) to (x1, y1)."""
    n = 7
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    pts = []
    for i in range(n + 1):
        t = i / n
        o = amp * math.sin((t * waves + phase) * 2 * math.pi) * (0.3 + 0.7 * t)
        pts.append((x0 + dx * t + nx * o, y0 + dy * t + ny * o))
    ink(d, pts, w=w, start=start, end=end, seed=seed)
