"""Савелий Петрович, about 70, a watchmaker — grumpy outside, kind inside. A bald dome with white cloud tufts over
big ears, heavy white cloud brows that hang over small dot eyes, a big bulb nose, a walrus moustache that hides the
mouth, round spectacles, a jeweller's loupe pushed up on the forehead. A pear body, a little stooped: rolled shirt
sleeves, a mustard waistcoat with a watch chain, baggy brown trousers, big black shoes.
Head: centre (0,0), radius 64."""
import math
from lib import (INK, LW, LWI, Head, P, blob, line, smooth, circle, ellipse, g, clip, union, eye, mouth, nose,
                 cheek, f, arm, leg)

SKIN = '#f3d2b4'
SKIN_SH = '#dfa98a'
NOSE = '#e8957c'
HAIRW = '#f4f0e6'
HAIRW_SH = '#cfc8b8'
SHIRT = '#f1ead8'
VEST = '#c9952f'
VEST_SH = '#a87a22'
PANTS = '#6b4a35'
SHOE = '#2a221e'
BRASS = '#d9a93a'
R = 64
FEET = 350  # the shoe soles

EXPR = {
    'neutral': dict(look=(.1, .1), lid=.3, brow=-.35, mouth='grumpy'),
    'joy': dict(eye='closed-happy', brow=.25, mouth='smile', blush=1.3),
    'surprise': dict(look=(0, 0), lid=None, brow=.5, browy=-14, mouth='o', glasses_up=True),
    'sad': dict(look=(0, .6), lid=.42, rot=.35, brow=.9, mouth='frown'),
    'angry': dict(look=(0, 0), lid=.45, rot=-.4, brow=-1.0, browy=6, mouth='shout', blush=1.2),
}


def cloud(cx, cy, w, h, n, fill, lw=LW, flip=False):
    """A scalloped cloud of white hair / brow / moustache: n round bumps along the top and outer edge."""
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = math.pi * (1 - t)
        pts.append((cx + math.cos(ang) * w / 2, cy - math.sin(ang) * h / 2))
    d = f'M {f(pts[0][0])} {f(pts[0][1])} '
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = mx - cx, my - cy
        L = math.hypot(nx, ny) or 1
        bump = math.hypot(x1 - x0, y1 - y0) * .55
        d += f'Q {f(mx + nx / L * bump)} {f(my + ny / L * bump)} {f(x1)} {f(y1)} '
    d += f'Q {f(cx)} {f(cy + h * .35)} {f(pts[0][0])} {f(pts[0][1])} Z'
    return P(d, fill, INK, lw)


def moustache(cx, cy, w, fz, droop=0.0, fill=HAIRW):
    """A walrus moustache: one soft mass under the nose, ends drooping, three round lobes along the bottom edge."""
    hw = w / 2 * (.6 + .4 * fz)
    dr = droop * 6
    pts = [(cx, cy - 12), (cx + hw * .55, cy - 13), (cx + hw * .95, cy - 2), (cx + hw * 1.08, cy + 14 + dr),
           (cx + hw * .82, cy + 18 + dr), (cx + hw * .55, cy + 12 + dr * .5), (cx + hw * .3, cy + 17 + dr * .3),
           (cx, cy + 11), (cx - hw * .3, cy + 17 + dr * .3), (cx - hw * .55, cy + 12 + dr * .5), (cx - hw * .82, cy + 18 + dr),
           (cx - hw * 1.08, cy + 14 + dr), (cx - hw * .95, cy - 2), (cx - hw * .55, cy - 13)]
    out = blob(pts, fill, LW, k=.9)
    for side in (-1, 1):
        out += line([(cx + side * hw * .2, cy - 4), (cx + side * hw * .55, cy + 3), (cx + side * hw * .8, cy + 10 + dr)], 1.6, HAIRW_SH)
    return out


def head(a=0.0, expr='neutral'):
    e = EXPR[expr]
    H = Head(R, a)
    s = math.sin(a)
    out = []
    # ears behind
    for side in (-1, 1):
        X, Y, Z, fz = H.project(side * 62, 14, 0)
        if Z > -20:
            sx = side if abs(s) < .9 else (1 if X > 0 else -1)
            out.append(blob([(X, Y - 18), (X + sx * 16, Y - 14), (X + sx * 18, Y + 6), (X + sx * 8, Y + 18), (X - sx * 2, Y + 14)], SKIN))
            out.append(line([(X + sx * 4, Y - 8), (X + sx * 11, Y - 4), (X + sx * 9, Y + 8)], 2))
    # the dome and the jowly lower face
    out.append(union([H.ball(), H.muzzle(36, 62, 46, 40, 22)], SKIN))
    # age: a few lines on the dome and a shine
    X, Y, _, _ = H.project(-14, -52)
    out.append(ellipse(X, Y, 14, 7, '#ffffff', 0, rot=-20, extra='opacity=".45"'))
    for y in (-34, -27):
        out.append(clip(H.ball(), line(H.pts([(-20, y), (0, y - 3), (20, y)]), 1.6, SKIN_SH)))
    # white tufts over the ears
    for side in (-1, 1):
        X, Y, Z, fz = H.project(side * 60, -10, 10)
        if Z > -30:
            out.append(g(cloud(0, 0, 44, 46, 6, HAIRW), X + side * 6, Y + 6, 1, rot=side * 75))
    blush = e.get('blush', 1.0)
    for x in (-40, 40):
        X, Y, Z, fz = H.project(x, 30)
        if fz > .15:
            out.append(cheek(X, Y, 11 * blush * (.5 + .5 * fz), op=.4))
    # eyes: small, dot pupils, under heavy brows
    for side, x in ((-1, -20), (1, 20)):
        X, Y, Z, fz = H.project(x, 2)
        if fz <= .08:
            continue
        out.append(eye(X, Y, 13, 17, look=e.get('look', (0, 0)), fz=fz, kind=e.get('eye', 'dot'), lid=e.get('lid'), rot=e.get('rot', 0),
                       side=side, skin=SKIN, pr=(7, 9)))
        bx, by, _, bfz = H.project(x + side * 4, -12 + e.get('browy', 0))
        t = e['brow']
        out.append(g(cloud(0, 0, 40 * (.5 + .5 * bfz), 26, 4, HAIRW, 2.6), bx, by, 1, rot=side * (t * 18)))
    # round spectacles
    gl = e.get('glasses_up')
    gpos = []
    for side, x in ((-1, -20), (1, 20)):
        X, Y, Z, fz = H.project(x, 10 if not gl else -46)
        if fz > .08:
            gpos.append((X, Y, fz))
            out.append(ellipse(X, Y, 16 * (.4 + .6 * fz), 15, 'none', 2.2, extra='stroke-opacity=".95"'))
            out.append(ellipse(X - 4, Y - 5, 3, 5, '#ffffff', 0, extra='opacity=".7"'))
    if len(gpos) == 2:
        (x1, y1, f1), (x2, y2, f2) = gpos
        out.append(line([(x1 + 16 * (.4 + .6 * f1), y1 - 2), ((x1 + x2) / 2, y1 - 6), (x2 - 16 * (.4 + .6 * f2), y2 - 2)], 2.2))
    # the loupe pushed up on the forehead (unless the glasses went there)
    if not gl:
        X, Y, Z, fz = H.project(16, -46)
        out.append(clip(H.ball(1), line(H.pts([(-64, -40), (-30, -50), (0, -52), (30, -50), (64, -40)]), 4.5, '#3b2e28')))
        out.append(g(blob([(-11, -9), (11, -9), (13, 9), (-13, 9)], '#2f2622', LWI, k=.6) + ellipse(0, 9, 13, 4, '#9fb7b9', LWI)
                     + ellipse(-4, 8, 4, 1.5, '#ffffff', 0), X, Y - 4, 1))
    # nose, moustache, mouth under it
    X, Y, Z, fz = H.project(0, 28, R + 12)
    mk = e['mouth']
    if mk in ('o', 'shout', 'smile', 'frown'):
        MX, MY, _, mfz = H.project(0, 50, R - 6)
        if mk == 'smile':
            out.append(mouth(MX, MY + 4, 34, 'grin', fz=mfz, open_=.7))
        elif mk == 'frown':
            out.append(mouth(MX, MY + 10, 24, 'wobble', fz=mfz))
        else:
            out.append(mouth(MX, MY + 4, 26 if mk == 'o' else 34, mk, fz=mfz, open_=1.1))
    MX, MY, _, mfz = H.project(0, 40, R - 4)
    out.append(moustache(MX, MY, 70, mfz, droop=.6 if mk in ('frown', 'grumpy') else (-.4 if mk == 'smile' else 0)))
    out.append(nose(X, Y, 15, NOSE, kind='bulb', fz=fz, dirx=s))
    # spectacles bridge sits on the nose: drawn after, if worn
    return ''.join(out)


# ---------------------------------------------------------------- the figure
def body(s=0.0, pose='stand'):
    """Shirt, waistcoat over a round belly, trousers; s: turn."""
    out = []
    belly = smooth([(-30 + 4 * s, 96), (-46 + 6 * s, 140), (-50 + 8 * s, 190), (-36 + 10 * s, 228), (0 + 14 * s, 238),
                    (40 + 16 * s, 226), (56 + 16 * s, 186), (50 + 12 * s, 136), (34 + 6 * s, 96), (0 + 6 * s, 90)])
    pants = smooth([(-38 + 10 * s, 210), (-44 + 10 * s, 250), (-42 + 8 * s, 298), (-8 + 8 * s, 300), (2 + 10 * s, 262), (10 + 12 * s, 300),
                    (46 + 14 * s, 298), (48 + 16 * s, 250), (44 + 16 * s, 210)])
    out.append(union([pants], PANTS))
    out.append(line([(2 + 10 * s, 262), (2 + 10 * s, 240)], 2))
    out.append(union([belly], SHIRT))
    # waistcoat: two fronts over the belly, a V at the neck
    vest = smooth([(-26 + 4 * s, 100), (-44 + 6 * s, 140), (-48 + 8 * s, 188), (-34 + 10 * s, 226), (2 + 14 * s, 236), (42 + 16 * s, 224),
                   (55 + 16 * s, 184), (49 + 12 * s, 136), (30 + 6 * s, 100), (14 + 8 * s, 104), (6 + 10 * s, 150), (-4 + 8 * s, 106)])
    out.append(clip(belly, P(vest, VEST, INK, LW)))
    out.append(P(belly, 'none', INK, LW))
    cx = 5 + 10 * s
    out.append(line([(cx, 150), (cx + 2, 232)], 2.2))
    for y in (166, 188, 210):
        out.append(circle(cx + 7, y, 3.2, BRASS, 1.6))
    # watch chain from a button to the pocket
    out.append(line([(cx + 7, 188), (cx + 22, 200), (cx + 36, 194)], 2.2, BRASS))
    out.append(line([(cx + 30, 196), (cx + 44, 196)], 2.4))
    # collar and tie
    out.append(blob([(cx - 14, 96), (cx - 2, 100), (cx - 6, 110)], SHIRT, LWI) + blob([(cx + 14, 96), (cx + 2, 100), (cx + 6, 110)], SHIRT, LWI))
    out.append(blob([(cx - 4, 102), (cx + 4, 102), (cx + 6, 132), (cx, 140), (cx - 6, 132)], '#7a2c24', LWI))
    return ''.join(out)


def figure(view='q', pose='stand', expr='neutral'):
    a = {'front': 0.0, 'q': .55, 'side': 1.25}[view]
    s = math.sin(a)
    out = []
    if view == 'side':
        return figure_side(pose, expr)
    tv = 'front' if view == 'front' else 'side'
    out.append(leg([(-20 + 8 * s, 280), (-22 + 8 * s, 312), (-24 + 6 * s, 328)], 30, 26, 22, PANTS, SHOE, ss=.95, toe=-1 if view == 'front' else 1, view=tv))
    out.append(leg([(26 + 14 * s, 280), (28 + 14 * s, 312), (30 + 16 * s, 328)], 30, 26, 22, PANTS, SHOE, ss=.95, toe=1, view=tv))
    if pose == 'stand':
        out.append(body(s))
        out.append(arm([(-38 + 6 * s, 112), (-56 + 6 * s, 160), (-50 + 6 * s, 208)], 18, SHIRT, 'rest', .85, flip=True))
        out.append(arm([(42 + 12 * s, 112), (60 + 14 * s, 160), (56 + 14 * s, 208)], 18, SHIRT, 'rest', .85))
        out = [f'<g transform="scale({1 - .1 * s:.3f} 1)">' + ''.join(out) + '</g>']
        out.append(g(head(a, expr), 4 + 6 * s, 30))
    elif pose == 'watch':
        # stooped, one hand behind the back, the other holds up a pocket watch to squint at it
        out.append(arm([(-38 + 6 * s, 112), (-58, 160), (-30, 200)], 18, SHIRT, 'rest', .85, flip=True))
        out.append(body(s))
        out.append(g(head(a, expr), 10 + 6 * s, 36, 1, rot=4))
        out.append(line([(118, 118), (112, 150), (80, 186), (50, 194)], 2.2, BRASS))
        out.append(arm([(44 + 12 * s, 112), (96, 168), (116, 132)], 18, SHIRT, 'hold', .85))
        out.append(g(pocketwatch(), 122, 110, 1.15, rot=10))
    # sleeve garters
    return ''.join(out)


def pocketwatch():
    out = circle(0, 0, 17, BRASS, LW) + circle(0, 0, 12.5, '#fbf3df', LWI)
    out += circle(0, -19, 4, BRASS, LWI)
    for i in range(12):
        ang = i * math.pi / 6
        out += line([(math.sin(ang) * 9.5, -math.cos(ang) * 9.5), (math.sin(ang) * 11.5, -math.cos(ang) * 11.5)], 1.2)
    out += line([(0, 0), (0, -8)], 1.8) + line([(0, 0), (6, 2)], 1.8)
    return out


def figure_side(pose='stand', expr='neutral'):
    a = 1.25
    out = []
    out.append(leg([(-4, 280), (-6, 312), (-6, 328)], 30, 26, 22, PANTS, SHOE, ss=.95, toe=1))
    out.append(arm([(-6, 112), (-14, 160), (-10, 206)], 18, '#ddd5c2', 'rest', .85))
    belly = smooth([(-16, 96), (-26, 140), (-24, 200), (-14, 232), (18, 238), (52, 214), (60, 172), (46, 126), (22, 96)])
    pants = smooth([(-22, 210), (-26, 260), (-24, 298), (22, 298), (30, 250), (38, 214)])
    out.append(union([pants], PANTS))
    out.append(leg([(10, 280), (12, 312), (14, 328)], 30, 26, 22, PANTS, SHOE, ss=.95, toe=1))
    out.append(union([belly], SHIRT))
    vest = smooth([(-14, 100), (-24, 140), (-22, 200), (-12, 230), (18, 236), (50, 214), (58, 172), (44, 128), (28, 112)])
    out.append(clip(belly, P(vest, VEST, INK, LW)) + P(belly, 'none', INK, LW))
    out.append(line([(46, 150), (56, 230)], 2.2))
    out.append(line([(54, 186), (40, 200), (24, 194)], 2.2, BRASS))
    out.append(blob([(24, 100), (34, 104), (30, 114)], SHIRT, LWI))
    out.append(arm([(4, 112), (14, 160), (10, 206)], 18, SHIRT, 'rest', .85))
    out.append(g(head(a, expr), 16, 32))
    return ''.join(out)
