"""Аня, about 20 — warm, trusting, dreamy. An egg of a face under a big chestnut mass of hair with loops in it,
eyes looking up, a small hooked nose; a mustard dress like a bell, a short brick-red cardigan, thin legs, red shoes.
"""
import math
import kit as K
import face as F
import body as B
from kit import form, ink, paint, hatch, ell, arc, move

NAME = 'Аня'
HEIGHT = 440
HAIR = '#4a1d12'
DRESS = '#e2a93a'
CARD = '#bf4a2c'
SHOE = '#a8321f'

HEAD = F.Head(rows=[(-56, 32), (-46, 40), (-26, 45), (-2, 45), (18, 39), (31, 28), (40, 13)],
              eye_y=-3, eye_gap=15, eye_r=6.4, prof=dict(nose=-2, chin=-3, jaw=0.5), nose='button', nose_s=1.05, nose_y=10, mouth_y=24, mouth_w=7,
              brow_y=-17, brow_len=8, brow_lw=3.0, ear=(0, 6, 0), blush_r=8.5, cheek_y=15, lashes=2,
              expr={'calm': dict(look=(0.35, -0.55), curve=0.55, brow=-1, tilt=0.12),
                    'sadness': dict(look=(0.1, 0.7)),
                    'anger': dict(mouth='teeth', open=0.45, lid=0.3, brow=3, tilt=-0.7),
                    'surprise': dict(open=0.7)})
HS = 0.9          # head units → figure units
NECK_Y = -337


def curl(x, y, r, d=1):
    """A curl drawn as a light open loop on the dark mass (as in «История одного преступления»)."""
    pts = [(x + d * r * math.cos(t) * (1 - 0.12 * t), y + r * math.sin(t) * (1 - 0.12 * t) * 0.85)
           for t in [i * 0.55 for i in range(11)]]
    return ink(pts, 1.6, taper=0.3, color='#f3e2c4', weight=0)


def hair(view):
    """(behind the face, over the face) in head units."""
    if view == 'front':
        back = [(-34, -64), (0, -70), (34, -64), (56, -42), (64, -8), (64, 30), (70, 58), (54, 76), (34, 66),
                (28, 30), (-28, 30), (-34, 66), (-54, 76), (-70, 58), (-64, 30), (-64, -8), (-56, -42)]
        fr = [(-46, -28), (-38, -54), (-10, -68), (20, -66), (44, -52), (50, -30), (46, -8), (36, -24), (16, -38),
              (2, -28), (-12, -40), (-32, -34), (-44, -6)]
        curls = [(-56, 44, 7, 1), (56, 50, 7, -1), (-60, 6, 6, 1), (60, 10, 6, -1), (-24, -54, 6, 1), (26, -54, 6, -1)]
    elif view == 'three':
        back = [(-34, -66), (2, -71), (32, -64), (49, -44), (52, -18), (44, -4), (34, 22), (-4, 34), (-16, 62),
                (-36, 80), (-62, 74), (-70, 42), (-72, 0), (-64, -40)]
        fr = [(-44, -30), (-34, -58), (-4, -70), (26, -66), (46, -50), (50, -28), (47, -12), (36, -28), (20, -38),
              (6, -31), (-8, -42), (-26, -38), (-38, -12)]
        curls = [(-56, 54, 7, 1), (-64, 16, 6, 1), (-46, -30, 6, 1), (-30, 66, 6, 1), (-6, -58, 6, -1)]
    else:
        back = [(-30, -68), (4, -71), (30, -64), (44, -48), (40, -32), (22, -36), (8, -14), (-6, 18), (-12, 52),
                (-28, 80), (-56, 76), (-70, 42), (-74, 0), (-64, -44)]
        fr = [(-26, -60), (0, -70), (28, -66), (44, -48), (40, -32), (24, -40), (6, -44), (-10, -34), (-20, -46)]
        curls = [(-52, 58, 7, 1), (-62, 14, 6, 1), (-44, -34, 6, 1), (-26, 68, 6, 1)]
    b = form(back, HAIR, lw=2.4, tex='brush')
    for cx, cy, r, d in curls:
        b += curl(cx, cy, r, d)
    f = form(fr, HAIR, lw=2.2, tex='brush')
    f += curl(14, -54, 5, -1)
    if view == 'side':
        # in profile the mass of hair lies over the back of the skull
        return '', b + f
    return b, f


def head(view='three', expr='calm'):
    b, f = hair(view)
    return HEAD.draw(view, expr, hair_back=b, hair_front=f)


def place_head(view, expr, x, y, tilt=0.0, s=1.2):
    with K.scaled(K.S() * s):
        h = head(view, expr)
    return '<g transform="translate(%.1f %.1f) rotate(%.1f) scale(%.3f)">%s</g>' % (x, y, tilt, s, h)


# ---------------------------------------------------------------- the figure
# feet at 0, hem at -104, shoulders at -306, chin at -316, crown at -440
HEAD_Y = -370


def dress(view):
    f = [(-16, -308), (16, -308), (26, -297), (24, -270), (18, -244), (32, -190), (60, -110), (30, -102), (0, -100),
         (-30, -102), (-60, -110), (-32, -190), (-18, -244), (-24, -270), (-26, -297)]
    s = [(-11, -310), (11, -308), (18, -294), (22, -272), (14, -244), (24, -190), (40, -110), (14, -102), (-4, -100),
         (-24, -102), (-50, -114), (-30, -190), (-15, -244), (-16, -270), (-17, -296)]
    return B.pick(f, s, view)


def shade_side(view):
    k = B.pick(1.0, 0.75, view)
    return [(15 * k, -242), (30 * k, -188), (58 * k, -112), (34 * k, -104), (21 * k, -190)]


def scarf(view):
    nx = B.pick(0, 6, view)
    band = [(nx - 16, -316), (nx - 4, -312), (nx + 16, -317), (nx + 18, -306), (nx + 2, -299), (nx - 17, -304)]
    if view == 'side':
        band = [(nx - 12, -318), (nx + 2, -314), (nx + 12, -319), (nx + 13, -306), (nx + 2, -300), (nx - 13, -304)]
    ex = nx + B.pick(8, 9, view)
    end = [(ex - 4, -304), (ex + 5, -304), (ex + 9, -262), (ex + 1, -258), (ex - 2, -282)]
    return form(end, CARD, lw=1.9, tex='brush') + hatch(end, '#5a1a0c', angle=1.3, step=3.2, op=0.4) + \
        form(band, CARD, lw=2.0, tex='brush')


def figure(view='three', expr='calm', pose='stand'):
    o = []
    act = pose == 'act'
    # legs and shoes
    if act and view == 'three':
        o.append(B.leg((-8, -106), (-6, -56), (-6, -11), 10))
        o.append(B.shoe(-4, 0, 1.35, 1, SHOE))
        o.append(B.leg((12, -106), (1, -56), (16, -14), 10))
        o.append(B.shoe(20, -5, 1.3, 1, SHOE))
    else:
        d = 0 if view == 'front' else 1
        for x in B.pick((-11, 11), (-3, 5), view):
            o.append(B.leg((x, -106), (x, -56), (x, -11), 10))
            o.append(B.shoe(x + (4 if d else 0), 0, 1.35, d, SHOE))
    # far arm when standing in three-quarters / side: behind the dress
    if not act and view != 'front':
        ax = B.pick(-24, -6, view)
        o.append(B.limb([(ax + 4, -296), (ax - 3, -250), (ax - 3, -204)], 14, 10, DRESS))
        o.append(B.hand(ax - 3, -203, 1.62, 'rest', 1.1, flip=True))
    o.append(form(dress(view), DRESS, lw=2.4, tex='brush'))
    o.append(hatch(shade_side(view), '#7a3e0c', angle=-1.15, step=4.2, op=0.5))
    hem = dress(view)
    o.append(ink([lerp_pt(hem[6], hem[5], 0.2), (hem[8][0], hem[8][1] - 15), lerp_pt(hem[10], hem[11], 0.2)], 1.5,
                 taper=0.3))
    # neck, scarf, head
    nx = B.pick(0, 6, view)
    o.append(form([(nx - 5.5, -326), (nx + 5.5, -326), (nx + 6, -302), (nx - 6, -302)], K.SKIN, lw=1.8, tex='flat'))
    o.append(scarf(view))
    tilt = -10 if act else 0
    o.append(place_head(view, expr, nx + (3 if act else 0), HEAD_Y, tilt, 1.2))
    if act and view == 'three':
        # both hands clasped at the chest, holding a daisy up to her cheek
        o.append(B.limb([(-17, -296), (-26, -258), (0, -250)], 14, 10, DRESS))
        o.append(ink([(10, -248), (30, -288), (50, -318)], 1.3, taper=0.1, weight=0))
        o.append(daisy(52, -322))
        o.append(B.hand(-1, -250, -0.2, 'fist', 1.05, flip=True))
        o.append(B.limb([(21, -296), (34, -262), (18, -246)], 14, 10, DRESS))
        o.append(B.hand(18, -246, -2.75, 'fist', 1.05, flip=True))
    elif view == 'front':
        for sg in (-1, 1):
            o.append(B.limb([(sg * 21, -296), (sg * 30, -250), (sg * 32, -204)], 14, 10, DRESS))
            o.append(B.hand(sg * 32, -203, 1.5 if sg > 0 else 1.64, 'rest', 1.1, flip=sg < 0))
    else:
        ax = B.pick(24, 8, view)
        o.append(B.limb([(ax - 2, -296), (ax + 6, -250), (ax + 6, -204)], 14, 10, DRESS))
        o.append(B.hand(ax + 6, -203, 1.5, 'rest', 1.1))
    return ''.join(o)


def lerp_pt(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def daisy(x, y):
    s = ''
    for i in range(9):
        a = i * 2 * math.pi / 9
        pts = ell(x + 6 * math.cos(a), y + 6 * math.sin(a), 4.2, 2.0, 7, rot=a)
        s += form(pts, '#fffaf0', lw=1.1, tex='flat', off=False)
    s += form(ell(x, y, 3.2, 3.2, 8), '#e8b22a', lw=1.1, tex='flat')
    return s
