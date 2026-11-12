"""The face signs of the character, taken from the drawing's own code (styles/s5-indie/tools), drawn head-on, without
the head shape and hair, on a transparent ground: one picture per expression of the expression sheet — the measure
for the live face (web/face.js), see face_check.mjs. Run from anywhere: python3 face_tex.py"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.basename(os.path.dirname(HERE))
STY = os.path.join(HERE, '../../../styles/s5-indie/tools')
sys.path.insert(0, STY)
import geo  # noqa: E402
import cast  # noqa: E402

# the picture covers this square of the head's own coordinates (drawing units, y down, head centre at 0,0),
# the same as `rect` in web/tim.js
X0, Y0, W, H = -76, -70, 152, 136
PX = 8          # pixels per drawing unit
OUT = os.path.join('/home/user/cache/to3d-' + FOLDER, 'tex')
EXPRS = ['neutral', 'joy', 'surprise', 'sad', 'anger']


def face_svg(ex):
    geo.SW = 2.4
    parts = cast.tim(0, ex)
    fp = [s for layer, s in parts if layer == 21]
    assert len(fp) == 1
    # the drawing puts the head at translate(0,-205) rotate(tilt); here the face is kept in the head's own frame
    s = re.sub(r'<g transform="translate\(0,-205\) rotate\(-?[\d.]+\)">', '<g>', fp[0], count=1)
    return geo.svg(s, (X0, Y0, W, H), W * PX, H * PX)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    args = []
    for ex in EXPRS:
        p = os.path.join(OUT, f'face-{ex}.svg')
        open(p, 'w').write(face_svg(ex))
        args += [p, os.path.join(OUT, f'face-{ex}.png')]
    subprocess.run(['node', os.path.join(HERE, 'svg2png.mjs')] + args, check=True)
