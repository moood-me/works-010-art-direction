"""Films of Тим, shot as stop motion is: 12 frames a second ("on twos"), a real lens with a shallow focus, the camera
going along with him so he stays big in the frame. The motion is Kimodo's through the engine (move.mjs), the face
lives (life.mjs: blinks, the eyes' jumps and the gaze leading the head, speech, expressions), Blender renders
(render.py), ffmpeg makes the mp4.
usage: python3 films.py NAME [samples]    NAME: turn | walk | face | wave | jump"""
import json, os, subprocess, sys, math
import numpy as np
from common import CACHE, HERE, FOLDER, pack

BLENDER = '/home/user/cache/blender/blender'
FPS = 12
_, BA = pack.read(f'{CACHE}/engine/data/bodies/savely8.json')
NV = len(BA['positions'])

FILMS = {
    # motion, seconds or None (whole clip), life, camera: (distance, height of the target over the hips' floor
    # point, yaw of the camera from his front, lens), W, H
    'walk': dict(motion='walk', life=dict(talk=True, seed=3, expr=[[0, {'calm': 1}], [2.4, {'joy': 1}]]),
                 cam=(2.2, 0.62, -38, 50), size=(640, 720)),
    'wave': dict(motion='wave', life=dict(talk=True, seed=5, expr={'grin': 1}), cam=(1.9, 0.66, -25, 50), size=(640, 720)),
    'jump': dict(motion='jump', life=dict(seed=9, expr=[[0, {'surprise': 1}], [1.4, {'joy': 1}]]), cam=(2.4, 0.7, -30, 50), size=(640, 720)),
    'face': dict(motion='idle', seconds=6.0, life=dict(talk=True, talkTo=2.4, seed=11,
                 expr=[[0, {'calm': 1}], [2.6, {'joy': 1}], [3.5, {'surprise': 1}], [4.3, {'sad': 1}], [5.1, {'anger': 1}]]),
                 head=dict(level='pitch', levelPitch=0.8), cam=(1.35, 'head', -20, 70), size=(560, 560)),
    'turn': dict(motion='bow', still=0, seconds=5.0, life=dict(seed=2, expr={'calm': 1}), cam=(2.0, 0.6, 'spin', 50),
                 size=(560, 720)),
}


def main(name, samples=16):
    F = FILMS[name]
    out = os.path.join(CACHE, 'film-' + name); os.makedirs(out, exist_ok=True)
    mv = dict(out=f'{out}/frames.bin', motion=F['motion'], life=F['life'])
    if 'head' in F: mv['head'] = F['head']
    with open(os.path.join(FOLDER, '../../engine/motions', F['motion'] + '.json')) as f:
        m = json.load(f)
    fps_m = m.get('fps', 30); nfr = m['frames']
    secs = F.get('seconds') or (nfr - 1) / fps_m
    n = int(secs * FPS)
    if 'still' in F:          # the turntable: one pose, the face alive (its own clock), the camera going round
        mv['frames'] = [F['still']] * n
        mv['clockFps'] = FPS
        mv['head'] = dict(level=True)
    else:
        mv['frames'] = [min(nfr - 1, k * fps_m / FPS) for k in range(n)]
    json.dump(mv, open(f'{out}/job-move.json', 'w'))
    subprocess.run(['node', os.path.join(HERE, 'move.mjs'), f'{out}/job-move.json'], check=True)
    info = json.load(open(f'{out}/frames.json'))
    hips = np.array(info['hips']); head = np.array(info['head'])
    # the camera: going along smoothly (a slow follow of the hips' path on the floor)
    d, ty, yaw, lens = F['cam']
    views = []
    sm = hips.copy()
    for k in range(1, len(sm)): sm[k] = sm[k - 1] + 0.35 * (hips[k] - sm[k - 1])
    for k in range(len(info['times'])):
        i = k
        c = sm[i].copy(); c[1] = 0
        if yaw == 'spin': a = math.radians(-360 * k / n)
        else: a = math.radians(yaw)
        tgt = c + np.array([0, (head[i][1] + 0.13) if ty == 'head' else ty, 0])
        if ty == 'head': tgt[0], tgt[2] = head[i][0], head[i][2] + 0.03
        pos = tgt + np.array([math.sin(a) * d, 0.08 if ty == 'head' else 0.18, math.cos(a) * d])
        views.append(dict(name=f'f{k:04d}', W=F['size'][0], H=F['size'][1], frame=i,
                          cam=dict(type='persp', pos=pos.tolist(), target=tgt.tolist(), lens=lens, fstop=2.0 if ty == 'head' else 0.8,
                                   focus=float(np.linalg.norm(pos - tgt)) - (0.12 if ty == 'head' else 0.0))))
    job = dict(out=out, samples=samples, frames=f'{out}/frames.bin', views=views, noise=0.05)
    json.dump(job, open(f'{out}/render.json', 'w'))
    subprocess.run([BLENDER, '-b', '--python', os.path.join(HERE, 'render.py'), '--', f'{out}/render.json'],
                   check=True, stdout=subprocess.DEVNULL)
    mp4 = os.path.join(FOLDER, 'pics', name + '.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{out}/f%04d.png',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', '-movflags', '+faststart', mp4], check=True)
    print('film', mp4)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 16)
