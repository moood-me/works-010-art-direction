"""Марат's face pieces, as a stop-motion puppet's: the head is one sculpted cast, and the expressions are made by
replacement pieces laid on it — a mouth (lips, the dark of the mouth, teeth) and brows — and by lids that turn over
the glass eyes. Each replacement piece has one mesh (fixed topology) and a library of shapes, one per expression of
the drawing's sheet and one per mouth shape of speech; a face is a weighted mix of them (`tools/web/face.mjs`).

The shapes are the drawing's own: `head.mouth()` and `head.brow()` of styles/s8-stopmotion, the same curves from the
same numbers (cast.EXPR), laid on the fitted head (each point onto the head's surface, raised along its normal: the
lips as two rolls of clay, the brows as a raised strip).
Lids: the head's own lid skin turns about each eye's horizontal axis (weights fall off from the margin);
the lash line is a thin dark strip on the upper margin that turns with it.
Output: CACHE/face.npz and the numbers in CACHE/face.json."""
import json, math
import numpy as np, igl
import base, drawing
from drawing import P, H0, EXPR
from common import CACHE, vertex_normals
from fit_head import R_EYE, LID_R

HD = np.load(f'{CACHE}/head_raw.npz')
HV = HD['V']; HT = base.tris(HD['Q'])
HN = vertex_normals(HV, HT)

# the mouth shapes of speech, in the drawing's mouth numbers
VISEMES = {
    'A': dict(mopen=0.55, wide=1.0, smile=0.1),
    'O': dict(mopen=0.55, wide=0.62),
    'U': dict(mopen=0.2, wide=0.5),
    'E': dict(mopen=0.28, wide=1.15, smile=0.15),
    'I': dict(mopen=0.12, wide=1.2, smile=0.25),
    'M': dict(mopen=0.0, wide=0.95),
    'F': dict(mopen=0.1, wide=1.0),
}
BROW_UP = 0.03
BROW_H = 0.02        # how far the thick black brows stand off the forehead
LID_K = 0.6          # the sheet's lids turn this much: a lid over a glass ball covers more than a painted one
FACES = ['calm', 'beam', 'laugh', 'surprise', 'sad', 'anger']      # beam is his resting face; his joy is the laugh


def on_head(X):
    """head-unit points near the surface → the nearest surface points and normals"""
    _, I, C = igl.point_mesh_squared_distance(X, HV, HT)
    N = HN[HT[I]].mean(1); N /= np.linalg.norm(N, axis=1, keepdims=True)
    return C, N


def laid(xl, yl, phi0, y0, h):
    """local (arc x, y down) round (phi0, y0) → the head's surface, raised by h along its normal"""
    xl, yl, h = map(np.asarray, (xl, yl, h))
    a = np.array([H0.a(y0 + y) for y in yl.ravel()]).reshape(yl.shape)
    S = np.array([drawing.surf(phi0 + x / aa, y0 + y) for x, y, aa in zip(xl.ravel(), yl.ravel(), a.ravel())])
    C, N = on_head(S)
    return C + N * (h.ravel()[:, None] + 0.0015)


def grid_tris(rows, cols, flip=False):
    T = []
    for i in range(rows - 1):
        for j in range(cols - 1):
            a, b, c, d = i * cols + j, i * cols + j + 1, (i + 1) * cols + j, (i + 1) * cols + j + 1
            T += [(a, c, b), (b, c, d)] if not flip else [(a, b, c), (b, d, c)]
    return np.array(T)


NX = 25


def mouth(ex):
    """the drawing's mouth() curves → four grids: upper lip, lower lip, the dark inside, the teeth"""
    ym = P['mouth_y']
    w = P['mouth_w'] * ex.get('wide', 1.0)
    smile, opn, skew = ex.get('smile', 0.0), ex.get('mopen', 0.0), ex.get('skew', 0.0)
    ul, ll = P.get('upper_lip', 0.010), P.get('lower_lip', 0.016)
    t = np.linspace(0, 1, NX)
    x = -w + 2 * w * t
    e = np.abs(2 * t - 1)
    corner = (smile + skew * (t - 0.5) * 2) * e ** 1.6
    y = -corner * 0.035 + smile * 0.01 * (1 - e)
    s = np.sin(np.pi * t)
    top = y - opn * 0.03 * s ** 0.7
    bot = y + opn * 0.06 * s ** 0.8 + smile * 0.012 * s
    env = s ** 0.45
    R = 6
    out = {}
    # upper lip: from its outer edge (s=0) to the line of the mouth (s=1); a roll that rises and turns in
    r = np.linspace(0, 1, R)[:, None]
    yu = top - (ul * 1.4 * s ** 0.5 + 0.004) * (1 - r)
    hu_ = 0.006 * np.sin(np.pi * (0.12 + 0.88 * r)) ** 0.7 * env
    out['lipU'] = laid(np.tile(x, (R, 1)), yu, 0.0, ym, hu_)
    yl = bot + (ll * 1.5 * s ** 0.6 + 0.005) * (1 - r)
    hl = 0.008 * np.sin(np.pi * (0.12 + 0.88 * r)) ** 0.7 * env
    out['lipL'] = laid(np.tile(x, (R, 1)), yl, 0.0, ym, hl)
    # the dark of the mouth between the lines; a little sunk in the middle (it reads as depth under the lips)
    yc = top + (bot - top) * r
    hc = 0.002 + 0.0 * r
    out['cav'] = laid(np.tile(x * 0.985, (R, 1)), yc, 0.0, ym, np.broadcast_to(hc, yc.shape))
    # teeth: a band under the upper line (and over the lower one, when the face shows the lower teeth)
    teeth = ex.get('teeth', True) and opn > 0.02
    dt = (np.minimum(top + 0.022 * r, bot) - top) if teeth else 0 * r
    out['teethU'] = laid(np.tile(x * 0.85, (R, 1)), top + dt + 0.0005, 0.0, ym, np.full((R, NX), 0.004) * (0.6 + 0.4 * env))
    lt = ex.get('lower_teeth') and opn > 0.02
    db = (np.maximum(bot - 0.016 * r, top) - bot) if lt else 0 * r
    out['teethL'] = laid(np.tile(x * 0.75, (R, 1)), bot + db - 0.0005, 0.0, ym, np.full((R, NX), 0.0035) * (0.6 + 0.4 * env))
    return out


def brow(side, ex, n=12, R=5):
    """head.brow: the bushy white brows — a thick slab whose lower edge droops toward the outer end (brow_droop)"""
    phi = side * P['eye_phi']
    yb = P['eye_y'] - P['brow_gap'] - BROW_UP
    w, th = P['brow_w'], P['brow_th']
    li, lo = ex.get('brow_in', 0.0), ex.get('brow_out', 0.0)
    ix, ox = (-w * 0.95, w * 1.1) if side > 0 else (w * 0.95, -w * 1.1)
    arch = P.get('brow_arch', 0.012); taper = P.get('brow_taper', 0.75); droop = P.get('brow_droop', 0.0)
    t = np.linspace(0, 1, n)
    x = ix + (ox - ix) * t
    y = -li * (1 - t) - lo * t - arch * np.sin(np.pi * np.minimum(1, t * 1.2)) + 0.004 * t
    thick = th * (1 - taper * t ** 1.3) * (0.8 + 0.2 * np.sin(np.pi * np.minimum(1, t * 2)))
    r = np.linspace(0, 1, R)[:, None]
    top, bot = y - thick * 0.6, y + thick * 0.4 + droop * t ** 2
    yy = top + (bot - top) * r
    ends = np.sin(np.pi * (0.06 + 0.88 * t)) ** 0.35           # the slab's ends rounded off
    h = BROW_H * np.sin(np.pi * (0.05 + 0.9 * r)) ** 0.6 * ends
    return laid(np.tile(x, (R, 1)), yy, phi, yb, h)


import hair as H
import fit_hair

_spots = H.curl_spots(H0, lambda phi, y: abs(phi) <= 0.64 and P['nose_tip'] + 0.05 <= y <= P['mouth_y'] - 0.03, 0.038,
                      P['nose_tip'] + 0.055, P['mouth_y'] + 0.03, out=0.03, seed=6, place=lambda phi, y: (phi, y, 0.0))


def moustache(ex):
    """marat.marat_hair's moustache: curls between the nose and the mouth (the same honeycomb, seed 6). In the drawing its
    lower edge rises with the corners of a smile, so the open mouth is never covered; here the same curls are squeezed up
    under that edge (one set of curls for every face, so the faces mix), and ride up a little with an opening mouth."""
    y0, y1 = P['nose_tip'] + 0.05, P['mouth_y'] - 0.03
    lift = 0.035 * ex.get('smile', 0.0) + 0.012 * ex.get('mopen', 0.0)
    spots = []
    for (phi, y, _), r, fc, a0, wind in _spots:
        edge = y1 - max(lift, -0.01) * min(1.0, abs(phi) / 0.45) ** 1.6 - 0.006 * ex.get('mopen', 0.0)
        yy = y0 + (y - y0) * (edge - y0) / (y1 - y0)
        spots.append((H0.surf(phi, yy, 0.03), r, fc, a0, wind))
    V, T, uv = fit_hair.curls(spots, lambda c: np.array([0.0, c[1] + 0.02, 0.0]))
    return V, T, uv


def tongue(ex):
    """head.mouth's tongue: an ellipse low in the open mouth (it and the teeth keep the laugh from reading as a hole)"""
    ym = P['mouth_y']; w = P['mouth_w'] * ex.get('wide', 1.0)
    smile, opn = ex.get('smile', 0.0), ex.get('mopen', 0.0)
    t = np.linspace(0, 1, NX); e = np.abs(2 * t - 1); s = np.sin(np.pi * t)
    y = -smile * e ** 1.6 * 0.035 + smile * 0.01 * (1 - e)
    top = y - opn * 0.03 * s ** 0.7; bot = y + opn * 0.06 * s ** 0.8 + smile * 0.012 * s
    cy = bot.max() * 0.7; rx, ry = w * 0.55, opn * 0.03
    u = np.linspace(-1, 1, NX); r = np.linspace(-1, 1, 6)[:, None]
    xx = np.tile(u * rx, (6, 1)); yy = cy + r * ry * np.sqrt(np.maximum(0, 1 - u ** 2))
    lim_b = np.interp(u * rx, -w + 2 * w * t, bot) - 0.003; lim_t = np.interp(u * rx, -w + 2 * w * t, top) + 0.002
    yy = np.maximum(np.minimum(yy, lim_b), np.minimum(lim_t, lim_b))
    h = 0.003 + 0.004 * (1 - r ** 2) * (1 - u ** 2) * min(1.0, opn * 3)
    return laid(xx, yy, 0.0, ym, np.broadcast_to(h, yy.shape))


def lids():
    """per vertex of the head: how much it turns with the upper and with the lower lid of each eye"""
    adj = igl.adjacency_list(HT)
    out = {}
    for side, key in ((1, 'L'), (-1, 'R')):
        c = drawing.eye_centre(side)
        mb = HD['m' + key]
        phi, ye = side * P['eye_phi'], P['eye_y']
        n = drawing.surf(phi, ye, 0.01) - drawing.surf(phi, ye, 0.0); n /= np.linalg.norm(n)
        up = np.array([0, 1.0, 0]); up -= (up @ n) * n; up /= np.linalg.norm(up)
        # rings from the margin
        dist = np.full(len(HV), 99); dist[mb] = 0
        frontier = set(mb.tolist())
        for k in range(1, 9):
            nxt = {j for i in frontier for j in adj[i] if dist[j] > k}
            for j in nxt: dist[j] = k
            frontier = nxt
        fall = np.clip(1 - dist / 8.0, 0, 1) ** 1.5
        d = HV - c
        el = (d @ up) / np.maximum(np.linalg.norm(d, axis=1), 1e-9)
        # the lids turn about an axis through the ball's centre along the opening's chord (corner to corner), and
        # less toward the corners — the lid sweeps as a drawn lid does, the corners stay
        lat = (HV[mb] - c) @ np.array([1.0, 0, 0]) * side
        inner, outer = HV[mb[lat.argmin()]], HV[mb[lat.argmax()]]
        ax = (outer - inner) / np.linalg.norm(outer - inner) * side
        if ax[0] < 0: ax = -ax
        s = np.clip(((HV - inner) @ (outer - inner)) / ((outer - inner) @ (outer - inner)), 0, 1)
        mid = np.sin(np.pi * s) ** 0.6
        wU = fall * np.clip((el + 0.15) / 0.3, 0, 1) * mid
        wL = fall * np.clip((0.15 - el) / 0.3, 0, 1) * mid
        out[key] = dict(c=c, n=n, up=up, ax=ax, wU=wU, wL=wL, margin=mb, mid=mid)
    return out


def lash(L, side):
    """the lash line: a thin dark strip along the upper margin, a little proud of the lid, with a wing at the outer
    corner (the drawing's lash and wing)"""
    mb = L['margin']; c = L['c']; up = L['up']; n = L['n']
    P_ = HV[mb]
    d = P_ - c
    upper = (d @ up) > -0.004
    idx = np.where(upper)[0]
    # order along the margin from inner to outer
    lat = d[idx] @ L['ax']
    o = np.argsort(lat * side)
    ids = mb[idx[o]]
    Pm = HV[ids]
    # out from the ball (radially) and up along the lid
    rad = (Pm - c) / np.linalg.norm(Pm - c, axis=1, keepdims=True)
    lw = P.get('lash_w', 0.012)
    tt = np.linspace(0, 1, len(ids))
    width = (lw * (0.6 + 0.8 * np.sin(np.pi * tt) ** 0.5))[:, None]
    tang = np.gradient(Pm, axis=0); tang /= np.linalg.norm(tang, axis=1, keepdims=True)
    upd = np.cross(tang, rad) * side
    upd *= np.sign((upd @ up).mean())
    rows = [Pm + rad * 0.0015, Pm + rad * 0.006 + upd * width * 0.5, Pm + rad * 0.003 + upd * width * 1.1]
    V = np.concatenate(rows)
    m = len(ids)
    T = grid_tris(3, m)
    # the wing past the outer corner
    wing_base = Pm[-1]
    wing_tip = wing_base + L['ax'] * side * 0.018 * P.get('wing', 1.0) + up * 0.012 * P.get('wing', 1.0) + rad[-1] * 0.004
    V = np.r_[V, [wing_tip]]
    T = np.r_[T, [[m - 1, 2 * m - 1, len(V) - 1], [2 * m - 1, 3 * m - 1, len(V) - 1]]]
    w = np.r_[np.tile(L['mid'][ids], 3), [L['mid'][ids[-1]]]]          # it turns as much as its piece of margin
    return V, T, w


def expr_numbers(ex):
    """the lids' turn for an expression (radians, + closes the upper lid / raises the lower), the gaze"""
    R = P['eye_r']
    def ang(h):
        return math.asin(max(-1.0, min(1.0, h / (R_EYE * LID_R))))
    op0 = EXPR['calm'].get('open', 1.0) * P['eye_open']
    top0, bot0 = R * P['lid_top'] * op0, R * P['lid_bot'] * op0
    op = ex.get('open', 1.0) * P['eye_open']
    top = R * P['lid_top'] * op * (1 + ex.get('lid_up', 0.0))
    bot = R * P['lid_bot'] * op * (1 - ex.get('lid_lo', 0.0))
    g = ex.get('gaze', (0.0, 0.0))
    return dict(up=LID_K * (ang(top0) - ang(top)), lo=LID_K * (ang(bot0) - ang(bot)), gaze=[g[0], -g[1]], pupil=ex.get('pupil', 0.38))


def main():
    shapes = {}
    allm = {k: dict(EXPR[k]) for k in FACES}
    for k, v in VISEMES.items(): allm['v' + k] = v
    for k, ex in allm.items():
        shapes[k] = mouth(ex)
    brows = {k: np.r_[brow(1, EXPR[k]), brow(-1, EXPR[k])] for k in FACES}
    res_m = {k: moustache(ex) for k, ex in allm.items()}
    L = lids()
    lashes = [lash(L[k], s) for k, s in (('L', 1), ('R', -1))]
    res = {}
    for k in allm: res['moust_' + k] = res_m[k][0]; res['tongue_' + k] = tongue(allm[k])
    res['moust_T'] = res_m['calm'][1]; res['moust_uv'] = res_m['calm'][2]; res['tongue_T'] = grid_tris(6, NX)
    R6, n = 6, NX
    for part in ('lipU', 'lipL', 'cav', 'teethU', 'teethL'):
        flip = part in ('lipL',)
        res[part + '_T'] = grid_tris(R6, n, flip)
        for k in allm:
            res[f'{part}_{k}'] = shapes[k][part]
    bt = grid_tris(5, 12)
    res['brow_T'] = np.r_[bt, grid_tris(5, 12, True) + 60]
    rr = np.repeat(np.linspace(0, 1, 5), 12); tt = np.tile(np.linspace(0, 1, 12), 5)
    res['brow_uv'] = np.tile(np.c_[rr * 0.7, tt], (2, 1))
    for k in FACES: res['brow_' + k] = brows[k]
    off = 0; LV, LT, LW = [], [], []
    for V, T, w in lashes:
        LV.append(V); LT.append(T + off); LW.append(w); off += len(V)
    res['lash_V'] = np.concatenate(LV); res['lash_T'] = np.concatenate(LT); res['lash_w'] = np.concatenate(LW)
    # the lash follows the upper lid fully
    for k in ('L', 'R'):
        for a in ('c', 'n', 'up', 'ax', 'wU', 'wL'):
            res[f'lid{k}_{a}'] = L[k][a]
    np.savez(f'{CACHE}/face.npz', **res)
    nums = {k: expr_numbers(EXPR[k]) for k in FACES}
    json.dump(dict(faces=FACES, visemes=list(VISEMES), expr=nums), open(f'{CACHE}/face.json', 'w'), indent=1)
    print('face pieces written', {k: v for k, v in nums.items()})


if __name__ == '__main__':
    main()
