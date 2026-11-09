"""Build every picture of the page: svg/*.svg and pics/*.png.   python3 tools/build.py [name-filter]"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lc, r3, scene, figures, cast, features as F, hands as Hd
from head import Glyph

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG, PNG = os.path.join(HERE, 'svg'), os.path.join(HERE, 'pics')
os.makedirs(SVG, exist_ok=True)
os.makedirs(PNG, exist_ok=True)
FILTER = sys.argv[1] if len(sys.argv) > 1 else ''
PAPER = '#f4ecd8'
NAMES = ['anya', 'savely', 'tim', 'vera']
RU = {'anya': 'Аня', 'savely': 'Савелий Петрович', 'tim': 'Тим', 'vera': 'Вера'}
PANEL = {'anya': '#cfe3e8', 'savely': '#ead9b4', 'tim': '#f2d9a6', 'vera': '#d7dbe3'}
EXPRS = ['joy', 'surprise', 'sad', 'anger']


def want(name):
    return not FILTER or FILTER in name


def save(d, name):
    p = os.path.join(SVG, name + '.svg')
    d.save(p)
    lc.render(p, os.path.join(PNG, name + '.png'), d.w, d.h)
    print(name, flush=True)


def panel(d, x, y, w, h, fill, lw=2.6):
    """A comic panel: flat colour, an even black frame."""
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{lc.INK}" stroke-width="{lw}"/>')


def clip_panel(d, cid, x, y, w, h):
    d.defs.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>')
    return f'<g clip-path="url(#{cid})">', '</g>'


def fig(name, bust=False, **kw):
    return getattr(figures, name + '_figure')(bust, **kw)


# ------------------------------------------------------------------------------------------------ portraits
def portrait(name, expr='calm', yaw=-20, w=500, h=600, s=1.42, tag='portrait'):
    f, col, floor = fig(name, True)
    d = lc.Doc(w, h, PAPER)
    panel(d, 14, 14, w - 28, h - 28, PANEL[name])
    g0, g1 = clip_panel(d, 'pp', 14, 14, w - 28, h - 28)
    cy = 70 + 118 * s
    v = r3.View(yaw=yaw, s=s, cx=w / 2, cy=cy)
    items, _ = scene.render([(f, dict(expr=F.EXPR[expr]))], v, (0, 0, w, h), col, lw=2.5, clip_prefix='p')
    d.add(g0, items, g1)
    panel(d, 14, 14, w - 28, h - 28, 'none')
    return d


# ------------------------------------------------------------------------------------------------ figures
def figure(name, yaw=-22, w=500, h=900):
    f, col, floor = fig(name)
    d = lc.Doc(w, h, PAPER)
    panel(d, 14, 14, w - 28, h - 28, PANEL[name])
    s = 780 / (1290 + 120)
    top = 60
    fy = h - 60                                   # where the floor is drawn
    cy = fy - floor * s
    d.add(f'<rect x="14" y="{fy - 8:.0f}" width="{w - 28}" height="{h - 14 - fy + 8:.0f}" '
          f'fill="{lc.mix(PANEL[name], "#7a6a58", 0.25)}"/>')
    d.add(lc.line([(14, fy - 8), (w - 14, fy - 8)], 1.6))
    v = r3.View(yaw=yaw, pitch=-7, s=s, cx=w / 2, cy=cy)
    items, _ = scene.render([(f, dict(expr=F.EXPR['calm']))], v, (0, 0, w, h), col, lw=1.9, clip_prefix='f')
    d.add(items)
    panel(d, 14, 14, w - 28, h - 28, 'none')
    return d


# ------------------------------------------------------------------------------------------------ turnarounds
def turnaround(name, w=1260, h=520, side=-1, **kw):
    """side: -1 turns the character to our left (the four), +1 to our right; kw goes to the figure."""
    d = lc.Doc(w, h, PAPER)
    cw = w / 3
    for i, (yaw, lab) in enumerate([(0, 'анфас'), (side * 45, 'три четверти'), (side * 90, 'профиль')]):
        f, col, floor = fig(name, True, head_rot=(0, 0, 0), **kw)
        x0 = i * cw
        panel(d, x0 + 12, 12, cw - 24, h - 60, PANEL[name])
        g0, g1 = clip_panel(d, f'tc{i}', x0 + 12, 12, cw - 24, h - 60)
        s = 1.05
        v = r3.View(yaw=yaw, s=s, cx=x0 + cw / 2, cy=50 + 118 * s)
        items, _ = scene.render([(f, {})], v, (x0, 0, x0 + cw, h - 48), col, lw=2.2, clip_prefix=f't{i}')
        d.add(g0, items, g1)
        panel(d, x0 + 12, 12, cw - 24, h - 60, 'none')
        d.add(lc.text(x0 + cw / 2, h - 20, lab, 18))
    return d


# ------------------------------------------------------------------------------------------------ expressions
EXPR_RU = {'joy': 'радость', 'surprise': 'удивление', 'sad': 'грусть', 'anger': 'злость'}
EXPR_HEAD = {'joy': (-3, 0, 4), 'surprise': (-4, 0, 0), 'sad': (10, 0, -4), 'anger': (6, 0, 0)}


def expressions(name, w=1240, h=420):
    d = lc.Doc(w, h, PAPER)
    cw = w / 4
    for i, e in enumerate(EXPRS):
        f, col, floor = fig(name, True, head_rot=EXPR_HEAD[e])
        x0 = i * cw
        panel(d, x0 + 10, 10, cw - 20, h - 56, PANEL[name])
        g0, g1 = clip_panel(d, f'ec{i}', x0 + 10, 10, cw - 20, h - 56)
        s = 1.1
        v = r3.View(yaw=-18, s=s, cx=x0 + cw / 2, cy=40 + 118 * s)
        items, _ = scene.render([(f, dict(expr=F.EXPR[e]))], v, (x0, 0, x0 + cw, h - 46), col, lw=2.2,
                                clip_prefix=f'e{i}')
        d.add(g0, items, g1)
        panel(d, x0 + 10, 10, cw - 20, h - 56, 'none')
        d.add(lc.text(x0 + cw / 2, h - 18, EXPR_RU[e], 18))
    return d


# ------------------------------------------------------------------------------------------------ the street
def street(d, w, h, ground):
    """A street in Brussels-comic manner: flat colours, the same clean line, a watchmaker's shop."""
    L = 1.6
    d.add(f'<rect width="{w}" height="{h}" fill="#cfe2e6"/>')
    # clouds: flat, white, outlined (Chaland's sky)
    for cx, cy, k in ((260, 90, 1.0), (1180, 60, 0.8)):
        pts = [(cx - 90 * k, cy + 20 * k), (cx - 70 * k, cy - 6 * k), (cx - 30 * k, cy - 10 * k),
               (cx - 10 * k, cy - 30 * k), (cx + 30 * k, cy - 26 * k), (cx + 50 * k, cy - 6 * k),
               (cx + 90 * k, cy), (cx + 96 * k, cy + 20 * k)]
        d.add(lc.shape(pts, '#fbfaf4', L, corners=(0, len(pts) - 1)))
    # the building
    bx0, bx1 = 120, 1380
    d.add(lc.poly([(bx0, 150), (bx1, 150), (bx1, ground), (bx0, ground)], '#e6cf9f', L))
    d.add(lc.poly([(bx0 - 14, 136), (bx1 + 14, 136), (bx1 + 14, 154), (bx0 - 14, 154)], '#d2b783', L))
    # upper windows
    for x in (180, 1090, 1260):
        d.add(lc.poly([(x, 190), (x + 90, 190), (x + 90, 300), (x, 300)], '#5c7f8c', L))
        d.add(lc.line([(x + 45, 190), (x + 45, 300)], L))
        d.add(lc.line([(x, 245), (x + 90, 245)], L))
        d.add(lc.poly([(x - 8, 300), (x + 98, 300), (x + 98, 310), (x - 8, 310)], '#d2b783', L))
    # the shop front: dark green wood, a sign, a window, a door
    sx0, sx1, top = 520, 1000, 160
    d.add(lc.poly([(sx0, top), (sx1, top), (sx1, ground), (sx0, ground)], '#2f5a4c', L))
    d.add(lc.poly([(sx0 + 14, top + 14), (sx1 - 14, top + 14), (sx1 - 14, top + 74), (sx0 + 14, top + 74)],
                  '#1f3d34', L))
    d.add(lc.text((sx0 + sx1) / 2, top + 56, 'ЧАСЫ · РЕМОНТ', 34, fill='#e9c46a'))
    wx0, wx1 = sx0 + 24, sx0 + 270
    d.add(lc.poly([(wx0, top + 96), (wx1, top + 96), (wx1, ground - 90), (wx0, ground - 90)], '#a9c8cc', L))
    for k in range(1, 3):
        x = wx0 + (wx1 - wx0) * k / 3
        d.add(lc.line([(x, top + 96), (x, ground - 90)], L))
    # clocks in the window
    for cx, cy, r in ((wx0 + 46, top + 160, 26), (wx0 + 126, top + 150, 18), (wx0 + 205, top + 172, 30)):
        d.add(lc.ellipse(cx, cy, r, r, '#e9c46a', L))
        d.add(lc.ellipse(cx, cy, r * 0.74, r * 0.74, '#fbf8ee', L * 0.7))
        d.add(lc.line([(cx, cy), (cx, cy - r * 0.55)], L * 0.8))
        d.add(lc.line([(cx, cy), (cx + r * 0.4, cy + r * 0.15)], L * 0.8))
    d.add(lc.poly([(wx0 - 6, ground - 90), (wx1 + 6, ground - 90), (wx1 + 6, ground - 78), (wx0 - 6, ground - 78)],
                  '#1f3d34', L))
    dx0, dx1 = sx1 - 150, sx1 - 30
    d.add(lc.poly([(dx0, top + 96), (dx1, top + 96), (dx1, ground), (dx0, ground)], '#264a3f', L))
    d.add(lc.poly([(dx0 + 16, top + 112), (dx1 - 16, top + 112), (dx1 - 16, top + 250), (dx0 + 16, top + 250)],
                  '#a9c8cc', L))
    d.add(lc.ellipse(dx0 + 18, top + 300, 5, 5, '#e9c46a', L * 0.8))
    # the big clock on a bracket
    kx = sx0 - 4
    d.add(lc.line([(kx, 190), (kx - 66, 190)], L * 1.6))
    d.add(lc.ellipse(kx - 66, 250, 46, 46, '#e9c46a', L))
    d.add(lc.ellipse(kx - 66, 250, 36, 36, '#fbf8ee', L))
    d.add(lc.line([(kx - 66, 250), (kx - 66, 224)], L))
    d.add(lc.line([(kx - 66, 250), (kx - 48, 260)], L))
    d.add(lc.line([(kx - 66, 204), (kx - 66, 196)], L))
    # a poster on the wall
    d.add(lc.poly([(150, 380), (260, 380), (260, 560), (150, 560)], '#c7553a', L))
    d.add(lc.poly([(162, 396), (248, 396), (248, 480), (162, 480)], '#f1e6c8', L))
    d.add(lc.ellipse(205, 438, 24, 24, '#e9c46a', L))
    d.add(lc.text(205, 520, 'КИНО', 24, fill='#f1e6c8'))
    # pavement and kerb
    d.add(lc.poly([(0, ground), (w, ground), (w, h), (0, h)], '#cbc3b2', L))
    for x in range(-40, w + 80, 120):
        d.add(lc.line([(x, ground), (x - 60, h)], L * 0.7))
    d.add(lc.poly([(0, h - 40), (w, h - 40), (w, h), (0, h)], '#9d968a', L))


def cast_picture(w=1500, h=900):
    d = lc.Doc(w, h, PAPER)
    ground = 640
    street(d, w, h, ground)
    s = 0.5
    v = r3.View(yaw=0, pitch=-6, s=s, cx=0, cy=0)
    chars = []
    floor_y = (ground + 150) / s          # model y of the people's floor (they stand on the pavement)
    places = {
        'vera': dict(x=330 / s, yaw=24, scale=0.93, expr=F.EXPR['calm']),
        'savely': dict(x=760 / s, yaw=-14, scale=1.0, expr=F.EXPR['calm'], z=-40),
        'anya': dict(x=1010 / s, yaw=-34, scale=1.0, expr=F.EXPR['dream'], z=10),
        'tim': dict(x=1230 / s, yaw=-30, scale=0.94, expr=F.EXPR['joy'], z=60),
    }
    cols = {}
    for name in ['vera', 'savely', 'anya', 'tim']:
        f, col, floor = fig(name)
        pl = places[name]
        pl['y'] = floor_y - floor * pl['scale'] + pl.get('z', 0) * 0.2
        chars.append((f, pl))
        # materials of different people share names (skin, hair, shoe): give each person its own
        cols.update({f'{name}.{k}': c for k, c in col.items()})
        f.mat_prefix = name
    out = render_people(chars, v, (0, 0, w, h), cols)
    d.add(out)
    return d


def render_people(chars, v, box, cols):
    """scene.render with each person's materials renamed person.material so colours don't collide."""
    import r3 as _r3

    class Renamed:
        def __init__(self, f):
            self.f = f

        def parts(self, res):
            out = []
            for p in self.f.parts(res):
                p.material = f'{self.f.mat_prefix}.{p.material}'
                out.append(p)
            return out

        def get_marks(self, expr, view):
            ms = self.f.get_marks(expr, view)
            for m in ms:
                if m.on is not None:
                    m.on = f'{self.f.mat_prefix}.{m.on}'
            return ms
    items, _ = scene.render([(Renamed(f), pl) for f, pl in chars], v, box, cols, lw=1.8, clip_prefix='k')
    return items


# ------------------------------------------------------------------------------------------------ rules pictures
def rule_method(w=1260, h=520):
    """How a picture is made here: flat colour regions, then one even line where a form is in front of
    another, then the few marks of the face."""
    d = lc.Doc(w, h, PAPER)
    cw = w / 3
    labels = ['1. плоские пятна цвета', '2. одна ровная линия по краю', '3. глаза, брови, рот, пряди']
    for i in range(3):
        f, col, floor = fig('anya', True, head_rot=(0, 0, 0))
        x0 = i * cw
        panel(d, x0 + 12, 12, cw - 24, h - 60, PANEL['anya'])
        g0, g1 = clip_panel(d, f'rc{i}', x0 + 12, 12, cw - 24, h - 60)
        s = 1.05
        v = r3.View(yaw=-30, s=s, cx=x0 + cw / 2, cy=50 + 118 * s)
        parts = f.parts(s * v.ss)
        R = r3.Render(parts, v, (x0, 0, x0 + cw, h - 48))
        items = R.fills(col)
        if i >= 1:
            items += R.lines(2.2)
        if i >= 2:
            from head import draw_marks
            ms = f.get_marks(F.EXPR['calm'], scene.Yaw(v.yaw_deg))
            for mat in sorted(set(m.on for m in ms), key=str):
                mm = [m for m in ms if m.on == mat]
                if mat in R.mats:
                    cid = f'r{i}-{mat}'
                    items.append(f'<defs>{R.clip_path([mat], cid)}</defs><g clip-path="url(#{cid})">'
                                 + ''.join(draw_marks(mm, R, 2.2)) + '</g>')
                else:
                    items += draw_marks(mm, R, 2.2)
        d.add(g0, items, g1)
        panel(d, x0 + 12, 12, cw - 24, h - 60, 'none')
        d.add(lc.text(x0 + cw / 2, h - 20, labels[i], 18))
    return d


def rule_faces(w=1260, h=430):
    """The four faces side by side, front view: how one set of rules makes four different people."""
    d = lc.Doc(w, h, PAPER)
    cw = w / 4
    for i, name in enumerate(NAMES):
        hd, col = getattr(cast, name)()
        x0 = i * cw
        panel(d, x0 + 10, 10, cw - 20, h - 56, PANEL[name])
        g0, g1 = clip_panel(d, f'fc{i}', x0 + 10, 10, cw - 20, h - 56)
        s = 1.2
        v = r3.View(yaw=-8, s=s, cx=x0 + cw / 2, cy=70 + 120 * s)
        items, _ = scene.render([(hd, dict(expr=F.EXPR['calm']))], v, (x0, 0, x0 + cw, h - 46), col, lw=2.3,
                                clip_prefix=f'fc{i}')
        d.add(g0, items, g1)
        panel(d, x0 + 10, 10, cw - 20, h - 56, 'none')
        d.add(lc.text(x0 + cw / 2, h - 18, RU[name], 18))
    return d


def rule_hands(w=1000, h=300):
    d = lc.Doc(w, h, PAPER)
    panel(d, 10, 10, w - 20, h - 20, '#ece3cf')
    for i, k in enumerate(['hang', 'grip', 'fist', 'open']):
        x = 140 + i * 240
        shapes = Hd.HANDS[k](cast.SKIN)
        for pts, fill, wd, closed in shapes:
            P = lc.xf(pts, x, 50, 2.0)
            d.add(lc.shape(P, fill, 2.4 * wd) if closed else lc.line(P, 2.4 * wd))
        d.add(lc.text(x, h - 30, {'hang': 'висит', 'grip': 'держит', 'fist': 'кулак', 'open': 'ладонь'}[k], 18))
    return d


def main():
    jobs = []
    for n in NAMES:
        jobs.append((f'portrait-{n}', lambda n=n: portrait(n)))
        jobs.append((f'figure-{n}', lambda n=n: figure(n)))
    for n in ('anya', 'savely'):
        jobs.append((f'turn-{n}', lambda n=n: turnaround(n)))
    for n in ('anya', 'tim'):
        jobs.append((f'expr-{n}', lambda n=n: expressions(n)))
    jobs.append(('cast', cast_picture))
    jobs.append(('rule-method', rule_method))
    jobs.append(('rule-faces', rule_faces))
    jobs.append(('rule-hands', rule_hands))
    for name, fn in jobs:
        if want(name):
            save(fn(), name)


if __name__ == '__main__':
    main()
