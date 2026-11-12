"""The live face and motions: films for the page (to3d/r47-s15-anya/pics). python3 make_live.py [name …]"""
import os, sys, json, subprocess, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = '/home/user/cache/to3d-r47-s15-anya/live'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = '/works-010-art-direction/to3d/r47-s15-anya/data/anya.json'
STAND = dict(pose='stand', poseOpts={'out': 0.08})
WIN = dict(kind='window', w=0.9, h=1.9, y=1.0, x=0.08)
DISC = dict(kind='disc', w=0.56, x=0.02)
HEAD = dict(mode='ortho', h=0.56, yaw=0.5, pitch=0.0, focus='Head', up=0.0, follow=False)
FULL = lambda yaw: dict(mode='persp', dist=6.0, fov=22, yaw=yaw, pitch=0.06, cy=0.86, follow=True, focus=None)
NEAR = lambda yaw: dict(mode='persp', dist=1.9, fov=22, yaw=yaw, pitch=0.03, focus='Head', up=-0.02, follow=False)

# 24 pictures a second; a clip's own frames are 30 a second
FILMS = {
    # the face alone: calm (blinks, saccades), talking, the sheet's expressions one into another, a mix
    'face-live': dict(w=520, h=560, set=dict(STAND, clip=None, cam=HEAD, back=DISC, floor=False, talk=True, talkFrom=2.0, talkTo=5.0,
                      exprTrack=[[0, 'calm'], [5.2, 'joy'], [6.9, 'surprise'], [8.4, 'sad'], [10.0, 'anger'],
                                 [11.6, {'joy': 0.5, 'surprise': 0.5}]]), time=(0, 13.0)),
    'walk': dict(w=600, h=860, set=dict(clip='walk', cam=FULL(0.8), back=WIN, floor=True, exprTrack=[[0, 'calm'], [2.0, 'joy']], talk=False), secs=4.0),
    'wave': dict(w=600, h=860, set=dict(clip='wave', cam=FULL(0.45), back=WIN, floor=True, exprTrack=[[0, 'joy']], talk=True, talkFrom=0.6, talkTo=2.4), secs=3.0),
    # looking round (Kimodo's idle): the eyes lead the head, blinks with the turns; the black shapes turn with the head
    'idle-face': dict(w=520, h=560, set=dict(clip='idle', cam=NEAR(0.35), back=DISC, floor=False, exprTrack=[[0, 'calm']], talk=False), secs=5.0),
    'sneak': dict(w=600, h=860, set=dict(clip='sneak', cam=FULL(0.9), back=WIN, floor=True, exprTrack=[[0, 'surprise'], [1.5, 'anger']], talk=False), secs=4.0),
    'sit': dict(w=600, h=860, set=dict(clip='sit', cam=dict(FULL(0.9), cy=0.66), back=WIN, floor=True, exprTrack=[[0, 'calm'], [2.4, 'sad']], talk=False), secs=4.0),
}


def run(name, f):
    d = os.path.join(WORK, name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    shots = []
    if 'time' in f:
        t0, t1 = f['time']; n = int((t1 - t0) * 24)
        shots.append(dict(name=f'{name}/f0000', set=dict(f['set'], time=t0)))
        for k in range(1, n): shots.append(dict(name=f'{name}/f{k:04d}', set=dict(time=t0 + k / 24)))
    else:
        n = int(f['secs'] * 24)
        shots.append(dict(name=f'{name}/f0000', set=dict(f['set'], t=0)))
        for k in range(1, n): shots.append(dict(name=f'{name}/f{k:04d}', set=dict(t=k * 30 / 24)))
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PK, w=f['w'], h=f['h'], shots=shots), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True, env=ENV, stdout=subprocess.DEVNULL)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(d, 'f%04d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', os.path.join(PICS, name + '.mp4')], check=True)


for name in (sys.argv[1:] or FILMS):
    run(name, FILMS[name]); print(name)
