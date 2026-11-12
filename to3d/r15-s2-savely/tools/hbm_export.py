"""Blender: Human Base Meshes (CC0) stylised head and its eyes as plain arrays, with which of the head's faces are
seen from outside (the socket and mouth linings are not).
  blender -b human_base_meshes_bundle.blend --python hbm_export.py -- out.npz"""
import bpy, sys, numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector

out = sys.argv[sys.argv.index('--') + 1]
NAMES = {'head': 'GEO-head_stylized', 'eyeL': 'GEO-head_stylized.eye.L', 'eyeR': 'GEO-head_stylized.eye.R'}
res, verts, polys = {}, [], []
for k, name in NAMES.items():
    o = bpy.data.objects[name]; M = o.matrix_world
    v = [M @ p.co for p in o.data.vertices]
    P = [list(p.vertices) for p in o.data.polygons]
    res[k + '_v'] = np.array([tuple(x) for x in v])
    res[k + '_fs'] = np.array([len(p) for p in P]); res[k + '_f'] = np.concatenate(P)
    base = len(verts); verts += v; polys += [[base + i for i in p] for p in P]
tree = BVHTree.FromPolygons(verts, polys)
dirs = np.random.default_rng(1).normal(size=(64, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
o = bpy.data.objects[NAMES['head']]; M = o.matrix_world
vis = []
for p in o.data.polygons:
    c = M @ p.center; n = (M.to_3x3() @ p.normal).normalized(); seen = 0
    for d in dirs:
        d = Vector(d)
        if d.dot(n) > 0.05 and tree.ray_cast(c + n * 1e-4 + d * 1e-4, d)[0] is None: seen += 1
    vis.append(seen)
res['head_vis'] = np.array(vis)
np.savez(out, **res)
print('exported', {k: v.shape for k, v in res.items()})
