"""Аня, about 20: warm, trusting, dreamy. An oval face with a soft jaw, a small slightly upturned nose, full lower lip;
light-brown hair to below the shoulders, parted on one side, a lock falling by the cheek; eyes a little larger than
the others', a lash at the outer corner, looking a little up and away."""
from features import *
from hair import Hair

HEAD = dict(
    sections=sections(cranium=0.97, cheek=0.97, jaw=0.9, chin=0.85, depth=0.97, face=0.96, hollow=0.0),
    nose=dict(profile=[(0.0, 0.006, 0.026), (0.08, 0.03, 0.03), (0.165, 0.085, 0.04), (0.185, 0.08, 0.045), (0.21, 0.015, 0.045)],
              tip=0.17, wing=0.05, bridge_from=0.55),
    eye=dict(x=0.135, y=0.0, w=0.07, h=0.041, crease=0.75, lash=1, iris=0.52, peak=-0.2),
    brow=dict(x0=0.05, x1=0.235, y=-0.09, arch=0.025, th=0.75, slope=0.01),
    mouth=dict(y=0.29, w=0.082, lower=0.03, upper_line=1, lip=0.02),
    ear=dict(y=0.07, h=0.22, w=0.11),
    neck=dict(rx=0.13, rz=0.15),
    jaw=dict(angle_y=0.40),
    rest=dict(smile=0.18, look=(-0.15, -0.25), open=0.95),
    shade=dict(level=0.14),
)
HAIR = Hair(mode='tone', part=-28, n=170, width=0.075, thick=0.055, top_thick=0.07,
            hl=[(0, -0.31), (35, -0.28), (70, -0.17), (95, -0.06), (120, 0.0), (180, 0.08)],
            end=[(0, -0.31), (62, -0.17), (80, 0.2), (105, 0.62), (135, 0.95), (180, 1.0)],
            end_neg=[(0, -0.31), (62, -0.17), (100, -0.02), (118, 0.6), (140, 0.95), (180, 1.0)],
            hl_neg=[(0, -0.31), (35, -0.28), (70, -0.17), (95, -0.08), (115, 0.0), (180, 0.08)],
            hang_out=0.12, wave=0.02, waves=1.5, tone_level=0.15, flow=0.8, streaks=1.2, edge=0.05, sweep=6, seed=21)
EXTRAS = [cheek_blush(0.8)]


# ---------------------------------------------------------------- the figure (three-quarter, facing right)
from body import *

HEIGHT = 7.1


def FIGURE(F, e=None, head=True):
    """Standing with her weight on the near leg, the hip out, a book held to her chest, the other hand loose;
    the head tilted, looking up and away."""
    me = __import__('chars.anya', fromlist=['x'])
    o = []
    pit = (0.06, -6.08)
    hv = dict(yaw=28, pitch=-5, roll=-8, e=e)
    if head:
        o.append(head_on(F, me, pit, hair='back', **hv))
    knit = lambda pts, sd: hatchf(F, pts, angle=88, gap=0.045, w=0.28, seed=sd)
    # far arm: the upper arm, behind the body
    sl, _ = limb(F, [(0.50, -5.86), (0.60, -5.2), (0.56, -4.72)], [0.15, 0.13, 0.12], fill=f'url(#{tone_id(0.12)})')
    o.append(sl)
    # legs below the skirt
    lg, _ = limb(F, [(0.26, -2.4), (0.38, -1.35), (0.47, -0.3)], [0.13, 0.115, 0.06])
    o.append(lg)
    o.append(shoe(F, (0.36, -0.06), (0.74, -0.02), h=0.12))
    lg, _ = limb(F, [(-0.22, -2.4), (-0.21, -1.3), (-0.17, -0.28)], [0.135, 0.12, 0.062])
    o.append(lg)
    o.append(line(F, [(-0.28, -1.9), (-0.2, -1.85)], 0.4))
    o.append(shoe(F, (-0.32, 0.0), (0.08, 0.035), h=0.13))
    # skirt: A-line to below the knee, a soft tone, folds from the waist
    skirt = [(-0.44, -4.45), (-0.1, -4.38), (0.24, -4.4), (0.44, -4.5), (0.56, -3.6), (0.72, -2.8), (0.84, -2.2),
             (0.5, -2.1), (0.15, -2.16), (-0.2, -2.08), (-0.55, -2.15), (-0.86, -2.2), (-0.78, -3.0), (-0.62, -3.8)]
    o.append(shaded(F, skirt, base=0.2, dark=0.45, off=(0.09, 0.02)))
    o.append(folds(F, [[(-0.25, -4.0), (-0.38, -3.0), (-0.52, -2.18)], [(0.12, -4.1), (0.12, -3.0), (0.18, -2.15)],
                       [(0.36, -3.7), (0.5, -2.8), (0.5, -2.12)], [(-0.05, -3.4), (-0.12, -2.6), (-0.15, -2.1)]], 0.8))
    # blouse in the opening of the cardigan
    blouse = [(-0.16, -6.08), (0.24, -6.08), (0.26, -4.42), (-0.24, -4.40)]
    o.append(shape(F, blouse, line=0.5))
    o.append(line(F, [(-0.13, -6.05), (0.03, -5.82), (0.22, -6.05)], 0.6))
    # cardigan, fitted, to the hip
    card_l = [(-0.16, -6.1), (-0.46, -6.0), (-0.62, -5.84), (-0.6, -5.1), (-0.46, -4.5), (-0.58, -3.95), (-0.18, -3.86),
              (-0.1, -4.45), (-0.05, -5.1), (-0.08, -5.75)]
    card_r = [(0.24, -6.1), (0.44, -6.02), (0.56, -5.86), (0.52, -5.1), (0.44, -4.55), (0.52, -3.98), (0.26, -3.9),
              (0.20, -4.45), (0.17, -5.1), (0.2, -5.75)]
    o.append(shaded(F, card_r, base=0.12, dark=0.4, off=(0.06, 0.03), extra=knit(card_r, 4)))
    o.append(shaded(F, card_l, base=0.12, dark=0.4, off=(0.06, 0.03), extra=knit(card_l, 5)))
    for y in (-5.5, -5.0, -4.5):
        o.append(f'<circle cx="{f1(F.p(-0.09, y)[0])}" cy="{f1(F.p(-0.09, y)[1])}" r="{f1(F.lw * 1.3)}" fill="{PAPER}" stroke="{INK}" stroke-width="{F.lw * 0.5:.1f}"/>')
    o.append(folds(F, [[(-0.52, -4.75), (-0.36, -4.55), (-0.2, -4.5)], [(0.44, -4.75), (0.3, -4.58)]], 0.7))
    # near arm hanging, the sleeve gathered at the wrist, the hand loose
    sl, _ = limb(F, [(-0.56, -5.86), (-0.70, -5.1), (-0.74, -4.52), (-0.66, -3.68)], [0.17, 0.145, 0.13, 0.115],
                 fill=f'url(#{tone_id(0.12)})', ends=(False, True))
    o.append(sl)
    o.append(folds(F, [[(-0.82, -4.62), (-0.68, -4.45)], [(-0.8, -4.85), (-0.66, -4.72)], [(-0.74, -3.9), (-0.6, -3.82)]], 0.6))
    o.append(hand(F, (-0.66, -3.66), 98, 0.56, 'relaxed', side=1, twist=95))
    # the book held to the chest by the far hand
    book = [(-0.2, -5.42), (0.36, -5.5), (0.44, -4.68), (-0.12, -4.6)]
    o.append(shaded(F, book, base=0.45, dark=0.75, off=(0.03, 0.02), smooth=False))
    o.append(line(F, [(-0.17, -5.33), (0.35, -5.41)], 0.35, smooth=False))
    o.append(line(F, [(-0.12, -4.6), (-0.1, -4.53), (0.44, -4.6)], 0.5, smooth=False))
    fa, _ = limb(F, [(0.56, -4.75), (0.38, -4.78), (0.16, -5.0)], [0.12, 0.115, 0.1], fill=f'url(#{tone_id(0.12)})', ends=(False, True))
    o.append(fa)
    o.append(hand(F, (0.15, -5.0), 215, 0.5, 'loose', side=1, twist=10))
    if head:
        o.append(head_on(F, me, pit, hair='front', **hv))
    return ''.join(o)
