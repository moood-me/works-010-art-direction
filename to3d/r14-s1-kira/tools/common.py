"""Shared paths and readers (style С1, Pixar → 3D); the character is named in char.py."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../..'))
ENGINE = os.path.join(REPO, 'engine')
STYLE = os.path.join(REPO, 'styles/s1-pixar')
import char
CACHE = char.CACHE
os.makedirs(CACHE, exist_ok=True)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ENGINE, 'tools'))
import pack  # noqa: E402

SK = json.load(open(os.path.join(ENGINE, 'data/skeleton.json')))
NAMES = [j['name'] for j in SK['joints']]
IX = {n: i for i, n in enumerate(NAMES)}
PARENT = np.array([j['parent'] for j in SK['joints']])
NJ = len(NAMES)

# the drawing's units → metres, the same for the whole cast of the style (Тим: 430 units = 1.20 m)
K = 0.0028
FLOOR = char.FLOOR


def to_m(P):
    """drawing person units (x his left, y down, z forward) → metres (x his left, y up, z forward), feet at 0"""
    P = np.asarray(P, float)
    return np.c_[P[..., 0] * K, (FLOOR - P[..., 1]) * K, P[..., 2] * K]


def children(j):
    return [k for k in range(NJ) if PARENT[k] == j]


def load_body(bid):
    h, a = pack.read(os.path.join(ENGINE, f'data/bodies/{bid}.json'))
    th, t = pack.read(os.path.join(ENGINE, f'data/topology/{h["topology"]}.json'))
    return dict(positions=a['positions'].astype(np.float64), joints=a['joints'].astype(np.float64),
                frames=a['frames'].astype(np.float64), triangles=t['triangles'].astype(np.int64),
                sj=t['skinJoints'].astype(np.int64), sw=t['skinWeights'].astype(np.float64),
                parts=t['parts'], partnames=th['parts'])


def dense(sj, sw):
    D = np.zeros((len(sj), NJ))
    for k in range(sj.shape[1]): np.add.at(D, (np.arange(len(sj)), sj[:, k]), sw[:, k])
    return D


def top4(D):
    j = np.argsort(-D, 1)[:, :4]; w = np.take_along_axis(D, j, 1)
    return j, w / np.maximum(w.sum(1, keepdims=True), 1e-9)
