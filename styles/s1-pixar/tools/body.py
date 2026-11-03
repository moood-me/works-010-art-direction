"""body — torso sweeps, limb tubes, hands and shoes, all turned by one yaw, painted as soft volumes."""
import math
from pix import Head, paint_volume, smooth_path, mix, f, norm3, cross, spline


class Rig:
    """projection shared by every part of one figure"""

    def __init__(self, cx, cy, s, yaw=0.0):
        self.cx, self.cy, self.s, self.yaw = cx, cy, s, yaw

    def rot(self, p):
        x, y, z = p
        b = self.yaw
        return x * math.cos(b) + z * math.sin(b), y, -x * math.sin(b) + z * math.cos(b)

    def proj(self, p):
        x, y, z = self.rot(p)
        return (self.cx + x * self.s, self.cy + y * self.s), z

    def P(self, p):
        return self.proj(p)[0]

    def depth(self, p):
        return self.rot(p)[2]


def sweep(rig, w, zf, zb, y0, y1, n=2.2, bumps=(), xoff=None, zoff=None, ny=60):
    """outline of a stacked-section body part (torso, skirt, garment) between y0 and y1"""
    hd = Head(w, zf, zb, n=n, bumps=bumps)
    right, left = [], []
    for i in range(ny + 1):
        y = y0 + (y1 - y0) * i / ny
        xo = spline(xoff, y) if xoff else 0.0
        zo = spline(zoff, y) if zoff else 0.0
        br = bl = None
        for j in range(72):
            phi = -math.pi + 2 * math.pi * j / 72
            X, Z = hd.section(y, phi)
            (sx, sy), _ = rig.proj((X + xo, y, Z + zo))
            if br is None or sx > br[0]:
                br = (sx, sy)
            if bl is None or sx < bl[0]:
                bl = (sx, sy)
        right.append(br)
        left.append(bl)
    pts = right + left[::-1]
    return smooth_path([p for i, p in enumerate(pts) if i % 2 == 0])


def section_pt(w, zf, zb, y, x, n=2.2, xoff=None, zoff=None, lift=0.0):
    """front-view x on a sweep at height y -> 3D surface point (for seams, buttons, prints)"""
    hd = Head(w, zf, zb, n=n)
    p = hd.surf(x, y, lift)
    xo = spline(xoff, y) if xoff else 0.0
    zo = spline(zoff, y) if zoff else 0.0
    return (p[0] + xo, p[1], p[2] + zo)


def tube_outline(rig, pts3, radii, caps=(True, True)):
    """a tapered tube through 3D points, seen from the rig: outline points (screen)"""
    p2 = [rig.P(p) for p in pts3]
    r2 = [r * rig.s for r in radii]
    n = len(p2)
    L, R = [], []
    for i in range(n):
        a = p2[max(0, i - 1)]
        b = p2[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        L.append((p2[i][0] + nx * r2[i], p2[i][1] + ny * r2[i]))
        R.append((p2[i][0] - nx * r2[i], p2[i][1] - ny * r2[i]))
    def arc(c, r, nrm, tng):
        return [(c[0] + r * (nrm[0] * math.cos(a) + tng[0] * math.sin(a)), c[1] + r * (nrm[1] * math.cos(a) + tng[1] * math.sin(a)))
                for a in [math.pi * k / 6 for k in range(1, 6)]]
    def dirs(i, j):
        dx, dy = p2[i][0] - p2[j][0], p2[i][1] - p2[j][1]
        l = math.hypot(dx, dy) or 1
        return (dx / l, dy / l)
    out = list(L)
    if caps[1]:
        t = dirs(-1, -2)
        out += arc(p2[-1], r2[-1], (-t[1], t[0]), t)
    out += R[::-1]
    if caps[0]:
        t = dirs(0, 1)
        out += arc(p2[0], r2[0], (-t[1], t[0]), t)
    return out


def tube(cv, rig, pts3, radii, base, shadow, caps=(True, True), size=None, lift=0.12, soft=0.09, rim=None):
    pts = tube_outline(rig, pts3, radii, caps)
    d = smooth_path(pts)
    sz = size or max(radii) * 2 * rig.s
    paint_volume(cv, d, base, shadow, sz, lift=lift, soft=soft, rim=rim)
    return d


def chain(points, m=5):
    """Catmull-Rom densify 3D points"""
    out = []
    n = len(points)
    for i in range(n - 1):
        p0 = points[max(0, i - 1)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(n - 1, i + 2)]
        for j in range(m):
            t = j / m
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[a]) + (-p0[a] + p2[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2 +
                                    (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3) for a in range(3)))
    out.append(points[-1])
    return out


def interp_r(radii, m=5):
    out = []
    for i in range(len(radii) - 1):
        for j in range(m):
            t = j / m
            out.append(radii[i] + (radii[i + 1] - radii[i]) * (t * t * (3 - 2 * t)))
    out.append(radii[-1])
    return out


# ------------------------------------------------------------------ hands

def hand(cv, rig, wrist, down, side, skin, shadow, scale=1.0, curl=0.35, spread=0.15, fat=1.0, pose="relaxed"):
    """a hand hanging from the wrist. down: unit 3D direction of the hand, side: +1 character's left hand.
    Four fingers and a thumb as tubes over a palm."""
    s = scale
    d = norm3(down)
    # palm faces the body (inward): palm normal = -side x
    pn = norm3((-side, 0, 0.15))
    ac = norm3(cross(d, pn))        # across the knuckles
    def at(o, a, b, c=0.0):
        return (o[0] + d[0] * a + ac[0] * b + pn[0] * c, o[1] + d[1] * a + ac[1] * b + pn[1] * c,
                o[2] + d[2] * a + ac[2] * b + pn[2] * c)
    parts = []
    # fingers: offsets across, lengths
    fl = [(-4.6, 10.5), (-1.6, 12.0), (1.5, 11.4), (4.3, 9.0)]
    fr = 1.75 * s * fat
    pz = 1 if rig.depth(at(wrist, 0, 0, 1)) > rig.depth(wrist) else -1
    fingers = []
    for i, (o, L) in enumerate(fl):
        o *= s * fat * (1 + spread * 0.5)
        L *= s
        k0 = at(wrist, 11 * s, o * 0.85)
        bend = curl * (0.8 + 0.1 * i)
        k1 = at(k0, L * 0.42, o * 0.06 * spread * 4, L * 0.12 * bend)
        k2 = at(k1, L * 0.33 * math.cos(bend), o * 0.04 * spread * 4, L * 0.33 * math.sin(bend) * 0.9)
        k3 = at(k2, L * 0.25 * math.cos(bend * 1.6), 0, L * 0.25 * math.sin(bend * 1.6))
        fingers.append(([k0, k1, k2, k3], [fr * 1.08, fr, fr * 0.92, fr * 0.8]))
    # thumb
    t0 = at(wrist, 3 * s, -side * 0 + 4.8 * s * fat, 2.2 * s)
    t1 = at(t0, 4.5 * s, 1.6 * s, 2.6 * s)
    t2 = at(t1, 3.6 * s, 0.6 * s, 2.0 * s * (0.5 + curl))
    t3 = at(t2, 2.8 * s, 0.0, 1.4 * s * (0.5 + curl))
    thumb = ([t0, t1, t2, t3], [fr * 1.45, fr * 1.25, fr * 1.05, fr * 0.9])
    palm = [at(wrist, 0, -3.6 * s * fat), at(wrist, 0, 3.8 * s * fat), at(wrist, 11.5 * s, 6.3 * s * fat),
            at(wrist, 13 * s, 2 * s * fat), at(wrist, 12.5 * s, -2 * s * fat), at(wrist, 11 * s, -6.2 * s * fat)]
    items = []
    for pts, rr in fingers:
        items.append((sum(rig.depth(p) for p in pts) / 4, 'f', pts, rr))
    items.append((sum(rig.depth(p) for p in thumb[0]) / 4 + 1.5 * pz, 'f', thumb[0], thumb[1]))
    palm_z = sum(rig.depth(p) for p in palm) / len(palm)
    items.sort(key=lambda a: a[0])
    # palm first, then fingers by depth; fingers behind the palm drawn before it
    drawn_palm = False
    for z, kind, pts, rr in items:
        if not drawn_palm and z > palm_z:
            d2 = smooth_path([rig.P(p) for p in palm])
            paint_volume(cv, d2, skin, shadow, 14 * s * rig.s, lift=0.12, soft=0.1)
            drawn_palm = True
        tube(cv, rig, chain(pts, 3), interp_r(rr, 3), skin, shadow, size=fr * 2.6 * rig.s, lift=0.14)
    if not drawn_palm:
        d2 = smooth_path([rig.P(p) for p in palm])
        paint_volume(cv, d2, skin, shadow, 14 * s * rig.s, lift=0.12, soft=0.1)


# ------------------------------------------------------------------ shoes

def shoe(cv, rig, ankle, fwd, length, width, height, col, shadow, sole="#f2ede4", sole_h=2.0, toe_up=0.0, rim=None):
    """an ellipsoid-like shoe from the heel to the toe, with a sole band"""
    fx, fz = fwd
    pts = []
    def P3(a, b, h):   # a along foot, b across, h up
        return (ankle[0] + fx * a - fz * b, ankle[1] - h, ankle[2] + fz * a + fx * b)
    # sample the shoe surface and take its hull
    from face import hull
    up = []
    for i in range(15):
        a = -length * 0.22 + length * i / 14
        t = i / 14
        hh = height * (1.0 - 0.55 * t ** 1.3) + (toe_up * t ** 3)
        ww = width * (0.75 + 0.35 * math.sin(math.pi * min(1, t * 1.15)))
        for j in range(9):
            b = -ww + 2 * ww * j / 8
            k = math.sqrt(max(0, 1 - (b / ww) ** 2))
            up.append(rig.P(P3(a, b, hh * k + sole_h)))
            up.append(rig.P(P3(a, b, 0)))
    h = hull(up)
    d = smooth_path(h)
    paint_volume(cv, d, col, shadow, height * 2 * rig.s, lift=0.12, soft=0.1, rim=rim)
    # sole band
    band = []
    for i in range(21):
        t = i / 20
        a = -length * 0.22 + length * t
        ww = width * (0.75 + 0.35 * math.sin(math.pi * min(1, t * 1.15)))
        band.append(rig.P(P3(a, ww if rig.depth(P3(a, ww, 0)) > rig.depth(P3(a, -ww, 0)) else -ww, sole_h)))
    lo = []
    for i in range(21):
        t = 1 - i / 20
        a = -length * 0.22 + length * t
        ww = width * (0.75 + 0.35 * math.sin(math.pi * min(1, t * 1.15)))
        lo.append(rig.P(P3(a, ww if rig.depth(P3(a, ww, 0)) > rig.depth(P3(a, -ww, 0)) else -ww, 0)))
    k = cv.clip(d)
    cv.add(f'<g clip-path="url(#{k})"><path d="{smooth_path(band + lo)}" fill="{sole}"/>'
           f'<path d="{smooth_path(band, closed=False)}" fill="none" stroke="{shadow}" stroke-width="{f(rig.s * 0.8)}" opacity="0.5"/></g>')
    return d


def ground_shadow(cv, cx, cy, rx, ry, a=0.22):
    cv.add(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="#3a2a20" opacity="{a}" '
           f'filter="url(#{cv.blur(ry * 0.5)})"/>')
