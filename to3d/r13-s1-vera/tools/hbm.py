"""The Human Base Meshes stylised head (CC0) and its eyes, in the drawing's head units with y UP: the crown at +50,
the chin's underside at −50, x his left, z forward (the drawing's head is 100 units crown to chin)."""
import numpy as np
from mesh import polys_of, triangulate
from common import CACHE

CROWN, CHIN, MIDX, ZC = 0.888, 0.572, 2.083, 0.03
S = 100 / (CROWN - CHIN)


def units(v):
    V = np.c_[v[:, 0] - MIDX, v[:, 2], -v[:, 1]]
    return np.c_[V[:, 0] * S, (V[:, 1] - CROWN) * S + 50, (V[:, 2] - ZC) * S - 4]


def load():
    d = np.load(f'{CACHE}/hbm.npz')
    out = {}
    for k in ('head', 'eyeL', 'eyeR', 'jaw'):
        P = polys_of(d[k + '_fs'], d[k + '_f'])
        out[k] = (units(d[k + '_v']), triangulate(P), P)
    return out
