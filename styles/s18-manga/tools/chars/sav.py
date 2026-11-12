"""Савелий Петрович, about 70, a watchmaker: grumpy outside, kind inside. A broad head with heavy jowls, a big
fleshy nose, drooping lids and bags, bushy white brows, a white moustache; bald on top, a fringe of white hair round
the back; small round glasses low on the nose — he looks over them."""
from features import *
from hair import Hair

HEAD = dict(
    sections=sections(cranium=1.02, cheek=1.02, jaw=1.12, chin=1.1, depth=1.0, face=1.02, jaw_angle=-0.1),
    nose=dict(profile=[(0.0, 0.01, 0.035), (0.08, 0.06, 0.045), (0.17, 0.13, 0.06), (0.2, 0.12, 0.065), (0.235, 0.02, 0.06)],
              tip=0.19, wing=0.07, bridge_from=0.3),
    eye=dict(x=0.14, y=0.0, w=0.06, h=0.028, crease=0.9, droop=0.6, bag=1.0, iris=0.5, peak=-0.35),
    brow=dict(x0=0.05, x1=0.25, y=-0.075, arch=0.02, style='bushy', hairs=16, size=1.3),
    mouth=dict(y=0.315, w=0.09, lower=0.03),
    ear=dict(y=0.08, h=0.27, w=0.13),
    neck=dict(rx=0.16, rz=0.17, lean=0.10),
    rest=dict(brow_in=-0.35, knit=0.5, frown=0.35, look=(0.0, -0.3), open=0.85),
    shade=dict(level=0.16),
)
HAIR = Hair(mode='light', bald=[(0, 0.3), (60, 0.3), (75, -0.1), (100, -0.1), (130, -0.18), (180, -0.22)],
            hl=[(0, -0.06), (80, -0.06), (100, 0.0), (130, 0.12), (180, 0.18)],
            n=110, width=0.06, thick=0.03, wave=0.0, waves=2, spike=0.015, flow=0.8, seed=31, back_only=88)
EXTRAS = [wrinkles(forehead=3, crows=3, naso=1, under=1),
          moustache(w=0.11, droop=0.04),
          glasses('round', r=0.055, dz=0.085, low=0.035, thick=0.75)]



# ---------------------------------------------------------------- the figure
from body3d import *
from figure import figure

HEIGHT = 6.85


def skeleton():
    H = HEIGHT
    j = stand(H, sw=0.6, hw=0.3)
    # stooped: the chest and the neck forward, the shoulders round
    j['chest'] = (0.0, j['chest'][1] + 0.05, 0.10); j['neck'] = (0.0, j['neck'][1] + 0.12, 0.26)
    j['sh_r'] = (-0.6, j['sh_r'][1] + 0.12, 0.08); j['sh_l'] = (0.6, j['sh_l'][1] + 0.12, 0.08)
    # the right hand holds the watch before his chest; the left is behind his back
    j['el_r'] = (-0.74, -4.3, 0.05); j['wr_r'] = (-0.28, -4.5, 0.72)
    j['el_l'] = (0.76, -4.35, -0.32); j['wr_l'] = (0.3, -3.85, -0.6)
    j['kn_r'] = (-0.28, j['kn_r'][1], 0.12); j['kn_l'] = (0.26, j['kn_l'][1], 0.14)
    j['toe_r'] = (-0.42, 0, 0.85); j['toe_l'] = (0.46, 0, 0.9)
    return Body(j, scale_sections(MALE, 0.9, belly=0.06), spine_of(j, H), twist=[(0, -4), (1, 4)])


def _vest(v, B, lw, P, polys):
    out = ''
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    out += clip(P, hatch(None, (min(xs), min(ys), max(xs), max(ys)), angle=80, gap=lw * 2.6, w=lw * 0.3, length=(0.04, 0.08), seed=12), smooth=False)
    # the V of the neck: the shirt and the bow tie in it
    vee = [surf(B, 0.99, -26, 0.06), surf(B, 0.62, -2, 0.07), surf(B, 0.99, 26, 0.06)]
    V = [v(p) for p in vee] + [v(surf(B, 1.0, 0, 0.0))]
    out += fillpath(V, PAPER, smooth=False) + stroke([v(p) for p in vee], lw * 0.9)
    out += seams(v, [surf(B, 0.62, -2, 0.07), surf(B, 0.05, -4, 0.07)], lw, 0.7)
    for f in (0.5, 0.36, 0.22):
        out += button(v, surf(B, f, -3, 0.08), lw)
    # the bow tie
    c = v(surf(B, 0.96, 0, 0.08)); r = 0.08 * v.s
    out += fillpath([(c[0] - r * 1.4, c[1] - r * 0.6), (c[0], c[1]), (c[0] - r * 1.4, c[1] + r * 0.6)], INK, smooth=False)
    out += fillpath([(c[0] + r * 1.2, c[1] - r * 0.6), (c[0], c[1]), (c[0] + r * 1.2, c[1] + r * 0.6)], INK, smooth=False)
    out += f'<circle cx="{f1(c[0])}" cy="{f1(c[1])}" r="{f1(r * 0.35)}" fill="{INK}"/>'
    # shirt collar points
    out += stroke([v(surf(B, 1.0, -20, 0.08)), v(surf(B, 0.95, -10, 0.1))], lw * 0.7) + stroke([v(surf(B, 1.0, 20, 0.08)), v(surf(B, 0.95, 10, 0.1))], lw * 0.7)
    # the watch chain from the pocket
    out += stroke([v(surf(B, 0.35, 40, 0.09)), v(surf(B, 0.28, 15, 0.1)), v(surf(B, 0.4, -10, 0.12))], lw * 0.5)
    return out


def _watch(v, pts, lw):
    w = pts[-1]
    c = v(add3(w, (0.12, -0.18, 0.15))); R = 0.16 * v.s
    ring = [(c[0] + R * math.cos(t), c[1] + R * 0.92 * math.sin(t)) for t in [k * math.pi / 12 for k in range(24)]]
    out = fillpath(ring, PAPER, smooth=False) + outline(ring, lw * 1.1, 0.5, smooth=False)
    out += f'<circle cx="{f1(c[0])}" cy="{f1(c[1])}" r="{f1(R * 0.78)}" fill="none" stroke="{INK}" stroke-width="{lw * 0.35:.2f}"/>'
    for k in range(12):
        a = k * math.pi / 6
        out += stroke([(c[0] + R * 0.68 * math.cos(a), c[1] + R * 0.68 * math.sin(a)), (c[0] + R * 0.76 * math.cos(a), c[1] + R * 0.76 * math.sin(a))], lw * 0.35, smooth=False)
    out += stroke([c, (c[0] + R * 0.05, c[1] - R * 0.55)], lw * 0.6, smooth=False) + stroke([c, (c[0] + R * 0.4, c[1] + R * 0.12)], lw * 0.5, smooth=False)
    out += fillpath([(c[0] - R * 0.15, c[1] - R * 1.0), (c[0] + R * 0.15, c[1] - R * 1.0), (c[0] + R * 0.15, c[1] - R * 1.2), (c[0] - R * 0.15, c[1] - R * 1.2)], PAPER, smooth=False)
    out += outline([(c[0] - R * 0.15, c[1] - R * 1.0), (c[0] + R * 0.15, c[1] - R * 1.0), (c[0] + R * 0.15, c[1] - R * 1.2), (c[0] - R * 0.15, c[1] - R * 1.2)], lw * 0.6, 0.3, smooth=False)
    return out


def FIGURE(v, e=None, lw=2.0, neutral=False, bust=False):
    """Stooped, the head forward and down over a pocket watch held before his chest; the other hand behind his back.
    A white shirt, a knitted vest, a bow tie, baggy trousers, old shoes."""
    d = dict(B=skeleton(), mod=__import__('chars.sav', fromlist=['x']), H=HEIGHT,
             head=dict(yaw_rel=4, pitch=14, roll=3, pit=(0, 0.04, 0.05)),
             arms=dict(r=(0.14, 0.12, 0.095, 0.105, 0.065), sleeve=dict(grow=0.06, until=0.95, tone=0.0, dark=0.25),
                       hands=dict(r=dict(pose='hold', twist=190, size=0.6, turn=-20, over=_watch), l=None),
                       front_from=dict(r=0.5), behind=['l']),
             legs=dict(r=(0.27, 0.21, 0.13, 0.14, 0.07), garment=dict(kind='trousers', grow=0.07, tone=0.22, dark=0.45, flare=0.02),
                       shoe=dict(w=0.18, h=0.26, toe_h=0.1, tone=0.55, dark=0.85)),
             torso=[dict(bottom=-3.35, grow=0.05, tone=0.0, dark=0.25, with_arms=True),
                    dict(bottom=-3.45, top=0.99, grow=0.08, tone=0.45, dark=0.78, extra=_vest)])
    return figure(v, d, e, lw, neutral, bust)
