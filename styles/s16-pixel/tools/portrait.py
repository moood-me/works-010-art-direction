"""Portraits (56 x 56): shared parts. A portrait is built in layers — back hair, neck, clothes, head, face, front
hair — each typed as rows of spans and small ASCII stamps; then the passes: cast shadows, the jaw line, the outline.
Light comes from the upper left."""
import px

W = H = 56
CX = 28           # the seam of the face's middle: columns 27 | 28


def new():
    return px.Canvas(W, H)


def skin(c, r, right=2):
    """Shade a head of ramp r drawn flat in step 3: a band along the right edge, a line under the jaw."""
    c.rim(r + '3', r + '2', [(1, 0)], right)
    c.rim(r + '3', r + '2', [(0, 1), (1, 1)], 1)


def cast(c, over, on, depth=2, to='2'):
    """A shadow that hair (ramps `over`) throws down on skin (ramp `on`)."""
    hit = []
    for y in range(c.h):
        for x in range(c.w):
            k = c.g[y][x]
            if k and k[0] == on and k[1] in '34':
                if any((c.get(x, y - d) or '..')[0] in over for d in range(1, depth + 1)) or \
                        (c.get(x - 1, y - 1) or '..')[0] in over and (c.get(x, y - 1) or '..')[0] in over:
                    hit.append((x, y))
    for x, y in hit:
        c.g[y][x] = on + to


def jaw(c, on, others, key=None, dirs=((1, 0), (0, 1))):
    """A darker line where the skin meets hair or cloth on the shaded sides — an outline only where it is needed."""
    hit = []
    for y in range(c.h):
        for x in range(c.w):
            k = c.g[y][x]
            if k and k[0] == on and any((c.get(x + dx, y + dy) or '..')[0] in others for dx, dy in dirs):
                hit.append((x, y))
    for x, y in hit:
        c.g[y][x] = key or on + '1'


def checker(c, x, y, w, h, key, on=None, phase=0):
    """A small dither: every other pixel (only over colour `on` if given)."""
    for j in range(h):
        for i in range(w):
            if (i + j + phase) % 2 == 0 and (on is None or c.get(x + i, y + j) == on):
                c.px(x + i, y + j, key)


def both(c, key, pts):
    """The same pixels on both halves of the face."""
    c.pxs(key, *pts); c.pxs(key, *mirror_pts(pts))


def eyes(c, x, y, rows, legend):
    """A pair of eyes from one stamp: the left one at x, y, the right one mirrored."""
    w = max(len(r) for r in rows)
    c.stamp(x, y, rows, legend); c.stamp(2 * CX - x - w, y, rows, legend, flip=True)


def blob(c, x, y, rows, key, on=None):
    """A small cluster typed as strings of '#'; only over colour `on` if given."""
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch == '#' and (on is None or c.get(x + i, y + j) == on):
                c.px(x + i, y + j, key)


def within(c, mask):
    """Drop the pixels of c that fall outside the drawn pixels of mask."""
    for y in range(c.h):
        for x in range(c.w):
            if c.g[y][x] and not mask.g[y][x]:
                c.g[y][x] = None


def stack(*layers):
    c = new()
    for l in layers:
        c.paste(l)
    return c


def mirror_pts(pts):
    return [(2 * CX - 1 - x, y) for x, y in pts]


def framed(p, bg='d1', bg2='d2', edge='x0', lite='d3'):
    """The portrait in its box, as in a game's dialogue: a backdrop with one dithered band, a two-pixel frame."""
    f = px.Canvas(W + 6, H + 6)
    f.rect(0, 0, f.w, f.h, edge)
    f.rect(1, 1, f.w - 2, f.h - 2, lite)
    f.rect(2, 2, f.w - 4, f.h - 4, edge)
    f.rect(3, 3, W, H, bg)
    f.rect(3, 3 + 34, W, H - 34, bg2)
    checker(f, 3, 3 + 30, W, 4, bg2)
    q = p.copy()
    q.outline()
    for y in range(H):                 # the box crops the portrait
        for x in range(W):
            if q.g[y][x]:
                f.px(3 + x, 3 + y, q.g[y][x])
    return f
