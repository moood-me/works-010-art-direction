"""Савелий Петрович (Klaus) in 3D: builds the character pack the viewer (web/klaus.js) and the engine take.
  python3 build.py [outdir]
Bases: Anny's old man (engine/data/bodies/moood-oldman: mesh, SOMA skeleton, weights) — made small, round-bellied and
hunched under the big head; Blender's Human Base Meshes stylised head (CC0) fitted to the drawing's numbers
(head.py); the drawing's forms as solids — nose, moustache, brows, tufts (blobs.py); glasses, loupe, band; the apron
hung in front of the body; the face's painted layers from the drawing's SVG parts (features.py).
Sizes: the drawn figure is 712 units from the floor to the dome → 1.60 m."""
import os, sys, json
import numpy as np
import pack, mesh as M, head as Hd, blobs as Bl, features as FT
from body import Body, sm, top4, grid_tris

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(OUT, exist_ok=True)
K = Hd.K


def rgb(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)
def mix(a, b, t): return a + (b - a) * t


KEY, SHADE = rgb('#ffc47a'), rgb('#3a2a5a')
SKIN = rgb('#e2a68a')
# material: base, how much key light in the lit colour, the shadow colour, the rim colour, gloss (a sheen where it
# turns to the light)
def mat(base, k=0.3, s=0.55, shade=SHADE, rim='#ffd8b0', gloss=0.0):
    b = rgb(base) if isinstance(base, str) else base
    return (mix(b, KEY, k), mix(b, shade, s), rgb(rim), gloss)


MAT = {
    'skin':   mat(SKIN, 0.3, 0.58, rgb('#4a1838'), '#ffb48a', 0.5),
    'nose':   mat(mix(SKIN, rgb('#d0605a'), 0.45), 0.3, 0.5, rgb('#4a1838'), '#ffb48a', 0.8),
    'white':  mat('#e8e2da', 0.2, 0.45, SHADE, '#fff0d8', 0.0),
    'shirt':  mat('#e6dccb', 0.3, 0.5, rgb('#2a1e40'), '#fff0d8'),
    'collar': mat('#e6dccb', 0.3, 0.5, rgb('#2a1e40'), '#fff0d8'),
    'vest':   mat('#3e5a48', 0.3, 0.55, rgb('#2a1e40'), '#c8b890'),
    'apron':  mat('#7a4e30', 0.3, 0.55, rgb('#2a1e40'), '#e0a070'),
    'trous':  mat('#3a3442', 0.3, 0.5, rgb('#2a1e40'), '#a08a90'),
    'shoe':   mat('#3a2620', 0.3, 0.5, rgb('#1e1020'), '#b08060'),
    'frame':  mat('#6a5030', 0.2, 0.5, rgb('#2a1e40'), '#e0b070'),
    'loupe':  mat('#2e2a2a', 0.2, 0.5, rgb('#1a1020'), '#a08a80', 0.6),
    'brass':  mat('#c89a48', 0.3, 0.5, rgb('#3a2010'), '#ffe0a0', 0.9),
    'glass':  mat('#7aa8b8', 0.2, 0.3, rgb('#2a3a5a'), '#ffffff', 1.0),
    'glint':  mat('#fff8ec', 0.0, 0.15, rgb('#8a80a0'), '#ffffff'),
    'band':   mat('#3a2a24', 0.2, 0.5, rgb('#1a1020'), '#a08070'),
}
MATS = list(MAT)

# ---------------------------------------------------------------- the body
B = Body('moood-oldman')
I = B.I; NJ = B.NJ
S = 0.80


def affine(n, d):
    if n == 'Hips': return np.diag([1.22, 1, 1.34])
    if n in ('Spine1', 'Spine2'): return np.diag([1.26, 1, 1.3])
    if n == 'Chest': return np.diag([1.16, 1, 1.1])
    if n.endswith('Shoulder'): return np.diag([1.0, 1.0, 1.1])
    r = {'Arm': 1.08, 'ForeArm': 1.05, 'Leg': 1.16, 'Shin': 1.2}.get(n.replace('Left', '').replace('Right', ''))
    if r and d is not None: return r * np.eye(3) + (1 - r) * np.outer(d, d)
    if 'Hand' in n: return np.eye(3) * 1.12
    if 'Foot' in n or 'Toe' in n: return np.diag([1.25, 1.1, 1.12])
    return np.eye(3)


LEN = {'Hips': 1.3, 'Spine1': 1.3, 'Spine2': 1.3, 'Chest': 1.25, 'LeftLeg': 0.93, 'RightLeg': 0.93, 'LeftShin': 0.93, 'RightShin': 0.93,
       'LeftArm': 1.08, 'RightArm': 1.08, 'LeftForeArm': 1.08, 'RightForeArm': 1.08}
B.reshape(S, affine, moves=[(s + 'Leg', np.array([-sg * 0.012, 0, 0])) for s, sg in (('Left', 1), ('Right', -1))], length=LEN)
# the habit: a round back, the shoulders forward
B.prepose({'Spine2': ([1, 0, 0], 0.16), 'Chest': ([1, 0, 0], 0.24), 'Neck1': ([1, 0, 0], -0.2),
           'LeftShoulder': ([0, 1, 0], -0.12), 'RightShoulder': ([0, 1, 0], 0.12)})
neck_y = B.J[I['Neck1'], 1]
gone = (B.part('head') > 0.5) | ((B.part('neck') > 0.3) & (B.P[:, 1] > neck_y + 0.01))
B.cut(gone)
# the neck's hole closed with a cap
for loop in M.boundary_loops(B.T):
    if len(loop) < 8: continue
    c = len(B.P)
    B.P = np.r_[B.P, [B.P[loop].mean(0) - [0, 0.01, 0]]]; B.P0 = np.r_[B.P0, [B.P0[loop].mean(0)]]
    B.SJ = np.r_[B.SJ, B.SJ[loop[:1]]]; B.SW = np.r_[B.SW, B.SW[loop[:1]]]; B.parts = np.r_[B.parts, B.parts[loop[:1]]]
    cap = np.array([[loop[k], loop[(k + 1) % len(loop)], c] for k in range(len(loop))])
    if np.cross(B.P[cap[:, 1]] - B.P[cap[:, 0]], B.P[cap[:, 2]] - B.P[cap[:, 0]])[:, 1].sum() < 0: cap = cap[:, ::-1]
    B.T = np.r_[B.T, cap]
P = B.P; by = P[:, 1]
arms = B.part('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand', 'Lclavicle', 'Rclavicle') > 0.5
notarm = B.part('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand') < 0.3
waist = B.J[I['Hips'], 1] - 0.03
# the round belly: the trunk's front pushed forward, most at the navel's height
zc = B.J[I['Spine1'], 2]
trunk = B.part('pelvis', 'spine') > 0.5
bel = np.exp(-((by - (B.J[I['Spine1'], 1] + 0.03)) / 0.13) ** 2) * sm((P[:, 2] - zc) / 0.08) * trunk
P[:, 2] += 0.045 * bel
B.P = P
# materials: the trunk and arms are one 'shirt' here; where the vest and the trousers begin is drawn by the shader
# from the rest position (a crisp edge, not one smeared between vertices)
m = np.full(len(P), MATS.index('shirt'))
m[B.part('Lhand', 'Rhand') > 0.5] = MATS.index('skin')
legs = B.part('Lthigh', 'Rthigh', 'Lshin', 'Rshin') > 0.5
foot = (B.part('Lfoot', 'Rfoot') > 0.5)
A = M.adjacency(len(P), B.T)
N = M.vertex_normals(P, B.T)
cloth = m == MATS.index('shirt')
off = np.where(cloth, 0.011, 0)
P = P + N * off[:, None]
# trouser legs: straight tubes, not calves and knees — every leg vertex at least so far from its bone
W = B.dense()
for s_, sg in (('Left', 1), ('Right', -1)):
    a0, a1 = B.J[I[s_ + 'Leg']], B.J[I[s_ + 'Foot']]
    ax = (a1 - a0) / np.linalg.norm(a1 - a0)
    wl = W[:, I[s_ + 'Leg']] + W[:, I[s_ + 'Shin']] + W[:, I[s_ + 'Foot']]
    t = (P - a0) @ ax; foot_ = a0 + np.outer(t, ax); rad = P - foot_; r = np.linalg.norm(rad, axis=1) + 1e-9
    u = np.clip(t / np.linalg.norm(a1 - a0), 0, 1)
    rmin = np.interp(u, [0, 0.25, 1], [0.0, 0.082, 0.072])
    k = sm((wl - 0.5) / 0.4) * cloth * sm((u - 0.12) / 0.2)
    P += rad / r[:, None] * (np.clip(rmin - r, 0, None) * k)[:, None]
P = M.smooth(P, A, cloth * 1.0, iters=45, lam=0.5)
# the feet go inside the shoes
for s_ in ('Left', 'Right'):
    c = (B.J[I[s_ + 'Foot']] + B.J[I[s_ + 'ToeBase']]) / 2
    w = sm((W[:, I[s_ + 'Foot']] + W[:, I[s_ + 'ToeBase']] + W[:, I[s_ + 'ToeEnd']] - 0.5) / 0.4)[:, None] * foot[:, None]
    P = P + (c - P) * 0.35 * w
B.P = P
print('body: shoulders', B.J[I['LeftArm']], 'neck', B.J[I['Neck1']], 'hips', B.J[I['Hips']], 'floor', P[:, 1].min())

# ---------------------------------------------------------------- the head and its forms
hv, hP, ear = Hd.fitted()
hT = M.triangulate(hP)
CHIN = 1.186
Z0 = B.J[I['Neck1'], 2] + 0.075
OFF = np.array([0, CHIN, Z0])
yd_h = Hd.CH - hv[:, 1] / K
Ah = M.adjacency(len(hv), hT)
hs = M.smooth(hv, Ah, np.ones(len(hv)), iters=30, lam=0.5)
pn = M.vertex_normals(hs, hT)
pw = 0.85 * (1 - sm((yd_h - 420) / 30))          # the face shades as one plain form
uv = np.c_[(hv[:, 0] / K + 250 - FT.X0) / FT.W, 1 - (yd_h - FT.Y0) / FT.H]
nh = M.vertex_normals(hv, hT)
inside = (uv[:, 0] > 0) & (uv[:, 0] < 1) & (uv[:, 1] > 0) & (uv[:, 1] < 1)
tw = sm((nh[:, 2] - 0.1) / 0.3) * (hv[:, 2] > 0.02) * inside


def chain_w(yd, zfwd, n):
    """Head above the chin; down the neck to Neck2, Neck1, the chest."""
    W = np.zeros((n, NJ)); y = yd - 14 * sm(zfwd / 0.05)
    t0, t1, t2 = sm((y - 428) / 26), sm((y - 448) / 16), sm((y - 470) / 16)
    W[:, I['Head']] = 1 - t0; W[:, I['Neck2']] = t0 * (1 - t1); W[:, I['Neck1']] = t0 * t1 * (1 - t2); W[:, I['Chest']] = t0 * t1 * t2
    return W


parts = []
def add(name, V, T, material, W=None, SJ=None, SW=None, **attr):
    if W is not None: SJ, SW = top4(W)
    parts.append(dict(name=name, V=np.asarray(V, float), T=np.asarray(T), mat=np.broadcast_to(material, (len(V),)).copy(), SJ=SJ, SW=SW, **attr))


def rigid(n, joint='Head'):
    W = np.zeros((n, NJ)); W[:, I[joint]] = 1; return W


add('body', B.P, B.T, m, SJ=B.SJ, SW=B.SW)
add('head', hv + OFF, hT, MATS.index('skin'), W=chain_w(yd_h, hv[:, 2], len(hv)), uv=uv, tw=tw, pn=pn, pw=pw,
    gloss=np.where(yd_h < 200, 1.0, 0.25))
F = Hd.forms(hv, hT)
for name, mt in (('earL', 'skin'), ('earR', 'skin'), ('nose', 'nose'), ('moustache', 'white'), ('browL', 'white'), ('browR', 'white'), ('tuftL', 'white'), ('tuftR', 'white')):
    v, t = F[name]; add(name, v + OFF, t, MATS.index(mt), W=rigid(len(v)))
Th = Hd.things(hv, hT)
for name, mt in (('glasses', 'frame'), ('glint', 'glint'), ('loupe', 'loupe'), ('brass', 'brass'), ('glass', 'glass'), ('band', 'band')):
    v, t = Th[name]; add(name, v + OFF, t, MATS.index(mt), W=rigid(len(v)))

# ---------------------------------------------------------------- the collar: a soft ring of the shirt round the neck
th = np.linspace(0, 2 * np.pi, 40, endpoint=False)
NK = B.J[I['Neck1']]
ring = np.c_[0.068 * np.sin(th), CHIN - 0.034 - 0.018 * np.cos(th), Z0 - 0.016 + 0.07 * np.cos(th)]
cv, ct = Bl.tube(ring, np.array([[0.011, 0.023]] * len(ring)), 10, closed=True)
Wc = np.zeros((len(cv), NJ)); Wc[:, I['Chest']] = 0.6; Wc[:, I['Neck1']] = 0.4
add('collar', cv, ct, MATS.index('collar'), W=Wc)

# ---------------------------------------------------------------- the leather apron: a bib from the chest to the knees
rows, cols = 44, 21
y_top, y_bot = 1.012, 0.44
ys = np.linspace(y_top, y_bot, rows)
AV = np.zeros((rows, cols, 3))
front_mask = notarm
for r, y in enumerate(ys):
    hw = np.interp(y, [y_bot, 0.75, y_top], [0.150, 0.146, 0.105])
    xs = np.linspace(-hw, hw, cols)
    zb = np.array([B.front(x, max(y, 0.60), 0.02, front_mask) for x in xs])
    zb = np.where(np.isnan(zb), np.nanmin(zb), zb)
    zm = np.nanmax(zb[cols // 2 - 2:cols // 2 + 3])
    AV[r] = np.c_[xs, np.full(cols, y), np.maximum(zb + 0.008, zm + 0.014 - 0.05 * (xs / hw) ** 2)]
# leather hangs: below the belly's most forward line it falls straight, only a little back
for c in range(cols):
    z = AV[:, c, 2]; k = int(np.argmax(z))
    for r in range(k + 1, rows): z[r] = max(z[r], z[k] - 0.08 * (ys[k] - ys[r]))
for _ in range(8):
    Q = AV.copy(); Q[1:-1, :, 2] = (AV[:-2, :, 2] + 2 * AV[1:-1, :, 2] + AV[2:, :, 2]) / 4
    Q[:, 1:-1, 2] = (Q[:, :-2, 2] + 2 * Q[:, 1:-1, 2] + Q[:, 2:, 2]) / 4; AV = Q
AVf = AV.reshape(-1, 3)
Wa = B.weights_at(np.c_[AVf[:, 0], np.maximum(AVf[:, 1], 0.66), AVf[:, 2] - 0.02], front_mask, k=8)
low = sm((0.70 - AVf[:, 1]) / 0.2)[:, None]                  # the hem follows the thighs only a little
Wh = np.zeros_like(Wa); Wh[:, I['Hips']] = 0.6
side = sm((AVf[:, 0] / 0.06 + 1) / 2)
Wh[:, I['LeftLeg']] = 0.4 * side; Wh[:, I['RightLeg']] = 0.4 * (1 - side)
Wa = Wa * (1 - low) + Wh * low
auv = np.stack(np.meshgrid(np.linspace(-1, 1, cols), np.linspace(0, 1, rows)), -1).reshape(-1, 2)
add('apron', AVf, grid_tris(rows, cols), MATS.index('apron'), W=Wa, two=1, uv=auv)
# its straps over the shoulders to the back of the neck
for sg in (1, -1):
    path = []
    for u in np.linspace(0, 1, 14):
        x = sg * np.interp(u, [0, 1], [0.092, 0.058]); y = np.interp(u, [0, 1], [y_top - 0.004, B.J[I['Neck1'], 1] - 0.012])
        z = B.front(x, y, 0.02, front_mask)
        path.append([x, y, (z if not np.isnan(z) else path[-1][2] - 0.012) + 0.012])
    path = np.array(path); path[:, 2] = np.convolve(np.r_[path[:1, 2], path[:, 2], path[-1:, 2]], [0.25, 0.5, 0.25], 'valid')
    sv, st = Bl.tube(path, np.array([[0.008, 0.003]] * len(path)), 8)
    add('strap', sv, st, MATS.index('apron'), W=B.weights_at(sv, front_mask, k=6))

# ---------------------------------------------------------------- the shoes: round-toed, a flat sole
for s_, sg in (('Left', 1), ('Right', -1)):
    an, toe = B.J[I[s_ + 'Foot']], B.J[I[s_ + 'ToeEnd']]
    d = toe - an; d[1] = 0; L = np.linalg.norm(d); d /= L
    heel = np.array([an[0], 0.05, an[2]]) - d * 0.035
    c, r = Bl.chain([heel, heel + d * 0.09 + [0, 0.004, 0], heel + d * (L + 0.035) + [0, -0.008, 0]], [0.047, 0.046, 0.043], 12)
    v, t = Bl.solid((c, r), k=0.012, cell=0.006, squash=(1.05, 0.9, 1))
    v[:, 1] = np.maximum(v[:, 1], 0.0)
    Ws = np.zeros((len(v), NJ)); f = sm(((v - an) @ d - 0.06) / 0.05)
    Ws[:, I[s_ + 'Foot']] = 1 - f; Ws[:, I[s_ + 'ToeBase']] = f
    add('shoe', v, t, MATS.index('shoe'), W=Ws)

# ---------------------------------------------------------------- joints
J = B.J.copy()
J[I['Neck2']] = [0, CHIN - 0.01, Z0 - 0.02]
J[I['Head']] = [0, CHIN + 0.03, Z0]
J[I['HeadEnd']] = [0, CHIN + 330 * K, Z0 - 0.01]
J[I['Jaw']] = [0, CHIN + 0.05, Z0 + 0.03]
for s, sg in (('Left', 1), ('Right', -1)):
    J[I[s + 'Eye']] = [sg * FT.EYE_X * K, CHIN + (Hd.CH - FT.EYE_Y) * K, Z0 + 0.1]


WAIST = float(B.J[I['Hips'], 1] + 0.0)
DECO = '''
void deco(vec3 rp, vec2 uv, float m, inout vec3 base, inout vec3 bshd) {
  if (abs(m - %(shirt)d.0) < 0.5) {
    // trousers below the waist; the vest over the trunk, open in a V at the neck where the shirt and a small tie show
    if (rp.y < %(waist).3f && abs(rp.x) < 0.26) { base = %(trous_l)s; bshd = %(trous_s)s; return; }
    bool trunk = abs(rp.x) < %(arm).3f - 0.5 * max(0.0, rp.y - %(shy).3f);
    float v = (rp.y - %(vy).3f) * 0.42;
    bool open = rp.z > %(zc).3f && abs(rp.x) < v;
    if (trunk && !open && (rp.y < %(necky).3f || rp.z < %(zc).3f)) {
      base = %(vest_l)s; bshd = %(vest_s)s;
      float e = min(abs(abs(rp.x) - v), abs(rp.y - %(waist).3f));
      if (rp.z > %(zc).3f && abs(abs(rp.x) - v) < 0.004 && v > 0.0) { base *= 0.72; bshd *= 0.8; }
    } else if (open && abs(rp.x) < 0.012 + 0.006 * sin((rp.y - %(vy).3f) * 30.0) && rp.y < %(necky).3f - 0.03) { base = vec3(0.50, 0.22, 0.20); bshd = vec3(0.27, 0.12, 0.17); }
  }
  if (abs(m - %(apron)d.0) < 0.5 && rp.z > 0.0) {
    float e = min(1.0 - abs(uv.x), min(uv.y, 1.0 - uv.y) * 3.0);
    if (e > 0.045 && e < 0.06) { base *= 0.8; bshd *= 0.85; }
    // the apron's pocket with two tools, a stitched edge
    vec2 p = vec2(rp.x + 0.035, rp.y - 0.84);
    if (abs(p.x) < 0.05 && abs(p.y) < 0.042) { base *= 0.82; bshd *= 0.85;
      if ((abs(p.x + 0.022) < 0.0035 || abs(p.x + 0.004) < 0.0035) && p.y > -0.02) { base = vec3(0.60, 0.60, 0.63); bshd = vec3(0.3, 0.28, 0.4); } }
  }
}'''

# the drawn stand: the hands behind the back
POSE = dict(Left=dict(down=0.72, fwd=-0.5, bend=0.9, axis=[0.5, 1, 0]), Right=dict(down=0.72, fwd=-0.5, bend=0.9, axis=[0.5, -1, 0]))

# ---------------------------------------------------------------- the pack
N = sum(len(p['V']) for p in parts)
def cat(key, default, dtype=np.float32):
    one = lambda p: np.asarray(p[key], float) if key in p and np.ndim(p[key]) else np.broadcast_to(np.asarray(p.get(key, default), float), (len(p['V']),) + np.shape(default))
    return np.concatenate([one(p) for p in parts]).astype(dtype)
pos = np.concatenate([p['V'] for p in parts]).astype(np.float32)
tri, base, groups = [], 0, {}
for p in parts:
    tri.append(p['T'] + base); groups.setdefault(p['name'], []).append([base, len(p['V'])]); base += len(p['V'])
tri = np.concatenate(tri).astype(np.uint32)
matv = np.concatenate([p['mat'] for p in parts])
lit = np.array([MAT[MATS[k]][0] for k in matv]); shd = np.array([MAT[MATS[k]][1] for k in matv]); rim = np.array([MAT[MATS[k]][2] for k in matv])
gl = np.array([MAT[MATS[k]][3] for k in matv]) * cat('gloss', 1.0)
floor = float(pos[:, 1].min())
v3 = lambda c: 'vec3(%.3f, %.3f, %.3f)' % tuple(c / 255)
DV = dict(shirt=MATS.index('shirt'), apron=MATS.index('apron'), waist=WAIST, arm=float(B.J[I['LeftArm'], 0] - 0.012), shy=float(B.J[I['LeftArm'], 1] - 0.03),
          vy=1.03, zc=float(B.J[I['Chest'], 2]), necky=float(B.J[I['Neck1'], 1] + 0.03),
          trous_l=v3(MAT['trous'][0]), trous_s=v3(MAT['trous'][1]), vest_l=v3(MAT['vest'][0]), vest_s=v3(MAT['vest'][1]))
# what moves on the face besides the painted layers: the brows and the moustache (head units → metres in the viewer)
movers = {g: dict(ranges=groups[g], pivot=[float(x) for x in np.mean([parts[i]['V'] for i in range(len(parts)) if parts[i]['name'] == g][0], 0) - OFF])
          for g in ('browL', 'browR', 'moustache')}
header = dict(format='engine/body', version=1, id='savely-klaus', label={'ru': 'Савелий Петрович (Клаус)'}, topology='savely-klaus',
              skeleton='soma', source='to3d/r15-s2-savely/tools/build.py', faces='faces', floor=floor, materials=MATS,
              deco=DECO % DV, K=K, headOrigin=[float(x) for x in OFF], movers=movers, expr=FT.EXPR,
              back=dict(top='#2e2230', bottom='#4a3030', glow='#f0a050'), seed=15,
              ui=dict(motions=[['', 'стоит'], ['walk', 'шаг'], ['wave', 'машет'], ['sneak', 'крадётся'], ['bow', 'поклон'], ['stomp', 'топает'], ['sit', 'садится'], ['dance', 'танец']],
                      expr=[['calm', 'ворчит'], ['kind', 'добрый'], ['surprise', 'удивлён'], ['sad', 'грустит'], ['anger', 'сердит']],
                      dist=5.0, cy=0.82, near=2.5, up=0.13, pose=POSE, look3d=dict(thr=0.08, light=[-0.48, 0.48, 0.74])))
pack.save(os.path.join(OUT, 'savely.json'), header, dict(
    positions=pos, triangles=tri, skinJoints=np.concatenate([p['SJ'] for p in parts]).astype(np.uint8),
    skinWeights=np.concatenate([p['SW'] for p in parts]).astype(np.float32),
    joints=J.astype(np.float32).ravel(), frames=B.frames.ravel(),
    col=lit.astype(np.uint8), shd=shd.astype(np.uint8), rim=rim.astype(np.uint8), gloss=(gl * 255).astype(np.uint8),
    uv=cat('uv', [0.0, 0.0]), tw=(cat('tw', 0.0) * 255).astype(np.uint8), pn=cat('pn', [0.0, 0.0, 0.0]),
    pw=(cat('pw', 0.0) * 255).astype(np.uint8), two=cat('two', 0.0, np.uint8), mat=matv.astype(np.uint8), rp=pos.copy()))
print('pack', N, 'vertices', len(tri), 'triangles; height', pos[:, 1].max() - floor)
