"""Side by side and overlay of the drawing and the 3D render in the drawing's own frames.
  python3 compare.py turn RENDERDIR OUT     (t0/t1/t2.png: one view per third of the turnaround sheet)
  python3 compare.py one DRAWING.jpg RENDER.png OUT"""
import sys, os
import numpy as np
from PIL import Image
S17 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../styles/s17-bilibin/pics')


def turn(rdir):
    ims = [np.asarray(Image.open(os.path.join(rdir, 't%d.png' % i)).convert('RGB')) for i in range(3)]
    out = ims[0].copy()
    w = out.shape[1]
    a, b = int(w * 0.343), int(w * 0.657)
    out[:, a:b] = ims[1][:, a:b]; out[:, b:] = ims[2][:, b:]
    return Image.fromarray(out)


def pair(dr, rn, out):
    dr = dr.convert('RGB'); rn = rn.convert('RGB').resize(dr.size)
    w, h = dr.size
    vertical = w > h
    sbs = Image.new('RGB', (w, 2 * h) if vertical else (2 * w, h))
    sbs.paste(dr, (0, 0)); sbs.paste(rn, (0, h) if vertical else (w, 0))
    ov = Image.blend(dr, rn, 0.5)
    sbs.save(out + '-side.webp', quality=86); ov.save(out + '-over.webp', quality=86)


if __name__ == '__main__':
    if sys.argv[1] == 'turn':
        r = turn(sys.argv[2]); r.save(os.path.join(sys.argv[2], 'turn.png'))
        pair(Image.open(os.path.join(S17, 'turn-vera.jpg')), r, sys.argv[3])
    else:
        pair(Image.open(sys.argv[2]), Image.open(sys.argv[3]), sys.argv[4])
