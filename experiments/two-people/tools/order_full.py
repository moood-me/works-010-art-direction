# A fullbody constraint for Kimodo from a hand constraint's poses (tools/order_hand.py's output, the same frames), its
# legs set to point given ways: each leg's thigh and shin turned by the least from where they point at rest to the
# directions asked (in the person's own space: x its left, y up, z forward), the feet carried along. For a held child,
# legs round the carrier's sides instead of hanging. Fingers left as they are; the whole pose is sent (fullbody keeps
# every joint's place).
#   python3 tools/order_full.py <hand constraint json> <legs spec json> <out json>
# legs spec: {"Left": {"thigh": [x,y,z], "shin": [x,y,z]}, "Right": {...}, "frames": [indices of the hand constraint's frames to keep]}
import json, re, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot
import pose as P

hand = json.load(open(sys.argv[1])); hand = hand[0] if isinstance(hand, list) else hand
spec = json.load(open(sys.argv[2]))
ix = P.IX


def between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); ax = np.cross(a, b); s = np.linalg.norm(ax)
    return np.eye(3) if s < 1e-9 else Rot.from_rotvec(ax / s * np.arctan2(s, a @ b)).as_matrix()


def from_native(N):
    """native local turns (as sent) → turns from rest (pose.py's L): L_j = R0_p N_j R0_jᵀ (the pelvis: N R0ᵀ)"""
    L = np.empty_like(N)
    for j in range(77):
        L[j] = N[j] @ P.R0[j].T if P.PARENT[j] < 0 else P.R0[P.PARENT[j]] @ N[j] @ P.R0[j].T
    return L


keep = spec.get('frames', list(range(len(hand['frame_indices']))))
poses, frames = [], []
for k in keep:
    N = np.array([Rot.from_rotvec(v).as_matrix() for v in hand['local_joints_rot'][k]])
    root = np.array(hand['root_positions'][k]); L = from_native(N)
    for side in ['Left', 'Right']:
        legs = spec[side]
        for joint, child, want in [(side + 'Leg', side + 'Shin', legs['thigh']), (side + 'Shin', side + 'Foot', legs['shin'])]:
            G, Pp = P.fk(L, root); j, c = ix[joint], ix[child]
            r = between(Pp[c] - Pp[j], np.array(want, float))
            L[j] = (G[P.PARENT[j]].T if P.PARENT[j] >= 0 else np.eye(3)) @ r @ G[j]
    poses.append((L, root)); frames.append(hand['frame_indices'][k])
con = P.kimodo('fullbody', frames, poses)
con['root_positions'] = [[round(x, 3) for x in r] for r in con['root_positions']]
con['local_joints_rot'] = [[[round(x, 3) + 0.0 for x in j] for j in f] for f in con['local_joints_rot']]
text = re.sub(r'(?<![\d.])-?0\.0(?=[,\]])', '0', json.dumps([con], separators=(',', ':')))
open(sys.argv[3], 'w').write(text)
G, Pp = P.fk(poses[0][0], poses[0][1])
print({n: [round(float(v), 3) for v in Pp[ix[n]]] for n in ['Hips', 'LeftShin', 'LeftFoot', 'RightFoot', 'LeftHand', 'RightHand']})
