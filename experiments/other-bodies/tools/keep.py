# keep a made motion: its body data (the studio's answer to motion(key, data: "body"), saved to a file) into
# motions/raw/<id>.json, and its order into motions/orders.json.
#   python3 tools/keep.py <id> <saved file> '<order as JSON: {label, key, ask, after?, startsAt?}>'
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
mid, src, order = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
d = json.load(open(src)); assert d['n'] and d['names']
json.dump(d, open(os.path.join(ROOT, 'motions', 'raw', mid + '.json'), 'w'))
path = os.path.join(ROOT, 'motions', 'orders.json')
orders = json.load(open(path)) if os.path.exists(path) else []
orders = [o for o in orders if o['id'] != mid] + [{'id': mid, **order}]
json.dump(orders, open(path, 'w'), indent=1, ensure_ascii=False)
print(mid, d['n'], 'frames kept')
