"""Drawing / 3D / overlay sheets.
python3 compare.py out.jpg drawing.jpg "x0,y0,x1,y1;…" render1.png render2.png …  [--labels a,b,c] [--width W]
Each crop of the drawing is set over its render: row 1 the drawing, row 2 the render, row 3 the render's ink lines in red
over the drawing made pale (the renders are taken with the drawing's own camera: same scale, same place)."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

args = [a for a in sys.argv[1:] if not a.startswith('--')]
opts = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--'))
out, drawing, boxes, renders = args[0], Image.open(args[1]).convert('RGB'), [tuple(map(int, b.split(','))) for b in args[2].split(';')], args[3:]
labels = opts.get('labels', '').split(',') if 'labels' in opts else None
cells = []
for box, rp in zip(boxes, renders):
    d = drawing.crop(box)
    r = Image.open(rp).convert('RGB').resize(d.size, Image.LANCZOS)
    a = np.asarray(r).astype(np.float32)
    ink = (a.sum(2) / 3 < 48)
    pale = np.asarray(d).astype(np.float32) * 0.35 + 255 * 0.65
    pale[ink] = [205, 30, 30]
    cells.append((d, r, Image.fromarray(pale.astype(np.uint8))))
w, h = cells[0][0].size
sheet = Image.new('RGB', (w * len(cells), h * 3), 'white')
for i, (d, r, o) in enumerate(cells):
    for k, im in enumerate((d, r, o)):
        sheet.paste(im, (i * w, k * h))
if labels:
    dr = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', max(14, h // 36))
    except OSError:
        f = ImageFont.load_default()
    for i, lab in enumerate(labels):
        for k, t in enumerate(('рисунок', '3D', 'наложение')):
            dr.text((i * w + 10, k * h + 8), f'{lab}: {t}', fill=(60, 50, 40), font=f)
W = int(opts.get('width', 1500))
if sheet.width > W:
    sheet = sheet.resize((W, int(sheet.height * W / sheet.width)), Image.LANCZOS)
sheet.save(out, quality=86)
