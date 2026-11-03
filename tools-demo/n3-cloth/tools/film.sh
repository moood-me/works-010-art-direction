#!/bin/bash
# film.sh <run name> <out mp4> <from> <to> <yaw> <pitch> <dist> <src:tag>... — shoots each simulator's frames of a run
# from the same camera (shoot.cjs) and puts them side by side in one h264 mp4 (30 fps).
set -e
run=$1; out=$2; from=$3; to=$4; yaw=$5; pitch=$6; dist=$7; shift 7
here=$(cd "$(dirname "$0")" && pwd); tmp=/home/user/cache/n3-cloth/frames/$run-$(basename "$out" .mp4); rm -rf "$tmp"; mkdir -p "$tmp"
inputs=(); k=0
for st in "$@"; do
  src=${st%%:*}; tag=${st#*:}
  W=${W:-400} H=${H:-480} node "$here/shoot.cjs" "http://local/cache/n3-cloth/runs/$run" "$src" "$tag" "$tmp/$src" "$yaw" "$pitch" "$dist" "$from" "$to" 1
  inputs+=(-framerate 30 -start_number "$from" -i "$tmp/$src/%04d.png"); k=$((k+1))
done
ffmpeg -y -loglevel error "${inputs[@]}" -filter_complex "$(for i in $(seq 0 $((k-1))); do printf '[%d:v]' $i; done)hstack=inputs=$k,format=yuv420p" -c:v libx264 -crf 26 -preset slow -movflags +faststart "$out"
ls -la "$out"
