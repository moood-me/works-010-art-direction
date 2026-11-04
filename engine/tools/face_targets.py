# Anny's own face settings for the engine: her local changes of the head and face (nose, mouth, eyes, brows, chin,
# cheeks, ears, forehead, the head's own scale — 129, made by people) carried onto moood's mesh as changes of moood's
# woman, for the `face` deformer (src/head/face.js) to weigh in on any body of this topology.
# How: Anny run on moood's woman's settings (experiments/anny-space/woman_ph.json) without and with each change at +1
# and at −1; the difference — smooth on Anny's own surface — sampled at moood's vertices through a map of moood's head
# onto Anny's (face_map). Т8's map (experiments/anny-space/map.npz: each moood vertex's closest point on Anny's fitted
# woman, 2.5 mm apart in the middle, 8 mm at p95) serves bodies, but on the face the two surfaces lie a few millimetres
# apart where the forms are fine and close — the lids, the nostrils, the lips: there a moood vertex's closest point is
# often on another sheet of Anny's (the other lid, the nostril's inside), and the change sampled there moved single
# vertices 3–10 mm against their neighbours (the face crumpled at the eyes, the nose and the mouth). So the head is
# mapped anew: Anny's head is first laid onto moood's surface by a smooth fit (non-rigid ICP: each round its vertices
# drawn to their closest points on moood's head where the two face the same way, the displacement kept smooth over
# Anny's own mesh, its stiffness eased round by round), so her sheets lie on moood's; then each moood vertex's closest
# point on that fitted head is its place on Anny's. Below the head Т8's map is kept. Only vertices that move more than
# 0.02 mm are kept.
# Written as a pack data/anny/face.json (+ .bin), version 2 (version 1: through Т8's map): per change its moved
# vertices and their moves at +1 and −1 (int16, in units of `unit` metres).
# python3 engine/tools/face_targets.py   (needs Anny and torch)
import os, re, json, numpy as np
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import splu
from scipy.sparse.csgraph import connected_components
import pack
from bodies_anny import Regression, SPACE, ROOT, conv, closest_on_mesh

FACE = re.compile(r'^(l-|r-)?(head|nose|mouth|eye|eyebrows|chin|cheek|ear|forehead)')
UNIT = 2e-6
# the fit: stiffness of Anny's head as it is laid on moood's, round by round (a membrane over her mesh, against the
# pull to the closest points); where the two count as facing the same way, and how near a closest point must be
# what is left where the two heads differ in kind (moood's eyes are closed slits, Anny's open over an eyeball; her
# nostrils deeper): a vertex moving unlike its neighbours — further from their median than SPIKE['mm'] and than
# SPIKE['share'] of the move there — is let go, and its move made the harmonic mean of the moves around it
SPIKE = {'mm': 0.8, 'share': 0.4}
FIT = {'stiffness': [30, 10, 4, 2, 1, 0.5, 0.25], 'rounds': 3, 'facing': 0.5, 'near': 0.012}


def normals(V, F):
    n = np.zeros_like(V); f = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    for k in range(3): np.add.at(n, F[:, k], f)
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


def laplacian(F, n):
    E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]); E = np.unique(np.sort(E, 1), axis=0)
    A = csr_matrix((np.ones(2 * len(E)), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n))
    return diags(np.asarray(A.sum(1)).ravel()) - A


def face_map(R, A0, AF, t0, bc0):
    """each moood vertex's Anny triangle and barycentrics: on the head through Anny's head fitted onto moood's (see the
    top), elsewhere Т8's"""
    W, MF = R.W0, R.F; used = np.zeros(len(W), bool); used[np.unique(MF)] = True
    sk = json.load(open(os.path.join(ROOT, 'data/skeleton.json')))['joints']; neck = R.J0[[j['name'] for j in sk].index('Neck1')]
    # Anny's skin: her mesh's largest piece (the others are her teeth and tongue, and her eyeballs — a moood vertex of
    # the lips or the lids is often nearer them than her own lips and lids)
    E = np.concatenate([AF[:, [0, 1]], AF[:, [1, 2]], AF[:, [2, 0]]]); _, piece = connected_components(csr_matrix((np.ones(len(E)), (E[:, 0], E[:, 1])), shape=(len(A0),) * 2), directed=False)
    skin = piece == np.bincount(piece).argmax()
    y0 = neck[1]; free = np.where(skin & (A0[:, 1] > y0))[0]          # Anny's vertices fitted: her head's skin down to the neck
    L = laplacian(AF, len(A0)).tocsr()[free][:, free]
    nW = normals(W, MF); U = np.zeros_like(A0); on = np.zeros(len(A0), bool)
    for k in FIT['stiffness']:
        for _ in range(FIT['rounds']):
            X = A0 + U; t, bc, d = closest_on_mesh(X[free], W, MF)
            q = (bc[:, :, None] * W[MF[t]]).sum(1); nq = (bc[:, :, None] * nW[MF[t]]).sum(1); nq /= np.linalg.norm(nq, axis=1, keepdims=True) + 1e-12
            ok = ((normals(X, AF)[free] * nq).sum(1) > FIT['facing']) & (d < FIT['near'])
            # the fade down the neck: there the fit lets go, so the head joins the body as Т8's map has it
            w = ok * np.clip((A0[free, 1] - y0) / 0.03, 0, 1)
            S = splu((diags(w) + k * L).tocsc())
            U[free] = np.stack([S.solve(w * (q[:, c] - A0[free, c])) for c in range(3)], 1)
            on[free] = ok
    # moood's head on what of Anny's was laid on it (not her mouth's inside, the eyes' sockets: they found no surface)
    X, mine, tris = A0 + U, np.where(used & (W[:, 1] > y0 + 0.02))[0], np.where(on[AF].all(1))[0]
    t, bc, d = closest_on_mesh(W[mine], X, AF[tris]); t = tris[t]
    T, BC = t0.copy(), bc0.copy(); T[mine], BC[mine] = t, bc
    print('the head fitted: moood\'s head from Anny\'s fitted head mm mean %.2f, p95 %.2f, max %.2f (Т8\'s map: mean %.2f, p95 %.2f)' % (
        d.mean() * 1e3, np.percentile(d, 95) * 1e3, d.max() * 1e3, *[f(np.linalg.norm(W[mine] - (bc0[mine, :, None] * A0[AF[t0[mine]]]).sum(1), axis=1)) * 1e3 for f in (np.mean, lambda a: np.percentile(a, 95))]), flush=True)
    return T, BC


def despike(d, nbr, L):
    """the change d (N×3) with its spikes let go and filled in from around them (see SPIKE), and how many"""
    d = d.copy(); free = np.zeros(len(d), bool)
    for _ in range(3):
        near = d[np.maximum(nbr, 0)]; near[nbr < 0] = np.nan; m = np.nanmedian(near, axis=1)
        r = np.linalg.norm(d - m, axis=1); spike = (r > SPIKE['mm'] * 1e-3) & (r > SPIKE['share'] * np.linalg.norm(m, axis=1)) & ~free & (nbr[:, 0] >= 0)
        if not spike.any(): break
        free |= spike; f = np.where(free)[0]; k = np.where(~free)[0]
        S = splu(L[f][:, f].tocsc())
        d[f] = np.stack([S.solve(-(L[f][:, k] @ d[k, c])) for c in range(3)], 1)
    return d, int(free.sum())


if __name__ == '__main__':
    R = Regression(); M = np.load(os.path.join(SPACE, 'map.npz')); AF = M['F'].astype(np.int64)
    run = lambda lc: conv(R.run(ph, lc)[0]['vertices'])
    ph = R.ph; a0 = run({})
    A0 = np.load(os.path.join(SPACE, 'anny_woman.npy'))          # Anny's fitted woman in moood's place (a translation of a0)
    t, bc = face_map(R, A0, AF, M['t'], M['bc'])
    sample = lambda P: bc[:, :1] * P[AF[t, 0]] + bc[:, 1:2] * P[AF[t, 1]] + bc[:, 2:] * P[AF[t, 2]]
    v0 = sample(a0)
    # moood's mesh: each used vertex's neighbours (−1 past its last), its Laplacian
    MF = R.F; L = laplacian(MF, len(R.W0)).tocsr(); nb = [L.indices[L.indptr[i]:L.indptr[i + 1]] for i in range(len(R.W0))]
    nb = [x[x != i] for i, x in enumerate(nb)]; nbr = -np.ones((len(nb), max(map(len, nb))), np.int64)
    for i, x in enumerate(nb): nbr[i, :len(x)] = x
    labels = sorted(l for l in R.mA.local_change_labels if FACE.match(l))
    arrays, changes = {}, []
    for k, l in enumerate(labels):
        (dp, sp), (dn, sn) = despike(sample(run({l: 1.0})) - v0, nbr, L), despike(sample(run({l: -1.0})) - v0, nbr, L)
        moved = np.where((np.linalg.norm(dp, axis=1) > 2e-5) | (np.linalg.norm(dn, axis=1) > 2e-5))[0]
        if not len(moved): continue
        big = max(np.abs(dp).max(), np.abs(dn).max())
        if big / UNIT > 32000: raise ValueError(f'{l}: moves {big} m, more than int16 of {UNIT} m holds')
        arrays[f'i{k}'] = moved.astype(np.uint32)
        arrays[f'p{k}'] = np.round(dp[moved] / UNIT).astype(np.int16); arrays[f'n{k}'] = np.round(dn[moved] / UNIT).astype(np.int16)
        lin = np.abs(dp[moved] + dn[moved]).max()   # how far from linear: +1 and −1 not opposite
        changes.append({'name': l, 'key': k, 'vertices': int(len(moved)), 'most': round(float(big), 5), 'unlinear': round(float(lin), 5), 'spikes': [sp, sn]})
        print(l, len(moved), 'most %.1f mm' % (big * 1000), 'unlinear %.2f mm' % (lin * 1000), 'spikes let go %d, %d' % (sp, sn), flush=True)
    pack.write(os.path.join(ROOT, 'data/anny/face.json'), {'format': 'engine/face-targets', 'version': 2, 'topology': 'anny-moood', 'unit': UNIT,
        'about': "Anny's local changes of the head and face (tools/face_targets.py), on moood's mesh as changes of moood's woman at +1 and −1, sampled through moood's head mapped onto Anny's fitted onto it; i<key>: the vertices moved, p<key>/n<key>: their moves (int16 × unit metres)",
        'fit': FIT, 'changes': changes}, arrays)
    print(len(changes), 'changes')
