"""Марат, about 35, a cook: huge, loud, merry.  head() and figure(), built on the style's shared parts.

The beard is a black mass with a scalloped edge (Hergé's captain, Chaland's bearded men), the mouth is drawn on
it: a laughing dark shape with a strip of teeth and a tongue.  Hair and beard are shells pushed into curls.
"""
import numpy as np
import lc, r3, body as B, features as F
from head import Head, Shell, Mark, Glyph, lock_part
from cast import wrapdeg, face_marks
from figures import inset
from hands import hand
from extra import Posed, OnShell, on, bumps, curl, grin_marks, strip, shell_z

SKIN = '#f0c39c'
HAIR = '#2a2422'
CURL = '#7d6c62'          # the lines inside black hair
COL = {'skin': SKIN, 'hair': HAIR, 'beard': HAIR,
       'jacket': '#f8f2e4', 'apron': '#c8623a', 'towel': '#f3e3c2', 'trousers': '#4a4e5a', 'shoe': '#2a2420',
       'steel': '#c3c9cc'}
PANEL = '#dbe3c8'
REST = dict(lid=0.5, squint=1.0, brow=2.5, smile=1.0, open=14)      # his resting face is a wide smile
MOUTH = dict(y=67, w=25)
TURN = dict(arms_down=True)             # in the turnaround the ladle would stand in front of his profile
PORTRAIT = dict(s=1.3)                  # a big man: a little farther off, so the shoulders are in the panel


def head():
    h = Head(
        slices=[
            (-106, 6, -14, -6, -22, 2.0),
            (-98, 40, -12, 24, -54, 2.0),
            (-82, 64, -10, 48, -84, 2.1),
            (-60, 76, -8, 64, -99, 2.2),
            (-40, 80, -6, 72, -104, 2.4),
            (-16, 82, -4, 76, -102, 2.7),
            (2, 81, -2, 72, -96, 3.0),
            (22, 83, 0, 77, -84, 3.0),
            (40, 82, 4, 79, -64, 2.8),
            (55, 76, 8, 78, -40, 2.6),
            (68, 67, 14, 76, -12, 2.4),
            (80, 54, 26, 73, 16, 2.2),
            (90, 36, 40, 68, 36, 2.1),
            (98, 12, 55, 62, 50, 2.0),
        ],
        # a broad, short nose
        nose=[(-4, 0, 9), (6, 3, 9), (18, 8, 11), (29, 15, 15), (36, 19, 19), (42, 15, 20), (47, 5, 18), (50, 0, 14)],
        lips=None, chin=None,
        brow=[(-24, 0, 48), (-16, 4, 52), (-9, 3, 50), (-3, 0, 36)],
        neck=dict(z=-14, rx=58, rz=50, y0=40, y1=170),
        ear=dict(y=10, z=-18, ry=22, rz=12, out=13, tilt=0.14),
    )
    hair = Shell([
        (-121, 8, -16, 2, -28, 2.0),
        (-114, 46, -14, 32, -64, 2.0),
        (-97, 72, -12, 56, -96, 2.1),
        (-73, 85, -10, 72, -110, 2.2),
        (-46, 89, -8, 80, -110, 2.3),
        (-20, 90, -6, 82, -107, 2.4),
        (6, 88, -4, 78, -102, 2.4),
        (30, 84, -2, 68, -92, 2.3),
        (48, 76, 0, 58, -82, 2.1),
    ])
    hl = np.array([(0, -55), (30, -57), (56, -50), (70, -36), (80, -20), (86, -8), (92, -14), (100, -14), (110, 4),
                   (124, 34), (180, 44)], float)

    def hair_keep(X, Y, Z, a):
        d = np.abs(wrapdeg(a))
        yh = np.interp(d, hl[:, 0], hl[:, 1]) + 7 * np.abs(np.sin(np.radians(wrapdeg(a) + 9) * 4.1)) - 4  # scallops
        return Y < yh

    beard = Shell([
        (-22, 84, -2, 60, -60, 2.6),
        (10, 87, 0, 80, -50, 2.8),
        (40, 88, 4, 86, -30, 2.8),
        (60, 84, 8, 90, -10, 2.6),
        (80, 74, 14, 91, 0, 2.5),
        (100, 58, 22, 87, 6, 2.4),
        (116, 38, 30, 77, 10, 2.2),
        (127, 10, 40, 62, 26, 2.0),
    ])
    bl = np.array([(0, 50), (14, 50), (24, 48), (36, 45), (50, 41), (62, 35), (72, 22), (78, 4), (83, -12), (90, -12)],
                  float)

    def beard_keep(X, Y, Z, a):
        dd = wrapdeg(a)
        d = np.abs(dd)
        top = np.interp(d, bl[:, 0], bl[:, 1]) + 2 - 5 * np.abs(np.sin(np.radians(dd) * 4.5))
        saw = 1 - np.abs((dd / 12) % 2 - 1)
        return (Y > top) & (d < np.interp(Y, [20, 50], [87, 100])) & (Z > -26) & (Y < 106 + 10 * saw ** 1.5)

    def hair_parts(hd, res):
        return [bumps(hair.part('hair', 'hair', res, hair_keep), (0, -22, -14), 6.0, 26),
                bumps(beard.part('beard', 'beard', res, beard_keep), (0, 62, 16), 4.0, 24, seed=0.4)]
    h.extra_parts.append(hair_parts)
    ob = OnShell(beard, lift=5.0)

    def details(hd, e, view):
        ms = []
        # curls: small 'c' strokes in the hair, a few in the beard
        hc = hair.curve
        k = 0
        for d in (-150, -118, -86, -52, -18, 16, 50, 84, 116, 150):
            for y in (-98, -76, -52):
                k += 1
                if y == -52 and abs(d) < 60:
                    continue
                ms.append(Mark(hc(curl((d + (k % 3 - 1) * 9, y + (k % 2) * 8), 6.5, turn=k * 1.9, flip=k % 2 == 0)),
                               w=0.7, on='hair', stroke=CURL, tol=12))
        for d in (-130, 130):
            for y in (-24, 4):
                ms.append(Mark(hc(curl((d, y), 6.5, turn=d + y)), w=0.7, on='hair', stroke=CURL, tol=12))
        bc = beard.curve
        for k, (d, y) in enumerate([(-66, 34), (-56, 70), (-34, 98), (62, 46), (48, 84), (20, 104), (-8, 100),
                                    (-70, 6), (72, 14)]):
            ms.append(Mark(bc(curl((d, y), 6, turn=k * 2.3, flip=k % 2 == 0)) + [0, 0, 5], w=0.7, on='beard',
                           stroke=CURL, tol=9))
        # the moustache: its lower edge, a light line from under the nose round the mouth
        for s in (1, -1):
            ms.append(Mark(ob.on_face(0, MOUTH['y'], [(s * 3, -10), (s * 14, -12), (s * 26, -10), (s * 34, -3),
                                                     (s * 37, 6)]), w=0.8, on='beard', stroke=CURL))
        # laughing cheeks: a short fold from the wing of the nose
        for s in (1, -1):
            ms.append(F.face_line(hd, s * 24, 33, [(0, 0), (s * 6, 5), (s * 9, 12)], w=0.6))
        return ms

    eye = dict(x=30, y=3, w=11, pupil=(3.6, 4.5), lidw=1.45, lid=0.62, crowsfeet=True)
    brow = dict(x=31, y=-15, len=16, th=2.0, colour=HAIR, arch=3.6, bushy=True)
    nose = dict(y=45, w=13)

    def face(hd, e, view):
        e = e or REST
        out = []
        for s in (1, -1):
            out += F.eye_marks(hd, s, e, eye)
            out += F.brow_marks(hd, s, e, brow)
        out += F.nose_marks(hd, e, nose, view.yaw_deg)
        if abs(view.yaw_deg) < 25:               # a broad nose: the other wing too
            s = 1 if view.yaw_deg >= 0 else -1
            out.append(F.face_line(hd, 0, nose['y'], [(s * 12, -4), (s * 14.5, -0.5), (s * 11, 2)], w=0.75))
        if F.ex(e, 'smile', 0) > 0 and F.ex(e, 'open', 0) > 0 and not F.ex(e, 'round'):
            out += on(grin_marks(ob, e, MOUTH), 'beard')
        else:
            out += on(F.mouth_marks(ob, e, dict(MOUTH, w=15, lower=False, ticks=False)), 'beard')
        return out
    h.marks.append(face)
    h.marks.append(details)
    return h, {k: COL[k] for k in ('skin', 'hair', 'beard')}


def ladle_bowl(c, r, res):
    """The bowl of the ladle: the lower half of a ball, open toward the viewer's upper side."""
    u, v = np.meshgrid(np.linspace(0, 2 * np.pi, int(2 * np.pi * r * res * 1.4) + 12),
                       np.linspace(0, np.pi / 2, int(r * res * 2) + 8), indexing='ij')
    P = np.stack([r * np.cos(u) * np.sin(v), r * np.cos(v), r * np.sin(u) * np.sin(v)], -1).reshape(-1, 3)
    return B.rotate(P, (-62, 0, -18)) + np.asarray(c, float)


def figure(bust=False, head_rot=(-7, 10, -7), arms_down=False):
    h, col = head()
    col = dict(COL)
    TORSO = [
        (126, 64, -14, 36, -64, 2.0),
        (148, 132, -14, 52, -78, 2.2),
        (174, 182, -16, 68, -90, 2.4),
        (218, 194, -16, 92, -100, 2.6),
        (292, 192, -12, 114, -102, 2.6),
        (382, 186, -10, 126, -100, 2.6),
        (462, 178, -10, 124, -100, 2.6),
        (542, 172, -12, 106, -102, 2.5),
        (604, 168, -14, 94, -102, 2.4),
    ]
    jacket = Shell(TORSO)
    collar = Shell([(104, 62, -14, 44, -66, 2.0), (126, 66, -14, 46, -68, 2.0), (146, 76, -14, 50, -72, 2.0)])
    apron = Shell(inset(TORSO, -5, y0=462) + [(800, 172, -10, 96, -104, 2.3), (1060, 180, -8, 102, -104, 2.2)])
    hips = Shell([(560, 168, -12, 100, -100, 2.5), (640, 166, -14, 92, -100, 2.4), (700, 150, -14, 84, -94, 2.3)])
    floor = 1300
    ladle = [(-318, 236, 84), (-326, 150, 92), (-338, 30, 100), (-346, -44, 104)]

    def arms(res):
        # left arm (x > 0): fist on the hip; the sleeves are rolled above the elbows, the forearms bare
        ps = []
        ps.append(B.tube('sleeveL', 'jacket', [(176, 208, -10), (238, 272, -26), (270, 334, -38)], [54, 52, 50], res))
        ps.append(B.tube('rollL', 'jacket', [(262, 322, -36), (276, 348, -40)], [56, 56], res))
        ps.append(B.tube('foreL', 'skin', [(272, 340, -38), (254, 404, -4), (214, 450, 30)], [45, 41, 33], res))
        # right arm (x < 0): raised, the ladle held up like a sceptre
        ps.append(B.tube('sleeveR', 'jacket', [(-176, 208, -10), (-246, 262, 0), (-288, 312, 14)], [54, 52, 50], res))
        ps.append(B.tube('rollR', 'jacket', [(-278, 302, 12), (-296, 322, 16)], [56, 56], res))
        ps.append(B.tube('foreR', 'skin', [(-290, 316, 16), (-316, 250, 50), (-318, 176, 76)], [45, 41, 33], res))
        ps.append(B.tube('ladle', 'steel', ladle, [7, 7, 7, 7], res))
        Q = ladle_bowl((-352, -84, 106), 44, res)
        ps.append(r3.Part('bowl', 'steel', Q[:, 0], Q[:, 1], Q[:, 2]))
        return ps

    def build(res, bust_only):
        ps = [jacket.part('jacket', 'jacket', res),
              collar.part('collar', 'jacket', res, lambda X, Y, Z, a: np.abs(wrapdeg(a)) > 7)]
        # the towel over his left shoulder: from the chest up over the shoulder and down the back
        tz = lambda x, y: float(shell_z(jacket, x, y)) + 7
        ps.append(strip('towel', 'towel', [(112, 380, tz(112, 380)), (114, 300, tz(114, 300)), (118, 226, tz(118, 226)),
                                           (120, 176, tz(120, 176) + 2), (120, 140, 16), (120, 136, -34),
                                           (120, 168, -84), (118, 250, -112), (116, 340, -114)], 25, res))
        if arms_down:                           # both arms hanging (the turnaround)
            for s in (1, -1):
                ps.append(B.tube(f'sleeve{s}', 'jacket', [(s * 176, 208, -10), (s * 214, 300, -12), (s * 222, 388, -6)],
                                 [54, 52, 50], res))
                ps.append(B.tube(f'roll{s}', 'jacket', [(s * 221, 374, -7), (s * 223, 400, -5)], [56, 56], res))
                ps.append(B.tube(f'fore{s}', 'skin', [(s * 222, 392, -6), (s * 224, 470, 6), (s * 216, 540, 20)],
                                 [45, 41, 33], res))
        else:
            ps += arms(res)
        if bust_only:
            return ps
        ps.append(apron.part('apron', 'apron', res, lambda X, Y, Z, a: np.abs(wrapdeg(a)) < 112))
        ps.append(hips.part('hips', 'trousers', res))
        # a wide, sure stance: the weight on his right leg, the left foot out
        ps.append(B.tube('legR', 'trousers', [(-84, 660, -14), (-88, 860, -8), (-90, 1060, -14),
                                              (-92, floor - 60, -18)], [78, 66, 56, 50], res))
        ps.append(B.tube('legL', 'trousers', [(86, 660, -14), (100, 860, 2), (112, 1060, -4),
                                              (120, floor - 60, -10)], [78, 66, 56, 50], res))
        ps.append(B.blob('shoeR', 'shoe', (-94, floor - 26, 16), (40, 27, 76), res, rot=(0, -10, 0)))
        ps.append(B.blob('shoeL', 'shoe', (128, floor - 26, 22), (40, 27, 76), res, rot=(0, 26, 0)))
        return ps

    def hands():
        return [hand((214, 452, 32), (150, 520, 70), 'fist', col['skin'], 150, flip=True, tol=60),
                hand((-318, 180, 80), (-326, 60, 92), 'fist', col['skin'], 150, flip=False, tol=80)]

    def marks(expr, view, bust_only):
        ms = []
        jc = jacket.curve
        # double-breasted: the edge of the front flap and two rows of buttons
        ms.append(Mark(jc([(-10, 150), (-27, 200), (-30, 300), (-28, 400), (-26, 462)]), w=0.7, on='jacket'))
        for y in (236, 306, 376, 440):
            for d in (-19, 17):
                ms += B.dots3([jc([(d, y)])[0] + [0, 0, 1.5]], 6.5, col['jacket'], on='jacket')
        # sleeve seams at the shoulders
        for s in (1, -1):
            ms.append(B.ring_mark((s * 182, 224, -10), (s * 0.5, 1, 0), 54, on='jacket', arc=(-110, 110)))
        # the towel's stripes
        for y in (346, 359):
            ms.append(Mark(np.array([(x, y, shell_z(jacket, x, y) + 10.5) for x in (89, 101, 113, 125, 137)]), w=1.6,
                           on='towel', stroke=col['apron'], tol=6))
        ms.append(Mark(np.array([(x, y, shell_z(jacket, x, y) + 10.5) for x, y in ((127, 190), (129, 260), (126, 330))]),
                       w=0.6, on='towel', tol=6))
        if arms_down:
            for s in (1, -1):
                ms.append(hand((s * 216, 542, 22), (s * 212, 660, 34), 'hang', col['skin'], 150, flip=s > 0, tol=40))
        else:
            ms += hands()
        if bust_only:
            return ms
        ac = apron.curve
        # the apron: folded over at the waist, a pocket, long folds
        ms.append(Mark(ac([(d, 500 + 4 * np.cos(np.radians(d))) for d in range(-110, 111, 5)]), w=0.7, on='apron'))
        ms.append(Mark(ac([(-58, 640), (-56, 740), (-22, 744), (-22, 640), (-58, 640)]), w=0.6, on='apron',
                       corners=(1, 2, 3)))
        for d in (-64, 30, 70):
            ms.append(Mark(ac([(d, 560), (d * 1.04, 800), (d * 1.08, 1052)]), w=0.6, on='apron'))
        return ms
    # he laughs leaning back: the belly forward, the shoulders and the head behind it, the weight on his right leg
    spine = [(-130, -40, -44, -4, 0), (120, -24, -30, -4, 3), (300, -2, 4, -3, 4), (520, 14, 20, 1, 0),
             (700, 10, 8, 0, 0), (floor, 0, 0, 0, 0)]
    return Posed(h, build, marks, bust, head_rot, head_drop=28, spine=spine), col, floor
