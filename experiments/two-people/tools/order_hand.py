# A hand constraint for Kimodo: a pose Kimodo made (a frame of a made motion), turned and moved so its pelvis stands
# where asked, its arm turned (shoulder, elbow) by the least to bring the palm onto the target; written as Kimodo's
# constraint (frames, root positions, every joint's local turn).
#   python3 tools/order_hand.py <spec.json> <out.json>
# spec: {source: <motion id here>, frame, side: "Right", kind: "right-hand", items: [{frame, target: [x,y,z], hip: [x,z],
#        heading?}]}  — target: where the palm's middle comes (Kimodo space), hip: where the pelvis stands then.
import json, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot
import pose as P

spec = json.load(open(sys.argv[1]))
side = spec['side']
L0, root0, _ = P.pose_at(spec['source'], spec['frame'])
# SOMA's palm middle at rest, as the page's palmRest (scene.js): between the hand and the middle finger's root, 1.5 cm
# out on the palm's side
R = P.REST; ix = P.IX
h, m, i, r = R[ix[side + 'Hand']], R[ix[side + 'HandMiddle1']], R[ix[side + 'HandIndex1']], R[ix[side + 'HandRing1']]
n = np.cross(r - i, m - h); n /= np.linalg.norm(n)
if side == 'Right': n = -n
palm_rest = (h + m) / 2 + 0.015 * n
c = ix[side + 'Hand']


def palm(L, root):
    G, Pp = P.fk(L, root)
    return Pp[c] + G[c] @ (palm_rest - R[c])


# the pose's own heading: its hips' line
def heading_of(L, root):
    G, Pp = P.fk(L, root)
    v = Pp[ix['LeftLeg']] - Pp[ix['RightLeg']]
    return np.arctan2(-v[2], v[0])


h0 = heading_of(L0, root0)
poses, frames, report = [], [], []
for it in spec['items']:
    want_h = it.get('heading', 0.0)   # 'own': the source pose's own heading kept
    L, root = P.turn_move(L0, root0, 0.0 if want_h == 'own' else want_h - h0, [0, 0])
    root = np.array([it['hip'][0], root[1], it['hip'][1]])
    target = np.array(it['target'], float)
    if 'handYaw' in it:   # the hand turned about the vertical so it points (wrist → middle finger) that way
        G, Pp = P.fk(L, root)
        d = Pp[ix[side + 'HandMiddle1']] - Pp[c]
        r = Rot.from_rotvec([0, it['handYaw'] - np.arctan2(d[0], d[2]), 0]).as_matrix()
        L[c] = G[P.PARENT[c]].T @ r @ G[c]
    # the arm alone; a few rounds, since the palm sits off the wrist
    for _ in range(6):
        pm = palm(L, root)
        G, Pp = P.fk(L, root)
        wrist_target = Pp[c] + (target - pm)
        L, _ = P.reach(L, root, side, wrist_target)
    miss = np.linalg.norm(palm(L, root) - target)
    report.append({'frame': it['frame'], 'palm miss mm': round(float(miss * 1000), 1)})
    poses.append((L, root)); frames.append(it['frame'])
con = P.kimodo(spec['kind'], frames, poses)
# shorter: 4 decimals are a tenth of a millimetre at a metre
# shorter: 3 decimals (a milliradian is a millimetre at a metre)
con['root_positions'] = [[round(x, 3) for x in r] for r in con['root_positions']]
con['local_joints_rot'] = [[[round(x, 3) + 0.0 for x in j] for j in f] for f in con['local_joints_rot']]
text = json.dumps(con, separators=(',', ':'))
import re
text = re.sub(r'(?<![\d.])-?0\.0(?=[,\]])', '0', text)
open(sys.argv[2], 'w').write(text)
print(json.dumps(report))
