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
    'calm':     dict(lid=0.38, low=0.12, brows=(0, 0), mouth='shut', look=(0.3, -0.05)),
    'smirk':    dict(lid=0.4, low=0.2, brows=(0, -2), mouth='smirk', look=(0.3, -0.05)),
    'joy':      dict(lid=0.36, low=0.36, brows=(-4, -3), mouth='halfsmile', look=(0.15, 0.1)),
    'surprise': dict(lid=0.02, low=0.0, brows=(-14, -12), mouth='o', look=(0.0, 0.0)),
    'sad':      dict(lid=0.56, low=0.05, brows=(2, 2), mouth='sad', look=(-0.25, 0.45), sad=True),
    'anger':    dict(lid=0.34, low=0.25, brows=(8, 8), mouth='angry', look=(0.3, -0.05), angry=True),
}
TILT = 'rotate(-6,300,330)'   # the head is held down: everything above the neck is turned about the nape


def mouth(d, kind):
    """Thin lips: a dark line and a faint shadow under the lower lip — no painted lips."""
    return '<g transform="translate(0,-13)">' + _mouth(d, kind) + '</g>'


def _mouth(d, kind):
    line = '#6a2c3a'
    lip = '#c88080'
    dim = mix(SKIN, INK, 0.45)
    under = d.tone('M220,341 C228,344 238,343 245,339 C239,346 226,347 220,341Z', '#7a3a58', 0.28, 1.8)
    if kind == 'shut':       # pressed shut, a little crooked: the near corner tucked in
        return '\n'.join([
            f'<path d="M212,333 C224,336 240,336 253,333" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>',
            f'<path d="M254,329 C257,331 257,335 255,338" fill="none" stroke="{dim}" stroke-width="1.4" stroke-linecap="round"/>',
            under])
    if kind == 'smirk':      # pressed, the near corner pulled up and back
        return '\n'.join([
            f'<path d="M210,334 C222,337 240,334 254,323" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>',
            f'<path d="M256,317 C260,320 260,325 257,328" fill="none" stroke="{dim}" stroke-width="1.4" stroke-linecap="round"/>',
            under])
    if kind == 'halfsmile':  # the most she allows: lips shut, the corners up, a dimple
        return '\n'.join([
            f'<path d="M210,331 C221,338 241,335 255,322" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>',
            f'<path d="M258,315 C262,319 262,324 258,328" fill="none" stroke="{dim}" stroke-width="1.4" stroke-linecap="round"/>',
            d.tone('M220,342 C228,346 240,344 247,338 C241,348 226,349 220,342Z', '#7a3a58', 0.28, 1.8)])
    if kind == 'o':
        return '\n'.join([
            f'<path d="M220,328 C225,322 237,322 241,329 C244,338 239,346 231,346 C223,346 217,338 220,328Z" fill="#4a1a26"/>',
            f'<path d="M223,327 C227,324 235,324 238,328 C235,331 227,331 223,327Z" fill="#f4ece4"/>',
            d.tone('M224,341 C228,337 235,337 238,342 C235,346 227,346 224,341Z', '#c45a64', 0.9, 0.8)])
    if kind == 'sad':        # pressed tight, the corners down, the lower lip pushed out
        return '\n'.join([
            f'<path d="M212,338 C221,331 238,329 251,335" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>',
            d.tone('M219,339 C227,336 238,336 245,339 C239,345 226,345 219,339Z', lip, 0.55, 1.2),
            d.tone('M220,349 C227,346 238,346 245,349 C238,353 227,353 220,349Z', '#7a3a58', 0.28, 2)])
    if kind == 'angry':      # a snarl: the upper lip lifted on the near side, the teeth shut
        return '\n'.join([
            f'<path d="M210,338 C219,331 240,324 254,327 C254,338 243,345 228,346 C219,346 212,343 210,338Z" fill="#4a1a26"/>',
            f'<path d="M214,338 C223,333 240,328 251,330 C250,337 241,341 228,342 C221,342 216,340 214,338Z" fill="#f4ece4"/>',
            f'<path d="M216,339 C227,336 241,334 251,335" fill="none" stroke="#4a1a26" stroke-width="1.1"/>',
            f'<path d="M206,340 C217,329 241,320 256,325" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>'])
    raise ValueError(kind)


def head34(d, out, expr='calm'):
    e = EXPR[expr]
    sk = mix(SKIN, '#4a1848', 0.6)
    # neck: thin, long, leaning forward
    neck = 'M256,334 C261,370 259,400 254,432 L310,436 C305,400 304,366 312,306Z'
    out.append(d.form(neck, SKIN, shift=9, soft=3.5, extra=d.tone('M246,330 C272,384 300,380 316,300 L330,480 L246,480Z', sk, 0.92, 3)
                      + d.tone('M240,326 L330,290 L330,384 C300,394 270,388 240,368Z', '#3a1440', 0.3, 6)))
    out.append(f'<g transform="{TILT}">')
    # the hair behind: a short shaggy mass that ends in choppy points at the nape
    back = ('M300,100 C258,96 220,112 204,146 C240,140 290,150 316,190 C324,214 326,244 326,268 '
            'C326,290 322,306 316,322 L334,310 L334,344 L354,318 L362,344 L378,314 L398,322 '
            'C399,304 399,288 397,274 L409,262 L395,256 C395,240 394,226 392,212 C388,180 380,152 366,134 L378,120 L356,122 C340,108 322,101 300,100Z')
    bx = d.tone('M336,120 C372,160 388,240 368,350 L420,350 L420,100Z', '#120a16', 0.65, 8)
    bx += d.tone('M320,130 C344,160 354,200 354,240 C346,204 334,170 312,146Z', SHEEN, 0.5, 5)
    out.append(d.form(back, HAIR, shift=12, soft=4, k=0.06, s=0.4, extra=bx, rim=2, rimcol='#b890a8', rimop=0.35))
    # face: a short lower face, a round young cheek, a small soft chin
    face = ('M212,152 C200,172 194,198 194,222 C194,238 197,248 195,258 C190,268 187,280 189,292 '
            'C191,304 197,316 205,326 C213,338 223,348 235,352 C243,355 253,353 261,348 '
            'C284,338 306,320 317,297 C325,279 328,256 326,232 C324,200 318,172 304,154 C282,134 236,134 212,152Z')
    fx = [d.tone('M294,150 C302,186 300,222 295,250 C290,276 284,298 270,318 C260,332 250,344 242,356 L350,380 L350,140Z', sk, 0.8, 4),
          d.tone('M240,258 C256,246 290,248 302,264 C298,280 266,286 246,278Z', '#7a3a60', 0.22, 5),
          d.tone('M250,298 C266,286 300,290 305,308 C298,324 266,324 254,312Z', ROSE, 0.42, 8),
          # the fringe's cast shadow
          d.tone('M186,300 C200,290 214,272 228,264 C244,246 280,228 330,224 L340,130 L180,130Z', '#6a2a50', 0.36, 5)]
    out.append(d.form(face, SKIN, shift=30, soft=8, s=0.5, rim=2.4, rimcol='#ffb89a', rimop=0.6, extra='\n'.join(fx)))
    # eyes: big enough for fifteen, set low, a dark lash line; the far one is under the fringe
    lid, look = e['lid'], e['look']
    out.append(eye(d, 267, 269, 18, 15.5, lid=lid, look=look, tilt=-1.5, skin=SKIN, iris='#5a6a52', crease=0.25,
                   low_lid=e['low'], lash=3.2, wing=1.1, irr=0.86, lower=0.35))
    out.append(eye(d, 208, 265, 9, 13.5, lid=lid, look=look, tilt=0, skin=SKIN, iris='#5a6a52', wing=-0.3, crease=0,
                   lower=0.3, low_lid=e['low'], lash=2.8, irr=0.86))
    # brows: straight and low, the inner end pulled down — the prickliness is here
    bc = mix(HAIR, INK, 0.3)
    bn, bf = e['brows']
    if e.get('sad'):
        out.append(brow((244, 240 + bn), (268, 240 + bn), (298, 251 + bn), 4.6, bc))
        out.append(brow((226, 240 + bf), (212, 240 + bf), (198, 248 + bf), 3.6, bc))
    elif e.get('angry'):
        out.append(brow((242, 252 + bn - 6), (266, 242 + bn - 8), (298, 237 + bn - 8), 5, bc))
        out.append(brow((228, 250 + bf - 6), (212, 244 + bf - 8), (198, 240 + bf - 8), 4, bc))
    else:
        out.append(brow((242, 249 + bn), (266, 241 + bn), (298, 243 + bn), 4.6, bc))
        out.append(brow((228, 247 + bf), (212, 243 + bf), (198, 245 + bf), 3.6, bc))
    # nose: small and soft, a round tip a little up
    nose = 'M223,266 C221,276 213,285 202,291 C197,294 197,300 203,302 C210,303 215,304 221,301 C226,298 227,292 226,286Z'
    nx = d.tone('M199,301 C209,303 215,304 223,300 L226,310 L196,310Z', '#6a2a50', 0.4, 1.5)
    out.append(d.form(nose, mix(SKIN, ROSE, 0.12), shift=6, soft=2.4, s=0.4, extra=nx))
    out.append(d.tone('M202,293 C205,290 209,290 211,292 C208,295 205,296 202,293Z', '#fff4e8', 0.8, 0.8))
    out.append(f'<path d="M210,299 C213,297 217,298 218,301" fill="none" stroke="{mix(SKIN, INK, 0.5)}" stroke-width="1.4" stroke-linecap="round"/>')
    out.append(mouth(d, e['mouth']))
    # a lock in front of the ear
    lock = 'M300,168 C322,200 330,250 324,290 L314,326 L308,298 L296,318 C300,282 300,240 290,200Z'
    out.append(d.form(lock, HAIR, shift=8, soft=3, k=0.14, s=0.7))
    # the fringe: from a parting on the near side, across the forehead and down over the far eye, cut in points
    fringe = ('M308,104 C270,98 224,110 202,146 C188,172 184,212 186,248 L180,304 L196,274 L202,300 L215,272 L226,292 '
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
    body = ('M146,770 L160,626 C170,574 198,540 236,526 L266,514 L302,512 L334,520 C374,536 398,574 406,626 L414,770Z')
    bx = d.tone('M322,514 C364,548 380,620 384,770 L430,770 L430,490Z', sh, 0.6, 8)
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
    place(d, out, head34, 'kira', (224, 240), 0.47, rot=-8, expr=expr)
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
    neck = 'M227,340 C230,372 229,402 225,432 L275,432 C271,402 270,372 273,340Z'
    out.append(d.form(neck, SKIN, shift=7, soft=3, extra=d.tone('M220,340 C240,376 262,376 280,340 L290,460 L220,460Z', sk, 0.88, 3)
                      + d.tone('M220,334 L280,334 L280,376 C262,386 240,386 220,376Z', '#3a1440', 0.3, 5)))
    face = ('M250,134 C206,134 184,170 182,216 C180,250 181,278 187,300 C194,326 220,354 250,358 '
            'C280,354 306,326 313,300 C319,278 320,250 318,216 C316,170 294,134 250,134Z')
    fx = [d.tone('M292,140 C312,190 314,250 308,296 C300,326 278,348 252,360 L340,380 L340,130Z', sk, 0.68, 5),
          d.tone('M262,258 C272,246 302,246 312,258 C308,274 282,280 266,276Z', '#7a3a60', 0.2, 4),
          d.tone('M270,300 C280,288 306,290 310,304 C306,318 282,320 272,312Z', ROSE, 0.4, 7),
          d.tone('M194,302 C204,290 226,292 230,304 C226,316 206,318 196,312Z', ROSE, 0.4, 7),
          d.tone('M170,310 C190,296 206,276 222,264 C244,242 286,228 330,228 L330,130 L170,130Z', '#6a2a50', 0.36, 5)]
    out.append(d.form(face, SKIN, shift=22, soft=8, s=0.5, rim=2.4, rimcol='#ffb89a', rimop=0.6, extra='\n'.join(fx)))
    lid = e['lid']
    for o, x in ((-1, 215), (1, 285)):
        out.append(eye(d, x, 269, 17, 15.5, lid=lid, look=(0.25, -0.05), tilt=-1.5, skin=SKIN, iris='#5a6a52', wing=o * 1.1,
                       crease=0.25, low_lid=e['low'], lash=3.2, irr=0.86, lower=0.35))
    bc = mix(HAIR, INK, 0.3)
    out.append(brow((262, 249), (284, 241), (310, 244), 4.6, bc))
    out.append(brow((238, 249), (216, 241), (190, 244), 4.6, bc))
    nose = 'M243,284 C241,292 239,298 242,303 C245,308 255,308 258,303 C261,298 259,292 257,284Z'
    out.append(d.form(nose, mix(SKIN, ROSE, 0.12), shift=5, soft=2.4, s=0.35,
                      extra=d.tone('M240,302 C245,310 255,310 260,302 L260,312 L240,312Z', sk, 0.45, 1.5)))
    out.append(d.tone('M246,295 C248,292 252,292 254,295 C252,297 248,297 246,295Z', '#fff4e8', 0.8, 0.8))
    nl = mix(SKIN, INK, 0.5)
    out.append(f'<path d="M243,304 C245,306 247,306 248,305 M252,305 C253,306 255,306 257,304" fill="none" stroke="{nl}" stroke-width="1.3" stroke-linecap="round"/>')
    out.append('<g transform="translate(18,1)">')
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
    neck = 'M240,336 C246,370 246,402 241,432 L300,436 C297,402 298,362 306,314Z'
    out.append(d.form(neck, SKIN, shift=9, soft=3.5, extra=d.tone('M232,344 C256,362 284,352 306,314 L320,460 L232,460Z', sk, 0.85, 4)))
    out.append(f'<g transform="{TILT}">')
    # the profile: a round forehead, a small soft nose a little up, a short lower face, a small round chin
    face = ('M222,150 C206,166 198,192 198,218 C198,234 200,246 198,256 C195,266 189,275 183,283 '
            'C179,288 180,294 187,295 C190,296 193,297 194,300 C192,305 192,309 194,312 C192,316 193,320 196,322 '
            'C195,328 196,334 200,339 C206,348 218,353 232,351 C256,347 282,337 300,321 '
            'C318,304 330,280 334,250 C338,200 320,160 290,140 C264,126 238,134 222,150Z')
    fx = [d.tone('M300,140 C324,190 324,250 310,292 C296,320 266,340 236,352 L360,370 L360,130Z', sk, 0.5, 8),
          d.tone('M202,258 C214,248 236,252 244,264 C238,280 216,282 206,274Z', '#7a3a60', 0.22, 4),
          d.tone('M220,294 C236,282 266,286 270,304 C264,320 236,320 224,310Z', ROSE, 0.42, 8),
          d.tone('M190,252 C210,228 250,214 330,226 L340,120 L190,120Z', '#6a2a50', 0.34, 5)]
    out.append(d.form(face, SKIN, shift=20, soft=7, s=0.5, rim=2.4, rimcol='#ffb89a', rimop=0.6, extra='\n'.join(fx)))
    out.append(d.tone('M184,287 C187,284 191,284 193,286 C190,289 187,290 184,287Z', '#fff4e8', 0.75, 0.8))
    out.append(f'<path d="M191,293 C194,291 198,293 198,296" fill="none" stroke="{mix(SKIN, INK, 0.5)}" stroke-width="1.4" stroke-linecap="round"/>')
    # thin lips pressed into a line, the corner tucked in
    out.append('<path d="M193,313 C200,314 208,315 215,315" fill="none" stroke="#6a2c3a" stroke-width="1.9" stroke-linecap="round"/>')
    out.append(f'<path d="M216,311 C219,313 219,317 217,320" fill="none" stroke="{mix(SKIN, INK, 0.45)}" stroke-width="1.3" stroke-linecap="round"/>')
    out.append(d.tone('M198,321 C203,324 210,324 214,320 C210,327 202,327 198,321Z', '#7a3a58', 0.25, 1.5))
    out.append(eye_side(219, 269, 1.45, iris='#5a6a52', skin=SKIN, lid=e['lid'], lash=1.2))
    out.append(brow((203, 251), (220, 244), (244, 247), 4.4, mix(HAIR, INK, 0.3)))
    # hair: the fringe hangs before the forehead, the rest is a short shaggy cap
    hair = ('M300,100 C262,94 226,108 208,140 C198,160 194,186 194,214 L186,256 L204,238 C214,228 228,220 244,216 L252,246 L262,213 '
            'C270,211 278,211 286,213 C296,250 296,290 284,328 L300,306 L306,334 L318,318 L334,310 L334,344 L354,318 L362,344 L378,314 L398,322 '
            'C399,304 399,288 397,274 L409,262 L395,256 C395,240 394,226 392,212 C388,180 380,152 366,134 L378,120 L356,122 C340,108 322,101 300,100Z')
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
    body = 'M112,770 L124,628 C134,576 162,542 200,528 L232,516 L268,516 L300,528 C338,542 366,576 376,628 L388,770Z'
    bx = d.tone('M292,520 C336,550 356,620 362,770 L400,770 L400,490Z', sh, 0.6, 8)
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
    body = 'M196,770 L200,620 C202,570 214,538 240,522 L276,512 L316,516 C350,530 372,570 378,630 L384,770Z'
    bx = d.tone('M310,514 C350,540 368,620 372,770 L400,770 L400,490Z', sh, 0.6, 8)
    out.append(d.form(body, HOOD, shift=26, soft=8, k=0.16, s=0.55, extra=bx))
    arm = 'M270,524 C304,522 322,552 322,600 L320,770 L270,770 L270,600 C270,566 264,542 270,524Z'
    out.append(d.form(arm, HOOD, shift=14, soft=5, k=0.16, s=0.55))


def bust_side_over(d, out):
    edge = 'M226,516 C240,500 262,504 272,520 C282,508 300,508 310,520 C306,544 286,554 262,554 C242,554 228,540 226,516Z'
    out.append(d.form(edge, mix(HOOD, '#1a0a20', 0.12), shift=8, soft=3, k=0.16, s=0.5))
    st = mix('#e8dccc', '#6a5a70', 0.2)
    out.append(f'<path d="M240,548 C238,576 240,600 236,626" fill="none" stroke="{st}" stroke-width="2.6" stroke-linecap="round"/>')
    _cup(d, out, 286, 520, 27)
