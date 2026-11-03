# prints head bbox (world) of evaluated head mesh and lists collections visibility
import bpy, sys, mathutils
head=sys.argv[sys.argv.index('--')+1]
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects[head]; e=o.evaluated_get(dg); m=e.to_mesh()
ps=[o.matrix_world@v.co for v in m.vertices]
mn=mathutils.Vector([min(p[i] for p in ps) for i in range(3)]); mx=mathutils.Vector([max(p[i] for p in ps) for i in range(3)])
print("BBOX", tuple(round(x,3) for x in mn), tuple(round(x,3) for x in mx))
def walk(lc,d=0):
    print("LC", "  "*d, lc.name, "excl", lc.exclude, "hide", lc.hide_viewport, "chide", lc.collection.hide_render)
    for c in lc.children: walk(c,d+1)
walk(bpy.context.view_layer.layer_collection)
for n in ['GEO-rain-body','GEO-snow-body']:
    if n in bpy.data.objects:
        o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); ps=[o.matrix_world@v.co for v in m.vertices]
        print("BODY z", min(p.z for p in ps), max(p.z for p in ps), "y", min(p.y for p in ps), max(p.y for p in ps))
