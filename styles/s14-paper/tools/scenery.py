"""С14 — what is behind the figures: all of it paper too."""
from kit import *


def mat(w, h, col):
    """A torn sheet of lighter paper laid on the background sheet."""
    m = 46
    return [torn([(m, m, 1), (w - m, m + 6, 1), (w - m - 4, h - m, 1), (m + 6, h - m - 8, 1)], col, 1)]


def floor(w, h, y, col):
    return [torn([(46, y - 30), (w * 0.3, y - 44), (w * 0.7, y - 36), (w - 48, y - 46), (w - 50, h - 46, 1), (52, h - 54, 1)], col, 1)]


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


def street(w, h, gy, evening=False):
    """Sky sheet (the Doc background), far hills torn from paper, a row of houses, the ground in two torn strips."""
    r = rnd(7 if not evening else 11)
    o = []
    o += sun(w - 210, 150, 58, '#f0b23c' if not evening else '#e8703c')
    o += cloud(260, 150, 1.3) + cloud(w * 0.55, 100, 1.0) + cloud(w - 520, 220, 0.8)
    hill = lambda y0, amp, col, lift, seed: torn([(-20, y0)] + [(i * w / 8, y0 - amp * (0.5 + 0.5 * rnd(seed + i).random())) for i in range(1, 8)] + [(w + 20, y0), (w + 20, h + 20, 1), (-20, h + 20, 1)], col, lift)
    o += [hill(gy - 250, 110, '#9cc0b4' if not evening else '#d99a7c', 1, 3), hill(gy - 170, 90, '#7fae96' if not evening else '#b8746a', 2, 9)]
    cols = ['#e7c36a', '#d9826a', '#8fb7c9', '#e9dcc0', '#c98aa0', '#9ab87a', '#e0a04c']
    roofs = ['#8a3b34', '#4c5a66', '#6b5546', '#3f7355']
    x = -10
    while x < w:
        hw = r.randint(84, 150)
        hh = r.randint(130, 300)
        o += house(x, gy - 60, hw, hh, r.choice(cols), r.choice(roofs), r)
        if r.random() < 0.3:
            o += tree(x + hw + 22, gy - 60, r.uniform(0.9, 1.3), '#5f9a6c' if not evening else '#a8643c')
            x += 44
        x += hw + r.randint(-6, 14)
    g1, g2 = ('#b7c98a', '#9fb673') if not evening else ('#c9a36a', '#a8824e')
    o += [torn([(-20, gy - 70), (w * 0.25, gy - 84), (w * 0.5, gy - 72), (w * 0.75, gy - 88), (w + 20, gy - 74), (w + 20, h + 20, 1), (-20, h + 20, 1)], g1, 2)]
    o += [torn([(-20, gy + 70), (w * 0.3, gy + 56), (w * 0.6, gy + 72), (w + 20, gy + 58), (w + 20, h + 20, 1), (-20, h + 20, 1)], g2, 2)]
    return o
