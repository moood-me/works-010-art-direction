"""Вера, about 40: strict, clever, tired. A long face, a straight sharp nose, thin lips; dark hair pulled back
into a bun with strands escaping; narrow spectacles; violet under the eyes; a teal coat with a high collar.
Head units as the others'."""
import math
from kit import ink, dot, wash, blot, hatch
from parts import eye, brow, mouth, hand, tube, shoe, EXPR, SKIN, BLUSH, SHADOW

HAIR = '#3b2622'
COAT = '#3e8a8c'
BLOUSE = '#efe6d8'
SKIRT = '#55606e'


def glasses(d):
    for (x, y, rx, ry) in [(-16, -2, 17, 10), (-64, -2, 10, 10)]:
        pts = [(x - rx, y - ry * 0.7), (x + rx * 0.2, y - ry), (x + rx, y - ry * 0.6), (x + rx * 0.9, y + ry * 0.6),
               (x, y + ry), (x - rx * 0.9, y + ry * 0.7), (x - rx, y - ry * 0.7)]
        ink(d, pts, w=1.2, start=0.9, end=0.9, jit=0.4, retrace=0.4)
    ink(d, [(-33, -4), (-44, -7), (-54, -4)], w=1.1)
    ink(d, [(1, -4), (44, -10)], w=1.0)


def head34(d, expr='stern'):
    e = EXPR[expr]
    sq = e.get('squint', False)
    wash(d, [(-56, -96), (-68, -40), (-92, 30), (-80, 50), (-66, 90), (-40, 108), (10, 100), (44, 60), (56, 0),
             (40, -80), (0, -104)], SKIN, 0.46, dx=5, dy=3)
    blot(d, 6, 36, 15, BLUSH, 0.25)
    # tired: violet under the eyes
    wash(d, [(-34, 10), (-4, 10), (-2, 18), (-30, 20)], SHADOW, 0.35, rough='S')
    wash(d, [(-72, 10), (-56, 10), (-56, 18), (-70, 18)], SHADOW, 0.3, rough='S')
    # hair: pulled back smooth, a bun high at the back, strands escaping
    wash(d, [(-60, -92), (-30, -126), (30, -130), (80, -104), (100, -50), (90, 10), (60, 40), (50, -20), (30, -70),
             (-20, -96)], HAIR, 0.85, dx=-2)
    wash(d, [(-40, -110), (30, -124), (84, -96), (96, -40), (70, 20), (50, -40), (0, -96)], HAIR, 0.7)
    wash(d, [(70, -150), (110, -150), (130, -110), (110, -80), (76, -96)], HAIR, 0.85)
    ink(d, [(-60, -86), (-40, -118), (0, -132), (44, -126), (76, -104)], w=2.1, start=0.5, end=0.2)
    ink(d, [(84, -98), (98, -64), (100, -20), (88, 20), (66, 46)], w=1.9, start=0.3, end=0.2)
    # the bun: a loose coil
    ink(d, [(88, -100), (96, -134), (116, -136), (120, -112), (104, -104)], w=1.0, start=0.4, end=0.1)
    ink(d, [(80, -120), (100, -150), (126, -128)], w=0.9, start=0.4, end=0.1, retrace=0)
    ink(d, [(74, -104), (84, -146), (112, -156), (132, -126), (118, -92), (90, -92)], w=1.8, start=0.6, end=0.3)
    # combed-back lines and the hairline
    for k, pts in enumerate([[(-44, -98), (0, -110), (50, -100), (82, -84)], [(-30, -88), (10, -96), (60, -80)],
                             [(-12, -80), (30, -80), (64, -60), (78, -30)]]):
        ink(d, pts, w=0.9, start=0.4, end=0.1, retrace=0, seed=510 + k)
    ink(d, [(-58, -84), (-30, -90), (10, -84), (40, -66), (54, -30), (52, 10)], w=1.3, start=0.3, end=0.2)
    # strands escaping (she is tired)
    ink(d, [(-50, -96), (-70, -80), (-78, -50), (-70, -30)], w=0.9, start=0.5, end=0.05, retrace=0)
    ink(d, [(-40, -100), (-58, -92), (-64, -70)], w=0.8, start=0.5, end=0.05, retrace=0)
    ink(d, [(54, 10), (60, 40), (52, 70), (58, 92)], w=0.8, start=0.5, end=0.05, retrace=0)
    # ear and a small earring
    ink(d, [(40, -6), (52, -16), (60, -2), (56, 20), (46, 28)], w=1.5, start=0.6, end=0.3)
    dot(d, 48, 36, 2.6)
    # face contour: high forehead, a straight sharp nose, thin lips, a long chin
    ink(d, [(-56, -82), (-62, -50), (-66, -24), (-66, -12), (-78, 8), (-94, 30), (-88, 34), (-76, 34)],
        w=2.0, start=0.4, end=0.3)
    ink(d, [(-74, 44), (-77, 50), (-73, 56), (-75, 62), (-70, 78), (-60, 96), (-44, 106), (-26, 108)],
        w=2.0, start=0.3, end=0.15)
    ink(d, [(-14, 107), (14, 96), (38, 66)], w=1.1, start=0.15, end=0.1, retrace=0)
    ink(d, [(-82, 30), (-76, 26)], w=1.0, retrace=0)
    # eyes: heavy lids, a fine line under each; brows straight
    eye(d, -16, -2, 1.0 * e['eye'], e['look'], e['lid'], lash=True, side=1, squint=sq, seed=51)
    eye(d, -62, -3, 0.75 * e['eye'], e['look'], e['lid'], lash=True, side=-1, squint=sq, seed=52)
    ink(d, [(-28, 14), (-16, 18), (-4, 14)], w=0.7, retrace=0)
    glasses(d)
    brow(d, -14, -26, 28, e['lift'], e['tilt'], side=1, w=1.5, arch=2, seed=53)
    brow(d, -62, -26, 14, e['lift'], e['tilt'] * 0.6, side=-1, w=1.3, arch=1, seed=54)
    if e['mouth'] in ('flat', 'soft'):
        # thin lips, pressed; the corners a little down
        wash(d, [(-74, 52), (-50, 50), (-44, 56), (-70, 60)], '#c45a52', 0.4, rough='S')
        ink(d, [(-76, 54), (-60, 55), (-44, 54), (-40, 58)], w=1.6, start=0.5, end=0.3)
    else:
        mouth(d, -60, 54, e['mouth'], 1.0, side=-1, lips=False)
    ink(d, [(-56, 30), (-46, 46)], w=0.8, start=0.3, end=0.1, retrace=0)


def bust(d, expr='stern'):
    """Head and shoulders, 600 x 720: upright, the collar high."""
    d.push(300, 262, 1.08, 2)
    wash(d, [(-40, 140), (20, 130), (100, 150), (150, 190), (164, 270), (166, 330), (-170, 330), (-160, 240),
             (-120, 170)], COAT, 0.66, dy=6)
    wash(d, [(-26, 96), (32, 90), (40, 150), (-20, 156)], SKIN, 0.42)
    wash(d, [(-30, 132), (38, 124), (30, 186), (-20, 190)], BLOUSE, 0.6)
    ink(d, [(-24, 104), (-20, 136)], w=1.4, start=0.3, end=0.2)
    ink(d, [(34, 86), (38, 128)], w=1.2, start=0.3, end=0.2)
    head34(d, expr)
    # blouse collar, coat lapels, a brooch
    ink(d, [(-28, 130), (-6, 142), (20, 138), (40, 124)], w=1.5, start=0.5, end=0.4)
    ink(d, [(-30, 132), (-46, 150), (-30, 196), (-18, 240)], w=1.8, start=0.5, end=0.2)
    ink(d, [(40, 126), (60, 150), (36, 196), (22, 240)], w=1.8, start=0.5, end=0.2)
    wash(d, [(-6, 152), (6, 150), (8, 162), (-6, 164)], '#b8463f', 0.8, rough='S')
    ink(d, [(-8, 150), (8, 150), (8, 164), (-8, 164), (-8, 150)], w=1.0, retrace=0)
    # square shoulders
    ink(d, [(-46, 150), (-110, 160), (-150, 182), (-164, 240), (-168, 320)], w=2.2, start=0.6, end=0.05)
    ink(d, [(60, 148), (110, 152), (150, 176), (162, 240), (166, 310)], w=2.1, start=0.6, end=0.05)
    ink(d, [(-30, 200), (-24, 260), (-20, 320)], w=1.3, start=0.4, end=0.05)
    for y in (232, 282):
        dot(d, -12, y, 3.0)
    d.pop()


def figure(d, expr='stern'):
    """Full figure, 600 x 1000. Upright; a folder held to her chest with one arm, the other straight down;
    a coat to below the knee."""
    # legs, heeled shoes
    tube(d, [(284, 700), (282, 790), (282, 858)], [11, 9, 7], '#c9a898', 0.4, w=1.6, seed=90)
    tube(d, [(318, 700), (322, 790), (326, 856)], [11, 9, 7], '#c9a898', 0.35, w=1.6, seed=92)
    shoe(d, 282, 878, 30, -1, '#2f2a30')
    shoe(d, 328, 876, 30, -1, '#2f2a30')
    ink(d, [(276, 878), (278, 892)], w=1.6)
    ink(d, [(322, 876), (324, 890)], w=1.6)
    # coat: teal, below the knee; square shoulders
    coat = [(286, 262), (240, 276), (228, 330), (226, 460), (222, 580), (214, 700), (300, 708), (386, 700),
            (378, 580), (372, 460), (370, 330), (358, 276), (314, 262)]
    wash(d, coat, COAT, 0.66, dx=3, dy=4)
    ink(d, [(286, 264), (244, 276), (230, 316), (228, 460), (222, 580), (214, 698)], w=2.1, start=0.5, end=0.3)
    ink(d, [(314, 264), (356, 276), (370, 318), (372, 460), (380, 580), (386, 696)], w=2.0, start=0.5, end=0.3)
    ink(d, [(212, 698), (260, 710), (300, 704), (340, 712), (388, 698)], w=1.7, start=0.5, end=0.5)
    ink(d, [(300, 420), (300, 580), (298, 704)], w=1.5, start=0.3, end=0.3)
    for y in (470, 540, 610):
        dot(d, 290, y, 2.6)
    ink(d, [(232, 470), (300, 476), (370, 470)], w=1.2, start=0.3, end=0.3)        # belt
    # collar, blouse
    wash(d, [(284, 262), (316, 262), (312, 300), (290, 300)], BLOUSE, 0.5)
    ink(d, [(282, 262), (270, 290), (296, 316)], w=1.6)
    ink(d, [(318, 262), (330, 290), (304, 316)], w=1.6)
    # the near arm hangs straight
    tube(d, [(244, 290), (236, 380), (234, 470), (238, 540)], [16, 15, 13, 12], COAT, 0.62, w=1.8, seed=94)
    hand(d, 238, 542, 1.0, 4, 'rest', color=SKIN)
    # the folder, held upright against the chest by the far arm
    folder = [(300, 318), (346, 310), (352, 440), (306, 446)]
    wash(d, folder, '#e7c47a', 0.75, rough='S')
    ink(d, folder + [folder[0]], w=1.6, start=0.9, end=0.9)
    ink(d, [(306, 324), (310, 440)], w=0.8, retrace=0)
    tube(d, [(358, 290), (370, 360), (360, 410), (330, 412)], [16, 15, 13, 11], COAT, 0.62, w=1.8, seed=96)
    hand(d, 330, 404, 0.95, 70, 'hold', color=SKIN)
    # neck
    wash(d, [(288, 228), (314, 224), (316, 266), (286, 268)], SKIN, 0.42)
    ink(d, [(290, 236), (288, 264)], w=1.3)
    ink(d, [(314, 228), (316, 262)], w=1.2)
    d.push(304, 182, 0.53, 2)
    head34(d, expr)
    d.pop()
