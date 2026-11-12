# The studio's body data of a motion (what motion(key, data: "body") answered, saved to a file) into motions/raw/<id>.json.
#   python3 tools/keep_raw.py <id> <file>
import json, os, sys
ITEM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(sys.argv[2])); assert set(d) >= {'n', 'fps', 'names', 'q', 'p'}
json.dump(d, open(os.path.join(ITEM, 'motions', 'raw', sys.argv[1] + '.json'), 'w'))
print(sys.argv[1], d['n'], 'frames')
