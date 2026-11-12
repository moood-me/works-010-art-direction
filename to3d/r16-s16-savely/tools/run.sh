#!/bin/sh
# shots.mjs through one of the three shared locks for heavy runs (the first that is free): sh run.sh jobs.json
C=/home/user/cache/to3d-r16-s16-savely
cd "$(dirname "$0")" || exit 1
while :; do
  for i in 0 1 2; do
    flock -n -E 99 /home/user/cache/heavy.$i.lock node shots.mjs "$1" $C/out > $C/shots.log 2>&1
    r=$?
    if [ $r -ne 99 ]; then grep -v "GPU stall\|page messages\|^built" $C/shots.log; exit $r; fi
  done
  sleep 3
done
