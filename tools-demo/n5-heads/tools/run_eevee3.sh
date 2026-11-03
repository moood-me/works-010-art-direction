#!/bin/sh
# Renders lost when other processes ran the machine out of memory (Blender "Killed"), done again.
T=$(dirname "$0"); B=/home/user/cache/blender/blender; C=/home/user/cache/n5-heads; O=$C/r/
cd $C
$B -b "rain/Rain v3.3/rain_v3.2.blend" -P $T/render.py -- "$(python3 $T/job.py rain EEVEE $O/e eyeL,mouth neutral 700)"
$B -b "snow/Snow/snow_v4.2.blend" -P $T/render.py -- "$(python3 $T/job.py snow EEVEE $O/e side,eyeL,mouth neutral 700)"
$B -b "snow/Snow/snow_v4.2.blend" -P $T/render.py -- "$(python3 $T/job.py snow EEVEE $O/e front smile,surprise,blink,anger 700)"
# bodies again, framed so the arms of the T-pose fit
$B -b "rain/Rain v3.3/rain_v3.2.blend" -P $T/render.py -- "$(python3 $T/job.py rain EEVEE $O/e bodyfront,body neutral 840)"
$B -b "snow/Snow/snow_v4.2.blend" -P $T/render.py -- "$(python3 $T/job.py snow EEVEE $O/e bodyfront,body neutral 840)"
