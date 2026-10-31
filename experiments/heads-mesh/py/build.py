# python3 py/build.py name… → out/<name>.json: Anny's own head (topology, bones, weights) laid onto the head drawn in
# chars.py: her landmarks carried to the drawing's by one smooth warp, then every point of the head set on the drawn
# surface and evened out along it; the lids and the mouth cut along mesh edges; the lids opened onto the eyeballs
import sys, os, json, base64, heapq
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl
from scipy.interpolate import RBFInterpolator
from anny import base, person, wOf, JI
from target import Head, mono
from chars import CH

HERE = os.path.dirname(__file__); OUT = os.path.join(HERE, '..', 'out'); os.makedirs(OUT, exist_ok=True)
bs = base(); N = bs['N']; T = bs['tris']
used = np.zeros(N, bool); used[T.ravel()] = True
headW = wOf(bs, ['Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye']); jawW = wOf(bs, ['Jaw'])
rows = np.r_[T[:, 0], T[:, 1], T[:, 2], T[:, 1], T[:, 2], T[:, 0]]; cols = np.r_[T[:, 1], T[:, 2], T[:, 0], T[:, 0], T[:, 1], T[:, 2]]
A = sp.coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N)).tocsr(); A.data[:] = 1
deg = np.asarray(A.sum(1)).ravel(); Lavg = sp.diags(1 / np.maximum(deg, 1)) @ A
def diffuse(f, its):
    for _ in range(its): f = 0.5 * f + 0.5 * (Lavg @ f)
    return f
omega = diffuse(np.clip(headW * 1.3, 0, 1), 10)
NBR = [A.indices[A.indptr[i]:A.indptr[i + 1]] for i in range(N)]
sst = lambda t: (lambda c: c * c * (3 - 2 * c))(np.clip(t, 0, 1))

def anny_frame(at, J):
    eL, eR = J[JI['LeftEye']], J[JI['RightEye']]; E = (eL + eR) / 2
    m = used & (headW > .5) & (np.abs(at[:, 1] - E[1]) < 0.006) & (np.abs(at[:, 0]) < abs(eL[0]) * 1.2); ez = at[m, 2].max()
    m = used & (headW > .6) & (np.abs(at[:, 0]) < 0.006) & (at[:, 2] > ez - 0.06); i = np.where(m)[0][np.argmin(at[m, 1])]
    U = E[1] - at[i, 1]
    return dict(E=E, eL=eL, eR=eR, ez=ez, U=U, chinB=at[i].copy())

def edge_path(at, a, b, ok, follow=None):
    """the shortest run of mesh edges from a to b through points ok(i), never going back in x (so it can be laid along a curve)"""
    sx = np.sign(at[b, 0] - at[a, 0]); dist = {a: 0.0}; prev = {}; q = [(0.0, a)]
    while q:
        d, v = heapq.heappop(q)
        if v == b: break
        if d > dist.get(v, 1e9): continue
        for w in NBR[v]:
            if w != b and not ok(w): continue
            if (at[w, 0] - at[v, 0]) * sx <= 0: continue
            c = np.linalg.norm(at[w] - at[v]) * (1 + (follow(w) if follow else 0))
            if d + c < dist.get(w, 1e9): dist[w] = d + c; prev[w] = v; heapq.heappush(q, (d + c, w))
    p = [b]
    while p[-1] != a: p.append(prev[p[-1]])
    return p[::-1]

def cut(tris, path, at):
    """split the triangles around the path's inner points into the side above and below; the points get a copy for below"""
    inner = set(path[1:-1]); pe = set((min(u, v), max(u, v)) for u, v in zip(path, path[1:]))
    reg = [t for t in range(len(tris)) if inner & set(tris[t])]
    edges = {}
    for t in reg:
        for k in range(3):
            u, v = tris[t][k], tris[t][(k + 1) % 3]; e = (min(u, v), max(u, v))
            if e in pe: continue
            edges.setdefault(e, []).append(t)
    adj = {t: [] for t in reg}
    for ts in edges.values():
        for x in ts:
            for y in ts:
                if x != y: adj[x].append(y)
    comp = {}; groups = []
    for t in reg:
        if t in comp: continue
        g = [t]; comp[t] = len(groups); st = [t]
        while st:
            x = st.pop()
            for y in adj[x]:
                if y not in comp: comp[y] = len(groups); g.append(y); st.append(y)
        groups.append(g)
    assert len(groups) == 2, 'cut: %d groups' % len(groups)
    py = np.interp
    xs = at[path, 0]; order = np.argsort(xs)
    def above(g):
        c = at[tris[g]].mean(1); return np.mean(c[:, 1] - np.interp(c[:, 0], xs[order], at[path, 1][order]))
    lo = groups[0] if above(groups[0]) < above(groups[1]) else groups[1]
    return lo, sorted(inner)

def build(name):
    S = CH[name]; at, J = person(S['who'], bs); F = anny_frame(at, J); E, U = F['E'], F['U']
    H = Head(S); P = S
    # ———— where the drawn head sits: its cranium on hers ————
    m = used & (headW > .9) & (at[:, 1] > E[1] + 0.25 * U)
    X = at[m]; M = np.c_[X[:, 0] ** 2, X[:, 1] ** 2, X[:, 2] ** 2, X[:, 1], X[:, 2]]; c = np.linalg.lstsq(M, np.ones(len(X)), rcond=None)[0]
    cy, cz = -c[3] / (2 * c[1]), -c[4] / (2 * c[2]); g = 1 + c[1] * cy ** 2 + c[2] * cz ** 2; rA = np.sqrt(g / c[:3])
    Ct = np.array(P['cranium']['c']); Rt = np.array(P['cranium']['r'])
    Ut = rA[0] * P.get('size', 1.0) / Rt[0]
    O = np.array([0, cy, cz]) - Ut * Ct
    O[1] += P.get('lift', 0) * Ut
    toW = lambda p: O + Ut * np.asarray(p); toF = lambda w: (np.asarray(w) - O) / Ut
    # her neck, measured, joins the drawn head: the head's underside eases into it
    sec = []
    for yy in (F['chinB'][1] - 0.2 * U, F['chinB'][1] - 0.6 * U):
        k = used & (headW < 0.5) & (np.abs(at[:, 1] - yy) < 0.04 * U) & (np.abs(at[:, 0]) < 0.07) & (at[:, 2] > E[2] - 0.2)
        q = at[k]; sec.append([(q[:, 2].max() + q[:, 2].min()) / 2, yy, (q[:, 0].max() - q[:, 0].min()) / 2, (q[:, 2].max() - q[:, 2].min()) / 2])
    sec = np.array(sec); a_, b_ = toF([0, sec[1, 1], sec[1, 0]]), toF([0, sec[0, 1], sec[0, 0]])
    H.neck = dict(a=a_ - (b_ - a_) * 2.0, b=b_ + (b_ - a_) * 1.2, rx=sec[0, 2] * S.get('neckR', 1.0) / Ut, rz=sec[0, 3] * S.get('neckR', 1.0) / Ut, k=S.get('neckK', 0.2)); print('  neck', np.round(sec, 4).tolist(), 'Ut', Ut)
    # ———— her landmarks ————
    mid = np.where(used & (headW > .5) & (np.abs(at[:, 0]) < 0.0015) & (at[:, 2] > F['ez'] - 0.03))[0]
    mid = mid[np.argsort(-at[mid, 1])]; my, mz = at[mid, 1], at[mid, 2]
    sel = lambda lo, hi: (my < E[1] + hi * U) & (my > E[1] + lo * U)
    k = sel(-0.75, -0.2); tip = at[mid[k][np.argmax(mz[k])]]
    k = sel(-0.08, 0.2); nas = at[mid[k][np.argmin(mz[k])]]
    k = np.where(jawW[mid] > .5)[0][0]; seam = (at[mid[k]] + at[mid[k - 1]]) / 2
    k = sel(-1.0, (seam[1] - E[1]) / U - 0.12); chinF = at[mid[k][np.argmax(mz[k])]]
    k = sel(0.3, 0.6); fore = at[mid[k][np.argmin(np.abs(my[k] - E[1] - 0.45 * U))]]
    top = at[used & (headW > .9)][np.argmax(at[used & (headW > .9), 1])]
    back = at[used & (headW > .9)][np.argmin(at[used & (headW > .9), 2])]
    # the closed lids' lines and the lips' parting: runs of mesh edges between the corners
    front = lambda i: at[i, 2] > F['ez'] - 0.02 and headW[i] > .5
    def nearest(p, ok):
        d = np.linalg.norm(at[:, :2] - p[:2], axis=1); d[~ok] = 9; return int(np.argmin(d))
    aw = 0.142 * U; eyes = []
    for eJ in (F['eL'], F['eR']):
        okf = used & (at[:, 2] > eJ[2]) & (headW > .5)
        ly = eJ[1] - 0.0125 * U
        a = nearest(np.array([eJ[0] - np.sign(eJ[0]) * aw, ly]), okf); b = nearest(np.array([eJ[0] + np.sign(eJ[0]) * aw, ly]), okf)
        ok = lambda i, eJ=eJ: at[i, 2] > eJ[2] and abs(at[i, 1] - ly) < 0.06 * U and abs(at[i, 0] - eJ[0]) < aw * 1.1
        pth = edge_path(at, a, b, ok, follow=lambda i, eJ=eJ: 40 * abs(at[i, 1] - ly) / U)
        eyes.append(dict(J=eJ, path=pth, inner=a, outer=b))
    bnd = np.array([jawW[i] >= .5 and any(jawW[j] < .5 for j in NBR[i]) for i in range(N)])
    okm = used & (at[:, 2] > F['ez'] - 0.03) & bnd & (np.abs(at[:, 1] - seam[1]) < 0.12 * U)
    mw = S.get('annyMouthW', 0.125) * U
    ma = nearest(np.array([-mw, seam[1]]), okm); mb = nearest(np.array([mw, seam[1]]), okm)
    mpath = edge_path(at, ma, mb, lambda i: front(i) and abs(at[i, 1] - seam[1]) < 0.1 * U, follow=lambda i: 0 if bnd[i] else 3)
    # ears: the farthest-out points beside the head, between the eyes' and the mouth's heights
    ears = []
    for sx in (1, -1):
        k = used & (headW > .5) & (at[:, 0] * sx > 0) & (at[:, 1] < E[1]) & (at[:, 1] > seam[1]) & (at[:, 2] < E[2] - 0.02)
        ears.append(at[k][np.argmax(np.abs(at[k, 0]))])
    # ———— the drawing's landmarks ————
    T_ = {}
    ex, ey, ez_ = S['eye']['x'], S['eye']['y'], S['eye']['z']; rB = S['eye']['r']
    zsurf = lambda x, y: H.rayz(np.array([[x, y]]))[0]
    pairs = []
    def lm(a_w, t_f, w=1.0): pairs.append((np.asarray(a_w, float), toW(t_f)))
    lm(nas, [0, S['nose']['root'][0], zsurf(0, S['nose']['root'][0])])
    lm(tip, [0, S['nose']['tip'][0], zsurf(0, S['nose']['tip'][0])])
    ly = S['lips']['y']; lm(seam, [0, ly, zsurf(0, ly)])
    cfy = S['face'].get('chinFrontY', -0.9); lm(chinF, [0, cfy, zsurf(0, cfy)])
    lm(F['chinB'], [0, H.chinY, S['face']['chinZ'] - 0.04])
    lm(fore, [0, 0.45, zsurf(0, 0.45)])
    cr = S['cranium']; lm(top, np.array(cr['c']) + [0, cr['r'][1], 0]); lm(back, np.array(cr['c']) - [0, 0, cr['r'][2]])
    # each lid's line: its points spread evenly between the drawn eye's corners
    sh = S['eye']
    for ei, e in enumerate(eyes):
        sx = 1 if e['J'][0] > 0 else -1
        # the corners stay on the ball's front (beyond ~3/4 of its radius the lids would show its side as a white wedge)
        inX = max(sh['inX'], ex - sh.get('cornerIn', 0.72) * rB); outX = min(sh['outX'], ex + sh.get('cornerOut', 0.8) * rB)
        cin = np.array([sx * inX, sh['inY']]); cout = np.array([sx * outX, sh['outY']])
        pth = e['path']; L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(at[pth], axis=0), axis=1))]; s = L / L[-1]; s = (1 - np.cos(np.pi * s)) / 2
        e['s'] = s; e['cin'], e['cout'] = cin, cout
        for k2 in range(0, len(pth), 1):
            q = cin + (cout - cin) * s[k2]; z = zsurf(*q); lm(at[pth[k2]], [q[0], q[1], z])
        lm(e['J'], [sx * ex, ey, ez_])
    # the lips' parting along the drawn mouth's line
    Lp = S['lips']; mcurve = lambda x: Lp['y'] + Lp.get('smile', 0) * (x / Lp['w']) ** 2
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(at[mpath], axis=0), axis=1))]; ms = L / L[-1]
    for k2 in range(len(mpath)):
        x = (2 * ms[k2] - 1) * Lp['w'] * Lp.get('corner', 0.92); lm(at[mpath[k2]], [x, mcurve(x), zsurf(x, mcurve(x))])
    for sx, ea in zip((1, -1), ears):
        ey_, ezz = S.get('ear', [-0.3, -0.75])
        # the side of the drawn head there, and the ear standing out of it as much as hers
        xs = np.linspace(2, 0, 400); pts = np.c_[sx * xs, np.full(400, ey_), np.full(400, ezz)]; v = H.f(pts); kk = np.argmax(v < 0)
        lm(ea, [sx * xs[kk] + sx * 0.012 / Ut, ey_, ezz])
    # far points stay: the neck, the shoulders
    fa = np.where(used & (omega < 0.02) & (np.linalg.norm(at - E, axis=1) < 0.3))[0][::7]
    src = np.array([p[0] for p in pairs] + list(at[fa])); dst = np.array([p[1] for p in pairs] + list(at[fa]))
    rbf = RBFInterpolator(src, dst - src, kernel='thin_plate_spline', smoothing=1e-7)
    act = np.where(used & (omega > 0.001))[0]
    earw = np.zeros(N)
    for ea in ears: earw = np.maximum(earw, sst((0.32 * U - np.linalg.norm(at - ea, axis=1)) / (0.12 * U)))
    # her face's own folds (nostrils, the lips' crease, the lids) smoothed away first: the drawn surface replaces them
    sm = at.copy(); ws = (sst((omega - 0.5) / 0.4) * (1 - earw))[:, None]
    for _ in range(S.get('presmooth', 30)): sm = sm + 0.5 * ws * ((Lavg @ sm) - sm)
    pw = sm.copy(); pw[act] += rbf(at[act]) * sst(omega[act] / 0.3)[:, None]
    # ———— set on the drawn surface ————
    wp = sst((omega - 0.02) / S.get('wpRamp', 0.15)) * (1 - earw)
    pin = np.zeros(N, bool); pin[mpath] = True
    for e in eyes: pin[e['path']] = True
    on = np.where(used & (wp > 0))[0]
    # every point that follows the drawing is set on it and evened out along it (the pinned lines stay); then each
    # point takes its share of that (all of it on the head, fading down the neck)
    sp_ = pw.copy(); sp_[on] = toW(H.project(toF(pw[on])))
    full = np.where(used & (wp > 0) & ~pin)[0]
    for it in range(S.get('relax', 40)):
        avg = (Lavg @ sp_)[full]; d = avg - sp_[full]
        sp_[full] = toW(H.project(toF(sp_[full] + 0.6 * d), 6))
    pos = pw.copy(); pos[on] = pw[on] + (sp_[on] - pw[on]) * wp[on, None]
    # ———— the lids: cut and opened onto the balls ————
    tris = T.copy(); extra = []; dupOf = {}
    def apply_cut(path):
        lo, inner = cut(tris, path, pos)
        mp = {}
        for v in inner: mp[v] = N + len(extra); extra.append(v)
        for t in lo:
            for k2 in range(3):
                if tris[t, k2] in mp: tris[t, k2] = mp[tris[t, k2]]
        return mp
    for e in eyes: e['dup'] = apply_cut(e['path'])
    mdup = apply_cut(mpath)
    M = N + len(extra); P2 = np.vstack([pos, pos[extra]])
    # the cut mesh's neighbours
    r2 = np.r_[tris[:, 0], tris[:, 1], tris[:, 2], tris[:, 1], tris[:, 2], tris[:, 0]]; c2 = np.r_[tris[:, 1], tris[:, 2], tris[:, 0], tris[:, 0], tris[:, 1], tris[:, 2]]
    A2 = sp.coo_matrix((np.ones(len(r2)), (r2, c2)), shape=(M, M)).tocsr(); A2.data[:] = 1
    balls = []; lidmoved = np.zeros(M, bool)
    for e in eyes:
        sx = 1 if e['J'][0] > 0 else -1; cB = toW([sx * ex, ey, ez_]); rw = rB * Ut
        pth = e['path']; up = sh['up']; lo_ = sh['lo']
        cin, cout = e['cin'], e['cout']
        def curve(s, h, peak):
            q = cin + (cout - cin) * s; u = np.where(s < peak, s / peak, (1 - s) / (1 - peak)) ; return q + [0, h * np.sin(np.pi / 2 * u) ** sh.get('round', 0.9)]
        fixed = {}
        for k2, v in enumerate(pth):
            s = e['s'][k2]
            if k2 in (0, len(pth) - 1): fixed[v] = curve(s, 0, 0.5); continue
            fixed[v] = curve(s, up, sh.get('peakUp', 0.45)); fixed[e['dup'][v]] = curve(s, -lo_, sh.get('peakLo', 0.55))
        # the lids open column by column along the eye's line: in each column the band from the line out to Hd is
        # stretched so the line lands on the curve (above for the upper lid, below for the lower), the band's far edge
        # stays — monotone in every column, so nothing crosses into the opening and nothing folds
        cur = toF(P2); ax_ = cout - cin; Lx = np.linalg.norm(ax_); ux = ax_ / Lx; uy = np.array([-ux[1], ux[0]]); uy = uy if uy[1] > 0 else -uy
        loc = cur[:, :2] - cin; S_ = (loc @ ux) / Lx; Y_ = loc @ uy
        Hd = sh.get('band', 1.32 * rB); fx = cur[:, 2] > ez_ - rB * 0.2
        def hgt(s_, h, peak):
            s2 = np.clip(s_, 1e-6, 1 - 1e-6); u_ = np.where(s2 < peak, s2 / peak, (1 - s2) / (1 - peak)); v_ = h * np.sin(np.pi / 2 * u_) ** sh.get('round', 0.9)
            return np.where((s_ > 0) & (s_ < 1), v_, 0)
        upper = np.zeros(M, bool); lower = np.zeros(M, bool)
        for v in pth[1:-1]: upper[v] = True; lower[e['dup'][v]] = True
        isd = np.zeros(M, bool); isd[list(e['dup'].values())] = True; isp = np.zeros(M, bool); isp[pth] = True
        band = fx & (Y_ < Hd) & (Y_ > -sh.get('bandLoH', 0.95 * rB)) & (S_ > -sh.get('endIn', 0.15)) & (S_ < 1 + sh.get('endOut', 0.15)) & ~isp & ~isd & (H.nose(cur) > 0.04)
        hu = hgt(S_, up, sh.get('peakUp', 0.45)); hl = hgt(S_, lo_, sh.get('peakLo', 0.55))
        # which lid each band point belongs to: the side of the cut itself (the path's own polyline, which runs along the
        # mesh's edges), not of the straight line between the corners
        ps_ = S_[pth]; py_ = Y_[pth]; o_ = np.argsort(ps_)
        Yc = Y_ - np.interp(S_, ps_[o_], py_[o_], left=0, right=0) * ((S_ > 0) & (S_ < 1))
        inS = band & (S_ > 0) & (S_ < 1)
        up_side = band & (Yc >= 0)
        lo_side = band & ~up_side
        eps = 0.03 * Hd; soft = lambda y: np.where(y > eps, y, eps * np.exp(np.minimum(y, eps) / eps - 1))
        Yn = Y_.copy(); HL = sh.get('bandLoH', 0.95 * rB)
        yu = np.where(inS, soft(Yc), Yc); yl = np.where(inS, soft(-Yc), -Yc)
        m1 = up_side; Yn[m1] = hu[m1] + yu[m1] * (Hd - hu[m1]) / Hd
        m2 = lo_side; Yn[m2] = -hl[m2] - yl[m2] * (HL - hl[m2]) / HL
        m3 = upper; Yn[m3] = hu[m3]; m4 = lower; Yn[m4] = -hl[m4]
        moved = np.where(band | upper | lower)[0]; lidmoved[moved] = True
        cur[moved, :2] = cin + np.outer(S_[moved] * Lx, ux) + np.outer(Yn[moved], uy)
        pr = H.project(cur[moved], 10)
        # near the rim the lid lies on the ball (a skin's thickness out), easing into the drawn surface across the band
        cBf = np.array([sx * ex, ey, ez_])
        def onsphere(q, R):
            # straight back onto the ball's front (x and y kept, so the opening keeps its drawn shape)
            dxy = q[:, :2] - cBf[:2]; r2 = R * R - (dxy ** 2).sum(1); ok = r2 > 0
            o_ = q.copy(); o_[ok, 2] = cBf[2] + np.sqrt(r2[ok]); return o_, ok
        P2[moved] = toW(pr)
        fixed = {v: None for v in list(pth) + list(e['dup'].values())}
        # the lid's rims (and the corners) tuck onto the ball; the move spreads smoothly over the lids around them
        # (a harmonic field: each point the mean of its neighbours, nothing beyond the band moves)
        rv = np.array(list(fixed.keys())); q_, okr = onsphere(toF(P2[rv]), rB + sh.get('rim', 0.008))
        disp = np.zeros((M, 3)); disp[rv[okr]] = toW(q_[okr]) - P2[rv[okr]]
        isfix = np.zeros(M, bool); isfix[rv] = True
        free = np.where(band & ~isfix)[0]; nbr = [A2.indices[A2.indptr[v]:A2.indptr[v + 1]] for v in free]
        for _ in range(sh.get('spread', 150)):
            disp[free] = np.array([disp[nb].mean(0) for nb in nbr])
        P2 += disp
        # the lids evened out (tangentially: each point toward its neighbours' mean, then back onto the surface or the
        # ball, whichever is in front), so a crowded corner does not crumple
        sm_ = np.where(fx & (np.abs(Y_) < Hd) & (S_ > -0.3) & (S_ < 1.3) & ~isfix)[0]; nb_ = [A2.indices[A2.indptr[v]:A2.indptr[v + 1]] for v in sm_]
        for _ in range(sh.get('even', 30)):
            avg = np.array([P2[nb].mean(0) for nb in nb_]); q = toF(P2[sm_] + 0.5 * (avg - P2[sm_]))
            qs = H.project(q, 4); qb, okq = onsphere(qs, rB + sh.get('lid', 0.02)); qs[okq, 2] = np.maximum(qs[okq, 2], qb[okq, 2])
            P2[sm_] = toW(qs)
        rimU = toF(P2[list(pth[1:-1])]); rimL = toF(P2[list(e['dup'].values())])
        print('  eye', sx, 'rim up y %.2f..%.2f, low y %.2f, x %.2f..%.2f' % (rimU[:, 1].min(), rimU[:, 1].max(), rimL[:, 1].min(), rimU[:, 0].min(), rimU[:, 0].max()), 'n', len(pth))
        balls.append(dict(c=cB.tolist(), r=rw))
    # ———— one even subdivision: each edge's middle on the drawn surface where both its ends are, so the shading is smooth
    # (the new points take their bones' weights from the edge's ends: the mesh still moves as hers) ————
    onT = np.zeros(M, bool); onT[:N] = (wp > 0.98) & used; onT[N:] = onT[np.array(extra, int)] if extra else []
    onT &= ~lidmoved
    E2 = np.sort(np.r_[tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]], axis=1); uE, inv = np.unique(E2, axis=0, return_inverse=True)
    mids = (P2[uE[:, 0]] + P2[uE[:, 1]]) / 2; both = onT[uE[:, 0]] & onT[uE[:, 1]]
    if both.any(): mids[both] = toW(H.project(toF(mids[both]), 8))
    nT = len(tris); mi = M + inv.reshape(3, nT).T  # middles of edges (01, 12, 20)
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]; m01, m12, m20 = mi[:, 0], mi[:, 1], mi[:, 2]
    tris = np.r_[np.c_[a, m01, m20], np.c_[m01, b, m12], np.c_[m20, m12, c], np.c_[m01, m12, m20]]
    P2 = np.vstack([P2, mids]); subEdges = uE; M0 = M; M = len(P2)
    if os.environ.get('DBG'):
        Fp = toF(P2); Pt = Fp[tris]; nz = np.cross(Pt[:, 1] - Pt[:, 0], Pt[:, 2] - Pt[:, 0])[:, 2]; ct = Pt.mean(1)
        for e in eyes:
            sx = 1 if e['J'][0] > 0 else -1
            k = np.where((nz < 0) & (np.abs(ct[:, 0] - sx * ex) < 0.45) & (np.abs(ct[:, 0]) > 0.12) & (np.abs(ct[:, 1] - ey) < 0.3) & (ct[:, 2] > -0.3))[0]
            print('  eye', sx, 'flipped (front view):', len(k), np.round(ct[k][:20], 3).tolist(), 'corners', e['cin'], e['cout'])
    # ———— nothing of the face inside the balls: a point closer than the lid's thickness is pushed out onto it ————
    for bl in balls:
        cB_ = np.array(bl['c']); R_ = bl['r'] + sh.get('rim', 0.008) * Ut * 0.9
        dv = P2 - cB_; dd = np.linalg.norm(dv, axis=1); k = (dd < R_) & (dd > 1e-9)
        P2[k] = cB_ + dv[k] / dd[k, None] * R_
        # ———— check: triangles turned inside out against the drawn surface ————
    Pt = P2[tris]; nt = np.cross(Pt[:, 1] - Pt[:, 0], Pt[:, 2] - Pt[:, 0]); ct = Pt.mean(1)
    face_t = np.where((omega[np.minimum(tris, N - 1)].min(1) > 0.9) & (earw[np.minimum(tris, N - 1)].max(1) == 0) & (tris.max(1) < N))[0]
    gt = H.grad(toF(ct[face_t])); dots = (nt[face_t] * gt).sum(1) / (np.linalg.norm(nt[face_t], axis=1) * np.linalg.norm(gt, axis=1) + 1e-12)
    bad = face_t[dots < 0.2]
    print('  turned triangles', len(bad), np.round(toF(ct[bad])[:40], 2).tolist())
    globals()['_bad'] = bad
    # ———— colours: skin, the lips ————
    col = np.tile(np.array(hexc(S['skin'])), (M, 1))
    lipc = np.array(hexc(S.get('lip', '#c9786c')))
    Lp = S['lips']; cf = toF(P2)
    # lips: above and below the parting, within the mouth's width, fading at the edge
    xm = np.abs(cf[:, 0]) / (Lp['w'] * 1.02); yrel = cf[:, 1] - mcurve(cf[:, 0])
    inside = np.clip(1 - xm ** 4, 0, 1) * np.where(yrel > 0, sst((Lp['uh'] * Lp.get('ucol', 1.0) - yrel) / 0.025), sst((Lp['lh'] * Lp.get('lcol', 1.0) + yrel) / 0.025))
    inside *= (cf[:, 2] > H.Zf(cf[:, 1]) - 0.25)
    t = np.clip(inside, 0, 1) * Lp.get('tint', 0.8); col = col * (1 - t[:, None]) + lipc * t[:, None]
    out = dict(name=name, pos=b64(P2.astype(np.float32)), tris=b64(tris.astype(np.uint32)), col=b64(col.astype(np.float32)),
               eyes=balls, iris=S.get('iris', '#5a3a24'), gaze=S.get('gaze', [0, 0]), view=S.get('view', [0, 0.05]), roll=S.get('roll', 0), ref=S['ref'], crop=S.get('crop'),
               sub=b64(subEdges.astype(np.uint32)), M0=int(M0), frame=dict(O=O.tolist(), U=Ut, top=float(toW(np.array(S['cranium']['c']) + [0, S['cranium']['r'][1], 0])[1]), chin=float(toW([0, H.chinY, 0])[1])), M=int(M))
    json.dump(out, open(os.path.join(OUT, name + '.json'), 'w'))
    print(name, 'ok', 'M', M, 'Ut %.4f Ua %.4f' % (Ut, U))

def hexc(h): h = h.lstrip('#'); return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
def b64(a): return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()

if __name__ == '__main__':
    for n in sys.argv[1:]: build(n)
