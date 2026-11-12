"""Тим, about 8 — mischievous, curious. A big round head with ears that stick out, a ginger tuft with a cowlick,
freckles, a grin; a striped jersey like Boniface's, brick-red shorts, thin legs with scabby knees, striped socks,
a slingshot.
"""
import math
import kit as K
import face as F
import body as B
from kit import form, ink, paint, hatch, ell, arc

NAME = 'Тим'
HEIGHT = 300
HAIR = '#d0702a'
JERSEY = '#f4ecda'
STRIPE = '#2f5f9e'
SHORTS = '#b8432a'
SHOE = '#5a3a24'

HEAD = F.Head(rows=[(-55, 34), (-45, 43), (-25, 48), (0, 48), (18, 44), (30, 36), (38, 23), (42, 9)],
              eye_y=-4, eye_gap=15, eye_r=6.0, nose='button', nose_s=1.2, nose_y=9, mouth_y=24, mouth_w=12,
              brow_y=-17, brow_len=8, brow_lw=3.0, ear=(0, 6, 12), blush_r=9, cheek_y=14, blush_op=0.8,
              prof=dict(nose=-1, chin=-2, jaw=0.5),
              expr={'calm': dict(mouth='smirk', look=(0.5, 0), brow=-2, tilt=-0.25, brow_out=-3),
                    'anger': dict(mouth='teeth', open=0.5)})
HS = 1.2


def freckles(view):
    L = HEAD.layout(view)
    s = ''
    r = K.rng()
    for cx in L['cheeks']:
        for i in range(4):
            s += K.dot(cx + r.uniform(-6, 6), 8 + r.uniform(-3, 4), 0.9, '#9a4a1e')
    return s


def hair(view):
    if view == 'front':
        pts = [(-40, -36), (-44, -52), (-30, -58), (-26, -70), (-12, -62), (-4, -76), (8, -62), (20, -72), (26, -58),
               (42, -54), (40, -36), (28, -46), (10, -40), (-6, -48), (-22, -40)]
    elif view == 'three':
        pts = [(-46, -30), (-52, -48), (-38, -58), (-34, -72), (-18, -62), (-6, -78), (8, -64), (24, -72), (30, -56),
               (46, -48), (44, -32), (32, -42), (14, -38), (-2, -46), (-22, -38), (-32, -28), (-38, -12), (-43, -2),
               (-48, -14)]
    else:
        pts = [(-56, -30), (-58, -48), (-44, -60), (-38, -74), (-22, -64), (-8, -78), (6, -64), (22, -70), (30, -56),
               (44, -44), (36, -38), (20, -46), (2, -46), (-14, -40), (-24, -28), (-32, -8), (-40, 12), (-50, 6),
               (-56, -10)]
    s = form(pts, HAIR, lw=2.2, tex='brush')
    s += ink([(-2, -64), (-8, -82), (2, -90)], 1.8, taper=0.3)       # the cowlick
    return s


def head(view='three', expr='calm'):
    return HEAD.draw(view, expr, hair_front=hair(view), over_face=freckles(view))


def place_head(view, expr, x, y, tilt=0.0, s=HS):
    with K.scaled(K.S() * s):
        h = head(view, expr)
    return '<g transform="translate(%.1f %.1f) rotate(%.1f) scale(%.3f)">%s</g>' % (x, y, tilt, s, h)


# ---------------------------------------------------------------- the figure (feet at 0, crown at -300)
def jersey(view):
    f = [(-24, -176), (0, -179), (24, -176), (34, -164), (30, -132), (30, -100), (0, -96), (-30, -100), (-30, -132),
         (-34, -164)]
    s = [(-12, -176), (6, -179), (16, -176), (22, -164), (24, -132), (22, -100), (4, -96), (-16, -100), (-18, -132),
         (-18, -164)]
    return B.pick(f, s, view)


def shorts(view):
    f = [(-30, -104), (30, -104), (32, -72), (4, -70), (0, -82), (-4, -70), (-32, -72)]
    s = [(-16, -104), (22, -104), (26, -72), (10, -70), (4, -80), (-4, -70), (-20, -72)]
    return B.pick(f, s, view)


def legs(view, act):
    o = []
    if act and view == 'three':
        spec = [((-10, -74), (-16, -38), (-24, -10), -26, 1), ((12, -74), (28, -40), (40, -14), 40, 1)]
    else:
        spec = [((x, -74), (x, -38), (x, -10), x, 0 if view == 'front' else 1) for x in B.pick((-13, 13), (-2, 6), view)]
    for hip, knee, ank, fx, d in spec:
        o.append(B.leg(hip, knee, ank, 9.5))
        o.append(form(ell(knee[0] + 1, knee[1], 3.4, 2.6, 8), '#e9a08a', lw=0, line=False, tex='crayon'))
        sock = B.tube([(ank[0] + (knee[0] - ank[0]) * 0.32, ank[1] + (knee[1] - ank[1]) * 0.32), ank], 10, 9.5)
        o.append(form(sock, '#fbf6ea', lw=1.6, tex='flat'))
        o.append(hatch(sock, STRIPE, angle=0.0, step=5.0, lw=1.6, op=0.9))
        o.append(B.shoe(fx + (4 if d else 0), 0, 1.3, d, SHOE))
    return ''.join(o)


def slingshot(x, y, a=0.0):
    pts = [(0, 0), (0, -16), (-6, -26), (0, -16), (6, -26)]
    c, s = math.cos(a), math.sin(a)
    P = [(x + px * c - py * s, y + px * s + py * c) for px, py in pts]
    return ink([P[0], P[1]], 3.4, taper=0.05) + ink([P[1], P[2]], 3.0, taper=0.1) + ink([P[1], P[4]], 3.0, taper=0.1) + \
        ink([P[2], (x + 0.3 * c * 0 - (-4) * s * 0, P[1][1] + 6), P[4]], 1.0, taper=0, color='#7a3a1a')


def upper(view, expr, act):
    o = []
    # far arm
    if view != 'front':
        if act:
            o.append(B.limb([(-14, -168), (-26, -136), (-34, -112)], 12, 9, JERSEY, tex='flat'))
            o.append(slingshot(-38, -100, -0.5))
            o.append(B.hand(-34, -112, 2.2, 'fist', 0.85, flip=True))
        else:
            ax = B.pick(-30, -8, view)
            o.append(B.limb([(ax + 4, -168), (ax - 2, -136), (ax - 2, -110)], 12, 9, JERSEY, tex='flat'))
            o.append(B.hand(ax - 2, -110, 1.62, 'rest', 0.85, flip=True))
    o.append(form(shorts(view), SHORTS, lw=2.2, tex='brush'))
    jp = jersey(view)
    o.append(paint(jp, JERSEY, 'flat'))
    o.append(hatch(jp, STRIPE, angle=0.02, step=10.0, lw=4.2, op=0.9, jitter=0.05))
    o.append(K.ink(jp, 2.3, closed=True))
    nx = B.pick(0, 6, view)
    o.append(place_head(view, expr, nx + (6 if act else 0), -232, 6 if act else 0))
    if act and view == 'three':
        # reaches forward, pointing at something he has found
        o.append(B.limb([(24, -168), (46, -150), (66, -152)], 12, 9, JERSEY, tex='flat'))
        o.append(hatch(B.tube([(24, -168), (46, -150), (66, -152)], 12, 9), STRIPE, angle=1.3, step=7, lw=3, op=0.85))
        o.append(B.hand(66, -152, -0.15, 'point', 0.95))
    elif view == 'front':
        for sg in (-1, 1):
            o.append(B.limb([(sg * 26, -168), (sg * 36, -136), (sg * 37, -110)], 12, 9, JERSEY, tex='flat'))
            o.append(B.hand(sg * 37, -110, 1.5 if sg > 0 else 1.64, 'rest', 0.85, flip=sg < 0))
    else:
        ax = B.pick(26, 6, view)
        o.append(B.limb([(ax - 2, -168), (ax + 4, -136), (ax + 4, -110)], 12, 9, JERSEY, tex='flat'))
        o.append(B.hand(ax + 4, -110, 1.5, 'rest', 0.85))
    return ''.join(o)


def figure(view='three', expr='calm', pose='stand'):
    act = pose == 'act'
    up = upper(view, expr, act)
    if act and view == 'three':
        up = '<g transform="rotate(12 0 -80) translate(6 6)">%s</g>' % up
    return legs(view, act) + up
