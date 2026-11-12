"""Р50 — Марат, низкополигональный (С19) → 3D.

The С19 drawing is a real 3D model already (styles/s19-lowpoly/tools: poly.py, body.py, face.py, marat.py): convex
facet pieces on a small skeleton, each face lit as a plane. Here the same code builds the same pieces in the drawing's
turnaround stand, and they are hung on SOMA's skeleton so that Kimodo moves them through the engine:

  1. the drawing's skeleton (body.Skel) in the turnaround pose is the rest; SOMA's 77 joints are placed on it;
  2. the pieces of marat.figure(), built by the same calls, each with a rule for its points' weights: limbs, hands,
     shoes, head, hair, beard — rigid on their bone; a faceted ball in each knee, elbow, ankle and wrist (the drawing
     fills a bent joint with a hull — a ball does it at every angle); the shoulder slope between chest and arm; the
     apron's hem partly on the thighs (so the legs don't walk through it);
  3. stripes and buttons (decals) are carried as flat polygons with the weights of the facet they lie on;
  4. the face's features are not baked: the head's front facets take a drawn layer (web/face.js);
     the jaw and the beard keep the drawing's two moves — `open` and `drop` — as per-vertex offsets;
  5. frames: turn(SOMA bone → our bone) · SOMA's frame for the limbs (Kimodo's bones are followed with our lengths),
     the hands by two axes (the bone and the palm), SOMA's own frames for the trunk and head;
  6. the drawing's poses (stand — the laughing one with the ladle) as joint turns: exact, frame over frame.

Writes web/data/marat.{json,bin} (an engine body + topology in one pack), web/data/poses.json, web/data/face.json.
python3 build.py
"""
import sys, os, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'styles', 's19-lowpoly', 'tools'))
sys.path.insert(0, os.path.join(REPO, 'engine', 'tools'))
import poly as PL, body as B, face as F, marat as M, pack   # noqa: E402
from poly import hull, ring, frame_along, press, face_planes, hexcol, tohex, mix   # noqa: E402

OUT = os.path.join(HERE, 'web', 'data')
os.makedirs(OUT, exist_ok=True)
CM = 0.01
REST_POSE = 'turn'
REST_OPEN = 1.0          # the hulls' faces are taken at his rest laugh

# ------------------------------------------------------------------ quaternions [x, y, z, w]


def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz])


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


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def qbetween(a, b):
    a = unit(a); b = unit(b)
    d = float(a @ b)
    if d < -0.999999:
        ax = np.cross(a, [1, 0, 0]) if abs(a[0]) < .9 else np.cross(a, [0, 1, 0])
        return np.array([*unit(ax), 0.0])
    q = np.array([*np.cross(a, b), 1 + d])
    return q / np.linalg.norm(q)


def basis(d, n):
    """An orthonormal frame from a bone direction and a second direction (made square to it)."""
    d = unit(d); n = unit(np.asarray(n, float) - np.dot(n, d) * d)
    return np.column_stack([d, n, np.cross(d, n)])


# ------------------------------------------------------------------ SOMA
SK = json.load(open(os.path.join(REPO, 'engine', 'data', 'skeleton.json')))
NAMES = [j['name'] for j in SK['joints']]
IDX = {n: i for i, n in enumerate(NAMES)}
PARENT = [j['parent'] for j in SK['joints']]
S_REST = np.array([j['rest'] for j in SK['joints']]) / CM          # SOMA's rest in cm
S_FRAME = np.array([j['frame'] for j in SK['joints']])
NJ = len(NAMES)
SIDE = {'L': 'Left', 'R': 'Right'}      # body.py: 'L' is the figure's left, +x — as the engine's


def soma_places(sk):
    """SOMA's joints (cm) on the drawing's skeleton. The drawing bends the trunk at one place — the waist — so
    SOMA's three spine joints sit close under it: the belly stays with the pelvis, the chest turns about the waist."""
    p = sk.p; sc = p['head_scale']; S = M.SPEC
    up = lambda R, L: R @ np.array([0, L, 0])
    P = {'Hips': sk.P, 'Spine1': sk.P + up(sk.Rp, .55 * p['waist']), 'Spine2': sk.P + up(sk.Rp, .85 * p['waist']),
         'Chest': sk.waist, 'Neck1': sk.neckb, 'Neck2': sk.neckb + up(sk.Rn, .5 * p['neck']), 'Head': sk.necktop,
         'HeadEnd': sk.head + sk.Rh @ np.array([0, S['crown'] * sc, 0]),
         'Jaw': sk.head + sk.Rh @ (sc * np.array([0, -3.0, 3.0]))}
    for k, s in SIDE.items():
        J = sk.j[k]; sg = J['s']
        P[s + 'Eye'] = sk.head + sk.Rh @ (sc * np.array([sg * S['eye_x'], S['eye_y'], S['face_z']]))
        P[s + 'Shoulder'] = sk.neckb + sk.Rc @ np.array([sg * 5.0, -2.5, -1.0])
        P[s + 'Arm'] = J['sh']; P[s + 'ForeArm'] = J['el']; P[s + 'Hand'] = J['wr']
        P[s + 'HandMiddle1'] = J['wr'] + J['Rh'] @ np.array([0, -.5 * p['hand'], 0])
        P[s + 'Leg'] = J['hip']; P[s + 'Shin'] = J['kn']; P[s + 'Foot'] = J['an']
        P[s + 'ToeBase'] = J['an'] + J['Rft'] @ np.array([0, -p['ankle_h'] + 2.0, .45 * p['foot']])
        P[s + 'ToeEnd'] = J['an'] + J['Rft'] @ np.array([0, -p['ankle_h'] + 1.0, .78 * p['foot']])
    return P


def seg_frames(sk):
    """Each SOMA joint's part of the drawing's skeleton: its rotation (3×3)."""
    R = {'Hips': sk.Rp, 'Spine1': sk.Rp, 'Spine2': sk.Rp, 'Chest': sk.Rc, 'Neck1': sk.Rn, 'Neck2': sk.Rn, 'Head': sk.Rh}
    for k, s in SIDE.items():
        J = sk.j[k]
        R.update({s + 'Shoulder': sk.Rc, s + 'Arm': J['Ru'], s + 'ForeArm': J['Rf'], s + 'Hand': J['Rh'],
                  s + 'Leg': J['Rt'], s + 'Shin': J['Rs'], s + 'Foot': J['Rft']})
    out = []
    for j in range(NJ):
        n = NAMES[j]
        out.append(R[n] if n in R else out[PARENT[j]])
    return out


SK0 = B.Skel(M.PROP, M.POSES[REST_POSE])
P0 = soma_places(SK0)


def rest_joints():
    R = np.zeros((NJ, 3))
    for j in range(NJ):
        n = NAMES[j]
        R[j] = P0[n] if n in P0 else R[PARENT[j]] + (S_REST[j] - S_REST[PARENT[j]])
    return R


REST = rest_joints()


def rest_frames():
    Fr = S_FRAME.copy()
    bone = {}
    for s in ('Left', 'Right'):
        bone.update({s + 'Arm': s + 'ForeArm', s + 'ForeArm': s + 'Hand', s + 'Leg': s + 'Shin', s + 'Shin': s + 'Foot',
                     s + 'Foot': s + 'ToeBase', s + 'ToeBase': s + 'ToeEnd'})
    for n, child in bone.items():
        j, c = IDX[n], IDX[child]
        Fr[j] = qmul(qbetween(S_REST[c] - S_REST[j], REST[c] - REST[j]), S_FRAME[j])
    # the hands by two axes: along the hand, and the palm's normal (the thumb says which side the palm is)
    for k, s in SIDE.items():
        J = SK0.j[k]; sg = J['s']; h = IDX[s + 'Hand']
        d_s = unit(S_REST[IDX[s + 'HandMiddle2']] - S_REST[h])      # to the knuckle (Middle1 sits in the wrist)
        n_s = np.cross(S_REST[IDX[s + 'HandIndex2']] - S_REST[h], S_REST[IDX[s + 'HandPinky2']] - S_REST[h])
        n_s = unit(n_s - np.dot(n_s, d_s) * d_s)
        th = S_REST[IDX[s + 'HandThumb2']] - S_REST[h]
        if np.dot(th, -sg * np.cross(d_s, n_s)) < 0:
            n_s = -n_s
        d_m = J['Rh'] @ np.array([0, -1.0, 0]); n_m = J['Rh'] @ np.array([-sg, 0, 0])
        r = basis(d_m, n_m) @ basis(d_s, n_s).T
        Fr[h] = qmul(mat2q(r), S_FRAME[h])
        for j in range(NJ):
            if NAMES[j].startswith(s + 'Hand') and j != h:
                Fr[j] = qmul(mat2q(r), S_FRAME[j])
    return Fr


FRAMES = rest_frames()
SEG0 = seg_frames(SK0)


def pose_of(name):
    """A drawn pose as every joint's turn from the rest (world) and the pelvis's place (cm)."""
    sk = B.Skel(M.PROP, M.POSES[name])
    seg = seg_frames(sk)
    Q = np.array([mat2q(seg[j] @ SEG0[j].T) for j in range(NJ)])
    return Q, sk.P


# ------------------------------------------------------------------ the pieces and their weights

def ball(c, R, r, n, phase=30.0, lat=48.0):
    """A faceted ball in a joint: the limb's own ring, a smaller ring above and below, two poles. Whatever the bend,
    it fills the wedge between the two prisms that meet there."""
    y = R[:, 1]; a = math.radians(lat)
    pts = ring(c, R, r, r, n, phase)
    pts += ring(c + y * r * math.sin(a), R, r * math.cos(a), r * math.cos(a), n, phase + 180.0 / n)
    pts += ring(c - y * r * math.sin(a), R, r * math.cos(a), r * math.cos(a), n, phase + 180.0 / n)
    return pts + [c + y * r, c - y * r]


def smooth01(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def parts(sk, e):
    """→ [(piece, weights rule, group)] in the rest pose. A rule is a joint's name (rigid) or f(point) → {joint: w}.
    The calls are marat.figure()'s, line for line; what is added: the joint balls, the open hands."""
    c = M.COL; out = []
    add = lambda pcs, rule, group='body': out.extend((p, rule, group) for p in (pcs if isinstance(pcs, list) else [pcs]))
    for k, s in SIDE.items():
        J = sk.j[k]
        th, sh1, sh2 = B.leg(sk, k, (10.0, 7.6, 8.0, 5.6), c['trousers'], 'cloth', n=7)[:3]
        add(th, s + 'Leg'); add([sh1, sh2], s + 'Shin')
        add(hull(ball(J['kn'], frame_along(J['an'] - J['kn']), 7.6, 7), c['trousers'], 'cloth', 'knee'), s + 'Shin')
        add(hull(ball(J['an'], frame_along(J['an'] - J['kn']), 5.6, 7), c['trousers'], 'cloth', 'ankle'), s + 'Shin')
        add(B.shoe(sk, k, c['shoe'], sole=c['sole']), s + 'Foot')
    # the jacket: the belly with the pelvis, the chest turning about the waist
    add(B.torso_hull(sk, 'p', 'p', [(20, 22.0, 14.4, 12.0, 10, 6.0), (6, 22.6, 14.0, 12.4, 10, 5.0),
                                    (-8, 20.0, 11.6, 11.6, 10, 1.0)], c['jacket'], name='belly'), 'Hips')
    jacket = B.torso_hull(sk, 'c', 'w', [(-2, 22.6, 14.6, 12.4, 10, 5.4), (14, 24.6, 14.2, 12.8, 10, 3.0),
                                         (26, 24.4, 11.0, 11.0, 10, 0.6), (32.5, 15.0, 7.0, 7.8, 10, 0), (35.0, 8.0, 5.0, 5.8, 8, 0)],
                          c['jacket'], name='jacket')
    for i in range(3):
        for x in (-4.6, 4.6):
            y = 8 + i * 6.5
            press(jacket, sk.at('c', 'w', [(x + dx, y + dy, 40) for dx, dy in [(-0.8, 0), (0, 0.8), (0.8, 0), (0, -0.8)]]),
                  c['button'], 1.0, dir=tuple(sk.Rc[:, 2]), lift=0.12)
    add(jacket, 'Chest')
    # the apron: the bib on the chest, the waist with the pelvis, the hem's halves going with the thighs
    ap = B.torso_hull(sk, 'p', 'p', [(33, 10.0, 17.0, -10.0, 8, 5.0), (26, 17.0, 18.0, -8.0, 8, 6.0), (18, 21.0, 18.4, -7.0, 8, 7.4),
                                     (4, 23.8, 17.4, -5.0, 8, 6.4), (-42, 23.0, 14.2, -5.0, 8, 0)], c['apron'], name='apron')
    B.band(ap, sk, 'p', 'p', 15.2, 17.2, c['apron2'], n=16, a0=-80, a1=80)

    def apron_w(q):
        y = q[1] - sk.P[1]; x = q[0] - sk.P[0]
        if y > 0:
            t = smooth01(8.0, 24.0, y)
            return {'Hips': 1 - t, 'Chest': t}
        t = 0.72 * smooth01(-2.0, -42.0, y)
        left = 1 / (1 + math.exp(-x / 7.0))
        return {'Hips': 1 - t, 'LeftLeg': t * left, 'RightLeg': t * (1 - left)}
    add(ap, apron_w)
    add(B.torso_hull(sk, 'c', 'c', [(-2.5, 9.0, 7.8, 6.8, 8, 0), (1.6, 7.6, 6.4, 6.4, 8, 0)], c['jacket'], name='collar'), 'Chest')
    add(B.limb(sk.neckb - sk.Rc @ np.array([0, 2.0, 0]), sk.necktop + sk.Rn @ np.array([0, 2.6, 0]),
               6.6, 6.0, c['skin'], 'skin', ext=0.1, name='neck'), 'Neck2')
    for k, s in SIDE.items():
        J = sk.j[k]
        # the slope from the neck to the arm: its inner points with the chest, the rings with the arm
        shp = B.shoulder(sk, k, 7.6, c['jacket'], inner=8.0, top=2.6)
        idx = {tuple(np.round(p, 6)): i for i, p in enumerate(shp.pts)}
        add(shp, lambda q, s=s, idx=idx: ({'Chest': 1.0} if idx[tuple(np.round(q, 6))] < 3 else
                                          {s + 'Arm': .6, 'Chest': .4} if idx[tuple(np.round(q, 6))] < 9 else {s + 'Arm': 1.0}))
        mid = J['sh'] + 0.62 * (J['el'] - J['sh'])
        add(B.chain([J['sh'], mid], (7.6, 6.8), c['jacket'], cap=(0.3, 0.0)), s + 'Arm')
        add(B.limb(mid - 0.06 * (J['el'] - J['sh']), mid + 0.1 * (J['el'] - J['sh']), 7.6, 7.4, c['jacket'], ext=0.0, n=8, name='roll'), s + 'Arm')
        up, fo = B.chain([mid, J['el'], J['wr']], (6.0, 5.6, 4.4), c['skin'], 'skin', cap=(0.0, 0.2))[:2]
        add(up, s + 'Arm'); add(fo, s + 'ForeArm')
        Rf = frame_along(J['wr'] - J['el'])
        add(hull(ball(J['el'], Rf, 5.6, 6), c['skin'], 'skin', 'elbow'), s + 'ForeArm')
        add(hull(ball(J['wr'], Rf, 4.4, 6), c['skin'], 'skin', 'wrist'), s + 'ForeArm')
        add(B.hand(sk, k, c['skin'], 'fist'), s + 'Hand', 'fist' + k)
        add(B.hand(sk, k, c['skin'], 'open'), s + 'Hand', 'open' + k)
    add(M.ladle(sk, 'R'), 'RightHand', 'ladle')
    add(M.towel(sk), 'Chest')
    head = F.head(M.SPEC, e) + M.hair(e)
    for pc in head[:4]:
        pc.decals = []          # the features are drawn alive in the browser (web/face.js)
    add(sk.place_head(head), 'Head', 'head')
    return out


# ------------------------------------------------------------------ the mesh

def tri_weights(piece, W, p):
    """Weights of a decal's point: those of the piece's triangle it lies on (barycentric)."""
    best = None
    for f in piece.faces:
        for a in range(1, len(f) - 1):
            ia, ib, ic = f[0], f[a], f[a + 1]
            A, Bp, C = piece.pts[ia], piece.pts[ib], piece.pts[ic]
            n = np.cross(Bp - A, C - A); nn = np.linalg.norm(n)
            if nn < 1e-9:
                continue
            n = n / nn
            q = p - n * np.dot(p - A, n)
            T = np.column_stack([Bp - A, C - A])
            uv, *_ = np.linalg.lstsq(T, q - A, rcond=None)
            b = np.array([1 - uv[0] - uv[1], uv[0], uv[1]])
            cost = abs(np.dot(p - A, n)) + 10 * max(0.0, -b.min())
            if best is None or cost < best[0]:
                best = (cost, (ia, ib, ic), np.clip(b, 0, None))
    _, ids, b = best
    b = b / b.sum(); w = {}
    if not hasattr(tri_weights, 'n'):
        tri_weights.n = {}
    tri_weights.n[id(piece), tuple(np.round(p, 6))] = np.cross(piece.pts[ids[1]] - piece.pts[ids[0]], piece.pts[ids[2]] - piece.pts[ids[0]])
    for i, bi in zip(ids, b):
        for j, v in W[i].items():
            w[j] = w.get(j, 0) + bi * v
    return w


def build_mesh():
    e0 = dict(M.EXPR['rest'])
    base = parts(SK0, dict(e0, open=REST_OPEN))
    # the two moves of the jaw and beard, as the drawing has them: `open` and `drop` = max(0, open − 0.6) · 1.2
    at = lambda o: [p for p, _, g in parts(SK0, dict(e0, open=o)) if g == 'head']
    h0, h6, h16 = at(0.0), at(0.6), at(1.6)
    P, W, T, PC, DO, DD, FXY = [], [], [], [], [], [], []
    pieces = []; n = 0; hi = 0
    for pc, rule, group in base:
        pts = pc.pts
        ws = [({rule: 1.0} if isinstance(rule, str) else rule(q)) for q in pts]
        tris = [(f[0], f[a], f[a + 1]) for f in pc.faces for a in range(1, len(f) - 1)]
        d_open = np.zeros_like(pts); d_drop = np.zeros_like(pts); fxy = np.zeros((len(pts), 2))
        if group == 'head':
            a, b, cc = h0[hi].pts, h6[hi].pts, h16[hi].pts; hi += 1
            d_open = (b - a) / 0.6
            d_drop = (cc - a - 1.6 * d_open) / 1.2
            pts = a
            if pc.name == 'head':
                fxy = (a - SK0.head)[:, :2] / SK0.p['head_scale']        # head space (cm): the rest head is upright
        rec = dict(name=pc.name or pc.mat, group=group, color=[round(float(v), 4) for v in pc.color], mat=pc.mat,
                   v0=n, vn=len(pts), t0=sum(len(t) for t in T), tn=len(tris), decal=False,
                   face=(group == 'head' and pc.name == 'head'))
        pieces.append(rec)
        P.append(pts); W += ws; T.append(np.array(tris) + n); PC += [len(pieces) - 1] * len(pts)
        DO.append(d_open); DD.append(d_drop); FXY.append(fxy); n += len(pts)
        for dpts, col, op in pc.decals:
            dw = [tri_weights(pc, ws, q) for q in dpts]
            m = len(dpts)
            newell = sum(np.cross(dpts[i], dpts[(i + 1) % m]) for i in range(m))
            if np.dot(newell, tri_weights.n[id(pc), tuple(np.round(dpts[0], 6))]) < 0:   # counter-clockwise seen from outside
                dpts = dpts[::-1]; dw = dw[::-1]
            pieces.append(dict(name='decal', group=group, color=[round(float(v), 4) for v in col], mat='decal', v0=n, vn=m,
                               t0=sum(len(t) for t in T), tn=m - 2, decal=True, face=False, opacity=op))
            P.append(dpts); W += dw; T.append(np.array([(0, a, a + 1) for a in range(1, m - 1)]) + n)
            PC += [len(pieces) - 1] * m
            DO.append(np.zeros_like(dpts)); DD.append(np.zeros_like(dpts)); FXY.append(np.zeros((m, 2))); n += m
    P = np.vstack(P) * CM
    N = len(P)
    SJ = np.zeros((N, 4), np.uint8); SW = np.zeros((N, 4), np.float32)
    for i, w in enumerate(W):
        items = sorted(((k, v) for k, v in w.items() if v > 1e-4), key=lambda kv: -kv[1])[:4]
        s = sum(v for _, v in items)
        for k, (jn, v) in enumerate(items):
            SJ[i, k] = IDX[jn]; SW[i, k] = v / s
    return dict(positions=P.astype(np.float32), triangles=np.vstack(T).astype(np.uint16), skinJoints=SJ, skinWeights=SW,
                piece=np.array(PC, np.uint16), dOpen=(np.vstack(DO) * CM).astype(np.float32),
                dDrop=(np.vstack(DD) * CM).astype(np.float32), faceXY=np.vstack(FXY).astype(np.float32)), pieces


def face_json():
    """What web/face.js needs of the drawing's numbers."""
    s = F.S(M.SPEC)
    keys = ['skin', 'lip', 'eye', 'brow', 'eye_x', 'eye_y', 'eye_w', 'eye_h', 'eye_tilt', 'iris', 'lid_th', 'lash',
            'brow_th', 'brow_len', 'brow_lift', 'brow_in', 'brow_arch', 'lip_w', 'lip_h', 'mouth_y', 'mouth_line',
            'smile', 'cheek_col', 'cheek_w', 'cheek_y']
    return dict(spec={k: s.get(k, 0) for k in keys}, expr=M.EXPR, head_scale=M.PROP['head_scale'],
                head=(SK0.head * CM).tolist(), light=dict(key=list(PL.Light().key), fill=list(PL.Light().fill)),
                bg=['#f0d6bf', '#c99e86'], plinth=dict(r=M.PLINTH * CM, h=0.04, color='#5f5b6b', n=12))


def main():
    arrays, pieces = build_mesh()
    arrays['joints'] = (REST * CM).astype(np.float32)
    arrays['frames'] = FRAMES.astype(np.float32)
    header = dict(format='engine/body', version=1, id='marat-s19', label={'ru': 'Марат (С19)'},
                  source='styles/s19-lowpoly marat.figure pieces on SOMA (to3d/r50-s19-marat/tools/build.py)',
                  skeleton=SK['id'], topology='marat-s19', vertices=int(len(arrays['positions'])), pieces=pieces)
    pack.write(os.path.join(OUT, 'marat.json'), header, arrays)
    poses = {}
    for name in ('turn', 'stand', 'portrait'):
        Q, hip = pose_of(name)
        poses[name] = dict(Q=np.round(Q, 6).tolist(), hips=(hip * CM).tolist(),
                           head=(B.Skel(M.PROP, M.POSES[name]).head * CM).tolist())
    json.dump(poses, open(os.path.join(OUT, 'poses.json'), 'w'))
    json.dump(face_json(), open(os.path.join(OUT, 'face.json'), 'w'), ensure_ascii=False)
    P = arrays['positions']
    print('vertices', len(P), 'triangles', len(arrays['triangles']), 'pieces', len(pieces),
          'floor', float(P[:, 1].min()), 'top', float(P[:, 1].max()))
    print('groups', sorted({p['group'] for p in pieces}))


if __name__ == '__main__':
    main()
