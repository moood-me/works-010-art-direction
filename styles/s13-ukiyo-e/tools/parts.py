"""The print's way of drawing a head, a face and a hand — shared by every character.

A head is drawn in its own units: 200 high, the eye line at y = 0, the crown at -100, the chin near +100,
x = 0 the middle of the skull. Views: 'q' three-quarter (the print's usual view, the face turned to the left),
'f' front, 's' side (looking left). A character is a dict of numbers (see P) plus its own hair and extras.
"""
import math
from kit import INK, SKIN, RED


def P(**kw):
    p = dict(
        skin=SKIN, line=2.0,
        long=1.0,        # length of the lower face
        cheek=0.0,       # fullness of the cheek, px
        jaw=0.0,         # heaviness of the jaw corner
        chin=0.0,        # + broad, - pointed
        brow_ridge=0.0,  # side view: how far the brow stands out
        eye=dict(w=36, h=9, iris=7.2, lid=3.4, slant=-2.0, lower=0.5, white='#fbf6e8', color='#2e2422',
                 lash=0.0, y=0),
        brow=dict(kind='arc', w=2.6, len=40, arch=5, y=-25, tilt=0),
        nose=dict(kind='soft', s=1.0),
        mouth=dict(w=22, y=62, lip=RED, full=1.0),
        blush=('#e8a48a', 0.0),
        ear=1.0,
    )
    for k, v in kw.items():
        if isinstance(v, dict) and isinstance(p.get(k), dict):
            p[k] = dict(p[k], **v)
        else:
            p[k] = v
    return p


# what the face does: brows (lift up, tilt = inner ends up), eyes (open 0 = a laughing arc), mouth
EXPR = {
    'calm':     dict(lift=0, tilt=0, open=1.0, look=(0, 0), mouth='calm'),
    'dream':    dict(lift=1, tilt=1, open=0.8, look=(-1.5, -1.0), mouth='smile'),
    'joy':      dict(lift=3, tilt=0, open=0.0, look=(0, 0), mouth='laugh', blush=0.5),
    'surprise': dict(lift=11, tilt=2, open=1.6, look=(0, 0.5), mouth='o'),
    'sad':      dict(lift=1, tilt=8, open=0.7, look=(-1, 2.5), mouth='sad'),
    'anger':    dict(lift=-7, tilt=-9, open=0.85, look=(0, 0), mouth='frown'),
    'grin':     dict(lift=3, tilt=0, open=0.0, look=(0, 0), mouth='grin', blush=0.5),
    'smirk':    dict(lift=-2, tilt=-3, open=0.75, look=(4, 0), mouth='smirk'),
    'stern':    dict(lift=-3, tilt=-3, open=0.8, look=(0, 0), mouth='pressed'),
    'grump':    dict(lift=-5, tilt=-5, open=0.85, look=(-1, 0), mouth='frown'),
    'sly':      dict(lift=2, tilt=-2, open=0.9, look=(4, 0), mouth='smirk'),
}


def expr_of(e):
    return dict(EXPR['calm'], **(EXPR[e] if isinstance(e, str) else e))


# ---------------------------------------------------------------- the head's outline

def head_pts(p, view):
    L, ck, jw, ch = p['long'], p['cheek'], p['jaw'], p['chin']
    if view == 'q':
        return [(8, -100), (-38, -92), (-66, -66), (-78, -32), (-80, -10), (-77, 8), (-80 - ck * 0.4, 28),
                (-75 - ck, 52 * L), (-64 - ck * 0.7, 76 * L), (-50 - ch * 0.6, 93 * L), (-31, 100 * L),
                (-12 + ch, 96 * L), (13 + jw * 0.6 + ch * 0.5, 84 * L), (37 + jw, 62 * L + jw * 0.3),
                (53 + jw * 0.4, 30), (62, 0), (84, -20), (90, -50), (72, -84), (42, -98)]
    if view == 'f':
        half = [(0, -100), (40, -94), (70, -68), (82, -30), (82, 0), (80 + ck * 0.3, 28),
                (72 + ck * 0.8, 52 * L), (56 + ck * 0.5 + jw * 0.8, 78 * L), (30 + ch + jw * 0.3, 95 * L)]
        return half + [(0, 100 * L)] + [(-x, y) for x, y in half[:0:-1]]
    if view == 's':
        n = p['nose']['s']
        r = p['brow_ridge']
        return [(0, -100), (-40, -95), (-66, -76), (-78, -46), (-80 - r, -18), (-75, -2),
                (-80 - 4 * n, 14), (-87 - 8 * n, 27), (-85 - 7 * n, 34), (-77, 37, 'c'), (-78, 44),
                (-80, 51), (-76, 57 * L, 'c'), (-78, 63 * L), (-73, 71 * L), (-75 - ch * 0.4, 85 * L),
                (-64 - ch * 0.3, 97 * L), (-42, 97 * L + jw * 0.2), (-12 + jw * 0.3, 80 * L + jw * 0.3),
                (14 + jw * 0.5, 60 * L + jw * 0.3), (24, 30), (40, 20), (90, -8), (99, -45), (82, -82), (46, -98)]
    raise ValueError(view)


def layout(p, view):
    """Where the features sit: (near eye, far eye or None, mouth centre and its left/right share, ear)."""
    L = p['long']
    ey = p['eye']['y']
    my = p['mouth']['y'] * L
    if view == 'q':
        return dict(eyes=[(-4, ey, 1.0, -1), (-57, ey - 1, 0.6, 1)], brows=[(-4, 1.0, -1), (-58, 0.58, 1)],
                    mouth=(-46, my, 0.42, 0.58), ear=(60, 8), nose=(-41, 0))
    if view == 'f':
        return dict(eyes=[(33, ey, 1.0, -1), (-33, ey, 1.0, 1)], brows=[(34, 1.0, -1), (-34, 1.0, 1)],
                    mouth=(0, my, 0.5, 0.5), ear=(84, 8), nose=(0, 0))
    return dict(eyes=[(-46, ey, 0.62, -1)], brows=[(-48, 0.7, -1)], mouth=(-76, 57 * L, 0.0, 0.62),
                ear=(26, 6), nose=None)


# ---------------------------------------------------------------- features

def eye(d, p, cx, cy, k, inner, ex, view='q'):
    """An eye: a full upper lid drawn with pressure, a hair-thin lower lid, a dark iris half under the lid.
    k — its width against the near eye (the far eye of a three-quarter face is short);
    inner — the side of the inner corner (-1 left, +1 right)."""
    e = p['eye']
    w = e['w'] * k
    h = e['h'] * max(ex['open'], 0.0)
    sl = e['slant'] - ex['tilt'] * 0.35
    xi, xo = cx + inner * w / 2, cx - inner * w / 2
    lid = e['lid'] * (0.8 if k < 0.8 else 1.0)
    if ex['open'] <= 0.05:
        # laughing: the eye closes into an arc
        d.line([(xi, cy + 2), (cx + inner * w * 0.1, cy - e['h'] * 0.75), (xo, cy + 1 + sl * 0.3),
                (xo - inner * 3, cy + 4)], lid * 1.1, 'swell')
        if e['lash']:
            d.line([(xo, cy + 1), (xo - inner * 5, cy + 1)], lid * 0.5, 'taper')
        return
    up = [(xi, cy + h * 0.45), (xi - inner * w * 0.2, cy - h * 0.55), (cx - inner * w * 0.02, cy - h),
          (xo + inner * w * 0.12, cy - h * 0.45 + sl * 0.6), (xo, cy + sl)]
    lo = [(xo, cy + sl), (cx - inner * w * 0.15, cy + h * 0.72 + sl * 0.4), (cx + inner * w * 0.2, cy + h * 0.78),
          (xi, cy + h * 0.45)]
    opening = up + lo[1:-1]
    d.fill(opening, e['white'])
    cid = d.clip(opening)
    lx, ly = ex['look']
    if view == 's':
        lx += inner * w * 0.16
    ix, iy = cx + lx * k - inner * w * 0.03, cy - h * 0.2 + ly
    with d.g(clip=cid):
        d.dot(ix, iy, e['iris'] * (0.86 if k < 0.8 else 1.0), e['color'])
        d.dot(ix, iy, e['iris'] * 0.45, INK)
    d.line(up + [(xo - inner * (2 + e['lash'] * 4), cy + sl - e['lash'] * 2)], lid, 'swell', nib=0.1)
    if e['lower']:
        d.line(lo[:3] if view != 's' else lo, max(0.9, lid * 0.3), 'even', op=e['lower'], nib=0.0)
    if e.get('crease'):
        d.line([(xi - inner * w * 0.1, cy - h * 0.9 - 3), (cx, cy - h - 4.5), (xo + inner * w * 0.1, cy - h * 0.5 - 3 + sl)],
               1.0, 'swell', op=e['crease'], nib=0)
    if e.get('bag'):
        d.line([(xi - inner * w * 0.1, cy + h + 5), (cx, cy + h + 8), (xo + inner * w * 0.15, cy + h + 4)],
               1.0, 'swell', op=e['bag'], nib=0)


def brow(d, p, cx, k, inner, ex, cy=0):
    b = p['brow']
    L = b['len'] * k
    y = cy + b['y'] - ex['lift'] + p['eye']['y']
    tilt = b['tilt'] + ex['tilt']
    xi, xo = cx + inner * L / 2, cx - inner * L / 2
    yi, yo = y - tilt * 0.5, y + tilt * 0.35 + 2
    pts = [(xi, yi), (cx + inner * L * 0.1, y - b['arch'] - abs(tilt) * 0.1), (xo, yo)]
    if b['kind'] == 'arc':          # a thin high arc: the brow of the beauties
        d.line(pts, b['w'], 'swell', nib=0.1)
    elif b['kind'] == 'thick':      # pressed at the inner end, tailing off: Sharaku's brow
        d.line(pts, b['w'], 'taper', nib=0.15)
    elif b['kind'] == 'bushy':      # an old man's: a stroke and loose hairs over it
        col = b.get('color', INK)
        d.line(pts, b['w'], 'taper', nib=0.15, color=col)
        d.fringe(pts, length=b['w'] * 1.3, w=1.3, side=-inner, lean=-0.9 * inner, step=3.2, color=col)
        d.fringe(pts, length=b['w'] * 0.8, w=1.1, side=inner, lean=-0.9 * inner, step=4.5, color=col)


def nose(d, p, view, ex):
    """The nose is one stroke: down from beside the far eye, a hook at the tip (the print's hooked nose)."""
    nz = p['nose']
    s = nz['s']
    k = nz['kind']
    lw = p['line'] * 1.15
    if view == 'q':
        ox, oy = -41, -2 + p['eye']['y']

        def q(x, y):
            return (ox + x * s, oy + y * s)
        if k == 'soft':
            d.line([q(0, 0), q(-4, 16), q(-14, 32), q(-17, 38), q(-13, 43), q(-6, 42)], lw, 'even', nib=0.2)
            d.line([q(-3, 40), q(1, 37), q(4, 40)], lw * 0.8, 'taper', nib=0)
        elif k == 'snub':
            d.line([q(-6, 18), q(-13, 30), q(-15, 35), q(-11, 40), q(-5, 39)], lw, 'tail', nib=0.2)
            d.line([q(-2, 37), q(1, 35), q(3, 37)], lw * 0.8, 'taper', nib=0)
        elif k == 'long':
            d.line([q(1, -4), q(-3, 16), q(-13, 36), q(-17, 43), q(-12, 48), q(-5, 46)], lw, 'even', nib=0.2)
            d.line([q(-2, 44), q(3, 40), q(6, 44)], lw * 0.8, 'taper', nib=0)
        elif k == 'big':        # an old man's: a bent bridge, a heavy tip, the wing drawn
            d.line([q(1, -6), q(-4, 10), q(-12, 22), q(-21, 36), q(-23, 44), q(-17, 50), q(-8, 48)], lw * 1.2,
                   'even', nib=0.25)
            d.line([q(-8, 48), q(-2, 50), q(6, 46), q(8, 38), q(3, 34)], lw, 'taper', nib=0.1)
        elif k == 'broad':      # wide and short, wide wings
            d.line([q(0, 4), q(-5, 18), q(-16, 30), q(-22, 37), q(-19, 44), q(-10, 46)], lw * 1.2, 'even', nib=0.25)
            d.line([q(-10, 46), q(-2, 47), q(8, 44), q(11, 36), q(6, 30)], lw, 'taper', nib=0.1)
    elif view == 'f':
        oy = p['eye']['y']

        def f(x, y):
            return (x * s, oy + y * s)
        if k in ('soft', 'long', 'snub'):
            top = {'soft': 6, 'long': 0, 'snub': 22}[k]
            bot = {'soft': 38, 'long': 44, 'snub': 34}[k]
            d.line([f(-5, top), f(-6, bot - 14), f(-9, bot - 3), f(-5, bot + 1)], lw, 'tail', nib=0.2)
            d.line([f(-5, bot + 1), f(0, bot + 3), f(6, bot + 1)], lw * 0.9, 'swell', nib=0)
            d.line([f(8, bot - 1), f(11, bot - 4), f(9, bot - 8)], lw * 0.8, 'taper', nib=0)
        else:
            wdt = 15 if k == 'broad' else 12
            bot = 46 if k == 'big' else 42
            d.line([f(-6, 0), f(-7, bot - 18), f(-wdt, bot - 6), f(-wdt + 2, bot + 2), f(-6, bot + 2)], lw * 1.2,
                   'even', nib=0.2)
            d.line([f(-6, bot + 2), f(0, bot + 5), f(6, bot + 2)], lw, 'swell', nib=0)
            d.line([f(6, bot + 2), f(wdt - 1, bot + 1), f(wdt + 1, bot - 6), f(wdt - 4, bot - 12)], lw, 'taper',
                   nib=0.1)
    elif view == 's':
        # the profile carries the nose; only the wing is drawn
        n = s
        d.line([(-70 - 4 * n, 23), (-64 - 3 * n, 27), (-65 - 3 * n, 34), (-71 - 4 * n, 37)], lw * 0.9, 'swell',
               nib=0.1)


def mouth(d, p, view, ex, lay):
    m = p['mouth']
    mx, my, fl, fr = lay['mouth']
    w = m['w']
    kind = ex['mouth']
    lip = m['lip']
    full = m['full']
    xl, xr = mx - w * fl, mx + w * fr
    lw = p['line']
    side = view == 's'

    def lips(up=1.0, low=1.0, dy=0.0):
        if not lip:
            # a man's mouth: only a shadow stroke under the lower lip
            d.line([(mx - w * fl * 0.45, my + 7 + dy), (mx + (fr - fl) * w * 0.2, my + 8.5 + dy),
                    (mx + w * fr * 0.5, my + 6.5 + dy)], lw * 0.8, 'swell', nib=0, op=0.7)
            return
        if up:
            d.fill([(xl + w * 0.08, my + dy, 'c'), (mx - w * fl * 0.35, my - 3.6 * full * up + dy),
                    (mx + (fr - fl) * w * 0.1, my - 2.0 * full * up + dy), (mx + w * fr * 0.4, my - 3.6 * full * up + dy),
                    (xr - w * 0.08, my + dy, 'c'), (mx + (fr - fl) * w * 0.1, my + 0.8 + dy)], lip)
        if low:
            d.fill([(xl + w * 0.2, my + 0.5 + dy, 'c'), (mx + (fr - fl) * w * 0.1, my + 1.6 + dy),
                    (xr - w * 0.2, my + 0.5 + dy, 'c'), (mx + w * fr * 0.35, my + 5.5 * full * low + dy),
                    (mx - w * fl * 0.3, my + 5.5 * full * low + dy)], lip)

    if kind == 'calm':
        lips()
        d.line([(xl, my - 0.5), (mx - w * fl * 0.4, my + 0.8), (mx + (fr - fl) * w * 0.1, my + 0.2),
                (mx + w * fr * 0.5, my + 0.9), (xr, my - 0.8)], lw, 'swell', nib=0)
    elif kind == 'smile':
        lips()
        d.line([(xl - 1, my - 2.5), (mx - w * fl * 0.4, my + 1.0), (mx + (fr - fl) * w * 0.1, my + 1.2),
                (mx + w * fr * 0.5, my + 1.0), (xr + 2, my - 3.5)], lw, 'swell', nib=0)
    elif kind == 'pressed':
        lips(up=0.6, low=0.6)
        d.line([(xl - 1, my + 1.0), (mx, my), (xr + 2, my + 1.0)], lw * 1.25, 'even', nib=0)
        if not side:
            d.line([(xr + 2, my - 1.5), (xr + 3.5, my + 1), (xr + 2, my + 3.5)], lw * 0.7, 'swell', nib=0)
    elif kind == 'smirk':
        lips(up=0.7, low=0.8)
        d.line([(xl, my + 1.5), (mx, my + 0.8), (xr, my - 1.5), (xr + 4, my - 5)], lw * 1.15, 'tail', nib=0)
        d.line([(xr + 3, my - 8), (xr + 6.5, my - 5), (xr + 5, my - 1)], lw * 0.7, 'swell', nib=0)
    elif kind == 'sad':
        lips(up=0.8, low=1.0)
        d.line([(xl - 1, my + 3), (mx - w * fl * 0.4, my + 0.2), (mx + (fr - fl) * w * 0.1, my - 0.4),
                (mx + w * fr * 0.5, my + 0.4), (xr + 1, my + 3.5)], lw, 'swell', nib=0)
    elif kind == 'frown':
        # the へ mouth of Sharaku's actors: pulled down, a hook at each corner
        lips(up=0.5, low=0.8, dy=-1)
        d.line([(xl - 2, my + 6), (xl, my + 2.5), (mx - w * fl * 0.3, my - 1.5), (mx + (fr - fl) * w * 0.1, my - 2),
                (mx + w * fr * 0.5, my - 1), (xr, my + 3), (xr + 2.5, my + 7)], lw * 1.5, 'even', nib=0)
    elif kind in ('o', 'gasp'):
        r = w * (0.2 if kind == 'o' else 0.28)
        c = mx + (fr - fl) * w * 0.25
        if side:
            c = mx + r * 0.9
        shape = [(c - r * (0.75 if not side else 0.9), my + 2), (c, my - r * 0.75 + 1), (c + r * 0.8, my + 2),
                 (c, my + r * 1.5 + 2)]
        if lip:
            d.fill([(x + (x - c) * 0.45, y + (y - my - 2 - r * 0.3) * 0.5) for x, y in shape], lip)
        d.shape(shape, '#5a2420', lw * 0.8)
    elif kind in ('laugh', 'grin', 'snarl'):
        # an open mouth: dark red inside, a white row of teeth above, the tongue below
        big = {'laugh': 0.8, 'grin': 1.25, 'snarl': 0.9}[kind]
        L, R = xl - w * 0.18 * big, xr + w * 0.22 * big
        if side:
            L = mx + 1
        dep = (9 if kind == 'laugh' else 15 if kind == 'grin' else 7) * full
        cxm = (L + R) / 2 + (fr - fl) * w * 0.1
        if kind == 'snarl':
            top = [(L, my + 1, 'c'), (cxm - (R - L) * 0.2, my - 3), (cxm + (R - L) * 0.2, my - 3), (R, my + 2, 'c')]
            bot = [(cxm + (R - L) * 0.25, my + dep), (cxm - (R - L) * 0.2, my + dep)]
        else:
            top = [(L, my - 3.5, 'c'), (cxm - (R - L) * 0.2, my + 0.5), (cxm + (R - L) * 0.2, my + 0.5),
                   (R, my - 4.5, 'c')]
            bot = [(cxm + (R - L) * 0.3, my + dep * 0.8), (cxm, my + dep), (cxm - (R - L) * 0.28, my + dep * 0.8)]
        shape = top + bot
        d.fill(shape, '#5a2420')
        cid = d.clip(shape)
        with d.g(clip=cid):
            if kind == 'snarl':
                d.fill([(L - 2, my - 6), (R + 2, my - 6), (R + 2, my + dep + 3), (L - 2, my + dep + 3)], '#fbf6e8', n=1)
                d.line([(L, my + dep * 0.45), (R, my + dep * 0.5)], 1.2, 'even', nib=0)
                for i in range(1, 6):
                    x = L + (R - L) * i / 6
                    d.line([(x, my - 3), (x, my + dep)], 0.9, 'even', nib=0)
            else:
                d.fill([(L - 2, my - 8), (R + 2, my - 8), (R + 2, my + dep * 0.36), (cxm, my + dep * 0.44),
                        (L - 2, my + dep * 0.36)], '#fbf6e8')
                d.fill([(cxm - (R - L) * 0.32, my + dep + 2), (cxm - (R - L) * 0.12, my + dep * 0.6),
                        (cxm + (R - L) * 0.14, my + dep * 0.58), (cxm + (R - L) * 0.34, my + dep + 2)], '#cf6a55')
        d.contour(shape, lw * 0.9, nib=0.2)
        if lip:
            d.line([(L + 2, my + dep * 0.85 + 1.5), (cxm, my + dep + 3), (R - 3, my + dep * 0.85 + 1.5)], lw * 1.6,
                   'swell', color=lip, nib=0)
        if not side:
            # the laugh pushes the cheeks: a stroke at each corner
            d.line([(R + 1, my - 9), (R + 5, my - 3), (R + 3, my + 4)], lw * 0.8, 'swell', nib=0)
            d.line([(L - 1, my - 8), (L - 3.5, my - 3), (L - 2, my + 3)], lw * 0.7, 'swell', nib=0)


def ear(d, p, view, lay):
    s = p['ear']
    lw = p['line']
    if view == 'f':
        for sg in (1, -1):
            x0 = sg * 80
            pts = [(x0, -10), (x0 + sg * 8 * s, -16 * s), (x0 + sg * 13 * s, -4), (x0 + sg * 10 * s, 22 * s), (x0, 30 * s)]
            d.fill(pts + [(x0 - sg * 4, 10)], p['skin'])
            d.line(pts, lw, 'even', nib=0.2)
            d.line([(x0 + sg * 8 * s, -6 * s), (x0 + sg * 6 * s, 6), (x0 + sg * 3, 16 * s)], lw * 0.7, 'swell', nib=0)
        return
    ex, ey = lay['ear']
    k = s * (1.0 if view == 'q' else 1.15)
    pts = [(ex - 8 * k, ey - 16 * k), (ex + 2 * k, ey - 24 * k), (ex + 12 * k, ey - 16 * k), (ex + 12 * k, ey + 2 * k),
           (ex + 5 * k, ey + 20 * k), (ex - 4 * k, ey + 26 * k), (ex - 9 * k, ey + 16 * k)]
    d.fill(pts, p['skin'])
    d.line(pts, lw, 'even', nib=0.2)
    d.line([(ex - 2 * k, ey - 14 * k), (ex + 6 * k, ey - 12 * k), (ex + 6 * k, ey), (ex, ey + 8 * k), (ex - 3 * k, ey + 2 * k)],
           lw * 0.75, 'swell', nib=0)


def head(d, p, view='q', expr='calm', back=None, front=None, extra=None, under=None):
    """A whole head. back(d, view) — hair behind the skull; under(d, view, ex, lay) — a beard, under the
    features; extra(d, view, ex, lay) — moustache, wrinkles, glasses, over the face; front(d, view) — hair
    over everything."""
    ex = expr_of(expr)
    lay = layout(p, view)
    if back:
        back(d, view)
    pts = head_pts(p, view)
    ear(d, p, view, lay)
    d.fill(pts, p['skin'])
    bc, bo = p['blush']
    bo = bo + ex.get('blush', 0) * 0.5
    if bo > 0:
        cid = d.clip(pts)
        with d.g(clip=cid):
            if view == 'q':
                spots = [(14, 34, 30), (-62, 34, 20)]
            elif view == 'f':
                spots = [(46, 36, 28), (-46, 36, 28)]
            else:
                spots = [(-34, 36, 30)]
            for x, y, r in spots:
                d.bokashi([(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)], bc, None, None, bo,
                          radial=(x, y, r))
    d.contour(pts, p['line'], nib=0.3)
    if under:
        under(d, view, ex, lay)
    for (cx, cy, k, inner) in lay['eyes']:
        eye(d, p, cx, cy, k, inner, ex, view)
    for (cx, k, inner) in lay['brows']:
        brow(d, p, cx, k, inner, ex)
    nose(d, p, view, ex)
    mouth(d, p, view, ex, lay)
    if extra:
        extra(d, view, ex, lay)
    if front:
        front(d, view)
    return lay


def neck(d, p, view, w=46, length=70, lean=0, lw=None):
    """A neck under the head (drawn before the head): two lines with pressure."""
    L = p['long']
    cx = {'q': 14, 'f': 0, 's': 16}[view]
    y0 = 60 * L
    y1 = 100 * L + length
    pts = [(cx - w / 2, y0), (cx - w / 2 + 2 + lean * 0.3, y0 + (y1 - y0) * 0.5), (cx - w / 2 - 6 + lean, y1),
           (cx + w / 2 + 8 + lean, y1), (cx + w / 2 + lean * 0.3, y0 + (y1 - y0) * 0.5), (cx + w / 2 + 2, y0 - 20)]
    d.fill(pts, p['skin'])
    lw = lw or p['line']
    d.line(pts[0:3], lw, 'even')
    d.line(pts[5:2:-1], lw, 'even')


# ---------------------------------------------------------------- the hand

def _finger(d, base, ang, L, curl, wb, skin, lw, wt=0.6, joints=(0.42, 0.32, 0.26), nail=False):
    """A finger: a soft tapering shape bending in the plane, outlined, open at its root."""
    a = math.radians(ang)
    c = math.radians(curl)
    pts = [base]
    x, y = base
    for i, f in enumerate(joints):
        aa = a + c * i / max(1, len(joints) - 1)
        x, y = x + math.sin(aa) * L * f, y + math.cos(aa) * L * f
        pts.append((x, y))
    from kit import curve
    sm = curve(pts, False, 6)
    n = len(sm)
    left, right = [], []
    for i in range(n):
        A = sm[max(0, i - 1)]
        B = sm[min(n - 1, i + 1)]
        dx, dy = B[0] - A[0], B[1] - A[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        t = i / (n - 1)
        hw = 0.5 * wb * (1 - (1 - wt) * t ** 1.3)
        left.append((sm[i][0] + nx * hw, sm[i][1] + ny * hw))
        right.append((sm[i][0] - nx * hw, sm[i][1] - ny * hw))
    # a round tip
    tx, ty = sm[-1]
    dx, dy = sm[-1][0] - sm[-2][0], sm[-1][1] - sm[-2][1]
    ln = math.hypot(dx, dy) or 1
    hw = 0.5 * wb * wt
    tip = (tx + dx / ln * hw * 0.9, ty + dy / ln * hw * 0.9)
    outline = left + [tip] + right[::-1]
    d.out.append('<path d="%s" fill="%s"/>' % (__import__('kit').path_d(outline), skin))
    d.line([(q[0], q[1]) for q in outline[::2]] + [outline[-1]], lw, 'even', nib=0.15, n=3)
    if nail:
        d.line([(tx - dy / ln * hw * 0.6, ty + dx / ln * hw * 0.6), (tx - dx / ln * hw * 0.5, ty - dy / ln * hw * 0.5),
                (tx + dy / ln * hw * 0.6, ty - dx / ln * hw * 0.6)], lw * 0.6, 'swell', nib=0)
    return sm[-1]


# A pose: the palm's outline (wrist at the origin, the hand hanging down +y, 100 = wrist to middle fingertip),
# the strokes drawn on the palm's edge, and the fingers back to front:
# (base x, base y, angle from straight down (° towards +x), length, curl °, width).
HANDS = {
    # hanging loose, seen from the thumb's side: fingers stacked and curled forward (+x), the thumb in front
    'rest': dict(
        palm=[(-13, 0), (-16, 22), (-13, 46), (-2, 54), (12, 50), (17, 30), (13, 0)],
        edge=[[(-13, 0), (-16, 22), (-13, 46)], [(13, 0), (17, 22), (15, 36)]],
        fingers=[(-8, 44, 14, 30, 55, 12), (-3, 47, 11, 36, 50, 12.5), (3, 48, 8, 39, 44, 13), (9, 45, 4, 36, 36, 13)],
        thumb=(12, 18, 12, 32, 12, 14)),
    # open, the palm to us, fingers spread: the hand of Sharaku's actors
    'open': dict(
        palm=[(-15, 0), (-22, 24), (-23, 46), (-10, 54), (8, 54), (22, 46), (21, 22), (15, 0)],
        edge=[[(-15, 0), (-22, 24), (-23, 44)], [(15, 0), (20, 12)]],
        fingers=[(-17, 46, -22, 32, 5, 12.5), (-6, 51, -8, 39, 3, 13), (6, 51, 5, 41, -3, 13),
                 (17, 46, 20, 36, -5, 12.5)],
        thumb=(19, 16, 58, 34, -20, 15)),
    # holding a small thing between thumb and forefinger, the rest fanned out: the hand of Utamaro's beauties
    'pinch': dict(
        palm=[(-13, 0), (-17, 22), (-15, 42), (-5, 50), (9, 48), (16, 30), (13, 0)],
        edge=[[(-13, 0), (-17, 22), (-15, 40)], [(13, 0), (16, 20)]],
        fingers=[(-11, 42, -20, 30, 34, 11), (-6, 46, -12, 36, 40, 11.5), (0, 48, -3, 38, 48, 12),
                 (7, 46, 8, 34, 62, 12)],
        thumb=(13, 20, 26, 33, 30, 13.5)),
    # the hand closed round a handle that runs across it: knuckles in a row; drawn over the handle
    'grip': dict(
        palm=[(-14, 0), (-20, 20), (-20, 40), (-8, 50), (12, 50), (20, 38), (18, 18), (14, 0)],
        edge=[[(-14, 0), (-20, 20), (-20, 40)], [(14, 0), (18, 18), (20, 36)]],
        fingers=[(-16, 30, 60, 30, 95, 10.5), (-17, 39, 64, 33, 95, 11), (-15, 48, 68, 33, 95, 11),
                 (-11, 56, 72, 29, 95, 10)],
        thumb=(15, 14, -38, 34, -50, 12.5)),
    # a pointing / raised forefinger, the others folded
    'point': dict(
        palm=[(-14, 0), (-19, 22), (-18, 42), (-6, 50), (10, 48), (17, 30), (14, 0)],
        edge=[[(-14, 0), (-19, 22), (-18, 40)], [(14, 0), (17, 22)]],
        fingers=[(-13, 44, 30, 24, 150, 10), (-7, 48, 26, 26, 150, 10.5), (0, 50, 22, 27, 150, 11),
                 (8, 47, 2, 46, 4, 10.5)],
        thumb=(15, 22, 40, 30, 40, 12)),
}


def hand(d, x, y, s=1.0, rot=0, pose='rest', flip=False, skin=SKIN, lw=1.7, nails=False, fingers_only=False):
    """A hand at the wrist (x, y); rot turns it (0 = hanging down), flip mirrors it."""
    h = HANDS[pose]
    with d.g(x, y, s, rot, flip):
        if not fingers_only:
            d.fill(h['palm'], skin)
            for e in h['edge']:
                d.line(e, lw, 'even', nib=0.2)
        fs = h['fingers']
        th = h['thumb']
        if pose in ('rest', 'pinch', 'point'):
            for f in fs:
                _finger(d, (f[0], f[1]), f[2], f[3], f[4], f[5], skin, lw, nail=nails)
            _finger(d, (th[0], th[1]), th[2], th[3], th[4], th[5], skin, lw, joints=(0.55, 0.45), nail=nails)
        else:
            _finger(d, (th[0], th[1]), th[2], th[3], th[4], th[5], skin, lw, joints=(0.55, 0.45), nail=nails)
            for f in fs:
                _finger(d, (f[0], f[1]), f[2], f[3], f[4], f[5], skin, lw, nail=nails)


# ---------------------------------------------------------------- bodies

def tube(pts, ws):
    """The outline of a limb or a sleeve: a centre line with a width at each point."""
    n = len(pts)
    left, right = [], []
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        hw = ws[i] / 2
        left.append((pts[i][0] + nx * hw, pts[i][1] + ny * hw))
        right.append((pts[i][0] - nx * hw, pts[i][1] - ny * hw))
    return left + right[::-1]


def shoulders(view, w=150, drop=0, bottom=340, neck=40, top=150):
    """The outline of clothed shoulders under a head (head units), cut by the sheet's lower edge."""
    if view == 'f':
        half = [(neck, top), (w * 0.6, top + 28 + drop * 0.4), (w * 0.94, top + 66 + drop), (w + 4, top + 136 + drop),
                (w + 6, bottom)]
        return [(-x, y) for x, y in half[::-1]] + half
    if view == 'q':
        c = 14
        return [(c - w * 0.72, bottom), (c - w * 0.72, top + 112 + drop), (c - w * 0.6, top + 52 + drop),
                (c - neck * 1.1, top + 14), (c + neck * 0.9, top - 6), (c + w * 0.66, top + 32 + drop * 0.5),
                (c + w * 0.95, top + 72 + drop), (c + w * 1.03, top + 140 + drop), (c + w * 1.05, bottom)]
    c = 30
    return [(c - w * 0.5, bottom), (c - w * 0.52, top + 110), (c - w * 0.42, top + 50), (c - neck * 0.8, top + 12),
            (c + neck * 0.9, top - 4), (c + w * 0.42, top + 30 + drop * 0.5), (c + w * 0.56, top + 100 + drop),
            (c + w * 0.58, bottom)]


def flower(d, x, y, r=9, petal='#fbf6e8', heart='#d9a53c', n=5, rot=0, lw=1.2):
    for i in range(n):
        a = math.radians(360 / n * i + rot)
        px, py = x + math.cos(a) * r * 0.7, y + math.sin(a) * r * 0.7
        d.ellipse(px, py, r * 0.52, r * 0.52, INK)
    for i in range(n):
        a = math.radians(360 / n * i + rot)
        px, py = x + math.cos(a) * r * 0.7, y + math.sin(a) * r * 0.7
        d.ellipse(px, py, r * 0.52 - lw * 0.55 * d.lw, r * 0.52 - lw * 0.55 * d.lw, petal)
    d.dot(x, y, r * 0.3, heart)


def oval(cx, cy, rx, ry, n=10, rot=0, sq=0.0):
    """Points of an ellipse (sq > 0 squares it a little)."""
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        c, s_ = math.cos(a), math.sin(a)
        k = 1 + sq * abs(math.sin(2 * a))
        x, y = rx * c * k, ry * s_ * k
        r = math.radians(rot)
        out.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return out


def glasses(d, view, r=21, ry=None, y=2, lw=1.8, tint=0.22, sq=0.0, color=INK):
    """Wire glasses: two thin rings, a bridge, an arm to the ear."""
    ry = ry or r
    if view == 'q':
        lenses = [oval(-4, y, r, ry, sq=sq), oval(-58, y - 1, r * 0.62, ry * 0.94, sq=sq)]
        bridge = [(-4 - r, y - 3), (-36, y - 8), (-58 + r * 0.62, y - 3)]
        arms = [[(-4 + r, y - 3), (40, y - 8), (60, y - 6)]]
    elif view == 'f':
        lenses = [oval(33, y, r, ry, sq=sq), oval(-33, y, r, ry, sq=sq)]
        bridge = [(33 - r, y - 3), (0, y - 8), (-33 + r, y - 3)]
        arms = [[(33 + r, y - 3), (80, y - 8)], [(-33 - r, y - 3), (-80, y - 8)]]
    else:
        lenses = [oval(-48, y, r * 0.6, ry, sq=sq)]
        bridge = [(-48 - r * 0.6, y - 2), (-72, y - 6), (-77, y - 2)]
        arms = [[(-48 + r * 0.6, y - 3), (0, y - 8), (26, y - 6)]]
    for ln in lenses:
        if tint:
            d.fill(ln, '#fbf6e8', op=tint)
        d.contour(ln, lw, color, nib=0.15)
    d.line(bridge, lw, 'even', color, nib=0)
    for a in arms:
        d.line(a, lw, 'even', color, nib=0)


def scallop(pts, r=10, closed=False, out=1, n=6):
    """A curly edge: the curve pts with round bumps on it (curls, a cloud of hair)."""
    from kit import curve
    sm = curve(pts, closed, n)
    res = []
    acc = 0.0
    last = sm[0]
    res.append(last)
    for i in range(1, len(sm)):
        acc += math.hypot(sm[i][0] - sm[i - 1][0], sm[i][1] - sm[i - 1][1])
        if acc >= r * 1.5:
            a, b = last, sm[i]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / ln * out, dx / ln * out
            res.append(((a[0] + b[0]) / 2 + nx * r * 0.75, (a[1] + b[1]) / 2 + ny * r * 0.75))
            res.append((b[0], b[1], 'c'))
            last = b
            acc = 0.0
    return res
