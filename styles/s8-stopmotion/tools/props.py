"""Things on a puppet's face: glasses, a moustache, a watchmaker's loupe. All placed in head units, so they turn
with the head."""
import math
from sculpt import pts, poly, f, mix


def glasses(h, d, P, shape='round', rw=0.085, rh=0.075, out=0.07, col='#3a2a22', lw=0.012, y_off=0.0, lens='#dfefff'):
    """Spectacles: two rims in front of the eyes, a bridge over the nose, temples back to the ears."""
    S = h.S
    res = []
    ye = P['eye_y'] + y_off
    rims = {}
    for side in (-1, 1):
        phi = side * P['eye_phi']
        tr, _ = h.frame(phi, ye, out)
        if shape == 'round':
            ring = [(rw * math.cos(t), rh * math.sin(t)) for t in [2 * math.pi * i / 32 for i in range(32)]]
        elif shape == 'half':     # half-moon reading glasses: a flat top
            ring = [(rw * math.cos(t), rh * max(-0.15, math.sin(t))) for t in [2 * math.pi * i / 36 for i in range(36)]]
        else:   # soft rectangle, a little narrower at the bottom, the outer top corner lifted
            ring = []
            for i in range(40):
                t = 2 * math.pi * i / 40
                c, s = math.cos(t), math.sin(t)
                x = rw * math.copysign(abs(c) ** 0.45, c)
                y = rh * math.copysign(abs(s) ** 0.5, s)
                if y > 0:
                    x *= 0.9
                ring.append((x, y))
        rims[side] = (tr, ring)
        vis = h.facing(phi, ye)
        if vis < -0.2:
            continue
        # lens: faint tint and a glare stripe from the key light
        cid = d.uid('ln')
        d.defs.append(f'<clipPath id="{cid}"><path d="{poly(ring)}" transform="{tr}"/></clipPath>')
        res.append(f'<g clip-path="url(#{cid})"><path d="{poly(ring)}" transform="{tr}" fill="{lens}" opacity="0.12"/>'
                   f'<path d="M{f(-rw*1.2)} {f(-rh*0.2)} L{f(-rw*0.2)} {f(-rh*1.2)} L{f(rw*0.15)} {f(-rh*1.2)} L{f(-rw*1.2)} {f(rh*0.25)}Z" '
                   f'transform="{tr}" fill="#ffffff" opacity="0.28"/></g>')
        res.append(d.bump(poly(ring), col, soft=max(1, S * 0.004), height=max(2, S * 0.012), spec=0.6, shine=40,
                          stroke=True, sw=lw, tr=tr))
    # bridge over the nose
    a = h.P(h.surf(-P['eye_phi'] * 0.45, ye - 0.02, out * 0.8))
    b = h.P(h.surf(0, ye - 0.03, out * 0.9))
    c = h.P(h.surf(P['eye_phi'] * 0.45, ye - 0.02, out * 0.8))
    res.append(d.bump(pts([a, b, c], close=False), col, soft=max(1, S * 0.004), height=max(2, S * 0.01), spec=0.6, shine=40,
                      stroke=True, sw=lw * S))
    # temples to the ears (only the near one shows past the face)
    for side in (-1, 1):
        p0 = h.surf(side * (P['eye_phi'] + 0.45), ye - 0.01, out * 0.6)
        p1 = h.surf(side * P['ear_phi'], P['ear_y'] - 0.03, 0.01)
        if h.rot(p0)[2] > -0.05:
            res.append(d.bump(pts([h.P(p0), h.P(p1)], close=False), col, soft=1, height=2, spec=0.5, stroke=True, sw=lw * S * 0.8))
    return res


def moustache(h, d, P, col, w=0.17, y=None, droop=0.05, thick=0.07, ex=None):
    """A sculpted moustache: one mass of two drooping wings under the nose, shaded as a form, cut with strands."""
    S = h.S
    y0 = (P['nose_tip'] + P['mouth_y']) / 2 + 0.005 if y is None else y
    tr, _ = h.frame(0, y0, 0.035)
    smile = (ex or {}).get('smile', 0.0)
    n = 12
    up, lo = [], []
    for i in range(-n, n + 1):
        t = abs(i) / n
        x = w * i / n
        lift = -smile * 0.03 * t
        up.append((x, -thick * 0.55 * (1 - t ** 1.8) + droop * t ** 1.5 + lift - 0.004 * math.cos(math.pi * t * 3) * (1 - t)))
        lo.append((x * 0.97, thick * 0.4 * (1 - t ** 1.2) + droop * t ** 1.3 + 0.008 + lift + 0.012 * (1 - t) * math.sin(math.pi * t * 4)))
    shape = up + lo[::-1]
    fid = d.form(S * 0.25, shade=P.get('hair_shade', '#4a3a3a'), depth=0.7, ao=0.4, sheen=0.25, rim=0.0, reach=0.25)
    res = [f'<g filter="url(#{fid})"><path d="{pts(shape)}" transform="{tr}" fill="{col}"/></g>']
    gid = d.relief(1.0, -max(1.5, round(S * 0.007, 1)), 0, 20)
    st = ''
    for side in (-1, 1):
        for k in range(7):
            o = -0.4 + 0.13 * k
            line = []
            for i in range(0, 10):
                t = i / 9
                x = side * (0.01 + w * t * 0.95)
                yy = o * thick * (1 - t * 0.8) + droop * t ** 1.4 - smile * 0.03 * t
                line.append((x, yy))
            st += f'<path d="{pts(line, close=False)}" transform="{tr}" fill="none" stroke="{mix(col, "#000000", 0.15)}" stroke-width="0.005"/>'
    cid = d.uid('mu')
    d.defs.append(f'<clipPath id="{cid}"><path d="{pts(shape)}" transform="{tr}"/></clipPath>')
    res.append(f'<g clip-path="url(#{cid})"><g filter="url(#{gid})">{st}</g></g>')
    return res


def loupe(h, d, P, side=1, col='#2a2420', out=0.11):
    """A watchmaker's loupe pushed up on the forehead: a little black cone on a band."""
    S = h.S
    phi, y = side * P['eye_phi'] * 1.05, P['eye_y'] - 0.27
    tr, _ = h.frame(phi, y, out)
    res = []
    # band round the head
    band = [h.P(h.surf(p, y - 0.01, 0.012, 1.04)) for p in [-math.pi * 0.5 + i * math.pi / 20 for i in range(21)]
            if h.facing(p, y) > -0.1]
    if len(band) > 2:
        res.append(d.bump(pts(band, close=False), '#4a3426', soft=max(1, S * 0.005), height=max(2, S * 0.01), spec=0.3,
                          stroke=True, sw=S * 0.03))
    cone = [(-0.06, -0.05), (0.06, -0.05), (0.075, 0.05), (-0.075, 0.05)]
    res.append(d.bump(pts(cone), col, soft=max(1.5, S * 0.008), height=max(3, S * 0.03), spec=0.7, shine=40, tr=tr))
    glass = [(0.065 * math.cos(t), 0.05 + 0.02 * math.sin(t)) for t in [2 * math.pi * i / 20 for i in range(20)]]
    res.append(f'<path d="{poly(glass)}" transform="{tr}" fill="#9ab0c0" opacity="0.8"/>')
    return res


def bun(h, d, P, col, y=-0.3, phi=math.pi * 0.92, r=0.15):
    """A hair bun at the back of the head: a coiled ball of locks. Returns (depth, svg)."""
    S = h.S
    c = h.surf(phi, y, r * 0.6, 1.0)
    x, yy, z = h.scr(c)
    R = r * S
    body = f'<circle cx="{f(x)}" cy="{f(yy)}" r="{f(R)}" fill="{col}"/>'
    fid = d.form(R * 2, shade=P.get('hair_shade', '#140806'), depth=0.7, ao=0.4, sheen=0.1, rim=0.0)
    gid = d.relief(1.2, -max(2, round(S * 0.01, 1)), 0, 20)
    coil = ''
    for k in range(3):
        rr = R * (0.85 - 0.25 * k)
        coil += f'<path d="M{f(x-rr)} {f(yy)} A{f(rr)} {f(rr*0.9)} 0 1 1 {f(x+rr*0.7)} {f(yy+rr*0.6)}" fill="none" stroke="{col}" stroke-width="{f(S*0.008)}"/>'
    return z, f'<g filter="url(#{fid})">{body}</g><g filter="url(#{gid})">{coil}</g>'
