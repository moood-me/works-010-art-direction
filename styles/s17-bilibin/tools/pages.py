"""The sheets: a portrait (Mucha's halo inside Bilibin's border), a figure page (Bilibin's landscape inside the
border), the group frieze, turnarounds and expression sheets."""
import kit
from kit import Doc, INK, RED, GOLD, CREAM, _f


def portrait(mod, yaw=None, e=None, seed=1, w=800, h=1000):
    d = Doc(w, h, seed)
    fw = 30
    d.raw('<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (w, h, getattr(mod, 'FIELD', '#e6dcbf')))
    hc = mod.HALO
    with d.g(w / 2, 400, 1.0):
        kit.halo(d, 0, 0, 300, hc['ring'], hc['field'], hc['ink'])
    with d.g(w / 2, 400, 1.55):
        mod.bust(d, **({} if yaw is None else {'yaw': yaw}), **({} if e is None else {'e': e}))
    d.frame(0, 0, w, h, kind=getattr(mod, 'BORDER', 'rhomb'), ink=getattr(mod, 'BORDER_INK', RED), width=fw)
    return d


def figure(mod, seed=2, w=700, h=1200, scale=None, land=None):
    """A figure page: Bilibin's border, a flat landscape, the figure standing on the near field."""
    d = Doc(w, h, seed)
    fw = 28
    H = mod.HEIGHT
    s = scale or (h * 0.80) / 1460.0
    feet = h - fw - 60
    lc = dict(land or {})
    lc.setdefault('trees', 'firs')
    kit.landscape(d, fw, fw, w - 2 * fw, h - 2 * fw, horizon=0.55, seed=seed, **lc)
    # the page's side trees: a birch on one side, a fir on the other
    kit.birch(d, fw + 50, h - fw - 120, h * 0.9, 26, 6)
    kit.fir(d, w - fw - 70, h - fw - 100, h * 0.62)
    top = feet - (H - 112 + 112) * s
    with d.g(w / 2, top + 112 * s, s):
        mod.figure(d)
    kit.meadow(d, fw, feet - 10, w - 2 * fw, h - fw - feet + 10, seed)
    d.frame(0, 0, w, h, kind=getattr(mod, 'BORDER', 'rhomb'), ink=getattr(mod, 'BORDER_INK', RED), width=fw)
    return d


def label(d, x, y, text, size=30, color=INK):
    d.over.append('<text x="%s" y="%s" font-family="\'PT Serif\', Georgia, \'DejaVu Serif\', serif" font-size="%s" '
                  'font-weight="bold" letter-spacing="2" text-anchor="middle" fill="%s">%s</text>'
                  % (_f(x), _f(y), _f(size), color, text))


def panel(d, x, y, w, h, field='#e6dcbf', arch=True):
    """An arched panel (a terem window, a Mucha niche) with an ink rule: the field of one bust in a sheet."""
    r = w / 2
    pts = [(x, y + h, 'c'), (x, y + r, 'c')]
    import math
    for i in range(1, 12):
        a = math.pi + math.pi * i / 12
        pts.append((x + r + r * math.cos(a), y + r + r * math.sin(a)))
    pts += [(x + w, y + r, 'c'), (x + w, y + h, 'c')]
    d.fill(pts, field, n=4)
    return pts


def row(mods_views, labels, title_h=0, w=None, h=860, cell=520, scale=0.95, seed=3, field='#e6dcbf', halo=None):
    """A sheet of busts in arched niches side by side: a turnaround or an expression sheet.
    mods_views: [(module, kwargs for bust)]."""
    n = len(mods_views)
    fw = 26
    w = w or n * cell + 2 * fw + 40
    d = Doc(w, h, seed)
    d.raw('<rect width="%d" height="%d" fill="#d9ccaa"/>' % (w, h))
    for i, (mod, kw) in enumerate(mods_views):
        x0 = fw + 20 + i * cell
        pts = panel(d, x0 + 14, fw + 24, cell - 28, h - 2 * fw - 110, field)
        with d.clipped(pts, n=4):
            if halo:
                hc = mod.HALO
                with d.g(x0 + cell / 2, fw + 24 + 300, 1.0):
                    kit.halo(d, 0, 0, 200, hc['ring'], hc['field'], hc['ink'])
            with d.g(x0 + cell / 2, fw + 24 + 300, scale):
                mod.bust(d, **kw)
        d.ink(pts, closed=True, n=4)
        label(d, x0 + cell / 2, h - fw - 36, labels[i], 34)
    d.frame(0, 0, w, h, kind='rhomb', ink=RED, width=fw)
    return d


def group(mods, w=2400, h=1250, seed=5, scale=0.62, xs=None, title=None):
    """The cast standing together on a fairy-tale field inside the border."""
    d = Doc(w, h, seed)
    fw = 34
    kit.landscape(d, fw, fw, w - 2 * fw, h - 2 * fw, horizon=0.5, seed=seed, trees='firs')
    for bx in (fw + 60, w - fw - 80):
        kit.birch(d, bx, h - fw - 140, h * 0.92, 30, 8 if bx < w / 2 else -8)
    kit.fir(d, fw + 150, h - fw - 120, h * 0.5)
    kit.fir(d, w - fw - 170, h - fw - 120, h * 0.56)
    feet = h - fw - 90
    n = len(mods)
    xs = xs or [fw + 160 + (w - 2 * fw - 320) * i / (n - 1) for i in range(n)]
    for i, (mod, x) in enumerate(zip(mods, xs)):
        H = mod.HEIGHT
        top = feet - H * scale
        with d.g(x, top + 112 * scale, scale):
            mod.figure(d)
    kit.meadow(d, fw, feet - 10, w - 2 * fw, h - fw - feet + 10, seed)
    d.frame(0, 0, w, h, kind='rhomb', ink=RED, width=fw)
    return d
