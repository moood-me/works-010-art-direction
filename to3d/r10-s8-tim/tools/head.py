"""Тим's head: the Human Base Meshes stylised head (CC0) fitted to the drawing's own 3D head (the loft of
styles/s8-stopmotion `cast.TIM`), so front, three-quarter and profile all come from one shape.

Two levels, so the sculptor's features survive the fit:
1. The eye-socket linings are cut away (faces inside the base's eyeballs): the lid margins become two clean loops.
   The mouth's bag is kept but left out of the next steps.
2. A smooth version of the base (implicit fairing, margins and lips' seam held) carries the big form; the base minus
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
R_EYE = P['eye_r']
LID_R = 1.04            # the lid margin's distance from the eye's centre, in eyeball radii
K_NOSE, K_LIPS, K_FACE, K_EAR = 0.5, 0.75, 0.75, 1.0


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


def targets():
    LV, LT = drawing.loft_mesh(160, 160)
    NV = drawing.neck_mesh(64, 40)
    nphi = 64; NT = []
    for i in range(39):
        for j in range(nphi):
            a, b = i * nphi + j, i * nphi + (j + 1) % nphi
            NT += [[a, a + nphi, b], [b, a + nphi, b + nphi]]
    return np.r_[LV, NV], np.r_[LT, np.array(NT) + len(LV)]


def main():
    B = base.load()
    V0, Q = B['V'].copy(), B['Q'].copy()
    T0 = base.tris(Q)
    N0 = vertex_normals(V0, T0)
    ao = igl.ambient_occlusion(V0, T0, V0 + N0 * 1e-4, N0, 64)
    # 1. cut the eye linings
    keep = np.ones(len(Q), bool)
    for s in 'LR':
        e = B['eye' + s][0]; c = e.mean(0); r = np.ptp(e[:, 0]) / 2
        keep &= ~(np.linalg.norm(V0[Q] - c, axis=2) < 0.97 * r).all(1)
    Q = Q[keep]
    used = np.unique(Q); remap = -np.ones(len(V0), int); remap[used] = np.arange(len(used))
    V0, Q, ao = V0[used], remap[Q], ao[used]
    T = base.tris(Q)
    adj = igl.adjacency_list(T)
    margins = {}
    for l in base.loops(Q):
        margins[1 if V0[l, 0].mean() > 0 else -1] = np.array(l)
    assert len(margins) == 2
    bag = (np.abs(V0[:, 0]) < 0.2) & (V0[:, 1] < -0.28) & (V0[:, 1] > -0.42) & (ao > 0.9)

    # 2. the smooth form (without the bag)
    keepS = ~bag[Q].all(1)
    QS = Q[keepS]; TS = base.tris(QS)
    inS = np.zeros(len(V0), bool); inS[np.unique(QS)] = True
    bnd = np.unique(np.concatenate(base.loops(QS)))
    S = V0.copy()
    W = np.zeros(len(V0)); W[bnd] = 1e3; W[~inS] = 1.0
    for it in range(8):
        L = igl.cotmatrix(S, TS); M = igl.massmatrix(S, TS, igl.MASSMATRIX_TYPE_VORONOI)
        A = (M - 1e-3 * L + diags(W)).tocsc()
        b = M @ S + W[:, None] * S
        S = np.column_stack([spsolve(A, b[:, k]) for k in range(3)])
    NS = vertex_normals(S, TS)
    tS, bS = frames(NS)
    D = V0 - S
    det = np.c_[(D * NS).sum(1), (D * tS).sum(1), (D * bS).sum(1)]

    # 3. the smooth form onto the loft
    TV, TT = targets()
    src, dst = [], []
    for side in (1, -1):
        Cd, _ = drawing.eye_opening(side, drawing.EXPR['calm'], n=80)
        mb = margins[side]
        src += list(mb); dst += list(match_by_angle(S[mb], Cd))
    seam = np.array([i for i in np.where(bag)[0] if any(not bag[k] for k in adj[i])
                     and V0[i, 2] > 0.3 and -0.335 < V0[i, 1] < -0.305])
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
    nose = (np.abs(V0[:, 0]) < 0.22) & (V0[:, 1] > -0.3) & (V0[:, 1] < -0.04) & (V0[:, 2] > 0.4)
    lips = (np.abs(V0[:, 0]) < 0.17) & (V0[:, 1] < -0.24) & (V0[:, 1] > -0.46) & (V0[:, 2] > 0.3) & ~nose
    ear = {s: (s * V0[:, 0] > 0.36) & (V0[:, 1] > -0.24) & (V0[:, 1] < 0.12) & (V0[:, 2] > -0.1) & (V0[:, 2] < 0.13)
           for s in (1, -1)}
    k = np.full(len(V0), K_FACE)
    k = k + (K_NOSE - K_FACE) * smooth_mask(nose, adj, 6) + (K_LIPS - K_FACE) * smooth_mask(lips, adj, 4)
    k = k + (K_EAR - K_FACE) * smooth_mask(ear[1] | ear[-1], adj, 3)
    neck = (V0[:, 1] < -0.47) & (V0[:, 2] < 0.25)
    k = k * (1 - smooth_mask(neck, adj, 6))
    V = S1 + k[:, None] * (det[:, :1] * N1 + det[:, 1:2] * t1 + det[:, 2:] * b1)
    # the bag follows its lips: displacement interpolated from the mouth's neighbourhood
    near = np.where(inS & (np.linalg.norm(V0 - V0[seam].mean(0), axis=1) < 0.2))[0]
    f = RBFInterpolator(V0[near], (V - V0)[near], kernel='linear', neighbors=60, smoothing=1e-4)
    V[~inS] = V0[~inS] + f(V0[~inS])

    V = fix_ears(V, ear, adj)
    V, lip = fix_eyes(V, Q, margins, adj)
    Q = np.r_[Q, lip['Q']]
    V = np.r_[V, lip['V']]
    np.savez(f'{CACHE}/head_raw.npz', V=V, Q=Q, S=S, S1=S1, V0=V0, mL=margins[1], mR=margins[-1], bag=bag,
             seam=seam, earL=ear[1], earR=ear[-1], nose=nose, lips=lips)
    print('head raw', V.min(0).round(3), V.max(0).round(3))


def fix_ears(V, ear, adj):
    """carry each ear whole onto the drawing's: about its root, scaled to the drawing's height, turned so it stands
    out by the drawing's angle; blended into the head over a few rings"""
    for side in (1, -1):
        m = ear[side]
        w = smooth_mask(m, adj, 4)
        E = V[m]
        ax = np.abs(E[:, 0])
        root = E[ax < ax.min() + 0.025].mean(0)
        outer = E[ax > np.percentile(ax, 70)].mean(0)
        u0 = outer - root; u0[1] = 0; u0 /= np.linalg.norm(u0)
        pts, droot, du = drawing.ear_plate(side)
        du = du.copy(); du[1] = 0; du /= np.linalg.norm(du)
        ang = math.atan2(du[0], du[2]) - math.atan2(u0[0], u0[2])
        c, s = math.cos(ang), math.sin(ang)
        Rm = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        sc = np.ptp(pts[:, 1]) / np.ptp(E[:, 1]) * 1.12
        ctr_d = pts.mean(0); ctr_b = E.mean(0)
        moved = droot + sc * (Rm @ (V - root).T).T
        # keep the ear's middle where the drawing's is (height), the root on the skull
        moved[:, 1] += (ctr_d[1] - (droot[1] + sc * (ctr_b[1] - root[1])))
        V = V + w[:, None] * (moved - V)
        print('ear', side, 'turn', round(math.degrees(ang), 1), 'scale', round(sc, 2))
    return V


def fix_eyes(V, Q, margins, adj):
    """the glass balls at the drawing's places; the margins onto the drawing's opening laid on the ball; the lid
    region kept outside the ball; a short lip from each margin in toward the ball's centre"""
    newV, newQ = [], []
    n0 = len(V)
    lips = {}
    for side in (1, -1):
        c = drawing.eye_centre(side)
        mb = margins[side]
        Cd, _ = drawing.eye_opening(side, drawing.EXPR['calm'], n=80)
        Cd = c + (Cd - c) / np.linalg.norm(Cd - c, axis=1, keepdims=True) * R_EYE * LID_R
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
