"""Аня (Klaus) in 3D: builds the character pack the viewer (web/anya.js) and the engine take.
  python3 build.py [outdir]
Bases: Anny's body (engine/data/bodies/moood-woman: its mesh, SOMA skeleton and weights) for the body, the arms and
the legs; Blender's Human Base Meshes stylised head (CC0; hbm_export.py), fitted to the drawing (head.py); the hair
lofted from the drawing's outlines (hair.py); the skirt and the scarf made here from the drawing's figure; the
face's painted layer from the drawing's SVG parts (features.py). Everything is skinned to SOMA's 77 joints."""
import os, sys, json
import numpy as np
from scipy.spatial import cKDTree
import pack, mesh as M, head as Hd, hair as Hr, features as FT

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/cache/to3d-r5-s2-anya/out'
os.makedirs(OUT, exist_ok=True)
K = Hd.K
sm = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))


def rgb(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)
def mix(a, b, t): return a + (b - a) * t


KEY, SHADE = rgb('#ffc47a'), rgb('#3a2a5a')
# per material: base colour, shadow colour (the drawing's: skin to a pink-lilac, cloth to a cool violet), rim colour
SKIN = rgb('#ecb497')
MAT = {
    'skin':   (SKIN, mix(SKIN, rgb('#4a1838'), 0.52), rgb('#ffb48a')),
    'hair':   (rgb('#94502c'), mix(rgb('#94502c'), rgb('#2a1020'), 0.5), rgb('#f0b080')),
    'cardi':  (rgb('#c99a3e'), mix(rgb('#c99a3e'), rgb('#3a2440'), 0.55), rgb('#f0b878')),
    'blouse': (rgb('#efe2cf'), mix(rgb('#efe2cf'), SHADE, 0.45), rgb('#fff0d8')),
    'scarf':  (rgb('#4f6e74'), mix(rgb('#4f6e74'), rgb('#2a2040'), 0.5), rgb('#e8b890')),
    'skirt':  (rgb('#4c5a3e'), mix(rgb('#4c5a3e'), rgb('#2a1e40'), 0.55), rgb('#e8a070')),
    'tights': (rgb('#6e5258'), mix(rgb('#6e5258'), rgb('#2a1e40'), 0.5), rgb('#d89a80')),
    'shoe':   (rgb('#4a2a1e'), mix(rgb('#5a3424'), rgb('#1e1020'), 0.5), rgb('#d08a60')),
}
MATS = list(MAT)

# ---------------------------------------------------------------- skeleton and Anny's body
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h, a, th, t = pack.body('moood-woman')
P0 = a['positions'].reshape(-1, 3).astype(float); J0 = a['joints'].reshape(-1, 3).astype(float)
FR = a['frames'].reshape(-1, 4).astype(np.float32)
TRI0 = t['triangles'].reshape(-1, 3).astype(np.int64)
SJ0 = t['skinJoints'].reshape(-1, 4).astype(np.int64); SW0 = t['skinWeights'].reshape(-1, 4).astype(float)
PARTS = t['parts'].reshape(len(P0), -1) / 255.0; PN = th['parts']
part = lambda *ns: sum(PARTS[:, PN.index(n)] for n in ns)

S = 1.03                                              # Anny 1.585 m → Аня's body under a 1.68 m head of hair


def under(j):
    out, st = [], [j]
    while st:
        k = st.pop(); out.append(k); st += list(np.where(PARENT == k)[0])
    return out


J1 = J0 * S
for s, sg in (('Left', 1), ('Right', -1)):            # shoulders a little narrower and lower (sloped, as drawn)
    for j in under(I[s + 'Shoulder']): J1[j] += [-sg * 0.006, -0.018, 0]
    for j in under(I[s + 'Arm']): J1[j] += [-sg * 0.022, -0.016, 0]
    for n in ('Leg',):
        for j in under(I[s + n]): J1[j] += [-sg * 0.012, 0, 0]


def joint_affine(j):
    """Joint j's own change of the rest about its place: the trunk slimmer, limbs thinner round their bones."""
    n = NAMES[j]
    if n in ('Hips', 'Spine1', 'Spine2'): return np.diag([0.86, 1, 0.92])
    if n in ('Chest',): return np.diag([0.82, 1, 0.9])
    if n.endswith('Shoulder'): return np.diag([0.85, 0.85, 0.9])
    r = {'LeftArm': 0.86, 'RightArm': 0.86, 'LeftForeArm': 0.86, 'RightForeArm': 0.86,
         'LeftLeg': 0.84, 'RightLeg': 0.84, 'LeftShin': 0.82, 'RightShin': 0.82}.get(n)
    if r:
        c = [k for k in range(NJ) if PARENT[k] == j][0]
        d = J0[c] - J0[j]; d /= np.linalg.norm(d)
        return r * np.eye(3) + (1 - r) * np.outer(d, d)
    if 'Foot' in n or 'Toe' in n: return np.diag([0.95, 1, 0.95])
    return np.eye(3)


AFF = [joint_affine(j) for j in range(NJ)]


def deform(P, SJ, SW):
    out = np.zeros_like(P)
    for k in range(4):
        for j in np.unique(SJ[:, k]):
            m = (SJ[:, k] == j) & (SW[:, k] > 0)
            out[m] += SW[m, k, None] * (J1[j] + S * (P[m] - J0[j]) @ AFF[j].T)
    return out


PB = deform(P0, SJ0, SW0)
# Anny's head and the upper neck out (the base head takes their place; the scarf covers the join)
gone = (part('head', 'neck') > 0.5) & (PB[:, 1] > 1.352)
tk = ~gone[TRI0].any(1)
bi = np.where(~gone)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
body = dict(V=PB[bi], T=remap[TRI0[tk]], SJ=SJ0[bi], SW=SW0[bi])
bp = PARTS[bi]; by = body['V'][:, 1]
bpart = lambda *ns: sum(bp[:, PN.index(n)] for n in ns)
mat = np.full(len(bi), MATS.index('cardi'))
mat[bpart('Lhand', 'Rhand') > 0.5] = MATS.index('skin')
legs = bpart('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot', 'pelvis') > 0.5
mat[legs & (by < 0.93)] = MATS.index('tights')
mat[bpart('Lfoot', 'Rfoot') > 0.5] = MATS.index('shoe')
mat[(by < 0.075) & legs] = MATS.index('shoe')
mat[bpart('neck') > 0.5] = MATS.index('skin')
# the blouse in the cardigan's opening: a V from the neckline down to the chest
bv = body['V']; vw = np.interp(by, [1.17, 1.33], [0.0, 0.034])
# the cardigan a little off the body (knit thickness), the shoes a little fuller
nb = M.vertex_normals(bv, body['T'])
off = np.where(mat == MATS.index('cardi'), 0.006, 0) + np.where(mat == MATS.index('shoe'), 0.004, 0)
# the cardigan's hem flares over the hips (as drawn) and is cut straight
hip = (mat == MATS.index('cardi')) & (by < 1.05)
off = off + np.where(hip, 0.02 * sm((1.05 - by) / 0.10), 0)
bv = bv + nb * off[:, None]
chest = (mat != MATS.index('skin')) & (by > 1.02) & (by < 1.32) & (bv[:, 2] > -0.02) & (bpart('spine') > 0.3)
Ab = M.adjacency(len(bv), body['T'])
bv = M.smooth(bv, Ab, chest * sm((bv[:, 2] + 0.02) / 0.06), iters=60, lam=0.5)
# shoes: the toes smoothed into one shoe form
feet = mat == MATS.index('shoe')
bv = M.smooth(bv, Ab, feet * 1.0, iters=90, lam=0.5)
body['V'] = bv
body['mat'] = mat
body['W'] = None

# ---------------------------------------------------------------- the head
hv, hP, patch = Hd.build()
hT = M.triangulate(hP)
neck_c = PB[(abs(PB[:, 1] - 1.34) < 0.008) & (part('neck', 'spine') > 0.3) & (abs(PB[:, 0]) < 0.05)]
nz = (neck_c[:, 2].max() + neck_c[:, 2].min()) / 2
hb = hv[hv[:, 1] < hv[:, 1].min() + 0.01]
CHIN = 1.422
OFF = np.array([0, CHIN, nz - (hb[:, 2].max() + hb[:, 2].min()) / 2])
HV = hv + OFF
yd_h = Hd.CHIN_Y - hv[:, 1] / K                      # drawing heights of the head's vertices
# proxy normals for the face's shade: the head smoothed into one plain form
Ah = M.adjacency(len(HV), hT)
hs = M.smooth(HV, Ah, np.ones(len(HV)), iters=40, lam=0.5)
pn = M.vertex_normals(hs, hT)
pw = 0.7 * (1 - sm((yd_h - 330) / 40))
# the painted layer: front projection of the face sheet (features.py frame)
xf = hv[:, 0] / K + Hd.XF
uv = np.c_[(xf - FT.X0) / FT.W, 1 - (yd_h - FT.Y0) / FT.H]
nh = M.vertex_normals(HV, hT)
tw = sm((nh[:, 2] - 0.05) / 0.25) * (hv[:, 2] > 0.0) * (uv[:, 0] > 0) * (uv[:, 0] < 1) * (uv[:, 1] > 0) * (uv[:, 1] < 1)
# weights: the head, then down the neck to the chest
def chain_w(yd, n, marks):
    W = np.zeros((n, NJ)); js = ['Head', 'Neck2', 'Neck1', 'Chest']
    ts = [sm((yd - m) / 40) for m in marks]
    W[:, I['Head']] = 1 - ts[0]
    W[:, I['Neck2']] = ts[0] * (1 - ts[1])
    W[:, I['Neck1']] = ts[0] * ts[1] * (1 - ts[2])
    W[:, I['Chest']] = ts[0] * ts[1] * ts[2]
    return W


headW = chain_w(yd_h - 20 * sm(hv[:, 2] / 0.04), len(HV), [345, 395, 440])

# ---------------------------------------------------------------- the hair
rv, rT, outer, yd_r = Hr.build(hv, M.vertex_normals(hv, hT))
RV = rv + OFF
hairW = chain_w(yd_r, len(RV), [400, 1e9, 1e9])
# the curtains' lower part follows the chest a little, so the tips rest on the shoulders as the head turns
low = sm((yd_r - 380) / 80) * 0.5
hairW = hairW * (1 - low)[:, None]; hairW[:, I['Chest']] += low

# ---------------------------------------------------------------- the skirt: an A-line from the waist to mid-calf
def ring_body(y, pad):
    m = (abs(body['V'][:, 1] - y) < 0.01) & (bpart('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand') < 0.3)
    v = body['V'][m]
    return abs(v[:, 0]).max() + pad, v[:, 2].max() + pad, v[:, 2].min() - pad


rows, cols = 26, 72
ys = np.linspace(0.97, 0.40, rows)
SV = []
for i, y in enumerate(ys):
    u = i / (rows - 1)
    ax, zf, zb = ring_body(min(max(y, 0.62), 0.97), 0.006)
    flare = 0.10 * u ** 1.3
    ax = max(ax, 0.0) + flare * 1.0; zf2 = zf + flare * 0.75; zb2 = zb - flare * 0.7
    zc = (zf2 + zb2) / 2
    th_ = np.linspace(0, 2 * np.pi, cols, endpoint=False)
    sn, cs = np.sin(th_), np.cos(th_)
    wave = 1 + 0.025 * np.sin(5 * th_ + 1.0) * u           # a soft wave in the hem, as drawn
    x = ax * sn * wave; z = zc + np.where(cs > 0, zf2 - zc, zc - zb2) * cs * wave
    SV.append(np.c_[x, np.full(cols, y), z])
SV = np.array(SV).reshape(-1, 3)
ST = []
for r in range(rows - 1):
    for c in range(cols):
        a0, a1 = r * cols + c, r * cols + (c + 1) % cols; b0, b1 = a0 + cols, a1 + cols
        ST += [[a0, b0, a1], [a1, b0, b1]]
ST = np.array(ST)
# weights: the pelvis at the waist; lower, each side's thigh then shin takes a share, smoothly across the middle
skW = np.zeros((len(SV), NJ))
yy = SV[:, 1]; side = sm((SV[:, 0] / 0.05 + 1) / 2)       # 0 right … 1 left
down = sm((1.0 - yy) / 0.35) * 0.6
knee = sm((0.55 - yy) / 0.15) * 0.25
skW[:, I['Hips']] = 1 - down
for s, f in (('Left', side), ('Right', 1 - side)):
    skW[:, I[s + 'Leg']] += (down - knee) * f
    skW[:, I[s + 'Shin']] += knee * f

# ---------------------------------------------------------------- the scarf: a soft roll round the neck's base, its end down the front
def tube(path, radius, n=18, closed=False):
    path = np.asarray(path, float)
    V, T = [], []
    for i, p in enumerate(path):
        d = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]; d /= np.linalg.norm(d)
        u = np.cross(d, [0, 0, 1.0]) if abs(d[2]) < 0.9 else np.cross(d, [1.0, 0, 0]); u /= np.linalg.norm(u)
        w = np.cross(d, u)
        rx, rz = radius[i] if np.ndim(radius[i]) else (radius[i], radius[i])
        for k in range(n):
            a_ = 2 * np.pi * k / n
            V.append(p + u * np.cos(a_) * rx + w * np.sin(a_) * rz)
    m = len(path)
    for i in range(m if closed else m - 1):
        for k in range(n):
            a0, a1 = i * n + k, i * n + (k + 1) % n; b0, b1 = ((i + 1) % m) * n + k, ((i + 1) % m) * n + (k + 1) % n
            T += [[a0, a1, b0], [a1, b1, b0]]
    return np.array(V), np.array(T)


th_ = np.linspace(0, 2 * np.pi, 48, endpoint=False)
ring = np.c_[0.056 * np.sin(th_), 1.368 - 0.010 * np.cos(th_), nz + 0.004 + 0.052 * np.cos(th_)]
sv1, st1 = tube(ring, [(0.021, 0.017)] * len(ring), closed=True)
# its end hangs on the chest, a flat knitted band: laid on the cardigan's surface
bv_ = body['V']
def on_chest(x, y, lift):
    m = (abs(bv_[:, 0] - x) < 0.012) & (abs(bv_[:, 1] - y) < 0.012) & (bv_[:, 2] > 0)
    return bv_[m, 2].max() + lift
ys_ = np.linspace(1.345, 1.215, 16)
end = np.array([[0.022 + 0.01 * (1.345 - y) / 0.13, y, on_chest(0.022 + 0.01 * (1.345 - y) / 0.13, y, 0.012)] for y in ys_])
end[0, 2] = max(end[0, 2], nz + 0.06)
end[:, 2] = np.polyval(np.polyfit(end[:, 1], end[:, 2], 2), end[:, 1])
sv2, st2 = tube(end, [(0.019, 0.006)] * len(end))
SCV = np.r_[sv1, sv2]; SCT = np.r_[st1, st2 + len(sv1)]
scW = np.zeros((len(SCV), NJ)); top = sm((SCV[:, 1] - 1.31) / 0.05)
scW[:, I['Chest']] = 1 - 0.5 * top; scW[:, I['Neck1']] = 0.5 * top


# ---------------------------------------------------------------- joints for the new head, and the pack
J = J1.copy()
J[I['Neck1']] = [0, 1.345, nz]
J[I['Neck2']] = [0, CHIN - 0.025, nz + 0.006]
J[I['Head']] = [0, CHIN + 0.025, OFF[2] + 0.004]
J[I['HeadEnd']] = [0, CHIN + 0.235, OFF[2] - 0.01]
J[I['Jaw']] = [0, CHIN + 0.05, OFF[2] + 0.03]
for s, sg in (('Left', 1), ('Right', -1)):
    J[I[s + 'Eye']] = [sg * 32 * K, CHIN + (370 - 248) * K, OFF[2] + 0.075]


def top4(W):
    idx = np.argsort(-W, 1)[:, :4]; w = np.take_along_axis(W, idx, 1); w /= w.sum(1, keepdims=True)
    return idx, w


parts_out = []
def add(V, T, mat, SJ=None, SW=None, W=None, **attr):
    if W is not None: SJ, SW = top4(W)
    parts_out.append(dict(V=V, T=T, mat=np.broadcast_to(mat, (len(V),)), SJ=SJ, SW=SW, **attr))


add(body['V'], body['T'], body['mat'], body['SJ'], body['SW'], rp=body['V'].copy())
add(HV, hT, MATS.index('skin'), W=headW, uv=uv, tw=tw, pn=pn, pw=pw)
add(RV, rT, MATS.index('hair'), W=hairW, two=1)
add(SV, ST, MATS.index('skirt'), W=skW, two=1)
add(SCV, SCT, MATS.index('scarf'), W=scW)

N = sum(len(p['V']) for p in parts_out)
cat = lambda k, d: np.concatenate([np.broadcast_to(p.get(k, d), (len(p['V']),) + np.shape(d)) if p.get(k) is None or np.ndim(p.get(k)) == 0 else p[k] for p in parts_out])
pos = np.concatenate([p['V'] for p in parts_out]).astype(np.float32)
tri, base = [], 0
for p in parts_out: tri.append(p['T'] + base); base += len(p['V'])
tri = np.concatenate(tri).astype(np.uint32)
SJ = np.concatenate([p['SJ'] for p in parts_out]).astype(np.uint8)
SW = np.concatenate([p['SW'] for p in parts_out]).astype(np.float32)
matv = np.concatenate([p['mat'] for p in parts_out])
col = np.array([MAT[MATS[m]][0] for m in matv]); shd = np.array([MAT[MATS[m]][1] for m in matv]); rim = np.array([MAT[MATS[m]][2] for m in matv])
uvv = np.concatenate([p['uv'] if 'uv' in p else np.zeros((len(p['V']), 2)) for p in parts_out]).astype(np.float32)
twv = np.concatenate([p['tw'] if 'tw' in p else np.zeros(len(p['V'])) for p in parts_out])
pnv = np.concatenate([p['pn'] if 'pn' in p else np.zeros((len(p['V']), 3)) for p in parts_out]).astype(np.float32)
pwv = np.concatenate([p['pw'] if 'pw' in p else np.zeros(len(p['V'])) for p in parts_out])
two = np.concatenate([np.full(len(p['V']), p.get('two', 0)) for p in parts_out]).astype(np.uint8)
ishair = (matv == MATS.index('hair')).astype(np.uint8)
iscardi = (matv == MATS.index('cardi')).astype(np.uint8)
rpv = np.concatenate([p['rp'] if 'rp' in p else np.zeros((len(p['V']), 3)) for p in parts_out]).astype(np.float32)

floor = float(pos[:, 1].min())
header = dict(format='engine/body', version=1, id='anya-klaus', label={'ru': 'Аня (Клаус)'}, topology='anya-klaus',
              skeleton='soma', source='to3d/r5-s2-anya/tools/build.py', faces='faces', skinning='cor', floor=floor,
              materials=MATS)
pack.save(os.path.join(OUT, 'anya.json'), header, dict(
    positions=pos, triangles=tri, skinJoints=SJ, skinWeights=SW,
    joints=J.astype(np.float32).ravel(), frames=FR.ravel(),
    col=col.astype(np.uint8), shd=shd.astype(np.uint8), rim=rim.astype(np.uint8),
    uv=uvv, tw=(twv * 255).astype(np.uint8), pn=pnv, pw=(pwv * 255).astype(np.uint8),
    pj=np.full(N, I['Head'], np.uint8), two=two, hair=ishair, cardi=iscardi, rp=rpv))
print('pack', N, 'vertices', len(tri), 'triangles; height', pos[:, 1].max() - floor)
