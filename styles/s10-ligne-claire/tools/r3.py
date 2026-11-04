"""A small 'ligne claire' renderer: 3D surfaces -> flat colour regions + one even contour line.

Parts are dense point samples of surfaces (X, Y, Z arrays; y points down, z toward the viewer at yaw 0).
A view rotates them (pitch about x, then yaw about y), projects orthographically, and splats them into a z-buffer
that keeps, per pixel, the nearest part. From the buffer:
  - fills: one region per material (union of its parts), drawn flat;
  - lines: for every part, the parts of its outline where it is in front of something else — the background,
    another material, or the same material farther back by more than a threshold (the nose over the cheek,
    the jaw over the neck, an ear). That is exactly where a ligne-claire artist draws a contour.
Marks on the surface (eyes, brows, mouth, folds) are 3D polylines mapped through the same view and kept where
the z-buffer says they are visible.
"""
import math
import numpy as np
from scipy import ndimage
from skimage import measure
import lc


class View:
    def __init__(self, yaw=0.0, pitch=0.0, roll=0.0, s=1.0, cx=0.0, cy=0.0, ss=2):
        self.yaw_deg = yaw
        self.yaw, self.pitch, self.roll = math.radians(yaw), math.radians(pitch), math.radians(roll)
        self.s, self.cx, self.cy, self.ss = s, cx, cy, ss   # ss: raster pixels per output pixel

    def rot(self, X, Y, Z):
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        Y1 = Y * cp - Z * sp
        Z1 = Y * sp + Z * cp
        cy_, sy_ = math.cos(self.yaw), math.sin(self.yaw)
        X2 = X * cy_ + Z1 * sy_
        Z2 = -X * sy_ + Z1 * cy_
        cr, sr = math.cos(self.roll), math.sin(self.roll)
        X3 = X2 * cr - Y1 * sr
        Y3 = X2 * sr + Y1 * cr
        return X3, Y3, Z2

    def to2d(self, X, Y, Z):
        """Model -> output picture coordinates and depth (bigger = nearer)."""
        X3, Y3, Z3 = self.rot(np.asarray(X, float), np.asarray(Y, float), np.asarray(Z, float))
        return X3 * self.s + self.cx, Y3 * self.s + self.cy, Z3


class Part:
    def __init__(self, name, material, X, Y, Z, line=True):
        self.name, self.material = name, material
        self.X, self.Y, self.Z = (np.asarray(a, float).ravel() for a in (X, Y, Z))
        self.line = line


def grid(fn, nu, nv, u0=0, u1=1, v0=0, v1=1):
    u, v = np.meshgrid(np.linspace(u0, u1, nu), np.linspace(v0, v1, nv), indexing='ij')
    return fn(u, v)


class Render:
    """Rasterise parts for one view; then hand out fills, lines and a visibility test for marks."""

    def __init__(self, parts, view, box, thr=6.0):
        self.parts, self.v = parts, view
        x0, y0, x1, y1 = box                              # output-picture box to rasterise
        ss = view.ss
        self.x0, self.y0, self.ss = x0, y0, ss
        W, H = int((x1 - x0) * ss) + 2, int((y1 - y0) * ss) + 2
        depth = np.full((H, W), -1e9)
        ids = np.full((H, W), -1, int)
        allx, ally, allz, alli = [], [], [], []
        for i, p in enumerate(parts):
            x, y, z = view.to2d(p.X, p.Y, p.Z)
            allx.append(x); ally.append(y); allz.append(z); alli.append(np.full(x.shape, i))
        x, y, z, pid = (np.concatenate(a) for a in (allx, ally, allz, alli))
        px = np.round((x - x0) * ss).astype(int)
        py = np.round((y - y0) * ss).astype(int)
        ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        px, py, z, pid = px[ok], py[ok], z[ok], pid[ok]
        order = np.argsort(z)
        depth[py[order], px[order]] = z[order]
        ids[py[order], px[order]] = pid[order]
        # close pinholes left by sparse sampling: a pixel with no sample takes its nearest neighbour's value
        empty = ids < 0
        filled = ndimage.binary_closing(~empty, iterations=2) & empty
        if filled.any():
            idx = ndimage.distance_transform_edt(empty, return_distances=False, return_indices=True)
            ids[filled] = ids[idx[0][filled], idx[1][filled]]
            depth[filled] = depth[idx[0][filled], idx[1][filled]]
        # a median pass removes speckles where two surfaces cross
        ids = ndimage.median_filter(ids, size=3) if False else ids
        self.depth, self.ids, self.W, self.H = depth, ids, W, H
        self.thr = thr * view.s * 0 + thr                # depth in model units (view scale not applied to z)
        self.mats = {}
        for i, p in enumerate(parts):
            self.mats.setdefault(p.material, []).append(i)

    # ---- helpers
    def _contours(self, mask, sigma=0.9):
        m = ndimage.gaussian_filter(mask.astype(float), sigma)
        cs = measure.find_contours(np.pad(m, 1), 0.5)
        out = []
        for c in cs:
            c = c - 1
            pts = np.stack([c[:, 1] / self.ss + self.x0, c[:, 0] / self.ss + self.y0], 1)
            out.append(pts)
        return out

    def material_mask(self, mat):
        return np.isin(self.ids, self.mats.get(mat, []))

    def fills(self, colours, grow=0.6):
        """SVG paths: one flat region per material (slightly grown so neighbours overlap under the lines)."""
        out = []
        for mat, idx in self.mats.items():
            if mat not in colours or colours[mat] is None:
                continue
            mask = np.isin(self.ids, idx)
            if not mask.any():
                continue
            if grow:
                mask = ndimage.binary_dilation(mask, iterations=max(1, int(round(grow * self.ss))))
            d = ''
            for c in self._contours(mask):
                c = rdp(c, 0.25)
                if len(c) < 3:
                    continue
                d += lc.smooth([tuple(p) for p in c[:-1]], True)
            if d:
                out.append(f'<path d="{d}" fill="{colours[mat]}" fill-rule="evenodd"/>')
        return out

    def clip_path(self, mats, cid):
        mask = np.isin(self.ids, sum((self.mats.get(m, []) for m in mats), []))
        d = ''
        for c in self._contours(mask):
            c = rdp(c, 0.3)
            if len(c) >= 3:
                d += lc.smooth([tuple(p) for p in c[:-1]], True)
        return f'<clipPath id="{cid}"><path d="{d}" fill-rule="evenodd"/></clipPath>'

    def lines(self, w=lc.LINE, colour=lc.INK, skip=()):
        """Contour strokes where a part is in front of something else."""
        out = []
        ss = self.ss
        for i, p in enumerate(self.parts):
            if not p.line or p.name in skip:
                continue
            mask = self.ids == i
            if mask.sum() < 4:
                continue
            for c in self._contours(mask, 0.8):
                # outward normal: contour of a mask from skimage runs with the region on the left/right;
                # test both sides and take the side that is not this part
                keep = np.zeros(len(c), bool)
                n = len(c)
                if n < 4:
                    continue
                tang = np.roll(c, -1, 0) - np.roll(c, 1, 0)
                nrm = np.stack([tang[:, 1], -tang[:, 0]], 1)
                nrm /= (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9)
                for k in range(n):
                    a = self._sample(c[k] + nrm[k] * 1.6 / ss * 1.0 * 1.5)
                    b = self._sample(c[k] - nrm[k] * 1.6 / ss * 1.5)
                    ia, da = a
                    ib, db = b
                    if ia == i and ib != i:
                        inside, outside, dout = da, ib, db
                    elif ib == i and ia != i:
                        inside, outside, dout = db, ia, da
                    else:
                        continue
                    if outside < 0:
                        keep[k] = True
                    elif self.parts[outside].material != p.material:
                        keep[k] = inside >= dout          # the nearer one draws the shared border
                    else:
                        keep[k] = inside - dout > self.thr
                keep = ndimage.binary_closing(keep, iterations=3) if keep.any() else keep
                keep = ndimage.binary_opening(keep, iterations=2) if keep.any() else keep
                for run in runs(keep, closed=np.allclose(c[0], c[-1])):
                    pts = c[run]
                    pts = rdp(pts, 0.3)
                    if len(pts) >= 2 and seglen(pts) > 3:
                        out.append(lc.line([tuple(q) for q in pts], w, stroke=colour))
        return out

    def _sample(self, pt):
        x = int(round((pt[0] - self.x0) * self.ss))
        y = int(round((pt[1] - self.y0) * self.ss))
        if 0 <= x < self.W and 0 <= y < self.H:
            i = self.ids[y, x]
            return i, self.depth[y, x]
        return -1, -1e9

    def visible(self, X, Y, Z, tol=4.0):
        """Mask of which 3D points are visible (not behind the buffer)."""
        x, y, z = self.v.to2d(X, Y, Z)
        px = np.clip(np.round((x - self.x0) * self.ss).astype(int), 0, self.W - 1)
        py = np.clip(np.round((y - self.y0) * self.ss).astype(int), 0, self.H - 1)
        d = self.depth[py, px]
        return (z >= d - tol) & (self.ids[py, px] >= 0), x, y


def runs(keep, closed):
    n = len(keep)
    if not keep.any():
        return []
    if keep.all():
        return [np.arange(n)]
    idx = np.arange(n)
    if closed:
        start = int(np.argmin(keep))          # rotate so we start at a gap
        idx = np.roll(idx, -start)
        keep = keep[idx]
    out, cur = [], []
    for j, k in zip(idx, keep):
        if k:
            cur.append(j)
        elif cur:
            out.append(np.array(cur)); cur = []
    if cur:
        out.append(np.array(cur))
    return out


def seglen(p):
    return float(np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1)))


def rdp(pts, eps):
    pts = np.asarray(pts)
    if len(pts) < 3:
        return pts
    keep = np.zeros(len(pts), bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        p, q = pts[a], pts[b]
        d = q - p
        L = np.hypot(*d)
        seg = pts[a + 1:b]
        if L < 1e-9:
            dist = np.hypot(*(seg - p).T)
        else:
            dist = np.abs(d[0] * (seg[:, 1] - p[1]) - d[1] * (seg[:, 0] - p[0])) / L
        k = int(np.argmax(dist))
        if dist[k] > eps:
            m = a + 1 + k
            keep[m] = True
            stack += [(a, m), (m, b)]
    return pts[keep]
