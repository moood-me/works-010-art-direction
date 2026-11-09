"""marat — Марат, the cook: head, curls and beard, body, clothes and props, as data for face.py / body.py / person.py."""
import math
from face import Hair, scalp_curls, jaw_curls, mouth_curves
from pix import spline, smooth_path as _sp, mix as _mix, f as _f, paint_volume
import cloth

M = dict(white="#f6efe2", white_sh="#c2ac93", terra="#cf6a3c", terra_sh="#8f3d22", pants="#5b4b45", pants_sh="#33282a",
         steel="#c9ccd0", steel_sh="#7c8088")
HAIR = ("#3d2a22", "#170e0c", "#9a7258")


def hl_marat(lon):
    """a low, wide hairline that stays above the ears"""
    a = abs(((lon + 180) % 360) - 180)
    return 31 - 20 * (a / 80) ** 1.6 if a < 80 else 11 - 54 * ((a - 80) / 100) ** 0.8


BEARD_R = [(-10, 43), (0, 44), (10, 45), (20, 45.5), (30, 44.5), (40, 41), (48, 35.5), (56, 27), (62, 17), (70, 8)]


def beard_rad(y):
    return spline(BEARD_R, y)


def beard_inside(a, y):
    if y < 18:
        return 68 <= a <= 82                       # sideburn in front of the ear
    edge = spline([(18, 64), (26, 47), (34, 36), (46, 31), (50, 0)], y) if y < 50 else 0   # cheek line, round the mouth
    return a >= edge and a <= (90 if y < 34 else 100)


def marat():
    c = dict(
        w=[(-50, 0), (-46, 19.5), (-40, 32), (-30, 40), (-18, 43.5), (-5, 44.5), (5, 45), (15, 45.5), (25, 45),
           (33, 42.5), (40, 37), (45.5, 28), (49, 15), (50, 0)],
        zf=[(-50, -4), (-45, 16), (-38, 28), (-25, 36), (-10, 38), (2, 35.5), (14, 36.5), (24, 38), (34, 37.5),
            (42, 34.5), (47, 29), (50, 16)],
        zb=[(-50, -4), (-44, -24), (-35, -38), (-20, -45), (-5, -46), (10, -41), (20, -30), (30, -17), (40, -7), (50, 0)],
        n=2.5,
        eye_x=17.5, eye_y=3.0, eye_w=19.0, eye_h=12.0, iris=6.3, eye_tilt=0.8, eye_peak=0.2,
        brow_h=10.0, brow_len=24, brow_w=5.6, brow_arch=2.6,
        nose_y=22.5, nose_w=9.4, nose_sh=0.8,
        mouth_y=37.0, mouth_w=28.0, lip_up=1.2, lip_low=3.4, lips_soft=True, mouth_open_max=13, teeth_h=4.2,
        lid_w=1.1, wing=0.0, crease=4.2, lower_a=0.45,
        skin="#e9b088", skin_sh="#bd6f52", blush="#e2664c", blush_a=0.42, lip="#c2625a", rim="#ffd2b4",
        iris_col="#4a2c1c", brow_col="#1c1412", lash="#1c110e", nostril="#7c3628", ear_in="#d36a54",
        ear_h=22, ear_wd=12, ear_y=9, blush_x=27, blush_y=19, socket=0.4,
    )
    c["bumps"] = [
        (0, 9, 4.0, 9, 3.0), (0, 20.0, 7.2, 6.2, 13.0), (-7.2, 23, 3.8, 3.2, 4.2), (7.2, 23, 3.8, 3.2, 4.2),
        (0, 35, 10.0, 2.4, 1.2), (0, 41, 8.0, 2.6, 1.6), (0, 47, 9, 3.5, 1.4),
        (-27, 18, 9.5, 9, 3.6), (27, 18, 9.5, 9, 3.6), (-17.5, 3, 8, 5, -2.6), (17.5, 3, 8, 5, -2.6),
        (-17, -7, 11, 3.6, 2.6), (17, -7, 11, 3.6, 2.6),
    ]
    c["lines"] = [([(-27.5, -1), (-30.5, 2.5), (-29.5, 6)], 0.4), ([(27.5, -1), (30.5, 2.5), (29.5, 6)], 0.4),   # laugh lines
                  ([(-28.5, -3), (-32, -1.5)], 0.3), ([(28.5, -3), (32, -1.5)], 0.3)]

    def under(cv, hd, ex):
        # the beard's own shadow on the jaw, under the clumps
        pts = []
        for y in (22, 28, 34, 40, 45, 49):
            pts.append((-(hd.width(y) - 1.5), y))
        for y in (49, 45, 40, 34, 28, 22):
            pts.append((hd.width(y) - 1.5, y))
        ins = [(31, 26), (20, 37), (17, 47), (0, 48.5), (-17, 47), (-20, 37), (-31, 26)]
        d = _sp([hd.P(x, y, lift=0.3) for x, y in pts + ins])
        cv.add(f'<path d="{d}" fill="{HAIR[1]}" opacity="0.8" filter="url(#{cv.blur(hd.s * 1.6)})"/>')

    def over(cv, hd, ex):
        # a thick moustache: two lobes from under the nose out past the corners of the mouth; it rides on the smile
        lt, lb, my, mw = mouth_curves(c, ex)
        ny = c["nose_y"] + 5.2
        cy = lt[0][1]                       # the corners of the mouth
        mid = lt[7][1]
        top = [(-mw - 6.5, cy - 0.5), (-mw - 1, cy - 6.5), (-mw * 0.55, (cy + ny) / 2 - 4.2), (-5, ny - 0.6), (0, ny + 1.0),
               (5, ny - 0.6), (mw * 0.55, (cy + ny) / 2 - 4.2), (mw + 1, cy - 6.5), (mw + 6.5, cy - 0.5)]
        bot = [(mw + 3, cy + 3.5), (mw - 1, cy + 0.8)] + [(x, y - 0.3) for x, y in lt[::-1][2:-2:2]] + [(-mw + 1, cy + 0.8), (-mw - 3, cy + 3.5)]
        d = _sp([hd.P(x, y, lift=3.4) for x, y in top + bot])
        paint_volume(cv, d, HAIR[0], HAIR[1], 22 * hd.s, lift=0.16, soft=0.11)
        k = cv.clip(d)
        for sd in (-1, 1):
            q = [hd.P(sd * x, y, lift=3.6) for x, y in [(4, ny + 2.2), (mw * 0.5, (cy + ny) / 2 - 1.2), (mw - 1, cy - 3.2)]]
            cv.add(f'<g clip-path="url(#{k})"><path d="{_sp(q, closed=False)}" fill="none" stroke="{HAIR[2]}" stroke-width="{_f(hd.s * 1.6)}" '
                   f'stroke-linecap="round" opacity="0.3" filter="url(#{cv.blur(hd.s * 0.8)})"/></g>')

    c["extra_under"] = under
    c["extra_face"] = over
    locks = scalp_curls(hl_marat, k=1.05, r=10.5, step=12.5, size=20, seed=5)
    locks += jaw_curls(beard_rad, beard_inside, -3, 61, r=8.6, step=11, size=18, seed=11)
    c["hair"] = Hair(HAIR[0], HAIR[1], HAIR[2], locks, sheen_a=0.3, cap=dict(k=1.03, to=(60, 180)), hairline=hl_marat)
    return c


# ------------------------------------------------------------------ figure

def marat_person():
    c = marat()

    def jacket_deco(cv, rig, L):
        s = rig.s
        # the double-breasted front: the flap's edge, two rows of buttons
        cloth.seam(cv, rig, L, [(6, 100), (24, 118), (27, 160), (25, 230), (22, 300)], M["white_sh"], w=5, a=0.5, blur=2.2)
        cloth.seam(cv, rig, L, [(6, 100), (24, 118), (27, 160), (25, 230), (22, 300)], M["white_sh"], w=1.2, a=0.8)
        for y in (150, 188, 226, 264):
            for x in (-21, 17):
                cloth.dot(cv, rig, L, x, y, 3.6, M["terra_sh"])
                cloth.dot(cv, rig, L, x - 0.7, y - 0.8, 2.6, M["terra"], lift=1.2)
        # soft folds where the belly pulls the cloth
        for x0, x1 in ((-66, -52), (64, 50)):
            cloth.seam(cv, rig, L, [(x0, 150), (x1, 200), (x0 * 0.9, 250)], M["white_sh"], w=7, a=0.35, blur=3)
        # the apron tied over the jacket: its band and a bow at the side
        cloth.band(cv, rig, L, 290, 312, M["terra"])
        cloth.band(cv, rig, L, 290, 293.5, _mix(M["terra"], "#ffffff", 0.25), a=0.7)
        cloth.seam(cv, rig, L, [(-80, 314), (0, 315), (80, 314)], M["terra_sh"], w=3, a=0.5, blur=1.5)

    def apron_deco(cv, rig, L):
        for x in (-52, -20, 22, 56):
            cloth.seam(cv, rig, L, [(x * 0.92, 318), (x, 420), (x * 1.03, 520)], M["terra_sh"], w=7, a=0.4, blur=3)
        cloth.patch(cv, rig, L, [(14, 352), (50, 352), (51, 398), (32, 405), (13, 398)], _mix(M["terra"], "#000000", 0.07),
                    edge=M["terra_sh"], edge_w=1.1)

    jacket = dict(w=[(84, 24), (92, 56), (104, 76), (140, 84), (200, 88), (260, 90), (300, 89.5), (316, 89)],
                  zf=[(84, 14), (104, 30), (150, 56), (210, 70), (270, 68), (316, 56)],
                  zb=[(84, -14), (104, -32), (160, -42), (240, -38), (316, -34)],
                  y0=86, y1=314, col=M["white"], sh=M["white_sh"], size=150, deco=jacket_deco, n=2.3)

    def towel(part):
        def fn(cv, rig, pose):
            sh = pose["_shift"]
            if part == "front":
                cen = [(48, 102, 6), (48, 110, 24), (47, 135, 47), (46, 170, 61), (45, 205, 68), (45, 236, 71)]
                nor = [(0.2, -0.9, 0.4), (0.2, -0.5, 0.8), (0.2, -0.2, 1), (0.2, 0, 1), (0.2, 0, 1), (0.2, 0, 1)]
                stripes = [(0.72, 0.8, M["terra"]), (0.86, 0.9, M["terra"])]
            else:
                cen = [(48, 102, 6), (48, 106, -18), (47, 135, -34), (46, 175, -38), (46, 200, -38)]
                nor = [(0.2, -0.9, -0.3), (0.2, -0.5, -0.8), (0.2, -0.1, -1), (0.2, 0, -1), (0.2, 0, -1)]
                stripes = [(0.7, 0.8, M["terra"])]
            from body import chain
            cen = [sh(p) for p in chain(cen, 4)]
            nor = chain(nor, 4)
            cloth.ribbon(cv, rig, cen, [17] * len(cen), nor, "#fbf6ec", "#b9a38c", 40, stripes=stripes)
        return fn

    return dict(
        head=c, hs=1.22, head_at=(0, 0, 4),
        neck=((0, 44, -5), (0, 98, -6), 18.5, 23.0),
        sh=(74, 120, -4), el=(94, 212, -8), wr=(92, 298, 6), hip=(30, 335, 0), kn=(28, 485, 3), an=(25, 622, -2),
        arm_r=[23, 20, 14.5], sleeve=dict(r=[30, 27, 24], col=M["white"], sh=M["white_sh"], end=0.5, roll="#fffaf0"),
        leg_r=[30, 19, 12.5], calf=2.0,
        pants=dict(r=[32, 22, 15.5], col=M["pants"], sh=M["pants_sh"], end=1),
        shoe=dict(floor=642, len=62, wid=17, h=20, col="#3d2f2a", sh="#1e1614", back=9, sole="#191210", sole_h=3.2),
        hand=dict(scale=2.9, curl=0.45, fat=1.25), shadow_w=130,
        before_torso=[towel("back")], after_torso=[towel("front")],
        layers=[
            dict(stage="low", w=[(296, 72), (330, 70), (356, 56)], zf=[(296, 44), (356, 30)], zb=[(296, -31), (356, -28)],
                 y0=298, y1=356, col=M["pants"], sh=M["pants_sh"], size=120),
            dict(stage="low", w=[(304, 58), (310, 80), (322, 87), (420, 82), (522, 78)], zf=[(300, 52), (340, 56), (522, 44)],
                 zb=[(300, -8), (522, -4)], y0=304, y1=522, n=2.2, col=M["terra"], sh=M["terra_sh"], size=160, deco=apron_deco),
            dict(w=[(74, 23.5), (100, 26)], zf=[(74, 22), (100, 25)], zb=[(74, -23), (100, -26)], y0=76, y1=100,
                 col=M["white"], sh=M["white_sh"], size=44, n=2.0),
            jacket,
        ],
    )
