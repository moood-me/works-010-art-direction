"""The steps, in clay, so one sees what each base gave: the head (Human Base Meshes as it is → its smooth form laid on
the drawing's loft → the sculptor's detail back, glass eyes, the lids on them → the replacement pieces and the hair)
and the body (Anny's child as it is → fitted to the drawing → dressed). Quick pictures (look.py's z-buffer)."""
import json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import base, drawing, look
import fit_body
from common import CACHE, FOLDER, pack, HH, BID

FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
CLAY, SKIN, HAIR = (0.84, 0.8, 0.74), (0.86, 0.66, 0.52), (0.2, 0.16, 0.15)
COL = dict(skin=(0.86, 0.66, 0.52), eye=(0.95, 0.95, 0.97), curl=(0.2, 0.16, 0.15), hairmass=(0.14, 0.11, 0.1), brow=(0.14, 0.1, 0.1), lip=(0.7, 0.36, 0.32), mouth=(0.25, 0.1, 0.1),
           tongue=(0.66, 0.27, 0.3), lash=(0.12, 0.08, 0.07), jacket=(0.93, 0.89, 0.82), apron=(0.77, 0.35, 0.18), aprontie=(0.66, 0.3, 0.15), towel=(0.97, 0.95, 0.9),
           trousers=(0.34, 0.31, 0.3), shoe=(0.23, 0.17, 0.13), sole=(0.12, 0.1, 0.1))


def label(im, text):
    W, H = im.size
    out = Image.new('RGB', (W, H + 34), (244, 238, 226)); out.paste(im, (0, 34))
    ImageDraw.Draw(out).text((10, 7), text, fill=(40, 32, 26), font=FONT)
    return out


def row(ims, out):
    W = sum(i.width for i in ims); H = max(i.height for i in ims)
    S = Image.new('RGB', (W, H), (244, 238, 226)); x = 0
    for i in ims: S.paste(i, (x, 0)); x += i.width
    S.save(out, quality=86)


def sphere(c, r, n=24):
    th = np.linspace(0, np.pi, n); ph = np.linspace(0, 2 * np.pi, n)
    P_ = np.array([[np.sin(t) * np.cos(p), np.cos(t), np.sin(t) * np.sin(p)] for t in th for p in ph]) * r + c
    T = []
    for i in range(n - 1):
        for j in range(n - 1):
            a = i * n + j; T += [[a, a + n, a + 1], [a + 1, a + n, a + n + 1]]
    return P_, np.array(T)


def head_steps():
    B = base.load(); box = (-0.62, 0.62, -0.8, 0.62)
    ims = []
    eyes = [(B['eye' + s][0], base.tris(B['eye' + s][1]), (0.95, 0.95, 0.97)) for s in 'LR']
    ims.append(label(look.raster([(B['V'], base.tris(B['Q']), CLAY)] + eyes, 30, box, 380), '1. основа: голова HBM как есть'))
    d = np.load(f'{CACHE}/head_raw.npz'); T = base.tris(d['Q'])
    S1 = np.r_[d['S1'], d['V'][len(d['S1']):]]
    LV, LT = drawing.loft_mesh(80, 60)
    ims.append(label(look.raster([(S1, T, CLAY)], 30, box, 380,
                                 lines=[(drawing.eye_opening(s)[0], (190, 60, 40)) for s in (-1, 1)]), '2. её гладкая форма на голове рисунка'))
    eyes = [(*sphere(drawing.eye_centre(s), drawing.EYE_R), (0.95, 0.95, 0.97)) for s in (-1, 1)]
    ims.append(label(look.raster([(d['V'], T, CLAY)] + eyes, 30, box, 380), '3. детали скульптора, стеклянные глаза'))
    M = json.load(open(f'{CACHE}/model.json'))
    _, a = pack.read(f'{CACHE}/engine/data/bodies/{BID}.json'); _, t = pack.read(f'{CACHE}/engine/data/topology/{BID}.json')
    V = (a['positions'].astype(float) - np.array(M['O'])) / HH; TT = t['triangles'].astype(int)
    C = COL
    mm = []
    for p in M['pieces']:
        if p['name'] in ('skin', 'neck') or p['mat'] not in C or p['mat'] in ('jacket', 'apron', 'aprontie', 'towel', 'trousers', 'shoe', 'sole'): continue
        s, n = p['start'], p['count']; m = (TT[:, 0] >= s) & (TT[:, 0] < s + n); mm.append((V[s:s + n], TT[m] - s, C[p['mat']]))
    ims.append(label(look.raster(mm, 30, box, 380), '4. сменные рот, брови и усы; кудри и борода'))
    row(ims, os.path.join(FOLDER, 'pics', 'steps-head.webp'))


def body_steps():
    B = fit_body.B; box = (-0.75, 0.75, -0.02, 1.8)
    ims = [label(look.raster([(B['positions'], B['triangles'], CLAY)], 25, box, 340), '1. основа: мужчина Anny')]
    V, J = fit_body.fit()
    box = (-0.65, 0.65, -0.02, 1.45)
    ims.append(label(look.raster([(V, B['triangles'], CLAY)], 25, box, 340), '2. пропорции рисунка'))
    M = json.load(open(f'{CACHE}/model.json'))
    _, a = pack.read(f'{CACHE}/engine/data/bodies/{BID}.json'); _, t = pack.read(f'{CACHE}/engine/data/topology/{BID}.json')
    P_ = a['positions'].astype(float); TT = t['triangles'].astype(int)
    C = COL
    mm = []
    for p in M['pieces']:
        s, n = p['start'], p['count']; m = (TT[:, 0] >= s) & (TT[:, 0] < s + n); mm.append((P_[s:s + n], TT[m] - s, C.get(p['mat'], CLAY)))
    ims.append(label(look.raster(mm, 25, box, 340), '3. голова, одежда из чисел рисунка'))
    row(ims, os.path.join(FOLDER, 'pics', 'steps-body.webp'))


if __name__ == '__main__':
    head_steps(); body_steps()
