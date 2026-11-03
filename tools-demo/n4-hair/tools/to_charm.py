# A hairstyle of build.py as a hair point cloud in CHARM's format (what HairDeck's point-cloud model takes): 10,000
# points on the evaluated hair curves with normals (out from the skull, across the strand), moved into CHARM's dataset
# frame: our fitted skull centre onto the mean skull centre of CHARM's test characters (head_params_test.json), scaled
# so the hair's top stands as high above it as there (the dataset puts the hair's top at y = 0.5), the face toward +Z.
# blender -b --factory-startup -P to_charm.py -- <style> <out.ply> <head_params_test.json>
import bpy, sys, json
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import scene as S, build

argv = sys.argv[sys.argv.index('--') + 1:]
name, out, hp = argv[0], argv[1], argv[2]
H = build.make(name)
dg = bpy.context.evaluated_depsgraph_get()
P, T = [], []
for h in H['hairs']:
    e = h.evaluated_get(dg).data
    Q = np.zeros(len(e.points) * 3, np.float32); e.points.foreach_get('position', Q); Q = Q.reshape(-1, 3)
    off = np.array([c.first_point_index for c in e.curves] + [len(Q)])
    for a, b in zip(off[:-1], off[1:]):
        q = Q[a:b]; t = np.gradient(q, axis=0); P.append(q); T.append(t)
P = np.concatenate(P); T = np.concatenate(T)
P = np.stack([P[:, 0], P[:, 2], -P[:, 1]], -1); T = np.stack([T[:, 0], T[:, 2], -T[:, 1]], -1)   # Blender -> three axes
T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
c = H['c']
n = P - c; n -= (n * T).sum(1, keepdims=True) * T; n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
pick = np.random.default_rng(0).choice(len(P), 10000, replace=False)
P, n = P[pick], n[pick]
params = [v for v in json.load(open(hp)).values() if v.get('status') == 'ok']
o = np.mean([v['o'] for v in params], 0); top = np.mean([v['hair_hi'][1] for v in params])
k = (top - o[1]) / (P[:, 1].max() - c[1])
X = (P - c) * k + o
print('scale', k, 'extent', X.min(0).round(3), X.max(0).round(3))
dt = np.dtype([('p', '<f8', 6), ('c', 'u1', 3)])
rec = np.zeros(len(X), dt); rec['p'] = np.c_[X, n]; rec['c'] = 128
hdr = f'ply\nformat binary_little_endian 1.0\nelement vertex {len(X)}\n' + ''.join(f'property double {a}\n' for a in ['x', 'y', 'z', 'nx', 'ny', 'nz']) + \
      ''.join(f'property uchar {a}\n' for a in ['red', 'green', 'blue']) + 'end_header\n'
open(out, 'wb').write(hdr.encode() + rec.tobytes())
json.dump(dict(c=list(map(float, c)), k=float(k), o=list(map(float, o)), style=name), open(out[:-4] + '.json', 'w'))
