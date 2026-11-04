"""Аня, about 20 — warm, trusting, dreamy. A round ball head with full cheeks and a small chin, big tall eyes set close
with a heavy upper lid and three lashes, a little button nose, small red lips; an auburn wavy bob with rolled curl
tips and a red bow. A polka-dot dress with puff sleeves, thin hose arms in gloves, shapely hose legs, Mary-Jane shoes.
Head: centre (0,0), radius 70. Figure: feet at y≈FEET."""
import math
from lib import (INK, LW, LWI, WHITE, Head, P, blob, line, smooth, circle, g, clip, union, hose, eye, brow,
                 mouth, nose, cheek, arm, leg)

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
FEET = 423  # the shoe soles

EXPR = {
    'neutral': dict(eye='ring', look=(.15, -.55), lid=.18, brow=0.15, mouth='lips-smile'),
    'joy': dict(eye='closed-happy', brow=-.05, mouth='grin', open_=.9, blush=1.3),
    'surprise': dict(eye='spark', look=(0, 0), brow=.15, browy=-12, mouth='lips-o'),
    'sad': dict(eye='ring', look=(0, .5), lid=.34, rot=.32, brow=.85, mouth='lips-frown', tear=True),
    'angry': dict(eye='ring', look=(0, .1), lid=.4, rot=-.6, brow=-1.3, browy=10, mouth='shout', open_=.8, blush=1.4),
}


def head(a=0.0, expr='neutral'):
    e = EXPR[expr]
    H = Head(R, a)
    s = math.sin(a)
    c = math.cos(a)
    out = []
    # back hair: a full bob behind the head, curls rolled under at jaw level
    back = [(-70, -40), (-80, 6), (-88, 50), (-84, 82), (-62, 94), (-36, 82), (36, 82), (62, 94), (84, 82), (88, 50),
            (80, 6), (70, -40)]
    back = [(x * (.75 + .25 * c) - 18 * s, y) for x, y in back]
    out.append(blob(back, HAIR))
    for cx in (-70 * (.75 + .25 * c) - 18 * s, 70 * (.75 + .25 * c) - 18 * s):
        out.append(line([(cx - 11, 84), (cx, 76), (cx + 10, 84)], 2.4, HAIR_HI))
    # the face: a ball with full cheeks and a small round chin
    out.append(union([H.ball(), H.muzzle(40, 62, 46, 46, 24)], SKIN))
    blush = e.get('blush', 1.0)
    for x in (-44, 44):
        X, Y, Z, fz = H.project(x, 38)
        if fz > .15:
            out.append(cheek(X, Y, 12 * blush * (.5 + .5 * fz), op=.45))
    # eyes: big, tall, nearly touching; heavy upper lid with three lashes
    for side, x in ((-1, -22), (1, 22)):
        X, Y, Z, fz = H.project(x, 6)
        if fz <= .08:
            continue
        out.append(eye(X, Y, 20, 29, look=e.get('look', (0, 0)), fz=fz, kind=e['eye'], lid=e.get('lid'), rot=e.get('rot', 0),
                       lash=3, side=side, heavy=.4 if e['eye'] not in ('closed-happy', 'closed') else 0, skin=SKIN))
        bx, by, _, bfz = H.project(x + side * 3, -38 + e.get('browy', 0))
        out.append(brow(bx, by, 24 * (.4 + .6 * bfz), tilt=e['brow'], th=3.6, side=side))
    if e.get('tear'):
        X, Y, _, _ = H.project(32, 34)
        out.append(blob([(X, Y - 8), (X + 6, Y + 4), (X, Y + 9), (X - 6, Y + 4)], '#bfe0ee', 2))
    # nose and mouth
    X, Y, Z, fz = H.project(0, 40)
    out.append(nose(X, Y, 6, SKIN_SH, fz=fz, dirx=s))
    X, Y, Z, fz = H.project(0, 60)
    out.append(mouth(X, Y, 22 if e['mouth'].startswith('lips') else 30, e['mouth'], fz=fz, open_=e.get('open_', 1), skin=SKIN))
    # hair over the skull: a side part on the left, a soft wave rolling over the forehead
    face_loop = [(-62, 24), (-64, 4), (-56, -18), (-44, -34), (-30, -40), (-20, -36), (-8, -46), (8, -52), (24, -50),
                 (40, -42), (54, -30), (63, -12), (64, 14), (66, 50), (40, 96), (0, 110), (-40, 96), (-66, 50)]
    out.append(H.cap(face_loop, HAIR, grow=10))
    ring = f'M {-R - 9} 0 A {R + 9} {R + 9} 0 1 1 {R + 9} 0 A {R + 9} {R + 9} 0 1 1 {-R - 9} 0 Z'
    for pts in ([(-6, -86), (-14, -70), (-16, -58)], [(22, -84), (34, -70), (40, -58)], [(-40, -76), (-50, -62), (-52, -48)]):
        out.append(clip(ring, line(H.loop(pts), 2.4, HAIR_HI)))
    # the bow on top, toward the near side
    bx = H.project(30, -60, 40)[0]
    by = -math.sqrt(max(80 ** 2 - bx ** 2, 0)) + 16
    out.append(g(blob([(-4, -6), (-24, -20), (-29, 0), (-22, 13), (-4, 6)], BOW) + blob([(4, -6), (24, -20), (29, 0), (22, 13), (4, 6)], BOW)
                 + circle(0, 0, 7.5, BOW) + line([(-19, -6), (-8, -1)], 1.6) + line([(19, -6), (8, -1)], 1.6), bx, by, 1, rot=16 + bx * .3))
    return ''.join(out)


# ---------------------------------------------------------------- the figure
def dots(d_shape, ox=0, step=26, r=5.2):
    """Polka dots clipped into a dress shape."""
    out = []
    for j in range(-2, 16):
        for i in range(-5, 6):
            x = ox + i * step + (step / 2 if j % 2 else 0)
            y = 90 + j * step * .86
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{DOT}"/>')
    return clip(d_shape, ''.join(out))


def dress(s=0.0, swing=0.0):
    """Bodice, puff sleeves are drawn with the arms; skirt a bell with a soft wavy hem. s: turn (0 front, ~.6 3/4)."""
    sk = 14 * swing
    bod = smooth([(-27 + 6 * s, 112), (-31 + 6 * s, 138), (-22 + 8 * s, 170), (22 + 8 * s, 170), (31 + 6 * s, 138), (27 + 6 * s, 112),
                   (0 + 8 * s, 104)])
    skirt = smooth([(-22 + 8 * s, 166), (-38 + 6 * s, 205), (-60 + 6 * s - sk, 258), (-38 + 4 * s - sk, 268), (-14 + 6 * s - sk, 262),
                    (10 + 6 * s - sk, 270), (36 + 8 * s - sk, 264), (62 + 10 * s - sk, 258), (40 + 10 * s, 205), (22 + 8 * s, 166)])
    out = union([skirt, bod], DRESS)
    out += dots(skirt + ' ' + bod, ox=8 * s)
    out += P(skirt, 'none', INK, LW) + P(bod, 'none', INK, LW)
    # skirt folds
    out += line([(-8 + 7 * s - sk * .5, 200), (-14 + 6 * s - sk, 260)], 2) + line([(18 + 8 * s - sk * .5, 200), (26 + 8 * s - sk, 262)], 2)
    # belt and collar
    out += blob([(-23 + 8 * s, 164), (23 + 8 * s, 164), (24 + 8 * s, 176), (-24 + 8 * s, 176)], BOW, LWI + .5, k=.6)
    cx = 8 * s
    out += blob([(cx - 2, 104), (cx - 28 + 4 * s, 108), (cx - 24 + 4 * s, 124), (cx - 4, 120), (cx, 112)], DOT, LWI + .5)
    out += blob([(cx + 2, 104), (cx + 28 + 4 * s, 108), (cx + 24 + 4 * s, 124), (cx + 4, 120), (cx, 112)], DOT, LWI + .5)
    return out


def puff(x, y, r=15):
    return blob([(x - r, y), (x - r * .7, y - r * .8), (x, y - r), (x + r * .8, y - r * .7), (x + r, y + r * .1), (x + r * .5, y + r * .9),
                 (x - r * .6, y + r * .85)], DRESS) + clip(smooth([(x - r, y), (x - r * .7, y - r * .8), (x, y - r), (x + r * .8, y - r * .7),
                                                                     (x + r, y + r * .1), (x + r * .5, y + r * .9), (x - r * .6, y + r * .85)]),
                                                              f'<circle cx="{x - 4}" cy="{y - 3}" r="4.5" fill="{DOT}"/><circle cx="{x + 7}" cy="{y + 6}" r="4.5" fill="{DOT}"/>')


def figure(view='q', pose='stand', expr='neutral'):
    """view: 'front', 'q' (three-quarter, turned to the viewer's right), 'side' (profile facing right)."""
    a = {'front': 0.0, 'q': .55, 'side': 1.25}[view]
    s = math.sin(a)
    out = []
    if view == 'side':
        return figure_side(pose, expr)
    if pose == 'stand':
        # straight, weight even, arms hanging in soft arcs
        out.append(leg([(-15 + 6 * s, 250), (-14 + 6 * s, 330), (-19 + 4 * s, 404)], 32, 24, 12, SKIN, SHOE, ss=.8, toe=-1 if view == 'front' else 1,
                       view='front' if view == 'front' else 'side'))
        out.append(leg([(16 + 8 * s, 250), (15 + 8 * s, 330), (21 + 10 * s, 404)], 32, 24, 12, SKIN, SHOE, ss=.8, toe=1,
                       view='front' if view == 'front' else 'side'))
        out.append(hose([(0 + 8 * s, 70), (0 + 8 * s, 112)], 15, SKIN))
        out.append(dress(s))
        out.append(arm([(-30 + 6 * s, 120), (-46 + 4 * s, 160), (-44 + 4 * s, 206)], 14, SKIN, 'rest', .72, flip=True))
        out.append(arm([(32 + 8 * s, 120), (48 + 8 * s, 160), (46 + 8 * s, 206)], 14, SKIN, 'rest', .72))
        out.append(puff(-30 + 6 * s, 118))
        out.append(puff(31 + 8 * s, 118))
        out = [f'<g transform="scale({1 - .1 * s:.3f} 1)">' + ''.join(out) + '</g>']
        out.append(head(a, expr))
    elif pose == 'dream':
        # weight on the far leg, the near foot kicked up behind; a daisy held up to the cheek, head tipped
        out.append(leg([(10 + 8 * s, 246), (6 + 8 * s, 296), (-22, 318), (-50, 294)], 32, 24, 14, SKIN, SHOE, ss=.8, toe=-1))
        out.append(leg([(-8 + 6 * s, 250), (-4 + 6 * s, 330), (2 + 6 * s, 404)], 32, 24, 12, SKIN, SHOE, ss=.8, toe=1))
        out.append(hose([(0 + 8 * s, 70), (2 + 8 * s, 112)], 15, SKIN))
        out.append(g(dress(s, swing=.6), 0, 0))
        # the far arm: a relaxed curve out to the side, open hand
        out.append(arm([(32 + 8 * s, 120), (58 + 8 * s, 150), (70 + 8 * s, 186)], 14, SKIN, 'open', .72))
        out.append(puff(31 + 8 * s, 118))
        out.append(g(head(a, expr), 6, -4, 1, rot=-8))
        # the near arm curls up; the hand holds a daisy at the chin
        out.append(daisy(-34, 22, 1.0))
        out.append(arm([(-30 + 6 * s, 120), (-60, 120), (-46, 72)], 14, SKIN, 'hold', .72, flip=True))
        out.append(puff(-30 + 6 * s, 118))
    return ''.join(out)


def daisy(x, y, sc=1.0):
    out = [line([(x, y + 8), (x + 4, y + 50), (x - 2, y + 80)], 3, '#4f7a3a'), line([(x, y + 8), (x + 4, y + 50), (x - 2, y + 80)], 1.2)]
    pet = ''
    for i in range(9):
        ang = i * 40
        pet += g(blob([(0, -2), (6, -12), (0, -22), (-6, -12)], WHITE, 1.8), 0, 0, 1, rot=ang)
    out.append(g(pet + circle(0, 0, 6, '#f2b632', 2), x, y, sc))
    return ''.join(out)


def figure_side(pose='stand', expr='neutral'):
    a = 1.25
    out = []
    # far leg, far arm, then body, near leg, near arm, head
    out.append(leg([(4, 250), (2, 330), (4, 404)], 32, 24, 12, SKIN_SH, SHOE, ss=.8, toe=1))
    out.append(arm([(4, 120), (8, 162), (2, 204)], 14, SKIN_SH, 'rest', .72))
    out.append(hose([(18, 70), (8, 112)], 15, SKIN))
    bod = smooth([(-12, 110), (-14, 140), (-10, 170), (20, 170), (24, 140), (16, 112), (4, 104)])
    skirt = smooth([(-10, 166), (-26, 205), (-40, 258), (-14, 268), (14, 266), (44, 258), (30, 205), (20, 166)])
    out.append(leg([(4, 250), (8, 330), (10, 404)], 32, 24, 12, SKIN, SHOE, ss=.8, toe=1))
    out.append(union([skirt, bod], DRESS) + dots(skirt + ' ' + bod, 0) + P(skirt, 'none', INK, LW) + P(bod, 'none', INK, LW))
    out.append(blob([(-11, 164), (21, 164), (22, 176), (-12, 176)], BOW, LWI + .5, k=.6))
    out.append(blob([(10, 104), (26, 110), (22, 122), (8, 118)], DOT, LWI + .5))
    out.append(arm([(2, 120), (10, 164), (4, 206)], 14, SKIN, 'rest', .72))
    out.append(puff(2, 118))
    out.append(head(a, expr))
    return ''.join(out)
