"""Hair: a shell over the skull (where the hairline allows) plus locks — tapered ribbons that hang from the shell.
Front hair (shell + front locks) is one flat shape drawn over the face; back hair (long locks behind the head and
shoulders) is drawn before the body. A few locks also leave a strand line inside the mass, as Ghibli draws clumps."""
import math
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union
from geo import poly, ribbon, bezier, smooth, shift, lines, resample
from head import table
from svgdoc import INK, shade


def periodic(pairs, mirror=True):
    """hairline: y as a function of azimuth t (degrees, 0 = front, +90 = the character's +x side)."""
    pts = list(pairs)
    if mirror:
        pts += [(-t, y) for t, y in pairs if 0 < t < 180]
    pts = sorted(pts)
    T = np.array([p[0] for p in pts], float)
    Y = np.array([p[1] for p in pts], float)
    T = np.r_[T - 360, T, T + 360]
    Y = np.r_[Y, Y, Y]
    return lambda t: np.interp(((np.asarray(t) + 180) % 360) - 180, T, Y)


class Hair:
    def __init__(self, head, P):
        self.h, self.P = head, P
        self.line_y = periodic(P['hairline'], P.get('mirror', True))
        # where the hair stops at the top (a bald crown); by default it covers the crown
        self.top_y = periodic(P['top'], P.get('mirror', True)) if 'top' in P else (lambda t: np.full_like(np.asarray(t, float), 1.0))
        self.k = table(P.get('volume', [(-1, 0.06), (0, 0.08), (1, 0.12)]))
        self.C = np.array([0, 0.05, float(head.zm(0.05))])

    def shell_pt(self, t_deg, y):
        h = self.h
        t = math.radians(t_deg)
        y = float(np.clip(y, -0.999, 0.999))
        a = float(h.a(y))
        zm = float(h.zm(y))
        n = h.n
        s, c = math.sin(t), math.cos(t)
        x = a * math.copysign(abs(s) ** (2 / n), s)
        d = (float(h.zf(y)) - zm) if c > 0 else (zm - float(h.zb(y)))
        z = zm + d * math.copysign(abs(c) ** (2 / n), c)
        p = np.array([x, y, z])
        return self.C + (p - self.C) * (1 + float(self.k(y)))

    def shell(self, view):
        """the visible part of the shell above the hairline."""
        h = self.h
        ts = np.arange(-180, 180, 4.0)
        nY = 30
        # each column starts exactly at the hairline, so the edge of the hair is a clean curve
        hl = np.minimum(self.line_y(ts), 0.97)
        tl = np.maximum(self.top_y(ts), hl + 0.01)
        G = np.array([[self.shell_pt(t, y0 + (y1 - y0) * (i / (nY - 1)) ** 1.3) for t, y0, y1 in zip(ts, hl, tl)]
                      for i in range(nY)])                                   # (nY, nt, 3)
        M = h.to_model(G.reshape(-1, 3))
        C = view.rot(M).reshape(nY, len(ts), 3)
        S = view.xy(M).reshape(nY, len(ts), 2)
        quads = []
        for i in range(nY - 1):
            for j in range(len(ts)):
                j2 = (j + 1) % len(ts)
                if tl[j] - hl[j] < 0.03 or tl[j2] - hl[j2] < 0.03:
                    continue
                e1 = C[i, j2] - C[i, j]
                e2 = C[i + 1, j] - C[i, j]
                nz = e1[0] * e2[1] - e1[1] * e2[0]
                if nz < 0:      # faces away
                    continue
                q = poly([S[i, j], S[i, j2], S[i + 1, j2], S[i + 1, j]])
                if q.area > 0:
                    quads.append(q.buffer(0.35))
        return unary_union(quads) if quads else poly([(0, 0), (0, 0.1), (0.1, 0)])

    def lock(self, view, L):
        """one lock: root on the shell at (t, y); `to` are offsets of the curve's further points from the root
        (head units, local); `w` the width at the root."""
        h = self.h
        roots = [L['root']] if not L.get('mirror') else [L['root'], (-L['root'][0], L['root'][1])]
        out = []
        for k, (t, y) in enumerate(roots):
            r = self.shell_pt(t, y)
            ctrl = [r] + [r + np.array([(-dx if k else dx), dy, dz]) for dx, dy, dz in L['to']]
            c = bezier(*ctrl, n=28)
            P2 = view.xy(h.to_model(c))
            s = np.linspace(0, 1, len(P2))
            prof = L.get('prof', 1.2)
            w = L['w'] * view.s * h.k * (1 - s ** prof) * (0.6 + 0.4 * np.sin(np.clip(s * 3, 0, 1) * np.pi / 2))
            w = np.maximum(w, 0.3)
            g = ribbon(P2, w).buffer(0)
            # does the root face the camera? a lock rooted on the far side hangs behind the head
            q = h.to_model(np.array([r, self.C + (r - self.C) * 1.05]))
            fz = float(view.rot(q[1:2])[0, 2] - view.rot(q[0:1])[0, 2])
            out.append((g, P2, w, fz))
        return out

    def build(self, view):
        front, back, strands = [self.shell(view)], [], []
        for bl in self.P.get('balls', []):
            # a bun or a knot: a ball sitting on the shell
            t, y, r, out = bl
            p = self.shell_pt(t, y)
            p = self.C + (p - self.C) * (1 + out)
            M = self.h.to_model(p[None])
            c = view.xy(M)[0]
            q = self.h.to_model((self.C + (p - self.C) * 1.05)[None])
            fz = float(view.rot(q)[0, 2] - view.rot(M)[0, 2])
            from shapely.geometry import Point as _P
            g = _P(c).buffer(r * view.s * self.h.k, 32)
            (front if fz >= 0 else back).append(g)
        for L in self.P.get('locks', []):
            for g, c, w, fz in self.lock(view, L):
                isback = L.get('back') or (fz < -0.002 and not L.get('front'))
                (back if isback else front).append(g)
                if isback:
                    continue
                if L.get('line'):
                    strands.append((c, w, L.get('line')))
        for path in self.P.get('flow', []):
            pts = np.array([self.shell_pt(t, y) for t, y in path])
            pts = np.vstack([self.C + (p - self.C) * 1.01 for p in pts])
            from geo import spline as _sp
            c = _sp(pts, 30)
            M = self.h.to_model(c)
            C = view.rot(M)
            # keep the part facing the camera (compare with a point a little further out)
            Mo = self.h.to_model(self.C + (c - self.C) * 1.05)
            vis = view.rot(Mo)[:, 2] - C[:, 2] > 0
            S = view.xy(M)
            run = []
            for p, v in zip(S, vis):
                if v:
                    run.append(p)
                elif len(run) > 1:
                    strands.append((np.array(run), None, 'flow')); run = []
                else:
                    run = []
            if len(run) > 1:
                strands.append((np.array(run), None, 'flow'))
        F = smooth(unary_union(front), 0.8)
        B = smooth(unary_union(back), 0.8) if back else None
        return F, B, strands

    def draw(self, d, view, g, color, strands=(), light=(-1, -0.6), extra_shadow=None):
        k = view.s * self.h.k
        sh = g.difference(shift(g, light[0] * 0.09 * k, light[1] * 0.09 * k))
        if extra_shadow is not None:
            sh = sh.union(extra_shadow)
        d.fill(g, color)
        d.fill(smooth(sh, 0.5).intersection(g), self.P.get('shadow', shade(color, 1.1)))
        inner = g.buffer(-0.8 * d.lw)
        for c, w, which in strands:
            if which == 'flow':
                for s_ in lines(LineString(c).intersection(inner)):
                    d.line(np.asarray(s_.coords), d.lw * 0.55)
                continue
            n = len(c)
            seg = c[int(n * 0.55):]
            T = np.gradient(seg, axis=0)
            T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-9)
            N = np.stack([-T[:, 1], T[:, 0]], 1)
            sgn = 1 if which in (True, 1, 'r') else -1
            e = seg + sgn * N * (w[int(n * 0.55):, None] / 2) * 0.8
            for s in lines(LineString(e).intersection(inner)):
                d.line(np.asarray(s.coords), d.lw * 0.6)
        d.outline(g)
