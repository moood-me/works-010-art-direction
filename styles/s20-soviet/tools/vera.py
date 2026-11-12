"""Вера, about 40 — strict, clever, tired. A tall narrow column: a long face, a long straight nose, round glasses,
heavy lids, a mouth like a ruled line, dark hair pulled up into a tight bun with a grey streak; a long deep-teal
coat-dress with a thin white collar, a folder of papers, small heeled shoes.
"""
import math
import kit as K
import face as F
import body as B
from kit import form, ink, paint, hatch, ell, arc

NAME = 'Вера'
HEIGHT = 480
HAIR = '#2b1d1b'
COAT = '#2f6670'
FOLDER = '#d39a35'
SHOE = '#3b1f1c'

HEAD = F.Head(rows=[(-62, 26), (-52, 33), (-30, 36), (-6, 35), (14, 31), (28, 24), (38, 15), (45, 6)],
              eye_y=-6, eye_gap=13, eye_r=4.6, nose='long', nose_s=1.25, nose_y=8, mouth_y=26, mouth_w=8,
              brow_y=-18, brow_len=8.5, brow_lw=2.8, ear=(0, 2, 7), blush_r=6.5, cheek_y=14, blush_op=0.45,
              prof=dict(brow=1, nose=-1, chin=1, jaw=0.45),
              expr={'calm': dict(eye='ring', lid=0.42, look=(0.2, 0.25), brow=1, tilt=-0.1, curve=-0.12),
                    'joy': dict(eye='happy', mouth='line', curve=0.8, brow=-3, tilt=0.15),
                    'sadness': dict(lid=0.55, tilt=0.5),
                    'anger': dict(lid=0.38, mouth='line', curve=-0.7, brow=4, tilt=-0.65),
                    'surprise': dict(open=0.6)})


def hair(view):
    if view == 'front':
        back = [(-30, -58), (0, -66), (30, -58), (38, -40), (36, -20), (28, -38), (0, -46), (-28, -38), (-36, -20),
                (-38, -40)]
        bun = ell(0, -76, 17, 13, 12)
        streak = [(-8, -64), (-2, -48)]
    elif view == 'three':
        back = [(-34, -56), (0, -66), (28, -60), (38, -42), (36, -24), (28, -40), (4, -48), (-24, -42), (-34, -18),
                (-40, -36)]
        bun = ell(-8, -76, 16, 13, 12)
        streak = [(-2, -64), (6, -48)]
    else:
        back = [(-44, -50), (-8, -66), (24, -62), (40, -46), (34, -40), (12, -50), (-14, -44), (-34, -26), (-46, -10),
                (-52, -30)]
        bun = ell(-30, -72, 15, 13, 12)
        streak = [(0, -62), (14, -50)]
    s = form(bun, HAIR, lw=2.2, tex='brush')
    s += ink(arc(bun[0][0] - 15 if False else (sum(p[0] for p in bun) / 12), -76, 9, 6, 3.3, 5.6, 6), 1.4,
             color='#d8cfc4', weight=0)
    s += form(back, HAIR, lw=2.2, tex='brush')
    s += ink(streak, 2.6, color='#bcb3ac', weight=0, taper=0.4)
    return s


def glasses(view, expr):
    L = HEAD.layout(view)
    s = ''
    rr = 9.5
    pts = []
    for x, k in L['eyes']:
        r = rr * k
        pts.append((x, r))
        s += ink(ell(x, HEAD.eye_y, r * (0.75 if view == 'side' else 1), r, 14), 1.9, closed=True, weight=0.3)
    if view == 'front':
        s += ink([(pts[0][0] + pts[0][1], HEAD.eye_y - 1), (0, HEAD.eye_y - 4), (pts[1][0] - pts[1][1], HEAD.eye_y - 1)],
                 1.6, taper=0)
        for sg in (-1, 1):
            s += ink([(sg * (abs(pts[0][0]) + rr), HEAD.eye_y - 2), (sg * 35, HEAD.eye_y - 4)], 1.5, taper=0)
    elif view == 'three':
        s += ink([(pts[0][0] + pts[0][1], HEAD.eye_y - 1), (L['nose'] - 2, HEAD.eye_y - 4),
                  (pts[1][0] - pts[1][1], HEAD.eye_y - 1)], 1.6, taper=0)
        s += ink([(pts[0][0] - pts[0][1], HEAD.eye_y - 2), (-22, HEAD.eye_y - 3)], 1.5, taper=0)
    else:
        s += ink([(pts[0][0] - pts[0][1] * 0.75, HEAD.eye_y - 2), (-2, HEAD.eye_y - 1)], 1.5, taper=0)
    return s


def head(view='three', expr='calm'):
    return HEAD.draw(view, expr, hair_front=hair(view), after=glasses(view, expr))


def place_head(view, expr, x, y, tilt=0.0, s=1.05):
    with K.scaled(K.S() * s):
        h = head(view, expr)
    return '<g transform="translate(%.1f %.1f) rotate(%.1f) scale(%.3f)">%s</g>' % (x, y, tilt, s, h)


# ---------------------------------------------------------------- the figure (feet at 0, crown at -480)
def coat(view):
    f = [(-12, -348), (12, -348), (27, -340), (30, -300), (24, -240), (26, -180), (32, -80), (0, -74), (-32, -80),
         (-26, -180), (-24, -240), (-30, -300), (-27, -340)]
    s = [(-8, -350), (8, -348), (16, -340), (22, -300), (16, -240), (18, -180), (24, -80), (0, -74), (-20, -80),
         (-18, -180), (-16, -240), (-20, -300), (-18, -340)]
    return B.pick(f, s, view)


def folder(x, y, a=0.0, w=40, h=30):
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    c, s = math.cos(a), math.sin(a)
    P = [(x + px * c - py * s, y + px * s + py * c) for px, py in pts]
    out = form(P, FOLDER, lw=1.9, tex='brush', smooth=False)
    for k in (0.25, 0.5):
        q = [(x + px * c - py * s, y + px * s + py * c) for px, py in [(-w / 2 + 3, -h / 2 + h * k), (w / 2 - 3, -h / 2 + h * k)]]
        out += ink(q, 0.9, taper=0.2)
    return out


def figure(view='three', expr='calm', pose='stand'):
    o = []
    act = pose == 'act'
    d = 0 if view == 'front' else 1
    for x in B.pick((-8, 8), (-2, 4), view):
        o.append(B.leg((x, -78), (x, -40), (x, -9), 8.5, color='#5b4a48'))
        o.append(B.shoe(x + (3 if d else 0), 0, 1.1, d, SHOE))
    if view != 'front' and not act:
        ax = B.pick(-26, -6, view)
        o.append(B.limb([(ax + 4, -334), (ax - 2, -278), (ax - 2, -226)], 13, 10, COAT))
        o.append(B.hand(ax - 2, -225, 1.62, 'rest', 1.0, flip=True))
    cp = coat(view)
    o.append(form(cp, COAT, lw=2.4, tex='brush'))
    k = B.pick(1.0, 0.7, view)
    o.append(hatch([(18 * k, -330), (28 * k, -300), (22 * k, -240), (30 * k, -84), (16 * k, -80), (12 * k, -240)],
                   '#0f2a30', angle=-1.25, step=4.0, op=0.5))
    # a row of buttons, a belt
    bx = B.pick(0, 14, view, 0.45)
    for by in (-320, -290, -260, -200, -160):
        o.append(form(ell(bx, by, 2.6, 2.6, 8), '#1a2f33', lw=1.0, tex='flat'))
    o.append(ink([(cp[12][0] + 2, -236), (bx, -232), (cp[3][0] - 2, -236)], 1.6, taper=0.1))
    # neck + collar + head
    nx = B.pick(0, 4, view)
    o.append(form([(nx - 5, -372), (nx + 5, -372), (nx + 5.5, -344), (nx - 5.5, -344)], K.SKIN, lw=1.7, tex='flat'))
    col = [(nx - 13, -352), (nx, -342), (nx + 13, -352), (nx + 12, -344), (nx, -334), (nx - 12, -344)]
    o.append(form(col, '#fbf6ea', lw=1.6, tex='flat'))
    o.append(place_head(view, expr, nx + (2 if act else 0), -412, -3 if act else 0))
    if act and view == 'three':
        # one arm hugs the folder to the chest, the other hand pushes the glasses up the nose
        o.append(B.limb([(-20, -334), (-30, -290), (0, -282)], 13, 10, COAT))
        o.append(folder(4, -300, -0.12, 44, 32))
        o.append(B.hand(0, -282, -0.4, 'fist', 0.95, flip=True))
        # the other hand up beside her, one finger raised: «Внимание.»
        o.append(B.limb([(22, -334), (52, -300), (54, -366)], 13, 10, COAT))
        o.append(B.hand(54, -366, -1.62, 'point', 0.95))
    elif view == 'front':
        for sg in (-1, 1):
            o.append(B.limb([(sg * 21, -334), (sg * 30, -278), (sg * 31, -226)], 13, 10, COAT))
            o.append(B.hand(sg * 31, -225, 1.5 if sg > 0 else 1.64, 'rest', 1.0, flip=sg < 0))
        o.append(folder(-40, -210, 1.48, 44, 30))
    else:
        ax = B.pick(24, 8, view)
        o.append(B.limb([(ax - 2, -334), (ax + 4, -278), (ax + 4, -226)], 13, 10, COAT))
        o.append(folder(ax + 6, -212, 1.5, 44, 30))
        o.append(B.hand(ax + 4, -225, 1.5, 'rest', 1.0))
    return ''.join(o)
