"""A whole puppet standing on the set floor.

The body is posed in 3D (head units; head centre at the origin, y down, z toward us) and drawn turned by the body
yaw: a torso loft (as in body.bust, longer), limbs as tubes along 3D polylines (arms, legs), sculpted hands and shoes,
and skirt or coat as lofts. Parts are sorted by depth (painter's order). F (the character's figure dict) gives the
pose and the clothes; see cast.py.
"""
import math
from sculpt import pts, poly, f, mix
from head import Head
from puppet import draw_head
from body import loft, ribs, stripes, neckline


def _ribbon(Pts, radii):
    """Outline of a tube through screen points with screen radii (round ends)."""
    n = len(Pts)
    L, R = [], []
    for i in range(n):
        x, y = Pts[i]
        xa, ya = Pts[max(0, i - 1)]
        xb, yb = Pts[min(n - 1, i + 1)]
        dx, dy = xb - xa, yb - ya
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        L.append((x + nx * radii[i], y + ny * radii[i]))
        R.append((x - nx * radii[i], y - ny * radii[i]))
    # round caps
    def cap(c, r, a0):
        return [(c[0] + r * math.cos(a0 + math.pi * k / 6), c[1] + r * math.sin(a0 + math.pi * k / 6)) for k in range(1, 6)]
    x0, y0 = Pts[0]; x1, y1 = Pts[1]
    a_start = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
    xe, ye = Pts[-1]; xp, yp = Pts[-2]
    a_end = math.atan2(ye - yp, xe - xp) - math.pi / 2
    return L + cap(Pts[-1], radii[-1], a_end)[::-1] + R[::-1] + cap(Pts[0], radii[0], a_start)[::-1]


def _smooth3(p, n=16):
    """Catmull-Rom resample of a 3D polyline."""
    if len(p) < 3:
        return [tuple(p[0][k] + (p[-1][k] - p[0][k]) * i / (n - 1) for k in range(3)) for i in range(n)]
    out = []
    seg = len(p) - 1
    for i in range(n):
        u = i / (n - 1) * seg
        j = min(int(u), seg - 1)
        t = u - j
        p0, p1, p2, p3 = p[max(0, j - 1)], p[j], p[j + 1], p[min(seg, j + 2)]
        out.append(tuple(0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                                + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in range(3)))
    return out


def tube(d, T, path3, r0, r1, col, texture=None, tex_amount=0.2, shade='#2a1830', ribs_step=None, stripes_col=None,
         radii=None, n=16):
    """A limb or sleeve: a tube along a 3D path, radius from r0 to r1 (head units). Returns (depth, svg)."""
    S = T.S
    P3 = _smooth3(path3, n)
    sc = [T.scr(p) for p in P3]
    Pts = [(q[0], q[1]) for q in sc]
    rr = radii or [r0 + (r1 - r0) * i / (n - 1) for i in range(n)]
    o = _ribbon(Pts, [r * S for r in rr])
    size = max(rr) * 2 * S * 2.2
    fid = d.form(size, shade=shade, depth=0.65, ao=0.4, sheen=0.15, rim=0.25, reach=0.3)
    inner = ''
    if stripes_col:
        # stripes across the tube
        k = 0
        segs = ''
        for i in range(0, n - 1, 2):
            a, b = Pts[i], Pts[i + 1]
            ra, rb = rr[i] * S * 1.3, rr[i + 1] * S * 1.3
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / ln, dx / ln
            segs += f'<path d="{poly([(a[0]+nx*ra, a[1]+ny*ra), (b[0]+nx*rb, b[1]+ny*rb), (b[0]-nx*rb, b[1]-ny*rb), (a[0]-nx*ra, a[1]-ny*ra)])}" fill="{stripes_col}"/>'
        cid = d.uid('ts')
        d.defs.append(f'<clipPath id="{cid}"><path d="{pts(o)}"/></clipPath>')
        inner = f'<g clip-path="url(#{cid})">{segs}</g>'
    s = f'<g filter="url(#{fid})"><path d="{pts(o)}" fill="{col}"/>{inner}</g>'
    if texture:
        tid = d.tex(texture, 1.0, tex_amount)
        s += f'<path d="{pts(o)}" fill="{col}" filter="url(#{tid})"/>'
    if ribs_step:
        gid = d.relief(1.0, -max(1.5, round(S * 0.006, 1)), 0, 20)
        lines = ''
        for o_ in (-0.6, -0.2, 0.2, 0.6):
            line = []
            for i in range(1, n - 1):
                a = Pts[i]
                b = Pts[min(n - 1, i + 1)]
                dx, dy = b[0] - a[0], b[1] - a[1]
                ln = math.hypot(dx, dy) or 1
                nx, ny = -dy / ln, dx / ln
                line.append((a[0] + nx * rr[i] * S * o_, a[1] + ny * rr[i] * S * o_))
            lines += f'<path d="{pts(line, close=False)}" fill="none" stroke="{col}" stroke-width="{f(max(1.2, S*0.007))}"/>'
        cid = d.uid('tr')
        d.defs.append(f'<clipPath id="{cid}"><path d="{pts(o)}"/></clipPath>')
        s += f'<g clip-path="url(#{cid})"><g filter="url(#{gid})">{lines}</g></g>'
    return sum(q[2] for q in sc) / n, s


def hand(d, T, wrist, direction, skin, size=0.11, pose='relaxed', side=1, shade='#5a2438'):
    """A sculpted puppet hand at a 3D wrist point, pointing along a 3D direction. pose: relaxed | fist | open | hold.
    Returns (depth, svg)."""
    S = T.S
    w = T.scr(wrist)
    tip = T.scr((wrist[0] + direction[0] * size, wrist[1] + direction[1] * size, wrist[2] + direction[2] * size))
    ang = math.degrees(math.atan2(tip[1] - w[1], tip[0] - w[0])) - 90
    L = size * S
    g = f'<g transform="translate({f(w[0])},{f(w[1])}) rotate({f(ang)}) scale({f(-side if T.cy_ >= 0 else side)},1)">'
    parts = []
    # palm
    palm = [(-0.32, 0.0), (0.3, 0.0), (0.38, 0.5), (0.25, 0.75), (-0.3, 0.75), (-0.4, 0.45)]
    parts.append(('palm', [(x * L, y * L) for x, y in palm]))
    fingers = []
    if pose in ('relaxed', 'open'):
        spread = 0.06 if pose == 'relaxed' else 0.16
        curl = 0.25 if pose == 'relaxed' else 0.05
        for k, (fx, ln) in enumerate(((-0.24, 0.42), (-0.06, 0.5), (0.12, 0.47), (0.28, 0.36))):
            a = (k - 1.5) * spread
            x0, y0 = fx * L, 0.72 * L
            x1 = x0 + math.sin(a) * ln * L
            y1 = y0 + math.cos(a) * ln * L * (1 - curl * 0.5)
            x2 = x1 + math.sin(a - curl) * 0.12 * L
            y2 = y1 + math.cos(a - curl) * 0.1 * L
            fingers.append([(x0, y0), (x1, y1), (x2, y2)])
        thumb = [(0.36 * L, 0.3 * L), (0.55 * L, 0.55 * L), (0.6 * L, 0.78 * L)]
    elif pose == 'fist':
        for k, fx in enumerate((-0.24, -0.06, 0.12, 0.28)):
            fingers.append([(fx * L, 0.7 * L), (fx * L, 0.88 * L), (fx * L * 0.9, 0.82 * L)])
        thumb = [(0.36 * L, 0.35 * L), (0.4 * L, 0.6 * L), (0.15 * L, 0.72 * L)]
    else:  # hold: fingers curled round something
        for k, fx in enumerate((-0.24, -0.06, 0.12, 0.28)):
            fingers.append([(fx * L, 0.7 * L), (fx * L + 0.05 * L, 0.95 * L), (fx * L - 0.05 * L, 1.02 * L)])
        thumb = [(0.36 * L, 0.3 * L), (0.5 * L, 0.6 * L), (0.35 * L, 0.85 * L)]
    col = mix(skin, '#c07a70', 0.1)
    out = d.shape(pts(parts[0][1]), col, L * 1.2, 'clay', 0.04, shade=shade, depth=0.55, reach=0.25)
    fr = max(1.5, L * 0.09)
    fing = ''.join(f'<path d="{pts(fp, close=False)}" fill="none" stroke="{col}" stroke-width="{f(fr*2)}" stroke-linecap="round" stroke-linejoin="round"/>'
                   for fp in fingers + [thumb])
    rid = d.relief(max(1.2, round(L * 0.05, 1)), max(2, round(L * 0.12, 1)), 0.3, 20)
    out += f'<g filter="url(#{rid})">{fing}</g>'
    return w[2], g + out + '</g>'


def _hull(points):
    pts_ = sorted(set((round(x, 2), round(y, 2)) for x, y in points))
    if len(pts_) < 3:
        return pts_

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts_:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts_):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def shoe(d, T, ankle, length, col, side=1, height=0.1, width=0.09, toe_up=0.0, sole='#2a1a14'):
    """A puppet shoe: a rounded box (half an ellipsoid on a sole) from heel to a big round toe, turned with the body.
    Returns (depth, svg)."""
    S = T.S
    x, y, z = ankle
    floor = y + height * 0.9
    cz = z + length * 0.3                 # the shoe sticks forward of the ankle
    up_pts, sole_pts = [], []
    for i in range(24):
        a = 2 * math.pi * i / 24
        for j in range(7):
            b = math.pi / 2 * j / 6       # 0 = sole level, pi/2 = top
            X = x + side * 0.01 + width * math.cos(a) * math.cos(b) * (1.1 if math.sin(a) > 0 else 0.95)
            Z = cz + length * 0.5 * math.sin(a) * math.cos(b)
            Y = floor - height * math.sin(b) * (1.0 - 0.35 * max(0, math.sin(a))) - toe_up * max(0, math.sin(a)) ** 3
            up_pts.append(T.P((X, Y, Z)))
        X = x + side * 0.01 + width * 1.05 * math.cos(a)
        Z = cz + length * 0.52 * math.sin(a)
        sole_pts.append(T.P((X, floor + 0.015, Z)))
        sole_pts.append(T.P((X, floor - 0.02, Z)))
    hull = _hull(up_pts)
    shull = _hull(sole_pts)
    s = d.shape(poly(shull), sole, S * 0.3, None, shade='#000000', depth=0.4, sheen=0.1, reach=0.2)
    s += d.shape(pts(hull), col, S * 0.3, 'clay', 0.05, shade='#140a0a', depth=0.6, sheen=0.35, reach=0.25)
    return T.scr((x, y, cz))[2], s


def figure(d, P, B, F, ex, S, cx, cy, yaw=20, body_yaw=None, roll=0, head_dx=0.0, head_dy=0.0):
    """The whole puppet. Head centre at (cx + head_dx*S, cy + head_dy*S); the body hangs under (cx, cy)."""
    by = yaw * 0.6 if body_yaw is None else body_yaw
    T = Head(F.get('torso', B['torso']), S, cx, cy, by)
    N = Head(B['neck'], S, cx, cy, (yaw + by) / 2)
    parts = []                   # (depth, svg)
    hd = draw_head(d, P, ex, S, cx + head_dx * S, cy + head_dy * S, yaw, roll)
    back = list(hd['back'])
    shade = B.get('shade', '#2a1830')
    cloth = B['cloth']
    tex = B.get('tex', 'cloth')
    # legs
    for side in (-1, 1):
        for item in F['legs'](side):
            z, s = tube(d, T, item['path'], item['r0'], item['r1'], item['col'], item.get('tex'), item.get('tex_amount', 0.2),
                        shade=item.get('shade', shade), ribs_step=item.get('ribs'), stripes_col=item.get('stripes'))
            parts.append((z + item.get('z', -0.5), s))
        sh = F['shoe'](side)
        z, s = shoe(d, T, sh['ankle'], sh['len'], sh['col'], side, sh.get('h', 0.1), sh.get('w', 0.09), sh.get('toe_up', 0.0))
        parts.append((z + sh.get('z', -0.15), s))
    # skirt / coat tails
    for sk in F.get('skirts', []):
        L = Head(sk['table'], S, cx, cy, by)
        s, o = loft(d, L, sk['y'][0], sk['y'][1], sk['col'], S * 1.2, sk.get('tex'), sk.get('tex_amount', 0.2),
                    shade=sk.get('shade', shade), depth=0.6)
        if sk.get('ribs'):
            s += ribs(d, L, sk['y'][0], sk['y'][1], sk['col'], step=sk['ribs'], clip_outline=o)
        parts.append((sk.get('z', 0.0), s))
    # torso
    ty0, ty1 = F.get('torso_y', B['torso_y'])
    nk = N.outline(y0=B['neck_y'][0], y1=B['neck_y'][1], n=20)
    parts.append((-0.05, d.shape(pts(nk), mix(P['skin'], '#c08070', 0.15), S * 0.3, 'clay', 0.04, shade=P.get('shade', '#5a2438'), depth=0.7)))
    ins = (lambda o: F['inside'](d, T, P, B, S, o)) if F.get('inside') else ((lambda o: B['inside'](d, T, P, B, S, o)) if B.get('inside') else None)
    s, to = loft(d, T, ty0, ty1, cloth, S * 1.1, tex, B.get('tex_amount', 0.22), shade=shade, depth=0.6, inside=ins)
    if B.get('ribs'):
        s += ribs(d, T, ty0 + 0.05, ty1, cloth, step=B['ribs'], clip_outline=to)
    if B.get('neckline'):
        s += ''.join(neckline(d, T, P, B, S, to))
    if B.get('collar'):
        C = Head(B['collar'], S, cx, cy, (yaw + by) / 2)
        cy0, cy1 = B['collar_y']
        cs, co = loft(d, C, cy0, cy1, B.get('collar_col', cloth), S * 0.35, tex, B.get('tex_amount', 0.22), shade=shade)
        s += cs
        if B.get('ribs'):
            s += ribs(d, C, cy0, cy1, B.get('collar_col', cloth), step=B['ribs'] * 0.8, clip_outline=co, n=6)
        if B.get('collar_extra'):
            s += ''.join(B['collar_extra'](d, T, C, P, B, S))
    if B.get('details'):
        s += ''.join(B['details'](d, T, N, P, B, S))
    for extra in F.get('torso_extra', []):
        s += ''.join(extra(d, T, P, B, S))
    parts.append((0.0, s))
    # chin shadow on the neck
    h = hd['h']
    jaw = h.outline(y0=0.25, y1=0.5, n=12)
    shp = [(x + S * 0.04, y + S * 0.07) for x, y in jaw]
    clip = d.uid('nc')
    d.defs.append(f'<clipPath id="{clip}"><path d="{pts(nk)}"/></clipPath>')
    parts.append((-0.04, f'<g clip-path="url(#{clip})"><g filter="url(#{d.blur(S*0.025)})" opacity="0.55"><path d="{pts(shp)}" fill="#3a1420"/></g></g>'))
    # arms and hands
    for side in (-1, 1):
        for item in F['arms'](side):
            z, s = tube(d, T, item['path'], item['r0'], item['r1'], item['col'], item.get('tex'), item.get('tex_amount', 0.2),
                        shade=item.get('shade', shade), ribs_step=item.get('ribs'), stripes_col=item.get('stripes'))
            parts.append((z + item.get('z', 0.0), s))
        hh = F['hand'](side)
        if hh:
            z, s = hand(d, T, hh['wrist'], hh['dir'], P['skin'], hh.get('size', 0.11), hh.get('pose', 'relaxed'), side,
                        P.get('shade', '#5a2438'))
            parts.append((z + hh.get('z', 0.02), s))
    for pr in F.get('props', []):
        parts.append(pr(d, T, P, S))
    parts.sort(key=lambda t: t[0])
    return back + [s for _, s in parts] + hd['head'], T
