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
from body import *

HEIGHT = 6.85


def FIGURE(F, e=None, head=True):
    """Stooped, the head forward and down over a pocket watch held in the near hand; the far hand behind his back.
    A white shirt, a knitted vest, a bow tie, baggy trousers, old shoes."""
    me = __import__('chars.sav', fromlist=['x'])
    o = []
    pit = (0.30, -5.78)
    hv = dict(yaw=30, pitch=10, roll=3, e=e)
    if head:
        o.append(head_on(F, me, pit, hair='back', **hv))
    # far arm going behind the back
    sl, _ = limb(F, [(0.72, -5.55), (0.86, -4.9), (0.8, -4.45)], [0.17, 0.16, 0.15])
    o.append(sl)
    # far leg, near leg: baggy trousers in a light tone
    tr = 0.22
    lg, _ = limb(F, [(0.36, -3.55), (0.48, -1.95), (0.56, -0.32)], [0.22, 0.19, (0.16, 0.18)], fill=f'url(#{tone_id(tr)})', ends=(False, True))
    o.append(lg)
    o.append(shoe(F, (0.40, -0.06), (0.98, -0.02), h=0.17))
    lg, _ = limb(F, [(-0.28, -3.55), (-0.33, -1.95), (-0.30, -0.3)], [0.23, 0.2, (0.17, 0.19)], fill=f'url(#{tone_id(tr)})', ends=(False, True))
    o.append(lg)
    o.append(folds(F, [[(-0.4, -2.1), (-0.25, -1.85)], [(-0.42, -1.0), (-0.22, -0.8)], [(-0.4, -0.6), (-0.2, -0.5)], [(0.42, -2.0), (0.6, -1.8)], [(0.5, -0.9), (0.68, -0.75)]], 0.7))
    o.append(shoe(F, (-0.5, 0.0), (0.16, 0.05), h=0.18))
    # shirt back and the vest
    shirt = [(-0.25, -5.85), (0.42, -5.85), (0.5, -4.7), (-0.2, -4.6)]
    o.append(shape(F, shirt, line=0.6))
    vest = [(-0.18, -5.82), (-0.55, -5.62), (-0.70, -5.0), (-0.70, -4.2), (-0.62, -3.55), (0.02, -3.42), (0.72, -3.52),
            (0.86, -4.2), (0.84, -4.9), (0.74, -5.55), (0.42, -5.8), (0.26, -5.0), (0.12, -4.62)]
    o.append(shaded(F, vest, base=0.45, dark=0.75, off=(0.07, 0.03),
                    extra=hatchf(F, vest, angle=80, gap=0.06, w=0.3, seed=12)))
    o.append(line(F, [(0.12, -4.62), (0.08, -3.45)], 0.6))
    for y in (-4.4, -4.05, -3.7):
        X, Y = F.p(0.1 + (y + 4.4) * 0.0, y)
        o.append(f'<circle cx="{f1(X)}" cy="{f1(Y)}" r="{f1(F.lw * 1.4)}" fill="{PAPER}" stroke="{INK}" stroke-width="{F.lw * 0.5:.1f}"/>')
    o.append(folds(F, [[(-0.6, -4.0), (-0.35, -3.9)], [(0.6, -3.95), (0.8, -4.05)], [(0.2, -4.2), (0.55, -4.3)]], 0.6))
    # collar and bow tie
    o.append(shape(F, [(-0.12, -5.86), (0.08, -5.62), (0.14, -5.75), (0.36, -5.88), (0.34, -5.95), (0.1, -5.82), (-0.1, -5.95)], line=0.7, smooth=False))
    o.append(shape(F, [(0.0, -5.66), (0.12, -5.6), (0.24, -5.68), (0.24, -5.52), (0.12, -5.58), (0.0, -5.5)], fill=INK, line=0.5, smooth=False))
    # watch chain into the vest pocket
    o.append(line(F, [(0.62, -4.4), (0.4, -4.25), (0.2, -4.45), (0.12, -4.8)], 0.45))
    # near arm: shirt sleeve, the forearm raised, the watch in the hand
    sl, _ = limb(F, [(-0.56, -5.55), (-0.76, -4.85), (-0.72, -4.3)], [0.2, 0.18, 0.17])
    o.append(sl)
    o.append(folds(F, [[(-0.86, -4.6), (-0.66, -4.45)], [(-0.84, -4.95), (-0.68, -4.85)]], 0.7))
    fa, _ = limb(F, [(-0.72, -4.32), (-0.42, -4.42), (-0.1, -4.62)], [0.17, 0.15, 0.13], ends=(False, True))
    o.append(fa)
    o.append(folds(F, [[(-0.55, -4.52), (-0.48, -4.3)]], 0.6))
    # the watch
    X, Y = F.p(0.1, -4.86); R = 0.15 * F.s
    o.append(f'<circle cx="{f1(X)}" cy="{f1(Y)}" r="{f1(R)}" fill="{PAPER}"/>' + outline([(X + R * math.cos(t), Y + R * math.sin(t)) for t in [k * math.pi / 12 for k in range(24)]], F.lw * 1.0, 0.5, smooth=False))
    o.append(f'<circle cx="{f1(X)}" cy="{f1(Y)}" r="{f1(R * 0.78)}" fill="none" stroke="{INK}" stroke-width="{F.lw * 0.35:.1f}"/>')
    o.append(stroke([(X, Y), (X + R * 0.05, Y - R * 0.55)], F.lw * 0.6) + stroke([(X, Y), (X + R * 0.42, Y + R * 0.1)], F.lw * 0.5))
    o.append(shape(F, [(0.06, -5.04), (0.14, -5.04), (0.14, -5.1), (0.06, -5.1)], line=0.5, smooth=False))
    o.append(hand(F, (-0.1, -4.62), 330, 0.6, 'hold', side=1, twist=200, tilt=10))
    if head:
        o.append(head_on(F, me, pit, hair='front', **hv))
    return ''.join(o)
