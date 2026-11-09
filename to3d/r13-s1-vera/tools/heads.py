"""Close looks at the head for work (not for the page): python3 heads.py out.png [expr …]"""
import sys, json, subprocess
from PIL import Image
from common import CACHE, HERE
import char
names = [a for a in sys.argv[2:] if not a.startswith('--') and not a.endswith('.json')] or ['calm']
ZOOM = 0.52
if names[0].startswith('z'): ZOOM = float(names[0][1:]); names = names[1:]
shots = []
for n in names:
    for yaw, k in ((0, 'a'), (-0.5, 'b'), (-1.5708, 'c'), (2.6, 'd')):
        shots.append({'name': n + k, 'set': {'expr': [{'t': 0, 'name': n}], 'cam': {'yaw': yaw, 'rel': 'head', 'joint': 'Head', 'offset': [0, 0.11 if ZOOM > 0.4 else 0.04, 0.03], 'dist': 5, 'height': ZOOM}}})
json.dump({'w': 560, 'h': 560, 'page': ('&model=' + sys.argv[sys.argv.index('--model') + 1]) if '--model' in sys.argv else '', 'set': {**char.STAND, 'still': True}, 'shots': shots}, open(f'{CACHE}/job_heads.json', 'w'))
subprocess.run(['node', f'{HERE}/shots.mjs', f'{CACHE}/job_heads.json', f'{CACHE}/heads'], check=True, stdout=subprocess.DEVNULL)
o = Image.new('RGB', (560 * 4, 560 * len(names)))
for i, n in enumerate(names):
    for j, k in enumerate('abcd'): o.paste(Image.open(f'{CACHE}/heads/{n}{k}.png').convert('RGB'), (560 * j, 560 * i))
o.resize((o.width * 2 // 3, o.height * 2 // 3) if len(names) == 1 else (o.width // 2, o.height // 2)).save(sys.argv[1])
