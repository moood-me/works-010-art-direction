"""Render a Blender Studio character (or a Human Base Mesh) in a clean neutral way.
usage: blender -b FILE -P render.py -- JSON
JSON: {"char": "rain"|"snow", "engine": "WB_CLAY"|"WB_MAT"|"EEVEE"|"CYCLES", "shots": [{"out":..., "view":"front|tq|side|body|eyeL|mouth", "pose": {...}, "wire": false, "res":[w,h]}]}
pose: {bone: {"loc":[x,y,z], "rot":[x,y,z] (degrees, euler)}}
"""
import bpy, sys, json, math, mathutils
from mathutils import Vector
cfg = json.loads(sys.argv[sys.argv.index('--') + 1])
sc = bpy.context.scene
CH = {
  'rain': dict(head='GEO-rain-head', rig='RIG-rain', hide=['GEO-rain-eyes_viewport', 'GEO-rain-body_nomask']),
  'snow': dict(head='GEO-snow-head', rig='RIG-Snow', hide=['GEO-snow-eye_anim', 'GEO-snow_head_helper', 'GEO-snow_pants_deformer', 'GEO-snow_shoes_base_deformer', 'GEO-snow_teeth_lower_helper', 'GEO-snow_teeth_upper_helper']),
}[cfg['char']]
for n in CH['hide']:
    if n in bpy.data.objects: bpy.data.objects[n].hide_render = True
for o in bpy.data.objects:
    if o.name.startswith('WGT-'): o.hide_render = True

eng = cfg.get('engine', 'WB_CLAY')
if eng.startswith('WB'):
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'STUDIO'; sh.studio_light = 'Default' if 'Default' in [s.name for s in bpy.context.preferences.studio_lights] else sh.studio_light
    sh.color_type = 'SINGLE' if eng == 'WB_CLAY' else ('TEXTURE' if eng == 'WB_TEX' else 'MATERIAL')
    sh.single_color = (0.80, 0.78, 0.76)
    sh.show_cavity = False; sh.show_shadows = False; sh.show_object_outline = False; sh.show_specular_highlight = True
    sh.background_type = 'VIEWPORT'; sh.background_color = (0.93, 0.92, 0.90)
    sc.display.render_aa = '16'
    w = bpy.data.worlds.new('neutral'); w.color = (0.85, 0.84, 0.82); sc.world = w
elif eng == 'EEVEE':
    sc.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    sc.eevee.taa_render_samples = 32
else:
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = cfg.get('samples', 24); sc.cycles.use_denoising = True
    sc.render.threads_mode = 'FIXED'; sc.render.threads = 2
sc.render.film_transparent = False
sc.view_settings.view_transform = 'Standard' if eng.startswith('WB') else 'AgX'
if not eng.startswith('WB'):
    w = bpy.data.worlds.new('neutral'); w.use_nodes = True; sc.world = w
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.8, 0.8, 0.8, 1); bg.inputs[1].default_value = 1.0
    # a soft key light and a fill from the camera side
    for name, rot, en, size in [('key', (55, 0, -35), 3.0, 3), ('rim', (60, 0, 150), 2.0, 2)]:
        L = bpy.data.lights.new(name, 'SUN'); L.energy = en; L.angle = math.radians(size * 10)
        ob = bpy.data.objects.new(name, L); ob.rotation_euler = [math.radians(a) for a in rot]; sc.collection.objects.link(ob)

rig = bpy.data.objects[CH['rig']]
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam

def reset_pose():
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)

def apply_pose(p):
    for b, t in p.items():
        pb = rig.pose.bones[b]
        if 'loc' in t: pb.location = t['loc']
        if 'rot' in t:
            if pb.rotation_mode == 'QUATERNION':
                pb.rotation_quaternion = mathutils.Euler([math.radians(a) for a in t['rot']]).to_quaternion()
            else: pb.rotation_euler = [math.radians(a) for a in t['rot']]
        if 'scale' in t: pb.scale = t['scale']
    for k, v in cfg.get('props', {}).items():
        exec(k + ' = v', {'bpy': bpy, 'v': v, 'rig': rig})

def bbox(name):
    dg = bpy.context.evaluated_depsgraph_get(); o = bpy.data.objects[name]; m = o.evaluated_get(dg).to_mesh()
    ps = [o.matrix_world @ v.co for v in m.vertices]
    mn = Vector([min(p[i] for p in ps) for i in range(3)]); mx = Vector([max(p[i] for p in ps) for i in range(3)])
    o.evaluated_get(dg).to_mesh_clear(); return mn, mx

def place(view, hb, bb):
    """front: camera on -Y looking +Y. Focal 85 mm-ish framing."""
    hc = (hb[0] + hb[1]) / 2; hs = hb[1] - hb[0]
    yaw = {'front': 0, 'tq': 35, 'side': 90, 'body': 25, 'bodyfront': 0, 'bodyside': 90, 'eyeL': 12, 'mouth': 10, 'eyeLside': 60}[view]
    cam_d.lens = 85; cam_d.sensor_width = 36
    if view.startswith('body'):
        c = (bb[0] + bb[1]) / 2; h = bb[1].z - bb[0].z; dist = h * 1.25 / 0.42 * 0.5 * 1.0
        tgt = Vector((c.x, c.y, c.z)); cam_d.lens = 50; dist = h / (36 / 50) * 1.12
    elif view in ('eyeL', 'eyeLside'):
        tgt = EYE_L.copy(); dist = hs.z * 0.42 / (36 / 85)
    elif view == 'mouth':
        tgt = MOUTH.copy(); dist = hs.z * 0.42 / (36 / 85)
    else:
        tgt = (EYE_L + MOUTH) / 2; tgt.x = 0; tgt.z += hs.z * 0.08; dist = hs.z * 1.35 / (36 / 85)
    a = math.radians(yaw)
    d = Vector((math.sin(a), -math.cos(a), 0.0))
    cam.location = tgt + d * dist + Vector((0, 0, dist * 0.02))
    dirv = tgt - cam.location; cam.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()

def bone_head(n): return rig.matrix_world @ rig.data.bones[n].head_local
EYE_L = bone_head({'rain': 'DEF-Eye.L', 'snow': 'ROOT-Eye.L'}[cfg['char']])
MOUTH = (bone_head({'rain': 'ACT-Lips_Corner.L', 'snow': 'ACT-Lips_Corner.L'}[cfg['char']]) + bone_head({'rain': 'ACT-Lips_Corner.R', 'snow': 'ACT-Lips_Corner.R'}[cfg['char']])) / 2
print('EYE', tuple(EYE_L), 'MOUTH', tuple(MOUTH))
body = {'rain': 'GEO-rain-body', 'snow': 'GEO-snow-body'}[cfg['char']]
for s in cfg['shots']:
    reset_pose(); apply_pose(s.get('pose', {})); bpy.context.view_layer.update()
    # rest bbox of the head for stable framing
    if 'hb' not in globals():
        hb = bbox(CH['head']); bbs = [bbox(o.name) for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render and o.visible_get()]
        bb = (Vector([min(b[0][i] for b in bbs) for i in range(3)]), Vector([max(b[1][i] for b in bbs) for i in range(3)]))
        print('HB', tuple(hb[0]), tuple(hb[1]), 'BB', tuple(bb[0]), tuple(bb[1]))
    place(s['view'], hb, bb)
    w, h = s.get('res', [900, 900]); sc.render.resolution_x = w; sc.render.resolution_y = h; sc.render.resolution_percentage = 100
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.show_wire = bool(s.get('wire')); o.show_all_edges = True
    if s.get('wire') and eng.startswith('WB'):
        sc.display.shading.show_xray = False
    sc.render.filepath = s['out']; bpy.ops.render.render(write_still=True); print('WROTE', s['out'])
