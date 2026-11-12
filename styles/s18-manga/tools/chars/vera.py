"""Вера, about 40: strict, clever, tired. A long narrow face, high cheekbones and a little hollow under them, a
defined jaw; a long straight nose; narrow eyes with tired lids and bags; thin lips, the corners down; thin
rectangular glasses; black hair pulled back hard into a bun, one strand loose at the temple."""
from features import *
from hair import Hair

HEAD = dict(
    sections=sections(cranium=0.96, cheek=0.97, jaw=0.88, chin=0.86, depth=1.0, face=1.08, hollow=0.06, jaw_angle=0.1, ramus=0.75),
    nose=dict(profile=[(-0.01, 0.012, 0.025), (0.08, 0.06, 0.03), (0.18, 0.115, 0.038), (0.2, 0.105, 0.042), (0.235, 0.015, 0.045)],
              tip=0.195, wing=0.048, bridge_from=0.25),
    eye=dict(x=0.135, y=0.0, w=0.066, h=0.029, crease=0.8, lash=1, bag=0.6, iris=0.5, tilt=0.06, peak=-0.3),
    brow=dict(x0=0.05, x1=0.24, y=-0.075, arch=0.012, th=0.85, slope=0.015),
    mouth=dict(y=0.325, w=0.08, lower=0.025, upper_line=1),
    ear=dict(y=0.08, h=0.23, w=0.11),
    neck=dict(rx=0.14, rz=0.16),
    rest=dict(frown=0.25, open=0.82, brow_in=-0.15, knit=0.25),
    shade=dict(level=0.16),
)
HAIR = Hair(mode='black', part=0, n=150, width=0.06, thick=0.025, top_thick=0.035,
            hl=[(0, -0.30), (40, -0.27), (75, -0.15), (95, 0.0), (120, 0.06), (180, 0.10)],
            streaks=0.8, flow=1.2, seed=51, sweep=0, to_bun=True, cap=False,
            bun=dict(c=(0.0, -0.24, -0.52), r=0.11, dir=(0, -0.2, -1.0)),
            locks=[dict(pts=[(0.30, -0.18, 0.18), (0.335, -0.05, 0.16), (0.33, 0.08, 0.17), (0.305, 0.2, 0.2)], w=0.018)])
EXTRAS = [wrinkles(naso=1, under=1, forehead=1), glasses('rect', r=0.07, rh=0.042, dz=0.05, thick=1.0)]



# ---------------------------------------------------------------- the figure
from body3d import *
from figure import figure

HEIGHT = 7.5
COAT = 0.6


def skeleton():
    H = HEIGHT
    j = stand(H, sw=0.5, hw=0.28, female=True)
    j['el_r'] = (-0.62, -4.62, -0.08); j['wr_r'] = (-0.58, -3.62, 0.22)
    j['el_l'] = (0.62, -5.15, 0.42); j['wr_l'] = (0.42, -6.42, 0.42)
    j['kn_l'] = (0.2, j['kn_l'][1], 0.12); j['an_l'] = (0.22, j['an_l'][1], 0.06); j['toe_l'] = (0.42, 0, 0.92)
    j['toe_r'] = (-0.36, 0, 0.88)
    return Body(j, scale_sections(FEMALE, 0.9), spine_of(j, H), twist=[(0, 0), (1, 4)])


def _coat(v, B, lw, P, polys):
    H = HEIGHT; j = B.j
    out = ''
    # the open front: the blouse inside, lapels
    f_w = frac(H, -0.6 * H, j); f_h = frac(H, -1.88, j)
    fs = (0.995, 0.86, 0.72, 0.55, 0.3, 0.0, -0.4, f_h)
    gr = lambda f: 0.1 + max(0.0, f_w - f) * 0.14 + 0.005
    er = [surf(B, f, -4 - max(0, f - 0.55) * 45, gr(f)) for f in fs]
    el = [surf(B, f, 4 + max(0, f - 0.55) * 45, gr(f)) for f in fs]
    opening = [v(p) for p in er] + [v(p) for p in el[::-1]]
    out += fillpath(opening, PAPER) + clip(opening, tone([v(surf(B, 0.42, -60, 0.1)), v(surf(B, 0.42, 60, 0.1)), (v(surf(B, 0.42, 60, 0.1))[0], 5000), (v(surf(B, 0.42, -60, 0.1))[0], 5000)], 0.5, smooth=False), smooth=False)
    out += seams(v, [surf(B, 0.42, -40, 0.06), surf(B, 0.42, 40, 0.06)], lw, 0.6)
    out += stroke([v(p) for p in er], lw * 1.0) + stroke([v(p) for p in el], lw * 1.0)
    # lapels
    lap = [surf(B, 0.995, -14, 0.11), surf(B, 0.9, -32, 0.13), surf(B, 0.7, -16, 0.12), surf(B, 0.72, -10, 0.11)]
    out += group([[v(p) for p in lap]], lw * 0.8, base=0.75, dark=0.0, s=v.s, shadow=False)
    lap = [surf(B, 0.995, 14, 0.11), surf(B, 0.9, 32, 0.13), surf(B, 0.7, 16, 0.12), surf(B, 0.72, 10, 0.11)]
    out += group([[v(p) for p in lap]], lw * 0.8, base=0.75, dark=0.0, s=v.s, shadow=False)
    # the blouse's high collar
    col = [surf(B, 1.04, -32, 0.02), surf(B, 1.06, 0, 0.03), surf(B, 1.04, 32, 0.02), surf(B, 0.95, 18, 0.04), surf(B, 0.94, -18, 0.04)]
    out += group([[v(p) for p in col]], lw * 0.8, base=0.0, dark=0.0, s=v.s, shadow=False)
    # belt line at the back, pockets
    out += seams(v, [surf(B, 0.3, -80, 0.1), surf(B, 0.25, -45, 0.1)], lw, 0.6, ink=PAPER)
    return out


def _tails(v, B, lw, P):
    H = HEIGHT; j = B.j
    out = ''
    f_top = frac(H, -0.6 * H, j)
    er = [surf(B, f, -4, 0.1 + max(0, f_top - f) * 0.15) for f in (0.0, -0.3, frac(H, -1.85, j))]
    el = [surf(B, f, 4, 0.1 + max(0, f_top - f) * 0.15) for f in (0.0, -0.3, frac(H, -1.85, j))]
    gap = [v(p) for p in er] + [v(p) for p in el[::-1]]
    out += fillpath(gap, f'url(#{tone_id(0.5)})', smooth=False) + stroke([v(p) for p in er], lw) + stroke([v(p) for p in el], lw)
    return out


def _folder(v, pts, lw):
    w = pts[-1]
    q = [add3(w, (-0.35, -0.55, 0.05)), add3(w, (0.12, -0.6, 0.12)), add3(w, (0.18, 0.55, 0.1)), add3(w, (-0.3, 0.6, 0.02))]
    P = [v(p) for p in q]
    return group([P], lw, base=0.1, dark=0.35, s=v.s, off=0.03) + stroke([lerp(P[0], P[1], 0.04), lerp(P[3], P[2], 0.04)], lw * 0.4)


def FIGURE(v, e=None, lw=2.0, neutral=False, bust=False):
    """Upright, a folder against her hip under one hand, the other hand at her glasses; a long dark coat open over a
    high-collared blouse and a dark skirt, low-heeled shoes."""
    d = dict(B=skeleton(), mod=__import__('chars.vera', fromlist=['x']), H=HEIGHT,
             head=dict(yaw_rel=2, pitch=4, roll=0, pit=(0, 0.02, 0.05)),
             arms=dict(r=(0.12, 0.105, 0.085, 0.095, 0.058), sleeve=dict(grow=0.06, until=0.94, tone=COAT, dark=0.9, black=True, fold_ink=PAPER),
                       hands=dict(r=dict(pose='hold', twist=110, size=0.56, hold_item=_folder), l=dict(pose='relaxed', twist=150, size=0.52, side=1, turn=-25)),
                       front_from=dict(l=0.45)),
             legs=dict(r=(0.26, 0.19, 0.11, 0.13, 0.058), skin_tone=0.1, skin_dark=0.3, shoe=dict(w=0.14, h=0.24, toe_h=0.08, tone=0.7, dark=0.9)),
             torso=[dict(bottom=-1.85, grow=0.1, tone=COAT, dark=0.9, black=True, with_arms=True, extra=_coat, flare=(-0.6 * HEIGHT, 0.14))])
    return figure(v, d, e, lw, neutral, bust)
