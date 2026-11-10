"""Pictures and films of the page.  python3 make.py refs | compare | steps | expr | figure | films [names] | all
Every browser run goes through one of the shared locks."""
import json
import os
import random
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.basename(os.path.dirname(HERE))
CACHE = f'/home/user/cache/to3d-{FOLDER}'
PICS = os.path.join(HERE, '..', 'pics')
CFG = json.load(open(os.path.join(HERE, 'character.json')))
K, BACK = CFG['key'], CFG['back']
HS, HC = CFG['head']['s'], CFG['head']['c']          # the head on the figure (figure units; 1 unit = 2.5 mm)
S = 1 / 400
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)


def heavy(cmd):
    subprocess.run(['flock', f'/home/user/cache/heavy.{random.randrange(3)}.lock'] + cmd, check=True, cwd=HERE)


def shots(name, jobs):
    out = os.path.join(CACHE, name); os.makedirs(out, exist_ok=True)
    json.dump(jobs, open(os.path.join(out, 'jobs.json'), 'w'))
    heavy(['node', 'shots.mjs', os.path.join(out, 'jobs.json'), out])
    return out


def row(ims, labels=None, bg='#11121b', pad=10, h=None):
    h = h or max(i.height for i in ims)
    ims = [i.convert('RGB').resize((round(i.width * h / i.height), h), Image.LANCZOS) for i in ims]
    top = 34 if labels else 0
    W = sum(i.width for i in ims) + pad * (len(ims) + 1)
    o = Image.new('RGB', (W, h + top + pad), bg); d = ImageDraw.Draw(o); x = pad
    for k, i in enumerate(ims):
        o.paste(i, (x, top))
        if labels:
            d.text((x + i.width / 2, 17), labels[k], fill='#8d8a80', font=FONT, anchor='mm')
        x += i.width + pad
    return o


def save(im, name, q=88):
    im.convert('RGB').save(os.path.join(PICS, name), quality=q); print('pics/' + name)


# the bust's frame of the style's sheets: head units ×2, the head's middle at (300, 300) of 600×700
def bust_cam():
    px = 0.5 * HS * S
    return {'ortho': [0, HC[1] * S - 50 * px, 350 * px]}


def refs():
    out = os.path.join(CACHE, 'refs')
    subprocess.run(['python3', 'drawing.py', K, 'refs', out], check=True, cwd=HERE)
    a = []
    for f in sorted(os.listdir(out)):
        if f.endswith('.svg'):
            a += [os.path.join(out, f), os.path.join(out, f[:-4] + '.png')]
    heavy(['node', 'svg2png.mjs'] + a)


VIEWS = [('f', 0, 'анфас'), ('q', -45, 'три четверти'), ('s', -90, 'профиль')]


def compare():
    jobs = [{'name': v, 'size': [600, 700], 'set': {'floor': False, 'view': 'style', 'bg': {'col': BACK[0]}, 'figures': [{'clip': 'rest', 'yaw': yaw, 'ex': 'neutral'}], 'cam': bust_cam()}} for v, yaw, _ in VIEWS]
    out = shots('compare', jobs)
    R = os.path.join(CACHE, 'refs'); ims = []; ov = []
    for v, yaw, lab in VIEWS:
        a = Image.open(f'{R}/ref-{v}-{CFG["rest"]}.png').convert('RGB'); b = Image.open(f'{out}/{v}.png').convert('RGB')
        ims += [a, b]; ov.append(Image.blend(a, b, 0.5))
    save(row(ims, ['рисунок', '3D'] * 3, h=560), 'compare.jpg')
    save(row(ov, [l for _, _, l in VIEWS], h=560), 'overlay.jpg')


STREET = {'floor': True, 'bg': None, 'view': 'style'}
PLAIN = {'floor': False, 'bg': {'col': BACK[0]}, 'view': 'style'}


def figure():
    """The drawing's figure and the 3D in its frame (700×1000, figure units ×1.16, the ground at y = 930, x = 360)."""
    px = S / 1.16
    cam = {'ortho': [-10 * px, 430 * px, 500 * px]}
    jobs = [{'name': 'fig', 'size': [700, 1000], 'set': {**PLAIN, 'bg': {'col': '#11121b', 'disc': None}, 'figures': [{'clip': 'stand', 'yaw': CFG.get('figYaw', -42)}], 'cam': cam}},
            {'name': 'street', 'size': [700, 1000], 'set': {**STREET, 'figures': [{'clip': 'stand', 'yaw': CFG.get('figYaw', -42)}], 'cam': {'yaw': 0, 'pitch': 4, 'dist': 6.2, 'ty': 0.86, 'fov': 20, 'follow': False}}},
            {'name': 'back', 'size': [700, 1000], 'set': {**STREET, 'figures': [{'clip': 'stand', 'yaw': 150}], 'cam': {'yaw': 0, 'pitch': 4, 'dist': 6.2, 'ty': 0.86, 'fov': 20, 'follow': False}}},
            {'name': 'left', 'size': [700, 1000], 'set': {**STREET, 'figures': [{'clip': 'stand', 'yaw': 60}], 'cam': {'yaw': 0, 'pitch': 4, 'dist': 6.2, 'ty': 0.86, 'fov': 20, 'follow': False}}}]
    out = shots('figure', jobs)
    d = Image.open(os.path.join(HERE, f'../../../styles/s15-noir/pics/figure-{K}.png')).convert('RGB')
    a = Image.open(f'{out}/fig.png').convert('RGB')
    save(row([d, Image.open(f'{out}/street.png'), Image.blend(d, a, 0.5)], ['рисунок', '3D', 'наложение'], h=760), 'figure.jpg')
    save(row([Image.open(f'{out}/street.png'), Image.open(f'{out}/left.png'), Image.open(f'{out}/back.png')], ['к свету', 'от света', 'со спины'], h=760), 'sides.jpg')


def steps():
    cam = {'ortho': [0, 1.02, 0.66]}
    fg = [{'clip': 'rest', 'yaw': -38}]
    base = {'floor': False, 'bg': {'col': BACK[0]}, 'figures': fg, 'cam': cam}
    jobs = [{'name': '1', 'size': [520, 760], 'set': {**base, 'view': 'clay'}}, {'name': '0', 'size': [520, 760], 'set': {'view': 'bones'}},
            {'name': '2', 'size': [520, 760], 'set': {'view': 'flat'}},
            {'name': '3', 'size': [520, 760], 'set': {'view': 'noface', 'shadow': False}}, {'name': '4', 'size': [520, 760], 'set': {'view': 'noface', 'shadow': True}},
            {'name': '5', 'size': [520, 760], 'set': {'view': 'style'}}]
    out = shots('steps', jobs)
    save(row([Image.open(f'{out}/{n}.png') for n in '102345'], ['форма из плоскостей', 'скелет SOMA', 'краски', 'свет: чёрное с граней', 'падающие тени', 'лицо и кромка'], h=640), 'steps.jpg')


EXPRS = [('neutral', None), ('joy', 'радость'), ('surprise', 'удивление'), ('sad', 'грусть'), ('anger', 'злость')]


def expr():
    c = bust_cam()
    jobs = [{'name': e, 'size': [600, 700], 'set': {**PLAIN, 'figures': [{'clip': 'rest', 'yaw': -38, 'ex': e}], 'cam': c}} for e, _ in EXPRS]
    jobs += [{'name': e + '-f', 'size': [600, 700], 'set': {**PLAIN, 'figures': [{'clip': 'rest', 'yaw': 0, 'ex': e}], 'cam': c}} for e, _ in EXPRS]
    out = shots('expr', jobs)
    labs = [CFG['restRu']] + [l for _, l in EXPRS[1:]]
    save(row([Image.open(f'{out}/{e}.png') for e, _ in EXPRS], labs, h=520), 'expr.jpg')
    save(row([Image.open(f'{out}/{e}-f.png') for e, _ in EXPRS], labs, h=520), 'expr-front.jpg')


def film(name, size, st, frames, fps=24):
    out = shots('film-' + name, [{'name': 'f', 'size': size, 'set': st, 'frames': frames}])
    heavy(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', f'{out}/f/f%04d.png', '-c:v', 'libx264', '-crf', '25', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
           os.path.join(PICS, name + '.mp4')])
    # a strip of moments to look at
    fs = sorted(os.listdir(f'{out}/f')); pick = [fs[int(i * (len(fs) - 1) / 7)] for i in range(8)]
    row([Image.open(f'{out}/f/{f}') for f in pick], h=360).save(os.path.join(CACHE, f'strip-{name}.jpg'), quality=85)
    print('pics/' + name + '.mp4')


def films(*names):
    F = CFG['films']
    for n in (names or F.keys()):
        f = F[n]; fps = 24; N = round(f['sec'] * fps)
        fr = []
        for i in range(N):
            o = {'t': i / fps, 'dt': 1 / fps}
            if f.get('turn'):
                o['yaw'] = f.get('yaw0', 0) - 360 * i / N
            for t0, key, val in f.get('keys', []):
                if abs(t0 - i / fps) < 0.5 / fps:
                    o[key] = val
            fr.append(o)
        fg = {'clip': f['clip'], 'yaw': f.get('yaw0', 0), 'live': True, 'talk': bool(f.get('talk')), 'ex': f.get('ex', 'neutral')}
        film(n, f.get('size', [560, 720]), {**STREET, 'figures': [fg], 'cam': f['cam']}, fr, fps)


def all():
    refs(); compare(); figure(); steps(); expr(); films()


if __name__ == '__main__':
    os.makedirs(PICS, exist_ok=True)
    for a in sys.argv[1:]:
        globals()[a.split(':')[0]](*a.split(':')[1:])
