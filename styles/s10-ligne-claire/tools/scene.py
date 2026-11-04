"""Put characters (a head alone, or a figure) into one picture and render them together, so where one person
overlaps another the contour is drawn just as it is inside one figure.

A character is anything with parts(res) -> [Part] and get_marks(expr, view) -> [Mark] in its own coordinates.
A placement: dict(x, y, z, yaw, scale, expr).  The view is the camera for the whole picture.
"""
import math
import numpy as np
import r3
from head import draw_marks


class Yaw:
    def __init__(self, deg):
        self.yaw_deg = deg


def _place(P, pl):
    s = pl.get('scale', 1.0)
    a = math.radians(pl.get('yaw', 0.0))
    X, Y, Z = P[..., 0] * s, P[..., 1] * s, P[..., 2] * s
    X2 = X * math.cos(a) + Z * math.sin(a)
    Z2 = -X * math.sin(a) + Z * math.cos(a)
    return np.stack([X2 + pl.get('x', 0), Y + pl.get('y', 0), Z2 + pl.get('z', 0)], -1)


def render(chars, view, box, colours, lw, clip_prefix='c', thr=6.0):
    """chars: list of (character, placement). colours: material -> colour (one table for the picture;
    materials of different people should have different names when their colours differ)."""
    parts, marks = [], []
    res = view.s * view.ss
    for k, (ch, pl) in enumerate(chars):
        sc = pl.get('scale', 1.0)
        for p in ch.parts(res * sc):
            P = _place(np.stack([p.X, p.Y, p.Z], -1), pl)
            q = r3.Part(f'{k}:{p.name}', p.material, P[:, 0], P[:, 1], P[:, 2], line=p.line)
            parts.append(q)
        for m in ch.get_marks(pl.get('expr') or {}, Yaw(view.yaw_deg + pl.get('yaw', 0.0))):
            m.pts = _place(m.pts, pl)
            m.tol = m.tol * sc
            marks.append(m)
    R = r3.Render(parts, view, box, thr=thr)
    out = R.fills(colours)
    out += R.lines(lw)
    for mat in sorted(set(m.on for m in marks), key=str):
        ms = [m for m in marks if m.on == mat]
        if mat not in R.mats:
            out += draw_marks(ms, R, lw)
            continue
        cid = f'{clip_prefix}-{mat}'
        out.append(f'<defs>{R.clip_path([mat], cid)}</defs><g clip-path="url(#{cid})">'
                   + ''.join(draw_marks(ms, R, lw)) + '</g>')
    return out, R
