"""Shared paths and readers for Кира's build."""
import os, sys, json
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
ENGINE = os.path.join(REPO, 'engine')
STYLE = os.path.join(REPO, 'styles/s14-paper')
CACHE = '/home/user/cache/to3d-r14-s14-kira'
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(CACHE, exist_ok=True)
sys.path.insert(0, os.path.join(ENGINE, 'tools'))
sys.path.insert(0, os.path.join(STYLE, 'tools'))
import pack  # noqa: E402

SK = json.load(open(os.path.join(ENGINE, 'data/skeleton.json')))
NAMES = [j['name'] for j in SK['joints']]
IX = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in SK['joints']])
NJ = len(NAMES)


def children(j):
    return [k for k in range(len(NAMES)) if PARENT[k] == j]


def load_body(bid):
    h, a = pack.read(os.path.join(ENGINE, f'data/bodies/{bid}.json'))
    th, t = pack.read(os.path.join(ENGINE, f'data/topology/{h["topology"]}.json'))
    return dict(positions=a['positions'].astype(np.float64), joints=a['joints'].astype(np.float64),
                frames=a['frames'].astype(np.float64), triangles=t['triangles'].astype(np.int64),
                sj=t['skinJoints'].astype(np.int64), sw=t['skinWeights'].astype(np.float64),
                parts=t['parts'], partnames=th['parts'])


def vertex_normals(V, T):
    n = np.zeros_like(V)
    fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    for k in range(3): np.add.at(n, T[:, k], fn)
    return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)


def dense(sj, sw):
    D = np.zeros((len(sj), NJ))
    for k in range(4): np.add.at(D, (np.arange(len(sj)), sj[:, k]), sw[:, k])
    return D


def top4(D):
    j = np.argsort(-D, 1)[:, :4]; w = np.take_along_axis(D, j, 1)
    return j, w / np.maximum(w.sum(1, keepdims=True), 1e-9)
