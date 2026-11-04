"""Render the 3D Савелий Петрович in the clear-line manner: flat colour (emission, no light, no shade) and one even
contour line (Freestyle: silhouettes, borders, material edges) — the same split as the drawing's own renderer.
Marks (lids, pupils, brows, wrinkles, the mouth, the glasses) are drawn as thin ink tubes and filled shapes lying on
the surface; their width follows the picture's line width, as in the drawing.

Cameras are the drawing's own views: orthographic, View(yaw, pitch, s px per unit, cx, cy) of
styles/s10-ligne-claire/tools/r3.py, so a render lies exactly over the drawing.

usage: blender -b -P render.py -- JOB.json
JOB: {scene: path.npz, out: dir, views: [{name, yaw, pitch, s, cx, cy, W, H, lw, bg}], frames?: path.npz,
      frame_range?: [a, b], marks_expr?: name}
scene.npz: obj_<name>_v (N×3, drawing units), obj_<name>_f (F×k, -1 padded), and scene.json beside it:
      {objects: [{name, colour, line, smooth, solidify}], marks: {expr: [...]}, k: metres per unit, floor: y}
"""
import bpy, bmesh, sys, json, math, os
import numpy as np
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index('--') + 1:]
job = json.load(open(args[0]))
SC = np.load(job['scene'])
meta = json.load(open(job['scene'].replace('.npz', '.json')))
K, FLOOR = meta['k'], meta['floor']
INK = meta.get('ink', '#1b1714')


def hexrgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]   # sRGB → linear


def to_b(P):
    """drawing units (x right, y down, z toward the viewer) → Blender (metres, z up, the figure facing -y)."""
    P = np.asarray(P, float)
    return np.stack([P[..., 0] * K, -P[..., 2] * K, (FLOOR - P[..., 1]) * K], -1)


# ------------------------------------------------------------------ the scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = job.get('samples', 16)
sc.cycles.use_denoising = False
sc.cycles.max_bounces = 0
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'
sc.render.film_transparent = False
sc.render.use_freestyle = True
sc.render.line_thickness_mode = 'ABSOLUTE'
world = bpy.data.worlds.new('w')
sc.world = world
world.use_nodes = True

MATS = {}


def flat(colour):
    if colour in MATS:
        return MATS[colour]
    m = bpy.data.materials.new(colour)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = hexrgb(colour) + [1]
    em.inputs['Strength'].default_value = 1.0
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(em.outputs[0], out.inputs[0])
    MATS[colour] = m
    return m


line_coll = bpy.data.collections.new('lined')
sc.collection.children.link(line_coll)
mark_coll = bpy.data.collections.new('marks')
sc.collection.children.link(mark_coll)
OBJ = {}


def mesh_obj(name, V, F, colour, lined=True, smooth=True, solidify=0.0, coll=None):
    me = bpy.data.meshes.new(name)
    faces = [[int(x) for x in f if x >= 0] for f in F]
    me.from_pydata([tuple(p) for p in to_b(V)], [], faces)
    me.update()
    if smooth:
        me.shade_smooth()
    o = bpy.data.objects.new(name, me)
    (coll or (line_coll if lined else mark_coll)).objects.link(o)
    o.data.materials.append(flat(colour))
    if solidify:
        s = o.modifiers.new('solid', 'SOLIDIFY')
        s.thickness = solidify * K
        s.offset = -1
    return o


for ob in meta['objects']:
    if ob.get('baked') and (not job.get('frames') or job.get('still_marks')):
        continue                 # marks baked for moving pictures; a still draws them at its own line width
    V, F = SC['obj_' + ob['name'] + '_v'], SC['obj_' + ob['name'] + '_f']
    o = mesh_obj(ob['name'], V, F, job.get('debug_colours', {}).get(ob['name'], ob['colour']), ob.get('line', True), ob.get('smooth', True), ob.get('solidify', 0))
    if ob.get('subsurf'):
        m = o.modifiers.new('sub', 'SUBSURF')
        m.levels = m.render_levels = ob['subsurf']
    if ob.get('colours'):         # per-face colours: a material per colour, face index → colour index
        o.data.materials.clear()
        for c in ob['colours']:
            o.data.materials.append(flat(c))
        o.data.polygons.foreach_set('material_index', SC['obj_' + ob['name'] + '_fc'].astype(np.int32))
    OBJ[ob['name']] = o


def tube_mesh(name, pts, r, colour, closed=False, nseg=8):
    """An ink line: a tube of radius r (metres) along pts (Blender coordinates)."""
    P = np.asarray(pts, float)
    if closed:
        P = np.vstack([P, P[:1]])
    n = len(P)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    ref = np.array([0, 0, 1.0])
    S = np.cross(T, ref)
    bad = np.linalg.norm(S, axis=1) < 1e-4
    S[bad] = np.cross(T[bad], [1, 0, 0])
    S /= np.linalg.norm(S, axis=1, keepdims=True)
    U = np.cross(S, T)
    a = np.linspace(0, 2 * np.pi, nseg, endpoint=False)
    Q = P[:, None] + r * (S[:, None] * np.cos(a)[None, :, None] + U[:, None] * np.sin(a)[None, :, None])
    verts = Q.reshape(-1, 3)
    faces = []
    for i in range(n - 1):
        for j in range(nseg):
            faces.append((i * nseg + j, i * nseg + (j + 1) % nseg, (i + 1) * nseg + (j + 1) % nseg, (i + 1) * nseg + j))
    # round caps: a small fan
    if not closed:
        for end, sign in ((0, -1), (n - 1, 1)):
            c = len(verts)
            verts = np.vstack([verts, P[end] + sign * T[end] * r * 0.8])
            for j in range(nseg):
                f = (end * nseg + j, end * nseg + (j + 1) % nseg, c)
                faces.append(f if sign > 0 else f[::-1])
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    o = bpy.data.objects.new(name, me)
    mark_coll.objects.link(o)
    o.data.materials.append(flat(colour))
    return o


def shape_mesh(name, pts, colour, tris=None):
    me = bpy.data.meshes.new(name)
    P = [tuple(p) for p in pts]
    me.from_pydata(P, [], tris if tris else [list(range(len(P)))])
    o = bpy.data.objects.new(name, me)
    mark_coll.objects.link(o)
    o.data.materials.append(flat(colour))
    return o


MARK_OBJS = []
HEAD_XF = None


def kabsch(A, B):
    """The rigid turn and shift taking points A to B (least squares)."""
    ca, cb = A.mean(0), B.mean(0)
    U, _, Vt = np.linalg.svd((A - ca).T @ (B - cb))
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    return R, cb - R @ ca


def build_marks(expr, lw_units, yaw=0.0, extra_skip=()):
    """lw_units: the contour's width in drawing units for this picture; a mark of width w is w times it.
    The nose hook is drawn only in near-front views (|yaw| < 25), as in the drawing."""
    for o in MARK_OBJS:
        bpy.data.objects.remove(o)
    MARK_OBJS.clear()
    skip = set(job.get('skip', meta.get('skip', []))) | set(extra_skip)
    for i, mk in enumerate(meta['marks'].get(expr, [])):
        if mk.get('group') in skip or (mk.get('group') == 'nose' and abs(yaw) >= 25):
            continue
        if 'pupil' in skip and mk.get('group') == 'eye' and mk['kind'] == 'shape' and mk.get('fill') == INK:
            continue          # the 3D eye has its own pupil
        P = np.array(mk['pts'], float)
        if HEAD_XF is not None:                  # the head turned in this pose: its marks turn with it
            P = P @ HEAD_XF[0].T + HEAD_XF[1]
        P = to_b(P)
        r = max(mk['w'] or 0, 0) * lw_units * K / 2
        stroke = mk.get('stroke') or INK
        if mk['kind'] == 'shape':
            if mk.get('fill') and mk['fill'] != 'none':
                MARK_OBJS.append(shape_mesh(f'mk{i}', P, mk['fill'], mk.get('tris')))
            if r > 0:
                MARK_OBJS.append(tube_mesh(f'mkl{i}', P[:mk.get('outline', len(P))], r, stroke, closed=True))
        else:
            MARK_OBJS.append(tube_mesh(f'mk{i}', P, r, stroke))


# ------------------------------------------------------------------ freestyle: one even line
vl = sc.view_layers[0]
fs = vl.freestyle_settings
fs.crease_angle = math.radians(job.get('crease', 100))
for ls in list(fs.linesets):
    fs.linesets.remove(ls)
ls = fs.linesets.new('ink')
ls.select_by_visibility = True
ls.visibility = 'VISIBLE'
ls.select_by_edge_types = True
ls.select_by_collection = True
ls.collection = line_coll
ls.collection_negation = 'INCLUSIVE'
ls.select_silhouette = True
ls.select_border = True
ls.select_crease = bool(job.get('crease_lines', False))
ls.select_material_boundary = True
ls.select_external_contour = True
lst = ls.linestyle
lst.color = hexrgb(INK)
lst.chaining = 'PLAIN'
lst.use_chain_count = False
lst.caps = 'ROUND'

cam_data = bpy.data.cameras.new('cam')
cam_data.type = 'ORTHO'
cam = bpy.data.objects.new('cam', cam_data)
sc.collection.objects.link(cam)
sc.camera = cam


def view_matrix(yaw, pitch, roll=0.0):
    """Rows: the drawing's screen right, screen down, toward the viewer — in drawing model coordinates."""
    y, p, r = map(math.radians, (yaw, pitch, roll))
    def rot(v):
        X, Y, Z = v
        Y1 = Y * math.cos(p) - Z * math.sin(p); Z1 = Y * math.sin(p) + Z * math.cos(p)
        X2 = X * math.cos(y) + Z1 * math.sin(y); Z2 = -X * math.sin(y) + Z1 * math.cos(y)
        X3 = X2 * math.cos(r) - Y1 * math.sin(r); Y3 = X2 * math.sin(r) + Y1 * math.cos(r)
        return [X3, Y3, Z2]
    return np.array([rot(e) for e in np.eye(3)]).T     # columns of images of the axes → rows are screen axes


def set_view(v):
    R = view_matrix(v.get('yaw', 0), v.get('pitch', 0), v.get('roll', 0))
    W, Hh, s = v['W'], v['H'], v['s']
    sc.render.resolution_x, sc.render.resolution_y = W, Hh
    sc.render.resolution_percentage = 100
    c = R.T @ np.array([(W / 2 - v['cx']) / s, (Hh / 2 - v['cy']) / s, 0.0])
    toward = R[2]
    pos = c + toward * 3000
    def dirb(d):
        return np.array([d[0], -d[2], -d[1]])
    right, down, tw = dirb(R[0]), dirb(R[1]), dirb(R[2])
    M = Matrix(((right[0], -down[0], tw[0]), (right[1], -down[1], tw[1]), (right[2], -down[2], tw[2]))).to_4x4()
    M.translation = Vector(to_b(pos))
    cam.matrix_world = M
    cam_data.ortho_scale = max(W, Hh) / s * K
    cam_data.clip_start, cam_data.clip_end = 0.01, 20
    world.node_tree.nodes['Background'].inputs['Color'].default_value = hexrgb(v.get('bg', '#ead9b4')) + [1]
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    lst.thickness = v.get('lw', 2.2)


os.makedirs(job['out'], exist_ok=True)
if not job.get('frames'):
    for v in job['views']:
        set_view(v)
        build_marks(v.get('expr', job.get('marks_expr', 'calm')), v.get('lw', 2.2) / v['s'], v.get('yaw', 0))
        sc.render.filepath = os.path.join(job['out'], v['name'] + '.png')
        bpy.ops.render.render(write_still=True)
else:
    # moving: every piece's vertices each frame from the engine (move.mjs), the face's marks baked in the mesh
    fj = json.load(open(job['frames'].replace('.bin', '.json')))
    offs = json.load(open(job['offsets']))
    N, nf = fj['N'], fj['frames']
    data = np.memmap(job['frames'], np.float32, 'r', shape=(nf, N, 3))
    a, b = job.get('frame_range', [0, nf])
    for vi, v in enumerate(job['views']):
        for fi in ([vi] if job.get('pair') else range(a, min(b, nf))):
            P = np.array(data[fi], float)
            D = np.stack([P[:, 0] / K, FLOOR - P[:, 1] / K, P[:, 2] / K], 1)     # back to the drawing's units
            for name, o in OBJ.items():
                if name not in offs or o.name not in bpy.data.objects:
                    continue
                i0, i1 = offs[name]
                o.data.vertices.foreach_set('co', to_b(D[i0:i1]).astype(np.float32).ravel())
                o.data.update()
            vv = dict(v)
            if v.get('follow'):
                hx, hy, hz = fj['hips'][fi]
                R = view_matrix(v.get('yaw', 0), v.get('pitch', 0))
                hp = R @ np.array([hx / K, 0.0, hz / K])
                vv['cx'] = v['cx'] - hp[0] * v['s']
                vv['cy'] = v['cy'] - hp[1] * v['s']        # with a pitch, going away or near moves him on screen
            set_view(vv)
            if job.get('still_marks'):       # the drawing's marks at this picture's line width, on the head as posed
                rest = SC['obj_head_v']
                i0, i1 = offs['head']
                sel = rest[:, 1] < 90
                HEAD_XF = kabsch(rest[sel], D[i0:i1][sel])
                build_marks(v.get('expr', job.get('marks_expr', 'calm')), v.get('lw', 2.2) / v['s'], v.get('yaw', 0),
                            v.get('skip', ()))
            sc.render.filepath = os.path.join(job['out'], f"{v['name']}_{fi:04d}.png")
            bpy.ops.render.render(write_still=True)
