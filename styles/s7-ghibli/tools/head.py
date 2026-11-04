"""The head: a soft 3D form (horizontal rings, a profile along the middle for brow, nose, lips and chin), with the
face drawn as flat templates laid on its surface — eyes, brows, nose mark, mouth, ears, wrinkles, blush — and hair as
a shell over the skull plus locks. Any view (front, three-quarter, side) comes from the same head.

Head-local units: the head is 2 tall (crown y=+1, chin y=-1), x to the character's left as seen from the front
(viewer's right), z forward. `Head.place(center_cm, height_cm, yaw, nod, tilt)` puts it in the model."""
import math
import numpy as np
from scipy.interpolate import PchipInterpolator
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
from geo import poly, hull_union, ribbon, bezier, spline, shift, polys, smooth, resample
from svgdoc import INK, mix, shade


def table(pairs):
    ys, vs = zip(*sorted(pairs))
    f = PchipInterpolator(ys, vs, extrapolate=True)
    return lambda y: np.asarray(f(np.clip(y, ys[0], ys[-1])))


def profile(nose_y, nose=0.14, bridge=0.04, mouth_y=None, lip=0.03, chin=0.02, brow=0.0):
    """the bulge along the middle of the face (head units forward of the plain form): brow, bridge, nose tip,
    under the nose, lips, chin."""
    my = mouth_y if mouth_y is not None else nose_y - 0.22
    return [(0.35, 0.0), (0.18, brow), (0.0, bridge * 0.5), (nose_y + 0.22, bridge), (nose_y + 0.08, nose * 0.65),
            (nose_y, nose), (nose_y - 0.05, nose * 0.4), (nose_y - 0.10, 0.015), (my + 0.03, lip),
            (my - 0.06, 0.0), (my - 0.18, chin), (-1.0, 0.0)]


def rotm(yaw, nod, tilt):
    """head turn (deg): yaw about y (+ face to the viewer's right at view yaw 0), nod about x (+ looks down),
    tilt about z (+ head leans to the viewer's right)."""
    a, b, c = (math.radians(v) for v in (yaw, nod, tilt))
    Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(b), math.sin(b)], [0, -math.sin(b), math.cos(b)]])
    Rz = np.array([[math.cos(c), math.sin(c), 0], [-math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


class Expr(dict):
    """what the face does. Every key has a neutral default."""
    DEF = dict(open=1.0, lid_in=0.0, lid_out=0.0, smile_eye=0.0, closed=0.0, iris=1.0, look=(0.0, 0.0),
               brow_up=0.0, brow_in=0.0, brow_arch=0.0,
               mouth='line', smile=0.0, mouth_w=1.0, mouth_open=0.0, teeth=False, tongue=True, blush=0.0,
               sweat=False, tear=False)

    def __getattr__(self, k):
        return self.get(k, self.DEF[k])


class Head:
    def __init__(self, P):
        """P: the face's design — a dict (see a character file)."""
        self.P = P
        self.a = table(P['a'])            # half width of each ring
        self.zf = table(P['zf'])          # front of each ring
        self.zb = table(P['zb'])          # back of each ring
        self.pr = table(P['prof'])        # extra forward bulge along the middle line: brow, nose, lips, chin
        self.sg = table(P['sigma'])       # how wide that bulge is
        self.n = P.get('n', 2.3)
        self.place((0, 0, 0), 23, 0, 0, 0)

    # ---------------------------------------------------------------- the form
    def place(self, center, height, yaw=0, nod=0, tilt=0):
        self.c = np.asarray(center, float)
        self.k = height / 2.0
        self.R = rotm(yaw, nod, tilt)
        return self

    def to_model(self, L):
        L = np.asarray(L, float).reshape(-1, 3)
        return (L * self.k) @ self.R.T + self.c

    def zm(self, y):
        return (self.zf(y) + self.zb(y)) / 2

    def surf(self, x, y):
        """front surface z at (x, y), with the middle bulge."""
        x, y = np.asarray(x, float), np.asarray(y, float)
        a = np.maximum(self.a(y), 1e-3)
        zm = self.zm(y)
        d = self.zf(y) - zm
        r = np.clip(np.abs(x) / a, 0, 1)
        z = zm + d * (1 - r ** self.n) ** (1 / self.n)
        return z + self.pr(y) * np.exp(-(x / np.maximum(self.sg(y), 1e-3)) ** 2)

    def on(self, x, y, lift=0.0):
        """head-local points on the face surface (N,3)."""
        x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
        return np.stack([x, y, self.surf(x, y) + lift], 1)

    def normal(self, x, y):
        e = 0.01
        p = self.on(x, y)
        px = self.on(np.asarray(x) + e, y) - self.on(np.asarray(x) - e, y)
        py = self.on(x, np.asarray(y) + e) - self.on(x, np.asarray(y) - e)
        n = np.cross(px, py)
        return n / np.linalg.norm(n, axis=1, keepdims=True)

    def facing(self, view, x, y):
        """how much the surface at (x, y) faces the camera (1 straight on, 0 at the rim)."""
        n = self.normal(x, y) @ self.R.T
        return view.dir(n)[:, 2]

    def ring(self, y, nt=72, scale=1.0, push=0.0):
        t = np.linspace(0, 2 * np.pi, nt, endpoint=False)
        a = float(self.a(y)) * scale + push
        zm = float(self.zm(y))
        df = (float(self.zf(y)) - zm) * scale + push
        db = (zm - float(self.zb(y))) * scale + push
        s, c = np.sin(t), np.cos(t)
        x = a * np.sign(s) * np.abs(s) ** (2 / self.n)
        ch = self.P.get('cheek')
        if ch:
            # the cheekbone: the front half of the face a little fuller at cheek height
            yc, amt, wy = ch
            x = x * (1 + amt * np.exp(-((y - yc) / wy) ** 2) * np.clip(c, 0, 1) ** 0.7)
        z = zm + np.where(c > 0, df, db) * np.sign(c) * np.abs(c) ** (2 / self.n)
        z = z + np.where(c > 0, float(self.pr(y)) * np.exp(-(x / max(float(self.sg(y)), 1e-3)) ** 2), 0)
        return np.stack([x, np.full_like(x, y), z], 1)

    def skull(self, view, y0=-1.0, y1=1.0, n=110):
        ys = np.linspace(y1, y0, n)
        rings = [view.xy(self.to_model(self.ring(y))) for y in ys]
        return smooth(hull_union(rings), 0.8)

    def xy(self, view, L):
        return view.xy(self.to_model(L))

    # ---------------------------------------------------------------- surface templates
    def tmpl(self, view, cx, cy, uv, mirror=False, lift=0.004):
        """2D template points (u right, v up, head units) laid on the surface around (cx, cy) → screen."""
        uv = np.asarray(uv, float)
        u = -uv[:, 0] if mirror else uv[:, 0]
        return self.xy(view, self.on(cx + u, cy + uv[:, 1], lift))

    def patch(self, view, pts, lift=0.01, closed=True, n=60):
        """a flat shape lying on the face surface (moustache, eyebrow tuft, plaster), from head-local (x, y)
        outline points through a Catmull-Rom curve."""
        c = spline(pts, n, closed=closed)
        L = self.xy(view, self.on(c[:, 0], c[:, 1], lift))
        return poly(L) if closed else L

    def ear(self, view, side):
        P = self.P
        ey0, ey1 = P.get('ear', (-0.06, -0.40))
        yc = (ey0 + ey1) / 2
        a = float(self.a(yc))
        root = np.array([side * (a - 0.03), 0, float(self.zm(yc)) + P.get('ear_z', -0.08)])
        out = math.radians(28)
        back = np.array([side * math.sin(out), 0, -math.cos(out)])
        h = ey0 - ey1
        uv = bezier((0, ey0 - 0.02), (0.20 * h / 0.34, ey0 + 0.07), (0.30 * h / 0.34, ey1 + 0.03),
                    (0.04, ey1 - 0.02), n=30)
        L = np.array([root + u * back + np.array([0, v, 0]) for u, v in uv])
        L = np.vstack([L, root + np.array([0, ey1 - 0.04, 0.06]), root + np.array([0, ey0, 0.06])])
        inner = bezier((0.06, ey0 - 0.07), (0.17, ey0 - 0.04), (0.16, ey1 + 0.12), (0.07, ey1 + 0.06), n=14)
        Li = np.array([root + u * back + np.array([0, v, 0]) for u, v in inner])
        # facing: the ear plane's normal turned toward the camera
        nrm = np.array([side * math.cos(out), 0, side * 0 + math.sin(out)])
        f = view.dir((nrm @ self.R.T)[None])[0, 2]
        return poly(self.xy(view, L)), self.xy(view, Li), f

    # ---------------------------------------------------------------- drawing
    def draw_face(self, d, view, E, skin, hair, iris_c='#3b2a26', brow_c=None, sc=None, light=(-1, -0.6),
                  hair_front=None, clip=None):
        """skin (head + ears) with its shadow, and the features on it. Returns the skin polygon."""
        P = self.P
        lw = d.lw
        head = self.skull(view)
        ears = []
        for side in (-1, 1):
            eg, ei, f = self.ear(view, side)
            if f > -0.15:
                ears.append((eg, ei, f))
        skin_g = smooth(unary_union([head] + [e[0] for e in ears]), 0.6)
        if clip is not None:
            skin_g = skin_g.intersection(clip)
        k = view.s * self.k
        sh = skin_g.difference(shift(skin_g, light[0] * 0.09 * k, light[1] * 0.06 * k))
        if hair_front is not None and not hair_front.is_empty:
            sh = sh.union(shift(hair_front, 0.015 * k, 0.045 * k).intersection(skin_g))
        sh = smooth(sh, 0.5)
        d.fill(skin_g, skin)
        d.fill(sh.intersection(skin_g), sc or shade(skin))
        d.outline(skin_g)
        for eg, ei, f in ears:
            if f > 0.15:
                d.line(ei, lw * 0.8)
        self.features(d, view, E, skin, hair, iris_c, brow_c or mix(hair, INK, 0.35), skin_g)
        return skin_g

    def visible(self, view, x, y):
        return self.facing(view, x, y)

    def features(self, d, view, E, skin, hair, iris_c, brow_c, skin_g):
        P = self.P
        lw = d.lw
        k = view.s * self.k
        inside = skin_g.buffer(-0.4 * lw)
        ex, ey = P['eye_x'], P['eye_y']
        # blush first, under everything
        if E.blush > 0 or P.get('blush', 0) > 0:
            amt = max(E.blush, P.get('blush', 0))
            bid = d.blur(0.018 * k)
            for side in (-1, 1):
                f = float(self.facing(view, side * (ex + 0.03), ey - 0.2)[0])
                if f < 0.2:
                    continue
                t = np.linspace(0, 2 * np.pi, 30)
                uv = np.stack([0.12 * np.cos(t), 0.055 * np.sin(t)], 1)
                g = poly(self.tmpl(view, side * (ex + 0.04), ey - 0.21, uv)).intersection(inside)
                from geo import path_of
                d.add(f'<path d="{path_of(g)}" fill="#e8706a" opacity="{0.55 * amt:.2f}" filter="url(#{bid})"/>')
                if P.get('blush_hatch'):
                    for j in range(3):
                        u0 = -0.06 + j * 0.05
                        pts = self.tmpl(view, side * (ex + 0.04), ey - 0.21, [(u0, -0.03), (u0 + 0.04, 0.03)])
                        d.line(pts, lw * 0.55, '#c0504a', 0.7)
        # wrinkles and marks that are part of the face design
        for w in P.get('marks', []):
            self._mark(d, view, w, inside, lw)
        for side in (-1, 1):
            f = float(self.facing(view, side * ex, ey)[0])
            if f < 0.08:
                continue
            self.eye(d, view, side, E, iris_c, skin, f, inside)
            self.brow(d, view, side, E, brow_c, inside)
        self.nose(d, view, E, inside)
        self.mouth(d, view, E, skin, inside)

    def _mark(self, d, view, m, inside, lw):
        pts = m['pts']
        sides = (-1, 1) if m.get('both', True) else (1,)
        for side in sides:
            P = np.array([(side * x, y) for x, y in pts])
            if float(self.facing(view, P[:, 0].mean(), P[:, 1].mean())[0]) < m.get('min_face', 0.15):
                continue
            curve = spline(P, 24) if len(P) > 2 else P
            L = self.xy(view, self.on(curve[:, 0], curve[:, 1], 0.004))
            ln = LineString(L).intersection(inside)
            from geo import lines as _lines
            for s in _lines(ln):
                d.line(np.asarray(s.coords), lw * m.get('w', 0.6), m.get('c', INK), m.get('op', 1.0))

    # ---- eye
    def eye(self, d, view, side, E, iris_c, skin, f, inside):
        P = self.P
        w, h = P['eye_w'], P['eye_h']
        ex, ey = P['eye_x'], P['eye_y']
        mirror = side < 0
        lw = d.lw
        o = E.open
        uv_up = lambda lin, lout: bezier((-0.5 * w, 0.0), (-0.28 * w, (0.95 - lin) * h * o),
                                         (0.22 * w, (1.0 - lout) * h * o), (0.5 * w, (0.35 - 0.3 * lout) * h * o), n=26)
        up = uv_up(E.lid_in, E.lid_out)
        tilt = P.get('eye_tilt', 0.0)
        up[:, 1] += tilt * up[:, 0] / w
        lo_raise = E.smile_eye * 0.35 * h
        lo = bezier((-0.5 * w, 0.0), (-0.22 * w, -0.48 * h + lo_raise), (0.25 * w, -0.46 * h + lo_raise),
                    (0.5 * w, (0.35 - 0.3 * E.lid_out) * h * o), n=26)
        lo[:, 1] += tilt * lo[:, 0] / w
        cx, cy = side * ex, ey
        if E.closed > 0.5:
            # joy: the eye shut in a soft upward arc; sorrow-closed: a downward arc
            sgn = 1 if E.closed < 1.5 else -1
            arc = bezier((-0.5 * w, -0.1 * h), (-0.2 * w, sgn * 0.5 * h + 0.1 * h), (0.25 * w, sgn * 0.5 * h + 0.1 * h),
                         (0.52 * w, -0.05 * h), n=24)
            pts = self.tmpl(view, cx, cy, arc, mirror)
            th = np.sin(np.linspace(0.15, np.pi - 0.15, len(pts))) * lw * 1.3 + lw * 0.5
            g = ribbon(pts, th)
            d.fill(g.intersection(inside), INK)
            if P.get('lashes', 0):
                self._lashes(d, view, cx, cy, arc, mirror, lw, P['lashes'], down=sgn < 0)
            return
        white_uv = np.vstack([up, lo[::-1]])
        white = poly(self.tmpl(view, cx, cy, white_uv, mirror)).buffer(0)
        white = white.intersection(inside)
        if white.is_empty:
            return
        d.fill(white, P.get('white', '#f6f1ea'))
        # shadow of the upper lid on the eyeball
        lid_sh = poly(self.tmpl(view, cx, cy, np.vstack([up, up[::-1] + [0, -0.22 * h]]), mirror)).buffer(0)
        d.fill(lid_sh.intersection(white), mix(P.get('white', '#f6f1ea'), '#8a8aa6', 0.35))
        # iris: a tall dark oval under the lid, lighter at the bottom; the look moves it
        lx, ly = E.look
        rw, rh = P['iris_w'] * E.iris, P['iris_h'] * E.iris
        # iris centre in head-local offsets (no mirroring: the look and the glint are the same for both eyes)
        icx = side * P.get('iris_dx', 0.0) * w + lx * 0.22 * w
        icy = 0.42 * h * o + ly * 0.15 * h - (0.0 if E.iris >= 1 else 0.08 * h)
        t = np.linspace(0, 2 * np.pi, 40)
        iris = poly(self.tmpl(view, cx, cy, np.stack([icx + rw * np.cos(t), icy + rh * np.sin(t)], 1))).buffer(0)
        iris = iris.intersection(white)
        d.fill(iris, iris_c)
        low = poly(self.tmpl(view, cx, cy, np.stack([icx + rw * 0.8 * np.cos(t),
                                                     icy - rh * 0.5 + rh * 0.45 * np.sin(t)], 1))).buffer(0)
        d.fill(low.intersection(iris), mix(iris_c, P.get('iris_light', '#8a5a40'), 0.55))
        d.fill(iris.intersection(lid_sh), mix(iris_c, '#000000', 0.3))
        # glints: a round one up-left (toward the light), a small one lower right
        for (hx, hy, hr) in P.get('glints', [(-0.35, 0.40, 0.24), (0.30, -0.35, 0.10)]):
            gpt = self.tmpl(view, cx, cy, [(icx + hx * rw, icy + hy * rh)])[0]
            g = Point(gpt).buffer(hr * rw * view.s * self.k * max(f, 0.6), 16).intersection(iris.buffer(0.5))
            d.fill(g, '#ffffff')
        # the upper lid: a thick line, heavier toward the outer corner, a small flick past it
        upl = up.copy()
        upl = np.vstack([upl, [[0.56 * w, upl[-1, 1] - 0.06 * h * P.get('flick', 1.0)]]])
        pts = self.tmpl(view, cx, cy, upl, mirror)
        s = np.linspace(0, 1, len(pts))
        th = lw * (0.6 + P.get('lid_w', 1.25) * np.sin(np.clip(s * 1.05, 0, 1) * np.pi * 0.85) ** 0.8)
        th[-1] = lw * 0.4
        d.fill(ribbon(pts, th), INK)
        # the lower lid: a short thin stroke toward the outer corner
        if P.get('lower_lid', True):
            seg = lo[int(len(lo) * 0.40):int(len(lo) * 0.96)]
            d.line(self.tmpl(view, cx, cy, seg, mirror), lw * 0.6)
        if P.get('crease', 0):
            cr = up[int(len(up) * 0.2):int(len(up) * 0.85)] + [0, 0.32 * h * P['crease']]
            d.line(self.tmpl(view, cx, cy, cr, mirror), lw * 0.45)
        if P.get('lashes', 0):
            self._lashes(d, view, cx, cy, up, mirror, lw, P['lashes'])

    def _lashes(self, d, view, cx, cy, up, mirror, lw, n, down=False):
        w = self.P['eye_w']
        for j in range(n):
            i = len(up) - 3 - j * 3
            if i < 1:
                break
            p = up[i]
            q = p + [0.07 * w, (0.09 if not down else -0.09) * w * (1 - j * 0.15)]
            d.line(self.tmpl(view, cx, cy, [p, q], mirror), lw * 0.7)

    # ---- brow
    def brow(self, d, view, side, E, c, inside):
        P = self.P
        if P.get('brow_style') == 'bushy':
            return self.bushy_brow(d, view, side, E, inside)
        w = P['brow_w']
        bx, by = P['eye_x'] + P.get('brow_dx', 0.0), P['eye_y'] + P['brow_y'] + E.brow_up * 0.08
        arch = P.get('brow_arch', 0.035) + E.brow_arch * 0.03
        tilt = E.brow_in * 0.07     # + : the inner end goes down (anger), - : up (sorrow)
        uv = bezier((-0.5 * w, -tilt), (-0.15 * w, arch - tilt * 0.4), (0.2 * w, arch), (0.5 * w, -0.01 - 0.02), n=20)
        pts = self.tmpl(view, side * bx, by, uv, side < 0)
        s = np.linspace(0, 1, len(pts))
        th = d.lw * P.get('brow_th', 1.6) * (1 - 0.75 * s) + d.lw * 0.3
        g = ribbon(pts, th).intersection(inside)
        d.fill(g, c)

    def bushy_brow(self, d, view, side, E, inside):
        """an old man's brow: a white tuft with a ragged lower edge that hangs over the eye."""
        P = self.P
        bx, by = P['eye_x'] + P.get('brow_dx', 0.0), P['eye_y'] + P['brow_y'] + E.brow_up * 0.07
        w = P['brow_w']
        ti = E.brow_in * 0.06
        top = [(-0.5 * w, 0.02 - ti), (-0.2 * w, 0.075 - ti * 0.5), (0.2 * w, 0.08), (0.55 * w, 0.03)]
        jag = [(0.62 * w, -0.06), (0.42 * w, -0.03), (0.32 * w, -0.08), (0.16 * w, -0.035), (0.02 * w, -0.075 - ti * 0.3),
               (-0.14 * w, -0.03 - ti * 0.6), (-0.3 * w, -0.06 - ti * 0.8), (-0.42 * w, -0.025 - ti), (-0.55 * w, -0.03 - ti)]
        pts = np.array(top + jag)
        pts[:, 0] = side * (bx + pts[:, 0])
        pts[:, 1] += by
        g = poly(self.xy(view, self.on(pts[:, 0], pts[:, 1], 0.02))).buffer(0).intersection(inside.buffer(0.03 * view.s * self.k))
        col = P.get('brow_c', '#ebe6de')
        d.fill(g, col)
        d.fill(g.difference(shift(g, -0.02 * view.s * self.k, -0.025 * view.s * self.k)), shade(col))
        d.outline(g, d.lw * 0.7)

    # ---- nose
    def nose(self, d, view, E, inside):
        P = self.P
        yt = P['nose_y']
        fy = float(self.facing(view, 0.0, yt)[0])
        # the far side of the nose: where the head turns away from the camera (front: the shadow side)
        side = 1 if self._turn(view) >= -2 else -1
        nw = P.get('nose_w', 0.075)
        nl = P.get('nose_len', 0.16)
        style = P.get('nose', 'hook')
        if style == 'hook':
            pts = [(side * nw * 0.55, yt + nl), (side * nw * 0.95, yt + 0.035), (side * nw * 0.55, yt - 0.025),
                   (side * nw * 0.05, yt - 0.03)]
        elif style == 'round':      # an old, fleshy nose: a rounded tip and a nostril wing
            pts = [(side * nw * 0.6, yt + nl), (side * nw * 1.25, yt + 0.02), (side * nw * 1.05, yt - 0.05),
                   (side * nw * 0.3, yt - 0.055), (-side * nw * 0.3, yt - 0.05)]
        else:                       # 'dash': a child's tiny nose, a single short stroke
            pts = [(side * nw * 0.7, yt + 0.01), (side * nw * 0.2, yt - 0.025), (-side * nw * 0.15, yt - 0.02)]
        curve = spline(pts, 20)
        L = self.xy(view, self.on(curve[:, 0], curve[:, 1], 0.004))
        if abs(self._turn(view)) > 70:
            # in profile the nose is in the outline; draw only the nostril wing
            L = L[len(L) // 2:]
        from geo import lines as _lines
        for s in _lines(LineString(L).intersection(inside.buffer(0.2 * d.lw))):
            d.line(np.asarray(s.coords), d.lw * 0.75)
        if style == 'round' and abs(self._turn(view)) < 70:
            # the other wing, faint
            q = spline([(-side * nw * 0.9, yt + 0.0), (-side * nw * 0.7, yt - 0.045)], 6)
            d.line(self.xy(view, self.on(q[:, 0], q[:, 1], 0.004)), d.lw * 0.6)

    def _turn(self, view):
        """how far the face is turned from the camera, degrees (+ to the viewer's right)."""
        fwd = view.dir((np.array([0, 0, 1.0]) @ self.R.T)[None])[0]
        return math.degrees(math.atan2(fwd[0], fwd[2]))

    # ---- mouth
    def mouth(self, d, view, E, skin, inside):
        P = self.P
        my = P['mouth_y']
        mw = P['mouth_w'] * E.mouth_w
        lw = d.lw
        sm = E.smile * 0.06
        turn = self._turn(view)
        if E.mouth == 'line' or E.mouth_open <= 0.01:
            u = np.linspace(-mw, mw, 22)
            v = sm * (u / mw) ** 2 - sm * 0.3 + P.get('mouth_curve', 0.0) * (1 - (u / mw) ** 2)
            pts = self.xy(view, self.on(u, my + v, 0.004))
            s = np.linspace(0, 1, len(pts))
            th = lw * (0.45 + 0.55 * np.sin(s * np.pi))
            g = ribbon(pts, th).intersection(inside.buffer(0.6 * lw))
            d.fill(g, INK)
            if E.smile < -0.3:
                pass
        else:
            mo = E.mouth_open * 0.11
            u = np.linspace(-mw, mw, 24)
            if E.mouth == 'D':      # laughing: flat top, round bottom
                top = my + sm * (u / mw) ** 2 * 0.8 + 0.01
                bot = my - mo * np.sqrt(np.clip(1 - (u / mw) ** 2, 0, 1)) + sm * (u / mw) ** 2 * 0.5
            elif E.mouth == 'O':    # surprise: a small open oval
                top = my + mo * 0.35 * np.sqrt(np.clip(1 - (u / mw) ** 2, 0, 1))
                bot = my - mo * 0.75 * np.sqrt(np.clip(1 - (u / mw) ** 2, 0, 1))
            else:                   # 'shout' / 'frown': corners down, open, squarish
                top = my - sm * 0 + 0.012 * (1 - (u / mw) ** 2) - 0.03 * (u / mw) ** 2
                bot = my - mo * (1 - 0.35 * (u / mw) ** 2) - 0.03 * (u / mw) ** 2
            T = self.xy(view, self.on(u, top, 0.004))
            B = self.xy(view, self.on(u, bot, 0.004))
            g = poly(np.vstack([T, B[::-1]])).intersection(inside.buffer(0.4 * lw))
            d.fill(g, P.get('mouth_c', '#7a2e2e'))
            if E.tongue:
                tu = np.linspace(-mw * 0.55, mw * 0.55, 14)
                tb = np.interp(tu, u, bot)
                tt = tb + mo * 0.45
                TT = self.xy(view, self.on(tu, tt, 0.004))
                TB = self.xy(view, self.on(tu, tb - 0.01, 0.004))
                d.fill(poly(np.vstack([TT, TB[::-1]])).intersection(g), '#d9706e')
            if E.teeth:
                tt = np.interp(u, u, top) - 0.022
                TT = self.xy(view, self.on(u, tt, 0.004))
                d.fill(poly(np.vstack([T, TT[::-1]])).intersection(g), '#fbf6ef')
            d.outline(g, lw * 0.7)
        if P.get('lower_lip', 0) and E.mouth_open <= 0.3:
            ll = P['lower_lip']
            u = np.linspace(-ll, ll, 10)
            pts = self.xy(view, self.on(u, my - 0.075 - E.mouth_open * 0.11 + 0.01 * (u / ll) ** 2, 0.004))
            if abs(turn) < 75:
                d.line(pts, lw * 0.5)
