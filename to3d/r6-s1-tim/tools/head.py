"""Тим's head: the Human Base Meshes stylised head (CC0) fitted to the drawing's head (cast.tim, pix.Head).

1. Shape: the drawing's head is a smooth ball (stacked superellipse sections); the base is a sculpted child's head.
   Seen from a centre inside the head, both are star-shaped. The base's low-frequency form r_B(dir) (a smooth fit of
   its outer surface's radius over directions, ears and neck left out) is made the drawing's r_D(dir) (the drawn ball
   without its bumps) by scaling every vertex's radius by r_D/r_B — the sculpted nose, lips, lids, sockets and ears
   ride on top, enlarged with the face. The linings inside (mouth bag, sockets) go with their direction.
2. Features: a thin-plate warp (scipy RBF) moves landmarks (eye centres and corners, nose tip, mouth corners and
   middle, chin) to where the drawing has them, everything far from them pinned.
3. The eyes: the eyeballs refitted as spheres behind the new lid openings (eye.py).
Head units (y up, crown +50, chin −50; x his left; z forward)."""
import numpy as np, igl
from scipy.interpolate import RBFInterpolator
from hbm import load
from drawing import head_mesh, C
from common import CACHE

CEN = np.array([0, 2.0, -4.0])


def unit(a): return a / np.linalg.norm(a, axis=-1, keepdims=True)


def radius_on(V, T, dirs, c=CEN):
    """the outermost hit of rays from c along dirs"""
    r = np.zeros(len(dirs))
    for i, d in enumerate(dirs):
        h = igl.ray_mesh_intersect(c, d, V, T, False)
        r[i] = h[-1][1] if h else np.nan
    return r


def fib(n):
    i = np.arange(n) + 0.5; phi = np.arccos(1 - 2 * i / n); th = np.pi * (1 + 5 ** 0.5) * i
    return np.c_[np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)]


def shape_map(V, outer, keep):
    """radius scale per direction: r_D / r_B (both smooth)"""
    D = unit(V - CEN); R = np.linalg.norm(V - CEN, axis=1)
    sel = outer & keep
    fB = RBFInterpolator(D[sel], R[sel], kernel='thin_plate_spline', smoothing=40.0, degree=1)
    DV, DT = head_mesh(bumps=False); DV = np.c_[DV[:, 0], -DV[:, 1], DV[:, 2]]
    S = fib(1500)
    rD = radius_on(DV, DT, S)
    ok = ~np.isnan(rD)
    fD = RBFInterpolator(S[ok], rD[ok], kernel='thin_plate_spline', smoothing=1.0, degree=1)
    return lambda X: fD(unit(X - CEN)) / fB(unit(X - CEN)), fB, fD


if __name__ == '__main__':
    B = load(); V, T, Q = B['head']
    outer = np.load(f'{CACHE}/outer.npy')
    ear = (np.abs(V[:, 0]) > 30) & (V[:, 1] > -22) & (V[:, 1] < 18) & (V[:, 2] < 10)
    neck = V[:, 1] < -44
    k, fB, fD = shape_map(V, outer, ~ear & ~neck)
    V1 = CEN + (V - CEN) * k(V)[:, None]
    np.savez(f'{CACHE}/head1.npz', V=V1)
    from look import views
    DV, DT = head_mesh(); DV = np.c_[DV[:, 0], -DV[:, 1], DV[:, 2]]
    views([(V1, T, [0.85, 0.85, 0.85])], overlay=(DV, DT), path=f'{CACHE}/head1.png')


def mirror_index(V):
    from scipy.spatial import cKDTree
    d, i = cKDTree(V).query(V * [-1, 1, 1])
    return i
