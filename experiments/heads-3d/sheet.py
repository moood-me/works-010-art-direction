import sys
from PIL import Image
REF={'marco':('a1-3',None),'gwen':('a1-2',None),'gogo':('a1-0',None),'jack':('a1-1',None),'ariel':('ariel',None),'boy3d':('boy3d',(200,60,560,420)),'doll':('doll',None),'kpopBraid':('kpop',(400,30,760,560)),'kpopPony':('kpop',(700,150,1101,640)),'kpopBuns':('kpop',(80,200,420,700)),'claire':('spiky',(100,0,600,450))}
names=sys.argv[1:]; H=360
rows=[]
for n in names:
  r,box=REF.get(n,(None,None)); tiles=[]
  if r:
    im=Image.open(f'ref/{r}.png').convert('RGB')
    if box: im=im.crop(box)
    tiles.append(im.resize((int(im.size[0]*H/im.size[1]),H)))
  for k,crop in (('f',(190,0,1090,900)),('q',(190,0,1090,900)),('s',(190,0,1090,900)),('b',(390,0,890,900))):
    im=Image.open(f'o/{n}-{k}.png').convert('RGB').crop(crop); tiles.append(im.resize((int(im.size[0]*H/im.size[1]),H)))
  W=sum(t.size[0] for t in tiles); row=Image.new('RGB',(W,H),'white'); x=0
  for t in tiles: row.paste(t,(x,0)); x+=t.size[0]
  rows.append(row)
W=max(r.size[0] for r in rows); out=Image.new('RGB',(W,H*len(rows)),'white')
for i,r in enumerate(rows): out.paste(r,(0,i*H))
out.save('sheet-'+'-'.join(names)[:60]+'.png'); print('sheet-'+'-'.join(names)[:60]+'.png')
