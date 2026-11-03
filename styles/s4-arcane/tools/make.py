"""Build every picture of the page: python3 make.py [what...]; SVG into ../svg, PNG into ../pics (headless Chrome)."""
import os, sys, subprocess
from cast import *

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, '..', 'svg')
PIC = os.path.join(HERE, '..', 'pics')
LIGHT = (-0.5, -0.55, 0.67)


def doc(w, h):
    d = Doc(w, h)
    d.defs.append(FILTERS)
    return d


def save(d, name):
    d.add(grain(d.w, d.h))
    p = os.path.join(SVG, name + '.svg')
    open(p, 'w').write(d.svg())
    png = os.path.join(PIC, name + '.png')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--screenshot=' + png,
                    '--window-size=%d,%d' % (d.w, d.h), 'file://' + os.path.abspath(p)], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    print(name)


def bust_parts(parts):
    """The parts that show above the chest (no legs, feet or skirts)."""
    return [p for p in parts if float(p.center[1]) < 700]


def ground(cx, cy, rx, op=0.35):
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#14100e" opacity="%s" filter="url(#soft2)"/>' % (fmt(cx), fmt(cy), fmt(rx), fmt(rx * 0.16), fmt(op))


def portrait(k):
    c = CAST[k]
    P = c['make']()
    W, H = 640, 800
    d = doc(W, H)
    d.add(background(d, W, H, *c['bg'], seed=3))
    v = View(yaw=22, s=2.2, cx=330, cy=330, light=LIGHT)
    d.add(draw_figure(d, P, v, c['neutral'], parts=bust_parts(c['body'](P))))
    save(d, 'portrait-' + k)


def turnaround(k):
    c = CAST[k]
    P = c['make']()
    W, H = 1500, 640
    d = doc(W, H)
    d.add(background(d, W, H, *c['bg'], seed=5))
    for i, yaw in enumerate([0, 40, 88]):
        v = View(yaw=yaw, s=1.45, cx=260 + i * 490, cy=270, light=LIGHT)
        d.add(draw_figure(d, P, v, c['neutral'], parts=bust_parts(c['body'](P))))
    save(d, 'turn-' + k)


def expressions(k):
    c = CAST[k]
    P = c['make']()
    W, H = 1600, 560
    d = doc(W, H)
    d.add(background(d, W, H, *c['bg'], seed=7))
    for i, (name, e) in enumerate(EXPR):
        v = View(yaw=14, s=1.3, cx=200 + i * 400, cy=250, light=LIGHT)
        d.add(draw_figure(d, P, v, e, parts=bust_parts(c['body'](P))))
    save(d, 'expr-' + k)


def figure(k, yaws=(18,), name=None):
    c = CAST[k]
    P = c['make']()
    s = 0.5
    W, H = 300 + 300 * len(yaws), 960
    d = doc(W, H)
    d.add(background(d, W, H, *c['bg'], seed=9))
    for i, yaw in enumerate(yaws):
        cx = 300 + i * 300 if len(yaws) > 1 else W / 2
        top = H - 50 - c['feet'] * s
        d.add(ground(cx, H - 48, 70))
        v = View(yaw=yaw, s=s, cx=cx, cy=top, light=LIGHT)
        d.add(draw_figure(d, P, v, c['neutral'], parts=c['body'](P)))
    save(d, name or ('figure-' + k))


def together():
    W, H = 1600, 1000
    d = doc(W, H)
    d.add(background(d, W, H, '#e6b678', '#6a5446', '#1e1e26', seed=11))
    s = 0.52
    ground_y = H - 60
    order = [('savely', 330, 24), ('anya', 650, 10), ('tim', 930, -14), ('vera', 1250, -22)]
    for k, x, yaw in order:
        c = CAST[k]
        P = c['make']()
        d.add(ground(x, ground_y + 2, 80))
        v = View(yaw=yaw, s=s, cx=x, cy=ground_y - c['feet'] * s, light=LIGHT)
        d.add(draw_figure(d, P, v, c['neutral'], parts=c['body'](P)))
    save(d, 'cast')


if __name__ == '__main__':
    what = sys.argv[1:] or ['portraits', 'turns', 'expr', 'figures', 'cast']
    for w in what:
        if w == 'portraits':
            for k in CAST:
                portrait(k)
        elif w == 'turns':
            for k in CAST:
                turnaround(k)
        elif w == 'expr':
            expressions('anya')
            expressions('tim')
        elif w == 'figures':
            for k in CAST:
                figure(k)
            figure('anya', (0, 40, 88), 'figure-turn-anya')
            figure('savely', (0, 40, 88), 'figure-turn-savely')
        elif w == 'cast':
            together()
        elif w.startswith('portrait-'):
            portrait(w[9:])
        elif w.startswith('turn-'):
            turnaround(w[5:])
        elif w.startswith('expr-'):
            expressions(w[5:])
        elif w.startswith('figure-'):
            figure(w[7:])
