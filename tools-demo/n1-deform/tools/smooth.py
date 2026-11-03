# Smoothing with libigl on the raw Anny woman: igl.cotmatrix + igl.massmatrix, implicit mean-curvature flow
# (M − t·L) Uₙ₊₁ = M Uₙ, the mass matrix rebuilt each step (Kazhdan et al. 2012, "conformalized" MCF keeps L fixed).
# The total time t = R² so it reaches as far as our smoothing of reach R.
import numpy as np, igl, scipy.sparse.linalg as sla
from common import *
f0 = F(); NU = f0.max() + 1; v0 = V('raw_woman')
V0, f, SVI, SVJ = merged(v0[:NU], f0)
L = igl.cotmatrix(V0, f)
for R in (0.02, 0.04):
    U = V0.copy(); steps = 4
    for _ in range(steps):
        M = igl.massmatrix(U, f, igl.MASSMATRIX_TYPE_BARYCENTRIC)
        U = sla.spsolve((M - (R * R / steps) * L).tocsc(), M @ U)
    U += (V0.mean(0) - U.mean(0)) * np.array([1, 0, 1])   # MCF drifts the centre a little; put it back over the feet
    out = v0.copy(); out[:NU] = U[SVJ]; save(f'mcf_{int(R*100)}', out)
    # the girth each loses: mean distance to the arm's own axis, the right forearm as a sample
    print(R, 'mean shrink mm', 1000 * np.linalg.norm(U - V0, axis=1).mean())
