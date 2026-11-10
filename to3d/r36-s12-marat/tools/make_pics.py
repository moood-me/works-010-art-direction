"""The page's pictures and films (../pics), drawn by web/figure.js through shots.mjs.
  python3 make_pics.py [stills|films|<name>...]      (after build.py)
Films are drawn at 12 drawings a second (a drawing held for two frames of 24, as hand-drawn animation is)."""
import os, sys, json, subprocess, shutil
from PIL import Image
import drawing as D

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = 'marat'
FOLDER = os.path.basename(os.path.dirname(HERE))
WORK = f'/home/user/cache/to3d-{FOLDER}/pics'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
STY = os.path.join(HERE, '..', '..', '..', 'styles', 's12-ink-watercolour', 'pics')
PACK = f'/works-010-art-direction/to3d/{FOLDER}/data/{NAME}.json'
want = sys.argv[1:] or ['stills', 'films']
PAPER = (253, 250, 243)


def on(name, kind):
    return kind in want or name in want


def shots(w, h, sh, name):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PACK, w=w, h=h, shots=sh), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True)


def im(n):
    return Image.open(os.path.join(WORK, n + '.png')).convert('RGB')


def row(ims, out, scale=1.0, q=88):
    W = sum(i.width for i in ims); H = max(i.height for i in ims)
    o = Image.new('RGB', (W, H), PAPER); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(PICS, out), quality=q)


def film(name, w, h, set_, frm, to, step, yaw=None, crf=25):
    d = os.path.join(WORK, name); shutil.rmtree(d, ignore_errors=True)
    if not set_.get('still'): set_ = {k: v for k, v in set_.items() if k != 'time'}       # the face's clock: the clip's
    shots(w, h, [dict(name=name, set=set_, film={'from': frm, 'to': to, 'step': step, **({'yaw': yaw} if yaw else {})})], name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '12', '-i', os.path.join(d, 'f%04d.png'), '-r', '24',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', str(crf), '-movflags', '+faststart',
                    os.path.join(PICS, name + '.mp4')], check=True)


REST = 'merry'
STAND = dict(pose='stand', poseOpts={}, still=True, exprTrack=[[0, REST]], time=2, clip=None, props=None,
             flat=False, noWash=False, noLine=False)
# the drawing's own scales: the figure sheet is 0.72 px a head unit, soles at y 880 of 1000; the turnaround's panels
# 0.86 px a unit, the eye line at y 228 of 620
FIG = dict(mode='ortho', h=1000 / 0.72 * D.K, cy=(500 - 120) / 0.72 * D.K, pitch=0, follow=False)
BUST = dict(mode='ortho', h=620 / 0.86 * D.K, cy=(D.FLOOR - 82 / 0.86) * D.K, pitch=0, follow=False)
# the figure as drawn: he laughs with the whole body — leaning back, the head thrown back, one arm raised like a toast
# (the drawing's ladle is not made), the other fist on the hip
LAUGH = dict(lean=-0.13, headNod=-0.12, headTurn=0.1,
             arms={'Right': {'upper': [-0.85, 0.12, 0.35], 'fore': [-0.12, 1, 0.12]}, 'Left': {'upper': [0.85, -0.62, -0.2], 'fore': [-0.55, -0.62, 0.45]}})

if on('compare', 'stills'):
    shots(600, 1000, [dict(name='fig', set=dict(STAND, poseOpts=LAUGH, exprTrack=[[0, 'joy']], cam=dict(FIG, yaw=0.7)))], 'fig')
    a, d = im('fig'), Image.open(os.path.join(STY, f'figure-{NAME}.jpg')).convert('RGB').resize((600, 1000))
    row([d, a], 'compare-figure.jpg', 0.8)
    row([Image.blend(a, d, 0.5)], 'overlay-figure.jpg', 0.8)
    shots(500, 620, [dict(name='b' + k, set=dict(STAND, cam=dict(BUST, yaw=y))) for k, y in (('f', 0), ('q', 0.75), ('s', 1.5708))], 'bust')
    t = Image.open(os.path.join(STY, f'turn-{NAME}.jpg')).convert('RGB').resize((1500, 620))
    ims = [im('bf'), im('bq'), im('bs')]
    o = Image.new('RGB', (1500, 620)); [o.paste(x, (i * 500, 0)) for i, x in enumerate(ims)]
    tall = Image.new('RGB', (1500, 1240)); tall.paste(t, (0, 0)); tall.paste(o, (0, 620))
    tall.resize((1050, 868), Image.LANCZOS).save(os.path.join(PICS, 'compare-turn.jpg'), quality=88)
    Image.blend(o, t, 0.5).resize((1050, 434), Image.LANCZOS).save(os.path.join(PICS, 'overlay-turn.jpg'), quality=88)

if on('steps', 'stills'):
    c = dict(FIG, yaw=0.6)
    shots(600, 1000, [dict(name='s1', set=dict(STAND, flat=True, cam=c)), dict(name='s2', set=dict(STAND, noWash=True, cam=c)),
                      dict(name='s3', set=dict(STAND, noLine=True, cam=c)), dict(name='s4', set=dict(STAND, cam=c))], 'steps')
    row([im('s1'), im('s2'), im('s3'), im('s4')], 'steps-render.jpg', 0.6)
    shots(600, 1000, [dict(name='bk' + str(i), set=dict(STAND, cam=dict(FIG, yaw=y))) for i, y in enumerate((-0.8, 3.1416, 2.3))], 'back')
    row([im('bk0'), im('bk1'), im('bk2')], 'back.jpg', 0.6)

if on('expr', 'stills'):
    E = [REST, 'joy', 'surprise', 'sad', 'anger']
    ce = dict(mode='ortho', h=0.66, cy=1.615, pitch=0, yaw=0.5, follow=False)
    shots(380, 420, [dict(name='e-' + e, set=dict(STAND, exprTrack=[[0, e]], cam=ce)) for e in E], 'expr')
    row([im('e-' + e) for e in E], 'expr-3d.jpg', 0.8)
    Image.open(os.path.join(STY, f'expr-{NAME}.jpg')).convert('RGB').resize((1200, 375), Image.LANCZOS).save(os.path.join(PICS, 'expr-drawing.jpg'), quality=88)

if on('turn', 'films'):
    film('turn', 480, 720, dict(STAND, cam=dict(FIG, h=2.25, cy=1.0, yaw=0)), 0, 47, 1, yaw=[0, 6.2832 * 47 / 48])
if on('walk', 'films'):
    film('walk', 520, 720, dict(STAND, still=False, clip='walk', cam=dict(mode='persp', fov=22, dist=5.6, cy=0.98, follow=True, yaw=0.9, pitch=0.05)), 0, 117.5, 2.5)
if on('wave', 'films'):
    film('wave', 560, 720, dict(STAND, still=False, clip='wave', exprTrack=[[0, REST], [0.6, 'joy'], [2.4, REST]],
                                cam=dict(mode='persp', fov=22, dist=5.9, cy=1.05, follow=True, yaw=0.45, pitch=0.05)), 0, 87.5, 2.5)
if on('stomp', 'films'):
    film('stomp', 520, 720, dict(STAND, still=False, clip='stomp', exprTrack=[[0, REST], [0.8, 'anger'], [2.4, REST]],
                                 cam=dict(mode='persp', fov=22, dist=5.6, cy=0.98, follow=True, yaw=-0.6, pitch=0.05)), 0, 87.5, 2.5)
if on('talk', 'films'):
    film('talk', 480, 520, dict(STAND, still=False, clip='idle', talk=True, talkFrom=0.4, talkTo=3.0, exprTrack=[[0, REST], [3.0, 'joy'], [4.4, REST]],
                                cam=dict(mode='persp', fov=22, dist=2.3, follow=False, focus='Head', up=0.04, yaw=0.6, pitch=0.03)), 0, 147.5, 2.5)
print('ok')
