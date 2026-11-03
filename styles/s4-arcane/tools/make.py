"""Build every picture of the page: python3 make.py [what...]; SVG into ../svg, PNG into ../pics (headless Chrome)."""
import os, sys, subprocess, gzip
from cast import *

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, '..', 'svg')
PIC = os.path.join(HERE, '..', 'pics')
SCRATCH = os.environ.get('S4_SCRATCH', '/home/user/cache/styles-s4-arcane/render')
LIGHT = (-0.5, -0.55, 0.67)


def doc(w, h):
    d = Doc(w, h)
    d.defs.append(FILTERS)
    return d


def save(d, name):
    d.add(grain(d.w, d.h))
    # the drawing is kept gzipped (svgz); a plain copy for rendering goes to the scratch folder
    os.makedirs(SCRATCH, exist_ok=True)
    p = os.path.join(SCRATCH, name + '.svg')
    open(p, 'w').write(d.svg())
    with gzip.open(os.path.join(SVG, name + '.svgz'), 'wt') as f:
        f.write(d.svg())
    png = os.path.join(SCRATCH, name + '.png')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--screenshot=' + png,
                    '--window-size=%d,%d' % (d.w, d.h), 'file://' + os.path.abspath(p)], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    subprocess.run(['convert', png, '-quality', '86', os.path.join(PIC, name + '.jpg')])
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
    v = View(yaw=22, s=2.2, cx=330, cy=330, light=LIGHT, rimcol=c['rim'])
    d.add(draw_figure(d, P, v, c['neutral'], parts=bust_parts(c['body'](P))))
    save(d, 'portrait-' + k)


def turnaround(k):
    c = CAST[k]
    P = c['make']()
    W, H = 1500, 640
    d = doc(W, H)
    d.add(background(d, W, H, *c['bg'], seed=5))
    for i, yaw in enumerate([0, 40, 88]):
        v = View(yaw=yaw, s=1.45, cx=260 + i * 490, cy=270, light=LIGHT, rimcol=c['rim'])
        d.add(draw_figure(d, P, v, c['neutral'], parts=bust_parts(c['body'](P))))
    save(d, 'turn-' + k)


def expressions(k):
    c = CAST[k]
    P = c['make']()
    W, H = 1600, 560
    d = doc(W, H)
    d.add(background(d, W, H, *c['bg'], seed=7))
    for i, (name, e) in enumerate(EXPR):
        v = View(yaw=14, s=1.3, cx=200 + i * 400, cy=250, light=LIGHT, rimcol=c['rim'])
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
        v = View(yaw=yaw, s=s, cx=cx, cy=top, light=LIGHT, rimcol=c['rim'])
        d.add(draw_figure(d, P, v, c['neutral'], parts=c['body'](P)))
    save(d, name or ('figure-' + k))


def room(d, W, H, top, mid, floor, glow, horizon):
    """A quiet painted room: a warm wall with a window glow, a darker floor."""
    g1, g2 = d.uid('w'), d.uid('f')
    d.defs.append('<linearGradient id="%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (g1, top, mid))
    d.defs.append('<linearGradient id="%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (g2, mix(floor, mid, 0.3), floor))
    g3 = d.uid('gl')
    d.defs.append('<radialGradient id="%s" cx="0.32" cy="0.3" r="0.55"><stop offset="0" stop-color="%s" stop-opacity="0.75"/><stop offset="0.5" stop-color="%s" stop-opacity="0.25"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (g3, glow, glow, glow))
    s = '<rect width="%d" height="%d" fill="url(#%s)"/>' % (W, H, g1)
    s += '<rect width="%d" height="%d" fill="url(#%s)"/>' % (W, H, g3)
    s += '<rect y="%s" width="%d" height="%s" fill="url(#%s)"/>' % (fmt(horizon), W, fmt(H - horizon), g2)
    s += '<rect y="%s" width="%d" height="3" fill="%s" opacity="0.5" filter="url(#edge)"/>' % (fmt(horizon), W, mix(floor, '#000000', 0.4))
    s += '<rect width="%d" height="%d" filter="url(#canvas)" opacity="0.10" style="mix-blend-mode:overlay"/>' % (W, H)
    return s


def together():
    W, H = 1600, 1000
    d = doc(W, H)
    d.add(room(d, W, H, '#8a6a52', '#5a4640', '#2e2624', '#f6c98a', 700))
    order = [('vera', 1120, -28, 0.5, H - 70), ('savely', 430, 30, 0.5, H - 70), ('anya', 760, 6, 0.5, H - 78), ('tim', 960, -12, 0.53, H - 34)]
    for k, x, yaw, s, gy in order:
        c = CAST[k]
        P = c['make']()
        d.add(ground(x, gy + 2, 80, 0.45))
        v = View(yaw=yaw, s=s, cx=x, cy=gy - c['feet'] * s, light=LIGHT, rimcol=c['rim'])
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
        elif w == 'construction':
            construction()
        elif w.startswith('portrait-'):
            portrait(w[9:])
        elif w.startswith('turn-'):
            turnaround(w[5:])
        elif w.startswith('expr-'):
            expressions(w[5:])
        elif w.startswith('figure-'):
            figure(w[7:])


def construction():
    """How a head is built: form, light and shadow, features, hair and texture."""
    c = CAST['anya']
    W, H = 1600, 560
    d = doc(W, H)
    d.add(background(d, W, H, *c['bg'], seed=13))
    yaw, s = 24, 1.3
    P = c['make']()
    head = P.head()
    nose = P.nose(head)
    neck = P.neck()
    pal = P.pal
    for i in range(4):
        v = View(yaw=yaw, s=s, cx=200 + i * 400, cy=250, light=LIGHT, rimcol=c['rim'])
        if i < 2:
            for sf, pl in ((neck, pal['neck']), (head, pal['skin']), (nose, pal['skin'])):
                R = regions(sf, v)
                if i == 0:
                    d.add(path(poly_path(R['sil']), pl['lit']) + path(poly_path(R['sil']), 'none', pl['line'], 1.2, 0.6))
                else:
                    d.add(shade_layers(d, R, pl, brush=sf is not nose, rim=sf is not nose))
        elif i == 2:
            Q = c['make']()
            for k in ('hair_locks', 'hair_cap'):
                delattr(Q, k)
            d.add(draw_head(d, Q, v, c['neutral'], bust=False))
        else:
            d.add(draw_head(d, P, v, c['neutral'], bust=False))
    save(d, 'construction')
