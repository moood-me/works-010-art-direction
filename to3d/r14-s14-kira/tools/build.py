"""Кира assembled as a figure of paper pieces: Anny's fitted girl body (only the hands show), the fitted base head with
a folded paper nose, the hair in three sheets, the hoodie with its pocket, hood, strings, the headphones, trousers and
boots — every piece a shell with a cut edge, skinned on SOMA's 77 joints — then the slouch is put into the rest
(joints and surface turned together, frames kept: Kimodo's motions carry it), and one model pack is written (model.py).
   python build.py [steps]     (steps: also the packs of the steps along the way, for the page)"""
import sys
import numpy as np
from scipy.spatial import cKDTree
from common import CACHE, HERE, IX, NAMES, PARENT, NJ, vertex_normals, dense, top4
from fitbody import B, fit
from model import part, write, join, MATS
from meshcut import cut, loops, smooth, neighbours
from hbm import tris
from drawing import K, U, ZOFF, CHIN, FRINGE_F, SIDE_F, HAIR_S, curve, sdf
import os

STEPS = 'steps' in sys.argv
DATA = os.path.join(os.path.dirname(HERE), 'data')


# ---------------- helpers ----------------
def one(n, joint): return np.tile([IX[joint], 0, 0, 0], (n, 1)), np.tile([1., 0, 0, 0], (n, 1))


def rays(V, T, O, D):
    """the first hit of each ray O[i] + t·D[i] on the mesh: t (inf where none)"""
    A, e1, e2 = V[T[:, 0]], V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]
    out = np.full(len(O), np.inf)
    for i, (o, d) in enumerate(zip(O, D)):
        p = np.cross(d, e2); det = (e1 * p).sum(1); ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
        s = o - A; u = (s * p).sum(1) * inv; qv = np.cross(s, e1); v = (qv @ d) * inv; t = (e2 * qv).sum(1) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
        if hit.any(): out[i] = t[hit].min()
    return out


def outward(V, T):
    """triangles turned so that the piece's faces look away from its middle"""
    c = V.mean(0); tc = V[T].mean(1); n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    return T if ((tc - c) * n).sum() > 0 else T[:, ::-1]


def thick(p, th, N=None):
    """the sheet's thickness: along every open edge a band turned in by th, marked as the cut edge (lighter core).
    The band has its own vertices, so the edge stays crisp."""
    V, T = p['V'], p['T']
    if N is None: N = vertex_normals(V, T)
    add = {k: [] for k in ('V', 'sj', 'sw', 'mat', 'fuv', 'pat', 'edge')}; Tn = []; n = len(V)
    for L in loops(T):
        if len(L) < 3: continue
        L = np.array(L); m = len(L)
        for k, x in (('V', V[L]), ('V', V[L] - N[L] * th), ('pat', p['pat'][L]), ('pat', p['pat'][L] - N[L] * th)): add[k].append(x)
        for k in ('sj', 'sw', 'mat', 'fuv'): add[k] += [p[k][L], p[k][L]]
        add['edge'] += [np.ones(m), np.ones(m)]
        a = np.arange(n, n + m); b = np.roll(a, -1); c = a + m; d = b + m
        Tn += [np.stack([b, a, c], 1), np.stack([b, c, d], 1)]; n += 2 * m
    if not Tn: return p
    q = dict(p)
    for k in add: q[k] = np.concatenate([p[k]] + add[k])
    q['T'] = np.concatenate([T] + Tn)
    return q


def split(p, g, mat2):
    """a part cut in two along g = 0: where g < 0 it keeps its paper, elsewhere it takes mat2 — a clean line"""
    A = np.c_[dense(p['sj'], p['sw']), p['fuv'], p['pat'], p['mat'], p['edge']]
    out = []
    for sgn, m in ((1, None), (-1, mat2)):
        v, t, a, _ = cut(p['V'], p['T'], sgn * g, A)
        if len(t) == 0: continue
        sj, sw = top4(a[:, :NJ])
        mm = np.rint(a[:, NJ + 6]).astype(int) if m is None else np.full(len(v), MATS.index(m))
        out.append(dict(V=v, T=t, sj=sj, sw=sw, mat=mm, fuv=a[:, NJ:NJ + 3], pat=a[:, NJ + 3:NJ + 6], edge=a[:, NJ + 7]))
    return out


def loft(sections, closed_ends=True):
    """rings of the same count joined into a tube; ends closed by fans"""
    nu, nv = len(sections), len(sections[0]); X = np.concatenate(sections); F = []
    for i in range(nu - 1):
        for j in range(nv):
            a, b = i * nv + j, i * nv + (j + 1) % nv
            F += [(a, b, a + nv), (b, b + nv, a + nv)]
    if closed_ends:
        for end in (0, nu - 1):
            ci = len(X); X = np.r_[X, X[end * nv:(end + 1) * nv].mean(0)[None]]
            for j in range(nv):
                tri = (end * nv + j, end * nv + (j + 1) % nv, ci); F.append(tri[::-1] if end == 0 else tri)
    return X, outward(X, np.array(F))


def facets(P, F, inner):
    """flat pieces folded along their shared edges: every face gets its own vertices (a crisp fold); inner — a point
    the faces look away from"""
    out = []
    for f in F:
        a, b, c = (np.asarray(P[i], float) for i in f)
        if np.cross(b - a, c - a) @ ((a + b + c) / 3 - inner) < 0: b, c = c, b
        out += [a, b, c]
    return np.array(out), np.arange(len(out)).reshape(-1, 3)


# ---------------- the body ----------------
V, J = fit()
T = B['triangles']; P = B['parts'] / 255.; PN = B['partnames']
pw = lambda *names: sum(P[:, PN.index(n)] for n in names)
D = dense(B['sj'], B['sw'])
NB = vertex_normals(V, T)
y = V[:, 1]
body_tree = cKDTree(V)
def near_weights(X, k=6):
    d, i = body_tree.query(X, k=k); w = 1 / (d + 1e-4) ** 2; w /= w.sum(1, keepdims=True)
    return (D[i] * w[..., None]).sum(1)

# where the head sits (upright, before the slouch): the drawing's head centre O
CHIN_Y = 1.196
O = np.array([0.0, CHIN_Y + CHIN * K, 0.012])
toW = lambda X: X + O
J2 = J.copy()
J2[IX['Head']] = O + [0, -(CHIN - 32) * K, -5 * K]
J2[IX['HeadEnd']] = O + [0, 112 * K, -5 * K]
J2[IX['Jaw']] = O + [0, -55 * K, 35 * K]
J2[IX['LeftEye']] = O + [31 * K, -12 * K, 55 * K]; J2[IX['RightEye']] = O + [-31 * K, -12 * K, 55 * K]
J2[IX['Neck2']] = (J2[IX['Neck1']] + J2[IX['Head']]) / 2

# ---------------- the head ----------------
hs = np.load(f'{CACHE}/head_steps.npz')
HV, HQ = hs['warped'].copy(), hs['Q']; HT = tris(HQ)
FB = hs['faired']
ew = np.clip((np.abs(FB[:, 0]) - 0.104) / 0.01, 0, 1) * ((FB[:, 1] > 0.66) & (FB[:, 1] < 0.80) & (FB[:, 2] > -0.045) & (FB[:, 2] < 0.035))
NECK_END = 1.165
HV, HT, EW, _ = cut(HV, HT, -(HV[:, 1] - (NECK_END - O[1])), ew[:, None]); EW = EW[:, 0]
yd, zd = -HV[:, 1] / K, HV[:, 2] / K
cm = ((yd > -70) & (yd < 112) & (zd > -25) & (EW < 0.01)).astype(float)
HV = smooth(HV, HT, it=25, lam=0.5, mask=cm)
HV = smooth(HV, HT, it=70, lam=0.5, mask=((yd > 20) & (yd < 104) & (zd > 5)).astype(float))
# the base's ears are smoothed into the skull: Кира's ears are two ovals of paper (below)
em = (EW > 0).astype(float); nbh = neighbours(HT, len(HV))
for _ in range(3): em = np.array([max(em[i], em[nbh[i]].max()) if len(nbh[i]) else em[i] for i in range(len(HV))])
HV = smooth(HV, HT, it=220, lam=0.6, mask=em)
EW = EW * 0
# the face is the egg of the front view; what lies outside it below the cheeks is the neck piece: drawn in under the
# jaw toward a thin neck, so the jaw's edge and the pointed chin stand over it
from drawing import FRONT
def neck_g(X):
    x, yv, z = X[:, 0] / K, -X[:, 1] / K, X[:, 2] / K
    gz = yv - np.interp(z, [-70, -49, -16, 1, 29, 80], [43, 43, 56, 93, 108, 112])
    gf = np.where((yv > 46) & (z > -16), sdf(curve(FRONT), np.c_[x, yv]), -99)
    return np.maximum(gz, gf)
g_ = neck_g(HV); tn = np.clip(g_ / 16, 0, 1) * 0.9
ang_ = np.arctan2(HV[:, 0], HV[:, 2] + 10 * K)
HV[:, 0] = HV[:, 0] * (1 - tn) + tn * 15 * K * np.sin(ang_)
HV[:, 2] = HV[:, 2] * (1 - tn) + tn * (-10 * K + 15 * K * np.cos(ang_))
HV = smooth(HV, HT, it=8, lam=0.5, mask=(g_ > 3).astype(float))
HN = vertex_normals(HV, HT)


def head_skin(W):
    yy = W[:, 1]; yH, y2, y1 = J2[IX['Head'], 1], J2[IX['Neck2'], 1], J2[IX['Neck1'], 1]
    Dh = np.zeros((len(W), NJ))
    a = np.clip((yy - y2) / (yH - y2), 0, 1); b = np.clip((yy - y1) / (y2 - y1), 0, 1)
    Dh[:, IX['Head']] = a; Dh[:, IX['Neck2']] = (1 - a) * b; Dh[:, IX['Neck1']] = (1 - a) * (1 - b)
    return top4(Dh)


def fuv_of(X, N):
    u = (X[:, 0] / K + 128) / 256; v = (-X[:, 1] / K + 128) / 256
    return np.c_[u, v, np.clip(N[:, 2], 0, 1) * (X[:, 2] > 0)]


parts = []; step = {}
sj, sw = head_skin(toW(HV))
head = part(toW(HV), HT, sj, sw, 'skin', fuv=fuv_of(HV, HN))
# the neck is a darker piece under the jaw line (face.py: neck), the ears their own paper
hp = split(head, g_, 'skin_d')
# the ears (face.py: ear): an oval of card standing out from the head's side, a darker oval glued in it
def oval(c, au, av, ru, rv, n=28):
    X = np.r_[[c], [c + au * ru * np.cos(q) + av * rv * np.sin(q) for q in np.linspace(0, 2 * np.pi, n, endpoint=False)]]
    F = np.array([(0, 1 + i, 1 + (i + 1) % n) for i in range(n)])
    return X, F
for s_ in (1, -1):
    o = np.array([s_ * 0.72, 0.0, -0.69]); nf = np.array([s_ * 0.69, 0.0, 0.72]); up = np.array([s_ * 0.12, 1.0, 0.0]); up -= nf * (up @ nf); up /= np.linalg.norm(up)
    au = np.cross(up, nf) * s_; au = au if au @ o > 0 else -au
    root = np.array([s_ * 64.0, -22.0, 4.0])
    for mat_, ru, rv, dz, sh in (('ear', 10.0, 15.5, 0.0, 5.0), ('skin_d', 4.0, 10.0, 0.7, 6.5)):
        Xe, Fe = oval((root + o * sh + nf * dz) * K, au, up, ru * K, rv * K)
        if np.cross(Xe[Fe[0, 1]] - Xe[Fe[0, 0]], Xe[Fe[0, 2]] - Xe[Fe[0, 0]]) @ nf < 0: Fe = Fe[:, ::-1]
        sj, sw = one(len(Xe), 'Head')
        q = part(toW(Xe), Fe, sj, sw, mat_)
        hp.append(thick(q, 1.2 * K) if mat_ == 'ear' else q)
parts += hp
step['head'] = list(hp)

# the nose: a piece of paper folded down its ridge, standing on the face (face.py: wedge; its profile from the side
# view) — two flat sides and the underside, each lit as a flat piece
def face_z(x, yv):
    t = rays(HV, HT, np.array([[x * K, -yv * K, 0.5]]), np.array([[0, 0, -1.0]]))[0]
    return (0.5 - t) / K
ap, tip = np.array([0.6, 12, face_z(0.6, 12) + 0.6]), np.array([1.2, 42.5, 78.0])
bl, br = np.array([-7.6, 45.5, face_z(-7.6, 45.5) + 0.8]), np.array([8.4, 44.0, face_z(8.4, 44) + 0.8])
bm = np.array([0.6, 49.5, face_z(0.6, 49.5) + 0.3])
hu = lambda p: np.array([p[0] * K, -p[1] * K, p[2] * K])
NXh, NT = facets([hu(p) for p in (ap, bl, tip, br, bm)], [(0, 1, 2), (0, 2, 3), (1, 4, 2), (4, 3, 2)], hu((0.5, 38, 55)))
sj, sw = one(len(NXh), 'Head')
nose = part(toW(NXh), NT, sj, sw, 'nose')
parts.append(nose); step['head'].append(nose)

# ---------------- the hair: three sheets of painted paper ----------------
# the profile's piece, its lower teeth taken lower over the temple and the ear than the profile draws them: the
# front view's fringe hangs to the cheek at the head's side, and the two views can't both be true — the front wins
HAIR_S3 = HAIR_S[:7] + [(-86, 68, 1), (-76, 44, 1), (-64, 64, 1), (-52, 40, 1), (-38, 58, 1), (-26, 30, 1), (-10, 44, 1), (2, 14, 1), (16, 30, 1),
                        (28, -4, 1), (42, 6, 1), (54, -22, 1)]
FR, SDp, HS = curve(FRINGE_F), curve(SIDE_F), curve(HAIR_S3)
def hair_fields(X):
    x = X[:, 0] / K; yv = -X[:, 1] / K; z = X[:, 2] / K
    th = np.degrees(np.arctan2(np.abs(x), z))
    f_fr = sdf(FR, np.c_[x, yv]); f_sd = sdf(SDp, np.c_[x, yv])
    f_front = np.minimum(f_fr, f_sd)
    f_side = sdf(HS, np.c_[z - ZOFF, yv])
    # at the nape the profile's teeth go on round the head
    f_back = yv - (50 + 13 * np.abs(((np.degrees(np.arctan2(x, -z)) / 24) % 2) - 1))
    wf = np.clip((72 - th) / 26, 0, 1); wb = np.clip((th - 118) / 24, 0, 1)
    f_all = wf * f_front + (1 - wf) * ((1 - wb) * f_side + wb * f_back)
    return f_all, f_fr, f_sd, th, z

def bell(v, v0):
    """below the head's widest the hair doesn't follow the skull in to the neck: at the sides and the back it hangs
    straight down, as a cut sheet does (v0: the same points on the head, for their height)"""
    zc = -8 * K
    ang = np.arctan2(v[:, 0], v[:, 2] - zc); r = np.hypot(v[:, 0], v[:, 2] - zc); yv = -v0[:, 1] / K
    band = (yv > -18) & (yv < 4); bins = np.linspace(-np.pi, np.pi, 49); R0 = np.zeros(48)
    for i in range(48):
        m = band & (ang >= bins[i]) & (ang < bins[i + 1]); R0[i] = r[m].max() if m.any() else 0
    R0 = np.where(R0 > 0, R0, R0[R0 > 0].mean()); R0 = (np.roll(R0, 1) + 2 * R0 + np.roll(R0, -1)) / 4
    rk = np.interp(ang, np.r_[bins[0] - np.pi / 48, (bins[:-1] + bins[1:]) / 2, bins[-1] + np.pi / 48], np.r_[R0[-1], R0, R0[0]])
    wa = np.clip((np.abs(np.degrees(ang)) - 52) / 24, 0, 1); wy = np.clip(yv / 24, 0, 1)
    rn = np.maximum(r, rk * (1 - 0.05 * wy)) * wa * (yv > 0) + r * (1 - wa * (yv > 0))
    k = rn / np.maximum(r, 1e-9)
    return np.c_[v[:, 0] * k, v[:, 1], zc + (v[:, 2] - zc) * k]


def sheet(f, off, mat, th=1.3 * K, it=3):
    """the head's surface where f < 0, lifted off it by off (per vertex, metres), as a sheet with a cut edge"""
    A = np.c_[HN, off]
    v, t, a, on = cut(HV, HT, f, A)
    n = a[:, :3] / np.linalg.norm(a[:, :3], axis=1, keepdims=True)
    v0 = v
    v = v + n * a[:, 3:4]
    v = bell(v, v0)
    v = smooth(v, t, it=it, lam=0.4)
    sj, sw = one(len(v), 'Head')
    return thick(part(toW(v), t, sj, sw, mat), th)

f_all, f_fr, f_sd, th_, z_ = hair_fields(HV)
ear_out = (EW - 0.05) * 40
yv_ = -HV[:, 1] / K
# the back piece: all the hair, low on the head
back = sheet(f_all, (4.0 + 5.0 * np.clip((yv_ + 105) / 60, 0, 1)) * K, 'hair_d')
# the side lock on her left temple: lies on the skin
side = sheet(np.maximum.reduce([f_sd, -(z_ + 6), -HV[:, 0] / K]), (6.0 + 5.5 * np.clip((yv_ + 105) / 60, 0, 1)) * K, 'hair')
# the fringe: glued at the crown, standing off the forehead more and more toward its points
lift = (6.0 + 7.5 * np.clip((yv_ + 105) / 70, 0, 1)) * K
wf_ = np.clip((72 - th_) / 26, 0, 1)
f_fringe = np.where(HV[:, 0] < 0, wf_ * f_fr + (1 - wf_) * f_all, f_fr + (1 - wf_) * 30)
fringe = sheet(np.maximum.reduce([f_fringe, -(z_ + 48)]), lift, 'hair')
hair = [back, side, fringe]
parts += hair; step['hair'] = hair

# ---------------- the hoodie ----------------
HEM, BAND, CUT, COLL = 0.640, 0.688, 0.735, 1.205
ZC = 0.022
def bone_t(X, a, b):
    A, Bb = J[IX[a]], J[IX[b]]; d = Bb - A
    return ((X - A) @ d) / (d @ d)
def bone_r(X, a, b):
    """foot of X on the bone a→b (clamped) and the direction from it"""
    A, Bb = J[IX[a]], J[IX[b]]; d = Bb - A; t = np.clip(((X - A) @ d) / (d @ d), 0, 1)
    F = A + t[:, None] * d; r = X - F
    return F, r / np.maximum(np.linalg.norm(r, axis=1, keepdims=True), 1e-9), t

ta = np.where(V[:, 0] > 0, bone_t(V, 'LeftArm', 'LeftForeArm'), bone_t(V, 'RightArm', 'RightForeArm'))
tf = np.where(V[:, 0] > 0, bone_t(V, 'LeftForeArm', 'LeftHand'), bone_t(V, 'RightForeArm', 'RightHand'))
armw = np.clip(pw('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand'), 0, 1)
handw = pw('Lhand', 'Rhand')
legw = pw('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot')
WR = 0.96           # the sleeve's cut on the forearm; it is lengthened over the hand below
f_hood = np.maximum.reduce([CUT - y, y - COLL, np.where(armw > 0.5, tf - WR, -1.0), handw - 0.5, legw - 0.6, pw('head') - 0.3])

# the shape it takes: round the trunk an oval tube widening to the hem, round the arms wide sleeves
YS = [CUT, 0.95, 1.08, 1.150, 1.185, COLL]
AW = [0.178, 0.180, 0.172, 0.146, 0.100, 0.066]
CD = [0.132, 0.138, 0.130, 0.108, 0.084, 0.068]
def trunk_target(X):
    a = np.interp(X[:, 1], YS, AW); c = np.interp(X[:, 1], YS, CD)
    ang = np.arctan2(X[:, 0], X[:, 2] - ZC)
    r = 1 / np.sqrt((np.sin(ang) / a) ** 2 + (np.cos(ang) / c) ** 2)
    return np.c_[r * np.sin(ang), X[:, 1], ZC + r * np.cos(ang)]
def arm_target(X):
    out = np.zeros_like(X)
    for s, sd in ((1, 'Left'), (-1, 'Right')):
        m = (X[:, 0] * s) > 0
        Fu, du, tu = bone_r(X[m], sd + 'Arm', sd + 'ForeArm'); Ff, df, tfo = bone_r(X[m], sd + 'ForeArm', sd + 'Hand')
        lower = (tu >= 1)
        F = np.where(lower[:, None], Ff, Fu); d = np.where(lower[:, None], df, du)
        r = np.where(lower, np.interp(tfo, [0, 1], [0.046, 0.040]), np.interp(tu, [0, 1], [0.054, 0.046]))
        out[m] = F + d * r[:, None]
    return out
aw_s = np.clip((armw - 0.25) / 0.5, 0, 1)
Vh = (1 - aw_s[:, None]) * trunk_target(V) + aw_s[:, None] * arm_target(V)
hv, ht, ha, on = cut(Vh, T, f_hood, D)
hv = smooth(hv, ht, it=12, lam=0.5, fixed=np.where(on)[0])
hD = ha

def extend(v, t, Dw, ring_of, n, Dnew=None):
    """the open edge(s) chosen by ring_of(loop) → (positions n×m×3) drawn on by n more rings (a hem, a cuff)"""
    for L in loops(t):
        R = ring_of(np.array(L), v)
        if R is None: continue
        L = np.array(L); m = len(L); prev = L
        for k in range(n):
            idx = np.arange(len(v), len(v) + m)
            v = np.r_[v, R[k]]; Dw = np.r_[Dw, Dw[L] if Dnew is None else Dnew(Dw[L], R[k], (k + 1) / n)]
            a, b = prev, np.roll(prev, -1); c, d = idx, np.roll(idx, -1)
            t = np.r_[t, np.stack([b, a, c], 1), np.stack([b, c, d], 1)]; prev = idx
    return v, t, Dw

# the hem: from the cut round the hips down to the hoodie's hem, a little wider
def hem_rings(L, v):
    if abs(v[L, 1].mean() - CUT) > 0.01: return None
    out = []
    for k in range(1, 7):
        yy = CUT + (HEM - CUT) * k / 6; s = 1 + 0.035 * k / 6
        out.append(np.c_[v[L, 0] * s, np.full(len(L), yy), ZC + (v[L, 2] - ZC) * s])
    return out
def hem_w(Dl, X, u):
    # a share of the thighs toward the hem, so that a striding leg carries it
    Dn = Dl * (1 - 0.3 * u); sx = np.clip(X[:, 0] / 0.05, -1, 1)
    Dn[:, IX['LeftLeg']] += 0.3 * u * (0.5 + 0.5 * sx); Dn[:, IX['RightLeg']] += 0.3 * u * (0.5 - 0.5 * sx)
    return Dn
hv, ht, hD = extend(hv, ht, hD, hem_rings, 6, hem_w)

# the sleeves: too long — drawn on over the hand, carried by the hand
def cuff_rings(L, v):
    c = v[L].mean(0)
    if c[1] > 1.05 or abs(c[0]) < 0.2: return None
    sd = 'Left' if c[0] > 0 else 'Right'
    A, Bb = J[IX[sd + 'ForeArm']], J[IX[sd + 'Hand']]; d = (Bb - A) / np.linalg.norm(Bb - A)
    return [v[L] + d * (0.052 * k / 4) + (c + d * 0 - v[L]) * 0.02 * k for k in range(1, 5)]
def cuff_w(Dl, X, u):
    Dn = Dl * (1 - 0.45 * u); sd = np.where(X[:, 0] > 0, IX['LeftHand'], IX['RightHand'])
    Dn[np.arange(len(X)), sd] += 0.45 * u
    return Dn
hv, ht, hD = extend(hv, ht, hD, cuff_rings, 4, cuff_w)
sj, sw = top4(hD)
hood_body = part(hv, ht, sj, sw, 'hood')
hood_tree = cKDTree(hv)
def hood_weights(X, k=4):
    d, i = hood_tree.query(X, k=k); w = 1 / (d + 1e-4) ** 2; w /= w.sum(1, keepdims=True)
    return top4((hD[i] * w[..., None]).sum(1))
hoodie = []
hb = split(hood_body, BAND - hood_body['V'][:, 1], 'band')       # the darker band along the hem
hoodie += [thick(q, 0.0035) for q in hb]

def on_front(xs, ys, off):
    """points of the hoodie's front under (x, y), lifted off it"""
    Oo = np.c_[xs, ys, np.full(len(xs), 0.6)]; t = rays(hv, ht, Oo, np.tile([0, 0, -1.0], (len(xs), 1)))
    return np.c_[xs, ys, 0.6 - t + off]

def patch(corners, nu, nv, off, mat, th=0.003):
    """a flat piece glued on the hoodie's front: corners (tl, tr, br, bl) as (x, y)"""
    tl, tr, br, bl = [np.array(c, float) for c in corners]
    uu, vv = np.meshgrid(np.linspace(0, 1, nu), np.linspace(0, 1, nv))
    Pq = (tl[None, None] * (1 - uu[..., None]) + tr[None, None] * uu[..., None]) * (1 - vv[..., None]) + (bl[None, None] * (1 - uu[..., None]) + br[None, None] * uu[..., None]) * vv[..., None]
    Pq = Pq.reshape(-1, 2); X = on_front(Pq[:, 0], Pq[:, 1], off)
    F = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            a = j * nu + i; F += [(a, a + nu, a + 1), (a + 1, a + nu, a + nu + 1)]
    F = np.array(F); n = np.cross(X[F[0, 1]] - X[F[0, 0]], X[F[0, 2]] - X[F[0, 0]])
    if n[2] < 0: F = F[:, ::-1]
    sj, sw = hood_weights(X)
    return thick(part(X, F, sj, sw, mat), th)

pocket = patch([(-0.100, 0.878), (0.100, 0.878), (0.134, 0.712), (-0.134, 0.712)], 15, 11, 0.004, 'pocket')
strings = [patch([(-0.031, 1.168), (-0.021, 1.168), (-0.026, 1.000), (-0.036, 1.000)], 2, 12, 0.003, 'string', 0.0015),
           patch([(0.021, 1.168), (0.031, 1.168), (0.037, 1.040), (0.027, 1.040)], 2, 10, 0.003, 'string', 0.0015)]

# the hood heaped behind the neck: a folded lump lying on the shoulders and the back
NC = np.array([0.0, 1.19, 0.0])
secs = []
for a in np.radians(np.linspace(-112, 112, 23)):
    k = np.cos(a / np.radians(112) * np.pi / 2) ** 0.5       # 1 at the back's middle, 0 at the ends
    c = NC + [np.sin(a) * 0.082, -0.020 - 0.022 * k, -np.cos(a) * (0.070 + 0.022 * k)]
    rad = np.array([np.sin(a), 0, -np.cos(a)]); up = np.array([0, 1.0, 0])
    w, h = 0.012 + 0.030 * k, 0.014 + 0.040 * k
    secs.append(np.array([c + rad * w * np.cos(q) + up * h * np.sin(q) * (1.0 if np.sin(q) > 0 else 0.55) for q in np.linspace(0, 2 * np.pi, 14, endpoint=False)]))
X, F = loft(secs)
sj, sw = hood_weights(X)
hood_piece = part(X, F, sj, sw, 'hood_d')
hoodie += [pocket] + strings + [hood_piece]
parts += hoodie; step['hoodie'] = hoodie

# ---------------- the headphones round the neck ----------------
def box(c, ax, ay, az, sx, sy, sz, p=4.0, n=10):
    """a pad: a rounded rectangle (2sx × 2sy along ax, ay) with thickness 2sz along az"""
    q = np.linspace(0, 2 * np.pi, 4 * n, endpoint=False); cx, cy = np.cos(q), np.sin(q)
    k = (np.abs(cx) ** p + np.abs(cy) ** p) ** (-1 / p)
    ring = ax[None] * (cx * k * sx)[:, None] + ay[None] * (cy * k * sy)[:, None]
    return loft([c + ring * 0.94 - az * sz, c + ring - az * sz * 0.8, c + ring + az * sz * 0.8, c + ring * 0.94 + az * sz])


phones = []
for s in (1, -1):
    c = on_front(np.array([s * 0.056]), np.array([1.172]), 0.007)[0]
    az = np.array([s * 0.42, 0.10, 0.90]); az /= np.linalg.norm(az)
    ay = np.array([0, 1.0, 0]) - az * az[1]; ay /= np.linalg.norm(ay); ax = np.cross(ay, az)
    X, F = box(c, ax, ay, az, 0.026, 0.035, 0.011)
    sj, sw = one(len(X), 'Chest')
    phones.append(part(X, F, sj, sw, 'lime'))
    X, F = box(c + az * 0.0115, ax, ay, az, 0.013, 0.020, 0.0012, p=2.0)
    sj, sw = one(len(X), 'Chest')
    phones.append(part(X, F, sj, sw, 'cup'))
secs = []
for a in np.radians(np.linspace(-128, 128, 25)):
    c = NC + [np.sin(a) * 0.060, 0.012 + 0.010 * (1 - abs(a) / np.radians(128)), -np.cos(a) * 0.056 + 0.004]
    rad = np.array([np.sin(a), 0, -np.cos(a)]); up = np.array([0, 1.0, 0])
    secs.append(np.array([c + rad * 0.0035 * np.cos(q) + up * 0.011 * np.sin(q) for q in np.linspace(0, 2 * np.pi, 8, endpoint=False)]))
X, F = loft(secs)
sj, sw = one(len(X), 'Chest')
phones.append(part(X, F, sj, sw, 'lime_d'))
parts += phones; step['phones'] = phones

# ---------------- trousers, boots, hands ----------------
def shell(region_f, off, mat, smooth_it=3):
    A = np.c_[D, NB, off]
    v, t, a, on = cut(V, T, region_f, A)
    d, n, o = a[:, :NJ], a[:, NJ:NJ + 3], a[:, -1]
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    v = smooth(v + n * o[:, None], t, it=smooth_it, lam=0.3, fixed=np.where(on)[0])
    sj, sw = top4(d)
    return part(v, t, sj, sw, mat)

BOOT_TOP = 0.118
f_tr = np.maximum.reduce([y - 0.75, (BOOT_TOP - 0.03) - y, armw - 0.3])
trousers = [shell(f_tr, np.full(len(V), 0.004), 'trou', smooth_it=6)]

def boot(side):
    F_, T_ = J[IX[side + 'Foot']], J[IX[side + 'ToeEnd']]
    ax = np.array([T_[0] - F_[0], 0, T_[2] - F_[2]]); L = np.linalg.norm(ax); ax /= L
    heel = np.array([F_[0], 0, F_[2]]) - ax * 0.050; Ltot = 0.185
    side_v = np.cross([0, 1, 0], ax)
    nu, nv = 34, 28; secs = []
    for i in range(nu):
        t = i / (nu - 1)
        c = heel + ax * Ltot * t
        w = 0.035 + 0.006 * np.sin(np.pi * min(t / 0.75, 1) / 2)
        hgt = np.interp(t, [0, 0.06, 0.40, 0.50, 0.62, 0.9, 1], [BOOT_TOP * 0.97, BOOT_TOP, BOOT_TOP, 0.082, 0.066, 0.058, 0.046])
        cap = np.clip(np.sin(np.pi * t) ** 0.22, 0.05, 1)
        ring = []
        for j in range(nv):
            a = 2 * np.pi * j / nv; sx, sy = np.cos(a), np.sin(a)
            r = (abs(sx) ** 3.4 + abs(sy) ** 3.4) ** (-1 / 3.4)
            py = (sy * r * 0.5 + 0.5) * hgt * (0.45 + 0.55 * cap)
            tread = 1.10 if py < 0.024 else 1.0                       # the thick sole stands out
            ring.append(c + side_v * (sx * r * w * cap * tread) + ax * ((cap - 1) * 0.0) + np.array([0, max(py, 0) - 0.001, 0]))
        secs.append(np.array(ring))
    X, F = loft(secs)
    tt = ((X - heel) @ ax) / Ltot
    Dd = np.zeros((len(X), NJ)); wt = np.clip((tt - 0.6) / 0.2, 0, 1)
    Dd[:, IX[side + 'Foot']] = 1 - wt; Dd[:, IX[side + 'ToeBase']] = wt
    sj, sw = top4(Dd)
    out = split(part(X, F, sj, sw, 'boot'), 0.024 - X[:, 1], 'sole')
    # the laces: three lime strips across the instep
    for k in range(3):
        tk = 0.44 + 0.055 * k
        ls = np.linspace(-0.021, 0.021, 7)
        Oo = heel[None] + ax[None] * Ltot * tk + side_v[None] * ls[:, None] + [0, 0.3, 0]
        hgt = 0.3 - rays(X, F, Oo, np.tile([0, -1.0, 0], (7, 1)))
        Pt = Oo.copy(); Pt[:, 1] = hgt + 0.0025
        d = ax * 0.0045 + np.array([0, -0.0035, 0])
        Xl = np.r_[Pt - d, Pt + d]; Fl = []
        for i in range(6): Fl += [(i, i + 7, i + 1), (i + 1, i + 7, i + 8)]
        Fl = np.array(Fl); n = np.cross(Xl[Fl[0, 1]] - Xl[Fl[0, 0]], Xl[Fl[0, 2]] - Xl[Fl[0, 0]])
        if n[1] < 0: Fl = Fl[:, ::-1]
        sj, sw = one(14, side + 'Foot')
        out.append(thick(part(Xl, Fl, sj, sw, 'lime'), 0.0012))
    return out
boots = boot('Left') + boot('Right')

f_hand = np.where(armw > 0.5, 0.86 - tf, 1.0)
v, t, a, _ = cut(V, T, f_hand, D)
# a hand cut from one piece of card: Anny's hand pressed flat, the fingers left as the scissors' snips
for sgn in (1, -1):
    m = v[:, 0] * sgn > 0; X = v[m]; c = X.mean(0)
    w_, U_ = np.linalg.eigh(np.cov((X - c).T)); nrm = U_[:, 0]
    v[m] = X - np.outer((X - c) @ nrm, nrm) * 0.72
sj, sw = top4(a)
hands = [part(v, t, sj, sw, 'skin')]
legs = trousers + boots
parts += legs + hands; step['legs'] = legs + hands


# ---------------- the slouch, put into the rest ----------------
def slouch(pieces, Jn, on=True):
    """turn the spine's joints about the body's side axis (degrees, + is forward) and roll the shoulders; every joint
    below goes with its parent, every vertex with its weights (the rest is re-posed; the frames stay)"""
    ANG = {} if not on else {'Spine1': (-6, 0, 0), 'Spine2': (9, 0, 0), 'Chest': (10, 0, 0), 'Neck1': (5, 0, 0), 'Head': (-4, 0, 0),
           'LeftShoulder': (0, -9, 7), 'RightShoulder': (0, 9, -7)}
    def rot(ax, ay, az):
        ax, ay, az = np.radians([ax, ay, az])
        Rx = np.array([[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]])
        Ry = np.array([[np.cos(ay), 0, np.sin(ay)], [0, 1, 0], [-np.sin(ay), 0, np.cos(ay)]])
        Rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
        return Rz @ Ry @ Rx
    G = np.zeros((NJ, 3, 4)); newJ = np.zeros_like(Jn)
    for j in range(NJ):
        p = PARENT[j]
        Gp = np.c_[np.eye(3), np.zeros(3)] if p < 0 else G[p]
        newJ[j] = Gp[:, :3] @ Jn[j] + Gp[:, 3]
        R = rot(*ANG.get(NAMES[j], (0, 0, 0)))
        # x → Gp(R (x − J_j) + J_j)
        G[j, :, :3] = Gp[:, :3] @ R; G[j, :, 3] = Gp[:, :3] @ (Jn[j] - R @ Jn[j]) + Gp[:, 3]
    out = []
    for p in pieces:
        W = np.zeros((len(p['V']), 3, 4))
        for k in range(4): W += p['sw'][:, k][:, None, None] * G[p['sj'][:, k]]
        W /= p['sw'].sum(1)[:, None, None]
        q = dict(p); q['V'] = np.einsum('nab,nb->na', W[:, :, :3], p['V']) + W[:, :, 3]
        out.append(q)
    return out, newJ


final, JF = slouch(parts, J2)
lo = min(p['V'][:, 1].min() for p in final)
for p in final: p['V'][:, 1] -= lo
JF[:, 1] -= lo
write('kira', final, JF, B['frames'], folder=DATA)
print('height', max(p['V'][:, 1].max() for p in final), 'head centre', (O[1]))
# the same figure standing straight (for comparing with the turnaround and expression sheets, drawn upright)
up, JU = slouch(parts, J2, False)
lo_u = min(p['V'][:, 1].min() for p in up)
for p in up: p['V'][:, 1] -= lo_u
JU[:, 1] -= lo_u
write('kira-up', up, JU, B['frames'])
np.savez(f'{CACHE}/build.npz', O=O - [0, lo_u, 0], JF=JF, J2=J2)

if STEPS:
    sjb, swb = top4(D)
    anny = part(B['positions'], T, sjb, swb, 'clay')
    write('step-anny', [anny], B['joints'], B['frames'])
    write('step-fit', [part(V, T, sjb, swb, 'clay')], J, B['frames'])
    hb = np.load(f'{CACHE}/head_steps.npz')
    for nm, key in (('step-head0', 'faired'), ('step-head1', 'warped')):
        Xh = hb[key] - (0 if key == 'warped' else [0, 0.7375, 0]); Th = tris(hb['Q'])
        s1, s2 = one(len(Xh), 'Head')
        write(nm, [part(toW(Xh), Th, s1, s2, 'clay')], J2, B['frames'])
    acc = []
    for nm in ('head', 'hair', 'hoodie', 'phones', 'legs'):
        acc += step[nm]
        write('step-' + nm, acc, J2, B['frames'])
