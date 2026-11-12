"""Quick looks while fitting: software-rastered meshes (orthographic, Lambert) side by side, with the drawing's
head mesh overlaid as a translucent tint. python-only, for checking shapes, not for the page."""
import numpy as np
from PIL import Image
from mesh import raster


def views(meshes, yaws=(0, -0.62, -1.5708), size=420, box=None, overlay=None, path=None):
    """meshes: list of (V, T, rgb); V in units with y UP. overlay: (V, T) drawn as a red tint over the result."""
    V = np.concatenate([m[0] for m in meshes]); T = np.concatenate([m[1] + sum(len(q[0]) for q in meshes[:i]) for i, m in enumerate(meshes)])
    col = np.concatenate([np.tile(m[2], (len(m[0]), 1)) for m in meshes])
    if box is None:
        r = np.abs(V[:, [0, 2]]).max() * 1.05; y0, y1 = V[:, 1].min(), V[:, 1].max(); m = (y1 - y0) * 0.04
        h = max(y1 - y0 + 2 * m, 2 * r); cy = (y0 + y1) / 2; box = (-h / 2, h / 2, cy - h / 2, cy + h / 2)
    ims = []
    for yaw in yaws:
        im, _ = raster(V, T, yaw=yaw, size=size, box=box, col=col)
        im = im.astype(float)
        if overlay is not None:
            o, _ = raster(overlay[0], overlay[1], yaw=yaw, size=size, box=box)
            mask = (o < 250).any(2)
            # outline of the overlay: edge of its mask
            e = mask ^ np.roll(mask, 1, 0) | mask ^ np.roll(mask, 1, 1)
            im[mask] = im[mask] * 0.8 + np.array([255, 120, 100]) * 0.2
            im[e] = [220, 30, 20]
        ims.append(im.astype(np.uint8))
    out = Image.fromarray(np.concatenate(ims, 1))
    if path: out.save(path)
    return out
