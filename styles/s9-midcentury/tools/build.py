"""Build every drawing of the page: svg/*.svg and pics/*.png.   python3 tools/build.py [name-filter]"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from kit import Doc, render, g
import scenery
import anya, savely, tim, vera, marat, kira

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG, PNG = os.path.join(HERE, 'svg'), os.path.join(HERE, 'pics')
os.makedirs(SVG, exist_ok=True)
os.makedirs(PNG, exist_ok=True)
FILTER = sys.argv[1] if len(sys.argv) > 1 else ''
SCRATCH = os.environ.get('S9_SCRATCH', '/home/user/cache/styles-s9-midcentury/render')
os.makedirs(SCRATCH, exist_ok=True)

CAST = {'anya': anya, 'savely': savely, 'tim': tim, 'vera': vera, 'marat': marat, 'kira': kira}


def save(d, name):
    if FILTER and FILTER not in name:
        return
    p = os.path.join(SVG, name + '.svg')
    d.save(p)
    # the paper and paint grain make PNGs heavy (1–2 MB each): render to a scratch PNG, keep a WebP (q 90) on the page
    tmp = os.path.join(SCRATCH, name + '.png')
    render(p, tmp, d.w, d.h)
    Image.open(tmp).convert('RGB').save(os.path.join(PNG, name + '.webp'), quality=90, method=6)
    print(name)


def portrait(name, view='34', expr='calm'):
    m = CAST[name]
    d = Doc(500, 600)
    scenery.backdrop(d, name, 'portrait')
    d.add(g(m.head(view, expr) + [g(m.bust(view), f'translate(0,{m.BUST_DY})')], 'translate(250,260) scale(1.25)', 'gouache'))
    return d


def figure(name):
    m = CAST[name]
    d = Doc(500, 900)
    scenery.backdrop(d, name, 'figure')
    d.add(g(m.figure(), f'translate(250,820) scale({1.08 * m.FIG_SCALE})', 'gouache'))
    return d


def turnaround(name):
    m = CAST[name]
    d = Doc(1500, 600)
    scenery.backdrop(d, name, 'wide')
    for i, v in enumerate(('front', '34', 'side')):
        d.add(g(m.head(v, 'calm') + [g(m.bust(v), f'translate(0,{m.BUST_DY})')], f'translate({250 + i * 500},260) scale(1.25)', 'gouache'))
    return d


def expressions(name, view='34'):
    m = CAST[name]
    d = Doc(1600, 500)
    scenery.backdrop(d, name, 'wide')
    for i, ex in enumerate(('joy', 'surprise', 'sad', 'anger')):
        d.add(g(m.head(view, ex) + [g(m.bust(view), f'translate(0,{m.BUST_DY})')], f'translate({200 + i * 400},240) scale(1.25)', 'gouache'))
    return d


def text(x, y, s, size=22, anchor='middle', color='#2a201c'):
    return (f'<text x="{x}" y="{y}" font-family="Georgia, serif" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{color}">{s}</text>')


def rule_flat():
    """The same portrait as clean vector shapes and as gouache on board."""
    d = Doc(1000, 600, texture=False)
    for i, tex in enumerate((False, True)):
        m = anya
        body = m.head('34', 'calm') + [g(m.bust('34'), f'translate(0,{m.BUST_DY})')]
        back = '#ec9f93'
        d.add(g([f'<rect x="{i * 500}" width="500" height="600" fill="{back}"/>'], filt='board' if tex else None))
        d.add(g(body, f'translate({250 + i * 500},260) scale(1.25)', 'gouache' if tex else None))
    d.add('<rect x="500" width="500" height="540" filter="url(#paper)" opacity="0.35"/>')
    d.add(g([f'<rect x="0" y="540" width="1000" height="60" fill="#f3ead6"/>', text(250, 580, 'чистые формы'),
             text(750, 580, 'гуашь: неровный край, пятна краски, бумага')]))
    return d


def rule_parts():
    """The kit of the face: eyes and mouths, drawn large."""
    from face import eye, mouth
    d = Doc(1400, 520)
    eyes = [('open', 'открытый'), ('look', 'взгляд вверх'), ('dot', 'точка'), ('closed', 'мечта'), ('happy', 'радость'),
            ('wide', 'удивление'), ('sad', 'грусть'), ('lid', 'усталость'), ('glare', 'злость')]
    o, labels = [], []
    for i, (k, name) in enumerate(eyes):
        x = 80 + i * 150
        o.append(g([eye(0, 0, 4.0, k, side=1)], f'translate({x},120)'))
        labels.append(text(x, 210, name, 20))
    mouths = [('lips', 'губы'), ('soft', 'улыбка'), ('smirk', 'хитрая'), ('flat', 'строгая'), ('grin', 'смех'), ('o', 'ах'),
              ('sad', 'грусть'), ('frown', 'недовольство'), ('shout', 'крик')]
    for i, (k, name) in enumerate(mouths):
        x = 80 + i * 150
        o.append(g([mouth(0, 0, 4.0, k, side=1)], f'translate({x},340)'))
        labels.append(text(x, 430, name, 20))
    d.add(g(o, filt='gouache'))
    d.add(g(labels))
    return d


def rule_heights():
    """How many heads tall each one is: ticks at every head height."""
    from kit import brush
    d = Doc(1400, 760)
    heads = {'vera': 0.5, 'anya': 0.5, 'savely': 0.6, 'tim': 0.6}      # the scale each figure draws its head at
    tall = {'vera': 6.0, 'anya': 6.3, 'savely': 3.9, 'tim': 3.5}       # measured on the drawings, in heads
    for i, (m, key) in enumerate(((vera, 'vera'), (anya, 'anya'), (savely, 'savely'), (tim, 'tim'))):
        x = 200 + i * 330
        hh = 232 * heads[key] * 0.85
        n = int(tall[key])
        ticks = [brush([(x - 150, 700 - k * hh), (x - 120, 700 - k * hh)], 3, '#8a7a66', taper=(0, 0)) for k in range(0, n + 1)]
        nums = [text(x - 160, 700 - (k + 0.5) * hh + 7, str(k + 1), 18, 'end', '#8a7a66') for k in range(0, n)]
        top = 700 - tall[key] * hh
        ticks.append(brush([(x - 150, top), (x + 110, top)], 1.6, '#8a7a66', taper=(0, 0), opacity=0.6))
        nums.append(text(x + 110, top - 10, '≈ ' + str(tall[key]).replace('.', ',') + ' головы', 18, 'end', '#8a7a66'))
        d.add(g(ticks + nums))
        d.add(g(m.figure(), f'translate({x},700) scale(0.85)', 'gouache'))
    return d


def cast():
    """The four together on a Provensen street: Вера, Тим, Аня face right, Савелий Петрович turns to them."""
    from kit import shape
    d = Doc(1600, 900)
    d.add(g([f'<rect width="1600" height="900" fill="#ead9b4"/>'], filt='board'))
    d.add(g([scenery.sun(1380, 150, 52, '#e8a03a')], filt='gouache'))
    scenery.town(d, 640)
    d.add(g([shape([(0, 620), (800, 610), (1600, 626), (1600, 900), (0, 900)], '#b9c58a'),
             shape([(0, 760), (800, 748), (1600, 770), (1600, 900), (0, 900)], '#a3b274')], filt='gouache'))
    for m, x, flip in ((vera, 430, 1), (tim, 660, 1), (anya, 900, 1), (savely, 1150, -1)):
        d.add(g(m.figure(), f'translate({x},840) scale({0.9 * flip},0.9)', 'gouache'))
    return d


def cast_six():
    """All six on the same street: Марат greets everyone with the ladle, Кира stands apart at the other end."""
    from kit import shape
    d = Doc(1600, 900)
    d.add(g([f'<rect width="1600" height="900" fill="#ead9b4"/>'], filt='board'))
    d.add(g([scenery.sun(1250, 130, 50, '#e8a03a')], filt='gouache'))
    scenery.town(d, 640)
    d.add(g([shape([(0, 620), (800, 610), (1600, 626), (1600, 900), (0, 900)], '#b9c58a'),
             shape([(0, 760), (800, 748), (1600, 770), (1600, 900), (0, 900)], '#a3b274')], filt='gouache'))
    for m, x, y, flip in ((marat, 250, 846, 1), (vera, 560, 836, 1), (tim, 745, 846, 1), (anya, 940, 838, 1),
                          (savely, 1160, 846, -1), (kira, 1440, 852, -1)):
        d.add(g(m.figure(), f'translate({x},{y}) scale({0.86 * flip},0.86)', 'gouache'))
    return d


if __name__ == '__main__':
    save(rule_flat(), 'rule-flat')
    save(rule_parts(), 'rule-parts')
    save(rule_heights(), 'rule-heights')
    save(cast(), 'cast')
    for n in CAST:
        save(portrait(n), 'portrait-' + n)
        save(figure(n), 'figure-' + n)
    save(turnaround('anya'), 'turn-anya')
    save(expressions('anya'), 'expr-anya')
    save(turnaround('tim'), 'turn-tim')
    save(expressions('tim'), 'expr-tim')
    save(cast_six(), 'cast-six')
    for n in ('marat', 'kira'):
        save(turnaround(n), 'turn-' + n)
        save(expressions(n), 'expr-' + n)
