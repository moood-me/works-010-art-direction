# A hand constraint for Kimodo: a pose Kimodo made (a frame of a made motion), turned and moved so its pelvis stands
# where asked, its arm turned (shoulder, elbow) by the least to bring the palm onto the target; written as Kimodo's
# constraint (frames, root positions, every joint's local turn).
#   python3 tools/order_hand.py <spec.json> <out.json>
# spec: {source: <motion id here>, frame, side: "Right", kind: "right-hand", items: [{frame, target: [x,y,z], hip: [x,z],
#        heading?, handYaw?}]}  — target: where the palm's middle comes (Kimodo space), hip: where the pelvis stands then;
# or both hands: {…, sides: ["Right", "Left"], items: [{frame, targets: {Right: […], Left: […]}, hip}]} → a constraint
# for each hand, the same pose in both.
import json, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot
import pose as P

spec = json.load(open(sys.argv[1]))
sides = spec.get('sides', [spec.get('side')])
L0, root0, _ = P.pose_at(spec['source'], spec['frame'])
# SOMA's palm middle at rest, as the page's palmRest (scene.js): between the hand and the middle finger's root, 1.5 cm
# out on the palm's side
R = P.REST; ix = P.IX


def palm_rest(side):
    h, m, i, r = R[ix[side + 'Hand']], R[ix[side + 'HandMiddle1']], R[ix[side + 'HandIndex1']], R[ix[side + 'HandRing1']]
    n = np.cross(r - i, m - h); n /= np.linalg.norm(n)
    if side == 'Right': n = -n
    return (h + m) / 2 + 0.015 * n


def palm(L, root, side):
    G, Pp = P.fk(L, root); c = ix[side + 'Hand']
    return Pp[c] + G[c] @ (palm_rest(side) - R[c])


# the pose's own heading: its hips' line
def heading_of(L, root):
    G, Pp = P.fk(L, root)
    v = Pp[ix['LeftLeg']] - Pp[ix['RightLeg']]
    return np.arctan2(-v[2], v[0])


def NAMES_UNDER(k, c):
    while k >= 0:
        if k == c: return True
        k = P.PARENT[k]
    return False


h0 = heading_of(L0, root0)
poses, frames, report = [], [], []
for it in spec['items']:
    want_h = it.get('heading', 0.0)   # 'own': the source pose's own heading kept
    if 'sourceFrame' in it:            # this item's pose from another frame of the source
        Ls, rs, _ = P.pose_at(spec['source'], it['sourceFrame']); hs = heading_of(Ls, rs)
    else: Ls, rs, hs = L0, root0, h0
    L, root = P.turn_move(Ls, rs, 0.0 if want_h == 'own' else want_h - hs, [0, 0])
    root = np.array([it['hip'][0], root[1], it['hip'][1]])
    targets = it.get('targets') or {sides[0]: it['target']}
    if 'fingersFrom' in spec:   # the fingers' own turns from another pose (a flat hand), the rest as it is
        Lf, _, _ = P.pose_at(spec['fingersFrom']['source'], spec['fingersFrom']['frame'])
        for sd in sides:
            h = ix[sd + 'Hand']
            for k in range(77):
                if k != h and NAMES_UNDER(k, h): L[k] = Lf[k]
    miss = {}
    for side in sides:
        c = ix[side + 'Hand']
        target = np.array(targets[side], float)
        if 'handYaw' in it:   # the hand turned about the vertical so it points (wrist → middle finger) that way
            G, Pp = P.fk(L, root)
            d = Pp[ix[side + 'HandMiddle1']] - Pp[c]
            r = Rot.from_rotvec([0, it['handYaw'] - np.arctan2(d[0], d[2]), 0]).as_matrix()
            L[c] = G[P.PARENT[c]].T @ r @ G[c]
        # the arm alone; a few rounds, since the palm sits off the wrist (and, with straightWrists, the wrist is
        # straightened each round: the hand going on as the forearm does)
        for _ in range(12):
            pm = palm(L, root, side)
            G, Pp = P.fk(L, root)
            L, _ = P.reach(L, root, side, Pp[c] + (target - pm))
            if it.get('straightWrists'): L[c] = np.eye(3)
            if 'elbowPole' in it:      # the arm turned about shoulder → wrist so the elbow points that way (down: hanging)
                G, Pp = P.fk(L, root); a_, b_ = ix[side + 'Arm'], ix[side + 'ForeArm']
                ax = Pp[c] - Pp[a_]; ax /= np.linalg.norm(ax)
                e = Pp[b_] - Pp[a_]; e -= ax * (e @ ax); d = np.array(it['elbowPole'], float); d -= ax * (d @ ax)
                ang = np.arctan2(np.cross(e, d) @ ax, e @ d)
                L[a_] = G[P.PARENT[a_]].T @ Rot.from_rotvec(ax * ang).as_matrix() @ G[a_]
                if 'handYaw' in it:   # the hand pointed again (the turn above carried it)
                    G, Pp = P.fk(L, root); dd = Pp[ix[side + 'HandMiddle1']] - Pp[c]
                    L[c] = G[P.PARENT[c]].T @ Rot.from_rotvec([0, it['handYaw'] - np.arctan2(dd[0], dd[2]), 0]).as_matrix() @ G[c]
        miss[side] = round(float(np.linalg.norm(palm(L, root, side) - target) * 1000), 1)
    report.append({'frame': it['frame'], 'palm miss mm': miss})
    poses.append((L, root)); frames.append(it['frame'])
import re

out = []
for side in sides:
    con = P.kimodo(side.lower() + '-hand', frames, poses)
    # only the hands' chains (pelvis → spine → arm → hand, and the fingers) put the hands where they are: the other
    # joints are sent as zero (a shorter ask). Both hands' chains in every constraint: Kimodo merges hand constraints
    # of the same frames into one pose (a try with each hand's own chain alone left the other arm in the T-pose there)
    keep = set()
    for sd in sides:
        c = ix[sd + 'Hand']; j = c
        while j >= 0: keep.add(j); j = P.PARENT[j]
        keep |= {k for k in range(77) if NAMES_UNDER(k, c)}
    con['local_joints_rot'] = [[r if k in keep else [0, 0, 0] for k, r in enumerate(f)] for f in con['local_joints_rot']]
    # shorter: 3 decimals (a milliradian is a millimetre at a metre)
    con['root_positions'] = [[round(x, 3) for x in r] for r in con['root_positions']]
    con['local_joints_rot'] = [[[round(x, 3) + 0.0 for x in j] for j in f] for f in con['local_joints_rot']]
    out.append(con)
text = json.dumps(out[0] if len(out) == 1 else out, separators=(',', ':'))
text = re.sub(r'(?<![\d.])-?0\.0(?=[,\]])', '0', text)
open(sys.argv[2], 'w').write(text)
print(json.dumps(report))
