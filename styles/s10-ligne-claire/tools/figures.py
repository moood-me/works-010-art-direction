"""Full figures: each character's head (cast.py) on a body with clothes, in one pose.

A Figure gives parts(res) and get_marks(expr, view) like a Head, so scene.render can draw it alone or with others.
Bodies are built from body.py pieces in the head's units (crown to chin about 200, y down, z toward the viewer).
The figure's floor is at FLOOR[name]; its neck sits on the head's neck.
"""
import numpy as np
import cast, body as B
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
    torso = Shell([
        (126, 34, -8, 26, -40, 2.0),
        (146, 76, -10, 42, -56, 2.2),
        (170, 112, -12, 52, -62, 2.4),
        (205, 118, -10, 62, -64, 2.6),
        (255, 108, -6, 72, -62, 2.6),
        (320, 90, -4, 58, -58, 2.6),
        (395, 78, -2, 50, -56, 2.6),
        (455, 92, 0, 54, -62, 2.6),
        (515, 104, 0, 58, -68, 2.5),
    ])
    blouse = Shell([
        (120, 30, -8, 20, -38, 2.0),
        (146, 72, -10, 38, -54, 2.2),
        (170, 108, -12, 48, -60, 2.4),
        (255, 104, -6, 68, -60, 2.6),
        (395, 74, -2, 46, -54, 2.6),
        (430, 78, -1, 46, -56, 2.6),
    ])
    skirt = Shell([
        (395, 80, -2, 50, -56, 2.4),
        (470, 100, 0, 60, -64, 2.3),
        (600, 116, 2, 70, -72, 2.2),
        (760, 128, 4, 80, -80, 2.1),
        (850, 134, 4, 84, -84, 2.0),
    ])
    floor = 1216

    def build(res, bust_only):
        ps = [blouse.part('blouse', 'blouse', res, y1=430),
              torso.part('cardigan', 'cardigan', res, open_front(14))]
        # Peter Pan collar: two round flaps
        for s in (1, -1):
            ps.append(lock_part(blouse, [(s * -2, 132), (s * -18, 136), (s * -34, 134), (s * -44, 128)],
                                [9, 12, 11, 6], lift=2.5, name=f'collar{s}', material='blouse', res=res, curl=1))
        # arms: her right (x < 0 on screen-left at yaw 0) holds a book to her chest, the left hangs
        ps.append(B.tube('armR', 'cardigan', [(-112, 182, -6), (-126, 300, 0), (-112, 372, 18), (-64, 330, 78),
                                              (-36, 312, 92)], [30, 27, 24, 21, 19], res))
        ps.append(B.tube('armL', 'cardigan', [(112, 182, -6), (128, 290, -8), (126, 380, -4), (116, 470, 6),
                                              (110, 505, 12)], [30, 27, 24, 21, 20], res))
        ps += B.hand('handL', (108, 532, 16), (-0.1, 1, 0.15), res, size=1.1, side=-1)
        ps += B.hand('handR', (-26, 300, 104), (1, -0.35, 0.1), res, size=1.1, rot=60, side=1)
        # the book, held against the chest
        ps.append(B.box('book', 'book', (6, 296, 92), (64, 88, 12), res, rot=(8, -12, -14)))
        if bust_only:
            return ps
        ps.append(skirt.part('skirt', 'skirt', res))
        for s in (1, -1):
            ps.append(B.tube(f'leg{s}', 'tights', [(s * 42, 820, 2), (s * 38, 960, 8), (s * 34, 1120, 0),
                                                   (s * 33, floor - 34, -2)], [30, 25, 24, 14], res))
            ps.append(B.blob(f'shoe{s}', 'shoe', (s * 33, floor - 16, 16), (16, 15, 34), res))
        return ps

    def marks(expr, view, bust_only):
        ms = []
        # buttons down the blouse, the cardigan's edges and cuffs, a pocket
        c = blouse.curve
        for y in (180, 230, 280, 330, 380):
            P = c([(0, y)])[0] + [0, 0, 2]
            ms += B.dots3([P], 3.2, '#fbf6ea', on='blouse')
        tc = torso.curve
        for s in (1, -1):
            ms.append(Mark(tc([(s * -60, 470), (s * -85, 470)]), w=0.6, on='cardigan'))
        ms.append(B.ring_mark((116, 470, 6), (-0.06, 1, 0.06), 23, on='cardigan'))
        ms.append(B.ring_mark((-64, 330, 78), (1, -0.4, 0.2), 22, on='cardigan'))
        # cardigan ribbing at the hem
        ms.append(Mark(tc([(d, 500) for d in range(-180, 181, 5)]), w=0.6, on='cardigan'))
        if not bust_only:
            sk = skirt.curve
            for d in (-40, 0, 40, 140, -140):
                ms.append(Mark(sk([(d, 470), (d * 1.05, 650), (d * 1.1, 845)]), w=0.6, on='skirt'))
        # pages edge of the book
        return ms
    return Figure(h, build, marks, bust), col, floor
