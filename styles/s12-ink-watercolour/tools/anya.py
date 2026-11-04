"""Аня, about 20: warm, trusting, dreamy. Long loose ginger-chestnut hair, freckles, a mustard cardigan over a
sea-green dress. Head units: crown about y=-125, chin y=100; the face looks to the viewer's left in '34'."""
from kit import ink, dot, wash, blot, hatch
from parts import extra, eye, brow, mouth, hand, tube, shoe, EXPR, SKIN, BLUSH

HAIR = '#c96f36'
CARDI = '#eeb43e'
DRESS = '#6fb3a0'


def freckles(d, pts):
    for x, y in pts:
        dot(d, x, y, 0.9)


def head34(d, expr='dream', hair=True):
    e = EXPR[expr]
    sq = e.get('squint', False)
    # --- washes ---
    wash(d, [(-60, -86), (-72, -30), (-86, 20), (-70, 50), (-60, 78), (-40, 90), (10, 84), (46, 50), (56, 0),
             (40, -70), (0, -96)], SKIN, 0.48, dx=5, dy=3)
    blot(d, -52, 30, 13, BLUSH, 0.42)
    blot(d, 12, 28, 17, BLUSH, 0.38)
    # --- face contour: forehead, brow, nose; then lips and a small chin ---
    ink(d, [(-52, -78), (-62, -46), (-68, -22), (-67, -10), (-78, 10), (-90, 24), (-86, 29), (-74, 30)],
        w=2.0, start=0.4, end=0.25)
    ink(d, [(-73, 38), (-77, 44), (-72, 50), (-75, 56), (-70, 66), (-60, 80), (-44, 89), (-26, 90)],
        w=2.0, start=0.3, end=0.15)
    ink(d, [(-14, 89), (14, 80), (40, 56)], w=1.1, start=0.15, end=0.1, retrace=0)
    ink(d, [(-80, 26), (-74, 22)], w=1.0, retrace=0)        # nostril
    # eyes, brows, mouth
    eye(d, -18, -6, 1.15 * e['eye'], e['look'], e['lid'], lash=True, side=1, squint=sq, seed=11)
    eye(d, -60, -7, 0.85 * e['eye'], e['look'], e['lid'], lash=True, side=-1, squint=sq, seed=12)
    brow(d, -16, -30, 26, e['lift'], e['tilt'], side=1, w=1.3, seed=13)
    brow(d, -60, -31, 14, e['lift'], e['tilt'] * 0.6, side=-1, w=1.1, arch=2, seed=14)
    mouth(d, -60, 48, e['mouth'], e.get('ms', 1.0), side=-1)
    extra(d, e, -18, -6, 10, 28, -60)
    freckles(d, [(-40, 16), (-34, 22), (-44, 24), (-28, 15), (-2, 18), (6, 24), (-8, 26)])
    if hair:
        hair34(d)


def hair34(d):
    # wash: one big wavy mass behind the face, down past the shoulders; paper left light on the crown
    wash(d, [(-50, -128), (10, -142), (70, -122), (110, -74), (126, -10), (116, 50), (138, 110), (124, 170),
             (146, 230), (120, 270), (84, 250), (76, 190), (60, 130), (58, 60), (54, -10), (36, -66), (-10, -96),
             (-48, -86), (-70, -96)], HAIR, 0.6, dx=-3, dy=2)
    wash(d, [(-80, -96), (-46, -128), (-24, -104), (-56, -76), (-70, -40), (-86, -60)], HAIR, 0.5)
    wash(d, [(64, -60), (96, -30), (100, 40), (124, 120), (110, 200), (84, 140), (70, 40)], '#9c4a22', 0.3)
    # outer line: waves, in pen strokes that don't quite meet
    ink(d, [(-82, -76), (-68, -112), (-30, -136), (16, -142), (58, -128)], w=2.2, start=0.5, end=0.3)
    ink(d, [(64, -124), (100, -96), (120, -50), (126, -6), (116, 40), (124, 84), (138, 116)], w=2.0, start=0.3,
        end=0.15)
    ink(d, [(136, 126), (124, 166), (134, 200), (148, 230), (136, 262), (114, 272)], w=1.6, start=0.4, end=0.05)
    # parting; the front lock sweeps over the temple
    ink(d, [(-20, -132), (-48, -114), (-66, -94), (-80, -64), (-76, -46)], w=1.6, end=0.1)
    ink(d, [(-14, -130), (14, -104), (38, -78), (52, -36), (54, 10), (64, 50), (60, 96), (76, 140), (70, 186),
            (86, 230), (82, 252)], w=1.7, start=0.6, end=0.05)
    # locks: a few long waves and short flicks, light
    for k, pts in enumerate([
            [(4, -134), (44, -116), (78, -80), (94, -30), (90, 30), (104, 90), (98, 150), (114, 210)],
            [(22, -136), (64, -118), (98, -76), (110, -20)],
            [(96, 120), (112, 160), (104, 200), (126, 250)],
            [(-34, -128), (-58, -106), (-72, -82)]]):
        ink(d, pts, w=0.85, start=0.3, end=0.05, jit=1.5, seed=100 + k)
    for x, y in [(80, 40), (92, 64), (108, 180), (70, 120), (118, 228)]:
        ink(d, [(x, y), (x + 4, y + 18), (x + 2, y + 30)], w=0.8, start=0.6, end=0.05, retrace=0)


def neck_and_shoulders(d):
    wash(d, [(-30, 86), (24, 80), (34, 150), (-30, 156)], SKIN, 0.42, dx=3)
    ink(d, [(-26, 92), (-27, 122), (-22, 148)], w=1.3, start=0.3, end=0.2)
    ink(d, [(30, 76), (32, 108), (40, 136)], w=1.1, start=0.3, end=0.2)


def bust(d, expr='dream'):
    """Head and shoulders, in a 600 x 720 frame. The washes thin out below, as on a book page."""
    d.push(300, 262, 1.1, -6)
    wash(d, [(-130, 186), (-90, 166), (-34, 160), (-14, 226), (30, 154), (90, 152), (146, 180), (166, 250),
             (170, 330), (100, 360), (0, 340), (-120, 370), (-178, 340), (-176, 250)], CARDI, 0.62, dy=6)
    wash(d, [(-32, 152), (40, 144), (30, 194), (6, 240), (-14, 230)], DRESS, 0.62)
    neck_and_shoulders(d)
    head34(d, expr)
    # sloping shoulders, a soft knit; the line breaks and trails off
    ink(d, [(-22, 152), (-70, 164), (-122, 184), (-156, 220)], w=2.1, start=0.6, end=0.3)
    ink(d, [(-162, 234), (-174, 290), (-178, 350)], w=1.8, start=0.5, end=0.05)
    ink(d, [(40, 144), (92, 154), (136, 176), (158, 216), (166, 290)], w=1.9, start=0.6, end=0.05)
    ink(d, [(-32, 156), (-18, 206), (4, 240), (22, 192), (40, 146)], w=1.4, start=0.3, end=0.3)       # neckline
    ink(d, [(-54, 164), (-42, 242), (-32, 320)], w=1.6, start=0.4, end=0.05)                           # cardigan
    ink(d, [(60, 152), (46, 240), (40, 300)], w=1.6, start=0.4, end=0.05)
    for y in (268, 312):
        ink(d, [(-24, y), (-18, y - 4), (-13, y + 1), (-19, y + 5), (-24, y)], w=1.0, retrace=0)
    for x, y in [(-146, 270), (-136, 310), (136, 240), (146, 290), (-106, 226)]:
        ink(d, [(x, y), (x + 3, y + 20)], w=0.8, start=0.6, end=0.1, retrace=0)
    d.pop()


def figure(d, expr='dream'):
    """Full figure, 600 x 1000. She stands lightly, weight on one leg, head tilted, a few wild flowers held to
    her chest; the other arm hangs loose."""
    # legs under the dress hem, and shoes
    tube(d, [(276, 735), (272, 800), (270, 865)], [11, 9, 6], SKIN, 0.4, w=1.6, seed=60)
    tube(d, [(318, 730), (326, 795), (334, 858)], [11, 9, 6], SKIN, 0.4, w=1.6, seed=62)
    shoe(d, 270, 878, 30, -1, '#b24a3a')
    shoe(d, 336, 872, 30, 1, '#b24a3a')
    # dress: sea green, A-line to below the knee, the hem lifting a little
    dress = [(262, 360), (338, 352), (352, 470), (372, 600), (398, 728), (350, 740), (300, 734), (250, 744),
             (206, 730), (230, 600), (252, 470)]
    wash(d, dress, DRESS, 0.6, dx=4, dy=4)
    ink(d, [(254, 470), (232, 600), (206, 728)], w=1.9, start=0.5, end=0.3)
    ink(d, [(350, 470), (374, 600), (398, 726)], w=1.9, start=0.5, end=0.3)
    ink(d, [(204, 730), (230, 742), (256, 736), (284, 744), (312, 734), (344, 742), (372, 732), (400, 728)], w=1.6,
        start=0.5, end=0.5)
    for x0, x1 in [(282, 270), (322, 334), (300, 300)]:
        ink(d, [(x0, 560), ((x0 + x1) / 2, 640), (x1, 720)], w=0.9, start=0.2, end=0.2, retrace=0)
    # cardigan: open, to the hip
    cardi_l = [(262, 290), (240, 302), (228, 340), (226, 420), (232, 520), (282, 536), (290, 440), (286, 330)]
    cardi_r = [(318, 288), (352, 300), (366, 340), (368, 420), (364, 512), (316, 530), (306, 440), (310, 330)]
    wash(d, cardi_l, CARDI, 0.62, dx=-3, dy=3)
    wash(d, cardi_r, CARDI, 0.62, dx=3, dy=3)
    ink(d, [(228, 344), (226, 420), (232, 520), (282, 538)], w=1.9, start=0.5, end=0.3)
    ink(d, [(284, 300), (288, 400), (284, 536)], w=1.6, start=0.4, end=0.2)
    ink(d, [(312, 300), (308, 400), (316, 530), (364, 512), (368, 430)], w=1.8, start=0.4, end=0.2)
    # her right arm hangs (viewer's left), loose
    tube(d, [(246, 306), (232, 380), (226, 452), (232, 520)], [16, 14, 12, 11], CARDI, 0.6, w=1.8, seed=64)
    hand(d, 232, 524, 1.1, 8, 'rest', color=SKIN)
    # the other arm bends; the hand holds flowers at the chest
    tube(d, [(350, 308), (372, 368), (376, 426), (344, 418), (318, 396)], [16, 15, 13, 11, 10], CARDI, 0.6,
         w=1.8, seed=66)
    # flowers: stems, a few heads of colour
    for k, (x1, y1) in enumerate([(286, 330), (300, 318), (276, 346), (312, 334)]):
        ink(d, [(310, 410), ((310 + x1) / 2 + 4, (410 + y1) / 2), (x1, y1)], w=0.9, start=0.5, end=0.3, retrace=0,
            color='#3f6d3a')
    for k, (x, y, c) in enumerate([(286, 326, '#e05a8a'), (300, 314, '#f2c230'), (274, 342, '#7a6bd0'),
                                   (314, 330, '#e05a8a')]):
        wash(d, [(x - 8, y - 6), (x + 8, y - 8), (x + 9, y + 6), (x - 7, y + 8)], c, 0.75, rough='S')
        ink(d, [(x - 5, y - 2), (x, y - 6), (x + 5, y - 1), (x + 1, y + 4), (x - 4, y + 2)], w=1.0, retrace=0)
    hand(d, 318, 396, 1.1, 120, 'hold', color=SKIN)
    # neck
    wash(d, [(286, 256), (314, 252), (318, 296), (284, 298)], SKIN, 0.42)
    ink(d, [(288, 262), (287, 292)], w=1.4)
    ink(d, [(316, 254), (318, 288)], w=1.2)
    ink(d, [(282, 296), (300, 318), (318, 292)], w=1.3)
    # head, tilted toward the flowers
    d.push(302, 214, 0.56, -10)
    head34(d, expr)
    d.pop()


def head_front(d, expr='calm'):
    e = EXPR[expr]
    # hair behind the face, falling to both shoulders
    wash(d, [(-20, -140), (60, -128), (100, -80), (112, 0), (120, 110), (130, 220), (90, 250), (70, 160), (66, 40),
             (40, -70), (-40, -70), (-66, 40), (-70, 160), (-92, 250), (-130, 220), (-118, 110), (-110, 0),
             (-98, -80), (-60, -128)], HAIR, 0.6, dy=2)
    wash(d, [(-62, -60), (-68, 0), (-60, 50), (-36, 86), (0, 98), (36, 86), (60, 50), (68, 0), (62, -60),
             (20, -84), (-30, -82)], SKIN, 0.48, dx=4, dy=3)
    blot(d, -34, 34, 14, BLUSH, 0.4)
    blot(d, 34, 34, 14, BLUSH, 0.4)
    # face: two contours that don't quite meet at the chin
    ink(d, [(-60, -50), (-66, 0), (-58, 46), (-36, 82), (-6, 97)], w=2.0, start=0.3, end=0.15)
    ink(d, [(60, -50), (66, 0), (58, 46), (36, 82), (8, 96)], w=1.8, start=0.3, end=0.15)
    # nose: one line and a little hook
    ink(d, [(-4, -4), (-7, 18), (-10, 28), (-3, 33), (6, 30)], w=1.6, start=0.3, end=0.2)
    eye(d, -28, -4, 1.1 * e['eye'], e['look'], e['lid'], lash=True, side=-1, squint=e.get('squint', False), seed=21)
    eye(d, 28, -4, 1.1 * e['eye'], e['look'], e['lid'], lash=True, side=1, squint=e.get('squint', False), seed=22)
    brow(d, -28, -28, 24, e['lift'], e['tilt'], side=-1, w=1.2, seed=23)
    brow(d, 28, -28, 24, e['lift'], e['tilt'], side=1, w=1.2, seed=24)
    mouth(d, 2, 54, e['mouth'], 1.0, side=-1)
    freckles(d, [(-20, 18), (-14, 24), (-26, 24), (14, 18), (20, 24), (26, 20)])
    # hair: middle parting, waves to both sides
    ink(d, [(-4, -134), (-40, -118), (-70, -84), (-82, -30), (-84, 30)], w=1.9, start=0.5, end=0.1)
    ink(d, [(-4, -134), (36, -120), (68, -86), (82, -30), (84, 30)], w=1.9, start=0.5, end=0.1)
    ink(d, [(-60, -128), (-100, -96), (-112, -20), (-110, 80), (-124, 160), (-118, 220), (-100, 250)], w=2.0,
        start=0.4, end=0.05)
    ink(d, [(40, -132), (98, -100), (112, -20), (112, 80), (128, 160), (124, 220), (106, 248)], w=2.0, start=0.4,
        end=0.05)
    ink(d, [(-60, -128), (-20, -142), (40, -134)], w=2.0, start=0.4, end=0.4)
    for k, sgn in enumerate((-1, 1)):
        ink(d, [(sgn * 6, -130), (sgn * 50, -104), (sgn * 86, -40), (sgn * 90, 60), (sgn * 104, 160),
                (sgn * 96, 230)], w=0.9, start=0.3, end=0.05, jit=1.5, seed=130 + k)
        ink(d, [(sgn * 84, 40), (sgn * 74, 120), (sgn * 84, 190)], w=0.9, start=0.3, end=0.05, seed=140 + k)


def head_side(d, expr='calm'):
    e = EXPR[expr]
    wash(d, [(-40, -134), (40, -130), (100, -90), (120, -10), (124, 90), (140, 200), (110, 260), (70, 230),
             (50, 140), (20, 60), (0, -40), (-40, -90)], HAIR, 0.6, dy=2)
    wash(d, [(-60, -86), (-72, -30), (-90, 20), (-76, 50), (-64, 86), (-40, 96), (0, 90), (20, 40), (20, -40),
             (-10, -90)], SKIN, 0.48, dx=4, dy=3)
    blot(d, -34, 30, 16, BLUSH, 0.4)
    # profile: forehead, nose, lips, chin, under the jaw to the ear
    ink(d, [(-52, -82), (-64, -46), (-70, -20), (-70, -10), (-82, 10), (-94, 24), (-90, 29), (-77, 30)],
        w=2.0, start=0.4, end=0.25)
    ink(d, [(-76, 38), (-81, 44), (-75, 50), (-79, 56), (-73, 68), (-64, 84), (-48, 94), (-28, 96)],
        w=2.0, start=0.3, end=0.15)
    ink(d, [(-20, 95), (0, 86), (14, 64)], w=1.3, start=0.2, end=0.1)
    ink(d, [(-84, 26), (-78, 22)], w=1.0, retrace=0)
    # one eye in profile, a brow, the mouth's corner
    eye(d, -54, -6, 0.85 * e['eye'], (-1, e['look'][1]), e['lid'], lash=True, side=-1, squint=e.get('squint', False),
        seed=25)
    brow(d, -52, -30, 18, e['lift'], e['tilt'], side=-1, w=1.2, arch=2, seed=26)
    ink(d, [(-80, 48), (-66, 49), (-60, 46)], w=1.4, start=0.4, end=0.2)
    wash(d, [(-82, 42), (-70, 42), (-72, 56), (-82, 56)], '#d4594b', 0.4, rough='S')
    # ear peeking through the hair
    ink(d, [(8, -6), (20, -14), (28, 0), (24, 20), (14, 28)], w=1.5, start=0.6, end=0.3)
    wash(d, [(10, -12), (28, -10), (26, 22), (12, 26)], SKIN, 0.4, rough='S')
    freckles(d, [(-46, 18), (-40, 24), (-52, 24), (-34, 18)])
    # hair: from the hairline back, a long fall behind the shoulder
    ink(d, [(-54, -86), (-40, -122), (0, -138), (50, -128), (96, -94), (118, -30), (122, 40), (120, 100),
            (136, 170), (130, 230), (110, 262)], w=2.1, start=0.5, end=0.05)
    ink(d, [(-50, -84), (-20, -94), (6, -80), (0, -40), (6, 0)], w=1.6, start=0.5, end=0.1)
    ink(d, [(30, 20), (40, 80), (56, 140), (70, 210), (76, 240)], w=1.6, start=0.4, end=0.05)
    for k, pts in enumerate([[(-20, -126), (40, -116), (86, -70), (100, 0), (100, 80), (114, 160), (108, 220)],
                             [(10, -110), (60, -90), (80, -30), (70, 40), (84, 120), (96, 200)],
                             [(-30, -110), (10, -100), (40, -70), (50, -20)]]):
        ink(d, pts, w=0.9, start=0.3, end=0.05, jit=1.5, seed=150 + k)


def bust_view(d, view, expr='calm'):
    """Head and cardigan shoulders, for the turnaround; view: 'front', '34', 'side'. Frame 500 x 620."""
    d.push(250, 250, 0.98)
    if view == 'front':
        wash(d, [(-150, 196), (-40, 160), (0, 210), (40, 160), (150, 196), (170, 320), (-170, 320)], CARDI, 0.6)
        wash(d, [(-36, 154), (36, 154), (0, 220)], DRESS, 0.6)
        wash(d, [(-28, 90), (28, 90), (32, 156), (-32, 156)], SKIN, 0.42)
        ink(d, [(-26, 96), (-28, 150)], w=1.3); ink(d, [(26, 96), (28, 150)], w=1.3)
        head_front(d, expr)
        ink(d, [(-30, 152), (-90, 166), (-140, 194), (-160, 250), (-166, 320)], w=2.0, start=0.6, end=0.05)
        ink(d, [(30, 152), (90, 166), (140, 194), (160, 250), (166, 320)], w=2.0, start=0.6, end=0.05)
        ink(d, [(-34, 156), (0, 222), (34, 156)], w=1.4)
        ink(d, [(-50, 166), (-30, 250), (-24, 320)], w=1.5, start=0.4, end=0.05)
        ink(d, [(50, 166), (30, 250), (24, 320)], w=1.5, start=0.4, end=0.05)
    elif view == 'side':
        wash(d, [(-70, 170), (0, 150), (60, 170), (90, 240), (96, 320), (-90, 320), (-90, 240)], CARDI, 0.6)
        wash(d, [(-34, 90), (14, 80), (24, 156), (-30, 160)], SKIN, 0.42)
        ink(d, [(-32, 96), (-36, 156)], w=1.3); ink(d, [(12, 86), (20, 150)], w=1.2)
        head_side(d, expr)
        ink(d, [(-36, 156), (-70, 176), (-90, 230), (-92, 320)], w=2.0, start=0.6, end=0.05)
        ink(d, [(20, 150), (70, 172), (90, 240), (94, 320)], w=2.0, start=0.6, end=0.05)
        ink(d, [(-10, 190), (0, 260), (6, 320)], w=1.2, start=0.4, end=0.05)
    else:
        d.pop()
        d.push(250, 230, 0.92)
        wash(d, [(-130, 206), (-90, 186), (-34, 180), (-14, 250), (30, 176), (90, 172), (150, 200), (172, 280),
                 (176, 350), (-180, 350), (-180, 280)], CARDI, 0.62, dy=6)
        wash(d, [(-34, 172), (40, 164), (30, 214), (6, 262), (-14, 252)], DRESS, 0.62)
        d.push(0, -16)
        neck_and_shoulders(d)
        head34(d, expr)
        d.pop()
        ink(d, [(-24, 156), (-70, 168), (-124, 190), (-160, 230), (-170, 350)], w=2.0, start=0.6, end=0.05)
        ink(d, [(40, 148), (92, 160), (138, 186), (160, 236), (170, 340)], w=1.9, start=0.6, end=0.05)
        ink(d, [(-34, 160), (-20, 212), (4, 246), (22, 196), (40, 150)], w=1.4)
        ink(d, [(-56, 168), (-44, 246), (-36, 340)], w=1.5, start=0.4, end=0.05)
        ink(d, [(60, 156), (46, 246), (40, 330)], w=1.5, start=0.4, end=0.05)
    d.pop()
