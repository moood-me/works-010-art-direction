"""Марат's head (Klaus). The drawing has front, three-quarter and profile (styles/s2-klaus/tools/marat.py: head_front,
head34, head_side — 500×600 frames, the face's chin at y=444, the beard's bottom at 484, the hair's top at 86, eyes at
262). The outline numbers below are read from the front and the profile: a wide heavy head on a short thick neck.
The base head (base_head.py) is fitted to them; the drawing's masses are separate smooth solids (blobs.py): the broad
nose, the ears, the moustache, the beard round the jaw (balls set on the head's own surface and melted into one
mass), the cap of curls (balls on the skull, hardly melted — each a curl).
Everything is returned in metres, the chin at y=0, the face to +z."""
import numpy as np
import mesh as M, base_head as B, blobs as Bl

K = 0.001069            # metres per head unit: the figure is 835 units = 1.94 m, the head drawn at 0.46 of its frame
CH = 444.0
HBM = '/home/user/cache/to3d-r16-s2-marat/hbm.npz'


def U(p):
    p = np.asarray(p, float)
    return np.c_[p[..., 0] * K, (CH - p[..., 1]) * K, p[..., 2] * K].reshape(p.shape)


_Y = [112, 120, 136, 160, 200, 222, 254, 300, 340, 380, 410, 430, 444, 456, 490]
_HW = [0, 42, 64, 80, 89, 91, 92, 91, 86, 74, 66, 64, 64, 64, 66]
_FW = [86, 72, 54, 34, 14]                                   # the jaw at 340 … 444
_ZF = [-10, 34, 62, 84, 104, 110, 110, 107, 106, 104, 98, 88, 72, 54, 50]
_ZB = [-10, -48, -62, -70, -76, -77, -77, -75, -70, -64, -60, -60, -60, -60, -60]
DRAW_Y = [492.0, 444.0, 428.0, 384.0, 330.0, 262.0, 236.0, 112.0]


def spec():
    yd = np.arange(116, 488, 6.0)
    f = lambda a: np.interp(yd, _Y, a)
    fw = np.interp(yd, [340, 380, 410, 430, 444], _FW); fw[(yd < 340) | (yd > 444)] = np.nan
    return dict(K=K, chin=CH, draw_y=DRAW_Y, yd=yd, hw=f(_HW), fw=fw, zf=f(_ZF), zb=f(_ZB), start=(0.75, 0.8))


def fitted():
    v, P = B.base(HBM)
    T = M.triangulate(P)
    ear = B.ears_of(v)
    V = B.fit(v, T, ~ear[T].any(1), spec())
    A = M.adjacency(len(V), T)
    grow = ear.copy()
    for _ in range(2): grow = grow | (A @ grow > 0)
    V = M.smooth(V, A, grow * 1.0, iters=120, lam=0.5)
    V = M.smooth(V, A, np.ones(len(V)), iters=4, lam=0.5)
    yd = CH - V[:, 1] / K
    P = [p for p in P if (yd[p] < 476).all()]
    V, P, mm = B.compact(V, P)
    return V, P, ear[mm >= 0]


def face_z(V, N, x, y):
    p, _ = B.surface_point(V, N, x * K, (CH - y) * K)
    return p[2] / K


def in_beard(x, y):
    """Is the front-view place (units, x from the middle) under the beard? Above it: the cheeks' line from the ear's
    front down to under the nose (the drawing's beard top)."""
    ax = abs(x)
    top = np.interp(ax, [0, 14, 46, 60, 76, 84, 96], [344, 342, 336, 328, 318, 296, 266])
    return y > top


def forms(V, T):
    N = M.vertex_normals(V, T)
    z = lambda x, y: face_z(V, N, x, y)
    yd = CH - V[:, 1] / K; xu = V[:, 0] / K; zu = V[:, 2] / K
    out = {}
    # ears
    for name, sx in (('earL', 1), ('earR', -1)):
        x0 = 93
        an = np.linspace(-0.75 * np.pi, 0.62 * np.pi, 9)
        rimp = [(sx * (x0 + 10 + 7 * np.cos(a - 0.3)), 284 - 30 * np.sin(a) + (5 if a < -1.6 else 0), 2 - 20 * np.cos(a)) for a in an]
        c1, r1 = Bl.chain(rimp, [8, 8.5, 7, 6, 6, 6, 6.5, 6.5, 5], 26)
        c2, r2 = Bl.chain([(sx * (x0 - 2), 262, 8), (sx * (x0 - 1), 286, 6), (sx * (x0 - 1), 308, 8)], [13, 14, 11], 8)
        v, t = Bl.solid((np.r_[c1, c2], np.r_[r1, r2]), k=2.5, cell=2.0)
        out[name] = (U(v), t[:, ::-1])
    # the nose: broad, a round tip, wide wings
    zn = z(0, 322)
    b, r = Bl.chain([(0, 254, z(0, 254) + 1), (0, 284, z(0, 284) + 8), (0, 308, zn + 17), (0, 322, zn + 22)], [10, 13, 20, 25], 20)
    wings = np.array([(sx * 30, 328, zn + 8) for sx in (1, -1)])
    v, t = Bl.solid((np.r_[b, wings], np.r_[r, [20, 20]]), k=5, cell=2.5)
    out['nose'] = (U(v), t[:, ::-1])
    # the beard: balls on the head's surface under the beard's line, melted into one mass; fuller under the chin
    m = in_beard(xu, yd) & (yd < 452) & (zu > np.interp(yd, [260, 330, 420], [6, -18, -40]))
    idx = np.where(m)[0]
    # thin the points out: about one every 9 units
    from scipy.spatial import cKDTree
    pts = np.c_[xu[idx], yd[idx], zu[idx]]; keep = []
    tree = cKDTree(pts); taken = np.zeros(len(pts), bool)
    for i in range(len(pts)):
        if taken[i]: continue
        keep.append(i); taken[tree.query_ball_point(pts[i], 9.0)] = True
    C = pts[keep]
    Nn = N[idx][keep] * [1, -1, 1]
    depth = np.interp(C[:, 1], [250, 330, 400, 444], [1, 5, 10, 13])       # thin at the sideburns, thick at the chin
    R = np.interp(C[:, 1], [250, 330, 444], [7, 11, 15])
    C = C + Nn * (depth - R * 0.5)[:, None]
    # the lower lobes: a row of big balls under the jaw, from side to side (the drawing's curly lower edge)
    low = [(sx * ax, y, zz) for ax, y, zz in ((0, 458, 76), (32, 456, 68), (66, 436, 46), (86, 400, 18), (94, 358, 2))
           for sx in ((1, -1) if ax else (1,))]
    C = np.r_[C, low]; R = np.r_[R, [25, 23, 23, 22, 22, 19, 19, 15, 15]]
    v, t = Bl.solid((C, R), k=6, cell=3.0, keep=0.35, smooth=12)
    out['beard'] = (U(v), t[:, ::-1])
    # the moustache: thick, the tips swept out and up
    def wing(sx):
        pts = [(sx * 4, 346, z(0, 346) + 22), (sx * 28, 346, z(28, 348) + 24), (sx * 56, 354, z(56, 352) + 24),
               (sx * 76, 350, z(74, 348) + 20), (sx * 88, 336, z(84, 338) + 14)]
        return Bl.chain(pts, [13, 15, 13, 9, 3.5], 40)
    (c1, r1), (c2, r2) = wing(1), wing(-1)
    v, t = Bl.solid((np.r_[c1, c2], np.r_[r1, r2]), k=3, cell=2.0, squash=(1, 1, 0.8))
    out['moustache'] = (U(v), t[:, ::-1])
    # the hair: a cap of short curls — balls on the skull over the hairline, each one a curl
    hairline = lambda ax: np.interp(ax, [0, 30, 60, 85, 100], [196, 190, 198, 214, 250])    # front view: hair above this
    cs, rs = [], []
    n = 150
    for i in range(n):                                  # even directions over the upper sphere
        u = 1 - (i + 0.5) / n * 1.25; ph = i * 2.399963
        d = np.array([np.sqrt(max(0, 1 - u * u)) * np.cos(ph), u, np.sqrt(max(0, 1 - u * u)) * np.sin(ph)])
        o = np.array([0, (CH - 232) * K, 8 * K])        # rays from the skull's middle
        rel = V - o; t_ = rel @ d
        perp = np.linalg.norm(rel - np.outer(t_, d), axis=1)
        ok = t_ > 0
        if not ok.any(): continue
        j = np.where(ok)[0][np.argmin(perp[ok])]
        px, py, pz = xu[j], yd[j], zu[j]
        front = pz > 20
        if front and py > hairline(abs(px)): continue
        if not front and py > np.interp(pz, [-80, -30, 20], [300, 268, 250]): continue
        cs.append([px, py, pz] + N[j] * [1, -1, 1] * 6); rs.append(20 + 3 * np.sin(i * 1.7))
    v, t = Bl.solid((np.array(cs), np.array(rs)), k=1.6, cell=3.0, keep=0.35)
    out['hair'] = (U(v), t[:, ::-1])
    return out


if __name__ == '__main__':
    import sys
    from PIL import Image
    V, P, ear = fitted(); T = M.triangulate(P)
    sk = (0.86, 0.61, 0.46)
    cols = dict(earL=sk, earR=sk, nose=(0.86, 0.55, 0.42), beard=(0.2, 0.17, 0.2), moustache=(0.16, 0.13, 0.16), hair=(0.2, 0.17, 0.2))
    parts = [(V, T, sk)] + [(v, t, cols[k]) for k, (v, t) in forms(V, T).items()]
    Vs, Ts = Bl.join([(v, t) for v, t, _ in parts]); C = np.concatenate([np.tile(c, (len(v), 1)) for v, _, c in parts])
    print(len(Vs), len(Ts))
    box = (-0.27, 0.27, -0.09, 0.42)
    ims = [M.raster(Vs, Ts, yaw, 420, box, col=C, light=(-0.6, 0.5, 0.6))[0] for yaw in (0, 0.7, np.pi / 2)]
    Image.fromarray(np.hstack(ims)).save(sys.argv[1])
