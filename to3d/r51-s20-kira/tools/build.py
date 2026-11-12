"""Кира (С20, Soviet animation of the 60–70s) in 3D: the pack the drawing renderer (web/kira.js, web/kit.js) takes.
  python3 build.py [outdir]

The style's people are caricature: one bold shape for the body, one for the head. So the form is built straight from
the numbers of the drawing's own code (styles/s20-soviet/tools/kira.py: the hoodie's front and side silhouettes, the
head's rows and profile, hair, legs, sleeves, boots) as lofted shells, in the drawing's units (feet at 0, y up), and
set on the engine's skeleton:
  * the skeleton is SOMA's 77 joints with moood-woman's rest frames (engine/data/bodies/moood-woman). Its rest (arms
    out, legs apart) is posed into the drawing's standing pose — arms hanging, legs straight — and that pose is baked
    as this body's rest: every joint's frame is turned with its bone, so Kimodo's turns still mean the same;
  * the slouch (the top forward and down, the head forward, nose down) is in the places of the joints and the form
    only, not in the frames — so it rides along in every motion (engine/src/retarget.js);
  * weights are written by rule: the bag by height on the spine, sleeves and legs along their bones, the rest rigid.
For the renderer: grp (which paint a vertex takes), edges (each once with its triangles: silhouettes and open edges are
found from them), the face grid (head units → a point on the head), strokes (lines that belong to the form).
"""
import os, sys, json
import numpy as np
import pack, mesh as M

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data')
os.makedirs(OUT, exist_ok=True)

K = 1.60 / 428            # drawing units → metres (the crown at 428 units: 1.60 m)
HS = 1.05                 # the head's scale in the figure (kira.py place_head)
SL = 0.7                  # the slouch of the standing figure (kira.py figure(): 0.7)
smooth = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))


def slouch(P):
    """kira.py hoodie(): the top goes forward and down, the back rounds."""
    P = np.array(P, float)
    t = np.clip((P[..., 1] - 158) / 170, 0, None)
    P[..., 2] += SL * t * t * 30
    P[..., 1] -= SL * t * 8
    return P


def catmull(pts, n):
    pts = np.asarray(pts, float); P = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]]); out = []
    for i in range(1, len(P) - 2):
        for s in np.linspace(0, 1, n, endpoint=False):
            p0, p1, p2, p3 = P[i - 1:i + 3]
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-2]); return np.array(out)


# ---------------------------------------------------------------- quaternions (x, y, z, w), as the engine's
def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz])


def qrot(q, v):
    u = np.array(q[:3]); w = q[3]; v = np.asarray(v, float)
    return v + 2 * np.cross(u, np.cross(u, v) + w * v)


def qbetween(a, b):
    a = np.asarray(a, float) / np.linalg.norm(a); b = np.asarray(b, float) / np.linalg.norm(b)
    c = np.cross(a, b); d = a @ b
    q = np.array([c[0], c[1], c[2], 1 + d]); return q / np.linalg.norm(q)


# ---------------------------------------------------------------- the skeleton: SOMA, posed into the drawing's stand
sk = pack.skeleton(); NAMES = [j['name'] for j in sk['joints']]; I = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in sk['joints']]); NJ = len(NAMES)
h0, a0, th0, t0 = pack.body('moood-woman')
J0 = a0['joints'].reshape(-1, 3).astype(float); F0 = a0['frames'].reshape(-1, 4).astype(float)

RW = np.tile([0, 0, 0, 1.0], (NJ, 1))        # each joint's turn from moood-woman's rest to this body's rest
J1 = np.zeros((NJ, 3))                       # places, drawing units
ARM = 43
PLACE = {'Hips': (0, 170, 0), 'Spine1': slouch((0, 200, 0)), 'Spine2': slouch((0, 235, 0)), 'Chest': slouch((0, 270, 0)),
         'Neck1': (0, 316, 25), 'Neck2': (0, 328, 27), 'Head': (0, 338, 27), 'HeadEnd': (0, 420, 33), 'Jaw': (0, 336, 45),
         'LeftEye': (13.6, 361, 74), 'RightEye': (-13.6, 361, 74)}
for s, sg in (('Left', 1), ('Right', -1)):
    PLACE[s + 'Shoulder'] = (sg * 5, 296, 14); PLACE[s + 'Arm'] = (sg * ARM, 302, 15)
    PLACE[s + 'Leg'] = (sg * 13, 166, 1)
# bones aimed as the drawing stands: (joint, child) → direction; and their lengths (units)
AIM = {}
for s, sg in (('Left', 1), ('Right', -1)):
    AIM[s + 'Arm'] = (s + 'ForeArm', (sg * 11, -58, 5), 59); AIM[s + 'ForeArm'] = (s + 'Hand', (sg * -2, -58, -3), 58)
    AIM[s + 'Hand'] = (s + 'HandMiddle1', (sg * -1, -10, 0.5), None)
    AIM[s + 'Leg'] = (s + 'Shin', (0, -1, 0), 80); AIM[s + 'Shin'] = (s + 'Foot', (0, -1, 0), 73)
    AIM[s + 'Foot'] = (s + 'ToeBase', (0, -9, 14), 16.6)
HANDK = 0.86 / K          # finger bones: moood-woman's, a little smaller (metres → units)
for j in range(NJ):
    n, p = NAMES[j], PARENT[j]
    if p >= 0: RW[j] = RW[p]
    if n in PLACE: J1[j] = PLACE[n]
    else:
        off = qrot(RW[p], J0[j] - J0[p])
        pn = NAMES[p]
        if pn in AIM and AIM[pn][0] == n and AIM[pn][2]: off = off / np.linalg.norm(off) * AIM[pn][2]
        elif 'Hand' in pn: off = off * HANDK
        elif 'Toe' in pn: off = off / np.linalg.norm(off) * 9
        else: off = off / K
        J1[j] = J1[p] + off
    if n in AIM:
        c = I[AIM[n][0]]
        RW[j] = qmul(qbetween(qrot(RW[j], J0[c] - J0[j]), AIM[n][1]), RW[j])
FR = np.array([qmul(RW[j], F0[j]) for j in range(NJ)])
FR /= np.linalg.norm(FR, axis=1, keepdims=True)


def under(j):
    out, st = [], [j]
    while st:
        k = st.pop(); out.append(k); st += list(np.where(PARENT == k)[0])
    return out


# ---------------------------------------------------------------- lofted shells
def ring(a, zc, df, db, th, p=2.4):
    s, c = np.sin(th), np.cos(th)
    x = a * np.sign(s) * np.abs(s) ** (2 / p)
    z = zc + np.where(c > 0, df, db) * np.sign(c) * np.abs(c) ** (2 / p)
    return x, z


def loft(rows, cols=64, p=2.4, cap0=None, cap1=None):
    """rows: (y, a, zc, df, db). A row with a ≈ 0 is one vertex (a pole); cap0 / cap1: close an open end with a fan."""
    V, T, idx = [], [], []
    th = np.linspace(0, 2 * np.pi, cols, endpoint=False)
    for (y, a, zc, df, db) in rows:
        if a < 1e-6: idx.append([len(V)]); V.append([0, y, zc]); continue
        x, z = ring(a, zc, df, db, th, p)
        idx.append(list(range(len(V), len(V) + cols))); V += list(np.c_[x, np.full(cols, y), z])
    for r in range(len(rows) - 1):
        A, B = idx[r], idx[r + 1]
        for c in range(cols):
            c1 = (c + 1) % cols
            if len(A) == 1 and len(B) == 1: continue
            if len(A) == 1: T.append([A[0], B[c], B[c1]])
            elif len(B) == 1: T.append([A[c], B[0], A[c1]])
            else: T += [[A[c], B[c], A[c1]], [A[c1], B[c], B[c1]]]
    for cap, r in ((cap0, 0), (cap1, len(rows) - 1)):
        if cap is None or len(idx[r]) == 1: continue
        y, a, zc, df, db = rows[r]
        k = len(V); V.append([0, y + cap, zc + (df - db) / 2])
        for c in range(cols): T.append([idx[r][c], idx[r][(c + 1) % cols], k])
    return np.array(V, float), np.array(T), idx


def tube(path, radii, cols=28):
    path = np.asarray(path, float); V = []
    ref = np.array([0, 0, 1.0])
    for i, pt in enumerate(path):
        tg = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]; tg /= np.linalg.norm(tg)
        n1 = ref - tg * (ref @ tg); n1 /= np.linalg.norm(n1); n2 = np.cross(tg, n1)
        for th in np.linspace(0, 2 * np.pi, cols, endpoint=False):
            V.append(pt + radii[i] * (np.cos(th) * n1 + np.sin(th) * n2))
    T = []
    for r in range(len(path) - 1):
        for c in range(cols):
            a_, a1 = r * cols + c, r * cols + (c + 1) % cols
            T += [[a_, a_ + cols, a1], [a1, a_ + cols, a1 + cols]]
    return np.array(V), np.array(T)


def ellipsoid(c, r, rows=14, cols=24, R=None):
    V = [[0, 1, 0]]; T = []
    for i in range(1, rows):
        ph = np.pi * i / rows
        for k in range(cols):
            a = 2 * np.pi * k / cols; V.append([np.sin(ph) * np.sin(a), np.cos(ph), np.sin(ph) * np.cos(a)])
    V.append([0, -1, 0]); n = len(V)
    for k in range(cols):
        k1 = (k + 1) % cols
        T.append([0, 1 + k, 1 + k1]); T.append([n - 1, 1 + (rows - 2) * cols + k1, 1 + (rows - 2) * cols + k])
        for i in range(rows - 2):
            a_, a1, b_, b1 = 1 + i * cols + k, 1 + i * cols + k1, 1 + (i + 1) * cols + k, 1 + (i + 1) * cols + k1
            T += [[a_, b_, a1], [a1, b_, b1]]
    V = np.array(V) * np.asarray(r, float)
    if R is not None: V = V @ np.asarray(R).T
    return V + np.asarray(c, float), np.array(T)


def outward(V, T):
    n = M.tri_normals(V, T); c = V[T].mean(1)
    return T if (n * (c - V.mean(0))).sum() > 0 else T[:, ::-1]


def W_of(n, **kw):
    """Weights from named columns: W_of(n, Hips=array, Chest=array …)."""
    W = np.zeros((n, NJ))
    for k, v in kw.items(): W[:, I[k]] = v
    return W


def chain_w(t, joints, nodes, soft):
    """Weights along a chain: t — a number per vertex, nodes — where each next joint takes over, soft — over what span."""
    W = np.zeros((len(t), NJ)); rest = np.ones(len(t))
    for j, nd in zip(joints[::-1], list(nodes[::-1]) + [None]):
        w = rest if nd is None else rest * smooth((t - nd) / soft + 0.5)
        W[:, I[j]] += w; rest = rest - w
    return W


pieces = []          # (name, V units, T, W, group)
G = dict(skin=1, hair=2, hoodie=3, trousers=4, boot=5, lime=6, dark=7)

# ---------------------------------------------------------------- the hoodie: one bag (kira.py hoodie(): front f, side s)
BAG_F = [(0, 158), (24, 160), (46, 168), (44, 200), (47, 270), (44, 312), (20, 326), (0, 327)]      # half-width
BAG_ZF = [(0, 158), (16, 160), (34, 168), (32, 200), (36, 270), (30, 312), (14, 326), (0, 327)]     # to the front
BAG_ZB = [(0, 158), (16, 160), (30, 168), (30, 200), (40, 270), (36, 312), (14, 328), (0, 328)]     # to the back
bf, bzf, bzb = catmull(BAG_F, 7), catmull(BAG_ZF, 7), catmull(BAG_ZB, 7)
bag_rows = [(bf[i, 1], max(bf[i, 0], 0), (bzf[i, 0] - bzb[i, 0]) / 2, (bzf[i, 0] + bzb[i, 0]) / 2, (bzf[i, 0] + bzb[i, 0]) / 2)
            for i in range(len(bf))]
bag_rows[0] = (158, 0, 0, 0, 0); bag_rows[-1] = (327.5, 0, 0, 0, 0)
BAG_P = 2.4
BV, BT, _ = loft(bag_rows, 72, BAG_P)
bag_y = BV[:, 1].copy()


def bag_w(y):
    return chain_w(y, ['Hips', 'Spine1', 'Spine2', 'Chest'], [192, 222, 256], 34)


pieces.append(('hoodie', slouch(BV), BT, bag_w(bag_y), G['hoodie']))


def bag_at(x, y, lift=0.6):
    """A point on the bag's front at drawing (x, y) — for the pocket and the strings."""
    r = np.array(bag_rows); o = np.argsort(r[:, 0])
    a, zc, df = [np.interp(y, r[o, 0], r[o, k]) for k in (1, 2, 3)]
    s = np.clip(abs(x) / a, 0, 1) ** (BAG_P / 2); c = np.sqrt(1 - s * s)
    return slouch([x, y, zc + (df + lift) * c ** (2 / BAG_P)])


# ---------------------------------------------------------------- the hood: a lump behind the neck; the neck
HV, HT = ellipsoid((0, 327, 3), (27, 17, 22), 12, 28)
pieces.append(('hood', HV, HT, W_of(len(HV), Chest=1), G['hoodie']))
NV_, NT_, _ = loft([(y, 5.6, 26.5 + (y - 310) * 0.05, 5.6, 5.6) for y in np.linspace(308, 346, 6)], 20, 2.0)
pieces.append(('neck', NV_, NT_, chain_w(NV_[:, 1], ['Chest', 'Neck1', 'Neck2', 'Head'], [314, 324, 336], 8), G['skin']))

# ---------------------------------------------------------------- sleeves and hands
strokes = []          # lines that belong to the form: dict(kind, lw, color, pts (units), W)
for s, sg in (('Left', 1), ('Right', -1)):
    A_, E_, H_ = J1[I[s + 'Arm']], J1[I[s + 'ForeArm']], J1[I[s + 'Hand']]
    d1 = (E_ - A_) / np.linalg.norm(E_ - A_); d2 = (H_ - E_) / np.linalg.norm(H_ - E_)
    path = catmull([A_ - d1 * 3, A_ + (E_ - A_) * 0.5, E_, E_ + (H_ - E_) * 0.5, H_ + d2 * 2], 8)
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    radii = np.interp(L / L[-1], [0, 0.08, 1.0], [8.0, 9.2, 7.6])
    V_, T_ = tube(path, radii)
    t = np.repeat(L, 28)
    W = chain_w(t, [s + 'Arm', s + 'ForeArm'], [np.linalg.norm(E_ - A_) + 3], 22)
    pieces.append(('sleeve' + s, V_, T_, W, G['hoodie']))
    # the hand: a mitten as drawn (body.py hand 'rest': fingers together, a small thumb), rigid on the hand
    tip = J1[I[s + 'HandMiddleEnd']]
    d = tip - H_; d /= np.linalg.norm(d)
    acr = J1[I[s + 'HandIndex1']] - J1[I[s + 'HandPinky1']]; acr -= d * (acr @ d); acr /= np.linalg.norm(acr)
    nrm_ = np.cross(d, acr) * sg
    Lh, rows_, cols_ = 25.0, 22, 20
    V_ = []
    for uu in np.linspace(-0.12, 1.0, rows_):
        tip_r = max(0.08, np.sqrt(max(0.0, 1 - max(0.0, (uu - 0.5) / 0.5) ** 2)))
        a_ = 7.4 * tip_r * (0.8 + 0.2 * smooth((uu + 0.1) / 0.3)); b_ = 4.0 * tip_r
        thumb = 3.2 * np.exp(-((uu - 0.3) / 0.14) ** 2)
        for th in np.linspace(0, 2 * np.pi, cols_, endpoint=False):
            x_ = a_ * np.cos(th) + thumb * max(np.cos(th), 0) ** 2; z_ = b_ * np.sin(th)
            V_.append(H_ + d * uu * Lh + acr * x_ + nrm_ * z_)
    V_ = np.array(V_)
    T_ = []
    for r in range(rows_ - 1):
        for c in range(cols_):
            a_, a1 = r * cols_ + c, r * cols_ + (c + 1) % cols_
            T_ += [[a_, a_ + cols_, a1], [a1, a_ + cols_, a1 + cols_]]
    pieces.append(('hand' + s, V_, np.array(T_), W_of(len(V_), **{s + 'Hand': 1}), G['skin']))
    # two finger lines on the back of the hand (the side away from the body)
    for off in (-0.28, 0.25):
        pts = [H_ + d * uu * Lh + acr * 7.4 * off + nrm_ * 4.3 * (1 if True else -1) for uu in np.linspace(0.5, 0.86, 4)]
        strokes.append(dict(kind='finger', lw=1.1, color=None, pts=np.array(pts), W=W_of(4, **{s + 'Hand': 1})))
        pts = [H_ + d * uu * Lh + acr * 7.4 * off - nrm_ * 4.3 for uu in np.linspace(0.5, 0.86, 4)]
        strokes.append(dict(kind='finger', lw=1.1, color=None, pts=np.array(pts), W=W_of(4, **{s + 'Hand': 1})))

# ---------------------------------------------------------------- legs and boots
LIME = '#c9e03b'
for s, sg in (('Left', 1), ('Right', -1)):
    Hp, Kn, An = J1[I[s + 'Leg']], J1[I[s + 'Shin']], J1[I[s + 'Foot']]
    path = np.array([Hp + [0, 12, 0]] + [Hp + (Kn - Hp) * u for u in np.linspace(0, 1, 9)] + [Kn + (An - Kn) * u for u in np.linspace(0, 1, 9)[1:]])
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    radii = np.interp(path[:, 1], [20, 86, 170], [6.4, 7.4, 8.6])
    V_, T_ = tube(path, radii, 24)
    W = chain_w(-np.repeat(path[:, 1], 24), [s + 'Leg', s + 'Shin'], [-Kn[1]], 26)
    pieces.append(('leg' + s, V_, T_, W, G['trousers']))
    # the boot (body.py shoe 'boot' × 1.45): a heavy shoe with a shaft; the front view's width, the side view's outline
    bx, bz = An[0], An[2]
    rows = [(0.0, 8.0, 24.0, -11.5), (1.6, 9.2, 25.4, -12.3), (6.0, 9.2, 24.6, -12.4), (9.5, 8.8, 19.0, -12.2),
            (12.5, 8.4, 11.5, -11.8), (16.0, 8.2, 8.8, -11.2), (20.0, 8.2, 7.8, -10.8), (23.4, 8.2, 7.6, -10.6)]
    rr = np.array(rows); ys = np.r_[np.linspace(0, 12.5, 12), np.linspace(14, 23.4, 6)]
    brows = [(y, np.interp(y, rr[:, 0], rr[:, 1]), bz + (np.interp(y, rr[:, 0], rr[:, 2]) + np.interp(y, rr[:, 0], rr[:, 3])) / 2,
              (np.interp(y, rr[:, 0], rr[:, 2]) - np.interp(y, rr[:, 0], rr[:, 3])) / 2,
              (np.interp(y, rr[:, 0], rr[:, 2]) - np.interp(y, rr[:, 0], rr[:, 3])) / 2) for y in ys]
    V_, T_, idx = loft(brows, 40, 3.0, cap0=0.0, cap1=0.0)
    V_[:, 0] += bx
    wt = smooth((V_[:, 2] - bz - 9) / 9) * smooth((11 - V_[:, 1]) / 4)
    pieces.append(('boot' + s, V_, T_, W_of(len(V_), **{s + 'Foot': 1 - wt, s + 'ToeBase': wt}), G['boot']))
    # lime laces: two short lines across the front of the shaft
    for y in (19.0, 13.5):
        a_, zc, df = [np.interp(y, [r[0] for r in brows], [r[k] for r in brows]) for k in (1, 2, 3)]
        th = np.linspace(-0.75, 0.75, 6); x, z = ring(a_ + 0.5, zc, df + 0.5, df, th, 3.0)
        strokes.append(dict(kind='lace', lw=1.7, color=LIME, pts=np.c_[x + bx, np.full(6, y) - x * sg * 0.12, z],
                            W=W_of(6, **{s + 'Foot': 1})))

# ---------------------------------------------------------------- the head (face.py Head: rows, the profile's face line)
ROWS = [(-56, 29), (-46, 36), (-26, 39), (-4, 38), (16, 32), (29, 24), (38, 14), (44, 5)]
TOP, BOT = ROWS[0][0] - 3, ROWS[-1][0] + 2.5
ol = catmull([(0, TOP)] + [(w, y) for y, w in ROWS] + [(0, BOT)], 6)
FACE_Z = np.array([(-59, 12), (-57, 22.6), (-46, 31), (-33, 37.8), (-13, 42.5), (-3, 40.3), (15, 40.5), (30, 40.5), (40, 40), (44, 35), (46.5, 30)])
BACK_Z = np.array([(-59, -8), (-56, -27.3), (-46, -34.9), (-26, -38.1), (-4, -37), (6, -36), (16, -29), (29, -11), (38, 7), (44, 21), (46.5, 28)])
hrows = []
for w, y in ol:
    w = max(w, 0.0); zf = np.interp(y, FACE_Z[:, 0], FACE_Z[:, 1]); zb = np.interp(y, BACK_Z[:, 0], BACK_Z[:, 1])
    if y < -56: k = (w / 29) ** 0.7; zf, zb = 4 + (zf - 4) * k, 4 + (zb - 4) * k
    if y > 44: k = w / 5; zf, zb = 29 + (zf - 29) * k, 29 + (zb - 29) * k
    hrows.append((y, w, (zf + zb) / 2, (zf - zb) / 2, (zf - zb) / 2))
hrows[0] = (TOP, 0, 4, 0, 0); hrows[-1] = (BOT, 0, 29, 0, 0)
HEAD_P = 2.5
HDV, HDT, _ = loft(hrows, 72, HEAD_P)            # head units: x, y down, z to the front

HEAD_C = np.array([0, 357.6, 31.2]); TILT = np.radians(8 * SL)


def head_place(V):
    """Head units (x, y down, z front) → the figure: scaled, nose down by the slouch's tilt, set on the neck."""
    x, y, z = V[:, 0] * HS, -V[:, 1] * HS, V[:, 2] * HS
    c, s = np.cos(TILT), np.sin(TILT)
    return np.c_[x, y * c - z * s, z * c + y * s] + HEAD_C


HDT = outward(head_place(HDV), HDT)
pieces.append(('head', head_place(HDV), HDT, W_of(len(HDV), Head=1), G['skin']))
for sg in (1, -1):
    EV, ET = ellipsoid((sg * 38.5, 4, -4), (5.6, 7.4, 5.2), 10, 16)
    pieces.append(('ear' + ('L' if sg > 0 else 'R'), head_place(EV), ET, W_of(len(EV), Head=1), G['skin']))
    # the ear's inner mark
    pts = [(sg * 38.5 + sg * 5.9 * np.cos(b) * np.cos(a), 4 + 7.6 * np.sin(b), -4 + 5.5 * np.cos(b) * np.sin(a))
           for a, b in ((0.9, -0.55), (0.45, 0.0), (0.9, 0.5))]
    strokes.append(dict(kind='ear', lw=1.3, color=None, pts=head_place(np.array(pts)), W=W_of(3, Head=1)))

# the face grid: head units (front view) → a point on the head
GX = np.arange(-44, 45, 2.0); GY = np.arange(-62, 51, 2.0)
gx, gy = np.meshgrid(GX, GY); q = np.c_[gx.ravel(), gy.ravel()]
faceTri = -np.ones(len(q), np.int64); faceBar = np.zeros((len(q), 3)); best = np.full(len(q), -1e9)
A3, B3, C3 = HDV[HDT[:, 0]], HDV[HDT[:, 1]], HDV[HDT[:, 2]]
for ti in range(len(HDT)):
    if min(A3[ti, 2], B3[ti, 2], C3[ti, 2]) < 0: continue
    a2, b2, c2 = A3[ti, :2], B3[ti, :2], C3[ti, :2]
    lo = np.minimum(np.minimum(a2, b2), c2); hi = np.maximum(np.maximum(a2, b2), c2)
    m = np.flatnonzero((q[:, 0] >= lo[0]) & (q[:, 0] <= hi[0]) & (q[:, 1] >= lo[1]) & (q[:, 1] <= hi[1]))
    if not len(m): continue
    v0, v1 = b2 - a2, c2 - a2; den = v0[0] * v1[1] - v1[0] * v0[1]
    if abs(den) < 1e-12: continue
    w = q[m] - a2
    l1 = (w[:, 0] * v1[1] - v1[0] * w[:, 1]) / den; l2 = (v0[0] * w[:, 1] - w[:, 0] * v0[1]) / den; l0 = 1 - l1 - l2
    ok = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
    m, l0, l1, l2 = m[ok], l0[ok], l1[ok], l2[ok]
    z = l0 * A3[ti, 2] + l1 * B3[ti, 2] + l2 * C3[ti, 2]
    better = z > best[m]
    m, z = m[better], z[better]
    best[m] = z; faceTri[m] = ti; faceBar[m] = np.c_[l0[better], l1[better], l2[better]]
print('face grid', len(q), 'on the head', (faceTri >= 0).sum())

# ---------------------------------------------------------------- the hair: one dark mass, a choppy edge (kira.py hair())
HW = np.array([(-67, 0), (-65, 16), (-62, 27), (-58, 34), (-48, 41), (-36, 44.5), (-6, 45), (14, 42.5), (24, 38)])
HZF = np.array([(-67, 2), (-65, 16), (-62, 27), (-58, 35), (-50, 42), (-42, 46), (-24, 48), (0, 47), (24, 45)])
HZB = np.array([(-67, 2), (-65, -16), (-62, -30), (-58, -40), (-50, -50), (-30, -56), (8, -56), (22, -46), (24, -42)])
HAIR_P = 2.3
# the edge: (angle round the head in degrees, 0 — the front, + — her left; y) — the front drawing's fringe (long over her
# right temple), up over the ears, locks behind them, the nape
HEM = [(-180, 21), (-170, 16), (-158, 22), (-146, 13), (-133, 19), (-124, 8), (-116, 15), (-109, 13), (-103, -10),
       (-97, -20), (-88, -23), (-80, -22), (-62, -27), (-55, -26), (-50, -12), (-43, 4), (-34, -6), (-24, -16), (-7.9, -30),
       (3.5, -22), (17.7, -32), (32, -22), (46.5, -34), (77, -28), (86, -24), (97, -21), (103, -10), (109, 13), (116, 15),
       (124, 8), (133, 19), (146, 13), (158, 22), (170, 16), (180, 21)]
HEM = np.array(HEM)


def hair_pt(th, y, lift=0.0):
    hw, zf, zb = np.interp(y, HW[:, 0], HW[:, 1]), np.interp(y, HZF[:, 0], HZF[:, 1]), np.interp(y, HZB[:, 0], HZB[:, 1])
    x, z = ring(hw + lift, (zf + zb) / 2, (zf - zb) / 2 + lift, (zf - zb) / 2 + lift, np.asarray(th, float), HAIR_P)
    return np.c_[x, np.broadcast_to(y, np.shape(x)), z] if np.ndim(x) else np.array([x, y, z])


HC, HR = 200, 24
ths = np.linspace(-np.pi, np.pi, HC, endpoint=False)
hems = np.interp(np.degrees(ths), HEM[:, 0], HEM[:, 1])
V_ = [[0, -67, 2]]
for r in range(1, HR):
    v = (r / (HR - 1)) ** 1.25
    y = -67 + (hems + 67) * v
    V_ += list(hair_pt(ths, y))
V_ = np.array(V_); T_ = []
for c in range(HC):
    c1 = (c + 1) % HC
    T_.append([0, 1 + c1, 1 + c])
    for r in range(HR - 2):
        a_, a1, b_, b1 = 1 + r * HC + c, 1 + r * HC + c1, 1 + (r + 1) * HC + c, 1 + (r + 1) * HC + c1
        T_ += [[a_, a1, b_], [a1, b1, b_]]
pieces.append(('hair', head_place(V_), np.array(T_), W_of(len(V_), Head=1), G['hair']))
# a light line down the hair, as the drawing's
hl = catmull([(0, -57), (-12, -37), (-19, -19)], 5)
pts = np.array([hair_pt(np.arcsin(np.clip(abs(x) / np.interp(y, HW[:, 0], HW[:, 1]), 0, 1) ** (HAIR_P / 2)) * np.sign(x), y, 0.5) for x, y in hl])
strokes.append(dict(kind='shine', lw=1.2, color='#6c5a6a', pts=head_place(pts), W=W_of(len(pts), Head=1)))

# ---------------------------------------------------------------- headphones round the neck (lime), the pocket, the strings
for sg in (1, -1):
    ax = np.array([sg * 0.72, 0.0, 0.69]); up = np.array([0, 1.0, 0]); sd = np.cross(up, ax)
    R = np.c_[sd, up, ax]                       # the cup: a thick disc looking out and forward
    c = np.array([sg * 24, 317, 36.0])
    V_, T_ = ellipsoid(c, (9.2, 10.4, 4.8), 10, 20, R)
    pieces.append(('cup' + ('L' if sg > 0 else 'R'), V_, T_, W_of(len(V_), Chest=0.5, Neck1=0.5), G['lime']))
    DV = [c + ax * 5.1]; DT = []
    for k in range(16):
        a = 2 * np.pi * k / 16; DV.append(c + ax * 5.0 + sd * 4.0 * np.cos(a) + up * 4.6 * np.sin(a))
        DT.append([0, 1 + k, 1 + (k + 1) % 16])
    pieces.append(('cupDark' + ('L' if sg > 0 else 'R'), np.array(DV), np.array(DT), W_of(17, Chest=0.5, Neck1=0.5), G['dark']))
band = catmull([(-22, 311, 41), (-11, 306, 48), (0, 304, 51), (11, 306, 48), (22, 311, 41)], 4)
strokes.append(dict(kind='band', lw=3.0, color=LIME, pts=band, W=W_of(len(band), Chest=1)))
strokes.append(dict(kind='band', lw=1.0, color=None, pts=band + [0, -1.0, 0.3], W=W_of(len(band), Chest=1)))
pk = catmull([(-26, 196), (-18, 220), (18, 220), (26, 196)], 6)
pts = np.array([bag_at(x, y) for x, y in pk])
strokes.append(dict(kind='pocket', lw=1.6, color=None, pts=pts, W=bag_w(pk[:, 1])))
for x0, y0, x1, y1 in ((-6, 312, -8, 276), (5, 312, 6, 282)):
    pts = np.array([bag_at(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, 1.0) for u in np.linspace(0, 1, 5)])
    strokes.append(dict(kind='string', lw=1.2, color='#d8cbd4', pts=pts, W=bag_w(np.linspace(y0, y1, 5))))

# ---------------------------------------------------------------- one pack
Vs, Ts, Ws, grp, pid = [], [], [], [], []
base = 0; tbase = 0; ranges = {}; tranges = {}
for i, (name, V, T, W, g) in enumerate(pieces):
    T = outward(V, T)
    Vs.append(V); Ts.append(T + base); Ws.append(W); grp.append(np.full(len(V), g)); pid.append(np.full(len(V), i))
    ranges[name] = [base, base + len(V)]; tranges[name] = [tbase, tbase + len(T)]; base += len(V); tbase += len(T)
st_out = []
for s in strokes:
    n = len(s['pts']); Vs.append(s['pts']); Ws.append(s['W']); grp.append(np.zeros(n)); pid.append(np.full(n, 255))
    st_out.append(dict(kind=s['kind'], lw=s['lw'], color=s['color'], v=list(range(base, base + n)))); base += n
V = np.vstack(Vs) * K; T = np.vstack(Ts); W = np.maximum(np.vstack(Ws), 0); N = len(V)
assert abs(V[np.unique(T), 1].min()) < 1e-6
order = np.argsort(-W, 1)[:, :4]
SJ = order.astype(np.uint8); SW = np.take_along_axis(W, order, 1); SW /= SW.sum(1, keepdims=True)

e = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
f = np.tile(np.arange(len(T)), 3)
key = np.sort(e, 1); o = np.lexsort((key[:, 1], key[:, 0])); key, f = key[o], f[o]
first = np.r_[True, (key[1:] != key[:-1]).any(1)]
idx = np.flatnonzero(first); cnt = np.diff(np.r_[idx, len(key)])
E = key[idx]; F0_ = f[idx]; F1_ = np.where(cnt >= 2, f[np.minimum(idx + 1, len(f) - 1)], -1)
print('edges', len(E), 'open', (F1_ < 0).sum(), 'more than two', (cnt > 2).sum())
# open edges that are not lines: the tubes' ends inside the bag and the boots (the cuff's end is a line)
PN = [p[0] for p in pieces]; vp = np.concatenate(pid).astype(int)
drop = np.zeros(len(E), bool)
for k in np.flatnonzero(F1_ < 0):
    n = PN[vp[E[k, 0]]]
    y = V[E[k, 0], 1] / K
    if n.startswith('leg') or n == 'neck' or n.startswith('hand'): drop[k] = True
    if n.startswith('sleeve') and y > 250: drop[k] = True

header = dict(format='r51/character', version=1, id='kira-s20', label={'ru': 'Кира, советская мультипликация'},
              skinning='dqs', source='shells lofted from the numbers of styles/s20-soviet/tools/kira.py on SOMA (moood-woman rest frames, posed)',
              pieces=ranges, trianglePieces=tranges, pieceNames=PN, groups=G, unit=K, headScale=HS,
              face=dict(gx=[float(GX[0]), 2.0, len(GX)], gy=[float(GY[0]), 2.0, len(GY)], tri0=tranges['head'][0]),
              strokes=st_out)
pack.save(os.path.join(OUT, 'kira.json'), header, dict(
    positions=V.astype(np.float32).ravel(), triangles=T.astype(np.uint32).ravel(),
    skinJoints=SJ, skinWeights=SW.astype(np.float32),
    joints=(J1 * K - [0, 0, 0]).astype(np.float32).ravel(), frames=FR.astype(np.float32).ravel(),
    grp=np.concatenate(grp).astype(np.uint8), pid=np.concatenate(pid).astype(np.uint8),
    edges=E.astype(np.uint32).ravel(), edgeTris=np.where(np.c_[F0_, F1_] < 0, 0xFFFFFFFF, np.c_[F0_, F1_]).astype(np.uint32).ravel(),
    edgeDrop=drop.astype(np.uint8),
    faceTri=np.where(faceTri < 0, 0xFFFFFFFF, faceTri + tranges['head'][0]).astype(np.uint32), faceBar=faceBar.astype(np.float32).ravel()))
print('saved', OUT, N, 'vertices', len(T), 'triangles', {k: v[1] - v[0] for k, v in ranges.items()})
