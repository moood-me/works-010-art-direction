"""Sculpted puppet hair: not single strands but a few solid masses, like resin or clay hair on a Laika or Aardman
puppet. A mass is the union of wide locks (ribbons along 3D centre lines) and, if wanted, a cap over the skull; the
union gets form shading as one object; then each lock is cut in with grooves along its flow and at its edges, and a
band of sheen crosses the locks where the key light catches them. Tips separate because the locks diverge.

Locks are given in head units (see head.Head) and turn with the head, so the same hair works in every view.
"""
import math
from sculpt import pts, poly, f, mix


class Lock:
    def __init__(self, path3, w0, w1=0.0, taper=1.5, z_bias=0.0, col=None, grooves=1, sheen=(0.12, 0.38), root=0.45, strands=5):
        self.path3, self.w0, self.w1, self.taper, self.root = path3, w0, w1, taper, root
        self.strands = strands
        self.z_bias, self.col, self.grooves, self.sheen = z_bias, col, grooves, sheen


def _resample(points, n):
    """Even spacing along a polyline (screen points with depth)."""
    d = [0.0]
    for i in range(1, len(points)):
        d.append(d[-1] + math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]))
    L = d[-1] or 1.0
    out, j = [], 0
    for k in range(n):
        s = L * k / (n - 1)
        while j < len(d) - 2 and d[j + 1] < s:
            j += 1
        t = (s - d[j]) / ((d[j + 1] - d[j]) or 1)
        a, b = points[j], points[j + 1]
        out.append(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))
    return out


def _smooth(points, it=2):
    p = list(points)
    for _ in range(it):
        q = [p[0]]
        for i in range(1, len(p) - 1):
            q.append(tuple((p[i - 1][k] + 2 * p[i][k] + p[i + 1][k]) / 4 for k in range(3)))
        q.append(p[-1])
        p = q
    return p


def geom(h, L, n=22):
    """Screen geometry of a lock: centre line, half widths, outline polygon, mean depth."""
    S = h.S
    c = _smooth(_resample([h.scr(p) for p in L.path3], n))
    left, right, half = [], [], []
    for i in range(n):
        x, y, _ = c[i]
        xa, ya, _ = c[max(0, i - 1)]
        xb, yb, _ = c[min(n - 1, i + 1)]
        dx, dy = xb - xa, yb - ya
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        t = i / (n - 1)
        w = (L.w0 + (L.w1 - L.w0) * t ** L.taper) * S / 2
        w *= min(1.0, L.root + (1 - L.root) * t / 0.22)      # narrow at the root, so roots don't stick out of the head
        half.append(w)
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    z = sum(p[2] for p in c) / n + L.z_bias
    return dict(c=c, half=half, left=left, right=right, poly=left + right[::-1], z=z)


def cap_polys(h, k, line, y_back=None, rows=80, cols=120):
    """The hair cap over the skull (shell = head scaled by k): the region above the hairline line(phi).
    Built as horizontal strips of the shell, split into the part turned away from us (back, drawn before the head)
    and the part facing us (front). Returns (back, front): lists of polygons."""
    back, front = [], []
    ys = [-0.5 + (0.5 + 0.35) * i / rows for i in range(rows + 1)]
    for r in range(rows):
        ya, yb = ys[r], ys[r + 1]
        ym = (ya + yb) / 2
        dp = 2 * math.pi / cols

        def cross(p_in, p_out, y):
            """phi where the hairline passes height y, between an inside and an outside phi."""
            for _ in range(18):
                m = (p_in + p_out) / 2
                if y <= line(m):
                    p_in = m
                else:
                    p_out = m
            return p_in

        def strip(run, open_l, open_r):
            # top edge at ya, bottom at yb; ends cut exactly at the hairline where the run meets it
            a0, a1 = run[0], run[-1]
            tl = cross(a0, a0 - dp, ya) if open_l else a0
            tr = cross(a1, a1 + dp, ya) if open_r else a1
            bl = cross(a0, a0 - dp, yb) if open_l and yb > line(a0) else (cross(a0, a0 - dp, yb) if open_l else a0)
            br = cross(a1, a1 + dp, yb) if open_r and yb > line(a1) else (cross(a1, a1 + dp, yb) if open_r else a1)
            if open_l and yb > line(a0):
                bl = a0
            if open_r and yb > line(a1):
                br = a1
            n = max(2, min(14, len(run)))
            top = [h.P(h.surf(tl + (tr - tl) * i / (n - 1), ya - 0.004, 0, k)) for i in range(n)]
            bot = [h.P(h.surf(bl + (br - bl) * i / (n - 1), yb + 0.004, 0, k)) for i in range(n)]
            return top + bot[::-1]

        run, run_front, open_l = [], None, False
        prev_inside = False
        for j in range(cols + 1):
            phi = -math.pi + dp * j
            inside = ym <= line(phi)
            fr = h.facing(phi, ym) >= 0 if inside else None
            if run and (not inside or fr != run_front):
                if len(run) > 1:
                    (front if run_front else back).append(strip(run, open_l, not inside))
                open_l = False
                run = [run[-1]] if inside else []
            if inside:
                if not run:
                    open_l = not prev_inside and j > 0
                run.append(phi)
                run_front = fr
            prev_inside = inside
        if len(run) > 1:
            (front if run_front else back).append(strip(run, open_l, False))
    return back, front


def mass(d, h, P, locks, col, cap=None, groove_col=None, sheen=0.28, name='hair'):
    """One sculpted mass of hair: union of locks (+ cap polygon) with form shading, grooves, sheen."""
    S = h.S
    G = [geom(h, L) for L in locks]
    if not G and not cap:
        return ''
    fid = d.form(S * 0.6, shade=P.get('hair_shade', '#1a0a06'), depth=0.6, ao=0.45, sheen=0.0, rim=0.0,
                 rim_col=P.get('hair_rim', '#c0d4ff'))
    gc = groove_col or mix(col, '#000000', 0.15)
    gid = d.relief(max(1.2, round(S * 0.004, 1)), -max(2.5, round(S * 0.012, 1)), 0, 20)
    gw = max(1.2, S * 0.0055)
    body = []
    if cap:
        body.append(''.join(f'<path d="{poly(c)}" fill="{col}" stroke="{col}" stroke-width="1"/>' for c in cap))
    # each lock in turn: its fill covers the cuts of the locks under it
    fid2 = d.relief(1.0, -max(1.5, round(S * 0.005, 1)), 0, 20)
    for g, L in zip(G, locks):
        fine = []
        body.append(f'<path d="{pts(g["poly"])}" fill="{L.col or col}"/>')
        n = len(g['c'])
        gr = ''
        for k in range(1, L.grooves + 1):
            o = k / (L.grooves + 1) * 2 - 1      # -1..1 across
            line = []
            a0 = int(n * (0.08 + 0.1 * abs(o)))
            for i in range(a0, n - 4):
                x, y, _ = g['c'][i]
                lx, ly = g['left'][i]
                line.append((x + (lx - x) * o * 0.85, y + (ly - y) * o * 0.85))
            if len(line) > 2:
                gr += f'<path d="{pts(line, close=False)}" fill="none" stroke="{gc}" stroke-width="{f(gw)}" stroke-linecap="round"/>'
        # fine strands: shallow cuts along the flow
        for k in range(L.strands):
            o = -0.9 + 1.8 * (k + 0.5) / L.strands
            line = []
            for i in range(int(n * 0.05), n - 2, 2):
                x, y, _ = g['c'][i]
                lx, ly = g['left'][i]
                line.append((x + (lx - x) * o, y + (ly - y) * o))
            fine.append(pts(line, close=False))
        e = g['left'][2:-1] + g['right'][::-1][1:-2]
        gr += f'<path d="{pts(e, close=False)}" fill="none" stroke="{gc}" stroke-width="{f(gw*1.6)}" stroke-linecap="round"/>'
        lc = d.uid('lc')
        d.defs.append(f'<clipPath id="{lc}"><path d="{pts(g["poly"])}"/></clipPath>')
        fl = ''.join(f'<path d="{q}" fill="none" stroke="{gc}" stroke-width="{f(gw*0.5)}"/>' for q in fine)
        body.append(f'<g clip-path="url(#{lc})"><g filter="url(#{fid2})" opacity="0.7">{fl}</g><g filter="url(#{gid})">{gr}</g></g>')
    out = [f'<g filter="url(#{fid})">{"".join(body)}</g>']
    # sheen: a light band across the locks where the key light catches the curve of the head
    cid = d.uid('hc')
    d.defs.append(f'<clipPath id="{cid}">' + (''.join(f'<path d="{poly(c)}"/>' for c in cap) if cap else '')
                  + ''.join(f'<path d="{pts(g["poly"])}"/>' for g in G) + '</clipPath>')
    hb = d.blur(max(1.5, S * 0.014))
    sh = ''
    for g, L in zip(G, locks):
        a, b = L.sheen
        n = len(g['c'])
        seg = g['c'][int(a * n):max(int(a * n) + 2, int(b * n))]
        if len(seg) >= 2:
            w = 2 * g['half'][int(a * n)] * 0.3
            sh += (f'<path d="{pts([(p[0], p[1]) for p in seg], close=False)}" fill="none" stroke="#ffe6c8" '
                   f'stroke-width="{f(w)}" stroke-linecap="round"/>')
    out.append(f'<g clip-path="url(#{cid})"><g filter="url(#{hb})" opacity="{sheen}" style="mix-blend-mode:screen">{sh}</g></g>')
    return ''.join(out)


def surf_path(h, pts3, out=0.03, k=1.04):
    """A path over the shell through (phi, y) way points (smoothly interpolated).
    out: distance off the shell — a number, or (at the root, at the end) to let the hair gain volume as it goes."""
    o0, o1 = out if isinstance(out, tuple) else (out, out)
    res = []
    m = len(pts3) - 1
    for i in range(m):
        (p0, y0), (p1, y1) = pts3[i], pts3[i + 1]
        for j in range(6):
            t = j / 6
            u = (i + t) / m
            res.append(h.surf(p0 + (p1 - p0) * t, y0 + (y1 - y0) * t, o0 + (o1 - o0) * u, k))
    res.append(h.surf(pts3[-1][0], pts3[-1][1], o1, k))
    return res


def fall(p, length, n=8, side=1, out_x=0.0, back_z=0.0, wave=0.0, waves=1.0, phase=0.0, flick=0.0):
    """Hang a lock down from 3D point p (head units)."""
    x0, y0, z0 = p
    res = []
    for i in range(1, n + 1):
        t = i / n
        x = x0 + side * (out_x * t + wave * math.sin(2 * math.pi * waves * t + phase) + flick * t ** 4)
        res.append((x, y0 + length * t, z0 + back_z * t))
    return res


# ------------------------------------------------------------------ sculpted curls
def curl_spots(h, inside, r, y0, y1, out=0.02, k=1.0, seed=1, place=None, radius=None, jitter=0.22):
    """Where the curls of a curly mass sit: a jittered honeycomb over the surface, kept where inside(phi, y).
    r — curl radius (head units); place(phi, y) → 3D point for a mass that leaves the head (a beard under the chin);
    radius(y) — the mass's half width there (for the spacing round it). The same seed gives the same curls in every
    view. Returns [(point3, radius, facing, start angle, winding)]."""
    import random
    rnd = random.Random(seed)
    spots = []
    step = r * 1.12
    rows = int((y1 - y0) / (step * 0.87)) + 1
    for i in range(rows):
        y = y0 + i * step * 0.87
        rad = radius(y) if radius else (h.a(y) + h.b(y)) / 2 * k
        m = max(3, int(2 * math.pi * max(rad, 0.03) / step))
        for j in range(m):
            phi = -math.pi + 2 * math.pi * (j + 0.5 * (i % 2)) / m + (rnd.random() - 0.5) * jitter * step / max(rad, 0.03)
            yy = y + (rnd.random() - 0.5) * jitter * step
            rr = r * (0.85 + 0.3 * rnd.random())
            a0, wind = rnd.random() * 2 * math.pi, rnd.choice((-1, 1))
            if not inside(phi, yy):
                continue
            p = place(phi, yy) if place else h.surf(phi, yy, out, k)
            spots.append((p, rr, h.facing(phi, max(-0.5, min(0.5, yy))), a0, wind))
    return spots


def coils(d, h, P, spots, col):
    """A curly mass, as on a clay or yarn-haired puppet: every curl is a small ball with a spiral cut into it, lit
    from the key side; the balls overlap from back to front and the whole mass is shaded as one form.
    Returns (behind the head, over the head)."""
    S = h.S
    ball = d.rad([(0, mix(col, '#ffe8d0', 0.3), 1), (0.45, col, 1), (1, mix(col, '#000000', 0.6), 1)],
                 cx=0.5, cy=0.5, r=0.56, fx=0.3, fy=0.24)
    cut, lit = mix(col, '#000000', 0.55), mix(col, '#ffe8d0', 0.38)
    back, front = [], []
    for p, rr, facing, a0, wind in spots:
        x, y, z = h.scr(p)
        R = rr * S
        sp = []
        for i in range(15):
            t = i / 14
            a = a0 + wind * 2 * math.pi * 1.2 * t
            q = R * (0.8 - 0.62 * t)
            sp.append((x + q * math.cos(a), y + q * math.sin(a)))
        path = pts(sp, close=False)
        s = (f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(R)}" fill="url(#{ball})"/>'
             f'<path d="{path}" fill="none" stroke="{cut}" stroke-width="{f(R*0.15)}" stroke-linecap="round"/>'
             f'<path d="{path}" fill="none" stroke="{lit}" stroke-width="{f(R*0.07)}" stroke-linecap="round" opacity="0.5" '
             f'transform="translate({f(-R*0.09)},{f(-R*0.09)})"/>')
        (front if facing > -0.2 else back).append((z, s))
    fid = d.form(S * 0.6, shade=P.get('hair_shade', '#1a0a06'), depth=0.5, ao=0.4, sheen=0.0, rim=0.0)
    res = []
    for lst in (back, front):
        lst.sort(key=lambda t: t[0])
        res.append(f'<g filter="url(#{fid})">{"".join(s for _, s in lst)}</g>' if lst else '')
    return res[0], res[1]
