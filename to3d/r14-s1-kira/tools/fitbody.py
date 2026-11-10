"""Anny's girl (engine/data/bodies/moood-girl, SOMA skeleton) fitted to the drawn Кира's proportions: thin and angular,
long thin arms and legs, narrow shoulders — and her slouch.

The deformer (Р3's, as Р6 and Р13 used it): each joint gets an affine map — a scale along its bone (sl) and across it
(sr, or sx/sz for the trunk) —, the joints are rebuilt down the chain with their parents' maps, and every vertex
moves by its skin weights' blend of its joints' maps. Frames are kept (the retargeting reference).

Targets (kira.kira_person, metres with K = 2.8 mm per unit): shoulder joint 1.28 m high and 7.6 cm off the middle,
leg joint 0.74 m and 3.4 cm off, knee 0.38, ankle 0.056; upper arm and forearm 0.25 each; thin limbs.

The slouch (kira.SLOUCH: the whole figure shifted forward and back by a spline over the height — the head 20 units
forward, the chest back, the hips forward) is put into the rest body itself by build.py (`slouch`), after everything
is built upright: the frames stay, so every Kimodo motion is carried by a body that slouches."""
import numpy as np
import char
from common import load_body, NAMES, IX, PARENT, children, CACHE

B = load_body(char.BODY)
OLD = B['joints']

# (sl along the bone, sr across it); trunk joints: (sl, sx, sz)
GROUPS = {
    'trunk': (['Hips', 'Spine1', 'Spine2', 'Chest'], (1.31, 0.58, 0.55)),
    'neck': (['Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'], (0.8, 0.6, 0.6)),
    'clav': (['LeftShoulder', 'RightShoulder'], (0.55, 0.6)),
    'upper': (['LeftArm', 'RightArm'], (1.08, 0.50)),
    'fore': (['LeftForeArm', 'RightForeArm'], (1.15, 0.58)),
    'hand': (['LeftHand', 'RightHand'], (0.86, 0.80)),
    'fingers': ([n for n in NAMES if 'Hand' in n and n not in ('LeftHand', 'RightHand')], (0.86, 0.85)),
    'thigh': (['LeftLeg', 'RightLeg'], (0.97, 0.47)),
    'shin': (['LeftShin', 'RightShin'], (0.92, 0.46)),
    'foot': (['LeftFoot', 'RightFoot', 'LeftToeBase', 'RightToeBase', 'LeftToeEnd', 'RightToeEnd'], (0.72, 0.72)),
}
HIP_SPREAD = 0.34            # the legs closer together (the drawing's are 3.4 cm off the middle; Anny's 10)
HIPS_Y, DZ = 0.83, -0.03


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
