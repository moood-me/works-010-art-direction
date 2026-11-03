# A pack: the engine's plain data file — a JSON header and a binary file of little-endian arrays beside it.
#   <name>.json: {"format": ..., "version": ..., ..., "bin": "<name>.bin",
#                 "arrays": {<key>: {"dtype": "float32" | "uint16" | "uint8" | "int16" | "uint32", "shape": [...], "offset": bytes}}}
#   <name>.bin:  the arrays one after another, each starting at a multiple of 4 bytes.
# src/pack.js reads the same.
import json, os, numpy as np

DTYPES = {'float32': '<f4', 'uint16': '<u2', 'uint8': 'u1', 'int16': '<i2', 'uint32': '<u4'}


def write(path_json, header, arrays):
    """header: dict (no 'arrays' / 'bin'); arrays: {key: np.ndarray} — written in this order."""
    base = os.path.splitext(os.path.basename(path_json))[0]
    out, meta, at = bytearray(), {}, 0
    for key, a in arrays.items():
        dt = np.dtype(a.dtype).name   # the caller gives each array in the type it is to be kept in
        if dt not in DTYPES: raise ValueError(f'{key}: {dt} is not a pack type')
        b = np.ascontiguousarray(a.astype(DTYPES[dt])).tobytes()
        meta[key] = {'dtype': dt, 'shape': list(a.shape), 'offset': at}
        out += b
        pad = (-len(out)) % 4
        out += b'\0' * pad
        at = len(out)
    h = dict(header)
    h['bin'] = base + '.bin'
    h['arrays'] = meta
    with open(path_json, 'w') as f:
        json.dump(h, f, indent=1, ensure_ascii=False)
        f.write('\n')
    with open(os.path.join(os.path.dirname(path_json), base + '.bin'), 'wb') as f:
        f.write(out)


def read(path_json):
    h = json.load(open(path_json))
    raw = open(os.path.join(os.path.dirname(path_json), h['bin']), 'rb').read()
    arrays = {}
    for key, m in h['arrays'].items():
        dt = np.dtype(DTYPES[m['dtype']])
        n = int(np.prod(m['shape']))
        arrays[key] = np.frombuffer(raw, dt, n, m['offset']).reshape(m['shape'])
    return h, arrays
