"""Builds every picture of the page: svg/*.svg (hand-built shapes, see cast.py) and pics/*.png (headless Chrome).
Run: python3 tools/build.py   (from styles/s5-indie)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo
import cast
import render
from geo import f

ROOT = os.path.dirname(HERE)
SVG = os.path.join(ROOT, 'svg')
PNG = os.path.join(ROOT, 'pics')
os.makedirs(SVG, exist_ok=True)
os.makedirs(PNG, exist_ok=True)

BG = '#ece5d9'
NAMES = {'anya': 'Аня', 'savely': 'Савелий Петрович', 'tim': 'Тим', 'vera': 'Вера'}
# head centre (body coords) and the portrait background colour per character
HEAD = {'anya': (-306, '#f3dccb'), 'savely': (-226, '#dfe3d2'), 'tim': (-205, '#d9e3ef'), 'vera': (-352, '#e3d9e3')}
EXPRS = [('neutral', 'спокойно'), ('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('anger', 'злость')]
FONT = 'font-family="system-ui, -apple-system, Segoe UI, sans-serif"'


def save(name, body, vb, w, h, bg=BG, sw=2.4):
    path = os.path.join(SVG, name + '.svg')
    open(path, 'w').write(geo.svg(body, vb, w, h, bg=bg))
    if '--svg' not in sys.argv:
        render.png(path, os.path.join(PNG, name + '.png'))
    print(name)


def fig(name, yaw=0, ex='neutral', sw=2.4):
    geo.SW = sw
    s = cast.render(name, yaw, ex)
    geo.SW = 2.4
    return s


def label(x, y, text, size=15, col='#6d6259'):
    return f'<text x="{f(x)}" y="{f(y)}" text-anchor="middle" font-size="{size}" fill="{col}" {FONT}>{text}</text>'


def portrait(n):
    hy, col = HEAD[n]
    # head and shoulders, a bit thinner line (the picture is a close-up)
    body = f'<circle cx="0" cy="{f(hy + 6)}" r="98" fill="{col}"/>' + fig(n, 12, 'neutral', sw=1.35)
    top = hy - (115 if n == 'vera' else 100)
    save(f'portrait-{n}', body, (-115, top, 230, 230), 600, 600)


def figure(n):
    body = fig(n, 18, 'neutral')
    save(f'figure-{n}', body, (-130, -490, 260, 510), 390, 765)


def turnaround(n):
    body = ''
    for i, (yaw, t) in enumerate([(0, 'спереди'), (45, 'три четверти'), (90, 'сбоку')]):
        body += f'<g transform="translate({175 + i * 230},0)">{fig(n, yaw)}</g>' + label(175 + i * 230, 26, t)
    save(f'turn-{n}', body, (40, -490, 720, 535), 1080, 802)


def expressions(n):
    hy, col = HEAD[n]
    top = hy - (128 if n == 'vera' else 105)
    body = ''
    for i, (ex, t) in enumerate(EXPRS):
        x = 100 + i * 200
        body += f'<circle cx="{x}" cy="{f(hy + 8)}" r="88" fill="{col}"/>'
        body += f'<g transform="translate({x},0)">{fig(n, 8 if i % 2 else -8, ex, sw=2.0)}</g>'
    body += f'<rect x="0" y="{f(hy + 104)}" width="1000" height="40" fill="{BG}"/>'
    for i, (ex, t) in enumerate(EXPRS):
        body += label(100 + i * 200, hy + 129, t, 15)
    save(f'expr-{n}', body, (0, top, 1000, hy + 144 - top), 1400, int((hy + 144 - top) * 1.4))


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
    if not only or 'rules' in only:
        proportions()
        face_signs()
