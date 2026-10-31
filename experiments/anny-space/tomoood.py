# carry Anny shapes (out/<name>.bin) onto moood's mesh: out/m-<name>.bin, out/mfaces.bin
import sys, numpy as np
M = np.load('map.npz'); t, bc, off, F = M['t'], M['bc'], M['off'], M['F']
shift = np.load('shift.npy')
B = open('/home/user/moood/engines/1/bodies/base.bin', 'rb').read()
T = np.frombuffer(B, np.uint32, 2, 0)[1]; mt = np.frombuffer(B, np.uint16, T * 3, 8); mt.tofile('out/mfaces.bin')
# moood's surface takes Anny's surface as it is (her offsets would print the adult woman's features onto any new face);
# the points off the surface (eyes and mouth inside) keep their place relative to it
surf = np.zeros(len(t), bool); surf[np.unique(mt)] = True
off = off * (~surf)[:, None]
for name in sys.argv[1:]:
    P = np.fromfile(f'out/{name}.bin', np.float32).reshape(-1, 3).astype(np.float64) + shift
    a, b, c = P[F[t, 0]], P[F[t, 1]], P[F[t, 2]]
    e1 = b - a; e1 /= np.linalg.norm(e1, axis=1, keepdims=True) + 1e-12
    n = np.cross(b - a, c - a); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    e2 = np.cross(n, e1)
    q = bc[:, :1] * a + bc[:, 1:2] * b + bc[:, 2:] * c
    v = q + off[:, :1] * e1 + off[:, 1:2] * e2 + off[:, 2:] * n
    v[:, 1] -= v[:, 1].min()
    v.astype(np.float32).tofile(f'out/m-{name}.bin')
