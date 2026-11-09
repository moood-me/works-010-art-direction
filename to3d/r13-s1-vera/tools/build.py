"""Вера (С1, Pixar) assembled: Anny's fitted woman body, the fitted Human Base Meshes head with its eyes as balls
under real lids, the sleek hair with its bun, the rectangular glasses, the turtleneck, the long coat (its top cut from
the body's own surface and brought to the drawing's sections, its skirt lofted on the same sections), the narrow
trousers and flat shoes — every part skinned on SOMA's 77 joints — written as one model pack (model.py) with its
look's attributes and baked ambient occlusion."""
import numpy as np
from common import CACHE, IX, NAMES, NJ, K, FLOOR, dense, top4, HERE
from fitbody import B, fit
from model import part, write, MATS
from meshcut import cut, loops, smooth, rim, neighbours
from sphere import sphere
from quads import Quads
from eyefit import ring, OUTER, LINING
import hair as HAIR
import char
from drawing import C, P as PERSON, head as drawn_head
import igl

OUT = [f'{HERE}/web/data']


from build_util import vnormals, sstep


def one(n, joint): return np.tile([IX[joint], 0, 0, 0], (n, 1)), np.tile([1., 0, 0, 0], (n, 1))


# ---------------- the body ----------------
V, J = fit()
T = B['triangles']; PP = B['parts'] / 255.; PN = B['partnames']
pw = lambda *names: sum(PP[:, PN.index(n)] for n in names)
D = dense(B['sj'], B['sw'])
NB = vnormals(V, T)

UY = lambda y: (FLOOR - y) * K            # a height of the drawing (person units, y down) in metres
# ---------------- the head (head units: y up, crown +50, chin −50; drawn HS times larger, its centre at person y 8) --
HS = char.HS
HY = FLOOR - PERSON['head_at'][1] - 1.0     # a unit lower than drawn: the chin comes down to the collar
Z0 = J[IX['Neck1'], 2] - PERSON['neck'][1][2] * K          # the drawing's axis (its z 0) in the model, by the neck's foot
HZ = Z0 / K
H2W = lambda X: np.c_[X[:, 0] * HS * K, (HY + X[:, 1] * HS) * K, (X[:, 2] * HS + HZ) * K]
MY = -C['mouth_y']
hf = np.load(f'{CACHE}/head_fit.npz')
HV = hf['final'].copy(); HT = hf['T']; MI = hf['mirror']; BALLS = hf['balls']; V0 = hf['base']
from hbm import load as hbm_load
HQ = hbm_load()['head'][2]
Q = Quads(HQ)


def neck(X):
    """below the jaw the base's neck becomes the drawing's thin round neck (radius 9.4 head units about x 0, z −10;
    the drawn one is 8.2), blended in under the jaw line"""
    y, z = X[:, 1], X[:, 2]
    yj = np.interp(z, [-30, -12, 8, 22, 32], [-35, -42, -47.5, -50, -52])          # the jaw line, higher at the nape
    w = sstep(yj - y, 0, 7)
    r = 9.4 + 1.0 * sstep(-y, 58, 75)
    zc = -10.0
    d = np.c_[X[:, 0], z - zc]; rr = np.linalg.norm(d, axis=1)
    tgt = d / np.maximum(rr, 1e-6)[:, None] * r[:, None]
    out = X.copy(); out[:, 0] = X[:, 0] * (1 - w) + tgt[:, 0] * w; out[:, 2] = z * (1 - w) + (zc + tgt[:, 1]) * w
    return out


HV = neck(HV)
# the neck smoothed where the reshaping left folds (the nape, under the jaw), the face and ears left as they are
nm = sstep(-HV[:, 1], 36, 46) * (1 - sstep(HV[:, 2], 20, 28)) * (np.abs(HV[:, 0]) < 30)
HV = smooth(HV, HT, it=40, lam=0.5, mask=nm.astype(float))
HW = H2W(HV)
# the head's joints where the drawn head is (frames kept)
J2 = J.copy()
J2[IX['Head']] = H2W(np.array([[0, -42.0, -9]]))[0]
J2[IX['HeadEnd']] = H2W(np.array([[0, 50.0, -4]]))[0]
J2[IX['Jaw']] = H2W(np.array([[0, -22.0, 0]]))[0]
J2[IX['LeftEye']] = H2W(BALLS[0:1, :3])[0]; J2[IX['RightEye']] = H2W(BALLS[1:2, :3])[0]
J2[IX['Neck2']] = (J2[IX['Neck1']] + J2[IX['Head']]) / 2


def lid_data(HV, Q, V0, MI, BALLS):
    out = np.zeros((len(HV), 4))
    for bi, side in ((0, 1), (1, -1)):
        c, R = BALLS[bi, :3], BALLS[bi, 3]
        M = ring(Q, V0, OUTER[0]); M = M if side == 1 else MI[M]
        pm = HV[M] - c; em = np.degrees(np.arctan2(pm[:, 1], pm[:, 2])); xm = pm[:, 0] * side
        mid = np.interp(xm, np.sort(xm), em[np.argsort(xm)])
        order = np.argsort(xm); xs = np.linspace(xm.min(), xm.max(), 40)
        up = np.array([em[(np.abs(xm - x) < 1.8) & (em >= np.median(em))].max(initial=-90) for x in xs])
        lo = np.array([em[(np.abs(xm - x) < 1.8) & (em <= np.median(em))].min(initial=90) for x in xs])
        ok = (up > -90) & (lo < 90); xs, up, lo = xs[ok], up[ok], lo[ok]
        close = lo + 0.28 * (up - lo)
        p = HV - c; r = np.linalg.norm(p, axis=1); e = np.degrees(np.arctan2(p[:, 1], p[:, 2])); x = p[:, 0] * side
        U = np.interp(x, xs, up); Lo = np.interp(x, xs, lo); Cl = np.interp(x, xs, close); Mid = (U + Lo) / 2
        W = (1 - sstep(r, R + 3.0, R + 6.5)) * (1 - sstep(np.abs(x - (xs[0] + xs[-1]) / 2), 0.42 * (xs[-1] - xs[0]), 0.62 * (xs[-1] - xs[0]))) * (p[:, 2] > -0.4 * R)
        upper = e > Mid
        m = (W > 0) & (np.abs(p[:, 0]) < 22)
        out[m & upper, 0] = (U - Cl)[m & upper]
        out[m & ~upper, 1] = (Cl - Lo)[m & ~upper]
        out[m, 2] = W[m]; out[m, 3] = side
    return out


def head_skin(W):
    """the head on Head; its neck from Head down to Neck1"""
    y = W[:, 1]; yH, y2, y1 = J2[IX['Head'], 1], J2[IX['Neck2'], 1], J2[IX['Neck1'], 1]
    Dh = np.zeros((len(W), NJ))
    a = np.clip((y - y2) / (yH - y2), 0, 1); b = np.clip((y - y1) / (y2 - y1), 0, 1)
    Dh[:, IX['Head']] = a; Dh[:, IX['Neck2']] = (1 - a) * b; Dh[:, IX['Neck1']] = (1 - a) * (1 - b)
    return top4(Dh)


# the face layer's coordinates (front projection of head units −60…60) and the lash line along the upper lids
HN = vnormals(HV, HT)
uv = np.c_[(HV[:, 0] + 60) / 120, (60 - HV[:, 1]) / 120]
facing = np.clip(HN[:, 2], 0, 1) * (HV[:, 2] > 0)
lash = np.zeros(len(HV))
for side, bi in ((1, 0), (-1, 1)):
    c = BALLS[bi, :3]
    for s, base_w in ((OUTER[0], 1.0), (LINING[0], 1.0), (OUTER[1], 0.0)):
        L = ring(Q, V0, s)
        L = L if side == 1 else MI[L]
        X = HV[L]
        up = X[:, 1] > c[1] - 1.5 + 2.0 * (side * (X[:, 0] - c[0]) / 11)       # the upper half (the corner line tilts)
        t = np.clip((side * (X[:, 0] - c[0]) + 10) / 20, 0, 1)                 # 0 at the inner corner, 1 the outer
        if s == OUTER[1]:
            w = np.clip((t - 0.4) / 0.6, 0, 1) * 0.5                           # the line thickens to the outer corner
        else:
            w = np.full(len(L), base_w)
        lash[L] = np.maximum(lash[L], w * up)
# the mouth's inside (its bag) and the lips
mouth_in = np.zeros(len(HV), bool)
for s in [798, 1822, 1836, 1812, 1813, 1815, 1816, 1798]:
    mouth_in[ring(Q, V0, s)] = True
outer = hf['outer']
# and what lies deep behind the lips (the bag's back), found by depth on the final head
lipz = HV[ring(Q, V0, 767), 2].mean()
_nb = neighbours(HT, len(HV)); _front = [int(v) for v in np.where(mouth_in)[0]]; _seen = set(_front)
while _front:                          # everything inside, reached from the bag's rings without coming out to the face
    _nx = []
    for v in _front:
        for u in _nb[v]:
            if u not in _seen and not outer[u] and abs(HV[u, 0]) < 22 and HV[u, 1] < MY + 22: _seen.add(int(u)); _nx.append(int(u))
    _front = _nx
mouth_in[list(_seen)] = True
# the eye sockets' lining (under the lids, behind the balls)
sock = np.zeros(len(HV), bool)
for s in LINING: L = ring(Q, V0, s); sock[L] = True; sock[MI[L]] = True
for bi in range(2):
    sock |= np.linalg.norm(HV - BALLS[bi, :3], axis=1) < BALLS[bi, 3] + 0.3
inner_lip = np.zeros(len(HV), bool)
for s_ in [770, 767]: inner_lip[ring(Q, V0, s_)] = True         # the lips to their parting line carry the lip colour
mat = np.where(inner_lip, MATS.index('lip'), np.where(mouth_in, MATS.index('mouth'), MATS.index('skin')))
aux = np.c_[uv, facing, lash]
# the jaw's share: the lower lip and everything below the mouth's line (found on the base, where the line ring's two
# halves part), fading under the chin into the neck and back toward the ears
L767 = ring(Q, V0, 767); y767 = V0[L767, 1].mean()
hm = 0.05 + 2.6 * sstep(np.abs(V0[:, 0]), 5.0, 9.8)
below = sstep(y767 - V0[:, 1], -hm, hm)
# the lips' rings and the mouth's bag: each ring runs from the middle of one lip round a corner to the middle of the
# other, so its place along the ring says which lip a vertex is on (by height the two halves of the parting line
# cannot be told apart: they lie 0.15 units from each other) — the upper half stays, the lower goes with the jaw
for s_ in [767, 770, 774, 798, 1822, 1836, 1851, 1798, 1812, 1813, 1815, 1816]:
    L = ring(Q, V0, s_); n_ = len(L)
    c_ = np.cos(2 * np.pi * np.arange(n_) / n_) * (1 if V0[L[0], 1] > V0[L[n_ // 2], 1] else -1)
    below[L] = sstep(-c_, -0.3, 0.3)
jaw = below * (1 - sstep(-HV[:, 1], 58, 72)) * sstep(HV[:, 2], -16, 4) * (1 - sstep(np.abs(HV[:, 0]), 30, 42))
# the lids: for each vertex of an upper (lower) lid, how far it turns about its ball's x axis to shut the eye (deg),
# and its weight — the margin's elevation over the ball comes down to a closing line low in the opening
lid = lid_data(HV, Q, V0, MI, BALLS)
lid_jaw = None
# the neck ends inside the shirt
A = np.c_[mat, aux, HV, lid, jaw]
hv, ht, a, _ = cut(HW, HT, -(HW[:, 1] - UY(90)), A)
hmat = np.rint(a[:, 0]).astype(int); haux = a[:, 1:5]; hrest = a[:, 5:8]; hlid = a[:, 8:12]; hjaw = a[:, 12]
sj, sw = head_skin(hv)
parts = [part(hv, ht, sj, sw, hmat, aux=haux, pat=hv, name='head')]
parts[0]['face'] = hlid; parts[0]['jaw'] = hjaw
HEAD_REST = hrest                       # head units of the head part's vertices (for the face rig)

# the eyes: balls with their own direction (the iris looks along +z of the ball)
for bi, nm in ((0, 'eyeL'), (1, 'eyeR')):
    c, R = BALLS[bi, :3], BALLS[bi, 3]
    X, F = sphere(np.zeros(3), 1.0, n=30, m=48)
    X = X[:, [0, 2, 1]] * [1, 1, 1]; F = F[:, ::-1]                           # pole along z
    W = H2W(c + X * R)
    sj, sw = one(len(W), 'Head')
    parts.append(part(W, F, sj, sw, 'eye', aux=np.c_[X, np.zeros(len(X))], name=nm))

# the teeth: rows of small rounded teeth behind the lips (the drawing's Тим has a gap in the upper row)
lipz = HV[ring(Q, V0, 767), 2].mean()
def teeth_row(y0, h, n, gap, rad, depth_z, name):
    Xs, Fs, k0 = [], [], 0
    zc = depth_z - rad
    for i in range(n):
        if i == gap: continue
        a = (i - (n - 1) / 2) * 2.3 / rad
        w = 2.6 if abs(i - (n - 1) / 2) < 1.6 else 2.3
        X, F = sphere(np.zeros(3), 1.0, n=10, m=14)
        X = np.sign(X) * np.abs(X) ** 0.45
        X = X * [w / 2 * 1.02, h / 2, 0.9]
        ca, sa = np.cos(a), np.sin(a)
        X = np.c_[X[:, 0] * ca + X[:, 2] * sa, X[:, 1], -X[:, 0] * sa + X[:, 2] * ca]
        X = X + [rad * np.sin(a), y0, zc + rad * np.cos(a)]
        Xs.append(X); Fs.append(F + k0); k0 += len(X)
    X = np.concatenate(Xs); F = np.concatenate(Fs)
    sj, sw = one(len(X), 'Head')
    return part(H2W(X), F, sj, sw, 'teeth', name=name)
parts.append(teeth_row(MY + 0.2, 5.2, 8, -1, 8.0, lipz - 1.6, 'teethUp'))
parts.append(teeth_row(MY - 3.0, 3.4, 8, -1, 7.5, lipz - 2.4, 'teethLo')); parts[-1]['jaw'] = np.ones(len(parts[-1]['V']))

# the tongue: a flat rounded body on the mouth's floor behind the lower teeth, going with the jaw (the drawing paints one
# in every open mouth; without it the mouth is a dark pocket — Р6's weak place)
X, F = sphere(np.zeros(3), 1.0, n=14, m=20)
X = X * [6.2, 2.0, 7.0] + [0, MY - 1.6, lipz - 12.0]
X[:, 1] -= 1.2 * np.clip((X[:, 2] - (lipz - 12.0)) / 7.0, -1, 1) ** 2          # its tip and root dip a little
sj, sw = one(len(X), 'Head')
parts.append(part(H2W(X), F[:, ::-1], sj, sw, 'tongue', name='tongue')); parts[-1]['jaw'] = np.ones(len(X))

# ---------------- the hair: the cap, the bun, the grey streak ----------------
for hv_, ht_, ha_, hm_ in HAIR.build(HV, HT):
    sj, sw = one(len(hv_), 'Head')
    parts.append(part(H2W(hv_), ht_, sj, sw, hm_, aux=ha_, name='hair'))


# ---------------- the glasses: thin rectangular rims before the eyes, a bridge, temples to the ears ----------------
def tube_mesh(pts, r, nv=8, closed=False):
    pts = np.asarray(pts, float); n = len(pts); X, F = [], []
    for i in range(n):
        a = pts[(i - 1) % n] if (closed or i > 0) else pts[i]; b = pts[(i + 1) % n] if (closed or i < n - 1) else pts[i]
        t = b - a; t /= np.linalg.norm(t)
        u = np.cross(t, [0, 0, 1.0]);
        if np.linalg.norm(u) < 1e-3: u = np.cross(t, [0, 1.0, 0])
        u /= np.linalg.norm(u); w = np.cross(t, u)
        for j in range(nv):
            q = 2 * np.pi * j / nv; X.append(pts[i] + r * (np.cos(q) * u + np.sin(q) * w))
    m = n if closed else n - 1
    for i in range(m):
        for j in range(nv):
            a_, b_ = i * nv + j, i * nv + (j + 1) % nv; c_, d_ = ((i + 1) % n) * nv + j, ((i + 1) % n) * nv + (j + 1) % nv
            F += [(a_, c_, b_), (b_, c_, d_)]
    return np.array(X), np.array(F)


def glasses():
    """cast.glasses(shape='rect', lift=8, cy=1, rx=10.5, ry=7): the same rims, wrapped a little round the face"""
    hd = drawn_head(); out = []
    ex, yc, rx, ry, lift = C['eye_x'], C['eye_y'] + 1.0, 10.5, 7.0, 8.0
    S = lambda x, y, l: np.array([hd.surf(x, y)[0], -y, hd.surf(x, y)[2] + l])
    z0 = hd.surf(ex, yc)[2] + lift
    for sd in (-1, 1):
        ring = []
        for i in range(40):
            a = 2 * np.pi * i / 40; ca, sa = np.cos(a), np.sin(a)
            x = sd * ex + rx * np.sign(ca) * abs(ca) ** 0.5; y = yc + ry * np.sign(sa) * abs(sa) ** 0.5
            ring.append([x, -y, z0 - 0.012 * (abs(x) - ex) * abs(abs(x) - ex + rx) ])      # the rims turn back a little toward the temples
        out.append(tube_mesh(ring, 0.5, closed=True))
        edge = np.array(ring)[np.argmax(np.array(ring)[:, 0] * sd - 0.3 * np.abs(np.array(ring)[:, 1] + yc - ry * 0.3))]
        ear = np.array([sd * (hd.width(C.get('ear_y', 8)) + 1.5), -(C.get('ear_y', 8) - 5), -6.0])
        mid = (edge + ear) / 2 + [sd * 1.5, 0, 0]
        out.append(tube_mesh([edge, mid, ear, ear + [-sd * 1.0, -4.0, -3.0]], 0.5))
    by = yc - ry * 0.25
    out.append(tube_mesh([[-ex + rx * 0.95, -by, z0], [0, -by + 1.2, z0 + 1.2], [ex - rx * 0.95, -by, z0]], 0.55))
    return out


for X, F in glasses():
    sj, sw = one(len(X), 'Head')
    parts.append(part(H2W(X), F, sj, sw, 'frame', name='glasses'))

# ---------------- clothes ----------------
def bone_t(X, a, b):
    A_, Bb = J[IX[a]], J[IX[b]]; d = Bb - A_
    return ((X - A_) @ d) / (d @ d)


def bone_r(X, a, b):
    A_, Bb = J[IX[a]], J[IX[b]]; d = Bb - A_; d = d / np.linalg.norm(d)
    return np.linalg.norm((X - A_) - np.outer((X - A_) @ d, d), axis=1)


def shell(region_f, off, mat, smooth_it=3, name='', move=None):
    """the body's surface where region_f < 0, pushed out along its normals by off (per vertex) or moved by move"""
    A_ = np.c_[D, NB, off, V if move is None else move]
    v, t, a, on = cut(V, T, region_f, A_)
    d, n, o, mv = a[:, :NJ], a[:, NJ:NJ + 3], a[:, NJ + 3], a[:, NJ + 4:]
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    v = (v if move is None else mv) + n * o[:, None]
    v = smooth(v, t, it=smooth_it, lam=0.3, fixed=np.where(on)[0])
    sj, sw = top4(d)
    return part(v, t, sj, sw, mat, name=name), on


# the coat's sections as the drawing sweeps them (cast.vera_person, the last layer): half-width w, depth before (zf)
# and behind (zb) the figure's axis over the height, superellipse sections of power 2.1
COAT = PERSON['layers'][-1]
from pix import Head as Sweep
_sw = Sweep(COAT['w'], COAT['zf'], COAT['zb'], n=COAT.get('n', 2.1))


# the coat's axis: the drawing's at the shoulders, the pelvis' own middle from the belt down (Anny stands with the
# pelvis a little behind the neck; the drawing's figure is a straight column)
_pb = (np.abs(V[:, 1] - J[IX['Hips'], 1]) < 0.06) & (np.abs(V[:, 0]) < 0.1)
ZB = (V[_pb, 2].min() + V[_pb, 2].max()) / 2
zax = lambda yw: Z0 + (ZB - Z0) * sstep(UY(120) - yw, 0, UY(120) - UY(232))


def coat_r(yw, psi):
    """the coat's radius about the axis at height yw (m) toward the direction psi (atan2(x, z))"""
    yd = np.clip(FLOOR - yw / K, COAT['y0'], COAT['y1'])
    ph = np.linspace(-np.pi, np.pi, 181)
    out = np.zeros(len(yw))
    for u in np.unique(np.round(yd, 0)):
        m = np.round(yd, 0) == u
        xz = np.array([_sw.section(u, p) for p in ph]) * K
        ang = np.unwrap(np.arctan2(xz[:, 0], xz[:, 1])); rr = np.hypot(xz[:, 0], xz[:, 1])
        o = np.argsort(ang)
        out[m] = np.interp(psi[m], np.r_[ang[o] - 2 * np.pi, ang[o], ang[o] + 2 * np.pi], np.r_[rr[o], rr[o], rr[o]])
    return out


y = V[:, 1]
BELT = UY(232); HEM = UY(COAT['y1']); COLL = UY(82)
arm = pw('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand')
armside = arm > 0.3
sl = np.where(V[:, 0] > 0, 0.5 * bone_t(V, 'LeftArm', 'LeftForeArm') + np.clip(bone_t(V, 'LeftForeArm', 'LeftHand'), 0, 9) * 0.5,
              0.5 * bone_t(V, 'RightArm', 'RightForeArm') + np.clip(bone_t(V, 'RightForeArm', 'RightHand'), 0, 9) * 0.5)
sl = np.where(sl < 0.5, np.minimum(sl, 0.5), sl)            # 0 at the shoulder, 0.5 the elbow, 1 the wrist
# the sleeves: the arm's surface out to the drawn sleeve (radius 13.5 → 12 → 11 units; the arm is 9 → 7 → 5.2)
SLEEVE_END = 0.965
r_arm = np.where(V[:, 0] > 0, np.where(sl < 0.5, bone_r(V, 'LeftArm', 'LeftForeArm'), bone_r(V, 'LeftForeArm', 'LeftHand')),
                 np.where(sl < 0.5, bone_r(V, 'RightArm', 'RightForeArm'), bone_r(V, 'RightForeArm', 'RightHand')))
r_sleeve = np.interp(sl, [0, 0.5, 1], np.array(PERSON['sleeve']['r']) * K)
off_arm = np.clip(r_sleeve - r_arm, 0.006, 0.022)
# the trunk: out to the coat's section
ZA = zax(y)
psi = np.arctan2(V[:, 0], V[:, 2] - ZA); r_body = np.hypot(V[:, 0], V[:, 2] - ZA)
r_coat = np.maximum(coat_r(y, psi), r_body + 0.007)
trunk_pos = np.c_[np.sin(psi) * r_coat, y, ZA + np.cos(psi) * r_coat]
aw = sstep(arm, 0.08, 0.6)[:, None]
move = trunk_pos * (1 - aw) + (V + NB * off_arm[:, None]) * aw
f_coat = np.maximum.reduce([BELT - y, y - COLL, np.where(armside, sl - SLEEVE_END, -1)])
coat, on = shell(f_coat, np.zeros(len(V)), 'coat', smooth_it=14, move=move, name='coat')
# the neckline drawn in round the turtleneck
sv = coat['V']; nz = Z0 + PERSON['neck'][1][2] * K
rr = np.hypot(sv[:, 0], sv[:, 2] - nz)
sgy = sstep(sv[:, 1], UY(104), COLL) ** 1.2
rt = 14.5 * K
k = np.where(rr > rt, (rr + (rt - rr) * sgy) / rr, 1.0)
sv[:, 0] *= k; sv[:, 2] = nz + (sv[:, 2] - nz) * k
# the cuffs: the sleeves' ends turned in
cv_, ct_, cd_ = coat['V'], coat['T'], dense(coat['sj'], coat['sw'])
for L in loops(ct_):
    L = np.array(L); c = cv_[L].mean(0)
    if abs(c[0]) < 0.12: continue                     # the sleeves' ends only
    cv_, ct_, cd_ = rim(cv_, ct_, L, (c - cv_[L]) * 0.3, cd_)
sj, sw = top4(cd_)
coat = part(cv_, ct_, sj, sw, 'coat', name='coat')

# the skirt of the coat: rings on the drawing's sections from the belt to the hem; at the belt it takes the top's edge
NS, NR = 96, 44
edge = np.where((np.abs(coat['V'][:, 1] - BELT) < 1e-6))[0]
pe = np.arctan2(coat['V'][edge, 0], coat['V'][edge, 2] - ZB); re = np.hypot(coat['V'][edge, 0], coat['V'][edge, 2] - ZB)
o = np.argsort(pe); pe, re = pe[o], re[o]
ps = np.linspace(-np.pi, np.pi, NS, endpoint=False)
r_top = np.interp(ps, np.r_[pe - 2 * np.pi, pe, pe + 2 * np.pi], np.r_[re, re, re])
r_t0 = coat_r(np.full(NS, BELT), ps)
SF = []
ys = np.linspace(BELT + 0.006, HEM, NR)
RG = np.array([coat_r(np.full(NS, yy), ps) + (r_top - r_t0) * (1 - sstep(BELT - yy, 0, 0.12)) - 0.0015 * (yy > BELT) for yy in ys])
grid = lambda R: np.c_[(np.sin(ps)[None] * R).ravel(), np.repeat(ys, NS), ZB + (np.cos(ps)[None] * R).ravel()]
# … and stays clear of the body under it (the seat, the thighs): where it comes nearer than 9 mm it is let out, softly
for _ in range(4):
    d = igl.signed_distance(grid(RG), V, T)[0].reshape(NR, NS)
    add = np.clip(0.009 - d, 0, None)
    for _ in range(6): add = np.maximum(add, (np.roll(add, 1, 1) + np.roll(add, -1, 1) + add + np.r_[add[:1], add[:-1]] + np.r_[add[1:], add[-1:]]) / 5)
    RG = RG + add
SK = grid(RG)
for i in range(NR - 1):
    for j in range(NS):
        a_, b_ = i * NS + j, i * NS + (j + 1) % NS
        SF += [(a_, a_ + NS, b_), (b_, a_ + NS, b_ + NS)]
SF = np.array(SF)
# its skinning: above the legs' fork the body's own weights at the nearest place; below, each side goes with its leg
# (thigh, then partly shin under the knee) and keeps a share of the hips, so the cloth lags the step
_, fi, cp = igl.point_mesh_squared_distance(SK, V, T)
bc = igl.barycentric_coordinates(cp, V[T[fi, 0]], V[T[fi, 1]], V[T[fi, 2]])
Wb = sum(bc[:, k:k + 1] * D[T[fi, k]] for k in range(3))
fork = J[IX['LeftLeg'], 1] - 0.05; knee = J[IX['LeftShin'], 1]
Wl = np.zeros((len(SK), NJ))
sL = sstep(SK[:, 0], -0.035, 0.035)
shin = sstep(knee + 0.05 - SK[:, 1], 0, 0.16) * 0.55
hips = np.clip(1 - (fork - SK[:, 1]) / 0.22, 0.18, 1)
for nm, sd in (('Left', sL), ('Right', 1 - sL)):
    Wl[:, IX[nm + 'Leg']] = sd * (1 - hips) * (1 - shin); Wl[:, IX[nm + 'Shin']] = sd * (1 - hips) * shin
Wl[:, IX['Hips']] = hips
u = sstep(fork + 0.06 - SK[:, 1], 0, 0.12)[:, None]
Ws = Wb * (1 - u) + Wl * u
nbS = neighbours(SF, len(SK))
for _ in range(8): Ws = 0.5 * Ws + 0.5 * np.array([Ws[n].mean(0) for n in nbS])
hem_loop = np.arange((NR - 1) * NS, NR * NS)
SK2, SF2, Ws2 = rim(SK, SF, hem_loop, np.c_[-np.sin(ps), np.full(NS, 0.25), -np.cos(ps)] * 0.012, Ws)
sj, sw = top4(Ws2)
skirt = part(SK2, SF2, sj, sw, 'coat', name='skirt')
# the coat's front layer (lapels, the turtleneck's wedge, the belt, buttons, the seam) is painted by look.js from the
# drawing's own shapes: aux = (x, y in the drawing's units at rest, how much the rest surface faces front, 0)
for p in (coat, skirt):
    n = vnormals(p['V'], p['T'])
    p['aux'] = np.c_[p['V'][:, 0] / K, FLOOR - p['V'][:, 1] / K, np.clip(n[:, 2], 0, 1), np.zeros(len(p['V']))]
    parts.append(p)

# the turtleneck's collar: a soft tube round the neck (the drawing's layer 0: radius 12.5 units from y 70 to 92)
TN = PERSON['layers'][0]
nu_, nv_ = 12, 40; X = []; nzc = PERSON['neck'][1][2]
prof = [(96, 12.6), (88, 12.7), (80, 12.8), (74, 12.8), (71, 12.4), (69.4, 11.4), (69.2, 10.4), (70.5, 9.6), (74, 9.3), (80, 9.2)]
for yy, r in prof:
    for j in range(nv_):
        q = 2 * np.pi * j / nv_
        X.append([np.sin(q) * r * K, UY(yy), Z0 + (nzc + np.cos(q) * r) * K])
X = np.array(X); F = []
for i in range(len(prof) - 1):
    for j in range(nv_):
        a_, b_ = i * nv_ + j, i * nv_ + (j + 1) % nv_
        F += [(a_, b_, a_ + nv_), (b_, b_ + nv_, a_ + nv_)]
sj, sw = head_skin(X)
parts.append(part(X, np.array(F), sj, sw, 'turtle', name='turtle'))

# the trousers: the legs' surface a little out, narrow to the ankle (the drawn 15 → 11 → 9 units)
legs = pw('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot', 'pelvis')
tl = np.where(V[:, 0] > 0, bone_t(V, 'LeftShin', 'LeftFoot'), bone_t(V, 'RightShin', 'RightFoot'))
f_pants = np.maximum.reduce([y - (J[IX['Hips'], 1] + 0.03), 0.3 - legs, 0.03 - y])
off_p = 0.003 + 0.008 * np.clip(tl, 0, 1)
pants, _ = shell(f_pants, off_p, 'pants', smooth_it=6, name='pants')
parts.append(pants)


# the shoes: lofted along each foot, heel to toe — low black flats
def shoe(side):
    F_, T_ = J[IX[side + 'Foot']], J[IX[side + 'ToeEnd']]
    ax = np.array([T_[0] - F_[0], 0, T_[2] - F_[2]]); L = np.linalg.norm(ax); ax /= L
    heel = np.array([F_[0], 0, F_[2]]) - ax * 0.026; Ltot = L + 0.026 + 0.012
    side_v = np.cross([0, 1, 0], ax)
    nu, nv = 30, 28; X = []
    for i in range(nu):
        t = i / (nu - 1)
        c = heel + ax * Ltot * t
        w = 0.021 + 0.006 * np.sin(np.pi * min(t / 0.72, 1) / 2) - 0.008 * sstep(t, 0.75, 1.0)
        hgt = np.interp(t, [0, 0.3, 0.55, 0.85, 1], [0.046, 0.046, 0.034, 0.024, 0.018])
        cap = np.clip(np.sin(np.pi * t) ** 0.3, 0.05, 1)
        for j in range(nv):
            a = 2 * np.pi * j / nv
            sx, sy = np.cos(a), np.sin(a)
            r = (abs(sx) ** 2.6 + abs(sy) ** 2.6) ** (-1 / 2.6)
            px, py = sx * r * w * cap, (sy * r * 0.5 + 0.5) * hgt * (0.35 + 0.65 * cap)
            X.append(c + side_v * px + np.array([0, max(py, 0) - 0.002, 0]))
    X = np.array(X); Fc = []
    for i in range(nu - 1):
        for j in range(nv):
            a_, b_ = i * nv + j, i * nv + (j + 1) % nv
            Fc += [(a_, b_, a_ + nv), (b_, b_ + nv, a_ + nv)]
    for end, rev in ((0, True), (nu - 1, False)):
        ci = len(X); X = np.r_[X, X[end * nv:(end + 1) * nv].mean(0)[None]]
        for j in range(nv):
            tri = (end * nv + j, end * nv + (j + 1) % nv, ci)
            Fc.append(tri[::-1] if rev else tri)
    tt = ((X - heel) @ ax) / Ltot
    Dd = np.zeros((len(X), NJ)); wt = np.clip((tt - 0.55) / 0.2, 0, 1)
    Dd[:, IX[side + 'Foot']] = 1 - wt; Dd[:, IX[side + 'ToeBase']] = wt
    sj, sw = top4(Dd)
    return part(X, np.array(Fc), sj, sw, 'shoe', name='shoes')


for sd in ('Left', 'Right'): parts.append(shoe(sd))

# the skin left showing: the hands
f_skin = np.where(armside, (SLEEVE_END - 0.05) - sl, 1.0)
v, t, a, _ = cut(V, T, f_skin, D)
sj, sw = top4(a)
parts.append(part(v, t, sj, sw, 'skin', name='limbs'))

# ---------------- ambient occlusion, baked on the rest model ----------------
from model import join
M, _ = join(parts)
N = vnormals(M['V'], M['T'])
ao = igl.ambient_occlusion(M['V'], M['T'], M['V'] + N * 1e-4, N, 64)
# the stance of the stills: the drawing's joints; its arms hang inside its coat (elbow at x 43, the coat's side at 40, the
# sleeve 12 thick: in the drawing the sleeve is painted over the coat), so here elbow and wrist stand off by the sleeve
STANCE = {k: list(PERSON[k]) for k in ('sh', 'el', 'wr', 'hip', 'kn', 'an')}
STANCE['el'] = [55, 196, 2]; STANCE['wr'] = [57, 280, 12]
from pix import mix
# the drawing's colours; skin and coat a third of the way to their shadow colours (the look's key light is strong, as Р6's)
PAINT = dict(skin=mix(C['skin'], C['skin_sh'], 0.52), lip=C['lip'], mouth='#5a1f22', eye='#f2ede8', hair=mix(C['hair'].base, C['hair'].dark, 0.45),
             coat=mix('#7d8b97', '#4c5866', 0.72), turtle=mix('#93334a', '#5e1c2c', 0.2), pants='#2e2c33', frame='#2a1f1c', shoe='#1e1c20',
             sole='#0c0b0d', teeth='#f4eee2', streak='#8f8882', belt='#6c7985', tongue='#c4545a')
write(char.NAME, parts, J2, B['frames'], ao=ao, out_dirs=OUT,
      extra=dict(K=K, hs=HS, headY=HY, headZ=HZ, balls=BALLS.tolist(), mouthY=MY, lipZ=float(lipz), floor=FLOOR, paint=PAINT,
                 iris=dict(col=mix(C['iris_col'], '#8a8a86', 0.45), r=C['iris'] / char.EYE_R),
                 legs=dict(r=[0.056, 0.044, 0.036], soft=0.012), hair=dict(light=C['hair'].light, dark=C['hair'].dark),
                 skinShade=C['skin_sh'], lash=C['lash'], stance=STANCE, eye=dict(x=C['eye_x'], y=C['eye_y'], browH=C['brow_h'])))
np.savez(f'{CACHE}/head_rest.npz', X=HEAD_REST)
