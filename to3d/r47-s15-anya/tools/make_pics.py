"""The page's pictures (to3d/r47-s15-anya/pics), from the packs in the cache.
python3 make_pics.py [stills] [turn]   (after build.py, bases.py, compare.py)"""
import os, sys, json, subprocess, shutil
import numpy as np
from PIL import Image
import drawing as D

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = '/home/user/cache/to3d-r47-s15-anya'
WORK = os.path.join(CACHE, 'pics'); os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
S15 = os.path.join(HERE, '..', '..', '..', 'styles', 's15-noir', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = '/cache/to3d-r47-s15-anya/out/'
want = sys.argv[1:] or ['stills', 'turn']


def shots(pack, w, h, shots, name):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PK + pack, w=w, h=h, shots=shots), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True, env=ENV, stdout=subprocess.DEVNULL)


def strip(names, out, scale=1.0, q=88, gap=6):
    ims = [Image.open(os.path.join(WORK, n + '.png')).convert('RGB') for n in names]
    W = sum(i.width for i in ims) + gap * (len(ims) - 1); o = Image.new('RGB', (W, ims[0].height), '#11121b'); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width + gap
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(PICS, out), quality=q)


HY = (D.FLOOR - 30) * D.K                     # the head's middle
V3 = [('f', 0.0), ('q', 0.6), ('s', 1.5708)]
if 'stills' in want:
    # ---- the head: the base as it comes, fitted with the drawn planes, with the look and the drawn face
    W, H = 440, 520
    hc = lambda y: dict(mode='ortho', h=0.52, yaw=y, pitch=0, target=[0, HY, 0], follow=False)
    disc = dict(kind='disc', w=0.46, y=HY, x=0)
    shots('hbm-head.json', W, H, [dict(name='hb-' + v, set=dict(pose='raw', flat=True, paint=False, back=disc, floor=False, cam=hc(y))) for v, y in V3], 'hb')
    strip(['hb-f', 'hb-q', 'hb-s'], 'step1-head-base.jpg')
    S = dict(pose='stand', poseOpts={'out': 0.08}, still=True, exprTrack=[[0, 'calm']], time=2.0, floor=False)
    shots('anya.json', W, H, [dict(name='hf-' + v, set=dict(S, show=['head'], flat=True, paint=False, back=disc, cam=hc(y))) for v, y in V3] +
          [dict(name='hp-' + v, set=dict(S, show=['head'], flat=False, paint=True, back=disc, cam=hc(y))) for v, y in V3] +
          [dict(name='hh-' + v, set=dict(S, show=['head', 'hair', 'dress', 'cardigan'], flat=False, paint=True, back=disc, cam=hc(y))) for v, y in V3], 'hf')
    strip(['hf-f', 'hf-q', 'hf-s'], 'step2-head-fitted.jpg')
    strip(['hp-f', 'hp-q', 'hp-s'], 'step3-head-look.jpg')
    strip(['hh-f', 'hh-q', 'hh-s'], 'step4-head-hair.jpg')
    # ---- the body: Anny as it comes; the form alone; the look; from behind
    bw, bh = 400, 860
    bc = lambda y: dict(mode='ortho', h=1.82, yaw=y, pitch=0, target=[0, 0.86, 0], follow=False)
    win = dict(kind='window', w=0.7, h=1.7, y=0.9, x=0)
    shots('anny.json', bw, bh, [dict(name='an-' + v, set=dict(pose='raw', flat=True, paint=False, back=win, floor=False, cam=bc(y))) for v, y in V3], 'an')
    strip(['an-f', 'an-q', 'an-s'], 'step5-body-base.jpg', scale=0.8)
    shots('anya.json', bw, bh, [dict(name='bf-' + v, set=dict(S, show=None, flat=True, paint=False, back=win, cam=bc(y))) for v, y in V3] +
          [dict(name='bl-' + v, set=dict(S, flat=False, paint=True, back=win, cam=bc(y))) for v, y in V3] +
          [dict(name='bb-' + v, set=dict(S, cam=bc(y))) for v, y in [('qb', -2.4), ('b', 3.1416), ('r', -1.5708)]], 'bk')
    strip(['bf-f', 'bf-q', 'bf-s'], 'step6-form.jpg', scale=0.8)
    strip(['bl-f', 'bl-q', 'bl-s'], 'step7-look.jpg', scale=0.8)
    strip(['bb-qb', 'bb-b', 'bb-r'], 'back.jpg', scale=0.8)
    # ---- the light: the same pose, the key moved — the black shapes stand on the drawn edges
    LS = [('l1', [-0.62, 0.5, 0.6]), ('l2', [-0.95, 0.3, 0.1]), ('l3', [0.0, 0.75, 0.65]), ('l4', [0.62, 0.5, 0.6]), ('l5', [-0.5, 0.3, -0.8])]
    pc = dict(mode='ortho', h=0.9, yaw=0.45, pitch=0, target=[0, 1.26, 0], follow=False)
    shots('anya.json', 420, 520, [dict(name=n, set=dict(S, light=l, back=dict(kind='disc', w=0.62, y=1.4, x=0.02), cam=pc)) for n, l in LS], 'ls')
    strip([n for n, _ in LS], 'light.jpg')
    # ---- expressions: the drawing's sheet, the 3D in three-quarter and in front
    E = ['joy', 'surprise', 'sad', 'anger']
    ce = dict(mode='ortho', h=0.62, yaw=0.6, pitch=0.0, target=[0, HY - 0.05, 0], follow=False)
    bd = dict(kind='disc', w=0.5, y=HY, x=0.02)
    shots('anya.json', 440, 540, [dict(name='e-' + e, set=dict(S, light=[-0.62, 0.5, 0.6], back=bd, exprTrack=[[0, e]], time=2.0, cam=ce)) for e in E] +
          [dict(name='ef-' + e, set=dict(exprTrack=[[0, e]], time=2.0, cam=dict(ce, yaw=0))) for e in E], 'ex')
    strip(['e-' + e for e in E], 'expr-three.jpg')
    strip(['ef-' + e for e in E], 'expr-front.jpg')
    Image.open(os.path.join(S15, 'expr-anya.png')).convert('RGB').resize((1780, 623), Image.LANCZOS).save(os.path.join(PICS, 'expr-drawing.jpg'), quality=88)
    # ---- the drawing and the 3D (compare.py's pictures)
    for n, o, k in (('turn-side', 'compare-turn', 0.85), ('turn-over', 'overlay-turn', 0.85), ('figure-side', 'compare-figure', 0.85), ('figure-over', 'overlay-figure', 0.7)):
        im = Image.open(os.path.join(CACHE, 'cmp', n + '.png')).convert('RGB')
        im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS).save(os.path.join(PICS, o + '.jpg'), quality=88)

if 'turn' in want:
    d = os.path.join(WORK, 'turn'); shutil.rmtree(d, ignore_errors=True)
    n = 72
    S = dict(pose='stand', poseOpts={'out': 0.08}, exprTrack=[[0, 'calm']], floor=True, back=dict(kind='window', w=0.72, h=1.8, y=0.96, x=0.03))
    sh = [dict(name=f'turn/f{k:04d}', set=dict(S if k == 0 else {}, time=k / 24,
               cam=dict(mode='persp', fov=18, dist=6.4, yaw=0.6 + 2 * np.pi * k / n, pitch=0.045, target=[0, 0.84, 0], follow=False))) for k in range(n)]
    os.makedirs(d)
    shots('anya.json', 520, 860, sh, 'turn')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '18', '-i', os.path.join(d, 'f%04d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '23', '-movflags', '+faststart', os.path.join(PICS, 'turn.mp4')], check=True)
print('ok')
