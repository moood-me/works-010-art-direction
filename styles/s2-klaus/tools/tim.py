"""Тим, about 8: mischievous, curious. A big round cranium, puffy cheeks, a small chin, a button nose turned up,
big ears, freckles, straw hair in a few pointed tufts, a gap-toothed sideways grin. A brick-red sweater."""
from kit import mix
from parts import eye, brow, INK

SKIN = '#f0b896'
HAIR = '#c89848'
HAIR_D = mix(HAIR, '#3a1a20', 0.5)
SWEATER = '#a8402e'
SHORTS = '#5a4a3a'
SOCKS = '#d8cfc0'
BOOT = '#4a2e22'
ROSE = '#e06a5a'

EXPR = {
    'calm':     dict(lid=0.22, brows=(-6, 4), mouth='grin', look=(-0.45, 0.0), low=0.18),
    'joy':      dict(lid=0.2, brows=(-8, -8), mouth='laugh', look=(-0.2, 0.0), low=0.45),
    'surprise': dict(lid=0.0, brows=(-16, -16), mouth='o', look=(-0.1, -0.05)),
    'sad':      dict(lid=0.45, brows=(8, 8), mouth='sad', look=(-0.1, 0.4), sad=True),
    'anger':    dict(lid=0.35, brows=(8, 8), mouth='angry', look=(-0.3, 0.0), angry=True),
}


def head34(d, out, expr='calm'):
    e = EXPR[expr]
    sk = mix(SKIN, '#4a1838', 0.58)
    # neck: thin, a child's
    neck = 'M236,384 C240,404 238,424 232,444 L306,448 C300,424 298,400 304,366Z'
    out.append(d.form(neck, SKIN, shift=8, soft=3, extra=d.tone('M236,370 C260,410 282,410 300,360 L310,480 L236,480Z', sk, 0.9, 3)))
    # big ear (near side)
    ear = 'M318,256 C336,232 368,240 370,272 C372,302 356,326 334,330 C322,332 316,322 320,312 C312,294 310,272 318,256Z'
    ex = d.tone('M330,266 C344,254 360,266 356,288 C352,306 340,314 334,306 C340,294 338,278 330,266Z', sk, 0.75, 1.5)
    ex += d.tone('M340,250 C356,250 366,262 368,280 C362,268 352,258 340,256Z', ROSE, 0.5, 2)
    # head: a big round cranium, round cheeks, a small chin
    face = ('M200,150 C236,110 316,110 346,160 C366,196 368,240 356,280 C348,320 336,350 312,372 '
            'C292,390 266,398 244,398 C224,398 206,388 196,372 C184,354 176,336 174,316 '
            'C170,296 172,276 178,258 C176,236 180,212 188,190 C190,176 194,162 200,150Z')
    fx = []
    fx.append(d.tone('M318,150 C340,200 338,250 326,290 C316,320 300,350 282,372 C268,388 256,396 244,400 '
                     'L380,420 L380,140Z', sk, 0.8, 4))
    fx.append(d.tone('M238,250 C254,238 288,240 302,256 C298,276 264,282 244,274Z', '#9a4c5c', 0.25, 5))
    # round cheeks, flushed
    fx.append(d.tone('M246,300 C262,286 298,290 304,312 C298,332 262,334 248,320Z', ROSE, 0.5, 8))
    fx.append(d.tone('M176,300 C184,292 196,296 196,310 C192,322 180,320 176,314Z', ROSE, 0.45, 5))
    # hair's cast shadow on the forehead
    fx.append(d.tone('M184,206 C210,226 240,236 270,226 C292,220 316,230 340,244 L350,140 L180,140Z', '#8a3a40', 0.35, 6))
    out.append(d.form(face, SKIN, shift=30, soft=9, s=0.5, extra='\n'.join(fx)))
    out.append(d.form(ear, SKIN, shift=8, soft=3, s=0.5, extra=ex))
    # freckles
    for x, y in ((252, 296), (262, 302), (274, 298), (266, 312), (284, 306), (244, 308), (186, 300), (192, 310), (204, 288), (212, 296)):
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="2.1" ry="1.6" fill="#b0603e" opacity="0.65"/>')
    # eyes: big, a child's; a sideways mischievous look
    lid, look = e['lid'], e['look']
    out.append(eye(d, 264, 262, 19, 18, lid=lid, look=look, tilt=2, skin=SKIN, iris='#4a6a7a', crease=0.25,
                   low_lid=e.get('low', 0), irr=0.84))
    out.append(eye(d, 200, 258, 11, 17, lid=lid + (0.08 if expr == 'calm' else 0), look=look, tilt=-1, skin=SKIN,
                   iris='#4a6a7a', wing=-0.3, crease=0, lower=0.3, low_lid=e.get('low', 0), irr=0.84))
    # brows: short, thick, the near one raised (curious), the far one down (scheming)
    bc = mix(HAIR, INK, 0.45)
    bn, bf = e['brows']
    if e.get('sad'):
        out.append(brow((244, 232 + bn - 8), (266, 226 + bn - 2), (290, 236 + bn), 5, bc))
        out.append(brow((214, 228 + bf - 8), (204, 226 + bf - 3), (190, 234 + bf), 4.2, bc))
    elif e.get('angry'):
        out.append(brow((244, 238 + bn - 4), (266, 226 + bn - 6), (292, 222 + bn - 10), 5.4, bc))
        out.append(brow((216, 236 + bf - 4), (204, 230 + bf - 6), (190, 226 + bf - 8), 4.6, bc))
    else:
        out.append(brow((244, 232 + bn), (266, 220 + bn), (290, 228 + bn), 5, bc))
        out.append(brow((216, 230 + bf), (204, 226 + bf), (190, 232 + bf), 4.2, bc))
    # button nose turned up
    nose = 'M214,270 C208,286 194,296 180,300 C170,304 170,316 180,320 C190,324 204,322 214,318 C222,312 222,300 218,292Z'
    nx = d.tone('M178,318 C190,324 204,322 214,318 L216,330 L174,330Z', '#6a2a40', 0.5, 2)
    nx += d.tone('M182,300 C190,296 200,298 206,304 C200,306 190,306 182,306Z', ROSE, 0.4, 3)
    out.append(d.form(nose, mix(SKIN, ROSE, 0.22), shift=7, soft=2.5, s=0.45, extra=nx))
    out.append(d.tone('M180,304 C184,301 188,301 191,303 C187,305 183,306 180,304Z', '#fff4e0', 0.85, 0.8))
    out.append(f'<path d="M192,314 C196,311 201,312 203,316" fill="none" stroke="{mix(SKIN, INK, 0.5)}" stroke-width="1.6" stroke-linecap="round"/>')
    out.append(mouth(d, e['mouth']))
    # hair: a few big pointed tufts from the crown; a fringe in three points over the forehead
    hair = ('M196,176 C186,150 196,120 222,104 C214,92 216,80 226,72 C238,84 248,90 262,92 '
            'C266,78 280,68 296,66 C294,80 296,90 304,98 C322,90 344,94 356,104 C346,110 342,118 342,128 '
            'C362,138 380,160 384,190 C372,186 366,188 362,192 C374,212 376,236 368,256 '
            'C360,248 352,244 344,244 C340,232 332,222 322,214 C316,222 308,226 298,228 '
            'C294,216 286,206 274,200 C264,214 250,224 232,228 C236,216 236,206 230,198 '
            'C218,206 208,216 194,222 C198,206 198,190 196,176Z')
    hx = d.tone('M222,104 C246,94 280,92 304,98 C280,104 250,110 228,122Z', mix(HAIR, '#fff0c0', 0.55), 0.85, 3)
    hx += d.tone('M226,72 C238,84 248,90 262,92 C252,96 240,96 232,92Z', mix(HAIR, '#fff0c0', 0.5), 0.7, 2)
    hx += d.tone('M318,110 C350,140 376,190 370,260 L400,260 L400,100Z', HAIR_D, 0.75, 8)
    hx += d.tone('M300,170 C320,190 340,210 350,250 L380,250 L380,160Z', HAIR_D, 0.5, 6)
    out.append(d.form(hair, HAIR, shift=8, soft=3, k=0.22, s=0.4, extra=hx, rim=2.5, rimcol='#ffe0a0', rimop=0.7))
    hl = mix(HAIR, '#3a1a20', 0.45)
    out.append(f'<path d="M262,92 C268,120 270,160 274,200 M304,98 C314,130 320,170 322,214 M342,128 C352,150 360,170 362,192" '
               f'fill="none" stroke="{hl}" stroke-width="1.8" stroke-linecap="round" opacity="0.45"/>')


def mouth(d, kind):
    line = '#5a2030'
    if kind == 'grin':  # sideways, the near corner up, a gap in the teeth
        return '\n'.join([
            f'<path d="M196,340 C214,350 252,346 280,326 C278,346 262,366 238,370 C218,372 202,360 196,340Z" fill="#4a1a24"/>',
            f'<path d="M200,342 C220,350 252,346 276,330 L272,340 C256,350 230,354 204,350Z" fill="#f4ece4"/>',
            f'<rect x="234" y="344" width="7" height="10" fill="#4a1a24"/>',
            d.tone('M214,362 C224,356 244,356 254,362 C246,370 222,370 214,362Z', '#c45a64', 0.9, 1.5),
            f'<path d="M280,326 C284,322 286,318 286,314" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>'])
    if kind == 'laugh':
        return '\n'.join([
            f'<path d="M192,334 C214,346 256,342 284,320 C286,352 266,384 236,386 C210,386 194,364 192,334Z" fill="#4a1a24"/>',
            f'<path d="M196,337 C220,346 254,342 280,324 L276,334 C258,346 228,350 200,346Z" fill="#f4ece4"/>',
            f'<rect x="232" y="341" width="7" height="9" fill="#4a1a24"/>',
            d.tone('M210,372 C222,362 248,362 260,372 C250,384 220,384 210,372Z', '#c45a64', 0.95, 1.5)])
    if kind == 'o':
        return '\n'.join([
            f'<path d="M216,340 C222,330 240,330 246,342 C250,360 242,376 230,376 C218,376 212,360 216,340Z" fill="#4a1a24"/>',
            d.tone('M220,364 C226,358 238,358 244,366 C238,374 224,374 220,364Z', '#c45a64', 0.9, 1)])
    if kind == 'sad':
        return '\n'.join([
            f'<path d="M206,356 C216,342 244,340 262,352" fill="none" stroke="{line}" stroke-width="2.4" stroke-linecap="round"/>',
            d.tone('M214,358 C226,354 244,354 254,360 C244,366 222,366 214,358Z', '#d27a74', 0.6, 1.5)])
    if kind == 'angry':
        return '\n'.join([
            f'<path d="M204,348 C216,338 248,334 266,344 C262,358 218,362 204,348Z" fill="#4a1a24"/>',
            f'<path d="M206,347 C220,339 248,336 264,344 L262,349 C246,344 222,346 208,352Z" fill="#f4ece4"/>',
            f'<path d="M200,352 C214,334 252,330 270,346" fill="none" stroke="{line}" stroke-width="2.2" stroke-linecap="round"/>'])
    raise ValueError(kind)


def bust(d, out):
    sh = '#2a1e40'
    body = ('M150,700 L160,620 C168,560 196,520 236,504 L266,496 C286,494 308,496 326,504 '
            'C362,520 386,560 394,620 L402,700Z')
    bx = d.tone('M316,500 C350,540 366,610 370,700 L420,700 L420,480Z', sh, 0.55, 8)
    bx += d.tone('M196,560 C210,530 230,514 250,508 C236,526 222,546 214,572Z', mix(SWEATER, '#ffd0a0', 0.5), 0.5, 3)
    out.append(d.form(body, SWEATER, shift=28, soft=8, s=0.55, extra=bx))
    # rolled collar
    col = 'M232,498 C246,486 296,484 314,498 C320,506 314,516 300,518 C280,522 256,522 240,516 C228,512 226,504 232,498Z'
    out.append(d.form(col, mix(SWEATER, '#3a1010', 0.15), shift=8, soft=3, s=0.5))
    # a patch on the shoulder
    out.append(d.form('M182,600 L222,592 L226,630 L188,640Z', '#6a7a4a', shift=5, soft=2))
    st = mix('#6a7a4a', '#f0e0c0', 0.5)
    out.append(f'<path d="M184,604 L222,596 L225,628 L189,637Z" fill="none" stroke="{st}" stroke-width="1.4" stroke-dasharray="4 3"/>')


def figure(d, out, expr='calm'):
    """Full figure: ~3.2 heads; legs apart, one hand stuffed in a pocket, a slingshot in the back pocket."""
    from common import place
    sh = '#2a1e40'
    out.append(d.tone('M160,846 C190,834 300,834 340,846 C300,858 190,858 160,846Z', '#140c22', 0.6, 4))
    # legs, socks, boots
    for x0, x1 in ((206, 200), (272, 282)):
        out.append(d.form(f'M{x0},734 C{x0},760 {x1},790 {x1},812 L{x1+18},812 C{x1+18},790 {x0+20},760 {x0+22},734Z', SKIN, shift=5, soft=2, s=0.5))
        out.append(d.form(f'M{x1-1},782 L{x1+19},782 L{x1+19},816 L{x1-1},816Z', SOCKS, shift=5, soft=2, s=0.5))
        out.append(f'<path d="M{x1},788 L{x1+18},788 M{x1},794 L{x1+18},794" stroke="{mix(SOCKS, "#5a2a2a", 0.35)}" stroke-width="2"/>')
    out.append(d.form('M196,810 L222,810 C226,824 226,836 222,846 L174,846 C168,836 178,824 196,818Z', BOOT, shift=5, soft=2))
    out.append(d.form('M280,810 L304,810 C308,822 314,834 322,846 L278,846 C274,836 276,822 280,816Z', BOOT, shift=5, soft=2))
    # shorts
    shorts = 'M190,676 L312,676 L320,742 L264,746 L252,708 L242,746 L184,742Z'
    out.append(d.form(shorts, SHORTS, shift=12, soft=4, s=0.55, extra=d.tone('M270,680 L314,680 L322,746 L280,746Z', sh, 0.45, 4)))
    # the slingshot sticking out of the back pocket
    out.append(f'<path d="M318,700 L330,664 M330,664 L322,640 M330,664 L344,644" fill="none" stroke="#6a4024" stroke-width="5" stroke-linecap="round"/>')
    out.append(f'<path d="M322,640 C330,650 338,652 344,644" fill="none" stroke="#c8a070" stroke-width="1.6"/>')
    # a baggy sweater
    sw = 'M224,546 C200,552 184,576 182,608 L180,690 C208,702 292,702 318,690 L316,608 C314,578 302,554 278,546Z'
    sx = d.tone('M290,550 C312,580 318,640 318,700 L340,700 L340,540Z', sh, 0.6, 5)
    sx += d.tone('M182,676 C210,686 290,686 318,676 L318,700 L182,700Z', mix(SWEATER, '#3a1010', 0.35), 0.8, 1.5)
    out.append(d.form(sw, SWEATER, shift=18, soft=5, s=0.55, extra=sx))
    for y in (684, 690):
        out.append(f'<path d="M184,{y} C210,{y+8} 290,{y+8} 316,{y}" fill="none" stroke="{mix(SWEATER, "#2a0a0a", 0.4)}" stroke-width="1.2" opacity="0.6"/>')
    out.append(d.form('M190,604 L222,598 L224,628 L194,634Z', '#6a7a4a', shift=4, soft=1.5))
    # the near arm: elbow out, the hand stuffed into the pocket
    arm = 'M286,552 C308,560 322,590 326,620 C330,646 322,668 304,684 L290,674 C302,660 308,642 304,620 C300,596 290,578 276,566Z'
    out.append(d.form(arm, SWEATER, shift=10, soft=3, s=0.6, extra=d.tone('M300,556 C326,590 330,650 310,690 L340,690 L340,550Z', sh, 0.5, 3)))
    out.append(d.form('M286,672 L306,680 L300,694 L282,688Z', mix(SWEATER, '#3a1010', 0.3), shift=3, soft=1.5))
    # far arm swinging, the hand showing
    far = 'M206,556 C188,566 178,600 176,632 C176,652 180,666 186,676 L200,672 C196,656 196,636 198,616 C200,592 208,574 218,564Z'
    out.append(d.form(far, SWEATER, shift=8, soft=3, s=0.5))
    out.append(d.form('M184,672 C192,668 202,670 204,680 C206,692 196,698 188,694 C180,690 178,678 184,672Z', SKIN, shift=4, soft=1.5))
    # neck and the head (tilted, curious)
    out.append(d.form('M232,520 L268,520 L270,552 L230,552Z', SKIN, shift=3, soft=2, extra=d.tone('M226,516 L276,516 L276,552 L226,552Z', mix(SKIN, '#4a1838', 0.58), 0.75, 3)))
    out.append(d.form('M222,540 C236,532 266,532 280,540 C284,548 278,556 268,556 C254,558 238,558 228,554 C220,550 218,544 222,540Z',
                      mix(SWEATER, '#3a1010', 0.15), shift=5, soft=2))
    place(d, out, head34, 'tim', (238, 548), 0.47, rot=8, expr=expr)
