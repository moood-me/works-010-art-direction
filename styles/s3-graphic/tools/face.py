"""Shared face parts in the graphic style: eye, brow, simple mouths."""
from lib import F, L, clip, LW

K = 4 / 3


def oval(cx, cy, rx, ry, top=1.0, bot=1.0, tilt=0.0):
    """An eye-like oval built of two cubics; top/bot flatten or round the halves; tilt raises the outer (right) end."""
    x0, x1 = cx - rx, cx + rx
    y0, y1 = cy + tilt, cy - tilt
    return (f'M {x0} {y0} C {x0} {cy - K * ry * top + tilt * .5}, {x1} {cy - K * ry * top - tilt * .5}, {x1} {y1} '
            f'C {x1} {cy + K * ry * bot - tilt * .5}, {x0} {cy + K * ry * bot + tilt * .5}, {x0} {y0} Z')


def eye(cx, cy, rx, ry, c, look=(0, 0), lid=0.0, lidtilt=0.0, lower=0.0, ir=None, sq=1.0, flick=1,
        tilt=0.0, top=1.0, bot=1.0, lash=2.4, lowline=True, hl=True):
    """c: dict with skin, line, white, iris, pupil, lash.
    lid: 0 open … 1 shut (from the top); lower: 0 … 1 lower lid pushed up (smile)."""
    ir = ir or ry * 0.62
    d = oval(cx, cy, rx, ry, top, bot, tilt)
    ix, iy = cx + look[0], cy + look[1]
    inner = [F(d, c['white'])]
    inner.append(f'<ellipse cx="{ix}" cy="{iy}" rx="{ir * sq}" ry="{ir}" fill="{c["iris"]}"/>')
    inner.append(f'<ellipse cx="{ix}" cy="{iy}" rx="{ir * .55 * sq}" ry="{ir * .55}" fill="{c["pupil"]}"/>')
    if hl:
        inner.append(f'<ellipse cx="{ix - ir * .35 * sq}" cy="{iy - ir * .4}" rx="{ir * .28 * sq}" ry="{ir * .28}" fill="#fff"/>')
        inner.append(f'<circle cx="{ix + ir * .35 * sq}" cy="{iy + ir * .38}" r="{ir * .12}" fill="#fff" opacity=".85"/>')
    # shadow of the upper lid on the eyeball
    h = cy - ry + 2 * ry * lid
    e = ry * 0.15 * lid
    ya, yb = cy + e + lidtilt, cy + e - lidtilt
    yc = (4 * h - (ya + yb) / 2) / 3
    edge = f'M {cx - rx - 3} {ya} C {cx - rx} {yc}, {cx + rx} {yc}, {cx + rx + 3} {yb}'
    inner.append(F(edge + f' L {cx + rx + 3} {yb + 7} C {cx + rx} {yc + 7}, {cx - rx} {yc + 7}, {cx - rx - 3} {ya + 7} Z',
                   c['line'], extra='opacity=".18"'))
    lidfill = edge + f' L {cx + rx + 6} {cy - ry - 30} L {cx - rx - 6} {cy - ry - 30} Z'
    inner.append(F(lidfill, c['skin']))
    if lower > 0:
        yl = cy + K * ry * (1 - 2.2 * lower)
        low = (f'M {cx - rx - 3} {cy + ry * .1} C {cx - rx * .7} {yl}, {cx + rx * .7} {yl}, {cx + rx + 3} {cy + ry * .1} '
               f'L {cx + rx + 6} {cy + ry + 30} L {cx - rx - 6} {cy + ry + 30} Z')
        inner.append(F(low, c['skin']))
    out = [clip(d, *inner)]
    # lid line, thick, with a flick at the outer corner
    if flick > 0:
        fx, fy = cx + rx + 3, yb
        fl = f' C {fx + 4} {fy - 1}, {fx + 8} {fy - 4}, {fx + 10} {fy - 9}'
    elif flick < 0:
        fx, fy = cx - rx - 3, ya
        fl = ''
    else:
        fl = ''
    if flick < 0:
        lidline = (f'M {cx - rx - 13} {ya - 9} C {cx - rx - 11} {ya - 4}, {cx - rx - 7} {ya - 1}, {cx - rx - 3} {ya} '
                   f'C {cx - rx} {yc}, {cx + rx} {yc}, {cx + rx + 3} {yb}')
    else:
        lidline = edge + fl
    out.append(L(lidline, c['lash'], LW[0] * lash))
    if lower > 0:
        yl = cy + K * ry * (1 - 2.2 * lower)
        out.append(L(f'M {cx - rx * .8} {cy + ry * .55 - lower * ry * .5} C {cx - rx * .5} {yl + 2}, '
                     f'{cx + rx * .5} {yl + 2}, {cx + rx * .8} {cy + ry * .55 - lower * ry * .5}', c['line'], LW[0] * .8))
    elif lowline:
        out.append(L(f'M {cx - rx * .55} {cy + ry * 1.0} C {cx - rx * .2} {cy + ry * 1.12}, {cx + rx * .3} {cy + ry * 1.1}, '
                     f'{cx + rx * .65} {cy + ry * .95}', c['line'], LW[0] * .7, 'opacity=".55"'))
    return ''.join(out)


def closed_eye(cx, cy, rx, c, up=True, w=2.4):
    """A shut eye: a happy arc (up) or a sad/sleeping arc (down)."""
    k = -1 if up else 1
    return L(f'M {cx - rx} {cy} C {cx - rx * .5} {cy + k * rx * .8}, {cx + rx * .5} {cy + k * rx * .8}, {cx + rx} {cy}',
             c['lash'], LW[0] * w)


def brow(x0, y0, x1, y1, bend, thick, col, taper_end=1):
    """A tapered brow: thick at the inner end (x0,y0), thin at the outer end; bend lifts the middle."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - bend
    t = thick
    return F(f'M {x0} {y0 + t * .5} Q {mx} {my + t * .4} {x1} {y1} Q {mx} {my - t * .6} {x0} {y0 - t * .5} Z', col,
             col, LW[0] * .6)
