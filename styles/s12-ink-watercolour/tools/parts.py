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
    # lift: brows up (+); tilt: inner ends up (+, sad) or down (-, angry); lid: 0 open .. 1 shut; look: pupils
    # (dx, dy); mouth: kind; eye: size; ms: mouth size; tilt_head: how the head goes with it (degrees);
    # extra: a mark beside the face (a tear, a start, a flush)
    'calm':     dict(lift=0, tilt=0, lid=0.25, look=(0, 0), mouth='soft', eye=1.0),
    'dream':    dict(lift=2, tilt=1, lid=0.5, look=(-0.5, -1), mouth='soft', eye=1.0),
    'joy':      dict(lift=7, tilt=0, lid=0.0, look=(0, 0), mouth='laugh', eye=0.9, squint=True, ms=1.6,
                     tilt_head=-10),
    'surprise': dict(lift=17, tilt=3, lid=0.0, look=(0, 0), mouth='O', eye=1.3, ms=1.5, tilt_head=-4,
                     extra='start'),
    'sad':      dict(lift=3, tilt=11, lid=0.5, look=(0, 1.5), mouth='down', eye=1.0, ms=1.4, tilt_head=12,
                     extra='tear'),
    'anger':    dict(lift=-7, tilt=-12, lid=0.3, look=(0, 0), mouth='shout', eye=1.0, ms=1.6, tilt_head=6,
                     extra='flush'),
    'grump':    dict(lift=-3, tilt=-5, lid=0.35, look=(0, 0), mouth='flat', eye=0.95),
    'smirk':    dict(lift=2, tilt=-2, lid=0.1, look=(-1, 0), mouth='grin', eye=1.0),
    'peer':     dict(lift=-2, tilt=-3, lid=0.45, look=(-1, 1.6), mouth='soft', eye=0.95),
    'stern':    dict(lift=-1, tilt=-3, lid=0.4, look=(0, 0), mouth='flat', eye=1.0),
    'merry':    dict(lift=5, tilt=0, lid=0.15, look=(0, 0), mouth='smile', eye=0.95),
    'sulk':     dict(lift=-4, tilt=-5, lid=0.5, look=(1.1, -0.2), mouth='flat', eye=1.0),
}


def extra(d, e, eye_x, eye_y, cheek_x, cheek_y, top_y):
    """The small marks Blake adds to a face: a tear for sadness, start-lines for surprise, a flush for anger."""
    k = e.get('extra')
    if k == 'tear':
        x, y = eye_x - 2, eye_y + 16
        pts = [(x, y), (x - 4, y + 10), (x, y + 15), (x + 4, y + 10), (x, y)]
        wash(d, pts, '#7fb6dc', 0.7, rough='S')
        ink(d, pts, w=1.0, retrace=0)
    elif k == 'start':
        for dx, a in ((-26, -20), (0, -30), (26, -20)):
            ink(d, [(eye_x + dx, top_y - 8), (eye_x + dx * 1.4, top_y - 26)], w=1.5, start=1.0, end=0.1, retrace=0)
    elif k == 'flush':
        blot(d, cheek_x, cheek_y, 26, '#e0503c', 0.45)
        for dx in (-10, 0, 10):
            ink(d, [(cheek_x + dx - 3, cheek_y - 6), (cheek_x + dx + 3, cheek_y + 4)], w=0.9, retrace=0)


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
    a, b = x + side * 12 * min(s, 1.0), x - side * 9 * s - side * 12 * (max(s, 1.0) - 1)   # near-the-profile corner, far
    x = (a + b) / 2
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
        pts = [(a, y - 3), ((a + b) / 2 - side * 2, y - 2), (b + side * 1, y - 6 * s),
               (b - side * 2, y + 6 * s), ((a + b) / 2, y + 14 * s), (a - side * 2, y + 6 * s)]
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


def tufts(d, path, n=12, length=(10, 22), lean=0.5, w=1.5, seed=0, inward=False):
    """A tufty hair edge along path: each tuft one pen stroke out to a point and back, of uneven size, all leaning
    the same way (lean: along the path, in tuft lengths). The outward side is to the left of the path's direction."""
    import random
    from kit import catmull
    r = random.Random(seed)
    C = catmull(path, False, 1.0)
    L = len(C)
    pts = [C[0]]
    for k in range(n):
        i0 = int(k / n * (L - 1)); i1 = int((k + 1) / n * (L - 1))
        a, b = C[i0], C[i1]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        tx, ty = b[0] - a[0], b[1] - a[1]
        nn = math.hypot(tx, ty) or 1
        tx, ty = tx / nn, ty / nn
        nx, ny = (ty, -tx) if not inward else (-ty, tx)
        ln = r.uniform(*length)
        pts.append((mx + nx * ln + tx * ln * lean, my + ny * ln + ty * ln * lean))
        pts.append(b)
    # draw as a few strokes so the pen lifts now and then
    i = 0
    while i < len(pts) - 1:
        j = min(len(pts), i + r.choice((5, 7, 9)))
        ink(d, pts[i:j], w=w, start=0.7, end=0.3, jit=0.3, retrace=0, seed=r.randint(0, 1 << 30))
        i = j - 1


def curls(d, path, n=10, r=(7, 12), w=1.5, seed=0, inward=False):
    """A curly hair edge along path: a row of round bumps, each its own small pen stroke that overshoots a little.
    The outward side is to the left of the path's direction (as in tufts)."""
    import random
    from kit import catmull
    rr = random.Random(seed)
    C = catmull(path, False, 1.0)
    L = len(C)
    for k in range(n):
        i0 = int(k / n * (L - 1)); i1 = int((k + 1) / n * (L - 1))
        a, b = C[i0], C[i1]
        tx, ty = b[0] - a[0], b[1] - a[1]
        nn = math.hypot(tx, ty) or 1
        ux, uy = tx / nn, ty / nn
        nx, ny = (uy, -ux) if not inward else (-uy, ux)
        h = rr.uniform(*r)
        o = rr.uniform(-0.12, 0.12) * nn
        pts = [(a[0] - nx * 2, a[1] - ny * 2),
               (a[0] + ux * (0.12 * nn + o) + nx * h * 0.75, a[1] + uy * (0.12 * nn + o) + ny * h * 0.75),
               (a[0] + ux * (0.5 * nn + o) + nx * h, a[1] + uy * (0.5 * nn + o) + ny * h),
               (b[0] - ux * 0.1 * nn + nx * h * 0.7, b[1] - uy * 0.1 * nn + ny * h * 0.7),
               (b[0] - nx * 3, b[1] - ny * 3)]
        ink(d, pts, w=w, start=0.6, end=0.25, jit=0.3, retrace=0, seed=rr.randint(0, 1 << 30))


def curl(d, x, y, r=6, rot=0, w=1.0, seed=None):
    """One small curl inside a mass of curly hair: an open hook of the pen, most of a turn."""
    pts = []
    for i in range(7):
        a = math.radians(rot) + i / 6 * 1.5 * math.pi
        k = r * (1 - 0.07 * i)
        pts.append((x + k * math.cos(a), y + k * math.sin(a) * 0.85))
    ink(d, pts, w=w, start=0.5, end=0.1, jit=0.3, retrace=0, seed=seed)


def chop(d, pts, w=1.5, seed=None):
    """Chopped hair ends: pts go base, tip, base, tip, … along the edge; every lock is two pen strokes that meet in
    a sharp point, of whatever length the points give."""
    for i in range(1, len(pts) - 1, 2):
        a, t, b = pts[i - 1], pts[i], pts[i + 1]
        s1 = None if seed is None else seed + i
        ink(d, [a, ((a[0] + t[0]) / 2 + (t[1] - a[1]) * 0.08, (a[1] + t[1]) / 2 - (t[0] - a[0]) * 0.08), t], w=w,
            start=0.6, end=0.12, jit=0.3, retrace=0, seed=s1)
        ink(d, [t, ((b[0] + t[0]) / 2 + (t[1] - b[1]) * 0.06, (b[1] + t[1]) / 2 - (t[0] - b[0]) * 0.06), b], w=w * 0.8,
            start=0.15, end=0.4, jit=0.3, retrace=0, seed=None if s1 is None else s1 + 50)


def offsets(center, widths):
    """Left and right edges of a tube along center with half-widths given per point."""
    L, R = [], []
    n = len(center)
    for i, (x, y) in enumerate(center):
        a = center[max(0, i - 1)]; b = center[min(n - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        nn = math.hypot(tx, ty) or 1
        nx, ny = -ty / nn, tx / nn
        w = widths[i] if isinstance(widths, (list, tuple)) else widths
        L.append((x + nx * w, y + ny * w)); R.append((x - nx * w, y - ny * w))
    return L, R


def tube(d, center, widths, color=None, opacity=0.6, w=1.8, sides=(True, True), wash_dx=0, wash_dy=0, seed=None):
    """A sleeve, a leg, a trouser leg: two pen lines along a centre line, and a wash between them.
    widths: half-width per centre point (or one number). sides: which edges to draw."""
    L, R = offsets(center, widths)
    if color:
        wash(d, L + R[::-1], color, opacity, wash_dx, wash_dy)
    if sides[0]:
        ink(d, L, w=w, start=0.6, end=0.3, seed=seed)
    if sides[1]:
        ink(d, R, w=w * 0.9, start=0.6, end=0.3, seed=None if seed is None else seed + 1)
    return L, R


def shoe(d, x, y, length=34, side=-1, color='#7a4a34', w=1.6):
    """A simple shoe seen from the side, toe pointing to side (-1 left)."""
    pts = [(x + side * -8, y - 12), (x + side * -10, y), (x + side * length, y + 2), (x + side * (length + 4), y - 4),
           (x + side * (length - 6), y - 12), (x + side * 8, y - 16)]
    wash(d, pts, color, 0.75, rough='S')
    ink(d, pts[:5], w=w, start=0.8, end=0.4)
