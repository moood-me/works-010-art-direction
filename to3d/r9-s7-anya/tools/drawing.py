"""The drawing as numbers. С7's Аня is itself built from 3D forms (styles/s7-ghibli/tools: head rings with a middle
profile, a torso loft, a skirt loft, tubes along a posed skeleton, hair as a shell plus locks along Bézier curves),
so the 3D here takes those very forms: the drawing's centimetres, its 'stand' pose (the turnaround's).

Drawing model space: centimetres, y up, the figure faces +z, its left +x, the floor at y=0. 3D here: metres, the same
axes (1 cm = 0.01 m). The drawing's views: View(yaw, pitch=4°, s px/cm); yaw a ↔ a camera at (−sin a, ·, cos a)."""
import os, sys
import numpy as np

S7 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'styles', 's7-ghibli', 'tools')
sys.path.append(S7)
import anya  # noqa: E402
from body import Figure, Loft  # noqa: E402
from head import Expr  # noqa: E402
import svgdoc  # noqa: E402

CM = 0.01
F = Figure(anya.B, anya.POSES['stand'])
J = F.J                                  # the stand pose's joints (cm)
HEAD = anya.head()
HEAD.place(J['head'], anya.B['head_h'])  # head-local units → model cm: L * k + c (k = 12 cm)
HAIR = anya.hair(HEAD)
HK = HEAD.k
HC = HEAD.c


def rgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def shade(h, k=1.0):
    return rgb(svgdoc.shade(h, k))


INK = svgdoc.INK
COL = dict(skin=anya.SKIN, hair=anya.HAIR, iris=anya.IRIS, top=anya.SPEC['top']['c'], over=anya.SPEC['over']['c'],
           skirt=anya.SPEC['bottom']['c'], shoe=anya.SPEC['shoes']['c'])


def head_to_model(L):
    """head-local (x, y, z) → model metres."""
    return (np.asarray(L, float).reshape(-1, 3) * HK + HC) * CM


def model_to_head(P):
    return (np.asarray(P, float).reshape(-1, 3) / CM - HC) / HK
