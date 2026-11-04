"""Quick looks at point sets: dots.py out.png a.npy:axes … — draws vertices projected (x,y) for checking shapes."""
import numpy as np
from PIL import Image, ImageDraw


def dots(views, out, size=500):
    """views: list of (points N×2, colour or None); drawn side by side, each fitted to its box, same scale."""
    allp = np.concatenate([v[0] for v in views])
    span = (allp.max(0) - allp.min(0)).max()
    im = Image.new('RGB', (size * len(views), size), 'white'); d = ImageDraw.Draw(im)
    for k, (p, c) in enumerate(views):
        c0 = (p.max(0) + p.min(0)) / 2
        q = (p - c0) / span * size * 0.9
        for x, y in q: d.point((k * size + size / 2 + x, size / 2 - y), fill=c or (0, 0, 0))
    im.save(out)
