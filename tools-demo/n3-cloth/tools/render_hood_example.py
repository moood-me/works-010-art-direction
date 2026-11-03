# Draws HOOD's own example (hood_example.py's npz: SMPL body and the T-shirt HOOD simulated on it) with Blender EEVEE.
# blender -b -P render_hood_example.py -- <npz> <out dir>
import bpy, sys, os, struct, math
import numpy as np

npz, out = sys.argv[sys.argv.index('--') + 1:][:2]
d = np.load(npz)
def zup(p): return np.stack([p[..., 0], -p[..., 2], p[..., 1]], -1)   # HOOD's Y up -> Blender's Z up
cloth, body = zup(d['cloth']), zup(d['body'])
F = min(len(cloth), len(body))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start, sc.frame_end = 0, F - 1
sc.render.engine = 'BLENDER_EEVEE_NEXT'; sc.eevee.taa_render_samples = 16
sc.render.resolution_x, sc.render.resolution_y = 400, 480; sc.render.image_settings.file_format = 'PNG'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.81, 0.78, 0.74, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.7

def mat(rgb, rough):
    m = bpy.data.materials.new('m'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; return m

def animated(name, frames, faces, m):
    me = bpy.data.meshes.new(name); me.from_pydata(frames[0].tolist(), [], faces.tolist()); me.update()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob); me.materials.append(m)
    p = os.path.join(out, name + '.pc2')
    with open(p, 'wb') as f:
        f.write(b'POINTCACHE2\0'); f.write(struct.pack('<iiffi', 1, frames.shape[1], 0.0, 1.0, frames.shape[0])); f.write(frames.astype('<f4').tobytes())
    c = ob.modifiers.new('a', 'MESH_CACHE'); c.cache_format = 'PC2'; c.filepath = p; c.frame_start = 0; c.forward_axis = 'POS_Y'; c.up_axis = 'POS_Z'
    return ob

os.makedirs(out, exist_ok=True)
animated('body', body[:F], d['body_faces'], mat((0.85, 0.62, 0.5), 0.6))
animated('shirt', cloth[:F], d['cloth_faces'], mat((0.25, 0.45, 0.6), 0.85))
floor_z = body[:F, :, 2].min()
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, floor_z)); bpy.context.object.data.materials.append(mat((0.62, 0.58, 0.53), 1))
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(50), math.radians(10), math.radians(-35))); bpy.context.object.data.energy = 3.5
# the camera follows the body (its centre, smoothed), from the front-right
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam
look = bpy.data.objects.new('look', None); sc.collection.objects.link(look)
t = cam.constraints.new('TRACK_TO'); t.target = look; t.track_axis = 'TRACK_NEGATIVE_Z'; t.up_axis = 'UP_Y'
c = body[:F].mean(1); k = np.ones(15) / 15; c = np.stack([np.convolve(np.pad(c[:, i], 7, mode='edge'), k, 'valid') for i in range(3)], 1)
for f in range(F):
    look.location = c[f]; look.keyframe_insert('location', frame=f)
    cam.location = c[f] + np.array([2.0, -2.8, 0.4]); cam.keyframe_insert('location', frame=f)
sc.render.filepath = os.path.join(out, '')
sc.frame_end = int(os.environ.get('LAST', F - 1))
bpy.ops.render.render(animation=True)
