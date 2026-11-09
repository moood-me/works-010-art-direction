"""Кира, about 15 — prickly, closed, defiant; vulnerable underneath. Thin and angular, a slouch, a look from under
the fringe. Choppy dark hair cut in sharp points, the fringe standing off the face and throwing a shadow over one
eye, an oversized plum hoodie, lime headphones round the neck, heavy boots with lime laces."""
from kit import *
import face as F
import body as B

HAIR, SKIN = '#2b2330', '#ecd3bf'
HOOD, TROU, LIME = '#5b2f57', '#37343c', '#c9e32f'
SPEC = dict(skin=SKIN, rx=70, ry=98, jaw=0.56, chin=0.09, eye_y=12, eye_gap=31, eye_w=13, eye_h=10,
            iris='#6d6688', lid='#8a6680', brow=HAIR, brow_w=6.5, brow_len=27, brow_y=-22,
            nose='wedge', nose_y=40, nose_s=0.85, mouth_y=66, mouth_w=15, lip='#a9566a',
            cheek='#dc8a9c', cheek_r=13, cheek_op=0.22, neck_w=19,
            rest=dict(open=0.56, tilt=-0.12, brow=-0.22, brow_dy=4, mouth='flat', look=0.9),
            on=dict(joy=dict(mouth='smirk', open=0.66, low=0.25, brow=-0.05, brow_dy=0, look=0.6),   # she never smiles openly
                    surprise=dict(mouth='pout', open=1.0, eye=1.1), sad=dict(look_y=0.8), angry=dict(mouth='frown')))


def front_pieces():
    back = [paint([(-82, 30), (-80, -30), (-68, -86), (0, -110), (68, -86), (80, -30), (82, 30), (74, 60, 1), (64, 36, 1), (54, 58, 1), (40, 30, 1),
                   (-40, 30, 1), (-54, 58, 1), (-64, 36, 1), (-74, 60, 1)], dark(HAIR, 0.15), 1, var=1)]
    side = [paint([(34, -98), (68, -76), (82, -24), (79, 26, 1), (68, -4, 1), (64, 16, 1), (54, -40)], HAIR, 2, var=1)]
    fringe = [paint([(42, -96), (-28, -110), (-74, -82), (-88, -30), (-85, 14), (-78, 40, 1), (-66, 8, 1), (-55, 34, 1), (-43, 2, 1), (-30, 20, 1),
                     (-16, -12, 1), (4, -38), (26, -66)], HAIR, 3, var=1)]
    return back, side, fringe


def head(yaw=0.5, expr=None, collar=None):
    f = F.face(SPEC, yaw, expr)
    sp = f['spec']
    if yaw < 0.75:
        back, side, fringe = front_pieces()
        if yaw >= 0.25:
            back, side, fringe = [F.turn(t, sp) for t in (back, side, fringe)]
            side = []
    else:
        back = []
        side = []
        fringe = [paint([(72, -36, 1), (62, -84), (20, -110), (-40, -106), (-88, -70), (-106, -10), (-98, 40), (-86, 68, 1), (-76, 42, 1), (-64, 64, 1),
                         (-52, 34, 1), (-34, 40, 1), (-24, 6, 1), (-4, 14, 1), (6, -18, 1), (24, -2, 1), (34, -34, 1), (54, -20, 1)], HAIR, 3, var=1)]
        f['on'] = []
    return [back, F.neck(SPEC, yaw, 44), collar or [], F.stack(f, mid=side, front=fringe)]


def phones(dx=0, s=1.0):
    """Headphones hanging round the neck: the band behind, two cups in front."""
    cup = lambda x: [card([(x - 13, 112), (x + 13, 112), (x + 15, 150), (x - 15, 150)], LIME, 2), card(ell(x, 132, 8, 12, n=8), '#2a2428', 1)]
    p = [card(crescent(dx - 36 * s, 122, dx + 36 * s, 122, -26, 9), dark(LIME, 0.25), 1)] + cup(dx - 37 * s) + cup(dx + 37 * s)
    return p


def shoulders(yaw=0):
    k, dx = (1.0, 0) if yaw < 0.25 else ((0.9, 4) if yaw < 0.75 else (0.62, -10))
    hood = [paint([(dx - 60 * k, 150), (dx - 52 * k, 104), (dx, 88), (dx + 52 * k, 104), (dx + 60 * k, 150)], dark(HOOD, 0.2), 1, var=1)]
    body = [paint([(dx - 30, 124), (dx + 30, 124), (dx + 74 * k, 138), (dx + 98 * k, 180), (dx + 104 * k, 262, 1), (dx - 104 * k, 262, 1), (dx - 98 * k, 180), (dx - 74 * k, 138)], HOOD, 1, var=1)]
    strings = [card(strip([(dx - 12, 150), (dx - 15, 214)], 4), lite(HOOD, 0.55), 1), card(strip([(dx + 12, 150), (dx + 13, 200)], 4), lite(HOOD, 0.55), 1)]
    return [hood, body, strings]


def bust(yaw=0, expr=None):
    dx = 0 if yaw < 0.25 else (4 if yaw < 0.75 else -10)
    return [shoulders(yaw), head(yaw, expr, phones(dx, 1.0 if yaw < 0.75 else 0.6))]


def figure(expr=None, yaw=0.5):
    """A slouch: hips forward, shoulders rounded, head pushed forward and down, one hand in the pocket, the other
    lost in a sleeve too long. One toe turned in. Feet at y = 0."""
    hs = 0.56
    o = []
    o += B.ground_shadow(0, 86)
    o += B.limb([(-2, -250), (-22, -132), (-30, -22)], [21, 18, 15], TROU, 1, joints=False)
    o += B.limb([(22, -250), (34, -132), (22, -22)], [21, 18, 15], TROU, 1, joints=False)
    o += B.boot(-48, 0, 1, 48, '#2d2a31', '#1e1b20', lace=LIME) + B.boot(42, 0, -1, 48, '#2d2a31', '#1e1b20', lace=LIME)
    # far arm into the pocket
    o += B.limb([(52, -418), (74, -338), (42, -286)], [27, 25, 23], dark(HOOD, 0.1), 1, 'paint', 1)
    # the hood lying on the back, then the hoodie body
    o += [paint([(-52, -410), (-40, -456), (10, -470), (48, -448), (56, -410)], dark(HOOD, 0.2), 1, var=1)]
    hd = [(-44, -436), (30, -440), (60, -412), (72, -320), (70, -236, 1), (-52, -226, 1), (-64, -320), (-62, -404)]
    o += [paint(hd, HOOD, 1, var=1)]
    o += B.folds(hd, [((-30, -300), (-10, -304)), ((40, -330), (58, -332))], 0.2)
    o += [paint(strip([(-52, -234), (10, -238), (70, -244)], 16), dark(HOOD, 0.18), 1, var=1)]
    o += [paint([(-26, -312, 1), (50, -318, 1), (62, -262, 1), (-38, -254, 1)], dark(HOOD, 0.12), 1, var=1)]
    o += [card(strip([(4, -420), (0, -356)], 3.5), lite(HOOD, 0.55), 1), card(strip([(24, -420), (26, -370)], 3.5), lite(HOOD, 0.55), 1)]
    o += move(rot(scale(head(yaw, expr, phones(4)), hs), 9), 22, -486)
    # near arm hanging, fingers only out of the sleeve
    o += B.hand(-72, -262, 6, 0.9, SKIN, spread=3, thumb=0)
    o += B.limb([(-54, -410), (-82, -334), (-72, -252)], [27, 25, 24], HOOD, 2, 'paint', 1)
    return o
