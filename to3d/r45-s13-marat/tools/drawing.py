"""Марат's drawing as numbers: the head's outlines of styles/s13-ukiyo-e (parts.head_pts with marat.p — front and
side), sampled; and the units. Head units ('hu'): the style's own (a head is 200 high, the eye line y = 0, y down);
in the figure the head is drawn at 0.5, a figure unit ('fu') is 2 hu; the figure is 800 fu high.
3D: metres, y up, the figure faces +z, its left is +x. Front view: drawing x → 3D x; side view (drawn looking left):
drawing x → −z."""
import os, sys
import numpy as np

S13 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'styles', 's13-ukiyo-e', 'tools')
sys.path.insert(0, S13)
import kit, parts, marat  # noqa: E402

HEIGHT = 1.95                 # metres, the top of the hair
KF = HEIGHT / 784.0           # a figure unit (the hair's top is at 784 fu: the head's centre 724, 0.5 × 117 above)
HEADK = 1.2                  # the head a little bigger than the figure draws it (nearer the bust sheets)
K = KF / 2 * HEADK            # a head unit
EYE = 724 * KF                # the eye line's height
FLOOR = EYE / K               # the floor in head units (y down from the eye line)


def poly(pts, flip=False):
    sm = kit.curve(pts, True, 10)
    return np.array([(-x if flip else x, y) for x, y in sm] + [(-sm[0][0] if flip else sm[0][0], sm[0][1])])


def span(P, y):
    a, b = P[:-1], P[1:]
    m = (a[:, 1] - y) * (b[:, 1] - y) <= 0
    xs = []
    for p, q in zip(a[m], b[m]):
        if p[1] == q[1]: xs += [p[0], q[0]]
        else: xs.append(p[0] + (y - p[1]) / (q[1] - p[1]) * (q[0] - p[0]))
    return (min(xs), max(xs)) if xs else (np.nan, np.nan)


def profile(P, ys):
    return np.array([span(P, y) for y in ys])


FRONT = dict(face=poly(parts.head_pts(marat.p, 'f')))
SIDE = dict(face=poly(parts.head_pts(marat.p, 's'), flip=True))      # now x → +z (the face looks to +x)
