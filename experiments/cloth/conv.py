# A Kimodo motion from the studio (motion(key, data: "body") → {n, fps, names, q, p}) as the cloth page plays it:
# the same as experiments/indie/conv.py (each joint's turn from SOMA's rest, the pelvis's place, the feet's height),
# and the height of SOMA's lowest point each frame (its whole skin, posed) — so a body lying, rolling or sitting lies
# on the floor, not only one standing on its feet.
import json, base64, struct, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot
sys.path.insert(0, '/home/user/works-010-art-direction/experiments/indie')
import conv as indie

b = open('/home/user/moood/engines/1/soma.bin', 'rb').read()
V, F, J = struct.unpack('<3I', b[:12]); at = 12
bind = np.frombuffer(b[at:at + V * 12], dtype='<f4').reshape(V, 3); at += V * 12 + F * 6
joint = np.frombuffer(b[at:at + V * 8], dtype=np.uint8).reshape(V, 8).astype(int); at += V * 8
weight = np.frombuffer(b[at:at + V * 8], dtype=np.uint8).reshape(V, 8) / 255.0

def lowest(q, p):
    # the posed skin: each point by its joints, x' = D (x - rest) + place
    N = q.shape[0]; out = np.zeros(N)
    for f in range(N):
        R = Rot.from_quat(q[f]).as_matrix() @ indie.RB.transpose(0, 2, 1)          # (77, 3, 3)
        T = p[f] / 1000.0 - np.einsum('jab,jb->ja', R, indie.REST)                   # (77, 3)
        y = np.zeros(V)
        for k in range(8):
            j = joint[:, k]; w = weight[:, k]
            y += w * (np.einsum('vb,vb->v', R[j, 1, :], bind) + T[j, 1])
        out[f] = y.min()
    return out

def convert(src, out):
    indie.convert(src, out)
    d, q, p = indie.load(src)
    m = json.load(open(out))
    m['low'] = [round(float(v), 4) for v in lowest(q, p)]
    json.dump(m, open(out, 'w'))

if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])
