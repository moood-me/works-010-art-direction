"""Small kit for drawing in the Klaus manner in SVG.

A form is one flat shape (as in the film's colour pass) lit by a few layered tone shapes:
  - the whole shape filled with the rim colour,
  - the shadow colour: the shape moved a little toward the light (leaves a thin rim on the far edge),
  - the lit colour: the shape moved further toward the light, softly blurred (leaves the core shadow band),
then extra hand-drawn tone shapes (cast shadows, occlusion, highlights) clipped to the form.
"""
import math, os, subprocess

_uid = [0]


def uid(p='u'):
    _uid[0] += 1
    return f'{p}{_uid[0]}'


def mix(a, b, t):
    a, b = (x if len(x) == 7 else '#' + ''.join(c * 2 for c in x[1:]) for x in (a, b))
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02x}' for x, y in zip(a, b))


class Light:
    """Direction the light comes FROM (unit vector, screen coords), its warm colour and the cool shadow colour."""

    def __init__(self, dx=-0.75, dy=-0.65, key='#ffd9a0', shade='#3b2f5c', rim='#ffe6c0'):
        n = math.hypot(dx, dy)
        self.dx, self.dy = dx / n, dy / n
        self.key, self.shade, self.rim = key, shade, rim

    def colours(self, base, k=0.3, s=0.55, r=0.45):
        """lit, shadow, rim colours for a flat base colour."""
        return mix(base, self.key, k), mix(base, self.shade, s), mix(base, self.rim, r)


class Doc:
    def __init__(self, w, h, light=None):
        self.w, self.h = w, h
        self.light = light or Light()
        self.defs = []
        self.body = []
        self._blur = {}

    def blur(self, sd):
        if sd not in self._blur:
            i = uid('b')
            self.defs.append(f'<filter id="{i}" x="-30%" y="-30%" width="160%" height="160%">'
                             f'<feGaussianBlur stdDeviation="{sd}"/></filter>')
            self._blur[sd] = i
        return self._blur[sd]

    def add(self, s):
        self.body.append(s)

    def clip(self, d, transform=''):
        i = uid('c')
        t = f' transform="{transform}"' if transform else ''
        self.defs.append(f'<clipPath id="{i}"><path d="{d}"{t}/></clipPath>')
        return i

    def form(self, d, base, *, shift=10, rim=0, soft=3.5, extra='', k=0.3, s=0.55, r=0.45,
             light=None, line=None, lw=1.4, rimcol=None, rimop=0.9, out=None):
        """A volumetric form. shift: how far the lit area reaches toward the far edge (width of the core shadow);
        rim: width of the rim light on the far edge; extra: more SVG drawn inside the form's clip."""
        L = light or self.light
        lit, sh, rm = L.colours(base, k, s, r)
        if rimcol:
            rm = rimcol
        c = self.clip(d)
        b = self.blur(soft)
        ms, mr = uid('m'), uid('m')
        lx, ly = L.dx * shift, L.dy * shift
        ox, oy = L.dx * rim, L.dy * rim
        self.defs.append(f'<mask id="{ms}" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="6000" height="6000">'
                         f'<path d="{d}" fill="#fff"/><path d="{d}" fill="#000" '
                         f'transform="translate({lx:.1f},{ly:.1f})" filter="url(#{b})"/></mask>')
        self.defs.append(f'<mask id="{mr}" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="6000" height="6000">'
                         f'<path d="{d}" fill="#fff"/><path d="{d}" fill="#000" '
                         f'transform="translate({ox:.1f},{oy:.1f})"/></mask>')
        g = [f'<path d="{d}" fill="{lit}"/>',
             f'<g clip-path="url(#{c})">',
             f'<path d="{d}" fill="{sh}" mask="url(#{ms})"/>',
             extra,
             f'<path d="{d}" fill="{rm}" mask="url(#{mr})" opacity="{rimop}"/>' if rim else '',
             '</g>']
        if line:
            g.append(f'<path d="{d}" fill="none" stroke="{line}" stroke-width="{lw}" stroke-linejoin="round"/>')
        return '\n'.join(g)

    def tone(self, d, fill, op=1.0, soft=0, blend=None):
        f = f' filter="url(#{self.blur(soft)})"' if soft else ''
        m = f' style="mix-blend-mode:{blend}"' if blend else ''
        return f'<path d="{d}" fill="{fill}" opacity="{op}"{f}{m}/>'

    def grain(self, op=0.10):
        i = uid('g')
        self.defs.append(
            f'<filter id="{i}" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>'
            f'<feColorMatrix type="saturate" values="0"/>'
            f'<feComponentTransfer><feFuncA type="table" tableValues="0 {op}"/></feComponentTransfer>'
            f'</filter>')
        self.add(f'<rect width="{self.w}" height="{self.h}" filter="url(#{i})" style="mix-blend-mode:multiply"/>')

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">\n<defs>\n' + '\n'.join(self.defs) + '\n</defs>\n'
                + '\n'.join(self.body) + '\n</svg>\n')

    def save(self, path):
        with open(path, 'w') as f:
            f.write(self.svg())


def bg(doc, top, bottom, glow=None, gx=0.3, gy=0.3, gr=0.6):
    i = uid('lg')
    doc.defs.append(f'<linearGradient id="{i}" x1="0" y1="0" x2="0" y2="1">'
                    f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>')
    doc.add(f'<rect width="{doc.w}" height="{doc.h}" fill="url(#{i})"/>')
    if glow:
        j = uid('rg')
        doc.defs.append(f'<radialGradient id="{j}" cx="{gx}" cy="{gy}" r="{gr}">'
                        f'<stop offset="0" stop-color="{glow}" stop-opacity="0.75"/>'
                        f'<stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>')
        doc.add(f'<rect width="{doc.w}" height="{doc.h}" fill="url(#{j})"/>')


def render(svg_path, png_path, w, h, scale=1):
    """Render with headless Chrome (one process, light)."""
    html = svg_path + '.html'
    with open(html, 'w') as f:
        f.write(f'<html><body style="margin:0"><img src="{os.path.basename(svg_path)}" '
                f'style="width:{w}px;height:{h}px;display:block"></body></html>')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    f'--force-device-scale-factor={scale}', f'--window-size={w},{h}',
                    f'--screenshot={os.path.abspath(png_path)}', 'file://' + os.path.abspath(html)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    os.remove(html)
