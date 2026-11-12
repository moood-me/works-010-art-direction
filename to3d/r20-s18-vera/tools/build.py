"""Вера (С18, black-and-white manga) in 3D: the pack the drawing renderer (web/vera.js) takes.
  python3 build.py            → ../data/vera.json|bin

Bases:
- body, arms, hands, legs, the SOMA skeleton and weights — Anny `moood-woman` (engine/data), made slimmer and
  longer-legged toward the drawing's figure (the way is Р7's: joint moves and per-joint affines; frames untouched);
- the head — the drawing's own 3D head (styles/s18-manga/tools/head.py: cross-sections changed by zones in
  chars/vera.py, the nose wedge, the lips' bump) lofted into a mesh, so the silhouette in every view is the drawing's;
  ears as the drawing's ear plates; the neck as the drawing's neck rings;
- hair — the drawing's shell (hair.py `Hair.shell`, `shell_ray`): a grid whose columns are the drawing's strands from
  the hairline to the bun; the bun a ball;
- the long coat — Anny's trunk and arms pushed out (cloth), below the hips a lofted shell to the hem (Р7's skirt);
  the blouse's stand collar a ring; shoes lofted (Р7's); a folder for the drawn pose.
What a pen-and-tone renderer needs instead of materials: `grp` (which tone a vertex has), `rp` (rest position: the
coat's opening, blouse and lapels are found from it per pixel), edges with their triangles, `inner` (where a contour of
skin over skin is a line of this drawing), `jawk` (how much a vertex follows the open jaw), curves on the surface
(the coat's edges and lapels, the white streaks of the hair), four marker points that carry the head's frame.
Units: metres; head units (crown to chin ≈ 1; y down from the eye line; z to the viewer) map as
world = (x·KH, EYE − y·KH, z·KH + ZOFF)."""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STY = os.path.join(HERE, '..', '..', '..', 'styles', 's18-manga', 'tools')
sys.path.insert(0, HERE); sys.path.insert(1, STY)
import pack, mesh as M                      # noqa: E402
from head import Head, interp_table         # noqa: E402
from chars import vera as CH                # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data')
os.makedirs(OUT, exist_ok=True)
sm = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))

TALL = 1.72
KB = TALL / 7.39                             # the body's unit (body3d: a figure of HEIGHT 7.5 is 7.39 with its head on)
KH = 1.08 * KB                               # the head's unit: figure.py draws the head 1.08 of the body's
NECK_Y = 1.423                               # the neck's base on the body (the collar sits here)
EYE = NECK_Y + 0.012 + 0.60 * KH             # body3d.head3d: the eye line is 0.6 of a head over the pit of the neck
FOLD_OFF = float(os.environ.get('FOLD_OFF', '0.02'))
G = dict(skin=1, hair=2, coat=3, leg=4, shoe=5, blouse=6, folder=7)

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
S = TALL / 1.585


def under(j):
    out, st = [], [j]
    while st:
        k = st.pop(); out.append(k); st += list(np.where(PARENT == k)[0])
    return out


LEG = 1.04                                   # the drawing's legs are long (the crotch at 0.47 of the height)
J1 = J0 * S
lift = J0[I['Hips'], 1] * S * (LEG - 1)
for s, sg in (('Left', 1), ('Right', -1)):
    for j in under(I[s + 'Leg']):
        J1[j, 1] = J0[I[s + 'Leg'], 1] * S + lift + (J0[j, 1] - J0[I[s + 'Leg'], 1]) * S * LEG
        J1[j] += [-sg * 0.034, 0, 0]
for j in range(NJ):
    if j not in under(I['LeftLeg']) and j not in under(I['RightLeg']):
        J1[j, 1] += lift * (1 - sm((J0[j, 1] * S - 1.0) / 0.45))
for s, sg in (('Left', 1), ('Right', -1)):   # narrow shoulders
    for j in under(I[s + 'Shoulder']): J1[j] += [-sg * 0.004, -0.004, 0]
    for j in under(I[s + 'Arm']): J1[j] += [-sg * 0.040, -0.008, 0]


def joint_affine(j):
    n = NAMES[j]
    if n in ('Hips',): return np.diag([0.74, 1, 0.84])
    if n in ('Spine1', 'Spine2'): return np.diag([0.78, 1, 0.84])
    if n in ('Chest',): return np.diag([0.80, 1, 0.84])
    if n.endswith('Shoulder'): return np.diag([0.78, 0.9, 0.86])
    r = {'LeftArm': 0.76, 'RightArm': 0.76, 'LeftForeArm': 0.78, 'RightForeArm': 0.78,
         'LeftLeg': 0.78, 'RightLeg': 0.78, 'LeftShin': 0.8, 'RightShin': 0.8}.get(n)
    if r:
        c = [k for k in range(NJ) if PARENT[k] == j][0]
        d = J0[c] - J0[j]; d /= np.linalg.norm(d)
        ax = r * np.eye(3) + (1 - r) * np.outer(d, d)
        if 'Leg' in n or 'Shin' in n: ax = ax + (LEG - 1) * np.outer(d, d)
        return ax
    if 'Hand' in n: return np.eye(3) * 0.9
    return np.eye(3)


AFF = [joint_affine(j) for j in range(NJ)]
for s in ('Left', 'Right'):                   # smaller hands: the fingers' joints follow
    hd = I[s + 'Hand']
    for j in under(hd):
        if j != hd: J1[j] = J1[hd] + (J1[j] - J1[hd]) * 0.9
LEG_IN = np.radians(6.0)                      # she stands with her feet near (a narrow figure)
for s, sg in (('Left', 1), ('Right', -1)):
    c, sn_ = np.cos(-sg * LEG_IN), np.sin(-sg * LEG_IN)
    Rz = np.array([[c, -sn_, 0], [sn_, c, 0], [0, 0, 1]])
    root = J1[I[s + 'Leg']].copy()
    for j in under(I[s + 'Leg']):
        J1[j] = root + Rz @ (J1[j] - root)
        AFF[j] = Rz @ AFF[j]


def deform(Pt, SJ, SW):
    out = np.zeros_like(Pt)
    for k in range(4):
        for j in np.unique(SJ[:, k]):
            m = (SJ[:, k] == j) & (SW[:, k] > 0)
            out[m] += SW[m, k, None] * (J1[j] + S * (Pt[m] - J0[j]) @ AFF[j].T)
    return out


PB = deform(P0, SJ0, SW0)
y0_ = PB[:, 1].min(); PB[:, 1] -= y0_; J1[:, 1] -= y0_

# ---------------------------------------------------------------- the drawing's head
HD = Head(CH.HEAD)
N_ = CH.HEAD['nose']; MO = CH.HEAD['mouth']; NK = CH.HEAD['neck']; EAR = CH.HEAD['ear']
ZOFF = float(J1[I['Neck1'], 2]) + 0.022


def Wh(p):
    p = np.asarray(p, float)
    return np.stack([p[..., 0] * KH, EYE - p[..., 1] * KH, p[..., 2] * KH + ZOFF], -1)


def nose_bump(x, y):
    prof = N_['profile']
    if y < prof[0][0] or y > prof[-1][0]: return 0.0
    pr, hw = interp_table(prof, y)
    if pr <= 0.002 or abs(x) >= hw: return 0.0
    return pr * (1 - abs(x / hw) ** 1.5)


def lip_bump(x, y):
    d = abs(y - MO['y'])
    if d > 0.07: return 0.0
    pr = MO.get('lip', 0.02) * (1 - (d / 0.07) ** 2)
    tt = x / (MO['w'] * 0.9)
    return pr * (1 - tt * tt) if abs(tt) < 1 else 0.0


US = np.unique(np.round(np.r_[np.sin(np.linspace(-np.pi / 2, np.pi / 2, 49)), np.linspace(-0.2, 0.2, 33)], 5))
NB_ = 40
LEV = np.unique(np.r_[np.linspace(HD.top, HD.bottom, 84), np.linspace(-0.02, 0.26, 40)])
rings = []
for y in LEV:
    w, zf, zb, z0, nf = HD.sec(y)
    row = []
    for u in US:
        x = w * u
        z = z0 + (zf - z0) * (1 - abs(u) ** nf) ** (1 / nf)
        row.append((x, y, z + nose_bump(x, y) + lip_bump(x, y)))
    for k in range(1, NB_):
        ang = math.pi * k / NB_
        row.append((w * math.cos(ang), y, z0 - (z0 - zb) * math.sin(ang)))
    rings.append(row)
NR = len(rings[0])
hv = np.array(rings).reshape(-1, 3)
ht = []
for i in range(len(LEV) - 1):
    for k in range(NR):
        a0, a1 = i * NR + k, i * NR + (k + 1) % NR; b0, b1 = a0 + NR, a1 + NR
        ht += [[a0, a1, b0], [a1, b1, b0]]
ctop = len(hv); hv = np.r_[hv, [[0, HD.top - 0.004, np.mean(hv[:NR, 2])]]]
ht += [[ctop, (k + 1) % NR, k] for k in range(NR)]
cbot = len(hv); o = (len(LEV) - 1) * NR; hv = np.r_[hv, [[0, HD.bottom + 0.003, np.mean(hv[o:o + NR, 2])]]]
ht += [[cbot, o + k, o + (k + 1) % NR] for k in range(NR)]
ht = np.array(ht)
jawk_h = np.clip((hv[:, 1] - 0.26) / 0.12, 0, 1)
# inner contours are lines on the head only below the mouth (chin, jaw) and at the back; the face's lines are drawn
front_face = (hv[:, 2] > HD.sec(0.1)[3] - 0.02) & (hv[:, 1] > -0.34) & (hv[:, 1] < MO['y'] + 0.07)
inner_h = np.where(front_face, 0, 1)


# ears: the drawing's plate (head.py draw_ear), a thin two-sided fan
def catmull_closed(P, n=5):
    P = np.asarray(P, float); m = len(P); out = []
    for i in range(m):
        p0, p1, p2, p3 = P[(i - 1) % m], P[i], P[(i + 1) % m], P[(i + 2) % m]
        for k in range(n):
            t_ = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t_ + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t_ ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t_ ** 3))
    return np.array(out)


ear_v, ear_t, ear_rim = [], [], []
yc, hh, ww = EAR.get('y', 0.08), EAR.get('h', 0.24), EAR.get('w', 0.12); zc_e = EAR.get('z', -0.10)
for side in (1, -1):
    x0 = side * (HD.sec(yc)[0] * 0.97 + 0.02)
    Pe = lambda dy, dz: (x0 + side * 0.03 * max(0, -dz / ww) * 0.8, yc + dy * hh, zc_e + dz * ww)
    rim = [Pe(0.45, 0.25), Pe(0.1, 0.42), Pe(-0.3, 0.38), Pe(-0.5, 0.05), Pe(-0.42, -0.35), Pe(-0.1, -0.5), Pe(0.25, -0.38), Pe(0.5, -0.18), Pe(0.55, 0.05)]
    R_ = catmull_closed(rim, 5)
    base = sum(len(q) for q in ear_v)
    c = R_.mean(0); c[0] += side * 0.004
    ear_v.append(np.r_[R_, [c]])
    n_ = len(R_)
    ear_t.append(np.array([[base + n_, base + i, base + (i + 1) % n_] for i in range(n_)]))
ear_v = np.vstack(ear_v); ear_t = np.vstack(ear_t)

# the neck: the drawing's rings (head.py neck_rings)
rx, rz, zc = NK.get('rx', 0.15), NK.get('rz', 0.17), NK.get('z', -0.08)
lean, flare = NK.get('lean', 0.05), NK.get('flare', 0.25)
NTOP, NBOT = 0.12, 1.0
nrows, ncols = 24, 48
nv = []
for i in range(nrows):
    y = NTOP + (NBOT - NTOP) * i / (nrows - 1); k = (y - NTOP) / (0.95 - NTOP)
    z = zc - lean * k; wd = 1 + flare * k ** 2.5
    for c_ in range(ncols):
        t_ = 2 * math.pi * c_ / ncols
        nv.append((rx * wd * math.sin(t_), y, z + rz * wd * math.cos(t_)))
nv = np.array(nv)
nt = []
for r in range(nrows - 1):
    for c_ in range(ncols):
        a0, a1 = r * ncols + c_, r * ncols + (c_ + 1) % ncols; b0, b1 = a0 + ncols, a1 + ncols
        nt += [[a0, b0, a1], [a1, b0, b1]]
nt = np.array(nt)


def chain_w(yh, n):
    """Head → Neck2 → Neck1 → Chest down the neck (yh: head units below the eye line)."""
    Wt = np.zeros((n, NJ))
    ts = [sm((yh - m) / 0.18) for m in (0.50, 0.68, 0.86)]
    Wt[:, I['Head']] = 1 - ts[0]
    Wt[:, I['Neck2']] = ts[0] * (1 - ts[1])
    Wt[:, I['Neck1']] = ts[0] * ts[1] * (1 - ts[2])
    Wt[:, I['Chest']] = ts[0] * ts[1] * ts[2]
    return Wt


def rigid_head(n):
    Wt = np.zeros((n, NJ)); Wt[:, I['Head']] = 1; return Wt


# ---------------------------------------------------------------- hair: the drawing's shell, columns = its strands
HAIR = CH.HAIR; BUN = HAIR.k['bun']
NAZ, NTT = 144, 30
C0 = np.array((0.0, -0.12, -0.07))
hair_v = np.zeros((NAZ, NTT + 1, 3))
for i in range(NAZ):
    az = -180 + 360 * i / NAZ
    yh = HAIR.hl(az)
    p0 = np.array(HAIR.shell(HD, az, yh))
    d0 = p0 - C0; d0 /= np.linalg.norm(d0)
    d1 = np.array(BUN['c']) - C0; d1 /= np.linalg.norm(d1)
    hair_v[i, 0] = HAIR.shell(HD, az, yh, grow=-0.004)            # the edge lies on the skin
    for j in range(NTT):
        t_ = j / (NTT - 1) * 0.985
        d = d0 * (1 - t_) + d1 * t_
        q, _ = HAIR.shell_ray(HD, tuple(d / np.linalg.norm(d)))
        hair_v[i, j + 1] = q
hair_v[..., 1] = np.maximum(hair_v[..., 1], HD.top - 0.022)                 # the crown without a knob
hair_v[:, 1] = hair_v[:, 1] * 0.65 + hair_v[:, 0] * 0.35          # a soft rise from the skin at the hairline
NTR = NTT + 1
hair_g = hair_v.reshape(-1, 3)
hair_t = []
for i in range(NAZ):
    i2 = (i + 1) % NAZ
    for j in range(NTR - 1):
        a0, a1, b0, b1 = i * NTR + j, i2 * NTR + j, i * NTR + j + 1, i2 * NTR + j + 1
        hair_t += [[a0, b0, a1], [a1, b0, b1]]
hair_t = np.array(hair_t)
bc = np.array(BUN['c']); br = BUN['r']
bth, bph = np.meshgrid(np.linspace(0.0, np.pi, 22), np.linspace(-np.pi, np.pi, 40, endpoint=False), indexing='ij')
bun_v = np.stack([bc[0] + br * np.sin(bth) * np.cos(bph), bc[1] + br * 0.95 * np.sin(bth) * np.sin(bph), bc[2] - br * 0.9 * np.cos(bth)], -1).reshape(-1, 3)
bun_t = []
for i in range(21):
    for j in range(40):
        j2 = (j + 1) % 40
        bun_t += [[i * 40 + j, i * 40 + j2, (i + 1) * 40 + j], [i * 40 + j2, (i + 1) * 40 + j2, (i + 1) * 40 + j]]
bun_t = np.array(bun_t)


def orient(V, T, c):
    n = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    out = (n * (V[T].mean(1) - c)).sum(1) < 0
    T = T.copy(); T[out] = T[out][:, [0, 2, 1]]
    return T


# ---------------------------------------------------------------- Anny's body: what is kept; the coat over it
gone = (part('head', 'neck') > 0.5) & (PB[:, 1] > NECK_Y - 0.012)
tk = ~gone[TRI0].any(1)
bi = np.where(~gone)[0]; remap = -np.ones(len(P0), int); remap[bi] = np.arange(len(bi))
bv = PB[bi].copy(); bT = remap[TRI0[tk]]; bSJ = SJ0[bi]; bSW = SW0[bi]
bp = PARTS[bi]; by = bv[:, 1].copy()
bpart = lambda *ns: sum(bp[:, PN.index(n)] for n in ns)
hands = bpart('Lhand', 'Rhand') > 0.5
legs = bpart('Lthigh', 'Rthigh', 'Lshin', 'Rshin', 'Lfoot', 'Rfoot') > 0.5
feet = bpart('Lfoot', 'Rfoot') > 0.5
WAIST = 0.60 * TALL                            # where the coat's lower shell begins (the hips)
HEM = 1.85 * KB
TOPS = 1.125                                  # the lower shell's top: the waist
grp = np.full(len(bv), G['coat'])
grp[hands] = G['skin']
grp[legs & (by < WAIST - 0.10)] = G['leg']
grp[feet] = G['leg']
nb = M.vertex_normals(bv, bT)
wrist = np.zeros(len(bv))
for s in ('Left', 'Right'):
    jw = J1[I[s + 'Hand']]; jf = J1[I[s + 'ForeArm']]
    d = (jw - jf) / np.linalg.norm(jw - jf)
    along = (bv - jw) @ d
    side = (bpart('Lhand', 'LforeArm') if s == 'Left' else bpart('Rhand', 'RforeArm')) > 0.3
    wrist = np.maximum(wrist, side * sm((along + 0.016) / 0.012))
coat = grp == G['coat']
grp[(wrist > 0.5) & coat] = G['skin']
coat = grp == G['coat']
arms_ = bpart('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm') > 0.4
off = np.where(coat, 0.009, 0) + np.where(coat & arms_, 0.002, 0) + 0
off = off + np.where(coat & (wrist > 0.0), 0.006 * (1 - wrist), 0)
bv = bv + nb * off[:, None]
Ab = M.adjacency(len(bv), bT)
# the coat hides the chest's and the belly's relief (a straight heavy cloth)
trunk = coat & ~arms_ & (bpart('Lclavicle', 'Rclavicle') < 0.5) & (by > TOPS - 0.08)
bv = M.smooth(bv, Ab, trunk * 1.0, iters=300, lam=0.5)
nb = M.vertex_normals(bv, bT)
bv[trunk] += nb[trunk] * 0.016
# the top edge of the coat round the neck: level
# shoes (Р7's loft): Anny's feet below the ankle go
footcut = feet & (bv[:, 1] < 0.085)
bT = bT[~footcut[bT].all(1)]
SHV, SHT, SHW = [], [], []
for s, sg in (('Left', 1), ('Right', -1)):
    jf = J1[I[s + 'Foot']]; jt = J1[I[s + 'ToeBase']]
    fwd = jt - jf; fwd[1] = 0; fwd /= np.linalg.norm(fwd)
    side = np.cross([0, 1.0, 0], fwd)
    base = np.array([jf[0], 0.0, jf[2]])
    rows, cols = 16, 48
    vs = []
    for i in range(rows):
        t_ = i / (rows - 1)
        y = 0.002 + t_ * 0.082
        front = max(0.185 * (1 - t_) ** 1.6 + 0.05 * t_, 0.05)
        back = 0.05 - 0.01 * t_
        w = 0.040 - 0.008 * t_
        if t_ > 0.55: front = 0.05 + 0.015 * (1 - (t_ - 0.55) / 0.45)
        a_ = np.linspace(0, 2 * np.pi, cols, endpoint=False)
        ca, sa = np.cos(a_), np.sin(a_)
        L_ = np.where(ca > 0, front, back)
        rr = (np.abs(ca) ** 2.4 + np.abs(sa) ** 2.4) ** (-1 / 2.4)
        for k in range(cols):
            vs.append(base + fwd * (ca[k] * L_[k] * rr[k]) + side * (sa[k] * w * rr[k]) + [0, y, 0])
    vs = np.array(vs)
    ts = []
    for i in range(rows - 1):
        for k in range(cols):
            a0, a1 = i * cols + k, i * cols + (k + 1) % cols; b0, b1 = a0 + cols, a1 + cols
            ts += [[a0, a1, b0], [a1, b1, b0]]
    c0 = len(vs); vs = np.r_[vs, [base + [0, 0.002, 0] + fwd * 0.07]]
    ts += [[c0, (k + 1) % cols, k] for k in range(cols)]
    c1 = len(vs); vs = np.r_[vs, [base + [0, 0.086, 0] + fwd * 0.012]]
    ts += [[c1, (rows - 1) * cols + k, (rows - 1) * cols + (k + 1) % cols] for k in range(cols)]
    off_ = sum(len(q) for q in SHV)
    SHV.append(vs); SHT.append(np.array(ts) + off_)
    w_ = np.zeros((len(vs), NJ)); w_[:, I[s + 'Foot']] = 1.0
    toe = np.clip(((vs - jt) @ fwd) / 0.04, 0, 1) * 0.6
    w_[:, I[s + 'Foot']] -= toe; w_[:, I[s + 'ToeBase']] += toe
    SHW.append(w_)
SHOE_V, SHOE_T, SHOE_W = np.vstack(SHV), np.vstack(SHT), np.vstack(SHW)

# the body under the coat's lower shell drawn in a little
armsall = bpart('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand', 'Lclavicle', 'Rclavicle') > 0.2
hipz = ~armsall & (bv[:, 1] < TOPS - 0.01) & (bv[:, 1] > HEM + 0.05) & (grp != G['shoe'])



# ---------------------------------------------------------------- the coat's lower shell: from the hips to the hem
def ring_body(y, pad):
    m = (abs(bv[:, 1] - y) < 0.012) & (bpart('LupperArm', 'RupperArm', 'LforeArm', 'RforeArm', 'Lhand', 'Rhand') < 0.3)
    v = bv[m]
    return abs(v[:, 0]).max() + pad, v[:, 2].max() + pad, v[:, 2].min() - pad


# under the shell the body is not kept (it would only show through in a step)
cutb = ~armsall & (bv[:, 1] < TOPS - 0.025) & (bv[:, 1] > HEM + 0.10)
bT = bT[~cutb[bT].all(1)]
srows, scols = 34, 96
ys = np.linspace(TOPS, HEM, srows)
SV = []
hip_y = J1[I['LeftLeg'], 1] - 0.03
RB = np.array([ring_body(max(y, hip_y), 0.0) for y in ys])
for _ in range(3):                                 # the body's rings are uneven: a smooth profile down the hips
    RB[1:-1] = (RB[:-2] + 2 * RB[1:-1] + RB[2:]) / 4
for i, y in enumerate(ys):
    u = i / (srows - 1)
    pad_ = 0.003 + 0.008 * sm(u / 0.08)
    axw, zfr, zbk = RB[i, 0] + pad_, RB[i, 1] + pad_, RB[i, 2] - pad_
    below = sm((hip_y - y) / 0.5)
    fl = 0.02 * below
    axw = axw + fl; zf2 = zfr + fl * 0.6; zb2 = zbk - fl * 0.8
    if y < hip_y:
        lx, lzf, lzb = ring_body(y, 0.016)
        axw = max(axw, lx); zf2 = max(zf2, lzf); zb2 = min(zb2, lzb)
    zc_ = (zf2 + zb2) / 2
    th_ = np.linspace(0, 2 * np.pi, scols, endpoint=False)
    sn, cs = np.sin(th_), np.cos(th_)
    wave = 1 + 0.012 * np.sin(5 * th_ + 0.6) * u ** 1.5
    pw_ = 2.0 + 0.3 * sm(u / 0.25)
    rr = (np.abs(sn) ** pw_ + np.abs(cs) ** pw_) ** (-1 / pw_)
    SV.append(np.c_[axw * sn * rr * wave, np.full(scols, y), zc_ + np.where(cs > 0, zf2 - zc_, zc_ - zb2) * cs * rr * wave])
SV = np.array(SV).reshape(-1, 3)
ST = []
for r in range(srows - 1):
    for c_ in range(scols):
        a0, a1 = r * scols + c_, r * scols + (c_ + 1) % scols; b0, b1 = a0 + scols, a1 + scols
        ST += [[a0, b0, a1], [a1, b0, b1]]
ST = np.array(ST)
skW = np.zeros((len(SV), NJ))
yy = SV[:, 1]; sidek = sm((SV[:, 0] / 0.05 + 1) / 2)
down = sm((hip_y - yy) / 0.35) * 0.62
knee = sm((J1[I['LeftShin'], 1] + 0.12 - yy) / 0.15) * 0.28
skW[:, I['Hips']] = 1 - down
for s, f in (('Left', sidek), ('Right', 1 - sidek)):
    skW[:, I[s + 'Leg']] += (down - knee) * f
    skW[:, I[s + 'Shin']] += knee * f
top_band = sm((yy - (TOPS - 0.07)) / 0.07)
skW = skW * (1 - top_band)[:, None]; skW[:, I['Spine1']] += top_band

# the blouse's stand collar: a white ring round the neck's base
crow, ccol = 8, 64
neck_at = lambda yw: (lambda k: (rx * (1 + flare * k ** 2.5) * KH, rz * (1 + flare * k ** 2.5) * KH, (zc - lean * k) * KH + ZOFF))((((EYE - yw) / KH) - NTOP) / (0.95 - NTOP))
CV = []
for i in range(crow):
    t_ = i / (crow - 1)
    y = NECK_Y - 0.02 + t_ * 0.05
    ax_, az_, zz = neck_at(y)
    g_ = 1.1 + 0.75 * (1 - t_) ** 1.6
    angs = np.linspace(0, 2 * np.pi, ccol, endpoint=False)
    dip = 0.010 * np.exp(-((np.minimum(angs, 2 * np.pi - angs)) / 0.35) ** 2) * t_      # a small V in front
    CV.append(np.c_[(ax_ * g_ + 0.003) * np.sin(angs), y - dip, zz + (az_ * g_ + 0.003) * np.cos(angs)])
CV = np.array(CV).reshape(-1, 3)
CT = []
for r in range(crow - 1):
    for c_ in range(ccol):
        a0, a1 = r * ccol + c_, r * ccol + (c_ + 1) % ccol; b0, b1 = a0 + ccol, a1 + ccol
        CT += [[a0, a1, b0], [a1, b1, b0]]
CT = np.array(CT)
colW = np.zeros((len(CV), NJ)); tc = sm((CV[:, 1] - NECK_Y + 0.02) / 0.06)
colW[:, I['Chest']] = 1 - 0.5 * tc; colW[:, I['Neck1']] = 0.5 * tc

# the folder (the drawn pose only): a thin board in the right hand
hr = J1[I['RightHand']]
fd = hr - J1[I['RightForeArm']]; fd /= np.linalg.norm(fd)                       # along the forearm
fpn = np.cross(J1[I['RightHandPinky1']] - J1[I['RightHandIndex1']], J1[I['RightHandMiddle1']] - hr); fpn /= np.linalg.norm(fpn)
fs = np.cross(fd, fpn); fs /= np.linalg.norm(fs)                                # across the palm
fc = hr - fd * 0.085 + fpn * FOLD_OFF + fs * 0.03
fo = np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]]) * [0.20, 0.29]
fq = np.array([fc + fs * x + fd * y for x, y in fo])
FV = np.r_[fq + fpn * 0.004, fq - fpn * 0.004]
FT = np.array([[0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6], [0, 4, 5], [0, 5, 1], [1, 5, 6], [1, 6, 2], [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0]])
foW = np.zeros((8, NJ)); foW[:, I['RightHand']] = 1

# ---------------------------------------------------------------- joints for the new head
J = J1.copy()
Jh = lambda p: Wh(np.array(p, float))
J[I['Neck1']] = [0, NECK_Y, Jh([0, 0.86, -0.13])[2]]
J[I['Neck2']] = Jh([0, 0.68, -0.115])
J[I['Head']] = Jh([0, 0.46, -0.10])
J[I['HeadEnd']] = Jh([0, -0.5, -0.08])
J[I['Jaw']] = Jh([0, 0.2, -0.02])
for s, sg in (('Left', 1), ('Right', -1)):
    J[I[s + 'Eye']] = Jh([sg * CH.HEAD['eye']['x'], 0, 0.25])


def top4(Wt):
    idx = np.argsort(-Wt, 1)[:, :4]; w = np.take_along_axis(Wt, idx, 1); w = w / w.sum(1, keepdims=True)
    return idx, w


parts_out = []


def add(name, V, T, g, SJ=None, SW=None, Wt=None, **attr):
    if Wt is not None: SJ, SW = top4(Wt)
    parts_out.append(dict(name=name, V=np.asarray(V, float), T=np.asarray(T), grp=np.broadcast_to(g, (len(V),)), SJ=SJ, SW=SW, **attr))


add('body', bv, bT, grp, bSJ, bSW)
HV = Wh(hv)
add('head', HV, orient(HV, ht, Wh([0, 0, -0.05])), G['skin'], Wt=rigid_head(len(HV)), jawk=jawk_h, inner=inner_h)
add('ears', Wh(ear_v), ear_t, G['skin'], Wt=rigid_head(len(ear_v)), inner=0)
NV_ = Wh(nv)
add('neck', NV_, orient(NV_, nt, Wh([0, 0.5, -0.1])), G['skin'], Wt=chain_w(nv[:, 1], len(nv)))
HG = Wh(hair_g)
add('hair', HG, orient(HG, hair_t, Wh(C0)), G['hair'], Wt=rigid_head(len(HG)))
BV = Wh(bun_v)
add('bun', BV, orient(BV, bun_t, Wh(bc)), G['hair'], Wt=rigid_head(len(BV)))
add('shoes', SHOE_V, SHOE_T, G['shoe'], Wt=SHOE_W)
add('skirt', SV, orient(SV, ST, np.array([0, 0.7, 0.03])), G['coat'], Wt=skW)
add('collar', CV, orient(CV, CT, np.array([0, NECK_Y, ZOFF - 0.02])), G['blouse'], Wt=colW)
add('folder', FV, FT, G['folder'], Wt=foW)
mk = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], float)
add('marks', Wh(mk), np.zeros((0, 3), int), 0, Wt=rigid_head(4))

N = sum(len(p['V']) for p in parts_out)
P = np.concatenate([p['V'] for p in parts_out])
T, base, pieces, tpieces = [], 0, {}, {}
tb = 0
for p in parts_out:
    T.append(p['T'] + base); pieces[p['name']] = [base, base + len(p['V'])]; tpieces[p['name']] = [tb, tb + len(p['T'])]
    base += len(p['V']); tb += len(p['T'])
T = np.concatenate(T).astype(np.int64)
SJ = np.concatenate([p['SJ'] for p in parts_out]); SW = np.concatenate([p['SW'] for p in parts_out])
grp_all = np.concatenate([p['grp'] for p in parts_out]).astype(np.uint8)
PNAMES = list(pieces)
pid = np.zeros(N, np.uint8)
for i, k in enumerate(PNAMES): pid[pieces[k][0]:pieces[k][1]] = i


def cat(k, default):
    return np.concatenate([np.broadcast_to(p.get(k, default), (len(p['V']),)) for p in parts_out])


jawk = cat('jawk', 0.0).astype(np.float32); inner = cat('inner', 1).astype(np.uint8)
# hands: the fingers' inner contours are not drawn (a hand in this drawing is an outline)
bsl = slice(*pieces['body'])

# ---------------------------------------------------------------- edges
e = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
f = np.tile(np.arange(len(T)), 3)
key = np.sort(e, 1); o = np.lexsort((key[:, 1], key[:, 0])); key, f = key[o], f[o]
first = np.r_[True, (key[1:] != key[:-1]).any(1)]
idx = np.flatnonzero(first); cnt = np.diff(np.r_[idx, len(key)])
E = key[idx]
F0 = f[idx]; F1 = np.where(cnt >= 2, f[np.minimum(idx + 1, len(f) - 1)], -1)
drop = np.zeros(len(E), bool)
openE = F1 < 0
ep = pid[E[:, 0]]
# open edges that are not lines: the body's cuts under the collar, at the ankles; the lower shell's top (inside the coat);
# the neck's ends; the collar's lower edge; the hair's edge on the skin is a line (the hairline)
for nm in ('body', 'neck', 'skirt', 'collar', 'ears'):
    m = openE & (ep == PNAMES.index(nm))
    if nm == 'skirt': m &= P[E[:, 0], 1] > TOPS - 0.01
    if nm == 'collar': m &= P[E[:, 0], 1] < NECK_Y + 0.01
    if nm == 'ears': m &= False
    drop |= m
print('edges', len(E), 'open', openE.sum(), 'dropped', drop.sum())


# ---------------------------------------------------------------- curves on the surface
def on_front(q, tris):
    """For points q (x, y) the front-most triangle of `tris` over them, and where on it."""
    TH = T[tris]
    A3, B3, C3 = P[TH[:, 0]], P[TH[:, 1]], P[TH[:, 2]]
    ft = -np.ones(len(q), np.int64); fb = np.zeros((len(q), 3)); best = np.full(len(q), -1e9)
    for ti in range(len(TH)):
        a2, b2, c2 = A3[ti, :2], B3[ti, :2], C3[ti, :2]
        lo = np.minimum(np.minimum(a2, b2), c2); hi = np.maximum(np.maximum(a2, b2), c2)
        m = np.flatnonzero((q[:, 0] >= lo[0]) & (q[:, 0] <= hi[0]) & (q[:, 1] >= lo[1]) & (q[:, 1] <= hi[1]))
        if not len(m): continue
        v0, v1 = b2 - a2, c2 - a2; den = v0[0] * v1[1] - v1[0] * v0[1]
        if abs(den) < 1e-14: continue
        w = q[m] - a2
        l1 = (w[:, 0] * v1[1] - v1[0] * w[:, 1]) / den; l2 = (v0[0] * w[:, 1] - w[:, 0] * v0[1]) / den; l0 = 1 - l1 - l2
        ok = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        m, l0, l1, l2 = m[ok], l0[ok], l1[ok], l2[ok]
        z = l0 * A3[ti, 2] + l1 * B3[ti, 2] + l2 * C3[ti, 2]
        better = z > best[m]
        m, z = m[better], z[better]
        best[m] = z; ft[m] = tris[ti]; fb[m] = np.c_[l0[better], l1[better], l2[better]]
    return ft, fb


# the coat's front in rest coordinates (the shader paints the same shapes per pixel, web/vera.js `paint`)
YTOP = NECK_Y + 0.004; YV = WAIST - 0.02; YL0 = YTOP - 0.05; YL1 = YTOP - 0.25
COATP = dict(cy0=YTOP - 0.05, cw0=0.062, cw1=0.036, ytop=YTOP, yv=YV, yl0=YL0, yl1=YL1, hem=HEM, wtop=0.034, wmid=0.02, lap=0.088, gap=0.007)


def wb(y):          # the blouse's half-width
    y = np.asarray(y, float)
    return np.where(y > YL1, COATP['wmid'] + (COATP['wtop'] - COATP['wmid']) * (y - YL1) / (YTOP - YL1), COATP['wmid'] * np.clip((y - YV) / (YL1 - YV), 0, 1))


coat_tris = np.r_[np.arange(*tpieces['body']), np.arange(*tpieces['skirt'])]
ct = T[coat_tris]
coat_tris = coat_tris[(np.abs(P[ct, 0]).max(1) < 0.16) & (grp_all[ct] == G['coat']).all(1)]
curves, cT, cB = [], [], []


def curve(kind, w, pts, taper=(0.1, 0.1), ink=1):
    q = np.asarray(pts, float)
    ft, fb = on_front(q, coat_tris)
    ok = ft >= 0
    if ok.sum() < 2: return
    curves.append(dict(kind=kind, w=w, start=len(cT), n=int(ok.sum()), taper=list(taper), ink=ink))
    cT.extend(ft[ok]); cB.extend(fb[ok])


for sg in (1, -1):
    ysq = np.linspace(YTOP - 0.004, YV, 60)
    curve('edge', 1.0, np.c_[sg * wb(ysq), ysq], (0.03, 0.25))                      # the coat's front edge over the blouse
    ysq = np.linspace(YV, HEM + 0.004, 50)
    curve('edge', 1.0, np.c_[sg * (COATP['gap'] + (YV - ysq) * 0.012) * np.clip((YV - ysq) / 0.05, 0, 1), ysq], (0.25, 0.03))
    lp = np.array([[wb(YTOP) + 0.012, YTOP - 0.004], [COATP['lap'], YL0], [float(wb(YL1)), YL1]])
    curve('lapel', 0.8, np.c_[sg * np.interp(np.linspace(0, 2, 40), [0, 1, 2], lp[:, 0]), np.interp(np.linspace(0, 2, 40), [0, 1, 2], lp[:, 1])], (0.05, 0.1))
    # the blouse's collar lying on the chest: its outer edge and its lower edge
    curve('collar', 0.8, np.c_[sg * np.linspace(COATP['cw1'], COATP['cw0'], 14), np.linspace(YTOP + 0.012, COATP['cy0'], 14)], (0.1, 0.05))
    curve('collar', 0.8, np.c_[sg * np.linspace(COATP['cw0'], 0.004, 14), np.linspace(COATP['cy0'], COATP['cy0'] + 0.012, 14)], (0.05, 0.2))
curve('seam', 0.6, np.c_[np.linspace(-0.05, 0.05, 12) * 0 + np.linspace(-wb(YL1 - 0.06), wb(YL1 - 0.06), 12), np.full(12, YL1 - 0.06)], (0.2, 0.2))

# the hair's streaks of light: parts of the strands (columns of the hair's grid), as vertex chains
rng = np.random.default_rng(51)
h0 = pieces['hair'][0]
streaks = []
for i in range(0, NAZ, 1):
    if rng.random() > 0.62: continue
    j0 = int(rng.integers(2, 12)); j1 = min(NTR - 2, j0 + int(rng.integers(5, 16)))
    streaks.append(dict(w=float(rng.uniform(0.35, 1.0)), v=[int(h0 + i * NTR + j) for j in range(j0, j1 + 1)]))
# the hairline's teeth: where the strands begin, short black points onto the forehead are drawn from these vertices
hairline = [int(h0 + i * NTR) for i in range(NAZ)]

# the lower shell's rings (for keeping it off the legs)
header = dict(format='r20/character', version=1, id='vera-s18', label={'ru': 'Вера, манга'}, skinning='dqs',
              source='Anny moood-woman + the head, hair and neck of styles/s18-manga (head.py, hair.py, chars/vera.py) + shells',
              pieces=pieces, trianglePieces=tpieces, pieceNames=PNAMES, groups=G, KH=KH, KB=KB, EYE=EYE, ZOFF=ZOFF,
              coat=COATP, waist=WAIST, skirt=dict(rows=srows, cols=scols), curves=curves, streaks=streaks, hairline=hairline,
              hair=dict(naz=NAZ, ntr=NTR), head=dict(sections=[list(map(float, r)) for r in CH.HEAD['sections']],
                                                     **{k: CH.HEAD[k] for k in ('nose', 'eye', 'brow', 'mouth', 'ear', 'rest')}),
              lock=HAIR.k['locks'][0])
pack.save(os.path.join(OUT, 'vera.json'), header, dict(
    positions=P.astype(np.float32).ravel(), triangles=T.astype(np.uint32).ravel(),
    skinJoints=SJ.astype(np.uint8), skinWeights=SW.astype(np.float32),
    joints=J.astype(np.float32).ravel(), frames=FR.ravel(),
    grp=grp_all, pid=pid, inner=inner, jawk=jawk,
    edges=E.astype(np.uint32).ravel(), edgeTris=np.where(np.c_[F0, F1] < 0, 0xFFFFFFFF, np.c_[F0, F1]).astype(np.uint32).ravel(),
    edgeDrop=drop.astype(np.uint8), curveTri=np.array(cT, np.uint32), curveBar=np.array(cB, np.float32).ravel()))
print('saved', N, 'vertices', len(T), 'triangles; height', round(float(P[:, 1].max()), 3), 'ZOFF', round(ZOFF, 4), 'KH', round(KH, 4))
