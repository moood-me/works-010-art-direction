"""Тим's head from the Human Base Meshes stylised head (CC0):
1. the face's front (eyes, nose, mouth with their linings) is cut out and closed by a smooth patch (biharmonic
   fairing): Тим's features are painted, a Blair face is a smooth round surface;
2. the head is bent to the drawing's front and side outlines by a thin-plate warp: points on the base's silhouettes
   (the midline profile front and back, the widest points each height, the neck) go to the drawing's;
3. a button nose where the drawing has it; the ears made larger and turned out as the drawing's stick out.
Output: the head in metres in its own frame (the drawing's head centre at 0; x his left, y up, z forward)."""
import numpy as np, igl
from scipy.interpolate import RBFInterpolator
from hbm import load, largest, clean, loops, close, tris
from drawing import K, FRONT, SIDE_NO_NOSE, extent
from common import CACHE, vertex_normals

CROWN_B, CHIN_B = 0.887, 0.588


def cut_and_fair():
    V, Q, vis = load()
    C = V[Q].mean(1)
    mask = (((C[:, 0] / 0.112) ** 2 + ((C[:, 1] - 0.668) / 0.106) ** 2) < 1) & (C[:, 2] > 0.05)
    Q = clean(largest(V, Q[~mask]))
    used = np.unique(Q); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used)); V, Q = V[used], remap[Q]
    L = loops(Q); assert len(L) == 1, [len(l) for l in L]
    V, Q, new = close(V, Q, L[0], rings=8)
    T = tris(Q)
    # free: the patch and two rings around it, so the face goes over smoothly
    free = set(new.tolist())
    adj = igl.adjacency_list(T)
    ring = set(L[0])
    for _ in range(6):
        free |= ring; ring = {k for v in ring for k in adj[v]} - free
    fixed = np.array(sorted(set(range(len(V))) - free))
    W = igl.harmonic(V, T, fixed, V[fixed], 2)
    return W, Q


def landmarks(V):
    """pairs (base point → drawing point, metres in the head frame)"""
    ty = lambda y: -106 + (CROWN_B - y) / (CROWN_B - CHIN_B) * 194     # base height → drawing y
    src, dst = [], []
    zc = 0.0          # the base's axis (ear) ↔ the drawing's side x = −8
    def add(p, x, y, z): src.append(p); dst.append((x * K, -y * K, z * K))
    mid = V[np.abs(V[:, 0]) < 0.006]
    for yb in np.linspace(CHIN_B + 0.01, CROWN_B - 0.012, 30):
        y = ty(yb)
        s = mid[np.abs(mid[:, 1] - yb) < 0.005]
        if len(s) == 0: continue
        f = s[s[:, 2].argmax()]; b = s[s[:, 2].argmin()]
        xf = extent(SIDE_NO_NOSE, y, +1); xb = extent(SIDE_NO_NOSE, y, -1)
        if xf is not None and f[2] > 0.03: add(f, f[0], y, xf + 8)
        if xb is not None and y < 60 and b[2] < -0.03: add(b, b[0], y, xb + 8)
        # the widest points each height (in front of the ears and behind them where the ears are)
        a = extent(FRONT, y, +1)
        sl = V[np.abs(V[:, 1] - yb) < 0.004]
        ear = 0.68 < yb < 0.80
        for sgn in (1, -1):
            for sel, k in ((sl[:, 2] > 0.045, 0.97), (sl[:, 2] < -0.05, 0.95)) if ear else ((np.ones(len(sl), bool), 1.0),):
                ss = sl[sel & (sgn * sl[:, 0] > 0)]
                if len(ss) == 0 or a is None: continue
                p = ss[(sgn * ss[:, 0]).argmax()]
                add(p, sgn * a * k, y, p[2] / K * 0.92 + 8 * 0)
    # round cross-sections: at each height points all round the head go onto the ellipse the two outlines give
    # (front: half-width a; side: front and back extents about the ear) — keeps the jaw full and the skull round
    for yb in np.linspace(CHIN_B + 0.03, CROWN_B - 0.03, 16):
        y = ty(yb)
        if y > 76 or y < 40: continue
        a = extent(FRONT, y, +1); xf = extent(SIDE_NO_NOSE, y, +1); xb = extent(SIDE_NO_NOSE, y, -1)
        if None in (a, xf, xb): continue
        sl = V[np.abs(V[:, 1] - yb) < 0.004]
        zc = (sl[:, 2].max() + sl[:, 2].min()) / 2
        ang = np.arctan2(sl[:, 0], sl[:, 2] - zc)
        ear = 0.665 < yb < 0.815
        for phi in np.radians([-60, -35, 35, 60]):
            if ear and 50 < abs(np.degrees(phi)) < 135: continue
            if abs(np.degrees(phi)) > 100 and y > 50: continue
            p = sl[np.abs(((ang - phi + np.pi) % (2 * np.pi)) - np.pi).argmin()]
            c = (xf + 8) if np.cos(phi) > 0 else -(xb + 8)
            r = 1 / np.sqrt((np.sin(phi) / a) ** 2 + (np.cos(phi) / c) ** 2)
            add(p, r * np.sin(phi), y, r * np.cos(phi))
    # the crown
    top = V[V[:, 1].argmax()]; add(top, 0, -106, top[2] / K * 0.92)
    # the neck: the base's neck rings → the drawing's neck (front ±22, side from −20 to 24 about the ear's −8)
    for yb, yd in ((0.56, 110), (0.53, 134)):
        sl = V[np.abs(V[:, 1] - yb) < 0.004]
        for p, (x, z) in ((sl[sl[:, 2].argmax()], (0, 24 + 8)), (sl[sl[:, 2].argmin()], (0, -20 + 8)),
                          (sl[sl[:, 0].argmax()], (22, None)), (sl[sl[:, 0].argmin()], (-22, None))):
            add(p, x if z is None else p[0] / K, yd, z if z is not None else p[2] / K)
    return np.array(src), np.array(dst)


def warp(V):
    src, dst = landmarks(V)
    keep = []
    for i, p in enumerate(src):          # no two pairs from nearly the same base point
        if all(np.linalg.norm(p - src[k]) > 0.008 for k in keep): keep.append(i)
    src, dst = src[keep], dst[keep]
    f = RBFInterpolator(src, dst - src, kernel='thin_plate_spline', smoothing=1e-5, degree=1)
    return V + f(V), src, dst


if __name__ == '__main__':
    V, Q = cut_and_fair()
    W, src, dst = warp(V)
    np.savez(f'{CACHE}/head_steps.npz', faired=V, warped=W, Q=Q, src=src, dst=dst)
    print('head', W.min(0) / K, W.max(0) / K)
