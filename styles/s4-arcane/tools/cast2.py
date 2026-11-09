"""The two who joined the cast: Марат (a cook, about 35) and Кира (about 15) — on the same shared parts as the four."""
import math, random
import numpy as np
from arc import *
from face import *
from person import *
from body import *
from cast import CAST, skinpal, arm_tube, folds, cloth_lines_vertical


def dot_piece(x, y, r, n=10):
    """A small round piece of cloth colour (a button)."""
    return [(x + r * math.cos(a), y + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


# ====================================================================== Марат

def marat():
    P = Person()
    P.ears_over_hair = True
    P.head_pose = dict(pitch=-5, roll=5)
    # a broad head: wide cheeks, a heavy square jaw
    P.a = [(-120, 0), (-112, 46), (-100, 67), (-70, 81), (-40, 85), (-15, 85), (0, 85), (20, 86), (40, 85), (60, 80), (75, 74), (88, 64), (98, 50), (106, 32), (112, 0)]
    P.zf = [(-120, -10), (-112, 34), (-100, 56), (-70, 74), (-40, 84), (-15, 92), (0, 85), (20, 85), (45, 88), (60, 90), (72, 90), (82, 88), (92, 86), (100, 80), (107, 65), (112, 38)]
    P.zb = [(-120, -10), (-112, -60), (-100, -84), (-70, -96), (-40, -98), (-15, -96), (0, -92), (20, -86), (40, -72), (50, -60), (60, -50), (72, -38), (82, -18), (92, 8), (100, 30), (106, 46), (112, 54)]
    P.p = [(-120, 2.0), (-40, 2.2), (20, 2.6), (70, 2.6), (112, 2.3)]
    P.pf = [(-120, 2.0), (-40, 2.2), (10, 2.5), (40, 2.3), (70, 2.2), (100, 2.0), (112, 1.9)]
    P.bumps = [(0.37, 2, 0.19, 12, -9), (-0.37, 2, 0.19, 12, -9), (0, -16, 0.55, 7, 4), (0.66, 30, 0.26, 14, 6), (-0.66, 30, 0.26, 14, 6),
               (0, 64, 0.22, 5, 2), (0, 76, 0.24, 6, 3), (0, 101, 0.22, 6, 4)]
    P.nose_k = dict(root=-6, tip=45, sub=53, width=[(0, 10), (0.4, 11), (0.65, 14), (0.82, 20), (0.92, 22), (1, 18)],
                    height=[(0, 3), (0.3, 8), (0.7, 17), (0.82, 21), (0.95, 12), (1, 1)], droop=1)
    P.neck_k = dict(a=[(30, 50), (200, 60)], bf=[(30, 46), (200, 52)], bb=[(30, 46), (200, 52)], p=2.2, z0=[(30, -14), (200, -26)])
    P.eye_x, P.eye_y, P.eye_w, P.eye_h, P.eye_tilt, P.lid_peak = 33, 0, 31, 12.5, 1.0, 0.46
    P.iris_r, P.wing, P.crease, P.lash_w = 7.6, 0.0, 2.6, (1.4, 2.5, 2.7, 1.8)
    P.iris = ('#1a0f0a', '#4a2c18', '#9a6634')
    P.brow = [(7, -12), (7, -23), (20, -28), (37, -29), (51, -24), (60, -15), (50, -17.5), (35, -19), (20, -16.5)]
    P.brow_inner_x, P.brow_outer_x, P.brow_hairs = 7, 60, 34
    P.mouth_y, P.mouth_w, P.ulip, P.llip = 71, 25, 3.4, 6.5
    P.ear_x, P.ear_y, P.ear_z, P.ear_flare = 82, 18, -12, 22
    P.ear = [(-9, -22), (5, -28), (15, -19), (15, 0), (10, 16), (1, 25), (-7, 20), (-8, 4)]
    P.ear_inner = [[(-1, -17), (8, -18), (9, -4), (4, 9)]]
    P.blush = [(46, 30, 22, 15, 0.34), (0, 30, 10, 8, 0.12)]
    P.freckles = []
    P.pal = dict(skin=skinpal('#e6b690', '#a9695a', '#d2603a', '#6e382c', '#d8694e', rim='#ffe6c0', warm='#e59a70'),
                 neck=dict(skinpal('#d39c78', '#a26252', '#d2603a', '#6e382c', '#d8694e', rim='#ffe6c0', warm='#e59a70')),
                 blush='#d8644a', freckle='#9a6048', white='#eadccf', lidshadow='#a08478', lid='#b9775f', lash='#1c1210',
                 brow='#1d1512', brow2='#3a2a22', mouth='#3e1614', tongue='#c05a54', lip_up='#9a4a40', lip_lo='#bb6654', mouthline='#4a201a', nostril='#5a2a22')

    def lines(e):
        L = []
        sm = e['smile'] if not isinstance(e['smile'], tuple) else max(e['smile'])
        for sd in (1, -1):
            if sm > 0.5:
                # the laugh gathers the skin at the outer corners of the eyes and lifts the cheeks
                L.append(([(sd * 51, -3), (sd * 57, -6)], 0.9, 0.4))
                L.append(([(sd * 52, 2), (sd * 59, 3)], 0.9, 0.4))
            L.append(([(sd * 19, 40), (sd * 26, 49), (sd * 31, 58)], 1.4, 0.5))
        if e['knit'] > 0.4:
            L.append(([(-4, -22), (-5, -12)], 1.3, 0.6))
            L.append(([(4, -22), (5, -12)], 1.3, 0.6))
        return L
    P.lines = lines
    P.hair = dict(base='#241813', shadow='#130c0a', dark='#0b0605', light='#4c3528', shine='#8a684e', line='#070303')
    hl = [(0, -76), (0.5, -73), (0.95, -50), (1.22, -24), (1.36, -2), (1.5, 14), (2.0, 34), (math.pi, 62)]

    def curly(U, V):
        return 9 + 5 * np.clip(-V / 110, 0, 1) + 2.6 * np.sin(8 * U + 0.7) * np.sin(0.17 * V + 1.0) + 1.6 * np.sin(13 * U) * np.cos(0.29 * V)
    P.hair_cap = lambda doc, view, head: hair_cap(doc, view, head, P, hl, curly)

    def locks(head):
        L = []
        rnd = random.Random(52)
        # short curls: every lock is a small hook lifting off the head
        for k in range(230):
            u0 = rnd.uniform(-math.pi, math.pi)
            v0 = rnd.uniform(-118, 46)
            lim = np.interp(abs(u0), [t[0] for t in hl], [t[1] for t in hl])
            if v0 > lim - 6:
                continue
            sd = rnd.choice((1, -1))
            du = sd * rnd.uniform(0.07, 0.12) / max(0.35, math.cos(math.radians(min(80, abs(v0) * 0.7))))
            dv = rnd.uniform(7, 11)
            L.append(dict(pts=[('s', u0, v0, 9), ('s', u0 + du, v0 + dv * 0.35, 15), ('s', u0 + du * 0.9, v0 + dv, 15), ('s', u0 + du * 0.15, v0 + dv * 1.3, 12)],
                          w=[4, 8, 7, 0.6], tone=rnd.choice((0, 0, 0, 1, 2)), strands=0, streak=None))
        return L
    P.hair_locks = locks

    # ---- the beard: a shell over the jaw, cheeks and upper lip, open round the mouth
    cheek = [(0, 55), (0.2, 56), (0.36, 59), (0.52, 60), (0.78, 53), (1.03, 35), (1.22, 10), (1.34, -14), (1.46, -22), (1.58, 34), (1.8, 56)]

    def beard(doc, view, head, e, ms):
        mw, my = ms['mw'], ms['my']
        sm = e['smile'] if not isinstance(e['smile'], tuple) else (e['smile'][0] + e['smile'][1]) / 2
        lift = sm * 5 - e['sad'] * 4
        op = e['open']
        hw = mw + 2.2

        def field(U, V):
            X, _, _ = head.pos(U, V)
            ax = np.abs(X)
            au = np.abs(U)
            f = np.minimum((V - np.interp(au, [t[0] for t in cheek], [t[1] for t in cheek])) / 6.0, (1.76 - au) * 5)
            t = np.clip(ax / hw, 0, 1)
            top = my - P.ulip - 2.2 - lift * t ** 2
            bot = my + op + P.llip + 1.6 - (lift + (op + P.llip) * 0.75) * t ** 2
            hole = np.minimum(np.minimum((hw - ax) / 3.0, (V - top) / 3.0), (bot - V) / 3.0)
            hole = np.where(np.cos(U) > 0, hole, -1)
            return np.minimum(f, -hole)

        def thick(U, V):
            return 3.5 + 12 * np.clip((V - 32) / 60, 0, 1) + 2.0 * np.sin(9 * U + 1) * np.sin(0.2 * V) + 1.2 * np.sin(15 * U) * np.cos(0.33 * V)
        # a tuft under the chin (the shell is ragged at the pole of the head form)
        cx_, cy_, _ = point3(view, 0, head.v1 + 5, float(interp(head.z0, head.v1)) + 4)
        s = '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" filter="url(#paint)"/>' % (fmt(cx_), fmt(cy_), fmt(26 * view.s), fmt(15 * view.s), P.hair['shadow'])
        s += hair_cap(doc, view, head, P, field, thick)
        # curls over it: short hooked strokes, lighter where the light falls
        shell = Offset(head, thick)
        rnd = random.Random(19)
        hp = P.hair
        for k in range(270):
            u = rnd.uniform(-1.72, 1.72)
            v = rnd.uniform(-18, head.v1 - 3)
            if float(field(np.array([u]), np.array([v]))[0]) < 0.5:
                continue
            sd = rnd.choice((1, -1))
            pts = [(u, v), (u + sd * 0.07, v + 3.5), (u + sd * 0.08, v + 8), (u + sd * 0.02, v + 11.5)]
            sp, nz = on_surface(shell, view, pts, 1.0)
            if min(nz) < 0.12:
                continue
            P_, N_ = shell.normals(np.array([u]), np.array([v]))
            nx_, ny_, nz_ = view.rot(N_[:, 0], N_[:, 1], N_[:, 2])
            dl = float(nx_[0] * view.L[0] + ny_[0] * view.L[1] + nz_[0] * view.L[2])
            col = mix(hp['base'], hp['light'], rnd.uniform(0.5, 1.0)) if (dl > 0.25 and rnd.random() < 0.6) else hp['dark']
            d2, _ = ribbon_screen(sp, [0.6 * view.s, rnd.uniform(2.6, 4.4) * view.s, 2.6 * view.s, 0.3])
            s += path(d2, col, op=rnd.uniform(0.5, 0.85))
        return s
    P.beard = beard
    return P


def marat_body(P, rest=False):
    """rest=True: both arms down (for the head-and-shoulders sheets); otherwise a fist on the hip and the ladle held up."""
    skin = P.pal['neck']
    white, white_d, terra, terra_d, trou = '#efe5d4', '#b9ab98', '#c8623a', '#8e3f22', '#3b3432'
    sh = '#8d7f96'
    # the line of the pose: the chest leans to his left, the belly and the hips push to his right
    lean = [(92, 0), (200, 6), (330, -6), (460, -20), (600, -22), (1340, -12)]
    T = Loft(a=[(92, 54), (106, 92), (122, 142), (140, 180), (162, 204), (210, 210), (280, 204), (360, 208), (440, 218), (520, 214), (600, 198)],
             bf=[(92, 44), (140, 62), (200, 90), (300, 108), (420, 136), (500, 130), (600, 96)],
             bb=[(92, 46), (140, 66), (200, 82), (300, 80), (420, 76), (600, 76)], p=2.5,
             z0=[(92, -24), (160, -26), (300, -16), (600, -10)], x0=lean)
    collar = [(-46, 98), (46, 98), (44, 120), (20, 132), (0, 126), (-20, 132), (-44, 120)]
    kerchief = [(-30, 122), (0, 116), (30, 122), (10, 168), (0, 176), (-10, 168)]
    towel = [(-104, 112), (-166, 138), (-170, 330), (-106, 322)]
    pieces = [(towel, '#e9cfae'), ([(-169, 284), (-106, 277), (-106, 291), (-169, 298)], terra), ([(-170, 306), (-106, 299), (-106, 306), (-170, 313)], terra),
              (collar, '#f8f1e4'), (kerchief, terra)]
    for y in (214, 284, 354, 424):
        for x in (-44, 44):
            pieces.append((dot_piece(x, y, 9), terra_d))
    torso = Part(T, white, pieces=pieces,
                 lines=[([(80, 150), (86, 300), (78, 560)], white_d, 1.4, 0.7), ([(-80, 150), (-86, 300), (-78, 560)], white_d, 1.0, 0.4),
                        ([(-136, 140), (-138, 270)], '#c9a67e', 1.2, 0.7), ([(-10, 168), (0, 150), (10, 168)], terra_d, 1.0, 0.6),
                        ([(-170, 330), (-106, 322)], '#b08c62', 1.2, 0.7)],
                 shadow=sh, center=(0, 300, 0))
    A = Loft(a=[(516, 218), (600, 212), (900, 206), (1340, 200)], bf=[(516, 136), (620, 116), (900, 106), (1340, 100)], bb=[(516, 80), (1340, 80)], p=2.5,
             z0=[(516, -10), (1340, -6)], x0=lean, extra=folds(640, 1340, 7, 7, 0.4))
    apron = Part(A, terra, pieces=[([(-230, 516), (230, 516), (230, 550), (-230, 550)], terra_d)],
                 lines=[([(-24, 550), (-44, 606), (-32, 668)], terra_d, 2.4, 0.8), ([(-20, 550), (2, 616), (20, 656)], terra_d, 2.4, 0.8),
                        ([(-42, 538), (-22, 530), (-22, 554), (-42, 548)], terra_d, 2.0, 0.8)] + cloth_lines_vertical([-130, 120], 600, 1340, terra_d, 1.0, 0.3),
                 shadow='#86687a', center=(-14, 950, 0), bias=-12)
    parts = [torso, apron]
    # legs: the weight on his right leg, the left set out to the side
    for sd, x0_, x1_ in ((-1, -118, -114), (1, 86, 112)):
        Lg = Tube([(x0_, 1160, -8), ((x0_ + x1_) / 2, 1400, -6), (x1_, 1640, -8)], [70, 62, 54])
        parts.append(Part(Lg, trou, shadow='#6a6070', center=((x0_ + x1_) / 2, 1400, -10), bias=-70))
        F = shoe(x1_ + sd * 4, 1616, 1700, 92, 46, '#4a3020', z=-2)
        parts.append(Part(F, '#4a3020', shadow='#6e5a6a', center=(x1_, 1660, 22), bias=-27))

    def sleeve(sd, pts, radii, c):
        parts.append(Part(arm_tube(sd, pts, radii), white, shadow=sh, center=c))

    def cuff(pts, c, b=2):
        parts.append(Part(Tube(pts, [51, 52, 50]), '#f6eee0', shadow=sh, center=c, bias=b))
    if rest:
        for sd in (1, -1):
            sleeve(sd, [(182, 196, -22), (214, 290, -22), (224, 390, -16)], [56, 52, 48], (sd * 206, 290, -20))
        return parts
    # the figure's right arm: akimbo, the fist on the hip
    sleeve(-1, [(182, 196, -22), (240, 284, -40), (284, 372, -54)], [56, 52, 47], (-234, 280, -40))
    cuff([(-272, 346, -50), (-284, 372, -54), (-284, 394, -50)], (-280, 372, -50))
    Fa = Tube([(-284, 378, -54), (-276, 462, -22), (-246, 538, 18)], [44, 41, 30])
    parts.append(Part(Fa, None, kind='skin', pal=skin, center=(-270, 458, -10), bias=4))
    parts += hand_parts((-248, 534, 18), (0.72, 0.5, 0.25), (0.25, -0.2, -1), skin, L=100, wid=62, curl=[1.25, 1.3, 1.35, 1.4], spread=0.1,
                        thumb=(1.0, 0.5), side=1, bias=8)
    # the figure's left arm: the forearm out to the side, the ladle held upright like a sceptre
    sleeve(1, [(182, 196, -22), (226, 286, -26), (248, 374, -20)], [56, 52, 47], (224, 284, -24))
    cuff([(240, 348, -22), (248, 374, -20), (262, 388, -12)], (248, 370, -18))
    wr = np.array((366, 316, 46.0))
    Fb = Tube([(250, 378, -20), (312, 352, 14), tuple(wr)], [44, 40, 30])
    parts.append(Part(Fb, None, kind='skin', pal=skin, center=(312, 350, 16), bias=4))
    d = np.array((0.86, -0.3, 0.42))
    n = np.array((-0.42, 0.0, 0.9))
    parts += hand_parts(tuple(wr), d, n, skin, L=100, wid=62, curl=[1.3, 1.3, 1.35, 1.4], spread=0.05, thumb=(0.9, 0.7), side=-1, bias=10)
    du = d / np.linalg.norm(d)
    rc = wr + du * 64 + np.array((0, 0, 14.0))
    steel, steel_s = '#b4aea4', '#6c6878'
    rod = Tube([(rc[0] - 8, rc[1] + 130, rc[2] - 4), tuple(rc), (rc[0] + 10, rc[1] - 300, rc[2] + 4)], [11, 9, 9])
    parts.append(Part(rod, steel, shadow=steel_s, center=(rc[0], rc[1] - 100, rc[2] - 30), bias=0))
    by, bx, R = rc[1] - 310, rc[0] + 66, 64
    prof = [(by - 40, R), (by - 10, R), (by + 26, R * 0.8), (by + 54, R * 0.3)]
    bowl = Loft(a=prof, bf=prof, bb=prof, p=2.0, x0=[(by - 40, bx), (by + 54, bx)], z0=[(by - 40, rc[2] + 4), (by + 54, rc[2] + 4)])
    parts.append(Part(bowl, steel, pieces=[([(-R, by - 40), (R, by - 40), (R, by - 30), (-R, by - 30)], '#ddd7ca')], shadow=steel_s,
                      center=(bx, by, rc[2] - 20)))
    return parts


# ====================================================================== Кира

def kira():
    P = Person()
    P.head_pose = dict(pitch=9, roll=-5, turn=-4)
    # between a child and a woman: a longer face than Тим's, a narrow jaw that is not yet Аня's fine wedge
    P.a = [(-122, 0), (-114, 42), (-100, 62), (-70, 74), (-40, 77), (-15, 76), (0, 75), (20, 73), (40, 66), (58, 55), (72, 45), (82, 35), (90, 26), (96, 16), (101, 0)]
    P.zf = [(-122, -10), (-114, 36), (-100, 58), (-70, 76), (-40, 85), (-15, 89), (0, 84), (20, 84), (45, 86), (58, 88), (68, 88), (76, 85), (84, 82), (91, 76), (97, 62), (101, 36)]
    P.zb = [(-122, -10), (-114, -60), (-100, -84), (-70, -96), (-40, -98), (-15, -96), (0, -92), (20, -86), (40, -70), (50, -55), (60, -42), (70, -30), (77, -12), (84, 12), (90, 30), (96, 44), (101, 50)]
    P.p = [(-122, 2.0), (-40, 2.1), (20, 2.45), (70, 2.3), (101, 2.0)]
    P.pf = [(-122, 2.0), (-40, 2.1), (10, 2.4), (40, 2.0), (66, 1.75), (92, 1.6), (101, 1.6)]
    P.bumps = [(0.36, 2, 0.19, 12, -8), (-0.36, 2, 0.19, 12, -8), (0, -14, 0.55, 7, 2), (0.72, 22, 0.2, 11, 4), (-0.72, 22, 0.2, 11, 4),
               (0, 57, 0.22, 5, 3), (0, 68, 0.24, 6, 3), (0, 88, 0.22, 6, 4), (0.95, 62, 0.3, 14, -2), (-0.95, 62, 0.3, 14, -2)]
    P.nose_k = dict(root=-6, tip=40, sub=47, width=[(0, 7.5), (0.4, 7.5), (0.65, 9), (0.82, 12.5), (0.92, 14), (1, 12)],
                    height=[(0, 2.5), (0.3, 7), (0.7, 14), (0.82, 17.5), (0.95, 10), (1, 1)], droop=-0.5)
    P.neck_k = dict(a=[(30, 24), (200, 30)], bf=[(30, 32), (200, 38)], bb=[(30, 32), (200, 38)], p=2.0, z0=[(30, -22), (200, -52)])
    P.eye_x, P.eye_y, P.eye_w, P.eye_h, P.eye_tilt, P.lid_peak = 31, 0, 31, 11, 1.4, 0.44
    P.iris_r, P.wing, P.crease, P.lash_w = 7.2, 0.07, 1.8, (2.0, 3.6, 3.9, 2.8)
    P.iris = ('#1c2224', '#4e6660', '#a9c0a8')
    P.brow = [(9, -13), (9.5, -18.5), (22, -21.5), (37, -22.5), (48, -19), (53, -13.5), (45, -16), (33, -17), (20, -15.5)]
    P.brow_inner_x, P.brow_outer_x, P.brow_hairs = 9, 53, 0
    P.mouth_y, P.mouth_w, P.ulip, P.llip = 61, 16.5, 4.6, 6.2
    P.ear_x, P.ear_y, P.ear_z, P.ear_flare = 75, 15, -12, 20
    P.ear = [(-8, -20), (4, -25), (13, -17), (13, 0), (8, 14), (0, 22), (-6, 18), (-7, 4)]
    P.ear_inner = [[(-1, -15), (7, -16), (8, -4), (3, 8)]]
    P.blush = [(40, 28, 17, 11, 0.13), (0, 34, 9, 7, 0.1)]
    rnd = random.Random(23)
    P.freckles = [(rnd.uniform(-34, 34), rnd.uniform(14, 30), rnd.uniform(0.5, 0.8)) for _ in range(14)]
    P.pal = dict(skin=skinpal('#f1d8cc', '#b78690', '#d86a62', '#7e4850', '#dc8a84', rim='#e4f7a0'),
                 neck=dict(skinpal('#dcb9ae', '#b07c88', '#d86a62', '#7e4850', '#dc8a84', rim='#e4f7a0')),
                 blush='#dc8280', freckle='#a8707a', white='#e6dad6', lidshadow='#9a8490', lid='#a8788a', lash='#150f14',
                 brow='#221a22', mouth='#4a2026', lip_up='#a85660', lip_lo='#c47478', mouthline='#5e2c34', nostril='#70404a')
    P.lines = lambda e: []
    P.hair = dict(base='#2e2434', shadow='#18121c', dark='#0d0a10', light='#5c4868', shine='#a48cb4', line='#060408')
    hl = [(0, -78), (0.5, -72), (0.95, -44), (1.3, -6), (1.45, 10), (2.0, 34), (math.pi, 60)]
    P.hair_cap = lambda doc, view, head: hair_cap(doc, view, head, P, hl, lambda U, V: 6 + 6 * np.clip(-V / 110, 0, 1))

    def locks(head):
        L = []
        rnd = random.Random(61)
        # choppy layers over the crown and the back: straight pieces of uneven length with blunt ends
        for k in range(54):
            u0 = rnd.uniform(-math.pi, math.pi)
            if -0.5 < u0 < 1.1:
                continue
            v0 = rnd.uniform(-116, -30)
            u1 = u0 + (u0 + 0.35) * 0.08 + rnd.uniform(-0.08, 0.08)
            back = abs(u1) > 1.5
            v1 = min(v0 + rnd.uniform(45, 80), (rnd.uniform(34, 62) if back else rnd.uniform(4, 26)))
            if v1 - v0 < 25:
                continue
            L.append(dict(pts=[('s', u0, v0, 6), ('s', (u0 + u1) / 2, (v0 + v1) / 2, 12), ('s', u1, v1 - 6, 13), ('s', u1 + rnd.uniform(-0.05, 0.05), v1, 12 + rnd.uniform(0, 5))],
                          w=[9, 13, 10, 1.2], tone=rnd.choice((0, 0, 1, 2)), strands=2, streak=None))
        # the figure's right side: short pieces pushed off the face, the right eye and brow left open
        L += family([('s', -0.36, -112, 6), ('s', -0.8, -94, 12), ('s', -1.14, -64, 13), ('s', -1.3, -38, 12), ('s', -1.36, -14, 13)],
                    [('s', -0.5, -116, 5), ('s', -1.2, -100, 10), ('s', -1.6, -58, 12), ('s', -1.74, -14, 12), ('s', -1.68, 22, 13)],
                    8, [8, 13, 12, 8, 1], seed=62, jit=3, streak=None, strands=2)
        # the long fringe: from the parting across the forehead and down over the figure's left eye to the cheek
        L += family([('s', -0.34, -110, 6), ('s', -0.05, -88, 12), ('s', 0.2, -52, 13), ('s', 0.3, -12, 14), ('s', 0.33, 18, 14), ('s', 0.3, 40, 13)],
                    [('s', -0.2, -116, 6), ('s', 0.5, -96, 12), ('s', 0.9, -58, 13), ('s', 1.02, -18, 13), ('s', 1.02, 14, 13), ('s', 0.95, 36, 12)],
                    9, [8, 13, 14, 12, 8, 1], seed=63, jit=3.5, streak=(0.2, 0.5), strands=3)
        # two thin strands that fall apart from the fringe
        L.append(dict(pts=[('s', -0.2, -100, 7), ('s', 0.02, -64, 13), ('s', 0.1, -24, 14), ('s', 0.08, 4, 14)], w=[3, 5, 4, 0.4], tone=2, strands=1, streak=None))
        L.append(dict(pts=[('s', 0.5, -86, 9), ('s', 1.0, -44, 13), ('s', 1.16, 0, 14), ('s', 1.12, 46, 15)], w=[4, 7, 6, 0.5], tone=1, strands=1, streak=None))
        return L
    P.hair_locks = locks
    return P


def kira_body(P, rest=False):
    """A slouch: the neck forward, the upper back round, the hips pushed forward; arms crossed, weight on one leg."""
    skin = P.pal['neck']
    plum, plum_d, plum_l = '#4c3050', '#2e1c32', '#5e3c62'
    coal, boot, lime = '#2c2b32', '#17161a', '#c9ee2c'
    sh = '#6f6488'
    zc = [(110, -36), (170, -48), (300, -38), (450, -16), (600, -2)]
    T = Loft(a=[(110, 26), (126, 42), (140, 70), (156, 92), (180, 102), (240, 104), (400, 105), (520, 108), (600, 100)],
             bf=[(110, 28), (150, 40), (220, 46), (400, 50), (600, 52)], bb=[(110, 30), (150, 48), (220, 60), (330, 52), (600, 46)], p=2.4, z0=zc)
    pocket = [(-52, 452), (52, 452), (64, 556), (-64, 556)]
    neckband = [(-26, 114), (26, 114), (32, 130), (0, 140), (-32, 130)]
    torso = Part(T, plum, pieces=[(pocket, '#432a46'), (neckband, plum_d), ([(-104, 574), (104, 574), (104, 600), (-104, 600)], plum_d)],
                 lines=[([(9, 132), (12, 190), (9, 236)], '#cfc4d6', 1.8, 0.9), ([(-9, 132), (-13, 180), (-10, 222)], '#cfc4d6', 1.8, 0.9),
                        ([(-52, 452), (52, 452)], plum_d, 1.2, 0.7)] + cloth_lines_vertical([-66, 70], 200, 570, plum_d, 1.0, 0.3, 0.04),
                 shadow=sh, center=(0, 300, -20))
    Hd = Loft(a=[(84, 0), (100, 40), (126, 54), (152, 46), (166, 0)], bf=[(84, 0), (100, 20), (126, 28), (152, 24), (166, 0)],
              bb=[(84, 0), (100, 20), (126, 28), (152, 24), (166, 0)], p=2.2, z0=[(84, -82), (166, -78)])
    parts = [torso, Part(Hd, plum_l, shadow=sh, center=(0, 120, -90), bias=-60)]
    # headphones round the neck: the one acid accent
    band = Tube([(60, 168, -16), (58, 140, -48), (34, 122, -88), (0, 116, -100), (-34, 122, -88), (-58, 140, -48), (-60, 168, -16)], [7, 7, 7, 7, 7, 7, 7])
    parts.append(Part(band, '#3a3840', shadow='#5a566a', center=(0, 130, -80), bias=-50))
    for sd in (1, -1):
        y = 178
        cup = Loft(a=[(y - 22, 4), (y - 15, 12), (y, 15), (y + 15, 12), (y + 22, 4)], bf=[(y - 22, 5), (y - 15, 12), (y, 15), (y + 15, 12), (y + 22, 5)],
                   bb=[(y - 22, 5), (y, 12), (y + 22, 5)], p=2.2, x0=[(y - 22, sd * 62), (y + 22, sd * 58)], z0=[(y - 22, -10), (y + 22, 0)])
        pad = Loft(a=[(y - 26, 5), (y - 17, 17), (y, 21), (y + 17, 17), (y + 26, 5)], bf=[(y - 26, 4), (y, 9), (y + 26, 4)], bb=[(y - 26, 4), (y, 12), (y + 26, 4)],
                   p=2.2, x0=[(y - 26, sd * 62), (y + 26, sd * 58)], z0=[(y - 26, -14), (y + 26, -4)])
        parts.append(Part(pad, '#2c2b32', shadow='#4c4860', center=(sd * 60, y, 24), bias=5))
        ring = dot_piece(0, y, 8, 14)
        parts.append(Part(cup, lime, lines=[(ring + ring[:1], '#8fae18', 1.6, 0.9)], shadow='#6c7a50', center=(sd * 60, y, 30), bias=6))
    if rest:
        for sd in (1, -1):
            A = arm_tube(sd, [(90, 178, -46), (104, 270, -44), (108, 370, -32)], [27, 26, 24])
            parts.append(Part(A, plum, shadow=sh, center=(sd * 100, 280, -40)))
        return parts
    # arms crossed on the chest: the right forearm under, the left over it, its hand holding the right arm
    for sd in (1, -1):
        A = arm_tube(sd, [(90, 178, -46), (108, 264, -36), (114, 350, -8)], [27, 26, 24])
        parts.append(Part(A, plum, shadow=sh, center=(sd * 104, 270, -34)))
    Fr = Tube([(-114, 350, -8), (-76, 372, 36), (-14, 372, 52), (60, 352, 46)], [24, 23, 21, 19])
    parts.append(Part(Fr, plum, shadow=sh, center=(-20, 368, 46), bias=2))
    Fl = Tube([(114, 350, -8), (84, 384, 44), (24, 396, 70), (-50, 384, 62)], [24, 23, 21, 20])
    parts.append(Part(Fl, plum, shadow=sh, center=(20, 392, 70), bias=8, lines=[]))
    parts += hand_parts((-52, 384, 62), (-0.9, -0.28, -0.15), (0.1, 0.1, -1), skin, L=62, wid=36, curl=[0.42, 0.45, 0.48, 0.5], spread=0.12,
                        thumb=(0.9, 0.3), side=1, bias=60, outline=1.6)
    # legs: the weight on her right, the left set forward and out
    legs = [(-1, [(-40, 570, -6), (-44, 980, -10), (-46, 1380, -12)]), (1, [(40, 570, -2), (58, 980, 24), (80, 1380, 14)])]
    for sd, pts in legs:
        Lg = Tube(pts, [39, 29, 23, 19])
        parts.append(Part(Lg, coal, shadow='#57526a', center=(pts[1][0], 1000, pts[1][2] - 4), bias=-30))
        x, z = pts[-1][0], pts[-1][2]
        B = limb(1300, 1420, [(1300, x), (1420, x)], [(1300, z), (1420, z + 2)], [(1300, 27), (1330, 30), (1420, 31)])
        parts.append(Part(B, boot, shadow='#4c4860', center=(x, 1370, z + 2), bias=-28,
                          lines=[([(-8, 1314 + 16 * k), (8, 1322 + 16 * k), (-8, 1330 + 16 * k)], lime, 2.2, 0.95) for k in range(6)]))
        F = shoe(x, 1400, 1470, 78, 32, boot, z=z + 4)
        parts.append(Part(F, boot, shadow='#4c4860', center=(x, 1440, z + 28), bias=-27))
    return parts


CAST.update(
    marat=dict(make=marat, body=marat_body, bust_body=lambda P: marat_body(P, rest=True), feet=1700, fig_s=0.47, name='Марат',
               bg=('#f2b878', '#9a5630', '#2a1a16'), rim='#ffe2b0',
               neutral=dict(smile=1.25, open=5.5, teeth=1, tongue=1, low=0.75, squint=0.4, brow_in=0.35, brow_out=0.5, wide=0.3),
               expr={'Радость': dict(smile=1.5, open=10.5, teeth=1, tongue=1, low=0.85, squint=0.5, lid=0.1, brow_in=0.6, brow_out=0.7, wide=0.5, nod=-6),
                     'Удивление': dict(brow_in=1.4, brow_out=1.2, lid=0.8, open=9, low=-0.2, tongue=1, nod=-2),
                     'Грусть': dict(brow_in=1.3, brow_out=-0.7, knit=0.3, lid=-0.35, sad=1.0, gy=2.2, low=0.2, nod=10, tilt=-4),
                     'Гнев': dict(knit=1.4, brow_in=-1.0, brow_out=0.5, lid=0.1, squint=0.5, sad=0.5, open=4, teeth=1, snarl=1, nod=8, tilt=-5)}),
    kira=dict(make=kira, body=kira_body, bust_body=lambda P: kira_body(P, rest=True), feet=1470, name='Кира',
              bg=('#a892bc', '#4e3c60', '#17131d'), rim='#dcf78e',
              neutral=dict(lid=-0.3, knit=0.45, brow_in=-0.45, brow_out=0.1, smile=(-0.15, 0.55), sad=0.15, gx=-2.2, gy=-1.6, low=0.15),
              expr={'Радость': dict(smile=(0.25, 1.15), low=0.45, lid=-0.1, brow_in=0.2, brow_out=(0.2, 0.7), gx=-1.5, gy=-0.8, nod=-5),
                    'Удивление': dict(brow_in=1.2, brow_out=1.0, lid=0.75, open=4.5, low=-0.2, nod=-9, tilt=3),
                    'Грусть': dict(brow_in=1.2, brow_out=-0.6, knit=0.3, lid=-0.4, sad=1.0, gy=2.4, gx=1.0, low=0.2, nod=6),
                    'Гнев': dict(knit=1.3, brow_in=-1.0, brow_out=0.5, lid=0.05, squint=0.5, sad=0.6, open=3.2, teeth=1, snarl=1, gy=-1.2, nod=3)}),
)
