"""Марат (Klaus) in 3D: builds the character pack the viewer (web/klaus.js) and the engine take.
  python3 build.py [outdir]
Bases: Anny's man (engine/data/bodies/moood-man: mesh, SOMA skeleton, weights) — made a barrel: the trunk 1.6–1.9
times wider and deeper, longer, the arms and legs thick, the shoulders moved out; Blender's Human Base Meshes
stylised head (CC0) fitted to the drawing's front and profile (head.py); the drawing's masses as solids — nose, ears,
moustache, beard, the cap of curls (blobs.py); the long apron as a shell round the hips and legs, the towel over
the shoulder, rolled sleeves, the collar, clogs; the face's painted layers from the drawing's SVG parts (features.py).
Sizes: the drawn figure is 835 units from the floor to the top of the hair → 1.94 m."""
import os, sys
import numpy as np
import pack, mesh as M, head as Hd, blobs as Bl, features as FT
from body import Body, sm, top4, grid_tris

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(OUT, exist_ok=True)
K = Hd.K


def rgb(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)
def mix(a, b, t): return a + (b - a) * t


KEY, SHADE = rgb('#ffc47a'), rgb('#3a2a5a')
SKIN = rgb('#dc9c76')
def mat(base, k=0.3, s=0.55, shade=SHADE, rim='#ffd8b0', gloss=0.0):
    b = rgb(base) if isinstance(base, str) else base
    return (mix(b, KEY, k), mix(b, shade, s), rgb(rim), gloss)


MAT = {
    'skin':   mat(SKIN, 0.3, 0.58, rgb('#4a1838'), '#ffb48a', 0.3),
    'nose':   mat(mix(SKIN, rgb('#d2584a'), 0.2), 0.3, 0.5, rgb('#4a1838'), '#ffb48a', 0.8),
    'hair':   mat('#1e181e', 0.12, 0.35, rgb('#0c080e'), '#b08a88', 0.2),
    'jacket': mat('#ece2d2', 0.25, 0.5, rgb('#2a1e40'), '#f0c8a0'),
    'collar': mat('#ece2d2', 0.25, 0.5, rgb('#2a1e40'), '#f0c8a0'),
    'cuff':   mat(mix(rgb('#ece2d2'), rgb('#8a7a80'), 0.18), 0.25, 0.5, rgb('#2a1e40'), '#f0c8a0'),
    'apron':  mat('#c2603a', 0.3, 0.55, rgb('#2a1e40'), '#f0a070'),
    'towel':  mat('#d8703e', 0.3, 0.5, rgb('#2a1030'), '#ffc090'),
    'shoe':   mat('#3a2a26', 0.3, 0.5, rgb('#1e1020'), '#b08060'),
}
MATS = list(MAT)

# ---------------------------------------------------------------- the body
B = Body('moood-man')
I = B.I; NJ = B.NJ
S = 1.0


def affine(n, d):
    if n == 'Hips': return np.diag([1.9, 1, 2.0])
    if n in ('Spine1', 'Spine2'): return np.diag([2.1, 1, 2.2])
    if n == 'Chest': return np.diag([1.95, 1, 1.9])
    if n.endswith('Shoulder'): return np.diag([1.25, 1.25, 1.5])
    r = {'Arm': 1.6, 'ForeArm': 1.95, 'Leg': 1.6, 'Shin': 1.5}.get(n.replace('Left', '').replace('Right', ''))
    if r and d is not None: return r * np.eye(3) + (1 - r) * np.outer(d, d)
    if 'Hand' in n: return np.eye(3) * 1.45
    if 'Foot' in n or 'Toe' in n: return np.diag([1.3, 1.1, 1.15])
    if n.startswith('Neck'): return np.diag([1.4, 1, 1.4])
    return np.eye(3)


LEN = {'Hips': 1.15, 'Spine1': 1.15, 'Spine2': 1.15, 'Chest': 1.12, 'LeftLeg': 0.9, 'RightLeg': 0.9, 'LeftShin': 0.9, 'RightShin': 0.9,
       'LeftShoulder': 2.1, 'RightShoulder': 2.1, 'LeftArm': 0.95, 'RightArm': 0.95}
B.reshape(S, affine, moves=[(s + 'Leg', np.array([sg * 0.07, 0, 0])) for s, sg in (('Left', 1), ('Right', -1))], length=LEN)
B.prepose({'Spine1': ([1, 0, 0], -0.05), 'Chest': ([1, 0, 0], -0.04)})          # the chest out, a little back: he stands open
neck_y = B.J[I['Neck1'], 1]
gone = (B.part('head') > 0.5) | ((B.part('neck') > 0.3) & (B.P[:, 1] > neck_y + 0.02))
B.cut(gone)
for loop in M.boundary_loops(B.T):
    if len(loop) < 8: continue
    c = len(B.P)
    B.P = np.r_[B.P, [B.P[loop].mean(0) - [0, 0.01, 0]]]; B.P0 = np.r_[B.P0, [B.P0[loop].mean(0)]]
    B.SJ = np.r_[B.SJ, B.SJ[loop[:1]]]; B.SW = np.r_[B.SW, B.SW[loop[:1]]]; B.parts = np.r_[B.parts, B.parts[loop[:1]]]
    cap = np.array([[loop[k], loop[(k + 1) % len(loop)], c] for k in range(len(loop))])
    if np.cross(B.P[cap[:, 1]] - B.P[cap[:, 0]], B.P[cap[:, 2]] - B.P[cap[:, 0]])[:, 1].sum() < 0: cap = cap[:, ::-1]
    B.T = np.r_[B.T, cap]
P = B.P; by = P[:, 1]
notarm = B.part('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand') < 0.3
# the belly: forward, most at the navel
zc = B.J[I['Spine1'], 2]
trunk = B.part('pelvis', 'spine') > 0.5
bel = np.exp(-((by - (B.J[I['Spine1'], 1] + 0.06)) / 0.2) ** 2) * sm((P[:, 2] - zc) / 0.1) * trunk
P[:, 2] += 0.05 * bel
# materials: the jacket over trunk and upper arms (its buttons and folds drawn by the shader); forearms and hands bare
W = B.dense()
m = np.full(len(P), MATS.index('jacket'))
fore = (W[:, I['LeftForeArm']] + W[:, I['RightForeArm']] + sum(W[:, j] for j in range(NJ) if 'Hand' in B.names[j])) > 0.62
m[fore] = MATS.index('skin')
A = M.adjacency(len(P), B.T)
N = M.vertex_normals(P, B.T)
cloth = m == MATS.index('jacket')
P = P + N * np.where(cloth, 0.012, 0)[:, None]
for s_, sg in (('Left', 1), ('Right', -1)):          # trouser legs: straight tubes
    a0, a1 = B.J[I[s_ + 'Leg']], B.J[I[s_ + 'Foot']]
    ax = (a1 - a0) / np.linalg.norm(a1 - a0)
    wl = W[:, I[s_ + 'Leg']] + W[:, I[s_ + 'Shin']] + W[:, I[s_ + 'Foot']]
    t = (P - a0) @ ax; rad = P - (a0 + np.outer(t, ax)); r = np.linalg.norm(rad, axis=1) + 1e-9
    u = np.clip(t / np.linalg.norm(a1 - a0), 0, 1)
    rmin = np.interp(u, [0, 0.25, 1], [0.0, 0.12, 0.1])
    k = sm((wl - 0.5) / 0.4) * cloth * sm((u - 0.12) / 0.2)
    P += rad / r[:, None] * (np.clip(rmin - r, 0, None) * k)[:, None]
P = M.smooth(P, A, cloth * 1.0, iters=50, lam=0.5)
P = M.smooth(P, A, (m == MATS.index('skin')) * 1.0, iters=3, lam=0.5)
foot = B.part('Lfoot', 'Rfoot') > 0.5
for s_ in ('Left', 'Right'):
    c = (B.J[I[s_ + 'Foot']] + B.J[I[s_ + 'ToeBase']]) / 2
    w = sm((W[:, I[s_ + 'Foot']] + W[:, I[s_ + 'ToeBase']] + W[:, I[s_ + 'ToeEnd']] - 0.5) / 0.4)[:, None] * foot[:, None]
    P = P + (c - P) * 0.35 * w
B.P = P
print('body: shoulders', B.J[I['LeftArm']], 'neck', B.J[I['Neck1']], 'hips', B.J[I['Hips']], 'floor', P[:, 1].min(), 'width', P[notarm, 0].max() * 2)

# ---------------------------------------------------------------- the head and its forms
hv, hP, ear = Hd.fitted()
hT = M.triangulate(hP)
CHIN = 1.556
Z0 = B.J[I['Neck1'], 2] + 0.035
OFF = np.array([0, CHIN, Z0])
yd_h = Hd.CH - hv[:, 1] / K
Ah = M.adjacency(len(hv), hT)
hs = M.smooth(hv, Ah, np.ones(len(hv)), iters=30, lam=0.5)
pn = M.vertex_normals(hs, hT)
pw = 0.85 * (1 - sm((yd_h - 430) / 30))


def sheet_uv(v):
    return np.c_[(v[:, 0] / K + 250 - FT.X0) / FT.W, 1 - ((Hd.CH - v[:, 1] / K) - FT.Y0) / FT.H]


def sheet_w(v, T, z0=0.02):
    uv = sheet_uv(v); n = M.vertex_normals(v, T)
    inside = (uv[:, 0] > 0) & (uv[:, 0] < 1) & (uv[:, 1] > 0) & (uv[:, 1] < 1)
    return uv, sm((n[:, 2] - 0.1) / 0.3) * (v[:, 2] > z0) * inside


def chain_w(yd, zfwd, n):
    W_ = np.zeros((n, NJ)); y = yd - 14 * sm(zfwd / 0.05)
    t0, t1, t2 = sm((y - 440) / 22), sm((y - 458) / 14), sm((y - 474) / 12)
    W_[:, I['Head']] = 1 - t0; W_[:, I['Neck2']] = t0 * (1 - t1); W_[:, I['Neck1']] = t0 * t1 * (1 - t2); W_[:, I['Chest']] = t0 * t1 * t2
    return W_


parts = []
def add(name, V, T, material, W=None, SJ=None, SW=None, **attr):
    if W is not None: SJ, SW = top4(W)
    parts.append(dict(name=name, V=np.asarray(V, float), T=np.asarray(T), mat=np.broadcast_to(material, (len(V),)).copy(), SJ=SJ, SW=SW, **attr))


def rigid(n, joint='Head'):
    W_ = np.zeros((n, NJ)); W_[:, I[joint]] = 1; return W_


add('body', B.P, B.T, m, SJ=B.SJ, SW=B.SW)
uv, tw = sheet_uv(hv), None
uv, tw = sheet_w(hv, hT)
add('head', hv + OFF, hT, MATS.index('skin'), W=chain_w(yd_h, hv[:, 2], len(hv)), uv=uv, tw=tw, pn=pn, pw=pw, gloss=0.3)
F = Hd.forms(hv, hT)
for name, mt in (('earL', 'skin'), ('earR', 'skin'), ('nose', 'nose'), ('moustache', 'hair'), ('hair', 'hair')):
    v, t = F[name]; add(name, v + OFF, t, MATS.index(mt), W=rigid(len(v)))
# the beard carries the painted mouth; its normals in front are smoothed so the mouth lies on a plain form
v, t = F['beard']
buv, btw = sheet_w(v, t, 0.03)
btw = btw * (abs(v[:, 0]) < 64 * K) * (v[:, 1] < (Hd.CH - 350) * K)          # only the mouth's place
bs = M.smooth(v, M.adjacency(len(v), t), np.ones(len(v)), iters=25, lam=0.5)
add('beard', v + OFF, t, MATS.index('hair'), W=rigid(len(v)), uv=buv, tw=btw, pn=M.vertex_normals(bs, t), pw=0.6 * btw)

# ---------------------------------------------------------------- the stand collar
th = np.linspace(0, 2 * np.pi, 40, endpoint=False)
ring = np.c_[0.092 * np.sin(th), CHIN - 0.052 - 0.012 * np.cos(th), Z0 - 0.012 + 0.095 * np.cos(th)]
cv, ct = Bl.tube(ring, np.array([[0.013, 0.03]] * len(ring)), 10, closed=True)
Wc = np.zeros((len(cv), NJ)); Wc[:, I['Chest']] = 0.7; Wc[:, I['Neck1']] = 0.3
add('collar', cv, ct, MATS.index('collar'), W=Wc)

# ---------------------------------------------------------------- rolled sleeves: a thick ring at each elbow
for s_, sg in (('Left', 1), ('Right', -1)):
    e0, e1 = B.J[I[s_ + 'ForeArm']], B.J[I[s_ + 'Hand']]
    d = (e1 - e0) / np.linalg.norm(e1 - e0); c = e0 + d * 0.035
    mk = (abs((B.P - c) @ d) < 0.02) & (W[:, I[s_ + 'ForeArm']] + W[:, I[s_ + 'Arm']] > 0.9)
    rr = np.linalg.norm((B.P[mk] - c) - np.outer((B.P[mk] - c) @ d, d), axis=1).max()
    u = np.cross(d, [0, 0, 1.0]); u /= np.linalg.norm(u); w = np.cross(d, u)
    ring = np.array([c + (u * np.cos(a) + w * np.sin(a)) * (rr + 0.004) for a in th])
    v, t = Bl.tube(ring, np.array([[0.016, 0.034]] * len(ring)), 10, closed=True)
    Ws = np.zeros((len(v), NJ)); Ws[:, I[s_ + 'ForeArm']] = 0.6; Ws[:, I[s_ + 'Arm']] = 0.4
    add('cuff', v, t, MATS.index('cuff'), W=Ws)

# ---------------------------------------------------------------- the long apron: a shell round the hips and legs, waist to shins
def ring_body(y, pad):
    mk = (abs(B.P[:, 1] - y) < 0.012) & notarm
    v = B.P[mk]
    return abs(v[:, 0]).max() + pad, v[:, 2].max() + pad, v[:, 2].min() - pad


rows, cols = 30, 72
WAIST = float(B.J[I['Hips'], 1] + 0.085)
ys = np.linspace(WAIST, 0.34, rows)
SV = []
ax0, zf0, zb0 = ring_body(WAIST - 0.02, 0.01)
for i, y in enumerate(ys):
    u = i / (rows - 1)
    ax, zf, zb = ring_body(min(max(y, 0.72), WAIST - 0.01), 0.012)
    ax = max(ax, ax0 * 0.97) + 0.012 * u; zf = max(zf, zf0 - 0.10 * u) ; zb = min(zb, zb0 + 0.03 * u) - 0.01 * u
    zc_ = (zf + zb) / 2
    a_ = np.linspace(0, 2 * np.pi, cols, endpoint=False)
    sn, cs = np.sin(a_), np.cos(a_)
    wave = 1 + 0.012 * np.sin(6 * a_ + 0.6) * u
    p_ = 2.4
    SV.append(np.c_[ax * np.sign(sn) * abs(sn) ** (2 / p_) * wave, np.full(cols, y), zc_ + (zf - zc_) * np.sign(cs) * abs(cs) ** (2 / p_) * wave])
SV = np.array(SV)
for _ in range(4): SV[1:-1] = (SV[:-2] + 2 * SV[1:-1] + SV[2:]) / 4
SVf = SV.reshape(-1, 3)
skW = np.zeros((len(SVf), NJ))
yy = SVf[:, 1]; side = sm((SVf[:, 0] / 0.08 + 1) / 2)
down = sm((WAIST - 0.1 - yy) / 0.4) * 0.6
knee = sm((0.56 - yy) / 0.16) * 0.22
top = sm((yy - (WAIST - 0.12)) / 0.12)
skW[:, I['Hips']] = (1 - down) * (1 - 0.5 * top); skW[:, I['Spine1']] = (1 - down) * 0.5 * top
for s_, f in (('Left', side), ('Right', 1 - side)):
    skW[:, I[s_ + 'Leg']] += (down - knee) * f; skW[:, I[s_ + 'Shin']] += knee * f
auv = np.stack(np.meshgrid(np.linspace(0, 1, cols, endpoint=False), np.linspace(0, 1, rows)), -1).reshape(-1, 2)
add('apron', SVf, grid_tris(rows, cols, wrap=True), MATS.index('apron'), W=skW, two=1, uv=auv)

# ---------------------------------------------------------------- the towel over his left shoulder
sx = float(B.J[I['LeftArm'], 0] - 0.075)
path = []
ymax = B.P[(abs(B.P[:, 0] - sx) < 0.03) & notarm, 1].max()
for y in np.linspace(ymax - 0.30, ymax - 0.02, 12): path.append([y, B.front(sx, y, 0.035, notarm) + 0.012])
front = np.array(path)
for y in np.linspace(ymax - 0.02, ymax - 0.22, 9): path.append([y, B.front(sx, y, 0.035, notarm, back=True) - 0.012])
path = np.array(path)
nf = len(front)
# over the top: a round turn between the front's last point and the back's first
arc = [[ymax + 0.012 * np.sin(a) * 1.6, (front[-1, 1] + path[nf, 1]) / 2 + (front[-1, 1] - path[nf, 1]) / 2 * np.cos(a)] for a in np.linspace(0.25, np.pi - 0.25, 7)]
line = np.r_[front, arc, path[nf:]]
line[:, 1] = np.r_[line[:1, 1], (line[:-2, 1] + 2 * line[1:-1, 1] + line[2:, 1]) / 4, line[-1:, 1]]
tc = 7
TV = np.array([[sx + wx, y, z] for (y, z) in line for wx in np.linspace(-0.062, 0.062, tc)])
tuv = np.stack(np.meshgrid(np.linspace(0, 1, tc), np.linspace(0, 1, len(line))), -1).reshape(-1, 2)
tt = grid_tris(len(line), tc)
if M.vertex_normals(TV, tt)[: tc * nf, 2].mean() < 0: tt = tt[:, ::-1]
add('towel', TV, tt, MATS.index('towel'), W=B.weights_at(TV, notarm, k=8), two=1, uv=tuv)

# ---------------------------------------------------------------- the clogs
for s_, sg in (('Left', 1), ('Right', -1)):
    an, toe = B.J[I[s_ + 'Foot']], B.J[I[s_ + 'ToeEnd']]
    d = toe - an; d[1] = 0; L = np.linalg.norm(d); d /= L
    f0 = B.P[foot, 1].min() - 0.012
    heel = np.array([an[0], f0 + 0.058, an[2]]) - d * 0.045
    c, r = Bl.chain([heel, heel + d * 0.11 + [0, 0.006, 0], heel + d * (L + 0.05) + [0, -0.008, 0]], [0.06, 0.06, 0.056], 12)
    v, t = Bl.solid((c, r), k=0.014, cell=0.007, squash=(1.08, 0.9, 1))
    v[:, 1] = np.maximum(v[:, 1], f0)
    Ws = np.zeros((len(v), NJ)); f = sm(((v - an) @ d - 0.07) / 0.05)
    Ws[:, I[s_ + 'Foot']] = 1 - f; Ws[:, I[s_ + 'ToeBase']] = f
    add('shoe', v, t, MATS.index('shoe'), W=Ws)

# ---------------------------------------------------------------- joints
J = B.J.copy()
J[I['Neck2']] = [0, CHIN - 0.01, Z0 - 0.02]
J[I['Head']] = [0, CHIN + 0.03, Z0]
J[I['HeadEnd']] = [0, CHIN + 358 * K, Z0 - 0.01]
J[I['Jaw']] = [0, CHIN + 0.05, Z0 + 0.03]
for s_, sg in (('Left', 1), ('Right', -1)):
    J[I[s_ + 'Eye']] = [sg * FT.EYE_X * K, CHIN + (Hd.CH - FT.EYE_Y) * K, Z0 + 0.11]

v3 = lambda c: 'vec3(%.3f, %.3f, %.3f)' % tuple(c / 255)
CY = float(B.J[I['Chest'], 1])
DECO = '''
void deco(vec3 rp, vec2 uv, float m, inout vec3 base, inout vec3 bshd) {
  if (abs(m - %(jacket)d.0) < 0.5) {
    if (rp.y < %(hip).3f && abs(rp.x) < 0.4) { base = %(tr_l)s; bshd = %(tr_s)s; return; }     // trousers under the apron
    if (rp.z > %(zc).3f && rp.y > %(waist).3f && rp.y < %(top).3f) {
      // the double-breasted front: two folds and two rows of three buttons
      float fx = 0.085 + 0.03 * (rp.y - %(waist).3f);
      if (abs(abs(rp.x) - fx - 0.045) < 0.0022) { base *= 0.8; bshd *= 0.86; }
      for (int k = 0; k < 3; k++) { float by = %(b0).3f - 0.115 * float(k);
        if (length(vec2(abs(rp.x) - fx, rp.y - by)) < 0.013) { base = %(bt_l)s; bshd = %(bt_s)s; } }
    }
  }
  if (abs(m - %(apron)d.0) < 0.5) {
    if (uv.y < 0.075) { base *= 0.68; bshd *= 0.78; }                                 // the waistband
    float a = abs(fract(uv.x + 0.5) - 0.5);                                          // 0 at the front's middle
    if (abs(a - 0.07) < 0.0018 && uv.y > 0.1) { base *= 0.8; bshd *= 0.86; }            // two long folds
  }
  if (abs(m - %(towel)d.0) < 0.5) {
    if (uv.y < 0.5 && (abs(uv.y - 0.07) < 0.012 || abs(uv.y - 0.12) < 0.012)) { base = vec3(0.97, 0.87, 0.74); bshd = vec3(0.62, 0.5, 0.52); }
  }
}'''
bt = mat(mix(rgb('#ece2d2'), rgb('#8a7a70'), 0.35), 0.25, 0.5, rgb('#2a1e40'))
tr = mat('#3a3644', 0.3, 0.5, rgb('#2a1e40'))
DV = dict(jacket=MATS.index('jacket'), apron=MATS.index('apron'), towel=MATS.index('towel'), hip=WAIST - 0.02, waist=WAIST, zc=float(B.J[I['Chest'], 2]),
          top=CY + 0.2, b0=CY + 0.14, tr_l=v3(tr[0]), tr_s=v3(tr[1]), bt_l=v3(bt[0]), bt_s=v3(bt[1]))
# the drawn stand, as far as a plain stand goes: the arms a little out from the barrel, big hands half closed
POSE = dict(down=0.42, straighten=0.35, curl=0.7)

# ---------------------------------------------------------------- the pack
N_ = sum(len(p['V']) for p in parts)
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
movers = {g: dict(ranges=groups[g], pivot=[float(x) for x in [p['V'] for p in parts if p['name'] == g][0].mean(0) - OFF]) for g in ('moustache', 'beard')}
header = dict(format='engine/body', version=1, id='marat-klaus', label={'ru': 'Марат (Клаус)'}, topology='marat-klaus',
              skeleton='soma', source='to3d/r16-s2-marat/tools/build.py', faces='faces', floor=floor, materials=MATS,
              deco=DECO % DV, K=K, headOrigin=[float(x) for x in OFF], movers=movers, expr=FT.EXPR,
              back=dict(top='#2e2430', bottom='#4a302c', glow='#f09a48'), seed=16,
              ui=dict(motions=[['', 'стоит'], ['walk', 'шаг'], ['wave', 'машет'], ['stomp', 'топает'], ['dance', 'танец'], ['bow', 'поклон'], ['jump', 'прыжок'], ['sit', 'садится']],
                      expr=[['calm', 'улыбается'], ['joy', 'хохочет'], ['surprise', 'удивлён'], ['sad', 'грустит'], ['anger', 'сердит']],
                      dist=6.2, cy=1.0, near=2.9, up=0.12, pose=POSE, look3d=dict(thr=0.08, light=[-0.48, 0.48, 0.74])))
pack.save(os.path.join(OUT, 'marat.json'), header, dict(
    positions=pos, triangles=tri, skinJoints=np.concatenate([p['SJ'] for p in parts]).astype(np.uint8),
    skinWeights=np.concatenate([p['SW'] for p in parts]).astype(np.float32),
    joints=J.astype(np.float32).ravel(), frames=B.frames.ravel(),
    col=lit.astype(np.uint8), shd=shd.astype(np.uint8), rim=rim.astype(np.uint8), gloss=(gl * 255).astype(np.uint8),
    uv=cat('uv', [0.0, 0.0]), tw=(cat('tw', 0.0) * 255).astype(np.uint8), pn=cat('pn', [0.0, 0.0, 0.0]),
    pw=(cat('pw', 0.0) * 255).astype(np.uint8), two=cat('two', 0.0, np.uint8), mat=matv.astype(np.uint8)))
print('pack', N_, 'vertices', len(tri), 'triangles; height', pos[:, 1].max() - floor)
