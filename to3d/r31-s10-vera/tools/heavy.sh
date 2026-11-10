#!/bin/bash
# A heavy run (Blender, a film) takes its turn on one of the three shared locks (docs/briefs/to3d.md): a free one
# if there is one, else it waits for one of them.
# usage: heavy.sh command…      heavy.sh blender ARGS… runs the local Blender
if [ "$1" = blender ]; then shift; set -- /home/user/cache/blender/blender "$@"; fi
for i in 0 1 2; do
  flock -n -E 222 /home/user/cache/heavy.$i.lock "$@"; r=$?
  [ $r -ne 222 ] && exit $r
done
exec flock /home/user/cache/heavy.$((RANDOM % 3)).lock "$@"
