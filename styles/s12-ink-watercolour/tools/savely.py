"""Савелий Петрович, about 70, a watchmaker: grumpy outside, kind inside. Bald dome, a fringe of wild white hair,
bushy brows, round spectacles, a big soft nose, a drooping white moustache; a mustard waistcoat over a pale blue
shirt, a watch chain. Head units as Аня's; the face looks to the viewer's left in '34'."""
from kit import ink, dot, wash, blot, hatch, white
from parts import eye, brow, mouth, hand, tube, shoe, EXPR, SKIN_OLD, BLUSH

HAIR = '#b8b6c4'       # white hair: a pale cool grey wash, mostly paper
VEST = '#c98f3a'
SHIRT = '#a9cbe0'
TROUS = '#7a6f6a'


def glasses(d, e):
    # round wire spectacles, a little low on the nose
    for (x, y, r, rx) in [(-14, 4, 17, 1.0), (-64, 4, 13, 0.6)]:
        pts = []
        import math
        for i in range(13):
            a = i / 12 * 2 * math.pi
            pts.append((x + r * rx * math.cos(a), y + r * math.sin(a)))
        ink(d, pts, w=1.2, start=0.8, end=0.8, jit=0.4, retrace=0.5)
    ink(d, [(-31, 2), (-40, -2), (-52, 2)], w=1.1)
    ink(d, [(3, 2), (40, -6)], w=1.0)


def head34(d, expr='grump'):
    e = EXPR[expr]
    sq = e.get('squint', False)
    # washes: ruddy skin, a redder nose, pale grey hair
    wash(d, [(-54, -96), (0, -128), (70, -104), (96, -40), (86, 30), (50, 80), (0, 100), (-50, 96), (-72, 60),
             (-96, 30), (-74, -20)], SKIN_OLD, 0.52, dx=6, dy=4)
    blot(d, -86, 28, 13, BLUSH, 0.5)
    blot(d, 8, 30, 18, BLUSH, 0.35)
    wash(d, [(56, -96), (100, -80), (120, -40), (118, 10), (100, 40), (70, 50), (64, 0), (74, -60)], HAIR, 0.45)
    # crown and the back of the head
    ink(d, [(-56, -88), (-30, -116), (10, -128), (54, -118), (82, -92)], w=2.1, start=0.5, end=0.3)
    # wild white fringe at the back and over the ear: a few curling wisps, not a brush
    for k, pts in enumerate([[(78, -96), (96, -92), (104, -100)], [(92, -74), (110, -70), (118, -80)],
                             [(100, -50), (118, -40), (124, -50)], [(104, -24), (120, -12), (118, -2)],
                             [(100, 4), (110, 20), (104, 30)], [(84, -84), (100, -76)], [(98, -36), (112, -28)],
                             [(96, 14), (104, 30), (96, 40)]]):
        ink(d, pts, w=1.0, start=0.7, end=0.05, retrace=0, seed=300 + k)
    # ear
    ink(d, [(46, -8), (60, -18), (70, -4), (66, 20), (56, 34), (48, 30)], w=1.6, start=0.6, end=0.3)
    ink(d, [(54, 0), (60, 6), (56, 18)], w=1.0)
    # face contour: forehead, brow ridge, a big soft nose; moustache; small chin; jowl
    ink(d, [(-56, -84), (-66, -50), (-70, -26), (-76, -16), (-72, -6), (-84, 10), (-100, 26), (-102, 40),
            (-94, 46), (-82, 42)], w=2.2, start=0.5, end=0.3)
    ink(d, [(-82, 42), (-76, 34), (-80, 26)], w=1.3)            # nostril wing
    ink(d, [(-74, 70), (-70, 84), (-56, 96), (-34, 100), (-12, 96)], w=1.9, start=0.3, end=0.2)   # chin
    ink(d, [(-4, 94), (22, 82), (44, 58)], w=1.3, start=0.3, end=0.1)    # jowl
    # moustache: a white drooping massd
    wash(d, [(-96, 46), (-60, 44), (-20, 50), (-14, 70), (-40, 64), (-70, 70), (-90, 64)], HAIR, 0.45)
    for k, (x0, y0, x1, y1) in enumerate([(-86, 48, -96, 66), (-74, 48, -82, 70), (-60, 48, -64, 70),
                                          (-46, 50, -40, 70), (-32, 52, -20, 72), (-22, 54, -12, 70)]):
        ink(d, [(x0, y0), ((x0 + x1) / 2 + 1, (y0 + y1) / 2), (x1, y1)], w=1.0, start=0.8, end=0.05, retrace=0,
            seed=320 + k)
    ink(d, [(-90, 46), (-60, 42), (-30, 48), (-16, 58)], w=1.4, start=0.4, end=0.2)
    # mouth under the moustache: grumpy line, the far corner turned up a hair (kind inside)
    if e['mouth'] in ('flat', 'soft', 'grin'):
        ink(d, [(-68, 78), (-52, 78), (-40, 76)], w=1.5, start=0.4, end=0.3)
        if e['mouth'] != 'flat':
            ink(d, [(-40, 76), (-34, 71)], w=1.2)
    else:
        mouth(d, -56, 78, e['mouth'], 0.9, side=-1, lips=False)
    # stubble dots on the chin
    for x, y in [(-56, 88), (-46, 92), (-36, 90), (-26, 92), (-62, 84), (-16, 88)]:
        dot(d, x, y, 0.7)
    # eyes behind spectacles, under heavy brows
    eye(d, -14, 0, 0.9 * e['eye'], e['look'], e['lid'] + 0.1, side=1, squint=sq, seed=31)
    eye(d, -63, 0, 0.7 * e['eye'], e['look'], e['lid'] + 0.1, side=-1, squint=sq, seed=32)
    glasses(d, e)
    # bushy white brows: a pale wash and a sheaf of short strokes
    lift, tilt = e['lift'], e['tilt']
    for bx, L, side in [(-14, 30, 1), (-64, 18, -1)]:
        yi, yo = -26 - lift - tilt, -24 - lift + tilt * 0.3
        xi, xo = bx - side * L * 0.5, bx + side * L * 0.6
        wash(d, [(xi, yi - 4), (xo, yo - 8), (xo, yo + 2), (xi, yi + 4)], HAIR, 0.5)
        for k in range(5):
            t = k / 4
            x = xi + (xo - xi) * t
            y = yi + (yo - yi) * t
            ink(d, [(x, y + 3), (x + side * 6, y - 5 - 3 * (1 - abs(t - 0.5) * 2))], w=1.3, start=0.8, end=0.05,
                retrace=0, seed=340 + k + (bx > -40) * 10)
    # wrinkles: forehead, crow's feet, the fold by the nose
    for y in (-58, -48):
        ink(d, [(-46, y), (-20, y - 3), (8, y)], w=0.9, start=0.2, end=0.2, retrace=0)
    ink(d, [(14, -6), (24, -10)], w=0.8); ink(d, [(14, 4), (24, 6)], w=0.8)
    ink(d, [(-60, 30), (-46, 48), (-40, 62)], w=1.1, start=0.4, end=0.1)
    ink(d, [(-8, 22), (-2, 40)], w=0.8, start=0.4, end=0.1)


def bust(d, expr='grump'):
    """Head and shoulders, 600 x 720. He leans forward a little; shoulders rounded and narrow."""
    d.push(300, 262, 1.18, 4)
    # shirt, waistcoat (paper left light where the light falls)
    wash(d, [(-40, 146), (60, 128), (124, 160), (150, 230), (150, 300), (100, 316), (-60, 310), (-140, 316),
             (-150, 230), (-110, 170)], SHIRT, 0.55, dy=6)
    wash(d, [(-96, 186), (-50, 176), (-30, 240), (-12, 300), (-70, 312), (-110, 290), (-120, 230)], VEST, 0.66)
    wash(d, [(56, 160), (104, 180), (120, 250), (110, 300), (60, 306), (36, 240)], VEST, 0.6)
    # neck
    wash(d, [(-30, 92), (40, 70), (48, 150), (-24, 156)], SKIN_OLD, 0.45)
    ink(d, [(-24, 100), (-20, 148)], w=1.5, start=0.3, end=0.2)
    ink(d, [(40, 66), (46, 110), (52, 134)], w=1.3, start=0.3, end=0.2)
    ink(d, [(-12, 120), (0, 130), (10, 126)], w=0.8)
    head34(d, expr)
    # collar: open, a little crumpled
    ink(d, [(-28, 146), (-10, 172), (8, 148), (28, 168), (54, 134)], w=1.6, start=0.6, end=0.3)
    ink(d, [(-30, 144), (-50, 156)], w=1.4)
    # shoulders: rounded, going forward; the line runs out at the bottom
    ink(d, [(-50, 156), (-96, 168), (-130, 194), (-146, 240), (-152, 300)], w=2.2, start=0.6, end=0.05)
    ink(d, [(56, 134), (98, 150), (130, 180), (146, 230), (152, 290)], w=2.1, start=0.6, end=0.05)
    # waistcoat edges, buttons, the watch chain
    ink(d, [(-48, 178), (-30, 240), (-14, 300)], w=1.7, start=0.4, end=0.05)
    ink(d, [(-100, 190), (-116, 250), (-120, 300)], w=1.3, start=0.4, end=0.05)
    ink(d, [(56, 162), (42, 240), (40, 300)], w=1.7, start=0.4, end=0.05)
    ink(d, [(104, 182), (118, 250), (120, 296)], w=1.3, start=0.4, end=0.05)
    for y in (228, 270):
        dot(d, -28 + (y - 228) * 0.25, y, 2.8)
    ink(d, [(-24, 250), (10, 270), (50, 268), (78, 256)], w=1.0, retrace=0)
    wash(d, [(72, 250), (86, 246), (88, 262), (74, 264)], '#d9b24a', 0.8, rough='S')
    hatch(d, [(-96, 196), (-60, 186), (-44, 240), (-90, 250)], angle=70, gap=9, w=0.8, fill=0.6, seed=9)
    d.pop()


def watch(d, x, y, r=11):
    """A pocket watch: a gold round with a white face and two hands."""
    import math
    pts = [(x + r * math.cos(a), y + r * math.sin(a)) for a in [i / 10 * 2 * math.pi for i in range(10)]]
    wash(d, pts, '#e0b040', 0.75, rough='S')
    white(d, x, y, r * 0.7, r * 0.7)
    ink(d, pts + [pts[0]], w=1.3, retrace=0)
    ink(d, [(x, y - r), (x, y - r - 5)], w=1.4)
    ink(d, [(x, y), (x, y - r * 0.5)], w=0.9, retrace=0)
    ink(d, [(x, y), (x + r * 0.4, y + r * 0.1)], w=0.9, retrace=0)


def figure(d, expr='peer'):
    """Full figure, 600 x 1000. Stooped, peering at a pocket watch in his palm; the other hand behind his back."""
    # trousers: baggy, knees a little bent
    tube(d, [(300, 600), (292, 720), (282, 850)], [24, 21, 19], TROUS, 0.58, w=1.9, seed=70)
    tube(d, [(352, 604), (358, 724), (358, 846)], [24, 21, 19], TROUS, 0.5, w=1.8, seed=72)
    ink(d, [(290, 710), (298, 738)], w=0.9, retrace=0)
    ink(d, [(354, 716), (350, 744)], w=0.9, retrace=0)
    shoe(d, 280, 872, 40, -1, '#4f3a30')
    shoe(d, 362, 868, 40, -1, '#4f3a30')
    d.turn(330, 600, -14)         # the upper body bends forward from the hips; the back is round
    shirt = [(276, 352), (320, 330), (372, 350), (392, 420), (384, 510), (384, 600), (274, 600), (262, 510),
             (260, 420)]
    wash(d, shirt, SHIRT, 0.5)
    wash(d, [(300, 366), (350, 356), (380, 420), (380, 560), (334, 576), (318, 470)], VEST, 0.65, dx=3)
    wash(d, [(266, 396), (292, 376), (304, 480), (302, 580), (266, 580), (262, 490)], VEST, 0.6, dx=-3)
    ink(d, [(326, 330), (370, 344), (394, 400), (390, 480), (384, 560), (390, 604)], w=2.1, start=0.5, end=0.3)
    ink(d, [(272, 358), (262, 420), (260, 500), (266, 556), (272, 602)], w=2.0, start=0.5, end=0.3)
    ink(d, [(268, 600), (330, 608), (392, 602)], w=1.7, start=0.5, end=0.3)
    ink(d, [(298, 370), (308, 460), (302, 560), (298, 592)], w=1.5, start=0.3, end=0.2)
    for y in (440, 480, 520):
        dot(d, 304, y, 2.4)
    ink(d, [(306, 490), (324, 510), (342, 502)], w=0.9, retrace=0)
    # far arm, behind the back
    tube(d, [(364, 360), (392, 440), (384, 500)], [15, 13, 11], SHIRT, 0.5, w=1.7, seed=74)
    # near arm: forearm forward, palm up with the watch
    tube(d, [(290, 366), (272, 440), (268, 482), (238, 488), (212, 478)], [16, 15, 13, 11, 10], SHIRT, 0.55,
         w=1.8, seed=76)
    ink(d, [(252, 476), (250, 498)], w=1.2)       # rolled cuff
    ink(d, [(244, 476), (242, 498)], w=1.2)
    hand(d, 212, 480, 1.15, 100, 'hold', color=SKIN_OLD)
    watch(d, 190, 462, 11)
    # neck goes forward
    wash(d, [(272, 330), (310, 326), (318, 356), (278, 362)], SKIN_OLD, 0.42)
    ink(d, [(270, 336), (278, 362)], w=1.4)
    ink(d, [(306, 326), (320, 346)], w=1.2)
    d.push(258, 292, 0.56, 22)
    head34(d, expr)
    d.pop()
    d.pop(); d.pop()
