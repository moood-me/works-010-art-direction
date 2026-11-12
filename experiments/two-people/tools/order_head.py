# A fullbody constraint for Kimodo from a made motion's own frames, its neck and head turned to look at a point: the
# turn that brings the head's forward onto the line from the eyes to the point, shared in three equal parts by Neck1,
# Neck2 and Head. Everything else is the motion's own pose (so the hands stay where that motion had them).
#   python3 tools/order_head.py <spec.json> <out.json>
# spec: {source: <motion id here>, max?: degrees the head turns at most (a glance aside), items: [{frame, at: [x,y,z] (the point, in the source's Kimodo space)}]}
import json, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot
import pose as P

spec = json.load(open(sys.argv[1])); ix = P.IX
poses, frames, report = [], [], []
for it in spec['items']:
    L, root, _ = P.pose_at(spec['source'], it['frame'])
    G, Pp = P.fk(L, root)
    eyes = (Pp[ix['LeftEye']] + Pp[ix['RightEye']]) / 2
    a = G[ix['Head']] @ np.array([0, 0, 1.0]); b = np.asarray(it['at'], float) - eyes
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    ax = np.cross(a, b); s = np.linalg.norm(ax); ang = np.arctan2(s, a @ b)
    ang_full = ang; ang = min(ang, np.radians(spec.get('max', 180)))
    part = Rot.from_rotvec(ax / s * ang / 3).as_matrix() if s > 1e-9 else np.eye(3)
    for n in ('Neck1', 'Neck2', 'Head'):
        G, Pp = P.fk(L, root); j = ix[n]
        L[j] = G[P.PARENT[j]].T @ part @ G[j]
    G, Pp = P.fk(L, root)
    after = G[ix['Head']] @ np.array([0, 0, 1.0])
    report.append({'frame': it['frame'], 'wanted deg': round(float(np.degrees(ang_full)), 1), 'turned deg': round(float(np.degrees(ang)), 1), 'left off deg': round(float(np.degrees(np.arccos(np.clip(after @ b, -1, 1)))), 2)})
    poses.append((L, root)); frames.append(it['frame'])
json.dump([P.kimodo('fullbody', frames, poses)], open(sys.argv[2], 'w'))
print(json.dumps(report))
