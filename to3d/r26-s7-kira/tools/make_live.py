"""The live face and the Kimodo motions: films for the page (../pics). python3 make_live.py [name …]
Reads the pack from ../data (copy build.py's output there first)."""
import os, sys, json, subprocess, shutil
import config, drawing as D

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(config.CACHE, 'live'); os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = f'/works-010-art-direction/to3d/{config.FOLDER}/data/{config.WHO}.json'
HY = float(D.J['head'][1]) / 100
HEAD = dict(mode='ortho', h=0.42, yaw=-0.38, pitch=0.05, target=[0, HY - 0.03, 0])
# the camera follows the pelvis, near, so the character is big in the frame
FULL = lambda yaw, d=4.2: dict(mode='persp', dist=d, fov=24, yaw=yaw, pitch=0.08, cy=D.B['hip_y'] / 100 - 0.01, follow=True)
NEAR = lambda yaw: dict(mode='persp', dist=1.45, fov=22, yaw=yaw, pitch=0.03, focus='Head', up=0.07, follow=False)

FILMS = {
    'face-live': dict(w=480, h=540, fps=30, set=dict(pose='stand', clip=None, cam=HEAD, talk=True, talkFrom=2.0, talkTo=5.0, linePx=2.2,
                      exprTrack=[[0, 'calm'], [5.2, 'joy'], [6.9, 'surprise'], [8.4, 'sad'], [10.0, 'anger'],
                                 [11.6, {'calm': 0.5, 'surprise': 0.5}]]), time=(0, 13.2)),
    'idle-face': dict(w=480, h=540, fps=30, set=dict(clip='idle', cam=NEAR(-0.2), exprTrack=[[0, 'calm']], talk=False, linePx=2.2), frames=150),
}
for name, (clip, yaw, frames, track, talk) in config.MOTION_FILMS.items():
    FILMS[name] = dict(w=520, h=800, fps=30, frames=frames,
                       set=dict(clip=clip, cam=FULL(yaw), exprTrack=track, talk=bool(talk), **(dict(talkFrom=talk[0], talkTo=talk[1]) if talk else {})))


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
                    '-pix_fmt', 'yuv420p', '-crf', '27', '-movflags', '+faststart', os.path.join(PICS, name + '.mp4')], check=True)


for name in (sys.argv[1:] or FILMS):
    run(name, FILMS[name]); print(name, flush=True)
