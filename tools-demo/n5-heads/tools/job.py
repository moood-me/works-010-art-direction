# python3 job.py char engine outprefix view[,view] expr[,expr] res  -> prints JSON for render.py
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__)); from poses import RAIN, SNOW
ch, eng, pre, views, exprs, res = sys.argv[1:7]
P = {'rain': RAIN, 'snow': SNOW}[ch]
shots = []
for v in views.split(','):
    for e in exprs.split(','):
        shots.append({'out': f'{pre}{ch}-{v}-{e}.png', 'view': v, 'pose': P[e], 'res': [int(res), int(res)] if not v.startswith('body') else [int(res) * 2 // 3, int(res)],
                      'wire': 'wire' in sys.argv[7:]})
print(json.dumps({'char': ch, 'engine': eng, 'shots': shots}))
