"""The drawing's own silhouettes (black on white, no rim, no signs) in the drawing's layouts, from the style's code:
turn (1500×760, yaw 0/45/90/135/180), full (640×860) and, where the style has one, the expression sheet (1500×720).
python3 drawing.py OUTDIR"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'styles', 's6-symbolic', 'tools'))
sys.path.insert(0, HERE)
from draw import figure_svg, svg_doc  # noqa: E402
import character as C                 # noqa: E402

out = sys.argv[1]
os.makedirs(out, exist_ok=True)


def sil(name, items, W, H):
    body = ''.join(figure_svg(C.ID, yaw=yw, k=k, x=x, y=y, ink='#000', rim=None, accents=False, pose=pose, opts=opts)[0]
                   for yw, k, x, y, pose, opts in items)
    open(os.path.join(out, name + '.svg'), 'w').write(svg_doc(W, H, body, bg='#ffffff'))


sil('turn', [(yw, C.TURN['k'], 1500 * (i + .5) / 5, 760 * .86, None, None) for i, yw in enumerate([0, 45, 90, 135, 180])], 1500, 760)
sil('full', [(C.FULL['yaw'], C.FULL['k'], 640 * C.FULL['x'], 860 * .9, None, None)], 640, 860)
if getattr(C, 'EXPR', None):
    E = C.EXPR
    n = len(E['order'])
    sil('expr', [(C.MOODS[m]['yaw'], E['k'], 1500 * (i + .5) / n + E['xs'][i], 720 * .84, C.MOODS[m]['pose'], C.MOODS[m].get('opts'))
                 for i, m in enumerate(E['order'])], 1500, 720)
