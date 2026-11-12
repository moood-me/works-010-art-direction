"""All the page's pictures and films (to3d/r15-s15-anya/pics), from the packs in the cache.
python3 make_pics.py  (after build.py, bases.py, faces.py + render_svg.mjs, compare.py)"""
import os, json, subprocess, shutil
import numpy as np
from PIL import Image
import drawing as D, overlay as O, anya

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = '/home/user/cache/to3d-r15-s15-anya'
WORK = os.path.join(CACHE, 'pics'); os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PK = '/cache/to3d-r15-s15-anya/out/'


def shots(pack, w, h, shots, name):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PK + pack, w=w, h=h, shots=shots), open(j, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True, env=ENV)


def strip(names, out, outline=None, box=None, scale=1.0, q=88):
    ims = [Image.open(os.path.join(WORK, n + '.png')).convert('RGB') for n in names]
    if outline:
        ims = [O.outline(im, sh, box, col=(40, 120, 200), w=2) if sh else im for im, sh in zip(ims, outline)]
    W = sum(i.width for i in ims); o = Image.new('RGB', (W, ims[0].height)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(PICS, out), quality=q)


# ---- heads: the base, fitted, painted (the drawing's outline over front and profile)
box = (-150, 270, -180, 180); W, H = 480, 560
c = O.cam_for(*box, W, H)
views = [('f', dict(c, yaw=0, target=[0, c['cy'], 0])), ('q', dict(c, yaw=-0.6, target=[0, c['cy'], 0])),
         ('s', dict(c, yaw=-1.5708, target=[0, c['cy'], 0]))]
OUTL = [[anya.FACE_F], None, [anya.FACE_S]]
shots('hbm-head.json', W, H, [dict(name='hb-' + v, set=dict(pose='raw', cam=cm)) for v, cm in views], 'hb')
strip(['hb-f', 'hb-q', 'hb-s'], 'step1-head-base.webp', OUTL, box)
shots('anya.json', W, H, [dict(name='hf-' + v, set=dict(pose='stand', show=['head'], paint=False, cam=cm)) for v, cm in views] +
      [dict(name='hp-' + v, set=dict(pose='stand', show=['head'], paint=True, cam=cm)) for v, cm in views], 'hf')
strip(['hf-f', 'hf-q', 'hf-s'], 'step2-head-fitted.webp', OUTL, box)
strip(['hp-f', 'hp-q', 'hp-s'], 'step3-head-painted.webp')

# ---- the body: Anny as it comes; what is kept of it with the head; with the clothes; the form alone
bw, bh = 420, 900
cb = dict(mode='ortho', h=1.78, cy=0.84, cx=0)
bv = [('f', 0.0), ('q', -0.6), ('s', -1.5708)]
shots('anny.json', bw, bh, [dict(name='an-' + v, set=dict(pose='raw', cam=dict(cb, yaw=y, target=[0, 0.84, 0]))) for v, y in bv], 'an')
strip(['an-f', 'an-q', 'an-s'], 'step4-body-base.webp', scale=0.8)
S = dict(pose='stand', poseOpts={'out': 0.08}, still=True)
cl = ['body', 'head', 'dress', 'collar', 'cardigan', 'sleeveLeft', 'sleeveRight']
shots('anya.json', bw, bh, [dict(name='bk-' + v, set=dict(S, show=['body', 'head'], cam=dict(cb, yaw=y, target=[0, 0.84, 0]))) for v, y in bv] +
      [dict(name='bc-' + v, set=dict(S, show=cl, cam=dict(cb, yaw=y, target=[0, 0.84, 0]))) for v, y in bv] +
      [dict(name='bf-' + v, set=dict(S, show=cl + ['hair'], flat=True, paint=False, cam=dict(cb, yaw=y, target=[0, 0.84, 0]))) for v, y in bv] +
      [dict(name='bb-' + v, set=dict(S, show=cl + ['hair'], flat=False, paint=True, cam=dict(cb, yaw=y, target=[0, 0.84, 0]))) for v, y in [('b', 3.1416), ('r', 1.5708), ('qb', 2.4)]], 'bk')
strip(['bk-f', 'bk-q', 'bk-s'], 'step5-body-kept.webp', scale=0.8)
strip(['bc-f', 'bc-q', 'bc-s'], 'step6-clothes.webp', scale=0.8)
# (the form alone, bf-*, is rendered but not shown: the folded eye sockets show in it)
strip(['bb-qb', 'bb-b', 'bb-r'], 'back.webp', scale=0.8)

# ---- the drawing and the 3D (compare.py's pictures)
for n in ('side', 'over'):
    im = Image.open(os.path.join(CACHE, 'cmp', n + '.png')).convert('RGB')
    im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(PICS, f'compare-{n}.webp'), quality=88)

# ---- expressions: the drawing's sheet, then the 3D in three-quarter and front
E = ['dream', 'joy', 'surprise', 'sad', 'anger']
ce = dict(mode='ortho', h=0.46, cy=1.40, yaw=-0.6, pitch=0.0, target=[0, 1.40, 0])
shots('anya.json', 380, 440, [dict(name='e-' + e, set=dict(S, exprTrack=[[0, e]], time=2.0, cam=ce)) for e in E] +
      [dict(name='ef-' + e, set=dict(S, exprTrack=[[0, e]], time=2.0, cam=dict(ce, yaw=0))) for e in E], 'ex')
strip(['e-' + e for e in E], 'expr-three.webp')
strip(['ef-' + e for e in E], 'expr-front.webp')
shutil.copy(os.path.join(HERE, '..', '..', '..', 'styles', 's3-graphic', 'pics', 'expressions-anya.png'), os.path.join(WORK, 'expr-drawing.png'))
im = Image.open(os.path.join(WORK, 'expr-drawing.png')).convert('RGB'); im.save(os.path.join(PICS, 'expr-drawing.webp'), quality=88)


# ---- films (the motions with the live face: make_live.py)
def film(name, pack, w, h, set_, frm, to, step, yaw=None, fps=24):
    d = os.path.join(WORK, name)
    shutil.rmtree(d, ignore_errors=True)
    f = dict(from_=0)
    sh = dict(name=name, set=set_, film={'from': frm, 'to': to, 'step': step, **({'yaw': yaw} if yaw else {})})
    shots(pack, w, h, [sh], name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(d, 'f%04d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', os.path.join(PICS, name + '.mp4')], check=True)


film('turn', 'anya.json', 540, 900, dict(S, cam=dict(cb, yaw=0, target=[0, 0.84, 0])), 0, 71, 1, yaw=[0, -2 * np.pi * 71 / 72])
print('ok')
