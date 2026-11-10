"""The drawing's numbers for the 3D, taken from the style's own code (styles/s15-noir/tools), and the drawing's
pictures to compare with.
  python3 drawing.py sav            -> web/sav_drawing.json (head outlines front and side, features, colours)
  python3 drawing.py sav refs DIR   -> DIR/ref-<view>-<expr>.svg: the style's bust in each view / expression"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../../../styles/s15-noir/tools'))
import head as H            # noqa: E402
import build as B           # noqa: E402
from cast import CAST, REST  # noqa: E402
from noir import svg, g     # noqa: E402


def flatten(pts, n=10):
    """The path noir.d draws through the points (hard corners, smooth ones as its cubics), as a closed polyline."""
    m = len(pts)

    def tan(i):
        if len(pts[i]) < 3:
            return (0.0, 0.0)
        a, b = pts[(i - 1) % m], pts[(i + 1) % m]
        return ((b[0] - a[0]) / 6.0, (b[1] - a[1]) / 6.0)
    out = []
    for i in range(m):
        j = (i + 1) % m
        p, q = pts[i], pts[j]
        t0, t1 = tan(i), tan(j)
        if t0 == (0, 0) and t1 == (0, 0):
            out.append([p[0], p[1]])
            continue
        c1 = (p[0] + t0[0], p[1] + t0[1]); c2 = (q[0] - t1[0], q[1] - t1[1])
        for k in range(n):
            t = k / n; u = 1 - t
            out.append([u ** 3 * p[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * q[0],
                        u ** 3 * p[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * q[1]])
    return [[round(x, 2), round(y, 2)] for x, y in out]


def export(k):
    p = CAST[k]
    f = H.front_outline(p); s = H.side_outline(p)
    fo = [f[n] for n in ['crown', 'tr', 'templer', 'cheekr', 'jawr', 'chinr', 'chinl', 'jawl', 'cheekl', 'templel', 'tl']]
    # the side outline without the nose and the lips' teeth: the face's front as a plane line (the nose is its own form)
    so = [s[n] for n in ['crown', 'backtop', 'back', 'occ', 'nape', 'jaw', 'chinb', 'chin', 'chinfold', 'lipl', 'mouth', 'lipu', 'nosebase', 'root', 'brow', 'fore']]
    out = dict(front=flatten(fo), side=flatten(so), sidePts={n: list(s[n][:2]) for n in s}, frontPts={n: list(f[n][:2]) for n in f},
               eye_y=p['eye_y'], eye=p['eye'], brow=p['brow'], nose=p['nose'], mouth=p['mouth'], ear=p['ear'], neck=p['neck'], socket=p['socket'],
               skin=p['skin'], lip=p['lip'], iris=p['iris'], browcol=p['browcol'], white=p['white'], rest=REST[k],
               hide_far_eye=bool(p.get('hide_far_eye')), expr={n: e for n, e in H.EXPR.items()})
    json.dump(out, open(os.path.join(HERE, 'web', k + '_drawing.json'), 'w'), ensure_ascii=False)
    print('web/%s_drawing.json' % k)


def refs(k, out):
    """Busts as the style's turnaround draws them (head units ×2, the head's centre at (300, 300) of a 600×700 picture)."""
    os.makedirs(out, exist_ok=True)
    c1 = B.BACK[k][0]
    for v in 'fqs':
        for e in [REST[k], 'calm', 'joy', 'surprise', 'sadness', 'anger']:
            inner = f'<rect width="600" height="700" fill="{c1}"/>' + B.bustfig(v, k, e, 300, 300, 2.0)
            open(os.path.join(out, f'ref-{v}-{e}.svg'), 'w').write(svg(600, 700, inner))
    print(out)


if __name__ == '__main__':
    k = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == 'refs':
        refs(k, sys.argv[3])
    else:
        export(k)
