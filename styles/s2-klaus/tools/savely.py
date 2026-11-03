"""Савелий Петрович, about 70, a watchmaker: grumpy outside, kind inside. A big dome, a big ruddy nose,
bushy white brows and moustache as big soft shapes, small eyes under heavy lids, a jeweller's loupe pushed up
on the forehead, round glasses low on the nose. Hunched, a green waistcoat and a leather apron."""
from kit import mix
from parts import eye, brow, INK

SKIN = '#e2a68a'
WHITE = '#e8e2da'
VEST = '#3e5a48'
SHIRT = '#e6dccb'
APRON = '#7a4e30'
TROUS = '#3a3442'
ROSE = '#d0605a'
BRASS = '#c89a48'

EXPR = {
    'calm':  dict(lid=0.52, brow=0, mouth='grump', look=(-0.25, 0.1)),
    'kind':  dict(lid=0.45, brow=-3, mouth='smile', look=(-0.2, 0.0), low=0.3),
}


def head34(d, out, expr='calm'):
    e = EXPR[expr]
    sk = mix(SKIN, '#4a1838', 0.6)
    # tufts of white hair behind the ear, sticking back: three big locks
    tufts = ('M318,190 C350,176 392,186 404,214 C392,208 380,210 372,214 C396,224 408,246 404,272 '
             'C394,258 380,252 368,252 C384,268 388,292 378,310 C362,292 344,282 330,280Z')
    out.append(d.form(tufts, WHITE, shift=16, soft=5, k=0.2, s=0.45, rim=2.5, rimcol='#fff0d8', rimop=0.8))
    # neck: thick, forward
    neck = 'M262,380 C266,410 262,430 252,450 L360,456 C350,426 344,400 346,340Z'
    out.append(d.form(neck, SKIN, shift=10, soft=4, extra=d.tone('M250,370 C280,430 320,420 350,340 L370,500 L250,500Z', sk, 0.9, 4)))
    # ear: big, long lobe
    ear = 'M326,262 C340,246 362,252 364,276 C366,300 356,322 342,330 C332,334 326,326 328,316 C320,300 320,280 326,262Z'
    ex = d.tone('M336,272 C346,264 354,272 352,290 C350,304 342,312 338,306 C342,296 340,282 336,272Z', sk, 0.8, 1.5)
    # face: a big dome, a forehead that slopes to a heavy brow, a short chin under the moustache
    face = ('M206,140 C230,100 300,92 340,124 C370,150 376,200 362,250 C356,290 352,330 340,360 '
            'C326,396 296,424 262,430 C236,432 214,420 206,400 C196,370 190,330 192,300 '
            'C188,280 186,262 190,246 C186,228 186,210 190,196 C192,174 196,156 206,140Z')
    fx = []
    fx.append(d.tone('M318,120 C344,170 340,220 330,260 C320,300 316,350 296,392 C282,416 266,430 250,436 '
                     'L380,440 L380,110Z', sk, 0.85, 3.5))
    # the dome's sheen
    fx.append(d.tone('M232,120 C254,104 290,102 312,112 C292,112 262,118 240,132Z', '#fff2e0', 0.75, 4))
    # deep sockets under the brow
    fx.append(d.tone('M236,250 C252,238 292,240 306,256 C302,276 266,282 244,274Z', '#7a3048', 0.45, 5))
    fx.append(d.tone('M194,248 C200,242 214,244 220,254 C216,268 202,268 196,262Z', '#7a3048', 0.35, 4))
    # ruddy cheeks
    fx.append(d.tone('M256,292 C270,280 304,284 310,304 C304,322 270,324 258,312Z', ROSE, 0.5, 8))
    out.append(d.form(face, SKIN, shift=30, soft=9, s=0.5, extra='\n'.join(fx)))
    out.append(d.form(ear, SKIN, shift=8, soft=3, s=0.55, extra=ex))
    # wrinkles: few, as lines that follow the forms
    wl = mix(SKIN, '#5a2030', 0.5)
    out.append(f'<path d="M226,176 C248,168 280,168 300,176 M232,192 C252,186 276,186 292,192" fill="none" stroke="{wl}" '
               f'stroke-width="1.6" stroke-linecap="round" opacity="0.7"/>')
    out.append(f'<path d="M262,286 C272,292 286,292 296,286 M300,262 C306,270 308,280 306,288" fill="none" stroke="{wl}" '
               f'stroke-width="1.5" stroke-linecap="round" opacity="0.7"/>')
    # eyes: small, heavy lids
    lid, look = e['lid'], e['look']
    out.append(eye(d, 276, 262, 12, 10.5, lid=lid, look=look, tilt=-2, skin=SKIN, iris='#4a5a6a', crease=0.4,
                   low_lid=e.get('low', 0.12)))
    out.append(eye(d, 212, 258, 7, 10, lid=lid, look=look, tilt=1, skin=SKIN, iris='#4a5a6a', wing=-0.3, crease=0,
                   lower=0.3, low_lid=e.get('low', 0.12)))
    # bushy brows: big soft white shapes, the inner ends pulled down (grumpy)
    bd = e['brow']
    nb = (f'M244,{246+bd} C246,{230+bd} 262,{214+bd} 290,{212+bd} C312,{210+bd} 330,{220+bd} 340,{236+bd} '
          f'C332,{234+bd} 324,{236+bd} 318,{240+bd} C322,{246+bd} 324,{250+bd} 322,{254+bd} '
          f'C312,{246+bd} 296,{242+bd} 282,{244+bd} C270,{244+bd} 256,{248+bd} 244,{246+bd}Z')
    out.append(d.form(nb, WHITE, shift=8, soft=3, k=0.25, s=0.45,
                      extra=d.tone(f'M260,{220+bd} C280,{214+bd} 300,{214+bd} 320,{222+bd} C300,{220+bd} 280,{222+bd} 262,{228+bd}Z', '#ffffff', 0.7, 2)))
    fb = (f'M228,{246+bd} C226,{232+bd} 214,{222+bd} 198,{224+bd} C190,{226+bd} 184,{234+bd} 182,{242+bd} '
          f'C192,{238+bd} 204,{240+bd} 210,{246+bd} C216,{244+bd} 222,{246+bd} 228,{246+bd}Z')
    out.append(d.form(fb, WHITE, shift=6, soft=2, k=0.25, s=0.45))
    sl = mix(WHITE, '#6a5a70', 0.45)
    out.append(f'<path d="M270,{236+bd} C280,{230+bd} 296,{228+bd} 310,{232+bd} M296,{240+bd} C306,{238+bd} 316,{240+bd} 322,{246+bd}" '
               f'fill="none" stroke="{sl}" stroke-width="1.3" stroke-linecap="round" opacity="0.7"/>')
    # nose: big, ruddy, a round bulb at the end
    nose = ('M230,250 C228,270 214,290 196,304 C176,312 164,330 172,348 C180,362 200,364 214,356 '
            'C226,362 244,360 250,346 C254,330 246,316 238,304 C244,288 246,268 242,252Z')
    nx = d.tone('M172,348 C180,362 200,364 214,356 C226,362 244,360 250,346 L256,372 L170,372Z', '#5a1830', 0.6, 2)
    nx += d.tone('M200,312 C214,306 232,312 238,326 C226,320 210,320 200,324Z', '#fff0e0', 0.25, 3)
    out.append(d.form(nose, mix(SKIN, ROSE, 0.45), shift=12, soft=4, s=0.45, extra=nx))
    out.append(d.tone('M186,318 C192,312 200,312 204,316 C198,320 190,322 186,318Z', '#fff4e8', 0.85, 1))
    # moustache: a big drooping walrus shape over the mouth
    m = e['mouth']
    if m == 'smile':
        mo = ('M176,364 C190,350 216,352 232,362 C250,352 280,354 300,368 C312,378 318,392 322,404 '
              'C304,396 288,394 276,396 C262,392 246,384 232,382 C218,388 202,394 186,396 C176,396 168,392 160,394 '
              'C164,382 168,372 176,364Z')
    else:
        mo = ('M176,364 C190,350 216,352 232,362 C250,352 280,354 300,368 C312,380 316,400 316,420 '
              'C302,408 288,404 276,404 C262,398 246,390 232,388 C218,394 202,402 186,404 C176,404 166,410 158,418 '
              'C158,398 164,378 176,364Z')
    mx = d.tone('M232,362 C232,372 232,380 232,388', '#000', 0)
    mx += d.tone('M196,360 C210,356 226,360 232,366 C216,366 204,368 194,372Z', '#ffffff', 0.5, 2)
    out.append(d.form(mo, WHITE, shift=12, soft=4, k=0.2, s=0.45, extra=mx))
    hl = mix(WHITE, '#6a5a70', 0.5)
    out.append(f'<path d="M232,366 C230,376 230,384 232,388 M210,372 C206,382 200,390 192,398 M258,372 C266,382 278,392 290,398" '
               f'fill="none" stroke="{hl}" stroke-width="1.4" stroke-linecap="round" opacity="0.7"/>')
    if m == 'smile':
        out.append(f'<path d="M210,404 C222,412 240,412 252,402" fill="none" stroke="#5a2030" stroke-width="2" stroke-linecap="round"/>')
    # chin: a small round shape under the moustache
    out.append(d.tone('M214,418 C226,428 246,428 258,420 C252,432 228,434 214,418Z', sk, 0.6, 2))
    # round glasses low on the nose
    gl = '#6a5030'
    out.append(f'<ellipse cx="270" cy="276" rx="22" ry="19" fill="#d8e8f0" opacity="0.12" stroke="{gl}" stroke-width="2.4"/>')
    out.append(f'<ellipse cx="210" cy="272" rx="11" ry="17" fill="#d8e8f0" opacity="0.12" stroke="{gl}" stroke-width="2.2"/>')
    out.append(f'<path d="M221,272 C228,266 240,266 248,272 M292,272 L332,266" fill="none" stroke="{gl}" stroke-width="2"/>')
    out.append(f'<path d="M256,264 C262,260 270,260 276,262" fill="none" stroke="#fff" stroke-width="1.6" opacity="0.7" stroke-linecap="round"/>')
    # a jeweller's loupe pushed up on the forehead, on a band
    out.append(f'<path d="M214,156 C250,140 310,140 352,170" fill="none" stroke="#3a2a24" stroke-width="5" stroke-linecap="round"/>')
    lp = 'M244,150 C244,132 256,124 270,124 C284,124 294,132 294,150 L290,156 C282,150 258,150 248,156Z'
    out.append(d.form(lp, '#2e2a2a', shift=8, soft=2.5, s=0.5))
    out.append(d.form('M250,154 C258,146 282,146 290,154 C290,166 282,172 270,172 C258,172 250,166 250,154Z', BRASS, shift=5, soft=2))
    out.append(d.tone('M256,158 C262,152 278,152 284,158 C282,166 276,168 270,168 C262,168 256,164 256,158Z', '#7aa8b8', 0.95))
    out.append(d.tone('M260,157 C264,155 268,155 271,156 C268,158 263,159 260,157Z', '#ffffff', 0.85))


def bust(d, out):
    sh = '#2a1e40'
    body = ('M110,700 L118,600 C126,540 160,500 214,482 L262,470 C290,466 330,466 356,474 '
            'C404,490 432,540 440,600 L450,700Z')
    bx = d.tone('M340,470 C380,520 396,600 400,700 L460,700 L460,460Z', sh, 0.55, 8)
    out.append(d.form(body, SHIRT, shift=30, soft=8, s=0.5, extra=bx))
    # waistcoat
    vest = ('M150,700 L160,600 C168,560 190,530 226,512 L262,560 L300,520 L340,512 C370,530 392,566 400,610 L410,700Z')
    vx = d.tone('M330,520 C370,560 390,620 396,700 L420,700 L420,500Z', sh, 0.6, 6)
    out.append(d.form(vest, VEST, shift=26, soft=7, s=0.55, extra=vx))
    # collar and a small dark tie
    out.append(d.form('M240,476 L262,520 L282,476 C276,470 248,470 240,476Z', SHIRT, shift=6, soft=2))
    out.append(d.form('M222,480 L262,520 L246,532 L214,494Z', SHIRT, shift=6, soft=2, s=0.45))
    out.append(d.form('M300,480 L262,520 L282,534 L310,494Z', SHIRT, shift=6, soft=2, s=0.6))
    out.append(d.form('M254,516 L270,516 L276,560 L262,572 L250,560Z', '#6a2a2a', shift=4, soft=2))
    # watch chain
    out.append(f'<path d="M236,620 C256,642 300,644 330,624" fill="none" stroke="{BRASS}" stroke-width="2.4" stroke-dasharray="3 2"/>')
    for y in (590, 640, 690):
        out.append(f'<circle cx="{262 + (y-560)*0.02}" cy="{y}" r="4" fill="{mix(BRASS, "#3a2010", 0.3)}"/>')


def figure(d, out, expr='calm'):
    """Full figure: short, hunched, the head pushed forward, hands behind the back. ~5 heads. Canvas 500x900."""
    from common import place
    sh = '#2a1e40'
    out.append(d.tone('M150,846 C190,832 310,832 350,846 C310,860 190,860 150,846Z', '#140c22', 0.6, 4))
    # legs: trousers, knees a little bent
    out.append(d.form('M196,560 C192,640 196,720 204,816 L240,816 C238,730 240,650 246,570Z', TROUS, shift=10, soft=3, s=0.5))
    out.append(d.form('M250,560 C256,650 262,730 266,816 L298,816 C300,720 300,640 304,556Z', TROUS, shift=10, soft=3, s=0.6))
    shoe = '#3a2620'
    out.append(d.form('M200,808 L242,808 C246,820 246,836 242,846 L176,846 C168,840 172,826 188,820Z', shoe, shift=6, soft=2,
                      extra=d.tone('M182,826 C192,820 206,820 214,824', '#000', 0)))
    out.append(d.form('M262,808 L300,808 C304,820 304,836 300,846 L238,846 C232,838 238,826 252,820Z', shoe, shift=6, soft=2))
    # body: a hunched back, a round belly
    body = ('M222,310 C198,322 184,350 182,390 C178,440 180,490 188,530 C192,550 194,566 196,576 '
            'L310,576 C318,540 326,500 334,456 C342,410 344,360 326,330 C306,306 262,300 222,310Z')
    bx = d.tone('M300,300 C336,340 344,420 330,480 C320,520 312,550 310,580 L360,580 L360,290Z', sh, 0.6, 5)
    out.append(d.form(body, SHIRT, shift=22, soft=6, s=0.5, extra=bx))
    vest = ('M196,330 C182,360 178,420 182,470 C186,510 192,540 196,560 L304,560 C312,520 320,480 322,440 '
            'C326,400 322,360 306,330 L262,380 Z')
    vx = d.tone('M296,334 C320,380 322,450 312,500 C308,530 306,550 304,566 L340,566 L340,320Z', sh, 0.6, 5)
    out.append(d.form(vest, VEST, shift=20, soft=6, s=0.55, extra=vx))
    # leather apron: from the chest to the knees, a strap round the neck
    apron = 'M196,396 C190,470 184,560 182,650 C210,662 250,664 284,652 C288,560 286,470 280,396 C252,388 224,388 196,396Z'
    ax = d.tone('M260,398 C276,480 282,580 284,656 L310,656 L300,390Z', sh, 0.55, 5)
    ax += d.tone('M200,450 C212,446 232,446 244,452 L244,500 C232,494 212,494 200,500Z', '#000', 0)
    out.append(d.form(apron, APRON, shift=18, soft=5, s=0.55, extra=ax))
    out.append(d.form('M206,470 L250,470 L250,508 L206,508Z', mix(APRON, '#000', 0.2), shift=4, soft=1.5))  # a pocket
    out.append(f'<path d="M214,474 L216,500 M224,472 L224,500" stroke="#8a8a90" stroke-width="2.4" stroke-linecap="round"/>')  # tools
    out.append(f'<path d="M206,396 C210,360 220,340 232,328 M272,396 C272,370 270,350 266,334" fill="none" stroke="{mix(APRON, "#000", 0.3)}" stroke-width="3"/>')
    # watch chain across the waistcoat
    out.append(f'<path d="M286,420 C300,438 312,440 318,432" fill="none" stroke="{BRASS}" stroke-width="2" stroke-dasharray="3 2"/>')
    # the near arm, bent back, the hands hidden behind
    arm = 'M288,322 C310,330 322,362 324,400 C326,430 322,454 308,468 L290,460 C300,446 302,426 298,400 C294,372 286,352 274,340Z'
    out.append(d.form(arm, SHIRT, shift=14, soft=4, s=0.55, extra=d.tone('M310,330 C334,370 340,430 320,476 L350,476 L350,320Z', sh, 0.55, 4)))
    out.append(d.form('M288,456 L310,464 L306,480 L284,472Z', mix(SHIRT, '#5a4a40', 0.3), shift=3, soft=1.5))
    # neck and head, pushed forward
    out.append(d.form('M206,290 C212,276 240,268 270,276 L284,312 C260,320 228,318 210,312Z', SKIN, shift=4, soft=2, s=0.65,
                      extra=d.tone('M200,280 L290,280 L290,320 L200,320Z', mix(SKIN, '#4a1838', 0.6), 0.7, 3)))
    out.append(d.form('M204,300 C224,290 262,288 284,300 L278,318 C256,310 226,312 210,320Z', SHIRT, shift=4, soft=2))
    place(d, out, head34, 'savely', (206, 318), 0.56, rot=-4, expr=expr)
