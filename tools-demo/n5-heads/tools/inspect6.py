import bpy
rig=bpy.data.objects['RIG-Snow']
ad=rig.animation_data
for d in ad.drivers:
    if any(k in d.data_path for k in ['Lips_Corner','Eyelid','Jaw','Eye_Ring','Cheek']) :
        print(d.data_path, '|', d.driver.expression, [[(t.bone_target, t.transform_type, t.transform_space) for t in v.targets] for v in d.driver.variables])
for n in ['ACT-Lips_Corner.L','ACT-Lips_Corner.R','MSTR-Eyelid_Upper.L','Jaw','CheekRaiser.L']:
    pb=rig.pose.bones[n]; print(n, pb.rotation_mode, [(c.type, c.name) for c in pb.constraints], pb.bone.matrix_local.to_3x3().transposed()[1][:])
