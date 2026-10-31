# carry Anny shapes onto moood's mesh as a change: moood's woman + (Anny's new surface − Anny's fitted surface), smoothed
# over moood's mesh so the change is a smooth field — moood's own features ride on it. out/d-<name>.bin
import sys, numpy as np
M = np.load('map.npz'); t, bc, F = M['t'], M['bc'], M['F']
shift = np.load('shift.npy'); A0 = np.load('anny_woman.npy')
N = 13814
B = open('/home/user/moood/engines/1/bodies/base.bin', 'rb').read()
T = np.frombuffer(B, np.uint32, 2, 0)[1]; mt = np.frombuffer(B, np.uint16, T * 3, 8).reshape(-1, 3).astype(np.int64)
W0 = np.fromfile('/home/user/moood/engines/1/bodies/woman.bin', np.int16, N * 3).reshape(-1, 3) / 1e4
nb = [set() for _ in range(N)]
for a, b, c in mt: nb[a] |= {b, c}; nb[b] |= {a, c}; nb[c] |= {a, b}
rows = np.repeat(np.arange(N), [len(s) for s in nb]); cols = np.concatenate([np.fromiter(s, np.int64) for s in nb if s] or [np.array([], np.int64)])
deg = np.array([len(s) for s in nb])
from scipy.sparse import csr_matrix
L = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N))
def sample(P): return (bc[:, :1] * P[F[t, 0]] + bc[:, 1:2] * P[F[t, 1]] + bc[:, 2:] * P[F[t, 2]])
it = int(sys.argv[1]); names = sys.argv[2:]
for name in names:
    P = np.fromfile(f'out/{name}.bin', np.float32).reshape(-1, 3).astype(np.float64) + shift
    d = sample(P) - sample(A0)
    for _ in range(it):
        nd = L @ d; d = np.where(deg[:, None] > 0, 0.5 * d + 0.5 * nd / np.maximum(deg, 1)[:, None], d)
    v = W0 + d; v[:, 1] -= v[:, 1].min()
    v.astype(np.float32).tofile(f'out/d-{name}.bin')
