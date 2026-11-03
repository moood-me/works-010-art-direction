# python3 sheet.py out.webp cols cellW "img|caption" ...  — pictures in a grid, a caption under each
import sys
from PIL import Image, ImageDraw, ImageFont
out, cols, cw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
items = [a.split('|', 1) for a in sys.argv[4:]]
ims = [Image.open(p).convert('RGB') for p, _ in items]
ch = max(round(cw * im.height / im.width) for im in ims)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', max(14, cw // 22))
pad = font.size + 14
rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (cols * cw, rows * (ch + pad)), '#f4f1ec')
d = ImageDraw.Draw(S)
for i, (im, (_, cap)) in enumerate(zip(ims, items)):
    x, y = (i % cols) * cw, (i // cols) * (ch + pad)
    h = round(cw * im.height / im.width)          # each keeps its own shape, set on its background colour
    cell = Image.new('RGB', (cw, ch), im.getpixel((2, 2))); cell.paste(im.resize((cw, h), Image.LANCZOS), (0, (ch - h) // 2)); S.paste(cell, (x, y))
    d.text((x + cw / 2, y + ch + pad / 2), cap, fill='#2a2622', font=font, anchor='mm')
S.save(out, quality=86)
