"""Pictures of the steps (quick software renders, clay): what each base gave and how it was fitted.
  step-head.webp: the Human Base Meshes head as it comes · shaped to the drawn ball · the eyes made the drawing's ·
                  the nose, mouth and ears moved; the drawing's head outline in red
  step-body.webp: Anny's child as it comes · fitted to the drawing's proportions"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from common import CACHE, HERE, K
from look import views
from sphere import sphere
from drawing import head_mesh
from mesh import raster

PICS = os.path.join(os.path.dirname(HERE), 'pics')
try: FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
except Exception: FONT = None


def lab(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, im.width, 34), fill=(255, 255, 255)); d.text((10, 6), t, fill=(30, 40, 50), font=FONT); return im


def head():
    from hbm import load
    B = load(); T = B['head'][1]; f = np.load(f'{CACHE}/head_fit.npz')
    DV, DT = head_mesh(); DV = np.c_[DV[:, 0], -DV[:, 1], DV[:, 2]]
    rows = []
    stages = [('base', 'база: стилизованная голова HBM', [B['eyeL'][:2], B['eyeR'][:2]]),
              ('shaped', 'форма — шар рисунка', None), ('eyes', 'глаза: шары и веки рисунка', 'balls'), ('final', 'нос, рот, уши на места', 'balls')]
    for key, title, eyes in stages:
        ms = [(f[key], T, [0.84, 0.82, 0.8])]
        if eyes == 'balls': ms += [(*sphere(f['balls'][i, :3], f['balls'][i, 3]), [0.95, 0.95, 0.97]) for i in range(2)]
        elif eyes: ms += [(e[0], e[1], [0.95, 0.95, 0.97]) for e in eyes]
        im = views(ms, yaws=(0, -1.5708), size=300, box=(-58, 58, -62, 54), overlay=(DV, DT))
        rows.append(lab(im, title))
    W = rows[0].width
    out = Image.new('RGB', (W * 2, rows[0].height * 2), 'white')
    for i, r in enumerate(rows): out.paste(r, ((i % 2) * W, (i // 2) * r.height))
    out.save(f'{PICS}/step-head.webp', quality=86)


def body():
    from fitbody import B, fit
    V0 = B['positions']; T = B['triangles']; V1, _ = fit()
    ims = []
    for V, t in ((V0, 'Anny, ребёнок 1,31 м'), (V1, 'подогнан к рисунку')):
        a, _ = raster(V, T, yaw=0, size=330, box=(-0.7, 0.7, -0.05, 1.35))
        b, _ = raster(V, T, yaw=1.5708, size=330, box=(-0.7, 0.7, -0.05, 1.35))
        ims.append(lab(Image.fromarray(np.concatenate([a, b], 1)), t))
    out = Image.new('RGB', (ims[0].width * 2, ims[0].height), 'white')
    for i, im in enumerate(ims): out.paste(im, (i * im.width, 0))
    out.save(f'{PICS}/step-body.webp', quality=86)


if __name__ == '__main__':
    head(); body()
