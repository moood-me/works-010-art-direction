"""Тим (С1, Pixar) assembled: Anny's fitted child body, the fitted Human Base Meshes head with its eyes as balls under
real lids, the hair locks, the clothes cut from the body's own surface, the sneakers — every part skinned on SOMA's 77
joints — written as one model pack (model.py) with its look's attributes and baked ambient occlusion."""
import numpy as np
from common import CACHE, IX, NAMES, NJ, K, dense, top4, HERE
from fitbody import B, fit
from model import part, write, MATS
from meshcut import cut, loops, smooth, rim, neighbours
from sphere import sphere
from quads import Quads
from eyefit import ring, OUTER, LINING
import hair as HAIR

OUT = [f'{HERE}/web/data']


from build_util import vnormals, sstep


def one(n, joint): return np.tile([IX[joint], 0, 0, 0], (n, 1)), np.tile([1., 0, 0, 0], (n, 1))


# ---------------- the body ----------------
V, J = fit()
T = B['triangles']; PP = B['parts'] / 255.; PN = B['partnames']
pw = lambda *names: sum(PP[:, PN.index(n)] for n in names)
D = dense(B['sj'], B['sw'])
NB = vnormals(V, T)

# ---------------- the head (head units: y up, crown +50, chin −50; the drawing's head centre at person y 8) ----------
HY = 373.0
H2W = lambda X: np.c_[X[:, 0] * K, (HY + X[:, 1]) * K, X[:, 2] * K]
hf = np.load(f'{CACHE}/head_fit.npz')
HV = hf['final'].copy(); HT = hf['T']; MI = hf['mirror']; BALLS = hf['balls']; V0 = hf['base']
from hbm import load as hbm_load
HQ = hbm_load()['head'][2]
Q = Quads(HQ)


def neck(X):
    """below the jaw the base's neck becomes the drawing's thin round neck (radius 11.5 about x 0, z −9; a little wider
    at its foot), blended in under the jaw line"""
    y, z = X[:, 1], X[:, 2]
    yj = np.interp(z, [-25, -12, 10, 25], [-38, -44, -52, -54])          # the jaw line, higher at the nape
    w = sstep(yj - y, 0, 9)
    r = 11.5 + 1.5 * sstep(-y, 58, 75)
    zc = -9.0
    d = np.c_[X[:, 0], z - zc]; rr = np.linalg.norm(d, axis=1)
    tgt = d / np.maximum(rr, 1e-6)[:, None] * r[:, None]
    out = X.copy(); out[:, 0] = X[:, 0] * (1 - w) + tgt[:, 0] * w; out[:, 2] = z * (1 - w) + (zc + tgt[:, 1]) * w
    return out


HV = neck(HV)
HW = H2W(HV)
# the head's joints where the drawn head is (frames kept)
J2 = J.copy()
J2[IX['Head']] = H2W(np.array([[0, -40.0, -8]]))[0]
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
mouth_in |= (HV[:, 2] < lipz - 4) & (HV[:, 2] > 0) & (np.abs(HV[:, 0]) < 13) & (np.abs(HV[:, 1] + 36.5) < 8) & ~outer
# the eye sockets' lining (under the lids, behind the balls)
sock = np.zeros(len(HV), bool)
for s in LINING: L = ring(Q, V0, s); sock[L] = True; sock[MI[L]] = True
for bi in range(2):
    sock |= np.linalg.norm(HV - BALLS[bi, :3], axis=1) < BALLS[bi, 3] + 0.3
inner_lip = np.zeros(len(HV), bool)
for s_ in [770]: inner_lip[ring(Q, V0, s_)] = True
mouth_in[ring(Q, V0, 767)] = True
mat = np.where(inner_lip, MATS.index('lip'), np.where(mouth_in, MATS.index('mouth'), MATS.index('skin')))
aux = np.c_[uv, facing, lash]
# the jaw's share: the lower lip and everything below the mouth's line (found on the base, where the line ring's two
# halves part), fading under the chin into the neck and back toward the ears
L767 = ring(Q, V0, 767); y767 = V0[L767, 1].mean()
hm = 0.05 + 2.6 * sstep(np.abs(V0[:, 0]), 5.0, 9.8)
below = sstep(y767 - V0[:, 1], -hm, hm)
jaw = below * (1 - sstep(-HV[:, 1], 58, 72)) * sstep(HV[:, 2], -16, 4) * (1 - sstep(np.abs(HV[:, 0]), 30, 42))
# the lids: for each vertex of an upper (lower) lid, how far it turns about its ball's x axis to shut the eye (deg),
# and its weight — the margin's elevation over the ball comes down to a closing line low in the opening
lid = lid_data(HV, Q, V0, MI, BALLS)
lid_jaw = None
# the neck ends inside the shirt
A = np.c_[mat, aux, HV, lid, jaw]
hv, ht, a, _ = cut(HW, HT, -(HW[:, 1] - 0.82), A)
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
parts.append(teeth_row(-36.5 + 0.4, 6.6, 8, 4, 9.0, 39.2, 'teethUp'))
parts.append(teeth_row(-36.5 - 3.2, 3.6, 8, -1, 8.5, 38.2, 'teethLo')); parts[-1]['jaw'] = np.ones(len(parts[-1]['V']))

# ---------------- the hair ----------------
hv_, ht_, hpat = HAIR.build(HV, HT)
sj, sw = one(len(hv_), 'Head')
parts.append(part(H2W(hv_), ht_, sj, sw, 'hair', aux=hpat, name='hair'))

# ---------------- clothes from the body's surface ----------------
def bone_t(X, a, b):
    A_, Bb = J[IX[a]], J[IX[b]]; d = Bb - A_
    return ((X - A_) @ d) / (d @ d)


def shell(region_f, off, mat, smooth_it=3, name=''):
    """the body's surface where region_f < 0, pushed out along its normals by off (per vertex)"""
    A_ = np.c_[D, NB, off]
    v, t, a, on = cut(V, T, region_f, A_)
    d, n, o = a[:, :NJ], a[:, NJ:NJ + 3], a[:, -1]
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    v = v + n * o[:, None]
    v = smooth(v, t, it=smooth_it, lam=0.3, fixed=np.where(on)[0])
    sj, sw = top4(d)
    return part(v, t, sj, sw, mat, name=name)


y = V[:, 1]
# the shirt: hem at the drawn 206 (0.509 m), sleeves to 0.36 of the arm, a crew neck round the thin neck
hem = 0.50; coll = 0.872
sl = np.maximum(np.where(V[:, 0] > 0, bone_t(V, 'LeftArm', 'LeftForeArm'), bone_t(V, 'RightArm', 'RightForeArm')), -9)
armside = pw('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand') > 0.3
f_shirt = np.maximum.reduce([hem - y, y - coll, np.where(armside | ((np.abs(V[:, 0]) > 0.10) & (y > 0.72)), sl - 0.62, -1)])
off_s = 0.008 + 0.016 * sstep(0.64 - y, 0, 0.08) + 0.012 * sstep(0.60 - y, 0, 0.09) + 0.009 * np.clip(sl / 0.6, 0, 1) * armside
shirt = shell(f_shirt, off_s, 'shirt', smooth_it=30, name='shirt')
sv = shirt['V']; nz = -9 * K
rr = np.hypot(sv[:, 0], sv[:, 2] - nz)
sgy = sstep(sv[:, 1], 0.815, coll) ** 1.2
rt = 0.040
k = np.where(rr > rt, (rr + (rt - rr) * sgy) / rr, 1.0)
sv[:, 0] *= k; sv[:, 2] = nz + (sv[:, 2] - nz) * k
shirt['pat'] = sv.copy()
# the collar: a darker red band round the neckline (the drawing's shirt shade there)
cl = sv[:, 1] - (coll - 0.010)
A_ = np.c_[dense(shirt['sj'], shirt['sw']), shirt['pat']]
for sgn, m in ((1, 'shirt'), (-1, 'collar')):
    v, t, a, _ = cut(shirt['V'], shirt['T'], sgn * cl, A_)
    sj, sw = top4(a[:, :NJ]); parts.append(part(v, t, sj, sw, m, pat=a[:, NJ:], name='shirt'))
# the shorts: from the waist to 0.34 of the thigh, wide legs
tl = np.maximum(bone_t(V, 'LeftLeg', 'LeftShin') * (V[:, 0] > 0), bone_t(V, 'RightLeg', 'RightShin') * (V[:, 0] < 0))
f_shorts = np.maximum(y - 0.535, tl - 0.66)
off_p = 0.007 + 0.022 * np.clip(tl / 0.5, 0, 1) ** 1.0
parts.append(shell(f_shorts, off_p, 'shorts', smooth_it=10, name='shorts'))


# the sneakers: lofted along each foot, heel to toe — rounded sections on a flat sole (cream with a red sole band)
def sneaker(side):
    F_, T_ = J[IX[side + 'Foot']], J[IX[side + 'ToeEnd']]
    ax = np.array([T_[0] - F_[0], 0, T_[2] - F_[2]]); L = np.linalg.norm(ax); ax /= L
    heel = np.array([F_[0], 0, F_[2]]) - ax * 0.03; Ltot = L + 0.03 + 0.016
    side_v = np.cross([0, 1, 0], ax)
    nu, nv = 30, 28; X = []
    for i in range(nu):
        t = i / (nu - 1)
        c = heel + ax * Ltot * t
        w = 0.025 + 0.009 * np.sin(np.pi * min(t / 0.72, 1) / 2)
        hgt = np.interp(t, [0, 0.3, 0.55, 0.85, 1], [0.060, 0.062, 0.046, 0.036, 0.030])
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
    sh = part(X, np.array(Fc), sj, sw, 'shoe', name='shoes')
    A_ = np.c_[dense(sj, sw)]
    out = []
    for sgn, m in ((1, 'shoe'), (-1, 'sole')):
        v, t, a, _ = cut(X, np.array(Fc), sgn * (0.012 - X[:, 1]), A_)
        s2, w2 = top4(a); out.append(part(v, t, s2, w2, m, name='shoes'))
    return out


for sd in ('Left', 'Right'): parts += sneaker(sd)

# the skin left showing: arms below the sleeves, hands, legs below the shorts (white socks above the shoes)
f_skin = np.minimum.reduce([np.where(armside, 0.5 - sl, 1.0), np.where(pw('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot') > 0.3, 0.55 - tl, 1.0)])
f_skin = np.where(y < 0.054, 1.0, f_skin)
v, t, a, _ = cut(V, T, f_skin, D)
sj, sw = top4(a)
sk = part(v, t, sj, sw, 'skin', name='limbs')
sock_top = 34 * K
A_ = np.c_[a]
for sgn, m in ((1, 'skin'), (-1, 'sock')):
    v2, t2, a2, _ = cut(v, t, sgn * (sock_top - v[:, 1]), A_)
    s2, w2 = top4(a2); parts.append(part(v2, t2, s2, w2, m, name='limbs'))

# ---------------- ambient occlusion, baked on the rest model ----------------
from model import join
M, _ = join(parts)
import igl
N = vnormals(M['V'], M['T'])
ao = igl.ambient_occlusion(M['V'], M['T'], M['V'] + N * 1e-4, N, 64)
# eyes: occlusion only from the lids (their own sphere hides itself)
write('tim', parts, J2, B['frames'], ao=ao, out_dirs=OUT,
      extra=dict(K=K, headY=HY, balls=BALLS.tolist(), mouthY=-36.5, lipZ=float(lipz), stripes=[[128, 140], [146, 152]], floor=388.0))
np.savez(f'{CACHE}/head_rest.npz', X=HEAD_REST)
