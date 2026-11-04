"""Тим, about 8 — mischievous, curious. A big head (nearly half his height), a mop of dark hair with three cowlick
tufts, big pie-cut eyes glancing sideways, one brow up, a snub nose, freckles, a wide grin with a missing tooth, big
ears. A red-and-white striped shirt, blue dungaree shorts on one strap, striped socks, big shoes.
Head: centre (0,0), radius 66."""
import math
from lib import (INK, LW, LWI, WHITE, Head, P, blob, line, tline, smooth, circle, g, clip, union, hose, tube,
                 eye, brow, mouth, nose, cheek, f, arm, leg)

SKIN = '#f5d5b6'
SKIN_SH = '#e2ad8c'
HAIR = '#3a2620'
HAIR_HI = '#6b4535'
SHIRT = '#d6493a'
SHIRT2 = '#f6efe0'
DUNG = '#3f6fa0'
DUNG_SH = '#30577f'
SOCK = '#f6efe0'
SHOE = '#7a4a2c'
R = 66
FEET = 295  # the shoe soles

EXPR = {
    'neutral': dict(look=(.75, -.1), brow=(.1, -.4), mouth='smirk'),
    'joy': dict(eye='closed-happy', brow=(.3, .3), mouth='grin', open_=1.1, blush=1.3),
    'surprise': dict(eye='spark', look=(0, 0), brow=(.6, .6), browy=-10, mouth='o'),
    'sad': dict(look=(0, .7), lid=.3, rot=.35, brow=(.9, .9), mouth='wobble'),
    'angry': dict(look=(0, .1), lid=.38, rot=-.45, brow=(-1.1, -1.1), browy=8, mouth='shout', blush=1.3),
}


def head(a=0.0, expr='neutral'):
    e = EXPR[expr]
    H = Head(R, a)
    s = math.sin(a)
    out = []
    out.append(union([H.ball(), H.muzzle(38, 60, 44, 44, 24)], SKIN))
    blush = e.get('blush', 1.0)
    for x in (-42, 42):
        X, Y, Z, fz = H.project(x, 36)
        if fz > .15:
            out.append(cheek(X, Y, 10 * blush * (.5 + .5 * fz), op=.45))
            for dx, dy in ((-6, -4), (2, -6), (6, 2), (-2, 3)):  # freckles
                out.append(circle(X + dx * (.5 + .5 * fz), Y + dy, 1.6, '#a8613f', 0))
    # eyes: big, tall, pie-cut, nearly touching
    for side, x in ((-1, -21), (1, 21)):
        X, Y, Z, fz = H.project(x, 4)
        if fz <= .08:
            continue
        out.append(eye(X, Y, 19, 27, look=e.get('look', (0, 0)), fz=fz, kind=e.get('eye', 'pie'), lid=e.get('lid'),
                       rot=e.get('rot', 0), side=side, skin=SKIN))
        bx, by, _, bfz = H.project(x + side * 2, -34 + e.get('browy', 0))
        t = e['brow'][0 if side < 0 else 1]
        out.append(brow(bx, by, 24 * (.4 + .6 * bfz), tilt=t, th=5.5, side=side))
    X, Y, Z, fz = H.project(0, 34, R + 6)
    out.append(nose(X, Y, 8, SKIN_SH, fz=fz, dirx=s))
    X, Y, Z, fz = H.project(4, 56, R - 4)
    mk = e['mouth']
    if mk == 'smirk':
        hw = 20 * (.55 + .45 * fz)
        out.append(tline([(X - hw, Y - 2), (X, Y + 6), (X + hw, Y - 8)], 2.2, 4.5, w2=2.2))
        out.append(line([(X + hw + 2, Y - 14), (X + hw - 2, Y - 6)], 2))
    elif mk == 'grin':
        out.append(mouth(X, Y, 40, 'grin', fz=fz, open_=e.get('open_', 1)))
        out.append(P(f'M {f(X - 9)} {f(Y - 2)} L {f(X - 1)} {f(Y - 2)} L {f(X - 1)} {f(Y + 5)} L {f(X - 9)} {f(Y + 5)} Z', WHITE, INK, 1.6))
        out.append(P(f'M {f(X + 5)} {f(Y - 2)} L {f(X + 13)} {f(Y - 2)} L {f(X + 13)} {f(Y + 5)} L {f(X + 5)} {f(Y + 5)} Z', WHITE, INK, 1.6))
    else:
        out.append(mouth(X, Y, 30, mk, fz=fz, open_=e.get('open_', 1)))
    # the mop: hair over the skull, cut by a ragged fringe, three cowlick tufts on top
    face_loop = [(-60, 20), (-60, -6), (-50, -22), (-40, -28), (-32, -22), (-22, -34), (-10, -28), (2, -38), (14, -30),
                 (26, -38), (38, -28), (50, -24), (60, -6), (60, 20), (64, 50), (40, 96), (0, 110), (-40, 96), (-64, 50)]
    out.append(H.cap(face_loop, HAIR, grow=8))
    for i, (x, y, ang) in enumerate(((-4, -78, 10), (12, -78, 38), (26, -72, 62))):
        X, Y, Z, fz = H.project(x, y, 40)
        out.append(g(blob([(-8, 6), (-6, -10), (0, -26 - 4 * (i == 1)), (6, -10), (8, 6)], HAIR, LW, k=.9), X, Y + 4, 1, rot=ang))
    # ears
    for side in (-1, 1):
        X, Y, Z, fz = H.project(side * 64, 18, 0)
        if Z > -20 and (abs(s) < .3 or side * s < 0):
            sx = side if abs(s) < .9 else (1 if X > 0 else -1)
            out.append(blob([(X, Y - 20), (X + sx * 20, Y - 16), (X + sx * 22, Y + 6), (X + sx * 10, Y + 20), (X - sx * 2, Y + 16)], SKIN))
            out.append(line([(X + sx * 5, Y - 9), (X + sx * 13, Y - 5), (X + sx * 11, Y + 8)], 2))
    out.append(clip(H.ball(9), line(H.loop([(-30, -70), (-38, -56)]), 2.4, HAIR_HI) + line(H.loop([(20, -72), (30, -58)]), 2.4, HAIR_HI)))
    return ''.join(out)


def body(s=0.0):
    out = []
    shirt = smooth([(-24 + 4 * s, 76), (-30 + 4 * s, 110), (-28 + 6 * s, 150), (30 + 10 * s, 150), (32 + 8 * s, 110), (26 + 6 * s, 76),
                    (2 + 6 * s, 72)])
    out.append(union([shirt], SHIRT2))
    stripes = ''.join(f'<rect x="-60" y="{y}" width="140" height="8" fill="{SHIRT}"/>' for y in range(78, 150, 16))
    out.append(clip(shirt, stripes))
    out.append(P(shirt, 'none', INK, LW))
    shorts = smooth([(-30 + 6 * s, 136), (-34 + 6 * s, 170), (-34 + 6 * s, 196), (-4 + 8 * s, 198), (2 + 8 * s, 182), (8 + 10 * s, 198),
                     (38 + 12 * s, 196), (36 + 12 * s, 168), (32 + 10 * s, 136)])
    bib = smooth([(-14 + 8 * s, 108), (18 + 10 * s, 108), (20 + 10 * s, 140), (-16 + 8 * s, 140)], True, .5)
    out.append(union([shorts, bib], DUNG))
    out.append(line([(2 + 8 * s, 182), (2 + 8 * s, 160)], 2))
    out.append(blob([(-6 + 9 * s, 116), (10 + 9 * s, 116), (10 + 9 * s, 128), (-6 + 9 * s, 128)], DUNG_SH, LWI, k=.4))
    # one strap up, the other hanging loose
    out.append(hose([(16 + 10 * s, 110), (22 + 10 * s, 92), (24 + 8 * s, 76)], 8, DUNG))
    out.append(hose([(-12 + 8 * s, 112), (-30 + 6 * s, 132), (-34 + 6 * s, 156)], 8, DUNG))
    out.append(circle(16 + 10 * s, 112, 3.4, '#e0b84a', 1.6) + circle(-12 + 8 * s, 112, 3.4, '#e0b84a', 1.6))
    return ''.join(out)


def legs(s, tv, toe):
    out = [leg([(-14 + 6 * s, 190), (-18 + 6 * s, 236), (-18 + 6 * s, 276)], 17, 16, 14, SKIN, SHOE, ss=.85, toe=toe, view=tv),
           leg([(18 + 10 * s, 190), (22 + 10 * s, 236), (22 + 12 * s, 276)], 17, 16, 14, SKIN, SHOE, ss=.85, toe=1, view=tv)]
    return ''.join(out)


def socks(pts_list):
    return ''.join(hose(p, 17, SOCK) + clip(tube(p, 17), ''.join(
        f'<rect x="-100" y="{y}" width="200" height="4" fill="{SHIRT}"/>' for y in range(250, 290, 8))) for p in pts_list)


def figure(view='q', pose='stand', expr='neutral'):
    a = {'front': 0.0, 'q': .55, 'side': 1.25}[view]
    s = math.sin(a)
    tv = 'front' if view == 'front' else 'side'
    out = []
    if view == 'side':
        return figure_side(pose, expr)
    if pose == 'stand':
        out.append(legs(s, tv, -1 if view == 'front' else 1))
        out.append(socks([[(-18 + 6 * s, 246), (-18 + 6 * s, 276)], [(22 + 11 * s, 246), (22 + 12 * s, 276)]]))
        out.append(body(s))
        out.append(arm([(-26 + 4 * s, 86), (-44 + 4 * s, 120), (-40 + 4 * s, 160)], 13, SKIN, 'rest', .7, flip=True))
        out.append(arm([(28 + 8 * s, 86), (46 + 8 * s, 120), (42 + 8 * s, 160)], 13, SKIN, 'rest', .7))
        out.append(sleeves(s))
        out.append(g(head(a, expr), 4 * s, 0))
    elif pose == 'sneak':
        # feet apart, a slingshot hidden behind the back, a finger to the lips: «shh», a sly look aside
        out.append(arm([(-26 + 4 * s, 86), (-40, 118), (-20, 146)], 13, SKIN, 'hold', .7, flip=True))
        out.append(g(slingshot(), -50, 150, 1.1, rot=-35))
        out.append(leg([(-14 + 6 * s, 190), (-26 + 6 * s, 236), (-34 + 6 * s, 276)], 17, 16, 14, SKIN, SHOE, ss=.85, toe=-1, view=tv))
        out.append(leg([(18 + 10 * s, 190), (30 + 10 * s, 236), (40 + 12 * s, 276)], 17, 16, 14, SKIN, SHOE, ss=.85, toe=1, view=tv))
        out.append(socks([[(-31 + 6 * s, 252), (-34 + 6 * s, 276)], [(36 + 11 * s, 252), (40 + 12 * s, 276)]]))
        out.append(body(s))
        out.append(sleeves(s))
        out.append(g(head(a, expr), 4 * s - 4, 2, 1, rot=-6))
        out.append(arm([(28 + 8 * s, 86), (68, 124), (54, 104)], 13, SKIN, 'point', .7))
    return ''.join(out)


def sleeves(s, near_only=False):
    out = ''
    for x, sd in ((-26 + 4 * s, -1), (28 + 8 * s, 1)):
        if near_only and sd < 0:
            continue
        d = smooth([(x - 12, 76), (x + 10, 74), (x + 14 * sd + 2, 98), (x - 2 + 8 * sd, 104), (x - 12 * sd, 96)])
        out += union([d], SHIRT2) + clip(d, ''.join(f'<rect x="{x - 30}" y="{y}" width="60" height="7" fill="{SHIRT}"/>' for y in range(70, 110, 14))) + P(d, 'none', INK, LW)
    return out


def slingshot():
    return (hose([(0, 0), (0, 22)], 7, '#9a6a3c') + hose([(0, 0), (-10, -18)], 7, '#9a6a3c') + hose([(0, 0), (10, -18)], 7, '#9a6a3c')
            + line([(-10, -18), (0, -6), (10, -18)], 2.4, '#c45a3a'))


def figure_side(pose='stand', expr='neutral'):
    a = 1.25
    out = []
    out.append(leg([(-2, 190), (-4, 236), (-4, 276)], 17, 16, 14, SKIN_SH, SHOE, ss=.85, toe=1))
    out.append(arm([(-4, 86), (-12, 120), (-8, 158)], 13, SKIN_SH, 'rest', .7))
    shirt = smooth([(-14, 76), (-18, 110), (-16, 150), (20, 150), (24, 110), (16, 76)])
    out.append(union([shirt], SHIRT2) + clip(shirt, ''.join(f'<rect x="-60" y="{y}" width="140" height="8" fill="{SHIRT}"/>' for y in range(78, 150, 16)))
               + P(shirt, 'none', INK, LW))
    shorts = smooth([(-18, 136), (-22, 196), (24, 196), (24, 136)], True, .6)
    bib = smooth([(10, 108), (24, 108), (26, 140), (8, 140)], True, .5)
    out.append(leg([(6, 190), (8, 236), (8, 276)], 17, 16, 14, SKIN, SHOE, ss=.85, toe=1))
    out.append(socks([[(8, 246), (8, 276)]]))
    out.append(union([shorts, bib], DUNG))
    out.append(hose([(16, 110), (6, 90), (2, 76)], 8, DUNG))
    out.append(arm([(2, 86), (10, 120), (6, 158)], 13, SKIN, 'rest', .7))
    d = smooth([(-10, 76), (14, 74), (16, 98), (4, 104), (-8, 96)])
    out.append(union([d], SHIRT2) + clip(d, ''.join(f'<rect x="-30" y="{y}" width="60" height="7" fill="{SHIRT}"/>' for y in range(70, 110, 14))) + P(d, 'none', INK, LW))
    out.append(head(a, expr))
    return ''.join(out)
