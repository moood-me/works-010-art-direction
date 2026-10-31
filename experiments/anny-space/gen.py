# usage: python3 gen.py specs.json  -> out/<name>.bin (float32 V*3, y-up, metres), out/faces.bin
# a spec: {name, ph: phenotype, lc: local changes, head: {ph, lc, r}} — head takes another Anny's head, r its size
import sys, json, numpy as np, torch, anny
specs = json.load(open(sys.argv[1]))
m = anny.Anny(phenotypes="all", local_changes="default", extrapolate_phenotypes=True).to(dtype=torch.float32)
F = m.faces.numpy().astype(np.int64); F.astype(np.uint16).tofile('out/faces.bin')
labels = set(m.local_change_labels); bones = list(m.bone_labels)
bw = m.vertex_bone_weights.numpy(); bi = m.vertex_bone_indices.numpy()
def boneW(names):
    ids = [bones.index(n) for n in names]
    return (bw * np.isin(bi, ids)).sum(1)
V = len(bw)
nb = [set() for _ in range(V)]
for a, b, c in F: nb[a] |= {b, c}; nb[b] |= {a, c}; nb[c] |= {a, b}
nb = [np.array(sorted(s)) for s in nb]
def smooth(w, it):
    for _ in range(it): w = np.array([0.5 * w[i] + 0.5 * w[n].mean() if len(n) else w[i] for i, n in enumerate(nb)])
    return w
headW = boneW(['head', 'eye.L', 'eye.R'])
blend = smooth(np.clip((headW + 0.7 * boneW(['neck03']) + 0.25 * boneW(['neck02'])) * 1.2, 0, 1), 6)
neckBand = boneW(['neck02', 'neck03'])
def run(ph, lc):
    phk = {k: torch.tensor([float(v)]) for k, v in ph.items()}
    lck = {}
    for k, v in lc.items():
        hits = [k] if k in labels else [l for l in labels if l in ('l-' + k, 'r-' + k)]
        if not hits: print('unknown', k)
        for h in hits: lck[h] = torch.tensor([float(v)])
    with torch.no_grad(): v = m(phenotype_kwargs=phk or None, local_changes_kwargs=lck or None)['vertices'][0].numpy()
    return np.stack([v[:, 0], v[:, 2], -v[:, 1]], 1)
for s in specs:
    v = run(s.get('ph', {}), s.get('lc', {}))
    if 'head' in s:
        h = s['head']; d = run(h.get('ph', s.get('ph', {})), h.get('lc', {}))
        aT = (v * neckBand[:, None]).sum(0) / neckBand.sum(); aS = (d * neckBand[:, None]).sum(0) / neckBand.sum()
        hm = headW > 0.5
        size = lambda x: np.ptp(x[hm, 1])
        sc = h.get('r', 1.0) * size(v) / size(d)
        d2 = (d - aS) * sc + aT
        v = v * (1 - blend[:, None]) + d2 * blend[:, None]
    v[:, 1] -= v[:, 1].min()
    v.astype(np.float32).tofile(f"out/{s['name']}.bin")
    print(s['name'], 'height %.3f' % v[:, 1].max())
