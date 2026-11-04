"""The painted places the cast stands in: a summer meadow under tall clouds (Аня, the four together), a
watchmaker's workshop (Савелий Петрович), a sunlit green thicket (Тим), a study with books at evening (Вера)."""
import random
import numpy as np
from shapely.geometry import Point, box, Polygon
from shapely.ops import unary_union
from backdrop import grad, painted, cloud, foliage, grass, flowers, sky


def meadow(d, w, h, horizon=0.62, seed=1, far=True):
    rnd = random.Random(seed)
    ro = d.rough(0.02, 7, seed)
    ro2 = d.rough(0.05, 4, seed + 1)
    sky(d, w, h * horizon + 40, '#4f8fcf', '#d8e8ee')
    # a tall cumulus heap on one side, smaller ones drifting, flat thin ones low near the horizon
    for cx, cy, cw, ch in ((0.74, 0.50, 0.42, 0.40), (0.16, 0.30, 0.22, 0.12), (0.40, 0.18, 0.14, 0.06),
                           (0.30, 0.54, 0.34, 0.10), (0.98, 0.26, 0.18, 0.10), (0.55, 0.58, 0.20, 0.05)):
        cloud(d, cx * w, cy * h * horizon / 0.62, cw * w, ch * h, rnd, ro)
    hy = h * horizon
    if far:
        # far hills, blue-green, then a darker band of woods
        g = Polygon([(0, hy + 10), (0, hy - 30), (w * 0.2, hy - 55), (w * 0.45, hy - 35), (w * 0.7, hy - 60),
                     (w, hy - 30), (w, hy + 10)])
        painted(d, g, '#7fa3a8', ro)
        g2 = unary_union([Point(rnd.uniform(0, w), hy - rnd.uniform(0, 14)).buffer(rnd.uniform(14, 30), 12)
                          for _ in range(int(w / 25))]).union(box(0, hy - 5, w, hy + 20))
        foliage(d, g2.intersection(box(0, 0, w, hy + 20)), '#4f7f52', rnd, ro2, n=int(w / 8), r=(6, 14))
    grad(d, 0, hy + 12, w, h - hy, [(0, '#8db35a'), (0.5, '#73a14a'), (1, '#5a8a3c')])
    d.mottle(0.012, 0.35, seed)
    flowers(d, 0, w, hy + 30, h, ['#f4f0e6', '#f2d36a', '#e9a0b0'], rnd, n=int(w / 18))


def meadow_front(d, w, h, seed=2):
    """tall grass in front of the feet."""
    rnd = random.Random(seed)
    ro = d.rough(0.06, 3, seed)
    grass(d, -20, w + 20, h + 6, h * 0.10, '#6d9a44', rnd, ro, n=int(w / 3))


def workshop(d, w, h, seed=3):
    """a warm wall of a small workshop: wainscot, shelves, clocks on the wall, light from a window on the left."""
    rnd = random.Random(seed)
    ro = d.rough(0.03, 5, seed)
    grad(d, 0, 0, w, h, [(0, '#b88a56'), (0.6, '#a87a4a'), (1, '#7a5634')])
    # window light falling on the wall
    gl = d.blur(40)
    d.add(f'<path d="M{w * 0.02},{h * 0.05} L{w * 0.38},{h * 0.02} L{w * 0.30},{h * 0.75} L{-w * 0.02},{h * 0.8}Z" '
          f'fill="#ffe2a8" opacity="0.45" filter="url(#{gl})"/>')
    # a shelf with small boxes and a lamp
    painted(d, box(-10, h * 0.66, w + 10, h * 0.69), '#5e3e26', ro)
    painted(d, box(-10, h * 0.69, w + 10, h * 0.72), '#4a2f1d', ro)
    x = 10
    while x < w:
        bw = rnd.uniform(25, 60)
        bh = rnd.uniform(18, 50)
        c = rnd.choice(['#6f5a44', '#8a6a46', '#5d6a5a', '#7a4a3a', '#9a8a6a'])
        painted(d, box(x, h * 0.66 - bh, x + bw, h * 0.66), c, ro)
        x += bw + rnd.uniform(8, 30)
    # clocks on the wall
    for cx, cy, r in ((0.16, 0.20, 0.07), (0.84, 0.16, 0.09), (0.70, 0.42, 0.05), (0.08, 0.48, 0.05),
                      (0.93, 0.50, 0.06)):
        X, Y, R = cx * w, cy * h, r * w
        painted(d, Point(X, Y).buffer(R * 1.18, 32), '#5a3a22', ro)
        painted(d, Point(X, Y).buffer(R, 32), '#efe2c4', ro)
        for k in range(12):
            a = k / 12 * 2 * np.pi
            d.line(np.array([[X + np.cos(a) * R * 0.78, Y + np.sin(a) * R * 0.78],
                             [X + np.cos(a) * R * 0.9, Y + np.sin(a) * R * 0.9]]), max(1.0, R * 0.04), '#5a4636')
        a1, a2 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
        d.line(np.array([[X, Y], [X + np.cos(a1) * R * 0.5, Y + np.sin(a1) * R * 0.5]]), R * 0.06, '#3a2a20')
        d.line(np.array([[X, Y], [X + np.cos(a2) * R * 0.72, Y + np.sin(a2) * R * 0.72]]), R * 0.04, '#3a2a20')
    # the bench edge at the bottom
    painted(d, box(-10, h * 0.9, w + 10, h + 10), '#6a4428', ro)
    d.mottle(0.015, 0.4, seed)


def thicket(d, w, h, seed=4):
    """sunlit summer trees: two big masses of leaves left and right, sky and a cloud between, bushes below."""
    rnd = random.Random(seed)
    ro = d.rough(0.025, 6, seed)
    sky(d, w, h, '#5b97cf', '#d4e6ea')
    cloud(d, w * 0.55, h * 0.42, w * 0.55, h * 0.25, rnd, ro)
    left = unary_union([Point(rnd.uniform(-0.2, 0.30) * w, rnd.uniform(-0.1, 0.75) * h).buffer(rnd.uniform(0.10, 0.2) * w, 18)
                        for _ in range(9)])
    right = unary_union([Point(rnd.uniform(0.80, 1.2) * w, rnd.uniform(-0.1, 0.6) * h).buffer(rnd.uniform(0.10, 0.18) * w, 18)
                         for _ in range(7)])
    low = unary_union([Point(rnd.uniform(-0.1, 1.1) * w, rnd.uniform(0.78, 1.0) * h).buffer(rnd.uniform(0.08, 0.14) * w, 18)
                       for _ in range(12)])
    painted(d, box(w * 0.08, h * 0.2, w * 0.13, h), '#5a4a38', ro)
    for reg, base in ((left, '#4a8442'), (right, '#4f8a46'), (low, '#5a9448')):
        foliage(d, reg.intersection(box(0, 0, w, h)), base, rnd, ro, n=int(reg.area / 900), r=(10, 24))
    d.mottle(0.012, 0.35, seed)


def study(d, w, h, seed=5):
    """a study at evening: a bookcase, a lamp's warm pool of light on a cool wall."""
    rnd = random.Random(seed)
    ro = d.rough(0.03, 4, seed)
    grad(d, 0, 0, w, h, [(0, '#56676e'), (1, '#3e4c55')])
    # the bookcase on the left two thirds
    bx1 = w * 0.62
    painted(d, box(-10, -10, bx1, h + 10), '#4a3a30', ro)
    for row in range(5):
        y0 = h * (0.03 + row * 0.2)
        y1 = y0 + h * 0.17
        painted(d, box(0, y1, bx1 - 10, y1 + h * 0.03), '#5e4838', ro)
        x = 6
        while x < bx1 - 20:
            bw = rnd.uniform(8, 20)
            bh = rnd.uniform(0.75, 0.98) * (y1 - y0)
            c = rnd.choice(['#7a3a32', '#3f5a6a', '#8a7a52', '#5a4a6a', '#4a6a4a', '#9a6a3a', '#c8b88a', '#6a2a2a'])
            painted(d, box(x, y1 - bh, x + bw, y1), c, ro)
            if rnd.random() < 0.5:
                d.add(f'<rect x="{x + 2:.0f}" y="{y1 - bh * 0.8:.0f}" width="{bw - 4:.0f}" height="2" fill="#e8d8a0" opacity="0.6"/>')
            x += bw + rnd.uniform(0, 3)
    # lamp glow on the right
    gl = d.blur(60)
    d.add(f'<circle cx="{w * 0.85}" cy="{h * 0.35}" r="{w * 0.28}" fill="#f0b870" opacity="0.45" filter="url(#{gl})"/>')
    d.mottle(0.015, 0.4, seed)


def workshop_floor(d, w, h, y, seed=6):
    ro = d.rough(0.03, 4, seed)
    grad(d, 0, y, w, h - y, [(0, '#7a5434'), (1, '#5a3a22')])
    for k in range(6):
        yy = y + (h - y) * (k / 6) ** 1.4
        d.add(f'<rect x="0" y="{yy:.0f}" width="{w}" height="1.5" fill="#4a2e1a" opacity="0.5"/>')


def ground_shadow(d, view, F, w=1.0):
    """a soft flat shadow on the ground under the feet."""
    J = F.J
    pts = [J['anl'], J['anr']]
    c = (pts[0] + pts[1]) / 2
    c = np.array([c[0], 0.0, c[2]])
    p = view.xy(c[None])[0]
    span = abs(view.xy(np.array([[J['anl'][0], 0, J['anl'][2]]]))[0][0] - view.xy(np.array([[J['anr'][0], 0, J['anr'][2]]]))[0][0])
    rx = (span / 2 + 16 * view.s) * w
    d.add(f'<ellipse cx="{p[0]:.1f}" cy="{p[1] + 0.5 * view.s:.1f}" rx="{rx:.1f}" ry="{4.5 * view.s:.1f}" '
          f'fill="#2a3a20" opacity="0.28"/>')
