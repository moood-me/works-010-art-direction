"""Марат, about 35, a cook — huge, loud, merry, generous. A broad head on a short neck, short dark curls, a thick
black beard with the mouth laughing in it, thick brows, a broad nose, dark eyes that narrow when he laughs. A white
cook's jacket with rolled sleeves, a long terracotta apron, a towel over the shoulder, a ladle."""
import random
import numpy as np
from head import Head, Expr, profile
from hair import Hair

SKIN = '#eebd98'
HAIR = '#2b2423'
IRIS = '#2e211e'
WHITE = '#f4efe2'
TERRA = '#c8683f'

FACE = dict(
    a=[(1.0, 0.0), (0.96, 0.30), (0.8, 0.57), (0.5, 0.71), (0.2, 0.74), (0.0, 0.74), (-0.2, 0.735), (-0.4, 0.72),
       (-0.6, 0.68), (-0.75, 0.60), (-0.88, 0.45), (-0.96, 0.26), (-1.0, 0.0)],
    zf=[(1.0, 0.05), (0.8, 0.44), (0.5, 0.60), (0.2, 0.63), (0.0, 0.62), (-0.2, 0.62), (-0.5, 0.58), (-0.7, 0.53),
        (-0.9, 0.44), (-1.0, 0.34)],
    zb=[(1.0, -0.05), (0.8, -0.72), (0.5, -0.88), (0.2, -0.88), (0.0, -0.80), (-0.2, -0.66), (-0.4, -0.36),
        (-0.6, -0.06), (-0.8, 0.06), (-1.0, 0.18)],
    prof=profile(-0.47, 0.19, bridge=0.07, mouth_y=-0.72, brow=0.04, chin=0.03),
    sigma=[(0.2, 0.16), (-0.3, 0.13), (-0.5, 0.21), (-0.8, 0.26)],
    eye_x=0.29, eye_y=-0.08, eye_w=0.26, eye_h=0.175, iris_w=0.080, iris_h=0.095, lashes=0, flick=0.3, lid_w=1.3,
    crease=0.0,
    brow_y=0.205, brow_w=0.33, brow_th=5.0, brow_arch=0.045, nose_y=-0.47, nose='round', nose_w=0.105, nose_len=0.14,
    mouth_y=-0.715, mouth_w=0.185, ear=(-0.02, -0.40), ear_z=0.04, blush=0.25,
    marks=[
        dict(pts=[(0.41, -0.05), (0.47, -0.02)], w=0.5),                 # laughter lines at the eyes
        dict(pts=[(0.15, -0.40), (0.21, -0.47), (0.23, -0.53)], w=0.55),  # the cheeks lifted by the laugh
    ],
)

# short curls: a low mass with round clumps all over its edge
_r = random.Random(5)
_curls = []
for t in range(-172, 180, 17):
    for y in (0.93, 0.62, 0.30):
        if abs(t) < 62 and y < 0.9:
            continue
        _curls.append((t + _r.uniform(-5, 5), y + _r.uniform(-0.05, 0.05), _r.uniform(0.09, 0.115), 0.02))
for t in (-58, -44, -30, -16, -2, 12, 26, 40, 54):      # the curls over the forehead
    _curls.append((t + _r.uniform(-3, 3), 0.63 + _r.uniform(-0.03, 0.03), _r.uniform(0.085, 0.105), 0.0))
for t in (-150, -125, -100, 100, 125, 150, 178):
    _curls.append((t, 0.0 + _r.uniform(-0.05, 0.05), 0.095, 0.01))

HAIRDEF = dict(
    hairline=[(0, 0.60), (30, 0.59), (55, 0.46), (66, 0.10), (72, -0.12), (80, 0.02), (88, 0.08), (100, -0.05),
              (125, -0.28), (180, -0.36)],
    volume=[(-1, 0.05), (0, 0.075), (1, 0.09)],
    balls=_curls,
    flow=[[(t, y), (t + 9, y + 0.07), (t + 17, y + 0.01), (t + 12, y - 0.06)]
          for t, y in ((-50, 0.80), (-20, 0.86), (12, 0.84), (40, 0.78), (-75, 0.55), (70, 0.52), (-100, 0.40),
                       (100, 0.36), (-130, 0.6), (130, 0.6), (160, 0.3), (-160, 0.3))],
)

# the beard is built as hair is: a shell over the jaw between the cheek line and the chin, with clumps below.
# Its upper edge: under the nose (the moustache), across the cheek, up to the sideburn in front of the ear.
_bcurls = [(t, y, r, 0.03) for t, y, r in (
    (-78, -0.60, 0.10), (-66, -0.78, 0.115), (-50, -0.92, 0.12), (-30, -0.985, 0.125), (-8, -0.999, 0.13),
    (14, -0.999, 0.13), (34, -0.98, 0.125), (52, -0.91, 0.12), (67, -0.77, 0.115), (79, -0.59, 0.10))]
BEARD = dict(
    hairline=[(0, -0.999), (180, -0.999)],
    top=[(0, -0.575), (10, -0.555), (22, -0.545), (36, -0.56), (50, -0.52), (60, -0.40), (68, -0.14), (76, -0.14),
         (82, -0.46), (96, -0.52), (104, -0.999), (180, -0.999)],
    volume=[(-1, 0.24), (-0.75, 0.14), (-0.5, 0.05), (-0.2, 0.02), (0, 0.02)],
    balls=_bcurls,
    flow=[[(-40, -0.66), (-34, -0.80), (-22, -0.90)], [(40, -0.66), (34, -0.80), (22, -0.90)],
          [(-62, -0.50), (-60, -0.64), (-52, -0.76)], [(62, -0.50), (60, -0.64), (52, -0.76)],
          [(-6, -0.90), (0, -0.96), (6, -0.90)]],
)

# what the face does when he is himself: a wide open laugh, the eyes narrowed by the cheeks
CALM = Expr(open=0.80, smile_eye=0.9, lid_out=0.1, mouth='D', mouth_open=1.0, teeth=True, smile=0.9, mouth_w=1.2,
            brow_up=0.35, brow_arch=0.5, blush=0.35, look=(0.2, 0.0))
EXPR = dict(
    joy=Expr(closed=1, mouth='D', mouth_open=1.0, smile=1.0, teeth=True, blush=0.6, brow_up=0.5, brow_arch=0.6,
             mouth_w=1.35),
)


def head():
    return Head(FACE)


def hair(h):
    return Hair(h, HAIRDEF)


def extra(d, view, F, h, skin_g):
    """the beard over the jaw, and the mouth drawn again on top of it."""
    bd = Hair(h, BEARD)
    g, _, strands = bd.build(view)
    bd.draw(d, view, g, HAIR, strands)
    E = getattr(F, 'expr', None) or CALM
    h.mouth(d, view, E, SKIN, g.union(skin_g))
    if E.mouth_open <= 0.01:
        # a shut mouth in a black beard: a lighter line, or it is lost
        P = h.P
        mw = P['mouth_w'] * E.mouth_w
        u = np.linspace(-mw, mw, 16)
        v = E.smile * 0.06 * ((u / mw) ** 2 - 0.3)
        d.line(h.xy(view, h.on(u, P['mouth_y'] + v, 0.03)), d.lw * 1.0, '#8a5a50')


# ---------------------------------------------------------------- body
B = dict(
    hip_y=95, hip_x=11.5, thigh=45, shin=42.5, shoulder=(21.5, 147.5, -1.0), upper=31, fore=27, hand=20,
    arm_r=[7.2, 6.6, 5.9, 4.3], hand_r=3.1, leg_r=[10.8, 9.2, 7.0, 6.0, 6.5, 5.8, 4.4, 4.0],
    neck=(154.0, 163, -0.5, 1.0), neck_r=6.8, head_c=(0, 172.0, 2.4), head_h=25.5, chest_y=136, torso_n=2.5,
    torso=[(86, 15, 10, -10), (95, 23.5, 14.5, -13), (106, 25.5, 18.5, -13), (116, 26, 19.5, -13), (126, 25.5, 18, -13),
           (135, 25.5, 16, -13), (142, 26, 14, -12.5), (147, 24.5, 11.5, -11), (151, 20, 9, -9.5),
           (154.5, 14.5, 7, -8), (157.5, 9.5, 5.5, -6.8)],
)

_LEGS = dict(legl=dict(thigh=(0.07, -1, 0.0), shin=(0.0, -1, -0.02)),
             legr=dict(thigh=(0.07, -1, 0.0), shin=(0.0, -1, -0.02)))
_HIP = dict(upper=(0.66, -0.72, -0.22), fore=(-0.50, -0.84, 0.16), hand=(-0.35, -0.85, 0.40), palm=(-1, 0.2, 0))

POSES = dict(
    stand=dict(
        arml=dict(upper=(0.16, -1, 0.02), fore=(0.06, -1, 0.16), hand=(0.0, -1, 0.1), palm=(-1, 0, 0.2)),
        armr=dict(upper=(0.16, -1, 0.02), fore=(0.06, -1, 0.16), hand=(0.0, -1, 0.1), palm=(-1, 0, 0.2)),
        **_LEGS,
    ),
    ladle=dict(
        # the ladle raised like a toast, the other fist on the hip, feet apart, the head thrown back in a laugh
        lean=-2.5, hip_shift=-2.0, head_rot=(6, 8, 6),
        arml=dict(upper=(0.62, -0.72, 0.30), fore=(0.45, 0.80, 0.42), hand=(0.3, 0.9, 0.3), palm=(-1, 0, 0.25),
                  hand_kind='hold'),
        armr=_HIP,
        legl=dict(thigh=(0.17, -1, 0.03), shin=(0.03, -1, -0.03)),
        legr=dict(thigh=(0.13, -1, 0.0), shin=(0.02, -1, -0.02)),
    ),
    hips=dict(
        # both fists on the hips: the master of his kitchen
        lean=-1.5, head_rot=(4, 5, 3),
        arml=_HIP, armr=_HIP,
        legl=dict(thigh=(0.14, -1, 0.02), shin=(0.03, -1, -0.03)),
        legr=dict(thigh=(0.14, -1, 0.02), shin=(0.03, -1, -0.03)),
    ),
)


def _apron_loft(F):
    """the torso's form (a little bigger) continued down to the knees."""
    lo = F.torso_loft(push=1.2)
    from body import Loft
    rings = [(y,) + tuple(lo.at(y)) for y in (96, 104, 112, 120, 128, 136, 144, 149)]
    a, zf, zb, x0, z0 = lo.at(96)
    rings += [(76, a + 0.8, zf + 0.5, zb, x0, z0), (56, a + 1.6, zf + 0.3, zb, x0, z0)]
    return Loft(rings, 2.5)


def apron(d, view, F):
    """a long bib apron: the bib on the chest, the skirt from the waist to below the knees, a strap round the neck,
    a pocket."""
    from dress import surface_patch, surface_line, fill_part
    lo = _apron_loft(F)
    k = view.s
    rows = []
    for y in np.linspace(56, 147, 40):
        w = 1.28 if y < 114 else (1.28 - (1.28 - 0.62) * min((y - 114) / 9.0, 1) ** 0.6 - 0.14 * max(y - 123, 0) / 24)
        rows.append((y, -w, w))
    g = surface_patch(view, lo, rows, push=0.3)
    # the strap: from the bib's corners up to the sides of the neck
    top = F.torso_loft(push=1.9)
    y1 = F.B['torso'][-1][0]
    for s_ in (-1, 1):
        ys = np.linspace(146.5, y1 + 0.5, 8)
        ts = np.linspace(s_ * 0.44, s_ * 0.50, 8)
        surface_line(d, view, top, ts, ys, 3.4 * k * 0.42, push=0.2, c='#2e2320')
        surface_line(d, view, top, ts, ys, 3.4 * k * 0.42 - d.lw * 1.6, push=0.2, c=TERRA)
    fill_part(d, g, TERRA, 1.0 * k)
    inner = g.buffer(-d.lw)
    # the waist tie and the folds it gathers; a pocket
    ts = np.linspace(-1.28, 1.28, 30)
    surface_line(d, view, lo, ts, [113.5 - 1.2 * np.cos(t) for t in ts], d.lw * 0.7, push=0.35, clip=inner)
    for t, y0, y1_ in ((-0.75, 110, 96), (0.1, 110, 99), (0.85, 110, 94), (-0.2, 72, 58), (0.6, 76, 58), (-1.0, 70, 58)):
        ys = np.linspace(y0, y1_, 6)
        surface_line(d, view, lo, [t + 0.02 * (y0 - y) / 10 for y in ys], ys, d.lw * 0.5, push=0.35, clip=inner)
    pk_t = [0.18, 0.18, 0.74, 0.74, 0.18]
    pk_y = [99, 86, 86, 99, 99]
    tt = np.concatenate([np.linspace(a, b, 6) for a, b in zip(pk_t[:-1], pk_t[1:])])
    yy = np.concatenate([np.linspace(a, b, 6) for a, b in zip(pk_y[:-1], pk_y[1:])])
    surface_line(d, view, lo, tt, yy, d.lw * 0.6, push=0.35, clip=inner)


def worn(d, view, F):
    """a towel thrown over his right shoulder."""
    from dress import surface_patch, fill_part
    lo = F.torso_loft(push=2.4)
    rows = [(y, -1.36, -0.74) for y in np.linspace(122, 152.5, 16)]
    g = surface_patch(view, lo, rows, push=0.2, nt=8)
    from geo import shift
    from svgdoc import shade
    d.fill(shift(g, 0.5 * view.s, 0.9 * view.s), shade(WHITE))
    fill_part(d, g, '#fbf8f0', 0.6 * view.s)
    for ya, yb in ((127, 128.6), (130.2, 131.0), (143, 144.6), (146.2, 147.0)):
        band = surface_patch(view, lo, [(ya - 2, -1.36, -0.74), (yb - 2, -1.36, -0.74)], push=0.25, nt=8)
        d.fill(band.intersection(g.buffer(-d.lw * 0.6)), TERRA)


def ladle(d, view, F):
    """a ladle held up in his left fist: a steel handle with a hook, a deep bowl."""
    from geo import tube, poly
    from dress import fill_part
    J = F.J
    if F.pose['arml'].get('hand_kind') != 'hold':
        return
    grip = J['wrl'] + (J['hdl'] - J['wrl']) * 0.5
    up = np.array([-0.22, 1.0, 0.05]); up /= np.linalg.norm(up)
    a, b = grip - up * 9, grip + up * 24
    steel = '#c9ccc9'
    k = view.s
    fill_part(d, tube(view, [a, b], [0.75, 0.75]), steel, 0.25 * k)
    c = b + up * 5.5
    bowl = tube(view, [c, c + [0.0, -2.5, 0.0]], [6.4, 5.4])
    fill_part(d, bowl, steel, 1.1 * k)
    # the opening of the bowl, turned a little toward us
    t = np.linspace(0, 2 * np.pi, 40, endpoint=False)
    rim = poly(view.xy(np.array([c + [0, 2.0, 0] + 5.6 * np.array([np.cos(x), 0.0, np.sin(x)]) for x in t]))).buffer(0.26 * 2.4 * k)
    d.fill(rim.intersection(bowl.buffer(1)), '#8f9494')
    d.outline(rim.intersection(bowl.buffer(1)), d.lw * 0.7)


SPEC = dict(
    skin=SKIN,
    top=dict(c=WHITE, ease=1.0, hem=92, sleeve=dict(upto=0.60, ease=0.7, roll=0.45)),
    bottom=dict(kind='trousers', c='#5b5560', ease=1.8, waist=108),
    shoes=dict(c='#3a2e2a', len=28, r=4.4, out=14),
    figure_scale=4.7,
    apron=apron, worn=worn, prop=ladle,
)
