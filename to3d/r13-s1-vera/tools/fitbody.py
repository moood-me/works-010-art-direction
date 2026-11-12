"""Anny's woman (engine/data/bodies/moood-woman, SOMA skeleton) fitted to the drawn Вера's proportions.

The deformer (Р3's, as Р6 used it): each joint gets an affine map — a scale along its bone (sl) and across it (sr, or
sx/sz for the trunk) —, the joints are rebuilt down the chain with their parents' maps, and every vertex moves by its
skin weights' blend of its joints' maps (the same weights that later move it in motion). Bones take the drawing's
lengths and the limbs its thickness; the surface stays Anny's, smooth where parts meet. Frames are kept (the
retargeting reference).

Targets (cast.vera_person, metres with K = 2.8 mm per unit): shoulder joint 1.34 m high and 9 cm off the middle, leg
joint 0.75 m and 4 cm off, knee 0.39, ankle 0.045; upper arm and forearm 0.235 each; a long narrow flat trunk
(the coat's half-width is 11 cm at the chest, its depth 11 cm), thin limbs."""
import numpy as np
import char
from common import load_body, NAMES, IX, PARENT, children, CACHE

B = load_body(char.BODY)
OLD = B['joints']

# (sl along the bone, sr across it); trunk joints: (sl, sx, sz)
GROUPS = {
    'trunk': (['Hips', 'Spine1', 'Spine2', 'Chest'], (1.30, 0.62, 0.52)),
    'neck': (['Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'], (0.8, 0.6, 0.6)),
    'clav': (['LeftShoulder', 'RightShoulder'], (0.62, 0.62)),
    'upper': (['LeftArm', 'RightArm'], (0.96, 0.60)),
    'fore': (['LeftForeArm', 'RightForeArm'], (1.03, 0.64)),
    'hand': (['LeftHand', 'RightHand'], (0.86, 0.80)),
    'fingers': ([n for n in NAMES if 'Hand' in n and n not in ('LeftHand', 'RightHand')], (0.86, 0.85)),
    'thigh': (['LeftLeg', 'RightLeg'], (0.94, 0.52)),
    'shin': (['LeftShin', 'RightShin'], (0.94, 0.50)),
    'foot': (['LeftFoot', 'RightFoot', 'LeftToeBase', 'RightToeBase', 'LeftToeEnd', 'RightToeEnd'], (0.62, 0.62)),
}
HIP_SPREAD = 0.36            # the legs closer together (the drawing's are 4 cm off the middle; Anny's 12)
HIPS_Y, DZ = 0.84, -0.03


def axis(j):
    ch = children(j)
    if not ch: return None
    k = max(ch, key=lambda c: np.linalg.norm(OLD[c] - OLD[j]))
    a = OLD[k] - OLD[j]
    return a / np.linalg.norm(a)


def maps():
    S = np.zeros((len(NAMES), 3, 3))
    for g, (names, s) in GROUPS.items():
        for n in names:
            j = IX[n]
            if g in ('trunk', 'neck'):
                S[j] = np.diag([s[1], s[0], s[2]]); continue
            a = axis(j)
            if a is None: a = axis(PARENT[j])
            S[j] = s[0] * np.outer(a, a) + s[1] * (np.eye(3) - np.outer(a, a))
    return S


def fit(hips_y=HIPS_Y, dz=DZ):
    S = maps()
    # the pelvis → leg offset narrowed
    Sp = S.copy()
    new = np.zeros_like(OLD)
    for j in range(len(NAMES)):
        p = PARENT[j]
        if p < 0: new[j] = [OLD[j, 0], hips_y, OLD[j, 2] + dz]; continue
        off = S[p] @ (OLD[j] - OLD[p])
        if NAMES[j] in ('LeftLeg', 'RightLeg'): off[0] = (OLD[j, 0] - OLD[p, 0]) * HIP_SPREAD
        new[j] = new[p] + off
    V = B['positions']
    out = np.zeros_like(V)
    for k in range(4):
        j = B['sj'][:, k]; w = B['sw'][:, k][:, None]
        out += w * (new[j] + np.einsum('nab,nb->na', S[j], V - OLD[j]))
    lo = out[:, 1].min(); out[:, 1] -= lo; new[:, 1] -= lo
    return out, new


if __name__ == '__main__':
    V, J = fit()
    for n in ['Hips', 'Chest', 'Neck1', 'LeftArm', 'LeftForeArm', 'LeftHand', 'LeftHandMiddleEnd', 'LeftLeg', 'LeftShin', 'LeftFoot', 'LeftToeEnd']:
        print(n, J[IX[n]].round(3))
    print('height', V[:, 1].max())
    np.savez(f'{CACHE}/body_fit.npz', V=V, J=J)
