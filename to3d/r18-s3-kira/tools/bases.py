"""Packs of the bases as they come, for the page's steps: Anny's girl body (moood-girl) and the Human Base Meshes
stylised head (only scaled to the drawing's head height), in the same flat look, no fitting.  python3 bases.py outdir"""
import os, sys
import numpy as np
import pack, mesh as M, head as Hd, drawing as D

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
sk = pack.skeleton(); I = {j['name']: i for i, j in enumerate(sk['joints'])}
h, a, th, t = pack.body('moood-girl')
skin, shade, line = [241, 211, 192], [220, 171, 151], [154, 96, 82]


def save(name, V, T, SJ, SW, joints):
    N = len(V)
    pack.save(os.path.join(out, name + '.json'), dict(format='r1/character', version=2, id=name, trianglePieces={'all': [0, len(T)]}),
              dict(positions=V.astype(np.float32).ravel(), triangles=T.astype(np.uint32).ravel(), skinJoints=SJ.astype(np.uint8),
                   skinWeights=SW.astype(np.float32), joints=joints.astype(np.float32).ravel(), frames=a['frames'].astype(np.float32).ravel(),
                   col=np.tile(skin, (N, 1)).astype(np.uint8), shd=np.tile(shade, (N, 1)).astype(np.uint8), lin=np.tile(line, (N, 1)).astype(np.uint8),
                   ow=np.full(N, 255, np.uint8), uv=np.zeros((N, 2), np.float32), tex=np.zeros(N, np.uint8), pn=np.zeros((N, 3), np.float32),
                   pw=np.zeros(N, np.uint8), pj=np.zeros(N, np.float32), two=np.zeros(N, np.uint8), band=np.full(N, -1, np.float32)))


save('anny', a['positions'].reshape(-1, 3), t['triangles'].reshape(-1, 3), t['skinJoints'].reshape(-1, 4), t['skinWeights'].reshape(-1, 4), a['joints'].reshape(-1, 3))
v, P, d = Hd.load(os.path.join(os.path.dirname(out.rstrip('/')), 'hbm_head.npz'))
s = ((Hd.Y_DRAW[1] - Hd.Y_DRAW[3]) * D.K) / (Hd.Y_BASE[3] - Hd.Y_BASE[1])       # chin to crown as drawn
V = (v - [0, Hd.Y_BASE[2], 0.03]) * s + [0, (D.FLOOR - Hd.Y_DRAW[2]) * D.K, 0]  # the eye line at the drawing's
T = M.triangulate(P)
SJ = np.zeros((len(V), 4)); SJ[:, 0] = I['Head']; SW = np.zeros((len(V), 4)); SW[:, 0] = 1
save('hbm-head', V, T, SJ, SW, a['joints'].reshape(-1, 3))
