"""Марат, about 35, a cook: huge, loud, merry, generous. A wide heavy head on a short neck, short dark curls, a
thick black beard and moustache as big masses, thick brows, a broad nose, dark eyes narrowed by the cheeks; his
resting face is a wide smile with teeth. A white cook's jacket with rolled sleeves, a long terracotta apron, a towel
over the shoulder, a ladle."""
import math
from kit import mix
from parts import eye, eye_side, brow, INK

SKIN = '#dc9c76'
HAIR = '#1e181e'
JACKET = '#ece2d2'
APRON = '#c2603a'
TOWEL = '#d8703e'
TROUS = '#3a3644'
ROSE = '#d2584a'
STEEL = '#9aa0a8'
SHEEN = '#8a7c94'   # the cool light on black hair

EXPR = {
    'calm':     dict(lid=0.26, low=0.3, brows=(0, 0), mouth='smile', look=(-0.3, 0.0)),
    'joy':      dict(shut=True, brows=(-6, -6), mouth='laugh'),
    'surprise': dict(lid=0.0, low=0.0, brows=(-18, -16), mouth='o', look=(-0.15, 0.0)),
    'sad':      dict(lid=0.5, low=0.1, brows=(4, 4), mouth='sad', look=(-0.15, 0.4), sad=True),
    'anger':    dict(lid=0.36, low=0.2, brows=(10, 9), mouth='angry', look=(-0.35, 0.05), angry=True),
}


def bumps(pts, amp, curl=0):
    """A curly edge through pts: each span bulges to the left of the direction of travel by amp (to the right if
    amp < 0). curl > 0: every span is a round arc instead (radius = span * curl; 0.5 is a half circle) — a row of
    curls. Returns path commands that start with L to the first point."""
    s = [f'L{pts[0][0]:.1f},{pts[0][1]:.1f}']
    n = len(pts)
    for i in range(n - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy) or 1
        if curl:
            r = ln * curl
            s.append(f'A{r:.1f},{r:.1f} 0 0,{1 if amp < 0 else 0} {x1:.1f},{y1:.1f}')
            continue
        nx, ny = dy / ln, -dx / ln
        s.append(f'Q{(x0 + x1) / 2 + nx * amp * 2:.1f},{(y0 + y1) / 2 + ny * amp * 2:.1f} {x1:.1f},{y1:.1f}')
    return ' '.join(s)


def smile_eye(d, cx, cy, rx, ry, o=1, skin=SKIN):
    """An eye shut by laughter: the lash line as an arch, the cheek pushed up under it, laugh lines at the outer
    corner (o = +1: the outer corner is on the right)."""
    xo, xi = cx + o * rx, cx - o * rx
    s = [f'<path d="M{xi},{cy + ry*0.35} C{cx - o*rx*0.5},{cy - ry*0.75} {cx + o*rx*0.5},{cy - ry*0.8} {xo + o*3},{cy + ry*0.3} '
         f'L{xo + o*8},{cy + ry*0.05} C{cx + o*rx*0.5},{cy - ry*1.15} {cx - o*rx*0.5},{cy - ry*1.05} {xi - o*1.5},{cy + ry*0.3}Z" fill="{INK}"/>']
    w = mix(skin, INK, 0.45)
    s.append(f'<path d="M{xi + o*rx*0.2},{cy + ry*0.95} C{cx},{cy + ry*0.55} {cx + o*rx*0.6},{cy + ry*0.6} {xo},{cy + ry*0.95}" '
             f'fill="none" stroke="{w}" stroke-width="1.5" stroke-linecap="round" opacity="0.8"/>')
    if rx > 10:
        s.append(f'<path d="M{xo + o*8},{cy - ry*0.25} L{xo + o*16},{cy - ry*0.75} M{xo + o*9},{cy + ry*0.3} L{xo + o*18},{cy + ry*0.3} '
                 f'M{xo + o*8},{cy + ry*0.8} L{xo + o*15},{cy + ry*1.3}" fill="none" stroke="{w}" stroke-width="1.4" stroke-linecap="round" opacity="0.8"/>')
    return '\n'.join(s)


def thick_brow(p0, p1, p2, w, col=HAIR):
    """A heavy brow: a thick tapered mass with a blunt inner end."""
    (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2
    return (f'<path d="M{x0},{y0 - w*0.55} Q{x1},{y1 - w*0.95} {x2},{y2} Q{x1},{y1 + w*0.35} {x0},{y0 + w*0.55}Z" '
            f'fill="{col}" stroke="{col}" stroke-width="2" stroke-linejoin="round"/>')


def mouth(d, kind, x0=186, x1=300, y=362):
    """The mouth inside the beard, between x0 (far corner) and x1 (near corner). Teeth and a tongue in every open one."""
    dark, teeth, tongue, lip = '#3a141c', '#f6eee2', '#c8525c', '#b8605a'
    xm = x0 + (x1 - x0) * 0.44
    w = x1 - x0
    if kind == 'smile':   # the resting wide smile: the upper teeth, a dark slit under them
        return '\n'.join([
            f'<path d="M{x0},{y-2} C{x0+w*0.25},{y+4} {x0+w*0.7},{y+4} {x1},{y-8} C{x1-4},{y+18} {x0+w*0.72},{y+36} {xm},{y+36} C{x0+w*0.2},{y+36} {x0+4},{y+22} {x0},{y-2}Z" fill="{dark}"/>',
            f'<path d="M{x0+3},{y} C{x0+w*0.25},{y+5} {x0+w*0.7},{y+5} {x1-3},{y-5} C{x1-8},{y+10} {x0+w*0.7},{y+24} {xm},{y+24} C{x0+w*0.22},{y+24} {x0+8},{y+14} {x0+3},{y}Z" fill="{teeth}"/>',
            d.tone(f'M{x0+w*0.2},{y+40} C{x0+w*0.35},{y+46} {x0+w*0.6},{y+46} {x0+w*0.74},{y+38} C{x0+w*0.6},{y+52} {x0+w*0.34},{y+52} {x0+w*0.2},{y+40}Z', lip, 0.9, 1.2)])
    if kind == 'laugh':   # head-back laughter: wide open, upper teeth, lower teeth, the tongue
        return '\n'.join([
            f'<path d="M{x0-2},{y-4} C{x0+w*0.25},{y+4} {x0+w*0.7},{y+4} {x1+2},{y-12} C{x1+2},{y+30} {x0+w*0.76},{y+70} {xm},{y+70} C{x0+w*0.18},{y+70} {x0-2},{y+36} {x0-2},{y-4}Z" fill="{dark}"/>',
            f'<path d="M{x0+2},{y-1} C{x0+w*0.25},{y+5} {x0+w*0.7},{y+5} {x1-2},{y-8} C{x1-6},{y+8} {x0+w*0.7},{y+21} {xm},{y+21} C{x0+w*0.22},{y+21} {x0+6},{y+12} {x0+2},{y-1}Z" fill="{teeth}"/>',
            f'<path d="M{x0+w*0.16},{y+52} C{x0+w*0.3},{y+34} {x0+w*0.62},{y+32} {x0+w*0.8},{y+46} C{x0+w*0.7},{y+66} {x0+w*0.56},{y+68} {xm},{y+68} C{x0+w*0.3},{y+68} {x0+w*0.2},{y+62} {x0+w*0.16},{y+52}Z" fill="{tongue}"/>',
            f'<path d="M{x0+w*0.3},{y+46} C{x0+w*0.42},{y+42} {x0+w*0.5},{y+44} {x0+w*0.62},{y+48}" fill="none" stroke="#9a3444" stroke-width="1.6" stroke-linecap="round"/>',
            d.tone(f'M{x0+w*0.2},{y+74} C{x0+w*0.35},{y+80} {x0+w*0.6},{y+80} {x0+w*0.74},{y+72} C{x0+w*0.6},{y+86} {x0+w*0.34},{y+86} {x0+w*0.2},{y+74}Z', lip, 0.9, 1.2)])
    if kind == 'o':
        a, b = xm - w*0.2, xm + w*0.2
        return '\n'.join([
            f'<path d="M{a},{y+10} C{a+4},{y-4} {b-4},{y-6} {b},{y+8} C{b+4},{y+34} {b-8},{y+52} {xm},{y+52} C{a+6},{y+52} {a-4},{y+34} {a},{y+10}Z" fill="{dark}"/>',
            f'<path d="M{a+4},{y+6} C{a+10},{y-1} {b-10},{y-2} {b-4},{y+5} C{b-10},{y+12} {a+10},{y+13} {a+4},{y+6}Z" fill="{teeth}"/>',
            f'<path d="M{a+6},{y+40} C{a+14},{y+30} {b-14},{y+30} {b-6},{y+38} C{b-10},{y+50} {a+12},{y+52} {a+6},{y+40}Z" fill="{tongue}"/>'])
    if kind == 'sad':
        return '\n'.join([
            f'<path d="M{x0+14},{y+16} C{x0+w*0.3},{y+2} {x0+w*0.62},{y} {x1-16},{y+12}" fill="none" stroke="{dark}" stroke-width="2.6" stroke-linecap="round"/>',
            d.tone(f'M{x0+w*0.24},{y+14} C{x0+w*0.38},{y+9} {x0+w*0.56},{y+9} {x0+w*0.7},{y+13} C{x0+w*0.56},{y+24} {x0+w*0.36},{y+24} {x0+w*0.24},{y+14}Z', lip, 0.95, 1.2)])
    if kind == 'angry':   # teeth clenched and bared
        return '\n'.join([
            f'<path d="M{x0+8},{y+6} C{x0+w*0.3},{y-4} {x0+w*0.66},{y-6} {x1-8},{y+2} C{x1-10},{y+24} {x0+w*0.66},{y+30} {xm},{y+30} C{x0+w*0.24},{y+30} {x0+10},{y+26} {x0+8},{y+6}Z" fill="{dark}"/>',
            f'<path d="M{x0+12},{y+8} C{x0+w*0.3},{y} {x0+w*0.66},{y-2} {x1-12},{y+5} C{x1-14},{y+20} {x0+w*0.66},{y+25} {xm},{y+25} C{x0+w*0.24},{y+25} {x0+14},{y+22} {x0+12},{y+8}Z" fill="{teeth}"/>',
            f'<path d="M{x0+13},{y+15} C{x0+w*0.3},{y+11} {x0+w*0.66},{y+10} {x1-13},{y+13}" fill="none" stroke="{dark}" stroke-width="1.6"/>',
            d.tone(f'M{x0+w*0.24},{y+34} C{x0+w*0.38},{y+38} {x0+w*0.58},{y+38} {x0+w*0.72},{y+32} C{x0+w*0.58},{y+44} {x0+w*0.36},{y+44} {x0+w*0.24},{y+34}Z', lip, 0.9, 1.2)])
    raise ValueError(kind)


def _beard_tones(d, right=True):
    t = d.tone('M330,240 C352,300 352,384 330,434 C310,474 280,490 250,494 L410,500 L410,230Z', '#0c080e', 0.6, 8)
    t += d.tone('M184,350 C186,396 202,440 236,466 C212,452 194,414 190,372Z', SHEEN, 0.8, 4)
    t += d.tone('M214,420 C232,440 262,446 290,436 C268,452 234,452 214,420Z', SHEEN, 0.45, 5)
    return t


def head34(d, out, expr='calm'):
    e = EXPR[expr]
    sk = mix(SKIN, '#4a1838', 0.6)
    laugh = e['mouth'] == 'laugh'
    # neck: short and thick, almost hidden by the beard
    neck = 'M250,400 L250,444 L382,448 C374,420 370,390 372,340Z'
    out.append(d.form(neck, SKIN, shift=10, soft=4, extra=d.tone('M240,380 L390,330 L400,500 L240,500Z', sk, 0.9, 4)))
    # face: wide, heavy; the far cheek pushed out by the smile
    face = ('M198,168 C222,124 304,116 346,150 C374,176 382,224 374,268 C370,310 362,350 346,384 '
            'C328,420 292,444 256,446 C226,446 204,430 194,404 C184,376 178,340 180,312 '
            'C176,296 176,278 182,258 C180,226 186,196 198,168Z')
    fx = [d.tone('M320,140 C346,190 342,240 332,280 C322,320 316,360 298,400 C284,424 268,438 252,446 L390,450 L390,130Z', sk, 0.85, 4),
          d.tone('M236,250 C252,238 294,240 308,256 C304,276 266,282 244,274Z', '#7a3048', 0.4, 5),
          d.tone('M190,248 C198,242 214,244 220,254 C216,268 200,268 192,262Z', '#7a3048', 0.3, 4),
          d.tone('M250,292 C266,276 310,280 318,304 C310,326 270,328 254,314Z', ROSE, 0.55, 8),
          d.tone('M178,296 C186,288 200,292 200,306 C196,318 182,318 178,310Z', ROSE, 0.5, 5),
          # the hair's cast shadow on the forehead
          d.tone('M186,214 C214,204 250,196 290,200 C314,204 334,222 346,250 L390,250 L390,120 L180,120Z', '#8a3a40', 0.32, 6)]
    out.append(d.form(face, SKIN, shift=30, soft=9, s=0.5, rim=2.4, rimcol='#ffb48a', rimop=0.6, extra='\n'.join(fx)))
    # beard: one big mass round the jaw, a curly lower edge
    low = [(176, 318), (172, 352), (176, 388), (188, 424), (208, 456), (236, 478), (268, 486), (300, 480), (330, 462),
           (354, 434), (370, 400), (380, 362), (382, 322), (378, 286), (366, 250)]
    dy = 14 if laugh else 0   # the jaw drops with the laugh
    low = [(x, y + dy * max(0, min(1, (y - 330) / 100))) for x, y in low]
    beard = ('M338,244 C336,274 328,298 310,314 C294,326 276,324 258,330 L198,332 C190,332 182,326 '
             + bumps(low, -3.2)[1:] + ' Z')
    out.append(d.form(beard, HAIR, shift=14, soft=5, k=0.12, s=0.35, extra=_beard_tones(d), rim=2.5, rimcol='#b08a88', rimop=0.55))
    hl = mix(HAIR, SHEEN, 0.6)
    out.append(f'<path d="M200,380 C204,410 216,436 236,452 M226,392 C230,416 242,436 258,446 M300,340 C316,352 328,372 330,398 M286,400 C296,416 298,436 290,452" '
               f'fill="none" stroke="{hl}" stroke-width="1.6" stroke-linecap="round" opacity="0.55"/>')
    # the cheek rides over the beard's upper edge when he smiles
    out.append(d.tone('M262,318 C282,312 304,304 318,288 C312,312 290,326 262,328Z', mix(SKIN, ROSE, 0.35), 0.0 if e.get('sad') else 0.55, 3))
    # ear
    ear = 'M334,256 C348,240 370,246 372,270 C374,294 364,316 350,324 C340,328 334,320 336,310 C328,294 328,274 334,256Z'
    ex = d.tone('M344,266 C354,258 362,266 360,284 C358,298 350,306 346,300 C350,290 348,276 344,266Z', sk, 0.8, 1.5)
    out.append(d.form(ear, SKIN, shift=8, soft=3, s=0.55, extra=ex))
    # eyes: dark, narrowed from below by the cheeks
    if e.get('shut'):
        out.append(smile_eye(d, 272, 264, 17, 12, 1))
        out.append(smile_eye(d, 208, 260, 9, 11, -1))
    else:
        out.append(eye(d, 272, 262, 16.5, 14, lid=e['lid'], look=e['look'], tilt=1, skin=SKIN, iris='#3a2218', crease=0.35,
                       low_lid=e['low'], irr=0.86))
        out.append(eye(d, 208, 258, 9, 13, lid=e['lid'], look=e['look'], tilt=0, skin=SKIN, iris='#3a2218', wing=-0.3,
                       crease=0, lower=0.3, low_lid=e['low'], irr=0.86))
        if e['low'] > 0.25:
            w = mix(SKIN, INK, 0.45)
            out.append(f'<path d="M296,256 L304,251 M297,264 L306,264 M295,271 L303,276" fill="none" stroke="{w}" stroke-width="1.3" stroke-linecap="round" opacity="0.7"/>')
    # brows: thick black masses
    bn, bf = e['brows']
    if e.get('sad'):
        out.append(thick_brow((244, 228 + bn), (268, 226 + bn), (304, 244 + bn), 10))
        out.append(thick_brow((228, 228 + bf), (210, 228 + bf), (188, 242 + bf), 8))
    elif e.get('angry'):
        out.append(thick_brow((242, 242 + bn), (270, 226 + bn), (306, 222 + bn), 11))
        out.append(thick_brow((230, 242 + bf), (210, 230 + bf), (188, 226 + bf), 9))
    else:
        out.append(thick_brow((244, 236 + bn), (272, 218 + bn), (306, 234 + bn), 10))
        out.append(thick_brow((228, 234 + bf), (208, 220 + bf), (188, 234 + bf), 8))
    # mouth, then the moustache over its upper edge
    out.append(mouth(d, e['mouth']))
    up = -6 if e['mouth'] in ('smile', 'laugh') else (6 if e.get('sad') else 0)   # the tips rise with the smile
    mo = (f'M216,338 C234,328 264,330 286,342 C300,350 312,{350+up} 322,{340+up} C320,{360+up} 304,372 284,370 '
          f'C262,368 240,362 216,362 C204,362 192,368 180,{366+up*0.5} C172,{364+up*0.5} 166,{354+up} 166,{344+up} '
          f'C174,{350+up} 184,348 192,342 C200,338 208,336 216,338Z')
    mx = d.tone('M222,340 C240,334 262,336 280,344 C262,342 240,344 224,348Z', SHEEN, 0.7, 2)
    out.append(d.form(mo, HAIR, shift=8, soft=3, k=0.12, s=0.3, extra=mx))
    # nose: broad, a wide wing
    nose = ('M228,250 C226,272 212,290 196,300 C178,306 166,320 172,334 C178,346 196,348 210,342 '
            'C224,348 244,346 250,332 C254,318 246,306 238,298 C244,282 246,266 242,250Z')
    nx = d.tone('M172,334 C178,346 196,348 210,342 C224,348 244,346 250,332 L256,356 L168,356Z', '#5a1830', 0.55, 2)
    nx += d.tone('M200,306 C214,300 232,306 238,318 C226,314 210,314 200,318Z', '#fff0e0', 0.25, 3)
    out.append(d.form(nose, mix(SKIN, ROSE, 0.2), shift=12, soft=4, s=0.45, extra=nx))
    out.append(d.tone('M184,312 C190,306 198,306 202,310 C196,314 188,316 184,312Z', '#fff4e8', 0.8, 1))
    out.append(f'<path d="M226,336 C232,330 240,330 244,336" fill="none" stroke="{mix(SKIN, INK, 0.6)}" stroke-width="1.8" stroke-linecap="round"/>')
    # hair: a cap of short curls
    outer = [(192, 208), (180, 176), (190, 142), (214, 116), (246, 94), (282, 84), (322, 90), (352, 106), (380, 134),
             (396, 170), (400, 208), (392, 244), (376, 274)]
    inner = [(376, 274), (360, 252), (340, 250), (330, 224), (312, 200), (286, 190), (262, 176), (236, 186), (214, 180),
             (192, 208)]
    hair = 'M192,208 ' + bumps(outer, -1, 0.62) + ' ' + bumps(inner, -1, 0.75) + ' Z'
    hx = d.tone('M222,112 C250,98 292,94 326,102 C296,104 256,112 232,128Z', SHEEN, 0.5, 5)
    hx += d.tone('M330,100 C372,130 396,200 380,280 L420,280 L420,90Z', '#0c080e', 0.6, 8)
    out.append(d.form(hair, HAIR, shift=10, soft=4, k=0.12, s=0.35, extra=hx, rim=2.5, rimcol='#b08a88', rimop=0.6))
    # a few curls drawn as short hooks
    out.append(f'<path d="M230,140 C238,130 250,130 254,140 M270,124 C278,114 292,116 294,126 M310,140 C320,132 332,136 332,146 '
               f'M250,160 C258,152 270,154 272,162 M340,180 C350,174 360,180 358,190 M290,160 C298,152 310,156 310,164" '
               f'fill="none" stroke="{hl}" stroke-width="1.8" stroke-linecap="round" opacity="0.5"/>')


def bust(d, out):
    """Shoulders for the portrait: far wider than the frame of anyone else, the white jacket, a neckerchief."""
    sh = '#2a1e40'
    body = ('M10,700 L26,612 C40,548 98,506 182,488 L250,476 C300,470 352,474 384,484 '
            'C444,500 488,548 496,612 L502,700Z')
    bx = d.tone('M356,476 C420,520 452,610 458,700 L520,700 L520,460Z', sh, 0.5, 10)
    bx += d.tone('M70,590 C92,548 132,520 180,506 C142,530 110,560 92,600Z', '#fff6e4', 0.7, 5)
    out.append(d.form(body, JACKET, shift=34, soft=10, k=0.25, s=0.5, extra=bx))
    fold = mix(JACKET, '#4a3a5a', 0.45)
    # the double-breasted front and its buttons
    out.append(f'<path d="M214,520 C204,580 200,640 202,700 M322,514 C330,580 334,640 334,700" fill="none" stroke="{fold}" stroke-width="1.8" opacity="0.7"/>')
    for x, y in ((228, 600), (226, 660), (306, 596), (308, 656)):
        out.append(d.form(f'M{x-7},{y} a7,7 0 1,0 14,0 a7,7 0 1,0 -14,0Z', mix(JACKET, '#8a7a70', 0.35), shift=3, soft=1.2))


    # the jacket's stand collar under the beard
    col = 'M226,494 C256,478 330,476 376,490 L380,520 C332,508 262,510 228,526Z'
    out.append(d.form(col, JACKET, shift=10, soft=4, k=0.25, s=0.5, extra=d.tone('M340,480 L390,480 L390,530 L340,530Z', sh, 0.4, 5)))
    out.append(f'<path d="M228,526 C262,510 332,508 380,520" fill="none" stroke="{fold}" stroke-width="1.6" opacity="0.7"/>')
    # the towel over the near shoulder
    towel = 'M352,484 C380,478 414,488 432,506 C440,560 444,630 446,700 L378,700 C378,630 372,560 352,484Z'
    tx = d.tone('M410,490 L460,500 L460,700 L420,700Z', '#2a1030', 0.4, 6)
    out.append(d.form(towel, TOWEL, shift=14, soft=5, s=0.5, extra=tx))
    st = mix(TOWEL, '#fff0dc', 0.75)
    out.append(f'<path d="M374,566 C396,560 420,562 438,570 M377,586 C398,580 422,582 440,590" fill="none" stroke="{st}" stroke-width="5" opacity="0.85"/>')


def _fist(d, out, cx, cy, r, rot=0):
    """A big closed hand: a block of four fingers with the knuckle lines and the thumb laid across."""
    g = f'<g transform="translate({cx},{cy}) rotate({rot}) scale({r/20})">'
    out.append(g)
    hand = 'M-20,-8 C-20,-18 -8,-22 4,-20 C16,-20 22,-12 22,-2 C22,10 16,18 4,20 C-8,22 -20,16 -22,6Z'
    out.append(d.form(hand, SKIN, shift=6, soft=2.5, s=0.5))
    fl = mix(SKIN, INK, 0.5)
    out.append(f'<path d="M-6,-19 C-2,-10 -2,-2 -6,6 M4,-20 C8,-10 8,0 4,8 M13,-17 C17,-9 17,0 13,7" fill="none" stroke="{fl}" stroke-width="1.6" stroke-linecap="round"/>')
    thumb = 'M-20,2 C-12,-4 0,2 6,10 C8,16 4,20 -2,20 C-10,18 -18,12 -20,2Z'
    out.append(d.form(thumb, SKIN, shift=4, soft=2, s=0.45))
    out.append('</g>')


def figure(d, out, expr='joy'):
    """Full figure: the tallest and by far the widest, ~4.8 heads with the beard. Laughing: the body leans back in
    one arc, the belly forward, the head thrown back; the ladle held up, the other fist on the hip."""
    from common import place
    sh = '#2a1e40'
    fold = mix(JACKET, '#4a3a5a', 0.45)
    out.append(d.tone('M110,846 C170,830 350,830 410,846 C350,862 170,862 110,846Z', '#140c22', 0.6, 4))
    # legs set wide, big clogs
    out.append(d.form('M176,520 C172,640 178,730 186,812 L238,812 C238,730 244,650 252,540Z', TROUS, shift=12, soft=4, s=0.5))
    out.append(d.form('M262,540 C270,650 282,730 290,812 L340,812 C344,720 350,630 356,520Z', TROUS, shift=12, soft=4, s=0.6))
    shoe = '#3a2a26'
    out.append(d.form('M182,802 L240,802 C246,818 246,834 242,846 L158,846 C148,838 154,822 174,816Z', shoe, shift=7, soft=2.5))
    out.append(d.form('M286,802 L342,802 C350,818 352,834 348,846 L270,846 C264,838 270,822 284,816Z', shoe, shift=7, soft=2.5))
    out.append('<g transform="translate(0,-14)">')
    # the far arm, raised: a rolled sleeve, a thick forearm
    far = 'M200,206 C160,208 122,238 96,278 C88,292 92,308 106,316 C120,322 136,320 144,310 C160,288 182,268 204,258Z'
    out.append(d.form(far, JACKET, shift=12, soft=4, k=0.25, s=0.5))
    fore = 'M82,292 C66,258 62,224 72,190 L116,188 C120,222 128,256 140,290 C128,312 96,314 82,292Z'
    out.append(d.form(fore, SKIN, shift=10, soft=3.5, s=0.5))
    out.append(d.form('M80,276 C96,262 126,266 142,284 L138,314 C120,324 96,320 82,304Z', mix(JACKET, '#8a7a80', 0.18), shift=6, soft=2.5, k=0.25, s=0.5))
    # the ladle: the handle through the fist, the bowl up
    out.append(f'<path d="M100,236 L84,74" stroke="{mix(STEEL, "#2a2030", 0.3)}" stroke-width="8" stroke-linecap="round"/>')
    out.append(f'<path d="M98,232 L83,76" stroke="{mix(STEEL, "#ffffff", 0.5)}" stroke-width="2.4" stroke-linecap="round"/>')
    bowl = 'M48,48 C50,78 72,94 96,90 C116,86 126,66 122,40 C100,48 70,52 48,48Z'
    out.append(d.form(bowl, STEEL, shift=10, soft=3.5, k=0.35, s=0.5))
    out.append(f'<path d="M48,48 C60,38 110,30 122,40 C110,50 60,56 48,48Z" fill="{mix(STEEL, "#2a2030", 0.45)}"/>')
    out.append(d.tone('M56,60 C60,72 68,80 78,84 C68,76 62,68 60,58Z', '#ffffff', 0.7, 1.2))
    _fist(d, out, 94, 172, 26, rot=-96)
    # the barrel of the body in the white jacket
    torso = ('M214,196 C176,202 150,222 140,262 C128,310 128,380 142,440 C150,490 160,530 170,566 L362,566 '
             'C376,520 388,470 394,420 C402,360 404,290 392,246 C382,214 350,196 310,192 C280,188 244,190 214,196Z')
    tx = d.tone('M330,190 C380,240 392,340 380,440 C372,500 364,540 360,570 L430,570 L430,180Z', sh, 0.5, 8)
    tx += d.tone('M152,270 C150,320 152,370 160,410 L172,408 C166,368 164,320 168,274Z', '#fff8e8', 0.7, 5)
    out.append(d.form(torso, JACKET, shift=30, soft=9, k=0.25, s=0.5, extra=tx, rim=2.5, rimcol='#f0c8a0', rimop=0.6))
    out.append(f'<path d="M226,214 C212,270 208,340 214,410 M312,206 C322,270 326,340 322,410" fill="none" stroke="{fold}" stroke-width="1.8" opacity="0.7"/>')
    for x, y in ((236, 262), (232, 322), (232, 382), (302, 258), (304, 318), (304, 378)):
        out.append(d.form(f'M{x-6},{y} a6,6 0 1,0 12,0 a6,6 0 1,0 -12,0Z', mix(JACKET, '#8a7a70', 0.35), shift=3, soft=1.2))
    # the long apron
    apron = 'M138,416 C134,500 138,610 150,716 C200,732 290,732 346,714 C360,610 382,500 398,408 C310,430 210,432 138,416Z'
    ax = d.tone('M300,420 C330,500 340,620 340,720 L400,720 L400,400Z', sh, 0.5, 7)
    ax += d.tone('M138,416 C210,432 310,430 398,408 L396,438 C310,456 210,458 138,444Z', mix(APRON, '#3a1020', 0.5), 0.75, 2)
    ax += d.tone('M154,480 C152,540 156,600 162,650 L176,648 C170,600 168,540 170,482Z', mix(APRON, '#ffd8a0', 0.5), 0.55, 4)
    out.append(d.form(apron, APRON, shift=26, soft=8, s=0.55, extra=ax))
    af = mix(APRON, '#2a0a18', 0.45)
    out.append(f'<path d="M216,470 C210,560 212,650 220,724 M286,468 C292,560 292,650 286,722" fill="none" stroke="{af}" stroke-width="1.8" opacity="0.6"/>')
    out.append(f'<path d="M398,408 C382,500 360,610 346,714" fill="none" stroke="{mix(APRON, "#2a1838", 0.6)}" stroke-width="2.4"/>')
    # the near arm: the elbow out, the fist on the hip
    upper = 'M352,200 C392,204 420,236 432,282 C440,308 444,332 442,354 C430,370 404,370 390,354 C390,322 382,290 362,262Z'
    out.append(d.form(upper, JACKET, shift=16, soft=5, k=0.25, s=0.55,
                      extra=d.tone('M410,220 C440,270 452,320 446,372 L470,372 L470,200Z', sh, 0.5, 5)))
    fore2 = 'M394,342 C412,334 438,342 444,360 C436,394 414,422 386,440 L362,412 C382,396 392,372 394,342Z'
    out.append(d.form(fore2, SKIN, shift=12, soft=4, s=0.55,
                      extra=d.tone('M430,340 C450,370 430,420 392,446 L460,446 L460,330Z', mix(SKIN, '#4a1838', 0.6), 0.7, 4)))
    out.append(d.form('M388,330 C406,320 436,326 448,346 L442,372 C426,362 404,362 388,372Z', mix(JACKET, '#8a7a80', 0.18), shift=6, soft=2.5, k=0.25, s=0.55))
    _fist(d, out, 368, 428, 24, rot=150)
    # collar, then the head thrown back
    col = 'M234,190 C258,178 318,176 346,190 L348,216 C316,206 264,206 236,218Z'
    out.append(d.form(col, JACKET, shift=8, soft=3, k=0.25, s=0.5))
    place(d, out, head34, 'marat', (272, 202), 0.46, rot=5, expr=expr)
    # the towel over the near shoulder
    towel = 'M338,190 C358,182 384,190 396,206 C400,250 400,300 396,338 L354,342 C358,300 356,250 338,190Z'
    out.append(d.form(towel, TOWEL, shift=10, soft=4, s=0.5, extra=d.tone('M382,196 L410,200 L410,340 L386,340Z', '#2a1030', 0.4, 4)))
    st = mix(TOWEL, '#fff0dc', 0.75)
    out.append(f'<path d="M356,306 C370,302 386,302 397,306 M356,318 C370,314 386,314 397,318" fill="none" stroke="{st}" stroke-width="3.4" opacity="0.85"/>')
    out.append('</g>')


def _curl_marks(pts, hl):
    return ('<path d="' + ' '.join(f'M{x},{y} C{x+8},{y-10} {x+20},{y-10} {x+24},{y}' for x, y in pts)
            + f'" fill="none" stroke="{hl}" stroke-width="1.8" stroke-linecap="round" opacity="0.5"/>')


def head_front(d, out, expr='calm'):
    e = EXPR[expr]
    sk = mix(SKIN, '#4a1838', 0.6)
    hl = mix(HAIR, SHEEN, 0.6)
    neck = 'M186,400 L186,446 L314,446 L314,400Z'
    out.append(d.form(neck, SKIN, shift=10, soft=4, extra=d.tone('M180,380 L320,380 L320,460 L180,460Z', sk, 0.85, 4)))
    for flip in (-1, 1):
        ear = (f'M{250+flip*86},{254} C{250+flip*102},{238} {250+flip*120},{248} {250+flip*120},{274} '
               f'C{250+flip*120},{300} {250+flip*108},{320} {250+flip*88},{318}Z')
        out.append(d.form(ear, SKIN, shift=6, soft=2.5, s=0.5 if flip < 0 else 0.62,
                          extra=d.tone(f'M{250+flip*96},{264} C{250+flip*108},{256} {250+flip*114},{268} {250+flip*112},{286} C{250+flip*108},{300} {250+flip*100},{304} {250+flip*96},{298}Z', sk, 0.6, 1.5)))
    face = ('M250,120 C196,120 164,156 160,208 C156,250 158,300 166,346 C176,400 210,440 250,444 '
            'C290,440 324,400 334,346 C342,300 344,250 340,208 C336,156 304,120 250,120Z')
    fx = [d.tone('M300,130 C330,180 334,250 326,310 C316,370 290,420 256,446 L370,450 L370,120Z', sk, 0.75, 5),
          d.tone('M186,250 C198,238 232,240 240,254 C236,274 204,276 190,266Z', '#7a3048', 0.3, 4),
          d.tone('M260,254 C268,240 302,238 314,250 C310,268 282,276 264,272Z', '#7a3048', 0.36, 4),
          d.tone('M164,296 C176,280 210,284 216,304 C210,324 178,326 166,314Z', ROSE, 0.55, 8),
          d.tone('M284,304 C290,284 324,280 336,296 C334,314 306,326 288,320Z', ROSE, 0.55, 8),
          d.tone('M160,214 C200,196 300,196 340,214 L346,110 L154,110Z', '#8a3a40', 0.3, 6)]
    out.append(d.form(face, SKIN, shift=24, soft=8, s=0.5, rim=2.4, rimcol='#ffb48a', rimop=0.6, extra='\n'.join(fx)))
    low = [(346, 250), (352, 290), (352, 330), (346, 372), (334, 412), (314, 448), (286, 474), (250, 484), (214, 474),
           (186, 448), (166, 412), (154, 372), (148, 330), (148, 290), (154, 250)]
    beard = ('M166,246 C166,278 174,302 190,316 C204,326 222,326 236,332 L264,332 C278,326 296,326 310,316 '
             'C326,302 334,278 334,246 ' + bumps(low, 3.2) + ' Z')
    bx = d.tone('M300,250 C340,300 344,400 300,470 L380,490 L380,240Z', '#0c080e', 0.6, 8)
    bx += d.tone('M162,340 C162,390 176,436 206,462 C186,440 174,400 170,350Z', SHEEN, 0.8, 4)
    out.append(d.form(beard, HAIR, shift=14, soft=5, k=0.12, s=0.35, extra=bx, rim=2.5, rimcol='#b08a88', rimop=0.55))
    out.append(f'<path d="M180,380 C184,410 196,436 216,452 M206,392 C210,416 222,436 238,446 M316,350 C324,380 322,410 310,436 M276,400 C284,416 284,436 276,452" '
               f'fill="none" stroke="{hl}" stroke-width="1.6" stroke-linecap="round" opacity="0.55"/>')
    for o, x in ((-1, 212), (1, 288)):
        out.append(eye(d, x, 262, 16, 13.5, lid=e['lid'], look=(-0.3, 0), tilt=1, skin=SKIN, iris='#3a2218', wing=o,
                       crease=0.35, low_lid=e['low'], irr=0.86))
    out.append(thick_brow((236, 238), (212, 220), (184, 236), 10))
    out.append(thick_brow((264, 238), (288, 220), (316, 236), 10))
    out.append(mouth(d, e['mouth'], x0=196, x1=304, y=364))
    mo = ('M250,338 C268,328 292,334 306,346 C316,352 326,346 334,334 C334,356 320,372 300,370 C282,368 266,362 250,362 '
          'C234,362 218,368 200,370 C180,372 166,356 166,334 C174,346 184,352 194,346 C208,334 232,328 250,338Z')
    out.append(d.form(mo, HAIR, shift=8, soft=3, k=0.12, s=0.3,
                      extra=d.tone('M204,344 C220,336 240,336 250,342 C238,342 220,344 208,350Z', SHEEN, 0.7, 2)))
    nose = ('M236,254 C234,280 222,296 214,308 C206,322 212,338 228,340 C238,346 262,346 272,340 '
            'C288,338 294,322 286,308 C278,296 266,280 264,254Z')
    nx = d.tone('M212,332 C226,346 274,346 288,332 L290,356 L210,356Z', '#5a1830', 0.5, 2)
    nx += d.tone('M270,256 C272,290 284,306 290,326 L300,326 L300,250Z', sk, 0.5, 3)
    out.append(d.form(nose, mix(SKIN, ROSE, 0.2), shift=8, soft=4, s=0.4, extra=nx))
    out.append(d.tone('M236,314 C240,308 250,308 254,314 C250,318 240,318 236,314Z', '#fff4e8', 0.75, 1.2))
    nl = mix(SKIN, INK, 0.6)
    out.append(f'<path d="M226,336 C230,331 236,331 240,335 M260,335 C264,331 270,331 274,336" fill="none" stroke="{nl}" stroke-width="1.8" stroke-linecap="round"/>')
    outer = [(158, 216), (148, 182), (158, 146), (182, 118), (212, 98), (250, 86), (288, 98), (318, 118), (342, 146),
             (352, 182), (342, 216)]
    inner = [(342, 216), (322, 196), (298, 188), (274, 176), (250, 186), (226, 176), (202, 188), (178, 196), (158, 216)]
    hair = 'M158,216 ' + bumps(outer, -1, 0.62) + ' ' + bumps(inner, -1, 0.75) + ' Z'
    hx = d.tone('M196,112 C226,96 274,94 304,104 C274,104 232,112 206,126Z', SHEEN, 0.5, 5)
    hx += d.tone('M300,100 C344,130 356,180 340,224 L380,224 L380,90Z', '#0c080e', 0.6, 8)
    out.append(d.form(hair, HAIR, shift=10, soft=4, k=0.12, s=0.35, extra=hx, rim=2.5, rimcol='#b08a88', rimop=0.6))
    out.append(_curl_marks(((190, 146), (232, 128), (276, 136), (210, 168), (256, 160), (300, 162)), hl))


def head_side(d, out, expr='calm'):
    e = EXPR[expr]
    sk = mix(SKIN, '#4a1838', 0.6)
    hl = mix(HAIR, SHEEN, 0.6)
    neck = 'M250,400 L250,446 L360,448 C354,420 352,390 356,340Z'
    out.append(d.form(neck, SKIN, shift=10, soft=4, extra=d.tone('M240,380 L390,330 L400,500 L240,500Z', sk, 0.9, 4)))
    # the profile: a low forehead, a heavy brow, a broad nose; the rest is the beard
    face = ('M214,150 C198,170 190,196 190,222 C190,236 186,246 186,254 C184,266 176,278 166,290 '
            'C156,300 152,314 160,322 C168,330 182,328 190,332 L196,348 C196,380 200,410 214,430 '
            'C240,450 290,440 330,410 C360,380 376,330 376,270 C376,210 356,160 320,136 C284,116 240,122 214,150Z')
    fx = [d.tone('M320,140 C356,190 360,270 340,340 C324,390 290,426 250,446 L400,450 L400,130Z', sk, 0.6, 8),
          d.tone('M196,250 C210,240 236,244 244,258 C238,276 212,278 200,268Z', '#7a3048', 0.36, 4),
          d.tone('M210,292 C226,276 268,280 276,304 C268,326 228,328 214,314Z', ROSE, 0.55, 8),
          d.tone('M190,214 C220,200 270,198 330,216 L350,120 L186,120Z', '#8a3a40', 0.3, 6)]
    out.append(d.form(face, SKIN, shift=24, soft=8, s=0.5, rim=2.4, rimcol='#ffb48a', rimop=0.6, extra='\n'.join(fx)))
    low = [(180, 326), (172, 356), (172, 392), (180, 428), (198, 458), (226, 478), (260, 484), (294, 474), (322, 452),
           (340, 420), (348, 384), (346, 346), (338, 312), (328, 280), (318, 248)]
    beard = ('M298,244 C298,272 292,296 276,312 C260,324 244,326 228,330 L196,334 C188,334 184,330 '
             + bumps(low, -3.2)[1:] + ' Z')
    bx = d.tone('M300,250 C336,300 340,390 310,450 C290,476 270,486 250,490 L400,500 L400,240Z', '#0c080e', 0.6, 8)
    bx += d.tone('M184,350 C186,396 200,440 232,466 C210,450 194,414 190,372Z', SHEEN, 0.8, 4)
    out.append(d.form(beard, HAIR, shift=14, soft=5, k=0.12, s=0.35, extra=bx, rim=2.5, rimcol='#b08a88', rimop=0.55))
    out.append(f'<path d="M198,380 C202,410 214,436 234,452 M224,392 C228,416 240,436 256,446 M286,340 C302,352 314,372 316,398 M280,400 C290,416 292,436 284,452" '
               f'fill="none" stroke="{hl}" stroke-width="1.6" stroke-linecap="round" opacity="0.55"/>')
    out.append(d.tone('M232,320 C250,314 270,306 282,290 C278,312 258,326 232,330Z', mix(SKIN, ROSE, 0.35), 0.55, 3))
    ear = 'M300,254 C314,238 338,244 340,270 C342,296 330,318 316,324 C306,328 300,320 302,310 C294,294 294,272 300,254Z'
    ex = d.tone('M310,264 C322,256 330,266 328,284 C326,300 316,306 312,300 C316,290 316,276 310,264Z', sk, 0.8, 1.5)
    out.append(d.form(ear, SKIN, shift=8, soft=3, s=0.55, extra=ex))
    out.append(eye_side(216, 264, 1.25, iris='#3a2218', skin=SKIN, lid=0.34))
    w = mix(SKIN, INK, 0.45)
    out.append(f'<path d="M240,256 L250,250 M241,264 L252,264 M239,272 L248,277" fill="none" stroke="{w}" stroke-width="1.3" stroke-linecap="round" opacity="0.7"/>')
    out.append(thick_brow((196, 240), (212, 222), (244, 236), 10))
    out.append(mouth(d, e['mouth'], x0=184, x1=258, y=362))
    mo = ('M178,340 C196,328 226,332 246,344 C258,350 268,344 276,334 C276,356 262,372 242,370 C222,368 204,362 190,364 '
          'C178,366 170,354 178,340Z')
    out.append(d.form(mo, HAIR, shift=8, soft=3, k=0.12, s=0.3,
                      extra=d.tone('M190,342 C206,336 224,338 238,346 C222,344 206,346 194,350Z', SHEEN, 0.7, 2)))
    nose = ('M194,250 C190,272 178,288 164,298 C150,306 146,322 156,332 C166,340 184,338 196,332 '
            'C212,338 226,330 226,318 C226,306 218,298 210,292 C212,278 210,262 206,250Z')
    nx = d.tone('M154,330 C166,340 184,338 196,332 C212,338 226,330 228,318 L234,350 L150,350Z', '#5a1830', 0.5, 2)
    out.append(d.form(nose, mix(SKIN, ROSE, 0.2), shift=10, soft=4, s=0.45, extra=nx))
    out.append(d.tone('M160,308 C166,302 174,302 178,306 C172,310 164,312 160,308Z', '#fff4e8', 0.8, 1))
    out.append(f'<path d="M204,326 C210,320 218,320 222,326" fill="none" stroke="{mix(SKIN, INK, 0.6)}" stroke-width="1.8" stroke-linecap="round"/>')
    outer = [(198, 208), (186, 176), (196, 142), (220, 114), (252, 94), (290, 84), (328, 92), (360, 110), (386, 140),
             (400, 178), (402, 218), (392, 256), (374, 286), (348, 300)]
    inner = [(348, 300), (344, 272), (334, 248), (312, 236), (296, 244), (290, 216), (268, 198), (242, 190), (218, 196),
             (198, 208)]
    hair = 'M198,208 ' + bumps(outer, -1, 0.62) + ' ' + bumps(inner, -1, 0.75) + ' Z'
    hx = d.tone('M226,110 C254,96 296,92 330,100 C300,102 260,110 236,126Z', SHEEN, 0.5, 5)
    hx += d.tone('M330,100 C376,130 400,200 380,300 L430,300 L430,90Z', '#0c080e', 0.6, 8)
    out.append(d.form(hair, HAIR, shift=10, soft=4, k=0.12, s=0.35, extra=hx, rim=2.5, rimcol='#b08a88', rimop=0.6))
    out.append(_curl_marks(((230, 140), (270, 122), (310, 136), (250, 162), (300, 170), (340, 180), (350, 230)), hl))


def _front_jacket(d, out, body, shade, cx, towel):
    sh = '#2a1e40'
    fold = mix(JACKET, '#4a3a5a', 0.45)
    out.append(d.form(body, JACKET, shift=34, soft=10, k=0.25, s=0.5, extra=d.tone(shade, sh, 0.5, 10)))
    out.append(f'<path d="M{cx-52},520 C{cx-60},580 {cx-64},640 {cx-62},700 M{cx+52},518 C{cx+60},580 {cx+64},640 {cx+64},700" fill="none" stroke="{fold}" stroke-width="1.8" opacity="0.7"/>')
    for x, y in ((cx - 38, 600), (cx - 40, 660), (cx + 38, 598), (cx + 40, 658)):
        out.append(d.form(f'M{x-7},{y} a7,7 0 1,0 14,0 a7,7 0 1,0 -14,0Z', mix(JACKET, '#8a7a70', 0.35), shift=3, soft=1.2))
    col = f'M{cx-70},494 C{cx-40},480 {cx+40},480 {cx+70},494 L{cx+72},522 C{cx+40},510 {cx-40},510 {cx-72},524Z'
    out.append(d.form(col, JACKET, shift=10, soft=4, k=0.25, s=0.5))
    out.append(d.form(towel, TOWEL, shift=14, soft=5, s=0.5))


def bust_front(d, out):
    body = ('M-6,700 L10,612 C24,548 80,506 164,488 L250,478 L336,488 C420,506 476,548 490,612 L506,700Z')
    _front_jacket(d, out, body, 'M340,480 C420,520 452,610 458,700 L520,700 L520,460Z', 250,
                  'M330,486 C360,484 394,494 410,508 C418,560 422,630 424,700 L360,700 C360,630 354,560 330,486Z')
    st = mix(TOWEL, '#fff0dc', 0.75)
    out.append(f'<path d="M354,566 C376,560 400,562 416,570 M357,586 C378,580 402,582 418,590" fill="none" stroke="{st}" stroke-width="5" opacity="0.85"/>')


def bust_side(d, out):
    """In profile the barrel of the chest and the belly show best."""
    sh = '#2a1e40'
    body = 'M150,700 C140,640 146,570 176,524 C198,496 240,482 290,480 C350,480 400,510 420,570 C432,610 436,660 438,700Z'
    bx = d.tone('M340,480 C400,520 420,610 424,700 L460,700 L460,460Z', sh, 0.5, 10)
    bx += d.tone('M166,600 C170,560 186,530 210,510 C196,536 186,566 182,604Z', '#fff6e4', 0.7, 5)
    out.append(d.form(body, JACKET, shift=34, soft=10, k=0.25, s=0.5, extra=bx))
    fold = mix(JACKET, '#4a3a5a', 0.45)
    for x, y in ((186, 600), (178, 660)):
        out.append(d.form(f'M{x-6},{y} a6,7 0 1,0 12,0 a6,7 0 1,0 -12,0Z', mix(JACKET, '#8a7a70', 0.35), shift=3, soft=1.2))
    col = 'M236,492 C262,478 330,476 366,490 L368,518 C332,506 268,508 238,524Z'
    out.append(d.form(col, JACKET, shift=10, soft=4, k=0.25, s=0.5))
    arm = 'M286,500 C340,496 380,530 386,590 L390,700 L296,700 L292,590 C290,556 280,524 286,500Z'
    out.append(d.form(arm, JACKET, shift=20, soft=7, k=0.25, s=0.55))
    out.append(f'<path d="M292,590 C294,630 296,670 296,700" fill="none" stroke="{fold}" stroke-width="1.8" opacity="0.7"/>')
    towel = 'M300,486 C326,480 352,486 366,498 C372,540 374,590 372,640 L322,642 C324,590 318,540 300,486Z'
    out.append(d.form(towel, TOWEL, shift=14, soft=5, s=0.5))
    st = mix(TOWEL, '#fff0dc', 0.75)
    out.append(f'<path d="M322,600 C338,596 356,596 372,602 M322,616 C338,612 356,612 372,618" fill="none" stroke="{st}" stroke-width="5" opacity="0.85"/>')
