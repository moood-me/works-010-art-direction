# Anny's own face settings for the engine: her local changes of the head and face (nose, mouth, eyes, brows, chin,
# cheeks, ears, forehead, the head's own scale — 129, made by people) carried onto moood's mesh as changes of moood's
# woman, for the `face` deformer (src/head/face.js) to weigh in on any body of this topology.
# How: Anny run on moood's woman's settings (experiments/anny-space/woman_ph.json) without and with each change at +1
# and at −1; the difference sampled at moood's vertices through the map Т8 made (experiments/anny-space/map.npz) — no
# smoothing: a difference of two Anny surfaces is smooth by itself. Only vertices that move more than 0.02 mm are kept.
# Written as a pack data/anny/face.json (+ .bin): per change its moved vertices and their moves at +1 and −1 (int16,
# in units of `unit` metres).
# python3 engine/tools/face_targets.py   (needs Anny and torch)
import os, re, json, numpy as np
import pack
from bodies_anny import Regression, SPACE, ROOT, conv

FACE = re.compile(r'^(l-|r-)?(head|nose|mouth|eye|eyebrows|chin|cheek|ear|forehead)')
UNIT = 2e-6

if __name__ == '__main__':
    R = Regression(); M = np.load(os.path.join(SPACE, 'map.npz')); t, bc, AF = M['t'], M['bc'], M['F'].astype(np.int64)
    sample = lambda P: bc[:, :1] * P[AF[t, 0]] + bc[:, 1:2] * P[AF[t, 1]] + bc[:, 2:] * P[AF[t, 2]]
    run = lambda lc: conv(R.run(ph, lc)[0]['vertices'])
    ph = R.ph; v0 = sample(run({}))
    labels = sorted(l for l in R.mA.local_change_labels if FACE.match(l))
    arrays, changes = {}, []
    for k, l in enumerate(labels):
        dp = sample(run({l: 1.0})) - v0; dn = sample(run({l: -1.0})) - v0
        moved = np.where((np.linalg.norm(dp, axis=1) > 2e-5) | (np.linalg.norm(dn, axis=1) > 2e-5))[0]
        if not len(moved): continue
        big = max(np.abs(dp).max(), np.abs(dn).max())
        if big / UNIT > 32000: raise ValueError(f'{l}: moves {big} m, more than int16 of {UNIT} m holds')
        arrays[f'i{k}'] = moved.astype(np.uint32)
        arrays[f'p{k}'] = np.round(dp[moved] / UNIT).astype(np.int16); arrays[f'n{k}'] = np.round(dn[moved] / UNIT).astype(np.int16)
        lin = np.abs(dp[moved] + dn[moved]).max()   # how far from linear: +1 and −1 not opposite
        changes.append({'name': l, 'key': k, 'vertices': int(len(moved)), 'most': round(float(big), 5), 'unlinear': round(float(lin), 5)})
        print(l, len(moved), 'most %.1f mm' % (big * 1000), 'unlinear %.2f mm' % (lin * 1000), flush=True)
    pack.write(os.path.join(ROOT, 'data/anny/face.json'), {'format': 'engine/face-targets', 'version': 1, 'topology': 'anny-moood', 'unit': UNIT,
        'about': "Anny's local changes of the head and face (tools/face_targets.py), on moood's mesh as changes of moood's woman at +1 and −1; i<key>: the vertices moved, p<key>/n<key>: their moves (int16 × unit metres)",
        'changes': changes}, arrays)
    print(len(changes), 'changes')
