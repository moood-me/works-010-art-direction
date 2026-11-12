"""Every picture and film of the page. python3 make.py [stills] [films]
The page (web/view.html) gives each picture as a grid of colour keys (shots.mjs); here the grids become PNGs, enlarged
by a whole factor, beside the style's own drawings (styles/s16-pixel/tools). Work files: /home/user/cache/to3d-r48-s16-savely."""
import json
import os
import subprocess
import sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PICS = os.path.join(HERE, '../pics')
CACHE = '/home/user/cache/to3d-r48-s16-savely'
OUT = os.path.join(CACHE, 'out')
D = json.load(open(os.path.join(CACHE, 'data.json')))        # gen.py
DARK = (35, 28, 56)


def rgb(k):
    h = D['RAMPS'][k[0]][int(k[1])]
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def rows(g):
    return [r.split(',') if isinstance(r, str) else list(r) for r in g]


def img(g, scale=8, bg=None):
    g = rows(g)
    im = Image.new('RGBA', (len(g[0]), len(g)), bg or (0, 0, 0, 0))
    for y, r in enumerate(g):
        for x, k in enumerate(r):
            if k:
                im.putpixel((x, y), rgb(k) + (255,))
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


def crop(g):
    g = rows(g)
    ys = [y for y, r in enumerate(g) if any(r)]; xs = [x for r in g for x, k in enumerate(r) if k]
    return [r[min(xs):max(xs) + 1] for r in g[min(ys):max(ys) + 1]]


def backdrop(w, h, floor):
    """sheets.py's backdrop"""
    g = [['d2' if y >= floor else 'd1'] * w for y in range(h)]
    for j in range(3):
        for x in range(w):
            if (x + j) % 2 == 0:
                g[floor - 3 + j][x] = 'd2'
    g[floor] = ['d3'] * w
    return g


def stand(c, s, cx, base):
    """sheets.py's stand: a sprite with its feet on row `base`, centred on column cx, a two-row shadow under them"""
    w, x = len(s[0]), cx - len(s[0]) // 2
    for i in range(x + 2, x + w - 2):
        c[base][i] = 'd1'
    for i in range(x + 4, x + w - 4):
        c[base + 1][i] = 'd1'
    for j, r in enumerate(s):
        for i, k in enumerate(r):
            if k:
                c[base - len(s) + 2 + j][x + i] = k


def lineup(sprites, w=32, top=10):
    h = max(len(s) for s in sprites) + top + 8
    c = backdrop(w * len(sprites), h, h - 12)
    for i, s in enumerate(sprites):
        stand(c, s, w // 2 + i * w, h - 8)
    return c


def stack(ims, gap=0, bg=DARK, horiz=False):
    if horiz:
        o = Image.new('RGB', (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), bg); x = 0
        for i in ims:
            o.paste(i.convert('RGB'), (x, 0)); x += i.width + gap
    else:
        o = Image.new('RGB', (max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), bg); y = 0
        for i in ims:
            o.paste(i.convert('RGB'), (0, y)); y += i.height + gap
    return o


def shots(jobs, name):
    p = os.path.join(CACHE, name + '.json')
    json.dump(jobs, open(p, 'w'))
    subprocess.run(['sh', os.path.join(HERE, 'run.sh'), p], check=True)


def load(n):
    return json.load(open(os.path.join(OUT, n + '.json')))


def best_shift(a, b):
    """how b lies on a (both cropped grids) so that most pixels agree: (matches, dx, dy)"""
    best = (-1, 0, 0)
    for dy in range(-3, 4):
        for dx in range(-4, 5):
            n = sum(1 for y, r in enumerate(a) for x, k in enumerate(r)
                    if k and 0 <= y + dy < len(b) and 0 <= x + dx < len(b[0]) and b[y + dy][x + dx] == k)
            best = max(best, (n, dx, dy))
    return best


FIG = {'W': 58, 'H': 70, 'zoom': 1, 'ax': 29.5, 'ay': 62, 'at': 'floor', 'floor': 58, 'face': 'sprite', 'mode': 'sprite', 'rules': True, 'live': False, 'expr': 'rest', 'talk': False, 't': 0}
POR = {'W': 56, 'H': 56, 'zoom': 2.6, 'ax': 28, 'ay': 24.5, 'at': 'head', 'bg': 'box', 'face': 'portrait', 'yaw': 0, 'clip': 'stand', 'mode': 'sprite', 'rules': True, 'live': False, 'talk': False, 't': 0}
EXPRS = ['rest', 'joy', 'surprise', 'sadness', 'anger']
TURN = [('front', 0), ('q', -22), ('side', -90)]


def stills():
    jobs = [{'name': v, 'set': {**FIG, 'clip': 'stand', 'yaw': y, 'bg': 'none'}} for v, y in TURN]
    jobs += [{'name': 'raw-' + v, 'set': {**FIG, 'clip': 'stand', 'yaw': y, 'bg': 'none', 'rules': False}} for v, y in TURN]
    jobs += [{'name': 'b%d' % y, 'set': {**FIG, 'clip': 'stand', 'yaw': y, 'bg': 'none'}} for y in (45, 90, 135, 180, -135)]
    jobs += [{'name': 'figure', 'set': {**FIG, 'clip': 'stand', 'yaw': 0, 'bg': 'figure'}}]
    jobs += [{'name': 'e-' + e, 'set': {**FIG, 'clip': 'stand', 'yaw': 0, 'bg': 'none', 'expr': e}} for e in EXPRS]
    jobs += [{'name': 'p-' + e, 'set': {**POR, 'expr': e}} for e in EXPRS]
    jobs += [{'name': 'p-raw', 'set': {**POR, 'rules': False}}]
    big = {**FIG, 'W': 96, 'H': 56, 'ax': 48.5, 'ay': 48, 'floor': 44, 'scale': 10, 'clip': 'stand'}
    for m, extra in (('clay', {'bones': True}), ('solid', {'bones': False})):
        for v, y in TURN:
            jobs.append({'name': f'{m}-{v}', 'set': {**big, 'W': 32, 'ax': 16.5, 'mode': m, 'yaw': y, **extra}})
    shots(jobs, 'stills')
    ours = {v: crop(load(v)) for v, _ in TURN}
    drawn = {v: crop(D['DRAWN'][v]) for v, _ in TURN}
    # the drawing above, ours below, on the style's own backdrop
    a = img(lineup([drawn[v] for v, _ in TURN]), 8); b = img(lineup([ours[v] for v, _ in TURN]), 8)
    stack([a, b], 8).save(os.path.join(PICS, 'turn-side.png'))
    b.convert('RGB').save(os.path.join(PICS, 'turn.png'))
    # pixel by pixel: the drawing, ours, and where they differ (agreeing pixels faded, differing ones in the drawing's colour on the left half, ours on the right)
    cells, report = [], {}
    for v, _ in TURN:
        A, B = drawn[v], ours[v]
        n, dx, dy = best_shift(A, B)
        tot = sum(1 for r in A for k in r if k)
        report[v] = (n, tot)
        w = max(len(A[0]), len(B[0]) - dx) + 4; h = max(len(A), len(B) - dy) + 4
        def put(g, ox, oy):
            c = [[''] * w for _ in range(h)]
            for y, r in enumerate(g):
                for x, k in enumerate(r):
                    if k and 0 <= y + oy < h and 0 <= x + ox < w:
                        c[y + oy][x + ox] = k
            return c
        ga, gb = put(A, 2, 2), put(B, 2 - dx, 2 - dy)
        diff = Image.new('RGB', (w, h), rgb('d1'))
        for y in range(h):
            for x in range(w):
                ka, kb = ga[y][x], gb[y][x]
                if ka == kb and ka:
                    diff.putpixel((x, y), tuple((c + 2 * d) // 3 for c, d in zip(rgb(ka), rgb('d1'))))
                elif ka or kb:
                    diff.putpixel((x, y), (255, 80, 200) if (ka and kb) else (255, 190, 60) if ka else (90, 220, 255))
        sc = 8
        cells.append(stack([img(ga, sc, rgb('d1') + (255,)), img(gb, sc, rgb('d1') + (255,)), diff.resize((w * sc, h * sc), Image.NEAREST)], 6, horiz=True))
    stack(cells, 10).save(os.path.join(PICS, 'turn-overlay.png'))
    json.dump(report, open(os.path.join(CACHE, 'match.json'), 'w'))
    print('pixels equal to the drawing:', report)
    # the figure, and at the sprite's true size
    f = img(load('figure'), 8); f.convert('RGB').save(os.path.join(PICS, 'figure.png'))
    dr = backdrop(58, 70, 58); stand(dr, drawn['front'], 29, 62)
    stack([img(dr, 8), f], 8, horiz=True).save(os.path.join(PICS, 'figure-side.png'))
    small = lineup([drawn['front'], ours['front'], drawn['q'], ours['q'], drawn['side'], ours['side']], 26, 6)
    stack([img(small, 1), img(small, 2), img(small, 3)], 6, horiz=True).save(os.path.join(PICS, 'true-size.png'))
    # round the back
    img(lineup([crop(load('b%d' % y)) for y in (45, 90, 135, 180, -135)]), 8).convert('RGB').save(os.path.join(PICS, 'back.png'))
    # portraits and expressions: the drawn sheet above, ours below
    def sheet(gs, sc=5):
        w, h = len(gs[0][0]), len(gs[0])
        c = [['d0'] * (len(gs) * (w + 2) + 2) for _ in range(h + 4)]
        for i, g in enumerate(gs):
            for y in range(h):
                c[2 + y][2 + i * (w + 2):2 + i * (w + 2) + w] = rows(g)[y]
        return img(c, sc)
    stack([sheet([D['PORTRAIT'][e] for e in EXPRS]), sheet([load('p-' + e) for e in EXPRS])], 6).save(os.path.join(PICS, 'expr-side.png'))
    stack([img(D['PORTRAIT']['rest'], 8), img(load('p-rest'), 8)], 8, horiz=True).save(os.path.join(PICS, 'portrait-side.png'))
    img(load('p-rest'), 8).convert('RGB').save(os.path.join(PICS, 'portrait.png'))
    img(lineup([crop(load('e-' + e)) for e in EXPRS], 30, 6), 8).convert('RGB').save(os.path.join(PICS, 'expr-sprite.png'))
    # steps
    def shot(n):
        return Image.open(os.path.join(OUT, n + '.png')).convert('RGB')
    stack([shot(f'clay-{v}') for v, _ in TURN], 0, horiz=True).save(os.path.join(PICS, 'step1-forms.png'))
    stack([shot(f'solid-{v}') for v, _ in TURN], 0, horiz=True).save(os.path.join(PICS, 'step2-colour.png'))
    img(lineup([crop(load('raw-' + v)) for v, _ in TURN]), 8).convert('RGB').save(os.path.join(PICS, 'step3-sampled.png'))
    b.convert('RGB').save(os.path.join(PICS, 'step4-rules.png'))
    stack([img(load('p-raw'), 8), img(load('p-rest'), 8)], 8, horiz=True).save(os.path.join(PICS, 'step5-portrait.png'))


def film(name, set_, frames, scale=8, fps=12, hold=1):
    shots([{'name': name, 'set': set_, 'frames': frames}], 'film-' + name)
    d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    gs = load(name); i = 0
    for g in gs:
        im = img(g, scale).convert('RGB')
        im = im.crop((0, 0, im.width // 2 * 2, im.height // 2 * 2))
        for _ in range(hold):
            im.save(os.path.join(d, 'f%04d.png' % i)); i += 1
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(d, 'f%04d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '14', '-preset', 'slow', '-tune', 'animation', '-movflags', '+faststart', os.path.join(PICS, name + '.mp4')], check=True)
    return gs


STAGE = {**FIG, 'W': 60, 'H': 56, 'ax': 30.5, 'ay': 48, 'floor': 44, 'bg': 'figure', 'live': True}


def fr(sec, **k):
    return [dict(t=i / 12, **k) for i in range(int(sec * 12))]


def films(which):
    if 'turn' in which:
        film('turn', {**STAGE, 'clip': 'stand', 'live': False}, [dict(t=0, yaw=-i * 15) for i in range(24)], hold=3)
    if 'walk' in which:
        gs = film('walk', {**STAGE, 'clip': 'walk', 'yaw': -62}, fr(8))
        film('walk-front', {**STAGE, 'clip': 'walk', 'yaw': -25}, fr(4))
        # a sprite sheet of the walk: every other drawing of the first two seconds
        cells = [crop_to(g, 14, 4, 34, 46) for g in gs[0:24:2]]
        stack([img(c, 6) for c in cells], 0, horiz=True).save(os.path.join(PICS, 'walk-sheet.png'))
    if 'idle' in which:
        film('idle', {**STAGE, 'clip': 'idle', 'yaw': -18}, fr(5))
    if 'wave' in which:
        film('wave', {**STAGE, 'clip': 'wave', 'yaw': 8}, fr(6))
    if 'stomp' in which:
        film('stomp', {**STAGE, 'clip': 'stomp', 'yaw': -28}, fr(6))
    if 'face' in which:
        # the portrait alive: blinks, looks, the sheet's expressions one after another, then speech
        seq = [('rest', 2.5), ('joy', 1.8), ('rest', 1.0), ('surprise', 1.6), ('sadness', 1.8), ('anger', 1.8), ('rest', 1.5)]
        frames, t = [], 0
        for e, d in seq:
            for _ in range(int(d * 12)):
                frames.append(dict(t=t, expr=e, talk=False)); t += 1 / 12
        for e, d in [('rest', 4.0), ('joy', 2.5)]:
            for _ in range(int(d * 12)):
                frames.append(dict(t=t, expr=e, talk=True)); t += 1 / 12
        film('face', {**POR, 'clip': 'stand', 'live': True}, frames)
        film('talk-sprite', {**STAGE, 'W': 40, 'H': 46, 'ax': 20.5, 'ay': 42, 'floor': 38, 'clip': 'idle', 'yaw': -10}, [dict(t=i / 12, expr='rest' if i < 60 else 'anger', talk=True) for i in range(96)], scale=10)


def crop_to(g, x, y, w, h):
    return [r[x:x + w] for r in rows(g)[y:y + h]]


if __name__ == '__main__':
    a = sys.argv[1:] or ['stills', 'films']
    os.makedirs(PICS, exist_ok=True)
    if 'stills' in a:
        stills()
    which = [x for x in a if x not in ('stills', 'films')] or (['turn', 'walk', 'idle', 'wave', 'stomp', 'face'] if 'films' in a else [])
    if which:
        films(which)
