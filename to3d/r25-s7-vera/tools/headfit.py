"""The head: Blender's Human Base Meshes stylised head (CC0; hbm_export.py), its eye sockets and mouth closed (the
eyes, brows, nose mark and mouth of this style are drawn, not modelled), then fitted to the character's own head form of the drawing (С7):
heights piecewise by landmarks (neck, chin, eye line, crown); at each height the width and the front/back to the
drawing's ring (head.py of the style: half width a(y), front zf(y) with the middle profile — nose, lips, chin —, back
zb(y)); below the chin to the drawn neck tube; then the face itself laid onto the drawing's front surface (`surf`),
so the face is the drawing's flat round plane with its small nose, and the base gives the rest: jaw, neck, ears,
clean topology."""
import numpy as np
import mesh as M
import drawing as D

C0 = 2.082951545715332   # the bundle's head stands at x=2.083
H = D.HEAD


def conv(v):
    return np.c_[v[:, 0] - C0, v[:, 2], -v[:, 1]]


def load(path):
    d = np.load(path)
    v = conv(d['head_v']); P = M.polys_of(d['head_fs'], d['head_f']); vis = d['head_vis']
    eyes = [conv(d['L_v']).mean(0), conv(d['R_v']).mean(0)]
    r = (conv(d['L_v']).max(0) - conv(d['L_v']).min(0)).max() / 2
    return v, P, eyes, r, vis


def fill(v, P, loop, rings=4):
    """Close a hole: rings from its edge to its middle (quads), a fan in the centre."""
    v = list(v); c = np.mean([v[i] for i in loop], 0); n = len(loop)
    prev = list(loop); new = []
    for r in range(1, rings + 1):
        t = r / (rings + 1); cur = []
        for i in loop:
            v.append(v[i] * (1 - t) + c * t); cur.append(len(v) - 1)
        new += cur
        for k in range(n):
            P.append([prev[k], cur[k], cur[(k + 1) % n], prev[(k + 1) % n]][::-1])
        prev = cur
    v.append(c); ci = len(v) - 1; new.append(ci)
    for k in range(n): P.append([prev[k], ci, prev[(k + 1) % n]][::-1])
    return np.array(v), P, new


def compact(v, P):
    used = sorted(set(i for p in P for i in p)); m = -np.ones(len(v), int); m[used] = np.arange(len(used))
    return v[used], [[int(m[i]) for i in p] for p in P], m


def blank(v, P, vis, eyes, r):
    """Eye sockets and the mouth closed: the faces there that no ray from outside reaches (their linings) taken out,
    the holes filled. The neck's opening stays open."""
    fc = np.array([v[p].mean(0) for p in P])
    near = np.zeros(len(P), bool)
    for c in eyes: near |= np.linalg.norm(fc - c, axis=1) < r * 1.5
    near |= (abs(fc[:, 0]) < 0.06) & (fc[:, 1] > 0.55) & (fc[:, 1] < 0.70) & (fc[:, 2] > -0.0) & (fc[:, 2] < 0.14)
    # every lining no ray from outside reaches (sockets, mouth bag, nostrils), above the neck
    drop = set(np.where((vis == 0) & near)[0])
    P = [p for i, p in enumerate(P) if i not in drop]
    v, P, _ = compact(v, P)
    for L in M.boundary_loops(P):
        if v[L].mean(0)[1] < 0.54: continue
        v, P, _ = fill(v, P, L)
    # small holes left where the linings met the surface (the mouth's corners, the nostrils): each closed by a fan
    # from its middle, over its boundary edges as they run
    cnt = M.edges_of(P); half = []
    for p in P:
        for a, b in zip(p, p[1:] + p[:1]):
            if cnt[(min(a, b), max(a, b))] == 1: half.append((a, b))
    par = {}
    def root(x):
        while par.get(x, x) != x: x = par[x]
        return x
    for a, b in half: par[root(a)] = root(b)
    groups = {}
    for a, b in half: groups.setdefault(root(a), []).append((a, b))
    v = list(v)
    for g in groups.values():
        if np.mean([v[a][1] for a, _ in g]) < 0.54: continue
        c = len(v); v.append(np.mean([v[a] for a, _ in g], 0))
        for a, b in g: P.append([b, a, c])
    return np.array(v), P


def ears(v):
    return (abs(v[:, 0]) > 0.085) & (v[:, 2] > -0.05) & (v[:, 2] < 0.075) & (v[:, 1] > 0.64) & (v[:, 1] < 0.80)


# ---------------------------------------------------------------- the drawing's head, as targets (head-local units)
# base heights (its metres) → head-local y: neck's end (into the clothes), chin, eye line, crown
Y_BASE = [0.513, 0.575, 0.7287, 0.888]
Y_HEAD = [-1.42, -1.0, D.FACE['eye_y'], 1.0]


def neck_axis(y):
    """the drawn neck tube (neck0 → neck1, r 3.2 cm), in head-local units: centre z and radius at height y."""
    n0, n1 = ((D.J['neck0'] - D.HC) @ D.HR) / D.HK, ((D.J['neck1'] - D.HC) @ D.HR) / D.HK
    t = (y - n0[1]) / (n1[1] - n0[1])
    z = n0[2] + t * (n1[2] - n0[2])
    r = D.B['neck_r'] / D.HK * np.interp(t, [0, 1], [1.05, 1.0])
    return z, r


def targets(ys):
    """half width, front and back of the drawing's head at head-local heights (the ring with the cheek and the
    middle profile), joined below the jaw to the neck tube."""
    w, zf, zb = [], [], []
    for y in ys:
        nz, nr = neck_axis(y)
        if y > -0.999:
            R = H.ring(min(y, 0.999), nt=180)
            a, f, b = np.abs(R[:, 0]).max(), R[:, 2].max(), R[:, 2].min()
        else:
            a, f, b = 0.0, -9.0, 9.0
        if y < -0.35:     # the neck under the jaw and behind it (the nape)
            u = np.clip((-0.35 - y) / 0.4, 0, 1); u = u * u * (3 - 2 * u)
            a = max(a, nr)
            f = max(f, nz + nr) if y < -0.95 else f
            b = min(b, b * (1 - u) + (nz - nr) * u) if y > -0.999 else nz - nr
        w.append(a); zf.append(f); zb.append(b)
    return np.array(w), np.array(zf), np.array(zb)


def smooth01(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def _fillnan(a):
    i = np.arange(len(a)); ok = ~np.isnan(a)
    return np.interp(i, i[ok], a[ok])


def fit(v, earm):
    """The base head into the drawing's head. Returns head-local positions (x, y, z)."""
    y = np.interp(v[:, 1], Y_BASE, Y_HEAD)
    bins = np.arange(-1.44, 1.02, 0.03)
    w_c, zf_c, zb_c = [], [], []
    for b in bins:
        m = (abs(y - b) < 0.05) & ~earm
        if m.sum() < 3: w_c.append(np.nan); zf_c.append(np.nan); zb_c.append(np.nan); continue
        w_c.append(abs(v[m, 0]).max()); zf_c.append(v[m, 2].max()); zb_c.append(v[m, 2].min())
    w_c, zf_c, zb_c = map(lambda a: _fillnan(np.array(a)), (w_c, zf_c, zb_c))
    w_t, zf_t, zb_t = targets(bins)
    sm = lambda a: np.convolve(np.pad(a, 2, mode='edge'), np.ones(5) / 5, 'valid')
    kx = sm(w_t / np.maximum(w_c, 1e-4))
    zf_t, zb_t, zf_c, zb_c = sm(zf_t), sm(zb_t), sm(zf_c), sm(zb_c)
    x = v[:, 0] * np.interp(y, bins, kx)
    a, b = np.interp(y, bins, zb_c), np.interp(y, bins, zf_c)
    A, B = np.interp(y, bins, zb_t), np.interp(y, bins, zf_t)
    z = A + (v[:, 2] - a) / (b - a) * (B - A)
    L = np.c_[x, y, z]
    # the face onto the drawing's own front surface: where a point lies in front of the ring's middle and inside its
    # width, its depth becomes the drawing's (weight fading toward the sides, the chin's underside and the forehead)
    yy = np.clip(y, -0.999, 0.999)
    aa = np.maximum(H.a(yy), 1e-3); zm = H.zm(yy)
    r = np.abs(x) / aa
    front = (z > zm) & ~earm & (y > -1.0)
    s = H.surf(np.clip(x, -aa, aa), yy)
    wgt = (1 - smooth01((r - 0.72) / 0.28)) * smooth01((y + 0.985) / 0.06) * front
    L[:, 2] = z * (1 - wgt) + s * wgt
    return L, wgt


def place_ears(L, earm):
    """the base's ears, smaller, at the drawing's ear (`ear` heights, `ear_z` from the ring's middle)."""
    P = D.FACE
    ey0, ey1 = P['ear']; yc = (ey0 + ey1) / 2; hgt = ey0 - ey1
    for s in (1, -1):
        m = earm & (np.sign(L[:, 0]) == s)
        if not m.any(): continue
        E = L[m]
        c = np.array([E[:, 0].min() if s > 0 else E[:, 0].max(), E[:, 1].mean(), E[:, 2].mean()])
        k = hgt / (E[:, 1].max() - E[:, 1].min()) * 1.1
        root = np.array([s * (float(H.a(yc)) - 0.03), yc, float(H.zm(yc)) + P.get('ear_z', 0.0)])
        L[m] = root + (E - c) * [k * 0.8, k, k]
    return L


def build(path):
    """→ head-local vertices, polygons, ear mask, face weight (1 where the face is the drawing's surface)."""
    v, P, eyes, r, vis = load(path)
    v, P = blank(v, P, vis, eyes, r)
    earm = ears(v)
    L, wgt = fit(v, earm)
    L = place_ears(L, earm)
    # a little smoothing of the whole (the fit's seams), the ears and the open neck rim kept
    A = M.adjacency(len(L), P)
    bnd = L[:, 1] < -1.3
    L = M.smooth(L, A, ~earm & ~bnd & (wgt < 0.99), iters=3, lam=0.4)
    # the face relaxed on the drawing's surface: where the base had sockets and lips, laying them on one surface
    # leaves folds; spreading the points evenly over it (and back onto it) takes the folds out
    face = wgt > 0.3
    for _ in range(40):
        L = M.smooth(L, A, face, iters=1, lam=0.5)
        yy = np.clip(L[:, 1], -0.999, 0.999); aa = np.maximum(H.a(yy), 1e-3)
        s = H.surf(np.clip(L[:, 0], -aa, aa), yy)
        L[face, 2] = L[face, 2] * (1 - wgt[face]) + s[face] * wgt[face]
    # what the base kept inside (the mouth bag's and nostrils' remains joined to the holes' fills) out onto the form:
    # left inside, its triangles pierce the face
    yy = np.clip(L[:, 1], -0.98, 0.98); zm = H.zm(yy); aa = np.maximum(H.a(yy), 1e-3)
    df = np.where(L[:, 2] > zm, H.zf(yy) - zm, zm - H.zb(yy))
    rr = (np.abs(L[:, 0] / aa) ** H.n + np.abs((L[:, 2] - zm) / df) ** H.n) ** (1 / H.n)
    inside = (rr < 0.93) & ~earm & (L[:, 1] > -0.9) & (L[:, 1] < 0.95)
    L[inside, 0] /= rr[inside]; L[inside, 2] = zm[inside] + (L[inside, 2] - zm[inside]) / rr[inside]
    # the seam where the drawing's face meets the base's cheek and jaw, smoothed (no ridge on the outline)
    seam = (wgt > 0.01) & (wgt < 0.97) & ~earm & ~bnd
    L = M.smooth(L, A, seam, iters=12, lam=0.5)
    return L, P, earm, wgt
