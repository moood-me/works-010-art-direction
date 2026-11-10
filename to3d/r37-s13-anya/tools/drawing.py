"""The drawing as numbers: Аня of С13 (styles/s13-ukiyo-e/tools/anya.py and parts.py — head_pts, layout, bust, figure)
as the silhouettes and heights the 3D is fitted to.
Units: the drawing's head units (a head is 200 high, the eye line y = 0, y down; chin 108, the hair's top −118). The
figure sheet draws the head at 0.46 of them: its eye line is 668 figure units over the soles → 1452 head units.
3D: metres, y up, the figure faces +z, its left is +x. Front view: drawing x → 3D x; the profile (drawn facing left) is
mirrored: 3D z = −x."""
import numpy as np

FLOOR = 1452.0          # the soles, in head units below the eye line
CROWN = -118.0          # top of the hair
HEIGHT = 1.68           # metres, hair top to soles
K = HEIGHT / (FLOOR - CROWN)
LONG = 1.08             # parts.P(long=…): the long oval of the shin-hanga beauties


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


# parts.head_pts(p, 'f') with long 1.08, cheek 0, jaw 0, chin −3
_FF = [(0, -100), (40, -94), (70, -68), (82, -30), (82, 0), (80, 28), (72, 56.2), (56, 84.2), (27, 102.6)]
FACE_F = dense(poly(_FF + [(0, 108)] + [(-x, y) for x, y in _FF[:0:-1]]))
# parts.head_pts(p, 's') (facing left) with the nose 'soft' 0.82: forehead, nose, lips, chin, the jaw to the ear, skull
_FS = [(0, -100), (-40, -95), (-66, -76), (-78, -46), (-80, -18), (-75, -2), (-83.3, 14), (-93.6, 27), (-90.7, 34),
       (-77, 37), (-78, 44), (-80, 51), (-76, 61.6), (-78, 68), (-73, 76.7), (-73.8, 91.8), (-63.1, 104.8), (-42, 104.8),
       (-12, 86.4), (14, 64.8), (24, 30), (40, 20), (90, -8), (99, -45), (82, -82), (46, -98)]
FACE_S = poly(_FS, flip=True)
NOSE = np.array([(-18, 79), (-2, 75), (14, 83.3), (27, 93.6), (34, 90.7), (37, 77)])      # (y, z front)
NOSE_SPAN = (-4, 40)
# parts.neck: a long thin neck (44 wide in front, 55 deep)
NECK_W = ([108, 140, 190], [23, 22, 28])
NECK_F = ([86, 108, 140, 190], [30, 18, 15, 20])
NECK_B = ([-8, 30, 60, 120, 190], [-90, -62, -44, -40, -44])
Y_DRAW = [190.0, 108.0, 0.0, -100.0]      # the base head's landmarks here: the neck's end, chin, eye line, crown
REG = [(33, 0, 26, 20), (-33, 0, 26, 20), (0, 67, 26, 14)]      # where the face is drawn: eyes and mouth
FACE_ONLY = (24, 106)     # head.py: between these heights the width is the face's in front of the ears
