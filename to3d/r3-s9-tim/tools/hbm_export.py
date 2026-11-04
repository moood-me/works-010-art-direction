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
