"""The four characters: head shapes, hair, faces, colours.  Bodies are in figures.py."""
import numpy as np
import lc, r3
from head import Head, Shell, Mark
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


# ---------------------------------------------------------------------------------------------------- Аня
def anya():
    h = Head(
        slices=[
            (-104, 6, -14, -6, -22, 2.0),
            (-96, 36, -12, 20, -50, 2.0),
            (-80, 57, -10, 42, -78, 2.1),
            (-60, 67, -8, 58, -93, 2.2),
            (-40, 70, -6, 67, -98, 2.4),
            (-16, 71, -4, 73, -96, 2.7),
            (2, 69, -2, 70, -91, 3.0),
            (22, 66, 0, 75, -79, 3.0),
            (40, 59, 4, 77, -58, 2.8),
            (55, 51, 8, 77, -34, 2.6),
            (68, 42, 14, 75, -8, 2.4),
            (80, 31, 25, 71, 18, 2.2),
            (90, 18, 40, 66, 38, 2.1),
            (96, 7, 55, 60, 50, 2.0),
        ],
        nose=[(-4, 0, 6), (8, 2, 6), (20, 6, 7), (30, 11, 8), (35, 12.5, 10), (39, 7, 11), (42, 1, 10), (44, 0, 8)],
        lips=[(46, 0, 16), (49, 2.6, 18), (52.5, 2.3, 19), (55, 0.4, 19), (58, 3.0, 16), (62, 2.0, 12), (66, 0, 8)],
        chin=[(72, 0, 14), (81, 2.5, 17), (89, 2.5, 15), (95, 0, 9)],
        neck=dict(z=-6, rx=27, rz=30, y0=40, y1=150),
        ear=dict(y=12, z=-16, ry=17, rz=10, out=11, tilt=0.12),
    )
    shell = Shell([
        (-111, 8, -16, 2, -28, 2.0),
        (-104, 42, -14, 30, -60, 2.0),
        (-88, 64, -12, 54, -88, 2.1),
        (-66, 76, -10, 68, -103, 2.2),
        (-40, 80, -8, 76, -106, 2.3),
        (-10, 81, -6, 80, -103, 2.4),
        (20, 82, -4, 80, -96, 2.4),
        (50, 82, -2, 76, -86, 2.3),
        (68, 78, 0, 70, -78, 2.2),
        (76, 70, 2, 64, -70, 2.0),
    ])
    # side parting on her right (the viewer's left); a soft wave sweeps across the forehead to the other side
    hairline = [(-180, -20), (-90, -22), (-80, -30), (-66, -44), (-50, -34), (-35, -32), (-18, -40), (2, -54),
                (20, -68), (30, -66), (45, -54), (62, -42), (78, -30), (90, -22), (180, -20)]
    side_z = [(-60, -14), (0, -10), (30, -4), (60, 8), (80, 18)]
    keep = hairline_keep(hairline, side_z)
    h.extra_parts.append(lambda hd, res: [shell.part('hair', 'hair', res, keep)])

    def locks(hd, e, view):
        c = shell.curve
        ms = []
        for pts in ([(26, -102), (8, -86), (-14, -70), (-40, -52), (-62, -40)],
                    [(24, -94), (2, -78), (-24, -62), (-48, -47)],
                    [(32, -100), (48, -84), (62, -62), (74, -44)],
                    [(-100, -30), (-104, 10), (-100, 45), (-96, 66)],
                    [(100, -30), (104, 10), (100, 45), (96, 66)],
                    [(-140, -60), (-142, 0), (-138, 60)],
                    [(140, -60), (142, 0), (138, 60)]):
            ms.append(Mark(c(pts), w=0.7, on='hair'))
        ms.append(Mark(c([(29, -111), (28, -100), (26, -86)]), w=0.8, on='hair'))
        return ms
    h.marks.append(face_marks(
        eye=dict(x=27, y=2, w=10.5, lashes=True, pupil=(3.3, 4.4), lidw=1.45, lid=0.85),
        brow=dict(x=28, y=-15, len=12, th=1.2, colour='#7a2e14', arch=3.2),
        mouth=dict(y=55, w=11, smile=0.2),
        nose=dict(y=37, w=6)))
    h.marks.append(locks)
    colours = {'skin': SKIN, 'hair': '#c4562a'}
    return h, colours
