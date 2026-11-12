"""A contact sheet of a motion's frames: python3 sheet.py motion from to step [yaw]"""
import sys, json, subprocess
from PIL import Image
from common import CACHE, HERE
m, a, b, st = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); yaw = float(sys.argv[5]) if len(sys.argv) > 5 else -0.6
shots = [{'name': f'{m}{i:03d}', 'set': {'motion': [m], 't': i, 'cam': {'yaw': yaw, 'follow': [0, 0.78, 0], 'height': 1.7}}} for i in range(a, b, st)]
json.dump({'w': 360, 'h': 640, 'set': {'ground': 'shadow', 'still': True}, 'shots': shots}, open(f'{CACHE}/look/{m}.json', 'w'))
subprocess.run(['flock', '/home/user/cache/heavy.1.lock', 'node', f'{HERE}/shots.mjs', f'{CACHE}/look/{m}.json', f'{CACHE}/look'], check=True)
out = Image.new('RGB', (360 * len(shots), 640), (213, 217, 196))
for k, s in enumerate(shots):
    im = Image.open(f"{CACHE}/look/{s['name']}.png").convert('RGBA'); out.paste(im, (k * 360, 0), im)
out.save(f'{CACHE}/look/{m}.png')
