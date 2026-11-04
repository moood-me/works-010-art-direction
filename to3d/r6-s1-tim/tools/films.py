"""The films: frames from the page (shots.mjs) → ffmpeg → short mp4s in ../pics.
  python3 films.py turn walk sit wave jump look face
The face is alive in all of them (life.js: blinks, small gaze jumps, the gaze leading head turns, speech, expressions
blended). The body moves by the engine's Kimodo motions; the camera follows him (perspective) and keeps him large."""
import sys, json, subprocess, os, shutil
from common import CACHE, HERE

PICS = os.path.join(os.path.dirname(HERE), 'pics')


def follow(yaw, pitch=0.1, dist=4.0, y=0.6, fov=20):
    return {'yaw': yaw, 'pitch': pitch, 'dist': dist, 'follow': [0, y, 0], 'fov': fov}


def motion_film(motion, frames, cam, expr, talk=(), W=640, H=720, step=1):
    return W, H, 30 // step, [{'name': f'f{i:04d}', 'set': {'motion': [motion], 't': i * step, 'cam': cam, 'expr': expr, 'talk': list(talk), 'lightCam': False, 'floor': True}}
                              for i in range(frames)]


FILMS = {
    'walk': lambda: motion_film('walk', 150, follow(-0.6), [{'t': 0, 'name': 'calm'}, {'t': 2.6, 'name': 'joy'}], [[0.8, 2.4]]),
    'sit': lambda: motion_film('sit', 150, follow(-0.9, 0.14, 3.4, 0.42), [{'t': 0, 'name': 'calm'}, {'t': 2.6, 'name': 'sad'}]),
    'wave': lambda: motion_film('wave', 120, follow(-0.25, 0.06, 3.2, 0.62), [{'t': 0, 'name': 'joy'}], [[1.0, 3.2]]),
    'jump': lambda: motion_film('jump', 105, follow(-0.4, 0.08, 4.0, 0.62), [{'t': 0, 'name': 'surprise'}, {'t': 1.4, 'name': 'joy'}]),
    'look': lambda: motion_film('idle', 180, follow(-0.25, 0.05, 2.6, 0.72), [{'t': 0, 'name': 'calm'}, {'t': 4.0, 'name': 'smirk'}], [[1.5, 3.5]]),
}


def face_film():
    ex = [{'t': 0, 'name': 'calm'}, {'t': 3.6, 'name': 'joy'}, {'t': 5.0, 'name': 'surprise'}, {'t': 6.4, 'name': 'sad'},
          {'t': 7.8, 'name': 'anger'}, {'t': 9.2, 'name': 'smirk'}]
    cam = {'yaw': -0.32, 'pitch': 0.03, 'dist': 1.6, 'joint': 'Head', 'offset': [0, 0.075, 0], 'fov': 14}
    return 600, 600, 30, [{'name': f'f{i:04d}', 'set': {'motion': ['bow'], 't': 0, 'faceTime': i / 30, 'cam': cam, 'expr': ex, 'talk': [[1.0, 3.3]]}} for i in range(320)]


def turn_film():
    n = 96
    return 500, 820, 24, [{'name': f'f{i:04d}', 'set': {'motion': ['bow'], 't': 0, 'faceTime': i / 24, 'expr': [{'t': 0, 'name': 'calm'}],
                                                        'cam': {'yaw': -6.2832 * i / n, 'follow': [0, 0.62, 0], 'height': 1.42, 'dist': 5}}} for i in range(n)]


if __name__ == '__main__':
    for name in sys.argv[1:]:
        W, H, fps, shots = face_film() if name == 'face' else turn_film() if name == 'turn' else FILMS[name]()
        out = f'{CACHE}/film-{name}'
        shutil.rmtree(out, ignore_errors=True)
        json.dump({'w': W, 'h': H, 'shots': shots}, open(f'{CACHE}/job_film_{name}.json', 'w'))
        subprocess.run(['node', f'{HERE}/shots.mjs', f'{CACHE}/job_film_{name}.json', out], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', f'{out}/f%04d.png', '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p', '-crf', '25', '-movflags', '+faststart', f'{PICS}/{name}.mp4'], check=True)
        print(name, os.path.getsize(f'{PICS}/{name}.mp4'), flush=True)
