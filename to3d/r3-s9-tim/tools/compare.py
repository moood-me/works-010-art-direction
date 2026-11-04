"""The drawing and the 3D side by side and overlaid, in the drawing's own framings:
turn  — turn-tim (front, three-quarter, profile busts; head unit 1.25 px, head centres at x 250/750/1250, y 260)
figure — figure-tim (whole figure; feet at y 820, head unit 0.907 px)
expr  — expr-tim (three-quarter heads, four expressions; head centres at x 200+400i, y 240, head unit 1.25 px)
python3 compare.py turn|figure|expr [pose json]"""
import sys, json, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from common import CACHE, HERE, STYLE
from drawing import K
from compose import compose

PICS = os.path.join(os.path.dirname(HERE), 'pics')
YAW34 = float(os.environ.get('YAW34', '-0.5'))
pose = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
OFF_HEAD = np.array([0, 58 * K, -4 * K])          # the drawing's head centre from the Head joint


def shoot(job, out):
    json.dump(job, open(f'{CACHE}/job_cmp.json', 'w'))
    subprocess.run(['node', f'{HERE}/shots.mjs', f'{CACHE}/job_cmp.json', out], check=True, capture_output=True)


def head_cam(yaw, ppm, cy, h):
    """an orthographic camera putting the drawing's head centre at pixel row cy of an image h tall"""
    off = OFF_HEAD + [0, -(h / 2 - cy) / ppm, 0]
    return {'yaw': yaw, 'joint': 'Head', 'offset': off.tolist(), 'height': h / ppm}


def label(im, text, xy):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 22)
    d.text(xy, text, fill=(42, 32, 28), font=f)


def sheet(drawing, render, w, h, name, captions):
    A = Image.open(drawing).convert('RGB').resize((w, h)); B = Image.open(render).convert('RGB')
    ov = Image.blend(A, B, 0.5)
    S = Image.new('RGB', (w, h * 3 + 3 * 40), (243, 234, 214))
    for i, (im, cap) in enumerate(zip((A, B, ov), captions)):
        S.paste(im, (0, i * (h + 40) + 40)); label(S, cap, (12, i * (h + 40) + 8))
    S.save(f'{PICS}/{name}.webp', quality=88, method=6)
    return S


kind = sys.argv[1]
base = {'model': '/cache/to3d-r3-s9-tim/tim.json', 'face': '/cache/to3d-r3-s9-tim/face/calm.png', **pose}
if kind == 'turn':
    ppm = 1.25 / K
    shots = [{'name': n, 'set': {**base, 'cam': head_cam(y, ppm, 260, 600)}} for n, y in (('front', 0), ('q34', YAW34), ('side', -np.pi / 2))]
    shoot({'w': 500, 'h': 600, 'shots': shots}, f'{CACHE}/cmp')
    compose(f'{CACHE}/cmp/turn.png', 1500, 600, 'wide', [(f'{CACHE}/cmp/{n}.png', 500 * i, 0) for i, n in enumerate(('front', 'q34', 'side'))])
    sheet(f'{STYLE}/pics/turn-tim.webp', f'{CACHE}/cmp/turn.png', 1500, 600, 'cmp-turn',
          ['рисунок (turn-tim): анфас, три четверти, профиль', '3D в тех же видах, через тот же фильтр гуаши', 'наложение: рисунок и 3D пополам'])
elif kind == 'expr':
    ppm = 1.25 / K
    names = ['joy', 'surprise', 'sad', 'anger']
    shots = [{'name': n, 'set': {**base, 'face': f'/cache/to3d-r3-s9-tim/face/{n}.png', 'cam': head_cam(YAW34, ppm, 240, 500)}} for n in names]
    shoot({'w': 400, 'h': 500, 'shots': shots}, f'{CACHE}/cmp')
    compose(f'{CACHE}/cmp/expr.png', 1600, 500, 'wide', [(f'{CACHE}/cmp/{n}.png', 400 * i, 0) for i, n in enumerate(names)])
    sheet(f'{STYLE}/pics/expr-tim.webp', f'{CACHE}/cmp/expr.png', 1600, 500, 'cmp-expr',
          ['рисунок (expr-tim): радость, удивление, грусть, злость', '3D: те же черты, нарисованные кодом рисунка, на голове', 'наложение'])
elif kind == 'figure':
    ppm = 0.907 / K
    cam = {'yaw': YAW34, 'follow': [0, (820 - 450) / ppm, 0], 'height': 900 / ppm}
    shoot({'w': 500, 'h': 900, 'shots': [{'name': 'fig', 'set': {**base, 'cam': cam}}]}, f'{CACHE}/cmp')
    compose(f'{CACHE}/cmp/figure.png', 500, 900, 'figure', [(f'{CACHE}/cmp/fig.png', 0, 0)])
    A = Image.open(f'{STYLE}/pics/figure-tim.webp').convert('RGB'); B = Image.open(f'{CACHE}/cmp/figure.png').convert('RGB')
    S = Image.new('RGB', (1500, 940), (243, 234, 214))
    for i, (im, cap) in enumerate(((A, 'рисунок'), (B, '3D'), (Image.blend(A, B, 0.5), 'наложение'))):
        S.paste(im, (i * 500, 40)); label(S, cap, (i * 500 + 12, 8))
    S.save(f'{PICS}/cmp-figure.webp', quality=88, method=6)
