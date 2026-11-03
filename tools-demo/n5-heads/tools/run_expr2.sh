#!/bin/sh
# More expressions of Rain and Snow (Workbench, their colours).
T=$(dirname "$0"); B=/home/user/cache/blender/blender; C=/home/user/cache/n5-heads; cd $C; mkdir -p r/expr2
$B -b "rain/Rain v3.3/rain_v3.2.blend" -P $T/render.py -- "$(python3 $T/job.py rain WB_MAT r/expr2/m front sad,disgust,puff,wink,oo 600)"
$B -b "snow/Snow/snow_v4.2.blend" -P $T/render.py -- "$(python3 $T/job.py snow WB_MAT r/expr2/m front sad,disgust,puff,wink,oo 600)"
