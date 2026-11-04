"""Вера, about 40 — strict, clever, tired. A long angular face, a straight nose that breaks the far cheek,
cat-eye glasses, dark hair pulled into a bun with a grey streak, a plum suit, books held to her side."""
from kit import edge, shape, brush, blush, ell, circle, dryb, limb, path, mix, INK
from face import eye, brow, mouth, EXPR

SKIN = '#f1d2bc'
SKIN_D = '#ddae96'
HAIR = '#2c2630'
HAIR_L = '#4c4450'
GREY = '#b9b4b8'
SUIT = '#6e3a5c'
SUIT_D = '#542b46'
BLOUSE = '#f6f0e4'
BLOUSE_D = '#dcd2c0'
FRAME = '#22343c'
CHEEK = '#e08474'
GOLD = '#d9a441'
FIG_SCALE = 1.0  # how much larger the full figure is drawn on its own page
BUST_DY = -40

OWN = {
    'calm':     dict(eye='lid', brow=(3, 0), mouth='flat'),
    'joy':      dict(eye='happy', brow=(-3, -1), mouth='smile', cheek=1.2),
    'surprise': dict(eye='wide', brow=(-8, -6), mouth='o'),
    'sad':      dict(eye='sad', brow=(-4, 4), mouth='sad'),
    'anger':    dict(eye='glare', brow=(7, -3), mouth='frown'),
}


def _e(expr):
    e = dict(EXPR[expr])
    e.update(OWN.get(expr, {}))
    return e


def _lens(x, y, side, sq=1.0):
    """Cat-eye rim: flat bottom, the outer top corner swept up."""
    pts = [(x + side * 15 * sq, y - 14, 'c'), (x + side * 2 * sq, y - 9), (x - side * 12 * sq, y - 6), (x - side * 13 * sq, y + 5),
           (x - side * 2 * sq, y + 9), (x + side * 11 * sq, y + 5)]
    return f'<path d="{path(pts)}" fill="#ffffff" fill-opacity="0.12" stroke="{FRAME}" stroke-width="3.2" stroke-linejoin="round"/>'


def head(view='34', expr='calm', neck=True):
    """The head around (0, 0), crown near y=-120, chin near y=95; neck=False leaves the neck to the figure."""
    if view != '34':
        raise ValueError('Вера is drawn in three-quarter only')
    e = _e(expr)
    bi, bo = e['brow']
    cheek = e.get('cheek', 1.0)
    o = []
    # the bun at the back, the neck
    o.append(circle(-60, -100, 34, HAIR))
    o.append(dryb([[(-84, -110), (-60, -128), (-36, -112)], [(-86, -94), (-60, -82), (-36, -96)]], 2.4, HAIR_L, 0.8))
    if neck:
        o.append(shape([(-28, 66), (22, 80), (24, 150), (-34, 150)], SKIN_D))
    # long face: high cheekbone on the far side, a narrow pointed chin
    face = [(-56, -60), (-40, -100), (0, -116), (42, -104), (62, -70), (66, -30), (70, 6), (66, 32), (56, 62),
                    (38, 90), (18, 106, 'c'), (-6, 98), (-34, 74), (-52, 40), (-60, -10)]
    o.append(shape(face, SKIN))
    o.append(edge(face, 9, 13, 1.8, '#9a6a58'))
    # ear with a pearl
    o.append(shape([(-54, -6), (-70, -12), (-76, 10), (-68, 32), (-54, 28)], SKIN))
    o.append(brush([(-60, -2), (-68, 10), (-62, 24)], 2.2, SKIN_D, taper=(0.3, 0.3)))
    o.append(circle(-64, 38, 5, '#f6f2ea'))
    o.append(blush(-18, 42, 15 * cheek, CHEEK, 0.45))
    # eyes: heavy lids, a tired line under each
    o.append(eye(-10, 8, 1.4, e['eye'], side=-1))
    o.append(eye(42, 6, 1.3, e['eye'], side=1, squash=0.65))
    o.append(brush([(-24, 20), (-12, 24), (0, 21)], 1.6, SKIN_D, taper=(0.4, 0.4)))
    o.append(brush([(34, 18), (44, 21), (50, 18)], 1.4, SKIN_D, taper=(0.4, 0.4)))
    o.append(brow(-10, -16, 1.25, side=-1, inner=bi, outer=bo, w=2.6, length=1.1))
    o.append(brow(44, -18, 1.25, side=1, inner=bi, outer=bo, w=2.6, squash=0.6))
    # the long straight nose; its tip breaks the far cheek
    o.append(shape([(58, 4), (68, 24), (78, 42), (72, 48), (62, 48)], SKIN))
    o.append(brush([(50, -6), (64, 22), (77, 42), (70, 48), (60, 47)], 2.4, '#a8705a', taper=(0.6, 0.15)))
    o.append(mouth(30, 72, 1.3 * e.get('ms', 1), e['mouth'], side=1, width=0.75, color='#a42f30'))
    # cat-eye glasses
    o.append(_lens(-10, 8, -1))
    o.append(_lens(42, 6, 1, 0.65))
    o.append(brush([(3, 2), (18, -2), (34, 2)], 2.6, FRAME, taper=(0.1, 0.1)))
    o.append(brush([(-25, -2), (-58, -8)], 2.6, FRAME, taper=(0.1, 0.4)))
    # hair pulled back hard, a grey streak from the temple
    o.append(shape([(-58, -6, 'c'), (-66, -60), (-48, -106), (-4, -128), (44, -118), (70, -84), (74, -50, 'c'), (56, -70),
                    (24, -82), (-8, -78), (-38, -62), (-54, -36)], HAIR))
    o.append(dryb([[(-50, -50), (-30, -96), (10, -116)], [(-24, -70), (10, -104), (50, -104)]], 2.4, HAIR_L, 0.8))
    o.append(brush([(64, -66), (36, -84), (0, -96), (-32, -94)], 7, GREY, taper=(0.2, 0.5)))
    return o


def bust(view='34'):
    o = []
    body = [(-140, 300), (-136, 220), (-110, 176), (-46, 150), (42, 154), (106, 174), (132, 216), (140, 300)]
    o.append(shape(body, SUIT))
    o.append(shape([(-26, 150), (30, 154), (34, 240), (0, 280), (-28, 240)], BLOUSE))
    # lapels
    o.append(shape([(-46, 150), (-26, 150), (-10, 232), (-2, 290), (-30, 300), (-64, 210), (-74, 196, 'c'), (-50, 186, 'c')],
                   SUIT_D))
    o.append(shape([(42, 154), (30, 154), (16, 232), (8, 290), (34, 300), (66, 210), (76, 198, 'c'), (54, 188, 'c')], SUIT_D))
    # soft bow at the neck
    o.append(shape([(2, 160), (-28, 150, 'c'), (-24, 176, 'c')], BLOUSE_D))
    o.append(shape([(4, 160), (34, 152, 'c'), (30, 178, 'c')], BLOUSE_D))
    o.append(ell(3, 162, 6, 5, BLOUSE))
    o.append(circle(-80, 230, 7, GOLD))
    o.append(circle(-80, 230, 3.5, '#b8352b'))
    return o


def figure(expr='calm'):
    """Full figure, feet at y=0, tall and straight (about 7½ heads); a stack of books against her hip."""
    o = []
    # legs, low pumps
    o.append(limb([(-14, -210), (-14, -120), (-12, -24)], [22, 18, 10], SKIN))
    o.append(limb([(14, -210), (16, -120), (20, -24)], [22, 18, 10], SKIN))
    o.append(shape([(-28, -2, 'c'), (-24, -24), (-6, -28), (-2, -6, 'c')], '#2c2630'))
    o.append(shape([(10, -2, 'c'), (12, -26), (28, -26), (40, -4, 'c')], '#2c2630'))
    up = len(o)
    # pencil skirt and fitted jacket with a peplum
    o.append(shape([(-34, -480), (32, -480), (42, -420), (36, -320), (26, -236, 'c'), (-28, -236, 'c'), (-38, -320), (-44, -420)], SUIT))
    o.append(brush([(8, -320), (8, -240)], 2.2, SUIT_D, taper=(0.3, 0)))
    o.append(shape([(-42, -620), (40, -622), (48, -566), (28, -500, 'c'), (52, -438), (0, -446), (-54, -436), (-30, -500, 'c'), (-50, -566)], SUIT))
    o.append(shape([(-14, -624), (14, -624), (6, -560), (0, -540), (-6, -560)], BLOUSE))
    o.append(shape([(-20, -624), (-6, -560), (-24, -520), (-36, -580)], SUIT_D))
    o.append(shape([(20, -624), (6, -560), (24, -520), (36, -580)], SUIT_D))
    o.append(shape([(0, -618), (-16, -626, 'c'), (-14, -606, 'c')], BLOUSE_D))
    o.append(shape([(0, -618), (16, -626, 'c'), (14, -606, 'c')], BLOUSE_D))
    o.append(brush([(-30, -500), (28, -500)], 3, SUIT_D, taper=(0, 0)))
    for y in (-540, -515):
        o.append(circle(0, y, 3.5, GOLD))
    # near arm straight down, far arm holding books against the hip
    o.append(limb([(-46, -612), (-60, -548), (-50, -470), (-42, -446)], [26, 22, 19, 17], SUIT))
    o.append(ell(-40, -434, 8, 11, SKIN, rot=-15))
    for i, c in enumerate(('#2f6f8f', '#c7a24a', '#b8352b', '#3d6b4a')):
        o.append(shape([(30, -470 + i * 22, 'c'), (100, -476 + i * 22, 'c'), (102, -456 + i * 22, 'c'), (32, -450 + i * 22, 'c')], c))
        o.append(brush([(36, -462 + i * 22), (96, -467 + i * 22)], 1.6, '#f6f0e4', taper=(0, 0), opacity=0.7))
    o.append(limb([(44, -612), (62, -540), (70, -470), (60, -450)], [26, 22, 18, 16], SUIT))
    o.append(ell(58, -444, 10, 9, SKIN))
    # neck and head, chin up a little
    o.append(shape([(-8, -650), (12, -646), (12, -620), (-10, -620)], SKIN_D))
    o.append('<g transform="translate(0,-696) rotate(-3) scale(0.5)">' + ''.join(head('34', expr, neck=False)) + '</g>')
    # everything from the skirt up sits 50 lower than drawn: the legs are a little shorter than a fashion plate's
    return o[:up] + ['<g transform="translate(0,50)">'] + o[up:] + ['</g>']
