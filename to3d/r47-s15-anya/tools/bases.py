"""Packs of the bases as they come, for the page's steps: Anny's body (moood-woman) and the Human Base Meshes stylised
head (only scaled to the drawing's head height), in the same flat style, no fitting.  python3 bases.py outdir"""
import os, sys
import numpy as np
import pack, mesh as M, headfit as Hd, drawing as D

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
sk = pack.skeleton(); I = {j['name']: i for i, j in enumerate(sk['joints'])}
h, a, th, t = pack.body('moood-woman')
skin, shade, line = [230, 198, 164], [7, 7, 11], [59, 69, 102]


def save(name, V, T, SJ, SW, joints):
    N = len(V)
    pack.save(os.path.join(out, name + '.json'), dict(format='r1/character', version=1, id=name, faces='.', trianglePieces={'all': [0, len(T)]}),
              dict(positions=V.astype(np.float32).ravel(), triangles=T.astype(np.uint32).ravel(), skinJoints=SJ.astype(np.uint8),
                   skinWeights=SW.astype(np.float32), joints=joints.astype(np.float32).ravel(), frames=a['frames'].astype(np.float32).ravel(),
                   col=np.tile(skin, (N, 1)).astype(np.uint8), shd=np.tile(shade, (N, 1)).astype(np.uint8), lin=np.tile(line, (N, 1)).astype(np.uint8),
                   ow=np.full(N, 255, np.uint8), uv=np.zeros((N, 2), np.float32), tex=np.zeros(N, np.uint8), pn=np.zeros((N, 3), np.float32),
                   pw=np.zeros(N, np.uint8), pj=np.zeros(N, np.float32), two=np.zeros(N, np.uint8), band=np.full(N, -1, np.float32)))


save('anny', a['positions'].reshape(-1, 3), t['triangles'].reshape(-1, 3), t['skinJoints'].reshape(-1, 4), t['skinWeights'].reshape(-1, 4), a['joints'].reshape(-1, 3))
v, P, eyes, r, vis = Hd.load('/home/user/cache/to3d-r47-s15-anya/hbm_head.npz')
s = ((D.CHIN - D.SKULL) * D.K) / (0.888 - 0.575)
V = (v - [0, 0.7287, 0.03]) * s + [0, (D.FLOOR) * D.K, 0]
V[:, 1] = (v[:, 1] - 0.7287) * s + D.FLOOR * D.K       # eye line at drawing y=0
T = M.triangulate(P)
SJ = np.zeros((len(V), 4)); SJ[:, 0] = I['Head']; SW = np.zeros((len(V), 4)); SW[:, 0] = 1
save('hbm-head', V, T, SJ, SW, a['joints'].reshape(-1, 3))
