"""The cast: four puppets. Each one is a dict P of head shape, features, colours and a hair function.
To add a character, copy one of these, change the tables and numbers, write its hair and its body (body.py)."""
import math
from sculpt import mix
from puppet import shell_path, hang, hair_cap
from head import lock

# ------------------------------------------------------------------ expressions (shared)
EXPR = {
    'calm':     {},
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
    col = P['hair_col']
    lite = mix(col, '#ffcf9a', 0.18)
    dark = mix(col, '#2a0e08', 0.35)
    part = -0.38
    locks = []

    def line(phi):
        a = abs(phi)
        if a < 1.0:
            return -0.27 + 0.2 * (a / 1.0) ** 2
        return -0.07 + 0.35 * min(1, (a - 1.0) / 1.2)

    capsvg = hair_cap(h, d, P, 1.05, -0.5, line, col)
    # locks sweeping from the part to the side and falling to the shoulders
    specs = [
        # phi_end, y_end at the side, hang length, out, wave phase, width, colour, side(+1 = viewer right)
        (1.05, -0.12, 0.0, 0.0, 0.0, 0.11, col, 1, -0.30),
        (1.25, -0.02, 0.75, 0.06, 0.4, 0.12, lite, 1, -0.22),
        (1.45, 0.02, 0.85, 0.09, 1.2, 0.12, col, 1, -0.10),
        (1.75, 0.0, 0.9, 0.06, 2.0, 0.13, dark, 1, 0.0),
        (-0.95, -0.14, 0.0, 0.0, 0.0, 0.10, lite, -1, -0.32),
        (-1.2, -0.05, 0.8, 0.05, 0.8, 0.12, col, -1, -0.25),
        (-1.45, 0.0, 0.9, 0.08, 1.6, 0.12, lite, -1, -0.12),
        (-1.75, 0.02, 0.92, 0.06, 2.4, 0.13, dark, -1, 0.0),
    ]
    for (pe, ye, ln, ox, ph, w, c, side, ystart) in specs:
        p = shell_path(h, part + (0.05 if side > 0 else -0.05), -0.47, pe, ye, n=9, out=0.035, k=1.04, ease=1.6)
        if ln > 0:
            p += hang(p[-1], ln, n=9, out_x=ox, back_z=-0.05, wave=0.025, waves=1.2, phase=ph, side=side, curl_end=0.03)
        locks.append(lock(h, d, p, w, 0.0, c, taper=2.2))
    # a soft wave that frames the face on the viewer's left
    p = shell_path(h, part - 0.05, -0.46, -0.7, -0.2, n=7, out=0.045, k=1.05, ease=1.3)
    p += shell_path(h, -0.7, -0.2, -1.0, 0.05, n=4, out=0.06, k=1.05)[1:]
    p += hang(p[-1], 0.6, n=7, out_x=0.02, back_z=0.02, wave=0.02, waves=1.0, phase=0.5, side=-1, curl_end=-0.04)
    locks.append(lock(h, d, p, 0.10, 0.0, lite, taper=2.0))
    # fringe sweeping right
    p = shell_path(h, part + 0.02, -0.47, 0.55, -0.25, n=10, out=0.05, k=1.05, ease=0.8)
    p += shell_path(h, 0.55, -0.25, 1.0, -0.08, n=4, out=0.05, k=1.05)[1:]
    locks.append(lock(h, d, p, 0.13, 0.02, col, taper=1.5))
    p = shell_path(h, part + 0.08, -0.44, 0.75, -0.18, n=9, out=0.065, k=1.05, ease=0.9)
    locks.append(lock(h, d, p, 0.07, 0.0, lite, taper=1.3))
    # back mass hanging behind the shoulders
    back = []
    bpts = []
    for phi in [i / 20 * 2 * math.pi - math.pi for i in range(21)]:
        bpts.append(phi)
    for i, phb in enumerate((-2.2, -2.6, 2.6, 2.2, math.pi)):
        p = shell_path(h, part, -0.47, phb, 0.05, n=7, out=0.03, k=1.05)
        p += hang(p[-1], 0.95, n=8, out_x=0.05, back_z=0.0, wave=0.02, phase=i, side=1 if phb > 0 else -1)
        locks.append(lock(h, d, p, 0.2, 0.06, dark, taper=1.0))
    return {'back': back, 'cap': capsvg, 'locks': locks}


ANYA = dict(
    name='anya',
    shape=dict(
        a=[(-0.5, 0.02), (-0.46, 0.2), (-0.38, 0.3), (-0.25, 0.36), (-0.1, 0.372), (0.0, 0.362), (0.1, 0.335),
           (0.2, 0.285), (0.3, 0.222), (0.4, 0.148), (0.47, 0.08), (0.5, 0.03)],
        front=[(-0.5, -0.02), (-0.46, 0.2), (-0.38, 0.33), (-0.25, 0.4), (-0.12, 0.42), (0.0, 0.405), (0.1, 0.395),
               (0.2, 0.37), (0.3, 0.345), (0.4, 0.31), (0.47, 0.25), (0.5, 0.14)],
        back=[(-0.5, -0.02), (-0.46, -0.24), (-0.38, -0.38), (-0.25, -0.46), (-0.1, -0.47), (0.0, -0.44), (0.1, -0.36),
              (0.2, -0.22), (0.3, -0.1), (0.4, -0.02), (0.5, 0.02)]),
    skin='#f0c4a4', skin_shade='#b0606a', shade='#5a2a40', blush=0.38, freckles=16,
    eye_phi=0.43, eye_y=0.075, eye_r=0.078, eye_w=0.085, eye_open=1.0, eye_tilt=0.004, iris_r=0.05, iris='#5a7a4a',
    lash='#2a1612', lash_w=0.011, wing=1.2,
    brow_gap=0.095, brow_w=0.07, brow_th=0.016, brow_col='#7a3a22', brow_arch=0.014,
    nose_root=0.1, nose_tip=0.235, nose_len=0.055, nose_w=0.034, nose_up=0.02,
    mouth_y=0.335, mouth_w=0.068, lip='#cc6a6a', upper_lip=0.011, lower_lip=0.017,
    ear_phi=1.5, ear_y=0.12, ear_w=0.06, ear_h=0.15, ear_out=20,
    hair=anya_hair, hair_col='#9a4424', hair_shade='#2a0a06',
)
