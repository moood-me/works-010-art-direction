"""Frames → a short mp4 in the drawing's panel manner (a floor band and an even frame), and a contact sheet.
usage: python3 film.py FRAMES_GLOB OUT.mp4 FPS FLOOR_Y [SHEET.png] [every]"""
import sys, glob, os, subprocess, tempfile
from PIL import Image, ImageDraw

pat, out, fps, fy = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
sheet = sys.argv[5] if len(sys.argv) > 5 else None
every = int(sys.argv[6]) if len(sys.argv) > 6 else 6
files = sorted(glob.glob(pat))
import os as _os
INK, BAND = '#1b1714', _os.environ.get('BAND', '#cbbd9d')
tmp = tempfile.mkdtemp()
ims = []
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB')
    W, H = im.size
    bg = im.getpixel((2, 2))
    # the floor band under the figure: drawn where the picture is still background
    d = ImageDraw.Draw(im)
    if fy >= H:                    # no floor in this picture (a close view): only the frame
        d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=3)
        im.save(os.path.join(tmp, f'{i:04d}.png'))
        if sheet and i % every == 0:
            ims.append(im.resize((W // 2, H // 2)))
        continue
    band = Image.new('RGB', (W, H - fy), BAND)
    lower = im.crop((0, fy, W, H))
    mask = Image.eval(lower.convert('L'), lambda v: 0)
    px, mp = lower.load(), mask.load()
    for y in range(H - fy):
        for x in range(W):
            if px[x, y] != bg:
                mp[x, y] = 255
    band.paste(lower, (0, 0), mask)
    im.paste(band, (0, fy))
    d = ImageDraw.Draw(im)
    d.line([(0, fy), (W, fy)], fill=INK, width=2)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=3)
    im.save(os.path.join(tmp, f'{i:04d}.png'))
    if sheet and i % every == 0:
        ims.append(im.resize((W // 2, H // 2)))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(tmp, '%04d.png'),
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '26', '-movflags', '+faststart', out], check=True)
if sheet:
    w, h = ims[0].size
    s = Image.new('RGB', (w * len(ims), h), 'white')
    for i, im in enumerate(ims):
        s.paste(im, (i * w, 0))
    s.save(sheet)
print(out, len(files))
