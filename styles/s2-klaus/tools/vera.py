"""Вера, about 40: strict, clever, tired. A long face with high cheekbones and a firm jaw, a long straight sharp
nose, thin pressed lips, heavy tired lids with bags, narrow glasses; dark hair pulled tight into a bun, one strand
escaped. A high-collared slate-blue dress with a white collar."""
from kit import mix
from parts import eye, brow, INK

SKIN = '#e0a888'
HAIR = '#2e1e26'
DRESS = '#34507a'
COLLAR = '#e8e0d4'
ROSE = '#c8686a'

EXPR = {
    'calm': dict(lid=0.5, brow=0, mouth='firm', look=(-0.35, 0.05)),
}


def head34(d, out, expr='calm'):
    e = EXPR[expr]
    sk = mix(SKIN, '#3a1838', 0.6)
    # bun at the back of the head
    bun = 'M336,150 C352,124 392,124 404,152 C414,178 400,206 376,212 C352,216 334,196 336,170Z'
    out.append(d.form(bun, HAIR, shift=18, soft=5, k=0.15, s=0.5, rim=2.5, rimcol='#c89a90', rimop=0.7,
                      extra=d.tone('M352,140 C366,132 384,134 394,146 C380,142 366,142 356,150Z', '#a08088', 0.6, 2)))
    # neck: long, straight
    neck = 'M262,370 C266,400 264,430 258,460 L328,464 C320,430 318,380 322,320Z'
    out.append(d.form(neck, SKIN, shift=10, soft=4, extra=d.tone('M252,360 C280,410 306,410 324,320 L340,480 L252,480Z', sk, 0.92, 3)))
    # face
    face = ('M214,146 C200,164 194,188 194,212 C194,226 198,234 196,244 C190,256 184,268 186,280 '
            'C190,298 200,312 204,328 C208,346 216,366 230,380 C238,386 250,386 260,380 '
            'C282,366 304,342 318,314 C328,292 332,264 330,236 C328,200 322,172 308,154 C284,132 240,130 214,146Z')
    fx = []
    fx.append(d.tone('M290,146 C298,180 298,214 292,240 C286,268 280,300 266,328 C256,350 248,368 240,386 '
                     'L350,400 L350,140Z', sk, 0.82, 3))
    # sockets, the bags under the eyes (tired)
    fx.append(d.tone('M240,246 C256,232 288,234 300,250 C298,268 266,274 246,266Z', '#7a3a50', 0.4, 5))
    fx.append(d.tone('M196,244 C204,238 220,240 226,250 C222,264 204,266 198,260Z', '#7a3a50', 0.32, 4))
    fx.append(d.tone('M248,274 C262,284 284,284 296,274 C290,286 262,290 248,280Z', '#7a3a50', 0.45, 2.5))
    # under the cheekbone: a long hollow plane
    fx.append(d.tone('M196,300 C208,318 220,336 236,346 C222,330 210,312 204,296Z', '#7a3a50', 0.35, 4))
    fx.append(d.tone('M256,296 C270,288 296,292 300,306 C294,318 268,318 258,308Z', ROSE, 0.3, 7))
    out.append(d.form(face, SKIN, shift=30, soft=8, s=0.5, extra='\n'.join(fx)))
    # small ear, the hair pulled back behind it
    ear = 'M318,252 C330,238 348,246 346,268 C344,290 334,304 322,304 C316,300 316,290 318,282 C312,272 312,262 318,252Z'
    out.append(d.form(ear, SKIN, shift=6, soft=2.5, s=0.55, extra=d.tone('M326,262 C336,256 342,266 338,282 C334,292 328,292 326,284 C330,276 330,268 326,262Z', sk, 0.8, 1.5)))
    # hair: pulled tight from a side parting over the skull to the bun, a smooth shape with a few lines
    hair = ('M262,96 C224,98 196,122 190,160 C188,176 190,192 194,206 C198,186 206,170 222,160 '
            'C244,148 272,146 292,150 C306,170 314,200 318,236 C320,250 324,256 330,256 '
            'C336,270 340,290 346,310 C358,300 366,280 368,250 C372,210 368,170 356,140 '
            'C344,112 312,94 262,96Z')
    hx = d.tone('M222,112 C248,100 286,100 312,110 C288,112 254,118 230,130Z', '#a08890', 0.7, 3)
    hx += d.tone('M320,120 C344,150 350,220 340,300 L380,300 L380,110Z', '#120a10', 0.6, 6)
    out.append(d.form(hair, HAIR, shift=10, soft=3, k=0.15, s=0.4, extra=hx, rim=2, rimcol='#c89a90', rimop=0.6))
    hl = mix(HAIR, '#a08890', 0.5)
    out.append(f'<path d="M226,128 C262,116 304,122 334,140 M206,160 C240,140 290,140 324,170 M300,104 C322,112 338,124 346,140" '
               f'fill="none" stroke="{hl}" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>')
    # one escaped strand by the face
    out.append(f'<path d="M206,164 C190,196 196,232 186,262 C182,276 184,290 194,298 C188,286 190,272 194,262 '
               f'C204,234 198,196 212,166Z" fill="{HAIR}"/>')
    # eyes: heavy tired lids
    lid, look = e['lid'], e['look']
    out.append(eye(d, 270, 258, 15, 12.5, lid=lid, look=look, tilt=0, skin=SKIN, iris='#3e4a3a', crease=0.4,
                   low_lid=0.1))
    out.append(eye(d, 212, 256, 8.5, 11.5, lid=lid, look=look, tilt=0, skin=SKIN, iris='#3e4a3a', wing=-0.3,
                   crease=0, lower=0.3, low_lid=0.1))
    # brows: straight, the inner ends a little down — strict
    bc = mix(HAIR, INK, 0.2)
    b = e['brow']
    out.append(brow((246, 236 + b), (272, 228 + b), (302, 232 + b), 4.2, bc))
    out.append(brow((224, 236 + b), (210, 230 + b), (196, 234 + b), 3.4, bc))
    # nose: long, straight, sharp
    nose = 'M232,240 C228,266 210,292 186,312 C182,318 186,322 194,322 C204,322 210,326 222,322 C230,318 234,310 232,300Z'
    nx = d.tone('M188,322 C204,322 210,326 226,320 L230,334 L184,334Z', '#5a2040', 0.55, 1.5)
    out.append(d.form(nose, mix(SKIN, ROSE, 0.1), shift=7, soft=2.2, s=0.45, extra=nx))
    out.append(d.tone('M222,262 C220,276 212,290 202,300 C214,290 222,278 226,264Z', '#fff0e0', 0.5, 1.2))
    out.append(f'<path d="M206,316 C210,312 216,313 218,318" fill="none" stroke="{mix(SKIN, INK, 0.55)}" stroke-width="1.6" stroke-linecap="round"/>')
    # mouth: thin, pressed, corners down a little
    out.append(d.tone('M214,348 C224,344 240,344 254,346 C242,350 226,352 214,348Z', '#9a4a50', 1))
    out.append(f'<path d="M210,352 C222,346 242,344 256,348" fill="none" stroke="#4a1a28" stroke-width="2" stroke-linecap="round"/>')
    out.append(d.tone('M218,353 C228,358 242,358 250,352 C244,362 226,362 218,353Z', '#c27070', 0.6, 1.5))
    # narrow glasses
    gl = '#2a2020'
    out.append(f'<path d="M248,248 L294,246 C296,256 294,266 288,270 L254,272 C248,266 246,256 248,248Z" fill="#d0e0f0" '
               f'opacity="0.12" stroke="{gl}" stroke-width="2"/>')
    out.append(f'<path d="M200,250 L226,248 C228,258 226,266 222,270 L204,270 C200,264 198,256 200,250Z" fill="#d0e0f0" '
               f'opacity="0.12" stroke="{gl}" stroke-width="1.8"/>')
    out.append(f'<path d="M226,252 C234,248 242,248 248,252 M294,250 L322,256" fill="none" stroke="{gl}" stroke-width="1.8"/>')
    out.append(f'<path d="M256,254 L270,252" stroke="#fff" stroke-width="1.6" opacity="0.6" stroke-linecap="round"/>')


def bust(d, out):
    sh = '#20182e'
    body = ('M140,700 L150,610 C158,556 190,520 232,500 L262,488 L300,484 L336,492 '
            'C384,512 410,556 418,610 L426,700Z')
    bx = d.tone('M330,490 C372,530 390,610 394,700 L440,700 L440,470Z', sh, 0.6, 8)
    bx += d.tone('M180,580 C192,548 212,528 236,514 C220,536 206,560 198,590Z', mix(DRESS, '#ffd8a0', 0.4), 0.5, 3)
    out.append(d.form(body, DRESS, shift=28, soft=8, k=0.12, s=0.55, extra=bx))
    # high collar of the dress, and a white collar folded over it
    out.append(d.form('M254,470 C272,462 310,462 330,472 L334,500 C312,494 276,494 252,500Z', DRESS, shift=8, soft=3, s=0.55))
    out.append(d.form('M250,498 C270,490 314,490 336,500 L330,526 L292,512 L254,528Z', COLLAR, shift=8, soft=3, s=0.45))
    # a small brooch
    out.append(d.form('M284,516 C290,510 298,510 302,516 C302,524 296,530 292,530 C286,530 282,524 284,516Z', '#8a3040', shift=3, soft=1.5))
    out.append(f'<circle cx="290" cy="517" r="1.6" fill="#fff" opacity="0.8"/>')
    # seams
    out.append(f'<path d="M292,530 L292,700" stroke="{mix(DRESS, "#000", 0.35)}" stroke-width="1.6"/>')
    for y in (560, 600, 640, 680):
        out.append(f'<circle cx="292" cy="{y}" r="2.6" fill="{mix(DRESS, "#000", 0.4)}"/>')


def figure(d, out, expr='calm'):
    """Full figure: tall, straight, arms folded; a long narrow dress. ~6.7 heads."""
    from common import place
    sh = '#1e1830'
    D = DRESS
    out.append(d.tone('M170,846 C200,834 300,834 330,846 C300,858 200,858 170,846Z', '#140c22', 0.6, 4))
    shoe = '#2a1e20'
    out.append(d.form('M214,814 L238,814 L238,836 C236,842 228,846 206,846 C198,842 204,832 214,826Z', shoe, shift=4, soft=1.5))
    out.append(d.form('M262,814 L286,814 L290,840 C286,846 270,846 262,844Z', shoe, shift=4, soft=1.5))
    # long dress: narrow, a little flare at the hem
    dress = ('M210,214 C204,260 210,330 222,380 C214,470 206,560 200,650 C196,730 194,790 192,822 '
             'C230,832 272,832 310,822 C306,760 302,700 296,640 C290,550 282,460 276,380 '
             'C290,330 298,260 292,214Z')
    dx = d.tone('M262,214 C290,280 286,340 270,390 C280,480 290,600 300,700 C304,760 308,800 312,830 L340,830 L340,200Z', sh, 0.6, 5)
    dx += d.tone('M210,500 C206,600 200,700 198,800 L212,800 C214,700 218,600 222,500Z', mix(D, '#ffd8a0', 0.35), 0.5, 4)
    out.append(d.form(dress, D, shift=22, soft=6, k=0.12, s=0.55, extra=dx, rim=2.5, rimcol='#c89aa0', rimop=0.6))
    fold = mix(D, '#000', 0.35)
    out.append(f'<path d="M240,420 C236,560 230,700 226,826 M262,420 C266,560 272,700 276,828" fill="none" stroke="{fold}" stroke-width="1.6" opacity="0.6"/>')
    out.append(f'<path d="M222,380 C240,388 262,388 276,380" fill="none" stroke="{fold}" stroke-width="2"/>')
    # the arms folded across the chest
    ua_l = 'M210,214 C196,232 192,270 196,304 C198,320 204,330 214,334 L228,320 C222,300 220,270 222,240Z'
    out.append(d.form(ua_l, D, shift=8, soft=3, k=0.12, s=0.5))
    ua_r = 'M292,214 C304,232 308,270 304,304 C302,322 296,332 286,336 L272,320 C278,300 280,268 278,240Z'
    out.append(d.form(ua_r, D, shift=8, soft=3, k=0.12, s=0.6, extra=d.tone('M290,214 C310,260 310,320 290,340 L320,340 L320,210Z', sh, 0.5, 3)))
    fa = 'M200,300 C230,290 270,290 304,300 C310,312 306,330 296,336 C266,330 232,330 206,336 C196,328 194,312 200,300Z'
    out.append(d.form(fa, D, shift=10, soft=3, k=0.12, s=0.55,
                      extra=d.tone('M200,326 C232,322 268,322 304,326 L304,340 L200,340Z', sh, 0.5, 3)))
    out.append(f'<path d="M210,316 C236,310 266,310 296,316" fill="none" stroke="{fold}" stroke-width="1.4" opacity="0.6"/>')
    cuff = COLLAR
    out.append(d.form('M268,296 L280,294 L284,312 L272,314Z', cuff, shift=3, soft=1))
    out.append(d.form('M226,294 C236,288 252,288 262,296 C264,306 254,312 242,312 C232,312 224,304 226,294Z', SKIN, shift=4, soft=1.5))
    out.append(f'<path d="M236,300 L254,298 M236,305 L252,304" stroke="{mix(SKIN, INK, 0.45)}" stroke-width="1" stroke-linecap="round"/>')
    # collar
    out.append(d.form('M226,206 C238,200 262,200 274,206 L270,222 L250,214 L230,222Z', COLLAR, shift=4, soft=2))
    out.append(d.form('M246,214 C249,210 254,210 256,214 C256,219 252,222 250,222 C248,222 245,219 246,214Z', '#8a3040', shift=2, soft=1))
    # neck and the head, held high
    out.append(d.form('M240,170 L262,170 L264,208 L238,208Z', SKIN, shift=3, soft=1.5, extra=d.tone('M236,166 L266,166 L266,206 L236,206Z', mix(SKIN, '#3a1838', 0.6), 0.75, 3)))
    out.append(d.form('M234,190 C244,184 262,184 270,190 L272,208 L232,208Z', D, shift=4, soft=1.5, k=0.12))
    place(d, out, head34, 'vera', (246, 192), 0.47, rot=-2, expr=expr)
