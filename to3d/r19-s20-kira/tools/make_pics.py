"""The page's pictures and films (to3d/r19-s20-kira/pics), drawn by web/kira.js through shots.mjs.
  python3 make_pics.py [stills|films|<name>...]      (after build.py)
Films are drawn at 12 drawings a second (a drawing held for two frames of 24, as hand-drawn animation is)."""
import os, sys, json, subprocess, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = '/home/user/cache/to3d-r19-s20-kira/pics'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
STY = os.path.join(HERE, '..', '..', '..', 'styles', 's20-soviet', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PACK = '/works-010-art-direction/to3d/r19-s20-kira/data/kira.json'
K = 1.60 / 428
want = sys.argv[1:] or ['stills', 'films']
on = lambda name, kind: kind in want or name in want


def shots(w, h, sh, name):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PACK, w=w, h=h, shots=sh), open(j, 'w'))
    subprocess.run(['flock', '/home/user/cache/heavy.%d.lock' % (os.getpid() % 3), 'node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True, env=ENV)


im = lambda n: Image.open(os.path.join(WORK, n + '.png')).convert('RGB')
sty = lambda n: Image.open(os.path.join(STY, n + '.webp')).convert('RGB')


def row(ims, out, scale=1.0, q=88):
    W = sum(i.width for i in ims); H = max(i.height for i in ims)
    o = Image.new('RGB', (W, H), (201, 193, 154)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(PICS, out), quality=q)


def film(name, w, h, set_, frm, to, step, yaw=None):
    d = os.path.join(WORK, name); shutil.rmtree(d, ignore_errors=True)
    if not set_.get('still'): set_ = {k: v for k, v in set_.items() if k != 'time'}       # the face's clock: the clip's
    shots(w, h, [dict(name=name, set=set_, film={'from': frm, 'to': to, 'step': step, **({'yaw': yaw} if yaw else {})})], name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '12', '-i', os.path.join(d, 'f%04d.png'), '-r', '24',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '25', '-movflags', '+faststart',
                    os.path.join(PICS, name + '.mp4')], check=True)


STAND = dict(pose='stand', still=True, exprTrack=[[0, 'calm']], time=2, clip=None, flat=False, noPaint=False, noLine=False)
# the drawing's sheets: turn — 720/460 points a unit, the floor at 840 of 950; figure — 860/450, the floor at 990 of 1100
TURN = dict(mode='ortho', h=950 / (720 / 460 / K), cy=(840 - 475) / (720 / 460 / K), pitch=0, follow=False)
FIG = dict(mode='ortho', h=1100 / (860 / 450 / K), cy=(990 - 550) / (860 / 450 / K), pitch=0, follow=False)

if on('compare', 'stills'):
    shots(490, 950, [dict(name='t' + k, set=dict(STAND, cam=dict(TURN, yaw=y))) for k, y in (('f', 0), ('q', -0.5), ('s', -1.5708))], 'turn')
    t = sty('turn-kira')
    o = Image.new('RGB', (1470, 950)); [o.paste(im('t' + k), (i * 490, 0)) for i, k in enumerate('fqs')]
    tc = t.crop((15, 0, 1485, 950))
    tall = Image.new('RGB', (1470, 1900)); tall.paste(tc, (0, 0)); tall.paste(o, (0, 950))
    tall.resize((1030, 1331), Image.LANCZOS).save(os.path.join(PICS, 'compare-turn.jpg'), quality=88)
    Image.blend(o, tc, 0.5).resize((1176, 760), Image.LANCZOS).save(os.path.join(PICS, 'overlay-turn.jpg'), quality=88)
    shots(900, 1100, [dict(name='fig', set=dict(STAND, pose='act', cam=dict(FIG, yaw=-0.5)))], 'fig')
    a, d = im('fig'), sty('figure-kira')
    row([d, a], 'compare-figure.jpg', 0.7)
    row([Image.blend(a, d, 0.5)], 'overlay-figure.jpg', 0.7)

if on('steps', 'stills'):
    c = dict(TURN, yaw=-0.5)
    shots(490, 950, [dict(name='s1', set=dict(STAND, flat=True, cam=c)), dict(name='s2', set=dict(STAND, noLine=True, cam=c)),
                     dict(name='s3', set=dict(STAND, noPaint=True, cam=c)), dict(name='s4', set=dict(STAND, cam=c))], 'steps')
    row([im('s1'), im('s2'), im('s3'), im('s4')], 'steps-render.jpg', 0.7)
    shots(490, 950, [dict(name='bk' + str(i), set=dict(STAND, cam=dict(TURN, yaw=y))) for i, y in enumerate((0.9, 3.1416, -2.3))], 'back')
    row([im('bk0'), im('bk1'), im('bk2')], 'back.jpg', 0.7)

if on('expr', 'stills'):
    E = ['joy', 'surprise', 'sadness', 'anger']
    ce = dict(mode='ortho', h=0.56, cy=1.335, pitch=0, yaw=-0.42, follow=False)
    shots(400, 440, [dict(name='e-' + e, set=dict(STAND, exprTrack=[[0, e]], cam=ce)) for e in E], 'expr')
    row([im('e-' + e) for e in E], 'expr-3d.jpg', 0.8)
    sty('expr-kira').resize((1280, 448), Image.LANCZOS).save(os.path.join(PICS, 'expr-drawing.jpg'), quality=88)

FOLLOW = dict(mode='persp', fov=22, dist=4.5, cy=0.8, follow=True, pitch=0.05)
if on('turn', 'films'):
    film('turn', 480, 800, dict(STAND, cam=dict(TURN, h=1.9, cy=0.82, yaw=0)), 0, 47, 1, yaw=[0, -6.2832 * 47 / 48])
if on('walk', 'films'):
    film('walk', 540, 800, dict(STAND, still=False, clip='walk', cam=dict(FOLLOW, yaw=-0.9)), 0, 117.5, 2.5)
if on('sneak', 'films'):
    film('sneak', 540, 800, dict(STAND, still=False, clip='sneak', exprTrack=[[0, 'calm'], [1.2, 'anger']], cam=dict(FOLLOW, yaw=-1.1)), 0, 117.5, 2.5)
if on('talk', 'films'):       # standing (Kimodo's idle bows the head into the hood): the face alone is alive
    d = os.path.join(WORK, 'talk'); shutil.rmtree(d, ignore_errors=True)
    set_ = dict(pose='stand', still=False, clip=None, talk=True, talkFrom=0.4, exprTrack=[[0, 'calm'], [1.8, 'surprise'], [2.8, 'joy'], [3.6, 'anger'], [4.6, 'calm']],
                cam=dict(mode='ortho', h=0.62, cy=1.31, yaw=-0.42, pitch=0, follow=False, focus=None))
    shots(520, 560, [dict(name='talk', set=set_, film={'from': 0, 'to': 177.5, 'step': 2.5, 'clock': 30})], 'talk')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '12', '-i', os.path.join(d, 'f%04d.png'), '-r', '24',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '25', '-movflags', '+faststart', os.path.join(PICS, 'talk.mp4')], check=True)
print('ok')
