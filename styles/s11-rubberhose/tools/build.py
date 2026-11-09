"""Build every sheet of the С11 «Резиновые 1930-е» page: svg/*.svg; render.js turns them into pics/*.png.
Run:  cd styles/s11-rubberhose/tools && python3 build.py && NODE_PATH=/opt/node-tools/node_modules node render.js ../pics 1 ../svg/*.svg"""
import os
import sys
import math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import (svg, g, P, circle, ellipse, clip, shadow, text, INK, glove, shoe, hose, eye, mouth)
import anya, savely, tim, vera, marat, kira

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'svg')
os.makedirs(OUT, exist_ok=True)

# per character: module, posed pose, head centre in the posed figure, portrait disc colour, name
CAST = {
    'anya': dict(m=anya, pose='dream', head=(6, -4), disc='#e9b8a6', name='Аня', seed=3),
    'savely': dict(m=savely, pose='watch', head=(18, 36), disc='#a9c3b8', name='Савелий Петрович', seed=5),
    'tim': dict(m=tim, pose='sneak', head=(0, 2), disc='#f0c75a', name='Тим', seed=7),
    'vera': dict(m=vera, pose='books', head=(8, -2), disc='#b9b3cf', name='Вера', seed=9),
    # round three: optional keys — ppose (the portrait's pose), fexpr (the figure's expression), top (the highest
    # point of the posed figure), tsc (the turnaround's scale), esc / ey (the expression heads' scale and shift)
    'marat': dict(m=marat, pose='laugh', ppose='hello', fexpr='joy', head=(14, 20), disc='#e3a15e', name='Марат', seed=13,
                  top=-150, tsc=1.14, esc=1.3, ey=-22, fx=-14),
    'kira': dict(m=kira, pose='sulk', head=(16, 26), disc='#c3cc92', name='Кира', seed=15, top=-64, tsc=1.42),
}
FOUR = ('anya', 'savely', 'tim', 'vera')


def save(name, w, h, body, **kw):
    open(os.path.join(OUT, name + '.svg'), 'w').write(svg(w, h, body, **kw))


def portrait(key):
    """Head and shoulders in a round medallion, as the 1930s title cards and Cuphead's portraits frame them."""
    c = CAST[key]
    W, H = 700, 760
    cx, cy, r = 350, 380, 300
    sc = 2.0
    hx, hy = c['head']
    disc = f'M {cx - r} {cy} A {r} {r} 0 1 1 {cx + r} {cy} A {r} {r} 0 1 1 {cx - r} {cy} Z'
    rays = ''.join(P(f'M {cx} {cy} L {cx + 2 * r * math.cos(a0):.1f} {cy + 2 * r * math.sin(a0):.1f} '
                     f'L {cx + 2 * r * math.cos(a0 + .13):.1f} {cy + 2 * r * math.sin(a0 + .13):.1f} Z', '#ffffff', None, 0, 'opacity=".16"')
                   for a0 in [i * math.pi / 12 for i in range(24)])
    inner = P(disc, c['disc'], None, 0) + rays + g(c['m'].figure('q', c.get('ppose', c['pose'])), cx - hx * sc, cy - 40 - hy * sc, sc)
    body = clip(disc, inner) + P(disc, 'none', INK, 7) + circle(cx, cy, r + 12, 'none', 2.4)
    save(f'portrait-{key}', W, H, body, seed=c['seed'])


def figure(key):
    c = CAST[key]
    m = c['m']
    W, H = 640, 1000
    top = {'anya': -100, 'savely': -40, 'tim': -104, 'vera': -70}.get(key) or c['top']
    sc = 800 / (m.FEET - top)
    gy = 920
    body = ellipse(320, 440, 250, 330, '#ffffff', 0, extra='opacity=".18"')
    body += shadow(320, gy + 2, 120 * sc, 12)
    body += g(m.figure('q', c['pose'], c.get('fexpr', 'neutral')), 320 + c.get('fx', 0), gy - m.FEET * sc, sc)
    save(f'figure-{key}', W, H, body, seed=c['seed'])


def turnaround(key):
    c = CAST[key]
    m = c['m']
    W, H = 1500, 900
    sc = {'anya': 1.36, 'savely': 1.6, 'tim': 1.6, 'vera': 1.26}.get(key) or c['tsc']
    gy = 800
    body = ''
    for i, (v, lab) in enumerate((('front', 'анфас'), ('q', 'три четверти'), ('side', 'профиль'))):
        x = 250 + i * 500
        body += shadow(x, gy + 2, 100, 12)
        body += g(m.figure(v, 'stand'), x, gy - m.FEET * sc, sc)
        body += text(x, 870, lab, 28, extra='opacity=".75"')
    save(f'turnaround-{key}', W, H, body, seed=c['seed'])


# squash and stretch: the whole head changes shape with the feeling, as in the 1930s shorts
SQUASH = {'neutral': (1, 1), 'joy': (1.06, .95), 'surprise': (.93, 1.09), 'sad': (1.02, .96), 'angry': (1.05, .95)}


def expressions(key):
    c = CAST[key]
    m = c['m']
    W, H = 1500, 420
    labels = (('neutral', 'спокойно'), ('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('angry', 'злость'))
    body = ''
    for i, (e, lab) in enumerate(labels):
        x = 150 + i * 300
        body += circle(x, 190, 135, '#ffffff', 0, extra='opacity=".22"')
        sx, sy = SQUASH[e]
        k = c.get('esc', 1.55)
        body += f'<g transform="translate({x} {185 + c.get("ey", 0)}) scale({k * sx:.3f} {k * sy:.3f})">{m.head(.3, e)}</g>'
        body += text(x, 395, lab, 26, extra='opacity=".75"')
    save(f'expressions-{key}', W, H, body, seed=c['seed'])


def cast(bw=False):
    W, H = 1600, 1000
    gy = 920
    sc = 1.42
    body = ellipse(800, 1020, 900, 200, '#ffffff', 0, extra='opacity=".18"')
    order = (('savely', 300, savely, 'watch'), ('anya', 640, anya, 'dream'), ('tim', 960, tim, 'sneak'), ('vera', 1300, vera, 'books'))
    for key, x, m, pose in order:
        body += shadow(x, gy + 2, 120, 14)
        body += g(m.figure('q', pose), x, gy - m.FEET * sc, sc)
    save('cast-bw' if bw else 'cast', W, H, body, bw=bw, bg='#e9dcc0' if not bw else '#d9d4c8', seed=11)


def cast6():
    """All six together (round three): the same sheet as the four, a little smaller to fit."""
    W, H = 1600, 1000
    gy = 930
    sc = 1.22
    body = ellipse(800, 1030, 900, 200, '#ffffff', 0, extra='opacity=".18"')
    order = (('savely', 150, 'neutral'), ('anya', 395, 'neutral'), ('marat', 745, 'joy'), ('tim', 1040, 'neutral'), ('vera', 1245, 'neutral'),
             ('kira', 1445, 'neutral'))
    for key, x, ex in order:
        c = CAST[key]
        body += shadow(x, gy + 2, 150 if key == 'marat' else 105, 13)
        body += g(c['m'].figure('q', c['pose'], ex), x, gy - c['m'].FEET * sc, sc)
    save('cast6', W, H, body, bg='#e9dcc0', seed=17)


def rules():
    """Diagram sheets: the parts of the style."""
    W, H = 1500, 470
    b = ''
    lab = lambda x, t: text(x, 430, t, 26, extra='opacity=".8"')
    b += hose([(70, 90), (130, 150), (150, 250)], 18, '#f6dcc4') + g(glove('open'), 150, 250, 1.1, -10)
    b += hose([(210, 90), (260, 200), (240, 300)], 18, '#f6dcc4', 24, 10)
    b += lab(160, 'шланг без локтя')
    for i, p in enumerate(('open', 'fist', 'point', 'rest')):
        b += g(glove(p), 360 + i * 85, 160, 1.3)
    b += lab(490, 'перчатка')
    b += eye(690, 180, 30, 44, look=(.2, 0), kind='pie') + eye(770, 180, 30, 44, look=(.3, -.5), kind='ring', lash=3, heavy=.4, side=1)
    b += eye(850, 180, 24, 32, look=(0, 0), kind='dot', lid=.35, rot=-.4, side=1)
    b += lab(770, 'глаз')
    for i, k in enumerate(('smile', 'grin', 'o', 'lips-smile')):
        b += mouth(990 + (i % 2) * 100, 140 + (i // 2) * 110, 56 if not k.startswith('lips') else 40, k)
    b += lab(1040, 'рот')
    b += g(shoe('#b8352a'), 1260, 170, 1.7) + g(shoe('#2a221e', view='front'), 1360, 290, 1.5)
    b += lab(1320, 'башмак')
    save('rule-parts', W, H, b)
    # proportions: four standing figures with head marks
    W, H = 1500, 800
    gy = 720
    b = ''
    for i, (key, m) in enumerate((('anya', anya), ('savely', savely), ('tim', tim), ('vera', vera))):
        x = 210 + i * 360
        top = {'anya': -100, 'savely': -64 + 30 - 4, 'tim': -100, 'vera': -82}[key]
        sc = 1.15
        b += shadow(x, gy + 2, 80, 10) + g(m.figure('front', 'stand'), x, gy - m.FEET * sc, sc)
        ht = {'anya': 3.0, 'savely': 2.7, 'tim': 2.2, 'vera': 3.6}[key]
        b += text(x, 770, CAST[key]['name'], 24, extra='opacity=".8"')
    save('rule-heights', W, H, b)


if __name__ == '__main__':
    for k in FOUR:
        portrait(k)
        figure(k)
        expressions(k)
    for k in FOUR:
        turnaround(k)
    cast()
    cast(bw=True)
    rules()
    # round three: Марат and Кира, and all six together (built after the four, so the four's files stay as they were)
    for k in ('marat', 'kira'):
        portrait(k)
        figure(k)
        expressions(k)
        turnaround(k)
    cast6()
