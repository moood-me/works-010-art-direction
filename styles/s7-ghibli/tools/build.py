"""Build every picture of the page: svg/*.svg and pics/*.png.

    python3 tools/build.py              # everything
    python3 tools/build.py portrait     # only pictures whose name contains "portrait"
"""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import View
from svgdoc import Doc, render
from head import Expr
from body import Figure
from dress import draw_figure, head_drawer
import scenes
import anya, savely, tim, vera, marat, kira

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
    'marat': (marat, 'ladle', 'ladle', 'kitchen'),
    'kira': (kira, 'pocket', 'pocket', 'dusk'),
}

EXPR = {
    'calm': Expr(),
    'joy': Expr(closed=1, mouth='D', mouth_open=0.9, smile=1.0, teeth=True, blush=0.6, brow_up=0.35, mouth_w=1.25),
    'surprise': Expr(open=1.2, iris=0.78, brow_up=1.0, brow_arch=0.6, mouth='O', mouth_open=0.7, mouth_w=0.7),
    'sad': Expr(open=0.72, lid_out=0.35, brow_in=-1.0, brow_up=0.2, smile=-0.9, look=(0.0, -0.7), mouth_w=0.9),
    'anger': Expr(open=0.85, lid_in=0.45, brow_in=1.1, brow_up=-0.45, mouth='shout', mouth_open=0.85, teeth=True,
                  smile=-0.5, mouth_w=1.35),
}
# small corrections of the face per character for the default look
CALM = {
    'anya': Expr(smile=0.25, look=(0.25, 0.15)),
    'savely': Expr(smile=-0.5, open=0.85, brow_in=0.6, look=(-0.2, -0.6)),
    'tim': Expr(smile=0.9, mouth_w=1.15, look=(0.35, 0.0), brow_in=-0.3, brow_up=0.2),
    'vera': Expr(open=0.82, smile=-0.25, brow_in=0.25, look=(0.3, 0.0)),
    'marat': marat.CALM,
    'kira': kira.CALM,
}


def save(d, name):
    if FILTER and FILTER not in name:
        return
    d.grain(0.06)
    p = os.path.join(SVG, name + '.svg')
    d.save(p)
    png = os.path.join(PNG, name + '.png')
    render(p, png, d.w, d.h)
    from PIL import Image
    Image.open(png).convert('RGB').save(os.path.join(PNG, name + '.jpg'), quality=88)
    os.remove(png)
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
    elif where == 'kitchen':
        scenes.kitchen(d, w, h, seed=seed)
        if floor_y:
            scenes.kitchen_floor(d, w, h, floor_y)
    elif where == 'dusk':
        scenes.dusk(d, w, h, seed=seed, ground=floor_y)


def expr_of(name, key):
    if key == 'calm':
        return Expr(CALM[name])
    # a character may show a feeling in its own way (its module's EXPR), else the common one
    return Expr(getattr(CAST[name][0], 'EXPR', {}).get(key, EXPR[key]))


# ---------------------------------------------------------------- pictures
def portrait(name, key='calm'):
    m, pp, fp, where = CAST[name]
    W, H = 600, 720
    d = Doc(W, H, lw=2.6)
    place(d, W, H, where, seed=7)
    F = Figure(m.B, m.POSES[pp])
    v = view_at(18, 14.0 * 23.5 / m.B['head_h'], F.J['head'], W * 0.5, H * 0.38)
    person(d, v, name, pp, expr_of(name, key))
    return d


def figure(name):
    m, pp, fp, where = CAST[name]
    W, H = 600, 1000
    d = Doc(W, H, lw=1.9)
    floor = H - 70
    place(d, W, H, where, floor_y=floor - 120 if where != 'meadow' else None, seed=3)
    F = Figure(m.B, m.POSES[fp])
    v = view_at(22, m.SPEC.get('figure_scale', 5.2), (0, 0, 0), W * 0.5, floor)   # a giant gets a smaller scale
    scenes.ground_shadow(d, v, F)
    person(d, v, name, fp, expr_of(name, 'calm'))
    if where == 'meadow':
        scenes.meadow_front(d, W, H)
    return d


def turnaround(name, calm=False):
    """calm=True: the character's own resting face instead of the neutral one."""
    m, pp, fp, where = CAST[name]
    W, H = 1500, 1000
    d = Doc(W, H, lw=1.9)
    scenes.grad(d, 0, 0, W, H, [(0, '#efe6d4'), (1, '#e2d6bf')])
    d.mottle(0.01, 0.3, 4)
    floor = H - 70
    for i, yaw in enumerate((0, 35, 90)):
        F = Figure(m.B, m.POSES['stand'])
        v = view_at(yaw, m.SPEC.get('figure_scale', 5.2), (0, 0, 0), W * (0.18 + 0.32 * i), floor)
        scenes.ground_shadow(d, v, F)
        person(d, v, name, 'stand', expr_of(name, 'calm') if calm else Expr())
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
    # two grown-ups a step behind, Аня and Тим in front
    places = [('vera', 560, 880, 4.7, 'crossed', 14), ('savely', 900, 868, 4.7, 'watch', 30),
              ('anya', 1190, 950, 5.3, 'hat', 24), ('tim', 1470, 966, 5.4, 'hips', 16)]
    for name, x, floor, s, pose, yaw in places:
        m = CAST[name][0]
        F = Figure(m.B, m.POSES[pose])
        v = view_at(yaw, s, (0, 0, 0), x, floor)
        scenes.ground_shadow(d, v, F)
        person(d, v, name, pose, expr_of(name, 'calm'))
    scenes.meadow_front(d, W, H)
    return d


def cast6():
    """all six on the meadow: Марат in the middle of the back row, Кира at the edge, a step apart."""
    W, H = 1800, 1000
    d = Doc(W, H, lw=1.8)
    scenes.meadow(d, W, H, horizon=0.58, seed=11)
    places = [('vera', 455, 878, 4.4, 'crossed', 14), ('marat', 770, 884, 4.4, 'ladle', 16),
              ('savely', 1100, 872, 4.4, 'watch', 30), ('kira', 185, 952, 4.9, 'pocket', 20),
              ('anya', 1350, 950, 4.9, 'hat', 24), ('tim', 1600, 964, 5.0, 'hips', 16)]
    for name, x, floor, s, pose, yaw in places:
        m = CAST[name][0]
        F = Figure(m.B, m.POSES[pose])
        v = view_at(yaw, s, (0, 0, 0), x, floor)
        scenes.ground_shadow(d, v, F)
        person(d, v, name, pose, expr_of(name, 'calm'))
    scenes.meadow_front(d, W, H)
    return d


def stages():
    """how a picture is made: the line; flat colour; one shadow tone."""
    import svgdoc
    W, H = 1500, 640
    d = Doc(W, H, lw=2.4)
    scenes.grad(d, 0, 0, W, H, [(0, '#efe6d4'), (1, '#e0d3ba')])
    for i, mode in enumerate(('line', 'flat', 'full')):
        svgdoc.MODE = mode
        sub = Doc(500, H, lw=2.4)
        F = Figure(anya.B, anya.POSES['stand'])
        v = view_at(18, 12.0, F.J['head'], 250, H * 0.42)
        person(sub, v, 'anya', 'stand', expr_of('anya', 'calm'))
        d.defs += sub.defs
        d.add(f'<g transform="translate({i * 500},0)">{"".join(sub.body)}</g>')
    svgdoc.MODE = 'full'
    for i, t in enumerate(('1. линия', '2. плоский цвет', '3. один тон тени')):
        d.add(f'<text x="{i * 500 + 250}" y="44" text-anchor="middle" font-family="sans-serif" font-size="26" '
              f'fill="#5a4a3a">{t}</text>')
    return d


def face_rule():
    """where things sit on a Ghibli face: the same head front and in profile with guide lines."""
    W, H = 1200, 700
    d = Doc(W, H, lw=2.6)
    scenes.grad(d, 0, 0, W, H, [(0, '#f3ecdc'), (1, '#e8dcc4')])
    m = anya
    h = m.head()
    marks = [(1.0, 'макушка'), (0.16, 'брови'), (-0.09, 'глаза'), (-0.50, 'низ носа'), (-0.72, 'рот'), (-1.0, 'подбородок')]
    for i, yaw in enumerate((0, 90)):
        v = View(yaw=yaw, pitch=0, s=13, ox=330 + i * 480, oy=350)
        h.place((0, 0, 0), 24)
        hr = m.hair(h)
        Fh, Bh, st = hr.build(v)
        if Bh is not None:
            hr.draw(d, v, Bh, m.HAIR)
        hr.draw_mid(d, v, m.HAIR)
        sk = h.draw_face(d, v, Expr(), m.SKIN, m.HAIR, m.IRIS, hair_front=Fh)
        hr.draw(d, v, Fh, m.HAIR, st)
    for y, t in marks:
        py = 350 - y * 12 * 13
        d.add(f'<line x1="120" x2="{W - 40}" y1="{py:.0f}" y2="{py:.0f}" stroke="#b0503a" stroke-width="1.4" '
              f'stroke-dasharray="6 6" opacity="0.8"/>')
        d.add(f'<text x="20" y="{py + 6:.0f}" font-family="sans-serif" font-size="22" fill="#8a3a2a">{t}</text>')
    return d


if __name__ == '__main__':
    if want('rule-stages'):
        save(stages(), 'rule-stages')
    if want('rule-face'):
        save(face_rule(), 'rule-face')
    for n in CAST:
        if want('portrait-' + n):
            save(portrait(n), 'portrait-' + n)
        if want('figure-' + n):
            save(figure(n), 'figure-' + n)
    for n in ('anya', 'tim', 'marat', 'kira'):
        if want('turn-' + n):
            save(turnaround(n, calm=n in ('marat', 'kira')), 'turn-' + n)
    for n in ('anya', 'tim', 'marat', 'kira'):
        if want('expr-' + n):
            save(expressions(n), 'expr-' + n)
    if want('cast'):
        save(cast(), 'cast')
    if want('six'):
        save(cast6(), 'six')
