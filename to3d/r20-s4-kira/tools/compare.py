"""Side by side and overlay of the drawing and the 3D render in the drawing's own frames.
  python3 compare.py turn RENDERDIR OUT     (t0/t1/t2.png: 1500×640 each, one view per third)
  python3 compare.py one DRAWING.jpg RENDER.png OUT"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drawing as DR  # noqa: E402
from PIL import Image, ImageDraw, ImageFont
S4 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../styles/s4-arcane/pics')


def turn(rdir):
    ims = [np.asarray(Image.open(os.path.join(rdir, 't%d.png' % i)).convert('RGB')) for i in range(3)]
    out = ims[0].copy()
    out[:, 505:995] = ims[1][:, 505:995]; out[:, 995:] = ims[2][:, 995:]
    return Image.fromarray(out)


def pair(dr, rn, out, label=('рисунок', '3D')):
    dr = dr.convert('RGB'); rn = rn.convert('RGB').resize(dr.size)
    w, h = dr.size
    vertical = w > h
    sbs = Image.new('RGB', (w, 2 * h) if vertical else (2 * w, h))
    sbs.paste(dr, (0, 0)); sbs.paste(rn, (0, h) if vertical else (w, 0))
    ov = Image.blend(dr, rn, 0.5)
    sbs.save(out + '-side.jpg', quality=88); ov.save(out + '-over.jpg', quality=88)


if __name__ == '__main__':
    if sys.argv[1] == 'turn':
        r = turn(sys.argv[2]); r.save(os.path.join(sys.argv[2], 'turn.png'))
        pair(Image.open(os.path.join(S4, 'turn-%s.jpg' % DR.WHO)), r, sys.argv[3])
    else:
        pair(Image.open(sys.argv[2]), Image.open(sys.argv[3]), sys.argv[4])
