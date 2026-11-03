"""Faces: features drawn in the face's flat coordinates and wrapped onto the head; ears, hair, bust.

Flat coordinates: x across the face (+x = the figure's left, which is the viewer's right in front view), y down,
eye line at y = 0. A point (x, y) sits on the head surface at that height where its sideways offset is x.
"""
import math
import numpy as np
from arc import *


def flat_uv(surf, x, y):
    """Angle u on a loft at height y whose sideways offset is x."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    u = np.arcsin(np.clip(x / 80.0, -0.99, 0.99))
    for _ in range(6):
        X, _, _ = surf.pos(u, y)
        x0 = interp(surf.x0, y) if getattr(surf, 'x0', None) else 0
        r = np.maximum(np.abs(X - x0), 1e-3)
        cur = X - x0
        # d x / d u ~ r cos u ; newton-like
        X2, _, _ = surf.pos(u + 1e-3, y)
        dxdu = (X2 - X) / 1e-3
        u = u - (cur - x) / np.where(np.abs(dxdu) < 1e-3, 1e-3, dxdu)
        u = np.clip(u, -math.pi, math.pi)
    return u


def wrap(surf, view, pts, lift=0.6):
    """Flat points [(x, y)] -> screen points and facing values."""
    P = np.array([(p[0], p[1]) for p in pts], float)
    u = flat_uv(surf, P[:, 0], P[:, 1])
    sp, nz = on_surface(surf, view, list(zip(u, P[:, 1])), lift)
    out = []
    for (x, y), p in zip(sp, pts):
        out.append((x, y, 1) if len(p) > 2 and p[2] else (x, y))
    return out, nz


def wrap_shape(surf, view, pts, closed=True, lift=0.6, minface=0.05, dens=6):
    """Wrap a smooth flat shape: sample its curve densely in flat space first."""
    fp = sample_curve(pts, closed, dens)
    sp, nz = wrap(surf, view, fp, lift)
    if np.mean(nz) < minface:
        return '', nz
    return ('M' + 'L'.join('%s,%s' % (fmt(x), fmt(y)) for x, y in [(q[0], q[1]) for q in sp]) + ('Z' if closed else '')), nz


def sample_curve(pts, closed=True, dens=6):
    """Points of a Catmull-Rom curve (corners kept) in flat space."""
    n = len(pts)
    P = [(p[0], p[1]) for p in pts]
    C = [len(p) > 2 and p[2] for p in pts]
    out = []
    segs = n if closed else n - 1
    for i in range(segs):
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[i]
        p1 = P[i]
        p2 = P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        if C[i]:
            c1 = p1
        if C[(i + 1) % n]:
            c2 = p2
        for k in range(dens):
            t = k / dens
            a = (1 - t) ** 3
            b = 3 * (1 - t) ** 2 * t
            c = 3 * (1 - t) * t ** 2
            d = t ** 3
            out.append((a * p1[0] + b * c1[0] + c * c2[0] + d * p2[0], a * p1[1] + b * c1[1] + c * c2[1] + d * p2[1]))
    if not closed:
        out.append(P[-1])
    return out


def mirror(pts):
    return [(-p[0], p[1]) + tuple(p[2:]) for p in pts]


def ribbon_flat(center, w0, w1, wmid=None):
    """A tapered ribbon in flat space as a closed point list."""
    c = sample_curve(center, False, 6)
    P = np.array(c)
    n = len(P)
    t = np.linspace(0, 1, n)
    if wmid is None:
        w = w0 + (w1 - w0) * t
    else:
        w = np.where(t < 0.5, w0 + (wmid - w0) * t / 0.5, wmid + (w1 - wmid) * (t - 0.5) / 0.5)
    d = np.gradient(P, axis=0)
    l = np.hypot(d[:, 0], d[:, 1]) + 1e-9
    nx, ny = -d[:, 1] / l, d[:, 0] / l
    L = list(zip(P[:, 0] + nx * w / 2, P[:, 1] + ny * w / 2))
    R = list(zip(P[:, 0] - nx * w / 2, P[:, 1] - ny * w / 2))[::-1]
    return L + R


def ribbon_flat_var(center, ws):
    """A ribbon with a width profile ws (list over t)."""
    c = sample_curve(center, False, 8)
    P = np.array(c)
    n = len(P)
    t = np.linspace(0, 1, n)
    w = np.interp(t, np.linspace(0, 1, len(ws)), ws)
    d = np.gradient(P, axis=0)
    l = np.hypot(d[:, 0], d[:, 1]) + 1e-9
    nx, ny = -d[:, 1] / l, d[:, 0] / l
    L = list(zip(P[:, 0] + nx * w / 2, P[:, 1] + ny * w / 2))
    R = list(zip(P[:, 0] - nx * w / 2, P[:, 1] - ny * w / 2))[::-1]
    return L + R


def lines_path(sp, closed=False):
    return 'M' + 'L'.join('%s,%s' % (fmt(q[0]), fmt(q[1])) for q in sp) + ('Z' if closed else '')
