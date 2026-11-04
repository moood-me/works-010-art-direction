"""Аня, about 20 — warm, trusting, dreamy. A round ball head with full cheeks and a small chin, big tall eyes set close
with a heavy upper lid and three lashes, a little button nose, small red lips; an auburn wavy bob with rolled curl
tips and a red bow. A polka-dot dress with puff sleeves, thin hose arms in gloves, shapely hose legs, Mary-Jane shoes.
Head: centre (0,0), radius 70. Figure: feet at y≈FEET."""
import math
from lib import (INK, LW, LWI, WHITE, Head, P, blob, line, tline, smooth, circle, ellipse, g, clip, union, sausage,
                 hose, tube, glove, shoe, shadow, eye, brow, mouth, nose, cheek, f)

SKIN = '#f6dcc4'
SKIN_SH = '#e9bfa3'
HAIR = '#8d3a1f'
HAIR_HI = '#b5552e'
DRESS = '#4f86b5'
DRESS_SH = '#3c6d97'
DOT = '#fbf7ee'
BOW = '#d4402f'
SHOE = '#b8352a'
R = 70
FEET = 420

EXPR = {
    'neutral': dict(eye='ring', look=(.15, -.55), lid=.18, brow=0.15, mouth='lips-smile'),
    'joy': dict(eye='closed-happy', brow=-.05, mouth='grin', open_=.9, blush=1.3),
    'surprise': dict(eye='spark', look=(0, 0), brow=.15, browy=-12, mouth='lips-o'),
    'sad': dict(eye='ring', look=(0, .5), lid=.34, rot=.32, brow=.85, mouth='lips-frown', tear=True),
    'angry': dict(eye='ring', look=(0, .1), lid=.36, rot=-.38, brow=-.9, mouth='lips-frown', blush=1.2),
}


def head(a=0.0, expr='neutral'):
    e = EXPR[expr]
    H = Head(R, a)
    s = math.sin(a)
    out = []
    # back hair: the bob behind the head, curls rolled under at the ends
    back = [(-76 + 20 * s, -30), (-84 + 26 * s, 20), (-88 + 30 * s, 58), (-76 + 30 * s, 84), (-56 + 26 * s, 88),
            (-40, 70), (40, 70), (56 + 26 * s, 88), (76 + 22 * s, 84), (88 + 16 * s, 58), (84 + 14 * s, 20), (76 + 10 * s, -30)]
    out.append(blob(back, HAIR))
    for cx in (-66 + 28 * s, 66 + 16 * s):  # rolled curl tips
        out.append(line([(cx - 10, 80), (cx, 74), (cx + 9, 80)], 2.2, HAIR_HI))
    # the face: a ball with full cheeks and a small round chin
    jaw = H.pts([(-60, 20), (-64, 42), (-48, 66), (-22, 80), (0, 84), (22, 80), (48, 66), (64, 42), (60, 20)])
    face = smooth(jaw, False)
    out.append(union([f'M {-R} 0 A {R} {R} 0 1 1 {R} 0 A {R} {R} 0 1 1 {-R} 0 Z', smooth(jaw + H.pts([(0, -10)]), True)], SKIN))
    # cheeks
    blush = e.get('blush', 1.0)
    for x in (-40, 40):
        X, Y, Z, fz = H.project(x, 34)
        if fz > .15:
            out.append(cheek(X, Y, 11 * blush * (.5 + .5 * fz), op=.5))
    # eyes
    for side, x in ((-1, -21), (1, 21)):
        X, Y, Z, fz = H.project(x, 0)
        if fz <= .05:
            continue
        out.append(eye(X, Y, 17, 24, look=e.get('look', (0, 0)), fz=fz, kind=e['eye'], lid=e.get('lid'), rot=e.get('rot', 0),
                       lash=3, side=side, heavy=.42 if e['eye'] not in ('closed-happy', 'closed') else 0, skin=SKIN))
        bx, by, _, bfz = H.project(x + side * 2, -36 + e.get('browy', 0))
        out.append(brow(bx, by, 26 * (.4 + .6 * bfz), tilt=e['brow'], th=4.2, side=side))
    if e.get('tear'):
        X, Y, _, _ = H.project(28, 26)
        out.append(blob([(X, Y - 8), (X + 6, Y + 4), (X, Y + 9), (X - 6, Y + 4)], '#bfe0ee', 2))
    # nose and mouth
    X, Y, Z, fz = H.project(0, 28)
    out.append(nose(X, Y, 6.5, SKIN_SH, fz=fz, dirx=s))
    X, Y, Z, fz = H.project(0, 50)
    out.append(mouth(X, Y, 24 if e['mouth'].startswith('lips') else 30, e['mouth'], fz=fz, open_=e.get('open_', 1), skin=SKIN))
    # front hair: a cap with a side part and a big wave rolling over the forehead, curls at the temples
    cap_out = [(-74, 12), (-80, -30), (-62, -70), (-22, -88), (24, -88), (64, -68), (80, -30), (76, 12)]
    line_in = [(70, 0), (66, -22), (52, -30), (40, -26), (30, -36), (12, -44), (-6, -42), (-22, -50), (-40, -46),
               (-54, -34), (-66, -18), (-70, 0)]
    cap = [(x + 14 * s, y) for x, y in cap_out] + H.pts(line_in)
    out.append(blob(cap, HAIR))
    # wave lines and the part
    out.append(line(H.pts([(-8, -82), (-20, -66), (-24, -54)]), 2.2, HAIR_HI))
    out.append(line(H.pts([(18, -80), (34, -62), (46, -44)]), 2.2, HAIR_HI))
    out.append(line(H.pts([(-40, -74), (-52, -58), (-58, -40)]), 2.2, HAIR_HI))
    # spit curls at the temples
    for side in (-1, 1):
        X, Y, Z, fz = H.project(side * 62, 6)
        if fz > .02 or side * s > 0:
            out.append(blob([(X - 8 * side, Y - 6), (X + 2 * side, Y - 10), (X + 8 * side, Y), (X + 2 * side, Y + 12),
                             (X - 6 * side, Y + 8)], HAIR, 2.4))
    # the bow on top
    bx = 30 + 18 * s
    out.append(g(blob([(-4, -6), (-26, -20), (-30, 0), (-24, 14), (-4, 6)], BOW) + blob([(4, -6), (26, -20), (30, 0), (24, 14), (4, 6)], BOW)
                 + circle(0, 0, 8, BOW) + line([(-20, -6), (-8, -1)], 1.6) + line([(20, -6), (8, -1)], 1.6), bx, -80, 1, rot=18))
    return ''.join(out)
