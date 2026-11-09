"""Anny's woman body (moood-woman, the engine's) fitted to Аня's proportions in figure-anya.

The deformer (as Р3's): each joint gets an affine map — a scale along its bone (sl) and across it (sr, or sx/sz for
the trunk) — and the joints are rebuilt down the chain with their parents' maps; every vertex moves by its skin weights'
blend of its joints' maps. Frames are kept (the retargeting reference).

Targets read off figure-anya (feet at 0, hair top at −736 figure units; 1 unit = 2.28 mm → 1.68 m): waist 1.07 m,
shoulder line 1.37, chin 1.42; shoulders ±12 cm with the cardigan, waist ±8 cm; legs 5.5 cm thick above the knee and
2 cm at the ankle, arms 6 → 3.5 cm: a long thin figure, narrow everywhere."""
import numpy as np
from common import load_body, NAMES, IX, PARENT, children, CACHE

B = load_body('moood-woman')
OLD = B['joints']

# (sl along the bone, sr across it); trunk joints: (sl, sx, sz)
GROUPS = {
    'hips': (['Hips'], (1.0, 0.66, 0.72)),
    'trunk': (['Spine1', 'Spine2', 'Chest'], (1.2, 0.6, 0.7)),
    'neck': (['Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'], (0.6, 0.6, 0.6)),
    'clav': (['LeftShoulder', 'RightShoulder'], (0.56, 0.62)),
    'upper': (['LeftArm', 'RightArm'], (0.82, 0.6)),
    'fore': (['LeftForeArm', 'RightForeArm'], (0.82, 0.56)),
    'hand': (['LeftHand', 'RightHand'], (0.62, 0.62)),
    'fingers': ([n for n in NAMES if 'Hand' in n and n not in ('LeftHand', 'RightHand') and 'Thumb' not in n], (0.5, 0.8)),
    'thumb': ([n for n in NAMES if 'Thumb' in n], (0.55, 0.8)),
    'thigh': (['LeftLeg', 'RightLeg'], (1.0, 0.52)),
    'shin': (['LeftShin', 'RightShin'], (1.0, 0.42)),
    'foot': (['LeftFoot', 'RightFoot', 'LeftToeBase', 'RightToeBase', 'LeftToeEnd', 'RightToeEnd'], (0.62, 0.55)),
}


def axis(j):
    ch = children(j)
    if not ch: return None
    # the main child: the one farthest (a spine's next joint, a hand's middle finger)
    k = max(ch, key=lambda c: np.linalg.norm(OLD[c] - OLD[j]))
    a = OLD[k] - OLD[j]
    return a / np.linalg.norm(a)


def maps():
    S = np.zeros((len(NAMES), 3, 3))
    for g, (names, s) in GROUPS.items():
        for n in names:
            j = IX[n]
            if g in ('trunk', 'hips'):
                S[j] = np.diag([s[1], s[0], s[2]])
                continue
            a = axis(j)
            if a is None: a = axis(PARENT[j])
            S[j] = s[0] * np.outer(a, a) + s[1] * (np.eye(3) - np.outer(a, a))
    return S


def fit(hips_y=0.88):
    S = maps()
    new = np.zeros_like(OLD)
    for j in range(len(NAMES)):
        p = PARENT[j]
        if p < 0: new[j] = [OLD[j, 0], hips_y, OLD[j, 2]]
        else: new[j] = new[p] + S[p] @ (OLD[j] - OLD[p])
    V = B['positions']
    out = np.zeros_like(V)
    for k in range(4):
        j = B['sj'][:, k]; w = B['sw'][:, k][:, None]
        out += w * (new[j] + np.einsum('nab,nb->na', S[j], V - OLD[j]))
    # stand on the floor
    lo = out[:, 1].min(); out[:, 1] -= lo; new[:, 1] -= lo
    return out, new


if __name__ == '__main__':
    V, J = fit()
    for n in ['Hips', 'Chest', 'Neck1', 'Head', 'LeftArm', 'LeftForeArm', 'LeftHand', 'LeftHandMiddleEnd', 'LeftLeg', 'LeftShin', 'LeftFoot', 'LeftToeEnd']:
        print(n, J[IX[n]].round(3))
    print('height', V[:, 1].max())
    np.savez(f'{CACHE}/body_fit.npz', V=V, J=J)
