"""Face parts in the Klaus manner: eyes with heavy lids and a wrapping lash line, brows set far, small mouths."""
from kit import mix

INK = '#2a1a1c'


def eye(d, cx, cy, rx, ry, lid=0.42, look=(-0.25, 0.05), tilt=0, skin='#e9b49a', iris='#4a3028',
        crease=0.35, wing=1.0, lower=0.5, low_lid=0.0, white='#f3ebe3', lash=2.6, shut=False, irr=0.86):
    """cx,cy centre; rx,ry radii; lid: how much the upper lid covers (0..1); look: pupil offset in radii;
    tilt: outer corner raised (+) in px; wing: lash wing past the outer corner (sign = which side is outer);
    low_lid: lower lid pushing up (smile / squint); shut: closed eye (a curved lash line only)."""
    L = d.light
    lit, sh, _ = L.colours(skin)
    s = []
    o = 1 if wing >= 0 else -1  # outer side
    w = abs(wing)
    xo, xi = cx + o * rx, cx - o * rx  # outer, inner corner x
    yo, yi = cy - tilt * 0.5, cy + tilt * 0.5
    if shut:
        yy = cy + ry * 0.35
        s.append(f'<path d="M{xi},{yi} C{cx - o*rx*0.4},{yy+ry*0.5} {cx + o*rx*0.5},{yy+ry*0.45} {xo},{yo} '
                 f'L{xo + o*6*w},{yo-3} C{cx + o*rx*0.5},{yy+ry*0.2} {cx - o*rx*0.4},{yy+ry*0.15} {xi},{yi-1.5}Z" fill="{INK}"/>')
        s.append(f'<path d="M{xi+o*1},{yi-ry*0.5} C{cx - o*rx*0.3},{cy-ry*0.9} {cx + o*rx*0.5},{cy-ry*0.9} {xo+o*2},{yo-ry*0.3}" '
                 f'fill="none" stroke="{mix(skin, INK, 0.35)}" stroke-width="1.3" stroke-linecap="round"/>')
        return '\n'.join(s)
    eyed = (f'M{xi},{yi} C{xi},{cy - ry*1.05} {xo},{cy - ry*1.15} {xo},{yo} '
            f'C{xo},{cy + ry*1.1} {xi},{cy + ry*1.05} {xi},{yi}Z')
    c = d.clip(eyed)
    ir = ry * irr
    ix, iy = cx + look[0] * rx, cy + look[1] * ry
    ly = cy - ry + lid * 2 * ry  # lid edge at centre
    lidd = (f'M{xi - o*4},{cy - ry - 10} L{xo + o*4},{cy - ry - 10} L{xo + o*4},{yo} '
            f'C{cx + o*rx*0.5},{ly + (yo-cy)*0.4} {cx - o*rx*0.5},{ly + (yi-cy)*0.4} {xi - o*4},{yi}Z')
    lowd = (f'M{xi - o*4},{cy + ry + 10} L{xo + o*4},{cy + ry + 10} L{xo + o*4},{yo} '
            f'C{cx + o*rx*0.5},{cy + ry*(1 - 1.6*low_lid)} {cx - o*rx*0.5},{cy + ry*(1 - 1.6*low_lid)} {xi - o*4},{yi}Z')
    s += [f'<g clip-path="url(#{c})">',
          f'<path d="{eyed}" fill="{white}"/>',
          d.tone(f'M{cx - rx},{cy + ry*0.1} C{cx},{cy + ry*1.2} {cx + rx},{cy + ry*0.3} {cx + rx},{cy + ry*1.1} '
                 f'L{cx + rx},{cy + ry + 4} L{cx - rx},{cy + ry + 4}Z', '#a898b0', 0.5, 2),
          f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="{ir:.1f}" fill="{iris}"/>',
          d.tone(f'M{ix - ir},{iy} a{ir},{ir} 0 0,0 {2*ir},0 a{ir*1.2},{ir*0.6} 0 0,1 {-2*ir},0Z',
                 mix(iris, '#ffe0b0', 0.35), 0.6, 1.5),
          f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="{ir*0.5:.1f}" fill="#120a0a"/>',
          d.tone(lidd, '#2a1830', 0.6, 2.4),
          f'<path d="{lidd}" fill="{mix(skin, L.key, 0.04)}"/>',
          f'<path d="{lowd}" fill="{mix(skin, L.key, 0.04)}"/>' if low_lid else '',
          f'<circle cx="{ix - ir*0.38:.1f}" cy="{max(iy - ir*0.25, ly + ir*0.32):.1f}" r="{max(ir*0.2, 1.4):.1f}" fill="#fff"/>',
          '</g>']
    # lash line: thick on the upper lid, wraps past the outer corner as a wing
    s.append(f'<path d="M{xi - o*1.5},{yi + 1} C{cx - o*rx*0.5},{ly + (yi-cy)*0.4 - 1} {cx + o*rx*0.5},{ly + (yo-cy)*0.4 - 1} '
             f'{xo + o*1},{yo} L{xo + o*(3 + 6*w)},{yo - 2 - 4*w} '
             f'C{cx + o*rx*0.5},{ly + (yo-cy)*0.4 - 1 - lash} {cx - o*rx*0.5},{ly + (yi-cy)*0.4 - 1 - lash} {xi - o*1.5},{yi - 1.5}Z" '
             f'fill="{INK}"/>')
    if low_lid:
        yl = cy + ry * (1 - 1.6 * low_lid)
        s.append(f'<path d="M{xi},{yi} C{cx - o*rx*0.5},{yl} {cx + o*rx*0.5},{yl} {xo},{yo}" fill="none" '
                 f'stroke="{mix(skin, INK, 0.5)}" stroke-width="1.6" stroke-linecap="round"/>')
    elif lower:
        s.append(f'<path d="M{cx - o*rx*0.5},{cy + ry*0.98} C{cx},{cy + ry*1.1} {cx + o*rx*0.6},{cy + ry*0.95} {xo},{yo + ry*0.3}" '
                 f'fill="none" stroke="{mix(skin, INK, 0.45)}" stroke-width="1.3" stroke-linecap="round" opacity="{lower}"/>')
    if crease:
        s.append(f'<path d="M{xi + o*rx*0.1},{cy - ry - 2} C{cx - o*rx*0.3},{cy - ry*1.5 - 2} {cx + o*rx*0.6},{cy - ry*1.45 - 2} {xo + o*rx*0.1},{yo - ry*0.55}" '
                 f'fill="none" stroke="{mix(skin, INK, 0.4)}" stroke-width="1.4" stroke-linecap="round" opacity="{crease*2.2}"/>')
    return '\n'.join(s)


def brow(p0, p1, p2, width=4.0, col='#5a3020'):
    """A tapered brow: thick at the inner end p0, curve through p1, thin at p2."""
    (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2
    return (f'<path d="M{x0},{y0 - width/2} Q{x1},{y1 - width*0.6} {x2},{y2} Q{x1},{y1 + width*0.6} {x0},{y0 + width/2}Z" '
            f'fill="{col}" stroke="{col}" stroke-width="1" stroke-linejoin="round"/>')
