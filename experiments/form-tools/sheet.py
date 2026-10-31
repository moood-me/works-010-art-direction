import sys
from PIL import Image
names=sys.argv[2:]; ims=[Image.open(f'q-{n}.png').crop((380,0,900,617)) for n in names]
W,H=ims[0].size; cols=4; rows=(len(ims)+3)//4; sheet=Image.new('RGB',(W*cols,H*rows),'white')
for k,im in enumerate(ims): sheet.paste(im,((k%cols)*W,(k//cols)*H))
sheet.save(sys.argv[1])
