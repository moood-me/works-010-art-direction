"""Савелий Петрович's head (Klaus). The drawing has one view of him — three-quarter (styles/s2-klaus/tools/savely.py,
head34: a 500×600 frame, the dome's top at y=100, eyes at 262, the nose's bulb at 335, the chin at 430). Front and
profile are not drawn, so the outline numbers below are read off that one view by hand: a tall egg of a dome, a short
heavy jaw, a thick neck. The base head (base_head.py) is fitted to them; the big soft forms of the drawing — the
nose, the walrus moustache, the brows, the tufts behind the ears — are separate smooth solids (blobs.py), as they are
separate forms in the drawing; the glasses, the loupe and its band are thin made things.
Everything is returned in metres, the chin at y=0, the face to +z."""
import numpy as np
import mesh as M, base_head as B, blobs as Bl

K = 0.001258            # metres per head unit: the figure is 712 units = 1.60 m, the head drawn at 0.56 of its frame
CH = 430.0              # the chin's unit height
HBM = '/home/user/cache/to3d-r15-s2-savely/hbm.npz'


def U(p):
    """Head units (x from the middle, y down, z forward) → metres."""
    p = np.asarray(p, float)
    return np.c_[p[..., 0] * K, (CH - p[..., 1]) * K, p[..., 2] * K].reshape(p.shape)


# the outline, by height (units)
_Y = [100, 108, 120, 140, 160, 200, 246, 262, 300, 340, 370, 395, 415, 430, 442, 456, 480]
_HW = [0, 40, 62, 78, 85, 90, 89, 88, 86, 80, 72, 60, 50, 44, 44, 45, 47]        # half width (lower: the neck)
_FW = [np.nan] * 9 + [80, 70, 54, 38, 18, np.nan, np.nan, np.nan]                # the jaw in front of the ears
_ZF = [-10, 40, 62, 84, 94, 102, 102, 96, 98, 100, 98, 94, 86, 66, 44, 40, 40]   # the face's line in profile
_ZB = [-10, -60, -80, -98, -106, -112, -108, -104, -94, -78, -66, -58, -54, -52, -52, -52, -54]
DRAW_Y = [482.0, 430.0, 416.0, 398.0, 344.0, 262.0, 240.0, 100.0]


def spec():
    yd = np.arange(104, 478, 6.0)
    f = lambda a: np.interp(yd, _Y, a)
    fw = np.interp(yd, _Y[9:14], _FW[9:14]); fw[(yd < 340) | (yd > 430)] = np.nan
    return dict(K=K, chin=CH, draw_y=DRAW_Y, yd=yd, hw=f(_HW), fw=fw, zf=f(_ZF), zb=f(_ZB), start=(0.75, 0.9))


def fitted():
    v, P = B.base(HBM)
    T = M.triangulate(P)
    ear = B.ears_of(v)
    V = B.fit(v, T, ~ear[T].any(1), spec())
    # the base's ears are smoothed away: the drawing's ear is one simple big form (forms(): earL, earR)
    A = M.adjacency(len(V), T)
    grow = ear.copy()
    for _ in range(2): grow = grow | (A @ grow > 0)
    V = M.smooth(V, A, grow * 1.0, iters=120, lam=0.5)
    V = M.smooth(V, A, np.ones(len(V)), iters=4, lam=0.5)
    # the base's flare to the shoulders is cut off: the neck ends inside the collar
    yd = CH - V[:, 1] / K
    P = [p for p in P if (yd[p] < 452).all()]
    V, P, mm = B.compact(V, P)
    return V, P, ear[mm >= 0]


def face_z(V, N, x, y):
    """The face's depth (units) at head units (x, y)."""
    p, _ = B.surface_point(V, N, x * K, (CH - y) * K)
    return p[2] / K


def forms(V, T):
    """The drawing's forms as solids. Returns {name: (V, T)} in metres."""
    N = M.vertex_normals(V, T)
    z = lambda x, y: face_z(V, N, x, y)
    out = {}
    cell = 2.5
    # the ears: big, a long lobe; a rolled rim round a shallow bowl, standing off the head at the back
    for name, sx in (('earL', 1), ('earR', -1)):
        x0 = np.interp(290, _Y, _HW) - 5
        an = np.linspace(-0.75 * np.pi, 0.62 * np.pi, 9)          # from the lobe's front, round the back, to the top's front
        rimp = [(sx * (x0 + 9 + 7 * np.cos(a - 0.3)), 288 - 36 * np.sin(a) + (8 if a < -1.6 else 0), -12 - 21 * np.cos(a)) for a in an]
        c1, r1 = Bl.chain(rimp, [8, 8.5, 7, 6, 6, 6, 6.5, 6.5, 5], 26)
        c2, r2 = Bl.chain([(sx * (x0 - 2), 262, -6), (sx * (x0 - 1), 290, -8), (sx * (x0 - 1), 316, -6)], [13, 14, 11], 8)
        v, t = Bl.solid((np.r_[c1, c2], np.r_[r1, r2]), k=2.5, cell=2.0)
        out[name] = (U(v), t[:, ::-1])
    # the nose: a bridge from between the brows down to a big round bulb, two wings
    zn = z(0, 330)
    b, r = Bl.chain([(0, 252, z(0, 252) + 1), (0, 286, z(0, 286) + 15), (0, 316, zn + 34), (0, 336, zn + 46)], [6.5, 10, 20, 29], 20)
    wings = np.array([(sx * 25, 344, zn + 16) for sx in (1, -1)])
    v, t = Bl.solid((np.r_[b, wings], np.r_[r, [19, 19]]), k=5, cell=cell)
    out['nose'] = (U(v), t[:, ::-1])
    # the moustache: two drooping walrus wings from under the nose, round the mouth's corners, tips out and down
    def wing(sx):
        pts = [(sx * 4, 368, z(0, 372) + 22), (sx * 26, 370, z(26, 372) + 20), (sx * 50, 382, z(50, 384) + 13),
               (sx * 68, 400, z(68, 400) + 6), (sx * 80, 420, z(74, 414) - 4)]
        return Bl.chain(pts, [18, 20, 17, 11, 3.5], 44)
    (c1, r1), (c2, r2) = wing(1), wing(-1)
    v, t = Bl.solid((np.r_[c1, c2], np.r_[r1, r2]), k=4, cell=cell, squash=(1, 1, 0.8))
    out['moustache'] = (U(v), t[:, ::-1])
    # the brows: big soft shapes over the eyes, the inner ends low (grumpy), wrapping back at the temples
    for name, sx in (('browL', 1), ('browR', -1)):
        pts = [(sx * 9, 244, z(9, 247) + 4), (sx * 26, 229, z(26, 236) + 7), (sx * 50, 222, z(50, 230) + 7),
               (sx * 72, 227, z(72, 236) + 5), (sx * 88, 240, z(84, 244) + 2)]
        c, r = Bl.chain(pts, [6.5, 10.5, 10.5, 8, 3], 34)
        # two loose tufts off the outer end, as drawn
        t1, q1 = Bl.chain([(sx * 62, 228, z(62, 236) + 6), (sx * 84, 248, z(80, 250) + 5)], [7, 2.5], 14)
        v, t = Bl.solid((np.r_[c, t1], np.r_[r, q1]), k=3, cell=2.0, squash=(1, 1, 0.75))
        out[name] = (U(v), t[:, ::-1])
    # the tufts behind the ears: three big locks a side, sticking back and out
    for name, sx in (('tuftL', 1), ('tuftR', -1)):
        cs, rs = [], []
        for y0, y1, back, outw in ((196, 206, 82, 30), (236, 252, 88, 34), (276, 298, 70, 24)):
            x0 = sx * (np.interp(y0, _Y, _HW) - 14)
            c, r = Bl.chain([(x0, y0, -40), (x0 + sx * outw * 0.6, (y0 + y1) / 2 - 4, -40 - back * 0.6),
                             (x0 + sx * outw, y1, -40 - back)], [20, 14, 2.5], 30)
            cs.append(c); rs.append(r)
        v, t = Bl.solid((np.concatenate(cs), np.concatenate(rs)), k=2.5, cell=2.5, squash=(0.7, 1, 1))
        out[name] = (U(v), t[:, ::-1])
    return out


def things(V, T):
    """The glasses, the loupe and its band: thin made things (tubes, discs), metres. {name: (V, T)}"""
    N = M.vertex_normals(V, T)
    z = lambda x, y: face_z(V, N, x, y)
    out = {}
    # round glasses low on the nose
    parts = []
    gz = z(34, 276) + 16
    th = np.linspace(0, 2 * np.pi, 40, endpoint=False)
    for sx in (1, -1):
        ring = np.c_[sx * 36 + 23 * np.cos(th), 277 + 20 * np.sin(th), gz - 0.10 * (23 * np.cos(th) * sx + 23)]
        parts.append(Bl.tube(U(ring), 1.5 * K, 8, closed=True))
        ez = z(88, 262) - 60
        temple = np.array([(sx * 59, 274, gz - 4), (sx * 78, 268, gz - 24), (sx * 90, 264, gz - 60), (sx * 92, 262, -6), (sx * 90, 272, -24)])
        parts.append(Bl.tube(U(Bl.chain(temple, [1] * 5, 16)[0]), 1.2 * K, 6))
    br = np.array([(-13, 274, gz + 1), (-6, 268, gz + 5), (6, 268, gz + 5), (13, 274, gz + 1)])
    parts.append(Bl.tube(U(Bl.chain(br, [1] * 4, 10)[0]), 1.3 * K, 6))
    out['glasses'] = Bl.join(parts)
    hl = []
    for sx in (1, -1):
        a = np.linspace(2.2, 3.4, 8)
        arc = np.c_[sx * 36 + 15 * np.cos(a), 277 - 13 * np.sin(a), np.full(8, gz - 0.10 * 23 + 0.5)]
        hl.append(Bl.tube(U(arc), 0.9 * K, 5))
    out['glint'] = Bl.join(hl)
    # the lenses: faint discs
    parts = []
    for sx in (1, -1):
        c = np.array([sx * 36, 277, gz - 0.10 * 23]); ring = np.c_[sx * 36 + 22 * np.cos(th), 277 + 19 * np.sin(th), gz - 0.10 * (22 * np.cos(th) * sx + 23)]
        Vv = U(np.r_[[c], ring]); Tt = np.array([[0, 1 + k, 1 + (k + 1) % len(th)] for k in range(len(th))])
        if np.cross(Vv[Tt[0, 1]] - Vv[Tt[0, 0]], Vv[Tt[0, 2]] - Vv[Tt[0, 0]])[2] < 0: Tt = Tt[:, ::-1]
        parts.append((Vv, Tt))
    out['lens'] = Bl.join(parts)
    # the loupe pushed up on the forehead, a little to his left: a dark barrel, a brass ring, a blue glass
    p, n = B.surface_point(V, N, 14 * K, (CH - 146) * K)
    n = n / np.linalg.norm(n)
    u = np.cross(n, [0, 1.0, 0]); u /= np.linalg.norm(u); w = np.cross(n, u)

    def barrel(r0, r1, h0, h1, seg=28):
        a = np.linspace(0, 2 * np.pi, seg, endpoint=False)
        ring = lambda r, h: p + n * h + np.outer(np.cos(a), u) * r + np.outer(np.sin(a), w) * r
        Vv = np.r_[ring(r0, h0), ring(r1, h1), [p + n * h1]]
        Tt = []
        for k in range(seg):
            k2 = (k + 1) % seg
            Tt += [[k, k2, seg + k], [k2, seg + k2, seg + k], [seg + k, seg + k2, 2 * seg]]
        Tt = np.array(Tt)
        nn = np.cross(Vv[Tt[:, 1]] - Vv[Tt[:, 0]], Vv[Tt[:, 2]] - Vv[Tt[:, 0]])
        if (nn * (Vv[Tt].mean(1) - (p + n * (h0 + h1) / 2))).sum() < 0: Tt = Tt[:, ::-1]
        return Vv, Tt
    out['loupe'] = barrel(26 * K, 22 * K, -6 * K, 20 * K)
    out['brass'] = barrel(21 * K, 19 * K, 18 * K, 25 * K)
    out['glass'] = barrel(15 * K, 13 * K, 24 * K, 27 * K)
    # the band: round the head through the loupe, lower at the back
    yb = lambda zz: 150 + 0.10 * (z(0, 150) - zz)           # the band's unit height by depth
    Vt = V.copy(); Vt[:, 1] = V[:, 1] - ((CH - yb(V[:, 2] / K)) * K - (CH - 150) * K)
    S = B.slice_segments(Vt, T, (CH - 150) * K).reshape(-1, 3)
    ang = np.arctan2(S[:, 0], S[:, 2] + 0.0)
    ring = []
    for a0 in np.linspace(-np.pi, np.pi, 72, endpoint=False):
        d = np.abs(np.angle(np.exp(1j * (ang - a0))))
        q = S[np.argsort(d)[:4]].mean(0)
        r = np.hypot(q[0], q[2]) + 1.5 * K
        zz = r * np.cos(a0)
        ring.append([r * np.sin(a0), (CH - yb(zz / K)) * K, zz])
    out['band'] = Bl.tube(np.array(ring), np.array([[1.2 * K, 3.2 * K]] * len(ring)), 8, closed=True)
    return out


if __name__ == '__main__':
    import sys
    from PIL import Image
    V, P, ear = fitted(); T = M.triangulate(P)
    parts = [(V, T, (0.89, 0.65, 0.54))]
    cols = dict(nose=(0.85, 0.5, 0.45), moustache=(0.9, 0.9, 0.86), earL=(0.89, 0.65, 0.54), earR=(0.89, 0.65, 0.54), browL=(0.9, 0.9, 0.86), browR=(0.9, 0.9, 0.86),
                tuftL=(0.9, 0.9, 0.86), tuftR=(0.9, 0.9, 0.86), glasses=(0.4, 0.3, 0.2), glint=(1, 1, 1), lens=(0.8, 0.9, 0.95),
                loupe=(0.2, 0.2, 0.2), brass=(0.8, 0.6, 0.3), glass=(0.5, 0.7, 0.75), band=(0.2, 0.15, 0.15))
    for k, (v, t) in {**forms(V, T), **things(V, T)}.items(): parts.append((v, t, cols[k]))
    Vs, Ts = Bl.join([(v, t) for v, t, _ in parts]); C = np.concatenate([np.tile(c, (len(v), 1)) for v, _, c in parts])
    print(len(Vs), len(Ts))
    box = (-0.3, 0.3, -0.12, 0.48)
    ims = [M.raster(Vs, Ts, yaw, 420, box, col=C, light=(-0.6, 0.5, 0.6))[0] for yaw in (0, 0.7, np.pi / 2)]
    Image.fromarray(np.hstack(ims)).save(sys.argv[1])
