"""The page's pictures and films (to3d/r52-s18-vera/pics), drawn by web/vera.js through shots.mjs.
  python3 make_pics.py [stills|films|<name>...]      (after build.py)
  python3 make_pics.py job <jobs.json> <outdir>      (any shots, for looking)
Every run of the browser goes through one of the three shared locks (/home/user/cache/heavy.N.lock).
Films are drawn 12 times a second and each drawing held for two frames of 24 (drawn animation "on twos")."""
import os, sys, json, subprocess, shutil, fcntl, time, math
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = '/home/user/cache/to3d-r52-s18-vera/pics'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
STY = os.path.join(HERE, '..', '..', '..', 'styles', 's18-manga', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
PACK = '/works-010-art-direction/to3d/r52-s18-vera/data/vera.json'
PAPER = (251, 250, 246)
want = sys.argv[1:] or ['stills', 'films']


def heavy(cmd):
    while True:
        for k in range(3):
            f = open(f'/home/user/cache/heavy.{k}.lock', 'w')
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                f.close(); continue
            try:
                return subprocess.run(cmd, env=ENV, check=True)
            finally:
                f.close()
        time.sleep(2)


def on(name, kind):
    return kind in want or name in want


def shots(w, h, sh, name, out=WORK):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PACK, w=w, h=h, shots=sh), open(j, 'w'))
    heavy(['node', os.path.join(HERE, 'shots.mjs'), j, out])


def im(n):
    return Image.open(os.path.join(WORK, n + '.png')).convert('RGB')


def row(ims, out=None, scale=1.0, gap=0):
    W = sum(i.width for i in ims) + gap * (len(ims) - 1); H = max(i.height for i in ims)
    o = Image.new('RGB', (W, H), PAPER); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width + gap
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    if out: o.save(os.path.join(PICS, out), quality=90, method=6)
    return o


def col(ims, out, scale=1.0):
    W = max(i.width for i in ims); H = sum(i.height for i in ims)
    o = Image.new('RGB', (W, H), PAPER); y = 0
    for i in ims: o.paste(i, (0, y)); y += i.height
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(PICS, out), quality=90, method=6)


def film(name, w, h, set_, frm, to, step, yaw=None, crf=24, clock=None):
    d = os.path.join(WORK, name); shutil.rmtree(d, ignore_errors=True)
    if not set_.get('still'): set_ = {k: v for k, v in set_.items() if k != 'time'}
    shots(w, h, [dict(name=name, set=set_, film={'from': frm, 'to': to, 'step': step, **({'yaw': yaw} if yaw else {}), **({'clock': clock} if clock else {})})], name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '12', '-i', os.path.join(d, 'f%04d.png'), '-r', '24',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', str(crf), '-movflags', '+faststart',
                    os.path.join(PICS, name + '.mp4')], check=True)


if want[0] == 'job':
    heavy(['node', os.path.join(HERE, 'shots.mjs'), want[1], want[2]]); sys.exit()

KH = 1.72 / 7.39; PIT = 1.423 + 0.012; ZAX = 0.04      # the body's unit, the pit of the neck, the body's axis
STAND = dict(pose='stand', poseOpts={}, still=True, exprTrack=[[0, 'rest']], time=2, clip=None, clay=False, noTone=False, noLine=False, ground=True, sky=None)
FIGP = dict(STAND, poseOpts={'figure': True, 'headTurn': 0.035, 'headNod': 0.07})


def cam_like(S, H, pit_y, yaw_deg, dx=0.0):
    """The drawing's View(yaw, s) with the pit of the neck at pit_y px in a panel H px high (dx: the pit's px right of the centre)."""
    y = -math.radians(yaw_deg); ppm = S / KH
    return dict(mode='ortho', h=H / ppm, yaw=y, pitch=0, follow=False, focus=None,
                target=[-dx / ppm * math.cos(y), PIT + (pit_y - H / 2) / ppm, ZAX + dx / ppm * math.sin(y)])


def cam_ground(S, H, gy, yaw_deg, dx=0.0):
    y = -math.radians(yaw_deg); ppm = S / KH
    return dict(mode='ortho', h=H / ppm, yaw=y, pitch=0, follow=False, focus=None, target=[-dx / ppm * math.cos(y), (gy - H / 2) / ppm, ZAX + dx / ppm * math.sin(y)])


if on('compare', 'stills'):
    # the turnaround (head and shoulders): front, three-quarter, profile — the drawing's own frames
    shots(500, 640, [dict(name='b' + k, set=dict(STAND, ground=False, cam=cam_like(300, 640, 470, yw))) for k, yw in (('f', 0), ('q', 35), ('s', 90))], 'bust')
    t = Image.open(os.path.join(STY, 'turn-vera.png')).convert('RGB').resize((1500, 640))
    o = row([im('bf'), im('bq'), im('bs')])
    col([t, o], 'compare-turn.webp', 0.8)
    Image.blend(o, t, 0.5).resize((1200, 512), Image.LANCZOS).save(os.path.join(PICS, 'overlay-turn.webp'), quality=88)
    # the figure as drawn: yaw 26, a folder under the right hand, the left hand at the glasses
    shots(700, 1150, [dict(name='fig', set=dict(FIGP, sky=[0, 0.1], cam=cam_ground(1000 / 8.1, 1150, 1080, 26)))], 'fig')
    a, d = im('fig'), Image.open(os.path.join(STY, 'figure-vera.png')).convert('RGB').resize((700, 1150))
    row([d, a], 'compare-figure.webp', 0.8)
    Image.blend(a, d, 0.5).resize((560, 920), Image.LANCZOS).save(os.path.join(PICS, 'overlay-figure.webp'), quality=88)
    # the portrait
    shots(800, 1000, [dict(name='por', set=dict(FIGP, sky=[0, 0.12], ground=False, cam=cam_like(360, 1000, 700, 26, dx=-32)))], 'por')
    a, d = im('por'), Image.open(os.path.join(STY, 'portrait-vera.png')).convert('RGB').resize((800, 1000))
    row([d, a], 'compare-portrait.webp', 0.8)
    Image.blend(a, d, 0.5).resize((640, 800), Image.LANCZOS).save(os.path.join(PICS, 'overlay-portrait.webp'), quality=88)
    a.save(os.path.join(PICS, 'cover.webp'), quality=90)

if on('steps', 'stills'):
    c = cam_ground(1000 / 8.1, 1150, 1080, 26)
    shots(700, 1150, [dict(name='s1', set=dict(STAND, clay=True, cam=c)), dict(name='s2', set=dict(STAND, noTone=True, cam=c)),
                      dict(name='s3', set=dict(STAND, noLine=True, cam=c)), dict(name='s4', set=dict(STAND, cam=c))], 'steps')
    row([im('s1'), im('s2'), im('s3'), im('s4')], 'steps.webp', 0.6)
    shots(700, 1150, [dict(name='bk' + str(i), set=dict(STAND, cam=dict(cam_ground(1000 / 8.1, 1150, 1080, 0), yaw=y))) for i, y in enumerate((1.0, 3.1416, -2.2))], 'back')
    row([im('bk0'), im('bk1'), im('bk2')], 'back.webp', 0.6)
    ch = cam_like(360, 800, 560, 35)
    shots(640, 800, [dict(name='h1', set=dict(STAND, ground=False, clay=True, cam=ch)), dict(name='h2', set=dict(STAND, ground=False, noTone=True, cam=ch)),
                     dict(name='h3', set=dict(STAND, ground=False, cam=ch))], 'steps-head')
    row([im('h1'), im('h2'), im('h3')], 'steps-head.webp', 0.75)

if on('expr', 'stills'):
    E = ['rest', 'joy', 'surprise', 'sadness', 'anger']
    ce = cam_like(330, 520, 420, 28)
    shots(420, 520, [dict(name='e-' + e, set=dict(STAND, ground=False, exprTrack=[[0, e]], cam=ce)) for e in E], 'expr')
    row([im('e-' + e) for e in E], 'expr.webp', 0.8)

FAR = dict(mode='persp', fov=22, dist=4.9, cy=0.9, follow=True, focus=None, target=None, pitch=0.05)
if on('turn', 'films'):
    film('turn', 480, 800, dict(STAND, cam=dict(cam_ground(88, 800, 760, 0))), 0, 47, 1, yaw=[0, -6.2832 * 47 / 48])
if on('walk', 'films'):
    film('walk', 520, 800, dict(STAND, still=False, clip='walk', cam=dict(FAR, yaw=-0.85)), 0, 117.5, 2.5)
if on('wave', 'films'):
    film('wave', 520, 800, dict(STAND, still=False, clip='wave', exprTrack=[[0, 'rest'], [0.7, 'joy'], [2.4, 'rest']], cam=dict(FAR, yaw=-0.45)), 0, 87.5, 2.5)
if on('talk', 'films'):
    film('talk', 520, 600, dict(STAND, still=False, ground=False, clip=None, talk=True, talkFrom=0.4,
                                exprTrack=[[0, 'rest'], [1.6, 'anger'], [2.8, 'rest'], [3.6, 'joy'], [4.5, 'rest']],
                                cam=dict(mode='persp', fov=22, dist=1.75, follow=False, focus='Head', up=0.06, target=None, yaw=-0.5, pitch=0.03)), 0, 147.5, 2.5, clock=30)
print('ok')
