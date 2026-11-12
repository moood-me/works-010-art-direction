"""Blender: take the stylised head (and its eyes) out of Human Base Meshes (CC0) as plain arrays.
blender -b human_base_meshes_bundle.blend --python hbm_export.py -- out.npz"""
import bpy, sys, numpy as np
out = sys.argv[sys.argv.index('--') + 1]
res = {}
for name in ['GEO-head_stylized', 'GEO-head_stylized.eye.L', 'GEO-head_stylized.eye.R']:
    o = bpy.data.objects[name]
    m = o.data
    M = np.array(o.matrix_world)
    v = np.array([(M @ np.array([*p.co, 1]))[:3] for p in m.vertices])
    polys = [list(p.vertices) for p in m.polygons]
    k = name.split('.')[-1] if '.' in name else 'head'
    res[k + '_v'] = v
    res[k + '_fs'] = np.array([len(p) for p in polys])
    res[k + '_f'] = np.concatenate(polys)
    print(name, v.shape, v.min(0), v.max(0), set(len(p) for p in polys))
np.savez(out, **res)

# which faces of the head can be seen from outside (rays from each face, over its outer hemisphere, that escape the
# head and the eyeballs): the hidden ones are the linings of the eye sockets and the mouth bag
from mathutils.bvhtree import BVHTree
from mathutils import Vector
verts, polys = [], []
for name in ['GEO-head_stylized', 'GEO-head_stylized.eye.L', 'GEO-head_stylized.eye.R']:
    o = bpy.data.objects[name]; M = o.matrix_world; base = len(verts)
    verts += [M @ p.co for p in o.data.vertices]
    polys += [[base + i for i in p.vertices] for p in o.data.polygons]
tree = BVHTree.FromPolygons(verts, polys)
rng = np.random.default_rng(1)
dirs = rng.normal(size=(64, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
o = bpy.data.objects['GEO-head_stylized']; M = o.matrix_world
vis = []
for p in o.data.polygons:
    c = M @ p.center; n = (M.to_3x3() @ p.normal).normalized()
    seen = 0
    for d in dirs:
        d = Vector(d)
        if d.dot(n) <= 0.05: continue
        hit = tree.ray_cast(c + n * 1e-4 + d * 1e-4, d)
        if hit[0] is None: seen += 1
    vis.append(seen)
res['head_vis'] = np.array(vis)
np.savez(out, **res)
print('visible', (np.array(vis) > 0).sum(), len(vis))
