"""Тим, about 8 — mischievous, curious. A big round head, straw hair snipped in zigzags, freckles of confetti,
a tee of glued stripes, shorts, a plaster on the knee, a paper plane about to fly."""
from kit import *
import face as F
import body as B

HAIR, SKIN = '#e29a30', '#f4cfa9'
TEE, STRIPE, SHORTS = '#c9412f', '#fbf6ea', '#3f5f97'
SPEC = dict(skin=SKIN, rx=86, ry=88, jaw=0.80, chin=0.0, eye_y=16, eye_gap=37, eye_w=15, eye_h=16,
            iris='#6a4a2c', brow='#b56a1e', brow_w=6, brow_len=26, brow_y=-32,
            nose='button', nose_y=42, nose_s=0.85, mouth_y=62, mouth_w=22, lip='#b8483f',
            cheek='#f0876c', cheek_r=18, cheek_op=0.38, ear=1.3, neck_w=22,
            rest=dict(open=0.92, brow=-0.12, brow_dy=-2, mouth='smirk', look=0.5),
            on=dict(joy=dict(low=0.0)))


def freckles(s=0):
    r = rnd(4)
    out = []
    for cx in (-40, 40 if not s else 24):
        for i in range(5):
            out.append(flat(ell(s + cx + r.uniform(-15, 15 if not s or cx < 0 else 8), 44 + r.uniform(-9, 7), 2.1, 2.1, n=5), '#cf8a55'))
    return out


def zig(pts_top, teeth):
    """The top outline + a fringe of scissor zigzags: teeth is a list of (x, y) tips and notches, right to left."""
    return pts_top + [corner(t) for t in teeth]


def hair(yaw):
    """One piece: the crown snipped into spikes, the fringe into zigzags."""
    crown = lambda dx: [(-70 + dx, -118), (-50 + dx, -102), (-34 + dx, -128), (-12 + dx, -106), (8 + dx, -132), (28 + dx, -106), (50 + dx, -122), (64 + dx, -98)]
    if yaw < 0.25:
        front = [paint(zig([(-92, -16, 1), (-98, -56), (-74, -96, 1)], crown(0) + [(74, -96)]) + [(98, -56), (92, -16, 1)] +
                       [corner(p) for p in [(78, -44), (66, -26), (50, -52), (36, -30), (18, -56), (2, -34), (-16, -58), (-32, -34), (-50, -56), (-64, -30), (-78, -48)]], HAIR, 2, var=1)]
        return [], front
    if yaw < 0.75:
        front = [paint(zig([(-98, 6, 1), (-106, -50), (-82, -94, 1)], crown(-6) + [(70, -90)]) + [(86, -54), (80, -18, 1)] +
                       [corner(p) for p in [(72, -44), (62, -28), (52, -54), (40, -30), (26, -56), (12, -34), (-6, -58), (-22, -32), (-42, -52), (-58, -22), (-74, -34), (-80, 4)]], HAIR, 2, var=1)]
        return [], front
    front = [paint(zig([(-20, 70, 1), (-70, 62), (-104, 10), (-106, -50), (-84, -92, 1)], crown(-14) + [(58, -88)]) + [(76, -52, 1)] +
                   [corner(p) for p in [(60, -62), (58, -34), (40, -54), (30, -26), (12, -46), (0, -14), (-18, -28), (-24, 14), (-40, 22), (-36, 54)]], HAIR, 2, var=1)]
    return [], front


def head(yaw=0.5, expr=None, collar=None):
    pl = F.place(dict(F.DEFAULT, **SPEC), yaw)
    f = F.face(SPEC, yaw, expr, extras=freckles(pl['s']) if yaw < 0.75 else [flat(ell(30 + i * 9, 46 + (i % 2) * 7, 2.1, 2.1, n=5), '#cf8a55') for i in range(4)])
    back, front = hair(yaw)
    if yaw >= 0.75:
        f['on'] = []
    out = [back, F.neck(SPEC, yaw, 30), collar or [], F.stack(f, front=front)]
    if yaw >= 0.75:
        out.append(F.ear(-20, 28, f['spec'], -1, 1.1))
    return out


def tee(pts, lines):
    """The tee: a red piece with white strips glued across."""
    return [card(pts, TEE, 1)] + [card(strip(l, 9), STRIPE, 1) for l in lines]


def shoulders(yaw=0):
    k, dx = (1.0, 0) if yaw < 0.25 else ((0.9, 4) if yaw < 0.75 else (0.6, -8))
    pts = [(dx - 26, 108), (dx + 26, 108), (dx + 78 * k, 128), (dx + 100 * k, 170), (dx + 104 * k, 240, 1), (dx - 104 * k, 240, 1), (dx - 100 * k, 170), (dx - 78 * k, 128)]
    out = [card(pts, TEE, 1)]
    for yy in (150, 182, 214):
        w = (88 if yy == 150 else 100) * k
        out.append(card(strip([(dx - w, yy), (dx, yy + 3), (dx + w, yy)], 11), STRIPE, 1))
    out.append(card(crescent(dx - 26, 108, dx + 26, 108, -14, 9), dark(TEE, 0.18), 1))
    return out


def bust(yaw=0, expr=None):
    return [shoulders(yaw), head(yaw, expr)]


def plane(x, y, ang=0, s=1.0):
    p = [card([(-34, 6, 1), (34, -4, 1), (-20, 16, 1)], '#d9d2c2', 1),
         card([(-36, -8, 1), (34, -4, 1), (-34, 6, 1)], '#fbf6ea', 2),
         card([(-22, 2, 1), (34, -4, 1), (-14, 12, 1)], '#ece5d6', 1)]
    return move(rot(scale(p, s), ang), x, y)


def figure(expr=None, yaw=0.5):
    """On the run, leaning forward, the paper plane drawn back for the throw. Feet at y = 0."""
    hs = 0.58
    o = []
    o += B.ground_shadow(4, 80)
    # back leg kicked up behind, front leg stepping
    o += B.limb([(-14, -150), (-46, -92), (-84, -62)], [22, 19, 15], SKIN, 1)
    o += [card(strip([(-80, -74), (-90, -52)], 16), '#fbf6ea', 1)]
    o += rot(B.shoe(-100, -40, 1, 36, '#c9412f'), 38, (-100, -40))
    o += B.limb([(14, -150), (40, -84), (30, -14)], [22, 19, 15], SKIN, 1)
    o += [card(strip([(35, -90), (45, -80)], 7), '#f1e1c0', 1)]                       # the plaster
    o += [card(strip([(30, -30), (29, -10)], 17), '#fbf6ea', 1)]
    o += B.shoe(12, 0, 1, 40, '#c9412f')
    # far arm reaching forward
    o += B.limb([(34, -246), (72, -226), (104, -250)], [18, 16, 13], SKIN, 1)
    o += B.hand(106, -252, -118, 0.82, SKIN, spread=14, thumb=-1)
    # shorts and tee (leaning)
    o += [paint([(-34, -176, 1), (34, -186, 1), (44, -122, 1), (6, -116, 1), (2, -146, 1), (-4, -112, 1), (-44, -116, 1)], SHORTS, 1, var=0)]
    t = [(-22, -262), (30, -268), (44, -240), (40, -178, 1), (-36, -168, 1), (-40, -236)]
    o += [card(t, TEE, 1)]
    for yy in (-236, -212, -188):
        o += [card(strip([(-40, yy + 6), (2, yy), (42, yy - 4)], 9), STRIPE, 1)]
    o += [card(strip([(22, -262), (38, -250), (46, -228)], 22), TEE, 1)]
    o += move(rot(scale(head(yaw, expr), hs), 6), 16, -322)
    # near arm drawn back and up with the plane
    o += [card(strip([(-24, -256), (-40, -250), (-50, -240)], 24), TEE, 2)]
    o += B.limb([(-36, -250), (-78, -262), (-86, -316)], [18, 16, 13], SKIN, 2)
    o += plane(-84, -346, -14, 1.0)
    o += B.fist(-86, -318, 176, 0.82, SKIN, 2)
    return o
