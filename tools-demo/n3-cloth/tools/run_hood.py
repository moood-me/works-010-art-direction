# HOOD (Grigorev et al., CVPR 2023; github.com/dolorousrtur/hood) on CPU, its "from any pose" mode: one garment mesh,
# dressed on the first frame of an arbitrary body mesh sequence, simulated by the trained graph network (postcvpr.pth).
# python run_hood.py <run dir> <garment> [frames]   (env: HOOD_PROJECT = the clone, HOOD_DATA = its unpacked data)
# Writes hood-<garment>.f32 (frames × points × 3, the page's Y-up space — HOOD's gravity is along Y too) and hood.json.
# The garment is ours as dressed (export.mjs), the body is Anny's skin each frame; HOOD has no pinned points in this
# mode (the garment hangs on the body by itself), and the fabric is given by HOOD's own material inputs: our fabric's
# weight (kg/m²) and bending rigidity, its stretch moduli at HOOD's defaults' middle.
import os, sys, json, time, pickle
import numpy as np
import torch
sys.path.insert(0, os.environ['HOOD_PROJECT'])
from utils.mesh_creation import add_coarse_edges
from utils.arguments import load_params, create_modules
from utils.common import pickle_dump
from utils.defaults import DEFAULTS

run, gname = sys.argv[1], sys.argv[2]
info = json.load(open(os.path.join(run, 'run.json')))
F = int(sys.argv[3]) if len(sys.argv) > 3 else info['frames']
g = next(x for x in info['garments'] if x['name'] == gname)
N = info['N']
body = np.fromfile(os.path.join(run, 'body.f32'), np.float32).reshape(-1, N, 3)[:F]
btris = np.fromfile(os.path.join(run, 'bodytris.u32'), np.uint32).reshape(-1, 3).astype(np.int64)
rest = np.fromfile(os.path.join(run, f'{gname}-rest.f32'), np.float32).reshape(-1, 3)
tris = np.fromfile(os.path.join(run, f'{gname}-tris.u32'), np.uint32).reshape(-1, 3).astype(np.int64)

work = os.path.join(DEFAULTS.data_root, 'ours', os.path.basename(run.rstrip('/')))
os.makedirs(work, exist_ok=True)
# the garment template, as utils.mesh_creation.obj2template makes it (there through trimesh; our mesh is clean already)
template = add_coarse_edges(dict(vertices=rest.astype(np.float64), faces=tris), 4)
pickle_dump(template, os.path.join(work, f'{gname}.pkl'))
pickle_dump(dict(verts=body, faces=btris), os.path.join(work, 'body.pkl'))

modules, config = load_params('aux/from_any_pose')
ds = config.dataloader.dataset.from_any_pose
ds.smpl_model = None; ds.pose_sequence_type = 'mesh'
ds.pose_sequence_path = os.path.relpath(os.path.join(work, 'body.pkl'), DEFAULTS.data_root)
ds.garment_template_path = os.path.relpath(os.path.join(work, f'{gname}.pkl'), DEFAULTS.data_root)
config.device = 'cpu'
mat = config.runner.from_any_pose.material
Fb = g['F']
mat.density_override = float(Fb['density'])
mat.bending_coeff_override = float(np.clip(Fb['bend'], mat.bending_coeff_min, mat.bending_coeff_max))
mat.lame_mu_override = float(np.sqrt(mat.lame_mu_min * mat.lame_mu_max))
mat.lame_lambda_override = float(0.5 * (mat.lame_lambda_min + mat.lame_lambda_max))
torch.set_num_threads(int(os.environ.get('THREADS', '2')))
dataloader_m, runner_module, runner, aux_modules = create_modules(modules, config)
state = torch.load(os.path.join(DEFAULTS.data_root, 'trained_models', 'postcvpr.pth'), map_location='cpu')
runner.load_state_dict(state['training_module'])
runner.eval()
sample = next(iter(dataloader_m.create_dataloader()))
t0 = time.time()
with torch.no_grad():
    traj = runner.valid_rollout(sample, bare=True)
secs = time.time() - t0
pred = np.asarray(traj['pred'], np.float32)
print('pred', pred.shape, 'seconds', round(secs, 1))
# HOOD predicts from the second frame on; the first is the garment as given
if pred.shape[0] == F - 1: pred = np.concatenate([rest[None], pred], 0)
pred.tofile(os.path.join(run, f'hood-{gname}.f32'))
json.dump({'seconds': secs, 'frames': int(pred.shape[0]), 'material': {k: float(mat[k]) for k in ['density_override', 'bending_coeff_override', 'lame_mu_override', 'lame_lambda_override']}},
          open(os.path.join(run, f'hood-{gname}.json'), 'w'), indent=1)
