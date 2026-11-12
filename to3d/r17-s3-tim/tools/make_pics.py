"""All the page's still pictures and the turn (../pics), from the packs in the cache.
python3 make_pics.py  (after build.py, bases.py, compare.py)"""
import os, json, subprocess, shutil
import numpy as np
from PIL import Image
import drawing as D, overlay as O, views as VW

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = 'tim'
CACHE = '/home/user/cache/to3d-r17-s3-tim'
WORK = os.path.join(CACHE, 'pics'); os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = '/cache/to3d-r17-s3-tim/out/'
S3 = os.path.join(HERE, '..', '..', '..', 'styles', 's3-graphic')


def shots(pack, w, h, shots, name):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PK + pack, w=w, h=h, shots=shots), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True, env=ENV, stdout=subprocess.DEVNULL)


def strip(names, out, outline=None, box=None, scale=1.0, q=88):
    ims = [Image.open(os.path.join(WORK, n + '.png')).convert('RGB') for n in names]
    if outline:
        ims = [O.outline(im, sh, box, col=(40, 120, 200), w=2) if sh else im for im, sh in zip(ims, outline)]
    W = sum(i.width for i in ims); o = Image.new('RGB', (W, ims[0].height)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(PICS, out), quality=q)


# ---- heads: the base, fitted, painted (the drawing's outline over front and profile)
box = (-170, 180, -180, 180); W, H = 480, 470
c = O.cam_for(*box, W, H)
views = [('f', dict(c, yaw=0, target=[0, c['cy'], 0])), ('q', dict(c, yaw=-0.62, target=[0, c['cy'], 0])),
         ('s', dict(c, yaw=-1.5708, target=[0, c['cy'], 0]))]
OUTL = [[VW.HEAD_F, VW.NECK_F, VW.EAR_F, VW.mx(VW.EAR_F)], None, [VW.HEAD_S]]
shots('hbm-head.json', W, H, [dict(name='hb-' + v, set=dict(pose='raw', cam=cm)) for v, cm in views], 'hb')
strip(['hb-f', 'hb-q', 'hb-s'], 'step1-head-base.webp', OUTL, box)
S = dict(pose='stand', poseOpts={'out': 0.04}, still=True, time=2.0)
shots(NAME + '.json', W, H, [dict(name='hf-' + v, set=dict(S, show=['head'], paint=False, cam=cm)) for v, cm in views] +
      [dict(name='hp-' + v, set=dict(S, show=['head'], paint=True, cam=cm)) for v, cm in views] +
      [dict(name='hh-' + v, set=dict(S, show=['head', 'hair'], paint=True, cam=cm)) for v, cm in views], 'hf')
strip(['hf-f', 'hf-q', 'hf-s'], 'step2-head-fitted.webp', OUTL, box)
strip(['hp-f', 'hp-q', 'hp-s'], 'step3-head-painted.webp')
strip(['hh-f', 'hh-q', 'hh-s'], 'step7-hair.webp')

# ---- the body: Anny's child as it comes; the skeleton moved and the limbs; with the clothes
bw, bh = 420, 720
cb = dict(mode='ortho', h=1.42, cy=0.66, cx=0)
bv = [('f', 0.0), ('q', -0.62), ('s', -1.5708)]
cam = lambda y: dict(cb, yaw=y, target=[0, 0.66, 0])
shots('anny.json', bw, bh, [dict(name='an-' + v, set=dict(pose='raw', cam=cam(y))) for v, y in bv], 'an')
strip(['an-f', 'an-q', 'an-s'], 'step4-body-base.webp', scale=0.8)
limbs = ['armLeft', 'armRight', 'legLeft', 'legRight', 'handLeft', 'handRight', 'head', 'plaster']
cl = limbs + ['shirt', 'shorts', 'shortsLeft', 'shortsRight', 'sleeveLeft', 'sleeveRight', 'sockLeft', 'sockRight', 'shoeLeft', 'shoeRight']
shots(NAME + '.json', bw, bh, [dict(name='bk-' + v, set=dict(S, show=limbs, cam=cam(y))) for v, y in bv] +
      [dict(name='bc-' + v, set=dict(S, show=cl, cam=cam(y))) for v, y in bv] +
      [dict(name='bb-' + v, set=dict(S, show=None, cam=cam(y))) for v, y in [('qb', 2.4), ('b', 3.1416), ('r', 1.5708)]], 'bk')
strip(['bk-f', 'bk-q', 'bk-s'], 'step5-body-limbs.webp', scale=0.8)
strip(['bc-f', 'bc-q', 'bc-s'], 'step6-clothes.webp', scale=0.8)
strip(['bb-qb', 'bb-b', 'bb-r'], 'back.webp', scale=0.8)

# ---- the drawing and the 3D (compare.py's pictures)
for n in ('side', 'over'):
    im = Image.open(os.path.join(CACHE, 'cmp', n + '.png')).convert('RGB')
    im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(PICS, f'compare-{n}.webp'), quality=88)
# the three-quarter alone, the style's drawing beside the 3D: the cover
im = Image.open(os.path.join(CACHE, 'cmp', 'side.png')).convert('RGB'); w3, h2 = im.width // 3, im.height // 2
cv = Image.new('RGB', (w3 * 2, h2)); cv.paste(im.crop((w3, 0, 2 * w3, h2)), (0, 0)); cv.paste(im.crop((w3, h2, 2 * w3, 2 * h2)), (w3, 0))
cv.resize((cv.width // 2, cv.height // 2), Image.LANCZOS).save(os.path.join(PICS, 'cover.webp'), quality=88)

# ---- expressions: the drawing's sheet, then the 3D in three-quarter and front
E = json.loads(subprocess.run(['node', '-e', "import('./web/face.js').then(m => console.log(JSON.stringify(m.EXPR_NAMES)))"], cwd=HERE, capture_output=True, text=True).stdout)
ce = dict(mode='ortho', h=0.56, cy=1.0, yaw=-0.62, pitch=0.0, target=[0, 1.0, 0])
shots(NAME + '.json', 380, 400, [dict(name='e-' + e, set=dict(S, show=None, exprTrack=[[0, e]], cam=ce)) for e in E] +
      [dict(name='ef-' + e, set=dict(S, exprTrack=[[0, e]], cam=dict(ce, yaw=0))) for e in E], 'ex')
strip(['e-' + e for e in E], 'expr-three.webp')
strip(['ef-' + e for e in E], 'expr-front.webp')
Image.open(os.path.join(S3, 'pics', f'expressions-{NAME}.png')).convert('RGB').save(os.path.join(PICS, 'expr-drawing.webp'), quality=88)

# ---- the turn
d = os.path.join(WORK, 'turn'); shutil.rmtree(d, ignore_errors=True)
shots(NAME + '.json', 440, 720, [dict(name='turn', set=dict(S, exprTrack=[[0, E[0]]], cam=cam(0)), film={'from': 0, 'to': 59, 'step': 1, 'yaw': [0, -2 * np.pi * 59 / 60]})], 'turn')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '20', '-i', os.path.join(d, 'f%04d.png'), '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', os.path.join(PICS, 'turn.mp4')], check=True)
print('ok')
