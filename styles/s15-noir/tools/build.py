"""Composes every picture -> ../svg, then render.js -> ../pics.   python3 build.py [part of a name]"""
import os, sys, subprocess
from noir import *
from head import head, neck, EXPR
from cast import CAST, NAMES, REST
from figures import figure, BODY, HEIGHT

HERE = os.path.dirname(os.path.abspath(__file__)); SVG = os.path.join(HERE, '..', 'svg')
PICS = {}
BACK = dict(anya=('#3b3350', '#d9c9a0'), sav=('#2c3a36', '#b99a4e'), tim=('#2b3550', '#c8553a'), vera=('#27343c', '#8c3a36'), marat=('#40302a', '#d9793f'), kira=('#2d2638', '#c9e23a'))
ORDER4 = ['anya', 'sav', 'tim', 'vera']; ORDER6 = ORDER4 + ['marat', 'kira']


def pic(name):
    def deco(f):
        PICS[name] = f
        return f
    return deco


def window(x, y, w, h, col, bars=True):
    """A lit window behind the figure: the dark side of the head reads against it."""
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}"/>'
    if bars:
        s += f'<rect x="{x + w * 0.5 - 4}" y="{y}" width="8" height="{h}" fill="{NIGHT}"/><rect x="{x}" y="{y + h * 0.42}" width="{w}" height="8" fill="{NIGHT}"/>'
    return s


def portrait(k):
    W, H = 800, 1000
    c1, c2 = BACK[k]
    b = BODY[k](); nx, ny = b['neck']; s = {'marat': 2.7, 'tim': 3.3}.get(k, 3.2)
    inner = f'<circle cx="{W * 0.56}" cy="{H * 0.42}" r="330" fill="{c1}"/>'
    inner += figure(k, x=W * 0.52 - nx * s, y=H * 0.66 - ny * s, s=s)
    return svg(W, H, inner)


def fig(k):
    W, H = 700, 1000
    c1, c2 = BACK[k]
    inner = window(W * 0.5 - 150, 40, 330, 830, c1) + f'<rect y="{H - 96}" width="{W}" height="96" fill="#1a1c28"/>'
    inner += f'<polygon points="{W*0.5-150},{H-96} {W*0.5+180},{H-96} {W*0.5+420},{H} {W*0.5-60},{H}" fill="{c1}" opacity="0.55"/>'
    s = 1.16 if k != 'marat' else 1.0
    inner += figure(k, x=W * 0.5 + (10 if k != 'marat' else 0), y=H - 70, s=s)
    return svg(W, H, inner)


for _k in ORDER6:
    PICS['portrait-' + _k] = (lambda k=_k: portrait(k))
    PICS['figure-' + _k] = (lambda k=_k: fig(k))


def bust(view, k):
    """Shoulders under a head for the turnaround and expression sheets (head units)."""
    w = {'f': 1.0, 'q': 0.82, 's': 0.5}[view]; sh = {'f': 0, 'q': 14, 's': 22}[view]
    col, W, top = dict(anya=('#c9982f', 108, 150), sav=('#3f5a48', 112, 152), tim=('#e6dcc4', 92, 146), vera=('#2f5560', 108, 150), marat=('#e8dfca', 150, 150), kira=('#4b2d4f', 112, 138))[k]
    W *= w; cx = {'f': 0, 'q': 22, 's': 30}[view]
    pts = [(cx - W, top + 34), (cx - W * 0.45, top + 4), (cx + W * 0.45 + sh * 0.3, top), (cx + W + sh * 0.2, top + 30), (cx + W + 6, 330), (cx - W - 6, 330)]
    shd = [[(cx + W * 0.25, top - 10), (cx + W * 0.4, top + 60), (cx + W * 0.2, 340), (cx + W + 40, 340), (cx + W + 40, top - 10)]]
    under = []
    vx = cx - W * (0.3 if view != 'f' else 0)
    if k == 'anya':
        under = [([(vx - 26, top), (vx + 26, top - 2), (vx, top + 70)], CAST[k]['skin']), ([(vx - 13, top + 34), (vx + 13, top + 32), (vx, top + 70)], '#4b6788')]
    if k == 'sav':
        under = [([(vx - 24, top - 2), (vx + 24, top - 2), (vx + 6, top + 110), (vx - 6, top + 110)], '#cfc9b8'), ([(vx - 16, top + 22), (vx, top + 10), (vx + 16, top + 22), (vx, top + 36)], '#7a2e2a')]
    if k == 'vera':
        under = [([(vx - 22, top - 2), (vx + 22, top - 2), (vx, top + 64)], '#d8d2c2')]
    if k == 'marat':
        under = [([(vx - 60, top + 110), (vx + 200, top + 100), (vx + 200, 340), (vx - 70, 340)], '#c2582e')]
    s = form(pts, col, lit=(-8, -4), shadows=shd, under=under)
    if k == 'tim':
        s += clip(pts, ''.join(shape([(cx - 200, y), (cx + W * 0.25 - 8, y - 5), (cx + W * 0.3 - 8, y + 13), (cx - 200, y + 18)], '#c23b2c') for y in range(top + 20, 340, 40)))
    if k == 'kira':
        lime = '#c9e23a'; a = cx - W * 0.5; b2 = cx + W * 0.5
        s += line([(a + 6, top + 8), (cx - 6, top + 26, 's'), (b2 - 6, top + 6)], lime, 9)
        s += form([(a - 8, top - 22), (a + 14, top - 26), (a + 18, top + 22), (a - 4, top + 26)], lime, lit=(-3, -2))
        if view != 's':
            s += form([(b2 - 12, top - 26), (b2 + 10, top - 22), (b2 + 12, top + 24), (b2 - 10, top + 20)], lime, lit=(-3, -2), shadows=[[(b2 + 2, top - 30), (b2 + 2, top + 30), (b2 + 20, top + 30), (b2 + 20, top - 30)]])
    return s


def bustfig(view, k, e, x, y, s, rot=0):
    p = CAST[k]
    if view == 'f':   # long hair goes behind the neck and the shoulders
        return g(head(view, p, e, part='back') + neck(view, p) + bust(view, k) + head(view, p, e, part='front'), x, y, s)
    return g(neck(view, p) + bust(view, k) + g(head(view, p, e), 0, 0, 1, rot=rot), x, y, s)


def turn(k):
    W, H = 1800, 800; c1, c2 = BACK[k]; inner = ''
    for i, (v, lab) in enumerate([('f', 'анфас'), ('q', 'три четверти'), ('s', 'профиль')]):
        x = 310 + i * 590
        inner += f'<rect x="{x - 210}" y="70" width="440" height="{H - 70}" fill="{c1}"/>'
        inner += bustfig(v, k, REST[k] if k != 'marat' else 'smile', x, 370, 2.0) + text(x + 10, 46, lab)
    return svg(W, H, inner)


def expr(k):
    W, H = 2000, 700; c1, c2 = BACK[k]; inner = ''
    for i, (e, lab) in enumerate([('joy', 'радость'), ('surprise', 'удивление'), ('sadness', 'грусть'), ('anger', 'злость')]):
        x = 270 + i * 490
        inner += f'<circle cx="{x + 14}" cy="350" r="215" fill="{c1}"/>'
        rot = {'joy': -4, 'surprise': 3, 'sadness': -9, 'anger': -3}[e]
        inner += bustfig('q', k, e, x, 345, 1.75, rot=rot) + text(x + 14, 60, lab)
    return svg(W, H, clip([(0, 0), (W, 0), (W, H), (0, H)], inner))


def street(W, H, gy, lamp_x, disc):
    """Night street: a big disc of sky light, black roofs with a few lit windows, a lamp in the middle — the light comes from it."""
    import random
    r = random.Random(7); s = f'<circle cx="{lamp_x}" cy="{gy - 430}" r="{H * 0.47}" fill="{disc}"/>'
    x = -20
    while x < W:
        w = r.randint(110, 220); h = r.randint(260, 560)
        s += f'<rect x="{x}" y="{gy - h}" width="{w}" height="{h}" fill="#1b1d2a"/>'
        if r.random() < 0.6:
            s += f'<polygon points="{x},{gy - h} {x + w * 0.5},{gy - h - r.randint(30, 70)} {x + w},{gy - h}" fill="#1b1d2a"/>'
        for _ in range(r.randint(1, 3)):
            wx = x + r.randint(14, max(15, w - 40)); wy = gy - h + r.randint(30, max(31, h - 240))
            s += f'<rect x="{wx}" y="{wy}" width="18" height="28" fill="#b99a4e"/>'
        x += w + r.randint(-10, 30)
    s += f'<rect y="{gy - 14}" width="{W}" height="{H - gy + 14}" fill="#1a1c28"/>'
    s += f'<polygon points="{lamp_x - 620},{gy - 14} {lamp_x + 620},{gy - 14} {lamp_x + 900},{H} {lamp_x - 900},{H}" fill="#2a2e40"/>'
    # the lamp
    s += f'<rect x="{lamp_x - 5}" y="{gy - 640}" width="10" height="640" fill="{BLACK}"/><polygon points="{lamp_x - 34},{gy - 640} {lamp_x + 34},{gy - 640} {lamp_x + 22},{gy - 690} {lamp_x - 22},{gy - 690}" fill="#e9dfb8"/>'
    s += f'<polygon points="{lamp_x - 40},{gy - 692} {lamp_x + 40},{gy - 692} {lamp_x},{gy - 730}" fill="{BLACK}"/>'
    s += f'<polygon points="{lamp_x - 34},{gy - 640} {lamp_x + 34},{gy - 640} {lamp_x + 520},{gy - 14} {lamp_x - 520},{gy - 14}" fill="#e9dfb8" opacity="0.07"/>'
    return s


def cast_shadow(x, gy, lx, w=40):
    dr = 1 if x > lx else -1; L = 150 + abs(x - lx) * 0.35
    return f'<polygon points="{x - w},{gy + 22} {x + w},{gy + 22} {x + dr * L + w * 1.6},{gy + 96} {x + dr * L - w},{gy + 96}" fill="{BLACK}" opacity="0.8"/>'


@pic('cast')
def cast4():
    W, H = 2000, 1125; gy = 1010; lx = 1000
    inner = street(W, H, gy, lx, '#3a2f4a') + ''.join(cast_shadow(x, gy, lx, w) for x, w in [(430, 30), (760, 40), (1250, 40), (1570, 30)])
    inner += figure('vera', x=430, y=gy + 20, flip=True) + figure('tim', x=760, y=gy + 44, flip=True)
    inner += figure('sav', x=1250, y=gy + 30) + figure('anya', x=1570, y=gy + 36)
    return svg(W, H, inner)


@pic('cast6')
def cast6():
    W, H = 2400, 1125; gy = 1010; lx = 1130
    inner = street(W, H, gy, lx, '#3a2f4a') + ''.join(cast_shadow(x, gy, lx, w) for x, w in [(300, 30), (600, 30), (900, 40), (1340, 40), (1620, 30), (2020, 80)])
    inner += figure('kira', x=300, y=gy + 20, flip=True) + figure('vera', x=600, y=gy + 24, flip=True) + figure('tim', x=900, y=gy + 46, flip=True)
    inner += figure('sav', x=1340, y=gy + 30) + figure('anya', x=1620, y=gy + 40) + figure('marat', x=2020, y=gy + 30)
    return svg(W, H, inner)


for _k in ['anya', 'sav', 'kira']:
    PICS['turn-' + _k] = (lambda k=_k: turn(k))
for _k in ['anya', 'tim', 'marat', 'kira']:
    PICS['expr-' + _k] = (lambda k=_k: expr(k))


if __name__ == '__main__':
    want = sys.argv[1:]
    names = [n for n in PICS if not want or any(w in n for w in want)]
    files = []
    for n in names:
        f = os.path.join(SVG, n + '.svg'); open(f, 'w').write(PICS[n]()); files.append(f)
    subprocess.run(['node', os.path.join(HERE, 'render.js')] + files, check=True)
    print(len(files), 'pictures')
