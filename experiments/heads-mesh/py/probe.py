import sys; sys.path.insert(0, 'py'); from anny import *
bs = base(); at, J = person(sys.argv[1], bs); N = bs['N']
used = np.zeros(N, bool); used[bs['tris'].ravel()] = True
eL, eR = J[JI['LeftEye']], J[JI['RightEye']]; print('eyes', eL, eR, 'head', J[JI['Head']], 'jaw', J[JI['Jaw']], 'headend', J[JI['HeadEnd']])
print('N', N, 'T', len(bs['tris']), 'face', len(bs['face']), bs['face'][:20])
hw = wOf(bs, ['Head','HeadEnd','Jaw','LeftEye','RightEye']); jw = wOf(bs, ['Jaw'])
print('head verts', (used & (hw > .5)).sum(), 'jaw verts', (used & (jw > .3)).sum())
m = used & (np.abs(at[:, 0]) < 0.0015) & (hw > .5) & (at[:, 2] > eL[2] - 0.03)
idx = np.where(m)[0]; idx = idx[np.argsort(-at[idx, 1])]
for i in idx: print(i, np.round((at[i] - [0, eL[1], 0]) * 1000, 1), 'jaw%.2f' % jw[i])
