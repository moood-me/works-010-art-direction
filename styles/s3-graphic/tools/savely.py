"""Савелий Петрович, about 70, a watchmaker: grumpy outside, kind inside. Shape: a square / barrel; short, stocky."""
from lib import F, L, clip, shaded, g, LW, mx
from face import eye, brow, closed_eye

C = dict(skin='#eab898', shade='#d4927a', line='#8e5644', blush='#e7866f', white='#fffaf3',
         iris='#5f7f97', pupil='#1f2a33', lash='#4a2a22',
         hair='#eeebe4', hairS='#cdc8be', hairL='#8d877c',
         vest='#56705a', vestS='#435a47', vestL='#283a2c',
         shirt='#f0e6d2', shirtS='#d8c9ae', shirtL='#8f7d62',
         trou='#6b5a4e', trouS='#55463c', trouL='#2f2520',
         shoe='#3f2a22', shoeL='#1f1410', brass='#d9a441', brassL='#8a6420')

FACE_Q = ('M -96 -30 C -100 -90, -50 -124, 0 -124 C 56 -124, 92 -90, 94 -40 C 95 -20, 92 -8, 94 4 '
          'C 98 22, 96 44, 90 64 C 82 92, 62 110, 28 114 C -12 118, -52 104, -74 80 C -94 58, -96 20, -96 -30 Z')


def head_q(expr='grump', tilt=0):
    out = []
    # neck / collar back
    out.append(shaded('M -46 80 L -44 132 L 34 132 L 36 100 Z', C['skin'], 'M -70 60 L 50 100 L 50 140 L -70 140 Z',
                      C['shade'], C['line']))
    out.append(F(FACE_Q, C['skin']))
    out.append(clip(FACE_Q,
                    F('M -110 -80 C -80 -40, -84 40, -40 110 L -120 120 Z', C['shade'], extra='opacity=".6"'),
                    F('M -20 -124 C 20 -128, 60 -110, 80 -84 C 50 -100, 20 -108, -20 -112 Z', '#f7d3bb'),
                    f'<ellipse cx="-34" cy="38" rx="26" ry="16" fill="{C["blush"]}" opacity=".5"/>',
                    f'<ellipse cx="78" cy="36" rx="12" ry="12" fill="{C["blush"]}" opacity=".5"/>'))
    out.append(L(FACE_Q, C['line']))
    # forehead wrinkles
    for i, y in enumerate((-82, -70)):
        out.append(L(f'M {-30 + i * 6} {y} C {0} {y - 5}, {30} {y - 5}, {56 - i * 6} {y + 1}', C['line'], LW[0] * .7, 'opacity=".7"'))
    # white hair: a crescent around the back of the head, then the ear over it
    hair = ('M -78 -74 C -100 -66, -116 -40, -118 -10 C -122 24, -112 58, -90 82 C -80 92, -66 96, -54 94 '
            'C -70 80, -78 62, -80 44 L -76 -10 C -78 -30, -76 -50, -68 -70 Z')
    out.append(shaded(hair, C['hair'], 'M -130 10 C -110 50, -90 80, -60 100 L -130 100 Z', C['hairS'], C['hairL']))
    for d in ('M -106 -30 C -100 -20, -96 -10, -96 0', 'M -110 30 C -104 42, -98 54, -88 64'):
        out.append(L(d, C['hairL'], LW[0] * .6))
    ear = 'M -84 -12 C -110 -24, -124 2, -116 28 C -110 46, -94 52, -80 42'
    out.append(F(ear + ' Z', C['skin'], C['line']))
    out.append(L('M -98 2 C -106 10, -104 24, -96 30', C['line'], LW[0] * .8))
    # the loupe on a band over the forehead
    out.append(L('M -94 -60 C -40 -74, 30 -76, 92 -58', '#3a302a', LW[0] * 2.4))
    loupe = 'M 30 -82 L 66 -86 L 78 -58 L 34 -52 Z'
    out.append(F(loupe, '#2e2a28', '#14100e'))
    out.append(F('M 64 -88 C 76 -90, 86 -76, 80 -58 C 76 -56, 70 -60, 66 -66 Z', '#5d5650', '#14100e'))
    out.append(F('M 40 -78 L 58 -80 L 56 -76 L 42 -74 Z', '#6b625b'))
    # eyes: small, under heavy brows
    look = {'grump': (3, 1), 'joy': (2, 0), 'surprise': (2, 0), 'sad': (1, 3), 'anger': (3, 1), 'kind': (3, 0)}.get(expr, (3, 1))
    lid = {'grump': .42, 'joy': .1, 'surprise': 0, 'sad': .45, 'anger': .4, 'kind': .3}.get(expr, .4)
    lt = {'grump': 4, 'anger': 6, 'sad': -4}.get(expr, 0)
    if expr == 'joy':
        out.append(closed_eye(-20, 0, 14, C, up=True, w=2.2))
        out.append(closed_eye(54, 0, 10, C, up=True, w=2.0))
    else:
        rs = 1.25 if expr == 'surprise' else 1
        out.append(eye(-20, 0, 14 * rs, 13 * rs, C, look=look, lid=lid, lidtilt=-lt, ir=9, flick=-1, lash=1.6, lowline=False, wing=False))
        out.append(eye(54, 0, 10 * rs, 12 * rs, C, look=look, lid=lid, lidtilt=lt, ir=8.5, sq=.8, flick=1, lash=1.4,
                       lowline=False, wing=False))
    # bags and crow's feet
    out.append(L('M -36 16 C -26 24, -12 24, -4 18', C['line'], LW[0] * .7, 'opacity=".75"'))
    out.append(L('M -44 -4 L -52 -8 M -44 2 L -54 2 M -44 8 L -52 12', C['line'], LW[0] * .6, 'opacity=".6"'))
    # brows: big white bushy blocks
    by = {'grump': (8, -8), 'anger': (14, -14), 'joy': (-6, 4), 'surprise': (-18, 6), 'sad': (-10, 12), 'kind': (-4, 4)}.get(expr, (8, -8))
    inner, outer = by
    nb = (f'M -58 {-30 + outer} C -62 {-40 + outer}, -52 {-52 + outer}, -38 {-50 + outer} C -22 {-52 + outer * .5}, -4 {-44 + inner}, 8 {-30 + inner} '
          f'C 12 {-24 + inner}, 8 {-18 + inner}, 2 {-20 + inner} C -6 {-24 + inner}, -14 {-26 + inner * .5}, -24 {-26 + outer * .5} '
          f'C -36 {-26 + outer}, -46 {-22 + outer}, -58 {-30 + outer} Z')
    fb = (f'M 36 {-28 + inner} C 46 {-42 + inner}, 62 {-50 + outer * .5}, 78 {-46 + outer} C 90 {-44 + outer}, 96 {-36 + outer}, 92 {-28 + outer} '
          f'C 84 {-30 + outer}, 76 {-28 + outer}, 66 {-26 + outer * .5} C 56 {-24 + inner}, 46 {-20 + inner}, 36 {-28 + inner} Z')
    out.append(shaded(nb, C['hair'], f'M -70 {-28 + outer} L 20 {-24 + inner} L 20 0 L -70 0 Z', C['hairS'], C['hairL']))
    out.append(shaded(fb, C['hair'], f'M 30 {-24 + inner} L 100 {-28 + outer} L 100 0 L 30 0 Z', C['hairS'], C['hairL']))
    # nose: a big soft bulb, rosy
    nose = 'M 62 -10 C 70 0, 88 8, 102 26 C 112 40, 108 58, 92 60 C 82 61, 74 56, 68 52 C 60 48, 54 40, 56 28 C 58 14, 62 4, 62 -10 Z'
    out.append(F(nose, C['skin']))
    out.append(clip(nose, F('M 40 0 C 56 30, 70 50, 90 66 L 40 70 Z', C['shade']),
                    f'<ellipse cx="92" cy="38" rx="12" ry="10" fill="{C["blush"]}" opacity=".55"/>',
                    '<ellipse cx="92" cy="22" rx="5" ry="3" fill="#fff" opacity=".6"/>'))
    out.append(L('M 63 -6 C 72 2, 88 8, 102 26 C 112 40, 108 58, 92 60 C 82 61, 74 56, 68 52 C 62 48, 56 42, 56 32',
                 C['line'], LW[0] * .9))
    out.append(L('M 70 50 C 76 44, 80 46, 82 52', C['line'], LW[0] * .8))
    # chin + mouth under the moustache
    mouth = {
        'grump': L('M 18 96 C 30 92, 46 92, 58 98', C['line'], LW[0] * 1.1),
        'kind': L('M 18 94 C 30 100, 46 100, 58 92', C['line'], LW[0] * 1.1),
        'joy': F('M 10 88 C 30 94, 52 94, 70 86 C 64 108, 44 116, 34 114 C 22 112, 12 102, 10 88 Z', '#6e2620', C['line']),
        'surprise': F('M 30 90 C 38 88, 48 88, 52 96 C 54 108, 46 116, 38 114 C 30 112, 26 98, 30 90 Z', '#6e2620', C['line']),
        'sad': L('M 18 102 C 30 94, 46 94, 58 100', C['line'], LW[0] * 1.1),
        'anger': F('M 12 92 C 30 88, 50 88, 66 92 C 60 106, 20 108, 12 92 Z', '#6e2620', C['line']) +
                 clip('M 12 92 C 30 88, 50 88, 66 92 C 60 106, 20 108, 12 92 Z', F('M 0 86 L 80 86 L 80 98 L 0 98 Z', '#fff')),
    }
    out.append(mouth.get(expr, mouth['grump']))
    # moustache: a white walrus shape
    mdroop = {'joy': -8, 'kind': -4, 'surprise': -6}.get(expr, 0)
    mo = (f'M 8 54 C 26 44, 58 46, 76 56 C 96 52, 110 62, 114 {80 + mdroop} C 108 {76 + mdroop}, 100 {76 + mdroop}, 94 {82 + mdroop} '
          f'C 82 {94 + mdroop}, 62 {96 + mdroop}, 46 {88 + mdroop} C 32 {96 + mdroop}, 12 {96 + mdroop}, -2 {86 + mdroop} '
          f'C -12 {90 + mdroop}, -22 {88 + mdroop}, -28 {80 + mdroop} C -16 {78 + mdroop}, -8 66, 8 54 Z')
    out.append(shaded(mo, C['hair'], 'M -40 80 C 0 96, 60 100, 120 84 L 120 120 L -40 120 Z', C['hairS'], C['hairL']))
    out.append(L('M 46 60 C 46 70, 46 78, 46 86', C['hairL'], LW[0] * .7))
    out.append(L('M 20 66 C 16 72, 10 78, 2 82', C['hairL'], LW[0] * .6))
    out.append(L('M 72 66 C 80 72, 90 76, 100 76', C['hairL'], LW[0] * .6))
    return f'<g transform="rotate({tilt} 0 100)">' + ''.join(out) + '</g>'


# ---------------------------------------------------------------- body, three-quarter; hands behind the back
VEST = ('M -130 150 C -150 200, -156 300, -150 380 C -146 450, -126 500, -90 520 L 110 520 '
        'C 150 500, 172 450, 170 380 C 168 290, 140 200, 112 150 C 60 128, -76 128, -130 150 Z')


def body_q():
    out = []
    # legs: short, wide trousers
    tn = 'M -108 500 L -4 500 C -6 600, -12 700, -16 800 L -98 804 C -102 700, -106 600, -108 500 Z'
    tf = 'M 10 500 L 112 500 C 112 600, 106 700, 100 790 L 26 792 C 22 700, 14 600, 10 500 Z'
    out.append(shaded(tf, C['trou'], 'M 66 500 L 130 500 L 130 800 L 74 800 Z', C['trouS'], C['trouL']))
    out.append(shaded(tn, C['trou'], 'M -130 500 L -80 500 L -76 810 L -130 810 Z', C['trouS'], C['trouL']))
    out.append(L('M -54 560 L -58 790', C['trouL'], LW[0] * .7))
    # shoes, round toes pointing right
    for x, y in ((-58, 800), (62, 788)):
        sh = (f'M {x - 46} {y - 4} L {x + 30} {y - 6} C {x + 64} {y - 2}, {x + 84} {y + 14}, {x + 84} {y + 34} '
              f'C {x + 84} {y + 46}, {x + 60} {y + 48}, {x + 30} {y + 48} L {x - 46} {y + 46} C {x - 54} {y + 30}, {x - 54} {y + 8}, {x - 46} {y - 4} Z')
        out.append(F(sh, C['shoe'], C['shoeL']))
        out.append(F(f'M {x + 40} {y + 4} C {x + 60} {y + 6}, {x + 72} {y + 14}, {x + 76} {y + 24} C {x + 64} {y + 18}, {x + 52} {y + 12}, {x + 40} {y + 4} Z', '#6b5045'))
    # far arm (a sliver of sleeve behind the body)
    out.append(shaded('M 112 160 C 146 200, 160 280, 156 360 C 154 390, 140 404, 124 400 C 132 330, 128 250, 104 190 Z',
                      C['shirt'], 'M 130 160 L 170 160 L 170 410 L 140 410 Z', C['shirtS'], C['shirtL']))
    # shirt front, collar, vest
    out.append(F('M -60 130 L 40 130 L 30 300 L -50 300 Z', C['shirt'], C['shirtL']))
    out.append(shaded(VEST, C['vest'], 'M -170 160 C -130 300, -120 430, -60 540 L -170 540 Z M 110 160 C 136 280, 146 420, 130 540 L 190 540 L 190 160 Z',
                      C['vestS'], C['vestL']))
    # vest opening (V) and shirt
    out.append(F('M -50 132 L 34 132 L -4 300 Z', C['shirt'], C['shirtL']))
    out.append(F('M -30 132 C -40 150, -48 166, -60 172 L -48 132 Z', C['shirt'], C['shirtL']))
    # bow tie / collar
    out.append(F('M -46 130 C -30 150, 10 150, 30 128 L 20 120 C 0 136, -30 136, -40 120 Z', C['shirt'], C['shirtL']))
    out.append(F('M -24 142 L -40 132 L -42 156 Z M -8 142 L 8 132 L 10 156 Z', '#a8443a', '#5b1f1a'))
    out.append(F('M -20 138 L -12 138 L -12 150 L -20 150 Z', '#a8443a', '#5b1f1a'))
    out.append(L('M -4 300 L -6 518', C['vestL'], LW[0] * .8))
    for y in (330, 380, 430, 480):
        out.append(f'<circle cx="8" cy="{y}" r="5.5" fill="{C["brass"]}" stroke="{C["brassL"]}" stroke-width="1.6"/>')
    # watch chain into the pocket
    out.append(L('M 8 380 C 34 414, 72 420, 100 404', C['brass'], LW[0] * 1.2))
    out.append(F('M 76 390 L 130 384 L 132 398 L 78 404 Z', C['vestS'], C['vestL'], LW[0] * .8))
    # near arm: sleeve going behind the back, rolled at the elbow
    arm = 'M -132 160 C -172 210, -186 290, -178 370 C -174 400, -152 414, -130 404 C -136 330, -130 250, -112 196 Z'
    out.append(shaded(arm, C['shirt'], 'M -200 200 C -180 300, -170 380, -140 420 L -200 420 Z', C['shirtS'], C['shirtL']))
    out.append(F('M -182 356 C -164 368, -144 370, -128 362 L -128 396 C -144 410, -170 410, -180 394 Z', C['shirtS'], C['shirtL']))
    out.append(L('M -154 220 C -158 260, -158 300, -156 340', C['shirtL'], LW[0] * .6))
    return ''.join(out)


def collar():
    out = [F('M -62 116 C -40 150, 24 154, 50 116 L 58 138 C 34 172, -44 174, -70 140 Z', C['shirt'], C['shirtL'])]
    out.append(F('M -14 150 L -40 136 L -42 166 Z M -2 150 L 24 136 L 26 166 Z', '#a8443a', '#5b1f1a'))
    out.append(F('M -14 144 L -2 144 L -2 158 L -14 158 Z', '#a8443a', '#5b1f1a'))
    return ''.join(out)


def figure_q(expr='grump'):
    # stocky, head a little forward, sunk into the collar
    return body_q() + g(head_q(expr), 14, 26, 1) + collar()


# ---------------------------------------------------------------- front view
FACE_F = ('M -92 -30 C -94 -92, -50 -124, 0 -124 C 50 -124, 94 -92, 92 -30 C 94 10, 92 50, 80 76 '
          'C 64 104, 34 116, 0 116 C -34 116, -64 104, -80 76 C -92 50, -94 10, -92 -30 Z')


def head_f(expr='grump'):
    out = []
    out.append(shaded('M -52 70 L -52 140 L 52 140 L 52 70 Z', C['skin'], 'M -60 60 C -20 110, 20 110, 60 60 L 60 140 L -60 140 Z',
                      C['shade'], C['line']))
    hair = ('M -74 -74 C -98 -66, -112 -40, -114 -10 C -118 24, -110 58, -90 82 C -82 90, -70 94, -60 92 '
            'C -74 78, -82 62, -84 44 L -82 -10 C -84 -30, -82 -50, -68 -70 Z')
    for d in (hair, mx(hair)):
        out.append(shaded(d, C['hair'], 'M -130 20 L 130 20 L 130 100 L -130 100 Z', C['hairS'], C['hairL']))
    for d in ('M -76 -10 C -104 -22, -118 4, -110 30 C -104 46, -90 52, -78 42', ):
        out.append(F(d + ' Z', C['skin'], C['line']))
        out.append(F(mx(d) + ' Z', C['skin'], C['line']))
    out.append(F(FACE_F, C['skin']))
    out.append(clip(FACE_F, F('M -110 -60 C -86 -10, -86 60, -40 120 L -110 130 Z', C['shade'], extra='opacity=".6"'),
                    F('M -30 -122 C 10 -126, 50 -112, 70 -88 C 40 -102, 10 -110, -30 -112 Z', '#f7d3bb'),
                    f'<ellipse cx="-52" cy="36" rx="22" ry="14" fill="{C["blush"]}" opacity=".5"/>',
                    f'<ellipse cx="52" cy="36" rx="22" ry="14" fill="{C["blush"]}" opacity=".5"/>'))
    out.append(L(FACE_F, C['line']))
    for y in (-84, -72):
        out.append(L(f'M -40 {y} C -10 {y - 5}, 10 {y - 5}, 40 {y}', C['line'], LW[0] * .7, 'opacity=".7"'))
    out.append(L('M -92 -60 C -40 -76, 40 -76, 92 -60', '#3a302a', LW[0] * 2.4))
    out.append(F('M 30 -88 C 30 -100, 62 -100, 62 -88 L 62 -60 C 62 -50, 30 -50, 30 -60 Z', '#2e2a28', '#14100e'))
    out.append('<ellipse cx="46" cy="-74" rx="11" ry="11" fill="#5d5650" stroke="#14100e" stroke-width="2"/>')
    lid = {'grump': .42, 'kind': .3}.get(expr, .4)
    out.append(eye(-38, 0, 13, 13, C, look=(0, 1), lid=lid, lidtilt=-4, ir=9, flick=-1, lash=1.6, lowline=False, wing=False))
    out.append(eye(38, 0, 13, 13, C, look=(0, 1), lid=lid, lidtilt=4, ir=9, flick=1, lash=1.6, lowline=False, wing=False))
    nb = ('M -76 -38 C -80 -48, -68 -58, -54 -56 C -38 -56, -18 -46, -6 -32 C -2 -26, -6 -20, -12 -22 '
          'C -20 -26, -30 -28, -42 -28 C -54 -28, -64 -26, -76 -38 Z')
    for d in (nb, mx(nb)):
        out.append(shaded(d, C['hair'], 'M -90 -30 L 90 -30 L 90 0 L -90 0 Z', C['hairS'], C['hairL']))
    nose = 'M -14 -10 C -14 10, -30 20, -30 38 C -30 54, -14 60, 0 60 C 14 60, 30 54, 30 38 C 30 20, 14 10, 14 -10 Z'
    out.append(F(nose, C['skin']))
    out.append(clip(nose, F('M -40 0 C -26 30, -20 50, -10 70 L -40 70 Z', C['shade']),
                    f'<ellipse cx="0" cy="40" rx="18" ry="14" fill="{C["blush"]}" opacity=".5"/>',
                    '<ellipse cx="6" cy="24" rx="6" ry="4" fill="#fff" opacity=".6"/>'))
    out.append(L(nose[:-2], C['line'], LW[0] * .9))
    out.append(L('M -26 96 C -10 92, 10 92, 26 96', C['line'], LW[0] * 1.1))
    mo = ('M 0 56 C 20 46, 50 50, 66 62 C 82 64, 94 74, 96 90 C 88 86, 80 86, 74 90 C 60 100, 36 100, 20 92 '
          'C 12 96, 4 96, 0 92 C -4 96, -12 96, -20 92 C -36 100, -60 100, -74 90 C -80 86, -88 86, -96 90 '
          'C -94 74, -82 64, -66 62 C -50 50, -20 46, 0 56 Z')
    out.append(shaded(mo, C['hair'], 'M -100 84 C -40 100, 40 100, 100 84 L 100 120 L -100 120 Z', C['hairS'], C['hairL']))
    out.append(L('M 0 62 L 0 90', C['hairL'], LW[0] * .7))
    out.append(L('M -30 68 C -44 76, -60 80, -76 82 M 30 68 C 44 76, 60 80, 76 82', C['hairL'], LW[0] * .6))
    return ''.join(out)


VEST_F = ('M -134 150 C -156 200, -164 300, -158 380 C -154 450, -134 500, -100 520 L 100 520 '
          'C 134 500, 154 450, 158 380 C 164 300, 156 200, 134 150 C 70 130, -70 130, -134 150 Z')


def body_f():
    out = []
    tn = 'M -100 500 L -6 500 C -8 600, -12 700, -14 800 L -92 804 C -96 700, -100 600, -100 500 Z'
    for d, sh in ((tn, 'M -120 500 L -70 500 L -66 810 L -120 810 Z'), (mx(tn), 'M 50 500 L 120 500 L 120 810 L 60 810 Z')):
        out.append(shaded(d, C['trou'], sh, C['trouS'], C['trouL']))
    for x in (-54, 54):
        sh = (f'M {x - 40} 796 L {x + 40} 796 C {x + 52} 810, {x + 54} 834, {x + 46} 846 L {x - 46} 846 '
              f'C {x - 54} 834, {x - 52} 810, {x - 40} 796 Z')
        out.append(F(sh, C['shoe'], C['shoeL']))
    arm = 'M -130 158 C -172 210, -186 290, -178 370 C -174 400, -152 414, -130 404 C -136 330, -132 250, -116 196 Z'
    for d in (arm, mx(arm)):
        out.append(shaded(d, C['shirt'], 'M -200 200 C -180 300, -170 380, -140 420 L -200 420 Z M 150 200 L 200 200 L 200 420 L 150 420 Z',
                          C['shirtS'], C['shirtL']))
    out.append(F('M -182 356 C -164 368, -144 370, -128 362 L -128 396 C -144 410, -170 410, -180 394 Z', C['shirtS'], C['shirtL']))
    out.append(F(mx('M -182 356 C -164 368, -144 370, -128 362 L -128 396 C -144 410, -170 410, -180 394 Z'), C['shirtS'], C['shirtL']))
    out.append(shaded(VEST_F, C['vest'], 'M -170 160 C -130 300, -126 430, -70 540 L -170 540 Z', C['vestS'], C['vestL']))
    out.append(F('M -44 132 L 44 132 L 0 300 Z', C['shirt'], C['shirtL']))
    out.append(L('M 0 300 L 0 518', C['vestL'], LW[0] * .8))
    for y in (330, 380, 430, 480):
        out.append(f'<circle cx="0" cy="{y}" r="5.5" fill="{C["brass"]}" stroke="{C["brassL"]}" stroke-width="1.6"/>')
    out.append(L('M 0 380 C 30 414, 70 418, 100 400', C['brass'], LW[0] * 1.2))
    out.append(F('M 76 390 L 124 386 L 124 400 L 76 404 Z', C['vestS'], C['vestL'], LW[0] * .8))
    return ''.join(out)


def collar_f():
    out = [F('M -56 116 C -40 150, 40 150, 56 116 L 62 138 C 40 172, -40 172, -62 138 Z', C['shirt'], C['shirtL'])]
    out.append(F('M -6 150 L -32 136 L -34 166 Z M 6 150 L 32 136 L 34 166 Z', '#a8443a', '#5b1f1a'))
    out.append(F('M -7 144 L 7 144 L 7 158 L -7 158 Z', '#a8443a', '#5b1f1a'))
    return ''.join(out)


def figure_f(expr='grump'):
    return body_f() + g(head_f(expr), 0, 26, 1) + collar_f()


# ---------------------------------------------------------------- side view (facing right)
FACE_S = ('M -96 -30 C -100 -96, -46 -126, 6 -124 C 52 -122, 74 -90, 74 -50 C 74 -30, 70 -18, 74 -6 '
          'C 76 6, 80 30, 80 50 C 80 80, 74 100, 56 112 C 30 124, -10 120, -40 104 C -80 84, -94 30, -96 -30 Z')


def head_s(expr='grump'):
    out = []
    out.append(shaded('M -46 70 L -36 140 L 30 140 L 30 90 Z', C['skin'], 'M -70 60 L 50 100 L 50 140 L -70 140 Z',
                      C['shade'], C['line']))
    out.append(F(FACE_S, C['skin']))
    out.append(clip(FACE_S, F('M -110 -40 C -90 20, -60 80, 0 130 L -120 130 Z', C['shade'], extra='opacity=".5"'),
                    F('M -40 -124 C 0 -128, 40 -116, 60 -92 C 30 -104, 0 -112, -40 -112 Z', '#f7d3bb'),
                    f'<ellipse cx="34" cy="36" rx="22" ry="14" fill="{C["blush"]}" opacity=".5"/>'))
    out.append(L(FACE_S, C['line']))
    hair = ('M -88 -62 C -102 -44, -108 -20, -106 4 C -106 36, -98 64, -80 84 C -70 96, -54 102, -40 100 '
            'C -56 84, -62 66, -62 44 C -44 40, -32 20, -36 0 C -40 -16, -52 -26, -58 -34 C -66 -44, -78 -52, -88 -62 Z')
    out.append(shaded(hair, C['hair'], 'M -120 30 C -100 60, -80 90, -40 110 L -120 110 Z', C['hairS'], C['hairL']))
    out.append(F('M -30 -10 C -54 -22, -68 4, -60 28 C -54 44, -38 48, -26 38 Z', C['skin'], C['line']))
    out.append(L('M -44 0 C -52 8, -50 22, -42 28', C['line'], LW[0] * .8))
    for y in (-84, -72):
        out.append(L(f'M -10 {y} C 20 {y - 4}, 40 {y - 2}, 60 {y + 4}', C['line'], LW[0] * .7, 'opacity=".7"'))
    out.append(L('M -100 -50 C -40 -70, 30 -76, 76 -64', '#3a302a', LW[0] * 2.4))
    out.append(F('M 56 -82 L 96 -84 L 98 -56 L 58 -54 Z', '#2e2a28', '#14100e'))
    out.append(F('M 92 -86 C 102 -86, 106 -54, 98 -54 Z', '#5d5650', '#14100e'))
    out.append(eye(52, 0, 7, 12, C, look=(3, 1), lid=.42, lidtilt=-2, ir=8, sq=.6, flick=-1, lash=1.6, lowline=False, wing=False))
    out.append(shaded('M 26 -30 C 30 -44, 50 -52, 72 -46 C 86 -42, 90 -32, 84 -24 C 72 -28, 60 -28, 50 -24 C 40 -22, 30 -22, 26 -30 Z',
                      C['hair'], 'M 20 -26 L 100 -26 L 100 0 L 20 0 Z', C['hairS'], C['hairL']))
    nose = 'M 70 -8 C 80 0, 98 8, 112 26 C 122 40, 118 58, 102 60 C 92 61, 84 56, 78 52 C 72 46, 70 30, 70 -8 Z'
    out.append(F(nose, C['skin']) + clip(nose, f'<ellipse cx="102" cy="38" rx="12" ry="10" fill="{C["blush"]}" opacity=".55"/>',
                                         '<ellipse cx="102" cy="22" rx="5" ry="3" fill="#fff" opacity=".6"/>') + L(nose, C['line'], LW[0] * .9))
    out.append(L('M 56 96 C 64 94, 72 94, 78 98', C['line'], LW[0] * 1.1))
    mo = 'M 44 54 C 62 46, 84 50, 96 58 C 108 64, 114 76, 112 90 C 104 84, 96 84, 90 88 C 76 96, 60 94, 46 86 C 36 82, 34 66, 44 54 Z'
    out.append(shaded(mo, C['hair'], 'M 30 80 C 60 96, 90 96, 120 84 L 120 120 L 30 120 Z', C['hairS'], C['hairL']))
    out.append(L('M 60 62 C 72 70, 86 76, 100 78', C['hairL'], LW[0] * .6))
    return ''.join(out)


def body_s():
    out = []
    for x, dx in ((14, 0), (-14, 0)):
        d = f'M {x - 50} 500 L {x + 46} 500 C {x + 44} 600, {x + 40} 700, {x + 36} 800 L {x - 40} 804 C {x - 44} 700, {x - 48} 600, {x - 50} 500 Z'
        out.append(shaded(d, C['trou'], f'M {x - 60} 500 L {x - 20} 500 L {x - 16} 810 L {x - 60} 810 Z', C['trouS'], C['trouL']))
        out.append(F(f'M {x - 44} 796 L {x + 30} 794 C {x + 64} 798, {x + 84} 814, {x + 84} 834 C {x + 84} 846, {x + 60} 848, {x + 30} 848 '
                     f'L {x - 44} 846 C {x - 52} 830, {x - 52} 808, {x - 44} 796 Z', C['shoe'], C['shoeL']))
    vest = ('M -70 150 C -100 200, -108 300, -104 380 C -102 450, -90 500, -64 520 L 90 520 C 140 500, 160 440, 156 370 '
            'C 152 300, 120 240, 80 190 C 60 160, 20 140, -20 136 C -40 138, -60 142, -70 150 Z')
    out.append(shaded(vest, C['vest'], 'M -120 160 C -90 300, -86 430, -50 540 L -120 540 Z', C['vestS'], C['vestL']))
    out.append(F('M 40 150 C 60 170, 70 190, 80 200 L 60 210 C 50 190, 40 170, 30 156 Z', C['shirt'], C['shirtL']))
    for y in (330, 380, 430, 480):
        out.append(f'<circle cx="{150 - abs(y - 400) * .15}" cy="{y}" r="5" fill="{C["brass"]}" stroke="{C["brassL"]}" stroke-width="1.6"/>')
    arm = 'M -40 160 C -80 200, -100 280, -96 350 C -94 380, -80 400, -60 400 C -50 360, -40 300, -10 220 Z'
    out.append(shaded(arm, C['shirt'], 'M -110 200 C -100 300, -96 360, -80 410 L -110 410 Z', C['shirtS'], C['shirtL']))
    out.append(F('M -100 340 C -84 352, -66 354, -54 346 L -58 384 C -72 396, -90 396, -98 380 Z', C['shirtS'], C['shirtL']))
    # hands clasped behind the back
    out.append(F('M -100 386 C -122 390, -134 410, -126 430 C -118 446, -98 446, -88 432 C -82 420, -86 400, -100 386 Z', C['skin'], C['line']))
    return ''.join(out)


def collar_s():
    return F('M -24 120 C -10 150, 40 156, 66 130 L 70 150 C 44 178, -10 176, -34 140 Z', C['shirt'], C['shirtL']) + \
        F('M 56 140 L 76 128 L 80 156 Z', '#a8443a', '#5b1f1a')


def figure_s(expr='grump'):
    return body_s() + g(head_s(expr), 20, 26, 1) + collar_s()
