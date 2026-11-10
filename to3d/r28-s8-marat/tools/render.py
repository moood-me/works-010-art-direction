"""Марат rendered as a puppet on a small set — Blender 4.5, Cycles on the CPU.

The look of С8 (styles/s8-stopmotion, «Правила стиля»): a small real object under real light. Every part has its
own material: the face resin-and-clay skin with light under it (subsurface), glass eyes with a sharp window glint,
sculpted hair with grooves and fine strands, a knitted sweater (ribs, stripes knitted in, fuzz), felt shorts, ribbed
socks, red shoes with a rubber sole. One warm key from the upper left, a cool rim from behind on the right, a dim fill;
behind him a dark set with out-of-focus lamps (real bokeh: small lights far behind, a lens with a shallow focus).

usage: blender -b -P render.py -- JOB.json
JOB: {out: dir, samples, views: [{name, W, H, cam, at?, frame?}], frames?: path.bin,
      frame_ids?: [...], stage?: {...}}
cam: {type: 'view', yaw, S, cx, cy, at: [x,y,z], fstop?}  — the drawing's view: S px per head unit, the point `at`
     (engine metres) on pixel (cx, cy), seen through a long lens from far; or {type: 'persp', pos, target, lens, fstop, focus?}.
The model: CACHE/engine/data/{bodies,topology}/marat8.* (build.py), its pieces and materials in CACHE/model.json,
the paint coordinates in CACHE/rest.npz. frames (optional): float32 frames × N × 3 (move.mjs), replacing the rest."""
import bpy, sys, json, math, os
import numpy as np
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index('--') + 1:]
job = json.load(open(args[0]))
CACHE = job.get('cache', '/home/user/cache/to3d-r28-s8-marat')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../engine/tools'))
import pack  # noqa: E402
meta = json.load(open(os.path.join(CACHE, 'model.json')))
BID = meta['id']
_, BA = pack.read(os.path.join(CACHE, f'engine/data/bodies/{BID}.json'))
_, TA = pack.read(os.path.join(CACHE, f'engine/data/topology/{BID}.json'))
RA = np.load(os.path.join(CACHE, 'rest.npz'))
TEX = meta['tex']
HH = meta['HH']
NTOT = len(BA['positions'])

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
sc.view_settings.view_transform = job.get('view', 'Filmic')
sc.view_settings.look = job.get('look', 'Medium High Contrast')
sc.view_settings.exposure = job.get('exposure', 0.25)
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
             'sheen_r': 'Sheen Roughness', 'sheen_t': 'Sheen Tint', 'spec': 'Specular IOR Level', 'ior': 'IOR', 'metal': 'Metallic',
             'alpha': 'Alpha', 'trans': 'Transmission Weight'}
    for k, v in kw.items(): bsdf.inputs[names[k]].default_value = v


def mat_skin():
    m, nt, b = nodes('skin')
    uv = attr(nt, 'tuv')
    img = image(nt, os.path.join(TEX, 'face.png'), uv.outputs['Vector'])
    tint = attr(nt, 'tint')                     # ears and hands warmer (per vertex)
    # Filmic pales a light skin: a little of a warmer, pinker one under the paint (the drawing's skin reads warm)
    warm = mixc(nt, SKIN_K, img.outputs['Color'], lin(SKIN_WARM))
    col = mixc(nt, tint.outputs['Fac'], warm, lin(SKIN_TINT))
    nt.links.new(col, b.inputs['Base Color'])
    set_(b, rough=0.42, sss=0.35, sss_r=(1.0, 0.45, 0.3), sss_s=0.012, coat=0.12, coat_r=0.35, spec=0.45)
    # resin cast: the faintest unevenness, fingerprints of the sculptor
    tc = nt.nodes.new('ShaderNodeTexCoord')
    h = math_(nt, 'MULTIPLY', noise(nt, tc.outputs['Object'], 140.0, 6, 0.55), 1.0)
    n1 = bump(nt, b, h, 0.05, 0.001)
    if os.path.exists(os.path.join(TEX, 'bump.png')):          # the sculpted wrinkles
        bi = image(nt, os.path.join(TEX, 'bump.png'), uv.outputs['Vector'], non_color=True)
        bump(nt, b, bi.outputs['Color'], 0.6, 0.0012, normal=n1)
    return m


def mat_hair(name='hair', base_c='#6a3e24', dark_c='#5a2c12', rough=0.5, coat=0.25):
    m, nt, b = nodes(name)
    uv = sep(nt, attr(nt, 'tuv').outputs['Vector'])
    base = lin(base_c)
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
    col = mixc(nt, math_(nt, 'MULTIPLY', nz, 0.35), base, lin(dark_c))
    nt.links.new(col, b.inputs['Base Color'])
    set_(b, rough=rough, coat=coat, coat_r=0.3, spec=0.5, sheen=0.15, sheen_r=0.4)
    return m


def mat_eye():
    m, nt, b = nodes('eye')
    uv = attr(nt, 'tuv')
    img = image(nt, os.path.join(TEX, 'iris.png'), uv.outputs['Vector'])
    nt.links.new(img.outputs['Color'], b.inputs['Base Color'])
    set_(b, rough=0.25, coat=1.0, coat_r=0.02, spec=0.6, sss=0.1, sss_r=(1, 0.8, 0.7), sss_s=0.005)
    return m


def mat_knit(name, base, stripe=None, period=None, y0=0.0, rib=0.013):
    """knitting: vertical ribs (the uv's across coordinate in metres), stitches as small Vs along them, stripes by
    the rest height (pat.y), fuzz (sheen)"""
    m, nt, b = nodes(name)
    uv = sep(nt, attr(nt, 'tuv').outputs['Vector'])
    pat = sep(nt, attr(nt, 'pat').outputs['Vector'])
    u = math_(nt, 'DIVIDE', uv.outputs['X'], rib)
    v = math_(nt, 'DIVIDE', uv.outputs['Y'], rib * 0.45)
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
        # cream where the coordinate (metres down from the first cream band) is in the first half of each period
        k = math_(nt, 'FRACT', math_(nt, 'DIVIDE', pat.outputs['Y'], 2 * period))
        f = math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', k, 0.5), math_(nt, 'GREATER_THAN', pat.outputs['Y'], 0.0))
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


def mat_cloth(name, base, weave=900.0, rough=0.85, sheen=0.4, dark='#000000', amount=0.3, strength=0.3):
    """woven cloth: a fine weave (two crossed waves in object space) and a soft unevenness of the dye"""
    m, nt, b = nodes(name)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    xyz = sep(nt, tc.outputs['Object'])
    wv = math_(nt, 'MULTIPLY', math_(nt, 'SINE', math_(nt, 'MULTIPLY', math_(nt, 'ADD', xyz.outputs['X'], xyz.outputs['Y']), weave)),
               math_(nt, 'SINE', math_(nt, 'MULTIPLY', xyz.outputs['Z'], weave)))
    nz = noise(nt, tc.outputs['Object'], 500.0, 6, 0.7)
    nz2 = noise(nt, tc.outputs['Object'], 25.0, 2, 0.5)
    bump(nt, b, math_(nt, 'ADD', math_(nt, 'MULTIPLY', wv, 0.5), nz), strength, 0.0012)
    col = mixc(nt, math_(nt, 'MULTIPLY', nz2, amount), base, lin(dark))
    nt.links.new(col, b.inputs['Base Color'])
    set_(b, rough=rough, sheen=sheen, sheen_r=0.5, spec=0.25)
    return m


def mat_metal(name, base, rough=0.28, beads=0.0):
    m, nt, b = nodes(name)
    nt.links.new(nt.nodes.new('ShaderNodeRGB').outputs[0], b.inputs['Base Color'])
    b.inputs['Base Color'].links[0].from_node.outputs[0].default_value = base
    set_(b, rough=rough, metal=1.0)
    if beads:                                        # links of a chain: beads along the tube (tuv.y 0…1 along it)
        uv = sep(nt, attr(nt, 'tuv').outputs['Vector'])
        bump(nt, b, math_(nt, 'ABSOLUTE', math_(nt, 'SINE', math_(nt, 'MULTIPLY', uv.outputs['Y'], beads * math.pi))), 1.0, 0.0012)
    return m


def mat_lens():
    """a thin spectacle lens: almost clear, a faint cool tint and the lamps' glare"""
    m = bpy.data.materials.new('lens'); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); tr.inputs[0].default_value = (0.93, 0.96, 1.0, 1)
    gl = nt.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.03
    fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs[0].default_value = 1.5
    k = math_(nt, 'MINIMUM', math_(nt, 'ADD', math_(nt, 'MULTIPLY', fr.outputs[0], 0.8), 0.03), 0.22)
    mx = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(k, mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(gl.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
    return m


def mat_curl(name, base, dark):
    """a curl of clay hair: a ball with a spiral cut into it (tuv: the angle round the curl, 0 at its top … 1)"""
    m, nt, b = nodes(name)
    uv = sep(nt, attr(nt, 'tuv').outputs['Vector'])
    sp = math_(nt, 'SINE', math_(nt, 'ADD', uv.outputs['X'], math_(nt, 'MULTIPLY', uv.outputs['Y'], 15.0)))
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = noise(nt, tc.outputs['Object'], 900.0, 3, 0.6)
    bump(nt, b, math_(nt, 'ADD', sp, math_(nt, 'MULTIPLY', nz, 0.35)), 0.55, 0.0016)
    col = mixc(nt, math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', math_(nt, 'ADD', sp, 1.0), 0.5)), 0.6), base, dark)
    nt.links.new(col, b.inputs['Base Color'])
    set_(b, rough=0.5, coat=0.2, coat_r=0.35, spec=0.5)
    return m


def mat_towel():
    m, nt, b = nodes('towel')
    pat = sep(nt, attr(nt, 'pat').outputs['Vector'])
    y = pat.outputs['Y']
    band = lambda a_, b_: math_(nt, 'MULTIPLY', math_(nt, 'GREATER_THAN', y, a_), math_(nt, 'LESS_THAN', y, b_))
    f = math_(nt, 'ADD', band(1.3, 1.335), band(1.365, 1.385))
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = noise(nt, tc.outputs['Object'], 700.0, 5, 0.7)
    bump(nt, b, nz, 0.5, 0.0015)
    nt.links.new(mixc(nt, f, lin('#f7f2e8'), lin('#c4582c')), b.inputs['Base Color'])
    set_(b, rough=0.95, sheen=0.7, sheen_r=0.6, spec=0.2)
    return m


SKIN_WARM, SKIN_TINT, SKIN_K = '#d8805a', '#d87a60', 0.3
MATS = {
    'skin': mat_skin, 'eye': mat_eye,
    'curl': lambda: mat_curl('curl', lin('#2e2320'), lin('#070405')),
    'hairmass': lambda: mat_plain('hairmass', lin('#0c0808'), rough=0.7),
    'brow': lambda: mat_hair('brow', '#1e1614', '#0a0606', rough=0.55, coat=0.1),
    'jacket': lambda: mat_cloth('jacket', lin('#ece2d0'), weave=1500.0, rough=0.8, sheen=0.3, dark='#8a7c6a', amount=0.25, strength=0.25),
    'apron': lambda: mat_cloth('apron', lin('#c4582c'), weave=1100.0, dark='#5a1c0c', amount=0.4, strength=0.35),
    'aprontie': lambda: mat_cloth('aprontie', lin('#a84a24'), weave=1100.0, dark='#4a180a', amount=0.4),
    'towel': mat_towel,
    'trousers': lambda: mat_cloth('trousers', lin('#56504e'), weave=1200.0, dark='#1c1818', amount=0.4),
    'shoe': lambda: mat_plain('shoe', lin('#3a2a22'), rough=0.4, coat=0.35, bump_scale=300),
    'sole': lambda: mat_plain('sole', lin('#1c1410'), rough=0.7, bump_scale=200),
    'lip': lambda: mat_plain('lip', lin('#b25a50'), rough=0.4, coat=0.2, sss=0.3),
    'mouth': lambda: mat_plain('mouth', lin('#3a1418'), rough=0.6),
    'tongue': lambda: mat_plain('tongue', lin('#a8444a'), rough=0.4, coat=0.2, sss=0.3),
    'teeth': lambda: mat_plain('teeth', lin('#f1e8dc'), rough=0.3, coat=0.3),
    'lash': lambda: mat_plain('lash', lin('#1c1210'), rough=0.5),
    'clay': lambda: mat_plain('clay', lin('#c9c2b6'), rough=0.6),
}
MCACHE = {}


def material(name):
    if job.get('clay') and name not in ('eye', 'lens'):
        name = 'clay'
    if name not in MCACHE: MCACHE[name] = MATS[name]()
    return MCACHE[name]


# ------------------------------------------------------------------ the puppet
OBJ = {}
TRI = TA['triangles'].astype(np.int64)
SKIP = set(job.get('hide', []))
for o in meta['pieces']:
    n, s0, cnt = o['name'], o['start'], o['count']
    if n in SKIP: continue
    m = (TRI[:, 0] >= s0) & (TRI[:, 0] < s0 + cnt)
    T = TRI[m] - s0
    V = B(BA['positions'][s0:s0 + cnt])
    me = bpy.data.meshes.new(n)
    me.from_pydata(V.tolist(), [], T.tolist())
    for key, arr in (('tuv', RA['uv']), ('pat', RA['pat'])):
        a = arr[s0:s0 + cnt]
        a3 = np.c_[a, np.zeros((len(a), 3 - a.shape[1]))] if a.shape[1] < 3 else a
        at = me.attributes.new(key, 'FLOAT_VECTOR', 'POINT'); at.data.foreach_set('vector', a3.astype(float).ravel())
    at = me.attributes.new('tint', 'FLOAT', 'POINT'); at.data.foreach_set('value', RA['tint'][s0:s0 + cnt].astype(float))
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.update()
    ob = bpy.data.objects.new(n, me); sc.collection.objects.link(ob)
    ob.data.materials.append(material(o['mat']))
    if o.get('subdiv') and not job.get('nosubdiv'):
        sd = ob.modifiers.new('s', 'SUBSURF'); sd.levels = sd.render_levels = o['subdiv']
    if n == 'lenses': ob.visible_shadow = False
    OBJ[n] = (ob, s0, cnt)

# ------------------------------------------------------------------ the set
st = dict(dict(floor='#30241c', back='#2a1c16', glow='#e8a458', seed=14), **job.get('stage', {}))


def plane(name, size, loc, rot, mat):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
    ob = bpy.context.active_object; ob.name = name; ob.data.materials.append(mat); return ob


fm, fnt, fb = nodes('floor')
tc = fnt.nodes.new('ShaderNodeTexCoord')
fcol = mixc(fnt, math_(fnt, 'MULTIPLY', noise(fnt, tc.outputs['Object'], 6.0, 3, 0.5), 0.6), lin(st['floor']), lin('#151111'))
fnt.links.new(fcol, fb.inputs['Base Color'])
bump(fnt, fb, noise(fnt, tc.outputs['Object'], 80.0, 4, 0.6), 0.1, 0.002)
set_(fb, rough=0.75, spec=0.3)
plane('floor', 40, (0, 0, 0), (0, 0, 0), fm)
bm, bnt, bb = nodes('backdrop')
bnt.links.new(bnt.nodes.new('ShaderNodeRGB').outputs[0], bb.inputs['Base Color'])
bb.inputs['Base Color'].links[0].from_node.outputs[0].default_value = lin(st['back'])
set_(bb, rough=0.9)
LAMP_MATS = []
for i, c in enumerate(['#ffcf8a', '#ffb070', '#ffe0b0', '#9ab8ff', '#ff9a70']):
    em = bpy.data.materials.new(f'lamp{i}'); em.use_nodes = True
    e = em.node_tree.nodes; o_ = e['Material Output']
    for n in list(e):
        if n != o_: e.remove(n)
    E = e.new('ShaderNodeEmission'); E.inputs[0].default_value = lin(c); E.inputs[1].default_value = 6.0
    em.node_tree.links.new(E.outputs[0], o_.inputs[0])
    LAMP_MATS.append(em)
SET = []


def set_behind(at, fwd, d, W, H, pxm):
    """the set behind him for this view: a backdrop across the view, and small lamps scattered between, far enough
    behind to go out of focus (the bokeh of the drawing's set)"""
    for ob in SET:
        try: bpy.data.objects.remove(ob)
        except ReferenceError: pass
    SET.clear()
    at, fwd = np.asarray(at), np.asarray(fwd)           # Blender axes; fwd points toward the camera
    right = np.cross([0, 0, 1.0], fwd); right /= np.linalg.norm(right)
    back = 3.0 if d > 6 else 4.0
    bpy.ops.mesh.primitive_plane_add(size=1)
    bd = bpy.context.active_object; bd.data.materials.append(bm); SET.append(bd)
    span = (d + back + 1.0) / d * max(W, H) / pxm * 1.4
    bd.scale = (span, span, 1)
    bd.location = Vector(at - fwd * (back + 1.0))
    bd.rotation_euler = Vector(fwd).to_track_quat('Z', 'Y').to_euler()
    rng = np.random.default_rng(st['seed'])
    wv = (d + back) / d * W / pxm; hv = (d + back) / d * H / pxm
    for i in range(int(st.get('lamps', 18))):
        x, y = rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.42)
        if abs(x) < 0.2 and y < 0.3: x += 0.3 * np.sign(x or 1)
        p = at - fwd * back + right * x * wv + np.array([0, 0, 1.0]) * y * hv
        p[2] = max(p[2], 0.15 + rng.uniform(0, 0.4) * hv)        # lamps stand above the set's floor
        rr = rng.uniform(0.003, 0.008) * (d + back) / 4 if d > 6 else rng.uniform(0.01, 0.025)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rr, location=tuple(p), segments=10, ring_count=5)
        s_ = bpy.context.active_object
        s_.data.materials.append(LAMP_MATS[rng.integers(len(LAMP_MATS))])
        s_.visible_shadow = False; s_.visible_diffuse = False; s_.visible_glossy = False
        SET.append(s_)
    # the warm pool of light on the backdrop, upper left of the picture
    l = bpy.data.lights.new('pool', 'SPOT'); l.energy = 140 * job.get('light', 1.0) * (d + back) ** 2 / 16
    l.color = lin(st['glow'])[:3]; l.spot_size = math.radians(28); l.spot_blend = 1.0
    ob = bpy.data.objects.new('pool', l); sc.collection.objects.link(ob); SET.append(ob)
    tgt = at - fwd * (back + 1.0) - right * 0.35 * wv + np.array([0, 0, 0.25 * hv])
    ob.location = Vector(tgt + fwd * 2.0 + np.array([0, 0, 0.5]))
    ob.rotation_euler = (Vector(tgt) - ob.location).to_track_quat('-Z', 'Y').to_euler()


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
    area('key', c + R @ Vector((-1.9, -1.5, 1.9)), c, 0.7, 210 * k, '#ffe4c4')
    area('rim', c + R @ Vector((1.6, 1.5, 1.2)), c, 0.5, 180 * k, '#a8c4ff')
    area('fill', c + R @ Vector((1.8, -1.6, 0.2)), c, 1.6, 30 * k, '#d8c8c0')


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
        set_behind(B(at), B(fwd), d, W, H, pxm)
    else:
        pos, tgt = np.array(c['pos']), np.array(c['target'])
        cd.type = 'PERSP'; cd.lens = c.get('lens', 50); cd.sensor_width = 36
        cam.location = Vector(B(pos)); look = Vector(B(tgt)) - cam.location
        cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
        cd.dof.use_dof = True
        cd.dof.focus_distance = c.get('focus', float(np.linalg.norm(tgt - pos)))
        cd.dof.aperture_fstop = c.get('fstop', 2.8)
        cd.clip_start = 0.05
        dv = pos - tgt; dist = float(np.linalg.norm(dv))
        lights(B(c.get('light_at', tgt)), c.get('light_yaw', math.atan2(dv[0], dv[2])))
        f_ = np.array([dv[0], 0, dv[2]]); f_ /= np.linalg.norm(f_)
        pxm = W / (36e-3 / (cd.lens * 1e-3) * dist)
        set_behind(B(tgt), B(f_), dist, W, H, pxm)


os.makedirs(job['out'], exist_ok=True)
frames = None
if job.get('frames'):
    frames = np.fromfile(job['frames'], np.float32).reshape(-1, NTOT, 3)


def apply_frame(i):
    for ob, s0, cnt in OBJ.values():
        ob.data.vertices.foreach_set('co', B(frames[i, s0:s0 + cnt]).astype(np.float32).ravel())
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
