"""С18 «Чёрно-белая манга: штрих и тон» — the kit.

Everything is black ink on white paper:
- `stroke`  a pen line with pressure: a filled band along a smooth centre line, thin at both ends, its width a
            function along the line (`w` a number, a list of widths at the points, or a function of t in 0..1);
- `outline` a closed contour whose weight follows the light: thin where the form faces the light (upper left),
            heavy where it turns away (lower right) — the line that carries volume in seinen manga;
- `tone`    screentone: a flat dot pattern (10–60 %) laid into a shape, as the artist cuts tone into a panel;
- `gtone`   graded screentone: dots whose size follows a function — gradients of shadow, sky, mood;
- `hatch`   pen hatching: parallel tapered strokes clipped to a shape, with irregular lengths;
- `blush`   short diagonal strokes on a cheek (Urasawa, Asano);
- `svg`     the page.
Coordinates are pixels; a point is (x, y)."""
import itertools, math, random

INK = '#111'
PAPER = '#fbfaf6'
_uid = itertools.count()


def uid(p='c'):
    return f'{p}{next(_uid)}'


def f1(v):
    return f'{v:.1f}'


# ---------------------------------------------------------------- curves

def catmull(pts, closed=False, n=8):
    """A smooth curve through points (centripetal-ish Catmull-Rom), sampled n per segment."""
    if len(pts) < 3:
        if len(pts) == 2:
            (ax, ay), (bx, by) = pts[0][:2], pts[1][:2]
            return [(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n + 1)]
        return [tuple(p[:2]) for p in pts]
    P = [tuple(p[:2]) for p in pts]
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [(2 * P[0][0] - P[1][0], 2 * P[0][1] - P[1][1])] + P + [(2 * P[-1][0] - P[-2][0], 2 * P[-1][1] - P[-2][1])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed:
        out.append(P[-2])
    return out


def poly(pts, closed=True, prec=1):
    if not pts:
        return ''
    out = []
    last = None
    for x, y in pts:
        q = (round(x, prec), round(y, prec)) if prec else (int(round(x)), int(round(y)))
        if q == last:
            continue
        last = q
        out.append(f'{q[0]:g} {q[1]:g}')
    s = 'M' + 'L'.join(out)
    return s + ('Z' if closed else '')


def smooth_d(pts, closed=True, n=6):
    return poly(catmull(pts, closed, n), closed)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def arclen(c):
    L = [0.0]
    for i in range(1, len(c)):
        L.append(L[-1] + math.hypot(c[i][0] - c[i - 1][0], c[i][1] - c[i - 1][1]))
    return L


def normals(c, closed=False):
    out = []
    n = len(c)
    for i in range(n):
        if closed:
            a, b = c[(i - 1) % n], c[(i + 1) % n]
        else:
            a, b = c[max(i - 1, 0)], c[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        out.append((-dy / L, dx / L))
    return out


# ---------------------------------------------------------------- the pen

def _wfun(w, n):
    if callable(w):
        return w
    if isinstance(w, (list, tuple)):
        ws = list(w)
        def f(t):
            x = t * (len(ws) - 1)
            i = min(int(x), len(ws) - 2)
            return ws[i] + (ws[i + 1] - ws[i]) * (x - i)
        return f
    return lambda t: w


def stroke(pts, w=1.6, taper=(0.18, 0.22), smooth=True, fill=INK, extra='', n=7):
    """A pen line with pressure along points. taper: the parts of the length (start, end) where the pen lifts."""
    c = catmull(pts, False, n) if smooth and len(pts) > 2 else [tuple(p[:2]) for p in pts]
    if len(c) == 2:
        c = [lerp(c[0], c[1], i / 4) for i in range(5)]
    L = arclen(c)
    tot = L[-1] or 1
    wf = _wfun(w, len(pts))
    a, b = taper
    nm = normals(c)
    left, right = [], []
    for i, p in enumerate(c):
        t = L[i] / tot
        k = 1.0
        if a > 0 and t < a:
            k = 0.12 + 0.88 * math.sin(t / a * math.pi / 2)
        if b > 0 and t > 1 - b:
            k = min(k, 0.08 + 0.92 * math.sin((1 - t) / b * math.pi / 2))
        hw = wf(t) * k / 2
        left.append((p[0] + nm[i][0] * hw, p[1] + nm[i][1] * hw))
        right.append((p[0] - nm[i][0] * hw, p[1] - nm[i][1] * hw))
    return f'<path d="{poly(left + right[::-1])}" fill="{fill}" {extra}/>'


LIGHT = (-0.55, -0.83)     # the light comes from the upper left


def outline(pts, w=2.2, k=0.75, closed=True, light=LIGHT, smooth=True, fill=INK, n=7, wmin=0.35, skip=None):
    """A contour whose weight follows the light: w*(1-k) on the lit side up to w*(1+k) on the dark side.
    skip(i, point) -> True leaves that part of the line out (a contour broken where a form meets another)."""
    c = catmull(pts, closed, n) if smooth else [tuple(p[:2]) for p in pts]
    nm = normals(c, closed)
    # the outward normal: for a clockwise shape in screen coordinates the left normal points out
    area = sum(c[i][0] * c[(i + 1) % len(c)][1] - c[(i + 1) % len(c)][0] * c[i][1] for i in range(len(c)))
    sgn = 1 if area > 0 else -1
    ws = []
    for i, (nx, ny) in enumerate(nm):
        d = -(nx * light[0] + ny * light[1]) * sgn * -1
        ws.append(max(wmin, w * (1 + k * d)))
    segs, cur = [], []
    for i, p in enumerate(c + ([c[0]] if closed else [])):
        j = i % len(c)
        if skip and skip(j, p):
            if len(cur) > 1:
                segs.append(cur)
            cur = []
        else:
            cur.append((p, ws[j]))
    if len(cur) > 1:
        segs.append(cur)
    out = []
    for s in segs:
        pts2 = [p for p, _ in s]
        wl = [ww for _, ww in s]
        out.append(stroke(pts2, wl, taper=(0.04, 0.04) if (closed and not skip) else (0.1, 0.1), smooth=False, fill=fill))
    return ''.join(out)


def fillpath(pts, fill=PAPER, closed=True, smooth=True, extra=''):
    d = smooth_d(pts, closed) if smooth else poly([p[:2] for p in pts], closed)
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def clip(pts_or_d, inner, smooth=True):
    """Draw `inner` only inside the shape."""
    cid = uid('k')
    d = pts_or_d if isinstance(pts_or_d, str) else (smooth_d(pts_or_d) if smooth else poly([p[:2] for p in pts_or_d]))
    return f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">{inner}</g>'


def g(inner, tr=''):
    return f'<g transform="{tr}">{inner}</g>' if tr else f'<g>{inner}</g>'


# ---------------------------------------------------------------- screentone

PITCH = 4.6          # dot pitch of the tone (pixels): about 60 lines per inch at the size of a printed page
TONES = {}           # level -> pattern id, collected into <defs>


def tone_id(level, pitch=PITCH, angle=45):
    key = (round(level, 2), pitch, angle)
    if key not in TONES:
        TONES[key] = f'tn{len(TONES)}'
    return TONES[key]


def tone_defs():
    out = []
    for (lv, pitch, angle), pid in TONES.items():
        r = math.sqrt(lv * pitch * pitch / math.pi)
        if lv >= 0.7:
            # a dark tone: white dots on black
            r2 = math.sqrt((1 - lv) * pitch * pitch / math.pi)
            body = f'<rect width="{pitch}" height="{pitch}" fill="{INK}"/><circle cx="{pitch/2:.2f}" cy="{pitch/2:.2f}" r="{r2:.2f}" fill="{PAPER}"/>'
        else:
            body = f'<circle cx="{pitch/2:.2f}" cy="{pitch/2:.2f}" r="{r:.2f}" fill="{INK}"/>'
        out.append(f'<pattern id="{pid}" width="{pitch}" height="{pitch}" patternUnits="userSpaceOnUse" '
                   f'patternTransform="rotate({angle})">{body}</pattern>')
    return ''.join(out)


def tone(pts, level=0.2, smooth=True, pitch=PITCH, extra=''):
    """Flat screentone cut to a shape."""
    d = pts if isinstance(pts, str) else (smooth_d(pts) if smooth else poly([p[:2] for p in pts]))
    return f'<path d="{d}" fill="url(#{tone_id(level, pitch)})" {extra}/>'


def gtone(box, cov, clip_pts=None, pitch=PITCH, smooth=True, angle=45, seed=0):
    """Graded screentone: dots on a 45° grid over box (x0, y0, x1, y1) with coverage cov(x, y) in 0..1."""
    x0, y0, x1, y1 = box
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + pitch
    groups = {}
    n = int(R / pitch) + 1
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            u, v = i * pitch, j * pitch
            x, y = cx + u * ca - v * sa, cy + u * sa + v * ca
            if x < x0 - pitch or x > x1 + pitch or y < y0 - pitch or y > y1 + pitch:
                continue
            c = cov(x, y)
            if c <= 0.015:
                continue
            c = min(c, 0.78)
            r = math.sqrt(c * pitch * pitch / math.pi)
            q = round(r * 5) / 5
            if q <= 0:
                continue
            groups.setdefault(q, []).append(f'M{x:.0f} {y:.0f}h0')
    body = ''.join(f'<path d="{"".join(v)}" stroke="{INK}" stroke-width="{2*q:.1f}" stroke-linecap="round"/>' for q, v in sorted(groups.items()))
    if clip_pts is not None:
        return clip(clip_pts, body, smooth)
    return body


# ---------------------------------------------------------------- hatching

def hatch(clip_pts, box, angle=-35, gap=5.0, w=0.9, length=(0.6, 1.0), density=None, seed=1, smooth=True, jitter=0.25):
    """Parallel pen strokes over box, clipped to clip_pts. density(x, y) in 0..1 keeps or drops strokes and shortens
    them: hatching that fades into the light. Drawn as round-capped lines, one path per width."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2
    buckets = {}
    k = -R
    while k < R:
        px, py = cx + nx * k, cy + ny * k
        s_ = -R
        while s_ < R:
            seg = R * 0.5 * rnd.uniform(*length)
            mx, my = px + dx * (s_ + seg / 2), py + dy * (s_ + seg / 2)
            if x0 - 2 <= mx <= x1 + 2 and y0 - 2 <= my <= y1 + 2:
                dens = density(mx, my) if density else 1.0
                if dens > 0.02 and rnd.random() < min(1.0, dens * 1.6):
                    sl = seg * min(1.0, 0.35 + dens)
                    off = rnd.uniform(-jitter, jitter) * gap
                    a0 = (px + dx * s_ + nx * off, py + dy * s_ + ny * off)
                    a1 = (px + dx * (s_ + sl) + nx * off, py + dy * (s_ + sl) + ny * off)
                    q = round(w * rnd.uniform(0.75, 1.15), 1)
                    buckets.setdefault(q, []).append(f'M{a0[0]:.0f} {a0[1]:.0f}L{a1[0]:.0f} {a1[1]:.0f}')
            s_ += seg * rnd.uniform(1.0, 1.3)
        k += gap
    body = ''.join(f'<path d="{"".join(v)}" stroke="{INK}" stroke-width="{q}" stroke-linecap="round" fill="none"/>' for q, v in buckets.items())
    return clip(clip_pts, body, smooth) if clip_pts is not None else body


def blush(cx, cy, w=26, h=10, n=6, angle=-60, lw=0.8, seed=3):
    """Short diagonal strokes on a cheek."""
    rnd = random.Random(seed)
    out = []
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    for i in range(n):
        t = (i + 0.5) / n - 0.5
        x = cx + t * w
        y = cy + rnd.uniform(-0.15, 0.15) * h
        L = h * rnd.uniform(0.8, 1.1)
        out.append(stroke([(x - dx * L / 2, y - dy * L / 2), (x + dx * L / 2, y + dy * L / 2)], lw, taper=(0.35, 0.45), smooth=False))
    return ''.join(out)


# ---------------------------------------------------------------- the page

def svg(W, H, inner, bg=PAPER):
    defs = tone_defs()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs>{defs}</defs><rect width="{W}" height="{H}" fill="{bg}"/>{inner}</svg>')


def panel(x, y, w, h, wd=2.4):
    """A panel border."""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="{wd}"/>'
