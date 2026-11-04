"""Тим, about 8: mischievous, curious. A big round head, spiky ginger hair, ears that stick out, an upturned nose,
freckles, a gap in his grin; a red-and-white striped jumper, navy shorts. Head units as the others'."""
import math
from kit import ink, dot, wash, blot, hatch
from parts import extra, eye, brow, mouth, hand, tufts, tube, shoe, EXPR, SKIN, BLUSH

HAIR = '#e2862e'
JUMPER = '#d9453a'
SHORTS = '#4b6fae'


def head34(d, expr='smirk'):
    e = EXPR[expr]
    sq = e.get('squint', False)
    wash(d, [(-60, -70), (-74, -20), (-92, 16), (-80, 40), (-70, 70), (-40, 86), (10, 84), (60, 60), (80, 0),
             (60, -70), (0, -90)], SKIN, 0.5, dx=5, dy=3)
    blot(d, -56, 34, 14, BLUSH, 0.5)
    blot(d, 14, 34, 18, BLUSH, 0.42)
    # hair: a ginger mop with spikes
    wash(d, [(-74, -66), (-70, -110), (-20, -140), (40, -136), (100, -100), (116, -40), (104, 10), (80, -10),
             (50, -50), (0, -70), (-40, -62)], HAIR, 0.7, dx=-2)
    # a tufty mop, swept back: the outline is all tufts, the fringe tufts point down
    tufts(d, [(-70, -56), (-74, -90), (-50, -120), (-10, -136), (40, -132), (84, -108), (108, -66), (110, -20),
              (100, 6)], n=16, length=(10, 24), lean=0.6, w=1.7, seed=401)
    tufts(d, [(44, -72), (20, -80), (-10, -82), (-40, -76), (-64, -62)], n=7, length=(10, 20), lean=0.5, w=1.4,
          seed=402)
    for k, (x, y) in enumerate([(-20, -108), (14, -112), (50, -104), (76, -76), (90, -40)]):
        ink(d, [(x, y), (x + 10, y + 8), (x + 22, y + 10)], w=0.9, start=0.6, end=0.05, retrace=0, seed=410 + k)
    # ear, sticking out
    ink(d, [(56, -10), (76, -26), (92, -12), (88, 16), (72, 30), (58, 26)], w=1.7, start=0.6, end=0.3)
    ink(d, [(66, -6), (76, 0), (70, 14)], w=1.0)
    wash(d, [(60, -16), (86, -20), (90, 14), (64, 28)], BLUSH, 0.3, rough='S')
    # face contour: forehead, brow, a small upturned nose; then lip, a round chin, the jaw
    ink(d, [(-64, -58), (-70, -36), (-72, -14), (-80, 2), (-92, 14), (-88, 22), (-80, 22)], w=2.0, start=0.4,
        end=0.3)
    ink(d, [(-80, 26), (-77, 34)], w=1.6, start=0.6, end=0.4)
    ink(d, [(-76, 50), (-72, 62), (-58, 72), (-40, 77), (-20, 76)], w=2.0, start=0.3, end=0.2)
    ink(d, [(-8, 75), (24, 66), (52, 44)], w=1.3, start=0.2, end=0.1, retrace=0)
    ink(d, [(-84, 20), (-80, 16)], w=1.0)
    # eyes: round, looking sideways — he's up to something
    eye(d, -20, 4, 1.25 * e['eye'], e['look'], e['lid'], side=1, squint=sq, seed=41)
    eye(d, -62, 4, 0.95 * e['eye'], e['look'], e['lid'], side=-1, squint=sq, seed=42)
    brow(d, -18, -20, 22, e['lift'] + 3, e['tilt'], side=1, w=1.5, seed=43)
    brow(d, -62, -18, 14, e['lift'] - 1, e['tilt'] * 0.6, side=-1, w=1.3, arch=2, seed=44)
    # mouth: a lopsided grin with a gap tooth
    if e['mouth'] == 'grin':
        wash(d, [(-72, 40), (-56, 45), (-36, 38), (-42, 48), (-60, 50)], '#c4473f', 0.6, rough='S')
        ink(d, [(-76, 38), (-62, 44), (-44, 43), (-30, 32)], w=1.9, start=0.6, end=0.2)
        ink(d, [(-70, 42), (-58, 49), (-46, 47)], w=1.0, retrace=0)
        ink(d, [(-58, 43), (-58, 47)], w=0.9, retrace=0)
        ink(d, [(-30, 32), (-27, 28)], w=1.1)
    else:
        mouth(d, -58, 42, e['mouth'], e.get('ms', 1.0), side=-1, lips=False)
    extra(d, e, -20, 4, 14, 34, -60)
    for x, y in [(-46, 22), (-40, 28), (-50, 30), (-34, 20), (-6, 24), (2, 30), (-12, 32), (-66, 26)]:
        dot(d, x, y, 0.9)


def bust(d, expr='smirk'):
    """Head and shoulders, 600 x 720; a child: a big head on narrow shoulders."""
    d.push(300, 290, 1.2, -3)
    wash(d, [(-30, 120), (40, 110), (110, 140), (130, 210), (130, 270), (-120, 270), (-130, 200), (-90, 140)],
         JUMPER, 0.25, dy=4)
    # stripes
    for k, y in enumerate([150, 186, 222, 258]):
        wash(d, [(-120, y - 6), (-40, y - 4), (40, y - 8), (124, y - 4), (128, y + 12), (40, y + 10),
                 (-40, y + 14), (-124, y + 12)], JUMPER, 0.72, angle=0)
    wash(d, [(-24, 88), (34, 80), (40, 126), (-20, 130)], SKIN, 0.45)
    ink(d, [(-18, 94), (-18, 120)], w=1.4, start=0.3, end=0.2)
    ink(d, [(34, 82), (36, 112)], w=1.2, start=0.3, end=0.2)
    d.push(0, 16)                 # a child's short neck: the head sits low on the collar
    head34(d, expr)
    d.pop()
    # jumper: a round neck, narrow shoulders, the line runs out
    ink(d, [(-24, 122), (6, 134), (40, 118)], w=1.6, start=0.6, end=0.5)
    ink(d, [(-26, 118), (4, 128), (38, 112)], w=1.1)
    ink(d, [(-26, 122), (-80, 134), (-112, 160), (-126, 210), (-130, 270)], w=2.1, start=0.6, end=0.05)
    ink(d, [(40, 116), (90, 128), (118, 156), (128, 220), (128, 260)], w=2.0, start=0.6, end=0.05)
    d.pop()


def jar(d, x, y):
    """A jam jar with a green beetle inside."""
    pts = [(x - 16, y - 18), (x - 18, y + 16), (x - 12, y + 22), (x + 12, y + 22), (x + 18, y + 16), (x + 16, y - 18)]
    wash(d, pts, '#a6d0dc', 0.4, rough='S')
    ink(d, pts, w=1.3)
    ink(d, [(x - 18, y - 22), (x + 18, y - 22)], w=1.6)
    wash(d, [(x - 4, y + 4), (x + 6, y + 2), (x + 7, y + 12), (x - 3, y + 13)], '#4f9a3a', 0.8, rough='S')
    ink(d, [(x - 4, y + 6), (x - 9, y + 2)], w=0.8, retrace=0)
    ink(d, [(x + 6, y + 4), (x + 11, y)], w=0.8, retrace=0)
    ink(d, [(x - 10, y - 10), (x - 10, y + 6)], w=0.7, retrace=0, alpha=0.5)


def figure(d, expr='smirk'):
    """Full figure, 600 x 1000. On tiptoe, leaning forward, peering; a jam jar with a beetle hidden behind his back."""
    d.push(0, 66)
    # legs: thin, one stepping forward, on the toes; socks and sneakers
    tube(d, [(282, 600), (268, 680), (256, 756)], [13, 10, 8], SKIN, 0.45, w=1.6, seed=80)
    tube(d, [(330, 600), (346, 678), (368, 748)], [13, 10, 8], SKIN, 0.4, w=1.6, seed=82)
    ink(d, [(260, 676), (274, 682)], w=1.0, retrace=0)       # knees
    ink(d, [(340, 676), (352, 678)], w=1.0, retrace=0)
    tube(d, [(257, 752), (254, 790)], 8, None, w=1.3)
    tube(d, [(368, 746), (378, 782)], 8, None, w=1.3)
    wash(d, [(246, 760), (266, 760), (266, 766), (246, 766)], JUMPER, 0.7, rough='S')
    wash(d, [(364, 756), (384, 754), (385, 760), (365, 762)], JUMPER, 0.7, rough='S')
    shoe(d, 256, 806, 34, -1, '#3d6fb6')
    d.push(386, 802, 1, -30)
    shoe(d, 0, 0, 30, -1, '#3d6fb6')
    d.pop()
    # shorts
    shorts = [(262, 520), (348, 520), (362, 606), (316, 612), (306, 576), (296, 612), (252, 606)]
    wash(d, shorts, SHORTS, 0.66)
    ink(d, [(262, 520), (252, 606), (296, 612), (306, 576), (316, 612), (362, 606), (348, 520)], w=1.8, start=0.5,
        end=0.4)
    d.turn(300, 530, -9)          # the whole upper body leans forward
    jumper = [(244, 380), (338, 380), (358, 450), (356, 532), (258, 534), (244, 450)]
    wash(d, jumper, JUMPER, 0.22)
    for y in (396, 428, 460, 492, 520):
        wash(d, [(244, y - 6), (300, y - 7), (356, y - 8), (356, y + 6), (300, y + 8), (246, y + 7)], JUMPER, 0.72,
             angle=-9)
    ink(d, [(246, 384), (236, 440), (246, 500), (256, 534)], w=1.9, start=0.5, end=0.3)
    ink(d, [(340, 384), (358, 440), (358, 500), (356, 532)], w=1.8, start=0.5, end=0.3)
    ink(d, [(254, 530), (306, 538), (358, 530)], w=1.6, start=0.5, end=0.3)
    # arms behind the back, the jar in his hands
    tube(d, [(334, 392), (366, 440), (384, 488)], [14, 12, 10], JUMPER, 0.45, w=1.7, seed=84)
    tube(d, [(252, 396), (280, 452), (334, 484)], [14, 12, 10], JUMPER, 0.45, w=1.7, seed=86)
    jar(d, 398, 504)
    hand(d, 386, 492, 0.95, -30, 'hold', color=SKIN)
    # neck
    wash(d, [(258, 350), (288, 346), (294, 386), (256, 388)], SKIN, 0.42)
    ink(d, [(262, 354), (262, 380)], w=1.3)
    ink(d, [(288, 348), (292, 378)], w=1.2)
    ink(d, [(250, 382), (272, 394), (300, 380)], w=1.4)
    d.push(256, 300, 0.66, -6)
    head34(d, expr)
    d.pop()
    d.pop(); d.pop()
    d.pop()


def head_front(d, expr='smirk'):
    e = EXPR[expr]
    sq = e.get('squint', False)
    wash(d, [(-80, -70), (-84, 0), (-70, 50), (-40, 80), (0, 88), (40, 80), (70, 50), (84, 0), (80, -70),
             (0, -90)], SKIN, 0.5, dx=4, dy=3)
    blot(d, -44, 34, 14, BLUSH, 0.45)
    blot(d, 44, 34, 14, BLUSH, 0.45)
    wash(d, [(-92, -40), (-100, -90), (-60, -136), (0, -150), (60, -136), (100, -90), (92, -40), (70, -60),
             (0, -76), (-70, -60)], HAIR, 0.7)
    tufts(d, [(-84, -40), (-96, -86), (-60, -126), (0, -140), (60, -126), (96, -86), (86, -40)], n=18,
          length=(10, 22), lean=0.3, w=1.7, seed=470)
    tufts(d, [(54, -68), (20, -80), (-20, -80), (-56, -68)], n=8, length=(10, 18), lean=0.2, w=1.4, seed=471)
    # ears both sides
    for sgn in (-1, 1):
        ink(d, [(sgn * 78, -16), (sgn * 98, -24), (sgn * 106, -4), (sgn * 98, 18), (sgn * 80, 22)], w=1.6, start=0.6,
            end=0.3)
        wash(d, [(sgn * 80, -18), (sgn * 104, -18), (sgn * 100, 16), (sgn * 82, 20)], BLUSH, 0.3, rough='S')
    # round face: two contours
    ink(d, [(-80, -50), (-84, 0), (-72, 46), (-44, 76), (-6, 86)], w=2.0, start=0.3, end=0.15)
    ink(d, [(80, -50), (84, 0), (72, 46), (44, 76), (8, 85)], w=1.8, start=0.3, end=0.15)
    # an upturned button nose: nostrils and a curve
    ink(d, [(-10, 22), (-4, 27), (4, 27), (10, 22)], w=1.5, start=0.6, end=0.6)
    ink(d, [(-2, 6), (-6, 16)], w=1.0)
    dot(d, -5, 24, 1.3); dot(d, 5, 24, 1.3)
    eye(d, -32, -2, 1.2 * e['eye'], e['look'], e['lid'], side=-1, squint=sq, seed=61)
    eye(d, 32, -2, 1.2 * e['eye'], e['look'], e['lid'], side=1, squint=sq, seed=62)
    brow(d, -32, -26, 22, e['lift'] + 4, e['tilt'], side=-1, w=1.5, seed=63)
    brow(d, 32, -26, 22, e['lift'] - 2, e['tilt'], side=1, w=1.5, seed=64)
    if e['mouth'] == 'grin':
        wash(d, [(-22, 46), (0, 50), (24, 42), (14, 52), (-8, 54)], '#c4473f', 0.55, rough='S')
        ink(d, [(-30, 40), (-10, 48), (14, 47), (32, 34)], w=1.9, start=0.6, end=0.2)
        ink(d, [(-22, 46), (-4, 54), (16, 50)], w=1.0, retrace=0)
        ink(d, [(-2, 48), (-2, 52)], w=0.9, retrace=0)
    else:
        mouth(d, 0, 46, e['mouth'], 1.0, side=-1, lips=False)
    for x, y in [(-22, 14), (-16, 20), (-28, 22), (16, 14), (22, 20), (28, 16)]:
        dot(d, x, y, 0.9)


def head_side(d, expr='smirk'):
    e = EXPR[expr]
    wash(d, [(-60, -70), (-74, -20), (-92, 16), (-80, 40), (-72, 66), (-40, 82), (10, 80), (40, 50), (40, -40),
             (0, -80)], SKIN, 0.5, dx=4, dy=3)
    blot(d, -44, 34, 15, BLUSH, 0.45)
    wash(d, [(-72, -60), (-76, -104), (-30, -140), (40, -140), (96, -100), (110, -40), (100, 20), (70, 30),
             (56, -20), (20, -56), (-30, -66)], HAIR, 0.7, dx=-2)
    tufts(d, [(-70, -56), (-76, -96), (-46, -130), (10, -142), (64, -126), (100, -90), (112, -40), (104, 10),
              (84, 36)], n=16, length=(10, 22), lean=0.7, w=1.7, seed=480)
    tufts(d, [(10, -76), (-20, -78), (-46, -72), (-66, -58)], n=5, length=(10, 18), lean=0.5, w=1.4, seed=481)
    # ear, in the middle of the head
    ink(d, [(16, -10), (36, -22), (48, -6), (44, 20), (26, 28), (16, 22)], w=1.7, start=0.6, end=0.3)
    ink(d, [(26, -4), (34, 2), (28, 14)], w=1.0)
    wash(d, [(18, -16), (46, -18), (46, 20), (20, 26)], BLUSH, 0.3, rough='S')
    ink(d, [(-64, -58), (-70, -36), (-72, -14), (-82, 2), (-96, 12), (-90, 21), (-80, 22)], w=2.0, start=0.4,
        end=0.3)
    ink(d, [(-80, 26), (-79, 34)], w=1.6, start=0.6, end=0.4)
    ink(d, [(-78, 48), (-74, 60), (-60, 72), (-40, 78), (-20, 78)], w=2.0, start=0.3, end=0.2)
    ink(d, [(-8, 77), (12, 66), (24, 40)], w=1.3, start=0.2, end=0.1)
    eye(d, -56, 2, 1.0 * e['eye'], (-1, e['look'][1]), e['lid'], side=-1, squint=e.get('squint', False), seed=65)
    brow(d, -54, -20, 16, e['lift'] + 2, e['tilt'], side=-1, w=1.4, arch=2, seed=66)
    if e['mouth'] == 'grin':
        ink(d, [(-80, 38), (-70, 44), (-56, 42), (-48, 34)], w=1.8, start=0.6, end=0.2)
        wash(d, [(-80, 38), (-58, 42), (-64, 48), (-78, 46)], '#c4473f', 0.6, rough='S')
    else:
        ink(d, [(-80, 40), (-62, 42)], w=1.6)
    for x, y in [(-46, 22), (-40, 28), (-52, 30), (-34, 20)]:
        dot(d, x, y, 0.9)


def bust_view(d, view, expr='smirk'):
    """Head and jumper shoulders, for the turnaround; frame 500 x 620."""
    d.push(250, 260, 1.05)
    if view == '34':
        d.pop(); d.push(260, 240, 1.0)
        bust_body = [(-30, 120), (40, 110), (110, 140), (126, 210), (130, 300), (-120, 300), (-130, 200),
                     (-90, 140)]
    else:
        bust_body = [(-40, 110), (40, 110), (110, 140), (126, 210), (130, 300), (-130, 300), (-126, 210),
                     (-110, 140)] if view == 'front' else [(-50, 110), (40, 110), (70, 150), (84, 220),
                                                          (86, 300), (-86, 300), (-84, 220), (-70, 150)]
    wash(d, bust_body, JUMPER, 0.22)
    xs = [p[0] for p in bust_body]
    for y in (150, 186, 222, 258, 290):
        a, b = min(xs) + 12, max(xs) - 12
        wash(d, [(a, y - 6), (0, y - 7), (b, y - 6), (b, y + 8), (0, y + 9), (a, y + 8)], JUMPER, 0.72, angle=0)
    neck = (-22, 70, 26, 120) if view != 'side' else (-30, 70, 14, 120)
    wash(d, [(neck[0], neck[1]), (neck[2], neck[1]), (neck[2] + 4, neck[3]), (neck[0] - 2, neck[3])], SKIN, 0.45)
    ink(d, [(neck[0], neck[1] + 6), (neck[0] - 1, neck[3])], w=1.3)
    ink(d, [(neck[2], neck[1] + 4), (neck[2] + 3, neck[3] - 4)], w=1.2)
    {'front': head_front, '34': head34, 'side': head_side}[view](d, expr)
    L = [p for p in bust_body if p[0] < 0]
    R = [p for p in bust_body if p[0] > 0]
    ink(d, [(neck[0] - 4, 118)] + sorted(L, key=lambda p: p[1])[1:], w=2.0, start=0.6, end=0.05)
    ink(d, [(neck[2] + 4, 114)] + sorted(R, key=lambda p: p[1])[1:], w=1.9, start=0.6, end=0.05)
    ink(d, [(neck[0] - 4, 118), ((neck[0] + neck[2]) / 2, 128), (neck[2] + 4, 114)], w=1.5)
    d.pop()
