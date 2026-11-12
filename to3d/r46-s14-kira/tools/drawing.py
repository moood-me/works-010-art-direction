"""Кира's drawing read as numbers: the outlines of her head and hair (front and side) from the drawing's own code
(styles/s14-paper/tools/kira.py, face.py), in head_front's units (y down; the face piece's centre 0,0; its top −98,
the chin 107). The side view looks to +x; a side x is a depth z = x + ZOFF."""
import numpy as np
import common  # noqa: F401  (paths)
import face as F
import kira as KR

K = 0.56 * 0.0028        # metres per head unit (the figure draws the head at 0.56; 1 figure unit = 2.8 mm)
U = 0.0028               # metres per figure unit
ZOFF = 8.0
SPEC = dict(F.DEFAULT); SPEC.update(KR.SPEC)
FRONT = F.outline(SPEC, 0)
SIDE = F.outline(SPEC, 1)
CHIN = SPEC['ry'] * (1 + SPEC['chin'])
_back, _side, _fringe = KR.front_pieces()
BACK_F, SIDE_F, FRINGE_F = _back[0].pts, _side[0].pts, _fringe[0].pts
HAIR_S = KR.head(1)[3][-2][0].pts          # the profile's one hair piece


def curve(pts, per=16):
    """the closed curve kit.path_d draws through the points ((x, y, 1) is a corner), as a polyline"""
    n = len(pts); P = [np.array(p[:2], float) for p in pts]; C = [len(p) > 2 and p[2] for p in pts]
    out = []
    for i in range(n):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        c1 = p1 if C[i] else p1 + (p2 - p0) / 6
        c2 = p2 if C[(i + 1) % n] else p2 - (p3 - p1) / 6
        for t in np.arange(per) / per:
            out.append((1 - t) ** 3 * p1 + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * p2)
    return np.array(out)


def extent(pts, y, side):
    """where a closed outline crosses height y: its largest (side=+1) or smallest (−1) x"""
    c = curve(pts); c = np.r_[c, c[:1]]; xs = []
    for i in range(len(c) - 1):
        (x0, y0), (x1, y1) = c[i], c[i + 1]
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
    if not xs: return None
    return max(xs) if side > 0 else min(xs)


def sdf(poly, X):
    """signed distance of points X (N×2) to a closed polyline (M×2): negative inside"""
    A = poly; Bp = np.roll(poly, -1, 0); d = Bp - A
    P = X[:, None, :] - A[None]
    t = np.clip((P * d).sum(-1) / np.maximum((d * d).sum(-1), 1e-12), 0, 1)
    dist = np.linalg.norm(P - t[..., None] * d, axis=-1).min(1)
    x, y = X[:, 0][:, None], X[:, 1][:, None]
    y0, y1 = A[:, 1][None], Bp[:, 1][None]; x0, x1 = A[:, 0][None], Bp[:, 0][None]
    cross = ((y0 <= y) != (y1 <= y)) & (x < x0 + (y - y0) / np.where(y1 == y0, 1e-12, y1 - y0) * (x1 - x0))
    inside = cross.sum(1) % 2 == 1
    return np.where(inside, -dist, dist)


if __name__ == '__main__':
    print('front', np.round(curve(FRONT).min(0)), np.round(curve(FRONT).max(0)))
    print('side', np.round(curve(SIDE).min(0)), np.round(curve(SIDE).max(0)))
    print('hair side', HAIR_S)
