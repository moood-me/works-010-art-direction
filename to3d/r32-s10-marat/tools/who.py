"""Who is built here: Марат of the С10 drawing (styles/s10-ligne-claire/tools/marat.py).
Every tool of this folder takes the character's measures from this file."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, '../../..')
LC = os.path.join(REPO, 'styles/s10-ligne-claire/tools')
sys.path.insert(0, LC)
sys.path.insert(0, os.path.join(REPO, 'engine/tools'))

ID = 'marat'
RU = 'Марат'
SOURCE = 'to3d/r32-s10-marat'
BASE_BODY = 'moood-man'
K = 1.60 / 1114          # metres per drawing unit — the same as Савелий Петрович's (Р2) and Вера's (Р31)
FLOOR = 1300.0           # the drawing's floor (marat.figure)
DROP = 28.0              # the head sits this much lower on the figure (marat.figure: head_drop)
EYE = (30.0, 3.0)        # the drawing's eye on the face (x, y), before the drop
PANEL = '#dbe3c8'
BAND = '#c3c5ac'         # the floor band of the moving pictures: the panel mixed with #7a6a58, as build.figure does
MOUTH_Y = 67 + DROP      # the mouth (marat.MOUTH) in the figure's frame; it is drawn on the beard
PORTRAIT_S = 1.3         # build6: his portrait is drawn a little farther off
FACE_REST = {'up': 12, 'low': 7}     # the live face's rest: eyes narrowed by the smile (marat.REST: lid 0.5, squint 1)
HEAD_PIECES = ('hair', 'beard')      # the drawing's own pieces on the head (steps.py)
EXPR_SHEET = [('calm', 'как всегда'), ('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('anger', 'злость')]


def head():
    import marat
    return marat.head()


def rest_expr():
    import marat
    return marat.REST


def colours():
    import marat
    return dict(marat.COL)
NOSE_W = 1.5             # the base's nose made broader before the fit (fit_head.py)
NOSE_SNAP = 0.85         # how far the nose's vertices are set onto the drawing's steep-sided nose (fit_head.py)
HEAD_SHIFT = (-34, -38)  # the drawing's pose leans him back: at the head's height the body is shifted so (marat.figure: spine)
EXPR_S = 1.2             # the expression sheet's scale (a big head)
