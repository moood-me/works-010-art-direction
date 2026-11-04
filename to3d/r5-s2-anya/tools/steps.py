"""Pictures of the steps (software raster, clay): the base head as it is, closed, fitted over the drawing; with the
hair; Anny's body before and after the fitting.  python3 steps.py outdir"""
import sys, os, numpy as np
from PIL import Image
import mesh as M, head as H, hair as HR, look_head as LH, pack

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
v, P, vis, eL, eR = H.load()
T = M.triangulate(P)
box = (-0.15, 0.15, 0.5, 0.9)
row = [M.raster(np.r_[v, eL, eR], np.r_[T, M.triangulate(M.polys_of(*[np.load(H.HBM)[k] for k in ('eyeL_fs', 'eyeL_f')])) + len(v),
       M.triangulate(M.polys_of(*[np.load(H.HBM)[k] for k in ('eyeR_fs', 'eyeR_f')])) + len(v) + len(eL)], y, 400, box if y < 1 else (-0.2, 0.1, 0.5, 0.9))[0] for y in (0, 0.7, np.pi / 2)]
Image.fromarray(np.hstack(row)).save(f'{out}/s1-base.png')
v2, P2, patch = H.blank(v, P); T2 = M.triangulate(P2)
Image.fromarray(np.hstack([M.raster(v2, T2, y, 400, box if y < 1 else (-0.2, 0.1, 0.5, 0.9))[0] for y in (0, 0.7, np.pi / 2)])).save(f'{out}/s2-closed.png')
V, P3, patch = H.build(); T3 = M.triangulate(P3)
LH.overlay(V, T3, f'{out}/s3-fitted.png')
N = M.vertex_normals(V, T3)
hv, ht, outer, yd = HR.build(V, N)
AV = np.r_[V, hv]; AT = np.r_[T3, ht + len(V)]
col = np.r_[np.tile([0.93, 0.71, 0.59], (len(V), 1)), np.tile([0.58, 0.31, 0.17], (len(hv), 1))]
LH.overlay(AV, AT, f'{out}/s4-hair.png', col)
h, a, th, t = pack.body('moood-woman')
P0 = a['positions'].reshape(-1, 3); T0 = t['triangles'].reshape(-1, 3).astype(np.int64)
b = (-0.6, 0.6, -0.05, 1.75)
Image.fromarray(np.hstack([M.raster(P0, T0, 0, 400, b)[0], M.raster(P0, T0, np.pi / 2, 400, b)[0]])).save(f'{out}/s5-anny.png')
