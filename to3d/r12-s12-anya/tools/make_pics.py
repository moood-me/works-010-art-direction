"""The page's pictures and films (to3d/r12-s12-anya/pics), drawn by web/anya.js through shots.mjs.
  python3 make_pics.py [stills|films|<name>...]      (after form.py and build.py)
Films are drawn at 12 drawings a second (a drawing held for two frames of 24, as hand-drawn animation is)."""
import os, sys, json, subprocess, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = '/home/user/cache/to3d-r12-s12-anya/pics'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
STY = os.path.join(HERE, '..', '..', '..', 'styles', 's12-ink-watercolour', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PACK = '/works-010-art-direction/to3d/r12-s12-anya/data/anya.json'
want = sys.argv[1:] or ['stills', 'films']


def on(name, kind):
    return kind in want or name in want


def shots(w, h, sh, name):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PACK, w=w, h=h, shots=sh), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True, env=ENV)


def im(n):
    return Image.open(os.path.join(WORK, n + '.png')).convert('RGB')


def row(ims, out, scale=1.0, q=88):
    W = sum(i.width for i in ims); H = max(i.height for i in ims)
    o = Image.new('RGB', (W, H), (253, 250, 243)); x = 0
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


STAND = dict(pose='stand', poseOpts={'out': 0.06}, still=True, exprTrack=[[0, 'calm']], time=2, clip=None, flowers=False,
             flat=False, noWash=False, noLine=False)
FIG = dict(mode='ortho', h=2.24, cy=0.852, pitch=0, follow=False)          # the drawing's figure: 446 px a metre
BUST = dict(mode='ortho', h=0.695, cy=1.397, pitch=0, follow=False)        # the drawing's turnaround panels

if on('compare', 'stills'):
    # the figure as drawn: three-quarter, the head tilted and turned to her right, flowers at the chest
    pose = dict(STAND, poseOpts={'out': 0.06, 'hold': True, 'headTilt': 0.12, 'headTurn': -0.45}, flowers=True, exprTrack=[[0, 'dream']])
    shots(600, 1000, [dict(name='fig', set=dict(pose, cam=dict(FIG, yaw=0.6)))], 'fig')
    a, d = im('fig'), Image.open(os.path.join(STY, 'figure-anya.jpg')).convert('RGB').resize((600, 1000))
    row([d, a], 'compare-figure.jpg', 0.8)
    row([Image.blend(a, d, 0.5)], 'overlay-figure.jpg', 0.8)
    # the turnaround (head and shoulders): front, three-quarter, profile
    shots(500, 620, [dict(name='b' + k, set=dict(STAND, cam=dict(BUST, yaw=y))) for k, y in (('f', 0), ('q', 0.75), ('s', 1.5708))], 'bust')
    t = Image.open(os.path.join(STY, 'turn-anya.jpg')).convert('RGB').resize((1500, 620))
    ims = [im('bf'), im('bq'), im('bs')]
    o = Image.new('RGB', (1500, 620)); [o.paste(x, (i * 500, 0)) for i, x in enumerate(ims)]
    tall = Image.new('RGB', (1500, 1240)); tall.paste(t, (0, 0)); tall.paste(o, (0, 620))
    tall.resize((1050, 868), Image.LANCZOS).save(os.path.join(PICS, 'compare-turn.jpg'), quality=88)
    Image.blend(o, t, 0.5).resize((1050, 434), Image.LANCZOS).save(os.path.join(PICS, 'overlay-turn.jpg'), quality=88)

if on('steps', 'stills'):
    c = dict(FIG, yaw=0.6)
    S = dict(STAND, exprTrack=[[0, 'dream']])
    shots(600, 1000, [dict(name='s1', set=dict(S, flat=True, cam=c)), dict(name='s2', set=dict(S, noWash=True, cam=c)),
                      dict(name='s3', set=dict(S, noLine=True, cam=c)), dict(name='s4', set=dict(S, cam=c))], 'steps')
    row([im('s1'), im('s2'), im('s3'), im('s4')], 'steps-render.jpg', 0.6)
    # the back and sides, where there is no drawing
    shots(600, 1000, [dict(name='bk' + str(i), set=dict(S, cam=dict(FIG, yaw=y))) for i, y in enumerate((-0.8, 3.1416, 2.3))], 'back')
    row([im('bk0'), im('bk1'), im('bk2')], 'back.jpg', 0.6)

if on('expr', 'stills'):
    E = ['dream', 'joy', 'surprise', 'sad', 'anger']
    ce = dict(mode='ortho', h=0.40, cy=1.42, pitch=0, yaw=1.0, follow=False)
    shots(380, 420, [dict(name='e-' + e, set=dict(STAND, exprTrack=[[0, e]], cam=ce)) for e in E], 'expr')
    row([im('e-' + e) for e in E], 'expr-3d.jpg', 0.8)
    shutil.copy(os.path.join(STY, 'expr-anya.jpg'), os.path.join(PICS, 'expr-drawing.jpg'))

if on('turn', 'films'):
    film('turn', 480, 800, dict(STAND, cam=dict(FIG, h=1.95, cy=0.86, yaw=0)), 0, 47, 1, yaw=[0, 6.2832 * 47 / 48])
if on('walk', 'films'):
    film('walk', 540, 800, dict(STAND, still=False, clip='walk', exprTrack=[[0, 'calm']],
                                cam=dict(mode='persp', fov=22, dist=4.4, cy=0.86, follow=True, yaw=0.9, pitch=0.05)), 0, 117.5, 2.5)
if on('talk', 'films'):
    film('talk', 480, 540, dict(STAND, still=False, clip='idle', talk=True, talkFrom=0.4, exprTrack=[[0, 'calm'], [2.6, 'joy'], [3.8, 'calm']],
                                cam=dict(mode='persp', fov=22, dist=1.7, follow=False, focus='Head', up=-0.04, yaw=0.7, pitch=0.03)), 0, 147.5, 2.5)
if on('wave', 'films'):
    film('wave', 540, 800, dict(STAND, still=False, clip='wave', exprTrack=[[0, 'calm'], [0.6, 'joy']],
                                cam=dict(mode='persp', fov=22, dist=4.4, cy=0.9, follow=True, yaw=0.5, pitch=0.05)), 0, 87.5, 2.5)
print('ok')
