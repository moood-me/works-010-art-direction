"""The material kit: a document, colours, and the filters that make flat SVG shapes look like small sculpted
objects under real light — resin and clay faces, sculpted hair, fabric, knit, wood.

Two ways to give a shape volume:
- `form`   — for big shapes (a head, a coat): shadow = the shape moved toward the light and blurred, the uncovered side
             goes to shadow colour; a darker band of occlusion along the edges; a soft sheen spot toward the light;
             a thin cool rim on the side away from the key. Smooth at any size.
- `relief` — for small parts (nose, lids, brows, lips, fingers, locks of hair): the shape's blurred alpha is a height
             map lit by the key light with feDiffuseLighting / feSpecularLighting, like a real bump of clay.
             A negative height makes a groove (wrinkles, seams, folds).
Textures (`tex`) lay a fine noise or weave over a shape: clay fingerprints, felt, woven cloth, knit.
"""
import math, os, subprocess

# key light from the upper left (SVG azimuth, degrees clockwise from +x in y-down space), rim from the right behind
KEY_AZ, KEY_EL = 220, 48
LX, LY = math.cos(math.radians(KEY_AZ)), math.sin(math.radians(KEY_AZ))   # unit vector toward the key light


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(round(v)))) for v in c)


def mix(a, b, t):
    a, b = hex2rgb(a), hex2rgb(b)
    return rgb2hex([a[i] + (b[i] - a[i]) * t for i in range(3)])


def f(v):
    return ('%.4f' % v).rstrip('0').rstrip('.')


def pts(points, close=True):
    """Smooth closed (or open) path through points (Catmull-Rom → cubic Bézier)."""
    n = len(points)
    if n < 3:
        return 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in points)
    out = [f'M{f(points[0][0])} {f(points[0][1])}']
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = points[(i - 1) % n] if (close or i > 0) else points[0]
        p1 = points[i]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n] if (close or i + 2 < n) else points[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f'C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}')
    if close:
        out.append('Z')
    return ' '.join(out)


def poly(points):
    return 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in points) + ' Z'


class Doc:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.defs, self.keys, self.body = [], {}, []
        self.n = 0

    def uid(self, p='i'):
        self.n += 1
        return f'{p}{self.n}'

    def add(self, s):
        self.body.append(s)

    def define(self, key, make):
        """Define something once per key; make(id) returns its XML."""
        if key not in self.keys:
            i = 'd%d' % len(self.keys)
            self.keys[key] = i
            self.defs.append(make(i))
        return self.keys[key]

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                f'<defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>')

    def save(self, path):
        with open(path, 'w') as fh:
            fh.write(self.svg())

    # ---------- filters ----------

    def form(self, size, shade='#3a2440', depth=0.55, ao=0.35, sheen=0.22, rim=0.25, rim_col='#9fc4ff'):
        """Volume for a big shape of about `size` px across (see module doc)."""
        size = max(8, round(size / 4) * 4)
        key = ('form', size, shade, depth, ao, sheen, rim, rim_col)

        def make(i):
            d, b = size * 0.32, size * 0.17
            e = size * 0.05
            hb = size * 0.22
            rw = max(1.5, size * 0.018)
            return (f'<filter id="{i}" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">'
                    f'<feOffset in="SourceAlpha" dx="{f(LX*d)}" dy="{f(LY*d)}" result="o"/>'
                    f'<feGaussianBlur in="o" stdDeviation="{f(b)}" result="ob"/>'
                    f'<feComposite in="SourceAlpha" in2="ob" operator="out" result="sh"/>'
                    f'<feFlood flood-color="{shade}" flood-opacity="{depth}"/>'
                    f'<feComposite in2="sh" operator="in" result="shc"/>'
                    f'<feGaussianBlur in="SourceAlpha" stdDeviation="{f(e)}" result="eb"/>'
                    f'<feComposite in="SourceAlpha" in2="eb" operator="out" result="ao"/>'
                    f'<feFlood flood-color="{shade}" flood-opacity="{ao}"/>'
                    f'<feComposite in2="ao" operator="in" result="aoc"/>'
                    f'<feGaussianBlur in="SourceAlpha" stdDeviation="{f(hb)}" result="hb"/>'
                    f'<feOffset in="hb" dx="{f(LX*size*0.16)}" dy="{f(LY*size*0.16)}" result="hbo"/>'
                    f'<feComponentTransfer in="hbo" result="hl"><feFuncA type="table" tableValues="0 0 0 0 0.15 0.55 1"/></feComponentTransfer>'
                    f'<feComposite in="hl" in2="SourceAlpha" operator="in" result="hl2"/>'
                    f'<feFlood flood-color="#fff4e4" flood-opacity="{sheen}"/>'
                    f'<feComposite in2="hl2" operator="in" result="hlc"/>'
                    f'<feOffset in="SourceAlpha" dx="{f(-rw*1.2)}" dy="{f(rw*0.4)}" result="ro"/>'
                    f'<feGaussianBlur in="ro" stdDeviation="{f(rw*0.5)}" result="rob"/>'
                    f'<feComposite in="SourceAlpha" in2="rob" operator="out" result="rim"/>'
                    f'<feFlood flood-color="{rim_col}" flood-opacity="{rim}"/>'
                    f'<feComposite in2="rim" operator="in" result="rimc"/>'
                    f'<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shc"/><feMergeNode in="aoc"/>'
                    f'<feMergeNode in="hlc"/><feMergeNode in="rimc"/></feMerge></filter>')
        return self.define(key, make)

    def relief(self, soft=4, height=8, spec=0.45, shine=22, dim=1.0):
        """A small part lit as a bump of material. soft = blur (px), height = surface scale (negative = groove)."""
        soft, height = round(soft, 1), round(height, 1)
        key = ('relief', soft, height, spec, shine, dim)

        def make(i):
            dc = dim / math.sin(math.radians(KEY_EL))
            s = (f'<feSpecularLighting in="h" surfaceScale="{height}" specularConstant="{spec}" specularExponent="{shine}" '
                 f'lighting-color="#fff3e2" result="s"><feDistantLight azimuth="{KEY_AZ}" elevation="{KEY_EL}"/></feSpecularLighting>'
                 f'<feComposite in="s" in2="SourceAlpha" operator="in" result="s2"/>') if spec > 0 else ''
            out = ('<feComposite in="m2" in2="s2" operator="arithmetic" k2="1" k3="1"/>' if spec > 0 else '')
            return (f'<filter id="{i}" filterUnits="userSpaceOnUse" x="0" y="0" width="{self.w}" height="{self.h}" '
                    f'color-interpolation-filters="sRGB">'
                    f'<feGaussianBlur in="SourceAlpha" stdDeviation="{soft}" result="h"/>'
                    f'<feDiffuseLighting in="h" surfaceScale="{height}" diffuseConstant="{f(dc)}" lighting-color="#ffffff" result="d">'
                    f'<feDistantLight azimuth="{KEY_AZ}" elevation="{KEY_EL}"/></feDiffuseLighting>'
                    f'<feBlend in="SourceGraphic" in2="d" mode="multiply" result="m"/>'
                    f'<feComposite in="m" in2="SourceAlpha" operator="in" result="m2"/>{s}{out}</filter>')
        return self.define(key, make)

    def blur(self, sd):
        sd = round(sd, 1)
        return self.define(('blur', sd), lambda i: f'<filter id="{i}" filterUnits="userSpaceOnUse" x="0" y="0" '
                           f'width="{self.w}" height="{self.h}">'
                           f'<feGaussianBlur stdDeviation="{sd}"/></filter>')

    def tex(self, kind, scale=1.0, amount=0.25, seed=2):
        """A texture filter applied to a shape painted in its colour: kind clay | cloth | felt | knit | wood | skin."""
        key = ('tex', kind, scale, amount, seed)

        def make(i):
            if kind == 'clay':
                fr, oc, sx = 0.035 / scale, 3, 1
            elif kind == 'skin':
                fr, oc, sx = 0.5 / scale, 2, 1
            elif kind == 'cloth':
                fr, oc, sx = 0.9 / scale, 2, 1
            elif kind == 'felt':
                fr, oc, sx = 0.35 / scale, 3, 1
            elif kind == 'wood':
                fr, oc, sx = 0.02 / scale, 3, 12
            else:  # knit
                fr, oc, sx = 0.25 / scale, 2, 0.4
            bf = f'{f(fr)} {f(fr*sx)}' if sx != 1 else f(fr)
            return (f'<filter id="{i}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
                    f'<feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="{oc}" seed="{seed}" result="n"/>'
                    f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1.6 0 0 0 -0.62" result="dark"/>'
                    f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 0.96  0 0 0 0 0.9  -1.6 0 0 0 0.86" result="lite"/>'
                    f'<feComponentTransfer in="dark" result="d2"><feFuncA type="linear" slope="{amount}"/></feComponentTransfer>'
                    f'<feComponentTransfer in="lite" result="l2"><feFuncA type="linear" slope="{amount*0.7}"/></feComponentTransfer>'
                    f'<feMerge result="t"><feMergeNode in="d2"/><feMergeNode in="l2"/></feMerge>'
                    f'<feComposite in="t" in2="SourceAlpha" operator="in"/></filter>')
        return self.define(key, make)

    def lin(self, stops, x1=0, y1=0, x2=0, y2=1, units='objectBoundingBox'):
        key = ('lin', tuple(stops), x1, y1, x2, y2, units)
        return self.define(key, lambda i: f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" gradientUnits="{units}">'
                           + ''.join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
                           + '</linearGradient>')

    def rad(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None, units='objectBoundingBox'):
        fx = cx if fx is None else fx
        fy = cy if fy is None else fy
        key = ('rad', tuple(stops), cx, cy, r, fx, fy, units)
        return self.define(key, lambda i: f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}" fx="{fx}" fy="{fy}" gradientUnits="{units}">'
                           + ''.join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
                           + '</radialGradient>')

    # ---------- painting helpers ----------

    def shape(self, d, col, size, texture=None, tex_amount=0.22, tex_scale=1.0, extra='', **form):
        """A big form: flat colour + form shading (+ texture)."""
        fid = self.form(size, **form)
        s = f'<path d="{d}" fill="{col}" filter="url(#{fid})" {extra}/>'
        if texture:
            tid = self.tex(texture, tex_scale, tex_amount)
            s += f'<path d="{d}" fill="{col}" filter="url(#{tid})" {extra}/>'
        return s

    def bump(self, d, col, soft=4, height=8, spec=0.45, shine=22, stroke=None, sw=0, tr=None):
        """A small part lit as relief. With tr, the path is drawn in that transform but lit in screen space."""
        fid = self.relief(soft, height, spec, shine)
        t = f' transform="{tr}"' if tr else ''
        if stroke:
            p = f'<path d="{d}"{t} fill="none" stroke="{col}" stroke-width="{f(sw)}" stroke-linecap="round" stroke-linejoin="round"/>'
        else:
            p = f'<path d="{d}"{t} fill="{col}"/>'
        return f'<g filter="url(#{fid})">{p}</g>'

    def groove(self, d, col, sw, soft=1.6, depth=-4, tr=None):
        fid = self.relief(soft, depth, 0, 20)
        t = f' transform="{tr}"' if tr else ''
        return (f'<g filter="url(#{fid})"><path d="{d}"{t} fill="none" stroke="{col}" stroke-width="{f(sw)}" '
                f'stroke-linecap="round"/></g>')

    def soft(self, inner, sd):
        """Blur a group in screen space."""
        return f'<g filter="url(#{self.blur(sd)})">{inner}</g>'


def studio(d, top='#2a2226', floor='#3a2e2a', glow='#c98a55', gx=0.4, gy=0.4, horizon=0.78, bokeh=None, seed=1):
    """A small stop-motion set behind the puppet: a dark backdrop with a warm pool of light, out-of-focus set lights
    (bokeh) and a floor with a soft light pool."""
    w, h = d.w, d.h
    g = d.rad([(0, glow, 0.55), (0.45, glow, 0.16), (1, glow, 0)], cx=gx, cy=gy, r=0.7)
    bg = d.lin([(0, mix(top, '#000000', 0.25), 1), (horizon, top, 1), (horizon, floor, 1), (1, mix(floor, '#000000', 0.4), 1)])
    d.add(f'<rect width="{w}" height="{h}" fill="url(#{bg})"/>')
    d.add(f'<rect width="{w}" height="{h}" fill="url(#{g})"/>')
    if bokeh == 'auto':
        import random
        r = random.Random(seed)
        cols = ['#ffcf8a', '#ffb070', '#ffe0b0', '#9ab8ff', '#ff9a70']
        bokeh = []
        for i in range(16):
            x, y = r.random(), r.random() * horizon * 0.95
            if abs(x - 0.5) < 0.22 and y > 0.15:
                x = x + (0.3 if x > 0.5 else -0.3)
            bokeh.append((x, y, 0.015 + r.random() * 0.04, r.choice(cols), round(0.12 + r.random() * 0.3, 2)))
    if bokeh:
        bl = d.blur(max(2, w * 0.006))
        s = ''.join(f'<circle cx="{f(x*w)}" cy="{f(y*h)}" r="{f(r*w)}" fill="{c}" opacity="{a}"/>' for x, y, r, c, a in bokeh)
        d.add(f'<g filter="url(#{bl})">{s}</g>')
    fl = d.rad([(0, mix(floor, glow, 0.35), 0.75), (1, floor, 0)], cx=0.5, cy=0.5, r=0.5)
    d.add(f'<ellipse cx="{w*0.5}" cy="{h*(horizon+0.12)}" rx="{w*0.55}" ry="{h*0.12}" fill="url(#{fl})"/>')


def finish(d, vignette=0.55, grain=0.06):
    """Vignette and fine film grain over the whole frame, as in a photographed set."""
    w, h = d.w, d.h
    v = d.rad([(0.55, '#000000', 0), (1, '#000000', vignette)], r=0.75)
    d.add(f'<rect width="{w}" height="{h}" fill="url(#{v})"/>')
    gid = d.define(('grain', grain), lambda i: (
        f'<filter id="{i}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" '
        f'numOctaves="2" seed="7"/><feColorMatrix type="matrix" values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 {grain*3} 0"/>'
        f'</filter>'))
    d.add(f'<rect width="{w}" height="{h}" filter="url(#{gid})" style="mix-blend-mode:overlay"/>')


def shadow_on_floor(d, cx, cy, rx, ry, a=0.55):
    b = d.blur(max(2, ry * 0.5))
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="#0c0606" opacity="{a}" filter="url(#{b})"/>'


def render(svg_path, png_path, w, h, scale=1):
    """Render with headless Chrome (SVG filters render as in a browser)."""
    html = svg_path + '.html'
    with open(html, 'w') as fh:
        fh.write(f'<html><body style="margin:0;background:#000"><img src="{os.path.basename(svg_path)}" '
                 f'style="width:{w}px;height:{h}px;display:block"></body></html>')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    f'--force-device-scale-factor={scale}', f'--window-size={w},{h}',
                    f'--screenshot={os.path.abspath(png_path)}', 'file://' + os.path.abspath(html)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    os.remove(html)


def puppet(d, inner, size, rim_col='#a8c8ff', rim=0.55, warm_col='#ffcf8a', warm=0.3):
    """Wrap a whole puppet: a cool rim light along its edge away from the key (right), a thin warm edge on the key
    side (left), as the set lights do on a small object."""
    w = max(2.0, size * 0.012)
    key = ('puppet', round(w, 1), rim_col, rim, warm_col, warm)

    def make(i):
        return (f'<filter id="{i}" filterUnits="userSpaceOnUse" x="0" y="0" width="{d.w}" height="{d.h}" color-interpolation-filters="sRGB">'
                f'<feOffset in="SourceAlpha" dx="{f(-w)}" dy="{f(w*0.3)}" result="o"/>'
                f'<feComposite in="SourceAlpha" in2="o" operator="out" result="r"/>'
                f'<feGaussianBlur in="r" stdDeviation="{f(w*0.35)}" result="rb"/>'
                f'<feComposite in="rb" in2="SourceAlpha" operator="in" result="rb2"/>'
                f'<feFlood flood-color="{rim_col}" flood-opacity="{rim}"/><feComposite in2="rb2" operator="in" result="rc"/>'
                f'<feOffset in="SourceAlpha" dx="{f(w*0.6)}" dy="{f(w*0.4)}" result="o2"/>'
                f'<feComposite in="SourceAlpha" in2="o2" operator="out" result="k"/>'
                f'<feGaussianBlur in="k" stdDeviation="{f(w*0.3)}" result="kb"/>'
                f'<feComposite in="kb" in2="SourceAlpha" operator="in" result="kb2"/>'
                f'<feFlood flood-color="{warm_col}" flood-opacity="{warm}"/><feComposite in2="kb2" operator="in" result="kc"/>'
                f'<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="rc"/><feMergeNode in="kc"/></feMerge></filter>')
    fid = d.define(key, make)
    return f'<g filter="url(#{fid})">{inner}</g>'


def keylight(d, x, y, r, dark='#1c1430', amount=0.55):
    """Fall-off of the key light over the frame: full at (x, y), darker and cooler away from it (multiply)."""
    g = d.rad([(0, '#ffffff', 1), (0.45, '#ffffff', 1), (1, dark, 1)], cx=x, cy=y, r=r, units='userSpaceOnUse')
    d.add(f'<rect width="{d.w}" height="{d.h}" fill="url(#{g})" opacity="{amount}" style="mix-blend-mode:multiply"/>')
