"""Тим's front and profile, drawn here by the С3 style's rules and code (styles/s3-graphic/tools: lib.py, face.py and
tim.py's colours) — the style page has only his three-quarter view, and the 3D needs two flat views to be fitted to.
Figure units are tim.py's own (the head's eye line at y=14, soles at y=682). The shapes named in capitals are what
build.py samples; figure_f() and figure_s() draw the views; sheet() puts them beside the style's own three-quarter.
  python3 views.py outdir   → turnaround-tim.svg (front, the style's 3/4, profile)"""
import os, sys, base64
S3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'styles', 's3-graphic', 'tools')
sys.path.insert(0, S3)
import tim  # noqa: E402
from lib import F, L, clip, shaded, g, LW, mx, svg, text  # noqa: E402
from face import eye, brow  # noqa: E402

C = tim.C
FLOOR, CROWN = 682.0, -156.0

# ---------------------------------------------------------------- front (symmetric shapes; x<0 is the picture's left)
HEAD_F = ('M -102 8 C -102 -64, -58 -106, 0 -106 C 58 -106, 102 -64, 102 8 C 102 34, 98 52, 92 66 '
          'C 80 100, 44 116, 0 116 C -44 116, -80 100, -92 66 C -98 52, -102 34, -102 8 Z')
NECK_F = 'M -30 96 L -32 152 L 32 152 L 30 96 Z'
EAR_F = 'M -96 0 C -124 -16, -140 12, -130 40 C -124 58, -106 60, -94 48 Z'          # the picture's left ear
HAIR_F = ('M -106 4 C -116 -60, -80 -116, -22 -122 L -30 -150 L 4 -126 L 16 -156 L 36 -122 '
          'C 82 -114, 114 -76, 110 -36 L 128 -46 L 106 0 C 102 -26, 96 -44, 84 -58 '
          'C 72 -48, 58 -44, 42 -46 L 50 -66 C 32 -54, 10 -50, -14 -54 L -6 -72 '
          'C -26 -60, -50 -52, -72 -46 C -86 -36, -94 -18, -96 2 Z')
SHIRT_F = ('M -40 124 C -78 128, -108 142, -114 176 C -118 230, -118 290, -112 338 L 112 338 '
           'C 118 290, 118 230, 114 176 C 108 142, 78 128, 40 124 C 20 138, -20 138, -40 124 Z')
SHORTS_F = 'M -112 316 L 112 316 L 118 446 L 14 452 L 0 392 L -14 452 L -118 446 Z'
SLEEVE_F = 'M -100 134 C -136 138, -156 160, -160 214 L -112 220 C -112 190, -108 166, -100 150 Z'   # the picture's left
ARM_F = 'M -154 206 C -158 250, -160 300, -160 350 L -124 350 C -122 300, -120 250, -116 210 Z'
HAND_F = 'M -162 344 C -168 370, -164 392, -146 398 C -130 400, -120 384, -122 344 Z'
LEGS_X, LEG_W = 62, 25          # the legs' centres and half-width

# ---------------------------------------------------------------- profile (faces the picture's right)
HEAD_S = ('M -6 -106 C 44 -108, 86 -80, 92 -34 C 94 -14, 94 6, 94 28 C 100 34, 114 40, 114 50 C 114 58, 104 62, 95 60 '
          'C 95 68, 94 78, 90 88 C 84 104, 64 116, 40 116 L 28 114 L 30 152 L -36 152 L -38 100 '
          'C -72 90, -100 56, -104 6 C -108 -60, -60 -104, -6 -106 Z')
PLANE_S = ('M -6 -106 C 44 -108, 86 -80, 92 -34 C 94 -14, 94 6, 94 28 C 95 40, 95 50, 95 60 '
           'C 95 68, 94 78, 90 88 C 84 104, 64 116, 40 116 L 28 114 L 30 152 L -36 152 L -38 100 '
           'C -72 90, -100 56, -104 6 C -108 -60, -60 -104, -6 -106 Z')
EAR_S = 'M -2 0 C -30 -18, -52 6, -44 36 C -38 56, -16 60, -4 46 Z'
HAIR_S = ('M -110 20 C -124 -50, -84 -118, -18 -122 L -30 -150 L 0 -126 L 14 -156 L 30 -122 '
          'C 70 -118, 100 -92, 104 -52 L 122 -50 L 100 -38 C 92 -50, 80 -58, 66 -62 C 58 -44, 44 -30, 26 -22 '
          'C 18 -14, 14 -6, 12 2 L 8 22 L -6 0 C -18 -6, -30 -2, -40 8 C -50 22, -60 36, -72 46 L -76 66 L -92 44 '
          'C -102 38, -108 30, -110 20 Z')
SHIRT_S = ('M -30 124 C -62 130, -84 150, -86 186 C -88 240, -86 290, -82 338 L 90 338 '
           'C 96 290, 94 230, 86 186 C 80 150, 60 130, 34 124 C 14 134, -12 134, -30 124 Z')
SHORTS_S = 'M -82 316 L 90 316 L 80 446 L -72 446 Z'


def stripes(d):
    return clip(d, ''.join(F(f'M -200 {y} L 200 {y} L 200 {y + 12} L -200 {y + 12} Z', C['stripe']) for y in range(160, 340, 36)))


def shoe_side(x, y):
    """tim.py's sneaker (it is drawn from the side there too)."""
    sh = (f'M {x - 28} {y} L {x + 18} {y - 4} C {x + 46} {y}, {x + 66} {y + 14}, {x + 68} {y + 32} '
          f'L {x - 30} {y + 34} C {x - 34} {y + 20}, {x - 34} {y + 8}, {x - 28} {y} Z')
    return (F(sh, C['shoe'], C['shoeL'])
            + F(f'M {x - 32} {y + 28} L {x + 68} {y + 26} L {x + 68} {y + 38} C {x + 30} {y + 42}, {x - 10} {y + 42}, {x - 32} {y + 40} Z', C['sole'], C['shoeL'])
            + L(f'M {x - 4} {y + 2} L {x + 4} {y + 12} M {x + 8} {y} L {x + 16} {y + 10}', C['shoeL'], LW[0] * .8))


def sock(x, y, w=20):
    return (F(f'M {x - w} {y - 20} L {x + w} {y - 20} L {x + w} {y + 8} L {x - w} {y + 8} Z', C['sock'], '#9c8a76')
            + L(f'M {x - w} {y - 12} L {x + w} {y - 12}', '#d06a55', LW[0] * 1.4))


def figure_f(face_png=None):
    out = []
    for sx in (-1, 1):
        x = sx * LEGS_X
        leg = f'M {x - LEG_W - 2} 440 L {x + LEG_W + 2} 440 C {x + LEG_W + 2} 520, {x + LEG_W - 4} 580, {x + LEG_W - 6} 640 L {x - LEG_W + 6} 640 C {x - LEG_W + 4} 580, {x - LEG_W - 2} 520, {x - LEG_W - 2} 440 Z'
        out.append(shaded(leg, C['skin'], f'M {x - 40} 440 L {x - LEG_W + 8} 440 L {x - LEG_W + 12} 650 L {x - 40} 650 Z', C['shade'], C['line']))
        out.append(sock(x, 636))
        sh = f'M {x - 24} 644 C {x - 26} 628, {x + 26} 628, {x + 24} 644 C {x + 34} 652, {x + 34} 668, {x + 32} 672 L {x - 32} 672 C {x - 34} 668, {x - 34} 652, {x - 24} 644 Z'
        out.append(F(sh, C['shoe'], C['shoeL']))
        out.append(F(f'M {x - 34} 668 L {x + 34} 668 L {x + 34} 680 C {x + 12} 683, {x - 12} 683, {x - 34} 680 Z', C['sole'], C['shoeL']))
        out.append(L(f'M {x - 8} 640 L {x + 8} 648 M {x + 8} 640 L {x - 8} 648', C['shoeL'], LW[0] * .8))
    out.append(F('M -80 514 L -48 514 L -48 532 L -80 532 Z', C['plaster'], '#b08a55', LW[0] * .8))
    out.append(L('M -70 516 L -70 530 M -60 516 L -60 530', '#b08a55', LW[0] * .5))
    out.append(shaded(SHORTS_F, C['shorts'], 'M -130 316 L -84 316 L -90 460 L -130 460 Z', C['shortsS'], C['shortsL']))
    # arms hanging: the arm, the mitten, then the sleeve over them
    for m in (lambda d: d, mx):
        out.append(shaded(m(ARM_F), C['skin'], 'M -200 300 L 200 300 L 200 360 L -200 360 Z', C['shade'], C['line']))
        out.append(F(m(HAND_F), C['skin'], C['line']))
    out.append(F(SHIRT_F, C['shirt']))
    out.append(stripes(SHIRT_F))
    out.append(clip(SHIRT_F, F('M -140 120 C -108 200, -110 280, -92 340 L -140 340 Z', C['shirtL'], extra='opacity=".22"')))
    out.append(L(SHIRT_F, C['shirtL']))
    out.append(F('M -40 124 C -20 142, 20 142, 40 124 C 22 134, -22 134, -40 124 Z', C['shirtS'], C['shirtL']))
    for m in (lambda d: d, mx):
        out.append(F(m(SLEEVE_F), C['shirt'], C['shirtL']))
        out.append(clip(m(SLEEVE_F), F('M -200 176 L 200 176 L 200 188 L -200 188 Z', C['stripe'])))
    out.append(shaded(NECK_F, C['skin'], 'M -40 96 L 40 96 L 40 118 L -40 110 Z', C['shade'], C['line']))
    for m in (lambda d: d, mx):
        out.append(shaded(m(EAR_F), C['skin'], m('M -150 26 L -90 26 L -90 70 L -150 70 Z'), C['shade'], C['line']))
        out.append(L(m('M -116 8 C -128 16, -128 34, -116 42'), C['line'], LW[0] * .8))
    out.append(F(HEAD_F, C['skin']))
    out.append(clip(HEAD_F, F('M -120 -40 C -98 0, -94 60, -60 120 L -120 120 Z', C['shade'], extra='opacity=".55"'),
                    g(F(HAIR_F, C['shade']), 3, 9)))
    out.append(L(HEAD_F, C['line']))
    if face_png:
        b = base64.b64encode(open(face_png, 'rb').read()).decode()
        out.append(f'<image href="data:image/png;base64,{b}" x="-120" y="-130" width="240" height="260"/>')
    out.append(F(HAIR_F, C['hair']))
    out.append(clip(HAIR_F, F('M -70 -98 C -40 -116, 10 -124, 50 -112 C 20 -110, -10 -104, -34 -92 Z', C['hairH']),
                    F('M -124 -50 C -104 -66, -78 -62, -66 -52 L -66 10 L -124 10 Z', C['hairS'])))
    out.append(L(HAIR_F, C['hairL']))
    out.append(L('M -40 -100 C -50 -84, -56 -70, -58 -54', C['hairL'], LW[0] * .7))
    out.append(L('M 50 -104 C 66 -90, 74 -78, 78 -60', C['hairL'], LW[0] * .7))
    return ''.join(out)


def figure_s():
    out = []
    for x, y in ((8, 636), (-6, 640)):        # the far leg a little ahead
        leg = f'M {x - 27} 440 L {x + 27} 440 C {x + 27} 520, {x + 21} 580, {x + 19} {y + 4} L {x - 19} {y + 4} C {x - 21} 580, {x - 27} 520, {x - 27} 440 Z'
        out.append(shaded(leg, C['skin'], f'M {x - 40} 440 L {x - 15} 440 L {x - 11} 650 L {x - 40} 650 Z', C['shade'], C['line']))
        out.append(sock(x, y))
        out.append(shoe_side(x, y))
    out.append(shaded(SHORTS_S, C['shorts'], 'M -100 316 L -50 316 L -44 460 L -100 460 Z', C['shortsS'], C['shortsL']))
    out.append(F(SHIRT_S, C['shirt']))
    out.append(stripes(SHIRT_S))
    out.append(clip(SHIRT_S, F('M -110 120 C -78 200, -80 280, -62 340 L -110 340 Z', C['shirtL'], extra='opacity=".22"')))
    out.append(L(SHIRT_S, C['shirtL']))
    # the near arm hangs over the side
    arm = 'M -18 206 C -20 250, -20 300, -18 350 L 18 350 C 20 300, 20 250, 18 206 Z'
    out.append(shaded(arm, C['skin'], 'M -40 206 L -8 206 L -6 360 L -40 360 Z', C['shade'], C['line']))
    out.append(F('M -20 344 C -24 370, -18 394, 0 398 C 18 396, 24 370, 20 344 Z', C['skin'], C['line']))
    slv = 'M -26 140 C -30 170, -30 196, -28 216 L 28 216 C 30 196, 30 170, 26 140 C 10 130, -10 130, -26 140 Z'
    out.append(F(slv, C['shirt'], C['shirtL']))
    out.append(clip(slv, F('M -200 176 L 200 176 L 200 188 L -200 188 Z', C['stripe'])))
    out.append(F(HEAD_S, C['skin']))
    out.append(clip(HEAD_S, F('M -120 -40 C -90 10, -60 80, 20 120 L 40 160 L -120 160 Z', C['shade'], extra='opacity=".55"'),
                    g(F(HAIR_S, C['shade']), 3, 9),
                    f'<ellipse cx="46" cy="60" rx="20" ry="13" fill="{C["blush"]}" opacity=".5"/>'))
    out.append(L(HEAD_S, C['line']))
    for x, y in ((56, 44), (66, 48), (46, 50)):
        out.append(f'<circle cx="{x}" cy="{y}" r="2" fill="#c06e52" opacity=".7"/>')
    out.append(eye(68, 14, 12, 25, C, look=(3, 0), lid=.32, lidtilt=3, ir=15, sq=.6, flick=-1, lash=1.8, wing=False))
    out.append(brow(88, -24, 54, -22, 6, 7, C['hairL']))
    out.append(F('M 14 40 L 50 32 L 54 48 L 18 56 Z', C['plaster'], '#b08a55', LW[0] * .8))
    out.append(L('M 28 40 L 30 50 M 38 38 L 40 48', '#b08a55', LW[0] * .6))
    grin = 'M 56 76 C 68 82, 82 80, 93 70 C 94 84, 86 98, 74 98 C 64 98, 58 88, 56 76 Z'
    out.append(F(grin, '#6e2620', C['line']) + clip(grin, F('M 50 66 L 100 60 L 100 80 C 84 86, 66 88, 50 82 Z', '#fff'),
                                                    '<ellipse cx="78" cy="100" rx="14" ry="8" fill="#de6e64"/>'))
    out.append(shaded(EAR_S, C['skin'], 'M -60 28 L 10 28 L 10 70 L -60 70 Z', C['shade'], C['line']))
    out.append(L('M -16 8 C -30 14, -32 32, -20 40', C['line'], LW[0] * .8))
    out.append(F(HAIR_S, C['hair']))
    out.append(clip(HAIR_S, F('M -60 -100 C -30 -118, 20 -122, 56 -108 C 26 -108, -4 -104, -28 -92 Z', C['hairH']),
                    F('M -130 -40 C -110 -60, -84 -50, -70 -30 L -60 70 L -130 70 Z', C['hairS'])))
    out.append(L(HAIR_S, C['hairL']))
    out.append(L('M -50 -100 C -66 -80, -74 -50, -74 -20', C['hairL'], LW[0] * .7))
    return ''.join(out)


def sheet(face_png=None):
    """The turnaround, laid out as the style's own (styles/s3-graphic/tools/build.py: turnaround)."""
    W, H, INK = 1500, 1000, '#3a2e2a'
    tall = FLOOR - CROWN; s = 760 / tall; gy = 900; top = gy - tall * s
    body = ''
    for y in (top, gy - (FLOOR - 116) * s, gy):
        body += L(f'M 40 {y:.1f} L {W - 40} {y:.1f}', '#b9a993', 1.4, 'stroke-dasharray="8 8"')
    views = ((figure_f(face_png), 'анфас (дорисован здесь)'), (tim.figure_q(), 'три четверти (рисунок стиля)'), (figure_s(), 'профиль (дорисован здесь)'))
    for i, (fig, lab) in enumerate(views):
        x = 260 + i * 490
        body += f'<ellipse cx="{x}" cy="{gy}" rx="120" ry="12" fill="#000" opacity=".1"/>'
        body += g(fig, x, gy - FLOOR * s, s)
        body += text(x, 970, lab, 26, INK)
    body += text(40, 50, 'Тим — поворот', 30, INK, 'start')
    return svg(W, H, body, '#f1e6d6')


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    fp = os.path.join(out, 'face-mischief.png')
    open(os.path.join(out, 'turnaround-tim.svg'), 'w').write(sheet(fp if os.path.exists(fp) else None))
