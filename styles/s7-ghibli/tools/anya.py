"""Аня, about 20 — warm, trusting, dreamy. Long chestnut hair with a soft clumpy fringe, a round soft face, big calm
eyes; a cream blouse, a moss-green cardigan, a long rust skirt."""
from head import Head, Expr
from hair import Hair

SKIN = '#f6d6bb'
HAIR = '#7a4a30'
IRIS = '#4a2f24'

FACE = dict(
    a=[(1.0, 0.0), (0.96, 0.30), (0.8, 0.58), (0.5, 0.74), (0.2, 0.77), (0.0, 0.76), (-0.2, 0.73), (-0.4, 0.67),
       (-0.6, 0.57), (-0.75, 0.45), (-0.88, 0.30), (-0.97, 0.14), (-1.0, 0.0)],
    zf=[(1.0, 0.05), (0.8, 0.46), (0.5, 0.68), (0.2, 0.72), (0.0, 0.66), (-0.2, 0.66), (-0.5, 0.62), (-0.7, 0.56),
        (-0.9, 0.46), (-1.0, 0.36)],
    zb=[(1.0, -0.05), (0.8, -0.72), (0.5, -0.96), (0.2, -0.96), (0.0, -0.86), (-0.2, -0.66), (-0.4, -0.36),
        (-0.6, -0.06), (-0.8, 0.06), (-1.0, 0.18)],
    prof=[(0.3, 0.0), (0.05, 0.0), (-0.08, 0.03), (-0.2, 0.07), (-0.31, 0.15), (-0.37, 0.06), (-0.43, 0.02),
          (-0.52, 0.03), (-0.62, 0.0), (-0.78, 0.02), (-0.92, 0.0)],
    sigma=[(0.2, 0.10), (-0.3, 0.07), (-0.5, 0.16), (-0.8, 0.22)],
    eye_x=0.32, eye_y=-0.07, eye_w=0.30, eye_h=0.22, iris_w=0.098, iris_h=0.125, lashes=2, flick=1.0, lid_w=1.5,
    brow_y=0.20, brow_w=0.28, brow_th=1.2, nose_y=-0.32, nose='hook', nose_len=0.10, mouth_y=-0.58, mouth_w=0.10,
    lower_lip=0.04, ear=(-0.04, -0.38), blush=0.35,
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
