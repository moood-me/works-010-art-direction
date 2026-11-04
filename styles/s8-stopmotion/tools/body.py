"""Puppet bodies.

A bust (for portraits and turnarounds) is built from lofts like the head (head.Head with other tables): a neck, a
torso and two upper arms, all in head units under the head centre (y = 0.5 is the chin, y = 1 is one head lower).
The torso turns less than the head (body_yaw), the neck in between. Clothes are the torso's own colour and texture
plus details laid on the surface (necklines, plackets, buttons, folds) with Head.frame.

Full figures (figure()) are drawn in one view only, as a stack of sculpted parts (see figures.py).
"""
import math
from sculpt import pts, poly, f, mix
from head import Head
from puppet import draw_head


def loft(d, L, y0, y1, col, size, texture=None, tex_amount=0.2, tex_scale=1.0, n=40, inside=None, **form):
    """A loft drawn as one sculpted object: its colour, anything painted on it (inside(o) → svg: stripes, panels),
    then form shading over all of it, then the material texture."""
    o = L.outline(y0=y0, y1=y1, n=n)
    fid = d.form(size, **form)
    s = f'<g filter="url(#{fid})"><path d="{pts(o)}" fill="{col}"/>{inside(o) if inside else ""}</g>'
    if texture:
        tid = d.tex(texture, tex_scale, tex_amount)
        s += f'<path d="{pts(o)}" fill="{col}" filter="url(#{tid})"/>'
    return s, o


def tx(T, X, y, out=0.0):
    """Point on the front of a loft at lateral offset X (head units) and height y."""
    phi = math.asin(max(-1.0, min(1.0, X / max(T.a(y), 1e-3))))
    return T.surf(phi, y, out)


def front_patch(T, xs_ys, out=0.0):
    """Screen polygon of a patch on the front of a loft given by (X, y) points."""
    return [T.P(tx(T, X, y, out)) for X, y in xs_ys]


def stripes(d, L, y0, y1, step, col, clip_outline, n=48):
    """Horizontal stripes knitted into a loft (bands of another colour)."""
    body = ''
    k = int((y1 - y0) / step)
    for i in range(0, k, 2):
        ya, yb = y0 + i * step, y0 + (i + 1) * step
        top, bot = [], []
        for j in range(n + 1):
            phi = -math.pi + 2 * math.pi * j / n
            top.append(L.scr(L.surf(phi, ya)))
            bot.append(L.scr(L.surf(phi, yb)))
        # keep the front half: points facing us
        fr = [j for j in range(n + 1) if L.facing(-math.pi + 2 * math.pi * j / n, (ya + yb) / 2) > -0.15]
        if len(fr) < 2:
            continue
        poly_ = [top[j][:2] for j in fr] + [bot[j][:2] for j in fr[::-1]]
        body += f'<path d="{poly(poly_)}" fill="{col}"/>'
    c = d.uid('st')
    d.defs.append(f'<clipPath id="{c}"><path d="{pts(clip_outline)}"/></clipPath>')
    return f'<g clip-path="url(#{c})" opacity="0.92">{body}</g>'


def ribs(d, L, y0, y1, col, step=0.1, S=None, width=None, depth=None, clip_outline=None, horizontal=False, n=24):
    """Knit ribs (or cord, or pleats): grooves running down the surface of a loft (or round it if horizontal)."""
    S = L.S
    lines = []
    if not horizontal:
        k = int(2 * math.pi / step)
        for i in range(k):
            phi = -math.pi + i * step
            seg = []
            for j in range(n + 1):
                y = y0 + (y1 - y0) * j / n
                x, yy, z = L.scr(L.surf(phi, y))
                if L.facing(phi, y) > 0.05:
                    seg.append((x, yy))
                elif len(seg) > 1:
                    lines.append(seg)
                    seg = []
                else:
                    seg = []
            if len(seg) > 1:
                lines.append(seg)
    else:
        k = int((y1 - y0) / step)
        for i in range(k + 1):
            y = y0 + i * step
            seg = []
            for j in range(73):
                phi = -math.pi + 2 * math.pi * j / 72
                if L.facing(phi, y) > 0.02:
                    seg.append(L.P(L.surf(phi, y)))
                elif len(seg) > 1:
                    lines.append(seg); seg = []
                else:
                    seg = []
            if len(seg) > 1:
                lines.append(seg)
    w = width or max(1.2, S * 0.007)
    gid = d.relief(max(1.0, round(S * 0.005, 1)), -(depth or max(2.0, round(S * 0.007, 1))), 0, 20)
    body = ''.join(f'<path d="{pts(s, close=False)}" fill="none" stroke="{col}" stroke-width="{f(w)}" stroke-linecap="round"/>' for s in lines)
    g = f'<g filter="url(#{gid})">{body}</g>'
    if clip_outline:
        c = d.uid('rb')
        d.defs.append(f'<clipPath id="{c}"><path d="{pts(clip_outline)}"/></clipPath>')
        g = f'<g clip-path="url(#{c})">{g}</g>'
    return g


def neckline(d, T, P, B, S, torso_outline):
    """An open neckline: skin of the upper chest above a curve on the torso, and a band (rib, hem) along the curve.
    B['neckline'] = (y at the front, y at the back, band width, band colour, phi half-range)."""
    yf, yb, bw, bc, wn = B['neckline']       # wn: half width of the neckline at the shoulders (head units)
    out = []
    curve, top = [], []
    N = 40
    for j in range(N + 1):
        t = -1 + 2 * j / N
        y = yb + (yf - yb) * (1 - t * t) ** 0.8
        X = t * wn
        phi = math.asin(max(-1, min(1, X / max(T.a(y), 1e-3))))
        if T.facing(phi, y) > -0.05:
            curve.append(T.P(T.surf(phi, y)))
            yt = B['torso_y'][0] + 0.005
            pt = math.asin(max(-1, min(1, X / max(T.a(yt), 1e-3))))
            top.append(T.P(T.surf(pt, yt)))
    if len(curve) < 3:
        return out
    patch = curve + top[::-1]
    c = d.uid('tc')
    d.defs.append(f'<clipPath id="{c}"><path d="{pts(torso_outline)}"/></clipPath>')
    skin = mix(P['skin'], '#c07a70', 0.12)
    out.append(f'<g clip-path="url(#{c})">' + d.shape(poly(patch), skin, S * 0.5, 'clay', 0.04, shade=P.get('shade', '#5a2438'), depth=0.6) + '</g>')
    # collarbones
    for side in (-1, 1):
        cb = [T.P(T.surf(side * (0.1 + 0.35 * t), B['torso_y'][0] + 0.09 + 0.02 * t * t, 0.004)) for t in (0, 0.33, 0.66, 1)]
        if T.facing(side * 0.4, B['torso_y'][0] + 0.08) > 0.1:
            out.append(f'<g clip-path="url(#{c})">' + d.bump(pts(cb, close=False), skin, soft=max(1.5, S * 0.008), height=max(2, S * 0.012),
                                                            spec=0.25, stroke=True, sw=S * 0.012) + '</g>')
    # the band
    out.append(f'<g clip-path="url(#{c})">' + d.bump(pts(curve, close=False), bc, soft=max(1.5, S * 0.01), height=max(3, S * 0.025),
                                                    spec=0.25, stroke=True, sw=bw * S) + '</g>')
    return out


def bust(d, P, B, ex, S, cx, cy, yaw=30, roll=0, body_yaw=None, extra=None):
    """Head + neck + shoulders + upper arms. B: the body dict of the character (see cast.py)."""
    by = yaw * 0.55 if body_yaw is None else body_yaw
    ny = (yaw + by) / 2
    T = Head(B['torso'], S, cx, cy, by)
    N = Head(B['neck'], S, cx, cy, ny)
    hd = draw_head(d, P, ex, S, cx, cy, yaw, roll)
    out = list(hd['back'])
    cloth = B['cloth']
    tex = B.get('tex', 'cloth')
    sz = S * 1.1
    shade = B.get('shade', '#2a1830')
    # arms: far one first
    arms = []
    for side in (-1, 1):
        A = Head(dict(B['arm'], x=[(0, side * B['arm_x'])]), S, cx, cy, by)
        z = T.rot((side * B['arm_x'], 0, 0))[2]
        arms.append((z, side, A))
    arms.sort(key=lambda t: t[0])
    y_arm0, y_arm1 = B['arm_y']
    def arm(A):
        ins = (lambda o: B['arm_inside'](d, A, P, B, S, o)) if B.get('arm_inside') else None
        s, o = loft(d, A, y_arm0, y_arm1, B.get('sleeve', cloth), S * 0.5, B.get('sleeve_tex', tex), B.get('tex_amount', 0.22),
                    shade=shade, inside=ins)
        if B.get('ribs'):
            s += ribs(d, A, y_arm0 + 0.06, y_arm1, B.get('sleeve', cloth), step=B['ribs'], clip_outline=o)
        return s
    for z, side, A in arms:
        out.append(arm(A))
    # neck
    nk = N.outline(y0=B['neck_y'][0], y1=B['neck_y'][1], n=20)
    out.append(d.shape(pts(nk), mix(P['skin'], '#c08070', 0.15), S * 0.3, 'clay', 0.04, shade=P.get('shade', '#5a2438'), depth=0.7))
    # torso
    ty0, ty1 = B['torso_y']
    ins = (lambda o: B['inside'](d, T, P, B, S, o)) if B.get('inside') else None
    s, to = loft(d, T, ty0, ty1, cloth, sz, tex, B.get('tex_amount', 0.22), shade=shade, depth=0.6, inside=ins)
    out.append(s)
    if B.get('ribs'):
        out.append(ribs(d, T, ty0 + 0.05, ty1, cloth, step=B['ribs'], clip_outline=to))
    if B.get('neckline'):
        out.extend(neckline(d, T, P, B, S, to))
    if B.get('collar'):
        C = Head(B['collar'], S, cx, cy, ny)
        cy0, cy1 = B['collar_y']
        s, co = loft(d, C, cy0, cy1, B.get('collar_col', cloth), S * 0.35, tex, B.get('tex_amount', 0.22), shade=shade)
        out.append(s)
        if B.get('ribs'):
            out.append(ribs(d, C, cy0, cy1, B.get('collar_col', cloth), step=B['ribs'] * 0.8, clip_outline=co, n=6))
        if B.get('collar_extra'):
            out.extend(B['collar_extra'](d, T, C, P, B, S))
    if B.get('details'):
        out.extend(B['details'](d, T, N, P, B, S))
    # the neck again over the neckline if the clothes are open at the neck
    if B.get('open_neck'):
        clip = d.uid('nk')
        d.defs.append(f'<clipPath id="{clip}"><path d="{pts(B["open_neck"](T))}"/></clipPath>')
        out.append(f'<g clip-path="url(#{clip})">' +
                   d.shape(pts(nk), mix(P['skin'], '#c08070', 0.15), S * 0.3, 'clay', 0.04, shade=P.get('shade', '#5a2438'), depth=0.7) + '</g>')
    # the chin's shadow on the neck
    h = hd['h']
    jaw = h.outline(y0=0.25, y1=0.5, n=12)
    sh = [(x + S * 0.04, y + S * 0.07) for x, y in jaw]
    clip = d.uid('nc')
    d.defs.append(f'<clipPath id="{clip}"><path d="{pts(nk)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{clip})"><g filter="url(#{d.blur(S*0.025)})" opacity="0.55"><path d="{pts(sh)}" fill="#3a1420"/></g></g>')
    if extra:
        out.extend(extra(d, T, N, P, B, S))
    out.extend(hd['head'])
    return out, hd['h'], T
