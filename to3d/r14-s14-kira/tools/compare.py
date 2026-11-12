"""The drawing and the 3D side by side and overlaid, in the drawing's own views and scale → ../pics.
   python3 compare.py turn | figure | expr
turn, expr: the upright figure (the sheets draw the head straight), at rest, an orthographic camera placed so that a
head unit is as many pixels as on the sheet. figure: the slouching figure in a moment of Kimodo's idle, on the
drawing's own sheet (its mat and floor strip), her shadow on it."""
import sys, json, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from common import CACHE, HERE, STYLE, heavy
from drawing import K, U

PICS = os.path.join(os.path.dirname(HERE), 'pics')
O = np.load(f'{CACHE}/build.npz')['O']
UP = '/cache/to3d-r14-s14-kira/kira-up.json'
YAW = [0, -0.42, -1.5708]
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 20) if os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf') else ImageFont.load_default()


def shoot(name, job):
    json.dump(job, open(f'{CACHE}/cmp-{name}.json', 'w'))
    heavy(['node', f'{HERE}/shots.mjs', f'{CACHE}/cmp-{name}.json', f'{CACHE}/cmp'], check=True)


def bust_cam(yaw, s, cy, h):
    """the camera that sees a bust as the sheet draws it: s px per head unit, the head's centre cy px from the top"""
    ppm = s / K
    return {'yaw': yaw, 'target': [0, float(O[1]) - (h / 2 - cy) / ppm, float(O[2])], 'height': h / ppm}


def label(im, x, y, text):
    ImageDraw.Draw(im).text((x, y), text, fill=(91, 74, 60), font=FONT, anchor='ma')


def save(im, name, w=None):
    if w and im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.convert('RGB').save(f'{PICS}/{name}.webp', quality=88); print(name, im.size)


def turn():
    W, H = 490, 720
    shoot('turn', {'w': W, 'h': H, 'set': {'model': UP, 'still': True, 'ground': False}, 'shots': [{'name': f'turn{i}', 'set': {'cam': bust_cam(y, 1.45, 300, H)}} for i, y in enumerate(YAW)]})
    dr = Image.open(f'{STYLE}/pics/turn-kira.webp').convert('RGBA')
    bd = Image.open(f'{CACHE}/bd-wide.png').convert('RGBA')
    out = Image.new('RGBA', (W * 3, H * 3 - 2 * 60), 'white')
    row3 = bd.copy(); row2 = bd.copy()
    for i in range(3):
        r = Image.open(f'{CACHE}/cmp/turn{i}.png').convert('RGBA')
        row3.alpha_composite(r, (i * W, 0))
        row2.alpha_composite(dr.crop((15 + i * W, 0, 15 + (i + 1) * W, H)), (i * W, 0))
        g = r.copy(); g.putalpha(g.getchannel('A').point(lambda a: a * 0.55)); row2.alpha_composite(g, (i * W, 0))
    out.alpha_composite(dr.crop((15, 0, 15 + 3 * W, H - 60)), (0, 0)); out.alpha_composite(row3.crop((0, 0, 3 * W, H - 60)), (0, H - 60)); out.alpha_composite(row2, (0, 2 * H - 120))
    for i, t in enumerate(('рисунок', '3D', '3D поверх рисунка')): label(out, 70, 14 + i * (H - 60), t)
    save(out, 'compare-turn', 1300)
    save(row3.crop((0, 0, 3 * W, H - 60)), 'turn3d', 1300)


def expr():
    W, H = 400, 560; names = ['joy', 'surprise', 'sad', 'angry']
    shoot('expr', {'w': W, 'h': H, 'set': {'model': UP, 'still': True, 'ground': False}, 'shots': [{'name': f'expr-{n}', 'set': {'expr': n, 'cam': bust_cam(0, 1.12, 230, H)}} for n in names]})
    dr = Image.open(f'{STYLE}/pics/expr-kira.webp').convert('RGBA')
    bd = Image.open(f'{CACHE}/bd-expr.png').convert('RGBA')
    for i, n in enumerate(names): bd.alpha_composite(Image.open(f'{CACHE}/cmp/expr-{n}.png').convert('RGBA'), (i * W, 0))
    for i, t in enumerate(('усмешка (её «радость»)', 'удивление', 'грусть', 'злость')): label(bd, 200 + i * W, 520, t)
    out = Image.new('RGBA', (1600, 1120), 'white'); out.alpha_composite(dr, (0, 0)); out.alpha_composite(bd, (0, 560))
    label(out, 60, 10, 'рисунок'); label(out, 40, 570, '3D')
    save(out, 'compare-expr', 1400); save(bd, 'expr3d', 1400)


def figure(motion='bow', t=0, yaw=-0.62, heading=0.0):
    W, H = 800, 1000; ppm = 1.346 / U
    cam = {'yaw': yaw, 'pitch': 0.10, 'follow': [0.02, (H / 2 - (H - 880)) / ppm, 0], 'height': H / ppm}
    shoot('figure', {'w': W, 'h': H, 'set': {'still': True, 'ground': 'shadow'}, 'shots': [{'name': 'figure', 'set': {'motion': [motion], 't': t, 'cam': cam}}]})
    bd = Image.open(f'{CACHE}/bd-figure.png').convert('RGBA'); r = Image.open(f'{CACHE}/cmp/figure.png').convert('RGBA')
    f3 = bd.copy(); f3.alpha_composite(r)
    dr = Image.open(f'{STYLE}/pics/figure-kira.webp').convert('RGBA')
    ov = dr.copy(); g = r.copy(); g.putalpha(g.getchannel('A').point(lambda a: a * 0.55)); ov.alpha_composite(g)
    out = Image.new('RGBA', (W * 3, H), 'white')
    for i, im in enumerate((dr, f3, ov)): out.alpha_composite(im, (i * W, 0))
    for i, tx in enumerate(('рисунок', '3D', '3D поверх рисунка')): label(out, 130 + i * W, 60, tx)
    save(out, 'compare-figure', 1500); save(f3, 'figure3d')


if __name__ == '__main__':
    for a in sys.argv[1:]: dict(turn=turn, expr=expr, figure=figure)[a]()
