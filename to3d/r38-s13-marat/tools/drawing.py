"""The drawing as numbers: Марат of С13 (styles/s13-ukiyo-e/tools/marat.py and parts.py — head_pts, HAIRS, BEARDS,
bust, figure) as the silhouettes and heights the 3D is fitted to.
Units: the drawing's head units (a head is 200 high, the eye line y = 0, y down; chin 98, the beard to 126, the curls'
top about −128). The figure sheet draws the head at 0.5 of them: its eye line is 724 figure units over the soles →
1448 head units. 3D: metres, y up, the figure faces +z, its left is +x. Front view: drawing x → 3D x; the profile
(drawn facing left) is mirrored: 3D z = −x."""
import numpy as np

FLOOR = 1448.0          # the soles, in head units below the eye line
CROWN = -128.0          # top of the curls
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


# parts.head_pts(p, 'f') with long 0.98, cheek 11, jaw 14, chin 9: a square head
_FF = [(0, -100), (40, -94), (70, -68), (82, -30), (82, 0), (83.3, 28), (80.8, 51), (72.7, 76.4), (43.2, 93.1)]
FACE_F = dense(poly(_FF + [(0, 98)] + [(-x, y) for x, y in _FF[:0:-1]]))
# parts.head_pts(p, 's') (facing left), the nose 'broad' 1.12, the brow ridge 3
_FS = [(0, -100), (-40, -95), (-66, -76), (-78, -46), (-83, -18), (-75, -2), (-84.5, 14), (-96, 27), (-92.8, 34),
       (-77, 37), (-78, 44), (-80, 51), (-76, 55.9), (-78, 61.7), (-73, 69.6), (-78.6, 83.3), (-66.7, 95.1), (-42, 97.9),
       (-7.8, 82.6), (21, 63), (24, 30), (40, 20), (90, -8), (99, -45), (82, -82), (46, -98)]
FACE_S = poly(_FS, flip=True)
NOSE = np.array([(-18, 82), (-2, 76), (14, 84.5), (27, 96), (34, 92.8), (38, 78)])      # (y, z front)
NOSE_SPAN = (-4, 40)
# parts.neck(…, 90, …): a short thick neck, mostly behind the beard
NECK_W = ([98, 126, 170], [46, 48, 58])
NECK_F = ([80, 98, 126, 170], [50, 42, 44, 56])
NECK_B = ([-8, 30, 60, 120, 170], [-90, -76, -68, -70, -78])
Y_DRAW = [170.0, 98.0, 0.0, -100.0]       # the base head's landmarks here: the neck's end, chin, eye line, crown
REG = [(33, 0, 25, 19), (-33, 0, 25, 19), (0, 68, 42, 24)]      # where the face is drawn: eyes and the wide mouth
FACE_ONLY = (24, 96)      # head.py: between these heights the width is the face's in front of the ears
PUSH_TOP = -64.0          # head.py: the face made one plain round plane from the forehead down
FACE_R = 0.12
