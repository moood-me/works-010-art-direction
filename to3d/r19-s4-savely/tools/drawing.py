"""The character's drawing as data: the Arcane drawing (styles/s4-arcane/tools/cast.py, cast2.py) builds the head as a
3D loft with a nose surface and a neck loft, and the features (eyes, brows, mouth, lines) in the face's flat coordinates, which
are the front view's x, y. Here those surfaces are sampled as points (the target for fitting the base head) and the
features' shapes are kept for painting the face layer.
Units: the drawing's (eye line y = 0, y down, z toward the viewer, x to the figure's left; crown and chin from the head table, feet
from CAST).
usage: python3 drawing.py CACHE   → CACHE/drawing.npz
Imported: drawing.person() gives the drawing's Person; drawing.S4 is the style's tools folder. WHO names the
character; FIT holds what the head fit needs to know about this face (fit_head.py)."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S4 = os.path.normpath(os.path.join(HERE, '../../../styles/s4-arcane/tools'))
sys.path.insert(0, S4)
import cast  # noqa: E402
import cast2  # noqa: E402,F401  (adds Марат and Кира to CAST)
import person  # noqa: E402

WHO = 'savely'
BODY = 'moood-man'                                  # Anny's body the build starts from (engine/data/bodies)
NEUTRAL = dict(person.NEUTRAL, **cast.CAST[WHO]['neutral'])
FEET = cast.CAST[WHO]['feet']
# the head fit: the eye region's size over the head's scale and its widening (an old man's eyes are small and deep-set),
# how far the ball sits behind the face, the drawn neck's widening (the drawn neck is a stick in 3D)
FIT = dict(eye_scale=1.1, eye_wide=1.04, eye_back=3.5, neck_x=1.3, neck_z=1.2, ear=0.95, mouth_narrow=0.78)
# the painted face layer (faces.py): brows and moustache are 3D shells of hair, age spots on the bald head
FACE = dict(brows3d=True, lid_shade=0.22, mouth_w=0.8, ulip=0.9, lip_hi=0.25, spots=0.4, nose_blush=0.28, ear_blush=0.16)


def person():
    return cast.CAST[WHO]['make']()


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
    P = person()
    head, nose, neck = surfaces(P)
    H = sample(head, 360, 240)
    N = sample(nose, 80, 120)
    # the nose surface lies on the face; points of the face under it are inside the nose: drop them
    NK = sample(neck, 180, 120, 60, 170)
    pts = np.r_[H, N, NK]
    lab = np.r_[np.zeros(len(H)), np.ones(len(N)), np.full(len(NK), 2)].astype(int)
    np.savez(os.path.join(C, 'drawing.npz'), pts=pts, lab=lab)
    print('head', H.min(0).round(1), H.max(0).round(1), 'nose', N.min(0).round(1), N.max(0).round(1), 'neck', NK.min(0).round(1), NK.max(0).round(1))
