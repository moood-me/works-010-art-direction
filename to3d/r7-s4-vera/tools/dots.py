"""Tiny point plotter (PIL) for looking at meshes and point clouds side by side: dots.py is imported."""
import numpy as np
from PIL import Image, ImageDraw


def plot(panels, path, size=600, grid=None):
    """panels: list of [(pts2d (N,2), colour, radius)] — each panel framed to its points (y up)."""
    W = size * len(panels)
    im = Image.new('RGB', (W, size), 'white')
    d = ImageDraw.Draw(im)
    for i, layers in enumerate(panels):
        allp = np.vstack([l[0] for l in layers])
        lo, hi = allp.min(0), allp.max(0)
        sc = 0.9 * size / max(hi - lo)
        c = (lo + hi) / 2
        def tr(p):
            return np.stack([i * size + size / 2 + (p[:, 0] - c[0]) * sc, size / 2 - (p[:, 1] - c[1]) * sc], 1)
        if grid:
            for g in np.arange(np.floor(lo.min() / grid) * grid, hi.max() + grid, grid):
                a = tr(np.array([[g, lo[1]], [g, hi[1]]])); d.line([tuple(a[0]), tuple(a[1])], fill='#eee')
                a = tr(np.array([[lo[0], g], [hi[0], g]])); d.line([tuple(a[0]), tuple(a[1])], fill='#eee')
        for pts, col, r in layers:
            for x, y in tr(np.asarray(pts)):
                d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    im.save(path)
