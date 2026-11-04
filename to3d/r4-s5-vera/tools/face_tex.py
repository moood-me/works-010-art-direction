"""The face signs of Вера, taken from the drawing's own code (styles/s5-indie/tools/cast.py), drawn head-on, without
the head shape, hair and glasses, on a transparent ground: one texture per expression of the expression sheet.
The 3D head carries it by a straight projection from the front. Run from anywhere: python3 face_tex.py"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STY = os.path.join(HERE, '../../../styles/s5-indie/tools')
sys.path.insert(0, STY)
import geo  # noqa: E402
import cast  # noqa: E402

# the texture covers this square of the head's own coordinates (drawing units, y down, head centre at 0,0)
X0, Y0, W, H = -76, -84, 152, 160
PX = 8          # pixels per drawing unit
OUT = os.path.join(HERE, 'tex')
EXPRS = ['neutral', 'joy', 'surprise', 'sad', 'anger']


def face_svg(ex):
    geo.SW = 2.4
    parts = cast.vera(0, ex)
    fp = [s for layer, s in parts if layer == 21]
    assert len(fp) == 1
    # the drawing puts the head at translate(0,-352) rotate(tilt); here the face is kept in the head's own frame
    s = re.sub(r'<g transform="translate\(0,-352\) rotate\(-?[\d.]+\)">', '<g>', fp[0], count=1)
    return geo.svg(s, (X0, Y0, W, H), W * PX, H * PX)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    args = []
    for ex in EXPRS:
        p = os.path.join('/home/user/cache/to3d-r4-s5-vera', f'face-{ex}.svg')
        open(p, 'w').write(face_svg(ex))
        args += [p, os.path.join(OUT, f'face-{ex}.png')]
    subprocess.run(['node', os.path.join(HERE, 'svg2png.mjs')] + args, check=True)
