"""Full figures: each character's head (cast.py) on a body with clothes, in one pose.

A Figure gives parts(res) and get_marks(expr, view) like a Head, so scene.render can draw it alone or with others.
Bodies are built from body.py pieces in the head's units (crown to chin about 200, y down, z toward the viewer).
The figure's floor is at FLOOR[name]; its neck sits on the head's neck.
"""
import numpy as np
import cast, body as B
from hands import hand
from head import Shell, Mark, lock_part
from cast import wrapdeg


class Figure:
    def __init__(self, head, build, marks=None, bust_only=False):
        self.head, self.build, self.extra_marks, self.bust_only = head, build, marks, bust_only

    def parts(self, res):
        ps = self.head.parts(res)
        ps += self.build(res, self.bust_only)
        return ps

    def get_marks(self, expr, view):
        out = self.head.get_marks(expr, view)
        if self.extra_marks:
            out += self.extra_marks(expr, view, self.bust_only)
        return out


def inset(rows, d, y0=None, y1=None):
    """Rows of a garment shell made d smaller (d < 0: larger) all round; optionally cut to [y0, y1]."""
    out = [(y, w - d, zm, zf - d, zb + d, n) for (y, w, zm, zf, zb, n) in rows]
    if y0 is not None:
        out = [r for r in out if r[0] >= y0]
    if y1 is not None:
        out = [r for r in out if r[0] <= y1]
    return out


def open_front(gap):
    """keep() for a garment shell open at the front by gap degrees each side of the middle."""
    def keep(X, Y, Z, a):
        return np.abs(wrapdeg(a)) > gap
    return keep


def vneck(depth_y, top_y, width_deg):
    """keep() for a garment with a V opening from top_y down to depth_y."""
    def keep(X, Y, Z, a):
        d = np.abs(wrapdeg(a))
        t = np.clip((depth_y - Y) / (depth_y - top_y), 0, 1)
        return d > width_deg * t
    return keep


# ---------------------------------------------------------------------------------------------------- Аня
ANYA_COL = {'cardigan': '#e0a43c', 'blouse': '#fbf6ea', 'skirt': '#2e6b78', 'shoe': '#7b2f1e',
            'book': '#a23c2a', 'pages': '#f3ead2', 'tights': '#4a3b45'}


def anya_figure(bust=False):
    h, col = cast.anya()
    col = dict(col, **ANYA_COL)
    TORSO = [
        (124, 34, -8, 26, -40, 2.0),
        (142, 86, -10, 44, -60, 2.2),
        (166, 126, -12, 56, -68, 2.4),
        (200, 132, -10, 68, -72, 2.6),
        (250, 126, -6, 80, -70, 2.6),
        (315, 108, -4, 66, -66, 2.6),
        (380, 104, -2, 64, -68, 2.6),
        (440, 126, 0, 74, -80, 2.5),
        (480, 136, 0, 80, -86, 2.4),
    ]
    torso = Shell(TORSO)
    blouse = Shell(inset(TORSO, 8, y1=380) + [(420, 104, -1, 60, -66, 2.6)])
    skirt = Shell([
        (380, 92, -2, 54, -58, 2.4),
        (440, 116, 0, 64, -70, 2.3),
        (560, 136, 2, 78, -82, 2.2),
        (700, 150, 4, 88, -90, 2.1),
        (790, 156, 4, 92, -94, 2.0),
    ])
    floor = 1150

    def build(res, bust_only):
        ps = [blouse.part('blouse', 'blouse', res, y1=430),
              torso.part('cardigan', 'cardigan', res, open_front(14))]
        # Peter Pan collar: two round flaps
        for s in (1, -1):
            ps.append(lock_part(blouse, [(s * -2, 132), (s * -18, 136), (s * -34, 134), (s * -44, 128)],
                                [9, 12, 11, 6], lift=2.5, name=f'collar{s}', material='blouse', res=res, curl=1))
        # arms: her right (x < 0) holds a book to her chest, the left hangs
        ps.append(B.tube('armR', 'cardigan', [(-118, 196, -6), (-140, 290, 0), (-134, 372, 22), (-80, 342, 92),
                                              (-48, 324, 108)], [33, 31, 28, 26, 25], res))
        ps.append(B.tube('armL', 'cardigan', [(118, 196, -6), (140, 290, -8), (140, 380, -4), (134, 460, 6),
                                              (130, 490, 12)], [33, 31, 28, 26, 25], res))
        # the book, held against the chest
        ps.append(B.box('book', 'book', (10, 300, 104), (110, 150, 22), res, rot=(8, -14, -14)))
        if bust_only:
            return ps
        ps.append(skirt.part('skirt', 'skirt', res))
        for s in (1, -1):
            ps.append(B.tube(f'leg{s}', 'tights', [(s * 52, 760, 2), (s * 48, 880, 6), (s * 44, 960, 2),
                                                   (s * 42, 1060, -2), (s * 40, floor - 44, -4)],
                                                   [52, 40, 44, 32, 24], res))
            ps.append(B.blob(f'shoe{s}', 'shoe', (s * 40, floor - 22, 24), (24, 20, 52), res))
        return ps

    def marks(expr, view, bust_only):
        ms = []
        # buttons down the blouse, the cardigan's edges and cuffs, a pocket
        c = blouse.curve
        for y in (175, 225, 275, 325):
            P = c([(0, y)])[0] + [0, 0, 2]
            ms += B.dots3([P], 3.2, '#fbf6ea', on='blouse')
        tc = torso.curve
        for s in (1, -1):
            ms.append(Mark(tc([(s * -55, 420), (s * -85, 420)]), w=0.6, on='cardigan'))
        ms.append(B.ring_mark((140, 455, 6), (-0.08, 1, 0.1), 29, on='cardigan'))
        ms.append(B.ring_mark((-80, 340, 92), (1, -0.4, 0.3), 29, on='cardigan'))
        # cardigan ribbing at the hem
        ms.append(Mark(tc([(d, 470) for d in range(-180, 181, 5)]), w=0.6, on='cardigan'))
        if not bust_only:
            sk = skirt.curve
            for d in (-40, 0, 40, 140, -140):
                ms.append(Mark(sk([(d, 500), (d * 1.05, 650), (d * 1.1, 785)]), w=0.6, on='skirt'))
        ms.append(hand((130, 494, 14), (128, 600, 20), 'hang', col['skin'], 128, flip=True, tol=40))
        ms.append(hand((-50, 322, 112), (60, 290, 130), 'grip', col['skin'], 135, flip=False, tol=40))
        return ms
    return Figure(h, build, marks, bust), col, floor


def watch_glyph(gold='#d9a837'):
    """A pocket watch, drawn flat: case, white face, two hands, the bow on top."""
    import numpy as np
    circ = lambda r, cx=0, cy=0: [(cx + r * np.cos(a), cy + r * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 33)[:-1]]
    return [(circ(12, 0, -44), gold, 1.0, True),
            (circ(44), gold, 1.0, True),
            (circ(35), '#fbf8ee', 0.7, True),
            ([(0, 0), (0, -24)], None, 0.8, False),
            ([(0, 0), (15, 8)], None, 0.8, False)]


# ---------------------------------------------------------------------------------------------------- Савелий
SAVELY_COL = {'vest': '#5a3a2a', 'shirt': '#f3eee0', 'trousers': '#7c7f86', 'shoe': '#2a2420', 'tie': '#9b2a22'}


def savely_figure(bust=False):
    import numpy as np
    from head import Glyph
    h, col = cast.savely()
    col = dict(col, **SAVELY_COL)
    TORSO = [
        (126, 40, -14, 22, -50, 2.0),
        (144, 100, -14, 42, -66, 2.2),
        (168, 140, -16, 54, -76, 2.4),
        (205, 146, -16, 70, -82, 2.6),
        (260, 140, -14, 84, -82, 2.6),
        (330, 136, -16, 94, -80, 2.6),
        (400, 138, -20, 90, -84, 2.6),
        (450, 142, -22, 78, -92, 2.5),
    ]
    vest = Shell(inset(TORSO, -2, y1=450))
    shirt = Shell(inset(TORSO, 6, y1=450))
    hips = Shell([(400, 134, -20, 84, -82, 2.5), (450, 140, -22, 78, -90, 2.5), (500, 140, -24, 70, -92, 2.4),
                  (540, 132, -26, 64, -92, 2.2)])
    floor = 1090

    def build(res, bust_only):
        ps = [shirt.part('shirt', 'shirt', res), vest.part('vest', 'vest', res, vneck(300, 140, 26))]
        # shirt collar points and the bow tie
        for s in (1, -1):
            ps.append(lock_part(shirt, [(s * -4, 124), (s * -14, 134), (s * -22, 146)], [8, 9, 0], lift=3,
                                name=f'col{s}', material='shirt', res=res))
            ps.append(B.blob(f'bow{s}', 'tie', (s * 16, 142, 48), (16, 10, 6), res, rot=(0, 0, s * -10)))
        ps.append(B.blob('knot', 'tie', (0, 142, 52), (7, 8, 6), res))
        # right arm raised, holding the watch up to his eyes; left arm behind the back
        ps.append(B.tube('armR', 'shirt', [(-134, 196, -14), (-158, 300, -6), (-150, 372, 30), (-96, 300, 104),
                                           (-80, 262, 120)], [36, 33, 30, 27, 26], res))
        ps.append(B.tube('armL', 'shirt', [(134, 196, -14), (154, 300, -26), (140, 380, -70), (80, 410, -112)],
                         [36, 33, 30, 27], res))
        if bust_only:
            return ps
        ps.append(hips.part('hips', 'trousers', res))
        for s in (1, -1):
            ps.append(B.tube(f'leg{s}', 'trousers', [(s * 66, 520, -26), (s * 62, 700, -14), (s * 58, 860, -24),
                                                     (s * 56, floor - 60, -30)], [62, 54, 48, 44], res))
            ps.append(B.blob(f'shoe{s}', 'shoe', (s * 58, floor - 24, -2), (30, 24, 60), res))
        return ps

    def marks(expr, view, bust_only):
        ms = []
        vc = vest.curve
        for y in (310, 352, 394):
            ms += B.dots3([vc([(0, y)])[0] + [0, 0, 1]], 4.5, '#c9a35a', on='vest')
        # the watch chain from a button to the pocket, and the pocket welts
        ms.append(Mark(vc([(0, 352), (14, 370), (30, 368), (44, 346)]), w=0.9, on='vest', stroke='#a87a1e'))
        for s in (1, -1):
            ms.append(Mark(vc([(s * 30, 360), (s * 52, 356)]), w=0.6, on='vest'))
            ms.append(Mark(vc([(s * 32, 250), (s * 52, 246)]), w=0.6, on='vest'))
            ms.append(Mark(vc([(s * 2, 420), (s * 6, 448)]), w=0.6, on='vest'))
        # cuff of the raised arm, and the watch in the hand
        ms.append(B.ring_mark((-100, 302, 102), (1, -0.8, 0.3), 27, on='shirt'))
        ms.append(Glyph((-62, 236, 140), (-62, 300, 140), watch_glyph(), 48, tol=60))
        ms.append(hand((-84, 262, 124), (-30, 258, 140), 'fist', col['skin'], 120, tol=60))
        ms.append(Mark(np.array([(-62, 236, 140), (-70, 280, 128), (-40, 330, 96), (10, 356, 90)]), w=0.8,
                       stroke='#a87a1e', tol=40))
        if not bust_only:
            for s in (1, -1):
                ms.append(Mark(hips.curve([(s * 40, 500), (s * 44, 540)]), w=0.6, on='trousers'))
        return ms
    return Figure(h, build, marks, bust), col, floor


# ---------------------------------------------------------------------------------------------------- Тим
TIM_COL = {'jumper': '#5d8a48', 'shorts': '#2c3f6b', 'sock': '#efeae0', 'shoe': '#b3332a', 'sole': '#fbf8ee',
           'patch': '#a8743c', 'sling': '#8a5a2c'}


def tim_figure(bust=False):
    import numpy as np
    from head import Glyph
    h, col = cast.tim()
    col = dict(col, **TIM_COL)
    TORSO = [
        (116, 30, -6, 20, -36, 2.0),
        (132, 74, -8, 36, -50, 2.2),
        (154, 102, -8, 44, -56, 2.4),
        (200, 104, -6, 58, -60, 2.6),
        (260, 100, -4, 62, -60, 2.6),
        (320, 102, -2, 62, -62, 2.6),
        (356, 108, 0, 60, -64, 2.4),
    ]
    jumper = Shell(TORSO)
    shorts = Shell([(330, 98, 0, 54, -58, 2.4), (380, 106, 0, 58, -64, 2.4), (420, 108, 0, 58, -66, 2.4)])
    floor = 970

    def build(res, bust_only):
        ps = [jumper.part('jumper', 'jumper', res)]
        # left hand in the pocket (the arm ends at the pocket), right hand behind the back with a slingshot
        ps.append(B.tube('armL', 'jumper', [(102, 166, -6), (118, 250, -4), (112, 320, 14), (88, 372, 34)],
                         [27, 25, 23, 22], res))
        ps.append(B.tube('armR', 'jumper', [(-102, 166, -6), (-120, 250, -12), (-112, 320, -50), (-60, 340, -92)],
                         [27, 25, 23, 22], res))
        if bust_only:
            return ps
        ps.append(shorts.part('shorts', 'shorts', res))
        for s in (1, -1):
            ps.append(B.tube(f'short{s}', 'shorts', [(s * 52, 400, 0), (s * 58, 500, 4)], [52, 50], res))
            ps.append(B.tube(f'leg{s}', 'skin', [(s * 50, 490, 2), (s * 48, 600, 6), (s * 46, 700, 2)], [28, 24, 27],
                             res))
            ps.append(B.tube(f'sock{s}', 'sock', [(s * 46, 690, 2), (s * 45, 800, 0), (s * 44, floor - 40, -2)],
                             [29, 24, 19], res))
            ps.append(B.blob(f'shoe{s}', 'shoe', (s * 46, floor - 26, 16), (25, 22, 46), res))
            ps.append(B.blob(f'sole{s}', 'sole', (s * 46, floor - 10, 14), (27, 9, 49), res))
        return ps

    def marks(expr, view, bust_only):
        ms = []
        jc = jumper.curve
        # ribbing at the hem and the neck, a patch on the elbow
        ms.append(Mark(jc([(d, 340) for d in range(-180, 181, 5)]), w=0.6, on='jumper'))
        for d in range(-170, 171, 12):
            ms.append(Mark(jc([(d, 342), (d, 354)]), w=0.45, on='jumper'))
        ms.append(Mark(jc([(d, 124) for d in range(-180, 181, 5)]) + [0, 0, 2], w=0.6, on='jumper'))
        ms.append(B.ring_mark((90, 368, 34), (-0.4, 1, 0.4), 23, on='jumper'))
        # the slingshot peeking from behind his back
        sl = [([(-4, 0), (-4, 60), (-26, 100), (-18, 104), (0, 72), (18, 104), (26, 100), (4, 60), (4, 0)],
               col['sling'], 1.0, True),
              ([(-22, 102), (0, 120), (22, 102)], None, 0.8, False)]
        ms.append(Glyph((-140, 330, -60), (-150, 230, -60), sl, 80, tol=200))
        if not bust_only:
            for s in (1, -1):
                for y in (700, 714):
                    ms.append(B.ring_mark((s * 46, y, 2), (0, 1, 0), 28.5, on='sock', w=1.6))
                ms.append(Mark(np.array([(s * 46 + 6, floor - 50, 40), (s * 46 + 16, floor - 40, 44)]), w=0.6,
                               on='shoe'))
            # a plaster on his knee
            ms.append(Mark(np.array([(40, 594, 30), (58, 588, 26), (60, 600, 26), (42, 606, 30)]), kind='shape',
                           fill='#e8c49a', w=0.6, on='skin'))
            ms.append(Mark(shorts.curve([(30, 380), (36, 408)]), w=0.6, on='shorts'))
        return ms
    return Figure(h, build, marks, bust), col, floor


# ---------------------------------------------------------------------------------------------------- Вера
VERA_COL = {'jacket': '#3c4a63', 'blouse': '#f1ead8', 'skirt': '#5c6068', 'tights': '#3a3236', 'shoe': '#1e1a1c',
            'folder': '#d8c48e', 'paper': '#fbf8ee'}


def vera_figure(bust=False):
    import numpy as np
    h, col = cast.vera()
    col = dict(col, **VERA_COL)
    TORSO = [
        (130, 32, -10, 22, -40, 2.0),
        (148, 86, -10, 40, -58, 2.2),
        (172, 124, -12, 52, -64, 2.4),
        (210, 128, -10, 64, -68, 2.6),
        (265, 118, -6, 74, -66, 2.6),
        (335, 98, -4, 58, -60, 2.6),
        (405, 94, -2, 56, -60, 2.6),
        (460, 118, 0, 64, -70, 2.5),
        (505, 128, 0, 68, -76, 2.4),
    ]
    jacket = Shell(TORSO)
    blouse = Shell(inset(TORSO, 7, y1=405))
    skirt = Shell([(400, 88, -2, 52, -56, 2.4), (470, 116, 0, 62, -68, 2.4), (600, 116, 0, 62, -68, 2.3),
                   (760, 106, 0, 58, -64, 2.2)])
    floor = 1290

    def build(res, bust_only):
        ps = [blouse.part('blouse', 'blouse', res), jacket.part('jacket', 'jacket', res, vneck(330, 140, 30))]
        # a high blouse collar and the jacket's lapels
        ps.append(B.tube('collar', 'blouse', [(-28, 118, 6), (0, 124, 26), (28, 118, 6)], [8, 8, 8], res))
        for s in (1, -1):
            ps.append(lock_part(jacket, [(s * -12, 142), (s * -24, 190), (s * -30, 250), (s * -26, 320)],
                                [10, 20, 14, 0], lift=3, name=f'lapel{s}', material='jacket', res=res))
        # left arm holds a folder against her hip; right arm hangs
        ps.append(B.tube('armL', 'jacket', [(124, 196, -6), (146, 300, -8), (148, 390, 10), (110, 440, 50)],
                         [33, 31, 28, 26], res))
        ps.append(B.tube('armR', 'jacket', [(-124, 196, -6), (-144, 300, -6), (-146, 400, 0), (-140, 480, 8)],
                         [33, 31, 28, 26], res))
        ps.append(B.box('folder', 'folder', (112, 470, 74), (40, 230, 170), res, rot=(0, -20, -8)))
        if bust_only:
            return ps
        ps.append(skirt.part('skirt', 'skirt', res))
        for s in (1, -1):
            ps.append(B.tube(f'leg{s}', 'tights', [(s * 42, 740, 0), (s * 38, 880, 6), (s * 34, 1020, 2),
                                                   (s * 30, floor - 44, -4)], [46, 34, 38, 22], res))
            ps.append(B.blob(f'shoe{s}', 'shoe', (s * 30, floor - 20, 22), (21, 17, 48), res, rot=(-8, 0, 0)))
        return ps

    def marks(expr, view, bust_only):
        ms = []
        jc = jacket.curve
        for y in (360, 420):
            ms += B.dots3([jc([(0, y)])[0] + [0, 0, 1.5]], 4.5, '#1e2534', on='jacket')
        for s in (1, -1):
            ms.append(Mark(jc([(s * 30, 452), (s * 58, 450)]), w=0.6, on='jacket'))
            ms.append(Mark(jc([(s * 40, 230), (s * 44, 330), (s * 40, 410)]), w=0.55, on='jacket'))
        ms.append(B.ring_mark((-140, 470, 8), (0.05, 1, 0.08), 26, on='jacket'))
        ms.append(hand((-140, 488, 10), (-138, 600, 14), 'hang', col['skin'], 140, flip=False, tol=40))
        ms.append(hand((104, 444, 56), (60, 520, 110), 'grip', col['skin'], 135, flip=True, tol=60))
        if not bust_only:
            ms.append(Mark(skirt.curve([(-20, 620), (-22, 758)]), w=0.6, on='skirt'))
        return ms
    return Figure(h, build, marks, bust), col, floor
