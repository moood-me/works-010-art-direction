"""Марат, about 35, a cook — huge, loud, merry, generous. The biggest of the cast: a barrel on short legs.
A Šašek man: a broad head, a cap of dark curls, a black beard as one big shape with the white grin cut into it,
a broad ruddy nose, thick brows. A white cook's jacket with rolled sleeves, a long terracotta apron, a towel over
the shoulder, a ladle raised like a toast."""
from kit import edge, shape, brush, blush, ell, circle, dryb, limb, hand, stripes, mix, INK
from face import eye, mouth, EXPR

SKIN = '#ecb991'
SKIN_D = '#d2946c'
NOSE = '#e6a583'
HAIR = '#2b2220'
HAIR_L = '#5c463a'
WHITE = '#f7f1e3'
WHITE_D = '#ddd3bf'
APRON = '#cf6534'
APRON_D = '#a84c24'
TROUS = '#3f4652'
SHOE = '#2c2420'
TOWEL = '#ead9b6'
STEEL = '#aebcbc'
STEEL_D = '#7d8c8e'
CHEEK = '#e0634a'
FIG_SCALE = 0.88  # how much larger the full figure is drawn on its own page (he is the tallest: a little smaller)
BUST_DY = 14

# his resting face is already a wide smile; joy is the laugh with the whole face
OWN = {
    'calm':     dict(eye='dot', brow=(-2, -1), mouth='beam', cheek=1.1, ms=1.25),
    'joy':      dict(eye='happy', brow=(-5, -3), mouth='laugh', cheek=1.3, ms=1.5),
    'surprise': dict(eye='wide', brow=(-10, -9), mouth='o', ms=2.0),
    'sad':      dict(eye='sad', brow=(-7, 6), mouth='sad', ms=1.8),
    'anger':    dict(eye='glare', brow=(10, -6), mouth='shout', cheek=1.3, ms=1.8),
}


def _e(expr):
    e = dict(EXPR[expr])
    e.update(OWN.get(expr, {}))
    return e


def _brow(x, y, side, inner, outer, squash=1.0):
    """A thick dark brow: a tapered block."""
    L = squash
    pts = [(x - side * 14 * L, y + inner - 2, 'c'), (x - side * 3 * L, y - 8 + (inner + outer) * 0.45), (x + side * 12 * L, y - 6 + outer),
           (x + side * 21 * L, y + outer + 3, 'c'), (x + side * 8 * L, y + 1 + outer * 0.7), (x - side * 11 * L, y + inner + 5)]
    return shape(pts, HAIR)


def _curls(pts, r):
    """Curly hair: round dabs of the brush along a line (the silhouette becomes scalloped)."""
    return ''.join(circle(x, y, r if len(q) < 3 else q[2], HAIR) for q in pts for x, y in [q[:2]])


def _mouth(x, y, e, width=1.0, side=1):
    return mouth(x, y, e.get('ms', 1), e['mouth'], side=side, width=width)


def head(view='34', expr='calm', neck=True):
    """The head around (0, 0), crown near y=-120, the beard down to y=135; neck=False leaves the neck to the figure."""
    e = _e(expr)
    bi, bo = e['brow']
    cheek = e.get('cheek', 1.0)
    laugh = e['mouth'] in ('laugh', 'beam')
    o = []
    if view == '34':
        # the cap of curls behind the head
        o.append(shape([(-76, 0), (-88, -50), (-74, -98), (-36, -126), (20, -130), (64, -110), (86, -70), (84, -30), (0, -40)], HAIR))
        o.append(_curls([(-84, -22), (-88, -56), (-76, -90), (-52, -114), (-20, -128), (14, -131), (46, -122), (72, -102), (86, -72)], 17))
        if neck:
            o.append(shape([(-46, 60), (44, 70), (48, 150), (-52, 150)], SKIN_D))
        face = [(-68, -36), (-58, -84), (-22, -110), (26, -110), (62, -88), (78, -48), (82, -6), (80, 30), (72, 60), (52, 88),
                (20, 102), (-16, 98), (-46, 78), (-64, 44), (-72, 0)]
        o.append(shape(face, SKIN))
        o.append(blush(-26, 30, 19 * cheek, CHEEK, 0.62))
        # the beard: one dark shape from ear to ear, scalloped below
        o.append(shape([(-72, -14), (-58, 22), (-38, 46), (-8, 54), (18, 46), (42, 44), (60, 50), (74, 38), (84, 14),
                        (90, 44), (86, 78), (66, 108), (36, 128), (0, 134), (-36, 122), (-64, 96), (-80, 56), (-80, 10)], HAIR))
        o.append(_curls([(-70, 92), (-46, 116), (-14, 130), (20, 132), (52, 118), (76, 94)], 15))
        o.append(dryb([[(-62, 50), (-50, 86), (-24, 108)], [(-30, 70), (-10, 104), (20, 114)], [(70, 66), (62, 96), (40, 112)]],
                      2.4, HAIR_L, 0.7))
        # ear
        o.append(ell(-76, 2, 13, 19, SKIN, rot=-8))
        o.append(brush([(-80, -8), (-85, 4), (-78, 14)], 2.4, SKIN_D, taper=(0.3, 0.3)))
        # eyes, laugh lines, brows
        ey = 2 if e['eye'] != 'happy' else 4
        o.append(eye(-14, ey - 4, 1.4, e['eye'], side=-1, lash=False))
        o.append(eye(52, ey - 6, 1.3, e['eye'], side=1, squash=0.7, lash=False))
        if laugh:
            o.append(brush([(-32, 2), (-40, -2), (-44, -9)], 1.8, SKIN_D, taper=(0.2, 0.5)))
            o.append(brush([(-32, 7), (-42, 8)], 1.6, SKIN_D, taper=(0.2, 0.5)))
            o.append(brush([(-28, 12), (-14, 16), (0, 11)], 1.8, SKIN_D, taper=(0.4, 0.4)))
        o.append(_brow(-14, -25, -1, bi, bo))
        o.append(_brow(54, -27, 1, bi, bo, squash=0.62))
        # the broad nose
        o.append(shape([(30, 4), (42, 0), (58, 12), (74, 28), (74, 42), (58, 48), (38, 46), (26, 38), (25, 20)], NOSE))
        o.append(brush([(48, 44), (56, 39), (64, 43)], 2.2, mix(NOSE, INK, 0.5), taper=(0.3, 0.3)))
        o.append(brush([(25, 30), (27, 39), (35, 45)], 2.0, mix(NOSE, INK, 0.3), taper=(0.3, 0.3)))
        # mouth in the beard, the moustache over it
        o.append(_mouth(30, 76, e, 1.0))
        o.append(shape([(-6, 52), (16, 44), (34, 48), (48, 44), (64, 50), (82, 66, 'c'), (62, 66), (46, 60), (34, 63), (16, 62),
                        (-4, 70), (-18, 76, 'c')], HAIR))
        o.append(dryb([[(12, 50), (-6, 66)], [(52, 50), (72, 62)]], 2.0, HAIR_L, 0.7))
        # curls over the forehead
        o.append(_curls([(-66, -52, 16), (-52, -80, 19), (-26, -98, 21), (6, -104, 22), (38, -98, 20), (62, -80, 18), (78, -56, 13)], 18))
        o.append(dryb([[(-60, -84), (-44, -104), (-22, -112)], [(-10, -112), (10, -120), (30, -114)], [(44, -108), (62, -98), (72, -82)],
                       [(-76, -40), (-80, -60), (-70, -76)]], 2.6, HAIR_L, 0.7))
    elif view == 'front':
        o.append(shape([(-88, 0), (-94, -50), (-78, -98), (-40, -126), (0, -132), (40, -126), (78, -98), (94, -50), (88, 0), (0, -40)], HAIR))
        o.append(_curls([(-90, -22), (-94, -56), (-80, -90), (-56, -114), (-22, -128), (22, -128), (56, -114), (80, -90), (94, -56),
                         (90, -22)], 17))
        if neck:
            o.append(shape([(-46, 60), (46, 60), (50, 150), (-50, 150)], SKIN_D))
        o.append(shape([(0, -110), (44, -102), (72, -70), (82, -24), (80, 24), (70, 62), (46, 90), (0, 102), (-46, 90), (-70, 62),
                        (-80, 24), (-82, -24), (-72, -70), (-44, -102)], SKIN))
        o.append(blush(-46, 30, 17 * cheek, CHEEK, 0.62))
        o.append(blush(46, 30, 17 * cheek, CHEEK, 0.62))
        o.append(shape([(-84, -14), (-68, 24), (-42, 46), (-16, 46), (0, 42), (16, 46), (42, 46), (68, 24), (84, -14), (90, 40),
                        (80, 88), (48, 122), (0, 134), (-48, 122), (-80, 88), (-90, 40)], HAIR))
        o.append(_curls([(-78, 88), (-54, 114), (-22, 130), (22, 130), (54, 114), (78, 88)], 15))
        o.append(dryb([[(-70, 50), (-58, 90), (-30, 112)], [(70, 50), (58, 90), (30, 112)], [(-10, 100), (0, 118), (12, 100)]],
                      2.4, HAIR_L, 0.7))
        o.append(ell(-88, 2, 12, 19, SKIN, rot=-8))
        o.append(ell(88, 2, 12, 19, SKIN, rot=8))
        ey = 2 if e['eye'] != 'happy' else 4
        o.append(eye(-30, ey, 1.4, e['eye'], side=-1, lash=False))
        o.append(eye(30, ey, 1.4, e['eye'], side=1, lash=False))
        if laugh:
            for t in (-1, 1):
                o.append(brush([(t * 48, 6), (t * 56, 2), (t * 60, -5)], 1.8, SKIN_D, taper=(0.2, 0.5)))
                o.append(brush([(t * 44, 16), (t * 30, 20), (t * 16, 15)], 1.8, SKIN_D, taper=(0.4, 0.4)))
        o.append(_brow(-31, -20, -1, bi, bo))
        o.append(_brow(31, -20, 1, bi, bo))
        o.append(shape([(-9, -8), (9, -8), (20, 20), (25, 36), (11, 45), (-11, 45), (-25, 36), (-20, 20)], NOSE))
        o.append(brush([(-12, 42), (-5, 37), (0, 41)], 2.2, mix(NOSE, INK, 0.5), taper=(0.3, 0.3)))
        o.append(brush([(12, 42), (5, 37), (0, 41)], 2.2, mix(NOSE, INK, 0.5), taper=(0.3, 0.3)))
        o.append(_mouth(0, 76, e, 1.1))
        o.append(shape([(0, 48), (22, 44), (48, 54), (62, 70, 'c'), (38, 64), (14, 62), (0, 59), (-14, 62), (-38, 64), (-62, 70, 'c'),
                        (-48, 54), (-22, 44)], HAIR))
        o.append(dryb([[(-12, 52), (-40, 62)], [(12, 52), (40, 62)]], 2.0, HAIR_L, 0.7))
        o.append(_curls([(-76, -52, 15), (-60, -80, 19), (-32, -98, 21), (0, -104, 22), (32, -98, 21), (60, -80, 19), (76, -52, 15)], 18))
        o.append(dryb([[(-66, -84), (-48, -104), (-26, -112)], [(-10, -114), (10, -120), (28, -112)], [(46, -106), (64, -92), (74, -74)]],
                      2.6, HAIR_L, 0.7))
    elif view == 'side':
        o.append(shape([(-20, -10), (-70, 30), (-84, -20), (-84, -66), (-58, -110), (-10, -130), (36, -124), (64, -98), (68, -70),
                        (20, -60)], HAIR))
        o.append(_curls([(-76, 14), (-88, -18), (-90, -52), (-78, -86), (-54, -112), (-22, -128), (12, -131), (44, -120), (66, -98)], 17))
        if neck:
            o.append(shape([(-34, 50), (30, 70), (30, 150), (-40, 150)], SKIN_D))
        o.append(shape([(-66, -30), (-56, -84), (-18, -112), (30, -108), (60, -84), (68, -48), (68, -14), (74, 0), (80, 30), (72, 50),
                        (70, 70), (60, 92), (20, 100), (-30, 84), (-58, 50), (-70, 10)], SKIN))
        o.append(blush(30, 30, 18 * cheek, CHEEK, 0.62))
        # the beard juts forward under the chin
        o.append(shape([(-30, -14), (-16, 22), (8, 44), (40, 48), (64, 48), (78, 54), (84, 72), (80, 102), (60, 128), (26, 136),
                        (-10, 124), (-34, 96), (-42, 50), (-40, 4)], HAIR))
        o.append(_curls([(-30, 96), (-8, 120), (24, 134), (56, 126), (78, 100)], 14))
        o.append(dryb([[(-24, 50), (-12, 90), (14, 112)], [(20, 70), (36, 104), (60, 110)]], 2.4, HAIR_L, 0.7))
        o.append(ell(-26, 2, 13, 19, SKIN, rot=-6))
        o.append(brush([(-30, -8), (-35, 4), (-28, 14)], 2.4, SKIN_D, taper=(0.3, 0.3)))
        ey = 0 if e['eye'] != 'happy' else 2
        o.append(eye(48, ey, 1.4, e['eye'], side=1, squash=0.7, lash=False))
        if laugh:
            o.append(brush([(30, 6), (22, 2), (18, -5)], 1.8, SKIN_D, taper=(0.2, 0.5)))
            o.append(brush([(34, 15), (46, 19), (58, 14)], 1.8, SKIN_D, taper=(0.4, 0.4)))
        o.append(_brow(52, -22, 1, bi, bo, squash=0.7))
        o.append(shape([(62, -12), (74, -4), (92, 22), (96, 36), (86, 46), (68, 44), (58, 30), (60, 8)], NOSE))
        o.append(brush([(70, 42), (78, 36), (86, 41)], 2.2, mix(NOSE, INK, 0.5), taper=(0.3, 0.3)))
        o.append(_mouth(70, 76, e, 0.55))
        o.append(shape([(50, 46), (70, 44), (88, 50), (94, 62, 'c'), (78, 62), (60, 64), (40, 72, 'c')], HAIR))
        o.append(shape([(66, -76), (44, -70), (16, -62), (-8, -40), (-20, -14), (-38, 22), (-70, 34), (-86, -20), (-84, -66),
                        (-58, -110), (-10, -130), (36, -124), (64, -100)], HAIR))
        o.append(_curls([(-30, 8, 14), (-18, -22, 15), (-4, -46, 17), (20, -64, 19), (46, -72, 18), (64, -66, 12)], 18))
        o.append(dryb([[(-60, -84), (-40, -106), (-14, -116)], [(0, -112), (22, -118), (44, -108)], [(-78, -30), (-80, -56), (-68, -76)]],
                      2.6, HAIR_L, 0.7))
    else:
        raise ValueError(view)
    return o


def _towel(pts, cid):
    return shape(pts, TOWEL) + stripes(pts, min(p[0] for p in pts), min(p[1] for p in pts) + 14, max(p[0] for p in pts),
                                       max(p[1] for p in pts), 60, 7, APRON, cid, angle=-6)


def bust(view='34'):
    """Shoulders that fill the sheet: the white jacket, the bib of the apron, the towel over the near shoulder."""
    o = []
    if view == 'side':
        body = [(-130, 300), (-124, 200), (-84, 138), (20, 132), (84, 180), (106, 300)]
        o.append(shape(body, WHITE))
        o.append(shape([(30, 190, 'c'), (88, 196), (106, 300), (22, 300)], APRON))
        o.append(brush([(30, 192), (10, 150), (-20, 132)], 7, APRON, taper=(0, 0.1)))
        o.append(shape([(-44, 126), (26, 130), (32, 150), (-6, 156), (-46, 146)], WHITE_D))
        o.append(_towel([(-70, 136, 'c'), (-16, 134, 'c'), (-14, 262, 'c'), (-74, 258, 'c')], 'martowside'))
        o.append(brush([(-104, 210), (-100, 300)], 3, WHITE_D, taper=(0.3, 0)))
        return o
    sx = 1 if view == '34' else 0
    body = [(-196 + sx * 10, 300), (-190 + sx * 10, 214), (-156 + sx * 8, 160), (-70, 126), (64 + sx * 6, 130), (148 + sx * 4, 158),
            (182, 212), (190, 300)]
    o.append(shape(body, WHITE))
    cx = sx * 10
    # double-breasted buttons beside the bib
    for t in (-1, 1):
        for y in (206, 248, 290):
            o.append(circle(cx + t * 86, y, 5.5, APRON))
    # the bib of the apron and its strap round the neck
    o.append(brush([(cx - 50, 206), (cx - 46, 160), (cx - 40, 134)], 8, APRON, taper=(0, 0.1)))
    o.append(brush([(cx + 52, 206), (cx + 50, 160), (cx + 46, 134)], 8, APRON, taper=(0, 0.1)))
    o.append(shape([(cx - 62, 200, 'c'), (cx + 64, 200, 'c'), (cx + 70, 300), (cx - 68, 300)], APRON))
    o.append(brush([(cx - 60, 214), (cx + 62, 214)], 2.4, APRON_D, taper=(0.05, 0.05)))
    # the stand-up collar
    o.append(shape([(cx - 74, 124), (cx, 134), (cx + 80, 126), (cx + 74, 146), (cx, 156), (cx - 70, 144)], WHITE_D))
    # sleeve seams, the towel over the near shoulder
    o.append(brush([(140, 196), (142, 300)], 3, WHITE_D, taper=(0.3, 0)))
    o.append(_towel([(-158 + sx * 8, 150, 'c'), (-100 + sx * 8, 136, 'c'), (-92 + sx * 8, 280, 'c'), (-150 + sx * 8, 290, 'c')],
                    'martow' + view))
    return o


def figure(expr='joy'):
    """Full figure, feet at y=0, about 6 heads and twice as wide as anyone: leaning back in a laugh, the ladle raised
    like a toast, the other fist on his hip."""
    o = []
    # short legs under the apron, big shoes
    o.append(limb([(-30, -240), (-38, -130), (-40, -28)], [74, 56, 46], TROUS, cap=False))
    o.append(limb([(40, -240), (48, -130), (50, -28)], [74, 56, 46], TROUS, cap=False))
    o.append(shape([(-84, -2, 'c'), (-76, -32), (-30, -40), (-12, -20), (-10, -2, 'c')], SHOE))
    o.append(shape([(22, -2, 'c'), (24, -38), (64, -36), (100, -16), (102, -2, 'c')], SHOE))
    # the barrel: white jacket; the shoulders lean back, the belly goes first
    body = [(-92, -250), (-124, -340), (-142, -450), (-138, -560), (-104, -630), (-36, -652), (40, -646), (98, -606), (136, -530),
            (164, -420), (160, -320), (122, -250)]
    o.append(shape(body, WHITE))
    for y in (-596, -556):
        o.append(circle(92 + (y + 596) * -0.5, y, 5, APRON))
    o.append(brush([(-128, -520), (-124, -420), (-112, -330)], 3, WHITE_D, taper=(0.3, 0.3)))
    # the long apron: bib, wide skirt round the belly, the tie
    o.append(brush([(-46, -560), (-52, -620), (-44, -650)], 9, APRON, taper=(0, 0.1)))
    o.append(brush([(66, -556), (60, -616), (42, -648)], 9, APRON, taper=(0, 0.1)))
    o.append(shape([(-54, -566, 'c'), (72, -562, 'c'), (96, -468), (-66, -470)], APRON))
    skirt = [(-104, -476, 'c'), (20, -468), (158, -474, 'c'), (176, -380), (160, -260), (128, -142, 'c'), (30, -134), (-60, -146, 'c'),
             (-88, -230), (-112, -340)]
    o.append(shape(skirt, APRON))
    o.append(brush([(-106, -474), (20, -462), (160, -470)], 9, APRON_D, taper=(0.02, 0.02)))
    o.append(shape([(34, -396, 'c'), (118, -392, 'c'), (112, -308), (40, -314)], APRON_D, opacity=0.55))
    o.append(dryb([[(-40, -430), (-54, -290), (-42, -170)], [(140, -430), (150, -310), (122, -180)], [(30, -270), (34, -210), (30, -160)]],
                  3, APRON_D, 0.6))
    # the towel over the near shoulder
    o.append(_towel([(-122, -642, 'c'), (-74, -650, 'c'), (-64, -520, 'c'), (-114, -510, 'c')], 'martowfig'))
    # the near arm: fist on the hip, elbow out
    o.append(limb([(-196, -492), (-134, -418)], [48, 38], SKIN, cap='round'))
    o.append(limb([(-118, -598), (-196, -496)], [66, 56], WHITE, cap='round'))
    o.append(brush([(-226, -506), (-198, -484), (-170, -474)], 9, WHITE_D, taper=(0.05, 0.05)))
    o.append(hand(-140, -428, 2.4, -62, SKIN, SKIN_D, 'fist', side=1))
    # the far arm: up and out, the ladle held high
    o.append(limb([(190, -580), (216, -676)], [48, 36], SKIN, cap='round'))
    o.append(limb([(96, -596), (188, -574)], [66, 56], WHITE, cap='round'))
    o.append(brush([(174, -546), (192, -562), (214, -596)], 9, WHITE_D, taper=(0.05, 0.05)))
    # ladle: the handle through the fist, the bowl up
    o.append(brush([(226, -640), (212, -740), (194, -800)], 7, STEEL_D, taper=(0, 0)))
    o.append(shape([(160, -828, 'c'), (226, -806, 'c'), (212, -776), (184, -770), (164, -790)], STEEL))
    o.append(brush([(162, -827), (194, -820), (225, -806)], 5, STEEL_D, taper=(0.05, 0.05)))
    o.append(hand(218, -670, 2.4, 172, SKIN, SKIN_D, 'fist', side=-1))
    # the head thrown back: the beard lies on the chest (hardly any neck)
    o.append('<g transform="translate(-18,-718) rotate(-10) scale(0.62)">' + ''.join(head('34', expr, neck=False)) + '</g>')
    return o
