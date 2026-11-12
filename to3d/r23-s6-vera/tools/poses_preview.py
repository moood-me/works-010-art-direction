"""A quick look at the moods without a browser: the style's own silhouette code draws each mood of character.py
(black shapes, PIL). python3 poses_preview.py OUT.png [k]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'styles', 's6-symbolic', 'tools'))
sys.path.insert(0, HERE)
import cast  # noqa: E402
import character as C  # noqa: E402
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection  # noqa: E402

k = float(sys.argv[2]) if len(sys.argv) > 2 else 2.4
order = [m for m in C.MOODS if C.MOODS[m].get('yaw') is not None]
W, H = int(150 * k), int(215 * k)
img = Image.new('RGB', (W * len(order), H), (233, 228, 220))
dr = ImageDraw.Draw(img)
for i, m in enumerate(order):
    M = C.MOODS[m]
    J, f, acc = cast.CAST[C.ID](pose=M['pose'], yaw=M['yaw'], **M.get('opts', {}))
    g = f.shape(M['yaw'])
    polys = [g] if isinstance(g, Polygon) else [p for p in g.geoms if isinstance(p, Polygon)]
    for p in polys:
        c = np.asarray(p.exterior.coords) * k + [W * i + W / 2, H - 18 * k]
        dr.polygon([tuple(q) for q in c], fill=(16, 19, 27))
        for r in p.interiors:
            c = np.asarray(r.coords) * k + [W * i + W / 2, H - 18 * k]
            dr.polygon([tuple(q) for q in c], fill=(233, 228, 220))
    dr.text((W * i + 8, 6), m, fill=(90, 80, 80))
img.save(sys.argv[1])
