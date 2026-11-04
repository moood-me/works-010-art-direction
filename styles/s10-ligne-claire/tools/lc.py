"""Ligne claire kit: SVG document, smooth paths through points, the one even line, flat colours, rendering.

Everything in the style is a closed shape with a flat fill and the same black contour, or an open black stroke.
Shapes are given as lists of points; `smooth` turns them into Catmull-Rom curves (corner points stay sharp).
"""
import os, subprocess, math

INK = '#1b1714'          # the line: near black, warm
LINE = 2.4               # contour width at portrait scale (head ~ 230 px tall); scale it with the drawing


class Doc:
    def __init__(self, w, h, bg='#f4ecd8'):
        self.w, self.h = w, h
        self.items = []
        self.defs = []
        self.bg = bg

    def add(self, *s):
        for x in s:
            if isinstance(x, (list, tuple)):
                self.add(*x)
            elif x:
                self.items.append(x)

    def svg(self):
        bg = f'<rect width="{self.w}" height="{self.h}" fill="{self.bg}"/>' if self.bg else ''
        defs = f'<defs>{"".join(self.defs)}</defs>' if self.defs else ''
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" stroke-linejoin="round" stroke-linecap="round">{defs}{bg}' + '\n'.join(self.items)
                + '</svg>')

    def save(self, path):
        with open(path, 'w') as f:
            f.write(self.svg())


def f2(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.') if abs(v) < 1e6 else str(v)


def smooth(pts, closed=True, corners=(), t=1.0):
    """Path data through points. corners: indices that stay sharp. t: tension (1 = Catmull-Rom)."""
    n = len(pts)
    if n < 2:
        return ''
    if n == 2:
        return f'M{f2(pts[0][0])},{f2(pts[0][1])}L{f2(pts[1][0])},{f2(pts[1][1])}'
    corners = set(i % n for i in corners)
    d = [f'M{f2(pts[0][0])},{f2(pts[0][1])}']
    segs = n if closed else n - 1
    for i in range(segs):
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        if i in corners:
            p0 = p1
        if (i + 1) % n in corners:
            p3 = p2
        k = t / 6
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        d.append(f'C{f2(c1[0])},{f2(c1[1])} {f2(c2[0])},{f2(c2[1])} {f2(p2[0])},{f2(p2[1])}')
    if closed:
        d.append('Z')
    return ''.join(d)


def shape(pts, fill, w=LINE, corners=(), stroke=INK, extra=''):
    """A closed flat shape with the contour."""
    s = f' stroke="{stroke}" stroke-width="{f2(w)}"' if w else ''
    return f'<path d="{smooth(pts, True, corners)}" fill="{fill}"{s}{extra}/>'


def line(pts, w=LINE, corners=(), stroke=INK, extra=''):
    """An open stroke (a fold, a crease, a lock of hair)."""
    return f'<path d="{smooth(pts, False, corners)}" fill="none" stroke="{stroke}" stroke-width="{f2(w)}"{extra}/>'


def poly(pts, fill, w=LINE, stroke=INK):
    d = 'M' + 'L'.join(f'{f2(x)},{f2(y)}' for x, y in pts) + 'Z'
    s = f' stroke="{stroke}" stroke-width="{f2(w)}"' if w else ''
    return f'<path d="{d}" fill="{fill}"{s}/>'


def ellipse(cx, cy, rx, ry, fill, w=LINE, rot=0, stroke=INK):
    tr = f' transform="rotate({f2(rot)} {f2(cx)} {f2(cy)})"' if rot else ''
    s = f' stroke="{stroke}" stroke-width="{f2(w)}"' if w else ''
    return f'<ellipse cx="{f2(cx)}" cy="{f2(cy)}" rx="{f2(rx)}" ry="{f2(ry)}" fill="{fill}"{s}{tr}/>'


def dot(x, y, r, fill=INK):
    return f'<circle cx="{f2(x)}" cy="{f2(y)}" r="{f2(r)}" fill="{fill}"/>'


def group(items, tx=0, ty=0, s=1, rot=0, flip=False):
    tr = f'translate({f2(tx)},{f2(ty)})'
    if rot:
        tr += f' rotate({f2(rot)})'
    if s != 1 or flip:
        tr += f' scale({f2(-s if flip else s)},{f2(s)})'
    return f'<g transform="{tr}">' + ''.join(flat(items)) + '</g>'


def flat(items):
    out = []
    for x in items:
        if isinstance(x, (list, tuple)):
            out += flat(x)
        elif x:
            out.append(x)
    return out


def xf(pts, tx=0, ty=0, s=1, rot=0, flip=False):
    """Transform points (rotate by rot degrees about origin, scale, mirror, translate)."""
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for x, y in pts:
        x2, y2 = x * c - y * si, x * si + y * c
        out.append(((-x2 if flip else x2) * s + tx, y2 * s + ty))
    return out


def mix(a, b, t):
    a, b = a.lstrip('#'), b.lstrip('#')
    c = [round(int(a[i:i + 2], 16) * (1 - t) + int(b[i:i + 2], 16) * t) for i in (0, 2, 4)]
    return '#' + ''.join(f'{v:02x}' for v in c)


def text(x, y, s, size=18, fill=INK, anchor='middle', weight='bold'):
    return (f'<text x="{f2(x)}" y="{f2(y)}" font-family="Futura, \'Century Gothic\', \'DejaVu Sans\', sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" '
            f'letter-spacing="1">{s}</text>')


def render(svg_path, png_path, w, h, scale=1):
    """Render with headless Chrome."""
    html = svg_path + '.html'
    with open(html, 'w') as f:
        f.write(f'<html><body style="margin:0"><img src="{os.path.basename(svg_path)}" '
                f'style="width:{w}px;height:{h}px;display:block"></body></html>')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    f'--force-device-scale-factor={scale}', f'--window-size={w},{h}',
                    f'--screenshot={os.path.abspath(png_path)}', 'file://' + os.path.abspath(html)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    os.remove(html)
