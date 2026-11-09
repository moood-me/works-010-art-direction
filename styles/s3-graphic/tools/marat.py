"""Марат, about 35, a cook: huge, loud, merry, generous. Shape: a big barrel; curly hair and a black beard,
a white cook's jacket, a terracotta apron. His resting state is a wide smile."""
from lib import F, L, clip, shaded, g, LW, mx, curls, mirror
from face import eye, brow, closed_eye, shout

C = dict(skin='#e4ae88', shade='#c98b68', line='#84503c', blush='#e27f60', white='#fffaf3',
         iris='#4a2f1e', pupil='#170f0a', lash='#241712',
         hair='#33271f', hairS='#221914', hairH='#5e493c', hairL='#130d0a', lip='#cf7560', mouth='#6e2620',
         coat='#f7f0e3', coatS='#dfd3be', coatL='#8f7e68',
         apron='#d9693d', apronS='#bb5231', apronL='#6e2a17',
         towel='#f3e2c4', towelL='#9a7f58',
         trou='#544c4b', trouS='#403939', trouL='#1c1818', shoe='#3a2a24', shoeL='#150f0d',
         steel='#b4bcc0', steelS='#868f94', steelL='#474e53')

HX, HY, HS = 4, -8, 1.25  # the head in the figure: sunk into the shoulders, a short neck

# ---------------------------------------------------------------- head, three-quarter (facing right)
FACE_Q = ('M -100 -30 C -104 -92, -54 -126, 2 -126 C 58 -126, 96 -92, 98 -40 C 99 -22, 96 -8, 98 4 '
          'C 102 24, 102 50, 96 72 C 88 104, 64 124, 26 128 C -18 132, -60 116, -82 88 C -100 62, -100 20, -100 -30 Z')
HAIR_Q = curls([(-106, -2), (-118, -42), (-112, -84), (-88, -120), (-50, -142), (-8, -152), (36, -148), (74, -130),
                (100, -100), (110, -62), (102, -30), (86, -62), (60, -86), (26, -97), (-8, -96), (-42, -86),
                (-68, -62), (-82, -32), (-88, -2), (-106, -2)], .3) + ' Z'
BEARD_Q = ('M -102 -14 C -96 10, -90 34, -72 52 C -52 68, -22 66, 2 58 C 28 50, 62 50, 80 58 C 90 56, 96 48, 99 34 '
           + curls([(99, 34), (106, 70), (98, 106), (80, 136), (50, 154), (14, 162), (-26, 156), (-62, 138),
                    (-90, 108), (-106, 68), (-110, 26), (-102, -14)], .2, start=False) + ' Z')
NOSE_Q = ('M 58 -8 C 66 4, 90 14, 102 30 C 110 44, 104 58, 90 60 C 80 61, 72 58, 64 56 C 52 54, 44 44, 50 32 '
          'C 54 20, 58 6, 58 -8 Z')


def _mouth(expr):
    lipline = C['apronL']
    if expr == 'joy':
        d = 'M -6 60 C 24 74, 70 70, 100 50 C 106 96, 82 130, 46 130 C 14 130, -4 100, -6 60 Z'
        return (F(d, C['mouth']) + clip(d, F('M -12 50 L 106 40 L 106 68 C 74 82, 28 84, -12 72 Z', '#fff'),
                                         '<ellipse cx="50" cy="128" rx="30" ry="20" fill="#de6e64"/>',
                                         L('M 50 112 L 50 132', '#b9504a', LW[0] * .7))
                + L(d, lipline) + F('M 14 128 C 34 140, 64 138, 82 122 C 68 146, 30 148, 14 128 Z', C['lip'], lipline, LW[0] * .7))
    if expr == 'surprise':
        d = 'M 26 68 C 38 58, 62 58, 70 72 C 76 96, 62 116, 46 114 C 30 112, 20 88, 26 68 Z'
        return (F(d, C['mouth']) + clip(d, F('M 10 54 L 80 54 L 80 70 C 60 74, 40 74, 10 72 Z', '#fff'),
                                         '<ellipse cx="48" cy="114" rx="16" ry="11" fill="#de6e64"/>') + L(d, lipline)
                + F('M 30 112 C 40 122, 54 122, 64 110 C 56 128, 38 128, 30 112 Z', C['lip'], lipline, LW[0] * .7))
    if expr == 'sad':
        return (F('M 12 92 C 28 80, 62 78, 80 88 C 64 86, 30 88, 12 92 Z', C['lip'], lipline, LW[0] * .8)
                + F('M 22 94 C 36 90, 56 88, 70 92 C 60 104, 34 106, 22 94 Z', C['lip'], lipline, LW[0] * .8))
    if expr == 'anger':
        return shout(4, 90, 66, 40, lipline) + F('M 16 108 C 34 118, 62 116, 78 104 C 66 124, 30 126, 16 108 Z', C['lip'], lipline, LW[0] * .7)
    # the resting wide smile: teeth, a tongue, the lower lip
    d = 'M -2 66 C 26 80, 68 76, 96 56 C 98 88, 78 112, 46 112 C 20 112, 4 92, -2 66 Z'
    return (F(d, C['mouth']) + clip(d, F('M -8 56 L 102 46 L 102 72 C 72 86, 28 88, -8 78 Z', '#fff'),
                                     '<ellipse cx="50" cy="114" rx="26" ry="13" fill="#de6e64"/>')
            + L(d, lipline) + F('M 14 110 C 32 122, 62 120, 80 104 C 66 128, 30 130, 14 110 Z', C['lip'], lipline, LW[0] * .7))


def head_q(expr='smile', tilt=None):
    tilt = {'smile': -4, 'joy': -10, 'surprise': -3, 'sad': 6, 'anger': 2}.get(expr, -4) if tilt is None else tilt
    out = []
    out.append(shaded('M -56 80 L -54 150 L 44 150 L 46 100 Z', C['skin'], 'M -70 60 L 50 110 L 50 150 L -70 150 Z',
                      C['shade'], C['line']))
    # ear
    ear = 'M -90 -16 C -118 -28, -132 0, -124 28 C -118 46, -102 52, -86 42'
    out.append(F(ear + ' Z', C['skin'], C['line']))
    out.append(L('M -104 -2 C -114 6, -112 22, -102 28', C['line'], LW[0] * .8))
    out.append(F(FACE_Q, C['skin']))
    up = 6 if expr in ('smile', 'joy') else 0  # the cheeks go up with the laugh
    out.append(clip(FACE_Q,
                    F('M -120 -80 C -86 -40, -90 40, -40 120 L -120 130 Z', C['shade'], extra='opacity=".55"'),
                    g(F(HAIR_Q, C['shade']), 4, 10),
                    f'<ellipse cx="-44" cy="{30 - up}" rx="28" ry="16" fill="{C["blush"]}" opacity=".5"/>',
                    f'<ellipse cx="82" cy="{26 - up}" rx="13" ry="12" fill="{C["blush"]}" opacity=".5"/>'))
    out.append(L(FACE_Q, C['line']))
    # beard: one dark mass with a curly edge, the lower part darker
    out.append(F(BEARD_Q, C['hair']))
    out.append(clip(BEARD_Q, F('M -120 40 C -80 90, -30 130, 40 136 C 70 136, 96 120, 120 90 L 120 180 L -120 180 Z', C['hairS'])))
    out.append(L(BEARD_Q, C['hairL']))
    for d in ('M -84 70 C -78 82, -70 92, -60 98', 'M -50 118 C -40 126, -28 132, -16 134', 'M 84 96 C 80 106, 74 114, 66 120'):
        out.append(L(d, C['hairH'], LW[0] * .7))
    # eyes: dark, narrowed by the cheeks
    look = {'smile': (4, 0), 'surprise': (2, -1), 'sad': (1, 4), 'anger': (4, 1)}.get(expr, (4, 0))
    if expr == 'joy':
        out.append(closed_eye(-24, 4, 21, C, up=True, w=2.4))
        out.append(closed_eye(52, 4, 14, C, up=True, w=2.2))
    else:
        lid = {'smile': .2, 'surprise': 0, 'sad': .42, 'anger': .36}.get(expr, .3)
        lt = {'sad': -5, 'anger': 6}.get(expr, 0)
        low = .26 if expr == 'smile' else 0
        rs = 1.2 if expr == 'surprise' else 1
        out.append(eye(-24, 0, 21 * rs, 19 * rs, C, look=look, lid=lid, lidtilt=-lt, lower=low, ir=12.5, flick=-1, lash=1.7,
                       lowline=False, wing=False))
        out.append(eye(52, 0, 14 * rs, 18 * rs, C, look=look, lid=lid, lidtilt=lt, lower=low, ir=12, sq=.8, flick=1, lash=1.6,
                       lowline=False, wing=False))
    if expr in ('smile', 'joy'):  # laugh lines at the outer corner
        out.append(L('M -54 -6 L -64 -12 M -55 2 L -66 2 M -54 9 L -63 14', C['line'], LW[0] * .6, 'opacity=".6"'))
    # brows: thick black wedges
    bb = {'smile': ((2, -36, -58, -34, 12), (36, -36, 86, -36, 10)),
          'joy': ((2, -40, -58, -34, 16), (36, -40, 86, -36, 13)),
          'surprise': ((2, -50, -58, -48, 14), (36, -50, 86, -48, 12)),
          'sad': ((2, -46, -58, -26, 2), (36, -46, 84, -28, 2)),
          'anger': ((6, -20, -58, -40, 0), (34, -20, 86, -42, 0))}.get(expr)
    (a0, a1, a2, a3, ab), (b0, b1, b2, b3, bb_) = bb
    out.append(brow(a0, a1, a2, a3, ab, 14, C['hairL']))
    out.append(brow(b0, b1, b2, b3, bb_, 12, C['hairL']))
    low = [_mouth(expr)]
    # moustache over the upper lip
    md = {'smile': -4, 'joy': -8, 'sad': 8, 'anger': 4}.get(expr, 0)
    mo = (f'M -18 {76 + md} C -8 56, 24 44, 48 52 C 66 44, 96 44, 110 {60 + md} C 96 {58 + md * .5}, 76 62, 50 64 '
          f'C 30 70, 4 {68 + md * .5}, -18 {76 + md} Z')
    low.append(F(mo, C['hair'], C['hairL'], LW[0] * .8))
    low.append(L(f'M 20 {62 + md * .4} C 10 {64 + md * .6}, 2 {68 + md * .8}, -6 {72 + md} M 80 {56 + md * .3} C 88 {56 + md * .5}, 96 {57 + md * .7}, 102 {59 + md}', C['hairH'], LW[0] * .7))
    out.append(g(low, 0, 12))
    # nose: broad, a round tip and a wing; it hangs over the moustache
    n = [F(NOSE_Q, C['skin']),
         clip(NOSE_Q, F('M 30 0 C 54 26, 62 46, 84 66 L 30 70 Z', C['shade']),
              '<ellipse cx="90" cy="26" rx="6" ry="3.5" fill="#fff" opacity=".5"/>'),
         L('M 59 -4 C 66 4, 90 14, 102 30 C 110 44, 104 58, 90 60 C 80 61, 72 58, 64 56 C 52 54, 44 44, 50 32', C['line'], LW[0] * .8),
         L('M 66 54 C 72 46, 78 48, 80 56', C['line'], LW[0] * .7)]
    out.append(f'<g transform="translate(58 -8) scale(1.0 1.14) translate(-58 8)">' + ''.join(n) + '</g>')
    # hair: a cap of curls
    out.append(F(HAIR_Q, C['hair']))
    out.append(clip(HAIR_Q, F('M -60 -126 C -34 -142, 6 -148, 40 -140 C 14 -136, -14 -130, -38 -118 Z', C['hairH']),
                    F('M -130 -60 C -104 -80, -84 -60, -70 -30 L -70 10 L -130 10 Z', C['hairS'])))
    out.append(L(HAIR_Q, C['hairL']))
    for d in ('M -84 -92 C -74 -100, -62 -98, -58 -88 C -56 -80, -64 -76, -70 -80',
              'M 20 -122 C 30 -130, 44 -126, 46 -116 C 46 -108, 38 -106, 32 -110',
              'M 70 -96 C 80 -100, 90 -92, 88 -82'):
        out.append(L(d, C['hairH'], LW[0] * .8))
    return f'<g transform="rotate({tilt} 0 100)">' + ''.join(out) + '</g>'


# ---------------------------------------------------------------- shared body parts
def shoe(x, y, k=1.25):
    """A heavy round-toed kitchen shoe pointing right; (x, y) is the ankle."""
    p = lambda a, b: f'{x + a * k:.1f} {y + b * k:.1f}'
    sh = (f'M {p(-46, -4)} L {p(30, -6)} C {p(64, -2)}, {p(84, 14)}, {p(84, 34)} C {p(84, 46)}, {p(60, 48)}, {p(30, 48)} '
          f'L {p(-46, 46)} C {p(-54, 30)}, {p(-54, 8)}, {p(-46, -4)} Z')
    hi = f'M {p(40, 4)} C {p(60, 6)}, {p(72, 14)}, {p(76, 24)} C {p(64, 18)}, {p(52, 12)}, {p(40, 4)} Z'
    return F(sh, C['shoe'], C['shoeL']) + F(hi, '#6b5045')


def fist(x, y, s=1, flip=1):
    """A big closed fist seen from the back of the hand: a rounded block, the thumb over it, three knuckle lines."""
    p = lambda a, b: f'{x + a * s * flip:.1f} {y + b * s:.1f}'
    d = (f'M {p(-44, -14)} C {p(-52, 18)}, {p(-34, 44)}, {p(-4, 46)} C {p(26, 48)}, {p(44, 26)}, {p(40, -2)} '
         f'C {p(36, -28)}, {p(12, -40)}, {p(-14, -38)} C {p(-28, -38)}, {p(-40, -28)}, {p(-44, -14)} Z')
    sh = f'M {p(-60, 10)} C {p(-30, 30)}, {p(10, 36)}, {p(50, 20)} L {p(50, 60)} L {p(-60, 60)} Z'
    th = f'M {p(-34, -30)} C {p(-16, -46)}, {p(14, -44)}, {p(26, -26)} C {p(12, -20)}, {p(-12, -20)}, {p(-34, -30)} Z'
    kn = f'M {p(24, -8)} C {p(32, 0)}, {p(34, 8)}, {p(32, 16)} M {p(14, 14)} C {p(22, 20)}, {p(24, 28)}, {p(20, 36)} M {p(-2, 24)} C {p(4, 30)}, {p(6, 36)}, {p(2, 42)}'
    return shaded(d, C['skin'], sh, C['shade'], C['line']) + F(th, C['skin'], C['line']) + L(kn, C['line'], LW[0] * .7)


def ladle(x0, y0, x1, y1):
    """A ladle: the handle from (x0, y0) up to the bowl at (x1, y1)."""
    out = [L(f'M {x0} {y0} L {x1} {y1}', C['steelL'], 13), L(f'M {x0} {y0} L {x1} {y1}', C['steel'], 8)]
    bowl = (f'M {x1 - 44} {y1 - 12} C {x1 - 50} {y1 - 62}, {x1 + 62} {y1 - 70}, {x1 + 64} {y1 - 20} '
            f'C {x1 + 60} {y1 + 30}, {x1 - 36} {y1 + 40}, {x1 - 44} {y1 - 12} Z')
    out.append(shaded(bowl, C['steel'], f'M {x1 - 60} {y1} C {x1 - 20} {y1 + 20}, {x1 + 30} {y1 + 14}, {x1 + 70} {y1 - 20} L {x1 + 70} {y1 + 50} L {x1 - 60} {y1 + 50} Z',
                      C['steelS'], C['steelL']))
    out.append(F(f'M {x1 - 30} {y1 - 30} C {x1 - 10} {y1 - 46}, {x1 + 24} {y1 - 48}, {x1 + 40} {y1 - 36} C {x1 + 20} {y1 - 40}, {x1 - 6} {y1 - 38}, {x1 - 30} {y1 - 30} Z', '#e6ecee'))
    return ''.join(out)


def legs(near, far):
    out = []
    for (x0, x1, yb), sh in ((far, 1), (near, -1)):
        d = f'M {x0} 1020 L {x1} 1020 C {x1 - 2} 1100, {x1 - 10} 1180, {x1 - 16} {yb} L {x0 + 16} {yb + 2} C {x0 + 10} 1180, {x0 + 2} 1100, {x0} 1020 Z'
        s = (f'M {x1 - 50} 1020 L {x1 + 20} 1020 L {x1 + 20} {yb + 10} L {x1 - 60} {yb + 10} Z' if sh > 0 else
             f'M {x0 - 20} 1020 L {x0 + 40} 1020 L {x0 + 50} {yb + 10} L {x0 - 20} {yb + 10} Z')
        out.append(shaded(d, C['trou'], s, C['trouS'], C['trouL']))
    return ''.join(out)


def towel(d, stripes, shade_d):
    return (F(d, C['towel']) + clip(d, F(shade_d, C['coatS'], extra='opacity=".7"'),
                                    ''.join(F(s, C['apron']) for s in stripes)) + L(d, C['towelL']))


def buttons(pts):
    return ''.join(f'<circle cx="{x}" cy="{y}" r="8" fill="{C["apron"]}" stroke="{C["apronL"]}" stroke-width="1.8"/>' for x, y in pts)


# ---------------------------------------------------------------- body, three-quarter
JACKET_Q = ('M -196 176 C -236 200, -250 280, -244 360 C -240 440, -232 520, -222 590 L 226 590 '
            'C 248 520, 262 430, 254 340 C 248 262, 222 200, 176 172 C 110 146, -120 148, -196 176 Z')
APRON_Q = ('M -228 546 C -100 566, 130 564, 252 538 C 270 640, 256 860, 226 1040 C 90 1056, -80 1056, -204 1040 '
           'C -216 880, -226 700, -228 546 Z')


def far_arm(pose):
    out = []
    if pose == 'ladle':  # the arm thrown up, the ladle like a sceptre
        out.append(ladle(350, 150, 428, -150))
        fore = 'M 290 310 C 286 236, 304 150, 326 92 L 410 110 C 410 176, 400 250, 378 316 Z'
        out.append(shaded(fore, C['skin'], 'M 280 320 C 300 240, 316 160, 340 90 L 300 90 L 270 320 Z', C['shade'], C['line']))
        for d in ('M 344 250 L 350 240 M 356 222 L 362 212 M 348 196 L 354 186 M 364 172 L 370 162',):
            out.append(L(d, C['line'], LW[0] * .6, 'opacity=".6"'))
        out.append(fist(370, 74, 1.25, -1))
        slv = 'M 150 168 C 226 150, 316 186, 372 244 C 392 270, 382 312, 352 328 L 292 326 C 250 320, 206 304, 170 294 Z'
        out.append(shaded(slv, C['coat'], 'M 170 262 C 230 284, 290 304, 350 330 L 170 340 Z', C['coatS'], C['coatL']))
        out.append(F('M 376 250 C 394 274, 384 314, 354 330 L 286 326 C 296 308, 300 292, 298 274 C 326 276, 354 268, 376 250 Z',
                     C['coatS'], C['coatL']))
    else:  # a fist on the far hip: the elbow shows behind the belly
        fore = 'M 322 384 C 322 440, 296 500, 250 540 L 216 500 C 246 470, 256 440, 252 410 Z'
        out.append(shaded(fore, C['skin'], 'M 200 480 L 330 440 L 330 560 L 200 560 Z', C['shade'], C['line']))
        slv = 'M 170 176 C 232 200, 292 270, 320 356 C 328 390, 312 416, 288 424 L 236 420 L 226 240 Z'
        out.append(shaded(slv, C['coat'], 'M 250 180 L 340 180 L 340 430 L 280 430 Z', C['coatS'], C['coatL']))
        out.append(F('M 324 350 C 332 388, 314 418, 286 426 L 240 420 L 244 388 C 276 386, 304 372, 324 350 Z', C['coatS'], C['coatL']))
    return ''.join(out)


def near_arm():
    """The near arm: a rolled sleeve, a thick forearm, the fist on the hip."""
    out = []
    fore = 'M -330 388 C -334 450, -306 508, -258 554 L -200 514 C -230 486, -242 452, -242 410 Z'
    out.append(shaded(fore, C['skin'], 'M -340 400 C -320 470, -290 520, -250 560 L -340 560 Z', C['shade'], C['line']))
    out.append(L('M -292 440 L -284 448 M -276 462 L -268 470 M -284 480 L -276 488 M -262 492 L -254 500', C['line'], LW[0] * .6, 'opacity=".6"'))
    out.append(fist(-212, 552, 1.25))
    slv = 'M -190 174 C -248 186, -294 250, -322 350 C -332 384, -320 414, -294 424 L -238 404 C -230 340, -214 280, -176 236 Z'
    out.append(shaded(slv, C['coat'], 'M -340 300 C -300 350, -270 390, -230 420 L -340 430 Z', C['coatS'], C['coatL']))
    out.append(F('M -328 338 C -308 366, -270 384, -232 384 L -236 420 C -276 432, -320 412, -336 378 Z', C['coatS'], C['coatL']))
    out.append(L('M -262 230 C -280 262, -292 296, -300 330', C['coatL'], LW[0] * .6))
    return ''.join(out)


def body_q(pose='ladle'):
    low = legs((-150, 0, 1250), (60, 220, 1236)) + shoe(-70, 1250) + shoe(150, 1234)
    out = [far_arm(pose)]
    # the jacket: a barrel, double-breasted
    out.append(shaded(JACKET_Q, C['coat'],
                      'M -260 180 C -216 320, -210 460, -190 600 L -260 600 Z M 176 170 C 210 300, 218 460, 204 600 L 270 600 L 270 170 Z',
                      C['coatS'], C['coatL']))
    out.append(L('M -40 160 C -64 260, -70 420, -62 560', C['coatL'], LW[0] * .8))
    out.append(buttons([(-26, 250), (-30, 330), (-30, 410), (-26, 490), (110, 244), (118, 324), (120, 404), (116, 484)]))
    # the apron: long, tied at the waist
    out.append(shaded(APRON_Q, C['apron'],
                      'M -240 540 C -200 700, -196 880, -180 1050 L -240 1050 Z M 176 540 C 196 700, 196 880, 184 1050 L 270 1050 L 270 540 Z',
                      C['apronS'], C['apronL']))
    out.append(L('M -60 620 C -66 760, -64 900, -58 1036', C['apronL'], LW[0] * .7))
    out.append(L('M 96 620 C 104 760, 102 900, 96 1036', C['apronL'], LW[0] * .7))
    out.append(F('M -170 700 L -76 706 C -76 760, -80 800, -86 830 C -116 836, -146 832, -164 824 C -170 790, -172 750, -170 700 Z', C['apron'], C['apronL'], LW[0] * .8))
    out.append(L('M -170 716 L -76 722', C['apronL'], LW[0] * .6))
    band = 'M -228 546 C -100 566, 130 564, 252 538 L 252 576 C 130 602, -100 604, -228 584 Z'
    out.append(F(band, C['apronS'], C['apronL']))
    out.append(F('M 30 574 C 10 548, -30 552, -34 580 C -30 604, 8 606, 30 588 Z M 44 574 C 66 548, 104 552, 106 578 C 102 602, 66 604, 44 588 Z',
                 C['apron'], C['apronL']))
    out.append(F('M 28 572 L 46 572 L 48 592 L 26 592 Z', C['apronS'], C['apronL']))
    out.append(F('M 28 592 C 20 620, 16 650, 22 676 L 40 668 C 36 640, 38 616, 44 592 Z M 44 592 C 56 616, 62 640, 60 660 L 76 650 C 74 626, 66 606, 52 590 Z',
                 C['apron'], C['apronL']))
    # the collar and a terracotta neckerchief
    out.append(F('M -86 150 C -40 196, 70 196, 112 146 L 116 176 C 70 228, -44 228, -92 182 Z', C['coat'], C['coatL']))
    out.append(F('M -70 170 C -30 204, 60 204, 100 164 C 70 216, 40 236, 22 262 C 4 238, -44 214, -70 170 Z', C['apron'], C['apronL']))
    # the towel over the near shoulder
    out.append(towel('M -176 160 C -150 150, -122 148, -100 152 C -96 240, -98 330, -106 410 L -180 416 C -176 330, -178 240, -176 160 Z',
                     ['M -200 356 L -80 348 L -80 362 L -200 370 Z', 'M -200 380 L -80 372 L -80 386 L -200 394 Z'],
                     'M -200 150 L -160 150 L -164 420 L -200 420 Z'))
    out.append(L('M -140 170 C -138 240, -140 300, -144 340', C['towelL'], LW[0] * .6))
    out.append(near_arm())
    return low, ''.join(out)


LEAN = 'rotate(-3.5 20 1040)'  # he laughs leaning back: the belly forward, the head behind it


def figure_q(expr='smile', pose='ladle'):
    low, up = body_q(pose)
    return low + f'<g transform="{LEAN}">' + up + g(head_q(expr), HX, HY, HS) + '</g>'


def figure_qn(expr='smile'):
    """The calm three-quarter view for the turnaround: both fists on the hips."""
    return figure_q(expr, 'hips')


# ---------------------------------------------------------------- front view
FACE_F = ('M -98 -30 C -100 -94, -52 -126, 0 -126 C 52 -126, 100 -94, 98 -30 C 100 12, 100 52, 88 80 '
          'C 70 112, 36 128, 0 128 C -36 128, -70 112, -88 80 C -100 52, -100 12, -98 -30 Z')
HAIR_F = curls([(-104, -2), (-116, -42), (-110, -84), (-86, -120), (-48, -144), (0, -154), (48, -144), (86, -120),
                (110, -84), (116, -42), (104, -2), (88, -2), (82, -34), (64, -66), (36, -90), (0, -98), (-36, -90),
                (-64, -66), (-82, -34), (-88, -2), (-104, -2)], .3) + ' Z'
BEARD_F = ('M -100 -14 C -96 14, -90 42, -72 58 C -52 72, -24 66, 0 60 C 24 66, 52 72, 72 58 C 90 42, 96 14, 100 -14 '
           + curls([(100, -14), (108, 26), (104, 68), (90, 108), (62, 140), (24, 160), (-24, 160), (-62, 140),
                    (-90, 108), (-104, 68), (-108, 26), (-100, -14)], .2, start=False) + ' Z')


def head_f(expr='smile'):
    out = []
    out.append(shaded('M -56 80 L -56 150 L 56 150 L 56 80 Z', C['skin'], 'M -60 60 C -20 120, 20 120, 60 60 L 60 150 L -60 150 Z',
                      C['shade'], C['line']))
    ear = 'M -90 -16 C -118 -28, -132 0, -124 28 C -118 46, -102 52, -86 42'
    for d in (ear, mx(ear)):
        out.append(F(d + ' Z', C['skin'], C['line']))
    out.append(F(FACE_F, C['skin']))
    out.append(clip(FACE_F, F('M -120 -80 C -90 -40, -92 40, -50 120 L -120 130 Z', C['shade'], extra='opacity=".55"'),
                    g(F(HAIR_F, C['shade']), 0, 10),
                    f'<ellipse cx="-58" cy="26" rx="24" ry="15" fill="{C["blush"]}" opacity=".5"/>',
                    f'<ellipse cx="58" cy="26" rx="24" ry="15" fill="{C["blush"]}" opacity=".5"/>'))
    out.append(L(FACE_F, C['line']))
    out.append(F(BEARD_F, C['hair']))
    out.append(clip(BEARD_F, F('M -120 50 C -70 120, 0 146, 60 136 C 90 128, 108 110, 120 90 L 120 180 L -120 180 Z', C['hairS'])))
    out.append(L(BEARD_F, C['hairL']))
    for d in ('M -84 76 C -78 88, -70 98, -60 104', 'M -40 132 C -30 138, -20 142, -8 142', 'M 84 76 C 78 88, 70 98, 60 104'):
        out.append(L(d, C['hairH'], LW[0] * .7))
    out.append(eye(-40, 0, 20, 19, C, look=(0, 0), lid=.2, lower=.26, ir=12.5, flick=-1, lash=1.7, lowline=False, wing=False))
    out.append(eye(40, 0, 20, 19, C, look=(0, 0), lid=.2, lower=.26, ir=12.5, flick=1, lash=1.7, lowline=False, wing=False))
    out.append(brow(-12, -36, -72, -34, 12, 14, C['hairL']))
    out.append(brow(12, -36, 72, -34, 12, 14, C['hairL']))
    # mouth, moustache, then the nose over it
    d = 'M -54 80 C -26 92, 26 92, 54 80 C 54 112, 32 132, 0 132 C -32 132, -54 112, -54 80 Z'
    out.append(F(d, C['mouth']) + clip(d, F('M -64 66 L 64 66 L 64 88 C 30 100, -30 100, -64 88 Z', '#fff'),
                                        '<ellipse cx="0" cy="134" rx="28" ry="14" fill="#de6e64"/>') + L(d, C['apronL']))
    out.append(F('M -34 130 C -14 142, 14 142, 34 130 C 20 150, -20 150, -34 130 Z', C['lip'], C['apronL'], LW[0] * .7))
    mo = 'M 0 72 C 22 60, 54 64, 76 82 C 56 80, 30 86, 0 86 C -30 86, -56 80, -76 82 C -54 64, -22 60, 0 72 Z'
    out.append(F(mo, C['hair'], C['hairL'], LW[0] * .8))
    out.append(L('M -30 74 C -42 74, -54 76, -64 80 M 30 74 C 42 74, 54 76, 64 80', C['hairH'], LW[0] * .7))
    nose = 'M -14 -8 C -14 16, -38 26, -38 48 C -38 64, -18 70, 0 70 C 18 70, 38 64, 38 48 C 38 26, 14 16, 14 -8 Z'
    out.append(F(nose, C['skin']))
    out.append(clip(nose, F('M -50 0 C -30 30, -24 50, -12 76 L -50 76 Z', C['shade']),
                    '<ellipse cx="8" cy="34" rx="7" ry="4" fill="#fff" opacity=".5"/>'))
    out.append(L(nose[:-2], C['line'], LW[0] * .8))
    out.append(L('M -22 62 C -18 54, -10 54, -8 62 M 22 62 C 18 54, 10 54, 8 62', C['line'], LW[0] * .7))
    out.append(F(HAIR_F, C['hair']))
    out.append(clip(HAIR_F, F('M -70 -124 C -40 -146, 10 -152, 50 -142 C 20 -138, -16 -130, -44 -114 Z', C['hairH']),
                    F('M -130 -60 C -104 -80, -84 -60, -70 -30 L -70 10 L -130 10 Z', C['hairS'])))
    out.append(L(HAIR_F, C['hairL']))
    for d in ('M -84 -92 C -74 -100, -62 -98, -58 -88 C -56 -80, -64 -76, -70 -80',
              'M 20 -124 C 30 -132, 44 -128, 46 -118 C 46 -110, 38 -108, 32 -112',
              'M 76 -96 C 86 -100, 96 -92, 94 -82'):
        out.append(L(d, C['hairH'], LW[0] * .8))
    return ''.join(out)


JACKET_F = ('M -206 176 C -246 200, -258 280, -252 360 C -248 440, -238 520, -228 590 L 228 590 '
            'C 238 520, 248 440, 252 360 C 258 280, 246 200, 206 176 C 130 148, -130 148, -206 176 Z')
APRON_F = ('M -236 546 C -100 566, 100 566, 236 546 C 248 700, 238 880, 218 1040 C 80 1056, -80 1056, -218 1040 '
           'C -238 880, -248 700, -236 546 Z')


def shoe_f(x, y, k=1.25):
    p = lambda a, b: f'{x + a * k:.1f} {y + b * k:.1f}'
    return F(f'M {p(-40, -4)} L {p(40, -4)} C {p(52, 10)}, {p(54, 34)}, {p(46, 46)} L {p(-46, 46)} '
             f'C {p(-54, 34)}, {p(-52, 10)}, {p(-40, -4)} Z', C['shoe'], C['shoeL'])


def body_f():
    out = [legs((-176, -12, 1250), (12, 176, 1250)), shoe_f(-94, 1252), shoe_f(94, 1252)]
    out.append(shaded(JACKET_F, C['coat'], 'M -270 180 C -226 320, -220 460, -200 600 L -270 600 Z', C['coatS'], C['coatL']))
    out.append(L('M -84 160 C -100 260, -104 420, -98 560', C['coatL'], LW[0] * .8))
    out.append(buttons([(-64, 250), (-66, 330), (-66, 410), (-64, 490), (64, 250), (66, 330), (66, 410), (64, 490)]))
    out.append(shaded(APRON_F, C['apron'], 'M -250 540 C -210 700, -206 880, -190 1050 L -250 1050 Z', C['apronS'], C['apronL']))
    out.append(L('M -80 620 C -86 760, -84 900, -78 1040 M 80 620 C 86 760, 84 900, 78 1040', C['apronL'], LW[0] * .7))
    out.append(F('M -236 546 C -100 566, 100 566, 236 546 L 236 584 C 100 604, -100 604, -236 584 Z', C['apronS'], C['apronL']))
    out.append(F('M -8 578 C -28 552, -68 556, -72 584 C -68 608, -30 610, -8 592 Z M 8 578 C 28 552, 68 556, 72 584 C 68 608, 30 610, 8 592 Z',
                 C['apron'], C['apronL']))
    out.append(F('M -10 574 L 10 574 L 12 596 L -12 596 Z', C['apronS'], C['apronL']))
    out.append(F('M -10 596 C -18 624, -22 654, -16 680 L 2 672 C -2 644, 0 620, 6 596 Z M 6 596 C 18 620, 24 644, 22 664 L 38 654 C 36 630, 28 610, 14 594 Z',
                 C['apron'], C['apronL']))
    out.append(F('M -100 150 C -50 196, 50 196, 100 150 L 104 180 C 56 228, -56 228, -104 180 Z', C['coat'], C['coatL']))
    out.append(F('M -84 170 C -40 204, 40 204, 84 170 C 50 216, 20 236, 0 262 C -20 236, -50 216, -84 170 Z', C['apron'], C['apronL']))
    out.append(towel('M -186 160 C -160 150, -132 148, -110 152 C -106 240, -108 330, -116 410 L -190 416 C -186 330, -188 240, -186 160 Z',
                     ['M -210 356 L -90 348 L -90 362 L -210 370 Z', 'M -210 380 L -90 372 L -90 386 L -210 394 Z'],
                     'M -210 150 L -170 150 L -174 420 L -210 420 Z'))
    out.append(g(near_arm(), -10, 0) + mirror(g(near_arm(), -10, 0)))
    return ''.join(out)


def figure_f(expr='smile'):
    return body_f() + g(head_f(expr), 0, HY, HS)


# ---------------------------------------------------------------- side view (facing right)
FACE_S = ('M -98 -30 C -102 -96, -46 -128, 6 -126 C 54 -124, 78 -92, 78 -50 C 78 -32, 74 -20, 78 -8 '
          'C 80 6, 84 30, 84 52 C 84 84, 78 106, 58 120 C 30 132, -12 128, -44 110 C -84 88, -96 30, -98 -30 Z')
HAIR_S = curls([(-72, 72), (-102, 40), (-116, 0), (-118, -44), (-106, -88), (-78, -122), (-38, -144), (8, -152),
                (48, -142), (76, -116), (88, -80), (80, -52), (56, -74), (26, -88), (-4, -80), (-22, -54),
                (-30, -24), (-56, -8), (-70, 24), (-64, 50), (-72, 72)], .3) + ' Z'
BEARD_S = ('M -26 4 C -20 30, -4 52, 20 60 C 40 66, 62 60, 84 62 '
           + curls([(84, 62), (92, 98), (80, 132), (50, 154), (12, 160), (-24, 146), (-48, 118), (-58, 80),
                    (-50, 40), (-26, 4)], .2, start=False) + ' Z')


def head_s(expr='smile'):
    out = []
    out.append(shaded('M -50 70 L -40 150 L 34 150 L 34 90 Z', C['skin'], 'M -70 60 L 50 110 L 50 150 L -70 150 Z',
                      C['shade'], C['line']))
    out.append(F(FACE_S, C['skin']))
    out.append(clip(FACE_S, F('M -110 -40 C -90 20, -60 80, 0 130 L -120 130 Z', C['shade'], extra='opacity=".5"'),
                    g(F(HAIR_S, C['shade']), 4, 10),
                    f'<ellipse cx="30" cy="26" rx="24" ry="15" fill="{C["blush"]}" opacity=".5"/>'))
    out.append(L(FACE_S, C['line']))
    out.append(F(BEARD_S, C['hair']))
    out.append(clip(BEARD_S, F('M -80 60 C -40 110, 20 140, 100 110 L 100 180 L -80 180 Z', C['hairS'])))
    out.append(L(BEARD_S, C['hairL']))
    for d in ('M -40 78 C -36 92, -28 104, -18 112', 'M 6 138 C 18 144, 30 144, 42 140'):
        out.append(L(d, C['hairH'], LW[0] * .7))
    out.append(eye(46, 0, 10, 18, C, look=(3, 0), lid=.2, lower=.26, ir=12, sq=.6, flick=-1, lash=1.7, lowline=False, wing=False))
    out.append(L('M 26 -6 L 16 -12 M 25 2 L 14 2 M 26 9 L 17 14', C['line'], LW[0] * .6, 'opacity=".6"'))
    out.append(brow(74, -38, 22, -34, 10, 14, C['hairL']))
    d = 'M 34 90 C 52 98, 70 94, 88 82 C 90 106, 80 126, 62 128 C 46 128, 36 112, 34 90 Z'
    out.append(F(d, C['mouth']) + clip(d, F('M 20 76 L 96 70 L 96 92 C 70 104, 50 106, 20 100 Z', '#fff'),
                                        '<ellipse cx="66" cy="130" rx="20" ry="12" fill="#de6e64"/>') + L(d, C['apronL']))
    out.append(F('M 44 124 C 56 134, 72 132, 82 120 C 76 140, 52 142, 44 124 Z', C['lip'], C['apronL'], LW[0] * .7))
    out.append(F('M 22 92 C 34 70, 66 62, 96 76 C 80 78, 60 86, 22 92 Z', C['hair'], C['hairL'], LW[0] * .8))
    nose = 'M 74 -8 C 82 4, 96 16, 104 32 C 112 48, 108 66, 94 68 C 86 69, 80 66, 74 64 C 66 56, 70 30, 74 -8 Z'
    out.append(F(nose, C['skin']) + clip(nose, '<ellipse cx="96" cy="32" rx="5" ry="3.5" fill="#fff" opacity=".5"/>')
               + L('M 75 -4 C 82 4, 96 16, 104 32 C 112 48, 108 66, 94 68 C 86 69, 80 66, 74 64', C['line'], LW[0] * .8)
               + L('M 74 62 C 78 54, 86 54, 88 62', C['line'], LW[0] * .7))
    out.append(F(HAIR_S, C['hair']))
    out.append(clip(HAIR_S, F('M -60 -126 C -30 -146, 10 -150, 46 -140 C 16 -136, -16 -130, -40 -116 Z', C['hairH']),
                    F('M -130 0 C -100 20, -80 50, -60 80 L -130 80 Z', C['hairS'])))
    out.append(L(HAIR_S, C['hairL']))
    for d in ('M -84 -60 C -74 -68, -62 -66, -58 -56 C -56 -48, -64 -44, -70 -48',
              'M 10 -122 C 20 -130, 34 -126, 36 -116 C 36 -108, 28 -106, 22 -110',
              'M -84 20 C -76 14, -66 18, -66 28'):
        out.append(L(d, C['hairH'], LW[0] * .8))
    out.append(F('M -30 -12 C -54 -24, -68 2, -60 26 C -54 42, -38 46, -26 36 Z', C['skin'], C['line']))
    out.append(L('M -44 -2 C -52 6, -50 20, -42 26', C['line'], LW[0] * .8))
    return ''.join(out)


def body_s():
    out = []
    for x in (26, -10):
        d = f'M {x - 84} 1020 L {x + 80} 1020 C {x + 78} 1100, {x + 70} 1180, {x + 64} 1250 L {x - 68} 1252 C {x - 74} 1180, {x - 82} 1100, {x - 84} 1020 Z'
        out.append(shaded(d, C['trou'], f'M {x - 100} 1020 L {x - 44} 1020 L {x - 34} 1260 L {x - 100} 1260 Z', C['trouS'], C['trouL']))
        out.append(shoe(x, 1250))
    jacket = ('M -96 180 C -130 230, -138 330, -132 420 C -130 480, -124 540, -116 590 L 170 590 C 214 540, 232 450, 222 370 '
              'C 214 300, 176 240, 124 200 C 92 176, 40 160, -20 158 C -52 160, -80 168, -96 180 Z')
    out.append(shaded(jacket, C['coat'], 'M -150 180 C -110 320, -106 460, -90 600 L -150 600 Z', C['coatS'], C['coatL']))
    out.append(buttons([(176, 280), (204, 350), (212, 420), (206, 490)]))
    apron = ('M -118 548 C -20 562, 100 560, 200 536 C 226 640, 212 860, 184 1040 C 100 1052, -20 1052, -104 1040 '
             'C -114 880, -120 700, -118 548 Z')
    out.append(shaded(apron, C['apron'], 'M -130 540 C -96 700, -92 880, -80 1050 L -130 1050 Z', C['apronS'], C['apronL']))
    out.append(L('M 60 620 C 64 760, 60 900, 54 1040', C['apronL'], LW[0] * .7))
    out.append(F('M -118 548 C -20 562, 100 560, 200 536 L 204 574 C 100 598, -20 600, -118 586 Z', C['apronS'], C['apronL']))
    out.append(F('M -44 150 C -10 190, 70 196, 104 160 L 108 190 C 70 226, -14 222, -52 180 Z', C['coat'], C['coatL']))
    out.append(F('M 60 186 C 80 190, 98 184, 108 172 C 110 200, 104 226, 96 244 C 84 224, 70 204, 60 186 Z', C['apron'], C['apronL']))
    out.append(towel('M -66 164 C -40 152, -12 150, 10 156 C 14 240, 12 330, 4 410 L -70 416 C -66 330, -68 240, -66 164 Z',
                     ['M -90 356 L 30 348 L 30 362 L -90 370 Z', 'M -90 380 L 30 372 L 30 386 L -90 394 Z'],
                     'M -90 150 L -50 150 L -54 420 L -90 420 Z'))
    # the near arm: the elbow back, the fist on the hip
    fore = 'M -120 392 C -112 452, -80 512, -30 558 L 22 514 C -8 488, -30 452, -38 410 Z'
    out.append(shaded(fore, C['skin'], 'M -130 420 C -100 490, -70 530, -30 566 L -130 566 Z', C['shade'], C['line']))
    out.append(fist(14, 548, 1.25))
    slv = 'M -76 178 C -110 240, -128 320, -122 392 C -112 424, -70 436, -30 420 C -22 340, -4 262, 30 200 C 0 172, -46 164, -76 178 Z'
    out.append(shaded(slv, C['coat'], 'M -140 300 C -110 360, -90 400, -50 430 L -140 440 Z', C['coatS'], C['coatL']))
    out.append(F('M -126 350 C -100 374, -62 384, -24 376 L -28 416 C -66 438, -112 426, -126 394 Z', C['coatS'], C['coatL']))
    return ''.join(out)


def figure_s(expr='smile'):
    return body_s() + g(head_s(expr), 20, HY, HS)
