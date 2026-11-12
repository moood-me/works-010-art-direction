"""The drawing beside the 3D in the drawing's own views and scale, and over it.
python3 compare.py [pack.json] — writes into the cache's cmp/: turn-side.png (the turn sheet's three views over the
same three of the 3D), turn-over.png (the two blended), figure-side.png (the figure drawing | the 3D standing in
three-quarter), and the renders."""
import sys, os, json, subprocess
import numpy as np
from PIL import Image
import drawing as D

HERE = os.path.dirname(os.path.abspath(__file__))
S15 = os.path.join(HERE, '..', '..', '..', 'styles', 's15-noir', 'pics')
CACHE = '/home/user/cache/to3d-r15-s15-anya'
pk = sys.argv[1] if len(sys.argv) > 1 else '/cache/to3d-r15-s15-anya/out/anya.json'
out = os.path.join(CACHE, 'cmp'); os.makedirs(out, exist_ok=True)
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
C1 = '#3b3350'

# the turn sheet (styles/s15-noir/tools/build.py turn): 1800×800, a panel per view, the head's origin at (310 + 590 i,
# 370), 2 px a head unit
PXM = 2.0 / (D.HS * D.K)                                   # pixels per metre
PW, Y0, Y1 = 440, 70, 800
y_org = (D.FLOOR - (0 - D.EYE) * D.HS) * D.K               # the head origin's height
cy = y_org - ((Y0 + Y1) / 2 - 370) / PXM
h = (Y1 - Y0) / PXM
dx = 10 / PXM                                              # the panel's middle is 10 px right of the origin
zs = D.ZC * D.HS * D.K                                     # the profile's origin stands this far in front of the neck's axis
ST = dict(pose='stand', poseOpts={'out': 0.08}, still=True, exprTrack=[[0, 'calm']], time=2.0, back=None, bg=C1, floor=False)
views = [('front', 0.0, [dx, cy, 0]), ('three', 0.6, [dx * np.cos(0.6), cy, -dx * np.sin(0.6)]), ('side', 1.5708, [0, cy, zs - dx])]
shots = [dict(name='turn-' + n, set=dict(ST, cam=dict(mode='ortho', h=h, yaw=y, pitch=0, target=t, follow=False))) for n, y, t in views]
# the figure (build.py fig): 700×1000, 1.16 px a figure unit, the soles at y 930, x 360; the window behind
FPX = 1.16 / (D.FS * D.K)
fh = 1000 / FPX; fcy = (930 - 500) / FPX; fdx = -10 / FPX
shots.append(dict(name='figure', w=700, h=1000, set=dict(pose='stand', poseOpts={'out': 0.05}, still=True, exprTrack=[[0, 'calm']], time=2.0, bg='#11121b', floor=True,
             back=dict(kind='window', w=330 / FPX, h=830 / FPX, y=fcy + (500 - 455) / FPX - 0.06, x=15 / FPX),
             cam=dict(mode='persp', fov=14, dist=fh / 2 / np.tan(np.radians(7)), yaw=0.6, pitch=0.035, target=[fdx * np.cos(0.6), fcy + 0.035 * 0, -fdx * np.sin(0.6)], follow=False))))
json.dump(dict(pack=pk, w=PW, h=Y1 - Y0, shots=shots), open(os.path.join(out, 'jobs.json'), 'w'))
subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), os.path.join(out, 'jobs.json'), out], check=True, env=ENV)

T = Image.open(os.path.join(S15, 'turn-anya.png')).convert('RGB')
W, H = PW, Y1 - Y0
side = Image.new('RGB', (W * 3 + 20, H * 2 + 10), '#11121b'); over = Image.new('RGB', (W * 3 + 20, H), '#11121b')
for i, (n, _, _) in enumerate(views):
    cx = 310 + i * 590 + 10
    d = T.crop((cx - PW // 2, Y0, cx + PW // 2, Y1))
    r = Image.open(os.path.join(out, f'turn-{n}.png')).convert('RGB')
    side.paste(d, (i * (W + 10), 0)); side.paste(r, (i * (W + 10), H + 10))
    over.paste(Image.blend(r, d, 0.5), (i * (W + 10), 0))
side.save(os.path.join(out, 'turn-side.png')); over.save(os.path.join(out, 'turn-over.png'))
F = Image.open(os.path.join(S15, 'figure-anya.png')).convert('RGB'); R = Image.open(os.path.join(out, 'figure.png')).convert('RGB')
fs = Image.new('RGB', (1410, 1000), '#11121b'); fs.paste(F, (0, 0)); fs.paste(R, (710, 0)); fs.save(os.path.join(out, 'figure-side.png'))
Image.blend(R, F, 0.5).save(os.path.join(out, 'figure-over.png'))
