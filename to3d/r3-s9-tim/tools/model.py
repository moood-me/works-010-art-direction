"""The model pack Tim's page draws: every part's vertices joined into one skinned mesh on SOMA's skeleton.
Format `tim/model` 1 (an engine pack): positions N×3, triangles T×3 (uint32), skinJoints N×4, skinWeights N×4,
joints 77×3, frames 77×4 (as an engine body), mat N (which paint), pat N×3 (where the paint's pattern is read: the
rest place), fuv N×3 (the face picture's coordinates and how much the surface faces it; −1 where none), parts N×1 (/255, the head)."""
import numpy as np
from common import pack, CACHE, HERE

MATS = ['skin', 'skin_d', 'hair', 'shirt', 'shorts', 'sock', 'shoe', 'sole', 'ear', 'collar', 'clay', 'ink', 'hair_d']


def part(V, T, sj, sw, mat, fuv=None, pat=None):
    V = np.asarray(V, float)
    return dict(V=V, T=np.asarray(T, np.int64), sj=np.asarray(sj, np.int64), sw=np.asarray(sw, float),
                mat=np.full(len(V), MATS.index(mat)) if isinstance(mat, str) else np.asarray(mat),
                fuv=np.full((len(V), 3), -1.0) if fuv is None else np.asarray(fuv, float), pat=V.copy() if pat is None else pat)


def write(name, parts, joints, frames, extra=None):
    V, T, SJ, SW, M, F, P = [], [], [], [], [], [], []
    n = 0
    for p in parts:
        V.append(p['V']); T.append(p['T'] + n); SJ.append(p['sj']); SW.append(p['sw']); M.append(p['mat']); F.append(p['fuv']); P.append(p['pat'])
        n += len(p['V'])
    sw = np.concatenate(SW); sw = sw / sw.sum(1, keepdims=True)
    # the body parts the engine's corrections read (only 'head': armsOutOfHead finds the head's ball from it)
    from common import IX
    sj = np.concatenate(SJ); hw = sum(np.where(np.isin(sj[:, k], [IX['Head'], IX['HeadEnd'], IX['Jaw']]), sw[:, k], 0) for k in range(4))
    h = dict(format='tim/model', version=1, id=name, skeleton='soma77', mats=MATS, parts=['head'], **(extra or {}))
    arrays = dict(positions=np.concatenate(V).astype(np.float32), triangles=np.concatenate(T).astype(np.uint32),
                  skinJoints=np.concatenate(SJ).astype(np.uint8), skinWeights=sw.astype(np.float32),
                  joints=np.asarray(joints, np.float32), frames=np.asarray(frames, np.float32),
                  mat=np.concatenate(M).astype(np.uint8), pat=np.concatenate(P).astype(np.float32),
                  fuv=np.concatenate(F).astype(np.float32), parts=np.round(hw * 255)[:, None].astype(np.uint8))
    pack.write(f'{CACHE}/{name}.json', h, arrays)
    if name == 'tim':      # the viewer's copy, in the folder (to3d/r3-s9-tim/model)
        import os
        os.makedirs(os.path.join(HERE, '..', 'model'), exist_ok=True)
        pack.write(os.path.join(HERE, '..', 'model', 'tim.json'), h, arrays)
    print(name, 'vertices', len(arrays['positions']), 'triangles', len(arrays['triangles']))
