"""Марат's drawing read as numbers: the outlines of his head (front and side) from the drawing's own code
(styles/s9-midcentury/tools/marat.py head('front'), head('side')), in its units (y down; head centre 0,0; the face's
top −110, chin 102; the curls reach −148, the beard 148)."""
import numpy as np
import common  # noqa: F401  (paths)
from kit import sample

K = 0.001414        # metres per drawing unit of the head (figure-marat draws the head at 0.62; 1 figure unit = 2.28 mm)
CROWN, CHIN = -112, 102
FRONT = [(0, -112), (44, -104), (72, -72), (82, -24), (80, 24), (70, 62), (46, 90), (0, 102), (-46, 90), (-70, 62),
         (-80, 24), (-82, -24), (-72, -72), (-44, -104)]
SIDE = [(-66, -30), (-56, -84), (-18, -112), (30, -108), (60, -84), (68, -48), (68, -14), (74, 0), (80, 30), (72, 50), (70, 70),
        (60, 92), (20, 100), (-30, 84), (-58, 50), (-70, 10)]
SIDE_NO_NOSE = [(-66, -30), (-56, -84), (-18, -112), (30, -108), (60, -84), (68, -48), (68, -14), (69, 20), (70, 50), (70, 70),
                (60, 92), (20, 100), (-30, 84), (-58, 50), (-70, 10)]
EAR_X = -16         # the side view's x of the head's axis (the drawing's ear is at −26; the base's ear sits a little forward of it)
NECK = dict(a=46, c0=-2, c=31, rings=((0.575, 112), (0.56, 126), (0.545, 140)))   # half-width, side centre, half-depth
JAW = (50, 92)      # heights where round cross-sections are asked for
BACK_MAX = 84


def curve(pts, per=24):
    return np.array(sample(pts, closed=True, per=per))


def extent(pts, y, side):
    """where a closed outline crosses height y: its largest (side=+1) or smallest (−1) x"""
    c = curve(pts); xs = []
    for i in range(len(c) - 1):
        (x0, y0), (x1, y1) = c[i], c[i + 1]
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
    if not xs: return None
    return max(xs) if side > 0 else min(xs)
