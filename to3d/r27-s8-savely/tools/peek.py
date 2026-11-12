"""Quick clay looks while building: python3 peek.py head|all OUT.png"""
import sys, json, numpy as np
import base, drawing, look
from common import CACHE, HH, pack, BID
what, out = sys.argv[1], sys.argv[2]
CL = (0.84, 0.8, 0.74)
COL = dict(skin=(0.86, 0.67, 0.56), eye=(0.95, 0.95, 0.97), hair=(0.9, 0.88, 0.84), whisker=(0.93, 0.91, 0.87), lip=(0.7, 0.36, 0.35), mouth=(0.25, 0.1, 0.1),
           lash=(0.2, 0.14, 0.12), gold=(0.75, 0.6, 0.3), lens=(0.8, 0.9, 1.0), vest=(0.43, 0.3, 0.2), shirt=(0.89, 0.84, 0.74), collar=(0.94, 0.9, 0.8),
           tie=(0.48, 0.16, 0.16), button=(0.23, 0.14, 0.1), chain=(0.85, 0.66, 0.25), trousers=(0.29, 0.29, 0.32), shoe=(0.23, 0.14, 0.1), sole=(0.12, 0.1, 0.1), dark=(0.1, 0.08, 0.08))
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
        c = COL.get(p['mat'], CL)
        mm.append((P_[s:s + n], TT[m] - s, c))
    if what == 'face':
        O = np.array(M['O']); box = (O[0] - 0.62 * HH, O[0] + 0.62 * HH, O[1] - 0.7 * HH, O[1] + 0.62 * HH)
        look.sheet([look.raster(mm, y, box, 460) for y in (0, 35, 90)], out)
    else:
        top = P_[:, 1].max() + 0.03; box = (-top * 0.42, top * 0.42, -0.02, top)
        look.sheet([look.raster(mm, y, box, 380) for y in (0, 35, 90, 180)], out)
