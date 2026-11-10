"""The page's pictures and films (../pics), printed by web/print.js through shots.mjs.
  python3 make_pics.py [stills|films|<name>...]      (after build.py)
Films are printed at 12 pictures a second (each held for two frames of 24). Every run of the browser goes through one
of the shared locks (heavy runs take turns)."""
import os, sys, json, subprocess, shutil, random
from PIL import Image
import drawing as D
import who

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = who.NAME
FOLDER = os.path.basename(os.path.dirname(HERE))
WORK = f'/home/user/cache/to3d-{FOLDER}/pics'; os.makedirs(WORK, exist_ok=True)
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
STY = os.path.join(HERE, '..', '..', '..', 'styles', 's13-ukiyo-e', 'pics')
PACK = f'/works-010-art-direction/to3d/{FOLDER}/data/{NAME}.json'
want = sys.argv[1:] or ['stills', 'films']
PAPER = (238, 227, 203)


def on(name, kind):
    return kind in want or name in want


def shots(w, h, sh, name):
    j = os.path.join(WORK, name + '.json')
    json.dump(dict(pack=PACK, w=w, h=h, shots=sh), open(j, 'w'))
    subprocess.run(['flock', '/home/user/cache/heavy.%d.lock' % random.randrange(3), 'node', os.path.join(HERE, 'shots.mjs'), j, WORK], check=True)


def im(n):
    return Image.open(os.path.join(WORK, n + '.png')).convert('RGB')


def row(ims, out, scale=1.0, q=88, gap=0):
    W = sum(i.width for i in ims) + gap * (len(ims) - 1); H = max(i.height for i in ims)
    o = Image.new('RGB', (W, H), PAPER); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width + gap
    if scale != 1: o = o.resize((int(o.width * scale), int(o.height * scale)), Image.LANCZOS)
    o.save(os.path.join(PICS, out), quality=q)


def film(name, w, h, set_, frm, to, step, yaw=None, crf=26):
    d = os.path.join(WORK, name); shutil.rmtree(d, ignore_errors=True)
    if not set_.get('still'): set_ = {k: v for k, v in set_.items() if k != 'time'}       # the face's clock: the clip's
    shots(w, h, [dict(name=name, set=set_, film={'from': frm, 'to': to, 'step': step, **({'yaw': yaw} if yaw else {})})], name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '12', '-i', os.path.join(d, 'f%04d.png'), '-r', '24',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', str(crf), '-movflags', '+faststart',
                    os.path.join(PICS, name + '.mp4')], check=True)


REST = who.REST
NONAME = dict(name=None)
STAND = dict(pose='stand', poseOpts={}, still=True, exprTrack=[[0, REST]], time=2, clip=None, props=None,
             flat=False, noBlocks=False, noPattern=False, noLine=False, sheet={})
# the drawing's own scales. The figure sheet (800 × 1200): 1.4 px a figure unit — who.FIG_PX px a head unit —, the soles
# at y 1120, the figure's middle at x 400 (who.FIG_X). The turnaround (1800 × 800): three busts, 1.5 px a head unit, the
# eye line at y 310. The expression sheet (2000 × 720): four busts, 1.4 px a unit, the eye line at y 280.
FIG = dict(mode='ortho', h=1200 / who.FIG_PX * D.K, cy=(1120 - 600) / who.FIG_PX * D.K, cx=who.FIG_CX, pitch=0, follow=False, focus=None)
BUST = dict(mode='ortho', h=800 / 1.5 * D.K, cy=(D.FLOOR - 90 / 1.5) * D.K, cx=0, pitch=0, follow=False, focus=None)
EXB = dict(mode='ortho', h=720 / 1.4 * D.K, cy=(D.FLOOR - 80 / 1.4) * D.K, cx=0, pitch=0, follow=False, focus=None)

if on('compare', 'stills'):
    shots(800, 1200, [dict(name='fig', set=dict(STAND, sheet=NONAME, poseOpts=who.FIG_POSE, exprTrack=[[0, who.FIG_EXPR]], props=who.FIG_PROPS, cam=dict(FIG, yaw=who.FIG_YAW)))], 'fig')
    a, d = im('fig'), Image.open(os.path.join(STY, f'figure-{NAME}.jpg')).convert('RGB').resize((800, 1200))
    row([d, a], 'compare-figure.jpg', 0.75, gap=16)
    row([Image.blend(a, d, 0.5)], 'overlay-figure.jpg', 0.75)
    shots(600, 800, [dict(name='b' + k, set=dict(STAND, sheet=NONAME, poseOpts=who.BUST_POSE, cam=dict(BUST, yaw=y, cx=cx))) for k, y, cx in (('f', 0, 0), ('q', 0.75, who.BUST_CX[0]), ('s', 1.5708, who.BUST_CX[1]))], 'bust')
    t = Image.open(os.path.join(STY, f'turn-{NAME}.jpg')).convert('RGB').resize((1800, 800))
    o = Image.new('RGB', (1800, 800)); [o.paste(x, (i * 600, 0)) for i, x in enumerate([im('bf'), im('bq'), im('bs')])]
    tall = Image.new('RGB', (1800, 1616), PAPER); tall.paste(t, (0, 0)); tall.paste(o, (0, 816))
    tall.resize((1200, 1077), Image.LANCZOS).save(os.path.join(PICS, 'compare-turn.jpg'), quality=88)
    Image.blend(o, t, 0.5).resize((1200, 533), Image.LANCZOS).save(os.path.join(PICS, 'overlay-turn.jpg'), quality=88)

if on('portrait', 'stills'):
    c = dict(mode='ortho', h=1100 / 2.0 * D.K, cy=(D.FLOOR - (550 - 480) / 2.0) * D.K, cx=-20 / 2.0 * D.K, pitch=0, follow=False, focus=None, yaw=0.75)
    shots(800, 1100, [dict(name='portrait', set=dict(STAND, poseOpts=who.BUST_POSE, cam=c))], 'portrait')
    a, d = im('portrait'), Image.open(os.path.join(STY, f'portrait-{NAME}.jpg')).convert('RGB').resize((800, 1100))
    row([d, a], 'compare-portrait.jpg', 0.75, gap=16)
    a.resize((600, 825), Image.LANCZOS).save(os.path.join(PICS, 'portrait.jpg'), quality=90)

if on('steps', 'stills'):
    c = dict(FIG, yaw=0.6, cx=0)
    plain = dict(name=None, plain=True, ground=None)
    shots(600, 900, [dict(name='s1', set=dict(STAND, flat=True, cam=c)), dict(name='s2', set=dict(STAND, noBlocks=True, sheet=plain, cam=c)),
                     dict(name='s3', set=dict(STAND, noLine=True, noPattern=True, sheet=plain, cam=c)), dict(name='s4', set=dict(STAND, noLine=True, sheet=plain, cam=c)),
                     dict(name='s5', set=dict(STAND, cam=c))], 'steps')
    row([im('s1'), im('s2'), im('s3'), im('s4'), im('s5')], 'steps-render.jpg', 0.6)
    shots(600, 900, [dict(name='bk' + str(i), set=dict(STAND, sheet=NONAME, cam=dict(FIG, cx=0, yaw=y))) for i, y in enumerate((-0.8, 3.1416, 2.3))], 'back')
    row([im('bk0'), im('bk1'), im('bk2')], 'back.jpg', 0.6)

if on('expr', 'stills'):
    E = ['joy', 'surprise', 'sad', 'anger']
    shots(490, 720, [dict(name='e-' + e, set=dict(STAND, sheet=NONAME, poseOpts=who.BUST_POSE, exprTrack=[[0, e]], cam=dict(EXB, yaw=0.75, cx=who.BUST_CX[0]))) for e in E], 'expr')
    row([im('e-' + e) for e in E], 'expr-3d.jpg', 0.7)
    Image.open(os.path.join(STY, f'expr-{NAME}.jpg')).convert('RGB').resize((1372, 494), Image.LANCZOS).save(os.path.join(PICS, 'expr-drawing.jpg'), quality=88)

for name, o in who.FILMS.items():
    if on(name, 'films'):
        film(name, o['w'], o['h'], dict(STAND, **o['set']), o['from'], o['to'], o.get('step', 2.5), yaw=o.get('yaw'))
print('ok')
