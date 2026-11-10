"""The live face and the Kimodo motions: films for the page (to3d/r9-s7-anya/pics). python3 make_live.py [name …]
Reads the pack from ../data (copy build.py's output there first)."""
import os, sys, json, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = '/home/user/cache/to3d-r9-s7-anya/live'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = '/works-010-art-direction/to3d/r9-s7-anya/data/anya.json'
STAND = dict(pose='stand')
HEAD = dict(mode='ortho', h=0.42, yaw=-0.38, pitch=0.05, target=[0, 1.47, 0])
# the camera follows the pelvis, near, so she is big in the frame
FULL = lambda yaw, d=4.1: dict(mode='persp', dist=d, fov=24, yaw=yaw, pitch=0.08, cy=0.83, follow=True)
NEAR = lambda yaw: dict(mode='persp', dist=1.45, fov=22, yaw=yaw, pitch=0.03, focus='Head', up=0.07, follow=False)

FILMS = {
    'face-live': dict(w=480, h=540, fps=30, set=dict(STAND, clip=None, cam=HEAD, talk=True, talkFrom=2.0, talkTo=5.0,
                      exprTrack=[[0, 'calm'], [5.2, 'joy'], [6.9, 'surprise'], [8.4, 'sad'], [10.0, 'anger'],
                                 [11.6, {'joy': 0.35, 'surprise': 0.65}]]), time=(0, 13.2)),
    'idle-face': dict(w=480, h=540, fps=30, set=dict(clip='idle', cam=NEAR(-0.2), exprTrack=[[0, 'dream']], talk=False), frames=150),
    'walk': dict(w=560, h=860, fps=30, set=dict(clip='walk', cam=FULL(0.8), exprTrack=[[0, 'calm'], [2.0, 'dream']], talk=False), frames=120),
    'wave': dict(w=560, h=860, fps=30, set=dict(clip='wave', cam=FULL(0.35), exprTrack=[[0, 'joy']], talk=True, talkFrom=0.6, talkTo=2.4), frames=90),
    'sit': dict(w=560, h=860, fps=30, set=dict(clip='sit', cam=dict(FULL(0.9, 4.2), cy=0.6), exprTrack=[[0, 'calm'], [2.4, 'sad']], talk=False), frames=120),
}


def run(name, f):
    d = os.path.join(WORK, name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    shots = []
    if 'time' in f:
        t0, t1 = f['time']; n = int((t1 - t0) * f['fps'])
        shots.append(dict(name=f'{name}/f0000', set=dict(f['set'], time=t0)))
        for k in range(1, n): shots.append(dict(name=f'{name}/f{k:04d}', set=dict(time=t0 + k / f['fps'])))
    else:
        shots.append(dict(name=f'{name}/f0000', set=dict(f['set'], t=0)))
        for k in range(1, f['frames']): shots.append(dict(name=f'{name}/f{k:04d}', set=dict(t=k)))
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PK, w=f['w'], h=f['h'], shots=shots), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True, env=ENV, stdout=subprocess.DEVNULL)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(f['fps']), '-i', os.path.join(d, 'f%04d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '26', '-movflags', '+faststart', os.path.join(PICS, name + '.mp4')], check=True)


for name in (sys.argv[1:] or FILMS):
    run(name, FILMS[name]); print(name, flush=True)
