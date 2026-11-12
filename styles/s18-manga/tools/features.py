"""Shared parts of faces: the shape of a head from the base one, glasses, wrinkles, freckles, a beard, a moustache."""
import math, random
from pen import *
from head import ADULT, on, View, silhouette, interp_table, Head


def sections(cranium=1.0, cheek=1.0, jaw=1.0, chin=1.0, depth=1.0, face=1.0, top=None, bottom=None, hollow=0.0,
             jaw_angle=0.0, chin_fwd=0.0, brow=0.0):
    """The base head changed by zones: widths of the cranium, cheekbones, jaw and chin; depth; a longer or shorter
    face (face > 1 stretches the part below the eyes); hollow cheeks; a squarer jaw angle; a chin forward."""
    out = []
    for y, w, zf, zb, z0, nf in ADULT:
        k_cr = max(0, min(1, (-y - 0.02) / 0.15))
        k_ch = max(0, 1 - abs(y - 0.10) / 0.14)
        k_jw = max(0, 1 - abs(y - 0.38) / 0.10)
        k_cn = max(0, min(1, (y - 0.43) / 0.05))
        m = 1 + (cranium - 1) * k_cr + (cheek - 1) * k_ch + (jaw - 1) * k_jw + (chin - 1) * k_cn
        m -= hollow * max(0, 1 - abs(y - 0.27) / 0.08)
        yy = y * face if y > 0 else y
        zf2 = zf * depth + chin_fwd * k_cn + brow * max(0, 1 - abs(y + 0.08) / 0.06)
        nf2 = nf + jaw_angle * k_jw
        out.append((yy, w * m, zf2, zb * depth, z0, nf2))
    return out


def scale_y(tab, k, pivot=0.0):
    return [((y - pivot) * k + pivot,) + tuple(r) for y, *r in tab]


# ---------------------------------------------------------------- glasses

def glasses(shape='round', r=0.062, rh=None, bridge=0.03, dz=0.05, lift=0.0, thick=0.9, temple=True, low=0.0):
    """Glasses in front of the eyes: rims as 3D rings, a bridge, temples back to the ears."""
    rh = rh or r
    def draw(h, v, lw):
        E = h.p['eye']
        out = []
        rims = []
        for s in (-1, 1):
            cx, cy = s * E['x'], E['y'] + 0.01 + low - lift
            z = h.zsurf(cx, cy) + dz
            pts = []
            for i in range(36):
                a = 2 * math.pi * i / 36
                if shape == 'round':
                    dx, dy = r * math.cos(a), rh * math.sin(a)
                else:
                    c, sn = math.cos(a), math.sin(a)
                    dx = r * math.copysign(abs(c) ** 0.45, c)
                    dy = rh * math.copysign(abs(sn) ** 0.45, sn)
                pts.append((cx + dx, cy + dy, z - abs(dx) * 0.25 * s * (1 if dx * s > 0 else 0)))
            vis = v.facing((s * 0.5, 0, 0.85)) > -0.2
            P = v.many(pts)
            rims.append((P, vis, s, cx, cy, z))
        for P, vis, s, cx, cy, z in rims:
            if not vis:
                continue
            out.append(f'<path d="{poly(P)}" fill="{PAPER}" fill-opacity="0.0"/>')
            out.append(outline(P, lw * thick, 0.4, smooth=False))
            # a glint across the lens
            g0 = v((cx - r * 0.55, cy - rh * 0.1, z)); g1 = v((cx - r * 0.1, cy - rh * 0.6, z))
            out.append(stroke([g0, g1], lw * 0.35, taper=(0.4, 0.4)))
        # bridge
        a = rims[0]; b = rims[1]
        br = [(-E['x'] + r * 0.95, E['y'] + low - lift - 0.005, a[5]), (0, E['y'] - 0.015 + low - lift, a[5] + 0.015), (E['x'] - r * 0.95, E['y'] + low - lift - 0.005, b[5])]
        out.append(stroke(v.many(br), lw * thick * 0.9, taper=(0.1, 0.1)))
        if temple:
            for s in (-1, 1):
                if v.facing((s, 0, 0.15)) > 0.1:
                    w = h.sec(E['y'])[0]
                    tp = [(s * (E['x'] + r), E['y'] + low - lift - 0.01, h.zsurf(s * (E['x'] + r), E['y']) + dz * 0.8), (s * (w + 0.015), E['y'] - 0.01, 0.05), (s * (w + 0.01), E['y'] + 0.02, -0.12)]
                    out.append(stroke(v.many(tp), lw * thick * 0.8, taper=(0.05, 0.3)))
        return ''.join(out)
    return draw


# ---------------------------------------------------------------- marks on the face

def wrinkles(forehead=0, crows=0, naso=0, neck=0, under=0, seed=3):
    """Lines of age, drawn thin and broken (seinen artists draw few, exact ones)."""
    def draw(h, v, lw):
        rnd = random.Random(seed)
        out = []
        E = h.p['eye']
        for i in range(forehead):
            y = -0.20 - i * 0.035
            for s in (-1, 1):
                pts = [on(h, s * x, y + 0.006 * math.sin(x * 12 + i), 0.003) for x in [0.03, 0.08, 0.13, 0.18]]
                if v.facing((s * 0.4, -0.3, 0.8)) > 0:
                    out.append(stroke(v.many(pts), lw * 0.4, taper=(0.4, 0.4)))
        for s in (-1, 1):
            if v.facing((s * 0.8, 0, 0.5)) < 0.05:
                continue
            for i in range(crows):
                a = -0.4 + i * 0.4
                x0 = s * (E['x'] + E['w'] * 1.1)
                pts = [on(h, x0, E['y'] + a * 0.02), on(h, x0 + s * 0.035, E['y'] + a * 0.04)]
                out.append(stroke(v.many(pts), lw * 0.35, taper=(0.3, 0.5)))
            if naso:
                m = h.p['mouth']
                pts = [on(h, s * 0.065, 0.17), on(h, s * 0.10, 0.25), on(h, s * (m['w'] + 0.025), 0.33 + 0.02 * naso)]
                out.append(stroke(v.many(pts), [lw * 0.3, lw * 0.9, lw * 0.4], taper=(0.3, 0.5)))
            if under:
                pts = [on(h, s * (E['x'] - E['w'] * 0.6), E['y'] + 0.06), on(h, s * (E['x'] + E['w'] * 0.4), E['y'] + 0.075)]
                out.append(stroke(v.many(pts), lw * 0.35, taper=(0.4, 0.4)))
        return ''.join(out)
    return draw


def freckles(n=14, seed=4):
    def draw(h, v, lw):
        rnd = random.Random(seed)
        out = []
        for i in range(n):
            s = -1 if i % 2 else 1
            x = s * rnd.uniform(0.04, 0.2); y = rnd.uniform(0.07, 0.15)
            if v.facing((s * 0.6, 0, 0.8)) < 0.1:
                continue
            X, Y = v(on(h, x, y, 0.002))
            out.append(f'<circle cx="{f1(X)}" cy="{f1(Y)}" r="{f1(lw * rnd.uniform(0.35, 0.6))}" fill="{INK}"/>')
        return ''.join(out)
    return draw


def cheek_blush(amount=1.0, y=0.12, x=0.17):
    def draw(h, v, lw):
        out = []
        for s in (-1, 1):
            if v.facing((s * 0.6, 0, 0.8)) < 0.15:
                continue
            X, Y = v(on(h, s * x, y))
            out.append(blush(X, Y, w=v.s * 0.09 * amount, h=v.s * 0.04, n=5, lw=lw * 0.45, seed=5 + s))
        return ''.join(out)
    return draw


def plaster(x=0.0, y=0.07, w=0.07, hgt=0.025, ang=-15):
    """A sticking plaster (Тим)."""
    def draw(h, v, lw):
        a = math.radians(ang)
        pts = []
        for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            px = x + (dx * w * math.cos(a) - dy * hgt * math.sin(a))
            py = y + (dx * w * math.sin(a) + dy * hgt * math.cos(a))
            pts.append(on(h, px, py, 0.012 + 0.02 * (1 - abs(px) / 0.1)))
        P = v.many(pts)
        return fillpath(P, PAPER, smooth=False) + outline(P, lw * 0.6, 0.3, smooth=False) + \
            stroke(v.many([on(h, x - w * 0.3, y, 0.03), on(h, x + w * 0.3, y - 0.005, 0.03)]), lw * 0.3)
    return draw


# ---------------------------------------------------------------- beard and moustache

def beard(thick=0.035, cheek=0.16, seed=9, length=0.05):
    """A full black beard: the part of the face below the line of the cheeks and round the mouth, filled black, and
    the lower outline of the head grown outwards below the mouth (the beard's own thickness); white curls of light
    inside, a broken edge. Drawn under the eyes and the mouth, so a laughing mouth opens in it."""
    def draw(h, v, lw):
        rnd = random.Random(seed)
        m = h.p['mouth']; my = m['y'] + h.e.get('jaw', 0) * 0.02
        mw = m['w'] * (1 + 0.25 * h.e.get('mwide', 0) + 0.12 * h.e.get('smile', 0))
        w = lambda y: h.sec(y)[0]
        yb = h.bottom
        # the region on the face: sideburn - cheek line - over the lip - cheek line - sideburn - along the jaw
        ring = []
        for s in (-1, 1):
            side = [(s * w(0.03) * 0.99, 0.0), (s * w(0.08) * 0.93, cheek - 0.04), (s * (mw + 0.085), cheek + 0.05),
                    (s * (mw + 0.05), my - 0.03), (s * mw * 0.75, my - 0.07), (s * 0.03, my - 0.075)]
            ring.append(side)
        top = ring[0] + ring[1][::-1]
        bottom = []
        ys = [0.03 + (yb - 0.005 - 0.03) * (k / 10) ** 0.8 for k in range(11)]
        bottom = [(w(y) * 0.99, y) for y in ys] + [(-w(y) * 0.99, y) for y in ys[::-1]]
        halves = []
        for side, s in ((ring[0], -1), (ring[1], 1)):
            down = [(0.0, my + 0.06), (0.0, yb - 0.005)]
            jaw_ = [(s * w(y) * 0.99, y) for y in ys[::-1]]
            halves.append([v(on(h, x, y, 0.004)) for x, y in side + down + jaw_])
        P = halves[0] + halves[1]
        # the outer thickness: the head's silhouette grown, below the mouth
        tab = list(h.tab)
        yl = tab[-1][0]
        tab = tab[:-1] + [(yl - 0.005, tab[-1][1] + 0.06, tab[-1][2] + 0.01, tab[-1][3] - 0.05, tab[-1][4], 2.0),
                          (yl + length * 0.7, 0.10, tab[-1][2] - 0.02, tab[-1][3] - 0.02, tab[-1][4], 2.0),
                          (yl + length, 0.03, tab[-1][2] - 0.05, tab[-1][3], tab[-1][4], 2.0)]
        hb = Head(h.p, h.e); hb.tab = tab; hb.bottom = tab[-1][0]
        R, L = silhouette(hb, v, grow=thick, y0=0.06, y1=hb.bottom, extra=False, levels=34)
        R = [r for r in R if r[1][1] > my - 0.02 or True]
        G = [a for a, _ in R] + [a for a, _ in L[::-1]]
        # the grown outline only below the cheek line: clip it under the line of the cheeks
        cheekline = [v(on(h, x, y, 0.004)) for x, y in top]
        far = 5 * v.s
        below = cheekline + [(cheekline[-1][0], cheekline[-1][1] + far), (cheekline[0][0], cheekline[0][1] + far)]
        out = ''.join(fillpath(H, INK, smooth=False) for H in halves) + clip(below, fillpath(G, INK, smooth=False), smooth=False)
        # a broken edge: short strokes out of the outer contour
        edge = []
        for i in range(0, len(G), 2):
            x, y = G[i]
            cx = sum(p[0] for p in G) / len(G); cy = sum(p[1] for p in G) / len(G)
            dx, dy = x - cx, y - cy; d = math.hypot(dx, dy) or 1
            L2 = lw * rnd.uniform(1.5, 4)
            edge.append(stroke([(x - dx / d * L2, y - dy / d * L2), (x + dx / d * L2, y + dy / d * L2)], lw * 1.2, taper=(0.1, 0.7)))
        out += clip(below, ''.join(edge), smooth=False)
        # curls of light
        allp = P + G
        xs = [p[0] for p in allp]; ys = [p[1] for p in allp]
        cl = []
        for i in range(55):
            X = rnd.uniform(min(xs), max(xs)); Y = rnd.uniform(min(ys), max(ys))
            r = v.s * rnd.uniform(0.01, 0.018)
            a0 = rnd.uniform(0, 6.28)
            arc = [(X + r * math.cos(a0 + t), Y + r * math.sin(a0 + t) * 0.8) for t in [k * 0.5 for k in range(5)]]
            cl.append(stroke(arc, lw * rnd.uniform(0.35, 0.6), taper=(0.4, 0.4), fill=PAPER))
        cid = uid('bd')
        out += f'<clipPath id="{cid}"><path d="{poly(halves[0])}"/><path d="{poly(halves[1])}"/><path d="{poly(G)}"/></clipPath><g clip-path="url(#{cid})">{"".join(cl)}</g>'
        return out
    return draw


def moustache(w=0.11, y=None, droop=0.04, thick=0.035, style='bushy', seed=2, ink=False):
    """A moustache over the upper lip: white with an outline and hair lines (the old man), or black."""
    def draw(h, v, lw):
        m = h.p['mouth']; my = (m['y'] if y is None else y) + h.e.get('jaw', 0) * 0.02
        rnd = random.Random(seed)
        top, bot = [], []
        for i in range(13):
            u = -1 + 2 * i / 12
            x = u * w
            t = my - 0.045 + 0.012 * u * u - 0.008 * (1 - abs(u))
            b = my - 0.005 + droop * u * u + 0.004 * math.sin(u * 9)
            top.append(on(h, x, t, 0.035 * (1 - u * u) + 0.012))
            bot.append(on(h, x, b, 0.035 * (1 - u * u) + 0.012))
        keep = [v.facing((p[0] * 2.5, 0, 0.9)) > -0.1 for p in top]
        T = [v(p) for p, k in zip(top, keep) if k]; B = [v(p) for p, k in zip(bot, keep) if k]
        if len(T) < 3:
            return ''
        shp = T + B[::-1]
        out = fillpath(shp, INK if ink else PAPER, smooth=False)
        lines = []
        for i in range(16):
            u = rnd.uniform(0.05, 0.95)
            k = int(u * (len(T) - 1))
            a = lerp(T[k], B[k], 0.15); b = lerp(T[k], B[k], 0.95)
            b = (b[0] + (b[0] - T[len(T) // 2][0]) * 0.08, b[1])
            lines.append(stroke([a, b], lw * 0.4, taper=(0.4, 0.5), fill=PAPER if ink else INK))
        out += clip(shp, ''.join(lines), smooth=False)
        out += outline(shp, lw * 0.8, 0.5, smooth=False)
        return out
    return draw
