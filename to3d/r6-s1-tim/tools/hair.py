"""Тим's hair from the drawing's own locks (cast.tim_hair: ribbons from a whorl at the back of the crown down to the
hairline all round, a fringe of tufts with sharp tips, a cowlick), each made a 3D lock: the same centre curve on the
drawing's shell (Shell: centre (0, −8, −4), radii 44/44/48, each point's lat, lon and lift k), the same widths, a
lens-shaped section with a thickness, the tip sharp. Under the locks a cap: the scalp above the hairline (hl_short)
lifted a little, so no skin shows between them. Everything is pushed out of the head. Head units, y up.
aux per vertex: (along the lock 0…1, across −1…1, lock id, 1 for the cap's 0)."""
import math
import numpy as np, igl
import drawing as DR
from meshcut import cut, smooth
import cast

SH_C = np.array([0.0, 8.0, -4.0]); SH_R = np.array([44.0, 44.0, 48.0])


def shell_pt(lat, lon, k):
    la, lo = math.radians(lat), math.radians(lon)
    return SH_C + SH_R * k * np.array([math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)])


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
        nn = shell_n(cen[i]) if cen[i][1] < SH_C[1] + SH_R[1] * 0.35 else None
        if nn is None:
            nn = np.array([cen[i][0] - SH_C[0], 0, (cen[i][2] - SH_C[2]) * 0.8]); nn /= np.linalg.norm(nn)
        sd = np.cross(t, nn); sd /= np.linalg.norm(sd); nn = np.cross(sd, t)
        w = wid[i]; h = max(0.25, min(thick * w, 3.2))
        s = i / (n - 1)
        for j in range(nv):
            q = 2 * math.pi * j / nv
            cq, sq = math.cos(q), math.sin(q)
            # a lens: the top rounded, the underside flatter, lying on the shell
            X.append(cen[i] + sd * w * cq + nn * (h * (sq if sq > 0 else 0.35 * sq) + h * 0.3))
            A.append((s, cq, lid, 1.0 if sq > 0 else 0.5))
    for i in range(n - 1):
        for j in range(nv):
            a_, b_ = i * nv + j, i * nv + (j + 1) % nv
            F += [(a_, b_, a_ + nv), (b_, b_ + nv, a_ + nv)]
    # close the root end
    c0 = len(X); X.append(cen[0]); A.append((0, 0, lid, 1))
    for j in range(nv): F.append((c0, (j + 1) % nv, j))
    return np.array(X), np.array(F), np.array(A, float)


def locks():
    H = cast.tim_hair()
    out = []
    for L in H.locks:
        ctrl = [shell_pt(sp[1], sp[2], sp[3]) for sp in L['pts']]
        cen, wid = catmull(ctrl, L['w'])
        out.append((cen, wid, L))
    return out


def push_out(X, HV, HT, gap):
    d, i, c = igl.signed_distance(X, HV, HT)[:3]
    move = d < gap
    n = X - c; n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
    n[d < 0] *= -1
    X = X.copy(); X[move] = c[move] + n[move] * gap
    return X


def build(HV, HT):
    parts_X, parts_F, parts_A = [], [], []
    n0 = 0
    # the cap: the scalp above the hairline (the locks end at hl_short(lon) − 4)
    p = (HV - SH_C) / SH_R
    lat = np.degrees(np.arcsin(np.clip(p[:, 1] / np.linalg.norm(p, axis=1), -1, 1)))
    lon = np.degrees(np.arctan2(p[:, 0], p[:, 2]))
    hl = np.array([cast.hl_short(l) for l in lon])
    f = (hl + 3) - lat
    cv, ct, _, edge = cut(HV, HT, f)
    from build_util import vnormals
    cn = vnormals(cv, ct)
    cv = cv + cn * 1.4
    cv = smooth(cv, ct, it=4, lam=0.4)
    parts_X.append(cv); parts_F.append(ct); parts_A.append(np.c_[np.zeros(len(cv)), np.zeros(len(cv)), np.full(len(cv), -1), np.zeros(len(cv))])
    n0 = len(cv)
    for k, (cen, wid, L) in enumerate(locks()):
        X, F, A = lock_mesh(cen, wid, lid=k)
        parts_X.append(X); parts_F.append(F + n0); parts_A.append(A); n0 += len(X)
    X = np.concatenate(parts_X); F = np.concatenate(parts_F); A = np.concatenate(parts_A)
    X = push_out(X, HV, HT, 0.9)
    return X, F, A
