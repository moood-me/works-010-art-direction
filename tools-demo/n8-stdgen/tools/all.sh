#!/bin/bash
# render every StdGEN result's whole refined mesh from 4 sides and tile into a sheet with the input and its views
cd /home/user/cache/hf
for d in out/*/; do n=$(basename $d); [ -f $d/refined3.glb ] || continue
  /home/user/cache/blender/blender -b -P render/turn.py -- $d/refined3.glb render/$n >/dev/null 2>&1
  python3 - "$n" <<'PY'
import sys; from PIL import Image
n=sys.argv[1]; h=640
base=n.split('_')[0]; ims=[Image.open(f'in/{base}.png').convert('RGB')]
ims+= [Image.open(f'render/{n}_{i}.png').convert('RGB') for i in range(4)]
ims=[i.resize((int(i.width*h/i.height),h)) for i in ims]
s=Image.new('RGB',(sum(i.width for i in ims),h),'white'); x=0
for i in ims: s.paste(i,(x,0)); x+=i.width
s.save(f'render/{n}-3d.png')
PY
done
