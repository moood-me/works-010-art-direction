"""Аня, about 20: warm, trusting, dreamy. Long loose ginger-chestnut hair, freckles, a mustard cardigan over a
sea-green dress. Head units: crown about y=-125, chin y=100; the face looks to the viewer's left in '34'."""
from kit import ink, dot, wash, blot, scribble, hatch
from parts import eye, brow, mouth, hand, shade, strand, EXPR, SKIN, BLUSH

HAIR = '#c96f36'
CARDI = '#eeb43e'
DRESS = '#6fb3a0'


def freckles(d, pts):
    for x, y in pts:
        dot(d, x, y, 0.9)


def head34(d, expr='dream', hair=True):
    e = EXPR[expr]
    # --- washes ---
    wash(d, [(-60, -86), (-72, -30), (-86, 20), (-70, 50), (-62, 86), (-40, 100), (10, 96), (50, 60), (58, 0),
             (40, -70), (0, -96)], SKIN, 0.5, dx=5, dy=3)
    blot(d, -50, 34, 14, BLUSH, 0.42)
    blot(d, 14, 30, 18, BLUSH, 0.38)
    # --- face contour: forehead, brow, nose, then lips and chin ---
    ink(d, [(-52, -78), (-62, -46), (-68, -22), (-67, -10), (-78, 10), (-90, 24), (-86, 29), (-74, 30)],
        w=2.0, start=0.4, end=0.25)
    ink(d, [(-73, 39), (-77, 45), (-72, 51), (-76, 58), (-70, 70), (-62, 86), (-48, 98), (-30, 102)],
        w=2.0, start=0.3, end=0.2)
    ink(d, [(-20, 101), (16, 92), (44, 66)], w=1.4, start=0.2, end=0.1)
    # nostril
    ink(d, [(-80, 26), (-74, 22)], w=1.0)
    # eyes
    eye(d, -18, -6, 1.15 * e['eye'], e['look'], e['lid'], lash=True, side=1, squint=e.get('squint', False), seed=11)
    eye(d, -60, -7, 0.85 * e['eye'], e['look'], e['lid'], lash=True, side=-1, squint=e.get('squint', False), seed=12)
    brow(d, -16, -30, 26, e['lift'], e['tilt'], side=1, w=1.3, seed=13)
    brow(d, -60, -31, 14, e['lift'], e['tilt'] * 0.6, side=-1, w=1.1, arch=2, seed=14)
    mouth(d, -60, 50, e['mouth'], 1.0, side=-1)
    freckles(d, [(-40, 18), (-34, 24), (-44, 26), (-28, 17), (-2, 20), (6, 26), (-8, 28)])
    if hair:
        hair34(d)


def hair34(d):
    # wash: one big loose wavy mass, behind the face and down past the shoulders; light left on the crown
    wash(d, [(-50, -128), (10, -142), (70, -120), (108, -70), (124, 0), (122, 70), (138, 140), (128, 210),
             (140, 260), (96, 270), (70, 220), (64, 140), (56, 60), (56, -10), (36, -66), (-10, -96), (-48, -86),
             (-70, -96)], HAIR, 0.6, dx=-3, dy=2)
    wash(d, [(-78, -96), (-46, -128), (-24, -104), (-56, -76), (-70, -40), (-84, -64)], HAIR, 0.5)
    wash(d, [(20, -120), (60, -100), (80, -40), (70, 40), (60, -30), (30, -80)], '#a8552a', 0.35)
    # outer line, in three pen strokes
    ink(d, [(-80, -78), (-66, -112), (-30, -136), (16, -142), (60, -126)], w=2.3, start=0.5, end=0.3)
    ink(d, [(56, -128), (96, -100), (116, -50), (122, 0), (116, 50), (126, 100), (136, 150)], w=2.1, start=0.3, end=0.2)
    ink(d, [(134, 146), (124, 190), (138, 230), (130, 262), (112, 272)], w=1.7, start=0.4, end=0.05)
    # parting; the front lock sweeps over the forehead and falls down by the cheek of the near side
    ink(d, [(-20, -132), (-48, -114), (-66, -94), (-78, -66), (-74, -50)], w=1.7, end=0.1)
    ink(d, [(-14, -130), (14, -104), (40, -78), (54, -36), (52, 12), (60, 60), (58, 110), (70, 160), (62, 210),
            (74, 250)], w=1.9, start=0.6, end=0.05)
    # locks with waves
    for k, (x0, y0, x1, y1) in enumerate([(2, -128, 84, 200), (22, -124, 100, 240), (44, -114, 118, 170),
                                          (66, -100, 112, 90), (32, -100, 80, 60), (80, 40, 96, 262)]):
        strand(d, x0, y0, x1, y1, amp=7, waves=1.6, w=0.9, phase=k * 0.3, seed=100 + k)
    strand(d, -34, -122, -70, -70, amp=3, waves=0.8, w=0.9, seed=120)
    strand(d, -26, -126, -60, -96, amp=2, waves=0.6, w=0.8, seed=121)
    # loose ends
    ink(d, [(96, 262), (106, 276), (118, 274)], w=1.0, end=0.1)
    ink(d, [(78, 236), (72, 262), (82, 280)], w=1.0, end=0.1)


def neck_and_shoulders(d):
    wash(d, [(-30, 96), (20, 92), (34, 170), (-30, 176)], SKIN, 0.45, dx=3)
    ink(d, [(-28, 102), (-30, 136), (-26, 168)], w=1.6, end=0.2)
    ink(d, [(26, 86), (30, 130), (40, 160)], w=1.4, end=0.2)
    shade(d, [(-24, 104), (22, 96), (26, 122), (-20, 126)], 0.22)


def bust(d, expr='dream'):
    """Head and shoulders, in a 600 x 720 frame."""
    d.push(300, 300, 1.05, -5)
    # cardigan and dress: washes looser than the lines, white paper left on the near shoulder
    wash(d, [(-150, 200), (-90, 180), (-34, 178), (-14, 250), (30, 176), (90, 170), (150, 196), (176, 280),
             (186, 380), (-200, 380), (-190, 270)], CARDI, 0.6, dy=6)
    wash(d, [(-34, 172), (40, 164), (30, 214), (6, 266), (-14, 256)], DRESS, 0.62)
    neck_and_shoulders(d)
    head34(d, expr)
    # shoulders: a soft knit, broken line
    ink(d, [(-28, 170), (-80, 182), (-136, 200), (-170, 240), (-186, 310), (-192, 380)], w=2.2, start=0.6, end=0.2)
    ink(d, [(40, 162), (96, 170), (142, 192), (166, 240), (176, 330)], w=2.0, start=0.6, end=0.2)
    ink(d, [(-36, 174), (-22, 228), (4, 266), (22, 214), (40, 164)], w=1.5, start=0.3, end=0.3)     # neckline
    ink(d, [(-58, 182), (-40, 262), (-24, 380)], w=1.8, start=0.4, end=0.1)                          # cardigan edge
    ink(d, [(62, 170), (44, 262), (34, 380)], w=1.8, start=0.4, end=0.1)
    for y in (296, 346):
        ink(d, [(-26, y), (-20, y - 4), (-15, y + 1), (-21, y + 5), (-26, y)], w=1.0, retrace=0)
    # a fold or two
    ink(d, [(-150, 260), (-140, 300), (-146, 340)], w=1.0, start=0.3, end=0.1)
    ink(d, [(130, 250), (120, 300)], w=1.0, start=0.3, end=0.1)
    d.pop()
