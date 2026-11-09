"""The face pictures: Марат's painted features in the front view, drawn by the drawing's own code (marat.py, face.py,
kit.py of styles/s9-midcentury) for each expression of the sheet, on a transparent square that the head, the nose, the
beard and the curls take by a front projection (the drawing's head units −160…160 both ways; y down): blush, eyes,
laugh lines, block brows, the nostrils, the mouth in the beard with the moustache over it, the dry-brush strokes."""
import subprocess, os
import common
from common import CACHE, HERE
from kit import blush, brush, shape, dryb, mix, INK, FILTERS
from face import eye
import marat as M

R = 160
PX = 1024


def features(expr='calm'):
    e = M._e(expr)
    bi, bo = e['brow']; cheek = e.get('cheek', 1.0)
    laugh = e['mouth'] in ('laugh', 'beam')
    ey = 2 if e['eye'] != 'happy' else 4
    o = [blush(-46, 30, 17 * cheek, M.CHEEK, 0.62), blush(46, 30, 17 * cheek, M.CHEEK, 0.62),
         dryb([[(-70, 50), (-58, 90), (-30, 112)], [(70, 50), (58, 90), (30, 112)], [(-10, 100), (0, 118), (12, 100)]], 2.4, M.HAIR_L, 0.7),
         eye(-30, ey, 1.4, e['eye'], side=-1, lash=False), eye(30, ey, 1.4, e['eye'], side=1, lash=False)]
    if laugh:
        for t in (-1, 1):
            o.append(brush([(t * 48, 6), (t * 56, 2), (t * 60, -5)], 1.8, M.SKIN_D, taper=(0.2, 0.5)))
            o.append(brush([(t * 44, 16), (t * 30, 20), (t * 16, 15)], 1.8, M.SKIN_D, taper=(0.4, 0.4)))
    o += [M._brow(-31, -20, -1, bi, bo), M._brow(31, -20, 1, bi, bo),
          brush([(-12, 42), (-5, 37), (0, 41)], 2.2, mix(M.NOSE, INK, 0.5), taper=(0.3, 0.3)),
          brush([(12, 42), (5, 37), (0, 41)], 2.2, mix(M.NOSE, INK, 0.5), taper=(0.3, 0.3)),
          M._mouth(0, 76, e, 1.1),
          shape([(0, 48), (22, 44), (48, 54), (62, 70, 'c'), (38, 64), (14, 62), (0, 59), (-14, 62), (-38, 64), (-62, 70, 'c'),
                 (-48, 54), (-22, 44)], M.HAIR),
          dryb([[(-12, 52), (-40, 62)], [(12, 52), (40, 62)]], 2.0, M.HAIR_L, 0.7),
          dryb([[(-66, -84), (-48, -104), (-26, -112)], [(-10, -114), (10, -120), (28, -112)], [(46, -106), (64, -92), (74, -74)]], 2.6, M.HAIR_L, 0.7)]
    return o


def svg(expr):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-R} {-R} {2 * R} {2 * R}" width="{PX}" height="{PX}">'
            f'<defs>{FILTERS}</defs>' + ''.join(features(expr)) + '</svg>')


EXPRS = ['calm', 'joy', 'surprise', 'sad', 'anger']

if __name__ == '__main__':
    out = f'{CACHE}/face'; os.makedirs(out, exist_ok=True)
    for e in EXPRS: open(f'{out}/{e}.svg', 'w').write(svg(e))
    subprocess.run(['node', f'{HERE}/svg2png.mjs', out, str(PX)] + EXPRS, check=True)
