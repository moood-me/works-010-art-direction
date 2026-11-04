# Blender's own cloth (Blender 4.5, mass-spring with collisions) on the same body, garments and motion as our О3 run.
# blender -b -P blender_cloth.py -- <run dir> [frames]
# Reads what export.mjs wrote; writes blender-<garment>.f32 (every frame's points, in the page's Y-up space) and
# blender.json (times, settings). The body is an animated mesh (point cache, MeshCache modifier) with a Collision
# modifier; each garment gets the body's skinning of its dressed shape as its animated base (what its pin group
# follows: waistband, neckline, cuffs — our own hold weights), then Cloth, then Collision (so garments meet each other).
import bpy, sys, os, json, time, struct
import numpy as np

args = sys.argv[sys.argv.index('--') + 1:]
run = args[0]
info = json.load(open(os.path.join(run, 'run.json')))
F = int(args[1]) if len(args) > 1 else info['frames']
N = info['N']
rd = lambda name, dt: np.fromfile(os.path.join(run, name), dtype=dt)
body = rd('body.f32', np.float32).reshape(-1, N, 3)[:F]
E = rd('E.f32', np.float32).reshape(-1, 77, 4, 4)[:F]           # column-major 4x4 as THREE: E[f, j, col, row]
btris = rd('bodytris.u32', np.uint32).reshape(-1, 3)

def zup(p):  # page (x, y up, z toward camera) -> Blender (x, -z, y)
    return np.stack([p[..., 0], -p[..., 2], p[..., 1]], -1)

def write_pc2(path, frames):  # frames [F, n, 3] in Blender space
    with open(path, 'wb') as f:
        f.write(b'POINTCACHE2\0'); f.write(struct.pack('<iiffi', 1, frames.shape[1], 1.0, 1.0, frames.shape[0]))
        f.write(frames.astype('<f4').tobytes())

def mesh_obj(name, verts, tris):
    me = bpy.data.meshes.new(name); me.from_pydata(verts.tolist(), [], tris.tolist()); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob); return ob

def cache(ob, frames, name):
    p = os.path.join(run, f'_{name}.pc2'); write_pc2(p, frames)
    m = ob.modifiers.new('anim', 'MESH_CACHE'); m.cache_format = 'PC2'; m.filepath = p
    m.frame_start = 0; m.frame_scale = 1.0; m.forward_axis = 'POS_Y'; m.up_axis = 'POS_Z'
    return m

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.fps = 30; sc.frame_start = 0; sc.frame_end = F - 1

# the floor
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0)); floor = bpy.context.object
c = floor.modifiers.new('col', 'COLLISION'); floor.collision.thickness_outer = 0.002; floor.collision.cloth_friction = 5

# the body
B = zup(body)
bo = mesh_obj('body', B[0], btris); cache(bo, B, 'body')
bo.modifiers.new('col', 'COLLISION')
bo.collision.thickness_outer = 0.004; bo.collision.cloth_friction = 5; bo.collision.damping = 0.1

# fabric -> Blender settings: Blender's own cloth presets nearest each fabric (Silk, Cotton, Denim, Leather), as an
# artist would set them: mass per point, tension/compression, shear, bending, air damping. (Blender's mass is per point
# and the presets are for coarse meshes, so on 5–9 thousand points a garment is far too heavy — it sags and stretches
# a little. The physical mass — the fabric's kg/m² times the area over the points — was tried too: with the same
# stiffness and 10 steps a frame the blouse became unstable mid-walk, the sleeves torn into strings; pics/blender-light-mass.webp.)
PRESET = {'silk': (0.15, 5, 5, 0.05, 1), 'chiffon': (0.15, 5, 5, 0.05, 1), 'jersey': (0.3, 15, 5, 0.5, 1),
  'heavyjersey': (0.3, 15, 5, 0.5, 1), 'suiting': (0.4, 40, 40, 5, 1), 'denim': (1, 40, 40, 10, 1), 'twill': (1, 40, 40, 10, 1)}

# what each garment meets: the floor, the body, and the garments under it (innermost first, as export.mjs gives them)
under = bpy.data.collections.new('under0'); under.objects.link(floor); under.objects.link(bo)
garms = []
for li, g in enumerate(info['garments']):
    n = g['n']; name = g['name']
    tris = rd(f'{name}-tris.u32', np.uint32).reshape(-1, 3)
    rest = rd(f'{name}-rest.f32', np.float32).reshape(n, 3)
    hold = rd(f'{name}-hold.f32', np.float32)
    J = rd(f'{name}-skinJ.u8', np.uint8).reshape(n, 4); W = rd(f'{name}-skinW.u8', np.uint8).reshape(n, 4).astype(np.float32) / 255
    # the dressed shape carried by the skin, every frame (what the pinned points follow) — as sim.js does
    R = np.concatenate([rest, np.ones((n, 1), np.float32)], 1)
    base = np.zeros((F, n, 3), np.float32)
    ws = W.sum(1, keepdims=True); ws[ws < 1e-6] = 1
    for f in range(F):
        M = E[f].transpose(0, 2, 1)[:, :3, :]           # [77, 3, 4]
        acc = np.zeros((n, 3), np.float32)
        for k in range(4):
            acc += W[:, k:k + 1] * np.einsum('nrc,nc->nr', M[J[:, k]], R)
        base[f] = acc / ws
    G = zup(base)
    ob = mesh_obj(name, G[0], tris); cache(ob, G, name)
    vg = ob.vertex_groups.new(name='hold')
    for i in range(n):
        if hold[i] > 0: vg.add([i], float(min(1, hold[i])), 'REPLACE')
    cm = ob.modifiers.new('cloth', 'CLOTH'); s = cm.settings; cs = cm.collision_settings
    mass, t, sh, bd, air = PRESET[g['fabric']]
    s.mass = mass
    s.tension_stiffness = s.compression_stiffness = t; s.shear_stiffness = sh; s.bending_stiffness = bd
    s.air_damping = air; s.quality = 10; s.vertex_group_mass = 'hold'; s.pin_stiffness = 1
    s.use_dynamic_mesh = False
    cs.collision_quality = 4; cs.distance_min = 0.005; cs.use_self_collision = True; cs.self_distance_min = 0.002
    cs.self_friction = 5; cs.friction = 5
    cm.point_cache.frame_start = 0; cm.point_cache.frame_end = F - 1
    cs.collection = under
    if li < len(info['garments']) - 1:   # a solid for the garments over it
        ob.modifiers.new('col', 'COLLISION'); ob.collision.thickness_outer = g['F']['thick']; ob.collision.cloth_friction = 5
        nxt = bpy.data.collections.new(f'under{li + 1}')
        for o in under.objects: nxt.objects.link(o)
        nxt.objects.link(ob); under = nxt
    garms.append((g, ob, s))
    print(name, n, g['fabric'], PRESET[g['fabric']])

# simulate: step through the frames, read the cloth back
outs = {g['name']: np.zeros((F, g['n'], 3), np.float32) for g, _, _ in garms}
t0 = time.time()
for f in range(F):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    for g, ob, _ in garms:
        me = ob.evaluated_get(dg).to_mesh(); a = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', a)
        a = a.reshape(-1, 3); outs[g['name']][f] = np.stack([a[:, 0], a[:, 2], -a[:, 1]], -1)
        ob.evaluated_get(dg).to_mesh_clear()
    if f % 20 == 0: print('frame', f, round(time.time() - t0, 1), 's', flush=True)
secs = time.time() - t0
for k, v in outs.items(): v.tofile(os.path.join(run, f'blender-{k}.f32'))
json.dump({'seconds': secs, 'frames': F, 'garments': {g['name']: {'mass': s.mass, 'quality': s.quality} for g, _, s in garms}},
          open(os.path.join(run, 'blender.json'), 'w'), indent=1)
print('done', F, 'frames', round(secs, 1), 's')
