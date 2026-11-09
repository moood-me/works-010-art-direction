"""Clay pictures of the head's steps with the drawing's outlines over them (front and side), for judging the fit."""
import sys, json, subprocess, numpy as np
from PIL import Image, ImageDraw
from model import part, write
from hbm import tris
from drawing import K, FRONT, SIDE, curve
from common import CACHE, IX, HERE
from body import B

d = np.load(f'{CACHE}/head_steps.npz')
key = sys.argv[1] if len(sys.argv) > 1 else 'warped'
if key == 'orig':
    from hbm import load
    V, Q, _ = load(); T = tris(Q); V = V - [0, 0.7375, 0]
else:
    V = d[key]; T = tris(d['Q'])
    if key == 'faired': V = V - [0, 0.7375, 0]
TY = -V[:, 1].min()
n = len(V)
write('look-head', [part(V, T, np.tile([IX['Head'], 0, 0, 0], (n, 1)), np.tile([1, 0, 0, 0], (n, 1)), 'clay')], B['joints'], B['frames'])
H = 0.5; S = 600
job = {'w': S, 'h': S, 'set': {'clay': True, 'model': '/cache/to3d-r29-s9-anya/look-head.json'}, 'shots': [
    {'name': 'front', 'set': {'cam': {'yaw': 0, 'target': [0, float(TY), -0.028], 'height': H}}},
    {'name': 'side', 'set': {'cam': {'yaw': -1.5708, 'target': [0, float(TY), -0.028], 'height': H}}},
    {'name': 'q34', 'set': {'cam': {'yaw': -0.7, 'target': [0, float(TY), -0.028], 'height': H}}}]}
json.dump(job, open(f'{CACHE}/job_head.json', 'w'))
subprocess.run(['node', f'{HERE}/shots.mjs', f'{CACHE}/job_head.json', f'{CACHE}/head'], check=True, capture_output=True)
ims = []
for name, outline, off in (('front', FRONT, 0), ('side', SIDE, 8), ('q34', None, 0)):
    im = Image.open(f'{CACHE}/head/{name}.png').convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im)
    dr = ImageDraw.Draw(bg)
    if outline and key == 'warped':
        c = curve(outline)
        pts = [((x + off) * K / H * S + S / 2, y * K / H * S + S / 2) for x, y in c]
        dr.line(pts + [pts[0]], fill=(200, 40, 40), width=2)
        if name == 'side':
            for p, q in zip(d['src'], d['dst']):
                pass
    ims.append(bg)
out = Image.new('RGB', (S * 3, S), 'white')
for i, im in enumerate(ims): out.paste(im, (i * S, 0))
out.save(f'{CACHE}/head_{key}.png')
