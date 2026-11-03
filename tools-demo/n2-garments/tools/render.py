"""Blender (4.5, background): a body (.obj, metres) with garments (.obj, centimetres, GarmentCode's output) in the
light of our clothes pictures (beige floor and backdrop, soft sun from the left front, shadow to the right).
blender -b -P render.py -- OUT.png BODY.obj SKIN_HEX [GARMENT.obj HEX]... [--yaw DEG] [--size W H] [--zoom F] [--top Y] """
import bpy, sys, math, mathutils
argv = sys.argv[sys.argv.index('--') + 1:]
opt = {'--yaw': 20.0, '--zoom': 1.0, '--samples': 48}
size = (600, 900); i = 0; pos = []
while i < len(argv):
    if argv[i] == '--size': size = (int(argv[i + 1]), int(argv[i + 2])); i += 3
    elif argv[i] in opt: opt[argv[i]] = float(argv[i + 1]); i += 2
    else: pos.append(argv[i]); i += 1
out, body, skin = pos[0], pos[1], pos[2]
garments = list(zip(pos[3::2], pos[4::2]))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def hexcol(h): h = h.lstrip('#'); return tuple(((int(h[k:k + 2], 16) / 255) ** 2.2) for k in (0, 2, 4)) + (1,)
def mat(name, col, rough=0.75, sheen=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = hexcol(col)
    b.inputs['Roughness'].default_value = rough
    if sheen: b.inputs['Sheen Weight'].default_value = sheen
    return m
def load(path, scale, m):
    bpy.ops.wm.obj_import(filepath=path, forward_axis='NEGATIVE_Z', up_axis='Y', validate_meshes=True)
    o = bpy.context.selected_objects[0]; o.scale = (scale,) * 3
    o.data.materials.clear(); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = True
    return o
load(body, 1.0, mat('skin', skin, 0.5))
for k, (g, col) in enumerate(garments):
    o = load(g, 0.01, mat(f'cloth{k}', col, 0.85, 0.4))
    sol = o.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = 0.002; sol.offset = 1
# floor and backdrop
bpy.ops.mesh.primitive_plane_add(size=30); fl = bpy.context.object; fl.data.materials.append(mat('floor', 'b8ae9f', 0.9))
sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = hexcol('d6cec2'); sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 2.2; sun.data.angle = math.radians(8)
sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
fill = bpy.data.objects.new('fill', bpy.data.lights.new('fill', 'AREA')); sc.collection.objects.link(fill)
fill.data.energy = 250; fill.data.size = 3; fill.location = (2.5, -3, 1.6); fill.rotation_euler = (math.radians(70), 0, math.radians(40))
# the lights turn with the camera (a back view lit as the front one)
rig = bpy.data.objects.new('rig', None); sc.collection.objects.link(rig)
sun.parent = rig; fill.parent = rig; rig.rotation_euler = (0, 0, math.radians(opt['--yaw']))
# camera: front, turned by yaw, framing the whole figure
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 70
yaw = math.radians(opt['--yaw']); d = 5.4 / opt['--zoom']; h = 0.8
cam.location = (d * math.sin(yaw), -d * math.cos(yaw), h + 0.35)
target = mathutils.Vector((0, 0, h))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(opt['--samples']); sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = size
sc.view_settings.view_transform = 'Standard'
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
