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
hb = (-0.27, 0.27, -0.1, 0.44)
save(shot(V, Tf, (0, 0.62, np.pi / 2), 360, hb), 's3-fitted')
sk = (0.86, 0.61, 0.46)
cols = dict(earL=sk, earR=sk, nose=(0.86, 0.55, 0.42), beard=(0.22, 0.19, 0.22), moustache=(0.17, 0.14, 0.17), hair=(0.22, 0.19, 0.22))
parts = [(V, Tf, sk)] + [(pv, pt, cols[k]) for k, (pv, pt) in Hd.forms(V, Tf).items()]
Vs, Ts = Bl.join([(a, b) for a, b, _ in parts]); C = np.concatenate([np.tile(c, (len(a), 1)) for a, _, c in parts])
save(shot(Vs, Ts, (0, 0.62, np.pi / 2), 360, hb, C), 's4-forms')
b = Body('moood-man')
bb = (-0.75, 0.75, -0.05, 2.0)
a = shot(b.P, b.T, (0, np.pi / 2), 300, bb)
h, arr = pack.load(os.path.join(HERE, '..', 'data', 'marat.json'))
pos = arr['positions']; tri = arr['triangles'].reshape(-1, 3).astype(np.int64)
c = shot(pos, tri, (0, np.pi / 2), 300, bb, arr['col'] / 255.0)
save(np.hstack([a, c]), 's5-body')
# the painted layers on the skin colour
tiles = []
for ex, mouth in (('calm', 'smile'), ('joy', 'laugh'), ('surprise', 'o'), ('sad', 'sad'), ('anger', 'angry')):
    bg = Image.new('RGBA', (880, 1040), (220, 156, 118, 255))
    for n in (f'skin-{mouth}', f'eyes-{ex}-oc'): bg.alpha_composite(Image.open(os.path.join(HERE, '..', 'data', 'faces', n + '.png')))
    tiles.append(np.asarray(bg.convert('RGB').resize((330, 390), Image.LANCZOS)))
save(np.hstack(tiles), 's6-face-layer')
