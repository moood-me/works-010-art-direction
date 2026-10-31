import sys
from PIL import Image
cols=int(sys.argv[2]); names=sys.argv[3:]; ims=[Image.open(f's-{n}.png') for n in names]
W,H=ims[0].size; rows=(len(ims)+cols-1)//cols; o=Image.new('RGB',(W*cols,H*rows),'white')
for k,im in enumerate(ims): o.paste(im,((k%cols)*W,(k//cols)*H))
o.save(sys.argv[1])
