#!/bin/sh
# Workbench clay and wireframe (base cage) renders of Rain and Snow.
T=$(dirname "$0"); B=/home/user/cache/blender/blender; C=/home/user/cache/n5-heads; cd $C
for ch in rain snow; do F="rain/Rain v3.3/rain_v3.2.blend"; [ $ch = snow ] && F="snow/Snow/snow_v4.2.blend"
$B -b "$F" -P $T/render.py -- "$(python3 $T/job.py $ch WB_CLAY r/clay/c front,side,eyeL,mouth neutral 800)"
$B -b "$F" -P $T/render.py -- "$(python3 $T/job.py $ch WB_CLAY r/clay/c mouth,eyeL smile,surprise,blink,anger 600)"
$B -b "$F" -P $T/render.py -- "$(python3 $T/job.py $ch WB_CLAY r/clay/w front,eyeL,mouth,side neutral 800 wire)"
$B -b "$F" -P $T/render.py -- "$(python3 $T/job.py $ch WB_CLAY r/clay/w mouth,eyeL smile,blink 600 wire)"
done
