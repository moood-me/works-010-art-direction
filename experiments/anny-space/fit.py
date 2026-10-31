# fit Anny's phenotype to moood's woman, then map moood's vertices onto Anny's surface (triangle + barycentrics + normal offset)
import numpy as np, torch, anny, json
from scipy.spatial import cKDTree
m = anny.Anny(phenotypes="all", local_changes="default", extrapolate_phenotypes=True).to(dtype=torch.float32)
F = m.faces.numpy().astype(np.int64)
N = 13814
tgt = np.fromfile('/home/user/moood/engines/1/bodies/woman.bin', np.int16, N * 3).reshape(-1, 3) / 1e4
B = open('/home/user/moood/engines/1/bodies/base.bin', 'rb').read()
T = np.frombuffer(B, np.uint32, 2, 0)[1]; mt = np.frombuffer(B, np.uint16, T * 3, 8).reshape(-1, 3)
used = np.unique(mt)
tg = torch.tensor(tgt[used], dtype=torch.float32)
labels = m.phenotype_labels
x = {k: torch.tensor([v], requires_grad=True) for k, v in dict(gender=1.0, age=0.69, muscle=0.5, weight=0.5, height=0.3, proportions=0.5, cupsize=0.5, firmness=0.5).items()}
def anny_pts():
    v = m(phenotype_kwargs=x)['vertices'][0]
    v = torch.stack([v[:, 0], v[:, 2], -v[:, 1]], 1)
    return v - torch.tensor([0, 1, 0.]) * v[:, 1].min()
opt = torch.optim.Adam([x[k] for k in x if k != 'gender'], lr=0.02)
shift = torch.zeros(3, requires_grad=True); opt.add_param_group({'params': [shift], 'lr': 0.003})
for it in range(60):
    v = anny_pts() + shift
    with torch.no_grad(): idx = cKDTree(v.numpy()).query(tg.numpy())[1]; idx2 = cKDTree(tg.numpy()).query(v.numpy())[1]
    loss = ((v[idx] - tg) ** 2).sum(1).mean() + ((tg[idx2] - v) ** 2).sum(1).mean()
    opt.zero_grad(); loss.backward(); opt.step()
    if it % 10 == 0 or it == 59: print(it, float(loss) ** 0.5 * 1000, {k: round(float(x[k]), 3) for k in x}, shift.detach().numpy().round(4))
json.dump({k: float(x[k]) for k in x}, open('woman_ph.json', 'w'))
with torch.no_grad(): A = (anny_pts() + shift).numpy()
np.save('anny_woman.npy', A); np.save('shift.npy', shift.detach().numpy())
# closest point on Anny's surface for each moood vertex
cent = A[F].mean(1); kd = cKDTree(cent)
def closest_on_tri(p, a, b, c):
    # Ericson's closest point on triangle, vectorised over rows
    ab, ac, ap = b - a, c - a, p - a
    d1, d2 = (ab * ap).sum(1), (ac * ap).sum(1)
    bp = p - b; d3, d4 = (ab * bp).sum(1), (ac * bp).sum(1)
    cp = p - c; d5, d6 = (ab * cp).sum(1), (ac * cp).sum(1)
    va = d3 * d6 - d5 * d4; vb = d5 * d2 - d1 * d6; vc = d1 * d4 - d3 * d2
    den = va + vb + vc; den[den == 0] = 1e-12
    v = vb / den; w = vc / den; u = 1 - v - w
    bc = np.stack([u, v, w], 1)
    # clamp to the triangle by projecting barycentrics, then renormalise (good enough near the surface)
    bc = np.clip(bc, 0, None); bc /= bc.sum(1, keepdims=True)
    q = bc[:, :1] * a + bc[:, 1:2] * b + bc[:, 2:] * c
    return q, bc
best_t = np.zeros(N, np.int64); best_bc = np.zeros((N, 3)); best_d = np.full(N, 1e9)
_, cand = kd.query(tgt, k=12)
for j in range(12):
    t = cand[:, j]; q, bc = closest_on_tri(tgt, A[F[t, 0]], A[F[t, 1]], A[F[t, 2]])
    d = np.linalg.norm(tgt - q, axis=1); better = d < best_d
    best_d[better] = d[better]; best_t[better] = t[better]; best_bc[better] = bc[better]
# normal frame offset: keep the residual in the triangle's local frame so it follows the shape
def frames(P):
    a, b, c = P[F[best_t, 0]], P[F[best_t, 1]], P[F[best_t, 2]]
    e1 = b - a; e1 /= np.linalg.norm(e1, axis=1, keepdims=True) + 1e-12
    n = np.cross(b - a, c - a); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    e2 = np.cross(n, e1)
    q = best_bc[:, :1] * a + best_bc[:, 1:2] * b + best_bc[:, 2:] * c
    return q, e1, e2, n
q, e1, e2, n = frames(A)
r = tgt - q; off = np.stack([(r * e1).sum(1), (r * e2).sum(1), (r * n).sum(1)], 1)
np.savez('map.npz', t=best_t, bc=best_bc, off=off, F=F)
iu = np.zeros(N, bool); iu[used] = True
print('residual mm: surface verts mean %.1f p95 %.1f max %.1f; isolated verts mean %.1f' % (best_d[iu].mean() * 1e3, np.percentile(best_d[iu], 95) * 1e3, best_d[iu].max() * 1e3, best_d[~iu].mean() * 1e3))
