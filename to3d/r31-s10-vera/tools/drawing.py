"""Read Вера out of the С10 drawing code (styles/s10-ligne-claire/tools) — the drawing is built there as simple 3D
volumes, so its shapes can be taken as they are, in the drawing's own units (head crown to chin ~200, y down,
z toward the viewer, x to the viewer's right in the front view).

Writes OUT/drawing.npz:
  head_pts   the head surface (skull with brow, nose, lips, chin, ears, neck) as dense points — the fitting target
  hair_*     the cap of hair drawn back (the shell of cast.vera cut by its hairline, the edge smooth), the knot
  marks      every mark of the face and hair for each expression (json): polyline/shape, width, fill, material
Everything with head_rot = 0 and the figure's head drop, so it is in the figure's frame.
usage: python3 drawing.py OUT
"""
import sys, os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import who                                         # noqa: E402
import meshes as M                                 # noqa: E402
import head as H, features as F                    # noqa: E402
from cast import wrapdeg                           # noqa: E402

OUT = sys.argv[1]
DROP = who.DROP


def main():
    h, col = who.head()
    pts, lab = [], []
    for p in h.parts(1.6):
        if p.material != 'skin':
            continue
        P = np.stack([p.X, p.Y + DROP, p.Z], 1)
        pts.append(P)
        lab += [p.name] * len(P)
    head_pts = np.vstack(pts)

    # hair: the shell and hairline of cast.vera, as a mesh with a smooth edge
    shell = H.Shell([
        (-110, 8, -16, 2, -28, 2.0), (-103, 40, -14, 28, -58, 2.0), (-86, 60, -12, 50, -86, 2.1),
        (-64, 69, -10, 64, -100, 2.2), (-40, 71, -8, 72, -104, 2.4), (-16, 71, -6, 76, -101, 2.6),
        (6, 70, -4, 74, -96, 2.6), (26, 66, -2, 66, -88, 2.4), (44, 52, 0, 50, -76, 2.2)])
    hl = np.array([(-180, 44), (-120, 40), (-96, 16), (-86, 2), (-78, -22), (-60, -44), (-40, -54), (-18, -60),
                   (0, -62), (14, -64), (22, -68), (40, -58), (60, -46), (78, -24), (86, 2), (96, 16), (120, 40),
                   (180, 44)], float)
    sz = np.array([(-60, -20), (0, -16), (40, -14)], float)

    def margin(X, Y, Z, U, V):
        d = wrapdeg(U)
        return np.maximum(np.interp(d, hl[:, 0], hl[:, 1]) - Y, np.interp(Y, sz[:, 0], sz[:, 1]) - Z)
    u = np.linspace(0, 2 * np.pi, 200, endpoint=False)
    v = np.linspace(shell.ymin, shell.ymax, 64)
    hv, hq = M.grid_cut(lambda U, V: shell.point(U, V), u, v, margin)
    hv = hv + [0, DROP, 0]
    kv, kq = M.ellipsoid((0, 2 + DROP, -112), (30, 24, 18), nu=36, nv=18)

    from scene import Yaw
    for fn in ('eye_marks', 'brow_marks', 'mouth_marks', 'nose_marks', 'glasses_marks'):
        def tagged(*a, _f=getattr(F, fn), _t=fn.split('_')[0], **kw):
            out = _f(*a, **kw)
            for mk in out:
                mk.group = _t
            return out
        setattr(F, fn, tagged)
    marks = {}
    exprs = dict(F.EXPR)
    exprs.update(who.EXPR_OWN)
    for e, ex in exprs.items():
        out = []
        for f in h.marks:
            out += f(h, ex, Yaw(0))
        marks[e] = [dict(kind=mk.kind, w=mk.w, fill=mk.fill, stroke=mk.stroke, on=mk.on,
                         group=getattr(mk, 'group', 'hairline' if mk.on == 'hair' else 'detail'),
                         pts=(mk.pts + [0, DROP, 0]).round(3).tolist()) for mk in out]
    np.savez(os.path.join(OUT, 'drawing.npz'), head_pts=head_pts, head_lab=np.array(lab),
             hair_v=hv, hair_q=hq, knot_v=kv, knot_q=kq)
    json.dump(dict(marks=marks, colours=who.colours(), ear=h.p['ear'], neck=h.p['neck']),
              open(os.path.join(OUT, 'drawing.json'), 'w'))
    print(head_pts.shape, len(hq), {k: len(v) for k, v in marks.items()})


main()
