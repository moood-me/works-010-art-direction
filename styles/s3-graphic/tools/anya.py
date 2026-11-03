"""Аня, about 20: warm, trusting, dreamy. Shape: a soft drop / S-curve; long copper hair."""
from lib import F, L, clip, shaded, g, LW
from face import eye, brow, closed_eye

C = dict(skin='#f4cdb0', shade='#e3a98c', line='#a8604a', blush='#f2967f', white='#fffaf3',
         iris='#6b7a3c', pupil='#2b2416', lash='#3b1d16',
         hair='#a8492e', hairS='#7e3220', hairH='#cf6d42', hairL='#4e1d14',
         lip='#d77467',
         knit='#6d8fb3', knitS='#557599', knitL='#36506e',
         dress='#e8b04a', dressS='#c98f31', dressL='#8a5a1c',
         sock='#f6eee2', shoe='#6b3a2a', shoeL='#3c1e15')

# ---------------------------------------------------------------- head, three-quarter (facing right)
# eye line y=0, chin about y=112, crown y=-122


def hair_back_q():
    d = ('M -20 -128 C -90 -126, -125 -70, -118 0 C -114 60, -132 120, -126 180 '
         'C -122 220, -100 250, -70 262 C -84 240, -86 222, -80 205 C -66 236, -40 252, -12 258 '
         'C -28 236, -30 214, -24 196 L 60 160 C 100 120, 112 60, 104 0 C 98 -80, 60 -128, -20 -128 Z')
    shade = 'M -60 60 C -70 120, -60 200, -20 258 L -140 270 L -140 40 Z'
    return shaded(d, C['hair'], shade, C['hairS'], C['hairL'])


def face_q(expr):
    face = ('M -92 -40 C -96 20, -84 62, -50 88 C -22 108, 18 118, 40 112 C 58 104, 70 84, 78 62 '
            'C 85 44, 90 24, 89 6 C 88 -4, 93 -16, 93 -30 C 95 -72, 60 -120, 0 -122 C -60 -122, -92 -92, -92 -40 Z')
    neck = 'M -44 70 C -44 110, -46 140, -52 175 L 34 175 C 28 140, 28 115, 32 96 Z'
    neck_sh = 'M -60 60 C -20 105, 20 118, 50 100 L 50 128 C 10 140, -30 128, -60 112 Z'
    face_sh = 'M -100 -60 C -80 -30, -84 40, -40 96 L -110 120 Z'
    out = [shaded(neck, C['skin'], neck_sh, C['shade'], C['line'])]
    out.append(F(face, C['skin']))
    out.append(clip(face, F(face_sh, C['shade'], extra='opacity=".55"'),
                    f'<ellipse cx="-30" cy="45" rx="24" ry="13" fill="{C["blush"]}" opacity=".45"/>',
                    f'<ellipse cx="70" cy="44" rx="13" ry="10" fill="{C["blush"]}" opacity=".45"/>'))
    out.append(L(face, C['line']))
    # ear (near side)
    ear = 'M -84 -2 C -100 -14, -112 4, -104 22 C -98 36, -88 40, -80 34'
    out.append(F(ear + ' Z', C['skin'], C['line']))
    out.append(L('M -92 6 C -98 12, -96 22, -90 26', C['line'], LW[0] * .8))
    # eyes
    e = dict(C)
    look = {'dream': (5, -6), 'joy': (4, 0), 'surprise': (2, 0), 'sad': (2, 4), 'anger': (4, 2)}.get(expr, (5, -3))
    lid = {'dream': .32, 'joy': .1, 'surprise': 0, 'sad': .38, 'anger': .34}.get(expr, .22)
    lt = {'sad': -5, 'anger': 6}.get(expr, 0)
    if expr == 'joy':
        out.append(closed_eye(-16, 6, 21, e, up=True, w=2.2))
        out.append(closed_eye(56, 6, 15, e, up=True, w=2.0))
    else:
        rs = 1.12 if expr == 'surprise' else 1.0
        ir = 15 if expr != 'surprise' else 12
        out.append(eye(-16, 0, 21 * rs, 24 * rs, e, look=look, lid=lid, lidtilt=lt, ir=ir, flick=-1))
        out.append(eye(56, 0, 15 * rs, 23 * rs, e, look=(look[0] * .8, look[1]), lid=lid, lidtilt=lt, ir=ir * .95,
                       sq=.78, flick=1))
    # brows
    b = {'dream': (-36, -40, 4, -46, -34, 6), 'joy': (-38, -44, 2, -50, -40, 8), 'surprise': (-38, -54, 2, -60, -52, 10),
         'sad': (-36, -36, 2, -48, -32, 2), 'anger': (-38, -44, 0, -30, -50, -2)}.get(expr, (-36, -40, 2, -44, -36, 6))
    x0, y0a, x1, y1a, y0b, bend = b
    if expr == 'sad':
        out.append(brow(x1, y1a, x0, y0a + 4, bend, 6, C['hairL']))
        out.append(brow(40, y1a + 2, 70, y0b + 8, bend * .6, 5, C['hairL']))
    elif expr == 'anger':
        out.append(brow(x1, y1a + 14, x0, y0a - 4, -2, 7, C['hairL']))
        out.append(brow(40, -26, 72, -40, -2, 6, C['hairL']))
    else:
        out.append(brow(x1, y1a + 2, x0, y0a, bend, 6, C['hairL']))
        out.append(brow(42, y1a + 4, 72, y0b, bend * .7, 5, C['hairL']))
    # nose: a small wedge, the shadow side only
    out.append(F('M 70 18 C 76 30, 86 38, 84 46 C 82 52, 74 53, 66 50 C 72 47, 76 42, 70 18 Z', C['shade']))
    out.append(L('M 72 22 C 80 32, 88 40, 84 47 C 80 52, 72 52, 66 50', C['line'], LW[0] * .9))
    # mouth
    m = {
        'dream': L('M 32 72 C 42 78, 56 78, 66 70', C['line'], LW[0] * 1.1) +
                 L('M 44 84 C 50 86, 56 85, 60 82', C['lip'], LW[0] * 1.0),
        'joy': F('M 22 66 C 36 70, 58 70, 72 62 C 70 86, 56 98, 44 98 C 32 98, 24 84, 22 66 Z', '#7a2a24', C['line']) +
               clip('M 22 66 C 36 70, 58 70, 72 62 C 70 86, 56 98, 44 98 C 32 98, 24 84, 22 66 Z',
                    F('M 18 60 L 76 56 L 74 74 C 56 80, 36 80, 18 74 Z', '#fff'),
                    '<ellipse cx="46" cy="98" rx="16" ry="9" fill="#e07a70"/>'),
        'surprise': F('M 40 76 C 48 72, 56 74, 58 84 C 58 96, 48 100, 42 96 C 36 92, 36 80, 40 76 Z', '#7a2a24', C['line']),
        'sad': L('M 30 82 C 40 74, 56 74, 64 80', C['line'], LW[0] * 1.1) +
               L('M 42 90 C 48 92, 54 92, 58 90', C['lip'], LW[0]),
        'anger': F('M 28 78 C 40 74, 56 74, 66 76 C 62 86, 36 88, 28 78 Z', '#7a2a24', C['line']) +
                 clip('M 28 78 C 40 74, 56 74, 66 76 C 62 86, 36 88, 28 78 Z', F('M 20 70 L 70 70 L 70 80 L 20 80 Z', '#fff')),
    }
    out.append(m.get(expr, m['dream']))
    return ''.join(out)


def hair_front_q():
    # fringe swept from a part on the left over the forehead, with pointed locks
    d = ('M -96 -30 C -106 -90, -60 -134, 0 -132 C 60 -130, 100 -96, 104 -40 C 106 -10, 100 20, 98 46 '
         'C 92 20, 88 0, 86 -16 C 80 -24, 76 -36, 74 -50 C 62 -40, 48 -34, 30 -34 C 40 -40, 46 -50, 48 -60 '
         'C 30 -46, 6 -40, -20 -42 C -2 -50, 8 -62, 12 -76 C -16 -60, -50 -54, -74 -40 C -82 -26, -86 -10, -88 6 '
         'C -94 -4, -96 -16, -96 -30 Z')
    shade = 'M -110 -10 C -90 -60, -40 -90, 20 -96 C 60 -98, 100 -70, 110 -50 L 110 60 L 80 -20 L -110 40 Z'
    hi = ('M -60 -112 C -30 -124, 20 -126, 50 -114 C 30 -112, 10 -108, -6 -100 C -20 -106, -40 -108, -60 -112 Z')
    return (F(d, C['hair']) + clip(d, F(shade, C['hairS'], extra='opacity=".0"'), F(hi, C['hairH'])) +
            L(d, C['hairL']) +
            L('M -40 -96 C -30 -80, -24 -66, -26 -50', C['hairL'], LW[0] * .7) +
            L('M 30 -100 C 46 -86, 56 -72, 60 -50', C['hairL'], LW[0] * .7))


def lock_front_q():
    # a long lock falling in front of the near shoulder
    d = ('M -96 -10 C -104 40, -96 90, -86 130 C -78 170, -84 210, -96 240 C -70 226, -58 196, -60 160 '
         'C -50 190, -40 214, -24 226 C -36 196, -40 160, -52 120 C -64 80, -70 30, -74 -20 Z')
    sh = 'M -80 0 C -76 60, -60 120, -40 230 L 0 230 L 0 0 Z'
    return shaded(d, C['hair'], sh, C['hairS'], C['hairL']) + \
        L('M -84 40 C -80 90, -72 130, -66 170', C['hairL'], LW[0] * .7)


def head_q(expr='dream'):
    return hair_back_q() + face_q(expr) + hair_front_q() + lock_front_q()


# ---------------------------------------------------------------- body pieces for the portrait (3/4)
def bust_q():
    # shoulders in a soft knitted cardigan over a mustard dress; drawn under the head (neck base at y≈170)
    dress = 'M -60 160 C -30 180, 20 182, 46 166 L 70 330 L -90 330 Z'
    cardi = ('M -70 150 C -120 160, -170 190, -184 250 C -192 290, -194 320, -196 330 L -40 330 '
             'C -46 280, -46 220, -30 178 Z')
    cardi2 = ('M 40 160 C 90 168, 130 190, 146 236 C 156 270, 160 310, 162 330 L 50 330 '
              'C 54 280, 54 220, 30 178 Z')
    collar = 'M -60 160 C -30 186, 14 188, 44 166 C 40 180, 20 196, -10 198 C -40 198, -56 184, -60 160 Z'
    out = [shaded(dress, C['dress'], 'M -100 170 L -20 180 L -40 330 L -100 330 Z', C['dressS'], C['dressL'])]
    out.append(F(collar, C['sock'], C['dressL']))
    out.append(shaded(cardi, C['knit'], 'M -200 200 C -150 240, -110 270, -80 330 L -200 330 Z', C['knitS'], C['knitL']))
    out.append(shaded(cardi2, C['knit'], 'M 30 170 C 60 220, 64 280, 60 330 L 40 330 Z', C['knitS'], C['knitL']))
    for x in (-150, -120, -90):
        pass
    out.append(L('M -44 200 C -46 240, -44 290, -42 330', C['knitL'], LW[0] * .8))
    out.append(L('M 40 200 C 50 240, 52 290, 54 330', C['knitL'], LW[0] * .8))
    for y in (232, 280):
        out.append(f'<circle cx="-38" cy="{y}" r="6" fill="{C["dress"]}" stroke="{C["knitL"]}" stroke-width="2"/>')
    return ''.join(out)
