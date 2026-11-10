"""Data for the browser viewer (tools/web/): the engine body and topology packs as they are, the live face's
measures, and the look — each vertex's flat colour (index into a palette). Copied from CACHE into tools/web/data/.
usage: python3 web_data.py CACHE"""
import sys, os, json, shutil
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import who
C = sys.argv[1]
OUT = os.path.join(HERE, 'web/data')
for sub in ('bodies', 'topology'):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    for ext in ('json', 'bin'):
        shutil.copy(os.path.join(C, f'engine/data/{sub}/{who.ID}.{ext}'), os.path.join(OUT, f'{sub}/{who.ID}.{ext}'))
shutil.copy(os.path.join(C, 'engine/face.json'), os.path.join(OUT, 'face.json'))
meta = json.load(open(os.path.join(C, 'scene.json')))
sc = np.load(os.path.join(C, 'scene.npz'))
offs = json.load(open(os.path.join(C, 'engine/offsets.json')))
N = max(b for a, b in offs.values())
palette, idx = [], np.zeros(N, np.uint8)
line = np.ones(N, np.uint8)
ids = np.zeros(N, np.uint16)          # what the outline separates: each piece, and the mouth's inside


def pal(c):
    if c not in palette:
        palette.append(c)
    return palette.index(c)


for o in meta['objects']:
    if o['name'] not in offs:
        continue
    a, b = offs[o['name']]
    idx[a:b] = pal(o['colour'])
    ids[a:b] = meta['objects'].index(o) + 1
    if o.get('colours'):                       # per-face colours (the mouth's dark inside): its vertices take them
        F = sc['obj_' + o['name'] + '_f']
        fc = sc['obj_' + o['name'] + '_fc']
        for k, c in enumerate(o['colours']):
            if k == 0:
                continue
            vs = np.unique(F[fc == k])
            vs = vs[vs >= 0]
            idx[a + vs] = pal(c)
            ids[a + vs] = 1000 + k
    if o.get('line') is False:
        line[a:b] = 0
json.dump(dict(panel=who.PANEL, palette=palette, colour=idx.tolist(), id=ids.tolist(), line=line.tolist()), open(os.path.join(OUT, 'look.json'), 'w'),
          separators=(',', ':'))
print('palette', palette, 'N', N)
