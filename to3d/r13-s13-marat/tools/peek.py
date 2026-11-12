"""A quick look at the form: front and side, triangles painted far to near by piece (no shading)."""
import sys, numpy as np, pack
from PIL import Image, ImageDraw
h, a = pack.load('/home/user/cache/to3d-r13-s13-marat/form/marat.json')
P = a['positions'].reshape(-1, 3); T = a['triangles'].reshape(-1, 3)
col = {'arms': (241, 215, 182), 'legs': (200, 196, 190), 'head': (241, 215, 182), 'beard': (40, 30, 30), 'hair': (60, 50, 50), 'jacket': (248, 242, 226),
       'collar': (235, 228, 210), 'sleeveLeft': (240, 234, 220), 'sleeveRight': (240, 234, 220), 'apron': (200, 104, 58), 'towel': (220, 180, 150),
       'strapLeft': (180, 90, 50), 'strapRight': (180, 90, 50), 'shoeLeft': (50, 44, 46), 'shoeRight': (50, 44, 46)}
tc = np.zeros((len(T), 3), int)
for k, (s, e) in h['trianglePieces'].items(): tc[s:e] = col[k]
S = 520; out = Image.new('RGB', (S * 3 // 2 * 2, int(S * 2.05)), (150, 165, 172))
for vi, (ax, sg) in enumerate(((0, 1), (2, 1))):
    im = ImageDraw.Draw(out)
    depth = P[:, 2] if ax == 0 else P[:, 0]
    n = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    o = np.argsort(depth[T].mean(1))
    for t in o:
        pts = [(vi * S * 1.5 + S * 0.75 + P[i, ax] * S * (1 if ax == 0 else -1), S * 2.0 - P[i, 1] * S) for i in T[t]]
        sh = 0.75 + 0.25 * abs(n[t, 2 if ax == 0 else 0])
        im.polygon(pts, fill=tuple(int(c * sh) for c in tc[t]))
out.save(sys.argv[1] if len(sys.argv) > 1 else '/home/user/cache/to3d-r13-s13-marat/peek.png')
