#!/bin/sh
# node shots through one of the shared locks: sh run.sh jobs.json
C=/home/user/cache/to3d-r16-s16-savely
cd "$(dirname "$0")" && flock /home/user/cache/heavy.$(( $(od -An -N1 -tu1 /dev/urandom) % 3 )).lock node shots.mjs "$1" $C/out 2>&1 | grep -v "GPU stall\|page messages"
