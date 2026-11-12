"""The page's pictures from the renders (shots.mjs with jobs/jstill.json and jobs/jfilm.json).
  python3 make_pics.py stills STILLDIR      → ../pics: compare (turn, portrait, figure), views, steps, expressions, close, cover
  python3 make_pics.py films FILMDIR        → ../pics: turn.mp4, walk.mp4, wave.mp4, idle.mp4, face.mp4"""
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
PICS = os.path.join(HERE, '..', 'pics'); S17 = os.path.join(HERE, '../../../styles/s17-bilibin/pics')
sys.path.insert(0, HERE)
import compare  # noqa: E402


def font(sz):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def row(d, names, out, labels=None, q=86):
    ims = [Image.open(os.path.join(d, n + '.png')).convert('RGB') for n in names]
    W = Image.new('RGB', (sum(i.width for i in ims), ims[0].height)); x = 0
    for k, i in enumerate(ims):
        W.paste(i, (x, 0))
        if labels: ImageDraw.Draw(W).text((x + 14, 10), labels[k], fill='#1d1712', font=font(22))
        x += i.width
    W.save(os.path.join(PICS, out), quality=q)


if sys.argv[1] == 'stills':
    d = sys.argv[2]
    r = compare.turn(d)
    compare.pair(Image.open(os.path.join(S17, 'turn-vera.jpg')), r, os.path.join(PICS, 'turn'))
    compare.pair(Image.open(os.path.join(S17, 'portrait-vera.jpg')), Image.open(os.path.join(d, 'por.png')), os.path.join(PICS, 'portrait'))
    compare.pair(Image.open(os.path.join(S17, 'figure-vera.jpg')), Image.open(os.path.join(d, 'fig.png')), os.path.join(PICS, 'figure'))
    row(d, ['v0', 'v1', 'v2', 'v3', 'v4'], 'views.webp')
    row(d, ['s1', 's2', 's3', 's4', 's5', 's6'], 'steps.webp', ['1', '2', '3', '4', '5', '6'])
    row(d, ['ex-calm', 'ex-joy', 'ex-surprise', 'ex-sad', 'ex-anger'], 'expressions.webp')
    Image.open(os.path.join(d, 'close.png')).convert('RGB').save(os.path.join(PICS, 'close.webp'), quality=88)
    Image.open(os.path.join(d, 'close.png')).convert('RGB').resize((640, 640), Image.LANCZOS).save(os.path.join(PICS, 'cover.webp'), quality=86)
else:
    d = sys.argv[2]
    for name, fps in (('turn', 25), ('walk', 30), ('wave', 30), ('idle', 30), ('face', 25)):
        if not os.path.isdir(os.path.join(d, name)): continue
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(d, name, 'f%04d.png'), '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p', '-crf', '25', '-movflags', '+faststart', os.path.join(PICS, name + '.mp4')], check=True)
