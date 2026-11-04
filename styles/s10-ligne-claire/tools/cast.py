"""The four characters: head shapes, hair, faces, colours.  Bodies are in figures.py."""
import numpy as np
import lc, r3
from head import Head, Shell, Mark, lock_part
import features as F

SKIN = '#f6d2b2'


def wrapdeg(a):
    """Shell angle (radians, pi/2 = front) -> signed degrees from the front, + toward the viewer's left (x < 0)."""
    return (np.degrees(a) - 90 + 180) % 360 - 180


def hairline_keep(hairline, side_z=None, cut_y=None):
    """keep(X, Y, Z, a) for a hair shell: keep what is above the hairline (angle in degrees from the front ->
    y); below it keep only what lies behind side_z (rows y -> z: the front edge of hair hanging at the sides);
    cut_y(angle) cuts the ends."""
    hl = np.array(hairline, float)
    sz = np.array(side_z, float) if side_z is not None else None

    def keep(X, Y, Z, a):
        d = wrapdeg(a)
        yh = np.interp(d, hl[:, 0], hl[:, 1])
        m = Y < yh
        if sz is not None:
            m |= Z < np.interp(Y, sz[:, 0], sz[:, 1])
        if cut_y is not None:
            m &= Y < cut_y(d)
        return m
    return keep


def Shell_lift(shell, pts, d):
    """Offsets that lift points of shell.curve(pts) by d along the shell's outward direction."""
    P = shell.curve(pts)
    zm = shell.sl(P[:, 1])[1]
    N = P - np.stack([0 * P[:, 0], P[:, 1], zm], 1)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
    return N * d


def face_marks(eye, brow, mouth, nose, extra=None):
    def fn(h, e, view):
        out = []
        for s in (1, -1):
            out += F.eye_marks(h, s, e, eye)
            out += F.brow_marks(h, s, e, brow)
        out += F.mouth_marks(h, e, mouth)
        out += F.nose_marks(h, e, nose, view.yaw_deg)
        if extra:
            out += extra(h, e, view)
        return out
    return fn


def squash(rows, k, pivot=20.0):
    """Shorten (k < 1) or lengthen the face below the pivot: a cartoonist's first decision about a face."""
    return [(r[0] if r[0] <= pivot else pivot + (r[0] - pivot) * k,) + tuple(r[1:]) for r in rows]


def sq(y, k, pivot=20.0):
    return y if y <= pivot else pivot + (y - pivot) * k


# ---------------------------------------------------------------------------------------------------- Аня
def anya():
    K = 0.83
    h = Head(
        slices=squash([
            (-104, 6, -14, -6, -22, 2.0),
            (-96, 34, -12, 20, -50, 2.0),
            (-80, 54, -10, 42, -78, 2.1),
            (-60, 63, -8, 58, -92, 2.2),
            (-40, 66, -6, 67, -97, 2.4),
            (-16, 66, -4, 73, -95, 2.7),
            (2, 64, -2, 70, -90, 3.0),
            (22, 62, 0, 75, -78, 3.0),
            (40, 59, 4, 77, -58, 2.7),
            (55, 54, 8, 77, -34, 2.4),
            (68, 45, 14, 75, -8, 2.2),
            (80, 32, 25, 72, 18, 2.1),
            (90, 17, 40, 68, 38, 2.0),
            (95, 6, 55, 62, 50, 2.0),
        ], K),
        nose=squash([(-4, 0, 6), (8, 2, 6), (20, 6, 7), (30, 11, 8), (35, 12.5, 10), (39, 7, 11), (42, 1, 10),
                     (44, 0, 8)], K),
        lips=squash([(46, 0, 16), (49, 2.6, 18), (52.5, 2.3, 19), (55, 0.4, 19), (58, 3.0, 16), (62, 2.0, 12),
                     (66, 0, 8)], K),
        chin=squash([(72, 0, 14), (81, 2.5, 17), (89, 2.5, 15), (95, 0, 9)], K),
        neck=dict(z=-10, rx=32, rz=33, y0=36, y1=150),
        ear=dict(y=12, z=-16, ry=17, rz=10, out=11, tilt=0.12),
    )
    shell = Shell([
        (-116, 8, -16, 2, -28, 2.0),
        (-109, 44, -14, 34, -62, 2.0),
        (-92, 68, -12, 60, -90, 2.0),
        (-66, 78, -10, 74, -104, 2.1),
        (-40, 80, -8, 80, -106, 2.2),
        (-10, 78, -6, 82, -102, 2.2),
        (20, 75, -4, 80, -96, 2.2),
        (50, 74, -4, 74, -90, 2.1),
        (80, 76, -6, 66, -86, 2.0),
        (100, 82, -8, 58, -84, 2.0),
        (112, 84, -10, 50, -80, 2.0),
    ])
    # the fringe sweeps from the parting to her left and ends in points over the temple
    hairline = [(-180, -20), (-90, -20), (-76, -22), (-62, -22), (-52, -16), (-45, -4), (-40, -14), (-34, -22),
                (-27, -26), (-23, -18), (-19, -28), (-8, -36), (8, -44), (26, -52),
                (36, -48), (50, -40), (64, -32), (78, -24), (90, -20), (180, -20)]
    hl = np.array(hairline, float)

    def keep(X, Y, Z, a):
        # shoulder-length hair: on her right (x < 0) it frames the cheek, on her left it is tucked behind the ear
        d = wrapdeg(a)
        m = Y < np.interp(d, hl[:, 0], hl[:, 1])
        front_r = np.interp(Y, [-40, 0, 40, 70, 112], [-6, 10, 22, 26, 20])
        front_l = np.interp(Y, [-40, 0, 40, 70, 112], [-16, -22, -18, -4, 6])
        m |= np.where(d > 0, Z < front_r, Z < front_l)
        saw = 1 - np.abs((d / 13) % 2 - 1)          # lock tips along the ends
        ends = 96 + 12 * saw ** 1.6
        return m & (Y < ends)
    h.extra_parts.append(lambda hd, res: [shell.part('hair', 'hair', res, keep)])

    def locks(hd, e, view):
        c = shell.curve
        ms = []
        for pts in ([(26, -102), (4, -84), (-22, -58), (-38, -28), (-45, -6)],
                    [(23, -92), (2, -70), (-16, -46), (-23, -20)],
                    [(30, -98), (-4, -96), (-36, -84), (-58, -60), (-66, -30)],
                    [(32, -100), (48, -84), (62, -62), (74, -44)],
                    [(-100, -30), (-104, 10), (-100, 45), (-96, 66)],
                    [(100, -30), (104, 10), (100, 45), (96, 66)],
                    [(-140, -60), (-142, 0), (-138, 60)],
                    [(140, -60), (142, 0), (138, 60)]):
            ms.append(Mark(c(pts), w=0.7, on='hair'))
        ms.append(Mark(c([(29, -111), (28, -100), (26, -86)]), w=0.8, on='hair'))
        return ms
    h.marks.append(face_marks(
        eye=dict(x=28, y=6, w=14, lashes=True, pupil=(4.6, 6.0), lidw=1.4, lid=0.82),
        brow=dict(x=29, y=-11, len=13.5, th=1.1, colour='#7a2e14', arch=4.2),
        mouth=dict(y=sq(54, K), w=11.5, smile=0.3, lower_y=6),
        nose=dict(y=sq(37, K), w=6)))
    h.marks.append(locks)
    colours = {'skin': SKIN, 'hair': '#c4562a'}
    return h, colours


# ---------------------------------------------------------------------------------------------------- Савелий Петрович
def savely():
    K = 0.95
    h = Head(
        slices=squash([
            (-104, 6, -14, -6, -22, 2.0),
            (-97, 38, -12, 24, -52, 2.0),
            (-82, 60, -10, 46, -80, 2.1),
            (-60, 71, -8, 62, -95, 2.2),
            (-40, 75, -6, 70, -100, 2.4),
            (-16, 76, -4, 74, -98, 2.7),
            (2, 74, -2, 69, -93, 3.0),
            (22, 72, 0, 74, -82, 3.0),
            (40, 69, 4, 75, -62, 2.8),
            (55, 66, 8, 74, -38, 2.5),
            (68, 60, 14, 72, -10, 2.3),
            (80, 49, 26, 70, 18, 2.2),
            (90, 32, 40, 66, 38, 2.1),
            (97, 12, 55, 60, 50, 2.0),
        ], K),
        # a big, round, slightly drooping nose: the caricature of the face
        nose=squash([(-4, 0, 8), (6, 3, 8), (18, 9, 10), (30, 19, 14), (38, 24, 17), (44, 18, 18), (48, 6, 16),
                     (51, 0, 12)], K),
        lips=squash([(54, 0, 18), (57, 1.5, 20), (60, 1.2, 21), (62, 0.3, 21), (65, 2.2, 18), (69, 1.5, 14),
                     (73, 0, 10)], K),
        chin=squash([(76, 0, 18), (84, 3, 22), (91, 3, 20), (97, 0, 12)], K),
        brow=[(-22, 0, 46), (-14, 4, 50), (-8, 3, 48), (-2, 0, 34)],
        neck=dict(z=-14, rx=46, rz=42, y0=40, y1=160),
        ear=dict(y=12, z=-18, ry=22, rz=12, out=14, tilt=0.15),
    )
    # white hair: a horseshoe round the back and over the ears, fluffy, the dome bald
    shell = Shell([
        (-80, 62, -14, 40, -86, 2.1),
        (-60, 76, -12, 60, -102, 2.2),
        (-40, 80, -10, 66, -105, 2.3),
        (-16, 81, -8, 70, -103, 2.5),
        (6, 80, -6, 68, -97, 2.5),
        (26, 77, -4, 60, -88, 2.3),
        (40, 70, -2, 50, -78, 2.1),
    ])

    def keep(X, Y, Z, a):
        # a fluffy horseshoe round the back, from the temples over the ears; wavy edges
        dd = wrapdeg(a)
        d = np.abs(dd)
        wave = 5 * np.sin(np.radians(dd) * 14)
        top = np.interp(d, [0, 74, 90, 120, 180], [200, 200, -14, -32, -40]) + wave
        bot = np.interp(d, [0, 74, 90, 110, 150, 180], [-200, -200, 8, 20, 30, 32]) + wave
        return (Y > top) & (Y < bot) & (Z < -4 + 0.4 * (Y + 14))
    skull = Shell(h.p['slices'])

    def hair_parts(hd, res):
        ps = [shell.part('hair', 'hair', res, keep)]
        # moustache: two drooping wings over the upper lip, standing off the face
        for s in (1, -1):
            ps.append(lock_part(skull, [(0, sq(51, K)), (s * -12, sq(52, K)), (s * -24, sq(56, K)),
                                        (s * -32, sq(63, K)), (s * -34, sq(68, K))],
                                [5, 7, 7, 5, 0], lift=[10, 9, 6, 4, 3], name=f'stache{s}', material='stache',
                                res=res, curl=2))
        return ps
    h.extra_parts.append(hair_parts)

    def details(hd, e, view):
        c = shell.curve
        ms = []
        for s in (1, -1):
            # tufts: little strokes in the white fluff
            for pts in ([(s * 96, -18), (s * 104, -2), (s * 102, 14)],
                        [(s * 120, -34), (s * 126, -10), (s * 124, 16)],
                        [(s * 150, -40), (s * 154, -10), (s * 150, 22)]):
                ms.append(Mark(c(pts), w=0.6, on='hair'))
        for pts in ([(-4, sq(54, K)), (-16, sq(57, K)), (-26, sq(63, K))], [(4, sq(54, K)), (16, sq(57, K)),
                                                                              (26, sq(63, K))]):
            ms.append(Mark(skull.curve(pts) + Shell_lift(skull, pts, 8.5), w=0.5, on='stache'))
        # brows: bushy, white, frowning
        # forehead lines, nasolabial folds, bags
        for yy, ww in ((-40, 22), (-48, 26), (-56, 20)):
            ms.append(F.face_line(hd, 0, yy - e.get('brow', 0) * 0.5, [(-ww, 1.5), (0, -0.5), (ww, 1.5)], w=0.55))
        for s in (1, -1):
            ms.append(F.face_line(hd, s * 22, sq(42, K), [(0, 0), (s * 6, 10), (s * 8, 20)], w=0.6))
        ms += F.glasses_marks(hd, dict(x=27, y=3, rx=14, ry=13, lift=12, w=1.0))
        return ms
    h.marks.append(face_marks(
        eye=dict(x=27, y=3, w=10, pupil=(3.2, 4.0), lidw=1.4, lid=0.7, bags=True, crowsfeet=True),
        brow=dict(x=28, y=-15, len=14, th=1.8, colour='#ece8e0', arch=1.5, bushy=True),
        mouth=dict(y=sq(62, K), w=12, smile=-0.2, lower_y=7),
        nose=dict(y=sq(46, K), w=10)))
    h.marks.append(details)
    colours = {'skin': '#f1c6a0', 'hair': '#efece6', 'stache': '#efece6'}
    return h, colours


# ---------------------------------------------------------------------------------------------------- Тим
def tim():
    K = 0.72
    h = Head(
        slices=squash([
            (-108, 6, -14, -6, -22, 2.0),
            (-100, 40, -12, 22, -54, 2.0),
            (-84, 62, -10, 46, -84, 2.1),
            (-62, 74, -8, 62, -100, 2.2),
            (-40, 78, -6, 70, -104, 2.3),
            (-16, 78, -4, 74, -100, 2.5),
            (4, 75, -2, 74, -92, 2.6),
            (22, 71, 0, 76, -80, 2.6),
            (40, 64, 4, 76, -58, 2.5),
            (55, 56, 8, 75, -34, 2.4),
            (68, 47, 14, 72, -8, 2.3),
            (80, 35, 25, 68, 18, 2.2),
            (90, 21, 40, 63, 38, 2.1),
            (96, 8, 55, 58, 50, 2.0),
        ], K),
        nose=squash([(10, 0, 6), (20, 3, 7), (30, 8, 9), (36, 10, 11), (40, 6, 11), (43, 1, 10), (45, 0, 8)], K),
        lips=squash([(48, 0, 14), (51, 1.6, 16), (54, 1.4, 16), (56, 0.3, 16), (59, 2.0, 14), (62, 1.2, 10),
                     (66, 0, 8)], K),
        chin=squash([(72, 0, 14), (82, 2, 16), (90, 2, 14), (95, 0, 8)], K),
        neck=dict(z=-8, rx=33, rz=32, y0=36, y1=150),
        ear=dict(y=16, z=-14, ry=18, rz=11, out=17, tilt=0.1),
    )
    shell = Shell([
        (-118, 8, -16, 2, -28, 2.0),
        (-111, 44, -14, 30, -62, 2.0),
        (-94, 68, -12, 56, -94, 2.1),
        (-70, 82, -10, 72, -110, 2.2),
        (-44, 86, -8, 80, -112, 2.3),
        (-20, 86, -6, 82, -108, 2.4),
        (6, 84, -4, 80, -100, 2.4),
        (30, 79, -2, 70, -90, 2.3),
        (46, 70, 0, 60, -80, 2.1),
    ])
    # straw hair, cut short and uneven: the hairline is a row of points
    hl = [(-180, 40), (-120, 34), (-96, 8), (-88, -8), (-80, -24), (-70, -20), (-62, -40), (-50, -34),
          (-40, -40), (-30, -28), (-22, -44), (-8, -50), (2, -34), (12, -52), (26, -50), (36, -36), (46, -48),
          (60, -46), (68, -30), (78, -34), (86, -14), (96, 8), (120, 34), (180, 40)]
    side_z = [(-60, -12), (0, -10), (40, -8)]
    keep = hairline_keep(hl, side_z)
    skull = Shell(h.p['slices'])
    # the cowlick: a lock that stands up at the crown
    cow = ([(-10, -96), (-14, -112), (-6, -126), (8, -128)], [7, 6, 4, 0])

    def hair_parts(hd, res):
        ps = [shell.part('hair', 'hair', res, keep)]
        # the cowlick: two tufts that stand up at the crown
        ps.append(lock_part(shell, [(-4, -96), (-6, -104), (-10, -110), (-4, -114)], [7, 6, 4, 0],
                            lift=[1, 6, 14, 22], name='cow1', res=res))
        ps.append(lock_part(shell, [(6, -98), (8, -106), (14, -110), (20, -108)], [6, 5, 3, 0],
                            lift=[1, 5, 11, 16], name='cow2', res=res))
        return ps
    h.extra_parts.append(hair_parts)

    def details(hd, e, view):
        c = shell.curve
        ms = []
        for pts in ([(0, -112), (-10, -84), (-14, -56)], [(10, -110), (20, -80), (28, -56)],
                    [(-12, -108), (-36, -80), (-36, -50)], [(16, -104), (44, -76), (48, -50)],
                    [(-30, -100), (-62, -70), (-64, -30)], [(30, -100), (66, -70), (66, -42)],
                    [(-60, -96), (-96, -50), (-96, 4)], [(60, -96), (96, -50), (94, 4)],
                    [(160, -100), (150, -40), (140, 20)], [(-160, -100), (-150, -40), (-140, 20)]):
            ms.append(Mark(c(pts), w=0.6, on='hair'))
        # freckles
        rng = np.random.default_rng(3)
        for s in (1, -1):
            for k in range(7):
                fx = s * (16 + rng.uniform(0, 18))
                fy = sq(28, K) + rng.uniform(-6, 5)
                P = hd.on_face(fx, fy, [(0, 0), (1.4, 0), (1.4, 1.4), (0, 1.4)])
                ms.append(Mark(P, kind='shape', fill='#c4703a', w=0))
        return ms
    h.marks.append(face_marks(
        eye=dict(x=28, y=8, w=10, pupil=(4.2, 5.4), lidw=1.4, lid=0.95, lower=False),
        brow=dict(x=29, y=-10, len=11, th=1.3, colour='#a8742a', arch=3),
        mouth=dict(y=sq(55, K), w=12, smile=0.45),
        nose=dict(y=sq(38, K), w=6)))
    h.marks.append(details)
    colours = {'skin': SKIN, 'hair': '#e9c160'}
    return h, colours


# ---------------------------------------------------------------------------------------------------- Вера
def vera():
    K = 1.04
    h = Head(
        slices=squash([
            (-104, 6, -14, -6, -22, 2.0),
            (-96, 34, -12, 20, -50, 2.0),
            (-80, 54, -10, 42, -78, 2.1),
            (-60, 63, -8, 58, -92, 2.2),
            (-40, 66, -6, 67, -97, 2.4),
            (-16, 66, -4, 73, -95, 2.7),
            (2, 64, -2, 69, -90, 3.0),
            (22, 62, 0, 75, -78, 3.0),
            (40, 55, 4, 76, -58, 2.8),
            (55, 48, 8, 75, -34, 2.5),
            (68, 41, 14, 73, -8, 2.3),
            (80, 31, 25, 70, 18, 2.2),
            (90, 19, 40, 66, 38, 2.1),
            (96, 7, 55, 60, 50, 2.0),
        ], K),
        # a long straight nose with a slight bump
        nose=squash([(-4, 0, 6), (8, 4, 6), (16, 8, 6.5), (24, 11, 7), (32, 15, 8), (38, 16, 10), (42, 9, 11),
                     (45, 1, 10), (47, 0, 8)], K),
        lips=squash([(49, 0, 15), (52, 1.6, 17), (55, 1.4, 18), (57, 0.3, 18), (60, 1.8, 15), (63, 1.2, 11),
                     (67, 0, 8)], K),
        chin=squash([(72, 0, 14), (81, 3, 17), (89, 3, 15), (95, 0, 9)], K),
        neck=dict(z=-12, rx=36, rz=35, y0=40, y1=160),
        ear=dict(y=12, z=-16, ry=17, rz=10, out=10, tilt=0.12),
    )
    # dark hair drawn back tight from a side parting into a knot at the back
    shell = Shell([
        (-110, 8, -16, 2, -28, 2.0),
        (-103, 40, -14, 28, -58, 2.0),
        (-86, 60, -12, 50, -86, 2.1),
        (-64, 69, -10, 64, -100, 2.2),
        (-40, 71, -8, 72, -104, 2.4),
        (-16, 71, -6, 76, -101, 2.6),
        (6, 70, -4, 74, -96, 2.6),
        (26, 66, -2, 66, -88, 2.4),
        (44, 52, 0, 50, -76, 2.2),
    ])
    hl = [(-180, 44), (-120, 40), (-96, 16), (-86, 2), (-78, -22), (-60, -44), (-40, -54), (-18, -60), (0, -62),
          (14, -64), (22, -68), (40, -58), (60, -46), (78, -24), (86, 2), (96, 16), (120, 40), (180, 44)]
    keep = hairline_keep(hl, [(-60, -20), (0, -16), (40, -14)])

    def hair_parts(hd, res):
        ps = [shell.part('hair', 'hair', res, keep)]
        # the knot: a squashed ball low at the back
        u, v = np.meshgrid(np.linspace(0, 2 * np.pi, int(220 * res / 2.4)), np.linspace(0, np.pi, int(120 * res / 2.4)),
                           indexing='ij')
        X = 30 * np.cos(u) * np.sin(v)
        Y = 2 + 24 * np.cos(v)
        Z = -112 + 18 * np.sin(u) * np.sin(v)
        ps.append(r3.Part('knot', 'hair', X, Y, Z))
        return ps
    h.extra_parts.append(hair_parts)

    def details(hd, e, view):
        c = shell.curve
        ms = []
        for pts in ([(22, -100), (60, -80), (90, -50), (110, -20), (140, 0)],
                    [(16, -96), (-20, -84), (-60, -60), (-100, -30), (-140, -2)],
                    [(14, -84), (-14, -72), (-50, -52), (-86, -22), (-120, 2)],
                    [(26, -86), (54, -70), (80, -46), (104, -16)],
                    [(-26, -104), (-80, -84), (-130, -50), (-160, -14)]):
            ms.append(Mark(c(pts), w=0.6, on='hair', stroke='#4e5a70'))
        # grey at the temple: a few light strands swept back from the parting
        for k in range(3):
            ms.append(Mark(c([(10 + k * 5, -64 - k * 2), (34 + k * 4, -76 - k * 2), (70 + k * 3, -64 - k * 3),
                              (100, -38 - k * 4)]), w=1.1, on='hair', stroke='#b9bcc4'))
        # tiredness: a fold under each eye, a line by the mouth
        for s in (1, -1):
            ms.append(F.face_line(hd, s * 19, sq(44, K), [(0, 0), (s * 3, 6), (s * 4, 11)], w=0.45))
        ms += F.glasses_marks(hd, dict(x=27, y=3, rx=15, ry=9, lift=11, w=1.1, shape='rect', colour='#2a1a12'))
        return ms
    h.marks.append(face_marks(
        eye=dict(x=27, y=3, w=11, pupil=(3.4, 4.4), lidw=1.45, lid=0.7, lashes=True, bags=True),
        brow=dict(x=28, y=-14, len=14, th=1.2, colour='#1f1c22', arch=2.0),
        mouth=dict(y=sq(57, K), w=10.5, smile=-0.12, ticks=True),
        nose=dict(y=sq(41, K), w=6)))
    h.marks.append(details)
    colours = {'skin': '#f4cfae', 'hair': '#232733', 'grey': '#a9adb5'}
    return h, colours
