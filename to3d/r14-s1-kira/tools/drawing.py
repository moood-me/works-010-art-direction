"""The drawing's own 3D shapes (styles/s1-pixar/tools: the character's person(), pix.Head): the head surface, the eye
openings, limbs and garments, in the drawing's person units (x the left = screen right in the front view, y down,
z toward the viewer). These are the targets every base is fitted to."""
import sys, math
import numpy as np
from common import STYLE
import char
sys.path.insert(0, f'{STYLE}/tools')
import pix, face  # noqa: E402

P = char.person()
C = P['head']
HEAD_AT = np.array(P['head_at'], float)          # the head's centre (local y −50 crown … 50 chin)


def head():
    return pix.Head(C['w'], C['zf'], C['zb'], n=C.get('n', 2.3), bumps=C['bumps'])


def head_mesh(ny=101, nphi=96, bumps=True):
    """the drawn head as a closed grid mesh in head-local units (y down, z forward)"""
    hd = head()
    if not bumps: hd.bumps = ()
    ys = np.linspace(-50, 50, ny)
    V = []
    for y in ys:
        for j in range(nphi):
            phi = -math.pi + 2 * math.pi * j / nphi
            x, z = hd.section(y, phi)
            V.append((x, y, z))
    V = np.array(V); F = []
    for i in range(ny - 1):
        for j in range(nphi):
            a, b = i * nphi + j, i * nphi + (j + 1) % nphi
            F += [(a, b, a + nphi), (b, b + nphi, a + nphi)]
    return V, np.array(F)
