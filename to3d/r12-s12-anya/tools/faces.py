"""The face's painted layer, one picture per expression, drawn with the drawing's own parts (styles/s3-graphic/tools:
face.py's eye, brow, closed eye, shout) in the front view, in the drawing's units; the 3D head takes it by front
projection (build.py: uv from x, y). Transparent where nothing is painted.
python3 faces.py outdir   (then render.js turns the SVGs into PNGs)"""
import os, sys
import drawing as D  # noqa: F401  (puts the drawing's tools on the path)
import anya
from anya import C
from face import eye, brow, closed_eye, shout
from lib import F, L, LW

# the picture's box in drawing units, and its size
X0, X1, Y0, Y1 = -120.0, 120.0, -130.0, 130.0
PX = 4.0


def face_front(expr):
    out = []
    for x in (-46, 46):
        out.append(f'<ellipse cx="{x}" cy="44" rx="20" ry="12" fill="{C["blush"]}" opacity=".45"/>')
    look = {'dream': (0, -3), 'joy': (0, 0), 'surprise': (0, 0), 'sad': (0, 4), 'anger': (0, 2)}[expr]
    lid = {'dream': .26, 'joy': .1, 'surprise': 0, 'sad': .34, 'anger': .3}[expr]
    lt = {'sad': -5, 'anger': 6}.get(expr, 0)
    if expr == 'joy':
        out.append(closed_eye(-36, 6, 21, C, up=True, w=2.2))
        out.append(closed_eye(36, 6, 21, C, up=True, w=2.2))
    else:
        rs = 1.12 if expr == 'surprise' else 1.0
        ir = 13 if expr == 'surprise' else 16
        # the far (image-left) eye mirrored: the lid's tilt goes the other way
        out.append(eye(-36, 0, 22 * rs, 26 * rs, C, look=look, lid=lid, lidtilt=-lt, ir=ir, flick=-1))
        out.append(eye(36, 0, 22 * rs, 26 * rs, C, look=look, lid=lid, lidtilt=lt, ir=ir, flick=1))
    # brows: inner end (x, y), outer end (x, y), bend — the right one mirrored
    b = {'dream': (-12, -38, -56, -36, 5), 'joy': (-12, -44, -56, -42, 8), 'surprise': (-12, -54, -56, -52, 10),
         'sad': (-12, -46, -56, -32, 2), 'anger': (-12, -26, -56, -44, -2)}[expr]
    x0, y0, x1, y1, bend = b
    out.append(brow(x0, y0, x1, y1, bend, 6 if expr != 'anger' else 7, C['hairL']))
    out.append(brow(-x0, y0, -x1, y1, bend, 6 if expr != 'anger' else 7, C['hairL']))
    # nose: the shadow wedge and the line under it
    out.append(F('M -2 22 C 4 34, 10 40, 8 46 C 4 50, -4 50, -8 47 C -4 44, 0 40, -2 22 Z', C['shade']))
    out.append(L('M -9 46 C -4 50, 4 50, 9 46', C['line'], LW[0] * .9))
    m = {
        'dream': L('M -20 70 C -8 78, 8 78, 20 70', C['line'], LW[0] * 1.1) +
                 F('M -8 82 C -2 86, 4 86, 8 82 C 2 84, -2 84, -8 82 Z', C['lip'], C['lip'], LW[0] * .8),
        'joy': None,
        'surprise': F('M -7 76 C 0 72, 8 74, 9 84 C 9 96, 0 100, -6 96 C -11 92, -12 80, -7 76 Z', '#7a2a24', C['line']),
        'sad': L('M -16 82 C -6 74, 6 74, 16 82', C['line'], LW[0] * 1.1) + L('M -8 90 C -2 92, 4 92, 8 90', C['lip'], LW[0]),
        'anger': shout(-24, 24, 70, 26, C['line']),
    }
    if expr == 'joy':
        from lib import clip
        d = 'M -24 66 C -10 70, 10 70, 24 66 C 22 86, 10 98, 0 98 C -10 98, -22 86, -24 66 Z'
        m['joy'] = F(d, '#7a2a24', C['line']) + clip(d, F('M -28 60 L 28 58 L 26 74 C 10 80, -10 80, -28 74 Z', '#fff'),
                                                     '<ellipse cx="0" cy="98" rx="16" ry="9" fill="#e07a70"/>')
    out.append(m[expr])
    for x, y in ((-50, 28), (-40, 34), (-58, 36), (-32, 26), (50, 28), (40, 34), (58, 36), (32, 26), (-46, 42), (46, 42)):
        out.append(f'<circle cx="{x}" cy="{y}" r="1.9" fill="#c7745a" opacity=".7"/>')
    return ''.join(out)


def svg(expr):
    w, h = (X1 - X0) * PX, (Y1 - Y0) * PX
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}">'
            f'<g transform="scale({PX}) translate({-X0} {-Y0})">{face_front(expr)}</g></svg>\n')


EXPRS = ['dream', 'joy', 'surprise', 'sad', 'anger']

if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for e in EXPRS:
        open(os.path.join(out, f'face-{e}.svg'), 'w').write(svg(e))
