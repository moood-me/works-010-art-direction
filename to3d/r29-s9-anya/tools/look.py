"""Quick looks while building: python3 look.py [clay] — the whole figure from four sides and the head close, one sheet."""
import sys, json, subprocess
from PIL import Image
from common import CACHE, HERE
M = f'/cache/{CACHE.split("/")[-1]}'
name = M.split('-')[-1]
clay = 'clay' in sys.argv
hgt = float(sys.argv[sys.argv.index('h') + 1]) if 'h' in sys.argv else 1.85
base = {'model': f'{M}/{name}.json', 'clay': clay, 'face': None if clay else f'{M}/face/calm.png', 'live': False, 'motion': ['bow'], 't': 0}
shots = [{'name': f'b{i}', 'set': {**base, 'cam': {'yaw': y, 'follow': [0, hgt / 2 - 0.03, 0], 'height': hgt}}} for i, y in enumerate((0, -0.6, -1.5708, 3.1416))]
shots += [{'name': f'h{i}', 'set': {**base, 'w': 460, 'cam': {'yaw': y, 'joint': 'Head', 'offset': [0, 0.03, 0], 'height': 0.5}}} for i, y in enumerate((0, -0.6, -1.5708, 2.5))]
json.dump({'w': 460, 'h': 760, 'shots': shots}, open(f'{CACHE}/job_look.json', 'w'))
r = subprocess.run(['node', f'{HERE}/shots.mjs', f'{CACHE}/job_look.json', f'{CACHE}/look'], capture_output=True, text=True)
if r.returncode: print(r.stdout[-2000:], r.stderr[-3000:])
S = Image.new('RGB', (460 * 4, 760 * 2), (236, 159, 147))
for k, p in enumerate(('b', 'h')):
    for i in range(4):
        im = Image.open(f'{CACHE}/look/{p}{i}.png').convert('RGBA'); S.paste(im, (460 * i, 760 * k), im)
S.save(f'{CACHE}/look.jpg', quality=88)
