"""Lay the renders out as the page's pictures (webp), with short Russian labels.
python3 compose.py  (reads /home/user/cache/n5-heads/r, writes ../pics)"""
import os
from PIL import Image, ImageDraw, ImageFont
R = '/home/user/cache/n5-heads/r'; P = os.path.join(os.path.dirname(__file__), '..', 'pics')
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
BG = (235, 234, 230)

def sheet(name, rows, cw=420, ch=None):
    """rows: list of rows; each row a list of (path, label) or None."""
    ims = [[(Image.open(os.path.join(R, p)).convert('RGB'), l) if p else None for p, l in row] for row in rows]
    W = max(len(r) for r in rows) * cw
    def cell_h(row):
        im = next(i for i, _ in (x for x in row if x))
        return ch or int(cw * im.height / im.width)
    H = sum(cell_h(r) for r in ims)
    G = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(G); y = 0
    for row in ims:
        h = cell_h(row)
        for i, c in enumerate(row):
            if not c: continue
            im, lab = c; s = min(cw / im.width, h / im.height); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
            x = i * cw + (cw - im.width) // 2; G.paste(im, (x, y + (h - im.height) // 2))
            if lab:
                tw = d.textlength(lab, font=F); d.rectangle([i * cw + 6, y + 6, i * cw + 18 + tw, y + 36], fill=(255, 255, 255)); d.text((i * cw + 12, y + 9), lab, fill=(25, 25, 25), font=F)
        y += h
    G.save(os.path.join(P, name), quality=86, method=6); print(name, G.size)

E = lambda ch, v, e='neutral': f'e{ch}-{v}-{e}.png'
C = lambda ch, v, e='neutral': f'clay/c{ch}-{v}-{e}.png'
Wr = lambda ch, v, e='neutral': f'clay/w{ch}-{v}-{e}.png'
H = lambda n: f'hbm/hbm-{n}.png'
# heads at three angles
sheet('heads-angles.webp', [[(E('rain', 'front'), 'Rain: спереди'), (E('rain', 'tq'), '3/4'), (E('rain', 'side'), 'профиль')],
                            [(E('snow', 'front'), 'Snow: спереди'), (E('snow', 'tq'), '3/4'), (E('snow', 'side'), 'профиль')],
                            [(H('sthead-front'), 'Base Meshes, стилиз.: спереди'), (H('sthead-tq'), '3/4'), (H('sthead-side'), 'профиль')]], cw=400)
# clay: the form alone
sheet('clay-forms.webp', [[(C('rain', 'front'), 'Rain, глина'), (C('rain', 'side'), 'профиль'), (C('snow', 'front'), 'Snow, глина'), (C('snow', 'side'), 'профиль')]], cw=400)
# expressions
for ch, nm in [('rain', 'Rain'), ('snow', 'Snow')]:
    sheet(f'expr-{ch}.webp', [[(E(ch, 'front'), f'{nm}: покой'), (E(ch, 'front', 'smile'), 'улыбка'), (E(ch, 'front', 'surprise'), 'удивление'),
                               (E(ch, 'front', 'blink'), 'моргание'), (E(ch, 'front', 'anger'), 'злость')]], cw=360)
sheet('expr-clay-close.webp', [[(C(ch, 'mouth', e), f'{ch.capitalize()}: {l}') for e, l in [('neutral', 'покой'), ('smile', 'улыбка'), ('surprise', 'удивление'), ('anger', 'злость')]] for ch in ('rain', 'snow')] +
                              [[(C(ch, 'eyeL', e), f'{ch.capitalize()}: {l}') for e, l in [('neutral', 'покой'), ('smile', 'улыбка'), ('surprise', 'удивление'), ('blink', 'моргание')]] for ch in ('rain', 'snow')], cw=330)
# eye and mouth close-ups
sheet('eye-close.webp', [[(E('rain', 'eyeL'), 'Rain: глаз'), (C('rain', 'eyeL'), 'глина'), (Wr('rain', 'eyeL'), 'сетка'), (Wr('rain', 'eyeL', 'blink'), 'сетка, веко закрыто')],
                         [(E('snow', 'eyeL'), 'Snow: глаз'), (C('snow', 'eyeL'), 'глина'), (Wr('snow', 'eyeL'), 'сетка'), (Wr('snow', 'eyeL', 'smile'), 'сетка, улыбка')],
                         [(H('sthead-eye-wire'), 'Base Meshes: глаз, сетка'), None, None, None]], cw=380)
sheet('mouth-close.webp', [[(E('rain', 'mouth'), 'Rain: рот'), (C('rain', 'mouth'), 'глина'), (Wr('rain', 'mouth'), 'сетка'), (Wr('rain', 'mouth', 'smile'), 'сетка, улыбка')],
                           [(E('snow', 'mouth'), 'Snow: рот'), (C('snow', 'mouth'), 'глина'), (Wr('snow', 'mouth'), 'сетка'), (Wr('snow', 'mouth', 'smile'), 'сетка, улыбка')],
                           [(H('sthead-mouth-wire'), 'Base Meshes: рот, сетка'), None, None, None]], cw=380)
# topology of whole heads
sheet('topology.webp', [[(Wr('rain', 'front'), 'Rain'), (Wr('rain', 'side'), 'Rain, профиль'), (Wr('snow', 'front'), 'Snow'), (Wr('snow', 'side'), 'Snow, профиль')],
                        [(H('sthead-wire'), 'Base Meshes, стилиз.'), (H('anim-wire'), 'Base Meshes, реалист. для анимации'), (H('anim-front'), 'она же, гладкая'), None]], cw=400)
# bodies
sheet('bodies.webp', [[(E('rain', 'bodyfront'), 'Rain'), (E('rain', 'body'), ''), (E('rain', 'bodyside'), ''), (E('snow', 'bodyfront'), 'Snow'), (E('snow', 'body'), ''), (E('snow', 'bodyside'), '')]], cw=300)
sheet('bodies-hbm.webp', [[(H('body-f-front'), 'Base Meshes: женщина'), (H('body-f-tq'), ''), (H('body-f-side'), ''), (H('body-m-front'), 'мужчина'), (H('body-m-tq'), ''), (H('body-m-side'), '')]], cw=300)
# what the base-mesh bundle is
pp = lambda n: f'parts/part-{n}.png'
sheet('hbm-parts.webp', [[(pp('Head_-_Planar'), 'голова для лепки'), (pp('Head_-_Generic_Topology'), 'простая сетка головы'), (pp('Head_-_Primitives'), 'голова из простых объёмов')],
                         [(pp('Body_Female_-_Primitive_Stylized'), 'тело из простых частей'), (pp('Hand_-_Stylized'), 'кисть'), (pp('Foot_-_Stylized'), 'стопа')],
                         [(pp('Eye_-_Stylized'), 'глаз'), (pp('Jaw_-_Stylized'), 'зубы и дёсны'), (pp('Skull_-_Realistic'), 'череп')]], cw=360)
