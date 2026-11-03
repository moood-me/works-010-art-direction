# SOMA, the 77-joint skeleton Kimodo moves (data/soma/soma.bin: Kimodo's SOMA skin, as moood converted it):
# its joints, parents, the part of the body each joint belongs to, and its rest frames (the T-pose a motion's
# rotations are measured against). Writes data/skeleton.json.  python3 tools/soma.py
import json, os, struct, numpy as np
from scipy.spatial.transform import Rotation as Rot

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOMA_BIN = os.path.join(ROOT, 'data/soma/soma.bin')

NAMES = ["Hips", "Spine1", "Spine2", "Chest", "Neck1", "Neck2", "Head", "HeadEnd", "Jaw", "LeftEye", "RightEye"] + \
    [s + n for s in ['Left', 'Right'] for n in
     ['Shoulder', 'Arm', 'ForeArm', 'Hand'] + [f'Hand{f}{k}' for f, ks in [('Thumb', ['1', '2', '3', 'End']), ('Index', ['1', '2', '3', '4', 'End']),
                                                                            ('Middle', ['1', '2', '3', '4', 'End']), ('Ring', ['1', '2', '3', '4', 'End']),
                                                                            ('Pinky', ['1', '2', '3', '4', 'End'])] for k in ks]] + \
    [s + n for s in ['Left', 'Right'] for n in ['Leg', 'Shin', 'Foot', 'ToeBase', 'ToeEnd']]


def load():
    b = open(SOMA_BIN, 'rb').read()
    V, F, J = struct.unpack('<3I', b[:12]); at = 12
    bind = np.frombuffer(b, '<f4', V * 3, at).reshape(V, 3); at += V * 12
    faces = np.frombuffer(b, '<u2', F * 3, at).reshape(F, 3); at += F * 6
    joint = np.frombuffer(b, 'u1', V * 8, at).reshape(V, 8).astype(int); at += V * 8
    weight = np.frombuffer(b, 'u1', V * 8, at).reshape(V, 8) / 255.0; at += V * 8
    inv = np.frombuffer(b, '<f4', J * 12, at).reshape(J, 3, 4).astype(np.float64); at += J * 48
    parent = np.frombuffer(b, 'u1', J, at).astype(int); parent[parent == 255] = -1
    R = np.array([I[:, :3].T for I in inv])                      # each joint's rest frame (its axes in the body's space)
    P = np.array([-(I[:, :3].T @ I[:, 3]) for I in inv])         # its rest place
    return dict(V=V, bind=bind, faces=faces, joint=joint, weight=weight, R=R, P=P, parent=parent)


def part(n):
    side = 'L' if n.startswith('Left') else 'R' if n.startswith('Right') else 'C'
    r = n[4:] if side == 'L' else n[5:] if side == 'R' else n
    kind = ('pelvis' if r == 'Hips' else 'spine' if r in ('Spine1', 'Spine2', 'Chest') else 'neck' if r in ('Neck1', 'Neck2') else
            'head' if r in ('Head', 'HeadEnd', 'Jaw') else 'eye' if r == 'Eye' else 'clavicle' if r == 'Shoulder' else 'upperArm' if r == 'Arm' else
            'foreArm' if r == 'ForeArm' else 'hand' if r == 'Hand' else 'finger' if r.startswith('Hand') else 'thigh' if r == 'Leg' else
            'shin' if r == 'Shin' else 'foot' if r == 'Foot' else 'toe')
    return side, kind


if __name__ == '__main__':
    S = load()
    assert len(NAMES) == 77
    q = Rot.from_matrix(S['R']).as_quat()                        # x, y, z, w
    out = {
        'format': 'engine/skeleton', 'version': 1, 'id': 'soma77',
        'about': 'SOMA: the skeleton NVIDIA Kimodo moves (77 joints with fingers). Rest: the T-pose a motion\'s rotations are measured '
                 'against — each joint\'s place (metres, y up, facing +z, the person\'s left +x) and frame (a quaternion x, y, z, w).',
        'floor': round(float(S['bind'][:, 1].min()), 5),   # the lowest point of SOMA's skin at rest (metres)
        'joints': [{'name': n, 'parent': int(S['parent'][j]), 'side': part(n)[0], 'part': part(n)[1],
                    'rest': [round(float(v), 6) for v in S['P'][j]], 'frame': [round(float(v), 7) for v in q[j]]} for j, n in enumerate(NAMES)],
    }
    json.dump(out, open(os.path.join(ROOT, 'data/skeleton.json'), 'w'), indent=1)
    print('skeleton.json:', len(NAMES), 'joints')
