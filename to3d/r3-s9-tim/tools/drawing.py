"""Тим's drawing read as numbers: the outlines of figure-tim / turn-tim's head (front and side) from the drawing's own
code (styles/s9-midcentury/tools/tim.py), in its units (y down; head centre 0,0; crown −106, chin 88)."""
import numpy as np
import common  # noqa: F401  (paths)
from kit import sample

K = 0.0014          # metres per drawing unit of the head
FRONT = [(0, -106), (46, -96), (72, -60), (78, -10), (72, 34), (52, 66), (24, 84), (0, 88), (-24, 84), (-52, 66),
         (-72, 34), (-78, -10), (-72, -60), (-46, -96)]
SIDE = [(-66, -30), (-56, -84), (-14, -110), (36, -104), (64, -72), (70, -30), (70, 10), (80, 30), (84, 40, 'c'),
        (72, 46), (70, 58), (62, 72), (38, 86), (6, 86), (-24, 76), (-52, 50), (-68, 10)]
SIDE_NO_NOSE = [p for p in SIDE if p[:2] not in [(80, 30), (84, 40), (72, 46)]]
EAR_FRONT = (78, 12, 15, 21, 12)       # centre x, y, rx, ry, tilt (deg) — mirrored for the other ear
EAR_SIDE = (-8, 14)
NOSE = dict(front=(0, 34, 9, 8), side_tip=(84, 40))
EYES = dict(front=[(-24, 14), (24, 14)], side=(52, 12))
MOUTH = dict(front=(2, 58), side=(64, 58))


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
