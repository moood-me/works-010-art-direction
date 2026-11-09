"""Кира, about 15: prickly, closed, defiant.  head() and figure(), built on the style's shared parts.

A longer face than Тим's and smaller eyes than Аня's; short choppy hair with a long fringe over one eye; the
head carried low and forward, the look sideways from under the brows; a mouth pressed shut with one corner up.
"""
import numpy as np
import lc, r3, body as B, features as F
from head import Head, Shell, Mark, Glyph, lock_part
from cast import wrapdeg, squash, sq
from extra import Posed, smirk_marks

SKIN = '#f6d7be'
HAIR = '#2b2331'
LOCK = '#75618a'          # the lines inside her dark hair
LIME = '#cfe82e'
COL = {'skin': SKIN, 'hair': HAIR, 'hoodie': '#553459', 'trousers': '#33353c', 'boot': '#232026',
       'sole': '#57505e', 'cup': LIME, 'pad': '#2c2a30'}
PANEL = '#e6dade'
K = 0.93
REST = dict(lid=0.6, brow=-0.5, tilt=-1.6, look=(2.4, 0.5), smirk=1.4)
# her own versions of the sheet's expressions: joy is a smile she doesn't quite let out; anger is a shut mouth
EXPR = {
    'joy': dict(lid=0.78, brow=3, tilt=1.0, look=(1.6, -0.4), smirk=2.0, squint=0.8),
    'anger': dict(lid=0.7, brow=-4, tilt=-6, look=(1.0, 0.3), smile=-1.0, mw=1.05, squint=0.7),
}
MOUTH = dict(y=sq(55, K), w=10, side=1, lower_y=5.5)
TURN = dict(side=1)       # turned to our right: the side where the fringe doesn't hide her face


def head():
    h = Head(
        slices=squash([
            (-104, 6, -14, -6, -22, 2.0),
            (-96, 34, -12, 20, -50, 2.0),
            (-80, 53, -10, 42, -78, 2.1),
            (-60, 62, -8, 58, -92, 2.2),
            (-40, 65, -6, 67, -97, 2.4),
            (-16, 65, -4, 73, -95, 2.7),
            (2, 63, -2, 70, -90, 3.0),
            (22, 60, 0, 75, -78, 3.0),
            (40, 54, 4, 76.5, -58, 2.7),
            (55, 47, 8, 76, -34, 2.4),
            (68, 38, 14, 74, -8, 2.2),
            (80, 27, 25, 71, 18, 2.1),
            (90, 15, 40, 67, 38, 2.0),
            (95.5, 6, 55, 61, 50, 2.0),
        ], K),
        # a small straight nose with a sharp tip
        nose=squash([(-2, 0, 5.5), (10, 2, 5.5), (22, 6, 6), (31, 11.5, 7), (35, 13.5, 8.5), (38, 8, 9), (41, 1, 8),
                     (43, 0, 7)], K),
        lips=squash([(47, 0, 13), (50, 2.0, 15), (53, 1.8, 15.5), (55, 0.3, 15.5), (58, 2.2, 13), (61, 1.5, 10),
                     (65, 0, 7)], K),
        chin=squash([(71, 0, 12), (80, 2.8, 14), (88, 2.8, 12), (94, 0, 8)], K),
        neck=dict(z=-10, rx=27, rz=29, y0=36, y1=150),
        ear=dict(y=12, z=-16, ry=16, rz=9.5, out=10, tilt=0.12),
    )
    shell = Shell([
        (-119, 8, -16, 2, -28, 2.0),
        (-112, 46, -14, 34, -64, 2.0),
        (-94, 69, -12, 60, -92, 2.0),
        (-66, 78, -10, 74, -105, 2.1),
        (-40, 80, -8, 80, -107, 2.2),
        (-10, 78, -6, 82, -102, 2.2),
        (20, 74, -4, 80, -94, 2.2),
        (50, 69, -4, 72, -82, 2.1),
        (84, 60, -6, 60, -66, 2.0),
    ])
    # the parting is on her right; the fringe falls across the forehead toward her left in long uneven points —
    # one down to the bridge of the nose, one past the outer corner of the left eye (the eye looks out between
    # them, its brow under the hair), one down the temple in front of the ear
    hl = np.array([(-180, -14), (-100, -14), (-88, -20), (-78, -14), (-71, 12), (-65, 34), (-59, 6), (-51, -18),
                   (-44, 12), (-38, 27), (-33, 8), (-27, -5), (-20, -6), (-14, -2), (-9, 9), (-4, -10), (2, -22), (8, -20),
                   (14, -32), (22, -42), (30, -51), (40, -45), (54, -37), (68, -29), (80, -21), (92, -14),
                   (180, -14)], float)

    def keep(X, Y, Z, a):
        d = wrapdeg(a)
        m = Y < np.interp(d, hl[:, 0], hl[:, 1])
        # at the sides: on her left the hair covers half the ear, on her right it is cut short behind it
        front_l = np.interp(Y, [-40, 0, 30, 60, 84], [-6, -4, -6, -12, -18])
        front_r = np.interp(Y, [-40, 0, 30, 60, 84], [-16, -24, -28, -30, -30])
        m |= np.where(d < 0, Z < front_l, Z < front_r)
        saw = 1 - np.abs((d / 10) % 2 - 1)                    # chopped ends: uneven points
        ends = np.where(d < 0, 46, 30) + 22 * saw ** 1.3 + 8 * np.sin(np.radians(d) * 2.3)
        return m & (Y < ends)

    def hair_parts(hd, res):
        ps = [shell.part('hair', 'hair', res, keep)]
        # tufts that won't lie flat: at the crown and down the back of the head
        for k, (path, wd, lift) in enumerate([
                ([(-108, -92), (-116, -78), (-124, -62), (-130, -46)], [10, 9, 5, 0], [1, 6, 13, 21]),
                ([(-118, -44), (-126, -28), (-132, -10), (-136, 6)], [10, 9, 5, 0], [1, 6, 13, 20]),
                ([(-122, 2), (-128, 18), (-132, 34), (-134, 48)], [9, 8, 5, 0], [1, 5, 11, 17]),
                ([(112, -80), (120, -64), (128, -48), (134, -32)], [10, 9, 5, 0], [1, 6, 13, 20]),
                ([(122, -28), (130, -12), (136, 6), (140, 22)], [9, 8, 5, 0], [1, 5, 11, 17])]):
            ps.append(lock_part(shell, path, wd, lift=lift, name=f'tuft{k}', res=res))
        return ps
    h.extra_parts.append(hair_parts)

    def locks(hd, e, view):
        c = shell.curve
        ms = []
        for pts in ([(28, -106), (6, -86), (-20, -54), (-34, -16), (-38, 18)],
                    [(26, -96), (4, -70), (-8, -36), (-9, 2)],
                    [(30, -104), (-12, -96), (-44, -72), (-60, -30), (-65, 22)],
                    [(34, -104), (50, -88), (64, -66), (74, -46)],
                    [(-100, -44), (-106, 0), (-102, 36)],
                    [(112, -44), (116, -6), (112, 22)],
                    [(150, -74), (152, -20), (148, 26)],
                    [(-150, -74), (-152, -20), (-148, 34)]):
            ms.append(Mark(c(pts), w=0.7, on='hair', stroke=LOCK))
        ms.append(Mark(c([(31, -114), (30, -102), (28, -90)]), w=0.8, on='hair', stroke=LOCK))
        return ms

    eye = dict(x=27, y=5, w=11.5, lashes=True, pupil=(3.9, 5.0), lidw=1.6, lid=0.6)
    brow = dict(x=28, y=-8.5, len=12.5, th=1.7, colour=HAIR, arch=1.4)
    nose = dict(y=sq(37, K), w=5.5)

    def face(hd, e, view):
        e = e or REST
        out = []
        for s in (1, -1):
            out += F.eye_marks(hd, s, e, eye)
            out += F.brow_marks(hd, s, e, brow)
        out += F.nose_marks(hd, e, nose, view.yaw_deg)
        if 'smirk' in e:
            out += smirk_marks(hd, e, MOUTH)
        else:
            out += F.mouth_marks(hd, e, dict(MOUTH, w=9.5))
        return out
    h.marks.append(face)
    h.marks.append(locks)
    return h, {k: COL[k] for k in ('skin', 'hair')}


def cuff_fingers(skin):
    """Fingers showing from a sleeve that is too long: curled, the thumb tucked in.  Wrist at (0, 0), 100 long."""
    out = [(-17, 0), (-19, 30), (-18, 60), (-13, 84), (-5, 97), (3, 99), (10, 92), (13, 78), (13, 62), (18, 50),
           (19, 38), (15, 28), (14, 0)]
    return [(out, skin, 1.0, True),
            ([(-9, 52), (-7, 76), (-4, 92)], None, 0.55, False),
            ([(0, 54), (2, 76), (4, 90)], None, 0.55, False),
            ([(8, 52), (10, 70)], None, 0.55, False)]


def figure(bust=False, head_rot=(9, -3, 4)):
    h, col = head()
    col = dict(COL)
    TORSO = [
        (120, 44, -10, 30, -48, 2.0),
        (144, 76, -10, 42, -60, 2.2),
        (172, 106, -12, 52, -68, 2.4),
        (214, 118, -10, 60, -72, 2.6),
        (290, 119, -8, 63, -72, 2.6),
        (390, 120, -6, 65, -73, 2.6),
        (456, 122, -4, 68, -75, 2.5),
        (492, 116, -4, 64, -72, 2.4),
        (512, 100, -4, 56, -66, 2.3),
    ]
    hoodie = Shell(TORSO)
    hips = Shell([(490, 90, -4, 52, -60, 2.4), (570, 92, -4, 54, -62, 2.4), (640, 62, -4, 40, -48, 2.2)])
    floor = 1110

    def build(res, bust_only):
        ps = [hoodie.part('hoodie', 'hoodie', res)]
        # the hood lies round her neck and on her back in a thick roll
        ps.append(B.tube('hood', 'hoodie', [(60, 158, 22), (88, 150, -30), (60, 150, -84), (0, 160, -106),
                                            (-60, 150, -84), (-88, 150, -30), (-60, 158, 22)],
                         [12, 26, 34, 38, 34, 26, 12], res))
        # headphones round the neck: the band behind, the cups hanging at the collarbones, turned to each other
        ps.append(B.tube('band', 'pad', [(50, 150, 34), (60, 122, 6), (44, 112, -44), (0, 112, -62),
                                         (-44, 112, -44), (-60, 122, 6), (-50, 150, 34)], [5] * 7, res))
        for s in (1, -1):
            ps.append(B.blob(f'pad{s}', 'pad', (s * 40, 178, 43), (11, 28, 28), res, rot=(0, s * 14, 0)))
            ps.append(B.blob(f'cup{s}', 'cup', (s * 51, 179, 40), (11, 25, 25), res, rot=(0, s * 14, 0)))
        # both hands deep in the hoodie's pocket would hide them: the left (x > 0) is in the pocket, the right
        # hangs, the sleeve down to the knuckles
        ps.append(B.tube('armL', 'hoodie', [(104, 192, -6), (138, 290, -14), (134, 384, 10), (92, 432, 50),
                                            (40, 446, 40)], [35, 34, 32, 30, 28], res, caps=(True, False)))
        ps.append(B.tube('armR', 'hoodie', [(-104, 192, -6), (-134, 300, -6), (-138, 404, 4), (-132, 490, 16)],
                         [35, 34, 32, 31], res))
        if bust_only:
            return ps
        ps.append(hips.part('hips', 'trousers', res))
        # thin legs in narrow trousers: the weight on her left leg, the right knee bent in and the foot turned in
        ps.append(B.tube('legL', 'trousers', [(46, 600, -2), (48, 790, 4), (50, 900, -2), (52, floor - 110, -4)],
                         [45, 33, 31, 27], res))
        ps.append(B.tube('legR', 'trousers', [(-46, 600, -2), (-52, 790, 44), (-78, 900, 34), (-98, floor - 110, 26)],
                         [45, 33, 31, 27], res))
        for s, x, z, yaw in ((1, 54, 0, 16), (-1, -100, 30, 30)):
            ps.append(B.tube(f'shaft{s}', 'boot', [(x, floor - 150, z - 2), (x, floor - 60, z)], [33, 34], res))
            ps.append(B.blob(f'boot{s}', 'boot', (x + np.sin(np.radians(yaw)) * 22, floor - 36, z + 24),
                             (34, 30, 60), res, rot=(0, yaw, 0)))
            ps.append(B.blob(f'sole{s}', 'sole', (x + np.sin(np.radians(yaw)) * 22, floor - 12, z + 24),
                             (37, 12, 64), res, rot=(0, yaw, 0)))
        return ps

    def marks(expr, view, bust_only):
        ms = []
        hc = hoodie.curve
        # two drawstrings from under the hood
        for s in (1, -1):
            ms.append(Mark(hc([(s * 8, 186), (s * 11, 250), (s * 9, 312)]) + [0, 0, 2], w=1.5, on='hoodie',
                           stroke='#d9cfdc'))
        # the kangaroo pocket, the hem and the cuff
        ms.append(Mark(hc([(-52, 476), (-52, 430), (-30, 384), (30, 384), (52, 430), (52, 476)]), w=0.7,
                       on='hoodie', corners=(1, 2, 3, 4)))
        ms.append(Mark(hc([(d, 494) for d in range(-180, 181, 5)]), w=0.6, on='hoodie'))
        ms.append(B.ring_mark((-133, 470, 13), (0.06, 1, 0.1), 31, on='hoodie'))
        # folds: in the crook of the pocket arm, under the hood, at the side
        ms.append(B.line3([(112, 380, 40), (126, 392, 24), (140, 396, 4)], w=0.6, on='hoodie', tol=8))
        ms.append(B.line3([(-128, 300, 26), (-120, 316, 30), (-108, 322, 32)], w=0.6, on='hoodie', tol=8))
        ms.append(Mark(hc([(-62, 250), (-56, 300), (-60, 350)]), w=0.6, on='hoodie'))
        ms.append(Glyph((-132, 492, 18), (-128, 590, 26), cuff_fingers(col['skin']), 84, flip=False, tol=40))
        if bust_only:
            return ms
        # lime laces on the boots
        for s, x, z in ((1, 54, 0), (-1, -100, 30)):
            for k in range(4):
                y = floor - 132 + k * 22
                ms.append(Mark(np.array([(x - 10, y, z + 36), (x + 10, y + 8, z + 36)]), w=1.3, stroke=LIME,
                               on='boot', tol=10))
        return ms
    # the slouch: the head forward and down, the upper back round, the hips pushed forward and to her left
    spine = [(-130, -6, 40, 0, 0), (110, -4, 26, 3, -6), (210, -8, -12, 4, -7), (400, 4, 2, 0, -2),
             (540, 16, 18, -4, 5), (820, 8, 8, 0, 0), (floor, 0, 0, 0, 0)]
    return Posed(h, build, marks, bust, head_rot, head_drop=30, spine=spine), col, floor
