"""Quick looks while building: python3 look.py name '{"set": {...}}' views…  → CACHE/look/name.png (a row of views).
views: f (front), q (three-quarter), s (her right side), b (back), l (her left three-quarter); head: hf hq hs hb hl"""
import sys, json, subprocess, os
from PIL import Image
from common import CACHE, HERE, heavy

YAW = dict(f=0, q=-0.62, s=-1.5708, b=3.1416, l=0.75, r=-2.4)


def look(name, set_=None, views='fqs', size=(520, 900), head=False, model=None, bg=(213, 217, 196), height=None):
    shots = []
    for v in views:
        cam = {'yaw': YAW[v], 'joint': 'Head', 'offset': [0, 0.03, 0], 'height': height or 0.52} if head else {'yaw': YAW[v], 'follow': [0, 0.78, 0], 'height': height or 1.7}
        shots.append({'name': f'{name}-{v}', 'set': {'cam': cam}})
    job = {'w': size[0], 'h': size[1], 'set': {'ground': 'shadow', 'still': True, **(set_ or {})}, 'shots': shots}
    if model: job['set']['model'] = model
    os.makedirs(f'{CACHE}/look', exist_ok=True)
    json.dump(job, open(f'{CACHE}/look/{name}.json', 'w'))
    r = heavy(['node', f'{HERE}/shots.mjs', f'{CACHE}/look/{name}.json', f'{CACHE}/look'], capture_output=True, text=True)
    if r.returncode: print(r.stdout[-2000:], r.stderr[-3000:]); sys.exit(1)
    out = Image.new('RGB', (size[0] * len(views), size[1]), bg)
    for i, v in enumerate(views):
        im = Image.open(f'{CACHE}/look/{name}-{v}.png').convert('RGBA'); out.paste(im, (i * size[0], 0), im)
    out.save(f'{CACHE}/look/{name}.png'); print(f'{CACHE}/look/{name}.png')


if __name__ == '__main__':
    name = sys.argv[1]; o = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    look(name, o.get('set'), o.get('views', 'fqs'), tuple(o.get('size', (520, 900))), o.get('head', False), o.get('model'), height=o.get('height'))
