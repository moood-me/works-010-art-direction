"""Shared paths, constants and small helpers for Савелий Петрович (С8, stop-motion) in 3D."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../..'))
ENGINE = os.path.join(REPO, 'engine')
STYLE = os.path.join(REPO, 'styles/s8-stopmotion')
CACHE = '/home/user/cache/to3d-r28-s8-marat'
FOLDER = os.path.abspath(os.path.join(HERE, '..'))
os.makedirs(CACHE, exist_ok=True)
sys.path.insert(0, os.path.join(ENGINE, 'tools'))
sys.path.insert(0, os.path.join(STYLE, 'tools'))
import pack  # noqa: E402  (the engine's pack writer/reader)

# The drawing's head height (crown to chin) in metres. The cast keeps one scale: in the style's picture of all six
# (build.py six()) Тим's head is 200 px and Савелий's 182, and Тим's head in 3D (Р10) is 0.342 m — so 0.311 m here.
# The figure is 3.88 heads tall (crown −0.5 … feet 3.38 under the head's centre, figure-savely): 1.21 m — a puppet's
# proportions, a little taller than Тим, as in the drawing of the cast.
HH = 0.342 * 182 / 200
FEET = 3.38          # the floor, in head units below the head's centre (styles/s8-stopmotion/tools/build.py FIG)
HEAD_Y = FEET * HH   # the head's centre above the floor at rest (metres)
BID = 'marat8'      # the engine body's id
NAME = 'savely'

SK = json.load(open(os.path.join(ENGINE, 'data/skeleton.json')))
NAMES = [j['name'] for j in SK['joints']]
IX = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in SK['joints']])


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


def hu(p):
    """the drawing's head units (x right, y down, z toward us; head centre 0) → engine axes in head units
    (x his left, y up, z forward)."""
    p = np.asarray(p, float)
    return np.stack([p[..., 0], -p[..., 1], p[..., 2]], -1)
