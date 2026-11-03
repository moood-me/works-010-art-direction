"""Аня, about 20: warm, trusting, dreamy. Shape: a soft drop / S-curve; long copper hair."""
from lib import F, L, clip, shaded, g, LW, mx
from face import eye, brow, closed_eye, shout

C = dict(skin='#f4cdb0', shade='#e3a98c', line='#a8604a', blush='#f2967f', white='#fffaf3',
         iris='#6b7a3c', pupil='#2b2416', lash='#3b1d16',
         hair='#a8492e', hairS='#7e3220', hairH='#cf6d42', hairL='#4e1d14',
         lip='#d77467',
         knit='#6d8fb3', knitS='#557599', knitL='#36506e',
         dress='#e8b04a', dressS='#c98f31', dressL='#8a5a1c',
         sock='#f6eee2', shoe='#6b3a2a', shoeL='#3c1e15')

# ---------------------------------------------------------------- head, three-quarter (facing right)
# eye line y=0, chin about y=112, crown y=-122


BACK_Q = ('M 10 -140 C -70 -140, -116 -80, -112 -10 C -110 40, -124 90, -120 150 C -118 196, -104 230, -80 252 '
          'C -86 230, -84 214, -76 202 C -66 230, -46 246, -18 252 C -28 232, -28 212, -20 198 L 40 196 '
          'C 60 170, 84 140, 96 104 C 104 70, 106 30, 104 -20 C 98 -90, 64 -140, 10 -140 Z')
NEAR_Q = ('M 14 -130 C -40 -132, -96 -100, -100 -30 C -102 20, -96 60, -94 100 C -90 150, -98 200, -112 238 '
          'C -86 228, -72 208, -68 182 C -62 206, -50 222, -30 230 C -44 202, -52 162, -56 122 '
          'C -60 82, -68 40, -66 0 C -64 -50, -40 -84, 14 -112 Z')
FAR_Q = ('M 14 -130 C 60 -130, 98 -96, 100 -50 C 102 -20, 100 0, 96 16 C 92 -8, 84 -30, 70 -50 '
         'C 56 -70, 36 -96, 14 -112 Z')
FACE_Q = ('M -86 -40 C -90 10, -80 52, -52 82 C -28 104, 8 116, 36 114 C 52 112, 62 102, 70 88 '
          'C 78 72, 86 54, 88 34 C 90 18, 88 6, 88 -2 C 87 -12, 92 -20, 92 -32 C 94 -76, 56 -124, 0 -126 '
          'C -56 -126, -86 -90, -86 -40 Z')


def hair_back_q():
    shade = 'M -66 40 C -70 120, -56 200, -10 258 L -140 270 L -140 40 Z M 20 120 L 120 60 L 120 200 L 20 200 Z'
    return shaded(BACK_Q, C['hairS'], 'M 0 0', C['hairS'], C['hairL'])


def face_q(expr):
    face = FACE_Q
    neck = 'M -30 78 C -28 110, -30 140, -38 178 L 24 178 C 18 146, 18 120, 22 104 Z'
    neck_sh = 'M -60 60 C -20 105, 20 118, 50 100 L 50 128 C 10 140, -30 128, -60 112 Z'
    face_sh = 'M -100 -60 C -80 -30, -84 40, -40 96 L -110 120 Z'
    out = [shaded(neck, C['skin'], neck_sh, C['shade'], C['line'])]
    out.append(F(face, C['skin']))
    out.append(clip(face, F(face_sh, C['shade'], extra='opacity=".55"'),
                    g(F(NEAR_Q, C['shade']) + F(FAR_Q, C['shade']), 7, 8),
                    f'<ellipse cx="-30" cy="45" rx="24" ry="13" fill="{C["blush"]}" opacity=".45"/>',
                    f'<ellipse cx="70" cy="44" rx="13" ry="10" fill="{C["blush"]}" opacity=".45"/>'))
    out.append(L(face, C['line']))
    # eyes
    e = dict(C)
    look = {'dream': (6, -5), 'joy': (4, 0), 'surprise': (2, 0), 'sad': (2, 4), 'anger': (4, 2)}.get(expr, (5, -3))
    lid = {'dream': .26, 'joy': .1, 'surprise': 0, 'sad': .34, 'anger': .3}.get(expr, .16)
    lt = {'sad': -5, 'anger': 6}.get(expr, 0)
    if expr == 'joy':
        out.append(closed_eye(-16, 6, 21, e, up=True, w=2.2))
        out.append(closed_eye(56, 6, 15, e, up=True, w=2.0))
    else:
        rs = 1.12 if expr == 'surprise' else 1.0
        ir = 17 if expr != 'surprise' else 13
        out.append(eye(-14, 0, 24 * rs, 27 * rs, e, look=look, lid=lid, lidtilt=lt, ir=ir, flick=-1))
        out.append(eye(58, 0, 16 * rs, 26 * rs, e, look=(look[0] * .8, look[1]), lid=lid, lidtilt=lt, ir=ir * .95,
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
    nose = 'M 76 6 C 82 20, 92 30, 95 38 C 97 44, 92 48, 84 48 C 80 48, 76 46, 72 47 C 70 40, 74 26, 76 6 Z'
    out.append(F(nose, C['skin']))
    out.append(clip(nose, F('M 60 0 C 74 20, 78 38, 80 52 L 60 60 Z', C['shade'])))
    out.append(L('M 77 8 C 83 22, 92 30, 95 38 C 97 44, 92 48, 84 48 C 80 48, 77 47, 73 47', C['line'], LW[0] * .9))
    # mouth
    m = {
        'dream': L('M 26 70 C 36 78, 56 80, 70 68', C['line'], LW[0] * 1.1) +
                 L('M 22 66 C 24 69, 26 71, 28 71', C['line'], LW[0] * .8) +
                 F('M 38 84 C 46 89, 56 88, 62 83 C 54 85, 46 85, 38 84 Z', C['lip'], C['lip'], LW[0] * .8),
        'joy': F('M 22 66 C 36 70, 58 70, 72 62 C 70 86, 56 98, 44 98 C 32 98, 24 84, 22 66 Z', '#7a2a24', C['line']) +
               clip('M 22 66 C 36 70, 58 70, 72 62 C 70 86, 56 98, 44 98 C 32 98, 24 84, 22 66 Z',
                    F('M 18 60 L 76 56 L 74 74 C 56 80, 36 80, 18 74 Z', '#fff'),
                    '<ellipse cx="46" cy="98" rx="16" ry="9" fill="#e07a70"/>'),
        'surprise': F('M 40 76 C 48 72, 56 74, 58 84 C 58 96, 48 100, 42 96 C 36 92, 36 80, 40 76 Z', '#7a2a24', C['line']),
        'sad': L('M 30 82 C 40 74, 56 74, 64 80', C['line'], LW[0] * 1.1) +
               L('M 42 90 C 48 92, 54 92, 58 90', C['lip'], LW[0]),
        'anger': shout(24, 70, 70, 26, C['line']),
    }
    out.append(m.get(expr, m['dream']))
    out.append(freckles())
    return ''.join(out)


def hair_front_q():
    hiN = ('M -74 -96 C -54 -116, -24 -126, 2 -126 C -18 -116, -36 -104, -48 -92 C -58 -94, -66 -95, -74 -96 Z')
    hiF = 'M 30 -124 C 56 -120, 80 -104, 90 -82 C 76 -94, 58 -104, 40 -110 Z'
    out = [F(NEAR_Q, C['hair']), clip(NEAR_Q, F('M -120 40 C -90 80, -80 160, -60 240 L -130 240 Z', C['hairS']),
                                      F(hiN, C['hairH'])), L(NEAR_Q, C['hairL'])]
    out += [F(FAR_Q, C['hair']), clip(FAR_Q, F(hiF, C['hairH'])), L(FAR_Q, C['hairL'])]
    out.append(L('M -20 -120 C -56 -100, -78 -60, -80 -10 C -82 40, -76 90, -80 150', C['hairL'], LW[0] * .7))
    out.append(L('M -84 120 C -82 160, -86 190, -96 214', C['hairL'], LW[0] * .7))
    out.append(L('M 40 -118 C 66 -100, 84 -70, 90 -30', C['hairL'], LW[0] * .7))
    return ''.join(out)


def freckles():
    pts = [(-40, 30), (-30, 36), (-48, 38), (-22, 30), (-36, 44), (62, 30), (70, 36), (56, 38), (40, 22), (48, 30)]
    return ''.join(f'<circle cx="{x}" cy="{y}" r="1.9" fill="#c7745a" opacity=".7"/>' for x, y in pts)


def _unused_lock():
    return ''.join(out)


def head_q(expr='dream', tilt=-5, back=True, front=True):
    return f'<g transform="rotate({tilt} 0 100)">' + (hair_back_q() if back else '') + \
        (face_q(expr) + hair_front_q() if front else '') + '</g>'


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


# ---------------------------------------------------------------- full figure, three-quarter
DRESS = ('M -64 196 C -36 212, 20 212, 46 198 L 62 420 C 112 640, 156 900, 166 1130 '
         'C 60 1156, -70 1156, -172 1130 C -150 900, -102 640, -74 420 Z')
CARD_N = ('M -56 188 C -104 194, -138 218, -146 268 L -150 450 C -152 540, -144 600, -134 652 '
          'C -104 664, -72 664, -46 654 C -48 520, -42 360, -18 222 Z')
CARD_F = ('M 36 188 C 78 196, 102 220, 106 262 L 110 440 C 112 520, 116 590, 118 640 '
          'C 100 652, 80 652, 62 646 C 60 520, 56 360, 28 222 Z')
SLV_N = ('M -140 236 C -170 300, -174 380, -162 440 C -144 482, -94 512, -42 520 L -38 486 '
         'C -80 476, -114 450, -122 420 C -128 360, -120 300, -104 250 Z')
SLV_F = ('M 98 248 C 120 320, 118 392, 100 442 C 82 482, 34 506, 4 510 L 0 480 C 32 470, 70 442, 80 410 '
         'C 86 360, 82 302, 70 262 Z')


def leg(x0, x1, top, bottom, w0, w1, sock_top, flip=1):
    """A tapered leg with a calf, from (x0,top) to (x1,bottom); sock from sock_top down; shoe pointing right."""
    k = top + (bottom - top) * .35
    legd = (f'M {x0 - w0} {top} C {x0 - w0 - 4} {k}, {x1 - w1 - 2} {k + 40}, {x1 - w1} {bottom} '
            f'L {x1 + w1} {bottom} C {x1 + w1 + 2} {k + 60}, {x0 + w0 + 10} {k}, {x0 + w0} {top} Z')
    sock = f'M {x1 - w1 - 6} {sock_top} L {x1 + w1 + 6} {sock_top} L {x1 + w1 + 2} {bottom + 4} L {x1 - w1 - 2} {bottom + 4} Z'
    shoe = (f'M {x1 - w1 - 6} {bottom - 6} L {x1 + w1} {bottom - 8} C {x1 + w1 + 22} {bottom}, {x1 + w1 + 40} {bottom + 10}, '
            f'{x1 + w1 + 42} {bottom + 26} C {x1 + w1 + 42} {bottom + 38}, {x1 + 10} {bottom + 40}, {x1 - 10} {bottom + 40} '
            f'L {x1 - w1 - 8} {bottom + 38} C {x1 - w1 - 14} {bottom + 22}, {x1 - w1 - 12} {bottom + 6}, {x1 - w1 - 6} {bottom - 6} Z')
    strap = L(f'M {x1 - w1 - 4} {bottom + 2} C {x1} {bottom + 8}, {x1 + w1 + 8} {bottom + 6}, {x1 + w1 + 14} {bottom}',
              C['shoeL'], LW[0] * 1.6)
    return (shaded(legd, C['skin'], f'M {x0 - w0 - 20} {top} L {x0 - w0 + 10} {top} L {x1 - w1 + 6} {bottom} L {x1 - w1 - 20} {bottom} Z',
                   C['shade'], C['line'])
            + shaded(sock, C['sock'], f'M {x1 - w1 - 10} {sock_top} L {x1 - w1 + 8} {sock_top} L {x1 - w1 + 6} {bottom + 6} L {x1 - w1 - 10} {bottom + 6} Z', '#e2d6c4', '#9c8a76')
            + L(f'M {x1 - w1 - 5} {sock_top + 10} L {x1 + w1 + 5} {sock_top + 10}', '#c9b9a3', LW[0] * .8)
            + F(shoe, C['shoe'], C['shoeL']) + strap)


def body_q():
    out = []
    # far leg, then near leg
    out.append(leg(40, 50, 960, 1330, 19, 12, 1250))
    out.append(leg(-62, -76, 960, 1346, 21, 13, 1266))
    out.append(shaded(DRESS, C['dress'], 'M -170 300 C -120 560, -96 800, -66 1040 L -180 1160 Z M 20 420 C 66 600, 100 800, 106 1160 L 180 1160 L 180 400 Z',
                      C['dressS'], C['dressL']))
    out.append(L('M -24 640 C -18 800, -14 1000, -12 1146', C['dressL'], LW[0] * .7))
    out.append(L('M 58 620 C 84 800, 100 1000, 108 1140', C['dressL'], LW[0] * .7))
    # sash at the waist
    out.append(F('M -78 404 C -30 418, 20 416, 62 402 L 64 432 C 20 446, -30 448, -80 434 Z', '#d9805f', '#8a3a28'))
    out.append(F('M -60 194 C -30 220, 14 222, 42 196 C 38 212, 18 230, -10 232 C -40 232, -56 214, -60 194 Z',
                 C['sock'], C['dressL']))
    out.append(shaded(CARD_F, C['knit'], 'M 20 200 C 60 300, 64 500, 70 660 L 30 660 Z', C['knitS'], C['knitL']))
    out.append(shaded(SLV_F, C['knit'], 'M 60 250 C 90 330, 90 420, 60 470 L 120 470 L 120 250 Z', C['knitS'], C['knitL']))
    out.append(shaded(CARD_N, C['knit'], 'M -170 240 C -140 360, -130 520, -110 670 L -170 670 Z', C['knitS'], C['knitL']))
    # knitted ribs at the hem
    out.append(L('M -136 630 C -104 640, -74 640, -46 632', C['knitL'], LW[0] * .7))
    out.append(L('M 62 626 C 82 632, 100 632, 118 624', C['knitL'], LW[0] * .7))
    for y in (300, 380, 460, 540):
        out.append(f'<circle cx="-40" cy="{y}" r="6" fill="{C["dress"]}" stroke="{C["knitL"]}" stroke-width="1.8"/>')
    # book held against the body
    book = 'M -64 430 L 40 410 L 58 520 L -46 540 Z'
    out.append(F('M -60 438 L 44 418 L 60 524 L -44 544 Z', '#f3ead8', '#7d4a33'))
    out.append(F(book, '#b2533c', '#5e2318'))
    out.append(L('M -50 450 L 36 434', '#e6b863', LW[0] * .9))
    out.append(shaded(SLV_N, C['knit'], 'M -190 260 C -170 360, -160 440, -110 520 L -190 520 Z', C['knitS'], C['knitL']))
    # hands
    out.append(F('M -46 482 C -30 476, -10 480, 0 490 C 6 500, 0 510, -10 512 C -24 516, -40 518, -48 514 Z', C['skin'], C['line']))
    out.append(F('M 0 476 C 14 470, 30 474, 34 486 C 36 496, 26 502, 14 504 C 6 506, 0 500, 0 476 Z', C['skin'], C['line']))
    out.append(L('M -30 494 C -22 494, -14 496, -8 500', C['line'], LW[0] * .7))
    return ''.join(out)


def figure_q(expr='dream'):
    return head_q(expr, front=False) + body_q() + head_q(expr, back=False)


# ---------------------------------------------------------------- front view
FACE_F = ('M -84 -40 C -86 20, -70 70, -40 98 C -22 112, 22 112, 40 98 C 70 70, 86 20, 84 -40 '
          'C 84 -90, 50 -126, 0 -126 C -50 -126, -84 -90, -84 -40 Z')
CURT_F = ('M 0 -132 C -56 -132, -100 -98, -102 -30 C -104 20, -98 60, -96 100 C -92 150, -100 200, -114 238 '
          'C -88 228, -74 208, -70 182 C -64 206, -52 222, -32 230 C -46 202, -54 162, -58 122 '
          'C -62 82, -72 40, -72 0 C -70 -50, -46 -88, 0 -112 Z')
BACK_F = ('M 0 -142 C -76 -142, -118 -80, -114 -10 C -112 40, -126 90, -122 150 C -120 196, -106 230, -82 252 '
          'C -40 262, 40 262, 82 252 C 106 230, 120 196, 122 150 C 126 90, 112 40, 114 -10 C 118 -80, 76 -142, 0 -142 Z')


def head_f(expr='dream', back=True):
    out = [F(BACK_F, C['hairS'], C['hairL'])] if back else []
    out.append(shaded('M -26 80 C -24 120, -26 150, -32 178 L 32 178 C 26 150, 24 120, 26 80 Z', C['skin'],
                      'M -40 70 C -20 110, 20 110, 40 70 L 40 128 C 10 140, -10 140, -40 128 Z', C['shade'], C['line']))
    out.append(F(FACE_F, C['skin']))
    out.append(clip(FACE_F, F('M -100 -60 C -80 -20, -80 50, -40 110 L -110 120 Z', C['shade'], extra='opacity=".55"'),
                    g(F(CURT_F, C['shade']) + F(mx(CURT_F), C['shade']), 0, 8),
                    f'<ellipse cx="-46" cy="44" rx="20" ry="12" fill="{C["blush"]}" opacity=".45"/>',
                    f'<ellipse cx="46" cy="44" rx="20" ry="12" fill="{C["blush"]}" opacity=".45"/>'))
    out.append(L(FACE_F, C['line']))
    look = (0, -3) if expr == 'dream' else (0, 0)
    lid = .26 if expr == 'dream' else .16
    out.append(eye(-36, 0, 22, 26, C, look=look, lid=lid, ir=16, flick=-1))
    out.append(eye(36, 0, 22, 26, C, look=look, lid=lid, ir=16, flick=1))
    out.append(brow(-12, -38, -56, -36, 5, 6, C['hairL']))
    out.append(brow(12, -38, 56, -36, 5, 6, C['hairL']))
    out.append(F('M -2 22 C 4 34, 10 40, 8 46 C 4 50, -4 50, -8 47 C -4 44, 0 40, -2 22 Z', C['shade']))
    out.append(L('M -9 46 C -4 50, 4 50, 9 46', C['line'], LW[0] * .9))
    out.append(L('M -20 70 C -8 78, 8 78, 20 70', C['line'], LW[0] * 1.1))
    out.append(F('M -8 82 C -2 86, 4 86, 8 82 C 2 84, -2 84, -8 82 Z', C['lip'], C['lip'], LW[0] * .8))
    for x, y in ((-50, 28), (-40, 34), (-58, 36), (-32, 26), (50, 28), (40, 34), (58, 36), (32, 26), (-46, 42), (46, 42)):
        out.append(f'<circle cx="{x}" cy="{y}" r="1.9" fill="#c7745a" opacity=".7"/>')
    hi = 'M -70 -100 C -50 -118, -24 -126, -4 -128 C -20 -118, -36 -106, -48 -94 C -58 -96, -66 -97, -70 -100 Z'
    for d, h in ((CURT_F, hi), (mx(CURT_F), mx(hi))):
        out.append(F(d, C['hair']) + clip(d, F(h, C['hairH'])) + L(d, C['hairL']))
    out.append(L('M -20 -120 C -60 -100, -80 -60, -84 -10 C -86 40, -80 90, -84 150', C['hairL'], LW[0] * .7))
    out.append(L('M 20 -120 C 60 -100, 80 -60, 84 -10 C 86 40, 80 90, 84 150', C['hairL'], LW[0] * .7))
    return ''.join(out)


DRESS_F = ('M -58 196 C -30 212, 30 212, 58 196 L 70 420 C 116 640, 156 900, 164 1130 '
           'C 60 1154, -60 1154, -164 1130 C -156 900, -116 640, -70 420 Z')
CARD_FL = ('M -50 188 C -100 194, -132 216, -140 266 L -144 450 C -146 540, -140 600, -132 652 '
           'C -104 664, -74 664, -48 654 C -50 520, -46 360, -20 222 Z')
ARM_FL = ('M -134 230 C -160 290, -168 380, -168 460 C -168 520, -164 570, -162 610 L -132 610 '
          'C -132 560, -132 500, -130 440 C -128 360, -124 300, -112 252 Z')


def body_f():
    out = []
    for x in (-40, 40):
        out.append(leg_front(x))
    out.append(shaded(DRESS_F, C['dress'], 'M -170 300 C -120 560, -100 800, -76 1160 L -180 1160 Z', C['dressS'], C['dressL']))
    out.append(L('M -40 640 C -40 800, -42 1000, -44 1148', C['dressL'], LW[0] * .7))
    out.append(L('M 40 640 C 40 800, 42 1000, 44 1148', C['dressL'], LW[0] * .7))
    out.append(F('M -78 404 C -30 418, 30 418, 78 404 L 80 434 C 30 448, -30 448, -80 434 Z', '#d9805f', '#8a3a28'))
    out.append(F('M -56 194 C -30 220, 30 220, 56 194 C 50 212, 26 230, 0 232 C -26 230, -50 212, -56 194 Z', C['sock'], C['dressL']))
    for d, sh in ((CARD_FL, 'M -170 240 C -140 360, -130 520, -110 670 L -170 670 Z'), (mx(CARD_FL), 'M 20 200 C 46 300, 50 500, 54 670 L 40 670 Z')):
        out.append(shaded(d, C['knit'], sh, C['knitS'], C['knitL']))
    for d, sh in ((ARM_FL, 'M -190 240 C -170 360, -166 480, -150 620 L -190 620 Z'), (mx(ARM_FL), 'M 140 240 L 190 240 L 190 620 L 150 620 Z')):
        out.append(shaded(d, C['knit'], sh, C['knitS'], C['knitL']))
    out.append(F('M -164 604 C -168 630, -164 660, -150 670 C -138 676, -128 664, -130 650 L -130 604 Z', C['skin'], C['line']))
    out.append(F('M 164 604 C 168 630, 164 660, 150 670 C 138 676, 128 664, 130 650 L 130 604 Z', C['skin'], C['line']))
    for y in (300, 380, 460, 540):
        out.append(f'<circle cx="-36" cy="{y}" r="6" fill="{C["dress"]}" stroke="{C["knitL"]}" stroke-width="1.8"/>')
    return ''.join(out)


def leg_front(x):
    top, bottom = 960, 1340
    s = 1 if x > 0 else -1
    legd = f'M {x - 20} {top} C {x - 24} 1080, {x - 16} 1200, {x - 12} {bottom} L {x + 12} {bottom} C {x + 18} 1200, {x + 24} 1080, {x + 20} {top} Z'
    sock = f'M {x - 18} 1252 L {x + 18} 1252 L {x + 15} {bottom + 4} L {x - 15} {bottom + 4} Z'
    shoe = (f'M {x - 18} {bottom - 4} L {x + 18} {bottom - 4} C {x + 24} {bottom + 10}, {x + 26} {bottom + 28}, {x + 20} {bottom + 38} '
            f'L {x - 20} {bottom + 38} C {x - 26} {bottom + 28}, {x - 24} {bottom + 10}, {x - 18} {bottom - 4} Z')
    return (shaded(legd, C['skin'], f'M {x - 40} {top} L {x - 8} {top} L {x - 4} {bottom} L {x - 40} {bottom} Z', C['shade'], C['line'])
            + F(sock, C['sock'], '#9c8a76') + F(shoe, C['shoe'], C['shoeL'])
            + L(f'M {x - 16} {bottom + 6} L {x + 16} {bottom + 6}', C['shoeL'], LW[0] * 1.6))


def figure_f(expr='dream'):
    return F(BACK_F, C['hairS'], C['hairL']) + body_f() + head_f(expr, back=False)


# ---------------------------------------------------------------- side view (facing right)
FACE_S = ('M -96 -40 C -100 -100, -40 -128, 10 -126 C 50 -124, 70 -96, 72 -60 C 74 -40, 72 -24, 76 -10 '
          'C 78 0, 84 12, 92 26 C 98 36, 102 42, 98 47 C 94 52, 86 52, 80 54 C 82 60, 84 64, 82 68 '
          'C 80 72, 78 74, 80 78 C 82 84, 78 90, 74 92 C 72 100, 66 108, 52 112 C 30 116, 10 110, -4 100 '
          'C -40 96, -92 40, -96 -40 Z')
HAIR_S = ('M 30 -134 C -40 -142, -110 -100, -112 -20 C -114 40, -122 120, -118 200 C -116 230, -106 250, -90 262 '
          'C -96 240, -94 224, -86 214 C -78 236, -62 252, -40 258 C -52 230, -50 200, -40 170 '
          'C -30 120, -30 60, -28 20 C -26 -20, -10 -60, 20 -80 C 40 -92, 58 -96, 70 -96 C 66 -116, 50 -132, 30 -134 Z')


def head_s(expr='dream'):
    out = []
    out.append(shaded('M -30 70 C -26 110, -28 140, -36 178 L 30 178 C 22 150, 22 124, 26 104 Z', C['skin'],
                      'M -60 60 L 30 110 L 30 140 L -60 140 Z', C['shade'], C['line']))
    out.append(F(FACE_S, C['skin']))
    out.append(clip(FACE_S, g(F(HAIR_S, C['shade']), 6, 8),
                    f'<ellipse cx="40" cy="44" rx="22" ry="13" fill="{C["blush"]}" opacity=".45"/>'))
    out.append(L(FACE_S, C['line']))
    out.append(eye(52, 0, 12, 25, C, look=(5, -3), lid=.26, ir=14, sq=.55, flick=-1, lowline=False))
    out.append(brow(40, -38, 68, -36, 4, 6, C['hairL']))
    out.append(L('M 60 70 C 66 72, 72 72, 76 70', C['line'], LW[0] * 1.0))
    for x, y in ((40, 30), (50, 34), (32, 36), (58, 28)):
        out.append(f'<circle cx="{x}" cy="{y}" r="1.9" fill="#c7745a" opacity=".7"/>')
    out.append(L('M 84 46 C 80 44, 76 46, 76 50', C['line'], LW[0] * .8))
    # ear peeking through the hair
    out.append(F('M -14 -6 C -30 -16, -40 6, -32 26 C -28 36, -18 38, -12 30 Z', C['skin'], C['line']))
    hi = 'M -60 -110 C -30 -128, 10 -132, 40 -126 C 10 -120, -20 -110, -44 -96 Z'
    out.append(F(HAIR_S, C['hair']) + clip(HAIR_S, F(hi, C['hairH']),
                                           F('M -130 40 C -100 100, -90 180, -70 270 L -140 270 Z', C['hairS'])) + L(HAIR_S, C['hairL']))
    out.append(L('M 10 -110 C -40 -90, -70 -40, -76 20 C -80 80, -84 150, -90 220', C['hairL'], LW[0] * .7))
    return ''.join(out)


def body_s():
    out = []
    # legs side by side, feet pointing right
    for dx in (14, -10):
        top, bottom = 960, 1344
        x = dx
        legd = f'M {x - 20} {top} C {x - 26} 1080, {x - 18} 1220, {x - 14} {bottom} L {x + 10} {bottom} C {x + 18} 1220, {x + 22} 1080, {x + 20} {top} Z'
        out.append(shaded(legd, C['skin'], f'M {x - 40} {top} L {x - 6} {top} L {x - 2} {bottom} L {x - 40} {bottom} Z', C['shade'], C['line']))
        out.append(F(f'M {x - 18} 1256 L {x + 14} 1256 L {x + 12} {bottom + 4} L {x - 16} {bottom + 4} Z', C['sock'], '#9c8a76'))
        out.append(F(f'M {x - 20} {bottom - 6} L {x + 12} {bottom - 6} C {x + 40} {bottom + 2}, {x + 54} {bottom + 16}, {x + 54} {bottom + 30} '
                     f'C {x + 50} {bottom + 40}, {x + 10} {bottom + 40}, {x - 20} {bottom + 38} C {x - 26} {bottom + 20}, {x - 26} {bottom + 4}, {x - 20} {bottom - 6} Z',
                     C['shoe'], C['shoeL']))
    dress = ('M -40 196 C -10 206, 20 206, 40 196 C 60 300, 70 380, 54 420 C 92 640, 124 900, 126 1130 '
             'C 40 1150, -60 1150, -136 1130 C -124 900, -92 640, -60 420 C -66 340, -60 260, -40 196 Z')
    out.append(shaded(dress, C['dress'], 'M -140 400 C -100 600, -80 800, -60 1160 L -150 1160 Z', C['dressS'], C['dressL']))
    out.append(F('M -60 404 C -20 414, 20 414, 56 404 L 58 434 C 20 444, -20 444, -62 434 Z', '#d9805f', '#8a3a28'))
    card = ('M -40 188 C -76 200, -92 240, -94 300 L -100 460 C -102 540, -96 600, -90 652 C -40 664, 20 664, 60 650 '
            'C 64 560, 70 460, 62 400 C 66 330, 60 260, 40 192 Z')
    out.append(F(card, C['knit']) + clip(card, F('M -120 200 C -90 360, -80 520, -60 680 L -120 680 Z', C['knitS']),
                                         F('M 6 200 L 70 200 L 70 680 L 10 680 Z', C['dress'])) + L(card, C['knitL']))
    out.append(L('M 6 210 L 6 652', C['knitL'], LW[0] * .8))
    out.append(L('M -88 630 C -40 640, 20 640, 60 630', C['knitL'], LW[0] * .7))
    arm = ('M -40 220 C -64 280, -70 380, -64 460 C -60 520, -54 570, -50 610 L -20 610 C -22 560, -24 500, -26 440 '
           'C -28 360, -20 290, 0 240 Z')
    out.append(shaded(arm, C['knit'], 'M -80 240 C -66 380, -60 500, -50 620 L -80 620 Z', C['knitS'], C['knitL']))
    out.append(F('M -52 604 C -54 630, -48 660, -34 668 C -22 672, -14 660, -18 646 L -20 604 Z', C['skin'], C['line']))
    return ''.join(out)


def figure_s(expr='dream'):
    return body_s() + head_s(expr)
