# Tiles pictures into a labelled sheet: sheet.py spec.json — spec: {out, title, cols, items: [[label, path], …]}
import sys, json
from PIL import Image, ImageDraw, ImageFont
S = json.load(open(sys.argv[1]))
ims = [Image.open(p).convert('RGB') for _, p in S['items']]
w = max(i.width for i in ims); h = max(i.height for i in ims); cols = S.get('cols', 6); rows = (len(ims) + cols - 1) // cols
font = lambda n: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)
top = 46 if S.get('title') else 0
sheet = Image.new('RGB', (w * cols, top + (h + 30) * rows), '#f4f1ec'); d = ImageDraw.Draw(sheet)
if S.get('title'): d.text((14, 12), S['title'], fill='#26231f', font=font(21))
for k, (im, (label, _)) in enumerate(zip(ims, S['items'])):
    x, y = (k % cols) * w, top + (k // cols) * (h + 30)
    sheet.paste(im, (x + (w - im.width) // 2, y)); d.text((x + 8, y + h + 6), label, fill='#26231f', font=font(15))
sheet.save(S['out'])
