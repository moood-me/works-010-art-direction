"""Render pieces of Blender's Human Base Meshes bundle (CC0) as clay, with or without wireframe.
usage: blender -b human_base_meshes_bundle.blend -P render_hbm.py -- OUTDIR"""
import bpy, sys, math
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]; out = args[0]; mode = args[1] if len(args) > 1 else 'main'
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading
sh.light = 'STUDIO'; sh.color_type = 'OBJECT'; sh.single_color = (0.80, 0.78, 0.76)
sh.show_cavity = False; sh.show_shadows = False; sh.show_specular_highlight = True
sc.display.render_aa = '16'; sc.render.film_transparent = False; sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('neutral'); w.color = (0.85, 0.84, 0.82); sc.world = w
cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam

def objs_of(coll):
    if coll in bpy.data.objects: return [bpy.data.objects[coll]]
    return [o for o in bpy.data.collections[coll].all_objects if o.type == 'MESH']

CLAY = (0.80, 0.78, 0.76, 1); INK = (0.12, 0.13, 0.16, 1)
WIRES = []
def add_wire(o, t):
    w = o.copy(); w.data = o.data; sc.collection.objects.link(w)
    for m in list(w.modifiers):
        if m.type in ('SUBSURF', 'MULTIRES'): w.modifiers.remove(m)
    wm = w.modifiers.new('wire', 'WIREFRAME'); wm.thickness = t; wm.offset = 1.0; wm.use_even_offset = True; wm.use_relative_offset = False; wm.use_boundary = True
    w.color = INK; WIRES.append(w); return w

def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH': o.hide_render = o not in objs

def bbox(objs):
    dg = bpy.context.evaluated_depsgraph_get(); ps = []
    for o in objs:
        m = o.evaluated_get(dg).to_mesh(); ps += [o.matrix_world @ v.co for v in m.vertices]; o.evaluated_get(dg).to_mesh_clear()
    return Vector([min(p[i] for p in ps) for i in range(3)]), Vector([max(p[i] for p in ps) for i in range(3)])

def shot(coll, name, yaw, res=(900, 900), wire=False, frame=1.25, focus=None, lens=85, mres=1):
    for w in WIRES: bpy.data.objects.remove(w)
    WIRES.clear()
    objs = objs_of(coll); show_only(objs)
    for o in objs:
        o.color = CLAY
        for p in o.data.polygons: p.use_smooth = True
        has = False
        for m in o.modifiers:
            if m.type == 'MULTIRES': m.render_levels = 0 if wire else mres; m.levels = m.render_levels; has = True
            if m.type == 'SUBSURF': m.render_levels = 0 if wire else 2; m.levels = m.render_levels; has = True
        if not has and not wire:
            m = o.modifiers.new('smooth', 'SUBSURF'); m.levels = m.render_levels = 2
        if wire:
            for m in list(o.modifiers):
                if m.name == 'smooth': o.modifiers.remove(m)
    bpy.context.view_layer.update()
    if wire:
        mn, mx = bbox(objs); t = (mx.z - mn.z) * 0.0012
        for o in objs: add_wire(o, t)
    bpy.context.view_layer.update()
    mn, mx = bbox(objs); c = (mn + mx) / 2; s = mx - mn
    if focus: c = Vector((c.x + s.x * focus[0], mn.y, c.z + s.z * focus[1])); size = s.z * focus[2]
    else: size = max(s.z, s.x, s.y if mode == "parts" else 0) * frame
    cd.lens = lens; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36; dist = size / (36 / lens)
    a = math.radians(yaw); cam.location = c + Vector((math.sin(a), -math.cos(a), 0.02)) * dist
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = f'{out}/{name}.png'; bpy.ops.render.render(write_still=True); print('WROTE', name, tuple(mn), tuple(mx))

if mode == 'parts':
    # what the bundle is: starting pieces for sculpting and modelling, from blocky to finished
    for name, yaw, wire in [('Head - Planar', 30, False), ('Head - Generic Topology', 30, True), ('Head - Primitives', 30, False),
                            ('Body Female - Primitive (Stylized)', 30, False), ('Jaw - Stylized ', 30, False), ('Eye - Stylized', 20, False),
                            ('Hand - Stylized ', 0, False), ('Foot - Stylized ', 40, False), ('Skull - Realistic', 30, False)]:
        shot(name, 'part-' + name.strip().replace(' ', '_').replace('(', '').replace(')', ''), yaw, res=(600, 600), wire=wire, frame=1.15, mres=2)
    sys.exit(0)
H = 'Head - Stylized'; HA = 'Head (Animation) - Realistic'
for yaw, v in [(0, 'front'), (35, 'tq'), (90, 'side')]:
    shot(H, f'hbm-sthead-{v}', yaw, frame=1.15)
shot(H, 'hbm-sthead-wire', 20, wire=True, frame=1.15)
shot(H, 'hbm-sthead-eye-wire', 15, wire=True, focus=(0.2, 0.12, 0.38))
shot(H, 'hbm-sthead-mouth-wire', 10, wire=True, focus=(0, -0.2, 0.4))
shot(HA, 'hbm-anim-wire', 20, wire=True, frame=1.15, mres=0)
shot(HA, 'hbm-anim-front', 20, frame=1.15, mres=2)
for c, n in [('Body Female - Stylized', 'f'), ('Body Male - Stylized', 'm')]:
    shot(c, f'hbm-body-{n}-front', 0, res=(600, 900), frame=1.08, lens=50)
    shot(c, f'hbm-body-{n}-tq', 35, res=(600, 900), frame=1.08, lens=50)
    shot(c, f'hbm-body-{n}-side', 90, res=(600, 900), frame=1.08, lens=50)
