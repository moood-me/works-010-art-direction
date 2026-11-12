"""Export Blender Human Base Meshes' head «for animation» (realistic, CC0) with its sculpted multires level applied,
and its eyes (sclera, iris), to an npz (world coordinates, Blender z-up); after Р2's export_hbm.py, plus which head
vertices are seen from outside (rays over the hemisphere; the mouth's inside and the sockets' linings are not), so the
fit only pulls the outer skin to the drawing.
usage: blender -b human_base_meshes_bundle.blend -P export_hbm.py -- OUT.npz"""
import bpy, sys, numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector
out = sys.argv[sys.argv.index('--') + 1]
d, allv, allp = {}, [], []
for key, name in (('head', 'GEO-head_animation_realistic'), ('scleraL', 'GEO-head_animation_realistic.sclera.L'), ('scleraR', 'GEO-head_animation_realistic.sclera.R'), ('irisL', 'GEO-head_animation_realistic.iris.L'), ('irisR', 'GEO-head_animation_realistic.iris.R')):
    o = bpy.data.objects[name]
    for m in o.modifiers:
        if m.type == 'MULTIRES':
            m.levels = m.total_levels
    dg = bpy.context.evaluated_depsgraph_get()
    me = o.evaluated_get(dg).to_mesh()
    V = [o.matrix_world @ v.co for v in me.vertices]
    F = [list(p.vertices) for p in me.polygons]
    n = max(len(f) for f in F)
    Fa = np.full((len(F), n), -1); [Fa.__setitem__((i, slice(0, len(f))), f) for i, f in enumerate(F)]
    d[key + '_v'] = np.array([tuple(v) for v in V]); d[key + '_f'] = Fa
    base = len(allv); allv += V; allp += [[base + i for i in f] for f in F]
    if key == 'head':
        NV = [(o.matrix_world.to_3x3() @ v.normal).normalized() for v in me.vertices]
tree = BVHTree.FromPolygons(allv, allp)
dirs = np.random.default_rng(1).normal(size=(96, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
vis = []
for v, n in zip(d['head_v'], NV):
    p = Vector(tuple(v)); seen = 0
    for dd in dirs:
        dd = Vector(dd)
        if dd.dot(n) > 0.1 and tree.ray_cast(p + n * 2e-4, dd)[0] is None: seen += 1
    vis.append(seen)
d['head_vis'] = np.array(vis)
np.savez(out, **d)
print('exported', {k: v.shape for k, v in d.items()})
