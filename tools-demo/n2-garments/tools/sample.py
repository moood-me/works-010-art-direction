"""GarmentCode's own random sampling of designs (as its dataset generator does: pyg.DesignSampler over
assets/design_params/default.yaml, the same validity checks), fitted to a body; saves design yamls and patterns.
cd GarmentCode root; PYTHONPATH=. python sample.py BODY_YAML OUTDIR N SEED"""
import sys, random, yaml
from pathlib import Path
sys.path.insert(0, '.')
import pygarment as pyg
from assets.garment_programs.meta_garment import MetaGarment
from assets.bodies.body_params import BodyParameters
from pattern_sampler import assert_param_combinations
body_yaml, out, n, seed = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
random.seed(seed)
body = BodyParameters(body_yaml)
sampler = pyg.DesignSampler('./assets/design_params/default.yaml')
out.mkdir(parents=True, exist_ok=True); k = 0
while k < n:
    d = sampler.randomize()
    try:
        assert_param_combinations(d)
        g = MetaGarment(f'rand{k:02d}', body, d); g.assert_total_length()
        if g.is_self_intersecting(): continue
        p = g.assembly()
        p.serialize(out, tag='', to_subfolder=True, with_3d=False, with_text=False, view_ids=False)
        yaml.dump({'design': d}, open(out / f'rand{k:02d}.yaml', 'w'))
        print(k, d['meta']['upper']['v'], d['meta']['wb']['v'], d['meta']['bottom']['v']); k += 1
    except BaseException as e:  # its checks raise BaseException subclasses
        if isinstance(e, KeyboardInterrupt): raise
        continue
