# startsAt of a motion made `after` another, as the studio computes it: the earlier one's pelvis at its frame n−k less
# the new one's at its frame 0 (x, z). Checked on a-look against the studio's own answer: within 0.5 mm.
#   python3 tools/startsat.py <earlier id here> <frames k> <the new one's body data file>
import sys, json, base64, numpy as np
import pose as P
q, p = P.raw(sys.argv[1]); k = int(sys.argv[2])
d = json.load(open(sys.argv[3])); p2 = np.frombuffer(base64.b64decode(d['p']), '<i2').reshape(d['n'], 77, 3) / 1000
s = p[len(p) - k, 0] - p2[0, 0]
print(json.dumps({'x': round(float(s[0]), 4), 'z': round(float(s[2]), 4)}))
