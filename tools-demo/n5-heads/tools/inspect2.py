import bpy
print(bpy.data.texts['ReadMe.txt'].as_string()[:3000] if 'ReadMe.txt' in bpy.data.texts else '')
for name in ['GEO-rain-head','GEO-snow-head']:
    o=bpy.data.objects.get(name)
    if o and o.data.shape_keys:
        print(name, [k.name for k in o.data.shape_keys.key_blocks])
        ad=o.data.shape_keys.animation_data
        if ad:
            for d in ad.drivers[:40]:
                print(" DRV", d.data_path, d.driver.type, d.driver.expression, [(v.name, [(t.id.name if t.id else None, t.bone_target, t.transform_type, t.data_path) for t in v.targets]) for v in d.driver.variables])
rig=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
names=[b.name for b in rig.data.bones if not b.name.startswith(('ORG','DEF','MCH','STR-T','FK-C'))]
import re
face=[n for n in names if re.search(r'(?i)eye|lid|brow|mouth|lip|jaw|cheek|nose|smile|face|blink|teeth|tongue',n)]
print(len(face)); print(face[:300])
print("PROPS", [(k) for k in rig.pose.bones[0].keys()][:20])
for pb in rig.pose.bones:
    ks=[k for k in pb.keys() if not k.startswith('_')]
    if ks and len(ks)<60: print("PB", pb.name, ks)
