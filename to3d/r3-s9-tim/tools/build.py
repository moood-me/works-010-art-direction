"""Тим assembled: Anny's fitted child body, the fitted base head with a button nose, the hair, the clothes cut from the
body's own surface, the shoes — every part skinned on SOMA's 77 joints — written as one model pack (model.py)."""
import numpy as np
from common import CACHE, IX, NAMES, vertex_normals
from body import B, fit
from model import part, write
from meshcut import cut, loops, smooth, rim, neighbours
from hbm import tris
from drawing import K, extent
import head as H

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
    from model import MATS
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


# ---------------- the body ----------------
V, J = fit()
T = B['triangles']; P = B['parts'] / 255.; PN = B['partnames']
pw = lambda *names: sum(P[:, PN.index(n)] for n in names)
D = dense(B['sj'], B['sw'])
NB = vertex_normals(V, T)

# where the head sits: the drawing's head centre O; chin (drawing y 88) a little above the shoulders
CHIN_Y = 0.848
O = np.array([0.0, CHIN_Y + 88 * K, 0.002])
toW = lambda X: X + O                         # head frame → world
J2 = J.copy()
J2[IX['Head']] = O + [0, -58 * K, 4 * K]
J2[IX['HeadEnd']] = O + [0, 112 * K, 4 * K]
J2[IX['Jaw']] = O + [0, -40 * K, 40 * K]
J2[IX['LeftEye']] = O + [24 * K, -14 * K, 66 * K]; J2[IX['RightEye']] = O + [-24 * K, -14 * K, 66 * K]
J2[IX['Neck2']] = (J2[IX['Neck1']] + J2[IX['Head']]) / 2

# ---------------- the head ----------------
hs = np.load(f'{CACHE}/head_steps.npz')
HV, HQ = hs['warped'].copy(), hs['Q']; HT = tris(HQ)
# the ears stick out as the drawing's do: each ear (found on the base) turned out about its front edge, a little larger
FB = hs['faired']
ew = np.clip((np.abs(FB[:, 0]) - 0.104) / 0.01, 0, 1) * ((FB[:, 1] > 0.66) & (FB[:, 1] < 0.80) & (FB[:, 2] > -0.045) & (FB[:, 2] < 0.035))
for sgn in (1, -1):
    m = (ew > 0) & (np.sign(HV[:, 0]) == sgn)
    c = (HV[m] * ew[m, None]).sum(0) / ew[m].sum(); zf = HV[m & (ew > 0.5), 2].max()
    w = ew[m, None]
    X = HV[m]; X = c + (X - c) * (1 + 0.18 * w)
    X[:, 0] += sgn * w[:, 0] * 0.4 * np.clip(zf - X[:, 2], 0, None)
    HV[m] = X
# the neck ends inside the shirt
HV, HT, EW, _ = cut(HV, HT, -(HV[:, 1] - (0.78 - O[1])), ew[:, None]); EW = EW[:, 0]
# the cheeks and jaw smoothed (the base's jaw muscles and the patch's edge leave dents a flat-painted face shows)
yd, zd = -HV[:, 1] / K, HV[:, 2] / K
cm = ((yd > -5) & (yd < 100) & (zd > -25) & (EW < 0.01)).astype(float)
HV = smooth(HV, HT, it=25, lam=0.5, mask=cm)
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
HN = vertex_normals(HV, HT)
def fuv_of(X, N):
    u = (X[:, 0] / K + 128) / 256; v = (-X[:, 1] / K + 128) / 256
    return np.c_[u, v, np.clip(N[:, 2], 0, 1) * (X[:, 2] > 0)]

parts = []
sj, sw = head_skin(HW)
# the neck a second tone darker under the jaw line (the drawing's SKIN_D): it parts the round head from the neck
jaw = -HV[:, 1] / K - np.interp(HV[:, 2] / K, [-70, -40, -15, 55], [86, 80, 64, 90])
parts += split(part(HW, HT, sj, sw, 'skin', fuv=fuv_of(HV, HN), pat=HW), jaw, 'skin_d')

# the button nose: a small ball on the face where the drawing has it (front 0,34 r 9×8; side tip at 84)
def ellipsoid(c, r, nu=24, nv=16):
    th = np.linspace(0, np.pi, nv); ph = np.linspace(0, 2 * np.pi, nu, endpoint=False)
    X = np.array([[np.sin(t) * np.cos(p), np.cos(t), np.sin(t) * np.sin(p)] for t in th for p in ph]) * r + c
    F = []
    for i in range(nv - 1):
        for j in range(nu):
            a, b = i * nu + j, i * nu + (j + 1) % nu; c2, d = a + nu, b + nu
            F += [(a, c2, b), (b, c2, d)]
    return X, np.array(F)

NX, NT = ellipsoid(np.array([0, -36 * K, (84 + 8 - 10) * K]), np.array([9, 8, 10]) * K)
sj, sw = one(len(NX), 'Head')
parts.append(part(toW(NX), NT, sj, sw, 'skin', fuv=fuv_of(NX, vertex_normals(NX, NT)), pat=toW(NX)))

# ---------------- the hair ----------------
FR = [(-90, -20), (-78, -26), (-66, -50), (-48, -42), (-34, -66), (-10, -48), (6, -70), (30, -50), (46, -68), (66, -46), (78, -28), (90, -20)]
SD = [(90, -62), (76, -62), (62, -56), (54, -70), (46, -46), (34, -62), (20, -30), (8, -44), (-6, -16), (-24, -34), (-44, -6), (-58, -14), (-72, 8), (-90, 14)]
def hairline(X):
    x = X[:, 0] / K; y = -X[:, 1] / K; z = X[:, 2] / K; sx = z - 8
    hf = np.interp(x, *zip(*FR)); hs_ = np.interp(-sx, *zip(*[(-a, b) for a, b in SD]))
    th = np.degrees(np.arctan2(np.abs(x), z))
    wf = np.clip((70 - th) / 35, 0, 1)
    return y - (wf * hf + (1 - wf) * hs_)

hv, ht, _, edge = cut(HV, HT, np.maximum(hairline(HV), (EW - 0.05) * 40))
hn = vertex_normals(hv, ht)
yy = -hv[:, 1] / K
thick = (5 + 11 * np.clip((-yy - 20) / 86, 0, 1)) * K
# the shell, thinning to a lip at its edge
nb = neighbours(ht, len(hv)); dist = np.where(edge, 0, 99)
for _ in range(6):
    for i in range(len(hv)):
        if len(nb[i]): dist[i] = min(dist[i], dist[nb[i]].min() + 1)
lip = np.clip(dist / 5, 0.3, 1.0)
hv2 = hv + hn * (thick * lip)[:, None]
hv2 = smooth(hv2, ht, it=4, lam=0.4, fixed=np.where(edge)[0])
L = max(loops(ht), key=len)
hv3, ht3, _ = rim(hv2, ht, L, -hn[L] * (thick * lip)[L][:, None] * 1.1)
# the cowlick: a flattened tapering lock from the crown, curling forward
def lock(p0, p1, p2, r0, flat=0.6, n=18, m=10):
    X, F = [], []
    for i in range(n):
        t = i / (n - 1); c = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
        tg = 2 * (1 - t) * (p1 - p0) + 2 * t * (p2 - p1); tg /= np.linalg.norm(tg)
        a = np.cross(tg, [0, 0, 1.0]); a /= np.linalg.norm(a); b = np.cross(tg, a)
        r = r0 * (1 - t) ** 1.2 + 1e-4
        for j in range(m):
            q = 2 * np.pi * j / m
            X.append(c + r * np.cos(q) * a + r * flat * np.sin(q) * b)
    for i in range(n - 1):
        for j in range(m):
            a_, b_ = i * m + j, i * m + (j + 1) % m
            F += [(a_, a_ + m, b_), (b_, a_ + m, b_ + m)]
    return np.array(X), np.array(F)

CX, CT = lock(np.array([4, 112, 20.]) * K, np.array([6, 132, 14.]) * K, np.array([12, 146, 6.]) * K, 9 * K)
hvA = np.r_[hv3, CX]; htA = np.r_[ht3, CT + len(hv3)]
hfuv = fuv_of(hvA, vertex_normals(hvA, htA))
sj, sw = one(len(hvA), 'Head')
parts.append(part(toW(hvA), htA, sj, sw, 'hair', fuv=hfuv, pat=toW(hvA)))

np.savez(f'{CACHE}/build_head.npz', O=O)

# ---------------- clothes from the body's surface ----------------
def bone_t(X, a, b):
    A, Bb = J[IX[a]], J[IX[b]]; d = Bb - A
    return ((X - A) @ d) / (d @ d)

def shell(region_f, off, mat, A_extra=None, rim_in=0.006, smooth_it=3):
    """the body's surface where region_f < 0, pushed out along its normals by off (per vertex), with a rim"""
    A = np.c_[D, NB, off]
    v, t, a, on = cut(V, T, region_f, A)
    d, n, o = a[:, :NJ], a[:, NJ:NJ + 3], a[:, -1]
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    v = v + n * o[:, None]
    v = smooth(v, t, it=smooth_it, lam=0.3, fixed=np.where(on)[0])
    sj, sw = top4(d)
    return part(v, t, sj, sw, mat)

y = V[:, 1]
# shirt: above the hem, below the collar, sleeves to the upper arm's middle
hem = 0.565; coll = 0.834
sl = np.maximum(np.where(V[:, 0] > 0, bone_t(V, 'LeftArm', 'LeftForeArm'), bone_t(V, 'RightArm', 'RightForeArm')), -9)
armside = pw('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand') > 0.3
f_shirt = np.maximum.reduce([hem - y, y - (coll - 0.010 * np.clip(V[:, 2] / 0.05, 0, 1)), np.where(armside | (np.abs(V[:, 0]) > 0.11), sl - 0.5, -1),
                             (pw('Lthigh', 'Rthigh') > 0.4) * 1.0 - 0.5])
off_s = 0.006 + 0.010 * np.clip((0.66 - y) / 0.1, 0, 1) + 0.006 * np.clip(sl / 0.5, 0, 1) * armside
shirt = shell(f_shirt, off_s, 'shirt', smooth_it=14)
# a crew neck: above the shoulders the shirt is drawn in round the (thin, drawn) neck
sv = shirt['V']; nz = O[2] + 10 * K
rr = np.hypot(sv[:, 0], sv[:, 2] - nz)
sgy = np.clip((sv[:, 1] - 0.785) / (coll - 0.785), 0, 1) ** 1.5
rt = 0.040
k = np.where(rr > rt, (rr + (rt - rr) * sgy) / rr, 1.0)
sv[:, 0] *= k; sv[:, 2] = nz + (sv[:, 2] - nz) * k
shirt['pat'] = sv.copy()
# the collar: a cream band at the neckline
sp = shirt['pat']
parts += split(shirt, sp[:, 1] - (coll - 0.008 - 0.010 * np.clip(sp[:, 2] / 0.05, 0, 1)), 'collar')
# shorts: from the waist to just below the crotch, wide legs
tl = np.maximum(bone_t(V, 'LeftLeg', 'LeftShin') * (V[:, 0] > 0), bone_t(V, 'RightLeg', 'RightShin') * (V[:, 0] < 0))
f_shorts = np.maximum(y - 0.574, tl - 0.42)
off_p = 0.005 + 0.012 * np.clip(tl / 0.42, 0, 1) ** 1.5
parts.append(shell(f_shorts, off_p, 'shorts', smooth_it=8))
# shoes: the foot below the ankle, puffed and smoothed
shoe_top = 0.062
f_shoe = np.where(pw('Lfoot', 'Rfoot', 'Lshin', 'Rshin') > 0.3, y - shoe_top, 1.0)
shoe = shell(f_shoe, np.full(len(V), 0.007), 'shoe', smooth_it=12)
sv = shoe['V']; sv[:, 1] = np.maximum(sv[:, 1], -0.002)
parts += split(shoe, 0.009 - sv[:, 1], 'sole')

# the skin left showing: arms below the sleeves, hands, legs below the shorts (white socks above the shoes)
f_skin = np.minimum.reduce([np.where(armside, 0.45 - sl, 1.0), np.where(pw('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot') > 0.3, 0.36 - tl, 1.0)])
f_skin = np.where((y < 0.03) & (pw('Lfoot', 'Rfoot') > 0.5), 1.0, f_skin)   # under the shoe
v, t, a, _ = cut(V, T, f_skin, D)
sj, sw = top4(a)
parts += split(part(v, t, sj, sw, 'skin'), 0.168 - v[:, 1], 'sock')

write('tim', parts, J2, B['frames'], extra=dict(stripes=dict(y0=0.5, period=0.034, width=0.42, top=0.79), sockBand=[0.148, 0.158]))
