"""Аня assembled: Anny's fitted woman body, the fitted base head with a small turned-up nose, the bob lofted from the
drawing's front and side outlines (fringe, flip, Alice band), the dress (a bodice cut from the body's surface, a full
skirt lofted as a bell with folds and a scalloped hem), the open cardigan, the round collar, ballet flats — every part
skinned on SOMA's 77 joints — written as one model pack (model.py)."""
import numpy as np
from common import CACHE, IX, NAMES, vertex_normals
from body import B, fit
from model import part, write, MATS
from meshcut import cut, loops, smooth, rim, neighbours
from hbm import tris
from drawing import K, extent, EAR_X, curve

NJ = len(NAMES)


def dense(sj, sw):
    D = np.zeros((len(sj), NJ))
    for k in range(4): np.add.at(D, (np.arange(len(sj)), sj[:, k]), sw[:, k])
    return D


def top4(D):
    j = np.argsort(-D, 1)[:, :4]; w = np.take_along_axis(D, j, 1)
    return j, w / np.maximum(w.sum(1, keepdims=True), 1e-9)


def split(p, g, mat2):
    """a part cut in two along g = 0: where g < 0 it keeps its paint, elsewhere it takes mat2 — so a paint changes on
    a clean line, never across a triangle"""
    A = np.c_[dense(p['sj'], p['sw']), p['fuv'], p['pat'], p['mat']]
    out = []
    for sgn, m in ((1, None), (-1, mat2)):
        v, t, a, _ = cut(p['V'], p['T'], sgn * g, A)
        if len(t) == 0: continue
        sj, sw = top4(a[:, :NJ])
        mm = np.rint(a[:, -1]).astype(int) if m is None else np.full(len(v), MATS.index(m))
        out.append(dict(V=v, T=t, sj=sj, sw=sw, mat=mm, fuv=a[:, NJ:NJ + 3], pat=a[:, NJ + 3:NJ + 6]))
    return out


def one(n, joint): return np.tile([IX[joint], 0, 0, 0], (n, 1)), np.tile([1., 0, 0, 0], (n, 1))


def grid(nu, nv, wrap=True):
    """triangles of a grid of nv rings of nu points (ring after ring); wrap: each ring closed"""
    F = []
    for i in range(nv - 1):
        for j in range(nu if wrap else nu - 1):
            a, b = i * nu + j, i * nu + (j + 1) % nu
            F += [(a, b, a + nu), (b, b + nu, a + nu)]
    return np.array(F)


# ---------------- the body ----------------
V, J = fit()
T = B['triangles']; P = B['parts'] / 255.; PN = B['partnames']
pw = lambda *names: sum(P[:, PN.index(n)] for n in names)
D = dense(B['sj'], B['sw'])
NB = vertex_normals(V, T)

# where the head sits: the drawing's head centre O; the chin (drawing y 97) 1.42 m up
CHIN_Y = 1.418
O = np.array([0.0, CHIN_Y + 97 * K, 0.022])
toW = lambda X: X + O                         # head frame → world
J2 = J.copy()
J2[IX['Head']] = O + [0, -70 * K, 4 * K]
J2[IX['HeadEnd']] = O + [0, 125 * K, 4 * K]
J2[IX['Jaw']] = O + [0, -50 * K, 36 * K]
J2[IX['LeftEye']] = O + [26 * K, -10 * K, 60 * K]; J2[IX['RightEye']] = O + [-26 * K, -10 * K, 60 * K]
J2[IX['Neck2']] = (J2[IX['Neck1']] + J2[IX['Head']]) / 2

# ---------------- the head ----------------
hs = np.load(f'{CACHE}/head_steps.npz')
HV, HQ = hs['warped'].copy(), hs['Q']; HT = tris(HQ)
# the base's ears are faired away: they would lie under the bob, and their lobes showed below its edge
FB = hs['faired']
em = ((np.abs(FB[:, 0]) > 0.096) & (FB[:, 1] > 0.65) & (FB[:, 1] < 0.815) & (FB[:, 2] > -0.06) & (FB[:, 2] < 0.045)).astype(float)
em = np.clip(smooth(np.c_[em, em, em], HT, it=2, lam=1.0)[:, 0] * 4, 0, 1)
HV = smooth(HV, HT, it=200, lam=0.6, mask=em)
NECK_CUT = 1.352
HV, HT, _, _ = cut(HV, HT, -(HV[:, 1] - (NECK_CUT - O[1])))
# the cheeks and jaw smoothed (the base's jaw muscles and the patch's edge leave dents a flat-painted face shows)
yd, zd = -HV[:, 1] / K, HV[:, 2] / K
cm = ((yd > -20) & (yd < 104) & (zd > -30)).astype(float)
for _ in range(30):                       # (Taubin's two steps: the lumps go, the form doesn't shrink)
    HV = smooth(HV, HT, it=1, lam=0.5, mask=cm); HV = smooth(HV, HT, it=1, lam=-0.53, mask=cm)
# nothing wider than the drawing's front outline (the base's ears lie flat under the bob)
from drawing import FRONT
wmax = np.array([extent(FRONT, min(max(v, -117), 96), +1) for v in -HV[:, 1] / K]) * K
HV[:, 0] = np.clip(HV[:, 0], -wmax, wmax)
HW = toW(HV)


def head_skin(W):
    """the head on Head; its neck from Head down to Neck1"""
    y = W[:, 1]; yH, y2, y1 = J2[IX['Head'], 1], J2[IX['Neck2'], 1], J2[IX['Neck1'], 1]
    Dh = np.zeros((len(W), NJ))
    a = np.clip((y - y2) / (yH - y2), 0, 1); b = np.clip((y - y1) / (y2 - y1), 0, 1)
    Dh[:, IX['Head']] = a
    Dh[:, IX['Neck2']] = (1 - a) * b
    Dh[:, IX['Neck1']] = (1 - a) * (1 - b)
    return top4(Dh)


# the face picture's coordinates: the front projection in the drawing's head units, and how much the surface faces front
def fuv_of(X, N):
    u = (X[:, 0] / K + 128) / 256; v = (-X[:, 1] / K + 128) / 256
    return np.c_[u, v, np.clip(N[:, 2], 0, 1) * (X[:, 2] > 0)]


# the hair's edge on the head, in the drawing's units (x, y down, s = the side view's x):
# the fringe's lower edge from the front view, the bob's front edge from the side view
FR = [(-100, -16), (-72, -30), (-62, -27), (-40, -50), (-10, -62), (20, -64), (52, -54), (72, -34), (100, -16)]
ED = [(-140, 66), (-60, 64), (-40, 40), (20, 0), (66, 10), (90, 12)]          # (y, s)
def hair_f(X):
    """< 0 where there is hair"""
    x = X[:, 0] / K; y = -X[:, 1] / K; s = X[:, 2] / K + EAR_X
    return np.maximum(np.minimum(y - np.interp(x, *zip(*FR)), (s - np.interp(y, *zip(*ED))) * 0.8), y - 76)
def skull_f(X):
    """< 0 where the skull under the hair is painted as hair (so nothing pale shows between the bob and the head): above
    the fringe's line and behind the ears — the face keeps its whole width in the front view"""
    x = X[:, 0] / K; y = -X[:, 1] / K; s = X[:, 2] / K + EAR_X
    return np.maximum(np.minimum(y - np.interp(x, *zip(*FR)) + 6, s + 14), y - 76)

parts = []
sj, sw = head_skin(HW)
# under the jaw line the neck is a second tone darker (the drawing's SKIN_D)
# (the line is the front view's chin: the drawing's face outline carried across the neck, so the chin reads as a round
# shape against the darker neck)
HN = vertex_normals(HV, HT); yd = -HV[:, 1] / K
jaw = yd - (np.interp(np.abs(HV[:, 0]) / K, [0, 10, 20, 28, 38], [97, 96, 92, 87, 170]) + 2)
head = part(HW, HT, sj, sw, 'skin', fuv=fuv_of(HV, HN), pat=HW)
for p in split(head, jaw, 'skin_d'):
    parts += split(p, -skull_f(p['V'] - O), 'hair') if p['mat'][0] == MATS.index('skin') else [p]


def ellipsoid(c, r, nu=24, nv=16):
    th = np.linspace(0, np.pi, nv); ph = np.linspace(0, 2 * np.pi, nu, endpoint=False)
    X = np.array([[np.sin(t) * np.cos(p), np.cos(t), np.sin(t) * np.sin(p)] for t in th for p in ph]) * r + c
    return X, grid(nu, nv)[:, ::-1]

# the small turned-up nose (side view: its tip at 78, 36)
NX, NT = ellipsoid(np.zeros(3), np.array([4.6, 14, 7.5]), nu=24, nv=20)
ny = -NX[:, 1] + 27; nz = NX[:, 2] + 64.5 + (ny - 27) * 0.42          # the ridge slopes forward down to the tip
ny = np.where(ny > 37, 37 + (ny - 37) * 0.35, ny)                      # a short flat underside
NX = np.c_[NX[:, 0] * np.clip((ny - 4) / 20, 0.2, 1), -ny, nz - EAR_X] * K
sj, sw = one(len(NX), 'Head')
# one flat paint, its underside a darker one: from the front only the drawn stroke shows, turned — a small wedge
nose = part(toW(NX), NT, sj, sw, 'nose', fuv=fuv_of(NX, np.tile([0, 0, 1.0], (len(NX), 1))), pat=toW(NX))
parts += split(nose, (-NX[:, 1] / K - 38.2), 'nose_d')

# ---------------- the hair: a bob lofted from the drawing's outlines ----------------
HAIR_FRONT = [(0, -132), (58, -118), (88, -76), (94, -20), (94, 36), (112, 66), (112, 80), (-112, 80), (-112, 66), (-94, 36),
              (-94, -20), (-88, -76), (-58, -118)]
HAIR_SIDE = [(-20, -132), (30, -124), (60, -98), (71, -62), (73, -20), (73, 40), (74, 80), (-98, 80), (-96, 74), (-90, 48),
             (-96, 0), (-90, -60), (-64, -112)]
SC = -12        # the sections' centre in the side view
nu, YS = 72, np.r_[np.linspace(-131.2, -120, 5), np.linspace(-116, 60, 34), [64, 68, 71]]
ring = []
for y in YS:
    a = extent(HAIR_FRONT, y, +1); f = extent(HAIR_SIDE, y, +1); b = extent(HAIR_SIDE, y, -1)
    if y > 40: a = 94 + 18 * ((y - 40) / 31) ** 2; b = min(b, -90 - 7 * ((y - 40) / 31) ** 2)     # the flip at the ends
    cs = SC if y > -100 else SC + (-20 - SC) * ((-100 - y) / 32) ** 1.0
    for k in range(nu):
        ph = 2 * np.pi * k / nu; c, s_ = np.cos(ph), np.sin(ph)
        rz = (f - cs) if c > 0 else (cs - b)
        n = 2.3                                           # a little squarer than an ellipse: a bob is a box of hair
        r = (abs(s_ / a) ** n + abs(c / rz) ** n) ** (-1 / n)
        ring.append((r * s_, y, cs + r * c))
# the ends turned in under the bob (its thickness), then the crown's point closes the top
base = ring[-nu:]
for sc_, y in ((0.94, 74), (0.86, 72), (0.82, 60)):
    ring += [(x * sc_, y, SC + (s - SC) * sc_) for x, _, s in base]
R = np.array(ring)
HX = np.c_[R[:, 0], -R[:, 1], R[:, 2] - EAR_X] * K
HXT = grid(nu, len(R) // nu)
top = len(HX); HX = np.r_[HX, [[0, 132 * K, (-20 - EAR_X) * K]]]
HXT = np.r_[HXT, [(k, top, (k + 1) % nu) for k in range(nu)]][:, ::-1]
hv, ht, _, edge = cut(HX, HXT, hair_f(HX))
L = max(loops(ht), key=len)
hn = vertex_normals(hv, ht)
hv2, ht2, _ = rim(hv, ht, L, -hn[L] * 5 * K)
hfuv = fuv_of(hv2, vertex_normals(hv2, ht2)); hfuv[:, 2] *= (-hv2[:, 1] / K < -40)      # the dry strokes only on the top
sj, sw = one(len(hv2), 'Head')
hair = part(toW(hv2), ht2, sj, sw, 'hair', fuv=hfuv, pat=toW(hv2))
# the Alice band: a hoop over the head from behind the ears, tilted forward
X = hair['V'] - O; yb = -X[:, 1] / K; sb = X[:, 2] / K + EAR_X
band = np.maximum(np.abs(sb - (-6 + (-64 - yb) * 0.8)) / np.hypot(1, 0.8) - 6.0, yb + 64)
parts += split(hair, -band, 'band')

np.savez(f'{CACHE}/build_head.npz', O=O)

# ---------------- clothes ----------------
def bone_t(X, a, b):
    A, Bb = J[IX[a]], J[IX[b]]; d = Bb - A
    return ((X - A) @ d) / (d @ d)

def shell(region_f, off, mat, smooth_it=3, free=0):
    """the body's surface where region_f < 0, pushed out along its normals by off (per vertex)"""
    A = np.c_[D, NB, off]
    v, t, a, on = cut(V, T, region_f, A)
    d, n, o = a[:, :NJ], a[:, NJ:NJ + 3], a[:, -1]
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    v = v + n * o[:, None]
    v = smooth(v, t, it=smooth_it, lam=0.3, fixed=np.where(on)[0])
    if free:                                              # the edge too: its line faired along itself
        for L in loops(t):
            L = np.array(L)
            for _ in range(free): v[L] = 0.5 * v[L] + 0.25 * (v[np.roll(L, 1)] + v[np.roll(L, -1)])
        v = smooth(v, t, it=2, lam=0.3, fixed=np.unique(np.concatenate([np.array(L) for L in loops(t)])))
    sj, sw = top4(d)
    return part(v, t, sj, sw, mat)

y = V[:, 1]
WAIST, COLL, HEM = 1.072, 1.386, 0.505
ua = np.where(V[:, 0] > 0, bone_t(V, 'LeftArm', 'LeftForeArm'), bone_t(V, 'RightArm', 'RightForeArm'))     # along the upper arm
fa = np.where(V[:, 0] > 0, bone_t(V, 'LeftForeArm', 'LeftHand'), bone_t(V, 'RightForeArm', 'RightHand'))   # along the forearm
arm = pw('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand')
armside = arm > 0.5
NZ = np.array([0, 0, J2[IX['Neck1'], 2]])
rneck = np.hypot(V[:, 0], V[:, 2] - NZ[2])

def to_neck(p, y0, rt=0.031, pw_=1.5):
    """above y0 a shell is drawn in round the thin drawn neck"""
    sv = p['V']; rr = np.hypot(sv[:, 0], sv[:, 2] - NZ[2])
    sg = np.clip((sv[:, 1] - y0) / (COLL - y0), 0, 1) ** pw_
    k = np.where(rr > rt, (rr + (rt - rr) * sg) / rr, 1.0)
    sv[:, 0] *= k; sv[:, 2] = NZ[2] + (sv[:, 2] - NZ[2]) * k
    return p

# the bodice: the trunk from the waist to the neck, sleeveless
f_bod = np.maximum.reduce([WAIST - 0.012 - y, y - COLL, np.where(armside, 1.0, -1.0), np.where(arm > 0.15, ua - 0.12, -1.0)])
zc = J[IX['Chest'], 2]
BOD_PAT = lambda bod: np.c_[np.arctan2(bod['V'][:, 0], bod['V'][:, 2] - zc + 0.05) * 0.11, bod['V'][:, 1], 0 * bod['V'][:, 1]]
# the cardigan: sleeves to the wrists, the back and the sides, open in front
open_x = np.interp(y, [1.04, 1.2, 1.36], [0.05, 0.046, 0.036])
f_open = np.where((V[:, 2] > zc - 0.01), np.abs(V[:, 0]) - open_x, 1.0)           # > 0: covered
f_car = np.maximum.reduce([1.036 - y, y - COLL + 0.004, np.where(armside, fa - 0.9, -f_open)])
# (the bodice shows only in the opening, and goes a little way under the cardigan's edges)
bod = to_neck(shell(np.maximum(f_bod, f_open - 0.014), np.full(len(V), 0.004), 'dress', smooth_it=20), 1.33)
bod['pat'] = BOD_PAT(bod)
parts.append(bod)
off_c = 0.009 + 0.004 * np.clip(fa, 0, 1) * armside
car = to_neck(shell(f_car, off_c, 'cardi', smooth_it=16, free=3), 1.33, rt=0.036)
parts.append(car)
# the round collar: two white lobes lying on the chest, a band round the back of the neck
cy = 1.352
lobe = lambda sx: np.hypot((V[:, 0] - sx * 0.047) / 0.046, (y - cy) / 0.034) - 1
f_col = np.where(V[:, 2] > NZ[2], np.minimum(lobe(1), lobe(-1)), (1.356 - y) / 0.03 + np.clip(np.abs(V[:, 0]) - 0.07, 0, 1) * 30)
f_col = np.maximum(f_col, y - COLL + 0.006)
col = to_neck(shell(f_col, np.full(len(V), 0.0145), 'collar', smooth_it=6, free=3), 1.35, rt=0.040, pw_=1.0)
parts.append(col)

# the skirt: a bell from the waist to the knee, folds deepening to a scalloped hem (twelve of each)
HIP = J[IX['Hips']]
NF, nus, nvs = 12, 144, 40
prof_y = [WAIST + 0.004, WAIST - 0.02, 0.96, 0.75, HEM]; prof_r = [0.074, 0.08, 0.142, 0.222, 0.272]
SK, SKP, slant = [], [], 0.0
k_cone = (0.272 - 0.08) / np.hypot(0.272 - 0.08, WAIST - HEM); rho0 = 0.08 / k_cone
for i in range(nvs):
    t = i / (nvs - 1)
    for j in range(nus + 1):
        th = 2 * np.pi * j / nus - np.pi                      # the seam at the back
        fold = np.cos(NF * th)
        yy = WAIST + 0.004 + (HEM - 0.008 * fold - WAIST - 0.004) * t
        r = np.interp(yy, prof_y[::-1], prof_r[::-1]) * (1 + 0.045 * t ** 1.6 * fold)
        sq = 0.86 + 0.14 * t                                   # the waist is an oval, the hem a circle
        SK.append((r * np.sin(th), yy, HIP[2] - 0.004 + r * sq * np.cos(th)))
        rho = rho0 + (WAIST - yy) / np.sqrt(1 - k_cone ** 2)
        SKP.append((rho * np.sin(th * k_cone), rho * np.cos(th * k_cone), 0))
SK = np.array(SK); SKT = grid(nus + 1, nvs, wrap=False)[:, ::-1]
# it hangs from the hips and swings with the legs: lower down each side follows its thigh more
t_ = np.clip((WAIST - SK[:, 1]) / (WAIST - HEM), 0, 1)
sidew = 0.5 + 0.5 * np.clip(SK[:, 0] / 0.09, -1, 1)
leg = 0.62 * np.clip((t_ - 0.12) / 0.88, 0, 1) ** 1.2
Ds = np.zeros((len(SK), NJ))
Ds[:, IX['LeftLeg']] = leg * sidew; Ds[:, IX['RightLeg']] = leg * (1 - sidew)
top_ = np.clip(1 - t_ / 0.15, 0, 1) * 0.5
Ds[:, IX['Spine1']] = top_; Ds[:, IX['Hips']] = 1 - leg - top_
sj, sw = top4(Ds)
skirt = part(SK, SKT, sj, sw, 'dress', pat=np.array(SKP))
parts += split(skirt, SK[:, 1] - (WAIST - 0.014), 'belt')

# ballet flats: lofted along each foot, low, a pointed toe
def flat(side):
    F_, T_ = J[IX[side + 'Foot']], J[IX[side + 'ToeEnd']]
    ax = np.array([T_[0] - F_[0], 0, T_[2] - F_[2]]); L_ = np.linalg.norm(ax); ax /= L_
    heel = np.array([F_[0], 0, F_[2]]) - ax * 0.03; Ltot = L_ + 0.03 + 0.016
    side_v = np.cross([0, 1, 0], ax)
    nu_, nv_ = 26, 20; X = []
    for i in range(nu_):
        t = i / (nu_ - 1)
        c = heel + ax * Ltot * t
        w = np.interp(t, [0, 0.15, 0.55, 0.8, 1], [0.014, 0.021, 0.027, 0.02, 0.004])
        hgt = np.interp(t, [0, 0.12, 0.3, 0.6, 0.85, 1], [0.03, 0.042, 0.03, 0.026, 0.022, 0.012])
        for j in range(nv_):
            a = 2 * np.pi * j / nv_
            sx, sy = np.cos(a), np.sin(a)
            r = (abs(sx) ** 2.4 + abs(sy) ** 2.4) ** (-1 / 2.4)
            X.append(c + side_v * sx * r * w + np.array([0, max((sy * r * 0.5 + 0.5) * hgt - 0.002, 0), 0]))
    X = np.array(X); Fc = [tuple(q) for q in grid(nv_, nu_)]
    for end, rev in ((0, True), (nu_ - 1, False)):
        ci = len(X); X = np.r_[X, X[end * nv_:(end + 1) * nv_].mean(0)[None]]
        for j in range(nv_):
            tri = (end * nv_ + j, end * nv_ + (j + 1) % nv_, ci)
            Fc.append(tri[::-1] if rev else tri)
    tt = ((X - heel) @ ax) / Ltot
    Dd = np.zeros((len(X), NJ)); wt = np.clip((tt - 0.55) / 0.2, 0, 1)
    Dd[:, IX[side + 'Foot']] = 1 - wt; Dd[:, IX[side + 'ToeBase']] = wt
    sj, sw = top4(Dd)
    return part(X, np.array(Fc), sj, sw, 'shoe')
for sd in ('Left', 'Right'): parts.append(flat(sd))

# the skin left showing: the hands below the cuffs, the legs below the skirt (the feet's toes are in the shoes)
legs = pw('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot') > 0.5
tb = np.where(V[:, 0] > 0, bone_t(V, 'LeftFoot', 'LeftToeEnd'), bone_t(V, 'RightFoot', 'RightToeEnd'))
f_skin = np.minimum(np.where(armside, 0.86 - fa, 1.0), np.where(legs, np.maximum(y - 0.66, (tb - 0.42) * 0.1), 1.0))
v, t, a, _ = cut(V, T, f_skin, D)
sj, sw = top4(a)
parts.append(part(v, t, sj, sw, 'skin'))

write('anya', parts, J2, B['frames'], extra=dict(dots=dict(mat='dress', step=0.044, r=0.0052)))
