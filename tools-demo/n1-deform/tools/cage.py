# The silhouette by a few handles with libigl's bounded biharmonic weights (Jacobson et al. 2011), against our 6×14×5
# B-spline lattice (experiments/form-tools, cageOf). Handles: rings of skin across the body at the heights of the
# lattice's profile (ankles, knees, hips, waist, chest, armpits, neck) plus the head and the two hands. Each ring gets
# the very scale our preset gives at its height (width, depth, shift forward), the hands ride with the shoulder as ours
# do; igl.bbw spreads the handles over the surface, linear blend skinning applies them.
import numpy as np, igl, time
from common import *
f = F(); NU = f.max() + 1
v0 = V('ft_disney'); Jd = J('ft_disney').reshape(-1, 3); V0 = v0[:NU]
CAGES = {  # experiments/form-tools/index.html, CAGES — [height 0..1, width, depth, forward shift in heights]
  'pear':      [[0, 1, 1, 0], [0.25, 1.06, 1.04, 0], [0.47, 1.32, 1.15, 0], [0.62, 1.04, 1, 0], [0.8, 0.84, 0.94, 0], [0.92, 1, 1, 0], [1, 1, 1, 0]],
  'wedge':     [[0, 0.94, 1, 0], [0.3, 0.92, 0.98, 0], [0.5, 0.88, 0.95, 0], [0.62, 1.02, 1.05, 0], [0.78, 1.32, 1.16, 0], [0.9, 1.04, 1, 0], [1, 1, 1, 0]],
  'hourglass': [[0, 1, 1, 0], [0.3, 1.04, 1, 0], [0.47, 1.16, 1.06, 0], [0.61, 0.78, 0.84, 0], [0.76, 1.14, 1.1, 0], [0.9, 1, 1, 0], [1, 1, 1, 0]],
  'egg':       [[0, 0.88, 0.9, 0], [0.3, 0.94, 0.98, 0], [0.56, 1.34, 1.38, 0.01], [0.72, 1.16, 1.16, 0], [0.86, 0.94, 1, 0], [1, 1, 1, 0]],
}
AMT = {'hourglass': 0.8, 'pear': 1, 'egg': 1, 'wedge': 1}
sst = lambda t: t * t * (3 - 2 * t)
def profile(keys, v):
    if v <= keys[0][0]: return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if v <= b[0]: u = sst((v - a[0]) / (b[0] - a[0])); return [a[c] + (b[c] - a[c]) * u for c in (1, 2, 3)]
    return keys[-1][1:]
lo, hi = V0.min(0), V0.max(0); H = hi[1] - lo[1]; cx, cz = Jd[JI['Hips']][0], Jd[JI['Hips']][2]
vh = (V0[:, 1] - lo[1]) / H
armW = weight_of(r'^(Left|Right)(Arm|ForeArm|Hand)')[:NU]
handW = weight_of(r'^(Left|Right)Hand')[:NU]
LEVELS = [0.04, 0.27, 0.47, 0.61, 0.76, 0.84, 0.9]
handles = []
for lv in LEVELS: handles.append(('ring', lv, np.where((abs(vh - lv) < 0.003) & (armW < 0.02))[0]))
handles.append(('head', 1.0, np.where(vh > 0.96)[0]))
for s in (1, -1): handles.append(('hand', s, np.where((handW > 0.95) & (np.sign(V0[:, 0] - cx) == s))[0]))
for h in handles: print(h[0], h[1], len(h[2]))
b = np.concatenate([h[2] for h in handles]); bc = np.zeros((len(b), len(handles)))
o = 0
for k, h in enumerate(handles): bc[o:o + len(h[2]), k] = 1; o += len(h[2])
t = time.time()
W = igl.bbw(V0, f, b.astype(np.int64), bc, partition_unity=False, max_iter=8)
W = W / W.sum(1, keepdims=True); print('bbw', time.time() - t, 's')
np.save(f'{OUT}/bbw_W.npy', W)
for name, keys in CAGES.items():
    amt = AMT[name]
    def T(v):  # the affine map our preset gives at height v
        w, d, fw = profile(keys, v); w, d = 1 + (w - 1) * amt, 1 + (d - 1) * amt
        A = np.diag([w, 1, d]); t = np.array([cx * (1 - w), 0, cz * (1 - d) + fw * amt * H]); return A, t
    sh = Jd[JI['LeftArm']]; vsh = (sh[1] - lo[1]) / H
    out = np.zeros_like(V0)
    for k, h in enumerate(handles):
        if h[0] == 'ring': A, t = T(h[1])
        elif h[0] == 'head': A, t = np.eye(3), np.zeros(3)
        else:  # a hand: carried by the shoulder's displacement, not scaled
            A, t0 = T(vsh); p = Jd[JI['LeftArm' if h[1] > 0 else 'RightArm']]; t = A @ p + t0 - p; A = np.eye(3)
        out += W[:, k:k + 1] * (V0 @ A.T + t)
    res = v0.copy(); res[:NU] = out; save('cage_bbw_' + name, res)
    print(name, 'max |ours - bbw| mm', 1000 * np.abs(V('ft_cage_' + name)[:NU] - out).max())
