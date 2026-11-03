"""Neutral Workbench renders of any Blender Studio character: whole body, head at three angles, clothes alone.
usage: blender -b FILE -P render_any.py -- JSON
JSON: {"name": "jay", "head": "GEO-jay_head", "out": DIR, "color": "MATERIAL"|"SINGLE",
       "views": ["body", "bodytq", "front", "tq", "side"], "parts": [[label, [object names]], ...], "pose": {bone: {...}}, "shots": [...]}"""
import bpy, sys, json, math
from mathutils import Vector, Euler
cfg = json.loads(sys.argv[sys.argv.index('--') + 1])
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading
sh.light = 'STUDIO'; sh.color_type = cfg.get('color', 'MATERIAL'); sh.single_color = (0.80, 0.78, 0.76)
sh.show_cavity = False; sh.show_shadows = False; sh.show_specular_highlight = True
sc.display.render_aa = '16'; sc.render.film_transparent = False; sc.view_settings.view_transform = 'Standard'; sc.render.image_settings.file_format = 'PNG'
w = bpy.data.worlds.new('neutral'); w.color = (0.85, 0.84, 0.82); sc.world = w
cd = bpy.data.cameras.new('c'); cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36
cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
for o in bpy.data.objects:  # widgets, helpers, cages, proxies the file itself keeps out of the picture
    if o.type == 'MESH' and any(k in o.name.lower() for k in ('wgt', 'widget', 'helper', 'cage', 'cs_', 'cornea', 'surfdef', 'deformer')): o.hide_render = True
def unlink(o):
    # out of the scene, not just hide_render: these rigs drive visibility with drivers that undo hide_render
    cs = list(o.users_collection)
    for c in cs: c.objects.unlink(o)
    return cs
for n in cfg.get('hide', []):
    if n in bpy.data.objects: unlink(bpy.data.objects[n])
rig = next((o for o in bpy.data.objects if o.type == 'ARMATURE' and o.name.startswith('RIG')), None)
for b, t in cfg.get('pose', {}).items():
    pb = rig.pose.bones[b]
    if 'loc' in t: pb.location = t['loc']
    if 'rot' in t:
        e = Euler([math.radians(a) for a in t['rot']])
        if pb.rotation_mode == 'QUATERNION': pb.rotation_quaternion = e.to_quaternion()
        else: pb.rotation_euler = e
bpy.context.view_layer.update()

def vis():
    return [o for o in bpy.data.objects if o.type in ('MESH', 'CURVES') and not o.hide_render and o.visible_get()]

def bbox(objs):
    dg = bpy.context.evaluated_depsgraph_get(); ps = []
    for o in objs:
        if o.type != 'MESH': continue
        e = o.evaluated_get(dg); m = e.to_mesh(); ps += [o.matrix_world @ v.co for v in m.vertices]; e.to_mesh_clear()
    return Vector([min(p[i] for p in ps) for i in range(3)]), Vector([max(p[i] for p in ps) for i in range(3)])

def shoot(name, c, size, yaw, res, lens=85):
    cd.lens = lens; dist = size / (36 / lens); a = math.radians(yaw)
    cam.location = c + Vector((math.sin(a), -math.cos(a), 0.0)) * dist
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = f"{cfg['out']}/{cfg['name']}-{name}.png"; bpy.ops.render.render(write_still=True); print('WROTE', name)

allv = vis(); bb = bbox(allv)
hb = bbox([bpy.data.objects[cfg['head']]]) if cfg.get('head') else None
for v in cfg.get('views', []):
    if v.startswith('body'):
        c = (bb[0] + bb[1]) / 2; shoot(v, c, (bb[1].z - bb[0].z) * 1.08 if v == 'bodyside' else max((bb[1].z - bb[0].z) * 1.08, (bb[1].x - bb[0].x) * 1.04 * 1.5), {'body': 0, 'bodytq': 35, 'bodyside': 90}[v], (600, 900), 50)
    else:
        c = (hb[0] + hb[1]) / 2; s = hb[1] - hb[0]; c.z += s.z * cfg.get('dz', 0.0)
        shoot(v, c, s.z * cfg.get('hframe', 1.25), {'front': 0, 'tq': 35, 'side': 90}[v], (700, 700))
for label, names in cfg.get('parts', []):
    keep = [bpy.data.objects[n] for n in names if n in bpy.data.objects]
    if not keep: print('MISSING', label); continue
    pb = bbox(keep); c = (pb[0] + pb[1]) / 2; s = pb[1] - pb[0]
    gone = {o: unlink(o) for o in list(sc.objects) if o not in keep and o.type not in ('ARMATURE', 'LATTICE', 'CAMERA', 'LIGHT') and o is not cam}
    shoot('part-' + label, c, max(s.z, s.x, s.y) * 1.15, 25, (500, 500))
    for o, cs in gone.items():
        for col in cs: col.objects.link(o)
