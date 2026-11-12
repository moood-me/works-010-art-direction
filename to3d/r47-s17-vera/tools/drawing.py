"""Вера's drawing as data: the Bilibin drawing (styles/s17-bilibin/tools: parts.py, vera.py) builds her head as a
volume — cross-sections a(y), the face surface zs(x, y) with the nose and lips, the back bb(y) — and projects it.
Here the same numbers are sampled as a mesh, and the hairline, the knot, the ears are taken from the same code.
Units: the drawing's head units (eye line y = 0, y down, z toward the viewer, x to the figure's left; crown −112,
chin 96; the floor at FEET)."""
import os, sys, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S17 = os.path.normpath(os.path.join(HERE, '../../../styles/s17-bilibin/tools'))
sys.path.insert(0, S17)
import parts  # noqa: E402
import vera  # noqa: E402

P = vera.p
FEET = 1354.0            # figure(): ankles at 1320, the shoe 36 high
K = 0.00114              # metres per unit: she is 1.67 m


def head_point(y, th):
    """The head's surface at height y and angle th round it (0 the face's middle, pi/2 her left ear, pi the back)."""
    a = P.a(y)
    x = a * math.sin(th)
    if math.cos(th) >= 0:
        z = P.zs(x, y)
    else:
        kb = min(1.0, max(0.0, (P.jaw_y + 4 - y) / 18.0))       # under the jaw corner the back is the neck's
        z = -P.bb(y) * kb * abs(math.cos(th))
    return x, y, z


def thetas(n):
    """Angles round the head, denser at the face's middle (the nose is narrow)."""
    u = np.linspace(-1, 1, n, endpoint=False)
    return np.pi * (0.72 * u + 0.28 * u ** 3)


def head_grid(ny=120, nth=200):
    ys = np.linspace(P.crown + 0.5, P.chin - 0.5, ny)
    ths = thetas(nth)
    V = np.array([[head_point(y, t) for t in ths] for y in ys])       # (ny, nth, 3)
    return ys, ths, V


def hairline_y(th):
    """The lowest height the hair reaches at angle th: the drawing's hairline (vera.hl()) in front, the cap's side
    (y 20) and back (y 36) behind — parts.shell(grow=8, y_side=20, y_back=36)."""
    from scipy.interpolate import PchipInterpolator
    keys = [(0.0, -76.0), (math.asin(0.45), -71.0), (math.asin(0.86), -46.0), (math.asin(0.92) + 0.16, 10.0),
            (math.pi / 2 + 0.25, 20.0), (math.pi, 36.0)]
    f = PchipInterpolator([k[0] for k in keys], [k[1] for k in keys])
    return f(np.abs(th))


KNOT = np.array([0.0, 24.0, -P.bb(24) - 22.0])
