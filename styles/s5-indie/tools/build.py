"""Builds every picture of the page: svg/*.svg (hand-built shapes, see cast.py) and pics/*.png (headless Chrome).
Run: python3 tools/build.py   (from styles/s5-indie)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo
import cast
import marat
import kira
import render
from geo import f

ROOT = os.path.dirname(HERE)
SVG = os.path.join(ROOT, 'svg')
PNG = os.path.join(ROOT, 'pics')
os.makedirs(SVG, exist_ok=True)
os.makedirs(PNG, exist_ok=True)

# the two who joined the four: a module each, registered here
cast.CAST['marat'] = marat.marat
cast.CAST['kira'] = kira.kira

BG = '#ece5d9'
NAMES = {'anya': 'Аня', 'savely': 'Савелий Петрович', 'tim': 'Тим', 'vera': 'Вера', 'marat': 'Марат', 'kira': 'Кира'}
# Марат is the widest by far: his sheets keep the scale and get wider; his close-ups step back a little
WIDE = {'marat': dict(portrait=1.22, figure=350, turn=320, expr=250, pose='calm')}
# head centre (body coords) and the portrait background colour per character
HEAD = {'anya': (-306, '#f3dccb'), 'savely': (-226, '#dfe3d2'), 'tim': (-205, '#d9e3ef'), 'vera': (-352, '#e3d9e3'),
        'marat': (-386, '#f5e3bf'), 'kira': (-300, '#e3e8cf')}
EXPRS = [('neutral', 'спокойно'), ('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('anger', 'злость')]
FONT = 'font-family="system-ui, -apple-system, Segoe UI, sans-serif"'


def save(name, body, vb, w, h, bg=BG, sw=2.4):
    path = os.path.join(SVG, name + '.svg')
    open(path, 'w').write(geo.svg(body, vb, w, h, bg=bg))
    if '--svg' not in sys.argv:
        render.png(path, os.path.join(PNG, name + '.png'))
    print(name)


def fig(name, yaw=0, ex='neutral', sw=2.4, **kw):
    geo.SW = sw
    s = cast.render(name, yaw, ex, **kw)
    geo.SW = 2.4
    return s


def label(x, y, text, size=15, col='#6d6259'):
    return f'<text x="{f(x)}" y="{f(y)}" text-anchor="middle" font-size="{size}" fill="{col}" {FONT}>{text}</text>'


def portrait(n):
    hy, col = HEAD[n]
    k = WIDE.get(n, {}).get('portrait', 1)
    # head and shoulders, a bit thinner line (the picture is a close-up)
    body = f'<circle cx="0" cy="{f(hy + 6 * k)}" r="{f(98 * k)}" fill="{col}"/>' + fig(n, 12, 'neutral', sw=1.35 * k)
    top = hy - (115 if n == 'vera' else 100) * k
    save(f'portrait-{n}', body, (-115 * k, top, 230 * k, 230 * k), 600, 600)


def figure(n):
    body = fig(n, 18, 'neutral')
    w = WIDE.get(n, {}).get('figure', 260)
    save(f'figure-{n}', body, (-w / 2, -490, w, 510), w * 1.5, 765)


def turnaround(n):
    body = ''
    dx = WIDE.get(n, {}).get('turn', 230)
    x0 = 175 + (dx - 230) / 2
    for i, (yaw, t) in enumerate([(0, 'спереди'), (45, 'три четверти'), (90, 'сбоку')]):
        body += f'<g transform="translate({f(x0 + i * dx)},0)">{fig(n, yaw)}</g>' + label(x0 + i * dx, 26, t)
    W = 720 + 3 * (dx - 230)
    save(f'turn-{n}', body, (40, -490, W, 535), W * 1.5, 802)


def expressions(n):
    hy, col = HEAD[n]
    wd = WIDE.get(n, {})
    dx = wd.get('expr', 200)
    k = dx / 200
    kw = {'pose': wd['pose']} if 'pose' in wd else {}
    top = hy - (128 if n == 'vera' else 105) * k
    bot = hy + 104 * k
    body = ''
    for i, (ex, t) in enumerate(EXPRS):
        x = dx / 2 + i * dx
        body += f'<circle cx="{f(x)}" cy="{f(hy + 8 * k)}" r="{f(88 * k)}" fill="{col}"/>'
        g = f'<g transform="translate({f(x)},0)">{fig(n, 8 if i % 2 else -8, ex, sw=2.0, **kw)}</g>'
        if n in WIDE:    # wider than his cell: keep him out of the neighbours'
            g = f'<clipPath id="cell{i}"><rect x="{f(x - dx / 2 + 3)}" y="{f(top)}" width="{f(dx - 6)}" height="{f(bot - top)}"/></clipPath><g clip-path="url(#cell{i})">{g}</g>'
        body += g
    body += f'<rect x="0" y="{f(bot)}" width="{5 * dx}" height="40" fill="{BG}"/>'
    for i, (ex, t) in enumerate(EXPRS):
        body += label(dx / 2 + i * dx, bot + 25, t, 15)
    save(f'expr-{n}', body, (0, top, 5 * dx, bot + 40 - top), 5 * dx * 1.4, int((bot + 40 - top) * 1.4))


def together():
    body = ''
    # a soft floor and a warm glow behind them
    body += '<ellipse cx="430" cy="0" rx="470" ry="40" fill="#e2d6c4"/>'
    body += ('<defs><radialGradient id="glow"><stop offset="0" stop-color="#f7ead4"/><stop offset=".6" stop-color="#f3e4cd"/>'
             '<stop offset="1" stop-color="#f3e4cd" stop-opacity="0"/></radialGradient></defs>'
             '<ellipse cx="430" cy="-230" rx="460" ry="330" fill="url(#glow)"/>')
    for x, (n, yaw, ex) in zip([150, 345, 540, 715], [('vera', 22, 'neutral'), ('anya', 14, 'joy'), ('tim', 22, 'neutral'), ('savely', -24, 'neutral')]):
        body += f'<g transform="translate({x},0)">{fig(n, yaw, ex)}</g>'
    save('cast', body, (20, -500, 840, 540), 1260, 810)


def together6():
    """All six. The four stand as on the cover; Марат laughs in the middle; Кира keeps a little apart."""
    body = ''
    body += '<ellipse cx="660" cy="0" rx="700" ry="42" fill="#e2d6c4"/>'
    body += ('<defs><radialGradient id="glow"><stop offset="0" stop-color="#f7ead4"/><stop offset=".6" stop-color="#f3e4cd"/>'
             '<stop offset="1" stop-color="#f3e4cd" stop-opacity="0"/></radialGradient></defs>'
             '<ellipse cx="660" cy="-240" rx="690" ry="340" fill="url(#glow)"/>')
    for x, n, yaw, ex in [(150, 'vera', 22, 'neutral'), (345, 'anya', 14, 'joy'), (590, 'marat', -14, 'joy'), (812, 'tim', -20, 'joy'),
                          (985, 'savely', -24, 'neutral'), (1185, 'kira', -26, 'neutral')]:
        body += f'<g transform="translate({x},0)">{fig(n, yaw, ex)}</g>'
    save('cast6', body, (20, -510, 1290, 550), 1935, 825)


def proportions():
    """Rule picture: how many heads tall each one is."""
    body = ''
    tops = {'vera': -432, 'anya': -380, 'tim': -269, 'savely': -290}
    heads = {'vera': 140, 'anya': 140, 'tim': 123, 'savely': 125}
    for i, n in enumerate(['vera', 'anya', 'tim', 'savely']):
        x = 110 + i * 210
        body += f'<g transform="translate({x},0)">{fig(n, 0)}</g>'
        h = heads[n]
        top = -h * round(-tops[n] / h * 10) / 10
        k = 0
        y = 0
        while y > tops[n] + 1:
            y2 = max(y - h, tops[n])
            body += f'<rect x="{x + 88}" y="{f(y2)}" width="10" height="{f(y - y2)}" fill="{"#c9a88a" if k % 2 == 0 else "#e4cfbb"}"/>'
            y = y2
            k += 1
        body += label(x, 30, f'{NAMES[n]}: {-tops[n] / h:.1f} головы', 14)
    save('rule-proportions', body, (0, -490, 860, 540), 1032, 648)


def face_signs():
    """Rule picture: the eye as one sign and the lid that carries character."""
    from face import eye, EXPR
    v = geo.View(0)
    body = ''
    P = dict(sclera=False, iris_col='#3d2a2c', lash=1.3, flick=True)
    items = [((0, 0), 'открыт: мечтательно'), ((.16, .16), 'чуть прикрыт: спокойно'), ((.36, .3), 'тяжёлое веко: устала'),
             ((.42, .3), 'низко и прямо: ворчит'), ((.1, .45), 'внешний угол вниз: грусть'), ((.48, .1), 'внутренний вниз: злость')]
    for i, (lid, t) in enumerate(items):
        x = 95 + i * 190
        E = dict(EXPR['neutral'])
        E['lid'] = lid
        geo.SW = 3
        body += eye(v, x - 22, 60, 1, 14, 19, -1, E, P, 3) + eye(v, x + 22, 60, 1, 14, 19, 1, E, P, 3)
        geo.SW = 2.4
        body += label(x, 120, t, 14)
    save('rule-eyes', body, (0, 20, 1140, 112), 1368, 134)


if __name__ == '__main__':
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    jobs = {'portrait': portrait, 'figure': figure, 'turn': turnaround, 'expr': expressions}
    for n in cast.CAST:
        for k, fn in jobs.items():
            if not only or k in only or n in only:
                fn(n)
    if not only or 'cast' in only:
        together()
    if not only or 'cast6' in only:
        together6()
    if not only or 'rules' in only:
        proportions()
        face_signs()
