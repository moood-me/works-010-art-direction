"""Кира, about 15: prickly, closed, defiant; vulnerable underneath. Shape: a thin bent hook — a slouch, all elbows and
knees; choppy dark hair with a fringe over one eye, an oversized plum hoodie, headphones round the neck, heavy boots.
She never smiles openly: her "joy" is a crooked half-smirk."""
from lib import F, L, clip, shaded, g, LW, mx
from face import eye, brow, closed_eye, shout

C = dict(skin='#f1d3c0', shade='#dcab97', line='#9a6052', blush='#e79a8c', white='#fbf7f2',
         iris='#5b6a80', pupil='#15171d', lash='#17121a',
         hair='#2b2231', hairS='#1c1621', hairH='#51415e', hairL='#0f0b12', lip='#b9666a',
         hood='#4d3150', hoodS='#3a233d', hoodH='#64446c', hoodL='#1e1021',
         trou='#3a3940', trouS='#2a292f', trouL='#111014',
         boot='#28262c', bootL='#0c0b0e', sole='#5c5962',
         lime='#d9ef3c', limeS='#b4cb24', limeL='#66780f', cord='#cfc6d2')

HX, HY, TILT = 26, 14, 10  # the head in the figure: pushed forward and down

# ---------------------------------------------------------------- head, three-quarter (facing right)
FACE_Q = ('M -84 -40 C -88 6, -82 46, -60 76 C -38 102, -2 116, 30 114 C 46 112, 56 104, 64 90 '
          'C 72 74, 80 56, 84 36 C 86 20, 85 8, 85 -2 C 85 -12, 89 -22, 89 -34 C 91 -78, 54 -124, 0 -126 '
          'C -54 -126, -84 -90, -84 -40 Z')
BACK_Q = ('M 0 -138 C -30 -139, -58 -130, -80 -110 L -100 -112 L -96 -92 C -106 -74, -112 -52, -112 -30 L -130 -20 L -112 -4 '
          'C -112 20, -110 42, -104 62 L -124 86 L -96 78 L -100 108 '
          'L -74 88 L -68 116 L -50 90 L -36 104 L -20 86 C 20 92, 56 80, 76 56 C 98 28, 104 -20, 100 -60 '
          'C 92 -110, 54 -138, 0 -138 Z')
NEAR_Q = ('M -30 -132 C -78 -126, -108 -90, -108 -40 C -108 0, -104 30, -100 54 L -112 80 L -88 66 L -86 96 '
          'L -68 68 L -58 84 C -58 50, -64 16, -62 -14 C -60 -40, -52 -58, -40 -72 Z')
FRINGE_Q = ('M -36 -132 C 22 -142, 82 -114, 98 -62 C 104 -38, 104 -6, 100 18 L 96 44 L 88 -2 L 76 12 L 66 -6 '
            'L 52 8 L 42 -10 L 30 6 C 24 -14, 10 -36, -12 -54 C -24 -64, -34 -70, -46 -72 C -48 -92, -44 -112, -36 -132 Z')
NOSE_Q = 'M 74 2 C 80 18, 92 30, 96 40 C 98 46, 92 50, 84 50 C 80 50, 76 48, 72 49 C 70 40, 72 24, 74 2 Z'


def hair_back_q():
    return (shaded(BACK_Q, C['hairS'], 'M 0 0', C['hairS'], C['hairL'])
            + L('M -96 20 C -96 44, -92 64, -86 80 M -72 40 C -70 60, -66 76, -60 88', C['hairH'], LW[0] * .6))


def _mouth(expr):
    if expr == 'smirk':  # one corner goes up, the other stays put
        return (L('M 24 84 C 38 88, 54 84, 68 70', C['line'], LW[0] * 1.2)
                + L('M 66 66 C 70 68, 72 72, 71 76', C['line'], LW[0] * .8)
                + F('M 34 92 C 42 96, 52 95, 58 90 C 50 92, 42 93, 34 92 Z', C['lip'], C['lip'], LW[0] * .8))
    if expr == 'surprise':
        d = 'M 38 80 C 46 76, 56 78, 58 88 C 58 100, 50 104, 44 102 C 36 98, 34 86, 38 80 Z'
        return F(d, '#6e2630', C['line'])
    if expr == 'sad':  # pressed, the lower lip pushed up
        return (L('M 26 90 C 36 82, 54 82, 64 88', C['line'], LW[0] * 1.2)
                + F('M 34 94 C 42 99, 52 99, 58 94 C 52 92, 42 92, 34 94 Z', C['lip'], C['lip'], LW[0] * .8)
                + L('M 38 106 C 44 103, 52 103, 56 105', C['line'], LW[0] * .6, 'opacity=".6"'))
    if expr == 'anger':
        return shout(24, 70, 74, 26, C['line'], tilt=3)
    # pressed shut, a little crooked
    return (L('M 26 84 C 38 82, 52 82, 66 78', C['line'], LW[0] * 1.2)
            + L('M 24 81 C 25 83, 26 85, 28 86', C['line'], LW[0] * .8)
            + F('M 34 90 C 42 95, 52 94, 58 89 C 50 90, 42 91, 34 90 Z', C['lip'], C['lip'], LW[0] * .8))


def face_q(expr):
    out = [shaded('M -30 80 C -28 120, -32 146, -38 176 L 22 176 C 16 150, 16 128, 20 104 Z', C['skin'],
                  'M -60 62 C -20 110, 20 120, 50 104 L 50 138 C 10 148, -30 134, -60 116 Z', C['shade'], C['line'])]
    out.append(F(FACE_Q, C['skin']))
    out.append(clip(FACE_Q,
                    F('M -100 -60 C -80 -30, -84 40, -40 100 L -110 130 Z', C['shade'], extra='opacity=".55"'),
                    g(F(NEAR_Q, C['shade']) + F(FRINGE_Q, C['shade']), 5, 9),
                    f'<ellipse cx="-34" cy="46" rx="22" ry="11" fill="{C["blush"]}" opacity=".38"/>'))
    out.append(L(FACE_Q, C['line']))
    # eyes: smaller than Аня's, heavy flat lids, a thick dark lash line; the far one looks out from under the fringe
    look = {'sulk': (8, 0), 'smirk': (7, 0), 'surprise': (3, 0), 'sad': (1, 5), 'anger': (6, 1)}.get(expr, (8, 0))
    lid = {'sulk': .4, 'smirk': .34, 'surprise': .02, 'sad': .44, 'anger': .36}.get(expr, .4)
    lt = {'sulk': 3, 'anger': 7, 'sad': -5}.get(expr, 0)
    low = {'smirk': .2}.get(expr, 0)
    rs = 1.14 if expr == 'surprise' else 1
    ir = 11.5 if expr == 'surprise' else 14
    out.append(eye(-18, 0, 23 * rs, 23 * rs, C, look=look, lid=lid, lidtilt=-lt, lower=low, ir=ir, flick=-1, lash=2.6))
    out.append(eye(54, 0, 15 * rs, 22 * rs, C, look=(look[0] * .8, look[1]), lid=lid, lidtilt=lt, lower=low, ir=ir * .95,
                   sq=.78, flick=1, lash=2.4, wing=False))
    out.append(L('M -36 25 C -28 30, -14 30, -4 25', C['line'], LW[0] * .6, 'opacity=".45"'))
    # brows: straight and low
    bb = {'sulk': (4, -22, -46, -32, 1), 'smirk': (4, -34, -46, -38, 7), 'surprise': (4, -46, -46, -50, 8),
          'sad': (4, -40, -46, -26, 0), 'anger': (6, -12, -48, -36, -1)}.get(expr)
    out.append(brow(bb[0], bb[1], bb[2], bb[3], bb[4], 7.5, C['hairL']))
    fb = {'sulk': (38, -20, 74, -30), 'smirk': (38, -22, 74, -28), 'surprise': (38, -42, 74, -44),
          'sad': (38, -36, 72, -24), 'anger': (36, -10, 74, -32)}.get(expr)
    out.append(brow(fb[0], fb[1], fb[2], fb[3], 1, 6.5, C['hairL']))
    # nose: a small sharp wedge
    out.append(F(NOSE_Q, C['skin']))
    out.append(clip(NOSE_Q, F('M 60 0 C 72 20, 76 38, 78 54 L 60 60 Z', C['shade'])))
    out.append(L('M 75 4 C 80 18, 92 30, 96 40 C 98 46, 92 50, 84 50 C 80 50, 77 49, 73 49', C['line'], LW[0] * .9))
    out.append(g(_mouth(expr), -5, -7))
    return ''.join(out)


def hair_front_q():
    out = [F(NEAR_Q, C['hair']), clip(NEAR_Q, F('M -130 20 C -100 40, -90 70, -80 100 L -130 100 Z', C['hairS'])),
           L(NEAR_Q, C['hairL'])]
    out += [F(FRINGE_Q, C['hair']),
            clip(FRINGE_Q, F('M -20 -128 C 20 -132, 60 -116, 82 -88 C 56 -104, 24 -112, -14 -112 Z', C['hairH'])),
            L(FRINGE_Q, C['hairL'])]
    for d in ('M -30 -110 C 10 -100, 44 -70, 58 -20', 'M 10 -118 C 46 -104, 74 -70, 84 -20', 'M -60 -100 C -84 -70, -90 -30, -84 20'):
        out.append(L(d, C['hairH'], LW[0] * .7))
    return ''.join(out)


def head_q(expr='sulk', tilt=TILT, back=True, front=True):
    return f'<g transform="rotate({tilt} 0 100)">' + (hair_back_q() if back else '') + \
        (face_q(expr) + hair_front_q() if front else '') + '</g>'


# ---------------------------------------------------------------- shared body parts
def boot(x, y, k=1.0):
    """A heavy laced boot pointing right; (x, y) is the ankle."""
    p = lambda a, b: f'{x + a * k:.1f} {y + b * k:.1f}'
    up = (f'M {p(-34, -84)} L {p(32, -88)} C {p(34, -50)}, {p(36, -30)}, {p(40, -14)} C {p(74, -10)}, {p(104, 6)}, {p(108, 40)} '
          f'L {p(-40, 44)} C {p(-44, 0)}, {p(-42, -40)}, {p(-34, -84)} Z')
    sole = f'M {p(-44, 38)} L {p(112, 34)} L {p(114, 62)} L {p(30, 64)} L {p(28, 56)} L {p(-10, 57)} L {p(-12, 66)} L {p(-44, 66)} Z'
    out = [shaded(up, C['boot'], f'M {p(-50, -90)} L {p(-14, -90)} L {p(-10, 50)} L {p(-50, 50)} Z', C['trouL'], C['bootL'])]
    out.append(F(f'M {p(60, 2)} C {p(78, 6)}, {p(92, 16)}, {p(98, 30)} C {p(84, 22)}, {p(72, 14)}, {p(60, 2)} Z', C['sole']))
    out.append(F(sole, C['sole'], C['bootL']))
    out.append(L(f'M {p(6, -70)} L {p(32, -62)} M {p(8, -52)} L {p(34, -44)} M {p(10, -34)} L {p(36, -26)} M {p(14, -16)} L {p(44, -8)}',
                 C['lime'], LW[0] * 1.5))
    return ''.join(out)


def cup(x, y, rx, ry):
    """A headphone cup: the acid accent."""
    return (f'<ellipse cx="{x}" cy="{y}" rx="{rx + 6}" ry="{ry + 6}" fill="{C["boot"]}" stroke="{C["bootL"]}" stroke-width="{LW[0]}"/>'
            f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{C["lime"]}" stroke="{C["limeL"]}" stroke-width="{LW[0]}"/>'
            f'<ellipse cx="{x + rx * .2}" cy="{y + ry * .2}" rx="{rx * .5}" ry="{ry * .5}" fill="{C["limeS"]}"/>')


# ---------------------------------------------------------------- body, three-quarter: a slouch, one hand in the pocket
HOODIE_Q = ('M -100 178 C -146 192, -170 252, -166 332 C -164 440, -150 540, -138 640 C -60 664, 60 664, 138 636 '
            'C 140 520, 132 400, 118 300 C 112 240, 100 198, 70 178 C 30 162, -54 162, -100 178 Z')


def near_arm():
    """The near arm hangs by its own weight: a long sleeve down to the knuckles, the fingers peep out."""
    a = []
    a.append(F('M -164 640 C -166 672, -160 700, -146 704 C -138 706, -134 698, -134 690 C -130 700, -122 702, -118 694 '
                 'C -114 700, -106 696, -106 686 C -104 672, -104 656, -106 640 Z', C['skin'], C['line']))
    a.append(L('M -134 690 L -134 668 M -118 694 L -119 670', C['line'], LW[0] * .7))
    arm = ('M -112 184 C -152 200, -176 262, -180 342 C -184 440, -182 540, -174 646 C -154 662, -120 662, -100 648 '
           'C -100 540, -100 440, -98 342 C -96 282, -92 232, -84 202 Z')
    a.append(shaded(arm, C['hood'], 'M -200 200 C -170 340, -166 500, -160 670 L -200 670 Z', C['hoodS'], C['hoodL']))
    a.append(F('M -176 618 C -154 632, -122 632, -100 620 L -100 648 C -120 662, -154 662, -174 646 Z', C['hoodS'], C['hoodL']))
    a.append(L('M -150 300 C -140 330, -136 360, -138 400 M -110 420 C -122 450, -126 480, -124 520', C['hoodL'], LW[0] * .6))
    return f'<g transform="rotate(5 -130 200)">' + ''.join(a) + '</g>'


def body_q():
    out = []
    # the far arm: only the elbow shows, the hand is in the pocket
    far = 'M 84 186 C 126 206, 152 268, 162 350 C 168 404, 156 446, 128 480 L 96 470 C 106 420, 104 300, 84 220 Z'
    out.append(shaded(far, C['hood'], 'M 120 200 L 180 200 L 180 490 L 130 490 Z', C['hoodS'], C['hoodL']))
    # thin legs, the knees a little bent; heavy boots
    nl = ('M -96 620 L -18 620 C -14 740, -22 860, -38 960 C -60 1060, -78 1180, -84 1290 L -134 1290 '
          'C -134 1180, -122 1060, -100 960 C -90 860, -98 740, -96 620 Z')
    fl = ('M 8 620 L 92 620 C 104 740, 108 850, 100 950 C 82 1060, 60 1170, 50 1276 L 2 1276 '
          'C 6 1170, 22 1060, 42 950 C 46 850, 20 740, 8 620 Z')
    out.append(shaded(fl, C['trou'], 'M 66 620 L 110 620 L 112 960 L 60 1290 L 26 1290 L 76 950 Z', C['trouS'], C['trouL']))
    out.append(shaded(nl, C['trou'], 'M -110 620 L -74 620 L -80 960 L -116 1300 L -150 1300 L -112 960 Z', C['trouS'], C['trouL']))
    out.append(L('M -44 950 C -54 956, -66 958, -78 956 M 94 942 C 84 948, 72 950, 60 948', C['trouL'], LW[0] * .7))
    out.append(boot(26, 1270) + boot(-108, 1284))
    low = ''.join(out[1:])
    out = [out[0]]
    # the hoodie: big and boxy, the back rounded
    out.append(shaded(HOODIE_Q, C['hood'],
                      'M -180 180 C -140 320, -132 480, -112 660 L -180 660 Z M 96 180 C 110 320, 118 480, 112 660 L 150 660 L 150 180 Z',
                      C['hoodS'], C['hoodL']))
    out.append(F('M -138 606 C -60 630, 60 630, 138 602 L 138 636 C 60 664, -60 664, -138 640 Z', C['hoodS'], C['hoodL']))
    # the pocket, the far hand pushed into it
    out.append(F('M -30 452 C 20 456, 70 452, 110 444 C 124 490, 130 540, 132 584 C 70 600, -10 602, -66 592 C -64 540, -52 490, -30 452 Z',
                 C['hood'], C['hoodL']))
    out.append(L('M 112 450 C 96 470, 84 500, 80 540', C['hoodL'], LW[0] * .7))
    out.append(L('M 60 500 C 76 506, 92 506, 106 500', C['hoodL'], LW[0] * .6))
    # folds
    out.append(L('M -60 300 C -40 340, -30 380, -28 430 M 96 280 C 84 320, 80 360, 82 410', C['hoodL'], LW[0] * .6))
    out.append(near_arm())
    # the hood lying on the back and shoulders
    hood = ('M -112 186 C -150 160, -150 112, -110 96 C -60 80, 20 92, 60 120 C 92 130, 110 160, 96 186 '
            'C 60 204, 20 222, 4 250 C -20 222, -70 204, -112 186 Z')
    out.append(shaded(hood, C['hood'], 'M -160 100 C -120 130, -100 170, -60 210 L -160 210 Z', C['hoodS'], C['hoodL']))
    return low, ''.join(out)


def band():
    return L('M -62 150 C -40 196, 40 204, 76 150', C['boot'], LW[0] * 4)


def phones():
    out = [cup(-64, 176, 22, 30) + cup(80, 172, 15, 28)]
    # drawstrings
    out.append(L('M -14 236 C -16 270, -12 300, -18 330 M 22 234 C 26 262, 22 290, 28 316', C['cord'], LW[0] * 1.3))
    return ''.join(out)


LEAN = 'rotate(-6 0 640)'  # the slouch: the hips forward, the back rounded behind them, the head pushed out


def figure_q(expr='sulk'):
    low, up = body_q()
    return (low + f'<g transform="{LEAN}">' + up + '</g>' + g(head_q(expr, back=True, front=False), HX, HY)
            + f'<g transform="{LEAN}">' + band() + '</g>' + g(head_q(expr, back=False), HX, HY) + f'<g transform="{LEAN}">' + phones() + '</g>')


# ---------------------------------------------------------------- front view
FACE_F = ('M -86 -40 C -90 10, -84 50, -60 82 C -40 104, -18 114, 0 114 C 18 114, 40 104, 60 82 '
          'C 84 50, 90 10, 86 -40 C 84 -92, 50 -126, 0 -126 C -50 -126, -84 -92, -86 -40 Z')
BACK_F = ('M 0 -138 C -30 -139, -60 -130, -82 -110 L -102 -112 L -98 -92 C -108 -74, -112 -52, -112 -30 L -130 -20 L -112 -4 '
          'C -112 20, -110 42, -106 62 L -124 86 L -98 80 L -100 108 L -78 90 L -70 112 L -54 92 L 54 92 L 70 112 L 78 90 '
          'L 100 108 L 98 80 L 124 86 L 106 62 C 110 40, 112 10, 110 -40 C 108 -100, 60 -138, 0 -138 Z')
NEAR_F = ('M -36 -132 C -80 -126, -110 -92, -110 -40 C -110 0, -108 30, -104 56 L -116 80 L -94 68 L -92 96 '
          'L -76 70 L -70 84 C -72 50, -76 16, -74 -14 C -72 -40, -62 -60, -48 -72 Z')
FRINGE_F = ('M -40 -132 C 20 -142, 88 -116, 106 -62 C 112 -36, 112 0, 108 30 L 102 70 L 92 12 L 80 24 L 68 0 '
            'L 54 14 L 42 -6 L 28 8 L 16 -14 C 6 -32, -14 -50, -32 -62 C -40 -68, -48 -72, -56 -72 C -54 -92, -48 -114, -40 -132 Z')


def head_f(expr='sulk', tilt=4):
    out = [shaded(BACK_F, C['hairS'], 'M 0 0', C['hairS'], C['hairL'])]
    out.append(shaded('M -30 80 L -32 176 L 32 176 L 30 80 Z', C['skin'], 'M -60 60 C -20 124, 20 124, 60 60 L 60 140 C 20 152, -20 152, -60 140 Z',
                      C['shade'], C['line']))
    out.append(F(FACE_F, C['skin']))
    out.append(clip(FACE_F, F('M -100 -60 C -84 -30, -86 40, -50 100 L -110 130 Z', C['shade'], extra='opacity=".55"'),
                    g(F(NEAR_F, C['shade']) + F(FRINGE_F, C['shade']), 4, 9),
                    f'<ellipse cx="-50" cy="46" rx="20" ry="11" fill="{C["blush"]}" opacity=".38"/>'))
    out.append(L(FACE_F, C['line']))
    out.append(eye(-38, 0, 22, 23, C, look=(5, 0), lid=.4, lidtilt=-3, ir=14, flick=-1, lash=2.6))
    out.append(eye(38, 0, 22, 23, C, look=(5, 0), lid=.4, lidtilt=3, ir=14, flick=1, lash=2.6))
    out.append(L('M -54 25 C -46 30, -32 30, -24 25', C['line'], LW[0] * .6, 'opacity=".45"'))
    out.append(brow(-14, -22, -62, -32, 1, 7.5, C['hairL']))
    out.append(brow(14, -22, 62, -32, 1, 7.5, C['hairL']))
    out.append(F('M -2 6 C -8 26, -12 38, -12 44 C -6 50, 6 50, 10 44 Z', C['shade'], extra='opacity=".45"'))
    out.append(L('M -10 42 C -6 50, 6 50, 11 42', C['line'], LW[0] * .9))
    out.append(L('M -22 78 C -8 76, 8 76, 24 72', C['line'], LW[0] * 1.2) + L('M -24 75 C -23 77, -22 79, -20 80', C['line'], LW[0] * .8)
               + F('M -12 84 C -4 89, 6 88, 12 83 C 4 84, -4 85, -12 84 Z', C['lip'], C['lip'], LW[0] * .8))
    out += [F(NEAR_F, C['hair']), clip(NEAR_F, F('M -130 20 C -100 40, -90 70, -80 100 L -130 100 Z', C['hairS'])), L(NEAR_F, C['hairL'])]
    out += [F(FRINGE_F, C['hair']),
            clip(FRINGE_F, F('M -20 -128 C 20 -132, 62 -116, 86 -88 C 58 -104, 24 -112, -14 -112 Z', C['hairH'])), L(FRINGE_F, C['hairL'])]
    for d in ('M -30 -110 C 10 -100, 44 -70, 58 -20', 'M 10 -118 C 48 -104, 78 -70, 90 -20', 'M -62 -100 C -86 -70, -92 -30, -86 20'):
        out.append(L(d, C['hairH'], LW[0] * .7))
    return f'<g transform="rotate({tilt} 0 100)">' + ''.join(out) + '</g>'


def boot_f(x, y):
    up = (f'M {x - 34} {y - 86} L {x + 34} {y - 86} L {x + 38} {y - 6} C {x + 50} {y + 14}, {x + 50} {y + 40}, {x + 44} {y + 44} '
          f'L {x - 44} {y + 44} C {x - 50} {y + 40}, {x - 50} {y + 14}, {x - 38} {y - 6} Z')
    out = [shaded(up, C['boot'], f'M {x - 60} {y - 90} L {x - 20} {y - 90} L {x - 24} {y + 50} L {x - 60} {y + 50} Z', C['trouL'], C['bootL'])]
    out.append(F(f'M {x - 48} {y + 38} L {x + 48} {y + 38} L {x + 50} {y + 64} L {x - 50} {y + 64} Z', C['sole'], C['bootL']))
    out.append(L(f'M {x - 14} {y - 66} L {x + 14} {y - 66} M {x - 14} {y - 48} L {x + 14} {y - 48} M {x - 15} {y - 30} L {x + 15} {y - 30} M {x - 16} {y - 12} L {x + 16} {y - 12}',
                 C['lime'], LW[0] * 1.5))
    return ''.join(out)


HOODIE_F = ('M -104 178 C -140 196, -150 260, -150 332 C -150 440, -146 540, -140 640 C -60 660, 60 660, 140 640 '
            'C 146 540, 150 440, 150 332 C 150 260, 140 196, 104 178 C 50 162, -50 162, -104 178 Z')


def body_f():
    out = []
    nl = ('M -96 620 L -8 620 C -8 740, -20 860, -30 960 C -38 1060, -40 1180, -40 1290 L -90 1290 '
          'C -92 1180, -96 1060, -92 960 C -90 860, -96 740, -96 620 Z')
    for d, sh in ((nl, 'M -110 620 L -70 620 L -66 1300 L -110 1300 Z'), (mx(nl), 'M 56 620 L 110 620 L 110 1300 L 66 1300 Z')):
        out.append(shaded(d, C['trou'], sh, C['trouS'], C['trouL']))
    out.append(L('M -34 950 C -46 956, -60 956, -74 952 M 34 950 C 46 956, 60 956, 74 952', C['trouL'], LW[0] * .7))
    out.append(boot_f(-66, 1284) + boot_f(66, 1284))
    out.append(shaded(HOODIE_F, C['hood'], 'M -180 180 C -140 320, -132 480, -116 660 L -180 660 Z', C['hoodS'], C['hoodL']))
    out.append(F('M -140 606 C -60 628, 60 628, 140 606 L 140 640 C 60 660, -60 660, -140 640 Z', C['hoodS'], C['hoodL']))
    out.append(F('M -74 452 C -30 458, 30 458, 74 452 C 90 490, 100 540, 104 588 C 40 602, -40 602, -104 588 C -100 540, -90 490, -74 452 Z',
                 C['hood'], C['hoodL']))
    out.append(L('M 74 456 C 60 476, 52 506, 50 546 M -74 456 C -60 476, -52 506, -50 546', C['hoodL'], LW[0] * .7))
    out.append(L('M -60 300 C -44 340, -38 380, -38 430 M 60 300 C 44 340, 38 380, 38 430', C['hoodL'], LW[0] * .6))
    # her left hand in the pocket, the elbow out
    arm = ('M 112 184 C 152 200, 178 262, 182 342 C 184 400, 176 440, 160 470 C 130 504, 100 522, 72 532 L 58 492 '
           'C 84 480, 100 460, 104 430 C 102 340, 96 250, 84 202 Z')
    out.append(shaded(arm, C['hood'], 'M 140 200 L 200 200 L 200 540 L 150 480 Z', C['hoodS'], C['hoodL']))
    out.append(L('M 150 300 C 142 330, 140 360, 144 400', C['hoodL'], LW[0] * .6))
    out.append(near_arm())
    hood = ('M -112 186 C -150 160, -146 116, -110 100 C -60 86, 60 86, 110 100 C 146 116, 150 160, 112 186 '
            'C 70 204, 20 222, 0 250 C -20 222, -70 204, -112 186 Z')
    out.append(shaded(hood, C['hood'], 'M -160 100 C -120 130, -100 170, -60 210 L -160 210 Z', C['hoodS'], C['hoodL']))
    return ''.join(out)


def figure_f(expr='sulk'):
    return (body_f() + L('M -70 150 C -40 200, 40 200, 70 150', C['boot'], LW[0] * 4) + g(head_f(expr), 0, HY)
            + cup(-72, 178, 20, 30) + cup(72, 178, 20, 30)
            + L('M -18 236 C -20 270, -16 300, -22 330 M 18 236 C 22 264, 18 292, 24 318', C['cord'], LW[0] * 1.3))


# ---------------------------------------------------------------- side view (facing right): the slouch shows best here
FACE_S = ('M -96 -30 C -100 -96, -46 -128, 6 -126 C 50 -124, 72 -92, 72 -52 C 72 -34, 70 -22, 72 -10 '
          'C 73 0, 72 20, 72 44 C 74 52, 74 58, 70 62 C 74 68, 72 76, 66 80 C 66 94, 56 104, 40 108 '
          'C 20 114, -14 108, -40 92 C -80 68, -94 30, -96 -30 Z')
HAIR_S = ('M 6 -138 C -24 -140, -54 -130, -78 -110 L -98 -112 L -94 -92 C -106 -74, -112 -54, -112 -34 L -130 -24 L -112 -8 '
          'C -112 20, -110 42, -102 62 L -122 86 L -94 78 L -98 108 L -72 88 L -64 114 L -48 86 '
          'C -40 60, -36 30, -34 0 C -32 -30, -20 -56, 0 -70 C 20 -84, 44 -88, 62 -80 L 68 -34 L 78 -66 L 86 -22 '
          'L 96 -62 C 96 -108, 60 -138, 6 -138 Z')


def head_s(expr='sulk', tilt=12):
    out = []
    # the far side of the fringe, seen past the forehead
    out.append(F('M 60 -100 C 84 -90, 100 -70, 104 -40 L 102 30 L 94 -6 L 84 14 L 78 -30 Z', C['hairS'], C['hairL']))
    out.append(shaded('M -40 70 C -36 120, -40 150, -46 176 L 18 176 C 14 150, 16 128, 22 104 Z', C['skin'],
                      'M -70 60 C -30 108, 10 120, 50 104 L 50 138 C 10 148, -30 134, -70 116 Z', C['shade'], C['line']))
    out.append(F(FACE_S, C['skin']))
    out.append(clip(FACE_S, F('M -110 -40 C -90 20, -60 70, 0 120 L -120 130 Z', C['shade'], extra='opacity=".5"'),
                    g(F(HAIR_S, C['shade']), 5, 9),
                    f'<ellipse cx="26" cy="44" rx="20" ry="11" fill="{C["blush"]}" opacity=".38"/>'))
    out.append(L(FACE_S, C['line']))
    nose = 'M 70 -2 C 76 14, 90 28, 94 40 C 96 46, 90 50, 82 50 C 76 50, 72 48, 68 48 Z'
    out.append(F(nose, C['skin']) + L('M 71 0 C 76 14, 90 28, 94 40 C 96 46, 90 50, 82 50 C 78 50, 74 49, 71 49', C['line'], LW[0] * .9))
    out.append(eye(44, 0, 11, 22, C, look=(3, 0), lid=.4, lidtilt=-3, ir=13, sq=.6, flick=-1, lash=2.6))
    out.append(brow(64, -22, 22, -32, 1, 7.5, C['hairL']))
    out.append(L('M 70 70 C 60 72, 50 72, 42 70', C['line'], LW[0] * 1.2))
    out.append(F(HAIR_S, C['hair']))
    out.append(clip(HAIR_S, F('M -30 -128 C 10 -134, 50 -122, 76 -96 C 48 -110, 14 -116, -24 -112 Z', C['hairH']),
                    F('M -130 20 C -100 40, -90 70, -70 110 L -130 110 Z', C['hairS'])))
    out.append(L(HAIR_S, C['hairL']))
    for d in ('M -20 -116 C 14 -108, 44 -96, 60 -74', 'M -60 -104 C -84 -74, -92 -34, -86 20', 'M -40 -90 C -58 -60, -62 -20, -60 30'):
        out.append(L(d, C['hairH'], LW[0] * .7))
    return f'<g transform="rotate({tilt} 0 100)">' + ''.join(out) + '</g>'


def body_s():
    low = []
    fl = ('M -30 620 L 50 620 C 60 740, 62 850, 54 950 C 36 1060, 14 1170, 4 1276 L -44 1276 '
          'C -40 1170, -24 1060, -4 950 C 0 850, -24 740, -30 620 Z')
    nl = ('M -50 620 L 34 620 C 38 740, 30 860, 14 960 C -8 1060, -26 1180, -32 1290 L -82 1290 '
          'C -82 1180, -70 1060, -48 960 C -38 860, -50 740, -50 620 Z')
    low.append(shaded(fl, C['trou'], 'M -40 620 L 0 620 L -10 960 L -50 1290 L -40 620 Z', C['trouS'], C['trouL']))
    low.append(boot(-20, 1270))
    low.append(shaded(nl, C['trou'], 'M -60 620 L -24 620 L -30 960 L -66 1300 L -100 1300 L -62 960 Z', C['trouS'], C['trouL']))
    low.append(L('M 8 950 C -2 956, -14 958, -26 956', C['trouL'], LW[0] * .7))
    low.append(boot(-56, 1284))
    out = []
    hoodie = ('M -44 178 C -96 196, -122 260, -118 340 C -116 440, -106 540, -96 640 C -40 658, 40 656, 100 636 '
              'C 104 520, 100 400, 90 300 C 84 240, 66 196, 30 178 C 10 168, -24 168, -44 178 Z')
    out.append(shaded(hoodie, C['hood'], 'M -140 180 C -100 320, -92 480, -76 660 L -140 660 Z', C['hoodS'], C['hoodL']))
    out.append(F('M -96 606 C -40 626, 40 624, 100 602 L 100 636 C 40 656, -40 658, -96 640 Z', C['hoodS'], C['hoodL']))
    out.append(F('M 34 452 C 54 452, 72 450, 90 446 C 98 490, 102 540, 102 584 C 72 594, 42 596, 16 592 C 18 540, 24 490, 34 452 Z',
                 C['hood'], C['hoodL']))
    # the near arm: the elbow back, the hand in the pocket
    arm = ('M -44 184 C -78 240, -96 320, -88 400 C -84 442, -62 462, -32 472 C 0 492, 30 512, 56 524 L 72 484 '
           'C 42 470, 18 450, 8 420 C 6 340, 12 260, 22 200 C 6 176, -26 172, -44 184 Z')
    out.append(shaded(arm, C['hood'], 'M -110 300 C -90 400, -60 450, 60 530 L -110 530 Z', C['hoodS'], C['hoodL']))
    out.append(L('M -40 300 C -34 330, -34 360, -40 396 M -10 430 C -20 440, -34 444, -48 442', C['hoodL'], LW[0] * .6))
    hood = ('M -64 190 C -104 170, -108 120, -74 100 C -44 86, 10 100, 40 130 C 60 150, 60 176, 44 190 '
            'C 20 206, -30 208, -64 190 Z')
    out.append(shaded(hood, C['hood'], 'M -120 100 C -90 140, -60 180, -20 210 L -120 210 Z', C['hoodS'], C['hoodL']))
    return ''.join(low), ''.join(out)


def figure_s(expr='sulk'):
    low, up = body_s()
    return (low + f'<g transform="{LEAN}">' + up + L('M -30 150 C -10 190, 30 196, 50 160', C['boot'], LW[0] * 4) + '</g>'
            + g(head_s(expr), HX + 14, HY) + f'<g transform="{LEAN}">' + cup(6, 178, 24, 30) + '</g>')
