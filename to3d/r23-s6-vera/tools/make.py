"""Pictures and films of a С6 character in 3D. python3 make.py [compare] [steps] [moods] [expr] [films] [turn] [walk] [life] [<motion>] …
Renders go through the page (tools/web/view.html?shots) by shots.mjs — a browser drawing frames: a heavy run, taken
through one of the shared locks. Work files in /home/user/cache/to3d-<folder>. What is the character's own is in
character.py."""
import json, os, subprocess, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import character as C   # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PICS = os.path.join(HERE, '..', 'pics')
CACHE = '/home/user/cache/to3d-' + C.FOLDER
STYLE = os.path.join(REPO, 'styles', 's6-symbolic', 'pics')
os.makedirs(PICS, exist_ok=True)
FONT = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
D = math.pi / 180


def heavy(cmd):
    """Heavy runs take turns: at most three at once on the machine (the brief's rule). A free lock is taken if there
    is one; otherwise wait for one of the three."""
    locks = ['/home/user/cache/heavy.%d.lock' % i for i in random.sample(range(3), 3)]
    for lk in locks:
        r = subprocess.run(['flock', '-n', '-E', '75', lk] + cmd)
        if r.returncode != 75:
            r.check_returncode()
            return
    subprocess.run(['flock', locks[0]] + cmd, check=True)


def shots(jobs, name):
    d = os.path.join(CACHE, 'r', name)
    os.makedirs(d, exist_ok=True)
    jf = os.path.join(d, 'jobs.json')
    json.dump(jobs, open(jf, 'w'))
    heavy(['node', os.path.join(HERE, 'shots.mjs'), jf, d])
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


PLATE = lambda horY, fb=.09, op=.4: {'horY': horY, 'fbH': fb, 'fbOp': op}
DRAWN = {'stat': 'drawn', 'mood': None, 'snap': True, 'breath': False, 'talk': False, 'motion': None, 'position': [0, 0, 0]}
MASK = {'world': False, 'rim': False, 'signs': False, 'grain': False}
TURN_YAWS = [0, 45, 90, 135, 180]
BG = (20, 16, 26)


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


def miss(drawing_sil, render_sil):
    """How far the two silhouettes differ: the share of the drawing's area that is not common."""
    a = np.asarray(drawing_sil.convert('L')) < 128; b = np.asarray(render_sil.convert('L')) < 128
    return float((a ^ b).sum() / a.sum())


def drawing_sils():
    dsil = os.path.join(CACHE, 'drawing')
    if not os.path.exists(os.path.join(dsil, 'turn.png')):
        subprocess.run(['python3', os.path.join(HERE, 'drawing.py'), dsil], check=True)
        names = ['turn', 'full'] + (['expr'] if getattr(C, 'EXPR', None) else [])
        heavy(['node', os.path.join(HERE, 'svg2png.mjs')] + [x for n in names for x in (f'{dsil}/{n}.svg', f'{dsil}/{n}.png')])
    return dsil


# ------------------------------------------------------------------ the drawing's views side by side and overlaid

def compare():
    dsil = drawing_sils()
    T, F = C.TURN, C.FULL
    jobs = []
    for i, yw in enumerate(TURN_YAWS):
        base = dict(DRAWN, heading=yw * D, view=ortho(T['k'], 150, 760 * .86), lightDir=[T['light'], .3])
        jobs.append({'name': 'turn%d' % i, 'size': [300, 760], 'set': dict(base, plate=PLATE(.86, 70 / 760), look={}, vign=0, grain=.045)})
        jobs.append({'name': 'tmask%d' % i, 'size': [300, 760], 'set': dict(base, plate=None, look=MASK)})
    base = dict(DRAWN, heading=F['yaw'] * D, view=ortho(F['k'], 640 * F['x'], 860 * .9), lightDir=[F['light'], .3])
    jobs.append({'name': 'full', 'size': [640, 860], 'set': dict(base, plate=PLATE(.66 + 10 / 860, 120 / 860, .45), look={}, contactR=F.get('foot'))})
    jobs.append({'name': 'fmask', 'size': [640, 860], 'set': dict(base, plate=None, look=MASK)})
    d = shots(jobs, 'compare')
    turn3d = Image.new('RGB', (1500, 760)); tmask = Image.new('RGB', (1500, 760))
    for i in range(5):
        turn3d.paste(Image.open(f'{d}/turn{i}.png').convert('RGB'), (300 * i, 0))
        tmask.paste(Image.open(f'{d}/tmask{i}.png').convert('RGB'), (300 * i, 0))
    dr = Image.open(os.path.join(STYLE, T['pic'])).convert('RGB')
    side = Image.new('RGB', (1500, 760 * 2 + 10), BG); side.paste(dr, (0, 0)); side.paste(vignette(turn3d, .35), (0, 770))
    jpg(side, 'turn-side.jpg')
    jpg(overlay(Image.open(dsil + '/turn.png'), tmask), 'turn-overlay.jpg')
    full = Image.open(f'{d}/full.png').convert('RGB')
    drf = Image.open(os.path.join(STYLE, F['pic'])).convert('RGB')
    s2 = Image.new('RGB', (640 * 3 + 20, 860), BG); s2.paste(drf, (0, 0)); s2.paste(full, (650, 0))
    hero = os.path.join(PICS, 'hero.jpg')
    if os.path.exists(hero): s2.paste(Image.open(hero).convert('RGB'), (1300, 0))
    jpg(s2, 'full-side.jpg')
    fm = Image.open(f'{d}/fmask.png')
    jpg(overlay(Image.open(dsil + '/full.png'), fm), 'full-overlay.jpg')
    print('silhouettes differ: turn %.1f %%, full %.1f %%' % (100 * miss(Image.open(dsil + '/turn.png'), tmask), 100 * miss(Image.open(dsil + '/full.png'), fm)))


# ------------------------------------------------------------------ the hero shot and the steps

def hero_set():
    H = C.HERO
    return {'stat': 'rest', 'mood': H['mood'], 'snap': True, 'breath': True, 'glance': False, 'talk': False, 'motion': None, 'heading': H['heading'],
            'position': [0, 0, 0], 'lamp': H['lamp'], 'plate': None, 'lightDir': None, 'view': None, 'cam': dict(H['cam'])}


def steps():
    W, H = 480, 680
    HERO = hero_set()
    looks = [
        ('формы рисунка на скелете SOMA', dict(HERO, mood=None, look={'shaded': True, 'world': False, 'grain': False, 'skeleton': True, 'signs': False})),
        ('поза рисунка', dict(HERO, look={'shaded': True, 'world': False, 'grain': False, 'signs': False})),
        ('одна форма', dict(HERO, look={'world': False, 'rim': False, 'signs': False, 'grain': False})),
        ('+ кромка света', dict(HERO, look={'world': False, 'signs': False, 'grain': False})),
        ('+ знак', dict(HERO, look={'world': False, 'grain': False})),
        ('+ ' + C.WORLD_LABEL, dict(HERO, look={})),
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

def moods():
    order = C.MOOD_SHEET
    W, H = int(2040 / len(order)), 700
    k = getattr(C, 'MOOD_K', 3.3)
    jobs = []
    for i, m in enumerate(order):
        jobs.append({'name': 'm%d' % i, 'size': [W, H], 'set': {'stat': 'rest', 'mood': m, 'snap': True, 'breath': False, 'motion': None, 'position': [0, 0, 0],
                     'heading': C.MOODS[m]['yaw'] * D, 'view': ortho(k, W / 2 + C.MOODS[m].get('dx', 0), H * .84), 'plate': PLATE(.84, 80 / 700), 'lightDir': [C.TURN['light'], .3], 'look': {}, 'vign': 0, 'grain': .045}})
    d = shots(jobs, 'moods')
    sheet = Image.new('RGB', (W * len(order), H + 50), BG)
    for i, m in enumerate(order):
        sheet.paste(Image.open(f'{d}/m{i}.png').convert('RGB'), (W * i, 0))
        label(sheet, C.MOODS[m]['label'], W * i + W / 2, H + 8, 26, (215, 190, 175))
    jpg(vignette(sheet, .3), 'moods.jpg')


def expr():
    """The style's expression sheet and the 3D in the same layout, and their silhouettes overlaid."""
    E = C.EXPR
    dsil = drawing_sils()
    n = len(E['order'])
    W, H = 1500, 720
    base = {'stat': 'rest', 'snap': True, 'breath': False, 'motion': None, 'position': [0, 0, 0], 'lightDir': [1, .3], 'pal': E['pal']}
    jobs = []
    for kind, extra in (('e', dict(plate=PLATE(.84, 80 / 720, .35), look={}, vign=0, contactR=E['foot'])), ('em', dict(plate=None, look=MASK))):
        for i, m in enumerate(E['order']):
            # one sheet-wide picture per figure: big gestures cross their column
            jobs.append({'name': '%s%d' % (kind, i), 'size': [W, H], 'set': dict(base, mood=m, heading=C.MOODS[m]['yaw'] * D,
                         view=ortho(E['k'], W * (i + .5) / n + E['xs'][i], H * .84), **extra)})
    d = shots(jobs, 'expr')
    sheet = None; mask = np.full((H, W), 255, np.uint8)
    for i in range(n):
        a = np.asarray(Image.open(f'{d}/e{i}.png').convert('RGB')).astype(int)
        m = np.asarray(Image.open(f'{d}/em{i}.png').convert('L'))
        if sheet is None:
            sheet = a.copy(); bg = a
        # what this figure changed on the empty sheet
        col = slice(int(W * i / n), int(W * (i + 1) / n))
        ch = np.zeros((H, W), bool); ch[:, col] = True
        fig = (m < 128)
        fig_near = np.asarray(Image.fromarray((fig * 255).astype('uint8')).resize((W, H))) > 0
        # take the figure's own column wholly, and outside it only where the figure reaches
        grow = np.zeros_like(fig_near)
        ys, xs = np.nonzero(fig_near)
        if len(xs):
            grow[max(ys.min() - 6, 0):ys.max() + 30, max(xs.min() - 6, 0):xs.max() + 7] = True
        take = ch | grow
        sheet[take] = a[take]
        mask[fig] = 0
    sheet = Image.fromarray(sheet.astype('uint8'))
    for i, m in enumerate(E['order']):
        label(sheet, E['labels'][i], W * (i + .5) / n, H * .94 - 22, 26, (58, 66, 88))
    dr = Image.open(os.path.join(STYLE, E['pic'])).convert('RGB')
    side = Image.new('RGB', (W, H * 2 + 10), BG); side.paste(dr, (0, 0)); side.paste(vignette(sheet, .3), (0, H + 10))
    jpg(side, 'expr-side.jpg')
    mk = Image.fromarray(mask)
    jpg(overlay(Image.open(dsil + '/expr.png'), mk), 'expr-overlay.jpg')
    print('expression silhouettes differ: %.1f %%' % (100 * miss(Image.open(dsil + '/expr.png'), mk)))


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
    n = 180
    HERO = hero_set()
    y0 = HERO['cam']['yaw']
    frames = [{'cam': {'yaw': y0 + 2 * math.pi * i / n}} for i in range(n)]
    film('turn', [640, 800], dict(HERO, cam=dict(HERO['cam'], dist=HERO['cam']['dist'] - .1), look={}), frames, keep=0)


def film_walk():
    Wk = C.WALK
    s = {'motion': Wk['motion'], 't': 0, 'loop': True, 'mood': Wk['mood'], 'snap': True, 'breath': True, 'glance': False, 'talk': False, 'heading': Wk['heading'],
         'position': Wk['position'], 'lamp': Wk['lamp'], 'lightDir': None, 'plate': None, 'view': None, 'cam': dict(Wk['cam']), 'look': {}}
    film('walk', [720, 720], s, Wk['frames'], keep=Wk['frames'] // 2)


def film_motion(mid, n, mood, opt=None):
    opt = opt or {}
    H = C.HERO
    s = {'motion': mid, 't': 0, 'loop': bool(opt.get('loop')), 'mood': mood, 'snap': True, 'breath': True, 'glance': False, 'talk': False, 'heading': opt.get('heading', H['heading']),
         'position': opt.get('position', [0, 0, 0]), 'lamp': opt.get('lamp', H['lamp']), 'lightDir': None, 'plate': None, 'view': None,
         'cam': opt.get('cam') or dict(H['cam'], dist=3.9, h=.9, fov=34, smooth=3), 'look': {}}
    film(mid, [720, 720], s, n, keep=opt.get('keep'))


def strip(mid, mood, n=8, opt=None):
    """A look at a motion before filming it: n moments in a row (work file, not for the page)."""
    opt = opt or {}
    H = C.HERO
    s = {'motion': mid, 't': 0, 'loop': False, 'mood': mood, 'snap': True, 'breath': True, 'glance': False, 'talk': False, 'heading': opt.get('heading', H['heading']),
         'position': [0, 0, 0], 'lamp': H['lamp'], 'lightDir': None, 'plate': None, 'view': None, 'grain': 0,
         'cam': dict(H['cam'], dist=4.4, h=.9, fov=34, smooth=30, yaw=opt.get('yaw', H['cam']['yaw'])), 'look': {}}
    L = json.load(open(os.path.join(HERE, 'web', 'data', 'motions', mid + '.json')))['frames']
    d = shots([{'name': mid, 'size': [300, 400], 'set': s, 'frames': n, 'dt': (L - 1) / 30 / n}], 'strip-' + mid)
    sheet = Image.new('RGB', (300 * n, 400))
    for i in range(n):
        sheet.paste(Image.open(f'{d}/{mid}/f{i:04d}.png').convert('RGB'), (300 * i, 0))
    sheet.save(os.path.join(CACHE, 'strip-' + mid + '.jpg'), quality=85)


def film_life():
    """Standing in the light: breathing, looking about; moods one after another, flowing; a few words."""
    L = C.LIFE
    n = int(L['seconds'] * 30)
    HERO = hero_set()
    y0 = HERO['cam']['yaw']
    frames = []
    for i in range(n):
        t = i / 30
        f = {}
        for t0, m in L['plan']:
            if (i == 0 and t0 == 0) or (i > 0 and (i - 1) / 30 < t0 <= t):
                f['mood'] = m
        if L.get('talk'):
            if (i - 1) / 30 < L['talk'][0] <= t: f['talk'] = True
            if (i - 1) / 30 < L['talk'][1] <= t: f['talk'] = False
        f['cam'] = {'yaw': y0 + 0.3 * math.sin(i / n * math.pi) ** 2}
        frames.append(f)
    film('life', [640, 800], dict(HERO, glance=True, mood=L['plan'][0][1], cam=dict(HERO['cam'], dist=HERO['cam']['dist'] - .7, h=1.0), look={}), frames, keep=L.get('keep', 60))


if __name__ == '__main__':
    what = sys.argv[1:] or ['compare', 'steps', 'moods']
    if 'compare' in what: compare()
    if 'steps' in what: steps()
    if 'moods' in what: moods()
    if 'expr' in what: expr()
    if 'turn' in what or 'films' in what: film_turn()
    if 'walk' in what or 'films' in what: film_walk()
    if 'life' in what or 'films' in what: film_life()
    for a in what:
        if a.startswith('strip:'):
            _, mid, mood = a.split(':'); strip(mid, mood)
    for f in C.FILMS:
        if f[0] in what or 'films' in what: film_motion(*f)
