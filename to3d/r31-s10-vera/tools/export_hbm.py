"""Export (with its sculpted multires level applied) Blender Human Base Meshes' head for animation (realistic, CC0) and its eyes to an npz (world coordinates, Blender z-up).
usage: blender -b human_base_meshes_bundle.blend -P export_hbm.py -- OUT.npz"""
import bpy, sys, numpy as np
out = sys.argv[sys.argv.index('--') + 1]
d = {}
for key, name in (('head', 'GEO-head_animation_realistic'), ('scleraL', 'GEO-head_animation_realistic.sclera.L'), ('scleraR', 'GEO-head_animation_realistic.sclera.R'), ('irisL', 'GEO-head_animation_realistic.iris.L'), ('irisR', 'GEO-head_animation_realistic.iris.R')):
    o = bpy.data.objects[name]
    for m in o.modifiers:
        if m.type == 'MULTIRES':
            print(name, 'multires levels', m.levels, m.render_levels, m.sculpt_levels, m.total_levels)
            m.levels = m.total_levels                # the sculpted form, not the bare cage
    dg = bpy.context.evaluated_depsgraph_get()
    me = o.evaluated_get(dg).to_mesh()
    V = np.array([tuple(o.matrix_world @ v.co) for v in me.vertices])
    F = [list(p.vertices) for p in me.polygons]
    n = max(len(f) for f in F)
    Fa = np.full((len(F), n), -1); [Fa.__setitem__((i, slice(0, len(f))), f) for i, f in enumerate(F)]
    d[key + '_v'] = V; d[key + '_f'] = Fa
    d[key + '_mat'] = np.array([p.material_index for p in me.polygons])
    print(key, V.shape, n, [m.name for m in me.materials], [g.name for g in o.vertex_groups][:20], [m.type for m in o.modifiers])
np.savez(out, **d)
