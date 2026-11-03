"""Вера, about 40: strict, clever, tired. Shape: a tall narrow rectangle / needle; straight lines, sharp corners."""
from lib import F, L, clip, shaded, g, LW
from face import eye, brow, closed_eye, shout

C = dict(skin='#e9bf9f', shade='#cf9a7f', line='#8a5644', blush='#de8c78', white='#fbf7f0',
         iris='#4c5a4e', pupil='#1a1d1a', lash='#211b20',
         hair='#2d2830', hairS='#1f1b22', hairH='#4a4350', hairL='#110e12', grey='#a9a4ad',
         lip='#b4524a',
         coat='#2f5f63', coatS='#244a4e', coatL='#122a2c',
         blouse='#f4f1ea', blouseS='#d9d4c8', blouseL='#8c867a',
         trou='#3b3a40', trouS='#2c2b30', trouL='#121115', shoe='#5a2a2a', shoeL='#26100f',
         folder='#c9a24f', folderL='#6b5020', frame='#3a2a2a')

FACE_Q = ('M -84 -40 C -86 10, -76 60, -50 96 C -26 124, 4 136, 28 134 C 44 132, 54 122, 60 108 '
          'C 68 88, 78 62, 82 36 C 85 20, 84 8, 84 -2 C 84 -12, 88 -22, 88 -34 C 90 -80, 54 -122, 0 -124 '
          'C -50 -124, -82 -90, -84 -40 Z')
HAIR_Q = ('M -92 -10 C -100 -70, -60 -134, 4 -134 C 60 -134, 96 -96, 94 -48 C 92 -40, 90 -34, 88 -30 '
          'C 80 -56, 62 -78, 40 -84 C 14 -92, -20 -90, -44 -80 C -62 -70, -74 -50, -78 -24 C -82 -14, -86 -8, -92 -10 Z')


def head_q(expr='strict', tilt=-3):
    out = []
    # bun at the back
    bun = 'M -96 -110 C -132 -112, -150 -76, -138 -46 C -126 -18, -94 -14, -78 -32 C -64 -52, -66 -100, -96 -110 Z'
    out.append(shaded(bun, C['hair'], 'M -160 -60 C -130 -30, -100 -24, -70 -40 L -70 0 L -160 0 Z', C['hairS'], C['hairL']))
    out.append(L('M -120 -96 C -106 -84, -100 -64, -104 -40', C['hairH'], LW[0] * .8))
    out.append(L('M -134 -70 C -122 -60, -114 -44, -112 -30', C['hairH'], LW[0] * .8))
    # neck, long
    out.append(shaded('M -32 96 C -28 140, -30 170, -34 206 L 24 206 C 20 176, 18 150, 22 124 Z', C['skin'],
                      'M -50 80 C -20 130, 10 140, 40 128 L 40 160 C 0 170, -30 150, -50 130 Z', C['shade'], C['line']))
    out.append(F(FACE_Q, C['skin']))
    out.append(clip(FACE_Q,
                    F('M -100 -60 C -80 -20, -80 60, -30 130 L -110 140 Z', C['shade'], extra='opacity=".6"'),
                    F('M 10 70 C 30 100, 50 110, 70 100 L 70 140 L 0 140 Z', C['shade'], extra='opacity=".35"'),
                    g(F(HAIR_Q, C['shade']), 4, 8),
                    f'<ellipse cx="-34" cy="46" rx="22" ry="12" fill="{C["blush"]}" opacity=".3"/>'))
    out.append(L(FACE_Q, C['line']))
    # cheekbone accent
    out.append(L('M -56 40 C -46 52, -36 58, -24 60', C['line'], LW[0] * .6, 'opacity=".5"'))
    # ear (small, hair pulled behind it)
    ear = 'M -78 -6 C -98 -16, -106 6, -100 24 C -96 36, -86 40, -76 34'
    out.append(F(ear + ' Z', C['skin'], C['line']))
    out.append(L('M -88 4 C -94 10, -92 20, -86 24', C['line'], LW[0] * .7))
    out.append('<circle cx="-92" cy="36" r="4" fill="#d8c27a" stroke="#7a6526" stroke-width="1.4"/>')
    # eyes: almond, tired lids, a line under each
    look = {'strict': (4, 0), 'joy': (3, 0), 'surprise': (2, -1), 'sad': (1, 4), 'anger': (4, 0), 'tired': (2, 3)}.get(expr, (4, 0))
    lid = {'strict': .36, 'surprise': .02, 'sad': .42, 'anger': .34, 'tired': .5}.get(expr, .3)
    lt = {'strict': 3, 'anger': 7, 'sad': -6, 'tired': -2}.get(expr, 0)
    if expr == 'joy':
        out.append(closed_eye(-18, 4, 20, C, up=True, w=2.0))
        out.append(closed_eye(52, 4, 14, C, up=True, w=1.8))
    else:
        rs = 1.18 if expr == 'surprise' else 1
        out.append(eye(-18, 0, 21 * rs, 18 * rs, C, look=look, lid=lid, lidtilt=-lt, ir=12, flick=-1, lash=1.9, tilt=2, lowline=False))
        out.append(eye(52, 0, 14 * rs, 17 * rs, C, look=look, lid=lid, lidtilt=lt, ir=11, sq=.8, flick=1, lash=1.8, tilt=-2,
                       lowline=False))
    # tired lines under the eyes
    out.append(L('M -36 22 C -26 28, -12 28, -2 22', C['line'], LW[0] * .7, 'opacity=".6"'))
    out.append(L('M 42 22 C 50 26, 58 26, 64 22', C['line'], LW[0] * .6, 'opacity=".5"'))
    # brows: straight, dark, firm
    bb = {'strict': ((-44, -28, 0, -24, 0), (38, -24, 76, -30, 0)),
          'joy': ((-44, -32, 0, -34, 4), (38, -34, 76, -32, 4)),
          'surprise': ((-44, -42, 0, -46, 6), (38, -46, 76, -42, 6)),
          'sad': ((-44, -24, 0, -34, -2), (38, -34, 74, -22, -2)),
          'anger': ((-44, -34, 0, -18, 0), (38, -18, 76, -34, 0)),
          'tired': ((-44, -26, 0, -30, 0), (38, -30, 76, -26, 0))}.get(expr)
    (a0, a1, a2, a3, ab), (b0, b1, b2, b3, bb_) = bb
    out.append(brow(a2, a3, a0, a1, ab, 6, C['hairL']))
    out.append(brow(b0, b1, b2, b3, bb_, 5.5, C['hairL']))
    # nose: long and straight
    nose = 'M 66 -8 L 96 48 C 98 54, 92 58, 84 58 C 80 58, 76 56, 72 58 C 70 40, 70 20, 66 -8 Z'
    out.append(F(nose, C['skin']))
    out.append(clip(nose, F('M 50 0 L 80 60 L 50 60 Z', C['shade'])))
    out.append(L('M 67 -6 L 96 48 C 98 54, 92 58, 84 58 C 80 58, 77 57, 73 58', C['line'], LW[0] * .9))
    # mouth: small, firm
    m = {
        'strict': F('M 22 86 C 32 82, 46 82, 58 84 C 50 86, 34 88, 22 86 Z', C['lip'], C['lip'], LW[0] * .8) +
                  L('M 20 88 C 32 86, 48 86, 60 86', C['line'], LW[0] * 1.0) +
                  F('M 28 92 C 36 98, 48 98, 54 92 C 46 94, 36 94, 28 92 Z', C['lip'], C['lip'], LW[0] * .7),
        'joy': F('M 16 80 C 32 86, 52 86, 66 76 C 62 96, 50 104, 40 104 C 28 104, 18 94, 16 80 Z', '#6e2620', C['line']) +
               clip('M 16 80 C 32 86, 52 86, 66 76 C 62 96, 50 104, 40 104 C 28 104, 18 94, 16 80 Z',
                    F('M 10 74 L 70 70 L 70 88 C 50 92, 30 92, 10 88 Z', '#fff')),
        'surprise': F('M 32 84 C 40 80, 50 82, 52 92 C 52 104, 44 108, 38 106 C 32 102, 30 92, 32 84 Z', '#6e2620', C['line']),
        'sad': L('M 22 92 C 32 84, 48 84, 58 92', C['line'], LW[0] * 1.1) +
               F('M 30 98 C 38 102, 46 102, 52 98 C 46 100, 38 100, 30 98 Z', C['lip'], C['lip'], LW[0] * .6),
        'anger': shout(18, 62, 80, 22, C['line']),
    }
    out.append(m.get(expr, m['strict']))
    # hair: pulled back flat, a grey streak, combed lines
    out.append(F(HAIR_Q, C['hair']))
    out.append(clip(HAIR_Q, F('M -20 -130 C 10 -126, 40 -110, 60 -84 L 48 -80 C 30 -100, 6 -114, -24 -120 Z', C['grey']),
                    F('M -70 -110 C -50 -126, -20 -132, 0 -132 C -24 -124, -46 -112, -60 -98 Z', C['hairH'])))
    out.append(L(HAIR_Q, C['hairL']))
    for d in ('M 40 -84 C 10 -96, -30 -100, -70 -90', 'M 60 -70 C 20 -86, -30 -84, -80 -64'):
        out.append(L(d, C['hairH'], LW[0] * .7))
    # glasses: thin rectangular frames
    out.append(F('M -46 -20 L 8 -20 L 6 18 L -44 18 Z', 'none', C['frame'], LW[0] * 1.0))
    out.append(F('M 30 -20 L 72 -22 L 70 16 L 32 18 Z', 'none', C['frame'], LW[0] * 1.0))
    out.append(L('M 8 -12 C 16 -16, 24 -16, 30 -12', C['frame'], LW[0] * 1.0))
    out.append(L('M -46 -16 L -76 -10', C['frame'], LW[0] * 1.0))
    out.append(F('M -40 -16 L -30 -16 L -42 10 Z', '#fff', extra='opacity=".35"'))
    return f'<g transform="rotate({tilt} 0 100)">' + ''.join(out) + '</g>'


# ---------------------------------------------------------------- body, three-quarter: long coat, a folder held to the chest
COAT = ('M -118 236 C -134 300, -136 500, -128 700 L -156 1110 L 130 1110 L 106 700 '
        'C 106 500, 110 300, 98 236 C 40 214, -66 214, -118 236 Z')


def body_q():
    out = []
    # trousers and shoes
    for d, x, y in (('M 20 980 L 76 980 L 70 1420 L 32 1420 Z', 51, 1420), ('M -100 980 L -36 980 L -44 1436 L -86 1436 Z', -65, 1436)):
        out.append(shaded(d, C['trou'], f'M {x + 6} 980 L {x + 60} 980 L {x + 60} 1440 L {x + 6} 1440 Z', C['trouS'], C['trouL']))
        sh = (f'M {x - 22} {y - 6} L {x + 14} {y - 6} C {x + 34} {y + 2}, {x + 54} {y + 12}, {x + 58} {y + 24} '
              f'C {x + 58} {y + 30}, {x + 50} {y + 32}, {x + 40} {y + 32} L {x - 8} {y + 30} C {x - 12} {y + 30}, {x - 14} {y + 34}, {x - 14} {y + 44} '
              f'L {x - 22} {y + 44} C {x - 26} {y + 30}, {x - 26} {y + 8}, {x - 22} {y - 6} Z')
        out.append(F(sh, C['shoe'], C['shoeL']))
    # far sleeve (behind), coat, lapels, blouse
    out.append(shaded('M 92 250 C 120 300, 124 420, 112 520 L 80 520 C 84 430, 82 330, 70 270 Z', C['coat'],
                      'M 90 250 L 140 250 L 140 520 L 100 520 Z', C['coatS'], C['coatL']))
    out.append(shaded(COAT, C['coat'], 'M -150 240 C -126 500, -120 760, -110 1020 L -160 1120 Z M 60 240 C 80 500, 86 760, 90 1120 L 140 1120 L 140 240 Z',
                      C['coatS'], C['coatL']))
    out.append(F('M -46 222 L 30 222 L 10 470 L -24 470 Z', C['blouse'], C['blouseL']))
    out.append(F('M -40 214 C -30 236, 18 236, 26 214 L 26 196 C 10 206, -26 206, -40 196 Z', C['blouse'], C['blouseL']))
    out.append(L('M -6 236 L -6 460', C['blouseL'], LW[0] * .7))
    out.append(F('M -60 226 L -24 470 L -60 420 L -84 300 Z', C['coatS'], C['coatL']))
    out.append(F('M 44 226 L 12 470 L 50 420 L 70 300 Z', C['coatS'], C['coatL']))
    out.append(L('M -12 470 L -14 1104', C['coatL'], LW[0] * .9))
    out.append(F('M -126 600 L 104 600 L 104 630 L -126 630 Z', C['coatS'], C['coatL']))
    out.append(F('M -30 596 L 4 596 L 4 634 L -30 634 Z', '#b9a065', '#5c4a1c'))
    # folder held to the chest by the far arm
    out.append(F('M -80 380 L 46 360 L 62 560 L -64 580 Z', C['folder'], C['folderL']))
    out.append(F('M -74 388 L 50 368 L 54 400 L -70 420 Z', '#f6f1e4', C['folderL'], LW[0] * .7))
    out.append(shaded('M 100 300 C 110 380, 100 440, 60 470 C 30 490, -20 492, -40 486 L -38 456 C -10 458, 30 450, 60 430 C 80 410, 80 360, 74 310 Z',
                      C['coat'], 'M 40 440 C 70 470, 100 470, 120 440 L 120 520 L 40 520 Z', C['coatS'], C['coatL']))
    out.append(F('M -40 452 C -56 450, -70 458, -72 470 C -72 482, -60 490, -40 488 Z', C['skin'], C['line']))
    # near arm hanging straight
    arm = 'M -116 240 C -140 280, -150 420, -146 560 C -144 640, -140 700, -138 740 L -104 740 C -104 660, -104 560, -100 440 C -98 360, -96 300, -92 270 Z'
    out.append(shaded(arm, C['coat'], 'M -170 240 C -150 400, -140 600, -130 760 L -170 760 Z', C['coatS'], C['coatL']))
    out.append(F('M -142 736 C -146 760, -144 790, -132 806 C -122 818, -106 812, -104 796 L -104 736 Z', C['skin'], C['line']))
    return ''.join(out)


def figure_q(expr='strict'):
    return body_q() + g(head_q(expr), 0, 26, 1) + collar()


def collar():
    return F('M -40 214 C -30 238, 18 238, 28 214 L 30 190 C 10 204, -26 204, -42 190 Z', C['blouse'], C['blouseL']) + \
        L('M -6 210 L -6 236', C['blouseL'], LW[0] * .7)
