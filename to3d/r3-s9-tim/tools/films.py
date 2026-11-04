"""The films: a turn round (the standing pose, 360°) and a walk (Kimodo's walk through the engine), each frame laid
on the drawing's backdrop through its gouache filter; ffmpeg makes short mp4s.   python3 films.py turn|walk"""
import sys, json, subprocess, os, glob
from common import CACHE, HERE
from compose import compose_many

PICS = os.path.join(os.path.dirname(HERE), 'pics')
base = {'model': '/cache/to3d-r3-s9-tim/tim.json', 'face': '/cache/to3d-r3-s9-tim/face/calm.png'}
kind = sys.argv[1]
out = f'{CACHE}/film-{kind}'
if kind == 'turn':
    W, H, n = 500, 760, 72
    shots = [{'name': f'f{i:04d}', 'set': {**base, 'motion': ['bow'], 't': 0,
              'cam': {'yaw': -6.2832 * i / n, 'follow': [0, 0.6, 0], 'height': 1.45}}} for i in range(n)]
    bd, fps = 'figure', 24
elif kind == 'walk':
    W, H, n = 960, 600, 120
    shots = [{'name': f'f{i:04d}', 'set': {**base, 'motion': ['walk'], 't': i,
              'cam': {'yaw': -1.05, 'target': [0.05, 0.7, 1.45], 'height': 1.75}}} for i in range(n)]
    bd, fps = 'walk', 30
json.dump({'w': W, 'h': H, 'shots': shots}, open(f'{CACHE}/job_film.json', 'w'))
subprocess.run(['node', f'{HERE}/shots.mjs', f'{CACHE}/job_film.json', f'{out}/raw'], check=True, capture_output=True)
os.makedirs(f'{out}/g', exist_ok=True)
compose_many([(f'{out}/g/f{i:04d}.png', [(f'{out}/raw/f{i:04d}.png', 0, 0)]) for i in range(n)], W, H, bd)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', f'{out}/g/f%04d.png', '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p', '-crf', '26', '-movflags', '+faststart', f'{PICS}/{kind}.mp4'], check=True)
print(kind, os.path.getsize(f'{PICS}/{kind}.mp4'))
