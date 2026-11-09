"""Кира, about 15 — prickly, closed, defiant; vulnerable underneath. Thin and angular, long hose arms and legs, a
slouch: the head pushed forward and down, the look sideways from under low straight brows. A longer, narrower face
than a child's, eyes smaller than Аня's with a dark upper lid, a small nose, a mouth pressed shut and a little crooked
— she never smiles openly, at most one corner goes up. Short choppy dark hair with tufts sticking out, a long jagged
fringe over one eye. An oversized dark-plum hoodie, acid-lime headphones round the neck, narrow charcoal trousers,
heavy boots with lime laces.
Head: centre (0,0), radius 60."""
import math
from lib import (INK, LW, LWI, WHITE, Head, P, blob, line, tline, smooth, circle, ellipse, g, clip, union, hose,
                 eye, brow, mouth, nose, cheek, f, arm, leg)

SKIN = '#f3dcc8'
SKIN_SH = '#deb39a'
HAIR = '#2e2434'
HAIR_HI = '#5d4c6c'
HOOD = '#5a3158'
HOOD_SH = '#43233f'
PANTS = '#3d3b45'
BOOT = '#28242b'
ACID = '#c8e03a'
PAD = '#2f2b33'
STRING = '#e9e1d0'
R = 60
FEET = 412  # the boot soles
HS = .92    # the head in the figure: a teenager's head is smaller against the body than a child's

EXPR = {
    'neutral': dict(look=(.8, .1), lid=.36, rot=-.14, brow=(-.45, -.45), mouth='pressed'),
    # her joy: one corner of the mouth, the lids soften — and she looks away
    'joy': dict(look=(.7, -.2), lid=.24, rot=.08, brow=(.1, .35), mouth='smirk', blush=1.6),
    'surprise': dict(eye='spark', look=(0, 0), brow=(.5, .5), browy=-9, mouth='o'),
    'sad': dict(look=(-.3, .8), lid=.46, rot=.34, brow=(.9, .9), mouth='wobble', blush=1.2),
    'angry': dict(look=(.2, .1), lid=.4, rot=-.5, brow=(-1.2, -1.2), browy=7, mouth='teeth', blush=1.5),
}


def tuft(x, y, ang, ln=22, w=10):
    """A choppy lock: a pointed blade from (x, y) outwards."""
    return g(blob([(-w, 2), (-w * .5, -ln * .5), (0, -ln), (w * .6, -ln * .45), (w, 2)], HAIR, LW, k=.8), x, y, 1, rot=ang)


def head(a=0.0, expr='neutral'):
    e = EXPR[expr]
    H = Head(R, a)
    s = math.sin(a)
    out = []
    grow = 6
    # choppy ends sticking out behind the jaw line: both sides from the front, the back of the head when turned
    rr = R + grow - 6
    left = [(195, 150), (175, 132), (155, 116), (137, 104)]           # (angle on the ring, the lock's direction), degrees
    right = [(180 - t, 180 - d) for t, d in left]
    locks = left + ([(118, 96), (212, 168)] if s > .3 else right)
    for t, d in locks:
        tr = math.radians(t)
        out.append(tuft(math.cos(tr) * rr, math.sin(tr) * rr, d + 90))
    # the face: a narrower ball with a longer lower face and a small chin
    face = [H.ball(), H.muzzle(40, 45, 47, 38, 20)]
    out.append(union(face, SKIN))
    blush = e.get('blush', 1.0)
    for x in (-36, 36):
        X, Y, Z, fz = H.project(x, 34)
        if fz > .15:
            out.append(cheek(X, Y, 8 * blush * (.5 + .5 * fz), op=.3))
    for side, x in ((-1, -18), (1, 18)):
        X, Y, Z, fz = H.project(x, 8)
        if fz <= .08:
            continue
        kind = e.get('eye', 'ring')
        out.append(eye(X, Y, 14.5, 19, look=e.get('look', (0, 0)), fz=fz, kind=kind, lid=e.get('lid'), rot=e.get('rot', 0),
                       side=side, heavy=.34 if kind == 'ring' else 0, lash=1, skin=SKIN, pr=(8.5, 10.5)))
        bx, by, _, bfz = H.project(x + side * 2, -15 + e.get('browy', 0))
        t = e['brow'][0 if side < 0 else 1]
        out.append(brow(bx, by, 25 * (.4 + .6 * bfz), tilt=t, arch=.04, th=6, side=side))
    X, Y, Z, fz = H.project(0, 36, R + 5)
    out.append(nose(X, Y, 5.2, SKIN_SH, fz=fz, dirx=s))
    X, Y, Z, fz = H.project(2, 58, R - 8)
    mk = e['mouth']
    hw = 11 * (.55 + .45 * fz)
    if mk == 'pressed':   # shut tight, one corner pulled down
        out.append(tline([(X - hw, Y - 1), (X, Y), (X + hw, Y + 2.5)], 2, 4.2, w2=2.4))
        out.append(line([(X + hw, Y + 1), (X + hw + 2.5, Y + 6)], 2))
    elif mk == 'smirk':   # the crooked half-smile
        out.append(tline([(X - hw, Y + 1.5), (X, Y + 2.5), (X + hw + 2, Y - 5)], 2, 4.2, w2=2.2))
        out.append(line([(X + hw + 5, Y - 11), (X + hw + 1, Y - 4)], 2))
    elif mk == 'teeth':   # clenched
        d = smooth([(X - hw - 2, Y - 3), (X, Y - 5), (X + hw + 2, Y - 3), (X + hw, Y + 7), (X, Y + 8), (X - hw, Y + 7)], True, .8)
        out.append(P(d, WHITE, INK, LWI + .3) + line([(X - hw - 1, Y + 2), (X + hw + 1, Y + 2)], 1.6)
                   + ''.join(line([(X + k * hw * .5, Y - 4), (X + k * hw * .5, Y + 7)], 1.3) for k in (-1, 0, 1)))
    else:
        out.append(mouth(X, Y, 18 if mk == 'o' else 20, mk, fz=fz))
    # hair: a short choppy cap, the hairline in jags
    hl = [(-55, 28), (-56, 4), (-50, -10), (-46, -4), (-40, -22), (-33, -16), (-26, -32), (-18, -30), (-10, -40), (6, -44), (24, -42),
          (40, -34), (52, -18), (57, 4), (56, 28), (62, 50), (40, 96), (0, 110), (-40, 96), (-62, 50)]
    out.append(H.cap(hl, HAIR, grow=grow))
    # the long fringe: from the parting it falls in three blades over the far eye
    fr = [(-22, -52), (4, -57), (32, -50), (52, -32), (59, -6), (54, 14), (46, 31), (39, 10), (31, 25), (24, 6), (15, 20), (8, -4),
          (-2, -22), (-14, -34)]
    if s > .8:   # in profile the far-side blades are out of sight: only a short bang is left over the brow
        fr = [(x, y if y < -14 else -14 + (y + 14) * .2) for x, y in fr]
    fp = H.pts(fr)
    out.append(blob(fp, HAIR, LW, k=.75))
    hi = line(H.pts([(-6, -46), (18, -40), (36, -22), (42, 2)]), 2.4, HAIR_HI) + line(H.pts([(-30, -58), (-44, -44), (-50, -28)]), 2.4, HAIR_HI)
    out.append(clip(H.ball(grow), hi))
    return ''.join(out)


# ---------------------------------------------------------------- the figure
def sway(y, k):
    """The slouch as a sideways shift down the body: shoulders back, hips forward (k: how much)."""
    pts = ((112, -12), (170, -16), (250, 10), (330, 8), (400, 0))
    if y <= pts[0][0]:
        return pts[0][1] * k
    for (y0, d0), (y1, d1) in zip(pts, pts[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            return (d0 + (d1 - d0) * t) * k
    return 0


def hoodie(s=0.0, k=0.0):
    """The oversized hoodie: a slumped bell with a ribbed hem, a kangaroo pocket, drawstrings; the hood bunched
    behind the neck is drawn by the figure."""
    w = lambda x, y: (x + sway(y, k), y)
    out = []
    body = smooth([w(-27 + 5 * s, 114), w(-38 + 5 * s, 150), (-45 + 7 * s + sway(205, k), 205), w(-46 + 8 * s, 246), w(-20 + 9 * s, 258),
                   w(22 + 9 * s, 258), w(48 + 10 * s, 246), w(45 + 9 * s, 205), w(37 + 7 * s, 150), w(27 + 6 * s, 114), w(2 + 6 * s, 108)])
    out.append(union([body], HOOD))
    out.append(clip(body, line([w(-48 + 8 * s, 240), w(0 + 9 * s, 250), w(50 + 10 * s, 240)], 2.2)))
    cx = 2 + 9 * s
    pocket = [w(cx - 22, 200), w(cx + 22, 200), w(cx + 32, 238), w(cx - 32, 238)]
    out.append(blob(pocket, HOOD, LWI + .4, k=.5))
    out.append(line([w(cx - 24, 204), w(cx - 30, 222)], 3.2, HOOD_SH) + line([w(cx + 24, 204), w(cx + 30, 222)], 3.2, HOOD_SH))
    for dx, ln in ((-7, 42), (8, 34)):
        x0, y0 = w(cx + dx - 2 * s, 118)
        out.append(line([(x0, y0), (x0 + dx * .2, y0 + ln * .6), (x0 + dx * .1, y0 + ln)], 2.6, STRING)
                   + circle(x0 + dx * .1, y0 + ln + 2, 2.6, STRING, 1.2))
    return ''.join(out)


def hood(x, y):
    return (blob([(x - 36, y + 6), (x - 30, y - 12), (x - 6, y - 20), (x + 22, y - 16), (x + 36, y), (x + 30, y + 14), (x - 28, y + 16)], HOOD, LW)
            + line([(x - 24, y - 4), (x - 2, y - 10), (x + 22, y - 6)], 2.2, HOOD_SH))


def phones(x, y, s=0.0, side=False):
    """Headphones worn round the neck: the band goes behind, a cup lies on each collarbone."""
    out = ''
    cups = ((x - 23, y, 12.5, 16, -12), (x + 23 + 3 * s, y + 1, 12.5 - 3 * s, 16, 12)) if not side else ((x + 4, y, 12.5, 16, -8),)
    for cx, cy, rx, ry, rot in cups:
        out += ellipse(cx, cy, rx, ry, ACID, LW, rot=rot) + ellipse(cx + (1 if cx > x else -1) * 0, cy + 1, rx * .55, ry * .6, PAD, LWI, rot=rot)
    return out


def band(x, y, s=0.0, side=False):
    """The headband's arc behind the neck (drawn before the neck and the head)."""
    if side:
        return hose([(x + 4, y - 8), (x - 12, y - 18), (x - 18, y - 6)], 7, ACID)
    return hose([(x - 23, y - 8), (x - 14, y - 22), (x + 2 * s, y - 26), (x + 16 + 3 * s, y - 22), (x + 23 + 3 * s, y - 8)], 7, ACID)


def boot(x, y, ss, view, toe=1):
    """Lime laces on the heavy boot: shaft above the big shoe."""
    out = hose([(x, y - 30), (x, y - 2)], 23, BOOT)
    k = 0 if view == 'front' else toe
    for i in range(3):
        yy = y - 25 + i * 8
        out += line([(x - 5 + 6 * k, yy), (x + 6 + 5 * k, yy + 2)], 2.2, ACID)
    return out


def legs(pts_far, pts_near, tv, toe_far=1):
    out = ''
    for pts, toe in ((pts_far, toe_far), (pts_near, 1)):
        x, y = pts[-1]
        out += leg(pts, 16, 15, 13, PANTS, BOOT, sole='#57525c', ss=.95, toe=toe, view=tv) + boot(x, y, .95, tv, toe)
    return out


def figure(view='q', pose='stand', expr='neutral'):
    a = {'front': 0.0, 'q': .55, 'side': 1.25}[view]
    s = math.sin(a)
    if view == 'side':
        return figure_side(pose, expr)
    tv = 'front' if view == 'front' else 'side'
    out = []
    if pose == 'stand':
        k = .5 if view == 'q' else 0
        hx = 9 * s + (8 if view == 'q' else 0)
        out.append(legs([(-14 + 7 * s + sway(250, k), 250), (-17 + 7 * s, 320), (-16 + 6 * s, 390)],
                        [(16 + 10 * s + sway(250, k), 250), (19 + 10 * s, 320), (18 + 12 * s, 390)], tv, -1 if view == 'front' else 1))
        out.append(hood(2 + 6 * s + sway(112, k), 108))
        out.append(band(2 + 7 * s + sway(112, k), 112, s))
        out.append(hose([(hx, 56), (2 + 7 * s + sway(112, k), 114)], 12, SKIN))
        out.append(hoodie(s, k))
        out.append(arm([(-31 + 5 * s + sway(120, k), 122), (-46 + 5 * s + sway(180, k), 180), (-41 + 6 * s + sway(240, k), 240)], 19, HOOD, 'rest', .7, flip=True))
        out.append(arm([(31 + 7 * s + sway(120, k), 122), (47 + 8 * s + sway(180, k), 180), (44 + 9 * s + sway(240, k), 240)], 19, HOOD, 'rest', .7))
        out.append(phones(2 + 7 * s + sway(112, k), 112, s))
        out.append(g(head(a, expr), hx, 8, HS, rot=5 * s * 2))
    elif pose == 'sulk':
        # the slouch: head forward and down, the back rounded, hips forward, knees slack; one hand deep in the pocket,
        # the other hanging in a fist out of a sleeve too long; weight on the back leg, the front foot set out
        k = 1.0
        hx = 24
        out.append(legs([(-12 + 7 * s + sway(250, k), 250), (-8, 322), (-24, 390)],
                        [(16 + 10 * s + sway(250, k), 250), (44, 318), (38, 390)], tv))
        out.append(arm([(31 + 7 * s + sway(120, k), 124), (62, 184), (61, 240)], 19, HOOD, 'fist', .7))
        out.append(hood(-4 + 6 * s + sway(112, k), 108))
        out.append(band(2 + 7 * s + sway(112, k), 113, s))
        out.append(hose([(hx - 3, 60), (2 + 7 * s + sway(112, k), 116)], 12, SKIN))
        out.append(hoodie(s, k))
        cx = 2 + 9 * s
        # the near arm: down into the pocket, the hand hidden to the wrist
        out.append(hose([(-31 + 5 * s + sway(120, k), 124), (-56, 186), (cx - 20 + sway(220, k), 226)], 19, HOOD))
        out.append(blob([(cx - 30 + sway(205, k), 206), (cx - 10 + sway(205, k), 204), (cx + 4 + sway(236, k), 238), (cx - 34 + sway(236, k), 240)], HOOD, LWI + .4, k=.5))
        out.append(line([(cx - 27 + sway(210, k), 208), (cx - 12 + sway(210, k), 206)], 3.2, HOOD_SH))
        out.append(phones(2 + 7 * s + sway(112, k), 113, s))
        out.append(g(head(a, expr), hx, 14, HS, rot=10))
    return ''.join(out)


def figure_side(pose='stand', expr='neutral'):
    a = 1.25
    k = .8
    out = []
    out.append(leg([(2 + sway(250, k), 250), (0, 320), (0, 390)], 16, 15, 13, '#33313a', BOOT, sole='#57525c', ss=.95, toe=1) + boot(0, 390, .95, 'side'))
    out.append(arm([(0 + sway(120, k), 122), (-4 + sway(180, k), 180), (2 + sway(240, k), 240)], 19, HOOD_SH, 'rest', .7))
    out.append(hood(-16 + sway(112, k), 110))
    out.append(band(2 + sway(112, k), 113, 0, side=True))
    out.append(hose([(26, 56), (6 + sway(112, k), 116)], 12, SKIN))
    out.append(leg([(8 + sway(250, k), 250), (12, 320), (12, 390)], 16, 15, 13, PANTS, BOOT, sole='#57525c', ss=.95, toe=1) + boot(12, 390, .95, 'side'))
    w = lambda x, y: (x + sway(y, k), y)
    body = smooth([w(-14, 114), w(-24, 150), w(-28, 205), w(-28, 246), w(0, 258), w(30, 246), w(32, 205), w(26, 150), w(20, 116), w(4, 108)])
    out.append(union([body], HOOD))
    out.append(clip(body, line([w(-30, 240), w(0, 250), w(32, 240)], 2.2)))
    out.append(blob([w(8, 200), w(30, 202), w(32, 236), w(2, 238)], HOOD, LWI + .4, k=.5))
    out.append(line([w(18 + sway(0, 0), 118), w(20, 150)], 2.6, STRING))
    out.append(arm([(4 + sway(120, k), 122), (10 + sway(180, k), 180), (8 + sway(240, k), 240)], 19, HOOD, 'rest', .7))
    out.append(phones(2 + sway(112, k), 113, 0, side=True))
    out.append(g(head(a, expr), 30, 10, HS, rot=10))
    return ''.join(out)
