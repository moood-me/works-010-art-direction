"""Вера, about 40 — strict, clever, tired. The tallest and slimmest: a smaller head on a long neck, dark hair waved
back from a middle part into a low bun, oval spectacles, half-lowered lids (tired), straight thin brows, a longer
slightly pointed nose, small dark-red lips. A long teal dress with a white collar and a belt, a cardigan over it,
books held to the chest, low heeled shoes.
Head: centre (0,0), radius 60."""
import math
from lib import (INK, LW, LWI, Head, blob, line, smooth, circle, ellipse, g, clip, union, hose, eye, brow,
                 mouth, nose, cheek, arm, leg)

SKIN = '#f1d4bd'
SKIN_SH = '#dcae92'
HAIR = '#2b2230'
HAIR_HI = '#5a4a62'
DRESS = '#2f7a78'
DRESS_SH = '#245f5d'
CARD = '#7d3b4a'
COLLAR = '#f4eee2'
SHOE = '#2a221e'
BOOK1 = '#b8432f'
BOOK2 = '#d9b45a'
R = 60
FEET = 486  # the shoe soles

EXPR = {
    'neutral': dict(look=(-.3, .15), lid=.42, brow=(-.05, .25), mouth='lips'),
    'joy': dict(eye='closed-happy', brow=(.15, .15), mouth='lips-smile', blush=1.3),
    'surprise': dict(look=(0, 0), lid=.05, brow=(.5, .5), browy=-10, mouth='lips-o'),
    'sad': dict(look=(0, .6), lid=.5, rot=.35, brow=(.8, .8), mouth='lips-frown'),
    'angry': dict(look=(0, .1), lid=.42, rot=-.42, brow=(-1.0, -1.0), browy=6, mouth='shout', open_=.7, blush=1.3),
}


def head(a=0.0, expr='neutral'):
    e = EXPR[expr]
    H = Head(R, a)
    s = math.sin(a)
    c = math.cos(a)
    out = []
    # the bun at the back of the head
    bx = -62 * s
    if abs(s) > .2:
        out.append(circle(bx - 8 * s, 6, 30, HAIR) + line([(bx - 24 * s, -6), (bx - 8 * s, 16), (bx + 6 * s, 2)], 2.2, HAIR_HI))
    else:
        out.append(blob([(-30, 50), (30, 50), (36, 66), (0, 76), (-36, 66)], HAIR))
    out.append(union([H.ball(), H.muzzle(40, 50, 50, 40, 22)], SKIN))
    blush = e.get('blush', 1.0)
    for x in (-38, 38):
        X, Y, Z, fz = H.project(x, 32)
        if fz > .15:
            out.append(cheek(X, Y, 9 * blush * (.5 + .5 * fz), op=.35))
    for side, x in ((-1, -20), (1, 20)):
        X, Y, Z, fz = H.project(x, 4)
        if fz <= .08:
            continue
        out.append(eye(X, Y, 18, 24, look=e.get('look', (0, 0)), fz=fz, kind=e.get('eye', 'ring'), lid=e.get('lid'),
                       rot=e.get('rot', 0), side=side, lash=1, heavy=.25 if e.get('eye', 'ring') == 'ring' else 0, skin=SKIN,
                       pr=(9.5, 12)))
        if e.get('eye', 'ring') == 'ring':  # tired: a soft line under the eye
            out.append(line([(X - 11 * (.4 + .6 * fz), Y + 25), (X, Y + 28), (X + 11 * (.4 + .6 * fz), Y + 25)], 1.6, SKIN_SH))
        bx2, by, _, bfz = H.project(x + side * 2, -26 + e.get('browy', 0))
        t = e['brow'][0 if side < 0 else 1]
        out.append(brow(bx2, by, 26 * (.4 + .6 * bfz), tilt=t, arch=.08, th=4.2, side=side))
    # oval spectacles
    gp = []
    for side, x in ((-1, -20), (1, 20)):
        X, Y, Z, fz = H.project(x, 6)
        if fz > .08:
            gp.append((X, Y, fz))
            out.append(ellipse(X, Y, 21 * (.4 + .6 * fz), 17, 'none', 2.2))
            out.append(ellipse(X - 5, Y - 5, 3, 5, '#ffffff', 0, extra='opacity=".6"'))
    if len(gp) == 2:
        (x1, y1, f1), (x2, y2, f2) = gp
        out.append(line([(x1 + 21 * (.4 + .6 * f1), y1 - 2), ((x1 + x2) / 2, y1 - 5), (x2 - 21 * (.4 + .6 * f2), y2 - 2)], 2.2))
    for side in (-1, 1):  # temple arms
        X, Y, Z, fz = H.project(side * 52, 2)
        if Z > 0 and abs(s) > .3:
            if gp:
                gx = min(gp, key=lambda p: abs(p[0] - X))
                out.append(line([(gx[0] + side * 21 * (.4 + .6 * gx[2]), gx[1] - 2), (X, Y - 2)], 2.2))
    X, Y, Z, fz = H.project(0, 33, R + 6)
    out.append(nose(X, Y, 7, SKIN_SH, kind='pointed', fz=fz, dirx=s))
    X, Y, Z, fz = H.project(0, 56, R - 8)
    out.append(mouth(X, Y, 20 if e['mouth'].startswith('lips') else 26, e['mouth'], fz=fz, lip='#8e2a2e', open_=e.get('open_', 1)))
    # hair: a middle part, waves swept back over the ears
    face_loop = [(-58, 30), (-58, 6), (-50, -16), (-34, -32), (-14, -40), (0, -44), (14, -40), (34, -32), (50, -16), (58, 6),
                 (58, 30), (62, 50), (40, 90), (0, 100), (-40, 90), (-62, 50)]
    out.append(H.cap(face_loop, HAIR, grow=6))
    ring = H.ball(6)
    waves = ''
    for sd in (-1, 1):
        waves += line(H.loop([(sd * 2, -60), (sd * 22, -50), (sd * 40, -40), (sd * 56, -18)]), 2.4, HAIR_HI)
        waves += line(H.loop([(sd * 4, -74), (sd * 30, -66), (sd * 52, -48)]), 2.4, HAIR_HI)
    out.append(clip(ring, waves + line(H.loop([(0, -44), (0, -66), (0, -90)]), 2.6, INK)))
    # finger waves swept back over the ears: a scalloped mass on each side
    for sd in (-1, 1):
        X, Y, Z, fz = H.project(sd * 54, 4, 18)
        if Z < -10:
            continue
        w = 17 * (.45 + .55 * max(fz, .3)) if abs(s) > .3 and sd * s > 0 else 17
        o = 1 if X > 0 else -1
        pts = [(X - o * w * .6, Y - 34), (X + o * w * .5, Y - 30), (X + o * w * .95, Y - 14), (X + o * w * .6, Y - 4),
               (X + o * w * 1.0, Y + 10), (X + o * w * .7, Y + 24), (X + o * w * .9, Y + 36), (X - o * w * .1, Y + 40),
               (X - o * w * .5, Y + 20), (X - o * w * .45, Y - 10)]
        out.append(blob(pts, HAIR))
        out.append(line([(X + o * w * .1, Y - 22), (X + o * w * .55, Y - 12), (X + o * w * .2, Y + 2)], 2.2, HAIR_HI))
        out.append(line([(X + o * w * .1, Y + 10), (X + o * w * .5, Y + 22), (X + o * w * .1, Y + 32)], 2.2, HAIR_HI))
    return ''.join(out)


def dress(s=0.0, swing=0.0):
    out = []
    sk = 10 * swing
    body = smooth([(-24 + 6 * s, 104), (-30 + 6 * s, 140), (-20 + 8 * s, 196), (22 + 10 * s, 196), (32 + 8 * s, 140), (26 + 6 * s, 104),
                   (2 + 8 * s, 98)])
    skirt = smooth([(-20 + 8 * s, 192), (-34 + 8 * s, 260), (-52 + 8 * s - sk, 368), (-20 + 8 * s - sk, 376), (14 + 8 * s - sk, 372),
                    (52 + 10 * s - sk, 366), (36 + 10 * s, 260), (22 + 10 * s, 192)])
    out.append(union([skirt, body], DRESS))
    out.append(line([(-6 + 8 * s, 230), (-14 + 8 * s - sk, 370)], 2) + line([(14 + 9 * s, 230), (24 + 9 * s - sk, 368)], 2))
    out.append(blob([(-21 + 8 * s, 190), (23 + 10 * s, 190), (24 + 10 * s, 202), (-22 + 8 * s, 202)], '#1d4746', LWI + .5, k=.6))
    cx = 2 + 8 * s
    out.append(blob([(cx, 98), (cx - 22, 100), (cx - 18, 116), (cx - 2, 112)], COLLAR, LWI + .5))
    out.append(blob([(cx, 98), (cx + 22, 100), (cx + 18, 116), (cx + 2, 112)], COLLAR, LWI + .5))
    out.append(circle(cx, 124, 3, COLLAR, 1.5) + circle(cx, 146, 3, COLLAR, 1.5))
    return ''.join(out)


def cardigan_sides(s=0.0):
    """Open cardigan fronts hanging down both sides of the body."""
    l = smooth([(-24 + 6 * s, 104), (-34 + 6 * s, 150), (-34 + 6 * s, 236), (-20 + 6 * s, 240), (-14 + 7 * s, 150), (-8 + 7 * s, 108)])
    r = smooth([(26 + 6 * s, 104), (36 + 8 * s, 150), (36 + 10 * s, 236), (22 + 10 * s, 240), (16 + 9 * s, 150), (12 + 9 * s, 108)])
    return union([l], CARD) + union([r], CARD)


def books():
    return (blob([(-26, -4), (26, -10), (28, 6), (-24, 12)], BOOK2, LW, k=.3) + line([(-22, 6), (26, 0)], 1.4)
            + blob([(-28, -20), (24, -22), (26, -6), (-26, -4)], BOOK1, LW, k=.3) + line([(-24, -10), (22, -12)], 1.4, '#f2d38a'))


def figure(view='q', pose='stand', expr='neutral'):
    a = {'front': 0.0, 'q': .55, 'side': 1.25}[view]
    s = math.sin(a)
    tv = 'front' if view == 'front' else 'side'
    out = []
    if view == 'side':
        return figure_side(pose, expr)
    out.append(leg([(-12 + 8 * s, 360), (-14 + 8 * s, 420), (-16 + 6 * s, 470)], 20, 16, 10, SKIN, SHOE, ss=.7, toe=-1 if view == 'front' else 1, view=tv))
    out.append(leg([(16 + 10 * s, 360), (16 + 10 * s, 420), (18 + 12 * s, 470)], 20, 16, 10, SKIN, SHOE, ss=.7, toe=1, view=tv))
    out.append(hose([(2 + 8 * s, 50), (2 + 8 * s, 104)], 16, SKIN))
    out.append(dress(s, swing=-.6 if pose == 'books' else 0))
    out.append(cardigan_sides(s))
    if pose == 'stand':
        out.append(arm([(-28 + 6 * s, 112), (-44 + 6 * s, 170), (-40 + 6 * s, 228)], 15, CARD, 'rest', .72, flip=True))
        out.append(arm([(30 + 8 * s, 112), (46 + 8 * s, 170), (42 + 8 * s, 228)], 15, CARD, 'rest', .72))
        out.append(g(head(a, expr), 2 + 8 * s, 0))
    elif pose == 'books':
        # upright, books held to the chest with the near arm, the other hand on the hip
        out.append(arm([(30 + 8 * s, 112), (70, 160), (40 + 8 * s, 196)], 15, CARD, 'fist', .72))
        out.append(g(head(a, expr), 4 + 8 * s, -2, 1, rot=-4))
        out.append(g(books(), 8 + 8 * s, 150, 1.1, rot=-12))
        out.append(arm([(-28 + 6 * s, 112), (-40, 170), (0, 168)], 15, CARD, 'rest', .72, flip=True))
    return ''.join(out)


def figure_side(pose='stand', expr='neutral'):
    a = 1.25
    out = []
    out.append(leg([(0, 360), (0, 420), (0, 470)], 20, 16, 10, SKIN_SH, SHOE, ss=.7, toe=1))
    out.append(arm([(2, 112), (-6, 170), (-2, 226)], 15, '#6a3240', 'rest', .72))
    out.append(hose([(14, 50), (6, 104)], 16, SKIN))
    body = smooth([(-12, 104), (-14, 140), (-10, 196), (18, 196), (26, 140), (18, 104), (6, 98)])
    skirt = smooth([(-10, 192), (-20, 260), (-30, 368), (0, 376), (34, 366), (24, 260), (18, 192)])
    out.append(leg([(8, 360), (10, 420), (12, 470)], 20, 16, 10, SKIN, SHOE, ss=.7, toe=1))
    out.append(union([skirt, body], DRESS))
    out.append(blob([(-11, 190), (19, 190), (20, 202), (-12, 202)], '#1d4746', LWI + .5, k=.6))
    out.append(blob([(10, 98), (26, 102), (22, 116), (8, 112)], COLLAR, LWI + .5))
    out.append(union([smooth([(-14, 104), (-18, 150), (-16, 236), (-2, 240), (0, 150), (4, 108)])], CARD))
    out.append(arm([(0, 112), (8, 170), (4, 228)], 15, CARD, 'rest', .72))
    out.append(g(head(a, expr), 16, 0))
    return ''.join(out)
