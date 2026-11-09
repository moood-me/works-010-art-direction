"""Марат, about 35, a cook — huge, loud, merry, generous. The biggest of the cast. Black hair and beard of rolled
paper curls, a wide laugh with teeth and tongue, a white jacket with rolled sleeves, a terracotta apron, a towel
over the shoulder, a ladle raised like a toast."""
from kit import *
import face as F
import body as B

HAIR, SKIN = '#2a2125', '#e0a87c'
WHITE, TERRA, TROU = '#f6efe0', '#c9623a', '#4a4850'
SPEC = dict(skin=SKIN, rx=92, ry=98, jaw=0.93, chin=0.0, eye_y=4, eye_gap=37, eye_w=14, eye_h=10.5,
            iris='#3b2a22', brow=HAIR, brow_w=11, brow_len=38, brow_y=-22,
            nose='broad', nose_y=34, nose_s=1.25, mouth_y=66, mouth_w=34, lip='#a8483c', inside='#4a151c',
            cheek='#e86a50', cheek_r=21, cheek_op=0.42, ear=1.2, neck_w=44,
            rest=dict(open=0.82, low=0.5, brow=0.12, brow_dy=-5, mouth='grin'),
            on=dict(joy=dict(mouth='laugh', open=0.0, brow_dy=-9), sad=dict(mouth='frown'), surprise=dict(mouth='o')))

CURLS_TOP = [(-92, -44, 14), (-78, -78, 15), (-52, -100, 15), (-20, -112, 16), (14, -113, 15), (46, -103, 16), (74, -82, 15), (92, -48, 14),
             (-62, -66, 13), (-34, -82, 14), (-2, -88, 13), (30, -84, 14), (58, -68, 13)]
CURLS_BEARD = [(-84, 86, 11), (-62, 110, 12), (-34, 126, 12), (-4, 133, 13), (26, 128, 12), (56, 114, 12), (80, 90, 11)]


def front_pieces():
    cap = [paint([(-94, -8, 1), (-98, -56), (-64, -100), (0, -112), (64, -100), (98, -56), (94, -8, 1), (84, -40), (56, -62), (20, -70), (-20, -70), (-56, -62), (-84, -40)], HAIR, 2, var=2)]
    curls = [B.curl(x, y, r, HAIR if i % 3 else lite(HAIR, 0.08), 2) for i, (x, y, r) in enumerate(CURLS_TOP)]
    beard = [paint([(-93, 4, 1), (-74, 30), (-48, 44), (-22, 40), (0, 46), (22, 40), (48, 44), (74, 30), (93, 4, 1), (99, 50), (86, 98),
                    (46, 126), (0, 134), (-46, 126), (-86, 98), (-99, 50)], HAIR, 2, var=2)]
    bcurls = [B.curl(x, y, r, HAIR if i % 2 else lite(HAIR, 0.08), 1) for i, (x, y, r) in enumerate(CURLS_BEARD)]
    mous = [paint([(0, 50), (-22, 44), (-48, 54), (-60, 72), (-40, 68), (-18, 62), (0, 62)], lite(HAIR, 0.07), 2, var=1),
            paint([(0, 50), (22, 44), (48, 54), (60, 72), (40, 68), (18, 62), (0, 62)], lite(HAIR, 0.07), 2, var=1)]
    return cap, curls, beard, bcurls, mous


def head(yaw=0.5, expr=None, collar=None):
    f = F.face(SPEC, yaw, expr)
    sp = f['spec']
    if yaw < 0.75:
        cap, curls, beard, bcurls, mous = front_pieces()
        if yaw >= 0.25:
            cap, curls, beard, bcurls, mous = [F.turn(t, sp) for t in (cap, curls, beard, bcurls, mous)]
        back = []
    else:
        back = []
        cap = [paint([(64, -62, 1), (54, -96), (10, -112), (-50, -104), (-96, -62), (-110, -6), (-96, 40), (-62, 48, 1), (-42, 8), (-12, -30), (30, -54)], HAIR, 2, var=2)]
        curls = [B.curl(x, y, r, HAIR if i % 3 else lite(HAIR, 0.08), 2) for i, (x, y, r) in enumerate(
            [(56, -86, 13), (28, -106, 15), (-6, -114, 15), (-42, -108, 16), (-76, -88, 15), (-100, -56, 15), (-110, -18, 14), (-100, 20, 13),
             (20, -78, 13), (-14, -84, 14), (-48, -74, 14), (-78, -48, 14), (-84, -8, 13)])]
        beard = [paint([(-24, 6, 1), (4, 36), (36, 44), (62, 40), (80, 52), (80, 96), (54, 126), (10, 130), (-24, 106), (-36, 60)], HAIR, 2, var=2)]
        bcurls = [B.curl(x, y, r, HAIR if i % 2 else lite(HAIR, 0.08), 1) for i, (x, y, r) in enumerate([(-22, 100, 11), (2, 122, 12), (32, 130, 12), (60, 118, 12), (80, 92, 11)])]
        mous = [paint([(40, 48), (70, 44), (90, 58), (84, 72), (62, 64), (44, 62)], lite(HAIR, 0.07), 2, var=1)]
        f['on'] = F.ear(-26, 16, sp, -1, 1.1)
    return [back, F.neck(SPEC, yaw, 30), collar or [], f['ears'], f['skin'], f['on'], f['feats'], beard, bcurls, f['mouth'], mous, f['nose'], cap, curls]


def collar(yaw=0):
    dx = 0 if yaw < 0.25 else (5 if yaw < 0.75 else -8)
    return [card([(dx - 50, 96), (dx, 108), (dx + 50, 96), (dx + 56, 122), (dx, 136), (dx - 56, 122)], WHITE, 2)]


def shoulders(yaw=0):
    k, dx = (1.0, 0) if yaw < 0.25 else ((0.92, 6) if yaw < 0.75 else (0.66, -10))
    j = [(dx - 56, 116), (dx + 56, 116), (dx + 126 * k, 138), (dx + 168 * k, 190), (dx + 176 * k, 270, 1), (dx - 176 * k, 270, 1), (dx - 168 * k, 190), (dx - 126 * k, 138)]
    out = [card(j, WHITE, 1), shade(j, (dx + 150 * k, 200), (dx + 60 * k, 200), 0.10)]
    out += [card([(dx - 20, 122, 1), (dx + 70 * k, 126), (dx + 86 * k, 270, 1), (dx - 44 * k, 270, 1)], lite(WHITE, 0.5), 1)]
    for i in range(2):
        out += [card(ell(dx - 20 * k, 176 + i * 50, 7, 7, n=8), TERRA, 1), card(ell(dx + 50 * k, 180 + i * 50, 7, 7, n=8), TERRA, 1)]
    # the towel over his left shoulder
    out += towel(dx + 104 * k, 128, 1.25)
    return out


def towel(x, y, s=1.0):
    t = [card([(-20, -8), (16, -10), (22, 40), (20, 120, 1), (-20, 124, 1), (-24, 40)], '#fbf6ea', 2)]
    t += [card(strip([(-22, 84), (21, 81)], 7), TERRA, 1), card(strip([(-21, 100), (21, 97)], 3.5), TERRA, 1)]
    t += [shade(t[0].pts, (-22, 60), (-4, 60), 0.14)]
    return move(scale(t, s), x, y)


def bust(yaw=0, expr=None):
    return [shoulders(yaw), head(yaw, expr, collar(yaw))]


def ladle(x, y, ang, s=1.0):
    """The handle runs from (0, 0) up to the bowl."""
    p = [card(strip([(0, 30), (0, -110)], 9), '#9aa4aa', 1),
         card(ell(0, -132, 30, 26, n=12), '#7f8a91', 2), flat(ell(-2, -136, 21, 16, n=10), '#b9c3c8'),
         flat(ell(-8, -140, 7, 4, rot=-20, n=8), '#e9eff1')]
    return move(rot(scale(p, s), ang), x, y)


def figure(expr='joy', yaw=0.5):
    """Feet wide, belly forward, head thrown back in a laugh; one fist on the hip, the ladle raised. Feet at y = 0."""
    hs = 0.66
    o = []
    o += B.ground_shadow(0, 150)
    o += B.limb([(-44, -250), (-52, -120), (-58, -16)], [56, 48, 40], TROU, 1, 'paint', 0, joints=False)
    o += B.limb([(44, -250), (54, -120), (62, -16)], [56, 48, 40], TROU, 1, 'paint', 0, joints=False)
    o += B.shoe(-34, 0, -1, 66, '#3a2c28', '#2a2020', 26) + B.shoe(38, 0, 1, 66, '#3a2c28', '#2a2020', 26)
    up = []                                                    # everything above the hips leans back a little
    # the far arm: fist on the hip
    up += B.limb([(112, -486), (182, -404)], [56, 50], WHITE, 1)
    j = [(-72, -528), (72, -528), (122, -486), (136, -400), (126, -312, 1), (-126, -312, 1), (-136, -400), (-122, -486)]
    up += [card(j, WHITE, 1), shade(j, (130, -400), (40, -400), 0.12)]
    up += [card([(-18, -522, 1), (64, -520), (86, -312, 1), (-44, -312, 1)], lite(WHITE, 0.5), 1)]
    for i in range(3):
        up += [card(ell(-22, -470 + i * 50, 6.5, 6.5, n=8), TERRA, 1), card(ell(52 + i * 5, -468 + i * 50, 6.5, 6.5, n=8), TERRA, 1)]
    o2 = []
    # the apron: tied at the waist, long, with folds
    ap = [(-104, -340, 1), (104, -340, 1), (112, -200), (104, -84, 1), (-104, -84, 1), (-112, -200)]
    o2 += [paint(ap, TERRA, 2, var=2)]
    o2 += B.folds(ap, [((-40, -200), (-18, -202)), ((36, -200), (60, -204))], 0.22)
    o2 += [light(ap, (-42, -200), (-60, -198), 0.2), light(ap, (34, -200), (16, -198), 0.2)]
    o2 += [card(strip([(-122, -330), (0, -322), (122, -330)], 15), dark(TERRA, 0.2), 1)]
    o2 += [card([(-112, -326, 1), (-142, -300), (-134, -290), (-112, -316, 1)], dark(TERRA, 0.2), 1),
           card([(-112, -326, 1), (-134, -350), (-142, -338), (-114, -318, 1)], dark(TERRA, 0.2), 1)]
    up2 = []
    up2 += B.limb([(182, -404), (118, -338)], [46, 38], SKIN, 2, joints=False)
    up2 += [card(ell(182, -404, 30, 28, n=10), WHITE, 2)]                              # the rolled sleeve
    up2 += B.brad(182, -404, 3.6)
    up2 += B.fist(122, -342, 120, 2.0, SKIN, 2)
    up2 += towel(84, -534, 1.0)
    up2 += move(rot(scale(head(yaw, expr, collar(yaw)), hs), -6), 0, -596)
    # the near arm raised with the ladle
    up2 += B.limb([(-112, -486), (-190, -470)], [56, 50], WHITE, 2)
    up2 += ladle(-212, -590, -24, 1.0)
    up2 += B.limb([(-190, -470), (-208, -566)], [46, 38], SKIN, 2, joints=False)
    up2 += [card(ell(-190, -470, 30, 28, n=10), WHITE, 2)]
    up2 += B.brad(-190, -470, 3.6)
    up2 += B.fist(-207, -562, 172, 2.0, SKIN, 2)
    o += rot(up, -3, (0, -300)) + o2 + rot(up2, -3, (0, -300))
    return o
