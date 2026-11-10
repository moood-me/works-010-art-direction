"""The page's pictures from the renders: the comparison sheets (stills.py) as webp, and the cover."""
import os
from PIL import Image
from common import CACHE, FOLDER

S = os.path.join(CACHE, 'stills'); P = os.path.join(FOLDER, 'pics')
for n in ('turn', 'portrait', 'figure', 'expr'):
    im = Image.open(os.path.join(S, f'cmp-{n}.jpg')).convert('RGB')
    k = min(1.0, 1800 / max(im.size))
    im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS).save(os.path.join(P, f'cmp-{n}.webp'), quality=82)
im = Image.open(os.path.join(S, 'portrait-3d.png')).convert('RGB')
im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS).save(os.path.join(P, 'cover.webp'), quality=85)
print('pics written')
