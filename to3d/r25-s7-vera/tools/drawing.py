"""The drawing as numbers. С7's characters are themselves built from 3D forms (styles/s7-ghibli/tools: head rings with
a middle profile, a torso loft, tubes along a posed skeleton, hair as a shell plus locks along Bézier curves), so the
3D here takes those very forms: the drawing's centimetres, its 'stand' pose (the turnaround's).

Drawing model space: centimetres, y up, the figure faces +z, its left +x, the floor at y=0. 3D here: metres, the same
axes (1 cm = 0.01 m). The drawing's views: View(yaw, pitch=4°, s px/cm); yaw a ↔ a camera at (−sin a, ·, cos a)."""
import os, sys, importlib
import numpy as np
import config

S7 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'styles', 's7-ghibli', 'tools')
sys.path.append(S7)
who = importlib.import_module(config.WHO)  # noqa: E402
from body import Figure, Loft  # noqa: E402
from head import Expr  # noqa: E402
import svgdoc  # noqa: E402

CM = 0.01
B, SPEC, FACE, HAIRDEF = who.B, who.SPEC, who.FACE, who.HAIRDEF
POSE = who.POSES['stand']
F = Figure(B, POSE)
J = F.J                                  # the stand pose's joints (cm)
HEAD = who.head()
HEAD.place(J['head'], B['head_h'], *POSE.get('head_rot', (0, 0, 0)))  # head-local → model cm: (L k) Rᵀ + c
HAIR = who.hair(HEAD)
HK, HC, HR = HEAD.k, HEAD.c, HEAD.R
LEAN = POSE.get('lean', 0.0)


def rgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def shade(h, k=1.0):
    return rgb(svgdoc.shade(h, k))


INK = svgdoc.INK
COL = dict(skin=who.SKIN, hair=who.HAIR, iris=who.IRIS)


def head_to_model(L):
    """head-local (x, y, z) → model metres."""
    return ((np.asarray(L, float).reshape(-1, 3) * HK) @ HR.T + HC) * CM


def head_dir(N):
    """head-local directions → model."""
    return np.asarray(N, float).reshape(-1, 3) @ HR.T


def model_to_head(P):
    return ((np.asarray(P, float).reshape(-1, 3) / CM - HC) @ HR) / HK
