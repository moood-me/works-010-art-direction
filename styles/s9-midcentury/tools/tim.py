"""Тим, about 8 — mischievous, curious. A Blair child: a big round head, features low and small, dot eyes,
a spiky ginger crop with a cowlick, freckles, ears that stick out, a striped shirt; a slingshot behind his back."""
from kit import edge, shape, brush, blush, ell, circle, dryb, limb, stripes, mix, INK
from face import eye, brow, mouth, EXPR

SKIN = '#f7d6bb'
SKIN_D = '#e8b096'
HAIR = '#d0642c'
HAIR_D = '#a8481c'
SHIRT = '#c8402f'
SHIRT_L = '#f6eedd'
SHORTS = '#2c4a6e'
SOCK = '#f6eedd'
SHOE = '#b8352b'
CHEEK = '#ee7a66'
FRECK = '#c97a52'
FIG_SCALE = 1.4  # how much larger the full figure is drawn on its own page
BUST_DY = -54

OWN = {
    'calm':     dict(eye='dot', brow=(0, 0), brow2=(4, -6), mouth='smirk'),
    'joy':      dict(eye='happy', brow=(-4, -2), mouth='grin', cheek=1.3, ms=1.45),
    'surprise': dict(eye='wide', brow=(-10, -8), mouth='o', ms=1.35),
    'sad':      dict(eye='sad', brow=(-7, 5), mouth='sad', ms=1.2),
    'anger':    dict(eye='glare', brow=(9, -6), mouth='shout', cheek=1.3, ms=1.45),
}


def _e(expr):
    e = dict(EXPR[expr])
    e.update(OWN.get(expr, {}))
    return e


def _freckles(pts):
    return ''.join(circle(x, y, 1.9, FRECK, 0.85) for x, y in pts)


def head(view='34', expr='calm', neck=True):
    """The head around (0, 0), crown near y=-120, chin near y=95; neck=False leaves the neck to the figure."""
    e = _e(expr)
    bi, bo = e['brow']
    b2i, b2o = e.get('brow2', e['brow'])
    cheek = e.get('cheek', 1.0)
    o = []
    if view == '34':
        if neck:
            o.append(shape([(-26, 60), (20, 70), (22, 140), (-28, 140)], SKIN_D))
        face = [(-62, -44), (-48, -88), (-8, -108), (40, -100), (68, -66), (78, -20), (76, 24), (62, 58), (34, 80),
                        (2, 86), (-32, 78), (-56, 52), (-68, 8)]
        o.append(shape(face, SKIN))
        o.append(edge(face, 8, 11, 1.8, '#b9806a'))
        o.append(ell(-70, 14, 15, 21, SKIN, rot=-10))
        o.append(brush([(-74, 2), (-80, 16), (-72, 30)], 2.4, SKIN_D, taper=(0.3, 0.3)))
        o.append(blush(-20, 40, 17 * cheek, CHEEK))
        o.append(blush(64, 38, 9 * cheek, CHEEK, 0.6))
        o.append(_freckles([(-30, 32), (-20, 28), (-10, 34), (-24, 40), (52, 30), (60, 34)]))
        o.append(eye(-6, 14, 1.45, e['eye'], side=-1, lash=False))
        o.append(eye(44, 12, 1.35, e['eye'], side=1, squash=0.72, lash=False))
        o.append(brow(-6, -10, 1.2, side=-1, inner=bi, outer=bo, w=3.2))
        o.append(brow(46, -12, 1.2, side=1, inner=b2i, outer=b2o, w=3.2, squash=0.6))
        o.append(ell(64, 32, 9, 8, SKIN))
        o.append(brush([(58, 38), (64, 41), (71, 37)], 2.2, SKIN_D, taper=(0.3, 0.3)))
        o.append(mouth(30, 58, 1.3 * e.get('ms', 1), e['mouth'], side=1, width=0.85))
        # spiky crop: a zigzag fringe and a cowlick
        o.append(shape([(-72, -24, 'c'), (-62, -48), (-46, -40, 'c'), (-34, -62), (-12, -46, 'c'), (4, -68), (30, -52, 'c'),
                        (46, -72), (70, -54, 'c'), (78, -78), (60, -106), (24, -122), (14, -146, 'c'), (2, -124),
                        (-34, -118), (-64, -98), (-78, -60)], HAIR))
        o.append(dryb([[(-50, -70), (-10, -104), (30, -110)], [(-20, -70), (20, -96), (60, -84)]], 2.6, HAIR_D, 0.7))
    elif view == 'front':
        if neck:
            o.append(shape([(-22, 60), (22, 60), (24, 140), (-24, 140)], SKIN_D))
        o.append(ell(-78, 12, 15, 21, SKIN, rot=-12))
        o.append(ell(78, 12, 15, 21, SKIN, rot=12))
        o.append(brush([(-82, 0), (-88, 14), (-80, 28)], 2.4, SKIN_D, taper=(0.3, 0.3)))
        o.append(brush([(82, 0), (88, 14), (80, 28)], 2.4, SKIN_D, taper=(0.3, 0.3)))
        o.append(shape([(0, -106), (46, -96), (72, -60), (78, -10), (72, 34), (52, 66), (24, 84), (0, 88), (-24, 84), (-52, 66),
                        (-72, 34), (-78, -10), (-72, -60), (-46, -96)], SKIN))
        o.append(blush(-40, 40, 16 * cheek, CHEEK))
        o.append(blush(40, 40, 16 * cheek, CHEEK))
        o.append(_freckles([(-48, 30), (-38, 26), (-28, 32), (-42, 38), (48, 30), (38, 26), (28, 32), (42, 38)]))
        o.append(eye(-24, 14, 1.45, e['eye'], side=-1, lash=False))
        o.append(eye(24, 14, 1.45, e['eye'], side=1, lash=False))
        o.append(brow(-25, -10, 1.2, side=-1, inner=bi, outer=bo, w=3.2))
        o.append(brow(25, -12, 1.2, side=1, inner=b2i, outer=b2o, w=3.2))
        o.append(ell(0, 34, 9, 8, SKIN))
        o.append(brush([(-6, 40), (0, 43), (6, 40)], 2.2, SKIN_D, taper=(0.3, 0.3)))
        o.append(mouth(2, 58, 1.3 * e.get('ms', 1), e['mouth'], side=1, width=0.85))
        o.append(shape([(-78, -26, 'c'), (-66, -50), (-48, -42, 'c'), (-34, -66), (-10, -48, 'c'), (6, -70), (30, -50, 'c'),
                        (46, -68), (66, -46, 'c'), (78, -28, 'c'), (80, -76), (54, -110), (16, -122), (10, -146, 'c'),
                        (-2, -122), (-46, -114), (-78, -84)], HAIR))
        o.append(dryb([[(-56, -70), (-16, -106), (30, -110)], [(-10, -74), (30, -100), (64, -76)]], 2.6, HAIR_D, 0.7))
    elif view == 'side':
        if neck:
            o.append(shape([(-20, 56), (24, 66), (22, 140), (-34, 140)], SKIN_D))
        o.append(shape([(-66, -30), (-56, -84), (-14, -110), (36, -104), (64, -72), (70, -30), (70, 10), (80, 30), (84, 40, 'c'),
                        (72, 46), (70, 58), (62, 72), (38, 86), (6, 86), (-24, 76), (-52, 50), (-68, 10)], SKIN))
        o.append(ell(-8, 14, 15, 21, SKIN, rot=-6))
        o.append(brush([(-12, 2), (-18, 16), (-10, 28)], 2.4, SKIN_D, taper=(0.3, 0.3)))
        o.append(blush(34, 40, 16 * cheek, CHEEK))
        o.append(_freckles([(28, 30), (38, 26), (46, 32), (36, 38)]))
        o.append(eye(52, 12, 1.45, e['eye'], side=1, squash=0.7, lash=False))
        o.append(brow(54, -12, 1.2, side=1, inner=b2i, outer=b2o, w=3.2, squash=0.6))
        o.append(mouth(64, 58, 1.3 * e.get('ms', 1), e['mouth'], side=1, width=0.5))
        o.append(shape([(-72, -20), (-74, -70), (-40, -110), (8, -124), (4, -146, 'c'), (20, -122), (50, -108), (70, -80),
                        (76, -62, 'c'), (62, -58), (54, -74), (48, -54, 'c'), (34, -72), (20, -50, 'c'), (6, -64), (-10, -36, 'c'),
                        (-30, -40), (-50, -16, 'c'), (-60, -30)], HAIR))
        o.append(dryb([[(-56, -60), (-16, -100), (30, -110)], [(-10, -64), (30, -96), (64, -76)]], 2.6, HAIR_D, 0.7))
    return o


def bust(view='34'):
    o = []
    if view == 'side':
        body = [(-90, 300), (-84, 190), (-50, 140), (30, 140), (70, 190), (80, 300)]
    else:
        body = [(-130, 300), (-124, 200), (-92, 160), (-30, 140), (30, 140), (92, 160), (124, 200), (130, 300)]
    o.append(shape(body, SHIRT))
    o.append(stripes(body, -140, 166, 140, 300, 30, 13, SHIRT_L, 'timst' + view))
    o.append(brush([(-30, 140), (0, 152), (30, 140)] if view != 'side' else [(-30, 140), (0, 150), (26, 140)], 7, SHIRT_L,
                   taper=(0.1, 0.1)))
    return o


def figure(expr='calm'):
    """Full figure, feet at y=0, about 3½ heads: leaning forward on his toes, hands — and a slingshot — behind his back."""
    o = []
    # legs: thin, knobbly knees, white socks, red sneakers; the back foot on its toes
    o.append(limb([(-16, -170), (-20, -100), (-18, -30)], [20, 16, 14], SKIN))
    o.append(limb([(18, -170), (12, -100), (-2, -40)], [20, 16, 14], SKIN))
    o.append(limb([(-19, -72), (-18, -22)], [17, 16], SOCK, cap=False))
    o.append(limb([(4, -64), (-3, -30)], [17, 16], SOCK, cap=False))
    o.append(brush([(-27, -66), (-10, -66)], 3, SHIRT, taper=(0, 0)))
    o.append(brush([(-4, -58), (13, -56)], 3, SHIRT, taper=(0, 0)))
    o.append(shape([(-28, -2, 'c'), (-28, -22), (-6, -26), (14, -12), (16, -2, 'c')], SHOE))
    o.append(brush([(-28, -4), (16, -4)], 4, SOCK, taper=(0, 0)))
    o.append(shape([(-20, -10, 'c'), (-14, -34), (6, -30), (8, -14)], SHOE))
    # shorts
    o.append(shape([(-34, -250), (34, -250), (42, -170), (8, -158), (0, -180), (-10, -158), (-40, -168)], SHORTS))
    # slingshot tucked behind his back, the fork showing above his hip
    o.append(brush([(-30, -268), (-48, -318)], 6, '#8a5a32', taper=(0, 0)))
    o.append(brush([(-48, -318), (-66, -346)], 5, '#8a5a32', taper=(0, 0.2)))
    o.append(brush([(-48, -318), (-40, -352)], 5, '#8a5a32', taper=(0, 0.2)))
    o.append(brush([(-66, -344), (-56, -330), (-40, -350)], 2, '#b8352b', taper=(0, 0)))
    # the far arm hides behind him: only the sleeve shows at the shoulder
    o.append(shape([(-8, -380), (14, -378), (16, -350), (-10, -350)], SKIN_D))
    o.append(limb([(30, -344), (36, -316)], [26, 22], SHIRT))
    # body leaning forward
    torso = [(-36, -246), (-42, -300), (-30, -350), (14, -360), (44, -330), (44, -280), (40, -246)]
    o.append(shape(torso, SHIRT))
    o.append(stripes(torso, -60, -340, 60, -240, 22, 10, SHIRT_L, 'timfig'))
    o.append(brush([(-14, -356), (6, -348), (22, -358)], 5, SHIRT_L, taper=(0.1, 0.1)))
    # the near arm swings back, the hand behind his back
    o.append(limb([(-26, -332), (-44, -298), (-34, -262)], [20, 16, 14], SKIN))
    o.append(limb([(-24, -342), (-38, -314)], [30, 26], SHIRT))
    o.append(brush([(-46, -320), (-30, -312)], 5, SHIRT_L, taper=(0, 0)))
    o.append(ell(-30, -258, 10, 10, SKIN))
    o.append('<g transform="translate(18,-410) rotate(10) scale(0.6)">' + ''.join(head('34', expr, neck=False)) + '</g>')
    return o
