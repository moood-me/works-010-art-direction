"""The drawing and the 3D side by side and overlaid, in the drawing's own views (orthographic, the drawing's scale:
1.6 px per drawing unit, K = 2.8 mm per unit, so 900 px = 1.575 m; the picture's middle at 0.63 m).
  python3 compare.py turn | figure | expr | portrait     → ../pics/cmp-*.webp"""
import sys, json, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from common import CACHE, HERE

PICS = os.path.join(os.path.dirname(HERE), 'pics')
RENDER = '/home/user/cache/styles-s1-pixar/render'
STAND = {'motion': ['bow'], 't': 0}


def shots(name, w, h, shots, page=''):
    job = f'{CACHE}/job_{name}.json'
    json.dump({'w': w, 'h': h, 'page': page, 'set': {**STAND, 'still': True}, 'shots': shots}, open(job, 'w'))
    subprocess.run(['node', f'{HERE}/shots.mjs', job, f'{CACHE}/{name}'], check=True)
    return {s['name']: Image.open(f'{CACHE}/{name}/{s["name"]}.png').convert('RGB') for s in shots}


def label(im, text):
    d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
    except Exception: f = None
    d.text((14, 10), text, fill=(40, 52, 64), font=f)
    return im


def triple(draw, rend):
    ov = Image.blend(draw, rend, 0.5)
    return [label(draw.copy(), 'рисунок'), label(rend.copy(), '3D'), label(ov, 'наложение')]


def turn():
    D = Image.open(f'{RENDER}/tim-turnaround.png').convert('RGB')
    views = [('front', 0.0, 270), ('tq', -0.62, 750), ('side', -1.5708, 1230)]
    R = shots('cmp_turn', 480, 900, [{'name': n, 'set': {'cam': {'yaw': y, 'follow': [0, 0.63, 0], 'dist': 5, 'height': 1.575}, 'expr': [{'t': 0, 'name': 'calm'}]}} for n, y, _ in views])
    rows = []
    for n, y, cx in views:
        d = D.crop((cx - 240, 0, cx + 240, 900))
        rows.append(np.concatenate([np.asarray(i) for i in triple(d, R[n])], 1))
    out = Image.fromarray(np.concatenate(rows, 0)).resize((864, 1620), Image.LANCZOS)
    out.save(f'{PICS}/cmp-turn.webp', quality=86)



def expr():
    D = Image.open(f'{RENDER}/tim-expressions.png').convert('RGB')
    names = ['joy', 'surprise', 'sad', 'anger']
    R = shots('cmp_expr', 400, 560, [{'name': n, 'set': {'cam': {'yaw': -0.18, 'pitch': -0.06 if n == 'sad' else 0, 'follow': [0, 1.028, 0], 'dist': 5, 'height': 0.682},
                                                            'expr': [{'t': 0, 'name': n}]}} for n in names])
    top = np.concatenate([np.asarray(D.crop((200 + 400 * i - 200, 0, 200 + 400 * i + 200, 560))) for i in range(4)], 1)
    bot = np.concatenate([np.asarray(R[n]) for n in names], 1)
    out = Image.fromarray(np.concatenate([top, bot], 0)).resize((1200, 840), Image.LANCZOS)
    out.save(f'{PICS}/cmp-expr.webp', quality=86)


def portrait():
    D = Image.open(f'{RENDER}/tim-portrait.png').convert('RGB')
    R = shots('cmp_portrait', 640, 760, [{'name': 'p', 'set': {'cam': {'yaw': -0.3, 'follow': [0, 0.967, 0], 'dist': 5, 'height': 0.773}, 'expr': [{'t': 0, 'name': 'smirk'}]}}])
    out = Image.fromarray(np.concatenate([np.asarray(i) for i in triple(D, R['p'])], 1)).resize((1440, 570), Image.LANCZOS)
    out.save(f'{PICS}/cmp-portrait.webp', quality=86)


def figure():
    D = Image.open(f'{RENDER}/tim-figure.png').convert('RGB')
    R = shots('cmp_figure', 620, 900, [{'name': 'f', 'set': {'cam': {'yaw': -0.3, 'follow': [0, 0.63, 0], 'dist': 5, 'height': 1.575}, 'expr': [{'t': 0, 'name': 'smirk'}]}}])
    out = Image.fromarray(np.concatenate([np.asarray(i) for i in triple(D, R['f'])], 1)).resize((1240, 600), Image.LANCZOS)
    out.save(f'{PICS}/cmp-figure.webp', quality=86)


if __name__ == '__main__':
    for k in sys.argv[1:]: globals()[k]()
