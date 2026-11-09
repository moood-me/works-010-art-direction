"""Марат and Кира for S6: full figures, turnarounds, expressions by pose, all six together, the six in black.
Uses the same worlds, light and finish as scenes.py.  python3 scenes_more.py [full turn expr together lineup]"""
import random, sys
from draw import figure_svg, glow_svg, finish
from scenes import (save, sky, hills, fogband, ground, contact, fig, turnaround, INK, DUSK, SNOW)

# two more lights of the same world
HEARTH = dict(top='#1c1513', hor='#7c4c37', fog='#a36a4c', ground='#231815', rim='#ffc89c', warm='#ff9c58')
PLUM = dict(top='#15111d', hor='#49395c', fog='#5f4d74', ground='#19141f', rim='#b8a9d8', warm='#d2ee3c')
HEARTH_DAY = dict(top='#2a1d1a', hor='#8f5f48', fog='#bb8c6e', ground='#d8c3ae', rim='#ffe2c6', warm='#ff9c58')


def fig2(name, yaw, k, x, y, P, light=1, pose=None, opts=None, foot=24):
    """As scenes.fig, but the shadow lies under the feet only — for a figure with an arm flung wide."""
    s, b, _ = figure_svg(name, yaw=yaw, pose=pose, k=k, x=x, y=y, ink=INK, rim=P['rim'], rim_w=max(1.2, k * .55), light=light, opts=opts)
    return contact(x, y, foot * k) + s, b


def full_more():
    W, H = 640, 860
    setups = {'marat': (HEARTH, 40, -1, 'house'), 'kira': (PLUM, 55, -1, 'lamp')}
    for name, (P, yaw, light, extra) in setups.items():
        hor = H * .66
        b = sky(W, H, hor, P, stars=26, seed=len(name) + 3)
        b += hills(W, hor, P['fog'], 60, 3 + len(name), .55, step=90)
        b += fogband(W, hor - 20, 120, P['fog'], .5)
        if extra == 'house':
            # his kitchen far away: a lit door, smoke from the chimney — the warm point of this world
            x0, y0 = W * .13, hor + 8
            b += glow_svg(x0 + 30, y0 - 20, 190, P['warm'], .9)
            b += '<path d="M%.1f %.1f v-34 l34 -24 l34 24 v34 Z M%.1f %.1f v-22 h9 v29 Z" fill="%s"/>' % (x0, y0, x0 + 46, y0 - 48, INK)
            b += '<rect x="%.1f" y="%.1f" width="11" height="22" fill="%s"/>' % (x0 + 28, y0 - 22, '#ffb873')
            b += '<rect x="%.1f" y="%.1f" width="8" height="8" fill="%s"/>' % (x0 + 9, y0 - 26, '#ffb873')
            b += ('<path d="M%.1f %.1f c-10 -22 12 -34 2 -58 c-9 -22 10 -36 4 -62" fill="none" stroke="%s" stroke-width="5" '
                  'stroke-linecap="round" opacity=".28"/>') % (x0 + 51, y0 - 74, '#e9c6a8')
        if extra == 'lamp':
            # the light she has turned her back on: a far street lamp and the blocks of the town
            rnd = random.Random(8)
            for bx, bw, bh in ((.04, 46, 92), (.13, 34, 64), (.2, 52, 120), (.30, 30, 54)):
                b += '<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="%s" opacity=".8"/>' % (W * bx, hor + 10 - bh, bw, bh, '#2a2238')
                for _ in range(bh // 14):
                    b += '<rect x="%.1f" y="%.1f" width="3" height="3" fill="#f2c88e" opacity="%.2f"/>' % (
                        W * bx + rnd.uniform(5, bw - 8), hor + 4 - rnd.uniform(8, bh - 6), rnd.uniform(.45, .9))
            b += glow_svg(W * .17, hor - 40, 230, '#8f7fb4', .7)
        b += hills(W, hor + 12, P['ground'], 26, 7, .85, step=120)
        b += ground(W, H, hor + 10, P)
        b += fogband(W, hor + 14, 40, P['fog'], .35)
        s, bb = fig2(name, yaw, 3.55, W * (.44 if name == 'marat' else .52), H * .9, P, light=light, foot=30 if name == 'marat' else 20)
        b += s
        b += finish(W, H)
        save('full-' + name, W, H, b)


# ------------------------------------------------------------ expressions by pose

EXPR_MARAT = {
    'радость': dict(pose=dict(lean=-13, hunch=-5, neck=-6, nod=-22, armL=(8, 112, 10, 34), armR=(8, 116, 10, 30),
                              legL=(10, 13, 6, 0), legR=(-8, 13, 2, 0), footL=(0, 22), footR=(0, 18)), opts={}, yaw=24),
    'удивление': dict(pose=dict(lean=-11, hunch=-3, neck=-10, nod=-2, shrug=3, armL=(42, 26, 104, 0), armR=(46, 26, 108, 0),
                                legL=(-12, 8, 3, 0), legR=(12, 8, 6, 0)), opts=dict(ladle=False), yaw=58),
    'грусть': dict(pose=dict(lean=7, hunch=27, neck=16, nod=26, slump=4, shrug=-2, armL=(5, 5, 2, 0), armR=(6, 6, 4, 0),
                             legL=(2, 5, 3, 0), legR=(-2, 5, 3, 0), footL=(0, 6), footR=(0, 8)), opts=dict(hot=False), yaw=60),
    'злость': dict(pose=dict(lean=13, hunch=8, neck=20, nod=-12, shrug=3.5, armL=(-30, 30, 30, -10), armR=(74, 14, 12, 0),
                             legL=(20, 10, 6, 0), legR=(-18, 10, 0, 0), footL=(0, 12), footR=(0, 14)), opts=dict(hot=False), yaw=50),
}
EXPR_KIRA = {
    # her joy is hers alone: the headphones on, the head back, a sway to the music
    'радость': dict(pose=dict(lean=-8, hunch=2, neck=0, nod=-26, headRoll=-10, roll=7, slump=0, shrug=1,
                              armL=(10, 100, 0, 135), armR=(-12, 34, 46, 24),
                              legL=(4, 4, 2, 0), legR=(26, 10, 56, 0), footL=(0, 8), footR=(30, 4)), opts=dict(pocket=False, phones='on'), yaw=-30),
    'удивление': dict(pose=dict(lean=-14, hunch=4, neck=-8, nod=-8, shrug=4, slump=0, armL=(30, 24, 115, 0), armR=(36, 22, 120, 0),
                                legL=(-16, 4, 6, 0), legR=(12, 4, 2, 0), footL=(0, 6), footR=(0, 6)), opts=dict(pocket=False), yaw=58),
    'грусть': dict(pose=dict(lean=18, hunch=34, neck=10, nod=14, slump=5, shrug=2, armL=(80, 8, -110, -10), armR=(80, 8, -110, -10),
                             legL=(104, 3, 150, 0), legR=(100, 3, 146, 0), footL=(0, 2), footR=(0, 2)), opts=dict(pocket=False), yaw=65),
    'злость': dict(pose=dict(lean=-5, hunch=18, neck=22, nod=6, shrug=4, slump=2, armL=(-22, 24, 4, -8), armR=(-18, 26, 4, -8),
                             legL=(48, 4, 12, 0), legR=(-6, 4, 8, 0), footL=(-16, 4), footR=(0, 10)), opts=dict(pocket=False), yaw=62),
}


def expr_sheet(name, table, P, k, xs=None, foot=22):
    """As scenes.expressions, with the place of each figure given (big gestures need room)."""
    n = len(table)
    W, H = 1500, 720
    b = sky(W, H, H * .84, P, stars=0)
    b += ground(W, H, H * .84, P)
    b += fogband(W, H * .84, 80, P['fog'], .35)
    for i, (label, e) in enumerate(table.items()):
        x = W * (i + .5) / n
        b += fig2(name, e['yaw'], k, x + (xs[i] if xs else 0), H * .84, P, light=1, pose=e['pose'], opts=e['opts'], foot=foot)[0]
        b += ('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="Georgia, serif" font-style="italic" '
              'font-size="26" fill="#3a4258">%s</text>') % (x, H * .94, label)
    b += finish(W, H, .3)
    save('expr-' + name, W, H, b)


def turn_more(name, P, k, pose=None, foot=22):
    """As scenes.turnaround, with a pose that keeps the arms inside the figure's own place."""
    W, H = 1500, 760
    b = sky(W, H, H * .86, P, stars=0)
    b += ground(W, H, H * .86, P)
    b += fogband(W, H * .86, 70, P['fog'], .4)
    for i, yw in enumerate([0, 45, 90, 135, 180]):
        b += fig2(name, yw, k, W * (i + .5) / 5, H * .86, P, light=1, pose=pose, foot=foot)[0]
    b += finish(W, H, .35)
    save('turn-' + name, W, H, b)


# ------------------------------------------------------------ all six together

def together_six(name='together-six', W=1600, H=900):
    P = dict(DUSK)
    hor = H * .70
    b = sky(W, H, hor + 60, P, stars=140, seed=9)
    b += glow_svg(W * .5, hor - 40, 900, '#7d86a8', .55)
    b += glow_svg(W * .8, H * .18, 220, '#e9ecf6', .6)
    b += '<circle cx="%.1f" cy="%.1f" r="22" fill="#ece8dc"/>' % (W * .8, H * .18)
    b += hills(W, hor - 30, '#4c5577', 50, 21, .7, step=140)
    b += fogband(W, hor - 20, 120, P['fog'], .45)
    b += hills(W, hor, '#2a3149', 30, 22, 1, step=160)
    rnd = random.Random(3)
    for _ in range(26):
        x = rnd.uniform(W * .05, W * .4) if rnd.random() < .6 else rnd.uniform(W * .7, W * .95)
        b += '<rect x="%.1f" y="%.1f" width="2.4" height="2.4" fill="#ffc47a" opacity="%.2f"/>' % (x, hor + rnd.uniform(-8, 10), rnd.uniform(.5, 1))
    b += fogband(W, hor + 10, 60, P['fog'], .35)
    gy = H * .86
    b += ground(W, H, gy, dict(ground='#161a26'), curve=26)
    k = 1.85
    surf = lambda fx: gy + 26 * (2 * fx - 1) ** 2 + 2
    put = lambda *a, **kw: fig(*a, **kw)[0]
    # Кира apart, her back to the others
    b += put('kira', -108, k, W * .15, surf(.15), P, light=1)
    b += put('anya', 62, k, W * .31, surf(.31), P, light=1, pose=dict(nod=-14))
    b += put('savely', 74, k, W * .43, surf(.43), P, light=1)
    b += put('tim', -78, k, W * .515, surf(.515), P, light=-1,
             pose=dict(lean=12, hunch=2, neck=6, nod=-30, headRoll=0, legL=(4, 2, 4, 0), legR=(-10, 2, 6, 0), footR=(18, 4)),
             opts=dict(scarf_wind=.5))
    # Марат laughs and holds the ladle out to Вера: taste it
    b += fig2('marat', 52, k, W * .665, surf(.665), P, light=1, foot=32)[0]
    b += put('vera', -58, k, W * .845, surf(.845), P, light=-1, pose=dict(nod=14))
    b += finish(W, H, .6)
    save(name, W, H, b)


def lineup_six(W=1700, H=640):
    """The check by blackness for all six: no light, no colour, no face — by height, low to high."""
    from cast import NAMES
    k = 2.9
    gy = H - 70
    b = '<rect width="%d" height="%d" fill="#dcd7cf"/>' % (W, H)
    for i in range(8):
        y = gy - i * 23 * k
        b += '<line x1="40" x2="%d" y1="%.1f" y2="%.1f" stroke="#b9b2a6" stroke-width="1"/>' % (W - 40, y, y)
    xs = [.07, .21, .355, .50, .64, .81]
    for x, n, yw in zip(xs, ['tim', 'savely', 'kira', 'anya', 'vera', 'marat'], [70, 74, 62, 62, 60, 40]):
        s, bb, _ = figure_svg(n, yaw=yw, k=k, x=W * x, y=gy, ink='#16171b', rim=None, accents=False)
        b += s
        b += ('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="Georgia, serif" font-style="italic" '
              'font-size="24" fill="#4a453e">%s</text>') % (W * x, gy + 44, NAMES[n])
    save('lineup-six', W, H, b)


if __name__ == '__main__':
    what = sys.argv[1:] or ['full', 'turn', 'expr', 'together', 'lineup']
    if 'full' in what:
        full_more()
    if 'turn' in what:
        turn_more('marat', HEARTH, 2.5, pose=dict(armR=(16, 24, 30, 146)), foot=30); turnaround('kira', PLUM)
    if 'expr' in what:
        expr_sheet('marat', EXPR_MARAT, HEARTH_DAY, 2.5, xs=[40, -30, -30, -150], foot=30); expr_sheet('kira', EXPR_KIRA, SNOW, 3.0, xs=[0, 0, 0, -30], foot=20)
    if 'together' in what:
        together_six()
    if 'lineup' in what:
        lineup_six()
