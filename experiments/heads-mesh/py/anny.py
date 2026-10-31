import numpy as np, json, base64, re, os
D = os.path.join(os.path.dirname(__file__), '..', 'data')
META = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'meta.json')))
JN = META['joints']; JI = {n: i for i, n in enumerate(JN)}
def raw(name):
    s = open(os.path.join(D, name + '.js')).read()
    return base64.b64decode(re.search(r'"([^"]+)"', s).group(1))
class R:
    def __init__(s, b): s.b = b; s.at = 0
    def take(s, dt, n):
        dt = np.dtype(dt); a = np.frombuffer(s.b[s.at:s.at + n * dt.itemsize], dt).copy(); s.at += n * dt.itemsize; return a
def base():
    r = R(raw('base')); N, T = r.take('<u4', 2); tris = r.take('<u2', T * 3).reshape(-1, 3).astype(np.int64)
    joint = r.take('u1', N * 4).reshape(-1, 4); weight = r.take('u1', N * 4).reshape(-1, 4) / 255.
    F = r.take('<u4', 1)[0]; face = r.take('<u2', F)
    return dict(N=int(N), tris=tris, joint=joint, weight=weight, face=face)
def person(name, bs):
    r = R(raw(name)); at = r.take('<i2', bs['N'] * 3).astype(np.float64).reshape(-1, 3) / 10000
    r.take('<i2', len(bs['face']) * 3); inv = r.take('<f4', 77 * 12).reshape(77, 12)
    J = []
    for j in range(77):
        m = np.eye(4); m[:3, :] = inv[j].reshape(3, 4); J.append(np.linalg.inv(m)[:3, 3])
    return at, np.array(J)
def wOf(bs, names):
    ids = [JI[n] for n in names]; return (np.isin(bs['joint'], ids) * bs['weight']).sum(1)
