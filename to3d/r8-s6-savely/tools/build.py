"""Р8 — Савелий Петрович, символический (С6) → 3D.

The С6 drawing is itself built in 3D (styles/s6-symbolic/tools/sil.py + cast.py): lofts of rings and tubes of spheres
on a small skeleton, projected and merged into one flat shape. Here the same code builds the same solids, but in a
rest pose whose joints are SOMA's (the engine's skeleton), so Kimodo's motions can move them:

  1. the drawing's skeleton in a neutral stand (no stoop), its arms laid along SOMA's rest arms;
  2. cast.savely() run unchanged on that skeleton → its lofts and tubes (the very solids of the drawing);
  3. every pair of neighbouring rings and every pair of neighbouring spheres → its 3D convex hull (the drawing merges
     the 2D hulls of exactly these pairs, so the 3D hulls project to the drawing's shape in any view);
  4. each hull's points weighted to SOMA joints (limbs rigid on their bone, torso and coat blended along the spine,
     the coat's skirt partly on the thighs, the head and its cap rigid, the chin on the jaw);
  5. SOMA's 77 joints placed on the drawing's skeleton; their frames turned from SOMA's so that Kimodo's bones are
     followed (src/retarget.js: Q = q·frameᵀ);
  6. poses from the drawing's own pose numbers (the drawn stand, the turnaround, moods) as SOMA joint turns.

Writes tools/web/data/savely.{json,bin} (an engine body + its topology in one pack) and tools/web/data/poses.json.
python3 build.py
"""
import sys, os, json, math
import numpy as np
from scipy.spatial import ConvexHull

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'styles', 's6-symbolic', 'tools'))
sys.path.insert(0, os.path.join(REPO, 'engine', 'tools'))
import sil, cast, pack   # noqa: E402

OUT = os.path.join(HERE, 'web', 'data')
os.makedirs(OUT, exist_ok=True)
CM = 0.01

# ------------------------------------------------------------------ quaternions [x, y, z, w]


def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz])


def qconj(q):
    return np.array([-q[0], -q[1], -q[2], q[3]])


def qrot(q, v):
    return (qmat(q) @ np.asarray(v, float))


def qmat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def mat2q(m):
    t = np.trace(m)
    if t > 0:
        s = math.sqrt(t + 1) * 2
        q = [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, s / 4]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = math.sqrt(1 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        q = [s / 4, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s, (m[2, 1] - m[1, 2]) / s]
    elif m[1, 1] > m[2, 2]:
        s = math.sqrt(1 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        q = [(m[0, 1] + m[1, 0]) / s, s / 4, (m[1, 2] + m[2, 1]) / s, (m[0, 2] - m[2, 0]) / s]
    else:
        s = math.sqrt(1 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        q = [(m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, s / 4, (m[1, 0] - m[0, 1]) / s]
    q = np.array(q)
    return q / np.linalg.norm(q)


def qbetween(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    d = float(a @ b)
    if d < -0.999999:
        ax = np.cross(a, [1, 0, 0]) if abs(a[0]) < .9 else np.cross(a, [0, 1, 0])
        ax /= np.linalg.norm(ax)
        return np.array([*ax, 0.0])
    c = np.cross(a, b)
    q = np.array([*c, 1 + d])
    return q / np.linalg.norm(q)


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


# ------------------------------------------------------------------ SOMA
SK = json.load(open(os.path.join(REPO, 'engine', 'data', 'skeleton.json')))
NAMES = [j['name'] for j in SK['joints']]
IDX = {n: i for i, n in enumerate(NAMES)}
PARENT = [j['parent'] for j in SK['joints']]
PARENT = [p if isinstance(p, int) else (IDX[p] if p is not None else -1) for p in PARENT]
S_REST = np.array([j['rest'] for j in SK['joints']]) / CM          # SOMA rest in cm
S_FRAME = np.array([j['frame'] for j in SK['joints']])
NJ = len(NAMES)

# sil's side 'L' is at −x: the person's right (the engine: the person's left is +x). sil 'R' → SOMA Left.
SIDE = {'L': 'Right', 'R': 'Left'}

# ------------------------------------------------------------------ the drawing's skeleton
B = cast.SAV_B
_real_skel = sil.skel
_seen = {}


def _spy(Bx, P):
    _seen['P'] = dict(P)
    return _real_skel(Bx, P)


cast.skel = _spy
cast.savely()
DRAWN = dict(sil.POSE0); DRAWN.update(_seen['P'])          # the drawing's own stand (looking at the watch)
cast.skel = _real_skel

NEUTRAL = dict(lean=0, hunch=0, neck=0, nod=0, slump=0, shrug=0, roll=0, headYaw=0, headRoll=0,
               armL=(0, 10, 0, 0), armR=(0, 10, 0, 0), legL=(0, 1.5, 0, 0), legR=(0, 1.5, 0, 0),
               footL=(0, 11), footR=(0, 11))


def rest_skeleton():
    """The drawing's skeleton standing straight; its arms along SOMA's rest arms (so arm frames stay SOMA's)."""
    J = sil.skel(B, NEUTRAL)
    for k, s in SIDE.items():
        dU = unit(S_REST[IDX[s + 'ForeArm']] - S_REST[IDX[s + 'Arm']])
        dF = unit(S_REST[IDX[s + 'Hand']] - S_REST[IDX[s + 'ForeArm']])
        J['el' + k] = J['sh' + k] + dU * B['armU']
        J['wr' + k] = J['el' + k] + dF * B['armF']
        J['dh' + k] = dF
    return J


def frames_of(J, p):
    """The drawing's rotations of the trunk parts for pose dict p."""
    roll = p.get('roll', 0)
    Rn = sil.rz(-roll * 1.4) @ sil.rx(p['lean'] + p['hunch'] + p['neck'])
    return dict(low=J['Rlow'], up=J['Rup'], n=Rn, h=J['Rh'])


def soma_places(J, p):
    """Every SOMA joint's place (cm) on a drawing skeleton J (rest or posed)."""
    F = frames_of(J, p)
    up = lambda R, L: R @ np.array([0, L, 0])
    P = {}
    lowL, neckL, H = B['lowL'], B['neckL'], B['H']
    P['Hips'] = J['pel']
    P['Spine1'] = J['pel'] + up(F['low'], .25 * lowL)
    P['Spine2'] = J['pel'] + up(F['low'], .62 * lowL)
    P['Chest'] = J['chest']
    P['Neck1'] = J['neck']
    P['Neck2'] = J['neck'] + up(F['n'], .5 * neckL)
    P['Head'] = J['ntop']
    P['HeadEnd'] = J['ntop'] + J['Rh'] @ np.array([0, .86 * H, 0])
    P['Jaw'] = J['ntop'] + J['Rh'] @ np.array([0, .28 * H, -.05 * B['Dp']])
    for s, x in (('Left', 1), ('Right', -1)):
        P[s + 'Eye'] = J['ntop'] + J['Rh'] @ np.array([x * .38 * B['W'], .38 * H, .8 * B['Dp']])
    for k, s in SIDE.items():
        sgn = 1 if s == 'Left' else -1
        P[s + 'Shoulder'] = J['neck'] + F['up'] @ np.array([sgn * 2.0, -3.5, -1.0])
        P[s + 'Arm'] = J['sh' + k]
        P[s + 'ForeArm'] = J['el' + k]
        P[s + 'Hand'] = J['wr' + k]
        P[s + 'Leg'] = J['hip' + k]
        P[s + 'Shin'] = J['kn' + k]
        P[s + 'Foot'] = J['an' + k]
        P[s + 'ToeBase'] = J['ball' + k]
        P[s + 'ToeEnd'] = J['toe' + k]
    return P


# which child gives each joint's bone direction, and which trunk frame gives its twist
BONE = {'Hips': ('Spine1', 'low'), 'Spine1': ('Spine2', 'low'), 'Spine2': ('Chest', 'low'), 'Chest': ('Neck1', 'up'),
        'Neck1': ('Neck2', 'n'), 'Neck2': ('Head', 'n'), 'Head': (None, 'h'), 'Jaw': (None, 'h'),
        'HeadEnd': (None, 'h'), 'LeftEye': (None, 'h'), 'RightEye': (None, 'h')}
for s in ('Left', 'Right'):
    BONE.update({s + 'Shoulder': (s + 'Arm', 'up'), s + 'Arm': (s + 'ForeArm', None), s + 'ForeArm': (s + 'Hand', None),
                 s + 'Leg': (s + 'Shin', None), s + 'Shin': (s + 'Foot', None), s + 'Foot': (s + 'ToeBase', None),
                 s + 'ToeBase': (s + 'ToeEnd', None)})

J0 = rest_skeleton()
P0 = soma_places(J0, NEUTRAL)


def rest_joints():
    """All 77 joints at rest (cm): the mapped ones from the drawing, the rest (fingers, toe ends…) carried along
    from SOMA's offsets under their nearest mapped ancestor."""
    R = np.zeros((NJ, 3))
    for j in range(NJ):
        n = NAMES[j]
        if n in P0:
            R[j] = P0[n]
        else:
            p = PARENT[j]
            R[j] = R[p] + (S_REST[j] - S_REST[p]) * (B['armF'] / 27.1 if 'Hand' in n else 1.0)
    return R


REST = rest_joints()


def rest_frames():
    """frame_mine = turn(SOMA bone → our bone) · frame_SOMA: Kimodo's bones are followed with our lengths. Hips and
    head keep SOMA's frames (their orientation, not a bone direction, is what matters), and so do joints that carry
    nothing of ours."""
    F = S_FRAME.copy()
    for n, (child, _) in BONE.items():
        if child is None or n == 'Hips':
            continue
        j, c = IDX[n], IDX[child]
        r = qbetween(S_REST[c] - S_REST[j], REST[c] - REST[j])
        F[j] = qmul(r, S_FRAME[j])
    # the hand: our drop lies along the forearm; SOMA's hand points to the middle finger
    for s in ('Left', 'Right'):
        j = IDX[s + 'Hand']
        r = qbetween(S_REST[IDX[s + 'HandMiddle1']] - S_REST[j], REST[IDX[s + 'Hand']] - REST[IDX[s + 'ForeArm']])
        F[j] = qmul(r, S_FRAME[j])
    return F


FRAMES = rest_frames()

# ------------------------------------------------------------------ poses from the drawing's numbers


def pose_of(p):
    """A static pose from a sil pose dict: every joint's turn from our rest (world), and the pelvis's place (cm)."""
    pp = dict(sil.POSE0); pp.update(NEUTRAL); pp.update(p)
    J = sil.skel(B, pp)
    Pp = soma_places(J, pp)
    Fp = frames_of(J, pp)
    Q = np.tile([0, 0, 0, 1.0], (NJ, 1))
    done = np.zeros(NJ, bool)
    for j in range(NJ):          # parents come before children in SOMA's list
        n = NAMES[j]
        if n in BONE:
            child, fr = BONE[n]
            R = Fp[fr] if fr else np.eye(3)
            q = mat2q(R)
            if child is not None:
                d_rest = qrot(q, REST[IDX[child]] - REST[j])
                q = qmul(qbetween(d_rest, Pp[child] - Pp[n]), q)
            Q[j] = q
        else:
            Q[j] = Q[PARENT[j]]
        done[j] = True
    # the hand goes on with its forearm (the drawing's hand lies along the forearm)
    for s in ('Left', 'Right'):
        Q[IDX[s + 'Hand']] = Q[IDX[s + 'ForeArm']]
        for j in range(NJ):
            if NAMES[j].startswith(s + 'Hand') and NAMES[j] != s + 'Hand':
                Q[j] = Q[IDX[s + 'ForeArm']]
    return Q, Pp['Hips'], J


def locals_of(Q):
    L = np.zeros_like(Q)
    for j in range(NJ):
        p = PARENT[j]
        L[j] = Q[j] if p < 0 else qmul(qconj(Q[p]), Q[j])
    return L


# moods: the posture is the expression (style rules: «Выражения — позой всего тела»)
MOODS = {
    'watch': dict(label='смотрит на часы', pose=DRAWN, arms=1.0),
    'grumpy': dict(label='ворчит', pose=dict(lean=6, hunch=24, neck=16, nod=-8, slump=2.5,
                                             armL=(-26, 10, -14, -84), armR=(-26, 10, -14, -84)), arms=1.0),
    'sad': dict(label='грустит', pose=dict(lean=14, hunch=32, neck=12, nod=26, slump=3, shrug=-1.5,
                                           armL=(3, 3, 2, 0), armR=(3, 3, 2, 0)), arms=1.0),
    'glad': dict(label='радуется', pose=dict(lean=-3, hunch=12, neck=4, nod=-16, slump=1, shrug=1,
                                             armL=(16, 22, 40, 10), armR=(20, 24, 46, 10)), arms=1.0),
    'surprised': dict(label='удивлён', pose=dict(lean=-9, hunch=10, neck=-2, nod=-12, slump=0, shrug=2,
                                                 armL=(34, 22, 98, 6), armR=(38, 20, 104, 6)), arms=1.0),
    'angry': dict(label='сердится', pose=dict(lean=12, hunch=18, neck=22, nod=-24, slump=2, shrug=2.4,
                                              armL=(-30, 18, -8, 4), armR=(-26, 18, -6, 4)), arms=1.0),
    'plain': dict(label='просто стоит', pose=dict(lean=4, hunch=22, neck=12, nod=-6, slump=2), arms=0.0),
}
LAYER_TRUNK = ['Spine1', 'Spine2', 'Chest', 'Neck1', 'Neck2', 'Head']
LAYER_ARMS = [s + n for s in ('Left', 'Right') for n in ('Shoulder', 'Arm', 'ForeArm', 'Hand')]


# ------------------------------------------------------------------ the solids, on the rest skeleton

def build_solids():
    cast.skel = lambda Bx, P: J0
    try:
        J, f, acc = cast.savely()
    finally:
        cast.skel = _real_skel
    return J, f, acc


def fib_sphere(c, r, n):
    i = np.arange(n) + .5
    phi = np.arccos(1 - 2 * i / n); th = np.pi * (1 + 5 ** .5) * i
    return c + r * np.stack([np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)], 1)


def sphere_n(r):
    return int(np.clip(70 * r, 160, 520))


def smooth01(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


class Mesh:
    def __init__(self):
        self.P, self.W, self.T, self.part = [], [], [], []
        self.n = 0
        self.parts = []

    def hull(self, pts, weights, part):
        """pts: K×3 (cm); weights: K dicts {joint: w}."""
        pts = np.asarray(pts, float)
        h = ConvexHull(pts)
        used = np.unique(h.simplices)
        remap = -np.ones(len(pts), int); remap[used] = np.arange(len(used)) + self.n
        tris = remap[h.simplices]
        # orient outward
        cen = pts[used].mean(0)
        a, b, c = pts[h.simplices[:, 0]], pts[h.simplices[:, 1]], pts[h.simplices[:, 2]]
        nrm = np.cross(b - a, c - a)
        flip = ((a - cen) * nrm).sum(1) < 0
        tris[flip] = tris[flip][:, [0, 2, 1]]
        self.P.append(pts[used]); self.W += [weights[i] for i in used]; self.T.append(tris)
        if part not in self.parts:
            self.parts.append(part)
        self.part += [self.parts.index(part)] * len(used)
        self.n += len(used)

    def arrays(self):
        P = np.vstack(self.P) * CM
        T = np.vstack(self.T)
        N = len(P)
        SJ = np.zeros((N, 4), np.uint8); SW = np.zeros((N, 4), np.float32)
        for i, w in enumerate(self.W):
            items = sorted(w.items(), key=lambda kv: -kv[1])[:4]
            s = sum(v for _, v in items)
            for k, (jn, v) in enumerate(items):
                SJ[i, k] = IDX[jn]; SW[i, k] = v / s
        return P.astype(np.float32), T.astype(np.uint32), SJ, SW, np.array(self.part, np.uint8)


def rigid(j):
    return lambda p: {j: 1.0}


def lerp_w(anchors, t):
    """anchors: [(t, joint)], sorted; weights for t, piecewise linear."""
    if t <= anchors[0][0]:
        return {anchors[0][1]: 1.0}
    for (ta, ja), (tb, jb) in zip(anchors, anchors[1:]):
        if t <= tb:
            u = (t - ta) / (tb - ta)
            u = u * u * (3 - 2 * u)
            w = {}
            w[ja] = w.get(ja, 0) + 1 - u; w[jb] = w.get(jb, 0) + u
            return w
    return {anchors[-1][1]: 1.0}


def add(w, j, v):
    w[j] = w.get(j, 0) + v


def build_mesh():
    J, f, acc = build_solids()
    M = Mesh()
    # --- tubes: legs (0, 2), feet (1, 3), neck (4), arm+hand (5–8), loupe (9)
    tube_bones = {0: ['L.Leg', 'L.Shin', 'L.Shin'], 2: ['R.Leg', 'R.Shin', 'R.Shin'],
                  1: ['L.Foot', 'L.ToeBase'], 3: ['R.Foot', 'R.ToeBase'],
                  5: ['L.Arm', 'L.ForeArm'], 6: ['L.Hand', 'L.Hand'], 7: ['R.Arm', 'R.ForeArm'], 8: ['R.Hand', 'R.Hand'],
                  9: ['Head']}
    part_of = {0: 'leg', 2: 'leg', 1: 'shoe', 3: 'shoe', 5: 'arm', 7: 'arm', 6: 'hand', 8: 'hand', 4: 'neck', 9: 'loupe'}

    def jname(s):
        if '.' in s:
            k, n = s.split('.')
            return SIDE[k] + n
        return s

    for ti, (pts, rad) in enumerate(f.tubes):
        for i in range(len(pts) - 1):
            a = fib_sphere(pts[i], max(rad[i], .05), sphere_n(rad[i]))
            b = fib_sphere(pts[i + 1], max(rad[i + 1], .05), sphere_n(rad[i + 1]))
            pp = np.vstack([a, b])
            if ti == 4:   # the neck: Neck1 → Neck2 → Head along its axis
                ax = pts[1] - pts[0]; L = np.linalg.norm(ax); ax = ax / L
                ws = [lerp_w([(0, 'Neck1'), (.5, 'Neck2'), (1, 'Head')], float(np.clip((q - pts[0]) @ ax / L, 0, 1))) for q in pp]
            else:
                j = jname(tube_bones[ti][min(i, len(tube_bones[ti]) - 1)])
                ws = [{j: 1.0}] * len(pp)
            M.hull(pp, ws, part_of[ti])
    # --- lofts: torso (0), skirt (1), head (2), moustache (3), cap (4), brim (5)
    torso, skirt, head, mo, capl, brim = f.lofts
    # torso: rings at t = 0, .3, .55, .78, .92, 1 along pelvis → chest(.5) → neck(1)
    ts = [0, .3, .55, .78, .92, 1]
    anchors = [(0, 'Hips'), (.12, 'Spine1'), (.31, 'Spine2'), (.5, 'Chest'), (.8, 'Chest'), (1, 'Neck1')]

    def torso_w(t, q):
        w = lerp_w(anchors, t)
        # the top of the coat over the shoulders goes partly with the collarbones
        x = q[0]
        sh = smooth01(.55, .9, t) * smooth01(6, 15, abs(x)) * .55
        if sh > 0:
            for k in list(w):
                w[k] *= 1 - sh
            add(w, 'LeftShoulder' if x > 0 else 'RightShoulder', sh)
        return w

    for i in range(len(torso) - 1):
        pp = np.vstack([torso[i], torso[i + 1]])
        ws = [torso_w(ts[i], q) for q in torso[i]] + [torso_w(ts[i + 1], q) for q in torso[i + 1]]
        M.hull(pp, ws, 'coat')
    # skirt: rings u = 0..1 from the pelvis to the hem (46 cm down the legs); the lower part goes with the thighs
    n = len(skirt) - 1

    def skirt_w(u, q):
        s = .78 * smooth01(.05, 1.0, u)
        x = q[0] - J0['pel'][0]
        side = 1 / (1 + math.exp(-x / 3.2))    # → the person's left (+x)
        w = {'Hips': 1 - s}
        add(w, 'LeftLeg', s * side); add(w, 'RightLeg', s * (1 - side))
        return w

    for i in range(n):
        pp = np.vstack([skirt[i], skirt[i + 1]])
        ws = [skirt_w(i / n, q) for q in skirt[i]] + [skirt_w((i + 1) / n, q) for q in skirt[i + 1]]
        M.hull(pp, ws, 'coat')
    # head: rings v = 0 (chin) .. 1 (crown); the lower front (chin, lower lip) goes with the jaw
    H, Dp = B['H'], B['Dp']
    nv = len(head)
    ntop = J0['ntop']

    def head_w(v, q):
        z = q[2] - ntop[2]
        jw = smooth01(.30, .17, v) * smooth01(.1 * Dp, .55 * Dp, z)
        return {'Head': 1 - jw, 'Jaw': jw} if jw > 0 else {'Head': 1.0}

    for i in range(nv - 1):
        v0, v1 = i / (nv - 1), (i + 1) / (nv - 1)
        pp = np.vstack([head[i], head[i + 1]])
        ws = [head_w(v0, q) for q in head[i]] + [head_w(v1, q) for q in head[i + 1]]
        M.hull(pp, ws, 'head')
    for loft, part in ((mo, 'moustache'), (capl, 'cap'), (brim, 'cap')):
        for i in range(len(loft) - 1):
            pp = np.vstack([loft[i], loft[i + 1]])
            M.hull(pp, [{'Head': 1.0}] * len(pp), part)
    return M, J, acc


def accents(acc):
    """Where the signs sit, at rest, and on which joint: the watch in the hand, the chain's pocket on the chest,
    the loupe's glint on the cap. The drawing gives them in its drawn pose; carried back to rest by that pose."""
    Qd, _, Jd = pose_of(DRAWN)
    Pd = soma_places(Jd, DRAWN)
    out = {}
    # rebuild the drawn accents
    cast.skel = lambda Bx, P: Jd
    try:
        _, _, accd = cast.savely()
    finally:
        cast.skel = _real_skel
    byk = {a['kind']: a for a in accd}

    def back(p, joint):
        j = IDX[joint]
        local = qrot(qconj(Qd[j]), np.asarray(p) - Pd[joint])
        return (REST[j] + local) * CM

    out['watch'] = dict(joint='LeftHand', rest=back(byk['watch']['p'], 'LeftHand').tolist(), r=byk['watch']['r'] * CM,
                        col=byk['watch']['col'])
    out['pocket'] = dict(joint='Chest', rest=back(byk['chain']['a'], 'Chest').tolist(), col=byk['chain']['col'])
    out['glint'] = dict(joint='Head', rest=back(byk['glint']['p'], 'Head').tolist(), r=byk['glint']['r'] * CM,
                        col=byk['glint']['col'])
    # the loupe's axis (its glass looks along it): from the tube's base to its end, in the head's rest
    lb = np.array([B['W'] * .42, -0.14 * B['H'] + .74 * B['H'], B['Dp'] * 1.02])
    le = lb + [0, .6, 3.2]
    out['glint']['dir'] = unit(le - lb).tolist()
    # the chain's length: as drawn, a little slack over the straight distance
    out['chain'] = dict(length=float(np.linalg.norm(np.asarray(byk['chain']['a']) - np.asarray(byk['chain']['b'])) * 1.12 * CM))
    return out


def main():
    M, J, acc = build_mesh()
    P, T, SJ, SW, PART = M.arrays()
    floor = float(P[:, 1].min())
    header = dict(format='engine/body', version=1, id='savely-s6', label={'ru': 'Савелий Петрович (С6)'},
                  source='styles/s6-symbolic cast.savely solids on SOMA (to3d/r8-s6-savely/tools/build.py)',
                  skeleton=SK['id'], topology='savely-s6', parts=M.parts, vertices=int(len(P)))
    pack.write(os.path.join(OUT, 'savely.json'), header, {
        'positions': P, 'triangles': T, 'skinJoints': SJ, 'skinWeights': SW, 'part': PART,
        'joints': (REST * CM).astype(np.float32), 'frames': FRAMES.astype(np.float32)})
    poses = {'names': NAMES, 'parent': PARENT, 'floor': floor}
    # the drawn stand and the turnaround: static poses of all joints
    Qd, hip, _ = pose_of(DRAWN)
    poses['drawn'] = dict(Q=np.round(Qd, 6).tolist(), hips=(hip * CM).tolist())
    Qn, hipn, _ = pose_of({})
    poses['rest'] = dict(Q=np.round(Qn, 6).tolist(), hips=(hipn * CM).tolist())
    moods = {}
    for key, m in MOODS.items():
        Q, hip, _ = pose_of(m['pose'])
        L = locals_of(Q)
        # the lean is the trunk's, not the legs': moved from the pelvis to Spine1
        trunk = {n: L[IDX[n]].tolist() for n in LAYER_TRUNK}
        trunk['Spine1'] = qmul(L[IDX['Hips']], L[IDX['Spine1']]).tolist()
        moods[key] = dict(label=m['label'], arms=m['arms'], trunk=trunk,
                          armLocals={n: L[IDX[n]].tolist() for n in LAYER_ARMS},
                          Q=np.round(Q, 6).tolist(), hips=(hip * CM).tolist())
    poses['moods'] = moods
    poses['accents'] = accents(acc)
    json.dump(poses, open(os.path.join(OUT, 'poses.json'), 'w'))
    print('vertices', len(P), 'triangles', len(T), 'parts', M.parts, 'floor', floor,
          'height', float(P[:, 1].max() - floor))


if __name__ == '__main__':
    main()
