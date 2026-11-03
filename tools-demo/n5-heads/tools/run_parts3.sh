#!/bin/sh
# Phil's clothes and Rain's hair again (other objects out of the scene; frame by the largest side)
python3 - <<'PY'
import json, subprocess
B = '/home/user/cache/blender/blender'; R = '/home/user/works-010-art-direction/tools-demo/n5-heads/tools/render_any.py'; O = '/home/user/cache/n5-heads/r/more'
for f, cfg in [('/home/user/cache/n5-heads/phil/phil.blend', {'name': 'phil', 'parts': [['shirt', ['GEO-phil_shirt']], ['pants', ['GEO-phil_pants', 'GEO-phil_shorts_fray']]]}),
               ('/home/user/cache/n5-heads/rain/Rain v3.3/rain_v3.2.blend', {'name': 'rain', 'parts': [['hair', ['GEO-rain-hair_main', 'GEO-rain-hair_ponytail', 'GEO-rain-hair_strand', 'GEO-rain-hairband']]]})]:
    cfg.update({'out': O, 'views': []}); subprocess.run([B, '-b', f, '-P', R, '--', json.dumps(cfg)])
PY
