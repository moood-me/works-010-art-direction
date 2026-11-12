"""Blender: the Human Base Meshes (CC0) stylised head, its two eyes and the stylised jaw (teeth, gums, tongue) as
plain arrays, in Blender's frame (z up, the face toward -y).
  blender -b human_base_meshes_bundle.blend --python hbm_export.py -- out.npz"""
import bpy, sys, numpy as np

out = sys.argv[sys.argv.index('--') + 1]
NAMES = {'head': 'GEO-head_stylized', 'eyeL': 'GEO-head_stylized.eye.L', 'eyeR': 'GEO-head_stylized.eye.R',
         'jaw': 'Jaw - Stylized '}
res = {}
for k, name in NAMES.items():
    o = bpy.data.objects[name]
    dg = bpy.context.evaluated_depsgraph_get()
    me = o.evaluated_get(dg).to_mesh()
    M = o.matrix_world
    res[k + '_v'] = np.array([tuple(M @ v.co) for v in me.vertices])
    P = [list(p.vertices) for p in me.polygons]
    res[k + '_fs'] = np.array([len(p) for p in P]); res[k + '_f'] = np.concatenate(P)
    # material slot per face, and the slot names (the eye: sclera / iris / cornea …)
    res[k + '_m'] = np.array([p.material_index for p in me.polygons])
    res[k + '_mn'] = np.array([s.material.name if s.material else '' for s in o.material_slots] or [''])
    # uv if any
    if me.uv_layers:
        uv = me.uv_layers.active.data
        res[k + '_uv'] = np.array([tuple(uv[i].uv) for p in me.polygons for i in p.loop_indices])
    print(k, name, len(me.vertices), len(P), list(res[k + '_mn']), [m.type for m in o.modifiers], o.parent.name if o.parent else None)
np.savez(out, **res)
