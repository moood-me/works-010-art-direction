"""The style's turnaround (styles/s3-graphic/svg/turnaround-kira.svg) beside the 3D in the same three views, and over it.
python3 compare.py pack.json outdir — writes side.png (drawing over 3D, per view) and over.png (the 3D with the drawing
laid over at half strength)."""
import sys, os, json, subprocess
from PIL import Image
import drawing as D

HERE = os.path.dirname(os.path.abspath(__file__))
pk, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
SC = 2                                   # pixels of the picture per the sheet's own pixel
S3 = os.path.join(HERE, '..', '..', '..', 'styles', 's3-graphic')
subprocess.run(['node', os.path.join(S3, 'tools', 'render.js'), out, str(SC), os.path.join(S3, 'svg', 'turnaround-kira.svg')],
               check=True, env=ENV, stdout=subprocess.DEVNULL)
T = Image.open(os.path.join(out, 'turnaround-kira.png')).convert('RGB')
s = 760 / (D.FLOOR - D.CROWN)            # the sheet's scale (styles/s3-graphic/tools/build.py: turnaround)
PW, Y0, Y1 = 470, 110, 930               # a panel: centre ±235 px, rows Y0…Y1 (sheet pixels)
yd0, yd1 = (Y0 - 900) / s + D.FLOOR, (Y1 - 900) / s + D.FLOOR
h = (yd1 - yd0) * D.K; cy = (D.FLOOR - (yd0 + yd1) / 2) * D.K
W, H = PW * SC, (Y1 - Y0) * SC
views = [('front', 0.0), ('three', -0.62), ('side', -1.5708)]
pose = json.loads(os.environ.get('POSE', '{"out": 0.03}'))
shots = [dict(name=n, set=dict(pose='stand', poseOpts=pose, still=True, time=2.0, cam=dict(mode='ortho', h=h, cy=cy, cx=0, yaw=y, pitch=0, target=[0, cy, 0]))) for n, y in views]
json.dump(dict(pack=pk, w=W, h=H, shots=shots), open(os.path.join(out, 'jobs.json'), 'w'))
subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), os.path.join(out, 'jobs.json'), out], check=True, env=ENV, stdout=subprocess.DEVNULL)
side = Image.new('RGB', (W * 3, H * 2), '#f1e6d6'); over = Image.new('RGB', (W * 3, H), '#f1e6d6')
for i, (n, _) in enumerate(views):
    cx = 260 + i * 490
    d = T.crop(((cx - PW // 2) * SC, Y0 * SC, (cx + PW // 2) * SC, Y1 * SC))
    r = Image.open(os.path.join(out, n + '.png')).convert('RGB')
    side.paste(d, (i * W, 0)); side.paste(r, (i * W, H))
    over.paste(Image.blend(r, d, 0.45), (i * W, 0))
side.save(os.path.join(out, 'side.png')); over.save(os.path.join(out, 'over.png'))
side.resize((side.width // 2, side.height // 2), Image.LANCZOS).save(os.path.join(out, 'side-small.png'))
over.resize((over.width // 2, over.height // 2), Image.LANCZOS).save(os.path.join(out, 'over-small.png'))
