# A made motion into this folder, in the early engine's motion format (engine/README.md: Motion), with everything that
# was asked for it (motions/asks.json: key, prompts, seconds, seed, constraints or the plan they came from, after) so it
# can be made again:
#   python3 tools/store.py <id> [startsAt x z]   — reads motions/raw/<id>.json (what motion(key, data: "body") gave)
# startsAt: for one made with `after`, where its origin is in the earlier one's space (motion(key) says it).
# The lowest point of SOMA's posed skin each frame is computed as engine/tools/motions.py does (copied: `lowest`).
import json, os, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot

HERE = os.path.dirname(os.path.abspath(__file__))
ITEM = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ITEM, '..', '..', 'engine', 'tools'))
import soma  # noqa: E402  (the engine's, read as it is)

S = soma.load()


def lowest(q, p):
    out = []
    for f in range(len(q)):
        R = Rot.from_quat(q[f] / 32767.0).as_matrix() @ S['R'].transpose(0, 2, 1)
        T = p[f] / 1000.0 - np.einsum('jab,jb->ja', R, S['P'])
        y = np.zeros(S['V'])
        for k in range(8):
            j = S['joint'][:, k]
            y += S['weight'][:, k] * (np.einsum('vb,vb->v', R[j, 1, :], S['bind']) + T[j, 1])
        out.append(round(float(y.min()), 4))
    return out


def store(mid, sx=None, sz=None):
    import base64
    d = json.load(open(os.path.join(ITEM, 'motions', 'raw', mid + '.json')))
    ask = json.load(open(os.path.join(ITEM, 'motions', 'asks.json')))[mid]
    assert d['names'] == soma.NAMES
    n = d['n']
    q = np.frombuffer(base64.b64decode(d['q']), '<i2').reshape(n, 77, 4)
    p = np.frombuffer(base64.b64decode(d['p']), '<i2').reshape(n, 77, 3)
    kim = {'key': ask['key'], 'prompts': ask['prompts'], 'seconds': ask['seconds'], 'ask': ask}
    if ask.get('after'):
        kim['after'] = dict(ask['after'])
        kim['startsAt'] = {'x': float(sx), 'z': float(sz)}
    out = {'format': 'engine/motion', 'version': 1, 'id': mid, 'label': {'ru': mid, 'en': mid}, 'kimodo': kim,
           'fps': d['fps'], 'frames': n, 'skeleton': 'soma77', 'data': {'names': d['names'], 'q': d['q'], 'p': d['p']},
           'derived': {'lowest': lowest(q.astype(float), p.astype(float))}}
    json.dump(out, open(os.path.join(ITEM, 'motions', mid + '.json'), 'w'))
    print(mid, n, 'frames')


if __name__ == '__main__':
    store(*sys.argv[1:])
