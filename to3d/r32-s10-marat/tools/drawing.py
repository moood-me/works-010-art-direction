"""Read Марат out of the С10 drawing code (styles/s10-ligne-claire/tools/marat.py) — the drawing is built there as
simple 3D volumes, so its shapes can be taken as they are, in the drawing's own units (head crown to chin ~200,
y down, z toward the viewer, x to the viewer's right in the front view).

Writes OUT/drawing.npz:
  head_pts   the head surface (skull with brow, nose, ears, neck) as dense points — the fitting target
  hair_*     the curly hair: marat.head's shell cut by its scalloped hairline, pushed into curls (extra.bumps)
  beard_*    the beard likewise
  mouth_top, mouth_bot   the laughing mouth's upper line and lower edge on the beard (extra.grin_marks at rest)
  marks      every mark of the face, hair and beard for each expression (json)
Everything with head_rot = 0 and the figure's head drop, so it is in the figure's frame.
usage: python3 drawing.py OUT
"""
import sys, os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import who                                         # noqa: E402
import meshes as M                                 # noqa: E402
import head as H, features as F, r3                # noqa: E402
import marat, extra                                # noqa: E402
from cast import wrapdeg                           # noqa: E402

OUT = sys.argv[1]
DROP = who.DROP


def curls(V, centre, amp, pitch, seed=0.0):
    p = extra.bumps(r3.Part('x', 'x', V[:, 0], V[:, 1], V[:, 2]), centre, amp, pitch, seed)
    return np.stack([p.X, p.Y, p.Z], 1)


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

    # hair and beard: the shells and cuts of marat.head (the cuts as margins, so the edges come out smooth)
    hair = H.Shell([
        (-121, 8, -16, 2, -28, 2.0), (-114, 46, -14, 32, -64, 2.0), (-97, 72, -12, 56, -96, 2.1),
        (-73, 85, -10, 72, -110, 2.2), (-46, 89, -8, 80, -110, 2.3), (-20, 90, -6, 82, -107, 2.4),
        (6, 88, -4, 78, -102, 2.4), (30, 84, -2, 68, -92, 2.3), (48, 76, 0, 58, -82, 2.1)])
    hl = np.array([(0, -55), (30, -57), (56, -50), (70, -36), (80, -20), (86, -8), (92, -14), (100, -14), (110, 4),
                   (124, 34), (180, 44)], float)

    def hair_margin(X, Y, Z, U, V):
        d = np.abs(wrapdeg(U))
        return np.interp(d, hl[:, 0], hl[:, 1]) + 7 * np.abs(np.sin(np.radians(wrapdeg(U) + 9) * 4.1)) - 4 - Y
    beard = H.Shell([
        (-22, 84, -2, 60, -60, 2.6), (10, 87, 0, 80, -50, 2.8), (40, 88, 4, 86, -30, 2.8), (60, 84, 8, 90, -10, 2.6),
        (80, 74, 14, 91, 0, 2.5), (100, 58, 22, 87, 6, 2.4), (116, 38, 30, 77, 10, 2.2), (127, 10, 40, 62, 26, 2.0)])
    bl = np.array([(0, 50), (14, 50), (24, 48), (36, 45), (50, 41), (62, 35), (72, 22), (78, 4), (83, -12), (90, -12)],
                  float)

    def beard_margin(X, Y, Z, U, V):
        dd = wrapdeg(U)
        d = np.abs(dd)
        top = np.interp(d, bl[:, 0], bl[:, 1]) + 2 - 5 * np.abs(np.sin(np.radians(dd) * 4.5))
        saw = 1 - np.abs((dd / 12) % 2 - 1)
        return np.minimum(np.minimum(Y - top, np.interp(Y, [20, 50], [87, 100]) - d),
                          np.minimum(Z + 26, 106 + 10 * saw ** 1.5 - Y))
    u = np.linspace(0, 2 * np.pi, 240, endpoint=False)
    hv, hq = M.grid_cut(lambda U, V: hair.point(U, V), u, np.linspace(hair.ymin, hair.ymax, 72), hair_margin)
    hv = curls(hv, (0, -22, -14), 6.0, 26) + [0, DROP, 0]
    bv, bq = M.grid_cut(lambda U, V: beard.point(U, V), u, np.linspace(beard.ymin, beard.ymax, 72), beard_margin)
    bv = curls(bv, (0, 62, 16), 4.0, 24, seed=0.4) + [0, DROP, 0]

    # the laughing mouth at rest (extra.grin_marks): its upper line and its lower edge, on the beard
    ob = extra.OnShell(beard, lift=5.0)
    W, op, c = marat.MOUTH['w'], marat.REST['open'], marat.REST['smile'] * 4.6
    top = [(-W, -c), (-W * 0.6, -c * 0.42), (-W * 0.2, -c * 0.06), (W * 0.2, -c * 0.06), (W * 0.6, -c * 0.42), (W, -c)]
    bot = [(-W, -c), (-W * 0.78, -c * 0.3 + op * 0.5), (-W * 0.36, op), (W * 0.36, op), (W * 0.78, -c * 0.3 + op * 0.5),
           (W, -c)]
    mouth_top = ob.on_face(0, marat.MOUTH['y'], top) + [0, DROP, 0]
    mouth_bot = ob.on_face(0, marat.MOUTH['y'], bot) + [0, DROP, 0]

    # marks, each tagged with what made it
    from scene import Yaw
    for fn in ('eye_marks', 'brow_marks', 'mouth_marks', 'nose_marks'):
        def tagged(*a, _f=getattr(F, fn), _t=fn.split('_')[0], **kw):
            out = _f(*a, **kw)
            for mk in out:
                mk.group = _t
            return out
        setattr(F, fn, tagged)

    def grin(*a, _f=marat.grin_marks, **kw):
        out = _f(*a, **kw)
        for mk in out:
            mk.group = 'mouth'
        return out
    marat.grin_marks = grin
    marks = {}
    exprs = dict(F.EXPR, calm=who.rest_expr())
    face_fn, details_fn = h.marks
    for e, ex in exprs.items():
        out = face_fn(h, ex, Yaw(0))
        for mk in out:                     # the broad nose's second wing is drawn by the face itself, front views only
            if not hasattr(mk, 'group'):
                mk.group = 'nose'
        out += details_fn(h, ex, Yaw(0))
        marks[e] = [dict(kind=mk.kind, w=mk.w, fill=mk.fill, stroke=mk.stroke, on=mk.on,
                         group=getattr(mk, 'group', 'detail'),
                         pts=(mk.pts + [0, DROP, 0]).round(3).tolist()) for mk in out]
    np.savez(os.path.join(OUT, 'drawing.npz'), head_pts=head_pts, head_lab=np.array(lab),
             hair_v=hv, hair_q=hq, beard_v=bv, beard_q=bq, mouth_top=mouth_top, mouth_bot=mouth_bot)
    json.dump(dict(marks=marks, colours=who.colours(), ear=h.p['ear'], neck=h.p['neck']),
              open(os.path.join(OUT, 'drawing.json'), 'w'))
    print(head_pts.shape, len(hq), len(bq), {k: len(v) for k, v in marks.items()})


main()
