"""The steps' pictures: what each base gave and what was done to it."""
import json, subprocess, os
from PIL import Image, ImageDraw, ImageFont
from common import CACHE, HERE
from compose import compose

PICS = os.path.join(os.path.dirname(HERE), 'pics')
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 22)
CREAM = (243, 234, 214)


def shoot(job, out):
    json.dump(job, open(f'{CACHE}/job_steps.json', 'w'))
    subprocess.run(['node', f'{HERE}/shots.mjs', f'{CACHE}/job_steps.json', out], check=True, capture_output=True)


def row(ims, caps, h=None, bg=CREAM):
    ims = [i.convert('RGBA') for i in ims]
    if h: ims = [i.resize((round(i.width * h / i.height), h)) for i in ims]
    W = sum(i.width for i in ims); H = max(i.height for i in ims) + 40
    S = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(S); x = 0
    for i, c in zip(ims, caps):
        S.paste(i, (x, 40), i); d.text((x + 10, 8), c, fill=(42, 32, 28), font=F); x += i.width
    return S


def stack(rows, path):
    W = max(r.width for r in rows); S = Image.new('RGB', (W, sum(r.height for r in rows)), CREAM); y = 0
    for r in rows: S.paste(r, (0, y)); y += r.height
    S.save(path, quality=88, method=6)


subprocess.run(['python3', f'{HERE}/step_body.py'], check=True, capture_output=True)
c = {'clay': True, 'live': False}
shoot({'w': 420, 'h': 640, 'shots': [
    {'name': 'anny', 'set': {**c, 'model': '/cache/to3d-r29-s9-anya/step-anny.json', 'cam': {'yaw': 0, 'target': [0, 0.87, 0], 'height': 1.9}}},
    {'name': 'fit', 'set': {**c, 'model': '/cache/to3d-r29-s9-anya/step-fit.json', 'cam': {'yaw': 0, 'target': [0, 0.87, 0], 'height': 1.9}}},
    {'name': 'fitside', 'set': {**c, 'model': '/cache/to3d-r29-s9-anya/step-fit.json', 'cam': {'yaw': -1.5708, 'target': [0, 0.87, 0], 'height': 1.9}}},
    {'name': 'clay', 'set': {**c, 'model': '/cache/to3d-r29-s9-anya/anya.json', 'motion': ['bow'], 't': 0, 'cam': {'yaw': -0.45, 'follow': [0, 0.87, 0], 'height': 1.9}}},
    {'name': 'paint', 'set': {'clay': False, 'live': False, 'face': '/cache/to3d-r29-s9-anya/face/calm.png', 'cam': {'yaw': -0.45, 'follow': [0, 0.87, 0], 'height': 1.9}}},
]}, f'{CACHE}/steps')
stack([row([Image.open(f'{CACHE}/steps/{n}.png') for n in ('anny', 'fit', 'fitside')],
           ['Anny, женщина (moood-woman), 1,59 м', 'подогнана: длинная, узкая', 'она же сбоку'])], f'{PICS}/step-body.webp')
stack([row([Image.open(f'{CACHE}/head_{k}.png').crop((0, 0, 1800, 600))], [cap], h=400) for k, cap in (
    ('orig', 'Human Base Meshes, стилизованная голова (CC0): как есть'),
    ('faired', 'лицо вырезано и закрыто гладкой заплатой (черты будут нарисованы)'),
    ('warped', 'согнута по контурам рисунка анфас и в профиль (красная линия — контур рисунка)'))], f'{PICS}/step-head.webp')
faces = [Image.alpha_composite(Image.new('RGBA', (1024, 1024), (246, 215, 191, 255)), Image.open(f'{CACHE}/face/{e}.png').convert('RGBA')).crop((160, 180, 864, 900))
         for e in ('calm', 'joy', 'surprise', 'sad', 'anger')]
stack([row(faces, ['спокойно', 'радость', 'удивление', 'грусть', 'злость'], h=300)], f'{PICS}/step-face.webp')
compose(f'{CACHE}/steps/gouache.png', 420, 640, 'portrait', [(f'{CACHE}/steps/paint.png', 0, 0)])
stack([row([Image.open(f'{CACHE}/steps/{n}.png') for n in ('clay', 'paint', 'gouache')],
           ['собран: форма', 'краски шейдера', 'на фоне рисунка, фильтр гуаши'], bg=(236, 159, 147))], f'{PICS}/step-paint.webp')
print('ok')
