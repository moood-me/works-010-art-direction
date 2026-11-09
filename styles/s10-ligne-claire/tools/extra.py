"""Shared parts added with Марат and Кира (round three); the four don't use them, so their pictures stay as
they were.

- Posed: a Figure whose whole body follows a line of action — the spine is given as rows of offsets by height.
- OnShell: lets the face marks of features.py be drawn on a shell (a mouth in a beard).
- bumps: turns a smooth shell part into a mass of curls (the silhouette becomes scalloped).
- strip: a band of cloth along a 3D path (a towel over a shoulder).
- grin_marks: an open laughing mouth with a strip of teeth and a tongue.
- smirk_marks: a closed mouth with one corner up.
"""
import math
import numpy as np
from scipy.interpolate import PchipInterpolator
import lc, r3, body as B
from head import Mark
from figures import Figure
from features import ex


# ------------------------------------------------------------------------------------------------ line of action
class Posed(Figure):
    """spine: rows (y, dx, dz, tilt, twist).  At height y the body is shifted by dx (to the viewer's right in the
    front view) and dz (toward the viewer), its cross-section is tilted (tilt: degrees, + lowers the x > 0 side)
    and turned about the vertical (twist: degrees).  Between rows the values are interpolated, so a few rows give
    a curve through head, chest, hips and feet: a lean, a slouch, a weight shift."""

    def __init__(self, *a, spine=None, **kw):
        super().__init__(*a, **kw)
        rows = np.array(spine if spine is not None else [(0, 0, 0, 0, 0), (1, 0, 0, 0, 0)], float)
        self._s = [PchipInterpolator(rows[:, 0], rows[:, i]) for i in range(1, 5)]
        self._y0, self._y1 = rows[0, 0], rows[-1, 0]

    def warp(self, P):
        P = np.asarray(P, float)
        y = np.clip(P[:, 1], self._y0, self._y1)
        dx, dz, tilt, twist = (f(y) for f in self._s)
        a = np.radians(twist)
        X = P[:, 0] * np.cos(a) + P[:, 2] * np.sin(a)
        Z = -P[:, 0] * np.sin(a) + P[:, 2] * np.cos(a)
        Y = P[:, 1] + X * np.tan(np.radians(tilt))
        return np.stack([X + dx, Y, Z + dz], 1)

    def parts(self, res):
        out = []
        for p in super().parts(res):
            Q = self.warp(np.stack([p.X, p.Y, p.Z], 1))
            out.append(r3.Part(p.name, p.material, Q[:, 0], Q[:, 1], Q[:, 2], line=p.line))
        return out

    def get_marks(self, expr, view):
        out = super().get_marks(expr, view)
        for m in out:
            m.pts = self.warp(m.pts)
        return out


# ------------------------------------------------------------------------------------------------ marks on a shell
def shell_z(shell, x, y):
    """Front surface of a shell at (x, y)."""
    w, zm, zf, zb, n = shell.sl(y)
    a = np.clip(np.abs(x) / np.maximum(w, 1e-3), 0, 1)
    return zm + (zf - zm) * (1 - a ** n) ** (1 / n)


class OnShell:
    """Stands in for a Head in features.*_marks: the marks land on the front of a shell (a beard) instead."""

    def __init__(self, shell, lift=1.0):
        self.shell, self.lift = shell, lift

    def on_face(self, x, y, uv, flip=False, scale=1.0, rot=0.0):
        out = []
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for u, v in uv:
            u, v = u * scale, v * scale
            u, v = u * c - v * s, u * s + v * c
            if flip:
                u = -u
            px, py = x + u, y + v
            out.append([px, py, float(shell_z(self.shell, px, py)) + self.lift])
        return np.array(out)


def on(marks, material):
    for m in marks:
        m.on = material
    return marks


# ------------------------------------------------------------------------------------------------ curls
def bumps(part, centre, amp, pitch, seed=0.0):
    """Push the points of a part outward from centre in a staggered pattern of round bumps about `pitch` wide
    and `amp` high: short curly hair, a curly beard.  The poles of the pattern lie on the z axis (the face and
    the back of the head), where they are not seen."""
    P = np.stack([part.X, part.Y, part.Z], 1) - np.asarray(centre, float)
    r = np.linalg.norm(P, axis=1) + 1e-9
    D = P / r[:, None]
    lat = np.arcsin(np.clip(D[:, 2], -1, 1))                 # 0 on the ring through crown and ears
    lon = np.arctan2(D[:, 1], D[:, 0])
    R = float(np.median(r))
    v = lat * R / pitch + seed
    row = np.floor(v)
    u = lon * R * np.cos(lat) / pitch + 0.5 * row + 0.37 * np.sin(row * 12.9898 + seed) * 2
    f = (np.cos(np.pi * (u - np.floor(u) - 0.5)) * np.cos(np.pi * (v - row - 0.5))) ** 0.6
    Q = P + D * (amp * f)[:, None] + np.asarray(centre, float)
    return r3.Part(part.name, part.material, Q[:, 0], Q[:, 1], Q[:, 2], line=part.line)


def curl(c, r, turn=0.0, flip=False):
    """A small 'c' of a curl: points round (cx, cy) in a shell's (degrees, y) coordinates."""
    cx, cy = c
    out = []
    for a in np.linspace(-0.2, 1.25, 7) * np.pi:
        a = a + turn
        u, v = r * np.cos(a), r * np.sin(a)
        out.append((cx + (-u if flip else u) * 0.75, cy + v))
    return out


def strip(name, material, pts, half_width, res, thick=3.0):
    """A band of cloth lying along a 3D path, its width along x (a towel over a shoulder, a strap)."""
    C, _ = B._spline(pts, int(sum(np.linalg.norm(np.diff(np.asarray(pts, float), axis=0), axis=1)) * res * 1.4) + 8)
    T = np.gradient(C, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    N = np.cross(T, [1.0, 0, 0])
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
    a = np.linspace(0, 2 * np.pi, int(4 * half_width * res * 1.4) + 12, endpoint=False)
    Q = (C[:, None, :] + np.array([1.0, 0, 0])[None, None, :] * (half_width * np.cos(a))[None, :, None]
         + N[:, None, :] * (thick * np.sin(a))[None, :, None]).reshape(-1, 3)
    return r3.Part(name, material, Q[:, 0], Q[:, 1], Q[:, 2])


# ------------------------------------------------------------------------------------------------ mouths
def grin_marks(h, e, st):
    """A wide open laughing mouth: a dark shape, a strip of upper teeth along its top, the tongue at the bottom.
    st: y, w (half width), smile, open; expression keys as in features.EXPR."""
    y = st['y']
    W = st.get('w', 16) * ex(e, 'mw', 1.0)
    sm = ex(e, 'smile', st.get('smile', 1.0))
    op = ex(e, 'open', st.get('open', 10))
    c = sm * 4.6
    top = [(-W, -c), (-W * 0.6, -c * 0.42), (-W * 0.2, -c * 0.06), (W * 0.2, -c * 0.06), (W * 0.6, -c * 0.42),
           (W, -c)]
    bot = [(W * 0.78, -c * 0.3 + op * 0.5), (W * 0.36, op), (-W * 0.36, op), (-W * 0.78, -c * 0.3 + op * 0.5)]
    out = [Mark(h.on_face(0, y, top + bot), kind='shape', fill='#4a1a14', w=1.0, corners=(0, 5))]
    t = op * 0.36
    k = 0.9
    teeth = [(u * k, v + 0.9) for u, v in top] + [(u * k * 0.97, v + 0.9 + t * (1 - 0.45 * abs(u) / W))
                                                 for u, v in top[::-1]]
    out.append(Mark(h.on_face(0, y, teeth), kind='shape', fill='#fffdf6', w=0.6, corners=(0, 5, 6, 11)))
    tongue = [(-W * 0.4, op * 0.9), (-W * 0.2, op * 0.62), (0, op * 0.68), (W * 0.2, op * 0.62), (W * 0.4, op * 0.9),
              (0, op * 0.97)]
    out.append(Mark(h.on_face(0, y, tongue), kind='shape', fill='#c8564a', w=0))
    out.append(Mark(h.on_face(0, y, [(0, op * 0.7), (0, op * 0.9)]), w=0.5))
    return out


def smirk_marks(h, e, st):
    """A mouth pressed shut with one corner pulled up: st['side'] (+1 / -1) says which, e['smirk'] how much."""
    y = st['y']
    W = st.get('w', 9)
    k = ex(e, 'smirk', st.get('smirk', 1.0))
    s = st.get('side', 1)
    pts = [(-s * W, 0.9), (-s * W * 0.4, 0.5), (s * W * 0.25, 0.3), (s * W * 0.75, -0.9 * k), (s * W * 1.08, -2.6 * k)]
    out = [Mark(h.on_face(0, y, pts), w=1.0)]
    out.append(Mark(h.on_face(0, y, [(s * (W * 1.0), -2.6 * k - 1.6), (s * (W * 1.22), -2.2 * k + 0.6)]), w=0.8))
    out.append(Mark(h.on_face(0, y, [(-s * (W - 0.2), -0.6), (-s * (W + 0.8), 1.6)]), w=0.7))
    lv = st.get('lower_y', 5.5)
    out.append(Mark(h.on_face(0, y, [(-W * 0.3, lv), (0, lv + 0.4), (W * 0.3, lv)]), w=0.6))
    return out
