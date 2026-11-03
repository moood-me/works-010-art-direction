# Blender 4.5: Anny's body (as experiments/hair puts it) and a hairstyle made with Blender's own hair tools:
# guide curves on a scalp mesh -> Essentials node groups (Interpolate, Clump, Shrinkwrap, Smooth, Set Profile, ...)
# -> Cycles with the Principled Hair BSDF. Imported by render.py / motion.py.
import bpy, json, math, os
import numpy as np
from mathutils import Matrix, Vector

CACHE = '/home/user/cache/n4-hair'
ESS = bpy.utils.resource_path('LOCAL') + '/datafiles/assets/geometry_nodes/procedural_hair_node_assets.blend'

def bl(p):  # three.js (Y up, face +Z) -> Blender (Z up, face -Y)
    p = np.asarray(p, dtype=np.float64)
    return np.stack([p[..., 0], -p[..., 2], p[..., 1]], -1)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(ESS) as (a, b):
        b.node_groups = [n for n in a.node_groups]

def mesh(name, pos, tris, mat=None):
    me = bpy.data.meshes.new(name)
    v = bl(np.asarray(pos).reshape(-1, 3))
    t = np.asarray(tris).reshape(-1, 3)
    me.from_pydata(v.tolist(), [], t.tolist())
    me.update()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mat: me.materials.append(mat)
    return ob

def principled(name, color, rough=0.6, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (0.02, 0.008, 0.005)
    return m

def srgb(h):
    c = [((h >> s) & 255) / 255 for s in (16, 8, 0)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

WEAR = {'woman': [0xe6e0d4, 0x3f4452, 0x2b211d], 'man': [0xcfc6b4, 0x3e4a5c, 0x2e231c], 'child': [0xe8d9a8, 0x4b5a6e, 0x3a2c25]}

def person(who, skin):
    R = json.load(open(f'{CACHE}/bodies/{who}-rest.json'))
    body = mesh('body', R['body']['pos'], R['body']['tris'], principled('skin', srgb(skin), 0.55, 0.15))
    gs = [mesh(g['name'], g['pos'], g['tris'], principled(g['name'], srgb(c), 0.85)) for g, c in zip(R['garments'], WEAR[who])]
    return R, body, gs

# ———— the skull: an ellipsoid fitted (in three's coordinates) to the body's points above the brows ————
def skull(R):
    P = np.asarray(R['body']['pos']).reshape(-1, 3)
    eyes = np.asarray(R['eyes']); ey = eyes[:, 1].mean(); h = np.asarray(R['head'])
    sel = P[(P[:, 1] > ey + 0.012) & (np.linalg.norm(P - h, axis=1) < 0.2)]
    # axis-aligned ellipsoid a x^2 + b y^2 + c z^2 + d x + e y + f z = 1
    A = np.c_[sel ** 2, sel]; k = np.linalg.lstsq(A, np.ones(len(sel)), rcond=None)[0]
    c = -k[3:] / (2 * k[:3]); g = 1 + (k[3:] ** 2 / (4 * k[:3])).sum(); r = np.sqrt(g / k[:3])
    return c, r, ey

def sph(c, r, th, ph, rr=1.0):  # a point on the (scaled) skull: th azimuth (0 front, + to the person's left), ph elevation
    return c + r * rr * np.array([math.cos(ph) * math.sin(th), math.sin(ph), math.cos(ph) * math.cos(th)])

def scalp(R, c, r, line, region=None, name='scalp'):
    """The body's faces inside the hairline line(th) (elevation) and the part's region(th, ph), lifted 1 mm: the
    surface the hair grows from."""
    P = np.asarray(R['body']['pos']).reshape(-1, 3); T = np.asarray(R['body']['tris']).reshape(-1, 3)
    d = (P - c) / r; th = np.arctan2(d[:, 0], d[:, 2]); ph = np.arcsin(np.clip(d[:, 1] / np.linalg.norm(d, axis=1), -1, 1))
    inside = (ph > np.vectorize(line)(th)) & (np.linalg.norm(P - c, axis=1) < 0.16)
    if region: inside &= np.vectorize(region)(th, ph)
    keep = T[inside[T].all(1)]
    used = np.unique(keep); remap = -np.ones(len(P), int); remap[used] = np.arange(len(used))
    ob = mesh(name, P[used], remap[keep])
    me = ob.data
    for v in me.vertices: v.co += v.normal * 0.001
    me.uv_layers.new(name='UVMap')
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.2, island_margin=0.02); bpy.ops.object.mode_set(mode='OBJECT')
    ob.select_set(False); ob.hide_render = True
    return ob

def hairline(front, side, back):
    def f(th):
        a = abs(th) / math.pi  # 0 front .. 1 back
        if a < 0.5: u = a / 0.5; return front + (side - front) * (1 - math.cos(u * math.pi)) / 2
        u = (a - 0.5) / 0.5; return side + (back - side) * (1 - math.cos(u * math.pi)) / 2
    return f

# ———— guides ————
def guides_object(name, strands, surface):
    """strands: list of (n,3) arrays in three's coordinates -> a hair Curves object on `surface`."""
    cv = bpy.data.hair_curves.new(name)
    cv.add_curves([len(s) for s in strands])
    pts = bl(np.concatenate(strands))
    cv.points.foreach_set('position', pts.astype(np.float32).ravel())
    ob = bpy.data.objects.new(name, cv); bpy.context.scene.collection.objects.link(ob)
    cv.surface = surface; cv.surface_uv_map = 'UVMap'
    # roots onto the surface (Blender's own operator): sets surface_uv_coordinate
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.view_layer.objects: o.select_set(False)
    ob.select_set(True)
    with bpy.context.temp_override(active_object=ob, selected_objects=[ob], object=ob):
        bpy.ops.curves.snap_curves_to_surface(attach_mode='NEAREST')
    return ob

def ease(t): return t * t * (3 - 2 * t)

def strand(c, r, th0, ph0, leave, tip_y, lift=0.08, sweep=0.0, flare=0.0, curl=0.0, n=24, out=None, swing=0.0):
    """One guide: from its root over the skull (azimuth turned by `sweep`) down to elevation `leave`, then hanging to
    height tip_y, flaring out by `flare`, the tip bent toward the head by `curl` (m); `swing` sideways (m) at the tip."""
    pts = []
    m = max(4, int(n * 0.45)) if ph0 > leave else 1
    for i in range(m):
        t = i / max(1, m - 1)
        th = th0 + sweep * ease(t); ph = ph0 + (leave - ph0) * t if m > 1 else ph0
        pts.append(sph(c, r, th, ph, 1.0 + lift * min(1, t * 3) if m > 1 else 1.0))
    p = pts[-1]; th = th0 + sweep
    outd = np.array([math.sin(th), 0, math.cos(th)]) if out is None else np.asarray(out, float)
    side = np.array([math.cos(th), 0, -math.sin(th)])
    drop = p[1] - tip_y
    k = n - m
    for i in range(1, k + 1):
        t = i / k
        q = p + np.array([0, -drop * t, 0]) + outd * flare * math.sin(t * math.pi / 2) - outd * curl * t ** 3 + side * swing * t ** 2
        pts.append(q)
    return np.array(pts)

# ———— Blender's node groups as modifiers ————
def gn(ob, group, **vals):
    m = ob.modifiers.new(group, 'NODES'); m.node_group = bpy.data.node_groups[group]
    ids = {it.name: it.identifier for it in m.node_group.interface.items_tree if it.item_type == 'SOCKET' and it.in_out == 'INPUT'}
    for k, v in vals.items():
        key = ids[k.replace('_', ' ')]
        if isinstance(v, tuple) and v and v[0] == 'attr':
            m[key + '_use_attribute'] = True; m[key + '_attribute_name'] = v[1]
        else:
            m[key] = v
    return m

def hair_material(name, melanin, redness, tint=None, rough=0.25, root=0.12):
    """Blender's Principled Hair BSDF (Chiang) by melanin (natural colours) and a tint (dyed ones); the roots a little
    darker (melanin up by `root` toward the root, along the strand's Intercept), per-strand random colour."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes
    N.remove(N['Principled BSDF'])
    h = N.new('ShaderNodeBsdfHairPrincipled'); h.model = 'CHIANG'; h.parametrization = 'MELANIN'
    info = N.new('ShaderNodeHairInfo'); mr = N.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = min(1, melanin + root); mr.inputs['To Max'].default_value = melanin
    mr.inputs['From Max'].default_value = 0.3
    nt.links.new(info.outputs['Intercept'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], h.inputs['Melanin'])
    h.inputs['Melanin Redness'].default_value = redness
    if tint: h.inputs['Tint'].default_value = (*tint, 1)
    h.inputs['Roughness'].default_value = rough
    h.inputs['Radial Roughness'].default_value = 0.5
    h.inputs['Random Color'].default_value = 0.15
    h.inputs['Random Roughness'].default_value = 0.1
    nt.links.new(h.outputs[0], N['Material Output'].inputs['Surface'])
    return m

# ———— light, camera, render as experiments/hair: hemisphere, key from front-right-above, cool rim from behind ————
def stage(res=(440, 520), samples=48):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = samples; s.cycles.use_denoising = True
    s.cycles.denoiser = 'OPENIMAGEDENOISE'
    s.render.resolution_x, s.render.resolution_y = res; s.render.resolution_percentage = 100
    s.cycles_curves.shape = 'THICK'; s.cycles_curves.subdivisions = 2
    s.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('w'); s.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (*srgb(0xd8d2c8), 1); bg.inputs['Strength'].default_value = 0.75
    def sun(name, energy, color, d):
        L = bpy.data.lights.new(name, 'SUN'); L.energy = energy; L.color = color; L.angle = 0.12
        o = bpy.data.objects.new(name, L); s.collection.objects.link(o)
        o.rotation_euler = Vector(bl(d)).to_track_quat('Z', 'Y').to_euler()
        return o
    sun('key', 2.6, (1, 0.97, 0.92), (1.2, 2.2, 2.4))
    sun('rim', 2.0, (0.85, 0.9, 1.0), (-1.6, 1.4, -2.0))
    g = bpy.data.meshes.new('ground'); g.from_pydata([(-20, -20, 0), (20, -20, 0), (20, 20, 0), (-20, 20, 0)], [], [(0, 1, 2, 3)])
    go = bpy.data.objects.new('ground', g); s.collection.objects.link(go); g.materials.append(principled('ground', srgb(0xcbc3b6), 1))
    cam = bpy.data.cameras.new('cam'); cam.sensor_fit = 'VERTICAL'; cam.angle_y = math.radians(22); cam.clip_start = 0.05
    co = bpy.data.objects.new('cam', cam); s.collection.objects.link(co); s.camera = co
    return co

def look(co, target, yaw, pitch, dist):
    t = np.asarray(target); cp = math.cos(pitch)
    p = t + np.array([math.sin(yaw) * cp * dist, math.sin(pitch) * dist, math.cos(yaw) * cp * dist])
    co.location = Vector(bl(p)); co.rotation_euler = (Vector(bl(t)) - Vector(bl(p))).to_track_quat('-Z', 'Y').to_euler()
