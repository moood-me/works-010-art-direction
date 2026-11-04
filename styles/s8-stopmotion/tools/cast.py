"""The cast: four puppets. Each one is a dict P of head shape, features, colours and a hair function.
To add a character, copy one of these, change the tables and numbers, write its hair and its body (body.py)."""
import math
from sculpt import mix, pts, poly, f
import hair as H

# ------------------------------------------------------------------ expressions (shared)
EXPR = {
    'calm':     {'smile': 0.12},
    'dream':    {'gaze': (0.18, -0.22), 'open': 0.92, 'smile': 0.25, 'brow_in': 0.008},
    'joy':      {'smile': 0.9, 'mopen': 0.35, 'lid_lo': 0.35, 'open': 0.85, 'brow_out': 0.01, 'brow_in': 0.012, 'wide': 1.2},
    'surprise': {'open': 1.35, 'lid_up': 0.25, 'brow_in': 0.03, 'brow_out': 0.03, 'mopen': 0.55, 'wide': 0.75,
                 'teeth': False, 'pupil': 0.3},
    'sad':      {'open': 0.78, 'brow_in': 0.03, 'brow_out': -0.012, 'smile': -0.55, 'gaze': (0.0, 0.25), 'lid_up': -0.1},
    'anger':    {'open': 0.8, 'brow_in': -0.03, 'brow_out': 0.01, 'smile': -0.4, 'mopen': 0.28, 'lower_teeth': True,
                 'lid_up': -0.18, 'wide': 1.05},
    'grin':     {'smile': 0.75, 'skew': 0.35, 'mopen': 0.22, 'lid_lo': 0.3, 'brow_in': 0.005, 'brow_out': 0.015},
    'stern':    {'smile': -0.15, 'open': 0.82, 'lid_up': -0.12, 'brow_in': -0.008},
}


# ------------------------------------------------------------------ Аня, 20
def anya_hair(h, d, P, ex):
    """Soft waves to the shoulders, parted on her right; the long side sweeps over the forehead to her left."""
    part = -0.38

    def line(phi):                     # hairline: high at the forehead, down at the temples
        a = abs(phi)
        return -0.26 + 0.17 * min(1.0, a / 1.1) ** 2 + 0.25 * max(0.0, a - 1.1)

    locks = []
    # the sweep: from the part across the forehead to her left temple, then down past the cheek to the shoulder
    for k in range(3):
        p = H.surf_path(h, [(part + 0.04, -0.44 + 0.02 * k), (0.05 + 0.1 * k, -0.24 + 0.075 * k), (0.7 + 0.1 * k, -0.08 + 0.06 * k),
                            (1.2 + 0.06 * k, 0.1 + 0.03 * k)], out=(0.012, 0.05 + 0.01 * (2 - k)), k=1.03)
        p += H.fall(p[-1], 0.5 - 0.06 * k, n=7, side=1, out_x=0.06, back_z=-0.05, wave=0.03, waves=0.8, phase=0.6 * k, flick=0.06)
        locks.append(H.Lock(p, 0.2 - 0.02 * k, 0.0, taper=1.3, z_bias=0.3 - 0.06 * k))
    # her right side: from the part down over the temple, past the cheek
    for k in range(3):
        p = H.surf_path(h, [(part - 0.04, -0.44 + 0.02 * k), (-0.8 - 0.15 * k, -0.2 + 0.05 * k), (-1.25 - 0.12 * k, 0.08 + 0.03 * k)],
                        out=(0.012, 0.05), k=1.03)
        p += H.fall(p[-1], 0.52 - 0.04 * k, n=7, side=-1, out_x=0.06, back_z=-0.04, wave=0.03, waves=0.8, phase=0.4 + 0.7 * k, flick=0.06)
        locks.append(H.Lock(p, 0.18, 0.0, taper=1.3, z_bias=0.25 - 0.06 * k))
    # back: wide locks hanging behind
    for k, phb in enumerate((-2.0, -2.6, 3.1, 2.6, 2.0)):
        p = H.surf_path(h, [(part, -0.45), (phb * 0.6, -0.3), (phb, 0.08)], out=(0.01, 0.04), k=1.03)
        p += H.fall(p[-1], 0.5, n=7, side=1 if phb > 0 else -1, out_x=0.05, back_z=0.0, wave=0.025, phase=k, flick=0.05)
        locks.append(H.Lock(p, 0.24, 0.02, taper=1.2, z_bias=-0.2))
    return dict(col=P['hair_col'], locks=locks, cap=(line, 0.18, 1.035))


ANYA = dict(
    name='anya',
    shape=dict(
        a=[(-0.5, 0.02), (-0.46, 0.2), (-0.38, 0.3), (-0.25, 0.35), (-0.1, 0.355), (0.0, 0.345), (0.1, 0.33),
           (0.2, 0.3), (0.3, 0.245), (0.4, 0.17), (0.46, 0.11), (0.5, 0.05)],
        bumps=[(0.95, 0.13, 0.05, 0.35, 0.09), (0.0, 0.44, 0.05, 0.35, 0.05), (0.38, -0.01, 0.025, 0.3, 0.05)],
        front=[(-0.5, -0.02), (-0.46, 0.2), (-0.38, 0.33), (-0.25, 0.4), (-0.12, 0.42), (0.0, 0.405), (0.1, 0.395),
               (0.2, 0.37), (0.3, 0.345), (0.4, 0.31), (0.46, 0.27), (0.5, 0.2)],
        back=[(-0.5, -0.02), (-0.46, -0.24), (-0.38, -0.38), (-0.25, -0.46), (-0.1, -0.47), (0.0, -0.44), (0.1, -0.36),
              (0.2, -0.22), (0.3, -0.08), (0.4, 0.04), (0.46, 0.1), (0.5, 0.13)]),
    skin='#f0c4a4', skin_shade='#b0606a', shade='#5a2a40', blush=0.38, freckles=16, skin_tex=0.05,
    eye_phi=0.43, eye_y=0.11, eye_r=0.082, eye_w=0.092, eye_open=0.92, eye_tilt=0.006, iris_r=0.056, iris='#5a7a4a',
    lash='#24120e', lash_w=0.015, wing=1.5, lid_paint='#b0607a', lid_paint_a=0.35, socket_a=0.25,
    brow_gap=0.1, brow_w=0.072, brow_th=0.012, brow_col='#7a3a22', brow_arch=0.014,
    nose_root=0.17, nose_tip=0.27, nose_len=0.045, nose_w=0.032, nose_up=0.02,
    mouth_y=0.36, mouth_w=0.08, lip='#c0605e', upper_lip=0.014, lower_lip=0.02,
    ear_phi=1.5, ear_y=0.15, ear_w=0.06, ear_h=0.15, ear_out=20,
    hair=anya_hair, hair_col='#9a4424', hair_shade='#2a0a06',
)


def anya_details(d, T, N, P, B, S):
    """Neckline of the sweater: a scoop of skin and a ribbed band round it."""
    out = []
    tr, _ = T.frame(0, 0.66, 0.0)
    scoop = [(-0.2, -0.02), (-0.14, 0.08), (0, 0.13), (0.14, 0.08), (0.2, -0.02), (0.0, -0.05)]
    return out


ANYA_BODY = dict(
    torso=dict(
        a=[(0.6, 0.12), (0.64, 0.3), (0.69, 0.43), (0.76, 0.51), (0.86, 0.54), (1.0, 0.52), (1.2, 0.47), (1.5, 0.41), (1.9, 0.38), (2.2, 0.42)],
        front=[(0.6, 0.02), (0.7, 0.12), (0.85, 0.19), (1.05, 0.25), (1.2, 0.27), (1.4, 0.22), (1.8, 0.17), (2.2, 0.2)],
        back=[(0.6, -0.12), (0.7, -0.18), (0.85, -0.22), (1.05, -0.23), (1.4, -0.2), (1.8, -0.16), (2.2, -0.2)]),
    torso_y=(0.6, 2.2),
    neck=dict(a=[(0.2, 0.1), (0.8, 0.11)], front=[(0.2, 0.06), (0.8, 0.08)], back=[(0.2, -0.13), (0.8, -0.13)]),
    neck_y=(0.25, 0.8),
    neckline=(0.82, 0.64, 0.035, '#b88028', 0.26),
    arm=dict(a=[(0.8, 0.06), (0.86, 0.11), (1.4, 0.105), (2.2, 0.09)],
             front=[(0.8, 0.05), (0.9, 0.1), (2.2, 0.09)], back=[(0.8, -0.06), (0.9, -0.12), (2.2, -0.09)]),
    arm_x=0.47, arm_y=(0.8, 2.2),
    cloth='#c8902e', tex='felt', tex_amount=0.12, shade='#3a2030', ribs=0.1,
)


# ------------------------------------------------------------------ Савелий Петрович, 70, часовщик
import props
from body import tx, front_patch, stripes


def savely_hair(h, d, P, ex):
    """Bald dome; a horseshoe of white tufts over the ears and round the back, sticking out a little."""
    locks = []
    for side in (-1, 1):
        for k in range(4):
            phi0 = side * (1.15 + 0.32 * k)
            p = H.surf_path(h, [(phi0, -0.2 + 0.03 * k), (phi0 + side * 0.12, 0.0 + 0.03 * k)], out=(0.0, 0.03), k=1.0)
            p += H.fall(p[-1], 0.08, n=3, side=side, out_x=0.06, back_z=-0.02, flick=0.03)
            locks.append(H.Lock(p, 0.16, 0.0, taper=1.0, root=0.7, strands=4, z_bias=0.0))
    for k, ph in enumerate((2.5, 2.85, -2.85, -2.5, 3.14)):
        p = H.surf_path(h, [(ph, -0.18), (ph, 0.12)], out=(0.0, 0.025), k=1.0)
        locks.append(H.Lock(p, 0.24, 0.05, taper=1.0, root=0.7, strands=5, z_bias=-0.3))
    return dict(col=P['hair_col'], locks=locks, cap=None)


def savely_under_nose(h, d, P, ex):
    return props.moustache(h, d, P, P['hair_col'], w=0.16, droop=0.06, thick=0.075, ex=ex)


def savely_over(h, d, P, ex):
    return (props.glasses(h, d, P, 'round', rw=0.078, rh=0.068, out=0.075, col='#8a6a3a', lw=0.009, y_off=0.035)
            + props.loupe(h, d, P, side=-1))


SAVELY = dict(
    name='savely',
    shape=dict(
        a=[(-0.5, 0.03), (-0.46, 0.22), (-0.38, 0.33), (-0.25, 0.385), (-0.1, 0.39), (0.0, 0.38), (0.1, 0.375),
           (0.2, 0.37), (0.3, 0.345), (0.4, 0.28), (0.46, 0.2), (0.5, 0.1)],
        front=[(-0.5, -0.02), (-0.46, 0.2), (-0.38, 0.33), (-0.25, 0.4), (-0.12, 0.42), (0.0, 0.4), (0.1, 0.39),
               (0.2, 0.38), (0.3, 0.36), (0.4, 0.33), (0.46, 0.29), (0.5, 0.22)],
        back=[(-0.5, -0.02), (-0.46, -0.24), (-0.38, -0.38), (-0.25, -0.45), (-0.1, -0.46), (0.0, -0.43), (0.1, -0.35),
              (0.2, -0.22), (0.3, -0.1), (0.4, 0.0), (0.46, 0.06), (0.5, 0.1)],
        bumps=[(1.0, 0.33, 0.06, 0.4, 0.1), (0.0, 0.45, 0.04, 0.4, 0.05), (0.38, -0.02, 0.04, 0.35, 0.05)]),
    skin='#e6a886', skin_shade='#a04a48', shade='#5a2030', blush=0.4, blush_col='#d8505a', skin_tex=0.08,
    eye_phi=0.42, eye_y=0.06, eye_r=0.066, eye_w=0.075, eye_open=0.7, eye_tilt=-0.008, iris_r=0.045, iris='#4a6a8a',
    lash='#3a2420', lash_w=0.01, wing=0.4, socket_a=0.4, bags=2, lid_top=0.7, lid_bot=0.4,
    brow_gap=0.085, brow_w=0.095, brow_th=0.04, brow_col='#e8e2d8', brow_arch=0.004,
    nose_root=0.07, nose_tip=0.25, nose_len=0.1, nose_w=0.068, nose_tint='#d0504a', nose_fade=0.4,
    mouth_y=0.36, mouth_w=0.075, lip='#b05a58', upper_lip=0.008, lower_lip=0.016,
    ear_phi=1.48, ear_y=0.12, ear_w=0.1, ear_h=0.2, ear_out=28, ear_tint='#d06060',
    hair=savely_hair, hair_col='#e8e2d8', hair_shade='#6a5a5a', hair_split=-0.15,
    under_nose=savely_under_nose, over_all=savely_over,
    wrinkles=[(0.0, -0.2, [(-0.16, 0.0), (0.0, -0.012), (0.16, 0.0)], 0.007),
              (0.0, -0.25, [(-0.13, 0.0), (0.0, -0.01), (0.13, 0.0)], 0.006),
              (0.0, -0.15, [(-0.12, 0.0), (0.0, -0.008), (0.12, 0.0)], 0.006),
              (0.7, 0.07, [(0.0, -0.03), (0.03, 0.0), (0.0, 0.03)], 0.005),
              (-0.7, 0.07, [(0.0, -0.03), (-0.03, 0.0), (0.0, 0.03)], 0.005),
              (0.32, 0.3, [(0.0, -0.06), (0.03, 0.0), (0.05, 0.07)], 0.008),
              (-0.32, 0.3, [(0.0, -0.06), (-0.03, 0.0), (-0.05, 0.07)], 0.008)],
    gaze=(0.0, 0.05),
)


def savely_inside(d, T, P, B, S, o):
    """Waistcoat open in a V over the shirt; buttons; a watch chain."""
    shirt = '#e8dcc0'
    v = front_patch(T, [(-0.2, 0.6), (-0.13, 0.75), (-0.03, 1.15), (0.0, 1.2), (0.03, 1.15), (0.13, 0.75), (0.2, 0.6)])
    res = f'<path d="{pts(v)}" fill="{shirt}"/>'
    # tie
    tie = front_patch(T, [(-0.035, 0.66), (0.035, 0.66), (0.05, 1.0), (0.0, 1.08), (-0.05, 1.0)], 0.005)
    res += f'<path d="{pts(tie)}" fill="#7a2a2a"/>'
    # buttons and chain
    for k in range(3):
        y = 1.22 + 0.13 * k
        p = T.P(tx(T, 0.0, y, 0.01))
        res += f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(S*0.018)}" fill="#3a2418"/>'
    ch = [T.P(tx(T, -0.06 + 0.32 * t, 1.3 + 0.12 * math.sin(math.pi * t), 0.012)) for t in [i / 8 for i in range(9)]]
    res += f'<path d="{pts(ch, close=False)}" fill="none" stroke="#d8a840" stroke-width="{f(S*0.008)}" stroke-dasharray="{f(S*0.008)} {f(S*0.004)}"/>'
    return res


def savely_details(d, T, N, P, B, S):
    """Shirt collar points; buttons as relief; lapel edges as grooves."""
    res = []
    for side in (-1, 1):
        col = front_patch(T, [(side * 0.04, 0.6), (side * 0.15, 0.6), (side * 0.09, 0.74), (side * 0.03, 0.7)], 0.01)
        res.append(d.bump(pts(col), '#efe4cc', soft=max(1.5, S * 0.008), height=max(2, S * 0.02), spec=0.3))
        edge = front_patch(T, [(side * 0.2, 0.6), (side * 0.13, 0.75), (side * 0.03, 1.15), (0.0, 1.2)], 0.0)
        res.append(d.groove(pts(edge, close=False), '#6a4a32', S * 0.012, soft=1.2, depth=-4))
    for k in range(3):
        y = 1.22 + 0.13 * k
        p = T.P(tx(T, 0.0, y, 0.01))
        res.append(d.bump(f'M{f(p[0]-S*0.018)} {f(p[1])} a{f(S*0.018)} {f(S*0.018)} 0 1 0 {f(S*0.036)} 0 a{f(S*0.018)} {f(S*0.018)} 0 1 0 {f(-S*0.036)} 0Z',
                          '#3a2418', soft=1.2, height=3, spec=0.6, shine=30))
    return res


SAVELY_BODY = dict(
    torso=dict(
        a=[(0.58, 0.14), (0.63, 0.34), (0.7, 0.46), (0.8, 0.53), (0.95, 0.56), (1.2, 0.6), (1.5, 0.63), (1.8, 0.6), (2.0, 0.56)],
        front=[(0.58, 0.04), (0.7, 0.15), (0.9, 0.24), (1.2, 0.36), (1.45, 0.42), (1.7, 0.38), (2.0, 0.3)],
        back=[(0.58, -0.16), (0.7, -0.25), (0.9, -0.3), (1.2, -0.28), (1.5, -0.25), (2.0, -0.22)]),
    torso_y=(0.58, 2.0),
    neck=dict(a=[(0.2, 0.15), (0.75, 0.16)], front=[(0.2, 0.08), (0.75, 0.1)], back=[(0.2, -0.15), (0.75, -0.17)]),
    neck_y=(0.3, 0.75),
    arm=dict(a=[(0.78, 0.07), (0.84, 0.13), (1.4, 0.125), (2.0, 0.11)],
             front=[(0.78, 0.06), (0.88, 0.12), (2.0, 0.11)], back=[(0.78, -0.07), (0.88, -0.13), (2.0, -0.11)]),
    arm_x=0.5, arm_y=(0.78, 2.0),
    cloth='#6e4c34', tex='cloth', tex_amount=0.3, shade='#24141a', sleeve='#e2d6bc', sleeve_tex='cloth',
    inside=savely_inside, details=savely_details,
)


# ------------------------------------------------------------------ Тим, 8
def tim_hair(h, d, P, ex):
    """Thick tousled hair with a cowlick at the crown and a fringe of chunky clumps."""
    def line(phi):
        a = abs(phi)
        return -0.2 + 0.12 * min(1.0, a / 1.2) ** 2 + 0.3 * max(0.0, a - 1.2)
    locks = []
    # fringe clumps falling forward over the forehead
    for k, (ph, ln) in enumerate(((-0.75, 0.16), (-0.45, 0.2), (-0.15, 0.22), (0.15, 0.2), (0.45, 0.19), (0.75, 0.15))):
        p = H.surf_path(h, [(ph * 0.4, -0.46), (ph * 0.8, -0.32), (ph, -0.2 + 0.02 * abs(k - 2.5))], out=(0.03, 0.06), k=1.03)
        p += H.fall(p[-1], ln * 0.4, n=3, side=1 if ph > 0 else -1, out_x=0.03, back_z=0.03, flick=0.03)
        locks.append(H.Lock(p, 0.15, 0.0, taper=1.0, root=0.6, strands=3, z_bias=0.3))
    # sides over the ears
    for side in (-1, 1):
        for k in range(2):
            p = H.surf_path(h, [(side * 0.6, -0.45), (side * (1.15 + 0.3 * k), -0.2), (side * (1.35 + 0.3 * k), 0.0)], out=(0.03, 0.05), k=1.03)
            p += H.fall(p[-1], 0.05, n=2, side=side, out_x=0.04, flick=0.03)
            locks.append(H.Lock(p, 0.17, 0.0, taper=1.0, root=0.6, strands=3, z_bias=0.1))
    # back
    for ph in (2.2, 2.7, 3.14, -2.7, -2.2, 1.7, -1.7):
        p = H.surf_path(h, [(ph * 0.4, -0.46), (ph, -0.1), (ph, 0.12)], out=(0.03, 0.05), k=1.03)
        locks.append(H.Lock(p, 0.24, 0.0, taper=1.2, root=0.6, strands=4, z_bias=-0.3))
    # the cowlick: two clumps standing up at the crown
    for k, (dx, h_) in enumerate(((-0.06, 0.2), (0.05, 0.15))):
        base = h.surf(-0.2 + dx * 3, -0.47, 0.02, 1.03)
        p = [base, (base[0] + dx, base[1] - h_ * 0.5, base[2] - 0.02), (base[0] + dx * 2.5, base[1] - h_, base[2] - 0.06)]
        locks.append(H.Lock(p, 0.09, 0.0, taper=1.0, root=0.8, strands=2, z_bias=0.4))
    return dict(col=P['hair_col'], locks=locks, cap=(line, 0.15, 1.03))


TIM = dict(
    name='tim',
    shape=dict(
        a=[(-0.5, 0.03), (-0.46, 0.24), (-0.38, 0.35), (-0.25, 0.41), (-0.1, 0.425), (0.0, 0.42), (0.1, 0.405),
           (0.2, 0.37), (0.3, 0.32), (0.4, 0.24), (0.46, 0.17), (0.5, 0.08)],
        front=[(-0.5, -0.02), (-0.46, 0.21), (-0.38, 0.34), (-0.25, 0.41), (-0.12, 0.43), (0.0, 0.42), (0.1, 0.42),
               (0.2, 0.41), (0.3, 0.38), (0.4, 0.33), (0.46, 0.28), (0.5, 0.2)],
        back=[(-0.5, -0.02), (-0.46, -0.25), (-0.38, -0.39), (-0.25, -0.46), (-0.1, -0.47), (0.0, -0.44), (0.1, -0.36),
              (0.2, -0.22), (0.3, -0.08), (0.4, 0.04), (0.46, 0.1), (0.5, 0.13)],
        bumps=[(0.95, 0.22, 0.06, 0.45, 0.1)]),
    skin='#f2c09a', skin_shade='#b8606a', shade='#5a2a40', blush=0.45, blush_col='#e85a5a', freckles=26, skin_tex=0.05,
    eye_phi=0.44, eye_y=0.1, eye_r=0.088, eye_w=0.092, eye_open=1.05, eye_tilt=0.0, iris_r=0.062, iris='#6a4a2a',
    lash='#2a1810', lash_w=0.012, wing=0.6, socket_a=0.2, lid_top=0.82, lid_bot=0.45,
    brow_gap=0.1, brow_w=0.075, brow_th=0.022, brow_col='#5a3018', brow_arch=0.006,
    nose_root=0.17, nose_tip=0.265, nose_len=0.05, nose_w=0.04, nose_up=0.03, nose_fade=0.6,
    mouth_y=0.37, mouth_w=0.085, lip='#c8706a', upper_lip=0.01, lower_lip=0.017,
    ear_phi=1.45, ear_y=0.15, ear_w=0.12, ear_h=0.19, ear_out=42, ear_tint='#e87a70',
    hair=tim_hair, hair_col='#7a4220', hair_shade='#1a0a04',
)


def tim_inside(d, T, P, B, S, o):
    return stripes(d, T, 0.62, 2.0, 0.09, '#f0e6d2', o)


def tim_arm_inside(d, A, P, B, S, o):
    return stripes(d, A, 0.8, 1.9, 0.09, '#f0e6d2', o)


TIM_BODY = dict(
    torso=dict(
        a=[(0.56, 0.12), (0.6, 0.27), (0.65, 0.36), (0.72, 0.42), (0.85, 0.44), (1.1, 0.42), (1.4, 0.41), (1.7, 0.42), (1.9, 0.42)],
        front=[(0.56, 0.02), (0.65, 0.12), (0.85, 0.2), (1.1, 0.24), (1.5, 0.26), (1.9, 0.24)],
        back=[(0.56, -0.12), (0.65, -0.18), (0.85, -0.22), (1.2, -0.22), (1.9, -0.2)]),
    torso_y=(0.56, 1.9),
    neck=dict(a=[(0.2, 0.11), (0.75, 0.12)], front=[(0.2, 0.06), (0.75, 0.08)], back=[(0.2, -0.13), (0.75, -0.14)]),
    neck_y=(0.3, 0.75),
    arm=dict(a=[(0.72, 0.06), (0.78, 0.1), (1.3, 0.095), (1.9, 0.09)],
             front=[(0.72, 0.05), (0.82, 0.09), (1.9, 0.09)], back=[(0.72, -0.06), (0.82, -0.1), (1.9, -0.09)]),
    arm_x=0.4, arm_y=(0.72, 1.9),
    cloth='#2c4a72', tex='knit', tex_amount=0.12, shade='#141a30', ribs=0.12,
    neckline=(0.7, 0.6, 0.04, '#24406a', 0.2),
    inside=tim_inside, arm_inside=tim_arm_inside,
)


# ------------------------------------------------------------------ Вера, 40
def vera_hair(h, d, P, ex):
    """Dark hair pulled back tight into a bun; two strands have escaped at the temples."""
    def line(phi):
        a = abs(phi)
        return -0.3 + 0.18 * min(1.0, a / 1.1) ** 2 + 0.3 * max(0.0, a - 1.1)
    locks = []
    # combed back from the hairline to the bun: smooth wide locks hugging the skull
    for k in range(9):
        ph = -1.6 + 3.2 * k / 8
        y0 = line(ph) + 0.01
        p = H.surf_path(h, [(ph, y0), (ph * 1.25 + (0.6 if ph > 0 else -0.6), -0.4), (math.pi * (0.95 if ph >= 0 else -0.95), -0.33)],
                        out=(0.012, 0.02), k=1.02)
        locks.append(H.Lock(p, 0.2, 0.08, taper=1.0, root=0.9, strands=4, grooves=1, sheen=(0.1, 0.35), z_bias=0.05))
    # escaped strands by the temples
    extra_front = []
    for side in (-1, 1):
        p = H.surf_path(h, [(side * 1.0, -0.12), (side * 1.12, 0.05)], out=0.03, k=1.02)
        p += H.fall(p[-1], 0.22, n=4, side=side, out_x=0.01, wave=0.015, waves=1.2)
        locks.append(H.Lock(p, 0.035, 0.0, taper=1.0, root=1.0, strands=1, grooves=0, z_bias=0.2))
    z, bun = props.bun(h, d, P, P['hair_col'], y=-0.28, phi=math.pi, r=0.17)
    out = dict(col=P['hair_col'], locks=locks, cap=(line, 0.2, 1.02))
    if z < 0:
        out['extra_back'] = [bun]
    else:
        out['extra_front'] = [bun]
    return out


def vera_over(h, d, P, ex):
    return props.glasses(h, d, P, 'rect', rw=0.1, rh=0.06, out=0.08, col='#2a1a22', lw=0.014, y_off=0.01)


VERA = dict(
    name='vera',
    shape=dict(
        a=[(-0.5, 0.02), (-0.46, 0.19), (-0.38, 0.29), (-0.25, 0.335), (-0.1, 0.34), (0.0, 0.33), (0.1, 0.315),
           (0.2, 0.285), (0.3, 0.24), (0.4, 0.17), (0.46, 0.1), (0.5, 0.04)],
        front=[(-0.5, -0.02), (-0.46, 0.19), (-0.38, 0.32), (-0.25, 0.39), (-0.12, 0.41), (0.0, 0.4), (0.1, 0.39),
               (0.2, 0.37), (0.3, 0.35), (0.4, 0.32), (0.46, 0.28), (0.5, 0.2)],
        back=[(-0.5, -0.02), (-0.46, -0.23), (-0.38, -0.37), (-0.25, -0.45), (-0.1, -0.46), (0.0, -0.43), (0.1, -0.35),
              (0.2, -0.22), (0.3, -0.08), (0.4, 0.04), (0.46, 0.1), (0.5, 0.13)],
        bumps=[(0.92, 0.08, 0.07, 0.3, 0.07), (0.0, 0.46, 0.04, 0.3, 0.04)]),
    skin='#ecc2a6', skin_shade='#9a5a6a', shade='#3a2440', blush=0.18, blush_col='#c86070', skin_tex=0.05,
    eye_phi=0.42, eye_y=0.09, eye_r=0.074, eye_w=0.088, eye_open=0.72, eye_tilt=0.012, iris_r=0.048, iris='#4a3a2a',
    lash='#1a1014', lash_w=0.014, wing=1.6, socket_a=0.45, bags=1, lid_top=0.72, lid_bot=0.4,
    lid_paint='#7a5a7a', lid_paint_a=0.35,
    brow_gap=0.075, brow_w=0.08, brow_th=0.016, brow_col='#2a1a18', brow_arch=0.018,
    nose_root=0.07, nose_tip=0.27, nose_len=0.075, nose_w=0.032, nose_fade=0.35,
    mouth_y=0.37, mouth_w=0.07, lip='#9a4a52', upper_lip=0.007, lower_lip=0.012,
    ear_phi=1.5, ear_y=0.14, ear_w=0.07, ear_h=0.15, ear_out=15,
    hair=vera_hair, hair_col='#3a2622', hair_shade='#0a0404',
    over_all=vera_over,
    wrinkles=[(0.3, 0.27, [(0.0, -0.05), (0.02, 0.0), (0.04, 0.06)], 0.005),
              (-0.3, 0.27, [(0.0, -0.05), (-0.02, 0.0), (-0.04, 0.06)], 0.005),
              (0.0, 0.0, [(-0.02, -0.03), (-0.015, 0.02)], 0.004)],
)


def vera_inside(d, T, P, B, S, o):
    """A dark cardigan open over a high-collared blouse."""
    blouse = '#c9cfd6'
    strip = front_patch(T, [(-0.13, 0.58), (-0.1, 0.9), (-0.08, 1.4), (-0.07, 2.2), (0.07, 2.2), (0.08, 1.4), (0.1, 0.9), (0.13, 0.58)])
    return f'<path d="{pts(strip)}" fill="{blouse}"/>'


def vera_details(d, T, N, P, B, S):
    res = []
    for side in (-1, 1):
        edge = front_patch(T, [(side * 0.13, 0.6), (side * 0.1, 0.9), (side * 0.08, 1.4), (side * 0.07, 2.2)], 0.0)
        res.append(d.groove(pts(edge, close=False), '#4a2a3a', S * 0.014, soft=1.2, depth=-5))
    for k in range(4):
        p = T.P(tx(T, 0.0, 0.95 + 0.22 * k, 0.012))
        res.append(d.bump(f'M{f(p[0]-S*0.012)} {f(p[1])} a{f(S*0.012)} {f(S*0.012)} 0 1 0 {f(S*0.024)} 0 a{f(S*0.012)} {f(S*0.012)} 0 1 0 {f(-S*0.024)} 0Z',
                          '#e8e4dc', soft=1, height=2.5, spec=0.7, shine=40))
    return res


def vera_collar(d, T, N, P, B, S):
    """The blouse's stand collar with a small brooch."""
    res = []
    p = N.P(N.surf(0, 0.68, 0.01))
    res.append(d.bump(f'M{f(p[0]-S*0.022)} {f(p[1])} a{f(S*0.022)} {f(S*0.026)} 0 1 0 {f(S*0.044)} 0 a{f(S*0.022)} {f(S*0.026)} 0 1 0 {f(-S*0.044)} 0Z',
                      '#8a2a3a', soft=1.5, height=4, spec=0.8, shine=50))
    return res


VERA_BODY = dict(
    torso=dict(
        a=[(0.6, 0.11), (0.65, 0.3), (0.71, 0.43), (0.8, 0.5), (0.95, 0.52), (1.2, 0.46), (1.5, 0.4), (1.8, 0.37), (2.2, 0.4)],
        front=[(0.6, 0.02), (0.7, 0.12), (0.85, 0.18), (1.05, 0.23), (1.2, 0.24), (1.4, 0.2), (1.8, 0.16), (2.2, 0.19)],
        back=[(0.6, -0.12), (0.7, -0.18), (0.85, -0.21), (1.05, -0.22), (1.4, -0.19), (1.8, -0.15), (2.2, -0.19)]),
    torso_y=(0.6, 2.2),
    neck=dict(a=[(0.2, 0.095), (0.85, 0.105)], front=[(0.2, 0.05), (0.85, 0.07)], back=[(0.2, -0.12), (0.85, -0.12)]),
    neck_y=(0.25, 0.85),
    collar=dict(a=[(0.48, 0.12), (0.52, 0.125), (0.66, 0.13), (0.7, 0.135)], front=[(0.48, 0.07), (0.7, 0.09)],
                back=[(0.48, -0.14), (0.7, -0.15)]),
    collar_y=(0.48, 0.7), collar_col='#c9cfd6',
    arm=dict(a=[(0.8, 0.06), (0.86, 0.105), (1.4, 0.1), (2.2, 0.085)],
             front=[(0.8, 0.05), (0.9, 0.095), (2.2, 0.085)], back=[(0.8, -0.06), (0.9, -0.11), (2.2, -0.085)]),
    arm_x=0.45, arm_y=(0.8, 2.2),
    cloth='#4a2c40', tex='knit', tex_amount=0.15, shade='#140a14', ribs=0.07,
    inside=vera_inside, details=vera_details, collar_extra=vera_collar,
)
