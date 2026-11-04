"""Read Савелий Петрович out of the С10 drawing code (styles/s10-ligne-claire/tools) — the drawing is built there as
simple 3D volumes, so its shapes can be taken as they are, in the drawing's own units (head crown to chin ~200,
y down, z toward the viewer, x to the viewer's right in the front view).

Writes OUT/drawing.npz:
  head_pts   the head surface (skull with brow, nose, lips, chin, ears, neck) as dense points — the fitting target
  hair_*     the white horseshoe of hair as a grid mesh (verts, quads) with its keep mask applied
  stache_*   the two moustache wings as grid meshes
  marks      every mark of the face for each expression (json): polyline/shape, width, fill, material it lies on
Everything with head_rot = 0 and the figure's head drop (20), so it is in the figure's frame.
usage: python3 drawing.py OUT
"""
import sys, os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LC = os.path.join(HERE, '../../../styles/s10-ligne-claire/tools')
sys.path.insert(0, LC)
import cast, figures, head as H, features as F   # noqa: E402
from cast import wrapdeg, sq                       # noqa: E402

OUT = sys.argv[1]
DROP = 20.0


def grid_quads(nu, nv, closed_u=False):
    q = []
    for i in range(nu - (0 if closed_u else 1)):
        for j in range(nv - 1):
            a = i * nv + j
            b = ((i + 1) % nu) * nv + j
            q.append((a, b, b + 1, a + 1))
    return np.array(q)


def main():
    h, col = cast.savely()
    # the fitting target: skull, bumps, ears, neck as points
    pts, lab = [], []
    for p in h.parts(1.6):
        if p.material != 'skin':
            continue
        P = np.stack([p.X, p.Y + DROP, p.Z], 1)
        pts.append(P)
        lab += [p.name] * len(P)
    head_pts = np.vstack(pts)

    # hair: rebuild the shell grid of cast.savely and keep the faces whose corners are all kept
    K = 0.95
    shell = H.Shell([
        (-80, 62, -14, 40, -86, 2.1), (-60, 76, -12, 60, -102, 2.2), (-40, 80, -10, 66, -105, 2.3),
        (-16, 81, -8, 70, -103, 2.5), (6, 80, -6, 68, -97, 2.5), (26, 77, -4, 60, -88, 2.3),
        (40, 70, -2, 50, -78, 2.1)])

    def keep(X, Y, Z, a):
        dd = wrapdeg(a)
        d = np.abs(dd)
        wave = 5 * np.sin(np.radians(dd) * 14)
        top = np.interp(d, [0, 74, 90, 120, 180], [200, 200, -14, -32, -40]) + wave
        bot = np.interp(d, [0, 74, 90, 110, 150, 180], [-200, -200, 8, 20, 30, 32]) + wave
        return (Y > top) & (Y < bot) & (Z < -4 + 0.4 * (Y + 14))
    def margin(X, Y, Z, a):
        # the same cut as a continuous margin (> 0 inside): the edge can then be found between grid points
        dd = wrapdeg(a)
        d = np.abs(dd)
        wave = 5 * np.sin(np.radians(dd) * 14)
        top = np.interp(d, [0, 74, 90, 120, 180], [200, 200, -14, -32, -40]) + wave
        bot = np.interp(d, [0, 74, 90, 110, 150, 180], [-200, -200, 8, 20, 30, 32]) + wave
        return np.minimum(np.minimum(Y - top, bot - Y), (-4 + 0.4 * (Y + 14)) - Z)
    nu, nv = 320, 80
    u, v = np.meshgrid(np.linspace(0, 2 * np.pi, nu, endpoint=False), np.linspace(shell.ymin, shell.ymax, nv),
                       indexing='ij')
    X, Y, Z = shell.point(u, v)
    f = margin(X, Y, Z, u)
    assert (keep(X, Y, Z, u) == (f > 0)).mean() > 0.995
    # a quad is kept if any corner is inside; its outside corners slide toward the inside ones to where the
    # margin crosses zero, so the edge is smooth instead of a staircase of grid cells
    U, Vv = u.copy(), v.copy()
    inside = f > 0
    su = np.zeros_like(u); sv = np.zeros_like(v); cnt = np.zeros_like(u)
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        fi = np.roll(f, (-di, -dj), (0, 1))
        ui = np.roll(u, (-di, -dj), (0, 1)); vi = np.roll(v, (-di, -dj), (0, 1))
        if dj:
            bad = np.zeros_like(inside); bad[:, -1 if dj > 0 else 0] = True
            fi = np.where(bad, -1, fi)
        ui = np.where(np.abs(ui - u) > np.pi, ui + np.sign(u - ui) * 2 * np.pi, ui)
        m = (~inside) & (fi > 0)
        t = np.clip(f / (f - fi + 1e-12), 0, 1)
        su += np.where(m, u + (ui - u) * t, 0); sv += np.where(m, v + (vi - v) * t, 0); cnt += m
    mv = cnt > 0
    U[mv], Vv[mv] = su[mv] / cnt[mv], sv[mv] / cnt[mv]
    X, Y, Z = shell.point(U, Vv)
    hv = np.stack([X.ravel(), Y.ravel() + DROP, Z.ravel()], 1)
    q = grid_quads(nu, nv, closed_u=True)
    ins = inside.ravel()
    q = q[ins[q].any(1) & (ins[q] | mv.ravel()[q]).all(1)]

    # moustache wings: lock_part grids (n along, m across)
    skull = H.Shell(h.p['slices'])
    stache = []
    for s in (1, -1):
        part = H.lock_part(skull, [(0, sq(51, K)), (s * -12, sq(52, K)), (s * -24, sq(56, K)),
                                   (s * -32, sq(63, K)), (s * -34, sq(68, K))],
                           [5, 7, 7, 5, 0], lift=[10, 9, 6, 4, 3], name=f'stache{s}', material='stache', res=1.0,
                           curl=2)
        P = np.stack([part.X, part.Y + DROP, part.Z], 1)
        mm = int(max(8, 7 * 2 * 1.0 * 1.5))
        n = len(P) // mm
        stache.append((P, n, mm))

    # marks for each expression, each tagged with what made it (eye, brow, mouth, nose, detail): the nose hook is
    # drawn only in near-front views, as in the drawing
    from scene import Yaw
    for fn in ('eye_marks', 'brow_marks', 'mouth_marks', 'nose_marks', 'glasses_marks'):
        def tagged(*a, _f=getattr(F, fn), _t=fn.split('_')[0], **kw):
            out = _f(*a, **kw)
            for mk in out:
                mk.group = _t
            return out
        setattr(F, fn, tagged)
    marks = {}
    for e, ex in F.EXPR.items():
        out = []
        for f in h.marks:
            out += f(h, ex, Yaw(0))
        marks[e] = [dict(kind=mk.kind, w=mk.w, fill=mk.fill, stroke=mk.stroke, on=mk.on,
                         group=getattr(mk, 'group', 'detail'),
                         pts=(mk.pts + [0, DROP, 0]).round(3).tolist()) for mk in out]
    np.savez(os.path.join(OUT, 'drawing.npz'), head_pts=head_pts, head_lab=np.array(lab),
             hair_v=hv, hair_q=q,
             stache0=stache[0][0], stache0_nm=stache[0][1:], stache1=stache[1][0], stache1_nm=stache[1][1:])
    json.dump(dict(marks=marks, colours=dict(col, **figures.SAVELY_COL), ear=h.p['ear'], neck=h.p['neck']),
              open(os.path.join(OUT, 'drawing.json'), 'w'))
    print(head_pts.shape, len(q), {k: len(v) for k, v in marks.items()})


main()
