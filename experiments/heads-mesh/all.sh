#!/bin/bash
# bash all.sh name… — build each head, render its sheet, and stack them into _all.png
cd "$(dirname "$0")"
for n in "$@"; do python3 py/build.py $n 2>&1 | grep -E " ok|rror|Trace"; done
ZOOM=1.4 node shot2.js "$@"
python3 -c "
import sys
from PIL import Image
ims=[Image.open('s-%s.png'%n) for n in sys.argv[1:]]
ims=[i.resize((int(i.width*300/i.height),300)) for i in ims]
o=Image.new('RGB',(max(i.width for i in ims),300*len(ims)),'white'); y=0
for i in ims: o.paste(i,(0,y)); y+=300
o.save('_all.png')" "$@"
