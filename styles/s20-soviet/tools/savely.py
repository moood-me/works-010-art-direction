"""Савелий Петрович, about 70, a watchmaker — grumpy outside, kind inside. Short and stooped, a big bald dome with
white tufts over the ears, a huge potato nose, bushy white brows over small eyes, a white walrus moustache, a
jeweller's loupe pushed up on the forehead; an olive waistcoat like an egg, a cream shirt with the sleeves rolled up,
baggy brown trousers, big shoes, a pocket watch on a chain.
"""
import math
import kit as K
import face as F
import body as B
from kit import form, ink, paint, hatch, ell, arc

NAME = 'Савелий Петрович'
HEIGHT = 340
VEST = '#6e7834'
SHIRT = '#efe2c4'
TROUS = '#6a4630'
SHOE = '#2a1e18'
WHITE = '#f7f1e4'
BROW = '#ddd8cf'
BRASS = '#d7a531'

HEAD = F.Head(rows=[(-62, 33), (-54, 41), (-36, 46), (-12, 46), (10, 44), (26, 38), (37, 27), (44, 13)],
              eye_y=-3, eye_gap=13, eye_r=5.0, nose='potato', nose_s=1.55, nose_y=8, mouth_y=37, mouth_w=10,
              brow_y=-14, brow_len=12, brow_lw=5.2, brow_fill=BROW, ear=(0, 4, 10), blush_r=8, cheek_y=16,
              blush_op=0.6, nose_fill='#f6dccb', prof=dict(brow=3, nose=-3, chin=-2, jaw=0.6),
              expr={'calm': dict(eye='dot', brow=4, tilt=-0.35, look=(0.3, 0.2)),
                    'joy': dict(brow=-2, tilt=0.2, open=0.55),
                    'surprise': dict(eye='ring', brow=-12),
                    'sadness': dict(eye='ring', lid=0.55, look=(0.1, 0.7), brow=-3, tilt=0.55),
                    'anger': dict(eye='ring', lid=0.3, look=(0.3, 0), brow=4, tilt=-0.55, open=0.4)})


def tuft(pts, lw=1.9):
    return form(pts, WHITE, lw=lw, tex='brush') + hatch(pts, '#8d8a86', angle=-0.5, step=3.2, op=0.4)


def tufts(view):
    """White hair over the ears and at the back, in head units."""
    if view == 'front':
        L = [(-44, -30), (-54, -26), (-52, -18), (-60, -12), (-55, -2), (-60, 6), (-50, 12), (-44, 18), (-46, 2)]
        return tuft(L) + tuft([(-x, y) for x, y in L][::-1])
    if view == 'three':
        L = [(-38, -34), (-50, -32), (-48, -24), (-58, -18), (-52, -8), (-58, 2), (-48, 8), (-50, 18), (-38, 20),
             (-36, 4)]
        R = [(44, -26), (50, -18), (48, -4), (44, 0)]
        return tuft(L) + tuft(R, 1.6)
    L = [(-30, -40), (-44, -38), (-42, -30), (-54, -24), (-48, -12), (-56, -2), (-46, 6), (-50, 18), (-34, 22),
         (-22, 8), (-22, -20)]
    return tuft(L)


def stache(view, expr):
    """A walrus moustache: two lobes from under the nose; the tips droop, and go up when he laughs."""
    droop = {'joy': -7, 'surprise': 9, 'sadness': 17, 'anger': 6}.get(expr, 13)
    lift = -3 if expr in ('joy', 'surprise', 'anger') else 0
    y0 = 23 + lift

    def lobe(cx, d, L):
        pts = [(cx, y0 - 6), (cx + d * L * 0.45, y0 - 5 + droop * 0.15), (cx + d * L, y0 + droop),
               (cx + d * L * 0.72, y0 + 8 + droop * 0.6), (cx + d * L * 0.3, y0 + 12 + droop * 0.2), (cx, y0 + 10)]
        return form(pts, WHITE, lw=1.9, tex='brush') + hatch(pts, '#8d8a86', angle=0.4 * d, step=3.0, op=0.35)

    if view == 'front':
        return lobe(-1, -1, 30) + lobe(1, 1, 30)
    if view == 'three':
        c = HEAD.layout('three')['nose']
        return lobe(c - 1, -1, 26) + lobe(c + 1, 1, 22)
    c = HEAD.layout('side')['nose']
    return lobe(c - 2, -1, 24)


def loupe(view):
    if view == 'front':
        x, y = 8, -44
    elif view == 'three':
        x, y = 18, -46
    else:
        x, y = 34, -44
    band = ink([(-44, -40), (-10, -46), (30, -42), (46, -36)] if view != 'side' else [(-46, -30), (0, -42), (40, -42)],
               1.8, taper=0.05, weight=0)
    body = [(x - 4.5, y - 5), (x + 4.5, y - 5), (x + 6, y + 4), (x - 6, y + 4)]
    return band + form(body, '#2b2620', lw=1.6, tex='flat', smooth=False) + \
        form(ell(x, y + 4, 6, 2.2, 10), '#8fb3bf', lw=1.3, tex='flat')


def head(view='three', expr='calm'):
    return HEAD.draw(view, expr, hair_back=tufts(view), stache=stache(view, expr), after=loupe(view))


def place_head(view, expr, x, y, tilt=0.0, s=1.15):
    with K.scaled(K.S() * s):
        h = head(view, expr)
    return '<g transform="translate(%.1f %.1f) rotate(%.1f) scale(%.3f)">%s</g>' % (x, y, tilt, s, h)


# ---------------------------------------------------------------- the figure (feet at 0, crown near -340)
def vest(view, lean):
    f = [(-30, -222), (0, -226), (30, -222), (42, -196), (48, -150), (44, -112), (24, -98), (0, -96), (-24, -98),
         (-44, -112), (-48, -150), (-42, -196)]
    s = [(-14, -224), (6, -228), (20, -220), (32, -194), (40, -150), (36, -112), (18, -98), (0, -96), (-16, -98),
         (-26, -112), (-30, -150), (-28, -196)]
    p = B.pick(f, s, view)
    return [(x + lean * (-96 - y) / 130, y) for x, y in p]


def figure(view='three', expr='calm', pose='stand'):
    o = []
    act = pose == 'act'
    lean = 0 if view == 'front' else (14 if view == 'three' else 22)
    # legs: baggy trousers, big shoes
    d = 0 if view == 'front' else 1
    for x in B.pick((-15, 15), (-4, 6), view):
        o.append(B.limb([(x, -104), (x + (2 if d else 0), -50), (x, -10)], 24, 20, TROUS, tex='brush'))
        o.append(B.shoe(x + (6 if d else 0), 0, 1.55, d, SHOE))
    # far arm
    if view != 'front':
        if act:
            pass   # the far hand is behind his back
        else:
            ax = B.pick(-34, -10, view) + lean * 0.8
            o.append(B.limb([(ax + 4, -210), (ax - 2, -170), (ax - 2, -134)], 18, 13, SHIRT, tex='flat'))
            o.append(B.hand(ax - 2, -134, 1.62, 'rest', 1.0, flip=True))
    # the shirt shows at the neck and under the vest
    vp = vest(view, lean)
    o.append(form(vp, VEST, lw=2.4, tex='brush'))
    k = B.pick(1.0, 0.6, view)
    o.append(hatch([(20 * k + lean * 0.6, -205), (42 * k + lean * 0.5, -180), (46 * k + lean * 0.2, -130),
                    (30 * k, -100), (22 * k, -140)], '#2f3a10', angle=-1.2, step=4.0, op=0.45))
    # opening of the vest with buttons, the watch chain
    cx = B.pick(0, 22, view, 0.45) + lean * 0.5
    o.append(form([(cx - 9, -224), (cx + 9, -224), (cx + 2, -176), (cx - 2, -176)], SHIRT, lw=1.8, tex='flat'))
    o.append(ink([(cx, -176), (cx, -100)], 1.6, taper=0.1))
    for by in (-160, -138, -116):
        o.append(form(ell(cx + 4, by, 2.6, 2.6, 8), BRASS, lw=1.2, tex='flat'))
    if not act:
        o.append(ink([(cx + 4, -138), (cx + 18, -128), (cx + 30, -136)], 1.4, taper=0.05, weight=0, color='#8a6512'))
    # head, forward of the body
    hx = B.pick(0, 20, view) + lean
    o.append(place_head(view, expr, hx, -268 + (6 if view == 'side' else 0), -4 if act else 0, 1.12))
    # near arm
    if act and view == 'three':
        # holds the pocket watch up close to his face, squinting at it
        o.append(B.limb([(32, -210), (54, -176), (56, -236)], 18, 13, SHIRT, tex='flat'))
        o.append(B.limb([(55, -196), (56, -236)], 12, 11, K.SKIN, tex='flat'))
        o.append(ink([(cx + 4, -138), (30, -150), (52, -196), (60, -244)], 1.3, taper=0.05, weight=0, color='#8a6512'))
        o.append(watch(64, -256, 11))
        o.append(B.hand(56, -232, -1.4, 'hold', 1.0, flip=True))
    elif view == 'front':
        for sg in (-1, 1):
            o.append(B.limb([(sg * 36, -210), (sg * 48, -170), (sg * 48, -134)], 18, 13, SHIRT, tex='flat'))
            o.append(B.hand(sg * 48, -134, 1.5 if sg > 0 else 1.64, 'rest', 1.0, flip=sg < 0))
    else:
        ax = B.pick(36, 10, view) + lean * 0.8
        o.append(B.limb([(ax - 2, -210), (ax + 6, -170), (ax + 6, -134)], 18, 13, SHIRT, tex='flat'))
        o.append(B.hand(ax + 6, -134, 1.5, 'rest', 1.0))
    return ''.join(o)


def watch(x, y, r):
    s = form(ell(x, y, r, r, 14), BRASS, lw=1.8, tex='brush')
    s += form(ell(x, y, r * 0.75, r * 0.75, 14), '#fbf4df', lw=1.1, tex='flat')
    s += ink([(x, y - r * 0.55), (x, y), (x + r * 0.4, y + r * 0.15)], 1.2, taper=0.2)
    s += form(ell(x, y - r - 2.5, 2.5, 2.5, 8), BRASS, lw=1.1, tex='flat')
    return s
