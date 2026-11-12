# SOMA's skin posed in Kimodo's space — to place a pose against a thing by its skin, not by its joints (the back on a
# wall, the buttocks on a seat, the body on a mattress). The posing is store.py's `lowest` (itself copied from the
# engine's tools/motions.py) for every coordinate: each joint's matrix is Kimodo's global rotation times the rest
# frame's inverse, a vertex the weighted sum of its joints' moves.
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'engine', 'tools'))
import soma  # noqa: E402  (the engine's, read as it is)

S = soma.load()
DOM = S['joint'][np.arange(S['V']), S['weight'].argmax(1)]          # each vertex's joint that carries most of it
PART = np.array([soma.part(soma.NAMES[j])[1] for j in DOM])         # its part: pelvis, spine, thigh, hand…
SIDE = np.array([soma.part(soma.NAMES[j])[0] for j in DOM])


def skin(G, p):
    """the posed skin [V, 3] from Kimodo's globals G (Rotation[77]) and joint places p [77, 3]"""
    R = G.as_matrix() @ S['R'].transpose(0, 2, 1)
    T = p - np.einsum('jab,jb->ja', R, S['P'])
    out = np.zeros((S['V'], 3))
    for k in range(8):
        j = S['joint'][:, k]
        out += S['weight'][:, k, None] * (np.einsum('vab,vb->va', R[j], S['bind']) + T[j])
    return out


def of(parts, side=None):
    m = np.isin(PART, parts)
    if side: m &= SIDE == side
    return m
