"""The live face and the motions: films for the page (../pics). python3 make_live.py [name …]
Reads the pack from ../data (copy it there from the cache first)."""
import os, sys, json, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER, NAME = 'r18-s3-kira', 'kira'
WORK = f'/home/user/cache/to3d-{FOLDER}/live'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = f'/works-010-art-direction/to3d/{FOLDER}/data/{NAME}.json'
STAND = dict(pose='stand', poseOpts={'out': 0.03})
HEAD = dict(mode='ortho', h=0.5, cy=1.39, yaw=-0.45, pitch=0.0, target=[0, 1.39, 0.04])
FULL = lambda yaw, **k: dict(dict(mode='persp', dist=5.5, fov=22, yaw=yaw, pitch=0.06, cy=0.8, follow=True), **k)
NEAR = lambda yaw: dict(mode='persp', dist=1.9, fov=22, yaw=yaw, pitch=0.03, focus='Head', up=0.11, follow=False)
R = 'sulk'

FILMS = {
    # the face alone: calm (blinks, saccades), a few words through her teeth, the sheet's expressions one into another, a mix
    'face-live': dict(w=480, h=480, fps=30, set=dict(STAND, clip=None, cam=HEAD, talk=True, talkFrom=2.0, talkTo=4.6,
                      exprTrack=[[0, R], [5.2, 'smirk'], [6.9, 'surprise'], [8.4, 'sad'], [10.0, 'anger'],
                                 [11.6, {'sulk': 0.5, 'smirk': 0.5}]]), time=(0, 13.2)),
    'idle-face': dict(w=480, h=480, fps=30, set=dict(clip='idle', cam=NEAR(0.2), exprTrack=[[0, R]], talk=False), frames=150),
    'idle': dict(w=480, h=700, fps=30, set=dict(clip='idle', cam=FULL(0.3), exprTrack=[[0, R], [3.0, 'smirk']], talk=False), frames=150),
    'walk': dict(w=520, h=700, fps=30, set=dict(clip='walk', cam=FULL(0.75), exprTrack=[[0, R]], talk=False), frames=120),
    'walk-side': dict(w=520, h=700, fps=30, set=dict(clip='walk', cam=FULL(1.5708), exprTrack=[[0, R]], talk=False), frames=120),
    'sneak': dict(w=520, h=700, fps=30, set=dict(clip='sneak', cam=FULL(0.9), exprTrack=[[0, R], [1.5, 'surprise'], [3.0, R]], talk=False), frames=120),
    'sit': dict(w=520, h=700, fps=30, set=dict(clip='sit', cam=FULL(0.9, cy=0.6), exprTrack=[[0, R], [2.4, 'sad']], talk=False), frames=120),
    'stomp': dict(w=520, h=700, fps=30, set=dict(clip='stomp', cam=FULL(0.4), exprTrack=[[0, 'anger']], talk=False), frames=90),
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
