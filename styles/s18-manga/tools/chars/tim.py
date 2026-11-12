"""Тим, about 8: mischievous, curious. A child's head — the cranium big, the face small and low, round full cheeks,
a small chin, a button nose with freckles and a plaster; black hair sticking up; a crooked grin."""
from features import *
from hair import Hair

_t = sections(cranium=1.04, cheek=1.06, jaw=1.0, chin=0.95, depth=0.96, face=0.80)
_t = [((y * 1.14 if y < 0 else y),) + tuple(r) for y, *r in _t]
HEAD = dict(
    sections=_t,
    nose=dict(profile=[(0.02, 0.004, 0.025), (0.08, 0.02, 0.03), (0.135, 0.06, 0.042), (0.155, 0.055, 0.045), (0.175, 0.01, 0.045)],
              tip=0.14, wing=0.045, bridge_from=0.7),
    eye=dict(x=0.135, y=0.0, w=0.066, h=0.04, crease=0.5, iris=0.55, peak=-0.1),
    brow=dict(x0=0.05, x1=0.22, y=-0.085, arch=0.02, th=0.9),
    mouth=dict(y=0.235, w=0.075, lower=0.022),
    ear=dict(y=0.05, h=0.22, w=0.12),
    neck=dict(rx=0.12, rz=0.13),
    jaw=dict(angle_y=0.33),
    rest=dict(smirk=0.8, brow_out=0.3, brow_in=-0.2, look=(0.3, 0.0)),
    shade=dict(level=0.14),
)
HAIR = Hair(mode='black', part=20, n=120, width=0.075, thick=0.05, top_thick=0.07, spike=0.11,
            hl=[(0, -0.36), (40, -0.33), (75, -0.2), (100, -0.05), (130, 0.05), (180, 0.12)],
            wave=0.02, waves=1.0, streaks=1.0, seed=41, cap_y=-0.36,
            locks=[dict(pts=[(x, -0.5, z), (x * 1.3, -0.62, z * 1.2 - 0.05), (x * 1.5 + 0.04, -0.69, z * 1.3 - 0.12)], w=0.07) for x, z in [(-0.1, -0.1), (0.05, -0.15), (0.15, -0.05), (-0.18, -0.25), (0.1, -0.3), (0.0, 0.05)]])
EXTRAS = [freckles(16), plaster(x=0.02, y=0.06, w=0.06, hgt=0.02, ang=-20), cheek_blush(0.7, y=0.11)]


# ---------------------------------------------------------------- the figure
from body import *

HEIGHT = 5.4


def FIGURE(F, e=None, head=True):
    """Leaning forward, pointing at something ahead with the far hand, a slingshot in the near hand, one foot up on
    its toes; a striped T-shirt, shorts, plasters on the knees, sneakers."""
    me = __import__('chars.tim', fromlist=['x'])
    o = []
    pit = (0.30, -4.42)
    hv = dict(yaw=30, pitch=-4, roll=4, e=e)
    if head:
        o.append(head_on(F, me, pit, hair='back', **hv))
    # far leg stepping forward
    lg, _ = limb(F, [(0.36, -2.55), (0.58, -1.45), (0.66, -0.28)], [0.15, (0.12, 0.11), (0.08, 0.07)])
    o.append(lg)
    o.append(limb(F, [(0.62, -0.62), (0.66, -0.25)], [0.085, 0.08], ends=(True, False))[0])
    o.append(shoe(F, (0.5, -0.04), (1.0, -0.01), h=0.17, kind='sneaker'))
    # near leg on tiptoe behind
    lg, _ = limb(F, [(-0.12, -2.55), (-0.30, -1.4), (-0.52, -0.42)], [0.16, (0.12, 0.12), (0.08, 0.07)])
    o.append(lg)
    o.append(limb(F, [(-0.47, -0.72), (-0.52, -0.40)], [0.085, 0.08], ends=(True, False))[0])
    o.append(shape(F, [(-0.42, -1.55), (-0.2, -1.6), (-0.2, -1.42), (-0.42, -1.38)], line=0.5))
    o.append(shoe(F, (-0.76, -0.35), (-0.22, 0.02), h=0.16, kind='sneaker'))
    # shorts
    shorts = [(-0.42, -3.1), (0.48, -3.15), (0.56, -2.6), (0.72, -2.15), (0.30, -2.0), (0.14, -2.4), (-0.02, -2.0), (-0.48, -2.1), (-0.45, -2.6)]
    o.append(shaded(F, shorts, base=0.55, dark=0.8, off=(0.06, 0.02)))
    o.append(folds(F, [[(0.12, -2.95), (0.14, -2.45)], [(0.4, -2.5), (0.55, -2.25)]], 0.6))
    # T-shirt, striped
    tee = [(0.04, -4.48), (-0.32, -4.38), (-0.56, -4.2), (-0.52, -3.6), (-0.46, -2.92), (0.1, -2.82), (0.60, -2.95),
           (0.64, -3.6), (0.70, -4.15), (0.52, -4.38), (0.38, -4.46), (0.22, -4.32)]
    P = F.P(tee)
    stripes = ''.join(tonef(F, [(-1, -4.4 + k * 0.24), (1.5, -4.48 + k * 0.24), (1.5, -4.36 + k * 0.24), (-1, -4.28 + k * 0.24)], 0.55, smooth=False) for k in range(8))
    o.append(shaded(F, tee, base=0.0, dark=0.3, off=(0.06, 0.02), extra=stripes))
    o.append(folds(F, [[(-0.3, -3.1), (-0.05, -3.0)], [(0.35, -3.3), (0.6, -3.25)]], 0.6))
    o.append(line(F, [(0.04, -4.48), (0.12, -4.36), (0.22, -4.32), (0.38, -4.46)], 0.7))
    # near arm, the slingshot hanging from the hand
    sl, _ = limb(F, [(-0.46, -4.3), (-0.6, -4.0)], [0.15, 0.14], fill=PAPER, ends=(False, True))
    arm, _ = limb(F, [(-0.56, -4.0), (-0.64, -3.4), (-0.56, -2.82)], [0.105, 0.09, 0.075])
    o.append(arm + sl)
    sx, sy = -0.52, -2.5
    o.append(line(F, [(sx - 0.05, sy - 0.05), (sx, sy + 0.35)], 1.6, smooth=False))
    o.append(line(F, [(sx, sy + 0.35), (sx - 0.15, sy + 0.62)], 1.4) + line(F, [(sx, sy + 0.35), (sx + 0.12, sy + 0.64)], 1.4))
    o.append(line(F, [(sx - 0.15, sy + 0.62), (sx - 0.05, sy + 0.95), (sx + 0.12, sy + 0.64)], 0.4))
    o.append(hand(F, (-0.56, -2.82), 92, 0.48, 'hold', side=1, twist=95))
    # far arm pointing ahead
    sl, _ = limb(F, [(0.52, -4.3), (0.78, -4.12)], [0.14, 0.13], ends=(False, True))
    arm, _ = limb(F, [(0.74, -4.14), (1.02, -4.0), (1.34, -4.22)], [0.1, 0.09, 0.075])
    o.append(arm + sl)
    o.append(hand(F, (1.34, -4.22), -30, 0.48, 'point', side=-1, twist=60))
    if head:
        o.append(head_on(F, me, pit, hair='front', **hv))
    return ''.join(o)
