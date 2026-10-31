# python3 py/crop.py ref.png x0 y0 x1 y1 out.png [scale] — a crop with a grid every 10 source pixels, labelled
import sys
from PIL import Image, ImageDraw
f, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]; s = int(sys.argv[7]) if len(sys.argv) > 7 else 6
im = Image.open('/home/user/works-010-art-direction/docs/pictures/references/' + f).convert('RGB').crop((x0, y0, x1, y1))
im = im.resize((im.width * s, im.height * s), Image.LANCZOS); d = ImageDraw.Draw(im)
for x in range((x0 // 10 + 1) * 10, x1, 10):
    X = (x - x0) * s; d.line([(X, 0), (X, im.height)], fill=(0, 255, 255) if x % 50 else (255, 0, 255), width=1); d.text((X + 2, 2), str(x), fill=(0, 0, 0))
for y in range((y0 // 10 + 1) * 10, y1, 10):
    Y = (y - y0) * s; d.line([(0, Y), (im.width, Y)], fill=(0, 255, 255) if y % 50 else (255, 0, 255), width=1); d.text((2, Y + 2), str(y), fill=(0, 0, 0))
im.save(out)
