"""Anny's man (moood-man, the engine's) fitted to Марат's puppet proportions (figure-marat of С8: 4.32 heads tall, the
head 0.316 m: a barrel of a body, heavy shoulders far apart, thick forearms, big hands, short thick legs).

The deformer (after Р3, as Р10): each joint gets an affine map — a scale along its bone and across it — and the joints
are rebuilt down the chain with their parents' maps; every vertex moves by its skin weights' blend of its joints' maps
(the weights that later move it in motion). Frames are kept (the retargeting reference).

Targets (head units below the head's centre → metres above the floor, from marat.MARAT_FIG; floor 3.82):
hip joints y 2.3 (±0.32), knees 3.05, ankles 3.7; shoulders y 0.92 (±0.72); upper arm 0.62, forearm 0.6 long;
the head's pivot 0.4 under the head's centre. The scales below are worked out from these and the base's own joints."""
import numpy as np
from common import load_body, NAMES, IX, PARENT, children, CACHE, HH, FEET

BASE = 'moood-man'
B = load_body(BASE)
OLD = B['joints']
yw = lambda yd: (FEET - yd) * HH                 # the drawing's height (head units down from the head's centre) → metres up

HIP_Y, KNEE_Y, ANKLE_Y, HIP_X = yw(2.3), yw(3.05), yw(3.7), 0.32 * HH
SH_Y, SH_X = yw(0.92), 0.72 * HH
UPPER, FORE = 0.62 * HH, 0.6 * HH
HEAD_PIVOT = yw(0.4)
O = lambda n: OLD[IX[n]]
ln = lambda a, b: np.linalg.norm(O(b) - O(a))
# the trunk's scale s: the hips' joint sits (Hips − LeftLeg)·s over the hip joints, the shoulders (LeftArm − Hips)·s over it
s_trunk = (SH_Y - HIP_Y) / ((O('Hips')[1] - O('LeftLeg')[1]) + (O('LeftArm')[1] - O('Hips')[1]))
HIPS_Y = HIP_Y + (O('Hips')[1] - O('LeftLeg')[1]) * s_trunk
s_thigh = (HIP_Y - KNEE_Y) / (O('LeftLeg')[1] - O('LeftShin')[1])
s_shin = (KNEE_Y - ANKLE_Y) / (O('LeftShin')[1] - O('LeftFoot')[1])
s_foot = ANKLE_Y / O('LeftFoot')[1]
s_clav = (SH_X - O('LeftShoulder')[0]) / (O('LeftArm')[0] - O('LeftShoulder')[0])
neck1 = HIPS_Y + (O('Neck1')[1] - O('Hips')[1]) * s_trunk
s_neck = (HEAD_PIVOT - neck1) / (O('Head')[1] - O('Neck1')[1])

# (along the bone, across it); trunk joints: (along, x, z)
GROUPS = {
    'trunk': (['Hips', 'Spine1', 'Spine2', 'Chest'], (s_trunk, 1.15, 1.0)),
    'neck': (['Neck1', 'Neck2'], (s_neck, 0.95, 0.95)),
    'head': (['Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'], (1.0, 1.0, 1.0)),
    'clav': (['LeftShoulder', 'RightShoulder'], (s_clav, 1.0)),
    'upper': (['LeftArm', 'RightArm'], (UPPER / ln('LeftArm', 'LeftForeArm'), 0.95)),
    'fore': (['LeftForeArm', 'RightForeArm'], (FORE / ln('LeftForeArm', 'LeftHand'), 1.12)),
    'hand': (['LeftHand', 'RightHand'], (0.66, 0.92)),
    'fingers': ([n for n in NAMES if 'Hand' in n and n not in ('LeftHand', 'RightHand') and 'Thumb' not in n], (0.6, 1.0)),
    'thumb': ([n for n in NAMES if 'Thumb' in n], (0.66, 1.0)),
    'thigh': (['LeftLeg', 'RightLeg'], (s_thigh, 0.8)),
    'shin': (['LeftShin', 'RightShin'], (s_shin, 0.7)),
    'foot': (['LeftFoot', 'RightFoot', 'LeftToeBase', 'RightToeBase', 'LeftToeEnd', 'RightToeEnd'], (s_foot, 0.75)),
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


def fit():
    S = maps()
    new = np.zeros_like(OLD)
    for j in range(len(NAMES)):
        p = PARENT[j]
        if p < 0: new[j] = [OLD[j, 0], HIPS_Y, OLD[j, 2]]
        else: new[j] = new[p] + S[p] @ (OLD[j] - OLD[p])
    # the legs where the drawing has them (hip joints ±0.22 head), carried down each leg; the shoulders likewise
    shift = np.zeros_like(OLD)
    for pre, s in (('Left', 1), ('Right', -1)):
        dx = s * HIP_X - new[IX[pre + 'Leg'], 0]
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
    print('scales', {g: np.round(s, 2).tolist() for g, (_, s) in GROUPS.items()})
    for n in ['Hips', 'Chest', 'Neck1', 'Neck2', 'Head', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand', 'LeftHandMiddleEnd',
              'LeftLeg', 'LeftShin', 'LeftFoot', 'LeftToeEnd']:
        print(n, J[IX[n]].round(3))
    print('height', V[:, 1].max().round(3), 'targets hip', round(HIP_Y, 3), 'shoulder', round(SH_Y, 3), round(SH_X, 3), 'head pivot', round(HEAD_PIVOT, 3))
