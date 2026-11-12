#!/bin/sh
# Heavy runs take turns (the brief): at most three at once on the machine. Takes whichever of the three shared locks
# is free, looking again every two seconds. Usage: heavy.sh <command…>
while :; do
  for i in 0 1 2; do
    flock -n -E 75 /home/user/cache/heavy.$i.lock "$@"; r=$?
    [ $r -ne 75 ] && exit $r
  done
  sleep 2
done
