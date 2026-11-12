"""Read and write the engine's packs (engine/src/pack.js) from Python."""
import json, os
import numpy as np

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'engine')
DT = {'float32': np.float32, 'uint16': np.uint16, 'uint8': np.uint8, 'int16': np.int16, 'uint32': np.uint32}


def load(path):
    h = json.load(open(path))
    raw = open(os.path.join(os.path.dirname(path), h['bin']), 'rb').read()
    a = {}
    for k, m in h['arrays'].items():
        dt = np.dtype(DT[m['dtype']]).newbyteorder('<')
        n = int(np.prod(m['shape']))
        a[k] = np.frombuffer(raw, dt, n, m['offset']).reshape(m['shape'])
    return h, a


def save(path, header, arrays):
    base = os.path.splitext(os.path.basename(path))[0]
    off, chunks, meta = 0, [], {}
    for k, v in arrays.items():
        v = np.ascontiguousarray(v)
        name = [n for n, t in DT.items() if np.dtype(t) == v.dtype][0]
        b = v.astype(v.dtype.newbyteorder('<')).tobytes()
        meta[k] = dict(dtype=name, shape=list(v.shape), offset=off)
        chunks.append(b); off += len(b)
        pad = (-off) % 8; chunks.append(b'\0' * pad); off += pad
    header = dict(header, arrays=meta, bin=base + '.bin')
    json.dump(header, open(path, 'w'), ensure_ascii=False, indent=1)
    open(os.path.join(os.path.dirname(path), base + '.bin'), 'wb').write(b''.join(chunks))


def body(bid):
    h, a = load(os.path.join(ENGINE, 'data', 'bodies', bid + '.json'))
    th, t = load(os.path.join(ENGINE, 'data', 'topology', h['topology'] + '.json'))
    return h, a, th, t


def skeleton():
    s = json.load(open(os.path.join(ENGINE, 'data', 'skeleton.json')))
    return s
