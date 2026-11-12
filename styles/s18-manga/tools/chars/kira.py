"""Кира, about 15: prickly, closed, defiant, vulnerable underneath. A longer face than a child's, narrow, a small
pointed chin; eyes smaller than Аня's, a sharp upper lid, a shadow under them; straight low brows; the mouth pressed
shut, a crooked half-smirk at most; the head a little down, the look from under the brows, sideways. Short choppy
dark hair, a long fringe falling over one eye (strands, with the eye seen between them)."""
from features import *
from hair import Hair

HEAD = dict(
    sections=sections(cranium=0.95, cheek=0.93, jaw=0.82, chin=0.74, depth=0.96, face=0.98, hollow=0.02, ramus=0.55),
    nose=dict(profile=[(0.0, 0.006, 0.024), (0.08, 0.035, 0.028), (0.17, 0.09, 0.036), (0.19, 0.085, 0.04), (0.215, 0.012, 0.04)],
              tip=0.175, wing=0.044, bridge_from=0.4),
    eye=dict(x=0.132, y=0.0, w=0.062, h=0.03, crease=0.45, iris=0.55, peak=-0.05, bag=0.3, tilt=0.04),
    brow=dict(x0=0.05, x1=0.225, y=-0.07, arch=0.008, th=0.85, slope=0.0),
    mouth=dict(y=0.3, w=0.07, lower=0.026, upper_line=1),
    ear=dict(y=0.07, h=0.22, w=0.11),
    neck=dict(rx=0.14, rz=0.15000000000000002),
    jaw=dict(angle_y=0.40),
    rest=dict(brow_in=-0.45, knit=0.35, look=(0.45, -0.65), open=0.85, smirk=0.25),
    shade=dict(level=0.18),
)
_fringe = []
for i, (x0, x1, yend, w) in enumerate([(-0.02, -0.12, 0.05, 0.05), (-0.06, -0.16, 0.10, 0.05), (-0.10, -0.2, 0.07, 0.045),
                                       (-0.14, -0.24, 0.03, 0.05), (0.02, -0.05, -0.02, 0.05), (-0.17, -0.27, -0.05, 0.05),
                                       (0.06, 0.02, -0.12, 0.05), (0.10, 0.08, -0.16, 0.045)]):
    _fringe.append(dict(pts=[(x0 * 0.6 + 0.05, -0.47, 0.18), (x0, -0.34, 0.37), ((x0 + x1) / 2, -0.12, 0.42), (x1, yend, 0.40)], w=w))
HAIR = Hair(mode='black', part=25, n=150, width=0.07, thick=0.045, top_thick=0.06, spike=0.04,
            hl=[(0, -0.31), (40, -0.27), (75, -0.12), (100, 0.0), (130, 0.08), (180, 0.14)],
            end=[(0, -0.31), (60, 0.0), (90, 0.32), (140, 0.36), (180, 0.38)],
            hang_out=0.04, wave=0.012, waves=1.0, streaks=0.7, flow=1.4, seed=71, locks=_fringe)
EXTRAS = []



# ---------------------------------------------------------------- the figure
from body3d import *
from figure import figure

HEIGHT = 6.95
HOOD = 0.72


def skeleton():
    H = HEIGHT
    j = stand(H, sw=0.46, hw=0.24, female=True)
    # the slouch: the chest sunk back, the neck and the head forward and down, the shoulders forward
    j['chest'] = (0.0, j['chest'][1] + 0.04, -0.12); j['neck'] = (0.02, j['neck'][1] + 0.16, 0.16)
    j['sh_r'] = (-0.46, j['sh_r'][1] + 0.18, 0.1); j['sh_l'] = (0.48, j['sh_l'][1] + 0.12, 0.1)
    # weight on the right leg; the left knee in, its toe turned in
    j['hip_r'] = (-0.3, j['hip_r'][1] - 0.04, 0); j['hip_l'] = (0.2, j['hip_l'][1] + 0.04, 0)
    j['kn_l'] = (0.02, j['kn_l'][1] + 0.08, 0.28); j['an_l'] = (0.2, j['an_l'][1], 0.0); j['heel_l'] = (0.22, 0, -0.1); j['toe_l'] = (0.0, 0, 0.78)
    j['kn_r'] = (-0.24, j['kn_r'][1], 0.04); j['an_r'] = (-0.22, j['an_r'][1], -0.06); j['heel_r'] = (-0.22, 0, -0.2); j['toe_r'] = (-0.34, 0, 0.8)
    j['el_r'] = (-0.56, -4.25, -0.05); j['wr_r'] = (-0.5, -3.32, 0.14)
    j['el_l'] = (0.56, -4.45, 0.18); j['wr_l'] = (0.3, -5.0, 0.58)
    return Body(j, scale_sections(FEMALE, 0.82, d=0.85, chest=0.85), spine_of(j, H), twist=[(0, -8), (1, 4)])


def _hoodie(v, B, lw, P, polys):
    H = HEIGHT; j = B.j
    out = ''
    # the kangaroo pocket, the band at the hem, the strings — light lines on the dark
    f_h = frac(H, -3.3, j)
    out += seams(v, [surf(B, f_h + 0.06, a, 0.13) for a in range(-80, 81, 20)], lw, 0.7, ink=PAPER)
    pk = [surf(B, 0.42, -40, 0.14), surf(B, 0.42, 40, 0.14), surf(B, 0.12, 52, 0.14), surf(B, 0.12, -52, 0.14)]
    out += stroke([v(p) for p in pk] + [v(pk[0])], lw * 0.6, fill=PAPER, smooth=False)
    out += seams(v, [surf(B, 0.95, -12, 0.15), surf(B, 0.8, -14, 0.16), surf(B, 0.68, -12, 0.16)], lw, 0.7, ink=PAPER)
    out += seams(v, [surf(B, 0.95, 12, 0.15), surf(B, 0.8, 13, 0.16), surf(B, 0.7, 12, 0.16)], lw, 0.7, ink=PAPER)
    for a in (-60, 50):
        out += seams(v, [surf(B, 0.62, a, 0.14), surf(B, 0.45, a * 0.6, 0.14)], lw, 0.5, ink=PAPER)
    # the backpack strap over the left shoulder
    st = [surf(B, 1.0, 40, 0.18), surf(B, 0.92, 52, 0.2), surf(B, 0.7, 50, 0.2), surf(B, 0.5, 52, 0.19)]
    out += stroke([v(p) for p in st], lw * 5.0, fill=INK) + stroke([v(p) for p in st], lw * 3.4, fill=f'url(#{tone_id(0.4)})')
    return out


def _hood(v, B, lw):
    pts = [surf(B, 1.0, -60, 0.18), surf(B, 1.12, -40, 0.12), surf(B, 1.2, 180, 0.15), surf(B, 1.12, 40, 0.12), surf(B, 1.0, 60, 0.18), surf(B, 0.94, 0, 0.2)]
    return group([[v(p) for p in pts]], lw, base=HOOD, dark=0.95, black=True, s=v.s, off=0.03)


def _headphones(v, B, lw):
    band = [surf(B, 1.05, -50, 0.16), surf(B, 1.0, -20, 0.22), surf(B, 0.98, 20, 0.22), surf(B, 1.05, 50, 0.16)]
    P = [v(p) for p in band]
    out = stroke(P, lw * 4.2) + stroke(P, lw * 2.4, fill=PAPER)
    for a, k in ((-55, 0), (55, 1)):
        c = v(surf(B, 1.06, a, 0.2))
        r = 0.11 * v.s
        cup = [(c[0] + r * 0.8 * math.cos(t), c[1] + r * math.sin(t)) for t in [i * math.pi / 10 for i in range(20)]]
        out += group([cup], lw, base=0.0, dark=0.3, s=v.s, off=0.02)
        out += f'<ellipse cx="{f1(c[0])}" cy="{f1(c[1])}" rx="{f1(r * 0.4)}" ry="{f1(r * 0.55)}" fill="none" stroke="{INK}" stroke-width="{lw * 0.5:.2f}"/>'
    return out


def _phone(v, pts, lw):
    w = pts[-1]
    q = [add3(w, (-0.08, 0.15, 0.1)), add3(w, (0.1, 0.15, 0.12)), add3(w, (0.1, 0.6, 0.1)), add3(w, (-0.08, 0.6, 0.08))]
    P = [v(p) for p in q]
    return fillpath(P, INK, smooth=False) + stroke([lerp(P[0], P[1], 0.2), lerp(P[3], P[2], 0.2)], lw * 0.3, fill=PAPER, smooth=False)


def _laces(v, side, j, lw):
    out = ''
    a, t = j['an_' + side], j['toe_' + side]
    for k in range(4):
        p = lerp3((a[0], -0.3, a[2] + 0.05), (t[0], -0.12, t[2] * 0.6), 0.15 + k * 0.17)
        c = v(p); r = 0.05 * v.s
        out += stroke([(c[0] - r, c[1] - r * 0.3), (c[0] + r, c[1] + r * 0.3)], lw * 0.9, fill=PAPER, smooth=False)
    return out


def FIGURE(v, e=None, lw=2.0, neutral=False, bust=False):
    """The slouch: shoulders forward, the head down, the look from under the brows; the weight on one leg, the other
    knee in. An oversized dark hoodie with the sleeves over half the hands, a backpack strap held at the chest, a
    phone in the other hand; headphones round the neck (white: her one bright accent); narrow trousers, heavy boots
    with white laces."""
    B = skeleton()
    d = dict(B=B, mod=__import__('chars.kira', fromlist=['x']), H=HEIGHT,
             head=dict(yaw_rel=4, pitch=12, roll=-4, pit=(0, 0.0, 0.04)),
             arms=dict(r=(0.1, 0.09, 0.075, 0.08, 0.052), sleeve=dict(grow=0.1, until=1.0, tone=HOOD, dark=0.95, black=True, fold_ink=PAPER, cuff=True),
                       hands=dict(r=dict(pose='hold', twist=60, size=0.48, hold_item=_phone), l=dict(pose='hold', twist=120, size=0.48, side=1, turn=170)),
                       front_from=dict(l=0.5)),
             legs=dict(r=(0.24, 0.17, 0.11, 0.12, 0.06), garment=dict(kind='trousers', grow=0.03, tone=0.55, dark=0.85),
                       shoe=dict(w=0.17, h=0.42, toe_h=0.13, kind='boot', tone=1.0, black=True, extra=_laces)),
             torso=[dict(bottom=-3.3, grow=0.15, tone=HOOD, dark=0.95, black=True, with_arms=True, extra=_hoodie)],
             items=dict(neck=[lambda v, B, lw, near: _hood(v, B, lw)], front=[lambda v, B, lw, near: _headphones(v, B, lw)]))
    return figure(v, d, e, lw, neutral, bust)
