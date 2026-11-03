"""The cast: Аня, Савелий Петрович, Тим, Вера — parameters of heads, faces, hair and clothes."""
import math, random
import numpy as np
from arc import *
from face import *
from person import *


def skinpal(lit, shadow, glow, line, blush, rim='#cfe3ee', hi='#fff5ec', warm='#efae8e'):
    return dict(lit=lit, shadow=shadow, glow=glow, deep=shadow, hi=hi, rim=rim, line=line, warm=warm, rim_op=0.45, hi_op=0.4, glow_op=0.3)


def anya():
    P = Person()
    P.zf = [(-126, -10), (-118, 40), (-100, 66), (-70, 80), (-40, 86), (-15, 90), (0, 85), (20, 84), (40, 86), (60, 85), (75, 84), (90, 80), (100, 74), (108, 62), (114, 40)]
    P.zb = [(-126, -10), (-118, -60), (-100, -84), (-70, -96), (-40, -98), (-15, -96), (0, -92), (20, -86), (40, -72), (55, -40), (68, -14), (85, -4), (100, 4), (108, 14), (114, 24)]
    P.a = [(-122, 0), (-114, 42), (-100, 63), (-70, 75), (-40, 78), (-15, 77), (0, 76), (20, 74), (40, 67), (60, 55), (75, 45), (88, 34), (98, 25), (105, 15), (110, 0)]
    P.zf = [(-122, -10), (-114, 36), (-100, 58), (-70, 75), (-40, 84), (-15, 90), (0, 84), (20, 84), (45, 87), (60, 89), (72, 90), (82, 87), (92, 85), (100, 79), (106, 64), (110, 38)]
    P.zb = [(-122, -10), (-114, -60), (-100, -84), (-70, -96), (-40, -98), (-15, -96), (0, -92), (20, -86), (40, -70), (50, -55), (60, -42), (75, -32), (90, -22), (100, -10), (105, 0), (110, 12)]
    P.p = [(-122, 2.0), (-40, 2.1), (20, 2.5), (70, 2.3), (114, 2.0)]
    P.pf = [(-122, 2.0), (-40, 2.1), (10, 2.4), (40, 2.0), (70, 1.7), (100, 1.5), (114, 1.5)]
    P.bumps = [(0.36, 2, 0.19, 12, -8), (-0.36, 2, 0.19, 12, -8), (0, -14, 0.55, 7, 2), (0.72, 22, 0.2, 11, 5), (-0.72, 22, 0.2, 11, 5), (0, 64, 0.22, 5, 3), (0, 76, 0.24, 6, 4), (0, 101, 0.22, 6, 4), (0.95, 72, 0.3, 14, -3), (-0.95, 72, 0.3, 14, -3)]
    P.nose_k = dict(root=-8, tip=44, sub=52, width=[(0, 9), (0.4, 8.5), (0.65, 10), (0.82, 14), (0.92, 16), (1, 14)], height=[(0, 3), (0.3, 8), (0.7, 16), (0.82, 20), (0.95, 11), (1, 1)])
    P.neck_k = dict(a=[(30, 30), (200, 35)], bf=[(30, 40), (200, 44)], bb=[(30, 40), (200, 44)], p=2.0, z0=[(30, -20), (200, -34)])
    P.eye_x, P.eye_y, P.eye_w, P.eye_h, P.eye_tilt, P.lid_peak = 31, 0, 33, 12.5, 1.5, 0.42
    P.iris_r, P.wing, P.crease, P.lash_w = 7.6, 0.1, 2.0, (1.6, 3.0, 3.4, 2.4)
    P.iris = ('#2c3a2a', '#5f7a4a', '#b9c27a')
    P.brow = [(9, -16), (9.5, -22.5), (22, -25.5), (37, -27.5), (47, -24), (53, -17.5), (45, -20.5), (33, -21.5), (20, -19.5)]
    P.brow_inner_x, P.brow_outer_x, P.brow_hairs = 10, 51, 0
    P.mouth_y, P.mouth_w, P.ulip, P.llip = 68, 21, 6, 8
    P.ear_x, P.ear_y, P.ear_z, P.ear_flare = 76, 16, -12, 18
    P.ear = [(-8, -20), (4, -25), (13, -17), (13, 0), (8, 14), (0, 22), (-6, 18), (-7, 4)]
    P.ear_inner = [[(-1, -15), (7, -16), (8, -4), (3, 8)]]
    P.blush = [(40, 32, 16, 10, 0.35), (0, 100, 12, 6, 0.15)]
    rnd = random.Random(4)
    P.freckles = [(rnd.uniform(-48, 48), rnd.uniform(18, 42), rnd.uniform(0.5, 0.9)) for _ in range(40)]
    P.freckles = [f for f in P.freckles if abs(f[0]) > 9 or f[1] < 30]
    P.pal = dict(skin=skinpal('#f2d3bd', '#c48a80', '#e06a4a', '#8e4f44', '#e4826e'),
                 neck=dict(skinpal('#dfb39c', '#c48a88', '#e8765a', '#9a5b50', '#e4826e')),
                 blush='#e4826e', freckle='#b0684c', white='#e8dbd2', lidshadow='#b99a9c', lid='#d79a90', lash='#3a2420',
                 brow='#6a3a26', mouth='#5a2626', lip_up='#b04e50', lip_lo='#cf6e68', mouthline='#6e3430', nostril='#7b4038')
    P.lines = lambda e: []
    P.hair = dict(base='#9a4a2a', shadow='#6a2c1c', dark='#4a1d14', light='#c8703c', shine='#f0b07a', line='#3a140c')
    P.hair_locks = lambda head: anya_hair(P)
    P.torso = torso_female()

    def bust(doc, view, head):
        T = P.torso
        blouse = [(-13, 124), (13, 124), (24, 170), (30, 240), (30, 345), (-30, 345), (-30, 240), (-24, 170)]
        collar_r = [(0, 126), (14, 122), (30, 132), (34, 148), (22, 156), (6, 146)]
        cardigan_band_r = [(24, 160), (36, 168), (44, 250), (46, 345), (34, 345), (32, 250), (28, 175)]
        pieces = [(blouse, '#efe2cc'), (collar_r, '#f6ecdc'), (mirror(collar_r), '#f6ecdc'),
                  (cardigan_band_r, '#5f7a52'), (mirror(cardigan_band_r), '#5f7a52')]
        lines = [([(0, 150), (0, 345)], '#b7a58c', 0.8, 0.6)]
        for k in range(-6, 7):
            if abs(k) > 1:
                x = k * 16
                lines.append(([(x * 0.8, 160), (x, 345)], '#4d6443', 0.8, 0.35))
        for b in (180, 220, 262, 304):
            pass
        return draw_cloth(doc, view, T, '#6d8a5c', pieces, shadow='#8c7f99', rim=P.pal.get('cloth_rim'), lines=lines)
    P.bust = bust
    hl = [(0, -80), (0.5, -72), (0.95, -42), (1.3, -5), (1.45, 12), (2.0, 35), (math.pi, 75)]
    P.hair_cap = lambda doc, view, head: hair_cap(doc, view, head, P, hl, lambda U, V: 5 + 5 * np.clip(-V / 110, 0, 1))
    return P


def anya_hair(P):
    L = []
    # back mass hanging behind the neck
    L += family([('s', 2.2, -60, 6), ('s', 2.6, 20, 10), (50, 110, -62), (58, 175, -50)],
                [('s', -2.2, -60, 6), ('s', -2.6, 20, 10), (-50, 110, -62), (-58, 175, -50)], 10, [18, 24, 20, 2], seed=2, layer='back', wave=5)
    # figure's right side: from the part, over the temple, down past the cheek to the shoulder, flaring out
    L += family([('s', -0.3, -114, 3), ('s', -0.78, -94, 9), ('s', -1.1, -55, 12), ('s', -1.25, -10, 15), (-88, 45, 18), (-98, 105, 4), (-104, 160, 2), (-92, 182, 8)],
                [('s', -0.55, -121, 3), ('s', -1.3, -100, 10), ('s', -1.75, -52, 12), ('s', -1.95, 0, 13), (-84, 55, -36), (-94, 115, -36), (-96, 165, -30), (-84, 185, -24)],
                10, [9, 14, 16, 15, 13, 9, 1], seed=3, jit=3, wave=7, period=70, strands=4)
    # figure's left side: swept back over the ear
    L += family([('s', 0.12, -119, 3), ('s', 0.9, -98, 9), ('s', 1.22, -60, 11), ('s', 1.48, -26, 10), ('s', 2.05, 18, 10), (74, 85, -40), (86, 140, -36), (80, 178, -26)],
                [('s', 0.0, -124, 3), ('s', 0.9, -113, 8), ('s', 1.7, -82, 10), ('s', 2.2, -42, 11), ('s', 2.5, 10, 10), (58, 85, -62), (66, 140, -58), (58, 172, -48)],
                9, [8, 13, 14, 13, 11, 8, 1], seed=4, jit=3, wave=6, period=70, strands=4)
    # side-swept fringe over the forehead, ending at the left temple
    L += family([('s', -0.3, -106, 4), ('s', 0.05, -98, 10), ('s', 0.55, -82, 12), ('s', 0.95, -52, 12), ('s', 1.12, -20, 11), ('s', 1.2, 8, 9)],
                [('s', -0.34, -88, 6), ('s', -0.1, -78, 11), ('s', 0.3, -66, 12), ('s', 0.72, -48, 12), ('s', 0.98, -22, 10), ('s', 1.06, 2, 9)],
                8, [8, 14, 14, 12, 8, 0.5], seed=5, jit=2.5, streak=(0.2, 0.5), strands=4)
    # a loose lock in front of the right temple
    L += [dict(pts=[('s', -0.3, -94, 7), ('s', -0.62, -62, 13), ('s', -0.84, -24, 13), ('s', -0.94, 10, 13), ('s', -1.0, 38, 12), ('s', -0.92, 56, 12)], w=[3, 6, 5, 4, 2.5, 0.3], tone=2, streak=None, strands=1)]
    return L


def savely():
    P = Person()
    P.a = [(-120, 0), (-112, 44), (-100, 64), (-70, 77), (-40, 80), (-15, 79), (0, 78), (20, 77), (40, 73), (60, 66), (75, 60), (88, 50), (98, 38), (106, 24), (112, 0)]
    P.zf = [(-120, -10), (-112, 34), (-100, 56), (-70, 74), (-40, 84), (-15, 93), (0, 85), (20, 84), (45, 87), (60, 89), (72, 89), (82, 87), (92, 85), (100, 79), (107, 64), (112, 38)]
    P.zb = [(-120, -10), (-112, -60), (-100, -84), (-70, -96), (-40, -98), (-15, -96), (0, -92), (20, -86), (40, -70), (50, -56), (60, -44), (75, -34), (90, -24), (100, -12), (106, 0), (112, 12)]
    P.p = [(-120, 2.0), (-40, 2.2), (20, 2.6), (70, 2.5), (112, 2.2)]
    P.pf = [(-120, 2.0), (-40, 2.2), (10, 2.5), (40, 2.3), (70, 2.1), (100, 1.9), (112, 1.8)]
    P.bumps = [(0.37, 2, 0.19, 12, -11), (-0.37, 2, 0.19, 12, -11), (0, -16, 0.55, 7, 4), (0.72, 24, 0.2, 11, 3), (-0.72, 24, 0.2, 11, 3),
               (0, 64, 0.22, 5, 2), (0, 76, 0.24, 6, 2), (0, 101, 0.22, 6, 4), (0.85, 55, 0.25, 14, -4), (-0.85, 55, 0.25, 14, -4),
               (0.95, 88, 0.25, 12, 5), (-0.95, 88, 0.25, 12, 5)]
    P.nose_k = dict(root=-8, tip=50, sub=58, width=[(0, 9), (0.4, 9), (0.65, 10.5), (0.82, 15.5), (0.92, 17.5), (1, 15)],
                    height=[(0, 4), (0.3, 10), (0.7, 20), (0.82, 24), (0.95, 13), (1, 1)], hump=3.5, droop=3)
    P.neck_k = dict(a=[(30, 34), (200, 40)], bf=[(30, 40), (200, 44)], bb=[(30, 40), (200, 44)], p=2.0, z0=[(30, -16), (200, -34)])
    P.eye_x, P.eye_y, P.eye_w, P.eye_h, P.eye_tilt, P.lid_peak = 32, 0, 28, 8.5, -0.5, 0.48
    P.iris_r, P.wing, P.crease, P.lash_w = 6.0, 0.0, 3.5, (1.1, 2.0, 2.2, 1.5)
    P.iris = ('#26303a', '#5a7284', '#a9bcc6')
    P.brow = [(8, -13), (8, -21), (20, -26), (36, -28), (50, -23), (59, -14), (49, -17), (34, -19.5), (20, -17)]
    P.brow_inner_x, P.brow_outer_x, P.brow_hairs = 8, 59, 30
    P.mouth_y, P.mouth_w, P.ulip, P.llip = 73, 19, 3.2, 5
    P.ear_x, P.ear_y, P.ear_z, P.ear_flare = 78, 20, -12, 20
    P.ear = [(-9, -24), (5, -30), (15, -21), (15, 0), (10, 17), (1, 27), (-7, 22), (-8, 4)]
    P.ear_inner = [[(-1, -18), (8, -19), (9, -4), (4, 10)]]
    P.blush = [(38, 34, 16, 11, 0.45), (0, 100, 12, 6, 0.1)]
    rnd = random.Random(8)
    P.freckles = [(rnd.uniform(-60, 60), rnd.uniform(-95, -55), rnd.uniform(0.9, 1.8)) for _ in range(9)]
    P.bags = 0.6
    P.moustache = [(0, 58.5), (7, 57.5), (15, 59.5), (22, 65), (26, 74), (21, 72.5), (13, 70.5), (0, 70)]
    P.glasses = dict(rx=12.5, ry=11, dy=6, dz=16, color='#a8834a', w=1.3, square=0)
    P.pal = dict(skin=skinpal('#efcab4', '#b97c74', '#d8644a', '#7e4238', '#dc7a6a'),
                 neck=dict(skinpal('#ddb39d', '#b4766e', '#d8644a', '#7e4238', '#dc7a6a')),
                 blush='#dc7466', freckle='#a8735a', white='#e3d6cc', lidshadow='#a88a88', lid='#c98a80', lash='#3a2a26',
                 brow='#e8e4dc', brow2='#b9b2a8', mouth='#4a2222', lip_up='#a85a54', lip_lo='#c47a6e', mouthline='#5e2e2a', nostril='#6b3530')

    def lines(e):
        L = []
        for sd in (1, -1):
            L.append(([(sd * 17, 44), (sd * 23, 56), (sd * 27, 70), (sd * 28, 82)], 1.6, 0.6))
            L.append(([(sd * 46, 6), (sd * 52, 3)], 1.0, 0.5))
            L.append(([(sd * 46, 10), (sd * 53, 11)], 1.0, 0.45))
            L.append(([(sd * 23, 92), (sd * 26, 100)], 1.1, 0.35))
        for y in (-48, -58, -68):
            L.append(([(-30, y + 2), (-10, y - 1), (10, y), (30, y + 2)], 1.0, 0.35))
        L.append(([(-4, -20), (-5, -12)], 1.1, 0.5))
        L.append(([(4, -20), (5, -12)], 1.1, 0.5))
        return L
    P.lines = lines
    P.hair = dict(base='#dcd6cc', shadow='#9c968f', dark='#6e6863', light='#f6f2ea', shine='#ffffff', line='#7a736c')

    def mask(U, V):
        side = np.abs(U) - 1.25
        return np.minimum(np.minimum(side * 60, V + 55), 70 - V)
    P.hair_cap = lambda doc, view, head: hair_cap(doc, view, head, P, mask, lambda U, V: 4 + 0 * U)

    def locks(head):
        L = []
        for sd in (1, -1):
            L += family([('s', sd * 1.3, -50, 4), ('s', sd * 1.42, -30, 10), ('s', sd * 1.5, -12, 13)],
                        [('s', sd * 2.3, -50, 4), ('s', sd * 2.3, -20, 10), ('s', sd * 2.2, 5, 12)], 7, [6, 10, 0.5], seed=20 + sd, jit=3, strands=2)
        L += family([('s', 2.2, -40, 4), ('s', 2.6, 0, 8), ('s', 2.8, 30, 6)], [('s', -2.2, -40, 4), ('s', -2.6, 0, 8), ('s', -2.8, 30, 6)], 8, [8, 12, 0.5], seed=24, layer='back')
        return L
    P.hair_locks = locks
    P.torso = torso_male(1.0)

    def bust(doc, view, head):
        T = P.torso
        shirt = [(-16, 120), (16, 120), (34, 175), (40, 345), (-40, 345), (-34, 175)]
        collar_r = [(0, 128), (16, 118), (24, 124), (26, 146), (12, 152), (3, 140)]
        vest_r = [(22, 160), (46, 150), (130, 160), (140, 345), (14, 345), (12, 260), (16, 200)]
        tie = [(-6, 138), (6, 138), (8, 148), (-8, 148)]
        pieces = [(shirt, '#d6d2c6'), (vest_r, '#3d5244'), (mirror(vest_r), '#3d5244'), (collar_r, '#e4e0d6'), (mirror(collar_r), '#e4e0d6'), (tie, '#7a2f2a')]
        lines = [([(14, 200), (13, 345)], '#26342b', 1.2, 0.7), ([(-14, 200), (-13, 345)], '#26342b', 1.2, 0.7),
                 ([(16, 270), (40, 290), (70, 280)], '#c79a4a', 1.6, 0.95)]
        s = draw_cloth(doc, view, T, '#3d5244', pieces, shadow='#7d7088', rim=None, lines=lines)
        for y in (215, 245, 275, 305):
            sp, nz = on_surface(T, view, [(flat_uv(T, 18, y), y)], 1)
            if nz[0] > 0.1:
                s += '<circle cx="%s" cy="%s" r="%s" fill="#c9a050"/><circle cx="%s" cy="%s" r="%s" fill="#fff0c0" opacity="0.6"/>' % (
                    fmt(sp[0][0]), fmt(sp[0][1]), fmt(2.6 * view.s), fmt(sp[0][0] - 0.8 * view.s), fmt(sp[0][1] - 0.8 * view.s), fmt(0.9 * view.s))
        return s
    P.bust = bust
    return P


def tim():
    P = Person()
    P.a = [(-118, 0), (-110, 46), (-96, 68), (-70, 80), (-40, 82), (-15, 80), (0, 78), (20, 74), (40, 66), (55, 57), (68, 47), (78, 35), (85, 21), (89, 0)]
    P.zf = [(-118, -10), (-110, 38), (-96, 62), (-70, 80), (-40, 88), (-15, 90), (0, 86), (20, 86), (40, 87), (52, 88), (60, 87), (70, 82), (78, 74), (84, 62), (89, 34)]
    P.zb = [(-118, -10), (-110, -62), (-96, -88), (-70, -100), (-40, -102), (-15, -98), (0, -92), (20, -82), (35, -64), (45, -48), (55, -36), (70, -24), (80, -12), (89, 8)]
    P.p = [(-118, 2.0), (-40, 2.1), (20, 2.35), (60, 2.2), (89, 2.0)]
    P.pf = [(-118, 2.0), (-40, 2.1), (10, 2.3), (40, 2.0), (65, 1.85), (89, 1.7)]
    P.bumps = [(0.35, 2, 0.19, 12, -6), (-0.35, 2, 0.19, 12, -6), (0.62, 32, 0.28, 14, 5), (-0.62, 32, 0.28, 14, 5),
               (0, 50, 0.2, 4, 2), (0, 60, 0.22, 5, 3), (0, 80, 0.22, 5, 3)]
    P.nose_k = dict(root=-2, tip=33, sub=39, width=[(0, 6), (0.5, 6.5), (0.82, 10.5), (0.92, 12), (1, 10)],
                    height=[(0, 1), (0.3, 4), (0.7, 10), (0.82, 13), (0.95, 8), (1, 1)], droop=-1.5)
    P.neck_k = dict(a=[(30, 22), (200, 26)], bf=[(30, 30), (200, 32)], bb=[(30, 30), (200, 32)], p=2.0, z0=[(30, -18), (200, -24)])
    P.eye_x, P.eye_y, P.eye_w, P.eye_h, P.eye_tilt, P.lid_peak = 29, 0, 30, 13.5, 0.8, 0.45
    P.iris_r, P.wing, P.crease, P.lash_w = 8.6, 0.0, 1.6, (1.2, 2.1, 2.3, 1.5)
    P.iris = ('#24160f', '#6b4528', '#c09050')
    P.brow = [(9, -17), (9.5, -21.5), (22, -24.5), (36, -25), (46, -21), (40, -21), (30, -21.5), (18, -19.5)]
    P.brow_inner_x, P.brow_outer_x, P.brow_hairs = 9, 46, 0
    P.mouth_y, P.mouth_w, P.ulip, P.llip = 54, 15, 3.6, 5
    P.ear_x, P.ear_y, P.ear_z, P.ear_flare = 77, 12, -12, 30
    P.ear = [(-8, -20), (4, -25), (13, -17), (13, 0), (8, 13), (0, 20), (-6, 16), (-7, 4)]
    P.ear_inner = [[(-1, -15), (7, -16), (8, -4), (3, 8)]]
    P.blush = [(38, 30, 18, 12, 0.5), (0, 82, 12, 6, 0.15)]
    rnd = random.Random(12)
    P.freckles = [(rnd.uniform(-38, 38), rnd.uniform(12, 30), rnd.uniform(0.5, 0.9)) for _ in range(34)]
    P.freckles = [f for f in P.freckles if abs(f[0]) > 8]
    P.pal = dict(skin=skinpal('#f0cdb0', '#c48676', '#e46a46', '#8a4c3c', '#e57c62'),
                 neck=dict(skinpal('#e3b79b', '#bf7f70', '#e46a46', '#8a4c3c', '#e57c62')),
                 blush='#e57c62', freckle='#a8603e', white='#ebe0d8', lidshadow='#b09494', lid='#d49a8c', lash='#2e1e18',
                 brow='#3c2418', mouth='#4e1e1e', lip_up='#c06a60', lip_lo='#d8857a', mouthline='#6a3028', nostril='#6e3a30')
    P.lines = lambda e: []
    P.hair = dict(base='#4a2e20', shadow='#2c1a12', dark='#1e110c', light='#7a4e32', shine='#b07a52', line='#140a06')
    hl = [(0, -74), (0.5, -68), (0.95, -40), (1.3, -2), (1.45, 10), (2.0, 30), (math.pi, 62)]
    P.hair_cap = lambda doc, view, head: hair_cap(doc, view, head, P, hl, lambda U, V: 7 + 6 * np.clip(-V / 110, 0, 1))

    def locks(head):
        L = []
        rnd = random.Random(31)
        # tufts all over the crown, radiating from a whorl, tips lifting off
        for k in range(46):
            u0 = rnd.uniform(-math.pi, math.pi)
            v0 = rnd.uniform(-116, -60)
            du = (u0 - 0.25) * 0.25
            u1 = u0 + du + rnd.uniform(-0.15, 0.15)
            v1 = min(v0 + rnd.uniform(25, 45), 40 if abs(u1) > 1.3 else -40)
            L.append(dict(pts=[('s', u0, v0, 6), ('s', (u0 + u1) / 2, (v0 + v1) / 2, 11), ('s', u1, v1, 15 + rnd.uniform(0, 8))],
                          w=[9, 12, 0.5], tone=rnd.choice((0, 0, 1, 2)), strands=2, streak=None))
        # fringe: short spiky bits over the forehead
        for k in range(9):
            u0 = -0.7 + k * 0.17 + rnd.uniform(-0.04, 0.04)
            L.append(dict(pts=[('s', u0 * 0.6, -100, 8), ('s', u0, -80, 11), ('s', u0 * 1.1 + rnd.uniform(-0.12, 0.12), -60 + rnd.uniform(-6, 6), 12)],
                          w=[9, 11, 0.5], tone=rnd.choice((0, 1, 2)), strands=2, streak=None, layer='front' if False else None))
        # cowlick
        L.append(dict(pts=[('s', 0.3, -110, 6), ('s', 0.35, -124, 22), ('s', 0.15, -128, 34)], w=[8, 6, 0.4], tone=2, strands=1, streak=None))
        L.append(dict(pts=[('s', 0.4, -108, 6), ('s', 0.55, -120, 20), ('s', 0.62, -130, 28)], w=[7, 5, 0.4], tone=0, strands=1, streak=None))
        return L
    P.hair_locks = locks
    P.torso = torso_child()

    def bust(doc, view, head):
        T = P.torso
        neckband = [(-24, 112), (24, 112), (30, 126), (0, 134), (-30, 126)]
        hood_r = [(18, 110), (40, 112), (64, 126), (58, 150), (30, 146), (14, 132)]
        pocket = [(-40, 230), (40, 230), (46, 300), (-46, 300)]
        stripe = [(-90, 186), (90, 186), (90, 196), (-90, 196)]
        pieces = [(stripe, '#3a6f8a'), (hood_r, '#c98f2e'), (mirror(hood_r), '#c98f2e'), (neckband, '#b07a22'), (pocket, '#c48b2c')]
        lines = [([(8, 126), (10, 150), (7, 176)], '#efe4d0', 1.8, 0.95), ([(-8, 126), (-10, 150), (-6, 172)], '#efe4d0', 1.8, 0.95),
                 ([(-40, 230), (40, 230)], '#8a5a14', 1.0, 0.6)]
        return draw_cloth(doc, view, T, '#d9a038', pieces, shadow='#8c7896', rim=None, lines=lines)
    P.bust = bust
    P.plaster = True

    def extras(doc, view, head, e):
        nose = P.nose(head)
        pts = [(-0.95, 0.2), (0.95, 0.2), (0.95, 0.34), (-0.95, 0.34)]
        sp, nz = on_surface(nose, view, sample_curve(pts, True, 3), 0.8)
        if np.mean(nz) > 0.05:
            d = 'M' + 'L'.join('%s,%s' % (fmt(a), fmt(b)) for a, b in sp) + 'Z'
            return path(d, '#e8cfa6', op=0.95) + path(d, 'none', '#b8946a', 0.8 * view.s, 0.8)
        return ''
    P.extras = extras
    return P


def vera():
    P = Person()
    P.a = [(-122, 0), (-114, 40), (-100, 60), (-70, 72), (-40, 75), (-15, 74), (0, 73), (20, 72), (40, 65), (60, 54), (75, 45), (88, 35), (98, 26), (106, 16), (112, 0)]
    P.zf = [(-122, -10), (-114, 36), (-100, 58), (-70, 75), (-40, 84), (-15, 90), (0, 84), (20, 84), (45, 87), (60, 88), (72, 88), (82, 86), (92, 84), (100, 78), (107, 63), (112, 38)]
    P.zb = [(-122, -10), (-114, -60), (-100, -84), (-70, -96), (-40, -98), (-15, -96), (0, -92), (20, -86), (40, -70), (50, -55), (60, -42), (75, -32), (90, -22), (100, -10), (106, 0), (112, 12)]
    P.p = [(-122, 2.0), (-40, 2.1), (20, 2.5), (70, 2.3), (112, 2.0)]
    P.pf = [(-122, 2.0), (-40, 2.1), (10, 2.4), (40, 1.9), (70, 1.65), (100, 1.45), (112, 1.45)]
    P.bumps = [(0.36, 2, 0.19, 12, -9), (-0.36, 2, 0.19, 12, -9), (0, -14, 0.55, 7, 2), (0.74, 18, 0.18, 10, 6), (-0.74, 18, 0.18, 10, 6),
               (0.9, 55, 0.3, 14, -4), (-0.9, 55, 0.3, 14, -4), (0, 64, 0.22, 5, 2), (0, 76, 0.24, 6, 3), (0, 101, 0.22, 6, 4)]
    P.nose_k = dict(root=-8, tip=47, sub=54, width=[(0, 7.5), (0.4, 7.5), (0.65, 8.5), (0.82, 12), (0.92, 13.5), (1, 12)],
                    height=[(0, 3), (0.3, 8), (0.7, 17), (0.82, 20.5), (0.95, 10), (1, 1)])
    P.neck_k = dict(a=[(30, 27), (200, 32)], bf=[(30, 38), (200, 42)], bb=[(30, 38), (200, 42)], p=2.0, z0=[(30, -20), (200, -34)])
    P.eye_x, P.eye_y, P.eye_w, P.eye_h, P.eye_tilt, P.lid_peak = 31, 0, 31, 10, 2.5, 0.5
    P.iris_r, P.wing, P.crease, P.lash_w = 7.0, 0.06, 2.5, (1.4, 2.6, 3.0, 2.0)
    P.iris = ('#1d2834', '#4d6a82', '#a6bac6')
    P.brow = [(9, -15), (9.5, -21), (24, -23.5), (40, -24), (50, -20), (54, -15), (44, -17.5), (30, -18.5), (18, -17.5)]
    P.brow_inner_x, P.brow_outer_x, P.brow_hairs = 9, 54, 0
    P.mouth_y, P.mouth_w, P.ulip, P.llip = 70, 18, 3.8, 5.5
    P.ear_x, P.ear_y, P.ear_z, P.ear_flare = 74, 16, -12, 14
    P.ear = [(-8, -20), (4, -25), (13, -17), (13, 0), (8, 14), (0, 22), (-6, 18), (-7, 4)]
    P.ear_inner = [[(-1, -15), (7, -16), (8, -4), (3, 8)]]
    P.blush = [(42, 30, 14, 9, 0.22)]
    P.freckles = []
    P.bags = 0.45
    P.glasses = dict(rx=14, ry=10, dy=1, dz=11, color='#2a2226', w=1.5, square=1)
    P.pal = dict(skin=skinpal('#ecccb8', '#ad7c78', '#cf6450', '#7a4440', '#d27c70'),
                 neck=dict(skinpal('#dcb5a2', '#a87472', '#cf6450', '#7a4440', '#d27c70')),
                 blush='#cf7a6e', freckle='#a07060', white='#e2d6d0', lidshadow='#9e8a90', lid='#c08a86', lash='#1e1416',
                 brow='#221a1a', mouth='#4a2224', lip_up='#985050', lip_lo='#b26862', mouthline='#5a2a2a', nostril='#663432')

    def lines(e):
        L = []
        for sd in (1, -1):
            L.append(([(sd * 15, 46), (sd * 21, 58), (sd * 24, 70)], 1.2, 0.35))
        L.append(([(-3, -19), (-4, -12)], 1.0, 0.4))
        return L
    P.lines = lines
    P.hair = dict(base='#2a2326', shadow='#151113', dark='#0c0a0b', light='#5a5056', shine='#a49aa2', line='#050404')
    hl = [(0, -84), (0.45, -78), (0.95, -46), (1.3, -8), (1.45, 8), (2.0, 32), (math.pi, 64)]
    P.hair_cap = lambda doc, view, head: hair_cap(doc, view, head, P, hl, lambda U, V: 4 + 3 * np.clip(-V / 110, 0, 1))
    bun_y, bun_z = -20, -112

    def locks(head):
        L = []
        # swept back from a side part to the bun
        L += family([('s', 0.25, -112, 3), ('s', 0.9, -95, 5), ('s', 1.5, -60, 5), ('s', 2.3, -36, 5), ('s', 2.75, -28, 5)],
                    [('s', 0.18, -86, 3), ('s', 0.85, -70, 5), ('s', 1.35, -30, 5), ('s', 2.0, -2, 5), ('s', 2.7, -10, 5)], 10, [6, 11, 10, 8, 2], seed=41, jit=1.5, strands=3, streak=(0.1, 0.4))
        L += family([('s', 0.22, -112, 3), ('s', -0.6, -100, 5), ('s', -1.4, -66, 5), ('s', -2.3, -36, 5), ('s', -2.75, -28, 5)],
                    [('s', 0.15, -84, 3), ('s', -0.6, -76, 5), ('s', -1.3, -34, 5), ('s', -2.0, -2, 5), ('s', -2.7, -10, 5)], 10, [6, 11, 10, 8, 2], seed=42, jit=1.5, strands=3, streak=(0.1, 0.4))
        # the grey streak at the front
        L.append(dict(pts=[('s', 0.2, -100, 5), ('s', 0.6, -92, 6), ('s', 1.1, -72, 6), ('s', 1.6, -46, 6)], w=[5, 8, 7, 1], tone=2, strands=2, streak=(0.1, 0.7), grey=True))
        # loose strands by the temples
        L.append(dict(pts=[('s', -0.85, -60, 5), ('s', -1.0, -30, 7), ('s', -1.05, 0, 8), ('s', -1.0, 25, 8)], w=[2, 3, 2, 0.2], tone=1, strands=0, streak=None))
        L.append(dict(pts=[('s', 1.0, -58, 5), ('s', 1.12, -30, 7), ('s', 1.15, 0, 8)], w=[2, 2.6, 0.2], tone=1, strands=0, streak=None))
        return L
    P.hair_locks = locks

    def bun(doc, view, head):
        B = Loft(a=[(bun_y - 30, 0), (bun_y - 24, 20), (bun_y, 30), (bun_y + 22, 22), (bun_y + 28, 0)],
                 bf=[(bun_y - 30, 0), (bun_y - 24, 16), (bun_y, 24), (bun_y + 22, 18), (bun_y + 28, 0)],
                 bb=[(bun_y - 30, 0), (bun_y - 24, 16), (bun_y, 24), (bun_y + 22, 18), (bun_y + 28, 0)], p=2.0, z0=[(bun_y - 30, bun_z), (bun_y + 28, bun_z)])
        R = regions(B, view, shadow=0.05)
        hp = P.hair
        s = path(poly_path(R['sil']), hp['base'], extra=' filter="url(#paint)"')
        s += path(poly_path(R['shadow']), hp['shadow'], extra=' filter="url(#brush)"')
        s += path(poly_path(R['hi']), hp['light'], op=0.6, extra=' filter="url(#soft)"')
        # coils
        for k in range(5):
            a0 = k * 1.3
            pts = [(bun_z + 0, 0)]
        return s
    P.bun = bun
    P.torso = torso_female()

    def bust(doc, view, head):
        T = P.torso
        collar_r = [(4, 112), (24, 108), (40, 118), (44, 150), (30, 170), (10, 160)]
        shirt = [(-12, 130), (12, 130), (18, 175), (-18, 175)]
        lapel_r = [(12, 160), (30, 168), (54, 200), (28, 300), (8, 345), (4, 250)]
        pieces = [(shirt, '#e8e2da'), (lapel_r, '#26303d'), (mirror(lapel_r), '#26303d'), (collar_r, '#33404f'), (mirror(collar_r), '#33404f')]
        lines = [([(0, 175), (0, 345)], '#141a22', 1.2, 0.8)]
        s = draw_cloth(doc, view, T, '#33404f', pieces, shadow='#7c7690', rim=None, lines=lines)
        sp, nz = on_surface(T, view, [(flat_uv(T, 0, 168), 168)], 1.5)
        if nz[0] > 0.1:
            s += '<circle cx="%s" cy="%s" r="%s" fill="#8a2c36"/><circle cx="%s" cy="%s" r="%s" fill="#ffd0d0" opacity="0.5"/>' % (
                fmt(sp[0][0]), fmt(sp[0][1]), fmt(4 * view.s), fmt(sp[0][0] - 1.2 * view.s), fmt(sp[0][1] - 1.2 * view.s), fmt(1.3 * view.s))
        return s
    P.bust = bust
    return P
