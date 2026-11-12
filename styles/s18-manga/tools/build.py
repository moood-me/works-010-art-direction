"""Every picture -> ../svg, then render.js -> ../pics.      python3 build.py [part of a name ...]"""
import os, sys, subprocess, math, random, gzip
from pen import *
from head import View, EXPR
from chars import CAST, NAMES, ORDER4, ORDER6

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, '..', 'svg')            # kept gzipped (.svgz): the drawings are text and big
PICS_DIR = os.path.join(HERE, '..', 'pics')
TMP = os.environ.get('TMPDIR_S18', '/home/user/cache/styles-s18-manga/svg')   # plain .svg copies for rendering
PICS = {}
JPG = set()           # pictures saved as jpg (the big ones)
# the head heights of the cast against each other (Тим is a child; Марат the biggest)
HEAD = dict(anya=1.0, sav=0.97, tim=0.9, vera=1.02, marat=1.1, kira=0.97)
# the way each one faces in the single pictures (yaw; negative turns to the left)
YAW = dict(anya=28, sav=30, tim=30, vera=26, marat=24, kira=-28)


def placed(k, yaw, s, px, py, e=None, lw=2.0, neutral=False, at='neck', bust=False):
    """Draw character k so that its neck pit (at='neck') or its feet (at='ground') land on (px, py)."""
    m = CAST[k]
    v = View(yaw=yaw, s=s, x=0, y=0)
    if at == 'neck':
        j = m.skeleton().j
        X, Y = v(j['neck'])
        v.ox, v.oy = px - X, py - Y
    else:
        v.ox, v.oy = px, py
    return m.FIGURE(v, e=e, lw=lw, neutral=neutral, bust=bust)


def frame(W, H, inner, border=True, bg=None):
    out = (bg or '') + inner
    if border:
        out = clip([(8, 8), (W - 8, 8), (W - 8, H - 8), (8, H - 8)], out, smooth=False) + panel(8, 8, W - 16, H - 16, 3)
    return svg(W, H, out)


def sky(W, H, top=0.0, bottom=0.35, x0=0, y0=0, seed=0):
    """A graded tone over the panel: light at the top left, darker to the lower right."""
    return gtone((x0, y0, x0 + W, y0 + H), lambda x, y: top + (bottom - top) * max(0, min(1, ((y - y0) / H) * 0.7 + ((x - x0) / W) * 0.3)) ** 1.4)


def ground_shadow(cx, cy, rx, ry, level=0.35):
    pts = [(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in [k * math.pi / 16 for k in range(32)]]
    return tone(pts, level)


def pic(name, jpg=False):
    def deco(f):
        PICS[name] = f
        if jpg:
            JPG.add(name)
        return f
    return deco


def expr_of(k, name):
    e = dict(EXPR['rest']); e.update(EXPR[name])
    e.update(getattr(CAST[k], 'EXPR_FIX', {}).get(name, {}))
    return e


# ---------------------------------------------------------------- single pictures

def portrait(k):
    W, H = 800, 1000
    S = 360 * HEAD[k] / HEAD[k]
    yaw = YAW[k]
    bg = sky(W, H, 0.0, 0.12)
    inner = placed(k, yaw, S, W * (0.5 - 0.04 * (1 if yaw > 0 else -1)), H * 0.7, lw=2.6, bust=True)
    return frame(W, H, inner, bg=bg)


def fig(k):
    W, H = 700, 1150
    m = CAST[k]
    S = (H - 150) / (m.HEIGHT + 0.6) if k != 'marat' else (H - 120) / 9.6
    yaw = YAW[k]
    gy = H - 70
    bg = sky(W, H, 0.0, 0.1) + ground_shadow(W * 0.5 + 20, gy, 0.85 * S, 0.16 * S, 0.3)
    inner = placed(k, yaw, S, W * 0.5 - (40 if k == 'marat' else 0), gy, lw=1.7, at='ground')
    return frame(W, H, inner, bg=bg)


def turn(k):
    W, H = 1500, 640
    S = 300
    out = ''
    for i, yaw in enumerate((0, 35, 90)):
        x = 250 + i * 500
        part = placed(k, yaw, S, x, 470, lw=2.2, neutral=True, bust=True)
        out += clip([(x - 250, 8), (x + 250, 8), (x + 250, H - 8), (x - 250, H - 8)], part, smooth=False)
    return frame(W, H, sky(W, H, 0.0, 0.08) + out)


def expr(k):
    W, H = 1640, 560
    S = 270
    out = ''
    for i, name in enumerate(('joy', 'surprise', 'sadness', 'anger')):
        x = 205 + i * 410
        part = placed(k, YAW[k] * 0.9, S, x, 430, e=expr_of(k, name), lw=2.0, neutral=True, bust=True)
        out += clip([(x - 205, 8), (x + 205, 8), (x + 205, H - 8), (x - 205, H - 8)], part, smooth=False)
        out += panel(x - 197, 14, 394, H - 28, 2.4) if False else ''
    seps = ''.join(f'<rect x="{205 + i * 410 + 205 - 5}" y="0" width="10" height="{H}" fill="{PAPER}"/>' + panel(205 + i * 410 + 205 - 5 - 1, 8, 0.1, H - 16, 2.4) + panel(205 + i * 410 + 205 + 5, 8, 0.1, H - 16, 2.4) for i in range(3))
    return frame(W, H, sky(W, H, 0.0, 0.08) + out + seps)


for _k in ORDER6:
    PICS['portrait-' + _k] = (lambda k=_k: portrait(k))
    PICS['figure-' + _k] = (lambda k=_k: fig(k))
    PICS['turn-' + _k] = (lambda k=_k: turn(k))
for _k in ('anya', 'tim', 'marat', 'kira'):
    PICS['expr-' + _k] = (lambda k=_k: expr(k))


# ---------------------------------------------------------------- together

def street(W, H, gy, seed=3):
    """A quiet street in thin line, as Taniguchi draws the town behind his walkers: a fence, houses, a pole with
    wires; tone for the sky and the shadows."""
    rnd = random.Random(seed)
    out = ''
    lw = 1.1
    hz = gy - 330
    # houses
    x = 20
    while x < W:
        w = rnd.uniform(220, 380); h = rnd.uniform(150, 260)
        top = hz - h + 140
        body = [(x, top), (x + w, top), (x + w, hz + 140), (x, hz + 140)]
        out += fillpath(body, PAPER, smooth=False) + outline(body, lw * 1.2, 0.3, smooth=False)
        roof = [(x - 14, top + 4), (x + w * 0.5, top - rnd.uniform(40, 70)), (x + w + 14, top + 4)]
        out += fillpath(roof + [(x + w + 14, top + 12), (x - 14, top + 12)], f'url(#{tone_id(0.22)})', smooth=False) + outline(roof + [(x + w + 14, top + 12), (x - 14, top + 12)], lw, 0.3, smooth=False)
        for wx in range(int(x + 30), int(x + w - 60), 90):
            win = [(wx, top + 40), (wx + 50, top + 40), (wx + 50, top + 90), (wx, top + 90)]
            out += fillpath(win, f'url(#{tone_id(0.14)})', smooth=False) + outline(win, lw * 0.7, 0.2, smooth=False)
            out += stroke([(wx + 25, top + 40), (wx + 25, top + 90)], lw * 0.5, smooth=False)
        out += hatch([(x + w - 40, top + 12), (x + w, top + 12), (x + w, hz + 140), (x + w - 40, hz + 140)], (x + w - 40, top, x + w, hz + 140), angle=-60, gap=4, w=0.5, seed=int(x))
        x += w + rnd.uniform(30, 90)
    # a fence in front of them
    fy = hz + 140
    out += fillpath([(0, fy - 70), (W, fy - 70), (W, fy + 10), (0, fy + 10)], PAPER, smooth=False)
    for fx in range(0, W, 26):
        out += stroke([(fx, fy - 70), (fx, fy + 10)], lw * 0.7, smooth=False)
    out += stroke([(0, fy - 70), (W, fy - 70)], lw * 1.1, smooth=False) + stroke([(0, fy - 40), (W, fy - 40)], lw * 0.8, smooth=False)
    # the road
    road = [(0, fy + 10), (W, fy + 10), (W, H), (0, H)]
    out += fillpath(road, PAPER, smooth=False) + stroke([(0, fy + 10), (W, fy + 10)], lw * 1.2, smooth=False)
    out += gtone((0, fy + 10, W, H), lambda x, y: 0.02 + 0.08 * (y - fy) / (H - fy))
    # a utility pole and wires
    px = W * 0.035
    out += fillpath([(px - 9, 0), (px + 9, 0), (px + 11, fy + 30), (px - 11, fy + 30)], PAPER, smooth=False) + outline([(px - 9, 0), (px + 9, 0), (px + 11, fy + 30), (px - 11, fy + 30)], lw * 1.2, 0.5, smooth=False)
    out += tone([(px + 2, 0), (px + 9, 0), (px + 11, fy + 30), (px + 3, fy + 30)], 0.5, smooth=False)
    for k in range(3):
        y0 = 40 + k * 22
        out += stroke([(px - 60, y0), (px + 60, y0)], lw * 1.2, smooth=False)
        out += stroke([(0, y0 + 60 + k * 10), (W * 0.4, y0 + 95 + k * 10), (px - 60, y0)], lw * 0.5)
        out += stroke([(px + 60, y0), (W, y0 + 30 + k * 8)], lw * 0.5)
    return out


def together(keys, W, H, xs, yaws, S, title_seed=1):
    gy = H - 90
    out = street(W, H, gy)
    for k, x, yaw in zip(keys, xs, yaws):
        s = S * HEAD[k]
        out += ground_shadow(x + 30, gy, 0.8 * s * (1.3 if k == 'marat' else 1), 0.15 * s, 0.35)
    order = sorted(range(len(keys)), key=lambda i: 0)
    for i in order:
        k = keys[i]
        out += placed(k, yaws[i], S * HEAD[k], xs[i], gy, lw=1.5, at='ground')
    return frame(W, H, out)


@pic('cast', jpg=True)
def cast4():
    return together(['tim', 'sav', 'anya', 'vera'], 1800, 1000, [300, 690, 1110, 1490], [32, 24, -24, -30], 108)


@pic('cast6', jpg=True)
def cast6():
    return together(['tim', 'sav', 'marat', 'anya', 'vera', 'kira'], 2400, 1050, [260, 610, 1010, 1440, 1830, 2180], [34, 26, 18, -18, -26, -34], 90)


# ---------------------------------------------------------------- run

def main(args):
    os.makedirs(SVG, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    names = [n for n in PICS if not args or any(a in n for a in args)]
    files = {True: [], False: []}
    for n in names:
        TONES.clear()
        s = PICS[n]()
        with gzip.open(os.path.join(SVG, n + '.svgz'), 'wt', compresslevel=9) as f:
            f.write(s)
        p = os.path.join(TMP, n + '.svg')
        open(p, 'w').write(s)
        files[n in JPG].append(p)
        print(n, len(s) // 1024, 'KB')
    for jpg, fs in files.items():
        if fs:
            env = dict(os.environ, OUT=PICS_DIR)
            if jpg:
                env['JPG'] = '1'
            subprocess.run(['node', os.path.join(HERE, 'render.js')] + fs, check=True, env=env)
    # black ink on paper: keep the PNGs grey (a third of the size)
    from PIL import Image
    for n in names:
        p = os.path.join(PICS_DIR, n + '.png')
        if os.path.exists(p) and n not in JPG:
            Image.open(p).convert('L').save(p, optimize=True)


if __name__ == '__main__':
    main(sys.argv[1:])
