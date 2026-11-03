# Loads the meshes exported by export.mjs (raw float32 / int32 files)
import json, numpy as np, os
MESH = os.environ.get('N1_MESH', '/home/user/cache/n1-deform/mesh')
OUT = os.environ.get('N1_OUT', '/home/user/cache/n1-deform/out')
def F():
    return np.fromfile(f'{MESH}/tris.i4', dtype=np.int32).reshape(-1, 3).astype(np.int64)
def V(name):
    return np.fromfile(f'{MESH}/{name}.f4', dtype=np.float32).reshape(-1, 3).astype(np.float64)
def J(name):
    return V(name + '_J')
JN = json.load(open(f'{MESH}/joints.json'))
JI = {n: i for i, n in enumerate(JN)}
def skin():
    j = np.fromfile(f'{MESH}/joint.i4', dtype=np.int32).reshape(-1, 4); w = np.fromfile(f'{MESH}/weight.i4', dtype=np.int32).reshape(-1, 4) / 255.0
    return j, w
def weight_of(regex):
    import re
    j, w = skin(); ok = np.array([bool(re.search(regex, n)) for n in JN])
    return (w * ok[j]).sum(1)
def save(name, X):
    os.makedirs(OUT, exist_ok=True); X.astype(np.float32).tofile(f'{OUT}/{name}.f4')
def merged(V0, f, eps=1e-7):
    """Anny's raw mesh has 4 zero-area triangles at a mouth corner (points exactly on each other), which make the
    cotangent Laplacian NaN. libigl's own remedy: merge the coincident points (igl.remove_duplicate_vertices), drop the
    collapsed triangles, work on that, and read the result back by SVJ (every original point → its merged point)."""
    import igl
    SV, SVI, SVJ, SF = igl.remove_duplicate_vertices(V0, f, eps)
    keep = (SF[:, 0] != SF[:, 1]) & (SF[:, 1] != SF[:, 2]) & (SF[:, 0] != SF[:, 2])
    return SV, SF[keep], SVI, SVJ
