"""Савелий Петрович's drawing (styles/s8-stopmotion) as 3D data. The drawing's head is itself a 3D object — a loft of elliptic
slices (`head.Head`, `cast.SAVELY`) with features laid on it by (phi, y) — so its own numbers are the fitting target:
no front/profile guessing. Everything here is in head units on the engine's axes (x his left, y up, z forward; head
centre at 0; head height 1)."""
import math
import numpy as np
import common  # noqa: F401  (puts the style's tools on the path)
import cast
from head import Head
from common import hu

P = cast.SAVELY
BODY = cast.SAVELY_BODY
FIG = cast.SAVELY_FIG
EXPR = cast.EXPR
H0 = Head(P['shape'], 1.0, 0.0, 0.0, 0.0, 0.0)     # yaw 0, 1 px per unit: scr() == the head-unit point


def surf(phi, y, out=0.0, k=1.0):
    return hu(H0.surf(phi, y, out, k))


def loft_mesh(nphi=160, ny=160, k=1.0, out=0.0, y0=-0.5, y1=0.5):
    """the head's loft as a closed-ish grid (rows of slices from crown to chin)"""
    ys = y0 + (y1 - y0) * (1 - np.cos(np.linspace(0, np.pi, ny))) / 2
    ph = np.linspace(-np.pi, np.pi, nphi, endpoint=False)
    V = np.array([[H0.surf(p, y, out, k) for p in ph] for y in ys]).reshape(-1, 3)
    T = []
    for i in range(ny - 1):
        for j in range(nphi):
            a, b = i * nphi + j, i * nphi + (j + 1) % nphi
            c, d = a + nphi, b + nphi
            T += [[a, c, b], [b, c, d]]
    return hu(V), np.array(T)


def neck_mesh(nphi=64, ny=40):
    """the drawing's neck (SAVELY_BODY['neck'], from under the jaw down into the sweater)"""
    from head import interp
    N = BODY['neck']
    ys = np.linspace(0.2, 0.75, ny)
    ph = np.linspace(-np.pi, np.pi, nphi, endpoint=False)
    V = []
    for y in ys:
        a = interp(N['a'], y); fr = interp(N['front'], y); bk = interp(N['back'], y)
        b, c = (fr - bk) / 2, (fr + bk) / 2
        V += [(a * math.sin(p), y, c + b * math.cos(p)) for p in ph]
    return hu(np.array(V))


def eye_centre(side):
    """centre of the glass eyeball (side −1: his right = the viewer's left; +1: his left)"""
    phi = side * P['eye_phi']
    return surf(phi, P['eye_y'], -P['eye_r'] * 0.55)


EYE_R = P['eye_r'] * 1.05          # the ball as the drawing draws it (head.eye: r = eye_r · 1.05)


def eye_opening(side, ex=None, n=24, peak=0.18, lower_pow=1.1, tall=1.0):
    """the lid opening as a closed 3D curve on the head's surface (the drawing's `eye()` shape, laid by (phi, y))"""
    ex = ex or {}
    phi0 = side * P['eye_phi']; ye = P['eye_y']; R = P['eye_r']; w = P['eye_w']
    op = ex.get('open', 1.0) * P['eye_open']; up = ex.get('lid_up', 0.0); lo = ex.get('lid_lo', 0.0)
    top_h = R * P.get('lid_top', 0.78) * op * (1 + up)
    bot_h = R * P.get('lid_bot', 0.42) * op * (1 - lo)
    inn, outer = (-w, w) if side > 0 else (w, -w)
    tilt = P.get('eye_tilt', 0.0)
    a = H0.a(ye)
    up_pts, lo_pts = [], []
    for i in range(n + 1):
        t = i / n
        x = inn + (outer - inn) * t
        yb = (0.04 * tilt) * (1 - t) - tilt * t          # the corners' line (head.eye: eye_tilt, outer corner up +)
        s = math.sin(math.pi * t) ** 0.8
        pk = 1 + peak * math.sin(math.pi * (t - 0.15))
        up_pts.append((x, yb - top_h * tall * s * pk * 0.95))
        lo_pts.append((x, yb + bot_h * tall * math.sin(math.pi * t) ** lower_pow))
    loc = up_pts + lo_pts[::-1][1:-1]
    return np.array([surf(phi0 + x / a, ye + y) for x, y in loc]), len(up_pts)


def nose_slices():
    """the nose's own loft (head.nose): (y, z of the front, half width) from root to tip, engine axes"""
    y0, y1 = P['nose_root'], P['nose_tip']
    L, W, up = P['nose_len'], P['nose_w'], P.get('nose_up', 0.0)
    out = []
    for i in range(17):
        t = i / 16
        y = y0 + (y1 - y0) * t
        prot = L * t ** 1.15
        wid = W * (0.42 + 0.58 * t ** 1.6)
        if t > 0.82:
            wid *= math.sqrt(max(0.0, 1 - 0.55 * ((t - 0.82) / 0.18) ** 2))
        base = H0.surf(0, y)
        out.append((-(y - up * t ** 3 * 0.5), base[2] + prot, wid))
    return np.array(out)


def mouth_line(n=13):
    """the closed lips' line (calm): x, y, z on the surface"""
    ym, w = P['mouth_y'], P['mouth_w']
    sm = EXPR['calm'].get('smile', 0)
    a = H0.a(ym)
    res = []
    for i in range(n):
        t = i / (n - 1); x = -w + 2 * w * t
        corner = sm * abs(2 * t - 1) ** 1.6
        y = -corner * 0.035 + sm * 0.01 * (1 - abs(2 * t - 1))
        res.append(surf(x / a, ym + y, 0.004))
    return np.array(res)


def ear_plate(side):
    """the ear: a C-shaped plate standing out (ear_out°) — its outline points, its root and its outward direction"""
    phi = side * P['ear_phi']; ye = P['ear_y']
    al = math.radians(P.get('ear_out', 25))
    u = np.array([side * max(math.sin(al), 0.4), 0.0, -math.cos(al)]); u /= np.linalg.norm(u)
    base = np.array(H0.surf(phi, ye, -0.01))
    W, Hh = P['ear_w'], P['ear_h']
    loc = [(0.0, -0.42), (0.35, -0.55), (0.8, -0.45), (1.0, -0.1), (0.85, 0.3), (0.5, 0.52), (0.2, 0.5), (0.0, 0.32)]
    pts = np.array([base + u * a * W + np.array([0, b * Hh, 0]) for a, b in loc])
    return hu(pts), hu(base), hu(u)


if __name__ == '__main__':
    V, T = loft_mesh()
    print('loft', V.min(0).round(3), V.max(0).round(3))
    for s in (-1, 1):
        print('eye', s, eye_centre(s).round(3), eye_opening(s)[0].min(0).round(3), eye_opening(s)[0].max(0).round(3))
    print('nose tip', nose_slices()[-1].round(3))
    print('mouth', mouth_line()[[0, 6, -1]].round(3))
    print('ear', ear_plate(1)[1].round(3), ear_plate(1)[0].max(0).round(3))
