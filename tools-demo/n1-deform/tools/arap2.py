# ARAP along the whole arc: besides the body, hands and feet, rings of skin across each limb at 35, 50 and 65 % of its
# length are carried rigidly onto our arc — their centre where ours puts it, turned to follow the arc's direction
# there (ours only shifts them). ARAP fills in between, keeping the limb's own forms and girth.
import numpy as np, igl
from common import *
f0 = F(); NU = f0.max() + 1
base = V('ln_base'); V0, f, SVI, SVJ = merged(base[:NU], f0)
def w(rx): return weight_of(rx)[:NU]
limb = w(r'^(Left|Right)(Shoulder|Arm|ForeArm|Hand|Leg|Shin|Foot|Toe)')
def rot(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = a @ b
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]); return np.eye(3) + K + K @ K / (1 + c)
X = base[:NU]
for name in ['arc05', 'arc1']:
    ours = V('ln_' + name)[:NU]
    sel = limb < 0.02; tgt = ours.copy()
    for s in ('Left', 'Right'):
        for A, Bn, C, end in (('Arm', 'ForeArm', 'Hand', r'Hand'), ('Leg', 'Shin', 'Foot', r'(Foot|Toe)')):
            part = w('^' + s + '(' + A + '|' + Bn + ')$') > 0.6
            cen = lambda m: X[m].mean(0)
            a = cen((w('^' + s + A + '$') > 0.3) & (limb > 0.3) & (w('^' + s + A + '$') < 0.7))   # where the limb leaves the body
            mid = cen((w('^' + s + A + '$') > 0.3) & (w('^' + s + Bn + '$') > 0.3))
            b = cen((w('^' + s + Bn + '$') > 0.3) & (w('^' + s + C) > 0.3))
            # each point's place t along the chain a→mid→b (0…1)
            l1, l2 = np.linalg.norm(mid - a), np.linalg.norm(b - mid)
            t1 = ((X - a) @ (mid - a)) / l1 ** 2; t2 = ((X - mid) @ (b - mid)) / l2 ** 2
            upper = w('^' + s + A + '$') >= w('^' + s + Bn + '$')
            t = np.where(upper, np.minimum(t1, 1) * l1, l1 + np.maximum(t2, 0) * l2) / (l1 + l2)
            for tk in (0.35, 0.5, 0.65):
                r = part & (abs(t - tk) < 0.02)
                if r.sum() < 6 or min((part & (abs(t - T) < 0.02)).sum() for T in (tk - 0.04, tk + 0.04)) < 6: print('skip', s, A, tk); continue
                c0, c1 = X[r].mean(0), ours[r].mean(0)
                # the arc's direction at tk from ours, by the centres of thin slabs just before and after
                def c_at(T, P): m = part & (abs(t - T) < 0.02); return P[m].mean(0)
                d0 = c_at(tk + 0.04, X) - c_at(tk - 0.04, X); d1 = c_at(tk + 0.04, ours) - c_at(tk - 0.04, ours)
                print(s, A, tk, r.sum(), np.round(1000 * (c1 - c0)), round(float(np.degrees(np.arccos(np.clip(d0 @ d1 / np.linalg.norm(d0) / np.linalg.norm(d1), -1, 1)))), 1))
                R = rot(d0, d1); tgt[r] = c1 + (X[r] - c0) @ R.T; sel |= r
            sel |= w('^' + s + end) > 0.95
    b = np.unique(SVJ[np.where(sel)[0]])
    full = np.zeros((len(V0), 3)); full[SVJ] = tgt
    data = igl.ARAPData(); data.max_iter = 60
    igl.arap_precomputation(V0, f, 3, b.astype(np.int32), data)
    U = igl.arap_solve(full[b], data, V0)
    out = base.copy(); out[:NU] = U[SVJ]; save('arapR_' + name, out)
    print(name, len(b), 'max |ours-arap| mm', 1000 * np.abs(out[:NU] - ours).max())
