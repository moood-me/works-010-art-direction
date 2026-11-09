"""С15 «Нуар: чёрное пятно» — the kit: paths with hard and soft corners, a form lit from one side
(the black shape is what is left when the lit copy of the form is moved towards the light), pictures."""
import itertools, math

BLACK = '#07070b'
NIGHT = '#11121b'
RIM = '#3b4566'     # the thin edge of back light that parts black from black (None: no rim)
_uid = itertools.count()


def uid(p='c'):
    return f'{p}{next(_uid)}'


def d(pts, closed=True):
    """Path through points. A point is (x, y) — a hard corner — or (x, y, 's') — the line passes smoothly."""
    n = len(pts)
    if n < 2:
        return ''
    def tan(i):
        if len(pts[i]) < 3:
            return (0.0, 0.0)
        if not closed and (i == 0 or i == n - 1):
            return (0.0, 0.0)
        a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        return ((b[0] - a[0]) / 6.0, (b[1] - a[1]) / 6.0)
    out = [f'M{pts[0][0]:.1f} {pts[0][1]:.1f}']
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        p, q = pts[i], pts[j]
        t0, t1 = tan(i), tan(j)
        if t0 == (0, 0) and t1 == (0, 0):
            out.append(f'L{q[0]:.1f} {q[1]:.1f}')
        else:
            out.append(f'C{p[0]+t0[0]:.1f} {p[1]+t0[1]:.1f} {q[0]-t1[0]:.1f} {q[1]-t1[1]:.1f} {q[0]:.1f} {q[1]:.1f}')
    return ' '.join(out) + ('Z' if closed else '')


def shape(pts, fill, extra=''):
    return f'<path d="{d(pts)}" fill="{fill}" {extra}/>'


def line(pts, col=BLACK, w=2, extra=''):
    return (f'<path d="{d(pts, False)}" fill="none" stroke="{col}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="miter" {extra}/>')


def wedge(a, b, w0, w1, fill=BLACK, bend=0.0):
    """A stroke with pressure: a tapered band from a (width w0) to b (width w1), bent sideways by `bend`."""
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    mx, my = (ax + bx) / 2 + nx * bend, (ay + by) / 2 + ny * bend
    wm = (w0 + w1) / 2
    pts = [(ax + nx * w0 / 2, ay + ny * w0 / 2), (mx + nx * wm / 2, my + ny * wm / 2, 's'),
           (bx + nx * w1 / 2, by + ny * w1 / 2), (bx - nx * w1 / 2, by - ny * w1 / 2),
           (mx - nx * wm / 2, my - ny * wm / 2, 's'), (ax - nx * w0 / 2, ay - ny * w0 / 2)]
    return shape(pts, fill)


def form(pts, fill, lit=(-6, -3), shadows=(), lights=(), rim='auto', rimw=2.0, under=()):
    """A form lit from one side.
    The form is black; its lit copy, moved by `lit` towards the light and cut by the form, is the colour:
    what the copy doesn't cover is the black shadow that follows the form's own edge.
    shadows: more black shapes on the form (point lists) — the planes turned from the light, cast shadows;
    lights: (pts, fill) shapes over the black — light let back in; under: (pts, fill) colour patches under the black;
    rim: colour of a thin edge of back light on the dark side."""
    if rim == 'auto':
        rim = RIM
    c = uid()
    path = d(pts)
    s = [f'<clipPath id="{c}"><path d="{path}"/></clipPath>']
    s.append(f'<path d="{path}" fill="{rim or BLACK}"/>')
    s.append(f'<g clip-path="url(#{c})">')
    if rim:
        s.append(f'<path d="{path}" fill="{BLACK}" transform="translate({-rimw},{-rimw * 0.3})"/>')
    if lit is None:
        s.append(f'<path d="{path}" fill="{fill}"/>')
    else:
        s.append(f'<path d="{path}" fill="{fill}" transform="translate({lit[0]},{lit[1]})"/>')
    for q, f in under:
        s.append(shape(q, f))
    if rim and shadows:
        c2 = uid()
        s.append(f'<clipPath id="{c2}"><path d="{path}" transform="translate({-rimw},{-rimw * 0.3})"/></clipPath>')
        s.append(f'<g clip-path="url(#{c2})">' + ''.join(shape(q, BLACK) for q in shadows) + '</g>')
    else:
        for q in shadows:
            s.append(shape(q, BLACK))
    for q, f in lights:
        s.append(shape(q, f))
    s.append('</g>')
    return ''.join(s)


def clip(pts, inner):
    c = uid()
    return f'<clipPath id="{c}"><path d="{d(pts)}"/></clipPath><g clip-path="url(#{c})">{inner}</g>'


def g(inner, x=0, y=0, s=1, flip=False, rot=0, extra=''):
    sx = -s if flip else s
    t = f'translate({x:.1f},{y:.1f})'
    if rot:
        t += f' rotate({rot})'
    t += f' scale({sx:.4f},{s:.4f})'
    return f'<g transform="{t}" {extra}>{inner}</g>'


def limb(pts, widths, fill, **kw):
    """A sleeve, a leg: a band along joints `pts` with the widths at each; hard corners at the joints."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            a = math.atan2(pts[i + 1][1] - y, pts[i + 1][0] - x); b = math.atan2(y - pts[i - 1][1], x - pts[i - 1][0])
            dx, dy = math.cos(a) + math.cos(b), math.sin(a) + math.sin(b)
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths[i] / 2
        left.append((x + nx * w, y + ny * w)); right.append((x - nx * w, y - ny * w))
    return form(left + right[::-1], fill, **kw)


def svg(w, h, inner, bg=NIGHT):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>{inner}</svg>')


def text(x, y, s, size=22, fill='#8d8a80', anchor='middle'):
    return (f'<text x="{x}" y="{y}" font-family="Georgia, serif" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="2">{s}</text>')
