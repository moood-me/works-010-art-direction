# New bodies from Anny's own settings (data/anny/specs.json): Anny run from her phenotype sliders and local targets
# (and, when asked, a head of another age), carried onto moood's mesh and given Anny's own joints — the same way as Т8's
# bodies (experiments/anny-space: gen.py, tomoood2.py; tools/bodies_anny.py), in one step, written as engine bodies
# data/bodies/<id>.json.
#
# How (Т8's way, checked to give its bodies again exactly: d-C-hero.bin within 1e-7 m):
#   1. Anny (github.com/naver/anny) gives the body's vertices on her own topology; a head of another age is Anny run
#      again with the head's settings, its head scaled to r × the body's head height and blended in over the neck
#      (gen.py);
#   2. carried onto moood's mesh as a change: moood's woman + (the new Anny − Anny fitted to moood's woman), the change
#      sampled at moood's vertices (experiments/anny-space/map.npz), smoothed by 6 steps over moood's mesh so it is a
#      smooth field moood's own features ride on (tomoood2.py), standing on the floor;
#   3. joints and frames by Anny's SOMA regression carried onto moood's mesh (bodies_anny.Regression).
# python3 engine/tools/bodies_new.py [ids…]   (needs Anny and torch; reads experiments/anny-space, writes data/bodies)
import json, os, sys, numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial.transform import Rotation as Rot
import pack
from bodies_anny import Regression, SPACE, ROOT
from bodies_moood import body_file

SMOOTH = 6


class Transfer:
    """Anny's surface carried onto moood's mesh as a smooth change from moood's woman (tomoood2.py)."""

    def __init__(self, R):
        M = np.load(os.path.join(SPACE, 'map.npz')); self.t, self.bc = M['t'], M['bc']; self.AF = M['F']
        self.shift = np.load(os.path.join(SPACE, 'shift.npy')); self.A0 = np.load(os.path.join(SPACE, 'anny_woman.npy'))
        self.W0 = R.W0; F = R.F; N = len(self.W0)
        nb = [set() for _ in range(N)]
        for a, b, c in F: nb[a] |= {b, c}; nb[b] |= {a, c}; nb[c] |= {a, b}
        rows = np.repeat(np.arange(N), [len(s) for s in nb]); cols = np.concatenate([np.fromiter(s, np.int64) for s in nb if s])
        self.deg = np.array([len(s) for s in nb]); self.L = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N))

    def sample(self, P):
        t, bc, F = self.t, self.bc, self.AF
        return bc[:, :1] * P[F[t, 0]] + bc[:, 1:2] * P[F[t, 1]] + bc[:, 2:] * P[F[t, 2]]

    def __call__(self, v):
        d = self.sample(v + self.shift) - self.sample(self.A0)
        for _ in range(SMOOTH):
            nd = self.L @ d; d = np.where(self.deg[:, None] > 0, 0.5 * d + 0.5 * nd / np.maximum(self.deg, 1)[:, None], d)
        out = self.W0 + d; out[:, 1] -= out[:, 1].min()
        return out


class Maker:
    """Anny's vertices for a spec (gen.py), on her own topology, y up, standing on the floor."""

    def __init__(self, R):
        import torch
        self.torch, self.m = torch, R.mA
        bones = list(self.m.bone_labels); bw = self.m.vertex_bone_weights.numpy(); bi = self.m.vertex_bone_indices.numpy()
        boneW = lambda names: (bw * np.isin(bi, [bones.index(n) for n in names])).sum(1)
        F = self.m.faces.numpy().astype(np.int64); V = len(bw)
        nb = [set() for _ in range(V)]
        for a, b, c in F: nb[a] |= {b, c}; nb[b] |= {a, c}; nb[c] |= {a, b}
        nb = [np.array(sorted(s)) for s in nb]
        def smooth(w, it):
            for _ in range(it): w = np.array([0.5 * w[i] + 0.5 * w[n].mean() if len(n) else w[i] for i, n in enumerate(nb)])
            return w
        self.headW = boneW(['head', 'eye.L', 'eye.R'])
        self.blend = smooth(np.clip((self.headW + 0.7 * boneW(['neck03']) + 0.25 * boneW(['neck02'])) * 1.2, 0, 1), 6)
        self.neckBand = boneW(['neck02', 'neck03'])
        self.labels = set(self.m.local_change_labels)

    def run(self, ph, lc):
        torch = self.torch
        phk = {k: torch.tensor([float(v)]) for k, v in ph.items()}; lck = {}
        for k, v in lc.items():
            hits = [k] if k in self.labels else [l for l in self.labels if l in ('l-' + k, 'r-' + k)]
            if not hits: raise ValueError(f'Anny has no local change {k}')
            for h in hits: lck[h] = torch.tensor([float(v)])
        with torch.no_grad(): v = self.m(phenotype_kwargs=phk or None, local_changes_kwargs=lck or None)['vertices'][0].numpy().astype(np.float64)
        return np.stack([v[:, 0], v[:, 2], -v[:, 1]], 1)

    def __call__(self, s):
        v = self.run(s.get('ph', {}), s.get('lc', {}))
        if 'head' in s:
            h = s['head']; d = self.run(h.get('ph', s.get('ph', {})), h.get('lc', {}))
            nb = self.neckBand; aT = (v * nb[:, None]).sum(0) / nb.sum(); aS = (d * nb[:, None]).sum(0) / nb.sum()
            hm = self.headW > 0.5; size = lambda x: np.ptp(x[hm, 1])
            d2 = (d - aS) * (h.get('r', 1.0) * size(v) / size(d)) + aT
            v = v * (1 - self.blend[:, None]) + d2 * self.blend[:, None]
        v[:, 1] -= v[:, 1].min()
        return v


if __name__ == '__main__':
    spec = json.load(open(os.path.join(ROOT, 'data/anny/specs.json')))
    want = set(sys.argv[1:])
    R = Regression(); T = Transfer(R); A = Maker(R)
    for s in spec['bodies']:
        if want and s['id'] not in want: continue
        V = T(A(s)); J = R.joints(V); Q = R.frames(V, J)
        body_file(s['id'], (s['label']['ru'], s['label']['en']), f"data/anny/specs.json ({s['id']}): Anny's own settings run by tools/bodies_new.py, "
                  "carried onto moood's mesh as Т8's bodies are; joints by Anny's SOMA regression carried onto this mesh", V, Rot.from_quat(Q).as_matrix(), J,
                  {'anny': {k: s[k] for k in ['ph', 'lc', 'head'] if k in s}})
        print(s['id'], 'height %.3f' % (V[:, 1].max() - V[:, 1].min()), flush=True)
