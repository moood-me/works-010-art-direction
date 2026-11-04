"""Put Савелий Петрович's 3D pieces into one scene for render.py: scene.npz + scene.json.
Pieces (drawing units, the figure's frame): the fitted base head, its eyes, the drawing's hair horseshoe and moustache,
the face marks; with --body, the fitted Anny body and the clothes (body.py → body.npz).
usage: python3 assemble.py CACHE [--body]
"""
import sys, os, json
import numpy as np

C = sys.argv[1]
WITH_BODY = '--body' in sys.argv
K = 1.60 / 1114            # metres per drawing unit: the drawing's figure (crown to floor 1114 units) is 1.60 m
FLOOR = 1030.0

d = np.load(os.path.join(C, 'drawing.npz'))
info = json.load(open(os.path.join(C, 'drawing.json')))
hf = np.load(os.path.join(C, 'head_fit.npz'))
col = info['colours']
SCLERA = os.environ.get('SCLERA', col['skin'])

objs, arrays = [], {}


def add(name, V, F, colour, **kw):
    arrays['obj_' + name + '_v'] = np.asarray(V, float)
    F = np.asarray(F)
    arrays['obj_' + name + '_f'] = F
    o = dict(name=name, colour=colour)
    o.update({k: v for k, v in kw.items() if k != 'fc'})
    if 'fc' in kw:
        arrays['obj_' + name + '_fc'] = np.asarray(kw['fc'])
    objs.append(o)


def grid(nu, nv):
    q = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a = i * nv + j
            q.append((a, a + nv, a + nv + 1, a + 1))
    return np.array(q)


if WITH_BODY:
    b = np.load(os.path.join(C, 'body.npz'))
    for name in b['names']:
        meta = json.loads(str(b[name + '_meta']))
        add(name, b[name + '_v'], b[name + '_f'], meta['colour'], **{k: v for k, v in meta.items() if k != 'colour'})
else:
    keep = ~hf['low']
    add('head', hf['v'], hf['f'], col['skin'], subsurf=1)
for s in 'LR':
    add('sclera' + s, hf['sclera' + s + '_v'], hf['sclera' + s + '_f'], SCLERA)
    add('iris' + s, hf['iris' + s + '_v'], hf['iris' + s + '_f'], '#1b1714', line=False)
add('hair', d['hair_v'], d['hair_q'], col['hair'])
for k in (0, 1):
    P = d[f'stache{k}']
    n, m = d[f'stache{k}_nm']
    add(f'stache{k}', P[:n * m], grid(n, m), col['stache'], solidify=1.5)

json.dump(dict(objects=objs, marks=info['marks'], k=K, floor=FLOOR, skip=['pupil']), open(os.path.join(C, 'scene.json'), 'w'))
np.savez(os.path.join(C, 'scene.npz'), **arrays)
print(len(objs), 'objects')
