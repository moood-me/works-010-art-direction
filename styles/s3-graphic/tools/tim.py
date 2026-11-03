"""Тим, about 8: mischievous, curious. Shape: a circle / ball; big head, spiky hair, ears out."""
from lib import F, L, clip, shaded, g, LW
from face import eye, brow, closed_eye, shout

C = dict(skin='#f2c29c', shade='#dda07e', line='#9a5c44', blush='#ef8f78', white='#fffaf3',
         iris='#6b4a2c', pupil='#1d140e', lash='#2e1d16',
         hair='#4a3022', hairS='#33201a', hairH='#6e4a34', hairL='#1e120d',
         shirt='#e4553f', shirtS='#c0412f', shirtL='#7a2219', stripe='#f6e7cc',
         shorts='#36557a', shortsS='#2a4462', shortsL='#16263a',
         sock='#f4ecdf', shoe='#e9e2d4', shoeL='#3a3a3e', sole='#c7473a', plaster='#f1d9a6')

FACE_Q = ('M -100 0 C -100 -70, -50 -112, 10 -112 C 70 -112, 104 -70, 104 -10 C 104 20, 100 40, 96 56 '
          'C 86 92, 56 110, 20 110 C -30 110, -76 90, -94 50 C -100 36, -100 18, -100 0 Z')
HAIR_Q = ('M -104 -10 C -112 -60, -84 -114, -14 -122 L -26 -150 L 8 -126 L 18 -156 L 40 -122 '
          'C 82 -116, 110 -84, 110 -42 L 126 -50 L 106 -14 C 102 -36, 94 -54, 82 -64 '
          'C 72 -52, 56 -48, 38 -50 L 46 -68 C 28 -56, 6 -52, -18 -56 L -10 -74 '
          'C -30 -62, -54 -54, -74 -48 C -84 -34, -90 -20, -92 -2 Z')


def head_q(expr='mischief', tilt=4):
    out = []
    out.append(shaded('M -30 90 L -32 132 L 30 132 L 32 96 Z', C['skin'], 'M -40 80 L 40 104 L 40 140 L -40 140 Z',
                      C['shade'], C['line']))
    # ears, sticking out
    for ex, s in ((-98, 1),):
        ear = f'M {ex + 10} -6 C {ex - 22} -26, {ex - 40} 4, {ex - 28} 34 C {ex - 20} 52, {ex} 52, {ex + 10} 40 Z'
        out.append(shaded(ear, C['skin'], f'M {ex - 50} 10 L {ex + 20} 10 L {ex + 20} 60 L {ex - 50} 60 Z', C['shade'], C['line']))
        out.append(L(f'M {ex - 12} 0 C {ex - 26} 10, {ex - 24} 28, {ex - 12} 34', C['line'], LW[0] * .8))
    out.append(F(FACE_Q, C['skin']))
    out.append(clip(FACE_Q,
                    F('M -120 -40 C -96 0, -90 60, -50 120 L -120 120 Z', C['shade'], extra='opacity=".55"'),
                    g(F(HAIR_Q, C['shade']), 4, 10),
                    f'<ellipse cx="-36" cy="54" rx="26" ry="15" fill="{C["blush"]}" opacity=".5"/>',
                    f'<ellipse cx="84" cy="50" rx="13" ry="12" fill="{C["blush"]}" opacity=".5"/>'))
    out.append(L(FACE_Q, C['line']))
    # freckles over the nose
    for x, y in ((-30, 40), (-20, 44), (-40, 46), (60, 38), (70, 42)):
        out.append(f'<circle cx="{x}" cy="{y}" r="2" fill="#c06e52" opacity=".7"/>')
    # eyes
    look = {'mischief': (9, 0), 'joy': (4, 0), 'surprise': (2, -2), 'sad': (2, 5), 'anger': (5, 2), 'curious': (6, -3)}.get(expr, (8, 0))
    if expr == 'joy':
        out.append(closed_eye(-14, 12, 22, C, up=True, w=2.4))
        out.append(closed_eye(60, 12, 15, C, up=True, w=2.2))
    else:
        lidN = {'mischief': .38, 'surprise': 0, 'sad': .3, 'anger': .32, 'curious': .05}.get(expr, .2)
        lidF = {'mischief': .22, 'surprise': 0, 'sad': .3, 'anger': .32, 'curious': .05}.get(expr, .2)
        ltN = {'mischief': 3, 'sad': -6, 'anger': 6}.get(expr, 0)
        rs = 1.12 if expr == 'surprise' else 1
        ir = 13 if expr == 'surprise' else 16
        lowN = .25 if expr == 'mischief' else 0
        out.append(eye(-14, 10, 23 * rs, 26 * rs, C, look=look, lid=lidN, lidtilt=-ltN, lower=lowN, ir=ir, flick=-1, lash=1.9, wing=False))
        out.append(eye(60, 10, 16 * rs, 25 * rs, C, look=look, lid=lidF, lidtilt=ltN, ir=ir * .95, sq=.78, flick=1, lash=1.8, wing=False))
    # brows: thick and asymmetric
    bb = {'mischief': ((-40, -26, -2, -30, 6), (40, -30, 74, -40, 10)),
          'curious': ((-40, -30, -2, -40, 8), (40, -40, 74, -42, 8)),
          'joy': ((-40, -24, -2, -32, 8), (40, -32, 74, -30, 8)),
          'surprise': ((-40, -40, -2, -48, 8), (40, -48, 74, -46, 8)),
          'sad': ((-40, -18, -2, -30, -2), (40, -30, 72, -18, -2)),
          'anger': ((-40, -30, -2, -14, 0), (40, -14, 74, -28, 0))}.get(expr)
    (a0, a1, a2, a3, ab), (b0, b1, b2, b3, bb_) = bb
    out.append(brow(a2, a3, a0, a1, ab, 8, C['hairL']))
    out.append(brow(b0, b1, b2, b3, bb_, 7, C['hairL']))
    # nose: small button + a plaster across it
    nose = 'M 80 18 C 90 26, 100 36, 98 46 C 96 54, 86 56, 76 52 C 74 40, 78 30, 80 18 Z'
    out.append(F(nose, C['skin']))
    out.append(clip(nose, F('M 60 20 C 76 36, 80 48, 82 60 L 60 60 Z', C['shade'])))
    out.append(L('M 81 20 C 90 26, 100 36, 98 46 C 96 54, 86 56, 77 52', C['line'], LW[0] * .9))
    out.append(F('M -58 40 L -22 30 L -18 46 L -54 56 Z', C['plaster'], '#b08a55', LW[0] * .8))
    out.append(L('M -42 38 L -40 48 M -34 36 L -32 46', '#b08a55', LW[0] * .6))
    # mouth
    grin = 'M 8 64 C 30 72, 64 70, 88 54 C 90 80, 70 98, 46 98 C 26 98, 12 84, 8 64 Z'
    m = {
        'mischief': F(grin, '#6e2620', C['line']) + clip(grin, F('M 0 56 L 96 46 L 96 70 C 70 78, 30 80, 0 72 Z', '#fff'),
                                                          F('M 40 60 L 52 58 L 52 76 L 40 78 Z', '#6e2620'),
                                                          '<ellipse cx="46" cy="100" rx="22" ry="12" fill="#de6e64"/>'),
        'joy': F('M 2 60 C 30 70, 70 66, 92 50 C 94 86, 72 106, 46 106 C 22 106, 6 86, 2 60 Z', '#6e2620', C['line']) +
               clip('M 2 60 C 30 70, 70 66, 92 50 C 94 86, 72 106, 46 106 C 22 106, 6 86, 2 60 Z',
                    F('M -4 52 L 100 42 L 100 66 C 70 76, 30 78, -4 70 Z', '#fff'),
                    F('M 40 58 L 52 56 L 52 74 L 40 76 Z', '#6e2620'),
                    '<ellipse cx="48" cy="106" rx="24" ry="14" fill="#de6e64"/>'),
        'curious': F('M 36 70 C 44 66, 56 66, 60 74 C 62 84, 54 90, 46 88 C 38 86, 32 78, 36 70 Z', '#6e2620', C['line']),
        'surprise': F('M 32 66 C 42 60, 58 60, 64 72 C 68 90, 56 102, 46 100 C 34 98, 26 82, 32 66 Z', '#6e2620', C['line']) +
                    clip('M 32 66 C 42 60, 58 60, 64 72 C 68 90, 56 102, 46 100 C 34 98, 26 82, 32 66 Z',
                         '<ellipse cx="48" cy="102" rx="14" ry="10" fill="#de6e64"/>'),
        'sad': L('M 18 84 C 32 72, 56 72, 70 82', C['line'], LW[0] * 1.2) +
               F('M 40 86 C 46 92, 54 92, 58 86 Z', C['line'], extra='opacity=".0"'),
        'anger': shout(10, 86, 62, 34, C['line']),
    }
    out.append(m.get(expr, m['mischief']))
    # hair: dark mass with spikes and a cowlick
    out.append(F(HAIR_Q, C['hair']))
    out.append(clip(HAIR_Q, F('M -80 -96 C -50 -116, 0 -124, 40 -114 C 10 -110, -20 -104, -44 -92 Z', C['hairH']),
                    F('M -120 -40 C -100 -60, -60 -60, -40 -50 L -40 0 L -120 0 Z', C['hairS'])))
    out.append(L(HAIR_Q, C['hairL']))
    out.append(L('M -40 -100 C -50 -84, -56 -70, -56 -56', C['hairL'], LW[0] * .7))
    out.append(L('M 50 -104 C 66 -90, 74 -78, 76 -62', C['hairL'], LW[0] * .7))
    return f'<g transform="rotate({tilt} 0 100)">' + ''.join(out) + '</g>'


# ---------------------------------------------------------------- body, three-quarter; hands in pockets
SHIRT = ('M -78 126 C -110 132, -124 156, -126 186 L -114 336 L 106 336 L 112 186 '
         'C 110 156, 94 132, 66 126 C 40 140, -50 140, -78 126 Z')


def body_q():
    out = []
    # legs
    for d, sh in (('M 38 440 L 86 440 C 86 520, 82 580, 80 640 L 50 640 C 48 580, 42 520, 38 440 Z', 'M 70 440 L 100 440 L 100 640 L 70 640 Z'),
                  ('M -94 440 L -40 440 C -40 520, -44 580, -46 650 L -80 650 C -84 580, -92 520, -94 440 Z', 'M -110 440 L -78 440 L -70 650 L -110 650 Z')):
        out.append(shaded(d, C['skin'], sh, C['shade'], C['line']))
    # knee plaster
    out.append(F('M -82 520 L -50 512 L -46 530 L -78 538 Z', C['plaster'], '#b08a55', LW[0] * .8))
    out.append(L('M -70 518 L -68 532 M -60 516 L -58 530', '#b08a55', LW[0] * .5))
    # socks and sneakers
    for x, y in ((64, 630), (-64, 640)):
        out.append(F(f'M {x - 20} {y - 20} L {x + 20} {y - 20} L {x + 20} {y + 8} L {x - 20} {y + 8} Z', C['sock'], '#9c8a76'))
        out.append(L(f'M {x - 20} {y - 12} L {x + 20} {y - 12}', '#d06a55', LW[0] * 1.4))
        sh = (f'M {x - 28} {y} L {x + 18} {y - 4} C {x + 46} {y}, {x + 66} {y + 14}, {x + 68} {y + 32} '
              f'L {x - 30} {y + 34} C {x - 34} {y + 20}, {x - 34} {y + 8}, {x - 28} {y} Z')
        out.append(F(sh, C['shoe'], C['shoeL']))
        out.append(F(f'M {x - 32} {y + 28} L {x + 68} {y + 26} L {x + 68} {y + 38} C {x + 30} {y + 42}, {x - 10} {y + 42}, {x - 32} {y + 40} Z', C['sole'], C['shoeL']))
        out.append(L(f'M {x - 4} {y + 2} L {x + 4} {y + 12} M {x + 8} {y} L {x + 16} {y + 10}', C['shoeL'], LW[0] * .8))
    # shorts
    shorts = 'M -112 316 L 106 316 L 112 446 L 14 452 L 0 390 L -14 452 L -118 446 Z'
    out.append(shaded(shorts, C['shorts'], 'M -130 316 L -80 316 L -86 460 L -130 460 Z M 60 316 L 130 316 L 130 460 L 70 460 Z',
                      C['shortsS'], C['shortsL']))
    out.append(L('M -100 340 C -90 360, -80 370, -66 374', C['shortsL'], LW[0] * .8))
    out.append(L('M 96 340 C 86 360, 76 370, 62 374', C['shortsL'], LW[0] * .8))
    # shirt with stripes
    stripes = ''.join(F(f'M -140 {y} L 140 {y} L 140 {y + 12} L -140 {y + 12} Z', C['stripe']) for y in range(160, 340, 36))
    out.append(F(SHIRT, C['shirt']))
    out.append(clip(SHIRT, stripes, F('M -140 120 C -110 200, -110 280, -90 340 L -140 340 Z M 70 120 C 90 200, 96 280, 90 340 L 140 340 L 140 120 Z',
                                      C['shirtL'], extra='opacity=".22"')))
    out.append(L(SHIRT, C['shirtL']))
    out.append(F('M -78 126 C -50 146, 40 146, 66 126 C 50 136, -40 140, -78 126 Z', C['shirtS'], C['shirtL']))
    # arms: elbows out, hands in pockets
    for sgn, x0 in ((1, 0),):
        pass
    arms = [
        ('M -98 132 C -132 140, -150 166, -152 204 L -114 214 C -112 184, -104 164, -90 152 Z',
         'M -150 196 C -158 250, -132 300, -100 336 L -80 320 C -104 292, -118 250, -114 206 Z'),
        ('M 86 132 C 120 140, 138 166, 140 204 L 102 214 C 100 184, 92 164, 80 152 Z',
         'M 138 196 C 146 250, 122 300, 92 336 L 72 320 C 96 292, 106 250, 102 206 Z'),
    ]
    for slv, fore in arms:
        out.append(shaded(fore, C['skin'], 'M -200 260 L 200 260 L 200 340 L -200 340 Z', C['shade'], C['line']))
        out.append(F(slv, C['shirt'], C['shirtL']))
        out.append(clip(slv, F('M -200 170 L 200 170 L 200 182 L -200 182 Z', C['stripe'])))
    # pocket slits over the wrists
    out.append(L('M -112 330 C -96 336, -80 334, -70 324', C['shortsL'], LW[0] * 1.2))
    out.append(L('M 104 330 C 90 336, 76 334, 64 324', C['shortsL'], LW[0] * 1.2))
    return ''.join(out)


def figure_q(expr='mischief'):
    return body_q() + g(head_q(expr), 0, 4, 1)
