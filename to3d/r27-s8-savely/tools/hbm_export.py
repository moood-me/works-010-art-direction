"""Blender: the stylised head of Human Base Meshes (CC0) and its two eyes as plain arrays (world coordinates):
the head's cage and the cage once subdivided (Catmull-Clark); each eye's mesh.
blender -b human_base_meshes_bundle.blend --python hbm_export.py -- out.npz"""
import bpy, sys, numpy as np
out = sys.argv[sys.argv.index('--') + 1]
res = {}


def grab(o, key, lev=0):
    for m in list(o.modifiers): o.modifiers.remove(m)
    if lev:
        s = o.modifiers.new('s', 'SUBSURF'); s.levels = lev; s.render_levels = lev
    dg = bpy.context.evaluated_depsgraph_get()
    me = o.evaluated_get(dg).to_mesh()
    M = o.matrix_world
    res[key + '_v'] = np.array([tuple(M @ v.co) for v in me.vertices])
    F = [list(p.vertices) for p in me.polygons]
    res[key + '_f'] = np.array([f if len(f) == 4 else f + [f[-1]] for f in F])
    print(key, res[key + '_v'].shape, set(len(f) for f in F))


o = bpy.data.objects['GEO-head_stylized']
grab(o, 'cage', 0)
grab(o, 'sub', 1)
for s in 'LR':
    grab(bpy.data.objects[f'GEO-head_stylized.eye.{s}'], 'eye' + s, 0)
np.savez(out, **res)
