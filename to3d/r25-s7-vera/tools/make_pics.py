"""The page's pictures (../pics), from the packs in the cache (build.py, bases.py), refs.py's sheets and compare.py's.
python3 make_pics.py [stills] [turn]"""
import os, sys, json, subprocess, shutil
import numpy as np
from PIL import Image
import config, drawing as D

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = config.CACHE
WORK = os.path.join(CACHE, 'pics'); os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
S7 = os.path.join(HERE, '..', '..', '..', 'styles', 's7-ghibli')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = CACHE.replace('/home/user', '') + '/out/'
W = config.WHO
WHAT = sys.argv[1:] or ['stills', 'turn']
PIECES = json.load(open(os.path.join(CACHE, 'out', W + '.json')))['pieces']


def shots(pack, w, h, shots, name):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PK + pack, w=w, h=h, shots=shots), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True, env=ENV, stdout=subprocess.DEVNULL)


def strip(names, out, scale=1.0, q=86):
    ims = [Image.open(os.path.join(WORK, n + '.png')).convert('RGB') for n in names]
    Wd = sum(i.width for i in ims); o = Image.new('RGB', (Wd, ims[0].height)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(PICS, out), quality=q)


HY = float(D.J['head'][1]) / 100                      # the head's middle, m
TOP = HY + D.B['head_h'] / 200 + 0.06
HC = dict(mode='ortho', h=0.40, pitch=0.0, target=[0, HY - 0.02, float(D.J['head'][2]) / 100])
HV = [('f', 0.0), ('q', -0.61), ('s', -1.5708)]
FC = dict(mode='ortho', h=TOP + 0.06, pitch=0.07, target=[0, TOP / 2 - 0.01, 0.0])
FV = [('f', 0.0), ('q', -0.61), ('s', -1.5708)]
ST = dict(pose='stand', still=True, exprTrack=[[0, 'calm']], time=2.0, linePx=2.3)

if 'stills' in WHAT:
    # the bases as they come
    shots('hbm-head.json', 400, 480, [dict(name='hb-' + v, set=dict(pose='raw', shadow=False, linePx=2.3, cam=dict(HC, yaw=y))) for v, y in HV], 'hb')
    strip(['hb-f', 'hb-q', 'hb-s'], 'step1-head-base.webp')
    shots('anny.json', 380, 820, [dict(name='an-' + v, set=dict(pose='raw', linePx=2.3, cam=dict(FC, yaw=y, h=1.75, target=[0, 0.82, 0]))) for v, y in FV], 'an')
    strip(['an-f', 'an-q', 'an-s'], 'step4-body-base.webp', 0.8)
    # the character: the head fitted, painted, with hair; what is kept of the body; the clothes; the whole; the back
    cl = [p for p in PIECES if p != 'hair']
    S = []
    S += [dict(name='hf-' + v, set=dict(ST, show=['head'], paint=False, shadow=False, cam=dict(HC, yaw=y))) for v, y in HV]
    S += [dict(name='hp-' + v, set=dict(ST, show=['head'], paint=True, cam=dict(HC, yaw=y))) for v, y in HV]
    S += [dict(name='hh-' + v, set=dict(ST, show=False, cam=dict(HC, yaw=y))) for v, y in HV + [('qb', 2.3), ('b', 3.1416)]]
    S += [dict(name='bk-' + v, set=dict(ST, show=['body', 'head'], shadow=True, cam=dict(FC, yaw=y))) for v, y in FV]
    S += [dict(name='bc-' + v, set=dict(ST, show=cl, cam=dict(FC, yaw=y))) for v, y in FV]
    S += [dict(name='bb-' + v, set=dict(ST, show=False, cam=dict(FC, yaw=y))) for v, y in [('qb', 2.4), ('b', 3.1416), ('r', 1.5708)]]
    EX = ['joy', 'surprise', 'sad', 'anger']
    ce = dict(mode='ortho', h=0.46, yaw=-0.384, pitch=0.07, target=[0, HY - 0.05, 0])
    S += [dict(name='e-' + e, set=dict(ST, exprTrack=[[0, e]], cam=ce)) for e in EX]
    S += [dict(name='ef-' + e, set=dict(ST, exprTrack=[[0, e]], cam=dict(ce, yaw=0))) for e in EX]
    S += [dict(name='portrait', set=dict(ST, cam=dict(mode='persp', dist=1.6, fov=22, yaw=-0.31, pitch=0.05, target=[0, HY - 0.08, 0])))]
    pick = lambda *pre: [x for x in S if x['name'].split('-')[0] in pre or x['name'] in pre]
    shots(W + '.json', 400, 480, pick('hf', 'hp', 'hh'), 'heads')
    strip(['hf-f', 'hf-q', 'hf-s'], 'step2-head-fitted.webp')
    strip(['hp-f', 'hp-q', 'hp-s'], 'step3-head-painted.webp')
    strip(['hh-f', 'hh-q', 'hh-s', 'hh-qb', 'hh-b'], 'head-hair.webp')
    shots(W + '.json', 380, 820, pick('bk', 'bc', 'bb'), 'figs')
    strip(['bk-f', 'bk-q', 'bk-s'], 'step5-body-kept.webp', 0.8)
    strip(['bc-f', 'bc-q', 'bc-s'], 'step6-clothes.webp', 0.8)
    strip(['bb-qb', 'bb-b', 'bb-r'], 'back.webp', 0.8)
    shots(W + '.json', 500, 620, pick('e', 'ef', 'portrait'), 'ex')
    strip(['e-' + e for e in EX], 'expr-three.webp')
    strip(['ef-' + e for e in EX], 'expr-front.webp')
    Image.open(os.path.join(WORK, 'portrait.png')).convert('RGB').save(os.path.join(PICS, 'portrait-3d.webp'), quality=88)
    Image.open(os.path.join(CACHE, 'refs', 'expr.png')).convert('RGB').save(os.path.join(PICS, 'expr-drawing.webp'), quality=86)
    Image.open(os.path.join(S7, 'pics', f'portrait-{W}.jpg')).convert('RGB').save(os.path.join(PICS, 'portrait-drawing.webp'), quality=86)
    Image.open(os.path.join(S7, 'pics', f'figure-{W}.jpg')).convert('RGB').save(os.path.join(PICS, 'figure-drawing.webp'), quality=86)
    for n in ('side', 'over'):
        im = Image.open(os.path.join(CACHE, 'cmp', n + '.png')).convert('RGB')
        im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(PICS, f'compare-{n}.webp'), quality=86)

if 'turn' in WHAT:
    d = os.path.join(WORK, 'turn'); shutil.rmtree(d, ignore_errors=True)
    sh = [dict(name='turn/f0000', set=dict(ST, show=False, cam=dict(FC, yaw=0)))]
    n = 72
    for k in range(1, n): sh.append(dict(name=f'turn/f{k:04d}', set=dict(cam=dict(FC, yaw=-2 * np.pi * k / n))))
    shots(W + '.json', 480, 860, sh, 'turn')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '20', '-i', os.path.join(d, 'f%04d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '26', '-movflags', '+faststart', os.path.join(PICS, 'turn.mp4')], check=True)
print('ok')
