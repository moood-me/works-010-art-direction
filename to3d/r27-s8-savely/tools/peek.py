"""Quick clay looks while building: python3 peek.py head|all OUT.png"""
import sys, json, numpy as np
import base, drawing, look
from common import CACHE, HH, pack, BID
what, out = sys.argv[1], sys.argv[2]
CL = (0.84, 0.8, 0.74)
if what == 'head':
    d = np.load(f'{CACHE}/head_raw.npz'); T = base.tris(d['Q'])
    box = (-0.62, 0.62, -0.62, 0.62)
    ns = drawing.nose_slices()
    lines = [(drawing.eye_opening(s)[0], (190, 60, 40)) for s in (-1, 1)] + [(drawing.mouth_line(), (190, 60, 40))]
    lines += [(np.c_[sg * ns[:, 2], ns[:, 0], ns[:, 1]], (40, 60, 190)) for sg in (-1, 1)]
    look.sheet([look.raster([(d['V'], T, CL)], y, box, 420, lines=lines) for y in (0, 35, 90)], out)
else:
    M = json.load(open(f'{CACHE}/model.json'))
    _, a = pack.read(f'{CACHE}/engine/data/bodies/{BID}.json'); _, t = pack.read(f'{CACHE}/engine/data/topology/{BID}.json')
    P_ = a['positions'].astype(float); TT = t['triangles'].astype(int)
    import colorsys
    mm = []
    cols = json.load(open(f'{CACHE}/peekcols.json')) if False else {}
    for i, p in enumerate(M['pieces']):
        s, n = p['start'], p['count']; m = (TT[:, 0] >= s) & (TT[:, 0] < s + n)
        c = M.get('clay', {}).get(p['mat'], CL)
        mm.append((P_[s:s + n], TT[m] - s, c))
    if what == 'face':
        O = np.array(M['O']); box = (O[0] - 0.62 * HH, O[0] + 0.62 * HH, O[1] - 0.7 * HH, O[1] + 0.62 * HH)
        look.sheet([look.raster(mm, y, box, 460) for y in (0, 35, 90)], out)
    else:
        top = P_[:, 1].max() + 0.03; box = (-top * 0.42, top * 0.42, -0.02, top)
        look.sheet([look.raster(mm, y, box, 380) for y in (0, 35, 90, 180)], out)
