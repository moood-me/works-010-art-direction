"""Аня, about 20 — warm, trusting, dreamy. Long chestnut hair with a soft clumpy fringe, a round soft face, big calm
eyes; a cream blouse, a moss-green cardigan, a long rust skirt."""
from head import Head, Expr, profile
from hair import Hair

SKIN = '#f6d6bb'
HAIR = '#7a4a30'
IRIS = '#33221d'

FACE = dict(
    a=[(1.0, 0.0), (0.96, 0.28), (0.8, 0.54), (0.5, 0.67), (0.2, 0.69), (0.0, 0.675), (-0.2, 0.655), (-0.4, 0.615),
       (-0.6, 0.545), (-0.75, 0.455), (-0.88, 0.32), (-0.96, 0.17), (-1.0, 0.0)],
    zf=[(1.0, 0.05), (0.8, 0.44), (0.5, 0.60), (0.2, 0.63), (0.0, 0.62), (-0.2, 0.62), (-0.5, 0.58), (-0.7, 0.53),
        (-0.9, 0.44), (-1.0, 0.34)],
    zb=[(1.0, -0.05), (0.8, -0.72), (0.5, -0.88), (0.2, -0.88), (0.0, -0.80), (-0.2, -0.66), (-0.4, -0.36),
        (-0.6, -0.06), (-0.8, 0.06), (-1.0, 0.18)],
    prof=profile(-0.50, 0.13, mouth_y=-0.72),
    sigma=[(0.2, 0.10), (-0.3, 0.07), (-0.5, 0.16), (-0.8, 0.22)],
    eye_x=0.27, eye_y=-0.09, eye_w=0.27, eye_h=0.185, iris_w=0.082, iris_h=0.10, lashes=0, flick=1.0, lid_w=1.5,
    brow_y=0.25, brow_w=0.25, brow_th=2.0, brow_arch=0.05, nose_y=-0.50, nose='hook', nose_len=0.13, mouth_y=-0.72, mouth_w=0.10, mouth_curve=0.0,
    lower_lip=0.04, cheek=(-0.32, 0.07, 0.22), ear_z=0.04, ear=(-0.04, -0.38), blush=0.15,
)

# a soft fringe, locks framing the face to the chin, the rest gathered low into a loose tail over the left
# shoulder, tied with a ribbon
HAIRDEF = dict(
    hairline=[(0, 0.66), (30, 0.60), (60, 0.38), (85, 0.10), (100, -0.05), (130, -0.4), (180, -0.6)],
    volume=[(-1, 0.06), (-0.3, 0.07), (0.3, 0.08), (1, 0.10)],
    flow=[[(150, 0.95), (125, 0.6), (115, 0.25)], [(-150, 0.95), (-125, 0.6), (-115, 0.25)],
          [(170, 0.9), (165, 0.3), (160, -0.3)], [(-170, 0.9), (-165, 0.3), (-160, -0.3)]],
    locks=[
        # fringe: a few soft clumps, curved, pointed, parted a little to the character's right
        dict(root=(-46, 0.84), to=[(-0.10, -0.30, 0.18), (-0.22, -0.80, 0.14)], w=0.30, line='r'),
        dict(root=(-22, 0.92), to=[(0.04, -0.36, 0.24), (-0.10, -0.90, 0.24)], w=0.32, line='r'),
        dict(root=(4, 0.94), to=[(0.10, -0.34, 0.26), (0.12, -0.82, 0.26)], w=0.28, line='l'),
        dict(root=(30, 0.88), to=[(0.14, -0.30, 0.24), (0.26, -0.78, 0.20)], w=0.30, line='l'),
        dict(root=(52, 0.76), to=[(0.10, -0.30, 0.16), (0.24, -0.82, 0.08)], w=0.26),
        # locks over the ears framing the cheeks, to the jaw
        dict(root=(82, 0.50), to=[(0.10, -0.45, 0.06), (0.08, -0.95, 0.06), (0.03, -1.30, 0.04)], w=0.30, line='l', prof=1.8),
        dict(root=(-82, 0.50), to=[(-0.10, -0.45, 0.06), (-0.08, -0.95, 0.06), (-0.04, -1.28, 0.04)], w=0.30, line='r', prof=1.8),
        # the gathered hair at the nape
        dict(root=(160, -0.2), to=[(0.10, -0.35, -0.10), (0.25, -0.55, -0.05)], w=0.55, prof=1.0, back=True),
        dict(root=(-160, -0.2), to=[(-0.05, -0.35, -0.10), (0.10, -0.55, -0.05)], w=0.55, prof=1.0, back=True),
        # the tail over the left shoulder, in front
        dict(root=(-140, -0.45), to=[(-0.25, -0.35, 0.10), (-0.42, -0.90, 0.45), (-0.40, -1.70, 0.70), (-0.28, -2.40, 0.70)],
             w=0.36, prof=0.9, line='r', front=True),
    ],
)


def head():
    return Head(FACE)


def hair(h):
    return Hair(h, HAIRDEF)


# ---------------------------------------------------------------- body
B = dict(
    hip_y=84, hip_x=8.5, thigh=40, shin=37.5, shoulder=(13.4, 131, -1.0), upper=27, fore=23, hand=15,
    arm_r=[3.5, 3.0, 2.6, 2.1], hand_r=2.0, leg_r=[7.4, 6.2, 4.6, 4.0, 4.6, 4.2, 3.0, 2.8], neck=(136.0, 143, -1.0, 0.5),
    neck_r=3.2, head_c=(0, 150.2, 1.8), head_h=24.0, chest_y=118,
    torso=[(76, 10.5, 7, -7), (84, 16.5, 8.5, -9.5), (93, 15.5, 8, -9), (103, 12.8, 7.2, -7.2), (112, 14.2, 9, -7.8),
           (120, 15.2, 10.5, -8.3), (126, 15.8, 9.4, -8.3), (130, 16.6, 7.6, -7.4), (133, 14.6, 6.0, -6.5), (135.5, 10.5, 4.6, -5.6), (137.5, 5.5, 3.6, -4.8)],
)

POSES = dict(
    hat=dict(
        # holding a straw hat in front with both hands, head tilted, looking a little up and away: dreaming
        head_rot=(10, -4, -6), hip_shift=-1.5,
        arml=dict(upper=(0.12, -1, 0.30), fore=(-0.62, -0.30, 0.72), hand=(-0.7, -0.4, 0.5), palm=(-1, 0, 0)),
        armr=dict(upper=(0.12, -1, 0.30), fore=(-0.62, -0.32, 0.70), hand=(-0.7, -0.4, 0.5), palm=(-1, 0, 0)),
        legl=dict(thigh=(0.03, -1, 0.0), shin=(0.0, -1, -0.02)),
        legr=dict(thigh=(0.08, -1, 0.08), shin=(-0.02, -1, -0.08)),
    ),
    stand=dict(
        arml=dict(upper=(0.07, -1, 0.02), fore=(0.06, -1, 0.14), hand=(0.0, -1, 0.1), palm=(-1, 0, 0.2)),
        armr=dict(upper=(0.07, -1, 0.02), fore=(0.06, -1, 0.14), hand=(0.0, -1, 0.1), palm=(-1, 0, 0.2)),
        legl=dict(thigh=(0.05, -1, 0.0), shin=(0.0, -1, -0.02)),
        legr=dict(thigh=(0.05, -1, 0.0), shin=(0.0, -1, -0.02)),
    ),
)

SPEC = dict(
    skin=SKIN,
    top=dict(c='#f3ead6', ease=0.5, hem=86, sleeve=dict(upto=1.0, ease=0.6), neck_cut=(5.5, 0.55)),
    over=dict(c='#8d9a62', ease=1.0, hem=88, open=(0.12, 0.46), sleeve=dict(upto=1.0, ease=0.9)),
    bottom=dict(kind='skirt', c='#b8664a', waist=103,
                rings=[(40, 25, 19, -19), (60, 21.5, 15.5, -16), (88, 17.5, 10.5, -11), (103, 13.8, 8, -8)],
                wave=(1.6, 7, 80),
                folds=[-0.9, -0.3, 0.35, 0.95]),
    shoes=dict(c='#6b4632', len=21, r=3.0, out=8),
)


def hat(d, view, F):
    """a straw hat held in front with both hands, its crown toward us, a red ribbon."""
    import numpy as np
    from geo import tube, poly, shift
    from dress import fill_part
    from svgdoc import mix
    J = F.J
    c = (J['hdl'] + J['hdr']) / 2 + np.array([0, -5.0, 2.0])
    n = np.array([0.0, 0.25, 1.0]); n /= np.linalg.norm(n)
    u = np.array([1.0, 0, 0]); w = np.cross(n, u)
    t = np.linspace(0, 2 * np.pi, 60, endpoint=False)
    brim = poly(view.xy(np.array([c + 19 * (np.cos(a) * u + np.sin(a) * w) for a in t])))
    straw = '#e9d08e'
    k = view.s
    fill_part(d, brim, straw, 0.5 * k)
    crown = tube(view, [c, c + n * 6.5], [9.5, 8.6])
    fill_part(d, crown, mix(straw, '#ffffff', 0.15), 0.8 * k)
    band = tube(view, [c + n * 0.3, c + n * 2.6], [9.7, 9.5])
    fill_part(d, band, '#c25a40', 0.5 * k)
    top = poly(view.xy(np.array([c + n * 6.5 + 8.6 * (np.cos(a) * u + np.sin(a) * w) for a in t])))
    fill_part(d, top, mix(straw, '#ffffff', 0.25), 0.6 * k)
    # weave: a few rings on the brim
    for r in (13, 16):
        ring = view.xy(np.array([c + r * (np.cos(a) * u + np.sin(a) * w) for a in t] + [c + r * u]))
        d.line(ring, d.lw * 0.35, '#b89a5a')


SPEC['prop'] = hat
