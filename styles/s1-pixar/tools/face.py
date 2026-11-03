"""face — the eye, brow, nose, mouth, ear and hair of the style, drawn on a pix.Head."""
import math
from pix import (Head, Shell, Canvas, paint_volume, smooth_path, poly_path, lock_ribbon, mix, f, norm3, spline,
                 LIGHT)

E0 = dict(gaze=(0, 0), open=1.0, lower=0.0, brow=0.0, brow_in=0.0, brow_out=0.0, smile=0.0, mopen=0.0, mwide=1.0,
          frown=0.0, squint=0.0, teeth=True, skew=0.0, sneer=0.0, pout=0.0, brow_l=None, mouth_x=0.0, look=None)


def expr(**kw):
    e = dict(E0)
    e.update(kw)
    return e


# ------------------------------------------------------------------ eye

def eye_shape(c, e, side, ex):
    """outline points of one eye opening in front coords. side=-1 screen-left eye, +1 screen-right."""
    x0, y0 = c["eye_x"] * side, c["eye_y"]
    W, Hh = c["eye_w"] / 2, c["eye_h"]
    tilt = c.get("eye_tilt", 1.2)     # outer corner up (+)
    op = ex["open"] * (1 - 0.35 * ex["squint"])
    low = ex["lower"] + 0.45 * ex["squint"] + 0.3 * ex["smile"]
    inner = (x0 - side * W, y0 + 1.0)
    outer = (x0 + side * W, y0 - tilt)
    top_h = Hh * 0.74 * op
    peak = c.get("eye_peak", 0.15)
    up = []
    for i in range(15):
        t = i / 14
        x = inner[0] + (outer[0] - inner[0]) * t
        yb = inner[1] + (outer[1] - inner[1]) * t
        a = math.sin(math.pi * (t ** (1 - peak))) ** 0.55
        up.append((x, yb - top_h * a))
    lo = []
    bot_h = Hh * 0.46 * (1 - 0.6 * low)
    for i in range(1, 14):
        t = 1 - i / 14
        x = inner[0] + (outer[0] - inner[0]) * t
        yb = inner[1] + (outer[1] - inner[1]) * t
        a = math.sin(math.pi * (t ** 0.9)) ** 0.65
        lo.append((x, yb + bot_h * a))
    return up, lo, inner, outer


def draw_eye(cv, hd, c, ex, side):
    up, lo, inner, outer = eye_shape(c, ex, side, ex)
    s = hd.s
    ex0, ey0 = c["eye_x"] * side, c["eye_y"]
    fx = hd.fore(ex0, ey0)
    if fx < 0.12:
        return
    P = hd.P
    sk, sc = c["skin"], c["skin_sh"]
    ink = c.get("lash", "#2b1a17")
    n = len(up)
    g = []
    # upper lid: a band of skin above the opening, lit on top, shaded toward the lashes
    cr = c.get("crease", 3.8) * (0.7 + 0.3 * ex["open"])
    lid_top = [(x + side * 0.3, y - cr * (0.35 + 0.65 * math.sin(math.pi * i / (n - 1)) ** 0.7)) for i, (x, y) in enumerate(up)]
    d_lid = smooth_path([P(*p) for p in up] + [P(*p) for p in lid_top[::-1]])
    g.append(f'<path d="{d_lid}" fill="{mix(sk, sc, 0.25)}" filter="url(#{cv.blur(s * 0.5)})"/>')
    hl = [P(x - side * 0.4, y - cr * 0.55 * math.sin(math.pi * i / (n - 1))) for i, (x, y) in enumerate(up) if 2 < i < n - 3]
    g.append(f'<path d="{smooth_path(hl, closed=False)}" fill="none" stroke="#fff4ea" stroke-width="{f(s * 1.1)}" '
             f'stroke-linecap="round" opacity="0.45" filter="url(#{cv.blur(s * 0.6)})"/>')
    g.append(f'<path d="{smooth_path([P(*p) for p in lid_top[1:-1]], closed=False)}" fill="none" stroke="{mix(sc, ink, 0.3)}" '
             f'stroke-width="{f(s * 0.8)}" stroke-linecap="round" opacity="0.55" filter="url(#{cv.blur(s * 0.45)})"/>')
    # opening
    opening = [P(*p, lift=-0.8) for p in up + lo]
    d_open = smooth_path(opening)
    k = cv.clip(d_open)
    top = P(ex0, ey0 - c["eye_h"] * 0.75)
    bot = P(ex0, ey0 + c["eye_h"] * 0.5)
    gr = cv.lingrad([(0, "#bfa59d", 1), (0.32, "#efe4de", 1), (1, "#fffcf9", 1)], top[0], top[1], bot[0], bot[1])
    g.append(f'<path d="{d_open}" fill="url(#{gr})"/>')
    g.append(f'<g clip-path="url(#{k})">')
    # corners a little darker (the eyeball turns away)
    for cx_, cy_ in (inner, outer):
        p = P(cx_, cy_)
        g.append(f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(s * 3.2)}" fill="#c9a49a" opacity="0.55" filter="url(#{cv.blur(s * 1.4)})"/>')
    gx, gy = ex["gaze"]
    ir = c["iris"]
    icx, icy = ex0 + gx * c["eye_w"] * 0.2, ey0 - 0.9 + gy * c["eye_h"] * 0.22
    circ = lambda r, lift=-0.2: [P(icx + r * math.cos(a), icy + r * math.sin(a), lift=lift) for a in
                                 [i * math.pi / 18 for i in range(36)]]
    ic = P(icx, icy)
    rr = ir * s
    col = c["iris_col"]
    gi = cv.radgrad([(0, mix(col, "#fff0c8", 0.35), 1), (0.5, mix(col, "#ffffff", 0.1), 1), (0.8, col, 1),
                     (0.93, mix(col, "#000000", 0.5), 1), (1, mix(col, "#000000", 0.75), 1)],
                    ic[0], ic[1] + rr * 0.25, rr * 1.1, ic[0], ic[1] + rr * 0.45)
    g.append(f'<path d="{smooth_path(circ(ir))}" fill="url(#{gi})"/>')
    # fibres: a few soft spokes
    for i in range(14):
        a = i * math.pi * 2 / 14 + 0.2
        p0 = P(icx + ir * 0.45 * math.cos(a), icy + ir * 0.45 * math.sin(a))
        p1 = P(icx + ir * 0.88 * math.cos(a), icy + ir * 0.88 * math.sin(a))
        g.append(f'<path d="M{f(p0[0])},{f(p0[1])}L{f(p1[0])},{f(p1[1])}" stroke="{mix(col, "#fff3d6", 0.4)}" '
                 f'stroke-width="{f(s * 0.45)}" opacity="0.35"/>')
    pr = ir * 0.42 * c.get("pupil", 1.0) * ex.get("pupil", 1.0)
    g.append(f'<path d="{smooth_path(circ(pr, -0.1))}" fill="#140b09"/>')
    # lid shadow over the eyeball
    sh = [P(*p, lift=-0.6) for p in up] + [P(x, y + c["eye_h"] * 0.38) for x, y in up[::-1]]
    g.append(f'<path d="{smooth_path(sh)}" fill="#3a1a14" opacity="0.32" filter="url(#{cv.blur(s * 1.0)})"/>')
    g.append('</g>')
    # catchlights
    lx, ly = LIGHT
    h1 = P(icx + lx * ir * 0.42 + 0.8, icy + ly * ir * 0.42)
    h2 = P(icx - lx * ir * 0.45, icy - ly * ir * 0.5)
    g.append(f'<ellipse cx="{f(h1[0])}" cy="{f(h1[1])}" rx="{f(ir * 0.27 * s * max(fx, .45))}" ry="{f(ir * 0.30 * s)}" fill="#ffffff" opacity="0.95"/>')
    g.append(f'<ellipse cx="{f(h2[0])}" cy="{f(h2[1])}" rx="{f(ir * 0.11 * s * max(fx, .45))}" ry="{f(ir * 0.11 * s)}" fill="#ffffff" opacity="0.75"/>')
    # lash line: thin at the inner corner, thick toward the outer, lashes as one form flicking out
    thick = c.get("lid_w", 1.3)
    wing = c.get("wing", 0.0)
    above = []
    for i, (x, y) in enumerate(up):
        t = i / (n - 1)
        w = thick * (0.15 + 0.95 * t ** 0.9) * (0.4 + 0.6 * math.sin(math.pi * min(1, 0.15 + t * 0.85)) ** 0.3)
        above.append(P(x, y - w))
    if wing > 0:
        ox, oy = up[-1]
        above.append(P(ox + side * wing * 2.4, oy - wing * 2.0))
        above.append(P(ox + side * wing * 1.2, oy - wing * 0.2))
    lidp = [P(*p, lift=-0.3) for p in up] + above[::-1]
    g.append(f'<path d="{smooth_path(lidp)}" fill="{ink}"/>')
    # lower lid: no outline — a soft rim of light skin and a faint shadow at the outer half
    lo_pts = [P(x, y + 0.9) for x, y in lo]
    g.append(f'<path d="{smooth_path(lo_pts, closed=False)}" fill="none" stroke="#fff3ea" stroke-width="{f(s * 0.9)}" '
             f'stroke-linecap="round" opacity="0.5" filter="url(#{cv.blur(s * 0.4)})"/>')
    outer_half = [P(x, y + 0.2) for x, y in lo[:7]]
    g.append(f'<path d="{smooth_path(outer_half, closed=False)}" fill="none" stroke="{mix(sc, ink, 0.45)}" '
             f'stroke-width="{f(s * 0.6)}" stroke-linecap="round" opacity="{c.get("lower_a", 0.55)}"/>')
    if c.get("bags", 0) > 0:
        bag = [P(x, y + 3.4 + 1.2 * math.sin(math.pi * i / len(lo))) for i, (x, y) in enumerate(lo) if 1 < i < len(lo) - 1]
        g.append(f'<path d="{smooth_path(bag, closed=False)}" fill="none" stroke="{sc}" stroke-width="{f(s * 1.0)}" '
                 f'stroke-linecap="round" opacity="{c["bags"]}" filter="url(#{cv.blur(s * 0.5)})"/>')
    cv.add("".join(g))


def draw_brow(cv, hd, c, ex, side):
    x0, y0 = c["eye_x"] * side, c["eye_y"] - c.get("brow_h", 9.5)
    L = c.get("brow_len", 20)
    th = c.get("brow_w", 2.4)
    raise_ = ex["brow"] * 5
    bi = ex["brow_in"] * 6      # inner end up (+)
    bo = ex["brow_out"] * 5
    if ex.get("brow_l") is not None and side < 0:
        raise_ = ex["brow_l"] * 4
    pts_c = []
    arch = c.get("brow_arch", 2.0)
    for i in range(9):
        t = i / 8
        x = x0 + side * (-L * 0.52 + L * t)
        y = y0 - raise_ - arch * math.sin(math.pi * (t ** 0.8)) - bi * (1 - t) ** 1.5 - bo * t ** 1.5 + t * 1.0
        pts_c.append((x, y))
    top, bot = [], []
    for i, (x, y) in enumerate(pts_c):
        t = i / 8
        w = th * (0.75 + 0.5 * math.sin(math.pi * min(1, t * 1.3))) * (1.15 - 0.85 * t ** 2.2)
        top.append((x, y - w * 0.55))
        bot.append((x, y + w * 0.45))
    if hd.fore(x0, y0) < 0.1:
        return
    pts = [hd.P(*p, lift=0.6) for p in top + bot[::-1]]
    col = c["brow_col"]
    cv.add(f'<path d="{smooth_path(pts)}" fill="{col}"/>')
    # a little texture: a lighter inner edge
    cv.add(f'<path d="{smooth_path([hd.P(*p, lift=0.7) for p in top[:5]], closed=False)}" fill="none" '
           f'stroke="{mix(col, "#ffffff", 0.25)}" stroke-width="{f(hd.s * 0.35)}" opacity="0.5"/>')


def draw_nose(cv, hd, c, ex):
    s = hd.s
    nt = c["nose_y"]
    nw = c.get("nose_w", 5.5)
    P = hd.P
    sh = c["skin_sh"]
    na = c.get("nose_sh", 0.6)
    # the side plane away from the light, from the bridge down to the wing
    side_pts = [(1.2, nt - 15), (2.8, nt - 7), (nw * 0.85, nt - 1.5), (nw * 1.15, nt + 1.8), (nw * 0.8, nt + 4.2),
                (2.0, nt + 3.0), (1.6, nt - 1), (0.6, nt - 8)]
    cv.add(f'<path d="{smooth_path([P(*p, lift=0.3) for p in side_pts])}" fill="{sh}" opacity="{na}" '
           f'filter="url(#{cv.blur(s * 1.5)})"/>')
    # under the tip: a crescent of shadow (the nose sits above the lip)
    und = [(-nw * 0.95, nt + 3.0), (0, nt + 5.2), (nw * 0.95, nt + 3.0), (nw * 0.6, nt + 6.2), (0, nt + 7.2),
           (-nw * 0.6, nt + 6.2)]
    cv.add(f'<path d="{smooth_path([P(*p, lift=0.2) for p in und])}" fill="{mix(sh, "#6a2e26", 0.2)}" opacity="{na * 0.9}" '
           f'filter="url(#{cv.blur(s * 1.1)})"/>')
    # nostrils
    for sd in (-1, 1):
        nx = sd * nw * 0.45
        pts = [(nx - sd * 1.3, nt + 3.6), (nx + sd * 0.4, nt + 2.7), (nx + sd * 1.5, nt + 3.5), (nx + sd * 0.2, nt + 4.3)]
        if hd.fore(nx, nt + 3) > 0.15:
            cv.add(f'<path d="{smooth_path([P(*p, lift=0.2) for p in pts])}" fill="{c.get("nostril", "#7a3a30")}" opacity="0.75" '
                   f'filter="url(#{cv.blur(s * 0.25)})"/>')
    # bridge and tip light
    br = [P(-1.0, nt - 14), P(-1.3, nt - 7), P(-1.4, nt - 2)]
    cv.add(f'<path d="{smooth_path(br, closed=False)}" fill="none" stroke="#fff4ea" stroke-width="{f(s * 1.4)}" '
           f'stroke-linecap="round" opacity="0.3" filter="url(#{cv.blur(s * 0.8)})"/>')
    h = P(-1.2, nt - 0.5, lift=0.5)
    cv.add(f'<ellipse cx="{f(h[0])}" cy="{f(h[1])}" rx="{f(s * nw * 0.32)}" ry="{f(s * 1.7)}" fill="#fff6ee" opacity="0.6" '
           f'filter="url(#{cv.blur(s * 0.7)})"/>')


def mouth_curves(c, ex):
    my = c["mouth_y"] + ex.get("mouth_dy", 0)
    mw = c["mouth_w"] / 2 * ex["mwide"] * (1 + 0.18 * ex["smile"])
    sm = ex["smile"] * 5.5 - ex["frown"] * 4.5
    op = ex["mopen"] * c.get("mouth_open_max", 12)
    sk = ex["skew"] * 2.5
    mx = ex["mouth_x"]
    # parting line (between the lips) / top edge of the opening
    line_top, line_bot = [], []
    for i in range(15):
        t = i / 14
        u = -1 + 2 * t
        x = mx + u * mw
        corner = abs(u) ** 2.2
        y = my - sm * corner - sk * u + 0.6 * (1 - corner)
        ytop = y - op * 0.28 * (1 - corner ** 1.6)
        ybot = y + op * 0.72 * (1 - corner ** 1.3) * (1 - 0.25 * ex["smile"] * (1 - abs(u)))
        line_top.append((x, ytop))
        line_bot.append((x, ybot))
    return line_top, line_bot, my, mw


def draw_mouth(cv, hd, c, ex):
    s = hd.s
    P = hd.P
    lt, lb, my, mw = mouth_curves(c, ex)
    lip = c["lip"]
    sh = c["skin_sh"]
    upper_h = c.get("lip_up", 2.6)
    lower_h = c.get("lip_low", 3.4)
    # upper lip: from parting line up to a cupid's bow
    ub = []
    for i, (x, y) in enumerate(lt):
        u = (x - ex["mouth_x"]) / mw
        bow = upper_h * (1 - abs(u) ** 1.8) * (1 - 0.35 * math.exp(-(u / 0.13) ** 2))
        ub.append((x, y - bow - 0.15))
    lbn = []
    for i, (x, y) in enumerate(lb):
        u = (x - ex["mouth_x"]) / mw
        lbn.append((x, y + lower_h * (1 - abs(u) ** 1.6) * 0.95 * (0.85 if ex["mopen"] > 0.2 else 1)))
    # lower lip shadow on the chin
    shp = [P(x, y + 2.2) for x, y in lbn[3:-3]]
    cv.add(f'<path d="{smooth_path(shp, closed=False)}" fill="none" stroke="{sh}" stroke-width="{f(s * 2.4)}" '
           f'stroke-linecap="round" opacity="0.55" filter="url(#{cv.blur(s * 1.2)})"/>')
    if c.get("lips_soft"):
        upal, loal = 0.45, 0.55
    else:
        upal, loal = 0.8, 0.85
    # mouth opening
    if ex["mopen"] > 0.05:
        d_open = smooth_path([P(*p) for p in lt + lb[::-1]])
        kk = cv.clip(d_open)
        g = [f'<path d="{d_open}" fill="#4a1a1c"/>', f'<g clip-path="url(#{kk})">']
        if ex["teeth"]:
            tt = [P(x, y + 1.6 * (1 - abs((x - ex["mouth_x"]) / mw) ** 2)) for x, y in lt]
            tt2 = [P(x, y - 0.4) for x, y in lt]
            g.append(f'<path d="{smooth_path(tt2 + tt[::-1])}" fill="#fbf4ee"/>')
            if c.get("gap_tooth"):
                gx = P(ex["mouth_x"] + 1.0, lt[7][1] + 0.6)
                g.append(f'<rect x="{f(gx[0] - s * 0.45)}" y="{f(gx[1] - s * 1.2)}" width="{f(s * 0.9)}" height="{f(s * 2.2)}" fill="#4a1a1c"/>')
        tongue = [P(x, y - 1.0 - 1.4 * (1 - abs((x - ex["mouth_x"]) / mw) ** 2)) for x, y in lb[2:-2]]
        g.append(f'<path d="{smooth_path(tongue + [P(x, y + 3) for x, y in lb[-3:1:-1]])}" fill="#c4545a" opacity="0.9"/>')
        g.append('</g>')
        cv.add("".join(g))
    up = [P(*p, lift=0.2) for p in lt + ub[::-1]]
    lo = [P(*p, lift=0.2) for p in lb + lbn[::-1]]
    cv.add(f'<path d="{smooth_path(up)}" fill="{mix(lip, "#3a1515", 0.18)}" opacity="{upal}"/>')
    cv.add(f'<path d="{smooth_path(lo)}" fill="{lip}" opacity="{loal}"/>')
    hl = P(ex["mouth_x"] - mw * 0.2, lbn[7][1] - lower_h * 0.45)
    cv.add(f'<ellipse cx="{f(hl[0])}" cy="{f(hl[1])}" rx="{f(s * mw * 0.32)}" ry="{f(s * 0.8)}" fill="#fff" opacity="0.35" '
           f'filter="url(#{cv.blur(s * 0.6)})"/>')
    # the parting line itself, darker at the corners
    if ex["mopen"] <= 0.05:
        cv.add(f'<path d="{smooth_path([P(*p, lift=0.3) for p in lt], closed=False)}" fill="none" stroke="#5a2424" '
               f'stroke-width="{f(s * 0.7)}" stroke-linecap="round" opacity="0.85"/>')
    # corners: little dimples when smiling, a crease when frowning
    for sd, (x, y) in ((-1, lt[0]), (1, lt[-1])):
        if ex["smile"] > 0.2:
            pts = [(x + sd * 0.2, y - 1.6), (x + sd * 1.1, y - 0.2), (x + sd * 0.8, y + 1.2)]
            cv.add(f'<path d="{smooth_path([P(*p) for p in pts], closed=False)}" fill="none" stroke="{sh}" '
                   f'stroke-width="{f(s * 0.6)}" stroke-linecap="round" opacity="{0.35 * ex["smile"]}" filter="url(#{cv.blur(s * 0.3)})"/>')


def draw_ear(cv, hd, c, side, behind_pass):
    """ear in a plane facing sideways and a little back. returns nothing; draws only when its pass matches."""
    ey = c.get("ear_y", 8)
    eh = c.get("ear_h", 17)
    ew = c.get("ear_wd", 10)
    wx = hd.width(ey)
    C = (side * (wx - 1.5), ey, c.get("ear_z", -4))
    up = (0, 1, 0)
    v = norm3((side * 0.55, 0, -0.85))
    pts3 = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        # an ear: rounder top, narrower lobe
        r = 1.0 if math.sin(a) < 0 else 0.85
        yy = -math.cos(a) * eh / 2 * 1.0
        xx = math.sin(a) * ew / 2 * r * (0.85 + 0.15 * (-math.cos(a)))
        pts3.append((C[0] + v[0] * xx, C[1] + yy + 1.5, C[2] + v[2] * xx))
    z = hd.rot(C)[2]
    if (z < -6) != behind_pass:
        return
    p2 = [hd.proj(p)[0] for p in pts3]
    d = smooth_path(p2)
    s = hd.s
    paint_volume(cv, d, c["skin"], c["skin_sh"], eh * s, lift=0.1, soft=0.08)
    # translucent warm inner and a fold when the ear faces us
    nrm = hd.rot((C[0] + side * 1, C[1], C[2])), hd.rot(C)
    facing = (nrm[0][0] - nrm[1][0]) * side
    inner = [(C[0] + v[0] * xx * 0.55, C[1] + yy * 0.6 + 1.5, C[2] + v[2] * xx * 0.55)
             for (xx, yy) in [(math.sin(a) * ew / 2 * 0.8, -math.cos(a) * eh / 2) for a in
                              [2 * math.pi * i / 16 for i in range(16)]]]
    q = [hd.proj(p)[0] for p in inner]
    cv.add(f'<path d="{smooth_path(q)}" fill="{c.get("ear_in", "#d77d6c")}" opacity="0.55" filter="url(#{cv.blur(s * 1.0)})"/>')


# ------------------------------------------------------------------ the whole head

def face_shading(cv, hd, c, ex, d_head):
    s = hd.s
    P = hd.P
    k = cv.clip(d_head)
    g = [f'<g clip-path="url(#{k})">']
    sh = c["skin_sh"]
    # eye sockets
    for sd in (-1, 1):
        x0, y0 = c["eye_x"] * sd, c["eye_y"]
        if hd.fore(x0, y0) < 0.1:
            continue
        p = P(x0 - sd * 3, y0 - 4.5)
        g.append(f'<ellipse cx="{f(p[0])}" cy="{f(p[1])}" rx="{f(s * c["eye_w"] * 0.62 * max(.3, hd.fore(x0, y0)))}" ry="{f(s * 6.5)}" '
                 f'fill="{sh}" opacity="{c.get("socket", 0.35)}" filter="url(#{cv.blur(s * 2.6)})"/>')
        # blush
        p = P(sd * c.get("blush_x", 23), c.get("blush_y", 19))
        g.append(f'<ellipse cx="{f(p[0])}" cy="{f(p[1])}" rx="{f(s * 10 * max(.3, hd.fore(sd * 23, 19)))}" ry="{f(s * 6.5)}" '
                 f'fill="{c["blush"]}" opacity="{c.get("blush_a", 0.45) * (1 + 0.4 * ex["smile"])}" filter="url(#{cv.blur(s * 4.2)})"/>')
    # under chin / jaw shadow is on the neck; here a soft darkening along the jaw
    jaw = [P(x, y) for x, y in [(-30, 30), (-20, 42), (0, 50), (20, 42), (30, 30)]]
    g.append(f'<path d="{smooth_path(jaw, closed=False)}" fill="none" stroke="{sh}" stroke-width="{f(s * 6)}" opacity="0.35" '
             f'filter="url(#{cv.blur(s * 3)})"/>')
    # highlights: forehead, cheekbone, chin
    for (x, y, rx, ry, a) in [(-9, -26, 13, 8, 0.28), (-22, 9, 7, 4, 0.22), (-2, 45, 5, 2.6, 0.25)]:
        if hd.fore(x, y) < 0.2:
            continue
        p = P(x, y)
        g.append(f'<ellipse cx="{f(p[0])}" cy="{f(p[1])}" rx="{f(s * rx * hd.fore(x, y))}" ry="{f(s * ry)}" fill="#fff8f0" '
                 f'opacity="{a}" filter="url(#{cv.blur(s * 2.5)})"/>')
    # wrinkles / age marks
    for path, a in c.get("lines", []):
        pts = [P(*p, lift=0.2) for p in path]
        if all(hd.fore(*p) > 0.15 for p in path):
            g.append(f'<path d="{smooth_path(pts, closed=False)}" fill="none" stroke="{mix(sh, "#4a2018", 0.25)}" '
                     f'stroke-width="{f(s * 0.7)}" stroke-linecap="round" opacity="{a}" filter="url(#{cv.blur(s * 0.3)})"/>')
    for (x, y, r, col, a) in c.get("spots", []):
        if hd.fore(x, y) > 0.2:
            p = P(x, y)
            g.append(f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(s * r)}" fill="{col}" opacity="{a}"/>')
    g.append('</g>')
    cv.add("".join(g))


def make_head(c, cx, cy, s, yaw=0.0, pitch=0.0, roll=0.0):
    return Head(c["w"], c["zf"], c["zb"], n=c.get("n", 2.3), bumps=c["bumps"], cx=cx, cy=cy, s=s, yaw=yaw,
                pitch=pitch, roll=roll)


def draw_head(cv, c, cx, cy, s, yaw=0.0, pitch=0.0, roll=0.0, ex=None, hair=None, before_face=None):
    """draws a whole head. hair: object with back(cv, hd) and front(cv, hd)."""
    ex = ex or expr()
    hd = make_head(c, cx, cy, s, yaw, pitch, roll)
    if hair:
        hair.back(cv, hd)
    for sd in (-1, 1):
        draw_ear(cv, hd, c, sd, True)
    if before_face:
        before_face(cv, hd)
    d = hd.outline()
    paint_volume(cv, d, c["skin"], c["skin_sh"], 100 * s, lift=c.get("lift", 0.12), soft=0.065, rim=c.get("rim"))
    face_shading(cv, hd, c, ex, d)
    for sd in (-1, 1):
        draw_ear(cv, hd, c, sd, False)
    if hair and hasattr(hair, "shadow"):
        hair.shadow(cv, hd, d, c["skin_sh"])
    if c.get("extra_under"):
        c["extra_under"](cv, hd, ex)
    order = sorted((-1, 1), key=lambda sd: hd.fore(c["eye_x"] * sd, c["eye_y"]))
    for sd in order:
        draw_eye(cv, hd, c, ex, sd)
    draw_nose(cv, hd, c, ex)
    draw_mouth(cv, hd, c, ex)
    if c.get("extra_face"):
        c["extra_face"](cv, hd, ex)
    for sd in order:
        draw_brow(cv, hd, c, ex, sd)
    if hair:
        hair.front(cv, hd)
    if c.get("extra_over"):
        c["extra_over"](cv, hd, ex)
    return hd


# ------------------------------------------------------------------ hair

class Hair:
    """locks on a shell. each lock: list of control specs; ('s', lat, lon, k) on the shell,
    ('c', lon, y, rad) on a cylinder around the head axis (for hanging hair). widths: list (same length)."""

    def __init__(self, base, dark, light, locks, shell=dict(), back_mass=None, cap=None, sheen="#ffffff",
                 sheen_a=0.22, hairline=None, bun=None):
        self.bun = bun
        self.base, self.dark, self.light = base, dark, light
        self.locks = locks
        self.shell_kw = shell
        self.back_mass = back_mass
        self.cap = cap
        self.sheen, self.sheen_a = sheen, sheen_a
        self.hairline = hairline

    def point(self, sh, sp):
        if sp[0] == 's':
            _, lat, lon, k = sp
            return sh.pt(lat, lon, k)
        _, lon, y, rad = sp
        lo = math.radians(lon)
        return (sh.c[0] + rad * math.sin(lo), y, sh.c[2] + rad * math.cos(lo) * sh.r[2] / sh.r[0])

    def build(self, hd):
        sh = Shell(hd, **self.shell_kw)
        out = []
        for L in self.locks:
            specs, widths = L["pts"], L["w"]
            ctrl = [self.point(sh, sp) for sp in specs]
            # densify along a Catmull-Rom curve
            cen, wid = [], []
            m = 6
            for i in range(len(ctrl) - 1):
                p0 = ctrl[max(0, i - 1)]
                p1, p2 = ctrl[i], ctrl[i + 1]
                p3 = ctrl[min(len(ctrl) - 1, i + 2)]
                for j in range(m):
                    t = j / m
                    t2, t3 = t * t, t * t * t
                    pt = tuple(0.5 * ((2 * p1[a]) + (-p0[a] + p2[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2 +
                                      (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3) for a in range(3))
                    cen.append(pt)
                    wid.append(widths[i] + (widths[i + 1] - widths[i]) * t)
            cen.append(ctrl[-1])
            wid.append(widths[-1])
            normals = []
            for p in cen:
                if p[1] > sh.c[1] + sh.r[1] * 0.35:
                    normals.append(norm3((p[0] - sh.c[0], 0.0, (p[2] - sh.c[2]) * 0.8)))
                else:
                    normals.append(norm3(sh.normal(p)))
            pts, z, c2 = lock_ribbon(hd, cen, wid, normals=normals)
            depth = L.get("z", None)
            out.append((z if depth is None else z + depth, pts, c2, L))
        return out

    def draw_lock(self, cv, hd, pts, c2, L):
        s = hd.s
        d = smooth_path(pts)
        base = L.get("col", self.base)
        dark = L.get("dark", self.dark)
        size = L.get("size", 22) * s
        paint_volume(cv, d, base, dark, size, lift=0.16, soft=0.11)
        # strands: a few fine lines along the lock
        lx, ly = LIGHT
        q = c2[1:-2]
        if len(q) > 3 and L.get("strands", 1):
            kk0 = cv.clip(d)
            g = [f'<g clip-path="url(#{kk0})">']
            for j, o in enumerate((-0.55, -0.2, 0.15, 0.45)):
                off = []
                for i2 in range(len(pts) // 2):
                    a2, b2 = pts[i2], pts[len(pts) - 1 - i2]
                    t = 0.5 + o
                    off.append((a2[0] + (b2[0] - a2[0]) * t, a2[1] + (b2[1] - a2[1]) * t))
                col = self.light if j % 2 == 0 else dark
                g.append(f'<path d="{smooth_path(off[1:-1], closed=False)}" fill="none" stroke="{col}" '
                         f'stroke-width="{f(size * 0.025)}" opacity="0.35"/>')
            g.append('</g>')
            cv.add("".join(g))
        if len(q) > 2:
            off = [(x + lx * size * 0.12, y + ly * size * 0.12) for x, y in q]
            kk = cv.clip(d)
            cv.add(f'<g clip-path="url(#{kk})"><path d="{smooth_path(off, closed=False)}" fill="none" stroke="{self.light}" '
                   f'stroke-width="{f(size * 0.16)}" stroke-linecap="round" opacity="{self.sheen_a * L.get("sheen", 1)}" '
                   f'filter="url(#{cv.blur(size * 0.07)})"/></g>')

    def back(self, cv, hd):
        sh = Shell(hd, **self.shell_kw)
        if self.back_mass:
            for bm in self.back_mass:
                pts = bm(hd, sh)
                d = smooth_path(pts)
                paint_volume(cv, d, mix(self.base, self.dark, 0.55), mix(self.dark, "#000000", 0.25), 80 * hd.s, lift=0.1, soft=0.1)
        self._locks = self.build(hd)
        if self.bun and self.bun_z(hd) < 0:
            self.draw_bun(cv, hd)
        for z, pts, c2, L in sorted(self._locks, key=lambda a: a[0]):
            if z < L.get("split", 0):
                self.draw_lock(cv, hd, pts, c2, L)

    def bun_z(self, hd):
        sh = Shell(hd, **self.shell_kw)
        b = self.bun
        return hd.rot(sh.pt(b["lat"], b["lon"], b["k"]))[2]

    def draw_bun(self, cv, hd):
        sh = Shell(hd, **self.shell_kw)
        b = self.bun
        (x, y), _ = hd.proj(sh.pt(b["lat"], b["lon"], b["k"]))
        r = b["r"] * hd.s
        d = f"M{f(x - r)},{f(y)} a{f(r)},{f(r)} 0 1,0 {f(2 * r)},0 a{f(r)},{f(r)} 0 1,0 {f(-2 * r)},0Z"
        paint_volume(cv, d, self.base, self.dark, 2 * r, lift=0.16, soft=0.12)
        k = cv.clip(d)
        g = [f'<g clip-path="url(#{k})">']
        for i in range(5):
            rr = r * (0.25 + 0.16 * i)
            a0 = i * 1.3
            pts = [(x + rr * math.cos(a0 + t / 10 * 4.4), y + rr * 0.9 * math.sin(a0 + t / 10 * 4.4)) for t in range(11)]
            g.append(f'<path d="{smooth_path(pts, closed=False)}" fill="none" stroke="{self.light if i % 2 else self.dark}" '
                     f'stroke-width="{f(r * 0.06)}" opacity="0.5"/>')
        g.append('</g>')
        cv.add("".join(g))

    def shadow(self, cv, hd, d_head, col):
        """front locks cast a soft shadow on the face (down-right, away from the light)"""
        k = cv.clip(d_head)
        lx, ly = LIGHT
        dx, dy = -lx * 5 * hd.s, -ly * 5 * hd.s
        g = [f'<g clip-path="url(#{k})" opacity="0.6">']
        if self.cap:
            g.append(f'<path d="{self.cap_path(hd)}" fill="{col}" transform="translate({f(dx)},{f(dy)})" '
                     f'filter="url(#{cv.blur(3 * hd.s)})"/>')
        for z, pts, c2, L in self._locks:
            if z >= L.get("split", 0):
                g.append(f'<path d="{smooth_path(pts)}" fill="{col}" transform="translate({f(dx)},{f(dy)})" '
                         f'filter="url(#{cv.blur(3 * hd.s)})"/>')
        g.append('</g>')
        cv.add("".join(g))

    def cap_path(self, hd):
        sh = Shell(hd, **self.shell_kw)
        hl = self.hairline
        k = self.cap.get("k", 1.04)
        yaw = math.degrees(hd.yaw)
        L, R = -90 - yaw, 90 - yaw
        pts = []
        n = 40
        for i in range(n + 1):
            lo = L + (R - L) * i / n
            pts.append(hd.proj(sh.pt(hl(lo), lo, k))[0])
        for i in range(1, 16):
            la = hl(R) + (90 - hl(R)) * i / 15
            pts.append(hd.proj(sh.pt(la, R, k))[0])
        for i in range(1, 16):
            la = 90 - (90 - hl(L)) * i / 15
            pts.append(hd.proj(sh.pt(la, L, k))[0])
        return smooth_path(pts)

    def draw_cap(self, cv, hd):
        """one smooth mass over the scalp above the hairline (sleek hair), with strands toward the bun"""
        sh = Shell(hd, **self.shell_kw)
        hl = self.hairline
        k = self.cap.get("k", 1.04)
        d = self.cap_path(hd)
        paint_volume(cv, d, self.base, self.dark, 70 * hd.s, lift=0.12, soft=0.1)
        kk = cv.clip(d)
        g = [f'<g clip-path="url(#{kk})">']
        tgt = self.cap.get("to", (60, 180))
        for i, lo in enumerate(range(-150, 151, 10)):
            la0 = hl(lo)
            sd = 1 if lo >= 0 else -1
            ctrl = [(la0, lo), (la0 + 18, lo * 0.9), (58, lo * 0.6 + sd * 40), (tgt[0] + 14, tgt[1] - sd * 30)]
            seg = []
            for j in range(16):
                t = j / 15
                # quadratic-ish blend through the controls
                idx = t * (len(ctrl) - 1)
                a = int(min(idx, len(ctrl) - 2))
                u = idx - a
                la = ctrl[a][0] + (ctrl[a + 1][0] - ctrl[a][0]) * u
                lon = ctrl[a][1] + (ctrl[a + 1][1] - ctrl[a][1]) * u
                p3 = sh.pt(la, lon, k + 0.005)
                if hd.rot(p3)[2] > 0:
                    seg.append(hd.proj(p3)[0])
            if len(seg) > 2:
                g.append(f'<path d="{smooth_path(seg, closed=False)}" fill="none" stroke="{self.light if i % 2 else self.dark}" '
                         f'stroke-width="{f(hd.s * 0.5)}" opacity="0.12"/>')
        # sheen band across the crown, toward the light
        band = [hd.proj(sh.pt(la, lo, k))[0] for la, lo in [(58, -60), (66, -20), (68, 20), (62, 60)]]
        lx, ly = LIGHT
        g.append(f'<path d="{smooth_path(band, closed=False)}" fill="none" stroke="{self.light}" stroke-width="{f(hd.s * 7)}" '
                 f'stroke-linecap="round" opacity="0.35" filter="url(#{cv.blur(hd.s * 3)})"/>')
        g.append('</g>')
        cv.add("".join(g))

    def front(self, cv, hd):
        if self.cap:
            self.draw_cap(cv, hd)
        for z, pts, c2, L in sorted(self._locks, key=lambda a: a[0]):
            if z >= L.get("split", 0):
                self.draw_lock(cv, hd, pts, c2, L)
        if self.bun and self.bun_z(hd) >= 0:
            self.draw_bun(cv, hd)


def cap_strips(hairline, part_lon=0.0, part_lat=86, step=15, w=9.0, k=1.03, size=22, skip=()):
    """locks covering the scalp: from the parting to the hairline, every `step` degrees of longitude."""
    out = []
    for lon in range(-180, 180, step):
        if any(a <= lon <= b for a, b in skip):
            continue
        lat_end = hairline(lon)
        mid = (part_lat + lat_end) / 2
        out.append(dict(pts=[('s', part_lat, part_lon + (lon - part_lon) * 0.15, k), ('s', mid + 8, lon * 0.85 + part_lon * 0.15, k + 0.02),
                             ('s', lat_end + 4, lon, k + 0.01), ('s', lat_end - 2, lon, k - 0.01)],
                        w=[2.0, w, w * 0.8, 0.4], size=size, sheen=0.6))
    return out


def hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    if len(pts) < 3:
        return pts
    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def curtain(lon0, lon1, lat_top, y_bot, rad, k=1.04):
    """a mass of hanging hair behind the head (a cylinder patch, seen as its convex outline)"""
    def fn(hd, sh):
        pts = []
        for i in range(13):
            lon = lon0 + (lon1 - lon0) * i / 12
            for la in range(int(lat_top), 91, 10):
                pts.append(hd.proj(sh.pt(la, lon, k))[0])
            lo = math.radians(lon)
            for j in range(7):
                y = sh.c[1] + (y_bot - sh.c[1]) * j / 6
                rr = rad * (0.9 + 0.1 * j / 6)
                p = (sh.c[0] + rr * math.sin(lo), y, sh.c[2] + rr * math.cos(lo) * sh.r[2] / sh.r[0])
                pts.append(hd.proj(p)[0])
        return hull(pts)
    return fn
