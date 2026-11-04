"""Build every picture of the page: svg/*.svg and pics/*.png.

    python3 tools/build.py              # everything
    python3 tools/build.py portrait     # only pictures whose name contains "portrait"
"""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import View
from svgdoc import Doc, render, mix
from head import Expr
from body import Figure
from dress import draw_figure, head_drawer
import scenes
import anya, savely, tim, vera

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG, PNG = os.path.join(HERE, 'svg'), os.path.join(HERE, 'pics')
os.makedirs(SVG, exist_ok=True)
os.makedirs(PNG, exist_ok=True)
FILTER = sys.argv[1] if len(sys.argv) > 1 else ''

# each one: module, pose for the portrait, pose for the full figure, the place
CAST = {
    'anya': (anya, 'hat', 'hat', 'meadow'),
    'savely': (savely, 'watch', 'watch', 'workshop'),
    'tim': (tim, 'hips', 'hips', 'thicket'),
    'vera': (vera, 'crossed', 'crossed', 'study'),
}

EXPR = {
    'calm': Expr(),
    'joy': Expr(closed=1, mouth='D', mouth_open=0.9, smile=1.0, teeth=True, blush=0.6, brow_up=0.35, mouth_w=1.25),
    'surprise': Expr(open=1.2, iris=0.78, brow_up=1.0, brow_arch=0.6, mouth='O', mouth_open=0.7, mouth_w=0.7),
    'sad': Expr(open=0.72, lid_out=0.35, brow_in=-1.0, brow_up=0.2, smile=-0.9, look=(0.0, -0.7), mouth_w=0.9),
    'anger': Expr(open=0.85, lid_in=0.45, brow_in=1.1, brow_up=-0.45, mouth='shout', mouth_open=0.55, teeth=True,
                  smile=-0.5, mouth_w=1.1),
}
# small corrections of the face per character for the default look
CALM = {
    'anya': Expr(smile=0.25, look=(0.25, 0.15)),
    'savely': Expr(smile=-0.5, open=0.85, brow_in=0.6, look=(-0.2, -0.6)),
    'tim': Expr(smile=0.9, mouth_w=1.15, look=(0.35, 0.0), brow_in=-0.3, brow_up=0.2),
    'vera': Expr(open=0.82, smile=-0.25, brow_in=0.25, look=(0.3, 0.0)),
}


def save(d, name):
    if FILTER and FILTER not in name:
        return
    d.grain(0.06)
    p = os.path.join(SVG, name + '.svg')
    d.save(p)
    render(p, os.path.join(PNG, name + '.png'), d.w, d.h)
    print(name, flush=True)


def want(name):
    return not FILTER or FILTER in name


def view_at(yaw, s, model_pt, px, py, pitch=4.0):
    v = View(yaw=yaw, pitch=pitch, s=s)
    a = v.xy(np.asarray(model_pt, float)[None])[0]
    v.ox, v.oy = px - a[0], py - a[1]
    return v


def person(d, view, name, pose, expr):
    m = CAST[name][0]
    F = Figure(m.B, m.POSES[pose])
    h = m.head()
    hr = m.hair(h)
    fn = head_drawer(h, hr, m.SKIN, m.HAIR, m.IRIS, expr, extra=getattr(m, 'extra', None))
    draw_figure(d, view, F, m.SPEC, fn)
    return F


def place(d, w, h, where, floor_y=None, seed=1):
    if where == 'meadow':
        scenes.meadow(d, w, h, horizon=0.6, seed=seed)
    elif where == 'workshop':
        scenes.workshop(d, w, h, seed=seed)
        if floor_y:
            scenes.workshop_floor(d, w, h, floor_y)
    elif where == 'thicket':
        scenes.thicket(d, w, h, seed=seed)
        if floor_y:
            scenes.grad(d, 0, floor_y, w, h - floor_y, [(0, '#8aa858'), (1, '#6a8c44')])
    elif where == 'study':
        scenes.study(d, w, h, seed=seed)
        if floor_y:
            scenes.grad(d, 0, floor_y, w, h - floor_y, [(0, '#5a4a3e'), (1, '#3e3028')])


def expr_of(name, key):
    e = Expr(EXPR[key])
    if key == 'calm':
        e = Expr(CALM[name])
    return e


# ---------------------------------------------------------------- pictures
def portrait(name, key='calm'):
    m, pp, fp, where = CAST[name]
    W, H = 600, 720
    d = Doc(W, H, lw=2.6)
    place(d, W, H, where, seed=7)
    F = Figure(m.B, m.POSES[pp])
    v = view_at(22, 14.0 * 23.5 / m.B['head_h'], F.J['head'], W * 0.5, H * 0.38)
    person(d, v, name, pp, expr_of(name, key))
    return d


def figure(name):
    m, pp, fp, where = CAST[name]
    W, H = 600, 1000
    d = Doc(W, H, lw=1.9)
    floor = H - 70
    place(d, W, H, where, floor_y=floor - 120 if where != 'meadow' else None, seed=3)
    F = Figure(m.B, m.POSES[fp])
    v = view_at(22, 5.2, (0, 0, 0), W * 0.5, floor)
    scenes.ground_shadow(d, v, F)
    person(d, v, name, fp, expr_of(name, 'calm'))
    if where == 'meadow':
        scenes.meadow_front(d, W, H)
    return d


def turnaround(name):
    m, pp, fp, where = CAST[name]
    W, H = 1500, 1000
    d = Doc(W, H, lw=1.9)
    scenes.grad(d, 0, 0, W, H, [(0, '#efe6d4'), (1, '#e2d6bf')])
    d.mottle(0.01, 0.3, 4)
    floor = H - 70
    for i, yaw in enumerate((0, 35, 90)):
        F = Figure(m.B, m.POSES['stand'])
        v = view_at(yaw, 5.2, (0, 0, 0), W * (0.18 + 0.32 * i), floor)
        scenes.ground_shadow(d, v, F)
        person(d, v, name, 'stand', Expr())
    return d


def expressions(name):
    m, pp, fp, where = CAST[name]
    W, H = 2000, 620
    d = Doc(W, H, lw=2.4)
    scenes.grad(d, 0, 0, W, H, [(0, '#efe6d4'), (1, '#e0d3ba')])
    d.mottle(0.01, 0.3, 5)
    for i, key in enumerate(('joy', 'surprise', 'sad', 'anger')):
        F = Figure(m.B, m.POSES['stand'])
        v = view_at(22, 11.0 * 23.5 / m.B['head_h'], F.J['head'], 250 + i * 500, H * 0.40)
        person(d, v, name, 'stand', expr_of(name, key))
    return d


def cast():
    W, H = 1800, 1000
    d = Doc(W, H, lw=1.9)
    scenes.meadow(d, W, H, horizon=0.58, seed=11)
    floor = H - 80
    places = [('vera', 330, 'crossed', 16), ('savely', 700, 'watch', 28), ('anya', 1080, 'hat', 26), ('tim', 1440, 'hips', 18)]
    for name, x, pose, yaw in places:
        m = CAST[name][0]
        F = Figure(m.B, m.POSES[pose])
        v = view_at(yaw, 5.0, (0, 0, 0), x, floor)
        scenes.ground_shadow(d, v, F)
        person(d, v, name, pose, expr_of(name, 'calm'))
    scenes.meadow_front(d, W, H)
    return d


if __name__ == '__main__':
    for n in CAST:
        if want('portrait-' + n):
            save(portrait(n), 'portrait-' + n)
        if want('figure-' + n):
            save(figure(n), 'figure-' + n)
    for n in ('anya', 'tim'):
        if want('turn-' + n):
            save(turnaround(n), 'turn-' + n)
    for n in ('anya', 'tim'):
        if want('expr-' + n):
            save(expressions(n), 'expr-' + n)
    if want('cast'):
        save(cast(), 'cast')
