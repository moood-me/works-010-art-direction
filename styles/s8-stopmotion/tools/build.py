"""Build every picture of the page: svg/*.svg and pics/*.png.
    python3 tools/build.py            # everything (headless google-chrome)
    python3 tools/build.py portrait   # only names containing "portrait"
"""
import os, sys, gzip, math
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sculpt import Doc, studio, finish, render, puppet, keylight, shadow_on_floor
from puppet import draw_head
from body import bust
from figure import figure
import cast, marat, kira

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG, PNG = os.path.join(HERE, 'svg'), os.path.join(HERE, 'pics')
os.makedirs(SVG, exist_ok=True)
os.makedirs(PNG, exist_ok=True)
FILTER = sys.argv[1] if len(sys.argv) > 1 else ''

FOUR = ['anya', 'savely', 'tim', 'vera']
NAMES = FOUR + ['marat', 'kira']
HOME = {'marat': marat, 'kira': kira}          # a character's module; the four live in cast.py
CH = {n: tuple(getattr(HOME.get(n, cast), n.upper() + part) for part in ('', '_BODY', '_FIG')) for n in NAMES}
EXPR = {**cast.EXPR, **marat.EXPR, **kira.EXPR}
# each one's set: backdrop, warm glow, bokeh seed; portrait expression and turn
LOOK = {
    'anya':   dict(top='#2a2026', floor='#3a2c26', glow='#d8945a', seed=3, expr='dream', yaw=24),
    'savely': dict(top='#2a1e18', floor='#3a2a1e', glow='#e0a050', seed=5, expr='grumpy', yaw=-24),
    'tim':    dict(top='#1e2430', floor='#2e2a2a', glow='#d89a60', seed=8, expr='grin', yaw=28),
    'vera':   dict(top='#1e1c26', floor='#2a2628', glow='#c08870', seed=11, expr='tired', yaw=-20),
    'marat':  dict(top='#2a1c16', floor='#3c2a1e', glow='#e8a458', seed=14, expr='beam', rest='beam', yaw=16, roll=-4,
                   fig=dict(expr='laugh', yaw=10, roll=-7, head_dx=-0.02, x=318)),
    'kira':   dict(top='#1c1a24', floor='#28242a', glow='#9a86a8', seed=17, expr='sulk', rest='sulk', yaw=-22, roll=-6,
                   fig=dict(yaw=22, roll=8, head_dx=0.07, head_dy=0.07)),
}
# full figures: head size (px) and where the feet are (head units below the head centre)
FIG = {'anya': (175, 3.95), 'savely': (200, 3.38), 'tim': (215, 2.86), 'vera': (160, 4.45), 'marat': (172, 3.82),
       'kira': (172, 3.95)}


def save(d, name):
    if FILTER and FILTER not in name:
        return
    finish(d)
    p = os.path.join(SVG, name + '.svg')
    d.save(p)
    png = os.path.join(PNG, name + '.png')
    render(p, png, d.w, d.h)
    # keep the folder small: pictures as JPEG, drawings gzipped (.svgz opens in a browser as is)
    Image.open(png).convert('RGB').save(os.path.join(PNG, name + '.jpg'), quality=88)
    os.remove(png)
    with open(p, 'rb') as fi, gzip.open(p + 'z', 'wb') as fo:
        fo.write(fi.read())
    os.remove(p)
    print(name, round(os.path.getsize(p + 'z') / 1024), 'KB')


def want(name):
    return not FILTER or FILTER in name


def set_for(d, n, horizon=1.2, gx=0.3, gy=0.3):
    L = LOOK[n]
    studio(d, top=L['top'], floor=L['floor'], glow=L['glow'], gx=gx, gy=gy, horizon=horizon, bokeh='auto', seed=L['seed'])


def portrait(n):
    P, B, F = CH[n]
    L = LOOK[n]
    d = Doc(700, 820)
    set_for(d, n)
    out, h, T = bust(d, P, B, EXPR[L['expr']], 330, 350, 335, L['yaw'], L.get('roll', 0))
    d.add(puppet(d, ''.join(out), 330))
    keylight(d, 160, 180, 950)
    return d


def full(n, yaw=None):
    P, B, F = CH[n]
    L = LOOK[n]
    S, feet = FIG[n]
    d = Doc(560, 960)
    set_for(d, n, horizon=0.82, gy=0.35)
    floor = 900
    cy = floor - feet * S
    pose = dict(L.get('fig', {}))          # a pose of its own for the full figure: expression, turn, lean of the head
    x = pose.pop('x', 280)
    e = EXPR[pose.pop('expr', L['expr'])]
    turn = pose.pop('yaw', L['yaw'] * 0.8)
    d.add(shadow_on_floor(d, x + S * 0.15, floor, S * 0.75, S * 0.12))
    out, T = figure(d, P, B, F, e, S, x, cy, turn if yaw is None else yaw, **pose)
    d.add(puppet(d, ''.join(out), S))
    keylight(d, 120, 200, 1100)
    return d


def turnaround(n):
    P, B, F = CH[n]
    d = Doc(1500, 620)
    set_for(d, n, gx=0.5)
    for i, yaw in enumerate((0, 40, 88)):
        out, h, T = bust(d, P, B, EXPR[LOOK[n].get('rest', 'calm')], 255, 250 + 500 * i, 255, yaw, body_yaw=yaw * 0.8)
        d.add(puppet(d, ''.join(out), 255))
    keylight(d, 300, 150, 1600, amount=0.4)
    return d


def expressions(n):
    P, B, F = CH[n]
    d = Doc(1600, 540)
    set_for(d, n, gx=0.5)
    for i, (e, roll) in enumerate((('joy', -5), ('surprise', 0), ('sad', 6), ('anger', -3))):
        r = draw_head(d, P, P.get('faces', {}).get(e, EXPR[e]), 290, 200 + 400 * i, 280, math.copysign(18, LOOK[n]['yaw']), roll)
        d.add(puppet(d, ''.join(r['back'] + r['head']), 290))
    keylight(d, 300, 100, 1700, amount=0.35)
    return d


def together():
    """All four on one small set: Savely shows the watch, Tim reaches up to see, Anya smiles, Vera looks on."""
    d = Doc(1800, 1000)
    studio(d, top='#241c1c', floor='#3a2c22', glow='#e0a050', gx=0.45, gy=0.35, horizon=0.8, bokeh='auto', seed=21)
    floor = 940
    place = [('vera', 1400, -30, dict(cast.EXPR['tired'], at_camera=False, gaze=(-0.15, 0.12)), 150),
             ('anya', 400, 30, dict(cast.EXPR['dream'], at_camera=False, gaze=(0.25, 0.05)), 165),
             ('savely', 820, 15, dict(cast.EXPR['grumpy'], at_camera=False, gaze=(0.2, 0.25)), 190),
             ('tim', 1110, -32, dict(cast.EXPR['joy'], at_camera=False, gaze=(-0.25, 0.15)), 200)]
    for n, x, yaw, e, S in place:
        P, B, F = CH[n]
        feet = FIG[n][1]
        cy = floor - feet * S
        d.add(shadow_on_floor(d, x + S * 0.15, floor, S * 0.75, S * 0.12))
        out, T = figure(d, P, B, F, e, S, x, cy, yaw)
        d.add(puppet(d, ''.join(out), S))
    keylight(d, 700, 250, 1500)
    return d


def six():
    """The whole cast on one set: the four round the watch as before, Marat laughing over them with his ladle,
    Vera eyeing the noise, Kira apart at the edge, glancing back from under her fringe."""
    d = Doc(2360, 1000)
    studio(d, top='#241c1c', floor='#3a2c22', glow='#e0a050', gx=0.5, gy=0.35, horizon=0.8, bokeh='auto', seed=33)
    floor = 940
    away = dict(at_camera=False)
    place = [('vera', 2090, -30, dict(EXPR['tired'], gaze=(-0.3, 0.02), **away), 154, {}),
             ('kira', 250, -20, dict(EXPR['sulk'], gaze=(0.55, -0.08), **away), 166, dict(roll=-6, head_dx=0.06, head_dy=0.07)),
             ('anya', 560, 30, dict(EXPR['dream'], gaze=(0.25, 0.05), **away), 165, {}),
             ('savely', 930, 15, dict(EXPR['grumpy'], gaze=(0.2, 0.25), **away), 182, {}),
             ('tim', 1200, -32, dict(EXPR['joy'], gaze=(-0.25, 0.15), **away), 200, {}),
             ('marat', 1680, -12, dict(EXPR['laugh'], gaze=(-0.2, 0.12), **away), 185, dict(roll=-7, head_dx=-0.02))]
    for n, x, yaw, e, S, pose in place:
        P, B, F = CH[n]
        cy = floor - FIG[n][1] * S
        d.add(shadow_on_floor(d, x + S * 0.15, floor, S * 0.75, S * 0.12))
        out, T = figure(d, P, B, F, e, S, x, cy, yaw, **pose)
        d.add(puppet(d, ''.join(out), S))
    keylight(d, 1000, 250, 2100)
    return d


def construction():
    """How a head is built: the sculpted form, then the face, then hair and the set light."""
    P = cast.ANYA
    d = Doc(1500, 560)
    studio(d, top='#262024', floor='#302824', glow='#c89060', gx=0.5, horizon=1.2)
    steps = [dict(P, stage='bare', hair=None), dict(P, stage='face', hair=None), dict(P)]
    for i, Pi in enumerate(steps):
        r = draw_head(d, Pi, cast.EXPR['calm'], 330, 250 + 500 * i, 280, 25, 0)
        g = ''.join(r['back'] + r['head'])
        d.add(puppet(d, g, 330) if i == 2 else g)
    return d


if __name__ == '__main__':
    for n in NAMES:
        if want('portrait-' + n):
            save(portrait(n), 'portrait-' + n)
        if want('figure-' + n):
            save(full(n), 'figure-' + n)
    for n in ('anya', 'tim', 'marat', 'kira'):
        if want('turn-' + n):
            save(turnaround(n), 'turn-' + n)
    for n in ('tim', 'anya', 'marat', 'kira'):
        if want('expr-' + n):
            save(expressions(n), 'expr-' + n)
    if want('cast'):
        save(together(), 'cast')
    if want('six'):
        save(six(), 'six')
    if want('rule-construction'):
        save(construction(), 'rule-construction')
