"""Аня's drawing read as numbers: the outlines of her head (front and side) from the drawing's own code
(styles/s9-midcentury/tools/anya.py head('front'), head('side')), in its units (y down; head centre 0,0; chin 97; the
face's top −104 under the fringe, the hair's top −132). The skull under the hair is ours: the face outline carried up to
a crown at −118 and round to a back at −78 (the bob's back is at −96)."""
import numpy as np
import common  # noqa: F401  (paths)
from kit import sample

K = 0.00114         # metres per drawing unit of the head (figure-anya draws the head at 0.5; 1 figure unit = 2.28 mm)
CROWN, CHIN = -118, 97
FRONT = [(0, -118), (46, -106), (70, -62), (72, -10), (64, 34), (46, 70), (20, 92), (0, 97), (-20, 92), (-46, 70),
         (-64, 34), (-72, -10), (-70, -62), (-46, -106)]
SIDE = [(-78, -30), (-66, -88), (-22, -118), (26, -116), (54, -86), (64, -50), (66, -14), (64, 4), (70, 24), (78, 36, 'c'),
        (68, 42), (64, 50), (66, 58), (62, 64), (64, 72), (56, 86), (36, 96), (10, 94), (-10, 80), (-34, 62), (-62, 40), (-76, 6)]
SIDE_NO_NOSE = [(-78, -30), (-66, -88), (-22, -118), (26, -116), (54, -86), (64, -50), (66, -14), (65, 12), (65, 40), (63, 62),
                (56, 86), (36, 96), (10, 94), (-10, 80), (-34, 62), (-62, 40), (-76, 6)]
EAR_X = -8          # the side view's x of the head's axis (the ear, under the bob)
NECK = dict(a=20, c0=2, c=19, rings=((0.575, 108), (0.56, 122), (0.545, 138)))   # half-width, side centre, half-depth
JAW = (45, 86)      # heights where round cross-sections are asked for
BACK_MAX = 80


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
