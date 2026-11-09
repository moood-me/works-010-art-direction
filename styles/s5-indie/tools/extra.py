"""Shared parts added with Марат and Кира (the four don't use them): a limb with a changing width, a hand with a
thumb, a mass below a line on the head (a beard), a scalloped outline (curls), layers by depth, a lean of the body."""
import math
import geo
from geo import *
from cast import cheat, hair_keys, smooth_pts, SKIN, SKIN_SH


def limb(v, pts3, widths, fill, n=8, **kw):
    """A limb whose width changes along it (thick forearm -> wrist, baggy sleeve -> cuff): one flat shape with
    round ends. widths: one per key point, or any number spread evenly along the limb."""
    pts = [v.p(*p) for p in pts3]
    return limb2d(pts, widths, fill, n=n, **kw)


def limb2d(pts, widths, fill, n=8, **kw):
    dense = smooth_pts(pts, n=n) if len(pts) > 2 else [tuple(pts[0][k] + (pts[1][k] - pts[0][k]) * i / n for k in (0, 1)) for i in range(n + 1)]
    N = len(dense)
    left, right = [], []
    for i, p in enumerate(dense):
        a, b = dense[max(i - 1, 0)], dense[min(i + 1, N - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        t = i / (N - 1) * (len(widths) - 1)
        j = min(int(t), len(widths) - 2)
        w = (widths[j] + (widths[j + 1] - widths[j]) * (t - j)) / 2
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))

    def cap(i, j, r, sgn):
        # half a circle round the end: from one side through the direction of the limb to the other side
        if r < 1:
            return []
        tx, ty = dense[i][0] - dense[j][0], dense[i][1] - dense[j][1]
        L = math.hypot(tx, ty) or 1
        tx, ty = tx / L, ty / L
        nx, ny = -ty * sgn, tx * sgn
        c = dense[i]
        return [(c[0] + r * (nx * math.cos(a) + tx * math.sin(a)), c[1] + r * (ny * math.cos(a) + ty * math.sin(a)))
                for a in (math.pi * .25, math.pi * .5, math.pi * .75)]

    poly = left + cap(N - 1, N - 2, widths[-1] / 2, 1) + right[::-1] + cap(0, 1, widths[0] / 2, 1)
    kw.setdefault('size', max(widths) * 2.2)
    return shape(smooth(poly, k=1 / 7), fill, **kw)


def mitt(v, X, Y, Z, r, fill, thumb=None, **kw):
    """A hand: the ball of the style plus a thumb (dx, dy, dz from the centre) — a mitten, so a big hand can hold."""
    out = ''
    kw.setdefault('shade_col', SKIN_SH if fill == SKIN else None)
    if thumb:
        out += sphere(v, X + thumb[0], Y + thumb[1], Z + thumb[2], r * .5, fill, **kw)
    return out + sphere(v, X, Y, Z, r, fill, **kw)


def lay(v, X, Z, front=16., back=9.5, edge=-15.):
    """The layer of a part by where it is: in front of the body or behind it."""
    return (front if v.depth(X, Z) > edge else back) + v.depth(X, Z) * .001


def lean(v, side=0., fwd=0., pivot=(0, 0)):
    """A screen rotation for the upper body: `side` degrees seen from the front, `fwd` degrees forward seen in
    profile (negative — leaning back). The cheap way to a line of action in a kit of upright volumes."""
    return f'rotate({f(side * v.c + fwd * v.s)} {f(pivot[0])} {f(pivot[1])})'


def scallop(pts, amp, bumps, phase=0.):
    """A closed outline pushed out in round bumps (a cloud edge): curls."""
    pts = smooth_pts(list(pts) + [pts[0]], n=10)[:-1]
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    seg = [math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    L = sum(seg)
    out, s = [], 0
    for i, p in enumerate(pts):
        a, b = pts[i - 1], pts[(i + 1) % len(pts)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        l = math.hypot(tx, ty) or 1
        nx, ny = -ty / l, tx / l
        if nx * (p[0] - cx) + ny * (p[1] - cy) < 0:
            nx, ny = -nx, -ny
        k = amp * abs(math.sin(math.pi * (bumps * s / L + phase))) ** .7
        out.append((p[0] + nx * k, p[1] + ny * k))
        s += seg[i]
    return out


def mass_below(v, rings, line, fill, edge=None):
    """A mass on the lower head (a beard): the volume `rings`, kept below a line of keys (phi, y) on its own
    surface — hair_cap upside down. edge: the colour of the line drawn along the upper edge (None: no line)."""
    d = smooth(vol_outline(v, rings))
    keys = [(cheat(v, phi), y) for phi, y in hair_keys(line, v)]
    pts = smooth_pts([surf(v, rings, phi, y)[:2] for phi, y in keys])
    region = poly_d(pts + [(pts[-1][0] + 400, pts[-1][1]), (pts[-1][0] + 400, 600), (pts[0][0] - 400, 600), (pts[0][0] - 400, pts[0][1])], True)
    cid = uid('b')
    o = f'<clipPath id="{cid}"><path d="{region}"/></clipPath><g clip-path="url(#{cid})">{shape(d, fill, size=120)}</g>'
    if edge:
        seg, segs = [], []
        for phi, y in keys:
            x, yy, fc = surf(v, rings, phi, y)
            if fc > -.05 and y < 50:
                seg.append((x, yy))
            elif seg:
                segs.append(seg)
                seg = []
        if seg:
            segs.append(seg)
        cc = uid('b')
        o += f'<clipPath id="{cc}"><path d="{d}"/></clipPath><g clip-path="url(#{cc})">'
        for s in segs:
            if len(s) > 2:
                o += stroke(smooth(s, closed=False), col=edge)
        o += '</g>'
    return o


def band(v, rings, y, phis, width, col, out=1, line=True):
    """A band lying on a volume at height y (a function of phi or a number) over the angles phis; only its
    visible part is drawn."""
    yy = y if callable(y) else (lambda p: y)
    runs, run = [], []
    for p in phis:
        x, y_, fc = surf(v, rings, p, yy(p), out=out)
        if fc > -.02:
            run.append((x, y_))
        else:
            runs.append(run)
            run = []
    runs.append(run)
    o = ''
    for pts in runs:
        if len(pts) > 2:
            d = smooth(pts, closed=False)
            o += (stroke(d, width + 2 * geo.SW, cap='butt') if line else '') + stroke(d, width, col, cap='butt')
    return o


def front_patch(v, rings, rows, bottom_wave=0.):
    """A patch lying on the front of a volume (an apron): rows of (y, half-angle). Only the part turned to the
    viewer is taken, so in profile it is a strip along the front edge. Returns a closed polygon."""
    left, right = [], []
    for y, a in rows:
        vis = [p for p in [-a + i * 2 * a / 40 for i in range(41)] if surf(v, rings, p, y)[2] >= -.02]
        if not vis:
            continue
        left.append(surf(v, rings, vis[0], y)[:2])
        right.append(surf(v, rings, vis[-1], y)[:2])
    def edge(row):
        y, a = row
        ps = [p for p in [-a + i * 2 * a / 16 for i in range(17)] if surf(v, rings, p, y)[2] >= -.02]
        return [surf(v, rings, p, y + bottom_wave * math.cos(p * 1.4))[:2] for p in ps]
    return left + edge(rows[-1])[1:-1] + right[::-1] + edge(rows[0])[::-1][1:-1]
