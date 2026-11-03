#!/bin/sh
# EEVEE colour renders of Rain and Snow: three angles, four expressions, the whole body.
T=$(dirname "$0"); B=/home/user/cache/blender/blender; C=/home/user/cache/n5-heads; O=$C/r/
cd $C
$B -b "rain/Rain v3.3/rain_v3.2.blend" -P $T/render.py -- "$(python3 $T/job.py rain EEVEE $O/e front,tq,side,eyeL,mouth neutral 700)"
$B -b "rain/Rain v3.3/rain_v3.2.blend" -P $T/render.py -- "$(python3 $T/job.py rain EEVEE $O/e front smile,surprise,blink,anger 700)"
$B -b "rain/Rain v3.3/rain_v3.2.blend" -P $T/render.py -- "$(python3 $T/job.py rain EEVEE $O/e bodyfront,body,bodyside neutral 840)"
$B -b "snow/Snow/snow_v4.2.blend" -P $T/render.py -- "$(python3 $T/job.py snow EEVEE $O/e front,tq,side,eyeL,mouth neutral 700)"
$B -b "snow/Snow/snow_v4.2.blend" -P $T/render.py -- "$(python3 $T/job.py snow EEVEE $O/e front smile,surprise,blink,anger 700)"
$B -b "snow/Snow/snow_v4.2.blend" -P $T/render.py -- "$(python3 $T/job.py snow EEVEE $O/e bodyfront,body,bodyside neutral 840)"
