"""Кира, about 15 — prickly, closed, defiant; vulnerable underneath, and she hides it. A longer face than a child's
with a small sharp chin, eyes smaller than Аня's under low straight brows, a mouth pressed shut; short choppy dark
hair, a long fringe falling over her left eye. An oversized plum hoodie, acid-yellow headphones round the neck,
narrow charcoal trousers, heavy boots. She slouches."""
import numpy as np
from head import Head, Expr, profile
from hair import Hair

SKIN = '#f3d3bc'
HAIR = '#33283a'
IRIS = '#3a3046'
PLUM = '#5b3759'
ACID = '#d2e03a'
COAL = '#3d3b45'

FACE = dict(
    a=[(1.0, 0.0), (0.96, 0.275), (0.8, 0.53), (0.5, 0.66), (0.2, 0.68), (0.0, 0.67), (-0.2, 0.65), (-0.4, 0.61),
       (-0.6, 0.545), (-0.75, 0.45), (-0.88, 0.30), (-0.96, 0.15), (-1.0, 0.0)],
    zf=[(1.0, 0.05), (0.8, 0.44), (0.5, 0.60), (0.2, 0.63), (0.0, 0.62), (-0.2, 0.62), (-0.5, 0.58), (-0.7, 0.53),
        (-0.9, 0.44), (-1.0, 0.34)],
    zb=[(1.0, -0.05), (0.8, -0.72), (0.5, -0.88), (0.2, -0.88), (0.0, -0.80), (-0.2, -0.66), (-0.4, -0.36),
        (-0.6, -0.06), (-0.8, 0.06), (-1.0, 0.18)],
    prof=profile(-0.50, 0.14, bridge=0.05, mouth_y=-0.73),
    sigma=[(0.2, 0.10), (-0.3, 0.07), (-0.5, 0.16), (-0.8, 0.21)],
    eye_x=0.28, eye_y=-0.10, eye_w=0.255, eye_h=0.165, iris_w=0.074, iris_h=0.09, lashes=1, flick=1.0, lid_w=1.7,
    eye_tilt=0.02, iris_light='#8a7a9a',
    brow_y=0.205, brow_w=0.27, brow_th=2.3, brow_arch=0.012, nose_y=-0.50, nose='hook', nose_len=0.12, nose_w=0.065,
    mouth_y=-0.73, mouth_w=0.085, lower_lip=0.035, cheek=(-0.34, 0.05, 0.2), ear_z=0.04, ear=(-0.05, -0.38),
)

# short and choppy: jagged ends at the nape and over the ears; parted on her right, the long fringe thrown across
# the forehead and down over the left eye
_back = []
for i, t in enumerate([-178, -158, -138, -118, 118, 138, 158]):
    sgn = np.sign(t)
    _back.append(dict(root=(t, 0.0), to=[(sgn * 0.03, -0.16, -0.04), (sgn * (0.06 + 0.05 * (i % 2)), -0.34 - 0.07 * (i % 3), -0.02)],
                      w=0.30, prof=1.3, back=True))

HAIRDEF = dict(
    tufts=[dict(ts=[-160, -135, -110, -88, 100, 125, 150, 175], y=0.86, drop=0.62, w=0.32, out=0.07, swirl=10),
           dict(ts=[-170, -146, -122, -98, 96, 120, 144, 168], y=0.42, drop=0.52, w=0.30, out=0.08, swirl=-8)],
    hairline=[(0, 0.64), (30, 0.61), (60, 0.42), (85, 0.12), (100, -0.02), (130, -0.24), (180, -0.34)],
    volume=[(-1, 0.09), (0, 0.13), (1, 0.18)],
    locks=[
        # the fringe: three long pointed clumps from the parting across to the left eye and the cheek
        dict(root=(-34, 0.90), to=[(0.20, -0.30, 0.24), (0.44, -0.82, 0.24), (0.50, -1.30, 0.12)], w=0.40, line='l', prof=1.7),
        dict(root=(-10, 0.94), to=[(0.18, -0.42, 0.26), (0.36, -0.98, 0.22), (0.46, -1.52, 0.08)], w=0.36, line='l', prof=1.7),
        dict(root=(22, 0.90), to=[(0.12, -0.40, 0.22), (0.30, -0.95, 0.12), (0.36, -1.42, 0.0)], w=0.34, prof=1.6),
        dict(root=(52, 0.76), to=[(0.10, -0.36, 0.14), (0.20, -0.86, 0.04), (0.18, -1.22, -0.02)], w=0.30, line='l', prof=1.5),
        # the short side: jagged bits by the right temple and in front of the ear
        dict(root=(-52, 0.82), to=[(-0.08, -0.22, 0.16), (-0.20, -0.50, 0.14)], w=0.26, line='r'),
        dict(root=(-70, 0.66), to=[(-0.08, -0.30, 0.10), (-0.14, -0.72, 0.06)], w=0.26),
        dict(root=(-86, 0.42), to=[(-0.05, -0.36, 0.04), (-0.02, -0.80, 0.03)], w=0.24, line='r'),
        dict(root=(88, 0.40), to=[(0.07, -0.40, 0.03), (0.06, -0.92, 0.02)], w=0.26),
        # a tuft that will not lie down, on the crown
        dict(root=(150, 0.93), to=[(0.06, 0.12, -0.06), (0.16, 0.18, -0.12)], w=0.16, prof=1.2),
    ] + _back,
)

# herself: the head a little down, the look from under the brows and aside, the mouth shut
CALM = Expr(open=0.80, lid_in=0.30, brow_in=0.55, brow_up=-0.35, smile=-0.30, mouth_w=0.95, look=(-0.55, 0.30))
EXPR = dict(
    # she never smiles openly: a crooked half-smile she turns away with, and gives herself away by blushing
    joy=Expr(open=0.88, smile_eye=0.7, smile=0.35, smirk=1.0, brow_up=0.25, brow_in=-0.2, blush=0.6, look=(0.6, -0.35)),
    surprise=Expr(open=1.22, iris=0.80, brow_up=0.9, brow_arch=0.5, mouth='O', mouth_open=0.45, mouth_w=0.55),
    sad=Expr(open=0.70, lid_out=0.40, brow_in=-0.9, brow_up=0.1, smile=-0.6, look=(0.3, -0.8), mouth_w=0.85),
    anger=Expr(open=0.92, lid_in=0.45, brow_in=1.3, brow_up=-0.6, mouth='shout', mouth_open=0.4, teeth=True, tongue=False,
               mouth_w=1.25, look=(-0.35, 0.2)),
)


def head():
    return Head(FACE)


def hair(h):
    return Hair(h, HAIRDEF)


# ---------------------------------------------------------------- body
B = dict(
    hip_y=84, hip_x=7.4, thigh=40, shin=37.5, shoulder=(11.8, 127.5, -1.0), upper=27, fore=24.5, hand=15,
    arm_r=[2.9, 2.5, 2.2, 1.8], hand_r=1.85, leg_r=[6.3, 5.3, 4.0, 3.4, 3.8, 3.4, 2.5, 2.4],
    neck=(132.5, 142, -1.0, 0.5), neck_r=2.9, head_c=(0, 148.4, 1.8), head_h=23.6, chest_y=116,
    torso=[(76, 9.4, 6.4, -6.4), (84, 13.8, 7.6, -8.4), (93, 12.8, 7.0, -7.8), (103, 11.2, 6.4, -6.4), (112, 12.2, 7.4, -7.0),
           (120, 13.0, 8.0, -7.4), (125.5, 13.6, 7.6, -7.4), (129, 14.2, 6.6, -6.8), (131.5, 12.4, 5.2, -5.8),
           (133.5, 8.8, 4.0, -5.0), (135.5, 4.6, 3.2, -4.2)],
)

HOOD_EASE = 3.4
POCKET = ((92.5, 0.62), (80.5, 1.0))      # the kangaroo pocket: (y, half-width as azimuth) at its top and its bottom

POSES = dict(
    stand=dict(
        lean=4.5, head_fwd=1.2, shrug=0.8, head_rot=(0, -6, 0),
        arml=dict(upper=(0.08, -1, -0.04), fore=(0.04, -1, 0.16), hand=(0.0, -1, 0.1), palm=(-1, 0, 0.2)),
        armr=dict(upper=(0.08, -1, -0.04), fore=(0.04, -1, 0.16), hand=(0.0, -1, 0.1), palm=(-1, 0, 0.2)),
        legl=dict(thigh=(0.04, -1, 0.0), shin=(0.0, -1, -0.02)),
        legr=dict(thigh=(0.04, -1, 0.0), shin=(0.0, -1, -0.02)),
    ),
    pocket=dict(
        # the slouch: weight on one leg, the other knee loose, one hand deep in the pocket with the elbow out, the
        # head down and turned away, the eyes coming back from under the fringe
        lean=6.0, head_fwd=3.5, shrug=1.2, hip_shift=2.2, head_rot=(10, -8, 5),
        armr=dict(upper=(0.30, -0.94, -0.16), fore=(-0.52, -0.66, 0.55), hand=(-0.6, -0.5, 0.5), palm=(0, 0, -1),
                  hand_kind='pocket'),
        arml=dict(upper=(0.10, -1, -0.10), fore=(0.02, -1, 0.18), hand=(-0.08, -1, 0.12), palm=(-1, 0, 0.2)),
        legl=dict(thigh=(0.01, -1, 0.0), shin=(0.0, -1, -0.02)),
        legr=dict(thigh=(0.10, -1, 0.16), shin=(-0.03, -1, -0.16)),
    ),
)


def pocket_mark(d, view, F, g):
    """the kangaroo pocket: its top edge and the two slanted openings."""
    from dress import surface_line
    lo = F.torso_loft(push=HOOD_EASE)
    (y1, w1), (y0, w0) = POCKET
    inner = g.buffer(-d.lw)
    ts = np.linspace(-w1, w1, 14)
    surface_line(d, view, lo, ts, [y1] * len(ts), d.lw * 0.75, clip=inner)
    for s_ in (-1, 1):
        ys = np.linspace(y1, y0, 8)
        surface_line(d, view, lo, np.linspace(s_ * w1, s_ * w0, 8), ys, d.lw * 0.75, clip=inner)
    # the hem band
    ts = np.linspace(-2.2, 2.2, 40)
    surface_line(d, view, lo, ts, [77.5] * len(ts), d.lw * 0.55, clip=inner)


def worn(d, view, F):
    """the hood lying round the neck, the headphones on it; the pocket's edge over a hand that is inside."""
    from geo import tube, bezier
    from dress import fill_part, surface_patch, surface_line
    from svgdoc import shade
    J, B_ = F.J, F.B
    k = view.s
    lw = d.lw
    boots(d, view, F)
    # ---- the pocket closes over the wrist
    lo = F.torso_loft(push=HOOD_EASE)
    (y1, w1), (y0, w0) = POCKET
    for side, s_ in (('r', -1), ('l', 1)):
        if F.pose['arm' + side].get('hand_kind') != 'pocket':
            continue
        rows = [(y, s_ * (w1 + (w0 - w1) * (y1 - y) / (y1 - y0)), s_ * 0.12) for y in np.linspace(y1, y0, 8)]
        g = surface_patch(view, lo, rows, push=0.5, nt=8)
        d.fill(g, PLUM)
        d.fill(g.intersection(F.arm_shape(view, side, ease=4.0)[0]), shade(PLUM))
        ys = np.linspace(y1, y0, 8)
        surface_line(d, view, lo, np.linspace(s_ * w1, s_ * w0, 8), ys, lw * 0.9, push=0.55)
        ts = np.linspace(s_ * w1, s_ * 0.12, 8)
        surface_line(d, view, lo, ts, [y1] * 8, lw * 0.75, push=0.55)
    # ---- the hood: a soft roll round the neck, high at the back, open at the throat
    n0 = J['neck0']
    up = (J['neck1'] - n0) / np.linalg.norm(J['neck1'] - n0)

    def ring(a_deg, r, y, fwd=0.0):
        a = np.radians(a_deg)
        return n0 + np.array([r * np.sin(a), 0.0, r * np.cos(a) + fwd]) + up * y
    neck = tube(view, [n0, J['neck1']], [B_['neck_r'] * 1.05, B_['neck_r']])
    head_g = F.head_g
    backs = [ring(a, 8.2, 4.6 - 1.6 * abs(abs(a) - 180) / 80, -1.5) for a in np.linspace(100, 260, 15)]
    g = tube(view, backs, [3.9] * len(backs))
    behind = g.difference(neck)
    fill_part(d, behind, PLUM, 0.6 * k)
    # the headphones' band behind the neck
    band = [ring(a, 7.6, 6.0 - 2.4 * abs(abs(a) - 180) / 100, -1.0) for a in np.linspace(80, 280, 17)]
    bg = tube(view, band, [1.25] * len(band)).difference(neck)
    fill_part(d, bg, COAL, 0.3 * k)
    for s_ in (-1, 1):
        fr = [ring(s_ * a, 8.4 - 1.2 * (100 - a) / 85, 3.0 - 6.4 * ((100 - a) / 85) ** 1.2, -1.5 + 2.2 * (100 - a) / 85)
              for a in np.linspace(100, 15, 10)]
        fg = tube(view, fr, list(np.linspace(3.9, 2.3, len(fr))))
        fill_part(d, fg, PLUM, 0.6 * k)
        # a drawstring
        a0 = fr[-1] + np.array([0, -1.5, 1.2])
        d.line(view.xy(bezier(a0, a0 + [s_ * 0.6, -4.5, 0.6], a0 + [s_ * 0.2, -9.0, 0.2], n=10)), lw * 1.5, '#e9e1d4')
    # the cups resting on the collarbones, turned outward: far one first
    cups = []
    for s_ in (-1, 1):
        c = ring(s_ * 60, 7.6, 0.6, 0.5)
        n = np.array([s_ * 0.80, 0.25, 0.55]); n /= np.linalg.norm(n)
        cups.append((float(view.depth(c[None])[0]), c, n))
    for _, c, n in sorted(cups, key=lambda x: x[0]):
        pad = tube(view, [c - n * 1.5, c - n * 0.2], [3.5, 3.7])
        fill_part(d, pad, COAL, 0.4 * k)
        cup = tube(view, [c, c + n * 2.0], [3.4, 2.8])
        fill_part(d, cup, ACID, 0.5 * k)
        cap = tube(view, [c + n * 2.1, c + n * 2.2], [1.5, 1.5])
        if float(view.dir(n[None])[0, 2]) > 0.1:
            d.outline(cap, lw * 0.6)


def boots(d, view, F):
    """heavy boots over the trousers: a thick sole, a shaft up the shin, acid laces."""
    from geo import tube
    from dress import fill_part
    from shapely.geometry import box
    from shapely.ops import unary_union
    sh = SPEC['shoes']
    r = sh['r']
    order = sorted(('l', 'r'), key=lambda s_: float(view.depth(F.J['an' + s_][None])[0]))
    for side in order:
        an, kn = F.J['an' + side], F.J['kn' + side]
        up = (kn - an) / np.linalg.norm(kn - an)
        foot = F.shoe(view, side, sh)
        g = unary_union([foot, tube(view, [an + up * 13, an + up * 2], [r * 0.92, r * 0.98])])
        fill_part(d, g, sh['c'], 0.3 * view.s)
        b = foot.bounds
        sole = g.intersection(box(b[0], b[3] - (b[3] - b[1]) * 0.24, b[2], b[3]))
        d.fill(sole, sh['sole'])
        d.outline(sole, d.lw * 0.7)
        d.outline(g)
        s_ = 1 if side == 'l' else -1
        out = np.radians(sh.get('out', 10))
        fwd = np.array([s_ * np.sin(out), 0, np.cos(out)])
        across = np.array([np.cos(out), 0, -s_ * np.sin(out)])
        if float(view.dir(fwd[None])[0, 2]) > 0.25:
            for i, h_ in enumerate((2.5, 5.2, 7.9, 10.6)):
                c = an + up * h_ + fwd * r * 0.93
                sl = 0.5 if i % 2 else -0.5
                d.line(view.xy(np.array([c - across * 1.7 + [0, sl, 0], c + across * 1.7 - [0, sl, 0]])), d.lw * 1.15, ACID)


SPEC = dict(
    skin=SKIN,
    top=dict(c=PLUM, ease=HOOD_EASE, hem=75, sleeve=dict(upto=1.0, ease=2.3), marks=[pocket_mark]),
    bottom=dict(kind='trousers', c=COAL, ease=0.45, waist=96, narrow=True),
    shoes=dict(c='#2f2b33', len=26, r=4.4, out=12, sole='#6a6470'),
    worn=worn,
)
