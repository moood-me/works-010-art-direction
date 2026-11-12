"""The head: Blender's Human Base Meshes stylised head (CC0) fitted to the drawing's front and profile silhouettes
(Р17 Тим's head.py; here in the head's own units, upright — build.py then pitches it and pushes it forward).
The head is laid on one designed form: at every height a superellipse whose half-width is the front view's and whose
front and back are the profile's; the base keeps a fifth of its own relief on it, its ears (small, under the hair) and
its topology. The nose is the profile's own wedge. Eye sockets and lips are laid flat where the drawing paints them (flatten)."""
import numpy as np
from scipy.interpolate import PchipInterpolator
import mesh as M
import drawing as D
import shapes as VW

C0 = 2.082951545715332   # the bundle's head stands at x=2.083
P = 2.25                 # the superellipse's power: a little squarer than an ellipse
NOSE_W = 11.0            # the nose's half-width (drawing units): a small sharp wedge


def conv(v):
    return np.c_[v[:, 0] - C0, v[:, 2], -v[:, 1]]


def load(path):
    d = np.load(path)
    return conv(d['head_v']), M.polys_of(d['head_fs'], d['head_f']), d


# the base's own heights (its units) → the drawing's (y down): neck's end, chin, eye line, crown
Y_BASE = [0.513, 0.575, 0.7287, 0.888]
Y_DRAW = [176.0, 112.0, 0.0, -126.0]
_ymap = PchipInterpolator(Y_BASE, Y_DRAW, extrapolate=False)
ydraw = lambda y: np.where(y < Y_BASE[0], Y_DRAW[0], np.where(y > Y_BASE[-1], Y_DRAW[-1], _ymap(np.clip(y, Y_BASE[0], Y_BASE[-1]))))
BINS = np.arange(-126, 177, 2.0)
sm = lambda a, n=7: np.convolve(np.pad(a, n // 2, mode='edge'), np.ones(n) / n, 'valid')


def _targets():
    f = np.array([D.profile(d, BINS)[:, 1] for d in VW.HEAD_F])
    w = np.nanmax(np.nan_to_num(f, nan=0), 0)
    pl = np.array([D.profile(d, BINS) for d in VW.PLANE_S]); hd = np.array([D.profile(d, BINS) for d in VW.HEAD_S])
    zb, zf = D.fillnan(np.nanmin(pl[:, :, 0], 0)), D.fillnan(np.nanmax(pl[:, :, 1], 0))
    nose = np.clip(D.fillnan(np.nanmax(hd[:, :, 1], 0)) - zf, 0, None)
    w[0] = 0; zf[0] = zb[0] = (zf[0] + zb[0]) / 2          # the crown is a point
    return sm(w, 3), sm(zf, 3), sm(zb, 3), nose


W_T, ZF_T, ZB_T, NOSE_T = _targets()


def shape(yd):
    """The designed head at drawing heights: half-width, front, back (drawing units)."""
    return np.interp(yd, BINS, W_T), np.interp(yd, BINS, ZF_T), np.interp(yd, BINS, ZB_T)


def ears(v):
    return (abs(v[:, 0]) > 0.098) & (v[:, 2] > -0.03) & (v[:, 2] < 0.06) & (v[:, 1] > 0.655) & (v[:, 1] < 0.80)


def fit(v, polys, extra=(), keep=0.2, ear=None):
    """ear: dict(root=(x, y, z) drawing units of the picture-right ear's root, h — its height, out — degrees it turns out)."""
    em = ears(v)
    yd = ydraw(v[:, 1])
    w_c, zf_c, zb_c = [], [], []
    for b in BINS:
        m = (abs(yd - b) < 5) & ~em
        if m.sum() < 3: w_c.append(np.nan); zf_c.append(np.nan); zb_c.append(np.nan); continue
        w_c.append(abs(v[m, 0]).max()); zf_c.append(v[m, 2].max()); zb_c.append(v[m, 2].min())
    w_c, zf_c, zb_c = (sm(D.fillnan(a), 9) for a in (w_c, zf_c, zb_c))
    out = []
    for V in (v,) + tuple(extra):
        y = ydraw(V[:, 1])
        a = V[:, 0] / np.maximum(np.interp(y, BINS, w_c), 1e-3)
        mc, hc = (np.interp(y, BINS, zf_c) + np.interp(y, BINS, zb_c)) / 2, (np.interp(y, BINS, zf_c) - np.interp(y, BINS, zb_c)) / 2
        b = (V[:, 2] - mc) / np.maximum(hc, 1e-3)
        rho = (abs(a) ** P + abs(b) ** P) ** (1 / P) + 1e-9
        k = rho ** keep / rho                           # toward the superellipse, a share of the relief kept
        w, zf, zb = shape(y)
        out.append((np.c_[a * k * w, y, (zf + zb) / 2 + b * k * (zf - zb) / 2], np.c_[a * w, y, (zf + zb) / 2 + b * (zf - zb) / 2]))
    H, plain = out[0]
    # the ears: the base's own, rigid, at the drawing's size and place, turned out; joined smoothly
    A = M.adjacency(len(v), polys)
    we = M.smooth(em.astype(float)[:, None], A, np.ones(len(v), bool), iters=6, lam=0.5)[:, 0]
    we = np.clip(we * 1.6, 0, 1)
    if ear:
        for sg in (1, -1):
            m = em & (np.sign(v[:, 0]) == sg)
            c = v[m].mean(0); c[0] = sg * abs(v[m, 0]).min()
            s = ear['h'] / ((v[m, 1].max() - v[m, 1].min()) / D.K)
            ang = -np.radians(ear['out']) * sg
            R = np.array([[np.cos(ang), 0, np.sin(ang)], [0, 1, 0], [-np.sin(ang), 0, np.cos(ang)]])
            mm = (we > 0) & (np.sign(v[:, 0]) == sg)
            q = (v[mm] - c) @ R.T * s
            E = np.c_[sg * ear['root'][0] + q[:, 0] / D.K, ear['root'][1] - q[:, 1] / D.K, ear['root'][2] + q[:, 2] / D.K]
            H[mm] = H[mm] * (1 - we[mm, None]) + E * we[mm, None]
    # the nose: the profile's own bump on the face's plane
    bump = np.interp(H[:, 1], BINS, NOSE_T)
    for X in [H] + [o[0] for o in out[1:]]:
        X[:, 2] += np.interp(X[:, 1], BINS, NOSE_T) * np.exp(-(X[:, 0] / NOSE_W) ** 2) * (X[:, 2] > 30)
    H = M.smooth(H, A, we < 0.5, iters=3, lam=0.5)
    res = [np.c_[X[:, 0] * D.K, (D.FLOOR - X[:, 1]) * D.K, X[:, 2] * D.K] for X in [H] + [o[0] for o in out[1:]]]
    return res, we


def flatten(V, regions, front_min=0.0):
    """Where the drawing paints (eyes, the mouth), the base's sockets and lips are laid onto one smooth surface: inside
    each ellipse (drawing units: cx, cy, rx, ry) every vertex in front of front_min goes to the surface fitted (a
    quadratic) to the face around it; between the ellipse and 1.6× it, a blend."""
    V = V.copy()
    xd, yd = V[:, 0] / D.K, D.FLOOR - V[:, 1] / D.K
    for cx, cy, rx, ry in regions:
        e = np.sqrt(((xd - cx) / rx) ** 2 + ((yd - cy) / ry) ** 2)
        front = V[:, 2] > front_min
        ring = (e > 1.15) & (e < 1.9) & front
        A = np.c_[np.ones(ring.sum()), xd[ring], yd[ring], xd[ring] ** 2, xd[ring] * yd[ring], yd[ring] ** 2]
        c, *_ = np.linalg.lstsq(A, V[ring, 2], rcond=None)
        z = np.c_[np.ones(len(V)), xd, yd, xd ** 2, xd * yd, yd ** 2] @ c
        t = np.clip((1.6 - e) / 0.6, 0, 1)
        t = t * t * (3 - 2 * t)
        m = front & (e < 1.6)
        V[m, 2] = V[m, 2] * (1 - t[m]) + z[m] * t[m]
    return V
