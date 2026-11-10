"""A quick software look at the built pack (flat material colours), front / three-quarter / side / back."""
import sys, numpy as np
from common import pack, CACHE
import char
from look import views
h, a = pack.read(f'{CACHE}/{char.NAME}.json')
col = np.array([[int(h['paint'][m][i:i + 2], 16) / 255 for i in (1, 3, 5)] for m in h['mats']])[a['mat']]
box = None
if len(sys.argv) > 2: box = tuple(float(x) for x in sys.argv[2].split(','))
views([(a['positions'].astype(float), a['triangles'].astype(int), None)], yaws=(0, -0.62, -1.5708, 3.1416), size=int(sys.argv[3]) if len(sys.argv) > 3 else 360, box=box, path=sys.argv[1]) if False else None
from mesh import raster
from PIL import Image
ims = [raster(a['positions'].astype(float), a['triangles'].astype(int), yaw=y, size=int(sys.argv[3]) if len(sys.argv) > 3 else 360, box=box, col=col)[0] for y in (0, -0.62, -1.5708, 3.1416)]
Image.fromarray(np.concatenate(ims, 1)).save(sys.argv[1])
