#!/bin/sh
# after.sh SCRIPT...: wait until none of this page's renders run, then run each script in turn (one heavy job at a time)
D=$(dirname "$0")
while pgrep -f "n5-heads/tools/(render|render_any|face_anim|render_hbm)\.py|run_more\.py" >/dev/null; do sleep 20; done
sleep 30
while pgrep -f "n5-heads/tools/(render|render_any|face_anim|render_hbm)\.py|run_more\.py" >/dev/null; do sleep 20; done
for s in "$@"; do "$D/$s"; done
