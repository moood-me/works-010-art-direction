"""Sheets of С16: the pictures of the page, each composed on one pixel grid and enlarged by a whole factor."""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'chars'))
import px
import pal
import portrait as P
import sprite

FOUR = ['anya', 'savely', 'tim', 'vera']
SIX = FOUR + ['marat', 'kira']
EXPRS = ['joy', 'surprise', 'sadness', 'anger']


def char(name):
    return importlib.import_module(name)


def spr(name, view='front', flip=False):
    m = char(name)
    return sprite.make(m.VIEWS[view], m.LEG, flip)


def stand(c, s, x, base, shadow='d1'):
    """Put a sprite with its feet on row `base`, a two-row shadow under them."""
    w = s.w
    c.hline(x + 2, x + w - 3, base, shadow); c.hline(x + 4, x + w - 5, base + 1, shadow)
    c.paste(s, x, base - s.h + 2)


def backdrop(w, h, floor):
    c = px.Canvas(w, h)
    c.rect(0, 0, w, h, 'd1')
    c.rect(0, floor, w, h - floor, 'd2')
    P.checker(c, 0, floor - 3, w, 3, 'd2')
    c.hline(0, w - 1, floor, 'd3')
    return c


def portrait_pic(name):
    return P.framed(char(name).portrait()), 9


def figure_pic(name):
    c = backdrop(58, 70, 58)
    s = spr(name)
    stand(c, s, (58 - s.w) // 2, 62)
    return c, 8


def turn_pic(name):
    ss = [spr(name, v) for v in ('front', 'q', 'side')]
    h = max(s.h for s in ss) + 16
    c = backdrop(96, h, h - 12)
    for i, s in enumerate(ss):
        stand(c, s, 16 + i * 32 - s.w // 2, h - 8)
    return c, 8


def expr_pic(name):
    fs = [P.framed(char(name).portrait(e)) for e in EXPRS]
    c = px.Canvas(len(fs) * (fs[0].w + 2) + 2, fs[0].h + 4)
    c.rect(0, 0, c.w, c.h, 'd0')
    for i, f in enumerate(fs):
        c.paste(f, 2 + i * (f.w + 2), 2)
    return c, 5


# ------------------------------------------------------------------ the street at dusk, for the group pictures
GLYPH = {'Ч': ["#..#", "#..#", "#..#", ".###", "...#", "...#", "...#"],
         'А': [".##.", "#..#", "#..#", "####", "#..#", "#..#", "#..#"],
         'С': [".###", "#...", "#...", "#...", "#...", "#...", ".###"],
         'Ы': ["#...#", "#...#", "#...#", "##..#", "#.#.#", "#.#.#", "##..#"]}


def text(c, x, y, s, key):
    for ch in s:
        g = GLYPH[ch]
        for j, r in enumerate(g):
            for i, q in enumerate(r):
                if q == '#':
                    c.px(x + i, y + j, key)
        x += len(g[0]) + 1


def street(w, h, floor):
    c = px.Canvas(w, h)
    bands = [('k0', 0), ('k1', int(floor * .22)), ('k2', int(floor * .48)), ('k3', int(floor * .70)), ('k4', int(floor * .86))]
    for i, (k, y0) in enumerate(bands):
        c.rect(0, y0, w, floor - y0, k)
        if i:
            P.checker(c, 0, y0 - 2, w, 2, k)               # the only gradient: two rows of dither between the bands
    for i, (x, y) in enumerate([(9, 5), (31, 12), (58, 4), (77, 9), (103, 6), (139, 11), (160, 3), (188, 8), (121, 15)]):
        if x < w:
            c.px(x, y, 'h2' if i % 3 else 'h1')
    # far roofs
    x = 0
    hs = [14, 22, 17, 26, 12, 20, 16, 24, 13, 19, 23, 15]
    i = 0
    while x < w:
        bw = 13 + (i * 5) % 9
        top = floor - hs[i % len(hs)]
        c.rect(x, top, bw, hs[i % len(hs)], 'd1')
        c.hline(x, x + bw - 1, top, 'd2')
        for wy in range(top + 4, floor - 4, 6):
            for wx in range(x + 3, x + bw - 3, 5):
                if (wx * 7 + wy * 3 + i) % 4 == 0:
                    c.rect(wx, wy, 1, 2, 'k3')
        x += bw; i += 1
    # the watchmaker's shop
    sx, sw, top = 14, 62, floor - 46
    c.rect(sx, top, sw, 46, 'd2'); c.rect(sx, top, sw, 2, 'd3'); c.vline(sx + sw - 1, top, floor, 'd1'); c.vline(sx + sw - 2, top + 2, floor, 'd1')
    c.rect(sx + 5, top + 5, 30, 11, 'b1'); c.rect(sx + 6, top + 6, 28, 9, 'b2'); c.hline(sx + 6, sx + 33, top + 6, 'b3')
    text(c, sx + 10, top + 7, 'ЧАСЫ', 'h1')
    c.rect(sx + 5, top + 20, 30, 20, 'b1'); c.rect(sx + 6, top + 21, 28, 18, 'h0'); c.rect(sx + 6, top + 21, 28, 5, 'h1')   # the lit window
    c.vline(sx + 20, top + 21, top + 38, 'b1')
    for cx, cy in ((sx + 12, top + 31), (sx + 27, top + 30)):                                     # clocks in it
        c.spans(cy - 3, [(cx - 1, cx + 1), (cx - 3, cx + 3), (cx - 3, cx + 3), (cx - 4, cx + 4), (cx - 3, cx + 3), (cx - 3, cx + 3), (cx - 1, cx + 1)], 'b2')
        c.spans(cy - 2, [(cx - 2, cx + 2), (cx - 2, cx + 2), (cx - 2, cx + 2), (cx - 2, cx + 2), (cx - 2, cx + 2)], 'h2')
        c.vline(cx, cy - 2, cy, 'b0'); c.hline(cx, cx + 1, cy, 'b0')
    c.rect(sx + 41, top + 18, 15, 28, 'b1'); c.rect(sx + 42, top + 19, 13, 27, 'g1'); c.rect(sx + 44, top + 22, 9, 9, 'h0')    # the door
    c.rect(sx + 44, top + 22, 9, 3, 'h1'); c.px(sx + 53, top + 34, 't3'); c.vline(sx + 48, top + 22, top + 30, 'b1')
    # a street lamp and its light
    lx = sx + sw + 34 if w > 150 else w - 26
    c.rect(lx, floor - 44, 2, 44, 'n1'); c.vline(lx, floor - 44, floor - 1, 'n2'); c.rect(lx - 1, floor - 2, 4, 2, 'n1')
    c.spans(floor - 52, [(lx - 1, lx + 2), (lx - 3, lx + 4), (lx - 2, lx + 3), (lx - 2, lx + 3), (lx - 2, lx + 3), (lx - 2, lx + 3), (lx - 3, lx + 4), (lx, lx + 1)], 'n1')
    c.rect(lx - 1, floor - 50, 4, 4, 'h1'); c.rect(lx, floor - 49, 2, 2, 'h2')
    for r, step in ((7, 2),):                      # the glow: sparse dither round the lamp
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                X, Y = lx + x, floor - 48 + y
                if r * r - 2 * r < x * x + y * y <= r * r and (x + y) % step == 0 and (c.get(X, Y) or 'k')[0] in 'kd' and Y < floor:
                    c.px(X, Y, 'h0')
    # the pavement: stone setts
    c.rect(0, floor, w, h - floor, 'd2'); c.hline(0, w - 1, floor, 'd3')
    for y in range(floor + 1, h):
        row = (y - floor) // 5
        if (y - floor) % 5 == 0:
            c.hline(0, w - 1, y, 'd1')
        else:
            for x in range((row * 6) % 12, w, 12):
                c.px(x, y, 'd1')
    for i in range(40):                                    # a few lighter stones
        x, y = (i * 37) % w, floor + 1 + (i * 11) % max(1, h - floor - 1)
        if c.get(x, y) == 'd2' and c.get(x + 1, y) == 'd2':
            c.hline(x, x + 1, y, 'd3')
    return c


def group_pic(names, w, h, scale, xs=None):
    floor = h - 16
    c = street(w, h, floor)
    ss = [spr(n) for n in names]
    gap = (w - sum(s.w for s in ss)) // (len(ss) + 1)
    x = gap
    for i, s in enumerate(ss):
        stand(c, s, xs[i] if xs else x, floor + 6)
        x += s.w + gap
    return c, scale


# ------------------------------------------------------------------ small pictures for the rules
def rule_palette():
    order = 'smatwvbpegrucoln'
    c = px.Canvas(5 * 7 + 3, len(order) * 5 + 3)
    c.rect(0, 0, c.w, c.h, 'x0')
    for j, r in enumerate(order):
        for i in range(5):
            c.rect(2 + i * 7, 2 + j * 5, 6, 4, r + str(i))
    return c, 12


def rule_outline():
    """One sprite three ways: no outline, a black outline, the coloured selective outline of the style."""
    m = char('tim')
    c = backdrop(96, 46, 36)
    for i in range(3):
        leg = dict(sprite.BASE); leg.update(m.LEG)
        s = px.from_ascii([r.ljust(22, '.') for r in m.FRONT], leg)
        if i == 1:
            s.outline(key='x0')
        elif i == 2:
            s.outline()
        c.paste(s, 5 + i * 31, 40 - s.h)
    return c, 8


def rule_scales():
    """The two scales on one pixel grid: the sprite's face of a dozen pixels and the portrait."""
    c = px.Canvas(100, 66)
    c.rect(0, 0, c.w, c.h, 'd1')
    f = P.framed(char('anya').portrait())
    c.paste(f, 34, 2)
    s = spr('anya'); c.paste(s, 5, 62 - s.h)
    c.hline(2, 28, 62, 'd3')
    return c, 8


def rule_face():
    """Faces of the sprites, enlarged: how few pixels carry a character."""
    heads = [(n, spr(n)) for n in SIX]
    c = px.Canvas(6 * 24 + 2, 22)
    c.rect(0, 0, c.w, c.h, 'd2')
    for i, (n, s) in enumerate(heads):
        top = {'marat': 9}.get(n, 0)
        x0 = {'marat': 8, 'tim': 4}.get(n, 2)
        for y in range(18):
            for x in range(21):
                k = s.get(x0 + x, top + y)
                if k:
                    c.px(2 + i * 24 + x, 2 + y, k)
    return c, 10


PICS = {}
for n in SIX:
    PICS['portrait-' + n] = (portrait_pic, n)
    PICS['figure-' + n] = (figure_pic, n)
for n in ('tim', 'savely', 'kira'):
    PICS['turn-' + n] = (turn_pic, n)
for n in ('anya', 'tim', 'savely', 'marat'):
    PICS['expr-' + n] = (expr_pic, n)
PICS['cast'] = (lambda: group_pic(['vera', 'savely', 'anya', 'tim'], 168, 96, 8, [80, 102, 123, 144]),)
PICS['six'] = (lambda: group_pic(['kira', 'vera', 'savely', 'anya', 'tim', 'marat'], 224, 100, 6, [80, 101, 121, 143, 164, 183]),)
PICS['rule-palette'] = (rule_palette,)
PICS['rule-outline'] = (rule_outline,)
PICS['rule-scales'] = (rule_scales,)
PICS['rule-face'] = (rule_face,)
