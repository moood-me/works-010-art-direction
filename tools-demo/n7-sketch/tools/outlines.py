# Outlines of our characters traced by hand on their front pictures (our-<name>-front.png, shot by shoot_ours.cjs),
# drawn the way Monster Mash wants: one outline per body part, back to front; a part that grows out of another
# is an open stroke that starts and ends inside it (the app closes it with an invisible "Neumann" line, which
# makes the join smooth), a part lying on another (muzzle on the head) is a closed stroke.
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
  'bear': dict(src='our-bear-front.png', parts=[
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
  'cat': dict(src='our-cat-front.png', parts=[
    ('earL', poly([(230, 110), (246, 150), (272, 215), (226, 225), (230, 160)], 8), 'head'),
    ('earR', poly([(455, 104), (454, 160), (460, 220), (414, 212), (440, 150)], 8), 'head'),
    ('legL', tube([(310, 470), (306, 570), (302, 668)], 11, 9), 'body'),
    ('legR', tube([(382, 470), (386, 570), (392, 668)], 11, 9), 'body'),
    ('footL', ell(300, 705, 46, 30), 'legL'),
    ('footR', ell(398, 705, 46, 30), 'legR'),
    ('armL', tube([(300, 400), (276, 440), (262, 480)], 9, 9), 'body'),
    ('armR', tube([(392, 400), (414, 440), (432, 480)], 9, 9), 'body'),
    ('handL', poly([(222, 470), (250, 455), (285, 480), (290, 520), (250, 540), (225, 515)]), 'armL'),
    ('handR', poly([(470, 470), (442, 455), (405, 480), (400, 520), (442, 540), (467, 515)]), 'armR'),
    ('body', poly([(300, 385), (345, 375), (392, 385), (402, 440), (390, 495), (345, 512), (300, 495), (290, 440)]), 'head'),
    ('head', ell(345, 290, 133, 100), None),
  ]),
  'imp': dict(src='our-imp-front.png', parts=[
    ('hornL', poly([(256, 102), (268, 128), (286, 158), (246, 162), (250, 130)], 8), 'head'),
    ('hornR', poly([(372, 98), (382, 130), (390, 160), (352, 158), (362, 128)], 8), 'head'),
    ('tail', tube([(352, 470), (420, 410), (470, 330), (500, 268)], 7, 6), 'body'),
    ('tip', poly([(486, 270), (500, 236), (526, 236), (532, 262), (514, 280)]), 'tail'),
    ('legL', tube([(312, 470), (302, 570), (296, 668)], 12, 10), 'body'),
    ('legR', tube([(372, 470), (382, 570), (390, 668)], 12, 10), 'body'),
    ('hoofL', poly([(276, 662), (316, 662), (322, 712), (270, 712)]), 'legL'),
    ('hoofR', poly([(372, 662), (412, 662), (420, 712), (368, 712)]), 'legR'),
    ('armL', tube([(292, 340), (266, 410), (258, 480)], 11, 10), 'head'),
    ('armR', tube([(392, 340), (418, 410), (428, 480)], 11, 10), 'head'),
    ('handL', poly([(236, 480), (268, 470), (290, 510), (270, 540), (236, 528)]), 'armL'),
    ('handR', poly([(452, 480), (420, 470), (398, 510), (418, 540), (452, 528)]), 'armR'),
    ('body', poly([(312, 380), (340, 372), (368, 380), (380, 440), (372, 490), (340, 512), (306, 490), (298, 440)]), 'head'),
    ('earL', poly([(136, 180), (190, 190), (252, 200), (252, 240), (190, 218)], 8), 'head'),
    ('earR', poly([(554, 164), (500, 186), (438, 200), (438, 240), (500, 212)], 8), 'head'),
    ('head', ell(344, 262, 132, 122), None),
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
        img = Image.open(os.path.join(work, C['src'])).convert('RGB')
        allp = np.concatenate([c for _, c, _ in C['parts']])
        lo, hi = allp.min(0), allp.max(0)
        s = 760 / (hi[1] - lo[1]); cx, cy = (lo + hi) / 2
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
                   'canvas': CANVAS, 'names': [n for n, _, _ in C['parts']]}, open(os.path.join(out, 'frame.json'), 'w'))

if __name__ == '__main__':
    main(sys.argv[1])
