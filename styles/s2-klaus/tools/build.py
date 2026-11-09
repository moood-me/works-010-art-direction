"""Build every drawing of the page: svg/*.svg and pics/*.png.  python3 tools/build.py [name-filter]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import Doc, Light, bg, render, mix
import anya, savely, tim, vera, marat, kira

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG, PNG = os.path.join(HERE, 'svg'), os.path.join(HERE, 'pics')
os.makedirs(SVG, exist_ok=True)
os.makedirs(PNG, exist_ok=True)
FILTER = sys.argv[1] if len(sys.argv) > 1 else ''

FOUR = ('anya', 'savely', 'tim', 'vera')
CAST = {'anya': anya, 'savely': savely, 'tim': tim, 'vera': vera, 'marat': marat, 'kira': kira}
# each one's backdrop and how high the shoulders sit under the head
BACK = {
    'anya':   dict(top='#2c2744', bottom='#4c3150', glow='#e8985a', dy=-68),
    'savely': dict(top='#2e2230', bottom='#4a3030', glow='#f0a050', dy=-44),
    'tim':    dict(top='#24304a', bottom='#3c3a52', glow='#e8a060', dy=-66),
    'vera':   dict(top='#222838', bottom='#3a3448', glow='#d89070', dy=-60),
    'marat':  dict(top='#2e2430', bottom='#4a302c', glow='#f09a48', dy=-30),
    'kira':   dict(top='#1e2236', bottom='#34283e', glow='#c88a78', dy=-106),
}


def light():
    return Light(-0.85, -0.5, key='#ffc47a', shade='#3a2a5a')


def save(d, name):
    if FILTER and FILTER not in name:
        return
    d.grain(0.12)
    p = os.path.join(SVG, name + '.svg')
    d.save(p)
    render(p, os.path.join(PNG, name + '.png'), d.w, d.h)
    print(name)


def over(m, bust, d, out, dy):
    """What a character wears over the neck (a kerchief, a hood's edge, headphones): `<bust>_over`, drawn after
    the head, if the character's module has it."""
    fn = getattr(m, bust + '_over', None)
    if fn:
        out.append(f'<g transform="translate(0,{dy})">')
        fn(d, out)
        out.append('</g>')


def portrait(name, expr='calm', flat=False):
    m, b = CAST[name], BACK[name]
    d = Doc(500, 600, light())
    d.flat = flat
    bg(d, b['top'], b['bottom'], glow=b['glow'], gx=0.15, gy=0.35, gr=0.65)
    out = [f'<g transform="translate(0,{b["dy"]})">']
    m.bust(d, out)
    out.append('</g>')
    m.head34(d, out, expr)
    over(m, 'bust', d, out, b['dy'])
    for s in out:
        d.add(s)
    return d


def figure(name):
    m, b = CAST[name], BACK[name]
    d = Doc(500, 900, light())
    bg(d, b['top'], b['bottom'], glow=b['glow'], gx=0.15, gy=0.3, gr=0.7)
    d.add(f'<rect y="790" width="500" height="110" fill="{mix(b["bottom"], "#000000", 0.25)}" opacity="0.6"/>')
    out = []
    m.figure(d, out)
    for s in out:
        d.add(s)
    return d


def turnaround(name):
    m, b = CAST[name], BACK[name]
    d = Doc(1500, 600, light())
    bg(d, b['top'], b['bottom'], glow=b['glow'], gx=0.2, gy=0.35, gr=0.8)
    out = []
    for i, (fn, bf) in enumerate((('head_front', 'bust_front'), ('head34', 'bust'), ('head_side', 'bust_side'))):
        out.append(f'<g transform="translate({i*500},0)">')
        out.append(f'<g transform="translate(0,{b["dy"]})">')
        getattr(m, bf)(d, out)
        out.append('</g>')
        getattr(m, fn)(d, out, 'calm')
        over(m, bf, d, out, b['dy'])
        out.append('</g>')
    for s in out:
        d.add(s)
    return d


def expressions(name):
    m, b = CAST[name], BACK[name]
    d = Doc(2000, 600, light())
    bg(d, b['top'], b['bottom'], glow=b['glow'], gx=0.2, gy=0.35, gr=0.8)
    out = []
    for i, ex in enumerate(('joy', 'surprise', 'sad', 'anger')):
        out.append(f'<g transform="translate({i*500},0)">')
        out.append(f'<g transform="translate(0,{b["dy"]})">')
        m.bust(d, out)
        out.append('</g>')
        m.head34(d, out, ex)
        over(m, 'bust', d, out, b['dy'])
        out.append('</g>')
    for s in out:
        d.add(s)
    return d


def cast(places=(('vera', 420, True), ('savely', 680, True), ('anya', 1110, False), ('tim', 1350, False))):
    """The cast together, round a street lantern at dusk: those on the left are turned to the right
    (mirrored), so each is lit from the lantern's side. places: (name, x of the figure's middle, mirrored)."""
    W, H = 1800, 900
    d = Doc(W, H, light())
    bg(d, '#232a44', '#3a3550')
    j = 'lantern'
    d.defs.append(f'<radialGradient id="{j}" cx="0.5" cy="0.3" r="0.55"><stop offset="0" stop-color="#ffb060" stop-opacity="0.85"/>'
                  f'<stop offset="0.45" stop-color="#e07a50" stop-opacity="0.3"/><stop offset="1" stop-color="#e07a50" stop-opacity="0"/></radialGradient>')
    d.add(f'<rect width="{W}" height="{H}" fill="url(#{j})"/>')
    # far houses, snow-blue, simple big shapes
    d.add('<path d="M0,560 L0,420 L90,360 L180,420 L180,380 L300,300 L420,380 L420,560Z" fill="#2c3352" opacity="0.9"/>')
    d.add('<path d="M1380,560 L1380,360 L1500,280 L1620,360 L1620,400 L1700,340 L1800,400 L1800,560Z" fill="#2c3352" opacity="0.9"/>')
    for x, y in ((120, 450), (330, 400), (1460, 380), (1560, 420), (1720, 440)):
        d.add(f'<rect x="{x}" y="{y}" width="22" height="30" fill="#f0a860" opacity="0.8"/>')
    # ground, snow
    d.add('<path d="M0,780 C400,760 1400,760 1800,780 L1800,900 L0,900Z" fill="#c8b8c8"/>')
    d.add('<path d="M0,780 C400,760 1400,760 1800,780 L1800,800 C1400,790 400,790 0,800Z" fill="#f0d8c0" opacity="0.6"/>')
    d.add('<ellipse cx="900" cy="800" rx="520" ry="50" fill="#ffc890" opacity="0.35" filter="url(#%s)"/>' % d.blur(20))
    # the lantern

    d.add('<path d="M894,800 L894,250 L906,250 L906,800Z" fill="#1e1a28"/>')
    d.add('<path d="M876,250 L924,250 L916,190 L884,190Z" fill="#ffd890"/><path d="M870,190 L930,190 L900,166Z" fill="#1e1a28"/>')
    d.add('<circle cx="900" cy="222" r="70" fill="#ffd090" opacity="0.35" filter="url(#%s)"/>' % d.blur(14))
    out = []
    # scale every figure to the scene; the ground in figures is y=846
    s = 0.86
    for name, x, mirror in places:
        tx = x
        ty = 800 - 846 * s
        if mirror:
            out.append(f'<g transform="translate({tx + 250*s},{ty}) scale({-s},{s})">')
        else:
            out.append(f'<g transform="translate({tx - 250*s},{ty}) scale({s})">')
        CAST[name].figure(d, out)
        out.append('</g>')
    for o in out:
        d.add(o)
    # falling snow
    import random
    rnd = random.Random(3)
    for _ in range(90):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, 760), rnd.uniform(1.2, 3.2)
        d.add(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#fff4ea" opacity="{rnd.uniform(0.35, 0.8):.2f}"/>')
    return d


SIX = (('vera', 270, True), ('kira', 490, True), ('savely', 720, True),
       ('anya', 1070, False), ('marat', 1330, False), ('tim', 1610, False))

def eye_rule():
    """A close look at one eye: white, big dark iris, heavy lid with its shadow, the lash line wrapping past the
    outer corner, the brow set far above."""
    from parts import eye, brow
    d = Doc(600, 300, light())
    bg(d, '#2c2744', '#4c3150')
    out = []
    out.append(f'<rect x="0" y="0" width="600" height="300" fill="{anya.SKIN}"/>')
    out.append('<g transform="translate(-551,-627) scale(3.2)">')
    out.append(d.tone('M150,200 L300,200 L300,300 L150,300Z', '#000', 0))
    out.append(eye(d, 266, 246, 18, 16, irr=0.9, lid=0.38, look=(-0.32, -0.12), tilt=1.5, skin=anya.SKIN,
                   iris='#7a4424', crease=0.3))
    out.append(brow((244, 220), (268, 208), (298, 220), 4.2, mix(anya.HAIR, '#2a1a1c', 0.35)))
    out.append('</g>')
    for o in out:
        d.add(o)
    return d


if __name__ == '__main__':
    for n in FOUR:
        save(portrait(n), f'portrait-{n}')
        save(figure(n), f'figure-{n}')
    save(turnaround('anya'), 'turn-anya')
    save(turnaround('tim'), 'turn-tim')
    save(expressions('anya'), 'expr-anya')
    save(expressions('tim'), 'expr-tim')
    save(portrait('anya', flat=True), 'rule-flat')
    save(eye_rule(), 'rule-eye')
    save(cast(), 'cast')
    # round three: Марат and Кира
    for n in ('marat', 'kira'):
        save(portrait(n), f'portrait-{n}')
        save(figure(n), f'figure-{n}')
        save(turnaround(n), f'turn-{n}')
        save(expressions(n), f'expr-{n}')
    save(cast(SIX), 'cast-six')
