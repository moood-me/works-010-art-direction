"""The films: frames from the page (shots.mjs) → ffmpeg → short mp4s in ../pics.
  python3 films.py turn face walk bow
The face is alive in all of them (life.js: blinks, small gaze jumps, the gaze leading head turns, speech, expressions
blended). The body moves by the engine's Kimodo motions; the camera follows (perspective) and keeps her large."""
import sys, json, subprocess, os, shutil
from common import CACHE, HERE
import char

PICS = os.path.join(os.path.dirname(HERE), 'pics')


def follow(yaw, pitch=0.1, dist=4.0, y=0.6, fov=20):
    return {'yaw': yaw, 'pitch': pitch, 'dist': dist, 'follow': [0, y, 0], 'fov': fov}


def motion_film(motion, frames, cam, expr, talk=(), W=560, H=720, step=1, t0=0):
    return W, H, 30 // step, [{'name': f'f{i:04d}', 'set': {'motion': [motion], 't': t0 + i * step, 'faceTime': i * step / 30, 'cam': cam, 'expr': expr, 'talk': list(talk), 'lightCam': False, 'floor': True}}
                              for i in range(frames)]


FILMS = char.FILMS(follow, motion_film)


def face_film():
    cam = {'yaw': -0.3, 'rel': 'head', 'pitch': 0.03, 'dist': 1.6 * char.HS, 'joint': 'Head', 'offset': [0, 0.075 * char.HS + 0.04, 0.02], 'fov': 14}
    return 560, 560, 30, [{'name': f'f{i:04d}', 'set': {**char.STAND, 'faceTime': i / 30, 'cam': cam, 'expr': char.FACE_EXPR, 'talk': char.FACE_TALK}} for i in range(char.FACE_FRAMES)]


def turn_film():
    n = 72; hgt = (char.FLOOR + 110) * 0.0028
    return 440, 800, 24, [{'name': f'f{i:04d}', 'set': {**char.STAND, 'faceTime': i / 24, 'expr': [{'t': 0, 'name': 'calm'}],
                                                        'cam': {'yaw': -6.2832 * i / n, 'follow': [0, hgt / 2 - 0.07, 0], 'height': hgt, 'dist': 6}}} for i in range(n)]


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
