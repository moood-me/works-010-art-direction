#!/bin/sh
# Phil again: his file is set to write a movie, render_any now forces PNG.
T=$(dirname "$0")
python3 - <<'PY'
import json, subprocess
cfg = {'name': 'phil', 'head': 'GEO-phil_head', 'out': '/home/user/cache/n5-heads/r/more', 'views': ['body', 'bodytq', 'front', 'tq', 'side'],
       'parts': [['shirt', ['GEO-phil_shirt']], ['pants', ['GEO-phil_pants', 'GEO-phil_shorts_fray']], ['flippers', ['GEO-phil_flippers']]]}
subprocess.run(['/home/user/cache/blender/blender', '-b', '/home/user/cache/n5-heads/phil/phil.blend', '-P', '/home/user/works-010-art-direction/tools-demo/n5-heads/tools/render_any.py', '--', json.dumps(cfg)])
PY
