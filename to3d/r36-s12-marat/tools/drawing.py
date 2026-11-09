"""The drawing as numbers: Марат of С12 (styles/s12-ink-watercolour/tools/marat.py — head_front, head_side, bust_view,
figure) as the silhouettes and heights the 3D is fitted to.
Units: the drawing's head units (eye line y = 0, y down; crown of the hair about −150, chin 106, the beard to 136); the
figure's pixels are 0.72 of them. 3D: metres, y up, the figure faces +z, its left is +x. Front view: drawing x → 3D x;
the profile (drawn facing left) is mirrored: 3D z = −x."""
import numpy as np

FLOOR = 958.0           # the soles, in head units below the eye line (figure: eye line 190 px, soles 880 px, 0.72 a unit)
CROWN = -150.0          # top of the hair
HEIGHT = 1.92           # metres, hair top to soles: the tallest of the cast
K = HEIGHT / (FLOOR - CROWN)


def poly(pts, flip=False):
    P = np.array([(-x if flip else x, y) for x, y in pts], float)
    return np.vstack([P, P[:1]])


def span(P, y):
    """Where a horizontal line at drawing-y crosses the closed polyline: (min x, max x) or (nan, nan)."""
    a, b = P[:-1], P[1:]
    m = (a[:, 1] - y) * (b[:, 1] - y) <= 0
    xs = []
    for p, q in zip(a[m], b[m]):
        if p[1] == q[1]: xs += [p[0], q[0]]
        else: xs.append(p[0] + (y - p[1]) / (q[1] - p[1]) * (q[0] - p[0]))
    return (min(xs), max(xs)) if xs else (np.nan, np.nan)


def profile(P, ys):
    return np.array([span(P, y) for y in ys])


def dense(P, n=8):
    """A polyline through the points, rounded (Catmull–Rom), closed."""
    P = np.asarray(P, float)[:-1]; m = len(P); out = []
    for i in range(m):
        p0, p1, p2, p3 = P[(i - 1) % m], P[i], P[(i + 1) % m], P[(i + 2) % m]
        for s in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(out[0]); return np.array(out)


# the head in front (head_front's skin: a wide face; above it the skull under the hair)
_FF = [(0, -128), (-36, -123), (-66, -106), (-84, -80), (-90, -40), (-94, 0), (-84, 56), (-50, 96), (-8, 106)]
FACE_F = dense(poly(_FF + [(-x, y) for x, y in _FF[::-1][:-1]]))
# the profile (head_side, facing left): forehead, the brow ridge, the broad round nose, the lips, the chin under the
# beard (the skin's wash), the jaw to the ear; then the skull's back under the hair
_FS = [(-52, -104), (-68, -54), (-73, -40), (-76, -24), (-82, -13), (-80, -3), (-92, 12), (-105, 26), (-106, 37),
       (-97, 44), (-86, 42), (-87, 52), (-88, 62), (-86, 76), (-80, 90), (-64, 101), (-44, 105), (-20, 104), (0, 100),
       (22, 90), (40, 72), (62, 56), (84, 30), (98, -10), (100, -50), (88, -90), (60, -116), (20, -128), (-22, -122)]
FACE_S = poly(_FS, flip=True)
NOSE = np.array([(-28, 75), (-14, 81), (-3, 80), (10, 90), (24, 103), (32, 106), (39, 104), (44, 96), (47, 86)])   # (y, z front)
# a short thick neck, mostly behind the beard
NECK_W = ([60, 106, 140, 170], [80, 68, 72, 82])
NECK_F = ([80, 106, 140, 170], [56, 50, 54, 62])
NECK_B = ([40, 70, 120, 170], [-90, -74, -62, -68])
Y_DRAW = [170.0, 106.0, 0.0, -128.0]      # the base head's landmarks here: the neck's end, chin, eye line, crown
REG = [(36, -4, 23, 20), (-36, -4, 23, 20), (0, 68, 48, 24)]      # where the face is drawn: eyes and the wide mouth
