"""Round three: the pictures of Марат and Кира and of all six together -> svg/*.svg, pics/*.png.
python3 tools/build6.py [name-filter]

The sheets are build.py's own (portrait, figure, turnaround, expressions, the street), so the new two are drawn
in the same format, size, line and paper as the four; the four's pictures are not rebuilt here.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FILTER = sys.argv[1] if len(sys.argv) > 1 else ''
sys.argv = sys.argv[:1]
import lc, r3, figures, features as F
import build, marat, kira

NEW = {'marat': marat, 'kira': kira}
for _n, _m in NEW.items():                      # build.fig() finds a figure as figures.<name>_figure
    setattr(figures, _n + '_figure', _m.figure)
    build.PANEL[_n] = _m.PANEL
build.RU.update(marat='Марат', kira='Кира')


def expressions(name):
    """build.expressions with the character's own versions of an expression where it has them (Кира never
    smiles openly)."""
    own = getattr(NEW[name], 'EXPR', {})
    saved = dict(F.EXPR)
    F.EXPR.update(own)
    try:
        return build.expressions(name)
    finally:
        F.EXPR.clear()
        F.EXPR.update(saved)


def six_picture(w=1500, h=900):
    """All six at the watchmaker's: the same street as the picture of the four, the height order of the cast."""
    d = lc.Doc(w, h, build.PAPER)
    ground = 640
    build.street(d, w, h, ground)
    s = 0.5
    v = r3.View(yaw=0, pitch=-6, s=s, cx=0, cy=0)
    floor_y = (ground + 150) / s
    places = [
        ('kira', dict(x=100 / s, yaw=30, scale=0.98, expr={}, z=10)),
        ('vera', dict(x=335 / s, yaw=22, scale=0.97, expr=F.EXPR['calm'], z=-20)),
        ('anya', dict(x=522 / s, yaw=28, scale=1.0, expr=F.EXPR['dream'], z=10)),
        ('savely', dict(x=770 / s, yaw=-14, scale=1.0, expr=F.EXPR['calm'], z=-40)),
        ('tim', dict(x=975 / s, yaw=24, scale=0.94, expr=F.EXPR['joy'], z=70)),
        ('marat', dict(x=1262 / s, yaw=-24, scale=1.0, expr=F.EXPR['joy'], z=20)),
    ]
    chars, cols = [], {}
    for name, pl in places:
        f, col, floor = build.fig(name)
        pl['y'] = floor_y - floor * pl['scale'] + pl.get('z', 0) * 0.2
        chars.append((f, pl))
        cols.update({f'{name}.{k}': c for k, c in col.items()})
        f.mat_prefix = name
    d.add(build.render_people(chars, v, (0, 0, w, h), cols))
    return d


def main():
    jobs = []
    for n in NEW:
        jobs.append((f'portrait-{n}', lambda n=n: build.portrait(n, **getattr(NEW[n], 'PORTRAIT', {}))))
        jobs.append((f'figure-{n}', lambda n=n: build.figure(n)))
        jobs.append((f'turn-{n}', lambda n=n: build.turnaround(n, **getattr(NEW[n], 'TURN', {}))))
        jobs.append((f'expr-{n}', lambda n=n: expressions(n)))
    jobs.append(('cast-six', six_picture))
    for name, fn in jobs:
        if not FILTER or FILTER in name:
            build.save(fn(), name)


if __name__ == '__main__':
    main()
