"""Аня, about 20: warm, trusting, dreamy. Long face with a narrow pointed chin, a small sharp upturned nose,
heavy dreamy lids, copper hair as a few big shapes falling past the cheeks, a mustard cardigan."""
from kit import mix
from parts import eye, brow, INK

SKIN = '#ecb497'
HAIR = '#94502c'
HAIR_D = mix(HAIR, '#2a1020', 0.45)
SWEATER = '#c99a3e'
BLOUSE = '#efe2cf'
SCARF = '#4f6e74'
DRESS = '#4c5a3e'
ROSE = '#d8706a'

EXPR = {
    'calm':     dict(lid=0.38, brow=-2, mouth='smile', look=(-0.32, -0.12)),
    'joy':      dict(lid=0.30, brow=-4, mouth='open_smile', look=(-0.25, 0.0), low=0.35),
    'surprise': dict(lid=0.05, brow=-12, mouth='o', look=(-0.2, -0.05)),
    'sad':      dict(lid=0.55, brow=6, mouth='sad', look=(-0.1, 0.35), sad=True),
    'anger':    dict(lid=0.38, brow=8, mouth='angry', look=(-0.35, 0.0), angry=True),
}


def head34(d, out, expr='calm'):
    """Three-quarter head turned to the viewer's left; light from upper left. Canvas units ~ a 500x600 bust."""
    L = d.light
    e = EXPR[expr]
    shade_skin = mix(SKIN, '#4a1838', 0.6)
    # --- back hair mass (behind neck and head)
    back = ('M206,120 C252,72 352,78 378,160 C394,214 382,300 386,372 C388,410 380,430 360,440 '
            'C330,446 300,430 296,400 C292,360 300,320 300,280 Z')
    out.append(d.form(back, mix(HAIR, '#1a0a20', 0.25), shift=30, soft=8, k=0.06, s=0.55))
    # --- neck: thin, set back, mostly in the head's shadow
    neck = 'M262,346 C266,372 266,400 262,432 L312,436 C306,398 304,352 308,300Z'
    nx = d.tone('M250,330 C266,376 290,380 318,300 L330,470 L272,470 C270,420 268,390 250,330Z', shade_skin, 0.95, 3)
    out.append(d.form(neck, SKIN, shift=14, soft=4, s=0.5, extra=nx))
    # --- face
    face = ('M212,146 C196,164 188,190 188,212 C188,224 192,232 190,240 C184,250 180,262 184,272 '
            'C190,290 202,324 222,348 C228,356 234,362 240,363 C248,363 256,358 264,352 '
            'C286,336 304,318 314,300 C322,284 324,262 322,240 C320,206 318,180 306,160 C284,138 240,134 212,146Z')
    fx = []
    # big shadow plane: the side of the face turned away (right), cheekbone to jaw
    fx.append(d.tone('M284,148 C290,180 292,214 290,240 C288,268 278,298 262,322 C252,338 246,352 238,366 '
                     'L340,380 L340,140Z', shade_skin, 0.8, 3.5))
    # eye sockets under the brow ridge
    fx.append(d.tone('M240,232 C254,220 284,220 298,234 C296,252 268,258 248,252Z', '#9a4c5c', 0.28, 5))
    fx.append(d.tone('M192,230 C200,224 220,226 226,236 C222,252 204,254 194,248Z', '#9a4c5c', 0.22, 4))
    # warm blush on the cheeks and the nose
    fx.append(d.tone('M252,276 C264,266 290,268 296,286 C292,302 262,304 252,292Z', ROSE, 0.42, 7))
    fx.append(d.tone('M188,276 C196,270 206,274 206,286 C202,296 192,294 188,288Z', ROSE, 0.35, 5))
    # nose cast shadow on the cheek (light from upper left)
    fx.append(d.tone('M220,262 C228,280 234,298 230,310 C222,312 214,308 210,302Z', shade_skin, 0.32, 3))
    # under the lower lip, chin plane
    fx.append(d.tone('M222,338 C230,334 244,334 250,340 C246,346 230,348 222,338Z', shade_skin, 0.25, 3))
    # cast shadow of the front hair on the forehead
    fx.append(d.tone('M186,150 C214,172 246,196 272,186 C292,178 306,196 320,214 L330,120 L186,120Z',
                     '#8a3a3a', 0.28, 7))
    fx.append(d.tone('M186,170 C196,200 200,250 196,300 L184,300 L180,170Z', '#5a2038', 0.55, 4))
    fx.append(d.tone('M196,180 C226,150 262,140 300,140 L300,128 L196,150Z', '#5a2038', 0.5, 4))
    out.append(d.form(face, SKIN, shift=34, soft=10, s=0.5, extra='\n'.join(fx)))
    # --- eyes
    lid, look = e['lid'], e['look']
    out.append(eye(d, 266, 246, 18, 16, irr=0.9, lid=lid, look=look, tilt=1.5, skin=SKIN, iris='#7a4424',
                   low_lid=e.get('low', 0), crease=0.3))
    out.append(eye(d, 208, 245, 10.5, 15, irr=0.9, lid=lid, look=look, tilt=-1, skin=SKIN, iris='#7a4424', wing=-0.4,
                   low_lid=e.get('low', 0), crease=0.0, lower=0.3))
    # --- brows: thin, set far above the eyes; they carry the expression
    b = e['brow']
    bc = mix(HAIR, INK, 0.35)
    if e.get('sad'):
        out.append(brow((246, 222 + b - 10), (268, 214 + b - 4), (296, 226 + b), 4.2, bc))
        out.append(brow((222, 220 + b - 10), (208, 216 + b - 4), (196, 226 + b - 2), 3.4, bc))
    elif e.get('angry'):
        out.append(brow((246, 226 + b - 2), (270, 216 + b - 6), (298, 214 + b - 10), 4.6, bc))
        out.append(brow((222, 224 + b - 2), (208, 218 + b - 6), (194, 216 + b - 8), 3.8, bc))
    else:
        out.append(brow((244, 222 + b), (268, 210 + b), (298, 222 + b), 4.2, bc))
        out.append(brow((222, 218 + b), (208, 212 + b), (194, 222 + b), 3.4, bc))
    # --- nose: small, sharp, the tip turned up; it pokes past the far cheek
    nose = 'M228,236 C224,258 206,280 186,290 C182,293 184,298 192,299 C202,300 210,305 222,302 C230,298 232,290 228,282 Z'
    nx = d.tone('M194,302 C206,302 214,306 226,300 L230,316 L188,316Z', '#6c2f50', 0.5, 1.5)
    nx += d.tone('M200,288 C208,282 220,284 226,292 C220,300 206,300 200,296Z', ROSE, 0.35, 3)
    out.append(d.form(nose, mix(SKIN, ROSE, 0.15), shift=7, soft=2.2, s=0.4, extra=nx))
    out.append(d.tone('M200,284 C204,282 208,281 211,283 C207,285 203,286 200,284Z', '#fff4e0', 0.7, 0.8))
    out.append(f'<path d="M207,296 C211,293 216,294 218,298" fill="none" stroke="{mix(SKIN, INK, 0.55)}" '
               f'stroke-width="1.6" stroke-linecap="round"/>')
    # --- mouth: small, close under the nose
    out.append(mouth(d, e['mouth']))
    # --- hair: from a parting at the crown, two big curtains framing the face, the tips flipping out
    left = ('M302,66 C240,82 188,112 176,170 C166,220 172,270 166,320 C162,360 156,400 140,432 '
            'C132,446 120,452 108,452 C116,462 136,464 150,456 C166,446 176,426 182,400 '
            'C192,360 196,320 196,280 C196,240 194,210 206,184 C222,152 258,136 296,132Z')
    lx = d.tone('M292,100 C246,98 206,120 190,166 C214,138 252,126 292,124Z', mix(HAIR, '#ffe0a8', 0.55), 0.85, 3)
    lx += d.tone('M182,196 C176,250 178,320 162,392 C176,330 186,262 188,206Z', mix(HAIR, '#ffe0a8', 0.45), 0.7, 2.5)
    lx += d.tone('M196,250 C196,300 192,350 182,400 L200,410 L210,250Z', HAIR_D, 0.6, 5)
    out.append(d.form(left, HAIR, shift=16, soft=5, k=0.2, s=0.5, extra=lx))
    right = ('M302,66 C344,90 372,124 378,176 C384,236 372,300 376,360 C378,400 390,430 412,446 '
             'C420,452 424,446 418,440 C428,452 424,468 408,468 C380,466 356,440 346,404 '
             'C336,364 336,320 332,280 C328,230 326,186 304,150 C298,140 292,134 286,132Z')
    rx = d.tone('M300,96 C340,104 364,130 370,170 C350,140 328,120 300,112Z', mix(HAIR, '#ffe0a8', 0.4), 0.7, 3)
    rx += d.tone('M332,240 C336,300 340,360 352,410 L330,420 L320,240Z', HAIR_D, 0.55, 5)
    out.append(d.form(right, HAIR, shift=46, soft=9, k=0.12, s=0.6, extra=rx, rim=2.5, rimcol='#f0b080', rimop=0.7))
    # front lock: sweeps from the parting over the forehead and down past the far cheek, ending in a point
    lock = ('M300,70 C262,84 214,112 196,160 C186,186 184,214 180,236 C178,248 172,258 164,266 '
            'C180,262 190,250 194,236 C198,216 200,198 208,184 C226,152 262,130 296,120 '
            'C298,104 300,86 300,70Z')
    kx = d.tone('M296,82 C262,96 226,122 210,160 C232,134 262,116 296,108Z', mix(HAIR, '#ffe2b0', 0.6), 0.9, 2.5)
    kx += d.tone('M200,190 C194,210 192,230 186,250 C196,236 200,214 206,196Z', HAIR_D, 0.5, 3)
    out.append(d.form(lock, mix(HAIR, '#c87a40', 0.25), shift=12, soft=4, k=0.25, s=0.45, extra=kx))


def mouth(d, kind):
    lipc = '#b85a5e'
    line = '#5a2030'
    if kind == 'smile':
        return '\n'.join([
            d.tone('M212,320 C222,317 234,317 244,316 C238,323 222,325 212,320Z', lipc, 1),
            f'<path d="M207,317 C214,323 232,325 246,314" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>',
            f'<path d="M205,315 C206,317 207,318 209,318" fill="none" stroke="{line}" stroke-width="1.4" stroke-linecap="round"/>',
            d.tone('M215,325 C224,331 236,329 242,323 C239,333 224,336 215,325Z', '#d27a74', 0.8, 1.2),
            d.tone('M220,327 C226,329 232,328 236,326', '#ffe8d8', 0)])
    if kind == 'open_smile':
        return '\n'.join([
            f'<path d="M206,318 C220,322 238,320 250,308 C248,326 236,340 224,340 C214,340 208,330 206,318Z" fill="#4a1a24"/>',
            f'<path d="M210,320 C222,323 238,321 248,311 L246,318 C236,325 222,327 211,325Z" fill="#f4ece4"/>',
            d.tone('M214,334 C220,330 232,330 238,334 C232,340 220,340 214,334Z', '#c45a64', 0.9, 1),
            f'<path d="M204,316 C206,318 208,319 210,319" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>'])
    if kind == 'o':
        return '\n'.join([
            f'<path d="M216,318 C222,312 234,312 238,320 C240,332 234,342 226,342 C218,342 214,330 216,318Z" fill="#4a1a24"/>',
            d.tone('M219,334 C224,330 232,330 236,336 C232,342 222,342 219,334Z', '#c45a64', 0.9, 1),
            f'<path d="M216,318 C222,312 234,312 238,320" fill="none" stroke="{line}" stroke-width="1.6"/>'])
    if kind == 'sad':
        return '\n'.join([
            d.tone('M214,326 C222,322 234,322 242,326 C234,328 222,330 214,326Z', lipc, 1),
            f'<path d="M210,330 C218,322 234,320 246,328" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>',
            d.tone('M218,331 C226,334 236,334 242,331 C238,338 224,338 218,331Z', '#d27a74', 0.6, 1.2)])
    if kind == 'angry':
        return '\n'.join([
            f'<path d="M208,322 C218,316 236,314 248,320 C244,330 220,332 208,322Z" fill="#4a1a24"/>',
            f'<path d="M210,321 C220,317 236,316 246,320 L245,324 C234,322 220,323 211,325Z" fill="#f4ece4"/>',
            f'<path d="M206,324 C216,314 238,312 250,322" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>'])
    raise ValueError(kind)


def bust(d, out):
    """Shoulders for the portrait: a cardigan over a blouse, a knitted scarf loosely around the neck."""
    L = d.light
    body = ('M156,700 L164,566 C170,528 190,504 224,490 L262,478 L284,484 L308,478 L344,490 '
            'C378,504 398,532 404,572 L410,700Z')
    bx = d.tone('M330,482 C352,520 360,570 362,700 L430,700 L430,460Z', '#3a2440', 0.55, 6)
    bx += d.tone('M326,480 C350,486 370,500 384,520 C362,512 344,506 330,500Z', '#3a2440', 0.5, 4)
    bx += d.tone('M176,560 C190,530 208,512 232,500 C214,520 200,540 190,570Z', mix(SWEATER, '#fff0c0', 0.5), 0.6, 3)
    out.append(d.form(body, SWEATER, shift=30, soft=8, s=0.55, extra=bx))
    # blouse in the opening, the cardigan's two edges
    bl = 'M262,478 L284,484 L308,478 L300,560 L290,700 L276,700 L270,560Z'
    out.append(d.form(bl, BLOUSE, shift=8, soft=3))
    edge = mix(SWEATER, '#3a2030', 0.45)
    out.append(f'<path d="M262,478 L270,560 L276,700" fill="none" stroke="{edge}" stroke-width="2.4" stroke-linecap="round"/>')
    out.append(f'<path d="M308,478 L300,560 L290,700" fill="none" stroke="{edge}" stroke-width="2.4" stroke-linecap="round"/>')
    for y in (570, 604):
        out.append(f'<circle cx="{268 + (y-560)*0.08}" cy="{y}" r="4" fill="{mix(SWEATER, "#3a2030", 0.55)}"/>')
        out.append(f'<circle cx="{267 + (y-560)*0.08}" cy="{y-1.2}" r="1.6" fill="{mix(SWEATER, "#fff0c0", 0.5)}"/>')
    # scarf: two big soft shapes
    sc1 = ('M226,452 C244,436 300,436 330,452 C342,462 340,478 326,486 C296,500 252,500 230,486 '
           'C216,476 214,462 226,452Z')
    s1x = d.tone('M240,440 C270,452 300,452 334,446 L340,500 L220,500Z', '#2a2040', 0.35, 6)
    out.append(d.form(sc1, SCARF, shift=14, soft=5, s=0.45, extra=s1x))
    sc2 = 'M300,484 C318,520 322,580 314,700 L270,700 C280,586 282,528 276,494Z'
    out.append(d.form(sc2, SCARF, shift=12, soft=5, s=0.45))
    # knit ribs on the scarf end
    for x in (282, 292, 302):
        out.append(f'<path d="M{x},{506} C{x+2},{540} {x+1},{570} {x-2},{600}" fill="none" stroke="{mix(SCARF, "#1a1a30", 0.35)}" stroke-width="1.4" opacity="0.6"/>')


def figure(d, out, expr='calm'):
    """Full figure, ~7.5 heads, slim, an S-curve: head tilted toward the light, hips to the right,
    weight on the right leg; hands clasped at the waist. Canvas 500x900."""
    ink = mix(SWEATER, '#2a1020', 0.6)
    sh = '#2a1e40'
    out.append(d.tone('M166,846 C200,834 300,834 330,846 C300,858 200,858 166,846Z', '#140c22', 0.6, 4))
    tights = '#4e3c4c'
    boot = '#5a3424'
    # relaxed leg (left), knee bent in, foot on its toe
    out.append(d.form('M226,630 C232,660 238,690 236,720 C234,760 226,792 220,818 L232,820 C242,792 252,760 254,720 '
                      'C256,690 254,660 250,630Z', tights, shift=6, soft=2, s=0.5))
    out.append(d.form('M216,810 L234,812 C236,824 232,836 226,844 L204,842 C200,836 208,826 216,820Z', boot, shift=4, soft=2))
    # weight leg (right), straight
    out.append(d.form('M268,600 C272,680 274,760 270,822 L284,822 C288,760 290,680 292,600Z', tights, shift=6, soft=2, s=0.55))
    out.append(d.form('M268,812 L286,812 C288,826 292,834 300,842 L266,844 C262,836 264,826 268,818Z', boot, shift=4, soft=2))
    # skirt: flares and sways to the left, the hem in one long wave
    skirt = ('M222,372 C210,440 188,540 166,640 C186,652 210,644 230,654 C252,662 274,650 294,652 '
             'C310,652 324,644 336,632 C322,530 306,440 294,368Z')
    kx = d.tone('M268,380 C290,460 306,540 318,624 L350,630 L320,360Z', sh, 0.55, 6)
    kx += d.tone('M222,372 L294,368 L296,400 C268,392 244,394 220,404Z', sh, 0.5, 5)
    kx += d.tone('M200,470 C192,520 182,570 176,604 L190,606 C196,560 204,510 210,470Z', mix(DRESS, '#ffe0a0', 0.4), 0.5, 4)
    out.append(d.form(skirt, DRESS, shift=26, soft=7, s=0.55, extra=kx, rim=2.5, rimcol='#e8a070', rimop=0.6))
    fold = mix(DRESS, '#101020', 0.45)
    out.append(f'<path d="M238,420 C230,500 220,580 210,646 M262,420 C262,500 262,580 262,656" fill="none" stroke="{fold}" stroke-width="1.6" opacity="0.6"/>')
    # cardigan: narrow at the waist, flaring over the hip
    torso = ('M236,184 C220,188 208,196 206,214 C204,250 214,296 222,330 C218,350 212,370 210,392 '
             'C236,400 270,400 300,388 C294,366 284,346 278,328 C288,292 296,250 294,214 C292,198 282,188 270,184Z')
    tx = d.tone('M276,186 C292,230 290,290 280,330 C288,350 296,370 304,392 L330,400 L330,180Z', sh, 0.6, 4)
    tx += d.tone('M228,190 C246,202 264,202 284,190 L284,216 C262,226 246,226 228,216Z', '#3a2040', 0.4, 5)
    tx += d.tone('M212,220 C214,260 220,300 226,330 L232,330 C226,300 220,260 220,220Z', mix(SWEATER, '#fff0c0', 0.5), 0.5, 3)
    out.append(d.form(torso, SWEATER, shift=22, soft=6, s=0.55, extra=tx, rim=2.5, rimcol='#f0b878', rimop=0.6))
    out.append(d.form('M240,188 L252,246 L266,188Z', BLOUSE, shift=4, soft=2))
    out.append(f'<path d="M240,188 L251,262 C252,300 252,340 254,396 M266,188 L255,262" fill="none" stroke="{ink}" stroke-width="1.4" opacity="0.7"/>')
    for y in (282, 310):
        out.append(f'<circle cx="252" cy="{y}" r="2.4" fill="{mix(SWEATER, "#3a2030", 0.55)}"/>')
    # neck and the head (tilted toward the light)
    out.append(d.form('M244,160 C246,174 244,186 242,194 L262,194 C260,184 260,172 262,156Z', SKIN, shift=4, soft=2, s=0.6,
                      extra=d.tone('M244,150 C252,176 258,176 262,150 L270,200 L240,200Z', mix(SKIN, '#4a1838', 0.6), 0.9, 2)))
    from common import place
    place(d, out, head34, 'anya', (234, 170), 0.48, rot=-6, expr=expr)
    # scarf
    sc = 'M226,182 C238,174 270,174 284,182 C290,188 288,196 280,200 C262,206 240,206 228,200 C220,194 220,188 226,182Z'
    out.append(d.form(sc, SCARF, shift=6, soft=3, s=0.45))
    out.append(d.form('M268,198 C278,226 282,262 278,296 L264,298 C266,264 264,232 258,202Z', SCARF, shift=5, soft=2, s=0.45))
    out.append(f'<path d="M265,298 L265,306 M271,297 L272,305 M277,296 L278,304" fill="none" stroke="{SCARF}" stroke-width="1.8"/>')
    # arms: elbows out a little, hands clasped low in front
    la = 'M210,200 C198,214 194,250 198,290 C202,320 214,346 234,360 L242,350 C228,334 218,312 216,288 C214,256 216,230 220,212Z'
    out.append(d.form(la, SWEATER, shift=10, soft=4, s=0.5))
    ra = 'M290,200 C302,214 306,254 300,290 C294,322 284,344 266,358 L258,348 C270,332 278,312 282,288 C286,256 284,230 280,212Z'
    out.append(d.form(ra, SWEATER, shift=14, soft=4, s=0.6,
                      extra=d.tone('M296,200 C312,240 310,310 290,350 L330,360 L330,190Z', sh, 0.55, 4)))
    cuff = mix(SWEATER, '#3a2030', 0.25)
    out.append(d.form('M228,360 L242,348 L250,358 L236,370Z', cuff, shift=3, soft=1.5))
    out.append(d.form('M258,346 L272,358 L264,368 L250,356Z', cuff, shift=3, soft=1.5))
    h1 = 'M236,366 C244,358 258,358 266,364 C270,372 264,380 254,382 C244,384 236,378 236,366Z'
    out.append(d.form(h1, SKIN, shift=4, soft=2, s=0.45))
    h2 = 'M248,360 C258,354 270,358 274,366 C274,374 268,378 260,378 C252,376 246,370 248,360Z'
    out.append(d.form(h2, SKIN, shift=4, soft=2, s=0.45))
    fl = mix(SKIN, INK, 0.45)
    out.append(f'<path d="M254,368 L262,374 M258,363 L267,369 M263,360 L271,365" fill="none" stroke="{fl}" stroke-width="1.1" stroke-linecap="round"/>')


def head_front(d, out, expr='calm'):
    """Front view for the turnaround, same 500x600 frame, chin at (250,368)."""
    sk = mix(SKIN, '#4a1838', 0.6)
    back = ('M168,150 C176,86 324,86 332,150 C346,220 340,320 352,400 C356,430 362,446 372,456 '
            'C320,470 300,440 280,420 L220,420 C200,440 180,470 128,456 C138,446 144,430 148,400 C160,320 154,220 168,150Z')
    out.append(d.form(back, mix(HAIR, '#1a0a20', 0.3), shift=20, soft=8, k=0.06, s=0.55))
    neck = 'M226,330 C230,370 228,400 222,436 L278,436 C272,400 270,370 274,330Z'
    out.append(d.form(neck, SKIN, shift=8, soft=3, s=0.5, extra=d.tone('M220,340 C240,380 262,384 280,340 L290,440 L280,440 C266,420 262,400 262,380 L220,380Z', sk, 0.9, 3)))
    face = ('M250,138 C210,138 186,160 184,200 C182,226 186,246 184,262 C184,296 202,330 226,356 '
            'C236,366 244,370 250,370 C256,370 264,366 274,356 C298,330 316,296 316,262 '
            'C314,246 318,226 316,200 C314,160 290,138 250,138Z')
    fx = [d.tone('M290,150 C302,190 302,230 298,262 C294,300 280,330 262,360 L250,372 L330,380 L330,140Z', sk, 0.75, 4),
          d.tone('M196,234 C206,224 232,226 240,240 C234,256 210,258 198,250Z', '#9a4c5c', 0.25, 4),
          d.tone('M260,240 C268,226 294,224 304,234 C302,250 278,258 262,256Z', '#9a4c5c', 0.3, 4),
          d.tone('M196,282 C204,272 222,274 226,288 C222,300 202,300 196,292Z', ROSE, 0.4, 6),
          d.tone('M274,288 C278,274 296,272 304,282 C304,292 282,300 276,298Z', ROSE, 0.4, 6),
          d.tone('M254,262 C262,282 268,300 262,312 L250,312Z', sk, 0.3, 3),
          d.tone('M236,338 C244,334 256,334 264,338 C258,346 242,346 236,338Z', sk, 0.25, 3),
          d.tone('M180,160 C220,200 280,200 320,160 L320,120 L180,120Z', '#8a3a3a', 0.25, 6)]
    out.append(d.form(face, SKIN, shift=22, soft=7, s=0.5, extra='\n'.join(fx)))
    e = EXPR[expr]
    out.append(eye(d, 218, 248, 16, 15, lid=e['lid'], look=(0.0, -0.1), tilt=1.5, skin=SKIN, iris='#7a4424', wing=-1, crease=0.3, irr=0.9))
    out.append(eye(d, 282, 248, 16, 15, lid=e['lid'], look=(0.0, -0.1), tilt=1.5, skin=SKIN, iris='#7a4424', wing=1, crease=0.3, irr=0.9))
    bc = mix(HAIR, INK, 0.35)
    out.append(brow((236, 222), (214, 210), (192, 222), 4, bc))
    out.append(brow((264, 222), (286, 210), (308, 222), 4, bc))
    nose = 'M244,250 C246,270 240,286 238,296 C240,304 246,306 250,306 C254,306 262,304 264,298 C262,286 256,270 256,250Z'
    out.append(d.form(nose, mix(SKIN, ROSE, 0.12), shift=6, soft=2.5, s=0.4,
                      extra=d.tone('M238,298 C244,308 256,308 264,298 L266,312 L236,312Z', sk, 0.5, 1.5)))
    nl = mix(SKIN, INK, 0.5)
    out.append(f'<path d="M238,300 C241,303 244,303 246,301 M254,301 C256,303 259,303 262,300" fill="none" stroke="{nl}" stroke-width="1.5" stroke-linecap="round"/>')
    out.append(d.tone('M246,286 C248,284 251,284 253,286 C251,288 248,288 246,286Z', '#fff4e0', 0.7, 0.8))
    out.append(d.tone('M236,326 C244,322 256,322 264,326 C256,330 244,330 236,326Z', '#b85a5e', 1))
    out.append('<path d="M230,324 C240,332 260,332 270,324" fill="none" stroke="#5a2030" stroke-width="2" stroke-linecap="round"/>')
    out.append(d.tone('M240,331 C246,336 254,336 260,331 C258,339 242,339 240,331Z', '#d27a74', 0.8, 1.2))
    left = ('M262,70 C210,76 176,108 170,160 C164,220 168,290 160,350 C156,390 148,420 130,444 '
            'C122,454 110,458 100,456 C110,468 132,468 146,458 C164,444 176,420 180,390 '
            'C186,346 186,300 186,260 C186,226 186,196 196,176 C212,150 236,136 262,128Z')
    out.append(d.form(left, HAIR, shift=12, soft=4, k=0.2, s=0.5,
                      extra=d.tone('M262,78 C222,84 192,110 182,150 C206,120 232,104 262,96Z', mix(HAIR, '#ffe0a8', 0.55), 0.8, 3)))
    right = ('M262,70 C300,74 324,108 330,160 C336,220 332,290 340,350 C344,390 352,420 370,444 '
             'C378,454 390,458 400,456 C390,468 368,468 354,458 C336,444 324,420 320,390 '
             'C314,346 314,300 314,260 C314,226 312,196 304,176 C292,152 278,138 262,128Z')
    out.append(d.form(right, HAIR, shift=24, soft=6, k=0.12, s=0.6, rim=2.5, rimcol='#f0b080', rimop=0.7,
                      extra=d.tone('M318,240 C320,300 326,360 344,430 L370,430 L350,230Z', HAIR_D, 0.5, 5)))
    lock = ('M262,70 C230,86 200,116 190,160 C186,182 184,200 180,214 C192,204 198,190 202,176 '
            'C214,150 238,132 262,124Z')
    out.append(d.form(lock, mix(HAIR, '#c87a40', 0.25), shift=8, soft=3, k=0.25, s=0.45))


def head_side(d, out, expr='calm'):
    """Profile facing left, same frame."""
    sk = mix(SKIN, '#4a1838', 0.6)
    back = ('M214,110 C260,70 350,78 376,150 C392,200 388,280 396,360 C400,400 410,430 428,450 '
            'C400,460 370,456 350,444 C334,420 326,380 322,340 Z')
    out.append(d.form(back, mix(HAIR, '#1a0a20', 0.25), shift=24, soft=8, k=0.06, s=0.55))
    neck = 'M232,350 C240,380 240,410 234,440 L304,444 C300,410 300,370 306,326Z'
    out.append(d.form(neck, SKIN, shift=10, soft=3, s=0.5, extra=d.tone('M230,366 C254,376 280,370 304,330 L320,450 L230,450Z', sk, 0.8, 4)))
    # the profile: forehead, brow, a small sharp upturned nose, lips, a pointed chin
    face = ('M218,128 C204,150 196,176 194,204 C194,216 190,224 192,232 C196,240 194,250 188,262 '
            'C180,276 170,284 166,290 C164,296 170,300 178,300 C184,300 188,304 188,310 '
            'C186,316 190,320 192,322 C188,326 188,330 192,334 C190,344 192,354 198,362 '
            'C206,370 222,372 234,368 C260,360 290,340 312,320 C330,300 340,270 340,230 '
            'C340,170 300,120 250,116 C238,116 226,120 218,128Z')
    fx = [d.tone('M300,140 C320,190 320,250 304,300 C290,330 260,356 232,372 L360,380 L360,130Z', sk, 0.55, 8),
          d.tone('M200,232 C212,226 232,228 240,240 C234,258 214,260 204,254Z', '#9a4c5c', 0.3, 4),
          d.tone('M220,276 C236,266 262,270 268,288 C262,302 236,302 222,292Z', ROSE, 0.4, 7),
          d.tone('M196,336 C204,342 214,344 222,342 C216,352 204,352 196,346Z', sk, 0.3, 2),
          d.tone('M200,140 C240,180 280,200 330,190 L330,110 L200,110Z', '#8a3a3a', 0.25, 6)]
    out.append(d.form(face, SKIN, shift=20, soft=7, s=0.5, extra='\n'.join(fx)))
    out.append(d.tone('M170,288 C174,285 178,285 181,287 C178,289 173,290 170,288Z', '#fff4e0', 0.7, 0.8))
    out.append(f'<path d="M184,298 C188,296 192,298 192,302" fill="none" stroke="{mix(SKIN, INK, 0.5)}" stroke-width="1.5" stroke-linecap="round"/>')
    # lips and the mouth corner
    out.append(d.tone('M192,322 C196,318 200,318 204,322 C200,324 196,324 192,322Z', '#b85a5e', 1))
    out.append(d.tone('M192,325 C196,330 202,332 206,326 C202,334 196,334 192,328Z', '#d27a74', 0.9))
    out.append('<path d="M190,322 C196,324 202,324 208,320" fill="none" stroke="#5a2030" stroke-width="1.8" stroke-linecap="round"/>')
    # ear
    ear = 'M290,250 C302,240 318,248 318,268 C318,288 306,300 296,300 C290,296 290,288 292,282 C286,272 286,260 290,250Z'
    out.append(d.form(ear, SKIN, shift=6, soft=2, s=0.55, extra=d.tone('M298,258 C308,254 312,264 308,280 C304,290 298,288 298,280 C302,272 302,264 298,258Z', sk, 0.7, 1.5)))
    # eye in profile: a wedge with the iris at its front, the heavy lid and the lashes over it
    e = EXPR[expr]
    ex, ey = 214, 248
    out.append(f'<path d="M{ex-10},{ey-2} C{ex-4},{ey-10} {ex+6},{ey-10} {ex+10},{ey-4} C{ex+6},{ey+6} {ex-2},{ey+8} {ex-8},{ey+4}Z" fill="#f3ebe3"/>')
    out.append(f'<path d="M{ex-10},{ey-4} C{ex-7},{ey-8} {ex-3},{ey-8} {ex-1},{ey-4} L{ex-1},{ey+6} C{ex-5},{ey+7} {ex-8},{ey+5} {ex-9},{ey+3}Z" fill="#7a4424"/>')
    out.append(f'<path d="M{ex-9},{ey-6} C{ex-4},{ey-10} {ex+6},{ey-10} {ex+10},{ey-4} L{ex+11},{ey-2} C{ex+4},{ey-6} {ex-4},{ey-4} {ex-9},{ey-1}Z" fill="{SKIN}"/>')
    out.append(f'<path d="M{ex-11},{ey-1} C{ex-6},{ey-5} {ex+2},{ey-6} {ex+11},{ey-3} L{ex+12},{ey-7} C{ex+2},{ey-10} {ex-6},{ey-8} {ex-12},{ey-3}Z" fill="{INK}"/>')
    out.append(f'<path d="M{ex-12},{ey-3} L{ex-17},{ey-5} M{ex-11},{ey-1} L{ex-16},{ey}" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>')
    out.append(f'<path d="M{ex-6},{ey+7} C{ex},{ey+8} {ex+6},{ey+5} {ex+9},{ey}" fill="none" stroke="{mix(SKIN, INK, 0.45)}" stroke-width="1.2" opacity="0.5"/>')
    out.append(brow((218, 222), (206, 216), (196, 222), 3.4, mix(HAIR, INK, 0.35)))
    out.append(f'<path d="M{ex-6},{ey-12} C{ex},{ey-15} {ex+8},{ey-14} {ex+12},{ey-8}" fill="none" stroke="{mix(SKIN, INK, 0.4)}" stroke-width="1.3" opacity="0.6"/>')
    # hair over the top, the curtain falling behind the ear
    hair = ('M220,118 C246,80 320,74 356,118 C376,146 380,200 372,250 C366,300 370,360 384,410 '
            'C392,436 404,450 418,458 C392,466 362,452 350,424 C336,390 334,340 330,300 '
            'C326,260 318,226 300,206 C280,190 250,186 226,180 C214,176 206,166 204,152 '
            'C196,160 192,172 192,186 C186,166 196,136 220,118Z')
    hx = d.tone('M226,110 C258,90 310,88 344,110 C310,100 262,104 234,124Z', mix(HAIR, '#ffe0a8', 0.55), 0.85, 3)
    hx += d.tone('M330,220 C340,300 344,380 364,440 L400,440 L370,210Z', HAIR_D, 0.55, 6)
    out.append(d.form(hair, HAIR, shift=14, soft=5, k=0.18, s=0.5, extra=hx, rim=2.5, rimcol='#f0b080', rimop=0.6))


def bust_front(d, out):
    sh = '#3a2440'
    body = ('M130,700 L138,610 C146,550 176,516 214,500 L236,494 L264,494 L286,500 '
            'C324,516 354,550 362,610 L370,700Z')
    bx = d.tone('M300,500 C336,530 352,600 356,700 L380,700 L380,480Z', sh, 0.55, 8)
    bx += d.tone('M160,580 C172,548 190,528 214,514 C198,536 186,560 178,590Z', mix(SWEATER, '#fff0c0', 0.5), 0.6, 3)
    out.append(d.form(body, SWEATER, shift=26, soft=8, s=0.55, extra=bx))
    out.append(d.form('M232,496 L250,520 L268,496 L262,700 L238,700Z', BLOUSE, shift=6, soft=2))
    edge = mix(SWEATER, '#3a2030', 0.45)
    out.append(f'<path d="M232,496 L240,700 M268,496 L260,700" fill="none" stroke="{edge}" stroke-width="2.4"/>')
    sc = 'M206,482 C226,468 274,468 294,482 C304,492 300,506 288,510 C264,518 236,518 212,510 C200,504 198,490 206,482Z'
    out.append(d.form(sc, SCARF, shift=10, soft=4, s=0.45, extra=d.tone('M206,480 L294,480 L294,492 C264,500 236,500 206,492Z', '#2a2040', 0.35, 4)))
    out.append(d.form('M262,506 C270,540 272,580 268,620 L250,620 C254,584 252,546 246,510Z', SCARF, shift=8, soft=3, s=0.45))


def bust_side(d, out):
    sh = '#3a2440'
    body = ('M190,700 L192,610 C192,560 204,520 232,500 L268,490 L306,494 C334,506 350,540 356,600 L362,700Z')
    bx = d.tone('M300,496 C334,520 348,600 352,700 L380,700 L380,480Z', sh, 0.55, 8)
    out.append(d.form(body, SWEATER, shift=26, soft=8, s=0.55, extra=bx))
    out.append(d.form('M232,500 C228,540 222,580 214,620 L200,620 C204,580 214,536 226,500Z', mix(SWEATER, '#3a2030', 0.2), shift=4, soft=2))
    sc = 'M222,484 C236,470 296,466 316,480 C324,490 320,504 306,508 C280,516 248,516 228,506 C216,500 214,490 222,484Z'
    out.append(d.form(sc, SCARF, shift=10, soft=4, s=0.45))
    out.append(d.form('M228,502 C222,540 218,580 220,620 L204,620 C202,580 208,536 216,500Z', SCARF, shift=6, soft=2, s=0.45))
    # the arm hanging at the side
    arm = 'M262,500 C292,500 308,530 308,580 L306,700 L262,700 L262,580 C262,540 256,516 262,500Z'
    out.append(d.form(arm, SWEATER, shift=14, soft=5, s=0.55))
