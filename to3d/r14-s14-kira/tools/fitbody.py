"""Anny's girl body (moood-girl, the engine's) fitted to Кира's proportions (Р3's deformer).

Each joint gets an affine map — a scale along its bone (sl) and across it (sr; sx/sz for the trunk) —, the joints are
rebuilt down the chain with their parents' maps, every vertex moves by its skin weights' blend of its joints' maps.
Frames are kept (the retargeting reference).

Targets read off figure-kira (feet at 0; 1 figure unit = 2.8 mm; the head is 0.56 of head_front's units): hips 0.76 m,
knee 0.40, shoulders 1.15 and narrow, long thin arms (0.5 m to the wrist), stick legs (6 cm thigh, 4.5 cm ankle)."""
import numpy as np
from common import load_body, NAMES, IX, PARENT, children, CACHE

B = load_body('moood-girl')
OLD = B['joints']

GROUPS = {
    'trunk': (['Hips', 'Spine1', 'Spine2', 'Chest'], (1.13, 0.74, 0.74)),
    'neck': (['Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'], (0.7, 0.7, 0.7)),
    'clav': (['LeftShoulder', 'RightShoulder'], (0.74, 0.8)),
    'upper': (['LeftArm', 'RightArm'], (1.16, 0.62)),
    'fore': (['LeftForeArm', 'RightForeArm'], (1.16, 0.62)),
    'hand': (['LeftHand', 'RightHand'], (0.86, 0.8)),
    'fingers': ([n for n in NAMES if 'Hand' in n and n not in ('LeftHand', 'RightHand')], (0.86, 0.8)),
    'thigh': (['LeftLeg', 'RightLeg'], (0.83, 0.5)),
    'shin': (['LeftShin', 'RightShin'], (0.93, 0.6)),
    'foot': (['LeftFoot', 'RightFoot', 'LeftToeBase', 'RightToeBase', 'LeftToeEnd', 'RightToeEnd'], (0.9, 0.8)),
}


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
            if g == 'trunk':
                S[j] = np.diag([s[1], s[0], s[2]])
                continue
            a = axis(j)
            if a is None: a = axis(PARENT[j])
            S[j] = s[0] * np.outer(a, a) + s[1] * (np.eye(3) - np.outer(a, a))
    return S


def fit(hips_y=0.76, hip_x=0.62):
    S = maps()
    new = np.zeros_like(OLD)
    for j in range(len(NAMES)):
        p = PARENT[j]
        if p < 0: new[j] = [OLD[j, 0], hips_y, OLD[j, 2]]
        else:
            d = S[p] @ (OLD[j] - OLD[p])
            if NAMES[j] in ('LeftLeg', 'RightLeg'): d = (OLD[j] - OLD[p]) * [hip_x, 1.0, 0.8]      # narrow hips
            new[j] = new[p] + d
    V = B['positions']
    out = np.zeros_like(V)
    for k in range(4):
        j = B['sj'][:, k]; w = B['sw'][:, k][:, None]
        out += w * (new[j] + np.einsum('nab,nb->na', S[j], V - OLD[j]))
    lo = out[:, 1].min(); out[:, 1] -= lo; new[:, 1] -= lo
    return out, new


if __name__ == '__main__':
    V, J = fit()
    for n in ['Hips', 'Chest', 'Neck1', 'Head', 'LeftArm', 'LeftForeArm', 'LeftHand', 'LeftHandMiddleEnd', 'LeftLeg', 'LeftShin', 'LeftFoot', 'LeftToeEnd']:
        print(n, J[IX[n]].round(3))
    print('height', V[:, 1].max())
