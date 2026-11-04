"""Тим, about 8 — mischievous, curious. A round head, big round eyes, a dash of a nose, a wide mouth; thick dark hair
that sticks up in spikes with a cowlick on the crown; a plaster on the cheek."""
import numpy as np
from head import Head, profile
from hair import Hair

SKIN = '#f5d0b0'
HAIR = '#3d2d27'
IRIS = '#3b2a24'

FACE = dict(
    a=[(1.0, 0.0), (0.96, 0.31), (0.8, 0.58), (0.5, 0.72), (0.2, 0.74), (0.0, 0.735), (-0.2, 0.72), (-0.4, 0.68),
       (-0.6, 0.61), (-0.75, 0.51), (-0.88, 0.36), (-0.96, 0.19), (-1.0, 0.0)],
    zf=[(1.0, 0.05), (0.8, 0.44), (0.5, 0.60), (0.2, 0.63), (0.0, 0.62), (-0.2, 0.62), (-0.5, 0.58), (-0.7, 0.53),
        (-0.9, 0.44), (-1.0, 0.34)],
    zb=[(1.0, -0.05), (0.8, -0.74), (0.5, -0.90), (0.2, -0.90), (0.0, -0.82), (-0.2, -0.68), (-0.4, -0.38),
        (-0.6, -0.08), (-0.8, 0.04), (-1.0, 0.16)],
    prof=profile(-0.48, 0.07, bridge=0.02, mouth_y=-0.68),
    sigma=[(0.2, 0.10), (-0.3, 0.08), (-0.5, 0.18), (-0.8, 0.22)],
    eye_x=0.305, eye_y=-0.16, eye_w=0.30, eye_h=0.26, iris_w=0.098, iris_h=0.118, lashes=0, flick=0.3, lid_w=1.25,
    brow_y=0.25, brow_w=0.22, brow_th=2.0, brow_arch=0.03, nose_y=-0.47, nose='dash', nose_w=0.06,
    mouth_y=-0.68, mouth_w=0.12, ear_z=0.04, ear=(-0.06, -0.40), blush=0.3,
    marks=[],
)

_sp = [
    # the mass is swept back and down and ends in short jagged clumps; a cowlick stands up on the crown
    dict(root=(-170, 0.92), to=[(-0.02, 0.16, -0.10), (-0.10, 0.30, -0.12)], w=0.22, prof=1.2),
    dict(root=(175, 0.95), to=[(0.06, 0.14, -0.06), (0.15, 0.24, -0.10)], w=0.18, prof=1.2),
]
for t in [-180, -160, -140, 140, 160]:
    side = np.sign(t) if t not in (0, 180) else 0
    sp = 0.10 + 0.05 * ((t // 20) % 2)
    _sp.append(dict(root=(t, 0.05 if abs(t) > 110 else 0.15),
                    to=[(side * 0.04, -0.12, -0.04), (side * sp, -0.26 - 0.06 * ((t // 20) % 3), -0.06)],
                    w=0.30, prof=1.3, back=abs(t) > 120))


HAIRDEF = dict(
    tufts=[dict(ts=[t for t in range(-170, 180, 24) if abs(t) > 60], y=0.85, drop=0.55, w=0.30, out=0.10, swirl=12),
           dict(ts=[t for t in range(-158, 180, 28) if abs(t) > 60], y=0.45, drop=0.45, w=0.30, out=0.09, swirl=-10)],
    hairline=[(0, 0.56), (30, 0.54), (60, 0.40), (85, 0.15), (100, 0.10), (130, -0.05), (180, -0.15)],
    volume=[(-1, 0.10), (0, 0.14), (1, 0.20)],
    locks=[
        # a jagged fringe: three, four spikes falling over the forehead, pointing a little sideways
        dict(root=(-44, 0.80), to=[(-0.06, -0.22, 0.20), (-0.20, -0.46, 0.18)], w=0.26, line='r'),
        dict(root=(-18, 0.90), to=[(-0.02, -0.26, 0.26), (-0.12, -0.54, 0.26)], w=0.24, line='r'),
        dict(root=(8, 0.92), to=[(0.04, -0.24, 0.26), (0.06, -0.48, 0.27)], w=0.22),
        dict(root=(32, 0.86), to=[(0.08, -0.22, 0.22), (0.20, -0.48, 0.20)], w=0.24, line='l'),
        dict(root=(58, 0.72), to=[(0.10, -0.18, 0.14), (0.26, -0.40, 0.08)], w=0.22),
        dict(root=(-64, 0.70), to=[(-0.10, -0.24, 0.12), (-0.24, -0.52, 0.06)], w=0.28),
    ] + _sp,
)

PLASTER = [(0.22, -0.36), (0.36, -0.31), (0.40, -0.39), (0.26, -0.44)]


def head():
    return Head(FACE)


def hair(h):
    return Hair(h, HAIRDEF)


def extra(d, view, F, h, skin_g):
    """a plaster on the left cheek."""
    from geo import poly
    if float(h.facing(view, 0.31, -0.37)[0]) < 0.15:
        return
    P = np.array(PLASTER)
    g = poly(h.xy(view, h.on(P[:, 0], P[:, 1], 0.012))).buffer(0.002 * view.s * h.k).intersection(skin_g)
    d.fill(g, '#ead2b0')
    d.outline(g, d.lw * 0.6)
    for u in (-0.02, 0.02):
        c = np.array([(0.31 + u, -0.35), (0.31 + u + 0.01, -0.40)])
        d.line(h.xy(view, h.on(c[:, 0], c[:, 1], 0.014)), d.lw * 0.4, '#b0907a')


# ---------------------------------------------------------------- body
B = dict(
    hip_y=63, hip_x=6.3, thigh=29.5, shin=28, shoulder=(10.6, 98.5, -0.5), upper=20, fore=17, hand=12,
    arm_r=[3.0, 2.6, 2.3, 1.8], hand_r=1.75, leg_r=[5.4, 4.6, 3.6, 3.3, 3.7, 3.3, 2.4, 2.2],
    neck=(100.5, 109, -0.5, 0.5), neck_r=2.9, head_c=(0, 115.8, 1.6), head_h=22.5, chest_y=86,
    torso=[(56, 8, 5.5, -5.5), (63, 11.2, 6.8, -7), (71, 10.8, 6.8, -6.5), (79, 10.6, 7.0, -6.0), (87, 11.3, 7.0, -6.2),
           (93, 12.0, 6.5, -6.2), (97, 13.0, 5.5, -5.6), (99.5, 10.5, 4.6, -5.0), (102, 4.6, 3.1, -3.7)],
)

POSES = dict(
    stand=dict(
        arml=dict(upper=(0.12, -1, 0.02), fore=(0.05, -1, 0.15), hand=(0.0, -1, 0.1), palm=(-1, 0, 0.2)),
        armr=dict(upper=(0.12, -1, 0.02), fore=(0.05, -1, 0.15), hand=(0.0, -1, 0.1), palm=(-1, 0, 0.2)),
        legl=dict(thigh=(0.08, -1, 0.0), shin=(0.0, -1, -0.02)),
        legr=dict(thigh=(0.08, -1, 0.0), shin=(0.0, -1, -0.02)),
    ),
    hips=dict(
        # fists on the hips, feet apart, chin up: ready for mischief
        head_rot=(8, -6, -5),
        arml=dict(upper=(0.62, -0.75, -0.15), fore=(-0.55, -0.80, 0.12), hand=(-0.4, -0.6, 0.3), palm=(-1, 0, 0),
                  hand_kind='fist'),
        armr=dict(upper=(0.62, -0.75, -0.15), fore=(-0.55, -0.80, 0.12), hand=(-0.4, -0.6, 0.3), palm=(-1, 0, 0),
                  hand_kind='fist'),
        legl=dict(thigh=(0.16, -1, 0.02), shin=(0.04, -1, -0.03)),
        legr=dict(thigh=(0.16, -1, 0.02), shin=(0.04, -1, -0.03)),
    ),
)

SPEC = dict(
    skin=SKIN,
    top=dict(c='#f3efe4', ease=0.7, hem=61, sleeve=dict(upto=0.36, ease=1.2), stripe_c='#4a6890',
             stripes=[(62, 64.5), (67.5, 70), (73, 75.5), (78.5, 81), (84, 86.5), (89.5, 92), (95, 97.5)]),
    bottom=dict(kind='shorts', c='#b49a68', ease=1.4, waist=72, upto=0.45),
    socks='#f4f1ea',
    shoes=dict(c='#c9503e', len=19, r=3.0, out=12, sole='#f2ede4'),
)
