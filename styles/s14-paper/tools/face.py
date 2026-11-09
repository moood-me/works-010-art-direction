"""С14 — the head: a face glued from a few pieces of paper.

Head space: the centre of the face piece is (0, 0), the face is about 2*ry tall (ry ≈ 100), y grows down.
yaw: 0 — front, 0.5 — three-quarter (turned to the viewer's right), 1 — profile to the right. Turn left with mirror().

A character is a `spec` (dict, see DEFAULT) plus its own hair pieces; `face()` returns the pieces of the face itself:
ears, face piece, cheeks, eyes with lids, brows, nose, mouth.
"""
import math
from kit import *

DEFAULT = dict(
    skin='#f0c9a4', rx=80, ry=100, jaw=0.62, chin=0.0,          # face piece: half-width, half-height, jaw width, extra chin
    eye_y=10, eye_gap=36, eye_w=15, eye_h=13,                   # eyes: height on the face, half-distance, half-sizes
    iris='#6b4a2f', lid=None, lash=False, lash_col='#33241f',
    brow='#6b4a2f', brow_w=7, brow_len=30, brow_y=-30, brow_kind='card',
    nose='button', nose_y=38, nose_s=1.0,
    mouth_y=62, mouth_w=22, lip='#b8483f', inside='#5c1a22',
    cheek='#e8748a', cheek_r=17, cheek_op=0.42,
    ear=1.0, neck_w=34,
    rest={},                                                    # this character's own «calm» (overrides EXPR['calm'])
)

# open: how far the upper lid is lifted (0.5 — half-closed, 1 — wide); tilt: lid slope (+ outer corner down — sad);
# brow: tilt (+ inner end up — sad, − inner end down — angry), brow_dy; mouth: the kind of mouth piece; low: lower lid
EXPR = {
    'calm':     dict(open=0.78, tilt=0.0, brow=0.0, brow_dy=0, mouth='smile', low=0.0, eye=1.0),
    'joy':      dict(open=0.80, tilt=0.0, brow=0.1, brow_dy=-6, mouth='grin', low=0.55, eye=1.0),
    'laugh':    dict(open=0.0, tilt=0.0, brow=0.15, brow_dy=-8, mouth='laugh', low=0.0, eye=1.0),
    'surprise': dict(open=1.1, tilt=0.0, brow=0.12, brow_dy=-15, mouth='o', low=0.0, eye=1.12),
    'sad':      dict(open=0.62, tilt=0.5, brow=0.55, brow_dy=-3, mouth='frown', low=0.0, eye=1.0),
    'angry':    dict(open=0.60, tilt=-0.55, brow=-0.6, brow_dy=9, mouth='grit', low=0.25, eye=0.95),
    'smirk':    dict(open=0.55, tilt=-0.1, brow=-0.15, brow_dy=3, mouth='smirk', low=0.0, eye=1.0),
    'tired':    dict(open=0.58, tilt=0.15, brow=0.1, brow_dy=0, mouth='flat', low=0.0, eye=1.0),
    'grump':    dict(open=0.62, tilt=-0.3, brow=-0.35, brow_dy=6, mouth='frown', low=0.15, eye=1.0),
}


def expr_of(spec, name):
    e = dict(EXPR['calm'])
    if name in (None, 'calm'):
        e.update(spec.get('rest', {}))
    elif isinstance(name, dict):
        e.update(spec.get('rest', {}))
        e.update(name)
    else:
        e.update(EXPR[name])
        e.update(spec.get('on', {}).get(name, {}))
    return e


def outline(spec, yaw=0):
    """The face piece. Front: an egg with a jaw; three-quarter: the far cheek pulled in; profile: skull + face."""
    rx, ry, jaw, chin = spec['rx'], spec['ry'], spec['jaw'], spec['chin']
    if yaw < 0.75:
        pts = []
        n = 18
        for i in range(n):
            a = 2 * math.pi * i / n - math.pi / 2
            x, y = math.cos(a), math.sin(a)
            wdt = 1.0
            if y > 0:
                wdt = 1 - (1 - jaw) * y ** 1.7
                y = y * (1 + chin * y ** 3)
            px = rx * x * wdt
            if yaw:                                            # far side (right) narrower, back of the head fuller
                px = px * (0.84 if px > 0 else 1.05) + rx * 0.05
                if px > 0 and y > 0.2:
                    px *= 1 - 0.10 * y
            pts.append((px, ry * y))
        return pts
    c = 1 + chin
    return [(-rx * 0.15, -ry), (rx * 0.42, -ry * 0.9), (rx * 0.78, -ry * 0.5), (rx * 0.84, -ry * 0.05),
            (rx * 0.80, ry * 0.32), (rx * 0.74, ry * 0.62), (rx * 0.6, ry * 0.9 * c), (rx * 0.3, ry * 1.0 * c),
            (-rx * 0.1, ry * 0.86 * c), (-rx * 0.35, ry * 0.55), (-rx * 0.82, ry * 0.42), (-rx * 1.08, ry * 0.0),
            (-rx * 1.0, -ry * 0.5), (-rx * 0.65, -ry * 0.88)]


def place(spec, yaw):
    """Where the features sit for this turn: centre line shift, near/far eye x and squeeze."""
    rx, g = spec['rx'], spec['eye_gap']
    if yaw < 0.25:
        return dict(s=0, eyes=[(-g, 1.0, -1), (g, 1.0, 1)], nose_x=0, mouth_x=0, mouth_k=1.0)
    if yaw < 0.75:
        s = rx * 0.20
        return dict(s=s, eyes=[(s - g * 0.98, 1.0, -1), (s + g * 0.86, 0.74, 1)], nose_x=s * 1.9, mouth_x=s * 1.25, mouth_k=0.9)
    return dict(s=rx * 0.5, eyes=[(rx * 0.40, 0.62, -1)], nose_x=rx * 0.80, mouth_x=rx * 0.56, mouth_k=0.5)


def eye(cx, cy, w, h, spec, e, side, yaw=0):
    """White, iris, pupil, a light speck; the upper lid — a piece of skin-coloured paper that casts a shadow on the eye."""
    w, h = w * e['eye'], h * e['eye']
    lid_c = spec['lid'] or mix(spec['skin'], '#c97a6a', 0.30)
    o = e['open']
    if o <= 0.05:                                              # eye shut by laughter: a dark sliver, arch up
        return [card(crescent(cx - w * 1.05, cy + h * 0.25, cx + w * 1.05, cy + h * 0.25, -h * 0.75, h * 0.42), spec['lash_col'], 1)]
    out = [card(ell(cx, cy, w, h, n=10), '#fbf6ea', 1)]
    look = e.get('look', 0) * w * 0.3 + (w * 0.12 if yaw else 0)
    ir = min(h * 0.82, w * 0.62)
    iy = cy + h * 0.06 + e.get('look_y', 0) * h * 0.3
    out += [flat(ell(cx + look, iy, ir, ir, n=10), spec['iris']),
            flat(ell(cx + look, iy, ir * 0.52, ir * 0.52, n=8), '#241a1c'),
            flat([corner(p) for p in ell(cx + look - ir * 0.38, iy - ir * 0.42, ir * 0.27, ir * 0.27, rot=20, n=4)], '#fffaf0')]
    # the upper lid: from an arch above the eye down to the lid edge
    k = (2 * min(o, 1.0) - 1)
    tilt = e['tilt'] * side
    n = 9
    edge, top = [], []
    for i in range(n):
        t = i / (n - 1)
        s = math.sin(math.pi * t)
        x = cx - w * 1.16 + 2.32 * w * t
        edge.append((x, cy + h * 0.12 - (h * k + h * 0.12) * s + tilt * h * (t - 0.5) * 1.5))
        top.append((x, cy + h * 0.12 - h * 1.42 * s ** 0.75 - h * 0.05))
    if o < 1.05:
        lid = [corner(top[0])] + top[1:-1] + [corner(top[-1])] + edge[-2:0:-1]
        out.append(card(lid, lid_c, 1))
        if spec['lash']:                                       # lashes: one dark sliver under the lid edge, flicked at the outer end
            th = h * 0.26
            low = [(x, y + th * math.sin(math.pi * i / (n - 1)) ** 0.6) for i, (x, y) in enumerate(edge)]
            oi = -1 if side > 0 else 0
            ox, oy = edge[oi]
            flick = (ox + side * w * 0.34, oy - h * 0.42, 1)
            body = edge + low[-2:0:-1] if side < 0 else edge + low[-2:0:-1]
            body = list(body)
            if side > 0:
                body = edge[:-1] + [flick, (ox, oy + th * 0.5)] + low[-2:0:-1]
            else:
                body = [flick] + edge[1:] + low[-2:0:-1] + [(ox, oy + th * 0.5)]
            out.append(flat(body, spec['lash_col']))
    if e['low'] > 0:                                           # the cheek pushes the lower lid up
        lo = e['low']
        up_ = [(cx - w * 1.25 + 2.5 * w * i / (n - 1), cy + h * (1.05 - 0.95 * lo * math.sin(math.pi * i / (n - 1)))) for i in range(n)]
        dn_ = [(cx - w * 1.25 + 2.5 * w * i / (n - 1), cy + h * (1.05 + 0.55 * math.sin(math.pi * i / (n - 1)))) for i in range(n)]
        out.append(card([corner(up_[0])] + up_[1:-1] + [corner(up_[-1])] + dn_[-2:0:-1], mix(spec['skin'], '#e8a79a', 0.12), 1))
    return out


def brow(cx, cy, spec, e, side, k=1.0):
    L, w = spec['brow_len'] * k, spec['brow_w']
    tl = e['brow']
    # inner end at -side, outer end at +side
    xi, xo = cx - side * L * 0.5, cx + side * L * 0.55
    yi = cy + e['brow_dy'] - tl * 13
    yo = cy + e['brow_dy'] + tl * 6 + 3
    arch = -4 - (3 if tl >= 0 else -2)
    pts = strip([(xi, yi), ((xi + xo) / 2, (yi + yo) / 2 + arch), (xo, yo)], [w, w * 0.9, w * 0.35])
    f = torn if spec['brow_kind'] == 'torn' else card
    return f(pts, spec['brow'], 1)


def nose(x, y, spec, yaw):
    """A separate little piece standing on the face; in profile it sticks out past the edge of the face piece."""
    s, kind = spec['nose_s'], spec['nose']
    c = mix(spec['skin'], '#d98a6c', 0.32)
    if yaw >= 0.75:
        if kind == 'button':
            pts = [(x - 10 * s, y - 20 * s), (x + 12 * s, y - 2 * s), (x + 13 * s, y + 6 * s), (x + 2 * s, y + 10 * s), (x - 12 * s, y + 8 * s)]
        else:
            pts = [(x - 8 * s, y - 44 * s, 1), (x + 20 * s, y - 2 * s), (x + 20 * s, y + 7 * s), (x + 6 * s, y + 12 * s), (x - 14 * s, y + 9 * s)]
        return [card(pts, c, 2)]
    lean = 0 if yaw < 0.25 else 1
    if kind == 'button':
        return [card(ell(x, y, 9.5 * s, 8 * s, n=8), c, 2)]
    if kind == 'broad':
        return [card([(x - 6 * s + lean * 4, y - 26 * s), (x + 4 * s + lean * 5, y - 22 * s), (x + 17 * s + lean * 4, y + 2 * s),
                      (x + 12 * s + lean * 3, y + 11 * s), (x, y + 13 * s), (x - 14 * s, y + 10 * s), (x - 17 * s, y + 1 * s)], c, 2)]
    if kind == 'long':
        return [card([(x - 4 * s + lean * 3, y - 40 * s), (x + 5 * s + lean * 5, y - 36 * s), (x + 11 * s + lean * 7, y - 2 * s),
                      (x + 9 * s + lean * 5, y + 9 * s), (x, y + 12 * s), (x - 10 * s, y + 8 * s), (x - 10 * s, y - 2 * s)], c, 2)]
    # 'wedge': a small soft triangle
    return [card([(x - 2 * s + lean * 3, y - 22 * s), (x + 4 * s + lean * 5, y - 18 * s), (x + 9 * s + lean * 5, y + 3 * s),
                  (x + 1 * s + lean * 2, y + 9 * s), (x - 8 * s, y + 4 * s)], c, 2)]


def mouth(x, y, spec, e, k=1.0, yaw=0):
    """The mouth is cut out: a sliver for a closed one; an open one is a dark piece with teeth and a tongue glued in."""
    w, kind = spec['mouth_w'] * k, e['mouth']
    lip, inside = spec['lip'], spec['inside']
    prof = yaw >= 0.75
    x0, x1 = (x - w, x + w) if not prof else (x - w * 1.6, x + w * 0.5)

    def lens(up, lo, n=11):
        a = [(x0 + (x1 - x0) * i / (n - 1), y + up(i / (n - 1))) for i in range(n)]
        b = [(x0 + (x1 - x0) * i / (n - 1), y + lo(i / (n - 1))) for i in range(n)]
        return [corner(a[0])] + a[1:-1] + [corner(a[-1])] + b[-2:0:-1]
    S = lambda t: math.sin(math.pi * t)
    if kind == 'smile':
        return [card(lens(lambda t: w * 0.30 * S(t), lambda t: w * 0.30 * S(t) + w * 0.26 * S(t)), lip, 1)]
    if kind == 'flat':
        return [card(lens(lambda t: -w * 0.03 * S(t), lambda t: w * 0.17 * S(t)), lip, 1)]
    if kind == 'frown':
        return [card(lens(lambda t: -w * 0.34 * S(t), lambda t: -w * 0.34 * S(t) + w * 0.24 * S(t)), lip, 1)]
    if kind == 'smirk':                                        # one corner pulled up
        up = lambda t: -w * 0.42 * t ** 2.2 + w * 0.10 * S(t)
        return [card(lens(up, lambda t: up(t) + w * 0.22 * S(t)), lip, 1)]
    if kind == 'pout':
        return [card(ell(x, y, w * 0.42, w * 0.26, n=8), lip, 1)]
    if kind == 'o':
        return [card(ell(x, y + w * 0.25, w * 0.50, w * 0.66, n=10), inside, 1),
                flat(ell(x, y + w * 0.62, w * 0.30, w * 0.22, n=8), '#d9606a')]
    if kind == 'grit':                                         # anger: a frowning mouth with clenched teeth
        up = lambda t: -w * 0.30 * S(t)
        lo = lambda t: -w * 0.30 * S(t) + w * 0.50 * S(t) ** 0.7
        m = [card(lens(up, lo), inside, 1)]
        m.append(flat(lens(lambda t: up(t) + (lo(t) - up(t)) * 0.18, lambda t: up(t) + (lo(t) - up(t)) * 0.82), '#fbf6ea'))
        return m
    # 'grin' and 'laugh': open, upper teeth, tongue
    deep = w * (0.78 if kind == 'grin' else 1.15)
    up = lambda t: w * 0.10 * S(t)
    lo = lambda t: w * 0.10 * S(t) + deep * S(t) ** 0.8
    m = [card(lens(up, lo), inside, 1)]
    m.append(flat(lens(up, lambda t: up(t) + (lo(t) - up(t)) * 0.36), '#fbf6ea'))
    m.append(flat(lens(lambda t: lo(t) - (lo(t) - up(t)) * (0.42 * S(t) ** 2), lo), '#d9606a'))
    return m


def ear(x, y, spec, side, s=1.0):
    r = 15 * spec['ear'] * s
    c = mix(spec['skin'], '#d98a6c', 0.18)
    return [card(ell(x, y, r * 0.8, r * 1.25, rot=-8 * side, n=8), c, 1),
            flat(ell(x + side * r * 0.1, y + r * 0.1, r * 0.36, r * 0.7, rot=-8 * side, n=6), mix(spec['skin'], '#c0705c', 0.42))]


def face(spec, yaw=0, expr=None, extras=None, glasses=None):
    """Ears, the face piece, cheeks, eyes, brows, nose, mouth. extras: pieces between the skin and the features
    (wrinkles, freckles). Returns a dict of layers so that a character can slip its hair between them."""
    sp = dict(DEFAULT)
    sp.update(spec)
    e = expr_of(sp, expr)
    pl = place(sp, yaw)
    rx, ry = sp['rx'], sp['ry']
    ey = sp['eye_y']
    ears = []
    if sp['ear']:
        if yaw < 0.25:
            ears = ear(-rx * 0.99, ey + 12, sp, -1) + ear(rx * 0.99, ey + 12, sp, 1)
        elif yaw < 0.75:
            ears = ear(-rx * 0.92, ey + 12, sp, -1)
    skin = [card(outline(sp, yaw), sp['skin'], 2)]
    on = []
    if sp['ear'] and yaw >= 0.25:                              # the ear lies on the face piece when the head turns
        ex = -rx * 0.50 if yaw < 0.75 else -rx * 0.22
        on = ear(ex, ey + 12, sp, -1, 1.1) if yaw >= 0.75 else []
    feats = []
    cr = sp['cheek_r']
    for (x, kx, side) in pl['eyes']:
        far = kx < 1 and side > 0 and yaw < 0.75
        cxk = x + side * sp['eye_gap'] * 0.42 if not far else x - 9
        cyk = ey + ry * 0.36 - (4 if e['low'] > 0.3 else 0)
        if yaw >= 0.75:
            cxk = x - sp['eye_gap'] * 0.5
        feats.append(tissue(ell(cxk, cyk, cr * (0.5 if far else 1), cr * (0.85 if far else 1), n=10), sp['cheek'], sp['cheek_op']))
    for (x, kx, side) in pl['eyes']:
        feats += eye(x, ey, sp['eye_w'] * kx, sp['eye_h'], sp, e, side, yaw)
        bx = x + (side * 2 if yaw < 0.75 else 4)
        feats.append(brow(bx, ey + sp['brow_y'], sp, e, side if yaw < 0.75 else 1, kx if yaw < 0.75 else 0.75))
    nz = nose(pl['nose_x'], sp['nose_y'], sp, yaw)
    mo = mouth(pl['mouth_x'], sp['mouth_y'], sp, e, pl['mouth_k'], yaw)
    return dict(ears=ears, skin=skin, on=on, extras=extras or [], feats=feats, nose=nz, mouth=mo, spec=sp, place=pl, expr=e)


def neck(spec, yaw=0, length=40, dx=0):
    sp = dict(DEFAULT)
    sp.update(spec)
    w, ry = sp['neck_w'], sp['ry']
    x = (-sp['rx'] * 0.12 if yaw >= 0.75 else (sp['rx'] * 0.04 if yaw else 0))
    c = mix(sp['skin'], '#c0705c', 0.20)
    return [card([(x - w, ry * 0.6, 1), (x + w, ry * 0.6, 1), (x + w + dx, ry + length, 1), (x - w + dx, ry + length, 1)], c, 1)]


def turn(tree, spec):
    """Front-view pieces lying on the head (hair, a beard) → the same for the three-quarter view: the far side
    pulled in like the face piece, the middle carried along with the features."""
    rx = spec.get('rx', DEFAULT['rx'])
    s = rx * 0.20

    def f(x, y):
        u = max(-1.0, min(1.0, x / rx))
        return ((x * 0.84 if x > 0 else x * 1.05) + rx * 0.05 + s * (1 - u * u) * 0.9, y)
    from kit import _map
    return _map(tree, f)


def stack(f, back=None, mid=None, front=None, top=None):
    """Glue order of a head: hair behind, ears, face, [mid: hair lying on the skin under the features], features,
    [front: fringe over the brows], nose and mouth stay visible; top: things over everything (glasses, a loupe)."""
    return [back or [], f['ears'], f['skin'], f['on'], f['extras'], mid or [], f['feats'], f['mouth'], f['nose'], front or [], top or []]
