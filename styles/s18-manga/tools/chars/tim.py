"""Тим, about 8: mischievous, curious. A child's head — the cranium big, the face small and low, round full cheeks,
a small chin, a button nose with freckles and a plaster; black hair sticking up; a crooked grin."""
from features import *
from hair import Hair

_t = sections(cranium=1.04, cheek=1.06, jaw=0.98, chin=0.92, depth=0.96, face=0.80, ramus=0.45, jaw_angle=-0.2)
_t = [((y * 1.14 if y < 0 else y),) + tuple(r) for y, *r in _t]
HEAD = dict(
    sections=_t,
    nose=dict(profile=[(0.02, 0.004, 0.025), (0.08, 0.02, 0.03), (0.135, 0.06, 0.042), (0.155, 0.055, 0.045), (0.175, 0.01, 0.045)],
              tip=0.14, wing=0.045, bridge_from=0.7),
    eye=dict(x=0.135, y=0.0, w=0.066, h=0.04, crease=0.5, iris=0.55, peak=-0.1),
    brow=dict(x0=0.05, x1=0.22, y=-0.085, arch=0.02, th=0.9),
    mouth=dict(y=0.235, w=0.075, lower=0.022),
    ear=dict(y=0.05, h=0.22, w=0.12),
    neck=dict(rx=0.135, rz=0.14),
    jaw=dict(angle_y=0.33),
    rest=dict(smirk=0.8, brow_out=0.3, brow_in=-0.2, look=(0.3, 0.0)),
    shade=dict(level=0.14),
)
HAIR = Hair(mode='black', part=20, n=120, width=0.075, thick=0.05, top_thick=0.07, spike=0.11,
            hl=[(0, -0.36), (40, -0.33), (75, -0.2), (100, -0.05), (130, 0.05), (180, 0.12)],
            wave=0.02, waves=1.0, streaks=1.0, seed=41, cap_y=-0.36,
            locks=[dict(pts=[(x, -0.5, z), (x * 1.3, -0.62, z * 1.2 - 0.05), (x * 1.5 + 0.04, -0.69, z * 1.3 - 0.12)], w=0.07) for x, z in [(-0.1, -0.1), (0.05, -0.15), (0.15, -0.05), (-0.18, -0.25), (0.1, -0.3), (0.0, 0.05)]])
EXTRAS = [freckles(16), plaster(x=0.02, y=0.06, w=0.06, hgt=0.02, ang=-20), cheek_blush(0.7, y=0.11)]



# ---------------------------------------------------------------- the figure
from body3d import *
from figure import figure

HEIGHT = 5.4


def skeleton():
    H = HEIGHT
    j = stand(H, sw=0.5, hw=0.24)
    # leaning forward, pointing ahead with the left hand; the right foot behind on its toes
    j['chest'] = (0.0, j['chest'][1], 0.12); j['neck'] = (0.02, j['neck'][1] + 0.04, 0.24)
    j['sh_r'] = (-0.5, j['sh_r'][1] + 0.05, 0.1); j['sh_l'] = (0.5, j['sh_l'][1] - 0.02, 0.12)
    j['el_l'] = (0.78, -3.7, 0.5); j['wr_l'] = (0.92, -3.95, 1.05)
    j['el_r'] = (-0.6, -3.3, -0.05); j['wr_r'] = (-0.55, -2.62, 0.14)
    j['kn_l'] = (0.24, -1.5, 0.45); j['an_l'] = (0.26, -0.24, 0.3); j['heel_l'] = (0.26, 0, 0.18); j['toe_l'] = (0.4, 0, 1.05)
    j['kn_r'] = (-0.22, -1.45, -0.15); j['an_r'] = (-0.25, -0.42, -0.55); j['heel_r'] = (-0.26, -0.32, -0.62); j['toe_r'] = (-0.3, 0, 0.22)
    return Body(j, scale_sections(MALE, 0.66, d=0.78), spine_of(j, H), twist=[(0, -8), (1, 8)])


def _stripes(v, B, lw, P, polys):
    out = ''
    bands = []
    for k in range(9):
        f0 = 0.97 - k * 0.12
        if f0 < 0.0:
            break
        top = [v(surf(B, f0, a, 0.07)) for a in range(-110, 111, 10)]
        bot = [v(surf(B, f0 - 0.055, a, 0.07)) for a in range(-110, 111, 10)]
        # widen across the page so the sleeves are banded too
        top = [(top[0][0] - 300, top[0][1])] + top + [(top[-1][0] + 300, top[-1][1])]
        bot = [(bot[0][0] - 300, bot[0][1])] + bot + [(bot[-1][0] + 300, bot[-1][1])]
        bands.append(top + bot[::-1])
    cid = uid('st')
    out += f'<clipPath id="{cid}">' + ''.join(f'<path d="{poly(q)}"/>' for q in polys) + '</clipPath>'
    out += f'<g clip-path="url(#{cid})">' + ''.join(tone(b, 0.62, smooth=False) for b in bands) + '</g>'
    out += seams(v, [surf(B, 0.99, -30, 0.08), surf(B, 0.95, 0, 0.09), surf(B, 0.99, 30, 0.08)], lw, 0.8)
    out += seams(v, [surf(B, 0.3, -60, 0.08), surf(B, 0.22, -20, 0.08)], lw, 0.5)
    return out


def _knee(v, side, j, lw):
    if side != 'l':
        return ''
    k = j['kn_l']
    c = v(add3(k, (0, 0.02, 0.13)))
    r = 0.07 * v.s
    pts = [(c[0] - r, c[1] - r * 0.5), (c[0] + r, c[1] - r * 0.7), (c[0] + r * 1.1, c[1] + r * 0.5), (c[0] - r * 0.9, c[1] + r * 0.7)]
    return fillpath(pts, PAPER, smooth=False) + outline(pts, lw * 0.6, 0.3, smooth=False)


def _socks(v, side, j, lw):
    a, k = j['an_' + side], j['kn_' + side]
    return stroke(ring_around(v, a, k, 0.18, 0.085), lw * 0.7) + stroke(ring_around(v, a, k, 0.14, 0.085), lw * 0.4)


def _slingshot(v, pts, lw):
    w = pts[-1]
    p0 = v(add3(w, (0.0, 0.12, 0.08))); p1 = v(add3(w, (0.0, 0.5, 0.08)))
    a = v(add3(w, (-0.12, 0.78, 0.08))); b = v(add3(w, (0.12, 0.8, 0.08)))
    out = stroke([p0, p1], lw * 2.6, taper=(0.05, 0.05), smooth=False)
    out += stroke([p1, lerp(p1, a, 0.5), a], lw * 2.0, taper=(0.05, 0.3)) + stroke([p1, lerp(p1, b, 0.5), b], lw * 2.0, taper=(0.05, 0.3))
    out += stroke([a, (a[0] + 0.06 * v.s, a[1] + 0.3 * v.s), b], lw * 0.5, taper=(0.1, 0.1))
    return out


def FIGURE(v, e=None, lw=2.0, neutral=False, bust=False):
    """Leaning forward, pointing at something ahead, a slingshot in the other hand, one foot behind on its toes;
    a striped T-shirt, shorts, a plaster on the knee, socks, sneakers."""
    d = dict(B=skeleton(), mod=__import__('chars.tim', fromlist=['x']), H=HEIGHT,
             head=dict(yaw_rel=6, pitch=-6, roll=5, pit=(0, 0.12, 0.05)),
             arms=dict(r=(0.1, 0.09, 0.075, 0.08, 0.05), sleeve=dict(grow=0.05, until=0.32, tone=0.0, dark=0.25),
                       hands=dict(r=dict(pose='hold', twist=95, size=0.5, hold_item=_slingshot), l=dict(pose='point', twist=40, size=0.5, side=1, turn=-10)),
                       front_from={}),
             legs=dict(r=(0.2, 0.15, 0.1, 0.11, 0.055), garment=dict(kind='trousers', grow=0.08, tone=0.55, dark=0.8, until=0.38, flare=0.05),
                       knee_extra=_knee, shoe=dict(w=0.15, h=0.22, toe_h=0.1, kind='sneaker', extra=_socks)),
             torso=[dict(bottom=-2.75, grow=0.07, tone=0.0, dark=0.25, with_arms=True, extra=_stripes)])
    return figure(v, d, e, lw, neutral, bust)
