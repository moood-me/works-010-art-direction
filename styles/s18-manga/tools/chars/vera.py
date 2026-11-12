"""Вера, about 40: strict, clever, tired. A long narrow face, high cheekbones and a little hollow under them, a
defined jaw; a long straight nose; narrow eyes with tired lids and bags; thin lips, the corners down; thin
rectangular glasses; black hair pulled back hard into a bun, one strand loose at the temple."""
from features import *
from hair import Hair

HEAD = dict(
    sections=sections(cranium=0.96, cheek=0.97, jaw=0.88, chin=0.86, depth=1.0, face=1.08, hollow=0.06, jaw_angle=0.2),
    nose=dict(profile=[(-0.01, 0.012, 0.025), (0.08, 0.06, 0.03), (0.18, 0.115, 0.038), (0.2, 0.105, 0.042), (0.235, 0.015, 0.045)],
              tip=0.195, wing=0.048, bridge_from=0.25),
    eye=dict(x=0.135, y=0.0, w=0.066, h=0.029, crease=0.8, lash=1, bag=0.6, iris=0.5, tilt=0.06, peak=-0.3),
    brow=dict(x0=0.05, x1=0.24, y=-0.075, arch=0.012, th=0.85, slope=0.015),
    mouth=dict(y=0.325, w=0.08, lower=0.025, upper_line=1),
    ear=dict(y=0.08, h=0.23, w=0.11),
    neck=dict(rx=0.125, rz=0.15),
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
from body import *

HEIGHT = 7.5


def FIGURE(F, e=None, head=True):
    """Upright, a folder held against her hip by the near arm, the far hand at her glasses; a long dark coat open
    over a high-collared blouse and a straight skirt."""
    me = __import__('chars.vera', fromlist=['x'])
    o = []
    pit = (0.08, -6.42)
    hv = dict(yaw=26, pitch=4, roll=0, e=e)
    if head:
        o.append(head_on(F, me, pit, hair='back', **hv))
    coat = 0.62
    # far sleeve (behind the body, up to the face)
    sl, _ = limb(F, [(0.56, -6.15), (0.82, -5.3), (0.55, -6.0)], [0.17, 0.16, 0.14], fill=f'url(#{tone_id(coat)})')
    o.append(sl)
    # legs
    lg, _ = limb(F, [(0.22, -2.2), (0.26, -1.3), (0.30, -0.3)], [0.11, (0.11, 0.1), 0.055])
    o.append(lg)
    o.append(shoe(F, (0.2, -0.08), (0.66, -0.06), h=0.14))
    lg, _ = limb(F, [(-0.2, -2.2), (-0.2, -1.3), (-0.17, -0.28)], [0.115, (0.12, 0.1), 0.057])
    o.append(lg)
    o.append(shoe(F, (-0.34, 0.0), (0.1, 0.04), h=0.14))
    # skirt between the coat's edges
    o.append(shaded(F, [(-0.4, -4.6), (0.42, -4.62), (0.44, -2.1), (-0.4, -2.08)], base=0.5, dark=0.75, off=(0.05, 0.0)))
    # blouse
    o.append(shape(F, [(-0.2, -6.45), (0.3, -6.45), (0.32, -4.55), (-0.25, -4.55)], line=0.5))
    o.append(shape(F, [(-0.12, -6.48), (0.2, -6.5), (0.24, -6.22), (0.05, -6.15), (-0.14, -6.24)], line=0.7))
    o.append(line(F, [(0.05, -6.15), (0.06, -4.6)], 0.4))
    # the coat: near panel and far panel, lapels
    near = [(-0.12, -6.5), (-0.46, -6.38), (-0.62, -6.2), (-0.62, -5.2), (-0.54, -4.5), (-0.66, -3.2), (-0.70, -1.95),
            (-0.18, -1.85), (-0.12, -3.5), (-0.14, -4.6), (-0.05, -5.6), (-0.15, -6.1)]
    far = [(0.26, -6.5), (0.46, -6.4), (0.58, -6.2), (0.56, -5.2), (0.48, -4.55), (0.56, -3.2), (0.62, -1.98), (0.3, -1.9),
           (0.26, -3.5), (0.22, -4.6), (0.18, -5.6), (0.26, -6.1)]
    o.append(shaded(F, far, base=coat, dark=0.85, off=(0.07, 0.02), black=True))
    o.append(shaded(F, near, base=coat, dark=0.85, off=(0.07, 0.02), black=True))
    o.append(shape(F, [(-0.12, -6.5), (-0.28, -6.3), (-0.05, -5.6), (-0.15, -6.1)], fill=f'url(#{tone_id(0.75)})', line=0.7))
    o.append(folds(F, [[(-0.5, -4.4), (-0.35, -3.2), (-0.4, -2.0)], [(-0.3, -3.8), (-0.25, -2.6)], [(0.45, -4.2), (0.4, -2.0)]], 0.7))
    o.append(line(F, [(-0.56, -4.55), (-0.3, -4.6), (-0.12, -4.62)], 0.6))
    # near arm hanging, the folder against the hip under the hand
    sl, _ = limb(F, [(-0.56, -6.2), (-0.72, -5.4), (-0.74, -4.7), (-0.62, -4.05)], [0.18, 0.16, 0.15, 0.14],
                 fill=f'url(#{tone_id(coat)})', ends=(False, True))
    o.append(sl)
    o.append(folds(F, [[(-0.84, -4.8), (-0.66, -4.62)], [(-0.8, -5.1), (-0.66, -4.95)]], 0.6))
    folder = [(-0.95, -4.6), (-0.42, -4.75), (-0.32, -3.4), (-0.85, -3.25)]
    o.append(shaded(F, folder, base=0.15, dark=0.4, off=(0.03, 0.02), smooth=False))
    o.append(line(F, [(-0.92, -4.5), (-0.4, -4.65)], 0.4, smooth=False))
    o.append(hand(F, (-0.6, -4.02), 75, 0.56, 'hold', side=1, twist=110))
    if head:
        o.append(head_on(F, me, pit, hair='front', **hv))
    # the far hand at the glasses, over the face
    fa, _ = limb(F, [(0.62, -6.0), (0.42, -6.5), (0.3, -6.82)], [0.14, 0.13, 0.11], fill=f'url(#{tone_id(coat)})', ends=(False, True))
    o.append(fa)
    o.append(hand(F, (0.3, -6.82), 235, 0.52, 'point', side=-1, twist=70))
    return ''.join(o)
