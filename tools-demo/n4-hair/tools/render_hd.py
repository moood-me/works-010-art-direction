# Pictures of HairDeck's cards (its GLB, CHARM's dataset frame) in Blender 4.5, the same light as the rest of the page.
#  charm <ply> <glb> <row> <out prefix>: CHARM's test point cloud (its input) and the cards, on HairDeck's own head
#      proxy (hairdeck.vis.head_proxy, moved into the dataset frame with the row's head fit, head_frame_test.npz);
#  ours <style> <glb> <transform json> <out prefix> <colour hex>: the cards moved back from CHARM's frame onto the Anny
#      body the point cloud came from (to_charm.py's transform inverted), in the views of our pictures.
# blender -b --factory-startup -P render_hd.py -- <mode> ...
import bpy, sys, json, math
import numpy as np
from mathutils import Matrix, Vector
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import scene as S

argv = sys.argv[sys.argv.index('--') + 1:]
mode = argv[0]
HD = '/home/user/cache/n4-hair/hdroot/data'

def cards(glb, colour):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb)
    obs = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    m = S.principled('cards', S.srgb(colour), 0.45)
    for o in obs:
        o.data.materials.clear(); o.data.materials.append(m)
        for p in o.data.polygons: p.use_smooth = True
    return obs

if mode == 'charm':
    ply, glb, row, out = argv[1], argv[2], int(argv[3]), argv[4]
    S.reset()
    raw = open(ply, 'rb').read(); e = raw.index(b'end_header\n') + 11
    dt = np.dtype([('p', '<f8', 6), ('c', 'u1', 3)]); X = np.frombuffer(raw[e:], dt)['p'][:, :3]
    hz = np.load(f'{HD}/head_frame_test.npz'); k, b = float(hz['k'][row]), hz['b'][row]
    W, O = float(hz['W']), hz['O']
    ch = O + np.array([0, (-0.547 + 0.10) * W, -0.2 * W]); rad = np.array([0.405, 0.5, 0.5]) * W
    c, r = (ch - b) / k, rad / k
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=tuple(S.bl(c)))
    hd = bpy.context.active_object; hd.scale = tuple(abs(S.bl(r))); hd.data.materials.append(S.principled('head', (0.6, 0.6, 0.6), 0.8))
    for p in hd.data.polygons: p.use_smooth = True
    # the input: points as small spheres (Mesh to Points)
    me = bpy.data.meshes.new('pc'); me.from_pydata(S.bl(X).tolist(), [], []); pc = bpy.data.objects.new('pc', me)
    bpy.context.scene.collection.objects.link(pc)
    ng = bpy.data.node_groups.new('pts', 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    i, o, m2p = ng.nodes.new('NodeGroupInput'), ng.nodes.new('NodeGroupOutput'), ng.nodes.new('GeometryNodeMeshToPoints')
    m2p.inputs['Radius'].default_value = 0.0012
    ng.links.new(i.outputs[0], m2p.inputs[0]); ng.links.new(m2p.outputs[0], o.inputs[0])
    pc.modifiers.new('pts', 'NODES').node_group = ng; pc.data.materials.append(S.principled('pts', (0.25, 0.35, 0.6), 0.6))
    cs = cards(glb, 0x8a6a4a)
    co = S.stage(res=(420, 480), samples=24); bpy.data.objects['ground'].hide_render = True
    tgt = c + np.array([0, -0.03, 0])
    for name, show in (('input', [pc]), ('cards', cs)):
        for ob in [pc] + cs: ob.hide_render = ob not in show
        for v, yaw in (('front', -0.5), ('back', math.pi - 0.5)):
            S.look(co, tgt, yaw, 0.1, 0.62)
            bpy.context.scene.render.filepath = f'{out}-{name}-{v}.png'; bpy.ops.render.render(write_still=True)

if mode == 'ours':
    style, glb, tj, out, colour = argv[1], argv[2], argv[3], argv[4], int(argv[5], 16)
    import build
    H = build.make(style)
    for h in H['hairs']: h.hide_render = True
    for o in bpy.data.objects:
        if o.name.startswith('scalp-'): o.hide_render = True
    T = json.load(open(tj)); c, k, o3 = np.array(T['c']), T['k'], np.array(T['o'])
    cs = cards(glb, colour)
    # dataset frame -> three: P = (X - o) / k + c, done in Blender's axes on the imported objects
    M = Matrix.Translation(Vector(S.bl(c))) @ Matrix.Scale(1 / k, 4) @ Matrix.Translation(-Vector(S.bl(o3)))
    for ob in cs: ob.matrix_world = M @ ob.matrix_world
    co = S.stage(samples=int(argv[6]) if len(argv) > 6 else 32)
    head = np.asarray(H['R']['head'])
    for v, yaw in (('front', -0.55), ('back', math.pi - 0.55)):
        S.look(co, head - np.array([0, 0.03, 0]), yaw, 0.06, H['st']['dist'])
        bpy.context.scene.render.filepath = f'{out}-{v}.png'; bpy.ops.render.render(write_still=True)
