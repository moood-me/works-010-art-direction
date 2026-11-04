"""Quick looks while building: a few views of the pack side by side.
  python3 look.py name '[{"cam": …, …}, …]' [w h]   → /home/user/cache/to3d-r9-s7-anya/look/name.png"""
import sys, os, json, subprocess
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = '/home/user/cache/to3d-r9-s7-anya/look'
PACK = os.environ.get('PACK', '/cache/to3d-r9-s7-anya/out/anya.json')


def look(name, sets, w=420, h=520):
    os.makedirs(OUT, exist_ok=True)
    shots = [dict(name=f'{name}-{i}', set=s) for i, s in enumerate(sets)]
    j = os.path.join(OUT, name + '.json')
    json.dump(dict(pack=PACK, w=w, h=h, shots=shots), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, OUT], check=True, stdout=subprocess.DEVNULL,
                   env=dict(os.environ, NODE_PATH='/opt/node-tools/node_modules'))
    ims = [Image.open(os.path.join(OUT, f'{name}-{i}.png')).convert('RGB') for i in range(len(sets))]
    o = Image.new('RGB', (w * len(ims), h))
    for i, im in enumerate(ims): o.paste(im, (i * w, 0))
    o.save(os.path.join(OUT, name + '.png'))


HEAD = lambda yaw, **k: dict(dict(pose='stand', still=True, shadow=False, cam=dict(mode='ortho', h=0.36, yaw=yaw, pitch=0.0, target=[0, 1.50, 0.0])), **k)
FIG = lambda yaw, **k: dict(dict(pose='stand', still=True, cam=dict(mode='ortho', h=1.8, yaw=yaw, pitch=0.05, target=[0, 0.86, 0.0])), **k)

if __name__ == '__main__':
    name, sets = sys.argv[1], sys.argv[2]
    sets = eval(sets, dict(HEAD=HEAD, FIG=FIG))
    w, h = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (420, 520)
    look(name, sets, w, h)
