"""Hands, drawn: in ligne claire a hand is a clear, simple shape — a square palm, fingers nearly as long, the
thumb set apart, a few short lines between the fingers — so they are drawn as 2D shapes pinned to the 3D wrist.
Each shape: fingers point down (+y), the wrist is at (0, 0), the hand is 100 long; x > 0 is the thumb side of a
right hand seen from its back.  Use head.Glyph(anchor, toward, HANDS[k](skin), length, flip)."""
from head import Glyph


def hang(skin):
    """Relaxed, hanging by the side, seen from the outside: back of the hand, fingers a little curled, thumb in front."""
    out = [(-12, 0), (-14, 18), (-17, 38), (-18, 52), (-17, 66), (-14, 80), (-9, 92), (-3, 98), (3, 98), (7, 93),
           (8, 84), (7, 74), (10, 66), (15, 60), (18, 52), (17, 46), (13, 42), (12, 22), (11, 0)]
    return [(out, skin, 1.0, True),
            ([(-8, 56), (-6, 74), (-4, 88)], None, 0.55, False),
            ([(0, 58), (2, 70), (3, 80)], None, 0.55, False),
            ([(8, 48), (13, 54)], None, 0.55, False)]


def grip(skin):
    """Holding something flat (a book, a folder) against the body: back of the hand, the fingers over the edge."""
    out = [(-13, 0), (-15, 16), (-19, 34), (-21, 46), (-21, 62), (-20, 78), (-18, 88), (-14, 92), (-10, 90),
           (-8, 94), (-3, 97), (1, 95), (4, 97), (9, 95), (12, 91), (15, 90), (18, 84), (20, 72), (21, 56), (20, 44),
           (17, 32), (14, 16), (13, 0)]
    return [(out, skin, 1.0, True),
            ([(-10, 64), (-10, 90)], None, 0.55, False),
            ([(-1, 66), (0, 95)], None, 0.55, False),
            ([(8, 64), (10, 91)], None, 0.55, False)]


def fist(skin):
    """A loose fist seen from the back of the hand."""
    out = [(-13, 0), (-16, 18), (-20, 38), (-21, 52), (-19, 64), (-13, 70), (-5, 72), (4, 72), (12, 70), (18, 64),
           (21, 54), (20, 44), (16, 36), (14, 18), (13, 0)]
    return [(out, skin, 1.0, True),
            ([(-12, 56), (-11, 68)], None, 0.55, False),
            ([(-3, 58), (-3, 70)], None, 0.55, False),
            ([(6, 58), (6, 70)], None, 0.55, False),
            ([(10, 44), (19, 50)], None, 0.55, False)]


def open_palm(skin):
    """Open, fingers together, the palm up or toward us, the thumb apart (holding something small)."""
    out = [(-13, 0), (-15, 18), (-18, 38), (-19, 52), (-19, 70), (-18, 84), (-14, 93), (-9, 94), (-7, 97), (-2, 99),
           (2, 98), (5, 100), (10, 98), (13, 94), (16, 86), (17, 70), (17, 56), (21, 48), (28, 40), (30, 34),
           (26, 30), (19, 34), (15, 24), (13, 0)]
    return [(out, skin, 1.0, True),
            ([(-9, 60), (-9, 93)], None, 0.55, False),
            ([(0, 60), (0, 98)], None, 0.55, False),
            ([(8, 60), (9, 97)], None, 0.55, False),
            ([(-12, 40), (6, 46)], None, 0.55, False)]


HANDS = dict(hang=hang, grip=grip, fist=fist, open=open_palm)


def hand(anchor, toward, kind, skin, length, flip=False, tol=12.0):
    return Glyph(anchor, toward, HANDS[kind](skin), length, flip, tol=tol)
