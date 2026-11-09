"""Every picture and film of the page. python3 make.py [stills] [films] [walk run ...]  (from anywhere)
Renders go to the cache folder's out/, the page's pictures to ../pics."""
import json
import os
import subprocess
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.basename(os.path.dirname(HERE))
WHO = 'tim'
STY = os.path.join(HERE, '../../../styles/s5-indie/pics')
PICS = os.path.join(HERE, '../pics')
CACHE = '/home/user/cache/to3d-' + FOLDER
OUT = os.path.join(CACHE, 'out')
sys.path.insert(0, HERE)
import compare  # noqa: E402

# the drawing's sheets (styles/s5-indie/tools/build.py): the same viewBoxes, the same pixels
HY = -205                                   # the head's centre
TURN = {'figures': [{'x': 175, 'yaw': 0}, {'x': 405, 'yaw': 45}, {'x': 635, 'yaw': 90}], 'cam': {'vb': [40, -490, 720, 535]}}
EXPRS = ['neutral', 'joy', 'surprise', 'sad', 'anger']
EXPR_VB = [0, HY - 105, 1000, 249]


def shots(jobs, name):
    p = os.path.join(CACHE, name + '.json')
    json.dump(jobs, open(p, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'shots.mjs'), p, OUT], check=True)


def jpg(src, dst, q=86, crop=None):
    im = Image.open(src).convert('RGB')
    if crop:
        im = im.crop(crop)
    im.save(dst, quality=q)


def stills():
    back = {'figures': [{'x': 175, 'yaw': 135}, {'x': 405, 'yaw': 180}, {'x': 635, 'yaw': -90}], 'cam': TURN['cam']}
    jobs = [
        {'name': 'turn', 'size': [1080, 802], 'set': {'view': 'style', 'line': 2.1, **TURN}},
        {'name': 'turn-nocheat', 'size': [1080, 802], 'set': {'view': 'style', 'line': 2.1, 'cheat': 0, **TURN}},
        {'name': 'step-skel', 'size': [1080, 802], 'set': {'view': 'skel', 'cheat': 0.38, **TURN}},
        {'name': 'step-clay', 'size': [1080, 802], 'set': {'view': 'clay', **TURN}},
        {'name': 'step-flat', 'size': [1080, 802], 'set': {'view': 'flat', **TURN}},
        {'name': 'figure', 'size': [390, 765], 'set': {'view': 'style', 'figures': [{'x': 0, 'yaw': 18}], 'cam': {'vb': [-130, -490, 260, 510]}}},
        {'name': 'portrait', 'size': [600, 600], 'set': {'view': 'style', 'line': 1.2, 'figures': [{'x': 0, 'yaw': 12}], 'cam': {'vb': [-115, HY - 100, 230, 230]}}},
        {'name': 'expr', 'size': [1400, 348], 'set': {'view': 'style', 'line': 1.75, 'figures': [
            {'x': 100 + i * 200, 'yaw': 8 if i % 2 else -8, 'ex': e} for i, e in enumerate(EXPRS)], 'cam': {'vb': EXPR_VB}}},
        {'name': 'back', 'size': [1080, 802], 'set': {'view': 'style', 'line': 2.1, **back}},
    ]
    shots(jobs, 'stills')
    o = lambda n: os.path.join(OUT, n + '.png')
    d = lambda n: os.path.join(STY, f'{n}-{WHO}.png')
    # the drawing above, the 3D below; and the drawing's lines over the 3D. The turnaround sheet is cut to the figure
    cut = {'turn': (0, 290, 1080, 802)}
    for n, vert in [('turn', True), ('figure', False), ('portrait', False), ('expr', True)]:
        a = Image.open(d(n)).convert('RGB')
        b = Image.open(o(n)).convert('RGB').resize(a.size)
        if n in cut:
            a, b = a.crop(cut[n]), b.crop(cut[n])
        compare.side(a, b, vert).save(os.path.join(PICS, f'{n}-side.jpg'), quality=86)
        compare.overlay(a, b).save(os.path.join(PICS, f'{n}-overlay.jpg'), quality=86)
    # the face's turn on the head: with it and without
    a = Image.open(d('turn')).convert('RGB').crop(cut['turn'])
    b = Image.open(o('turn')).convert('RGB').crop(cut['turn'])
    c = Image.open(o('turn-nocheat')).convert('RGB').crop(cut['turn'])
    box = (380, 0, 1080, 250)
    compare.side(compare.side(a.crop(box), b.crop(box), True), c.crop(box), True).save(os.path.join(PICS, 'cheat.jpg'), quality=86)
    # steps: the skeleton on the faded drawing, then the forms, the paints, the face
    a = Image.open(d('turn')).convert('RGB')
    sk = Image.open(o('step-skel')).convert('RGB')
    faded = Image.blend(a, Image.new('RGB', a.size, (236, 229, 217)), 0.6)
    import numpy as np
    S = np.asarray(sk).astype(int)
    bg = np.abs(S - np.array([236, 229, 217])).sum(2) < 24
    F = np.asarray(faded).copy()
    F[~bg] = S[~bg]
    Image.fromarray(F.astype('uint8')).crop(cut['turn']).save(os.path.join(PICS, 'step1-skeleton.jpg'), quality=86)
    jpg(o('step-clay'), os.path.join(PICS, 'step2-forms.jpg'), crop=cut['turn'])
    jpg(o('step-flat'), os.path.join(PICS, 'step3-paint.jpg'), crop=cut['turn'])
    jpg(o('turn'), os.path.join(PICS, 'step4-face.jpg'), crop=cut['turn'])
    jpg(o('back'), os.path.join(PICS, 'back.jpg'), crop=cut['turn'])


def encode(name, fps, dst=None):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(OUT, name, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '25', '-preset', 'slow', '-movflags', '+faststart',
                    dst or os.path.join(PICS, name + '.mp4')], check=True)


def turn_film():
    # a turn around: he turns in place, the camera a little above, as a person looks
    n = 72
    fig = lambda i: {'set': {'figures': [{'yaw': 360 * i / n}]}}
    shots([{'name': 'turn', 'size': [560, 640], 'set': {'view': 'style', 'line': 2.1, 'figures': [{'yaw': 0}], 'cam': {'pos': [0, 0.56, 3.0], 'at': [0, 0.36, 0], 'fov': 16}},
            'frames': [fig(i) for i in range(n)]}], 'film-turn')
    encode('turn', 24)
    jpg(os.path.join(OUT, 'turn', 'f0009.png'), os.path.join(PICS, 'turn-frame.jpg'))


def live_film(name, clip, n, cam, size=(640, 720), fps=30, events=None, hold=None, fig=None, still=None):
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
    encode(name, fps)
    jpg(os.path.join(OUT, name, f'f{(still or n // 2):04d}.png'), os.path.join(PICS, name + '-frame.jpg'))


LIVE = {
    'walk': lambda: live_film('walk', 'walk', 120, {'yaw': 32, 'pitch': 7, 'dist': 1.75, 'ty': 0.36, 'fov': 26, 'follow': True}),
    'run': lambda: live_film('run', 'run', 90, {'yaw': 38, 'pitch': 7, 'dist': 1.9, 'ty': 0.36, 'fov': 26, 'follow': True}, events={0.0: {'expr': 'joy'}}),
    'sneak': lambda: live_film('sneak', 'sneak', 120, {'yaw': 30, 'pitch': 7, 'dist': 1.75, 'ty': 0.34, 'fov': 26, 'follow': True}),
    'jump': lambda: live_film('jump', 'jump', 90, {'yaw': 24, 'pitch': 5, 'dist': 2.1, 'ty': 0.44, 'fov': 26},
                              events={0.0: {'expr': {'neutral': 0.5, 'joy': 0.5}}, 0.9: {'expr': 'joy'}}),
    'wave': lambda: live_film('wave', 'wave', 96, {'yaw': 20, 'pitch': 6, 'dist': 1.7, 'ty': 0.4, 'fov': 26}, events={0.0: {'expr': 'joy'}}, hold=2.95),
    # looking round, hands behind his back: the eyes go first, the head follows, a blink with the big turns
    'look': lambda: live_film('look', 'look', 150, {'yaw': 12, 'pitch': 4, 'dist': 1.35, 'ty': 0.44, 'fov': 24}, size=(640, 640)),
    # the face close: speaking, then the sheet's expressions one after another, then a mix and speaking again
    'face': lambda: live_film('face', 'look', 300, {'yaw': 10, 'pitch': 2, 'dist': 1.05, 'ty': 0.5, 'fov': 22}, size=(640, 640), fig={'clip': 'idle'},
                              events={0.3: {'talk': True}, 4.2: {'talk': False}, 4.4: {'expr': 'joy'}, 5.5: {'expr': 'surprise'},
                                      6.6: {'expr': 'sad'}, 7.7: {'expr': 'anger'}, 8.7: {'expr': {'joy': 0.5, 'neutral': 0.5}, 'talk': True}}),
}


if __name__ == '__main__':
    os.makedirs(PICS, exist_ok=True)
    what = sys.argv[1:] or ['stills', 'films']
    if 'stills' in what:
        stills()
    if 'films' in what:
        what += ['turn'] + list(LIVE)
    if 'turn' in what:
        turn_film()
    for w in what:
        if w in LIVE:
            LIVE[w]()
