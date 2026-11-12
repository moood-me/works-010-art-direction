"""Pictures for judging: the drawing's views beside the 3D render and over it.
The drawing's own SVG pieces are drawn (as outlines) over a render made with an orthographic camera in the drawing's
scale, so a render pixel and a drawing pixel are the same place."""
import sys, os, json, subprocess
import numpy as np
from PIL import Image, ImageDraw
import drawing as D

HERE = os.path.dirname(os.path.abspath(__file__))


def cam_for(yd0, yd1, xd0, xd1, W, H):
    """An orthographic camera showing drawing box [xd0,xd1]×[yd0,yd1] in W×H pixels."""
    h = (yd1 - yd0) * D.K
    cy = (D.FLOOR - (yd0 + yd1) / 2) * D.K
    cx = (xd0 + xd1) / 2 * D.K
    return dict(mode='ortho', h=h, cy=cy, cx=cx)


def px(xd, yd, box, W, H):
    yd0, yd1, xd0, xd1 = box
    s = H / (yd1 - yd0)
    return (W / 2 + (xd - (xd0 + xd1) / 2) * s, (yd - yd0) * s)


def outline(img, shapes, box, col=(40, 120, 200), w=2):
    d = ImageDraw.Draw(img); W, H = img.size
    for sh in shapes:
        for P in D.sample(sh):
            pts = [px(x, y, box, W, H) for x, y in P]
            d.line(pts, fill=col, width=w)
    return img
