"""The drawing's own silhouettes (black on white, no rim, no signs) in the drawing's layouts, from the style's code:
turn (1500×760, yaw 0/45/90/135/180, k 3.2) and full (640×860, yaw 70, k 3.55). python3 drawing.py OUTDIR"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'styles', 's6-symbolic', 'tools'))
from draw import figure_svg, svg_doc  # noqa: E402

out = sys.argv[1]
os.makedirs(out, exist_ok=True)


def sil(name, items, W, H):
    body = ''.join(figure_svg('savely', yaw=yw, k=k, x=x, y=y, ink='#000', rim=None, accents=False)[0] for yw, k, x, y in items)
    open(os.path.join(out, name + '.svg'), 'w').write(svg_doc(W, H, body, bg='#ffffff'))


sil('turn', [(yw, 3.2, 1500 * (i + .5) / 5, 760 * .86) for i, yw in enumerate([0, 45, 90, 135, 180])], 1500, 760)
sil('full', [(70, 3.55, 320, 860 * .9)], 640, 860)
