"""С14 — the sheets. `python3 build.py [name…]` writes svg/<name>.svg; then `node render.js [name…]` and
`python3 webp.py` make pics/. Names: portrait-<who>, figure-<who>, turn-<who>, expr-<who>, cast, cast6, rule-*."""
import sys
from kit import *
import face as F
import body as B
import scenery as S
import anya, savely, tim, vera, marat, kira

WHO = dict(anya=anya, savely=savely, tim=tim, vera=vera, marat=marat, kira=kira)
BG = dict(anya='#cfe0dc', savely='#e6d6b8', tim='#cfe3ee', vera='#e3d3d6', marat='#f0d9b2', kira='#d5d9c4')
NAMES = dict(anya='Аня', savely='Савелий Петрович', tim='Тим', vera='Вера', marat='Марат', kira='Кира')
HEIGHT = dict(anya=545, savely=470, tim=372, vera=590, marat=675, kira=535)      # as drawn by figure(), units


def portrait(who):
    """Head and shoulders, three-quarter, on a sheet of the character's own paper with a torn mat."""
    d = Doc(800, 960, BG[who])
    d.add(S.mat(800, 960, lite(BG[who], 0.55)))
    m = WHO[who]
    b = m.bust(0.5)
    if who in ('savely', 'kira'):
        b = mirror(b)
    d.add(b, 400, 440 if who != 'marat' else 480, 2.1 if who != 'marat' else 1.85)
    return d


def figure(who):
    d = Doc(800, 1000, BG[who])
    d.add(S.mat(800, 1000, lite(BG[who], 0.55)))
    d.add(S.floor(800, 1000, 880, dark(BG[who], 0.10)))
    m = WHO[who]
    s = min(1.42, 720 / HEIGHT[who]) if who != 'tim' else 1.6
    x = dict(anya=440, savely=380, tim=400, vera=400, marat=440, kira=390)[who]
    d.add(m.figure(), x, 880, s)
    return d


def turnaround(who):
    d = Doc(1500, 720, BG[who])
    m = WHO[who]
    s = 1.45 if who != 'marat' else 1.3
    for i, (yaw, name) in enumerate(((0, 'анфас'), (0.5, 'три четверти'), (1, 'профиль'))):
        d.add(m.bust(yaw), 260 + i * 490, 300, s)
        d.text(260 + i * 490, 700, name)
    return d


def expressions(who):
    d = Doc(1600, 560, BG[who])
    m = WHO[who]
    s = 1.12 if who != 'marat' else 1.0
    for i, (ex, name) in enumerate((('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('angry', 'злость'))):
        d.add(m.bust(0, ex), 200 + i * 400, 230, s)
        d.text(200 + i * 400, 540, name)
    return d


def cast():
    """The four: a street of cut paper — hills, houses, a paper sun; each figure stands on its own shadow."""
    d = Doc(1600, 900, '#cfe6e4')
    d.add(S.street(1600, 900, 770))
    for who, x, flip in (('savely', 300, False), ('tim', 640, False), ('anya', 1010, False), ('vera', 1320, True)):
        f = WHO[who].figure()
        d.add(mirror(f) if flip else f, x, 820, 1.12)
    return d


def cast6():
    d = Doc(2000, 960, '#f6dcae')
    d.add(S.street(2000, 960, 810, evening=True))
    d.add(S.bunting(2000, 40))
    for who, x, flip in (('kira', 250, False), ('savely', 540, False), ('tim', 800, False), ('marat', 1150, False), ('anya', 1560, False), ('vera', 1800, True)):
        f = WHO[who].figure()
        d.add(mirror(f) if flip else f, x, 850, 1.0)
    return d


def rule_layers():
    """How a head is made: the pieces apart, then glued; the same head flat (no paper) and as paper."""
    d = Doc(1600, 620, '#e9dfcb')
    sp = anya.SPEC
    f = F.face(sp, 0)
    back, front = anya.hair(0)
    parts = [(back, 'волосы сзади'), (f['skin'] + f['ears'], 'лицо и уши'), (f['feats'], 'щёки, глаза, брови'), (f['nose'] + f['mouth'], 'нос и рот'), (front, 'чёлка и прядь')]
    for i, (p, name) in enumerate(parts):
        d.add(p, 150 + i * 235, 250, 0.95)
        d.text(150 + i * 235, 480, name, 20)
    d.add(anya.bust(0), 1400, 250, 1.05)
    d.text(1400, 560, 'склеено: выше слой — длиннее тень', 20)
    d.text(700, 580, 'пять слоёв бумаги, снизу вверх', 20)
    return d


def rule_paper():
    """The kinds of paper and what a fold, a curl and a brad look like."""
    d = Doc(1600, 520, '#e9dfcb')
    x = 130
    items = [
        ([card(ell(0, 0, 80, 62, n=12), '#6c9bc4', 1)], 'картон, ножницы: слой 1'),
        ([card(ell(0, 0, 80, 62, n=12), '#6c9bc4', 3)], 'тот же кусок выше: слой 3'),
        ([paint(ell(0, 0, 80, 62, n=12), '#e0ae38', 2, var=1)], 'крашеная бумага (мазки)'),
        ([torn(ell(0, 0, 80, 62, n=12), '#c9623a', 2)], 'рваный край, белая сердцевина'),
    ]
    fp = [(-70, -60, 1), (70, -60, 1), (84, 60, 1), (-84, 60, 1)]
    items.append(([paint(fp, '#3f7355', 2, var=0)] + B.folds(fp, [((-24, 0), (0, -2)), ((30, 0), (56, -2))], 0.3) +
                  [light(fp, (-26, 0), (-46, 2), 0.3), light(fp, (28, 0), (10, 2), 0.3)], 'сгибы: тень и свет полосой'))
    items.append((B.limb([(-60, -40), (0, 30), (64, -30)], [30, 26, 22], '#5b2f57', 2, 'paint', 1) + B.curl(-20, -40, 22, '#a9502c', 2) + B.curl(30, 44, 15, '#2a2125', 2),
                  'шарнир на скрепке, завитки'))
    for i, (p, name) in enumerate(items):
        d.add(p, x + i * 268, 220, 1.0)
        d.text(x + i * 268, 400, name, 19)
    d.text(800, 480, 'свет всегда слева сверху; контурной линии нет нигде — форму держат край, тень и цвет', 21)
    return d


def rule_parts():
    """The set of face pieces: eyes by lid, mouths."""
    d = Doc(1600, 560, '#e9dfcb')
    sp = dict(F.DEFAULT, **anya.SPEC)
    for i, (ex, name) in enumerate((('calm', 'спокойно'), ('joy', 'радость'), ('laugh', 'смех'), ('surprise', 'удивление'), ('sad', 'грусть'), ('angry', 'злость'), ('tired', 'усталость'))):
        e = F.expr_of(sp, ex) if ex != 'calm' else dict(F.EXPR['calm'])
        x = 130 + i * 222
        bg = [card(ell(0, 6, 62, 50, n=12), sp['skin'], 1)]
        d.add(bg + F.eye(-2, 10, 24, 21, sp, e, 1) + [F.brow(0, -34, dict(sp, brow_len=44, brow_w=8), e, 1)], x, 130, 1.3)
        bg2 = [card(ell(0, 6, 62, 40, n=12), sp['skin'], 1)]
        d.add(bg2 + F.mouth(0, 0, dict(sp, mouth_w=30), e), x, 360, 1.3)
        d.text(x, 490, name, 20)
    d.text(800, 536, 'глаз: белок, радужка, зрачок, блик — и веко, кусок бумаги, который бросает тень на глаз; рот вырезан, зубы и язык вклеены', 19)
    return d


def rule_heights():
    d = Doc(2000, 900, '#e9dfcb')
    order = ['tim', 'savely', 'kira', 'anya', 'vera', 'marat']
    xs = [200, 480, 780, 1090, 1400, 1740]
    for who, x in zip(order, xs):
        h = HEIGHT[who]
        m = WHO[who]
        sp = dict(F.DEFAULT, **m.SPEC)
        hh = sp['ry'] * 2 * dict(anya=.60, savely=.60, tim=.58, vera=.56, marat=.66, kira=.56)[who]
        n = h / hh
        for k in range(int(n) + 1):
            d.add([card(strip([(x - 140, 840 - k * hh), (x - 116, 840 - k * hh)], 4), '#8a7a66', 1)])
        d.add(m.figure(), x, 840, 1.0)
        d.text(x, 880, f'{NAMES[who]}: ≈ {n:.1f}'.replace('.', ',') + ' головы', 20)
    return d


SHEETS = {'cast': cast, 'cast6': cast6, 'rule-layers': rule_layers, 'rule-paper': rule_paper, 'rule-parts': rule_parts, 'rule-heights': rule_heights}
for w in WHO:
    SHEETS['portrait-' + w] = (lambda w=w: portrait(w))
    SHEETS['figure-' + w] = (lambda w=w: figure(w))
    SHEETS['expr-' + w] = (lambda w=w: expressions(w))
for w in ('anya', 'tim', 'marat', 'kira'):
    SHEETS['turn-' + w] = (lambda w=w: turnaround(w))

if __name__ == '__main__':
    for n in (sys.argv[1:] or list(SHEETS)):
        SHEETS[n]().save(n)
