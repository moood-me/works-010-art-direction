"""Blender: the stylised head of Human Base Meshes (CC0) as plain arrays — the cage, and the cage once subdivided
(Catmull-Clark), with which faces of the cage are seen from outside (not the eye-socket and mouth linings).
blender -b human_base_meshes_bundle.blend --python hbm_export.py -- out.npz"""
import bpy, sys, numpy as np
out = sys.argv[sys.argv.index('--') + 1]
res = {}
for o in bpy.data.objects:
    if o.type == 'MESH' and 'stylized' in o.name: print('object', o.name, len(o.data.vertices), [m.type for m in o.modifiers])
o = bpy.data.objects['GEO-head_stylized']
M = o.matrix_world
for key, lev in (('cage', 0), ('sub', 1)):
    for m in list(o.modifiers): o.modifiers.remove(m)
    if lev:
        s = o.modifiers.new('s', 'SUBSURF'); s.levels = lev; s.render_levels = lev
    dg = bpy.context.evaluated_depsgraph_get()
    me = o.evaluated_get(dg).to_mesh()
    res[key + '_v'] = np.array([tuple(M @ v.co) for v in me.vertices])
    F = [list(p.vertices) for p in me.polygons]
    res[key + '_f'] = np.array([f if len(f) == 4 else f + [f[-1]] for f in F])
    print(key, res[key + '_v'].shape, set(len(f) for f in F))
np.savez(out, **res)

# which faces of the subdivided head can be seen from outside: rays from each face over its outer hemisphere that
# escape the head; the hidden ones are the linings of the eye sockets, the nostrils and the mouth bag
from mathutils.bvhtree import BVHTree
from mathutils import Vector
V = [Vector(p) for p in res['sub_v']]
P = [list(dict.fromkeys(q)) for q in res['sub_f'].tolist()]
tree = BVHTree.FromPolygons(V, P)
rng = np.random.default_rng(1)
dirs = rng.normal(size=(48, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
vis = []
for q in P:
    c = sum((V[i] for i in q), Vector()) / len(q)
    n = (V[q[1]] - V[q[0]]).cross(V[q[2]] - V[q[0]]).normalized()
    seen = 0
    for d in dirs:
        d = Vector(d)
        if d.dot(n) <= 0.05: continue
        if tree.ray_cast(c + n * 1e-4 + d * 1e-4, d)[0] is None: seen += 1
    vis.append(seen)
res['sub_vis'] = np.array(vis)
np.savez(out, **res)
print('visible', (res['sub_vis'] > 0).sum(), len(vis))
