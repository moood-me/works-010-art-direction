#!/bin/sh
# build the pack and look at it: sh run.sh [jobs.json]  → cache/t1/all.png
set -e
C=/home/user/cache/to3d-r17-s3-tim
cd "$(dirname "$0")"
python3 build.py > /dev/null
cd $C && node /home/user/works-010-art-direction/to3d/r17-s3-tim/tools/shots.mjs ${1:-t1.json} t1 > /dev/null
python3 -c "
from PIL import Image
ims=[Image.open('t1/t-%s.png'%n) for n in 'fqsb']+[Image.open('t1/t-rest.png')]
w,h=ims[0].size; o=Image.new('RGB',(w*5,h)); [o.paste(i,(w*k,0)) for k,i in enumerate(ims)]; o.resize((2000,2000*h//(5*w))).save('t1/all.png')"
