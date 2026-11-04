"""Pictures and films of Р8 (Савелий Петрович, С6 → 3D). python3 make.py [compare] [steps] [moods] [films] [turn] [walk] …
Renders go through the page (tools/web/view.html?shots) by shots.mjs; work files in /home/user/cache/to3d-r8-s6-savely."""
import json, os, subprocess, sys, math, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PICS = os.path.join(HERE, '..', 'pics')
CACHE = '/home/user/cache/to3d-r8-s6-savely'
STYLE = os.path.join(REPO, 'styles', 's6-symbolic', 'pics')
os.makedirs(PICS, exist_ok=True)
FONT = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
D = math.pi / 180


def shots(jobs, name):
    d = os.path.join(CACHE, 'r', name)
    os.makedirs(d, exist_ok=True)
    jf = os.path.join(d, 'jobs.json')
    json.dump(jobs, open(jf, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), jf, d], check=True)
    return d


def jpg(img, name, q=88):
    img.convert('RGB').save(os.path.join(PICS, name), quality=q)


def label(img, text, x, y, size=24, fill=(170, 150, 150)):
    dr = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, size)
    w = dr.textlength(text, font=f)
    dr.text((x - w / 2, y), text, font=f, fill=fill)


def vignette(img, v=.4):
    """The drawing's vignette over a whole sheet (the tiles are drawn without their own)."""
    w, h = img.size
    y, x = np.mgrid[0:h, 0:w]
    d = np.hypot((x / w - .5) / .75, (y / h - .5) / .75)
    k = 1 - v * np.clip((d - .55) / .45, 0, 1)
    return Image.fromarray((np.asarray(img.convert('RGB')).astype(float) * k[..., None]).astype('uint8'))


def ortho(k, cx, feetY):
    return {'type': 'ortho', 'k': k, 'cx': cx, 'feetY': feetY}


PLATE = lambda horY, fb=.09: {'horY': horY, 'fbH': fb}
DRAWN = {'stat': 'drawn', 'mood': None, 'snap': True, 'breath': False, 'talk': False, 'motion': None}
MASK = {'world': False, 'rim': False, 'signs': False, 'grain': False}
TURN_YAWS = [0, 45, 90, 135, 180]


def edges(a):
    A = np.asarray(a.convert('L')).astype(float)
    m = A < 128
    e = np.zeros_like(m)
    e[:-1] |= m[:-1] != m[1:]; e[:, :-1] |= m[:, :-1] != m[:, 1:]
    e[1:] |= e[:-1].copy()
    return Image.fromarray((e * 255).astype('uint8'))


def overlay(drawing_sil, render_sil):
    """The drawing's outline (red) over the 3D's silhouette (pale)."""
    r = render_sil.convert('L')
    R = np.asarray(r).astype(float)
    pale = np.where(R[..., None] < 128, np.array([120, 128, 150]), np.array([236, 232, 226])).astype('uint8')
    out = Image.fromarray(pale)
    out.paste(Image.new('RGB', out.size, (215, 30, 60)), (0, 0), edges(drawing_sil))
    return out


# ------------------------------------------------------------------ the drawing's views side by side and overlaid

def compare():
    dsil = os.path.join(CACHE, 'drawing')
    if not os.path.exists(os.path.join(dsil, 'turn.png')):
        subprocess.run(['python3', os.path.join(HERE, 'drawing.py'), dsil], check=True)
        subprocess.run(['node', os.path.join(HERE, 'svg2png.mjs'), dsil + '/turn.svg', dsil + '/turn.png', dsil + '/full.svg', dsil + '/full.png'], check=True)
    jobs = []
    for i, yw in enumerate(TURN_YAWS):
        base = dict(DRAWN, heading=yw * D, view=ortho(3.2, 150, 760 * .86), lightDir=[1, .3])
        jobs.append({'name': 'turn%d' % i, 'size': [300, 760], 'set': dict(base, plate=PLATE(.86, 70 / 760), look={}, vign=0)})
        jobs.append({'name': 'tmask%d' % i, 'size': [300, 760], 'set': dict(base, plate=None, look=MASK)})
    base = dict(DRAWN, heading=70 * D, view=ortho(3.55, 320, 860 * .9), lightDir=[1, .3])
    jobs.append({'name': 'full', 'size': [640, 860], 'set': dict(base, plate=PLATE(.66, 120 / 860), look={})})
    jobs.append({'name': 'fmask', 'size': [640, 860], 'set': dict(base, plate=None, look=MASK)})
    d = shots(jobs, 'compare')
    turn3d = Image.new('RGB', (1500, 760)); tmask = Image.new('RGB', (1500, 760))
    for i in range(5):
        turn3d.paste(Image.open(f'{d}/turn{i}.png').convert('RGB'), (300 * i, 0))
        tmask.paste(Image.open(f'{d}/tmask{i}.png').convert('RGB'), (300 * i, 0))
    dr = Image.open(os.path.join(STYLE, 'turn-savely.jpg')).convert('RGB')
    side = Image.new('RGB', (1500, 760 * 2 + 10), (20, 14, 22)); side.paste(dr, (0, 0)); side.paste(vignette(turn3d, .35), (0, 770))
    jpg(side, 'turn-side.jpg')
    jpg(overlay(Image.open(dsil + '/turn.png'), tmask), 'turn-overlay.jpg')
    full = Image.open(f'{d}/full.png').convert('RGB')
    drf = Image.open(os.path.join(STYLE, 'full-savely.jpg')).convert('RGB')
    s2 = Image.new('RGB', (640 * 3 + 20, 860), (20, 14, 22)); s2.paste(drf, (0, 0)); s2.paste(full, (650, 0))
    hero = os.path.join(PICS, 'hero.jpg')
    if os.path.exists(hero): s2.paste(Image.open(hero).convert('RGB'), (1300, 0))
    jpg(s2, 'full-side.jpg')
    jpg(overlay(Image.open(dsil + '/full.png'), Image.open(f'{d}/fmask.png')), 'full-overlay.jpg')


# ------------------------------------------------------------------ the hero shot and the steps

HERO = {'stat': 'rest', 'mood': 'watch', 'snap': True, 'breath': True, 'talk': False, 'motion': None, 'heading': 1.22,
        'lamp': [0.95, 0, -1.7], 'plate': None, 'lightDir': None, 'view': None,
        'cam': {'yaw': -0.12, 'pitch': -0.03, 'dist': 4.3, 'h': .9, 'fov': 33}}


def steps():
    W, H = 480, 680
    looks = [
        ('формы рисунка на скелете SOMA', dict(HERO, mood=None, look={'shaded': True, 'world': False, 'grain': False, 'skeleton': True, 'signs': False})),
        ('поза рисунка', dict(HERO, look={'shaded': True, 'world': False, 'grain': False, 'signs': False})),
        ('одна форма', dict(HERO, look={'world': False, 'rim': False, 'signs': False, 'grain': False})),
        ('+ кромка света', dict(HERO, look={'world': False, 'signs': False, 'grain': False})),
        ('+ тёплый знак', dict(HERO, look={'world': False, 'grain': False})),
        ('+ фонарь, туман, зерно', dict(HERO, look={})),
    ]
    jobs = [{'name': 's%d' % i, 'size': [W, H], 'warm': .5, 'set': s} for i, (_, s) in enumerate(looks)]
    jobs.append({'name': 'hero', 'size': [640, 860], 'warm': .5, 'set': dict(HERO, look={})})
    d = shots(jobs, 'steps')
    sheet = Image.new('RGB', (W * 3 + 20, (H + 50) * 2), (24, 18, 26))
    for i, (lab, _) in enumerate(looks):
        x, y = (i % 3) * (W + 10), (i // 3) * (H + 50)
        sheet.paste(Image.open(f'{d}/s{i}.png').convert('RGB'), (x, y))
        label(sheet, lab, x + W / 2, y + H + 10, 26, (215, 190, 175))
    jpg(sheet, 'steps.jpg')
    jpg(Image.open(f'{d}/hero.png'), 'hero.jpg')


# ------------------------------------------------------------------ moods: the posture is the expression

MOOD_ORDER = ['watch', 'grumpy', 'sad', 'glad', 'surprised', 'angry']
MOOD_YAW = {'watch': 70, 'grumpy': 72, 'sad': 64, 'glad': 62, 'surprised': 66, 'angry': 72}


def moods():
    poses = json.load(open(os.path.join(HERE, 'web', 'data', 'poses.json')))
    W, H = 340, 700
    jobs = []
    for i, k in enumerate(MOOD_ORDER):
        jobs.append({'name': 'm%d' % i, 'size': [W, H], 'set': {'stat': 'rest', 'mood': k, 'snap': True, 'breath': False, 'motion': None,
                     'heading': MOOD_YAW[k] * D, 'view': ortho(3.3, W / 2, H * .84), 'plate': PLATE(.84, 80 / 700), 'lightDir': [1, .3], 'look': {}, 'vign': 0}})
    d = shots(jobs, 'moods')
    sheet = Image.new('RGB', (W * len(MOOD_ORDER), H + 50), (28, 20, 32))
    for i, k in enumerate(MOOD_ORDER):
        sheet.paste(Image.open(f'{d}/m{i}.png').convert('RGB'), (W * i, 0))
        label(sheet, poses['moods'][k]['label'], W * i + W / 2, H + 8, 26, (215, 190, 175))
    jpg(vignette(sheet, .3), 'moods.jpg')


# ------------------------------------------------------------------ films

def film(name, size, setv, frames, fps=30, keep=None, crf=27):
    d = shots([{'name': name, 'size': size, 'set': setv, 'frames': frames, 'warm': .5}], 'film-' + name)
    out = os.path.join(PICS, name + '.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', f'{d}/{name}/f%04d.png', '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', str(crf), '-preset', 'slow', '-movflags', '+faststart', out], check=True)
    n = len(frames) if isinstance(frames, list) else frames
    k = keep if keep is not None else n // 2
    jpg(Image.open(f'{d}/{name}/f{k:04d}.png'), name + '-frame.jpg')
    print(name, os.path.getsize(out) // 1024, 'KB')


def film_turn():
    n = 210
    frames = [{'cam': {'yaw': -0.12 + 2 * math.pi * i / n}} for i in range(n)]
    film('turn', [640, 800], dict(HERO, cam=dict(HERO['cam'], dist=4.2, h=.95)), frames, keep=0)


def film_walk():
    s = {'motion': 'walk', 't': 0, 'loop': True, 'mood': 'plain', 'snap': True, 'breath': True, 'talk': False, 'heading': math.pi / 2,
         'position': [-3.0, 0, 0], 'lamp': [0.6, 0, -1.3], 'lightDir': None, 'plate': None, 'view': None,
         'cam': {'yaw': 0.18, 'pitch': 0.0, 'dist': 3.7, 'h': .85, 'fov': 34, 'smooth': 2.5}, 'look': {}}
    film('walk', [720, 720], s, 240, keep=120)


def film_motion(mid, n, mood='plain', heading=1.15, cam=None, lamp=(0.95, 0, -1.7), keep=None):
    s = {'motion': mid, 't': 0, 'loop': False, 'mood': mood, 'snap': True, 'breath': True, 'talk': False, 'heading': heading,
         'position': [0, 0, 0], 'lamp': list(lamp), 'lightDir': None, 'plate': None, 'view': None,
         'cam': cam or {'yaw': -0.1, 'pitch': 0.0, 'dist': 3.6, 'h': .9, 'fov': 34, 'smooth': 3}, 'look': {}}
    film(mid, [720, 720], s, n, keep=keep)


def film_life():
    """Standing at the lamp: breathing; moods one after another, flowing; a few words to himself."""
    plan = [(0, 'watch'), (3.2, 'grumpy'), (6.0, 'glad'), (8.4, 'sad'), (11.0, 'watch')]
    n = 13 * 30
    frames = []
    for i in range(n):
        t = i / 30
        f = {}
        for t0, m in plan:
            if abs(t - t0) < 1e-6 or (i > 0 and (i - 1) / 30 < t0 <= t):
                f['mood'] = m
        if abs(t - 3.6) < 1 / 60: f['talk'] = True
        if abs(t - 6.0) < 1 / 60: f['talk'] = False
        f['cam'] = {'yaw': -0.12 + 0.5 * math.sin(i / n * math.pi) ** 2 * 0.6}
        frames.append(f)
    film('life', [640, 800], dict(HERO, mood='watch', cam=dict(HERO['cam'], dist=3.6, h=1.0)), frames, keep=60)


if __name__ == '__main__':
    what = sys.argv[1:] or ['compare', 'steps', 'moods']
    if 'compare' in what: compare()
    if 'steps' in what: steps()
    if 'moods' in what: moods()
    if 'turn' in what or 'films' in what: film_turn()
    if 'walk' in what or 'films' in what: film_walk()
    if 'life' in what or 'films' in what: film_life()
    for mid, n, mood in (('bow', 89, 'plain'), ('wave', 89, 'plain'), ('stomp', 89, 'plain'), ('sit', 119, 'plain')):
        if mid in what or 'films' in what: film_motion(mid, n + 20, mood)
