# HairDeck's point-cloud model on this machine's CPU (no GPU here; the image model needs the gated SAM 3 and DINOv3
# weights, which need their licences accepted on Hugging Face). Hair cards from hair point clouds in CHARM's format
# (hair_reform.ply: points with normals on the hair's surface, dataset frame): Dora-VAE 1.1 condition tokens, the
# point-cloud DiT (50 Euler steps, CFG 2), the card VAE -> CHARM json + GLB per hairstyle, and the time it took.
# HAIRDECK_ROOT=... HAIRDECK_DEVICE=cpu venv/bin/python -I hairdeck_pc.py <hairdeck repo> <out> <ply> [<ply> ...]
import sys, os, time, json
repo, out, plys = sys.argv[1], sys.argv[2], sys.argv[3:]
sys.path.insert(0, repo)
import numpy as np, torch
torch.set_num_threads(int(os.environ.get('THREADS', '3')))
from hairdeck.encoders.dora import condition_tokens
from hairdeck.testset.pointcloud import sample, CKPT

os.makedirs(out, exist_ok=True)
t0 = time.time()
cond = condition_tokens('test', device='cpu', plys=plys)
t1 = time.time()
hairs = sample(CKPT, cond, out, seed=0, device='cpu')
t2 = time.time()
json.dump(dict(plys=plys, condition_sec=round(t1 - t0, 1), sample_sec=round(t2 - t1, 1), n_cards=[len(h) for h in hairs],
               threads=torch.get_num_threads()), open(f'{out}/cpu_timing.json', 'w'), indent=1)
print('condition', round(t1 - t0), 's; cards', round(t2 - t1), 's;', [len(h) for h in hairs])
