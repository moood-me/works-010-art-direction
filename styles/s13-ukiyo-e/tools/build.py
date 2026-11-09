"""Draws every picture of the style: python3 build.py [part of a name] — writes ../svg/*.svg and renders
../pics/*.jpg with render.js (headless Chromium through Playwright)."""
import os
import subprocess
import sys

import anya
import kira
import marat
import parts
import savely
import tim
import vera
from kit import Doc, INK, RED

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = {}
MADE = []

# the ground of each one's sheet and the bokashi along its top edge
GROUND = {
    'anya': ('#e2d2a2', '#c9a35a'), 'savely': ('#a7a096', '#6e6a6c'), 'tim': ('#c3cdb6', '#7f9c94'),
    'vera': ('#cfc6c4', '#8c8496'), 'marat': ('#8fa3ab', '#4f6c80'), 'kira': ('#c2c1ae', '#6c5a72'),
}
WHO = dict(anya=anya, savely=savely, tim=tim, vera=vera, marat=marat, kira=kira)


def job(fn):
    JOBS[fn.__name__] = fn
    return fn


def out(name, d):
    path = os.path.join(ROOT, 'svg', name + '.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(d.svg())
    MADE.append(name)


def portrait(key, x=440, y=520, s=1.5):
    m = WHO[key]
    d = Doc(800, 1100, seed=3 + len(key))
    g, top = GROUND[key]
    d.ground(g, top=top)
    with d.g(x, y, s):
        m.bust(d, 'q', hand=True)
    name = m.NAME.replace(' ', '·')
    d.cartouche(name, 690, 60, 26 if len(name) < 8 else 19)
    out('portrait-' + key, d)


def figure(key, x=430, s=1.15):
    m = WHO[key]
    d = Doc(800, 1200, seed=11 + len(key))
    g, top = GROUND[key]
    d.ground(g, top=top, bottom='#b9a67c')
    with d.g(x, 1110, s):
        m.figure(d)
    out('figure-' + key, d)


def turn(key):
    m = WHO[key]
    d = Doc(1800, 800, seed=21 + len(key))
    g, top = GROUND[key]
    d.ground(g, top=top)
    for i, v in enumerate(('f', 'q', 's')):
        with d.g(300 + i * 600, 330, 1.25):
            m.bust(d, v)
    out('turn-' + key, d)


def expr(key):
    m = WHO[key]
    d = Doc(2000, 720, seed=31 + len(key))
    g, top = GROUND[key]
    d.ground(g, top=top)
    for i, e in enumerate(('joy', 'surprise', 'sad', 'anger')):
        with d.g(270 + i * 490, 300, 1.1):
            m.bust(d, 'q', e)
    out('expr-' + key, d)


def _each(prefix, fn, keys):
    for k in keys:
        JOBS[prefix + '_' + k] = (lambda k=k: fn(k))


_each('portrait', portrait, WHO)
_each('figure', lambda k: figure(k, 440, 1.1) if k == 'marat' else figure(k), WHO)
_each('turn', turn, ('anya', 'savely', 'marat'))
_each('expr', expr, ('anya', 'tim', 'savely', 'marat', 'kira'))


def stand(d, m, x, s, flip=False, y=1150):
    with d.g(x, y, s, flip=flip):
        m.figure(d)


@job
def cast():
    """The four: Тим runs after his butterfly, Савелий Петрович raises a finger after him, Аня and Вера."""
    d = Doc(2200, 1300, seed=5)
    d.ground('#d6cba8', top='#6f8ca0', bottom='#a9a27a')
    s = 1.2
    stand(d, tim, 560, s)
    stand(d, savely, 1010, s)
    stand(d, anya, 1420, s, flip=True)
    stand(d, vera, 1850, s)
    d.cartouche('четверо', 2090, 60, 24)
    out('cast', d)


@job
def cast6():
    """All six."""
    d = Doc(3000, 1400, seed=6)
    d.ground('#d6cba8', top='#6f8ca0', bottom='#a9a27a')
    s = 1.2
    stand(d, tim, 520, s, y=1250)
    stand(d, savely, 930, s, y=1250)
    stand(d, anya, 1290, s, flip=True, y=1250)
    stand(d, marat, 1900, s, y=1250)
    stand(d, vera, 2330, s, y=1250)
    stand(d, kira, 2700, s, flip=True, y=1250)
    d.cartouche('шестеро', 2890, 60, 24)
    out('cast6', d)


@job
def rule_line():
    """The brush: the strokes of the key block and the outline of a shape."""
    d = Doc(1600, 560, seed=7)
    d.ground('#e2d7ba')
    for i, (prof, w) in enumerate((('taper', 9), ('tail', 9), ('swell', 9), ('press', 8), ('even', 3))):
        y = 90 + i * 80
        d.line([(80, y), (200, y - 26), (340, y + 14), (470, y - 16), (560, y)], w, prof)
    d.shape([(700, 90), (800, 60), (900, 120), (960, 260), (900, 420), (760, 470), (660, 380), (640, 220)], '#c8683a',
            5.0, pattern=d.seigaiha('#e08e5c', 16, 1.2), nib=0.6)
    for f in ([(760, 110), (800, 250), (780, 440)], [(860, 140), (880, 280), (850, 420)],
              [(700, 200), (720, 320), (700, 400)]):
        d.line(f, 4.5, 'taper')
    black = [(1060, 150), (1160, 80), (1300, 80), (1420, 150), (1440, 300), (1400, 440), (1300, 300), (1180, 250),
             (1090, 290)]
    d.fill(black, '#1f1a1c')
    d.strands([(1090, 280), (1180, 240), (1300, 290), (1396, 420)], [(1066, 150), (1160, 86), (1300, 86), (1436, 290)],
              8, 1.0, '#8c8a94', op=0.6)
    d.fringe([(1062, 160), (1090, 290), (1180, 250), (1300, 300), (1400, 440)], 9, 1.0, '#1f1a1c', lean=0.7,
             step=3.2, side=-1)
    out('rule-line', d)


@job
def rule_face():
    """The face of the print in three views and what the eyes, brows and mouth do."""
    d = Doc(2000, 760, seed=8)
    d.ground('#e2d7ba')
    p = parts.P(long=1.08, blush=('#e79a86', 0.25), eye=dict(w=42, h=8.6, lash=1.0, crease=0.35))
    for i, v in enumerate(('f', 'q', 's')):
        with d.g(210 + i * 330, 250, 1.3):
            parts.neck(d, p, v)
            parts.head(d, p, v, 'calm')
    for i, e in enumerate(('calm', 'joy', 'surprise', 'sad', 'anger', 'grin', 'smirk', 'stern')):
        with d.g(1180 + (i % 4) * 210, 190 + (i // 4) * 300, 0.82):
            parts.head(d, p, 'q', e)
    out('rule-face', d)


@job
def rule_cloth():
    """Cloth: flat colour, a pattern printed flat over it, bokashi, folds as strokes with a pressed start."""
    d = Doc(2000, 520, seed=9)
    d.ground('#e2d7ba')
    sw = [('#d8a23a', d.asanoha('#b9812a', 26, 1.0)), ('#6f8fa8', d.blossoms('#f3ead6', 30, 3.6, heart='#d8a23a')),
          ('#566b4b', d.kasuri('#8da07a', 20, 6)), ('#f6f0e0', d.stripes('#b8402f', 30, 14, rot=90)),
          ('#3f5263', d.dots('#6d8296', 9, 1.3)), ('#c8683a', d.seigaiha('#e08e5c', 16, 1.2)),
          ('#e6dfd0', d.checks('#3f4a5a', 10)), ('#4b2f48', d.asanoha('#33203a', 30, 1.4))]
    for i, (c, pat) in enumerate(sw):
        x = 70 + i * 236
        shape = [(x, 90, 'c'), (x + 190, 80, 'c'), (x + 200, 420, 'c'), (x + 100, 440), (x + 10, 410, 'c')]
        d.shape(shape, c, 4.0, pattern=pat, nib=0.6)
        d.bokashi(shape, '#2a2426', (x, 440), (x, 250), 0.38)
        d.line([(x + 60, 96), (x + 74, 250), (x + 60, 420)], 4.0, 'taper')
        d.line([(x + 130, 92), (x + 150, 240), (x + 144, 426)], 4.0, 'taper')
    out('rule-cloth', d)


@job
def rule_hands():
    """Hands: each finger a soft tapering shape with a thin outline."""
    d = Doc(1600, 520, seed=10)
    d.ground('#e2d7ba')
    for i, pose in enumerate(('rest', 'pinch', 'open', 'point', 'grip')):
        x = 190 + i * 300
        d.shape([(x - 60, 40, 'c'), (x + 60, 40, 'c'), (x + 34, 150), (x - 34, 150)], '#3f5263', 3.6, nib=0.6,
                pattern=d.dots('#6d8296', 9, 1.3))
        parts.hand(d, x, 146, 2.6, 0, pose, lw=1.5)
        d.line([(x - 36, 146), (x, 154), (x + 36, 146)], 3.6, 'swell')
    out('rule-hands', d)


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'svg'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'pics'), exist_ok=True)
    flt = (sys.argv[1] if len(sys.argv) > 1 else '').replace('-', '_')
    for name, fn in JOBS.items():
        if flt in name:
            fn()
    args = []
    for n in MADE:
        args += [os.path.join(ROOT, 'svg', n + '.svg'), os.path.join(ROOT, 'pics', n + '.jpg'), '1']
    if args:
        subprocess.run(['node', os.path.join(ROOT, 'tools', 'render.js')] + args, check=True)
    print('made:', ' '.join(MADE))
