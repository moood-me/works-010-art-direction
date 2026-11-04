"""Packs of the bases as they come, for the page's steps: Anny's body (moood-woman) and the Human Base Meshes stylised
head (only scaled and placed at the drawing's head), in the same flat style, no fitting.  python3 bases.py outdir"""
import os, sys
import numpy as np
import pack, mesh as M, headfit as Hf, drawing as D

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
sk = pack.skeleton(); I = {j['name']: i for i, j in enumerate(sk['joints'])}
h, a, th, t = pack.body('moood-woman')
skin, shade, line = D.rgb(D.COL['skin']), D.shade(D.COL['skin']), D.rgb(D.INK)


def save(name, V, T, SJ, SW, joints):
    N = len(V)
    pack.save(os.path.join(out, name + '.json'), dict(format='r1/character', version=1, id=name, faces='.', face=dict(x0=-1, x1=1, y0=-1, y1=1),
                                                       pieces={'all': [0, N], 'skirt': [0, 0]}, trianglePieces={'all': [0, len(T)], 'skirt': [0, 0]}),
              dict(positions=V.astype(np.float32).ravel(), triangles=T.astype(np.uint32).ravel(), skinJoints=SJ.astype(np.uint8),
                   skinWeights=SW.astype(np.float32), joints=joints.astype(np.float32).ravel(), frames=a['frames'].astype(np.float32).ravel(),
                   col=np.tile(skin, (N, 1)).astype(np.uint8), shd=np.tile(shade, (N, 1)).astype(np.uint8), lin=np.tile(line, (N, 1)).astype(np.uint8),
                   ow=np.full(N, 255, np.uint8), uv=np.zeros((N, 2), np.float32), tex=np.zeros(N, np.uint8), pn=np.zeros((N, 3), np.float32),
                   pw=np.zeros(N, np.uint8), pj=np.zeros(N, np.float32), two=np.ones(N, np.uint8), band=np.full(N, -1, np.float32),
                   ob=np.zeros(N, np.float32)))


save('anny', a['positions'].reshape(-1, 3), t['triangles'].reshape(-1, 3), t['skinJoints'].reshape(-1, 4), t['skinWeights'].reshape(-1, 4), a['joints'].reshape(-1, 3))
v, P, eyes, r, vis = Hf.load('/home/user/cache/to3d-r9-s7-anya/hbm_head.npz')
# chin → y −1, crown → +1 of the drawing's head; centred like it
s = 2.0 / (Hf.Y_BASE[3] - Hf.Y_BASE[1])
L = (v - [0, (Hf.Y_BASE[3] + Hf.Y_BASE[1]) / 2, 0.02]) * s
V = D.head_to_model(L)
T = M.triangulate(P)
SJ = np.zeros((len(V), 4)); SJ[:, 0] = I['Head']; SW = np.zeros((len(V), 4)); SW[:, 0] = 1
save('hbm-head', V, T, SJ, SW, a['joints'].reshape(-1, 3))
