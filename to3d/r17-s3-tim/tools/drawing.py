"""The drawing as numbers: the views' paths (views.py) sampled into polylines, and the silhouettes the 3D is fitted to.
Drawing units: the figure's own (eye line y=14, y down, soles at y=682); 3D: metres, y up, the figure faces +z, its
left +x. Front view: drawing x → 3D x; profile (faces right): drawing x → 3D z."""
import re
import numpy as np
import views as VW

FLOOR = VW.FLOOR        # shoe soles
CROWN = VW.CROWN        # the hair's highest spike
HEIGHT = 1.26           # metres, spike to soles: a boy of about 8, with a cartoon head
K = HEIGHT / (FLOOR - CROWN)


def sample(d, n=24):
    """An absolute SVG path (M L C Q Z) → list of closed/open polylines (arrays N×2)."""
    toks = re.findall(r'[MLCQZmlcqz]|-?\d+(?:\.\d+)?', d)
    out, cur, i, cmd, p0 = [], [], 0, None, None
    pos = np.zeros(2)
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd in 'Zz':
                if cur:
                    cur.append(cur[0].copy()); out.append(np.array(cur)); cur = []
                pos = p0.copy() if p0 is not None else pos
                continue
        if cmd == 'M':
            if cur: out.append(np.array(cur))
            pos = np.array([num(), num()]); p0 = pos.copy(); cur = [pos.copy()]; cmd = 'L'
        elif cmd == 'L':
            pos = np.array([num(), num()]); cur.append(pos.copy())
        elif cmd == 'C':
            c1 = np.array([num(), num()]); c2 = np.array([num(), num()]); e = np.array([num(), num()])
            for s in np.linspace(0, 1, n + 1)[1:]:
                cur.append((1 - s) ** 3 * pos + 3 * (1 - s) ** 2 * s * c1 + 3 * (1 - s) * s * s * c2 + s ** 3 * e)
            pos = e
        elif cmd == 'Q':
            c1 = np.array([num(), num()]); e = np.array([num(), num()])
            for s in np.linspace(0, 1, n + 1)[1:]:
                cur.append((1 - s) ** 2 * pos + 2 * (1 - s) * s * c1 + s * s * e)
            pos = e
        else:
            raise ValueError(cmd)
    if cur: out.append(np.array(cur))
    return out


def span(polys, y, ax=1):
    """Where a horizontal line at drawing-y (ax=1; a vertical one at x for ax=0) crosses the shapes: (min, max) or None."""
    xs = []
    for P in polys:
        a, b = P[:-1], P[1:]
        m = (a[:, ax] - y) * (b[:, ax] - y) <= 0
        for p, q in zip(a[m], b[m]):
            if p[ax] == q[ax]: xs += [p[1 - ax], q[1 - ax]]
            else: xs.append(p[1 - ax] + (y - p[ax]) / (q[ax] - p[ax]) * (q[1 - ax] - p[1 - ax]))
    return (min(xs), max(xs)) if xs else None


def profile(d, ys, n=24, ax=1):
    P = sample(d, n)
    r = [span(P, y, ax) for y in ys]
    return np.array([[np.nan, np.nan] if s is None else s for s in r])


def fillnan(a):
    a = np.asarray(a, float); i = np.arange(len(a)); ok = ~np.isnan(a)
    return np.interp(i, i[ok], a[ok])
