"""Савелий Петрович, about 70, a watchmaker — grumpy outside, kind inside. A bald dome, hair, brows and a walrus
moustache torn from white paper, a loupe pushed up on the forehead, a green waistcoat, a pocket watch on a chain."""
from kit import *
import face as F
import body as B

WHITE, SKIN = '#f3eee2', '#edc2a4'
VEST, SHIRT, TROU, BOW = '#3f7355', '#f6efe0', '#6b5546', '#b8402f'
SPEC = dict(skin=SKIN, rx=84, ry=92, jaw=0.84, chin=0.0, eye_y=12, eye_gap=33, eye_w=11, eye_h=9.5,
            iris='#4f6679', brow=WHITE, brow_kind='torn', brow_w=12, brow_len=34, brow_y=-21,
            nose='broad', nose_y=40, nose_s=1.15, mouth_y=84, mouth_w=15, lip='#a8544c',
            cheek='#e8857a', cheek_r=17, cheek_op=0.4, ear=1.35, neck_w=30,
            rest=dict(open=0.66, tilt=-0.22, brow=-0.38, brow_dy=5, mouth='frown', low=0.3),
            on=dict(joy=dict(mouth='smile', open=0.0)))


def loupe(x, y, s=1.0):
    ring = card(ell(x, y, 17 * s, 14 * s, rot=-15, n=12), B.BRASS, 2, holes=[ell(x, y, 12 * s, 9.5 * s, rot=-15, n=10)[::-1]])
    return [flat(ell(x, y, 12 * s, 9.5 * s, rot=-15, n=10), '#2d3438'), tissue(ell(x - 3 * s, y - 2 * s, 5 * s, 3.5 * s, rot=-15, n=8), '#cfe6ee', 0.5), ring]


def head(yaw=0.5, expr=None, collar=None):
    wr = lambda x0, y0, x1, y1, b: flat(crescent(x0, y0, x1, y1, b, 2.4), mix(SKIN, '#b8705c', 0.45))
    if yaw < 0.25:
        ex = [wr(-34, -50, 30, -52, -4), wr(-24, -62, 22, -63, -3), wr(-58, 4, -50, 14, 2), wr(58, 4, 50, 14, -2)]
        f = F.face(SPEC, yaw, expr, extras=ex)
        back = [torn([(-70, -30), (-100, -22), (-108, 20), (-98, 52), (-74, 46)], WHITE, 1),
                torn([(70, -30), (100, -22), (108, 20), (98, 52), (74, 46)], WHITE, 1)]
        band = [card(strip([(-80, -44), (0, -60), (80, -44)], 9), '#3a3034', 1)]
        mou = [torn([(-4, 50), (-24, 46), (-48, 62), (-56, 84), (-34, 82), (-14, 72), (0, 66)], WHITE, 2),
               torn([(4, 50), (24, 46), (48, 62), (56, 84), (34, 82), (14, 72), (0, 66)], WHITE, 2)]
        top = loupe(34, -62)
    else:
        ex = [wr(-20, -50, 44, -52, -4), wr(-10, -62, 38, -63, -3), wr(-44, 4, -36, 14, 2)]
        f = F.face(SPEC, yaw, expr, extras=ex)
        back = [torn([(-50, -40), (-96, -30), (-112, 16), (-100, 56), (-66, 50), (-52, 10)], WHITE, 1)]
        band = [card(strip([(-80, -40), (10, -60), (74, -46)], 9), '#3a3034', 1)]
        s = f['place']['mouth_x']
        mou = [torn([(s - 2, 50), (s - 22, 46), (s - 48, 62), (s - 58, 84), (s - 36, 82), (s - 14, 72), (s, 66)], WHITE, 2),
               torn([(s + 4, 50), (s + 18, 46), (s + 36, 60), (s + 42, 80), (s + 26, 80), (s + 10, 72), (s, 66)], WHITE, 2)]
        top = loupe(48, -62, 0.95)
        f['on'] = F.ear(-52, 24, f['spec'], -1, 1.0) + [torn([(-58, -30), (-84, -20), (-90, 14), (-76, 40), (-62, 20)], WHITE, 1)]
        f['ears'] = []
    return [back, F.neck(SPEC, yaw, 34), collar or [], f['ears'], f['skin'], f['on'], f['extras'], band, f['feats'], f['mouth'], mou, f['nose'], top]


def shoulders(yaw=0):
    k, dx = (1.0, 0) if yaw < 0.25 else (0.9, 6)
    shirt = [card([(dx - 36, 112), (dx + 36, 112), (dx + 100 * k, 140), (dx + 132 * k, 190), (dx + 138 * k, 260, 1), (dx - 138 * k, 260, 1), (dx - 132 * k, 190), (dx - 100 * k, 140)], SHIRT, 1)]
    vl = [paint([(dx - 40, 118), (dx - 86 * k, 140), (dx - 96 * k, 260, 1), (dx - 8, 260, 1), (dx - 14, 200)], VEST, 2, var=2)]
    vr = [paint([(dx + 40, 118), (dx + 86 * k, 140), (dx + 96 * k, 260, 1), (dx + 8, 260, 1), (dx + 14, 200)], VEST, 2, var=2)]
    return [shirt, vl, vr]


def bowtie(yaw=0):
    dx = 0 if yaw < 0.25 else 6
    return [card([(dx, 126), (dx - 28, 110), (dx - 30, 142)], BOW, 2), card([(dx, 126), (dx + 28, 110), (dx + 30, 142)], BOW, 2),
            card(ell(dx, 126, 6, 7, n=8), dark(BOW, 0.15), 2)]


def bust(yaw=0, expr=None):
    return [shoulders(yaw), head(yaw, expr, bowtie(yaw))]


def watch(x, y, s=1.0):
    return move(scale([card(ell(0, 0, 15, 15, n=12), B.BRASS, 2), flat(ell(0, 0, 11, 11, n=12), '#fbf6ea'),
                       flat(strip([(0, 0), (0, -8)], 1.8), '#3a3034'), flat(strip([(0, 0), (5, 3)], 1.8), '#3a3034'),
                       card(ell(0, -18, 4, 4, n=6), B.BRASS, 1)], s), x, y)


def figure(expr=None, yaw=0.5):
    """Stooped a little, one hand behind the back, the other holds the watch up before the eyes. Feet at y = 0."""
    hs = 0.60
    o = []
    o += B.ground_shadow(0, 95)
    o += B.limb([(-24, -180), (-26, -90), (-28, -10)], [34, 30, 26], TROU, 1, 'paint', 0, joints=False)
    o += B.limb([(22, -180), (26, -90), (24, -10)], [34, 30, 26], TROU, 1, 'paint', 0, joints=False)
    o += B.shoe(-44, 0, 1, 46, '#3a2c28', '#2a2020') + B.shoe(6, 0, 1, 48, '#3a2c28', '#2a2020')
    # the arm behind the back: only the sleeve shows
    o += B.limb([(-40, -322), (-70, -268), (-50, -222)], [26, 23, 20], dark(SHIRT, 0.08), 1)
    # body: shirt, then the waistcoat in two panels over the belly
    body = [(-40, -340), (16, -346), (52, -322), (64, -250), (56, -176, 1), (-52, -176, 1), (-62, -250), (-56, -316)]
    o += [card(body, SHIRT, 1)]
    o += [paint([(-34, -338), (-58, -312), (-64, -250), (-56, -168), (-30, -158, 1), (4, -186, 1), (-4, -270)], VEST, 2, var=2),
          paint([(24, -340), (54, -318), (66, -250), (58, -168), (30, -158, 1), (4, -186, 1), (6, -270)], VEST, 2, var=2)]
    for i in range(3):
        o += B.brad(8, -256 + i * 26, 2.6)
    for i in range(7):                                         # the chain: paper confetti
        t = i / 6
        o += [card(ell(34 + 30 * t + 10 * t * (1 - t), -232 - 96 * t + 70 * t * (1 - t), 2.3, 2.3, n=6), B.BRASS, 1)]
    o += move(rot(scale(head(yaw, expr, bowtie(yaw)), hs), 9), 10, -412)
    # the near arm: sleeve rolled, hand with the watch
    o += B.limb([(48, -318), (86, -270), (74, -330)], [27, 24, 20], SHIRT, 2)
    o += watch(70, -356, 0.9)
    o += B.fist(74, -332, 172, 1.0, SKIN, 2)
    return o
