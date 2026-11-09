"""kira — Кира, a teenager: head, choppy hair with a long fringe, a slouching thin body, a hoodie, headphones, boots."""
import math
from face import Hair, hull
from pix import spline, smooth_path as _sp, mix as _mix, f as _f, paint_volume
from body import tube, chain, interp_r
from cast import woman_head
import cloth

K = dict(plum="#553458", plum_sh="#2c1830", rib="#43284a", pants="#3a3740", pants_sh="#1d1b22", boot="#2b2730",
         boot_sh="#121016", lime="#d6f23c", lime_sh="#8fae1c", phone="#33303a", phone_sh="#17151c")
HAIR = ("#2b2630", "#110e15", "#5f5769")


def hl_kira(lon):
    a = abs(((lon + 180) % 360) - 180)
    return 30 - 26 * (a / 90) ** 1.5 if a < 90 else 4 - 34 * ((a - 90) / 90) ** 0.8


def kira():
    c = woman_head(
        w=[(-50, 0), (-47, 17.5), (-40, 31), (-30, 38.5), (-18, 41.5), (-5, 41), (5, 39.5), (15, 36.5), (25, 31.5),
           (33, 25.5), (40, 18.5), (45, 12.5), (48.5, 6), (50, 0)],
        skin="#f4d3bf", skin_sh="#cf968a", blush="#e58a86", blush_a=0.16, lip="#bb6670", rim="#ffe2d4",
        iris_col="#5d6b62", brow_col="#241a26", lash="#17101a", nostril="#93514c", ear_in="#dd8a7c",
        eye_x=17.0, eye_y=0.5, eye_w=18.5, eye_h=11.2, iris=6.3, eye_tilt=2.3, eye_peak=0.3,
        brow_h=10.2, brow_len=20, brow_w=3.7, brow_arch=0.8,
        nose_y=22.0, nose_w=4.5, nose_sh=0.5,
        mouth_y=34.5, mouth_w=15.0, lip_up=2.0, lip_low=3.2,
        lid_w=2.0, wing=0.5, crease=4.2, bags=0.2, lower_a=0.75,
    )
    c["bumps"] = [
        (0, 8, 3.0, 9, 2.2), (0, 19.5, 4.0, 4.4, 8.6), (-4.2, 21.5, 2.6, 2.5, 2.2), (4.2, 21.5, 2.6, 2.5, 2.2),
        (0, 31, 7.5, 2.2, 2.0), (0, 37, 6.2, 2.3, 2.2), (0, 45, 6.5, 3.6, 1.8),
        (-17, -8, 10, 3.5, 1.4), (17, -8, 10, 3.5, 1.4), (-25, 13, 7.5, 6, 2.0), (25, 13, 7.5, 6, 2.0),
        (-17.5, 0.5, 8.5, 5, -2.6), (17.5, 0.5, 8.5, 5, -2.6),
    ]
    c["hair"] = kira_hair()
    return c


def kira_hair():
    import random
    rnd = random.Random(3)
    part = -30
    locks = []
    # choppy sides and back: strips from the crown that hang to different lengths and end in sharp tips
    for lon in range(-180, 180, 17):
        a = abs(lon)
        if a < 58:
            continue
        side = a < 115
        y_tip = (33 if side else 26) + rnd.uniform(-7, 7)
        tw = rnd.uniform(-7, 7)
        locks.append(dict(pts=[('s', 78, part + (lon - part) * 0.35, 1.05), ('s', 34, lon, 1.09), ('c', lon, 4, 47.5),
                               ('c', lon + tw * 0.4, y_tip - 12, 46.5), ('c', lon + tw, y_tip, 43 if side else 40)],
                          w=[4, 11.5, 11, 8, 0.4], size=26, sheen=0.7, z=(-60 if a > 125 else 0)))
    # the fringe: from a side parting across the forehead, the longest lock falls over her left eye
    locks.append(dict(pts=[('s', 80, part, 1.05), ('s', 52, -52, 1.09), ('s', 24, -66, 1.10), ('s', -6, -72, 1.07)],
                      w=[4, 10, 9, 0.4], size=24))
    locks.append(dict(pts=[('s', 78, part + 2, 1.05), ('s', 50, -24, 1.10), ('s', 28, -12, 1.12), ('s', 9, -2, 1.10)],
                      w=[4, 10, 8.5, 0.4], size=24))
    locks.append(dict(pts=[('s', 72, 8, 1.06), ('s', 42, 40, 1.11), ('s', 12, 56, 1.11), ('s', -24, 62, 1.06)],
                      w=[4, 11, 10, 0.4], size=26))
    locks.append(dict(pts=[('s', 80, part + 6, 1.06), ('s', 54, -8, 1.11), ('s', 27, 9, 1.14), ('s', 2, 21, 1.14),
                           ('s', -20, 28, 1.11), ('s', -38, 33, 1.06)],
                      w=[4, 13, 15, 13.5, 9, 0.4], size=30, z=6))
    return Hair(HAIR[0], HAIR[1], HAIR[2], locks, sheen_a=0.34, cap=dict(k=1.03, to=(60, 180)), hairline=hl_kira)


# ------------------------------------------------------------------ figure

SLOUCH = dict(z=[(-40, 20), (40, 18), (100, 6), (170, -6), (300, 3), (428, 6), (564, 0)])


def kira_person():
    c = kira()

    def hoodie_deco(cv, rig, L):
        # the hem's ribbing, the kangaroo pocket, the cords of the hood
        cloth.band(cv, rig, L, 286, 302, K["rib"])
        cloth.seam(cv, rig, L, [(-46, 286), (0, 287), (46, 286)], K["plum_sh"], w=2.5, a=0.6, blur=1.2)
        pk = [(-17, 214), (17, 214), (30, 250), (30, 272), (-30, 272), (-30, 250)]
        cloth.patch(cv, rig, L, pk, _mix(K["plum"], "#000000", 0.08))
        cloth.seam(cv, rig, L, [(-30, 270), (-30, 250), (-17, 214), (17, 214), (30, 250), (30, 270)], K["plum_sh"], w=1.6, a=0.8)
        for sd in (-1, 1):
            cloth.seam(cv, rig, L, [(sd * 29, 268), (sd * 28, 250), (sd * 21, 228)], K["plum_sh"], w=5, a=0.6, blur=1.6)
            cloth.seam(cv, rig, L, [(sd * 6, 92), (sd * 7, 120), (sd * 9, 148 + 8 * (sd > 0))], "#b9b0c2", w=1.7, a=0.95, lift=1.2)
            cloth.dot(cv, rig, L, sd * 9, 150 + 8 * (sd > 0), 2.0, "#d9d2e0", lift=1.4)
        # folds of a hoodie that is too big
        cloth.seam(cv, rig, L, [(-38, 130), (-30, 170), (-36, 205)], K["plum_sh"], w=7, a=0.4, blur=3)
        cloth.seam(cv, rig, L, [(36, 150), (27, 185), (33, 215)], K["plum_sh"], w=7, a=0.4, blur=3)

    def cup_at(sd):
        return (sd * 14, 94, 7), (sd * 0.74, 0.1, 0.66)

    def phones_back(cv, rig, pose):
        sh = pose["_shift"]
        pts = []
        for i in range(13):
            a = math.radians(-118 + 236 * i / 12)
            pts.append(sh((16 * math.sin(a), 86 - 5 * math.cos(a), -8 - 14 * math.cos(a))))
        tube(cv, rig, chain(pts, 2), [3.1] * (2 * 12 + 1), K["phone"], K["phone_sh"], lift=0.14)
        for sd in (-1, 1):
            if rig.depth(sh(cup_at(sd)[0])) < rig.depth(sh((0, 96, -8))) - 4:
                cup(cv, rig, sh, sd)

    def phones_front(cv, rig, pose):
        sh = pose["_shift"]
        for sd in sorted((-1, 1), key=lambda sd: rig.depth(sh(cup_at(sd)[0]))):
            if rig.depth(sh(cup_at(sd)[0])) >= rig.depth(sh((0, 96, -8))) - 4:
                cup(cv, rig, sh, sd)

    def cup(cv, rig, sh, sd):
        cen, nrm = cup_at(sd)
        cen = sh(cen)
        up = (0, 1, 0)
        ax = (nrm[1] * up[2] - nrm[2] * up[1], nrm[2] * up[0] - nrm[0] * up[2], nrm[0] * up[1] - nrm[1] * up[0])
        l = math.sqrt(sum(a * a for a in ax))
        ax = tuple(a / l for a in ax)
        ay = (nrm[1] * ax[2] - nrm[2] * ax[1], nrm[2] * ax[0] - nrm[0] * ax[2], nrm[0] * ax[1] - nrm[1] * ax[0])
        def ring(r, out, ry=1.0):
            return [rig.P(tuple(cen[i] + nrm[i] * out + (ax[i] * math.cos(t) + ay[i] * ry * math.sin(t)) * r for i in range(3)))
                    for t in [2 * math.pi * k / 20 for k in range(20)]]
        body = hull(ring(10.5, 0, 1.12) + ring(10.5, 4.5, 1.12) + ring(8.4, 7, 1.12))
        paint_volume(cv, _sp(body), K["phone"], K["phone_sh"], 24 * rig.s, lift=0.14, soft=0.1)
        if rig.rot(nrm)[2] > 0.1:
            paint_volume(cv, _sp(ring(7.5, 7.2, 1.12)), K["lime"], K["lime_sh"], 17 * rig.s, lift=0.16, soft=0.12)
            cv.add(f'<path d="{_sp(ring(2.9, 7.4, 1.12))}" fill="{K["phone"]}" opacity="0.85"/>')

    def laces(cv, rig, pose):
        J = pose["_J"]
        for sd in (-1, 1):
            a = J["an"][sd]
            for i in range(3):
                y = a[1] - 14 + 8.5 * i
                z = a[2] + 8.5 + 2.2 * i
                q = [rig.P((a[0] + dx, y + dy, z + 0.5)) for dx, dy in ((-5, 1.5), (0, -1.2), (5, 1.5))]
                cv.add(f'<path d="{_sp(q, closed=False)}" fill="none" stroke="{K["lime"]}" stroke-width="{_f(1.9 * rig.s)}" '
                       f'stroke-linecap="round"/>')

    return dict(
        head=c, hs=1.0, head_at=(0, 22, 0), bend=SLOUCH,
        neck=((0, 46, -11), (0, 94, -9), 8.0, 9.0),
        sh=(27, 106, 3), el=(37, 196, -5), wr=(36, 286, 8), hip=(12, 300, 0), kn=(11, 428, 4), an=(10, 544, -2),
        arm_r=[7.4, 5.8, 4.6], sleeve=dict(r=[15, 13.5, 12.5], col=K["plum"], sh=K["plum_sh"], cuff=K["rib"], cuff_len=15),
        leg_r=[11, 7.4, 5.4], calf=1.6,
        pants=dict(r=[12.5, 8.8, 7.2], col=K["pants"], sh=K["pants_sh"], end=0.84),
        sock=dict(r=9.6, col=K["boot"], sh=K["boot_sh"], h=38),
        shoe=dict(floor=564, len=47, wid=12.5, h=19, col=K["boot"], sh=K["boot_sh"], back=8, sole="#0f0d13", sole_h=6.5),
        hand=dict(scale=1.65, curl=0.55, fat=0.9), shadow_w=60,
        before_torso=[phones_back], after_torso=[phones_front], after_head=[laces],
        layers=[
            dict(stage="low", w=[(268, 27), (300, 27), (320, 22)], zf=[(268, 18), (320, 15)], zb=[(268, -17), (320, -16)],
                 y0=270, y1=320, col=K["pants"], sh=K["pants_sh"], size=70),
            dict(stage="low", w=[(62, 18), (74, 33), (92, 40), (108, 34), (118, 22)], zf=[(62, 0), (118, 8)],
                 zb=[(62, -22), (80, -36), (98, -39), (118, -24)], y0=64, y1=118, col=K["rib"], sh=K["plum_sh"], size=70, n=2.0),
            dict(w=[(76, 13), (84, 28), (94, 38), (112, 43), (160, 45), (230, 46), (290, 46.5), (302, 46)],
                 zf=[(76, 9), (94, 15), (130, 21), (200, 22), (285, 24), (302, 21)],
                 zb=[(76, -9), (94, -18), (140, -22), (230, -21), (302, -20)],
                 y0=78, y1=302, col=K["plum"], sh=K["plum_sh"], size=110, deco=hoodie_deco, n=2.2),
        ],
    )
