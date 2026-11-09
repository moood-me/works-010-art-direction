"""Mid-century gouache kit: flat shapes with painted edges, tapered brush lines, paper and print texture.

Everything a character is made of goes through three calls:
  shape(pts, fill)      — a flat gouache shape; pts are (x, y) or (x, y, 'c') for a sharp corner
  brush(pts, w, ink)    — a tapered brush line along a centre line
  dots / blush          — round marks
Doc collects the SVG, keeps the shared filters, and adds paper at the end.
"""
import math, os, subprocess

# ---------- colour ----------

def hx(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return '#%02x%02x%02x' % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


INK = '#2a201c'        # the dark brush colour (never pure black: gouache lamp-black on warm paper)
PAPER = '#f3ead6'      # cream board

# ---------- geometry ----------

def _p(q):
    return q[0], q[1]


def _corner(q):
    return len(q) > 2 and q[2] == 'c'


def path(pts, closed=True, tension=1.0):
    """Catmull-Rom through the points as cubic Béziers; points marked 'c' are sharp corners."""
    n = len(pts)
    if n < 2:
        return ''
    P = [_p(q) for q in pts]
    out = ['M%.1f,%.1f' % P[0]]
    segs = n if closed else n - 1
    for i in range(segs):
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[i]
        p1, p2 = P[i], P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else P[(i + 1) % n]
        k = tension / 6
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        if _corner(pts[i]):
            c1 = (p1[0] + (p2[0] - p1[0]) * 0.3, p1[1] + (p2[1] - p1[1]) * 0.3)
        if _corner(pts[(i + 1) % n]):
            c2 = (p2[0] + (p1[0] - p2[0]) * 0.3, p2[1] + (p1[1] - p2[1]) * 0.3)
        out.append('C%.1f,%.1f %.1f,%.1f %.1f,%.1f' % (c1 + c2 + p2))
    if closed:
        out.append('Z')
    return ''.join(out)


def sample(pts, closed=False, per=10):
    """Points along the Catmull-Rom curve (used for brush lines)."""
    P = [_p(q) for q in pts]
    n = len(P)
    res = []
    segs = n if closed else n - 1
    for i in range(segs):
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[i]
        p1, p2 = P[i], P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else P[(i + 1) % n]
        for s in range(per):
            t = s / per
            t2, t3 = t * t, t * t * t
            res.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    res.append(P[0] if closed else P[-1])
    return res









# ---------- marks ----------

def shape(pts, fill, opacity=None, extra=''):
    op = f' opacity="{opacity}"' if opacity is not None else ''
    return f'<path d="{path(pts)}" fill="{fill}"{op}{extra}/>'


def brush(pts, w, color=INK, taper=(0.25, 0.35), per=8, opacity=None, closed=False):
    """A tapered brush line: thick in the middle, thin at the ends (taper = share of length that thins at each end)."""
    c = sample(pts, closed=closed, per=per)
    L = [0.0]
    for i in range(1, len(c)):
        L.append(L[-1] + math.dist(c[i - 1], c[i]))
    tot = L[-1] or 1
    left, right = [], []
    for i, p in enumerate(c):
        t = L[i] / tot
        a, b = taper
        k = 1.0
        if a > 0 and t < a:
            k = 0.18 + 0.82 * math.sin(t / a * math.pi / 2)
        if b > 0 and t > 1 - b:
            k = min(k, 0.12 + 0.88 * math.sin((1 - t) / b * math.pi / 2))
        q0 = c[max(i - 1, 0)]
        q1 = c[min(i + 1, len(c) - 1)]
        dx, dy = q1[0] - q0[0], q1[1] - q0[1]
        dl = math.hypot(dx, dy) or 1
        nx, ny = -dy / dl, dx / dl
        hw = w * k / 2
        left.append((p[0] + nx * hw, p[1] + ny * hw))
        right.append((p[0] - nx * hw, p[1] - ny * hw))
    poly = left + right[::-1]
    d = 'M' + ' L'.join('%.1f,%.1f' % q for q in poly) + 'Z'
    op = f' opacity="{opacity}"' if opacity is not None else ''
    return f'<path d="{d}" fill="{color}"{op}/>'


def circle(cx, cy, r, fill, opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ''
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"{op}/>'


def ell(cx, cy, rx, ry, fill, rot=0, opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" transform="rotate({rot} {cx:.1f} {cy:.1f})" fill="{fill}"{op}/>'


def blush(cx, cy, r, color='#e8746a', opacity=0.7):
    """Blair's cheek: a round soft pink patch."""
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}" opacity="{opacity}" filter="url(#soft)"/>'


def dryb(pts_list, w, color, opacity=0.35):
    """Dry-brush strokes inside a mass (hair, cloth): a few thin tapered lines."""
    return ''.join(brush(p, w, color, taper=(0.3, 0.5), opacity=opacity) for p in pts_list)


def pattern_dots(clip_pts, x0, y0, x1, y1, step, r, color, cid, offset=True):
    """Little printed dots across a shape (a dress fabric)."""
    s = [f'<clipPath id="{cid}"><path d="{path(clip_pts)}"/></clipPath><g clip-path="url(#{cid})">']
    j = 0
    y = y0
    while y < y1:
        x = x0 + (step / 2 if (offset and j % 2) else 0)
        while x < x1:
            s.append(circle(x, y, r, color))
            x += step
        y += step * 0.87
        j += 1
    s.append('</g>')
    return ''.join(s)


def stripes(clip_pts, x0, y0, x1, y1, step, width, color, cid, angle=0):
    s = [f'<clipPath id="{cid}"><path d="{path(clip_pts)}"/></clipPath><g clip-path="url(#{cid})">'
         f'<g transform="rotate({angle} {(x0 + x1) / 2:.0f} {(y0 + y1) / 2:.0f})">']
    y = y0
    while y < y1:
        s.append(f'<rect x="{x0 - 200}" y="{y:.1f}" width="{x1 - x0 + 400}" height="{width}" fill="{color}"/>')
        y += step
    s.append('</g></g>')
    return ''.join(s)


def g(items, tf='', filt=None):
    f = f' filter="url(#{filt})"' if filt else ''
    t = f' transform="{tf}"' if tf else ''
    return f'<g{t}{f}>' + ''.join(items) + '</g>'

# ---------- document ----------

FILTERS = '''
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>
<filter id="gouache" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="2" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="2.4" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.018 0.045" numOctaves="3" seed="11" result="m"/>
  <feColorMatrix in="m" type="matrix" values="0.45 0 0 0 0.275  0.45 0 0 0 0.275  0.45 0 0 0 0.275  0 0 0 0 1" result="mg"/>
  <feBlend in="mg" in2="d" mode="soft-light" result="mb"/>
  <feComposite in="mb" in2="d" operator="in" result="mls"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="1" seed="3" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0.16  0 0 0 0 0.12  0 0 0 0 0.1  0 0 0 -4 1.3" result="gd"/>
  <feComposite in="gd" in2="d" operator="in" result="gds"/>
  <feMerge><feMergeNode in="mls"/><feMergeNode in="gds"/></feMerge>
</filter>
<filter id="board" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.02 0.035" numOctaves="3" seed="5" result="m"/>
  <feColorMatrix in="m" type="matrix" values="0.28 0 0 0 0.36  0.28 0 0 0 0.36  0.28 0 0 0 0.36  0 0 0 0 1" result="mg"/>
  <feBlend in="mg" in2="SourceGraphic" mode="soft-light" result="mb"/>
  <feComposite in="mb" in2="SourceGraphic" operator="in"/>
</filter>
<filter id="paper" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" seed="21" result="t"/>
  <feColorMatrix in="t" type="matrix" values="0 0 0 0 0.3  0 0 0 0 0.24  0 0 0 0 0.18  0 0 0 -2.5 1.25"/>
</filter>
'''


class Doc:
    def __init__(self, w, h, paper=PAPER, texture=True):
        self.w, self.h = w, h
        self.texture = texture
        self.parts = [f'<rect width="{w}" height="{h}" fill="{paper}"/>']
        self.defs = []

    def add(self, *s):
        self.parts.extend(s)

    def svg(self):
        paper = f'<rect width="{self.w}" height="{self.h}" filter="url(#paper)" opacity="0.35"/>' if self.texture else ''
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">'
                f'<defs>{FILTERS}{"".join(self.defs)}</defs>' + ''.join(self.parts) + paper + '</svg>')

    def save(self, p):
        with open(p, 'w') as f:
            f.write(self.svg())


def render(svg_path, png_path, w, h, scale=1):
    """Render with headless Chrome (one light process)."""
    html = svg_path + '.html'
    with open(html, 'w') as f:
        f.write(f'<html><body style="margin:0"><img src="{os.path.basename(svg_path)}" '
                f'style="width:{w}px;height:{h}px;display:block"></body></html>')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    f'--force-device-scale-factor={scale}', f'--window-size={w},{h}',
                    f'--screenshot={os.path.abspath(png_path)}', 'file://' + os.path.abspath(html)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    os.remove(html)


def limb(pts, ws, fill, per=8, cap=True):
    """A limb or any tube: centre line pts with a width at each point (linearly between them).
    cap=True: ends cut by an inward half-circle (they sit under a hand or a sleeve); cap='round': ends rounded outward."""
    c = sample(pts, per=per)
    n = len(pts)
    W = []
    for i in range(len(c)):
        u = min(i / per, n - 1.0001)
        k = int(u)
        W.append(ws[k] + (ws[min(k + 1, n - 1)] - ws[k]) * (u - k))
    left, right = [], []
    for i, p in enumerate(c):
        q0, q1 = c[max(i - 1, 0)], c[min(i + 1, len(c) - 1)]
        dx, dy = q1[0] - q0[0], q1[1] - q0[1]
        dl = math.hypot(dx, dy) or 1
        nx, ny = -dy / dl, dx / dl
        left.append((p[0] + nx * W[i] / 2, p[1] + ny * W[i] / 2))
        right.append((p[0] - nx * W[i] / 2, p[1] - ny * W[i] / 2))
    sw = 0 if cap == 'round' else 1     # cap=True bites a half-circle into each end; cap='round' rounds the end outward
    d = 'M' + ' L'.join('%.1f,%.1f' % q for q in left)
    if cap:
        d += ' A%.1f,%.1f 0 0 %d %.1f,%.1f' % (W[-1] / 2, W[-1] / 2, sw, *right[-1])
    d += ' L' + ' L'.join('%.1f,%.1f' % q for q in right[::-1])
    if cap:
        d += ' A%.1f,%.1f 0 0 %d %.1f,%.1f' % (W[0] / 2, W[0] / 2, sw, *left[0])
    return f'<path d="{d}Z" fill="{fill}"/>'


def edge(pts, i0, i1, w=2.2, color=INK, dx=1.6, dy=1.2, opacity=0.85):
    """Part of a shape's contour in ink, a little off the fill (the print's misregistration): the Šašek line."""
    seg = [(q[0] + dx, q[1] + dy) for q in pts[i0:i1 + 1]]
    return brush(seg, w, color, taper=(0.3, 0.3), opacity=opacity)


def hand(x, y, s=1.0, rot=0, fill='#f0c8a8', line=None, kind='open', side=1):
    """A hand as a few flat shapes, not a mitten: wrist at (x, y), fingers toward +y before `rot` (degrees);
    side=+1 puts the thumb on -x. kind: open (fingers spread) | fist (knuckles, thumb across) | curl (relaxed)."""
    o = []
    t = side
    if kind == 'open':
        for dx, ang, ln in ((-6.5, -20, 12), (-2.2, -7, 14.5), (2.2, 6, 13.5), (6.2, 19, 10.5)):
            a = math.radians(ang) * t
            x0, y0 = dx * s * t, 15 * s
            o.append(limb([(x0, y0), (x0 + math.sin(a) * ln * s, y0 + math.cos(a) * ln * s)], [5.2 * s, 4.0 * s], fill, cap='round'))
        o.append(limb([(-7 * s * t, 6 * s), (-15 * s * t, 9 * s), (-19 * s * t, 17 * s)], [6.5 * s, 5.5 * s, 4.2 * s], fill, cap='round'))
        o.append(ell(0, 10 * s, 9.5 * s, 10.5 * s, fill))
    elif kind == 'fist':
        o.append(ell(0, 10 * s, 11 * s, 10 * s, fill))
        o.append(limb([(-8 * s * t, 5 * s), (-11 * s * t, 13 * s), (-4 * s * t, 17 * s)], [6.5 * s, 6 * s, 5 * s], fill, cap='round'))
        if line:
            for dx in (-1.5, 3, 7):
                o.append(brush([(dx * s * t, 13 * s), (dx * s * t + 0.6 * s, 19 * s)], 1.5 * s, line, taper=(0.2, 0.5)))
            o.append(brush([(-10 * s * t, 6 * s), (-11.5 * s * t, 13 * s), (-5 * s * t, 17.5 * s)], 1.4 * s, line, taper=(0.3, 0.3)))
    elif kind == 'curl':
        for dx, ln in ((-5, 9), (-1, 11), (3, 10.5), (6.5, 8)):
            x0 = dx * s * t
            o.append(limb([(x0, 14 * s), (x0 + 1.5 * s * t, 14 * s + ln * s * 0.7), (x0 - 1.5 * s * t, 14 * s + ln * s)],
                          [4.8 * s, 4.4 * s, 3.6 * s], fill))
        o.append(limb([(-6 * s * t, 6 * s), (-11 * s * t, 13 * s), (-9 * s * t, 20 * s)], [6 * s, 5 * s, 4 * s], fill, cap='round'))
        o.append(ell(0, 9 * s, 8.5 * s, 9.5 * s, fill))
    else:
        raise ValueError(kind)
    return f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot})">' + ''.join(o) + '</g>'
