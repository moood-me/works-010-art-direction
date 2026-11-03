"""Faces of a few graphic signs: eyes (cream oval, one dark iris, a highlight, a lid that cuts it),
brows, a mouth, blush. Positions come from the head volume, so they turn with the head."""
import math
from geo import *

SCLERA = '#fff8ec'

# expressions: lids are (inner, outer) as a fraction of the eye height cut from the top
EXPR = {
    'neutral':  dict(lid=(.12, .12), look=(0, 0), brow=(0, 0), mouth='soft', shut=False),
    'joy':      dict(lid=(0, 0), look=(0, 0), brow=(-4, 3), mouth='open', shut='happy'),
    'surprise': dict(lid=(0, 0), look=(0, -1), brow=(-12, 0), mouth='o', shut=False, big=1.15, iris=.72),
    'sad':      dict(lid=(.1, .45), look=(0, 2), brow=(-3, -9), mouth='frown', shut=False, tear=True),
    'anger':    dict(lid=(.48, .1), look=(0, 0), brow=(4, 9), mouth='clench', shut=False),
}


def eye(v, x, y, fc, rx, ry, side, ex, P, sw):
    """side = -1 for the eye on the -X side, +1 for +X; inner corner is toward the nose."""
    if fc < .12:
        return ''
    sq = max(fc, .25) ** .85
    big = ex.get('big', 1)
    rx, ry = rx * sq * big, ry * big
    out = ''
    shut = ex.get('shut')
    # inner corner sits toward the face centre; in projection that's toward smaller |phi|
    inner = -side
    if shut == 'happy':
        d = f'M{f(x - rx)},{f(y + ry * .25)} Q{f(x)},{f(y - ry * 1.05)} {f(x + rx)},{f(y + ry * .25)}'
        return stroke(d, sw * 1.35)
    if shut == 'closed':
        d = f'M{f(x - rx)},{f(y)} Q{f(x)},{f(y + ry * .55)} {f(x + rx)},{f(y)}'
        return stroke(d, sw * 1.2)
    li, lo = ex['lid']
    li += P.get('lid_add', (0, 0))[0]
    lo += P.get('lid_add', (0, 0))[1]
    top = y - ry
    xi, xo = x + inner * rx * 1.25, x - inner * rx * 1.25
    yi, yo = top + li * 2 * ry, top + lo * 2 * ry
    cid = uid('e')
    clip = f'<clipPath id="{cid}"><path d="{poly_d([(xi, yi), (xo, yo), (xo, y + ry * 3), (xi, y + ry * 3)], True)}"/></clipPath>'
    ed = ellipse_d(x, y, rx, ry)
    iris_r = min(rx, ry) * ex.get('iris', P.get('iris', .78))
    lx, ly = ex['look']
    lx += P.get('look', (0, 0))[0]
    ly += P.get('look', (0, 0))[1]
    ix, iy = x + lx * sq + (1 - sq) * rx * .6 * (1 if v.s >= 0 else -1), y + ly + ry * .12
    eid = uid('s')
    out += clip + f'<clipPath id="{eid}"><path d="{ed}"/></clipPath>'
    out += f'<g clip-path="url(#{cid})">'
    if P.get('sclera', True):
        out += f'<path d="{ed}" fill="{SCLERA}"/>'
        out += f'<g clip-path="url(#{eid})"><path d="{ellipse_d(ix, iy, iris_r * sq ** .3, iris_r)}" fill="{P["iris_col"]}"/>'
        out += f'<path d="{ellipse_d(ix, iy + iris_r * .1, iris_r * .55 * sq ** .3, iris_r * .58)}" fill="{LINE}"/></g>'
    else:
        out += f'<path d="{ed}" fill="{P["iris_col"]}"/>'
    hr = max(rx, ry) * .2
    out += f'<circle cx="{f(ix - iris_r * .35)}" cy="{f(iy - iris_r * .38)}" r="{f(hr)}" fill="#fff"/>'
    out += f'<circle cx="{f(ix + iris_r * .3)}" cy="{f(iy + iris_r * .32)}" r="{f(hr * .45)}" fill="#fff" opacity=".85"/>'
    out += stroke(ed, sw * .9)
    out += '</g>'
    # the lid line: heavier, a little longer than the eye, with an outer flick for lashes
    lw = sw * P.get('lash', 1.4)
    # lid follows the eye top when open: draw the visible top edge
    if max(li, lo) < .06:
        d = f'M{f(x - rx * 1.08)},{f(y - ry * .15)} Q{f(x - rx * .7)},{f(y - ry * 1.08)} {f(x)},{f(y - ry * 1.04)} Q{f(x + rx * .75)},{f(y - ry * 1.04)} {f(x + rx * 1.08)},{f(y - ry * .2)}'
    else:
        # straight-ish lid with a slight arch
        mx, my = (xi + xo) / 2, (yi + yo) / 2 - ry * .08
        # clamp the lid endpoints to the eye edge
        d = f'M{f(x - rx * 1.1)},{f(yi if inner < 0 else yo)} Q{f(mx)},{f(my)} {f(x + rx * 1.1)},{f(yo if inner < 0 else yi)}'
    out += stroke(d, lw)
    if P.get('flick'):
        ox = x - inner * rx * 1.05
        oy = (yo if True else yi) + (ry * .1 if max(li, lo) >= .06 else ry * -.1)
        out += stroke(f'M{f(ox)},{f(oy)} l{f(-inner * rx * .38)},{f(-ry * .28)}', sw * 1.1)
    if P.get('bags'):
        out += stroke(f'M{f(x - rx * .7)},{f(y + ry * 1.25)} Q{f(x)},{f(y + ry * 1.55)} {f(x + rx * .7)},{f(y + ry * 1.25)}', sw * .6, extra='opacity=".55"')
    if ex.get('tear') and side == -1:
        tx, ty = x + rx * .3, y + ry * 1.3
        out += shape(f'M{f(tx)},{f(ty)} q{f(-5)},{f(9)} 0,{f(12)} q5,-3 0,-12 Z', '#9fd3ea', shade=False, sw=sw * .6)
    return out


def brow(v, x, y, fc, w, side, ex, P, sw):
    if fc < .12:
        return ''
    sq = max(fc, .25) ** .85
    inner = -side
    dy_all, tilt = ex['brow']
    w = w * sq
    yi = y + dy_all + tilt * .5
    yo = y + dy_all - tilt * .5
    xi, xo = x + inner * w * .5, x - inner * w * .5
    kind = P.get('brow_kind', 'line')
    if kind == 'bush':
        # a soft cloud of white brow
        pts = [(xi, yi - 2), ((xi + xo) / 2, min(yi, yo) - 7), (xo + (-inner) * 6, yo - 1), (xo, yo + 6), ((xi + xo) / 2, (yi + yo) / 2 + 5), (xi, yi + 5)]
        return shape(smooth(pts), P['brow_col'], size=w, sw=sw * .8)
    th = P.get('brow_w', 1.6)
    d = f'M{f(xi)},{f(yi)} Q{f((xi + xo) / 2)},{f(min(yi, yo) - P.get("brow_arch", 3))} {f(xo)},{f(yo)}'
    return stroke(d, sw * th, P.get('brow_col', LINE))


def mouth(x, y, fc, ex, P, sw):
    if fc < .1:
        return ''
    sq = max(fc, .3) ** .8
    k = ex['mouth']
    w = P.get('mouth_w', 12) * sq
    MC = '#7b2f35'
    if k == 'soft':
        c = P.get('smile', 4)
        return stroke(f'M{f(x - w)},{f(y - c * .3)} Q{f(x)},{f(y + c)} {f(x + w)},{f(y - c * .3)}', sw * 1.1)
    if k == 'flat':
        return stroke(f'M{f(x - w)},{f(y)} Q{f(x)},{f(y + 1)} {f(x + w)},{f(y + 1.5)}', sw * 1.1)
    if k == 'strict':
        return stroke(f'M{f(x - w)},{f(y + 1.5)} Q{f(x)},{f(y - 1)} {f(x + w)},{f(y + 1.5)}', sw * 1.1)
    if k == 'grump':
        return stroke(f'M{f(x - w)},{f(y + 3)} Q{f(x)},{f(y - 3)} {f(x + w)},{f(y + 3)}', sw * 1.1)
    if k == 'smirk':
        return stroke(f'M{f(x - w)},{f(y)} Q{f(x + w * .1)},{f(y + 4)} {f(x + w * 1.1)},{f(y - 5)}', sw * 1.15)
    if k == 'frown':
        return stroke(f'M{f(x - w * .8)},{f(y + 3)} Q{f(x)},{f(y - 4)} {f(x + w * .8)},{f(y + 3)}', sw * 1.1)
    if k == 'open':
        W = w * 1.25
        d = f'M{f(x - W)},{f(y - 2)} Q{f(x)},{f(y + 1)} {f(x + W)},{f(y - 2)} Q{f(x + W * .8)},{f(y + W * 1.1)} {f(x)},{f(y + W * 1.15)} Q{f(x - W * .8)},{f(y + W * 1.1)} {f(x - W)},{f(y - 2)} Z'
        cid = uid('m')
        t = f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})"><path d="{d}" fill="{MC}"/><ellipse cx="{f(x)}" cy="{f(y + W * 1.15)}" rx="{f(W * .7)}" ry="{f(W * .5)}" fill="#e0767a"/></g>'
        return t + stroke(d, sw)
    if k == 'o':
        d = ellipse_d(x, y + 3, w * .45, w * .6)
        return shape(d, MC, shade=False, sw=sw)
    if k == 'clench':
        W = w * 1.1
        d = f'M{f(x - W)},{f(y + 2)} Q{f(x)},{f(y - 4)} {f(x + W)},{f(y + 2)} L{f(x + W * .9)},{f(y + 8)} Q{f(x)},{f(y + 5)} {f(x - W * .9)},{f(y + 8)} Z'
        return shape(d, '#fffaf2', shade=False, sw=sw) + stroke(f'M{f(x - W * .9)},{f(y + 4.5)} Q{f(x)},{f(y + 1)} {f(x + W * .9)},{f(y + 4.5)}', sw * .6)
    if k == 'grin':
        W = w * 1.35
        d = f'M{f(x - W)},{f(y - 4)} Q{f(x)},{f(y + 2)} {f(x + W)},{f(y - 7)} Q{f(x + W * .6)},{f(y + W * .95)} {f(x - W * .1)},{f(y + W * .85)} Q{f(x - W * .8)},{f(y + W * .7)} {f(x - W)},{f(y - 4)} Z'
        cid = uid('m')
        teeth = f'<path d="M{f(x - W)},{f(y - 4)} Q{f(x)},{f(y + 2)} {f(x + W)},{f(y - 7)} L{f(x + W)},{f(y + 1)} L{f(x - W)},{f(y + 4)} Z" fill="#fffaf2"/>'
        gap = f'<rect x="{f(x - W * .15)}" y="{f(y - 4)}" width="{f(W * .22)}" height="{f(7)}" fill="{MC}"/>' if P.get('gap') else ''
        t = f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})"><path d="{d}" fill="{MC}"/>{teeth}{gap}<ellipse cx="{f(x)}" cy="{f(y + W * .9)}" rx="{f(W * .6)}" ry="{f(W * .4)}" fill="#e0767a"/></g>'
        return t + stroke(d, sw)
    return ''
