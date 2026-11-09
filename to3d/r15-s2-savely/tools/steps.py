"""The step pictures (what each base gave), by the plain software rasteriser (mesh.raster) → ../pics/s*.webp
  python3 steps.py"""
import os
import numpy as np
from PIL import Image
import mesh as M, base_head as B, head as Hd, blobs as Bl, pack
from body import Body

HERE = os.path.dirname(os.path.abspath(__file__)); PICS = os.path.join(HERE, '..', 'pics')
CLAY = (0.86, 0.80, 0.74)


def shot(V, T, yaws, size, box, col=None):
    return np.hstack([M.raster(V, T, y, size, box, col=col, light=(-0.55, 0.5, 0.65))[0] for y in yaws])


def save(a, name): Image.fromarray(a).save(os.path.join(PICS, name + '.webp'), quality=88); print(name, a.shape)


v, P = B.load(Hd.HBM); T = M.triangulate(P)
box = (-0.2, 0.2, 0.5, 0.9)
save(shot(v, T, (0, 0.7, np.pi / 2), 360, box), 's1-base')
v2, P2 = B.base(Hd.HBM); T2 = M.triangulate(P2)
save(shot(v2, T2, (0, 0.7, np.pi / 2), 360, box), 's2-closed')
V, Pf, ear = Hd.fitted(); Tf = M.triangulate(Pf)
hb = (-0.27, 0.27, -0.1, 0.5)
save(shot(V, Tf, (0, 0.62, np.pi / 2), 360, hb), 's3-fitted')
cols = dict(nose=(0.85, 0.52, 0.47), moustache=(0.92, 0.9, 0.86), browL=(0.92, 0.9, 0.86), browR=(0.92, 0.9, 0.86), earL=(0.89, 0.65, 0.54), earR=(0.89, 0.65, 0.54),
            tuftL=(0.92, 0.9, 0.86), tuftR=(0.92, 0.9, 0.86), glasses=(0.4, 0.3, 0.2), glint=(1, 1, 1), lens=None,
            loupe=(0.2, 0.2, 0.2), brass=(0.8, 0.6, 0.3), glass=(0.5, 0.7, 0.75), band=(0.2, 0.15, 0.15))
parts = [(V, Tf, (0.89, 0.65, 0.54))]
for k, (pv, pt) in {**Hd.forms(V, Tf), **Hd.things(V, Tf)}.items():
    if cols[k]: parts.append((pv, pt, cols[k]))
Vs, Ts = Bl.join([(a, b) for a, b, _ in parts]); C = np.concatenate([np.tile(c, (len(a), 1)) for a, _, c in parts])
save(shot(Vs, Ts, (0, 0.62, np.pi / 2), 360, hb, C), 's4-forms')
b = Body('moood-oldman')
bb = (-0.62, 0.62, -0.05, 1.8)
a = shot(b.P, b.T, (0, np.pi / 2), 300, bb)
h, arr = pack.load(os.path.join(HERE, '..', 'data', 'savely.json'))
pos = arr['positions']; tri = arr['triangles'].reshape(-1, 3).astype(np.int64)
c = shot(pos, tri, (0, np.pi / 2), 300, bb, arr['col'] / 255.0)
save(np.hstack([a, c]), 's5-body')
# the painted layers on the skin colour
tiles = []
for ex in ('calm', 'kind', 'surprise', 'sad', 'anger'):
    bg = Image.new('RGBA', (880, 1200), (226, 166, 138, 255))
    mouth = {'kind': 'smile', 'surprise': 'o'}.get(ex, 'none')
    for n in (f'skin-{mouth}', f'eyes-{ex}-oc'): bg.alpha_composite(Image.open(os.path.join(HERE, '..', 'data', 'faces', n + '.png')))
    tiles.append(np.asarray(bg.convert('RGB').resize((330, 450), Image.LANCZOS)))
save(np.hstack(tiles), 's6-face-layer')
