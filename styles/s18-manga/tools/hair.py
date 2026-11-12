"""Hair: locks (tapered ribbons) laid on a shell around the head, from the parting (or the crown) to the hairline,
and on down for long hair. The union of the locks is the hair's mass; it is drawn black with white streaks of light
(dark hair), or white with an outline and pen lines along the flow (light or grey hair).

A lock is a 3D curve; every segment goes to the back layer (drawn before the face) or the front layer (after it) by
which way its piece of the shell faces, so the same numbers give the front, the three-quarter and the profile."""
import math, random
from pen import *
from head import interp_table, LIGHT3, silhouette


def periodic(keys, a, asym=None):
    """keys: [(azimuth in degrees 0..180, value)] for a symmetric head; asym: the same for negative azimuths."""
    tab = keys
    if a < 0:
        if asym is not None:
            tab = asym; a = -a
        else:
            a = -a
    a = min(180, a)
    for i in range(len(tab) - 1):
        if tab[i][0] <= a <= tab[i + 1][0]:
            t = (a - tab[i][0]) / (tab[i + 1][0] - tab[i][0])
            t = t * t * (3 - 2 * t)
            return tab[i][1] + (tab[i + 1][1] - tab[i][1]) * t
    return tab[-1][1]


class Hair:
    def __init__(self, **k):
        self.k = dict(mode='black', hl=[(0, -0.30), (45, -0.26), (80, -0.10), (100, 0.04), (130, 0.12), (180, 0.20)],
                      hl_neg=None, end=None, end_neg=None, thick=0.045, top_thick=0.06, part=-25, n=120, width=0.075,
                      wave=0.0, waves=3.0, spike=0.0, hang_out=0.05, hang_back=0.0, bald=None, seed=5,
                      streaks=1.0, flow=1.0, locks=None, bun=None, tone_level=0.0, lw_scale=1.0, back_only=None,
                      sweep=0.0)
        self.k.update(k)

    # ------------------------------------------------ geometry
    def hl(self, a):
        return periodic(self.k['hl'], a, self.k['hl_neg'])

    def end(self, a):
        if self.k['end'] is None:
            return self.hl(a)
        return max(self.hl(a), periodic(self.k['end'], a, self.k['end_neg']))

    def shell(self, h, a, y, grow=None):
        """The shell point at azimuth a (degrees; 0 is the front, + towards the character's left) and level y."""
        g = self.k['thick'] if grow is None else grow
        if y < -0.3:
            g += (self.k['top_thick'] - self.k['thick']) * min(1, (-0.3 - y) / 0.15)
        yy = min(y, 0.16)
        w, zf, zb, z0, nf = h.sec(yy)
        w += g; zf += g; zb -= g
        r = math.radians(a)
        s, c = math.sin(r), math.cos(r)
        # walk out from the axis in direction (s, c) until the section boundary
        if c >= 0:
            # superellipse front: |x/w|^nf + |(z-z0)/(zf-z0)|^nf = 1 along the ray
            t = 1.0 / (((abs(s) / w) ** nf + (c / max(zf - z0, 1e-3)) ** nf) ** (1 / nf))
        else:
            t = 1.0 / math.sqrt((s / w) ** 2 + (c / max(z0 - zb, 1e-3)) ** 2)
        x, z = s * t, z0 + c * t
        if y > 0.16:
            # hanging below the skull: out a little and down
            d = y - 0.16
            x += s * self.k['hang_out'] * min(1, d * 3)
            z += c * self.k['hang_out'] * min(1, d * 3) - self.k['hang_back'] * d
        return (x, y, z)

    def shell_ray(self, h, d, C=(0.0, -0.12, -0.07)):
        """Where a ray from inside the head in direction d meets the shell."""
        def inside(r):
            x, y, z = C[0] + d[0] * r, C[1] + d[1] * r, C[2] + d[2] * r
            g = self.k['thick'] + (self.k['top_thick'] - self.k['thick']) * min(1, max(0, (-0.3 - y) / 0.15))
            if y < h.top - g:
                return False
            z0 = h.sec(min(y, 0.16))[3]
            a = math.degrees(math.atan2(x, z - z0))
            q = self.shell(h, a, y)
            return math.hypot(x, z - z0) < math.hypot(q[0], q[2] - z0)
        lo, hi = 0.0, 1.5
        for _ in range(22):
            mid = (lo + hi) / 2
            if inside(mid):
                lo = mid
            else:
                hi = mid
        r = (lo + hi) / 2
        p = (C[0] + d[0] * r, C[1] + d[1] * r, C[2] + d[2] * r)
        z0 = h.sec(min(p[1], 0.16))[3]
        return p, (math.degrees(math.atan2(p[0], p[2] - z0)), p[1])

    def normal(self, h, a, y):
        r = math.radians(a)
        up = max(0.0, min(1.0, (-0.25 - y) / 0.25))
        n = (math.sin(r) * (1 - up), -up, math.cos(r) * (1 - up))
        L = math.sqrt(sum(c * c for c in n)) or 1
        return tuple(c / L for c in n)

    def strands(self, h):
        k = self.k
        rnd = random.Random(k['seed'])
        out = []
        n = k['n']
        part = k['part']
        for i in range(n):
            a_end = -180 + 360 * (i + rnd.uniform(-0.3, 0.3)) / n
            if k['back_only'] is not None and abs(a_end) < k['back_only']:
                continue
            ye = self.end(a_end)
            yh = self.hl(a_end)
            if ye > yh + 0.1:
                ye += rnd.uniform(-0.1, 0.03) * min(1.0, (ye - yh))
            if k.get('to_bun'):
                B = k['bun']
                C = (0.0, -0.12, -0.07)
                p0 = self.shell(h, a_end, yh)
                d0 = [p0[i] - C[i] for i in range(3)]
                d1 = [B['c'][i] - C[i] for i in range(3)]
                n0 = math.sqrt(sum(c * c for c in d0)); n1 = math.sqrt(sum(c * c for c in d1))
                d0 = [c / n0 for c in d0]; d1 = [c / n1 for c in d1]
                p3, ay = [], []
                m = 16
                for j in range(m + 1):
                    t = j / m
                    d = [d0[i] * (1 - t) + d1[i] * t for i in range(3)]
                    q, (aa, yy) = self.shell_ray(h, d)
                    p3.append(q); ay.append((aa, yy))
                w = k['width'] * rnd.uniform(0.8, 1.2)
                out.append(dict(pts=ay[::-1], p3=p3[::-1], w=w, phase=0, amp=0, spike=0, key=i, root_end=True))
                continue
            if k['bald'] is not None:
                a_start = a_end
                y_start = periodic(k['bald'], a_end)
            else:
                d = a_end - part
                if d > 180: d -= 360
                if d < -180: d += 360
                f = min(1.0, abs(d) / 150)
                a_start = part + (d * 0.15 if abs(d) < 150 else d * 0.6)
                y_start = self.hl(part) * (1 - f) + (-0.47) * f
                y_start = min(y_start, yh - 0.05)
            pts = []
            m = 9
            sweep = k['sweep']
            for j in range(m + 1):
                t = j / m
                a = a_start + (a_end - a_start) * (1 - (1 - t) ** 2) + sweep * math.sin(t * math.pi)
                y = y_start + (yh - y_start) * t
                pts.append((a, y))
            if ye > yh + 0.02:
                mm = max(2, int((ye - yh) / 0.1))
                for j in range(1, mm + 1):
                    t = j / mm
                    pts.append((a_end + rnd.uniform(-2, 2) * t, yh + (ye - yh) * t))
            w = k['width'] * rnd.uniform(0.75, 1.25)
            out.append(dict(pts=pts, w=w, phase=rnd.uniform(0, 6.28), amp=k['wave'] * rnd.uniform(0.6, 1.3),
                            spike=k['spike'] * rnd.uniform(0.5, 1.3), key=i))
        return out

    def lock3d(self, h, s):
        """The strand's 3D points with its wave and spike."""
        if 'p3' in s:
            return list(zip(s['p3'], s['pts']))
        P = []
        n = len(s['pts'])
        for j, (a, y) in enumerate(s['pts']):
            p = self.shell(h, a, y)
            t = j / (n - 1)
            if s['amp']:
                nn = self.normal(h, a, y)
                off = s['amp'] * math.sin(s['phase'] + t * self.k['waves'] * 2 * math.pi) * min(1, t * 3)
                # sideways wave (along the azimuth direction)
                r = math.radians(a)
                p = (p[0] + math.cos(r) * off, p[1], p[2] - math.sin(r) * off)
            if s['spike'] and j == n - 1:
                nn = self.normal(h, a, y)
                p = tuple(p[i] + nn[i] * s['spike'] for i in range(3))
                p = (p[0], p[1] + s['spike'] * 0.4, p[2])
            P.append((p, (a, y)))
        return P

    # ------------------------------------------------ drawing
    def _pieces(self, h, v):
        if getattr(self, '_cache', None) and self._cache[0] is h and self._cache[1] is v:
            return self._cache[2]
        back, front = [], []
        for s in self.strands(h):
            P = self.lock3d(h, s)
            # split the strand by facing
            cur, cur_front = [], None
            n = len(P)
            for j, (p, (a, y)) in enumerate(P):
                f = v.facing(self.normal(h, a, y)) > -0.05
                if cur_front is None:
                    cur_front = f
                if f != cur_front and len(cur) > 1:
                    (front if cur_front else back).append((cur + [(p, (a, y), j / (n - 1))], s))
                    cur = [cur[-1]]
                    cur_front = f
                cur.append((p, (a, y), j / (n - 1)))
            if len(cur) > 1:
                (front if cur_front else back).append((cur, s))
        # the scalp: small quads of the shell above the hairline, so no paper shows between the locks
        scalp_f, scalp_b = [], []
        if self.k.get('cap', True):
            da = 9
            for ai in range(-180, 180, da):
                for side_a in (ai,):
                    a0, a1 = side_a, side_a + da
                    yt = h.top + 0.004 if self.k['bald'] is None else max(periodic(self.k['bald'], a0), periodic(self.k['bald'], a1))
                    yh = min(self.hl(a0), self.hl(a1)) - self.k.get('edge', 0.035)
                    if yh <= yt:
                        continue
                    nlev = max(1, int((yh - yt) / 0.05))
                    for j in range(nlev):
                        y0 = yt + (yh - yt) * j / nlev; y1 = yt + (yh - yt) * (j + 1) / nlev
                        q = [self.shell(h, a0, y0), self.shell(h, a1, y0), self.shell(h, a1, y1), self.shell(h, a0, y1)]
                        f = v.facing(self.normal(h, (a0 + a1) / 2, (y0 + y1) / 2)) > -0.05
                        (scalp_f if f else scalp_b).append(v.many(q))
        if self.k.get('cap', True) and self.k['bald'] is None:
            # the crown: the shell's top ring as one piece
            top = [self.shell(h, a, h.top + 0.004) for a in range(-180, 180, 15)]
            scalp_f.append(v.many(top))
        for q in (self.k.get('quads3') or []):
            c = [sum(p[i] for p in q) / 4 for i in range(3)]
            f = v.facing((c[0] * 2, 0.2, 0.8)) > -0.1
            if f:
                scalp_f.append(v.many(q))
        self._scalp = (scalp_b, scalp_f)
        for L in (self.k['locks'] or []):
            pts = L['pts']
            P = [(p, (math.degrees(math.atan2(p[0], p[2] + 0.05)), p[1]), j / (len(pts) - 1)) for j, p in enumerate(pts)]
            (front if L.get('layer', 'front') == 'front' else back).append((P, dict(w=L.get('w', 0.06), key=-1, taper=L.get('taper'))))
        self._cache = (h, v, (back, front))
        return back, front

    def _ribbon(self, v, piece, s, scale=1.0):
        pts = [v(p) for p, _, _ in piece]
        ts = [t for _, _, t in piece]
        W = s['w'] * v.s * scale
        def wf(u):
            t = ts[0] + (ts[-1] - ts[0]) * u
            # wide at the root, a point at the tip
            return W * (0.55 + 0.45 * math.sin(min(1, t * 1.5) * math.pi / 2)) * (1 - t ** 3) ** 0.8 + 0.6
        tp = s.get('taper') or ((0.0 if ts[0] > 0.05 else 0.08), (0.25 if ts[-1] > 0.95 else 0.0))
        if s.get('root_end'):
            wf0 = wf
            wf = lambda u: wf0(1 - u)
            tp = ((0.25 if ts[0] < 0.05 else 0.0), 0.0)
        return stroke(pts, wf, taper=tp, n=2)

    def _mass(self, v, pieces, scale=1.0, cap=False):
        m = ''.join(self._ribbon(v, p, s, scale) for p, s in pieces)
        quads = self._scalp[1 if cap else 0]
        if quads:
            m = ''.join(f'<path d="{poly(q)}" fill="{INK}" stroke="{INK}" stroke-width="1.2"/>' for q in quads) + m
        return m

    def _layer(self, h, v, lw, pieces, front):
        if not pieces and not self._scalp[1 if front else 0]:
            return ''
        mode = self.k['mode']
        cap = front
        mass = self._mass(v, pieces, cap=cap)
        md = mass.replace(f' fill="{INK}" stroke="{INK}" stroke-width="1.2"', '').replace(f' fill="{INK}"', '')
        mid = uid('hd')
        cid = uid('hm')
        U = lambda attrs: f'<use href="#{mid}" {attrs}/>'
        out = [f'<defs><g id="{mid}">{md}</g></defs><mask id="{cid}" maskUnits="userSpaceOnUse" x="-9999" y="-9999" width="29999" height="29999"><use href="#{mid}" fill="#fff" stroke="#fff" stroke-width="1.2"/></mask>']
        INKS = f'fill="{INK}" stroke="{INK}" stroke-width="1.2"'
        PAPS = f'fill="{PAPER}" stroke="{PAPER}" stroke-width="1.2"'
        rnd = random.Random(self.k['seed'] + (1 if front else 2))
        if mode in ('black', 'tone'):
            if mode == 'black':
                out.append(U(INKS))
            else:
                o = lw * 0.5
                out.append(U(INKS + f' transform="translate({o:.1f},{o:.1f})"') + U(INKS + f' transform="translate({-o*0.5:.1f},{-o*0.5:.1f})"'))
                tid = tone_id(self.k['tone_level'] or 0.3)
                out.append(U(PAPS))
                out.append(U(f'fill="url(#{tid})"'))
            inner = []
            # streaks of light: white tapered lines along the locks where the shell faces the light
            Lx, Ly, Lz = LIGHT3
            for p, s in pieces:
                if rnd.random() > 0.55 * self.k['streaks']:
                    continue
                seg = []
                for q, (a, y), t in p:
                    nn = v.rot(self.normal(h, a, y))
                    lit = nn[0] * Lx + nn[1] * Ly + nn[2] * Lz
                    seg.append((v(q), lit, t))
                # one streak per lock where it is lit most
                best = max(range(len(seg)), key=lambda i: seg[i][1])
                if seg[best][1] < 0.15:
                    continue
                i0 = max(0, best - rnd.randint(0, 1)); i1 = min(len(seg) - 1, best + rnd.randint(1, 2))
                if i1 - i0 < 1:
                    continue
                line = [seg[i][0] for i in range(i0, i1 + 1)]
                off = rnd.uniform(-0.3, 0.3) * s['w'] * v.s
                line = [(x + off, y) for x, y in line]
                inner.append(stroke(line, lw * rnd.uniform(0.45, 0.9), taper=(0.45, 0.45), fill=PAPER))
            # fine separations between locks: thin white lines from the roots
            for p, s in pieces:
                if rnd.random() > 0.35 * self.k['flow']:
                    continue
                pts = [v(q) for q, _, _ in p]
                if len(pts) < 3:
                    continue
                k0 = rnd.randint(0, max(0, len(pts) // 3))
                k1 = min(len(pts), k0 + rnd.randint(3, 6))
                if k1 - k0 < 2:
                    continue
                inner.append(stroke(pts[k0:k1], lw * (0.35 if mode == 'black' else 0.4), taper=(0.5, 0.5), fill=PAPER if mode == 'black' else INK))
            if self.k.get('curls'):
                xs, ys = [], []
                for p, s in pieces:
                    for q, _, _ in p:
                        X, Y = v(q); xs.append(X); ys.append(Y)
                for i in range(self.k['curls']):
                    X = rnd.uniform(min(xs), max(xs)); Y = rnd.uniform(min(ys), max(ys))
                    r = v.s * rnd.uniform(0.010, 0.02)
                    a0 = rnd.uniform(0, 6.28)
                    arc = [(X + r * math.cos(a0 + t), Y + r * math.sin(a0 + t) * 0.8) for t in [k * 0.5 for k in range(5)]]
                    inner.append(stroke(arc, lw * rnd.uniform(0.4, 0.65), taper=(0.4, 0.4), fill=PAPER))
            out.append(f'<g mask="url(#{cid})">{"".join(inner)}</g>')
        else:
            # white (or toned) mass with an outline heavier to the lower right: a black copy moved there under it
            o = lw * 0.55
            out.append(U(INKS + f' transform="translate({o:.1f},{o:.1f})"'))
            out.append(U(INKS + f' transform="translate({-o*0.6:.1f},{-o*0.6:.1f})"'))
            out.append(U(PAPS))
            inner = []
            if self.k['tone_level'] > 0:
                inner.append(f'<rect x="-5000" y="-5000" width="10000" height="10000" fill="url(#{tone_id(self.k["tone_level"])})"/>')
            Lx, Ly, Lz = LIGHT3
            for p, s in pieces:
                pts = []
                for q, (a, y), t in p:
                    nn = v.rot(self.normal(h, a, y))
                    lit = nn[0] * Lx + nn[1] * Ly + nn[2] * Lz
                    pts.append((v(q), lit))
                if len(pts) < 3:
                    continue
                # flow lines: more and longer in the shadow
                nlines = 1 if rnd.random() < self.k['flow'] else 0
                for _ in range(nlines):
                    off = rnd.uniform(-0.4, 0.4) * s['w'] * v.s
                    dark = [i for i, (_, lit) in enumerate(pts) if lit < rnd.uniform(0.15, 0.55)]
                    if len(dark) < 2:
                        k0 = rnd.randint(0, len(pts) - 2); k1 = min(len(pts), k0 + 3)
                        seg = [pts[i][0] for i in range(k0, k1)]
                        if rnd.random() < 0.5:
                            continue
                    else:
                        seg = [pts[i][0] for i in range(dark[0], dark[-1] + 1)]
                    if len(seg) < 2:
                        continue
                    seg = [(x + off, y) for x, y in seg]
                    inner.append(stroke(seg, lw * rnd.uniform(0.3, 0.55), taper=(0.35, 0.4)))
            out.append(f'<g mask="url(#{cid})">{"".join(inner)}</g>')
        return ''.join(out)

    def hairline_mask(self, h, v):
        """Not needed: the locks end at the hairline themselves."""
        return ''

    def back(self, h, v, lw):
        b, f = self._pieces(h, v)
        s = self._layer(h, v, lw, b, False)
        if self.k['bun'] and v.facing(self.k['bun']['dir']) <= 0.25:
            s += self.draw_bun(h, v, lw)
        return s

    def front(self, h, v, lw):
        b, f = self._pieces(h, v)
        s = ''
        if self.k['bun'] and v.facing(self.k['bun']['dir']) > 0.25:
            s += self.draw_bun(h, v, lw)
        return s + self._layer(h, v, lw, f, True)

    def draw_bun(self, h, v, lw):
        B = self.k['bun']
        c = B['c']; r = B['r']
        rnd = random.Random(11)
        out = []
        ring = [v((c[0] + r * math.cos(t) * B.get('sx', 1.0), c[1] + r * math.sin(t), c[2] - r * 0.3 * abs(math.cos(t)))) for t in [2 * math.pi * i / 24 for i in range(24)]]
        cx = sum(p[0] for p in ring) / 24; cy = sum(p[1] for p in ring) / 24
        R = r * v.s
        body = f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(R)}" fill="{INK}"/>'
        for i in range(9):
            a0 = rnd.uniform(0, 6.28)
            arc = [(cx + R * 0.8 * math.cos(a0 + t) * (0.5 + 0.5 * t / 2.5), cy + R * 0.8 * math.sin(a0 + t) * (0.5 + 0.5 * t / 2.5)) for t in [k * 0.3 for k in range(8)]]
            out.append(stroke(arc, lw * 0.5, taper=(0.4, 0.4), fill=PAPER))
        return body + clip(f'M{cx-R} {cy}a{R} {R} 0 1 0 {2*R} 0a{R} {R} 0 1 0 {-2*R} 0', ''.join(out))
