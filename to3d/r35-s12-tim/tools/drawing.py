"""The drawing as numbers: Тим of С12 (styles/s12-ink-watercolour/tools/tim.py — head_front, head_side, bust_view,
figure) as the silhouettes and heights the 3D is fitted to.
Units: the drawing's head units (eye line y = 0, y down; crown of the hair about −150, chin 88); the figure's pixels are
0.66 of them. 3D: metres, y up, the figure faces +z, its left is +x. Front view: drawing x → 3D x; the profile (drawn
facing left) is mirrored: 3D z = −x."""
import numpy as np

FLOOR = 770.0           # the soles, in head units below the eye line (figure: chin 358 px, soles 808 px, 0.66 a unit)
CROWN = -150.0          # top of the hair
HEIGHT = 1.25           # metres, hair top to soles: a boy of eight
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


# the head in front (head_front's two face contours; above them the skull under the hair)
_FF = [(0, -124), (-34, -119), (-60, -104), (-75, -80), (-80, -50), (-84, 0), (-72, 46), (-44, 76), (-6, 87)]
FACE_F = dense(poly(_FF + [(-x, y) for x, y in _FF[::-1][:-1]]))
# the profile (head_side, facing left): forehead, the upturned nose, lip, the round chin, the jaw to the ear; then the
# skull's back under the hair (the hair's outer line less its thickness)
_FS = [(-52, -96), (-64, -58), (-70, -36), (-72, -14), (-82, 2), (-96, 12), (-90, 21), (-80, 22), (-80, 26), (-79, 34),
       (-80, 40), (-78, 48), (-74, 60), (-60, 72), (-40, 78), (-20, 78), (-8, 77), (12, 66), (30, 52), (54, 44), (74, 24),
       (88, -10), (90, -50), (78, -88), (52, -112), (16, -124), (-22, -118)]
FACE_S = poly(_FS, flip=True)
NOSE = np.array([(-16, 70), (-8, 72), (0, 79), (6, 88), (9, 93.5), (12, 96), (16, 95), (20, 90), (23, 80)])   # (y, z front) units
# the neck (bust_view: front ±24 at the chin, the profile −30…14 → z −14…30), down into the jumper's collar
NECK_W = ([60, 90, 120, 150], [40, 33, 34, 38])
NECK_F = ([60, 88, 120, 150], [30, 26, 28, 34])
NECK_B = ([40, 70, 120, 150], [-74, -40, -18, -26])
Y_DRAW = [150.0, 88.0, 0.0, -124.0]       # the base head's landmarks here: the neck's end, chin, eye line, crown
REG = [(32, -2, 22, 22), (-32, -2, 22, 22), (0, 46, 30, 10)]      # where the face is drawn: eyes and mouth
NOSE_SPAN = (-16, 26)       # the nose's heights in the profile
