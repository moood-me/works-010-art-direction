# libigl in the uses it was made for (not ours), on the raw Anny woman at rest:
#  1. ARAP "puppet": a few pins dragged, the shape keeps its form (frames for a film + a still against the naive way);
#  2. bounded biharmonic weights: an automatic rig for a few handles, weights as colour, then the handles moved;
#  3. smoothing a noisy surface (as from a 3D scan) with the cotangent Laplacian;
#  4. heat geodesics: distance measured along the skin from one point.
import numpy as np, igl, os, scipy.sparse.linalg as sla
from common import *
f0 = F(); NU = f0.max() + 1; v0 = V('raw_woman')
V0, f, SVI, SVJ = merged(v0[:NU], f0)
nV = len(V0)
def back(U): out = v0.copy(); out[:NU] = U[SVJ]; return out
def wm(rx): x = np.zeros(nV); x[SVJ] = weight_of(rx)[:NU]; return x
def lin(c): c = np.asarray(c, float); return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)   # colours are given in sRGB
def savec(name, C): out = np.ones((len(v0), 3)) * 0.5; out[:NU] = C[SVJ]; save(name, out)
os.makedirs(f'{OUT}/frames', exist_ok=True)

# ——— 1. ARAP puppet: feet pinned, the left hand dragged over the head, the head pulled a little aside ———
feet = np.where(wm(r'^(Left|Right)(Foot|Toe)') > 0.9)[0]
hand = np.where(wm(r'^LeftHand') > 0.9)[0]
head = np.where(wm(r'^(Head|HeadEnd|Jaw|LeftEye|RightEye)$') > 0.95)[0]
b = np.concatenate([feet, hand, head])
goal_hand = np.array([0.12, 1.92, 0.05]) - V0[hand].mean(0)
goal_head = np.array([-0.10, -0.03, 0.0])
data = igl.ARAPData(); data.max_iter = 20
igl.arap_precomputation(V0, f, 3, b.astype(np.int32), data)
U = V0.copy(); n = 48
for k in range(n + 1):
    s = 0.5 - 0.5 * np.cos(np.pi * k / n)
    bc = np.concatenate([V0[feet], V0[hand] + s * goal_hand, V0[head] + s * goal_head])
    U = igl.arap_solve(bc, data, U); save(f'frames/puppet_{k:03d}', back(U))
save('use_arap', back(U))
# the naive way for the same pins: the smoothest displacement (biharmonic), no notion of rotation
bc = np.concatenate([np.zeros((len(feet), 3)), np.repeat(goal_hand[None], len(hand), 0), np.repeat(goal_head[None], len(head), 0)])
save('use_naive', back(V0 + igl.harmonic(V0, f, b.astype(np.int64), bc, 2)))
print('puppet done')

# ——— 2. bounded biharmonic weights: an automatic rig ———
def region(rx, thr=0.9): return np.where(wm(rx) > thr)[0]
H = [('head', region(r'^(Head|HeadEnd|Jaw|LeftEye|RightEye)$', 0.95)), ('chest', region(r'^Chest$', 0.8)), ('hips', region(r'^Hips$', 0.8)),
     ('elbowL', region(r'^LeftForeArm$', 0.45) [:0]), ]
H = [h for h in H if len(h[1])]
def ring(a, bname): x = wm('^' + a + '$'); y = wm('^' + bname + '$'); return np.where((x > 0.35) & (y > 0.35))[0]
for s in ('Left', 'Right'):
    H += [('elbow' + s, ring(s + 'Arm', s + 'ForeArm')), ('hand' + s, region('^' + s + 'Hand', 0.9)), ('knee' + s, ring(s + 'Leg', s + 'Shin')), ('foot' + s, region('^' + s + '(Foot|Toe)', 0.9))]
for h in H: print(h[0], len(h[1]))
bb = np.concatenate([h[1] for h in H]); bcw = np.zeros((len(bb), len(H))); o = 0
for k, h in enumerate(H): bcw[o:o + len(h[1]), k] = 1; o += len(h[1])
W = igl.bbw(V0, f, bb.astype(np.int64), bcw, partition_unity=False, max_iter=10); W = np.clip(W, 0, 1); W /= W.sum(1, keepdims=True)
PAL = lin([[0.85, 0.33, 0.31], [0.95, 0.75, 0.3], [0.45, 0.7, 0.4], [0.3, 0.55, 0.85], [0.6, 0.4, 0.8], [0.25, 0.75, 0.75], [0.9, 0.5, 0.7],
           [0.95, 0.6, 0.25], [0.5, 0.8, 0.9], [0.75, 0.85, 0.35], [0.55, 0.45, 0.35]][:len(H)])
savec('use_bbw_colors', W @ PAL)
# the rig used: rotations about the handles' own centres, as a person would pose it
def R(axis, deg):
    a = np.radians(deg); axis = np.asarray(axis, float) / np.linalg.norm(axis); K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * K @ K
c = {h[0]: V0[h[1]].mean(0) for h in H}
shL = V0[np.where(wm(r'^LeftArm$') > 0.5)[0]].mean(0) * [1, 1, 1]
T = {h[0]: (np.eye(3), np.zeros(3)) for h in H}
def about(Rm, p): return Rm, p - Rm @ p
Rup = R([0, 0, 1], 75)                        # the left arm raised about the shoulder
T['elbowLeft'] = about(Rup, shL); T['handLeft'] = (lambda A, t: (R([0, 0, 1], 50) @ A, R([0, 0, 1], 50) @ t + (Rup @ c['elbowLeft'] + T['elbowLeft'][1]) - R([0, 0, 1], 50) @ (Rup @ c['elbowLeft'] + T['elbowLeft'][1])))(*about(Rup, shL))
Rf = R([1, 0, 0], -100)                       # the right forearm bent forward about the elbow
T['handRight'] = about(Rf, c['elbowRight'])
hipL = V0[np.where(wm(r'^LeftLeg$') > 0.5)[0]].mean(0); hipL[1] = c['hips'][1]
Rk = R([1, 0, 0], -40)                        # the left leg kicked forward about the hip
T['kneeLeft'] = about(Rk, hipL); T['footLeft'] = about(Rk, hipL)
P = sum(W[:, k:k + 1] * (V0 @ T[h[0]][0].T + T[h[0]][1]) for k, h in enumerate(H))
save('use_bbw_posed', back(P)); savec('use_bbw_posed_colors', W @ PAL)
print('bbw done')

# ——— 3. a noisy surface smoothed ———
rng = np.random.default_rng(1)
N = igl.per_vertex_normals(V0, f)
noisy = V0 + N * rng.normal(0, 0.0015, (nV, 1))
L = igl.cotmatrix(V0, f); M = igl.massmatrix(noisy, f, igl.MASSMATRIX_TYPE_BARYCENTRIC)
clean = sla.spsolve((M - 0.00002 * L).tocsc(), M @ noisy)
save('use_noisy', back(noisy)); save('use_denoised', back(clean))
print('denoise done')

# ——— 4. heat geodesics from the tip of the left middle finger ———
src = np.where(wm(r'^LeftHandMiddle(3|4|End)') > 0.5)[0]
tip = src[np.argmax(V0[src, 0])]
hg = igl.heat_geodesics_precompute(V0, f) if False else None
d = None
try:
    data_h = igl.HeatGeodesicsData(); igl.heat_geodesics_precompute(V0, f, data_h); d = igl.heat_geodesics_solve(data_h, np.array([tip], dtype=np.int64))
except Exception as e: print('heat api', e)
d = np.asarray(d).ravel(); d -= d.min()
band = 0.5 + 0.5 * np.cos(2 * np.pi * d / 0.05)
u = np.clip(d / d.max(), 0, 1)[:, None]
base_c = lin([0.95, 0.78, 0.45]) * (1 - u) + lin([0.35, 0.45, 0.75]) * u
savec('use_geo_colors', base_c * (0.55 + 0.45 * band[:, None]))
print('geodesic max m', d.max())
