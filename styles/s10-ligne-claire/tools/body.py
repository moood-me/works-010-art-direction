"""Bodies and clothes for the ligne-claire renderer: tubes along 3D polylines (limbs, sleeves, trouser legs),
blobs (ellipsoids: hands, shoes, a bun), and Shells from head.py (torso, skirt, coat).  Units are the head's
(crown to chin about 200), y down; a figure stands on the floor at its `floor` y.
"""
import numpy as np
import r3
from head import Mark


def _spline(pts, n):
    """Catmull-Rom through 3D points, n samples."""
    P = np.asarray(pts, float)
    if len(P) == 2:
        t = np.linspace(0, 1, n)[:, None]
        return P[0] * (1 - t) + P[1] * t, np.linspace(0, 1, n)
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    seg = len(P) - 3
    out, tt = [], []
    for i in range(seg):
        p0, p1, p2, p3 = P[i:i + 4]
        m = max(2, n // seg)
        for t in np.linspace(0, 1, m, endpoint=(i == seg - 1)):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
            tt.append((i + t) / seg)
    return np.array(out), np.array(tt)


def tube(name, material, pts, radii, res, flat=1.0, caps=(True, True), line=True):
    """A tube along pts with radius profile radii (one per point, interpolated). flat < 1 squashes it front-to-back."""
    P0 = np.asarray(pts, float)
    L = float(np.sum(np.linalg.norm(np.diff(P0, axis=0), axis=1)))
    rmax = float(np.max(radii))
    n = int(L * res * 1.4) + 8
    C, tt = _spline(P0, n)
    r = np.interp(tt, np.linspace(0, 1, len(radii)), radii)
    T = np.gradient(C, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    # frame: keep 'side' near the x axis so flat tubes stay flat front-to-back
    ref = np.array([0, 0, 1.0])
    S = np.cross(T, ref)
    bad = np.linalg.norm(S, axis=1) < 1e-3
    S[bad] = np.cross(T[bad], [1, 0, 0])
    S /= np.linalg.norm(S, axis=1, keepdims=True)
    U = np.cross(S, T)
    m = int(2 * np.pi * rmax * res * 1.4) + 12
    a = np.linspace(0, 2 * np.pi, m, endpoint=False)
    Q = (C[:, None, :] + S[:, None, :] * (r[:, None, None] * np.cos(a)[None, :, None])
         + U[:, None, :] * (r[:, None, None] * flat * np.sin(a)[None, :, None]))
    Q = Q.reshape(-1, 3)
    parts = [Q]
    for k, end in enumerate(caps):
        if not end:
            continue
        c = C[0] if k == 0 else C[-1]
        rr = r[0] if k == 0 else r[-1]
        parts.append(_ellipsoid_pts(c, (rr, rr, rr * flat), res, frame=(S[0 if k == 0 else -1], T[0 if k == 0 else -1],
                                                                        U[0 if k == 0 else -1])))
    Q = np.vstack(parts)
    return r3.Part(name, material, Q[:, 0], Q[:, 1], Q[:, 2], line=line)


def _ellipsoid_pts(c, radii, res, frame=None):
    rx, ry, rz = radii
    rm = max(radii)
    nu, nv = int(2 * np.pi * rm * res * 1.4) + 12, int(np.pi * rm * res * 1.4) + 8
    u, v = np.meshgrid(np.linspace(0, 2 * np.pi, nu), np.linspace(0, np.pi, nv), indexing='ij')
    x = rx * np.cos(u) * np.sin(v)
    y = ry * np.cos(v)
    z = rz * np.sin(u) * np.sin(v)
    if frame is None:
        P = np.stack([x, y, z], -1).reshape(-1, 3)
    else:
        S, T, U = frame
        P = (x[..., None] * S + y[..., None] * T + z[..., None] * U).reshape(-1, 3)
    return P + np.asarray(c, float)


def blob(name, material, c, radii, res, rot=(0, 0, 0), line=True):
    """An ellipsoid, rotated by rot = (about x, about y, about z) in degrees."""
    P = _ellipsoid_pts((0, 0, 0), radii, res)
    P = rotate(P, rot) + np.asarray(c, float)
    return r3.Part(name, material, P[:, 0], P[:, 1], P[:, 2], line=line)


def rotate(P, rot):
    ax, ay, az = np.radians(rot)
    Rx = np.array([[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]])
    Ry = np.array([[np.cos(ay), 0, np.sin(ay)], [0, 1, 0], [-np.sin(ay), 0, np.cos(ay)]])
    Rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
    return P @ (Rz @ Ry @ Rx).T


def box_pts(c, size, res, rot=(0, 0, 0), round_=0.0):
    """Points on a box (a book, a folder, a briefcase)."""
    sx, sy, sz = size
    out = []
    for axis in range(3):
        for sgn in (-1, 1):
            dims = [sx, sy, sz]
            a, b = [i for i in range(3) if i != axis]
            na, nb = int(dims[a] * res * 1.5) + 2, int(dims[b] * res * 1.5) + 2
            A, B = np.meshgrid(np.linspace(-dims[a] / 2, dims[a] / 2, na), np.linspace(-dims[b] / 2, dims[b] / 2, nb))
            P = np.zeros(A.shape + (3,))
            P[..., a], P[..., b], P[..., axis] = A, B, sgn * dims[axis] / 2
            out.append(P.reshape(-1, 3))
    P = np.vstack(out)
    return rotate(P, rot) + np.asarray(c, float)


def box(name, material, c, size, res, rot=(0, 0, 0)):
    P = box_pts(c, size, res, rot)
    return r3.Part(name, material, P[:, 0], P[:, 1], P[:, 2])


def hand(name, c, direction, res, size=1.0, material='skin', rot=0.0, fist=False, side=1, spread=0.0):
    """A hand as the style draws it: a flat palm, the four fingers as one mitten split by three short lines, a
    thumb.  direction: where the fingers point; rot turns the palm about it; side: 1 right hand, -1 left.
    Returns (parts, marks)."""
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
    w = np.cross(d, up); w /= np.linalg.norm(w)
    n = np.cross(w, d)
    ca, sa = np.cos(np.radians(rot)), np.sin(np.radians(rot))
    w, n = w * ca + n * sa, -w * sa + n * ca
    s = size
    c = np.asarray(c, float)
    palm = _ellipsoid_pts((0, 0, 0), (9.5 * s, 10 * s, 3.6 * s), res, frame=(w, d, n)) + c
    if fist:
        fing = _ellipsoid_pts((0, 0, 0), (9.5 * s, 6.5 * s, 6 * s), res, frame=(w, d, n)) + c + d * 9 * s + n * 3 * s
    else:
        # fingers: a mitten a little narrower than the palm, slightly curled toward the palm
        fing = _ellipsoid_pts((0, 0, 0), (9 * s, 10.5 * s, 3.0 * s), res, frame=(w, d, n)) + c + d * 15 * s - n * 1.5 * s
    P = np.vstack([palm, fing])
    parts = [r3.Part(name, material, P[:, 0], P[:, 1], P[:, 2])]
    th = [c + w * side * 6 * s - d * 4 * s, c + w * side * (11 + spread) * s + d * 3 * s + n * 2.5 * s,
          c + w * side * (12 + spread) * s + d * 10 * s + n * 3.5 * s]
    parts.append(tube(name + 'T', material, th, [3.6 * s, 3.1 * s, 2.5 * s], res))
    marks = []
    if not fist:
        for k in (-1, 0, 1):
            a0 = c + d * 15 * s + w * k * 3.2 * s - n * 1.5 * s
            seg = [a0 + d * 2 * s + n * 3.1 * s, a0 + d * 9 * s + n * 2.6 * s]
            segb = [a0 + d * 2 * s - n * 3.1 * s, a0 + d * 9 * s - n * 2.6 * s]
            marks.append(Mark(np.array(seg), w=0.55, on=material, tol=2.5 * s))
            marks.append(Mark(np.array(segb), w=0.55, on=material, tol=2.5 * s))
    else:
        for k in (-1, 0, 1):
            a0 = c + d * 12 * s + w * k * 3.2 * s + n * 3 * s
            marks.append(Mark(np.array([a0 - d * 4 * s + n * 6 * s, a0 + n * 6.2 * s, a0 + d * 4 * s + n * 4 * s]),
                              w=0.55, on=material, tol=2.5 * s))
    return parts, marks


def ring_mark(center, axis, r, w=0.7, on=None, n=48, flat=1.0, arc=(0, 360)):
    """A line around a tube (a cuff, a hem)."""
    axis = np.asarray(axis, float); axis /= np.linalg.norm(axis)
    ref = np.array([0, 0, 1.0])
    S = np.cross(axis, ref)
    if np.linalg.norm(S) < 1e-3:
        S = np.cross(axis, [1, 0, 0])
    S /= np.linalg.norm(S)
    U = np.cross(S, axis)
    a = np.radians(np.linspace(arc[0], arc[1], n))
    P = np.asarray(center, float) + np.outer(np.cos(a) * r, S) + np.outer(np.sin(a) * r * flat, U)
    return Mark(P, w=w, on=on, tol=3)


def line3(pts, w=0.7, on=None, tol=3, n=40, stroke=None):
    P, _ = _spline(pts, n)
    m = Mark(P, w=w, on=on, tol=tol)
    if stroke:
        m.stroke = stroke
    return m


def dots3(pts, r, fill, on=None, w=0.6):
    """Buttons: small discs facing the viewer roughly (drawn as tiny shapes)."""
    out = []
    for p in pts:
        a = np.linspace(0, 2 * np.pi, 13)[:-1]
        P = np.asarray(p, float) + np.stack([np.cos(a) * r, np.sin(a) * r, 0 * a + 1.5], 1)
        out.append(Mark(P, kind='shape', fill=fill, w=w, on=on, tol=6))
    return out
