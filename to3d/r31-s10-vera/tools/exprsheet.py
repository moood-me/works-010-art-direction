"""The five expressions of the live face as stills: the stand pose with the head a little turned, the face set by
web/face.mjs (stand.mjs FACE=…), rendered with the baked marks — what the moving pictures and the viewer show.
usage: python3 exprsheet.py CACHE  → CACHE/expr/sheet.png"""
import sys, os, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import who
C = os.path.abspath(sys.argv[1])
EX = [('calm', 'спокойна'), ('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('anger', 'злость')]
EX = getattr(who, 'EXPR_SHEET', EX)
fr = []
for e, _ in EX:
    env = dict(os.environ, FACE=json.dumps({e: 1}), HEAD=json.dumps(getattr(who, 'EXPR_HEAD', dict(pitch=0, yaw=0))))
    subprocess.run(['node', HERE + '/stand.mjs', C, C + '/ex.bin'], check=True, env=env, stdout=subprocess.DEVNULL)
    fr.append(np.fromfile(C + '/ex.bin', np.float32))
np.concatenate(fr).tofile(C + '/expr.bin')
j = json.load(open(C + '/ex.json'))
n = len(EX)
json.dump(dict(j, frames=n, times=list(range(n)), hips=j['hips'] * n, head=j['head'] * n), open(C + '/expr.json', 'w'))
s = getattr(who, 'EXPR_S', 1.9)
v = [dict(name=f'e{i}', yaw=-18, s=s, cx=200, cy=40 + 118 * s, W=400, H=440, lw=2.6, bg=who.PANEL) for i in range(n)]
json.dump(dict(scene=C + '/scene.npz', offsets=C + '/engine/offsets.json', frames=C + '/expr.bin', out=C + '/expr',
               samples=16, pair=True, views=v), open(C + '/job_expr.json', 'w'))
subprocess.run([HERE + '/heavy.sh', 'blender', '-b', '-P', HERE + '/render.py', '--', C + '/job_expr.json'],
               check=True, stdout=subprocess.DEVNULL)
sheet = Image.new('RGB', (n * 400, 480), '#f4ecd8')
d = ImageDraw.Draw(sheet)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
for i, (e, ru) in enumerate(EX):
    im = Image.open(f'{C}/expr/e{i}_{i:04d}.png').convert('RGB')
    ImageDraw.Draw(im).rectangle([0, 0, 399, 439], outline='#1b1714', width=3)
    sheet.paste(im, (i * 400, 0))
    d.text((i * 400 + 200, 460), ru, fill='#1b1714', font=font, anchor='mm')
sheet.save(C + '/expr/sheet.png')
