"""The drawing's turnaround beside the 3D in the same three views (front, three-quarter, profile), and over it.
The 3D is rendered with the drawing's own camera: orthographic, yaw 0 / 35 / 90°, pitch 4°, 5.2 px per cm, the
figure's origin where the drawing put it — so a render pixel and a drawing pixel are the same place.
  python3 compare.py pack-url outdir [expr]   → side.png (drawing over 3D), over.png (3D, the drawing at half), a.png…"""
import sys, os, json, math, subprocess
from PIL import Image
import config

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
SC = 2


def cam(yaw_deg, yc_cm, h_cm, pitch=4.0):
    a, p = math.radians(yaw_deg), math.radians(pitch)
    uy = [math.sin(a) * math.sin(p), math.cos(p), -math.cos(a) * math.sin(p)]
    return dict(mode='ortho', h=h_cm / 100, yaw=-a, pitch=p, target=[yc_cm * u / 100 for u in uy])


VIEWS = [('front', 0, 270), ('three', 35, 750), ('side', 90, 1230)]
X_HALF, Y0, Y1, FLOOR, S = 230, 40, 980, 930, 5.2


def shots(pack, out, expr='calm', extra=None):
    W, H = 2 * X_HALF * SC, (Y1 - Y0) * SC
    yc = (FLOOR - (Y0 + Y1) / 2) / S
    sh = [dict(name=n, set=dict(dict(pose='stand', still=True, exprTrack=[[0, expr]], time=2.0, shadow=False,
                                     cam=cam(y, yc, (Y1 - Y0) / S)), **(extra or {}))) for n, y, _ in VIEWS]
    json.dump(dict(pack=pack, w=W, h=H, shots=sh), open(os.path.join(out, 'jobs.json'), 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), os.path.join(out, 'jobs.json'), out], check=True, env=ENV)


if __name__ == '__main__':
    pk, out = sys.argv[1], sys.argv[2]
    expr = sys.argv[3] if len(sys.argv) > 3 else 'calm'
    os.makedirs(out, exist_ok=True)
    ref = os.path.join(config.CACHE, 'refs', 'turn.png')        # refs.py
    shots(pk, out, expr)
    T = Image.open(ref).convert('RGB')
    W, H = 2 * X_HALF * SC, (Y1 - Y0) * SC
    side = Image.new('RGB', (W * 3, H * 2)); over = Image.new('RGB', (W * 3, H))
    for i, (n, _, cx) in enumerate(VIEWS):
        d = T.crop(((cx - X_HALF) * SC, Y0 * SC, (cx + X_HALF) * SC, Y1 * SC))
        r = Image.open(os.path.join(out, n + '.png')).convert('RGB')
        side.paste(d, (i * W, 0)); side.paste(r, (i * W, H))
        over.paste(Image.blend(r, d, 0.5), (i * W, 0))
    side.save(os.path.join(out, 'side.png')); over.save(os.path.join(out, 'over.png'))
