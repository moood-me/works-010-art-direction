"""The drawing as numbers: Аня's own paths (styles/s3-graphic/tools/anya.py) sampled into polylines, and the
silhouettes the 3D is fitted to. Drawing units: the figure's own (eye line y=0, y down, shoe soles at y=1378);
3D: metres, y up, the figure faces +z, its left +x. Front view: drawing x → 3D x; profile (faces right): drawing x → 3D z."""
import os, re, sys
import numpy as np

S3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'styles', 's3-graphic', 'tools')
sys.path.insert(0, S3)
import anya  # noqa: E402
from lib import mx  # noqa: E402

FLOOR = 1378.0          # shoe soles
CROWN = -142.0          # top of the hair
HEIGHT = 1.62           # metres, crown to soles
K = HEIGHT / (FLOOR - CROWN)


def to3(xd, yd):
    return np.asarray(xd) * K, (FLOOR - np.asarray(yd)) * K


def to_d(y3):
    return FLOOR - np.asarray(y3) / K


def sample(d, n=24):
    """An absolute SVG path (M L C Q Z) → list of closed/open polylines (arrays N×2)."""
    toks = re.findall(r'[MLCQZmlcqz]|-?\d+(?:\.\d+)?', d)
    out, cur, i, cmd, p0 = [], [], 0, None, None
    pos = np.zeros(2)
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd in 'Zz':
                if cur:
                    cur.append(cur[0].copy()); out.append(np.array(cur)); cur = []
                pos = p0.copy() if p0 is not None else pos
                continue
        if cmd == 'M':
            if cur: out.append(np.array(cur))
            pos = np.array([num(), num()]); p0 = pos.copy(); cur = [pos.copy()]; cmd = 'L'
        elif cmd == 'L':
            pos = np.array([num(), num()]); cur.append(pos.copy())
        elif cmd == 'C':
            c1 = np.array([num(), num()]); c2 = np.array([num(), num()]); e = np.array([num(), num()])
            for s in np.linspace(0, 1, n + 1)[1:]:
                cur.append((1 - s) ** 3 * pos + 3 * (1 - s) ** 2 * s * c1 + 3 * (1 - s) * s * s * c2 + s ** 3 * e)
            pos = e
        elif cmd == 'Q':
            c1 = np.array([num(), num()]); e = np.array([num(), num()])
            for s in np.linspace(0, 1, n + 1)[1:]:
                cur.append((1 - s) ** 2 * pos + 2 * (1 - s) * s * c1 + s * s * e)
            pos = e
        else:
            raise ValueError(cmd)
    if cur: out.append(np.array(cur))
    return out


def span(polys, y):
    """Where a horizontal line at drawing-y crosses the shapes: (min x, max x) or None."""
    xs = []
    for P in polys:
        a, b = P[:-1], P[1:]
        m = (a[:, 1] - y) * (b[:, 1] - y) <= 0
        for p, q in zip(a[m], b[m]):
            if p[1] == q[1]: xs += [p[0], q[0]]
            else: xs.append(p[0] + (y - p[1]) / (q[1] - p[1]) * (q[0] - p[0]))
    return (min(xs), max(xs)) if xs else None


def profile(d, ys, n=24):
    P = sample(d, n)
    r = [span(P, y) for y in ys]
    return np.array([[np.nan, np.nan] if s is None else s for s in r])


# the shapes, by name
FRONT = dict(face=anya.FACE_F, hair_back=anya.BACK_F, curtain=anya.CURT_F, dress=anya.DRESS_F, card=anya.CARD_FL,
             arm=anya.ARM_FL)
SIDE = dict(face=anya.FACE_S, hair=anya.HAIR_S)
# the profile's dress and cardigan are local to anya.body_s(); copied here as they are there
SIDE['dress'] = ('M -40 196 C -10 206, 20 206, 40 196 C 60 300, 70 380, 54 420 C 92 640, 124 900, 126 1130 '
                 'C 40 1150, -60 1150, -136 1130 C -124 900, -92 640, -60 420 C -66 340, -60 260, -40 196 Z')
SIDE['card'] = ('M -40 188 C -76 200, -92 240, -94 300 L -100 460 C -102 540, -96 600, -90 652 C -40 664, 20 664, 60 650 '
                'C 64 560, 70 460, 62 400 C 66 330, 60 260, 40 192 Z')
