"""The drawing's own 3D shapes (styles/s1-pixar/tools: cast.tim_person, pix.Head): Тим's head surface, his eye
openings, limbs and garments, in the drawing's person units (x his left = screen right in the front view, y down,
z toward the viewer; the floor at y 388). These are the targets every base is fitted to."""
import sys, math
import numpy as np
from common import STYLE
sys.path.insert(0, f'{STYLE}/tools')
import cast, pix, face  # noqa: E402

P = cast.tim_person()
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


def eye_outline(side, ex=None, n=40):
    """the drawn eye opening (upper lid line + lower line) in front coords of the head, as 3D points on its surface"""
    ex = ex or face.expr()
    hd = head()
    up, lo = face.eye_shape(C, ex, side, ex)[:2] if False else _eye(side, ex)
    return [np.array([hd.surf(x, y) for x, y in L]) for L in (up, lo)]


def _eye(side, ex):
    r = face.eye_shape(C, ex, side, ex)
    return r[0], r[1]
