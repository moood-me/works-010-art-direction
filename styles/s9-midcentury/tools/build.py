"""Build every drawing of the page: svg/*.svg and pics/*.png.   python3 tools/build.py [name-filter]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import Doc, render, g
import scenery
import anya, savely, tim

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG, PNG = os.path.join(HERE, 'svg'), os.path.join(HERE, 'pics')
os.makedirs(SVG, exist_ok=True)
os.makedirs(PNG, exist_ok=True)
FILTER = sys.argv[1] if len(sys.argv) > 1 else ''

CAST = {'anya': anya, 'savely': savely, 'tim': tim}


def save(d, name):
    if FILTER and FILTER not in name:
        return
    p = os.path.join(SVG, name + '.svg')
    d.save(p)
    render(p, os.path.join(PNG, name + '.png'), d.w, d.h)
    print(name)


def portrait(name, view='34', expr='calm'):
    m = CAST[name]
    d = Doc(500, 600)
    scenery.backdrop(d, name, 'portrait')
    d.add(g([g(m.bust(view), f'translate(0,{m.BUST_DY})')] + m.head(view, expr), 'translate(250,260) scale(1.25)', 'gouache'))
    return d


def figure(name):
    m = CAST[name]
    d = Doc(500, 900)
    scenery.backdrop(d, name, 'figure')
    d.add(g(m.figure(), 'translate(250,830) scale(1.08)', 'gouache'))
    return d


def turnaround(name):
    m = CAST[name]
    d = Doc(1500, 600)
    scenery.backdrop(d, name, 'wide')
    for i, v in enumerate(('front', '34', 'side')):
        d.add(g([g(m.bust(v), f'translate(0,{m.BUST_DY})')] + m.head(v, 'calm'), f'translate({250 + i * 500},260) scale(1.25)', 'gouache'))
    return d


def expressions(name, view='34'):
    m = CAST[name]
    d = Doc(1600, 460)
    scenery.backdrop(d, name, 'wide')
    for i, ex in enumerate(('joy', 'surprise', 'sad', 'anger')):
        d.add(g([g(m.bust(view), f'translate(0,{m.BUST_DY})')] + m.head(view, ex), f'translate({200 + i * 400},200) scale(1.0)', 'gouache'))
    return d


if __name__ == '__main__':
    for n in CAST:
        save(portrait(n), 'portrait-' + n)
        save(figure(n), 'figure-' + n)
    save(turnaround('anya'), 'turn-anya')
    save(expressions('anya'), 'expr-anya')
    save(turnaround('tim'), 'turn-tim')
    save(expressions('tim'), 'expr-tim')
