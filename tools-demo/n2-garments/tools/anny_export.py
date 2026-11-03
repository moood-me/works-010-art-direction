"""Export an engine body (Anny as moood bakes it) for GarmentCode: mesh .obj in metres, part segmentation."""
import json, sys, numpy as np
from pathlib import Path
R = Path('/home/user/works-010-art-direction/engine/data')
def pack(p):
    h = json.load(open(p)); b = open(p.parent / h['bin'], 'rb').read(); out = {}
    for k, a in h['arrays'].items():
        n = int(np.prod(a['shape'])); dt = np.dtype(a['dtype'])
        out[k] = np.frombuffer(b, dt, n, a['offset']).reshape(a['shape'])
    return h, out
who = sys.argv[1] if len(sys.argv) > 1 else 'moood-woman'
out = Path(sys.argv[2] if len(sys.argv) > 2 else '/home/user/cache/n2-garments/bodies/anny')
hb, B = pack(R / 'bodies' / f'{who}.json')
ht, T = pack(R / 'topology' / 'anny-moood.json')
P, F, parts = B['positions'].astype(np.float64), T['triangles'].astype(np.int64), T['parts']
used = np.zeros(len(P), bool); used[F.ravel()] = True
print('verts', len(P), 'used', used.sum(), 'tris', len(F), 'bbox', P[used].min(0), P[used].max(0))
# keep only the vertices the triangles use (eyes etc. are separate), and move the body into GarmentCode's frame:
# x centred, the waist's centre at GarmentCode's mean body's waist centre z (0.036 m), feet on y = 0
idx = np.flatnonzero(used); remap = -np.ones(len(P), int); remap[idx] = np.arange(len(idx))
F = remap[F]; P = P[idx]; parts = parts[idx]
wy = 0.62 * P[:, 1].max(); band = P[np.abs(P[:, 1] - wy) < 0.01]
shift = np.array([0.0, -P[:, 1].min(), 0.036 - (band[:, 2].min() + band[:, 2].max()) / 2])
P = P + shift
print('shift', shift)
names = ht['parts']; top = parts.argmax(1)
lab = np.array([names[i] for i in top])
seg = {'body': [], 'left_arm': [], 'right_arm': [], 'left_leg': [], 'right_leg': [], 'face_internal': []}
for i in range(len(P)):
    n = lab[i]
    if n in ('LupperArm', 'LforeArm', 'Lhand'): seg['left_arm'].append(i)
    elif n in ('RupperArm', 'RforeArm', 'Rhand'): seg['right_arm'].append(i)
    elif n in ('Lthigh', 'Lshin', 'Lfoot'): seg['left_leg'].append(i)
    elif n in ('Rthigh', 'Rshin', 'Rfoot'): seg['right_leg'].append(i)
    else: seg['body'].append(i)
for k, v in seg.items(): print(k, len(v))
out.mkdir(parents=True, exist_ok=True)
json.dump(seg, open(out / 'ggg_body_segmentation.json', 'w'))
with open(out / f'{who}.obj', 'w') as f:
    for p in P: f.write(f'v {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n')
    for t in F + 1: f.write(f'f {t[0]} {t[1]} {t[2]}\n')
np.save(out / f'{who}_joints.npy', B['joints'] + shift)
json.dump({'engine_vertex_ids': idx.tolist(), 'shift_m': shift.tolist(), 'body': who}, open(out / f'{who}_map.json', 'w'))
