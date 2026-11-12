"""Аня, about 20: warm, trusting, dreamy. An oval face with a soft jaw, a small slightly upturned nose, full lower lip;
light-brown hair to below the shoulders, parted on one side, a lock falling by the cheek; eyes a little larger than
the others', a lash at the outer corner, looking a little up and away."""
from features import *
from hair import Hair

HEAD = dict(
    sections=sections(cranium=0.98, cheek=0.97, jaw=0.84, chin=0.82, depth=0.97, face=0.93, hollow=0.0, ramus=0.45, jaw_angle=-0.15),
    nose=dict(profile=[(0.0, 0.006, 0.026), (0.08, 0.03, 0.03), (0.165, 0.085, 0.04), (0.185, 0.08, 0.045), (0.21, 0.015, 0.045)],
              tip=0.17, wing=0.05, bridge_from=0.55),
    eye=dict(x=0.135, y=0.0, w=0.07, h=0.041, crease=0.75, lash=1, iris=0.52, peak=-0.2),
    brow=dict(x0=0.05, x1=0.235, y=-0.09, arch=0.025, th=0.75, slope=0.01),
    mouth=dict(y=0.29, w=0.082, lower=0.03, upper_line=1, lip=0.02),
    ear=dict(y=0.07, h=0.22, w=0.11),
    neck=dict(rx=0.145, rz=0.16),
    jaw=dict(angle_y=0.40),
    rest=dict(smile=0.18, look=(-0.15, -0.25), open=0.95),
    shade=dict(level=0.14),
)
HAIR = Hair(mode='tone', part=-28, n=190, width=0.08, thick=0.075, top_thick=0.1,
            hl=[(0, -0.31), (35, -0.28), (70, -0.17), (95, -0.06), (120, 0.0), (180, 0.08)],
            end=[(0, -0.31), (62, -0.17), (80, 0.2), (105, 0.62), (135, 0.95), (180, 1.0)],
            end_neg=[(0, -0.31), (62, -0.17), (100, -0.02), (118, 0.6), (140, 0.95), (180, 1.0)],
            hl_neg=[(0, -0.31), (35, -0.28), (70, -0.17), (95, -0.08), (115, 0.0), (180, 0.08)],
            hang_out=0.12, wave=0.02, waves=1.5, tone_level=0.22, flow=2.0, streaks=1.4, edge=0.05, sweep=6, seed=21)
# a soft side-swept fringe from the parting across the forehead
_fr = []
for i, (x1, y1, w) in enumerate([(0.10, -0.17, 0.065), (0.17, -0.14, 0.065), (0.24, -0.10, 0.06), (0.29, -0.04, 0.055), (0.03, -0.21, 0.06), (0.33, 0.04, 0.05), (0.20, -0.12, 0.05)]):
    _fr.append(dict(pts=[(-0.11 + i * 0.012, -0.47, 0.17), (-0.07 + x1 * 0.3, -0.39, 0.34), (x1 * 0.65, -0.29, 0.39), (x1, y1, 0.39 - abs(x1) * 0.3)], w=w))
HAIR.k['locks'] = _fr
EXTRAS = [cheek_blush(0.8)]


# ---------------------------------------------------------------- the figure
from body3d import *
from figure import figure

HEIGHT = 7.1


def skeleton():
    H = HEIGHT
    j = stand(H, sw=0.5, hw=0.3, female=True)
    # weight on the right leg, the hip out to that side, the shoulders tilted against it
    for k in ('pelvis', 'crotch'):
        j[k] = (-0.07, j[k][1] - 0.03, 0)
    j['hip_r'] = (-0.37, j['hip_r'][1] - 0.06, 0.0); j['hip_l'] = (0.23, j['hip_l'][1] + 0.02, 0.0)
    j['kn_r'] = (-0.28, j['kn_r'][1], 0.04); j['kn_l'] = (0.10, j['kn_l'][1] + 0.05, 0.22)
    j['an_r'] = (-0.22, j['an_r'][1], -0.06); j['an_l'] = (0.2, j['an_l'][1], 0.12)
    j['heel_r'] = (-0.22, 0, -0.18); j['toe_r'] = (-0.34, 0, 0.82)
    j['heel_l'] = (0.2, 0, 0.0); j['toe_l'] = (0.48, 0, 0.95)
    j['waist'] = (-0.03, j['waist'][1], -0.02); j['chest'] = (0.02, j['chest'][1], 0.0); j['neck'] = (0.03, j['neck'][1], -0.04)
    j['sh_r'] = (-0.5, j['sh_r'][1] + 0.06, -0.04); j['sh_l'] = (0.52, j['sh_l'][1] - 0.02, -0.04)
    j['el_r'] = (-0.64, j['el_r'][1] + 0.05, -0.1); j['wr_r'] = (-0.6, j['wr_r'][1] + 0.05, 0.12)
    j['el_l'] = (0.62, -4.5, 0.2); j['wr_l'] = (0.06, -4.86, 0.62)
    return Body(j, scale_sections(FEMALE, 0.95), spine_of(j, H), twist=[(0, -6), (1, 6)])


def _cardigan(v, B, lw, P, polys):
    H = HEIGHT; j = B.j
    out = ''
    allp = [p for q in polys for p in q]
    xs = [p[0] for p in allp]; ys = [p[1] for p in allp]
    cid = uid('kn')
    out += f'<clipPath id="{cid}">' + ''.join(f'<path d="{poly(q)}"/>' for q in polys) + '</clipPath>'
    out += f'<g clip-path="url(#{cid})">' + hatch(None, (min(xs), min(ys), max(xs), max(ys)), angle=90, gap=lw * 3.0, w=lw * 0.3, length=(0.03, 0.06), seed=6) + '</g>'
    edge_r = [surf(B, f, -2 - max(0, f - 0.62) * 38, 0.05) for f in [0.995, 0.9, 0.8, 0.7, 0.62]]
    edge_l = [surf(B, f, 2 + max(0, f - 0.62) * 38, 0.05) for f in [0.995, 0.9, 0.8, 0.7, 0.62]]
    opening = [v(p) for p in edge_r] + [v(p) for p in edge_l[::-1]]
    out += fillpath(opening, PAPER, smooth=False) + stroke([v(p) for p in edge_r], lw * 0.9) + stroke([v(p) for p in edge_l], lw * 0.9)
    # the blouse: a small round collar and its placket
    out += stroke([v(surf(B, 0.985, -14, 0.06)), v(surf(B, 0.955, -5, 0.07)), v(surf(B, 0.95, 0, 0.07)), v(surf(B, 0.955, 6, 0.07)), v(surf(B, 0.985, 14, 0.06))], lw * 0.6)
    out += seams(v, [surf(B, 0.95, 0, 0.065), surf(B, 0.64, 0, 0.065)], lw, 0.4)
    out += button(v, surf(B, 0.86, 0, 0.065), lw, 0.9) + button(v, surf(B, 0.74, 0, 0.065), lw, 0.9)
    out += seams(v, [surf(B, 0.97, -28, 0.07), surf(B, 0.995, 0, 0.0), surf(B, 0.97, 28, 0.07)], lw, 0.6)
    f_c = frac(H, -3.85, j)
    out += seams(v, [surf(B, f, -2, 0.06) for f in (0.6, 0.4, f_c + 0.01)], lw, 0.7)
    for f in (0.52, 0.38, 0.24):
        out += button(v, surf(B, f, -6, 0.06), lw)
    out += fold_like(v, B, lw)
    return out


def fold_like(v, B, lw):
    # pull at the waist where the hip pushes out
    return seams(v, [surf(B, 0.36, -70, 0.05), surf(B, 0.33, -45, 0.05)], lw, 0.5) + seams(v, [surf(B, 0.3, -75, 0.05), surf(B, 0.26, -50, 0.05)], lw, 0.45)


def _knit_sleeve(v, P, lw):
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    return clip(P, hatch(None, (min(xs), min(ys), max(xs), max(ys)), angle=90, gap=lw * 3.0, w=lw * 0.3, length=(0.03, 0.06), seed=7), smooth=False)


def _book(v, pts, lw):
    B = skeleton()
    bk = [surf(B, 0.8, -25, 0.12), surf(B, 0.82, 35, 0.12), surf(B, 0.5, 38, 0.14), surf(B, 0.48, -22, 0.14)]
    P = [v(p) for p in bk]
    return group([P], lw, base=0.45, dark=0.75, s=v.s, off=0.03) + stroke([lerp(P[0], P[3], 0.05), lerp(P[1], P[2], 0.05)], lw * 0.4)


def FIGURE(v, e=None, lw=2.0, neutral=False, bust=False):
    """Standing at ease with her weight on one leg, a book held to her chest, the other hand loose; the head tilted,
    looking up and away. A knitted cardigan over a blouse, an A-line skirt below the knee, flat shoes."""
    knit = 0.12
    d = dict(B=skeleton(), mod=__import__('chars.anya', fromlist=['x']), H=HEIGHT,
             head=dict(yaw_rel=6, pitch=-5, roll=-8),
             arms=dict(r=(0.12, 0.105, 0.085, 0.095, 0.06), sleeve=dict(grow=0.035, until=0.93, tone=knit, dark=0.42, extra=_knit_sleeve),
                       hands=dict(r=dict(pose='relaxed', twist=95, size=0.6), l=dict(pose='loose', twist=20, size=0.55, hold_item=_book)),
                       front=['l']),
             legs=dict(r=(0.27, 0.2, 0.12, 0.14, 0.062), shoe=dict(w=0.15, h=0.24, toe_h=0.09)),
             skirts=[dict(top=-0.615 * HEIGHT, hem=-2.0, flare=0.3, tone=0.2, dark=0.45)],
             torso=[dict(bottom=-3.85, grow=0.05, tone=knit, dark=0.42, with_arms=True, extra=_cardigan)])
    return figure(v, d, e, lw, neutral, bust)
