"""Small helpers for hand-written SVG: flat shapes, coloured lines, clipped cel shadows."""

_n = [0]


def uid(p='c'):
    _n[0] += 1
    return f'{p}{_n[0]}'


LW = [2.6]  # current line width


def F(d, fill, line=None, w=None, extra=''):
    """A flat shape with a coloured outline."""
    s = f'<path d="{d}" fill="{fill}"'
    if line:
        s += f' stroke="{line}" stroke-width="{w or LW[0]}" stroke-linejoin="round" stroke-linecap="round"'
    return s + f' {extra}/>'


def L(d, line, w=None, extra=''):
    """A line only."""
    return (f'<path d="{d}" fill="none" stroke="{line}" stroke-width="{w or LW[0]}" '
            f'stroke-linejoin="round" stroke-linecap="round" {extra}/>')


def clip(form_d, *inner):
    """Draw inner shapes clipped to form_d."""
    i = uid('k')
    return f'<clipPath id="{i}"><path d="{form_d}"/></clipPath><g clip-path="url(#{i})">{"".join(inner)}</g>'


def shaded(d, fill, shade_d, shade, line, w=None):
    """A form: flat fill, a cel shadow shape clipped inside, then the outline on top."""
    return F(d, fill) + clip(d, F(shade_d, shade)) + L(d, line, w)


def g(content, x=0, y=0, s=1, extra=''):
    sx = s if not isinstance(s, tuple) else s[0]
    sy = s if not isinstance(s, tuple) else s[1]
    return f'<g transform="translate({x} {y}) scale({sx} {sy})" {extra}>{"".join(content) if isinstance(content, list) else content}</g>'


def mirror(content):
    return f'<g transform="scale(-1 1)">{content}</g>'


def svg(w, h, body, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">{b}{body}</svg>\n')


def text(x, y, t, size=22, col='#3a2e2a', anchor='middle', weight=600):
    return (f'<text x="{x}" y="{y}" font-family="Georgia, \'DejaVu Serif\', serif" font-size="{size}" '
            f'fill="{col}" text-anchor="{anchor}" font-weight="{weight}">{t}</text>')
