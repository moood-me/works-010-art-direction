"""Every picture and film of the page.  python3 make.py [stills] [films] [steps]
Renders through shots.mjs (headless Chromium, the page tools/web/view.html), compares with compare.py, encodes mp4 with
ffmpeg, writes webp/mp4 into ../pics. Work files in /home/user/cache/to3d-r34-s11-marat/.
As Р11's make.py, with Марат's cameras."""
import json
import os
import subprocess
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
C = '/home/user/cache/to3d-r34-s11-marat'
PICS = os.path.join(HERE, '..', 'pics')
D = os.path.join(HERE, '..', '..', '..', 'styles', 's11-rubberhose', 'pics')
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
S = 0.004
os.makedirs(C, exist_ok=True)


def shots(name, jobs):
    p = f'{C}/{name}.json'
    json.dump(jobs, open(p, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), p, f'{C}/{name}'], check=True, env=ENV)
    return f'{C}/{name}'


def webp(src, dst, q=84):
    Image.open(src).convert('RGB').save(os.path.join(PICS, dst), 'WEBP', quality=q, method=6)


def film(folder, dst, fps=24, crf=26):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', f'{folder}/f%04d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-crf', str(crf), '-preset', 'slow', '-movflags', '+faststart', os.path.join(PICS, dst)], check=True)


# the drawing's cameras: turnaround-marat (scale 1.14, soles at y 800, cells 500 px; the body's middle is the
# drawing's x = 4) and expressions-marat (heads at 1.3, drawn without the figure's head scale 1.08; centre 22 px higher)
FEET, TS, XC, HS = 516, 1.14, 4, 1.08
TURN = {'mode': 'ortho', 'pitch': 0, 'target': [0, (800 - 450) / TS * S, 0], 'ortho': {'h': 900 / TS * S}}
ES = 1.3 / HS
VIEWS = [('front', 0, XC * S), ('q', -31.5, 0.035), ('side', -72, 0.08)]
EXPRS = ['neutral', 'joy', 'surprise', 'sad', 'angry']
HEADY = (FEET + 4) * S                       # the head's centre over the floor
BODY = {'mode': 'persp', 'pitch': 5, 'fov': 24, 'follow': True, 'followY': 1.2}
FACE = {'mode': 'persp', 'pitch': -2, 'dist': 3.6, 'fov': 24, 'follow': True, 'followHead': True}


def stills():
    jobs = [{'name': v, 'size': [500, 900], 'set': {'clip': 'stand', 'still': True, 'expr': {'neutral': 1}, 'mode': 'film', 'cam': {**TURN, 'yaw': y, 'ortho': {**TURN['ortho'], 'dx': dx}}}} for v, y, dx in VIEWS]
    jobs += [{'name': 'ex-' + e, 'size': [300, 420], 'set': {'expr': {e: 1}, 'still': True, 'cam': {'mode': 'ortho', 'yaw': -17.2, 'pitch': 0, 'target': [0, HEADY - 47 / ES * S, 0.03], 'ortho': {'h': 420 / ES * S, 'dx': 0}}}} for e in EXPRS]
    jobs += [{'name': 'bw', 'size': [500, 900], 'set': {'expr': {'neutral': 1}, 'bw': True, 'cam': {**TURN, 'yaw': -31.5, 'ortho': {**TURN['ortho'], 'dx': 0.035}}}}]
    jobs += [{'name': 'cover', 'size': [900, 900], 'set': {'bw': False, 'expr': {'neutral': 1}, 'cam': {'mode': 'persp', 'yaw': -24, 'pitch': 6, 'dist': 6.5, 'fov': 24, 'follow': False, 'target': [0, 1.2, 0]}}}]
    jobs += [{'name': 'portrait', 'size': [700, 760], 'set': {'expr': {'neutral': 1}, 'cam': {'mode': 'persp', 'yaw': -22, 'pitch': 4, 'dist': 3.6, 'fov': 24, 'follow': False, 'target': [0, 1.95, 0]}}}]
    jobs += [{'name': 'back', 'size': [500, 900], 'set': {'cam': {**TURN, 'yaw': 150, 'ortho': {**TURN['ortho'], 'dx': 0}}}}]
    out = shots('stills', jobs)
    cmp = os.path.join(HERE, 'compare.py')
    subprocess.run(['python3', cmp, f'{C}/cmp-turn.jpg', f'{D}/turnaround-marat.jpg', '0,0,500,900;500,0,1000,900;1000,0,1500,900',
                    *[f'{out}/{v}.png' for v, _, _ in VIEWS], '--labels=анфас,три четверти,профиль', '--width=1500'], check=True)
    subprocess.run(['python3', cmp, f'{C}/cmp-expr.jpg', f'{D}/expressions-marat.jpg', ';'.join(f'{i * 300},0,{i * 300 + 300},420' for i in range(5)),
                    *[f'{out}/ex-{e}.png' for e in EXPRS], '--width=1500'], check=True)
    webp(f'{C}/cmp-turn.jpg', 'compare-turn.webp'); webp(f'{C}/cmp-expr.jpg', 'compare-expressions.webp')
    # black-and-white film (the drawing's black-and-white sheet has only the first four of the cast): colour beside it
    pair = Image.new('RGB', (1000, 900), 'white'); pair.paste(Image.open(f'{out}/q.png').convert('RGB'), (0, 0)); pair.paste(Image.open(f'{out}/bw.png').convert('RGB'), (500, 0))
    pair.save(f'{C}/bw-pair.png'); webp(f'{C}/bw-pair.png', 'film-bw.webp')
    webp(f'{out}/cover.png', 'cover.webp'); webp(f'{out}/portrait.png', 'portrait.webp')


def steps():
    cam = {'mode': 'persp', 'yaw': -28, 'pitch': 6, 'dist': 6.5, 'fov': 24, 'follow': False, 'target': [0, 1.2, 0]}
    jobs = [{'name': m, 'size': [480, 640], 'set': {'clip': 'stand', 'still': True, 'expr': {'neutral': 1}, 'mode': m, 'film': m == 'film', 'cam': cam}} for m in ('skeleton', 'clay', 'paint', 'film')]
    jobs += [{'name': 'walk-skel', 'size': [480, 640], 'set': {'clip': 'walk', 't': 1.0, 'mode': 'skeleton', 'film': False, 'cam': {**cam, 'follow': True, 'followY': 1.2}}},
             {'name': 'walk-clay', 'size': [480, 640], 'set': {'clip': 'walk', 't': 1.0, 'mode': 'clay', 'film': False, 'cam': {**cam, 'follow': True, 'followY': 1.2}}}]
    out = shots('steps', jobs)
    names = ['skeleton', 'clay', 'paint', 'film', 'walk-skel', 'walk-clay']
    ims = [Image.open(f'{out}/{n}.png').convert('RGB') for n in names]
    sheet = Image.new('RGB', (480 * 3, 640 * 2), 'white')
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 3) * 480, (i // 3) * 640))
    sheet.save(f'{C}/steps.png'); webp(f'{C}/steps.png', 'steps.webp')


def seq(n, **kw):
    return [{'t': k / 24, 'dt': 1 / 24, **{a: (v(k) if callable(v) else v) for a, v in kw.items()}} for k in range(n)]


def films(which=None):
    F = []
    F.append(('turnaround', [600, 750], {'clip': 'stand', 'still': False, 'expr': {'neutral': 1}, 'mode': 'film', 'film': True,
                                         'cam': {'mode': 'persp', 'yaw': 0, 'pitch': 5, 'dist': 6.9, 'fov': 24, 'follow': False, 'target': [0, 1.2, 0]}}, seq(120, cam_yaw=lambda k: k * 3)))
    F.append(('walk', [640, 640], {'clip': 'walk', 'expr': {'neutral': 1}, 'cam': {**BODY, 'yaw': 40, 'dist': 7.0}}, seq(96)))
    sched = [(0, 'neutral'), (0.5, 'joy'), (1.5, 'surprise'), (2.5, 'sad'), (3.5, 'angry'), (4.5, 'neutral')]
    F.append(('live-expressions', [560, 560], {'clip': 'idle', 'expr': {'neutral': 1}, 'cam': {**FACE, 'yaw': -20}},
              seq(int(4.98 * 24), expr=lambda k: {[n for s, n in sched if s <= k / 24][-1]: 1})))
    F.append(('live-talk', [560, 560], {'clip': 'idle', 'expr': {'neutral': 1}, 'talk': True, 'cam': {**FACE, 'yaw': 18}},
              seq(int(4.98 * 24), talk=lambda k: k < 96, expr=lambda k: {'joy': 1} if k >= 96 else {'neutral': 1})))
    F.append(('live-wave', [640, 640], {'clip': 'wave', 'expr': {'joy': 1}, 'talk': True, 'cam': {**BODY, 'yaw': 42, 'dist': 7.0, 'followY': 1.3}}, seq(72, expr=lambda k: {'neutral': 1} if k > 16 else {'joy': 1})))
    F.append(('live-dance', [640, 640], {'clip': 'dance', 'expr': {'joy': 1}, 'cam': {**BODY, 'yaw': 20, 'dist': 7.6}}, seq(96)))
    F.append(('live-stomp', [640, 640], {'clip': 'stomp', 'expr': {'angry': 1}, 'talk': True, 'cam': {**BODY, 'yaw': -25, 'dist': 7.6}}, seq(72)))
    F.append(('live-bw-walk', [640, 640], {'clip': 'walk', 'expr': {'neutral': 1}, 'bw': True, 'cam': {**BODY, 'yaw': -35, 'dist': 7.0}}, seq(96)))
    for name, size, st, frames in F:
        if which and name not in which:
            continue
        job = {'name': name, 'size': size, 'set': {'t': 0, 'still': False, 'talk': False, **st, 'bw': st.get('bw', False)}, 'frames': frames}
        out = shots('film-' + name, [job])
        film(f'{out}/{name}', name + '.mp4')


if __name__ == '__main__':
    what = sys.argv[1:] or ['stills', 'steps', 'films']
    if 'stills' in what: stills()
    if 'steps' in what: steps()
    if 'films' in what: films([a for a in what if a not in ('stills', 'steps', 'films')] or None)
    for a in what:
        if a.startswith('film:'): films([a[5:]])
