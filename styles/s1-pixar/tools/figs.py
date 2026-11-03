"""figs — the figures of the cast (body, clothes, pose) around their heads."""
import math
from pix import Canvas, paint_volume, smooth_path, mix, f, spline
from face import draw_head, expr
from body import Rig, sweep, section_pt, tube, chain, interp_r, hand, shoe, ground_shadow
import cast


def neck(cv, rig, c, top=(0, 30, -6), base=(0, 92, -8), r=(9.0, 10.5)):
    pts = [top, ((top[0] + base[0]) / 2, (top[1] + base[1]) / 2, (top[2] + base[2]) / 2), base]
    d = tube(cv, rig, pts, [r[0], (r[0] + r[1]) / 2, r[1]], c["skin"], c["skin_sh"], caps=(False, False),
             lift=0.1, soft=0.1)
    # the head's shadow on the neck
    k = cv.clip(d)
    p0 = rig.P((0, 50, 6))
    cv.add(f'<g clip-path="url(#{k})"><ellipse cx="{f(p0[0])}" cy="{f(p0[1])}" rx="{f(34 * rig.s)}" ry="{f(14 * rig.s)}" '
           f'fill="{mix(c["skin_sh"], "#7a3a30", 0.25)}" opacity="0.75" filter="url(#{cv.blur(4 * rig.s)})"/></g>')


def arm_pts(sh, side, el, wr):
    return [sh, el, wr]


# ------------------------------------------------------------------ Аня

ANYA = dict(
    dress="#9fc0d8", dress_sh="#6e8fb0", cardi="#e8b04a", cardi_sh="#b77a2c", shoe="#8a4a32", shoe_sh="#5c2e20",
    sock="#f3ede4",
)


def anya_torso(rig, k):
    """sweep keys of Аня's cardigan / dress torso"""
    w = [(76, 12), (82, 28), (90, 40), (102, 46), (130, 43), (165, 39), (195, 37), (230, 42), (275, 50)]
    zf = [(72, 8), (88, 14), (120, 22), (150, 23), (175, 19), (200, 18), (240, 22), (275, 27)]
    zb = [(72, -8), (88, -16), (120, -19), (160, -17), (200, -17), (240, -21), (275, -25)]
    return w, zf, zb


def anya_figure(cv, cx, cy, s, yaw=0.0, ex=None, pose=None, bust=False, head_yaw=None, head_pitch=0.0, head_roll=0.0):
    c = cast.anya()
    A = ANYA
    rig = Rig(cx, cy, s, yaw)
    pose = pose or {}
    hy = yaw if head_yaw is None else head_yaw
    # joints
    shoulder = {sd: (sd * 34, 100, -4) for sd in (-1, 1)}
    elbow = {sd: (sd * 47, 186, -8) for sd in (-1, 1)}
    wrist = {sd: (sd * 49, 268, 2) for sd in (-1, 1)}
    elbow.update(pose.get("elbow", {}))
    wrist.update(pose.get("wrist", {}))
    hip = {sd: (sd * 15, 300, 0) for sd in (-1, 1)}
    knee = {sd: (sd * 12, 425, 3) for sd in (-1, 1)}
    ankle = {sd: (sd * 10, 548, -2) for sd in (-1, 1)}
    order = sorted((-1, 1), key=lambda sd: rig.depth(shoulder[sd]))
    if not bust:
        ground_shadow(cv, *rig.P((0, 567, 0)), 70 * s, 12 * s)
    # far arm behind the body
    def arm(sd):
        sl = chain([shoulder[sd], elbow[sd], wrist[sd]], 5)
        rr = interp_r([15, 13.5, 12.5], 5)
        tube(cv, rig, sl[:-1], rr[:-1], A["cardi"], A["cardi_sh"], caps=(True, False), lift=0.1, soft=0.1)
        e, w_ = elbow[sd], wrist[sd]
        dv = (w_[0] - e[0], w_[1] - e[1], w_[2] - e[2])
        l = math.sqrt(sum(a * a for a in dv))
        dv = tuple(a / l for a in dv)
        cuff_a = tuple(w_[i] - dv[i] * 15 for i in range(3))
        cuff = chain([cuff_a, w_], 2)
        tube(cv, rig, cuff, [12.8] * len(cuff), mix(A["cardi"], "#ffffff", 0.08), A["cardi_sh"], lift=0.12)
        hand(cv, rig, tuple(w_[i] - dv[i] * 3 for i in range(3)), dv, sd, c["skin"], c["skin_sh"], scale=1.05,
             curl=pose.get("curl", 0.4))
    def legs():
        for sd in sorted((-1, 1), key=lambda sd: rig.depth(hip[sd])):
            pts = chain([hip[sd], knee[sd], ankle[sd]], 6)
            rr = interp_r([16, 9.0, 5.8], 6)
            # calf bulge
            rr = [r + 3.0 * math.sin(math.pi * min(1, max(0, (i - 6) / 6))) if i > 6 else r for i, r in enumerate(rr)]
            tube(cv, rig, pts, rr, c["skin"], c["skin_sh"], lift=0.1, soft=0.1)
            # sock
            sk = chain([(ankle[sd][0], ankle[sd][1] - 22, ankle[sd][2]), ankle[sd]], 2)
            tube(cv, rig, sk, [6.0] * len(sk), A["sock"], "#cfc3b4", caps=(False, False), lift=0.1)
            shoe(cv, rig, (ankle[sd][0], 566, ankle[sd][2] - 6), (math.sin(sd * 0.12), math.cos(sd * 0.12)), 40, 9.6, 15,
                 A["shoe"], A["shoe_sh"], sole="#3a2018", sole_h=1.6)
    if not bust:
        legs()
    c["hair"].back_only = True
    # hair hanging behind everything
    from face import make_head
    hd = make_head(c, *rig.P((0, 0, 0)), s, yaw=hy, pitch=head_pitch, roll=head_roll)
    c["hair"].back(cv, hd)
    near = [sd for sd in order if rig.depth(shoulder[sd]) > -10]
    far = [sd for sd in order if sd not in near]
    # skirt
    if not bust:
        skw = [(220, 36), (250, 43), (300, 55), (380, 66), (470, 74)]
        skz = [(220, 17), (300, 30), (470, 46)]
        skb = [(220, -17), (300, -28), (470, -42)]
        d = sweep(rig, skw, skz, skb, 222, 470, n=2.0)
        paint_volume(cv, d, A["dress"], A["dress_sh"], 120 * s, lift=0.08, soft=0.1)
        # folds: soft vertical shadows
        k = cv.clip(d)
        g = [f'<g clip-path="url(#{k})">']
        for x in (-34, -12, 14, 38):
            p0 = rig.P(section_pt(skw, skz, skb, 300, x * 0.85))
            p1 = rig.P(section_pt(skw, skz, skb, 470, x))
            g.append(f'<path d="M{f(p0[0])},{f(p0[1])} L{f(p1[0])},{f(p1[1])}" stroke="{A["dress_sh"]}" stroke-width="{f(5 * s)}" '
                     f'opacity="0.5" filter="url(#{cv.blur(2.5 * s)})"/>')
        g.append('</g>')
        cv.add("".join(g))
    for sd in far:
        if bust:
            tube(cv, rig, chain([shoulder[sd], elbow[sd]], 4), interp_r([15, 13.5], 4), A["cardi"], A["cardi_sh"], lift=0.1)
        else:
            arm(sd)
    neck(cv, rig, c)
    # torso: dress top then the open cardigan
    w, zf, zb = anya_torso(rig, 0)
    d = sweep(rig, w, zf, zb, 78, 275, n=2.1)
    paint_volume(cv, d, A["cardi"], A["cardi_sh"], 110 * s, lift=0.08, soft=0.1)
    # the dress between the open fronts
    k = cv.clip(d)
    front = []
    for i in range(9):
        y = 78 + (276 - 78) * i / 8
        hw = 8 + 14 * (i / 8) ** 0.7
        front.append(rig.P(section_pt(w, zf, zb, y, -hw, lift=0.3)))
    for i in range(9):
        y = 276 - (276 - 78) * i / 8
        hw = 8 + 14 * ((8 - i) / 8) ** 0.7
        front.append(rig.P(section_pt(w, zf, zb, y, hw, lift=0.3)))
    dd = smooth_path(front)
    g = [f'<g clip-path="url(#{k})">']
    g.append(f'<path d="{dd}" fill="{A["dress"]}"/>')
    g.append(f'<path d="{dd}" fill="none" stroke="{A["cardi_sh"]}" stroke-width="{f(4 * s)}" opacity="0.6" filter="url(#{cv.blur(1.6 * s)})"/>')
    # knit ribbing at the cardigan edge
    for sd in (-1, 1):
        edge = [rig.P(section_pt(w, zf, zb, 78 + (276 - 78) * i / 8, sd * (8 + 14 * (i / 8) ** 0.7) + sd * 3, lift=0.5)) for i in range(9)]
        g.append(f'<path d="{smooth_path(edge, closed=False)}" fill="none" stroke="{mix(A["cardi"], "#fff6dc", 0.25)}" '
                 f'stroke-width="{f(5.5 * s)}" stroke-linecap="round" opacity="0.8"/>')
    # buttons on the near front
    for i in range(4):
        y = 120 + 30 * i
        p = rig.P(section_pt(w, zf, zb, y, -(8 + 14 * ((y - 78) / 198) ** 0.7) - 4, lift=1))
        g.append(f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(2.4 * s)}" fill="#f6efe0"/>')
    # collar of the dress: a small rounded collar
    for sd in (-1, 1):
        col = [rig.P(section_pt(w, zf, zb, y, x, lift=1.0)) for x, y in
               [(sd * 1, 80), (sd * 10, 77), (sd * 15, 82), (sd * 11, 92), (sd * 3, 90)]]
        g.append(f'<path d="{smooth_path(col)}" fill="#fbf7f0"/>')
    g.append('</g>')
    cv.add("".join(g))
    for sd in near:
        if bust:
            tube(cv, rig, chain([shoulder[sd], elbow[sd]], 4), interp_r([15, 13.5], 4), A["cardi"], A["cardi_sh"], lift=0.1)
        else:
            arm(sd)
    hd = draw_head(cv, c, *rig.P((0, 0, 0)), s, yaw=hy, pitch=head_pitch, roll=head_roll, ex=ex, hair=_FrontOnly(c["hair"]))
    return rig


class _FrontOnly:
    """the hair's back part was already drawn behind the body"""

    def __init__(self, hair):
        self.h = hair

    def shadow(self, *a):
        self.h.shadow(*a)

    def back(self, cv, hd):
        self.h._locks = self.h.build(hd)

    def front(self, cv, hd):
        self.h.front(cv, hd)
