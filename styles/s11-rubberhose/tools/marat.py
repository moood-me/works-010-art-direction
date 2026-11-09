"""Марат, about 35, a cook — huge, loud, merry, generous. The biggest of the cast: a barrel chest on short thick legs,
heavy shoulders, thick forearms (the hose swells below the rolled sleeve), big gloves. A ball head on no neck: short
black curls (a scalloped cap), a thick black beard with a curly edge, thick black brows, a broad nose, pie-cut eyes
pushed up by the cheeks — and a wide open grin with teeth and tongue, his resting face. A warm-white double-breasted
cook's jacket, a long terracotta apron, a striped towel over the shoulder, a ladle.
Head: centre (0,0), radius 68."""
import math
from lib import (INK, LW, LWI, WHITE, MOUTH, TONGUE, Head, P, blob, line, tline, smooth, circle, ellipse, g, clip,
                 union, hose, eye, brow, mouth, cheek, f, arm, leg, uid)

SKIN = '#f0c9a6'
SKIN_SH = '#dba27f'
NOSE = '#e59a7c'
LIP = '#d98468'
HAIR = '#33262a'
HAIR_HI = '#6a5257'
JACKET = '#f6f0e0'
JACKET_SH = '#d8cfba'
APRON = '#d0673a'
APRON_SH = '#a94e2a'
PANTS = '#4d443f'
SHOE = '#2a221e'
TOWEL = '#f1e3bd'
STEEL = '#b9c2c0'
BRASS = '#d9a93a'
R = 68
FEET = 516  # the shoe soles
HS = 1.08   # the head in the figure

EXPR = {
    # his resting face is a wide smile: the cheeks push the lower lids up
    'neutral': dict(look=(.3, 0), lower=.3, brow=.25, mouth='grin', mw=50, open_=.62),
    'joy': dict(eye='closed-happy', brow=.45, browy=-5, mouth='grin', mw=62, open_=1.0, blush=1.35),
    'surprise': dict(eye='spark', look=(0, 0), brow=.6, browy=-12, mouth='o'),
    'sad': dict(look=(0, .65), lid=.36, rot=.4, brow=1.0, mouth='pout'),
    'angry': dict(look=(0, .1), lid=.4, rot=-.45, brow=-1.1, browy=9, mouth='shout', blush=1.3),
}


def circ(cx, cy, r):
    return f'M {f(cx - r)} {f(cy)} A {f(r)} {f(r)} 0 1 1 {f(cx + r)} {f(cy)} A {f(r)} {f(r)} 0 1 1 {f(cx - r)} {f(cy)} Z'


def grin(cx, cy, w, open_=1.0, fz=1.0):
    """The big laugh: an open D with a smile-curved upper edge, a row of upper teeth along it, a tongue, and a lower
    lip so it reads against the beard."""
    w = w * (.55 + .45 * fz)
    hw = w / 2
    dep = w * .52 * open_
    top = [(cx - hw, cy - 8), (cx - hw * .55, cy - 2), (cx, cy), (cx + hw * .55, cy - 2), (cx + hw, cy - 8)]
    d = smooth(top + [(cx + hw * .82, cy + dep * .55), (cx + hw * .3, cy + dep), (cx - hw * .3, cy + dep), (cx - hw * .82, cy + dep * .55)], True, .9)
    th = 6 + 3.5 * open_
    teeth = smooth([(x, y - 6) for x, y in top] + [(x, y + th) for x, y in reversed(top)], True, .8)
    i = uid('m')
    inner = ellipse(cx + w * .04, cy + dep * 1.02, w * .3, dep * .42, TONGUE, 1.6)
    inner += line([(cx + w * .04, cy + dep * .72), (cx + w * .05, cy + dep)], 1.4, '#a8382b')
    inner += P(teeth, WHITE, INK, 1.6)
    for k in (-1.5, -.5, .5, 1.5):  # gaps between the teeth
        x = cx + k * hw * .36
        inner += line([(x, cy - 6), (x, cy + th + 2)], 1.2, '#9a8f84')
    out = ellipse(cx, cy + dep + 1, hw * .62, 5.5, LIP, LWI)
    out += f'<clipPath id="{i}"><path d="{d}"/></clipPath>' + P(d, MOUTH, None, 0)
    out += f'<g clip-path="url(#{i})">{inner}</g>' + P(d, 'none', INK, LWI + .6)
    return out


def head(a=0.0, expr='neutral'):
    e = EXPR[expr]
    H = Head(R, a)
    s = math.sin(a)
    out = []
    grow = 4
    # curls round the skull: a scalloped edge behind the cap (further down at the back of a turned head)
    curls, curls_in = [], []
    t0 = -208 - 22 * s                      # the back end of the curls
    t1 = 28 - 173 * s if s < .3 else -24 - 32 * (s - .3)     # the front end climbs to the hairline as the head turns
    n = 16
    for i in range(n + 1):
        t = math.radians(t0 + (t1 - t0) * i / n)
        rr = R + grow - 3
        curls.append(circ(math.cos(t) * rr, math.sin(t) * rr, 9 + 1.5 * (i % 2)))
        curls_in.append(circ(math.cos(t) * rr, math.sin(t) * rr, 7 + 1.5 * (i % 2)))
    out.append(union(curls, HAIR))
    # the silhouette: the ball and the volume of the beard (a wider, deeper lower ball with a curly edge)
    mcy, mA, mB, mC, mcz = 44, 70, 56, 54, 24
    mx = mcz * s
    mrx = math.hypot(mA * math.cos(a), mC * s)
    vol = [H.ball(), H.muzzle(mcy, mA, mB, mC, mcz)]
    for i in range(9):
        t = math.radians(8 + i * 164 / 8)
        vol.append(circ(mx + math.cos(t) * (mrx - 5), mcy + math.sin(t) * (mB - 5), 12.5 + 1.5 * (i % 2)))
    out.append(union(vol, SKIN))
    vol_d = ' '.join(vol)
    # the beard, painted inside the silhouette: sideburns, under the cheeks, up under the nose
    beard = [(-68, -14), (-58, 12), (-50, 32), (-36, 42), (-20, 37), (0, 35), (20, 37), (36, 42), (50, 32), (58, 12), (68, -14),
             (96, 30), (84, 116), (0, 150), (-84, 116), (-96, 30)]
    bd = smooth(H.loop(beard), True)
    marks = ''
    for x, y in ((-44, 62), (-22, 86), (8, 92), (36, 74), (52, 50), (-56, 40)):
        X, Y, Z, fz = H.project(x, y)
        if fz > .1:
            k = .5 + .5 * fz
            marks += line([(X - 7 * k, Y - 3), (X - 2 * k, Y + 5), (X + 6 * k, Y + 1)], 2.2, HAIR_HI)
    out.append(clip(vol_d, P(bd, HAIR, INK, LW) + marks))
    blush = e.get('blush', 1.0)
    for x in (-42, 42):
        X, Y, Z, fz = H.project(x, 20)
        if fz > .15:
            out.append(cheek(X, Y, 11 * blush * (.5 + .5 * fz), op=.5))
    # eyes: pie-cut, close together; thick black brows (drawn last, over the hairline)
    brows = []
    for side, x in ((-1, -18), (1, 18)):
        X, Y, Z, fz = H.project(x, -2)
        if fz <= .08:
            continue
        out.append(eye(X, Y, 15, 19.5, look=e.get('look', (0, 0)), fz=fz, kind=e.get('eye', 'pie'), lid=e.get('lid'),
                       rot=e.get('rot', 0), lower=e.get('lower'), side=side, skin=SKIN))
        bx, by, _, bfz = H.project(x + side * 3, -30 + e.get('browy', 0))
        brows.append(brow(bx, by, 30 * (.4 + .6 * bfz), tilt=e['brow'], arch=.3, th=13, side=side))
    # mouth in the beard
    mk = e['mouth']
    MX, MY, MZ, mfz = H.project(0, 54, R - 2)
    MX -= 14 * (1 - mfz) * (1 if s >= 0 else -1)
    if mk == 'grin':
        m = grin(MX, MY, e.get('mw', 50), e.get('open_', 1), mfz)
    elif mk == 'o':
        m = ellipse(MX, MY + 8, 15 * (.55 + .45 * mfz), 18, LIP, LWI) + mouth(MX, MY + 4, 34, 'o', fz=mfz)
    elif mk == 'shout':
        m = ellipse(MX, MY + 22, 17 * (.55 + .45 * mfz), 5.5, LIP, LWI) + mouth(MX, MY + 2, 42, 'shout', fz=mfz, open_=1.05)
    else:  # pout: the moustache droops over a pushed-out lower lip
        hw = 13 * (.55 + .45 * mfz)
        m = blob([(MX - hw, MY + 5), (MX, MY + 2), (MX + hw, MY + 5), (MX + hw * .7, MY + 13), (MX, MY + 16), (MX - hw * .7, MY + 13)], LIP, LWI)
    out.append(clip(vol_d, m))
    # the broad nose over the moustache
    X, Y, Z, fz = H.project(0, 22, R + 9)
    k = .6 + .4 * fz
    out.append(ellipse(X, Y, 17.5 * k, 12.5, NOSE, LWI + .4))
    out.append(ellipse(X - 6 * k + 3 * s, Y - 5, 5, 2.8, '#ffffff', 0, extra='opacity=".7"'))
    # hair: a cap of short curls with a wavy hairline
    hl = [(-56, 24), (-56, -6), (-52, -26), (-44, -36), (-34, -46), (-22, -45), (-11, -52), (0, -49), (11, -52), (22, -45),
          (34, -46), (44, -36), (52, -26), (56, -6), (56, 24), (66, 50), (40, 96), (0, 110), (-40, 96), (-66, 50)]
    out.append(H.cap(hl, HAIR, grow=grow))
    cm = ''
    for x, y in ((-30, -66), (-4, -74), (24, -68), (-50, -44), (46, -50), (8, -58)):
        px, py = H.loop([(x, y)])[0]
        cm += line([(px - 7, py + 2), (px - 2, py - 5), (px + 6, py - 1)], 2.2, HAIR_HI)
    out.append(clip(H.ball(grow), cm))
    out.extend(brows)
    # the cap's own outline must not show inside the curls
    out.append(''.join(P(c, HAIR, None, 0) for c in curls_in))
    # ears
    for side in (-1, 1):
        X, Y, Z, fz = H.project(side * 66, 4, 0)
        if Z > -20 and (abs(s) < .2 or side * s < 0):
            sx = side if abs(s) < .9 else (1 if X > 0 else -1)
            out.append(blob([(X - sx * 4, Y - 17), (X + sx * 13, Y - 14), (X + sx * 16, Y + 4), (X + sx * 8, Y + 16), (X - sx * 4, Y + 13)], SKIN))
            out.append(line([(X + sx * 2, Y - 7), (X + sx * 9, Y - 4), (X + sx * 7, Y + 6)], 2))
    return ''.join(out)


# ---------------------------------------------------------------- the figure
def torso(s=0.0):
    """The barrel: jacket, apron, towel. s: turn."""
    out = []
    chest = smooth([(-72 + 6 * s, 86), (-104 + 6 * s, 128), (-110 + 8 * s, 196), (-94 + 10 * s, 268), (0 + 14 * s, 284),
                    (100 + 14 * s, 268), (118 + 14 * s, 196), (110 + 10 * s, 128), (76 + 8 * s, 86), (2 + 6 * s, 78)])
    out.append(union([chest], JACKET))
    cx = 4 + 16 * s
    # double-breasted front: the flap's edge and two rows of buttons
    out.append(clip(chest, line([(cx - 26, 84), (cx - 40, 150), (cx - 36, 262)], 2.2)))
    for y in (140, 178, 216):
        out.append(circle(cx - 22, y, 4.2, BRASS, 1.6) + circle(cx + 22, y, 4.2, BRASS, 1.6))
    # the long apron from the waist
    ap = smooth([(-94 + 10 * s, 246), (-96 + 10 * s, 330), (-84 + 10 * s, 426), (-30 + 12 * s, 436), (20 + 12 * s, 432), (92 + 14 * s, 426),
                 (106 + 14 * s, 330), (104 + 14 * s, 246), (4 + 14 * s, 254)], True, .9)
    out.append(union([ap], APRON))
    out.append(line([(-34 + 12 * s, 300), (-40 + 12 * s, 430)], 2) + line([(40 + 13 * s, 300), (48 + 13 * s, 428)], 2))
    out.append(blob([(-96 + 10 * s, 244), (4 + 14 * s, 252), (106 + 14 * s, 244), (107 + 14 * s, 260), (4 + 14 * s, 268), (-97 + 10 * s, 260)], APRON_SH, LWI + .5, k=.7))
    # the tie: a bow at the front, a little to the side
    bx, by = 34 + 14 * s, 258
    out.append(blob([(bx, by - 3), (bx - 18, by - 12), (bx - 20, by + 8), (bx, by + 3)], APRON_SH, LWI)
               + blob([(bx, by - 3), (bx + 18, by - 12), (bx + 20, by + 8), (bx, by + 3)], APRON_SH, LWI)
               + hose([(bx - 3, by + 4), (bx - 8, by + 30)], 6, APRON_SH, lw=LWI) + hose([(bx + 3, by + 4), (bx + 10, by + 26)], 6, APRON_SH, lw=LWI)
               + circle(bx, by, 5, APRON_SH, LWI))
    out.append(blob([(-52 + 11 * s, 322), (-8 + 12 * s, 324), (-10 + 12 * s, 366), (-30 + 12 * s, 372), (-50 + 11 * s, 366)], APRON, LWI, k=.6))
    return ''.join(out)


def towel(x, y, sc=1.0, rot=0):
    """A striped kitchen towel hanging over the shoulder."""
    d = smooth([(-17, -4), (0, -10), (17, -4), (19, 50), (17, 104), (0, 108), (-17, 104), (-19, 50)], True, .7)
    stripes = ''.join(f'<rect x="-30" y="{y0}" width="60" height="7" fill="{APRON}"/>' for y0 in (70, 84))
    fr = ''.join(line([(x0, 106), (x0, 114)], 1.8) for x0 in (-12, -4, 4, 12))
    return g(fr + union([d], TOWEL) + clip(d, stripes) + P(d, 'none', INK, LW) + line([(-6, 6), (-8, 60)], 1.6, '#cdbb8f'), x, y, sc, rot)


def ladle():
    """Handle from (0,0) up to the bowl."""
    return (hose([(0, 10), (10, -50), (24, -104)], 7, STEEL) + ellipse(30, -122, 25, 21, STEEL, LW, rot=14)
            + ellipse(31, -127, 19, 11, '#8d9795', LWI, rot=14) + line([(14, -118), (20, -134)], 2.6, '#ffffff', extra='opacity=".7"'))


ARM = dict(w=32, w1=44, w2=27)


def figure(view='q', pose='stand', expr='neutral'):
    a = {'front': 0.0, 'q': .55, 'side': 1.25}[view]
    s = math.sin(a)
    if view == 'side':
        return figure_side(pose, expr)
    tv = 'front' if view == 'front' else 'side'
    out = []
    if pose == 'stand':
        out.append(leg([(-38 + 8 * s, 400), (-40 + 8 * s, 450), (-42 + 6 * s, 486)], 50, 46, 40, PANTS, SHOE, ss=1.2, toe=-1 if view == 'front' else 1, view=tv))
        out.append(leg([(44 + 14 * s, 400), (46 + 14 * s, 450), (48 + 16 * s, 486)], 50, 46, 40, PANTS, SHOE, ss=1.2, toe=1, view=tv))
        out.append(torso(s))
        out.append(arm([(-98 + 6 * s, 122), (-134 + 6 * s, 190), (-122 + 6 * s, 262)], ARM['w'], SKIN, 'rest', 1.2, flip=True, w1=ARM['w1'], w2=ARM['w2'],
                       sleeve=(JACKET, .42)))
        out.append(arm([(106 + 12 * s, 122), (142 + 14 * s, 190), (132 + 14 * s, 262)], ARM['w'], SKIN, 'rest', 1.2, w1=ARM['w1'], w2=ARM['w2'],
                       sleeve=(JACKET, .42)))
        out.append(towel(-66 + 6 * s, 90))
        out = [f'<g transform="scale({1 - .08 * s:.3f} 1)">' + ''.join(out) + '</g>']
        out.append(g(head(a, expr), 4 + 8 * s, -4, HS))
    elif pose == 'laugh':
        # thrown back in a laugh: belly forward, head tipped back, a fist on the hip, the ladle swung up high
        out.append(leg([(-40 + 8 * s, 400), (-52, 450), (-62, 486)], 50, 46, 40, PANTS, SHOE, ss=1.2, toe=1, view=tv))
        out.append(leg([(46 + 14 * s, 400), (60, 450), (70, 486)], 50, 46, 40, PANTS, SHOE, ss=1.2, toe=1, view=tv))
        up = []
        up.append(torso(s))
        up.append(arm([(-98 + 6 * s, 122), (-158, 186), (-104, 250)], ARM['w'], SKIN, 'fist', 1.2, flip=True, w1=ARM['w1'], w2=ARM['w2'],
                      sleeve=(JACKET, .42)))
        up.append(towel(-64 + 6 * s, 90, rot=4))
        up.append(g(ladle(), 186, 46, 1, rot=12))
        up.append(arm([(106 + 12 * s, 122), (170, 150), (184, 66)], ARM['w'], SKIN, 'hold', 1.2, w1=ARM['w1'], w2=ARM['w2'], sleeve=(JACKET, .42)))
        up.append(g(head(a, expr), 0 + 8 * s, -6, HS, rot=-12))
        out.append(f'<g transform="rotate(-7 0 420)">{"".join(up)}</g>')
    elif pose == 'hello':
        # for the portrait: upright, beaming, the ladle held up by the shoulder like a sceptre
        up = []
        up.append(torso(s))
        up.append(arm([(-98 + 6 * s, 122), (-134 + 6 * s, 190), (-122 + 6 * s, 262)], ARM['w'], SKIN, 'rest', 1.2, flip=True, w1=ARM['w1'], w2=ARM['w2'],
                      sleeve=(JACKET, .42)))
        up.append(towel(-64 + 6 * s, 90, rot=4))
        up.append(g(ladle(), 122, 108, .72, rot=6))
        up.append(arm([(106 + 12 * s, 122), (156, 178), (120, 124)], ARM['w'], SKIN, 'hold', 1.2, w1=ARM['w1'], w2=ARM['w2'], sleeve=(JACKET, .42)))
        up.append(g(head(a, expr), 0 + 8 * s, -6, HS, rot=-5))
        out.append(f'<g transform="rotate(-3 0 420)">{"".join(up)}</g>')
    return ''.join(out)


def figure_side(pose='stand', expr='neutral'):
    a = 1.25
    out = []
    out.append(leg([(-10, 400), (-12, 450), (-12, 486)], 50, 46, 40, PANTS, SHOE, ss=1.2, toe=1))
    out.append(arm([(8, 116), (-4, 184), (4, 256)], ARM['w'], SKIN_SH, 'rest', 1.2, w1=ARM['w1'], w2=ARM['w2'], sleeve=(JACKET_SH, .42)))
    chest = smooth([(-40, 88), (-62, 140), (-60, 210), (-48, 270), (20, 284), (86, 264), (106, 204), (98, 140), (62, 92), (10, 80)])
    out.append(leg([(16, 400), (18, 450), (20, 486)], 50, 46, 40, PANTS, SHOE, ss=1.2, toe=1))
    out.append(union([chest], JACKET))
    for y in (140, 178, 216):
        out.append(circle(84 + (y - 140) * .1, y, 4.2, BRASS, 1.6))
    ap = smooth([(-52, 246), (-56, 330), (-48, 426), (10, 434), (84, 424), (98, 330), (98, 246), (20, 254)], True, .9)
    out.append(union([ap], APRON))
    out.append(line([(40, 300), (46, 430)], 2))
    out.append(blob([(-54, 244), (20, 252), (100, 244), (101, 260), (20, 268), (-55, 260)], APRON_SH, LWI + .5, k=.7))
    out.append(arm([(10, 116), (26, 184), (18, 258)], ARM['w'], SKIN, 'rest', 1.2, w1=ARM['w1'], w2=ARM['w2'], sleeve=(JACKET, .42)))
    out.append(towel(12, 90, rot=-3))
    out.append(g(head(a, expr), 24, -4, HS))
    return ''.join(out)
