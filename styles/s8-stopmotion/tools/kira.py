"""Кира, about 15: thin and angular, a long face that hasn't settled, small pale eyes under low brows, a mouth pressed
shut or a crooked half-smirk. Short choppy dark hair, the long fringe falling over her left eye. An oversized
dark-plum hoodie, headphones round the neck and boot laces in acid lime, narrow trousers, heavy boots."""
import math
from sculpt import mix, pts, poly, f
import hair as H
from body import tx, front_patch

EXPR = {
    'sulk':  {'smile': -0.25, 'skew': 0.3, 'open': 0.8, 'lid_up': -0.3, 'brow_in': -0.022, 'gaze': (0.0, -0.1)},
    'smirk': {'smile': 0.2, 'skew': 0.7, 'open': 0.8, 'lid_up': -0.25, 'lid_lo': 0.2, 'brow_in': -0.008, 'brow_out': 0.014,
              'gaze': (0.0, -0.06)},
}
LIME = '#c9e028'


def kira_hair(h, d, P, ex):
    part = -0.45

    def line(phi):
        a = abs(phi)
        return -0.27 + 0.17 * min(1.0, a / 1.1) ** 2 + 0.25 * max(0.0, a - 1.1)

    locks = []
    # the fringe: from the part across the forehead and down over her left eye, cut to uneven points
    for k, ln in enumerate((0.1, 0.25, 0.31, 0.2)):
        p = H.surf_path(h, [(part + 0.04, -0.45 + 0.015 * k), (0.0 + 0.12 * k, -0.27 + 0.05 * k), (0.28 + 0.12 * k, -0.08 + 0.04 * k)],
                        out=(0.012, 0.05), k=1.03)
        p += H.fall(p[-1], ln, n=4, side=1, out_x=0.015, back_z=-0.01, flick=-0.025)
        locks.append(H.Lock(p, 0.18, 0.0, taper=1.0, root=0.5, strands=4, z_bias=0.35 - 0.04 * k))
    # her left side, behind the fringe, to the jaw
    for k, ln in enumerate((0.27, 0.2)):
        p = H.surf_path(h, [(part + 0.04, -0.46), (0.95 + 0.25 * k, -0.2), (1.3 + 0.2 * k, 0.03)], out=(0.012, 0.05), k=1.03)
        p += H.fall(p[-1], ln, n=4, side=1, out_x=0.03, back_z=-0.03, flick=0.045)
        locks.append(H.Lock(p, 0.19, 0.0, taper=1.0, strands=4, z_bias=0.2 - 0.08 * k))
    # her right side: short, behind the ear, the ends flicking out
    for k, ln in enumerate((0.16, 0.27, 0.2)):
        p = H.surf_path(h, [(part - 0.04, -0.45 + 0.015 * k), (-1.0 - 0.18 * k, -0.2 + 0.04 * k), (-1.42 - 0.16 * k, 0.0 + 0.02 * k)],
                        out=(0.012, 0.05), k=1.03)
        p += H.fall(p[-1], ln, n=4, side=-1, out_x=0.03, back_z=-0.03, flick=0.05)
        locks.append(H.Lock(p, 0.18, 0.0, taper=1.0, strands=4, z_bias=0.25 - 0.07 * k))
    # the back: short, chopped at different lengths
    for k, (phb, ln) in enumerate(((-2.0, 0.17), (-2.6, 0.25), (3.1, 0.15), (2.6, 0.24), (2.0, 0.18))):
        p = H.surf_path(h, [(part, -0.45), (phb * 0.6, -0.3), (phb, 0.08)], out=(0.01, 0.04), k=1.03)
        p += H.fall(p[-1], ln, n=4, side=1 if phb > 0 else -1, out_x=0.04, flick=0.05)
        locks.append(H.Lock(p, 0.24, 0.0, taper=1.1, strands=4, z_bias=-0.2))
    return dict(col=P['hair_col'], locks=locks, cap=(line, 0.18, 1.035))


KIRA = dict(
    name='kira',
    shape=dict(
        a=[(-0.5, 0.02), (-0.46, 0.19), (-0.38, 0.29), (-0.25, 0.335), (-0.1, 0.34), (0.0, 0.33), (0.1, 0.312),
           (0.2, 0.282), (0.3, 0.236), (0.4, 0.165), (0.46, 0.105), (0.5, 0.045)],
        front=[(-0.5, -0.02), (-0.46, 0.2), (-0.38, 0.33), (-0.25, 0.4), (-0.12, 0.415), (0.0, 0.4), (0.1, 0.39),
               (0.2, 0.37), (0.3, 0.35), (0.4, 0.32), (0.46, 0.28), (0.5, 0.21)],
        back=[(-0.5, -0.02), (-0.46, -0.24), (-0.38, -0.38), (-0.25, -0.46), (-0.1, -0.47), (0.0, -0.44), (0.1, -0.36),
              (0.2, -0.22), (0.3, -0.08), (0.4, 0.04), (0.46, 0.1), (0.5, 0.13)],
        bumps=[(0.93, 0.11, 0.06, 0.3, 0.07), (0.0, 0.455, 0.06, 0.3, 0.045), (0.38, -0.01, 0.03, 0.3, 0.05)]),
    skin='#edd3c2', skin_shade='#a06c74', shade='#5e3040', shade_depth=0.65, blush=0.16, blush_col='#d0606e', skin_tex=0.05,
    eye_phi=0.43, eye_y=0.09, eye_r=0.074, eye_w=0.086, eye_open=0.8, eye_tilt=0.012, iris_r=0.05, iris='#77828e',
    lash='#1a1016', lash_w=0.019, wing=1.0, lid_paint='#3a2438', lid_paint_a=0.5, socket_a=0.4, lid_top=0.74, lid_bot=0.42,
    brow_gap=0.078, brow_w=0.08, brow_th=0.019, brow_col='#241a22', brow_arch=0.002, brow_taper=0.6,
    nose_root=0.13, nose_tip=0.268, nose_len=0.058, nose_w=0.028, nose_fade=0.5,
    mouth_y=0.368, mouth_w=0.07, lip='#a8565c', upper_lip=0.008, lower_lip=0.013,
    ear_phi=1.5, ear_y=0.15, ear_w=0.065, ear_h=0.15, ear_out=22,
    hair=kira_hair, hair_col='#2c2230', hair_shade='#08040a',
    faces={'joy': EXPR['smirk']},       # she never smiles openly: her joy is the crooked half-smirk
)

HOODIE, CORD = '#3b2540', '#b9a8b8'
POCKET = [(-0.24, 1.62), (0.24, 1.62), (0.34, 1.86), (0.34, 2.04), (-0.34, 2.04), (-0.34, 1.86)]


def kira_details(d, T, N, P, B, S):
    """The kangaroo pocket, the ribbed hem, the hood's two cords."""
    res = []
    dark = mix(HOODIE, '#000000', 0.3)
    pk = front_patch(T, POCKET, 0.004)
    res.append(d.groove(poly(pk), dark, S * 0.012, soft=1.2, depth=-4))
    hem = front_patch(T, [(-0.47 + 0.94 * i / 12, 2.12) for i in range(13)], 0.004)
    res.append(d.groove(pts(hem, close=False), dark, S * 0.012, soft=1.2, depth=-4))
    for side, ln in ((-1, 0.36), (1, 0.44)):
        c = front_patch(T, [(side * (0.045 + 0.012 * math.sin(3 * t)), 0.9 + ln * t) for t in [i / 6 for i in range(7)]], 0.012)
        res.append(d.bump(pts(c, close=False), CORD, soft=1.2, height=max(2, S * 0.012), spec=0.2, stroke=True, sw=S * 0.016))
        e = c[-1]
        res.append(d.bump(f'M{f(e[0])} {f(e[1])} l0 {f(S*0.045)}', '#8a8a92', soft=1, height=2.5, spec=0.8, shine=40, stroke=True, sw=S * 0.022))
    return res


def kira_headphones(d, T, C, P, B, S):
    """Headphones hung round the neck over the hood: two cups resting at the collarbones, turned toward each other
    (the lime shell outside, the dark cushion showing on the inner side), the band going back round the neck."""
    res = []
    dark = '#26242c'
    oval = lambda rx, ry, dx=0.0: poly([(dx + rx * math.cos(t), ry * math.sin(t)) for t in [2 * math.pi * i / 28 for i in range(28)]])
    for side in sorted((-1, 1), key=lambda s: C.rot(C.surf(s, 0.74, 0.05))[2]):
        band = [C.P(C.surf(side * (1.0 + 0.8 * i / 6), 0.7 - 0.1 * i / 6, 0.03)) for i in range(7)
                if C.facing(side * (1.0 + 0.8 * i / 6), 0.66) > -0.05]
        if C.facing(side, 0.76) < -0.1:
            continue
        if len(band) > 1:
            res.append(d.bump(pts(band, close=False), dark, soft=1.5, height=max(3, S * 0.02), spec=0.6, shine=30,
                              stroke=True, sw=S * 0.04))
        tr, _ = C.frame(side, 0.76, 0.06)
        res.append(d.bump(oval(0.062, 0.1, -side * 0.035), dark, soft=max(1.5, S * 0.012), height=max(3, S * 0.03), spec=0.3, tr=tr))
        res.append(d.bump(oval(0.066, 0.105), LIME, soft=max(2, S * 0.018), height=max(4, S * 0.045), spec=0.7, shine=26, tr=tr))
        res.append(d.groove(oval(0.04, 0.07), mix(LIME, '#000000', 0.25), 0.008, soft=1.2, depth=-3, tr=tr))
    return res


KIRA_BODY = dict(
    torso=dict(
        a=[(0.6, 0.1), (0.64, 0.24), (0.7, 0.35), (0.78, 0.42), (0.9, 0.455), (1.2, 0.46), (1.6, 0.47), (2.0, 0.48), (2.2, 0.47)],
        front=[(0.6, 0.02), (0.7, 0.11), (0.85, 0.17), (1.1, 0.2), (1.5, 0.21), (2.2, 0.22)],
        back=[(0.6, -0.14), (0.7, -0.22), (0.85, -0.27), (1.1, -0.27), (1.5, -0.23), (2.2, -0.21)]),
    torso_y=(0.6, 2.2),
    neck=dict(a=[(0.2, 0.088), (0.85, 0.095)], front=[(0.2, 0.05), (0.85, 0.07)], back=[(0.2, -0.12), (0.85, -0.12)]),
    neck_y=(0.25, 0.85),
    collar=dict(a=[(0.56, 0.13), (0.64, 0.2), (0.76, 0.3), (0.87, 0.39), (0.91, 0.3), (0.93, 0.12)], front=[(0.56, 0.06), (0.74, 0.13), (0.9, 0.17)],
                back=[(0.56, -0.2), (0.64, -0.3), (0.76, -0.38), (0.9, -0.34)]),
    collar_y=(0.56, 0.93), collar_col=mix(HOODIE, '#ffffff', 0.04),
    open_neck=lambda T: [T.P(q) for q in ((-0.13, 0.3, 0.12), (0.13, 0.3, 0.12), (0.09, 0.72, 0.16), (0.0, 0.95, 0.2), (-0.09, 0.72, 0.16))],
    arm=dict(a=[(0.8, 0.06), (0.86, 0.11), (2.2, 0.1)], front=[(0.8, 0.05), (2.2, 0.1)], back=[(0.8, -0.06), (2.2, -0.1)]),
    arm_x=0.42, arm_y=(0.8, 2.2),
    cloth=HOODIE, tex='felt', tex_amount=0.16, shade='#120816',
    details=kira_details, collar_extra=kira_headphones,
)

BOOT, TROUSERS = '#27222a', '#33333c'
FEET = {-1: (-0.12, 0.0), 1: (0.3, 0.05)}       # where each boot stands (x, z): the weight on her right leg


def _laces(d, T, P, S):
    """Lime laces crossing up the front of each boot."""
    s = ''
    for side, (x, z) in FEET.items():
        for i in range(4):
            y = 3.44 + 0.075 * i
            a, b = T.P((x - 0.05, y, z + 0.115)), T.P((x + 0.05, y + 0.035, z + 0.115))
            c, e = T.P((x + 0.05, y, z + 0.115)), T.P((x - 0.05, y + 0.035, z + 0.115))
            s += f'<path d="M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])} M{f(c[0])} {f(c[1])} L{f(e[0])} {f(e[1])}"/>'
    g = d.relief(1.0, 2.0, 0.3, 20)
    return (0.3, f'<g filter="url(#{g})" fill="none" stroke="{LIME}" stroke-width="{f(S*0.016)}" stroke-linecap="round">{s}</g>')


def _pocket_lip(d, T, P, S):
    """The near end of the pocket laid over the forearm that goes into it, fading into the hoodie's front."""
    lip = front_patch(T, [(-0.25, 1.62), (-0.06, 1.62), (-0.06, 2.04), (-0.34, 2.04), (-0.34, 1.86)], 0.02)
    x0, x1 = T.P(tx(T, -0.3, 1.85))[0], T.P(tx(T, -0.06, 1.85))[0]
    g = d.lin([(0, HOODIE, 1), (0.45, HOODIE, 1), (1, HOODIE, 0)], x1=f(x0), y1=0, x2=f(x1), y2=0, units='userSpaceOnUse')
    s = f'<path d="{poly(lip)}" fill="url(#{g})"/><path d="{poly(lip)}" fill="url(#{g})" filter="url(#{d.tex("felt", 1.0, 0.16)})"/>'
    s += d.groove(pts(lip[:1] + lip[3:][::-1], close=False), mix(HOODIE, '#000000', 0.3), S * 0.014, soft=1.2, depth=-4)
    return (0.6, s)


def _legs(side):
    x, z = FEET[side]
    hip = (-0.05 + side * 0.15, 2.25, 0.0)
    knee = (-0.16, 3.0, 0.03) if side < 0 else (0.3, 2.95, 0.14)
    return [dict(path=[hip, knee, (x, 3.5, z)], r0=0.1, r1=0.06, col=TROUSERS, tex='cloth', tex_amount=0.15, z=-0.3),
            dict(path=[(x, 3.36, z), (x, 3.72, z)], r0=0.1, r1=0.108, col=BOOT, tex='clay', tex_amount=0.05, shade='#000000', z=-0.2)]


def _arms(side):
    if side < 0:      # her right arm: the hand pushed into the pocket
        path = [(-0.42, 0.9, -0.02), (-0.63, 1.5, -0.03), (-0.2, 1.9, 0.28)]
    else:             # her left: hanging, the fist half in the long sleeve
        path = [(0.43, 0.9, -0.02), (0.6, 1.55, -0.02), (0.6, 2.2, 0.05)]
    return [dict(path=path, r0=0.105, r1=0.092, col=HOODIE, tex='felt', tex_amount=0.16, shade='#120816', z=0.06)]


KIRA_FIG = dict(
    torso=dict(a=KIRA_BODY['torso']['a'] + [(2.3, 0.455), (2.36, 0.4), (2.38, 0.25)], front=KIRA_BODY['torso']['front'] + [(2.36, 0.2)],
               back=KIRA_BODY['torso']['back'] + [(2.36, -0.2)], x=[(0.6, 0.0), (1.3, 0.035), (2.38, -0.05)]),
    torso_y=(0.6, 2.38),
    legs=_legs,
    shoe=lambda side: dict(ankle=(FEET[side][0], 3.74, FEET[side][1]), len=0.5, col=BOOT, h=0.15, w=0.13),
    arms=_arms,
    hand=lambda side: None if side < 0 else dict(wrist=(0.6, 2.2, 0.05), dir=(0.0, 1.0, 0.05), size=0.2, pose='fist'),
    props=[_laces, _pocket_lip],
)
