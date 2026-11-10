# Т8's bodies — Anny's own settings carried onto moood's mesh (experiments/anny-space/out/d-*.bin) — as engine bodies,
# with real joints: Anny's own SOMA joint regression, applied to each body's own surface.
#
# How. Anny's SOMA rig (anny.models.soma) places each of SOMA's joints as a fixed linear combination of its SOMA-topology
# mesh's vertices (`sparse_rbf_matrix`, RBF regression). The regression is carried onto moood's mesh once: Anny's
# SOMA-topology surface of the woman fitted to moood's (experiments/anny-space/woman_ph.json) is laid onto moood's woman
# (each SOMA vertex: its closest point there, a triangle and barycentrics). A body's joints are then moood woman's joints
# plus the regression of how its surface moved from hers — the joints follow the body's own final surface, the head of
# another age and the smoothing included. Each joint's frame turns as its bone does: a joint with one child bone by the
# smallest turn that carries the bone's direction, others by the best rotation (Kabsch) of the skin they carry.
#
# python3 tools/bodies_anny.py [--check]   (needs Anny: github.com/naver/anny, `pip install` it; torch)
# --check: compares the carried regression with Anny's own exact joints on bodies made from Anny's settings alone.
import json, os, sys, numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation as Rot
import pack
from soma import NAMES
from bodies_moood import body_file

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPACE = os.path.join(ROOT, '..', 'experiments', 'anny-space')
conv = lambda v: np.stack([v[..., 0], v[..., 2], -v[..., 1]], -1)       # Anny's axes (z up) to ours (y up)
C = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)                  # the same as a matrix

RU = {'W': 'женщина moood (Anny)', 'C-princess': 'принцесса', 'C-hero': 'герой', 'C-elf': 'эльф', 'C-andro': 'андрогин', 'C-pear': 'груша',
      'C-square': 'квадрат', 'C-old': 'старая', 'C-bean': 'фасолина', 'C-burton': 'Бёртон', 'C-chibi': 'чиби',
      'T-W-child12': 'женщина + голова ребёнка', 'T-W-tod13': 'женщина + голова малыша', 'T-W-H2-25': 'женщина + своя голова ×2.5',
      'T-princ-tod125': 'принцесса + голова малыша', 'T-teen-tod14': 'девушка + голова малыша', 'T-girl-baby12': 'девочка + голова младенца',
      'T-kid-baby14': 'ребёнок + голова младенца', 'T-chibi-baby17': 'чиби + голова младенца', 'T-burton-tod16': 'Бёртон + голова малыша',
      'T-hero-child09': 'герой + голова ребёнка', 'T-man-tod13': 'мужчина + голова малыша', 'T-man-stocky-baby15': 'коренастый + голова младенца',
      'T-old-H2': 'старая + своя голова'}


def closest_on_mesh(P, V, F):
    """each point's closest point on the mesh (V, F): its triangle and barycentrics."""
    cent = V[F].mean(1); _, cand = cKDTree(cent).query(P, k=16)
    best_t = np.zeros(len(P), int); best_bc = np.zeros((len(P), 3)); best_d = np.full(len(P), np.inf)
    for j in range(cand.shape[1]):
        t = cand[:, j]; a, b, c = V[F[t, 0]], V[F[t, 1]], V[F[t, 2]]
        # Ericson's closest point on a triangle, by regions
        ab, ac, ap = b - a, c - a, P - a
        d1, d2 = (ab * ap).sum(1), (ac * ap).sum(1)
        bp = P - b; d3, d4 = (ab * bp).sum(1), (ac * bp).sum(1)
        cp = P - c; d5, d6 = (ab * cp).sum(1), (ac * cp).sum(1)
        va, vb, vc = d3 * d6 - d5 * d4, d5 * d2 - d1 * d6, d1 * d4 - d3 * d2
        bc = np.zeros((len(P), 3))
        den = np.where(va + vb + vc == 0, 1e-30, va + vb + vc)
        bc[:, 1], bc[:, 2] = vb / den, vc / den; bc[:, 0] = 1 - bc[:, 1] - bc[:, 2]
        def setr(m, w):
            bc[m] = w[m]
        r = (d1 <= 0) & (d2 <= 0); setr(r, np.tile([1, 0, 0], (len(P), 1)))
        r2 = (d3 >= 0) & (d4 <= d3) & ~r; setr(r2, np.tile([0, 1, 0], (len(P), 1)))
        r3 = (d6 >= 0) & (d5 <= d6) & ~r & ~r2; setr(r3, np.tile([0, 0, 1], (len(P), 1)))
        done = r | r2 | r3
        e = (vc <= 0) & (d1 >= 0) & (d3 <= 0) & ~done; v = d1 / np.where(d1 - d3 == 0, 1e-30, d1 - d3)
        setr(e, np.stack([1 - v, v, 0 * v], 1)); done |= e
        e = (vb <= 0) & (d2 >= 0) & (d6 <= 0) & ~done; w = d2 / np.where(d2 - d6 == 0, 1e-30, d2 - d6)
        setr(e, np.stack([1 - w, 0 * w, w], 1)); done |= e
        e = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0) & ~done; w = (d4 - d3) / np.where((d4 - d3) + (d5 - d6) == 0, 1e-30, (d4 - d3) + (d5 - d6))
        setr(e, np.stack([0 * w, 1 - w, w], 1))
        q = bc[:, :1] * a + bc[:, 1:2] * b + bc[:, 2:] * c
        d = np.linalg.norm(P - q, axis=1); m = d < best_d
        best_d[m], best_t[m], best_bc[m] = d[m], t[m], bc[m]
    return best_t, best_bc, best_d


class Regression:
    """Anny's SOMA joint regression carried onto moood's mesh (see the top of this file)."""

    def __init__(self):
        import torch, anny
        from anny.models.soma import _load_soma_rig
        self.torch, self.anny = torch, anny
        rig = _load_soma_rig()
        assert [str(x) for x in rig['bone_labels']][1:] == NAMES
        self.rbf = rig['sparse_rbf_matrix'].to_dense().numpy().astype(np.float64)          # (78, 18056); row 0 Root = Hips
        self.rbf[0] = self.rbf[1]
        self.mA = anny.Anny(phenotypes='all', local_changes='default', extrapolate_phenotypes=True).to(dtype=torch.float32)
        self.mS = anny.Anny(rig='soma', topology='soma', phenotypes='all', local_changes='default', extrapolate_phenotypes=True).to(dtype=torch.float32)
        self.ph = json.load(open(os.path.join(SPACE, 'woman_ph.json')))
        self.labels = set(self.mS.local_change_labels)
        # moood's woman and her joints
        th, ta = pack.read(os.path.join(ROOT, 'data/topology/anny-moood.json'))
        wh, wa = pack.read(os.path.join(ROOT, 'data/bodies/moood-woman.json'))
        self.F = ta['triangles'].astype(int); self.skinJ = ta['skinJoints'].astype(int); self.skinW = ta['skinWeights'].astype(np.float64)
        self.W0 = wa['positions'].astype(np.float64); self.J0 = wa['joints'].astype(np.float64); self.Q0 = wa['frames'].astype(np.float64)
        # Anny's SOMA surface of the fitted woman, in moood's place: the axes as fit.py has them, then the small offset
        # between the two surfaces found by laying one on the other
        sA, sS = self.run(self.ph, {})
        A0 = np.load(os.path.join(SPACE, 'anny_woman.npy'))
        off = (A0 - conv(sA['vertices'])).mean(0)
        S = conv(sS['rest_vertices']) + off
        for _ in range(4):
            t, bc, d = closest_on_mesh(S, self.W0, self.F)
            q = (bc[:, :, None] * self.W0[self.F[t]]).sum(1)
            S = S + np.median(q - S, 0)
        self.t, self.bc, self.d = closest_on_mesh(S, self.W0, self.F)
        self.fitS = sS
        print('SOMA surface on moood woman: mm mean %.1f, p95 %.1f' % (self.d.mean() * 1e3, np.percentile(self.d, 95) * 1e3))

    def run(self, ph, lc):
        torch = self.torch
        phk = {k: torch.tensor([float(v)]) for k, v in ph.items()}
        lck = {}
        for k, v in lc.items():
            hits = [k] if k in self.labels else [l for l in self.labels if l in ('l-' + k, 'r-' + k)]
            for h in hits: lck[h] = torch.tensor([float(v)])
        with torch.no_grad():
            a = self.mA(phenotype_kwargs=phk or None, local_changes_kwargs=lck or None)
            s = self.mS(phenotype_kwargs=phk or None, local_changes_kwargs=lck or None)
        g = lambda o: {k: v[0].numpy().astype(np.float64) for k, v in o.items()}
        return g(a), g(s)

    def joints(self, V):
        """moood woman's joints, moved as Anny's regression moves them for the surface V (moood's mesh)."""
        dV = V - self.W0
        dS = (self.bc[:, :, None] * dV[self.F[self.t]]).sum(1)
        return self.J0 + (self.rbf @ dS)[1:]

    def frames(self, V, J):
        """each joint's frame, turned from moood woman's as its bone turned (see the top)."""
        R0 = Rot.from_quat(self.Q0).as_matrix(); out = np.zeros_like(R0)
        kids = {j: [k for k in range(77) if PARENT[k] == j] for j in range(77)}
        for j in range(77):
            ks = [k for k in kids[j] if np.linalg.norm(self.J0[k] - self.J0[j]) > 1e-4]
            if len(ks) == 1:
                a = self.J0[ks[0]] - self.J0[j]; b = J[ks[0]] - J[j]
                out[j] = swing(a, b) @ R0[j]
                continue
            w = (self.skinW * (self.skinJ == j)).sum(1)
            m = w > 0.05
            if m.sum() < 4:
                out[j] = out[PARENT[j]] @ R0[PARENT[j]].T @ R0[j] if PARENT[j] >= 0 else R0[j]
                continue
            X = self.W0[m] - self.J0[j]; Y = V[m] - J[j]; ww = w[m][:, None]
            H = (X * ww).T @ Y
            U, _, Vt = np.linalg.svd(H); Dg = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
            out[j] = (Vt.T @ Dg @ U.T) @ R0[j]
        return Rot.from_matrix(out).as_quat()


def swing(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = a @ b
    if c < -0.999999: raise ValueError('a bone turned around')
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K / (1 + c)


SK = json.load(open(os.path.join(ROOT, 'data/skeleton.json')))
PARENT = [j['parent'] for j in SK['joints']]


def check(R):
    """the carried regression against Anny's own exact joints, for bodies made of Anny's settings alone (s3.json): each
    body's Anny surface is sampled at moood's vertices (map.npz: moood vertex -> Anny triangle) as a change from the
    fitted woman's, added to moood's woman — the test body; its exact joints are Anny's own (SOMA topology, which Anny
    places with a global offset of its own: laid onto the Anny-topology surface by a translation first)."""
    M = np.load(os.path.join(SPACE, 'map.npz')); mt, mbc, AF = M['t'], M['bc'], M['F']
    specs = {s['name']: s for f in ['s3.json'] for s in json.load(open(os.path.join(SPACE, f)))}
    def exact(ph, lc):
        a, S = R.run(ph, lc); A = conv(a['vertices']); Ss = conv(S['rest_vertices']); T = np.zeros(3)
        for _ in range(4):
            t, bc, d = closest_on_mesh(Ss + T, A, AF)
            T += np.median((bc[:, :, None] * A[AF[t]]).sum(1) - (Ss + T), 0)
        return (mbc[:, :, None] * A[AF[mt]]).sum(1), conv(S['rest_bone_heads'][1:]) + T
    p0, j0 = exact(R.ph, {})
    for name in ['C-hero', 'C-chibi', 'C-pear', 'C-elf', 'C-princess', 'C-bean']:
        s = specs[name]; p, j = exact(s.get('ph', {}), s.get('lc', {}))
        V = R.W0 + p - p0; want = R.J0 + j - j0
        e = np.linalg.norm(R.joints(V) - want, axis=1) * 1e3; big = np.argsort(-e)[:3]
        print(f'{name}: joints against Anny exact: mean {e.mean():.1f} mm, max {e.max():.1f} ({", ".join(NAMES[i] for i in big)}); '
              f'the guess from skin displacement (view.html): mean {np.linalg.norm(guess(R, V) - want, axis=1).mean() * 1e3:.1f} mm')


def guess(R, V):
    """view.html's guess (each joint moved as the skin hung on it moved) — for comparison only"""
    J = R.J0.copy()
    for j in range(77):
        w = (R.skinW * (R.skinJ == j)).sum(1)
        if w.sum() > 1e-6: J[j] = R.J0[j] + (w[:, None] * (V - R.W0)).sum(0) / w.sum()
    return J


if __name__ == '__main__':
    R = Regression()
    if '--check' in sys.argv: check(R); sys.exit()
    index = []
    for f in sorted(os.listdir(os.path.join(SPACE, 'out'))):
        if not f.startswith('d-') or not f.endswith('.bin'): continue
        name = f[2:-4]
        V = np.fromfile(os.path.join(SPACE, 'out', f), np.float32).reshape(-1, 3).astype(np.float64)
        J = R.joints(V); Q = R.frames(V, J)
        bid = 'anny-' + name
        body_file(bid, (RU.get(name, name), name), f'experiments/anny-space/out/{f}: Anny\'s own settings (Т8) on moood\'s mesh; '
                  'joints by Anny\'s SOMA regression carried onto this mesh (tools/bodies_anny.py)', V, Rot.from_quat(Q).as_matrix(), J)
        print(bid, 'height %.3f' % (V[:, 1].max() - V[:, 1].min()))
