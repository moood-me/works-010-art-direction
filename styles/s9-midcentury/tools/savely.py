"""Савелий Петрович, about 70, a watchmaker — grumpy outside, kind inside.
A Šašek head: tall bald dome, a big soft nose, a white walrus moustache, heavy white brows, little round spectacles,
the watchmaker's loupe pushed up on his forehead."""
from kit import shape, brush, blush, ell, circle, dryb, limb, mix, INK
from face import eye, brow, mouth, EXPR

SKIN = '#efc3a2'
SKIN_D = '#d99c7c'
NOSE = '#e79a80'
WHITE = '#f6f1e6'
WHITE_D = '#d9d2c4'
VEST = '#a9382b'
VEST_D = '#7e2a21'
SHIRT = '#f4efe2'
SHIRT_D = '#d8cfbd'
TROUS = '#4e4036'
TIE = '#2f5a4a'
SLEEVE = '#cdd6d0'
BRASS = '#d9a441'
CHEEK = '#e2715c'
BUST_DY = -52

OWN = {
    'calm':     dict(eye='dot', brow=(5, -2), mouth=None),
    'joy':      dict(eye='happy', brow=(-2, 0), mouth='grin', cheek=1.3),
    'surprise': dict(eye='wide', brow=(-9, -8), mouth='o'),
    'sad':      dict(eye='sad', brow=(-4, 6), mouth='sad'),
    'anger':    dict(eye='dot', brow=(9, -6), mouth='shout'),
}


def _e(expr):
    e = dict(EXPR[expr])
    e.update(OWN.get(expr, {}))
    return e


def _brow(x, y, side, inner, outer, s=1.0, squash=1.0):
    """Heavy white brow: a tufted block, inner end lowered for the frown."""
    L = squash
    pts = [(x - side * 14 * L, y + inner - 3), (x - side * 4 * L, y - 9 + (inner + outer) * 0.4), (x + side * 10 * L, y - 8 + outer),
           (x + side * 20 * L, y + outer + 2, 'c'), (x + side * 8 * L, y + 1 + outer * 0.7), (x - side * 12 * L, y + inner + 5, 'c')]
    return shape(pts, WHITE) + brush([(x - side * 10 * L, y + inner), (x + side * 14 * L, y + outer - 2)], 1.4, WHITE_D,
                                     taper=(0.3, 0.3), opacity=0.8)


def head(view='34', expr='calm'):
    e = _e(expr)
    o = []
    if view != '34':
        raise ValueError('Савелий Петрович is drawn in three-quarter only')
    # white hair: a fringe of tufts round the back of the dome
    o.append(shape([(-46, -70), (-78, -50), (-92, -14), (-86, 28), (-70, 52), (-54, 40), (-60, 10), (-50, -30)], WHITE))
    o.append(dryb([[(-80, -40), (-84, 0), (-72, 36)], [(-66, -54), (-76, -10)]], 2.2, WHITE_D, 0.8))
    # neck
    o.append(shape([(-30, 60), (30, 74), (34, 150), (-40, 150)], SKIN_D))
    # the dome and face
    o.append(shape([(-60, -36), (-56, -86), (-24, -116), (22, -118), (56, -96), (70, -58), (72, -16), (70, 30), (62, 64),
                    (40, 90), (12, 100), (-18, 94), (-44, 74), (-58, 40), (-64, 0)], SKIN))
    # ear
    o.append(shape([(-56, -12), (-74, -18), (-82, 6), (-74, 34), (-56, 32)], SKIN))
    o.append(brush([(-62, -6), (-72, 6), (-66, 26)], 2.2, SKIN_D, taper=(0.3, 0.3)))
    # loupe pushed up on the forehead: black barrel, brass rim, the band round the head
    o.append(brush([(-60, -66), (-10, -88), (40, -92), (70, -78)], 4, '#3a2c26', taper=(0.05, 0.05)))
    o.append(f'<g transform="rotate(-18 18 -84)">' + shape([(4, -100, 'c'), (34, -100, 'c'), (38, -70, 'c'), (0, -70, 'c')], '#2c2420')
             + ell(19, -70, 19, 6, BRASS) + ell(19, -70, 13, 3.6, '#7fa9b0') + '</g>')
    # forehead lines and crow's feet
    for dy in (-50, -40):
        o.append(brush([(-30, dy + 2), (10, dy - 2), (50, dy + 1)], 1.6, SKIN_D, taper=(0.4, 0.4)))
    cheek = e.get('cheek', 1.0)
    o.append(blush(-16, 38, 17 * cheek, CHEEK, 0.6))
    o.append(blush(60, 30, 8 * cheek, CHEEK, 0.5))
    # eyes, small, behind round spectacles
    o.append(eye(-8, 4, 1.25, e['eye'], side=-1, lash=False))
    o.append(eye(44, 2, 1.15, e['eye'], side=1, squash=0.7, lash=False))
    o.append(brush([(-30, 12), (-36, 6), (-38, 0)], 1.6, SKIN_D, taper=(0.3, 0.3)))
    o.append(brush([(-30, 18), (-37, 16)], 1.4, SKIN_D, taper=(0.3, 0.3)))
    bi, bo = e['brow']
    o.append(_brow(-6, -18, -1, bi, bo))
    o.append(_brow(46, -20, 1, bi, bo, squash=0.6))
    # big soft nose, ruddy, that breaks the far cheek
    o.append(shape([(30, -6), (44, -12), (60, 8), (78, 26), (84, 40), (76, 50), (62, 48), (50, 50), (40, 42), (38, 22)], NOSE))
    o.append(brush([(52, 46), (60, 40), (66, 44)], 2.0, mix(NOSE, INK, 0.5), taper=(0.3, 0.3)))
    # spectacles: little round rims, low on the nose
    o.append(f'<circle cx="-8" cy="6" r="15" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    o.append(f'<ellipse cx="44" cy="4" rx="10" ry="14" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    o.append(brush([(7, 4), (22, 0), (34, 2)], 2.0, INK, taper=(0.1, 0.1)))
    o.append(brush([(-23, 4), (-56, -4)], 2.0, INK, taper=(0.1, 0.4)))
    # mouth under the moustache
    m = e['mouth']
    if m:
        o.append(mouth(26, 80, 1.3, m, side=1, width=0.9))
    else:
        o.append(brush([(14, 84), (26, 88), (38, 84)], 3.0, '#b0503e', taper=(0.3, 0.3)))
    # the walrus moustache: two heavy white sweeps
    o.append(shape([(36, 46), (60, 50), (80, 58), (82, 74, 'c'), (64, 70), (48, 72), (30, 64), (12, 74), (-10, 78, 'c'),
                    (-4, 62), (14, 50)], WHITE))
    o.append(dryb([[(20, 54), (0, 70)], [(46, 56), (72, 66)], [(34, 58), (30, 66)]], 1.6, WHITE_D, 0.9))
    return o


def bust(view='34'):
    o = []
    body = [(-150, 300), (-146, 230), (-120, 176), (-54, 140), (48, 146), (110, 170), (138, 216), (150, 300)]
    o.append(shape(body, SLEEVE))
    # waistcoat with a V opening, shirt and tie inside
    o.append(shape([(-150, 300), (-146, 230), (-120, 176), (-74, 150), (-24, 156), (6, 250), (14, 300)], VEST))
    o.append(shape([(150, 300), (138, 216), (110, 170), (70, 152), (40, 160), (22, 250), (14, 300)], VEST))
    o.append(shape([(-18, 146), (2, 150), (14, 176), (2, 182), (-12, 172)], SHIRT_D))
    o.append(shape([(-2, 176), (10, 176), (14, 240), (4, 252), (-6, 240)], TIE))
    o.append(shape([(-20, 144), (-6, 176, 'c'), (-34, 166)], SHIRT))
    o.append(shape([(30, 148), (14, 176, 'c'), (44, 168)], SHIRT))
    for y in (250, 282):
        o.append(circle(10, y, 4, BRASS))
    # watch chain
    o.append(brush([(-90, 262), (-50, 282), (8, 266)], 2.4, BRASS, taper=(0.05, 0.05)))
    return o


def figure(expr='calm'):
    """Full figure, feet at y=0: short and heavy (under 5 heads), the back rounded, bent over a pocket watch."""
    o = []
    # short baggy trousers, big shoes, knees a little bent
    o.append(limb([(-26, -214), (-32, -120), (-30, -26)], [50, 42, 38], TROUS, cap=False))
    o.append(limb([(24, -214), (34, -120), (36, -26)], [50, 42, 38], TROUS, cap=False))
    o.append(brush([(-20, -150), (-26, -40)], 2, mix(TROUS, INK, 0.4), taper=(0.4, 0.4)))
    o.append(shape([(-66, -2, 'c'), (-58, -28), (-20, -36), (-8, -18), (-6, -2, 'c')], '#2c2420'))
    o.append(shape([(14, -2, 'c'), (16, -34), (54, -32), (80, -14), (82, -2, 'c')], '#2c2420'))
    # the back arm (sleeve) behind the body
    o.append(limb([(-40, -400), (-70, -330), (-58, -262)], [40, 34, 30], SLEEVE))
    # a bean of a body: round back, belly forward and down
    body = [(-56, -200), (-72, -290), (-66, -370), (-38, -416), (10, -424), (48, -404), (74, -350), (86, -280), (74, -214),
            (40, -194)]
    o.append(shape(body, SHIRT))
    o.append(shape([(-56, -200), (-72, -290), (-66, -370), (-38, -416), (-2, -422), (22, -330), (30, -194)], VEST))
    o.append(shape([(46, -406), (74, -350), (86, -280), (74, -214), (40, -194), (36, -300), (34, -370)], VEST))
    o.append(shape([(4, -424), (24, -420), (30, -370), (26, -360), (18, -372)], TIE))
    for y in (-330, -290, -250):
        o.append(circle(34 - (y + 330) * 0.02, y, 4.5, BRASS))
    o.append(brush([(-50, -280), (-6, -262), (34, -276)], 2.4, BRASS, taper=(0.05, 0.05)))
    o.append(brush([(-56, -206), (-20, -196), (38, -198)], 3, VEST_D, taper=(0.2, 0.2), opacity=0.8))
    # the front arm: bent up, the watch on its chain held under his nose
    o.append(limb([(36, -404), (72, -350), (92, -380), (96, -414)], [40, 34, 30, 26], SLEEVE))
    o.append(ell(96, -420, 13, 14, SKIN))
    o.append(brush([(96, -416), (90, -330), (60, -300)], 2, BRASS, taper=(0, 0)))
    o.append(circle(108, -446, 21, BRASS))
    o.append(circle(108, -446, 15, '#fbf6ea'))
    o.append(circle(108, -470, 4, BRASS))
    o.append(brush([(108, -446), (109, -458)], 2, INK, taper=(0, 0.3)))
    o.append(brush([(108, -446), (117, -443)], 2, INK, taper=(0, 0.3)))
    o.append(ell(92, -416, 7, 9, SKIN))
    # head bent forward and down toward the watch
    o.append('<g transform="translate(34,-482) rotate(12) scale(0.6)">' + ''.join(head('34', expr)) + '</g>')
    return o
