"""Савелий Петрович, about 70, a watchmaker — grumpy outside, kind inside. Bald crown with a white fringe that sticks
out over the ears, bushy white brows, a drooping white moustache, a round fleshy nose, small eyes in deep wrinkles,
little round reading glasses low on the nose, a watchmaker's loupe on a band across the forehead."""
import numpy as np
from head import Head, Expr, profile
from hair import Hair
from svgdoc import INK, mix, shade

SKIN = '#efc4a2'
HAIR = '#ece7df'
IRIS = '#3a2a26'

FACE = dict(
    a=[(1.0, 0.0), (0.96, 0.30), (0.8, 0.57), (0.5, 0.71), (0.2, 0.73), (0.0, 0.72), (-0.2, 0.71), (-0.4, 0.69),
       (-0.6, 0.64), (-0.75, 0.56), (-0.88, 0.43), (-0.96, 0.25), (-1.0, 0.0)],
    zf=[(1.0, 0.05), (0.8, 0.44), (0.5, 0.60), (0.2, 0.63), (0.0, 0.62), (-0.2, 0.62), (-0.5, 0.58), (-0.7, 0.53),
        (-0.9, 0.44), (-1.0, 0.34)],
    zb=[(1.0, -0.05), (0.8, -0.72), (0.5, -0.88), (0.2, -0.88), (0.0, -0.80), (-0.2, -0.66), (-0.4, -0.36),
        (-0.6, -0.06), (-0.8, 0.06), (-1.0, 0.18)],
    prof=profile(-0.47, 0.19, bridge=0.07, mouth_y=-0.74, brow=0.04, chin=0.03),
    sigma=[(0.2, 0.16), (-0.3, 0.12), (-0.5, 0.20), (-0.8, 0.26)],
    eye_x=0.285, eye_y=-0.08, eye_w=0.21, eye_h=0.11, iris_w=0.042, iris_h=0.052, lashes=0, flick=0.0, lid_w=1.0,
    crease=0.55, glints=[(-0.3, 0.3, 0.35)], iris_light='#3a2a26',
    brow_style='bushy', brow_y=0.17, brow_w=0.34, nose_y=-0.47, nose='round', nose_w=0.10, nose_len=0.13,
    mouth_y=-0.74, mouth_w=0.11, ear=(-0.02, -0.42), ear_z=0.04,
    marks=[
        dict(pts=[(0.16, 0.42), (0.0, 0.445), (-0.18, 0.42)], both=False, w=0.55),
        dict(pts=[(0.24, 0.52), (0.05, 0.545), (-0.12, 0.53)], both=False, w=0.5),
        dict(pts=[(0.41, -0.04), (0.47, -0.08)], w=0.5),               # crow's feet
        dict(pts=[(0.40, -0.12), (0.46, -0.13)], w=0.5),
        dict(pts=[(0.19, -0.16), (0.27, -0.19), (0.35, -0.17)], w=0.5),  # bags under the eyes
        dict(pts=[(0.14, -0.43), (0.22, -0.58), (0.26, -0.74)], w=0.6),  # cheek folds
        dict(pts=[(0.42, -0.64), (0.43, -0.80)], w=0.5),
    ],
)

HAIRDEF = dict(
    hairline=[(0, 0.95), (60, 0.95), (78, 0.12), (90, 0.0), (105, -0.25), (140, -0.5), (180, -0.55)],
    top=[(0, 0.2), (60, 0.2), (80, 0.34), (110, 0.42), (150, 0.50), (180, 0.52)],
    volume=[(-1, 0.12), (0, 0.17), (1, 0.14)],
    shadow='#b9b2bf',
    locks=[
        # soft white fluff over the ears, a little out and up; it does not reach the bald crown
        dict(root=(84, 0.26), to=[(0.10, 0.03, -0.02), (0.17, 0.08, -0.08)], w=0.22, mirror=True, prof=1.0),
        dict(root=(96, 0.12), to=[(0.11, -0.03, -0.05), (0.18, -0.01, -0.13)], w=0.24, mirror=True, prof=1.0, line='l'),
        dict(root=(112, 0.30), to=[(0.10, 0.05, -0.08), (0.14, 0.12, -0.18)], w=0.20, mirror=True, prof=1.0),
        dict(root=(100, -0.06), to=[(0.08, -0.08, -0.05), (0.12, -0.14, -0.12)], w=0.18, mirror=True, prof=1.0),
    ],
)

MOUSTACHE = [(0.0, -0.495), (0.09, -0.490), (0.19, -0.540), (0.27, -0.640), (0.31, -0.750), (0.27, -0.720),
             (0.25, -0.780), (0.20, -0.710), (0.16, -0.760), (0.12, -0.690), (0.07, -0.730), (0.03, -0.680),
             (-0.03, -0.680), (-0.07, -0.730), (-0.12, -0.690), (-0.16, -0.760), (-0.20, -0.710), (-0.25, -0.780),
             (-0.27, -0.720), (-0.31, -0.750), (-0.27, -0.640), (-0.19, -0.540), (-0.09, -0.490)]


def head():
    return Head(FACE)


def hair(h):
    return Hair(h, HAIRDEF)


def extra(d, view, F, h, skin_g, glasses=False, loupe=True):
    """the moustache, the loupe on its band, the reading glasses."""
    from geo import poly, shift, lines, tube
    from shapely.geometry import LineString, Point
    k = view.s * h.k
    inside = skin_g.buffer(0.02 * k)
    P = np.array(MOUSTACHE)
    g = poly(h.xy(view, h.on(P[:, 0], P[:, 1], 0.035))).buffer(0).intersection(inside)
    d.fill(g, HAIR)
    d.fill(g.difference(shift(g, -0.03 * k, -0.05 * k)), '#bdb6c2')
    d.outline(g, d.lw * 0.8)
    if loupe:
        # the band round the head above the brows, the loupe tipped up on it over the character's right eye
        y0 = 0.40
        a0 = float(h.a(y0))
        xs = np.linspace(-a0 * 0.995, a0 * 0.995, 50)
        ys = y0 + 0.03 * (xs / a0) ** 2
        vis = h.facing(view, xs, ys) > 0.02
        pts = h.xy(view, h.on(xs, ys, 0.015))
        from geo import ribbon
        runs, cur = [], []
        for p, v in zip(pts, vis):
            if v:
                cur.append(p)
            elif cur:
                runs.append(cur); cur = []
        if cur:
            runs.append(cur)
        for r in runs:
            if len(r) > 2:
                bg = ribbon(np.array(r), [0.045 * k] * len(r))
                d.fill(bg, '#5a4038')
                d.outline(bg, d.lw * 0.6)
        lx = -0.28
        if float(h.facing(view, lx, y0)[0]) > 0.05:
            base = h.on(lx, y0 + 0.01, 0.03)[0]
            tip = base + np.array([0.0, 0.13, 0.22])
            M = h.to_model(np.array([base, tip]))
            g1 = tube(view, M, [0.09 * h.k, 0.12 * h.k])
            d.fill(g1, '#3e3533')
            d.fill(g1.difference(shift(g1, -0.05 * k, -0.04 * k)), '#2a2220')
            d.outline(g1, d.lw * 0.8)
            end = view.xy(h.to_model(tip[None]))[0]
            gl = Point(end).buffer(0.09 * k, 24)
            d.fill(gl, '#9fb3bd')
            d.fill(Point(end[0] - 0.03 * k, end[1] - 0.03 * k).buffer(0.025 * k, 12), '#ffffff')
            d.outline(gl, d.lw * 0.7)
    if glasses:
        # small round readers sitting low, on the middle of the nose
        rims = []
        for side in (-1, 1):
            cx, cy = side * 0.30, -0.18
            if float(h.facing(view, cx, cy)[0]) < 0.1:
                continue
            tt = np.linspace(0, 2 * np.pi, 40)
            pts = h.xy(view, h.on(cx + 0.13 * np.cos(tt), cy + 0.10 * np.sin(tt), 0.10))
            rims.append(pts)
            lens = poly(pts)
            d.fill(lens, '#ffffff', 0.18)
            d.line(np.vstack([pts, pts[:1]]), d.lw * 0.9, '#5a4a3a')
        br = h.xy(view, h.on(np.array([-0.17, 0.0, 0.17]), np.array([-0.16, -0.13, -0.16]), np.array([0.10])))
        d.line(br, d.lw * 0.9, '#5a4a3a')
        for side in (-1, 1):
            if float(h.facing(view, side * 0.6, -0.15)[0]) > 0.05:
                arm = h.xy(view, h.on(np.array([side * 0.43, side * 0.62, side * 0.74]), np.array([-0.16, -0.12, -0.10]), np.array([0.08])))
                d.line(arm, d.lw * 0.8, '#5a4a3a')


# ---------------------------------------------------------------- body
B = dict(
    hip_y=82, hip_x=9.5, thigh=39, shin=36.5, shoulder=(15.2, 130, -1.0), upper=28, fore=24, hand=17,
    arm_r=[4.4, 3.9, 3.3, 2.7], hand_r=2.5, leg_r=[8.0, 6.8, 5.0, 4.4, 4.9, 4.4, 3.3, 3.1],
    neck=(134.5, 145, -0.5, 1.0), neck_r=4.5, head_c=(0, 150.2, 2.6), head_h=23.5, chest_y=114,
    torso=[(74, 12, 8, -8), (82, 17.5, 10, -10), (92, 17.8, 12.5, -10), (101, 17.6, 13.5, -9.5), (110, 17.0, 12, -9.5),
           (118, 17.4, 10.5, -9.5), (125, 18.2, 9.5, -9.5), (129, 18.8, 8, -8.5), (132, 15.5, 6.5, -7.5),
           (134.5, 10.5, 5, -6.5), (136.5, 6.2, 4, -5.2)],
)

POSES = dict(
    watch=dict(
        # looking down over his glasses at a pocket watch in his palm; the other hand behind his back
        lean=3.0, head_fwd=2.0, head_rot=(-12, 16, 3),
        armr=dict(upper=(0.10, -0.80, 0.60), fore=(-0.55, 0.50, 0.40), hand=(-0.45, 0.35, 0.45), palm=(0.1, 1, 0.2)),
        arml=dict(upper=(0.10, -1, -0.32), fore=(-0.25, -0.30, -0.85), hand=(-0.6, -0.2, -0.6), palm=(0, 0, -1),
                  hand_behind=True),
        legl=dict(thigh=(0.07, -1, 0.02), shin=(0.0, -1, -0.03)),
        legr=dict(thigh=(0.07, -1, 0.02), shin=(0.0, -1, -0.03)),
    ),
    stand=dict(
        lean=4.0, head_fwd=2.0,
        arml=dict(upper=(0.10, -1, 0.04), fore=(0.03, -1, 0.18), hand=(0.0, -1, 0.15), palm=(-1, 0, 0.2)),
        armr=dict(upper=(0.10, -1, 0.04), fore=(0.03, -1, 0.18), hand=(0.0, -1, 0.15), palm=(-1, 0, 0.2)),
        legl=dict(thigh=(0.06, -1, 0.0), shin=(0.0, -1, -0.03)),
        legr=dict(thigh=(0.06, -1, 0.0), shin=(0.0, -1, -0.03)),
    ),
    behind=dict(
        # hands clasped behind the back: the grumpy watchmaker in his doorway
        lean=4.0, head_fwd=2.0,
        arml=dict(upper=(0.08, -1, -0.30), fore=(-0.45, -0.35, -0.75), hand=(-0.8, -0.2, -0.4), palm=(0, 0, -1),
                  hand_behind=True),
        armr=dict(upper=(0.08, -1, -0.30), fore=(-0.45, -0.30, -0.70), hand=(-0.8, -0.2, -0.4), palm=(0, 0, -1),
                  hand_behind=True),
        legl=dict(thigh=(0.07, -1, 0.02), shin=(0.0, -1, -0.03)),
        legr=dict(thigh=(0.07, -1, 0.02), shin=(0.0, -1, -0.03)),
    ),
)

SPEC = dict(
    skin=SKIN,
    top=dict(c='#eceee6', ease=0.6, hem=84, sleeve=dict(upto=0.62, ease=1.4), collar=3.2),
    over=dict(c='#8a5f3c', ease=1.3, hem=86, open=(0.0, 0.42, 112), buttons=[90, 97, 104, 110]),
    bottom=dict(kind='trousers', c='#6e675a', ease=1.6, waist=96),
    shoes=dict(c='#3a2e2a', len=26, r=3.6, out=14),
)


def watch(d, view, F):
    """a gold pocket watch lying in the palm, its chain running to the waistcoat pocket."""
    import numpy as np
    from geo import poly
    from dress import fill_part
    from shapely.geometry import Point
    J = F.J
    c = J['wrr'] + (J['hdr'] - J['wrr']) * 0.55 + np.array([0, 2.4, 0])
    n = np.array([0.2, 1.0, 0.35]); n /= np.linalg.norm(n)
    u = np.cross(n, [0, 0, 1.0]); u /= np.linalg.norm(u); w = np.cross(n, u)
    t = np.linspace(0, 2 * np.pi, 40, endpoint=False)
    disk = poly(view.xy(np.array([c + 2.6 * (np.cos(a) * u + np.sin(a) * w) for a in t])))
    face = poly(view.xy(np.array([c + n * 0.4 + 2.0 * (np.cos(a) * u + np.sin(a) * w) for a in t])))
    store = {}

    def draw():
        fill_part(d, disk, '#d6aa48', 0.3 * view.s)
        d.fill(face, '#f6efdc'); d.outline(face, d.lw * 0.5)
        ctr = view.xy((c + n * 0.45)[None])[0]
        d.line(np.array([ctr, ctr + [0, -1.5 * view.s]]), d.lw * 0.5)
        d.line(np.array([ctr, ctr + [1.1 * view.s, 0.3 * view.s]]), d.lw * 0.5)
        pocket = np.array([-6.0, 100.0, 12.5])
        chain = np.array([c + n * 0.2, (c + pocket) / 2 + [0, -9, 4], pocket])
        from geo import bezier
        d.line(view.xy(bezier(*chain, n=20)), d.lw * 0.8, '#b58a30')
    # the watch lies on the palm: drawn after the hand
    F.after_hands = getattr(F, 'after_hands', []) + [draw]


SPEC['prop'] = watch
