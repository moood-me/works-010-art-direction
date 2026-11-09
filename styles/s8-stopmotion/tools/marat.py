"""Марат, about 35, a cook: the biggest puppet of the cast — a broad head on a short neck, a barrel of a body,
thick forearms, big hands. Short black curls and a thick black beard (hair.coils), a wide laugh with teeth.
A warm-white cook's jacket with rolled sleeves, a long terracotta apron, a towel over the shoulder, a ladle."""
import math
from sculpt import mix, pts, poly, f
import hair as H
from body import front_patch

EXPR = {
    'beam':  {'smile': 0.95, 'mopen': 0.62, 'lid_lo': 0.4, 'open': 0.86, 'wide': 1.2, 'brow_in': 0.014, 'brow_out': 0.014},
    'laugh': {'smile': 1.0, 'mopen': 0.8, 'lid_lo': 0.8, 'open': 0.6, 'wide': 1.25, 'brow_in': 0.03, 'brow_out': 0.022},
}

JAW = 0.34            # where the beard leaves the face and hangs as a mass of its own
BEARD_END = 0.66


def _hairline(phi):
    a = abs(phi)
    if a < 1.25:
        return -0.25 + 0.2 * (a / 1.25) ** 2
    if a < 1.75:
        return -0.05 - 0.03 * math.sin((a - 1.25) / 0.5 * math.pi)
    return -0.05 + 0.26 * min(1.0, (a - 1.75) / 0.9)


def _beard_top(a):
    """Upper edge of the beard by the angle from the middle of the face: under the lip, up the cheek, to the ear."""
    for (a0, y0), (a1, y1) in zip(_BT, _BT[1:]):
        if a <= a1:
            return y0 + (y1 - y0) * (a - a0) / (a1 - a0)
    return 9.0


_BT = [(0.0, 0.455), (0.38, 0.445), (0.5, 0.37), (0.6, 0.29), (0.85, 0.2), (1.0, 0.1), (1.15, 0.0), (1.44, -0.07), (1.5, 0.2), (1.9, 0.3)]


def marat_hair(h, d, P, ex):
    col = P['hair_col']

    def beard_at(phi, y):
        if y <= JAW:
            return h.surf(phi, y, 0.02 + 0.03 * max(0.0, (y - 0.1) / (JAW - 0.1)))
        base = h.surf(phi, JAW, 0.05)
        t = (y - JAW) / (BEARD_END - JAW)
        s = math.sqrt(max(0.0, 1 - t ** 2.4))
        cz = h.c(JAW)
        return (base[0] * s, y, cz + (base[2] - cz) * (0.3 + 0.7 * s) + 0.04 * t)

    def beard_rad(y):
        r = (h.a(JAW) + h.b(JAW)) / 2
        return r if y <= JAW else r * math.sqrt(max(0.02, 1 - ((y - JAW) / (BEARD_END - JAW)) ** 2.4))

    top = H.curl_spots(h, lambda phi, y: y <= _hairline(phi), 0.052, -0.5, 0.25, out=0.03, k=1.0, seed=4)
    beard = H.curl_spots(h, lambda phi, y: _beard_top(abs(phi)) <= y <= BEARD_END - 0.035, 0.044, -0.04, BEARD_END,
                         seed=9, place=beard_at, radius=beard_rad)
    # the moustache follows the mouth of this face: its lower edge rises with the corners of a smile
    lift = 0.035 * ex.get('smile', 0.0)
    mo = H.curl_spots(h, lambda phi, y: abs(phi) <= 0.64 and P['nose_tip'] + 0.05 <= y <= P['mouth_y'] - 0.03 - lift * min(1.0, abs(phi) / 0.45) ** 1.6,
                      0.038, P['nose_tip'] + 0.055, P['mouth_y'] + 0.03, out=0.03, seed=6)
    tb, tf = H.coils(d, h, P, top, col)
    bb, bf = H.coils(d, h, P, beard + mo, col)
    return dict(col=col, locks=[], cap=(_hairline, 0.18, 1.02), extra_back=[tb, bb], extra_front=[tf, bf])


MARAT = dict(
    name='marat',
    shape=dict(
        a=[(-0.5, 0.03), (-0.46, 0.2), (-0.38, 0.3), (-0.25, 0.355), (-0.1, 0.38), (0.0, 0.39), (0.1, 0.4),
           (0.2, 0.405), (0.3, 0.39), (0.38, 0.35), (0.45, 0.27), (0.5, 0.15)],
        front=[(-0.5, -0.02), (-0.46, 0.2), (-0.38, 0.32), (-0.25, 0.39), (-0.12, 0.41), (0.0, 0.4), (0.1, 0.39),
               (0.2, 0.39), (0.3, 0.38), (0.4, 0.35), (0.46, 0.31), (0.5, 0.23)],
        back=[(-0.5, -0.02), (-0.46, -0.24), (-0.38, -0.37), (-0.25, -0.43), (-0.1, -0.44), (0.0, -0.42), (0.1, -0.35),
              (0.2, -0.24), (0.3, -0.12), (0.4, -0.02), (0.46, 0.05), (0.5, 0.1)],
        bumps=[(0.9, 0.17, 0.07, 0.42, 0.09), (0.36, -0.07, 0.04, 0.35, 0.05)]),
    skin='#dba783', skin_shade='#9a5648', shade='#5a2a30', warm='#c8502e', blush=0.42, blush_col='#d8503a', skin_tex=0.07,
    eye_phi=0.4, eye_y=0.0, eye_r=0.074, eye_w=0.085, eye_open=0.9, eye_tilt=0.004, iris_r=0.05, iris='#4a2c18',
    lash='#1c1210', lash_w=0.012, wing=0.5, socket_a=0.3, lid_top=0.78, lid_bot=0.44,
    brow_gap=0.092, brow_w=0.1, brow_th=0.045, brow_col='#1e1614', brow_arch=0.018, brow_taper=0.45, brow_bushy=True,
    nose_root=0.03, nose_tip=0.21, nose_len=0.105, nose_w=0.095, nose_tint='#d8604a', nose_fade=0.5,
    mouth_y=0.352, mouth_w=0.132, lip='#b25a50', upper_lip=0.008, lower_lip=0.02,
    ear_phi=1.5, ear_y=0.08, ear_w=0.09, ear_h=0.19, ear_out=26, ear_tint='#d86a58',
    hair=marat_hair, hair_col='#2a201e', hair_shade='#060304',
    faces={'joy': EXPR['laugh']},      # his joy on the expression sheet is the full laugh
    wrinkles=[(0.74, 0.01, [(0.0, -0.03), (0.03, -0.004), (0.004, 0.03)], 0.005),
              (-0.74, 0.01, [(0.0, -0.03), (-0.03, -0.004), (-0.004, 0.03)], 0.005),
              (0.0, -0.17, [(-0.12, 0.0), (0.0, -0.008), (0.12, 0.0)], 0.005)],
)

JACKET, APRON, TOWEL = '#ece2d0', '#c4582c', '#f7f2e8'


def _edge(pa, pb, n=6):
    return [(pa[0] + (pb[0] - pa[0]) * i / n, pa[1] + (pb[1] - pa[1]) * i / n) for i in range(n)]


BIB = (_edge((-0.3, 1.02), (0.3, 1.02)) + _edge((0.3, 1.02), (0.5, 1.72)) + _edge((0.5, 1.72), (0.58, 2.45), 4)
       + _edge((0.58, 2.45), (-0.58, 2.45), 4) + _edge((-0.58, 2.45), (-0.5, 1.72), 4) + _edge((-0.5, 1.72), (-0.3, 1.02)))


def marat_inside(d, T, P, B, S, o):
    """The apron painted on the jacket before the form is shaded: a bib and two straps to the neck."""
    res = f'<path d="{poly(front_patch(T, BIB, 0.004))}" fill="{APRON}"/>'
    for side in (-1, 1):
        strap = _edge((side * 0.19, 0.56), (side * 0.27, 0.56), 2) + _edge((side * 0.3, 1.03), (side * 0.22, 1.03), 2)
        res += f'<path d="{poly(front_patch(T, strap, 0.004))}" fill="{APRON}"/>'
    return res


def marat_details(d, T, N, P, B, S):
    """The apron's hems and its tie under the belly; the jacket's front edge; the towel over his left shoulder."""
    res = []
    hem = mix(APRON, '#000000', 0.25)
    top = front_patch(T, [(-0.3, 1.02), (-0.15, 1.02), (0.0, 1.02), (0.15, 1.02), (0.3, 1.02)], 0.006)
    res.append(d.bump(pts(top, close=False), mix(APRON, '#ffffff', 0.08), soft=max(1.2, S * 0.006), height=max(2, S * 0.014),
                      spec=0.2, stroke=True, sw=S * 0.03))
    for side in (-1, 1):
        e = front_patch(T, [(side * 0.3, 1.02), (side * 0.37, 1.25), (side * 0.44, 1.5), (side * 0.5, 1.72), (side * 0.56, 2.26)], 0.004)
        res.append(d.groove(pts(e, close=False), hem, S * 0.012, soft=1.2, depth=-4))
    tie = front_patch(T, [(-0.69 + 1.38 * i / 12, 2.3 + 0.02 * math.sin(math.pi * i / 12)) for i in range(13)], 0.006)
    res.append(d.bump(pts(tie, close=False), mix(APRON, '#000000', 0.1), soft=max(1.2, S * 0.006), height=max(2, S * 0.016),
                      spec=0.2, stroke=True, sw=S * 0.035))
    # the towel: a folded cloth hanging from the shoulder down the chest, two woven stripes and a hem near its end
    x0, x1, y1 = 0.43, 0.62, 1.42

    def over(X):                 # the height where the shoulder is just wide enough: the towel comes over its top
        return next(y for y in [0.5 + 0.005 * i for i in range(200)] if T.a(y) >= X * 1.04)
    y0 = over(x1)
    tw = ([(x0 + (x1 - x0) * i / 4, over(x0 + (x1 - x0) * i / 4)) for i in range(5)]
          + [(x1 + 0.012 * math.sin(3 * i), y0 + (y1 - y0) * i / 6) for i in range(1, 7)]
          + [(x1 - (x1 - x0) * i / 4, y1 + 0.012 * (i % 2)) for i in range(1, 5)]
          + [(x0 - 0.01 * math.sin(2 * i), y1 - (y1 - over(x0)) * i / 6) for i in range(1, 6)])
    tp = front_patch(T, tw, 0.012)
    cid = d.uid('tw')
    d.defs.append(f'<clipPath id="{cid}"><path d="{pts(tp)}"/></clipPath>')
    fid = d.relief(max(2, round(S * 0.012, 1)), max(3, round(S * 0.03, 1)), 0.15, 14)
    bands = ''
    for ya, yb in ((1.3, 1.335), (1.365, 1.385)):
        b = front_patch(T, [(x0 - 0.03, ya), (x1 + 0.03, ya), (x1 + 0.03, yb), (x0 - 0.03, yb)], 0.012)
        bands += f'<path d="{poly(b)}" fill="{APRON}"/>'
    res.append(f'<g filter="url(#{fid})"><path d="{pts(tp)}" fill="{TOWEL}"/><g clip-path="url(#{cid})">{bands}</g></g>')
    res.append(f'<path d="{pts(tp)}" fill="{TOWEL}" filter="url(#{d.tex("cloth", 1.0, 0.3)})"/>')
    return res


MARAT_BODY = dict(
    torso=dict(
        a=[(0.5, 0.22), (0.56, 0.44), (0.64, 0.63), (0.76, 0.75), (0.95, 0.8), (1.3, 0.8), (1.7, 0.79), (2.0, 0.75), (2.2, 0.72)],
        front=[(0.52, 0.06), (0.66, 0.2), (0.9, 0.34), (1.25, 0.46), (1.6, 0.52), (1.9, 0.5), (2.2, 0.45)],
        back=[(0.52, -0.2), (0.66, -0.3), (0.9, -0.36), (1.3, -0.36), (1.8, -0.32), (2.2, -0.3)]),
    torso_y=(0.52, 2.2),
    neck=dict(a=[(0.2, 0.22), (0.7, 0.26)], front=[(0.2, 0.12), (0.7, 0.15)], back=[(0.2, -0.2), (0.7, -0.22)]),
    neck_y=(0.3, 0.68),
    arm=dict(a=[(0.8, 0.1), (0.9, 0.2), (2.2, 0.18)], front=[(0.8, 0.1), (2.2, 0.18)], back=[(0.8, -0.1), (2.2, -0.18)]),
    arm_x=0.74, arm_y=(0.8, 2.2),
    cloth=JACKET, tex='cloth', tex_amount=0.22, shade='#3a2c3a',
    inside=marat_inside, details=marat_details,
)


# ------------------------------------------------------------------ the whole puppet
def _ladle(grip, top):
    """A steel ladle held up like a sceptre: the handle through the fist, the bowl at the top, tipped toward him."""
    def prop(d, T, P, S):
        a = T.P((grip[0] + (grip[0] - top[0]) * 0.22, grip[1] + (grip[1] - top[1]) * 0.22, grip[2]))
        b = T.P(top)
        r = S * 0.15
        s = d.bump(f'M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}', '#b9b4aa', soft=max(1.2, S * 0.006), height=max(3, S * 0.02),
                   spec=0.9, shine=40, stroke=True, sw=S * 0.036)
        cx, cy = b[0] + r * 0.55, b[1] - r * 0.25
        bowl = [(cx + r * math.cos(t) * 1.0, cy + r * math.sin(t) * (0.95 if math.sin(t) > 0 else 0.3))
                for t in [2 * math.pi * i / 28 for i in range(28)]]
        s += f'<g transform="rotate(-24 {f(cx)} {f(cy)})">'
        s += d.bump(pts(bowl), '#b9b4aa', soft=max(2, S * 0.022), height=max(4, S * 0.05), spec=1.0, shine=30)
        inner = [(cx + r * 0.86 * math.cos(t), cy + r * 0.22 * math.sin(t) - r * 0.02) for t in [2 * math.pi * i / 24 for i in range(24)]]
        s += f'<path d="{pts(inner)}" fill="#6a625c"/>'
        s += f'<path d="{pts(inner[1:11], close=False)}" fill="none" stroke="#e8e2d6" stroke-width="{f(S*0.008)}" opacity="0.7"/>'
        s += '</g>'
        return (T.scr(grip)[2] + 0.0, s)
    return prop


def _arms(side):
    if side < 0:      # his right arm: raised, the ladle in the fist
        sh, el, wr = (-0.76, 0.92, -0.02), (-1.12, 1.22, 0.08), (-1.2, 0.6, 0.2)
    else:             # his left: the fist on the hip, the elbow far out
        sh, el, wr = (0.76, 0.92, -0.02), (1.2, 1.55, -0.04), (0.84, 2.02, 0.26)
    mid = tuple((sh[k] + el[k]) / 2 + (0.03 if k == 1 else 0) for k in range(3))
    fm = tuple((el[k] + wr[k]) / 2 for k in range(3))
    roll = tuple(el[k] + (wr[k] - el[k]) * 0.14 for k in range(3))
    return [dict(path=[sh, mid, el], r0=0.2, r1=0.175, col=JACKET, tex='cloth', tex_amount=0.22, z=0.02),
            dict(path=[el, fm, wr], r0=0.15, r1=0.115, col=mix(MARAT['skin'], '#c07a70', 0.1), tex='clay', tex_amount=0.05,
                 shade='#5a2a30', z=0.06),
            dict(path=[el, roll], r0=0.185, r1=0.18, col=mix(JACKET, '#ffffff', 0.15), tex='cloth', tex_amount=0.22, z=0.1)]


MARAT_FIG = dict(
    torso=dict(a=MARAT_BODY['torso']['a'] + [(2.4, 0.68), (2.47, 0.6), (2.5, 0.4)], front=MARAT_BODY['torso']['front'] + [(2.5, 0.42)],
               back=MARAT_BODY['torso']['back'] + [(2.5, -0.28)],
               x=[(0.5, 0.0), (1.2, 0.02), (1.9, 0.07), (2.5, 0.1)]),
    torso_y=(0.52, 2.5),
    legs=lambda side: [dict(path=[(0.1 + side * 0.3, 2.3, 0.0), (0.08 + side * 0.36, 3.05, 0.04), (0.06 + side * 0.4, 3.68, 0.0)],
                            r0=0.22, r1=0.16, col='#56504e', tex='cloth', tex_amount=0.3, z=-0.3)],
    shoe=lambda side: dict(ankle=(0.06 + side * 0.4, 3.7, 0.0), len=0.5, col='#3a2a22', h=0.13, w=0.15),
    skirts=[dict(table=dict(a=[(2.3, 0.58), (2.8, 0.6), (3.24, 0.62), (3.29, 0.58), (3.31, 0.42)], front=[(2.3, 0.47), (3.3, 0.44)], back=[(2.3, 0.2), (3.3, 0.16)],
                            x=[(2.3, 0.09), (3.3, 0.1)]),
                 y=(2.32, 3.31), col=APRON, tex='cloth', tex_amount=0.22, shade='#3a1414', ribs=0.9, z=0.01)],
    arms=_arms,
    hand=lambda side: dict(wrist=(-1.2, 0.6, 0.2), dir=(-0.05, -1.0, 0.0), size=0.34, pose='hold', z=0.1) if side < 0 else
    dict(wrist=(0.86, 2.0, 0.26), dir=(-0.9, 0.35, 0.2), size=0.34, pose='fist', z=0.12),
    props=[_ladle((-1.21, 0.42, 0.2), (-1.3, -0.42, 0.2))],
)
