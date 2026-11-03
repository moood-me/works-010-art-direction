"""cast — the four characters as data for face.py / body.py."""
import math
from face import Hair, cap_strips, curtain
from pix import spline

# ------------------------------------------------------------------ shared head shapes

def woman_head(**kw):
    c = dict(
        w=[(-50, 0), (-47, 18), (-40, 32), (-30, 40), (-18, 43.5), (-5, 43), (5, 41), (15, 38), (25, 33),
           (33, 27), (40, 20.5), (45, 14), (48.5, 7), (50, 0)],
        zf=[(-50, -4), (-46, 14), (-40, 26), (-30, 34), (-18, 37.5), (-5, 37), (5, 34), (15, 34.5), (25, 34),
            (35, 33), (42, 30), (47, 24), (50, 12)],
        zb=[(-50, -4), (-44, -24), (-35, -38), (-20, -45), (-5, -46), (10, -40), (20, -28), (30, -14), (40, -5),
            (50, 0)],
        n=2.35,
        eye_x=18.0, eye_y=2.0, eye_w=21.5, eye_h=13.5, iris=7.6, eye_tilt=1.2, eye_peak=0.2,
        brow_h=14.5, brow_len=21, brow_w=2.6, brow_arch=2.6,
        nose_y=22.0, nose_w=5.2,
        mouth_y=34.0, mouth_w=18.0, lip_up=2.4, lip_low=4.0,
        lid_w=1.4, wing=0.9, crease=4.4,
    )
    c["bumps"] = [
        (0, 8, 3.2, 9, 2.0),        # bridge
        (0, 19.5, 4.4, 4.6, 8.5),   # tip
        (-4.6, 21.5, 2.8, 2.6, 2.4), (4.6, 21.5, 2.8, 2.6, 2.4),   # wings
        (0, 30.5, 8.0, 2.3, 1.6),   # upper lip
        (0, 36.5, 6.5, 2.4, 2.0),   # lower lip
        (0, 44.5, 7.5, 3.8, 1.2),   # chin
        (-17, -8, 10, 3.5, 1.4), (17, -8, 10, 3.5, 1.4),          # brow ridge
        (-24, 16, 8, 7, 2.2), (24, 16, 8, 7, 2.2),                 # cheeks
        (-17.5, 2, 8.5, 5, -2.6), (17.5, 2, 8.5, 5, -2.6),        # sockets
    ]
    c.update(kw)
    return c


# ------------------------------------------------------------------ Аня

def anya():
    c = woman_head(
        skin="#f5c9a8", skin_sh="#d98f78", blush="#f0857c", blush_a=0.3, lip="#d8706e", rim="#ffd9c4",
        iris_col="#5f8f5a", brow_col="#7a3c26", lash="#2e1712", nostril="#9b4a3c", ear_in="#e07c68",
        iris=8.0, eye_w=22, eye_h=14.5, brow_arch=2.4, brow_w=2.6, blush_x=25, blush_y=21,
    )
    c["hair"] = anya_hair()
    return c


def hl_long(lon):
    a = abs(((lon + 180) % 360) - 180)
    return 28 - 62 * (a / 180) ** 1.3


def wave_lock(root, mid, side_lon, y0, y1, rad0, rad1, amp, n, w0, wmax, z=None, split=None, size=22, tipcurl=0, ph=0.0,
              col=None):
    """a lock: from the shell (root, mid on shell) down a cylinder with a wave."""
    pts = [('s',) + root, ('s',) + mid]
    ws = [w0, wmax * 0.85]
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        lon = side_lon + amp * math.sin(ph + t * math.pi * 2.2) + tipcurl * t ** 3
        rad = rad0 + (rad1 - rad0) * t
        pts.append(('c', lon, y, rad))
        ws.append(wmax * (1 - 0.15 * t) if i < n else 0.3)
    L = dict(pts=pts, w=ws, size=size)
    if z is not None:
        L["z"] = z
    if split is not None:
        L["split"] = split
    if col:
        L["col"] = col
    return L


def hl_anya(lon):
    a = abs(((lon + 180) % 360) - 180)
    # forehead (lat ~30), temples, behind the ears, nape
    return 30 - 22 * (a / 90) ** 1.6 if a < 90 else 8 - 40 * ((a - 90) / 90) ** 0.9


def anya_hair():
    part = 14
    locks = cap_strips(hl_anya, part_lon=part, step=15, w=10, size=24, k=1.05, skip=[(-60, 60)])
    # hanging masses in front of the shoulders, behind the ears
    for i, (sd, lon) in enumerate([(-1, -92), (-1, -108), (1, 94), (1, 110)]):
        locks.append(wave_lock((40, lon * 0.85, 1.06), (5, lon, 1.08), lon, 16, 104 + 10 * (i % 2), 46, 52, 6, 4,
                               5, 13, size=34, ph=1.2 * i, tipcurl=sd * 6))
    # the lock that frames the face: from the parting across the forehead, down the cheek
    locks.append(dict(pts=[('s', 86, part, 1.05), ('s', 62, -8, 1.09), ('s', 40, -28, 1.10), ('s', 14, -56, 1.09),
                           ('c', -76, 14, 46), ('c', -74, 40, 47), ('c', -82, 66, 49), ('c', -76, 92, 49), ('c', -82, 108, 47)],
                      w=[3, 16, 15, 12, 10.5, 10, 9, 6, 0.4], size=30))
    locks.append(dict(pts=[('s', 84, part, 1.04), ('s', 52, 34, 1.08), ('s', 26, 56, 1.09),
                           ('c', 80, 16, 46), ('c', 78, 42, 47), ('c', 86, 70, 49), ('c', 80, 96, 48), ('c', 86, 106, 46)],
                      w=[3, 15, 12, 10, 9.5, 8.5, 6, 0.4], size=30))
    # top: two wide sweeps from the parting
    locks.append(dict(pts=[('s', 88, part + 40, 1.04), ('s', 70, -10, 1.08), ('s', 48, -40, 1.10), ('s', 30, -62, 1.09)],
                      w=[4, 16, 14, 0.5], size=28, z=-2))
    locks.append(dict(pts=[('s', 88, part - 30, 1.04), ('s', 68, 40, 1.08), ('s', 44, 62, 1.09), ('s', 28, 74, 1.08)],
                      w=[4, 14, 12, 0.5], size=28, z=-2))
    # back: hanging locks over a mass
    for i, lon in enumerate(range(115, 250, 22)):
        locks.append(wave_lock((40, lon, 1.06), (10, lon, 1.08), lon, 16, 112 + 6 * (i % 2), 48, 52, 5, 4, 5, 12,
                               size=32, ph=i * 0.8, z=-80))
    back = [curtain(90, 270, 10, 110, 50)]
    return Hair("#8a4126", "#56241a", "#e8a06a", locks, back_mass=back, sheen_a=0.3)


# ------------------------------------------------------------------ figures

from pix import smooth_path as _sp, mix as _mix, f as _f
from body import section_pt as _spt


def _front_panel(L, rig, y0, y1, hw0, hw1, lift=0.3):
    w, zf, zb = L["w"], L["zf"], L["zb"]
    pts = []
    for i in range(9):
        y = y0 + (y1 - y0) * i / 8
        hw = hw0 + (hw1 - hw0) * (i / 8) ** 0.7
        pts.append(rig.P(_spt(w, zf, zb, y, -hw, lift=lift)))
    for i in range(9):
        y = y1 - (y1 - y0) * i / 8
        hw = hw0 + (hw1 - hw0) * ((8 - i) / 8) ** 0.7
        pts.append(rig.P(_spt(w, zf, zb, y, hw, lift=lift)))
    return pts


def anya_person():
    c = anya()
    A = dict(dress="#9fc0d8", dress_sh="#6e8fb0", cardi="#e8b04a", cardi_sh="#b77a2c")

    def skirt_deco(cv, rig, L):
        for x in (-34, -12, 14, 38):
            p0 = rig.P(_spt(L["w"], L["zf"], L["zb"], 300, x * 0.85))
            p1 = rig.P(_spt(L["w"], L["zf"], L["zb"], 470, x))
            cv.add(f'<path d="M{_f(p0[0])},{_f(p0[1])} L{_f(p1[0])},{_f(p1[1])}" stroke="{A["dress_sh"]}" '
                   f'stroke-width="{_f(5 * rig.s)}" opacity="0.45" filter="url(#{cv.blur(2.5 * rig.s)})"/>')

    def cardi_deco(cv, rig, L):
        s = rig.s
        pts = _front_panel(L, rig, 78, 276, 8, 22)
        d = _sp(pts)
        cv.add(f'<path d="{d}" fill="{A["dress"]}"/>')
        cv.add(f'<path d="{d}" fill="none" stroke="{A["cardi_sh"]}" stroke-width="{_f(4 * s)}" opacity="0.6" filter="url(#{cv.blur(1.6 * s)})"/>')
        for sd in (-1, 1):
            edge = [rig.P(_spt(L["w"], L["zf"], L["zb"], 78 + 198 * i / 8, sd * (8 + 14 * (i / 8) ** 0.7) + sd * 3, lift=0.5)) for i in range(9)]
            cv.add(f'<path d="{_sp(edge, closed=False)}" fill="none" stroke="{_mix(A["cardi"], "#fff6dc", 0.25)}" '
                   f'stroke-width="{_f(5.5 * s)}" stroke-linecap="round" opacity="0.8"/>')
        for i in range(4):
            y = 120 + 30 * i
            p = rig.P(_spt(L["w"], L["zf"], L["zb"], y, -(8 + 14 * ((y - 78) / 198) ** 0.7) - 4, lift=1))
            cv.add(f'<circle cx="{_f(p[0])}" cy="{_f(p[1])}" r="{_f(2.4 * s)}" fill="#f6efe0"/>')
        for sd in (-1, 1):
            col = [rig.P(_spt(L["w"], L["zf"], L["zb"], y, x, lift=1.0)) for x, y in
                   [(sd * 1, 80), (sd * 10, 77), (sd * 15, 82), (sd * 11, 92), (sd * 3, 90)]]
            cv.add(f'<path d="{_sp(col)}" fill="#fbf7f0"/>')

    return dict(
        head=c, hs=1.0,
        neck=((0, 30, -6), (0, 92, -8), 9.0, 10.5),
        sh=(34, 100, -4), el=(47, 186, -8), wr=(49, 268, 2), hip=(15, 300, 0), kn=(12, 425, 3), an=(10, 548, -2),
        arm_r=[10, 7.5, 5.5], sleeve=dict(r=[15, 13.5, 12.5], col=A["cardi"], sh=A["cardi_sh"],
                                           cuff=_mix(A["cardi"], "#ffffff", 0.08), cuff_len=15),
        leg_r=[16, 9.0, 5.8], calf=3.0, sock=dict(r=6.0, col="#f3ede4", sh="#cfc3b4", h=22),
        shoe=dict(floor=566, len=40, wid=9.6, h=15, col="#8a4a32", sh="#5c2e20", back=6),
        hand=dict(scale=1.05, curl=0.4),
        layers=[
            dict(stage="low", w=[(220, 36), (250, 43), (300, 55), (380, 66), (470, 74)], zf=[(220, 17), (300, 30), (470, 46)],
                 zb=[(220, -17), (300, -28), (470, -42)], y0=222, y1=470, n=2.0, col=A["dress"], sh=A["dress_sh"],
                 size=120, deco=skirt_deco),
            dict(w=[(76, 12), (82, 28), (90, 40), (102, 46), (130, 43), (165, 39), (195, 37), (230, 42), (275, 50)],
                 zf=[(72, 8), (88, 14), (120, 22), (150, 23), (175, 19), (200, 18), (240, 22), (275, 27)],
                 zb=[(72, -8), (88, -16), (120, -19), (160, -17), (200, -17), (240, -21), (275, -25)],
                 y0=78, y1=275, col=A["cardi"], sh=A["cardi_sh"], deco=cardi_deco),
        ],
    )


# ------------------------------------------------------------------ accessories on a face

def glasses(shape="round", col="#5a4632", lift=7.0, cy=None, rx=8.5, ry=7.5, bridge_y=None, lens="#dfe8ee",
            width=0.9, temple=True):
    """spectacles floating in front of the eyes; drawn after the face"""
    def fn(cv, hd, ex, c=None):
        cc = fn.c
        s = hd.s
        yc = cc["eye_y"] + (cy or 0)
        rings = []
        for sd in (-1, 1):
            x0 = cc["eye_x"] * sd
            pts = []
            for i in range(28):
                a = 2 * math.pi * i / 28
                if shape == "round":
                    x, y = math.cos(a) * rx, math.sin(a) * ry
                else:   # soft rectangle
                    ca, sa = math.cos(a), math.sin(a)
                    k = 4.0
                    x = rx * math.copysign(abs(ca) ** (2 / k), ca)
                    y = ry * math.copysign(abs(sa) ** (2 / k), sa)
                pts.append((x0 + x, yc + y))
            rings.append((sd, pts))
        for sd, pts in rings:
            if hd.fore(cc["eye_x"] * sd, yc) < 0.12:
                continue
            q = [hd.P(x, y, lift=lift) for x, y in pts]
            d = _sp(q)
            cv.add(f'<path d="{d}" fill="{lens}" opacity="0.18"/>')
            # a glint across the lens
            g0 = hd.P(cc["eye_x"] * sd - rx * 0.5, yc - ry * 0.2, lift=lift)
            g1 = hd.P(cc["eye_x"] * sd - rx * 0.1, yc - ry * 0.7, lift=lift)
            cv.add(f'<path d="M{_f(g0[0])},{_f(g0[1])}L{_f(g1[0])},{_f(g1[1])}" stroke="#ffffff" stroke-width="{_f(s * 1.6)}" '
                   f'stroke-linecap="round" opacity="0.45"/>')
            cv.add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{_f(s * width)}"/>')
        # bridge
        by = yc - ry * 0.25 if bridge_y is None else bridge_y
        b = [hd.P(-cc["eye_x"] + rx * 0.92, by, lift=lift), hd.P(0, by - 1.5, lift=lift + 2), hd.P(cc["eye_x"] - rx * 0.92, by, lift=lift)]
        cv.add(f'<path d="{_sp(b, closed=False)}" fill="none" stroke="{col}" stroke-width="{_f(s * width)}"/>')
        # temples toward the ears, when seen
        if temple:
            for sd in (-1, 1):
                a3 = hd.surf(cc["eye_x"] * sd + sd * rx, yc - ry * 0.3, lift)
                e3 = (sd * (hd.width(cc.get("ear_y", 8)) + 1), cc.get("ear_y", 8) - 5, -6)
                pa, za = hd.proj(a3)
                pe, ze = hd.proj(e3)
                if -sd * math.sin(hd.yaw) > 0.25:
                    cv.add(f'<path d="M{_f(pa[0])},{_f(pa[1])}L{_f(pe[0])},{_f(pe[1])}" stroke="{col}" stroke-width="{_f(s * width)}"/>')
    fn.c = None
    return fn


def strand_shape(cv, hd, pts_front, lift, col, dark, light, size, strands=5):
    """a soft shape on the face (mustache, brows of an old man) painted with strands"""
    from pix import paint_volume
    q = [hd.P(x, y, lift=lift) for x, y in pts_front]
    d = _sp(q)
    paint_volume(cv, d, col, dark, size * hd.s, lift=0.14, soft=0.1)
    k = cv.clip(d)
    xs = [p[0] for p in pts_front]
    ys = [p[1] for p in pts_front]
    g = [f'<g clip-path="url(#{k})">']
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    for i in range(strands * 4):
        t = (i + 0.5) / (strands * 4)
        x = x0 + (x1 - x0) * t
        sd = 1 if x > (x0 + x1) / 2 else -1
        a = hd.P(x * 0.9, y0 + 0.5, lift=lift + 0.5)
        b = hd.P(x * 1.05 + sd * 1.5, y1 - 0.5, lift=lift + 0.5)
        g.append(f'<path d="M{_f(a[0])},{_f(a[1])}L{_f(b[0])},{_f(b[1])}" stroke="{light if i % 2 else dark}" '
                 f'stroke-width="{_f(hd.s * 0.45)}" opacity="0.45"/>')
    g.append('</g>')
    cv.add("".join(g))


# ------------------------------------------------------------------ Тим

def hl_short(lon):
    a = abs(((lon + 180) % 360) - 180)
    return 32 - 30 * (a / 90) ** 1.5 if a < 90 else 2 - 30 * ((a - 90) / 90) ** 0.8


def tim():
    c = dict(
        w=[(-50, 0), (-46, 21), (-38, 36), (-25, 44), (-10, 46.5), (5, 45.5), (15, 42.5), (25, 37.5), (33, 31),
           (40, 24), (45.5, 15), (48.8, 7), (50, 0)],
        zf=[(-50, -4), (-45, 16), (-38, 29), (-25, 38), (-10, 40), (2, 37), (14, 37), (24, 37), (34, 36),
            (42, 32), (47, 25), (50, 12)],
        zb=[(-50, -4), (-44, -26), (-35, -41), (-20, -48), (-5, -48), (10, -42), (20, -30), (30, -16), (40, -6), (50, 0)],
        n=2.3,
        eye_x=18.5, eye_y=7.0, eye_w=21.0, eye_h=15.5, iris=7.8, eye_tilt=0.4, eye_peak=0.0,
        brow_h=13.5, brow_len=19, brow_w=3.4, brow_arch=1.4,
        nose_y=25.5, nose_w=5.4, nose_sh=0.5,
        mouth_y=36.5, mouth_w=19.0, lip_up=1.6, lip_low=2.8, lips_soft=True, gap_tooth=True, mouth_open_max=10,
        lid_w=1.0, wing=0.0, crease=3.8, lower_a=0.35,
        skin="#f3c7a2", skin_sh="#d88c70", blush="#ef7d6e", blush_a=0.42, lip="#d27a70", rim="#ffdcc6",
        iris_col="#6f4a2a", brow_col="#9a5f2c", lash="#3a2216", nostril="#a0503e", ear_in="#e8806a",
        ear_h=19, ear_wd=13, ear_y=12, blush_x=26, blush_y=24,
    )
    c["bumps"] = [
        (0, 14, 3.0, 8, 1.0), (0, 22.5, 4.6, 4.4, 7.0), (-4.4, 24.5, 2.8, 2.5, 2.0), (4.4, 24.5, 2.8, 2.5, 2.0),
        (0, 33.5, 8.0, 2.3, 1.2), (0, 39.5, 7.0, 2.4, 1.6), (0, 46, 8, 3.5, 1.0),
        (-26, 22, 9, 8, 3.0), (26, 22, 9, 8, 3.0), (-18.5, 7, 8.5, 5, -2.2), (18.5, 7, 8.5, 5, -2.2),
    ]
    import random
    rnd = random.Random(7)
    c["spots"] = [(sd * (8 + rnd.random() * 18), 15 + rnd.random() * 13, 0.55 + rnd.random() * 0.4, "#b8683e", 0.55)
                  for sd in (-1, 1) for _ in range(9)]
    c["hair"] = tim_hair()
    return c


def tim_hair():
    locks = []
    whorl = (68, 165)
    # strips from the crown whorl to the hairline, all around
    for lon in range(-180, 180, 18):
        a = abs(((lon + 180) % 360) - 180)
        lat_end = hl_short(lon)
        front = a < 80
        tip_lift = 1.18 if front else 1.1
        mid_lon = lon + (12 if lon > 0 else -12) * (1 if front else 0)
        pts = [('s', whorl[0], whorl[1], 1.06), ('s', (whorl[0] + lat_end) / 2 + 14, lon * 0.92, 1.12),
               ('s', lat_end + 6, mid_lon, 1.10), ('s', lat_end - 4, mid_lon + (8 if lon >= 0 else -8), tip_lift)]
        locks.append(dict(pts=pts, w=[3, 11, 9.5, 0.4], size=26, sheen=0.9))
    # fringe: tufts over the forehead with sharp tips pointing every which way
    for lon, tilt, ln in [(-34, -14, 14), (-14, -6, 18), (6, 10, 16), (24, 16, 14), (42, 18, 11)]:
        locks.append(dict(pts=[('s', 62, lon * 0.6, 1.12), ('s', 44, lon, 1.14), ('s', 32, lon + tilt * 0.5, 1.12),
                               ('s', 32 - ln, lon + tilt, 1.08)], w=[3, 10, 8, 0.4], size=24))
    # cowlick at the crown, sticking up
    locks.append(dict(pts=[('s', 70, 175, 1.08), ('s', 80, 160, 1.18), ('s', 84, 130, 1.26), ('s', 80, 108, 1.28)],
                      w=[5, 6, 3.5, 0.3], size=14, z=40))
    locks.append(dict(pts=[('s', 70, 150, 1.08), ('s', 80, 185, 1.17), ('s', 80, 215, 1.22)],
                      w=[5, 5, 0.3], size=12, z=40))
    return Hair("#c9873a", "#8a5222", "#f6cf86", locks, sheen_a=0.32)


# ------------------------------------------------------------------ Савелий Петрович

def hl_bald(lon):
    a = abs(((lon + 180) % 360) - 180)
    return 25 - 10 * (a / 180)


def savely():
    c = dict(
        w=[(-50, 0), (-46, 19), (-40, 31), (-30, 38.5), (-18, 41.5), (-5, 42), (5, 42.5), (15, 43), (25, 42.5),
           (33, 40), (40, 34), (45.5, 25), (49, 13), (50, 0)],
        zf=[(-50, -4), (-45, 16), (-38, 28), (-25, 36), (-10, 38), (2, 35), (14, 36), (24, 38), (34, 37),
            (42, 34), (47, 28), (50, 15)],
        zb=[(-50, -4), (-44, -24), (-35, -38), (-20, -45), (-5, -46), (10, -41), (20, -30), (30, -17), (40, -7), (50, 0)],
        n=2.5,
        eye_x=17.0, eye_y=4.0, eye_w=17.5, eye_h=10.5, iris=5.6, eye_tilt=-1.0, eye_peak=0.35,
        brow_h=8.5, brow_len=23, brow_w=5.2, brow_arch=1.5,
        nose_y=24.0, nose_w=8.5, nose_sh=0.6,
        mouth_y=39.0, mouth_w=17.0, lip_up=1.2, lip_low=3.0, lips_soft=True,
        lid_w=0.9, wing=0.0, crease=4.6, lower_a=0.5, bags=0.45,
        skin="#efbc9a", skin_sh="#c97d66", blush="#e0705e", blush_a=0.42, lip="#c06a62", rim="#ffd6c2",
        iris_col="#5e7f96", brow_col="#e9e5de", lash="#4a3027", nostril="#8a3e32", ear_in="#d96e5e",
        ear_h=24, ear_wd=13, ear_y=10, blush_x=26, blush_y=22, socket=0.45,
    )
    c["bumps"] = [
        (0, 10, 3.6, 9, 2.5), (0, 21.5, 7.0, 6.0, 12.0), (-6.5, 24.5, 3.6, 3.2, 3.5), (6.5, 24.5, 3.6, 3.2, 3.5),
        (0, 36.5, 9.0, 2.4, 1.0), (0, 42, 8.0, 2.6, 1.5), (0, 47, 9, 3.5, 1.2),
        (-26, 20, 9, 9, 3.0), (26, 20, 9, 9, 3.0), (-17, 4, 8, 5, -2.8), (17, 4, 8, 5, -2.8),
        (-17, -6, 10, 3.5, 2.5), (17, -6, 10, 3.5, 2.5), (-30, 36, 8, 8, 2.0), (30, 36, 8, 8, 2.0),
    ]
    c["lines"] = [
        ([(-12, -22), (0, -23.5), (12, -22)], 0.35), ([(-9, -17.5), (0, -18.8), (9, -17.5)], 0.3),   # forehead
        ([(-27, 0), (-29.5, 4), (-28, 8)], 0.55), ([(27, 0), (29.5, 4), (28, 8)], 0.55),                # crow's feet
        ([(-28.5, -1.5), (-31.5, 1)], 0.4), ([(28.5, -1.5), (31.5, 1)], 0.4),
        ([(-10.5, 20), (-15, 31), (-17, 40)], 0.5), ([(10.5, 20), (15, 31), (17, 40)], 0.5),           # nasolabial
        ([(-2.5, -9), (-3, -4)], 0.35), ([(2.5, -9), (3, -4)], 0.35),                                     # frown lines
    ]
    c["spots"] = [(-24, -18, 1.6, "#c98a68", 0.35), (20, -30, 1.2, "#c98a68", 0.3), (30, 14, 1.0, "#c98a68", 0.3)]
    gl = glasses(shape="round", col="#8a6a3a", lift=10, cy=7.5, rx=8.2, ry=6.8, width=0.9)
    gl.c = c

    def over(cv, hd, ex):
        # mustache: a soft walrus shape under the nose
        my = c["nose_y"] + 4.5
        sm = ex["smile"] * 2 - ex["frown"] * 1.5
        pts = [(0, my - 0.5), (5, my - 1.5), (11, my + 0.5), (17, my + 6 - sm), (19, my + 11 - sm), (14, my + 9 - sm),
               (8, my + 8), (2, my + 7.5), (0, my + 7), (-2, my + 7.5), (-8, my + 8), (-14, my + 9 - sm), (-19, my + 11 - sm),
               (-17, my + 6 - sm), (-11, my + 0.5), (-5, my - 1.5)]
        strand_shape(cv, hd, pts, 3.0, "#e6e1d8", "#a69c90", "#ffffff", 18, strands=6)
        gl(cv, hd, ex)
    c["extra_face"] = over
    c["hair"] = savely_hair()
    return c


def savely_hair():
    locks = []
    # white hair only around the back and over the ears: fluffy clumps that stick out
    for sd in (-1, 1):
        for j, (lon, lat, out) in enumerate([(62, 20, 1.30), (80, 22, 1.36), (100, 20, 1.34), (122, 16, 1.28),
                                            (145, 12, 1.22), (168, 10, 1.18)]):
            lo = sd * lon
            locks.append(dict(pts=[('s', lat + 14, lo - sd * 6, 1.0), ('s', lat + 4, lo, 1.12), ('s', lat - 6, lo + sd * 8, out),
                                   ('s', lat - 12, lo + sd * 16, out - 0.05)],
                              w=[7, 11, 9, 4], size=18, sheen=0.8, z=(-1 if lon > 95 else 1) * 10))
        for j, (lon, lat) in enumerate([(70, 2), (95, 0), (125, -4), (155, -8)]):
            lo = sd * lon
            locks.append(dict(pts=[('s', lat + 12, lo, 1.0), ('s', lat, lo + sd * 3, 1.12), ('s', lat - 10, lo + sd * 10, 1.2)],
                              w=[6, 9, 4], size=15, sheen=0.7, z=-20))
    # three wisps across the top
    for lon, ln in [(-26, 40), (-8, 46), (12, 40)]:
        locks.append(dict(pts=[('s', 45, -80, 1.0), ('s', 74, lon - 26, 1.03), ('s', 80, lon + 16, 1.05), ('s', 70, lon + ln, 1.08)],
                          w=[0.6, 1.4, 1.0, 0.2], size=5, sheen=0.4, strands=0))
    return Hair("#efebe4", "#aaa298", "#ffffff", locks, sheen_a=0.25)


# ------------------------------------------------------------------ Вера

def hl_bun(lon):
    a = abs(((lon + 180) % 360) - 180)
    return 36 - 10 * (a / 45) ** 1.2 if a < 45 else (26 - 26 * ((a - 45) / 45) ** 1.3 if a < 90 else 0 - 28 * ((a - 90) / 90) ** 0.8)


def vera():
    c = woman_head(
        w=[(-50, 0), (-47, 16.5), (-40, 29.5), (-30, 37), (-18, 40), (-5, 40), (5, 39), (15, 36.5), (25, 31.5),
           (33, 25), (40, 18), (45, 11.5), (48.5, 5), (50, 0)],
        skin="#eec2a6", skin_sh="#c88672", blush="#d9786e", blush_a=0.22, lip="#a63e4c", rim="#ffd8c8",
        iris_col="#5b4434", brow_col="#2c201c", lash="#1e1412", nostril="#8a4038", ear_in="#d97a6a",
        eye_x=17.5, eye_y=1.0, eye_w=20, eye_h=12.5, iris=7.0, eye_tilt=1.8, eye_peak=0.3,
        brow_h=13.5, brow_len=21, brow_w=1.9, brow_arch=3.6,
        nose_y=24.0, nose_w=4.8, nose_sh=0.6,
        mouth_y=35.5, mouth_w=16.5, lip_up=2.0, lip_low=3.0,
        lid_w=1.5, wing=1.3, crease=4.2, bags=0.38,
    )
    c["bumps"] = [
        (0, 9, 3.0, 10, 3.2), (0, 21.5, 4.0, 4.8, 9.0), (-4.2, 23.5, 2.6, 2.5, 2.0), (4.2, 23.5, 2.6, 2.5, 2.0),
        (0, 32, 7.5, 2.2, 1.4), (0, 38, 6.5, 2.3, 1.6), (0, 45.5, 7, 3.5, 1.4),
        (-17, -8, 10, 3.5, 1.4), (17, -8, 10, 3.5, 1.4), (-26, 9, 7, 5, 2.4), (26, 9, 7, 5, 2.4),
        (-17.5, 1, 8, 5, -2.8), (17.5, 1, 8, 5, -2.8),
    ]
    c["lines"] = [([(-10.5, 22), (-13.5, 30), (-15, 37)], 0.25), ([(10.5, 22), (13.5, 30), (15, 37)], 0.25),
                  ([(-2.2, -9), (-2.5, -5)], 0.25)]
    gl = glasses(shape="rect", col="#2a1f1c", lift=8, cy=1.0, rx=10.5, ry=7.0, width=1.0)
    gl.c = c
    c["extra_face"] = lambda cv, hd, ex: gl(cv, hd, ex)
    c["hair"] = vera_hair()
    return c


def vera_hair():
    locks = []
    bun = (14, 180)
    # a grey streak from the parting, on the screen-left
    locks.append(dict(pts=[('s', 29, -20, 1.045), ('s', 42, -22, 1.06), ('s', 62, -40, 1.065), ('s', 50, -130, 1.06),
                           ('s', 24, -168, 1.05)], w=[3, 4.5, 5, 4, 1], size=20, col="#9a928c", dark="#615a55", sheen=0.8, z=30))
    # one loose lock by the temple: tired
    locks.append(dict(pts=[('s', 24, 40, 1.04), ('s', 12, 55, 1.07), ('s', -4, 60, 1.08), ('s', -18, 56, 1.07)],
                      w=[2, 3, 2.5, 0.3], size=10, z=30))
    return Hair("#3e2c27", "#1d1412", "#8e6e60", locks, sheen_a=0.35, bun=dict(lat=bun[0], lon=bun[1], r=17, k=1.25),
                cap=dict(k=1.07, to=(30, 180)), hairline=hl_bun)
