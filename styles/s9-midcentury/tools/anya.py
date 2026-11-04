"""Аня, about 20 — warm, trusting, dreamy. A 1950s bob with a flip, an Alice band, a Peter Pan collar."""
from kit import shape, brush, blush, ell, circle, dryb, pattern_dots, limb, edge, INK
from face import eye, brow, mouth, EXPR

SKIN = '#f6d7bf'
SKIN_D = '#e9b89c'
HAIR = '#3a231f'
HAIR_L = '#6a4034'
BAND = '#2f8f8a'
DRESS = '#e8b33a'
DRESS_D = '#c98f22'
CARDI = '#2f8f8a'
CARDI_D = '#226e6a'
COLLAR = '#fbf6ea'
CHEEK = '#ec7f72'
FIG_SCALE = 1.0  # how much larger the full figure is drawn on its own page
BUST_DY = -34

# Аня looks a little dreamy even when calm: lids lowered a touch
OWN = {'calm': dict(eye='look', lid=0.3, brow=(0, 0), mouth='lips')}


def _e(expr):
    e = dict(EXPR[expr])
    e.update(OWN.get(expr, {}))
    return e


def head(view='34', expr='calm', neck=True):
    """The head around (0, 0), crown near y=-120, chin near y=95; neck=False leaves the neck to the figure."""
    e = _e(expr)
    o = []
    if view == '34':
        o.append(shape([(-30, -132), (32, -128), (76, -100), (92, -55), (90, 0), (88, 38), (104, 66, 'c'), (80, 70),
                        (60, 62), (0, 74), (-52, 66), (-80, 66), (-104, 76, 'c'), (-94, 48), (-92, 0), (-86, -62),
                        (-62, -110)], HAIR))
        if neck:
            o.append(shape([(-24, 66), (20, 78), (24, 150), (-28, 150)], SKIN_D))
        face = [(-54, -60), (-28, -98), (15, -104), (50, -84), (64, -46), (66, -8), (64, 22), (56, 50), (38, 76),
                (18, 90), (-2, 88), (-26, 74), (-46, 46), (-58, 6)]
        o.append(shape(face, SKIN))
        o.append(edge(face, 9, 13, 1.8, '#9a6450'))
        cheek = e.get('cheek', 1.0)
        o.append(blush(-20, 40, 16 * cheek, CHEEK))
        o.append(eye(-12, 12, 1.55, e['eye'], side=-1, lid=e.get('lid', 0)))
        o.append(eye(40, 10, 1.45, e['eye'], side=1, squash=0.62, lid=e.get('lid', 0)))
        bi, bo = e['brow']
        o.append(brow(-12, -16, 1.25, side=-1, inner=bi, outer=bo))
        o.append(brow(42, -18, 1.25, side=1, inner=bi, outer=bo, squash=0.6))
        # small turned-up nose: a skin-dark wedge that breaks toward the far cheek
        o.append(shape([(58, 16), (66, 30), (69, 36, 'c'), (62, 41), (54, 40)], SKIN))
        o.append(brush([(57, 18), (65, 31), (69, 36), (62, 41)], 2.2, '#a8624c', taper=(0.7, 0.2)))
        o.append(mouth(32, 60, 1.25 * e.get('ms', 1), e['mouth'], side=1, width=0.8))
        # fringe swept to the near side, Alice band behind it
        o.append(shape([(-66, -40), (-58, -86), (-20, -118), (30, -120), (70, -96), (84, -58), (72, -46), (50, -60),
                        (18, -66), (-14, -60), (-42, -46), (-62, -22, 'c')], HAIR))
        o.append(dryb([[(-50, -50), (-10, -98), (40, -110)], [(-20, -62), (20, -100), (62, -96)], [(30, -66), (66, -86), (80, -60)]],
                      3, HAIR_L, 0.55))
        o.append(brush([(-70, -60), (-42, -104), (10, -126), (60, -112), (88, -76)], 11, BAND, taper=(0.1, 0.1)))
    elif view == 'front':
        o.append(shape([(0, -132), (58, -118), (88, -76), (94, -20), (94, 36), (112, 66, 'c'), (84, 72), (60, 64), (0, 74),
                        (-60, 64), (-84, 72), (-112, 66, 'c'), (-94, 36), (-94, -20), (-88, -76), (-58, -118)], HAIR))
        if neck:
            o.append(shape([(-24, 66), (24, 66), (26, 150), (-26, 150)], SKIN_D))
        o.append(shape([(0, -104), (44, -94), (66, -56), (70, -10), (64, 34), (46, 70), (20, 92), (0, 97), (-20, 92), (-46, 70),
                        (-64, 34), (-70, -10), (-66, -56), (-44, -94)], SKIN))
        cheek = e.get('cheek', 1.0)
        o.append(blush(-38, 38, 14 * cheek, CHEEK))
        o.append(blush(38, 38, 14 * cheek, CHEEK))
        o.append(eye(-26, 10, 1.15, e['eye'], side=-1, lid=e.get('lid', 0)))
        o.append(eye(26, 10, 1.15, e['eye'], side=1, lid=e.get('lid', 0)))
        bi, bo = e['brow']
        o.append(brow(-27, -15, 1.0, side=-1, inner=bi, outer=bo))
        o.append(brow(27, -15, 1.0, side=1, inner=bi, outer=bo))
        o.append(brush([(4, 22), (8, 38), (1, 42)], 2.4, '#b9775e', taper=(0.4, 0.2)))
        o.append(mouth(0, 63, 1.0 * e.get('ms', 1), e['mouth'], side=1, width=0.9))
        o.append(shape([(-72, -30), (-66, -84), (-30, -118), (20, -122), (62, -104), (76, -60), (72, -34), (52, -54), (20, -64),
                        (-10, -62), (-40, -50), (-62, -26, 'c')], HAIR))
        o.append(dryb([[(-56, -50), (-20, -100), (30, -112)], [(-10, -62), (30, -100), (64, -86)]], 3, HAIR_L, 0.55))
        o.append(brush([(-82, -64), (-50, -110), (0, -128), (50, -110), (82, -64)], 11, BAND, taper=(0.1, 0.1)))
    elif view == 'side':
        o.append(shape([(-20, -130), (30, -122), (60, -96), (64, -60), (40, -40), (0, 20), (10, 66), (-30, 70), (-70, 66),
                        (-96, 78, 'c'), (-90, 48), (-96, 0), (-90, -60), (-64, -112)], HAIR))
        if neck:
            o.append(shape([(-14, 60), (22, 72), (20, 150), (-30, 150)], SKIN_D))
        # profile: forehead, small scoop at the bridge, turned-up nose, lips, small chin
        o.append(shape([(-30, -100), (20, -104), (52, -84), (64, -50), (66, -14), (64, 4), (70, 24), (78, 36, 'c'), (68, 42),
                        (64, 50), (66, 58), (62, 64), (64, 72), (56, 86), (36, 96), (10, 94), (-10, 80), (-24, 40), (-30, -40)],
                       SKIN))
        cheek = e.get('cheek', 1.0)
        o.append(blush(26, 40, 14 * cheek, CHEEK))
        o.append(eye(44, 8, 1.15, e['eye'], side=1, squash=0.75, lid=e.get('lid', 0)))
        bi, bo = e['brow']
        o.append(brow(46, -16, 1.0, side=1, inner=bi, outer=bo, squash=0.7))
        o.append(mouth(58, 63, 1.0 * e.get('ms', 1), e['mouth'], side=1, width=0.55))
        # ear is under the bob
        o.append(shape([(-34, -40), (-40, -86), (-6, -118), (36, -118), (62, -90), (70, -58), (52, -60), (30, -64), (0, -56),
                        (-24, -40), (-36, -10, 'c')], HAIR))
        o.append(dryb([[(-30, -50), (0, -100), (40, -110)], [(0, -60), (40, -96), (64, -70)]], 3, HAIR_L, 0.55))
        o.append(brush([(-40, -70), (-20, -110), (20, -124), (52, -110), (68, -82)], 11, BAND, taper=(0.1, 0.1)))
    return o


def bust(view='34'):
    """Shoulders and chest under a head drawn at (0, 0)."""
    o = []
    if view == 'side':
        body = [(-40, 140), (24, 140), (60, 200), (70, 300), (-80, 300), (-74, 190)]
        o.append(shape(body, DRESS))
        o.append(shape([(-80, 300), (-74, 186), (-40, 150), (-20, 200), (-30, 300)], CARDI))
        o.append(shape([(-18, 136), (28, 140), (40, 166), (8, 176), (-20, 160)], COLLAR))
        return o
    sx = 1 if view == '34' else 0
    body = [(-150 + sx * 20, 300), (-140 + sx * 18, 210), (-112 + sx * 14, 176), (-40, 146), (40 + sx * 6, 150),
            (112 + sx * 6, 176), (138, 214), (146, 300)]
    o.append(shape(body, DRESS))
    o.append(pattern_dots(body, -160, 150, 160, 300, 22, 2.6, '#fbf0d4', 'anyadots' + view))
    # open cardigan over the dress
    o.append(shape([(-150 + sx * 20, 300), (-140 + sx * 18, 210), (-112 + sx * 14, 176), (-50, 150), (-30, 200), (-52, 300)], CARDI))
    o.append(shape([(146, 300), (138, 214), (112 + sx * 6, 176), (52 + sx * 6, 152), (40 + sx * 8, 210), (62 + sx * 6, 300)], CARDI))
    o.append(brush([(-112 + sx * 14, 196), (-108 + sx * 14, 300)], 3, CARDI_D, taper=(0.3, 0)))
    o.append(brush([(118, 200), (118, 300)], 3, CARDI_D, taper=(0.3, 0)))
    # the round white collar
    cx = sx * 4
    o.append(shape([(cx - 4, 150), (cx - 46, 146), (cx - 60, 168), (cx - 34, 188), (cx - 6, 172, 'c')], COLLAR))
    o.append(shape([(cx + 4, 152, 'c'), (cx + 48, 150), (cx + 60, 172), (cx + 32, 190), (cx + 6, 174, 'c')], COLLAR))
    o.append(brush([(cx, 160), (cx, 176)], 2.0, DRESS_D))
    for y in (214, 248, 282):
        o.append(circle(cx - 2, y, 4, '#fbf6ea'))
    return o


def figure(expr='calm'):
    """Full figure, feet at y=0, about 7 heads; weight on the near leg, the other foot pointed, a posy in both hands."""
    o = []
    # legs: thin, a small calf, tiny ankles; red ballet flats
    o.append(limb([(-16, -240), (-14, -170), (-12, -100), (-12, -24)], [24, 21, 15, 9], SKIN))
    o.append(limb([(18, -240), (24, -170), (22, -100), (34, -34)], [24, 21, 15, 9], SKIN))
    o.append(shape([(-30, -2, 'c'), (-24, -24), (-6, -30), (-2, -10), (8, -2, 'c')], '#b8352b'))
    o.append(shape([(28, -40), (40, -38), (60, -16, 'c'), (52, -10), (32, -22)], '#b8352b'))
    # full skirt swinging a little to the right, scalloped hem, dots
    skirt = [(-36, -468), (32, -470), (100, -330), (128, -232), (98, -218), (66, -228), (36, -214), (4, -226), (-28, -212),
             (-60, -224), (-104, -218)]
    o.append(shape(skirt, DRESS))
    o.append(pattern_dots(skirt, -120, -470, 140, -205, 20, 2.4, '#fbf0d4', 'anyaskirt'))
    o.append(brush([(-14, -440), (-34, -240)], 2.4, DRESS_D, taper=(0.4, 0.2), opacity=0.7))
    o.append(brush([(16, -440), (54, -240)], 2.4, DRESS_D, taper=(0.4, 0.2), opacity=0.7))
    # bodice and open cardigan
    o.append(shape([(-34, -604), (30, -606), (38, -540), (30, -466), (-36, -466), (-42, -540)], DRESS))
    o.append(shape([(-36, -466), (-42, -540), (-34, -606), (-52, -600), (-60, -540), (-54, -456)], CARDI))
    o.append(shape([(30, -466), (38, -540), (30, -606), (50, -600), (58, -540), (54, -458)], CARDI))
    o.append(brush([(-38, -472), (34, -474)], 7, DRESS_D, taper=(0, 0)))
    o.append(shape([(-4, -606), (-30, -608), (-38, -592), (-22, -580), (-4, -590, 'c')], COLLAR))
    o.append(shape([(4, -606), (30, -608), (38, -592), (22, -580), (4, -590, 'c')], COLLAR))
    # arms: both bent, the hands meet at the waist holding the flowers
    o.append(limb([(-40, -598), (-58, -580), (-64, -536), (-44, -496), (-8, -490)], [28, 28, 22, 18, 15], CARDI))
    o.append(limb([(38, -600), (56, -582), (62, -536), (40, -498), (12, -494)], [28, 28, 22, 18, 15], CARDI))
    o.append(brush([(-60, -560), (-56, -520), (-42, -500)], 2.4, CARDI_D, taper=(0.4, 0.4)))
    o.append(brush([(58, -560), (54, -522), (40, -502)], 2.4, CARDI_D, taper=(0.4, 0.4)))
    o.append(brush([(30, -500), (34, -536)], 2, '#2e6b3c'))
    o.append(brush([(30, -500), (20, -540)], 2, '#2e6b3c'))
    o.append(brush([(30, -500), (42, -538)], 2, '#2e6b3c'))
    for (fx, fy, c) in ((18, -544, '#fbf6ea'), (32, -556, '#ec7f72'), (46, -544, '#fbf6ea'), (30, -538, '#e8b33a')):
        o.append(circle(fx, fy, 8, c))
        o.append(circle(fx, fy, 2.6, '#c98f22'))
    o.append(ell(2, -492, 10, 8, SKIN))
    o.append(ell(20, -494, 9, 8, SKIN))
    # neck and head, tilted toward the flowers
    o.append(shape([(-9, -630), (11, -626), (12, -600), (-11, -600)], SKIN_D))
    o.append('<g transform="translate(4,-670) rotate(-7) scale(0.5)">' + ''.join(head('34', expr, neck=False)) + '</g>')
    return o
