"""The films, each frame laid on the drawing's backdrop through its gouache filter, then ffmpeg → short mp4s.
   python3 films.py <name>…   (names: turn, walk, sit, wave, jump, look, face)
The face is alive in all of them (web/face.js): blinks, the gaze's small jumps and its lead before head turns; some
talk; expressions change over time (blended). The body moves by the engine's Kimodo motions; the camera follows him
(a perspective one, over a painted ground that slides under him, so the travel shows) and keeps him large."""
import sys, json, subprocess, os
from common import CACHE, HERE
from compose import compose_many

PICS = os.path.join(os.path.dirname(HERE), 'pics')
M = '/cache/to3d-r3-s9-tim/tim.json'


def follow(yaw, pitch=0.1, dist=3.9, y=0.55, fov=20):
    return {'yaw': yaw, 'pitch': pitch, 'dist': dist, 'follow': [0, y, 0], 'fov': fov}


def motion_film(motion, frames, cam, expr, talk=lambda s: False, W=640, H=720, bd='figure'):
    return W, H, bd, 30, [{'name': f'f{i:04d}', 'set': {'model': M, 'ground': True, 'motion': [motion], 't': i, 'cam': cam,
                                                        'expr': expr, 'talk': talk(i / 30)}} for i in range(frames)]


FILMS = {
    'walk': lambda: motion_film('walk', 120, follow(-0.55), [{'t': 0, 'name': 'calm'}, {'t': 2.4, 'name': 'joy'}], lambda s: 0.6 < s < 2.3),
    'sit': lambda: motion_film('sit', 120, follow(-0.9, 0.16, 3.8, 0.4), [{'t': 0, 'name': 'calm'}, {'t': 2.2, 'name': 'sad'}]),
    'wave': lambda: motion_film('wave', 90, follow(-0.25), [{'t': 0, 'name': 'joy'}], lambda s: 0.9 < s < 2.8),
    'jump': lambda: motion_film('jump', 90, follow(-0.4, 0.08, 4.4, 0.65), [{'t': 0, 'name': 'surprise'}, {'t': 1.3, 'name': 'joy'}]),
    'look': lambda: motion_film('idle', 150, follow(-0.2, 0.06, 3.0, 0.75), [{'t': 0, 'name': 'calm'}]),
}


def face_film():
    """a close look at the face: standing still (Kimodo's stance), blinking and glancing, talking, then the sheet's
    expressions one after another, blended"""
    ex = [{'t': 0, 'name': 'calm'}, {'t': 3.8, 'name': 'joy'}, {'t': 5.0, 'name': 'surprise'}, {'t': 6.2, 'name': 'sad'},
          {'t': 7.6, 'name': 'anger'}, {'t': 8.8, 'name': 'calm'}]
    cam = {'yaw': -0.35, 'pitch': 0.04, 'dist': 1.6, 'joint': 'Head', 'offset': [0, 0.05, 0], 'fov': 20}
    n = 300
    return 600, 600, 'portrait', 30, [{'name': f'f{i:04d}', 'set': {'model': M, 'ground': False, 'motion': ['bow'], 't': 0, 'faceTime': i / 30, 'cam': cam,
                                                                     'expr': ex, 'talk': 1.0 < i / 30 < 3.5}} for i in range(n)]


def turn_film():
    n = 72
    return 500, 760, 'figure', 24, [{'name': f'f{i:04d}', 'set': {'model': M, 'ground': False, 'motion': ['bow'], 't': 0, 'faceTime': i / 24,
                                     'cam': {'yaw': -6.2832 * i / n, 'follow': [0, 0.6, 0], 'height': 1.45}}} for i in range(n)]


for name in sys.argv[1:]:
    W, H, bd, fps, shots = face_film() if name == 'face' else turn_film() if name == 'turn' else FILMS[name]()
    out = f'{CACHE}/film-{name}'
    json.dump({'w': W, 'h': H, 'shots': shots}, open(f'{CACHE}/job_film_{name}.json', 'w'))
    subprocess.run(['node', f'{HERE}/shots.mjs', f'{CACHE}/job_film_{name}.json', f'{out}/raw'], check=True, capture_output=True)
    os.makedirs(f'{out}/g', exist_ok=True)
    compose_many([(f'{out}/g/f{i:04d}.png', [(f'{out}/raw/f{i:04d}.png', 0, 0)]) for i in range(len(shots))], W, H, bd)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', f'{out}/g/f%04d.png', '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '26', '-movflags', '+faststart', f'{PICS}/{name}.mp4'], check=True)
    print(name, os.path.getsize(f'{PICS}/{name}.mp4'), flush=True)
