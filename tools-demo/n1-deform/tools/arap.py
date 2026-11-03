# Limbs bent into arcs with libigl ARAP (as-rigid-as-possible, Sorkine & Alexa 2007) on the posed Anny woman, against
# our deform() in experiments/lines. The same targets for both: the body, the hands and feet stay where ours leaves
# them, the elbow and knee rings go exactly where our arc puts them; ARAP decides everything between.
import numpy as np, igl
from common import *
f0 = F(); NU = f0.max() + 1
base = V('ln_base')
V0, f, SVI, SVJ = merged(base[:NU], f0)          # the 4 zero-area triangles at the mouth corner (see common.merged)
def w(rx): return weight_of(rx)[:NU]
limb = w(r'^(Left|Right)(Shoulder|Arm|ForeArm|Hand|Leg|Shin|Foot|Toe)')
def ring(a, bn): return (w('^' + a + '$') > 0.3) & (w('^' + bn + '$') > 0.3)
for name in ['arc05', 'arc1']:
    ours = V('ln_' + name)[:NU]
    sel = (limb < 0.02)
    for s in ('Left', 'Right'):
        sel |= ring(s + 'Arm', s + 'ForeArm') | ring(s + 'Leg', s + 'Shin')
        sel |= w('^' + s + 'Hand') > 0.95
        sel |= w('^' + s + '(Foot|Toe)') > 0.95
    b = np.unique(SVJ[np.where(sel)[0]])          # merged indices
    bc = np.zeros((len(V0), 3)); bc[SVJ] = ours; bc = bc[b]
    data = igl.ARAPData(); data.max_iter = 60
    igl.arap_precomputation(V0, f, 3, b.astype(np.int32), data)
    U = igl.arap_solve(bc, data, V0)
    out = base.copy(); out[:NU] = U[SVJ]; save('arap_' + name, out)
    # the girth along the upper arm: ours shears it, ARAP keeps its sections
    print(name, len(b), 'handles; max |ours-arap| mm', 1000 * np.abs(out[:NU] - ours).max())
