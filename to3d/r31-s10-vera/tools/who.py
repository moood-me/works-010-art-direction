"""Who is built here: Вера of the С10 drawing (styles/s10-ligne-claire/tools: cast.vera, figures.vera_figure).
Every tool of this folder takes the character's measures from this file."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, '../../..')
LC = os.path.join(REPO, 'styles/s10-ligne-claire/tools')
sys.path.insert(0, LC)
sys.path.insert(0, os.path.join(REPO, 'engine/tools'))

ID = 'vera'
RU = 'Вера'
SOURCE = 'to3d/r31-s10-vera'
BASE_BODY = 'moood-woman'
K = 1.60 / 1114          # metres per drawing unit — the same as Савелий Петрович's (Р2), so they stand side by side
FLOOR = 1230.0           # the drawing's floor (figures.vera_figure)
DROP = 20.0              # the head sits this much lower on the figure (figures.Figure.head_drop)
FACE_K = 1.04            # cast.vera's squash of the face below the eyes
EYE = (27.0, 3.0)        # the drawing's eye on the face (x, y), before the drop
PANEL = '#d7dbe3'
MOUTH_Y = 20 + (57 - 20) * FACE_K + DROP      # the mouth line in the figure's frame
EXPR_OWN = {}            # the character's own versions of the sheet's expressions (none)


def head():
    import cast
    return cast.vera()


def colours():
    import figures
    h, col = head()
    return dict(col, **figures.VERA_COL)
MOUTH_SX = 0.62          # the base's mouth drawn in to the drawing's narrow mouth (fit_head.py)
MOUTH_FROM = 'calm'      # the expression whose mouth line is the moving mouth's rest (assemble.py)
NOSE_SNAP = 0.85         # how far the nose's vertices are set onto the drawing's steep-sided nose (fit_head.py)
FACE_REST = {'up': 7}    # the live face's rest: her lids a little lowered (the drawing's lid 0.7)
