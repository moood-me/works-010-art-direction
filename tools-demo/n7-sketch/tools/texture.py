# The colours for the inflated model: our front picture, as Monster Mash's own "template image" texture,
# with our dark outline line around the silhouette taken out (it would lie on the surface as a dark band)
# and the colours spread a little past the silhouette (the traced outlines are not pixel-exact).
# usage: python3 texture.py <workdir> <name>  -> <workdir>/<name>/tex.png
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

work, name = sys.argv[1], sys.argv[2]
im = Image.open(os.path.join(work, f'our-{name}-front.png')).convert('RGB')
a = np.asarray(im).astype(float)
# the background: greyish beige pixels (backdrop, floor, shadow) connected to the picture's border
sat = a.max(2) - a.min(2); lum0 = a @ [0.3, 0.59, 0.11]
like = Image.fromarray((((sat < 30) & (lum0 > 120) & (lum0 < 228)) * 255).astype(np.uint8)).copy()
# seeds: the border, and pixels of the backdrop's or floor's very colour (backdrop seen between the legs)
seeds = [(1, 1), (like.width - 2, 1), (1, like.height - 2), (like.width - 2, like.height - 2)]
ref = [a[2, 2], a[-3, -3]]
close = np.zeros(a.shape[:2], bool)
for r in ref: close |= np.abs(a - r).max(2) < 8
close = np.asarray(Image.fromarray(close.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(15))) > 0   # only wide patches of it
ys, xs = np.nonzero(close); seeds += list(zip(xs[::37].tolist(), ys[::37].tolist()))
for c in seeds:
    if like.getpixel(c) == 255: ImageDraw.floodfill(like, c, 128)
bg = np.asarray(like) == 128
near = np.asarray(Image.fromarray((bg * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(11))) > 0
lum = a @ [0.3, 0.59, 0.11]
ink = near & ((lum < 80) | ((sat < 45) & (lum < 170))) & ~bg
valid = ~bg & ~ink
import json
if json.load(open(os.path.join(work, name, 'frame.json')))['thin']:
    # thin dark lines inside the figure (where one part overlaps another) are lines of the drawing, not colour
    dark = Image.fromarray((((lum < 80) & ~bg) * 255).astype(np.uint8))
    thick = np.asarray(dark.filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(9))) > 0
    valid &= ~((lum < 80) & ~thick)
# an ink pixel whose inner neighbours are dark too (hooves, claws) is the thing's own colour, not a line: keep it
dark_inside = np.asarray(Image.fromarray(((lum < 80) & ~bg).astype(np.uint8) * 255).filter(ImageFilter.MinFilter(9))) > 0
valid |= ink & np.asarray(Image.fromarray(dark_inside.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(9))) > 0
col = a * valid[..., None]; w = valid.astype(float)
for it in range(40):
    s = np.zeros_like(col); sw = np.zeros_like(w)
    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
        s += np.roll(np.roll(col * w[..., None], dy, 0), dx, 1); sw += np.roll(np.roll(w, dy, 0), dx, 1)
    fill = (w == 0) & (sw > 0)
    col[fill] = s[fill] / sw[fill, None]; w = w.copy(); w[fill] = 1
Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).save(os.path.join(work, name, 'tex.png'))
