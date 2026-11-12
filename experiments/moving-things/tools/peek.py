# What a made motion does, in numbers (Kimodo's own space): every `step` frames the pelvis (x, y, z, heading) and
# the middles of both palms. For reading a free take before writing constraints from it, and for checking a
# constrained take against what was asked.
#   python3 tools/peek.py <id> [step]          — motions/<id>.json or motions/raw/<id>.json
import os, sys, numpy as np
import kimodo as K
from pose import heading_of

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(HERE)


def load(n):
    p = os.path.join(ITEM, 'motions', n + '.json')
    return K.read_raw(p if os.path.exists(p) else os.path.join(ITEM, 'motions', 'raw', n + '.json'))


if __name__ == '__main__':
    m = load(sys.argv[1]); step = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    f2 = lambda v: ' '.join(f'{x:6.2f}' for x in v)
    print(f'{m["n"]} frames')
    for f in list(range(0, m['n'], step)) + [m['n'] - 1]:
        ps = K.pose(m, f); p = ps['p']
        print(f'{f:4d} pelvis {f2(p[0])} h {np.degrees(heading_of(ps["G"])):6.0f} | L {f2(K.palm(p, "L"))} | R {f2(K.palm(p, "R"))}')
