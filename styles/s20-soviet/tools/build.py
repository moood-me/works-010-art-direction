"""Build every sheet of С20 into ../svg.   python3 build.py [name …]   (no names = all)

Sheets: portrait-<who>, figure-<who>, turn-<who>, expr-<who>, cast (the four), cast6 (all six), rule-*.
"""
import math, os, sys, importlib
import kit as K
from kit import form, ink, paint, ell, hatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'svg')

WHO = ['anya', 'savely', 'tim', 'vera', 'marat', 'kira']
MOD = {w: importlib.import_module(w) for w in WHO}
# a flat background colour for each, as Khitruk's films set a figure on one bright field
BG = {'anya': '#9fd0dd', 'savely': '#e7b84a', 'tim': '#f0c64a', 'vera': '#e9b9a0', 'marat': '#8cc6d6',
      'kira': '#c9c19a'}
TURN = ['anya', 'tim', 'marat', 'kira']
EXPRS = [('joy', 'радость'), ('surprise', 'удивление'), ('sadness', 'грусть'), ('anger', 'злость')]


# ------------------------------------------------------------------ scenery
def cloud(x, y, w, seed=0):
    r = K.rng()
    pts = []
    n = 14
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = 1 + 0.25 * math.sin(3 * a + seed) + 0.1 * r.uniform(-1, 1)
        pts.append((x + w * math.cos(a) * rr, y + w * 0.32 * math.sin(a) * rr))
    return paint(pts, '#fbfaf3', 'crayon', off=False, op=0.95)


def flower(x, y, s, color):
    out = ''
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.3
        out += paint(ell(x + 3.4 * s * math.cos(a), y + 3.4 * s * math.sin(a), 2.6 * s, 2.6 * s, 7), color, 'crayon',
                     off=False)
    out += K.dot(x, y, 1.2 * s, '#3a2a1a')
    return out


def meadow(w, h, y0, color='#b3bf55', seed=3, flowers=70):
    """A strip of grass painted with a dry brush, crayon flowers scattered over it (as in «Фильм, фильм, фильм»)."""
    r = K.rng()
    pts = [(-20, y0 + 10)]
    for i in range(13):
        x = i * w / 12
        pts.append((x, y0 + 6 * math.sin(i * 1.3 + seed) + r.uniform(-3, 3)))
    pts += [(w + 20, y0 + 6), (w + 20, h + 20), (-20, h + 20)]
    out = paint(pts, color, 'brush', off=False)
    out += hatch(pts, '#5e7d22', angle=-1.45, step=7, lw=1.1, op=0.45)
    cols = ['#e2584a', '#f2c43a', '#fbf6ea', '#4f7fc0', '#e88a3a']
    for i in range(flowers):
        x, y = r.uniform(10, w - 10), r.uniform(y0 + 14, h - 6)
        out += flower(x, y, r.uniform(1.3, 2.1), cols[i % len(cols)])
    return out


def field(d, bg, clouds=()):
    d.add('<rect width="%d" height="%d" fill="%s"/>' % (d.w, d.h, bg))
    for c in clouds:
        d.add(cloud(*c))


def label(d, x, y, s, size=24):
    d.add(K.text(x, y, s, size))


def place(mod, view, expr, pose, x, y, s, seed=1):
    with K.scaled(s, seed):
        return K.group([mod.figure(view, expr, pose)], x, y, s)


def shadow(x, y, w, s=1.0):
    with K.scaled(s):
        return K.group([paint(ell(0, 0, w, 7, 12), '#2a3a10', 'crayon', off=False, op=0.35)], x, y, s)


# ------------------------------------------------------------------ sheets
def portrait(who):
    m = MOD[who]
    W, H = 900, 1000
    d = K.Doc(W, H)
    field(d, BG[who], [(170, 150, 90), (730, 230, 70)])
    frac = {'anya': 0.58, 'savely': 0.68, 'tim': 0.76, 'vera': 0.52, 'marat': 0.6, 'kira': 0.56}[who]
    s = 880 / (m.HEIGHT * frac)
    d.add(place(m, 'three', 'calm', 'stand', W / 2 - (30 if who == 'marat' else 10), 100 + m.HEIGHT * s, s))
    d.add(K.text(36, H - 34, m.NAME, 34, anchor='start'))
    d.save(os.path.join(OUT, 'portrait-%s.svg' % who))


def figure(who):
    m = MOD[who]
    W, H = 900, 1100
    d = K.Doc(W, H)
    field(d, BG[who], [(180, 160, 80), (720, 110, 60)])
    s = 860 / (m.HEIGHT + (70 if who == 'marat' else 30))
    gy = H - 110
    d.add(meadow(W, H, gy - 40, seed=len(who)))
    d.add(shadow(W / 2, gy, 90 if who == 'marat' else 50, s))
    d.add(place(m, 'three', 'calm', 'act', W / 2 - {'tim': 40, 'savely': 30, 'marat': 20}.get(who, 0), gy, s))
    d.add(K.text(36, 60, m.NAME, 34, anchor='start'))
    d.save(os.path.join(OUT, 'figure-%s.svg' % who))


def turn(who):
    m = MOD[who]
    W, H = 1500, 950
    d = K.Doc(W, H)
    field(d, BG[who])
    s = 720 / max(m.HEIGHT + 40, 420)
    gy = H - 110
    d.add('<rect x="0" y="%d" width="%d" height="%d" fill="#000" opacity="0.06"/>' % (gy, W, H - gy))
    for i, (v, cap) in enumerate([('front', 'анфас'), ('three', 'три четверти'), ('side', 'профиль')]):
        x = 260 + i * 490
        d.add(shadow(x, gy, 90 if who == 'marat' else 45, s))
        d.add(place(m, v, 'calm', 'stand', x, gy, s, seed=7))
        d.add(K.text(x, H - 40, cap, 28))
    d.add(K.text(36, 56, m.NAME, 34, anchor='start'))
    d.save(os.path.join(OUT, 'turn-%s.svg' % who))


def expr(who):
    m = MOD[who]
    W, H = 1600, 560
    d = K.Doc(W, H)
    field(d, BG[who])
    for i, (e, cap) in enumerate(EXPRS):
        x = 200 + i * 400
        s = {'marat': 2.0, 'anya': 2.2}.get(who, 2.4)
        y = {'marat': 270, 'savely': 270, 'tim': 290, 'vera': 300}.get(who, 270)
        with K.scaled(s, 11):
            d.add(K.group([m.head('three', e)], x, y, s))
        d.add(K.text(x, H - 40, cap, 28))
    d.add(K.text(30, 46, m.NAME, 30, anchor='start'))
    d.save(os.path.join(OUT, 'expr-%s.svg' % who))


def cast(names, fname, W, order_x, s=1.0):
    H = 900
    d = K.Doc(W, H)
    field(d, '#8fcde0', [(200, 110, 110), (W * 0.47, 70, 80), (W - 240, 130, 100)])
    gy = H - 80
    d.add(meadow(W, H, gy - 50, seed=5, flowers=110 if W > 2000 else 80))
    for who, x in zip(names, order_x):
        m = MOD[who]
        d.add(shadow(x, gy, 95 if who == 'marat' else 50, s))
    for who, x in zip(names, order_x):
        m = MOD[who]
        d.add(place(m, 'three', 'calm', 'act', x, gy, s))
    d.save(os.path.join(OUT, fname + '.svg'))


def rule_line():
    """How a thing is made: the line, the paint off register, the crayon, the hatching, the paper."""
    W, H = 1500, 520
    d = K.Doc(W, H)
    d.add('<rect width="%d" height="%d" fill="#ede3cc"/>' % (W, H))
    s = 2.2
    cols = [('линия с нажимом', 0), ('краска мимо линии', 1), ('мелок и штрих', 2), ('бумага вместо лица', 3)]
    for i, (cap, k) in enumerate(cols):
        x = 190 + i * 370
        with K.scaled(s, 21 + i):
            if k == 0:
                g = [ink([(-60, 40), (-30, -40), (20, -60), (60, -10), (40, 50)], 3.4, taper=0.3, press=[0.6, 1.4, 1.0, 0.5]),
                     ink(K.ell(0, 10, 30, 22, 12), 2.4, closed=True, weight=1.2)]
            elif k == 1:
                pts = K.ell(0, 0, 60, 50, 12)
                g = [form(pts, '#c8582f', lw=2.6, tex='brush'), form(K.ell(10, -6, 18, 14, 10), '#e2a93a', lw=1.8)]
            elif k == 2:
                pts = [(-60, -50), (60, -50), (64, 50), (-56, 54)]
                g = [paint(pts, '#f4ecda', 'flat'), hatch(pts, '#2f5f9e', angle=0.02, step=10, lw=4.2, op=0.9, jitter=0.05),
                     ink(pts, 2.4, closed=True), K.blush(0, 90, 24)]
            else:
                import savely
                g = [savely.head('front', 'calm')]
            d.add(K.group(g, x, 220, s if k < 3 else 1.9))
        d.add(K.text(x, H - 40, cap, 26))
    d.save(os.path.join(OUT, 'rule-line.svg'))


def rule_heads():
    """Each head is one bold shape; the nose is the biggest thing on it."""
    W, H = 1700, 520
    d = K.Doc(W, H)
    d.add('<rect width="%d" height="%d" fill="#ede3cc"/>' % (W, H))
    caps = {'anya': 'яйцо', 'savely': 'ящик', 'tim': 'шар', 'vera': 'карандаш', 'marat': 'котёл', 'kira': 'клин'}
    order = ['tim', 'savely', 'kira', 'anya', 'vera', 'marat']
    for i, w in enumerate(order):
        x = 150 + i * 280
        s = 1.9
        with K.scaled(s, 31):
            d.add(K.group([MOD[w].head('three', 'calm')], x, 250, s))
        d.add(K.text(x, H - 70, MOD[w].NAME, 24))
        d.add(K.text(x, H - 36, caps[w], 22, italic=True))
    d.save(os.path.join(OUT, 'rule-heads.svg'))


def build(names):
    os.makedirs(OUT, exist_ok=True)
    jobs = {}
    for w in WHO:
        jobs['portrait-' + w] = lambda w=w: portrait(w)
        jobs['figure-' + w] = lambda w=w: figure(w)
        jobs['expr-' + w] = lambda w=w: expr(w)
    for w in TURN:
        jobs['turn-' + w] = lambda w=w: turn(w)
    jobs['cast'] = lambda: cast(['tim', 'anya', 'savely', 'vera'], 'cast', 1800, [330, 700, 1090, 1450], 1.55)
    jobs['cast6'] = lambda: cast(['kira', 'tim', 'anya', 'marat', 'savely', 'vera'], 'cast6', 2400,
                                 [250, 560, 880, 1290, 1720, 2100], 1.4)
    jobs['rule-line'] = rule_line
    jobs['rule-heads'] = rule_heads
    for n in (names or list(jobs)):
        K.USED.clear()
        jobs[n]()
        print('svg', n)


if __name__ == '__main__':
    build(sys.argv[1:])
