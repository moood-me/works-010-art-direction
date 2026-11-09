#!/bin/bash
# A heavy run (Blender, a film) takes its turn on one of the three shared locks (docs/briefs/to3d.md).
# usage: heavy.sh command…      heavy.sh blender ARGS… runs the local Blender
if [ "$1" = blender ]; then shift; set -- /home/user/cache/blender/blender "$@"; fi
exec flock /home/user/cache/heavy.$((RANDOM % 3)).lock "$@"
