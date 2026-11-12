# The numbers of a scene (what the page measured every frame: tools/shots.cjs with `measure`), summed up.
#   python3 tools/report.py measures/<scene>.json        (a copy of К1's tools/report.py, with К2's touches and feet)
# Hands (a palm on a rail), over the frames the touch is weighed in fully: how far the middle of the palm is from its
# place — Kimodo's own and after the correction — and the hand's skin against the rail (negative: in it).
# Touches (a part of the body resting on a thing), over the frames it is held (scenes.json `held`): the nearest of
# that part's skin to the thing's faces (negative: how deep in it). Feet on steps: how far each foot's sole was in or
# over the step under its ankle, Kimodo's and corrected, over the frames it stands (within 5 cm). Then everything of
# the body that goes into the things, over the whole clip.
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(HERE)
m = json.load(open(sys.argv[1]))
name = os.path.basename(sys.argv[1]).split('.')[0].replace('-raw', '')
scene = next(s for s in json.load(open(os.path.join(ITEM, 'scenes.json')))['scenes'] if s['id'] == name)
cm = lambda x: f'{x * 100:.1f}'
out = {}
for side in sorted({c['side'] for f in m for c in f['contacts']}):
    held = [(f['t'], c) for f in m for c in f['contacts'] if c['side'] == side and c['w'] >= 0.999]
    if not held: continue
    b = np.array([c['palmBefore'] for _, c in held]); a = np.array([c['palmAfter'] for _, c in held])
    g = np.array([c['gap'] for _, c in held if c.get('gap') is not None])
    out[held[0][1]['name']] = {'frames': f'{held[0][0]}–{held[-1][0]}', 'kimodo_palm_cm': f'mean {cm(b.mean())}, max {cm(b.max())}',
                               'corrected_palm_cm': f'mean {cm(a.mean())}, max {cm(a.max())}',
                               'skin_to_rail_cm': f'min {cm(g.min())}, mean {cm(g.mean())}, max {cm(g.max())}'}
for k, tc in enumerate(scene.get('touches', [])):
    a, b = tc['held']
    g = np.array([f['touches'][k]['gap'] for f in m if a <= f['t'] <= b])
    out[tc['name']] = {'frames': f'{a}–{b}', 'gap_cm': f'min {cm(g.min())}, mean {cm(g.mean())}, max {cm(g.max())}'}
for k, ft in enumerate(scene.get('feet', [])):
    st = [f['feet'][k] for f in m if f['feet'][k]['before'] < 0.05]
    b = np.array([x['before'] for x in st]); a = np.array([x['after'] for x in st])
    out[ft['name'] + ' на ступени'] = {'frames_standing': len(st), 'kimodo_cm': f'min {cm(b.min())}, mean {cm(b.mean())}, max {cm(b.max())}',
                                      'corrected_cm': f'min {cm(a.min())}, mean {cm(a.mean())}, max {cm(a.max())}'}
into = {}
for f in m:
    for x in f['into']:
        k = f"{x['thing']}/{x['part']}"
        d = into.setdefault(k, {'frames': 0, 'deepest_cm': 0, 'at': None, 'by': {}})
        d['frames'] += 1; d['by'][x.get('by')] = max(d['by'].get(x.get('by'), 0), round(x['deepest'] * 100, 1))
        if x['deepest'] > d['deepest_cm'] / 100: d['deepest_cm'] = round(x['deepest'] * 100, 1); d['at'] = f['t']
out['into_things'] = into or 'nothing'
print(json.dumps(out, ensure_ascii=False, indent=1))
