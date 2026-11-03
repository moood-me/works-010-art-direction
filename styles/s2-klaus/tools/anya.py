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
