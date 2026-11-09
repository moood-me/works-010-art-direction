"""Вера's hair from the drawing's own shapes (cast.vera_hair): a sleek cap — the drawing's hair shell (an ellipsoid,
centre (0, 13, −2), radii 46.5 / 47 / 52 in head units, y up) above its hairline hl_bun (a side parting on her right,
a swoop low over the left temple) —, a bun at the back (a ball of radius 17 at lat 40°, lon 180°, 1.12 of the shell)
and the grey streak swept back from the parting (a lock, as Тим's locks).

The cap is a grid laid from the bun: its meridians run from the hairline over the crown into the bun, the way the
hair is combed, so the strands of the look follow them. Each point lies on the shell or, where the head comes nearer
than 1.2 units, that far over the head; toward the hairline it comes down to the scalp, and the edge is turned in.
aux per vertex: (along 0…1 from the bun, the strand's turn round the bun 0…1, −1 for the cap / the lock's id, 1)."""
import math
import numpy as np, igl
from drawing import C
from meshcut import cut, smooth, loops, rim
from sphere import sphere

H = C['hair']
_sk = H.shell_kw
SH_C = np.array([_sk['c'][0], -_sk['c'][1], _sk['c'][2]], float); SH_R = np.array(_sk['r'], float)
_hl = H.hairline


def HL(lon):
    """the drawing's hairline; at the nape, which no drawing of Вера shows, it is taken lower (to −44° instead of −30°),
    so that the back of the head is not bare under the bun"""
    a = abs(((lon + 180) % 360) - 180)
    t = min(1.0, max(0.0, (a - 105) / 55)); t = t * t * (3 - 2 * t)
    return _hl(lon) - 14 * t


def shell_dir(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return np.array([math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)])


def shell_pt(lat, lon, k):
    return SH_C + SH_R * k * shell_dir(lat, lon)


def shell_n(p):
    n = (p - SH_C) / SH_R ** 2; return n / np.linalg.norm(n)


def catmull(ctrl, widths, m=8):
    cen, wid = [], []
    for i in range(len(ctrl) - 1):
        p0 = ctrl[max(0, i - 1)]; p1, p2 = ctrl[i], ctrl[i + 1]; p3 = ctrl[min(len(ctrl) - 1, i + 2)]
        for j in range(m):
            t = j / m; t2, t3 = t * t, t ** 3
            cen.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
            wid.append(widths[i] + (widths[i + 1] - widths[i]) * t)
    cen.append(ctrl[-1]); wid.append(widths[-1])
    return np.array(cen), np.array(wid)


def lock_mesh(cen, wid, thick=0.32, nv=10, lid=0):
    n = len(cen); X, A, F = [], [], []
    for i in range(n):
        a, b = cen[max(0, i - 1)], cen[min(n - 1, i + 1)]
        t = b - a; t /= np.linalg.norm(t)
        nn = shell_n(cen[i])
        sd = np.cross(t, nn); sd /= np.linalg.norm(sd); nn = np.cross(sd, t)
        w = wid[i]; h = max(0.25, min(thick * w, 3.2))
        s = i / (n - 1)
        for j in range(nv):
            q = 2 * math.pi * j / nv
            cq, sq = math.cos(q), math.sin(q)
            X.append(cen[i] + sd * w * cq + nn * (h * (sq if sq > 0 else 0.35 * sq) + h * 0.3))
            A.append((s, cq, lid, 1.0 if sq > 0 else 0.5))
    for i in range(n - 1):
        for j in range(nv):
            a_, b_ = i * nv + j, i * nv + (j + 1) % nv
            F += [(a_, b_, a_ + nv), (b_, b_ + nv, a_ + nv)]
    c0 = len(X); X.append(cen[0]); A.append((0, 0, lid, 1))
    for j in range(nv): F.append((c0, (j + 1) % nv, j))
    return np.array(X), np.array(F), np.array(A, float)


def push_out(X, HV, HT, gap):
    d, i, c = igl.signed_distance(X, HV, HT)[:3]
    move = d < gap
    n = X - c; n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
    n[d < 0] *= -1
    X = X.copy(); X[move] = c[move] + n[move] * gap
    return X


def cap(HV, HT, na=64, nt=120):
    b = shell_dir(H.bun['lat'], H.bun['lon'])
    e1 = np.cross([1.0, 0, 0], b); e1 /= np.linalg.norm(e1); e2 = np.cross(b, e1)
    X, A, f = [], [], []
    for i in range(na + 1):
        a = math.radians(4) + (math.pi - math.radians(4)) * i / na
        for j in range(nt):
            t = 2 * math.pi * j / nt
            u = math.cos(a) * b + math.sin(a) * (math.cos(t) * e1 + math.sin(t) * e2)
            lat = math.degrees(math.asin(max(-1, min(1, u[1])))); lon = math.degrees(math.atan2(u[0], u[2]))
            d = SH_R * u; ds = np.linalg.norm(d); d /= ds
            h = igl.ray_mesh_intersect(SH_C, d, HV, HT, False)
            dh = h[-1][1] if h else 0.0
            g = lat - HL(lon)                                    # degrees above the hairline
            edge = 1 - min(1.0, max(0.0, g / 14.0)) ** 0.6       # 1 at the hairline, 0 from 14° up
            r = max(ds, dh + 1.2)
            r = r * (1 - edge) + min(r, dh + 1.5) * edge
            X.append(SH_C + d * r); A.append((i / na, j / nt, -1.0, 1.0)); f.append(-g)
    X = np.array(X); A = np.array(A); f = np.array(f); F = []
    for i in range(na):
        for j in range(nt):
            a_, b_ = i * nt + j, i * nt + (j + 1) % nt
            F += [(a_, a_ + nt, b_), (b_, a_ + nt, b_ + nt)]
    F = np.array(F)
    X = smooth(X, F, it=6, lam=0.4)
    v, t, a, on = cut(X, F, f, A)
    # the hairline's edge turned in to the scalp
    for L in loops(t):
        L = np.array(L)
        if not on[L].mean() > 0.5: continue
        inward = SH_C - v[L]; inward /= np.linalg.norm(inward, axis=1, keepdims=True)
        v, t, a = rim(v, t, L, inward * 1.6, a)
    return v, t, a


def bun():
    c = shell_pt(H.bun['lat'], H.bun['lon'], H.bun['k']); r = H.bun['r']
    X, F = sphere(np.zeros(3), 1.0, n=28, m=40)
    ax = shell_dir(H.bun['lat'], H.bun['lon'])
    e1 = np.cross([1.0, 0, 0], ax); e1 /= np.linalg.norm(e1); e2 = np.cross(ax, e1)
    # the ball's pole along the bun's axis, a little flattened on it; the hair winds round the axis
    P = c + r * (np.outer(X[:, 1] * 0.86, ax) + np.outer(X[:, 0], e1) + np.outer(X[:, 2], e2))
    turn = (np.arctan2(X[:, 2], X[:, 0]) / (2 * np.pi)) % 1
    along = np.arccos(np.clip(X[:, 1], -1, 1)) / np.pi
    A = np.c_[along, (turn + 1.3 * along) % 1, np.full(len(X), -2.0), np.ones(len(X))]
    return P, F[:, ::-1], A


def build(HV, HT):
    cv, ct, ca = cap(HV, HT)
    bv, bt, ba = bun()
    parts = [(cv, ct, ca, 'hair'), (bv, bt, ba, 'hair')]
    for k, L in enumerate(H.locks):
        ctrl = [shell_pt(sp[1], sp[2], sp[3]) for sp in L['pts']]
        cen, wid = catmull(ctrl, L['w'])
        # the streak lies on the cap: its centre line is brought onto it
        d, i, c = igl.point_mesh_squared_distance(cen, cv, ct)
        n = np.array([shell_n(p) for p in c]); cen = c + n * 0.15
        X, F, A = lock_mesh(cen, wid * 0.85, thick=0.16, lid=k)
        X = push_out(X, cv, ct, 0.1); F = F[:, ::-1]
        parts.append((X, F, A, 'streak'))
    return parts
