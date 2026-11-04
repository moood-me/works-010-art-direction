"""Тим, about 8 — mischievous, curious. A Blair child: a big round head, features low and small, dot eyes,
a spiky ginger crop with a cowlick, freckles, ears that stick out, a striped shirt; a slingshot behind his back."""
from kit import shape, brush, blush, ell, circle, dryb, limb, stripes, mix, INK
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
BUST_DY = -40

OWN = {
    'calm':     dict(eye='dot', brow=(0, 0), brow2=(4, -6), mouth='smirk'),
    'joy':      dict(eye='happy', brow=(-4, -2), mouth='grin', cheek=1.3),
    'surprise': dict(eye='wide', brow=(-10, -8), mouth='o'),
    'sad':      dict(eye='sad', brow=(-4, 5), mouth='sad'),
    'anger':    dict(eye='lid', brow=(6, -4), mouth='shout'),
}


def _e(expr):
    e = dict(EXPR[expr])
    e.update(OWN.get(expr, {}))
    return e


def _freckles(pts):
    return ''.join(circle(x, y, 1.9, FRECK, 0.85) for x, y in pts)


def head(view='34', expr='calm'):
    e = _e(expr)
    bi, bo = e['brow']
    b2i, b2o = e.get('brow2', e['brow'])
    cheek = e.get('cheek', 1.0)
    o = []
    if view == '34':
        o.append(shape([(-34, 60), (24, 70), (26, 140), (-36, 140)], SKIN_D))
        o.append(shape([(-62, -44), (-48, -88), (-8, -108), (40, -100), (68, -66), (78, -20), (76, 24), (62, 58), (34, 80),
                        (2, 86), (-32, 78), (-56, 52), (-68, 8)], SKIN))
        o.append(ell(-70, 14, 15, 21, SKIN, rot=-10))
        o.append(brush([(-74, 2), (-80, 16), (-72, 30)], 2.4, SKIN_D, taper=(0.3, 0.3)))
        o.append(blush(-20, 40, 17 * cheek, CHEEK))
        o.append(blush(64, 38, 9 * cheek, CHEEK, 0.6))
        o.append(_freckles([(-30, 32), (-20, 28), (-10, 34), (-24, 40), (52, 30), (60, 34)]))
        o.append(eye(-6, 14, 1.45, e['eye'], side=-1, lash=False))
        o.append(eye(44, 12, 1.35, e['eye'], side=1, squash=0.72, lash=False))
        o.append(brow(-6, -10, 1.2, side=-1, inner=bi, outer=bo, w=3.2))
        o.append(brow(46, -12, 1.2, side=1, inner=b2i, outer=b2o, w=3.2, squash=0.6))
        o.append(ell(62, 34, 8, 7, SKIN_D))
        o.append(mouth(30, 58, 1.3, e['mouth'], side=1, width=0.85))
        # spiky crop: a zigzag fringe and a cowlick
        o.append(shape([(-70, -40, 'c'), (-56, -50), (-44, -44, 'c'), (-34, -64), (-20, -50, 'c'), (-6, -70), (10, -54, 'c'),
                        (24, -74), (38, -58, 'c'), (54, -76), (66, -60, 'c'), (78, -66, 'c'), (72, -94), (44, -116),
                        (14, -124), (6, -146, 'c'), (-4, -122), (-30, -118), (-60, -102), (-74, -70)], HAIR))
        o.append(dryb([[(-50, -70), (-10, -104), (30, -110)], [(-20, -70), (20, -96), (60, -84)]], 2.6, HAIR_D, 0.7))
    elif view == 'front':
        o.append(shape([(-28, 60), (28, 60), (30, 140), (-30, 140)], SKIN_D))
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
        o.append(ell(0, 36, 8, 7, SKIN_D))
        o.append(mouth(2, 58, 1.3, e['mouth'], side=1, width=0.85))
        o.append(shape([(-76, -40, 'c'), (-62, -52), (-50, -44, 'c'), (-38, -66), (-22, -50, 'c'), (-8, -72), (6, -54, 'c'),
                        (20, -72), (34, -52, 'c'), (48, -68), (60, -48, 'c'), (76, -42, 'c'), (78, -80), (50, -112), (14, -122),
                        (8, -146, 'c'), (-4, -122), (-46, -114), (-76, -84)], HAIR))
        o.append(dryb([[(-56, -70), (-16, -106), (30, -110)], [(-10, -74), (30, -100), (64, -76)]], 2.6, HAIR_D, 0.7))
    elif view == 'side':
        o.append(shape([(-20, 56), (24, 66), (22, 140), (-34, 140)], SKIN_D))
        o.append(shape([(-66, -30), (-56, -84), (-14, -110), (36, -104), (64, -72), (70, -30), (70, 10), (80, 30), (84, 40, 'c'),
                        (72, 46), (70, 58), (62, 72), (38, 86), (6, 86), (-24, 76), (-52, 50), (-68, 10)], SKIN))
        o.append(ell(-8, 14, 15, 21, SKIN, rot=-6))
        o.append(brush([(-12, 2), (-18, 16), (-10, 28)], 2.4, SKIN_D, taper=(0.3, 0.3)))
        o.append(blush(34, 40, 16 * cheek, CHEEK))
        o.append(_freckles([(28, 30), (38, 26), (46, 32), (36, 38)]))
        o.append(eye(52, 12, 1.45, e['eye'], side=1, squash=0.7, lash=False))
        o.append(brow(54, -12, 1.2, side=1, inner=b2i, outer=b2o, w=3.2, squash=0.6))
        o.append(mouth(64, 58, 1.3, e['mouth'], side=1, width=0.5))
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
    # slingshot sticking out from behind his back
    o.append(brush([(-60, -250), (-76, -290)], 5, '#8a5a32', taper=(0, 0)))
    o.append(brush([(-76, -290), (-92, -322)], 5, '#8a5a32', taper=(0, 0.2)))
    o.append(brush([(-76, -290), (-66, -326)], 5, '#8a5a32', taper=(0, 0.2)))
    o.append(brush([(-92, -320), (-80, -308), (-66, -324)], 2, '#b8352b', taper=(0, 0)))
    # body leaning forward, arms back
    o.append(limb([(-26, -330), (-48, -290), (-60, -250)], [24, 20, 17], SHIRT))
    torso = [(-36, -246), (-42, -300), (-30, -350), (14, -360), (44, -330), (44, -280), (40, -246)]
    o.append(shape(torso, SHIRT))
    o.append(stripes(torso, -60, -340, 60, -240, 22, 10, SHIRT_L, 'timfig'))
    o.append(limb([(30, -336), (6, -296), (-32, -262)], [24, 20, 17], SHIRT))
    o.append(stripes([(30, -350), (44, -320), (-20, -246), (-46, -270)], -60, -350, 60, -240, 22, 10, SHIRT_L, 'timarm'))
    o.append(ell(-50, -258, 10, 10, SKIN))
    o.append('<g transform="translate(22,-412) rotate(10) scale(0.6)">' + ''.join(head('34', expr)) + '</g>')
    return o
