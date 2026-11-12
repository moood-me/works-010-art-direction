"""Films of Марат, shot as stop motion is: 12 frames a second ("on twos"), a real lens with a shallow focus, the camera
going along with him so he stays big in the frame. The motion is Kimodo's through the engine (move.mjs), the face
lives (life.mjs: blinks, the eyes' jumps and the gaze leading the head, speech, expressions), Blender renders
(render.py), ffmpeg makes the mp4.
usage: python3 films.py NAME [samples]    NAME: turn | walk | face | wave | dance"""
import json, os, subprocess, sys, math
import numpy as np
from common import CACHE, HERE, FOLDER, pack, BID

BLENDER = '/home/user/cache/blender/blender'
FPS = 12
_, BA = pack.read(f'{CACHE}/engine/data/bodies/{BID}.json')
NV = len(BA['positions'])

FILMS = {
    # motion, seconds or None (whole clip), life, camera: (distance, height of the target over the hips' floor
    # point, yaw of the camera from his front, lens), W, H
    'walk': dict(motion='walk', life=dict(talk=True, talkTo=2.4, seed=3, expr=[[0, {'beam': 1}], [2.6, {'laugh': 1}]]),
                 cam=(2.45, 0.72, -36, 50), size=(480, 560)),
    'wave': dict(motion='wave', life=dict(talk=True, seed=5, expr=[[0, {'beam': 1}], [1.5, {'laugh': 1}]]), cam=(2.4, 0.76, -22, 50), size=(480, 560)),
    'dance': dict(motion='dance', life=dict(seed=9, expr=[[0, {'laugh': 1}], [2.2, {'beam': 1}]]), cam=(2.6, 0.72, -28, 50), size=(480, 560)),
    'face': dict(motion='idle', seconds=5.5, life=dict(talk=True, talkTo=2.0, seed=11,
                 expr=[[0, {'beam': 1}], [2.2, {'laugh': 1}], [3.1, {'surprise': 1}], [3.9, {'sad': 1}], [4.7, {'anger': 1}]]),
                 head=dict(level='pitch', levelPitch=0.85), cam=(1.45, 'head', -20, 70), size=(460, 460)),
    'turn': dict(motion='bow', still=0, seconds=4.5, life=dict(seed=2, expr={'beam': 1}), cam=(2.35, 0.7, 'spin', 50),
                 size=(460, 580)),
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
    subprocess.run([os.path.join(CACHE, 'heavy.sh'), BLENDER, '-b', '--python', os.path.join(HERE, 'render.py'), '--', f'{out}/render.json'],
                   check=True, stdout=subprocess.DEVNULL)
    mp4 = os.path.join(FOLDER, 'pics', name + '.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{out}/f%04d.png',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', '-movflags', '+faststart', mp4], check=True)
    print('film', mp4)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 16)
