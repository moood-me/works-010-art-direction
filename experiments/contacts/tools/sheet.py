# A sheet: pictures side by side in rows, each with a small caption.
#   python3 tools/sheet.py out.png cols "caption|file" "caption|file" …
import sys
from PIL import Image, ImageDraw, ImageFont

out, cols, items = sys.argv[1], int(sys.argv[2]), [a.split('|', 1) for a in sys.argv[3:]]
ims = [(c, Image.open(f).convert('RGB')) for c, f in items]
w, h = ims[0][1].size
rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (w * cols, h * rows), '#cfc8bd')
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
except OSError: font = ImageFont.load_default()
d = ImageDraw.Draw(S)
for k, (c, im) in enumerate(ims):
    x, y = (k % cols) * w, (k // cols) * h
    S.paste(im, (x, y))
    if c:
        tw = d.textlength(c, font=font)
        d.rectangle([x + 6, y + 6, x + 14 + tw, y + 28], fill='#26231f')
        d.text((x + 10, y + 8), c, fill='#f4efe8', font=font)
S.save(out)
print(out, S.size)
