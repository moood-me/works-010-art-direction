#!/bin/sh
# a quick sheet to look at: four sides of the figure and the head close → the cache's look/body.jpg, look/head.jpg
C=/home/user/cache/to3d-$(basename $(dirname $(dirname $(readlink -f $0))))
flock /home/user/cache/heavy.$(($$ % 3)).lock node $(dirname $0)/shots.mjs $C/look.json $C/look 2>&1 | grep -v "GPU stall" | grep -iv "^[a-z]*$"
cd $C/look && python3 -c "
from PIL import Image
for out, names in (('body', ['f','q','s','b']), ('head', ['hf','hq','hs'])):
    ims=[Image.open(n+'.png') for n in names]
    o=Image.new('RGB',(600*len(ims),900)); [o.paste(i,(k*600,0)) for k,i in enumerate(ims)]; o.save(out+'.jpg',quality=85)"
