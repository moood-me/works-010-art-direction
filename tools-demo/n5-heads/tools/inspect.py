import bpy, sys
print("FILE", bpy.data.filepath)
print("SCENES", [s.name for s in bpy.data.scenes])
for o in bpy.data.objects:
    extra=""
    if o.type=='MESH':
        me=o.data; sk=me.shape_keys
        extra=f" v={len(me.vertices)} sk={len(sk.key_blocks) if sk else 0} mods={[m.type for m in o.modifiers]}"
    if o.type=='ARMATURE':
        extra=f" bones={len(o.data.bones)}"
    print("OBJ", o.type, repr(o.name), "coll", [c.name for c in o.users_collection], extra, "hide", o.hide_render)
for t in bpy.data.texts: print("TEXT", t.name)
