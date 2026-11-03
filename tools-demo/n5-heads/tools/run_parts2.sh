#!/bin/sh
# Parts and Jay's bare head again, other objects taken out of the scene (their visibility is driven by the rig)
T=$(dirname "$0"); python3 $T/run_parts.py
python3 - <<'PY'
import json, subprocess
cfg = {'name': 'jay', 'head': 'GEO-jay_head', 'out': '/home/user/cache/n5-heads/r/more', 'views': ['front', 'tq', 'side'], 'hide': ['GEO-jay_hat', 'GEO-jay_shades']}
subprocess.run(['/home/user/cache/blender/blender', '-b', '/home/user/cache/n5-heads/jay/jay.blend', '-P', '/home/user/works-010-art-direction/tools-demo/n5-heads/tools/render_any.py', '--', json.dumps(cfg)])
PY
