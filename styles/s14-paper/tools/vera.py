"""Вера, about 40 — strict, clever, tired. A long narrow face, dark hair drawn back into a rolled bun, thin
glasses cut as rings, a long coat, a plum scarf, a stack of papers."""
from kit import *
import face as F
import body as B

HAIR, SKIN = '#3a2c33', '#ebc7a8'
COAT, SCARF, FRAME = '#3d6c76', '#7a3558', '#8a2f3c'
SPEC = dict(skin=SKIN, rx=72, ry=100, jaw=0.56, chin=0.07, eye_y=8, eye_gap=31, eye_w=14, eye_h=9.5,
            iris='#4c5a66', lash=True, lid='#cfa59c', brow=HAIR, brow_w=5, brow_len=28, brow_y=-25,
            nose='long', nose_y=40, nose_s=0.78, mouth_y=67, mouth_w=16, lip='#9c4048',
            cheek='#d98888', cheek_r=14, cheek_op=0.24, neck_w=22,
            rest=dict(open=0.60, tilt=0.14, brow=0.06, brow_dy=-1, mouth='flat'),
            on=dict(joy=dict(mouth='smile', open=0.7, low=0.45, brow_dy=-4)))


def glasses(f, yaw):
    out = []
    eyes = f['place']['eyes']
    y = SPEC['eye_y'] + 1
    for (x, kx, side) in eyes:
        rx_, ry_ = 21 * kx, 16
        out.append(tissue(ell(x, y, rx_, ry_, n=12), '#d6ecf2', 0.22))
        out.append(card(ell(x, y, rx_, ry_, n=12), FRAME, 1, holes=[ell(x, y, rx_ - 3.2, ry_ - 3.2, n=12)[::-1]]))
    if len(eyes) == 2:
        (x0, k0, _), (x1, k1, _) = eyes
        out.append(card(crescent(x0 + 20 * k0, y - 2, x1 - 20 * k1, y - 2, -3, 3), FRAME, 1))
        out.append(card(strip([(x0 - 20, y - 2), (-SPEC['rx'] * (1.0 if yaw < 0.25 else 0.82), y - 6)], 3), FRAME, 1))
        if yaw < 0.25:
            out.append(card(strip([(x1 + 20, y - 2), (SPEC['rx'], y - 6)], 3), FRAME, 1))
    return out


def hair(yaw):
    if yaw < 0.25:
        back = B.curl(8, -112, 30, HAIR, 1) + [paint([(-74, -30), (-70, -84), (0, -108), (70, -84), (74, -30), (60, 20), (-60, 20)], dark(HAIR, 0.1), 1, var=1)]
        front = [paint([(-74, 14, 1), (-80, -44), (-52, -96), (0, -108), (52, -96), (80, -44), (74, 14, 1), (66, -30), (40, -64), (2, -78, 1), (-36, -64), (-64, -30)], HAIR, 2, var=1),
                 flat(crescent(8, -100, 62, -44, -10, 4), '#9a8f96')]
        return back, front
    back = B.curl(-58, -98, 30, HAIR, 1) + [paint([(-88, -20), (-80, -80), (-10, -108), (60, -90), (72, -40), (20, -20), (-60, 30)], dark(HAIR, 0.1), 1, var=1)]
    front = [paint([(-78, 4, 1), (-90, -30), (-74, -82), (-16, -110), (44, -98), (70, -60), (72, -24, 1), (58, -56), (30, -76, 1), (-8, -62), (-36, -36), (-48, -12), (-58, 6)], HAIR, 2, var=1),
             flat(crescent(30, -98, 66, -50, -8, 4), '#9a8f96')]
    return back, front


def head(yaw=0.5, expr=None, collar=None):
    f = F.face(SPEC, yaw, expr)
    back, front = hair(yaw)
    bags = [tissue(crescent(x - 12 * kx, SPEC['eye_y'] + 13, x + 12 * kx, SPEC['eye_y'] + 13, 4, 5), '#9a6f86', 0.3) for (x, kx, s) in f['place']['eyes']]
    f['extras'] = bags
    f['ears'] = [] if yaw >= 0.25 else f['ears']
    return [back, F.neck(SPEC, yaw, 44), collar or [], F.stack(f, front=front, top=glasses(f, yaw))]


def scarf(dx=0, s=1.0):
    return [paint([(dx - 40 * s, 104), (dx, 92), (dx + 40 * s, 104), (dx + 46 * s, 132), (dx, 146), (dx - 46 * s, 132)], SCARF, 2, var=0),
            paint([(dx + 6 * s, 132, 1), (dx + 34 * s, 130, 1), (dx + 40 * s, 220, 1), (dx + 28 * s, 214, 1), (dx + 22 * s, 224, 1), (dx + 10 * s, 216, 1)], SCARF, 2, var=3)]


def shoulders(yaw=0):
    k, dx = (1.0, 0) if yaw < 0.25 else (0.9, 5)
    coat = [paint([(dx - 30, 122), (dx + 30, 122), (dx + 84 * k, 142), (dx + 108 * k, 190), (dx + 112 * k, 262, 1), (dx - 112 * k, 262, 1), (dx - 108 * k, 190), (dx - 84 * k, 142)], COAT, 1, var=1)]
    lap = [paint([(dx - 30, 126), (dx - 60 * k, 150), (dx - 34 * k, 262, 1), (dx - 4, 262, 1)], dark(COAT, 0.12), 2, var=1),
           paint([(dx + 30, 126), (dx + 60 * k, 150), (dx + 34 * k, 262, 1), (dx + 4, 262, 1)], dark(COAT, 0.12), 2, var=1)]
    return [coat, lap]


def bust(yaw=0, expr=None):
    return [shoulders(yaw), head(yaw, expr, scarf(0 if yaw < 0.25 else 5))]


def papers(x, y, ang=0):
    p = []
    for i, c in enumerate(('#e8dcc0', '#fbf6ea', '#d9e3ea', '#fbf6ea')):
        p.append(rot(card([(-30, -40, 1), (30, -40, 1), (30, 40, 1), (-30, 40, 1)], c, 1), -8 + i * 5))
    for i in range(4):
        p.append(flat(strip([(-18, -22 + i * 11), (16 - (i % 2) * 10, -20 + i * 11)], 2.4), '#9aa3ad'))
    return move(rot(p, ang), x, y)


def figure(expr=None, yaw=0.5):
    """Tall and straight, weight on one hip, papers pressed to the chest, the free hand hanging. Feet at y = 0."""
    hs = 0.56
    o = []
    o += B.ground_shadow(0, 90)
    o += B.limb([(-16, -160), (-18, -80), (-20, -14)], [20, 17, 14], '#34323a', 1, joints=False)
    o += B.limb([(14, -160), (20, -80), (22, -14)], [20, 17, 14], '#34323a', 1, joints=False)
    o += B.shoe(-34, 0, 1, 40, '#2a2428', '#2a2428', 20) + B.shoe(8, 0, 1, 42, '#2a2428', '#2a2428', 20)
    # far arm hanging
    o += B.limb([(48, -440), (60, -366), (56, -296)], [24, 21, 18], COAT, 1, 'paint', 1)
    o += B.hand(56, -292, -6, 0.95, SKIN, spread=3, thumb=-1)
    coat = [(-36, -462), (36, -462), (52, -430), (50, -330), (60, -220), (70, -100, 1), (-62, -100, 1), (-54, -220), (-48, -330), (-52, -430)]
    o += [paint(coat, COAT, 1, var=1)]
    o += B.folds(coat, [((8, -200), (30, -204)), ((-30, -180), (-12, -182))], 0.24)
    o += [paint([(4, -330, 1), (16, -330, 1), (26, -100, 1), (2, -100, 1)], dark(COAT, 0.14), 1, var=1)]
    for i in range(3):
        o += [card(ell(-8, -310 + i * 44, 4.5, 4.5, n=8), dark(COAT, 0.4), 1)]
    o += move(rot(scale(head(yaw, expr, scarf(4)), hs), 4), 6, -516)
    # near arm bent, holding the papers to the chest
    o += papers(-14, -376, -6)
    o += B.limb([(-48, -440), (-66, -372), (-22, -350)], [24, 21, 18], COAT, 2, 'paint', 1)
    o += B.hand(-20, -350, -76, 0.95, SKIN, spread=5, thumb=1, lift=1)
    return o
