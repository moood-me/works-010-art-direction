"""The head: Blender's Human Base Meshes stylised head (CC0), fitted to the drawing's front and profile silhouettes
(drawing.py), made plain where the drawing paints (eyes, mouth), its nose replaced by the drawing's.
From Р12's head.py (to3d/r12-s12-anya), with the character's numbers taken from drawing.py."""
import numpy as np
import mesh as M
import drawing as D

C0 = 2.082951545715332   # the bundle's head stands at x=2.083
Y_BASE = [0.513, 0.575, 0.7287, 0.888]      # the base's own heights: the neck's end, chin, eye line, crown


def conv(v):
    return np.c_[v[:, 0] - C0, v[:, 2], -v[:, 1]]


def load(path):
    d = np.load(path)
    return conv(d['head_v']), M.polys_of(d['head_fs'], d['head_f']), conv(d['L_v']), conv(d['R_v'])


def smooth01(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def _fillnan(a):
    i = np.arange(len(a)); ok = ~np.isnan(a)
    return np.interp(i, i[ok], a[ok])


def ears(v):
    return (abs(v[:, 0]) > 0.085) & (v[:, 2] > -0.05) & (v[:, 2] < 0.075) & (v[:, 1] > 0.64) & (v[:, 1] < 0.80)


def targets(yd):
    """The drawing's half-width (front) and front/back (profile) at drawing heights yd: the head, then the neck."""
    chin = D.Y_DRAW[1]
    f = D.profile(D.FACE_F, yd); s = D.profile(D.FACE_S, yd)
    w, zf, zb = f[:, 1].copy(), s[:, 1].copy(), s[:, 0].copy()
    nk = np.interp(yd, *D.NECK_W); nf = np.interp(yd, *D.NECK_F); nb = np.interp(yd, *D.NECK_B)
    below = yd >= chin + 2
    w = np.where(below | np.isnan(w), np.maximum(nk, np.nan_to_num(w, nan=0)), w)
    zf = np.where(below | np.isnan(zf), nf, zf)
    zb = np.where((yd >= D.NECK_B[0][0]) | np.isnan(zb), nb, zb)       # the nape: from the skull's back to the neck's
    return w, zf, zb


def fit(v, ears_mask, extra=(), ear=None):
    """The base head into the drawing: heights piecewise by its landmarks, then each height's width (front) and
    front/back (profile) to the drawing's. Returns 3D metres (y up, facing +z).
    ear: (root x, scale xyz) for the ears."""
    yd = np.interp(v[:, 1], Y_BASE, D.Y_DRAW)
    bins = np.arange(D.Y_DRAW[3] - 4, D.Y_DRAW[0] + 6, 4.0)
    w_c, zf_c, zb_c = [], [], []
    for b in bins:
        m = (abs(yd - b) < 9) & ~ears_mask
        if m.sum() < 3: w_c.append(np.nan); zf_c.append(np.nan); zb_c.append(np.nan); continue
        # the face's width is the face's, not the skull's behind it (FACE_ONLY: between these drawing heights the
        # width is measured in front of the ears only — a long narrow jaw is then fitted as a jaw)
        fo = getattr(D, 'FACE_ONLY', None); mw = m & (v[:, 2] > 0.0) if fo and fo[0] < b < fo[1] else m
        w_c.append(abs(v[mw if mw.sum() >= 3 else m, 0]).max()); zf_c.append(v[m, 2].max()); zb_c.append(v[m, 2].min())
    w_c, zf_c, zb_c = map(lambda a: _fillnan(np.array(a)), (w_c, zf_c, zb_c))
    w_t, zf_t, zb_t = map(_fillnan, targets(bins))
    sm = lambda a: np.convolve(np.pad(a, 2, mode='edge'), np.ones(5) / 5, 'valid')
    kx = sm(w_t * D.K / np.maximum(w_c, 1e-3))
    zf_t, zb_t = sm(zf_t * D.K), sm(zb_t * D.K)
    zf_c, zb_c = sm(zf_c), sm(zb_c)
    out = []
    for V in (v,) + tuple(extra):
        y = np.interp(V[:, 1], Y_BASE, D.Y_DRAW)
        x = V[:, 0] * np.interp(y, bins, kx)
        a, b = np.interp(y, bins, zb_c), np.interp(y, bins, zf_c)
        A, B = np.interp(y, bins, zb_t), np.interp(y, bins, zf_t)
        z = A + (V[:, 2] - a) / (b - a) * (B - A)
        out.append(np.c_[x, (D.FLOOR - y) * D.K, z])
    # the lower face fuller and flatter in front (the drawing's face is one round plane; the base has a muzzle)
    V = out[0]; y = yd; chin = D.Y_DRAW[1]
    # (the face's front without the nose: across the nose's heights, a straight line from above it to below it)
    n0, n1 = D.NOSE_SPAN; zp = zf_t.copy(); mm = (bins > n0) & (bins < n1)
    zp[mm] = np.interp(bins[mm], [n0, n1], [np.interp(n0, bins, zf_t), np.interp(n1, bins, zf_t)])
    zf = np.interp(y, bins, zp)
    # (PUSH_TOP: from which height down; FACE_R: the plane's radius — a print's face is flatter than a head, so that
    # in three-quarter the far eye is still on the face)
    top = getattr(D, 'PUSH_TOP', 10.0); fr = getattr(D, 'FACE_R', 0.085)
    wy = smooth01((y - top) / 30) * (1 - smooth01((y - chin) / 14))
    arc = zf - V[:, 0] ** 2 / (2 * fr * D.K / 0.00106) - 0.004
    push = np.clip(arc - V[:, 2], 0, None) * wy * (V[:, 2] > 0.0) * np.exp(-(V[:, 0] / (0.075 * D.K / 0.00106)) ** 4)
    V[:, 2] += 0.85 * push
    if ear is not None:
        e = ears_mask; c = V[e].mean(0)
        for s_ in (1, -1):
            m = e & (np.sign(V[:, 0]) == s_)
            root = np.array([s_ * ear[0], c[1], c[2]])
            V[m] = root + (V[m] - root) * ear[1]
    return out


def flatten(V, regions, front_min=0.0):
    """Where the drawing paints (eyes, the mouth's line), the base's sockets and lips are laid onto one smooth
    surface: inside each ellipse (drawing units: cx, cy, rx, ry) every vertex in front of front_min goes to the surface
    fitted (a quadratic) to the face around it; between the ellipse and 1.6× it, a blend."""
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
