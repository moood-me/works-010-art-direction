"""Anny's child body (moood-child, the engine's) fitted to Тим's proportions.

The deformer: each joint gets an affine map — a scale along its bone (sl) and across it (sr, or sx/sz for the trunk) —
and the joints are rebuilt down the chain with their parents' maps; every vertex moves by its skin weights' blend of
its joints' maps (the same weights that later move it in motion). So bones get the drawing's lengths and the limbs its
thickness, while the surface stays Anny's, smooth where parts meet. Frames are kept (the retargeting reference).

Targets read off figure-tim (feet at 0, chin at -358 figure units; 1 unit = 2.33 mm): hip joint 0.43 m, knee 0.23,
ankle 0.05, shoulder 0.79; arms about 0.3 m to the fingertips (the drawing's are even shorter — bent behind his back),
thin limbs (the drawing: 4.7 cm thigh, 3.3 cm ankle, mitten hands)."""
import numpy as np
from common import load_body, NAMES, IX, PARENT, children, CACHE

B = load_body('moood-child')
OLD = B['joints']

# (sl along the bone, sr across it); trunk joints: (sl, sx, sz)
GROUPS = {
    'trunk': (['Hips', 'Spine1', 'Spine2', 'Chest'], (1.0, 0.8, 0.78)),
    'neck': (['Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'], (0.6, 0.8, 0.8)),
    'clav': (['LeftShoulder', 'RightShoulder'], (0.86, 0.86)),
    'upper': (['LeftArm', 'RightArm'], (0.62, 0.55)),
    'fore': (['LeftForeArm', 'RightForeArm'], (0.6, 0.52)),
    'hand': ([n for n in NAMES if 'Hand' in n], (0.55, 0.6)),
    'thigh': (['LeftLeg', 'RightLeg'], (0.69, 0.56)),
    'shin': (['LeftShin', 'RightShin'], (0.6, 0.52)),
    'foot': (['LeftFoot', 'RightFoot', 'LeftToeBase', 'RightToeBase', 'LeftToeEnd', 'RightToeEnd'], (0.62, 0.62)),
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
            if g == 'trunk':
                S[j] = np.diag([s[1], s[0], s[2]])
                continue
            a = axis(j)
            if a is None: a = axis(PARENT[j])
            S[j] = s[0] * np.outer(a, a) + s[1] * (np.eye(3) - np.outer(a, a))
    return S


def fit(hips_y=0.47):
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
