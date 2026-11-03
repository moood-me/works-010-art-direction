import bpy
rig=bpy.data.objects['RIG-Snow']
for bc in rig.data.collections_all:
    bs=[b.name for b in bc.bones]
    if any(k in bc.name.lower() for k in ['face','eye','mouth','lip','brow','jaw']): print("BC", bc.name, bc.is_visible, len(bs), bs[:80])
seen={}
for pb in rig.pose.bones:
    for c in pb.constraints:
        if c.type=='ACTION' and c.action:
            key=(c.action.name,c.subtarget,c.transform_channel,round(c.min,4),round(c.max,4),c.frame_start,c.frame_end)
            seen[key]=seen.get(key,0)+1
for k,v in sorted(seen.items()): print("ACT",k,v)
o=bpy.data.objects['GEO-snow-head']; print([k.name for k in o.data.shape_keys.key_blocks])
ad=o.data.shape_keys.animation_data
for d in (ad.drivers if ad else []): print(" DRV", d.data_path, d.driver.expression, [[(t.bone_target, t.transform_type, t.data_path) for t in v.targets] for v in d.driver.variables])
print(bpy.data.texts['ReadMe.txt'].as_string()[:1500])
