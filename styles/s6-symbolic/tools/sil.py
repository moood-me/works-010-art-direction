"""Silhouette engine for style S6 «Символический: почти знак».

A figure is built in 3D from a few solids (lofts of rings, tubes of spheres), turned by a yaw angle, projected
orthographically and merged into ONE flat shape (shapely union). That one shape is the figure: drawn in one ink,
with a rim of light cut from its own edge. Accents (a scarf, a lantern, a glint) are separate small shapes.

Units: centimetres. Body frame: x to screen right (front view), y up, z toward the viewer (the figure's forward).
Yaw 0 = facing the viewer, 90 = profile facing screen right, 180 = from behind.
"""
import math
import numpy as np
from shapely.geometry import Point, MultiPoint, Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union

D = math.pi / 180
UP = np.array([0.0, 1.0, 0.0])
FWD = np.array([0.0, 0.0, 1.0])
LAT = np.array([1.0, 0.0, 0.0])


def rx(a):
    c, s = math.cos(a * D), math.sin(a * D)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(a):
    c, s = math.cos(a * D), math.sin(a * D)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(a):
    c, s = math.cos(a * D), math.sin(a * D)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def ldir(flex, abd, side, twist=0.0):
    """Direction of a hanging limb: flex forward (deg), abduct outward (deg) for side ±1."""
    v = rz(side * abd) @ np.array([0.0, -1.0, 0.0])
    return rx(-flex) @ v


def curve(ctrl):
    """Smooth 1-D function through (t, value) control points (Catmull-Rom), returned as f(t)."""
    ctrl = sorted(ctrl)
    ts = np.array([c[0] for c in ctrl], float)
    vs = np.array([c[1] for c in ctrl], float)
    dense_t, dense_v = [], []
    n = len(ts)
    for i in range(n - 1):
        p0 = vs[max(i - 1, 0)]; p1 = vs[i]; p2 = vs[i + 1]; p3 = vs[min(i + 2, n - 1)]
        for k in range(12):
            u = k / 12
            v = 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u +
                       (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
            dense_t.append(ts[i] + (ts[i + 1] - ts[i]) * u); dense_v.append(v)
    dense_t.append(ts[-1]); dense_v.append(vs[-1])
    dt, dv = np.array(dense_t), np.array(dense_v)
    return lambda t: np.interp(t, dt, dv)


def ring(w, df, db, n=40, cx=0.0, cz=0.0):
    """Ellipse-like section: half-width w, front depth df, back depth db; points (x, 0, z)."""
    th = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x = w * np.cos(th) + cx
    z = np.where(np.sin(th) > 0, df, db) * np.sin(th) + cz
    return np.stack([x, np.zeros_like(x), z], 1)


class Fig:
    """Collects solids in body space; projects and merges them."""

    def __init__(self):
        self.lofts = []   # list of (list of Nx3 arrays)
        self.tubes = []   # list of (pts Kx3, radii K)
        self.acc = []     # accents: dict(kind, ...)

    def loft(self, rings):
        self.lofts.append([np.asarray(r, float) for r in rings])

    def tube(self, pts, radii):
        self.tubes.append((np.asarray(pts, float), np.asarray(radii, float)))

    # --- projection ---
    @staticmethod
    def proj(P, yaw):
        R = ry(yaw)
        Q = np.asarray(P, float) @ R.T
        return np.stack([Q[..., 0], -Q[..., 1]], -1), Q[..., 2]

    @staticmethod
    def tube2d(pts, radii, yaw):
        p2, _ = Fig.proj(pts, yaw)
        circles = [Point(*p).buffer(max(r, 0.05), quad_segs=10) for p, r in zip(p2, radii)]
        if len(circles) == 1:
            return circles[0]
        parts = [unary_union([circles[i], circles[i + 1]]).convex_hull for i in range(len(circles) - 1)]
        return unary_union(parts)

    @staticmethod
    def loft2d(rings, yaw):
        parts = []
        r2 = [Fig.proj(r, yaw)[0] for r in rings]
        for i in range(len(r2) - 1):
            parts.append(MultiPoint(np.vstack([r2[i], r2[i + 1]])).convex_hull)
        return unary_union(parts)

    def shape(self, yaw):
        parts = [self.loft2d(l, yaw) for l in self.lofts] + [self.tube2d(p, r, yaw) for p, r in self.tubes]
        g = unary_union(parts)
        g = g.buffer(0.35, quad_segs=6).buffer(-0.35, quad_segs=6).simplify(0.08)   # close seams, round inner corners
        return g

    def depth(self, P, yaw):
        return self.proj(np.asarray(P, float)[None], yaw)[1][0]


def d_of(g, k=1.0, dx=0.0, dy=0.0, nd=1, smooth=2):
    """SVG path data of a shapely geometry, scaled by k and moved."""
    polys = []
    if isinstance(g, Polygon):
        polys = [g]
    elif isinstance(g, (MultiPolygon, GeometryCollection)):
        polys = [p for p in g.geoms if isinstance(p, Polygon)]
    out = []
    fmt = '%.' + str(nd) + 'f'
    for p in polys:
        for r in [p.exterior] + list(p.interiors):
            c = np.asarray(r.coords)[:-1]
            for _ in range(smooth):
                q = np.roll(c, -1, 0)
                c = np.stack([.75 * c + .25 * q, .25 * c + .75 * q], 1).reshape(-1, 2)
            c = c * k + [dx, dy]
            out.append('M' + ' L'.join(fmt % x + ' ' + fmt % y for x, y in c) + 'Z')
    return ''.join(out)


# ---------------------------------------------------------------- skeleton

POSE0 = dict(lean=0, hunch=0, roll=0, shrug=0, slump=0, neck=0, nod=0, headYaw=0, headRoll=0, lift=0,
             hipShift=0,
             armL=(4, 6, 8, 0), armR=(4, 6, 8, 0),          # (flex, abd, forearm flex, forearm abd)
             legL=(0, 3, 0, 0), legR=(0, 3, 0, 0),          # (thigh flex, abd, knee bend, shin abd)
             footL=(0, 8), footR=(0, 8),                     # (pitch: toe down +, toe-out deg)
             handL='hang', handR='hang')


def skel(B, pose):
    p = dict(POSE0); p.update(pose)
    J = {'p': p}
    lean, hunch, roll = p['lean'], p['hunch'], p['roll']
    Rlow = rz(-roll) @ rx(lean)
    Rup = rz(-roll * 1.4) @ rx(lean + hunch)
    pel = np.zeros(3)
    chest = pel + Rlow @ UP * B['lowL']
    neck = chest + Rup @ UP * B['upL']
    J.update(pel=pel, chest=chest, neck=neck, Rlow=Rlow, Rup=Rup)
    Rn = rz(-roll * 1.4) @ rx(lean + hunch + p['neck'])
    ntop = neck + Rn @ UP * B['neckL']
    J['ntop'] = ntop
    J['Rh'] = rz(-roll * 1.4 - p['headRoll']) @ rx(lean + hunch + p['neck'] + p['nod']) @ ry(p['headYaw'])
    lat_up = Rup @ LAT
    lat_low = rz(-roll * 0.4) @ LAT
    for side, key in ((-1, 'L'), (1, 'R')):
        sh = neck - Rup @ UP * B['shDrop'] + lat_up * side * B['shW'] + UP * p['shrug'] + FWD * p['slump']
        f, a, ff, fa = p['arm' + key]
        d1 = ldir(f, a, side); el = sh + d1 * B['armU']
        d2 = ldir(f + ff, a + fa, side); wr = el + d2 * B['armF']
        J['sh' + key], J['el' + key], J['wr' + key], J['dh' + key] = sh, el, wr, d2
        hip = pel + lat_low * side * B['hipW']
        tf, ta, kb, sa = p['leg' + key]
        d1 = ldir(tf, ta, side); kn = hip + d1 * B['thighL']
        d2 = ldir(tf - kb, sa, side); an = kn + d2 * B['shinL']
        pitch, out = p['foot' + key]
        Rf = ry(side * -out) @ rx(pitch)
        fl = B['footL']
        heel = an + np.array([0, -B['ankH'] + B['footR'][0], 0]) + Rf @ FWD * (-0.22 * fl)
        ball = an + np.array([0, -B['ankH'] + B['footR'][1], 0]) + Rf @ FWD * (0.48 * fl)
        toe = an + np.array([0, -B['ankH'] + B['footR'][2], 0]) + Rf @ FWD * (0.74 * fl)
        if pitch:
            # pointed foot: rotate the foot about the ankle
            Rp = rx(pitch)
            heel, ball, toe = [an + Rp @ (q - an) for q in (heel, ball, toe)]
        J.update({'hip' + key: hip, 'kn' + key: kn, 'an' + key: an, 'heel' + key: heel, 'ball' + key: ball,
                  'toe' + key: toe})
    # ground: lowest sole touches y=0, plus lift
    low = min(min(J['heel' + k][1] - B['footR'][0], J['ball' + k][1] - B['footR'][1],
                  J['toe' + k][1] - B['footR'][2]) for k in 'LR')
    shift = np.array([p['hipShift'], -low + p['lift'], 0])
    for k, v in list(J.items()):
        if isinstance(v, np.ndarray) and v.shape == (3,) and not k.startswith('dh'):
            J[k] = v + shift
    return J


def along(J, keys, t):
    """Point at fraction t along the polyline of joints keys."""
    pts = [J[k] for k in keys]
    seg = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    L = sum(seg) * t
    for i, s in enumerate(seg):
        if L <= s or i == len(seg) - 1:
            u = 0 if s == 0 else min(L / s, 1)
            return pts[i] + (pts[i + 1] - pts[i]) * u
        L -= s


def head_rings(J, H, W, Dp, Db, prof, base, width, back, nose_w=1.2, n=56, zc=0.0):
    """Head as rings in head space. prof/base/width/back: functions of v (0 chin .. 1 crown)
    giving the centre-line profile depth, the face front depth, half width, back depth (all × W or Dp)."""
    rings = []
    for v in np.linspace(0, 1, n):
        w = max(width(v) * W, 0.05)
        df = max(base(v) * Dp, 0.05); db = max(back(v) * Db, 0.05)
        r = ring(w, df, db, n=64)
        pz = prof(v) * Dp
        if pz > df:
            extra = np.array([[0, 0, pz], [nose_w * 0.6, 0, pz - nose_w * 0.6], [-nose_w * 0.6, 0, pz - nose_w * 0.6],
                              [nose_w, 0, (pz + df) / 2], [-nose_w, 0, (pz + df) / 2]])
            r = np.vstack([r, extra])
        y = -0.14 * H + v * H
        r = r + [0, y, zc]
        rings.append(r)
    return [J['ntop'] + r @ J['Rh'].T for r in rings]


def to_world(J, pts_local):
    return J['ntop'] + np.asarray(pts_local, float) @ J['Rh'].T


def torso(J, sections, roll_rings=True):
    """sections: list of (t, w, df, db, dz) along pelvis(0)→chest(.5)→neck(1)."""
    rings = []
    for t, w, df, db, dz in sections:
        if t <= 0.5:
            c = J['pel'] + (J['chest'] - J['pel']) * (t / 0.5); R = J['Rlow']
        else:
            c = J['chest'] + (J['neck'] - J['chest']) * ((t - 0.5) / 0.5); R = J['Rup']
        r = ring(w, df, db, cz=dz)
        rings.append(c + r @ R.T)
    return rings


def skirt(J, top, L, flare, legR, n=6, ease=1.0, dz=0.0):
    """Rings from the pelvis ring `top` (w, df, db) down to a hem `L` cm along the legs."""
    w0, df0, db0 = top
    pts = {}
    for k in 'LR':
        pts[k] = along(J, ['hip' + k, 'kn' + k, 'an' + k], min(L / (np.linalg.norm(J['kn' + k] - J['hip' + k]) +
                                                                  np.linalg.norm(J['an' + k] - J['kn' + k])), 1))
    a, b = pts['L'], pts['R']
    cen = (a + b) / 2
    hw = max(w0 + flare, abs(a[0] - b[0]) / 2 + legR + flare * 0.6)
    hd = max((df0 + db0) / 2 + flare * 0.7, abs(a[2] - b[2]) / 2 + legR + flare * 0.5)
    rings = []
    for i in range(n + 1):
        u = i / n
        e = u ** ease
        c = J['pel'] * (1 - u) + cen * u + [0, 0, dz * u]
        w = w0 + (hw - w0) * e
        df = df0 + (hd - df0) * e; db = db0 + (hd - db0) * e
        rings.append(c + ring(w, df, db))
    return rings
