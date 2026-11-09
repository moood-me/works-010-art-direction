"""The drawing and the 3D side by side and overlaid, in the drawing's own views (orthographic, the drawing's scale and
place: build.py of the style puts the floor 90 px above the sheet's bottom and draws 1.25 px per unit for Вера —
min(1.6, 750 / (floor + 60)) —, K = 2.8 mm per unit).
  python3 compare.py turn | figure | expr | portrait     → ../pics/cmp-*.webp
The portrait and the figure are the style's pictures; the turnaround and the expression sheet are drawn by the
style's code for these comparisons (drawn.py), the style's page has none of Вера."""
import sys, json, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from common import CACHE, HERE, K, FLOOR
from drawing import P
import char

PICS = os.path.join(os.path.dirname(HERE), 'pics')
RENDER = '/home/user/cache/styles-s1-pixar/render'
STAND = char.STAND
S = min(1.6, 750 / (FLOOR + 60))                   # px per unit in the figure sheets
HEAD_UP = 42 * char.HS * K                         # the head's centre over the Head joint (build.py puts the joint at head y −42)


def head_cam(yaw, px, down_px, H, pitch=0):
    """the camera of a head sheet: px pixels per unit, the head's centre down_px below the picture's middle"""
    return {'yaw': yaw, 'rel': 'head', 'pitch': pitch, 'joint': 'Head', 'offset': [0, HEAD_UP + down_px / px * K, 0], 'dist': 6, 'height': H / px * K}


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


def fig_cam(yaw, H=900):
    # the sheet: floor at H − 90 px, S px per unit → the picture's middle is (H/2 − 90) / S units above the floor
    return {'yaw': yaw, 'rel': 'body', 'follow': [0, (H / 2 - 90) / S * K, 0], 'dist': 6, 'height': H / S * K}


def turn():
    D = Image.open(f'{CACHE}/drawn/{char.NAME}-turnaround.png' if char.DRAWN_TURN else f'{RENDER}/{char.NAME}-turnaround.png').convert('RGB')
    views = [('front', 0.0, 270), ('tq', -0.62, 750), ('side', -1.5708, 1230)]
    R = shots('cmp_turn', 480, 900, [{'name': n, 'set': {'cam': fig_cam(y), 'expr': [{'t': 0, 'name': 'calm'}]}} for n, y, _ in views])
    rows = []
    for n, y, cx in views:
        d = D.crop((cx - 240, 0, cx + 240, 900))
        rows.append(np.concatenate([np.asarray(i) for i in triple(d, R[n])], 1))
    out = Image.fromarray(np.concatenate(rows, 0)).resize((864, 1620), Image.LANCZOS)
    out.save(f'{PICS}/cmp-turn.webp', quality=86)


def expr():
    # the sheet: 2.3 px per unit, the head's centre at y 250 px of 560, each face 400 px wide, turned 0.18
    D = Image.open(f'{CACHE}/drawn/{char.NAME}-expressions.png' if char.DRAWN_EXPR else f'{RENDER}/{char.NAME}-expressions.png').convert('RGB')
    names = ['joy', 'surprise', 'sad', 'anger']
    R = shots('cmp_expr', 400, 560, [{'name': n, 'set': {'cam': head_cam(-0.18, 2.3, 280 - 250, 560, -0.06 if n == 'sad' else 0),
                                                            'expr': [{'t': 0, 'name': n}]}} for n in names])
    top = np.concatenate([np.asarray(D.crop((400 * i, 0, 400 * i + 400, 560))) for i in range(4)], 1)
    bot = np.concatenate([np.asarray(R[n]) for n in names], 1)
    out = Image.fromarray(np.concatenate([top, bot], 0)).resize((1200, 840), Image.LANCZOS)
    out.save(f'{PICS}/cmp-expr.webp', quality=86)


def portrait():
    # the sheet: 2.75 px per unit, the head's centre at y 285 px of 760, turned as build.PORTRAIT
    D = Image.open(f'{RENDER}/{char.NAME}-portrait.png').convert('RGB')
    R = shots('cmp_portrait', 640, 760, [{'name': 'p', 'set': {'cam': head_cam(char.PORTRAIT_YAW, 2.75, 380 - 285, 760),
                                                              'expr': [{'t': 0, 'name': char.PORTRAIT_EXPR}], **char.PORTRAIT_SET}}])
    out = Image.fromarray(np.concatenate([np.asarray(i) for i in triple(D, R['p'])], 1)).resize((1440, 570), Image.LANCZOS)
    out.save(f'{PICS}/cmp-portrait.webp', quality=86)


def figure():
    D = Image.open(f'{RENDER}/{char.NAME}-figure.png').convert('RGB')
    R = shots('cmp_figure', 620, 900, [{'name': 'f', 'set': {'cam': fig_cam(char.PORTRAIT_YAW), 'expr': [{'t': 0, 'name': char.PORTRAIT_EXPR}], **char.PORTRAIT_SET}}])
    out = Image.fromarray(np.concatenate([np.asarray(i) for i in triple(D, R['f'])], 1)).resize((1240, 600), Image.LANCZOS)
    out.save(f'{PICS}/cmp-figure.webp', quality=86)


if __name__ == '__main__':
    for k in sys.argv[1:]: globals()[k]()
