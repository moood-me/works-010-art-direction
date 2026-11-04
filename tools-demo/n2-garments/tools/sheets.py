"""Sheets for the page from the renders (tools/render_all.sh) and GarmentCode's pattern pictures."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
GC = Path('/home/user/cache/n2-garments'); R = GC / 'renders'
OUT = Path(__file__).resolve().parent.parent / 'pics'
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
BG = (214, 206, 194)
def fig(name, yaw=20, body='moood-woman', box=(70, 170, 530, 740)):
    return Image.open(R / f'{body}-{name}-{yaw}.png').convert('RGB').crop(box)
def sheet(out, cells, cols, cap_h=34):
    """cells: [(image, caption)]"""
    w = max(c[0].width for c in cells); h = max(c[0].height for c in cells)
    rows = (len(cells) + cols - 1) // cols
    S = Image.new('RGB', (w * cols, (h + cap_h) * rows), BG); d = ImageDraw.Draw(S)
    for k, (im, cap) in enumerate(cells):
        x, y = (k % cols) * w, (k // cols) * (h + cap_h)
        S.paste(im, (x + (w - im.width) // 2, y + cap_h))
        d.text((x + 8, y + 6), cap, font=F, fill=(40, 36, 32))
    S.save(OUT / out, quality=88); print(out, S.size)
def pattern(name, body='moood-woman', size=(520, 380)):
    im = Image.open(GC / 'runs' / body / name / f'{name}_pattern.png').convert('RGBA')
    s = min((size[0] - 30) / im.width, (size[1] - 30) / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    c = Image.new('RGB', size, (250, 248, 244)); c.paste(im, ((size[0] - im.width) // 2, (size[1] - im.height) // 2), im)
    return c
what = sys.argv[1:] or ['all']
def want(k): return 'all' in what or k in what
if want('dresses'):
    sheet('dresses.webp', [(fig('dress-bell'), 'колокол (круговая юбка)'), (fig('dress-aline-puff'), 'А-силуэт, рукав-фонарик'),
                           (fig('dress-trapeze'), 'прямое свободное'), (fig('dress-bell', 160), 'колокол сзади'),
                           (fig('dress-aline-puff', 160), 'А-силуэт сзади'), (fig('dress-trapeze', 160), 'прямое сзади')], 3)
if want('everyday'):
    sheet('everyday.webp', [(fig('outfit-shirt-skirt'), 'рубашка и юбка'), (fig('outfit-shirt-pants'), 'рубашка и брюки'),
                            (fig('outfit-shirt-skirt', 160), 'сзади'), (fig('outfit-shirt-pants', 160), 'сзади')], 4)
if want('variants'):
    sheet('variants.webp', [(fig('dress-bell'), 'исходное: suns = 1, длина 0.6'), (fig('var-suns03'), 'suns = 0.3'),
                            (fig('var-suns15-short'), 'suns = 1.5, длина 0.35'), (fig('var-vneck-short'), 'V-вырез, длина 0.4')], 4)
if want('patterns'):
    sheet('patterns.webp', [(pattern('dress-bell'), 'платье-колокол'), (pattern('dress-aline-puff'), 'А-силуэт с фонариком'),
                            (pattern('outfit-shirt-pants'), 'рубашка с брюками'), (pattern('dress-trapeze'), 'прямое свободное')], 2)
if want('fit'):
    sheet('fit.webp', [(fig('dress-bell'), 'Anny (наше тело): рост 158, талия 67'),
                       (fig('dress-bell', 20, 'mean_female'), 'тело GarmentCode: рост 166, талия 80')], 2)
if want('samples'):
    import glob
    sheet('samples-patterns.webp', [(pattern(f'rand{k:02d}', 'samples', (420, 300)), f'{k + 1}') for k in range(12)], 4)
    sheet('samples-draped.webp', [(fig(f'rand{k}'), f'случайный {int(k) + 1}') for k in ('01', '09', '10')], 3)
