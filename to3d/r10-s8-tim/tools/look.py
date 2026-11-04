"""Quick clay pictures for looking at a mesh while building (numpy z-buffer, orthographic): any number of meshes,
each with a colour, plus 3D polylines drawn over (e.g. the drawing's outlines)."""
import numpy as np
from PIL import Image, ImageDraw
from common import vertex_normals


def raster(meshes, yaw=0.0, box=(-0.6, 0.6, -0.6, 0.6), size=500, light=(-0.5, 0.6, 0.7), lines=(), pitch=0.0):
    c, s = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))
    cp, sp = np.cos(np.radians(pitch)), np.sin(np.radians(pitch))
    x0, x1, y0, y1 = box
    W = size; H = int(round(size * (y1 - y0) / (x1 - x0)))

    def view(V):
        X = V[:, 0] * c + V[:, 2] * s; Z = -V[:, 0] * s + V[:, 2] * c; Y = V[:, 1]
        Y, Z = Y * cp - Z * sp, Y * sp + Z * cp
        return np.c_[X, Y, Z]
    img = np.full((H, W, 3), 0.97); zb = np.full((H, W), -1e9)
    L = np.array(light, float); L /= np.linalg.norm(L)
    for V, T, col in meshes:
        Q = view(V)
        N = vertex_normals(Q, T)
        sh = np.clip(N @ L, 0, 1) * 0.7 + 0.3
        col = np.broadcast_to(np.asarray(col, float), (len(V), 3))
        vc = col * sh[:, None]
        px = (Q[:, 0] - x0) / (x1 - x0) * W; py = (y1 - Q[:, 1]) / (y1 - y0) * H
        for t in T:
            xs, ys = px[t], py[t]
            mnx, mxx = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
            mny, mxy = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
            if mnx > mxx or mny > mxy: continue
            den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
            if abs(den) < 1e-12: continue
            gx, gy = np.meshgrid(np.arange(mnx, mxx + 1) + 0.5, np.arange(mny, mxy + 1) + 0.5)
            l0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / den
            l1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / den
            l2 = 1 - l0 - l1
            ins = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
            if not ins.any(): continue
            z = l0 * Q[t[0], 2] + l1 * Q[t[1], 2] + l2 * Q[t[2], 2]
            sub = zb[mny:mxy + 1, mnx:mxx + 1]; upd = ins & (z > sub); sub[upd] = z[upd]
            im = img[mny:mxy + 1, mnx:mxx + 1]
            for k in range(3): im[..., k][upd] = (l0 * vc[t[0], k] + l1 * vc[t[1], k] + l2 * vc[t[2], k])[upd]
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for P, colr in lines:
        Q = view(np.asarray(P, float))
        px = (Q[:, 0] - x0) / (x1 - x0) * W; py = (y1 - Q[:, 1]) / (y1 - y0) * H
        d.line(list(zip(px, py)), fill=colr, width=1)
    return im


def sheet(ims, out):
    W = sum(i.width for i in ims); H = max(i.height for i in ims)
    S = Image.new('RGB', (W, H), 'white'); x = 0
    for i in ims: S.paste(i, (x, 0)); x += i.width
    S.save(out)
