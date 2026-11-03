#!/bin/sh
# Phil again: his file is set to write a movie, render_any now forces PNG.
T=$(dirname "$0")
python3 - <<'PY'
import json, subprocess
cfg = {'name': 'phil', 'head': 'GEO-phil_head', 'out': '/home/user/cache/n5-heads/r/more', 'views': ['body', 'bodytq', 'front', 'tq', 'side'],
       'parts': [['shirt', ['GEO-phil_shirt']], ['pants', ['GEO-phil_pants', 'GEO-phil_shorts_fray']], ['flippers', ['GEO-phil_flippers']]]}
subprocess.run(['/home/user/cache/blender/blender', '-b', '/home/user/cache/n5-heads/phil/phil.blend', '-P', '/home/user/works-010-art-direction/tools-demo/n5-heads/tools/render_any.py', '--', json.dumps(cfg)])
PY
# Einar's side view and clothes: the first run was killed (out of memory) after the 3/4 view
python3 - <<'PY'
import json, subprocess
cfg = {'name': 'einar', 'head': 'GEO-einar_head', 'out': '/home/user/cache/n5-heads/r/more', 'views': ['side'],
       'parts': [['jacket', ['GEO-einar_jacket_main', 'GEO-einar_jacket_collar1', 'GEO-einar_jacket_collar2', 'GEO-einar_jacket_pocket1', 'GEO-einar_jacket_pocket2', 'GEO-einar_jacket_zipper', 'GEO-einar_jacket_tape', 'GEO-einar_jacket_belts']],
                 ['boots', ['GEO-einar_boot_main.L', 'GEO-einar_boot_sole.L']], ['hat', ['GEO-einar_hat']], ['glove', ['GEO-einar_glove', 'GEO-einar_fingers']]]}
subprocess.run(['/home/user/cache/blender/blender', '-b', '/home/user/cache/n5-heads/einar/einar_release_v1.blend', '-P', '/home/user/works-010-art-direction/tools-demo/n5-heads/tools/render_any.py', '--', json.dumps(cfg)])
PY
python3 $(dirname "$0")/run_parts.py
# Rain's «oo» again: the corner control's in/out axis is not mirrored on the right side
cd /home/user/cache/n5-heads && /home/user/cache/blender/blender -b "rain/Rain v3.3/rain_v3.2.blend" -P $T/render.py -- "$(python3 $T/job.py rain WB_MAT r/expr2/m front oo 600)"
