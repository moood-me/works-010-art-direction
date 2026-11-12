"""Bodies in 3D, drawn by the pen: a posed skeleton, the torso as cross-sections along a bent spine, limbs as tapered
capsules, clothes as shells grown over them. Each group (an arm, a leg, the torso with its garments) is drawn as one
shape: a black copy a little larger and moved to the lower right under a white one — the union's outline, heavier on
the side away from the light — then tone, the cast shadow, folds and seams on top.

Units: the character's head height = 1; y down, the ground at y = 0; x to the character's left, z to its front.
A Body holds the joints (3D points) and the numbers of the torso; a garment is a dict (see `shell`, `sleeve`...)."""
import math, random
from pen import *
from head import View, Head, draw_head, EXPR, interp_table
from body import hand as hand2d, _hull


def lerp3(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def add3(a, b):
    return tuple(a[i] + b[i] for i in range(3))


# ---------------------------------------------------------------- the torso

def torso_ring(B, f, grow=0.0, n=40):
    """The torso's cross-section at height fraction f of the spine (0 the crotch, 1 the neck), in 3D."""
    w, zf, zb, sq = interp_table(B.sections, f)
    c, tw = B.spine_at(f)
    w += grow; zf += grow; zb += grow
    ct, st = math.cos(tw), math.sin(tw)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ca, sa = math.cos(a), math.sin(a)
        x = w * math.copysign(abs(ca) ** (2 / sq), ca)
        z = (zf if sa > 0 else zb) * math.copysign(abs(sa) ** (2 / sq), sa)
        X = x * ct + z * st
        Z = -x * st + z * ct
        pts.append((c[0] + X, c[1], c[2] + Z))
    return pts


class Body:
    def __init__(self, joints, sections, spine, twist=None):
        """joints: dict of 3D points (pelvis, waist, chest, neck; sh_l/r, el_l/r, wr_l/r; hip_l/r, kn_l/r, an_l/r,
        toe_l/r). sections: [(f, half-width, front, back, squareness)]. spine: [(f, (x, y, z))] the spine's points
        (0 = the crotch level, 1 = the base of the neck). twist: [(f, degrees)] the torso's turn along the spine."""
        self.j = joints
        self.sections = sections
        self.spine = spine
        self.twist = twist or [(0, 0), (1, 0)]

    def spine_at(self, f):
        S = self.spine
        if f <= S[0][0]:
            # below the crotch (a skirt, a coat's tails): straight on down
            a, b = S[0], S[1]
            t = (f - a[0]) / (b[0] - a[0])
            c = (a[1][0], a[1][1] + (b[1][1] - a[1][1]) * t, a[1][2])
        elif f >= S[-1][0]:
            c = S[-1][1]
        else:
            for i in range(len(S) - 1):
                if S[i][0] <= f <= S[i + 1][0]:
                    t = (f - S[i][0]) / (S[i + 1][0] - S[i][0])
                    c = lerp3(S[i][1], S[i + 1][1], t)
                    break
        T = self.twist
        tw = T[0][1]
        for i in range(len(T) - 1):
            if T[i][0] <= f <= T[i + 1][0]:
                tw = T[i][1] + (T[i + 1][1] - T[i][1]) * (f - T[i][0]) / (T[i + 1][0] - T[i][0])
        if f > T[-1][0]:
            tw = T[-1][1]
        return c, math.radians(tw)


def torso_outline(B, v, f0, f1, grow=0.0, levels=40, hem='front', top='back', flare=None):
    """The outline of the torso (or of a shell grown over it) between f0 (bottom) and f1 (top), as a screen
    polygon. The hem is the visible front arc of the bottom ring, so a jacket's edge curves round the body.
    flare(f) -> extra growth (a skirt, a coat's tails)."""
    R, L = [], []
    rings = []
    for i in range(levels + 1):
        f = f1 + (f0 - f1) * i / levels
        g = grow + (flare(f) if flare else 0.0)
        ring = torso_ring(B, f, g)
        rings.append(ring)
        best_r = best_l = None
        for p in ring:
            X = v.rot(p)[0]
            if best_r is None or X > best_r[0]:
                best_r = (X, p)
            if best_l is None or X < best_l[0]:
                best_l = (X, p)
        R.append(v(best_r[1])); L.append(v(best_l[1]))
    def arc(ring, front=True):
        P = [(v(p), v.depth(p)) for p in ring]
        n = len(P)
        ir = max(range(n), key=lambda i: P[i][0][0]); il = min(range(n), key=lambda i: P[i][0][0])
        # two ways from the right extreme to the left one; take the one through the nearer (or farther) points
        a1 = [P[(ir + k) % n] for k in range(((il - ir) % n) + 1)]
        a2 = [P[(ir - k) % n] for k in range(((ir - il) % n) + 1)]
        d1 = sum(d for _, d in a1) / len(a1); d2 = sum(d for _, d in a2) / len(a2)
        a = a1 if (d1 > d2) == front else a2
        return [p for p, _ in a]
    bottom = arc(rings[-1], hem == 'front')
    topa = arc(rings[0], top == 'front')
    poly_ = topa[::-1][1:-1] + R + bottom[1:-1] + L[::-1]
    return poly_, bottom, rings


# ---------------------------------------------------------------- limbs

def chain_outline(v, pts, radii, caps=(True, True), n=6):
    """The outline of a tapered capsule along 3D points with radii (head units): two offset lines and round caps."""
    P = [v(p) for p in pts]
    C = catmull(P, False, n)
    m = len(C)
    rr = []
    for i in range(m):
        t = i / (m - 1) * (len(pts) - 1)
        j = min(int(t), len(pts) - 2); u = t - j
        u2 = u * u * (3 - 2 * u)
        rr.append((radii[j] + (radii[j + 1] - radii[j]) * u2) * v.s)
    N = normals(C)
    Lf = [(c[0] + nn[0] * r, c[1] + nn[1] * r) for c, nn, r in zip(C, N, rr)]
    Rg = [(c[0] - nn[0] * r, c[1] - nn[1] * r) for c, nn, r in zip(C, N, rr)]
    out = list(Lf)
    if caps[1]:
        a = math.atan2(C[-1][1] - C[-2][1], C[-1][0] - C[-2][0])
        out += [(C[-1][0] + math.cos(a + math.pi / 2 - k * math.pi / 8) * rr[-1], C[-1][1] + math.sin(a + math.pi / 2 - k * math.pi / 8) * rr[-1]) for k in range(1, 8)]
    out += Rg[::-1]
    if caps[0]:
        a = math.atan2(C[0][1] - C[1][1], C[0][0] - C[1][0])
        out += [(C[0][0] + math.cos(a + math.pi / 2 - k * math.pi / 8) * rr[0], C[0][1] + math.sin(a + math.pi / 2 - k * math.pi / 8) * rr[0]) for k in range(1, 8)]
    return out, C, N, rr


def ring_around(v, a, b, t, r, front=True, n=16):
    """The visible half of a ring round the axis a->b at t (a cuff, a hem of a trouser leg)."""
    c = lerp3(a, b, t)
    d = [b[i] - a[i] for i in range(3)]
    L = math.sqrt(sum(x * x for x in d)) or 1
    d = [x / L for x in d]
    up = (0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0)
    e1 = [d[1] * up[2] - d[2] * up[1], d[2] * up[0] - d[0] * up[2], d[0] * up[1] - d[1] * up[0]]
    l1 = math.sqrt(sum(x * x for x in e1)) or 1
    e1 = [x / l1 for x in e1]
    e2 = [d[1] * e1[2] - d[2] * e1[1], d[2] * e1[0] - d[0] * e1[2], d[0] * e1[1] - d[1] * e1[0]]
    pts = [(c[0] + r * (math.cos(q) * e1[0] + math.sin(q) * e2[0]), c[1] + r * (math.cos(q) * e1[1] + math.sin(q) * e2[1]),
            c[2] + r * (math.cos(q) * e1[2] + math.sin(q) * e2[2])) for q in [2 * math.pi * k / n for k in range(n)]]
    dep = [v.depth(p) for p in pts]
    mid = sum(dep) / n
    vis = [v(p) for p, dd in zip(pts, dep) if (dd >= mid) == front]
    # order along the arc
    if len(vis) > 2:
        cx = sum(p[0] for p in vis) / len(vis); cy = sum(p[1] for p in vis) / len(vis)
        vis.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
        # cut the arc at its largest gap
        gaps = [math.hypot(vis[(i + 1) % len(vis)][0] - vis[i][0], vis[(i + 1) % len(vis)][1] - vis[i][1]) for i in range(len(vis))]
        k = max(range(len(gaps)), key=lambda i: gaps[i])
        vis = vis[k + 1:] + vis[:k + 1]
    return vis


# ---------------------------------------------------------------- drawing a group

def group(polys, lw, base=0.0, dark=0.35, black=False, off=0.05, s=100.0, extra='', light=(-1, -0.6), line=1.0, shadow=True):
    """polys: screen polygons of one group (their union is one shape). The outline: a black copy grown and moved to
    the lower right under the fill. base: tone of the fill; the cast shadow: `dark` (or black) on the far side."""
    if not polys:
        return ''
    o = lw * 0.45 * line
    paths = [poly(p) for p in polys]
    blk = ''.join(f'<path d="{d}" fill="{INK}" stroke="{INK}" stroke-width="{lw * 1.1 * line:.2f}" stroke-linejoin="round"/>' for d in paths)
    out = f'<g transform="translate({o:.1f},{o * 0.8:.1f})">{blk}</g>' + blk
    fill_base = PAPER if base <= 0 else f'url(#{tone_id(base)})'
    whites = ''.join(f'<path d="{d}" fill="{PAPER}"/>' for d in paths)
    out += whites
    cid = uid('gp')
    out += f'<clipPath id="{cid}">' + ''.join(f'<path d="{d}"/>' for d in paths) + '</clipPath>'
    inner = ''
    if shadow and (dark > 0 or black):
        dx, dy = off * s * -light[0], off * s * -light[1]
        fill_dark = INK if black else f'url(#{tone_id(dark)})'
        inner += ''.join(f'<path d="{d}" fill="{fill_dark}"/>' for d in paths)
        inner += ''.join(f'<path d="{d}" transform="translate({-dx:.1f},{-dy:.1f})" fill="{PAPER}"/>' for d in paths)
        if base > 0:
            inner += ''.join(f'<path d="{d}" transform="translate({-dx:.1f},{-dy:.1f})" fill="{fill_base}"/>' for d in paths)
    elif base > 0:
        inner += ''.join(f'<path d="{d}" fill="{fill_base}"/>' for d in paths)
    inner += extra
    out += f'<g clip-path="url(#{cid})">{inner}</g>'
    return out


def fold_lines(C, N, rr, at, lw, side=1, n=3, length=0.7, seed=1, ink=INK):
    """Folds across a limb near index `at` of its centre line, from one contour inwards."""
    rnd = random.Random(seed)
    out = []
    m = len(C)
    for k in range(n):
        i = max(1, min(m - 2, at + int((k - n / 2) * 2.2) + rnd.randint(-1, 1)))
        c, nn, r = C[i], N[i], rr[i]
        a = (c[0] + nn[0] * r * side * 0.98, c[1] + nn[1] * r * side * 0.98)
        L = r * 2 * length * rnd.uniform(0.6, 1.0)
        tx, ty = C[min(m - 1, i + 1)][0] - C[i - 1][0], C[min(m - 1, i + 1)][1] - C[i - 1][1]
        tl = math.hypot(tx, ty) or 1
        tx, ty = tx / tl, ty / tl
        b = (a[0] - nn[0] * side * L + tx * L * 0.35 * rnd.uniform(-1, 1), a[1] - nn[1] * side * L + ty * L * 0.35 * rnd.uniform(-1, 1))
        mid = ((a[0] + b[0]) / 2 + tx * L * 0.12, (a[1] + b[1]) / 2 + ty * L * 0.12)
        out.append(stroke([a, mid, b], [lw * 0.9, lw * 0.7, lw * 0.15], taper=(0.02, 0.5), fill=ink))
    return ''.join(out)


def shoe3d(v, heel, toe, width=0.17, height=0.2, toe_h=0.09, kind='shoe'):
    """A shoe: the hull of points of a rounded box from the heel to the toe on the ground."""
    pts = []
    d = [toe[i] - heel[i] for i in range(3)]
    L = math.sqrt(d[0] ** 2 + d[2] ** 2) or 1
    fx, fz = d[0] / L, d[2] / L
    sx, sz = -fz, fx
    for k in range(13):
        t = k / 12
        hh = height * (1 - t) ** 0.8 * (1 - 0.15 * t) + toe_h * t
        if kind == 'boot':
            hh = height * (1 - 0.65 * t ** 1.5)
        ww = width * (0.75 + 0.35 * math.sin(min(1, t * 1.3) * math.pi * 0.85)) * (1 - 0.35 * t ** 4)
        if t > 0.92:
            ww *= 0.8
        c = (heel[0] + fx * L * t, 0.0, heel[2] + fz * L * t)
        for a in range(10):
            q = math.pi * a / 9
            px = c[0] + sx * ww * math.cos(q)
            pz = c[2] + sz * ww * math.cos(q)
            py = -hh * math.sin(q) ** 0.6 if 0 < q < math.pi else 0.0
            pts.append((px, py, pz))
            pts.append((px, 0.0, pz))
    P = [v(p) for p in pts]
    hull = _hull(P)
    sole = [v((heel[0] + fx * L * t, -0.035, heel[2] + fz * L * t)) for t in [0, 0.5, 1.0]]
    return hull, sole


# ---------------------------------------------------------------- the head on a body

def head3d(v, mod, pit3, yaw_rel=0.0, pitch=0.0, roll=0.0, hs=1.0, e=None, part='all', lw=2.0):
    """The character's head with its neck standing on pit3 (the pit of the neck, 3D body point)."""
    x, y = v(pit3)
    s = v.s * hs
    vh = View(yaw=math.degrees(v.yaw) + yaw_rel, pitch=pitch, roll=roll, s=s, x=x, y=y - 0.80 * s)
    h = Head(mod.HEAD, EXPR.get(e) if isinstance(e, str) else e)
    if part == 'back':
        return mod.HAIR.back(h, vh, lw)
    if part == 'front':
        return mod.HAIR.front(h, vh, lw)

    class NoHair:
        def back(self, h, v, lw):
            return ''

        def front(self, h, v, lw):
            return ''
    return draw_head(h, vh, lw, hair=NoHair(), extras=mod.EXTRAS)


def hand_at(v, wrist3, elbow3, size, pose, twist=90, side=1, lw=2.0, turn=0.0, **k):
    """A hand at the wrist, pointing on along the forearm (turn: degrees more on the page)."""
    W = v(wrist3); E = v(elbow3)
    ang = math.degrees(math.atan2(W[1] - E[1], W[0] - E[0])) + turn

    class F:
        pass
    Fp = F(); Fp.s = v.s; Fp.lw = lw; Fp.flip = False
    Fp.p = lambda x, y: (x, y)
    Fp.P = lambda pts: [(q[0], q[1]) for q in pts]
    # hand2d works in "head units" through F.p; give it page coordinates with size in page units
    return hand2d(Fp, W, ang, size * v.s, pose, side=side, twist=twist, lw=lw * 0.8, **k)


# ---------------------------------------------------------------- a standing skeleton and its parts

MALE = [(0.0, 0.52, 0.30, 0.40, 2.2), (0.09, 0.66, 0.36, 0.48, 2.2), (0.25, 0.62, 0.38, 0.42, 2.2), (0.41, 0.58, 0.40, 0.38, 2.2),
        (0.58, 0.64, 0.45, 0.42, 2.3), (0.72, 0.70, 0.48, 0.45, 2.3), (0.84, 0.74, 0.42, 0.44, 2.4), (0.93, 0.60, 0.30, 0.36, 2.2),
        (1.0, 0.24, 0.19, 0.21, 2.0)]
FEMALE = [(0.0, 0.52, 0.30, 0.42, 2.2), (0.09, 0.68, 0.38, 0.52, 2.2), (0.25, 0.60, 0.36, 0.44, 2.2), (0.41, 0.47, 0.34, 0.34, 2.2),
          (0.56, 0.52, 0.40, 0.36, 2.2), (0.68, 0.56, 0.50, 0.40, 2.2), (0.80, 0.58, 0.40, 0.40, 2.3), (0.90, 0.52, 0.28, 0.32, 2.2),
          (1.0, 0.21, 0.17, 0.19, 2.0)]


def scale_sections(tab, w=1.0, d=1.0, belly=0.0, chest=1.0, hips=1.0):
    out = []
    for f, ww, zf, zb, sq in tab:
        k_b = max(0, 1 - abs(f - 0.45) / 0.3)
        k_c = max(0, 1 - abs(f - 0.72) / 0.2)
        k_h = max(0, 1 - abs(f - 0.12) / 0.2)
        m = w * (1 + (chest - 1) * k_c + (hips - 1) * k_h)
        out.append((f, ww * m, zf * d + belly * k_b, zb * d, sq))
    return out


def stand(H, sw=0.80, hw=0.30, female=False):
    """Joints of a person of height H (head units) standing at ease, facing +z."""
    y = lambda f: -f * H
    j = dict(
        crotch=(0, y(0.47), 0.0), pelvis=(0, y(0.50), 0.0), waist=(0, y(0.615), -0.02), chest=(0, y(0.72), 0.0),
        neck=(0, y(0.825), -0.06),
        sh_r=(-sw, y(0.79), -0.04), sh_l=(sw, y(0.79), -0.04),
        el_r=(-sw - 0.06, y(0.625), -0.08), el_l=(sw + 0.06, y(0.625), -0.08),
        wr_r=(-sw - 0.02, y(0.48), 0.05), wr_l=(sw + 0.02, y(0.48), 0.05),
        hip_r=(-hw, y(0.505), 0.0), hip_l=(hw, y(0.505), 0.0),
        kn_r=(-hw + 0.03, y(0.28), 0.06), kn_l=(hw - 0.03, y(0.28), 0.06),
        an_r=(-hw + 0.04, -0.27, -0.04), an_l=(hw - 0.04, -0.27, -0.04),
        heel_r=(-hw + 0.04, 0.0, -0.16), heel_l=(hw - 0.04, 0.0, -0.16),
        toe_r=(-hw - 0.06, 0.0, 0.9), toe_l=(hw + 0.06, 0.0, 0.9))
    return j


def spine_of(j, H):
    return [(0.0, j['crotch']), (0.35, j['waist']), (0.7, j['chest']), (1.0, j['neck'])]


def frac(H, yv, j):
    """The spine fraction at a height y."""
    y0, y1 = j['crotch'][1], j['neck'][1]
    return (yv - y0) / (y1 - y0)


def arm_chain(j, side, r=(0.17, 0.14, 0.11, 0.125, 0.075), until=1.0, grow=0.0):
    """The arm as points and radii: shoulder - mid upper arm - elbow - forearm - wrist; `until` cuts it short."""
    s, e, w = j['sh_' + side], j['el_' + side], j['wr_' + side]
    pts = [s, lerp3(s, e, 0.5), e, lerp3(e, w, 0.35), w]
    rad = [x + grow for x in r]
    return cut(pts, rad, until)


def leg_chain(j, side, r=(0.28, 0.22, 0.14, 0.165, 0.075), until=1.0, grow=0.0, top=None):
    h, k, a = j['hip_' + side], j['kn_' + side], j['an_' + side]
    if top:
        h = add3(h, top)
    pts = [h, lerp3(h, k, 0.45), k, lerp3(k, a, 0.3), a]
    rad = [x + grow for x in r]
    return cut(pts, rad, until)


def cut(pts, rad, until):
    if until >= 0.999:
        return pts, rad
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.dist(pts[i - 1], pts[i]))
    T = L[-1] * until
    P, R = [pts[0]], [rad[0]]
    for i in range(1, len(pts)):
        if L[i] < T:
            P.append(pts[i]); R.append(rad[i])
        else:
            u = (T - L[i - 1]) / ((L[i] - L[i - 1]) or 1)
            P.append(lerp3(pts[i - 1], pts[i], u)); R.append(rad[i - 1] + (rad[i] - rad[i - 1]) * u)
            break
    return P, R


def seams(v, pts3, lw, w=0.6, ink=INK):
    """A line on a surface (a seam, an edge, a placket) from 3D points."""
    return stroke([v(p) for p in pts3], [lw * w * 0.5, lw * w, lw * w * 0.6], taper=(0.15, 0.2), fill=ink)


def button(v, p, lw, r=1.4):
    X, Y = v(p)
    return f'<circle cx="{f1(X)}" cy="{f1(Y)}" r="{f1(lw * r)}" fill="{PAPER}" stroke="{INK}" stroke-width="{lw * 0.5:.2f}"/>'


def surf(B, f, a_deg, grow=0.0, dy=0.0):
    """A point on the torso (or a shell over it) at spine fraction f and angle a (0 = the front, + to the left)."""
    w, zf, zb, sq = interp_table(B.sections, f)
    c, tw = B.spine_at(f)
    w += grow; zf += grow; zb += grow
    a = math.radians(a_deg)
    sa, ca = math.sin(a), math.cos(a)
    x = w * math.copysign(abs(sa) ** (2 / sq), sa)
    z = (zf if ca > 0 else zb) * math.copysign(abs(ca) ** (2 / sq), ca)
    ct, st = math.cos(tw), math.sin(tw)
    return (c[0] + x * ct + z * st, c[1] + dy, c[2] - x * st + z * ct)
