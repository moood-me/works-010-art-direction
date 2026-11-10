#!/bin/sh
# a quick sheet to look at: four sides of the figure and the head close → the cache's look/body.jpg, look/head.jpg
C=/home/user/cache/to3d-$(basename $(dirname $(dirname $(readlink -f $0))))
k=0; while :; do flock -n -E 75 /home/user/cache/heavy.$k.lock node $(dirname $0)/shots.mjs $C/look.json $C/look > $C/look.log 2>&1; [ $? = 75 ] || break; k=$(((k + 1) % 3)); sleep 2; done
grep -i "error" $C/look.log
cd $C/look && python3 -c "
from PIL import Image
for out, names in (('body', ['f','q','s','b']), ('head', ['hf','hq','hs'])):
    ims=[Image.open(n+'.png') for n in names]
    o=Image.new('RGB',(600*len(ims),900)); [o.paste(i,(k*600,0)) for k,i in enumerate(ims)]; o.save(out+'.jpg',quality=85)"
