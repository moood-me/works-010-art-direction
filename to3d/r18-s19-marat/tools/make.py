"""Every picture and film of the page.  python3 make.py [compare] [steps] [stills] [films] [film:<name>]
Renders through shots.mjs (headless Chromium, the page tools/web/view.html) with the drawing's own cameras, sets the
renders beside and over the drawing's sheets (styles/s19-lowpoly/pics), encodes mp4 with ffmpeg, writes webp/mp4 into
../pics. Work files in /home/user/cache/to3d-r18-s19-marat/. Heavy runs go through the shared locks."""
import json
import os
import random
import subprocess
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
C = '/home/user/cache/to3d-r18-s19-marat'
PICS = os.path.join(HERE, '..', 'pics')
D = os.path.join(HERE, '..', '..', '..', 'styles', 's19-lowpoly', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
POSES = json.load(open(os.path.join(HERE, 'web', 'data', 'poses.json')))
os.makedirs(C, exist_ok=True)
os.makedirs(PICS, exist_ok=True)


def shots(name, jobs):
    p = f'{C}/{name}.json'
    json.dump(jobs, open(p, 'w'))
    subprocess.run(['flock', f'/home/user/cache/heavy.{random.randrange(3)}.lock', 'node', os.path.join(HERE, 'shots.mjs'), p, f'{C}/{name}'], check=True, env=ENV)
    return f'{C}/{name}'


def webp(src, dst, q=86):
    im = src if isinstance(src, Image.Image) else Image.open(src)
    im.convert('RGB').save(os.path.join(PICS, dst), 'WEBP', quality=q, method=6)


def film(folder, dst, fps=24, crf=25):
    subprocess.run(['flock', f'/home/user/cache/heavy.{random.randrange(3)}.lock', 'ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', f'{folder}/f%04d.png',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', str(crf), '-preset', 'slow', '-movflags', '+faststart', os.path.join(PICS, dst)], check=True)


def font(size):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
    except OSError:
        return ImageFont.load_default()


# ---------------------------------------------------------------- the drawing's cameras (styles/s19-lowpoly/tools/build.py)
def draw_cam(yaw, pitch, f, scale, ox, oy, target=(0, 0, 0)):
    return {'mode': 'draw', 'yaw': yaw, 'pitch': pitch, 'dist': f / 100, 'scale': scale * 100, 'ox': ox, 'oy': oy, 'target': list(target), 'follow': None}


def head_cam(pose, yaw, scale, ox, oy, up):
    h = POSES[pose]['head']
    return draw_cam(yaw, 3.0, 520.0, scale, ox, oy, (h[0], h[1] + up / 100, h[2]))


H_TURN = POSES['turn']['head'][1] * 100 + 14
H_STAND = POSES['stand']['head'][1] * 100 + 14
SC_TURN = min(560.0 / (H_TURN + 10), 3.1)
SC_FIG = min(800.0 / (H_STAND + 12), 5.6)
ON_PLINTH = {'plinth': True, 'ground': False, 'shadow': True, 'bg': True}
YAWS = [(0, 'анфас'), (38, 'три четверти'), (90, 'профиль')]
EXPRS = [('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('anger', 'злость')]


def sheet(cells, labels, out, width=1500):
    """cells: [(drawing crop, render, render with alpha)] → rows: the drawing, the 3D, the 3D's outline in red over
    the drawing made pale (the renders are taken with the drawing's own camera: same scale, same place)."""
    w, h = cells[0][0].size
    S = Image.new('RGB', (w * len(cells), h * 3), 'white')
    dr = ImageDraw.Draw(S); f = font(max(14, h // 34))
    for i, (d, r, a) in enumerate(cells):
        m = np.asarray(a.split()[3]).astype(np.float32) / 255
        mm = Image.fromarray((m > 0.5).astype(np.uint8) * 255)
        edge = np.asarray(mm.filter(ImageFilter.MaxFilter(3))).astype(int) - np.asarray(mm.filter(ImageFilter.MinFilter(3))).astype(int) > 0
        pale = np.asarray(d.convert('RGB')).astype(np.float32) * 0.45 + 255 * 0.55
        pale[edge] = [205, 30, 30]
        for k, im in enumerate((d, r.convert('RGB'), Image.fromarray(pale.astype(np.uint8)))):
            S.paste(im, (i * w, k * h))
            if labels:
                dr.text((i * w + 10, k * h + 8), f'{labels[i]}: {("рисунок", "3D", "наложение")[k]}', fill=(70, 55, 50), font=f)
    if S.width > width:
        S = S.resize((width, int(S.height * width / S.width)), Image.LANCZOS)
    S.save(out)
    return S


def compare():
    base = {'still': True, 'breath': False, 'mode': 'full'}
    jobs = []
    for a in (False, True):
        look = {**ON_PLINTH, 'bg': not a}
        sfx = '-a' if a else ''
        for i, (yaw, _) in enumerate(YAWS):
            jobs.append({'name': f'turn{i}{sfx}', 'size': [500, 720], 'alpha': a, 'set': {**base, 'clip': 'turn', 'expr': {'rest': 1}, 'look': look, 'cam': draw_cam(yaw, 6, 1600, SC_TURN, 250, 640)}})
        jobs.append({'name': f'figure{sfx}', 'size': [800, 1000], 'alpha': a, 'set': {**base, 'clip': 'stand', 'expr': {'rest': 1}, 'look': look, 'cam': draw_cam(18, 7, 1600, SC_FIG, 400, 915)}})
        jobs.append({'name': f'portrait{sfx}', 'size': [800, 960], 'alpha': a, 'set': {**base, 'clip': 'portrait', 'expr': {'rest': 1}, 'look': look, 'cam': head_cam('portrait', 16, 11.8, 400, 430, -10)}})
        for i, (e, _) in enumerate(EXPRS):
            jobs.append({'name': f'expr{i}{sfx}', 'size': [400, 500], 'alpha': a, 'set': {**base, 'clip': 'turn', 'expr': {e: 1}, 'look': look, 'cam': head_cam('turn', 14, 10.0, 200, 268, -5)}})
    out = shots('compare', jobs)
    R = lambda n: (Image.open(f'{out}/{n}.png').convert('RGB'), Image.open(f'{out}/{n}-a.png').convert('RGBA'))
    t = Image.open(f'{D}/turn-marat.webp').convert('RGB')
    webp(sheet([(t.crop((i * 500, 0, i * 500 + 500, 720)), *R(f'turn{i}')) for i in range(3)], [l for _, l in YAWS], f'{C}/cmp-turn.png'), 'compare-turn.webp')
    f = Image.open(f'{D}/figure-marat.webp').convert('RGB')
    p = Image.open(f'{D}/portrait-marat.webp').convert('RGB')
    for name, d, r in (('figure', f, R('figure')), ('portrait', p, R('portrait'))):
        w, h = d.size
        S = Image.new('RGB', (w * 3, h), 'white')
        tmp = sheet([(d, *r)], None, f'{C}/tmp.png', width=10 ** 6)
        for k in range(3):
            S.paste(tmp.crop((0, k * h, w, k * h + h)), (k * w, 0))
        dr = ImageDraw.Draw(S)
        for k, lab in enumerate(('рисунок', '3D', 'наложение')):
            dr.text((k * w + 12, 10), lab, fill=(70, 55, 50), font=font(24))
        S = S.resize((1500, int(h * 1500 / (w * 3))), Image.LANCZOS)
        webp(S, f'compare-{name}.webp')
    e = Image.open(f'{D}/expr-marat.webp').convert('RGB')
    webp(sheet([(e.crop((i * 400, 0, i * 400 + 400, 500)), *R(f'expr{i}')) for i in range(4)], [l for _, l in EXPRS], f'{C}/cmp-expr.png', width=1600), 'compare-expressions.webp')


def steps():
    cam = {'mode': 'orbit', 'yaw': 24, 'pitch': 7, 'dist': 6.0, 'fov': 24, 'follow': None, 'target': [0, 0.93, 0]}
    st = {'clip': 'stand', 'still': True, 'breath': False, 'expr': {'rest': 1}, 'look': ON_PLINTH, 'cam': cam}
    wk = {'clip': 'walk', 't': 1.9, 'still': True, 'expr': {'rest': 1}, 'look': {'plinth': False, 'ground': True, 'bg': True}, 'cam': {**cam, 'yaw': 50, 'follow': 'hips', 'followY': 0.95}}
    jobs = [{'name': 'rest', 'size': [480, 640], 'set': {**st, 'clip': 'turn', 'mode': 'skeleton'}},
            {'name': 'clay', 'size': [480, 640], 'set': {**st, 'clip': 'turn', 'mode': 'clay'}},
            {'name': 'full', 'size': [480, 640], 'set': {**st, 'clip': 'turn', 'mode': 'full'}},
            {'name': 'w-skel', 'size': [480, 640], 'set': {**wk, 'mode': 'skeleton'}},
            {'name': 'w-clay', 'size': [480, 640], 'set': {**wk, 'mode': 'clay'}},
            {'name': 'w-full', 'size': [480, 640], 'set': {**wk, 'mode': 'full'}}]
    out = shots('steps', jobs)
    S = Image.new('RGB', (480 * 3, 640 * 2), 'white')
    for i, j in enumerate(jobs):
        S.paste(Image.open(f"{out}/{j['name']}.png").convert('RGB'), ((i % 3) * 480, (i // 3) * 640))
    webp(S, 'steps.webp')


def stills():
    g = {'plinth': False, 'ground': True, 'bg': True, 'shadow': True}
    jobs = [{'name': 'cover', 'size': [900, 900], 'set': {'clip': 'stand', 'still': True, 'breath': False, 'mode': 'full', 'expr': {'rest': 1}, 'look': ON_PLINTH,
                                                         'cam': {'mode': 'orbit', 'yaw': 18, 'pitch': 7, 'dist': 5.3, 'fov': 24, 'follow': None, 'target': [0, 0.97, 0]}}},
            {'name': 'back', 'size': [600, 800], 'set': {'cam': {'yaw': 200, 'dist': 5.6}}},
            {'name': 'calm', 'size': [700, 760], 'set': {'clip': 'portrait', 'expr': {'calm': 1}, 'cam': {'mode': 'orbit', 'yaw': -20, 'pitch': 3, 'dist': 2.5, 'fov': 24, 'follow': 'head'}}},
            {'name': 'walk', 'size': [800, 800], 'set': {'clip': 'walk', 't': 2.3, 'still': True, 'expr': {'rest': 1}, 'look': g, 'cam': {'mode': 'orbit', 'yaw': 38, 'pitch': 7, 'dist': 5.6, 'fov': 24, 'follow': 'hips', 'followY': 0.95}}},
            {'name': 'wave', 'size': [800, 800], 'set': {'clip': 'wave', 't': 1.2, 'expr': {'joy': 1}, 'cam': {'yaw': -28}}},
            {'name': 'dance', 'size': [800, 800], 'set': {'clip': 'dance', 't': 3.6, 'expr': {'rest': 1}, 'cam': {'yaw': 12}}}]
    out = shots('stills', jobs)
    for j in jobs:
        webp(f"{out}/{j['name']}.png", j['name'] + '.webp')


def films(which=None):
    g = {'plinth': False, 'ground': True, 'bg': True, 'shadow': True}
    base = {'still': False, 'mode': 'full', 'breath': True, 'talk': False}
    ex = lambda t, sched: {[n for s, n in sched if s <= t][-1]: 1}
    F = []
    F.append(('turn', [560, 700], {**base, 'clip': 'stand', 'expr': {'rest': 1}, 'look': ON_PLINTH, 'cam': {'mode': 'orbit', 'yaw': 0, 'pitch': 7, 'dist': 5.9, 'fov': 24, 'follow': None, 'target': [0, 0.95, 0]}},
              [{'t': k / 24, 'dt': 1 / 24, 'cam_yaw': k * 3, 'expr': ex(k / 24, [(0, 'rest'), (1.8, 'calm'), (3.6, 'rest')])} for k in range(120)]))
    F.append(('walk', [640, 640], {**base, 'clip': 'walk', 't': 0, 'expr': {'calm': 1}, 'look': g, 'cam': {'mode': 'orbit', 'yaw': 32, 'pitch': 7, 'dist': 5.8, 'fov': 24, 'follow': 'hips', 'followY': 0.95}},
              [{'t': k / 24, 'dt': 1 / 24, 'expr': ex(k / 24, [(0, 'calm'), (1.6, 'rest')])} for k in range(95)]))
    F.append(('wave', [640, 640], {**base, 'clip': 'wave', 't': 0, 'expr': {'joy': 1}, 'talk': True, 'look': g, 'cam': {'mode': 'orbit', 'yaw': -22, 'pitch': 6, 'dist': 5.8, 'fov': 24, 'follow': 'hips', 'followY': 1.02}},
              [{'t': k / 24, 'dt': 1 / 24} for k in range(71)]))
    F.append(('dance', [640, 640], {**base, 'clip': 'dance', 't': 0, 'expr': {'rest': 1}, 'look': g, 'cam': {'mode': 'orbit', 'yaw': 14, 'pitch': 7, 'dist': 6.0, 'fov': 24, 'follow': 'hips', 'followY': 0.95}},
              [{'t': k / 24, 'dt': 1 / 24, 'expr': ex(k / 24, [(0, 'rest'), (1.5, 'calm'), (2.6, 'joy')])} for k in range(95)]))
    sched = [(0, 'calm'), (1.0, 'rest'), (2.2, 'surprise'), (3.3, 'sad'), (4.4, 'anger'), (5.4, 'joy'), (6.4, 'calm')]
    F.append(('face', [560, 560], {**base, 'clip': 'portrait', 't': 0, 'expr': {'calm': 1}, 'look': {**g, 'ground': False}, 'cam': {'mode': 'orbit', 'yaw': 14, 'pitch': 0, 'dist': 1.55, 'fov': 24, 'follow': 'head'}},
              [{'t': k / 24, 'dt': 1 / 24, 'expr': ex(k / 24, sched)} for k in range(170)]))
    F.append(('talk', [560, 560], {**base, 'clip': 'idle', 't': 0, 'expr': {'calm': 1}, 'talk': True, 'look': g, 'cam': {'mode': 'orbit', 'yaw': -18, 'pitch': -4, 'dist': 1.7, 'fov': 24, 'follow': 'head'}},
              [{'t': 2 + k / 24, 'dt': 1 / 24, 'talk': k < 110, 'expr': ex(k / 24, [(0, 'calm'), (4.6, 'rest')])} for k in range(140)]))
    for name, size, st, frames in F:
        if which and name not in which:
            continue
        out = shots('film-' + name, [{'name': name, 'size': size, 'set': st, 'frames': frames}])
        film(f'{out}/{name}', name + '.mp4')


if __name__ == '__main__':
    what = sys.argv[1:] or ['compare', 'steps', 'stills', 'films']
    if 'compare' in what: compare()
    if 'steps' in what: steps()
    if 'stills' in what: stills()
    if 'films' in what: films([a for a in what if a not in ('compare', 'steps', 'stills', 'films')] or None)
    for a in what:
        if a.startswith('film:'): films([a[5:]])
