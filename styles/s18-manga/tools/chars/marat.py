"""Марат, about 35, a cook: huge, loud, merry, generous. A wide head on a thick short neck, a big jaw, a broad nose,
thick black brows, dark eyes that narrow when he laughs; short black curls, a thick black beard. His resting face
is a wide laugh — teeth and tongue showing."""
from features import *
from hair import Hair

HEAD = dict(
    sections=sections(cranium=1.06, cheek=1.12, jaw=1.2, chin=1.15, depth=1.03, face=1.0, jaw_angle=-0.2),
    nose=dict(profile=[(0.0, 0.012, 0.04), (0.08, 0.05, 0.05), (0.17, 0.12, 0.07), (0.2, 0.11, 0.075), (0.235, 0.02, 0.07)],
              tip=0.185, wing=0.082, bridge_from=0.45),
    eye=dict(x=0.15, y=0.0, w=0.064, h=0.03, crease=0.6, iris=0.55, peak=-0.2),
    brow=dict(x0=0.05, x1=0.26, y=-0.08, arch=0.015, th=1.8),
    mouth=dict(y=0.31, w=0.11, lower=0.0, halo=2.2),
    ear=dict(y=0.08, h=0.24, w=0.12),
    neck=dict(rx=0.23, rz=0.22, flare=0.3),
    rest=dict(smile=1.0, mopen=0.75, mwide=0.3, jaw=0.45, squint=0.85, open=0.55, brow_in=0.35, brow_out=0.1),
    shade=dict(level=0.16),
)
HAIR = Hair(mode='black', part=-10, n=150, width=0.07, thick=0.06, top_thick=0.08, wave=0.03, waves=3.0, spike=0.015,
            hl=[(0, -0.31), (40, -0.28), (75, -0.14), (95, 0.02), (130, 0.12), (180, 0.18)],
            streaks=0.8, curls=60, seed=61, cap_y=-0.3)
HEAD['under'] = [beard(thick=0.035, length=0.05)]
EXTRAS = [wrinkles(crows=2)]



# ---------------------------------------------------------------- the figure
from body3d import *
from figure import figure

HEIGHT = 7.4


def skeleton():
    H = HEIGHT
    j = stand(H, sw=0.86, hw=0.4)
    # leaning back with the laugh, the belly forward; a wide stance
    j['chest'] = (0.0, j['chest'][1], -0.1); j['neck'] = (0.0, j['neck'][1], -0.24); j['waist'] = (0, j['waist'][1], 0.04)
    j['sh_r'] = (-0.86, j['sh_r'][1] + 0.02, -0.16); j['sh_l'] = (0.86, j['sh_l'][1] - 0.04, -0.16)
    j['el_l'] = (1.12, -6.55, 0.15); j['wr_l'] = (0.98, -7.55, 0.3)
    j['el_r'] = (-1.4, -4.85, -0.3); j['wr_r'] = (-0.92, -4.3, 0.12)
    j['hip_r'] = (-0.42, j['hip_r'][1], 0); j['hip_l'] = (0.42, j['hip_l'][1], 0)
    j['kn_r'] = (-0.58, j['kn_r'][1], 0.08); j['kn_l'] = (0.56, j['kn_l'][1], 0.12)
    j['an_r'] = (-0.62, j['an_r'][1], -0.02); j['an_l'] = (0.62, j['an_l'][1], 0.0)
    j['heel_r'] = (-0.62, 0, -0.16); j['toe_r'] = (-0.95, 0, 0.85); j['heel_l'] = (0.62, 0, -0.14); j['toe_l'] = (0.92, 0, 0.88)
    return Body(j, scale_sections(MALE, 1.22, d=1.15, belly=0.28, chest=1.05), spine_of(j, H), twist=[(0, -4), (1, 6)])


def _jacket(v, B, lw, P, polys):
    out = ''
    # double-breasted: the overlap edge and two rows of buttons
    out += seams(v, [surf(B, 0.97, 18, 0.06), surf(B, 0.7, 22, 0.07), surf(B, 0.4, 24, 0.08), surf(B, 0.12, 22, 0.08)], lw, 0.8)
    for f in (0.85, 0.7, 0.55):
        out += button(v, surf(B, f, -12, 0.07), lw, 1.6) + button(v, surf(B, f, 14, 0.07), lw, 1.6)
    # a stand collar
    col = [surf(B, 1.05, -40, 0.03), surf(B, 1.07, 0, 0.04), surf(B, 1.05, 40, 0.03), surf(B, 0.97, 30, 0.07), surf(B, 0.97, -30, 0.07)]
    out += group([[v(p) for p in col]], lw * 0.8, base=0.0, dark=0.0, s=v.s, shadow=False)
    # strain folds at the belly
    out += seams(v, [surf(B, 0.5, -55, 0.06), surf(B, 0.47, -25, 0.07)], lw, 0.5) + seams(v, [surf(B, 0.42, 40, 0.07), surf(B, 0.45, 60, 0.06)], lw, 0.5)
    return out


def _apron(v, B, lw):
    H = HEIGHT; j = B.j
    fb = frac(H, -1.55, j); ft = 0.66
    def edge(a0, a1):
        return [surf(B, f, a0 + (a1 - a0) * 0, 0.12 + max(0, 0.2 - f) * 0.12) for f in (ft, 0.4, 0.2, 0.0, -0.3, fb)]
    left = [surf(B, f, -55 if f > 0.3 else -58, 0.12 + max(0, 0.2 - f) * 0.18) for f in (ft, 0.45, 0.2, 0.0, -0.3, fb)]
    right = [surf(B, f, 55 if f > 0.3 else 58, 0.12 + max(0, 0.2 - f) * 0.18) for f in (ft, 0.45, 0.2, 0.0, -0.3, fb)]
    bottom = [surf(B, fb, a, 0.12 + (0.2 - fb) * 0.18) for a in range(-58, 59, 8)]
    P = [v(p) for p in left] + [v(p) for p in bottom] + [v(p) for p in right[::-1]]
    out = group([P], lw, base=0.32, dark=0.62, s=v.s, off=0.08)
    for a in (-35, -5, 25, 45):
        out += seams(v, [surf(B, 0.0, a, 0.13), surf(B, -0.4, a * 1.05, 0.13 + 0.1), surf(B, fb + 0.02, a * 1.1, 0.12 + (0.2 - fb) * 0.18)], lw, 0.55)
    # waist tie and the neck strap
    out += seams(v, [surf(B, 0.3, -70, 0.12), surf(B, 0.3, 70, 0.12)], lw, 0.9)
    out += seams(v, [surf(B, ft, -50, 0.12), surf(B, 0.97, -30, 0.08)], lw, 0.8) + seams(v, [surf(B, ft, 50, 0.12), surf(B, 0.97, 30, 0.08)], lw, 0.8)
    return out


def _towel(v, B, lw):
    pts = [surf(B, 1.0, -30, 0.1), surf(B, 0.98, -70, 0.14), surf(B, 0.75, -95, 0.17), surf(B, 0.55, -92, 0.18), surf(B, 0.55, -62, 0.16), surf(B, 0.82, -45, 0.13), surf(B, 0.99, -10, 0.1)]
    P = [v(p) for p in pts]
    stripes = ''.join(tone([v(surf(B, f, -130, 0.2)), v(surf(B, f, -30, 0.2)), v(surf(B, f - 0.035, -30, 0.2)), v(surf(B, f - 0.035, -130, 0.2))], 0.55, smooth=False) for f in (0.68, 0.62))
    return group([P], lw, base=0.08, dark=0.32, s=v.s, off=0.03, extra=stripes)


def _ladle(v, pts, lw):
    w = pts[-1]
    a = v(add3(w, (0.02, 0.25, 0.05))); b = v(add3(w, (-0.05, -1.25, 0.0)))
    out = stroke([a, b], lw * 2.6, taper=(0.05, 0.05), smooth=False) + stroke([a, b], lw * 1.0, taper=(0.1, 0.1), smooth=False, fill=PAPER)
    c = v(add3(w, (-0.08, -1.45, 0.02))); R = 0.27 * v.s
    bowl = [(c[0] + R * math.cos(t), c[1] + R * 0.55 * math.sin(t)) for t in [k * math.pi / 12 for k in range(24)]]
    cup = [(c[0] + R * math.cos(t), c[1] + R * 0.95 * math.sin(t)) for t in [k * math.pi / 12 for k in range(13)]]
    out += group([cup], lw, base=0.0, dark=0.4, s=v.s, off=0.04) + fillpath(bowl, f'url(#{tone_id(0.45)})', smooth=False) + outline(bowl, lw * 0.9, 0.4, smooth=False)
    # a splash of soup flying out with the laugh
    for k, (dx, dy, r) in enumerate([(0.1, -0.35, 0.045), (0.28, -0.5, 0.03), (-0.15, -0.42, 0.035)]):
        out += f'<circle cx="{f1(c[0] + dx * v.s)}" cy="{f1(c[1] + dy * v.s)}" r="{f1(r * v.s)}" fill="{PAPER}" stroke="{INK}" stroke-width="{lw * 0.6:.2f}"/>'
    return out


def _forearm_hair(v, P, lw):
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    return clip(P, hatch(None, (min(xs), min(ys), max(xs), max(ys)), angle=65, gap=lw * 2.4, w=lw * 0.28, length=(0.02, 0.05), seed=8, density=lambda x, y: 0.5), smooth=False)


def FIGURE(v, e=None, lw=2.0, neutral=False, bust=False):
    """Laughing with the whole body: leaning back, the ladle up in one hand, the other fist on his hip; a white
    double-breasted cook's jacket with the sleeves rolled up, a long apron, a towel over the shoulder."""
    B = skeleton()
    d = dict(B=B, mod=__import__('chars.marat', fromlist=['x']), H=HEIGHT,
             head=dict(yaw_rel=-2, pitch=-12, roll=6, hs=1.14, pit=(0, 0.0, 0.08)),
             arms=dict(r=(0.2, 0.18, 0.14, 0.16, 0.1), sleeve=dict(grow=0.07, until=0.55, tone=0.0, dark=0.25), skin_extra=_forearm_hair,
                       hands=dict(r=dict(pose='fist', twist=30, size=0.7, turn=0), l=dict(pose='hold', twist=80, size=0.7, side=1, hold_item=_ladle)),
                       front=['r']),
             legs=dict(r=(0.34, 0.27, 0.17, 0.19, 0.1), garment=dict(kind='trousers', grow=0.08, tone=0.62, dark=0.85, flare=0.03),
                       shoe=dict(w=0.2, h=0.28, toe_h=0.11, tone=0.7, dark=0.9)),
             torso=[dict(bottom=-3.45, grow=0.07, tone=0.0, dark=0.22, with_arms=True, extra=_jacket)],
             items=dict(torso=[lambda v, B, lw, near: _apron(v, B, lw) + _towel(v, B, lw)]))
    return figure(v, d, e, lw, neutral, bust)
