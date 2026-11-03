"""Build every sheet of the С3 style page: svg/*.svg (then render.js turns them into pics/*.png).
Run: cd styles/s3-graphic/tools && python3 build.py && NODE_PATH=/opt/node-tools/node_modules node render.js ../pics 1.5 ../svg/*.svg"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import svg, g, F, L, text, LW
import anya, savely, tim, vera
from face import eye

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'svg')
os.makedirs(OUT, exist_ok=True)
INK = '#3a2e2a'


def save(name, w, h, body, bg):
    open(os.path.join(OUT, name + '.svg'), 'w').write(svg(w, h, body, bg))


# name, module, 3/4 figure fn, head centre in figure coords, feet y, backdrop
CAST = {
    'anya': dict(m=anya, head=(0, 0), feet=1386, crown=-142, bg='#ead9c5', disc='#f2c98e', name='Аня'),
    'savely': dict(m=savely, head=(14, 26), feet=848, crown=-98, bg='#d8ccb5', disc='#efe4cc', name='Савелий Петрович'),
    'tim': dict(m=tim, head=(0, 4), feet=682, crown=-156, bg='#cfe0df', disc='#f3d26e', name='Тим'),
    'vera': dict(m=vera, head=(0, 26), feet=1480, crown=-108, bg='#d4d8da', disc='#ebe5da', name='Вера'),
}


def clockface(cx, cy, r, col, tick):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/>']
    import math
    for i in range(12):
        a = i * math.pi / 6
        r0 = r * (.82 if i % 3 else .74)
        out.append(L(f'M {cx + r0 * math.sin(a):.1f} {cy - r0 * math.cos(a):.1f} L {cx + r * .9 * math.sin(a):.1f} {cy - r * .9 * math.cos(a):.1f}',
                     tick, 4 if i % 3 else 7))
    return ''.join(out)


def backdrop(key, w, h, cx, cy, r):
    c = CAST[key]
    if key == 'savely':
        return clockface(cx, cy, r, c['disc'], '#c9b892')
    if key == 'vera':
        return (F(f'M {cx - r * .62} {cy + r * 1.3} L {cx - r * .62} {cy - r * .7} C {cx - r * .62} {cy - r * 1.3}, {cx + r * .62} {cy - r * 1.3}, {cx + r * .62} {cy - r * .7} L {cx + r * .62} {cy + r * 1.3} Z', c['disc'])
                + L(f'M {cx} {cy - r * 1.1} L {cx} {cy + r * 1.3} M {cx - r * .62} {cy - r * .1} L {cx + r * .62} {cy - r * .1}', c['bg'], 10))
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c["disc"]}"/>'


# ---------------------------------------------------------------- portraits
def portrait(key):
    c = CAST[key]
    m = c['m']
    W, H = 700, 800
    s = 1.45
    hx, hy = c['head']
    body = backdrop(key, W, H, 350, 330, 260)
    body += g(m.figure_q(), 350 - hx * s - 10, 360 - (hy + 0) * s, s)
    save(f'portrait-{key}', W, H, body, c['bg'])


# ---------------------------------------------------------------- full figures
def figure(key):
    c = CAST[key]
    m = c['m']
    W, H = 600, 1000
    tall = c['feet'] - c['crown']
    s = 820 / tall if key in ('anya', 'vera') else (620 / tall if key == 'savely' else 520 / tall)
    gy = 930
    body = backdrop(key, W, H, 300, 420, 220)
    body += f'<rect x="0" y="{gy}" width="{W}" height="{H - gy}" fill="{c["disc"]}" opacity=".55"/>'
    body += f'<ellipse cx="300" cy="{gy}" rx="{150 * s / .55 if key != "vera" else 120}" ry="14" fill="#000" opacity=".12"/>'
    body += g(m.figure_q(), 300, gy - c['feet'] * s, s)
    save(f'figure-{key}', W, H, body, c['bg'])


# ---------------------------------------------------------------- turnarounds
def turnaround(key, label):
    c = CAST[key]
    m = c['m']
    W, H = 1500, 1000
    tall = c['feet'] - c['crown']
    s = 760 / tall
    gy = 900
    top = gy - tall * s
    body = ''
    for y in (top, gy - (c['feet'] - 120 - c['head'][1]) * s, gy):
        body += L(f'M 40 {y:.1f} L {W - 40} {y:.1f}', '#b9a993', 1.4, 'stroke-dasharray="8 8"')
    views = [('figure_f', 'анфас'), ('figure_q', 'три четверти'), ('figure_s', 'профиль')]
    for i, (fn, lab) in enumerate(views):
        x = 260 + i * 490
        body += f'<ellipse cx="{x}" cy="{gy}" rx="120" ry="12" fill="#000" opacity=".1"/>'
        body += g(getattr(m, fn)(), x, gy - c['feet'] * s, s)
        body += text(x, 970, lab, 26, INK)
    body += text(40, 50, label, 30, INK, 'start')
    save(f'turnaround-{key}', W, H, body, '#f1e6d6')


# ---------------------------------------------------------------- expressions
EXPR = {
    'anya': [('dream', 'мечтает'), ('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('anger', 'гнев')],
    'savely': [('grump', 'ворчит'), ('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('anger', 'гнев')],
    'tim': [('mischief', 'хитрит'), ('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('anger', 'гнев')],
    'vera': [('strict', 'строгость'), ('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('anger', 'гнев')],
}


def expressions(key):
    c = CAST[key]
    m = c['m']
    W, H = 1700, 520
    body = text(40, 50, c['name'] + ' — выражения', 30, INK, 'start')
    for i, (e, lab) in enumerate(EXPR[key]):
        x = 190 + i * 330
        body += f'<circle cx="{x}" cy="250" r="150" fill="{c["disc"]}"/>'
        body += g(m.head_q(e), x - 10, 240, 1.0)
        body += text(x, 490, lab, 26, INK)
    save(f'expressions-{key}', W, H, body, c['bg'])


# ---------------------------------------------------------------- together
def cast():
    W, H = 1800, 1100
    gy = 1000
    body = clockface(900, 470, 400, '#f1dfbf', '#dcc396')
    body += f'<rect x="0" y="{gy}" width="{W}" height="{H - gy}" fill="#d9b98c"/>'
    order = [('vera', 380, .5), ('savely', 760, .62), ('anya', 1120, .47), ('tim', 1450, .56)]
    for key, x, s in order:
        c = CAST[key]
        body += f'<ellipse cx="{x}" cy="{gy}" rx="{120 if key != "savely" else 110}" ry="14" fill="#000" opacity=".14"/>'
        body += g(c['m'].figure_q(), x, gy - c['feet'] * s, s)
    save('cast', W, H, body, '#e9d3b4')


# ---------------------------------------------------------------- rule diagrams
def shapes():
    """Silhouettes with the one big shape each character is built on."""
    W, H = 1600, 900
    gy = 820
    body = ('<defs><filter id="sil"><feFlood flood-color="#4a3c36" result="f"/>'
            '<feComposite in="f" in2="SourceAlpha" operator="in"/></filter></defs>')
    order = [('vera', 260, .46, 'игла / прямоугольник'), ('savely', 640, .58, 'квадрат / бочка'),
             ('anya', 1000, .44, 'капля / S-кривая'), ('tim', 1340, .52, 'круг')]
    for key, x, s, lab in order:
        c = CAST[key]
        y0 = gy - c['feet'] * s
        body += f'<g filter="url(#sil)" opacity=".85">{g(c["m"].figure_q(), x, y0, s)}</g>'
        top = y0 + c['crown'] * s
        hgt = gy - top
        col = '#e9704f'
        if key == 'vera':
            body += L(f'M {x - 70} {gy} L {x - 46} {top + 10} L {x + 40} {top + 10} L {x + 70} {gy} Z', col, 5)
        elif key == 'savely':
            body += L(f'M {x - 100} {top + hgt * .28} L {x + 110} {top + hgt * .28} C {x + 130} {top + hgt * .6}, {x + 110} {top + hgt * .75}, {x + 90} {top + hgt * .8} L {x - 90} {top + hgt * .8} C {x - 110} {top + hgt * .7}, {x - 112} {top + hgt * .4}, {x - 100} {top + hgt * .28} Z', col, 5)
        elif key == 'anya':
            body += L(f'M {x + 4} {top - 6} C {x + 70} {top + hgt * .2}, {x + 100} {top + hgt * .6}, {x + 80} {gy - 20} C {x + 20} {gy + 10}, {x - 60} {gy + 10}, {x - 90} {gy - 20} C {x - 100} {top + hgt * .6}, {x - 70} {top + hgt * .2}, {x + 4} {top - 6} Z', col, 5)
        else:
            body += f'<circle cx="{x}" cy="{top + 128 * s}" r="{140 * s}" fill="none" stroke="{col}" stroke-width="5"/>'
            body += f'<circle cx="{x}" cy="{top + 128 * s + 260 * s}" r="{150 * s}" fill="none" stroke="{col}" stroke-width="5" stroke-dasharray="10 8"/>'
        body += text(x, 870, lab, 24, INK)
    save('rule-shapes', W, H, body, '#f1e6d6')


def eyes():
    """How the eye is built, and how it differs per character."""
    W, H = 1600, 520
    body = ''
    C = anya.C
    steps = [('1. белок-овал', dict(lid=0, hl=False, lashes=False, lidshade=False, lowline=False, ir=.01)),
             ('2. большая радужка', dict(lid=0, hl=False, lashes=False, lidshade=False, lowline=False, ir=16)),
             ('3. веко и его тень', dict(lid=.22, hl=False, lashes=False, lowline=False, ir=16)),
             ('4. ресницы, блики', dict(lid=.22, ir=16))]
    for i, (lab, kw) in enumerate(steps):
        x, y = 170 + i * 260, 200
        body += f'<rect x="{x - 115}" y="{y - 125}" width="230" height="250" rx="30" fill="{C["skin"]}"/>'
        body += g(eye(0, 0, 22, 24, C, look=(5, -2), flick=1, **kw), x, y, 3)
        body += text(x, 380, lab, 22, INK)
    # per character
    for j, (key, kw) in enumerate([('anya', dict(rx=22, ry=24, lid=.26, ir=16)), ('vera', dict(rx=21, ry=18, lid=.36, ir=12, wing=True)),
                                    ('tim', dict(rx=23, ry=26, lid=.3, ir=16, wing=False)), ('savely', dict(rx=14, ry=13, lid=.42, ir=9, wing=False))]):
        x, y = 1180 + (j % 2) * 230, 150 + (j // 2) * 210
        cc = CAST[key]['m'].C
        body += f'<circle cx="{x}" cy="{y}" r="70" fill="{cc["skin"]}"/>'
        body += g(eye(0, 0, kw['rx'], kw['ry'], cc, look=(4, 0), lid=kw['lid'], ir=kw['ir'], flick=1, wing=kw.get('wing', True),
                      lash=2.0 if key != 'savely' else 1.6), x, y, 2)
        body += text(x, y + 90, CAST[key]['name'], 20, INK)
    save('rule-eyes', W, H, body, '#f1e6d6')


if __name__ == '__main__':
    for k in CAST:
        portrait(k)
        figure(k)
        expressions(k)
    turnaround('anya', 'Аня — поворот')
    turnaround('savely', 'Савелий Петрович — поворот')
    cast()
    shapes()
    eyes()
    print('ok')
