"""Compose and render every picture of С12: svg/ and pics/.

    python3 tools/build.py            # all
    python3 tools/build.py portrait   # only names containing "portrait"
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import Doc, render, ink, wash, catmull
import parts
import anya, savely, tim, vera

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAST = {'anya': anya, 'savely': savely, 'tim': tim, 'vera': vera}
JOBS = {}


def job(fn):
    JOBS[fn.__name__] = fn
    return fn


def out(name, d, scale=1.0):
    svg = os.path.join(ROOT, 'svg', name + '.svg')
    png = os.path.join(ROOT, 'pics', name + '.png')
    d.save(svg)
    render(svg, png, d.w, d.h, scale)
    # watercolour grain makes PNGs heavy: keep a good JPEG instead
    from PIL import Image
    Image.open(png).convert('RGB').save(png[:-4] + '.jpg', quality=88)
    os.remove(png)
    print('made', name)


def portrait(name):
    d = Doc(600, 720, seed=3)
    d.lw = 1.6
    d.fade = (470, 690)
    CAST[name].bust(d)
    out('portrait-' + name, d)


def figure(name):
    d = Doc(600, 1000, seed=5)
    d.lw = 1.15
    CAST[name].figure(d)
    out('figure-' + name, d)


for _n in CAST:
    JOBS['portrait_' + _n] = (lambda n: lambda: portrait(n))(_n)
    JOBS['figure_' + _n] = (lambda n: lambda: figure(n))(_n)


def turnaround(name):
    d = Doc(1500, 620, seed=7)
    d.lw = 1.5
    d.fade = (460, 600)
    for i, v in enumerate(['front', '34', 'side']):
        d.push(i * 500, 0)
        CAST[name].bust_view(d, v)
        d.pop()
    out('turn-' + name, d)


JOBS['turn_anya'] = lambda: turnaround('anya')
JOBS['turn_tim'] = lambda: turnaround('tim')


def expressions(name, faces, y=220, s=0.86):
    d = Doc(1600, 500, seed=9)
    d.lw = 1.4
    m = CAST[name]
    for i, e in enumerate(faces):
        d.push(200 + i * 400, y, s, parts.EXPR[e].get('tilt_head', 0))
        m.head34(d, e)
        d.pop()
    out('expr-' + name, d)


JOBS['expr_anya'] = lambda: expressions('anya', ['joy', 'surprise', 'sad', 'anger'])
JOBS['expr_tim'] = lambda: expressions('tim', ['joy', 'surprise', 'sad', 'anger'], y=270, s=1.1)


@job
def cast():
    """The four together: Савелий Петрович turned to the others, Тим showing off his jar, Аня and Вера looking on."""
    d = Doc(1800, 880, seed=11)
    d.lw = 1.08
    s = 0.92
    place = [('savely', 380, True, 'peer'), ('tim', 740, False, 'smirk'), ('anya', 1090, False, 'dream'),
             ('vera', 1440, False, 'stern')]
    for name, cx, flip, e in place:
        # a pale shadow under the feet, then the figure
        wash(d, [(cx - 110, 820), (cx + 100, 814), (cx + 110, 836), (cx - 100, 840)], '#b9b2c6', 0.35)
        d.push(cx + 300 * s if flip else cx - 300 * s, 10, s, 0, flip)
        CAST[name].figure(d, e)
        d.pop()
    for x0, x1 in [(250, 520), (610, 880), (960, 1220), (1310, 1570)]:
        ink(d, [(x0, 830), ((x0 + x1) / 2, 827), (x1, 831)], w=1.0, start=0.2, end=0.2)
    out('cast', d)


@job
def rule_line():
    """The pen: one stroke tapered and swelling, one gone over twice, one skipping; hatching; tufts."""
    d = Doc(1200, 360, seed=2)
    d.lw = 1.6
    ink(d, [(60, 80), (200, 60), (360, 90), (520, 70)], w=2.6, start=1.0, end=0.05, retrace=0)
    ink(d, [(60, 150), (200, 130), (360, 160), (520, 140)], w=2.4, start=0.3, end=0.2, retrace=1.0, seed=4)
    ink(d, [(60, 220), (200, 200), (360, 230), (520, 210)], w=2.2, start=0.5, end=0.3, skip=0.25, seed=5)
    from kit import hatch
    hatch(d, [(620, 60), (820, 50), (840, 220), (630, 240)], angle=60, gap=10, w=1.0, fill=0.8, seed=3)
    parts.tufts(d, [(900, 200), (980, 160), (1080, 160), (1150, 200)], n=10, length=(12, 24), lean=0.5, w=1.6,
                seed=8)
    out('rule-line', d)


@job
def rule_layers():
    """Line, wash, and both: the wash is laid loosely, off the line, with white paper left."""
    big = Doc(1800, 720, seed=3)
    big.lw = 1.6
    big.fade = (470, 690)
    for k, mode in enumerate(['ink', 'wash', 'both']):
        big.push(k * 600, 0)
        big.rnd.seed(3)                 # the same drawing three times
        n_w, n_i, n_h = len(big.washes), len(big.inks), len(big.whites)
        anya.bust(big)
        if mode == 'ink':
            del big.washes[n_w:]
            del big.whites[n_h:]
        elif mode == 'wash':
            del big.inks[n_i:]
        big.pop()
    out('rule-layers', big, 0.8)


@job
def rule_faces():
    """Eyes and mouths: a round of white paper, a dot, a loose lid; mouths as one stroke."""
    d = Doc(1200, 380, seed=4)
    d.lw = 1.6
    for i, e in enumerate(['calm', 'dream', 'joy', 'surprise', 'sad', 'anger']):
        x = 110 + i * 190
        ex = parts.EXPR[e]
        wash(d, [(x - 70, 60), (x + 70, 56), (x + 74, 300), (x - 66, 306)], parts.SKIN, 0.4)
        parts.eye(d, x - 30, 130, 1.6 * ex['eye'], ex['look'], ex['lid'], lash=True, side=-1,
                  squint=ex.get('squint', False))
        parts.eye(d, x + 30, 130, 1.6 * ex['eye'], ex['look'], ex['lid'], lash=True, side=1,
                  squint=ex.get('squint', False))
        parts.brow(d, x - 30, 92, 32, ex['lift'] * 1.6, ex['tilt'] * 1.6, side=-1, w=1.4)
        parts.brow(d, x + 30, 92, 32, ex['lift'] * 1.6, ex['tilt'] * 1.6, side=1, w=1.4)
        parts.mouth(d, x, 240, ex['mouth'], 1.8, side=-1, lips=ex['mouth'] == 'soft')
    out('rule-faces', d)


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'svg'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'pics'), exist_ok=True)
    flt = sys.argv[1] if len(sys.argv) > 1 else ''
    for name, fn in JOBS.items():
        if flt.replace('-', '_') in name:
            fn()
