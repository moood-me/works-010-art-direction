#!/bin/sh
# render.sh in.svg out.png W H  — headless Chrome screenshot of an SVG
google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=$3,$4 --screenshot="$2" "file://$(realpath "$1")" >/dev/null 2>&1
