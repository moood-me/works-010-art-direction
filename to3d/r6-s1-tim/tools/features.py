"""The nose and the mouth moved where the drawing has them (lower on the face: the drawn nose tip at y 22.5, the mouth
at 36.5, a small chin), the nose made a smaller button, the ears made the drawing's size. Displacements are set on
handles (the nose, the lips with the mouth bag behind them, the ears' rims) and held at zero on the eyes (already
placed), the skull and the neck; everything between gets the biharmonic interpolation over the surface (libigl), so
the face stretches smoothly, without kinks."""
import numpy as np, igl
from quads import Quads
from eyefit import ring, OUTER, LINING

NOSE_DY, NOSE_S = -7.0, 0.8
MOUTH_Y = -36.5
MOUTH_RINGS = [767, 770, 774, 1851, 1836, 1822, 798, 1798, 1812, 1813, 1815, 1816]
EAR_S = 0.72


def place_features(V, T, P, mirror_ix, outer):
    Q = Quads(P)
    tgt = {}
    held = set()
    for s in OUTER + LINING:
        L = ring(Q, V, s); held |= set(L.tolist()) | set(mirror_ix[L].tolist())
    mouth = set()
    for s in MOUTH_RINGS:
        mouth |= set(ring(Q, V, s).tolist())
    line = ring(Q, V, 767)
    dy_m = MOUTH_Y - V[line, 1].mean()
    inside = np.where(~outer & (V[:, 1] < -12) & (V[:, 1] > -45) & (np.abs(V[:, 0]) < 20) & (V[:, 2] > 0))[0]
    for i in set(mouth) | set(inside.tolist()): tgt[i] = np.array([0, dy_m, 0.5])
    tip = np.argmax(np.where(np.abs(V[:, 0]) < 1, V[:, 2], -1e9))
    d = np.linalg.norm(V - V[tip], axis=1)
    nose = np.where((d < 8) & (V[:, 1] > V[tip, 1] - 7))[0]
    root = V[tip] + [0, 0, -9]
    for i in nose: tgt[i] = (root + (V[i] - root) * NOSE_S + [0, NOSE_DY, 0]) - V[i]
    # the ears: their outer part scaled about the root
    for sgn in (1, -1):
        x = sgn * V[:, 0]
        m = np.where((x > 37) & (V[:, 1] > -26) & (V[:, 1] < 20) & (V[:, 2] < 14) & (V[:, 2] > -22))[0]
        c = np.array([sgn * 34, V[m, 1].mean(), V[m, 2].mean()])
        for i in m: tgt[i] = (c + (V[i] - c) * EAR_S) - V[i]
    hold = list(held) + list(np.where(V[:, 1] > 16)[0]) + list(np.where(V[:, 1] < -50)[0])
    for sgn in (1, -1):     # round the ears' roots
        x = sgn * V[:, 0]
        hold += list(np.where((x > 28) & (x < 32) & (V[:, 1] > -30) & (V[:, 1] < 24))[0])
    hold += list(np.where((V[:, 2] < -10))[0])
    for i in hold:
        if i not in tgt: tgt[i] = np.zeros(3)
    b = np.array(sorted(tgt)); bc = np.array([tgt[i] for i in b])
    D = igl.harmonic(V, T, b, bc, 2)
    return V + D, dict(tip=int(tip), dy_mouth=float(dy_m))
