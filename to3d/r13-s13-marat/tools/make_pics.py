"""The page's pictures and films (to3d/r13-s13-marat/pics), printed by web/marat.js through shots.mjs.
  python3 make_pics.py [stills|films|<name>...]      (after form.py and build.py)
Films are 12 prints a second (each held for two frames of 24)."""
import os, sys, json, subprocess, shutil, time
from PIL import Image
import drawing as D

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = '/home/user/cache/to3d-r13-s13-marat/pics'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
STY = os.path.join(HERE, '..', '..', '..', 'styles', 's13-ukiyo-e', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PACK = '/works-010-art-direction/to3d/r13-s13-marat/data/marat.json'
want = sys.argv[1:] or ['stills', 'films']
on = lambda name, kind: kind in want or name in want


def shots(w, h, sh, name):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PACK, w=w, h=h, shots=sh), open(j, 'w'))
    while True:          # heavy runs take turns: whichever of the three shared locks is free
        for k in range(3):
            r = subprocess.run(['flock', '-n', '-E', '99', '/home/user/cache/heavy.%d.lock' % k, 'node', os.path.join(HERE, 'shots.mjs'), j, WORK],
                               env=ENV, stdout=subprocess.DEVNULL)
            if r.returncode != 99: r.check_returncode(); return
        time.sleep(3)


im = lambda n: Image.open(os.path.join(WORK, n + '.png')).convert('RGB')


def row(ims, out, scale=1.0, q=88):
    W = sum(i.width for i in ims); H = max(i.height for i in ims)
    o = Image.new('RGB', (W, H), (238, 227, 203)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(PICS, out), quality=q)


def film(name, w, h, set_, frm, to, step, yaw=None):
    d = os.path.join(WORK, name); shutil.rmtree(d, ignore_errors=True)
    if not set_.get('still'): set_ = {k: v for k, v in set_.items() if k != 'time'}       # the face's clock: the clip's
    shots(w, h, [dict(name=name, set=set_, film={'from': frm, 'to': to, 'step': step, **({'yaw': yaw} if yaw else {})})], name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '12', '-i', os.path.join(d, 'f%04d.png'), '-r', '24',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '27', '-movflags', '+faststart',
                    os.path.join(PICS, name + '.mp4')], check=True)


STAND = dict(pose='stand', poseOpts={}, still=True, exprTrack=[[0, 'grin']], time=2, clip=None, ladle=False, sheet=True, name=True,
             noColour=False, noLine=False, noFace=False, plain=False, noTexture=False, talk=False)
# the drawing's sheets: the figure at 1.12 px a figure unit on 800 × 1200 (feet at y 1120); the busts of the turnaround
# at 1.5 px a head unit (eye line at y 310 of 800); the expression heads at 1.4 (eye line at 280 of 720)
FIG = dict(mode='ortho', h=1200 * D.KF / 1.12, cy=(1120 - 600) * D.KF / 1.12, pitch=0, follow=False, focus=None)
BUST = dict(mode='ortho', h=800 * D.K / 1.5, cy=D.EYE - 90 * D.K / 1.5, pitch=0, follow=False, focus=None, target=None)
EXPR = dict(mode='ortho', h=720 * D.K / 1.4, cy=D.EYE - 80 * D.K / 1.4, pitch=0, follow=False, focus=None, target=None)
FIGPOSE = dict(STAND, poseOpts={'figure': True, 'headTurn': 0.1, 'headTilt': 0.08}, ladle=True)
FIGCAM = dict(FIG, yaw=0.6, target=[-0.08, FIG['cy'], 0.14])

if on('compare', 'stills'):
    shots(800, 1200, [dict(name='fig', set=dict(FIGPOSE, name=False, cam=FIGCAM))], 'fig')
    a, d = im('fig'), Image.open(os.path.join(STY, 'figure-marat.jpg')).convert('RGB').resize((800, 1200))
    row([d, a], 'compare-figure.jpg', 0.75)
    row([Image.blend(a, d, 0.5)], 'overlay-figure.jpg', 0.75)
    shots(600, 800, [dict(name='b' + k, set=dict(STAND, name=False, cam=dict(BUST, yaw=y))) for k, y in (('f', 0), ('q', 0.7), ('s', 1.5708))], 'bust')
    t = Image.open(os.path.join(STY, 'turn-marat.jpg')).convert('RGB').resize((1800, 800))
    o = Image.new('RGB', (1800, 800)); [o.paste(im('b' + k), (i * 600, 0)) for i, k in enumerate('fqs')]
    tall = Image.new('RGB', (1800, 1600)); tall.paste(t, (0, 0)); tall.paste(o, (0, 800))
    tall.resize((1260, 1120), Image.LANCZOS).save(os.path.join(PICS, 'compare-turn.jpg'), quality=88)
    Image.blend(o, t, 0.5).resize((1260, 560), Image.LANCZOS).save(os.path.join(PICS, 'overlay-turn.jpg'), quality=88)

if on('steps', 'stills'):
    c = dict(FIG, yaw=0.6, target=[-0.08, FIG['cy'], 0.14]); S = dict(STAND, name=False, poseOpts={'figure': True, 'headTurn': 0.1, 'headTilt': 0.08})
    shots(800, 1200, [dict(name='s1', set=dict(S, plain=True, noLine=True, noFace=True, sheet=False, noTexture=True, cam=c)),
                      dict(name='s2', set=dict(S, noLine=True, noFace=True, cam=c)),
                      dict(name='s3', set=dict(S, noColour=True, noFace=True, cam=c)),
                      dict(name='s4', set=dict(S, ladle=True, name=True, cam=c))], 'steps')
    row([im('s1'), im('s2'), im('s3'), im('s4')], 'steps-render.jpg', 0.5)
    S = dict(STAND, name=False)
    shots(700, 1200, [dict(name='bk' + str(i), set=dict(S, cam=dict(FIG, yaw=y, target=None))) for i, y in enumerate((0, -0.9, 3.1416, 2.2))], 'back')
    row([im('bk0'), im('bk1'), im('bk2'), im('bk3')], 'back.jpg', 0.5)

if on('expr', 'stills'):
    E = ['grin', 'surprise', 'sad', 'anger']
    shots(490, 720, [dict(name='e-' + e, set=dict(STAND, name=False, exprTrack=[[0, e]], cam=dict(EXPR, yaw=0.7))) for e in E], 'expr')
    row([im('e-' + e) for e in E], 'expr-3d.jpg', 0.7)
    Image.open(os.path.join(STY, 'expr-marat.jpg')).convert('RGB').resize((1400, 504), Image.LANCZOS).save(os.path.join(PICS, 'expr-drawing.jpg'), quality=88)
    shots(490, 720, [dict(name='c-' + str(i), set=dict(STAND, name=False, exprTrack=[[0, e]], cam=dict(EXPR, yaw=y))) for i, (e, y) in
                     enumerate((('calm', 0.0), ('calm', -0.8), ({'grin': 0.5, 'surprise': 0.5}, 0.4), ({'sad': 0.5, 'anger': 0.5}, 0.9)))], 'expr2')
    row([im('c-%d' % i) for i in range(4)], 'expr-more.jpg', 0.7)

FOLLOW = dict(mode='persp', fov=22, dist=6.6, cy=1.02, follow=True, focus=None, target=None, pitch=0.05)
if on('turn', 'films'):
    film('turn', 520, 780, dict(STAND, cam=dict(FIG, h=2.35, cy=1.03, yaw=0, target=None)), 0, 47, 1, yaw=[0, 6.2832 * 47 / 48])
if on('walk', 'films'):
    film('walk', 520, 780, dict(STAND, still=False, clip='walk', exprTrack=[[0, 'calm'], [1.4, 'grin'], [3.0, 'calm']], cam=dict(FOLLOW, yaw=0.9)), 0, 117.5, 2.5)
if on('wave', 'films'):
    film('wave', 520, 780, dict(STAND, still=False, clip='wave', exprTrack=[[0, 'calm'], [0.5, 'grin']], cam=dict(FOLLOW, yaw=0.35, cy=1.12, dist=7.2)), 0, 87.5, 2.5)
if on('dance', 'films'):
    film('dance', 520, 780, dict(STAND, still=False, clip='dance', exprTrack=[[0, 'grin']], cam=dict(FOLLOW, yaw=0.3, cy=1.08, dist=7.0)), 0, 117.5, 2.5)
if on('talk', 'films'):
    film('talk', 520, 600, dict(STAND, still=False, clip='idle', talk=True, talkFrom=0.5, talkTo=5.2,
                                exprTrack=[[0, 'calm'], [2.2, 'surprise'], [3.2, 'calm'], [5.2, 'grin']],
                                cam=dict(mode='persp', fov=22, dist=2.3, follow=False, focus='Head', up=-0.03, yaw=0.5, pitch=0.03, target=None)), 0, 177.5, 2.5)
print('ok')
