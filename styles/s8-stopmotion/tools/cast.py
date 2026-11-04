"""The cast: four puppets. Each one is a dict P of head shape, features, colours and a hair function.
To add a character, copy one of these, change the tables and numbers, write its hair and its body (body.py)."""
import math
from sculpt import mix, pts, poly, f
import hair as H

# ------------------------------------------------------------------ expressions (shared)
EXPR = {
    'calm':     {'smile': 0.12},
    'dream':    {'gaze': (0.12, -0.2), 'open': 0.86, 'smile': 0.3, 'brow_in': 0.012, 'brow_out': 0.004},
    'joy':      {'smile': 1.0, 'mopen': 0.5, 'lid_lo': 0.5, 'open': 0.8, 'brow_out': 0.012, 'brow_in': 0.02, 'wide': 1.25},
    'surprise': {'open': 1.4, 'lid_up': 0.3, 'brow_in': 0.05, 'brow_out': 0.045, 'mopen': 0.7, 'wide': 0.7,
                 'teeth': False, 'pupil': 0.28},
    'sad':      {'open': 0.75, 'brow_in': 0.05, 'brow_out': -0.015, 'smile': -0.8, 'gaze': (0.0, 0.3), 'lid_up': -0.15},
    'anger':    {'open': 0.78, 'brow_in': -0.055, 'brow_out': 0.015, 'smile': -0.6, 'mopen': 0.38, 'lower_teeth': True,
                 'lid_up': -0.3, 'wide': 1.1},
    'grin':     {'smile': 0.75, 'skew': 0.35, 'mopen': 0.25, 'lid_lo': 0.3, 'brow_in': 0.005, 'brow_out': 0.02},
    'stern':    {'smile': -0.25, 'open': 0.85, 'lid_up': -0.12, 'brow_in': -0.015},
    'grumpy':   {'smile': -0.45, 'open': 0.8, 'lid_up': -0.15, 'brow_in': -0.025, 'gaze': (0.0, 0.1)},
    'tired':    {'smile': -0.1, 'open': 0.78, 'lid_up': -0.2, 'brow_in': 0.012, 'brow_out': -0.006},
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
    skin='#f0cbb2', skin_shade='#b0707a', shade='#6a3038', blush=0.34, freckles=16, skin_tex=0.05,
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
    """Bald dome; fluffy white tufts over the ears and round the back, sticking out and curling up."""
    locks = []
    for side in (-1, 1):
        for k in range(8):
            phi0 = side * (1.0 + 0.2 * k)
            y0 = -0.21 + 0.025 * k + 0.02 * (k % 2)
            p = H.surf_path(h, [(phi0, y0), (phi0 + side * 0.08, y0 + 0.1)], out=(0.0, 0.03), k=1.0)
            p += H.fall(p[-1], 0.04, n=3, side=side, out_x=0.05 - 0.004 * k + 0.02 * (k % 2), back_z=-0.02, flick=0.03)
            p += [(p[-1][0] + side * 0.035, p[-1][1] - 0.05 - 0.02 * (k % 2), p[-1][2])]
            locks.append(H.Lock(p, 0.1, 0.0, taper=0.8, root=0.7, strands=3, z_bias=0.0, sheen=(0.3, 0.7)))
    for k, ph in enumerate((2.45, 2.8, -2.8, -2.45, 3.14)):
        p = H.surf_path(h, [(ph, -0.17), (ph, 0.1)], out=(0.0, 0.025), k=1.0)
        locks.append(H.Lock(p, 0.26, 0.05, taper=1.0, root=0.7, strands=5, z_bias=-0.3))
    return dict(col=P['hair_col'], locks=locks, cap=None)


def savely_under_nose(h, d, P, ex):
    return props.moustache(h, d, P, '#e4ded4', w=0.2, droop=0.08, thick=0.1, ex=ex)


def savely_over(h, d, P, ex):
    return props.glasses(h, d, P, 'half', rw=0.075, rh=0.05, out=0.1, col='#b08a4a', lw=0.008, y_off=0.075)


SAVELY = dict(
    name='savely',
    shape=dict(
        a=[(-0.5, 0.03), (-0.46, 0.18), (-0.38, 0.27), (-0.25, 0.32), (-0.1, 0.345), (0.0, 0.355), (0.1, 0.37),
           (0.2, 0.38), (0.3, 0.37), (0.38, 0.33), (0.45, 0.25), (0.5, 0.13)],
        front=[(-0.5, -0.02), (-0.46, 0.2), (-0.38, 0.32), (-0.25, 0.39), (-0.12, 0.41), (0.0, 0.39), (0.1, 0.38),
               (0.2, 0.38), (0.3, 0.37), (0.4, 0.34), (0.46, 0.3), (0.5, 0.22)],
        back=[(-0.5, -0.02), (-0.46, -0.24), (-0.38, -0.37), (-0.25, -0.43), (-0.1, -0.44), (0.0, -0.42), (0.1, -0.35),
              (0.2, -0.24), (0.3, -0.12), (0.4, -0.02), (0.46, 0.05), (0.5, 0.1)],
        bumps=[(1.05, 0.3, 0.06, 0.45, 0.1), (0.0, 0.45, 0.03, 0.4, 0.05), (0.38, -0.04, 0.05, 0.35, 0.05)]),
    skin='#dcaa90', skin_shade='#9a5a50', shade='#5a2a34', warm='#c84a3a', blush=0.32, blush_col='#d0585a', skin_tex=0.08,
    eye_phi=0.4, eye_y=0.04, eye_r=0.07, eye_w=0.078, eye_open=0.72, eye_tilt=-0.01, iris_r=0.05, iris='#4a6a8a',
    lash='#3a2420', lash_w=0.011, wing=0.4, socket_a=0.4, bags=2, lid_top=0.72, lid_bot=0.42,
    brow_gap=0.085, brow_w=0.1, brow_th=0.06, brow_col='#ece6dc', brow_arch=0.0, brow_taper=0.3, brow_bushy=True, brow_droop=0.03,
    nose_root=0.06, nose_tip=0.235, nose_len=0.12, nose_w=0.085, nose_tint='#d0504a', nose_fade=0.45,
    mouth_y=0.37, mouth_w=0.08, lip='#b05a58', upper_lip=0.006, lower_lip=0.016,
    ear_phi=1.48, ear_y=0.12, ear_w=0.11, ear_h=0.21, ear_out=30, ear_tint='#d06060',
    hair=savely_hair, hair_col='#e4ded4', hair_shade='#6a5a5a', hair_split=-0.15,
    under_nose=savely_under_nose, over_all=savely_over,
    wrinkles=[(0.0, -0.22, [(-0.16, 0.0), (0.0, -0.012), (0.16, 0.0)], 0.007),
              (0.0, -0.27, [(-0.13, 0.0), (0.0, -0.01), (0.13, 0.0)], 0.006),
              (0.0, -0.17, [(-0.12, 0.0), (0.0, -0.008), (0.12, 0.0)], 0.006),
              (0.72, 0.05, [(0.0, -0.035), (0.035, 0.0), (0.0, 0.035)], 0.005),
              (-0.72, 0.05, [(0.0, -0.035), (-0.035, 0.0), (0.0, 0.035)], 0.005)],
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
        a=[(0.55, 0.16), (0.6, 0.36), (0.68, 0.48), (0.8, 0.55), (0.95, 0.58), (1.2, 0.61), (1.5, 0.63), (1.8, 0.6), (2.0, 0.56)],
        front=[(0.58, 0.04), (0.7, 0.15), (0.9, 0.24), (1.2, 0.36), (1.45, 0.42), (1.7, 0.38), (2.0, 0.3)],
        back=[(0.58, -0.16), (0.7, -0.25), (0.9, -0.3), (1.2, -0.28), (1.5, -0.25), (2.0, -0.22)]),
    torso_y=(0.55, 2.0),
    neck=dict(a=[(0.2, 0.17), (0.7, 0.19)], front=[(0.2, 0.1), (0.7, 0.12)], back=[(0.2, -0.16), (0.7, -0.18)]),
    neck_y=(0.3, 0.7),
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
        if a < 1.2:
            return -0.2 + 0.12 * (a / 1.2) ** 2
        if a < 1.75:
            return -0.08 - 0.04 * math.sin((a - 1.2) / 0.55 * math.pi)
        return -0.08 + 0.3 * min(1.0, (a - 1.75) / 1.0)
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
    skin='#eec4a4', skin_shade='#b0686a', shade='#6a3038', blush=0.45, blush_col='#e85a5a', freckles=26, skin_tex=0.05,
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
    # combed back: smooth wide bands from the hairline up over the skull
    for k in range(11):
        ph = -1.5 + 3.0 * k / 10
        y0 = line(ph) + 0.005
        p = H.surf_path(h, [(ph, y0), (ph * 0.8, (y0 - 0.44) / 2 - 0.02), (ph * 0.55, -0.45)], out=(0.008, 0.012), k=1.02)
        locks.append(H.Lock(p, 0.17, 0.12, taper=1.0, root=1.0, strands=3, grooves=0, sheen=(0.3, 0.6), z_bias=0.1))
    # escaped strands by the temples
    extra_front = []
    for side in (-1, 1):
        p = H.surf_path(h, [(side * 1.12, -0.1), (side * 1.25, 0.04)], out=0.03, k=1.02)
        p += H.fall(p[-1], 0.12, n=4, side=side, out_x=0.02, wave=0.012, waves=1.0)
        locks.append(H.Lock(p, 0.03, 0.0, taper=1.0, root=1.0, strands=0, grooves=0, z_bias=0.2))
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
        a=[(-0.5, 0.02), (-0.46, 0.18), (-0.38, 0.27), (-0.25, 0.31), (-0.1, 0.315), (0.0, 0.305), (0.1, 0.29),
           (0.2, 0.262), (0.3, 0.22), (0.4, 0.15), (0.46, 0.09), (0.5, 0.035)],
        front=[(-0.5, -0.02), (-0.46, 0.19), (-0.38, 0.32), (-0.25, 0.39), (-0.12, 0.41), (0.0, 0.4), (0.1, 0.39),
               (0.2, 0.37), (0.3, 0.35), (0.4, 0.32), (0.46, 0.28), (0.5, 0.2)],
        back=[(-0.5, -0.02), (-0.46, -0.23), (-0.38, -0.37), (-0.25, -0.45), (-0.1, -0.46), (0.0, -0.43), (0.1, -0.35),
              (0.2, -0.22), (0.3, -0.08), (0.4, 0.04), (0.46, 0.1), (0.5, 0.13)],
        bumps=[(0.92, 0.08, 0.07, 0.3, 0.07), (0.0, 0.46, 0.04, 0.3, 0.04)]),
    skin='#ead0be', skin_shade='#9a6a6a', shade='#5a3038', shade_depth=0.6, blush=0.18, blush_col='#c86070', skin_tex=0.05,
    eye_phi=0.43, eye_y=0.07, eye_r=0.07, eye_w=0.085, eye_open=0.66, eye_tilt=0.014, iris_r=0.046, iris='#3a4a3a',
    lash='#1a1014', lash_w=0.014, wing=1.6, socket_a=0.45, bags=1, lid_top=0.72, lid_bot=0.4,
    lid_paint='#7a5a7a', lid_paint_a=0.35,
    brow_gap=0.07, brow_w=0.085, brow_th=0.014, brow_col='#2a1a18', brow_arch=0.006,
    nose_root=0.05, nose_tip=0.27, nose_len=0.085, nose_w=0.03, nose_fade=0.3, nose_hook=0.15,
    mouth_y=0.37, mouth_w=0.068, lip='#9a4a52', upper_lip=0.006, lower_lip=0.011,
    ear_phi=1.5, ear_y=0.14, ear_w=0.07, ear_h=0.15, ear_out=15,
    hair=vera_hair, hair_col='#3a2622', hair_shade='#0a0404',
    over_all=vera_over,
    wrinkles=[(0.0, 0.0, [(-0.018, -0.025), (-0.014, 0.015)], 0.004)],
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


# ------------------------------------------------------------------ figures (full height, in head units)
def _flower(stem_from, col='#e8d8a0'):
    """A wild flower on a thin stem (a prop in Anya's hand)."""
    def prop(d, T, P, S):
        x, y, z = stem_from
        top = (x + 0.05, y - 0.55, z + 0.05)
        a, b = T.P(stem_from), T.P(top)
        s = d.bump(f'M{f(a[0])} {f(a[1])} Q{f(a[0]+S*0.02)} {f((a[1]+b[1])/2)} {f(b[0])} {f(b[1])}', '#5a7a3a', soft=1, height=2,
                   spec=0.2, stroke=True, sw=S * 0.012)
        petals = ''
        for k in range(7):
            ang = 2 * math.pi * k / 7
            px, py = b[0] + math.cos(ang) * S * 0.045, b[1] + math.sin(ang) * S * 0.035
            petals += f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="{f(S*0.035)}" ry="{f(S*0.02)}" transform="rotate({f(math.degrees(ang))} {f(px)} {f(py)})" fill="{col}"/>'
        s += f'<g filter="url(#{d.relief(1.5, 3, 0.3, 20)})">{petals}</g>'
        s += d.bump(f'M{f(b[0]-S*0.025)} {f(b[1])} a{f(S*0.025)} {f(S*0.025)} 0 1 0 {f(S*0.05)} 0 a{f(S*0.025)} {f(S*0.025)} 0 1 0 {f(-S*0.05)} 0Z',
                    '#d89a30', soft=1.5, height=3, spec=0.4)
        return (T.scr(top)[2] + 0.3, s)
    return prop


ANYA_FIG = dict(
    legs=lambda side: [dict(path=[(side * 0.17, 2.1, 0.0), (side * 0.16, 3.0, 0.03), (side * 0.15, 3.85, 0.0)], r0=0.1, r1=0.06,
                            col='#4a3448', tex='cloth', tex_amount=0.1, z=-0.3)],
    shoe=lambda side: dict(ankle=(side * 0.15, 3.86, 0.0), len=0.36, col='#7a3a24', h=0.11, w=0.1),
    skirts=[dict(table=dict(a=[(1.9, 0.38), (2.2, 0.47), (2.6, 0.57), (3.0, 0.64)], front=[(1.9, 0.2), (3.0, 0.42)],
                            back=[(1.9, -0.18), (3.0, -0.38)]), y=(1.92, 3.0), col='#2e5a5e', tex='cloth', tex_amount=0.2,
                 ribs=0.22, z=-0.1)],
    arms=lambda side: [dict(path=[(side * 0.48, 0.86, -0.02), (side * 0.6, 1.5, -0.04), (side * 0.48 if side < 0 else 0.3, 2.05, 0.12 if side > 0 else 0.0)],
                            r0=0.1, r1=0.075, col='#c8902e', tex='felt', tex_amount=0.12, ribs=True, z=0.05)],
    hand=lambda side: dict(wrist=(side * 0.48 if side < 0 else 0.3, 2.07, 0.12 if side > 0 else 0.0),
                           dir=(0.0, 1.0, 0.1), size=0.26, pose='relaxed' if side < 0 else 'hold'),
    props=[_flower((0.28, 2.2, 0.2))],
)

SAVELY_FIG = dict(
    torso=dict(SAVELY_BODY['torso'], a=SAVELY_BODY['torso']['a'] + [(2.2, 0.55)], front=SAVELY_BODY['torso']['front'] + [(2.2, 0.26)],
               back=SAVELY_BODY['torso']['back'] + [(2.2, -0.2)]),
    torso_y=(0.55, 2.2),
    legs=lambda side: [dict(path=[(side * 0.22, 2.05, 0.0), (side * 0.22, 2.7, 0.04), (side * 0.2, 3.25, 0.0)], r0=0.17, r1=0.14,
                            col='#4a4a52', tex='cloth', tex_amount=0.25, z=-0.3)],
    shoe=lambda side: dict(ankle=(side * 0.2, 3.27, 0.0), len=0.36, col='#3a2418', h=0.11, w=0.1),
    arms=lambda side: [dict(path=[(side * 0.52, 0.8, -0.02), (side * 0.66, 1.45, 0.0), (side * 0.3, 1.75, 0.38)] if side > 0 else
                            [(side * 0.52, 0.8, -0.02), (side * 0.7, 1.5, -0.04), (side * 0.6, 2.15, 0.0)],
                            r0=0.13, r1=0.11, col='#e2d6bc', tex='cloth', tex_amount=0.25, z=0.05)],
    hand=lambda side: dict(wrist=(0.28, 1.76, 0.4) if side > 0 else (-0.6, 2.17, 0.0), dir=(-0.4, 0.2, 0.6) if side > 0 else (0, 1, 0),
                           size=0.28, pose='hold' if side > 0 else 'relaxed', z=0.1),
)


def _watch(at):
    """A pocket watch held up: gold case, white face, two hands."""
    def prop(d, T, P, S):
        x, y = T.P(at)
        r = S * 0.07
        s = d.bump(f'M{f(x-r)} {f(y)} a{f(r)} {f(r)} 0 1 0 {f(2*r)} 0 a{f(r)} {f(r)} 0 1 0 {f(-2*r)} 0Z', '#d8a840', soft=2, height=5,
                   spec=0.9, shine=50)
        s += f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r*0.78)}" fill="#f4eee0"/>'
        for k in range(12):
            a = 2 * math.pi * k / 12
            s += f'<circle cx="{f(x+math.cos(a)*r*0.62)}" cy="{f(y+math.sin(a)*r*0.62)}" r="{f(r*0.05)}" fill="#3a2a20"/>'
        s += f'<path d="M{f(x)} {f(y)} L{f(x+r*0.4)} {f(y-r*0.25)} M{f(x)} {f(y)} L{f(x-r*0.1)} {f(y-r*0.55)}" stroke="#2a1a14" stroke-width="{f(r*0.07)}" stroke-linecap="round"/>'
        s += d.bump(f'M{f(x-r*0.15)} {f(y-r*1.05)} h{f(r*0.3)} v{f(-r*0.25)} h{f(-r*0.3)}Z', '#d8a840', soft=1, height=2, spec=0.8)
        s += f'<path d="M{f(x)} {f(y-r*1.3)} q{f(-r*1.5)} {f(-r*0.5)} {f(-r*2.6)} {f(r*0.8)}" fill="none" stroke="#d8a840" stroke-width="{f(S*0.008)}" stroke-dasharray="{f(S*0.008)} {f(S*0.004)}"/>'
        return (T.scr(at)[2] + 0.5, s)
    return prop


SAVELY_FIG['props'] = [_watch((0.2, 1.62, 0.5))]

TIM_FIG = dict(
    torso=dict(TIM_BODY['torso']),
    torso_y=(0.56, 1.75),
    legs=lambda side: [dict(path=[(side * 0.15, 1.65, 0.0), (side * 0.17, 2.0, 0.02)], r0=0.15, r1=0.14, col='#6a5a3a', tex='cloth',
                            tex_amount=0.3, z=-0.25),
                       dict(path=[(side * 0.16, 1.95, 0.02), (side * 0.18 + (0.05 if side > 0 else 0), 2.35, 0.03), (side * 0.17 + (0.08 if side > 0 else 0), 2.72, 0.0)],
                            r0=0.075, r1=0.06, col='#eec4a4', z=-0.3),
                       dict(path=[(side * 0.17 + (0.08 if side > 0 else 0), 2.5, 0.0), (side * 0.17 + (0.08 if side > 0 else 0), 2.72, 0.0)],
                            r0=0.07, r1=0.068, col='#e8e0d0', tex='knit', tex_amount=0.15, z=-0.29, ribs=True)],
    shoe=lambda side: dict(ankle=(side * 0.17 + (0.08 if side > 0 else 0), 2.74, 0.0), len=0.34, col='#c83a2a', h=0.11, w=0.1, toe_up=0.02),
    arms=lambda side: [dict(path=[(side * 0.4, 0.75, -0.02), (side * 0.56, 1.25, 0.0), (side * 0.44, 1.7, 0.1)] if side < 0 else
                            [(side * 0.4, 0.75, -0.02), (side * 0.7, 1.1, 0.05), (side * 0.62, 0.62, 0.15)],
                            r0=0.09, r1=0.08, col='#2c4a72', tex='knit', tex_amount=0.12, stripes='#f0e6d2', z=0.05)],
    hand=lambda side: dict(wrist=(side * 0.44, 1.72, 0.1), dir=(0, 1, 0), size=0.22, pose='fist') if side < 0 else
    dict(wrist=(0.62, 0.58, 0.15), dir=(0.1, -1.0, 0.1), size=0.22, pose='open', z=0.05),
)

VERA_FIG = dict(
    torso=dict(VERA_BODY['torso'], a=VERA_BODY['torso']['a'] + [(2.5, 0.44)], front=VERA_BODY['torso']['front'] + [(2.5, 0.21)],
               back=VERA_BODY['torso']['back'] + [(2.5, -0.21)]),
    torso_y=(0.6, 2.5),
    legs=lambda side: [dict(path=[(side * 0.14, 2.5, 0.0), (side * 0.13, 3.5, 0.02), (side * 0.12, 4.35, 0.0)], r0=0.085, r1=0.055,
                            col='#2a2430', tex='cloth', tex_amount=0.1, z=-0.3)],
    shoe=lambda side: dict(ankle=(side * 0.12, 4.36, 0.0), len=0.36, col='#2a1c22', h=0.1, w=0.085),
    skirts=[dict(table=dict(a=[(2.15, 0.36), (2.5, 0.42), (3.0, 0.44), (3.45, 0.44)], front=[(2.15, 0.2), (3.45, 0.24)],
                            back=[(2.15, -0.2), (3.45, -0.24)]), y=(2.17, 3.45), col='#3a3a4a', tex='cloth', tex_amount=0.25,
                 ribs=0.3, z=-0.1)],
    arms=lambda side: [dict(path=[(side * 0.47, 0.86, -0.02), (side * 0.58, 1.55, 0.0), (side * 0.2 if side > 0 else -0.05, 1.55, 0.36)],
                            r0=0.095, r1=0.075, col='#4a2c40', tex='knit', tex_amount=0.15, ribs=True, z=0.1)],
    hand=lambda side: dict(wrist=(0.2, 1.55, 0.37) if side > 0 else (-0.05, 1.55, 0.37), dir=(-0.8, 0.2, 0.3) if side > 0 else (0.8, 0.2, 0.3),
                           size=0.25, pose='hold', z=0.2),
)


def _folder(at):
    """A thick folder of papers held against the chest."""
    def prop(d, T, P, S):
        x, y, z = at
        corners = [(x - 0.32, y - 0.38, z), (x + 0.22, y - 0.4, z + 0.04), (x + 0.24, y + 0.3, z + 0.04), (x - 0.3, y + 0.32, z)]
        pp = [T.P(c) for c in corners]
        s = d.shape(poly(pp), '#2e4a3a', S * 0.6, 'cloth', 0.2, shade='#0a1410', depth=0.5, sheen=0.25, reach=0.2)
        pages = [(p[0] + S * 0.02, p[1] - S * 0.02) for p in pp]
        s = d.shape(poly(pages), '#ece6d6', S * 0.6, 'cloth', 0.1, shade='#3a3020', depth=0.3, reach=0.2) + s
        return (T.scr(at)[2] + 0.05, s)
    return prop


VERA_FIG['props'] = [_folder((0.08, 1.45, 0.3))]
