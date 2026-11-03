# HOOD on its own example, as its notebook Inference_from_any_pose.ipynb runs it: the T-shirt from
# $HOOD_DATA/fromanypose/tshirt.obj on the SMPL body mesh sequence fromanypose/mesh_sequence.pkl, model postcvpr.pth,
# on CPU. python hood_example.py <out.npz> [frames]  — saves the cloth and body trajectories and the time.
import os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.environ['HOOD_PROJECT'])
from utils.mesh_creation import obj2template
from utils.arguments import load_params, create_modules
from utils.common import pickle_dump, pickle_load
from utils.defaults import DEFAULTS

out = sys.argv[1]; F = int(sys.argv[2]) if len(sys.argv) > 2 else -1
d = DEFAULTS.data_root
pickle_dump(obj2template(os.path.join(d, 'fromanypose', 'tshirt.obj')), os.path.join(d, 'fromanypose', 'tshirt.pkl'))
if F > 0:   # a shorter piece of the sequence (CPU time)
    seq = pickle_load(os.path.join(d, 'fromanypose', 'mesh_sequence.pkl'))
    pickle_dump(dict(verts=seq['verts'][:F], faces=seq['faces']), os.path.join(d, 'fromanypose', 'mesh_sequence_short.pkl'))
modules, config = load_params('aux/from_any_pose')
ds = config.dataloader.dataset.from_any_pose
ds.smpl_model = None; ds.pose_sequence_type = 'mesh'; ds.garment_template_path = 'fromanypose/tshirt.pkl'
ds.pose_sequence_path = 'fromanypose/mesh_sequence_short.pkl' if F > 0 else 'fromanypose/mesh_sequence.pkl'
config.device = 'cpu'
torch.set_num_threads(int(os.environ.get('THREADS', '2')))
dataloader_m, runner_module, runner, aux_modules = create_modules(modules, config)
runner.load_state_dict(torch.load(os.path.join(d, 'trained_models', 'postcvpr.pth'), map_location='cpu')['training_module'])
sample = next(iter(dataloader_m.create_dataloader()))
t0 = time.time()
with torch.no_grad():
    traj = runner.valid_rollout(sample, bare=True)
secs = time.time() - t0
np.savez(out, cloth=traj['pred'], body=traj['obstacle'], cloth_faces=traj['cloth_faces'], body_faces=traj['obstacle_faces'], seconds=secs)
print('frames', np.asarray(traj['pred']).shape, 'seconds', round(secs, 1))
