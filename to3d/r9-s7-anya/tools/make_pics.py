"""The page's pictures (to3d/r9-s7-anya/pics), from the packs in the cache (build.py, bases.py) and compare.py's.
python3 make_pics.py [stills|turn]"""
import os, sys, json, subprocess, shutil
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = '/home/user/cache/to3d-r9-s7-anya'
WORK = os.path.join(CACHE, 'pics'); os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
S7 = os.path.join(HERE, '..', '..', '..', 'styles', 's7-ghibli')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = '/cache/to3d-r9-s7-anya/out/'
WHAT = sys.argv[1:] or ['stills', 'turn']


def shots(pack, w, h, shots, name):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PK + pack, w=w, h=h, shots=shots), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True, env=ENV, stdout=subprocess.DEVNULL)


def strip(names, out, scale=1.0, q=86):
    ims = [Image.open(os.path.join(WORK, n + '.png')).convert('RGB') for n in names]
    W = sum(i.width for i in ims); o = Image.new('RGB', (W, ims[0].height)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(PICS, out), quality=q)


HC = dict(mode='ortho', h=0.40, pitch=0.0, target=[0, 1.50, 0.0])
HV = [('f', 0.0), ('q', -0.61), ('s', -1.5708)]
FC = dict(mode='ortho', h=1.80, pitch=0.07, target=[0, 0.86, 0.0])
FV = [('f', 0.0), ('q', -0.61), ('s', -1.5708)]
ST = dict(pose='stand', still=True, exprTrack=[[0, 'calm']], time=2.0)

if 'stills' in WHAT:
    # the bases as they come
    shots('hbm-head.json', 400, 480, [dict(name='hb-' + v, set=dict(pose='raw', shadow=False, cam=dict(HC, yaw=y))) for v, y in HV], 'hb')
    strip(['hb-f', 'hb-q', 'hb-s'], 'step1-head-base.webp')
    shots('anny.json', 380, 820, [dict(name='an-' + v, set=dict(pose='raw', cam=dict(FC, yaw=y, h=1.75, target=[0, 0.82, 0]))) for v, y in FV], 'an')
    strip(['an-f', 'an-q', 'an-s'], 'step4-body-base.webp', 0.8)
    # Аня: the head fitted, painted, with hair; the body kept; the clothes; the whole; the back; the expressions
    cl = ['body', 'head', 'skin', 'skirt', 'top', 'cardigan', 'sleeveLeft', 'sleeveRight', 'shoeLeft', 'shoeRight', 'lines']
    S = []
    S += [dict(name='hf-' + v, set=dict(ST, show=['head'], paint=False, shadow=False, cam=dict(HC, yaw=y))) for v, y in HV]
    S += [dict(name='hp-' + v, set=dict(ST, show=['head'], paint=True, cam=dict(HC, yaw=y))) for v, y in HV]
    S += [dict(name='hh-' + v, set=dict(ST, show=False, cam=dict(HC, yaw=y))) for v, y in HV + [('b', 3.1416), ('qb', 2.3)]]
    S += [dict(name='bk-' + v, set=dict(ST, show=['body', 'head', 'skin'], shadow=True, cam=dict(FC, yaw=y))) for v, y in FV]
    S += [dict(name='bc-' + v, set=dict(ST, show=cl, cam=dict(FC, yaw=y))) for v, y in FV]
    S += [dict(name='bb-' + v, set=dict(ST, show=False, cam=dict(FC, yaw=y))) for v, y in [('qb', 2.4), ('b', 3.1416), ('r', 1.5708)]]
    EX = ['joy', 'surprise', 'sad', 'anger']
    ce = dict(mode='ortho', h=0.46, yaw=-0.384, pitch=0.07, target=[0, 1.45, 0])
    S += [dict(name='e-' + e, set=dict(ST, exprTrack=[[0, e]], cam=ce)) for e in EX]
    S += [dict(name='ef-' + e, set=dict(ST, exprTrack=[[0, e]], cam=dict(ce, yaw=0))) for e in EX]
    S += [dict(name='portrait', set=dict(ST, exprTrack=[[0, 'dream']], cam=dict(mode='persp', dist=1.6, fov=22, yaw=-0.31, pitch=0.05, target=[0, 1.42, 0])))]
    shots('anya.json', 400, 480, S[:3 * 3 + 5], 'heads')
    strip(['hf-f', 'hf-q', 'hf-s'], 'step2-head-fitted.webp')
    strip(['hp-f', 'hp-q', 'hp-s'], 'step3-head-painted.webp')
    strip(['hh-f', 'hh-q', 'hh-s', 'hh-qb', 'hh-b'], 'head-hair.webp')
    shots('anya.json', 380, 820, S[14:14 + 9], 'figs')
    strip(['bk-f', 'bk-q', 'bk-s'], 'step5-body-kept.webp', 0.8)
    strip(['bc-f', 'bc-q', 'bc-s'], 'step6-clothes.webp', 0.8)
    strip(['bb-qb', 'bb-b', 'bb-r'], 'back.webp', 0.8)
    shots('anya.json', 500, 620, S[23:], 'ex')
    strip(['e-' + e for e in EX], 'expr-three.webp')
    strip(['ef-' + e for e in EX], 'expr-front.webp')
    Image.open(os.path.join(WORK, 'portrait.png')).convert('RGB').save(os.path.join(PICS, 'portrait-3d.webp'), quality=88)
    Image.open(os.path.join(S7, 'pics', 'expr-anya.jpg')).convert('RGB').save(os.path.join(PICS, 'expr-drawing.webp'), quality=86)
    Image.open(os.path.join(S7, 'pics', 'portrait-anya.jpg')).convert('RGB').save(os.path.join(PICS, 'portrait-drawing.webp'), quality=86)
    for n in ('side', 'over'):
        im = Image.open(os.path.join(CACHE, 'cmp', n + '.png')).convert('RGB')
        im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(PICS, f'compare-{n}.webp'), quality=86)

if 'turn' in WHAT:
    d = os.path.join(WORK, 'turn'); shutil.rmtree(d, ignore_errors=True)
    sh = [dict(name='turn/f0000', set=dict(ST, show=False, cam=dict(FC, yaw=0)))]
    n = 90
    for k in range(1, n): sh.append(dict(name=f'turn/f{k:04d}', set=dict(cam=dict(FC, yaw=-2 * np.pi * k / n))))
    shots('anya.json', 480, 860, sh, 'turn')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(d, 'f%04d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '26', '-movflags', '+faststart', os.path.join(PICS, 'turn.mp4')], check=True)
print('ok')
