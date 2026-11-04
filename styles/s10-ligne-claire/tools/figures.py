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
        ms.append(hand((130, 494, 14), (128, 600, 20), 'hang', col['skin'], 140, flip=True, tol=40))
        ms.append(hand((-50, 322, 112), (60, 290, 130), 'grip', col['skin'], 135, flip=False, tol=40))
        return ms
    return Figure(h, build, marks, bust), col, floor
