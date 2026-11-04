"""Тим rendered as a puppet on a small set — Blender 4.5, Cycles on the CPU.

The look of С8 (styles/s8-stopmotion, «Правила стиля»): a small real object under real light. Every part has its
own material: the face resin-and-clay skin with light under it (subsurface), glass eyes with a sharp window glint,
sculpted hair with grooves and fine strands, a knitted sweater (ribs, stripes knitted in, fuzz), felt shorts, ribbed
socks, red shoes with a rubber sole. One warm key from the upper left, a cool rim from behind on the right, a dim fill;
behind him a dark set with out-of-focus lamps (real bokeh: small lights far behind, a lens with a shallow focus).

usage: blender -b -P render.py -- JOB.json
JOB: {scene: CACHE/scene.npz, out: dir, samples, views: [{name, W, H, cam, at?, frame?}], frames?: path.bin,
      frame_ids?: [...], stage?: {...}}
cam: {type: 'view', yaw, S, cx, cy, at: [x,y,z], fstop?}  — the drawing's view: S px per head unit, the point `at`
     (engine metres) on pixel (cx, cy), seen through a long lens from far; or {type: 'persp', pos, target, lens, fstop, focus?}.
scene.npz: <name>_V (N×3 engine metres: x his left, y up, z forward), <name>_T, optional <name>_uv, <name>_pat;
scene.json: {objects: [{name, mat}], HH}.
frames (optional): float32 frames × N × 3 of the whole model in scene order (see move.mjs), replacing the rest."""
import bpy, sys, json, math, os
import numpy as np
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index('--') + 1:]
job = json.load(open(args[0]))
SC = np.load(job['scene'])
meta = json.load(open(job['scene'].replace('.npz', '.json')))
TEX = meta['tex']
HH = meta['HH']


def lin(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0]


def B(P):
    """engine axes → Blender's (z up, the figure facing −y)"""
    P = np.asarray(P, float)
    return np.stack([P[..., 0], -P[..., 2], P[..., 1]], -1)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = job.get('samples', 64)
sc.cycles.use_denoising = True
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = job.get('noise', 0.03)
try:
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception:
    pass
sc.cycles.max_bounces = 6
sc.cycles.transparent_max_bounces = 4
sc.cycles.caustics_reflective = False
sc.cycles.caustics_refractive = False
sc.cycles.blur_glossy = 1.0
sc.render.threads_mode = 'FIXED'
sc.render.threads = job.get('threads', 4)
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = job.get('exposure', 0.0)
sc.render.film_transparent = False
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = lin('#0b0c10')
world.node_tree.nodes['Background'].inputs[1].default_value = 1.0


# ------------------------------------------------------------------ materials
def nodes(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return m, nt, bsdf


def attr(nt, name, kind='GEOMETRY'):
    a = nt.nodes.new('ShaderNodeAttribute'); a.attribute_name = name; return a


def sep(nt, sock):
    s = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(sock, s.inputs[0]); return s


def math_(nt, op, a, b=None, c=None):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def mixc(nt, fac, a, b):
    n = nt.nodes.new('ShaderNodeMix'); n.data_type = 'RGBA'
    if isinstance(fac, (int, float)): n.inputs[0].default_value = fac
    else: nt.links.new(fac, n.inputs[0])
    for i, v in ((6, a), (7, b)):
        if isinstance(v, (list, tuple)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs[2]


def bump(nt, bsdf, height, strength, dist=0.002, normal=None):
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = strength; b.inputs['Distance'].default_value = dist
    nt.links.new(height, b.inputs['Height'])
    if normal is not None: nt.links.new(normal, b.inputs['Normal'])
    nt.links.new(b.outputs[0], bsdf.inputs['Normal'])
    return b.outputs[0]


def noise(nt, vec, scale, detail=4.0, rough=0.6):
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = scale
    n.inputs['Detail'].default_value = detail; n.inputs['Roughness'].default_value = rough
    if vec is not None: nt.links.new(vec, n.inputs['Vector'])
    return n.outputs['Fac']


def image(nt, path, vec, extension='EXTEND', non_color=False):
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path); t.extension = extension
    if non_color: t.image.colorspace_settings.name = 'Non-Color'
    nt.links.new(vec, t.inputs['Vector'])
    return t


def set_(bsdf, **kw):
    names = {'base': 'Base Color', 'rough': 'Roughness', 'sss': 'Subsurface Weight', 'sss_r': 'Subsurface Radius',
             'sss_s': 'Subsurface Scale', 'coat': 'Coat Weight', 'coat_r': 'Coat Roughness', 'sheen': 'Sheen Weight',
             'sheen_r': 'Sheen Roughness', 'sheen_t': 'Sheen Tint', 'spec': 'Specular IOR Level', 'ior': 'IOR'}
    for k, v in kw.items(): bsdf.inputs[names[k]].default_value = v


def mat_skin():
    m, nt, b = nodes('skin')
    uv = attr(nt, 'tuv')
    img = image(nt, os.path.join(TEX, 'face.png'), uv.outputs['Vector'])
    tint = attr(nt, 'tint')                     # ears and hands warmer (per vertex)
    col = mixc(nt, tint.outputs['Fac'], img.outputs['Color'], lin('#e8a090'))
    nt.links.new(col, b.inputs['Base Color'])
    set_(b, rough=0.42, sss=0.35, sss_r=(1.0, 0.45, 0.3), sss_s=0.012, coat=0.12, coat_r=0.35, spec=0.45)
    # resin cast: the faintest unevenness, fingerprints of the sculptor
    tc = nt.nodes.new('ShaderNodeTexCoord')
    h = math_(nt, 'MULTIPLY', noise(nt, tc.outputs['Object'], 140.0, 6, 0.55), 1.0)
    bump(nt, b, h, 0.05, 0.001)
    return m


def mat_hair():
    m, nt, b = nodes('hair')
    uv = sep(nt, attr(nt, 'tuv').outputs['Vector'])
    base = lin('#7a4220')
    # fine strands across each lock (the drawing's strand lines) and its grooves: stripes in the across coordinate
    across = uv.outputs['X']
    w = math_(nt, 'MULTIPLY', across, 9.0)
    s1 = math_(nt, 'SINE', math_(nt, 'MULTIPLY', w, math.pi))
    s2 = math_(nt, 'SINE', math_(nt, 'MULTIPLY', across, 37.0))
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = noise(nt, tc.outputs['Object'], 60.0, 3, 0.5)
    h = math_(nt, 'ADD', math_(nt, 'MULTIPLY', s1, 0.6), math_(nt, 'MULTIPLY', s2, 0.25))
    h = math_(nt, 'ADD', h, math_(nt, 'MULTIPLY', nz, 0.4))
    bump(nt, b, h, 0.25, 0.0015)
    dark = math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', 1.0, math_(nt, 'ABSOLUTE', s1)), 0.0)
    col = mixc(nt, math_(nt, 'MULTIPLY', nz, 0.35), base, lin('#5a2c12'))
    nt.links.new(col, b.inputs['Base Color'])
    set_(b, rough=0.5, coat=0.25, coat_r=0.3, spec=0.5, sheen=0.15, sheen_r=0.4)
    return m


def mat_eye():
    m, nt, b = nodes('eye')
    uv = attr(nt, 'tuv')
    img = image(nt, os.path.join(TEX, 'iris.png'), uv.outputs['Vector'])
    nt.links.new(img.outputs['Color'], b.inputs['Base Color'])
    set_(b, rough=0.25, coat=1.0, coat_r=0.02, spec=0.6, sss=0.1, sss_r=(1, 0.8, 0.7), sss_s=0.005)
    return m


def mat_knit(name, base, stripe=None, period=None, y0=0.0, rib=0.0045):
    """knitting: vertical ribs (the uv's across coordinate in metres), stitches as small Vs along them, stripes by
    the rest height (pat.y), fuzz (sheen)"""
    m, nt, b = nodes(name)
    uv = sep(nt, attr(nt, 'tuv').outputs['Vector'])
    pat = sep(nt, attr(nt, 'pat').outputs['Vector'])
    u = math_(nt, 'DIVIDE', uv.outputs['X'], rib)
    v = math_(nt, 'DIVIDE', uv.outputs['Y'], rib * 0.75)
    ribs = math_(nt, 'ABSOLUTE', math_(nt, 'SINE', math_(nt, 'MULTIPLY', u, math.pi)))
    # stitches: each rib a column of small chevrons
    st = math_(nt, 'FRACT', math_(nt, 'ADD', v, math_(nt, 'MULTIPLY', math_(nt, 'ABSOLUTE', math_(nt, 'SUBTRACT', math_(nt, 'FRACT', u), 0.5)), 1.2)))
    st = math_(nt, 'ABSOLUTE', math_(nt, 'SUBTRACT', st, 0.5))
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = noise(nt, tc.outputs['Object'], 220.0, 3, 0.6)
    h = math_(nt, 'ADD', math_(nt, 'MULTIPLY', ribs, 0.8), math_(nt, 'MULTIPLY', st, 0.5))
    h = math_(nt, 'ADD', h, math_(nt, 'MULTIPLY', nz, 0.3))
    bump(nt, b, h, 0.6, 0.0016)
    col = base
    if stripe:
        k = math_(nt, 'FRACT', math_(nt, 'DIVIDE', math_(nt, 'SUBTRACT', pat.outputs['Y'], y0), 2 * period))
        f = math_(nt, 'GREATER_THAN', k, 0.5)
        col = mixc(nt, f, base, stripe)
    # yarn colour varies a little; deeper between the ribs
    col = mixc(nt, math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', 1.0, ribs), 0.35), col, lin('#000000'))
    nt.links.new(col, b.inputs['Base Color'])
    set_(b, rough=0.85, sheen=0.6, sheen_r=0.45, spec=0.25)
    return m


def mat_felt(name, base):
    m, nt, b = nodes(name)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = noise(nt, tc.outputs['Object'], 400.0, 8, 0.75)
    nz2 = noise(nt, tc.outputs['Object'], 30.0, 2, 0.5)
    bump(nt, b, math_(nt, 'ADD', nz, math_(nt, 'MULTIPLY', nz2, 0.5)), 0.35, 0.002)
    col = mixc(nt, math_(nt, 'MULTIPLY', nz2, 0.4), base, lin('#3a3226'))
    nt.links.new(col, b.inputs['Base Color'])
    set_(b, rough=0.95, sheen=0.8, sheen_r=0.6, spec=0.2)
    return m


def mat_plain(name, base, rough=0.5, coat=0.0, sheen=0.0, sss=0.0, bump_scale=0.0):
    m, nt, b = nodes(name)
    nt.links.new(nt.nodes.new('ShaderNodeRGB').outputs[0], b.inputs['Base Color'])
    b.inputs['Base Color'].links[0].from_node.outputs[0].default_value = base
    set_(b, rough=rough, coat=coat, coat_r=0.25, sheen=sheen, sss=sss, sss_r=(1, 0.5, 0.4), sss_s=0.01)
    if bump_scale:
        tc = nt.nodes.new('ShaderNodeTexCoord')
        bump(nt, b, noise(nt, tc.outputs['Object'], bump_scale, 4, 0.6), 0.15, 0.001)
    return m


MATS = {
    'skin': mat_skin, 'hair': mat_hair, 'eye': mat_eye,
    'sweater': lambda: mat_knit('sweater', lin('#2c4a72'), lin('#f0e6d2'), 0.09 * HH, meta.get('stripe_y0', 0.0)),
    'cuff': lambda: mat_knit('cuff', lin('#24406a'), rib=0.003),
    'sock': lambda: mat_knit('sock', lin('#e8e0d0'), rib=0.0035),
    'shorts': lambda: mat_felt('shorts', lin('#6a5a3a')),
    'shoe': lambda: mat_plain('shoe', lin('#c83a2a'), rough=0.38, coat=0.35, bump_scale=300),
    'sole': lambda: mat_plain('sole', lin('#efe6d6'), rough=0.7, bump_scale=200),
    'lip': lambda: mat_plain('lip', lin('#c8706a'), rough=0.35, coat=0.2, sss=0.3),
    'mouth': lambda: mat_plain('mouth', lin('#3a1418'), rough=0.6),
    'teeth': lambda: mat_plain('teeth', lin('#f1e8dc'), rough=0.3, coat=0.3),
    'tongue': lambda: mat_plain('tongue', lin('#a8444a'), rough=0.4, sss=0.3),
    'brow': lambda: mat_plain('brow', lin('#5a3018'), rough=0.6, sheen=0.3, bump_scale=600),
    'lash': lambda: mat_plain('lash', lin('#2a1810'), rough=0.5),
    'clay': lambda: mat_plain('clay', lin('#c9c2b6'), rough=0.6),
}
MCACHE = {}


def material(name):
    if job.get('clay') and name not in ('eye',):
        name = 'clay'
    if name not in MCACHE: MCACHE[name] = MATS[name]()
    return MCACHE[name]


# ------------------------------------------------------------------ the puppet
OBJ = {}
for o in meta['objects']:
    n = o['name']
    V = B(SC[n + '_V']); T = SC[n + '_T'].astype(int)
    me = bpy.data.meshes.new(n)
    me.from_pydata(V.tolist(), [], T.tolist())
    for key in ('uv', 'pat', 'tint'):  # stored as tuv, pat, tint ("uv" is taken by UV maps)
        if n + '_' + key in SC:
            a = SC[n + '_' + key]
            if key == 'tint':
                at = me.attributes.new('tint', 'FLOAT', 'POINT'); at.data.foreach_set('value', a.astype(float).ravel())
            else:
                a3 = np.c_[a, np.zeros((len(a), 3 - a.shape[1]))] if a.shape[1] < 3 else a
                at = me.attributes.new('tuv' if key == 'uv' else key, 'FLOAT_VECTOR', 'POINT'); at.data.foreach_set('vector', a3.astype(float).ravel())
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.update()
    ob = bpy.data.objects.new(n, me); sc.collection.objects.link(ob)
    ob.data.materials.append(material(o['mat']))
    if o.get('subdiv'):
        s = ob.modifiers.new('s', 'SUBSURF'); s.levels = s.render_levels = o['subdiv']
    OBJ[n] = (ob, len(V))

# ------------------------------------------------------------------ the set
st = dict(dict(floor='#2e2a2a', back='#1e2430', glow='#d89a60', seed=8), **job.get('stage', {}))


def plane(name, size, loc, rot, mat):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
    ob = bpy.context.active_object; ob.name = name; ob.data.materials.append(mat); return ob


fm, fnt, fb = nodes('floor')
tc = fnt.nodes.new('ShaderNodeTexCoord')
wood = fnt.nodes.new('ShaderNodeTexWave'); wood.wave_type = 'BANDS'; wood.inputs['Scale'].default_value = 3.0
wood.inputs['Distortion'].default_value = 6.0; wood.inputs['Detail'].default_value = 4
fnt.links.new(tc.outputs['Object'], wood.inputs['Vector'])
fcol = mixc(fnt, math_(fnt, 'MULTIPLY', wood.outputs['Fac'], 0.5), lin(st['floor']), lin('#1a1616'))
fnt.links.new(fcol, fb.inputs['Base Color'])
set_(fb, rough=0.55, spec=0.4)
plane('floor', 40, (0, 0, 0), (0, 0, 0), fm)
bm, bnt, bb = nodes('backdrop')
bnt.links.new(bnt.nodes.new('ShaderNodeRGB').outputs[0], bb.inputs['Base Color'])
bb.inputs['Base Color'].links[0].from_node.outputs[0].default_value = lin(st['back'])
set_(bb, rough=0.9)
plane('back', 40, (0, 6.0, 4), (math.radians(90), 0, 0), bm)

# bokeh: small warm and cool lamps scattered far behind (out of focus they become discs)
rng = np.random.default_rng(st['seed'])
cols = ['#ffcf8a', '#ffb070', '#ffe0b0', '#9ab8ff', '#ff9a70']
for i in range(26):
    x = rng.uniform(-3.2, 3.2); z = rng.uniform(0.4, 3.0); y = rng.uniform(3.5, 5.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rng.uniform(0.02, 0.05), location=(x, y, z), segments=12, ring_count=6)
    s = bpy.context.active_object
    em = bpy.data.materials.new(f'bk{i}'); em.use_nodes = True
    e = em.node_tree.nodes; o_ = e['Material Output']
    for n in list(e):
        if n != o_: e.remove(n)
    E = e.new('ShaderNodeEmission'); E.inputs[0].default_value = lin(cols[rng.integers(len(cols))])
    E.inputs[1].default_value = rng.uniform(8, 30)
    em.node_tree.links.new(E.outputs[0], o_.inputs[0])
    s.data.materials.append(em)
    s.visible_shadow = False; s.visible_diffuse = False; s.visible_glossy = False


def area(name, loc, target, size, power, col):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = power; l.color = lin(col)[:3]
    ob = bpy.data.objects.new(name, l); sc.collection.objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc); ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


def lights(centre, yaw=0.0):
    """the key, rim and fill turn with the camera (a turntable: the puppet turns, the lamps stay where the camera
    sees them), the glow on the backdrop stays"""
    c = Vector(centre)
    k = job.get('light', 1.0)
    R = Matrix.Rotation(-yaw, 3, 'Z')
    area('key', c + R @ Vector((-1.6, -1.8, 1.9)), c, 0.9, 260 * k, '#ffd8a8')
    area('rim', c + R @ Vector((1.5, 1.6, 1.1)), c, 0.6, 160 * k, '#a8c4ff')
    area('fill', c + R @ Vector((1.8, -1.6, 0.2)), c, 1.6, 30 * k, '#b8c0d8')
    area('glow', Vector((-0.8, 5.0, 2.4)), Vector((0, 6.0, 2.0)), 3.0, 900 * k, st['glow'])


# ------------------------------------------------------------------ cameras and output
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam


def set_cam(c, W, H):
    sc.render.resolution_x, sc.render.resolution_y = W, H
    cd = cam.data
    if c['type'] == 'view':
        # the drawing's view (orthographic in the drawing) as a long lens from far away — nearly orthographic, and a
        # real lens, so the set's lamps behind go out of focus: S px per head unit, the point `at` on pixel (cx, cy)
        yaw = math.radians(c['yaw']); pxm = c['S'] / HH
        lens = c.get('lens', 300.0)
        at = np.array(c['at'])
        d = W * lens * 1e-3 / (36e-3 * pxm)
        fwd = np.array([-math.sin(yaw), 0, math.cos(yaw)])
        pos = at + fwd * d
        cd.type = 'PERSP'; cd.lens = lens; cd.sensor_width = 36; cd.sensor_fit = 'HORIZONTAL'
        cam.location = Vector(B(pos)); look = Vector(B(at)) - cam.location
        cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
        cd.shift_x = (W / 2 - c['cx']) / W
        cd.shift_y = (c['cy'] - H / 2) / W
        cd.clip_end = 200
        cd.dof.use_dof = True; cd.dof.focus_distance = d; cd.dof.aperture_fstop = c.get('fstop', 8.0)
        lights(B(at), yaw)
    else:
        pos, tgt = np.array(c['pos']), np.array(c['target'])
        cd.type = 'PERSP'; cd.lens = c.get('lens', 50); cd.sensor_width = 36
        cam.location = Vector(B(pos)); look = Vector(B(tgt)) - cam.location
        cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
        cd.dof.use_dof = True
        cd.dof.focus_distance = c.get('focus', float(np.linalg.norm(tgt - pos)))
        cd.dof.aperture_fstop = c.get('fstop', 2.8)
        cd.clip_start = 0.05
        d = pos - tgt
        lights(B(c.get('light_at', tgt)), c.get('light_yaw', math.atan2(d[0], d[2])))


os.makedirs(job['out'], exist_ok=True)
frames = None
if job.get('frames'):
    fr = np.fromfile(job['frames'], np.float32)
    NTOT = sum(n for _, n in OBJ.values())
    frames = fr.reshape(-1, NTOT, 3)


def apply_frame(i):
    off = 0
    for o in meta['objects']:
        ob, n = OBJ[o['name']]
        P = B(frames[i, off:off + n]); off += n
        ob.data.vertices.foreach_set('co', P.astype(np.float32).ravel())
        ob.data.update()


for v in job['views']:
    for l in [o for o in sc.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(l)
    if frames is not None and v.get('frame') is not None:
        apply_frame(v['frame'])
    set_cam(v['cam'], v['W'], v['H'])
    sc.render.filepath = os.path.join(job['out'], v['name'] + '.png')
    bpy.ops.render.render(write_still=True)
    print('wrote', sc.render.filepath, flush=True)
