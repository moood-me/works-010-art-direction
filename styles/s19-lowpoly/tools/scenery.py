"""Backgrounds and stands: a soft graded backdrop with a few large faint facets, a faceted round plinth under each
figure (the board-game figures of the GO games stand on one), and a small low-poly diorama for the cast."""
import math
import random
from poly import hull, hexcol, tohex, mix

BG = {   # backdrop: top colour, bottom colour (each character has its own mood)
    'anya': ('#e9d7c1', '#c9b8b2'), 'savely': ('#d9d2c4', '#a9a49c'), 'tim': ('#d6e3dc', '#a9c0bb'),
    'vera': ('#cdd3da', '#8f99a6'), 'marat': ('#f0d6bf', '#c99e86'), 'kira': ('#c9c3cf', '#7e778a'),
}


def backdrop(doc, w, h, top, bottom, seed=3, facets=True):
    gid = 'bg%d' % len(doc.defs)
    doc.defs.append('<linearGradient id="%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/>'
                    '<stop offset="1" stop-color="%s"/></linearGradient>' % (gid, top, bottom))
    doc.add('<rect width="%d" height="%d" fill="url(#%s)"/>' % (w, h, gid))
    if not facets:
        return
    # a few large triangles, barely lighter or darker: the backdrop is faceted too
    rnd = random.Random(seed)
    cols = int(round(w / 260)) + 1; rows = int(round(h / 260)) + 1
    P = [[(i * w / (cols - 1) + (rnd.uniform(-60, 60) if 0 < i < cols - 1 else 0),
           j * h / (rows - 1) + (rnd.uniform(-60, 60) if 0 < j < rows - 1 else 0)) for i in range(cols)] for j in range(rows)]
    for j in range(rows - 1):
        for i in range(cols - 1):
            a, b, c, d = P[j][i], P[j][i + 1], P[j + 1][i + 1], P[j + 1][i]
            for tri in ((a, b, c), (a, c, d)) if (i + j) % 2 else ((a, b, d), (b, c, d)):
                v = rnd.uniform(-1, 1)
                col = '#ffffff' if v > 0 else '#2a2440'
                doc.add('<polygon points="%s" fill="%s" fill-opacity="%.3f"/>'
                        % (' '.join('%.1f,%.1f' % p for p in tri), col, abs(v) * 0.05))


def plinth(r=30.0, h=4.0, color='#5d5a66', n=10, y=0.0, x=0.0, z=0.0):
    """A faceted round base under the feet (top at y)."""
    top = [(x + r * math.sin(2 * math.pi * i / n), y, z + r * math.cos(2 * math.pi * i / n)) for i in range(n)]
    mid = [(x + (r + 1.6) * math.sin(2 * math.pi * (i + 0.5) / n), y - h * 0.45, z + (r + 1.6) * math.cos(2 * math.pi * (i + 0.5) / n)) for i in range(n)]
    bot = [(x + (r + 1.2) * math.sin(2 * math.pi * i / n), y - h, z + (r + 1.2) * math.cos(2 * math.pi * i / n)) for i in range(n)]
    return [hull(top + mid + bot, color, 'cloth', 'plinth')]


def diorama(w=520.0, d=200.0, h=26.0, seed=5, top='#8fa07a', side='#6b5b4b', path='#d8cdb6'):
    """A raised tile of faceted ground: a jittered grid of triangles on top, earth on the sides, a pale path."""
    rnd = random.Random(seed)
    pieces = []
    nx, nz = 10, 4
    xs = [-w / 2 + w * i / nx for i in range(nx + 1)]
    zs = [-d / 2 + d * j / nz for j in range(nz + 1)]
    Y = [[(0.0 if (i in (0, nx) or j in (0, nz)) else rnd.uniform(0.3, 2.6)) for i in range(nx + 1)] for j in range(nz + 1)]
    J = [[(xs[i] + (rnd.uniform(-8, 8) if 0 < i < nx else 0), zs[j] + (rnd.uniform(-8, 8) if 0 < j < nz else 0))
          for i in range(nx + 1)] for j in range(nz + 1)]
    for j in range(nz):
        for i in range(nx):
            a = (J[j][i][0], Y[j][i], J[j][i][1]); b = (J[j][i + 1][0], Y[j][i + 1], J[j][i + 1][1])
            c = (J[j + 1][i + 1][0], Y[j + 1][i + 1], J[j + 1][i + 1][1]); dd = (J[j + 1][i][0], Y[j + 1][i], J[j + 1][i][1])
            onpath = j in (1, 2)
            for tri in ((a, c, b), (a, dd, c)):
                col = path if onpath else top
                col = tohex(mix(hexcol(col), hexcol('#ffffff' if rnd.random() > 0.5 else '#203020'), rnd.uniform(0, 0.08)))
                pieces.append(hull(list(tri) + [(x, y - 0.6, z) for x, y, z in tri], col, 'cloth', 'ground'))
    body = [(x, y, z) for x in (-w / 2, w / 2) for y in (-0.7, -h) for z in (-d / 2, d / 2)]
    pieces.append(hull(body, side, 'cloth', 'earth'))
    return pieces
