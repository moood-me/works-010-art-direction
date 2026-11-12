# The motions ordered for this item, as the early engine keeps them (copied from engine/tools/motions.py and changed:
# the list of motions is motions/orders.json, the studio's body data is motions/raw/<id>.json, the files go to
# motions/<id>.json beside them).  python3 tools/convert.py
#
# orders.json: [{id, label: {ru, en}, key, ask: what was asked (prompts, seconds, seed, constraints — as sent, or
# described when long), after?: {motion: <id here>, frames}, startsAt?: {x, z}}] — the studio's `motion(key)` gives
# startsAt for one made with `after`.
# raw/<id>.json: the studio's `motion(key, data: "body")` → {n, fps, names, q, p}, unchanged (tools/keep.py puts it
# there; once converted it is kept only inside motions/<id>.json, whose `data` is the same, and raw/ is emptied).
import base64, json, os, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, '..', '..', 'engine', 'tools'))
import soma  # noqa: E402  (engine/tools/soma.py, read as it is)

S = soma.load()


def arrays(d):
    n = d['n']
    q = np.frombuffer(base64.b64decode(d['q']), '<i2').reshape(n, 77, 4).copy()
    p = np.frombuffer(base64.b64decode(d['p']), '<i2').reshape(n, 77, 3).copy()
    return q, p


def lowest(q, p):
    """SOMA's skin posed each frame, its lowest point (as engine/tools/motions.py)"""
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


if __name__ == '__main__':
    orders = json.load(open(os.path.join(ROOT, 'motions', 'orders.json')))
    keys = {o['id']: o['key'] for o in orders}
    index = []
    only = set(sys.argv[1:])
    for o in orders:
        src = os.path.join(ROOT, 'motions', 'raw', o['id'] + '.json')
        dst = os.path.join(ROOT, 'motions', o['id'] + '.json')
        if not os.path.exists(src) and not os.path.exists(dst):
            print('no data yet:', o['id']); continue
        index.append({'id': o['id'], 'label': o['label'], **({'after': o['after']['motion']} if o.get('after') else {})})
        if (only and o['id'] not in only and os.path.exists(dst)) or not os.path.exists(src): continue
        d = json.load(open(src))
        assert d['names'] == soma.NAMES
        q, p = arrays(d)
        kim = {'key': o['key'], 'prompts': o['ask']['prompts'], 'seconds': o['ask']['seconds']}
        if o.get('after'): kim['after'] = {**o['after'], 'key': keys[o['after']['motion']]}
        if o.get('startsAt'): kim['startsAt'] = o['startsAt']
        out = {'format': 'engine/motion', 'version': 1, 'id': o['id'], 'label': o['label'], 'kimodo': kim,
               'fps': d['fps'], 'frames': int(len(q)), 'skeleton': 'soma77',
               'data': {'names': d['names'], 'q': d['q'], 'p': d['p']},
               'derived': {'lowest': lowest(q, p)}}
        json.dump(out, open(dst, 'w'))
        print(o['id'], len(q), 'frames')
    json.dump({'format': 'two-people/motions', 'motions': index}, open(os.path.join(ROOT, 'motions', 'index.json'), 'w'), indent=1, ensure_ascii=False)
