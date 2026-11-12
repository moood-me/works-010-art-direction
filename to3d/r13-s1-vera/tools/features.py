"""The nose and the mouth moved where the drawing has them (lower on the face: the drawn nose tip at y 22.5, the mouth
at 36.5, a small chin), the nose made a smaller button, the ears made the drawing's size. Displacements are set on
handles (the nose, the lips with the mouth bag behind them, the ears' rims) and held at zero on the eyes (already
placed), the skull and the neck; everything between gets the biharmonic interpolation over the surface (libigl), so
the face stretches smoothly, without kinks."""
import numpy as np, igl
from quads import Quads
from eyefit import ring, OUTER, LINING

import char
from drawing import C
NOSE_S = char.NOSE_S
NOSE_TIP_Y = -C['bumps'][1][1]          # the drawn nose tip (the head's second bump), y up
MOUTH_Y = -C['mouth_y']
MOUTH_RINGS = [767, 770, 774, 1851, 1836, 1822, 798, 1798, 1812, 1813, 1815, 1816]
EAR_S = char.EAR_S


def place_features(V, T, P, mirror_ix, outer, ear_res, ear_band, V0):
    """V0: the base as it came (its rings are found on it)"""
    Q = Quads(P)
    tgt = {}
    held = set()
    for s in OUTER + LINING:
        L = ring(Q, V0, s); held |= set(L.tolist()) | set(mirror_ix[L].tolist())
    mouth = set()
    for s in MOUTH_RINGS:
        mouth |= set(ring(Q, V0, s).tolist())
    line = ring(Q, V0, 767)
    dy_m = MOUTH_Y - V[line, 1].mean()
    outer = outer & outer[mirror_ix]
    ear_res = np.minimum(ear_res, ear_res[mirror_ix]); ear_band = ear_band & ear_band[mirror_ix]
    inside = np.where(~outer & (V0[:, 1] < -12) & (V0[:, 1] > -45) & (np.abs(V0[:, 0]) < 14) & (V0[:, 2] > 0))[0]
    for i in set(mouth): tgt[i] = np.array([0, dy_m, 0.5])
    tip = np.argmax(np.where(np.abs(V[:, 0]) < 1, V[:, 2], -1e9))
    d = np.linalg.norm(V - V[tip], axis=1)
    nose = np.where(d < 11)[0]
    root = V[tip] + [0, 1, -11]
    nose_dy = NOSE_TIP_Y - (root[1] + (V[tip, 1] - root[1]) * NOSE_S)
    for i in nose: tgt[i] = (root + (V[i] - root) * NOSE_S + [0, nose_dy, char.NOSE_OUT]) - V[i]
    # the ears: their rims (ear_res > 1.2: standing out of the skull's smooth form, found on the base) scaled about
    # the ear's root; the skin round the root held
    from scipy.spatial import cKDTree
    for sgn in (1, -1):
        m = np.where((ear_res > 0.4) & (np.sign(V[:, 0]) == sgn))[0]
        rootm = np.where((np.abs(ear_res) < 0.25) & (np.sign(V[:, 0]) == sgn) & (ear_band))[0]
        dd, _ = cKDTree(V[m]).query(V[rootm]); rootm = rootm[(dd < 6) & (dd > 1.5)]
        c = V[rootm].mean(0)
        for i in m: tgt[i] = (c + (V[i] - c) * EAR_S) - V[i]
        for i in rootm: tgt[i] = np.zeros(3)
    hold = list(held) + list(np.where(V[:, 1] > 16)[0]) + list(np.where(V[:, 1] < -50)[0])
    hold += list(np.where((V[:, 2] < -10))[0])
    for i in hold:
        if i not in tgt: tgt[i] = np.zeros(3)
    b = np.array(sorted(tgt)); bc = np.array([tgt[i] for i in b])
    D = igl.harmonic(V, T, b, bc, 2)
    return V + D, dict(tip=int(tip), dy_mouth=float(dy_m))
