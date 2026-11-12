"""How this style draws a head, a face, a hand, a limb.

A head is built as a simple volume — horizontal cross-sections (half-width a, front depth bf, back depth bb) plus a
front profile (forehead, brow, nose, lips, chin) — and turned by `yaw` (0 front, ~38 three-quarter, 90 profile;
the face turns to the left of the sheet). The outline, the features and the hairline are projected from it, so the
three views of a turnaround agree. What is drawn on it is drawn flat: an even ink contour, one flat skin tone,
features as a few lines (Bilibin) — the eye an almond with a dark iris, the nose a single line with a hook of a
nostril, the mouth a short line and a small red lower lip.

Head units: a head is about 200 high, eye line at y = 0, the crown at about -112, the chin at about +90.
"""
import math
from kit import INK, SKIN, SKIN_SH, RED, CREAM, curve, path_d, _f, _f2

RAD = math.pi / 180


def interp(table, y):
    """Smooth monotone cubic interpolation of a table [(y, v), ...] sorted by y (no bumps between keys)."""
    n = len(table)
    if y <= table[0][0]:
        return table[0][1]
    if y >= table[-1][0]:
        return table[-1][1]
    xs = [t[0] for t in table]
    vs = [t[1] for t in table]
    dk = [(vs[i + 1] - vs[i]) / ((xs[i + 1] - xs[i]) or 1e-6) for i in range(n - 1)]
    m = [dk[0]] + [0.0 if dk[i - 1] * dk[i] <= 0 else (dk[i - 1] + dk[i]) / 2 for i in range(1, n - 1)] + [dk[-1]]
    for i in range(n - 1):
        if dk[i] == 0:
            m[i] = m[i + 1] = 0.0
        else:
            a, b = m[i] / dk[i], m[i + 1] / dk[i]
            h = a * a + b * b
            if h > 9:
                t = 3 / math.sqrt(h)
                m[i], m[i + 1] = t * a * dk[i], t * b * dk[i]
    i = 0
    while xs[i + 1] < y:
        i += 1
    h = xs[i + 1] - xs[i]
    t = (y - xs[i]) / h
    t2, t3 = t * t, t * t * t
    return ((2 * t3 - 3 * t2 + 1) * vs[i] + (t3 - 2 * t2 + t) * h * m[i] + (-2 * t3 + 3 * t2) * vs[i + 1]
            + (t3 - t2) * h * m[i + 1])


class P:
    """A character's head: numbers. Defaults are a young adult."""

    def __init__(self, **kw):
        self.crown = -112
        self.chin = 92
        self.cheek = 66          # half-width at the cheekbones (y ~ 8)
        self.temple = 64
        self.jaw = 55            # half-width at the jaw corner
        self.jaw_y = 60
        self.chin_w = 17
        self.skull = 70          # half-width of the cranium (y ~ -50)
        self.back = 1.12         # depth of the back of the head against its half-width
        self.face_d = 0.86       # depth of the face half against its half-width
        # profile (z forward): forehead, brow, nose, lips, chin
        self.forehead = 64
        self.brow_z = 68
        self.nose_y = 46
        self.nose_z = 86          # tip
        self.nose_w = 11          # half-width of the nostrils
        self.nose = 'straight'    # straight, snub, big, hooked
        self.lip_z = 70
        self.chin_z = 62
        self.mouth_y = 66
        self.mouth_w = 20
        self.lip = 'thin'         # thin (a line and a small lower lip), full, none
        self.lip_col = '#c4655a'
        self.eye_x = 29
        self.eye_w = 19
        self.eye_h = 8.5
        self.eye_tilt = 0          # outer corner up (+) or down (-)
        self.iris = 5.6
        self.iris_col = '#4b3a2b'
        self.lid = 1.0             # weight of the upper lid line
        self.lashes = 0            # number of lash strokes at the outer corner
        self.under = 0             # lines under the eye (age, tiredness)
        self.brow_y = -19
        self.brow = 'arc'          # arc, straight, bushy, thick, sharp
        self.brow_w = 1.0
        self.brow_col = INK
        self.ear_y = (-6, 38)
        self.wrinkles = 0
        self.skin = SKIN
        self.blush = 0.0
        self.neck = 34
        self.freckles = []
        for k, v in kw.items():
            if not hasattr(self, k):
                raise KeyError(k)
            setattr(self, k, v)

    # the volume ---------------------------------------------------------
    def a(self, y):
        c = self
        return interp([(c.crown, 6), (c.crown + 12, 42), (c.crown + 34, c.skull * 0.93), (-50, c.skull),
                       (-20, c.temple), (8, c.cheek), (30, (c.cheek * 0.6 + c.jaw * 0.4)), (c.jaw_y, c.jaw),
                       (c.chin - 20, c.chin_w + 17), (c.chin - 9, c.chin_w + 7), (c.chin - 3, c.chin_w * 0.7),
                       (c.chin, 1)], y)

    def bf(self, y):
        """Depth of the front half: the face mask (no nose) below the forehead, the round skull above."""
        c = self
        if y < -78:
            return interp([(c.crown, 6), (c.crown + 14, 40), (c.crown + 36, c.forehead * 0.8),
                           (-78, c.forehead * 0.9)], y)
        return self.zm(y)

    def zm(self, y):
        """The face mask's middle line: forehead, brow, cheeks, lips, chin — the profile without the nose."""
        c = self
        return interp([(-78, c.forehead * 0.9), (-55, c.forehead), (c.brow_y + 4, c.brow_z), (2, c.brow_z - 7),
                       (c.nose_y, c.brow_z - 5), (c.mouth_y - 4, c.lip_z), (c.mouth_y + 12, c.chin_z - 6),
                       (c.chin - 10, c.chin_z), (c.chin, c.chin_z - 14)], y)

    def bb(self, y):
        c = self
        return interp([(c.crown, 6), (c.crown + 16, 50), (-60, c.skull * c.back), (-10, c.skull * c.back * 0.98),
                       (25, c.skull * c.back * 0.8), (c.jaw_y, c.jaw * 0.6), (c.chin, 4)], y)

    def zf(self, y):
        """The front profile: how far forward the face is at height y (None above the forehead)."""
        c = self
        n0 = c.nose_y
        tab = [(-78, c.forehead * 0.9), (-55, c.forehead), (c.brow_y + 4, c.brow_z), (-2, c.brow_z - 5),
               (n0 - 22, c.brow_z - 2 + (c.nose_z - c.brow_z) * 0.35),
               (n0 - 3, c.nose_z), (n0 + 4, c.nose_z - 6), (n0 + 9, c.lip_z - 4),
               (c.mouth_y - 5, c.lip_z), (c.mouth_y + 1, c.lip_z - 6), (c.mouth_y + 7, c.lip_z - 3),
               (c.mouth_y + 14, c.chin_z - 8), (c.chin - 10, c.chin_z), (c.chin, c.chin_z - 12)]
        if c.nose == 'snub':
            tab[5] = (n0 - 4, c.nose_z)
            tab[4] = (n0 - 20, c.brow_z - 4 + (c.nose_z - c.brow_z) * 0.2)
        if c.nose == 'hooked':
            tab[4] = (n0 - 20, c.brow_z + (c.nose_z - c.brow_z) * 0.75)
        return interp(tab, y)

    def zs(self, x, y):
        """Depth of the face surface at (x, y): flat in front, rounding off at the sides; the nose and the lips
        rise out of the middle."""
        a = self.a(y)
        u = min(1.0, abs(x) / max(a, 1))
        base = self.bf(y) * (1 - u ** 2.4) ** (1 / 2.4)
        if -78 < y:
            extra = self.zf(y) - self.zm(y)
            if extra > 0:
                k = max(0.0, 1 - abs(x) / (self.nose_w * 1.3 if y < self.nose_y + 8 else self.mouth_w * 1.3))
                base += extra * k * k * (3 - 2 * k)
        return base


class View:
    """A head turned by yaw (degrees): projection of head points to the sheet."""

    def __init__(self, p, yaw=0):
        self.p = p
        self.yaw = yaw
        self.s, self.c = math.sin(yaw * RAD), math.cos(yaw * RAD)

    def pt(self, x, y, z):
        return (x * self.c - z * self.s, y)

    def surf(self, x, y, lift=0.0):
        return self.pt(x, y, self.p.zs(x, y) + lift)

    def facing(self, x, y=0):
        """How much a point of the face at (x, y) faces the viewer: 1 frontal, 0 edge-on, < 0 hidden."""
        z = self.p.zs(x, y)
        phi = math.atan2(x, max(z, 1))
        return math.cos(phi - self.yaw * RAD)

    def extent(self, y, grow=0.0):
        """Left and right edge of the head's cross-section at height y as seen in this view."""
        p = self.p
        a = p.a(y) + grow
        lo, hi = 1e9, -1e9
        for i in range(25):
            x = -a + 2 * a * i / 24
            xx = max(-p.a(y), min(p.a(y), x))
            zfr = p.zs(xx, y) + grow if abs(x) <= p.a(y) else grow * math.sqrt(max(0, 1 - ((abs(x) - p.a(y)) / max(grow, 1e-6)) ** 2))
            u = min(1.0, abs(x) / a)
            # under the jaw corner the back of the cross-section is the neck, not the head
            kb = min(1.0, max(0.0, (p.jaw_y + 4 - y) / 18.0))
            zbk = -(p.bb(y) * kb + grow) * math.sqrt(max(0.0, 1 - u * u))
            for z in (zfr, zbk):
                X = x * self.c - z * self.s
                lo, hi = min(lo, X), max(hi, X)
        return lo, hi

    def outline(self, y_top=None):
        """The head's silhouette (crown to chin), a closed list of points."""
        p = self.p
        s, c = self.s, self.c
        ys = [p.crown + (p.chin - p.crown) * i / 60 for i in range(61)]
        left, right = [], []
        for y in ys:
            xl, xr = self.extent(y)
            left.append((xl, y))
            right.append((xr, y))
        chin_c = self.pt(0, p.chin, p.chin_z - 14)
        bottom = [(chin_c[0], p.chin + 1)]
        L = left[1:-1][::2]
        R = right[::-1][1:-1][::-1][::2][::-1]
        return L + bottom + R



# ---------------------------------------------------------------- expressions

EXPR = {
    'calm':     dict(brow=0, tilt=0, open=1.0, smile=0.15, mouth=0.0, wide=1.0, look=(0, 0)),
    'joy':      dict(brow=4, tilt=-1, open=0.45, smile=1.0, mouth=0.55, wide=1.25, look=(0, 0), cheeks=1),
    'surprise': dict(brow=10, tilt=1.5, open=1.35, smile=0.0, mouth=0.6, wide=0.7, round=True, look=(0, 0)),
    'sadness':  dict(brow=3, tilt=5, open=0.75, smile=-0.6, mouth=0.0, wide=0.85, look=(0, 2.5)),
    'anger':    dict(brow=-5, tilt=-6, open=0.85, smile=-0.7, mouth=0.35, wide=1.1, teeth=True, look=(0, 0)),
}


def expr(name, **over):
    e = dict(EXPR['calm'])
    e.update(EXPR.get(name, {}))
    e.update(over)
    return e


# ---------------------------------------------------------------- the head

def _eye(d, v, side, e, p):
    """One eye: an almond of the upper lid line (even ink) and a thin lower line, a dark iris, a small highlight."""
    x0 = p.eye_x * side
    f = v.facing(x0, 0)
    if f < 0.22:
        return
    cx, cy = v.surf(x0, 0, -6)
    w = p.eye_w * (0.25 + 0.75 * f)
    op = e['open']
    h = p.eye_h * op
    inner = -side          # the inner corner points to the nose
    # in a turned head the eye's inner corner is the side toward the nose on the sheet
    tilt = p.eye_tilt
    ic = (cx + inner * w * 0.5 * (1 if v.yaw < 60 else 0.6), cy + 1.5)
    oc = (cx - inner * w * 0.5, cy - tilt)
    if v.yaw > 0:
        # the far eye (side -1 when turned) is narrower and its outer half hides behind the cheek
        pass
    top = [ic, (cx + inner * w * 0.2, cy - h * 1.05), (cx - inner * w * 0.18, cy - h * 1.0), oc]
    bot = [oc, (cx - inner * w * 0.1, cy + h * 0.55 + 1), (cx + inner * w * 0.25, cy + h * 0.45 + 1), ic]
    if op < 0.25:
        # closed with laughter: one arc
        d.ink([ic, (cx, cy - 4 - 3 * e.get('smile', 0)), oc], p.lid * 2.6)
        return
    eye_pts = top + bot[1:-1]
    d.fill(eye_pts, '#fbf6ea')
    lx, ly = e['look']
    ir = p.iris * (0.6 + 0.4 * f) * (1.0 if not e.get('round') else 0.85)
    ix = cx + lx + (-v.s * w * 0.18)
    iy = cy - h * 0.12 + ly
    with d.clipped(eye_pts):
        d.raw('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (_f(ix), _f(iy), _f2(ir * (0.7 + 0.3 * f)),
                                                                        _f2(ir), p.iris_col))
        d.dot(ix, iy, ir * 0.48, INK)
        d.dot(ix + ir * 0.35, iy - ir * 0.4, ir * 0.22, '#fffaf0')
    d.ink(top, 2.6 * p.lid)
    d.thin(bot, k=0.8)
    # a crease of the lid above
    if op > 0.6:
        d.thin([(ic[0] - inner * w * -0.05, ic[1] - h * 0.9), (cx, cy - h * 1.75), (oc[0] + inner * 1.5, oc[1] - h * 1.1)],
               k=0.7, op=0.7)
    for i in range(p.lashes):
        t = i / max(1, p.lashes - 1)
        bx, by = oc[0] + inner * w * 0.15 * t, oc[1] - h * 0.2 * t
        d.lock([(bx, by), (bx - inner * 4, by - 4 - 1.5 * t)], 2.2)
    for i in range(p.under):
        d.thin([(cx + inner * w * 0.35, cy + h * 0.9 + 3 + 4 * i), (cx, cy + h * 1.15 + 4 + 4 * i),
                (cx - inner * w * 0.4, cy + h * 0.6 + 3 + 4 * i)], k=0.6, op=0.65)


def _brow(d, v, side, e, p):
    x0 = p.eye_x * side
    f = v.facing(x0, p.brow_y)
    if f < 0.15:
        return
    raise_, tilt = e['brow'], e['tilt']
    xs = [x0 - side * 16, x0 - side * 2, x0 + side * 13]
    ys = [p.brow_y - raise_ - tilt + 2, p.brow_y - raise_ - 4, p.brow_y - raise_ + 1 + tilt * 0.3]
    pts = [v.surf(x, y, 2) for x, y in zip(xs, ys)]
    if p.brow == 'bushy':
        # a tufted mass with an ink edge (white brows still read on skin)
        from kit import offset
        sm = curve(pts, False, 6)
        w = 11 * p.brow_w
        up = offset(sm, lambda t: w * (0.35 + 0.65 * math.sin(math.pi * min(1, t * 1.1)) ** 0.5) / 2)
        dn = offset(sm, lambda t: -w * 0.35)
        if side < 0:
            up, dn = dn, up
        poly = up + dn[::-1]
        d.fill(poly, p.brow_col)
        d.ink(poly, d.THIN * 1.1, closed=True)
        for i in range(4):
            q = sm[int((len(sm) - 1) * (i + 0.5) / 4)]
            d.thin([q, (q[0] + side * 7, q[1] - 7)], k=0.7)
    elif p.brow == 'thick':
        d.lock(pts, 8 * p.brow_w, p.brow_col, 'swell')
    elif p.brow == 'straight':
        d.lock(pts, 5.5 * p.brow_w, p.brow_col, 'swell')
    else:
        d.lock(pts, 4.4 * p.brow_w, p.brow_col, 'swell')


def _nose(d, v, e, p):
    s = v.s
    n0 = p.nose_y
    if v.yaw < 8:
        # front: a single line down the shadow side, a rounded tip, two nostril hooks
        d.thin([(-5, n0 - 24), (-6, n0 - 12), (-8, n0 - 2)], k=0.9)
        d.thin([(-p.nose_w, n0 - 1), (-p.nose_w - 2, n0 + 5), (-p.nose_w + 4, n0 + 8), (-3, n0 + 7)], k=1.0)
        d.thin([(p.nose_w, n0 - 1), (p.nose_w + 2, n0 + 5), (p.nose_w - 4, n0 + 8), (3, n0 + 7)], k=1.0)
        return
    if v.yaw < 75:
        # three-quarter: the near contour of the nose follows the profile; the wing on the near side
        pts = [v.pt(1.5, y, p.zf(y)) for y in (-4, n0 - 22, n0 - 8)]
        tip = v.pt(2, n0, p.nose_z - 2)
        d.thin(pts + [tip, v.pt(1, n0 + 6, p.nose_z - 9)], k=1.05)
    # the nostril wing on the near side
    wx, wy = v.surf(p.nose_w * 0.95, n0 + 2, 3)
    d.thin([(wx - 2, wy - 7), (wx + 3, wy - 1), (wx, wy + 5), (wx - 6, wy + 5)], k=1.0)


def tx_mid(pts):
    return sum(q[0] for q in pts) / len(pts)


def _mouth(d, v, e, p):
    my = p.mouth_y
    sm = e['smile']
    wide = e['wide']
    mw = p.mouth_w * wide
    opn = e['mouth']
    sk = e.get('smirk', 0)
    lc = v.surf(-mw, my - sm * 5 + sk * 3, 1)
    rc = v.surf(mw, my - sm * 5 - sk * 6, 1)
    fl, fr = v.facing(-mw, my), v.facing(mw, my)
    c = v.surf(0, my + sm * 2.5, 1)
    if fl < 0.25:
        lc = v.pt(-mw * 0.3, my - sm * 5, p.zf(my) - 4)
    if opn > 0.05:
        # an open mouth: dark red, teeth above, tongue below
        h = 22 * opn
        if e.get('round'):
            top = [lc, v.surf(0, my - h * 0.35, 2), rc]
            bot = [rc, v.surf(0, my + h * 0.75, 2), lc]
        else:
            top = [lc, v.surf(-mw * 0.45, my - 3 - sm * 2, 2), v.surf(0, my - 2.5, 2),
                   v.surf(mw * 0.45, my - 3 - sm * 2, 2), rc]
            bot = [rc, v.surf(mw * 0.5, my + h * 0.8 - sm * 1, 2), v.surf(0, my + h, 2),
                   v.surf(-mw * 0.5, my + h * 0.8 - sm * 1, 2), lc]
        poly = top + bot[1:-1]
        d.fill(poly, '#6e1f1c')
        top_y = min(q[1] for q in top)
        bot_y = max(q[1] for q in bot)
        hh = bot_y - top_y
        with d.clipped(poly):
            # the upper teeth: a band under the upper lip, its lower edge a gentle curve
            tb = 0.32 if not e.get('round') else 0.22
            tp = [(lc[0] - 6, top_y - 8), (rc[0] + 6, top_y - 8), (rc[0] + 6, top_y + hh * tb * 0.7),
                  ((lc[0] + rc[0]) / 2, top_y + hh * tb + 2), (lc[0] - 6, top_y + hh * tb * 0.7)]
            d.fill(tp, '#fbf6ea')
            if e.get('teeth'):
                bp = [(lc[0] - 6, bot_y + 8), (rc[0] + 6, bot_y + 8), (rc[0] + 6, bot_y - hh * 0.28),
                      ((lc[0] + rc[0]) / 2, bot_y - hh * 0.22), (lc[0] - 6, bot_y - hh * 0.28)]
                d.fill(bp, '#fbf6ea')
            else:
                tx = (lc[0] + rc[0]) / 2 + (bot[2][0] - tx_mid(top)) * 0.2
                d.raw('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#c8605a"/>' % (
                    _f(tx), _f(bot_y - hh * 0.05), _f(abs(rc[0] - lc[0]) * 0.3), _f(hh * 0.38)))
        d.ink(poly, 2.4, closed=True)
        return
    # closed: a short line, the lower lip as a small red shape
    line = [lc, v.surf(-mw * 0.4, my + sm * 1.2, 1), c, v.surf(mw * 0.4, my + sm * 1.2, 1), rc]
    if p.lip != 'none':
        lw = 1.0 if p.lip == 'thin' else 1.5
        lo = [v.surf(-mw * 0.55, my + 1.5, 1), v.surf(0, my + 6.5 * lw, 1), v.surf(mw * 0.55, my + 1.5, 1),
              v.surf(0, my + 2.5, 1)]
        d.fill(lo, p.lip_col, op=0.85)
        if p.lip == 'full':
            up = [v.surf(-mw * 0.6, my - 0.5, 1), v.surf(-mw * 0.15, my - 4.5, 1), v.surf(0, my - 3, 1),
                  v.surf(mw * 0.15, my - 4.5, 1), v.surf(mw * 0.6, my - 0.5, 1), v.surf(0, my + 0.5, 1)]
            d.fill(up, p.lip_col, op=0.75)
    d.ink(line, 2.2)
    # corners: a small tick deepens a smile or a frown
    for q, sd in ((lc, -1), (rc, 1)):
        if abs(sm) > 0.3:
            d.thin([(q[0] - sd * 1, q[1]), (q[0] + sd * 3, q[1] - sm * 4)], k=0.8)


def ear(d, v, p, side=1, behind=False):
    y0, y1 = p.ear_y
    x = p.a((y0 + y1) / 2) * side
    zc = -p.a(15) * 0.18
    f = math.cos(math.atan2(side, 0.15) - v.yaw * RAD)
    if behind != (f < 0.35):
        return
    if f < -0.1:
        return
    cx, _ = v.pt(x * 0.97, 0, zc)
    w = 9 + 13 * max(0.0, f)
    ex = cx + side * (w * 0.6 if f < 0.35 else 0)
    pts = [(cx, y0 + 2), (ex + side * w * 0.6, y0 - 1), (ex + side * w * 0.9, y0 + 14), (ex + side * w * 0.5, y1 - 6),
           (cx + side * 2, y1)]
    if f >= 0.35:
        # a face-on ear in profile: a C, its centre on the head
        pts = [(cx - w * 0.3, y0 + 3), (cx + w * 0.25, y0 - 2), (cx + w * 0.55, y0 + 14), (cx + w * 0.3, y1 - 5),
               (cx - w * 0.2, y1 + 1), (cx - w * 0.35, y1 - 8)]
    d.shape(pts, p.skin, 2.6)
    if f >= 0.35:
        d.thin([(cx + w * 0.25, y0 + 6), (cx + w * 0.05, y0 + 14), (cx + w * 0.2, y1 - 12), (cx, y1 - 7)], k=0.9)
    else:
        d.thin([(ex + side * w * 0.35, y0 + 5), (ex + side * w * 0.5, y0 + 15), (ex + side * w * 0.25, y1 - 10)],
               k=0.8)


def head(d, p, yaw=0, e=None, back=None, front=None, under=None, extra=None, neck_col=None):
    """Draw a head. back(d, v) — hair behind the head; under(d, v) — over the skin, under the features (a beard's
    mass, a shadow under hair); front(d, v) — hair in front; extra(d, v) — glasses, wrinkles, a moustache."""
    e = e or expr('calm')
    v = View(p, yaw)
    if back:
        back(d, v)
    ear(d, v, p, 1, behind=True)
    ear(d, v, p, -1, behind=True)
    out = v.outline()
    d.fill(out, p.skin)
    if under:
        under(d, v)
    if p.blush or e.get('cheeks'):
        for sd in (1, -1):
            f = v.facing(p.eye_x * sd, 28)
            if f > 0.3:
                bx, by = v.surf(p.eye_x * sd * 1.05, 28)
                d.raw('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#d9776a" opacity="%s"/>' % (
                    _f(bx), _f(by), _f(12 * f), 7, _f2(0.18 + 0.15 * (p.blush + e.get('cheeks', 0) * 0.6))))
    ear(d, v, p, 1)
    _nose(d, v, e, p)
    _mouth(d, v, e, p)
    for sd in (1, -1):
        _eye(d, v, sd, e, p)
        _brow(d, v, sd, e, p)
    if e.get('cheeks') and e['smile'] > 0.5:
        # laugh lines from the nose wings
        for sd in (1, -1):
            if v.facing(sd * 24, 55) > 0.35:
                d.thin([v.surf(sd * 15, p.nose_y + 4, 2), v.surf(sd * 22, p.mouth_y - 4, 1),
                        v.surf(sd * 22, p.mouth_y + 6, 1)], k=0.8)
    for (fx, fy) in getattr(p, 'freckles', []):
        if v.facing(fx, fy) > 0.3:
            q = v.surf(fx, fy, 1)
            d.dot(q[0], q[1], 2.0, '#b5653f')
    for i in range(p.wrinkles):
        y = -60 + i * 9
        d.thin([v.surf(-22 + i * 3, y + 2), v.surf(0, y - 1), v.surf(22 - i * 3, y + 2)], k=0.6, op=0.7)
    d.ink(out, closed=True)
    if extra:
        extra(d, v)
    if front:
        front(d, v)
    return v


# ---------------------------------------------------------------- hair helpers

def shell(v, grow=8, y_side=8, hairline=None, n=40, y_back=None):
    """A cap of hair over the head as seen in view v: the head's silhouette enlarged by `grow` from the crown down
    to y_side on the face side (y_back on the back side), closed along the hairline (3D points on the face, left
    temple to right). Hairline points turned away from the viewer are left out."""
    p = v.p
    y_back = y_side if y_back is None else y_back
    if hairline:
        # the face side of the cap rises to the hairline's top as the head turns to profile
        htop = min(q[1] for q in hairline)
        y_side = y_side + (htop + 6 - y_side) * min(1.0, v.s ** 1.5 * 1.1)
    top = p.crown - grow * 0.85
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        yl = top + (y_side - top) * t
        yr = top + (y_back - top) * t
        for y, side in ((yl, left), (yr, right)):
            if y < p.crown + 4:
                k = (p.crown + 4 - y) / (p.crown + 4 - top)
                g = grow * math.sqrt(max(0.0, 1 - k * k))
                lo, hi = v.extent(p.crown + 4, grow)
                lo, hi = lo * math.sqrt(max(0.0, 1 - k ** 2)), hi * math.sqrt(max(0.0, 1 - k ** 2))
                mid = v.pt(0, 0, (p.bf(p.crown + 4) - p.bb(p.crown + 4)) / 2)[0]
                lo, hi = mid + (lo - mid), mid + (hi - mid)
            else:
                lo, hi = v.extent(y, grow)
            side.append((lo if side is left else hi, y))
    pts = left[::-1] + right[1:]
    if hairline:
        hl = []
        for q in hairline:
            if v.facing(q[0], q[1]) > 0.05:
                hl.append(v.pt(*q))
        pts = pts + hl[::-1]
    return pts


def hairline(p, top=-70, temple=-40, side_y=8, back=0.0):
    """Hairline points (3D) from the left temple over the forehead to the right one."""
    out = []
    for x, y in ((-p.a(side_y) * 0.92, side_y), (-p.a(temple) * 0.86, temple), (-p.a(top) * 0.45, top + 5),
                 (0, top), (p.a(top) * 0.45, top + 5), (p.a(temple) * 0.86, temple), (p.a(side_y) * 0.92, side_y)):
        out.append((x, y, p.zs(x, y) * (1 - back) + 2))
    return out


# ---------------------------------------------------------------- body pieces

def limb(d, pts, w0, w1, color, pattern=None, line=True, n=8):
    """A tube along pts tapering from w0 to w1 (a sleeve, a trouser leg, an arm)."""
    from kit import offset
    sm = curve(pts, False, n)
    a = offset(sm, lambda t: (w0 + (w1 - w0) * t) / 2)
    b = offset(sm, lambda t: -(w0 + (w1 - w0) * t) / 2)
    poly = a + b[::-1]
    d.raw('<path d="%s" fill="%s"/>' % (path_d(poly), color))
    if pattern:
        d.raw('<path d="%s" fill="url(#%s)"/>' % (path_d(poly), pattern))
    if line:
        d.raw('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>'
              % (path_d(poly), INK, _f2(d.LINE * d.lw)))
    return a, b


HANDS = {
    # one silhouette per pose, the wrist at (0, 0), the fingers down (+y); a right hand seen from its back, the thumb
    # on the -x side. Points tagged 'c' are the notches between fingers. A hand is ~100 long (scale 1.4 for an adult
    # at head scale: a hand is about as long as the face).
    'rest': ([(-16, 0), (-19, 20, 'c'), (-28, 34), (-30, 48), (-25, 58), (-19, 52), (-18, 44, 'c'), (-19, 62),
              (-18, 82), (-14, 90), (-9, 84), (-7, 68, 'c'), (-6, 88), (-2, 98), (3, 92), (3, 70, 'c'),
              (6, 88), (10, 93), (13, 86), (12, 66, 'c'), (16, 78), (20, 80), (22, 72), (20, 50), (17, 0)],
             [[(-17, 46), (-12, 52)], [(-3, 46), (-2, 60)], [(7, 46), (8, 60)]]),
    'open': ([(-15, 0), (-20, 18, 'c'), (-34, 28), (-46, 36), (-47, 44), (-40, 46), (-24, 42, 'c'), (-26, 62),
              (-28, 84), (-23, 90), (-17, 84), (-13, 62, 'c'), (-10, 86), (-6, 98), (0, 96), (0, 64, 'c'),
              (6, 90), (12, 94), (14, 88), (9, 62, 'c'), (20, 80), (25, 82), (26, 76), (19, 52), (18, 30),
              (17, 0)], [[(-12, 40), (-8, 50)], [(1, 40), (2, 50)]]),
    'fist': ([(-16, 0), (-20, 20), (-26, 34), (-24, 46), (-14, 56), (-4, 62), (8, 62), (18, 56), (22, 44),
              (21, 22), (17, 0)],
             [[(-14, 38), (-6, 50)], [(-20, 32), (-10, 32), (-2, 40)], [(-2, 50), (-1, 61)], [(8, 50), (8, 61)],
              [(-12, 56), (-14, 46)]]),
    'point': ([(-16, 0), (-19, 20, 'c'), (-27, 34), (-28, 46), (-22, 52), (-17, 48, 'c'), (-17, 70), (-16, 98),
               (-11, 104), (-7, 98), (-6, 62, 'c'), (-2, 66), (6, 66), (14, 62), (20, 54), (21, 30), (17, 0)],
              [[(-6, 56), (14, 56)], [(1, 60), (1, 66)], [(9, 58), (9, 64)]]),
}


def hand(d, x, y, ang=0, s=1.4, pose='rest', skin=SKIN, flip=False, sleeve=None):
    """A hand drawn as one outlined silhouette with the fingers as lobes (the way the ornamental illustration
    draws a hand: few lines, the fingers told by the notches between them). ang turns it (0: fingers down),
    flip mirrors it (a left hand)."""
    pts, inner = HANDS[pose]
    with d.g(x, y, s, ang, flip):
        d.shape(pts, skin, n=6)
        for ln in inner:
            d.thin(ln, k=0.8)


# ---------------------------------------------------------------- hair locks (Mucha's whiplash, Bilibin's strands)

def ribbon(d, pts, w0, w1, color, inner=2, curl=0.0, n=7, line=True, inner_col=None, taper0=1.0):
    """A lock of hair as a ribbon: centre curve pts, width w0 at the root to w1 at the tip; `inner` thin strand
    lines run inside along it; `curl` (radius) rolls the tip into a small loop, as Mucha's locks end."""
    from kit import offset
    sm = curve(pts, False, n)
    if curl:
        # continue the curve into a spiral turning toward the side of the last bend
        (x1, y1), (x2, y2) = sm[-2], sm[-1]
        ang = math.atan2(y2 - y1, x2 - x1)
        sgn = 1 if curl > 0 else -1
        r = abs(curl)
        cx, cy = x2 + math.cos(ang + sgn * math.pi / 2) * r, y2 + math.sin(ang + sgn * math.pi / 2) * r
        a0 = math.atan2(y2 - cy, x2 - cx)
        for i in range(1, 14):
            t = i / 13
            a = a0 + sgn * t * math.pi * 1.5
            rr = r * (1 - 0.55 * t)
            sm.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    wfun = lambda t: (w0 + (w1 - w0) * t) * (1 - t ** 6) * (taper0 + (1 - taper0) * min(1.0, t / 0.18) ** 0.6) + 0.6
    a = offset(sm, lambda t: wfun(t) / 2)
    b = offset(sm, lambda t: -wfun(t) / 2)
    poly = a + b[::-1]
    d.raw('<path d="%s" fill="%s"/>' % (path_d(poly), color))
    for k in range(inner):
        f = (k + 1) / (inner + 1) - 0.5
        q = offset(sm, lambda t, f=f: wfun(t) * f * 0.8)
        cut = int(len(q) * (0.75 + 0.2 * ((k * 37) % 5) / 5))
        d.raw('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (
            path_d(q[2:cut], False), inner_col or INK, _f2(d.THIN * d.lw * 0.75)))
    if line:
        d.raw('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
            path_d(poly), INK, _f2(d.LINE * d.lw * 0.85)))
    return sm


def strands(d, a, b, count, color=INK, k=0.75, t0=0.1, t1=0.9, cut=0.9, op=1.0):
    """Thin lines between two guide curves: the flow of hair inside a mass."""
    from kit import lerp_pts
    sa, sb = curve(a, False, 8), curve(b, False, 8)
    for i in range(count):
        t = t0 + (t1 - t0) * i / max(1, count - 1)
        q = lerp_pts(sa, sb, t)
        m = int(len(q) * (cut - 0.15 * ((i * 7) % 3) / 2))
        d.raw('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"%s/>' % (
            path_d(q[:max(2, m)], False), color, _f2(d.THIN * d.lw * k), '' if op == 1 else ' opacity="%s"' % op))


# ---------------------------------------------------------------- neck and shoulders of a bust

class Torso:
    """Shoulders and chest as a simple volume, turned by yaw like the head (the body turns less than the head
    in a portrait). Head units: neck base at y ~ 118, shoulder line ~ 160."""

    def __init__(self, yaw=0, W=120, neck=32, top=116, slope=40, depth=0.5, bottom=420, drop=0):
        self.yaw = yaw
        self.s, self.c = math.sin(yaw * RAD), math.cos(yaw * RAD)
        self.W, self.neck, self.top, self.slope, self.depth, self.bottom = W, neck, top, slope, depth, bottom
        self.drop = drop     # one shoulder lower than the other (+: the right one lower)

    def a(self, y):
        W, t = self.W, self.top
        return interp([(t, self.neck), (t + 8, self.neck + 18), (t + self.slope, W * 0.82),
                       (t + self.slope + 22, W * 0.97), (t + self.slope + 60, W), (t + self.slope + 160, W * 0.96),
                       (self.bottom, W * 0.92)], y)

    def b(self, y):
        return self.a(y) * self.depth

    def pt(self, x, y, z=None):
        if z is None:
            a = self.a(y)
            u = min(1.0, abs(x) / a)
            z = self.b(y) * math.sqrt(max(0.0, 1 - u ** 2.5))
        return (x * self.c - z * self.s, y + self.drop * x / self.W)

    def outline(self):
        left, right = [], []
        ys = [self.top + (self.bottom - self.top) * i / 40 for i in range(41)]
        for y in ys:
            a, b = self.a(y), self.b(y)
            e = math.sqrt((a * self.c) ** 2 + (b * self.s) ** 2)
            left.append((-e, y - self.drop * e / self.W))
            right.append((e, y + self.drop * e / self.W))
        return left[::-1] + right


def neck(d, v, w=None, color=None, shade=False):
    """The neck: a tube from under the jaw to the shoulders, set back from the face."""
    p = v.p
    w = w or p.neck
    cx = v.pt(0, 0, -12)[0]
    pts = [(cx - w, p.jaw_y), (cx - w * 1.02, 112), (cx - w * 1.15, 140), (cx + w * 1.15, 140), (cx + w * 1.02, 112),
           (cx + w, p.jaw_y)]
    d.fill(pts, color or p.skin)
    if shade:
        # the shadow the jaw throws on the neck (the one place skin gets a second tone)
        chin = v.pt(0, p.chin, p.chin_z - 8)
        sh = [(cx - w - 2, p.jaw_y + 6), (chin[0] - 4, p.chin + 6), (cx + w + 2, p.jaw_y + 16),
              (cx + w + 2, p.chin + 14), (chin[0], p.chin + 18), (cx - w - 2, p.chin + 6)]
        d.fill(sh, SKIN_SH, op=0.7)
    d.ink([(cx - w, p.jaw_y + 10), (cx - w * 1.02, 112), (cx - w * 1.15, 140)])
    d.ink([(cx + w, p.jaw_y + 20), (cx + w * 1.02, 112), (cx + w * 1.15, 140)])


def side_hair(v, y0=-50, y1=34, grow=10, z_in=0.3, side=1, bumps=0, n=14):
    """The hair round the back and sides of a balding head (or under a cap): a band from y0 to y1 between a line
    just in front of the ear (z_in of the depth) and the head's silhouette grown by `grow`. side=1 the near (right)
    side, -1 the far side. bumps > 0 makes the outer edge tufty."""
    p = v.p
    outer, inner = [], []
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        lo, hi = v.extent(y, grow)
        a = p.a(y)
        z = z_in * p.bf(y)
        x = a * math.sqrt(max(0.0, 1 - (z / max(p.bf(y), 1)) ** 2)) * side
        ix = v.pt(x, y, z)[0]
        ox = hi if side > 0 else lo
        if bumps and 0 < i < n:
            ox += side * bumps * (1 if i % 2 else -0.3)
        outer.append((ox, y))
        inner.append((ix, y))
    # round the ends
    top = ((outer[0][0] + inner[0][0]) / 2, y0 - grow * 0.6)
    bot = ((outer[-1][0] + inner[-1][0]) / 2, y1 + grow * 0.4)
    return [top] + outer + [bot] + inner[::-1]


def lobes(pts, count, amp, start=0, end=None, closed=True, sharp=0.0):
    """Turn a run of an outline into lobes (curls, tufts, locks): between start and end (indices into pts)
    `count` bumps of height amp push outward; sharp > 0 points their tips (locks rather than curls)."""
    from kit import curve as _c
    end = len(pts) - 1 if end is None else end
    run = _c(pts[start:end + 1], False, 6)
    # outward normal: away from the centroid of the whole shape
    cx = sum(q[0] for q in pts) / len(pts)
    cy = sum(q[1] for q in pts) / len(pts)
    from kit import arclen
    L = arclen(run)
    tot = L[-1] or 1
    out = []
    for i, (x, y) in enumerate(run):
        a, b = run[max(0, i - 1)], run[min(len(run) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = dy / ln, -dx / ln
        if (x - cx) * nx + (y - cy) * ny < 0:
            nx, ny = -nx, -ny
        ph = (L[i] / tot) * count
        f = abs(math.sin(math.pi * ph))
        f = f ** (1 + sharp * 2)
        out.append((x + nx * amp * f, y + ny * amp * f))
    return pts[:start] + out + pts[end + 1:]
