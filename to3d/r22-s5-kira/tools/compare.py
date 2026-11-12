"""Side by side and overlaid: the drawing and the 3D render made in the same view (same viewBox, same pixels).
python3 compare.py drawing.png render.png out_side.jpg out_overlay.jpg [vertical]"""
import sys
from PIL import Image, ImageChops


def side(a, b, vertical=False, gap=12, bg=(236, 229, 217)):
    if vertical:
        out = Image.new('RGB', (max(a.width, b.width), a.height + b.height + gap), bg)
        out.paste(a, (0, 0)); out.paste(b, (0, a.height + gap))
    else:
        out = Image.new('RGB', (a.width + b.width + gap, max(a.height, b.height)), bg)
        out.paste(a, (0, 0)); out.paste(b, (a.width + gap, 0))
    return out


def overlay(a, b):
    """The drawing's dark lines over a pale copy of the render: where the two outlines part, the shapes differ."""
    import numpy as np
    pale = Image.blend(b, Image.new('RGB', b.size, (255, 255, 255)), 0.4)
    A = np.asarray(a).astype(float)
    gx = np.abs(np.diff(A, axis=1, append=A[:, -1:])).sum(2)
    gy = np.abs(np.diff(A, axis=0, append=A[-1:])).sum(2)
    g = Image.fromarray(((np.maximum(gx, gy) > 60) * 255).astype('uint8'))
    pale.paste(Image.new('RGB', a.size, (215, 30, 60)), (0, 0), g)
    return pale


if __name__ == '__main__':
    a = Image.open(sys.argv[1]).convert('RGB')
    b = Image.open(sys.argv[2]).convert('RGB').resize(a.size)
    vertical = len(sys.argv) > 5
    side(a, b, vertical).save(sys.argv[3], quality=88)
    overlay(a, b).save(sys.argv[4], quality=88)
