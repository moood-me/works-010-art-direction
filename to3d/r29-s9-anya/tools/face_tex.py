"""The face pictures: Аня's painted features in the front view, drawn by the drawing's own code (anya.py, face.py,
kit.py of styles/s9-midcentury) for each expression of the sheet, on a transparent square that the head takes by a
front projection (the drawing's head units −128…128 both ways; y down). Also the dry-brush strokes of the hair."""
import subprocess, os
import common
from common import CACHE, HERE
from kit import blush, brush, dryb, FILTERS
from face import eye, brow, mouth
import anya

R = 128
PX = 1024


def features(expr='calm'):
    e = anya._e(expr)
    bi, bo = e['brow']; cheek = e.get('cheek', 1.0)
    o = [blush(-38, 38, 14 * cheek, anya.CHEEK), blush(38, 38, 14 * cheek, anya.CHEEK),
         eye(-26, 10, 1.15, e['eye'], side=-1, lid=e.get('lid', 0)), eye(26, 10, 1.15, e['eye'], side=1, lid=e.get('lid', 0)),
         brow(-27, -15, 1.0, side=-1, inner=bi, outer=bo), brow(27, -15, 1.0, side=1, inner=bi, outer=bo),
         brush([(4, 22), (8, 38), (1, 42)], 2.4, '#b9775e', taper=(0.4, 0.2)),
         mouth(0, 63, 1.0 * e.get('ms', 1), e['mouth'], side=1, width=0.9),
         dryb([[(-56, -50), (-20, -100), (30, -112)], [(-10, -62), (30, -100), (64, -86)]], 3, anya.HAIR_L, 0.55)]
    return o


def svg(expr):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-R} {-R} {2 * R} {2 * R}" width="{PX}" height="{PX}">'
            f'<defs>{FILTERS}</defs>' + ''.join(features(expr)) + '</svg>')


EXPRS = ['calm', 'joy', 'surprise', 'sad', 'anger']

if __name__ == '__main__':
    out = f'{CACHE}/face'; os.makedirs(out, exist_ok=True)
    for e in EXPRS: open(f'{out}/{e}.svg', 'w').write(svg(e))
    subprocess.run(['node', f'{HERE}/svg2png.mjs', out, str(PX)] + EXPRS, check=True)
