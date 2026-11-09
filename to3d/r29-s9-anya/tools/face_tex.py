"""The face pictures: Тим's painted features in the front view, drawn by the drawing's own code (tim.py, face.py, kit.py
of styles/s9-midcentury) for each expression of the sheet, on a transparent square that the head takes by a front
projection (the drawing's head units −128…128 both ways; y down). Also the dry-brush strokes of the hair."""
import json, subprocess, os
import common
from common import CACHE, HERE
from kit import blush, FILTERS
from face import eye, brow, mouth
import tim

R = 128
PX = 1024


def features(expr='calm'):
    e = tim._e(expr)
    bi, bo = e['brow']; b2i, b2o = e.get('brow2', e['brow']); cheek = e.get('cheek', 1.0)
    o = [blush(-40, 40, 16 * cheek, tim.CHEEK), blush(40, 40, 16 * cheek, tim.CHEEK),
         tim._freckles([(-48, 30), (-38, 26), (-28, 32), (-42, 38), (48, 30), (38, 26), (28, 32), (42, 38)]),
         eye(-24, 14, 1.45, e['eye'], side=-1, lash=False), eye(24, 14, 1.45, e['eye'], side=1, lash=False),
         brow(-25, -10, 1.2, side=-1, inner=bi, outer=bo, w=3.2), brow(25, -12, 1.2, side=1, inner=b2i, outer=b2o, w=3.2),
         mouth(2, 58, 1.3 * e.get('ms', 1), e['mouth'], side=1, width=0.85)]
    # the hair's dry brush (front view of tim.head)
    from kit import dryb
    o.append(dryb([[(-56, -70), (-16, -106), (30, -110)], [(-10, -74), (30, -100), (64, -76)]], 2.6, tim.HAIR_D, 0.7))
    return o


def svg(expr):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-R} {-R} {2 * R} {2 * R}" width="{PX}" height="{PX}">'
            f'<defs>{FILTERS}</defs>' + ''.join(features(expr)) + '</svg>')


EXPRS = ['calm', 'joy', 'surprise', 'sad', 'anger']

if __name__ == '__main__':
    out = f'{CACHE}/face'; os.makedirs(out, exist_ok=True)
    for e in EXPRS: open(f'{out}/{e}.svg', 'w').write(svg(e))
    subprocess.run(['node', f'{HERE}/svg2png.mjs', out, str(PX)] + EXPRS, check=True)
