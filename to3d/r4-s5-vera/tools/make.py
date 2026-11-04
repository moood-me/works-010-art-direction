"""Every picture and film of the page. python3 make.py [stills] [films]  (from anywhere)
Renders go to /home/user/cache/to3d-r4-s5-vera/out, the page's pictures to ../pics."""
import json
import math
import os
import subprocess
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
STY = os.path.join(HERE, '../../../styles/s5-indie/pics')
PICS = os.path.join(HERE, '../pics')
CACHE = '/home/user/cache/to3d-r4-s5-vera'
OUT = os.path.join(CACHE, 'out')
sys.path.insert(0, HERE)
import compare  # noqa: E402

TURN = {'figures': [{'x': 175, 'yaw': 0}, {'x': 405, 'yaw': 45}, {'x': 635, 'yaw': 90}], 'cam': {'vb': [40, -490, 720, 535]}}
EXPRS = ['neutral', 'joy', 'surprise', 'sad', 'anger']


def shots(jobs, name):
    p = os.path.join(CACHE, name + '.json')
    json.dump(jobs, open(p, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), p, OUT], check=True)


def jpg(src, dst, q=86):
    Image.open(src).convert('RGB').save(dst, quality=q)


def stills():
    jobs = [
        {'name': 'turn', 'size': [1080, 802], 'set': {'view': 'style', 'line': 2.1, **TURN}},
        {'name': 'step-skel', 'size': [1080, 802], 'set': {'view': 'skel', **TURN}},
        {'name': 'step-clay', 'size': [1080, 802], 'set': {'view': 'clay', **TURN}},
        {'name': 'step-flat', 'size': [1080, 802], 'set': {'view': 'flat', **TURN}},
        {'name': 'figure', 'size': [390, 765], 'set': {'view': 'style', 'figures': [{'x': 0, 'yaw': 18}], 'cam': {'vb': [-130, -490, 260, 510]}}},
        {'name': 'portrait', 'size': [600, 600], 'set': {'view': 'style', 'line': 1.5, 'figures': [{'x': 0, 'yaw': 12}], 'cam': {'vb': [-115, -467, 230, 230]}}},
        {'name': 'expr', 'size': [1400, 380], 'set': {'view': 'style', 'line': 1.9, 'figures': [
            {'x': 100 + i * 200, 'yaw': 8 if i % 2 else -8, 'ex': e} for i, e in enumerate(EXPRS)], 'cam': {'vb': [0, -480, 1000, 272]}}},
        {'name': 'back', 'size': [1080, 802], 'set': {'view': 'style', 'line': 2.1, 'figures': [{'x': 175, 'yaw': 135}, {'x': 405, 'yaw': 180}, {'x': 635, 'yaw': -90}], 'cam': {'vb': [40, -490, 720, 535]}}},
    ]
    shots(jobs, 'stills')
    o = lambda n: os.path.join(OUT, n + '.png')
    d = lambda n: os.path.join(STY, n + '-vera.png')
    # the drawing above, the 3D below; and the drawing's lines over the 3D
    for n, draw, vert in [('turn', 'turn', True), ('figure', 'figure', False), ('portrait', 'portrait', False), ('expr', 'expr', True)]:
        a = Image.open(d(draw)).convert('RGB')
        b = Image.open(o(n)).convert('RGB').resize(a.size)
        compare.side(a, b, vert).save(os.path.join(PICS, f'{n}-side.jpg'), quality=86)
        compare.overlay(a, b).save(os.path.join(PICS, f'{n}-overlay.jpg'), quality=86)
    # steps: the skeleton on the faded drawing, then the forms, the paints, the face
    a = Image.open(d('turn')).convert('RGB')
    sk = Image.open(o('step-skel')).convert('RGB')
    faded = Image.blend(a, Image.new('RGB', a.size, (236, 229, 217)), 0.6)
    import numpy as np
    S = np.asarray(sk).astype(int)
    bg = np.abs(S - np.array([236, 229, 217])).sum(2) < 24
    F = np.asarray(faded).copy()
    F[~bg] = S[~bg]
    Image.fromarray(F.astype('uint8')).save(os.path.join(PICS, 'step1-skeleton.jpg'), quality=86)
    jpg(o('step-clay'), os.path.join(PICS, 'step2-forms.jpg'))
    jpg(o('step-flat'), os.path.join(PICS, 'step3-paint.jpg'))
    jpg(o('turn'), os.path.join(PICS, 'step4-face.jpg'))
    jpg(o('back'), os.path.join(PICS, 'back.jpg'))


def film(name, frames, size, fps, dst):
    shots([{'name': name, 'size': size, 'frames': frames}], 'film-' + name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(OUT, name, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-movflags', '+faststart', dst], check=True)


def films(which=('turn', 'walk')):
    if 'turn' in which:
        turn_film()
    if 'walk' in which:
        walk_film()


def turn_film():
    # a turn around: she turns in place, the camera a little above, as a person looks
    n = 96
    film('turn', [{'view': 'style', 'line': 2.1, 'figures': [{'yaw': 360 * i / n}], 'cam': {'pos': [0, 0.78, 4.4], 'at': [0, 0.56, 0], 'fov': 18}} for i in range(n)],
         [640, 800], 24, os.path.join(PICS, 'turn.mp4'))
    jpg(os.path.join(OUT, 'turn', 'f0012.png'), os.path.join(PICS, 'turn-frame.jpg'))


def walk_film():
    # Kimodo's walk: she comes toward the camera and to its left, seen from three quarters
    film('walk', [{'view': 'style', 'line': 2.1, 'figures': [{'yaw': -32, 'x': 150, 'z': -120, 'motion': 'walk', 'f': f, 'travel': True}],
                   'cam': {'pos': [0.75, 0.8, 3.3], 'at': [-0.05, 0.5, 0.3], 'fov': 24}} for f in range(120)],
         [960, 600], 30, os.path.join(PICS, 'walk.mp4'))
    jpg(os.path.join(OUT, 'walk', 'f0060.png'), os.path.join(PICS, 'walk-frame.jpg'))


if __name__ == '__main__':
    os.makedirs(PICS, exist_ok=True)
    what = sys.argv[1:] or ['stills', 'films']
    if 'stills' in what:
        stills()
    if 'films' in what:
        films()
    if 'walk' in what:
        films(('walk',))
