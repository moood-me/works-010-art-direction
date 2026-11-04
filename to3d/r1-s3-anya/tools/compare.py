"""The drawing's turnaround beside the 3D in the same three views, and over it.
python3 compare.py pack.json outdir [expr] — writes side.png (drawing | 3D per view), over.png (3D with the drawing laid
over at half strength), and the three renders."""
import sys, os, json, subprocess
import numpy as np
from PIL import Image, ImageChops
import drawing as D

HERE = os.path.dirname(os.path.abspath(__file__))
S3 = os.path.join(HERE, '..', '..', '..', 'styles', 's3-graphic')
pk, out = sys.argv[1], sys.argv[2]
expr = sys.argv[3] if len(sys.argv) > 3 else 'dream'
os.makedirs(out, exist_ok=True)
SC = 2                                   # pixels of the turnaround picture per its own pixel
s = 760 / (1386 + 142)                   # the turnaround's scale (styles/s3-graphic/tools/build.py)
ref = os.path.join(out, 'turnaround-anya.png')
if not os.path.exists(ref):
    subprocess.run(['node', os.path.join(S3, 'tools', 'render.js'), out, str(SC), os.path.join(S3, 'svg', 'turnaround-anya.svg')],
                   check=True, env=dict(os.environ, NODE_PATH='/opt/node-tools/node_modules'))
T = Image.open(ref).convert('RGB')
PW, Y0, Y1 = 470, 100, 930              # a panel: centre ±235 px, rows Y0…Y1 (turnaround pixels)
yd0, yd1 = (Y0 - 900) / s + 1386, (Y1 - 900) / s + 1386
h = (yd1 - yd0) * D.K; cy = (D.FLOOR - (yd0 + yd1) / 2) * D.K
W, H = PW * SC, (Y1 - Y0) * SC
views = [('front', 0.0), ('three', -0.785), ('side', -1.5708)]
pose = json.loads(os.environ.get('POSE', '{}'))
shots = [dict(name=n, set=dict(pose='stand', poseOpts=pose, expr=expr, cam=dict(mode='ortho', h=h, cy=cy, cx=0, yaw=y, pitch=0, target=[0, cy, 0]))) for n, y in views]
json.dump(dict(pack=pk, w=W, h=H, shots=shots), open(os.path.join(out, 'jobs.json'), 'w'))
subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), os.path.join(out, 'jobs.json'), out], check=True,
               env=dict(os.environ, NODE_PATH='/opt/node-tools/node_modules'))
side = Image.new('RGB', (W * 3, H * 2), '#f1e6d6'); over = Image.new('RGB', (W * 3, H), '#f1e6d6')
for i, (n, _) in enumerate(views):
    cx = 260 + i * 490
    d = T.crop(((cx - PW // 2) * SC, Y0 * SC, (cx + PW // 2) * SC, Y1 * SC))
    r = Image.open(os.path.join(out, n + '.png')).convert('RGB')
    side.paste(d, (i * W, 0)); side.paste(r, (i * W, H))
    over.paste(Image.blend(r, d, 0.45), (i * W, 0))
side.save(os.path.join(out, 'side.png')); over.save(os.path.join(out, 'over.png'))
