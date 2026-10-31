# Two studio motions as one: the second made to go on from the first (make_motion with `after`), its first frames the
# first's last ones — the second moved over the floor to where the first left off, joined without them twice.
# python3 chain.py first.txt second.txt overlap out.txt [keep]   (the studio's body data: {n, fps, names, q, p}; keep:
# only so many of the first's frames, when it ends lying still as the second begins)
import json, base64, sys, numpy as np
a, b, k, out = json.load(open(sys.argv[1])), json.load(open(sys.argv[2])), int(sys.argv[3]), sys.argv[4]
def arr(d, key, w): return np.frombuffer(base64.b64decode(d[key]), dtype='<i2').reshape(d['n'], 77, w).copy()
qa, pa, qb, pb = arr(a, 'q', 4), arr(a, 'p', 3), arr(b, 'q', 4), arr(b, 'p', 3)
if len(sys.argv) > 5: qa, pa = qa[:int(sys.argv[5])], pa[:int(sys.argv[5])]
d = pa[-k, :, :].astype(int) - pb[0, :, :].astype(int); d[:, 1] = 0
pb = (pb.astype(int) + d[0]).astype('<i2')
q, p = np.concatenate([qa, qb[k:]]), np.concatenate([pa, pb[k:]])
json.dump({'n': len(q), 'fps': a['fps'], 'names': a['names'], 'q': base64.b64encode(q.astype('<i2').tobytes()).decode(), 'p': base64.b64encode(p.astype('<i2').tobytes()).decode()}, open(out, 'w'))
