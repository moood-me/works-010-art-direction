"""Scenes, sheets and the cast together for S6. Writes ../svg/*.svg; render.sh makes ../pics/*.png."""
import math, os, random, subprocess, sys
from draw import figure_svg, svg_doc, glow_svg, finish

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, '..', 'svg')
PIC = os.path.join(HERE, '..', 'pics')
os.makedirs(SVG, exist_ok=True); os.makedirs(PIC, exist_ok=True)

INK = '#10131b'

# one world, a few lights: palettes name (sky top, sky horizon, fog, ground, rim, warm)
DUSK = dict(top='#121726', hor='#3d4766', fog='#59627f', ground='#1a1f2e', rim='#b9c6e2', warm='#ffc47a')
EMBER = dict(top='#1c1420', hor='#6b4446', fog='#8a5b55', ground='#22171c', rim='#f0b48a', warm='#ffcf86')
DAWN = dict(top='#2b3550', hor='#c7a59a', fog='#d9bfb4', ground='#3a3346', rim='#ffe2c4', warm='#fff0d0')
SNOW = dict(top='#1b2233', hor='#6d7894', fog='#9aa4bd', ground='#c3cad8', rim='#e7ecf6', warm='#ffbf6e')


def save(name, w, h, body):
    p = os.path.join(SVG, name + '.svg')
    open(p, 'w').write(svg_doc(w, h, body, bg=None))
    png = os.path.join(PIC, name + '.png')
    subprocess.run([os.path.join(HERE, 'render.sh'), p, png, str(w), str(h)])
    subprocess.run(['convert', png, '-quality', '88', os.path.join(PIC, name + '.jpg')])
    os.remove(png)


def sky(w, h, hor_y, P, stars=40, seed=1):
    out = ('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/>'
           '<stop offset="1" stop-color="%s"/></linearGradient></defs><rect width="%d" height="%d" fill="url(#sky)"/>') % (
        P['top'], P['hor'], w, int(hor_y) + 2)
    rnd = random.Random(seed)
    for _ in range(stars):
        x, y = rnd.uniform(0, w), rnd.uniform(0, hor_y * .7)
        out += '<circle cx="%.1f" cy="%.1f" r="%.2f" fill="#e8ecf6" opacity="%.2f"/>' % (x, y, rnd.uniform(.4, 1.1), rnd.uniform(.25, .7))
    return out


def hills(w, hor_y, col, amp, seed, op=1.0, base=None, step=60):
    rnd = random.Random(seed)
    pts = []
    x = -20
    while x < w + 80:
        pts.append((x, hor_y - rnd.uniform(0, amp)))
        x += rnd.uniform(step * .6, step * 1.4)
    d = 'M%.1f %.1f ' % (-20, base if base else hor_y + 400)
    d += 'L%.1f %.1f ' % pts[0]
    for i in range(1, len(pts)):
        (x0, y0), (x1, y1) = pts[i - 1], pts[i]
        d += 'Q%.1f %.1f %.1f %.1f ' % (x0 + (x1 - x0) * .5, y0, x1, y1) if i % 2 else 'T%.1f %.1f ' % (x1, y1)
    d += 'L%.1f %.1f Z' % (w + 80, base if base else hor_y + 400)
    return '<path d="%s" fill="%s" opacity="%.2f"/>' % (d, col, op)


def fogband(w, y, hgt, col, op):
    gid = 'fb%d' % int(y * 10 + hgt)
    return ('<defs><linearGradient id="%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="%s" stop-opacity="%.2f"/><stop offset="1" stop-color="%s" stop-opacity="0"/>'
            '</linearGradient></defs><rect x="0" y="%.1f" width="%d" height="%.1f" fill="url(#%s)"/>') % (
        gid, col, col, op, col, y - hgt / 2, w, hgt, gid)


def ground(w, h, y, P, curve=0):
    if curve:
        return '<path d="M-10 %.1f Q%.1f %.1f %.1f %.1f L%.1f %d L-10 %d Z" fill="%s"/>' % (
            y + curve, w / 2, y - curve, w + 10, y + curve, w + 10, h, h, P['ground'])
    return '<rect x="0" y="%.1f" width="%d" height="%.1f" fill="%s"/>' % (y, w, h - y, P['ground'])


def contact(x, y, rx, col='#000', op=.45):
    return '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity="%.2f"/>' % (x, y + 1, rx, rx * .12, col, op)


def fig(name, yaw, k, x, y, P, light=1, pose=None, rim_w=None, plane=None, ink=INK, opts=None, glow=True):
    s, b, _ = figure_svg(name, yaw=yaw, pose=pose, k=k, x=x, y=y, ink=ink, rim=P['rim'], rim_w=rim_w or max(1.2, k * .55),
                         light=light, plane=plane, opts=opts, glow=glow)
    return contact(x, y, (b[2] - b[0]) * .55) + s, b


# ------------------------------------------------------------ full figures, each in its own small world

def full_figures():
    W, H = 640, 860
    setups = {
        # name: (palette, yaw, light side, world extras)
        'anya': (DUSK, 62, 1, 'lake'),
        'savely': (EMBER, 70, 1, 'lamp'),
        'tim': (SNOW, 55, -1, 'snow'),
        'vera': (DAWN, -58, -1, 'window'),
    }
    for name, (P, yaw, light, extra) in setups.items():
        hor = H * .66
        b = sky(W, H, hor, P, stars=50 if P is DUSK else 18, seed=len(name))
        b += hills(W, hor, P['fog'], 60, 3, .55, step=90)
        b += fogband(W, hor - 20, 120, P['fog'], .5)
        b += hills(W, hor + 12, P['ground'], 26, 7, .85, step=120)
        b += ground(W, H, hor + 10, P)
        b += fogband(W, hor + 14, 40, P['fog'], .35)
        k = 3.55
        x, y = W * .5, H * .9
        if extra == 'lamp':
            # a street lamp behind him: the warm light that makes his rim
            b += '<rect x="%.1f" y="%.1f" width="5" height="%.1f" fill="%s"/>' % (W * .82, H * .2, H * .7, INK)
            b += '<path d="M%.1f %.1f h-46 v8 h46Z" fill="%s"/>' % (W * .82 + 5, H * .2, INK)
            b += glow_svg(W * .82 - 36, H * .2 + 14, 260, P['warm'], 1.0)
            b += '<ellipse cx="%.1f" cy="%.1f" rx="12" ry="6" fill="%s"/>' % (W * .82 - 36, H * .2 + 12, P['warm'])
        if extra == 'window':
            b += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".9"/>' % (W * .06, H * .12, W * .26, H * .52, '#f4dcc0')
            b += '<rect x="%.1f" y="%.1f" width="5" height="%.1f" fill="%s"/>' % (W * .19 - 2.5, H * .12, H * .52, INK)
            b += '<rect x="%.1f" y="%.1f" width="%.1f" height="5" fill="%s"/>' % (W * .06, H * .36, W * .26, INK)
            b += glow_svg(W * .19, H * .38, 380, '#ffe7c8', .7)
        if extra == 'lake':
            b += glow_svg(W * .8, H * .2, 160, '#e9ecf6', .7)
            b += '<circle cx="%.1f" cy="%.1f" r="26" fill="#ece8dc"/>' % (W * .8, H * .2)
        if extra == 'snow':
            rnd = random.Random(5)
            for _ in range(120):
                b += '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#eef2fa" opacity="%.2f"/>' % (
                    rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice([.8, 1.1, 1.6, 2.4]), rnd.uniform(.3, .8))
            b += glow_svg(W * .16, hor - 6, 70, P['warm'], 1)
            b += '<rect x="%.1f" y="%.1f" width="7" height="6" fill="%s"/>' % (W * .16 - 3.5, hor - 9, P['warm'])
        s, bb = fig(name, yaw, k, x, y, P, light=light)
        b += s
        b += finish(W, H)
        save('full-' + name, W, H, b)


# ------------------------------------------------------------ turnarounds

def turnaround(name, P, k=3.2):
    yaws = [0, 45, 90, 135, 180]
    W, H = 1500, 760
    b = sky(W, H, H * .86, P, stars=0)
    b += ground(W, H, H * .86, P)
    b += fogband(W, H * .86, 70, P['fog'], .4)
    for i, yw in enumerate(yaws):
        x = W * (i + .5) / len(yaws)
        s, _ = fig(name, yw, k, x, H * .86, P, light=1)
        b += s
    # thin height lines: head units
    b += finish(W, H, .35)
    save('turn-' + name, W, H, b)


# ------------------------------------------------------------ expressions by pose (Тим)

EXPR_TIM = {
    'радость': dict(pose=dict(lean=-6, hunch=-6, neck=-8, nod=-20, headRoll=0, lift=16,
                              armL=(150, 38, 8, 0), armR=(156, 34, 6, 0), legL=(36, 4, 70, 0), legR=(-4, 4, 60, 0),
                              footL=(30, 6), footR=(40, 6)), opts=dict(slingshot=False, scarf_wind=1.4), yaw=30),
    'удивление': dict(pose=dict(lean=-14, hunch=-6, neck=-10, nod=-12, headRoll=0,
                                armL=(36, 22, 112, 4), armR=(40, 20, 118, 4), legL=(-12, 4, 4, 0), legR=(10, 4, 6, 0),
                                footL=(0, 12), footR=(0, 10)), opts=dict(slingshot=False, scarf_wind=.4), yaw=55),
    'грусть': dict(pose=dict(lean=22, hunch=26, neck=14, nod=26, headRoll=0, shrug=-1.5, slump=2,
                             armL=(6, 2, 0, 0), armR=(4, 2, 2, 0), legL=(2, 2, 2, 0), legR=(-2, 2, 2, 0),
                             footL=(0, -8), footR=(0, -10)), opts=dict(slingshot=False, scarf_wind=0), yaw=40),
    'злость': dict(pose=dict(lean=16, hunch=4, neck=22, nod=-28, headRoll=0, shrug=2.6,
                             armL=(-30, 20, -6, 4), armR=(-26, 20, -4, 4), legL=(24, 7, 4, 0), legR=(-14, 7, 0, 0),
                             footL=(0, 10), footR=(0, 14)), opts=dict(slingshot=False, scarf_wind=1.2), yaw=72),
}


def expressions(name='tim', table=EXPR_TIM, P=SNOW, k=4.0):
    n = len(table)
    W, H = 1500, 720
    b = sky(W, H, H * .84, P, stars=0)
    b += ground(W, H, H * .84, P)
    b += fogband(W, H * .84, 80, P['fog'], .35)
    for i, (label, e) in enumerate(table.items()):
        x = W * (i + .5) / n
        s, _ = fig(name, e['yaw'], k, x, H * .84, P, light=1, pose=e['pose'], opts=e['opts'])
        b += s
        b += ('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="Georgia, serif" font-style="italic" '
              'font-size="26" fill="#3a4258">%s</text>') % (x, H * .94, label)
    b += finish(W, H, .3)
    save('expr-' + name, W, H, b)


if __name__ == '__main__':
    what = sys.argv[1:] or ['full', 'turn', 'expr']
    if 'full' in what:
        full_figures()
    if 'turn' in what:
        turnaround('savely', EMBER); turnaround('vera', DAWN)
    if 'expr' in what:
        expressions()


# ------------------------------------------------------------ the four together

def together(name='together', W=1600, H=900):
    P = dict(DUSK)
    hor = H * .70
    b = sky(W, H, hor + 60, P, stars=140, seed=9)
    b += glow_svg(W * .5, hor - 40, 900, '#7d86a8', .55)
    b += glow_svg(W * .78, H * .2, 220, '#e9ecf6', .6)
    b += '<circle cx="%.1f" cy="%.1f" r="22" fill="#ece8dc"/>' % (W * .78, H * .2)
    b += hills(W, hor - 30, '#4c5577', 50, 21, .7, step=140)
    b += fogband(W, hor - 20, 120, P['fog'], .45)
    b += hills(W, hor, '#2a3149', 30, 22, 1, step=160)
    # town lights far away: the warm points in a cold world
    rnd = random.Random(3)
    for _ in range(26):
        x = rnd.uniform(W * .05, W * .4) if rnd.random() < .6 else rnd.uniform(W * .7, W * .95)
        y = hor + rnd.uniform(-8, 10)
        b += '<rect x="%.1f" y="%.1f" width="2.4" height="2.4" fill="#ffc47a" opacity="%.2f"/>' % (x, y, rnd.uniform(.5, 1))
    b += fogband(W, hor + 10, 60, P['fog'], .35)
    # the hill they stand on: the top of a small planet
    gy = H * .86
    b += ground(W, H, gy, dict(ground='#161a26'), curve=26)
    k = 1.85
    surf = lambda fx: gy + 26 * (2 * fx - 1) ** 2   # the hill's top line at a fraction of the width
    s, _ = fig('anya', 62, k, W * .33, surf(.33) + 2, P, light=1, pose=dict(nod=-14))
    b += s
    s, _ = fig('savely', 74, k, W * .47, surf(.47) + 2, P, light=1)
    b += s
    s, _ = fig('tim', -78, k, W * .555, surf(.555) + 2, P, light=-1,
               pose=dict(lean=12, hunch=2, neck=6, nod=-30, headRoll=0, legL=(4, 2, 4, 0), legR=(-10, 2, 6, 0),
                         footR=(18, 4)), opts=dict(scarf_wind=.5))
    b += s
    s, _ = fig('vera', -58, k, W * .67, surf(.67) + 2, P, light=-1, pose=dict(nod=14))
    b += s
    b += finish(W, H, .6)
    save(name, W, H, b)


if __name__ == '__main__' and 'together' in sys.argv:
    together()


def lineup(W=1400, H=640):
    """Rule picture: the four as pure black shapes — they must be told apart with no light, no colour, no face."""
    from cast import NAMES, CAST
    k = 2.9
    gy = H - 70
    b = '<rect width="%d" height="%d" fill="#dcd7cf"/>' % (W, H)
    for i in range(8):
        y = gy - i * 23 * k
        b += '<line x1="40" x2="%d" y1="%.1f" y2="%.1f" stroke="#b9b2a6" stroke-width="1"/>' % (W - 40, y, y)
    names = ['anya', 'savely', 'tim', 'vera']
    yaws = [62, 74, 70, 60]
    for i, (n, yw) in enumerate(zip(names, yaws)):
        x = W * (i + .5) / 4
        s, bb, _ = figure_svg(n, yaw=yw, k=k, x=x, y=gy, ink='#16171b', rim=None, accents=False)
        b += s
        b += ('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="Georgia, serif" font-style="italic" '
              'font-size="24" fill="#4a453e">%s</text>') % (x, gy + 44, NAMES[n])
    save('lineup', W, H, b)


if __name__ == '__main__' and 'lineup' in sys.argv:
    lineup()


def light_steps(W=1200, H=620):
    """Rule picture: one shape → a rim of light from its own edge → one warm accent."""
    P = DUSK
    b = sky(W, H, H * .85, P, stars=30, seed=2) + ground(W, H, H * .85, P)
    k = 2.7
    labels = ['одна форма', '+ кромка света', '+ один тёплый знак']
    for i in range(3):
        x = W * (i + .5) / 3
        s, _, _ = figure_svg('anya', yaw=62, k=k, x=x, y=H * .85, ink=INK, rim=P['rim'] if i else None,
                             rim_w=1.6, accents=(i == 2))
        b += contact(x, H * .85, 40) + s
        b += ('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="Georgia, serif" font-style="italic" '
              'font-size="22" fill="#aab3cc">%s</text>') % (x, H * .95, labels[i])
    b += finish(W, H, .4)
    save('light-steps', W, H, b)


if __name__ == '__main__' and 'steps' in sys.argv:
    light_steps()
