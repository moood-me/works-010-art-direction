"""engine/motions/<id>.json (the studio's Kimodo data: every SOMA joint's world turn and place) → tools/motions/<id>.json
in the form experiments/indie uses: each joint's turn against SOMA's rest (D), SOMA's rest joints, the pelvis's
path, the feet's height. Same maths as experiments/indie/conv.py. python3 conv.py walk sit idle wave …"""
import base64
import json
import os
import struct
import sys
import numpy as np
from scipy.spatial.transform import Rotation as Rot

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.join(HERE, '../../../engine/motions')
b = open('/home/user/moood/engines/1/soma.bin', 'rb').read()
V, F, n = struct.unpack('<3I', b[:12]); at = 12 + V * 12 + F * 6 + V * 16
I = np.frombuffer(b[at:at + n * 48], dtype='<f4').reshape(n, 3, 4).copy()
RB = np.array([I[j][:, :3].T for j in range(n)])
REST = np.array([-(I[j][:, :3].T @ I[j][:, 3]) for j in range(n)])
OURS = ['Hips', 'Spine1', 'Spine2', 'Chest', 'Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'] + \
    [s + b for s in ['Left', 'Right'] for b in ['Shoulder', 'Arm', 'ForeArm', 'Hand', 'Leg', 'Shin', 'Foot', 'ToeBase', 'ToeEnd']]


def convert(mid):
    d = json.load(open(os.path.join(ENG, mid + '.json')))
    N, names = d['frames'], d['data']['names']
    q = np.frombuffer(base64.b64decode(d['data']['q']), dtype='<i2').reshape(N, len(names), 4) / 32767.0
    p = np.frombuffer(base64.b64decode(d['data']['p']), dtype='<i2').reshape(N, len(names), 3)
    A = {nm: i for i, nm in enumerate(names)}
    D = {}
    for nm in OURS:
        j = A[nm]
        Dm = Rot.from_quat(q[:, j]).as_matrix() @ RB[j].T
        D[nm] = [round(float(x), 5) for x in Rot.from_matrix(Dm).as_quat().reshape(-1)]
    feet = [A[s + b] for s in ['Left', 'Right'] for b in ['Foot', 'ToeBase', 'ToeEnd']]
    restMin = min(REST[j][1] for j in feet)
    out = {'id': mid, 'label': d['label'], 'n': N, 'fps': d['fps'], 'D': D,
           'rest': {nm: [round(float(x), 4) for x in REST[A[nm]]] for nm in OURS + ['LeftHandMiddle1', 'RightHandMiddle1']},
           'hipY': round(float(REST[A['Hips']][1]), 4), 'hips': [round(float(x) / 1000, 4) for x in p[:, A['Hips']].reshape(-1)],
           'foot': [round(float(p[f, feet, 1].min() / 1000 - restMin), 4) for f in range(N)]}
    json.dump(out, open(os.path.join(HERE, 'motions', mid + '.json'), 'w'))
    # a few measures to choose by: how far the head turns, how high each hand goes
    hy = Rot.from_quat(q[:, A['Head']]).as_euler('YXZ', degrees=True)[:, 0]
    print(mid, N, 'head yaw %.0f..%.0f' % (hy.min() - hy[0], hy.max() - hy[0]),
          'hands up L %.2f R %.2f' % (p[:, A['LeftHand'], 1].max() / 1000, p[:, A['RightHand'], 1].max() / 1000),
          'travel %.2f' % (np.linalg.norm(p[-1, A['Hips'], [0, 2]] - p[0, A['Hips'], [0, 2]]) / 1000))


if __name__ == '__main__':
    for m in sys.argv[1:]:
        convert(m)
