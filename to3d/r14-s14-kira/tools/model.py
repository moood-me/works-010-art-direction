"""The model pack Кира's page draws: every part's vertices joined into one skinned mesh on SOMA's skeleton.
Format `kira/model` 1 (an engine pack): positions N×3, triangles T×3 (uint32), skinJoints N×4, skinWeights N×4,
joints 77×3, frames 77×4 (as an engine body), mat N (which paper), pat N×3 (where the paper's streaks and grain are
read: the place at rest before the slouch), fuv N×3 (the face picture's coordinates and how much the surface faces
it; −1 where none), edge N (/255: the sheet's cut edge), rim N (metres to the piece's nearest cut edge, 1 where it has none), parts N×1 (/255, the head)."""
import os
import numpy as np
from common import pack, CACHE, HERE, IX

MATS = ['skin', 'skin_d', 'ear', 'nose', 'hair', 'hair_d', 'hood', 'hood_d', 'pocket', 'band', 'string', 'trou', 'boot', 'sole',
        'lime', 'lime_d', 'cup', 'clay', 'white']


def part(V, T, sj, sw, mat, fuv=None, pat=None, edge=None, rim=None):
    V = np.asarray(V, float)
    return dict(V=V, T=np.asarray(T, np.int64), sj=np.asarray(sj, np.int64), sw=np.asarray(sw, float),
                mat=np.full(len(V), MATS.index(mat)) if isinstance(mat, str) else np.asarray(mat),
                fuv=np.full((len(V), 3), -1.0) if fuv is None else np.asarray(fuv, float), pat=V.copy() if pat is None else pat,
                edge=np.zeros(len(V)) if edge is None else np.asarray(edge, float),
                rim=np.ones(len(V)) if rim is None else np.asarray(rim, float))


def join(parts):
    n = 0; T = []
    for p in parts: T.append(p['T'] + n); n += len(p['V'])
    c = lambda k: np.concatenate([p[k] for p in parts])
    return dict(V=c('V'), T=np.concatenate(T), sj=c('sj'), sw=c('sw'), mat=c('mat'), fuv=c('fuv'), pat=c('pat'), edge=c('edge'), rim=c('rim'))


def write(name, parts, joints, frames, extra=None, folder=None):
    m = join(parts)
    sw = m['sw'] / m['sw'].sum(1, keepdims=True)
    hw = sum(np.where(np.isin(m['sj'][:, k], [IX['Head'], IX['HeadEnd'], IX['Jaw']]), sw[:, k], 0) for k in range(4))
    h = dict(format='kira/model', version=1, id=name, skeleton='soma77', mats=MATS, parts=['head'], **(extra or {}))
    arrays = dict(positions=m['V'].astype(np.float32), triangles=m['T'].astype(np.uint32),
                  skinJoints=m['sj'].astype(np.uint8), skinWeights=sw.astype(np.float32),
                  joints=np.asarray(joints, np.float32), frames=np.asarray(frames, np.float32),
                  mat=m['mat'].astype(np.uint8), pat=m['pat'].astype(np.float32), fuv=m['fuv'].astype(np.float32),
                  edge=np.round(np.clip(m['edge'], 0, 1) * 255).astype(np.uint8), rim=m['rim'].astype(np.float32), parts=np.round(hw * 255)[:, None].astype(np.uint8))
    folder = folder or CACHE
    os.makedirs(folder, exist_ok=True)
    pack.write(os.path.join(folder, f'{name}.json'), h, arrays)
    print(name, 'vertices', len(arrays['positions']), 'triangles', len(arrays['triangles']))
