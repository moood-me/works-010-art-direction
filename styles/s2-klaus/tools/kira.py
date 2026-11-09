"""Кира, about 15: prickly, closed, defiant; vulnerable underneath. A narrow angular face with a small sharp chin,
the head down and the look from under the brows; short choppy dark hair, a long fringe over the far eye; a mouth
pressed shut or a crooked half-smirk. An oversized dark plum hoodie, lime headphones round the neck, narrow
trousers, heavy boots with lime laces."""
from kit import mix
from parts import eye, eye_side, brow, INK

SKIN = '#ecc0a8'
HAIR = '#2c1c30'
HOOD = '#4c2c52'
TROUS = '#2a2c3c'
BOOT = '#1c1a22'
LIME = '#c6e23a'
ROSE = '#d0707a'
SHEEN = '#8a6c98'
PAD = mix(LIME, '#28321a', 0.55)   # the cups' inner side

EXPR = {
    'calm':     dict(lid=0.42, low=0.12, brows=(0, 0), mouth='shut', look=(0.3, -0.05)),
    'smirk':    dict(lid=0.4, low=0.2, brows=(0, -2), mouth='smirk', look=(0.3, -0.05)),
    'joy':      dict(lid=0.36, low=0.36, brows=(-4, -3), mouth='halfsmile', look=(0.15, 0.1)),
    'surprise': dict(lid=0.02, low=0.0, brows=(-14, -12), mouth='o', look=(0.0, 0.0)),
    'sad':      dict(lid=0.56, low=0.05, brows=(2, 2), mouth='sad', look=(-0.25, 0.45), sad=True),
    'anger':    dict(lid=0.34, low=0.25, brows=(8, 8), mouth='angry', look=(0.3, -0.05), angry=True),
}
TILT = 'rotate(-6,300,330)'   # the head is held down: everything above the neck is turned about the nape


def mouth(d, kind):
    line = '#5a2434'
    lip = '#c2727a'
    if kind == 'shut':       # pressed shut, a little crooked: the near corner tucked in
        return '\n'.join([
            d.tone('M214,332 C226,329 240,329 252,328 C242,335 226,337 214,332Z', lip, 0.7, 1),
            f'<path d="M208,334 C222,335 240,333 256,329" fill="none" stroke="{line}" stroke-width="2.2" stroke-linecap="round"/>',
            f'<path d="M257,324 C260,327 260,331 258,334" fill="none" stroke="{mix(SKIN, INK, 0.5)}" stroke-width="1.5" stroke-linecap="round"/>',
            d.tone('M216,340 C226,343 238,343 246,339 C240,347 224,348 216,340Z', lip, 0.5, 1.5)])
    if kind == 'smirk':      # pressed, the near corner pulled up and back
        return '\n'.join([
            d.tone('M212,333 C224,330 240,329 254,323 C244,334 226,338 212,333Z', lip, 0.75, 1),
            f'<path d="M206,334 C220,337 240,334 256,322" fill="none" stroke="{line}" stroke-width="2.2" stroke-linecap="round"/>',
            f'<path d="M258,316 C262,319 262,324 259,327" fill="none" stroke="{mix(SKIN, INK, 0.5)}" stroke-width="1.5" stroke-linecap="round"/>',
            d.tone('M216,340 C226,343 238,342 246,336 C240,346 224,348 216,340Z', lip, 0.5, 1.5)])
    if kind == 'halfsmile':  # the most she allows: lips shut, both corners up, a dimple
        return '\n'.join([
            d.tone('M210,331 C224,334 242,331 256,321 C246,336 224,340 210,331Z', lip, 0.8, 1),
            f'<path d="M208,331 C220,338 242,335 257,321" fill="none" stroke="{line}" stroke-width="2.2" stroke-linecap="round"/>',
            f'<path d="M260,314 C264,318 264,323 260,327" fill="none" stroke="{mix(SKIN, INK, 0.5)}" stroke-width="1.5" stroke-linecap="round"/>',
            d.tone('M216,341 C226,345 240,343 248,336 C242,348 224,350 216,341Z', lip, 0.5, 1.5)])
    if kind == 'o':
        return '\n'.join([
            f'<path d="M218,328 C224,321 238,321 243,329 C246,339 240,348 231,348 C222,348 215,339 218,328Z" fill="#4a1a26"/>',
            f'<path d="M221,327 C226,323 236,323 240,328 C236,331 226,331 221,327Z" fill="#f4ece4"/>',
            d.tone('M222,342 C227,338 236,338 240,343 C236,348 226,348 222,342Z', '#c45a64', 0.9, 0.8),
            d.tone('M218,350 C226,354 236,354 243,349 C238,357 224,358 218,350Z', lip, 0.5, 1.5)])
    if kind == 'sad':        # pressed tight, the corners down, the lower lip pushed out
        return '\n'.join([
            f'<path d="M210,338 C220,330 238,328 252,335" fill="none" stroke="{line}" stroke-width="2.2" stroke-linecap="round"/>',
            d.tone('M216,338 C226,334 238,334 247,338 C240,346 224,346 216,338Z', lip, 0.75, 1.2),
            d.tone('M218,350 C226,346 238,346 246,350 C238,354 226,354 218,350Z', '#7a3a50', 0.3, 2)])
    if kind == 'angry':      # a snarl: the upper lip lifted on the near side, the teeth shut
        return '\n'.join([
            f'<path d="M208,338 C218,330 240,322 256,326 C256,338 244,346 228,347 C218,347 210,344 208,338Z" fill="#4a1a26"/>',
            f'<path d="M212,338 C222,332 240,326 253,329 C252,337 242,342 228,343 C220,343 214,341 212,338Z" fill="#f4ece4"/>',
            f'<path d="M214,339 C226,336 242,333 253,334" fill="none" stroke="#4a1a26" stroke-width="1.2"/>',
            f'<path d="M204,340 C216,328 242,318 258,324" fill="none" stroke="{line}" stroke-width="2.2" stroke-linecap="round"/>',
            d.tone('M214,351 C224,355 238,353 248,346 C242,358 222,360 214,351Z', lip, 0.55, 1.5)])
    raise ValueError(kind)


def head34(d, out, expr='calm'):
    e = EXPR[expr]
    sk = mix(SKIN, '#4a1848', 0.6)
    # neck: thin, long, leaning forward
    neck = 'M254,350 C260,386 258,420 252,452 L312,456 C306,420 304,380 312,316Z'
    out.append(d.form(neck, SKIN, shift=9, soft=3.5, extra=d.tone('M246,346 C272,400 300,396 316,312 L330,480 L246,480Z', sk, 0.92, 3)
                      + d.tone('M240,340 L330,300 L330,400 C300,410 270,404 240,384Z', '#3a1440', 0.35, 6)))
    out.append(f'<g transform="{TILT}">')
    # the hair behind: a short shaggy mass that ends in choppy points at the nape
    back = ('M300,100 C258,96 220,112 204,146 C240,140 290,150 316,190 C324,214 326,244 326,268 '
            'C326,290 322,306 316,322 L334,310 L334,344 L354,318 L362,344 L378,314 L398,322 '
            'C398,284 398,244 392,212 C388,180 380,152 366,134 L378,120 L356,122 C340,108 322,101 300,100Z')
    bx = d.tone('M336,120 C372,160 388,240 368,350 L420,350 L420,100Z', '#120a16', 0.65, 8)
    bx += d.tone('M320,130 C344,160 354,200 354,240 C346,204 334,170 312,146Z', SHEEN, 0.5, 5)
    out.append(d.form(back, HAIR, shift=12, soft=4, k=0.06, s=0.4, extra=bx, rim=2, rimcol='#b890a8', rimop=0.35))
    # face: narrow, a flat cheek that runs to a small sharp chin
    face = ('M212,152 C200,172 194,198 194,222 C194,236 197,244 195,254 C190,264 188,276 190,288 '
            'C192,304 198,318 204,332 C210,348 220,362 232,370 C240,374 250,372 258,366 '
            'C280,352 302,330 314,306 C324,284 328,258 326,232 C324,200 318,172 304,154 C282,134 236,134 212,152Z')
    fx = [d.tone('M292,150 C300,186 298,220 292,246 C286,272 280,300 266,326 C256,346 246,360 238,374 L350,390 L350,140Z', sk, 0.82, 3.5),
          d.tone('M240,250 C256,238 290,240 302,256 C298,274 266,280 246,272Z', '#6a3058', 0.38, 5),
          d.tone('M250,278 C264,286 284,286 296,276 C290,290 262,292 250,284Z', '#6a3058', 0.3, 2.5),
          d.tone('M252,296 C266,286 296,290 300,306 C294,320 266,320 256,310Z', ROSE, 0.32, 7),
          # the fringe's cast shadow
          d.tone('M186,300 C200,290 214,270 228,262 C244,244 280,226 330,222 L340,130 L180,130Z', '#6a2a50', 0.4, 5)]
    out.append(d.form(face, SKIN, shift=30, soft=8, s=0.5, rim=2.4, rimcol='#ffb89a', rimop=0.6, extra='\n'.join(fx)))
    # eyes: smaller than Аня's, a dark line round them; the far one is under the fringe
    lid, look = e['lid'], e['look']
    out.append(eye(d, 268, 262, 16, 13.5, lid=lid, look=look, tilt=-1.5, skin=SKIN, iris='#5a6a52', crease=0.3,
                   low_lid=e['low'], lash=3.4, wing=1.2, irr=0.84))
    out.append(eye(d, 210, 259, 9, 12.5, lid=lid, look=look, tilt=0, skin=SKIN, iris='#5a6a52', wing=-0.3, crease=0,
                   lower=0.3, low_lid=e['low'], lash=3.0, irr=0.84))
    out.append(d.tone('M252,274 C264,280 280,280 290,272 C284,282 262,284 252,278Z', '#3a1a40', 0.35, 1.5))
    # brows: straight and low, the inner end pulled down
    bc = mix(HAIR, INK, 0.3)
    bn, bf = e['brows']
    if e.get('sad'):
        out.append(brow((246, 236 + bn), (270, 236 + bn), (298, 246 + bn), 4.6, bc))
        out.append(brow((226, 236 + bf), (212, 236 + bf), (198, 244 + bf), 3.6, bc))
    elif e.get('angry'):
        out.append(brow((244, 248 + bn - 6), (268, 238 + bn - 8), (298, 232 + bn - 8), 5, bc))
        out.append(brow((228, 246 + bf - 6), (212, 240 + bf - 8), (198, 236 + bf - 8), 4, bc))
    else:
        out.append(brow((244, 243 + bn), (268, 236 + bn), (298, 238 + bn), 4.6, bc))
        out.append(brow((228, 242 + bf), (212, 238 + bf), (198, 240 + bf), 3.6, bc))
    # nose: small, straight, a sharp tip
    nose = 'M226,248 C223,264 212,280 197,291 C191,296 193,302 200,303 C208,304 214,306 222,302 C228,298 230,292 229,284Z'
    nx = d.tone('M196,302 C208,304 214,306 224,301 L228,314 L192,314Z', '#5a2048', 0.5, 1.5)
    out.append(d.form(nose, mix(SKIN, ROSE, 0.14), shift=6, soft=2.2, s=0.45, extra=nx))
    out.append(d.tone('M199,293 C203,290 207,290 210,292 C206,295 202,296 199,293Z', '#fff4e8', 0.8, 0.8))
    out.append(f'<path d="M209,299 C212,296 217,297 219,301" fill="none" stroke="{mix(SKIN, INK, 0.55)}" stroke-width="1.5" stroke-linecap="round"/>')
    out.append(mouth(d, e['mouth']))
    # a lock in front of the ear
    lock = 'M300,168 C322,200 330,250 324,290 L314,326 L308,298 L296,318 C300,282 300,240 290,200Z'
    out.append(d.form(lock, HAIR, shift=8, soft=3, k=0.14, s=0.7))
    # the fringe: from a parting on the near side, across the forehead and down over the far eye, cut in points
    fringe = ('M308,104 C270,98 224,110 202,146 C188,172 184,212 186,248 L180,304 L196,274 L202,300 L213,264 L224,284 '
              'C230,258 242,240 258,228 C276,216 298,210 322,208 C326,170 320,130 308,104Z')
    hx = d.tone('M226,120 C250,108 280,106 302,112 C280,116 252,124 234,138Z', SHEEN, 0.75, 3)
    hx += d.tone('M196,170 C192,200 190,230 192,262 L200,262 C200,230 202,200 208,172Z', SHEEN, 0.5, 3)
    hx += d.tone('M296,110 C320,140 326,180 322,212 L350,212 L350,100Z', '#120a16', 0.55, 6)
    out.append(d.form(fringe, HAIR, shift=10, soft=3.5, k=0.08, s=0.4, extra=hx))
    hl = mix(HAIR, SHEEN, 0.55)
    out.append(f'<path d="M298,112 C262,124 232,150 214,264 M304,118 C276,140 256,176 248,232 M300,108 C246,112 208,150 198,270" '
               f'fill="none" stroke="{hl}" stroke-width="1.5" stroke-linecap="round" opacity="0.45"/>')
    out.append('</g>')


def bust(d, out):
    """Narrow sloping shoulders in an oversized hoodie; the hood lies behind the neck."""
    sh = '#1c1230'
    hood = 'M214,520 C210,480 250,452 300,452 C352,452 388,480 386,522 C370,548 240,548 214,520Z'
    out.append(d.form(hood, mix(HOOD, '#1a0a20', 0.25), shift=14, soft=5, k=0.14, s=0.5))
    band = mix(LIME, '#20281a', 0.3)
    out.append(f'<path d="M232,524 C226,478 352,470 350,520" fill="none" stroke="{band}" stroke-width="9" stroke-linecap="round"/>')
    body = ('M146,700 L160,626 C170,574 198,540 236,526 L266,514 L302,512 L334,520 C374,536 398,574 406,626 L414,700Z')
    bx = d.tone('M322,514 C364,548 380,620 384,700 L430,700 L430,490Z', sh, 0.6, 8)
    bx += d.tone('M190,596 C202,566 222,546 244,534 C230,554 216,576 208,604Z', mix(HOOD, '#ffc8a0', 0.45), 0.5, 3)
    out.append(d.form(body, HOOD, shift=28, soft=8, k=0.16, s=0.55, extra=bx))
    fold = mix(HOOD, '#120818', 0.5)
    out.append(f'<path d="M180,640 C196,620 206,600 212,580 M372,600 C368,630 370,660 376,690" fill="none" stroke="{fold}" stroke-width="1.6" opacity="0.6"/>')


def bust_over(d, out):
    """Drawn over the neck: the hood's front edge, the drawstrings and the headphones round the neck."""
    sh = '#1c1230'
    edge = 'M232,518 C246,500 268,506 282,524 C294,506 322,498 342,514 C336,540 312,552 284,552 C258,552 238,540 232,518Z'
    out.append(d.form(edge, mix(HOOD, '#1a0a20', 0.12), shift=8, soft=3, k=0.16, s=0.5))
    st = mix('#e8dccc', '#6a5a70', 0.2)
    out.append(f'<path d="M262,546 C260,574 262,600 258,628 M300,548 C304,574 302,596 306,620" fill="none" stroke="{st}" stroke-width="2.6" stroke-linecap="round"/>')
    # headphones: the band behind the neck, a cup on each side
    cup_far = 'M222,500 C234,494 248,500 250,516 C252,534 242,548 230,548 C218,546 212,532 214,516 C214,508 218,502 222,500Z'
    out.append(d.form(cup_far, LIME, shift=6, soft=2.5, k=0.2, s=0.5))
    cup = 'M330,494 C350,488 370,500 372,524 C374,548 360,566 340,566 C322,566 310,550 310,528 C310,510 318,498 330,494Z'
    cx = d.tone('M352,496 C376,516 372,556 348,570 L390,570 L390,490Z', sh, 0.45, 4)
    out.append(d.form(cup, LIME, shift=10, soft=3.5, k=0.2, s=0.5, extra=cx))
    out.append(d.form('M332,510 C344,506 356,514 356,528 C356,542 348,552 338,552 C328,550 322,540 322,528 C322,518 326,512 332,510Z',
                      PAD, shift=5, soft=2, s=0.4))


def figure(d, out, expr='calm'):
    """Full figure, ~6 heads: a slouch in one long curve — the head pushed forward and down, the back round, the
    hips forward, the weight on the near leg; one hand in the hoodie's pocket, the other lost in a long sleeve."""
    from common import place
    sh = '#1c1230'
    out.append(d.tone('M150,846 C190,834 290,834 330,846 C290,858 190,858 150,846Z', '#140c22', 0.6, 4))
    # narrow trousers: the far leg forward, its knee loose
    out.append(d.form('M206,508 C196,570 184,630 186,690 C186,726 188,760 188,792 L214,792 C216,760 220,726 224,690 C230,630 240,570 246,516Z',
                      TROUS, shift=7, soft=2.5, k=0.07, s=0.45))
    out.append(d.form('M252,516 C262,600 268,700 266,792 L294,792 C300,700 308,600 312,508Z', TROUS, shift=8, soft=2.5, k=0.07, s=0.55))
    # heavy boots: a thick sole, lime laces
    for bx, heel in ((0, 0), (80, 4)):
        boot = (f'M{184+bx},774 L{218+bx},774 L{220+bx},812 C{222+bx},828 {220+bx},838 {216+bx},846 L{154+bx+heel*3},846 '
                f'C{146+bx+heel*3},836 {152+bx+heel*3},822 {172+bx},812 C{180+bx},804 {184+bx},790 {184+bx},774Z')
        out.append(d.form(boot, BOOT, shift=6, soft=2.5, k=0.1, s=0.4,
                          extra=d.tone(f'M{150+bx},838 L{224+bx},838 L{224+bx},850 L{150+bx},850Z', '#0a060c', 0.8)))
        for i in range(4):
            y = 782 + i * 8
            out.append(f'<path d="M{184+bx - i*3.4:.1f},{y+4} L{198+bx - i*2:.1f},{y}" stroke="{LIME}" stroke-width="2.2" stroke-linecap="round"/>')
    # the far arm hangs, the sleeve down to the fingers
    far = 'M212,262 C194,272 186,312 182,362 C178,402 176,440 176,474 L200,478 C202,440 206,402 210,364 C214,322 220,292 228,274Z'
    out.append(d.form(far, HOOD, shift=8, soft=3, k=0.16, s=0.5))
    out.append(d.form('M179,474 C177,488 180,500 187,503 C194,504 199,494 198,478Z', SKIN, shift=4, soft=1.5, s=0.5))
    out.append(f'<path d="M185,482 L186,499 M191,482 L192,498" stroke="{mix(SKIN, INK, 0.45)}" stroke-width="1" stroke-linecap="round"/>')
    # the oversized hoodie: flat in front, a round back
    hoodie = ('M224,250 C202,256 190,278 188,308 C184,362 186,430 192,500 C194,512 198,520 206,524 '
              'C238,536 282,536 312,524 C320,518 322,508 322,496 C328,430 330,360 320,304 C312,268 292,250 264,246Z')
    hx = d.tone('M286,250 C320,290 328,380 322,470 C320,500 318,516 314,530 L350,530 L350,240Z', sh, 0.6, 6)
    hx += d.tone('M196,300 C192,350 194,400 198,440 L208,440 C204,400 204,350 208,302Z', mix(HOOD, '#ffc8a0', 0.45), 0.5, 4)
    hx += d.tone('M192,500 C230,514 290,514 322,500 L322,540 L192,540Z', mix(HOOD, '#120818', 0.5), 0.6, 2)
    out.append(d.form(hoodie, HOOD, shift=20, soft=6, k=0.16, s=0.55, extra=hx, rim=2.5, rimcol='#b890a8', rimop=0.55))
    fold = mix(HOOD, '#120818', 0.5)
    pocket = 'M210,420 L288,418 L300,480 L204,482Z'
    out.append(d.form(pocket, mix(HOOD, '#120818', 0.14), shift=8, soft=3, k=0.16, s=0.5))
    out.append(f'<path d="M222,330 C230,350 232,370 228,392 M300,360 C296,380 298,400 304,416" fill="none" stroke="{fold}" stroke-width="1.5" opacity="0.6"/>')
    # the near arm: the elbow back, the hand deep in the pocket
    near = 'M294,256 C318,264 332,300 334,342 C336,384 324,424 300,456 L276,440 C292,416 298,384 296,350 C294,316 286,290 274,272Z'
    out.append(d.form(near, HOOD, shift=12, soft=4, k=0.16, s=0.6,
                      extra=d.tone('M312,262 C340,310 342,400 312,460 L350,460 L350,250Z', sh, 0.5, 4)))
    out.append(f'<path d="M300,330 C306,340 314,344 324,344 M294,372 C302,380 312,382 322,378" fill="none" stroke="{fold}" stroke-width="1.5" opacity="0.6"/>')
    # the hood behind the neck, the head pushed forward and down
    hood = 'M240,240 C254,220 300,222 316,248 C324,272 306,290 282,290 C258,288 240,270 240,240Z'
    out.append(d.form(hood, mix(HOOD, '#1a0a20', 0.2), shift=10, soft=4, k=0.16, s=0.5))
    place(d, out, head34, 'kira', (224, 238), 0.44, rot=-8, expr=expr)
    # the hood's edge and the headphones over the neck
    edge = 'M212,256 C222,246 238,250 244,262 C254,252 272,252 280,262 C276,278 262,284 246,284 C230,284 216,274 212,256Z'
    out.append(d.form(edge, mix(HOOD, '#1a0a20', 0.1), shift=5, soft=2, k=0.16, s=0.5))
    st = mix('#e8dccc', '#6a5a70', 0.2)
    out.append(f'<path d="M232,282 C230,296 232,310 229,324 M252,284 C254,298 252,310 255,322" fill="none" stroke="{st}" stroke-width="1.8" stroke-linecap="round"/>')
    out.append(d.form('M206,244 C212,240 220,244 221,252 C222,262 216,268 210,268 C204,266 201,258 202,251Z', LIME, shift=3, soft=1.5, k=0.2, s=0.5))
    cup = 'M264,240 C275,237 286,244 287,257 C288,270 280,280 269,280 C259,280 252,271 252,259 C252,249 257,242 264,240Z'
    out.append(d.form(cup, LIME, shift=5, soft=2, k=0.2, s=0.5))
    out.append(d.form('M265,249 C272,247 278,252 278,259 C278,267 274,272 268,272 C263,271 260,266 260,259 C260,254 262,250 265,249Z', PAD, shift=3, soft=1.2, s=0.4))


def head_front(d, out, expr='calm'):
    e = EXPR[expr]
    sk = mix(SKIN, '#4a1848', 0.6)
    back = ('M250,98 C196,98 164,136 160,196 C158,240 160,290 166,330 L178,310 L186,342 L198,314 L208,330 L292,330 '
            'L304,316 L314,344 L324,312 L336,334 C342,290 344,240 340,196 C338,170 330,146 318,130 L326,116 L306,118 C290,104 270,98 250,98Z')
    out.append(d.form(back, HAIR, shift=12, soft=4, k=0.06, s=0.4, rim=2, rimcol='#b890a8', rimop=0.35,
                      extra=d.tone('M300,110 C336,150 344,240 334,340 L370,340 L370,100Z', '#120a16', 0.6, 8)))
    neck = 'M226,356 C230,390 228,420 224,452 L276,452 C272,420 270,390 274,356Z'
    out.append(d.form(neck, SKIN, shift=7, soft=3, extra=d.tone('M220,356 C240,392 262,392 280,356 L290,460 L220,460Z', sk, 0.88, 3)
                      + d.tone('M220,350 L280,350 L280,392 C262,402 240,402 220,392Z', '#3a1440', 0.35, 5)))
    face = ('M250,134 C206,134 184,170 182,216 C180,250 182,280 190,306 C198,334 222,368 250,374 '
            'C278,368 302,334 310,306 C318,280 320,250 318,216 C316,170 294,134 250,134Z')
    fx = [d.tone('M290,140 C310,190 312,250 304,300 C296,336 276,362 252,376 L340,380 L340,130Z', sk, 0.72, 5),
          d.tone('M262,252 C272,238 300,238 310,250 C306,268 280,274 266,270Z', '#6a3058', 0.36, 4),
          d.tone('M264,278 C276,286 294,284 304,274 C298,290 274,292 264,284Z', '#6a3058', 0.3, 2.5),
          d.tone('M268,298 C278,286 302,288 306,302 C302,316 280,318 270,310Z', ROSE, 0.3, 7),
          d.tone('M196,300 C206,288 226,290 230,302 C226,314 206,316 198,310Z', ROSE, 0.3, 7),
          d.tone('M170,310 C190,296 206,274 222,262 C244,240 286,226 330,226 L330,130 L170,130Z', '#6a2a50', 0.4, 5)]
    out.append(d.form(face, SKIN, shift=22, soft=8, s=0.5, rim=2.4, rimcol='#ffb89a', rimop=0.6, extra='\n'.join(fx)))
    lid = e['lid']
    out.append(eye(d, 216, 262, 15, 13.5, lid=lid, look=(0.25, -0.05), tilt=-1.5, skin=SKIN, iris='#5a6a52', wing=-1.2,
                   crease=0.3, low_lid=e['low'], lash=3.4, irr=0.84))
    out.append(eye(d, 284, 262, 15, 13.5, lid=lid, look=(0.25, -0.05), tilt=-1.5, skin=SKIN, iris='#5a6a52', wing=1.2,
                   crease=0.3, low_lid=e['low'], lash=3.4, irr=0.84))
    out.append(d.tone('M270,274 C280,280 294,280 302,272 C296,282 278,284 270,278Z', '#3a1a40', 0.35, 1.5))
    bc = mix(HAIR, INK, 0.3)
    out.append(brow((264, 243), (284, 236), (308, 239), 4.6, bc))
    out.append(brow((236, 243), (216, 236), (192, 239), 4.6, bc))
    nose = 'M242,276 C240,290 237,298 240,305 C244,311 256,311 260,305 C263,298 260,290 258,276Z'
    out.append(d.form(nose, mix(SKIN, ROSE, 0.14), shift=5, soft=2.2, s=0.4,
                      extra=d.tone('M238,304 C244,313 256,313 262,304 L262,316 L238,316Z', sk, 0.5, 1.5)))
    out.append(d.tone('M246,294 C248,291 252,291 254,294 C252,296 248,296 246,294Z', '#fff4e8', 0.8, 0.8))
    nl = mix(SKIN, INK, 0.55)
    out.append(f'<path d="M241,306 C243,309 246,309 248,307 M252,307 C254,309 257,309 259,306" fill="none" stroke="{nl}" stroke-width="1.4" stroke-linecap="round"/>')
    out.append('<g transform="translate(18,2)">')
    out.append(mouth(d, e['mouth']))
    out.append('</g>')
    lock = 'M300,180 C320,212 326,262 320,300 L312,334 L306,306 L296,322 C302,286 302,240 292,204Z'
    out.append(d.form(lock, HAIR, shift=8, soft=3, k=0.14, s=0.7))
    fringe = ('M296,106 C252,98 200,114 180,154 C168,184 166,224 170,258 L168,312 L184,282 L192,308 L204,272 L216,294 '
              'C226,264 244,242 266,230 C284,220 304,214 326,216 C330,176 318,130 296,106Z')
    hx = d.tone('M206,122 C232,108 264,106 288,112 C264,116 234,126 214,140Z', SHEEN, 0.75, 3)
    hx += d.tone('M178,176 C172,206 172,236 174,268 L182,268 C182,236 184,206 190,178Z', SHEEN, 0.5, 3)
    hx += d.tone('M286,112 C314,142 326,182 324,218 L350,218 L350,100Z', '#120a16', 0.55, 6)
    out.append(d.form(fringe, HAIR, shift=10, soft=3.5, k=0.08, s=0.4, extra=hx))
    hl = mix(HAIR, SHEEN, 0.55)
    out.append(f'<path d="M288,114 C250,128 216,156 200,270 M294,120 C268,142 252,178 248,236 M290,110 C234,116 192,156 182,276" '
               f'fill="none" stroke="{hl}" stroke-width="1.5" stroke-linecap="round" opacity="0.45"/>')


def head_side(d, out, expr='calm'):
    e = EXPR[expr]
    sk = mix(SKIN, '#4a1848', 0.6)
    neck = 'M236,350 C244,384 244,420 238,452 L302,456 C298,420 298,376 306,326Z'
    out.append(d.form(neck, SKIN, shift=9, soft=3.5, extra=d.tone('M232,360 C256,376 284,366 306,326 L320,460 L232,460Z', sk, 0.85, 4)))
    out.append(f'<g transform="{TILT}">')
    # the profile: a straight forehead, a small sharp nose, a short upper lip, a small firm chin
    face = ('M222,150 C206,166 198,192 198,218 C198,232 200,242 197,252 C192,264 184,278 176,290 '
            'C172,296 174,302 182,303 C186,304 190,304 192,306 C190,314 188,320 190,324 C186,330 188,336 192,338 '
            'C190,346 192,352 196,358 C200,368 212,374 226,372 C250,368 276,358 296,340 '
            'C316,322 330,290 334,250 C338,200 320,160 290,140 C264,126 238,134 222,150Z')
    fx = [d.tone('M300,140 C324,190 324,250 308,300 C294,332 264,356 232,372 L360,380 L360,130Z', sk, 0.55, 8),
          d.tone('M200,250 C212,240 234,244 242,256 C236,272 214,274 204,266Z', '#6a3058', 0.36, 4),
          d.tone('M218,290 C232,280 258,284 262,300 C256,314 232,314 220,304Z', ROSE, 0.32, 7),
          d.tone('M190,250 C210,226 250,212 330,224 L340,120 L190,120Z', '#6a2a50', 0.38, 5)]
    out.append(d.form(face, SKIN, shift=20, soft=7, s=0.5, rim=2.4, rimcol='#ffb89a', rimop=0.6, extra='\n'.join(fx)))
    out.append(d.tone('M178,292 C182,289 186,289 189,291 C186,294 181,295 178,292Z', '#fff4e8', 0.75, 0.8))
    out.append(f'<path d="M188,300 C192,298 196,300 196,304" fill="none" stroke="{mix(SKIN, INK, 0.55)}" stroke-width="1.5" stroke-linecap="round"/>')
    # lips pressed, the corner tucked in
    out.append(d.tone('M190,324 C196,320 204,320 210,323 C204,327 196,327 190,324Z', '#c2727a', 0.9))
    out.append(d.tone('M192,330 C198,334 206,334 210,329 C206,338 198,338 192,332Z', '#c2727a', 0.6, 1))
    out.append('<path d="M189,326 C198,328 208,328 216,326" fill="none" stroke="#5a2434" stroke-width="2" stroke-linecap="round"/>')
    out.append(f'<path d="M218,321 C221,324 221,328 218,331" fill="none" stroke="{mix(SKIN, INK, 0.5)}" stroke-width="1.4" stroke-linecap="round"/>')
    out.append(eye_side(218, 262, 1.2, iris='#5a6a52', skin=SKIN, lid=e['lid'], lash=1.4))
    out.append(d.tone('M210,272 C218,278 230,276 236,268 C232,280 216,282 210,276Z', '#3a1a40', 0.35, 1.5))
    out.append(brow((204, 244), (220, 237), (242, 240), 4.4, mix(HAIR, INK, 0.3)))
    # hair: the fringe hangs before the forehead, the rest is a short shaggy cap
    hair = ('M300,100 C262,94 226,108 208,140 C198,160 194,186 194,214 L186,256 L204,238 C214,228 228,220 244,216 L252,246 L262,213 '
            'C270,211 278,211 286,213 C296,250 296,290 284,328 L300,306 L306,334 L318,318 L334,310 L334,344 L354,318 L362,344 L378,314 L398,322 '
            'C398,284 398,244 392,212 C388,180 380,152 366,134 L378,120 L356,122 C340,108 322,101 300,100Z')
    hx = d.tone('M226,120 C250,108 280,106 302,112 C280,116 252,124 234,138Z', SHEEN, 0.75, 3)
    hx += d.tone('M204,160 C198,186 198,210 200,232 L210,226 C208,206 210,186 216,164Z', SHEEN, 0.5, 3)
    hx += d.tone('M300,130 C326,160 338,200 338,250 C330,206 318,170 292,146Z', SHEEN, 0.4, 5)
    hx += d.tone('M336,120 C372,160 388,240 368,350 L420,350 L420,100Z', '#120a16', 0.65, 8)
    out.append(d.form(hair, HAIR, shift=12, soft=4, k=0.06, s=0.4, extra=hx, rim=2, rimcol='#b890a8', rimop=0.35))
    hl = mix(HAIR, SHEEN, 0.55)
    out.append(f'<path d="M300,108 C262,116 230,140 210,220 M312,116 C300,140 300,180 314,224 M340,124 C360,170 366,240 356,310" '
               f'fill="none" stroke="{hl}" stroke-width="1.5" stroke-linecap="round" opacity="0.45"/>')
    out.append('</g>')


def _cup(d, out, cx, cy, r, shade=True):
    sh = '#1c1230'
    cup = (f'M{cx-r*0.2},{cy-r} C{cx+r*0.5},{cy-r*1.1} {cx+r},{cy-r*0.5} {cx+r},{cy+r*0.1} C{cx+r},{cy+r*0.8} {cx+r*0.5},{cy+r*1.25} {cx-r*0.1},{cy+r*1.25} '
           f'C{cx-r*0.7},{cy+r*1.25} {cx-r},{cy+r*0.7} {cx-r},{cy+r*0.1} C{cx-r},{cy-r*0.5} {cx-r*0.7},{cy-r*0.9} {cx-r*0.2},{cy-r}Z')
    out.append(d.form(cup, LIME, shift=r*0.32, soft=r*0.11, k=0.2, s=0.5))
    q = r * 0.52
    out.append(d.form(f'M{cx-q},{cy+r*0.12} a{q},{q*1.2} 0 1,0 {2*q},0 a{q},{q*1.2} 0 1,0 {-2*q},0Z', PAD, shift=q*0.4, soft=2, s=0.4))


def bust_front(d, out):
    sh = '#1c1230'
    hood = 'M170,524 C166,482 204,454 250,454 C296,454 334,482 330,524 C314,550 186,550 170,524Z'
    out.append(d.form(hood, mix(HOOD, '#1a0a20', 0.25), shift=14, soft=5, k=0.14, s=0.5))
    band = mix(LIME, '#20281a', 0.3)
    out.append(f'<path d="M198,526 C192,480 308,480 302,526" fill="none" stroke="{band}" stroke-width="9" stroke-linecap="round"/>')
    body = 'M112,700 L124,628 C134,576 162,542 200,528 L232,516 L268,516 L300,528 C338,542 366,576 376,628 L388,700Z'
    bx = d.tone('M292,520 C336,550 356,620 362,700 L400,700 L400,490Z', sh, 0.6, 8)
    bx += d.tone('M150,600 C162,570 182,550 204,538 C190,558 176,580 168,608Z', mix(HOOD, '#ffc8a0', 0.45), 0.5, 3)
    out.append(d.form(body, HOOD, shift=28, soft=8, k=0.16, s=0.55, extra=bx))


def bust_front_over(d, out):
    edge = 'M198,520 C212,502 236,508 250,526 C264,508 288,502 302,520 C298,542 276,554 250,554 C224,554 202,542 198,520Z'
    out.append(d.form(edge, mix(HOOD, '#1a0a20', 0.12), shift=8, soft=3, k=0.16, s=0.5))
    st = mix('#e8dccc', '#6a5a70', 0.2)
    out.append(f'<path d="M232,548 C230,576 232,602 228,630 M268,548 C272,576 270,598 274,622" fill="none" stroke="{st}" stroke-width="2.6" stroke-linecap="round"/>')
    _cup(d, out, 196, 522, 24)
    _cup(d, out, 306, 522, 24)


def bust_side(d, out):
    """In profile: the back round, the chest flat, the hood a heap behind the neck."""
    sh = '#1c1230'
    hood = 'M252,520 C250,476 290,452 330,460 C366,470 384,502 374,536 C350,556 270,552 252,520Z'
    out.append(d.form(hood, mix(HOOD, '#1a0a20', 0.25), shift=14, soft=5, k=0.14, s=0.5))
    body = 'M196,700 L200,620 C202,570 214,538 240,522 L276,512 L316,516 C350,530 372,570 378,630 L384,700Z'
    bx = d.tone('M310,514 C350,540 368,620 372,700 L400,700 L400,490Z', sh, 0.6, 8)
    out.append(d.form(body, HOOD, shift=26, soft=8, k=0.16, s=0.55, extra=bx))
    arm = 'M270,524 C304,522 322,552 322,600 L320,700 L270,700 L270,600 C270,566 264,542 270,524Z'
    out.append(d.form(arm, HOOD, shift=14, soft=5, k=0.16, s=0.55))


def bust_side_over(d, out):
    edge = 'M226,516 C240,500 262,504 272,520 C282,508 300,508 310,520 C306,544 286,554 262,554 C242,554 228,540 226,516Z'
    out.append(d.form(edge, mix(HOOD, '#1a0a20', 0.12), shift=8, soft=3, k=0.16, s=0.5))
    st = mix('#e8dccc', '#6a5a70', 0.2)
    out.append(f'<path d="M240,548 C238,576 240,600 236,626" fill="none" stroke="{st}" stroke-width="2.6" stroke-linecap="round"/>')
    _cup(d, out, 286, 520, 27)
