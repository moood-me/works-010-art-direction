# python3 grid.py out.png cols cellw img1 [label1] ...   (pairs "path::label")
import sys
from PIL import Image, ImageDraw, ImageFont
out, cols, cw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
items = [a.split('::') for a in sys.argv[4:]]
ims = [Image.open(p).convert('RGB') for p, *_ in items]
ch = int(cw * ims[0].height / ims[0].width)
rows = (len(ims) + cols - 1) // cols
G = Image.new('RGB', (cols * cw, rows * ch), (235, 234, 230))
try: F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', max(14, cw // 22))
except Exception: F = ImageFont.load_default()
d = ImageDraw.Draw(G)
for i, (im, it) in enumerate(zip(ims, items)):
    x, y = (i % cols) * cw, (i // cols) * ch
    G.paste(im.resize((cw, ch), Image.LANCZOS), (x, y))
    if len(it) > 1:
        tw = d.textlength(it[1], font=F); d.rectangle([x + 6, y + 6, x + 16 + tw, y + 12 + F.size], fill=(255, 255, 255))
        d.text((x + 11, y + 8), it[1], fill=(30, 30, 30), font=F)
G.save(out, quality=88) if out.endswith(('.jpg', '.webp')) else G.save(out)
