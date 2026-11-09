"""Кира, about 15: prickly, closed, defiant; vulnerable underneath. Thin and angular, a slouch, the head down and
the look from under the brows, sideways. Short choppy dark hair, a long fringe over one eye (the far one in '34'),
a mouth pressed shut or a crooked half-smirk — she never smiles openly, and her 'joy' is that smirk grown a
little. An oversized dark plum hoodie, acid-lime headphones round the neck, narrow charcoal trousers, heavy boots
with lime laces. Head units as the others'; a longer face than a child's, eyes smaller than Аня's."""
import math
from kit import ink, dot, wash, blot, hatch, paper, gouache, gouache_line
from parts import extra, eye, brow, mouth, hand, chop, tube, EXPR, SKIN, BLUSH, SHADOW

HAIR = '#2a1f2e'
HOOD = '#5a3260'        # dark plum
TROUS = '#3a3a44'       # charcoal
ACID = '#c4e01c'        # the one sharp accent: headphones, laces


def dark(d, poly, color=HAIR, op=0.85, **kw):
    """Dark colours take two layers of wash."""
    wash(d, poly, color, op, **kw)
    wash(d, poly, color, op * 0.6, **kw)


def her(expr):
    """Her face for an expression: joy is not a laugh but the half-smirk, a little warmer."""
    e = dict(EXPR[expr])
    if expr == 'joy':
        e.update(mouth='grin', squint=False, lid=0.25, look=(1.0, 0.2), lift=5, tilt=2, warm=True)
    return e


def lips(d, e, x, y, k=1.0, side=-1):
    """Her mouth, x at its middle: pressed shut, or the crooked half-smirk (the near corner goes up)."""
    m = e['mouth']
    if m in ('flat', 'soft'):
        ink(d, [(x + side * 13 * k, y - 1), (x, y + 1), (x - side * 11 * k, y), (x - side * 16 * k, y + 4)], w=1.6,
            start=0.5, end=0.3)
        ink(d, [(x + side * 4, y + 8), (x - side * 5, y + 8)], w=0.8, jit=0.2, retrace=0)
    elif m == 'grin':
        ink(d, [(x + side * 13 * k, y + 1), (x, y + 2), (x - side * 12 * k, y - 2), (x - side * 18 * k, y - 9)],
            w=1.7, start=0.5, end=0.25)
        ink(d, [(x - side * 20 * k, y - 13), (x - side * 23 * k, y - 6)], w=1.0, retrace=0)
        ink(d, [(x + side * 4, y + 9), (x - side * 5, y + 9)], w=0.8, jit=0.2, retrace=0)
    else:
        mouth(d, x - side * 7, y, m, e.get('ms', 1.0) * 0.8, side=side, lips=False)


def her_eye(d, x, y, s, e, side, seed, look=None):
    """A smaller eye with a heavy dark upper lid and a tired shade under it."""
    sq = e.get('squint', False)
    wash(d, [(x - 10 * s, y + 9 * s), (x + 10 * s, y + 9 * s), (x + 8 * s, y + 15 * s), (x - 8 * s, y + 15 * s)],
         SHADOW, 0.3, rough='S')
    eye(d, x, y, s * e['eye'], look or e['look'], e['lid'], lash=True, side=side, squint=sq, seed=seed)
    if not sq:
        top = y - 8.4 * s * e['eye'] * (1 - e['lid'] * 1.1)
        ink(d, [(x - 9 * s, y - 1 + e['lid'] * 2), (x, top - 1.5), (x + 9 * s, y - 1 + e['lid'] * 2)], w=2.0,
            start=0.5, end=0.4, retrace=0, seed=seed + 7)


def studs(d, pts):
    for x, y in pts:
        dot(d, x, y, 1.9)


def head34(d, expr='sulk'):
    e = her(expr)
    wash(d, [(-54, -86), (-66, -30), (-82, 22), (-70, 50), (-62, 84), (-42, 104), (0, 96), (34, 58), (48, 0),
             (40, -70), (0, -96)], SKIN, 0.4, dx=5, dy=3)
    blot(d, 4, 32, 14, BLUSH, 0.42 if e.get('warm') else 0.2)
    # the back of the hair: short, the ends chopped into uneven points
    back = [(102, -44), (110, -4), (96, -8), (104, 28), (86, 18), (88, 50), (70, 34), (62, 60), (52, 26)]
    dark(d, [(-40, -122), (10, -134), (58, -122), (92, -90)] + back + [(52, 0), (48, -30), (40, -70), (0, -100)],
         dx=-2)
    ink(d, [(-44, -116), (-10, -131), (30, -133), (68, -118), (92, -90), (102, -44)], w=2.1, start=0.5, end=0.3)
    chop(d, back, seed=801)
    # a lock in front of the ear, to the jaw
    dark(d, [(40, -40), (56, -24), (58, 16), (46, 50), (42, 8)], rough='S')
    chop(d, [(40, -30), (46, 50), (56, 6)], w=1.3, seed=806)
    # the lobe of the ear under the hair, two studs
    studs(d, [(54, 40), (60, 28)])
    # nose: small, straight, a sharp tip; lips; a longer, pointed chin; an angular jaw
    ink(d, [(-62, -24), (-64, -12), (-63, -5), (-71, 10), (-81, 23), (-78, 29), (-68, 30)], w=2.0, start=0.4,
        end=0.25)
    ink(d, [(-67, 37), (-70, 44), (-66, 49), (-68, 55), (-66, 72), (-60, 92), (-48, 103), (-34, 104)], w=2.0,
        start=0.3, end=0.15)
    ink(d, [(-24, 102), (6, 86), (30, 56)], w=1.3, start=0.2, end=0.1, retrace=0)
    ink(d, [(-73, 26), (-68, 22)], w=1.0, retrace=0)
    her_eye(d, -18, -2, 1.05, e, 1, 81)
    brow(d, -15, -21, 26, e['lift'], e['tilt'], side=1, w=2.0, arch=1, seed=83)
    lips(d, e, -58, 55)
    extra(d, e, -18, -2, 4, 32, -60)
    # the fringe: from a parting on the near side, across the forehead, long uneven locks down over the far eye
    edge = [(-80, 42), (-68, 2), (-57, 28), (-48, -6), (-37, 8), (-30, -26), (-12, -42), (4, -34), (14, -48),
            (30, -34), (46, -30)]
    dark(d, [(24, -126), (-30, -124), (-66, -98), (-86, -54), (-91, -4)] + edge + [(46, -80)])
    ink(d, [(-34, -122), (-66, -98), (-86, -56), (-92, -6), (-80, 42)], w=2.0, start=0.5, end=0.1)
    chop(d, [(-92, -6)] + edge[:6], w=1.4, seed=812)
    ink(d, [(-30, -26), (-12, -42), (4, -36)], w=1.2, start=0.3, end=0.1, retrace=0)
    for k, pts in enumerate([[(18, -124), (-20, -100), (-50, -62), (-62, -20)], [(26, -118), (2, -86), (-18, -56)],
                             [(30, -114), (40, -74), (48, -36)]]):
        ink(d, pts, w=1.1, start=0.5, end=0.05, retrace=0, seed=810 + k)


def head_front(d, expr='sulk'):
    e = her(expr)
    wash(d, [(-54, -60), (-58, 0), (-50, 50), (-28, 90), (0, 106), (28, 90), (50, 50), (58, 0), (54, -60),
             (0, -90)], SKIN, 0.4, dx=4, dy=3)
    blot(d, 30, 34, 14, BLUSH, 0.4 if e.get('warm') else 0.2)
    left = [(-56, 26), (-64, 56), (-70, 22), (-82, 34), (-78, -4), (-88, -14)]
    right = [(88, -14), (78, -2), (84, 32), (70, 20), (66, 54), (56, 24)]
    dark(d, left + [(-74, -88), (-32, -132), (30, -134), (74, -88)] + right + [(58, -30), (40, -70), (-40, -70),
                                                                              (-58, -30)])
    ink(d, [(-54, 24), (-47, 56), (-27, 89), (-5, 105)], w=2.0, start=0.3, end=0.15)
    ink(d, [(54, -4), (54, 22), (47, 56), (27, 89), (7, 104)], w=1.8, start=0.3, end=0.15)
    ink(d, [(-3, -2), (-5, 18), (-8, 26), (-2, 31), (6, 28)], w=1.4, start=0.3, end=0.2)
    her_eye(d, 27, -3, 1.05, e, 1, 85)
    brow(d, 28, -22, 26, e['lift'], e['tilt'], side=1, w=2.0, arch=1, seed=87)
    lips(d, e, 0, 58, side=-1)
    ink(d, [(-80, -20), (-75, -88), (-34, -130), (0, -137), (34, -131), (75, -88), (80, -20)], w=2.1, start=0.4,
        end=0.3)
    chop(d, left, seed=820)
    chop(d, right, seed=824)
    studs(d, [(60, 40)])
    # the fringe, over the eye on the viewer's left
    edge = [(-74, 40), (-63, 4), (-52, 30), (-42, -2), (-32, 14), (-22, -22), (-6, -38), (8, -32), (18, -46),
            (34, -34), (56, -30)]
    dark(d, [(30, -132), (-30, -132), (-72, -96), (-82, -30)] + edge + [(66, -44), (70, -80)])
    chop(d, [(-82, -30)] + edge[:6], w=1.4, seed=830)
    ink(d, [(-22, -22), (-6, -38), (8, -34)], w=1.2, start=0.3, end=0.1, retrace=0)
    for k, pts in enumerate([[(22, -126), (-18, -100), (-48, -60), (-58, -14)], [(28, -118), (6, -84), (-12, -50)],
                             [(28, -124), (52, -90), (62, -50), (64, -40)]]):
        ink(d, pts, w=1.1, start=0.5, end=0.05, retrace=0, seed=834 + k)


def head_side(d, expr='sulk'):
    e = her(expr)
    wash(d, [(-54, -86), (-66, -30), (-84, 22), (-72, 50), (-64, 86), (-46, 104), (-8, 96), (12, 50), (20, -40),
             (-10, -92)], SKIN, 0.4, dx=4, dy=3)
    blot(d, -30, 32, 15, BLUSH, 0.4 if e.get('warm') else 0.2)
    back = [(102, -44), (110, -2), (96, -6), (104, 32), (84, 22), (84, 56), (64, 38), (54, 62), (40, 30), (34, 56),
            (24, 10)]
    dark(d, [(-50, -118), (0, -134), (50, -124), (90, -92)] + back + [(10, -40), (-20, -70), (-50, -80),
                                                                     (-70, -90)], dx=-2)
    ink(d, [(-64, -24), (-66, -12), (-65, -5), (-74, 10), (-85, 23), (-82, 29), (-71, 30)], w=2.0, start=0.4,
        end=0.25)
    ink(d, [(-70, 37), (-74, 44), (-69, 49), (-72, 55), (-69, 72), (-63, 92), (-51, 103), (-37, 104)], w=2.0,
        start=0.3, end=0.15)
    ink(d, [(-27, 102), (-6, 88), (8, 62)], w=1.3, start=0.2, end=0.1)
    ink(d, [(-77, 26), (-72, 22)], w=1.0, retrace=0)
    her_eye(d, -50, -2, 1.0, e, -1, 89, look=(-1, e['look'][1]))
    brow(d, -48, -21, 21, e['lift'], e['tilt'], side=-1, w=1.9, arch=1, seed=91)
    m = e['mouth']
    if m in ('flat', 'soft'):
        ink(d, [(-73, 54), (-60, 55), (-54, 59)], w=1.6, start=0.5, end=0.3)
    elif m == 'grin':
        ink(d, [(-73, 55), (-60, 54), (-52, 47)], w=1.7, start=0.5, end=0.25)
    else:
        mouth(d, -64, 55, m, 0.8, side=-1, lips=False)
    studs(d, [(16, 40), (22, 28)])
    ink(d, [(-54, -114), (-10, -132), (40, -130), (84, -102), (102, -44)], w=2.1, start=0.5, end=0.3)
    chop(d, back, seed=840)
    for k, pts in enumerate([[(-14, -122), (8, -84), (22, -40), (26, -4)], [(10, -126), (44, -88), (62, -36)]]):
        ink(d, pts, w=1.0, start=0.5, end=0.05, retrace=0, seed=850 + k)
    # the fringe hangs in front of the forehead, its points past the brow
    edge = [(-82, 30), (-76, -10), (-70, 8), (-64, -40)]
    dark(d, [(-20, -124), (-60, -106), (-82, -70), (-89, -20)] + edge + [(-50, -64), (-20, -78)], rough='S')
    ink(d, [(-24, -124), (-60, -106), (-83, -70), (-90, -22)], w=2.0, start=0.5, end=0.2)
    chop(d, [(-90, -22)] + edge, w=1.4, seed=860)
    ink(d, [(-10, -116), (-48, -92), (-68, -56), (-74, -24)], w=1.1, start=0.5, end=0.05, retrace=0, seed=866)


def cup(d, x, y, rx=18, ry=23, rot=0):
    """One cup of the headphones, lying on the collarbone: acid lime, a dark cushion ring."""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    el = lambda k: [(x + rx * k * math.cos(a) * c - ry * k * math.sin(a) * s, y + rx * k * math.cos(a) * s + ry * k * math.sin(a) * c)
                    for a in [i / 10 * 2 * math.pi for i in range(10)]]
    gouache(d, el(1.0), ACID)
    P = el(1.0)
    ink(d, P + [P[0], P[1]], w=1.6, start=0.8, end=0.6, retrace=0)
    Q = el(0.45)
    ink(d, Q + [Q[0]], w=1.0, retrace=0)
    dot(d, x, y, rx * 0.16)


def band(d, pts, w=6):
    """A piece of the headphones' band."""
    ink(d, pts, w=w + 2.4, start=1, end=1, jit=0.2, press=0.1, retrace=0)
    gouache_line(d, pts, w, ACID, start=1, end=1, jit=0.2, press=0.1)


def bust(d, expr='sulk'):
    """Head and shoulders, 600 x 720: narrow sloping shoulders in a hoodie too big for her, the head pushed forward
    and down, the eye up and sideways."""
    d.push(310, 268, 1.12, 0)
    dark(d, [(-44, 150), (30, 140), (92, 152), (132, 190), (150, 260), (154, 330), (-150, 330), (-146, 260),
             (-122, 192), (-82, 162)], HOOD, 0.8, dy=5)
    # the hood, heaped behind the neck
    dark(d, [(14, 100), (66, 90), (106, 118), (116, 162), (66, 156), (30, 144)], HOOD, 0.8)
    wash(d, [(-38, 92), (14, 86), (22, 146), (-34, 152)], SKIN, 0.36)
    ink(d, [(-36, 100), (-36, 126), (-32, 146)], w=1.3, start=0.3, end=0.2)
    d.push(-16, 10, 1.0, 9)
    head34(d, expr)
    d.pop()
    ink(d, [(22, 94), (64, 88), (106, 116), (118, 160)], w=2.0, start=0.5, end=0.3)
    ink(d, [(34, 110), (70, 112), (96, 134)], w=1.0, start=0.4, end=0.1, retrace=0)
    # shoulders: sloping, the line trails off
    ink(d, [(-56, 156), (-96, 170), (-126, 196), (-146, 256), (-152, 326)], w=2.1, start=0.6, end=0.05)
    ink(d, [(104, 158), (132, 190), (150, 256), (156, 320)], w=2.0, start=0.6, end=0.05)
    # neckline and the strings
    ink(d, [(-40, 148), (-14, 166), (16, 164), (34, 146)], w=1.6, start=0.5, end=0.4)
    for x in (-18, 6):
        ink(d, [(x, 166), (x - 3, 220), (x + 1, 262)], w=1.1, start=0.5, end=0.3, retrace=0)
        ink(d, [(x + 1, 262), (x + 1, 274)], w=2.4, retrace=0)
    for x, y in [(-116, 240), (-104, 286), (116, 232), (124, 284)]:
        ink(d, [(x, y), (x + 3, y + 22)], w=0.8, start=0.6, end=0.1, retrace=0)
    # headphones round the neck
    band(d, [(-58, 150), (-48, 134), (-36, 126)])
    band(d, [(52, 142), (44, 128), (30, 122)])
    cup(d, -62, 172, 19, 25, 12)
    cup(d, 58, 164, 19, 25, -14)
    d.pop()


def bust_view(d, view, expr='sulk'):
    """Head and hoodie shoulders for the turnaround; frame 500 x 620."""
    d.push(250, 240, 1.0)
    if view == 'front':
        body = [(-40, 146), (40, 146), (96, 160), (130, 200), (146, 270), (150, 360), (-150, 360), (-146, 270),
                (-130, 200), (-96, 160)]
        hood = [(-52, 100), (-66, 130), (-50, 156), (50, 156), (66, 130), (52, 100)]
        cups = [(-58, 170, 12), (58, 170, -12)]
        bands = [[(-54, 150), (-46, 136), (-36, 130)], [(54, 150), (46, 136), (36, 130)]]
        neck = (-24, 26)
    elif view == 'side':
        body = [(-44, 150), (20, 142), (60, 160), (84, 210), (92, 280), (94, 360), (-84, 360), (-84, 280),
                (-76, 200), (-64, 164)]
        hood = [(6, 96), (60, 92), (96, 124), (100, 170), (50, 160), (16, 144)]
        cups = [(-10, 172, 0)]
        bands = [[(-6, 152), (2, 138), (12, 130)]]
        neck = (-34, 12)
    else:
        body = [(-44, 150), (30, 140), (92, 152), (132, 190), (150, 260), (154, 360), (-150, 360), (-146, 260),
                (-122, 192), (-82, 162)]
        hood = [(14, 100), (66, 90), (106, 118), (116, 162), (66, 156), (30, 144)]
        cups = [(-62, 172, 12), (58, 164, -14)]
        bands = [[(-58, 150), (-48, 134), (-36, 126)], [(52, 142), (44, 128), (30, 122)]]
        neck = (-34, 18)
    dark(d, body, HOOD, 0.8, dy=5)
    dark(d, hood, HOOD, 0.8)
    wash(d, [(neck[0], 88), (neck[1], 86), (neck[1] + 6, 148), (neck[0], 152)], SKIN, 0.36)
    ink(d, [(neck[0], 98), (neck[0] + 1, 146)], w=1.3, start=0.3, end=0.2)
    if view == 'front':
        ink(d, [(neck[1], 98), (neck[1] - 1, 146)], w=1.2, start=0.3, end=0.2)
    {'front': head_front, '34': head34, 'side': head_side}[view](d, expr)
    if view != 'front':
        ink(d, [hood[0], hood[1], hood[2], hood[3]], w=2.0, start=0.5, end=0.3)
    else:
        ink(d, [(-50, 104), (-66, 130), (-52, 154)], w=1.8, start=0.5, end=0.3)
        ink(d, [(50, 104), (66, 130), (52, 154)], w=1.8, start=0.5, end=0.3)
    L = sorted([p for p in body if p[0] < 0], key=lambda p: p[1])
    R = sorted([p for p in body if p[0] > 0], key=lambda p: p[1])
    ink(d, L, w=2.1, start=0.6, end=0.05)
    ink(d, R, w=2.0, start=0.6, end=0.05)
    ink(d, [L[0], ((L[0][0] + R[0][0]) / 2, L[0][1] + 18), R[0]], w=1.6, start=0.5, end=0.4)
    for b_ in bands:
        band(d, b_)
    for x, y, r in cups:
        cup(d, x, y, 19, 25, r)
    d.pop()


def boot(d, x, y, s=1.0):
    """A heavy boot, toe to the viewer's left: a tall shaft, a thick sole, acid laces."""
    d.push(x, y, s)
    dark(d, [(-12, -52), (13, -52), (15, 0), (-40, 2), (-45, -10), (-36, -21), (-13, -25)], TROUS, 0.85,
         rough='S')
    ink(d, [(-12, -52), (-13, -25), (-36, -20), (-46, -9), (-41, 3)], w=1.7, start=0.6, end=0.4)
    ink(d, [(13, -52), (15, -20), (15, 3)], w=1.6, start=0.6, end=0.4)
    ink(d, [(-13, -53), (0, -55), (13, -53)], w=1.4)
    ink(d, [(-42, 5), (-10, 6), (17, 5)], w=3.2, start=0.9, end=0.9, jit=0.3, retrace=0)       # the sole
    for k in range(4):
        yy = -44 + k * 8
        gouache_line(d, [(-13 - k * 0.5, yy), (-2, yy + 3)], 2.6, ACID, start=1, end=0.8)
    d.pop()


def figure(d, expr='sulk'):
    """Full figure, 600 x 1000. A slouch: the hips forward, the back round, the head pushed forward and down; one
    hand deep in the hoodie's pocket, the elbow out, the other hanging with her phone; one knee turned in."""
    # legs: long and thin; the near knee turns in
    tube(d, [(298, 586), (270, 716), (286, 838)], [13, 10, 9], TROUS, 0.8, w=1.7, seed=130)
    tube(d, [(334, 586), (362, 712), (352, 838)], [13, 10, 9], TROUS, 0.7, w=1.7, seed=132)
    ink(d, [(264, 710), (276, 720)], w=1.0, retrace=0)
    ink(d, [(354, 710), (368, 714)], w=1.0, retrace=0)
    boot(d, 290, 880, 1.05)
    boot(d, 358, 878, 1.05)
    d.turn(316, 600, 9)
    # the hoodie: too big, to the hips; the back round, the front hollow
    body = [(274, 324), (304, 314), (346, 320), (372, 376), (380, 460), (374, 592), (316, 602), (258, 594),
            (256, 470), (266, 390)]
    wash(d, body, HOOD, 0.8, dx=2, dy=3)
    wash(d, [(300, 330), (346, 326), (372, 380), (378, 470), (372, 590), (330, 598), (336, 470)], HOOD, 0.45)
    dark(d, [(316, 286), (358, 288), (382, 322), (368, 342), (334, 328)], HOOD, 0.8, rough='S')      # the hood
    ink(d, [(320, 284), (356, 286), (384, 320), (372, 342)], w=1.9, start=0.5, end=0.3)
    ink(d, [(256, 520), (258, 594)], w=1.8, start=0.3, end=0.3)
    ink(d, [(372, 342), (384, 392), (384, 440)], w=2.0, start=0.4, end=0.2)          # the round back
    ink(d, [(258, 594), (316, 604), (376, 590)], w=1.8, start=0.5, end=0.4)
    for x in (276, 304, 332, 358):
        ink(d, [(x, 586), (x + 1, 600)], w=0.8, retrace=0)
    ink(d, [(288, 524), (296, 492), (346, 492), (356, 524)], w=1.2, start=0.4, end=0.3, retrace=0)    # the pocket
    # the far arm hangs, long; the sleeve to the knuckles, the phone in her fingers
    tube(d, [(354, 336), (388, 430), (384, 536)], [15, 14, 12], HOOD, 0.55, w=1.8, seed=134)
    hand(d, 384, 538, 0.85, 4, 'hold', color=SKIN)
    gouache(d, [(376, 566), (390, 564), (394, 598), (380, 600)], '#cfe0ea')
    ink(d, [(374, 562), (392, 560), (396, 600), (378, 602), (374, 562)], w=1.6, retrace=0)
    # the near arm: the elbow out, the hand deep in the pocket
    tube(d, [(278, 336), (232, 420), (294, 506)], [15, 14, 12], HOOD, 0.55, w=1.9, seed=136)
    # neck, headphones
    wash(d, [(278, 298), (304, 294), (312, 326), (284, 330)], SKIN, 0.36)
    band(d, [(278, 322), (284, 310), (292, 304)], 4)
    band(d, [(330, 316), (324, 306), (316, 300)], 4)
    cup(d, 274, 336, 11, 15, 12)
    cup(d, 334, 330, 11, 15, -14)
    d.push(272, 254, 0.52, 13)
    head34(d, expr)
    d.pop()
    d.pop(); d.pop()
