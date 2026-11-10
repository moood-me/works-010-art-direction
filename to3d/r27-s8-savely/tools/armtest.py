import json, subprocess, sys, numpy as np, look
from common import CACHE, pack, BID
M = json.load(open(f'{CACHE}/model.json')); _, t = pack.read(f'{CACHE}/engine/data/topology/{BID}.json'); TT = t['triangles'].astype(int)
ims = []
for turns in json.loads(sys.argv[1]):
    json.dump(dict(out=f'{CACHE}/arm.bin', motion='bow', frames=[0], head=dict(level=True), turns=turns), open(f'{CACHE}/arm.json', 'w'))
    subprocess.run(['node', 'move.mjs', f'{CACHE}/arm.json'], check=True, stdout=subprocess.DEVNULL)
    F = np.fromfile(f'{CACHE}/arm.bin', np.float32).reshape(-1, 3).astype(float)
    ims.append(look.raster([(F, TT, (0.8, 0.75, 0.7))], -12, (-0.5, 0.5, 0, 1.25), 300))
look.sheet(ims, f'{CACHE}/arm.png')
