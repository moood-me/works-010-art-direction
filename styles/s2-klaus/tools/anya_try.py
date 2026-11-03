import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = '/home/user/cache/styles-s2-klaus/try'
os.makedirs(OUT, exist_ok=True)

SKIN = '#e9b49a'
HAIR = '#8a4a2a'
INK = '#2a1a1c'


def eye(d, cx, cy, rx, ry, lid=0.42, look=(-0.25, 0.05), tilt=0, skin=SKIN, iris='#5a3a2a', crease=True,
        wing=1.0, lower=0.5):
    """Klaus eye: round white, big dark iris, a heavy upper lid with a thick lash line wrapping the eye."""
    c = d.clip(f'M{cx-rx},{cy} a{rx},{ry} 0 1,0 {2*rx},0 a{rx},{ry} 0 1,0 {-2*rx},0Z')
    ir = ry * 0.86
    ix, iy = cx + look[0] * rx, cy + look[1] * ry
    ly = cy - ry + lid * 2 * ry  # lid edge height at centre
    lidd = (f'M{cx-rx-4},{cy-ry-8} L{cx+rx+4},{cy-ry-8} L{cx+rx+4},{cy+tilt*0.3} '
            f'C{cx+rx*0.5},{ly-2+tilt*0.5} {cx-rx*0.5},{ly-2-tilt*0.5} {cx-rx-4},{cy-tilt*0.3}Z')
    lit, sh, _ = d.light.colours(skin)
    s = [f'<g clip-path="url(#{c})">',
         f'<rect x="{cx-rx-2}" y="{cy-ry-2}" width="{2*rx+4}" height="{2*ry+4}" fill="#f4ece4"/>',
         d.tone(f'M{cx-rx},{cy+ry*0.2} C{cx},{cy+ry*1.3} {cx+rx},{cy+ry*0.4} {cx+rx},{cy+ry*1.2} L{cx+rx},{cy+ry+2} L{cx-rx},{cy+ry+2}Z',
                '#b7a6b8', 0.6, 2),
         f'<circle cx="{ix}" cy="{iy}" r="{ir}" fill="{iris}"/>',
         f'<circle cx="{ix}" cy="{iy}" r="{ir*0.55}" fill="#140c0c"/>',
         # shadow of the lid on the eyeball
         d.tone(lidd, '#3a2440', 0.55, 2.2) if True else '',
         f'<path d="{lidd}" fill="{mix(skin, d.light.key, 0.05)}"/>',
         d.tone(f'M{cx-rx},{ly-6} L{cx+rx},{ly-6} L{cx+rx},{cy-ry} L{cx-rx},{cy-ry}Z', sh, 0.35, 2),
         f'<circle cx="{ix-ir*0.35}" cy="{max(iy-ir*0.2, ly+ir*0.25)}" r="{ir*0.22}" fill="#fff"/>',
         '</g>']
    # lash line: thick, along the lid edge, wrapping past the outer corner (wing)
    ox = cx + rx * (1 if wing > 0 else -1)
    s.append(f'<path d="M{cx-rx-1.5},{cy-tilt*0.3+1} C{cx-rx*0.5},{ly-2-tilt*0.5} {cx+rx*0.5},{ly-2+tilt*0.5} '
             f'{cx+rx+1},{cy+tilt*0.3} L{ox+6*wing},{cy+tilt*0.3-5} '
             f'C{cx+rx*0.5},{ly-6+tilt*0.5} {cx-rx*0.5},{ly-6-tilt*0.5} {cx-rx-1.5},{cy-tilt*0.3-2}Z" fill="{INK}"/>')
    if lower:
        s.append(f'<path d="M{cx-rx*0.6},{cy+ry*0.92} C{cx},{cy+ry*1.08} {cx+rx*0.6},{cy+ry*0.95} {cx+rx},{cy+ry*0.3}" '
                 f'fill="none" stroke="{mix(skin, INK, 0.45)}" stroke-width="1.3" stroke-linecap="round" opacity="{lower}"/>')
    if crease:
        s.append(f'<path d="M{cx-rx*0.7},{cy-ry-3} C{cx-rx*0.2},{cy-ry*1.55-2} {cx+rx*0.6},{cy-ry*1.5-2} {cx+rx*1.05},{cy-ry*0.7}" '
                 f'fill="none" stroke="{mix(skin, INK, 0.35)}" stroke-width="1.4" stroke-linecap="round"/>')
    return '\n'.join(s)


def anya_head(d, out):
    L = d.light
    # back hair mass
    back = ('M196,128 C240,70 360,70 384,170 C398,236 380,320 396,410 C402,440 412,458 424,470 '
            'C380,478 340,456 322,420 C306,388 304,330 300,290 Z')
    out.append(d.form(back, HAIR, shift=26, rim=3, soft=8, k=0.10, s=0.55, out=[]))
    # neck
    neck = 'M236,330 C240,360 238,400 230,440 L312,446 C302,400 300,350 304,300 Z'
    neckx = d.tone('M230,320 C260,360 290,350 310,300 L312,446 L230,446 Z', L.shade, 0.45, 4)
    out.append(d.form(neck, SKIN, shift=14, rim=2.5, soft=4, extra=neckx, out=[]))
    # face
    face = ('M206,146 C186,168 178,200 182,222 C184,232 186,238 184,247 C180,264 182,286 190,305 '
            'C198,326 212,346 228,357 C234,361 242,361 248,356 C276,336 300,312 312,286 '
            'C322,262 322,202 310,166 C290,140 240,134 206,146 Z')
    fx = []
    # eye sockets: soft warm-dark under the brow, cast shadow on the far side of the face
    fx.append(d.tone('M188,214 C205,206 228,210 236,226 C232,242 210,246 194,240 Z', '#a0605c', 0.25, 5))
    fx.append(d.tone('M240,224 C255,210 285,212 300,226 C296,246 262,252 244,242 Z', '#a0605c', 0.22, 5))
    # cheek blush
    fx.append(d.tone('M250,272 C262,262 290,266 296,282 C292,298 262,300 250,290 Z', '#e0706a', 0.35, 7))
    fx.append(d.tone('M188,276 C196,270 206,272 208,284 C204,294 192,292 188,286 Z', '#e0706a', 0.30, 5))
    # nose cast shadow on the cheek, to lower right
    fx.append(d.tone('M218,250 C228,270 236,292 232,304 C224,306 214,302 210,296 Z', '#7a3f4e', 0.30, 3))
    # shadow under the chin region / jaw turning away
    fx.append(d.tone('M246,356 C276,334 300,312 312,286 L330,300 L330,380 L240,380Z', L.shade, 0.4, 5))
    # hair's cast shadow on the forehead
    fx.append(d.tone('M180,150 C210,170 240,190 270,180 C290,176 306,190 320,200 L320,120 L180,120Z', '#5a2c3a', 0.55, 6))
    out.append(d.form(face, SKIN, shift=16, rim=2.4, soft=6, extra='\n'.join(fx), out=[]))
    # ear peeking under hair (far side)
    # nose
    nose = 'M224,226 C218,252 204,274 190,290 C186,296 190,302 198,301 C206,300 212,304 222,300 C228,296 230,290 226,282 Z'
    nx = d.tone('M196,300 C206,298 214,302 224,298 L226,310 L190,310Z', '#7a3f4e', 0.5, 1.5)
    nx += d.tone('M200,284 C206,282 214,286 214,290', '#000', 0)
    out.append(d.form(nose, mix(SKIN, '#e88a7a', 0.25), shift=6, rim=1.6, soft=2.5, extra=nx, out=[]))
    out.append(f'<path d="M206,293 C210,290 215,292 216,296" fill="none" stroke="{mix(SKIN, INK, 0.5)}" stroke-width="1.6" stroke-linecap="round"/>')
    # brows (far from the eyes)
    out.append(f'<path d="M236,210 C254,198 280,200 298,212 C280,205 256,205 238,213Z" fill="{mix(HAIR, INK, 0.3)}" stroke="{mix(HAIR, INK, 0.3)}" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<path d="M190,212 C198,204 210,203 220,206 C210,206 200,208 191,214Z" fill="{mix(HAIR, INK, 0.3)}" stroke="{mix(HAIR, INK, 0.3)}" stroke-width="2" stroke-linejoin="round"/>')
    # eyes
    out.append(eye(d, 266, 238, 15, 13, lid=0.45, look=(-0.3, 0.1)))
    out.append(eye(d, 206, 238, 9, 12.5, lid=0.45, look=(-0.35, 0.1), wing=0.6, crease=False))
    # mouth: small, close under the nose, a gentle smile
    out.append(d.tone('M210,322 C220,318 232,318 244,316 C236,324 222,328 210,322Z', '#9a4a50', 1))
    out.append(f'<path d="M206,320 C218,326 234,324 246,314" fill="none" stroke="#5a2430" stroke-width="2" stroke-linecap="round"/>')
    out.append(d.tone('M214,327 C224,333 236,331 242,326 C238,336 222,338 214,327Z', '#c86a6a', 0.7, 1.5))
    out.append(d.tone('M218,340 C226,344 234,342 238,338', '#000', 0))
    # front hair: big swoop from the parting across the forehead, falling past the cheek
    front = ('M300,96 C250,88 196,110 178,160 C166,196 168,240 160,282 C156,300 150,316 140,326 '
             'C160,322 176,300 184,272 C190,240 192,210 206,180 C224,148 262,132 300,132 '
             'C330,134 350,150 362,176 C366,140 340,100 300,96 Z')
    hx = d.tone('M300,104 C262,104 222,124 204,160 C230,138 262,126 300,124Z', mix(HAIR, '#ffd9a0', 0.45), 0.8, 3)
    out.append(d.form(front, HAIR, shift=12, rim=3, soft=5, k=0.12, s=0.5, extra=hx, out=[]))


def anya_body_bust(d, out):
    L = d.light
    sweater = '#c9a24a'
    body = ('M150,600 C150,520 170,470 220,440 C240,432 260,432 270,440 C290,432 312,432 330,440 '
            'C380,462 410,520 420,600 Z')
    bx = d.tone('M270,440 C300,470 320,500 330,600 L430,600 L430,430 Z', L.shade, 0.45, 8)
    out.append(d.form(body, sweater, shift=24, rim=3, soft=10, extra=bx, out=[]))
    # collar of a blouse
    col = 'M232,438 C250,452 262,470 270,486 C282,468 296,452 316,440 C300,436 284,438 270,446 C256,436 244,434 232,438Z'
    out.append(d.form(col, '#efe4d4', shift=8, rim=2, soft=3, out=[]))


def main():
    d = Doc(500, 600, Light(-0.8, -0.6, key='#ffd8a8', shade='#43305e'))
    bg(d, '#3d3552', '#6a4a5a', glow='#f2b77a', gx=0.25, gy=0.25, gr=0.7)
    out = []
    anya_body_bust(d, out)
    anya_head(d, out)
    for s in out:
        d.add(s)
    d.grain(0.10)
    p = f'{OUT}/anya_try.svg'
    d.save(p)
    render(p, p.replace('.svg', '.png'), 500, 600)


main()
