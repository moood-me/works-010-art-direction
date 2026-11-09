"""Pixel canvas of С16: a grid of colour keys (pal.py); every pixel is put by a decision of the drawing code.
Shared by sprites, portraits and sheets. Output: SVG of crisp rects, enlarged by a whole factor."""
import pal


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = [[None] * w for _ in range(h)]

    # --- putting pixels
    def get(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def px(self, x, y, key):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = key

    def pxs(self, key, *pts):
        for x, y in pts:
            self.px(x, y, key)

    def rect(self, x, y, w, h, key):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.px(i, j, key)

    def hline(self, x0, x1, y, key):
        for i in range(min(x0, x1), max(x0, x1) + 1):
            self.px(i, y, key)

    def vline(self, x, y0, y1, key):
        for j in range(min(y0, y1), max(y0, y1) + 1):
            self.px(x, j, key)

    def line(self, x0, y0, x1, y1, key):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        e = dx + dy
        while True:
            self.px(x0, y0, key)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * e
            if e2 >= dy:
                e += dy; x0 += sx
            if e2 <= dx:
                e += dx; y0 += sy

    def spans(self, y, rows, key):
        """rows: (x0, x1) inclusive for each row down from y — a silhouette typed row by row."""
        for j, r in enumerate(rows):
            if r is not None:
                self.hline(r[0], r[1], y + j, key)

    def sym(self, cx, y, halfs, key):
        """rows of half-widths around the seam between columns cx-1 and cx."""
        for j, hw in enumerate(halfs):
            if hw:
                self.hline(cx - hw, cx + hw - 1, y + j, key)

    def stamp(self, x, y, rows, legend, flip=False):
        """An ASCII map: one character a pixel; '.' and ' ' are empty; legend: char -> colour key."""
        for j, row in enumerate(rows):
            if flip:
                row = row[::-1]
            for i, ch in enumerate(row):
                if ch not in '. ':
                    self.px(x + i, y + j, legend[ch])

    # --- passes over what is drawn
    def keys(self, pred):
        return [(x, y) for y in range(self.h) for x in range(self.w) if self.g[y][x] and pred(self.g[y][x])]

    def rim(self, src, dst, dirs, depth=1):
        """Pixels of colour `src` that have, within `depth` steps along one of `dirs`, a pixel that is not of the
        same ramp (an edge of the form) become `dst`: a band of shade (or light) along chosen edges."""
        hit = []
        for y in range(self.h):
            for x in range(self.w):
                if self.g[y][x] != src:
                    continue
                for dx, dy in dirs:
                    if any((self.get(x + dx * k, y + dy * k) or '..')[0] != src[0] for k in range(1, depth + 1)):
                        hit.append((x, y)); break
        for x, y in hit:
            self.g[y][x] = dst

    def outline(self, key=None, sel=True, skip=()):
        """Outline one pixel wide round the drawing. key=None: the colour is step 0 of the ramp of the pixel it
        hugs (a coloured, selective outline); with sel, where the light falls (above and to the left of the form)
        it is one step lighter for the ramps that have room."""
        add = []
        for y in range(self.h):
            for x in range(self.w):
                if self.g[y][x]:
                    continue
                for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    n = self.get(x + dx, y + dy)
                    if n and n[0] not in skip:
                        if key:
                            k = key
                        else:
                            lit = sel and (dx, dy) in ((0, 1), (1, 0)) and int(n[1]) >= 3
                            k = n[0] + ('1' if lit and n[0] in 'satwco' else '0')
                        add.append((x, y, k)); break
        for x, y, k in add:
            self.g[y][x] = k

    def paste(self, other, x=0, y=0, flip=False):
        for j in range(other.h):
            for i in range(other.w):
                k = other.g[j][other.w - 1 - i if flip else i]
                if k:
                    self.px(x + i, y + j, k)

    def copy(self):
        c = Canvas(self.w, self.h)
        c.g = [r[:] for r in self.g]
        return c

    def bbox(self):
        xs = [x for y in range(self.h) for x in range(self.w) if self.g[y][x]]
        ys = [y for y in range(self.h) for x in range(self.w) if self.g[y][x]]
        return min(xs), min(ys), max(xs), max(ys)

    def colours(self):
        return sorted({k for r in self.g for k in r if k})

    # --- out
    def svg(self, scale, bg=None):
        W, H = self.w * scale, self.h * scale
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {self.w} {self.h}" '
               f'shape-rendering="crispEdges">']
        if bg:
            out.append(f'<rect width="{self.w}" height="{self.h}" fill="{pal.hexof(bg)}"/>')
        by = {}
        for y in range(self.h):
            x = 0
            while x < self.w:
                k = self.g[y][x]
                if not k or k == bg:
                    x += 1; continue
                x1 = x
                while x1 + 1 < self.w and self.g[y][x1 + 1] == k:
                    x1 += 1
                by.setdefault(k, []).append(f'M{x} {y}h{x1 - x + 1}v1h-{x1 - x + 1}z')
                x = x1 + 1
        for k in sorted(by):
            out.append(f'<path fill="{pal.hexof(k)}" d="{"".join(by[k])}"/>')
        out.append('</svg>')
        return '\n'.join(out)


def from_ascii(rows, legend, pad=1):
    w = max(len(r) for r in rows)
    c = Canvas(w + 2 * pad, len(rows) + 2 * pad)
    c.stamp(pad, pad, rows, legend)
    return c
