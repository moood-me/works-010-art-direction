"""person — one drawing routine for any figure of the cast: legs, clothes, arms, neck, head, in depth order."""
import math
from pix import paint_volume, smooth_path, mix, f, spline
from face import draw_head, make_head, expr
from body import Rig, sweep, section_pt, tube, chain, interp_r, hand, shoe, ground_shadow


def mirror(p, sd):
    return (p[0] * sd, p[1], p[2])


def sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def unit(v):
    l = math.sqrt(sum(a * a for a in v)) or 1
    return tuple(a / l for a in v)


def along(pts, t):
    """point at fraction t along a polyline (by index)"""
    n = len(pts) - 1
    k = min(n - 1, int(t * n))
    u = t * n - k
    return tuple(pts[k][i] + (pts[k + 1][i] - pts[k][i]) * u for i in range(3))


class HairSplit:
    """the back of the hair is drawn behind the body, the front with the head"""

    def __init__(self, hair):
        self.h = hair

    def back(self, cv, hd):
        self.h._locks = self.h.build(hd)

    def shadow(self, *a):
        self.h.shadow(*a)

    def front(self, cv, hd):
        self.h.front(cv, hd)


def joints(P, pose, shift=None):
    J = {}
    for k in ("sh", "el", "wr", "hip", "kn", "an"):
        J[k] = {sd: mirror(P[k], sd) for sd in (-1, 1)}
        J[k].update(pose.get(k, {}))
        if shift:
            J[k] = {sd: shift(p) for sd, p in J[k].items()}
    return J


def bender(bend):
    """a line of action: the whole figure is shifted sideways (x) and forward (z) by splines over the height y.
    bend = dict(x=[(y, dx), ...], z=[(y, dz), ...]); returns the shift of a 3D point, or None without a bend."""
    if not bend:
        return None
    bx, bz = bend.get("x"), bend.get("z")
    return lambda p: (p[0] + (spline(bx, p[1]) if bx else 0.0), p[1], p[2] + (spline(bz, p[1]) if bz else 0.0))


def draw_arm(cv, rig, P, J, sd, pose):
    c = P["head"]
    pts = chain([J["sh"][sd], J["el"][sd], J["wr"][sd]], 6)
    rr = interp_r(P["arm_r"], 6)
    sl = P.get("sleeve")
    hidden = sd in pose.get("hide_hand", ())
    e, w_ = J["el"][sd], J["wr"][sd]
    dv = unit(sub(w_, e))
    if not sl or sl.get("end", 1) < 1:
        tube(cv, rig, pts, rr, c["skin"], c["skin_sh"], lift=0.1, soft=0.1)
    if sl:
        end = sl.get("end", 1)
        n = max(2, int(round(end * (len(pts) - 1))) + 1)
        sp = pts[:n]
        sr = interp_r(sl["r"], 6)[:n]
        tube(cv, rig, sp, sr, sl["col"], sl["sh"], caps=(True, end < 1), lift=0.1, soft=0.1)
        if sl.get("cuff") and end >= 1:
            a = tuple(w_[i] - dv[i] * sl.get("cuff_len", 12) for i in range(3))
            cc = chain([a, w_], 2)
            tube(cv, rig, cc, [sl["r"][-1] * 1.02] * len(cc), sl["cuff"], sl["sh"], lift=0.12)
        if sl.get("roll") and end < 1:
            # a rolled sleeve: a band at its end
            a = along(pts, end)
            b = along(pts, max(0, end - 0.12))
            cc = chain([b, a], 2)
            tube(cv, rig, cc, [sl["r"][1] * 1.08] * len(cc), sl["roll"], sl["sh"], lift=0.12)
    if not hidden:
        H = P.get("hand", {})
        curl = pose.get("curl", H.get("curl", 0.4))
        if isinstance(curl, dict):      # per side
            curl = curl.get(sd, H.get("curl", 0.4))
        hand(cv, rig, tuple(w_[i] - dv[i] * 2 for i in range(3)), pose.get("hand_dir", {}).get(sd, dv),
             sd, c["skin"], c["skin_sh"], scale=H.get("scale", 1.0), curl=curl, fat=H.get("fat", 1.0),
             spread=pose.get("spread", {}).get(sd, 0.15), palm=pose.get("palm", {}).get(sd))


def draw_legs(cv, rig, P, J):
    c = P["head"]
    for sd in sorted((-1, 1), key=lambda sd: rig.depth(J["hip"][sd])):
        pts = chain([J["hip"][sd], J["kn"][sd], J["an"][sd]], 6)
        rr = interp_r(P["leg_r"], 6)
        cb = P.get("calf", 2.5)
        rr = [r + cb * math.sin(math.pi * min(1, max(0, (i - 6) / 5))) if i > 6 else r for i, r in enumerate(rr)]
        pa = P.get("pants")
        if not pa or pa.get("end", 1) < 1:
            tube(cv, rig, pts, rr, c["skin"], c["skin_sh"], lift=0.1, soft=0.1)
        if P.get("sock"):
            so = P["sock"]
            a = J["an"][sd]
            sk = chain([(a[0], a[1] - so.get("h", 20), a[2]), a], 2)
            tube(cv, rig, sk, [so["r"]] * len(sk), so["col"], so["sh"], caps=(False, False), lift=0.1)
        for m in P.get("leg_marks", []):
            m(cv, rig, sd, pts)
        if pa:
            end = pa.get("end", 1)
            n = max(2, int(round(end * (len(pts) - 1))) + 1)
            pr = interp_r(pa["r"], 6)[:n]
            tube(cv, rig, pts[:n], pr, pa["col"], pa["sh"], caps=(True, end < 1), lift=0.1, soft=0.1)
            if pa.get("cuff"):
                a = along(pts, min(end, 0.999))
                b = along(pts, max(0, end - 0.07))
                cc = chain([b, a], 2)
                tube(cv, rig, cc, [pa["r"][-1] * 1.12] * len(cc), pa["cuff"], pa["sh"], lift=0.12)
        sh = P["shoe"]
        a = J["an"][sd]
        turn = sh.get("turn", 0.12) * sd
        shoe(cv, rig, (a[0], sh["floor"], a[2] - sh.get("back", 6)), (math.sin(turn), math.cos(turn)), sh["len"], sh["wid"],
             sh["h"], sh["col"], sh["sh"], sole=sh.get("sole", "#3a2018"), sole_h=sh.get("sole_h", 1.6))


def draw_layer(cv, rig, L):
    d = sweep(rig, L["w"], L["zf"], L["zb"], L["y0"], L["y1"], n=L.get("n", 2.1), xoff=L.get("xoff"), zoff=L.get("zoff"))
    paint_volume(cv, d, L["col"], L["sh"], L.get("size", 110) * rig.s, lift=L.get("lift", 0.08), soft=0.1, rim=L.get("rim"))
    if L.get("deco"):
        k = cv.clip(d)
        cv.add(f'<g clip-path="url(#{k})">')
        L["deco"](cv, rig, L)
        cv.add('</g>')
    return d


def draw_neck(cv, rig, P):
    c = P["head"]
    top, base, r0, r1 = P["neck"]
    mid = tuple((top[i] + base[i]) / 2 for i in range(3))
    d = tube(cv, rig, [top, mid, base], [r0, (r0 + r1) / 2, r1], c["skin"], c["skin_sh"], caps=(False, False), lift=0.1,
             soft=0.1)
    k = cv.clip(d)
    hp = P.get("head_at", (0, 0, 0))
    hs = P.get("hs", 1.0)
    p0 = rig.P((hp[0], hp[1] + 50 * hs, hp[2] + 6))
    cv.add(f'<g clip-path="url(#{k})"><ellipse cx="{f(p0[0])}" cy="{f(p0[1])}" rx="{f(34 * rig.s * hs)}" ry="{f(15 * rig.s * hs)}" '
           f'fill="{mix(c["skin_sh"], "#7a3a30", 0.25)}" opacity="0.75" filter="url(#{cv.blur(4 * rig.s)})"/></g>')


def draw_person(cv, P, cx, cy, s, yaw=0.0, ex=None, pose=None, head_yaw=None, head_pitch=0.0, head_roll=0.0,
                shadow=True):
    """pose: joints by side (sh, el, wr, hip, kn, an), hide_hand, curl (a number or by side), by side: hand_dir,
    palm (where the palm looks), spread (of the fingers); head_at, and `bend` — a line of
    action (see bender); a character may carry a habitual one in P["bend"]. Hooks of a character, each a list of
    fn(cv, rig, pose): before_torso (behind the neck and the torso), after_torso, after_head; they find the joints
    in pose["_J"] and the bend in pose["_shift"]."""
    pose = dict(pose or {})
    rig = Rig(cx, cy, s, yaw)
    bend = pose.get("bend", P.get("bend"))
    shift = bender(bend)
    J = joints(P, pose, shift)
    pose["_J"], pose["_shift"] = J, shift or (lambda p: p)
    c = P["head"]
    hs = P.get("hs", 1.0)
    hp = pose.get("head_at", P.get("head_at", (0, 0, 0)))
    layers = P["layers"]
    if shift:
        hp = shift(hp)
        top, base, r0, r1 = P["neck"]
        P = dict(P, neck=(shift(top), shift(base), r0, r1), head_at=hp)
        layers = [dict(L, xoff=bend.get("x"), zoff=bend.get("z")) for L in layers]
    hy = yaw + (head_yaw or 0.0)
    if shadow:
        ground_shadow(cv, *rig.P((0, P["shoe"]["floor"], 0)), P.get("shadow_w", 70) * s, 12 * s)
    order = sorted((-1, 1), key=lambda sd: rig.depth(J["sh"][sd]))
    near = [sd for sd in order if rig.depth(J["sh"][sd]) > 12 or rig.depth(J["wr"][sd]) > 18]
    far = [sd for sd in order if sd not in near]
    hair = c.get("hair")
    hcx, hcy = rig.P(hp)
    hd = make_head(c, hcx, hcy, s * hs, yaw=hy, pitch=head_pitch, roll=head_roll)
    if hair:
        hair.back(cv, hd)
    draw_legs(cv, rig, P, J)
    for L in layers:
        if L.get("stage") == "low":
            draw_layer(cv, rig, L)
    for sd in far:
        draw_arm(cv, rig, P, J, sd, pose)
    for fn in P.get("before_torso", []):
        fn(cv, rig, pose)
    draw_neck(cv, rig, P)
    for L in layers:
        if L.get("stage", "torso") == "torso":
            draw_layer(cv, rig, L)
    for fn in P.get("after_torso", []):
        fn(cv, rig, pose)
    for sd in near:
        draw_arm(cv, rig, P, J, sd, pose)
    for L in layers:
        if L.get("stage") == "over":
            draw_layer(cv, rig, L)
    draw_head(cv, c, hcx, hcy, s * hs, yaw=hy, pitch=head_pitch, roll=head_roll, ex=ex,
              hair=HairSplit(hair) if hair else None)
    for fn in P.get("after_head", []):
        fn(cv, rig, pose)
    return rig
