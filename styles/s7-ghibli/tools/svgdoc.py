"""The page an image is drawn on: layers of flat shapes, the cel drawing primitives (fill, one shadow tone, an
outline), painted watercolour-like backdrops, film grain, and rendering to PNG with headless Chrome."""
import os
import subprocess
import random
from geo import path_of, line_of, polys

INK = '#2e2320'          # the line: dark warm brown, never pure black
MODE = 'full'            # 'full'; 'flat' — colours without the shadow tone; 'line' — only the line (for the rules)


def mix(a, b, t):
    a, b = a.lstrip('#'), b.lstrip('#')
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02x}' for x, y in zip(ca, cb))


def shade(c, k=1.0):
    """the one shadow tone of a colour: as if multiplied by a soft warm lavender — Ghibli's cel shadow keeps the
    colour's warmth, it does not turn grey."""
    if MODE != 'full':
        return c
    c = c.lstrip('#')
    m = (0.86, 0.78, 0.84)
    v = [int(c[i:i + 2], 16) for i in (0, 2, 4)]
    return '#' + ''.join(f'{round(x * (1 - (1 - f) * k)):02x}' for x, f in zip(v, m))


class Doc:
    def __init__(self, w, h, lw=2.4):
        self.w, self.h, self.lw = w, h, lw
        self.defs, self.body = [], []
        self._n = 0

    def uid(self, p='i'):
        self._n += 1
        return f'{p}{self._n}'

    def add(self, s):
        self.body.append(s)

    # ---- cel primitives
    def fill(self, g, c, op=1.0):
        if MODE == 'line' and c != INK:
            c, op = '#fbf8f1', 1.0
        d = path_of(g)
        if d:
            o = f' opacity="{op}"' if op < 1 else ''
            self.add(f'<path d="{d}" fill="{c}" fill-rule="evenodd"{o}/>')

    def outline(self, g, w=None, c=INK):
        d = path_of(g)
        if d:
            self.add(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w or self.lw}" '
                     f'stroke-linejoin="round" stroke-linecap="round"/>')

    def line(self, pts, w=None, c=INK, op=1.0):
        d = line_of(pts)
        if d:
            o = f' opacity="{op}"' if op < 1 else ''
            self.add(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w or self.lw}" '
                     f'stroke-linejoin="round" stroke-linecap="round"{o}/>')

    def part(self, g, c, shadow=None, sc=None, line=True, w=None):
        """a flat shape: colour, then its shadow tone, then the line."""
        self.fill(g, c)
        if shadow is not None and not shadow.is_empty:
            self.fill(shadow.intersection(g), sc or shade(c))
        if line:
            self.outline(g, w)

    # ---- backdrops
    def rough(self, scale=0.012, amount=10, seed=1):
        """a filter that makes a painted edge: the shape wobbles a little, as gouache on paper."""
        i = self.uid('r')
        self.defs.append(
            f'<filter id="{i}" x="-10%" y="-10%" width="120%" height="120%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{scale}" numOctaves="3" seed="{seed}" result="n"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{amount}" xChannelSelector="R" yChannelSelector="G"/>'
            f'</filter>')
        return i

    def blur(self, r):
        i = self.uid('b')
        self.defs.append(f'<filter id="{i}" x="-50%" y="-50%" width="200%" height="200%">'
                         f'<feGaussianBlur stdDeviation="{r}"/></filter>')
        return i

    def mottle(self, freq=0.02, op=0.18, seed=3, w=None, h=None):
        """a broad uneven wash over everything painted below — watercolour pooling."""
        i = self.uid('m')
        self.defs.append(
            f'<filter id="{i}" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="4" seed="{seed}"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 0.5  0 0 0 0 0.45  0 0 0 0 0.4  1.2 0 0 0 -0.35"/>'
            f'</filter>')
        self.add(f'<rect width="{w or self.w}" height="{h or self.h}" filter="url(#{i})" opacity="{op}" '
                 f'style="mix-blend-mode:soft-light"/>')

    def grain(self, op=0.07):
        i = self.uid('g')
        self.defs.append(
            f'<filter id="{i}" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/>'
            f'<feColorMatrix type="saturate" values="0"/></filter>')
        self.add(f'<rect width="{self.w}" height="{self.h}" filter="url(#{i})" opacity="{op}" '
                 f'style="mix-blend-mode:overlay"/>')

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}"><defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>')

    def save(self, path):
        with open(path, 'w') as f:
            f.write(self.svg())


def render(svg_path, png_path, w, h):
    html = svg_path + '.html'
    with open(html, 'w') as f:
        f.write(f'<html><body style="margin:0;background:#fff"><img src="{os.path.basename(svg_path)}" '
                f'style="width:{w}px;height:{h}px;display:block"></body></html>')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    f'--window-size={w},{h}', f'--screenshot={os.path.abspath(png_path)}',
                    'file://' + os.path.abspath(html)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    os.remove(html)
