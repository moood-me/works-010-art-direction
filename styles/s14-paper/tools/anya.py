"""Аня, about 20 — warm, trusting, dreamy. Auburn hair with a curled lock, a mustard cardigan, a cornflower dress,
a folded paper bird on her hand."""
from kit import *
import face as F
import body as B

HAIR, HAIR_D = '#a9502c', '#8c3d20'
DRESS, CARD_, SKIN = '#6c9bc4', '#e0ae38', '#f2cba7'
SPEC = dict(skin=SKIN, rx=78, ry=98, jaw=0.60, chin=0.04, eye_y=14, eye_gap=35, eye_w=16.5, eye_h=15,
            iris='#5c8259', lash=True, brow=HAIR_D, brow_w=5.5, brow_len=30, brow_y=-31,
            nose='button', nose_y=42, nose_s=0.8, mouth_y=64, mouth_w=19, lip='#c4524e',
            cheek='#ee7f8c', cheek_r=18, neck_w=24,
            rest=dict(open=0.74, tilt=0.12, brow=0.12, mouth='smile'),
            on=dict(joy=dict(mouth='grin', open=0.0)))


def hair(yaw):
    """→ (behind the head, over the forehead)"""
    if yaw < 0.25:
        back = [paint([(-66, -94), (0, -116), (66, -94), (92, -40), (94, 40), (106, 104), (100, 156, 1), (82, 138), (62, 160, 1),
                       (40, 130), (-40, 130), (-62, 160, 1), (-82, 138), (-100, 156, 1), (-106, 104), (-94, 40), (-92, -40)], HAIR_D, 1, var=1)]
        front = [paint([(-88, 10, 1), (-93, -48), (-62, -100), (0, -114), (62, -100), (93, -48), (88, 10, 1), (76, -34),
                        (52, -66), (22, -80, 1), (-12, -58), (-48, -40), (-72, -22)], HAIR, 2, var=1)]
        front += [paint([(80, -6), (96, 44), (90, 104), (102, 148), (90, 154), (74, 106), (80, 50), (72, 0)], HAIR, 2, var=1)]
        front += B.curl(97, 160, 13, HAIR, 2)
        return back, front
    if yaw < 0.75:
        back = [paint([(-60, -96), (8, -116), (66, -92), (84, -40), (70, 0), (20, 60), (-6, 126), (-20, 160, 1), (-44, 140),
                       (-66, 166, 1), (-90, 144), (-112, 160, 1), (-122, 104), (-108, 40), (-104, -30)], HAIR_D, 1, var=1)]
        front = [paint([(-80, 30, 1), (-98, -20), (-84, -74), (-36, -110), (26, -112), (68, -86), (80, -44), (76, -8, 1),
                        (62, -52), (38, -76, 1), (6, -54), (-28, -36), (-50, -8), (-58, 30)], HAIR, 2, var=1)]
        front += [paint([(-66, 16), (-86, 30), (-96, 90), (-84, 140), (-92, 166), (-80, 168), (-68, 130), (-78, 80)], HAIR, 2, var=1)]
        front += B.curl(-86, 174, 13, HAIR, 2)
        return back, front
    back = [paint([(-20, -104), (-70, -96), (-108, -40), (-116, 30), (-128, 110), (-112, 166), (-60, 170), (-36, 120),
                   (-30, 60), (-10, 20), (20, -60)], HAIR_D, 1, var=1)]
    front = [paint([(58, -62, 1), (50, -92), (10, -112), (-50, -106), (-94, -66), (-108, -10), (-104, 60), (-112, 120),
                    (-92, 150), (-70, 120), (-62, 60), (-40, 30), (-18, 28, 1), (-10, -10), (14, -44), (36, -58)], HAIR, 2, var=1)]
    front += B.curl(-96, 156, 13, HAIR, 2)
    return back, front


def head(yaw=0.5, expr=None, collar=None):
    f = F.face(SPEC, yaw, expr)
    back, front = hair(yaw)
    return [back, F.neck(SPEC, yaw), collar or [], F.stack(f, front=front)]


def bird(x, y, s=1.0, col='#fbf6ea'):
    """A folded paper bird: three facets of one sheet."""
    b = [card([(-22, 4, 1), (0, -4, 1), (4, 10, 1)], dark(col, 0.12), 1),
         card([(0, -4, 1), (26, -14, 1), (14, 2, 1), (4, 10, 1)], col, 1),
         card([(-2, -3, 1), (8, -26, 1), (12, 0, 1)], lite(col, 0.3), 2),
         card([(24, -13, 1), (34, -9, 1), (25, -8, 1)], '#e0ae38', 1)]
    return move(scale(b, s), x, y)


def shoulders(yaw=0):
    """Head-and-shoulders: what is under the neck."""
    k = 1.0 if yaw < 0.25 else (0.9 if yaw < 0.75 else 0.62)
    dx = 0 if yaw < 0.25 else (4 if yaw < 0.75 else -10)
    dress = [paint([(dx - 30, 118, 1), (dx + 30, 118, 1), (dx + 60 * k, 150), (dx + 70 * k, 260, 1), (dx - 70 * k, 260, 1), (dx - 60 * k, 150)], DRESS, 1, var=0)]
    cl = [paint([(dx - 34, 122), (dx - 84 * k, 140), (dx - 114 * k, 190), (dx - 122 * k, 260, 1), (dx - 30 * k, 260, 1), (dx - 40 * k, 180)], CARD_, 2, var=1)]
    cr = [paint([(dx + 34, 122), (dx + 84 * k, 140), (dx + 114 * k, 190), (dx + 122 * k, 260, 1), (dx + 30 * k, 260, 1), (dx + 40 * k, 180)], CARD_, 2, var=1)]
    if yaw >= 0.75:
        cl = [paint([(dx - 30, 120), (dx - 80, 150), (dx - 96, 260, 1), (dx + 60, 260, 1), (dx + 40, 160), (dx + 26, 122)], CARD_, 2, var=1)]
        cr = []
    return [dress, cl, cr]


def collar(yaw=0):
    dx = 0 if yaw < 0.25 else (4 if yaw < 0.75 else -10)
    if yaw >= 0.75:
        return [card([(dx - 26, 112), (dx + 30, 118), (dx + 34, 134), (dx - 30, 130)], '#fbf6ea', 1)]
    return [card([(dx - 28, 112), (dx, 132), (dx + 28, 112), (dx + 38, 130), (dx, 154), (dx - 38, 130)], '#fbf6ea', 1)]


def bust(yaw=0, expr=None):
    return [shoulders(yaw), head(yaw, expr, collar(yaw))]


def figure(expr=None, yaw=0.5):
    """Standing, weight on one leg, head tilted to the paper bird on her raised hand. Feet at y = 0."""
    hs = 0.60
    hc = (6, -462)
    o = []
    o += B.ground_shadow(0, 90)
    # legs and shoes
    o += B.limb([(-18, -190), (-22, -100), (-26, -12)], [20, 17, 13], SKIN, 1, joints=False)
    o += B.limb([(16, -190), (24, -100), (20, -12)], [20, 17, 13], SKIN, 1, joints=False)
    o += B.shoe(-34, 0, 1, 40, '#9c3b34') + B.shoe(10, 0, 1, 42, '#9c3b34')
    # the far arm (her left), down, holding the skirt
    o += B.limb([(46, -384), (62, -320), (58, -262)], [22, 19, 16], CARD_, 1, 'paint', 1)
    o += B.hand(58, -258, -8, 0.95, SKIN, spread=4, thumb=-1)
    # the dress: bodice and a skirt with three folds, a scalloped hem
    skirt = [(-40, -300, 1), (40, -300, 1), (62, -230), (86, -150, 1)]
    for i in range(7):
        skirt += [(86 - 24.5 * (i + 0.5), -138), (86 - 24.5 * (i + 1), -150, 1)]
    skirt += [(-62, -230)]
    o += [paint(skirt, DRESS, 1, var=0)]
    o += B.folds(skirt, [((-34, -200), (-18, -202)), ((8, -200), (26, -203)), ((46, -200), (62, -205))], 0.30)
    o += [light(skirt, (-36, -200), (-50, -197), 0.30), light(skirt, (6, -200), (-8, -198), 0.28), light(skirt, (44, -200), (30, -198), 0.25)]
    bod = [(-34, -400), (34, -400), (44, -350), (40, -296, 1), (-40, -296, 1), (-44, -350)]
    o += [paint(bod, DRESS, 1, var=0)]
    o += [card(strip([(-41, -300), (0, -297), (41, -300)], 9), '#fbf6ea', 1)]
    # cardigan panels
    o += [paint([(-26, -406), (-48, -396), (-54, -340), (-48, -272), (-30, -266, 1), (-16, -300), (-18, -360)], CARD_, 2, var=1),
          paint([(26, -406), (48, -396), (54, -340), (48, -272), (30, -266, 1), (16, -300), (18, -360)], CARD_, 2, var=1)]
    # head: turned to the bird and tilted towards it
    o += move(rot(scale(mirror(head(yaw, expr, collar(yaw))), hs), -8), -4, -462)
    # the near arm raised, the bird on the open hand
    o += B.limb([(-46, -384), (-74, -332), (-106, -384)], [22, 19, 16], CARD_, 2, 'paint', 1)
    o += B.hand(-108, -388, 150, 0.95, SKIN, spread=10, thumb=1, lift=1)
    o += bird(-128, -422, 0.9)
    return o
