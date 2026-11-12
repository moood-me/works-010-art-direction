"""Кира, about 15: prickly, closed, defiant, vulnerable underneath. A longer face than a child's, narrow, a small
pointed chin; eyes smaller than Аня's, a sharp upper lid, a shadow under them; straight low brows; the mouth pressed
shut, a crooked half-smirk at most; the head a little down, the look from under the brows, sideways. Short choppy
dark hair, a long fringe falling over one eye (strands, with the eye seen between them)."""
from features import *
from hair import Hair

HEAD = dict(
    sections=sections(cranium=0.95, cheek=0.93, jaw=0.82, chin=0.72, depth=0.96, face=1.02, hollow=0.02),
    nose=dict(profile=[(0.0, 0.006, 0.024), (0.08, 0.035, 0.028), (0.17, 0.09, 0.036), (0.19, 0.085, 0.04), (0.215, 0.012, 0.04)],
              tip=0.175, wing=0.044, bridge_from=0.4),
    eye=dict(x=0.132, y=0.0, w=0.062, h=0.03, crease=0.45, iris=0.55, peak=-0.05, bag=0.3, tilt=0.04),
    brow=dict(x0=0.05, x1=0.225, y=-0.07, arch=0.008, th=0.85, slope=0.0),
    mouth=dict(y=0.3, w=0.07, lower=0.026, upper_line=1),
    ear=dict(y=0.07, h=0.22, w=0.11),
    neck=dict(rx=0.12, rz=0.14),
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
from body import *

HEIGHT = 6.95


def FIGURE(F, e=None, head=True):
    """The slouch: shoulders rounded, the head down and forward, the look from under the brows; the weight on one leg,
    the other knee in. An oversized dark hoodie, a backpack strap held at the chest by the far hand, a phone in the
    near hand half hidden by the sleeve; headphones round the neck (white: her one bright accent); narrow trousers,
    heavy boots with white laces."""
    me = __import__('chars.kira', fromlist=['x'])
    o = []
    pit = (0.22, -5.82)
    hv = dict(yaw=24, pitch=12, roll=-4, e=e)
    if head:
        o.append(head_on(F, me, pit, hair='back', **hv))
    hood = 0.72
    # backpack behind the far shoulder
    o.append(shaded(F, [(0.55, -5.85), (1.05, -5.6), (1.12, -4.2), (0.7, -4.0)], base=0.4, dark=0.8, off=(0.05, 0.02)))
    # legs: narrow dark trousers
    tr = 0.6
    lg, _ = limb(F, [(0.30, -3.4), (0.22, -1.85), (0.36, -0.42)], [0.15, (0.12, 0.12), 0.1], fill=f'url(#{tone_id(tr)})', ends=(False, True))
    o.append(lg)
    o.append(shoe(F, (0.28, -0.12), (0.62, -0.02), h=0.3, kind='boot', fill=INK))
    o.append(line(F, [(0.40, -0.35), (0.5, -0.32)], 0.4) + line(F, [(0.41, -0.27), (0.52, -0.23)], 0.4))
    lg, _ = limb(F, [(-0.18, -3.4), (-0.16, -1.85), (-0.16, -0.4)], [0.16, (0.13, 0.12), 0.1], fill=f'url(#{tone_id(tr)})', ends=(False, True))
    o.append(lg)
    o.append(folds(F, [[(-0.26, -1.95), (-0.08, -1.8)], [(0.12, -1.95), (0.3, -1.85)], [(-0.24, -0.7), (-0.06, -0.6)]], 0.6))
    o.append(shoe(F, (-0.36, 0.0), (0.12, 0.05), h=0.32, kind='boot', fill=INK))
    for k in range(3):
        o.append(stroke(F.P([(-0.1 + k * 0.05, -0.36 + k * 0.07), (0.04 + k * 0.05, -0.33 + k * 0.07)]), F.lw * 1.2, fill=PAPER))
    # hoodie: oversized, hanging off the slouched shoulders
    body = [(-0.05, -5.88), (-0.48, -5.72), (-0.70, -5.4), (-0.74, -4.6), (-0.66, -3.75), (-0.62, -3.3), (0.1, -3.18),
            (0.72, -3.3), (0.7, -3.9), (0.72, -4.7), (0.68, -5.45), (0.5, -5.78)]
    o.append(shaded(F, body, base=hood, dark=0.9, off=(0.08, 0.03), black=True))
    o.append(shape(F, [(-0.62, -3.55), (0.68, -3.55), (0.72, -3.3), (0.1, -3.18), (-0.62, -3.3)], fill=f'url(#{tone_id(0.82)})', line=0.6))
    o.append(folds(F, [[(-0.5, -4.2), (-0.2, -3.9)], [(0.5, -4.4), (0.25, -4.0)], [(-0.2, -5.0), (0.0, -4.6)]], 0.8).replace(f'fill="{INK}"', f'fill="{PAPER}"'))
    # pocket
    o.append(line(F, [(-0.45, -4.35), (0.45, -4.4)], 0.6).replace(f'fill="{INK}"', f'fill="{PAPER}"'))
    # hood folded behind the neck
    o.append(shaded(F, [(-0.32, -5.95), (0.0, -6.15), (0.5, -6.05), (0.55, -5.75), (0.2, -5.85), (-0.1, -5.8)], base=hood, dark=0.9, off=(0.04, 0.03), black=True))
    # strings
    o.append(line(F, [(0.05, -5.8), (0.0, -5.2)], 0.5).replace(f'fill="{INK}"', f'fill="{PAPER}"') + line(F, [(0.28, -5.82), (0.3, -5.25)], 0.5).replace(f'fill="{INK}"', f'fill="{PAPER}"'))
    # backpack strap over the far shoulder, the far hand holding it
    o.append(shape(F, [(0.38, -5.82), (0.56, -5.86), (0.6, -4.4), (0.46, -4.38)], fill=f'url(#{tone_id(0.35)})', line=0.7))
    sl, _ = limb(F, [(0.62, -5.55), (0.72, -4.9), (0.52, -4.75)], [0.17, 0.16, 0.15], fill=f'url(#{tone_id(hood)})', ends=(False, True))
    o.append(sl)
    o.append(hand(F, (0.48, -4.78), 250, 0.48, 'hold', side=-1, twist=120))
    # near arm hanging, the sleeve over half the hand, a phone
    sl, _ = limb(F, [(-0.62, -5.5), (-0.78, -4.75), (-0.76, -4.05), (-0.66, -3.45)], [0.2, 0.18, 0.17, 0.16],
                 fill=f'url(#{tone_id(hood)})', ends=(False, True))
    o.append(sl)
    o.append(folds(F, [[(-0.88, -4.2), (-0.7, -4.05)], [(-0.82, -3.7), (-0.62, -3.6)]], 0.6).replace(f'fill="{INK}"', f'fill="{PAPER}"'))
    o.append(shape(F, [(-0.72, -3.4), (-0.52, -3.42), (-0.5, -3.0), (-0.7, -2.98)], fill=INK, line=0.5, smooth=False))
    o.append(hand(F, (-0.66, -3.42), 95, 0.46, 'hold', side=1, twist=60))
    if head:
        o.append(head_on(F, me, pit, hair='front', **hv))
    # headphones round the neck (over the hood and the hair at the back)
    hp = [(-0.18, -5.95), (-0.05, -5.75), (0.25, -5.72), (0.45, -5.9)]
    o.append(line(F, hp, 3.2).replace(f'fill="{INK}"', f'fill="{INK}"'))
    o.append(line(F, hp, 1.6).replace(f'fill="{INK}"', f'fill="{PAPER}"'))
    o.append(shape(F, [(-0.32, -6.02), (-0.1, -6.1), (-0.04, -5.82), (-0.24, -5.74)], line=1.2))
    o.append(shape(F, [(0.36, -6.0), (0.56, -6.02), (0.6, -5.8), (0.42, -5.72)], line=1.2))
    return ''.join(o)
