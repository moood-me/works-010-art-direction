"""Марат, about 35, a cook — huge, loud, merry, generous. The biggest silhouette in the cast: a barrel in a white
cook's jacket under a long terracotta apron, a small head with no neck, black curls, a thick black beard, a broad
nose, eyes narrowed by laughing, the mouth wide open with teeth and tongue; thick forearms, big hands, a towel on the
shoulder, a ladle.
"""
import math
import kit as K
import face as F
import body as B
from kit import form, ink, paint, hatch, ell, arc

NAME = 'Марат'
HEIGHT = 520
HAIR = '#1d1716'
JACKET = '#e2e6e2'
APRON = '#c8582f'
TROUS = '#38302d'
SHOE = '#1d1716'
STEEL = '#b9c4c6'

HEAD = F.Head(rows=[(-56, 36), (-46, 43), (-26, 46), (-2, 47), (18, 46), (32, 42), (42, 32), (48, 18)],
              eye_y=-6, eye_gap=15, eye_r=5.0, nose='potato', nose_s=1.35, nose_y=6, mouth_y=26, mouth_w=15,
              brow_y=-21, brow_len=11, brow_lw=5.2, ear=(0, 2, 9), blush_r=10, cheek_y=10, blush_op=0.85,
              nose_fill='#f6d8c4', prof=dict(brow=2, nose=-2, chin=6, jaw=0.75, lip=3, lip2=4),
              expr={'calm': dict(eye='happy', mouth='open', curve=1.0, open=0.85, brow=-4, tilt=0.1),
                    'joy': dict(eye='happy', mouth='open', curve=1.0, open=1.15, brow=-8, tilt=0.15),
                    'surprise': dict(eye='wide', mouth='o', open=1.0),
                    'sadness': dict(eye='ring', lid=0.4, mouth='line', curve=-0.9, tilt=0.6),
                    'anger': dict(eye='ring', lid=0.3, mouth='teeth', open=0.6, brow=5, tilt=-0.7)})


EXPR_MOUTH = {k: v.get('mouth') for k, v in HEAD.expr.items()}


def curl_hair(view):
    if view == 'front':
        base = [(-44, -34), (-46, -60), (-20, -80), (16, -80), (44, -62), (44, -34), (30, -48), (0, -52), (-30, -48)]
        cs = [(-38, -60), (-22, -74), (-2, -80), (18, -76), (34, -64), (-44, -44), (44, -46), (-8, -66), (12, -64)]
    elif view == 'three':
        base = [(-50, -28), (-50, -60), (-24, -80), (12, -80), (40, -64), (44, -42), (30, -50), (4, -52), (-34, -44)]
        cs = [(-44, -58), (-28, -74), (-8, -80), (14, -76), (32, -64), (-50, -38), (-20, -62), (2, -66)]
    else:
        base = [(-56, -24), (-56, -58), (-28, -80), (8, -80), (34, -62), (30, -46), (6, -52), (-26, -46), (-46, -18)]
        cs = [(-50, -52), (-36, -72), (-14, -80), (8, -76), (26, -64), (-56, -32), (-28, -58)]
    s = form(base, HAIR, lw=2.2, tex='brush')
    for i, (x, y) in enumerate(cs):
        r = 9.5 + (i % 3) * 1.2
        s += form(ell(x, y, r, r * 0.85, 10, start=i), HAIR, lw=1.8, tex='flat', off=False)
        s += ink(arc(x - 1, y + 1, r * 0.55, r * 0.45, 3.5, 5.9, 5), 1.3, color='#7a6a62', weight=0)
    return s


def beard(view, expr):
    L = HEAD.layout(view)
    mx, my = L['mouth'], HEAD.mouth_y
    if view == 'front':
        pts = [(-46, 4), (-40, 26), (-30, 48), (-14, 62), (0, 66), (14, 62), (30, 48), (40, 26), (46, 4), (38, 12),
               (24, 16), (12, 14), (0, 15), (-12, 14), (-24, 16), (-38, 12)]
    elif view == 'three':
        pts = [(-40, 0), (-38, 24), (-26, 48), (-6, 62), (14, 66), (34, 58), (48, 40), (52, 16), (46, 8), (34, 14),
               (22, 13), (10, 15), (-4, 16), (-22, 14)]
    else:
        W = HEAD.front_x()
        pts = [(-10, 0), (-6, 26), (4, 48), (22, 62), (40, 64), (W + 4, 52), (W + 6, 32), (W, 18), (W - 12, 14),
               (14, 14)]
    s = form(pts, HAIR, lw=2.2, tex='brush')
    # a light hole in the beard round the mouth, so the mouth reads
    o = 1.0 if expr in ('calm', 'joy') else 0.6
    if view == 'side':
        hole = ell(mx - 4, my + 6, 9, 9 * o + 3, 10)
    else:
        hole = ell(mx, my + 7, HEAD.mouth_w + 5, 10 * o + 4, 12)
    lips = EXPR_MOUTH.get(expr, 'open') == 'line'
    s += paint(hole if not lips else [(x, y - 3) for x, y in ell(hole[0][0] - (HEAD.mouth_w + 5), my + 4, HEAD.mouth_w + 2, 7, 12)],
               '#3a2622' if not lips else '#e8c3b0', 'flat', off=False)
    # moustache over the top of the mouth
    if view == 'front':
        st = [(-2, 15), (-14, 14), (-24, 20), (-20, 24), (-8, 21), (0, 22), (8, 21), (20, 24), (24, 20), (14, 14), (2, 15)]
    elif view == 'three':
        st = [(mx - 2, 14), (mx - 16, 14), (mx - 24, 21), (mx - 18, 24), (mx - 6, 21), (mx + 2, 22), (mx + 12, 21),
              (mx + 22, 23), (mx + 22, 17), (mx + 10, 13)]
    else:
        st = [(mx - 6, 13), (mx - 16, 17), (mx - 14, 23), (mx - 4, 21), (mx + 6, 22), (mx + 8, 16)]
    s_st = form(st, HAIR, lw=1.8, tex='flat', off=False)
    for x, y in [(-30, 40), (-14, 54), (8, 58), (26, 44)] if view != 'side' else [(10, 46), (30, 56), (0, 26)]:
        s += ink(arc(x + (6 if view == 'three' else 0), y, 4.5, 3.6, 3.4, 6.0, 5), 1.2, color='#6d5f58', weight=0)
    return s, s_st


def head(view='three', expr='calm'):
    b, st = beard(view, expr)
    return HEAD.draw(view, expr, beard=b, stache=st, hair_front=curl_hair(view))


def place_head(view, expr, x, y, tilt=0.0, s=1.0):
    with K.scaled(K.S() * s):
        h = head(view, expr)
    return '<g transform="translate(%.1f %.1f) rotate(%.1f) scale(%.3f)">%s</g>' % (x, y, tilt, s, h)


# ---------------------------------------------------------------- the figure (feet at 0, crown at -540)
HEIGHT = 540
HEAD_Y = -480


def jacket(view):
    f = [(-28, -452), (0, -456), (28, -452), (70, -440), (96, -408), (108, -340), (108, -260), (98, -200), (80, -166),
         (0, -158), (-80, -166), (-98, -200), (-108, -260), (-108, -340), (-96, -408), (-70, -440)]
    s = [(-14, -454), (10, -456), (34, -450), (58, -436), (80, -404), (98, -340), (100, -260), (90, -200), (70, -166),
         (10, -158), (-34, -166), (-48, -200), (-54, -260), (-56, -340), (-52, -408), (-38, -440)]
    return B.pick(f, s, view)


def apron(view):
    f = [(-40, -404), (40, -404), (44, -340), (66, -300), (72, -200), (70, -112), (0, -106), (-70, -112), (-72, -200),
         (-66, -300), (-44, -340)]
    s = [(70, -398), (90, -396), (96, -340), (104, -300), (106, -200), (102, -112), (80, -106), (60, -112), (62, -200),
         (66, -300), (72, -340)]
    return B.pick(f, s, view, 0.25)


def towel(view):
    x0, top = {'front': (-46, -446), 'three': (-34, -444), 'side': (8, -452)}[view]
    pts = [(x0 - 14, top - 8), (x0 + 12, top - 8), (x0 + 18, top + 30), (x0 + 14, top + 84), (x0 - 8, top + 86),
           (x0 - 8, top + 30)]
    s = form(pts, '#f4ead2', lw=1.9, tex='brush')
    for k in (0.66, 0.76):
        y = top + 86 * k
        s += ink([(x0 - 7, y), (x0 + 15, y - 1)], 2.8, color='#b8432a', weight=0, taper=0.05)
    return s


def ladle(x, y, a=-1.3, L=90):
    c, s = math.cos(a), math.sin(a)
    tip = (x + c * L, y + s * L)
    out = form(B.tube([(x - c * 14, y - s * 14), tip], 6, 5), STEEL, lw=1.7, tex='brush')
    bowl = ell(tip[0] + c * 14, tip[1] + s * 14, 21, 15, 12, rot=a)
    out += form(bowl, STEEL, lw=2.1, tex='brush')
    out += ink(arc(tip[0] + c * 12, tip[1] + s * 12, 11, 7, 0.5 + a, 2.4 + a, 6), 1.3, color='#fbfbf6', weight=0)
    return out


def arm(sh, el, wr, hand_a, kind, flip=False):
    """A thick arm: a thick bare forearm, the white sleeve rolled up just below the elbow, a big hand."""
    cuff_a, cuff_b = K.lerp(el, wr, 0.12), K.lerp(el, wr, 0.3)
    o = B.limb([K.lerp(el, wr, 0.2), wr], 34, 27, K.SKIN, tex='flat')
    o += ink([K.lerp(el, wr, 0.45), K.lerp(el, wr, 0.75)], 1.0, color='#6d5f58', weight=0)    # a hairy forearm
    o += B.limb([sh, el, cuff_b], 48, 44, JACKET)
    o += form(B.tube([cuff_a, cuff_b], 52, 50), JACKET, lw=2.1, tex='brush')
    o += B.hand(wr[0], wr[1], hand_a, kind, 1.9, flip=flip)
    return o


def upper(view, expr, act):
    o = []
    if view != 'front':
        if act:
            o.append(arm((-70, -414), (-126, -330), (-90, -268), -0.5, 'fist', flip=True))
        else:
            ax = B.pick(-100, -44, view)
            o.append(arm((ax + 12, -414), (ax - 6, -330), (ax - 2, -258), 1.62, 'rest', flip=True))
    if view == 'front':
        # the arms come out from under the jacket's shoulders
        for sg in (-1, 1):
            o.append(arm((sg * 84, -404), (sg * 112, -326), (sg * 110, -256), 1.5 if sg > 0 else 1.64, 'rest',
                         flip=sg < 0))
    jp = jacket(view)
    o.append(form(jp, JACKET, lw=2.7, tex='brush'))
    k = B.pick(1.0, 0.8, view)
    o.append(hatch([(56 * k, -436), (86 * k, -400), (94 * k, -300), (84 * k, -200), (66 * k, -170), (66 * k, -300)],
                   '#8a7f70', angle=-1.2, step=4.5, op=0.45))
    # two rows of buttons above the apron bib
    bx = B.pick(0, 50, view, 0.4)
    for dx in ((-14, 14) if view != 'side' else (0,)):
        for by in (-430, -410):
            o.append(form(ell(bx + dx, by, 3.6, 3.6, 8), '#e8dcc8', lw=1.3, tex='flat'))
    ap = apron(view)
    o.append(form(ap, APRON, lw=2.4, tex='brush'))
    o.append(hatch([ap[2], ap[3], ap[4], ap[5], K.lerp(ap[5], ap[6], 0.4), K.lerp(ap[3], ap[8], 0.35)],
                   '#6b2410', angle=-1.3, step=4.0, op=0.45))
    if view != 'side':
        px = B.pick(0, 16, view, 0.35)
        o.append(form([(px - 22, -250), (px + 22, -250), (px + 20, -212), (px - 20, -212)], APRON, lw=1.8,
                      tex='brush'))
    o.append(ink([(ap[0][0] + 2, -400), (ap[0][0] - 8, -448)], 2.0, taper=0.1))
    o.append(ink([(ap[1][0] - 2, -400), (ap[1][0] + 8, -448)], 2.0, taper=0.1))
    o.append(towel(view))
    hx = B.pick(0, 30, view)
    o.append(place_head(view, expr, hx + (-4 if act else 0), HEAD_Y, -8 if act else 0, 1.15))
    if act and view == 'three':
        # the ladle up high, laughing
        o.append(arm((72, -420), (130, -404), (136, -492), -1.55, 'hold', flip=True))
        o.append(ladle(136, -500, -1.42, 70))
        o.append(B.hand(136, -492, -1.55, 'hold', 1.9, flip=True))
    elif view == 'front':
        pass
    else:
        ax = B.pick(88, 56, view)
        o.append(arm((ax - 8, -414), (ax + 6, -330), (ax + 6, -258), 1.5, 'rest'))
    return ''.join(o)


def figure(view='three', expr='calm', pose='stand'):
    act = pose == 'act'
    o = []
    d = 0 if view == 'front' else 1
    feet = B.pick((-32, 32), (16, 40), view)
    if act and view == 'three':
        feet = (-44, 46)
    for x in feet:
        o.append(B.limb([(x * 0.7, -170), (x, -80), (x, -12)], 40, 34, TROUS, tex='brush'))
        o.append(B.shoe(x + (6 if d else 0), 0, 2.1, d, SHOE))
    up = upper(view, expr, act)
    if act and view == 'three':
        up = '<g transform="rotate(-5 0 -170)">%s</g>' % up
    return ''.join(o) + up
