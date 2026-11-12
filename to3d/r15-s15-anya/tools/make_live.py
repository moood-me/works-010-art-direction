"""The live face and motions: films for the page (to3d/r15-s15-anya/pics). python3 make_live.py [name …]"""
import os, sys, json, subprocess, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = '/home/user/cache/to3d-r15-s15-anya/live'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = '/works-010-art-direction/to3d/r15-s15-anya/data/anya.json'
STAND = dict(pose='stand', poseOpts={'out': 0.08})
HEAD = dict(mode='ortho', h=0.44, cy=1.40, yaw=-0.45, pitch=0.0, target=[0, 1.40, 0])
FULL = lambda yaw: dict(mode='persp', dist=6.2, fov=22, yaw=yaw, pitch=0.06, cy=0.82, follow=True)
NEAR = lambda yaw: dict(mode='persp', dist=1.45, fov=22, yaw=yaw, pitch=0.03, focus='Head', up=0.03, follow=False)

FILMS = {
    # the face alone: calm (blinks, saccades), talking, the sheet's expressions one into another, a mix
    'face-live': dict(w=520, h=560, fps=30, set=dict(STAND, clip=None, cam=HEAD, talk=True, talkFrom=2.0, talkTo=5.0,
                      exprTrack=[[0, 'dream'], [5.2, 'joy'], [6.9, 'surprise'], [8.4, 'sad'], [10.0, 'anger'],
                                 [11.6, {'joy': 0.5, 'surprise': 0.5}]]), time=(0, 13.2)),
    # looking round (Kimodo's idle): the eyes lead the head, blinks with the turns
    'idle-face': dict(w=520, h=560, fps=30, set=dict(clip='idle', cam=NEAR(0.2), exprTrack=[[0, 'dream']], talk=False), frames=150),
    'idle': dict(w=540, h=860, fps=30, set=dict(clip='idle', cam=FULL(0.3), exprTrack=[[0, 'dream']], talk=False), frames=150),
    'walk': dict(w=640, h=860, fps=30, set=dict(clip='walk', cam=FULL(0.75), exprTrack=[[0, 'dream'], [2.0, 'joy']], talk=False), frames=120),
    'wave': dict(w=640, h=860, fps=30, set=dict(clip='wave', cam=FULL(0.35), exprTrack=[[0, 'joy']], talk=True, talkFrom=0.6, talkTo=2.4), frames=90),
    'sit': dict(w=640, h=860, fps=30, set=dict(clip='sit', cam=dict(FULL(0.9), cy=0.6), exprTrack=[[0, 'dream'], [2.4, 'sad']], talk=False), frames=120),
    'stomp': dict(w=640, h=860, fps=30, set=dict(clip='stomp', cam=FULL(0.4), exprTrack=[[0, 'anger']], talk=False), frames=90),
}


def run(name, f):
    d = os.path.join(WORK, name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    shots = []
    if 'time' in f:
        t0, t1 = f['time']; n = int((t1 - t0) * f['fps'])
        first = dict(f['set'])
        shots.append(dict(name=f'{name}/f0000', set=dict(first, time=t0)))
        for k in range(1, n): shots.append(dict(name=f'{name}/f{k:04d}', set=dict(time=t0 + k / f['fps'])))
    else:
        shots.append(dict(name=f'{name}/f0000', set=dict(f['set'], t=0)))
        for k in range(1, f['frames']): shots.append(dict(name=f'{name}/f{k:04d}', set=dict(t=k)))
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PK, w=f['w'], h=f['h'], shots=shots), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True, env=ENV, stdout=subprocess.DEVNULL)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(f['fps']), '-i', os.path.join(d, 'f%04d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', os.path.join(PICS, name + '.mp4')], check=True)


for name in (sys.argv[1:] or FILMS):
    run(name, FILMS[name]); print(name)
