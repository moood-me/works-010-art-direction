# Measures a run's garments from each simulator the same way: how many cloth points are inside the body (deeper than
# 2 mm under the nearest skin point, along its normal — as sim.js's inside() counts) and how much the cloth is
# stretched (edge lengths against the dressed rest shape). python3 measure.py <run dir> ours blender hood
import sys, os, json
import numpy as np
from scipy.spatial import cKDTree

run, srcs = sys.argv[1], sys.argv[2:]
info = json.load(open(os.path.join(run, 'run.json'))); N = info['N']
body = np.fromfile(os.path.join(run, 'body.f32'), np.float32).reshape(-1, N, 3)
bt = np.fromfile(os.path.join(run, 'bodytris.u32'), np.uint32).reshape(-1, 3)

def normals(p):
    n = np.zeros_like(p); fn = np.cross(p[bt[:, 1]] - p[bt[:, 0]], p[bt[:, 2]] - p[bt[:, 0]])
    for k in range(3): np.add.at(n, bt[:, k], fn)
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)

out = {}
for g in info['garments']:
    name, n = g['name'], g['n']
    tris = np.fromfile(os.path.join(run, f'{name}-tris.u32'), np.uint32).reshape(-1, 3)
    rest = np.fromfile(os.path.join(run, f'{name}-rest.f32'), np.float32).reshape(n, 3)
    E = np.unique(np.sort(np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]]), 1), axis=0)
    L0 = np.linalg.norm(rest[E[:, 0]] - rest[E[:, 1]], axis=1)
    for s in srcs:
        p = os.path.join(run, f'{s}-{name}.f32')
        if not os.path.exists(p): continue
        X = np.fromfile(p, np.float32).reshape(-1, n, 3); F = min(len(X), len(body))
        inside, stretch = [], []
        for f in range(0, F, 2):
            B = body[f]; nb = normals(B); d, j = cKDTree(B).query(X[f])
            depth = np.einsum('ij,ij->i', X[f] - B[j], nb[j])
            inside.append(float(np.mean(depth < -0.002)) * 100)
            L = np.linalg.norm(X[f][E[:, 0]] - X[f][E[:, 1]], axis=1); stretch.append(float(np.mean(L / L0)))
        out.setdefault(name, {})[s] = {'inside_mean_pct': round(float(np.mean(inside)), 2), 'inside_max_pct': round(float(np.max(inside)), 2),
                                       'stretch_mean_pct': round((float(np.mean(stretch)) - 1) * 100, 1), 'stretch_max_pct': round((float(np.max(stretch)) - 1) * 100, 1)}
json.dump(out, open(os.path.join(run, 'measure.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
