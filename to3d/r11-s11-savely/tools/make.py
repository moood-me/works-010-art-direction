"""Every picture and film of the page.  python3 make.py [stills] [films] [steps]
Renders through shots.mjs (headless Chromium, the page tools/web/view.html), compares with compare.py, encodes mp4 with
ffmpeg, writes webp/mp4 into ../pics. Work files in /home/user/cache/to3d-r11-s11-savely/."""
import json
import os
import subprocess
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
C = '/home/user/cache/to3d-r11-s11-savely'
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


# the drawing's cameras: turnaround-savely (scale 1.6, soles at y 800, cells 500 px) and expressions-savely (1.55)
TURN = {'mode': 'ortho', 'pitch': 0, 'target': [-0.012, 0.875, 0], 'ortho': {'h': 900 / 1.6 * S}}
VIEWS = [('front', 0, 0), ('q', -31.5, -0.07), ('side', -72, -0.2)]
EXPRS = ['neutral', 'joy', 'surprise', 'sad', 'angry']


def stills():
    jobs = [{'name': v, 'size': [500, 900], 'set': {'clip': 'stand', 'still': True, 'expr': {'neutral': 1}, 'mode': 'film', 'cam': {**TURN, 'yaw': y, 'ortho': {**TURN['ortho'], 'dx': dx}}}} for v, y, dx in VIEWS]
    jobs += [{'name': 'ex-' + e, 'size': [300, 420], 'set': {'expr': {e: 1}, 'still': True, 'cam': {'mode': 'ortho', 'yaw': -17.2, 'pitch': 0, 'target': [0.004, 1.175, 0.044], 'ortho': {'h': 420 / 1.55 * S, 'dx': 0}}}} for e in EXPRS]
    jobs += [{'name': 'bw', 'size': [500, 900], 'set': {'expr': {'neutral': 1}, 'bw': True, 'cam': {**TURN, 'yaw': -31.5, 'ortho': {**TURN['ortho'], 'dx': -0.07}}}}]
    jobs += [{'name': 'cover', 'size': [900, 900], 'set': {'bw': False, 'expr': {'neutral': 1}, 'cam': {'mode': 'persp', 'yaw': -24, 'pitch': 6, 'dist': 4.0, 'fov': 24, 'follow': False, 'target': [0, 0.8, 0]}}}]
    jobs += [{'name': 'portrait', 'size': [700, 760], 'set': {'expr': {'neutral': 1}, 'cam': {'mode': 'persp', 'yaw': -22, 'pitch': 4, 'dist': 2.1, 'fov': 24, 'follow': False, 'target': [0, 1.17, 0]}}}]
    out = shots('stills', jobs)
    cmp = os.path.join(HERE, 'compare.py')
    subprocess.run(['python3', cmp, f'{C}/cmp-turn.jpg', f'{D}/turnaround-savely.jpg', '0,0,500,900;500,0,1000,900;1000,0,1500,900',
                    *[f'{out}/{v}.png' for v, _, _ in VIEWS], '--labels=анфас,три четверти,профиль', '--width=1500'], check=True)
    subprocess.run(['python3', cmp, f'{C}/cmp-expr.jpg', f'{D}/expressions-savely.jpg', ';'.join(f'{i * 300},0,{i * 300 + 300},420' for i in range(5)),
                    *[f'{out}/ex-{e}.png' for e in EXPRS], '--width=1500'], check=True)
    webp(f'{C}/cmp-turn.jpg', 'compare-turn.webp'); webp(f'{C}/cmp-expr.jpg', 'compare-expressions.webp')
    # black-and-white: the drawing's cast on film beside the 3D
    bwd = Image.open(f'{D}/cast-bw.jpg').convert('RGB').crop((120, 180, 520, 960)).resize((462, 900))
    pair = Image.new('RGB', (462 + 500, 900), 'white'); pair.paste(bwd, (0, 0)); pair.paste(Image.open(f'{out}/bw.png').convert('RGB'), (462, 0))
    pair.save(f'{C}/bw-pair.png'); webp(f'{C}/bw-pair.png', 'compare-bw.webp')
    webp(f'{out}/cover.png', 'cover.webp'); webp(f'{out}/portrait.png', 'portrait.webp')


def steps():
    cam = {'mode': 'persp', 'yaw': -28, 'pitch': 6, 'dist': 4.0, 'fov': 24, 'follow': False, 'target': [0, 0.8, 0]}
    jobs = [{'name': m, 'size': [480, 640], 'set': {'clip': 'stand', 'still': True, 'expr': {'neutral': 1}, 'mode': m, 'film': m == 'film', 'cam': cam}} for m in ('skeleton', 'clay', 'paint', 'film')]
    jobs += [{'name': 'walk-skel', 'size': [480, 640], 'set': {'clip': 'walk', 't': 1.0, 'mode': 'skeleton', 'film': False, 'cam': {**cam, 'follow': True, 'followY': 0.8}}},
             {'name': 'walk-clay', 'size': [480, 640], 'set': {'clip': 'walk', 't': 1.0, 'mode': 'clay', 'film': False, 'cam': {**cam, 'follow': True, 'followY': 0.8}}}]
    out = shots('steps', jobs)
    names = ['skeleton', 'clay', 'paint', 'film', 'walk-skel', 'walk-clay']
    ims = [Image.open(f'{out}/{n}.png').convert('RGB') for n in names]
    sheet = Image.new('RGB', (480 * 3, 640 * 2), 'white')
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 3) * 480, (i // 3) * 640))
    sheet.save(f'{C}/steps.png'); webp(f'{C}/steps.png', 'steps.webp')


def films(which=None):
    F = []
    turn = [{'t': k / 24, 'dt': 1 / 24, 'cam_yaw': k * 3} for k in range(120)]
    F.append(('turnaround', [600, 750], {'clip': 'stand', 'still': False, 'expr': {'neutral': 1}, 'bw': False, 'mode': 'film', 'film': True,
                                         'cam': {'mode': 'persp', 'yaw': 0, 'pitch': 5, 'dist': 4.3, 'fov': 24, 'follow': False, 'target': [0, 0.8, 0]}}, turn))
    walk = [{'t': k / 24, 'dt': 1 / 24} for k in range(96)]
    F.append(('walk', [640, 640], {'clip': 'walk', 't': 0, 'still': False, 'expr': {'neutral': 1}, 'cam': {'mode': 'persp', 'yaw': 40, 'pitch': 5, 'dist': 4.5, 'fov': 24, 'follow': True, 'followY': 0.8}}, walk))
    sched = [(0, 'neutral'), (0.5, 'joy'), (1.5, 'surprise'), (2.5, 'sad'), (3.5, 'angry'), (4.5, 'neutral')]
    ex = []
    for k in range(int(4.98 * 24)):
        t = k / 24; e = [n for s, n in sched if s <= t][-1]
        ex.append({'t': t, 'dt': 1 / 24, 'expr': {e: 1}})
    F.append(('live-expressions', [560, 560], {'clip': 'idle', 't': 0, 'still': False, 'expr': {'neutral': 1}, 'talk': False, 'cam': {'mode': 'persp', 'yaw': -20, 'pitch': -2, 'dist': 2.5, 'fov': 24, 'follow': True, 'followHead': True}}, ex))
    talk = [{'t': k / 24, 'dt': 1 / 24, 'talk': k < 100, 'expr': {'neutral': 0.6, 'angry': 0.4} if 40 < k < 80 else {'neutral': 1}} for k in range(int(4.98 * 24))]
    F.append(('live-talk', [560, 560], {'clip': 'idle', 't': 0, 'still': False, 'expr': {'neutral': 1}, 'talk': True, 'cam': {'mode': 'persp', 'yaw': 18, 'pitch': -2, 'dist': 2.5, 'fov': 24, 'follow': True, 'followHead': True}}, talk))
    F.append(('live-dance', [640, 640], {'clip': 'dance', 't': 0, 'still': False, 'expr': {'joy': 1}, 'talk': False, 'cam': {'mode': 'persp', 'yaw': 20, 'pitch': 5, 'dist': 4.0, 'fov': 24, 'follow': True, 'followY': 0.8}},
                  [{'t': k / 24, 'dt': 1 / 24} for k in range(96)]))
    F.append(('live-stomp', [640, 640], {'clip': 'stomp', 't': 0, 'still': False, 'expr': {'angry': 1}, 'talk': True, 'cam': {'mode': 'persp', 'yaw': -25, 'pitch': 5, 'dist': 4.7, 'fov': 24, 'follow': True, 'followY': 0.8}},
                  [{'t': k / 24, 'dt': 1 / 24} for k in range(72)]))
    F.append(('live-wave', [640, 640], {'clip': 'wave', 't': 0, 'still': False, 'expr': {'joy': 1}, 'talk': True, 'cam': {'mode': 'persp', 'yaw': -50, 'pitch': 5, 'dist': 4.4, 'fov': 24, 'follow': True, 'followY': 0.85}},
                  [{'t': k / 24, 'dt': 1 / 24} for k in range(72)]))
    F.append(('live-bw-walk', [640, 640], {'clip': 'walk', 't': 0, 'still': False, 'expr': {'neutral': 1}, 'bw': True, 'cam': {'mode': 'persp', 'yaw': -35, 'pitch': 5, 'dist': 4.5, 'fov': 24, 'follow': True, 'followY': 0.8}},
                  [{'t': k / 24, 'dt': 1 / 24} for k in range(96)]))
    for name, size, st, frames in F:
        if which and name not in which:
            continue
        job = {'name': name, 'size': size, 'set': {**st, 'bw': st.get('bw', False)}, 'frames': frames}
        out = shots('film-' + name, [job])
        film(f'{out}/{name}', name + '.mp4')


if __name__ == '__main__':
    what = sys.argv[1:] or ['stills', 'steps', 'films']
    if 'stills' in what: stills()
    if 'steps' in what: steps()
    if 'films' in what: films([a for a in what if a not in ('stills', 'steps', 'films')] or None)
    for a in what:
        if a.startswith('film:'): films([a[5:]])
