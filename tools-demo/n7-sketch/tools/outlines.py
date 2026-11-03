# Outlines of our characters traced by hand on their front pictures (our-<name>-front.png, shot by shoot_ours.cjs),
# drawn the way Monster Mash wants: one outline per body part, back to front; a part that grows out of another
# is an open stroke that starts and ends inside it (the app closes it with an invisible "Neumann" line, which
# makes the join smooth), a part lying on another (muzzle on the head) is a closed stroke.
# Colours (frame.json): parts in 'tex' carry the picture (face, stripes) on their front side; the others, and every
# back side, are one colour each - the median of the picture over the part, or the one given in 'colors'.
# usage: python3 outlines.py <workdir>   -> <workdir>/<name>/shape.txt, frame.json, trace.png
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw

CANVAS = 1000

def catmull(pts, n=12):
    """a smooth closed curve through the points"""
    P = np.array(pts, float); out = []
    for i in range(len(P)):
        p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % len(P)], P[(i + 2) % len(P)]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return np.array(out)

def ell(cx, cy, rx, ry, rot=0, n=120):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False); c, s = math.cos(rot), math.sin(rot)
    x, y = rx * np.cos(t), ry * np.sin(t)
    return np.stack([cx + c * x - s * y, cy + s * x + c * y], 1)

def tube(pts, r0, r1, n=10):
    """a tapered limb along a smooth path: radius r0 at the start, r1 at the end, round ends"""
    P = catmull_open(pts, n)
    d = np.gradient(P, axis=0); d /= np.linalg.norm(d, axis=1, keepdims=True); nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    r = np.linspace(r0, r1, len(P))[:, None]
    left, right = P + nrm * r, P - nrm * r
    a0 = math.atan2(d[0, 1], d[0, 0]); a1 = math.atan2(d[-1, 1], d[-1, 0])
    cap1 = [P[-1] + r1 * np.array([math.cos(a1 + math.pi / 2 - t), math.sin(a1 + math.pi / 2 - t)]) for t in np.linspace(0, math.pi, 12)[1:-1]]
    cap0 = [P[0] + r0 * np.array([math.cos(a0 - math.pi / 2 - t), math.sin(a0 - math.pi / 2 - t)]) for t in np.linspace(0, math.pi, 12)[1:-1]]
    return np.concatenate([left, np.array(cap1), right[::-1], np.array(cap0)])

def catmull_open(pts, n=10):
    P = np.array(pts, float); P = np.concatenate([[2 * P[0] - P[1]], P, [2 * P[-1] - P[-2]]]); out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2]); return np.array(out)

def poly(pts, n=12): return catmull(pts, n)

# —— the characters: (name, closed curve, the part it grows out of or None), back to front; coordinates of the front picture
CHARS = {
  'bear': dict(src='our-bear-front.png', tex=['head', 'muzzle', 'body'], thin=True, colors={}, parts=[
    ('earL', ell(113, 115, 31, 30), 'head'),
    ('earR', ell(328, 106, 31, 30), 'head'),
    ('legL', poly([(158, 290), (234, 290), (236, 362), (224, 378), (168, 378), (155, 364)]), 'body'),
    ('legR', poly([(238, 290), (316, 290), (318, 364), (306, 378), (250, 378), (238, 362)]), 'body'),
    ('armL', tube([(172, 225), (128, 258), (100, 284)], 24, 25), 'body'),
    ('armR', tube([(288, 225), (334, 256), (376, 282)], 24, 25), 'body'),
    ('body', poly([(160, 205), (228, 200), (298, 205), (310, 250), (305, 295), (230, 305), (155, 295), (146, 250)]), 'head'),
    ('head', ell(228, 147, 128, 62), None),
    ('muzzle', ell(228, 185, 62, 23), None),
  ]),
  'cat': dict(src='our-cat-front.png', tex=['head', 'body'], thin=False, colors={'handL': '#f1ecf7', 'handR': '#f1ecf7', 'footL': '#f1ecf7', 'footR': '#f1ecf7'}, parts=[
    ('earL', poly([(236, 114), (250, 170), (272, 250), (232, 255), (234, 180)], 8), 'head'),
    ('earR', poly([(452, 110), (454, 180), (458, 250), (418, 245), (436, 170)], 8), 'head'),
    ('legL', tube([(310, 470), (304, 560), (296, 650)], 10, 9), 'body'),
    ('legR', tube([(378, 470), (388, 560), (400, 650)], 10, 9), 'body'),
    ('footL', ell(282, 668, 38, 27), 'legL'),
    ('footR', ell(434, 670, 38, 27), 'legR'),
    ('armL', tube([(292, 396), (272, 430), (264, 466)], 10, 10), 'body'),
    ('armR', tube([(398, 396), (418, 430), (424, 466)], 10, 10), 'body'),
    ('handL', poly([(244, 452), (272, 444), (304, 466), (310, 500), (282, 516), (248, 500)]), 'armL'),
    ('handR', poly([(464, 456), (436, 446), (398, 470), (394, 504), (424, 520), (462, 504)]), 'armR'),
    ('body', poly([(290, 390), (340, 380), (396, 390), (408, 440), (394, 484), (342, 498), (292, 484), (280, 440)]), 'head'),
    ('head', ell(345, 278, 166, 112), None),
  ]),
  'imp': dict(src='our-imp-front.png', tex=['head', 'body'], thin=False, colors={'handL': '#3b1c1e', 'handR': '#3b1c1e', 'tip': '#3b1c1e', 'hoofL': '#3b1c1e', 'hoofR': '#3b1c1e', 'hornL': '#3b1c1e', 'hornR': '#3b1c1e'}, parts=[
    ('hornL', poly([(312, 96), (322, 120), (340, 150), (300, 156), (304, 120)], 8), 'head'),
    ('hornR', poly([(396, 94), (404, 120), (404, 150), (366, 146), (380, 118)], 8), 'head'),
    ('tail', tube([(390, 440), (430, 380), (468, 330), (500, 292)], 7, 6), 'body'),
    ('tip', poly([(494, 296), (500, 258), (520, 250), (538, 268), (520, 300)]), 'tail'),
    ('legL', tube([(318, 450), (310, 560), (300, 664)], 12, 10), 'body'),
    ('legR', tube([(386, 450), (404, 560), (424, 664)], 12, 10), 'body'),
    ('hoofL', poly([(280, 652), (322, 652), (326, 700), (274, 700)]), 'legL'),
    ('hoofR', poly([(406, 648), (446, 648), (450, 700), (402, 700)]), 'legR'),
    ('armL', tube([(290, 340), (276, 400), (268, 456)], 10, 10), 'head'),
    ('armR', tube([(418, 340), (432, 400), (440, 456)], 10, 10), 'head'),
    ('handL', poly([(250, 450), (285, 452), (312, 500), (300, 540), (262, 540), (248, 500)]), 'armL'),
    ('handR', poly([(468, 452), (436, 452), (392, 500), (404, 544), (446, 544), (470, 500)]), 'armR'),
    ('body', poly([(322, 378), (362, 370), (402, 378), (420, 420), (410, 460), (362, 476), (316, 460), (306, 420)]), 'head'),
    ('earL', poly([(138, 180), (190, 196), (250, 205), (250, 245), (190, 222)], 8), 'head'),
    ('earR', poly([(556, 168), (500, 192), (450, 198), (450, 240), (500, 218)], 8), 'head'),
    ('head', ell(350, 258, 134, 122), None),
  ]),
  # the tool's own kind of case: a creature drawn from scratch in side view (no picture under it), canvas pixels
  'monster': dict(src=None, tex=[], thin=False, colors={}, parts=[
    ('legFarF', tube([(400, 520), (392, 680), (380, 800)], 26, 22), 'body'),
    ('legFarB', tube([(650, 520), (662, 680), (670, 800)], 28, 22), 'body'),
    ('tail', tube([(700, 470), (790, 430), (850, 340), (868, 280)], 30, 12), 'body'),
    ('body', ell(550, 500, 205, 110), 'head'),
    ('legF', tube([(350, 540), (336, 680), (326, 805)], 34, 28), 'body'),
    ('legB', tube([(700, 540), (712, 680), (722, 805)], 36, 28), 'body'),
    ('ear', poly([(320, 300), (350, 210), (380, 200), (370, 290)], 8), 'head'),
    ('head', ell(300, 380, 120, 88, -0.15), None),
    ('eye', ell(260, 352, 20, 22), None),
  ]),
}

def contains(poly, pts):
    """even-odd point in polygon"""
    x, y = pts[:, 0][:, None], pts[:, 1][:, None]
    x0, y0 = poly[:, 0][None], poly[:, 1][None]; x1, y1 = np.roll(poly[:, 0], -1)[None], np.roll(poly[:, 1], -1)[None]
    cross = ((y0 > y) != (y1 > y)) & (x < (x1 - x0) * (y - y0) / (y1 - y0 + 1e-12) + x0)
    return cross.sum(1) % 2 == 1

def stroke(curve, parent):
    """the open stroke a person would draw: the part's outline outside the parent, its ends a little inside it"""
    if parent is None: return np.concatenate([curve, curve[:1]])
    inside = contains(parent, curve)
    if inside.all(): raise ValueError('part entirely inside its parent')
    if not inside.any(): return np.concatenate([curve, curve[:1]])
    n = len(curve); start = next(i for i in range(n) if inside[i - 1] and not inside[i])
    run = []; i = start
    while not inside[i % n]: run.append(i % n); i += 1
    # reach into the parent: a few points on both ends
    k = 3
    idx = [(run[0] - j) % n for j in range(k, 0, -1)] + run + [(run[-1] + j) % n for j in range(1, k + 1)]
    return curve[idx]

def main(work):
    for name, C in CHARS.items():
        if C['src']:
            img = Image.open(os.path.join(work, C['src'])).convert('RGB')
            allp = np.concatenate([c for _, c, _ in C['parts']])
            lo, hi = allp.min(0), allp.max(0)
            s = 760 / (hi[1] - lo[1]); cx, cy = (lo + hi) / 2
        else:
            img = Image.new('RGB', (CANVAS, CANVAS), (255, 255, 255)); s = 1; cx = cy = CANVAS / 2
        T = lambda P: np.stack([(P[:, 0] - cx) * s + CANVAS / 2, (P[:, 1] - cy) * s + CANVAS / 2], 1)
        curves = {n: c for n, c, _ in C['parts']}
        out = os.path.join(work, name); os.makedirs(out, exist_ok=True)
        L = [f'size {CANVAS} {CANVAS}']
        im = img.copy(); d = ImageDraw.Draw(im)
        for n, c, par in C['parts']:
            st = stroke(c, curves[par] if par else None)
            L.append(f'part {n}'); L += [f'p {x:.1f} {y:.1f}' for x, y in T(st)]; L.append('end')
            d.line([tuple(p) for p in st], fill=(0, 140, 255), width=2)
            d.line([tuple(st[-1]), tuple(st[0])], fill=(0, 200, 80), width=1)
        open(os.path.join(out, 'shape.txt'), 'w').write('\n'.join(L) + '\n')
        im.save(os.path.join(out, 'trace.png'))
        json.dump({'src': C['src'], 'imgW': img.width, 'imgH': img.height, 'cx': float(cx), 'cy': float(cy), 's': float(s),
                   'canvas': CANVAS, 'names': [n for n, _, _ in C['parts']],
                   'tex': C['tex'], 'thin': C['thin'], 'colors': C['colors']}, open(os.path.join(out, 'frame.json'), 'w'))

if __name__ == '__main__':
    main(sys.argv[1])
