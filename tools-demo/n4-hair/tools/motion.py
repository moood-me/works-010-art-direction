# A hairstyle of build.py in motion on Anny's body through a Kimodo motion (exported by bodies.mjs):
#  - the body and its clothes: Blender's Mesh Cache modifier (the motion's points, every frame);
#  - the scalp and the hair follow the Head joint (an empty keyed with the head's matrix every frame);
#  - dyn: Blender's own hair dynamics — the guide curves turned into a particle hair system (Blender's operator
#    curves.convert_to_particle_system) with Hair Dynamics on (the cloth solver for hair), colliding with the body and
#    the T-shirt; each frame the simulated guides are written back into the Curves object, whose node groups
#    (Interpolate, Clump, ...) grow the hairstyle from them.
# blender -b --factory-startup -P motion.py -- <style> <motion-turns> <out dir> [dyn|rigid] [step] [samples] [view]
import bpy, sys, math, json, os
import numpy as np
from mathutils import Matrix, Vector
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import scene as S, build

argv = sys.argv[sys.argv.index('--') + 1:]
name, clip, out = argv[0], argv[1], argv[2]
mode = argv[3] if len(argv) > 3 else 'dyn'
step = int(argv[4]) if len(argv) > 4 else 2
samples = int(argv[5]) if len(argv) > 5 else 10
yaw = float(argv[6]) if len(argv) > 6 else -0.55
os.makedirs(out, exist_ok=True)
STIFF = {'gwen': 2.0, 'marco': 5.0, 'alva': 0.5, 'kpony': 0.5}   # bending stiffness of each hairstyle's guides

H = build.make(name)
who = H['who']; R = H['R']
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))

# ———— the body in motion: one PC2 per object, in Blender's axes ————
src = f'{S.CACHE}/bodies/{who}-{clip}.pc2'
raw = open(src, 'rb').read(); V = np.frombuffer(raw, '<i4', 1, 16)[0]; F = np.frombuffer(raw, '<i4', 1, 28)[0]
P = np.frombuffer(raw, '<f4', F * V * 3, 32).reshape(F, V, 3)
objs = [bpy.data.objects['body']] + [bpy.data.objects[g['name']] for g in R['garments']]
at = 0
for o in objs:
    n = len(o.data.vertices); Q = S.bl(P[:, at:at + n]).astype('<f4'); at += n
    fn = f'{S.CACHE}/bodies/split-{who}-{clip}-{o.name}.pc2'
    with open(fn, 'wb') as f:
        f.write(b'POINTCACHE2\0' + np.array([1, n], '<i4').tobytes() + np.array([0, 1], '<f4').tobytes() + np.array([F], '<i4').tobytes())
        f.write(Q.tobytes())
    m = o.modifiers.new('motion', 'MESH_CACHE'); m.cache_format = 'PC2'; m.filepath = fn
    m.forward_axis = 'POS_Y'; m.up_axis = 'POS_Z'; m.frame_start = 1
assert at == V

# ———— the head: an empty keyed with the Head joint's matrix ————
heads = json.load(open(f'{S.CACHE}/bodies/{who}-{clip}-head.json'))
head = bpy.data.objects.new('head', None); bpy.context.scene.collection.objects.link(head)
head.rotation_mode = 'QUATERNION'
for f, e in enumerate(heads):
    M = Matrix([[e[c * 4 + r] for c in range(4)] for r in range(4)])
    head.matrix_world = C @ M @ C.inverted()
    head.keyframe_insert('location', frame=f + 1); head.keyframe_insert('rotation_quaternion', frame=f + 1)
followers = [o for o in bpy.data.objects if o.name.startswith(('hair-', 'scalp-')) or o.name == 'tie']
for o in followers: o.parent = head; o.matrix_parent_inverse = Matrix()

sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, F; sc.render.fps = 30
dyn = []
if mode == 'dyn':
    for o in objs[:2]:  # the body and the T-shirt: what the hair meets
        o.modifiers.new('collision', 'COLLISION'); o.collision.thickness_outer = 0.006; o.collision.cloth_friction = 5
    for hair in [o for o in bpy.data.objects if o.name.startswith('hair-')]:
        scalp = hair.data.surface
        for o in bpy.context.view_layer.objects: o.select_set(False)
        hair.select_set(True); bpy.context.view_layer.objects.active = hair
        with bpy.context.temp_override(active_object=hair, selected_objects=[hair], selected_editable_objects=[hair], object=hair):
            bpy.ops.curves.convert_to_particle_system()
        ps = scalp.particle_systems[-1]; st = ps.settings
        ps.use_hair_dynamics = True
        cs = ps.cloth.settings; cs.quality = 8; cs.mass = 0.3; cs.air_damping = 1.5
        cs.bending_stiffness = STIFF.get(name, 0.5); cs.pin_stiffness = 0.6; cs.bending_damping = 0.6
        cs.internal_friction = 0.2
        st.render_type = 'NONE'; st.display_step = 5
        ps.point_cache.frame_start = 1; ps.point_cache.frame_end = F
        n = len(hair.data.curves); k = len(hair.data.points) // n
        dyn.append((hair, scalp, n, k))
        print('dynamics on', hair.name, n, 'guides', k, 'points each')

def resample(A, k):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(A, axis=0), axis=1))]; t = np.linspace(0, d[-1], k)
    return np.stack([np.interp(t, d, A[:, c]) for c in range(3)], -1)

co = S.stage(res=(400, 470), samples=samples)
sc.frame_end = F
rest = {h.name: np.array([p.position[:] for p in h.data.points]) for h, *_ in dyn}
for f in range(1, F + 1):
    sc.frame_set(f)
    if dyn:
        dg = bpy.context.evaluated_depsgraph_get()
        for hair, scalp, n, k in dyn:
            se = scalp.evaluated_get(dg); ps = se.particle_systems[-1]
            m = 2 ** ps.settings.display_step   # co_hair gives the drawn hair: 2^display_step segments, resampled to k points
            W = np.concatenate([resample(np.array([ps.co_hair(se, particle_no=i, step=s)[:] for s in range(m + 1)]), k) for i in range(n)])
            if not np.isfinite(W).all() or np.abs(W).sum() == 0: continue
            inv = hair.matrix_world.inverted()
            L = np.array([(inv @ Vector(w))[:] for w in W])
            hair.data.points.foreach_set('position', L.astype(np.float32).ravel())
            hair.data.update_tag()
    if (f - 1) % step: continue
    hp = head.matrix_world @ Vector(S.bl(R['head'])); target = np.array([hp.x, hp.z - 0.03, -hp.y])
    S.look(co, target, yaw, 0.06, H['st']['dist'])
    sc.render.filepath = f'{out}/{f:04d}.png'
    bpy.ops.render.render(write_still=True)
