"""The head: the Human Base Meshes stylised head (CC0) fitted to the drawing's head (the character's head data, pix.Head).

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




def mirror_index(V):
    from scipy.spatial import cKDTree
    d, i = cKDTree(V).query(V * [-1, 1, 1])
    return i



def outer_surface(V, T, extra):
    """which vertices are on the outer surface: the first hit of a ray from outside toward the centre (the eyeballs
    in `extra` close the sockets)"""
    AV = np.r_[V] if extra is None else np.r_[V, extra[0]]
    AT = T if extra is None else np.r_[T, extra[1] + len(V)]
    dirs = unit(V - CEN); out = np.zeros(len(V), bool)
    for i, (v, d) in enumerate(zip(V, dirs)):
        h = igl.ray_mesh_intersect(CEN + d * 300, -d, AV, AT, True)
        if h: out[i] = np.linalg.norm(CEN + d * (300 - h[0][1]) - v) < 0.6
    return out


def ear_residual(V, outer):
    """how far each vertex stands out of the skull's smooth form, in a band where the ears are (0 elsewhere)"""
    band = (np.abs(V[:, 0]) > 22) & (V[:, 1] > -30) & (V[:, 1] < 25) & (V[:, 2] < 15) & (V[:, 2] > -25)
    D = unit(V - CEN); R = np.linalg.norm(V - CEN, axis=1)
    sel = outer & ~band & (V[:, 1] > -44)
    f = RBFInterpolator(D[sel], R[sel], kernel='thin_plate_spline', smoothing=40.0, degree=1)
    return (R - f(D)) * band


def build():
    from eyefit import fit_eyes
    from features import place_features
    B = load(); V, T, P = B['head']
    EL, ET, _ = B['eyeL']; ER = B['eyeR'][0]
    mi = mirror_index(V)
    outer = outer_surface(V, T, (np.r_[EL, ER], np.r_[ET, ET + len(EL)]))
    outer = outer & outer[mi]
    ear = (np.abs(V[:, 0]) > 30) & (V[:, 1] > -22) & (V[:, 1] < 18) & (V[:, 2] < 10)
    neck = V[:, 1] < -44
    k, _, _ = shape_map(V, outer, ~ear & ~neck)
    V1 = CEN + (V - CEN) * k(V)[:, None]
    eyes = {s: CEN + (B['eye' + s][0] - CEN) * k(B['eye' + s][0])[:, None] for s in 'LR'}
    V2, balls = fit_eyes(V1, P, eyes, mi, V)
    er = ear_residual(V, outer)
    V3, info = place_features(V2, T, P, mi, outer, er, er != 0, V)
    np.savez(f'{CACHE}/head_fit.npz', base=V, shaped=V1, eyes=V2, final=V3, T=T,
             balls=np.array([np.r_[balls['L'][0], balls['L'][1]], np.r_[balls['R'][0], balls['R'][1]]]), mirror=mi, outer=outer)
    return V3, T, P, balls


if __name__ == '__main__':
    V3, T, P, balls = build()
    from look import views
    from sphere import sphere
    from drawing import head_mesh
    ms = [(V3, T, [0.85, 0.85, 0.85])] + [(*sphere(*balls[s]), [0.95, 0.95, 1.0]) for s in 'LR']
    DV, DT = head_mesh(); DV = np.c_[DV[:, 0], -DV[:, 1], DV[:, 2]]
    views(ms, overlay=(DV, DT), path=f'{CACHE}/head_fit.png')
    views(ms, yaws=(0, -0.62, -1.5708), size=500, box=(-50, 50, -55, 45), path=f'{CACHE}/head_fit_z.png')
