"""The steps along the way, for the page → ../pics/steps-body.webp, steps-head.webp (the packs come from
`build.py steps`): what each base gave."""
import json, os
from PIL import Image, ImageDraw
from common import CACHE, HERE, heavy
from compare import FONT, PICS, save

M = '/cache/to3d-r14-s14-kira/'
BG = (213, 217, 196)


def row(name, items, W, H):
    shots = [{'name': f'{name}{i}', 'set': s} for i, (s, _) in enumerate(items)]
    json.dump({'w': W, 'h': H, 'set': {'still': True, 'ground': False}, 'shots': shots}, open(f'{CACHE}/job_{name}.json', 'w'))
    heavy(['node', f'{HERE}/shots.mjs', f'{CACHE}/job_{name}.json', f'{CACHE}/steps'], check=True)
    out = Image.new('RGBA', (W * len(items), H + 46), BG + (255,))
    d = ImageDraw.Draw(out)
    for i, (_, label) in enumerate(items):
        out.alpha_composite(Image.open(f'{CACHE}/steps/{name}{i}.png').convert('RGBA'), (i * W, 0))
        d.text((i * W + W / 2, H + 8), label, fill=(91, 74, 60), font=FONT, anchor='ma')
    return out


def close():
    """how the paper looks near: the head's sheets, the pocket and strings, the back"""
    st = {'motion': ['bow'], 't': 0}
    items = [({**st, 'cam': {'yaw': -0.55, 'joint': 'Head', 'offset': [0, 0.02, 0], 'height': 0.5}}, 'листы волос, чёлка бросает тень'),
             ({**st, 'cam': {'yaw': 0.75, 'joint': 'Head', 'offset': [0, 0.02, 0], 'height': 0.5}}, 'с её левой стороны: прядь и ухо'),
             ({**st, 'cam': {'yaw': -0.35, 'joint': 'Chest', 'offset': [0, -0.05, 0], 'height': 0.62}}, 'наушники, шнурки, карман'),
             ({**st, 'cam': {'yaw': 2.6, 'joint': 'Chest', 'offset': [0, 0.12, 0], 'height': 0.8}}, 'сзади: капюшон, зубцы волос')]
    save(row('cl', items, 560, 560), 'paper-close', 1700)



if __name__ == '__main__':
    body = lambda y=0.78, h=1.75: {'yaw': -0.5, 'follow': [0, y, 0], 'height': h}
    head = {'yaw': -0.5, 'joint': 'Head', 'offset': [0, 0.04, 0], 'height': 0.52}
    save(row('sb', [
        ({'model': M + 'step-anny.json', 'clay': True, 'face': False, 'cam': body()}, 'тело Anny (девочка)'),
        ({'model': M + 'step-fit.json', 'clay': True, 'face': False, 'cam': body()}, 'по рисунку: тонкая, длиннорукая'),
        ({'model': M + 'step-legs.json', 'clay': False, 'cam': body()}, 'голова и куски бумаги поверх тела'),
        ({'model': '../../data/kira.json', 'clay': False, 'motion': ['bow'], 't': 0, 'cam': body()}, 'сутулость и поза Kimodo'),
    ], 440, 760), 'steps-body', 1600)
    save(row('sh', [
        ({'model': M + 'step-head0.json', 'clay': True, 'face': False, 'cam': head}, 'голова-основа, лицо заглажено'),
        ({'model': M + 'step-head1.json', 'clay': True, 'face': False, 'cam': head}, 'подогнана к рисунку'),
        ({'model': M + 'step-head.json', 'clay': True, 'face': False, 'cam': head}, 'уши и нос — куски бумаги'),
        ({'model': M + 'step-head.json', 'clay': False, 'cam': head}, 'лицо: куски рисунка'),
        ({'model': M + 'step-hair.json', 'clay': False, 'cam': head}, 'волосы — три листа'),
    ], 440, 480), 'steps-head', 1600)
    close()
