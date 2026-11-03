import bpy
for o in bpy.data.objects:
    if o.type == 'MESH' and not o.name.startswith(('WGT', 'WIDGET', 'CS_')) and len(o.data.vertices) > 100:
        sk = o.data.shape_keys
        print("M", repr(o.name), len(o.data.vertices), "sk", len(sk.key_blocks) if sk else 0, "hideR", o.hide_render, [c.name for c in o.users_collection][:2])
for o in bpy.data.objects:
    if o.type == 'ARMATURE':
        fc = [bc.name + ':' + str(len(bc.bones)) for bc in o.data.collections_all if 'ace' in bc.name]
        print("A", o.name, len(o.data.bones), fc)
