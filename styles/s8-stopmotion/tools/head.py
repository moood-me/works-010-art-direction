"""A puppet head as a real (simple) 3D object, so the same head turns (front, three-quarter, profile) and changes
expression like a replacement-face puppet.

The head is a loft: horizontal elliptic slices from crown to chin, each with a half-width a(y), a half-depth b(y) and a
forward shift c(y) (the face and jaw sit forward of the skull). Units: head height = 1, y from -0.5 (crown) to
+0.5 (chin), x right, z toward the viewer. The head turns by `yaw` (degrees; + turns the face to the viewer's right)
and leans by `roll` (degrees, in the picture plane).

Features are placed on the surface by (phi, y): phi is the angle round the slice (0 = middle of the face), and are
drawn as flat shapes laid on the surface (scaled across by how much the surface faces us). The nose and the hair are
lofts / ribbons of their own.
"""
import math
from sculpt import pts, poly, f, mix


def interp(table, y):
    """Catmull-Rom through [(y, v), ...] sorted by y."""
    if y <= table[0][0]:
        return table[0][1]
    if y >= table[-1][0]:
        return table[-1][1]
    for i in range(len(table) - 1):
        if table[i][0] <= y <= table[i + 1][0]:
            break
    y0, v0 = table[max(0, i - 1)]
    y1, v1 = table[i]
    y2, v2 = table[i + 1]
    y3, v3 = table[min(len(table) - 1, i + 2)]
    t = (y - y1) / (y2 - y1)
    m1 = (v2 - v0) / (y2 - y0) * (y2 - y1) if y2 != y0 else 0
    m2 = (v3 - v1) / (y3 - y1) * (y2 - y1) if y3 != y1 else 0
    t2, t3 = t * t, t * t * t
    return (2 * t3 - 3 * t2 + 1) * v1 + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * v2 + (t3 - t2) * m2


class Head:
    """shape: dict with tables 'a', 'b', 'c' as [(y, value)], all in head-height units."""

    def __init__(self, shape, S, cx, cy, yaw=0.0, roll=0.0):
        self.sh = shape
        self.S, self.cx, self.cy = S, cx, cy
        self.yaw, self.roll = math.radians(yaw), math.radians(roll)
        self.cy_, self.sy_ = math.cos(self.yaw), math.sin(self.yaw)
        self.cr, self.sr = math.cos(self.roll), math.sin(self.roll)

    # --- geometry in head units ---
    def a(self, y):
        return max(0.0, interp(self.sh['a'], y))

    def b(self, y):
        if 'front' in self.sh:
            return max(0.0, (interp(self.sh['front'], y) - interp(self.sh['back'], y)) / 2)
        return max(0.0, interp(self.sh['b'], y))

    def c(self, y):
        if 'front' in self.sh:
            return (interp(self.sh['front'], y) + interp(self.sh['back'], y)) / 2
        return interp(self.sh['c'], y)

    def surf(self, phi, y, out=0.0, k=1.0):
        """3D point on the surface (scaled by k about the slice centre, pushed out along the normal by `out`)."""
        a, b, c = self.a(y) * k, self.b(y) * k, self.c(y)
        X, Z = a * math.sin(phi), c + b * math.cos(phi)
        nx, nz = math.sin(phi) / max(a, 1e-3), math.cos(phi) / max(b, 1e-3)
        n = math.hypot(nx, nz)
        return (X + out * nx / n, y, Z + out * nz / n)

    def normal(self, phi, y):
        a, b = max(self.a(y), 1e-3), max(self.b(y), 1e-3)
        nx, nz = math.sin(phi) / a, math.cos(phi) / b
        n = math.hypot(nx, nz)
        return (nx / n, 0.0, nz / n)

    # --- projection ---
    def rot(self, p):
        X, Y, Z = p
        return (X * self.cy_ + Z * self.sy_, Y, -X * self.sy_ + Z * self.cy_)

    def scr(self, p):
        """head-unit 3D point → screen (x, y, depth)."""
        x, y, z = self.rot(p)
        x, y = x * self.S, y * self.S
        return (self.cx + x * self.cr - y * self.sr, self.cy + x * self.sr + y * self.cr, z)

    def P(self, p):
        x, y, _ = self.scr(p)
        return (x, y)

    def facing(self, phi, y=0.0):
        return self.rot(self.normal(phi, y))[2]

    def frame(self, phi, y, out=0.0):
        """Screen affine for a flat feature laid on the surface at (phi, y): returns an SVG transform string.
        Local units: 1 = head height; local x runs round the surface, local y down."""
        p = self.surf(phi, y, out)
        x0, y0, _ = self.scr(p)
        d = 0.002
        x1, y1, _ = self.scr(self.surf(phi + d / max(self.a(y), 0.05), y, out))
        tx, ty = (x1 - x0) / d, (y1 - y0) / d     # screen motion per unit of arc
        # vertical axis: straight down (with roll)
        vx, vy = -self.sr * self.S, self.cr * self.S
        return f'matrix({f(tx/1)},{f(ty)},{f(vx)},{f(vy)},{f(x0)},{f(y0)})', (tx, ty)

    def outline(self, k=1.0, y0=-0.5, y1=0.5, n=60, extra=0.0):
        """Silhouette of the loft (scaled by k) between y0 and y1."""
        left, right = [], []
        for i in range(n + 1):
            y = y0 + (y1 - y0) * i / n
            a, b, c = self.a(y) * k + extra, self.b(y) * k + extra, self.c(y)
            # extreme x of the rotated ellipse X = a sin t, Z = c + b cos t:  x = X cy + Z sy
            ang = math.atan2(a * self.cy_, b * self.sy_)
            xs = []
            for t in (ang, ang + math.pi):
                X, Z = a * math.sin(t), c + b * math.cos(t)
                xs.append((X, Z))
            pr = [self.scr((X, y, Z)) for X, Z in xs]
            pr.sort(key=lambda q: q[0] * self.cr + q[1] * self.sr)
            left.append(pr[0][:2])
            right.append(pr[1][:2])
        return left + right[::-1]


# ------------------------------------------------------------------ features

def eye(h, d, side, P, ex, skin, out):
    """One eye: a glossy eyeball sunk in the head, lids of skin over it, a painted iris with a dark ring and a sharp
    highlight, the lash line as the lid's dark edge.
    P: character face params; ex: expression params; side: -1 (character's right = viewer's left) or +1."""
    phi = side * P['eye_phi']
    ye = P['eye_y']
    if h.facing(phi, ye) < -0.05:
        return
    S = h.S
    R = P['eye_r']                       # eyeball radius (head units)
    # eyeball centre: a bit inside the surface
    cpt = h.surf(phi, ye, -R * 0.55)
    ecx, ecy, _ = h.scr(cpt)
    tr, (tx, ty) = h.frame(phi, ye, 0.0)
    w = P['eye_w']                       # half width of the opening (local units)
    op = ex.get('open', 1.0) * P['eye_open']
    up = ex.get('lid_up', 0.0)            # upper lid raise (+) / lower (-)
    lo = ex.get('lid_lo', 0.0)            # lower lid push up (+)
    tilt = P.get('eye_tilt', 0.0) * 1.0   # outer corner up (+)
    inn, outer = (-w, w) if side > 0 else (w, -w)   # local x of inner and outer corners
    # local coordinates: x across, y down; inner corner lower than outer when tilt>0
    ci = (inn, 0.004 * (1 if tilt >= 0 else -1) * abs(tilt) * 10)
    co = (outer, -tilt)
    top_h = R * 1.05 * op * (1 + up)
    bot_h = R * 0.62 * op * (1 - lo)
    # opening polygon: upper arc (peak toward the inner third), lower arc
    up_pts, lo_pts = [], []
    N = 14
    for i in range(N + 1):
        t = i / N
        x = ci[0] + (co[0] - ci[0]) * t
        yb = ci[1] + (co[1] - ci[1]) * t
        s = math.sin(math.pi * t) ** 0.8
        peak = 1 + 0.18 * math.sin(math.pi * (t - 0.15))     # fuller toward the inner side
        up_pts.append((x, yb - top_h * s * peak * 0.95))
        lo_pts.append((x, yb + bot_h * math.sin(math.pi * t) ** 1.1))
    shape = up_pts + lo_pts[::-1][1:-1]
    cid = h_id = d.uid('eye')
    d.defs.append(f'<clipPath id="{cid}"><path d="{poly(shape)}" transform="{tr}"/></clipPath>')
    # socket shadow around the eye
    sock = []
    for i in range(N + 1):
        t = i / N
        x = ci[0] * 1.35 + (co[0] * 1.3 - ci[0] * 1.35) * t
        sock.append((x, -top_h * 1.7 * math.sin(math.pi * t) - 0.004))
    for i in range(N, -1, -1):
        t = i / N
        x = ci[0] * 1.35 + (co[0] * 1.3 - ci[0] * 1.35) * t
        sock.append((x, bot_h * 1.6 * math.sin(math.pi * t) + 0.006))
    bl = d.blur(max(1.5, S * 0.012))
    out.append(f'<g filter="url(#{bl})" opacity="0.55"><path d="{pts(sock)}" transform="{tr}" fill="{mix(skin, P.get("socket", "#7a4050"), 0.55)}"/></g>')
    # eyeball
    white = P.get('white', '#efe6dc')
    g = d.rad([(0, mix(white, '#ffffff', 0.4), 1), (0.65, white, 1), (1, mix(white, '#8a6a70', 0.55), 1)], fx=0.38, fy=0.3)
    ball = f'<circle cx="{f(ecx)}" cy="{f(ecy)}" r="{f(R*S*1.05)}" fill="url(#{g})"/>'
    # iris: on the ball toward the gaze
    gx, gy = ex.get('gaze', P.get('gaze', (0.0, 0.0)))
    gv = (math.sin(gx) * math.cos(gy), math.sin(gy), math.cos(gx) * math.cos(gy))
    # gaze in head space; place iris centre on the eyeball surface
    ip = (cpt[0] + gv[0] * R, cpt[1] + gv[1] * R, cpt[2] + gv[2] * R)
    icx, icy, _ = h.scr(ip)
    gr = h.rot(gv)
    foreshort = max(0.25, gr[2])
    ir = P['iris_r'] * S
    ang = math.degrees(math.atan2(gr[1], gr[0])) if abs(gr[0]) + abs(gr[1]) > 1e-4 else 0
    iris_c = P['iris']
    ig = d.rad([(0, mix(iris_c, '#000000', 0.55), 1), (0.32, mix(iris_c, '#000000', 0.3), 1), (0.55, iris_c, 1),
                (0.85, mix(iris_c, '#ffffff', 0.12), 1), (0.93, mix(iris_c, '#000000', 0.55), 1), (1, mix(iris_c, '#000000', 0.7), 1)])
    pupil = ex.get('pupil', 0.38)
    iris = (f'<g transform="translate({f(icx)},{f(icy)}) rotate({f(ang)}) scale({f(foreshort)},1)">'
            f'<circle r="{f(ir)}" fill="url(#{ig})"/>'
            f'<circle r="{f(ir*pupil)}" fill="#120c0c"/></g>')
    # lid shadow on the ball (the lid has thickness)
    lidsh = []
    for (x, y) in up_pts:
        lidsh.append((x, y))
    for (x, y) in up_pts[::-1]:
        lidsh.append((x, y + R * 0.55))
    bl2 = d.blur(max(1.2, S * 0.008))
    shade = f'<g filter="url(#{bl2})" opacity="0.55"><path d="{pts(lidsh)}" transform="{tr}" fill="#3a1e24"/></g>'
    # glints: a sharp window of the key light (upper left) and a faint fill
    hx, hy = icx - ir * 0.42 * 1, icy - ir * 0.45
    glint = (f'<ellipse cx="{f(hx)}" cy="{f(hy)}" rx="{f(ir*0.26)}" ry="{f(ir*0.2)}" fill="#ffffff" opacity="0.95" transform="rotate(-30 {f(hx)} {f(hy)})"/>'
             f'<circle cx="{f(icx+ir*0.4)}" cy="{f(icy+ir*0.42)}" r="{f(ir*0.09)}" fill="#ffffff" opacity="0.45"/>')
    out.append(f'<g clip-path="url(#{cid})">{ball}{iris}{shade}{glint}</g>')
    # upper lid: a thin crescent of skin above the opening + a lash line along the edge
    lid = up_pts + [(x, y - R * 0.38 * op - 0.004) for (x, y) in up_pts[::-1]]
    out.append(d.bump(pts(lid), mix(skin, '#c07a70', 0.18), soft=max(1.2, S*0.006), height=max(2, S*0.02), spec=0.35,
                      tr=tr))
    lash = P.get('lash', '#24161a')
    lw = P.get('lash_w', 0.010)
    lash_pts = up_pts[:]
    # wing past the outer corner
    ox, oy = co
    wing = (ox + (0.018 if side > 0 else -0.018) * P.get('wing', 1.0), oy - 0.012 * P.get('wing', 1.0))
    lpath = pts(lash_pts + [wing], close=False)
    out.append(f'<path d="{lpath}" transform="{tr}" fill="none" stroke="{lash}" stroke-width="{f(lw)}" '
               f'stroke-linecap="round" stroke-linejoin="round" vector-effect="none"/>')
    # lower lid: a soft ledge
    ll = lo_pts + [(x, y + R * 0.22) for (x, y) in lo_pts[::-1]]
    out.append(d.bump(pts(ll), mix(skin, '#b06a68', 0.12), soft=max(1, S*0.005), height=max(1.5, S*0.012), spec=0.25,
                      tr=tr))
    lowline = pts(lo_pts[2:-2], close=False)
    out.append(f'<path d="{lowline}" transform="{tr}" fill="none" stroke="{mix(lash, skin, 0.55)}" stroke-width="{f(lw*0.35)}" opacity="0.7"/>')
    # crease of the upper lid
    if P.get('crease', True):
        cr = [(x * 0.95, y - R * (0.55 + 0.35 * up) * op - 0.012) for (x, y) in up_pts[2:-1]]
        out.append(f'<path d="{pts(cr, close=False)}" transform="{tr}" fill="none" stroke="{mix(skin, "#5a2a30", 0.45)}" '
                   f'stroke-width="{f(lw*0.4)}" opacity="0.6" stroke-linecap="round"/>')
    # bags under the eyes (age, tiredness)
    for k in range(P.get('bags', 0)):
        bg_ = [(x * (1.0 - 0.1 * k), y + R * (0.55 + 0.38 * k)) for (x, y) in lo_pts[2:-1]]
        out.append(d.groove(pts(bg_, close=False), skin, 0.008, soft=max(1, round(S * 0.004, 1)), depth=-3,
                            tr=tr))


def brow(h, d, side, P, ex, out):
    phi = side * P['eye_phi']
    yb = P['eye_y'] - P['brow_gap']
    if h.facing(phi, yb) < -0.1:
        return
    tr, _ = h.frame(phi, yb, 0.004)
    w = P['brow_w']
    lift_in = ex.get('brow_in', 0.0)     # + = inner end up (sad/surprised), - = down (angry)
    lift_out = ex.get('brow_out', 0.0)
    th = P['brow_th']
    inner_x, outer_x = (-w * 0.95, w * 1.1) if side > 0 else (w * 0.95, -w * 1.1)
    arch = P.get('brow_arch', 0.012)
    n = 9
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        x = inner_x + (outer_x - inner_x) * t
        y = -lift_in * (1 - t) - lift_out * t - arch * math.sin(math.pi * min(1, t * 1.2)) + 0.004 * t
        thick = th * (1.0 - 0.75 * t ** 1.3) * (0.8 + 0.2 * math.sin(math.pi * min(1, t * 2)))
        top.append((x, y - thick * 0.6))
        bot.append((x, y + thick * 0.4))
    shape = top + bot[::-1]
    col = P['brow_col']
    out.append(d.bump(pts(shape), col, soft=max(1, h.S * 0.006), height=max(2, h.S * 0.03), spec=0.3, shine=14,
                      tr=tr))


def nose(h, d, P, out):
    """The nose as a small loft of its own: slices from the root to the tip, pushed forward of the face."""
    y0, y1 = P['nose_root'], P['nose_tip']
    L = P['nose_len']            # how far the tip stands out (head units)
    W = P['nose_w']              # half width at the tip
    hook = P.get('nose_hook', 0.0)
    up = P.get('nose_up', 0.0)   # tip turned up
    slices = []
    n = 16
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        prot = L * (t ** 1.15) * (1 + hook * math.sin(math.pi * t))
        wid = W * (0.42 + 0.58 * t ** 1.6)
        if t > 0.82:      # round the end
            k = (t - 0.82) / 0.18
            wid *= math.sqrt(max(0.0, 1 - 0.55 * k * k))
        base = h.surf(0, y)
        slices.append((y - up * t ** 3 * 0.5, base[2] + prot, wid))
    # tip ball and under side
    yt, zt, wt = slices[-1]
    left, right = [], []
    for (y, zc, wid) in slices:
        for sgn, lst in ((-1, left), (1, right)):
            # extreme of ellipse X = wid sin t, Z = zc - wid*0.9 + wid*0.9 cos t
            a, b = wid, wid * 0.9
            ang = math.atan2(a * h.cy_, b * h.sy_)
            cands = []
            for tt in (ang, ang + math.pi):
                X, Z = a * math.sin(tt), zc - b + b * math.cos(tt)
                cands.append(h.scr((X, y, Z)))
            cands.sort(key=lambda q: q[0] * h.cr + q[1] * h.sr)
            lst.append(cands[0 if sgn < 0 else 1][:2])
    # round bottom: a half ellipse under the tip
    bot = []
    for i in range(1, 10):
        tt = math.pi * i / 10
        a, b = wt, wt * 0.9
        ang = math.atan2(a * h.cy_, b * h.sy_)
        X = a * math.sin(ang + tt)
        Z = zt - b + b * math.cos(ang + tt)
        bot.append(h.scr((X, yt + wt * 0.55 * math.sin(tt), Z))[:2])
    outline = left + bot[::-1] + right[::-1] if False else left + right[::-1]
    outline = left + _arc_under(h, slices[-1]) + right[::-1]
    skin = P['skin']
    S = h.S
    # cast shadow of the nose on the face (light from upper left → shadow to lower right)
    sh = [(x + S * 0.03, y + S * 0.035) for (x, y) in outline]
    bl = d.blur(max(1.5, S * 0.01))
    out.append(f'<path d="{pts(sh)}" fill="#4a1e22" opacity="0.32" filter="url(#{bl})"/>')
    col = mix(skin, P.get('nose_tint', '#e07a6a'), 0.12)
    out.append(d.bump(pts(outline), col, soft=max(2, S * 0.022), height=max(4, S * 0.07), spec=0.45, shine=24))
    # nostrils: two small dark shapes under the tip, seen when facing
    for side in (-1, 1):
        X = side * wt * 0.55
        p = h.scr((X, yt + wt * 0.38, zt - wt * 0.55))
        vis = h.rot((side * 0.5, 0.6, 0.6))[2]
        if vis > 0:
            out.append(f'<ellipse cx="{f(p[0])}" cy="{f(p[1])}" rx="{f(S*wt*0.28*max(0.35, abs(h.cy_)))}" ry="{f(S*wt*0.13)}" '
                       f'fill="#3a1416" opacity="0.75" transform="rotate({f(math.degrees(h.roll)+side*12)} {f(p[0])} {f(p[1])})"/>')
    # alae (wings)
    for side in (-1, 1):
        X = side * wt * 0.95
        p = h.scr((X, yt + wt * 0.1, zt - wt * 1.0))
        if h.rot((side, 0, 0.4))[2] > -0.3:
            out.append(d.bump(f'M{f(p[0]-S*wt*0.5)} {f(p[1])} a{f(S*wt*0.5)} {f(S*wt*0.42)} 0 1 0 {f(S*wt)} 0 '
                              f'a{f(S*wt*0.5)} {f(S*wt*0.42)} 0 1 0 {f(-S*wt)} 0Z', col, soft=max(1.5, S*0.01), height=max(2, S*0.03), spec=0.2))
    # tip highlight
    tp = h.scr((-wt * 0.25, yt - wt * 0.35, zt - wt * 0.1))
    out.append(f'<ellipse cx="{f(tp[0])}" cy="{f(tp[1])}" rx="{f(S*wt*0.28)}" ry="{f(S*wt*0.2)}" fill="#fff6ee" opacity="0.35" filter="url(#{d.blur(max(1, S*0.004))})"/>')


def _arc_under(h, sl):
    y, zc, wid = sl
    pts_ = []
    a, b = wid, wid * 0.9
    ang = math.atan2(a * h.cy_, b * h.sy_)
    # go from the left extreme to the right extreme under the tip, bulging down
    p0 = None
    for i in range(1, 12):
        t = i / 12
        tt = ang + math.pi + (ang - (ang + math.pi)) * t   # sweep the front half
        X, Z = a * math.sin(tt), zc - b + b * math.cos(tt)
        p = h.scr((X, y + wid * 0.5 * math.sin(math.pi * t), Z))
        pts_.append(p[:2])
    return pts_


def mouth(h, d, P, ex, out):
    ym = P['mouth_y']
    tr, (tx, ty) = h.frame(0, ym, 0.004)
    S = h.S
    w = P['mouth_w'] * ex.get('wide', 1.0)
    smile = ex.get('smile', 0.0)      # corners up (+) / down (-)
    opn = ex.get('open', 0.0) if 'mopen' not in ex else ex['mopen']
    opn = ex.get('mopen', 0.0)
    skew = ex.get('skew', 0.0)         # one corner higher (smirk)
    lip = P['lip']
    ul = P.get('upper_lip', 0.010)
    ll = P.get('lower_lip', 0.016)
    n = 12
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        x = -w + 2 * w * t
        corner = (smile + skew * (t - 0.5) * 2) * abs(2 * t - 1) ** 1.6
        cupid = -0.004 * math.cos(math.pi * (t - 0.5) * 6) * (1 - abs(2 * t - 1)) if P.get('cupid', True) else 0
        y = -corner * 0.035 + smile * 0.01 * (1 - abs(2 * t - 1))
        top.append((x, y - opn * 0.03 * math.sin(math.pi * t) ** 0.7 + cupid * 0))
        bot.append((x, y + opn * 0.06 * math.sin(math.pi * t) ** 0.8 + smile * 0.012 * math.sin(math.pi * t)))
    # cavity (when open)
    if opn > 0.02:
        cav = top + bot[::-1]
        cid = d.uid('m')
        d.defs.append(f'<clipPath id="{cid}"><path d="{pts(cav)}" transform="{tr}"/></clipPath>')
        g = f'<path d="{pts(cav)}" transform="{tr}" fill="#3a1418"/>'
        teeth = ''
        if ex.get('teeth', True):
            tt_ = [(x * 0.85, y - 0.002) for (x, y) in top] + [(x * 0.85, y + 0.022) for (x, y) in top[::-1]]
            teeth = f'<path d="{pts(tt_)}" transform="{tr}" fill="#f1e8dc"/>'
            if ex.get('lower_teeth'):
                lt = [(x * 0.75, y - 0.016) for (x, y) in bot] + [(x * 0.75, y + 0.01) for (x, y) in bot[::-1]]
                teeth += f'<path d="{pts(lt)}" transform="{tr}" fill="#e6dccf"/>'
        tongue = f'<ellipse cx="0" cy="{f(max(b[1] for b in bot)*0.7)}" rx="{f(w*0.55)}" ry="{f(opn*0.03)}" transform="{tr}" fill="#a8444a"/>'
        out.append(f'<g clip-path="url(#{cid})">{g}{tongue}{teeth}</g>')
    # upper lip: band above the line
    U = [(x, y - ul * math.sin(math.pi * (i / n)) ** 0.5 - 0.002) for i, (x, y) in enumerate(top)] + top[::-1]
    out.append(d.bump(pts(U), mix(lip, '#000000', 0.08), soft=max(1, S*0.005), height=max(2, S*0.02), spec=0.25))
    U2 = U  # keep transform
    out[-1] = out[-1].replace('/>', f' transform="{tr}"/>')
    # lower lip: fuller, catches light
    L = bot + [(x, y + ll * math.sin(math.pi * (i / n)) ** 0.6 + 0.002) for i, (x, y) in list(enumerate(bot))[::-1]]
    out.append(d.bump(pts(L), lip, soft=max(1, S*0.006), height=max(2, S*0.025), spec=0.5, shine=30,
                      tr=tr))
    # the line between the lips
    line = pts(top, close=False) if opn <= 0.02 else None
    if line:
        out.append(f'<path d="{line}" transform="{tr}" fill="none" stroke="#4a1a20" stroke-width="{f(0.006)}" stroke-linecap="round"/>')
    # corners (dimples)
    for x, y in (top[0], top[-1]):
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="0.006" fill="#5a2228" opacity="0.5" transform="{tr}"/>')
    # philtrum / under-lip shadow
    bl = d.blur(max(1, S * 0.006))
    out.append(f'<g filter="url(#{bl})" opacity="0.35"><ellipse cx="0" cy="{f(max(y for _, y in L) + 0.012)}" rx="{f(w*0.55)}" ry="0.008" fill="#5a2a2a" '
               f'transform="{tr}"/></g>')


def ear(h, d, side, P, out, behind):
    phi = side * P['ear_phi']
    ye = P['ear_y']
    # ear normal: sideways, turned toward the front by ear_out
    al = math.radians(P.get('ear_out', 25))
    n3 = (side * math.cos(al), 0, math.sin(al))
    nz = h.rot(n3)[2]
    base = h.surf(phi, ye, -0.004)
    z = h.rot(base)[2]
    if behind != (z < 0.0):
        return
    x0, y0, _ = h.scr(base)
    # direction of the ear plane across: perpendicular to normal in xz-plane, pointing back
    across = (-math.sin(al) * side, 0, math.cos(al))
    ax = h.rot(across)[0] * h.cr
    w = P['ear_w'] * h.S
    ht = P['ear_h'] * h.S
    sx = max(0.18, abs(nz))
    skin = P['skin']
    # C-shaped ear outline in its plane (local: x back from the head, y down)
    loc = [(0, -0.5), (0.45, -0.55), (0.9, -0.3), (1.0, 0.05), (0.8, 0.4), (0.45, 0.55), (0.15, 0.48), (0.0, 0.3)]
    dirx = -side * (1 if h.cy_ >= 0 else -1)
    # where the ear's far edge goes on screen: away from the face
    proj = []
    for (u, v) in loc:
        proj.append((x0 + dirx * u * w * (0.35 + 0.65 * sx) * 1.0 * (-1 if side < 0 else 1) * -1, y0 + v * ht))
    col = mix(skin, P.get('ear_tint', '#e08070'), 0.25)
    out.append(d.bump(pts(proj), col, soft=max(1.5, h.S * 0.012), height=max(3, h.S * 0.04), spec=0.25))
    # inner fold
    inner = [(x0 + (px - x0) * 0.62 + (1 if side > 0 else -1) * w * 0.02, y0 + (py - y0) * 0.62) for (px, py) in proj[1:6]]
    out.append(d.groove(pts(inner, close=False), col, h.S * 0.012, soft=max(1, h.S * 0.006), depth=-4))


def wrinkle(h, d, phi, y, local_pts, P, out, sw=0.006, depth=-3):
    """A sculpted groove on the surface: local_pts in head units around (phi, y)."""
    if h.facing(phi, y) < 0.05:
        return
    tr, _ = h.frame(phi, y, 0.0)
    out.append(d.groove(pts(local_pts, close=False), P['skin'], sw, soft=max(1, round(h.S * 0.004, 1)), depth=depth, tr=tr))


def blush(h, d, side, P, out, amount=0.35, col='#e0606a'):
    phi = side * P['eye_phi'] * 1.15
    y = P['eye_y'] + 0.1
    if h.facing(phi, y) < 0:
        return
    tr, _ = h.frame(phi, y, 0)
    bl = d.blur(max(2, h.S * 0.03))
    out.append(f'<g filter="url(#{bl})" opacity="{amount}"><ellipse cx="0" cy="0" rx="0.07" ry="0.045" fill="{col}" transform="{tr}"/></g>')


def freckles(h, d, P, out, n=14, seed=3, col='#9a5a3a'):
    import random
    r = random.Random(seed)
    for i in range(n):
        side = -1 if i % 2 else 1
        phi = side * (0.08 + r.random() * 0.45)
        y = P['eye_y'] + 0.06 + r.random() * 0.07
        if h.facing(phi, y) < 0.15:
            continue
        x, yy, _ = h.scr(h.surf(phi, y))
        out.append(f'<circle cx="{f(x)}" cy="{f(yy)}" r="{f(h.S*(0.004+r.random()*0.003))}" fill="{col}" opacity="{f(0.35+r.random()*0.3)}"/>')


# ------------------------------------------------------------------ hair

def lock(h, d, path3, w0, w1=0.0, col='#3a2418', hi=None, soft=None, height=None, taper=1.0, curl=0.0):
    """A sculpted lock of hair: a ribbon along a 3D centre line (head units), width from w0 at the root to w1 at the tip.
    Returns (depth, svg)."""
    S = h.S
    P2 = [h.scr(p) for p in path3]
    zs = [p[2] for p in P2]
    n = len(P2)
    # smooth the centre line
    import math as m
    L, R = [], []
    for i in range(n):
        x, y, _ = P2[i]
        xa, ya, _ = P2[max(0, i - 1)]
        xb, yb, _ = P2[min(n - 1, i + 1)]
        dx, dy = xb - xa, yb - ya
        ln = m.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        t = i / (n - 1)
        wd = (w0 + (w1 - w0) * t ** taper) * S
        L.append((x + nx * wd / 2, y + ny * wd / 2))
        R.append((x - nx * wd / 2, y - ny * wd / 2))
    shape = L + R[::-1]
    soft = soft if soft is not None else max(1.5, w0 * S * 0.22)
    height = height if height is not None else max(3, w0 * S * 0.5)
    svg = d.bump(pts(shape), col, soft=round(soft, 1), height=round(height, 1), spec=0.55, shine=26)
    return (sum(zs) / n, svg)


def cap(h, d, k, y_top, y_bottom_fn, col, out, n=40):
    """The hair mass over the skull: the shell (head scaled by k) above a hairline y_bottom_fn(phi), as one shape.
    Built as many thick horizontal strokes (slices) that merge into one silhouette, then given form."""
    S = h.S
    segs = []
    for i in range(n + 1):
        y = y_top + (0.5 - y_top) * i / n
        arc = []
        for j in range(73):
            phi = -math.pi + 2 * math.pi * j / 72
            if y <= y_bottom_fn(phi):
                arc.append(h.scr(h.surf(phi, y, 0, k))[:2])
            else:
                if len(arc) > 1:
                    segs.append(arc)
                arc = []
        if len(arc) > 1:
            segs.append(arc)
    sw = S * (0.5 - y_top) / n * 2.2
    body = ''.join(f'<path d="{poly(s)[:-2]}" fill="none" stroke="{col}" stroke-width="{f(sw)}" stroke-linejoin="round" stroke-linecap="round"/>' for s in segs)
    return body
