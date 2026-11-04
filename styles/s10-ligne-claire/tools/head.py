"""A head built for the ligne-claire renderer: skull and face from horizontal slices, nose and lips as bumps,
ears as tilted sheets, a neck, hair as a shell with a hairline, and marks (eyes, brows, mouth, wrinkles) drawn on
the surface.  Units: the head from crown to chin is about 200; y = 0 is the eye line; y grows downward; z toward
the viewer when the head looks at us; x to the viewer's right in the front view.

A character is a dict of parameters (see DEFAULT) plus optional extra parts and marks; see cast.py.
"""
import math
import numpy as np
from scipy.interpolate import PchipInterpolator
import lc, r3

# slice table rows: y, half width w, z of the widest point zm, front z at the middle zf, back z zb, front exponent n
DEFAULT = dict(
    slices=[
        (-104, 6, -14, -6, -22, 2.0),
        (-96, 36, -12, 22, -50, 2.0),
        (-80, 58, -10, 46, -78, 2.1),
        (-60, 69, -8, 62, -95, 2.2),
        (-40, 73, -6, 70, -100, 2.3),
        (-20, 74, -4, 74, -100, 2.4),
        (0, 72, -2, 76, -94, 2.6),
        (20, 69, 0, 77, -82, 2.6),
        (40, 63, 4, 78, -60, 2.5),
        (55, 57, 8, 78, -36, 2.4),
        (70, 49, 14, 76, -8, 2.3),
        (82, 39, 24, 73, 18, 2.2),
        (92, 26, 40, 67, 40, 2.1),
        (98, 10, 55, 60, 50, 2.0),
    ],
    # nose: rows y, extra height at the middle, half width
    nose=[(-4, 0, 7), (6, 3, 7), (18, 9, 8), (30, 16, 9), (36, 17, 12), (40, 10, 13), (43, 2, 12), (45, 0, 10)],
    lips=[(47, 0, 18), (50, 2.5, 20), (54, 2, 21), (56, 0.5, 21), (59, 2.2, 18), (63, 1.5, 14), (67, 0, 10)],
    chin=[(72, 0, 18), (82, 3, 22), (90, 3, 20), (96, 0, 12)],
    brow=[(-22, 0, 40), (-14, 2.5, 46), (-8, 1.5, 44), (-2, 0, 30)],
    ear=dict(y=10, z=-16, ry=19, rz=11, out=13, tilt=0.12),
    neck=dict(z=-8, rx=31, rz=34, y0=40, y1=170),
    eye=dict(x=27, y=0, kind='lid'),
    mouth=dict(y=56),
    thr=6.0,
)


class Head:
    def __init__(self, **kw):
        p = dict(DEFAULT)
        p.update(kw)
        self.p = p
        rows = np.array(p['slices'], float)
        self.ymin, self.ymax = rows[0, 0], rows[-1, 0]
        self._f = {k: PchipInterpolator(rows[:, 0], rows[:, i]) for i, k in enumerate(['w', 'zm', 'zf', 'zb', 'n'], 1)}
        self.bumps = {}
        for k in ('nose', 'lips', 'chin', 'brow'):
            if p.get(k):
                r = np.array(p[k], float)
                self.bumps[k] = (r[0, 0], r[-1, 0], PchipInterpolator(r[:, 0], r[:, 1]), PchipInterpolator(r[:, 0], r[:, 2]))
        self.extra_parts = []      # callables (head) -> [Part]
        self.marks = []            # callables (head, expr) -> [mark]

    # ---------------------------------------------------------------- geometry
    def sl(self, y):
        y = np.clip(y, self.ymin, self.ymax)
        return [self._f[k](y) for k in ('w', 'zm', 'zf', 'zb', 'n')]

    def base_z(self, x, y):
        w, zm, zf, zb, n = self.sl(y)
        a = np.clip(np.abs(x) / np.maximum(w, 1e-3), 0, 1)
        return zm + (zf - zm) * (1 - a ** n) ** (1 / n)

    def bump(self, k, x, y):
        if k not in self.bumps:
            return 0 * x
        y0, y1, h, hw = self.bumps[k]
        yy = np.clip(y, y0, y1)
        inside = (y >= y0) & (y <= y1)
        t = np.clip(1 - (np.asarray(x) / np.maximum(hw(yy), 1e-3)) ** 2, 0, 1)
        return np.where(inside, h(yy) * t ** 0.8, 0)

    def face_z(self, x, y):
        z = self.base_z(x, y)
        for k in self.bumps:
            z = z + self.bump(k, x, y)
        return z

    def frame(self, x, y, e=0.6):
        """Surface point and tangent frame (T along x, B along y, N outward) at face position (x, y)."""
        z = self.face_z(x, y)
        dzx = (self.face_z(x + 0.5, y) - self.face_z(x - 0.5, y))
        dzy = (self.face_z(x, y + 0.5) - self.face_z(x, y - 0.5))
        T = np.array([1, 0, dzx]); T /= np.linalg.norm(T)
        B = np.array([0, 1, dzy]); B /= np.linalg.norm(B)
        N = np.cross(T, B); N /= np.linalg.norm(N)
        N = -N if N[2] < 0 else N
        return np.array([x, y, z]) + N * e, T, B, N

    def on_face(self, x, y, uv, flip=False, scale=1.0, rot=0.0):
        """Map 2D mark points (u right, v down) placed at face position (x, y) onto the surface."""
        out = []
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for u, v in uv:
            u, v = u * scale, v * scale
            u, v = u * c - v * s, u * s + v * c
            if flip:
                u = -u
            px, py = x + u, y + v
            out.append([px, py, float(self.face_z(px, py)) + 0.6])
        return np.array(out)

    # ---------------------------------------------------------------- parts
    def skull_part(self, res=2.4):
        nu, nv = int(2 * np.pi * 85 * res * 1.3), int((self.ymax - self.ymin) * res * 1.5)
        def fn(u, v):
            y = self.ymin + (self.ymax - self.ymin) * v
            w, zm, zf, zb, n = self.sl(y)
            a = u * 2 * np.pi
            ca, sa = np.cos(a), np.sin(a)
            front = sa >= 0
            ex = 2 / n
            X = np.where(front, w * np.sign(ca) * np.abs(ca) ** ex, w * ca)
            Z = np.where(front, zm + (zf - zm) * np.abs(sa) ** ex, zm - (zm - zb) * np.abs(sa))
            # bumps on the front
            if 'brow' in self.bumps:
                Z = Z + np.where(front, self.bump('brow', X, y), 0)
            return X, y, Z
        X, Y, Z = r3.grid(fn, nu, nv)

        def front(u, v):     # the superellipse angle is sparse at the middle of the face: add even-x samples
            y = self.ymin + (self.ymax - self.ymin) * v
            w = self.sl(y)[0]
            x = (u * 2 - 1) * w
            return x, y, self.base_z(x, y) + self.bump('brow', x, y)
        X2, Y2, Z2 = r3.grid(front, int(160 * res), nv)
        return r3.Part('skull', 'skin', np.concatenate([X.ravel(), X2.ravel()]),
                       np.concatenate([Y.ravel(), Y2.ravel()]), np.concatenate([Z.ravel(), Z2.ravel()]))

    def bump_part(self, k, name=None, res=2.4):
        y0, y1, h, hw = self.bumps[k]
        nv = int((y1 - y0) * res * 1.6) + 4
        nu = int(2 * float(np.max(hw(np.linspace(y0, y1, 20)))) * res * 1.6) + 4

        def fn(u, v):
            y = y0 + (y1 - y0) * v
            x = (u * 2 - 1) * hw(y)
            return x, y, self.face_z(x, y) + 0.05
        X, Y, Z = r3.grid(fn, nu, nv)
        return r3.Part(name or k, 'skin', X, Y, Z)

    def ear_part(self, side, res=2.4):
        e = self.p['ear']
        w = float(self.sl(e['y'])[0])

        def fn(u, v):
            r = np.sqrt(u)
            a = v * 2 * np.pi
            dy = e['ry'] * r * np.sin(a)
            dz = e['rz'] * r * np.cos(a)
            # the back edge stands off the head; the lobe is a little narrower
            dz = np.where(dy > 0, dz * (1 - 0.25 * dy / e['ry']), dz)
            xo = w - 3 + e['out'] * (0.25 + 0.75 * np.clip((-dz + e['rz']) / (2 * e['rz']), 0, 1)) * r
            Y = e['y'] + dy - e['tilt'] * dz
            Z = e['z'] + dz
            return side * xo, Y, Z
        X, Y, Z = r3.grid(fn, int(25 * res * 1.5), int(2 * np.pi * 20 * res * 1.5))
        return r3.Part('ear' + ('R' if side > 0 else 'L'), 'skin', X, Y, Z)

    def neck_part(self, res=2.4):
        nk = self.p['neck']

        def fn(u, v):
            a = u * 2 * np.pi
            y = nk['y0'] + (nk['y1'] - nk['y0']) * v
            return nk['rx'] * np.cos(a), y, nk['z'] + nk['rz'] * np.sin(a)
        X, Y, Z = r3.grid(fn, int(2 * np.pi * 36 * res * 1.4), int((nk['y1'] - nk['y0']) * res * 1.5))
        return r3.Part('neck', 'skin', X, Y, Z)

    def parts(self, res=2.4):
        """res: raster pixels per model unit (view scale x supersampling); sampling follows it."""
        ps = [self.skull_part(res)]
        for k in ('nose', 'lips', 'chin'):
            if k in self.bumps:
                ps.append(self.bump_part(k, res=res))
        ps += [self.ear_part(1, res), self.ear_part(-1, res), self.neck_part(res)]
        for f in self.extra_parts:
            ps += f(self, res)
        return ps


# --------------------------------------------------------------------------- hair
class Shell:
    """A closed volume from horizontal slices (like the skull), used for hair masses and clothes."""

    def __init__(self, rows):
        rows = np.array(rows, float)
        self.ymin, self.ymax = rows[0, 0], rows[-1, 0]
        self._f = [PchipInterpolator(rows[:, 0], rows[:, i]) for i in range(1, 6)]

    def sl(self, y):
        return [f(np.clip(y, self.ymin, self.ymax)) for f in self._f]

    def point(self, a, y):
        """a: angle around (0 = viewer's right side, pi/2 = front, pi = left, 3pi/2 = back)."""
        w, zm, zf, zb, n = self.sl(y)
        ca, sa = np.cos(a), np.sin(a)
        front = sa >= 0
        ex = 2 / n
        X = np.where(front, w * np.sign(ca) * np.abs(ca) ** ex, w * ca)
        Z = np.where(front, zm + (zf - zm) * np.abs(sa) ** ex, zm - (zm - zb) * np.abs(sa))
        return X, y + 0 * a, Z

    def part(self, name, material, res, keep=None, y0=None, y1=None):
        y0 = self.ymin if y0 is None else y0
        y1 = self.ymax if y1 is None else y1
        ys = np.linspace(y0, y1, 30)
        size = max(float(np.max(self.sl(ys)[0])), float(np.max(np.abs(self.sl(ys)[2] - self.sl(ys)[3]))) / 2)
        nu, nv = int(2 * np.pi * size * res * 1.3) + 8, int((y1 - y0) * res * 1.5) + 4
        u, v = np.meshgrid(np.linspace(0, 2 * np.pi, nu), np.linspace(y0, y1, nv), indexing='ij')
        X, Y, Z = self.point(u, v)
        # even-x samples on the front, where the superellipse angle is sparse
        uf, vf = np.meshgrid(np.linspace(-1, 1, int(nu * 0.4)), np.linspace(y0, y1, nv), indexing='ij')
        w, zm, zf, zb, n = self.sl(vf)
        Xf = uf * w
        Zf = zm + (zf - zm) * (1 - np.abs(uf) ** n) ** (1 / n)
        Af = np.arccos(np.clip(np.sign(uf) * np.abs(uf) ** (n / 2), -1, 1))
        X, Y, Z, u = (np.concatenate([a.ravel(), b.ravel()]) for a, b in ((X, Xf), (Y, vf), (Z, Zf), (u, Af)))
        if keep is not None:
            m = keep(X, Y, Z, u)
            X, Y, Z = X[m], Y[m], Z[m]
        return r3.Part(name, material, X, Y, Z)

    def curve(self, pts):
        """3D points on the shell from (angle in degrees, y) pairs; angle 90 = front middle."""
        a = np.radians([p[0] for p in pts])
        y = np.array([p[1] for p in pts], float)
        X, Y, Z = self.point(a, y)
        return np.stack([X, Y, Z], 1)


# --------------------------------------------------------------------------- marks
class Mark:
    """A 3D polyline or closed shape drawn on top of the regions."""

    def __init__(self, pts, kind='line', w=1.0, fill=None, stroke=lc.INK, corners=(), tol=4.0, whole=False, on='skin'):
        self.on = on
        self.pts, self.kind, self.w, self.fill, self.stroke = np.asarray(pts, float), kind, w, fill, stroke
        self.corners, self.tol, self.whole = corners, tol, whole


def draw_marks(marks, R, lw):
    out = []
    for m in marks:
        vis, x, y = R.visible(m.pts[:, 0], m.pts[:, 1], m.pts[:, 2], m.tol)
        pts = list(zip(x, y))
        if m.kind == 'shape':
            if vis.mean() < 0.6:
                continue
            out.append(lc.shape(pts, m.fill, lw * m.w if m.w else 0, corners=m.corners, stroke=m.stroke))
        else:
            if m.whole:
                if vis.mean() < 0.6:
                    continue
                vis = np.ones(len(vis), bool)
            for run in r3.runs(vis, closed=False):
                if len(run) >= 2:
                    out.append(lc.line([pts[i] for i in run], lw * m.w, stroke=m.stroke,
                                       corners=[c - run[0] for c in m.corners if run[0] <= c <= run[-1]]))
    return out


def draw(head, view, box, colours, expr=None, lw=lc.LINE, clip_id='fc'):
    """Render a head (with its parts and marks) for one view. Returns (svg items, Render)."""
    parts = head.parts(view.s * view.ss)
    R = r3.Render(parts, view, box, thr=head.p.get('thr', 6.0))
    out = R.fills(colours)
    out += R.lines(lw)
    marks = []
    for f in head.marks:
        marks += f(head, expr or {}, view)
    # marks are clipped to the material they lie on, so nothing crosses a contour in near-profile views
    for mat in sorted(set(m.on for m in marks)):
        ms = [m for m in marks if m.on == mat]
        cid = f'{clip_id}-{mat}'
        out.append(f'<defs>{R.clip_path([mat], cid)}</defs><g clip-path="url(#{cid})">'
                   + ''.join(draw_marks(ms, R, lw)) + '</g>')
    return out, R
