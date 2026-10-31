# the drawn head: one smooth solid read off the picture, in face units (the eyes' line y=0, the chin's bottom y=-1,
# the front of the face at the eyes z=0; x to the character's left)
import numpy as np

def smin(a, b, k):
    if k <= 0: return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1); return b * (1 - h) + a * h - k * h * (1 - h)
def smax(a, b, k): return -smin(-a, -b, k)

def mono(K):
    """monotone cubic through [y, v] keys; flat beyond the ends"""
    P = np.array(sorted(K)); x, y = P[:, 0], P[:, 1]; n = len(x)
    if n == 1: return lambda q: np.full_like(np.asarray(q, float), y[0])
    d = np.diff(y) / np.diff(x); m = np.zeros(n); m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1): m[i] = 0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2
    for i in range(n - 1):
        if d[i] == 0: m[i] = m[i + 1] = 0; continue
        a, b = m[i] / d[i], m[i + 1] / d[i]; h = np.hypot(a, b)
        if h > 3: m[i], m[i + 1] = 3 * a / h * d[i], 3 * b / h * d[i]
    m[0] = m[-1] = 0
    def f(q):
        q = np.clip(np.asarray(q, float), x[0], x[-1]); i = np.clip(np.searchsorted(x, q) - 1, 0, n - 2)
        hh = x[i + 1] - x[i]; t = (q - x[i]) / hh; t2, t3 = t * t, t * t * t
        return (2 * t3 - 3 * t2 + 1) * y[i] + (t3 - 2 * t2 + t) * hh * m[i] + (-2 * t3 + 3 * t2) * y[i + 1] + (t3 - t2) * hh * m[i + 1]
    return f

def sdEll(p, c, r):
    q = (p - c) / r; k0 = np.linalg.norm(q, axis=1); k1 = np.linalg.norm(q / r, axis=1)
    return np.where(k1 < 1e-9, -min(r), k0 * (k0 - 1) / np.maximum(k1, 1e-9))
def sdCaps(p, a, b, ra, rb):
    a, b = np.asarray(a, float), np.asarray(b, float); ba = b - a; pa = p - a
    h = np.clip((pa @ ba) / (ba @ ba), 0, 1); return np.linalg.norm(pa - h[:, None] * ba, axis=1) - (ra + (rb - ra) * h)

class Head:
    def __init__(s, P):
        s.P = P
        f = P['face']
        s.W = mono(f['W']); s.Zf = mono(f['Z']); s.Dz = mono(f.get('D', [[0, 0.62]])); s.n = f.get('n', 2.2); s.Db = mono(f.get('B', [[0, 0.5]]))
        s.chinY = min(k[0] for k in f['W'])
        e = P['eye']; s.eyes = [np.array([sx * e['x'], e['y'], e['z']]) for sx in (1, -1)]; s.rB = e['r']
    def f(s, p):
        P = s.P; F = P['face']; x, y, z = p[:, 0], p[:, 1], p[:, 2]
        # the cranium
        c = P['cranium']; d = sdEll(p, np.array(c['c']), np.array(c['r']))
        # the face: at each height a rounded slice — half-width W, its front Z on the midline, its edge D behind the front,
        # closing behind at B (inside the cranium above, at the jaw's back below)
        W, Zf, Dz = s.W(y), s.Zf(y), s.Dz(y); zc = Zf - Dz; Db = s.Db(y)
        ax = np.abs(x) / W; az = np.where(z > zc, (z - zc) / Dz, (zc - z) / Db); q = (ax ** s.n + az ** s.n) ** (1 / s.n)
        df = (q - 1) * np.minimum(W, Dz)
        df = smax(df, y - F.get('top', 0.15), F.get('topK', 0.3))
        # under the jaw: from the chin's bottom back up to the jaw's angle
        B = np.array([s.chinY, F['chinZ']]); A = np.array(F['jaw'])  # (y, z)
        t = (A - B) / np.linalg.norm(A - B); nrm = np.array([t[1], -t[0]])
        du = (y - B[0]) * nrm[0] + (z - B[1]) * nrm[1]
        df = smax(df, du, F.get('chinK', 0.12))
        d = smin(d, df, P.get('kCF', 0.25))
        # cheeks, chin, brow: masses on the face
        for m in P.get('masses', []):
            for sx in ((1, -1) if m.get('pair') else (1,)):
                cc = np.array(m['c'], float) * [sx, 1, 1]; d = smin(d, sdEll(p, cc, np.array(m['r'])), m.get('k', 0.08))
        # the nose: a bridge from its root to the tip (through a bend), the tip, the wings, the underside to the lip
        N = P['nose']
        if N:
            root, mid, tip, sub = [np.array([0, *N[k]]) for k in ('root', 'mid', 'tip', 'sub')]
            rr, rm, rt = N['rRoot'], N['rMid'], N['rTip']
            dn = smin(sdCaps(p, root, mid, rr, rm), sdCaps(p, mid, tip - [0, 0, rt * 0.6], rm, rt * 0.75), 0.03)
            dn = smin(dn, sdEll(p, tip - [0, 0, rt * 0.55], np.array([rt * N.get('tipW', 1.0), rt * N.get('tipH', 0.9), rt])), N.get('kTip', 0.04))
            wg = N.get('wing')
            if wg:
                for sx in (1, -1): dn = smin(dn, sdEll(p, np.array([sx * wg[0], wg[1], wg[2]]), np.array(wg[3])), 0.03)
            dn = smin(dn, sdCaps(p, tip - [0, rt * 0.4, rt * 0.5], sub, rt * 0.55, N.get('rSub', 0.03)), 0.07)
            d = smin(d, dn, N.get('k', 0.06)); s._dn = dn
        # the lips: gentle masses above and below the parting, the parting a thin groove along the mouth's curve
        L = P['lips']
        if L:
            my, w = L['y'], L['w']
            def front(xq, yq):
                W_, Z_, D_ = s.W(yq), s.Zf(yq), s.Dz(yq); return Z_ - D_ + D_ * np.clip(1 - (np.abs(xq) / W_) ** s.n, 0, 1) ** (1 / s.n)
            R = L.get('depth', 0.14)
            for key, sy in (('uh', 1), ('lh', -1)):
                h = L[key]; dz_ = L['ud' if sy > 0 else 'ld']
                if dz_ <= 0: continue
                yc = my + sy * h * 0.5; c = np.array([0, yc, float(front(0, yc)) - R + dz_])
                d = smin(d, sdEll(p, c, np.array([w * (0.9 if sy > 0 else L.get('lw', 0.8)), h * 0.75, R])), L.get('k', 0.07))
            gr = L.get('groove', 0.012)
            if gr > 0 and not getattr(s, '_nogroove', False):
                xs = np.linspace(-w * L.get('corner', 0.92), w * L.get('corner', 0.92), 9); ys = my + L.get('smile', 0) * (xs / w) ** 2
                if not hasattr(s, '_gz'):
                    s._nogroove = True; s._gz = s.rayz(np.c_[xs, ys]); del s._nogroove
                zs = s._gz + L.get('gz', 0.0); g = 9.0
                for i in range(8):
                    ra = gr * np.sin(np.pi * (i / 8)) ** 0.7; rb = gr * np.sin(np.pi * ((i + 1) / 8)) ** 0.7
                    g = np.minimum(g, sdCaps(p, [xs[i], ys[i], zs[i]], [xs[i + 1], ys[i + 1], zs[i + 1]], ra, rb))
                d = smax(d, -g, gr * 0.8)
        # the neck (hers, measured), joined smoothly under the jaw
        nk = getattr(s, 'neck', None)
        if nk is not None:
            sc = np.array([1, 1, nk['rx'] / nk['rz']]); dn_ = sdCaps(p * sc, nk['a'] * sc, nk['b'] * sc, nk['rx'], nk['rx'])
            d = smin(d, dn_, nk['k'])
        # the eyes' balls under the lids
        sk = P['eye'].get('skin', 0.03)
        for E in s.eyes: d = smin(d, np.linalg.norm(p - E, axis=1) - (s.rB + sk), P['eye'].get('k', 0.08))
        return d
    def nose(s, p):
        s.f(p); return s._dn
    def grad(s, p, h=1e-3):
        g = np.zeros_like(p)
        for k in range(3):
            e = np.zeros(3); e[k] = h; g[:, k] = (s.f(p + e) - s.f(p - e)) / (2 * h)
        return g
    def project(s, p, its=12):
        p = p.copy()
        for _ in range(its):
            d = s.f(p); g = s.grad(p); g2 = np.maximum((g * g).sum(1), 1e-6); p -= (d / g2)[:, None] * g
        return p
    def rayz(s, xy, z0=2.0, z1=-1.5):
        """where a ray from the front, along -z, at (x, y) meets the surface"""
        xy = np.atleast_2d(xy).astype(float); n = len(xy); zs = np.linspace(z0, z1, 400)
        z = np.full(n, np.nan)
        for i in range(n):
            pts = np.c_[np.full(400, xy[i, 0]), np.full(400, xy[i, 1]), zs]; v = s.f(pts); k = np.argmax(v < 0)
            if v[k] >= 0: continue
            a, b = zs[k - 1], zs[k]
            for _ in range(30):
                m = (a + b) / 2
                if s.f(np.array([[xy[i, 0], xy[i, 1], m]]))[0] > 0: a = m
                else: b = m
            z[i] = (a + b) / 2
        return z
