"""Савелий Петрович's head: the Human Base Meshes stylised head (CC0) fitted to the drawing's own 3D head (the loft of
styles/s8-stopmotion `cast.SAVELY`), so front, three-quarter and profile all come from one shape.

Two levels, so the sculptor's features survive the fit:
1. The eye-socket linings are cut away (faces inside the base's eyeballs): the lid margins become two clean loops.
   The mouth's bag is kept but left out of the next steps.
2. A smooth version of the base (implicit fairing, lid margins held) carries the big form; the base minus
   it is the detail (nose, lips, lids, ears, chin) in each vertex's own frame (normal, up the surface, across).
3. The smooth form is warped onto the drawing's loft (thin-plate RBF: the lid margins → the drawing's lid openings,
   the mouth's corners → the drawing's, many points → their nearest loft points; then every vertex projected onto
   the loft or the drawing's thin neck).
4. The detail is laid back in the new frames, scaled per region: the drawing's face is a smooth mask with a small
   button nose and small lips, so the nose's detail is shrunk most.
5. The eyes: glass balls of the drawing's size at the drawing's places; the lids around them pushed onto the ball
   (the margins radially onto a sphere a little bigger than the ball), with a short lip going in at the margin.
6. The ears are carried whole onto the drawing's (lower, smaller, standing out 42°).
Output: CACHE/head.npz (head units, engine axes)."""
import numpy as np, igl, math
from scipy.interpolate import RBFInterpolator
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve
import base, drawing
from common import CACHE, vertex_normals

P = drawing.P
R_EYE = P['eye_r'] * 1.05          # the drawing draws the ball 5 % bigger than eye_r
LID_R = 1.03            # the lid margin's distance from the eye's centre, in eyeball radii
K_NOSE, K_LIPS, K_FACE, K_EAR = 0.25, 0.0, 0.2, 1.0
EAR_TURN, EAR_K = 30.0, 1.4     # degrees on top of the drawing's ear_out; the ear's height against the drawing's plate
NOSE_LONG, NOSE_OUT = 1.0, 1.0
NOSE_WING = 1.2                  # the wings' half width in nose_w (head.nose: the alae stand out past the tip's width)
OPEN_K = 1.14
LOWZ = None


def frames(N):
    up = np.array([0.0, 1.0, 0.0])
    t = up - (N @ up)[:, None] * N
    bad = np.linalg.norm(t, axis=1) < 0.2
    alt = np.array([0.0, 0.0, 1.0])
    t[bad] = alt - (N[bad] @ alt)[:, None] * N[bad]
    t /= np.linalg.norm(t, axis=1, keepdims=True)
    b = np.cross(N, t)
    return t, b


def smooth_mask(mask, adj, n=4):
    w = mask.astype(float)
    for _ in range(n):
        w = np.array([0.5 * w[i] + 0.5 * np.mean(w[adj[i]]) for i in range(len(w))])
    return w


def match_by_angle(src_pts, curve):
    """for each src point, the point on the closed curve at the same angle round the two centres (x, y plane)"""
    cb = src_pts.mean(0); cd = curve.mean(0)
    ab = np.arctan2(src_pts[:, 1] - cb[1], src_pts[:, 0] - cb[0])
    ad = np.arctan2(curve[:, 1] - cd[1], curve[:, 0] - cd[0])
    o = np.argsort(ad); a3 = np.r_[ad[o] - 2 * np.pi, ad[o], ad[o] + 2 * np.pi]; C3 = np.r_[curve[o], curve[o], curve[o]]
    return np.array([[np.interp(a, a3, C3[:, k]) for k in range(3)] for a in ab])


LOFT = None


def LOFTM():
    global LOFT
    if LOFT is None:
        LOFT = drawing.loft_mesh(160, 160)
    return LOFT


def main():
    B = base.load()
    V0, Q = B['V'].copy(), B['Q'].copy()
    T0 = base.tris(Q)
    N0 = vertex_normals(V0, T0)
    ao = igl.ambient_occlusion(V0, T0, V0 + N0 * 1e-4, N0, 64)
    # 1. cut the eye linings and the mouth's bag; close the lips' seam (the mouth is a replacement piece of its own)
    keep = np.ones(len(Q), bool)
    for s_ in 'LR':
        e = B['eye' + s_][0]; c = e.mean(0); r = np.ptp(e[:, 0]) / 2
        keep &= ~(np.linalg.norm(V0[Q] - c, axis=2) < 0.97 * r).all(1)
    bag = (np.abs(V0[:, 0]) < 0.2) & (V0[:, 1] < -0.28) & (V0[:, 1] > -0.42) & (ao > 0.5)
    keep &= ~bag[Q].any(1)
    # the neck goes too: a puppet's head sits on a neck of its own (the drawing's thin neck, made in build.py);
    # the cut runs along the jaw from under the chin to the nape
    neck = V0[:, 1] < -0.47 + 0.367 * (0.35 - V0[:, 2])
    keep &= ~neck[Q].any(1)
    Q = base.largest(V0, Q[keep])
    used = np.unique(Q); remap = -np.ones(len(V0), int); remap[used] = np.arange(len(used))
    V0, Q, ao = V0[used], remap[Q], ao[used]
    margins = {}
    for l in base.loops(Q):
        m = V0[l].mean(0)
        if np.linalg.norm(m[:2] - [0, -0.32]) < 0.05 and m[2] > 0.3:
            seam = np.array(l)
        elif abs(m[0]) > 0.1:
            margins[1 if m[0] > 0 else -1] = np.array(l)
        else:
            under = np.array(l)
    assert len(margins) == 2
    patches = []
    for hole, rings in ((seam, 5), (under, 12)):
        V0, Q, new = base.close(V0, Q, hole, rings=rings)
        T = base.tris(Q)
        adj = igl.adjacency_list(T)
        free = set(new.tolist()); ring = set(hole.tolist())
        for _ in range(3):
            free |= ring; ring = {k for v in ring for k in adj[v]} - free
        fixed = np.array(sorted(set(range(len(V0))) - free))
        V0 = igl.harmonic(V0, T, fixed, V0[fixed], 2)
        patches.append(np.array(sorted(free)))
    ao = np.r_[ao, np.zeros(len(V0) - len(ao))]
    underpatch = np.zeros(len(V0), bool); underpatch[patches[1]] = True
    mouthpatch = np.zeros(len(V0), bool); mouthpatch[patches[0]] = True
    bag = np.zeros(len(V0), bool)

    # 2. the smooth form (without the bag)
    QS = Q; TS = T
    inS = np.ones(len(V0), bool)
    bnd = np.r_[margins[1], margins[-1]]          # the lid margins held
    S = V0.copy()
    W = np.full(len(V0), 1e-9); W[bnd] = 1e3; W[~inS] = 1.0
    L = igl.cotmatrix(V0, TS); M = igl.massmatrix(V0, TS, igl.MASSMATRIX_TYPE_VORONOI)
    A = (M - 1e-3 * L + diags(W)).tocsc()
    for it in range(8):
        b = M @ S + W[:, None] * S
        S = np.column_stack([spsolve(A, b[:, k]) for k in range(3)])
    NS = vertex_normals(S, TS)
    tS, bS = frames(NS)
    D = V0 - S
    det = np.c_[(D * NS).sum(1), (D * tS).sum(1), (D * bS).sum(1)]

    # 3. the smooth form onto the loft
    TV, TT = LOFTM()
    src, dst = [], []
    for side in (1, -1):
        Cd, _ = drawing.eye_opening(side, drawing.EXPR['calm'], n=80)
        mb = margins[side]
        src += list(mb); dst += list(match_by_angle(S[mb], Cd))
    ML = drawing.mouth_line(25)
    for i in seam[np.argsort(V0[seam, 0])][[0, len(seam) // 2, -1]]:
        u = (V0[i, 0] - V0[seam, 0].min()) / np.ptp(V0[seam, 0])
        src.append(i); dst.append([np.interp(u, np.linspace(0, 1, 25), ML[:, k]) for k in range(3)])
    src = np.array(src); dst = np.array(dst)
    eyezone = np.zeros(len(V0), bool)
    for side in (1, -1):
        eyezone |= np.linalg.norm(S - S[margins[side]].mean(0), axis=1) < 0.16
    cand = np.where(inS & ~eyezone & (np.abs(S[:, 0]) + 1 > 0))[0]
    samp = np.random.default_rng(3).choice(cand, 900, replace=False)
    S1 = S.copy()
    for it in range(4):
        _, _, C = igl.point_mesh_squared_distance(S1[samp], TV, TT)
        f = RBFInterpolator(np.r_[S[src], S[samp]], np.r_[dst, C] - np.r_[S[src], S[samp]],
                            kernel='thin_plate_spline', smoothing=1e-3, degree=1)
        S1 = S + f(S)
    _, _, C = igl.point_mesh_squared_distance(S1, TV, TT)
    S1[inS] = C[inS]
    S1[src[:len(src) - 3]] = dst[:len(src) - 3]

    # 4. the detail back, in the new frames, scaled per region
    N1 = vertex_normals(S1, TS); t1, b1 = frames(N1)
    nose = (np.abs(V0[:, 0]) < 0.22) & (V0[:, 1] > -0.245) & (V0[:, 1] < -0.04) & (V0[:, 2] > 0.4)
    lips = (np.abs(V0[:, 0]) < 0.27) & (V0[:, 1] < -0.245) & (V0[:, 1] > -0.47) & (V0[:, 2] > 0.3)
    ear = {s: (s * V0[:, 0] > 0.36) & (V0[:, 1] > -0.24) & (V0[:, 1] < 0.12) & (V0[:, 2] > -0.1) & (V0[:, 2] < 0.13)
           for s in (1, -1)}
    # the lower face is the drawing's smooth mask (a puppet's cheeks): less of the base's folds there
    k = K_FACE * np.clip((V0[:, 1] + 0.16) / 0.12, 0, 1)
    for mask, kk in ((smooth_mask(nose, adj, 6), K_NOSE), (np.minimum(1, 1.6 * smooth_mask(lips, adj, 8)), K_LIPS),
                     (smooth_mask(ear[1] | ear[-1], adj, 3), K_EAR)):
        k = k * (1 - mask) + kk * mask
    k = k * (1 - smooth_mask(underpatch, adj, 6))
    V = S1 + k[:, None] * (det[:, :1] * N1 + det[:, 1:2] * t1 + det[:, 2:] * b1)
    global LOWZ
    LOWZ = np.r_[underpatch | mouthpatch, np.zeros(len(V) - len(V0), bool)]
    V = relax_low(V, Q, adj)

    V = fix_ears(V, ear, adj, base.tris(Q), V0)
    V = fix_nose(V, nose, adj, V0, base.tris(Q))
    V, lip = fix_eyes(V, Q, margins, adj)
    Q = np.r_[Q, lip['Q']]
    V = np.r_[V, lip['V']]
    np.savez(f'{CACHE}/head_raw.npz', V=V, Q=Q, S=S, S1=S1, V0=V0, mL=margins[1], mR=margins[-1], bag=bag,
             seam=seam, earL=ear[1], earR=ear[-1], nose=nose, lips=lips)
    print('head raw', V.min(0).round(3), V.max(0).round(3))


def relax_low(V, Q, adj, iters=60):
    """tangential relaxation under the jaw and on the neck (the projection crowds the base's long jaw into the
    drawing's small one): each vertex toward its neighbours' mean, then back onto the surface"""
    T = base.tris(Q)
    zone = np.where(LOWZ)[0]
    for it in range(iters):
        m = np.array([V[adj[i]].mean(0) for i in zone])
        V[zone] = V[zone] + 0.6 * (m - V[zone])
        if it % 5 == 4 or it == iters - 1:
            V[zone] = igl.point_mesh_squared_distance(V[zone], *LOFTM())[2]
    return V


def fix_ears(V, ear, adj, T, V0):
    """carry each ear whole onto the drawing's: about its root, scaled to the drawing's height, turned so it stands
    out by the drawing's angle. The ear itself moves rigidly; a few rings of skin round it follow by a biharmonic
    blend (a soft weight instead would drag a skirt of skin out with the lobe)."""
    V = V.copy(); V_in = V.copy()
    for side in (1, -1):
        m = ear[side]
        E = V0[m]                                   # the sculptor's ear as it is in the base (the detail transfer bends it)
        ax = np.abs(E[:, 0])
        root = E[ax < ax.min() + 0.025].mean(0)
        outer = E[ax > np.percentile(ax, 70)].mean(0)
        u0 = outer - root; u0[1] = 0; u0 /= np.linalg.norm(u0)
        pts, droot, du = drawing.ear_plate(side)
        du = du.copy(); du[1] = 0; du /= np.linalg.norm(du)
        ang = math.atan2(du[0], du[2]) - math.atan2(u0[0], u0[2]) + side * math.radians(EAR_TURN)
        c, s = math.cos(ang), math.sin(ang)
        Rm = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        sc = np.ptp(pts[:, 1]) / np.ptp(E[:, 1]) * EAR_K
        ctr_d = pts.mean(0); ctr_b = E.mean(0)
        moved = droot + sc * (Rm @ (V0 - root).T).T
        moved[:, 1] += (ctr_d[1] - (droot[1] + sc * (ctr_b[1] - root[1])))
        # the part of the ear that stands off the skull moves whole; its foot and the skin round it blend
        off = m & (np.abs(V0[:, 0]) > ax.min() + 0.03)
        ring = set(np.where(m)[0].tolist()); zone = set(ring)
        for _ in range(5):
            ring = {k for v in ring for k in adj[v]} - zone; zone |= ring
        free = np.array(sorted(zone - set(np.where(off)[0].tolist())))
        fixed = np.array(sorted(set(range(len(V))) - set(free.tolist())))
        D = np.zeros_like(V); D[off] = moved[off] - V_in[off]
        D = igl.harmonic(V_in, T, fixed, D[fixed], 2)
        V = V + D * (np.isin(np.arange(len(V)), np.r_[free, np.where(off)[0]]))[:, None]
        print('ear', side, 'turn', round(math.degrees(ang), 1), 'scale', round(sc, 2))
    return V


def fix_nose(V, nose, adj, V0, T):
    """the sculptor's nose itself (the base's, as it is in V0: tip (0, −0.18, 0.6), wings ±0.1, standing 0.14 off the
    face, 0.13 from root to tip) stretched to the drawing's nose (head.nose: root → tip heights, how far the tip stands
    out, the width — for Савелий a long big bulb) and set with its tip on the drawing's tip; the skin round it follows
    by a biharmonic blend."""
    ns = drawing.nose_slices()                       # (y, z of the front, half width), root → tip
    yt, zt = ns[-1, 0], ns[-1, 1]
    core = nose & (V0[:, 2] > 0.475) & (np.abs(V0[:, 0]) < 0.115) & (V0[:, 1] < -0.06)
    tip0 = np.array([0.0, -0.18, 0.6])
    k = np.array([P['nose_w'] * NOSE_WING / 0.1, (ns[0, 0] - yt) / 0.13 * NOSE_LONG, P['nose_len'] / 0.14 * NOSE_OUT])
    moved = np.array([0.0, yt, zt]) + (V0 - tip0) * k
    ring = set(np.where(core)[0].tolist()); zone = set(ring)
    for _ in range(7):
        ring = {q for v in ring for q in adj[v]} - zone; zone |= ring
    free = np.array(sorted(zone - set(np.where(core)[0].tolist())))
    fixed = np.array(sorted(set(range(len(V))) - set(free.tolist())))
    D = np.zeros_like(V); D[core] = moved[core] - V[core]
    D = igl.harmonic(V, T, fixed, D[fixed], 2)
    V = V + D
    print('nose scale', k.round(2), 'tip', (0, round(yt, 3), round(zt, 3)))
    return V


def onto_ball(C, side, r=None):
    """points of the drawing's lid opening (laid on the head's surface) carried along the surface's normal at the
    eye onto the lid sphere round the glass ball — the opening keeps the drawn size and shape seen face-on"""
    r = r or R_EYE * LID_R
    c = drawing.eye_centre(side)
    phi, ye = side * P['eye_phi'], P['eye_y']
    n = drawing.surf(phi, ye, 0.01) - drawing.surf(phi, ye, 0.0); n /= np.linalg.norm(n)
    d = C - c
    lat = d - (d @ n)[:, None] * n
    L = np.linalg.norm(lat, axis=1, keepdims=True)
    lat = np.where(L > 0.985 * r, lat / L * 0.985 * r, lat)
    h = np.sqrt(np.maximum(r * r - (lat * lat).sum(1), 0))
    return c + lat + h[:, None] * n


def fix_eyes(V, Q, margins, adj):
    """the glass balls at the drawing's places; the margins onto the drawing's opening laid on the ball; the lid
    region kept outside the ball; a short lip from each margin in toward the ball's centre"""
    newV, newQ = [], []
    n0 = len(V)
    lips = {}
    for side in (1, -1):
        c = drawing.eye_centre(side)
        mb = margins[side]
        # the drawing's opening, a little rounder (no lean of the arc toward the outer corner, a fuller lower lid,
        # a little taller): on a glass ball a leaning lid reads as a frown
        Cd, _ = drawing.eye_opening(side, drawing.EXPR['calm'], n=80, peak=0.0, lower_pow=0.8, tall=1.12)
        # a glass ball shows less than a flat painted eye of the same outline: the opening a little larger
        cc = Cd.mean(0); Cd = cc + (Cd - cc) * OPEN_K
        Cd = onto_ball(Cd, side)
        tgt = match_by_angle(V[mb], Cd)
        r = np.linalg.norm(V - c, axis=1)
        zone = (r < 2.2 * R_EYE)
        zone[mb] = False
        anchor = np.where((r > 1.9 * R_EYE) & (r < 2.4 * R_EYE))[0]
        f = RBFInterpolator(np.r_[V[mb], V[anchor]], np.r_[tgt - V[mb], np.zeros((len(anchor), 3))],
                            kernel='thin_plate_spline', smoothing=1e-5)
        zi = np.where(zone)[0]
        fall = np.clip((2.2 * R_EYE - r[zi]) / (0.3 * R_EYE), 0, 1)[:, None]
        V[zi] = V[zi] + f(V[zi]) * fall
        V[mb] = tgt
        # nothing of the lids inside the ball (front half only)
        r = np.linalg.norm(V - c, axis=1)
        inside = (r < R_EYE * LID_R) & (V[:, 2] > c[2] - 0.5 * R_EYE) & (r > 1e-6)
        V[inside] = c + (V[inside] - c) / r[inside, None] * R_EYE * LID_R
        ring = c + (V[mb] - c) / np.linalg.norm(V[mb] - c, axis=1, keepdims=True) * R_EYE * 0.94
        ids = np.arange(n0, n0 + len(mb)); n0 += len(mb)
        newV.append(ring)
        newQ.append(np.stack([mb, ids, np.roll(ids, -1), np.roll(mb, -1)], 1))
        lips[side] = ids
    return V, dict(V=np.concatenate(newV), Q=np.concatenate(newQ), ids=lips)


if __name__ == '__main__':
    main()
