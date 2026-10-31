import sys; sys.path.insert(0, 'py'); from anny import *
from collections import Counter
bs = base(); at, J = person('girl', bs); T = bs['tris']
hw = wOf(bs, ['Head','HeadEnd','Jaw','LeftEye','RightEye'])
E = Counter()
for a, b, c in T:
    for u, v in ((a, b), (b, c), (c, a)): E[(min(u, v), max(u, v))] += 1
bd = [e for e, n in E.items() if n == 1 and hw[e[0]] > .3]
print('boundary edges in head', len(bd), 'nonmanifold', sum(1 for e,n in E.items() if n>2))
vs = sorted(set(v for e in bd for v in e)); P = at[vs]
print(np.round(P[:40]*1000,1))
f = bs['face']; print('face idx range', f.min(), f.max(), 'are verts head?', (hw[f] > .3).mean())
eL = J[JI['LeftEye']]
# point cloud near left eye: which head verts exist inside eye socket
m = (np.linalg.norm(at - eL, axis=1) < 0.014)
print('verts within 14mm of eye joint', m.sum(), np.round((at[m]-eL)[:10]*1000,1))
