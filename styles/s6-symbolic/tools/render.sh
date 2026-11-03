#!/bin/sh
# render.sh in.svg out.png W H — headless Chrome screenshot of an SVG
google-chrome --headless=new --disable-gpu --hide-scrollbars --screenshot="$2" --window-size="$3,$4" "file://$(readlink -f "$1")" >/dev/null 2>&1
