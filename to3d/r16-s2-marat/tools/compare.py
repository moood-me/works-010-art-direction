"""Puts the drawing and the 3D pictures (shots.mjs → final/) side by side and over each other → ../pics.
  python3 compare.py /home/user/cache/to3d-r15-s2-savely/final"""
import os, sys
from PIL import Image
src = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
PICS = os.path.join(HERE, '..', 'pics'); os.makedirs(PICS, exist_ok=True)
STYLE = os.path.join(HERE, '..', '..', '..', 'styles', 's2-klaus', 'pics')
R = lambda n: Image.open(os.path.join(src, n + '.png')).convert('RGB')
D = lambda n: Image.open(os.path.join(STYLE, n + '.png')).convert('RGB')


def row(ims, gap=0, bg=(30, 22, 30)):
    h = max(i.height for i in ims); w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    out = Image.new('RGB', (w, h), bg); x = 0
    for i in ims: out.paste(i, (x, 0)); x += i.width + gap
    return out


def save(im, name, q=86, maxw=2000):
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(os.path.join(PICS, name + '.webp'), quality=q, method=6); print(name, im.size)


if __name__ == '__main__':
    dp, df = D('portrait-savely'), D('figure-savely')
    save(row([dp, R('head-q'), R('head-f'), R('head-s')], 6), 'cmp-head')
    save(row([dp, Image.blend(dp, R('head-q'), 0.5), R('head-q')], 6), 'ov-head', maxw=1512)
    save(row([df, R('fig-q'), R('fig-f'), R('fig-s'), R('fig-b')], 6), 'cmp-fig')
    save(row([df, Image.blend(df, R('fig-q'), 0.5), R('fig-q')], 6), 'ov-fig', maxw=1512)
    save(row([R('e-' + e) for e in ('calm', 'kind', 'surprise', 'sad', 'anger')], 6), 'expr')
    save(row([R('light-1'), R('light-2'), R('light-3')], 6), 'light-steps', maxw=1512)
    save(R('close'), 'close')
    save(R('close').crop((60, 40, 740, 800)), 'cover', maxw=680)
