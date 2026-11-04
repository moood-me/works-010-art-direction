"""Вера, about 40 — strict, clever, tired. A longer face with a narrow chin and clear cheekbones, eyes under heavy
lids, thin straight brows, a straighter nose, a mouth with its corners a little down; dark hair parted on the side
and pulled back into a low knot, one strand fallen loose; small earrings."""
import numpy as np
from head import Head, Expr, profile
from hair import Hair
from svgdoc import INK, mix, shade

SKIN = '#f1d0b6'
HAIR = '#3a2c2e'
IRIS = '#3a2a2a'

FACE = dict(
    a=[(1.0, 0.0), (0.96, 0.27), (0.8, 0.52), (0.5, 0.65), (0.2, 0.67), (0.0, 0.66), (-0.2, 0.64), (-0.4, 0.595),
       (-0.6, 0.52), (-0.75, 0.42), (-0.88, 0.28), (-0.96, 0.14), (-1.0, 0.0)],
    zf=[(1.0, 0.05), (0.8, 0.44), (0.5, 0.60), (0.2, 0.63), (0.0, 0.62), (-0.2, 0.62), (-0.5, 0.58), (-0.7, 0.53),
        (-0.9, 0.44), (-1.0, 0.34)],
    zb=[(1.0, -0.05), (0.8, -0.72), (0.5, -0.88), (0.2, -0.88), (0.0, -0.80), (-0.2, -0.66), (-0.4, -0.36),
        (-0.6, -0.06), (-0.8, 0.06), (-1.0, 0.18)],
    prof=profile(-0.50, 0.15, bridge=0.06, mouth_y=-0.73),
    sigma=[(0.2, 0.10), (-0.3, 0.075), (-0.5, 0.16), (-0.8, 0.20)],
    eye_x=0.26, eye_y=-0.08, eye_w=0.27, eye_h=0.15, iris_w=0.072, iris_h=0.085, lashes=1, flick=0.8, lid_w=1.4,
    crease=0.55, eye_tilt=0.015,
    brow_y=0.22, brow_w=0.30, brow_th=1.0, brow_arch=0.012, nose_y=-0.50, nose='hook', nose_len=0.15, nose_w=0.07,
    mouth_y=-0.73, mouth_w=0.095, mouth_curve=-0.006, lower_lip=0.04, ear_z=0.04, ear=(-0.04, -0.38),
    marks=[
        dict(pts=[(0.17, -0.19), (0.26, -0.215), (0.35, -0.19)], w=0.45, op=0.6),     # tired lines under the eyes
    ],
)

# pulled back from a side part into a low knot at the nape; the front swept across; one strand fallen loose
HAIRDEF = dict(
    hairline=[(0, 0.62), (25, 0.60), (55, 0.45), (80, 0.20), (95, 0.04), (115, -0.20), (150, -0.45), (180, -0.50)],
    volume=[(-1, 0.08), (0, 0.11), (1, 0.15)],
    flow=[[(-28, 0.93), (20, 0.86), (55, 0.66), (85, 0.40), (120, 0.1), (160, -0.2)],
          [(-28, 0.93), (-55, 0.80), (-80, 0.55), (-115, 0.25), (-160, -0.15)],
          [(-28, 0.93), (-100, 0.88), (-150, 0.55), (-175, 0.2)], [(-28, 0.93), (60, 0.92), (120, 0.65), (165, 0.3)]],
    balls=[(180, -0.22, 0.33, 0.16)],
    locks=[
        # the front, swept from the part across the forehead to the left temple and back over the ear
        dict(root=(-28, 0.92), to=[(0.28, -0.04, 0.16), (0.56, -0.24, 0.12), (0.70, -0.48, -0.05)], w=0.44, line='l', prof=2.2),
        dict(root=(-34, 0.88), to=[(-0.14, -0.20, 0.14), (-0.30, -0.42, 0.06), (-0.50, -0.50, -0.20)], w=0.34, line='r', prof=2.2),
        # one strand fallen loose by the right cheek
        dict(root=(-55, 0.72), to=[(-0.06, -0.40, 0.12), (-0.02, -0.85, 0.10), (-0.08, -1.10, 0.06)], w=0.07, prof=1.0, front=True),
    ],
)


def head():
    return Head(FACE)


def hair(h):
    return Hair(h, HAIRDEF)


def extra(d, view, F, h, skin_g):
    """small gold earrings."""
    from shapely.geometry import Point
    for side in (-1, 1):
        a = float(h.a(-0.40))
        p = np.array([[side * (a - 0.01), -0.44, float(h.zm(-0.40)) + 0.06]])
        nrm = np.array([[side * 0.9, 0, 0.4]]) @ h.R.T
        if float(view.dir(nrm)[0, 2]) < -0.2:
            continue
        c = view.xy(h.to_model(p))[0]
        g = Point(c[0], c[1] + 0.03 * view.s * h.k).buffer(0.035 * view.s * h.k, 16)
        d.fill(g, '#d8b058')
        d.outline(g, d.lw * 0.5)


# ---------------------------------------------------------------- body
B = dict(
    hip_y=87, hip_x=8.5, thigh=41, shin=39, shoulder=(14.4, 135, -1.0), upper=28, fore=24, hand=16,
    arm_r=[3.9, 3.3, 2.8, 2.2], hand_r=2.1, leg_r=[7.2, 6.0, 4.4, 3.9, 4.4, 4.0, 2.9, 2.7],
    neck=(140.0, 147, -1.0, 0.5), neck_r=3.5, head_c=(0, 153.6, 1.8), head_h=23.5, chest_y=122,
    torso=[(79, 10.5, 7, -7), (87, 16.0, 8.5, -9.5), (96, 15.0, 8, -9), (106, 12.4, 7.0, -7.0), (115, 13.8, 8.6, -7.6),
           (123, 14.8, 10.0, -8.0), (130, 16.2, 9.0, -8.0), (134, 17.4, 7.4, -7.2), (137, 15.0, 5.8, -6.4),
           (139.5, 10.0, 4.5, -5.5), (141.5, 5.3, 3.5, -4.6)],
)

POSES = dict(
    stand=dict(
        arml=dict(upper=(0.07, -1, 0.02), fore=(0.05, -1, 0.14), hand=(0.0, -1, 0.1), palm=(-1, 0, 0.2)),
        armr=dict(upper=(0.07, -1, 0.02), fore=(0.05, -1, 0.14), hand=(0.0, -1, 0.1), palm=(-1, 0, 0.2)),
        legl=dict(thigh=(0.04, -1, 0.0), shin=(0.0, -1, -0.02)),
        legr=dict(thigh=(0.04, -1, 0.0), shin=(0.0, -1, -0.02)),
    ),
    crossed=dict(
        # arms crossed over the chest, weight on one leg, head a little tilted: waiting, unimpressed
        head_rot=(-6, 4, 4), hip_shift=1.5,
        arml=dict(upper=(0.10, -1, 0.42), fore=(-1, 0.22, 0.30), hand=(-1, 0.1, -0.2), palm=(0, 0, -1)),
        armr=dict(upper=(0.10, -1, 0.36), fore=(-1, 0.30, 0.42), hand=(-1, 0.2, -0.3), palm=(0, 0, -1),
                  hand_behind=True),
        legl=dict(thigh=(0.02, -1, 0.0), shin=(0.0, -1, -0.02)),
        legr=dict(thigh=(0.10, -1, 0.06), shin=(-0.02, -1, -0.06)),
    ),
)

SPEC = dict(
    skin=SKIN,
    top=dict(c='#dfe6ee', ease=0.5, hem=88, sleeve=dict(upto=1.0, ease=0.8), collar=3.4),
    over=dict(c='#4b5468', ease=1.4, hem=84, open=(0.10, 0.38), sleeve=dict(upto=1.0, ease=1.2), buttons=[96, 104]),
    bottom=dict(kind='trousers', c='#5b5a62', ease=1.8, waist=104),
    shoes=dict(c='#3b3236', len=23, r=3.0, out=8),
)
