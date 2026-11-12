"""Quick clay looks while building: python3 peek.py head|all OUT.png"""
import sys, json, numpy as np
import base, drawing, look
from common import CACHE, HH, pack, BID
what, out = sys.argv[1], sys.argv[2]
CL = (0.84, 0.8, 0.74)
COL = dict(skin=(0.86, 0.66, 0.52), eye=(0.95, 0.95, 0.97), curl=(0.2, 0.16, 0.15), hairmass=(0.14, 0.11, 0.1), brow=(0.14, 0.1, 0.1), lip=(0.7, 0.36, 0.32), mouth=(0.25, 0.1, 0.1),
           tongue=(0.66, 0.27, 0.3), lash=(0.12, 0.08, 0.07), jacket=(0.93, 0.89, 0.82), apron=(0.77, 0.35, 0.18), aprontie=(0.66, 0.3, 0.15), towel=(0.97, 0.95, 0.9),
           trousers=(0.34, 0.31, 0.3), shoe=(0.23, 0.17, 0.13), sole=(0.12, 0.1, 0.1))
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
