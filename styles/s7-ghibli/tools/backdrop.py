"""Painted backdrops in the manner of Ghibli's backgrounds: skies with tall cumulus, masses of foliage built from
many leaf clumps in three tones, washes of colour with uneven pooling, edges softened as gouache on paper.
Everything is SVG shapes passed through a displacement filter — no images."""
import random
import numpy as np
from shapely.geometry import Point, box
from shapely.ops import unary_union
from geo import path_of, shift, smooth
from svgdoc import mix


def grad(d, x, y, w, h, stops, vertical=True):
    i = d.uid('lg')
    st = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    xy = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    d.defs.append(f'<linearGradient id="{i}" {xy}>{st}</linearGradient>')
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{i})"/>')


def painted(d, g, c, rough=None, op=1.0):
    if g.is_empty:
        return
    f = f' filter="url(#{rough})"' if rough else ''
    o = f' opacity="{op}"' if op < 1 else ''
    d.add(f'<path d="{path_of(g)}" fill="{c}"{f}{o}/>')


def cloud(d, cx, cy, w, h, rnd, rough, top='#fbfaf6', shadow='#b9c3d6', mid='#e3e6ee'):
    """a cumulus: a heap of round puffs on a flat base; lit tops, a lavender-grey belly."""
    puffs = []
    n = int(10 + w / 30)
    for i in range(n):
        t = rnd.random()
        x = cx + (t - 0.5) * w * 0.9
        hh = h * (1 - abs(t - 0.5) * 1.5) * rnd.uniform(0.6, 1.0)
        r = rnd.uniform(0.18, 0.32) * w * (0.5 + 0.5 * (1 - abs(t - 0.5) * 2))
        y = cy - max(hh, r * 0.5) + r * 0.6
        puffs.append(Point(x, y).buffer(r, 24))
    g = unary_union(puffs).intersection(box(cx - w, cy - h * 2, cx + w, cy))
    painted(d, g, shadow, rough)
    lit = g.intersection(shift(g, 0.04 * w, 0.22 * h))
    painted(d, lit, mid, rough)
    lit2 = g.intersection(shift(g, 0.07 * w, 0.42 * h))
    painted(d, lit2, top, rough)


def foliage(d, region, base, rnd, rough, n=60, r=(12, 30), light=(-0.5, -1)):
    """a mass of leaves: the dark mass, then mid clumps toward the light, then a few light clumps."""
    painted(d, region, mix(base, '#10201a', 0.35), rough)
    b = region.bounds
    for tone, k, sz in ((base, 1.0, 1.0), (mix(base, '#e8f0a0', 0.30), 0.55, 0.75), (mix(base, '#fff6c0', 0.55), 0.25, 0.5)):
        clumps = []
        for _ in range(int(n * k)):
            x, y = rnd.uniform(b[0], b[2]), rnd.uniform(b[1], b[3])
            # clumps gather toward the lit side
            if rnd.random() > 0.35 + 0.65 * ((b[3] - y) / max(b[3] - b[1], 1)) ** (1.2 / k):
                continue
            rr = rnd.uniform(*r) * sz
            c = Point(x, y).buffer(rr, 16)
            c = c.difference(shift(c, -light[0] * rr * 0.5, -light[1] * rr * 0.5))
            clumps.append(c)
        g = unary_union(clumps).intersection(region)
        painted(d, g, tone, rough)


def grass(d, x0, x1, y, h, base, rnd, rough, n=220):
    """tall grass and blades along a line, a few flowers."""
    blades = []
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        hh = rnd.uniform(0.4, 1.0) * h
        lean = rnd.uniform(-0.25, 0.25) * hh
        w = rnd.uniform(2.5, 6)
        blades.append(f'M{x - w:.1f},{y + 4:.1f} Q{x + lean * 0.3:.1f},{y - hh * 0.6:.1f} {x + lean:.1f},{y - hh:.1f} '
                      f'Q{x + lean * 0.3 + w:.1f},{y - hh * 0.5:.1f} {x + w:.1f},{y + 4:.1f}Z')
    tones = [mix(base, '#0e2018', 0.3), base, mix(base, '#e8f0a0', 0.35)]
    for k, t in enumerate(tones):
        d.add(f'<path d="{"".join(blades[k::3])}" fill="{t}" filter="url(#{rough})"/>')


def flowers(d, x0, x1, y0, y1, colors, rnd, n=30):
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        c = rnd.choice(colors)
        r = rnd.uniform(2.5, 5)
        d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{c}"/>'
              f'<circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.3:.1f}" r="{r * 0.45:.1f}" fill="#fffbe8" opacity="0.7"/>')


def sky(d, w, h, top='#5f9ad0', bottom='#cfe3ee', y=0):
    grad(d, 0, y, w, h, [(0, top), (0.75, mix(top, bottom, 0.7)), (1, bottom)])
