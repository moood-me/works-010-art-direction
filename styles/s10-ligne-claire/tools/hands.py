"""Hands, drawn: in ligne claire a hand is a clear, simple shape — a square palm, fingers nearly as long, the
thumb set apart, a few short lines between the fingers — so they are drawn as 2D shapes pinned to the 3D wrist.
Each shape: fingers point down (+y), the wrist is at (0, 0), the hand is 100 long; x > 0 is the thumb side of a
right hand seen from its back.  Use head.Glyph(anchor, toward, HANDS[k](skin), length, flip)."""
from head import Glyph


def hang(skin):
    """Relaxed, hanging by the side, seen from the outside: back of the hand, fingers a little curled, thumb in front."""
    out = [(-17, 0), (-20, 20), (-22, 42), (-21, 58), (-18, 74), (-13, 88), (-6, 97), (2, 99), (8, 95), (10, 86),
           (9, 76), (12, 68), (18, 62), (24, 56), (27, 48), (24, 42), (17, 38), (17, 20), (16, 0)]
    return [(out, skin, 1.0, True),
            ([(-11, 60), (-8, 76), (-4, 92)], None, 0.55, False),
            ([(-1, 60), (2, 74), (4, 86)], None, 0.55, False),
            ([(12, 50), (17, 56)], None, 0.55, False)]


def grip(skin):
    """Holding something flat (a book, a folder) against the body: back of the hand, the fingers over the edge."""
    out = [(-18, 0), (-21, 24), (-22, 48), (-21, 66), (-20, 82), (-16, 92), (-10, 96), (-5, 93), (0, 98), (6, 95),
           (10, 97), (15, 92), (19, 84), (21, 66), (20, 44), (18, 22), (16, 0)]
    return [(out, skin, 1.0, True),
            ([(-10, 70), (-8, 92)], None, 0.55, False),
            ([(0, 70), (0, 95)], None, 0.55, False),
            ([(9, 70), (10, 93)], None, 0.55, False)]


def fist(skin):
    """A loose fist seen from the back of the hand."""
    out = [(-18, 0), (-21, 22), (-23, 44), (-22, 60), (-17, 70), (-8, 74), (2, 75), (12, 73), (19, 66), (24, 56),
           (25, 44), (21, 36), (18, 20), (16, 0)]
    return [(out, skin, 1.0, True),
            ([(-12, 58), (-10, 72)], None, 0.55, False),
            ([(-2, 60), (-1, 74)], None, 0.55, False),
            ([(8, 59), (9, 72)], None, 0.55, False),
            ([(14, 46), (22, 50)], None, 0.55, False)]


def open_palm(skin):
    """Open, fingers together, the palm toward us (a gesture)."""
    out = [(-17, 0), (-21, 26), (-23, 46), (-22, 62), (-21, 82), (-17, 95), (-11, 99), (-6, 96), (-3, 100), (3, 101),
           (7, 98), (11, 100), (16, 96), (19, 86), (20, 66), (24, 54), (31, 46), (34, 38), (30, 33), (22, 36),
           (18, 24), (16, 0)]
    return [(out, skin, 1.0, True),
            ([(-11, 66), (-10, 96)], None, 0.55, False),
            ([(0, 66), (0, 99)], None, 0.55, False),
            ([(9, 66), (10, 98)], None, 0.55, False)]


HANDS = dict(hang=hang, grip=grip, fist=fist, open=open_palm)


def hand(anchor, toward, kind, skin, length, flip=False, tol=12.0):
    return Glyph(anchor, toward, HANDS[kind](skin), length, flip, tol=tol)
