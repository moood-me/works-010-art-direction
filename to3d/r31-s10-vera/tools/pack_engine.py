"""Write the character (who.py) as an engine body (engine/README.md: Formats): one mesh of every piece, its own topology
(triangles, four SOMA joints and weights per vertex, parts), and the body pack (positions, joints, frames — Anny's
frames unchanged, so Kimodo's motions carry onto it as onto any engine body). Also offsets.json: which vertices are
which piece, for the renderer.  Written to CACHE/engine/data/{bodies,topology}/<who.ID>.*"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, '../../..')
sys.path.insert(0, os.path.join(REPO, 'engine/tools'))
sys.path.insert(0, HERE)
import who    # noqa: E402
import pack   # noqa: E402


def write(C, objs, arrays, RIG, J1, K, FLOOR):
    _, bod = pack.read(os.path.join(REPO, f'engine/data/bodies/{who.BASE_BODY}.json'))
    th, _ = pack.read(os.path.join(REPO, 'engine/data/topology/anny-moood.json'))
    Vs, Ts, SJ, SW, offs = [], [], [], [], {}
    n = 0
    for o in objs:
        V = arrays['obj_' + o['name'] + '_v']
        F = arrays['obj_' + o['name'] + '_f']
        tris = []
        for f in F:
            f = [x for x in f if x >= 0]
            for i in range(1, len(f) - 1):
                tris.append((f[0], f[i], f[i + 1]))
        Vs.append(V); Ts.append(np.array(tris, int) + n)
        sj, sw = RIG[o['name']]
        sw = np.asarray(sw, float); sw = sw / sw.sum(1, keepdims=True)
        SJ.append(np.asarray(sj)); SW.append(sw)
        offs[o['name']] = [n, n + len(V)]
        n += len(V)
    V = np.vstack(Vs)
    P = np.stack([V[:, 0] * K, (FLOOR - V[:, 1]) * K, V[:, 2] * K], 1).astype(np.float32)
    J = np.stack([J1[:, 0] * K, (FLOOR - J1[:, 1]) * K, J1[:, 2] * K], 1)
    # the drawing's frame flips y: a triangle's winding is mirrored there — turned back for the engine's normals
    T = np.vstack(Ts)[:, ::-1]
    sj = np.vstack(SJ); sw = np.vstack(SW)
    parts = np.zeros((len(V), len(th['parts'])), np.uint8)
    out = os.path.join(C, 'engine/data')
    os.makedirs(out + '/bodies', exist_ok=True); os.makedirs(out + '/topology', exist_ok=True)
    pack.write(out + f'/topology/{who.ID}.json',
               dict(format='engine/topology', version=1, id=who.ID, about=who.RU + ': every piece in one mesh',
                    source=who.SOURCE, skeleton='soma77', vertices=len(V), triangles=len(T),
                    parts=th['parts']),
               dict(triangles=T.astype(np.uint32), skinJoints=sj.astype(np.uint8), skinWeights=sw.astype(np.float32),
                    parts=parts))
    pack.write(out + f'/bodies/{who.ID}.json',
               dict(format='engine/body', version=1, id=who.ID, label=dict(ru=who.RU, en=who.ID.capitalize()),
                    source=who.SOURCE + f': Anny ({who.BASE_BODY}) fitted to the С10 drawing, HBM head',
                    topology=who.ID, skeleton='soma77'),
               dict(positions=P, joints=J.astype(np.float32), frames=np.asarray(bod['frames'], np.float32)))
    json.dump(offs, open(os.path.join(C, 'engine/offsets.json'), 'w'))
    print('engine body', len(V), 'vertices', len(T), 'triangles')
