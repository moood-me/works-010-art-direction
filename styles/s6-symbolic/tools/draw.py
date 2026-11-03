"""Drawing: a figure as one ink shape + rim light + accents, inside small scenes. Writes SVG; render.sh makes PNG."""
import math
import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
from sil import Fig, d_of
from cast import CAST

_uid = [0]


def uid(p='i'):
    _uid[0] += 1
    return '%s%d' % (p, _uid[0])


def figure_svg(name, yaw=0, pose=None, k=1.0, x=0, y=0, ink='#11141c', rim='#c9d3e6', rim_w=1.6, light=1,
               plane=None, glow=True, opts=None, accents=True):
    """One character, its feet at (x, y), scale k px per cm. light: +1 rim on the right edge, -1 on the left.
    plane: (colour, offset px) — a broad, low-contrast lit plane on the light side (KRZ-like two tones)."""
    J, f, acc = CAST[name](pose=pose, yaw=yaw, **(opts or {}))
    g = f.shape(yaw)
    d = d_of(g, k, x, y)
    out = []
    back, front = [], []
    for a in (acc if accents else []):
        s = accent_svg(a, f, J, yaw, k, x, y, glow)
        if s is None:
            continue
        lay, svg = s
        (front if lay > 0 else back).append(svg)
    out += back
    out.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, ink))
    def crescent(col, off, op=1.0):
        mid = uid('m')
        return ('<mask id="%s" maskUnits="userSpaceOnUse"><path d="%s" fill="#fff" fill-rule="evenodd"/>'
                '<path d="%s" fill="#000" fill-rule="evenodd" transform="translate(%.2f %.2f)"/></mask>'
                '<path d="%s" fill="%s" opacity="%.2f" fill-rule="evenodd" mask="url(#%s)"/>') % (
            mid, d, d, -light * off, off * .3, d, col, op, mid)
    if plane:
        out.append(crescent(plane[0], plane[1]))
    if rim:
        out.append(crescent(rim, rim_w))
    out += front
    bounds = [b * k for b in g.bounds]
    return '\n'.join(out), (bounds[0] + x, bounds[1] + y, bounds[2] + x, bounds[3] + y), (J, f)


def P2(f, P, yaw, k, x, y):
    p, z = Fig.proj(np.asarray(P, float)[None], yaw)
    return p[0][0] * k + x, p[0][1] * k + y, z[0]


def glow_svg(cx, cy, r, col, op=1.0):
    gid = uid('g')
    return ('<defs><radialGradient id="%s"><stop offset="0" stop-color="%s" stop-opacity="%.2f"/>'
            '<stop offset=".25" stop-color="%s" stop-opacity="%.2f"/><stop offset="1" stop-color="%s" stop-opacity="0"/>'
            '</radialGradient></defs><circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#%s)"/>') % (
        gid, col, .55 * op, col, .22 * op, col, cx, cy, r, gid)


def accent_svg(a, f, J, yaw, k, x, y, glow):
    body_z = f.depth((J['pel'] + J['neck']) / 2, yaw)
    if a['kind'] == 'lantern':
        cx, cy, z = P2(f, a['p'], yaw, k, x, y)
        hx, hy, _ = P2(f, a['top'], yaw, k, x, y)
        s = a['size'] * k
        lay = 1 if z > body_z - 2 else -1
        svg = ''
        if glow:
            svg += glow_svg(cx, cy, s * 7, a['col'], 1.0)
        svg += '<path d="M%.1f %.1f L%.1f %.1f" stroke="#11141c" stroke-width="%.1f"/>' % (hx, hy, cx, cy - s * .55, max(k * .5, .6))
        svg += ('<path d="M%.1f %.1f q%.1f %.1f 0 %.1f q%.1f %.1f %.1f 0 q%.1f %.1f 0 %.1f Z" fill="%s"/>') % (
            cx - s * .42, cy - s * .5, -s * .14, s * .5, s * 1.0, s * .42, s * .14, s * .84, s * .14, -s * .5, -s * 1.0, a['col'])
        svg += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#11141c"/>' % (cx - s * .3, cy - s * .62, s * .6, s * .14)
        return lay, svg
    if a['kind'] == 'glint':
        cx, cy, z = P2(f, a['p'], yaw, k, x, y)
        if z < f.depth(J['ntop'], yaw) - 2:
            return None
        r = a['r'] * k
        return 1, (glow_svg(cx, cy, r * 6, a['col'], .8) if glow else '') + '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r * .55, a['col'])
    if a['kind'] == 'watch':
        cx, cy, z = P2(f, a['p'], yaw, k, x, y)
        lay = 1 if z > body_z else -1
        r = a['r'] * k
        svg = (glow_svg(cx, cy, r * 9, a['col'], .9) if glow else '')
        svg += '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r * .75, a['col'])
        return lay, svg
    if a['kind'] == 'chain':
        ax, ay, za = P2(f, a['a'], yaw, k, x, y)
        bx, by, zb = P2(f, a['b'], yaw, k, x, y)
        if za < body_z:
            return None
        mx, my = (ax + bx) / 2, max(ay, by) + 3 * k
        return 1, '<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="%.2f" stroke-dasharray="%.1f %.1f" opacity=".85"/>' % (
            ax, ay, mx, my, bx, by, a['col'], max(.35 * k, .5), .6 * k, .5 * k)
    if a['kind'] == 'lens':
        cx, cy, z = P2(f, a['p'], yaw, k, x, y)
        if z < f.depth(J['ntop'], yaw) + 1:
            return None
        # a lens seen at an angle is a thin ellipse; facing us, a small disc
        c = abs(math.cos(math.radians(yaw)))
        if c > .8:
            # facing us, lenses would read as eyes: show only the thin bright edge of the frames
            return 1, '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s" opacity=".55"/>' % (
                cx - a['r'] * k, cy - .22 * k, a['r'] * 2 * k, .44 * k, .2 * k, a['col'])
        rx_, ry_ = a['r'] * k * max(c, .25), a['r'] * k * .5
        return 1, '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity=".85"/>' % (cx, cy, rx_, ry_, a['col'])
    if a['kind'] == 'tube':
        p2, z = Fig.proj(np.asarray(a['pts'], float), yaw)
        if a.get('ring'):
            # a scarf knot round the neck: a flat band, always over the body
            c = p2[0] * k + [x, y]
            r = a['r'][0] * k
            return 1, '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>' % (c[0], c[1], r, r * .55, a['col'])
        g = Fig.tube2d(np.asarray(a['pts']), a['r'], yaw)
        zr = f.depth(a['ref'], yaw)
        return (1 if zr > body_z else -1), '<path d="%s" fill="%s"/>' % (d_of(g, k, x, y), a['col'])
    return None


def svg_doc(w, h, body, bg='#1a1f2c', defs=''):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
            '<defs>%s</defs>%s</svg>') % (w, h, w, h, defs, ('<rect width="%d" height="%d" fill="%s"/>' % (w, h, bg) if bg else '') + body)


GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" '
         'numOctaves="2" seed="4" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/>'
         '<feComponentTransfer><feFuncA type="table" tableValues="0 .14"/></feComponentTransfer></filter>')


def finish(w, h, vign=.55):
    """Grain over everything and a vignette that pulls the eye to the centre."""
    return ('<defs><radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/>'
            '<stop offset="1" stop-color="#000" stop-opacity="%.2f"/></radialGradient>%s</defs>'
            '<rect width="%d" height="%d" fill="url(#vig)"/><rect width="%d" height="%d" filter="url(#grain)"/>') % (
        vign, GRAIN, w, h, w, h)
