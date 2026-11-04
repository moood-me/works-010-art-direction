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


def films(which=('turn', 'walk', 'sit', 'look', 'wave', 'face')):
    if 'turn' in which:
        turn_film()
    for k in which:
        if k in LIVE:
            LIVE[k]()


def turn_film():
    # a turn around: she turns in place, the camera a little above, as a person looks
    n = 96
    film('turn', [{'view': 'style', 'line': 2.1, 'figures': [{'yaw': 360 * i / n}], 'cam': {'pos': [0, 0.78, 4.4], 'at': [0, 0.56, 0], 'fov': 18}} for i in range(n)],
         [640, 800], 24, os.path.join(PICS, 'turn.mp4'))
    jpg(os.path.join(OUT, 'turn', 'f0012.png'), os.path.join(PICS, 'turn-frame.jpg'))


def live_film(name, clip, n, cam, size=(720, 900), fps=30, events=None, hold=None, fig=None):
    """A clip with the live face: events {second: {expr, talk}} change the face on the way; hold: stop the motion
    there (the face lives on)."""
    events = events or {}
    frames = []
    for k in range(n):
        t = k / fps
        fr = {'t': min(t, hold) if hold else t, 'dt': 1 / fps}
        for et, ev in events.items():
            if abs(et - t) < 0.5 / fps:
                fr.update(ev)
        frames.append(fr)
    F = {'clip': clip, 'live': True, 'yaw': 0, 'exprW': {'neutral': 1}, **(fig or {})}
    shots([{'name': name, 'size': list(size), 'set': {'view': 'style', 'line': 2.1, 'floor': True, 'figures': [F], 'cam': cam}, 'frames': frames}], 'film-' + name)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(OUT, name, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-movflags', '+faststart', os.path.join(PICS, name + '.mp4')], check=True)
    jpg(os.path.join(OUT, name, f'f{n // 2:04d}.png'), os.path.join(PICS, name + '-frame.jpg'))


LIVE = {
    # the walk, the camera going along with her
    'walk': lambda: live_film('walk', 'walk', 150, {'yaw': 32, 'pitch': 7, 'dist': 2.75, 'ty': 0.56, 'fov': 26, 'follow': True}),
    # sitting down on the floor; tired at the end
    'sit': lambda: live_film('sit', 'sit', 150, {'yaw': 34, 'pitch': 13, 'dist': 2.6, 'ty': 0.42, 'fov': 26, 'follow': False},
                             events={3.3: {'expr': {'neutral': 0.5, 'sad': 0.5}}}, hold=3.95),
    # looking round: the eyes go first, the head follows, a blink with the big turns
    'look': lambda: live_film('look', 'look', 150, {'yaw': 12, 'pitch': 4, 'dist': 1.75, 'ty': 0.74, 'fov': 24}, size=(720, 720)),
    # the arms free: the folder goes into the left hand, the right one waves
    'wave': lambda: live_film('wave', 'wave', 105, {'yaw': 22, 'pitch': 6, 'dist': 3.0, 'ty': 0.6, 'fov': 26},
                              events={0.0: {'expr': 'joy'}}, hold=2.95),
    # the face close: speaking, then the sheet's expressions one after another, then a mix and speaking again
    'face': lambda: live_film('face', 'idle', 300, {'yaw': 12, 'pitch': 2, 'dist': 1.2, 'ty': 0.87, 'fov': 22}, size=(720, 720),
                              events={0.3: {'talk': True}, 4.4: {'talk': False}, 4.6: {'expr': 'joy'}, 5.7: {'expr': 'surprise'},
                                      6.8: {'expr': 'sad'}, 7.9: {'expr': 'anger'}, 8.9: {'expr': {'joy': 0.6, 'neutral': 0.4}, 'talk': True}}),
}


if __name__ == '__main__':
    os.makedirs(PICS, exist_ok=True)
    what = sys.argv[1:] or ['stills', 'films']
    if 'stills' in what:
        stills()
    if 'films' in what:
        films()
    if [w for w in what if w in LIVE]:
        films([w for w in what if w in LIVE])
