"""The films: frames from the page (shots.mjs), each laid on the drawing's own sheet (backdrop.py), ffmpeg → mp4.
   python3 films.py turn walk sneak idle wave sit face
The body moves by the engine's Kimodo motions; the face is alive in all of them (web/face.js); the camera follows
her and keeps her large; the floor is a sheet of paper with scraps glued on, so the travel shows."""
import sys, json, subprocess, os
from PIL import Image
from common import CACHE, HERE, heavy

PICS = os.path.join(os.path.dirname(HERE), 'pics')


def follow(yaw, pitch=0.10, dist=5.6, y=0.74, fov=20):
    return {'yaw': yaw, 'pitch': pitch, 'dist': dist, 'follow': [0, y, 0], 'fov': fov}


def motion_film(motion, frames, cam, expr, talk=lambda s: False, W=640, H=720, bd='film', step=1):
    return W, H, bd, 30 // step, [{'name': f'f{k:04d}', 'set': {'ground': True, 'motion': [motion], 't': i, 'cam': cam(i) if callable(cam) else cam,
                                                              'expr': expr, 'talk': talk(i / 30)}} for k, i in enumerate(range(0, frames, step))]


FILMS = {
    'walk': lambda: motion_film('walk', 120, follow(-0.55), [{'t': 0, 'name': 'calm'}, {'t': 2.6, 'name': 'joy'}]),
    'sneak': lambda: motion_film('sneak', 120, follow(-0.7, 0.12, 5.4, 0.66), [{'t': 0, 'name': 'calm'}, {'t': 1.2, 'name': 'surprise'}, {'t': 2.4, 'name': 'calm'}]),
    'idle': lambda: motion_film('idle', 150, follow(-0.3, 0.08, 4.6, 0.86), [{'t': 0, 'name': 'calm'}, {'t': 3.2, 'name': 'angry'}], lambda s: 1.0 < s < 2.8),
    'wave': lambda: motion_film('wave', 90, follow(-0.25), [{'t': 0, 'name': 'calm'}, {'t': 0.8, 'name': 'joy'}]),
    'sit': lambda: motion_film('sit', 120, follow(-0.9, 0.16, 5.4, 0.6), [{'t': 0, 'name': 'calm'}, {'t': 2.2, 'name': 'sad'}]),
}


def face_film():
    """a close look at the face while she stands (Kimodo's stance): blinking and glancing, muttering, then the sheet's
    expressions one after another, blended"""
    ex = [{'t': 0, 'name': 'calm'}, {'t': 3.6, 'name': 'joy'}, {'t': 5.0, 'name': 'surprise'}, {'t': 6.2, 'name': 'sad'},
          {'t': 7.6, 'name': 'angry'}, {'t': 9.0, 'name': 'calm'}]
    cam = {'yaw': -0.32, 'pitch': -0.05, 'dist': 2.1, 'joint': 'Head', 'offset': [0, 0.035, 0], 'fov': 20}
    return 640, 640, 'close', 30, [{'name': f'f{i:04d}', 'set': {'ground': False, 'motion': ['bow'], 't': 0, 'faceTime': i / 30, 'cam': cam,
                                                               'expr': ex, 'talk': 1.0 < i / 30 < 3.3}} for i in range(300)]


def turn_film():
    n = 72
    return 520, 720, 'film', 24, [{'name': f'f{i:04d}', 'set': {'ground': True, 'motion': ['bow'], 't': 0, 'faceTime': i / 24,
                                   'cam': {'yaw': -6.2832 * i / n, 'pitch': 0.10, 'dist': 5.6, 'follow': [0, 0.74, 0], 'fov': 20}}} for i in range(n)]


if __name__ == '__main__':
    for name in sys.argv[1:]:
        W, H, bd, fps, shots = face_film() if name == 'face' else turn_film() if name == 'turn' else FILMS[name]()
        out = f'{CACHE}/film-{name}'
        json.dump({'w': W, 'h': H, 'set': {'still': False}, 'shots': shots}, open(f'{CACHE}/job_film_{name}.json', 'w'))
        heavy(['node', f'{HERE}/shots.mjs', f'{CACHE}/job_film_{name}.json', f'{out}/raw'], check=True)
        os.makedirs(f'{out}/g', exist_ok=True)
        back = Image.open(f'{CACHE}/bd-{bd}.png').convert('RGBA')
        if back.size != (W, H): back = back.resize((W, H), Image.LANCZOS)
        for s in shots:
            im = back.copy(); im.alpha_composite(Image.open(f"{out}/raw/{s['name']}.png").convert('RGBA')); im.convert('RGB').save(f"{out}/g/{s['name']}.png")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', f'{out}/g/f%04d.png', '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p', '-crf', '25', '-movflags', '+faststart', f'{PICS}/{name}.mp4'], check=True)
        print(name, os.path.getsize(f'{PICS}/{name}.mp4'), flush=True)
