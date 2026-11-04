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
    lower_lip=0.04, ear_z=0.04, ear=(-0.04, -0.38), blush=0.15,
)

# shoulder-length hair in clumps with pointed ends, a soft parted fringe
_back = []
for i, t in enumerate(range(100, 261, 20)):
    tt = t if t <= 180 else t - 360
    side = 1 if tt > 0 else -1
    out = 0.18 * side if abs(tt) < 170 else 0.0
    ln = 1.05 + 0.12 * ((i * 37) % 5) / 4
    _back.append(dict(root=(tt, 0.2), to=[(out * 0.6, -0.5, -0.05), (out, -ln, 0.0)], w=0.42, prof=2.5,
                      back=abs(tt) > 125, line=('l' if i % 2 else 'r') if abs(tt) <= 125 else None))

HAIRDEF = dict(
    hairline=[(0, 0.55), (30, 0.50), (60, 0.32), (85, 0.10), (100, -0.05), (130, -0.4), (180, -0.6)],
    volume=[(-1, 0.10), (0, 0.11), (1, 0.15)],
    flow=[[(150, 0.95), (120, 0.6), (110, 0.25)], [(-150, 0.95), (-120, 0.6), (-110, 0.25)],
          [(100, 0.9), (90, 0.55)], [(-100, 0.9), (-90, 0.55)]],
    locks=[
        # fringe: a few broad soft clumps with pointed ends, parted a little to the character's right
        dict(root=(-45, 0.80), to=[(-0.06, -0.25, 0.16), (-0.20, -0.62, 0.18)], w=0.34, line='r'),
        dict(root=(-18, 0.90), to=[(0.0, -0.30, 0.22), (-0.10, -0.80, 0.26)], w=0.34, line='r'),
        dict(root=(10, 0.90), to=[(0.06, -0.30, 0.24), (0.10, -0.72, 0.26)], w=0.30, line='l'),
        dict(root=(38, 0.80), to=[(0.10, -0.26, 0.20), (0.22, -0.66, 0.18)], w=0.32, line='l'),
        # locks over the ears framing the cheeks
        dict(root=(100, 0.45), to=[(0.10, -0.45, 0.0), (0.10, -1.05, -0.02), (0.06, -1.45, -0.05)], w=0.34, line='l', prof=2),
        dict(root=(-100, 0.45), to=[(-0.10, -0.45, 0.0), (-0.10, -1.0, -0.02), (-0.08, -1.40, -0.05)], w=0.34, line='r', prof=2),
    ] + _back,
)


def head():
    return Head(FACE)


def hair(h):
    return Hair(h, HAIRDEF)


# ---------------------------------------------------------------- body
B = dict(
    hip_y=84, hip_x=8.5, thigh=40, shin=37.5, shoulder=(14.2, 131, -1.0), upper=27, fore=23, hand=15,
    arm_r=[3.9, 3.3, 2.9, 2.3], hand_r=2.1, leg_r=[7.4, 6.2, 4.6, 4.0, 4.6, 4.2, 3.0, 2.8], neck=(136.0, 143, -1.0, 0.5),
    neck_r=3.5, head_c=(0, 149.2, 1.8), head_h=24.0, chest_y=118,
    torso=[(76, 10.5, 7, -7), (84, 16.5, 8.5, -9.5), (93, 15.5, 8, -9), (103, 12.8, 7.2, -7.2), (112, 14.2, 9, -7.8),
           (120, 15.2, 10.5, -8.3), (126, 16.6, 9.4, -8.3), (130, 17.8, 7.6, -7.4), (133, 15.6, 6.0, -6.5), (135.5, 10.5, 4.6, -5.6), (137.5, 5.5, 3.6, -4.8)],
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
    top=dict(c='#f3ead6', ease=0.6, hem=86, sleeve=dict(upto=1.0, ease=0.8), collar=3.0),
    over=dict(c='#8d9a62', ease=1.5, hem=88, open=(0.10, 0.42), sleeve=dict(upto=1.0, ease=1.3)),
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
