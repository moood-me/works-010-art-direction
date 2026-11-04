"""Backdrops: one bold flat colour, a band of ground, a few painted motifs at the edges (Blair, Provensen)."""
import math
from kit import shape, brush, circle, ell, g, mix

# each one's colour field, its motif, and the colour of the motif
BACK = {
    'anya':   dict(field='#ec9f93', ground='#d9796f', motif='daisy', mc='#fbf3e4'),
    'savely': dict(field='#d7a64a', ground='#b98634', motif='clock', mc='#f3e6c4'),
    'tim':    dict(field='#7fc4c0', ground='#5ea6a0', motif='sun', mc='#f2c94c'),
    'vera':   dict(field='#5e7591', ground='#4a5f78', motif='leaf', mc='#a9bfcf'),
}


def daisy(x, y, r, c, centre='#e8b33a'):
    o = [ell(x + r * 0.7 * math.cos(a), y + r * 0.7 * math.sin(a), r * 0.55, r * 0.26, c, rot=math.degrees(a))
         for a in [i * math.pi / 4 for i in range(8)]]
    o.append(circle(x, y, r * 0.28, centre))
    return ''.join(o)


def sun(x, y, r, c):
    o = [brush([(x + r * 1.15 * math.cos(a), y + r * 1.15 * math.sin(a)), (x + r * 1.7 * math.cos(a), y + r * 1.7 * math.sin(a))],
               r * 0.22, c, taper=(0, 0.6)) for a in [i * math.pi / 6 for i in range(12)]]
    o.append(circle(x, y, r, c))
    o.append(circle(x, y, r * 0.55, '#ec7f3a'))
    return ''.join(o)


def clock(x, y, r, c, ink='#5a3e1c'):
    o = [circle(x, y, r, c)]
    for i in range(12):
        a = i * math.pi / 6
        o.append(circle(x + r * 0.8 * math.cos(a), y + r * 0.8 * math.sin(a), r * 0.05, ink))
    o.append(brush([(x, y), (x + r * 0.35, y - r * 0.4)], r * 0.08, ink, taper=(0, 0.4)))
    o.append(brush([(x, y), (x - r * 0.1, y - r * 0.65)], r * 0.06, ink, taper=(0, 0.4)))
    return ''.join(o)


def leaf(x, y, r, c, rot=0):
    pts = [(0, -r, 'c'), (r * 0.42, -r * 0.2), (0, r, 'c'), (-r * 0.42, -r * 0.2)]
    return (f'<g transform="translate({x},{y}) rotate({rot})">' + shape(pts, c)
            + brush([(0, -r * 0.8), (0, r * 0.9)], 2.2, mix(c, '#2a201c', 0.35), taper=(0.1, 0.1)) + '</g>')


MOTIF = {'daisy': daisy, 'sun': sun, 'clock': clock, 'leaf': leaf}


def backdrop(d, who, kind):
    b = BACK[who]
    w, h = d.w, d.h
    o = [f'<rect width="{w}" height="{h}" fill="{b["field"]}"/>']
    f = MOTIF[b['motif']]
    if kind == 'portrait':
        o.append(f'<rect y="{h * 0.84}" width="{w}" height="{h}" fill="{b["ground"]}"/>')
        spots = [(60, 80, 26), (440, 120, 18), (420, 380, 22), (70, 420, 16)]
    elif kind == 'figure':
        o.append(shape([(0, h * 0.86), (w * 0.5, h * 0.84), (w, h * 0.87), (w, h), (0, h)], b['ground']))
        spots = [(70, 110, 30), (420, 200, 20), (430, 520, 16), (60, 560, 22)]
    else:
        o.append(f'<rect y="{h * 0.86}" width="{w}" height="{h}" fill="{b["ground"]}"/>')
        spots = [(60 + i * (w - 120) / 6, 60 + (i % 2) * (h - 160), 16 + (i % 3) * 4) for i in range(7)]
    for (x, y, r) in spots:
        if b['motif'] == 'leaf':
            o.append(f(x, y, r * 1.4, b['mc'], rot=(x * 7) % 60 - 30))
        else:
            o.append(f(x, y, r, b['mc']))
    d.add(g(o, filt='gouache'))
