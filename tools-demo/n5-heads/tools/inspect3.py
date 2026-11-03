import bpy
rig=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
for bc in rig.data.collections_all:
    bs=[b.name for b in bc.bones]
    print("BC", bc.name, "vis", bc.is_visible, len(bs), bs[:60] if any(k in bc.name.lower() for k in ['face','eye','mouth','head','lip','brow','jaw']) else '')
print([a.name for a in bpy.data.actions][:100])
