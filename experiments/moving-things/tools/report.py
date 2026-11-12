# The numbers of a scene (what the page measured every frame: tools/shots.cjs with `measure`), summed up.
#   python3 tools/report.py measures/<scene>.json [measures/<scene>-raw.json]
# For each contact, over the frames it is held (weight 1): how far the middle of the palm is from its place —
# Kimodo's own (before the correction) and after it (each contact by its name); the hand's skin against the surface (a table top, an armrest:
# the lowest point of the hand over it, negative = into it) or against the other person (the nearest skin; inside =
# how deep the deepest hand point is under their skin). Then everything of the body that goes into the things.
import json, sys
import numpy as np

m = json.load(open(sys.argv[1]))
cm = lambda x: f'{x * 100:.1f}'
out = {}
names = list(dict.fromkeys(c['name'] or c['side'] for f in m for c in f['contacts']))
for side in names:
    held = [(f['t'], c) for f in m for c in f['contacts'] if (c['name'] or c['side']) == side and c['w'] >= 0.999]
    if not held: continue
    b = np.array([c['palmBefore'] for _, c in held]); a = np.array([c['palmAfter'] for _, c in held])
    gaps = np.array([c['gap'] for _, c in held if c.get('gap') is not None])
    ins = np.array([c.get('inside', 0) for _, c in held])
    r = {'frames': f'{held[0][0]}–{held[-1][0]}', 'kimodo_palm_cm': f'mean {cm(b.mean())}, max {cm(b.max())}',
         'corrected_palm_cm': f'mean {cm(a.mean())}, max {cm(a.max())}'}
    if len(gaps): r['skin_gap_cm'] = f'min {cm(gaps.min())}, mean {cm(gaps.mean())}, max {cm(gaps.max())}'
    if ins.max() > 0: r['hand_inside_other_cm'] = f'max {cm(ins.max())}'
    out[side] = r
into = {}
for f in m:
    for x in f['into']:
        k = f"{x['thing']}/{x['part']}"
        d = into.setdefault(k, {'frames': 0, 'deepest_cm': 0, 'at': None, 'by': {}})
        d['frames'] += 1; d['by'][x.get('by')] = max(d['by'].get(x.get('by'), 0), round(x['deepest'] * 100, 1))
        if x['deepest'] > d['deepest_cm'] / 100: d['deepest_cm'] = round(x['deepest'] * 100, 1); d['at'] = f['t']
out['into_things'] = into or 'nothing'
# the things: a door's opening; a cup's rim to the lips while it is at the mouth; where a thing stands at the end
th = {}
for f in m:
    for x in f.get('things', []):
        d = th.setdefault(x['id'], {})
        if 'open' in x: d['open_deg_max'] = round(max(d.get('open_deg_max', 0), x['open']), 1); d['open_deg_end'] = round(x['open'], 1)
        if 'lips' in x: d['lips_cm_min'] = round(min(d.get('lips_cm_min', 99), x['lips'] * 100), 1)
        if 'over' in x and not x['held']: d['end_over_cm'] = round(x['over'] * 100, 1); d['end_tilt_deg'] = round(x['tilt'], 1)
out['things'] = th
print(json.dumps(out, ensure_ascii=False, indent=1))
