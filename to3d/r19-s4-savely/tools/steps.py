"""The steps along the way, as clay (software raster, mesh.raster): what each base gave.
  1 the HBM head as it comes; 2 fitted to the drawing (eyes carried, nose lengthened, the drawing's surface as dots);
  3 Anny's body as it comes; 4 Anny made the character, dressed, with the fitted head.
usage: python3 steps.py CACHE OUT.jpg"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mesh as M, pack, drawing as DR  # noqa: E402

C, OUT = sys.argv[1], sys.argv[2]
d = np.load(os.path.join(C, 'hbm_head.npz')); hf = np.load(os.path.join(C, 'head_fit.npz'))


def tri(f):
    return np.array([[q[0], q[k], q[k + 1]] for q in f for k in range(1, len([x for x in q if x >= 0]) - 1)])


def shot(V, T, yaw, box, size=360, col=None):
    im, _ = M.raster(V, T, yaw=yaw, size=size, box=box, col=col, light=(-0.5, 0.55, 0.67))
    return Image.fromarray(im)


panels = []
# 1: the base head (Blender z-up → y-up; facing −y → +z)
V = d['head_v'][:, [0, 2, 1]] * [1, 1, -1]; V = V - [V[:, 0].mean(), 0, 0]
T = tri(d['head_f'])
bx = (-0.13, 0.13, 0.55, 0.92)
panels += [shot(V, T, 0, bx), shot(V, T, -1.2, bx)]
# 2: fitted, drawing units → y up
V2 = hf['v'] * [1, -1, 1]; T2 = hf['tris']
b2 = (-135, 135, -170, 150)
panels += [shot(V2, T2, 0, b2), shot(V2, T2, -1.2, b2)]
# 3: Anny as it comes; 4: the pack
h, a, th, t = pack.body(DR.BODY)
P0 = a['positions'].reshape(-1, 3); T0 = t['triangles'].reshape(-1, 3)
b3 = (-0.62, 0.62, -0.02, 1.84)
panels += [shot(P0, T0, -0.3, b3)]
hd, ar = pack.load(os.path.join(C, 'out', DR.WHO + '.json'))
P1 = ar['positions'].reshape(-1, 3); T1 = ar['triangles'].reshape(-1, 3).astype(np.int64)
col = ar['col'].astype(float) / 255
panels += [shot(P1, T1, -0.3, b3, col=col)]
names = ['1. голова HBM как есть', '', '2. подогнана к рисунку', '', '3. тело Anny как есть', '4. собранный персонаж (цвета без света)']
W = sum(p.width for p in panels); H = max(p.height for p in panels) + 30
im = Image.new('RGB', (W, H), 'white'); dr = ImageDraw.Draw(im)
try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
except Exception:
    f = None
x = 0
for p, n in zip(panels, names):
    im.paste(p, (x, 30)); dr.text((x + 8, 7), n, fill='black', font=f); x += p.width
im.save(OUT, quality=85)
