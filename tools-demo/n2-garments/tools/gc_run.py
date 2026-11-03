"""Sew and drape one GarmentCode design on a body, on CPU.

Run from GarmentCode's root (it reads ./system.json and ./assets relative to it):
  cd /home/user/cache/n2-garments/src
  PYTHONPATH=. ../venv/bin/python <this> --design D.yaml --body DIR/NAME --out OUTDIR [--name N] [--sim gui]

DIR holds NAME.obj (metres, Y up, feet near y=0), NAME.yaml (GarmentCode measurements, cm)
and ggg_body_segmentation.json (vertex ids per part: body, left_arm, right_arm, left_leg, right_leg, face_internal).
"""
import argparse, shutil, sys, yaml
from pathlib import Path
import numpy as np

sys.path.insert(0, '.')
from assets.garment_programs.meta_garment import MetaGarment
from assets.bodies.body_params import BodyParameters
import pygarment.data_config as data_config
from pygarment.meshgen.boxmeshgen import BoxMesh
from pygarment.meshgen.sim_config import PathCofig
from pygarment.meshgen import garment as gc_garment
from pygarment.meshgen.simulation import run_sim

# GarmentCode bug on CPU: Cloth.update keeps `current_verts = particle_q.numpy()`, which on CPU is a view,
# not a copy; with an even number of substeps the view points to the same buffer every frame, so the
# "is it static?" check sees no motion and stops the drape after the zero-gravity frames. Copy it.
_orig_update = gc_garment.Cloth.update
def _update(self, frame):
    _orig_update(self, frame)
    self.current_verts = np.array(self.current_verts, copy=True)
gc_garment.Cloth.update = _update

ap = argparse.ArgumentParser()
ap.add_argument('--design', required=True)
ap.add_argument('--body', required=True, help='DIR/NAME without extension')
ap.add_argument('--out', required=True)
ap.add_argument('--name', default=None)
ap.add_argument('--sim', default='gui', help='gui (mid-soft fabric) or default (very soft)')
ap.add_argument('--dry', action='store_true', help='only make the pattern')
ap.add_argument('--set', action='append', default=[], help='override design value: a.b.c=value (yaml)')
a = ap.parse_args()

body_dir, body_name = Path(a.body).parent, Path(a.body).name
body = BodyParameters(str(body_dir / f'{body_name}.yaml'))
with open(a.design) as f:
    design = yaml.safe_load(f)['design']
for s in a.set:
    k, v = s.split('=', 1)
    d = design
    for p in k.split('.'):
        d = d[p]
    d['v'] = yaml.safe_load(v)
name = a.name or Path(a.design).stem

g = MetaGarment(name, body, design)
pattern = g.assembly()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
folder = Path(pattern.serialize(out, tag='', to_subfolder=True, with_3d=False, with_text=False,
                                view_ids=False, with_printable=False))
body.save(folder)
with open(folder / 'design_params.yaml', 'w') as f:
    yaml.dump({'design': design}, f)

if a.dry:
    print('PATTERN', folder); sys.exit(0)
props = data_config.Properties(f'./assets/Sim_props/{a.sim}_sim_props.yaml')
props['sim']['config']['max_frame_time'] = None
props['sim']['config']['max_sim_time'] = 3000
props.set_section_stats('sim', fails={}, sim_time={}, spf={}, fin_frame={}, body_collisions={}, self_collisions={})
props.set_section_stats('render', render_time={})

paths = PathCofig(in_element_path=folder, out_path=out, in_name=pattern.name, out_name=f'{name}_sim',
                  body_name='mean_all', smpl_body=False, add_timestamp=False)
# the body: ours instead of the default folder's
paths.in_body_mes = body_dir / f'{body_name}.yaml'
paths.in_body_obj = body_dir / f'{body_name}.obj'
paths.body_seg = body_dir / 'ggg_body_segmentation.json'

bm = BoxMesh(paths.in_g_spec, props['sim']['config']['resolution_scale'])
bm.load()
bm.serialize(paths, store_panels=False, uv_config=props['render']['config']['uv_texture'])
run_sim(bm.name, props, paths, save_v_norms=False, store_usd=False, optimize_storage=False, verbose=False)
props.serialize(paths.element_sim_props)
print('OUT', paths.g_sim)
