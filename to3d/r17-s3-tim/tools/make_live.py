"""The live face and the motions: films for the page (../pics). python3 make_live.py [name …]
Reads the pack from ../data (copy it there from the cache first)."""
import os, sys, json, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER, NAME = 'r17-s3-tim', 'tim'
WORK = f'/home/user/cache/to3d-{FOLDER}/live'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = f'/works-010-art-direction/to3d/{FOLDER}/data/{NAME}.json'
STAND = dict(pose='stand', poseOpts={'out': 0.04})
HEAD = dict(mode='ortho', h=0.56, cy=1.0, yaw=-0.45, pitch=0.0, target=[0, 1.0, 0])
FULL = lambda yaw, **k: dict(dict(mode='persp', dist=4.4, fov=22, yaw=yaw, pitch=0.06, cy=0.64, follow=True), **k)
NEAR = lambda yaw: dict(mode='persp', dist=1.75, fov=22, yaw=yaw, pitch=0.03, focus='Head', up=0.13, follow=False)
R = 'mischief'

FILMS = {
    # the face alone: calm (blinks, saccades), talking, the sheet's expressions one into another, a mix
    'face-live': dict(w=480, h=480, fps=30, set=dict(STAND, clip=None, cam=HEAD, talk=True, talkFrom=2.0, talkTo=5.0,
                      exprTrack=[[0, R], [5.2, 'joy'], [6.9, 'surprise'], [8.4, 'sad'], [10.0, 'anger'],
                                 [11.6, {'joy': 0.5, 'surprise': 0.5}]]), time=(0, 13.2)),
    'idle-face': dict(w=480, h=480, fps=30, set=dict(clip='idle', cam=NEAR(0.2), exprTrack=[[0, R]], talk=False), frames=150),
    'walk': dict(w=520, h=640, fps=30, set=dict(clip='walk', cam=FULL(0.75), exprTrack=[[0, R], [2.0, 'joy']], talk=False), frames=120),
    'run': dict(w=520, h=640, fps=30, set=dict(clip='run', cam=FULL(0.8), exprTrack=[[0, 'joy']], talk=False), frames=90),
    'jump': dict(w=520, h=640, fps=30, set=dict(clip='jump', cam=FULL(0.4, cy=0.72), exprTrack=[[0, R], [0.8, 'joy'], [2.2, 'surprise']], talk=False), frames=90),
    'wave': dict(w=520, h=640, fps=30, set=dict(clip='wave', cam=FULL(0.35), exprTrack=[[0, 'joy']], talk=True, talkFrom=0.6, talkTo=2.4), frames=90),
    'stomp': dict(w=520, h=640, fps=30, set=dict(clip='stomp', cam=FULL(0.4), exprTrack=[[0, 'anger']], talk=False), frames=90),
    'dance': dict(w=520, h=640, fps=30, set=dict(clip='dance', cam=FULL(0.3), exprTrack=[[0, 'joy'], [2.5, R]], talk=False), frames=120),
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
                    '-pix_fmt', 'yuv420p', '-crf', '25', '-movflags', '+faststart', os.path.join(PICS, name + '.mp4')], check=True)


for name in (sys.argv[1:] or FILMS):
    run(name, FILMS[name]); print(name)
