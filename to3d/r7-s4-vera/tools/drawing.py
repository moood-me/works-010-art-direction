"""Вера's drawing as data: the Arcane drawing (styles/s4-arcane/tools/cast.py, vera()) builds her head as a 3D loft
with a nose surface and a neck loft, and her features (eyes, brows, mouth, lines) in the face's flat coordinates, which
are the front view's x, y. Here those surfaces are sampled as points (the target for fitting the base head) and the
features' shapes are kept for painting the face layer.
Units: the drawing's (eye line y = 0, y down, z toward the viewer, x to the figure's left; crown −122, chin 112,
feet 1656).
usage: python3 drawing.py CACHE   → CACHE/drawing.npz
Imported: drawing.vera() gives the drawing's Person; drawing.S4 is the style's tools folder."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S4 = os.path.normpath(os.path.join(HERE, '../../../styles/s4-arcane/tools'))
sys.path.insert(0, S4)
import cast  # noqa: E402
import person  # noqa: E402

NEUTRAL = dict(person.NEUTRAL, **cast.CAST['vera']['neutral'])
FEET = cast.CAST['vera']['feet']


def vera():
    return cast.vera()


def surfaces(P):
    head = P.head()
    nose = P.nose(head)
    neck = P.neck()
    return head, nose, neck


def sample(surf, nu, nv, v0=None, v1=None):
    u = np.linspace(surf.u0, surf.u1, nu)
    v = np.linspace(surf.v0 if v0 is None else v0, surf.v1 if v1 is None else v1, nv)
    U, V = np.meshgrid(u, v)
    X, Y, Z = surf.pos(U, V)
    return np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)


if __name__ == '__main__':
    C = sys.argv[1]
    P = vera()
    head, nose, neck = surfaces(P)
    H = sample(head, 360, 240)
    N = sample(nose, 80, 120)
    # the nose surface lies on the face; points of the face under it are inside the nose: drop them
    NK = sample(neck, 180, 120, 60, 170)
    pts = np.r_[H, N, NK]
    lab = np.r_[np.zeros(len(H)), np.ones(len(N)), np.full(len(NK), 2)].astype(int)
    np.savez(os.path.join(C, 'drawing.npz'), pts=pts, lab=lab)
    print('head', H.min(0).round(1), H.max(0).round(1), 'nose', N.min(0).round(1), N.max(0).round(1), 'neck', NK.min(0).round(1), NK.max(0).round(1))
