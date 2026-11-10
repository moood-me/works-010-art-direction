#!/bin/bash
# One moving picture: the engine moves the character (move.mjs, with the live face), Blender draws the frames
# (through the shared lock), film.py makes the mp4.
# usage: film.sh CACHE NAME MOTION KIND(full|face) STEP FPS [YAW] [A:B]    LIFE='{…}' in the environment
T=$(dirname "$(readlink -f "$0")"); C=$1; N=$2
cd "$C" || exit 1
LIFE=${LIFE:-'{"seed":3}'} node $T/move.mjs . $3 $N.bin $5 $8 || exit 1
python3 $T/films.py . $N $N.bin $4 ${7:--28} >/dev/null
rm -rf film/$N
$T/heavy.sh blender -b -P $T/render.py -- job_$N.json 2>&1 | grep -E "Traceback|rror:" | grep -v "strokes set"
FY=600; [ "$4" = face ] && FY=9999
python3 $T/film.py "film/$N/*.png" film/$N.mp4 $6 $FY film/$N-sheet.png 8
