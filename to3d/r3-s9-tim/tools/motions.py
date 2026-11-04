"""Kimodo motions ordered for Тим from the moood studio (make_motion), kept as the engine keeps motions
(engine/motions/<id>.json format, written to the cache): python3 motions.py <id> <raw.json> <key> <prompt> <seconds>
raw.json is the studio's `motion(key, data: "body")`."""
import sys, json, os, base64
import common
from common import CACHE, ENGINE
sys.path.insert(0, os.path.join(ENGINE, 'tools'))
import motions as M   # the engine's own converter (arrays, lowest)

mid, raw, key, prompt, secs = sys.argv[1:6]
d = json.load(open(raw))
q, p = M.arrays(d)
out = {'format': 'engine/motion', 'version': 1, 'id': mid, 'label': {'ru': mid, 'en': mid},
       'kimodo': {'key': key, 'prompts': [prompt], 'seconds': [float(secs)]}, 'fps': d['fps'], 'frames': int(len(q)), 'skeleton': 'soma77',
       'data': {'names': d['names'], 'q': base64.b64encode(q.astype('<i2').tobytes()).decode(), 'p': base64.b64encode(p.astype('<i2').tobytes()).decode()},
       'derived': {'lowest': M.lowest(q, p)}}
os.makedirs(f'{CACHE}/motions', exist_ok=True)
json.dump(out, open(f'{CACHE}/motions/{mid}.json', 'w'))
print(mid, len(q))
