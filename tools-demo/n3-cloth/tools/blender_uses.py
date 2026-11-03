# What Blender's cloth is made for, used as its manual shows it: a tablecloth dropped on a table, a flag in the wind,
# a cushion blown up by pressure. blender -b -P blender_uses.py -- <out dir> [which: table|flag|pillow]
# Renders PNG frames (EEVEE) to <out dir>/<which>/; times go to <out dir>/<which>.json.
import bpy, sys, os, json, time, math

args = sys.argv[sys.argv.index('--') + 1:]
out, which = args[0], args[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.fps = 30
sc.render.engine = 'BLENDER_EEVEE_NEXT'; sc.eevee.taa_render_samples = 16
sc.render.resolution_x, sc.render.resolution_y = 480, 360
sc.render.image_settings.file_format = 'PNG'
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.81, 0.78, 0.74, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 0.7

def mat(name, rgb, rough=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    return m

def sun():
    bpy.ops.object.light_add(type='SUN', rotation=(math.radians(50), math.radians(10), math.radians(-35))); bpy.context.object.data.energy = 3.5

def camera(loc, look):
    bpy.ops.object.camera_add(location=loc); c = bpy.context.object; sc.camera = c
    d = bpy.data.objects.new('look', None); d.location = look; sc.collection.objects.link(d)
    t = c.constraints.new('TRACK_TO'); t.target = d; t.track_axis = 'TRACK_NEGATIVE_Z'; t.up_axis = 'UP_Y'

def floor():
    bpy.ops.mesh.primitive_plane_add(size=30); f = bpy.context.object; f.data.materials.append(mat('floor', (0.62, 0.58, 0.53), 1))
    return f

def grid(size, cuts, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=cuts, y_subdivisions=cuts, size=size, location=loc, rotation=rot)
    return bpy.context.object

sun(); floor()
if which == 'table':   # a tablecloth falls on a round table (cotton preset)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.75, location=(0, 0, 0.375), vertices=64); t = bpy.context.object
    t.data.materials.append(mat('wood', (0.35, 0.2, 0.1), 0.5)); t.modifiers.new('c', 'COLLISION'); t.collision.thickness_outer = 0.005
    cl = grid(1.9, 90, (0, 0, 1.15)); cl.data.materials.append(mat('cloth', (0.75, 0.15, 0.15)))
    bpy.ops.object.shade_smooth()
    cm = cl.modifiers.new('cloth', 'CLOTH'); s = cm.settings; s.mass = 0.3; s.tension_stiffness = s.compression_stiffness = 15; s.bending_stiffness = 0.5; s.quality = 8
    cm.collision_settings.use_self_collision = True; cm.collision_settings.distance_min = 0.005; cm.collision_settings.self_distance_min = 0.004
    sub = cl.modifiers.new('s', 'SUBSURF'); sub.levels = sub.render_levels = 1
    camera((2.6, -2.6, 1.9), (0, 0, 0.6)); frames = 100
elif which == 'flag':  # a flag on a pole in gusty wind (pinned edge, a wind force field with noise)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=3, location=(0, 0, 1.5)); bpy.context.object.data.materials.append(mat('pole', (0.3, 0.3, 0.32), 0.4))
    cl = grid(1.0, 60, (0.52, 0, 2.5), (math.radians(90), 0, 0)); cl.scale = (1, 0.65, 1); bpy.ops.object.transform_apply(scale=True)
    cl.data.materials.append(mat('flag', (0.1, 0.25, 0.6))); bpy.ops.object.shade_smooth()
    vg = cl.vertex_groups.new(name='pin'); vg.add([v.index for v in cl.data.vertices if (cl.matrix_world @ v.co).x < 0.03], 1, 'REPLACE')
    cm = cl.modifiers.new('cloth', 'CLOTH'); s = cm.settings; s.mass = 0.15; s.tension_stiffness = s.compression_stiffness = 5; s.bending_stiffness = 0.05; s.quality = 8
    s.vertex_group_mass = 'pin'
    bpy.ops.object.effector_add(type='WIND', location=(-2, 0, 2.5), rotation=(0, math.radians(90), 0)); w = bpy.context.object
    w.field.strength = 900; w.field.noise = 2.5; w.field.flow = 0.5
    camera((2.0, -3.6, 2.4), (0.6, 0, 2.2)); frames = 120
else:                  # a cushion: a closed cloth blown up by pressure, dropped on the floor
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.6)); cl = bpy.context.object; cl.scale = (0.6, 0.6, 0.12); bpy.ops.object.transform_apply(scale=True)
    m = cl.modifiers.new('r', 'SUBSURF'); m.subdivision_type = 'SIMPLE'; m.levels = 5; bpy.ops.object.modifier_apply(modifier='r')
    cl.data.materials.append(mat('cushion', (0.85, 0.65, 0.25))); bpy.ops.object.shade_smooth()
    cm = cl.modifiers.new('cloth', 'CLOTH'); s = cm.settings; s.mass = 0.3; s.quality = 8; s.use_pressure = True; s.uniform_pressure_force = 6; s.shrink_min = 0
    cm.collision_settings.use_self_collision = True
    camera((1.9, -1.9, 1.3), (0, 0, 0.15)); frames = 80
sc.frame_start, sc.frame_end = 1, frames
for o in sc.objects:
    if o.type == 'MESH' and o.name.startswith(('Plane',)): o.modifiers.new('c', 'COLLISION')
cm.point_cache.frame_start, cm.point_cache.frame_end = 1, frames
os.makedirs(os.path.join(out, which), exist_ok=True)
t0 = time.time()
for f in range(1, frames + 1): sc.frame_set(f)       # simulate (the point cache keeps it)
sim = time.time() - t0
sc.render.filepath = os.path.join(out, which, '')
t1 = time.time(); bpy.ops.render.render(animation=True); ren = time.time() - t1
json.dump({'simulate_s': sim, 'render_s': ren, 'frames': frames, 'points': len(cl.data.vertices)}, open(os.path.join(out, which + '.json'), 'w'))
print('done', which, round(sim, 1), round(ren, 1))
