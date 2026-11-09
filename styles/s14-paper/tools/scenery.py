"""С14 — what is behind the figures: all of it paper too."""
from kit import *


def mat(w, h, col):
    """A torn sheet of lighter paper laid on the background sheet."""
    m = 46
    return [torn([(m, m, 1), (w - m, m + 6, 1), (w - m - 4, h - m, 1), (m + 6, h - m - 8, 1)], col, 1)]


def floor(w, h, y, col):
    return [torn([(74, y - 30), (w * 0.3, y - 44), (w * 0.7, y - 36), (w - 76, y - 46), (w - 80, h - 70, 1), (80, h - 76, 1)], col, 1)]


def house(x, y, w, h, col, roof, r=None, door=True):
    r = r or rnd(int(x))
    o = [paint([(x, y, 1), (x, y - h, 1), (x + w, y - h, 1), (x + w, y, 1)], col, 1, var=r.randint(0, 3)),
         card([(x - 8, y - h + 2, 1), (x + w / 2, y - h - w * 0.42, 1), (x + w + 8, y - h + 2, 1)], roof, 2)]
    n = max(1, int(w // 44))
    for j in range(int(h // 60)):
        for i in range(n):
            wx = x + (i + 0.5) * w / n - 9
            wy = y - h + 22 + j * 54
            if door and j == int(h // 60) - 1 and i == 0:
                continue
            o.append(card([(wx, wy, 1), (wx + 18, wy, 1), (wx + 18, wy + 26, 1), (wx, wy + 26, 1)], '#fbf1cf' if r.random() < 0.6 else '#4c5a66', 1))
    if door:
        o.append(card([(x + 10, y, 1), (x + 10, y - 40), (x + 21, y - 50), (x + 32, y - 40), (x + 32, y, 1)], dark(col, 0.45), 1))
    return o


def tree(x, y, s, col):
    return [card(strip([(x, y), (x + 2, y - 70 * s)], 9 * s), '#6b5546', 1),
            torn(ell(x + 2, y - 110 * s, 44 * s, 56 * s, n=10), col, 2), torn(ell(x - 20 * s, y - 84 * s, 26 * s, 30 * s, n=8), dark(col, 0.12), 2)]


def cloud(x, y, s):
    return [torn([(x - 70 * s, y), (x - 50 * s, y - 26 * s), (x - 10 * s, y - 44 * s), (x + 30 * s, y - 30 * s), (x + 70 * s, y - 4 * s), (x + 40 * s, y + 10 * s), (x - 40 * s, y + 12 * s)], '#fbf6ea', 2)]


def sun(x, y, r, col):
    rays = []
    for i in range(12):
        a = i * 30
        rays.append(rot(card([(x - r * 0.16, y - r * 1.25, 1), (x, y - r * 1.75, 1), (x + r * 0.16, y - r * 1.25, 1)], lite(col, 0.2), 1), a, (x, y)))
    return rays + [paint(ell(x, y, r, r, n=14), col, 2, var=2)]


def pine(x, y, s, col):
    o = [card(strip([(x, y), (x, y - 40 * s)], 8 * s), '#6b5546', 1)]
    for k in range(3):
        yy = y - 30 * s - k * 46 * s
        ww = (62 - k * 14) * s
        o.append(paint([(x - ww, yy, 1), (x, yy - 84 * s, 1), (x + ww, yy, 1)], dark(col, 0.10 * (2 - k)), 2, var=k))
    return o


def hung(x, y, piece_fn, top=-10):
    """Something hung from above on a thread, as in a paper theatre."""
    return [flat(strip([(x, top), (x, y)], 1.6), '#8a7a66')] + piece_fn(x, y)


def street(w, h, gy, evening=False):
    """A paper theatre: the sky sheet (the Doc background), a sun and clouds hung on threads, four rows of torn
    hills going back into tissue haze, paper trees, the ground in two torn strips."""
    o = []
    sky = ['#9cc3bd', '#7fb0a0', '#5f9a7c', '#4c8a66'] if not evening else ['#eebf8c', '#e0a070', '#c98060', '#a8684e']
    tr = '#3f7a5a' if not evening else '#2f5f62'
    o += hung(w * 0.72, 150, lambda x, y: sun(x, y, 60, '#f0b23c' if not evening else '#f6e2a0'))
    o += hung(250, 150, lambda x, y: cloud(x, y, 1.3)) + hung(w * 0.52, 110, lambda x, y: cloud(x, y, 1.0)) + hung(w - 130, 230, lambda x, y: cloud(x, y, 0.8))

    def hill(y0, amp, col, lift, seed, n=7):
        r = rnd(seed)
        return torn([(-20, y0)] + [(i * w / n, y0 - amp * r.random()) for i in range(1, n)] + [(w + 20, y0), (w + 20, h + 20, 1), (-20, h + 20, 1)], col, lift)
    haze = lambda y0: tissue([(-20, y0, 1), (w + 20, y0, 1), (w + 20, h, 1), (-20, h, 1)], '#fff8ea', 0.22)
    r = rnd(5 if not evening else 12)
    for k, (y0, amp) in enumerate(((gy - 330, 150), (gy - 230, 130), (gy - 140, 110))):
        o += [hill(y0, amp, sky[k], 2, 3 + k * 7 + (20 if evening else 0), 6 + k)]
        for j in range(3 + k):
            x = r.uniform(40, w - 40)
            sc = 0.55 + 0.3 * k
            o += pine(x, y0 + 30 + r.uniform(0, 30), sc, mix(sky[k + 1], tr, 0.5)) if r.random() < 0.6 else tree(x, y0 + 30, sc, mix(sky[k + 1], tr, 0.3))
        o += [haze(y0 + 40)]
    g1, g2 = (sky[3], dark(sky[3], 0.15))
    o += [torn([(-20, gy - 70), (w * 0.25, gy - 86), (w * 0.5, gy - 72), (w * 0.75, gy - 90), (w + 20, gy - 74), (w + 20, h + 20, 1), (-20, h + 20, 1)], mix(g1, '#c9d88a' if not evening else '#d9a070', 0.55), 2)]
    o += [torn([(-20, gy + 76), (w * 0.3, gy + 62), (w * 0.6, gy + 78), (w + 20, gy + 64), (w + 20, h + 20, 1), (-20, h + 20, 1)], mix(g2, '#b7c97a' if not evening else '#b8804e', 0.5), 2)]
    return o


def bunting(w, y, n=14, cols=('#c9412f', '#e0ae38', '#6c9bc4', '#fbf6ea', '#c9623a', '#5b2f57')):
    """A string of paper flags across the sheet."""
    import math
    o = []
    pts = [(i * w / n, y + 60 * math.sin(math.pi * i / n) ) for i in range(n + 1)]
    o.append(flat(strip(pts, 2), '#6b5546'))
    for i in range(1, n):
        x, yy = pts[i]
        o.append(card([(x - 20, yy, 1), (x + 20, yy + 2, 1), (x + 2, yy + 46, 1)], cols[i % len(cols)], 2))
    return o
