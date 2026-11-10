"""Anny's child body (moood-child, the engine's) fitted to Тим's puppet proportions (figure-tim of С8: 3.36 heads
tall, the head 0.342 m; short thin legs, a barrel of a body, thin arms, small mitten hands).

The deformer (after Р3): each joint gets an affine map — a scale along its bone and across it — and the joints are
rebuilt down the chain with their parents' maps; every vertex moves by its skin weights' blend of its joints' maps
(the weights that later move it in motion). Frames are kept (the retargeting reference).

Targets (metres above the floor, from cast.TIM_FIG; 1 head unit = 0.342 m, floor 2.86 under the head's centre):
hip joints 0.41, knees 0.23, ankles 0.05; shoulders 0.72, ±0.14; elbow 0.55; wrist 0.39; neck base 0.74; the head's
pivot 0.84 (under the skull)."""
import numpy as np
from common import load_body, NAMES, IX, PARENT, children, CACHE

B = load_body('moood-child')
OLD = B['joints']

# (along the bone, across it); trunk joints: (along, x, z)
GROUPS = {
    'trunk': (['Hips', 'Spine1', 'Spine2', 'Chest'], (0.80, 1.0, 0.95)),
    'neck': (['Neck1', 'Neck2'], (0.95, 0.82, 0.82)),
    'head': (['Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'], (1.0, 1.0, 1.0)),
    'clav': (['LeftShoulder', 'RightShoulder'], (1.05, 0.85)),
    'upper': (['LeftArm', 'RightArm'], (0.88, 0.62)),
    'fore': (['LeftForeArm', 'RightForeArm'], (0.84, 0.62)),
    'hand': (['LeftHand', 'RightHand'], (0.62, 0.78)),
    'fingers': ([n for n in NAMES if 'Hand' in n and n not in ('LeftHand', 'RightHand') and 'Thumb' not in n], (0.5, 0.95)),
    'thumb': ([n for n in NAMES if 'Thumb' in n], (0.6, 0.95)),
    'thigh': (['LeftLeg', 'RightLeg'], (0.63, 0.72)),
    'shin': (['LeftShin', 'RightShin'], (0.61, 0.55)),
    'foot': (['LeftFoot', 'RightFoot', 'LeftToeBase', 'RightToeBase', 'LeftToeEnd', 'RightToeEnd'], (0.72, 0.8)),
}


def axis(j):
    ch = children(j)
    if not ch: return None
    k = max(ch, key=lambda c: np.linalg.norm(OLD[c] - OLD[j]))
    a = OLD[k] - OLD[j]
    return a / np.linalg.norm(a)


def maps():
    S = np.tile(np.eye(3), (len(NAMES), 1, 1))
    for g, (names, s) in GROUPS.items():
        for n in names:
            j = IX[n]
            if g == 'trunk':
                S[j] = np.diag([s[1], s[0], s[2]]); continue
            if g == 'head':
                S[j] = np.eye(3) * s[0]; continue
            a = axis(j)
            if a is None: a = axis(PARENT[j])
            S[j] = s[0] * np.outer(a, a) + s[1] * (np.eye(3) - np.outer(a, a))
    return S


LEG_X = 0.058


def fit(hips_y=0.47):
    S = maps()
    new = np.zeros_like(OLD)
    for j in range(len(NAMES)):
        p = PARENT[j]
        if p < 0: new[j] = [OLD[j, 0], hips_y, OLD[j, 2]]
        else: new[j] = new[p] + S[p] @ (OLD[j] - OLD[p])
    # the legs closer together (the drawing's stand: feet ±0.17 head apart), carried down each leg
    shift = np.zeros_like(OLD)
    for pre, s in (('Left', 1), ('Right', -1)):
        dx = s * LEG_X - new[IX[pre + 'Leg'], 0]
        for n in NAMES:
            if n.startswith(pre) and any(k in n for k in ('Leg', 'Shin', 'Foot', 'Toe')):
                shift[IX[n], 0] = dx
    new = new + shift
    V = B['positions']
    out = np.zeros_like(V)
    for k in range(4):
        j = B['sj'][:, k]; w = B['sw'][:, k][:, None]
        out += w * (new[j] + np.einsum('nab,nb->na', S[j], V - OLD[j]))
    lo = out[:, 1].min(); out[:, 1] -= lo; new[:, 1] -= lo
    return out, new


if __name__ == '__main__':
    V, J = fit()
    for n in ['Hips', 'Chest', 'Neck1', 'Neck2', 'Head', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand', 'LeftHandMiddleEnd',
              'LeftLeg', 'LeftShin', 'LeftFoot', 'LeftToeEnd']:
        print(n, J[IX[n]].round(3))
    print('height', V[:, 1].max().round(3))
