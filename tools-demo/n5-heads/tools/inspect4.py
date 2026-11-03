import bpy
rig=bpy.data.objects[[o.name for o in bpy.data.objects if o.type=='ARMATURE'][0]]
seen={}
for pb in rig.pose.bones:
    for c in pb.constraints:
        if c.type=='ACTION' and c.action:
            key=(c.action.name,c.subtarget,c.transform_channel,c.target_space,round(c.min,4),round(c.max,4),c.frame_start,c.frame_end)
            seen[key]=seen.get(key,0)+1
for k,v in sorted(seen.items()): print("ACT",k,v)
for n in ['MSTR-Jaw','MSTR-Mouth','MSTR-Eyebrow.L','ACT-Eyelid_Upper.L','ACT-Lips_Corner.L','MSTR-Eyering_Upper.L','BB-Eye.L','TGT-Eyes']:
    pb=rig.pose.bones.get(n)
    if pb:
        print("BONE",n,"lock",tuple(pb.lock_location),tuple(pb.lock_rotation),pb.rotation_mode,[ (c.type, getattr(c,'min_x',None),getattr(c,'max_x',None),getattr(c,'min_y',None),getattr(c,'max_y',None),getattr(c,'min_z',None),getattr(c,'max_z',None)) for c in pb.constraints][:4])
