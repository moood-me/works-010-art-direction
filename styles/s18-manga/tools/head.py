"""The head: a 3D form made of horizontal cross-sections, features as 3D curves on its surface, drawn by the pen.

Head units: crown to chin is about 1; y down, eye line at y = 0; x to the character's left (screen right in front
view); z towards the viewer. A view is yaw (turn: + turns the face to screen right), pitch (+ bows the head) and roll.
The silhouette is found per level as the extreme points of the turned cross-sections, so the cheek, the brow, the
nose and the chin break the contour exactly where they would in a three-quarter view or a profile."""
import math
from pen import *

# ---------------------------------------------------------------- the form

# y, half-width, front (midline z), back z, z of the widest point, squareness of the front
ADULT = [(-0.50, 0.03, -0.05, -0.13, -0.09, 2.0),
         (-0.47, 0.16, 0.08, -0.28, -0.10, 2.0),
         (-0.40, 0.26, 0.20, -0.38, -0.10, 2.0),
         (-0.30, 0.32, 0.28, -0.44, -0.09, 2.1),
         (-0.18, 0.345, 0.33, -0.46, -0.08, 2.2),
         (-0.08, 0.35, 0.36, -0.455, -0.07, 2.3),
         (0.00, 0.345, 0.33, -0.44, -0.06, 2.1),
         (0.10, 0.315, 0.33, -0.40, -0.05, 2.2),
         (0.20, 0.29, 0.355, -0.33, -0.05, 2.2),
         (0.28, 0.265, 0.37, -0.22, -0.06, 2.1),
         (0.36, 0.24, 0.345, -0.15, -0.08, 2.0),
         (0.42, 0.21, 0.33, -0.10, -0.05, 2.0),
         (0.445, 0.185, 0.32, -0.03, 0.01, 2.0),
         (0.468, 0.145, 0.305, 0.06, 0.10, 2.0),
         (0.49, 0.10, 0.285, 0.14, 0.17, 2.0),
         (0.505, 0.055, 0.258, 0.18, 0.20, 2.0),
         (0.512, 0.015, 0.235, 0.20, 0.21, 2.0)]


def interp_table(tab, y):
    if y <= tab[0][0]:
        return tab[0][1:]
    if y >= tab[-1][0]:
        return tab[-1][1:]
    for i in range(len(tab) - 1):
        a, b = tab[i], tab[i + 1]
        if a[0] <= y <= b[0]:
            # smooth (Catmull-Rom) through the keys
            t = (y - a[0]) / (b[0] - a[0])
            p0 = tab[max(i - 1, 0)]; p3 = tab[min(i + 2, len(tab) - 1)]
            out = []
            for j in range(1, len(a)):
                v0, v1, v2, v3 = p0[j], a[j], b[j], p3[j]
                out.append(0.5 * ((2 * v1) + (-v0 + v2) * t + (2 * v0 - 5 * v1 + 4 * v2 - v3) * t * t
                                  + (-v0 + 3 * v1 - 3 * v2 + v3) * t ** 3))
            return tuple(out)


class Head:
    """p: the character's numbers (see DEFAULT); e: the expression (see EXPR)."""

    def __init__(self, p, e=None):
        self.p = p
        self.e = dict(EXPR['rest']); self.e.update(p.get('rest', {})); self.e.update(e or {})
        self.tab = p['sections']
        self.top = self.tab[0][0]; self.bottom = self.tab[-1][0]
        jaw = self.e.get('jaw', 0) * 0.07
        if jaw:
            tab = []
            for row in self.tab:
                y = row[0]
                k = max(0.0, min(1.0, (y - 0.26) / 0.12))
                tab.append((y + jaw * k,) + row[1:])
            self.tab = tab
            self.bottom = self.tab[-1][0]

    # the cross-section at a level
    def sec(self, y):
        return interp_table(self.tab, y)

    def zsurf(self, x, y):
        """z of the front surface at (x, y) (without the nose)."""
        w, zf, zb, z0, nf = self.sec(y)
        u = min(1.0, abs(x) / max(w, 1e-4))
        return z0 + (zf - z0) * (1 - u ** nf) ** (1 / nf)

    def ring(self, y, n=48, grow=0.0):
        """Points of the cross-section at level y (front half by superellipse, back by ellipse), grown outwards."""
        w, zf, zb, z0, nf = self.sec(y)
        w += grow; zf += grow; zb -= grow
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            c, s = math.cos(a), math.sin(a)
            x = w * math.copysign(abs(c) ** (2 / nf if s > 0 else 1), c)
            if s >= 0:
                z = z0 + (zf - z0) * abs(s) ** (2 / nf)
            else:
                z = z0 + (z0 - zb) * -abs(s)
            pts.append((x, y, z))
        return pts

    def nose_pts(self, y):
        """Extra points of the nose at level y: a narrow wedge on the midline."""
        n = self.p['nose']
        prof = n['profile']          # (y, projection beyond the face, half-width)
        if y < prof[0][0] or y > prof[-1][0]:
            return []
        pr, hw = interp_table(prof, y)
        if pr <= 0.002:
            return []
        out = []
        for i in range(-4, 5):
            t = i / 4
            x = t * hw
            z = self.zsurf(x, y) + pr * (1 - abs(t) ** 1.5)
            out.append((x, y, z))
        return out

    def lips_pts(self, y):
        m = self.p['mouth']
        y0 = m['y'] + self.e.get('jaw', 0) * 0.02
        d = abs(y - y0)
        if d > 0.07:
            return []
        pr = m.get('lip', 0.02) * (1 - (d / 0.07) ** 2)
        out = []
        for i in range(-4, 5):
            t = i / 4
            x = t * m['w'] * 0.9
            out.append((x, y, self.zsurf(x, y) + pr * (1 - t * t)))
        return out


# ---------------------------------------------------------------- the view

class View:
    def __init__(self, yaw=0.0, pitch=0.0, roll=0.0, s=200.0, x=0.0, y=0.0):
        self.yaw, self.pitch, self.roll = math.radians(yaw), math.radians(pitch), math.radians(roll)
        self.s, self.ox, self.oy = s, x, y
        self.cy, self.sy = math.cos(self.yaw), math.sin(self.yaw)
        self.cp, self.sp = math.cos(self.pitch), math.sin(self.pitch)
        self.cr, self.sr = math.cos(self.roll), math.sin(self.roll)

    def rot(self, p):
        x, y, z = p
        X = x * self.cy + z * self.sy
        Z = -x * self.sy + z * self.cy
        Y = y * self.cp + Z * self.sp
        Z2 = -y * self.sp + Z * self.cp
        Xr = X * self.cr - Y * self.sr
        Yr = X * self.sr + Y * self.cr
        return Xr, Yr, Z2

    def __call__(self, p):
        X, Y, Z = self.rot(p)
        return (self.ox + X * self.s, self.oy + Y * self.s)

    def depth(self, p):
        return self.rot(p)[2]

    def facing(self, n):
        """Is a direction n (in head space) turned towards the viewer?"""
        return self.rot(n)[2]

    def many(self, pts):
        return [self(p) for p in pts]


def silhouette(h, v, grow=0.0, y0=None, y1=None, extra=True, levels=70):
    """The outline of the head (or of a shell grown around it) seen in view v: the extreme points of each level
    (measured across the screen after the roll is undone). Returns (right side top→bottom, left side top→bottom)
    as lists of (screen point, head point)."""
    y0 = h.top if y0 is None else y0
    y1 = h.bottom if y1 is None else y1
    R, L = [], []
    for i in range(levels + 1):
        y = y0 + (y1 - y0) * i / levels
        pts = h.ring(y, 56, grow)
        if extra and grow == 0:
            pts = pts + h.nose_pts(y) + h.lips_pts(y)
        best_r = best_l = None
        for p in pts:
            X, Y, Z = v.rot(p)
            # undo the roll to measure across
            Xu = X * v.cr + Y * v.sr
            if best_r is None or Xu > best_r[0]:
                best_r = (Xu, p)
            if best_l is None or Xu < best_l[0]:
                best_l = (Xu, p)
        R.append((v(best_r[1]), best_r[1]))
        L.append((v(best_l[1]), best_l[1]))
    return R, L


def head_outline(h, v, grow=0.0, y0=None, y1=None):
    R, L = silhouette(h, v, grow, y0, y1)
    return [a for a, _ in R] + [a for a, _ in L[::-1]], R, L


# ---------------------------------------------------------------- features

def on(h, x, y, dz=0.0):
    return (x, y, h.zsurf(x, y) + dz)


def eye_curves(h, side):
    """Upper and lower lid curves (3D) of one eye. side +1 is the character's left (screen right in front)."""
    E = h.p['eye']; e = h.e
    ex, ey, ew, eh = E['x'], E['y'], E['w'], E['h']
    tilt = E.get('tilt', 0.0)
    openness = e.get('open', 1.0) * E.get('open', 1.0)
    squint = e.get('squint', 0.0)
    up, lo = [], []
    for i in range(13):
        u = -1 + 2 * i / 12           # -1 inner corner .. +1 outer corner
        x = side * (ex + u * ew)
        bump_up = (1 - u * u) * (1 + E.get('peak', -0.25) * u)
        bump_lo = (1 - u * u) * (1 + E.get('lpeak', 0.2) * u)
        yy = ey - tilt * u * ew
        y_up = yy - eh * openness * bump_up + E.get('droop', 0.0) * max(0, u) ** 2 * eh
        y_lo = yy + eh * 0.55 * bump_lo * (1 - squint * 0.8) - squint * 0.25 * eh * (1 - u * u)
        y_up = min(y_up, y_lo - 0.002) if openness > 0.12 else yy - eh * 0.1 * bump_up
        up.append(on(h, x, y_up, -0.012))
        lo.append(on(h, x, y_lo, -0.012))
    return up, lo


def draw_eye(h, v, side, lw):
    """One eye in the manga way: a heavy upper lid, a short broken lower lid, a dark iris with a highlight,
    a thin crease above."""
    E = h.p['eye']; e = h.e
    up, lo = eye_curves(h, side)
    UP, LO = v.many(up), v.many(lo)
    # how turned away is this eye (for the far eye in three-quarters)
    face_n = v.facing((side * 0.6, 0, 0.8))
    if face_n < 0.05:
        return ''
    out = []
    openness = e.get('open', 1.0) * E.get('open', 1.0)
    ex, ey, ew, eh = E['x'], E['y'], E['w'], E['h']
    if openness > 0.12:
        # the white of the eye is the paper; the iris clipped to the opening
        opening = UP + LO[::-1]
        gx, gy = e.get('look', (0.0, 0.0))
        ix = side * (ex + E.get('iris_dx', 0.0) * side) + gx * ew * 0.45
        iy = ey - eh * 0.15 + gy * eh * 0.5
        ir = E.get('iris', 0.48) * eh * 2 * (1 - 0.15 * e.get('small', 0))
        ring = [on(h, ix + ir * 0.92 * math.cos(a), iy + ir * math.sin(a), -0.004) for a in [2 * math.pi * k / 24 for k in range(24)]]
        RG = v.many(ring)
        inner = fillpath(opening, PAPER, smooth=False)
        cx = sum(p[0] for p in RG) / len(RG); cy = sum(p[1] for p in RG) / len(RG)
        rad = (max(p[0] for p in RG) - min(p[0] for p in RG)) / 2
        style = E.get('iris_style', 'dark')
        if style == 'dark':
            inner += fillpath(RG, INK)
            # the iris is a little lighter round the pupil: a ring of tone under the lid
            inner += f'<circle cx="{f1(cx + rad*0.12)}" cy="{f1(cy + rad*0.18)}" r="{f1(rad*0.55)}" fill="url(#{tone_id(0.72)})"/>'
            inner += f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rad*0.42)}" fill="{INK}"/>'
        else:
            # a light iris: hatched ring and a black pupil
            inner += fillpath(RG, f'url(#{tone_id(0.35)})')
            inner += outline(RG, lw * 0.5, 0.3)
            inner += f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rad*0.45)}" fill="{INK}"/>'
        # highlight towards the light
        if E.get('shine', True):
            inner += f'<circle cx="{f1(cx - rad*0.38)}" cy="{f1(cy - rad*0.38)}" r="{f1(max(1.2, rad*0.22))}" fill="{PAPER}"/>'
        # the lid's shadow on the eyeball
        sh = [UP[i] for i in range(len(UP))] + [(p[0], p[1] + rad * 0.35) for p in UP[::-1]]
        inner += fillpath(sh, f'url(#{tone_id(0.3)})', smooth=False)
        out.append(clip(opening, inner, smooth=False))
    # upper lid: heavy, heavier to the outer corner; the inner end thin
    wl = [lw * 0.4, lw * 0.9, lw * 1.3, lw * 1.5, lw * 1.6, lw * 1.7, lw * 1.6]
    if E.get('lash', 0) > 0:
        wl = [lw * 0.5, lw * 1.0, lw * 1.5, lw * 1.9, lw * 2.2, lw * 2.6, lw * 2.8]
    up_line = UP[1:] if openness > 0.12 else UP
    out.append(stroke(up_line, wl, taper=(0.05, 0.12)))
    if E.get('lash', 0) > 0 and openness > 0.12:
        # a small flick at the outer corner
        a, b = UP[-1], UP[-3]
        dx, dy = a[0] - b[0], a[1] - b[1]
        L = math.hypot(dx, dy) or 1
        out.append(stroke([a, (a[0] + dx / L * lw * 3.2, a[1] + dy / L * lw * 3.2 - lw * 1.4)], [lw * 1.6, lw * 0.4], taper=(0, 0.5)))
    # lower lid: a short thin line under the outer half, broken
    if openness > 0.12:
        n = len(LO)
        out.append(stroke(LO[n // 2 - 1:n - 1], lw * 0.55, taper=(0.4, 0.3)))
        out.append(stroke(LO[2:n // 2 - 2], lw * 0.4, taper=(0.5, 0.5)))
    # crease (double lid) above
    cr = E.get('crease', 0.6)
    if cr > 0:
        cl = [on(h, p[0], p[1] - eh * cr * (0.8 + 0.4 * (1 - abs(-1 + 2 * i / 12))) * max(0.5, openness), -0.01) for i, p in enumerate(up)][3:12]
        out.append(stroke(v.many(cl), lw * 0.45, taper=(0.4, 0.4)))
    # bags under tired / old eyes
    bag = E.get('bag', 0)
    if bag:
        bl = [on(h, p[0], p[1] + eh * (0.55 + 0.35 * bag), -0.005) for p in lo[3:12]]
        out.append(stroke(v.many(bl), lw * 0.4, taper=(0.5, 0.5)))
    # laugh lines: when the cheek pushes the lower lid up
    if e.get('squint', 0) > 0.5:
        x0 = side * (ex + ew * 1.0)
        ll = [on(h, x0, ey + eh * 0.1), on(h, x0 + side * ew * 0.35, ey + eh * 0.5)]
        out.append(stroke(v.many(ll), lw * 0.4, taper=(0.4, 0.5)))
        ll = [on(h, x0 - side * ew * 0.05, ey + eh * 0.55), on(h, x0 + side * ew * 0.2, ey + eh * 1.0)]
        out.append(stroke(v.many(ll), lw * 0.35, taper=(0.4, 0.5)))
    return ''.join(out)


def draw_brow(h, v, side, lw):
    B = h.p['brow']; e = h.e; E = h.p['eye']
    if v.facing((side * 0.6, 0, 0.8)) < 0.0:
        return ''
    raise_in = e.get('brow_in', 0.0); raise_out = e.get('brow_out', 0.0); knit = e.get('knit', 0.0)
    pts = []
    n = 9
    for i in range(n):
        u = i / (n - 1)          # 0 inner .. 1 outer
        x = side * (B['x0'] + (B['x1'] - B['x0']) * u - knit * 0.012 * (1 - u))
        arch = B.get('arch', 0.02) * math.sin(u * math.pi) * (1 + B.get('arch_out', 0.2) * u)
        y = (B['y'] - arch + B.get('slope', 0.0) * u
             - raise_in * 0.035 * (1 - u) ** 1.2 - raise_out * 0.03 * u + knit * 0.02 * (1 - u) ** 2)
        pts.append(on(h, x, y, 0.004))
    P = v.many(pts)
    style = B.get('style', 'stroke')
    th = B.get('th', 1.0)
    if style == 'stroke':
        return stroke(P, [lw * 1.0 * th, lw * 2.2 * th, lw * 2.0 * th, lw * 1.4 * th, lw * 0.6 * th], taper=(0.1, 0.4))
    # bushy: many short strokes along the line (the old man's white brows), outlined
    out = []
    import random
    rnd = random.Random(7 + side)
    for k in range(B.get('hairs', 14)):
        u = k / (B.get('hairs', 14) - 1)
        i = min(int(u * (n - 1)), n - 2)
        a = lerp(P[i], P[i + 1], u * (n - 1) - i)
        L = lw * (6 + 5 * math.sin(u * math.pi)) * B.get('size', 1.0)
        ang = math.radians(-20 if side > 0 else 200) + rnd.uniform(-0.3, 0.3) - side * u * 0.5
        b = (a[0] + math.cos(ang) * L * (1 if side > 0 else 1), a[1] + math.sin(ang) * L * 0.6 + L * 0.35)
        out.append(stroke([a, b], lw * 0.7, taper=(0.2, 0.6), smooth=False))
    return ''.join(out)


def draw_nose(h, v, lw):
    """The nose the way Taniguchi draws it: the bridge only as a line on the shadow side (often only its lower
    part), the wing of the nostril as a curve, the nostril as a dark comma, the tip left open."""
    n = h.p['nose']
    prof = n['profile']
    ytip = n['tip']; ybase = prof[-1][0]
    out = []
    yaw = v.yaw
    sgn = 1 if yaw >= 0 else -1          # the far side is on the left of the screen when the face turns right
    # the midline ridge, in 3D
    ridge = []
    for i in range(11):
        y = prof[0][0] + (ytip - prof[0][0]) * i / 10
        pr, hw = interp_table(prof, y)
        ridge.append((0.0, y, h.zsurf(0, y) + pr))
    # the far side line of the nose: the side wall seen against the cheek
    side_line = []
    for i in range(12):
        y = prof[0][0] + 0.05 + (ytip + 0.02 - prof[0][0] - 0.05) * i / 11
        pr, hw = interp_table(prof, y)
        # the extreme point of the nose wedge across the screen on the far side
        best = None
        for k in range(-8, 9):
            t = k / 8
            x = t * hw
            p = (x, y, h.zsurf(x, y) + pr * (1 - abs(t) ** 1.5))
            X = v.rot(p)[0]
            if best is None or (X * sgn > best[0] * sgn):
                best = (X, p)
        side_line.append(best[1])
    if abs(math.degrees(yaw)) < 8:
        # front: the shadow side line only low down, a light hint up top
        ln = [(-0.035 * n.get('w', 1), y, h.zsurf(-0.035, y) + 0.01) for y in [prof[0][0] + 0.07 + k * (ytip - prof[0][0] - 0.08) / 6 for k in range(7)]]
        out.append(stroke(v.many(ln[3:]), lw * 0.6, taper=(0.5, 0.3)))
    elif abs(math.degrees(yaw)) < 70:
        # three-quarter: the far side wall of the nose: thin up top, firmer to the tip
        P = v.many(side_line)
        k0 = int(len(P) * n.get('bridge_from', 0.35))
        out.append(stroke(P[k0:], [lw * 0.3, lw * 0.8, lw * 1.2], taper=(0.4, 0.15)))
    # tip and wings
    tw = n.get('wing', 0.055)
    yb = ybase - 0.01
    wings = []
    for s in (-1, 1):
        # nostril wing: a curve from the side of the tip round to the cheek
        cx = s * tw
        wing = [on(h, s * tw * 0.55, ytip + 0.035, n['profile'][-2][1] * 0.6 + 0.03),
                on(h, s * tw * 1.05, ytip + 0.01, 0.025),
                on(h, s * tw * 1.15, yb - 0.02, 0.02),
                on(h, s * tw * 0.75, yb + 0.005, 0.02)]
        vis = v.facing((s * 0.7, 0.1, 0.7))
        if vis > -0.25:
            P = v.many(wing)
            far = (s > 0) == (yaw >= 0) and abs(math.degrees(yaw)) >= 8
            wl = lw * (0.8 if far else 1.1)
            if abs(math.degrees(yaw)) > 70 and far:
                continue
            out.append(stroke(P, [wl * 0.5, wl * 1.2, wl * 1.0, wl * 0.4], taper=(0.3, 0.3)))
        # the nostril: a short dark comma under the tip
        nost = [on(h, s * tw * 0.15, yb + 0.004, 0.035), on(h, s * tw * 0.55, yb - 0.004, 0.03)]
        if v.facing((s * 0.3, 0.6, 0.7)) > -0.1 and not (abs(math.degrees(yaw)) > 70 and (s > 0) == (yaw >= 0)):
            out.append(stroke(v.many(nost), [lw * 0.6, lw * 1.6], taper=(0.3, 0.4)))
    # the tip's underside (in three-quarter and profile the line under the tip)
    if abs(math.degrees(yaw)) >= 8:
        tip = [ridge[-1], (0.0, ytip + 0.03, h.zsurf(0, ytip + 0.03) + interp_table(prof, ytip + 0.03)[0] * 0.8)]
        under = [(0, ybase - 0.005, h.zsurf(0, ybase) + 0.02), (sgn * -0.02, yb, h.zsurf(0, ybase) + 0.03)]
        out.append(stroke(v.many([tip[-1]] + under), lw * 0.7, taper=(0.3, 0.4)))
    return ''.join(out)


def mouth_curve(h, part='mid'):
    m = h.p['mouth']; e = h.e
    smile = e.get('smile', 0.0); open_ = e.get('mopen', 0.0); wide = e.get('mwide', 0.0)
    jaw = e.get('jaw', 0.0)
    y0 = m['y'] + jaw * 0.02
    hw = m['w'] * (1 + 0.25 * wide + 0.12 * smile)
    side_skew = e.get('smirk', 0.0)
    pts_up, pts_lo, mid = [], [], []
    for i in range(15):
        u = -1 + 2 * i / 14
        x = u * hw
        corner = smile * 0.035 * u * u - e.get('frown', 0.0) * 0.03 * u * u + side_skew * 0.03 * max(0, u) ** 2 * 1.0 - side_skew * 0.008 * max(0, -u)
        bow = m.get('bow', 0.006) * math.cos(u * math.pi / 2) ** 2
        y_mid = y0 - corner + bow * 0.5
        yo = open_ * 0.075 * (1 - u * u) ** 0.8
        y_up = y_mid - yo * 0.30
        y_lo = y_mid + yo * 0.70 + open_ * 0.004
        mid.append(on(h, x, y_mid, 0.012 * (1 - u * u)))
        pts_up.append(on(h, x, y_up, 0.012 * (1 - u * u)))
        pts_lo.append(on(h, x, y_lo, 0.01 * (1 - u * u)))
    return mid, pts_up, pts_lo


def draw_mouth(h, v, lw):
    m = h.p['mouth']; e = h.e
    mid, up, lo = mouth_curve(h)
    out = []
    open_ = e.get('mopen', 0.0)
    yaw = math.degrees(v.yaw)
    # cut away the part of the mouth behind the cheek in three-quarter
    keep = [v.facing((p[0] * 2.5, 0, 0.9)) > 0.05 for p in mid]
    def vis(L):
        return [v(p) for p, k in zip(L, keep) if k]
    if open_ > 0.08:
        UP, LO = vis(up), vis(lo)
        if len(UP) > 2:
            hole = UP + LO[::-1]
            if m.get('halo'):
                out.append(stroke(hole + [hole[0]], lw * m['halo'], taper=(0, 0), smooth=False, fill=PAPER))
            inner = fillpath(hole, INK, smooth=False)
            # teeth: a white band under the upper lip; the tongue: a light shape low in the mouth
            if e.get('teeth', 1) and open_ > 0.15:
                tb = [v(on(h, p[0] * 0.92, p[1] + 0.012 + 0.006 * (1 - (p[0] / (m['w'] * 1.3)) ** 2), 0.004)) for p, k in zip(up, keep) if k]
                inner += fillpath(UP + tb[::-1], PAPER, smooth=False)
                inner += stroke(tb[1:-1], lw * 0.35, taper=(0.3, 0.3))
            if open_ > 0.3:
                ty = lambda p: p[1] - 0.018 - 0.01 * (1 - (p[0] / (m['w'] * 1.4)) ** 2)
                tg = [v(on(h, p[0] * 0.75, ty(p), 0.0)) for p, k in zip(lo, keep) if k]
                inner += fillpath(tg + LO[::-1][1:-1], f'url(#{tone_id(0.25)})', smooth=False)
                inner += stroke(tg[1:-1], lw * 0.45, taper=(0.3, 0.3))
            out.append(clip(hole, inner, smooth=False))
            out.append(stroke(UP, [lw * 0.6, lw * 1.4, lw * 1.6, lw * 1.4, lw * 0.6], taper=(0.12, 0.12)))
            out.append(stroke(LO, [lw * 0.5, lw * 1.0, lw * 1.2, lw * 1.0, lw * 0.5], taper=(0.15, 0.15)))
    else:
        M = vis(mid)
        if len(M) > 2:
            out.append(stroke(M, [lw * 0.4, lw * 1.2, lw * 1.5, lw * 1.2, lw * 0.4], taper=(0.12, 0.15)))
    # the lower lip: a short line (or a little tone) under the mouth
    ll = m.get('lower', 0.035)
    if ll:
        ylo = (m['y'] + e.get('jaw', 0) * 0.02 + 0.02 + ll + open_ * 0.055)
        lip = [on(h, u * m['w'] * 0.45, ylo + 0.004 * (1 - u * u), 0.008) for u in (-1, -0.4, 0.2, 0.8)]
        if v.facing((0, 0.3, 0.9)) > 0:
            out.append(stroke(v.many(lip), lw * 0.75, taper=(0.4, 0.4)))
    # the upper lip edge for women (a fine line above)
    if m.get('upper_line', 0):
        ul = [on(h, u * m['w'] * 0.7, m['y'] - 0.018 - 0.006 * math.cos(u * 1.4), 0.012) for u in (-0.9, -0.3, 0.3, 0.9)]
        out.append(stroke(v.many(ul), lw * 0.35, taper=(0.4, 0.4)))
    # the dimple of a corner
    if e.get('smile', 0) > 0.3 or e.get('smirk', 0) > 0.3:
        for s in (-1, 1):
            if e.get('smirk', 0) > 0.3 and s < 0:
                continue
            c = mid[-1] if s > 0 else mid[0]
            if v.facing((s * 0.8, 0, 0.6)) > 0:
                d = [on(h, c[0] + s * 0.012, c[1] - 0.012), on(h, c[0] + s * 0.02, c[1] + 0.01)]
                out.append(stroke(v.many(d), lw * 0.5, taper=(0.4, 0.4)))
    return ''.join(out)


def draw_ear(h, v, side, lw, fill=True):
    """An ear: rim, the inner fold, the lobe; in its own plane at the side of the head."""
    E = h.p.get('ear', {})
    yc = E.get('y', 0.08); hh = E.get('h', 0.24); ww = E.get('w', 0.12)
    w, zf, zb, z0, nf = h.sec(yc)
    zc = E.get('z', -0.10)
    x0 = side * (w * 0.97)
    def P(dy, dz, out_=0.0):
        return (x0 + side * (out_ + 0.03 * max(0, -dz / ww)), yc + dy * hh, zc + dz * ww)
    rim = [P(0.45, 0.25), P(0.1, 0.42), P(-0.3, 0.38), P(-0.5, 0.05), P(-0.42, -0.35), P(-0.1, -0.5), P(0.25, -0.38), P(0.5, -0.18), P(0.55, 0.05)]
    inner = [P(-0.25, 0.1), P(-0.32, -0.12), P(-0.1, -0.28), P(0.18, -0.2), P(0.25, 0.0)]
    R = v.many(rim)
    out = ''
    if fill:
        out += fillpath(R + [v(P(0.4, 0.3))], PAPER)
    out += stroke(R, [lw * 0.6, lw * 1.2, lw * 1.4, lw * 1.2, lw * 1.0, lw * 1.4, lw * 1.2, lw * 0.6], taper=(0.1, 0.15))
    if v.facing((side, 0, 0)) > 0.2:
        out += stroke(v.many(inner), lw * 0.6, taper=(0.3, 0.3))
        out += stroke(v.many([P(0.05, 0.2), P(0.18, 0.1)]), lw * 0.8, taper=(0.3, 0.3))
    return out


# ---------------------------------------------------------------- neck, shading, the whole head

def neck_rings(h, v, top=0.12, bottom=0.95):
    N = h.p.get('neck', {})
    rx, rz, zc = N.get('rx', 0.15), N.get('rz', 0.17), N.get('z', -0.08)
    lean = N.get('lean', 0.05)      # the neck leans forward: its base is behind
    R, L = [], []
    for i in range(16):
        y = top + (bottom - top) * i / 15
        k = (y - top) / (bottom - top)
        z = zc - lean * k
        widen = 1 + N.get('flare', 0.25) * k ** 2.5
        best_r = best_l = None
        for a in range(24):
            t = 2 * math.pi * a / 24
            p = (rx * widen * math.cos(t), y, z + rz * widen * math.sin(t))
            X = v.rot(p)[0]
            if best_r is None or X > best_r[0]:
                best_r = (X, p)
            if best_l is None or X < best_l[0]:
                best_l = (X, p)
        R.append(v(best_r[1])); L.append(v(best_l[1]))
    return R, L


def jaw_curve(h):
    """The lower edge of the jaw in 3D, from the left ear lobe round the chin to the right one."""
    J = h.p.get('jaw', {})
    w = lambda y: h.sec(y)[0]
    E = h.p.get('ear', {})
    yl = E.get('y', 0.08) + E.get('h', 0.24) * 0.45
    ya = J.get('angle_y', 0.41); za = J.get('angle_z', -0.10)
    yb = h.bottom
    side = lambda s: [(s * w(yl) * 0.96, yl, E.get('z', -0.10)), (s * w(ya) * 1.0, ya, za),
                      (s * w(yb - 0.035) * 1.0, yb - 0.03, 0.10), (s * w(yb - 0.012) * 0.6, yb - 0.004, h.sec(yb)[1] - 0.05)]
    chin = [(0, yb + 0.004, h.sec(yb)[1] - 0.03)]
    return side(-1) + chin + side(1)[::-1]


def jaw_region(h, v):
    """The region under and behind the jaw, where the neck is in front of the head's lower outline."""
    J = jaw_curve(h)
    P = [(x, y + 0.012 * v.s) for x, y in v.many(J)]
    far = 3.0 * v.s
    yaw = math.degrees(v.yaw)
    if abs(yaw) < 12:
        a, b = P[0], P[-1]
        return [(a[0] - far, a[1]), *P, (b[0] + far, b[1]), (b[0] + far, b[1] + far), (a[0] - far, a[1] + far)]
    n = len(J) // 2
    near = P[:n + 1] if yaw > 0 else P[n:][::-1]      # lobe -> chin on the near side
    d = 1 if yaw > 0 else -1
    lobe, chin = near[0], near[-1]
    return [(lobe[0] - d * far, lobe[1]), *near, (chin[0] + d * far, chin[1]), (chin[0] + d * far, chin[1] + far), (lobe[0] - d * far, lobe[1] + far)]


def jaw_line(h, v, lw):
    """In three-quarter and profile the underside of the jaw is drawn where the neck stands in front of it."""
    yaw = math.degrees(v.yaw)
    if abs(yaw) < 12:
        return ''
    J = jaw_curve(h)
    n = len(J) // 2
    near = J[1:n + 1] if yaw > 0 else J[n:-1][::-1]
    return stroke(v.many(near), [lw * 0.5, lw * 1.2, lw * 1.0], taper=(0.3, 0.1))


LIGHT3 = (-0.45, -0.55, 0.70)     # in view space: from the upper left and in front


def shade_tone(h, v, outline_pts, thresh=-0.02, level=0.16, extra_dark=None):
    """Form shadow as flat tone with a crisp edge, where the face turns from the light."""
    L = LIGHT3
    n = math.sqrt(sum(c * c for c in L)); L = tuple(c / n for c in L)
    cell = PITCH * 0.9
    grid = {}
    for i in range(70):
        y = h.top + 0.02 + (h.bottom - h.top - 0.03) * i / 69
        w, zf, zb, z0, nf = h.sec(y)
        for j in range(-34, 35):
            x = w * j / 34.5
            z = h.zsurf(x, y)
            dx = (h.zsurf(x + 0.005, y) - h.zsurf(x - 0.005, y)) / 0.01
            dy = (h.zsurf(x, y + 0.005) - h.zsurf(x, y - 0.005)) / 0.01
            N = (-dx, -dy, 1.0)
            nn = math.sqrt(sum(c * c for c in N)); N = tuple(c / nn for c in N)
            Nv = v.rot(N)
            if Nv[2] < 0:
                continue
            d = sum(a * b for a, b in zip(Nv, L))
            X, Y = v((x, y, z))
            grid[(int(X // cell), int(Y // cell))] = min(d, grid.get((int(X // cell), int(Y // cell)), 9))
    xs = [p[0] for p in outline_pts]; ys = [p[1] for p in outline_pts]
    box = (min(xs), min(ys), max(xs), max(ys))
    def cov(X, Y):
        d = grid.get((int(X // cell), int(Y // cell)))
        if d is None:
            # outside the sampled face (the far edge): shade if the neighbours do
            for dd in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                d = grid.get((int(X // cell) + dd[0], int(Y // cell) + dd[1]))
                if d is not None:
                    break
        if d is None:
            return 0
        return level if d < thresh else 0
    return gtone(box, cov, outline_pts, smooth=False)


def draw_head(h, v, lw=2.0, hair=None, shade=True, neck=True, extras=None):
    """The whole head. hair: an object with .back(h, v, lw) and .front(h, v, lw) (see hair.py).
    extras: functions (h, v, lw) -> svg drawn over the face (glasses, beard, wrinkles)."""
    out = []
    yaw = math.degrees(v.yaw)
    if hair:
        out.append(hair.back(h, v, lw))
    contour, R, L = head_outline(h, v)
    if neck:
        NR, NL = neck_rings(h, v)
        npoly = NR + NL[::-1]
        out.append(fillpath(npoly, PAPER, smooth=False))
        neck_lines = stroke(NR[2:], [lw * 1.2, lw * 0.9, lw * 0.5], taper=(0.1, 0.3)) + stroke(NL[2:], [lw * 1.0, lw * 0.8, lw * 0.4], taper=(0.1, 0.3))
        out.append(neck_lines)
    # ears: the far one behind the head, both behind in front view (they stand out from it)
    near_side = -1 if yaw > 0 else 1
    if abs(yaw) < 12:
        out.append(draw_ear(h, v, 1, lw) + draw_ear(h, v, -1, lw))
    elif abs(yaw) < 60:
        out.append(draw_ear(h, v, -near_side, lw))
    out.append(fillpath(contour, PAPER, smooth=False))
    out.append(outline(contour, lw * 1.25, 0.6))
    if neck:
        jr = jaw_region(h, v)
        patch = fillpath(npoly, PAPER, smooth=False) + neck_lines
        out.append(clip(jr, patch, smooth=False))
        # the jaw's cast shadow on the neck
        J = v.many(jaw_curve(h))
        cx = sum(p[0] for p in J) / len(J)
        lower = [(cx + (x - cx) * 0.8, y + 0.13 * v.s) for x, y in J[::-1]]
        under = clip(npoly, tone(J + lower, 0.3), smooth=False)
        out.append(clip(jr, under, smooth=False))
        out.append(jaw_line(h, v, lw))
    if abs(yaw) >= 12:
        out.append(draw_ear(h, v, near_side, lw))
    if shade:
        out.append(shade_tone(h, v, contour, **h.p.get('shade', {})))
    for f in (h.p.get('under') or []):
        out.append(f(h, v, lw))
    for side in (-1, 1):
        out.append(draw_eye(h, v, side, lw))
        out.append(draw_brow(h, v, side, lw))
    out.append(draw_nose(h, v, lw))
    out.append(draw_mouth(h, v, lw))
    for f in (h.p.get('marks') or []):
        out.append(f(h, v, lw))
    for f in (extras or []):
        out.append(f(h, v, lw))
    if hair:
        out.append(hair.front(h, v, lw))
    return ''.join(out)


# ---------------------------------------------------------------- expressions

EXPR = {
    'rest': dict(open=1.0, squint=0.0, brow_in=0.0, brow_out=0.0, knit=0.0, smile=0.0, mopen=0.0, mwide=0.0,
                 frown=0.0, jaw=0.0, smirk=0.0, look=(0.0, 0.0)),
    'joy': dict(open=0.75, squint=0.6, brow_in=0.3, brow_out=0.2, smile=1.0, mopen=0.35, mwide=0.2, jaw=0.2),
    'surprise': dict(open=1.25, brow_in=1.0, brow_out=1.0, mopen=0.45, mwide=-0.3, jaw=0.5, small=1),
    'sadness': dict(open=0.75, brow_in=1.0, brow_out=-0.5, frown=0.6, look=(0.0, 0.5), knit=0.3),
    'anger': dict(open=0.9, squint=0.3, brow_in=-0.9, knit=1.0, frown=0.5, mopen=0.18, mwide=0.2, jaw=0.1),
}
