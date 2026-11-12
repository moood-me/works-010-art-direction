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
from body import *

HEIGHT = 7.4


def FIGURE(F, e=None, head=True):
    """Laughing with the whole body: leaning back, the ladle up in the far hand, the near fist on his hip; a white
    double-breasted cook's jacket with the sleeves rolled up, a long apron, a towel over the shoulder."""
    me = __import__('chars.marat', fromlist=['x'])
    o = []
    pit = (-0.05, -6.28)
    hv = dict(yaw=24, pitch=-12, roll=6, e=e)
    if head:
        o.append(head_on(F, me, pit, hair='back', **hv))
    # far arm raised with the ladle
    sl, _ = limb(F, [(0.85, -5.95), (1.32, -6.45)], [0.27, 0.25], ends=(False, True))
    arm, _ = limb(F, [(1.30, -6.42), (1.42, -7.0), (1.36, -7.55)], [0.2, 0.19, 0.15], shade=hatch(None, (0, 0, 1, 1)))
    o.append(arm + sl)
    o.append(line(F, [(1.32, -7.1), (1.3, -9.0)], 1.4, smooth=False) + line(F, [(1.38, -7.1), (1.36, -9.0)], 1.2, smooth=False))
    bowl = [(1.05, -9.0), (1.6, -9.0), (1.55, -9.25), (1.33, -9.38), (1.1, -9.25)]
    o.append(shaded(F, bowl, base=0.0, dark=0.4, off=(0.04, 0.03)))
    o.append(hand(F, (1.36, -7.55), 270, 0.66, 'hold', side=-1, twist=80))
    # legs, wide stance
    tr = 0.62
    lg, _ = limb(F, [(0.48, -3.6), (0.66, -1.95), (0.74, -0.32)], [0.28, 0.24, 0.21], fill=f'url(#{tone_id(tr)})', ends=(False, True))
    o.append(lg)
    o.append(shoe(F, (0.52, -0.06), (1.22, -0.02), h=0.2))
    lg, _ = limb(F, [(-0.48, -3.6), (-0.62, -1.95), (-0.66, -0.3)], [0.29, 0.25, 0.22], fill=f'url(#{tone_id(tr)})', ends=(False, True))
    o.append(lg)
    o.append(shoe(F, (-0.9, 0.0), (-0.1, 0.05), h=0.2))
    # jacket: the barrel of the body, leaning back, the belly forward
    jacket = [(-0.25, -6.32), (-0.75, -6.2), (-1.05, -5.95), (-1.12, -5.2), (-1.0, -4.3), (-0.98, -3.6), (-0.1, -3.42),
              (0.85, -3.55), (1.08, -4.3), (1.18, -5.0), (1.08, -5.7), (0.85, -6.05), (0.4, -6.3)]
    o.append(shaded(F, jacket, base=0.0, dark=0.22, off=(0.1, 0.04)))
    # double row of buttons, the overlap
    o.append(line(F, [(0.42, -6.1), (0.55, -5.2), (0.62, -4.3)], 0.6))
    for y, x0 in ((-5.8, 0.18), (-5.25, 0.26), (-4.7, 0.32)):
        for dx in (0.0, 0.5):
            X, Y = F.p(x0 + dx * (1 - 0.2), y)
            o.append(f'<circle cx="{f1(X)}" cy="{f1(Y)}" r="{f1(F.lw * 1.6)}" fill="{PAPER}" stroke="{INK}" stroke-width="{F.lw * 0.55:.1f}"/>')
    # collar
    o.append(shape(F, [(-0.25, -6.32), (0.4, -6.3), (0.38, -6.12), (-0.22, -6.14)], line=0.8))
    # apron: from the chest down below the knee, terracotta as a mid tone
    apron = [(-0.62, -5.0), (0.85, -5.05), (0.96, -4.2), (1.0, -3.0), (1.05, -1.6), (0.2, -1.45), (-0.75, -1.55), (-0.82, -3.0), (-0.78, -4.2)]
    o.append(shaded(F, apron, base=0.32, dark=0.6, off=(0.08, 0.02)))
    o.append(folds(F, [[(-0.4, -3.4), (-0.45, -2.4), (-0.4, -1.6)], [(0.4, -3.6), (0.5, -2.5), (0.55, -1.55)], [(0.05, -3.2), (0.0, -1.5)]], 0.8))
    o.append(line(F, [(-0.62, -5.0), (-0.85, -5.6), (-0.6, -6.1)], 0.8) + line(F, [(0.85, -5.05), (0.9, -5.7), (0.6, -6.08)], 0.8))
    o.append(line(F, [(-0.8, -4.25), (0.97, -4.2)], 0.9))
    # towel over the near shoulder, striped
    towel = [(-0.75, -6.25), (-0.4, -6.3), (-0.5, -5.4), (-0.65, -4.7), (-0.95, -4.75), (-0.95, -5.5), (-1.05, -6.0)]
    o.append(shaded(F, towel, base=0.1, dark=0.35, off=(0.04, 0.02), extra=''.join(tonef(F, [(-1.2, y), (-0.2, y - 0.08), (-0.2, y + 0.05), (-1.2, y + 0.13)], 0.5, smooth=False) for y in (-5.15, -4.95))))
    # near arm: rolled sleeve, the thick forearm, the fist on the hip
    sl, _ = limb(F, [(-1.0, -5.9), (-1.4, -5.2)], [0.28, 0.27], ends=(False, True))
    arm, _ = limb(F, [(-1.38, -5.25), (-1.5, -4.85), (-1.1, -4.3)], [0.21, 0.2, 0.15],
                  shade=hatchf(F, [(-1.7, -5.3), (-0.9, -5.3), (-0.9, -4.2), (-1.7, -4.2)], angle=60, gap=0.05, w=0.3, seed=8))
    o.append(arm + sl)
    o.append(shape(F, [(-1.2, -5.55), (-1.62, -5.25), (-1.52, -5.05), (-1.12, -5.35)], line=0.8))
    o.append(hand(F, (-1.1, -4.3), 20, 0.68, 'fist', side=1, twist=40))
    if head:
        o.append(head_on(F, me, pit, hair='front', hs=1.0, **hv))
    return ''.join(o)
