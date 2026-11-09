"""The model pack the page draws: every part joined into one skinned mesh on SOMA's 77 joints.
Format `tim-pixar/model` 1 (Р6's) (an engine pack): positions N×3, triangles T×3 (uint32), skinJoints N×4, skinWeights N×4,
joints 77×3, frames 77×4 (as an engine body); and for the look: mat N (which material), pat N×3 (the rest place, where
patterns are read), aux N×4 (per material: the face layer's u, v, how much the surface faces front, the lash line; the
eye's own direction for the iris), ao N (ambient occlusion baked on the rest model), parts N (/255, the head's share,
which the engine's arms-out-of-head correction reads)."""
import numpy as np
from common import pack, CACHE, HERE, IX

# the first five and 'teeth' keep their places in every character of the style (the look reads them by number)
MATS = ['skin', 'lip', 'mouth', 'eye', 'hair', 'coat', 'turtle', 'pants', 'frame', 'shoe', 'sole', 'teeth', 'streak', 'belt', 'tongue']


def part(V, T, sj, sw, mat, aux=None, pat=None, name=''):
    V = np.asarray(V, float)
    return dict(V=V, T=np.asarray(T, np.int64), sj=np.asarray(sj, np.int64), sw=np.asarray(sw, float),
                mat=np.full(len(V), MATS.index(mat)) if isinstance(mat, str) else np.asarray(mat),
                aux=np.zeros((len(V), 4)) if aux is None else np.asarray(aux, float), pat=V.copy() if pat is None else np.asarray(pat, float),
                name=name)


def join(parts):
    out = {k: [] for k in ('V', 'T', 'sj', 'sw', 'mat', 'aux', 'pat', 'face', 'jaw')}; n = 0; ranges = {}
    for p in parts:
        p.setdefault('face', np.zeros((len(p['V']), 4))); p.setdefault('jaw', np.zeros(len(p['V'])))
        for k in out: out[k].append(p[k] + (n if k == 'T' else 0))
        if p['name']:
            a, b = ranges.get(p['name'], (n, n)); ranges[p['name']] = (min(a, n), n + len(p['V']))
        n += len(p['V'])
    return {k: np.concatenate(v) for k, v in out.items()}, ranges


def write(name, parts, joints, frames, ao=None, extra=None, out_dirs=()):
    M, ranges = join(parts)
    sw = M['sw'] / M['sw'].sum(1, keepdims=True)
    sj = M['sj']
    hw = sum(np.where(np.isin(sj[:, k], [IX['Head'], IX['HeadEnd'], IX['Jaw']]), sw[:, k], 0) for k in range(4))
    h = dict(format='tim-pixar/model', version=1, id=name, skeleton='soma77', mats=MATS, parts=['head'],
             ranges={k: list(map(int, v)) for k, v in ranges.items()}, **(extra or {}))
    arrays = dict(positions=M['V'].astype(np.float32), triangles=M['T'].astype(np.uint32),
                  skinJoints=sj.astype(np.uint8), skinWeights=sw.astype(np.float32),
                  joints=np.asarray(joints, np.float32), frames=np.asarray(frames, np.float32),
                  mat=M['mat'].astype(np.uint8), pat=M['pat'].astype(np.float32), aux=M['aux'].astype(np.float32),
                  ao=(np.zeros(len(M['V'])) if ao is None else ao).astype(np.float32), face=M['face'].astype(np.float32), jaw=M['jaw'].astype(np.float32),
                  parts=np.round(hw * 255)[:, None].astype(np.uint8))
    for d in (CACHE,) + tuple(out_dirs):
        pack.write(f'{d}/{name}.json', h, arrays)
    print(name, 'vertices', len(arrays['positions']), 'triangles', len(arrays['triangles']))
    return M
