"""Anny's man body (moood-man, the engine's) fitted to Марат's proportions in figure-marat: a barrel on short legs.

The deformer is Р3's: each joint gets an affine map — a scale along its bone (sl) and across it (sr, or sx/sz for
the trunk) — the joints are rebuilt down the chain with their parents' maps, every vertex moves by its skin weights'
blend of its joints' maps; frames are kept (the retargeting reference). Two things added for him:
- the trunk grows forward more than back (the belly goes first): what lies behind a trunk joint is scaled by BACK;
- a joint may be shifted after its parent's map placed it (SHIFT): his legs stand close together under the wide barrel.

Targets read off figure-marat (feet at 0, the curls' top at −810 figure units; 1 unit = 2.28 mm → 1.85 m): legs to the
hip joint 0.66 m (Anny's man: 0.93), the trunk from there to the shoulders 0.75 m and 0.7 m wide at the belly,
shoulders ±27 cm, upper arms 15 cm thick, forearms 11, big fists."""
import numpy as np
from common import load_body, NAMES, IX, PARENT, children, CACHE

B = load_body('moood-man')
OLD = B['joints']

# (sl along the bone, sr across it); trunk joints: (sl, sx, sz)
TRUNK = ('hips', 'belly', 'chest')
GROUPS = {
    'hips': (['Hips'], (1.0, 1.55, 1.75)),
    'belly': (['Spine1', 'Spine2'], (1.5, 2.0, 2.3)),
    'chest': (['Chest'], (1.5, 1.75, 1.75)),
    'neck': (['Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'], (0.5, 1.5, 1.5)),
    'clav': (['LeftShoulder', 'RightShoulder'], (1.35, 1.5)),
    'upper': (['LeftArm', 'RightArm'], (1.0, 1.5)),
    'fore': (['LeftForeArm', 'RightForeArm'], (1.0, 1.4)),
    'hand': (['LeftHand', 'RightHand'], (1.25, 1.3)),
    'fingers': ([n for n in NAMES if 'Hand' in n and n not in ('LeftHand', 'RightHand') and 'Thumb' not in n], (1.1, 1.35)),
    'thumb': ([n for n in NAMES if 'Thumb' in n], (1.1, 1.35)),
    'thigh': (['LeftLeg', 'RightLeg'], (0.7, 1.12)),
    'shin': (['LeftShin', 'RightShin'], (0.7, 1.3)),
    'foot': (['LeftFoot', 'RightFoot', 'LeftToeBase', 'RightToeBase', 'LeftToeEnd', 'RightToeEnd'], (0.9, 1.1)),
}
BACK = 0.62
SHIFT = {'LeftLeg': [-0.075, 0, 0], 'RightLeg': [0.075, 0, 0]}


def axis(j):
    ch = children(j)
    if not ch: return None
    # the main child: the one farthest (a spine's next joint, a hand's middle finger)
    k = max(ch, key=lambda c: np.linalg.norm(OLD[c] - OLD[j]))
    a = OLD[k] - OLD[j]
    return a / np.linalg.norm(a)


def maps():
    S = np.zeros((len(NAMES), 3, 3)); back = np.ones(len(NAMES))
    for g, (names, s) in GROUPS.items():
        for n in names:
            j = IX[n]
            if g in TRUNK:
                S[j] = np.diag([s[1], s[0], s[2]]); back[j] = BACK
                continue
            a = axis(j)
            if a is None: a = axis(PARENT[j])
            S[j] = s[0] * np.outer(a, a) + s[1] * (np.eye(3) - np.outer(a, a))
    return S, back


def fit(hips_y=0.75):
    S, back = maps()
    new = np.zeros_like(OLD)
    for j in range(len(NAMES)):
        p = PARENT[j]
        if p < 0: new[j] = [OLD[j, 0], hips_y, OLD[j, 2]]
        else: new[j] = new[p] + S[p] @ (OLD[j] - OLD[p]) + SHIFT.get(NAMES[j], [0, 0, 0])
    V = B['positions']
    out = np.zeros_like(V)
    for k in range(4):
        j = B['sj'][:, k]; w = B['sw'][:, k][:, None]
        loc = V - OLD[j]
        loc[:, 2] = np.where(loc[:, 2] < 0, loc[:, 2] * back[j], loc[:, 2])
        out += w * (new[j] + np.einsum('nab,nb->na', S[j], loc))
    # stand on the floor
    lo = out[:, 1].min(); out[:, 1] -= lo; new[:, 1] -= lo
    return out, new


if __name__ == '__main__':
    V, J = fit()
    for n in ['Hips', 'Chest', 'Neck1', 'Head', 'LeftArm', 'LeftForeArm', 'LeftHand', 'LeftHandMiddleEnd', 'LeftLeg', 'LeftShin', 'LeftFoot', 'LeftToeEnd']:
        print(n, J[IX[n]].round(3))
    print('height', V[:, 1].max(), 'x', V[:, 0].min(), V[:, 0].max(), 'z', V[:, 2].min(), V[:, 2].max())
    np.savez(f'{CACHE}/body_fit.npz', V=V, J=J)
