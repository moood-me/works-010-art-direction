"""Кира, about 15 — prickly, closed, defiant, vulnerable underneath. All elbows and knees: a slouch in one curve,
the head down and forward, the look from under the brows and sideways; short choppy dark hair with a long fringe
over one side of the face (both eyes stay visible); a crooked half-smirk. An oversized dark plum hoodie, lime
headphones round the neck, narrow charcoal trousers, heavy boots with lime laces.
"""
import math
import kit as K
import face as F
import body as B
from kit import form, ink, paint, hatch, ell, arc

NAME = 'Кира'
HEIGHT = 420
HAIR = '#221a24'
HOODIE = '#4a2c49'
TROUS = '#2e2c31'
BOOT = '#1c1a1d'
LIME = '#c9e03b'

HEAD = F.Head(rows=[(-56, 29), (-46, 36), (-26, 39), (-4, 38), (16, 32), (29, 24), (38, 14), (44, 5)],
              eye_y=-4, eye_gap=13, eye_r=4.7, nose='button', nose_s=1.1, nose_y=10, mouth_y=26, mouth_w=8,
              brow_y=-14, brow_len=9, brow_lw=3.2, ear=(0, 4, 7), blush_r=6, cheek_y=15, blush_op=0.35,
              prof=dict(nose=-1, chin=0, jaw=0.5),
              expr={'calm': dict(lid=0.38, look=(0.75, -0.1), mouth='smirk', brow=2, tilt=-0.2),
                    'joy': dict(eye='ring', lid=0.3, look=(0.6, 0), mouth='smirk', brow=-2, tilt=0.1),
                    'surprise': dict(open=0.5, brow=-9),
                    'sadness': dict(lid=0.5, look=(0.1, 0.8), tilt=0.5, curve=-0.4),
                    'anger': dict(lid=0.35, look=(0.6, 0), mouth='teeth', open=0.4, brow=5, tilt=-0.7)})


def hair(view):
    """Choppy dark hair; the fringe falls over the far side of the face but leaves both eyes clear."""
    if view == 'front':
        back = [(-34, -58), (0, -66), (34, -58), (44, -36), (44, -6), (40, 14), (34, -10), (-34, -10), (-42, 14),
                (-46, -8), (-46, -36)]
        fr = [(-42, -24), (-38, -50), (-12, -64), (18, -62), (40, -48), (44, -28), (34, -34), (26, -22), (16, -32),
              (4, -22), (-8, -30), (-20, -14), (-30, -2), (-36, 10), (-40, -6)]
    elif view == 'three':
        back = [(-36, -58), (0, -67), (30, -60), (42, -40), (40, -16), (-26, -8), (-34, 10), (-40, 0), (-46, 12),
                (-50, -6), (-52, -30)]
        fr = [(-42, -28), (-34, -52), (-6, -66), (24, -62), (42, -48), (46, -30), (36, -34), (28, -24), (16, -32),
              (6, -24), (-6, -28), (-14, -18), (-20, -4), (-28, 8), (-30, -10)]
    else:
        back = [(-38, -60), (0, -68), (28, -62), (42, -46), (40, -36), (10, -40), (-14, -28), (-30, 0), (-42, 22),
                (-56, 8), (-56, -30)]
        fr = [(-10, -56), (10, -66), (34, -58), (46, -42), (48, -24), (40, -30), (34, -20), (26, -30), (14, -34)]
    s_back = form(back, HAIR, lw=2.2, tex='brush')
    s_fr = form(fr, HAIR, lw=2.2, tex='brush')
    s_fr += ink([(0, -56), (-12, -36), (-20, -16)], 1.2, taper=0.4, color='#6c5a6a', weight=0)
    if view == 'side':
        return '', s_back + s_fr
    return s_back, s_fr


def head(view='three', expr='calm'):
    b, f = hair(view)
    return HEAD.draw(view, expr, hair_back=b, hair_front=f)


def place_head(view, expr, x, y, tilt=0.0, s=1.05):
    with K.scaled(K.S() * s):
        h = head(view, expr)
    return '<g transform="translate(%.1f %.1f) rotate(%.1f) scale(%.3f)">%s</g>' % (x, y, tilt, s, h)


# ---------------------------------------------------------------- the figure (feet at 0, crown near -420)
def hoodie(view, slouch):
    # an oversized bag: shoulders drop, the hem bunches at the hips
    f = [(-20, -326), (20, -326), (44, -312), (48, -270), (44, -200), (46, -168), (24, -160), (0, -158), (-24, -160),
         (-46, -168), (-44, -200), (-48, -270), (-44, -312)]
    s = [(-14, -328), (14, -326), (30, -312), (36, -270), (32, -200), (34, -168), (16, -160), (0, -158), (-16, -160),
         (-30, -168), (-30, -200), (-40, -270), (-36, -312)]
    p = B.pick(f, s, view)
    # slouch: the top goes forward (right) and down, the back rounds
    out = []
    for x, y in p:
        t = max(0.0, (-158 - y) / 170)
        out.append((x + slouch * t * t * 30, y + slouch * t * 8))
    return out


def hood(view, slouch):
    dx = slouch * 30
    if view == 'front':
        pts = [(-26, -330), (-20, -346), (0, -340), (20, -346), (26, -330), (14, -318), (0, -322), (-14, -318)]
    elif view == 'three':
        pts = [(-34, -324), (-34, -348), (-14, -350), (6, -338), (18, -322), (0, -318), (-20, -312)]
    else:
        pts = [(-36, -320), (-40, -346), (-20, -354), (0, -340), (8, -324), (-10, -316), (-28, -312)]
    return [(x + dx, y + slouch * 8) for x, y in pts]


def headphones(view, slouch):
    dx, dy = slouch * 30, slouch * 8
    if view == 'front':
        cups = [(-17, -326), (17, -326)]
        band = [(-17, -326), (0, -312), (17, -326)]
    elif view == 'three':
        cups = [(-16, -328), (16, -322)]
        band = [(-16, -328), (2, -312), (16, -322)]
    else:
        cups = [(6, -322)]
        band = [(-8, -330), (6, -312)]
    s = ink([(x + dx, y + dy) for x, y in band], 3.0, taper=0.05, color=LIME, weight=0)
    s += ink([(x + dx, y + dy) for x, y in band], 1.0, taper=0.05)
    for x, y in cups:
        s += form(ell(x + dx, y + dy, 8, 9.5, 10, rot=0.3), LIME, lw=1.9, tex='brush')
        s += form(ell(x + dx, y + dy, 3.6, 4.2, 8, rot=0.3), '#2b2d18', lw=1.0, tex='flat', off=False)
    return s


def boot(x, y, d):
    s = B.shoe(x, y, 1.45, d, BOOT, kind='boot' if d else 'shoe')
    if d:
        s += ink([(x + 1, y - 18), (x + 8, y - 15)], 1.6, color=LIME, weight=0, taper=0.1)
        s += ink([(x + 2, y - 12), (x + 9, y - 10)], 1.6, color=LIME, weight=0, taper=0.1)
    else:
        s += ink([(x - 4, y - 6), (x + 4, y - 7)], 1.6, color=LIME, weight=0, taper=0.1)
    return s


def figure(view='three', expr='calm', pose='stand'):
    o = []
    act = pose == 'act'
    slouch = 0.0 if view == 'front' else (0.7 if not act else 1.0)
    d = 0 if view == 'front' else 1
    # legs: long, narrow, knees that show
    if act and view == 'three':
        legs = [((-14, -166), (-6, -86), (-14, -12), -14), ((12, -166), (-2, -88), (20, -14), 22)]
    else:
        legs = [((x, -166), (x, -86), (x, -12), x) for x in B.pick((-13, 13), (-4, 6), view)]
    for hip, knee, ank, fx in legs:
        o.append(B.limb([hip, knee, ank], 17, 13, TROUS, tex='brush'))
        o.append(boot(fx + (4 if d else 0), 0, d))
    # far arm
    if act and view == 'three':
        # arms crossed tight over the chest: «не трогайте меня»
        o.append(B.limb([(-20, -306), (-34, -250), (24, -262)], 18, 15, HOODIE))
    elif view != 'front':
        sx = -28 + slouch * 24
        o.append(B.limb([(sx, -308), (sx - 10, -250), (sx - 6, -192)], 18, 15, HOODIE))
        o.append(B.hand(sx - 6, -188, 1.7, 'rest', 0.9, flip=True))
    hp = hoodie(view, slouch)
    o.append(paint(hood(view, slouch), HOODIE, 'brush'))
    o.append(K.ink(hood(view, slouch), 2.0, closed=True))
    o.append(form(hp, HOODIE, lw=2.4, tex='brush'))
    k = B.pick(1.0, 0.75, view)
    o.append(hatch([(30 * k + slouch * 20, -300), (44 * k + slouch * 16, -270), (42 * k, -200), (44 * k, -168),
                    (26 * k, -166), (30 * k, -240)], '#1a0c1a', angle=-1.2, step=4.0, op=0.5))
    # the pocket and the strings
    if view != 'side':
        px = B.pick(0, 14, view)
        o.append(ink([(px - 26, -196), (px - 18, -220), (px + 18, -220), (px + 26, -196)], 1.6, taper=0.1))
        sx = px + slouch * 22
        o.append(ink([(sx - 6, -316), (sx - 8, -276)], 1.2, color='#d8cbd4', weight=0))
        o.append(ink([(sx + 5, -316), (sx + 6, -282)], 1.2, color='#d8cbd4', weight=0))
    # neck, head down and forward, headphones
    nx = B.pick(0, 6, view) + slouch * 30
    o.append(form([(nx - 5, -346), (nx + 5, -346), (nx + 6, -322), (nx - 6, -322)], K.SKIN, lw=1.7, tex='flat'))
    o.append(headphones(view, slouch))
    o.append(place_head(view, expr, nx + slouch * 6, -366 + slouch * 12, 8 * slouch, 1.05))
    if act and view == 'three':
        o.append(B.hand(26, -262, 0.1, 'rest', 0.85))
        o.append(B.limb([(40 + slouch * 16, -306), (56, -252), (-4, -268)], 18, 15, HOODIE))
        o.append(B.hand(-4, -268, 3.0, 'rest', 0.85, flip=True))
    elif view == 'front':
        for sg in (-1, 1):
            o.append(B.limb([(sg * 40, -308), (sg * 50, -250), (sg * 48, -192)], 18, 15, HOODIE))
            o.append(B.hand(sg * 48, -188, 1.5 if sg > 0 else 1.64, 'rest', 0.9, flip=sg < 0))
    else:
        sx = B.pick(36, 10, view) + slouch * 22
        o.append(B.limb([(sx, -308), (sx + 6, -250), (sx + 2, -192)], 18, 15, HOODIE))
        o.append(B.hand(sx + 2, -188, 1.62, 'rest', 0.9))
    return ''.join(o)
