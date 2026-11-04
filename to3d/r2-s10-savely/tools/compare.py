"""Side by side and overlaid: the drawing's panels and the renders of the same views.
usage: python3 compare.py OUT.png DRAWING.png "x0,y0,w,h;..." RENDER1.png RENDER2.png ... [--labels a,b,c] [--rows draw,render,overlay]
Each crop box of the drawing goes with one render (same size); rows: the drawing, the render, the two overlaid
(the render's ink lines in red over the drawing faded)."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

args = [a for a in sys.argv[1:] if not a.startswith('--')]
opts = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--'))
out, drawing, boxes = args[0], Image.open(args[1]).convert('RGB'), [tuple(map(int, b.split(','))) for b in args[2].split(';')]
renders = [Image.open(p).convert('RGB') for p in args[3:]]
rows = opts.get('rows', 'draw,render,overlay').split(',')
labels = opts['labels'].split(',') if 'labels' in opts else None
cw, ch = boxes[0][2], boxes[0][3]
pad = 6
top = 30 if labels else 0
ROW = opts.get('layout') == 'row'          # one row: each box's drawing, render, overlay side by side
W = len(boxes) * (cw + pad) + pad if not ROW else len(boxes) * len(rows) * (cw + pad) + pad
H = top + len(rows) * (ch + pad) + pad if not ROW else top + ch + 2 * pad
sheet = Image.new('RGB', (W, H), '#f4ecd8')
dr = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
except OSError:
    font = ImageFont.load_default()
for i, (b, r) in enumerate(zip(boxes, renders)):
    x0, y0, w, h = b
    crop = drawing.crop((x0, y0, x0 + w, y0 + h))
    r = r.resize((w, h))
    x0 = pad + i * (cw + pad) * (len(rows) if ROW else 1)
    if labels:
        dr.text((x0 + 4, 6), labels[i], fill='#1b1714', font=font)
    for j, kind in enumerate(rows):
        x = x0 + j * (cw + pad) if ROW else x0
        y = top + pad if ROW else top + pad + j * (ch + pad)
        if kind == 'draw':
            sheet.paste(crop, (x, y))
        elif kind == 'render':
            sheet.paste(r, (x, y))
        else:
            a = np.asarray(crop, float)
            g = a.mean(2, keepdims=True)
            base = 255 - (255 - g) * 0.45                     # the drawing faded to grey
            ink = np.linalg.norm(np.asarray(r, float) - [27, 23, 20], axis=2) < 45   # the render's ink lines
            o = np.repeat(base, 3, 2)
            o[ink] = [215, 40, 30]
            sheet.paste(Image.fromarray(o.astype(np.uint8)), (x, y))
sheet.save(out)
