"""Марат, about 35, a cook: huge, loud, merry, generous. The biggest of the cast: a wide head on a short neck, short
dark curls, a thick black beard, thick brows, a broad nose, eyes that narrow when he laughs; a white cook's jacket
with rolled sleeves, a long terracotta apron, a towel over the shoulder, a ladle. His resting face is a wide smile
with teeth. Head units as the others' (the beard goes below the chin); the face looks to the viewer's left in '34'."""
import math
from kit import ink, dot, wash, blot, hatch, white, paper
from parts import extra, eye, brow, mouth, hand, tube, shoe, curls, curl, EXPR, BLUSH

SKIN_M = '#e9ac80'      # a warmer, ruddier skin than the others'
HAIR = '#2a211e'
APRON = '#d76a36'       # terracotta-orange
SHADE = '#c9bba6'       # the shade on the white jacket: warm grey, the white itself is paper
TROUS = '#59606e'
STEEL = '#93a0ad'

OPEN = {'smile': 0.3, 'laugh': 1.0}      # how far the jaw drops in his own two mouths


def dark(d, poly, op=0.8, **kw):
    """Dark hair takes two layers of wash."""
    wash(d, poly, HAIR, op, **kw)
    wash(d, poly, HAIR, op * 0.6, **kw)


def grin(d, xa, xb, y, op, ups, los):
    """His mouth: a wide open smile between the far corner xa and the near corner xb. Teeth are paper left white
    under the upper lip, the dark of the mouth below them, and a tongue when he laughs. ups / los: the y offsets
    of the upper and the lower lip line at five points from xa to xb. Returns the lowest y of the mouth."""
    T = (0, 0.2, 0.52, 0.84, 1)
    X = [xa + (xb - xa) * t for t in T]
    drop = 26 * op
    up = [(X[i], y + ups[i]) for i in range(5)]
    lo = [(X[i], y + los[i] + drop * math.sin(math.pi * T[i]) ** 0.7) for i in range(5)]
    th = 8 + 3 * op                                   # the height of the teeth
    tb = [(X[i], up[i][1] + th * math.sin(math.pi * T[i]) ** 0.6) for i in range(5)]
    if op > 0.6:
        tt = [(X[i], lo[i][1] - 11 * math.sin(math.pi * T[i])) for i in (1, 2, 3)]       # the top of the tongue
        wash(d, tb[1:4] + tt[::-1], '#7c2424', 0.85, rough='S')
        wash(d, [tt[0], (X[2], tt[1][1] - 4), tt[2], lo[3], lo[2], lo[1]], '#e2716c', 0.7, rough='S')
        ink(d, [tt[0], (X[2], tt[1][1] - 4), tt[2]], w=1.0, start=0.4, end=0.3, retrace=0)
        ink(d, [(X[2], tt[1][1] - 2), (X[2] + 1, lo[2][1] - 4)], w=0.7, retrace=0)
    else:
        wash(d, tb[1:4] + [lo[3], lo[2], lo[1]], '#7c2424', 0.85, rough='S')
    paper(d, up[:] + tb[::-1][1:4])
    ink(d, up, w=1.9, start=0.5, end=0.3)
    ink(d, [up[0]] + lo[1:4] + [up[4]], w=2.1, start=0.4, end=0.3)
    ink(d, tb[1:4], w=0.8, start=0.4, end=0.4, jit=0.3, retrace=0)
    for i in (1, 2, 3):                               # a few teeth, not a fence
        x = xa + (xb - xa) * (0.2 + 0.16 * i)
        ink(d, [(x, y + ups[2] + 1), (x, y + ups[2] + th - 2)], w=0.6, jit=0.2, retrace=0, alpha=0.7)
    return max(p[1] for p in lo)


def thick_brow(d, x, y, length, e, side, k=1.0, seed=None):
    brow(d, x, y, length, e['lift'] * k, e['tilt'] * k, side=side, w=2.9, arch=5, seed=seed)
    brow(d, x, y + 3, length * 0.8, e['lift'] * k, e['tilt'] * k, side=side, w=2.0, arch=4,
         seed=None if seed is None else seed + 5)


def head34(d, expr='merry'):
    e = EXPR[expr]
    sq = e.get('squint', False)
    op = OPEN.get(e['mouth'])
    dr = 12 * (op or 0)                       # the jaw and the beard go down with the laugh
    wash(d, [(-60, -92), (-74, -30), (-102, 24), (-90, 50), (-80, 80), (-40, 104), (20, 100), (70, 70), (96, 10),
             (84, -70), (10, -110)], SKIN_M, 0.5, dx=5, dy=3)
    blot(d, 8, 20, 21, BLUSH, 0.5)
    blot(d, -90, 30, 12, BLUSH, 0.42)
    # hair: a cap of short dark curls
    dark(d, [(-70, -58), (-66, -112), (-20, -142), (40, -144), (96, -114), (118, -60), (110, -12), (90, -20),
             (80, -44), (54, -62), (10, -78), (-30, -76)], 0.85, dx=-2)
    curls(d, [(-70, -56), (-72, -100), (-40, -131), (10, -145), (58, -137), (98, -108), (118, -62), (112, -16)],
          n=10, r=(7, 13), w=1.8, seed=601)
    for k, (x, y, r, a) in enumerate([(-52, -66, 9, 60), (-22, -76, 10, 100), (14, -76, 9, 70), (48, -62, 9, 30)]):
        curl(d, x, y, r, a, w=1.3, seed=604 + k)
    for k, (x, y, r, a) in enumerate([(-30, -108, 7, 20), (8, -116, 8, 200), (46, -108, 7, 90), (78, -84, 7, 300),
                                      (92, -48, 6, 150), (20, -100, 5, 40)]):
        curl(d, x, y, r * 1.5, a, w=1.0, seed=610 + k)
    # ear
    ink(d, [(60, -8), (76, -22), (90, -6), (86, 22), (74, 36), (64, 30)], w=1.7, start=0.6, end=0.3)
    ink(d, [(70, -2), (78, 6), (72, 20)], w=1.0)
    # forehead, brow ridge, a broad round nose
    ink(d, [(-68, -54), (-72, -40), (-74, -24), (-80, -13), (-78, -3), (-88, 12), (-100, 26), (-101, 37), (-93, 44),
            (-83, 40)], w=2.3, start=0.4, end=0.3)
    ink(d, [(-83, 41), (-76, 33), (-80, 24)], w=1.4)
    # the mouth, in the gap the beard leaves
    if op is not None:
        mb = grin(d, -92, -20, 60, op, (-5, 1, 2, -5, -14), (-2, 10, 12, 4, -14))
    else:
        mouth(d, -58, 62, e['mouth'], e.get('ms', 1.0) * 1.3, side=-1, lips=False)
        mb = 62 + 12 * e.get('ms', 1.0)
    mb = max(mb, 74)
    # moustache and beard: dark washes with a curly edge
    dark(d, [(-100, 46), (-80, 43), (-50, 47), (-24, 38), (-10, 40), (-16, 52), (-30, 55), (-52, 61), (-76, 60),
             (-96, 55)], 0.7, rough='S')
    beard = [(-98, 60), (-102, 84 + dr), (-84, 110 + dr), (-50, 128 + dr), (-6, 130 + dr), (40, 114 + dr * 0.6),
             (72, 78), (86, 38), (66, 34), (60, -22), (48, -20), (42, 12), (22, 36), (-4, 42), (-16, 54),
             (-30, mb + 2), (-56, mb + 8), (-80, mb + 3), (-92, 64)]
    dark(d, beard, 0.85)
    curls(d, [(-96, 62), (-103, 84 + dr), (-86, 110 + dr), (-50, 129 + dr), (-6, 131 + dr), (40, 115 + dr * 0.6),
              (73, 78), (84, 44)], n=9, r=(7, 13), w=1.7, seed=620, inward=True)
    curls(d, [(50, -18), (42, 12), (22, 36), (-2, 42)], n=5, r=(4, 7), w=1.1, seed=621)
    ink(d, [(-98, 47), (-80, 42), (-50, 46), (-26, 38)], w=1.3, start=0.4, end=0.2)
    for k, (x, y, r, a) in enumerate([(-70, 96, 6, 30), (-36, 108, 7, 200), (6, 104, 7, 100), (40, 84, 6, 300),
                                      (56, 50, 5, 20), (-14, 80, 5, 160), (30, 56, 5, 250)]):
        curl(d, x, y + dr * 0.7, r * 1.5, a, w=1.0, seed=630 + k)
    # eyes that narrow with the smile: the cheek pushes the lower lid up
    eye(d, -22, -4, 1.2 * e['eye'], e['look'], e['lid'], side=1, squint=sq, seed=71)
    eye(d, -66, -4, 0.9 * e['eye'], e['look'], e['lid'], side=-1, squint=sq, seed=72)
    if op is not None:
        ink(d, [(-36, 13), (-22, 9), (-7, 13)], w=1.0, start=0.3, end=0.3, retrace=0)
        ink(d, [(-5, -8), (5, -12)], w=0.8, retrace=0)
        ink(d, [(-4, -2), (7, -2)], w=0.8, retrace=0)
        ink(d, [(-10, 26), (-2, 34), (-6, 44)], w=1.1, start=0.4, end=0.1, retrace=0)
    thick_brow(d, -20, -30, 36, e, 1, seed=73)
    thick_brow(d, -66, -30, 18, e, -1, 0.7, seed=74)
    extra(d, e, -22, -4, 8, 20, -66)


def head_front(d, expr='merry'):
    e = EXPR[expr]
    sq = e.get('squint', False)
    op = OPEN.get(e['mouth'])
    dr = 12 * (op or 0)
    wash(d, [(-88, -70), (-94, 0), (-84, 56), (-50, 96), (0, 106), (50, 96), (84, 56), (94, 0), (88, -70),
             (0, -104)], SKIN_M, 0.5, dx=4, dy=3)
    blot(d, -46, 22, 19, BLUSH, 0.48)
    blot(d, 46, 22, 19, BLUSH, 0.48)
    blot(d, 0, 30, 12, BLUSH, 0.35)
    dark(d, [(-96, -30), (-106, -84), (-64, -136), (0, -150), (64, -136), (106, -84), (96, -30), (80, -52),
             (30, -74), (-30, -74), (-80, -52)], 0.85)
    curls(d, [(-94, -26), (-106, -84), (-64, -133), (0, -148), (64, -133), (106, -84), (94, -26)], n=12,
          r=(7, 13), w=1.8, seed=640)
    for k, (x, y, r, a) in enumerate([(-66, -56, 9, 80), (-36, -70, 10, 60), (-2, -74, 9, 110), (34, -70, 10, 60), (66, -56, 9, 100)]):
        curl(d, x, y, r, a, w=1.3, seed=644 + k)
    for k, (x, y, r, a) in enumerate([(-56, -100, 7, 20), (-16, -116, 8, 200), (30, -112, 7, 90), (66, -92, 7, 300)]):
        curl(d, x, y, r * 1.5, a, w=1.0, seed=650 + k)
    for sgn in (-1, 1):
        ink(d, [(sgn * 90, -14), (sgn * 106, -22), (sgn * 114, -2), (sgn * 106, 24), (sgn * 92, 30)], w=1.6,
            start=0.6, end=0.3)
        ink(d, [(sgn * 90, -44), (sgn * 94, -10)], w=1.9, start=0.3, end=0.2)
    # a broad nose: the round tip and two wings
    ink(d, [(-5, -6), (-9, 16)], w=1.1, start=0.3, end=0.2)
    ink(d, [(-22, 24), (-21, 36), (-9, 39), (0, 43), (10, 39), (21, 36), (22, 24)], w=1.9, start=0.5, end=0.5)
    if op is not None:
        mb = grin(d, -42, 42, 62, op, (-10, 0, 3, 0, -10), (-8, 8, 13, 8, -8))
    else:
        mouth(d, 0, 64, e['mouth'], e.get('ms', 1.0) * 1.15, side=-1, lips=False)
        mb = 64 + 12 * e.get('ms', 1.0)
    mb = max(mb, 76)
    dark(d, [(-50, 50), (-24, 44), (0, 48), (24, 44), (50, 50), (40, 60), (0, 62), (-40, 60)], 0.7, rough='S')
    beard = [(-92, -24), (-98, 40), (-86, 96 + dr), (-46, 128 + dr), (0, 136 + dr), (46, 128 + dr),
             (86, 96 + dr), (98, 40), (92, -24), (80, -20), (72, 26), (56, 46), (46, 60), (34, mb + 2), (0, mb + 9),
             (-34, mb + 2), (-46, 60), (-56, 46), (-72, 26), (-80, -20)]
    dark(d, beard, 0.85)
    curls(d, [(98, 30), (88, 96 + dr), (46, 129 + dr), (0, 137 + dr), (-46, 129 + dr), (-88, 96 + dr), (-98, 30)],
          n=11, r=(7, 13), w=1.7, seed=660)
    curls(d, [(-80, -14), (-72, 26), (-56, 46)], n=4, r=(4, 7), w=1.1, seed=661, inward=True)
    curls(d, [(56, 46), (72, 26), (80, -14)], n=4, r=(4, 7), w=1.1, seed=662, inward=True)
    ink(d, [(-48, 51), (-24, 44), (0, 49), (24, 44), (48, 51)], w=1.3, start=0.3, end=0.3)
    for k, (x, y, r, a) in enumerate([(-60, 84, 6, 30), (-28, 110, 7, 200), (10, 114, 7, 100), (50, 96, 6, 300),
                                      (70, 60, 5, 20), (-74, 50, 5, 160)]):
        curl(d, x, y + dr * 0.7, r * 1.5, a, w=1.0, seed=670 + k)
    eye(d, -36, -4, 1.15 * e['eye'], e['look'], e['lid'], side=-1, squint=sq, seed=75)
    eye(d, 36, -4, 1.15 * e['eye'], e['look'], e['lid'], side=1, squint=sq, seed=76)
    if op is not None:
        for sgn in (-1, 1):
            ink(d, [(sgn * 50, 13), (sgn * 36, 9), (sgn * 22, 13)], w=1.0, start=0.3, end=0.3, retrace=0)
            ink(d, [(sgn * 53, -8), (sgn * 63, -12)], w=0.8, retrace=0)
            ink(d, [(sgn * 54, -2), (sgn * 64, -2)], w=0.8, retrace=0)
    thick_brow(d, -36, -30, 34, e, -1, seed=77)
    thick_brow(d, 36, -30, 34, e, 1, seed=78)


def head_side(d, expr='merry'):
    e = EXPR[expr]
    sq = e.get('squint', False)
    op = OPEN.get(e['mouth'])
    dr = 12 * (op or 0)
    wash(d, [(-60, -92), (-76, -30), (-104, 24), (-92, 50), (-84, 80), (-50, 104), (0, 100), (40, 60), (50, -30),
             (10, -106)], SKIN_M, 0.5, dx=4, dy=3)
    blot(d, -34, 20, 20, BLUSH, 0.48)
    blot(d, -98, 30, 12, BLUSH, 0.42)
    dark(d, [(-70, -58), (-66, -112), (-20, -142), (40, -146), (98, -116), (118, -60), (112, 0), (90, 30),
             (62, 20), (50, -40), (20, -66), (-30, -76)], 0.85, dx=-2)
    curls(d, [(-70, -56), (-72, -100), (-40, -131), (10, -146), (60, -138), (100, -110), (120, -62), (114, -4),
              (92, 30)], n=11, r=(7, 13), w=1.8, seed=680)
    for k, (x, y, r, a) in enumerate([(-54, -64, 9, 60), (-26, -76, 10, 100), (6, -72, 9, 70), (36, -50, 9, 20)]):
        curl(d, x, y, r, a, w=1.3, seed=684 + k)
    for k, (x, y, r, a) in enumerate([(-30, -108, 7, 20), (8, -116, 8, 200), (50, -108, 7, 90), (86, -80, 7, 300),
                                      (96, -36, 6, 150), (60, -60, 6, 40), (84, 0, 5, 220)]):
        curl(d, x, y, r * 1.5, a, w=1.0, seed=690 + k)
    ink(d, [(22, -8), (40, -22), (54, -6), (50, 22), (36, 34), (26, 28)], w=1.7, start=0.6, end=0.3)
    ink(d, [(32, -2), (40, 6), (34, 20)], w=1.0)
    ink(d, [(-68, -54), (-73, -40), (-76, -24), (-82, -13), (-80, -3), (-92, 12), (-105, 26), (-106, 37),
            (-97, 44), (-86, 40)], w=2.3, start=0.4, end=0.3)
    ink(d, [(-88, 41), (-80, 33), (-84, 24)], w=1.4)
    if op is not None:
        mb = grin(d, -98, -46, 60, op, (-3, 2, 1, -6, -14), (-1, 8, 10, 2, -14))
    else:
        mouth(d, -70, 62, e['mouth'], e.get('ms', 1.0), side=-1, lips=False)
        mb = 62 + 12 * e.get('ms', 1.0)
    mb = max(mb, 74)
    dark(d, [(-104, 46), (-84, 43), (-56, 46), (-40, 40), (-34, 46), (-44, 54), (-70, 60), (-98, 56)], 0.7,
         rough='S')
    beard = [(-102, 60), (-106, 84 + dr), (-90, 110 + dr), (-56, 128 + dr), (-14, 128 + dr), (22, 106 + dr * 0.6),
             (44, 70), (50, 34), (30, 34), (24, -22), (10, -20), (4, 12), (-14, 36), (-34, 44), (-42, 54),
             (-52, mb + 2), (-72, mb + 7), (-90, mb + 2), (-98, 64)]
    dark(d, beard, 0.85)
    curls(d, [(-100, 62), (-107, 84 + dr), (-92, 110 + dr), (-56, 129 + dr), (-14, 129 + dr), (23, 106 + dr * 0.6),
              (45, 70), (50, 42)], n=9, r=(7, 13), w=1.7, seed=700, inward=True)
    curls(d, [(12, -18), (4, 12), (-14, 36), (-34, 44)], n=5, r=(4, 7), w=1.1, seed=701)
    ink(d, [(-102, 47), (-84, 42), (-56, 46), (-42, 40)], w=1.3, start=0.4, end=0.2)
    for k, (x, y, r, a) in enumerate([(-76, 96, 6, 30), (-44, 108, 7, 200), (-6, 102, 7, 100), (20, 76, 6, 300),
                                      (26, 46, 5, 20), (-30, 70, 5, 160)]):
        curl(d, x, y + dr * 0.7, r * 1.5, a, w=1.0, seed=710 + k)
    eye(d, -56, -4, 1.1 * e['eye'], (-1, e['look'][1]), e['lid'], side=-1, squint=sq, seed=79)
    if op is not None:
        ink(d, [(-68, 10), (-58, 6), (-46, 10)], w=1.0, start=0.3, end=0.3, retrace=0)
        ink(d, [(-44, -8), (-34, -12)], w=0.8, retrace=0)
        ink(d, [(-43, -2), (-32, -2)], w=0.8, retrace=0)
    thick_brow(d, -56, -30, 26, e, -1, seed=80)


def towel(d, pts, stripes=((0.72, 0.8), (0.86, 0.92))):
    """A kitchen towel hanging over the shoulder: paper white, a shade, two terracotta stripes near its end.
    pts: four corners, top-left, top-right, bottom-right, bottom-left."""
    a, b, c, e_ = pts
    wash(d, pts, SHADE, 0.3, rough='S')
    for t0, t1 in stripes:
        q = [(a[0] + (e_[0] - a[0]) * t0, a[1] + (e_[1] - a[1]) * t0), (b[0] + (c[0] - b[0]) * t0, b[1] + (c[1] - b[1]) * t0),
             (b[0] + (c[0] - b[0]) * t1, b[1] + (c[1] - b[1]) * t1), (a[0] + (e_[0] - a[0]) * t1, a[1] + (e_[1] - a[1]) * t1)]
        wash(d, q, APRON, 0.75, rough='S')
    ink(d, [a, ((a[0] + e_[0]) / 2 - 2, (a[1] + e_[1]) / 2), e_], w=1.5, start=0.6, end=0.4)
    ink(d, [b, ((b[0] + c[0]) / 2 + 2, (b[1] + c[1]) / 2), c], w=1.4, start=0.6, end=0.4)
    ink(d, [e_, ((e_[0] + c[0]) / 2, (e_[1] + c[1]) / 2 + 3), c], w=1.3, start=0.5, end=0.5)
    ink(d, [((a[0] + b[0]) / 2, a[1] + 14), ((e_[0] + c[0]) / 2 + 2, (e_[1] + c[1]) / 2 - 40)], w=0.8, start=0.4,
        end=0.05, retrace=0)


def bust(d, expr='merry'):
    """Head and shoulders, 600 x 720: he fills the page — heavy shoulders, no neck to speak of, the head thrown
    back a little in a laugh."""
    d.push(292, 246, 1.0, 3)
    # the white jacket is paper; a warm grey shade down the far side and under the beard
    wash(d, [(-234, 250), (-214, 186), (-176, 170), (-166, 240), (-176, 340), (-240, 340)], SHADE, 0.32)
    wash(d, [(150, 150), (226, 190), (246, 330), (190, 336), (176, 230)], SHADE, 0.25)
    # the apron's bib and its strap
    wash(d, [(-116, 262), (104, 256), (112, 350), (-126, 352)], APRON, 0.7, dy=4)
    wash(d, [(46, 130), (72, 106), (116, 250), (92, 258)], APRON, 0.6, rough='S')
    wash(d, [(-88, 142), (-70, 132), (-98, 260), (-116, 262)], APRON, 0.6, rough='S')
    # a short thick neck behind the beard
    wash(d, [(30, 96), (84, 60), (92, 116), (40, 136)], SKIN_M, 0.45)
    d.push(0, 0, 1.0, -7)
    head34(d, expr)
    d.pop()
    ink(d, [(78, 66), (84, 96), (96, 112)], w=1.4, start=0.3, end=0.2)
    # the stand-up collar, open; the double-breasted flap
    ink(d, [(-92, 136), (-58, 150), (-30, 176), (-12, 208)], w=1.8, start=0.5, end=0.3)
    ink(d, [(94, 110), (70, 122), (30, 150), (-12, 208)], w=1.8, start=0.5, end=0.3)
    ink(d, [(-12, 208), (-18, 258)], w=1.4, start=0.5, end=0.2)
    for x, y in [(-56, 226), (24, 222)]:
        ink(d, [(x - 5, y), (x, y - 5), (x + 5, y), (x, y + 5), (x - 5, y)], w=1.0, retrace=0)
    # heavy shoulders: the line starts hard and runs out below
    ink(d, [(-96, 134), (-150, 146), (-204, 172), (-234, 232), (-244, 340)], w=2.5, start=0.6, end=0.05)
    ink(d, [(98, 108), (150, 124), (206, 156), (238, 216), (250, 330)], w=2.4, start=0.6, end=0.05)
    ink(d, [(-188, 220), (-182, 290), (-186, 340)], w=1.1, start=0.4, end=0.05)
    ink(d, [(-118, 262), (-10, 258), (104, 256)], w=1.6, start=0.5, end=0.4)
    ink(d, [(-70, 134), (-96, 200), (-116, 262)], w=1.3, start=0.4, end=0.3)
    ink(d, [(74, 110), (100, 190), (104, 256)], w=1.3, start=0.4, end=0.3)
    ink(d, [(-120, 264), (-126, 350)], w=1.3, start=0.4, end=0.05)
    ink(d, [(106, 258), (112, 340)], w=1.3, start=0.4, end=0.05)
    towel(d, [(126, 114), (176, 136), (206, 300), (150, 312)])
    d.pop()


def bust_view(d, view, expr='merry'):
    """Head and shoulders for the turnaround; frame 500 x 620."""
    d.push(250, 228, 0.86)
    if view == 'front':
        body = [(-70, 126), (70, 126), (170, 150), (230, 200), (250, 290), (254, 420), (-254, 420), (-250, 290),
                (-230, 200), (-170, 150)]
        bib = [(-112, 270), (112, 270), (118, 420), (-118, 420)]
        straps = [[(-112, 270), (-96, 200), (-72, 140)], [(112, 270), (96, 200), (72, 140)]]
        collar = [[(-74, 134), (-40, 160), (-6, 214)], [(74, 134), (40, 160), (-6, 214)]]
    elif view == 'side':
        body = [(-60, 130), (30, 110), (100, 140), (130, 200), (140, 300), (140, 420), (-150, 420), (-150, 300),
                (-130, 200), (-100, 150)]
        bib = [(-150, 270), (-60, 270), (-56, 420), (-160, 420)]
        straps = [[(-130, 270), (-90, 200), (-40, 136)]]
        collar = [[(-66, 136), (-30, 150), (20, 126)]]
    else:
        body = [(-96, 134), (40, 124), (150, 124), (206, 156), (238, 216), (250, 300), (252, 420), (-246, 420),
                (-240, 300), (-234, 232), (-204, 172), (-150, 146)]
        bib = [(-116, 270), (104, 264), (112, 420), (-126, 420)]
        straps = [[(-116, 270), (-96, 200), (-70, 138)], [(104, 264), (100, 190), (74, 112)]]
        collar = [[(-92, 136), (-58, 150), (-30, 176), (-12, 214)], [(94, 110), (70, 122), (30, 150), (-12, 214)]]
    xs = [p[0] for p in body]
    wash(d, [(min(xs) + 4, 230), (min(xs) + 60, 170), (min(xs) + 96, 260), (min(xs) + 70, 420), (min(xs), 420)],
         SHADE, 0.4)
    wash(d, bib, APRON, 0.7, dy=4)
    for s_ in straps:
        wash(d, [(s_[0][0] - 9, s_[0][1]), (s_[1][0] - 9, s_[1][1]), (s_[2][0] - 9, s_[2][1]), (s_[2][0] + 9, s_[2][1]),
                 (s_[1][0] + 9, s_[1][1]), (s_[0][0] + 9, s_[0][1])], APRON, 0.6, rough='S')
        ink(d, [(p[0] - 9, p[1]) for p in s_], w=1.2, start=0.4, end=0.3)
        ink(d, [(p[0] + 9, p[1]) for p in s_], w=1.2, start=0.4, end=0.3)
    {'front': head_front, '34': head34, 'side': head_side}[view](d, expr)
    for c in collar:
        ink(d, c, w=1.8, start=0.5, end=0.3)
    L = sorted([p for p in body if p[0] < 0], key=lambda p: p[1])
    R = sorted([p for p in body if p[0] > 0], key=lambda p: p[1])
    ink(d, L, w=2.4, start=0.6, end=0.05)
    ink(d, R, w=2.3, start=0.6, end=0.05)
    ink(d, [bib[0], ((bib[0][0] + bib[1][0]) / 2, bib[0][1] - 3), bib[1]], w=1.6, start=0.5, end=0.4)
    ink(d, [bib[0], bib[3]], w=1.3, start=0.4, end=0.05)
    ink(d, [bib[1], bib[2]], w=1.3, start=0.4, end=0.05)
    d.pop()


def ladle(d, x0, y0, x1, y1):
    """A ladle: the handle from (x0, y0) to the bowl at (x1, y1)."""
    ink(d, [(x0, y0), ((x0 + x1) / 2 + 3, (y0 + y1) / 2), (x1, y1)], w=2.4, start=0.9, end=0.8, retrace=0.6)
    ux, uy = x1 - x0, y1 - y0
    n = math.hypot(ux, uy) or 1
    ux, uy = ux / n, uy / n
    bowl = [(x1 + (-uy) * a * 20 + ux * b * 24, y1 + ux * a * 20 + uy * b * 24)
            for a, b in [(-1, 0), (-0.9, 0.7), (0, 1.1), (0.9, 0.7), (1, 0)]]
    wash(d, bowl, STEEL, 0.6, rough='S')
    ink(d, bowl, w=1.8, start=0.7, end=0.6)
    ink(d, [bowl[0], (x1 - ux * 4, y1 - uy * 4), bowl[4]], w=1.3, start=0.5, end=0.5)


def clog(d, x, y, s=1.5):
    d.push(x, y, s)
    shoe(d, 0, 0, 36, -1, '#4a3a34', w=1.3)
    d.pop()


def figure(d, expr='joy'):
    """Full figure, 600 x 1000. He laughs with the whole body: leaning back, the belly forward, the head thrown
    back, a ladle raised like a toast, the other fist on the hip."""
    # legs under the apron: thick, planted apart; kitchen clogs
    tube(d, [(236, 690), (240, 780), (238, 850)], [31, 28, 25], TROUS, 0.58, w=1.9, seed=110)
    tube(d, [(350, 690), (364, 780), (372, 848)], [31, 28, 25], TROUS, 0.5, w=1.8, seed=112)
    clog(d, 228, 878)
    clog(d, 370, 874)
    d.turn(300, 720, 8)            # the whole upper body leans back from the knees
    # the white jacket is paper; shade under the raised arm and down the back
    wash(d, [(196, 330), (226, 322), (222, 400), (228, 470), (160, 474), (158, 410)], SHADE, 0.35)
    wash(d, [(392, 330), (424, 372), (438, 470), (376, 476), (384, 400)], SHADE, 0.28)
    # the long apron: a bib, tied at the waist over the belly, down to the shins
    apron = [(232, 384), (352, 380), (362, 476), (438, 486), (446, 600), (434, 714), (300, 722), (164, 716),
             (140, 600), (142, 482), (226, 478)]
    wash(d, apron, APRON, 0.7, dx=3, dy=3)
    ink(d, [(232, 384), (292, 380), (352, 380)], w=1.7, start=0.5, end=0.4)
    ink(d, [(232, 384), (226, 478)], w=1.5, start=0.5, end=0.3)
    ink(d, [(352, 380), (362, 476)], w=1.5, start=0.5, end=0.3)
    ink(d, [(142, 484), (226, 480), (300, 486), (362, 478), (438, 486)], w=1.6, start=0.4, end=0.3)
    ink(d, [(142, 484), (132, 540), (140, 620), (164, 716)], w=2.2, start=0.5, end=0.3)        # the belly leads
    ink(d, [(444, 566), (446, 620), (442, 670), (434, 712)], w=1.9, start=0.3, end=0.3)
    ink(d, [(162, 716), (230, 726), (300, 720), (370, 726), (436, 712)], w=1.7, start=0.5, end=0.5)
    for x0, x1 in [(210, 214), (330, 340), (396, 404)]:
        ink(d, [(x0, 530), ((x0 + x1) / 2 - 4, 620), (x1, 700)], w=0.9, start=0.2, end=0.1, retrace=0)
    ink(d, [(250, 556), (252, 606), (304, 608), (306, 556)], w=1.1, start=0.4, end=0.3, retrace=0)     # a pocket
    # the apron's straps to the neck
    for a, b in [((232, 384), (252, 300)), ((352, 380), (336, 296))]:
        wash(d, [(a[0] - 7, a[1]), (b[0] - 7, b[1]), (b[0] + 7, b[1]), (a[0] + 7, a[1])], APRON, 0.6, rough='S')
        ink(d, [(a[0] - 7, a[1]), (b[0] - 7, b[1])], w=1.1, start=0.4, end=0.3)
        ink(d, [(a[0] + 7, a[1]), (b[0] + 7, b[1])], w=1.1, start=0.4, end=0.3)
    # the jacket's outline: the chest and belly one round line in front; the back breaks where the fist sits
    ink(d, [(196, 340), (170, 384), (150, 440), (142, 484)], w=2.3, start=0.5, end=0.3)
    ink(d, [(414, 410), (434, 450), (438, 486)], w=2.0, start=0.3, end=0.3)
    for x, y in [(268, 340), (318, 338)]:
        ink(d, [(x - 4, y), (x, y - 4), (x + 4, y), (x, y + 4), (x - 4, y)], w=0.9, retrace=0)
    # the arm on the hip: a rolled sleeve, a thick bare forearm, a fist
    tube(d, [(398, 318), (450, 370), (478, 432)], [28, 27, 25], None, w=2.0, seed=114)
    wash(d, [(424, 356), (462, 410), (480, 440), (456, 446), (430, 400)], SHADE, 0.3)
    tube(d, [(478, 436), (460, 488), (432, 520)], [21, 20, 18], SKIN_M, 0.5, w=1.9, seed=116)
    ink(d, [(454, 424), (478, 442), (500, 434)], w=1.5, start=0.5, end=0.4)
    ink(d, [(452, 434), (476, 452), (498, 446)], w=1.2, start=0.5, end=0.4)
    hand(d, 434, 514, 1.6, 50, 'fist', color=SKIN_M)
    # the towel over that shoulder
    towel(d, [(366, 292), (398, 298), (410, 416), (376, 424)])
    # the raised arm: sleeve to the elbow, forearm up, the ladle in the fist
    ladle(d, 92, 190, 122, 40)
    tube(d, [(204, 318), (156, 306), (116, 272)], [27, 26, 24], None, w=2.0, seed=118)
    wash(d, [(200, 340), (156, 330), (124, 300), (134, 292), (164, 310), (204, 322)], SHADE, 0.3)
    tube(d, [(114, 272), (98, 214), (100, 168)], [20, 19, 17], SKIN_M, 0.5, w=1.9, seed=120)
    ink(d, [(92, 268), (114, 276), (136, 262)], w=1.5, start=0.5, end=0.4)
    ink(d, [(94, 258), (114, 266), (134, 252)], w=1.2, start=0.5, end=0.4)
    hand(d, 98, 172, 1.6, 174, 'fist', color=SKIN_M)
    # shoulders: one heavy line each side of the head
    ink(d, [(244, 290), (218, 296), (204, 310)], w=2.2, start=0.5, end=0.3)
    ink(d, [(344, 286), (380, 292), (398, 310)], w=2.1, start=0.5, end=0.3)
    ink(d, [(254, 296), (276, 312), (294, 304), (316, 310), (338, 292)], w=1.6, start=0.5, end=0.4)
    d.push(284, 190, 0.72, -9)
    head34(d, expr)
    d.pop()
    d.pop(); d.pop()
