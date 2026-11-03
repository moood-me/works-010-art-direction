# The face by points with libigl: the same ~20 landmarks as experiments/form-tools (landmarksOf, ported line by line)
# moved by exactly the displacement our tool gave them; the rest of the head by igl.harmonic (k=2: biharmonic,
# on the surface), the neck and the body below held still. Also ARAP with the same points, for comparison.
import numpy as np, igl, scipy.sparse as sp
from common import *
f = F(); NU = f.max() + 1
v0 = V('ft_disney'); Jd = J('ft_disney').reshape(-1, 3)
headW = weight_of(r'^(Head|HeadEnd|Jaw|LeftEye|RightEye)$')
def landmarks(pos, J):
    eL, eR = J[JI['LeftEye']], J[JI['RightEye']]; e = (eL + eR) / 2; g = np.linalg.norm(eL - eR); h = max(0.05, J[JI['HeadEnd']][1] - J[JI['Head']][1])
    head = np.array([i for i in range(NU) if headW[i] > 0.6]); P = pos[head]
    def best(ok, score):
        m = ok(P); 
        if not m.any(): return -1
        s = np.where(m, score(P), -np.inf); return head[int(np.argmax(s))]
    front = lambda x, y, rx, ry: best(lambda p: (abs(p[:, 0] - x) < rx) & (abs(p[:, 1] - y) < ry), lambda p: p[:, 2])
    L = {}
    L['nose'] = best(lambda p: (abs(p[:, 0] - e[0]) < 0.2 * g) & (p[:, 1] < e[1] - 0.05 * h) & (p[:, 1] > e[1] - 0.5 * h), lambda p: p[:, 2])
    ny = pos[L['nose'], 1]
    L['chin'] = best(lambda p: (abs(p[:, 0] - e[0]) < 0.25 * g) & (p[:, 2] > e[2] - 0.3 * h) & (p[:, 1] < ny), lambda p: -p[:, 1])
    cy = pos[L['chin'], 1]; my = ny + 0.42 * (cy - ny)
    L['browC'] = front(e[0], e[1] + 0.13 * h, 0.12 * g, 0.04 * h)
    L['top'] = best(lambda p: np.ones(len(p), bool), lambda p: p[:, 1])
    L['back'] = best(lambda p: (abs(p[:, 0] - e[0]) < 0.2 * g) & (abs(p[:, 1] - e[1]) < 0.06 * h), lambda p: -p[:, 2])
    for s, sx in (('L', 1), ('R', -1)):
        eye = eL if sx > 0 else eR
        L['mouth' + s] = front(e[0] + sx * 0.42 * g, my, 0.1 * g, 0.05 * h)
        L['cheek' + s] = front(e[0] + sx * 0.9 * g, e[1] - 0.22 * h, 0.12 * g, 0.06 * h)
        L['brow' + s] = front(e[0] + sx * 0.75 * g, e[1] + 0.1 * h, 0.1 * g, 0.05 * h)
        L['eyeOut' + s] = front(eye[0] + sx * 0.38 * g, eye[1], 0.08 * g, 0.04 * h)
        L['eyeIn' + s] = front(eye[0] - sx * 0.3 * g, eye[1], 0.08 * g, 0.04 * h)
        jp = np.array([e[0] + sx * 1.0 * g, cy + 0.18 * h, e[2] - 0.45 * h])
        L['jaw' + s] = best(lambda p: np.ones(len(p), bool), lambda p: -((p - jp) ** 2).sum(1))
        L['temple' + s] = best(lambda p: (abs(p[:, 1] - (e[1] + 0.2 * h)) < 0.05 * h) & ((p[:, 0] - e[0]) * sx > 0), lambda p: (p[:, 0] - e[0]) * sx)
    return {k: int(i) for k, i in L.items() if i >= 0}
L = landmarks(v0, Jd)
lm = np.array(sorted(set(L.values())))
np.save(f'{OUT}/landmarks.npy', lm)
print(len(L), 'landmarks')
y0 = Jd[JI['Neck1']][1]
fixed = np.where(v0[:NU, 1] < y0)[0]          # the neck from its base down: still, as in ours
V0 = v0[:NU]
for name in ['elf', 'anime', 'burton', 'pixar', 'hero']:
    ours = V('ft_face_' + name)
    d = ours[lm] - v0[lm]
    b = np.concatenate([lm, fixed]); bc = np.concatenate([d, np.zeros((len(fixed), 3))])
    D = igl.harmonic(V0, f, b.astype(np.int64), bc, 2)
    out = v0.copy(); out[:NU] += D; save('face_bih_' + name, out)
    # ARAP needs handle regions, not single points (single points pull out spikes): each landmark with the skin
    # within 6 mm of it, moved by the landmark's displacement; the neck still
    reg, rd = [], []
    for i, di in zip(lm, d):
        near = np.where(np.linalg.norm(V0 - V0[i], axis=1) < 0.006)[0]; reg.append(near); rd.append(np.repeat(di[None], len(near), 0))
    reg = np.concatenate(reg); rd = np.concatenate(rd); reg, ui = np.unique(reg, return_index=True); rd = rd[ui]
    ba = np.concatenate([reg, fixed]); bca = np.concatenate([rd, np.zeros((len(fixed), 3))])
    data = igl.ARAPData(); data.max_iter = 30
    igl.arap_precomputation(V0, f, 3, ba.astype(np.int32), data)
    U = igl.arap_solve(V0[ba] + bca, data, V0 + D)
    out2 = v0.copy(); out2[:NU] = U; save('face_arap_' + name, out2)
    print(name, 'max |ours-bih| mm', 1000 * np.abs(ours[:NU] - out[:NU]).max())
