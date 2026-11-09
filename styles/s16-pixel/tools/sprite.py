"""Small sprites: an ASCII map (one character a pixel, typed by hand) -> canvas with the coloured outline."""
import px

BASE = {'s': 's3', 't': 's2', 'u': 's1', 'h': 's4', 'k': 'x0', 'i': 'x1', 'p': 'x2', 'j': 'x3'}


def make(rows, legend, flip=False):
    """rows: an ASCII map, or a function that draws the canvas itself (big figures are easier in spans)."""
    if callable(rows):
        src = rows()
        x0, y0, x1, y1 = src.bbox()
        c = px.Canvas(x1 - x0 + 3, y1 - y0 + 3); c.paste(src, 1 - x0, 1 - y0)
    else:
        leg = dict(BASE); leg.update(legend)
        w = max(len(r) for r in rows)
        c = px.from_ascii([r.ljust(w, '.') for r in rows], leg)
        x0, y0, x1, y1 = c.bbox()
        d = px.Canvas(x1 - x0 + 3, y1 - y0 + 3); d.paste(c, 1 - x0, 1 - y0); c = d
    c.outline()
    if flip:
        d = px.Canvas(c.w, c.h); d.paste(c, flip=True); c = d
    return c
